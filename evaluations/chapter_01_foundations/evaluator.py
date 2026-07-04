"""
Chapter 1 - Foundations of LLM Evaluation
Evaluator module: Core evaluation logic demonstrating all foundational concepts.
"""

import time
import json
import os
from collections import Counter
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# 1. BASIC EVALUATION METRICS
# ---------------------------------------------------------------------------

def compute_accuracy(ground_truths: list[str], predictions: list[str]) -> float:
    if len(ground_truths) != len(predictions):
        raise ValueError("Ground truths and predictions must have the same length")
    correct = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == pred)
    return correct / len(ground_truths)


def compute_per_class_accuracy(
    ground_truths: list[str],
    predictions: list[str],
) -> dict[str, dict]:
    classes = sorted(set(ground_truths))
    results = {}
    for cls in classes:
        indices = [i for i, gt in enumerate(ground_truths) if gt == cls]
        if not indices:
            continue
        correct = sum(1 for i in indices if predictions[i] == cls)
        results[cls] = {
            "total": len(indices),
            "correct": correct,
            "accuracy": round(correct / len(indices), 4),
        }
    return results


def build_confusion_matrix(
    ground_truths: list[str],
    predictions: list[str],
) -> dict:
    labels = sorted(set(ground_truths) | set(predictions))
    matrix = {actual: {pred: 0 for pred in labels} for actual in labels}
    for gt, pred in zip(ground_truths, predictions):
        matrix[gt][pred] += 1
    return {"labels": labels, "matrix": matrix}


# ---------------------------------------------------------------------------
# 2. OFFLINE vs ONLINE EVALUATION
# ---------------------------------------------------------------------------

class OfflineEvaluator:
    """Evaluates a fixed dataset against predictions — batch mode."""

    def __init__(self, questions: list[dict], predictions: list[str]):
        self.questions = questions
        self.predictions = predictions
        self.ground_truths = [q["ground_truth"] for q in questions]

    def run(self) -> dict:
        accuracy = compute_accuracy(self.ground_truths, self.predictions)
        per_class = compute_per_class_accuracy(self.ground_truths, self.predictions)
        confusion = build_confusion_matrix(self.ground_truths, self.predictions)

        errors = []
        for q, pred in zip(self.questions, self.predictions):
            if q["ground_truth"] != pred:
                errors.append({
                    "id": q["id"],
                    "prompt": q["prompt"][:100] + "...",
                    "expected": q["ground_truth"],
                    "predicted": pred,
                })

        return {
            "evaluation_type": "offline",
            "total_questions": len(self.questions),
            "accuracy": round(accuracy, 4),
            "per_class_accuracy": per_class,
            "confusion_matrix": confusion,
            "total_errors": len(errors),
            "errors": errors[:5],
        }


class OnlineEvaluator:
    """Evaluates predictions one-at-a-time as they arrive — streaming mode."""

    def __init__(self):
        self.total = 0
        self.correct = 0
        self.history = []
        self.window_size = 20
        self.window_correct = 0
        self.window_results = []

    def record(self, ground_truth: str, prediction: str, latency_ms: float = 0.0):
        is_correct = ground_truth == prediction
        self.total += 1
        self.correct += int(is_correct)

        self.window_results.append(is_correct)
        self.window_correct += int(is_correct)
        if len(self.window_results) > self.window_size:
            removed = self.window_results.pop(0)
            self.window_correct -= int(removed)

        self.history.append({
            "step": self.total,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "is_correct": is_correct,
            "cumulative_accuracy": round(self.correct / self.total, 4),
            "rolling_accuracy": round(
                self.window_correct / len(self.window_results), 4
            ),
            "latency_ms": latency_ms,
        })

    def get_status(self) -> dict:
        if self.total == 0:
            return {"evaluation_type": "online", "status": "no_data"}

        latencies = [h["latency_ms"] for h in self.history]
        return {
            "evaluation_type": "online",
            "total_evaluated": self.total,
            "cumulative_accuracy": round(self.correct / self.total, 4),
            "rolling_accuracy": self.history[-1]["rolling_accuracy"],
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "p95_latency_ms": round(
                sorted(latencies)[int(len(latencies) * 0.95)], 2
            ),
        }


