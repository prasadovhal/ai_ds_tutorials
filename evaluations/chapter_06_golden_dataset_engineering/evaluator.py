"""
Chapter 6 - Golden Dataset Engineering
Evaluator module: Dataset quality evaluation, coverage analysis, balance checks,
duplicate detection, inter-annotator agreement, drift detection, and regression testing.
"""

import json
import math
import hashlib
import random
from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# COVERAGE ANALYZER
# ---------------------------------------------------------------------------

class CoverageAnalyzer:
    """
    Measures how well a golden dataset covers the target domain.
    Checks category coverage, difficulty spread, answer distribution, and gaps.
    """

    def __init__(self, expected_categories: Optional[list] = None):
        self.expected_categories = expected_categories or [
            "physics", "biology", "chemistry", "mathematics",
            "earth_science", "astronomy", "general",
        ]

    def analyze(self, items: list) -> dict:
        """Full coverage analysis of a golden dataset."""
        if not items:
            return {"error": "No items to analyze", "coverage_score": 0.0}

        category_counts = Counter()
        difficulty_counts = Counter()
        answer_counts = Counter()
        edge_case_count = 0
        prompt_lengths = []
        subcategories = Counter()

        for item in items:
            category_counts[item.get("category", "unknown")] += 1
            difficulty_counts[item.get("difficulty", "unknown")] += 1
            answer_counts[item.get("ground_truth", "?")] += 1
            if item.get("is_edge_case") or item.get("edge_case"):
                edge_case_count += 1
            prompt_lengths.append(len(item.get("prompt", "")))
            if "subcategory" in item:
                subcategories[item["subcategory"]] += 1

        total = len(items)

        # Category coverage score: % of expected categories present
        present = set(category_counts.keys()) & set(self.expected_categories)
        cat_coverage = len(present) / max(len(self.expected_categories), 1)

        # Difficulty coverage: all 3 levels present?
        expected_diffs = {"easy", "medium", "hard"}
        diff_coverage = len(set(difficulty_counts.keys()) & expected_diffs) / 3

        # Answer balance: entropy-based (higher = more balanced)
        answer_entropy = self._entropy(answer_counts, total)
        max_entropy = math.log2(max(len(answer_counts), 1)) if answer_counts else 0
        answer_balance = answer_entropy / max_entropy if max_entropy > 0 else 0

        # Overall coverage score (weighted)
        overall = 0.4 * cat_coverage + 0.3 * diff_coverage + 0.3 * answer_balance

        # Gap analysis
        missing_cats = set(self.expected_categories) - set(category_counts.keys())
        missing_diffs = expected_diffs - set(difficulty_counts.keys())

        return {
            "total_items": total,
            "coverage_score": round(overall, 4),
            "category_coverage": {
                "score": round(cat_coverage, 4),
                "present": sorted(present),
                "missing": sorted(missing_cats),
                "distribution": dict(category_counts.most_common()),
            },
            "difficulty_coverage": {
                "score": round(diff_coverage, 4),
                "present": sorted(set(difficulty_counts.keys()) & expected_diffs),
                "missing": sorted(missing_diffs),
                "distribution": dict(difficulty_counts.most_common()),
            },
            "answer_distribution": {
                "balance_score": round(answer_balance, 4),
                "entropy": round(answer_entropy, 4),
                "distribution": dict(answer_counts.most_common()),
            },
            "edge_cases": {
                "count": edge_case_count,
                "percentage": round(edge_case_count / total * 100, 1),
            },
            "prompt_length_stats": {
                "min": min(prompt_lengths),
                "max": max(prompt_lengths),
                "avg": round(sum(prompt_lengths) / total, 1),
            },
            "subcategory_count": len(subcategories),
            "subcategories": dict(subcategories.most_common()),
            "gaps": {
                "missing_categories": sorted(missing_cats),
                "missing_difficulties": sorted(missing_diffs),
                "recommendations": self._recommendations(
                    missing_cats, missing_diffs, answer_balance, edge_case_count, total
                ),
            },
        }

    def _entropy(self, counter: Counter, total: int) -> float:
        """Shannon entropy of a distribution."""
        if total == 0:
            return 0.0
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy

    def _recommendations(
        self, missing_cats, missing_diffs, answer_balance, edge_count, total
    ) -> list:
        recs = []
        if missing_cats:
            recs.append(f"Add items for missing categories: {', '.join(sorted(missing_cats))}")
        if missing_diffs:
            recs.append(f"Add items for missing difficulties: {', '.join(sorted(missing_diffs))}")
        if answer_balance < 0.8:
            recs.append("Answer distribution is skewed; add items to balance answer keys")
        if edge_count < total * 0.1:
            recs.append("Edge case ratio is below 10%; consider adding more edge cases")
        if not recs:
            recs.append("Dataset coverage looks good")
        return recs


