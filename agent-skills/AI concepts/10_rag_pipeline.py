"""
File 10: RAG Pipeline
Concepts: Embedding, vector store, retrieval, generation, augmented prompts

RAG = Retrieve-Augment-Generate: fetch relevant context, then use it in LLM prompt.

This enables LLM to answer based on custom knowledge (papers, docs, FAQ).
Without RAG: LLM uses only training data (can hallucinate on new topics).
With RAG: LLM grounds answers in retrieved documents.

Components:
1. Load documents (data/science_kb.txt)
2. Chunk them
3. Embed each chunk (sentence-transformers)
4. Store in vector DB (ChromaDB)
5. Retrieve top-k for query
6. Generate answer using context
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
import faiss

load_dotenv()

ollama_client = ollama.Client()

# Initialize embeddings model (runs locally, no API key needed)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# FAISS vector store wrapper
class FAISSVectorStore:
    def __init__(self, embedding_dim=384):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)  # L2 (Euclidean) distance
        self.documents = []
        self.metadata = []

    def add(self, text, metadata):
        """Add document to store."""
        embedding = embedder.encode(text).reshape(1, -1).astype('float32')
        self.index.add(embedding)
        self.documents.append(text)
        self.metadata.append(metadata)

    def query(self, query_text, top_k=3):
        """Find most similar documents."""
        query_embedding = embedder.encode(query_text).reshape(1, -1).astype('float32')

        # Search using FAISS
        distances, indices = self.index.search(query_embedding, top_k)

        results = {
            "documents": [[self.documents[i] for i in indices[0]]],
            "distances": [distances[0].tolist()],  # L2 distances
            "metadatas": [[self.metadata[i] for i in indices[0]]]
        }
        return results

# Initialize vector store
vector_store = FAISSVectorStore()


def load_knowledge_base(kb_path):
    """
    Load knowledge base from file.
    Each chunk is separated by "===== ... =====" markers.

    Returns: list of chunks with metadata
    """

    with open(kb_path, 'r') as f:
        content = f.read()

    # Split by section headers
    sections = content.split("===== ")
    chunks = []

    for section in sections:
        if section.strip():
            # Extract category and content
            lines = section.strip().split("\n", 1)
            category = lines[0].rstrip(" =====").strip() if len(lines) > 0 else "general"
            text = lines[1].strip() if len(lines) > 1 else section.strip()

            # Further split by "Chunk X:" to get individual chunks
            sub_chunks = text.split("Chunk ")
            for sub in sub_chunks:
                if sub.strip():
                    chunks.append({
                        "text": sub.strip(),
                        "category": category
                    })

    return chunks


def build_vector_store(kb_path):
    """
    Build vector store:
    1. Load documents
    2. Embed each
    3. Store in memory
    """

    print(f"Loading knowledge base from {kb_path}...")
    chunks = load_knowledge_base(kb_path)

    print(f"Loaded {len(chunks)} chunks")

    # Create in-memory vector store
    store = SimpleVectorStore()

    # Embed and store chunks
    print("Embedding and storing chunks...")
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        category = chunk["category"]

        # Store in vector store
        store.add(text, {"category": category, "chunk_id": i})

        if (i + 1) % 5 == 0:
            print(f"  Stored {i + 1}/{len(chunks)} chunks")

    print(f"Vector store ready: {len(chunks)} chunks indexed\n")
    return store


def retrieve_chunks(query, store, top_k=3):
    """
    Retrieve top-k most relevant chunks for a query.

    Process:
    1. Embed the query
    2. Search vector store for nearest neighbors
    3. Return top-k results with scores
    """

    # Search
    results = store.query(query, top_k=top_k)

    # Format results
    retrieved = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            score = results["distances"][0][i] if results["distances"] else 0
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}

            retrieved.append({
                "text": doc,
                "score": score,
                "category": metadata.get("category", "unknown"),
                "rank": i + 1
            })

    return retrieved


def rag_answer(query, collection, top_k=3):
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Concatenate as context
    3. Prompt LLM with context + query
    4. Return answer
    """

    # Step 1: Retrieve
    retrieved = retrieve_chunks(query, collection, top_k=top_k)

    if not retrieved:
        context = "No relevant knowledge base entries found."
    else:
        context = "\n\n".join([
            f"[{r['category']}] {r['text'][:200]}"
            for r in retrieved
        ])

    # Step 2: Prompt with context
    system_prompt = """You are a science expert answering questions based on knowledge base excerpts.
    Use the provided context to answer. If context is insufficient, say so explicitly.
    Be accurate and grounded in the context."""

    prompt = f"""Knowledge base context:
    {context}

    Question: {query}

    Answer:"""

    # Step 3: Generate
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
    print("=" * 60)

    # Path to knowledge base
    kb_path = Path("data/science_kb.txt")

    if not kb_path.exists():
        print(f"Error: {kb_path} not found")
        print("Please ensure data/science_kb.txt exists (created in pyproject step)")
    else:
        # Build vector store
        print("\n--- Building Vector Store ---")
        collection = build_vector_store(str(kb_path))

        # Test retrieval
        print("\n--- Retrieval Example ---")
        test_query = "What is the role of mitochondria?"
        retrieved = retrieve_chunks(test_query, collection, top_k=3)

        print(f"Query: {test_query}")
        print(f"Retrieved {len(retrieved)} chunks:")
        for r in retrieved:
            print(f"  [{r['category']}] Score: {r['score']:.3f}")
            print(f"    {r['text'][:80]}...")

        # Full RAG example
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

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. RAG grounds LLM answers in actual documents")
    print("2. Embedding: convert text to vectors (semantic similarity)")
    print("3. Vector store: fast retrieval of similar documents")
    print("4. Retrieved context: passed in LLM prompt")
    print("5. Result: accurate, grounded answers based on KB")
    print("6. Next: Add LangFuse tracing to see retrieval in dashboard")
