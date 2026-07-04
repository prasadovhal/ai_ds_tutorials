"""
Chapter 7 - Evaluation Dataset Engineering
Dataset module: Load and prepare evaluation data from multiple sources.
"""

import csv
import json
import os
import random
import math
from collections import Counter
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


def load_sample_data() -> dict:
    """Load the sample dataset with intentional quality issues."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load train.csv with 199 MCQ science questions."""
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


# ---------------------------------------------------------------------------
# ANSWER DISTRIBUTION ANALYSIS
# ---------------------------------------------------------------------------

def analyze_answer_distribution(questions: list[dict]) -> dict:
    """Analyze the distribution of correct answers across options."""
    answers = [q["ground_truth"] for q in questions]
    counts = Counter(answers)
    total = len(answers)
    distribution = {}
    for label in sorted(counts.keys()):
        count = counts[label]
        distribution[label] = {
            "count": count,
            "percentage": round(count / total * 100, 2),
        }
    # Compute balance metrics
    expected_pct = 100.0 / len(distribution)
    max_deviation = max(
        abs(v["percentage"] - expected_pct) for v in distribution.values()
    )
    chi_squared = sum(
        (v["count"] - total / len(distribution)) ** 2 / (total / len(distribution))
        for v in distribution.values()
    )
    return {
        "total": total,
        "distribution": distribution,
        "expected_pct_if_balanced": round(expected_pct, 2),
        "max_deviation_from_expected": round(max_deviation, 2),
        "chi_squared": round(chi_squared, 4),
    }


# ---------------------------------------------------------------------------
# TOPIC DETECTION (heuristic, no ML)
# ---------------------------------------------------------------------------

TOPIC_KEYWORDS = {
    "physics": [
        "force", "energy", "momentum", "wave", "quantum", "relativity",
        "gravity", "mass", "acceleration", "velocity", "electric",
        "magnetic", "thermodynamic", "entropy", "diffraction", "optics",
        "photon", "newton", "electromagnetic", "field", "particle",
        "spin", "angular", "frequency", "wavelength", "nuclear",
        "radiation", "mechanics", "kinetic", "potential",
    ],
    "chemistry": [
        "chemical", "molecule", "atom", "bond", "reaction", "element",
        "compound", "acid", "base", "ph", "oxidation", "reduction",
        "electron", "proton", "neutron", "ion", "solution", "solvent",
        "molar", "avogadro", "periodic", "valence",
    ],
    "biology": [
        "cell", "dna", "rna", "protein", "gene", "evolution",
        "organism", "species", "ecology", "photosynthesis", "mitosis",
        "meiosis", "enzyme", "membrane", "tissue", "organ",
        "chromosome", "mutation", "natural selection", "metabolism",
        "transport", "convection",
    ],
    "astronomy": [
        "planet", "star", "galaxy", "universe", "solar", "lunar",
        "orbit", "telescope", "nebula", "supernova", "black hole",
        "cosmology", "red giant", "white dwarf", "asteroid", "comet",
        "tidal", "eddington", "gravitational wave",
    ],
    "mathematics": [
        "theorem", "proof", "equation", "integral", "derivative",
        "function", "matrix", "vector", "topology", "algebra",
        "geometry", "calculus", "probability", "statistics",
        "dimension", "axiom", "set theory", "manifold",
    ],
    "earth_science": [
        "geology", "tectonic", "earthquake", "volcano", "mineral",
        "rock", "erosion", "atmosphere", "climate", "weather",
        "ocean", "continent", "fossil", "sediment",
    ],
}


def detect_topic(prompt: str) -> str:
    """Detect topic of a question using keyword matching."""
    prompt_lower = prompt.lower()
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in prompt_lower)
        if score > 0:
            scores[topic] = score
    if not scores:
        return "other"
    return max(scores, key=scores.get)


def analyze_topic_coverage(questions: list[dict]) -> dict:
    """Analyze how well questions cover different topics."""
    topics = [detect_topic(q["prompt"]) for q in questions]
    counts = Counter(topics)
    total = len(topics)

    coverage = {}
    for topic in sorted(counts.keys()):
        count = counts[topic]
        coverage[topic] = {
            "count": count,
            "percentage": round(count / total * 100, 2),
        }

    all_known_topics = set(TOPIC_KEYWORDS.keys())
    covered_topics = set(counts.keys()) - {"other"}
    missing_topics = all_known_topics - covered_topics

    return {
        "total_questions": total,
        "topics_found": len(covered_topics),
        "topics_defined": len(all_known_topics),
        "coverage_ratio": round(len(covered_topics) / len(all_known_topics), 4),
        "distribution": coverage,
        "missing_topics": sorted(missing_topics),
    }