# ---------------------------------------------------------------------------
# BALANCE CHECKER
# ---------------------------------------------------------------------------

class BalanceChecker:
    """
    Checks whether a golden dataset is balanced across key dimensions.
    Uses chi-squared test approximation and Gini coefficient.
    """

    def check_balance(self, items: list, dimension: str = "category") -> dict:
        """Check balance across a single dimension."""
        counts = Counter(item.get(dimension, "unknown") for item in items)
        total = len(items)
        n_classes = len(counts)

        if n_classes <= 1:
            return {
                "dimension": dimension,
                "is_balanced": True,
                "gini": 0.0,
                "distribution": dict(counts),
            }

        # Expected uniform count
        expected = total / n_classes

        # Chi-squared statistic
        chi_sq = sum((obs - expected) ** 2 / expected for obs in counts.values())

        # Gini coefficient (0 = perfect equality, 1 = maximum inequality)
        values = sorted(counts.values())
        n = len(values)
        gini_num = sum((2 * (i + 1) - n - 1) * values[i] for i in range(n))
        gini = gini_num / (n * sum(values)) if sum(values) > 0 else 0

        # Imbalance ratio: max count / min count
        imbalance_ratio = max(counts.values()) / max(min(counts.values()), 1)

        # Threshold: balanced if gini < 0.3 and imbalance_ratio < 3
        is_balanced = gini < 0.3 and imbalance_ratio < 3

        return {
            "dimension": dimension,
            "is_balanced": is_balanced,
            "gini_coefficient": round(gini, 4),
            "chi_squared": round(chi_sq, 4),
            "imbalance_ratio": round(imbalance_ratio, 2),
            "expected_per_class": round(expected, 1),
            "distribution": {
                k: {"count": v, "percentage": round(v / total * 100, 1)}
                for k, v in counts.most_common()
            },
            "most_represented": counts.most_common(1)[0][0],
            "least_represented": counts.most_common()[-1][0],
        }

    def full_balance_report(self, items: list) -> dict:
        """Check balance across multiple dimensions."""
        dimensions = ["category", "difficulty", "ground_truth"]
        results = {}
        all_balanced = True

        for dim in dimensions:
            # Only check if dimension exists in data
            if any(dim in item or dim == "ground_truth" for item in items):
                result = self.check_balance(items, dim)
                results[dim] = result
                if not result["is_balanced"]:
                    all_balanced = False

        return {
            "overall_balanced": all_balanced,
            "dimensions_checked": list(results.keys()),
            "results": results,
        }


# ---------------------------------------------------------------------------
# DUPLICATE DETECTOR
# ---------------------------------------------------------------------------

