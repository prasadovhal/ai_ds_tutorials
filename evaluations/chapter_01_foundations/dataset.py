"""
Chapter 1 - Foundations of LLM Evaluation
Dataset module: Load and prepare evaluation data from multiple sources.
"""

import csv
import json
import os
import random
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


def load_sample_data() -> dict:
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
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


def load_test_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    rows = []
    path = os.path.join(data_dir, "test.csv")
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
            })
    return rows


def simulate_llm_predictions(
    questions: list[dict],
    accuracy: float = 0.7,
    seed: int = 42,
) -> list[str]:
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


def create_evaluation_pairs(
    questions: list[dict],
    predictions: list[str],
) -> list[dict]:
    pairs = []
    for q, pred in zip(questions, predictions):
        pairs.append({
            "id": q["id"],
            "prompt": q["prompt"],
            "ground_truth": q["ground_truth"],
            "prediction": pred,
            "is_correct": q["ground_truth"] == pred,
        })
    return pairs


def get_dataset_summary(questions: list[dict]) -> dict:
    answer_dist = {}
    for q in questions:
        ans = q["ground_truth"]
        answer_dist[ans] = answer_dist.get(ans, 0) + 1

    avg_prompt_len = sum(len(q["prompt"]) for q in questions) / len(questions)
    avg_choice_len = sum(
        sum(len(v) for v in q["choices"].values()) / 5
        for q in questions
    ) / len(questions)

    return {
        "total_questions": len(questions),
        "answer_distribution": dict(sorted(answer_dist.items())),
        "avg_prompt_length_chars": round(avg_prompt_len, 1),
        "avg_choice_length_chars": round(avg_choice_len, 1),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("DATASET MODULE - Quick Test")
    print("=" * 60)

    train = load_train_data(limit=10)
    print(f"\nLoaded {len(train)} training questions")
    print(f"First question: {train[0]['prompt'][:80]}...")
    print(f"Ground truth: {train[0]['ground_truth']}")

    summary = get_dataset_summary(load_train_data())
    print(f"\nFull dataset summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    preds = simulate_llm_predictions(train, accuracy=0.7)
    pairs = create_evaluation_pairs(train, preds)
    correct = sum(1 for p in pairs if p["is_correct"])
    print(f"\nSimulated predictions (70% accuracy): {correct}/{len(pairs)} correct")
