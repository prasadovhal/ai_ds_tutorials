"""
Project 5: Continuous Evaluation System

Monitors model accuracy and performance over batches simulating data arrival over time.
Detects drift using chi-squared test, tracks accuracy trends, and flags regressions.
Compares 3 model versions (weak, medium, drifting) across batches.
"""
import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv, os, random

# === Load data ===
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
rows = []
with open(DATA_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)
print(f"Loaded {len(rows)} questions from train.csv\n")

# === Split into batches (simulating data arriving over time) ===
BATCH_SIZE = 20
batches = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
print(f"Split into {len(batches)} batches of ~{BATCH_SIZE} each\n")

# === Simulate 3 model versions ===
CHOICES = ["A", "B", "C", "D", "E"]
random.seed(42)

def model_v1(row):
    return row["answer"] if random.random() < 0.55 else random.choice(CHOICES)

def model_v2(row):
    return row["answer"] if random.random() < 0.72 else random.choice(CHOICES)

def model_v3(row):
    acc = max(0.45, 0.85 - getattr(model_v3, "_bi", 0) * 0.04)
    return row["answer"] if random.random() < acc else random.choice(CHOICES)

models = {"v1_weak": model_v1, "v2_medium": model_v2, "v3_drifting": model_v3}

# === Setup for drift detection ===
ACCURACY_THRESHOLD = 0.55
history = {name: [] for name in models}

def chi_squared(observed, expected_dist, n):
    chi2 = 0.0
    for key in CHOICES:
        obs, exp = observed.get(key, 0), expected_dist.get(key, 0) * n
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp
    return chi2

# Expected distribution from full dataset
ans_counts = {}
for row in rows:
    ans_counts[row["answer"]] = ans_counts.get(row["answer"], 0) + 1
expected_dist = {k: v / len(rows) for k, v in ans_counts.items()}

print("=" * 80)
print("CONTINUOUS EVALUATION TIMELINE")
print("=" * 80)

for bi, batch in enumerate(batches):
    model_v3._bi = bi
    print(f"\n--- Batch {bi + 1} ({len(batch)} questions) ---")

    batch_ans = {}
    for row in batch:
        batch_ans[row["answer"]] = batch_ans.get(row["answer"], 0) + 1

    chi2 = chi_squared(batch_ans, expected_dist, len(batch))
    drift = chi2 > 9.49  # critical value df=4, alpha=0.05
    tag = f"[DRIFT] Chi2={chi2:.2f} (>9.49) — distribution differs!" if drift else f"[OK]    Chi2={chi2:.2f} — consistent"
    print(f"  {tag}")

    for mname, mfn in models.items():
        correct = sum(1 for row in batch if mfn(row) == row["answer"])
        acc = correct / len(batch)
        history[mname].append(acc)
        recent = history[mname][-3:]
        rolling = sum(recent) / len(recent)
        alert = " ** ALERT: below threshold! **" if acc < ACCURACY_THRESHOLD else ""
        print(f"  {mname:15s}  batch_acc={acc:.2f}  rolling_avg={rolling:.2f}{alert}")

# === Detect trends ===
print("\n" + "=" * 80)
print("TREND ANALYSIS")
print("=" * 80)

def detect_trend(accs):
    n = len(accs)
    if n < 2:
        return "STABLE", 0.0
    xm, ym = (n - 1) / 2.0, sum(accs) / n
    num = sum((i - xm) * (a - ym) for i, a in enumerate(accs))
    den = sum((i - xm) ** 2 for i in range(n))
    slope = num / den if den > 0 else 0.0
    if slope > 0.01:
        return "IMPROVING", slope
    return ("DEGRADING", slope) if slope < -0.01 else ("STABLE", slope)

for mname in models:
    trend, slope = detect_trend(history[mname])
    avg = sum(history[mname]) / len(history[mname])
    print(f"  {mname:15s}  trend={trend:10s}  slope={slope:+.4f}  overall_avg={avg:.3f}")

# === ASCII timeline chart ===
print("\n" + "=" * 80)
print("ASCII ACCURACY CHART (per batch)")
print("=" * 80)

W = 40
sym = {"v1_weak": ".", "v2_medium": "o", "v3_drifting": "*"}
print(f"{'Batch':>6}  |{'0%':^{W // 2}}{'100%':>{W // 2}}|")
print(f"{'':>6}  +{'-' * W}+")

for bi in range(len(batches)):
    line = [" "] * W
    tp = int(ACCURACY_THRESHOLD * W)
    if 0 <= tp < W:
        line[tp] = "|"
    for mname in models:
        pos = min(int(history[mname][bi] * W), W - 1)
        line[pos] = sym[mname]
    print(f"  B{bi + 1:>3}  |{''.join(line)}|")

print(f"{'':>6}  +{'-' * W}+")
print(f"\n  Legend: .=v1_weak  o=v2_medium  *=v3_drifting  |=threshold({ACCURACY_THRESHOLD})")

# === Summary ===
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
alerts = sum(1 for n in models for a in history[n] if a < ACCURACY_THRESHOLD)
drifts = 0
for batch in batches:
    ba = {}
    for row in batch:
        ba[row["answer"]] = ba.get(row["answer"], 0) + 1
    if chi_squared(ba, expected_dist, len(batch)) > 9.49:
        drifts += 1

print(f"  Total batches processed:  {len(batches)}")
print(f"  Accuracy alerts fired:    {alerts}")
print(f"  Drift detections:         {drifts}")
print(f"  Models monitored:         {len(models)}")
print("\nDone.")
