"""
Chapter 6 - Golden Dataset Engineering
Dataset module: Tools for building, curating, versioning, and managing golden datasets.
"""

import csv
import json
import os
import random
import hashlib
import math
import copy
from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------

def load_sample_data() -> dict:
    """Load the curated golden dataset sample."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list:
    """Load training data from train.csv."""
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
    questions: list,
    accuracy: float = 0.7,
    seed: int = 42,
) -> list:
    """Simulate LLM predictions with configurable accuracy."""
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


# ---------------------------------------------------------------------------
# GOLDEN DATASET BUILDER
# ---------------------------------------------------------------------------

class GoldenDatasetBuilder:
    """
    Creates golden evaluation datasets from raw data sources.

    Implements stratified sampling, deduplication, category balancing,
    edge-case inclusion, and metadata enrichment.
    """

    def __init__(self, name: str = "golden_dataset", seed: int = 42):
        self.name = name
        self.seed = seed
        self.rng = random.Random(seed)
        self.items = []
        self.metadata = {
            "name": name,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0.0",
            "quality_tier": "gold",
        }

    def load_from_train_csv(self, limit: Optional[int] = None) -> list:
        """Load raw questions from train.csv."""
        raw = load_train_data(limit=limit)
        return raw

    def categorize_questions(self, questions: list) -> dict:
        """
        Automatically categorize questions by detecting domain keywords.
        In production, this would use an LLM or human annotation.
        """
        categories = defaultdict(list)
        keyword_map = {
            "physics": [
                "force", "energy", "mass", "velocity", "acceleration",
                "momentum", "wave", "quantum", "electron", "photon",
                "gravity", "magnetic", "electric", "thermodynamic",
                "diffraction", "optics", "nuclear", "relativity",
                "spin", "angular", "field", "particle", "radiation",
                "convection", "temperature", "pressure", "entropy",
                "newton", "einstein", "maxwell", "gauss", "heisenberg",
            ],
            "biology": [
                "cell", "dna", "rna", "protein", "gene", "organism",
                "evolution", "species", "enzyme", "membrane", "transport",
                "mitosis", "photosynthesis", "ecosystem", "biological",
            ],
            "chemistry": [
                "chemical", "reaction", "molecule", "atom", "bond",
                "acid", "base", "solution", "compound", "element",
                "metal", "crystallize", "eutectoid", "oxidation",
            ],
            "mathematics": [
                "theorem", "equation", "function", "integral", "derivative",
                "topology", "algebra", "geometry", "matrix", "vector",
                "tiling", "dimension", "skeleton", "manifold", "group",
            ],
            "earth_science": [
                "earthquake", "volcano", "climate", "weather", "ocean",
                "mineral", "rock", "plate", "tectonic", "atmosphere",
            ],
            "astronomy": [
                "star", "planet", "galaxy", "universe", "cosmic",
                "mond", "baryonic", "eddington", "gravitational",
                "astrophysic", "redshift", "blueshift",
            ],
        }

        for q in questions:
            prompt_lower = q["prompt"].lower()
            # Combine prompt and choice text for better categorization
            all_text = prompt_lower
            for choice_text in q["choices"].values():
                all_text += " " + choice_text.lower()

            best_cat = "general"
            best_score = 0
            for category, keywords in keyword_map.items():
                score = sum(1 for kw in keywords if kw in all_text)
                if score > best_score:
                    best_score = score
                    best_cat = category

            q["category"] = best_cat
            categories[best_cat].append(q)

        return dict(categories)

    def estimate_difficulty(self, question: dict) -> str:
        """
        Estimate question difficulty based on heuristics.
        In production, use human ratings or model performance data.
        """
        prompt = question["prompt"]
        choices = question["choices"]

        # Heuristic 1: longer questions tend to be harder
        prompt_len = len(prompt)

        # Heuristic 2: longer answer options suggest more nuance
        avg_choice_len = sum(len(v) for v in choices.values()) / 5

        # Heuristic 3: similarity between choices (crude proxy)
        choice_texts = list(choices.values())
        common_words = set(choice_texts[0].lower().split())
        for ct in choice_texts[1:]:
            common_words &= set(ct.lower().split())
        similarity_ratio = len(common_words) / max(
            len(choice_texts[0].split()), 1
        )

        score = 0
        if prompt_len > 200:
            score += 1
        if prompt_len > 400:
            score += 1
        if avg_choice_len > 100:
            score += 1
        if similarity_ratio > 0.3:
            score += 1  # Similar choices = harder to distinguish

        if score >= 3:
            return "hard"
        elif score >= 1:
            return "medium"
        else:
            return "easy"

    def stratified_sample(
        self,
        questions: list,
        n: int,
        stratify_by: str = "category",
    ) -> list:
        """
        Sample n items maintaining proportional representation across strata.

        Stratified sampling ensures every category/difficulty level is
        represented proportionally in the golden dataset.
        """
        groups = defaultdict(list)
        for q in questions:
            key = q.get(stratify_by, "unknown")
            groups[key].append(q)

        total = len(questions)
        sampled = []

        for key, group_items in groups.items():
            proportion = len(group_items) / total
            group_n = max(1, round(n * proportion))
            group_n = min(group_n, len(group_items))
            chosen = self.rng.sample(group_items, group_n)
            sampled.extend(chosen)

        # Trim or pad to exact n
        if len(sampled) > n:
            sampled = self.rng.sample(sampled, n)
        elif len(sampled) < n:
            remaining = [q for q in questions if q not in sampled]
            extra = self.rng.sample(
                remaining, min(n - len(sampled), len(remaining))
            )
            sampled.extend(extra)

        return sampled

    def deduplicate(self, questions: list, threshold: float = 0.8) -> dict:
        """
        Detect and remove near-duplicate questions.

        Uses word-level Jaccard similarity as a proxy. In production,
        you would use embedding similarity (cosine distance).
        """
        def tokenize(text):
            return set(text.lower().split())

        def jaccard_similarity(set_a, set_b):
            if not set_a or not set_b:
                return 0.0
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            return intersection / union if union > 0 else 0.0

        token_cache = []
        for q in questions:
            tokens = tokenize(q["prompt"])
            token_cache.append(tokens)

        duplicates = []
        unique_indices = set(range(len(questions)))

        for i in range(len(questions)):
            if i not in unique_indices:
                continue
            for j in range(i + 1, len(questions)):
                if j not in unique_indices:
                    continue
                sim = jaccard_similarity(token_cache[i], token_cache[j])
                if sim >= threshold:
                    duplicates.append({
                        "item_a_id": questions[i]["id"],
                        "item_b_id": questions[j]["id"],
                        "similarity": round(sim, 4),
                        "prompt_a_preview": questions[i]["prompt"][:60],
                        "prompt_b_preview": questions[j]["prompt"][:60],
                    })
                    unique_indices.discard(j)

        unique_questions = [questions[i] for i in sorted(unique_indices)]

        return {
            "original_count": len(questions),
            "unique_count": len(unique_questions),
            "duplicates_found": len(duplicates),
            "duplicate_pairs": duplicates[:10],
            "unique_questions": unique_questions,
        }

    def balance_categories(
        self,
        questions: list,
        target_per_category: Optional[int] = None,
    ) -> dict:
        """
        Balance the dataset across categories by undersampling majority
        categories or oversampling minority categories.
        """
        groups = defaultdict(list)
        for q in questions:
            groups[q.get("category", "unknown")].append(q)

        category_counts = {k: len(v) for k, v in groups.items()}

        if target_per_category is None:
            # Use median count as target
            counts = sorted(category_counts.values())
            mid = len(counts) // 2
            target_per_category = counts[mid] if counts else 5

        balanced = []
        balance_report = {}

        for cat, items in groups.items():
            if len(items) >= target_per_category:
                # Undersample
                chosen = self.rng.sample(items, target_per_category)
                action = "undersampled"
            else:
                # Keep all (could oversample, but for golden data we prefer
                # keeping originals and flagging gaps)
                chosen = items
                action = "kept_all (below target)"

            balanced.extend(chosen)
            balance_report[cat] = {
                "original": len(items),
                "after_balancing": len(chosen),
                "target": target_per_category,
                "action": action,
            }

        return {
            "balanced_questions": balanced,
            "balance_report": balance_report,
            "total_before": len(questions),
            "total_after": len(balanced),
        }

    def identify_edge_cases(self, questions: list) -> dict:
        """
        Identify potential edge cases based on heuristics.
        Edge cases are crucial for golden datasets.
        """
        edge_cases = []
        normal_cases = []

        for q in questions:
            is_edge = False
            reasons = []

            # Very long prompt (complex question)
            if len(q["prompt"]) > 500:
                is_edge = True
                reasons.append("very_long_prompt")

            # Short prompt (might be ambiguous)
            if len(q["prompt"]) < 50:
                is_edge = True
                reasons.append("very_short_prompt")

            # Check for negation in prompt (tricky questions)
            negation_words = ["not", "except", "without", "never", "neither"]
            if any(w in q["prompt"].lower().split() for w in negation_words):
                is_edge = True
                reasons.append("contains_negation")

            # Check for multiple correct-sounding options
            choice_lengths = [len(v) for v in q["choices"].values()]
            max_len = max(choice_lengths)
            long_choices = sum(1 for cl in choice_lengths if cl > max_len * 0.8)
            if long_choices >= 3:
                is_edge = True
                reasons.append("multiple_detailed_options")

            q["is_edge_case"] = is_edge
            q["edge_case_reasons"] = reasons

            if is_edge:
                edge_cases.append(q)
            else:
                normal_cases.append(q)

        return {
            "edge_cases": edge_cases,
            "normal_cases": normal_cases,
            "edge_case_count": len(edge_cases),
            "normal_count": len(normal_cases),
            "edge_case_ratio": round(
                len(edge_cases) / max(len(questions), 1), 4
            ),
        }

    def analyze_domain_coverage(self, questions: list) -> dict:
        """
        Analyze how well the dataset covers the domain space.
        Reports gaps and overrepresented areas.
        """
        categories = defaultdict(int)
        subcategories = defaultdict(int)
        difficulties = defaultdict(int)
        prompt_lengths = []

        for q in questions:
            categories[q.get("category", "unknown")] += 1
            difficulties[q.get("difficulty", "unknown")] += 1
            prompt_lengths.append(len(q["prompt"]))

        total = len(questions)
        coverage = {
            "total_items": total,
            "category_coverage": {
                cat: {
                    "count": count,
                    "percentage": round(count / max(total, 1) * 100, 1),
                }
                for cat, count in sorted(
                    categories.items(), key=lambda x: -x[1]
                )
            },
            "difficulty_coverage": {
                diff: {
                    "count": count,
                    "percentage": round(count / max(total, 1) * 100, 1),
                }
                for diff, count in sorted(
                    difficulties.items(), key=lambda x: -x[1]
                )
            },
            "prompt_length_stats": {
                "min": min(prompt_lengths) if prompt_lengths else 0,
                "max": max(prompt_lengths) if prompt_lengths else 0,
                "avg": round(
                    sum(prompt_lengths) / max(len(prompt_lengths), 1), 1
                ),
            },
        }

        # Identify gaps
        expected_categories = {
            "physics", "biology", "chemistry", "mathematics",
            "earth_science", "astronomy",
        }
        missing = expected_categories - set(categories.keys())
        if missing:
            coverage["gaps"] = {
                "missing_categories": list(missing),
                "recommendation": "Add samples from missing categories",
            }

        return coverage

    def build_golden_dataset(
        self,
        questions: list,
        target_size: int = 30,
        include_edge_cases: bool = True,
    ) -> dict:
        """
        End-to-end golden dataset construction pipeline.

        Steps:
        1. Categorize questions
        2. Estimate difficulty
        3. Deduplicate
        4. Identify edge cases
        5. Stratified sample
        6. Balance categories
        7. Analyze coverage
        8. Add metadata
        """
        # Step 1: Categorize
        categorized = self.categorize_questions(questions)
        all_categorized = []
        for cat_items in categorized.values():
            all_categorized.extend(cat_items)

        # Step 2: Estimate difficulty
        for q in all_categorized:
            q["difficulty"] = self.estimate_difficulty(q)

        # Step 3: Deduplicate
        dedup_result = self.deduplicate(all_categorized)
        unique_questions = dedup_result["unique_questions"]

        # Step 4: Identify edge cases
        edge_result = self.identify_edge_cases(unique_questions)

        # Step 5: Stratified sample
        sample_size = min(target_size, len(unique_questions))
        sampled = self.stratified_sample(
            unique_questions, sample_size, stratify_by="category"
        )

        # Step 5b: Ensure edge cases are included
        if include_edge_cases:
            sampled_ids = {q["id"] for q in sampled}
            for ec in edge_result["edge_cases"]:
                if ec["id"] not in sampled_ids and len(sampled) < target_size:
                    sampled.append(ec)
                    sampled_ids.add(ec["id"])

        # Step 6: Analyze coverage
        coverage = self.analyze_domain_coverage(sampled)

        # Step 7: Build final dataset with metadata
        golden_items = []
        for idx, q in enumerate(sampled):
            golden_items.append({
                "golden_id": f"gold_{idx+1:04d}",
                "source_id": q["id"],
                "prompt": q["prompt"],
                "choices": q["choices"],
                "ground_truth": q["ground_truth"],
                "category": q.get("category", "unknown"),
                "difficulty": q.get("difficulty", "unknown"),
                "is_edge_case": q.get("is_edge_case", False),
                "edge_case_reasons": q.get("edge_case_reasons", []),
            })

        self.items = golden_items

        return {
            "dataset_name": self.name,
            "version": self.metadata["version"],
            "total_source_questions": len(questions),
            "deduplication": {
                "before": dedup_result["original_count"],
                "after": dedup_result["unique_count"],
                "removed": dedup_result["duplicates_found"],
            },
            "edge_cases": {
                "total_found": edge_result["edge_case_count"],
                "included": sum(
                    1 for item in golden_items if item["is_edge_case"]
                ),
            },
            "final_dataset_size": len(golden_items),
            "coverage": coverage,
            "items": golden_items,
        }


# ---------------------------------------------------------------------------
# ANNOTATION MANAGER
# ---------------------------------------------------------------------------

class AnnotationManager:
    """
    Manages multi-annotator annotation workflows.

    Simulates multiple annotators labeling the same items and computes
    inter-annotator agreement metrics including Cohen's Kappa.
    """

    def __init__(self, num_annotators: int = 3, seed: int = 42):
        self.num_annotators = num_annotators
        self.rng = random.Random(seed)
        self.annotations = {}

    def simulate_annotations(
        self,
        questions: list,
        annotator_accuracies: Optional[list] = None,
    ) -> dict:
        """
        Simulate multiple annotators labeling the same questions.

        Each annotator has a different accuracy level, reflecting
        real-world variance in annotator quality.
        """
        if annotator_accuracies is None:
            # Default: varying skill levels
            annotator_accuracies = [
                0.90 + self.rng.uniform(-0.05, 0.05)
                for _ in range(self.num_annotators)
            ]

        choices = ["A", "B", "C", "D", "E"]
        all_annotations = []

        for q in questions:
            item_annotations = {
                "question_id": q["id"],
                "ground_truth": q["ground_truth"],
                "annotator_labels": {},
            }

            for ann_idx in range(self.num_annotators):
                ann_id = f"annotator_{ann_idx + 1}"
                accuracy = annotator_accuracies[ann_idx]

                if self.rng.random() < accuracy:
                    label = q["ground_truth"]
                    confidence = self.rng.uniform(0.8, 1.0)
                else:
                    wrong = [c for c in choices if c != q["ground_truth"]]
                    label = self.rng.choice(wrong)
                    confidence = self.rng.uniform(0.3, 0.7)

                item_annotations["annotator_labels"][ann_id] = {
                    "label": label,
                    "confidence": round(confidence, 2),
                    "time_seconds": round(self.rng.uniform(10, 90), 1),
                }

            # Determine consensus via majority vote
            labels = [
                v["label"]
                for v in item_annotations["annotator_labels"].values()
            ]
            label_counts = Counter(labels)
            consensus_label, consensus_count = label_counts.most_common(1)[0]
            item_annotations["consensus"] = {
                "label": consensus_label,
                "agreement_count": consensus_count,
                "total_annotators": self.num_annotators,
                "is_unanimous": consensus_count == self.num_annotators,
                "matches_ground_truth": consensus_label == q["ground_truth"],
            }

            all_annotations.append(item_annotations)

        self.annotations = {a["question_id"]: a for a in all_annotations}

        # Summary statistics
        unanimous = sum(
            1 for a in all_annotations if a["consensus"]["is_unanimous"]
        )
        correct_consensus = sum(
            1 for a in all_annotations
            if a["consensus"]["matches_ground_truth"]
        )

        return {
            "total_items": len(all_annotations),
            "num_annotators": self.num_annotators,
            "annotator_accuracies": [
                round(a, 4) for a in annotator_accuracies
            ],
            "unanimous_agreement": unanimous,
            "unanimous_rate": round(unanimous / max(len(questions), 1), 4),
            "consensus_accuracy": round(
                correct_consensus / max(len(questions), 1), 4
            ),
            "annotations": all_annotations,
        }

    def compute_cohens_kappa(
        self,
        annotator_a_labels: list,
        annotator_b_labels: list,
    ) -> dict:
        """
        Compute Cohen's Kappa for inter-annotator agreement.

        Kappa = (P_observed - P_expected) / (1 - P_expected)

        Interpretation:
          < 0.00  Poor
          0.00-0.20  Slight
          0.21-0.40  Fair
          0.41-0.60  Moderate
          0.61-0.80  Substantial
          0.81-1.00  Almost perfect
        """
        n = len(annotator_a_labels)
        if n != len(annotator_b_labels):
            raise ValueError("Both annotator label lists must be same length")

        # Observed agreement
        agreements = sum(
            1 for a, b in zip(annotator_a_labels, annotator_b_labels)
            if a == b
        )
        p_observed = agreements / n

        # Expected agreement by chance
        all_labels = sorted(
            set(annotator_a_labels) | set(annotator_b_labels)
        )
        p_expected = 0.0
        for label in all_labels:
            p_a = sum(1 for x in annotator_a_labels if x == label) / n
            p_b = sum(1 for x in annotator_b_labels if x == label) / n
            p_expected += p_a * p_b

        # Cohen's Kappa
        if p_expected == 1.0:
            kappa = 1.0
        else:
            kappa = (p_observed - p_expected) / (1 - p_expected)

        # Interpretation
        if kappa < 0:
            interpretation = "poor"
        elif kappa < 0.21:
            interpretation = "slight"
        elif kappa < 0.41:
            interpretation = "fair"
        elif kappa < 0.61:
            interpretation = "moderate"
        elif kappa < 0.81:
            interpretation = "substantial"
        else:
            interpretation = "almost_perfect"

        return {
            "cohens_kappa": round(kappa, 4),
            "p_observed": round(p_observed, 4),
            "p_expected": round(p_expected, 4),
            "interpretation": interpretation,
            "n_items": n,
            "n_agreements": agreements,
        }

    def compute_all_pairwise_kappa(self) -> dict:
        """
        Compute Cohen's Kappa for all annotator pairs.
        """
        if not self.annotations:
            return {"error": "No annotations available. Run simulate_annotations first."}

        annotator_ids = set()
        for item in self.annotations.values():
            annotator_ids.update(item["annotator_labels"].keys())
        annotator_ids = sorted(annotator_ids)

        # Collect labels per annotator
        labels_by_annotator = defaultdict(list)
        item_ids = sorted(self.annotations.keys())
        for item_id in item_ids:
            item = self.annotations[item_id]
            for ann_id in annotator_ids:
                labels_by_annotator[ann_id].append(
                    item["annotator_labels"][ann_id]["label"]
                )

        # All pairwise comparisons
        pairwise_results = {}
        for i in range(len(annotator_ids)):
            for j in range(i + 1, len(annotator_ids)):
                ann_a = annotator_ids[i]
                ann_b = annotator_ids[j]
                pair_key = f"{ann_a}_vs_{ann_b}"
                result = self.compute_cohens_kappa(
                    labels_by_annotator[ann_a],
                    labels_by_annotator[ann_b],
                )
                pairwise_results[pair_key] = result

        # Average kappa
        kappas = [r["cohens_kappa"] for r in pairwise_results.values()]
        avg_kappa = sum(kappas) / max(len(kappas), 1)

        return {
            "pairwise_kappas": pairwise_results,
            "average_kappa": round(avg_kappa, 4),
            "num_pairs": len(pairwise_results),
        }

    def create_annotation_guidelines(self) -> dict:
        """
        Generate a structured annotation guideline document.
        """
        return {
            "title": "Golden Dataset Annotation Guidelines",
            "version": "1.0",
            "task_description": (
                "Annotate science MCQ questions by selecting the single "
                "correct answer from 5 options (A through E)."
            ),
            "steps": [
                "1. Read the question carefully and completely.",
                "2. Read ALL five answer options before selecting.",
                "3. Select the most accurate and complete answer.",
                "4. Rate your confidence (0.0 to 1.0).",
                "5. Estimate the question difficulty (easy/medium/hard).",
                "6. Flag if the question is ambiguous or has errors.",
            ],
            "quality_criteria": {
                "correctness": (
                    "The answer must be factually accurate based on "
                    "established scientific knowledge."
                ),
                "completeness": (
                    "The chosen answer should fully address the question, "
                    "not just be partially correct."
                ),
                "clarity_check": (
                    "If the question itself is unclear or ambiguous, "
                    "flag it for review rather than guessing."
                ),
            },
            "common_pitfalls": [
                "Choosing an answer that is only partially correct",
                "Confusing similar scientific terms (e.g., reddening vs redshifting)",
                "Selecting the first plausible answer without reading all options",
                "Letting familiarity bias override careful reading",
            ],
            "rubric": {
                "5_excellent": "Clearly correct, unambiguous, well-supported",
                "4_good": "Correct with minor stylistic issues",
                "3_acceptable": "Mostly correct but could be more precise",
                "2_poor": "Partially correct or misleading",
                "1_unacceptable": "Factually wrong or completely off-topic",
            },
            "escalation_criteria": [
                "Two annotators disagree on the correct answer",
                "Average confidence below 0.6",
                "Question flagged as ambiguous by any annotator",
            ],
        }

    def quality_control_report(self) -> dict:
        """
        Generate a quality control report for the annotation process.
        """
        if not self.annotations:
            return {"error": "No annotations available."}

        # Per-annotator performance
        annotator_ids = set()
        for item in self.annotations.values():
            annotator_ids.update(item["annotator_labels"].keys())
        annotator_ids = sorted(annotator_ids)

        annotator_stats = {}
        for ann_id in annotator_ids:
            correct = 0
            total = 0
            confidences = []
            times = []
            for item in self.annotations.values():
                ann_data = item["annotator_labels"][ann_id]
                total += 1
                if ann_data["label"] == item["ground_truth"]:
                    correct += 1
                confidences.append(ann_data["confidence"])
                times.append(ann_data["time_seconds"])

            annotator_stats[ann_id] = {
                "accuracy": round(correct / max(total, 1), 4),
                "avg_confidence": round(
                    sum(confidences) / max(len(confidences), 1), 2
                ),
                "avg_time_seconds": round(
                    sum(times) / max(len(times), 1), 1
                ),
                "total_labeled": total,
            }

        # Items needing review
        needs_review = []
        for item_id, item in self.annotations.items():
            consensus = item["consensus"]
            if not consensus["is_unanimous"]:
                needs_review.append({
                    "question_id": item_id,
                    "consensus_label": consensus["label"],
                    "agreement": f"{consensus['agreement_count']}/{consensus['total_annotators']}",
                    "matches_ground_truth": consensus["matches_ground_truth"],
                })

        return {
            "total_items": len(self.annotations),
            "annotator_performance": annotator_stats,
            "items_needing_review": needs_review,
            "review_rate": round(
                len(needs_review) / max(len(self.annotations), 1), 4
            ),
        }


# ---------------------------------------------------------------------------
# DATASET VERSION MANAGER
# ---------------------------------------------------------------------------

class DatasetVersionManager:
    """
    Tracks dataset versions, diffs, and changelog.

    Enables reproducible evaluation by maintaining a history of
    all changes to the golden dataset.
    """

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.versions = {}
        self.current_version = None

    def create_version(
        self,
        version: str,
        items: list,
        author: str = "system",
        description: str = "",
    ) -> dict:
        """Create a new dataset version."""
        # Create hash of content for integrity checking
        content_str = json.dumps(
            [{"id": i.get("golden_id", i.get("id")), "gt": i.get("ground_truth")}
             for i in items],
            sort_keys=True,
        )
        content_hash = hashlib.md5(content_str.encode()).hexdigest()[:12]

        version_record = {
            "version": version,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": author,
            "description": description,
            "item_count": len(items),
            "content_hash": content_hash,
            "items": copy.deepcopy(items),
        }

        self.versions[version] = version_record
        self.current_version = version

        return {
            "version": version,
            "item_count": len(items),
            "content_hash": content_hash,
            "status": "created",
        }

    def compute_diff(self, version_a: str, version_b: str) -> dict:
        """
        Compute the diff between two dataset versions.
        Shows added, removed, and modified items.
        """
        if version_a not in self.versions:
            return {"error": f"Version {version_a} not found"}
        if version_b not in self.versions:
            return {"error": f"Version {version_b} not found"}

        items_a = {
            i.get("golden_id", i.get("id", idx)): i
            for idx, i in enumerate(self.versions[version_a]["items"])
        }
        items_b = {
            i.get("golden_id", i.get("id", idx)): i
            for idx, i in enumerate(self.versions[version_b]["items"])
        }

        ids_a = set(items_a.keys())
        ids_b = set(items_b.keys())

        added = ids_b - ids_a
        removed = ids_a - ids_b
        common = ids_a & ids_b

        modified = []
        for item_id in common:
            a = items_a[item_id]
            b = items_b[item_id]
            if a.get("ground_truth") != b.get("ground_truth"):
                modified.append({
                    "id": item_id,
                    "field": "ground_truth",
                    "old": a.get("ground_truth"),
                    "new": b.get("ground_truth"),
                })
            if a.get("category") != b.get("category"):
                modified.append({
                    "id": item_id,
                    "field": "category",
                    "old": a.get("category"),
                    "new": b.get("category"),
                })

        return {
            "version_a": version_a,
            "version_b": version_b,
            "added_count": len(added),
            "removed_count": len(removed),
            "modified_count": len(modified),
            "unchanged_count": len(common) - len(
                set(m["id"] for m in modified)
            ),
            "added_ids": sorted(added)[:10],
            "removed_ids": sorted(removed)[:10],
            "modifications": modified[:10],
            "summary": (
                f"{len(added)} added, {len(removed)} removed, "
                f"{len(modified)} modified"
            ),
        }

    def get_version_history(self) -> list:
        """Get chronological version history."""
        history = []
        for ver, record in self.versions.items():
            history.append({
                "version": ver,
                "date": record["created_date"],
                "author": record["author"],
                "description": record["description"],
                "item_count": record["item_count"],
                "hash": record["content_hash"],
            })
        return history

    def rollback_to(self, version: str) -> dict:
        """Rollback to a previous version."""
        if version not in self.versions:
            return {"error": f"Version {version} not found"}

        self.current_version = version
        return {
            "rolled_back_to": version,
            "item_count": self.versions[version]["item_count"],
            "hash": self.versions[version]["content_hash"],
        }


# ---------------------------------------------------------------------------
# SYNTHETIC DATA GENERATOR
# ---------------------------------------------------------------------------

class SyntheticDataGenerator:
    """
    Generates synthetic golden dataset items for evaluation.

    In production, this would use an LLM to generate questions.
    Here we simulate the process to demonstrate the workflow.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.templates = self._build_templates()

    def _build_templates(self) -> list:
        """Build question templates for synthetic generation."""
        return [
            {
                "pattern": "What is the relationship between {concept_a} and {concept_b}?",
                "category": "physics",
                "concepts": [
                    ("force", "acceleration"),
                    ("energy", "mass"),
                    ("wavelength", "frequency"),
                    ("voltage", "current"),
                    ("pressure", "volume"),
                ],
            },
            {
                "pattern": "Which statement best describes {concept}?",
                "category": "biology",
                "concepts": [
                    ("mitosis",),
                    ("photosynthesis",),
                    ("natural selection",),
                    ("DNA replication",),
                    ("cellular respiration",),
                ],
            },
            {
                "pattern": "What is the primary function of {concept} in {context}?",
                "category": "chemistry",
                "concepts": [
                    ("catalysts", "chemical reactions"),
                    ("buffers", "solution chemistry"),
                    ("enzymes", "biochemistry"),
                    ("oxidation", "electrochemistry"),
                    ("isotopes", "nuclear chemistry"),
                ],
            },
        ]

    def generate_synthetic_questions(
        self,
        n: int = 10,
        categories: Optional[list] = None,
    ) -> dict:
        """
        Generate synthetic MCQ questions.

        In production, you would:
        1. Prompt an LLM to generate questions in specific formats
        2. Have humans review and validate each question
        3. Add proper ground truth labels
        4. Run quality checks before including in golden dataset
        """
        if categories is None:
            categories = ["physics", "biology", "chemistry"]

        generated = []
        review_queue = []

        for i in range(n):
            cat = self.rng.choice(categories)
            matching_templates = [
                t for t in self.templates if t["category"] == cat
            ]
            if not matching_templates:
                matching_templates = self.templates

            template = self.rng.choice(matching_templates)
            concept_set = self.rng.choice(template["concepts"])

            if len(concept_set) == 1:
                prompt = template["pattern"].format(concept=concept_set[0])
            elif len(concept_set) == 2:
                try:
                    prompt = template["pattern"].format(
                        concept_a=concept_set[0],
                        concept_b=concept_set[1],
                    )
                except (KeyError, IndexError):
                    prompt = template["pattern"].format(
                        concept=concept_set[0],
                        context=concept_set[1],
                    )
            else:
                prompt = template["pattern"].format(concept=concept_set[0])

            correct_answer = self.rng.choice(["A", "B", "C", "D", "E"])

            item = {
                "id": f"synthetic_{i+1:04d}",
                "prompt": prompt,
                "choices": {
                    "A": f"Option A for: {prompt[:30]}",
                    "B": f"Option B for: {prompt[:30]}",
                    "C": f"Option C for: {prompt[:30]}",
                    "D": f"Option D for: {prompt[:30]}",
                    "E": f"Option E for: {prompt[:30]}",
                },
                "ground_truth": correct_answer,
                "category": cat,
                "source": "synthetic",
                "generation_method": "template_based",
                "needs_human_review": True,
                "quality_status": "pending_review",
            }

            generated.append(item)
            review_queue.append({
                "id": item["id"],
                "prompt": item["prompt"],
                "status": "pending_review",
                "priority": "normal",
            })

        return {
            "total_generated": len(generated),
            "categories": dict(
                Counter(g["category"] for g in generated)
            ),
            "items": generated,
            "review_queue": review_queue,
            "warnings": [
                "All synthetic items MUST be human-reviewed before use",
                "Ground truth labels are placeholders - verify each one",
                "Choice text is template-generated - replace with real content",
            ],
        }

    def simulate_human_review(self, items: list) -> dict:
        """
        Simulate a human review workflow for synthetic data.

        In production, humans would:
        1. Check factual correctness
        2. Verify answer options are realistic
        3. Confirm ground truth label
        4. Rate quality and flag issues
        """
        reviewed = []
        approved = 0
        rejected = 0
        needs_revision = 0

        for item in items:
            review_score = self.rng.uniform(0, 1)

            if review_score > 0.7:
                status = "approved"
                approved += 1
            elif review_score > 0.3:
                status = "needs_revision"
                needs_revision += 1
            else:
                status = "rejected"
                rejected += 1

            reviewed.append({
                "id": item["id"],
                "review_status": status,
                "reviewer_id": f"reviewer_{self.rng.randint(1, 5)}",
                "quality_score": round(review_score * 5, 1),
                "feedback": {
                    "approved": "Factually correct, well-formed question",
                    "needs_revision": "Answer options need improvement",
                    "rejected": "Question is ambiguous or incorrect",
                }.get(status, ""),
            })

        return {
            "total_reviewed": len(reviewed),
            "approved": approved,
            "needs_revision": needs_revision,
            "rejected": rejected,
            "approval_rate": round(approved / max(len(items), 1), 4),
            "reviewed_items": reviewed,
        }

    def validate_synthetic_data(self, items: list) -> dict:
        """
        Run validation checks on synthetic data.
        """
        issues = []
        valid_count = 0

        for item in items:
            item_issues = []

            # Check prompt is not empty
            if not item.get("prompt") or len(item["prompt"]) < 10:
                item_issues.append("prompt_too_short")

            # Check all 5 choices exist
            choices = item.get("choices", {})
            if len(choices) != 5:
                item_issues.append("missing_choices")

            # Check ground truth is valid
            gt = item.get("ground_truth", "")
            if gt not in ["A", "B", "C", "D", "E"]:
                item_issues.append("invalid_ground_truth")

            # Check for duplicate choice text
            choice_texts = list(choices.values())
            if len(set(choice_texts)) < len(choice_texts):
                item_issues.append("duplicate_choices")

            if item_issues:
                issues.append({
                    "id": item.get("id"),
                    "issues": item_issues,
                })
            else:
                valid_count += 1

        return {
            "total_checked": len(items),
            "valid": valid_count,
            "invalid": len(issues),
            "validation_rate": round(valid_count / max(len(items), 1), 4),
            "issues": issues[:10],
        }


# ---------------------------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("DATASET MODULE - Quick Test")
    print("=" * 60)

    # Test data loading
    train = load_train_data(limit=10)
    print(f"\nLoaded {len(train)} training questions")
    print(f"First question: {train[0]['prompt'][:80]}...")

    # Test golden dataset builder
    builder = GoldenDatasetBuilder()
    questions = load_train_data(limit=50)
    result = builder.build_golden_dataset(questions, target_size=15)
    print(f"\nGolden dataset built: {result['final_dataset_size']} items")

    # Test annotation manager
    ann_mgr = AnnotationManager(num_annotators=3)
    ann_result = ann_mgr.simulate_annotations(questions[:10])
    print(f"Annotation consensus accuracy: {ann_result['consensus_accuracy']}")

    # Test version manager
    ver_mgr = DatasetVersionManager("test_dataset")
    ver_mgr.create_version("1.0.0", result["items"][:10])
    print(f"Version created: 1.0.0")

    print("\nAll dataset module tests passed.")