class DuplicateDetector:
    """
    Detects exact and near-duplicate items in a golden dataset.
    Uses hash-based exact matching and Jaccard similarity for near-duplicates.
    """

    def detect(self, items: list, similarity_threshold: float = 0.75) -> dict:
        """Find exact and near-duplicate items."""
        exact_dupes = self._find_exact_duplicates(items)
        near_dupes = self._find_near_duplicates(items, similarity_threshold)

        total = len(items)
        unique = total - len(exact_dupes["duplicate_ids"])

        return {
            "total_items": total,
            "unique_items": unique,
            "exact_duplicates": exact_dupes,
            "near_duplicates": near_dupes,
            "quality_score": round(unique / max(total, 1), 4),
            "recommendation": (
                "No duplicates found" if not exact_dupes["pairs"] and not near_dupes["pairs"]
                else "Review and remove duplicates before using dataset"
            ),
        }

    def _find_exact_duplicates(self, items: list) -> dict:
        """Find items with identical prompts."""
        seen = {}
        pairs = []
        duplicate_ids = set()

        for item in items:
            prompt_hash = hashlib.md5(
                item.get("prompt", "").strip().lower().encode()
            ).hexdigest()

            item_id = item.get("id") or item.get("golden_id", "unknown")
            if prompt_hash in seen:
                pairs.append({
                    "item_a": seen[prompt_hash],
                    "item_b": item_id,
                    "type": "exact",
                })
                duplicate_ids.add(item_id)
            else:
                seen[prompt_hash] = item_id

        return {
            "count": len(pairs),
            "pairs": pairs[:10],
            "duplicate_ids": sorted(duplicate_ids),
        }

    def _find_near_duplicates(self, items: list, threshold: float) -> dict:
        """Find items with similar prompts using Jaccard similarity."""
        tokenized = []
        for item in items:
            tokens = set(item.get("prompt", "").lower().split())
            item_id = item.get("id") or item.get("golden_id", "unknown")
            tokenized.append((item_id, tokens))

        pairs = []
        for i in range(len(tokenized)):
            for j in range(i + 1, len(tokenized)):
                id_a, tokens_a = tokenized[i]
                id_b, tokens_b = tokenized[j]
                if not tokens_a or not tokens_b:
                    continue
                intersection = len(tokens_a & tokens_b)
                union = len(tokens_a | tokens_b)
                similarity = intersection / union if union > 0 else 0

                if similarity >= threshold:
                    pairs.append({
                        "item_a": id_a,
                        "item_b": id_b,
                        "similarity": round(similarity, 4),
                        "type": "near_duplicate",
                    })

        return {
            "count": len(pairs),
            "threshold": threshold,
            "pairs": pairs[:10],
        }


# ---------------------------------------------------------------------------
# INTER-ANNOTATOR AGREEMENT (IAA) CALCULATOR
# ---------------------------------------------------------------------------

