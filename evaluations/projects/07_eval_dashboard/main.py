import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""Project 7: Evaluation Dashboard — comprehensive metrics and ASCII visualizations."""
import csv, os, random

# === Load data ===
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
rows = []
with open(DATA_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)
print(f"Loaded {len(rows)} questions\n")

# === Simulate predictions from 3 models ===
CHOICES = ["A", "B", "C", "D", "E"]
random.seed(42)

def simulate(rows, accuracy):
    preds = []
    for row in rows:
        if random.random() < accuracy:
            preds.append(row["answer"])
        else:
            preds.append(random.choice([c for c in CHOICES if c != row["answer"]]))
    return preds

configs = [("GPT-Basic", 0.60), ("Claude-Mid", 0.78), ("DeepEval-Pro", 0.88)]
models = {name: simulate(rows, acc) for name, acc in configs}
truths = [row["answer"] for row in rows]

# === Compute metrics ===
def compute_metrics(truths, preds, name):
    n = len(truths)
    accuracy = sum(1 for t, p in zip(truths, preds) if t == p) / n
    # Per-class accuracy
    cc, ct = {c: 0 for c in CHOICES}, {c: 0 for c in CHOICES}
    for t, p in zip(truths, preds):
        ct[t] += 1
        if t == p: cc[t] += 1
    pca = {c: cc[c] / ct[c] if ct[c] > 0 else 0.0 for c in CHOICES}
    # F1 per class -> macro F1
    f1s = {}
    for c in CHOICES:
        tp = sum(1 for t, p in zip(truths, preds) if t == c and p == c)
        fp = sum(1 for t, p in zip(truths, preds) if t != c and p == c)
        fn = sum(1 for t, p in zip(truths, preds) if t == c and p != c)
        pr = tp / (tp + fp) if tp + fp > 0 else 0.0
        rc = tp / (tp + fn) if tp + fn > 0 else 0.0
        f1s[c] = 2 * pr * rc / (pr + rc) if pr + rc > 0 else 0.0
    macro_f1 = sum(f1s.values()) / len(f1s)
    # Confusion matrix
    cm = {t: {p: 0 for p in CHOICES} for t in CHOICES}
    for t, p in zip(truths, preds):
        cm[t][p] += 1
    errors = [i for i, (t, p) in enumerate(zip(truths, preds)) if t != p]
    return {"name": name, "accuracy": accuracy, "pca": pca, "macro_f1": macro_f1,
            "f1s": f1s, "cm": cm, "errors": errors}

all_m = [compute_metrics(truths, models[n], n) for n, _ in configs]

# === Build Dashboard ===
lines = []
def out(t=""):
    lines.append(t)
    print(t)

out("=" * 80)
out("                     EVALUATION DASHBOARD")
out("=" * 80)

# Section 1: Model Comparison Bars
out("\n--- MODEL COMPARISON ---")
out(f"{'Model':<16} {'Accuracy':>8}  {'F1':>6}  Bar")
out("-" * 60)
for m in all_m:
    bl = int(m["accuracy"] * 40)
    out(f"  {m['name']:<14} {m['accuracy']:>7.1%}  {m['macro_f1']:>5.3f}  [{'#' * bl + '.' * (40 - bl)}]")

# Section 2: Per-Class Accuracy
out("\n--- PER-CLASS ACCURACY ---")
out(f"{'Model':<16}" + "".join(f"{'  ' + c:>8}" for c in CHOICES))
out("-" * 60)
for m in all_m:
    out(f"  {m['name']:<14}" + "".join(f"{m['pca'][c]:>8.1%}" for c in CHOICES))

# Section 3: Confusion Matrix for best model
best = max(all_m, key=lambda m: m["accuracy"])
out(f"\n--- CONFUSION MATRIX: {best['name']} (best) ---")
out(f"{'True\\Pred':>10}" + "".join(f"{c:>6}" for c in CHOICES) + "  | Tot")
out("-" * 48)
for t in CHOICES:
    rv = "".join(f"{best['cm'][t][p]:>6}" for p in CHOICES)
    out(f"  {t:>8}{rv}  | {sum(best['cm'][t].values()):>3}")

# Section 4: Accuracy Trend over Time Windows
out("\n--- ACCURACY TREND (time windows) ---")
WS = 25
nw = len(rows) // WS
for mi in all_m:
    preds = models[mi["name"]]
    out(f"\n  {mi['name']}:")
    for w in range(nw):
        s, e = w * WS, (w + 1) * WS
        wa = sum(1 for t, p in zip(truths[s:e], preds[s:e]) if t == p) / WS
        bl = int(wa * 30)
        mark = " <<" if wa < 0.50 else ""
        out(f"    W{w+1:>2}: {wa:>5.1%} [{'=' * bl:<30}]{mark}")

# Section 5: Error Distribution
out("\n--- ERROR DISTRIBUTION ---")
out(f"{'Model':<16} {'Errors':>7} {'Err%':>6}  Most confused pair")
out("-" * 58)
for m in all_m:
    ne = len(m["errors"])
    mp, mc = ("?", "?"), 0
    for t in CHOICES:
        for p in CHOICES:
            if t != p and m["cm"][t][p] > mc:
                mc = m["cm"][t][p]
                mp = (t, p)
    out(f"  {m['name']:<14} {ne:>6}  {ne/len(rows):>5.1%}  True={mp[0]}->Pred={mp[1]} ({mc}x)")

# Section 6: Top-5 Hardest Questions
out("\n--- TOP-5 HARDEST QUESTIONS (wrong by all models) ---")
errcnt = {}
for i in range(len(rows)):
    errcnt[i] = sum(1 for n, _ in configs if models[n][i] != truths[i])
hardest = sorted(errcnt, key=lambda i: -errcnt[i])[:5]
out(f"{'Rank':<6}{'ID':>5} {'Wrong':>6} {'Ans':>5}  Prompt (first 55 chars)")
out("-" * 65)
for rank, idx in enumerate(hardest, 1):
    r = rows[idx]
    out(f"  {rank:<4} {r['id']:>5} {errcnt[idx]:>4}/3  {r['answer']:>4}  {r['prompt'][:55].replace(chr(10),' ')}...")

# Summary
out("\n" + "=" * 80)
worst = min(all_m, key=lambda m: m["accuracy"])
allw = sum(1 for i in range(len(rows)) if errcnt[i] == len(configs))
out(f"  Best:  {best['name']} (acc={best['accuracy']:.1%}, F1={best['macro_f1']:.3f})")
out(f"  Worst: {worst['name']} (acc={worst['accuracy']:.1%}, F1={worst['macro_f1']:.3f})")
out(f"  Questions wrong by ALL models: {allw}")
out("=" * 80)

# Save
rp = os.path.join(os.path.dirname(__file__), "dashboard_report.txt")
with open(rp, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"\nDashboard saved to: {rp}")
print("Done.")
