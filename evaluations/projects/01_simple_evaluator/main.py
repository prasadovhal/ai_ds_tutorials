"""
Project 1: Simple Evaluator

Comprehensive multi-metric evaluator for classification predictions.
Computes accuracy, per-class accuracy, confusion matrix, BLEU, and ROUGE scores.
Compares random vs smart predictors and saves results to JSON.
"""
import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv, json, random, os
from collections import Counter

# --- Load sklearn metrics (fallback if missing) ---
try:
    from sklearn.metrics import accuracy_score, confusion_matrix
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("[WARN] sklearn not found — using manual accuracy/confusion matrix")

# --- Load BLEU / ROUGE (fallback if missing) ---
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    HAS_BLEU = True
except ImportError:
    HAS_BLEU = False
    print("[WARN] nltk not found — skipping BLEU")

try:
    from rouge_score import rouge_scorer
    HAS_ROUGE = True
except ImportError:
    HAS_ROUGE = False
    print("[WARN] rouge-score not found — skipping ROUGE")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")
LABELS = ["A", "B", "C", "D", "E"]

# ── 1. Load data ─────────────────────────────────────────────────────────────
def load_data(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

# ── 2. Simulated predictors ─────────────────────────────────────────────────
def predict_random(rows):
    return [random.choice(LABELS) for _ in rows]

def predict_smart(rows):
    """Picks the correct answer 60% of the time, random otherwise."""
    preds = []
    for r in rows:
        if random.random() < 0.6:
            preds.append(r["answer"])
        else:
            preds.append(random.choice(LABELS))
    return preds

# ── 3. Metrics ───────────────────────────────────────────────────────────────
def compute_accuracy(y_true, y_pred):
    if HAS_SKLEARN:
        return accuracy_score(y_true, y_pred)
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)

def compute_per_class_accuracy(y_true, y_pred):
    per_class = {}
    for label in LABELS:
        indices = [i for i, y in enumerate(y_true) if y == label]
        if indices:
            per_class[label] = sum(y_pred[i] == label for i in indices) / len(indices)
        else:
            per_class[label] = 0.0
    return per_class

def compute_confusion(y_true, y_pred):
    if HAS_SKLEARN:
        cm = confusion_matrix(y_true, y_pred, labels=LABELS)
        return {LABELS[i]: {LABELS[j]: int(cm[i][j]) for j in range(5)} for i in range(5)}
    cm = {a: {b: 0 for b in LABELS} for a in LABELS}
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1
    return cm

def compute_bleu_rouge(rows, preds):
    """Compute BLEU/ROUGE between predicted answer text and gold answer text."""
    bleu_scores, rouge_scores = [], []
    for row, pred in zip(rows, preds):
        gold_text = row.get(row["answer"], "")
        pred_text = row.get(pred, "")
        if HAS_BLEU:
            ref = gold_text.split()
            hyp = pred_text.split()
            smooth = SmoothingFunction().method1
            bleu_scores.append(sentence_bleu([ref], hyp, smoothing_function=smooth))
        if HAS_ROUGE:
            scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
            sc = scorer.score(gold_text, pred_text)
            rouge_scores.append(sc["rougeL"].fmeasure)
    avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else None
    avg_rouge = sum(rouge_scores) / len(rouge_scores) if rouge_scores else None
    return avg_bleu, avg_rouge

# ── 4. Report ────────────────────────────────────────────────────────────────
def print_report(name, acc, per_class, cm, bleu, rouge):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Overall Accuracy : {acc:.4f}")
    print(f"  Per-class Accuracy:")
    for label, val in per_class.items():
        print(f"    {label}: {val:.4f}")
    print(f"  BLEU (avg)       : {bleu if bleu is not None else 'N/A'}")
    print(f"  ROUGE-L (avg)    : {rouge if rouge is not None else 'N/A'}")
    print(f"  Confusion Matrix :")
    print(f"    {'':>5}", "  ".join(f"{l:>5}" for l in LABELS))
    for row_label in LABELS:
        vals = "  ".join(f"{cm[row_label][c]:>5}" for c in LABELS)
        print(f"    {row_label:>5} {vals}")

# ── 5. Main ──────────────────────────────────────────────────────────────────
def main():
    print("Loading data ...")
    rows = load_data(DATA_PATH)
    y_true = [r["answer"] for r in rows]
    print(f"Loaded {len(rows)} questions  |  Label distribution: {dict(Counter(y_true))}")

    results = {}
    for name, predictor in [("Random", predict_random), ("Smart (60%)", predict_smart)]:
        preds = predictor(rows)
        acc = compute_accuracy(y_true, preds)
        per_class = compute_per_class_accuracy(y_true, preds)
        cm = compute_confusion(y_true, preds)
        bleu, rouge = compute_bleu_rouge(rows, preds)
        print_report(name, acc, per_class, cm, bleu, rouge)
        results[name] = {"accuracy": acc, "per_class": per_class,
                         "bleu": bleu, "rouge": rouge, "confusion": cm}

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {RESULTS_PATH}")

if __name__ == "__main__":
    main()