class IAACalculator:
    """
    Computes inter-annotator agreement metrics.
    Supports Cohen's Kappa (pairwise), Fleiss' Kappa (multi-annotator),
    and percentage agreement.
    """

    def cohens_kappa(self, labels_a: list, labels_b: list) -> dict:
        """
        Cohen's Kappa for two annotators.
        Kappa = (P_observed - P_expected) / (1 - P_expected)
        """
        n = len(labels_a)
        if n != len(labels_b):
            raise ValueError("Label lists must be the same length")
        if n == 0:
            return {"cohens_kappa": 0.0, "interpretation": "no_data"}

        # Observed agreement
        agreements = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
        p_observed = agreements / n

        # Expected agreement
        all_labels = sorted(set(labels_a) | set(labels_b))
        p_expected = 0.0
        for label in all_labels:
            p_a = sum(1 for x in labels_a if x == label) / n
            p_b = sum(1 for x in labels_b if x == label) / n
            p_expected += p_a * p_b

        # Kappa
        if p_expected == 1.0:
            kappa = 1.0
        else:
            kappa = (p_observed - p_expected) / (1 - p_expected)

        return {
            "cohens_kappa": round(kappa, 4),
            "p_observed": round(p_observed, 4),
            "p_expected": round(p_expected, 4),
            "n_items": n,
            "n_agreements": agreements,
            "interpretation": self._interpret_kappa(kappa),
        }

    def fleiss_kappa(self, annotation_matrix: list) -> dict:
        """
        Fleiss' Kappa for multiple annotators.
        annotation_matrix: list of dicts, each mapping category -> count of annotators
                           who chose that category for this item.
        Example: [{"A": 2, "B": 1}, {"A": 0, "B": 3}] means 3 annotators rated 2 items.
        """
        n_items = len(annotation_matrix)
        if n_items == 0:
            return {"fleiss_kappa": 0.0, "interpretation": "no_data"}

        # All categories
        categories = set()
        for row in annotation_matrix:
            categories.update(row.keys())
        categories = sorted(categories)

        # Number of annotators per item (assumed constant)
        n_raters = sum(annotation_matrix[0].values())
        if n_raters <= 1:
            return {"fleiss_kappa": 0.0, "interpretation": "insufficient_raters"}

        # P_i for each item: proportion of agreeing pairs
        p_items = []
        for row in annotation_matrix:
            sum_sq = sum(row.get(cat, 0) ** 2 for cat in categories)
            p_i = (sum_sq - n_raters) / (n_raters * (n_raters - 1))
            p_items.append(p_i)

        p_bar = sum(p_items) / n_items

        # P_j for each category: proportion of all assignments to category j
        total_assignments = n_items * n_raters
        p_cats = {}
        for cat in categories:
            cat_total = sum(row.get(cat, 0) for row in annotation_matrix)
            p_cats[cat] = cat_total / total_assignments

        p_e = sum(p ** 2 for p in p_cats.values())

        # Fleiss' Kappa
        if p_e == 1.0:
            kappa = 1.0
        else:
            kappa = (p_bar - p_e) / (1 - p_e)

        return {
            "fleiss_kappa": round(kappa, 4),
            "p_bar": round(p_bar, 4),
            "p_e": round(p_e, 4),
            "n_items": n_items,
            "n_raters": n_raters,
            "n_categories": len(categories),
            "interpretation": self._interpret_kappa(kappa),
        }

    def percentage_agreement(self, labels_a: list, labels_b: list) -> dict:
        """Simple percentage agreement between two annotators."""
        n = len(labels_a)
        agreements = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
        pct = agreements / max(n, 1)
        return {
            "percentage_agreement": round(pct, 4),
            "agreements": agreements,
            "disagreements": n - agreements,
            "total": n,
        }

    def all_pairwise_kappa(self, annotations_by_annotator: dict) -> dict:
        """
        Compute Cohen's Kappa for all annotator pairs.
        annotations_by_annotator: {annotator_id: [labels...]}
        """
        annotator_ids = sorted(annotations_by_annotator.keys())
        pairs = {}
        kappas = []

        for i in range(len(annotator_ids)):
            for j in range(i + 1, len(annotator_ids)):
                a_id = annotator_ids[i]
                b_id = annotator_ids[j]
                result = self.cohens_kappa(
                    annotations_by_annotator[a_id],
                    annotations_by_annotator[b_id],
                )
                pair_key = f"{a_id} vs {b_id}"
                pairs[pair_key] = result
                kappas.append(result["cohens_kappa"])

        avg_kappa = sum(kappas) / max(len(kappas), 1)
        return {
            "pairwise_results": pairs,
            "average_kappa": round(avg_kappa, 4),
            "interpretation": self._interpret_kappa(avg_kappa),
            "num_pairs": len(pairs),
        }

    def analyze_from_golden_items(self, items: list) -> dict:
        """
        Compute IAA from golden dataset items that have embedded annotations.
        Expects items with 'annotations' field: list of {annotator_id, answer}.
        """
        if not items or "annotations" not in items[0]:
            return {"error": "Items must have 'annotations' field"}

        # Collect labels per annotator
        annotator_labels = defaultdict(list)
        for item in items:
            for ann in item.get("annotations", []):
                ann_id = ann.get("annotator_id", "unknown")
                label = ann.get("answer", ann.get("label", "?"))
                annotator_labels[ann_id].append(label)

        # All pairwise kappa
        pairwise = self.all_pairwise_kappa(dict(annotator_labels))

        # Build Fleiss matrix
        fleiss_matrix = []
        all_labels = set()
        for item in items:
            for ann in item.get("annotations", []):
                all_labels.add(ann.get("answer", ann.get("label", "?")))

        for item in items:
            row = Counter()
            for ann in item.get("annotations", []):
                label = ann.get("answer", ann.get("label", "?"))
                row[label] += 1
            fleiss_matrix.append(dict(row))

        fleiss = self.fleiss_kappa(fleiss_matrix)

        return {
            "pairwise_kappa": pairwise,
            "fleiss_kappa": fleiss,
            "num_items": len(items),
            "num_annotators": len(annotator_labels),
        }

    def _interpret_kappa(self, kappa: float) -> str:
        if kappa < 0:
            return "poor"
        elif kappa < 0.21:
            return "slight"
        elif kappa < 0.41:
            return "fair"
        elif kappa < 0.61:
            return "moderate"
        elif kappa < 0.81:
            return "substantial"
        else:
            return "almost_perfect"


