"""
Project 8: CI/CD Evaluation Pipeline

Gated evaluation pipeline for model deployment with 6 stages:
load data, run inference (with latency), compute metrics, regression testing, quality gates, and report.
Checks accuracy thresholds, latency p95, and regressions before deployment approval.
"""
import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv, os, random, time
from sklearn.metrics import accuracy_score, recall_score

try:
    import json
except ImportError:
    json = None
    print("Warning: json not available, report saving skipped.")

# === Load golden dataset ===
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
rows = []
with open(DATA_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

CHOICES = ["A", "B", "C", "D", "E"]
random.seed(42)

# === Pipeline stages ===
def stage_load_data():
    t0 = time.time()
    truths = [row["answer"] for row in rows]
    return {"truths": truths, "count": len(rows), "ms": (time.time() - t0) * 1000, "status": "PASS"}

def stage_run_inference(rows, accuracy, model_name):
    t0 = time.time()
    preds, latencies = [], []
    for row in rows:
        if random.random() < accuracy:
            preds.append(row["answer"])
        else:
            preds.append(random.choice([c for c in CHOICES if c != row["answer"]]))
        latencies.append(random.uniform(50, 450) if accuracy > 0.70 else random.uniform(100, 600))
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    return {"preds": preds, "latencies": latencies, "p95_ms": p95,
            "ms": (time.time() - t0) * 1000, "model": model_name, "status": "PASS"}

def stage_compute_metrics(truths, preds):
    t0 = time.time()
    n = len(truths)
    accuracy = accuracy_score(truths, preds)
    recalls = recall_score(truths, preds, labels=CHOICES, average=None, zero_division=0.0)
    per_class = {c: recalls[i] for i, c in enumerate(CHOICES)}
    return {"accuracy": accuracy, "per_class": per_class, "correct": int(accuracy * n),
            "total": n, "ms": (time.time() - t0) * 1000, "status": "PASS"}

def stage_check_gates(m_base, m_cand, inf_cand):
    gates = []
    ok = True
    # Gate 1: min accuracy >= 0.70
    g1 = m_cand["accuracy"] >= 0.70
    gates.append({"gate": "min_accuracy >= 0.70", "val": f"{m_cand['accuracy']:.3f}", "res": "PASS" if g1 else "FAIL"})
    if not g1: ok = False
    # Gate 2: regression <= 2%
    reg = m_base["accuracy"] - m_cand["accuracy"]
    g2 = reg <= 0.02
    gates.append({"gate": "regression <= 2%", "val": f"{reg:+.3f}", "res": "PASS" if g2 else "FAIL"})
    if not g2: ok = False
    # Gate 3: no per-class below 0.50
    minc = min(m_cand["per_class"].values())
    mink = min(m_cand["per_class"], key=m_cand["per_class"].get)
    g3 = minc >= 0.50
    gates.append({"gate": "per_class >= 0.50", "val": f"{mink}={minc:.3f}", "res": "PASS" if g3 else "FAIL"})
    if not g3: ok = False
    # Gate 4: latency P95 <= 500ms
    p95 = inf_cand["p95_ms"]
    g4 = p95 <= 500.0
    gates.append({"gate": "latency_p95 <= 500ms", "val": f"{p95:.1f}ms", "res": "PASS" if g4 else "FAIL"})
    if not g4: ok = False
    return {"gates": gates, "all_pass": ok, "status": "PASS" if ok else "FAIL"}

def stage_generate_report(data, path):
    if not json:
        return {"path": path, "status": "SKIP"}
    report = {}
    for key, val in data.items():
        if isinstance(val, dict):
            report[key] = {k: v for k, v in val.items() if k not in ("truths", "preds", "latencies")}
        else:
            report[key] = val
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return {"path": path, "status": "PASS"}

# === Run pipeline for a model ===
def run_pipeline(model_name, accuracy):
    print(f"\n{'=' * 70}")
    print(f"  PIPELINE RUN: {model_name} (accuracy ~ {accuracy:.0%})")
    print(f"{'=' * 70}")
    # Stage 1
    print("\n  [1/5] load_data ........", end=" ")
    data = stage_load_data()
    print(f"{data['status']} ({data['count']} rows, {data['ms']:.1f}ms)")
    # Stage 2
    print(f"  [2/5] run_inference ....", end=" ")
    inf = stage_run_inference(rows, accuracy, model_name)
    print(f"{inf['status']} (P95={inf['p95_ms']:.1f}ms)")
    # Stage 3
    print(f"  [3/5] compute_metrics .", end=" ")
    met = stage_compute_metrics(data["truths"], inf["preds"])
    print(f"{met['status']} (accuracy={met['accuracy']:.3f})")
    return {"model": model_name, "load": data, "inference": inf, "metrics": met}, data, inf, met

# Run baseline + candidate
v1r, v1d, v1i, v1m = run_pipeline("model_v1_baseline", 0.74)
v2r, v2d, v2i, v2m = run_pipeline("model_v2_candidate", 0.82)

# Stage 4: Gates
print(f"\n{'=' * 70}")
print("  QUALITY GATES CHECK")
print(f"{'=' * 70}")
print(f"\n  [4/5] check_gates .....", end=" ")
gr = stage_check_gates(v1m, v2m, v2i)
print(gr["status"])

print(f"\n  {'Gate':<25} {'Value':<20} {'Result':<8}")
print(f"  {'-' * 55}")
for g in gr["gates"]:
    mark = "  OK" if g["res"] == "PASS" else "  XX"
    print(f"  {g['gate']:<25} {g['val']:<20} {g['res']:<8}{mark}")

# Stage 5: Report
pipe_all = {"baseline": v1r, "candidate": v2r, "gates": gr,
            "decision": "DEPLOY" if gr["all_pass"] else "BLOCK"}
rp = os.path.join(os.path.dirname(__file__), "pipeline_report.json")
print(f"\n  [5/5] generate_report .", end=" ")
rout = stage_generate_report(pipe_all, rp)
print(f"{rout['status']} -> {rout['path']}")

# === Final Decision ===
print(f"\n{'=' * 70}")
dec = "PASS --> DEPLOY model_v2_candidate" if gr["all_pass"] else "FAIL --> BLOCK model_v2_candidate"
print(f"  PIPELINE RESULT: {dec}")
print(f"{'=' * 70}")

# Comparison summary
print(f"\n  COMPARISON SUMMARY:")
print(f"    {'Metric':<25} {'Baseline':>12} {'Candidate':>12} {'Delta':>10}")
print(f"    {'-' * 60}")
print(f"    {'Accuracy':<25} {v1m['accuracy']:>11.3f} {v2m['accuracy']:>11.3f} {v2m['accuracy']-v1m['accuracy']:>+9.3f}")
print(f"    {'P95 Latency (ms)':<25} {v1i['p95_ms']:>11.1f} {v2i['p95_ms']:>11.1f} {v2i['p95_ms']-v1i['p95_ms']:>+9.1f}")
for c in CHOICES:
    v1v, v2v = v1m["per_class"][c], v2m["per_class"][c]
    print(f"    {'Class ' + c + ' accuracy':<25} {v1v:>11.3f} {v2v:>11.3f} {v2v-v1v:>+9.3f}")

print(f"\n  Report saved to: {rp}")
print("Done.")
