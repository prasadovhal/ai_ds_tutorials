"""
File 11: LangFuse RAG Tracing
Concepts: Tracing retrieval & generation, RAG debugging, metadata logging

Now we combine files 9 (LangFuse) + 10 (RAG).
Trace the retrieval step separately from generation.

This lets us see:
- Which chunks were retrieved and their relevance scores
- How long retrieval took vs. LLM inference
- Whether the right chunks were selected (debugging)
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
import time
import faiss
from langfuse import Langfuse

load_dotenv()

# Initialize clients
ollama_client = ollama.Client()
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# FAISS vector store (same as file 10)
class FAISSVectorStore:
    def __init__(self, embedding_dim=384):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.documents = []
        self.metadata = []

    def add(self, text, metadata):
        embedding = embedder.encode(text).reshape(1, -1).astype('float32')
        self.index.add(embedding)
        self.documents.append(text)
        self.metadata.append(metadata)

    def query(self, query_text, top_k=3):
        query_embedding = embedder.encode(query_text).reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)
        results = {
            "documents": [[self.documents[i] for i in indices[0]]],
            "distances": [distances[0].tolist()],
            "metadatas": [[self.metadata[i] for i in indices[0]]]
        }
        return results

lf_client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    baseurl=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
)


def load_knowledge_base(kb_path):
    """Load knowledge base (same as file 10)."""
    with open(kb_path, 'r') as f:
        content = f.read()

    sections = content.split("===== ")
    chunks = []

    for section in sections:
        if section.strip():
            lines = section.strip().split("\n", 1)
            category = lines[0].rstrip(" =====").strip() if len(lines) > 0 else "general"
            text = lines[1].strip() if len(lines) > 1 else section.strip()

            sub_chunks = text.split("Chunk ")
            for sub in sub_chunks:
                if sub.strip():
                    chunks.append({"text": sub.strip(), "category": category})

    return chunks


def build_vector_store(kb_path):
    """Build vector store (same as file 10)."""
    chunks = load_knowledge_base(kb_path)
    store = FAISSVectorStore()

    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        category = chunk["category"]
        store.add(text, {"category": category, "chunk_id": i})

    return store


def traced_retrieve_chunks(query, store, trace_id, top_k=3):
    """
    Retrieve chunks with LangFuse tracing.

    Logs:
    - Retrieval time
    - Number of chunks retrieved
    - Scores and metadata
    """

    # Create a span for retrieval
    span = lf_client.span(
        trace_id=trace_id,
        name="vector_retrieval",
        input={"query": query, "top_k": top_k}
    )

    start_time = time.time()

    # Search using FAISS
    results = store.query(query, top_k=top_k)

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    # Format results
    retrieved = []
    chunk_info = []
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

            chunk_info.append({
                "rank": i + 1,
                "score": score,
                "category": metadata.get("category", "unknown"),
                "preview": doc[:100]
            })

    # Log the retrieval span with metadata
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


def traced_rag_answer(query, collection, trace_id, top_k=3):
    """
    Full RAG pipeline with LangFuse tracing.

    Trace includes:
    1. Retrieval span
    2. Generation span
    Both linked by trace_id
    """

    # Step 1: Retrieve (with tracing)
    retrieved = traced_retrieve_chunks(query, collection, trace_id, top_k=top_k)

    # Build context
    if not retrieved:
        context = "No relevant knowledge base entries found."
    else:
        context = "\n\n".join([
            f"[{r['category']}] {r['text'][:200]}"
            for r in retrieved
        ])

    # Step 2: Generate (with tracing)
    span_gen = lf_client.span(
        trace_id=trace_id,
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

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    answer = response['message']['content']

    # Log generation
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
    print("=" * 60)

    kb_path = Path("data/science_kb.txt")

    if not kb_path.exists():
        print(f"Error: {kb_path} not found")
    else:
        # Build vector store
        print("\nBuilding vector store...")
        collection = build_vector_store(str(kb_path))

        # Test RAG with tracing
        print("\nRunning RAG queries with LangFuse tracing...\n")

        test_queries = [
            "What is photosynthesis?",
            "Explain quantum entanglement",
            "What is the structure of DNA?"
        ]

        for i, query in enumerate(test_queries):
            # Create a trace for each query
            trace = lf_client.trace(
                name=f"rag_query_{i+1}",
                input={"query": query},
                metadata={
                    "domain": "science",
                    "retrieval_type": "vector_search"
                }
            )

            print(f"Query {i+1}: {query}")

            # Run RAG with tracing
            result = traced_rag_answer(query, collection, trace.id, top_k=2)

            print(f"  Retrieved: {result['retrieved']} chunks")
            print(f"  Answer: {result['answer'][:100]}...")
            print(f"  View trace: https://cloud.langfuse.com/traces/{trace.id}\n")

    print("=" * 60)
    print("Key Takeaways:")
    print("1. Trace RAG retrieval separately from generation")
    print("2. Retrieval span logs: chunks, scores, latency")
    print("3. Generation span logs: tokens, latency, context size")
    print("4. Metadata: makes traces searchable and filterable")
    print("5. LangFuse dashboard shows: which chunks retrieved, why")
    print("6. Debugging: identify why wrong chunks are retrieved")