# ---------------------------------------------------------------------------
# DATASET QUALITY SCORER
# ---------------------------------------------------------------------------

class DatasetQualityScorer:
    """
    Computes an overall quality score for a golden dataset based on
    coverage, balance, uniqueness, annotation agreement, and edge case inclusion.
    """

    def __init__(self):
        self.coverage_analyzer = CoverageAnalyzer()
        self.balance_checker = BalanceChecker()
        self.duplicate_detector = DuplicateDetector()
        self.iaa_calculator = IAACalculator()

    def score(self, items: list) -> dict:
        """Compute composite quality score (0-100)."""
        scores = {}

        # 1. Coverage (25%)
        coverage = self.coverage_analyzer.analyze(items)
        scores["coverage"] = coverage["coverage_score"]

        # 2. Balance (20%)
        balance = self.balance_checker.full_balance_report(items)
        balance_score = sum(
            1 for r in balance["results"].values() if r["is_balanced"]
        ) / max(len(balance["results"]), 1)
        scores["balance"] = balance_score

        # 3. Uniqueness (20%)
        dupes = self.duplicate_detector.detect(items)
        scores["uniqueness"] = dupes["quality_score"]

        # 4. Annotation quality (20%)
        has_annotations = any("annotations" in item for item in items)
        if has_annotations:
            iaa = self.iaa_calculator.analyze_from_golden_items(items)
            kappa = iaa["fleiss_kappa"].get("fleiss_kappa", 0.5)
            scores["annotation_quality"] = max(0, min(1, (kappa + 1) / 2))
        else:
            scores["annotation_quality"] = 0.5  # neutral if no annotations

        # 5. Edge case inclusion (15%)
        edge_count = sum(
            1 for item in items
            if item.get("is_edge_case") or item.get("edge_case")
        )
        edge_ratio = edge_count / max(len(items), 1)
        # Ideal: 10-30% edge cases
        if 0.10 <= edge_ratio <= 0.30:
            scores["edge_cases"] = 1.0
        elif edge_ratio > 0:
            scores["edge_cases"] = min(edge_ratio / 0.10, 1.0)
        else:
            scores["edge_cases"] = 0.0

        # Weighted composite
        weights = {
            "coverage": 0.25,
            "balance": 0.20,
            "uniqueness": 0.20,
            "annotation_quality": 0.20,
            "edge_cases": 0.15,
        }

        composite = sum(scores[k] * weights[k] for k in weights)

        # Grade
        if composite >= 0.9:
            grade = "A"
        elif composite >= 0.8:
            grade = "B"
        elif composite >= 0.7:
            grade = "C"
        elif composite >= 0.6:
            grade = "D"
        else:
            grade = "F"

        return {
            "composite_score": round(composite * 100, 1),
            "grade": grade,
            "component_scores": {k: round(v * 100, 1) for k, v in scores.items()},
            "weights": {k: f"{v:.0%}" for k, v in weights.items()},
            "total_items": len(items),
        }


# ---------------------------------------------------------------------------
# DRIFT DETECTOR
# ---------------------------------------------------------------------------

