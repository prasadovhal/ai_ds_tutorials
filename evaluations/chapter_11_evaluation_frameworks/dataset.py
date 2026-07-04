"""
Chapter 11 - Evaluation Frameworks
Dataset module: Load and prepare data for framework comparisons.
"""

import csv
import json
import os
import random
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


def load_sample_data() -> dict:
    """Load the chapter's sample data with RAG examples, MCQs, and agent traces."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load science MCQ questions from train.csv."""
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
    """Simulate LLM predictions at a given accuracy level."""
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


def get_rag_examples() -> list[dict]:
    """Get RAG evaluation examples from sample data."""
    data = load_sample_data()
    return data["rag_examples"]


def get_mcq_examples() -> list[dict]:
    """Get MCQ examples from sample data."""
    data = load_sample_data()
    return data["mcq_examples"]


def get_agent_traces() -> list[dict]:
    """Get agent trace examples from sample data."""
    data = load_sample_data()
    return data["agent_traces"]


def get_framework_test_cases() -> list[dict]:
    """Get standardized test cases for framework comparison."""
    data = load_sample_data()
    return data["framework_test_cases"]["cases"]


def build_rag_dataset_for_framework(examples: list[dict]) -> list[dict]:
    """
    Convert RAG examples into a standardized format that all
    framework simulators can consume.
    """
    dataset = []
    for ex in examples:
        dataset.append({
            "id": ex["id"],
            "question": ex["question"],
            "contexts": ex["context"],
            "answer": ex["generated_answer"],
            "reference": ex["reference_answer"],
            "expected_scores": ex.get("expected_scores", {}),
        })
    return dataset


def get_dataset_summary(questions: list[dict]) -> dict:
    """Compute summary statistics for a question dataset."""
    answer_dist = {}
    for q in questions:
        ans = q["ground_truth"]
        answer_dist[ans] = answer_dist.get(ans, 0) + 1

    avg_prompt_len = sum(len(q["prompt"]) for q in questions) / len(questions)

    return {
        "total_questions": len(questions),
        "answer_distribution": dict(sorted(answer_dist.items())),
        "avg_prompt_length_chars": round(avg_prompt_len, 1),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("DATASET MODULE - Quick Test")
    print("=" * 60)

    train = load_train_data(limit=5)
    print(f"\nLoaded {len(train)} training questions")
    print(f"First question: {train[0]['prompt'][:80]}...")

    rag = get_rag_examples()
    print(f"\nLoaded {len(rag)} RAG examples")
    print(f"First RAG question: {rag[0]['question']}")

    agents = get_agent_traces()
    print(f"\nLoaded {len(agents)} agent traces")

    test_cases = get_framework_test_cases()
    print(f"\nLoaded {len(test_cases)} framework test cases")
