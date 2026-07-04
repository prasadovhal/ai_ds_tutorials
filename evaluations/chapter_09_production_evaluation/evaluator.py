"""
Chapter 9 - Production Evaluation
Evaluator module: Production evaluation system implementations.

Classes:
  - RegressionTestSuite        : Run tests against golden datasets, report pass/fail
  - CanaryDeployer             : Simulate canary rollout with progressive evaluation
  - ShadowEvaluator            : Compare two model versions on same traffic
  - DriftDetector              : Detect distribution shifts in inputs/outputs
  - ProductionMonitor          : Track metrics over time windows
  - AlertManager               : Configurable alerts with escalation
  - PromptVersionManager       : Version, compare, and rollback prompts
  - DeploymentPipeline         : Full CI/CD simulation with evaluation gates
  - ContinuousBenchmark        : Track performance across versions with trend analysis
"""

import math
import time
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# 1. REGRESSION TESTING
# ---------------------------------------------------------------------------

class RegressionTestSuite:
    """
    Automated regression testing against golden datasets.

    Compares a new model's predictions against a golden dataset to detect
    regressions -- cases where a previously correct answer becomes wrong.

    Architecture:
        Golden Dataset (versioned)
            |
            v
        [Run Model] --> Predictions
            |
            v
        [Compare] --> {passed, failed, regressions, improvements}
            |
            v
        [Report] --> Pass/Fail decision
    """

    def __init__(self, golden_dataset: dict, threshold: float = 0.05):
        """
        Args:
            golden_dataset: Dict with 'questions' and 'ground_truths' keys.
            threshold: Max allowed regression rate (fraction of previously
                       correct answers that become wrong). Default 5%.
        """
        self.golden = golden_dataset
        self.threshold = threshold
        self.history = []

    def run(
        self,
        predictions: list[str],
        baseline_predictions: Optional[list[str]] = None,
        version_label: str = "unknown",
    ) -> dict:
        """
        Run regression tests.

        Args:
            predictions: New model's predictions (list of answer letters).
            baseline_predictions: Previous model's predictions for comparison.
                If None, compares only against ground truth.
            version_label: Label for this test run.

        Returns:
            Dict with test results including pass/fail, regressions, metrics.
        """
        ground_truths = self.golden["ground_truths"]
        n = len(ground_truths)

        if len(predictions) != n:
            raise ValueError(
                f"Expected {n} predictions, got {len(predictions)}"
            )

        # Basic accuracy
        correct = sum(1 for gt, p in zip(ground_truths, predictions) if gt == p)
        accuracy = correct / n

        result = {
            "version": version_label,
            "dataset_version": self.golden["version"],
            "total_questions": n,
            "correct": correct,
            "accuracy": round(accuracy, 4),
            "timestamp": datetime.now().isoformat(),
        }

        # Regression analysis (requires baseline)
        if baseline_predictions is not None:
            if len(baseline_predictions) != n:
                raise ValueError(
                    f"Baseline must have {n} predictions, got {len(baseline_predictions)}"
                )

            regressions = []
            improvements = []
            stable_correct = 0
            stable_wrong = 0

            for i, (gt, new_p, old_p) in enumerate(
                zip(ground_truths, predictions, baseline_predictions)
            ):
                old_correct = (gt == old_p)
                new_correct = (gt == new_p)

                if old_correct and not new_correct:
                    regressions.append({
                        "question_id": self.golden["questions"][i]["id"],
                        "ground_truth": gt,
                        "old_prediction": old_p,
                        "new_prediction": new_p,
                    })
                elif not old_correct and new_correct:
                    improvements.append({
                        "question_id": self.golden["questions"][i]["id"],
                        "ground_truth": gt,
                        "old_prediction": old_p,
                        "new_prediction": new_p,
                    })
                elif old_correct and new_correct:
                    stable_correct += 1
                else:
                    stable_wrong += 1

            baseline_correct = sum(
                1 for gt, p in zip(ground_truths, baseline_predictions) if gt == p
            )
            regression_rate = (
                len(regressions) / baseline_correct if baseline_correct > 0 else 0
            )

            result.update({
                "baseline_accuracy": round(baseline_correct / n, 4),
                "regressions": len(regressions),
                "regression_details": regressions,
                "improvements": len(improvements),
                "improvement_details": improvements,
                "stable_correct": stable_correct,
                "stable_wrong": stable_wrong,
                "regression_rate": round(regression_rate, 4),
                "passed": regression_rate <= self.threshold,
                "threshold": self.threshold,
            })
        else:
            result["passed"] = accuracy >= 0.75  # Default accuracy gate
            result["regressions"] = None
            result["regression_rate"] = None

        self.history.append(result)
        return result

    def get_history(self) -> list[dict]:
        """Return all test run results."""
        return self.history

    def format_report(self, result: dict) -> str:
        """Format a test result as a human-readable report."""
        lines = []
        status = "PASSED" if result["passed"] else "FAILED"
        lines.append(f"  Regression Test Report: {status}")
        lines.append(f"  {'=' * 50}")
        lines.append(f"  Model Version:   {result['version']}")
        lines.append(f"  Dataset Version: {result['dataset_version']}")
        lines.append(f"  Accuracy:        {result['accuracy']:.2%} "
                      f"({result['correct']}/{result['total_questions']})")

        if result.get("baseline_accuracy") is not None:
            lines.append(f"  Baseline:        {result['baseline_accuracy']:.2%}")
            delta = result["accuracy"] - result["baseline_accuracy"]
            direction = "+" if delta >= 0 else ""
            lines.append(f"  Delta:           {direction}{delta:.2%}")
            lines.append(f"  Regressions:     {result['regressions']} "
                          f"(rate: {result['regression_rate']:.2%}, "
                          f"threshold: {result['threshold']:.2%})")
            lines.append(f"  Improvements:    {result['improvements']}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. CANARY TESTING
# ---------------------------------------------------------------------------

class CanaryDeployer:
    """
    Simulate canary rollout with progressive traffic shifting and evaluation.

    Architecture:
        Traffic --> [Load Balancer]
                        |
                   +---------+---------+
                   |                   |
              [Control]           [Canary]
              (1 - pct)%           pct %
                   |                   |
              [Evaluate]          [Evaluate]
                   |                   |
                   +----> [Compare] <--+
                              |
                         [Promote / Rollback]
    """

    def __init__(
        self,
        stages: Optional[list[dict]] = None,
        min_requests_per_stage: int = 20,
        accuracy_threshold: float = 0.70,
        max_regression_rate: float = 0.10,
    ):
        """
        Args:
            stages: List of canary stages, each with 'percentage' and 'duration'.
                Default: [5%, 10%, 25%, 50%, 100%].
            min_requests_per_stage: Minimum canary requests before advancing.
            accuracy_threshold: Minimum accuracy for canary to pass.
            max_regression_rate: Maximum allowed regression rate vs control.
        """
        self.stages = stages or [
            {"percentage": 5, "label": "smoke_test"},
            {"percentage": 10, "label": "initial_canary"},
            {"percentage": 25, "label": "expanded_canary"},
            {"percentage": 50, "label": "half_traffic"},
            {"percentage": 100, "label": "full_rollout"},
        ]
        self.min_requests = min_requests_per_stage
        self.accuracy_threshold = accuracy_threshold
        self.max_regression_rate = max_regression_rate
        self.rollout_log = []

    def evaluate_stage(
        self,
        control_logs: list[dict],
        canary_logs: list[dict],
        stage: dict,
    ) -> dict:
        """Evaluate a single canary stage."""
        if not canary_logs:
            return {
                "stage": stage["label"],
                "percentage": stage["percentage"],
                "status": "skipped",
                "reason": "No canary traffic",
            }

        control_correct = sum(1 for r in control_logs if r["is_correct"])
        canary_correct = sum(1 for r in canary_logs if r["is_correct"])

        control_acc = control_correct / len(control_logs) if control_logs else 0
        canary_acc = canary_correct / len(canary_logs) if canary_logs else 0

        control_latencies = [r["latency_ms"] for r in control_logs]
        canary_latencies = [r["latency_ms"] for r in canary_logs]

        control_p50 = _percentile(control_latencies, 50) if control_latencies else 0
        canary_p50 = _percentile(canary_latencies, 50) if canary_latencies else 0

        # Decision
        passed = (
            canary_acc >= self.accuracy_threshold
            and (control_acc - canary_acc) <= self.max_regression_rate
        )

        result = {
            "stage": stage["label"],
            "percentage": stage["percentage"],
            "control_requests": len(control_logs),
            "canary_requests": len(canary_logs),
            "control_accuracy": round(control_acc, 4),
            "canary_accuracy": round(canary_acc, 4),
            "accuracy_delta": round(canary_acc - control_acc, 4),
            "control_p50_latency_ms": round(control_p50, 1),
            "canary_p50_latency_ms": round(canary_p50, 1),
            "passed": passed,
            "status": "advance" if passed else "rollback",
        }

        self.rollout_log.append(result)
        return result

    def simulate_rollout(
        self,
        control_logs: list[dict],
        canary_logs: list[dict],
    ) -> dict:
        """
        Simulate a full canary rollout through all stages.
        Uses the provided logs, splitting them proportionally per stage.
        """
        results = []
        final_status = "promoted"

        total_canary = len(canary_logs)
        used = 0

        for stage in self.stages:
            # Allocate a proportional slice of canary logs
            stage_size = max(
                self.min_requests,
                int(total_canary * stage["percentage"] / 100),
            )
            stage_canary = canary_logs[used:used + stage_size]
            used += stage_size

            if not stage_canary:
                results.append({
                    "stage": stage["label"],
                    "percentage": stage["percentage"],
                    "status": "skipped",
                    "reason": "Insufficient canary traffic",
                    "passed": True,
                })
                continue

            # Use corresponding control logs
            stage_control = control_logs[:len(stage_canary) * 5]

            result = self.evaluate_stage(stage_control, stage_canary, stage)
            results.append(result)

            if not result["passed"]:
                final_status = "rolled_back"
                break

        return {
            "stages": results,
            "final_status": final_status,
            "stages_completed": len(results),
            "total_stages": len(self.stages),
        }

    def format_rollout_report(self, rollout: dict) -> str:
        """Format rollout results as a readable report."""
        lines = []
        lines.append(f"  Canary Rollout: {rollout['final_status'].upper()}")
        lines.append(f"  {'=' * 55}")
        lines.append(f"  Stages completed: {rollout['stages_completed']}/{rollout['total_stages']}")
        lines.append("")
        lines.append(f"  {'Stage':<20s} {'%':>4s} {'Ctrl Acc':>9s} {'Canary':>9s} "
                      f"{'Delta':>7s} {'Status':>10s}")
        lines.append(f"  {'-'*20} {'-'*4} {'-'*9} {'-'*9} {'-'*7} {'-'*10}")

        for s in rollout["stages"]:
            if s.get("status") == "skipped":
                lines.append(
                    f"  {s['stage']:<20s} {s['percentage']:>3d}% "
                    f"{'':>9s} {'':>9s} {'':>7s} {'SKIPPED':>10s}"
                )
            else:
                delta_str = f"{s['accuracy_delta']:+.2%}"
                status_str = "PASS" if s["passed"] else "FAIL"
                lines.append(
                    f"  {s['stage']:<20s} {s['percentage']:>3d}% "
                    f"{s['control_accuracy']:>8.2%} {s['canary_accuracy']:>8.2%} "
                    f"{delta_str:>7s} {status_str:>10s}"
                )

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. SHADOW DEPLOYMENT
# ---------------------------------------------------------------------------

class ShadowEvaluator:
    """
    Compare two model versions running on the same traffic.

    The primary model serves responses; the shadow model runs in parallel
    but its responses are discarded. Both are evaluated offline.

    Architecture:
        Request --> [Primary Model v1.1] --> Response to user
            |
            +----> [Shadow Model v2.0]  --> Logged (not served)
                        |
                   [Compare Primary vs Shadow]
                        |
                   [Promotion Decision]
    """

    def __init__(self, primary_label: str = "primary", shadow_label: str = "shadow"):
        self.primary_label = primary_label
        self.shadow_label = shadow_label
        self.comparison_log = []

    def compare(
        self,
        questions: list[dict],
        primary_predictions: list[str],
        shadow_predictions: list[str],
    ) -> dict:
        """
        Compare primary and shadow model predictions on the same questions.
        """
        n = len(questions)
        ground_truths = [q["ground_truth"] for q in questions]

        primary_correct = 0
        shadow_correct = 0
        both_correct = 0
        both_wrong = 0
        primary_only_correct = 0
        shadow_only_correct = 0
        disagreements = []

        for i, (gt, p_pred, s_pred) in enumerate(
            zip(ground_truths, primary_predictions, shadow_predictions)
        ):
            p_ok = (gt == p_pred)
            s_ok = (gt == s_pred)

            if p_ok:
                primary_correct += 1
            if s_ok:
                shadow_correct += 1

            if p_ok and s_ok:
                both_correct += 1
            elif p_ok and not s_ok:
                primary_only_correct += 1
            elif not p_ok and s_ok:
                shadow_only_correct += 1
            else:
                both_wrong += 1

            if p_pred != s_pred:
                disagreements.append({
                    "question_id": questions[i]["id"],
                    "ground_truth": gt,
                    "primary_prediction": p_pred,
                    "shadow_prediction": s_pred,
                    "primary_correct": p_ok,
                    "shadow_correct": s_ok,
                })

        agreement_rate = sum(
            1 for p, s in zip(primary_predictions, shadow_predictions) if p == s
        ) / n

        result = {
            "total_questions": n,
            "primary_accuracy": round(primary_correct / n, 4),
            "shadow_accuracy": round(shadow_correct / n, 4),
            "both_correct": both_correct,
            "both_wrong": both_wrong,
            "primary_only_correct": primary_only_correct,
            "shadow_only_correct": shadow_only_correct,
            "agreement_rate": round(agreement_rate, 4),
            "disagreements_count": len(disagreements),
            "disagreement_details": disagreements[:10],  # First 10
            "recommendation": self._recommend(
                primary_correct / n, shadow_correct / n,
                primary_only_correct, shadow_only_correct, n
            ),
        }

        self.comparison_log.append(result)
        return result

    def _recommend(
        self,
        primary_acc: float,
        shadow_acc: float,
        primary_only: int,
        shadow_only: int,
        total: int,
    ) -> str:
        if shadow_acc > primary_acc + 0.02:
            return "PROMOTE: Shadow outperforms primary significantly"
        elif shadow_acc > primary_acc:
            return "CONSIDER: Shadow slightly better, run longer test"
        elif abs(shadow_acc - primary_acc) < 0.01:
            return "NEUTRAL: Performance equivalent, decide on other factors"
        elif primary_acc - shadow_acc < 0.05:
            return "CAUTION: Shadow slightly worse, investigate regressions"
        else:
            return "REJECT: Shadow significantly worse than primary"

    def format_report(self, result: dict) -> str:
        lines = []
        lines.append(f"  Shadow Deployment Analysis")
        lines.append(f"  {'=' * 55}")
        lines.append(f"  Primary ({self.primary_label}) accuracy: "
                      f"{result['primary_accuracy']:.2%}")
        lines.append(f"  Shadow  ({self.shadow_label}) accuracy:  "
                      f"{result['shadow_accuracy']:.2%}")
        lines.append(f"  Agreement rate:                "
                      f"{result['agreement_rate']:.2%}")
        lines.append(f"")
        lines.append(f"  Breakdown:")
        lines.append(f"    Both correct:         {result['both_correct']}")
        lines.append(f"    Both wrong:           {result['both_wrong']}")
        lines.append(f"    Primary only correct: {result['primary_only_correct']}")
        lines.append(f"    Shadow only correct:  {result['shadow_only_correct']}")
        lines.append(f"    Disagreements:        {result['disagreements_count']}")
        lines.append(f"")
        lines.append(f"  --> {result['recommendation']}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. DRIFT DETECTION
# ---------------------------------------------------------------------------

class DriftDetector:
    """
    Detect distribution shifts in inputs, outputs, and concepts.

    Drift types:
      - Input drift:   Distribution of incoming questions changes
      - Output drift:  Distribution of model predictions changes
      - Concept drift: Relationship between inputs and correct answers changes

    Architecture:
        [Reference Window] --+
                             |--> [Statistical Test] --> Drift Score
        [Current Window]  ---+                              |
                                                      [Threshold]
                                                            |
                                                    [Alert if exceeded]
    """

    def __init__(
        self,
        kl_threshold: float = 0.10,
        length_drift_threshold: float = 0.20,
        accuracy_drift_threshold: float = 0.10,
    ):
        self.kl_threshold = kl_threshold
        self.length_drift_threshold = length_drift_threshold
        self.accuracy_drift_threshold = accuracy_drift_threshold

    def detect_input_drift(
        self,
        reference_window: dict,
        current_window: dict,
    ) -> dict:
        """
        Detect drift in input distribution (question characteristics).
        Compares prompt length distributions and answer distributions.
        """
        ref_len = reference_window["avg_prompt_length"]
        cur_len = current_window["avg_prompt_length"]
        length_shift = abs(cur_len - ref_len) / ref_len if ref_len > 0 else 0

        # KL divergence on answer distribution
        ref_dist = reference_window["answer_distribution"]
        cur_dist = current_window["answer_distribution"]
        kl_div = _kl_divergence(ref_dist, cur_dist)

        input_drifted = (
            length_shift > self.length_drift_threshold
            or kl_div > self.kl_threshold
        )

        return {
            "drift_type": "input",
            "ref_avg_length": round(ref_len, 1),
            "cur_avg_length": round(cur_len, 1),
            "length_shift_pct": round(length_shift * 100, 1),
            "length_threshold_pct": round(self.length_drift_threshold * 100, 1),
            "answer_kl_divergence": round(kl_div, 4),
            "kl_threshold": self.kl_threshold,
            "drifted": input_drifted,
        }

    def detect_output_drift(
        self,
        reference_window: dict,
        current_window: dict,
    ) -> dict:
        """
        Detect drift in output distribution (prediction patterns).
        """
        ref_dist = reference_window["prediction_distribution"]
        cur_dist = reference_window.get("prediction_distribution", {})
        cur_dist = current_window["prediction_distribution"]
        kl_div = _kl_divergence(ref_dist, cur_dist)

        return {
            "drift_type": "output",
            "ref_distribution": ref_dist,
            "cur_distribution": cur_dist,
            "kl_divergence": round(kl_div, 4),
            "kl_threshold": self.kl_threshold,
            "drifted": kl_div > self.kl_threshold,
        }

    def detect_concept_drift(
        self,
        reference_window: dict,
        current_window: dict,
    ) -> dict:
        """
        Detect concept drift: accuracy degradation over time indicates
        the relationship between inputs and correct answers has changed.
        """
        ref_acc = reference_window["accuracy"]
        cur_acc = current_window["accuracy"]
        acc_delta = ref_acc - cur_acc

        return {
            "drift_type": "concept",
            "ref_accuracy": round(ref_acc, 4),
            "cur_accuracy": round(cur_acc, 4),
            "accuracy_delta": round(acc_delta, 4),
            "accuracy_threshold": self.accuracy_drift_threshold,
            "drifted": acc_delta > self.accuracy_drift_threshold,
        }

    def full_drift_analysis(
        self,
        reference_window: dict,
        current_window: dict,
    ) -> dict:
        """Run all drift detection methods and aggregate."""
        input_drift = self.detect_input_drift(reference_window, current_window)
        output_drift = self.detect_output_drift(reference_window, current_window)
        concept_drift = self.detect_concept_drift(reference_window, current_window)

        any_drift = (
            input_drift["drifted"]
            or output_drift["drifted"]
            or concept_drift["drifted"]
        )

        return {
            "input_drift": input_drift,
            "output_drift": output_drift,
            "concept_drift": concept_drift,
            "any_drift_detected": any_drift,
            "severity": self._severity(input_drift, output_drift, concept_drift),
        }

    def _severity(self, input_d: dict, output_d: dict, concept_d: dict) -> str:
        drift_count = sum([
            input_d["drifted"],
            output_d["drifted"],
            concept_d["drifted"],
        ])
        if drift_count == 0:
            return "none"
        elif drift_count == 1:
            return "low"
        elif drift_count == 2:
            return "medium"
        else:
            return "high"

    def format_report(self, analysis: dict) -> str:
        lines = []
        lines.append(f"  Drift Detection Report")
        lines.append(f"  {'=' * 55}")

        for dtype in ["input_drift", "output_drift", "concept_drift"]:
            d = analysis[dtype]
            status = "DRIFTED" if d["drifted"] else "STABLE"
            lines.append(f"  {d['drift_type'].upper():>10s} drift: {status}")

            if dtype == "input_drift":
                lines.append(f"    Length shift: {d['length_shift_pct']:.1f}% "
                              f"(threshold: {d['length_threshold_pct']:.1f}%)")
                lines.append(f"    KL divergence: {d['answer_kl_divergence']:.4f} "
                              f"(threshold: {d['kl_threshold']})")
            elif dtype == "output_drift":
                lines.append(f"    KL divergence: {d['kl_divergence']:.4f} "
                              f"(threshold: {d['kl_threshold']})")
            else:
                lines.append(f"    Accuracy: {d['ref_accuracy']:.2%} -> "
                              f"{d['cur_accuracy']:.2%} "
                              f"(delta: {d['accuracy_delta']:.2%})")

        lines.append(f"")
        lines.append(f"  Overall severity: {analysis['severity'].upper()}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 5. PRODUCTION MONITORING
# ---------------------------------------------------------------------------

class ProductionMonitor:
    """
    Real-time quality monitoring over sliding time windows.

    Tracks: accuracy, latency percentiles, error rates, throughput.

    Architecture:
        [Incoming Requests] --> [Log Entry]
                                    |
                               [Window Buffer]
                                    |
                            [Compute Metrics]
                                    |
                         [Dashboard / Alert Manager]
    """

    def __init__(self, window_size: int = 50):
        """
        Args:
            window_size: Number of recent requests to track per window.
        """
        self.window_size = window_size
        self.buffer = []
        self.metrics_history = []

    def ingest(self, log_entry: dict):
        """Add a log entry to the monitoring buffer."""
        self.buffer.append(log_entry)

    def ingest_batch(self, log_entries: list[dict]):
        """Add multiple log entries."""
        self.buffer.extend(log_entries)

    def compute_window_metrics(self, window: Optional[list[dict]] = None) -> dict:
        """Compute metrics for the current (or given) window."""
        if window is None:
            window = self.buffer[-self.window_size:]

        if not window:
            return {"error": "Empty window"}

        correct = sum(1 for r in window if r.get("is_correct", False))
        latencies = [r["latency_ms"] for r in window if "latency_ms" in r]

        metrics = {
            "window_size": len(window),
            "accuracy": round(correct / len(window), 4),
            "error_rate": round(1 - correct / len(window), 4),
            "total_requests": len(window),
        }

        if latencies:
            latencies_sorted = sorted(latencies)
            metrics.update({
                "latency_p50_ms": round(_percentile(latencies_sorted, 50), 1),
                "latency_p95_ms": round(_percentile(latencies_sorted, 95), 1),
                "latency_p99_ms": round(_percentile(latencies_sorted, 99), 1),
                "latency_mean_ms": round(sum(latencies) / len(latencies), 1),
                "latency_min_ms": round(min(latencies), 1),
                "latency_max_ms": round(max(latencies), 1),
            })

        # Prediction distribution
        pred_counts = Counter(r.get("prediction", "?") for r in window)
        metrics["prediction_distribution"] = dict(sorted(pred_counts.items()))

        # Model version distribution
        version_counts = Counter(r.get("model_version", "unknown") for r in window)
        metrics["model_versions"] = dict(sorted(version_counts.items()))

        self.metrics_history.append(metrics)
        return metrics

    def compute_sliding_windows(self, step: int = None) -> list[dict]:
        """Compute metrics across all sliding windows in the buffer."""
        if step is None:
            step = max(1, self.window_size // 2)

        windows = []
        for start in range(0, len(self.buffer), step):
            end = start + self.window_size
            window = self.buffer[start:end]
            if len(window) >= self.window_size // 2:  # Min half-window
                metrics = self.compute_window_metrics(window)
                metrics["window_start"] = start
                metrics["window_end"] = min(end, len(self.buffer))
                windows.append(metrics)

        return windows

    def get_trend(self, metric_name: str = "accuracy") -> dict:
        """Analyze trend for a given metric across the metrics history."""
        if len(self.metrics_history) < 2:
            return {"trend": "insufficient_data", "values": []}

        values = [
            m.get(metric_name)
            for m in self.metrics_history
            if m.get(metric_name) is not None
        ]

        if len(values) < 2:
            return {"trend": "insufficient_data", "values": values}

        # Simple linear trend
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0

        if slope > 0.001:
            direction = "improving"
        elif slope < -0.001:
            direction = "degrading"
        else:
            direction = "stable"

        return {
            "metric": metric_name,
            "trend": direction,
            "slope": round(slope, 6),
            "current": values[-1],
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "num_windows": n,
        }

    def format_metrics(self, metrics: dict) -> str:
        lines = []
        lines.append(f"    Accuracy:      {metrics.get('accuracy', 0):.2%}")
        lines.append(f"    Requests:      {metrics.get('total_requests', 0)}")
        if "latency_p50_ms" in metrics:
            lines.append(f"    Latency P50:   {metrics['latency_p50_ms']:.0f}ms")
            lines.append(f"    Latency P95:   {metrics['latency_p95_ms']:.0f}ms")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 6. ALERTING
# ---------------------------------------------------------------------------

class AlertManager:
    """
    Configurable alert system with threshold-based and anomaly-based alerts.

    Supports:
      - Threshold alerts: fire when metric crosses a boundary
      - Anomaly alerts: fire when metric deviates significantly from baseline
      - Escalation: alerts progress through severity levels

    Architecture:
        [Metrics] --> [Alert Rules Engine]
                           |
                    +------+------+
                    |             |
              [Threshold]   [Anomaly]
                    |             |
                    v             v
               [Alert Queue] <---+
                    |
              [Escalation]
                    |
              [Notification]
    """

    def __init__(self):
        self.rules = []
        self.alerts_fired = []
        self.alert_id_counter = 0

    def add_threshold_rule(
        self,
        name: str,
        metric: str,
        operator: str,
        threshold: float,
        severity: str = "warning",
        cooldown_count: int = 0,
    ):
        """
        Add a threshold-based alert rule.

        Args:
            name: Human-readable rule name.
            metric: Metric key to monitor.
            operator: One of '>=', '<=', '>', '<', '=='.
            threshold: Value to compare against.
            severity: 'info', 'warning', 'critical'.
            cooldown_count: Minimum alerts before escalation.
        """
        self.rules.append({
            "type": "threshold",
            "name": name,
            "metric": metric,
            "operator": operator,
            "threshold": threshold,
            "severity": severity,
            "cooldown_count": cooldown_count,
            "consecutive_fires": 0,
        })

    def add_anomaly_rule(
        self,
        name: str,
        metric: str,
        baseline_values: list[float],
        sigma_threshold: float = 2.0,
        severity: str = "warning",
    ):
        """
        Add an anomaly-based alert rule using standard deviation.
        Fires when current value is > sigma_threshold standard deviations
        from the mean of baseline_values.
        """
        if not baseline_values:
            return

        mean = sum(baseline_values) / len(baseline_values)
        variance = sum((x - mean) ** 2 for x in baseline_values) / len(baseline_values)
        std = math.sqrt(variance) if variance > 0 else 0.001

        self.rules.append({
            "type": "anomaly",
            "name": name,
            "metric": metric,
            "mean": mean,
            "std": std,
            "sigma_threshold": sigma_threshold,
            "severity": severity,
            "consecutive_fires": 0,
        })

    def evaluate(self, metrics: dict) -> list[dict]:
        """Evaluate all rules against current metrics. Return fired alerts."""
        fired = []

        for rule in self.rules:
            metric_val = metrics.get(rule["metric"])
            if metric_val is None:
                continue

            should_fire = False

            if rule["type"] == "threshold":
                should_fire = _check_threshold(
                    metric_val, rule["operator"], rule["threshold"]
                )
            elif rule["type"] == "anomaly":
                z_score = abs(metric_val - rule["mean"]) / rule["std"]
                should_fire = z_score > rule["sigma_threshold"]

            if should_fire:
                rule["consecutive_fires"] += 1
                severity = rule["severity"]

                # Escalation: after repeated fires, escalate severity
                if rule["consecutive_fires"] >= 3 and severity == "warning":
                    severity = "critical"

                self.alert_id_counter += 1
                alert = {
                    "alert_id": self.alert_id_counter,
                    "rule_name": rule["name"],
                    "rule_type": rule["type"],
                    "severity": severity,
                    "metric": rule["metric"],
                    "metric_value": metric_val,
                    "consecutive_fires": rule["consecutive_fires"],
                }

                if rule["type"] == "threshold":
                    alert["threshold"] = rule["threshold"]
                    alert["operator"] = rule["operator"]
                    alert["message"] = (
                        f"{rule['metric']} = {metric_val:.4f} "
                        f"{rule['operator']} {rule['threshold']}"
                    )
                else:
                    z_score = abs(metric_val - rule["mean"]) / rule["std"]
                    alert["z_score"] = round(z_score, 2)
                    alert["baseline_mean"] = round(rule["mean"], 4)
                    alert["baseline_std"] = round(rule["std"], 4)
                    alert["message"] = (
                        f"{rule['metric']} = {metric_val:.4f} "
                        f"(z-score: {z_score:.2f}, threshold: {rule['sigma_threshold']})"
                    )

                fired.append(alert)
                self.alerts_fired.append(alert)
            else:
                rule["consecutive_fires"] = 0

        return fired

    def get_alert_summary(self) -> dict:
        """Summarize all fired alerts."""
        by_severity = Counter(a["severity"] for a in self.alerts_fired)
        by_rule = Counter(a["rule_name"] for a in self.alerts_fired)
        return {
            "total_alerts": len(self.alerts_fired),
            "by_severity": dict(by_severity),
            "by_rule": dict(by_rule),
        }

    def format_alert(self, alert: dict) -> str:
        severity_icon = {
            "info": "[INFO]",
            "warning": "[WARN]",
            "critical": "[CRIT]",
        }
        icon = severity_icon.get(alert["severity"], "[????]")
        return (
            f"  {icon} Alert #{alert['alert_id']}: {alert['rule_name']}\n"
            f"         {alert['message']}\n"
            f"         Consecutive fires: {alert['consecutive_fires']}"
        )


# ---------------------------------------------------------------------------
# 7. PROMPT VERSION MANAGER
# ---------------------------------------------------------------------------

class PromptVersionManager:
    """
    Version, compare, and rollback prompt templates.

    Every prompt change is tracked with:
      - Version hash (content-addressable)
      - Performance metrics
      - Rollback capability

    Architecture:
        [New Prompt] --> [Hash & Version]
                              |
                         [Store in Registry]
                              |
                    +---------+---------+
                    |                   |
               [Evaluate]         [Compare]
                    |                   |
                    v                   v
              [Metrics Log]     [Diff Report]
                    |
               [Set Active / Rollback]
    """

    def __init__(self):
        self.versions = {}      # hash -> version_info
        self.active_hash = None
        self.version_order = []  # Ordered list of hashes
        self.performance_log = {}  # hash -> list of metric snapshots

    def register(
        self,
        template: str,
        label: str = "",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Register a new prompt version.
        Returns the version hash.
        """
        content_hash = hashlib.sha256(template.encode()).hexdigest()[:12]

        if content_hash not in self.versions:
            version_num = len(self.versions) + 1
            self.versions[content_hash] = {
                "hash": content_hash,
                "version_num": version_num,
                "label": label or f"v{version_num}",
                "template": template,
                "metadata": metadata or {},
                "registered_at": datetime.now().isoformat(),
            }
            self.version_order.append(content_hash)
            self.performance_log[content_hash] = []

        return content_hash

    def set_active(self, version_hash: str):
        """Set a version as the active prompt."""
        if version_hash not in self.versions:
            raise ValueError(f"Unknown version: {version_hash}")
        self.active_hash = version_hash

    def rollback(self) -> Optional[str]:
        """Rollback to the previous version. Returns the new active hash."""
        if len(self.version_order) < 2:
            return None

        current_idx = self.version_order.index(self.active_hash)
        if current_idx == 0:
            return None

        prev_hash = self.version_order[current_idx - 1]
        self.active_hash = prev_hash
        return prev_hash

    def log_performance(self, version_hash: str, metrics: dict):
        """Log performance metrics for a prompt version."""
        if version_hash in self.performance_log:
            self.performance_log[version_hash].append({
                "timestamp": datetime.now().isoformat(),
                **metrics,
            })

    def compare_versions(self, hash_a: str, hash_b: str) -> dict:
        """Compare two prompt versions."""
        if hash_a not in self.versions or hash_b not in self.versions:
            raise ValueError("One or both version hashes not found")

        va = self.versions[hash_a]
        vb = self.versions[hash_b]

        perf_a = self.performance_log.get(hash_a, [])
        perf_b = self.performance_log.get(hash_b, [])

        avg_acc_a = (
            sum(p.get("accuracy", 0) for p in perf_a) / len(perf_a)
            if perf_a else None
        )
        avg_acc_b = (
            sum(p.get("accuracy", 0) for p in perf_b) / len(perf_b)
            if perf_b else None
        )

        # Simple template diff: count changed lines
        lines_a = va["template"].splitlines()
        lines_b = vb["template"].splitlines()
        added = sum(1 for l in lines_b if l not in lines_a)
        removed = sum(1 for l in lines_a if l not in lines_b)

        return {
            "version_a": {"hash": hash_a, "label": va["label"]},
            "version_b": {"hash": hash_b, "label": vb["label"]},
            "template_a_length": len(va["template"]),
            "template_b_length": len(vb["template"]),
            "lines_added": added,
            "lines_removed": removed,
            "avg_accuracy_a": round(avg_acc_a, 4) if avg_acc_a is not None else None,
            "avg_accuracy_b": round(avg_acc_b, 4) if avg_acc_b is not None else None,
            "perf_samples_a": len(perf_a),
            "perf_samples_b": len(perf_b),
        }

    def get_all_versions(self) -> list[dict]:
        """Return all versions in order."""
        result = []
        for h in self.version_order:
            v = self.versions[h]
            perf = self.performance_log.get(h, [])
            avg_acc = (
                sum(p.get("accuracy", 0) for p in perf) / len(perf)
                if perf else None
            )
            result.append({
                "hash": h,
                "label": v["label"],
                "is_active": h == self.active_hash,
                "avg_accuracy": round(avg_acc, 4) if avg_acc is not None else None,
                "perf_samples": len(perf),
                "template_preview": v["template"][:80] + "..."
                    if len(v["template"]) > 80 else v["template"],
            })
        return result

    def format_version_table(self) -> str:
        lines = []
        lines.append(f"  {'#':>3s} {'Label':<12s} {'Hash':<14s} {'Active':>6s} "
                      f"{'Accuracy':>9s} {'Samples':>8s}")
        lines.append(f"  {'-'*3} {'-'*12} {'-'*14} {'-'*6} {'-'*9} {'-'*8}")

        for v in self.get_all_versions():
            active = " *" if v["is_active"] else ""
            acc = f"{v['avg_accuracy']:.2%}" if v["avg_accuracy"] is not None else "N/A"
            lines.append(
                f"  {v['hash'][:3]:>3s} {v['label']:<12s} {v['hash']:<14s} "
                f"{active:>6s} {acc:>9s} {v['perf_samples']:>8d}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 8. DEPLOYMENT PIPELINE (CI/CD with Evaluation Gates)
# ---------------------------------------------------------------------------

class DeploymentPipeline:
    """
    Full CI/CD simulation with evaluation gates.

    Each stage must pass before the pipeline advances. A failure
    at any stage halts deployment and reports the reason.

    Architecture:
        [Code Push] --> [Build] --> [Unit Tests]
             |
             v
        [Eval Gate 1: Accuracy] --> Pass? --> [Eval Gate 2: Regression]
             |                                       |
             | Fail                                  | Pass?
             v                                       v
        [REJECT]                     [Eval Gate 3: Latency] --> Pass?
                                              |                    |
                                              | Fail               v
                                              v             [Eval Gate 4: Drift]
                                          [REJECT]                 |
                                                              Pass? --> [DEPLOY]
                                                                |
                                                            [REJECT]
    """

    def __init__(self):
        self.gates = []
        self.pipeline_runs = []

    def add_gate(
        self,
        name: str,
        metric: str,
        operator: str,
        threshold: float,
        description: str = "",
        blocking: bool = True,
    ):
        """
        Add an evaluation gate to the pipeline.

        Args:
            name: Gate name (e.g., 'accuracy_gate').
            metric: Metric key to check.
            operator: Comparison operator ('>=', '<=', '>', '<', '==').
            threshold: Pass/fail boundary.
            description: Human-readable description.
            blocking: If True, pipeline stops on failure. If False, logs warning.
        """
        self.gates.append({
            "name": name,
            "metric": metric,
            "operator": operator,
            "threshold": threshold,
            "description": description,
            "blocking": blocking,
        })

    def run(self, metrics: dict, version_label: str = "unknown") -> dict:
        """
        Run the deployment pipeline with all configured gates.
        Returns a result dict with per-gate outcomes and final decision.
        """
        gate_results = []
        all_passed = True
        first_failure = None

        for gate in self.gates:
            metric_val = metrics.get(gate["metric"])

            if metric_val is None:
                result = {
                    "gate": gate["name"],
                    "status": "error",
                    "reason": f"Metric '{gate['metric']}' not found",
                    "blocking": gate["blocking"],
                }
                if gate["blocking"]:
                    all_passed = False
                    if first_failure is None:
                        first_failure = gate["name"]
            else:
                passed = _check_threshold(metric_val, gate["operator"], gate["threshold"])
                result = {
                    "gate": gate["name"],
                    "metric": gate["metric"],
                    "value": metric_val,
                    "operator": gate["operator"],
                    "threshold": gate["threshold"],
                    "status": "passed" if passed else "failed",
                    "blocking": gate["blocking"],
                    "description": gate["description"],
                }
                if not passed and gate["blocking"]:
                    all_passed = False
                    if first_failure is None:
                        first_failure = gate["name"]

            gate_results.append(result)

        pipeline_result = {
            "version": version_label,
            "gates": gate_results,
            "gates_total": len(self.gates),
            "gates_passed": sum(1 for g in gate_results if g["status"] == "passed"),
            "gates_failed": sum(1 for g in gate_results if g["status"] == "failed"),
            "decision": "DEPLOY" if all_passed else "REJECT",
            "first_failure": first_failure,
            "timestamp": datetime.now().isoformat(),
        }

        self.pipeline_runs.append(pipeline_result)
        return pipeline_result

    def format_pipeline_report(self, result: dict) -> str:
        lines = []
        decision = result["decision"]
        lines.append(f"  Deployment Pipeline: {decision}")
        lines.append(f"  {'=' * 55}")
        lines.append(f"  Version: {result['version']}")
        lines.append(f"  Gates: {result['gates_passed']}/{result['gates_total']} passed")
        lines.append("")

        for g in result["gates"]:
            if g["status"] == "passed":
                icon = "[PASS]"
            elif g["status"] == "failed":
                icon = "[FAIL]"
            else:
                icon = "[ERR ]"

            block = " (blocking)" if g.get("blocking") else " (warning)"

            if "value" in g:
                lines.append(
                    f"  {icon} {g['gate']:<25s} "
                    f"{g['value']:.4f} {g['operator']} {g['threshold']}{block}"
                )
            else:
                lines.append(f"  {icon} {g['gate']:<25s} {g.get('reason', '')}{block}")

        if result["decision"] == "REJECT":
            lines.append(f"\n  --> Deployment BLOCKED at gate: {result['first_failure']}")
        else:
            lines.append(f"\n  --> All gates passed. DEPLOYING.")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 9. CONTINUOUS BENCHMARKING
# ---------------------------------------------------------------------------

class ContinuousBenchmark:
    """
    Track performance across model versions over time with trend analysis.

    Architecture:
        [Model Version N] --> [Run Benchmark Suite]
                                    |
                              [Record Results]
                                    |
                            [Append to History]
                                    |
                          [Trend Analysis & Charts]
                                    |
                        [Compare Against Baselines]
    """

    def __init__(self):
        self.history = []
        self.baselines = {}

    def record(
        self,
        version: str,
        accuracy: float,
        latency_p50_ms: float = 0,
        latency_p95_ms: float = 0,
        metadata: Optional[dict] = None,
    ):
        """Record a benchmark result."""
        self.history.append({
            "version": version,
            "accuracy": round(accuracy, 4),
            "latency_p50_ms": round(latency_p50_ms, 1),
            "latency_p95_ms": round(latency_p95_ms, 1),
            "metadata": metadata or {},
            "recorded_at": datetime.now().isoformat(),
            "index": len(self.history),
        })

    def set_baseline(self, name: str, version: str):
        """Set a version as a named baseline for comparison."""
        matching = [h for h in self.history if h["version"] == version]
        if matching:
            self.baselines[name] = matching[-1]

    def get_trend(self, metric: str = "accuracy") -> dict:
        """Analyze trend for a metric across all recorded versions."""
        values = [h[metric] for h in self.history if metric in h]
        if len(values) < 2:
            return {"trend": "insufficient_data"}

        # Linear regression
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0

        if slope > 0.001:
            direction = "improving"
        elif slope < -0.001:
            direction = "degrading"
        else:
            direction = "stable"

        return {
            "metric": metric,
            "direction": direction,
            "slope": round(slope, 6),
            "values": values,
            "versions": [h["version"] for h in self.history],
            "best": round(max(values), 4),
            "worst": round(min(values), 4),
            "current": round(values[-1], 4),
        }

    def compare_to_baseline(self, version: str, baseline_name: str) -> dict:
        """Compare a version against a named baseline."""
        baseline = self.baselines.get(baseline_name)
        if not baseline:
            return {"error": f"Baseline '{baseline_name}' not found"}

        matching = [h for h in self.history if h["version"] == version]
        if not matching:
            return {"error": f"Version '{version}' not found"}

        current = matching[-1]
        return {
            "version": version,
            "baseline": baseline_name,
            "baseline_version": baseline["version"],
            "accuracy_current": current["accuracy"],
            "accuracy_baseline": baseline["accuracy"],
            "accuracy_delta": round(current["accuracy"] - baseline["accuracy"], 4),
            "latency_p50_current": current["latency_p50_ms"],
            "latency_p50_baseline": baseline["latency_p50_ms"],
            "latency_p50_delta": round(
                current["latency_p50_ms"] - baseline["latency_p50_ms"], 1
            ),
        }

    def format_history_chart(self, metric: str = "accuracy", width: int = 40) -> str:
        """Render an ASCII chart of metric history."""
        values = [h[metric] for h in self.history if metric in h]
        versions = [h["version"] for h in self.history if metric in h]

        if not values:
            return "  No data to chart."

        min_val = min(values)
        max_val = max(values)
        val_range = max_val - min_val if max_val > min_val else 1

        lines = []
        lines.append(f"  {metric} over versions (range: {min_val:.2f} - {max_val:.2f})")
        lines.append(f"  {'=' * (width + 20)}")

        for ver, val in zip(versions, values):
            bar_len = int((val - min_val) / val_range * width) if val_range > 0 else width // 2
            bar = "#" * max(1, bar_len)
            lines.append(f"  {ver:<8s} |{bar:<{width}s}| {val:.2%}")

        return "\n".join(lines)

    def format_comparison_table(self) -> str:
        """Format all recorded versions as a comparison table."""
        lines = []
        lines.append(f"  {'Version':<10s} {'Accuracy':>9s} {'P50 (ms)':>9s} "
                      f"{'P95 (ms)':>9s} {'vs Best':>8s}")
        lines.append(f"  {'-'*10} {'-'*9} {'-'*9} {'-'*9} {'-'*8}")

        best_acc = max(h["accuracy"] for h in self.history) if self.history else 0

        for h in self.history:
            delta = h["accuracy"] - best_acc
            delta_str = f"{delta:+.2%}" if delta != 0 else "  BEST"
            lines.append(
                f"  {h['version']:<10s} {h['accuracy']:>8.2%} "
                f"{h['latency_p50_ms']:>8.1f} {h['latency_p95_ms']:>8.1f} "
                f"{delta_str:>8s}"
            )

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def _percentile(sorted_values: list[float], p: float) -> float:
    """Compute the p-th percentile of a sorted list."""
    if not sorted_values:
        return 0
    values = sorted(sorted_values)
    k = (len(values) - 1) * (p / 100)
    f = int(k)
    c = f + 1
    if c >= len(values):
        return values[-1]
    return values[f] + (values[c] - values[f]) * (k - f)


def _kl_divergence(p_dist: dict, q_dist: dict) -> float:
    """
    Compute KL divergence D(P || Q) between two discrete distributions.
    Distributions are given as {label: count} dicts.
    Uses Laplace smoothing to handle zero probabilities.
    """
    all_keys = set(p_dist.keys()) | set(q_dist.keys())
    if not all_keys:
        return 0.0

    total_p = sum(p_dist.values()) + len(all_keys)  # Laplace smoothing
    total_q = sum(q_dist.values()) + len(all_keys)

    kl = 0.0
    for key in all_keys:
        p_val = (p_dist.get(key, 0) + 1) / total_p
        q_val = (q_dist.get(key, 0) + 1) / total_q
        if p_val > 0 and q_val > 0:
            kl += p_val * math.log(p_val / q_val)

    return max(0.0, kl)


def _check_threshold(value: float, operator: str, threshold: float) -> bool:
    """Check if a value satisfies a threshold condition."""
    ops = {
        ">=": lambda v, t: v >= t,
        "<=": lambda v, t: v <= t,
        ">": lambda v, t: v > t,
        "<": lambda v, t: v < t,
        "==": lambda v, t: abs(v - t) < 1e-9,
    }
    check_fn = ops.get(operator)
    if check_fn is None:
        raise ValueError(f"Unknown operator: {operator}")
    return check_fn(value, threshold)


def compute_accuracy(ground_truths: list[str], predictions: list[str]) -> float:
    """Simple accuracy computation."""
    if not ground_truths:
        return 0.0
    correct = sum(1 for gt, p in zip(ground_truths, predictions) if gt == p)
    return correct / len(ground_truths)