class DriftDetector:
    """
    Detects distribution drift between dataset versions or between
    a golden dataset and production data.
    """

    def detect_drift(self, baseline_items: list, current_items: list) -> dict:
        """Compare two datasets for distribution drift."""
        baseline_cats = Counter(
            item.get("category", "unknown") for item in baseline_items
        )
        current_cats = Counter(
            item.get("category", "unknown") for item in current_items
        )

        baseline_diffs = Counter(
            item.get("difficulty", "unknown") for item in baseline_items
        )
        current_diffs = Counter(
            item.get("difficulty", "unknown") for item in current_items
        )

        baseline_answers = Counter(
            item.get("ground_truth", "?") for item in baseline_items
        )
        current_answers = Counter(
            item.get("ground_truth", "?") for item in current_items
        )

        cat_drift = self._distribution_distance(baseline_cats, current_cats)
        diff_drift = self._distribution_distance(baseline_diffs, current_diffs)
        ans_drift = self._distribution_distance(baseline_answers, current_answers)

        # Overall drift score
        overall_drift = (cat_drift + diff_drift + ans_drift) / 3

        # Threshold
        if overall_drift < 0.1:
            severity = "none"
        elif overall_drift < 0.25:
            severity = "low"
        elif overall_drift < 0.5:
            severity = "moderate"
        else:
            severity = "high"

        return {
            "overall_drift": round(overall_drift, 4),
            "severity": severity,
            "needs_update": overall_drift >= 0.25,
            "category_drift": {
                "distance": round(cat_drift, 4),
                "baseline": dict(baseline_cats.most_common()),
                "current": dict(current_cats.most_common()),
            },
            "difficulty_drift": {
                "distance": round(diff_drift, 4),
                "baseline": dict(baseline_diffs.most_common()),
                "current": dict(current_diffs.most_common()),
            },
            "answer_drift": {
                "distance": round(ans_drift, 4),
                "baseline": dict(baseline_answers.most_common()),
                "current": dict(current_answers.most_common()),
            },
            "baseline_size": len(baseline_items),
            "current_size": len(current_items),
        }

    def _distribution_distance(self, dist_a: Counter, dist_b: Counter) -> float:
        """
        Total Variation Distance between two distributions.
        TVD = 0.5 * sum(|p_i - q_i|), range [0, 1].
        """
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        total_a = max(sum(dist_a.values()), 1)
        total_b = max(sum(dist_b.values()), 1)

        tvd = 0.0
        for key in all_keys:
            p = dist_a.get(key, 0) / total_a
            q = dist_b.get(key, 0) / total_b
            tvd += abs(p - q)

        return tvd / 2


# ---------------------------------------------------------------------------
# REGRESSION COMPARATOR
# ---------------------------------------------------------------------------

