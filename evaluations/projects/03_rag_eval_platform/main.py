"""
Project 3: RAG Evaluation Platform

End-to-end RAG system with TF-IDF retrieval, Ollama generation, and evaluation.
Computes context precision/recall, faithfulness, and answer relevancy.
Includes Langfuse tracing and LangGraph RAG chain orchestration.
"""
import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv, json, random, os, re

# --- TF-IDF retriever (sklearn) ---
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("[WARN] sklearn not found — using keyword fallback retriever")

# --- Ollama ---
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
CORPUS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "wiki_stem_corpus.csv")
OLLAMA_URL = "http://localhost:11434/api/generate"
NUM_QUESTIONS = 10
TOP_K = 3
MAX_CORPUS = 200

# Quick check: is Ollama reachable?
import socket, select
OLLAMA_AVAILABLE = False
if HAS_REQUESTS:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        err = s.connect_ex(("127.0.0.1", 11434))
        if err == 0:
            OLLAMA_AVAILABLE = True
        else:
            _, w, _ = select.select([], [s], [], 0.5)
            if w:
                OLLAMA_AVAILABLE = (s.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0)
        s.close()
    except Exception:
        pass
    if not OLLAMA_AVAILABLE:
        print("[INFO] Ollama not available — using fallback methods")

# ── 1. Load data ─────────────────────────────────────────────────────────────
def load_questions(path, n):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
            if len(rows) >= n:
                break
    return rows

def load_corpus(path, max_rows):
    docs = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            docs.append({
                "id": r.get("content_id", ""),
                "title": r.get("page_title", ""),
                "section": r.get("section_title", ""),
                "text": r.get("text", "")
            })
            if len(docs) >= max_rows:
                break
    return docs

# ── 2. Build retriever ───────────────────────────────────────────────────────
class TfidfRetriever:
    def __init__(self, docs):
        self.docs = docs
        texts = [d["text"] for d in docs]
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        else:
            self.vectorizer = None

    def retrieve(self, query, top_k=3):
        if HAS_SKLEARN and self.vectorizer:
            q_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(q_vec, self.tfidf_matrix).flatten()
            top_idx = scores.argsort()[-top_k:][::-1]
            return [(self.docs[i], float(scores[i])) for i in top_idx]
        # Fallback: keyword overlap
        query_words = set(query.lower().split())
        scored = []
        for doc in self.docs:
            doc_words = set(doc["text"].lower().split())
            overlap = len(query_words & doc_words)
            scored.append((doc, overlap))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

# ── 3. Generate answer ───────────────────────────────────────────────────────
def generate_answer(question_row, contexts):
    context_text = "\n".join(c["text"][:300] for c, _ in contexts)
    prompt = (
        f"Context:\n{context_text}\n\n"
        f"Question: {question_row['prompt'][:300]}\n"
        f"Choices: A:{question_row['A'][:80]} B:{question_row['B'][:80]} "
        f"C:{question_row['C'][:80]} D:{question_row['D'][:80]} E:{question_row['E'][:80]}\n"
        f"Based on the context, reply with just the letter."
    )
    if OLLAMA_AVAILABLE:
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": "mistral", "prompt": prompt, "stream": False
            }, timeout=30)
            if resp.status_code == 200:
                answer = resp.json().get("response", "").strip()
                for ch in "ABCDE":
                    if ch in answer:
                        return ch
        except Exception:
            pass
    # Fallback: pick the choice whose text overlaps most with retrieved contexts
    ctx_text = " ".join(c["text"].lower() for c, _ in contexts)
    ctx_words = set(ctx_text.split())
    best_label, best_overlap = "A", 0
    for label in "ABCDE":
        choice_words = set(question_row[label].lower().split())
        overlap = len(ctx_words & choice_words)
        if overlap > best_overlap:
            best_overlap = overlap
            best_label = label
    return best_label

# ── 4. RAG evaluation metrics (manual implementations) ───────────────────────
def context_precision(retrieved_docs, gold_answer_text):
    """How many retrieved docs are actually relevant (contain answer-related terms)."""
    gold_words = set(gold_answer_text.lower().split()[:20])
    relevant = sum(1 for doc, _ in retrieved_docs
                   if len(gold_words & set(doc["text"].lower().split())) > 3)
    return relevant / len(retrieved_docs) if retrieved_docs else 0.0

def context_recall(retrieved_docs, gold_answer_text):
    """What fraction of gold answer key terms appear in retrieved context."""
    gold_words = set(re.findall(r'\w+', gold_answer_text.lower()))
    if not gold_words:
        return 0.0
    ctx_text = " ".join(doc["text"].lower() for doc, _ in retrieved_docs)
    ctx_words = set(re.findall(r'\w+', ctx_text))
    covered = len(gold_words & ctx_words)
    return covered / len(gold_words)

def faithfulness(predicted_label, retrieved_docs, question_row):
    """Is the predicted answer grounded in retrieved context?"""
    pred_text = question_row.get(predicted_label, "").lower()
    pred_words = set(re.findall(r'\w+', pred_text))
    if not pred_words:
        return 0.0
    ctx_text = " ".join(doc["text"].lower() for doc, _ in retrieved_docs)
    ctx_words = set(re.findall(r'\w+', ctx_text))
    grounded = len(pred_words & ctx_words)
    return grounded / len(pred_words)

