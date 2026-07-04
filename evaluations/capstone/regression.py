import sys, io
if sys.stdout.encoding != "utf-8" and hasattr(sys.stdout, "buffer"): sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def compare_versions(results_v1, results_v2, threshold=0.02):
    """Compare two sets of evaluation results and flag regressions."""
    comparisons = {}
    # Compare accuracy
    acc1 = results_v1.get("accuracy", {}).get("accuracy", 0)
    acc2 = results_v2.get("accuracy", {}).get("accuracy", 0)
    diff = round(acc2 - acc1, 4)
    comparisons["accuracy"] = {
        "v1": acc1, "v2": acc2, "diff": diff,
        "status": "REGRESSION" if diff < -threshold else
                  "IMPROVED" if diff > threshold else "STABLE",
    }
    # Compare retrieval precision
    rp1 = results_v1.get("retrieval", {}).get("context_precision", 0)
    rp2 = results_v2.get("retrieval", {}).get("context_precision", 0)
    diff_r = round(rp2 - rp1, 4)
    comparisons["retrieval_precision"] = {
        "v1": rp1, "v2": rp2, "diff": diff_r,
        "status": "REGRESSION" if diff_r < -threshold else
                  "IMPROVED" if diff_r > threshold else "STABLE",
    }
    # Compare latency (lower is better)
    lat1 = results_v1.get("latency", {}).get("avg", 0)
    lat2 = results_v2.get("latency", {}).get("avg", 0)
    diff_l = round(lat2 - lat1, 4)
    comparisons["latency_avg"] = {
        "v1": lat1, "v2": lat2, "diff": diff_l,
        "status": "REGRESSION" if diff_l > threshold else
                  "IMPROVED" if diff_l < -threshold else "STABLE",
    }
    # Overall verdict
    regressions = [k for k, v in comparisons.items() if v["status"] == "REGRESSION"]
    return {
        "comparisons": comparisons,
        "has_regression": len(regressions) > 0,
        "regressions": regressions,
        "verdict": "FAIL" if regressions else "PASS",
    }


def check_gates(metrics, min_accuracy=0.70, max_latency_p95=5.0,
                min_judge_score=2.5):
    """Check quality gates against minimum thresholds."""
    gates = {}
    # Accuracy gate
    acc = metrics.get("accuracy", {}).get("accuracy", 0)
    gates["accuracy"] = {
        "value": acc, "threshold": min_accuracy,
        "status": "PASS" if acc >= min_accuracy else "FAIL",
    }
    # Latency gate
    p95 = metrics.get("latency", {}).get("p95", 0)
    gates["latency_p95"] = {
        "value": p95, "threshold": max_latency_p95,
        "status": "PASS" if p95 <= max_latency_p95 else "FAIL",
    }
    # Judge score gate
    judge = metrics.get("judge", {}).get("avg_score", 0)
    gates["judge_score"] = {
        "value": judge, "threshold": min_judge_score,
        "status": "PASS" if judge >= min_judge_score else "FAIL",
    }
    failed = [k for k, v in gates.items() if v["status"] == "FAIL"]
    return {
        "gates": gates,
        "all_passed": len(failed) == 0,
        "failed": failed,
        "verdict": "PASS" if not failed else "FAIL",
    }