# ---------------------------------------------------------------------------
# 3. REFERENCE vs REFERENCE-FREE EVALUATION
# ---------------------------------------------------------------------------

class ReferenceEvaluator:
    """Evaluates by comparing prediction to a known ground truth."""

    def evaluate(self, ground_truth: str, prediction: str) -> dict:
        return {
            "method": "reference-based",
            "exact_match": ground_truth == prediction,
            "ground_truth": ground_truth,
            "prediction": prediction,
        }


class ReferenceFreeEvaluator:
    """Evaluates prediction quality without a ground truth reference."""

    def evaluate(self, question: str, prediction: str, choices: dict) -> dict:
        is_valid_choice = prediction in choices
        answer_length = len(choices.get(prediction, "")) if is_valid_choice else 0

        return {
            "method": "reference-free",
            "is_valid_choice": is_valid_choice,
            "prediction": prediction,
            "answer_length": answer_length,
            "has_content": answer_length > 0,
        }


# ---------------------------------------------------------------------------
# 4. HUMAN vs AUTOMATIC EVALUATION
# ---------------------------------------------------------------------------

class AutomaticEvaluator:
    """Programmatic evaluation — fast, consistent, scalable."""

    def evaluate_batch(
        self, ground_truths: list[str], predictions: list[str]
    ) -> dict:
        start = time.time()
        accuracy = compute_accuracy(ground_truths, predictions)
        elapsed = time.time() - start

        return {
            "method": "automatic",
            "accuracy": round(accuracy, 4),
            "evaluation_time_seconds": round(elapsed, 6),
            "scalability": "high",
            "consistency": "perfect",
            "cost": "near_zero",
        }


class SimulatedHumanEvaluator:
    """Simulates human evaluation — slow, expensive, but captures nuance."""

    def __init__(self, agreement_rate: float = 0.85, time_per_item_sec: float = 30):
        self.agreement_rate = agreement_rate
        self.time_per_item = time_per_item_sec

    def evaluate_batch(
        self, ground_truths: list[str], predictions: list[str]
    ) -> dict:
        import random
        rng = random.Random(42)

        annotator_1_scores = [gt == pred for gt, pred in zip(ground_truths, predictions)]
        annotator_2_scores = []
        for score in annotator_1_scores:
            if rng.random() < self.agreement_rate:
                annotator_2_scores.append(score)
            else:
                annotator_2_scores.append(not score)

        agreements = sum(
            1 for a, b in zip(annotator_1_scores, annotator_2_scores) if a == b
        )
        total_time = len(ground_truths) * self.time_per_item

        return {
            "method": "human_simulated",
            "annotator_1_accuracy": round(
                sum(annotator_1_scores) / len(annotator_1_scores), 4
            ),
            "annotator_2_accuracy": round(
                sum(annotator_2_scores) / len(annotator_2_scores), 4
            ),
            "inter_annotator_agreement": round(agreements / len(ground_truths), 4),
            "estimated_time_seconds": total_time,
            "estimated_cost_usd": round(total_time * 0.01, 2),
            "scalability": "low",
            "consistency": "variable",
        }


# ---------------------------------------------------------------------------
# 5. INTRINSIC vs EXTRINSIC EVALUATION
# ---------------------------------------------------------------------------

class IntrinsicEvaluator:
    """Measures model quality on the task itself (accuracy, correctness)."""

    def evaluate(self, ground_truths: list[str], predictions: list[str]) -> dict:
        accuracy = compute_accuracy(ground_truths, predictions)
        per_class = compute_per_class_accuracy(ground_truths, predictions)

        return {
            "evaluation_type": "intrinsic",
            "description": "Measures how well the model performs the core task",
            "accuracy": round(accuracy, 4),
            "per_class_accuracy": per_class,
            "metrics_focus": ["accuracy", "exact_match", "f1", "precision", "recall"],
        }


