"""
Chapter 9 - Production Evaluation
Dataset module: Load data and simulate production traffic, logs, and drift scenarios.
"""

import csv
import json
import os
import random
import math
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


def load_sample_data() -> dict:
    """Load the sample production data (logs, alerts, versions)."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load training data as list of question dicts."""
    rows = []
    path = os.path.join(data_dir, "train.csv")
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            rows.append({
                "id": int(row["id"]),
                "prompt": row["prompt"],
                "choices": {
                    "A": row["A"],
                    "B": row["B"],
                    "C": row["C"],
                    "D": row["D"],
                    "E": row["E"],
                },
                "ground_truth": row["answer"],
            })
    return rows


def simulate_llm_predictions(
    questions: list[dict],
    accuracy: float = 0.7,
    seed: int = 42,
) -> list[str]:
    """Simulate model predictions at a given accuracy level."""
    rng = random.Random(seed)
    predictions = []
    choices = ["A", "B", "C", "D", "E"]
    for q in questions:
        if rng.random() < accuracy:
            predictions.append(q["ground_truth"])
        else:
            wrong = [c for c in choices if c != q["ground_truth"]]
            predictions.append(rng.choice(wrong))
    return predictions


def simulate_model_versions(
    questions: list[dict],
    seed: int = 42,
) -> dict[str, list[str]]:
    """
    Simulate predictions for multiple model versions with different characteristics:
      - v1.0: solid baseline (78% accuracy)
      - v1.1: slight improvement (80% accuracy)
      - v2.0: regression on a subset (65% overall -- fast but less accurate)
      - v2.1: hotfix (83% accuracy)
    """
    return {
        "v1.0": simulate_llm_predictions(questions, accuracy=0.78, seed=seed),
        "v1.1": simulate_llm_predictions(questions, accuracy=0.80, seed=seed + 1),
        "v2.0": simulate_llm_predictions(questions, accuracy=0.65, seed=seed + 2),
        "v2.1": simulate_llm_predictions(questions, accuracy=0.83, seed=seed + 3),
    }


def simulate_production_traffic(
    questions: list[dict],
    model_version: str,
    accuracy: float,
    num_requests: int = 100,
    base_latency_ms: float = 250.0,
    seed: int = 42,
) -> list[dict]:
    """
    Simulate production traffic logs for a given model version.
    Returns list of request log entries with timestamps, predictions, latencies.
    """
    rng = random.Random(seed)
    logs = []
    choices = ["A", "B", "C", "D", "E"]

    for i in range(num_requests):
        q = rng.choice(questions)
        is_correct = rng.random() < accuracy
        if is_correct:
            prediction = q["ground_truth"]
        else:
            wrong = [c for c in choices if c != q["ground_truth"]]
            prediction = rng.choice(wrong)

        # Simulate latency with some jitter
        latency = max(50, base_latency_ms + rng.gauss(0, base_latency_ms * 0.2))

        logs.append({
            "request_id": f"req_{i:04d}",
            "timestamp_offset_minutes": i * 5,
            "model_version": model_version,
            "question_id": q["id"],
            "prediction": prediction,
            "ground_truth": q["ground_truth"],
            "is_correct": is_correct,
            "latency_ms": round(latency, 1),
            "confidence": round(rng.uniform(0.4, 0.99) if is_correct else rng.uniform(0.2, 0.7), 2),
        })

    return logs


def simulate_drift_scenario(
    questions: list[dict],
    num_windows: int = 6,
    window_size: int = 30,
    seed: int = 42,
) -> list[dict]:
    """
    Simulate a drift scenario where input distribution changes over time.
    - Early windows: questions are sampled uniformly
    - Later windows: questions skew toward longer/harder questions
    - This simulates concept drift in production
    Returns list of windows, each with stats and predictions.
    """
    rng = random.Random(seed)
    sorted_by_length = sorted(questions, key=lambda q: len(q["prompt"]))
    n = len(sorted_by_length)

    windows = []
    for w in range(num_windows):
        # Progressively bias toward longer questions
        drift_factor = w / max(num_windows - 1, 1)

        # Sample questions with increasing bias toward longer ones
        sampled = []
        for _ in range(window_size):
            if rng.random() < drift_factor * 0.7:
                # Pick from top 30% (longer questions)
                idx = rng.randint(int(n * 0.7), n - 1)
            else:
                idx = rng.randint(0, n - 1)
            sampled.append(sorted_by_length[idx])

        # Accuracy degrades as drift increases (model wasn't trained for shifted dist)
        base_accuracy = 0.80
        degraded_accuracy = base_accuracy - (drift_factor * 0.20)
        preds = simulate_llm_predictions(sampled, accuracy=degraded_accuracy, seed=seed + w)

        correct = sum(1 for q, p in zip(sampled, preds) if q["ground_truth"] == p)
        avg_len = sum(len(q["prompt"]) for q in sampled) / len(sampled)

        # Compute answer distribution
        answer_dist = {}
        for q in sampled:
            a = q["ground_truth"]
            answer_dist[a] = answer_dist.get(a, 0) + 1

        pred_dist = {}
        for p in preds:
            pred_dist[p] = pred_dist.get(p, 0) + 1

        windows.append({
            "window_id": w,
            "drift_factor": round(drift_factor, 2),
            "num_questions": window_size,
            "accuracy": round(correct / window_size, 4),
            "avg_prompt_length": round(avg_len, 1),
            "answer_distribution": dict(sorted(answer_dist.items())),
            "prediction_distribution": dict(sorted(pred_dist.items())),
            "questions": sampled,
            "predictions": preds,
        })

    return windows