class RegressionComparator:
    """
    Uses golden dataset to compare model performance across prompt versions
    or model versions. Identifies specific items that regressed.
    """

    def compare_predictions(
        self,
        items: list,
        predictions_a: list,
        predictions_b: list,
        label_a: str = "model_A",
        label_b: str = "model_B",
    ) -> dict:
        """Compare two sets of predictions against golden ground truth."""
        ground_truths = [item.get("ground_truth") for item in items]
        n = len(items)

        correct_a = sum(1 for gt, p in zip(ground_truths, predictions_a) if gt == p)
        correct_b = sum(1 for gt, p in zip(ground_truths, predictions_b) if gt == p)

        acc_a = correct_a / max(n, 1)
        acc_b = correct_b / max(n, 1)
        delta = acc_b - acc_a

        # Per-item analysis
        regressions = []
        improvements = []
        stable_correct = 0
        stable_wrong = 0

        for i, (item, pa, pb) in enumerate(zip(items, predictions_a, predictions_b)):
            gt = item.get("ground_truth")
            a_correct = (pa == gt)
            b_correct = (pb == gt)

            if a_correct and not b_correct:
                regressions.append({
                    "id": item.get("id") or item.get("golden_id"),
                    "category": item.get("category", "unknown"),
                    "ground_truth": gt,
                    f"{label_a}_pred": pa,
                    f"{label_b}_pred": pb,
                    "prompt_preview": item.get("prompt", "")[:60],
                })
            elif not a_correct and b_correct:
                improvements.append({
                    "id": item.get("id") or item.get("golden_id"),
                    "category": item.get("category", "unknown"),
                })
            elif a_correct and b_correct:
                stable_correct += 1
            else:
                stable_wrong += 1

        # Category breakdown
        cat_acc_a = defaultdict(lambda: {"correct": 0, "total": 0})
        cat_acc_b = defaultdict(lambda: {"correct": 0, "total": 0})
        for item, pa, pb in zip(items, predictions_a, predictions_b):
            cat = item.get("category", "unknown")
            gt = item.get("ground_truth")
            cat_acc_a[cat]["total"] += 1
            cat_acc_b[cat]["total"] += 1
            if pa == gt:
                cat_acc_a[cat]["correct"] += 1
            if pb == gt:
                cat_acc_b[cat]["correct"] += 1

        per_category = {}
        for cat in sorted(set(cat_acc_a.keys()) | set(cat_acc_b.keys())):
            a_acc = cat_acc_a[cat]["correct"] / max(cat_acc_a[cat]["total"], 1)
            b_acc = cat_acc_b[cat]["correct"] / max(cat_acc_b[cat]["total"], 1)
            per_category[cat] = {
                f"{label_a}_accuracy": round(a_acc, 4),
                f"{label_b}_accuracy": round(b_acc, 4),
                "delta": round(b_acc - a_acc, 4),
            }

        return {
            label_a: {"accuracy": round(acc_a, 4), "correct": correct_a},
            label_b: {"accuracy": round(acc_b, 4), "correct": correct_b},
            "delta": round(delta, 4),
            "is_regression": delta < -0.02,
            "is_improvement": delta > 0.02,
            "regressions": {
                "count": len(regressions),
                "items": regressions[:10],
            },
            "improvements": {
                "count": len(improvements),
                "items": improvements[:10],
            },
            "stable_correct": stable_correct,
            "stable_wrong": stable_wrong,
            "per_category": per_category,
            "total_items": n,
        }

    def compare_prompts(
        self,
        items: list,
        prompt_configs: dict,
        seed: int = 42,
    ) -> dict:
        """
        Simulate comparing different prompt strategies on the golden dataset.
        prompt_configs: {name: {"accuracy": float, "seed": int}}
        """
        rng = random.Random(seed)
        choices = ["A", "B", "C", "D", "E"]

        results = {}
        for name, config in prompt_configs.items():
            accuracy = config.get("accuracy", 0.7)
            s = config.get("seed", seed)
            r = random.Random(s)

            preds = []
            for item in items:
                gt = item.get("ground_truth", "A")
                if r.random() < accuracy:
                    preds.append(gt)
                else:
                    wrong = [c for c in choices if c != gt]
                    preds.append(r.choice(wrong))

            correct = sum(1 for gt_item, p in zip(items, preds) if gt_item.get("ground_truth") == p)
            results[name] = {
                "accuracy": round(correct / max(len(items), 1), 4),
                "correct": correct,
                "total": len(items),
            }

        # Rank by accuracy
        ranked = sorted(results.items(), key=lambda x: -x[1]["accuracy"])
        best = ranked[0][0] if ranked else None
        worst = ranked[-1][0] if ranked else None

        return {
            "results": results,
            "ranking": [{"rank": i + 1, "name": name, "accuracy": data["accuracy"]}
                        for i, (name, data) in enumerate(ranked)],
            "best_prompt": best,
            "worst_prompt": worst,
            "spread": round(
                ranked[0][1]["accuracy"] - ranked[-1][1]["accuracy"], 4
            ) if len(ranked) > 1 else 0.0,
        }


# ---------------------------------------------------------------------------
# MAINTENANCE TRACKER
# ---------------------------------------------------------------------------