class ExtrinsicEvaluator:
    """Measures model impact on a downstream task or real-world outcome."""

    def evaluate(
        self,
        ground_truths: list[str],
        predictions: list[str],
        latencies_ms: list[float],
        user_satisfaction_scores: list[float],
    ) -> dict:
        accuracy = compute_accuracy(ground_truths, predictions)
        avg_latency = sum(latencies_ms) / len(latencies_ms)
        avg_satisfaction = sum(user_satisfaction_scores) / len(user_satisfaction_scores)

        task_completion = sum(
            1 for gt, pred in zip(ground_truths, predictions) if gt == pred
        ) / len(ground_truths)

        return {
            "evaluation_type": "extrinsic",
            "description": "Measures model impact on downstream goals",
            "task_completion_rate": round(task_completion, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_user_satisfaction": round(avg_satisfaction, 2),
            "metrics_focus": [
                "task_completion",
                "user_satisfaction",
                "latency",
                "cost",
                "business_impact",
            ],
        }


# ---------------------------------------------------------------------------
# 6. ERROR TAXONOMY & FAILURE ANALYSIS
# ---------------------------------------------------------------------------

class ErrorTaxonomy:
    """Classifies errors into categories for systematic failure analysis."""

    CATEGORIES = {
        "wrong_choice": "Model selected an incorrect answer option",
        "hallucination": "Model produced an answer not in the choices",
        "no_response": "Model failed to produce any answer",
        "format_error": "Model answered in wrong format",
        "partial_correct": "Model's reasoning was right but chose wrong option",
    }

    def classify_errors(
        self,
        questions: list[dict],
        predictions: list[str],
    ) -> dict:
        valid_choices = {"A", "B", "C", "D", "E"}
        error_counts = Counter()
        error_examples = {cat: [] for cat in self.CATEGORIES}

        for q, pred in zip(questions, predictions):
            gt = q["ground_truth"]
            if pred == gt:
                continue

            if not pred or pred.strip() == "":
                category = "no_response"
            elif pred not in valid_choices:
                category = "format_error"
            else:
                category = "wrong_choice"

            error_counts[category] += 1
            if len(error_examples[category]) < 2:
                error_examples[category].append({
                    "id": q["id"],
                    "expected": gt,
                    "predicted": pred,
                    "prompt_preview": q["prompt"][:80],
                })

        total_errors = sum(error_counts.values())
        return {
            "total_errors": total_errors,
            "error_rate": round(total_errors / len(questions), 4) if questions else 0,
            "error_distribution": dict(error_counts),
            "error_examples": {
                k: v for k, v in error_examples.items() if v
            },
        }


# ---------------------------------------------------------------------------
# 7. REGRESSION TESTING
# ---------------------------------------------------------------------------

class RegressionTester:
    """Compares two model versions to detect performance regressions."""

    def __init__(self, threshold: float = 0.02):
        self.threshold = threshold

    def compare(
        self,
        ground_truths: list[str],
        predictions_v1: list[str],
        predictions_v2: list[str],
    ) -> dict:
        acc_v1 = compute_accuracy(ground_truths, predictions_v1)
        acc_v2 = compute_accuracy(ground_truths, predictions_v2)
        delta = acc_v2 - acc_v1

        regressions = []
        improvements = []
        for i, (gt, p1, p2) in enumerate(
            zip(ground_truths, predictions_v1, predictions_v2)
        ):
            if p1 == gt and p2 != gt:
                regressions.append(i)
            elif p1 != gt and p2 == gt:
                improvements.append(i)

        has_regression = delta < -self.threshold

        return {
            "v1_accuracy": round(acc_v1, 4),
            "v2_accuracy": round(acc_v2, 4),
            "delta": round(delta, 4),
            "threshold": self.threshold,
            "has_regression": has_regression,
            "status": "FAIL" if has_regression else "PASS",
            "regressions_count": len(regressions),
            "improvements_count": len(improvements),
            "regressed_indices": regressions[:10],
            "improved_indices": improvements[:10],
        }


# ---------------------------------------------------------------------------
# 8. EVALUATION PIPELINE
# ---------------------------------------------------------------------------

class EvaluationPipeline:
    """End-to-end evaluation pipeline that runs multiple evaluators."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.steps = []
        self.results = {}

    def add_step(self, name: str, evaluator_fn, **kwargs):
        self.steps.append({"name": name, "fn": evaluator_fn, "kwargs": kwargs})

    def run(self) -> dict:
        self.results = {
            "pipeline_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "summary": {},
        }

        start = time.time()
        for step in self.steps:
            step_start = time.time()
            try:
                result = step["fn"](**step["kwargs"])
                self.results["steps"][step["name"]] = {
                    "status": "success",
                    "duration_seconds": round(time.time() - step_start, 4),
                    "result": result,
                }
            except Exception as e:
                self.results["steps"][step["name"]] = {
                    "status": "error",
                    "duration_seconds": round(time.time() - step_start, 4),
                    "error": str(e),
                }

        self.results["summary"] = {
            "total_steps": len(self.steps),
            "successful": sum(
                1 for s in self.results["steps"].values() if s["status"] == "success"
            ),
            "failed": sum(
                1 for s in self.results["steps"].values() if s["status"] == "error"
            ),
            "total_duration_seconds": round(time.time() - start, 4),
        }
        return self.results


# ---------------------------------------------------------------------------
# 9. EVALUATION LIFECYCLE TRACKER
# ---------------------------------------------------------------------------

class EvaluationLifecycle:
    """Tracks the full lifecycle of an evaluation experiment."""

    STAGES = [
        "dataset_preparation",
        "model_inference",
        "metric_computation",
        "error_analysis",
        "regression_check",
        "report_generation",
    ]

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.stages = {}
        self.current_stage = None

    def start_stage(self, stage: str):
        if stage not in self.STAGES:
            raise ValueError(f"Unknown stage: {stage}. Must be one of {self.STAGES}")
        self.current_stage = stage
        self.stages[stage] = {
            "status": "in_progress",
            "start_time": time.time(),
        }

    def complete_stage(self, stage: str, result: Optional[dict] = None):
        if stage not in self.stages:
            raise ValueError(f"Stage {stage} was never started")
        self.stages[stage]["status"] = "completed"
        self.stages[stage]["end_time"] = time.time()
        self.stages[stage]["duration"] = round(
            self.stages[stage]["end_time"] - self.stages[stage]["start_time"], 4
        )
        if result:
            self.stages[stage]["result_summary"] = result

    def get_report(self) -> dict:
        return {
            "experiment": self.experiment_name,
            "stages": {
                stage: {
                    "status": self.stages.get(stage, {}).get("status", "not_started"),
                    "duration": self.stages.get(stage, {}).get("duration", None),
                }
                for stage in self.STAGES
            },
            "completed": all(
                self.stages.get(s, {}).get("status") == "completed"
                for s in self.STAGES
            ),
        }


# ---------------------------------------------------------------------------
# 10. EVALUATION DASHBOARD (Text-based)
# ---------------------------------------------------------------------------

class TextDashboard:
    """Renders evaluation results as formatted text with ASCII charts."""

    @staticmethod
    def render_accuracy_bar(label: str, value: float, width: int = 40) -> str:
        filled = int(value * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"  {label:<20s} |{bar}| {value:.1%}"

    @staticmethod
    def render_confusion_matrix(confusion: dict) -> str:
        labels = confusion["labels"]
        matrix = confusion["matrix"]
        col_width = 6

        header = " " * 12 + "PREDICTED".center(len(labels) * col_width)
        lines = [header]
        lines.append(" " * 12 + "".join(f"{l:>{col_width}}" for l in labels))
        lines.append(" " * 8 + "+" + "-" * (len(labels) * col_width))

        for actual in labels:
            row_vals = "".join(f"{matrix[actual][pred]:>{col_width}}" for pred in labels)
            lines.append(f"  {actual:>5s}   |{row_vals}")

        lines.insert(3, "  ACTUAL")
        return "\n".join(lines)

    @staticmethod
    def render_summary(results: dict) -> str:
        lines = [
            "=" * 60,
            "  EVALUATION DASHBOARD",
            "=" * 60,
        ]

        if "accuracy" in results:
            lines.append(f"\n  Overall Accuracy: {results['accuracy']:.2%}")

        if "per_class_accuracy" in results:
            lines.append("\n  Per-Class Accuracy:")
            for cls, info in results["per_class_accuracy"].items():
                lines.append(
                    TextDashboard.render_accuracy_bar(
                        f"Class {cls} ({info['total']})",
                        info["accuracy"],
                    )
                )

        if "total_errors" in results:
            lines.append(f"\n  Total Errors: {results['total_errors']}")

        if "confusion_matrix" in results:
            lines.append("\n  Confusion Matrix:")
            lines.append(
                TextDashboard.render_confusion_matrix(results["confusion_matrix"])
            )

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 11. CI/CD GATE
# ---------------------------------------------------------------------------

class CICDGate:
    """Evaluation gate for CI/CD — blocks deployment if quality drops."""

    def __init__(self, min_accuracy: float = 0.75, max_regression: float = 0.02):
        self.min_accuracy = min_accuracy
        self.max_regression = max_regression

    def check(
        self,
        current_accuracy: float,
        previous_accuracy: Optional[float] = None,
    ) -> dict:
        checks = []

        accuracy_pass = current_accuracy >= self.min_accuracy
        checks.append({
            "check": "minimum_accuracy",
            "threshold": self.min_accuracy,
            "actual": round(current_accuracy, 4),
            "status": "PASS" if accuracy_pass else "FAIL",
        })

        if previous_accuracy is not None:
            delta = current_accuracy - previous_accuracy
            regression_pass = delta >= -self.max_regression
            checks.append({
                "check": "regression",
                "max_allowed_drop": self.max_regression,
                "actual_delta": round(delta, 4),
                "status": "PASS" if regression_pass else "FAIL",
            })
        else:
            regression_pass = True

        all_pass = accuracy_pass and regression_pass
        return {
            "gate_status": "PASS" if all_pass else "FAIL",
            "deploy_allowed": all_pass,
            "checks": checks,
        }


# ---------------------------------------------------------------------------
# 12. CONTINUOUS EVALUATION SIMULATOR
# ---------------------------------------------------------------------------

class ContinuousEvaluator:
    """Simulates continuous evaluation across multiple model versions."""

    def __init__(self):
        self.versions = []

    def add_version(
        self,
        version: str,
        accuracy: float,
        timestamp: Optional[str] = None,
    ):
        self.versions.append({
            "version": version,
            "accuracy": accuracy,
            "timestamp": timestamp or datetime.now().isoformat(),
        })

    def get_trend(self) -> dict:
        if len(self.versions) < 2:
            return {"trend": "insufficient_data", "versions": self.versions}

        deltas = []
        for i in range(1, len(self.versions)):
            deltas.append(
                self.versions[i]["accuracy"] - self.versions[i - 1]["accuracy"]
            )

        avg_delta = sum(deltas) / len(deltas)
        if avg_delta > 0.01:
            trend = "improving"
        elif avg_delta < -0.01:
            trend = "degrading"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "avg_delta_per_version": round(avg_delta, 4),
            "best_version": max(self.versions, key=lambda v: v["accuracy"]),
            "worst_version": min(self.versions, key=lambda v: v["accuracy"]),
            "versions": self.versions,
        }

    def render_trend_chart(self, width: int = 50) -> str:
        if not self.versions:
            return "No data"

        accuracies = [v["accuracy"] for v in self.versions]
        min_acc = min(accuracies) - 0.05
        max_acc = max(accuracies) + 0.05
        acc_range = max_acc - min_acc if max_acc != min_acc else 1

        lines = ["\n  Accuracy Trend Over Versions:"]
        lines.append(f"  {'':>8s} {min_acc:.0%}{' ' * (width - 8)}{max_acc:.0%}")
        lines.append(f"  {'':>8s} |{'─' * width}|")

        for v in self.versions:
            pos = int((v["accuracy"] - min_acc) / acc_range * width)
            pos = max(0, min(width - 1, pos))
            bar = " " * pos + "●"
            lines.append(f"  {v['version']:>8s} |{bar:<{width}s}| {v['accuracy']:.1%}")

        lines.append(f"  {'':>8s} |{'─' * width}|")
        return "\n".join(lines)