def answer_relevancy(predicted_label, gold_label):
    """Simple: 1.0 if correct, 0.0 otherwise."""
    return 1.0 if predicted_label == gold_label else 0.0

# ── 5. Main ──────────────────────────────────────────────────────────────────
def main():
    print("Loading data ...")
    questions = load_questions(DATA_PATH, NUM_QUESTIONS)
    corpus = load_corpus(CORPUS_PATH, MAX_CORPUS)
    print(f"Questions: {len(questions)}  |  Corpus passages: {len(corpus)}")

    print("Building TF-IDF index ...")
    retriever = TfidfRetriever(corpus)

    all_metrics = []
    print(f"\n{'Q#':<4} {'Pred':<5} {'Gold':<5} {'Match':<6} {'CtxPrec':<8} {'CtxRec':<8} {'Faith':<8} {'AnsRel':<8}")
    print("-" * 60)

    for i, q in enumerate(questions):
        # Retrieve
        retrieved = retriever.retrieve(q["prompt"], TOP_K)
        # Generate
        pred = generate_answer(q, retrieved)
        gold = q["answer"]
        gold_text = q.get(gold, "")
        # Evaluate
        cp = context_precision(retrieved, gold_text)
        cr = context_recall(retrieved, gold_text)
        fa = faithfulness(pred, retrieved, q)
        ar = answer_relevancy(pred, gold)

        match = "YES" if pred == gold else "no"
        print(f"{i+1:<4} {pred:<5} {gold:<5} {match:<6} {cp:<8.3f} {cr:<8.3f} {fa:<8.3f} {ar:<8.3f}")

        all_metrics.append({"question_id": q["id"], "predicted": pred, "gold": gold,
                            "context_precision": cp, "context_recall": cr,
                            "faithfulness": fa, "answer_relevancy": ar,
                            "retrieved_titles": [d["title"] for d, _ in retrieved]})

    # Aggregate
    n = len(all_metrics)
    print(f"\n{'='*60}")
    print(f"  AGGREGATE RESULTS ({n} questions)")
    print(f"{'='*60}")
    for metric in ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]:
        avg = sum(m[metric] for m in all_metrics) / n
        print(f"  {metric:<22}: {avg:.4f}")
    accuracy = sum(1 for m in all_metrics if m["predicted"] == m["gold"]) / n
    print(f"  {'accuracy':<22}: {accuracy:.4f}")

    # ── Langfuse tracing ──
    print(f"\n{'='*60}")
    print("  LANGFUSE TRACING")
    print(f"{'='*60}")
    try:
        from langfuse import Langfuse
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

        langfuse = Langfuse(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_BASE_URL,
        )
        trace = langfuse.trace(name="project3-rag-eval",
                               metadata={"retriever": "TF-IDF" if HAS_SKLEARN else "keyword"})
        for m in all_metrics:
            span = trace.span(name=f"q-{m['question_id']}",
                              input={"predicted": m["predicted"], "gold": m["gold"]})
            span.score(name="ctx_precision", value=m["context_precision"])
            span.score(name="ctx_recall", value=m["context_recall"])
            span.score(name="faithfulness", value=m["faithfulness"])
            span.score(name="answer_relevancy", value=m["answer_relevancy"])
            span.end()
        langfuse.flush()
        print(f"  {len(all_metrics)} traces sent. View at https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")

    # ── LangGraph RAG chain demo ──
    print(f"\n{'='*60}")
    print("  LANGGRAPH RAG CHAIN")
    print(f"{'='*60}")
    try:
        from langgraph.graph import StateGraph, START, END
        from typing import TypedDict, List

        class RAGState(TypedDict):
            question: str
            contexts: List[str]
            answer: str

        def _retrieve(state: RAGState) -> RAGState:
            results = retriever.retrieve(state["question"], TOP_K)
            return {"question": state["question"],
                    "contexts": [d["text"][:200] for d, _ in results], "answer": ""}

        def _generate(state: RAGState) -> RAGState:
            ctx = "\n".join(state["contexts"])
            ans = f"Based on context: {state['question'][:50]}"
            if OLLAMA_AVAILABLE:
                try:
                    resp = requests.post(OLLAMA_URL, json={
                        "model": "mistral",
                        "prompt": f"Context:\n{ctx}\n\nQ: {state['question']}\nAnswer briefly.",
                        "stream": False}, timeout=30)
                    ans = resp.json().get("response", ans)
                except Exception:
                    pass
            return {"question": state["question"], "contexts": state["contexts"], "answer": ans}

        g = StateGraph(RAGState)
        g.add_node("retrieve", _retrieve)
        g.add_node("generate", _generate)
        g.add_edge(START, "retrieve")
        g.add_edge("retrieve", "generate")
        g.add_edge("generate", END)
        chain = g.compile()
        result = chain.invoke({"question": questions[0]["prompt"], "contexts": [], "answer": ""})
        print(f"  Q: {questions[0]['prompt'][:60]}...")
        print(f"  Retrieved {len(result['contexts'])} docs")
        print(f"  Answer: {result['answer'][:80]}...")
    except Exception as e:
        print(f"  LangGraph not available ({e}), skipping.")

if __name__ == "__main__":
    main()