def simulate_canary_traffic(
    questions: list[dict],
    control_accuracy: float = 0.80,
    canary_accuracy: float = 0.65,
    total_requests: int = 200,
    canary_percentage: float = 0.10,
    seed: int = 42,
) -> dict:
    """
    Simulate canary deployment traffic split between control and canary.
    Returns dict with control_logs, canary_logs, and metadata.
    """
    rng = random.Random(seed)
    choices = ["A", "B", "C", "D", "E"]

    control_logs = []
    canary_logs = []

    for i in range(total_requests):
        q = rng.choice(questions)
        is_canary = rng.random() < canary_percentage

        if is_canary:
            acc = canary_accuracy
            version = "v2.0-canary"
        else:
            acc = control_accuracy
            version = "v1.1-control"

        is_correct = rng.random() < acc
        if is_correct:
            prediction = q["ground_truth"]
        else:
            wrong = [c for c in choices if c != q["ground_truth"]]
            prediction = rng.choice(wrong)

        entry = {
            "request_id": f"req_{i:04d}",
            "model_version": version,
            "question_id": q["id"],
            "prediction": prediction,
            "ground_truth": q["ground_truth"],
            "is_correct": is_correct,
            "latency_ms": round(max(50, (180 if is_canary else 250) + rng.gauss(0, 30)), 1),
        }

        if is_canary:
            canary_logs.append(entry)
        else:
            control_logs.append(entry)

    return {
        "control_logs": control_logs,
        "canary_logs": canary_logs,
        "canary_percentage": canary_percentage,
        "total_requests": total_requests,
        "control_count": len(control_logs),
        "canary_count": len(canary_logs),
    }


def create_golden_dataset(
    questions: list[dict],
    limit: int = 50,
    version: str = "1.0",
) -> dict:
    """Create a versioned golden dataset for regression testing."""
    subset = questions[:limit]
    return {
        "version": version,
        "num_questions": len(subset),
        "questions": subset,
        "ground_truths": [q["ground_truth"] for q in subset],
        "metadata": {
            "created_by": "evaluation_team",
            "description": f"Golden dataset v{version} for regression testing",
            "answer_distribution": _count_answers(subset),
        },
    }


def create_dataset_versions(
    questions: list[dict],
) -> list[dict]:
    """Create multiple versions of a dataset to demonstrate dataset versioning."""
    versions = []

    # v1.0: First 50 questions
    versions.append(create_golden_dataset(questions, limit=50, version="1.0"))

    # v1.1: First 75 questions (expanded)
    versions.append(create_golden_dataset(questions, limit=75, version="1.1"))

    # v2.0: First 100 questions with rebalanced distribution
    versions.append(create_golden_dataset(questions, limit=100, version="2.0"))

    # v2.1: All 199 questions
    versions.append(create_golden_dataset(questions, limit=199, version="2.1"))

    return versions


def _count_answers(questions: list[dict]) -> dict:
    dist = {}
    for q in questions:
        a = q["ground_truth"]
        dist[a] = dist.get(a, 0) + 1
    return dict(sorted(dist.items()))


if __name__ == "__main__":
    print("=" * 60)
    print("DATASET MODULE - Quick Test")
    print("=" * 60)

    train = load_train_data(limit=10)
    print(f"\nLoaded {len(train)} training questions")
    print(f"First question: {train[0]['prompt'][:80]}...")
    print(f"Ground truth: {train[0]['ground_truth']}")

    versions = simulate_model_versions(train)
    for v, preds in versions.items():
        correct = sum(1 for q, p in zip(train, preds) if q["ground_truth"] == p)
        print(f"  {v}: {correct}/{len(train)} correct")

    print("\nDrift simulation:")
    windows = simulate_drift_scenario(load_train_data(), num_windows=4, window_size=20)
    for w in windows:
        print(f"  Window {w['window_id']}: accuracy={w['accuracy']:.2%}, "
              f"avg_len={w['avg_prompt_length']:.0f}")
