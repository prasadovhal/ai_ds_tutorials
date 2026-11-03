import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json, re

try:
    import requests
except ImportError:
    requests = None


def evaluate_accuracy(results, ground_truths=None):
    """Compute accuracy metrics from pipeline results."""
    if ground_truths is None:
        ground_truths = [r.get("ground_truth", "") for r in results]
    predictions = [r.get("predicted", "") for r in results]
    total = len(predictions)
    if total == 0:
        return {"accuracy": 0.0, "correct": 0, "total": 0}
    correct = sum(1 for p, g in zip(predictions, ground_truths) if p == g)
    return {"accuracy": round(correct / total, 4), "correct": correct, "total": total}


def evaluate_retrieval(results):
    """Evaluate retrieval quality (context precision and recall via heuristics)."""
    precision_scores, recall_scores = [], []
    for r in results:
        q_words = set(r.get("question", "").lower().split())
        c_words = set(r.get("context", "").lower().split())
        overlap = len(q_words & c_words)
        precision_scores.append(overlap / max(len(c_words), 1))
        recall_scores.append(overlap / max(len(q_words), 1))
    avg = lambda lst: round(sum(lst) / max(len(lst), 1), 4)
    return {"context_precision": avg(precision_scores),
            "context_recall": avg(recall_scores), "num_evaluated": len(results)}


def evaluate_generation(results):
    """Evaluate generation quality (faithfulness and relevance heuristics)."""
    faith_scores, rel_scores = [], []
    for r in results:
        context = r.get("context", "").lower()
        predicted = r.get("predicted", "").lower()
        faith_scores.append(1.0 if predicted in context else 0.5)
        rel_scores.append(1.0 if len(predicted.strip()) > 0 else 0.0)
    avg = lambda lst: round(sum(lst) / max(len(lst), 1), 4)
    return {"faithfulness": avg(faith_scores), "relevance": avg(rel_scores)}


def evaluate_latency(results):
    """Compute latency statistics from pipeline results."""
    latencies = sorted([r.get("latency", 0) for r in results])
    if not latencies:
        return {"p50": 0, "p95": 0, "avg": 0}
    n = len(latencies)
    return {"p50": round(latencies[n // 2], 4), "p95": round(latencies[int(n * 0.95)], 4),
            "avg": round(sum(latencies) / n, 4),
            "min": round(latencies[0], 4), "max": round(latencies[-1], 4)}


def judge_quality(question, answer):
    """Use Ollama as LLM judge; fallback to heuristic scoring."""
    if requests:
        try:
            prompt = (f"Rate this answer on a scale of 1-5 for correctness.\n"
                      f"Question: {question}\nAnswer: {answer}\n"
                      f"Return JSON: {{\"score\": <int>, \"reason\": \"<text>\"}}")
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False}, timeout=10)
            if resp.status_code == 200:
                data = json.loads(resp.json().get("response", ""))
                return {"score": data.get("score", 3), "reason": data.get("reason", "LLM judge")}
        except Exception:
            pass
    score = 4 if len(answer.strip()) == 1 and answer.strip().upper() in "ABCDE" else 3
    return {"score": score, "reason": "heuristic: valid format check"}


def full_evaluation(results, ground_truths=None):
    """Run all evaluation metrics and return combined results."""
    accuracy = evaluate_accuracy(results, ground_truths)
    retrieval = evaluate_retrieval(results)
    generation = evaluate_generation(results)
    latency = evaluate_latency(results)
    # Judge a sample (first 5) to save time
    judge_scores = [judge_quality(r["question"], r["predicted"]) for r in results[:5]]
    avg_judge = round(sum(j["score"] for j in judge_scores) / max(len(judge_scores), 1), 2)
    return {"accuracy": accuracy, "retrieval": retrieval, "generation": generation,
            "latency": latency,
            "judge": {"avg_score": avg_judge, "sample_size": len(judge_scores),
                      "details": judge_scores}}
