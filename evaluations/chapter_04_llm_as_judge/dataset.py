"""
Chapter 4 - LLM-as-a-Judge
Dataset module: Load questions, model responses, and prepare judge evaluation data.
"""

import csv
import json
import os
import random
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


def load_sample_data() -> dict:
    """Load the curated sample data with model responses for judging."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load MCQ science questions from train.csv."""
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


def get_questions_with_responses(limit: Optional[int] = None) -> list[dict]:
    """
    Build evaluation items: each item has a question, reference answer,
    and responses from multiple models ready for judging.
    """
    sample = load_sample_data()
    questions = sample["questions"]
    models = sample["model_responses"]

    items = []
    for i, q in enumerate(questions):
        if limit and i >= limit:
            break
        item = {
            "id": q["id"],
            "prompt": q["prompt"],
            "reference_answer": q["reference_answer"],
            "topic": q["topic"],
            "model_responses": {},
        }
        for model_key, model_data in models.items():
            item["model_responses"][model_key] = {
                "model_name": model_data["name"],
                "response": model_data["responses"][i],
            }
        items.append(item)
    return items


def get_pairwise_items(limit: Optional[int] = None) -> list[dict]:
    """
    Build pairwise comparison items: each item has a question
    and two model responses to compare head-to-head.
    """
    sample = load_sample_data()
    questions = sample["questions"]
    models = sample["model_responses"]
    comparisons = sample.get("pairwise_comparisons", [])

    items = []
    for comp in comparisons:
        if limit and len(items) >= limit:
            break
        q = questions[comp["question_id"]]
        items.append({
            "id": comp["question_id"],
            "prompt": q["prompt"],
            "reference_answer": q["reference_answer"],
            "response_a": models["model_a"]["responses"][comp["model_a_response_idx"]],
            "response_b": models["model_b"]["responses"][comp["model_b_response_idx"]],
            "model_a_name": models["model_a"]["name"],
            "model_b_name": models["model_b"]["name"],
            "human_preference": comp["human_preference"],
            "human_reason": comp["reason"],
        })
    return items


def get_bias_test_data() -> dict:
    """Load bias test pairs for detecting judge biases."""
    sample = load_sample_data()
    return sample.get("bias_test_pairs", {})


def get_dataset_summary() -> dict:
    """Return a summary of the sample dataset."""
    sample = load_sample_data()
    questions = sample["questions"]
    models = sample["model_responses"]

    topics = {}
    for q in questions:
        t = q["topic"]
        topics[t] = topics.get(t, 0) + 1

    return {
        "total_questions": len(questions),
        "topics": topics,
        "models": {
            key: {"name": m["name"], "description": m["description"]}
            for key, m in models.items()
        },
        "pairwise_comparisons": len(sample.get("pairwise_comparisons", [])),
        "bias_tests": list(sample.get("bias_test_pairs", {}).keys()),
    }


def generate_arena_matchups(
    model_keys: list[str],
    num_questions: int = 10,
    seed: int = 42,
) -> list[dict]:
    """
    Generate round-robin matchups between all model pairs
    across all questions for arena-style evaluation.
    """
    rng = random.Random(seed)
    matchups = []
    match_id = 0
    for qi in range(num_questions):
        for i in range(len(model_keys)):
            for j in range(i + 1, len(model_keys)):
                # Randomly swap position to counteract position bias
                if rng.random() < 0.5:
                    a, b = model_keys[i], model_keys[j]
                else:
                    a, b = model_keys[j], model_keys[i]
                matchups.append({
                    "match_id": match_id,
                    "question_id": qi,
                    "position_a": a,
                    "position_b": b,
                })
                match_id += 1
    return matchups


if __name__ == "__main__":
    print("=" * 60)
    print("DATASET MODULE - Quick Test")
    print("=" * 60)

    summary = get_dataset_summary()
    print(f"\nDataset summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    items = get_questions_with_responses(limit=2)
    print(f"\nLoaded {len(items)} evaluation items")
    for item in items:
        print(f"  Q{item['id']}: {item['prompt'][:60]}...")
        for mk, mr in item["model_responses"].items():
            print(f"    {mk} ({mr['model_name']}): {mr['response'][:50]}...")

    pairs = get_pairwise_items(limit=2)
    print(f"\nLoaded {len(pairs)} pairwise comparison items")
    for p in pairs:
        print(f"  Q{p['id']}: preference={p['human_preference']}")