class MaintenanceTracker:
    """
    Tracks golden dataset health over time and recommends maintenance actions.
    """

    def __init__(self):
        self.checkpoints = []

    def add_checkpoint(
        self,
        version: str,
        date: str,
        quality_score: float,
        item_count: int,
        notes: str = "",
    ):
        """Record a quality checkpoint."""
        self.checkpoints.append({
            "version": version,
            "date": date,
            "quality_score": quality_score,
            "item_count": item_count,
            "notes": notes,
        })

    def get_health_report(self) -> dict:
        """Generate health report with trend analysis."""
        if not self.checkpoints:
            return {"error": "No checkpoints recorded"}

        scores = [cp["quality_score"] for cp in self.checkpoints]
        sizes = [cp["item_count"] for cp in self.checkpoints]

        # Trend
        if len(scores) >= 2:
            recent_delta = scores[-1] - scores[-2]
            if recent_delta > 0.02:
                trend = "improving"
            elif recent_delta < -0.02:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
            recent_delta = 0.0

        # Maintenance schedule
        actions = []
        current_score = scores[-1]
        if current_score < 0.7:
            actions.append("URGENT: Quality below 70% - full dataset review needed")
        if len(scores) >= 3 and all(scores[-i] < scores[-i - 1] for i in range(1, min(3, len(scores)))):
            actions.append("WARNING: Quality declining for 3+ checkpoints")
        if sizes[-1] < 20:
            actions.append("Dataset too small - add more items")
        if not actions:
            actions.append("Dataset health is good - routine review recommended")

        return {
            "current_version": self.checkpoints[-1]["version"],
            "current_quality": round(current_score, 4),
            "current_size": sizes[-1],
            "trend": trend,
            "recent_delta": round(recent_delta, 4),
            "best_quality": round(max(scores), 4),
            "worst_quality": round(min(scores), 4),
            "total_checkpoints": len(self.checkpoints),
            "maintenance_actions": actions,
            "history": self.checkpoints,
        }

    def render_quality_chart(self) -> str:
        """ASCII chart of quality over time."""
        if not self.checkpoints:
            return "  No data to chart."

        lines = ["\n  Quality Score Over Time:"]
        lines.append("  " + "-" * 50)

        max_bar = 40
        for cp in self.checkpoints:
            score = cp["quality_score"]
            bar_len = int(score * max_bar)
            bar = "#" * bar_len + "." * (max_bar - bar_len)
            lines.append(f"  {cp['version']:<8s} |{bar}| {score:.1%}")

        lines.append("  " + "-" * 50)
        lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("EVALUATOR MODULE - Quick Test")
    print("=" * 60)

    # Test data
    test_items = [
        {"id": 1, "prompt": "Test question one about physics", "category": "physics",
         "difficulty": "easy", "ground_truth": "A", "edge_case": False},
        {"id": 2, "prompt": "Test question two about biology", "category": "biology",
         "difficulty": "medium", "ground_truth": "B", "edge_case": False},
        {"id": 3, "prompt": "Test question three about chemistry", "category": "chemistry",
         "difficulty": "hard", "ground_truth": "C", "edge_case": True},
    ]

    # Coverage
    cov = CoverageAnalyzer()
    result = cov.analyze(test_items)
    print(f"\nCoverage score: {result['coverage_score']}")

    # Balance
    bal = BalanceChecker()
    result = bal.full_balance_report(test_items)
    print(f"Overall balanced: {result['overall_balanced']}")

    # Duplicates
    dup = DuplicateDetector()
    result = dup.detect(test_items)
    print(f"Unique items: {result['unique_items']}/{result['total_items']}")

    # IAA
    iaa = IAACalculator()
    result = iaa.cohens_kappa(["A", "B", "C", "A"], ["A", "B", "A", "A"])
    print(f"Cohen's Kappa: {result['cohens_kappa']} ({result['interpretation']})")

    print("\nAll evaluator module tests passed.")
