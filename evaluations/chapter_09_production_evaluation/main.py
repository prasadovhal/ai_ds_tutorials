"""
Chapter 9 - Production Evaluation
Demonstrates regression testing, canary/shadow deployments, drift detection,
monitoring, alerting, CI/CD gates, prompt versioning, and continuous benchmarking.
"""

import sys
import io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from dataset import (
    load_sample_data,
    load_train_data,
    simulate_llm_predictions,
    simulate_model_versions,
    simulate_production_traffic,
    simulate_drift_scenario,
    simulate_canary_traffic,
    create_golden_dataset,
    create_dataset_versions,
)
from evaluator import (
    RegressionTestSuite,
    CanaryDeployer,
    ShadowEvaluator,
    DriftDetector,
    ProductionMonitor,
    AlertManager,
    PromptVersionManager,
    DeploymentPipeline,
    ContinuousBenchmark,
    compute_accuracy,
)

SEPARATOR = "=" * 70


def print_header(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


# ── Load data ──────────────────────────────────────────────────────────────

print_header("CHAPTER 9: PRODUCTION EVALUATION")

questions = load_train_data(limit=100)
sample_data = load_sample_data()
print(f"  Loaded {len(questions)} questions, sample keys: {list(sample_data.keys())}")


# ── 1. Regression Testing ─────────────────────────────────────────────────

print_header("1. REGRESSION TESTING")

golden = create_golden_dataset(questions, limit=50)
print(f"  Golden dataset: v{golden['version']}, {golden['num_questions']} questions")
print(f"  Answer distribution: {golden['metadata']['answer_distribution']}")

baseline_preds = simulate_llm_predictions(golden["questions"], accuracy=0.78, seed=10)
new_preds_good = simulate_llm_predictions(golden["questions"], accuracy=0.82, seed=20)
new_preds_bad = simulate_llm_predictions(golden["questions"], accuracy=0.60, seed=30)

suite = RegressionTestSuite(golden, threshold=0.05)

result_good = suite.run(new_preds_good, baseline_preds, version_label="v1.1-improved")
print(f"\n{suite.format_report(result_good)}")

result_bad = suite.run(new_preds_bad, baseline_preds, version_label="v2.0-regression")
print(f"\n{suite.format_report(result_bad)}")

if result_bad.get("regression_details"):
    print(f"\n  First 3 regressions:")
    for r in result_bad["regression_details"][:3]:
        print(f"    Q{r['question_id']}: expected={r['ground_truth']}, "
              f"was={r['old_prediction']}, now={r['new_prediction']}")


# ── 2. Canary Testing ─────────────────────────────────────────────────────

print_header("2. CANARY TESTING")

canary_data = simulate_canary_traffic(
    questions,
    control_accuracy=0.80,
    canary_accuracy=0.72,
    total_requests=200,
    canary_percentage=0.15,
    seed=42,
)
print(f"  Total: {canary_data['total_requests']} requests  "
      f"Control: {canary_data['control_count']}  Canary: {canary_data['canary_count']}")

deployer = CanaryDeployer(accuracy_threshold=0.70, max_regression_rate=0.10)
rollout = deployer.simulate_rollout(canary_data["control_logs"], canary_data["canary_logs"])
print(f"\n{deployer.format_rollout_report(rollout)}")

print(f"\n  --- Successful canary (high-quality model) ---")
canary_good = simulate_canary_traffic(
    questions, control_accuracy=0.80, canary_accuracy=0.84,
    total_requests=200, canary_percentage=0.15, seed=99,
)
deployer2 = CanaryDeployer(accuracy_threshold=0.70, max_regression_rate=0.10)
rollout2 = deployer2.simulate_rollout(canary_good["control_logs"], canary_good["canary_logs"])
print(f"\n{deployer2.format_rollout_report(rollout2)}")


# ── 3. Shadow Deployment ──────────────────────────────────────────────────

print_header("3. SHADOW DEPLOYMENT")

subset = questions[:50]
primary_preds = simulate_llm_predictions(subset, accuracy=0.80, seed=100)
shadow_preds = simulate_llm_predictions(subset, accuracy=0.85, seed=200)

evaluator = ShadowEvaluator(primary_label="v1.1", shadow_label="v2.1")
comparison = evaluator.compare(subset, primary_preds, shadow_preds)
print(evaluator.format_report(comparison))

print(f"\n  --- Shadow with worse performance ---")
shadow_bad = simulate_llm_predictions(subset, accuracy=0.65, seed=300)
evaluator2 = ShadowEvaluator(primary_label="v1.1", shadow_label="v2.0-beta")
comparison2 = evaluator2.compare(subset, primary_preds, shadow_bad)
print(evaluator2.format_report(comparison2))


# ── 4. Drift Detection ────────────────────────────────────────────────────

print_header("4. DRIFT DETECTION")

windows = simulate_drift_scenario(questions, num_windows=6, window_size=30, seed=42)

detector = DriftDetector(
    kl_threshold=0.10,
    length_drift_threshold=0.15,
    accuracy_drift_threshold=0.08,
)

print("  Window-by-window drift analysis (reference = window 0):\n")
reference = windows[0]
for w in windows[1:]:
    analysis = detector.full_drift_analysis(reference, w)
    severity = analysis["severity"].upper()
    inp = "DRIFT" if analysis["input_drift"]["drifted"] else "ok"
    out = "DRIFT" if analysis["output_drift"]["drifted"] else "ok"
    con = "DRIFT" if analysis["concept_drift"]["drifted"] else "ok"
    print(f"  Window {w['window_id']}: drift_factor={w['drift_factor']:.2f}  "
          f"accuracy={w['accuracy']:.2%}  "
          f"input={inp:<5s}  output={out:<5s}  concept={con:<5s}  "
          f"severity={severity}")

print()
worst = windows[-1]
full_analysis = detector.full_drift_analysis(reference, worst)
print(detector.format_report(full_analysis))


# ── 5. Production Monitoring ──────────────────────────────────────────────

print_header("5. PRODUCTION MONITORING")

traffic = simulate_production_traffic(
    questions, model_version="v1.1", accuracy=0.80,
    num_requests=150, base_latency_ms=250.0, seed=42,
)

monitor = ProductionMonitor(window_size=50)
monitor.ingest_batch(traffic)

sliding = monitor.compute_sliding_windows(step=30)
print(f"  Ingested {len(traffic)} requests, {len(sliding)} sliding windows\n")

print(f"  {'Window':<10s} {'Requests':>9s} {'Accuracy':>9s} {'P50 (ms)':>9s} {'P95 (ms)':>9s}")
print(f"  {'-'*10} {'-'*9} {'-'*9} {'-'*9} {'-'*9}")
for i, w in enumerate(sliding):
    print(f"  {i:<10d} {w['window_size']:>9d} {w['accuracy']:>8.2%} "
          f"{w.get('latency_p50_ms', 0):>8.1f} {w.get('latency_p95_ms', 0):>8.1f}")

trend = monitor.get_trend("accuracy")
print(f"\n  Accuracy trend: {trend['trend']} (slope={trend.get('slope', 'N/A')})")


# ── 6. Alerting ────────────────────────────────────────────────────────────

print_header("6. ALERTING")

alert_mgr = AlertManager()

alert_mgr.add_threshold_rule("low_accuracy", "accuracy", "<=", 0.72, severity="warning")
alert_mgr.add_threshold_rule("critical_accuracy", "accuracy", "<=", 0.60, severity="critical")
alert_mgr.add_threshold_rule("high_latency_p95", "latency_p95_ms", ">=", 450, severity="warning")

healthy_accuracies = [0.78, 0.80, 0.79, 0.81, 0.80, 0.79]
alert_mgr.add_anomaly_rule("accuracy_anomaly", "accuracy", healthy_accuracies, sigma_threshold=2.0)

scenario = [
    {"label": "healthy",    "accuracy": 0.80, "latency_p95_ms": 400},
    {"label": "degrading",  "accuracy": 0.73, "latency_p95_ms": 420},
    {"label": "worse",      "accuracy": 0.68, "latency_p95_ms": 460},
    {"label": "critical",   "accuracy": 0.55, "latency_p95_ms": 510},
    {"label": "recovering", "accuracy": 0.75, "latency_p95_ms": 380},
    {"label": "recovered",  "accuracy": 0.81, "latency_p95_ms": 390},
]

for metrics in scenario:
    label = metrics.pop("label")
    fired = alert_mgr.evaluate(metrics)
    if fired:
        print(f"  [{label}]")
        for a in fired:
            print(alert_mgr.format_alert(a))
    else:
        print(f"  [{label}] No alerts fired.")

summary = alert_mgr.get_alert_summary()
print(f"\n  Alert summary: {summary['total_alerts']} total")
print(f"  By severity: {summary['by_severity']}")
print(f"  By rule:     {summary['by_rule']}")


# ── 7. CI/CD Integration & Evaluation Gates ───────────────────────────────

print_header("7. CI/CD INTEGRATION & EVALUATION GATES")

pipeline = DeploymentPipeline()
pipeline.add_gate("accuracy_gate", "accuracy", ">=", 0.75,
                  description="Min 75% accuracy on golden set", blocking=True)
pipeline.add_gate("regression_gate", "regression_rate", "<=", 0.05,
                  description="Max 5% regression rate", blocking=True)
pipeline.add_gate("latency_gate", "p95_latency_ms", "<=", 500,
                  description="P95 latency under 500ms", blocking=True)
pipeline.add_gate("drift_gate", "kl_divergence", "<=", 0.10,
                  description="Output drift within tolerance", blocking=False)

good_metrics = {"accuracy": 0.83, "regression_rate": 0.03, "p95_latency_ms": 380, "kl_divergence": 0.05}
result_v21 = pipeline.run(good_metrics, version_label="v2.1")
print(pipeline.format_pipeline_report(result_v21))

print()
bad_metrics = {"accuracy": 0.65, "regression_rate": 0.12, "p95_latency_ms": 350, "kl_divergence": 0.08}
result_v20 = pipeline.run(bad_metrics, version_label="v2.0")
print(pipeline.format_pipeline_report(result_v20))


# ── 8. Prompt / Dataset / Model Versioning ────────────────────────────────

print_header("8. PROMPT / DATASET / MODEL VERSIONING")

print("  --- Prompt Versioning ---\n")
pvm = PromptVersionManager()

prompts = sample_data["prompt_versions"]
hashes = {}
for name, info in prompts.items():
    h = pvm.register(info["template"], label=name)
    pvm.set_active(h)
    pvm.log_performance(h, {
        "accuracy": info["performance"]["accuracy"],
        "latency_ms": info["performance"]["avg_latency_ms"],
    })
    hashes[name] = h

print(pvm.format_version_table())

cmp = pvm.compare_versions(hashes["prompt_v1"], hashes["prompt_v2.1"])
print(f"\n  Comparing {cmp['version_a']['label']} vs {cmp['version_b']['label']}:")
print(f"    Lines added: {cmp['lines_added']}, removed: {cmp['lines_removed']}")
print(f"    Accuracy: {cmp['avg_accuracy_a']:.2%} -> {cmp['avg_accuracy_b']:.2%}")

rolled = pvm.rollback()
active_label = pvm.versions[pvm.active_hash]["label"]
print(f"\n  Rolled back to: {active_label} (hash: {pvm.active_hash})")

print(f"\n  --- Dataset Versioning ---\n")
ds_versions = create_dataset_versions(questions)
for ds in ds_versions:
    print(f"  Dataset v{ds['version']}: {ds['num_questions']} questions, "
          f"distribution={ds['metadata']['answer_distribution']}")

print(f"\n  --- Model Versioning ---\n")
for ver, info in sample_data["model_versions"].items():
    print(f"  {ver}: acc={info['expected_accuracy']:.0%}, "
          f"prompt={info['prompt_version']}, status={info['status']}")


# ── 9. Continuous Benchmarking ─────────────────────────────────────────────

print_header("9. CONTINUOUS BENCHMARKING")

bench = ContinuousBenchmark()

for entry in sample_data["continuous_benchmarks"]:
    bench.record(
        version=entry["version"],
        accuracy=entry["accuracy"],
        latency_p50_ms=entry["latency_p50_ms"],
        latency_p95_ms=entry["latency_p95_ms"],
        metadata={"date": entry["date"]},
    )

bench.set_baseline("initial_release", "v1.0")

print(bench.format_comparison_table())
print()
print(bench.format_history_chart("accuracy", width=35))

print()
acc_trend = bench.get_trend("accuracy")
lat_trend = bench.get_trend("latency_p50_ms")
print(f"  Accuracy trend:    {acc_trend['direction']} "
      f"(slope={acc_trend['slope']}, best={acc_trend['best']:.2%}, "
      f"worst={acc_trend['worst']:.2%})")
print(f"  Latency P50 trend: {lat_trend['direction']} "
      f"(slope={lat_trend['slope']}, best={lat_trend['best']:.0f}ms, "
      f"worst={lat_trend['worst']:.0f}ms)")

cmp_bl = bench.compare_to_baseline("v2.1", "initial_release")
print(f"\n  v2.1 vs baseline (v1.0):")
print(f"    Accuracy: {cmp_bl['accuracy_baseline']:.2%} -> "
      f"{cmp_bl['accuracy_current']:.2%} ({cmp_bl['accuracy_delta']:+.2%})")
print(f"    Latency P50: {cmp_bl['latency_p50_baseline']:.0f}ms -> "
      f"{cmp_bl['latency_p50_current']:.0f}ms ({cmp_bl['latency_p50_delta']:+.0f}ms)")


# ── Summary ────────────────────────────────────────────────────────────────

print_header("SUMMARY")
print("  1. Regression Testing   - Catch accuracy regressions before release")
print("  2. Canary Testing       - Gradual rollout with automatic rollback")
print("  3. Shadow Deployment    - Risk-free A/B comparison on live traffic")
print("  4. Drift Detection      - Detect input/output/concept distribution shifts")
print("  5. Monitoring           - Sliding-window metrics for real-time tracking")
print("  6. Alerting             - Threshold + anomaly alerts with escalation")
print("  7. CI/CD Gates          - Automated pass/fail deployment decisions")
print("  8. Versioning           - Track prompts, datasets, and models over time")
print("  9. Continuous Benchmark - Long-term performance trending and charts")
print(f"\n{SEPARATOR}")