# ---------------------------------------------------------------------------
# DIFFICULTY ESTIMATION (heuristic)
# ---------------------------------------------------------------------------

def estimate_difficulty(question: dict) -> str:
    """Estimate question difficulty based on prompt length and vocabulary."""
    prompt = question["prompt"]
    word_count = len(prompt.split())
    avg_word_len = (
        sum(len(w) for w in prompt.split()) / max(word_count, 1)
    )

    # Long prompts with technical vocabulary tend to be harder
    if word_count > 40 and avg_word_len > 6:
        return "hard"
    elif word_count > 25 or avg_word_len > 5.5:
        return "medium"
    else:
        return "easy"


def analyze_difficulty_distribution(questions: list[dict]) -> dict:
    """Analyze difficulty distribution of questions."""
    difficulties = [estimate_difficulty(q) for q in questions]
    counts = Counter(difficulties)
    total = len(difficulties)

    distribution = {}
    for level in ["easy", "medium", "hard"]:
        count = counts.get(level, 0)
        distribution[level] = {
            "count": count,
            "percentage": round(count / total * 100, 2),
        }

    return {
        "total": total,
        "distribution": distribution,
    }


# ---------------------------------------------------------------------------
# PROMPT LENGTH ANALYSIS
# ---------------------------------------------------------------------------

def analyze_prompt_lengths(questions: list[dict]) -> dict:
    """Analyze distribution of prompt lengths (words and characters)."""
    word_lengths = [len(q["prompt"].split()) for q in questions]
    char_lengths = [len(q["prompt"]) for q in questions]

    def stats(values):
        n = len(values)
        if n == 0:
            return {}
        sorted_v = sorted(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        return {
            "min": sorted_v[0],
            "max": sorted_v[-1],
            "mean": round(mean, 2),
            "median": sorted_v[n // 2],
            "std": round(math.sqrt(variance), 2),
            "p25": sorted_v[int(n * 0.25)],
            "p75": sorted_v[int(n * 0.75)],
        }

    return {
        "word_lengths": stats(word_lengths),
        "char_lengths": stats(char_lengths),
    }


# ---------------------------------------------------------------------------
# DUPLICATE DETECTION
# ---------------------------------------------------------------------------

def find_duplicates(questions: list[dict], threshold: float = 0.8) -> list[dict]:
    """Find near-duplicate questions using word overlap (Jaccard similarity)."""
    duplicates = []
    n = len(questions)

    for i in range(n):
        words_i = set(questions[i]["prompt"].lower().split())
        for j in range(i + 1, n):
            words_j = set(questions[j]["prompt"].lower().split())
            if not words_i or not words_j:
                continue
            intersection = len(words_i & words_j)
            union = len(words_i | words_j)
            similarity = intersection / union if union > 0 else 0

            if similarity >= threshold:
                duplicates.append({
                    "id_1": questions[i]["id"],
                    "id_2": questions[j]["id"],
                    "similarity": round(similarity, 4),
                    "prompt_1": questions[i]["prompt"][:80] + "...",
                    "prompt_2": questions[j]["prompt"][:80] + "...",
                })

    return duplicates


# ---------------------------------------------------------------------------
# SIMULATED PREDICTIONS
# ---------------------------------------------------------------------------

def simulate_llm_predictions(
    questions: list[dict],
    accuracy: float = 0.7,
    seed: int = 42,
) -> list[str]:
    """Simulate LLM predictions with a given accuracy level."""
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


def generate_annotator_labels(
    questions: list[dict],
    n_annotators: int = 3,
    agreement_rate: float = 0.85,
    seed: int = 123,
) -> list[list[str]]:
    """Simulate multiple annotator labels for inter-annotator agreement."""
    rng = random.Random(seed)
    choices = ["A", "B", "C", "D", "E"]
    all_labels = []
    for q in questions:
        labels = []
        for _ in range(n_annotators):
            if rng.random() < agreement_rate:
                labels.append(q["ground_truth"])
            else:
                wrong = [c for c in choices if c != q["ground_truth"]]
                labels.append(rng.choice(wrong))
        all_labels.append(labels)
    return all_labels
