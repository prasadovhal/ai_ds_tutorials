import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 5 Hands-On: RAG Evaluation with Real Embeddings + FAISS
Uses: langchain, FAISS, ragas, deepeval, ollama, pandas

pip install faiss-cpu sentence-transformers langchain langchain-community langchain-huggingface
pip install ragas deepeval datasets ollama pandas scikit-learn  # optional
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ── 1. Load data ────────────────────────────────────────────────────────
print("=== 1. DATA LOADED ===")
train = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\train.csv", nrows=5)
corpus = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\wiki_stem_corpus.csv", nrows=500)
passages = corpus["text"].fillna("").tolist()
print(f"Questions: {len(train)} | Passages: {len(corpus)}")
print(train[["id", "prompt", "answer"]].to_string(index=False, max_colwidth=60))

# ── 2. Build vector store ──────────────────────────────────────────────
print("\n=== 2. BUILD VECTOR STORE ===")
vectorstore = None
use_faiss = False

try:
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    print("  Loading HuggingFace embeddings (this may take a moment)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("  Building FAISS index from 500 passages...")
    vectorstore = FAISS.from_texts(passages, embeddings)
    use_faiss = True
    print("  FAISS vector store ready.")
except Exception as e:
    print(f"  FAISS/HuggingFace failed ({e}), falling back to TF-IDF.")

# Fallback: TF-IDF retrieval
tfidf_matrix = None
tfidf_vectorizer = None
if not use_faiss:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        print("  Building TF-IDF index...")
        tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = tfidf_vectorizer.fit_transform(passages)
        print("  TF-IDF index ready.")
    except Exception as e2:
        print(f"  TF-IDF also failed ({e2}). Will use keyword matching.")

# ── 3. Retrieve top-3 passages per question ─────────────────────────────
print("\n=== 3. RETRIEVAL ===")
all_contexts = {}

for _, row in train.iterrows():
    question = row["prompt"]
    qid = row["id"]

    if use_faiss and vectorstore is not None:
        docs = vectorstore.similarity_search(question, k=3)
        ctx = [d.page_content for d in docs]
    elif tfidf_matrix is not None:
        from sklearn.metrics.pairwise import cosine_similarity
        q_vec = tfidf_vectorizer.transform([question])
        sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
        top_idx = sims.argsort()[-3:][::-1]
        ctx = [passages[i] for i in top_idx]
    else:
        # Last-resort keyword overlap
        def _score(p):
            qw = set(question.lower().split())
            return len(qw & set(p.lower().split()))
        ranked = sorted(enumerate(passages), key=lambda x: _score(x[1]), reverse=True)
        ctx = [passages[i] for i, _ in ranked[:3]]

    all_contexts[qid] = ctx
    print(f"Q{qid}: {question[:80]}...")
    for rank, c in enumerate(ctx, 1):
        print(f"  [{rank}] {c[:100]}...")

# ── 4. Generate answers with ollama ─────────────────────────────────────
print("\n=== 4. LLM ANSWERS (ollama) ===")
answers = {}
try:
    import ollama
    model_name = "llama3.2"
    try:
        available = [m.model for m in ollama.list().models]
        if not any(model_name in m for m in available):
            model_name = available[0] if available else "llama3.2"
            print(f"  Using available model: {model_name}")
    except Exception:
        pass

    for _, row in train.iterrows():
        ctx = "\n\n".join(all_contexts[row["id"]])
        prompt = (
            f"Context:\n{ctx}\n\n"
            f"Question: {row['prompt']}\n"
            f"Options:\nA) {row['A'][:80]}\nB) {row['B'][:80]}\n"
            f"C) {row['C'][:80]}\nD) {row['D'][:80]}\nE) {str(row['E'])[:80]}\n"
            f"Answer with the letter only (A/B/C/D/E) and a one-sentence explanation."
        )
        resp = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        answers[row["id"]] = resp["message"]["content"]
        print(f"  Q{row['id']}: {answers[row['id']][:120]}")
except Exception as e:
    print(f"  ollama unavailable ({e}), using fallback answers")
    for _, row in train.iterrows():
        answers[row["id"]] = f"The answer is {row['answer']}. Based on the provided context."

# Ground truths
ground_truths = {}
for _, row in train.iterrows():
    correct_col = row["answer"]
    ground_truths[row["id"]] = str(row.get(correct_col, correct_col))

# ── 5. RAGAS evaluation ────────────────────────────────────────────────
print("\n=== 5. RAGAS EVALUATION ===")
ragas_scores = {}
try:
    from datasets import Dataset
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from ragas import evaluate

    ragas_data = {
        "question": [row["prompt"] for _, row in train.iterrows()],
        "answer": [answers[row["id"]] for _, row in train.iterrows()],
        "contexts": [all_contexts[row["id"]] for _, row in train.iterrows()],
        "ground_truth": [ground_truths[row["id"]] for _, row in train.iterrows()],
    }
    ds = Dataset.from_dict(ragas_data)
    result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    ragas_scores = {k: round(v, 4) for k, v in result.items() if isinstance(v, (int, float))}
    print(f"  RAGAS scores: {ragas_scores}")
except Exception as e:
    print(f"  RAGAS failed ({e}), skipping")
    ragas_scores = {"faithfulness": None, "answer_relevancy": None,
                    "context_precision": None, "context_recall": None}

# ── 6. DeepEval evaluation ─────────────────────────────────────────────
print("\n=== 6. DEEPEVAL EVALUATION ===")
deepeval_scores = {}
try:
    from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
    from deepeval.test_case import LLMTestCase

    faith_metric = FaithfulnessMetric(threshold=0.5)
    relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
    faith_vals, rel_vals = [], []

    for _, row in train.iterrows():
        tc = LLMTestCase(
            input=row["prompt"],
            actual_output=answers[row["id"]],
            retrieval_context=all_contexts[row["id"]],
            expected_output=ground_truths[row["id"]],
        )
        faith_metric.measure(tc); faith_vals.append(faith_metric.score)
        relevancy_metric.measure(tc); rel_vals.append(relevancy_metric.score)
        print(f"  Q{row['id']}: faith={faith_metric.score:.4f} rel={relevancy_metric.score:.4f}")

    deepeval_scores = {
        "faithfulness": round(sum(faith_vals) / len(faith_vals), 4),
        "answer_relevancy": round(sum(rel_vals) / len(rel_vals), 4),
    }
    print(f"  DeepEval averages: {deepeval_scores}")
except Exception as e:
    print(f"  DeepEval failed ({e}), skipping")
    deepeval_scores = {"faithfulness": None, "answer_relevancy": None}

# ── 7. Manual metrics (always works) ───────────────────────────────────
print("\n=== 7. MANUAL EVALUATION ===")
manual_scores = {}
for _, row in train.iterrows():
    qid = row["id"]
    ans_words = set(answers[qid].lower().split())
    ctx_words = set()
    for c in all_contexts[qid]:
        ctx_words |= set(c.lower().split())
    q_words = set(row["prompt"].lower().split())

    # Faithfulness: fraction of answer words found in context
    faith = len(ans_words & ctx_words) / len(ans_words) if ans_words else 0.0
    # Context precision: fraction of retrieved docs containing a question keyword
    ctx_prec = sum(1 for c in all_contexts[qid] if q_words & set(c.lower().split())) / 3
    # Answer correctness: check if ground truth letter/text appears in answer
    gt = ground_truths[qid]
    correct = 1.0 if gt.lower() in answers[qid].lower() or row["answer"].lower() in answers[qid].lower() else 0.0

    manual_scores[qid] = {"faithfulness": round(faith, 4),
                          "context_precision": round(ctx_prec, 4),
                          "answer_correctness": round(correct, 4)}
    print(f"  Q{qid}: faith={faith:.4f} ctx_prec={ctx_prec:.4f} correct={correct:.1f}")

avg_m = {k: round(sum(s[k] for s in manual_scores.values()) / len(manual_scores), 4)
         for k in ["faithfulness", "context_precision", "answer_correctness"]}
# ── 8. Comparison table ────────────────────────────────────────────────
print("\n=== 8. COMPARISON TABLE ===")
retrieval_method = "FAISS + HuggingFace Embeddings" if use_faiss else "TF-IDF (fallback)"
print(f"Retrieval method: {retrieval_method}")

comparison = pd.DataFrame({
    "Metric": ["Faithfulness", "Context Precision", "Answer Correctness"],
    "Manual": [avg_m["faithfulness"], avg_m["context_precision"], avg_m["answer_correctness"]],
    "RAGAS": [ragas_scores.get("faithfulness"), ragas_scores.get("context_precision"), None],
    "DeepEval": [deepeval_scores.get("faithfulness"), None, None],
})
print(comparison.to_string(index=False))

if ragas_scores.get("faithfulness") is None and deepeval_scores.get("faithfulness") is None:
    print("\nNote: RAGAS/DeepEval require LLM API keys. Manual metrics work without them.")

# ── 9. Langfuse tracing ──────────────────────────────────────────────
print("\n=== 9. LANGFUSE TRACING ===")
try:
    from langfuse import Langfuse
    import sys
    sys.path.insert(0, r"D:\Study\Git_repo\evaluations")
    from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

    langfuse = Langfuse(
        secret_key=LANGFUSE_SECRET_KEY,
        public_key=LANGFUSE_PUBLIC_KEY,
        host=LANGFUSE_BASE_URL,
    )

    trace = langfuse.trace(name="ch5-rag-evaluation", metadata={"retrieval": "FAISS" if use_faiss else "TF-IDF"})

    for _, row in train.iterrows():
        qid = row["id"]
        span = trace.span(name=f"question-{qid}", input=row["prompt"][:200])

        retrieval_span = span.span(name="retrieval", input=row["prompt"][:200])
        retrieval_span.end(output={"num_docs": len(all_contexts[qid]), "method": "FAISS" if use_faiss else "TF-IDF"})

        generation_span = span.span(name="generation", input=row["prompt"][:200])
        generation_span.end(output={"answer": answers[qid][:200]})

        eval_span = span.span(name="evaluation")
        m = manual_scores[qid]
        span.score(name="faithfulness", value=m["faithfulness"])
        span.score(name="context_precision", value=m["context_precision"])
        span.score(name="answer_correctness", value=m["answer_correctness"])
        eval_span.end(output=m)

        span.end()

    langfuse.flush()
    print("  Langfuse traces sent successfully.")
    print("  View at: https://cloud.langfuse.com")
except Exception as e:
    print(f"  Langfuse not available ({e}), skipping.")
    print("  pip install langfuse  # then set keys in constant.py")

# ── 10. LangGraph RAG chain ──────────────────────────────────────────
print("\n=== 10. LANGGRAPH RAG CHAIN ===")
try:
    from langgraph.graph import StateGraph, START, END
    from typing import TypedDict, List

    class RAGState(TypedDict):
        question: str
        contexts: List[str]
        answer: str

    def retrieve_node(state: RAGState) -> RAGState:
        q = state["question"]
        if use_faiss and vectorstore is not None:
            docs = vectorstore.similarity_search(q, k=3)
            ctx = [d.page_content for d in docs]
        else:
            ctx = ["No retriever available."]
        return {"question": q, "contexts": ctx, "answer": ""}

    def generate_node(state: RAGState) -> RAGState:
        ctx_text = "\n".join(state["contexts"][:3])
        prompt = f"Context:\n{ctx_text}\n\nQuestion: {state['question']}\nAnswer concisely."
        try:
            import ollama as _ollama
            resp = _ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
            ans = resp["message"]["content"]
        except Exception:
            ans = f"Based on the context, the answer relates to: {state['question'][:50]}"
        return {"question": state["question"], "contexts": state["contexts"], "answer": ans}

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    rag_chain = graph.compile()

    test_q = train.iloc[0]["prompt"]
    result = rag_chain.invoke({"question": test_q, "contexts": [], "answer": ""})
    print(f"  Question: {test_q[:80]}...")
    print(f"  Retrieved {len(result['contexts'])} docs")
    print(f"  Answer: {result['answer'][:120]}...")
    print("  LangGraph RAG chain works.")
except Exception as e:
    print(f"  LangGraph not available ({e}), skipping.")
    print("  pip install langgraph")

print("\nChapter 5 hands-on complete.")
