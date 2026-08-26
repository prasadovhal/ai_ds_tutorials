import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json, time, re

try:
    import numpy as np
except ImportError:
    np = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
try:
    import faiss; HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
try:
    import requests
except ImportError:
    requests = None


def build_retriever(passages):
    """Build a TF-IDF retriever from passages. Try FAISS if available."""
    if not HAS_SKLEARN:
        return {"type": "keyword", "passages": passages}
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    matrix = vectorizer.fit_transform(passages)
    if HAS_FAISS and np is not None:
        dense = np.ascontiguousarray(matrix.toarray().astype("float32"))
        index = faiss.IndexFlatIP(dense.shape[1])
        faiss.normalize_L2(dense)
        index.add(dense)
        return {"type": "faiss", "index": index, "vectorizer": vectorizer,
                "passages": passages}
    return {"type": "tfidf", "matrix": matrix, "vectorizer": vectorizer,
            "passages": passages}


def retrieve(retriever, query, k=3):
    """Retrieve top-k passages for a query."""
    passages = retriever["passages"]
    if retriever["type"] == "keyword":
        query_words = set(query.lower().split())
        scored = [len(query_words & set(p.lower().split())) for p in passages]
        top_idx = sorted(range(len(scored)), key=lambda i: scored[i], reverse=True)[:k]
        return [passages[i] for i in top_idx]
    vectorizer = retriever["vectorizer"]
    query_vec = vectorizer.transform([query])
    if retriever["type"] == "faiss" and np is not None:
        dense_q = np.ascontiguousarray(query_vec.toarray().astype("float32"))
        faiss.normalize_L2(dense_q)
        _, indices = retriever["index"].search(dense_q, k)
        return [passages[i] for i in indices[0] if i < len(passages)]
    similarities = cosine_similarity(query_vec, retriever["matrix"]).flatten()
    top_idx = similarities.argsort()[-k:][::-1]
    return [passages[i] for i in top_idx]


def generate_answer(question, context, choices=None):
    """Generate answer using Ollama; fallback to best-choice heuristic."""
    if requests:
        try:
            prompt = (f"Context:\n{context}\n\nQuestion: {question}\n"
                      f"Choices: {choices}\nAnswer with ONLY the letter (A-E).")
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False}, timeout=15)
            if resp.status_code == 200:
                match = re.search(r"[A-E]", resp.json().get("response", ""))
                if match:
                    return match.group()
        except Exception:
            pass
    if choices:
        context_words = set(context.lower().split())
        best, best_score = "A", 0
        for letter, text in choices.items():
            score = len(set(text.lower().split()) & context_words)
            if score > best_score:
                best, best_score = letter, score
        return best
    return "A"


def run_pipeline(questions_df, retriever):
    """Run RAG pipeline on a DataFrame of questions."""
    results = []
    for _, row in questions_df.iterrows():
        start = time.time()
        context = "\n".join(retrieve(retriever, row["prompt"], k=3))
        choices = {c: str(row.get(c, "")) for c in "ABCDE" if c in row}
        answer = generate_answer(row["prompt"], context, choices)
        latency = time.time() - start
        results.append({"id": row.get("id", ""), "question": row["prompt"],
            "context": context, "predicted": answer,
            "ground_truth": row.get("answer", ""), "latency": round(latency, 4)})
    return results
