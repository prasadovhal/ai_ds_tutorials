"""
Chapter 2 - Classical NLP Metrics
Dataset module: Load and prepare evaluation data from multiple sources.
Provides both MCQ classification data and text generation data for metric demos.
"""

import csv
import json
import os
import random
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


def load_sample_data() -> dict:
    """Load the chapter's curated sample data with text generation examples."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load training data with ground-truth answers for classification metrics."""
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
    """Load test data (no answers) for inference-only demos."""
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
    """Simulate LLM predictions for MCQ with a target accuracy."""
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


def simulate_llm_confidences(
    questions: list[dict],
    predictions: list[str],
    seed: int = 42,
) -> list[float]:
    """
    Simulate confidence scores for each prediction.
    Correct predictions tend to get higher confidence, but not always
    (to demonstrate calibration issues).
    """
    rng = random.Random(seed)
    confidences = []
    for q, pred in zip(questions, predictions):
        is_correct = q["ground_truth"] == pred
        if is_correct:
            # Correct: usually high confidence, sometimes low (underconfident)
            conf = rng.gauss(0.82, 0.12)
        else:
            # Wrong: sometimes high confidence (overconfident), sometimes low
            conf = rng.gauss(0.55, 0.20)
        confidences.append(max(0.01, min(0.99, conf)))
    return confidences


def create_text_generation_pairs(
    questions: list[dict],
    seed: int = 42,
) -> list[dict]:
    """
    Create reference/hypothesis pairs for text generation metrics (BLEU, ROUGE, etc.).
    Uses question prompts as a basis and simulates LLM text answers.
    """
    rng = random.Random(seed)
    pairs = []

    # Templates for simulated answers of varying quality
    good_templates = [
        "The answer is {choice} because {reason}.",
        "Based on the scientific principles involved, {choice} is correct. {reason}.",
        "{reason} Therefore, the answer is {choice}.",
        "The correct answer is {choice}. This is because {reason}.",
    ]

    mediocre_templates = [
        "I think it is {choice}. {partial_reason}.",
        "The answer should be {choice} based on general knowledge.",
        "{choice} seems right because {partial_reason}.",
    ]

    poor_templates = [
        "The answer is {wrong_choice}.",
        "I believe {wrong_choice} is correct.",
        "{wrong_choice}. This is my best guess.",
    ]

    choices_list = ["A", "B", "C", "D", "E"]

    for q in questions:
        gt = q["ground_truth"]
        gt_text = q["choices"][gt]
        prompt_words = q["prompt"].split()

        # Build a "reason" from the correct answer text
        reason = gt_text[:80] if len(gt_text) > 80 else gt_text
        partial_reason = " ".join(gt_text.split()[:8])

        wrong = [c for c in choices_list if c != gt]
        wrong_choice = rng.choice(wrong)

        # Reference answer (what a perfect answer looks like)
        reference = f"The correct answer is {gt}. {reason}"

        # Good hypothesis
        tmpl = rng.choice(good_templates)
        good_hyp = tmpl.format(choice=gt, reason=reason)

        # Mediocre hypothesis
        tmpl = rng.choice(mediocre_templates)
        med_hyp = tmpl.format(choice=gt, partial_reason=partial_reason)

        # Poor hypothesis (wrong answer)
        tmpl = rng.choice(poor_templates)
        poor_hyp = tmpl.format(wrong_choice=wrong_choice)

        pairs.append({
            "id": q["id"],
            "prompt": q["prompt"],
            "reference": reference,
            "good_hypothesis": good_hyp,
            "mediocre_hypothesis": med_hyp,
            "poor_hypothesis": poor_hyp,
        })

    return pairs


def get_dataset_summary(questions: list[dict]) -> dict:
    """Compute summary statistics for the dataset."""
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

    pairs = create_text_generation_pairs(train[:3])
    print(f"\nText generation pairs:")
    for p in pairs[:2]:
        print(f"  Reference:  {p['reference'][:80]}...")
        print(f"  Good hyp:   {p['good_hypothesis'][:80]}...")
        print(f"  Poor hyp:   {p['poor_hypothesis'][:80]}...")
        print()
