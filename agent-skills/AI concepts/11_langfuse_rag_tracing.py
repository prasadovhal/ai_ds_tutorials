"""
File 11: LangFuse RAG Tracing
Concepts: Tracing retrieval & generation, RAG debugging, metadata logging

Now we combine files 9 (LangFuse) + 10 (RAG).
Trace the retrieval step separately from generation.

This lets us see:
- Which chunks were retrieved and their relevance scores
- How long retrieval took vs. LLM inference
- Whether the right chunks were selected (debugging)

Prerequisites:
- pip install langchain-community langchain-huggingface
- PostgreSQL + pgvector running (see file 10 setup notes)
"""

import os
import uuid
from dotenv import load_dotenv
from pathlib import Path
from langchain_community.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
import time
from langfuse import Langfuse

load_dotenv()

ollama_client = ollama.Client()
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

lf_client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
)

CONNECTION_STRING = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', '')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', 5432)}/"
    f"{os.getenv('POSTGRES_DB', 'ragdb')}"
)


def load_knowledge_base(kb_path):
    """Load and chunk a text file using RecursiveCharacterTextSplitter."""
    with open(kb_path, 'r') as f:
        content = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    texts = splitter.split_text(content)
    source = Path(kb_path).stem
    return [{"text": t, "category": source} for t in texts]


def build_vector_store(kb_path):
    """
    Build vector store using LangChain PGVector.
    pre_delete_collection=True clears old data before each rebuild.
    """
    chunks = load_knowledge_base(kb_path)
    texts = [c["text"] for c in chunks]
    metadatas = [{"category": c["category"]} for c in chunks]

    store = PGVector.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        collection_name="documents",
        pre_delete_collection=True,
    )
    return store


def traced_retrieve_chunks(query, store, trace, top_k=3):
    """
    Retrieve chunks with LangFuse tracing.

    Logs:
    - Retrieval time
    - Number of chunks retrieved
    - Scores and metadata
    """

    span = trace.span(
        name="vector_retrieval",
        input={"query": query, "top_k": top_k}
    )

    start_time = time.time()
    results = store.similarity_search_with_score(query, k=top_k)
    latency_ms = (time.time() - start_time) * 1000

    retrieved = []
    chunk_info = []
    for i, (doc, score) in enumerate(results):
        retrieved.append({
            "text": doc.page_content,
            "score": float(score),
            "category": doc.metadata.get("category", "unknown"),
            "rank": i + 1
        })
        chunk_info.append({
            "rank": i + 1,
            "score": float(score),
            "category": doc.metadata.get("category", "unknown"),
            "preview": doc.page_content[:100]
        })

    span.end(
        output={
            "num_retrieved": len(retrieved),
            "chunks": chunk_info,
            "latency_ms": latency_ms
        },
        metadata={
            "retrieval_latency_ms": latency_ms,
            "top_score": chunk_info[0]["score"] if chunk_info else None,
            "top_category": chunk_info[0]["category"] if chunk_info else None
        }
    )

    return retrieved


def traced_rag_answer(query, collection, trace, top_k=3):
    """
    Full RAG pipeline with LangFuse tracing.

    Trace includes:
    1. Retrieval span
    2. Generation span
    Both linked under the same trace
    """

    # Step 1: Retrieve (with tracing)
    retrieved = traced_retrieve_chunks(query, collection, trace, top_k=top_k)

    # Build context
    if not retrieved:
        context = "No relevant knowledge base entries found."
    else:
        context = "\n\n".join([
            f"[{r['category']}] {r['text'][:200]}"
            for r in retrieved
        ])

    # Step 2: Generate (with tracing)
    span_gen = trace.span(
        name="llm_generation",
        input={"query": query, "num_retrieved": len(retrieved)}
    )

    system_prompt = """You are a science expert answering questions based on knowledge base excerpts.
    Use the provided context to answer. If context is insufficient, say so explicitly."""

    prompt = f"""Context:
    {context}

    Question: {query}

    Answer:"""

    start_time = time.time()

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    latency_ms = (time.time() - start_time) * 1000
    answer = response['message']['content']

    span_gen.generation(
        name="mistral_rag_response",
        model="mistral",
        input=prompt,
        output=answer,
        usage={
            "input": len(prompt.split()) // 0.75,
            "output": len(answer.split()) // 0.75,
            "total": (len(prompt.split()) + len(answer.split())) // 0.75
        },
        metadata={
            "generation_latency_ms": latency_ms,
            "chunks_used": len(retrieved),
            "context_length": len(context)
        }
    )

    span_gen.end()

    return {
        "query": query,
        "retrieved": len(retrieved),
        "answer": answer,
        "context_preview": context[:200]
    }


if __name__ == "__main__":
    print("File 11: LangFuse RAG Tracing")

    kb_path = Path("data/science_kb.txt")

    if not kb_path.exists():
        print(f"Error: {kb_path} not found")
    else:
        print("\nBuilding vector store...")
        collection = build_vector_store(str(kb_path))

        print("\nRunning RAG queries with LangFuse tracing...\n")

        # session_id groups all traces from this run into one Session in Langfuse
        session_id = f"rag-session-{uuid.uuid4().hex[:8]}"
        print(f"Session ID: {session_id}\n")

        test_queries = [
            "What is photosynthesis?",
            "Explain quantum entanglement",
            "What is the structure of DNA?"
        ]

        for i, query in enumerate(test_queries):
            trace = lf_client.trace(
                name=f"rag_query_{i+1}",
                session_id=session_id,
                input={"query": query},
                metadata={
                    "domain": "science",
                    "retrieval_type": "vector_search"
                }
            )

            print(f"Query {i+1}: {query}")

            result = traced_rag_answer(query, collection, trace, top_k=2)

            print(f"  Retrieved: {result['retrieved']} chunks")
            print(f"  Answer: {result['answer'][:100]}...")
            print(f"  View trace: https://cloud.langfuse.com/traces/{trace.id}\n")

        # Flush ensures all async trace data is sent before the script exits
        lf_client.flush()
        print(f"Traces flushed. View session: https://cloud.langfuse.com/sessions/{session_id}")
