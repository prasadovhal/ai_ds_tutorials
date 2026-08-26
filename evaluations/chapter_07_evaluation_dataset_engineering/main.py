"""
Chapter 7: Evaluation Dataset Engineering

Covers building high-quality evaluation benchmarks:
- Benchmark design: defining scope, coverage, and representativeness
- Dataset quality: ensuring fairness and reliability
- Coverage metrics: topic coverage, difficulty levels, edge cases
- Failure-mode coverage: systematic inclusion of hard cases
- Dataset balancing: representative distribution across labels
- Contamination detection: ensuring no train/test overlap
- Leakage prevention: avoiding information leaks between splits
- Label noise: identifying and handling annotation errors
- Annotation quality: inter-annotator agreement metrics
- Cohen's Kappa: agreement coefficient for two annotators
- Fleiss' Kappa: agreement for multiple annotators
- Meta-evaluation: evaluating the evaluator and dataset quality

Simple benchmark design and dataset quality checks in one file.
"""

from collections import Counter
from statistics import mean


QUESTIONS = [
    {"id": 1, "prompt": "What is gravity?", "topic": "physics", "difficulty": "easy", "label": "good"},
    {"id": 2, "prompt": "Explain photosynthesis.", "topic": "biology", "difficulty": "easy", "label": "good"},
    {"id": 3, "prompt": "What is the Roche limit?", "topic": "astronomy", "difficulty": "hard", "label": "good"},
    {"id": 4, "prompt": "What is gravity?", "topic": "physics", "difficulty": "easy", "label": "good"},
]


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def coverage_by_topic(rows):
    return Counter(row["topic"] for row in rows)


def coverage_by_difficulty(rows):
    return Counter(row["difficulty"] for row in rows)


def duplicate_pairs(rows):
    seen = {}
    duplicates = []
    for row in rows:
        prompt = row["prompt"]
        if prompt in seen:
            duplicates.append((seen[prompt], row["id"]))
        else:
            seen[prompt] = row["id"]
    return duplicates


def contamination_score(train_prompts, eval_prompts):
    overlap = 0
    for prompt in eval_prompts:
        if prompt in train_prompts:
            overlap += 1
    return overlap / len(eval_prompts)


def label_noise_rate(gold_labels, noisy_labels):
    mismatches = 0
    for gold, noisy in zip(gold_labels, noisy_labels):
        if gold != noisy:
            mismatches += 1
    return mismatches / len(gold_labels)


def cohen_kappa(labels_a, labels_b):
    observed = 0
    for left, right in zip(labels_a, labels_b):
        if left == right:
            observed += 1
    observed = observed / len(labels_a)

    label_space = sorted(set(labels_a + labels_b))
    expected = 0
    for label in label_space:
        prob_a = labels_a.count(label) / len(labels_a)
        prob_b = labels_b.count(label) / len(labels_b)
        expected += prob_a * prob_b

    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def fleiss_kappa(annotation_rows, categories):
    per_item_scores = []
    for row in annotation_rows:
        total_votes = sum(row.values())
        agreement = 0
        for category in categories:
            votes = row.get(category, 0)
            agreement += votes * (votes - 1)
        agreement = agreement / (total_votes * (total_votes - 1))
        per_item_scores.append(agreement)
    return mean(per_item_scores)


def meta_eval(metric_scores):
    return mean(metric_scores)


def main():
    section("Chapter 7: Evaluation Dataset Engineering")

    section("1. Benchmark Design")
    print(f"Topic coverage: {dict(coverage_by_topic(QUESTIONS))}")
    print(f"Difficulty coverage: {dict(coverage_by_difficulty(QUESTIONS))}")

    section("2. Dataset Quality")
    print(f"Duplicate prompt pairs: {duplicate_pairs(QUESTIONS)}")

    section("3. Coverage Checks")
    print("Coverage should include topics, difficulty levels, and edge cases.")

    section("4. Contamination")
    train_prompts = ["What is gravity?", "Define inertia."]
    eval_prompts = [row["prompt"] for row in QUESTIONS[:3]]
    print(f"Contamination score: {contamination_score(train_prompts, eval_prompts):.2f}")

    section("5. Label Noise")
    gold_labels = ["good", "good", "good", "good"]
    noisy_labels = ["good", "bad", "good", "good"]
    print(f"Label noise rate: {label_noise_rate(gold_labels, noisy_labels):.2f}")

    section("6. Cohen's Kappa")
    labels_a = ["pass", "pass", "fail", "pass"]
    labels_b = ["pass", "fail", "fail", "pass"]
    print(f"Cohen's kappa: {cohen_kappa(labels_a, labels_b):.2f}")

    section("7. Fleiss' Kappa")
    annotations = [
        {"pass": 3, "fail": 0},
        {"pass": 2, "fail": 1},
        {"pass": 0, "fail": 3},
    ]
    print(f"Fleiss' kappa style agreement: {fleiss_kappa(annotations, ['pass', 'fail']):.2f}")

    section("8. Meta-Evaluation")
    print(f"Meta-eval score: {meta_eval([0.80, 0.75, 0.90]):.2f}")


if __name__ == "__main__":
    main()
