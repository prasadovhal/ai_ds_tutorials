"""
Chapter 6: Golden Dataset Engineering

Covers creating and maintaining golden evaluation datasets:
- Why golden datasets matter: regression testing, prompt comparison, baseline evaluation
- Dataset types: golden, test, validation, benchmark, evaluation, production, synthetic
- Creating golden data from:
  * Production logs and customer conversations
  * Support tickets and search queries
  * Human-written and LLM-generated examples
  * Synthetic generation and failure-driven sampling
- Data quality: deduplication, balancing, coverage (domain, long-tail, edge cases)
- Annotation workflow: guidelines, rubrics, ground truth, multiple annotators
- Quality metrics: inter-annotator agreement, Cohen's Kappa
- Using golden data: regression testing, prompt comparison, A/B testing
- Maintaining datasets: versioning, drift detection, updates and retirement
- Synthetic golden data: risks, validation, when to use

One-file version focused on simple flow and small utility functions.
"""

from collections import Counter
from statistics import mean


ITEMS = [
    {"id": 1, "prompt": "What planet is red?", "answer": "Mars", "topic": "astronomy", "difficulty": "easy"},
    {"id": 2, "prompt": "What gas do plants absorb?", "answer": "Carbon dioxide", "topic": "biology", "difficulty": "easy"},
    {"id": 3, "prompt": "What is the Roche limit?", "answer": "A tidal disruption distance", "topic": "astronomy", "difficulty": "hard"},
    {"id": 4, "prompt": "What gas do plants absorb?", "answer": "Carbon dioxide", "topic": "biology", "difficulty": "easy"},
]


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def topic_counts(items):
    return Counter(item["topic"] for item in items)


def difficulty_counts(items):
    return Counter(item["difficulty"] for item in items)


def deduplicate(items):
    seen = set()
    unique_items = []
    for item in items:
        key = (item["prompt"], item["answer"])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    return unique_items


def balanced_sample(items):
    by_topic = {}
    for item in items:
        by_topic.setdefault(item["topic"], [])
        by_topic[item["topic"]].append(item)
    sample = []
    for topic_items in by_topic.values():
        sample.append(topic_items[0])
    return sample


def annotator_agreement(labels_a, labels_b):
    matches = 0
    for left, right in zip(labels_a, labels_b):
        if left == right:
            matches += 1
    return matches / len(labels_a)


def prompt_comparison(dataset_score_a, dataset_score_b):
    return dataset_score_b - dataset_score_a


def drift_score(old_topics, new_topics):
    old_total = sum(old_topics.values())
    new_total = sum(new_topics.values())
    score = 0
    for topic in set(old_topics) | set(new_topics):
        old_ratio = old_topics.get(topic, 0) / old_total
        new_ratio = new_topics.get(topic, 0) / new_total
        score += abs(old_ratio - new_ratio)
    return score / 2


def synthetic_item(topic):
    return {
        "prompt": f"Explain a beginner question from {topic}.",
        "answer": f"This is a simple synthetic answer about {topic}.",
        "topic": topic,
        "difficulty": "medium",
    }


def quality_score(items, agreement):
    unique_ratio = len(deduplicate(items)) / len(items)
    topic_balance = len(topic_counts(items)) / 3
    return mean([unique_ratio, agreement, min(topic_balance, 1.0)])


def main():
    section("Chapter 6: Golden Dataset Engineering")

    section("1. Why Golden Datasets Matter")
    print(f"Topic distribution: {dict(topic_counts(ITEMS))}")
    print(f"Difficulty distribution: {dict(difficulty_counts(ITEMS))}")

    section("2. Create, Deduplicate, Balance")
    unique_items = deduplicate(ITEMS)
    print(f"Original items: {len(ITEMS)}")
    print(f"Unique items: {len(unique_items)}")
    print(f"Balanced sample size: {len(balanced_sample(unique_items))}")

    section("3. Annotation Workflow")
    agreement = annotator_agreement(["correct", "correct", "wrong"], ["correct", "wrong", "wrong"])
    print(f"Annotator agreement: {agreement:.2f}")

    section("4. Regression and Prompt Comparison")
    print(f"Prompt B minus Prompt A: {prompt_comparison(0.74, 0.81):+.2f}")

    section("5. Versioning and Drift")
    old_topics = Counter({"astronomy": 6, "biology": 4})
    new_topics = Counter({"astronomy": 3, "biology": 4, "chemistry": 3})
    print(f"Drift score: {drift_score(old_topics, new_topics):.2f}")

    section("6. Synthetic Data")
    print(synthetic_item("chemistry"))

    section("7. Dataset Quality")
    print(f"Quality score: {quality_score(ITEMS, agreement):.2f}")


if __name__ == "__main__":
    main()
