"""
Chapter 9: Production Evaluation

Covers evaluation strategies for production LLM systems:
- Regression testing: preventing performance degradation
  * Accuracy thresholds: minimum acceptable performance
  * Latency limits: response time constraints
  * Allowed drift: acceptable variation from baseline
- Canary testing: gradual rollout with monitoring
- Shadow deployment: running new model without affecting users
- Drift detection: identifying performance degradation over time
- Monitoring: continuous tracking of metrics and alerts
- Alerting: triggering actions when thresholds violated
- CI/CD integration: evaluation gates blocking bad deployments
- Evaluation gates: quality checks before production release
- Prompt versioning: tracking prompt history and changes
- Dataset versioning: managing evaluation dataset versions
- Model versioning: tracking model lineage and changes
- Continuous benchmarking: tracking performance trends over time

Single-file version demonstrating production evaluation workflow.
"""

from statistics import mean


BASELINE_ACCURACY = 0.80
NEW_MODEL_ACCURACY = 0.76
LIVE_TRAFFIC = [
    {"day": "2026-08-20", "accuracy": 0.82, "latency_ms": 900},
    {"day": "2026-08-21", "accuracy": 0.81, "latency_ms": 950},
    {"day": "2026-08-22", "accuracy": 0.77, "latency_ms": 1200},
]


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def regression_status(old_score, new_score, limit=0.02):
    delta = new_score - old_score
    if delta < -limit:
        return {"delta": delta, "status": "fail"}
    return {"delta": delta, "status": "pass"}


def canary_result(canary_score, baseline_score):
    return canary_score >= baseline_score - 0.01


def shadow_result(primary_score, shadow_score):
    return {"primary": primary_score, "shadow": shadow_score, "difference": shadow_score - primary_score}


def drift_detected(history):
    first_half = mean(item["accuracy"] for item in history[:2])
    second_half = history[-1]["accuracy"]
    return abs(second_half - first_half) > 0.03


def average_latency(history):
    return mean(item["latency_ms"] for item in history)


def alert_needed(accuracy_value, latency_value):
    return accuracy_value < 0.78 or latency_value > 1100


def cicd_gate(accuracy_value, regression_result):
    return accuracy_value >= 0.78 and regression_result["status"] == "pass"


def prompt_version_compare(version_a, version_b):
    return version_b - version_a


def benchmark_trend(scores):
    return mean(scores)


def main():
    section("Chapter 9: Production Evaluation")

    section("1. Regression Testing")
    regression = regression_status(BASELINE_ACCURACY, NEW_MODEL_ACCURACY)
    print(regression)

    section("2. Canary Testing")
    print(f"Canary safe to expand: {canary_result(0.79, BASELINE_ACCURACY)}")

    section("3. Shadow Deployment")
    print(shadow_result(0.80, 0.78))

    section("4. Drift Detection")
    print(f"Drift detected: {drift_detected(LIVE_TRAFFIC)}")

    section("5. Monitoring")
    print(f"Average latency: {average_latency(LIVE_TRAFFIC):.1f} ms")

    section("6. Alerting")
    latest = LIVE_TRAFFIC[-1]
    print(f"Alert needed on {latest['day']}: {alert_needed(latest['accuracy'], latest['latency_ms'])}")

    section("7. CI/CD Gates")
    print(f"Deploy allowed: {cicd_gate(NEW_MODEL_ACCURACY, regression)}")

    section("8. Prompt Versioning")
    print(f"Prompt v2 improvement over v1: {prompt_version_compare(0.74, 0.79):+.2f}")

    section("9. Continuous Benchmarking")
    print(f"Average benchmark score: {benchmark_trend([0.78, 0.80, 0.81, 0.79]):.2f}")


if __name__ == "__main__":
    main()
