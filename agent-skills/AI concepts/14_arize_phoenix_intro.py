"""
File 14: Arize Phoenix Introduction
Concepts: Arize Phoenix, local RAG debugging, hallucination detection, retrieval analysis

Arize Phoenix is a local-first observability tool optimized for RAG debugging.
Unlike LangFuse (cloud SaaS), Phoenix runs on your machine.

Key advantages:
- Zero external dependencies (runs locally)
- RAG-specific: visualize retrieval quality
- Detect hallucinations and grounding issues
- No data leaves your machine (privacy)

This file shows: start Phoenix, log RAG traces, debug retrieval.
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
import time
import faiss

load_dotenv()

# Try to import phoenix
try:
    import phoenix as px
    from phoenix.trace import json_schema
    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    print("Note: phoenix not installed. Run: pip install arize-phoenix")
    print("Showing conceptual examples...\n")

ollama_client = ollama.Client()
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# FAISS vector store (same as files 10, 11)
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


def start_phoenix_app():
    """
    Start Phoenix app (local dashboard).
    This launches a local web UI where you can see traces.
    """

    if not PHOENIX_AVAILABLE:
        print("Phoenix not available. In production:")
        print("  px.launch_app() starts local server at http://localhost:6006")
        print("  All RAG traces are sent here automatically")
        return None

    print("Starting Phoenix local dashboard...")
    try:
        # Launch Phoenix app (creates local server)
        # By default: http://localhost:6006
        app = px.launch_app()
        print("✓ Phoenix running at http://localhost:6006")
        return app
    except Exception as e:
        print(f"Could not start Phoenix: {e}")
        print("Phoenix requires pytorch. If issues, run: pip install torch --index-url https://download.pytorch.org/whl/cpu")
        return None


def load_knowledge_base(kb_path):
    """Load knowledge base (same as file 10/11)."""
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


def build_vector_store_for_phoenix(kb_path):
    """Build vector store (same as file 10)."""
    chunks = load_knowledge_base(kb_path)
    store = FAISSVectorStore()

    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        category = chunk["category"]
        store.add(text, {"category": category, "chunk_id": i})

    return store


def phoenix_rag_trace(query, collection, app=None):
    """
    Run RAG and send trace to Phoenix.
    Phoenix visualizes: which chunks retrieved, relevance scores, hallucinations.
    """

    if not PHOENIX_AVAILABLE:
        print(f"Conceptual Phoenix RAG trace for query: {query}")
        print("In reality, this would send to Phoenix dashboard")
        return

    # Retrieve
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    retrieved = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            score = results["distances"][0][i] if results["distances"] else 0
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}

            retrieved.append({
                "text": doc,
                "score": score,
                "category": metadata.get("category", "unknown")
            })

    # Build context
    context = "\n\n".join([f"[{r['category']}] {r['text'][:150]}" for r in retrieved])

    # Generate answer
    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a science expert. Answer based on context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
    )

    answer = response['message']['content']

    # In real Phoenix usage, you'd send structured traces
    # This is the conceptual structure:
    print(f"\nRAG Query: {query}")
    print(f"Retrieved chunks: {len(retrieved)}")
    for r in retrieved:
        print(f"  - [{r['category']}] Score: {r['score']:.3f}")
    print(f"Answer: {answer[:100]}...")
    print("(In Phoenix, this would appear in the RAG debugging dashboard)")

    return {
        "query": query,
        "retrieved": retrieved,
        "answer": answer
    }


def hallucination_analysis_concept():
    """
    Phoenix can detect hallucinations by comparing:
    - Retrieved documents (ground truth)
    - Generated answer (might contain hallucinations)
    """

    print("\n=== Hallucination Detection (Phoenix Concept) ===\n")

    print("Phoenix detects hallucinations by analyzing:")
    print("1. Retrieved context: actual facts from knowledge base")
    print("2. Generated answer: what the LLM said")
    print("3. Overlap analysis: % of answer grounded in retrieved docs")
    print("4. Semantic similarity: answer vs. context")

    example = {
        "query": "What is DNA replication?",
        "retrieved_context": [
            "DNA replication is semi-conservative and uses DNA polymerase",
            "Leading strand is continuous, lagging strand uses Okazaki fragments"
        ],
        "generated_answer": "DNA replication is semi-conservative and uses RNA polymerase...",
        "analysis": {
            "grounding_score": 0.75,  # 75% grounded in context
            "hallucination_detected": True,
            "issue": "Model said RNA polymerase instead of DNA polymerase",
            "recommendation": "Flag this for review, likely low confidence"
        }
    }

    import json
    print(json.dumps(example, indent=2))


def retrieval_quality_analysis():
    """
    Phoenix helps debug retrieval: are we getting the right chunks?
    Visualize retrieval scores, categories, and ranking.
    """

    print("\n=== Retrieval Quality Analysis (Phoenix) ===\n")

    print("Phoenix shows:")
    print("1. Retrieval metrics:")
    print("   - Top score: highest relevance score")
    print("   - Score distribution: range of scores")
    print("   - Category distribution: which domains retrieved")

    print("\n2. Retrieval debugging:")
    print("   - Missing relevant chunks? Embedding model may be weak")
    print("   - Wrong chunks retrieved? Query may be ambiguous")
    print("   - Low scores on all? Knowledge base may be incomplete")

    print("\n3. Example retrieval trace:")
    retrieval_trace = {
        "query": "What is photosynthesis?",
        "retrieval_results": [
            {"rank": 1, "score": 0.92, "category": "biology", "text": "Photosynthesis is..."},
            {"rank": 2, "score": 0.85, "category": "biology", "text": "Light reactions occur..."},
            {"rank": 3, "score": 0.72, "category": "chemistry", "text": "Chemical bonds in ATP..."}
        ],
        "analysis": {
            "top_score": 0.92,
            "average_score": 0.83,
            "score_gap_rank1_to_rank3": 0.20,
            "quality": "Good - top result highly relevant, others decent"
        }
    }

    import json
    print(json.dumps(retrieval_trace, indent=2))


def phoenix_vs_langfuse():
    """
    Comparison: Phoenix vs LangFuse
    """

    print("\n=== Phoenix vs LangFuse ===\n")

    comparison = {
        "Phoenix": {
            "Deployment": "Local (your machine)",
            "Cost": "Free",
            "Privacy": "Data stays local",
            "Best for": "RAG debugging",
            "Setup": "pip install, run locally",
            "Hallucination detection": "Built-in RAG-specific",
            "Cloud integration": "Optional (Arize cloud)"
        },
        "LangFuse": {
            "Deployment": "Cloud SaaS",
            "Cost": "Free tier + paid",
            "Privacy": "Data on Langfuse servers",
            "Best for": "General LLM observability",
            "Setup": "API keys, SDK",
            "Hallucination detection": "Via custom evaluators",
            "Cloud integration": "Native"
        }
    }

    for tool, features in comparison.items():
        print(f"\n{tool}:")
        for key, val in features.items():
            print(f"  {key}: {val}")


if __name__ == "__main__":
    print("File 14: Arize Phoenix Introduction")
    print("=" * 60)

    # Try to start Phoenix (local)
    app = start_phoenix_app()

    # Show concepts
    hallucination_analysis_concept()
    retrieval_quality_analysis()
    phoenix_vs_langfuse()

    # If KB exists, show Phoenix tracing
    kb_path = Path("data/science_kb.txt")
    if kb_path.exists():
        print("\n=== Phoenix RAG Tracing Example ===")
        collection = build_vector_store_for_phoenix(str(kb_path))

        test_queries = [
            "What is photosynthesis?",
            "Explain DNA replication"
        ]

        for query in test_queries:
            phoenix_rag_trace(query, collection, app)

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Phoenix: local-first RAG observability tool")
    print("2. No external API keys needed; runs on your machine")
    print("3. RAG-specific: visualize retrieval, detect hallucinations")
    print("4. Complementary to LangFuse: use both for comprehensive observability")
    print("5. For RAG debugging: start with Phoenix (local, focused)")
    print("6. For production monitoring: add LangFuse (cloud, scalable)")
