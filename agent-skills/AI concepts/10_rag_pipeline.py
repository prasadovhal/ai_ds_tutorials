"""
File 10: RAG Pipeline
Concepts: Embedding, vector store, retrieval, generation, augmented prompts

RAG = Retrieve-Augment-Generate: fetch relevant context, then use it in LLM prompt.

This enables LLM to answer based on custom knowledge (papers, docs, FAQ).
Without RAG: LLM uses only training data (can hallucinate on new topics).
With RAG: LLM grounds answers in retrieved documents.

Components:
1. Load documents (data/science_kb.txt)
2. Chunk them with RecursiveCharacterTextSplitter
3. Embed each chunk (HuggingFaceEmbeddings / sentence-transformers)
4. Store in pgvector via LangChain PGVector
5. Retrieve top-k for query using cosine similarity
6. Generate answer using context

Prerequisites:
- PostgreSQL + pgvector running (docker run -d --name pgvector
    -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ragdb
    -p 5432:5432 pgvector/pgvector:pg16)
- pip install langchain-community langchain-huggingface langchain-text-splitters
- Set POSTGRES_* vars in .env
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_community.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama

load_dotenv()

ollama_client = ollama.Client()
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

CONNECTION_STRING = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', '')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', 5432)}/"
    f"{os.getenv('POSTGRES_DB', 'ragdb')}"
)


def load_knowledge_base(kb_path):
    """
    Load and chunk a text file using RecursiveCharacterTextSplitter.
    Works with any plain-text knowledge base, not tied to a specific format.

    Returns: list of {"text": ..., "category": <filename stem>}
    """
    with open(kb_path, 'r') as f:
        content = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,    # chars; fits within all-MiniLM-L6-v2's 256-token limit
        chunk_overlap=50,  # preserves context across chunk boundaries
    )
    texts = splitter.split_text(content)
    source = Path(kb_path).stem
    return [{"text": t, "category": source} for t in texts]


def build_vector_store(kb_path):
    """
    Build vector store using LangChain PGVector.
    pre_delete_collection=True clears existing data before each rebuild.
    """
    print(f"Loading knowledge base from {kb_path}...")
    chunks = load_knowledge_base(kb_path)
    print(f"Loaded {len(chunks)} chunks")

    print("Embedding and storing chunks...")
    store = PGVector.from_texts(
        texts=[c["text"] for c in chunks],
        embedding=embeddings,
        metadatas=[{"category": c["category"]} for c in chunks],
        connection_string=CONNECTION_STRING,
        collection_name="documents",
        pre_delete_collection=True,
    )
    print(f"Vector store ready: {len(chunks)} chunks indexed\n")
    return store


def retrieve_chunks(query, store, top_k=3):
    """
    Retrieve top-k most relevant chunks for a query.

    Process:
    1. Embed the query
    2. Search pgvector for nearest neighbours
    3. Return top-k results with scores
    """
    results = store.similarity_search_with_score(query, k=top_k)
    return [
        {
            "text": doc.page_content,
            "score": float(score),
            "category": doc.metadata.get("category", "unknown"),
            "rank": i + 1
        }
        for i, (doc, score) in enumerate(results)
    ]


def rag_answer(query, collection, top_k=3):
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Concatenate as context
    3. Prompt LLM with context + query
    4. Return answer
    """
    retrieved = retrieve_chunks(query, collection, top_k=top_k)

    if not retrieved:
        context = "No relevant knowledge base entries found."
    else:
        context = "\n\n".join([
            f"[{r['category']}] {r['text'][:200]}"
            for r in retrieved
        ])

    system_prompt = """You are a science expert answering questions based on knowledge base excerpts.
    Use the provided context to answer. If context is insufficient, say so explicitly.
    Be accurate and grounded in the context."""

    prompt = f"""Knowledge base context:
    {context}

    Question: {query}

    Answer:"""

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response['message']['content']

    return {
        "query": query,
        "retrieved_chunks": retrieved,
        "context": context,
        "answer": answer,
        "num_chunks_retrieved": len(retrieved)
    }


if __name__ == "__main__":
    print("File 10: RAG Pipeline")

    kb_path = Path("data/science_kb.txt")

    if not kb_path.exists():
        print(f"Error: {kb_path} not found")
        print("Please ensure data/science_kb.txt exists")
    else:
        print("\n--- Building Vector Store ---")
        collection = build_vector_store(str(kb_path))

        print("\n--- Retrieval Example ---")
        test_query = "What is the role of mitochondria?"
        retrieved = retrieve_chunks(test_query, collection, top_k=3)

        print(f"Query: {test_query}")
        print(f"Retrieved {len(retrieved)} chunks:")
        for r in retrieved:
            print(f"  [{r['category']}] Score: {r['score']:.4f}")
            print(f"    {r['text'][:80]}...")

        print("\n--- Full RAG Pipeline ---")
        test_queries = [
            "What is photosynthesis?",
            "Explain quantum entanglement",
            "What is DNA replication?"
        ]

        for query in test_queries:
            result = rag_answer(query, collection, top_k=2)
            print(f"\nQuery: {result['query']}")
            print(f"Retrieved: {result['num_chunks_retrieved']} chunks")
            print(f"Answer preview: {result['answer'][:150]}...")
