"""
Chapter 7 - Evaluation Dataset Engineering
Evaluator module: Dataset quality evaluation implementations.

Classes:
  - BenchmarkDesigner       : Creates structured benchmarks from raw data
  - DatasetQualityChecker   : Runs quality checks on datasets
  - CoverageAnalyzer        : Measures topic/difficulty/format coverage
  - ContaminationDetector   : Checks for data leakage between splits
  - LabelNoiseDetector      : Finds potentially mislabeled examples
  - CohenKappaCalculator    : Computes Cohen's Kappa for two raters
  - FleissKappaCalculator   : Computes Fleiss' Kappa for multiple raters
  - MetaEvaluator           : Evaluates the evaluation dataset quality
"""

import math
import random
from collections import Counter
from typing import Optional


# ===========================================================================
# 1. BENCHMARK DESIGNER
# ===========================================================================

class BenchmarkDesigner:
    """
    Creates structured benchmarks from raw question data.

    A benchmark is not just a collection of questions - it is a carefully
    designed evaluation instrument with defined:
      - Scope (what it measures)
      - Structure (how questions are organized)
      - Balance (fair representation across categories)
      - Difficulty gradient (easy -> hard progression)

    Analogy: Think of a benchmark like designing a school exam.
    You would not put 50 easy questions and 0 hard ones.
    You would not test only one topic out of ten.
    A good exam covers the syllabus fairly.
    """

    def __init__(self, questions: list[dict], topic_fn=None, difficulty_fn=None):
        self.questions = questions
        self.topic_fn = topic_fn
        self.difficulty_fn = difficulty_fn

    def design_benchmark(
        self,
        target_size: int = 50,
        topics: Optional[list[str]] = None,
        difficulty_distribution: Optional[dict] = None,
        seed: int = 42,
    ) -> dict:
        """
        Design a balanced benchmark from available questions.

        Args:
            target_size: desired number of questions
            topics: list of topics to include (None = all)
            difficulty_distribution: e.g. {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            seed: random seed for reproducibility

        Returns:
            dict with selected questions and design metadata
        """
        rng = random.Random(seed)

        # Classify questions by topic and difficulty
        classified = []
        for q in self.questions:
            topic = self.topic_fn(q["prompt"]) if self.topic_fn else "general"
            difficulty = self.difficulty_fn(q) if self.difficulty_fn else "medium"
            classified.append({**q, "_topic": topic, "_difficulty": difficulty})

        # Filter by requested topics
        if topics:
            classified = [q for q in classified if q["_topic"] in topics]

        if not classified:
            return {"questions": [], "metadata": {"error": "No matching questions"}}

        # Default difficulty distribution
        if not difficulty_distribution:
            difficulty_distribution = {"easy": 0.33, "medium": 0.34, "hard": 0.33}

        # Group by difficulty
        by_difficulty = {}
        for q in classified:
            diff = q["_difficulty"]
            by_difficulty.setdefault(diff, []).append(q)

        # Select questions maintaining difficulty balance
        selected = []
        for diff_level, fraction in difficulty_distribution.items():
            n_wanted = max(1, int(target_size * fraction))
            pool = by_difficulty.get(diff_level, [])
            if pool:
                rng.shuffle(pool)
                selected.extend(pool[:n_wanted])

        # If we have fewer than target, fill from remaining
        selected_ids = {q["id"] for q in selected}
        remaining = [q for q in classified if q["id"] not in selected_ids]
        rng.shuffle(remaining)
        while len(selected) < target_size and remaining:
            selected.append(remaining.pop())

        # Trim to target size
        selected = selected[:target_size]

        # Compute design statistics
        topic_counts = Counter(q["_topic"] for q in selected)
        diff_counts = Counter(q["_difficulty"] for q in selected)
        answer_counts = Counter(q["ground_truth"] for q in selected)

        return {
            "questions": selected,
            "metadata": {
                "total_selected": len(selected),
                "total_available": len(self.questions),
                "topic_distribution": dict(topic_counts),
                "difficulty_distribution": dict(diff_counts),
                "answer_distribution": dict(answer_counts),
                "design_principles": [
                    "Balanced across difficulty levels",
                    "Representative of available topics",
                    "Answer distribution checked for bias",
                    "Reproducible via seed parameter",
                ],
            },
        }

    def validate_benchmark(self, benchmark: dict) -> dict:
        """Validate a designed benchmark for common issues."""
        questions = benchmark.get("questions", [])
        issues = []

        if len(questions) < 10:
            issues.append("WARNING: Benchmark has fewer than 10 questions - "
                          "may not be statistically meaningful")

        # Check answer balance
        answers = Counter(q["ground_truth"] for q in questions)
        total = len(questions)
        if total > 0:
            expected = total / max(len(answers), 1)
            for ans, count in answers.items():
                if count > expected * 2:
                    issues.append(
                        f"IMBALANCE: Answer '{ans}' appears {count} times "
                        f"(expected ~{expected:.0f})"
                    )

        # Check for duplicates
        prompts = [q["prompt"].lower().strip() for q in questions]
        seen = set()
        for i, p in enumerate(prompts):
            if p in seen:
                issues.append(f"DUPLICATE: Question {i} is an exact duplicate")
            seen.add(p)

        # Check for empty prompts
        for q in questions:
            if not q.get("prompt", "").strip():
                issues.append(f"EMPTY: Question {q.get('id', '?')} has no prompt")

        return {
            "is_valid": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues,
        }


# ===========================================================================
# 2. DATASET QUALITY CHECKER
# ===========================================================================

class DatasetQualityChecker:
    """
    Runs comprehensive quality checks on evaluation datasets.

    Quality dimensions:
      - Completeness: Are all required fields present?
      - Correctness: Are labels valid? Are prompts well-formed?
      - Consistency: Are formats uniform? Are labels from the right set?
      - Uniqueness: Are there duplicates?

    Analogy: This is like a factory quality inspector checking products
    on an assembly line. Each product must meet certain standards
    before it ships.
    """

    def __init__(self, questions: list[dict]):
        self.questions = questions
        self.required_fields = ["id", "prompt", "ground_truth"]
        self.valid_answers = {"A", "B", "C", "D", "E"}

    def check_completeness(self) -> dict:
        """Check that all required fields are present and non-empty."""
        issues = []
        for q in self.questions:
            for field in self.required_fields:
                if field not in q:
                    issues.append({
                        "id": q.get("id", "unknown"),
                        "issue": f"Missing field: {field}",
                        "severity": "critical",
                    })
                elif not str(q[field]).strip():
                    issues.append({
                        "id": q.get("id", "unknown"),
                        "issue": f"Empty field: {field}",
                        "severity": "critical",
                    })

            # Check choices completeness
            choices = q.get("choices", {})
            for option in ["A", "B", "C", "D", "E"]:
                if option not in choices:
                    issues.append({
                        "id": q.get("id", "unknown"),
                        "issue": f"Missing choice: {option}",
                        "severity": "high",
                    })

        completeness_score = 1.0 - (len(issues) / max(
            len(self.questions) * (len(self.required_fields) + 5), 1
        ))

        return {
            "total_checked": len(self.questions),
            "issues_found": len(issues),
            "completeness_score": round(max(0, completeness_score), 4),
            "issues": issues,
        }

    def check_correctness(self) -> dict:
        """Check that labels are valid and internally consistent."""
        issues = []
        for q in self.questions:
            # Check answer is in valid set
            answer = q.get("ground_truth", "")
            if answer not in self.valid_answers:
                issues.append({
                    "id": q.get("id", "unknown"),
                    "issue": f"Invalid answer label: '{answer}' "
                             f"(expected one of {self.valid_answers})",
                    "severity": "critical",
                })

            # Check answer option exists in choices
            choices = q.get("choices", {})
            if answer in self.valid_answers and answer not in choices:
                issues.append({
                    "id": q.get("id", "unknown"),
                    "issue": f"Answer '{answer}' has no corresponding choice",
                    "severity": "critical",
                })

            # Check prompt is a question (heuristic)
            prompt = q.get("prompt", "")
            if prompt and not any(
                prompt.strip().endswith(c) for c in ["?", ".", ":", ";"]
            ):
                issues.append({
                    "id": q.get("id", "unknown"),
                    "issue": "Prompt does not end with expected punctuation",
                    "severity": "low",
                })

        return {
            "total_checked": len(self.questions),
            "issues_found": len(issues),
            "issues": issues,
        }

    def check_consistency(self) -> dict:
        """Check format consistency across the dataset."""
        issues = []
        prompt_lengths = [len(q.get("prompt", "").split()) for q in self.questions]

        if prompt_lengths:
            mean_len = sum(prompt_lengths) / len(prompt_lengths)
            std_len = math.sqrt(
                sum((x - mean_len) ** 2 for x in prompt_lengths)
                / len(prompt_lengths)
            )

            # Flag outliers (more than 3 std from mean)
            for i, q in enumerate(self.questions):
                plen = prompt_lengths[i]
                if std_len > 0 and abs(plen - mean_len) > 3 * std_len:
                    issues.append({
                        "id": q.get("id", "unknown"),
                        "issue": f"Prompt length outlier: {plen} words "
                                 f"(mean={mean_len:.0f}, std={std_len:.0f})",
                        "severity": "medium",
                    })

        # Check number of choices is consistent
        choice_counts = Counter(
            len(q.get("choices", {})) for q in self.questions
        )
        if len(choice_counts) > 1:
            issues.append({
                "id": "dataset",
                "issue": f"Inconsistent number of choices: {dict(choice_counts)}",
                "severity": "high",
            })

        return {
            "total_checked": len(self.questions),
            "issues_found": len(issues),
            "prompt_length_stats": {
                "mean": round(sum(prompt_lengths) / max(len(prompt_lengths), 1), 2),
                "min": min(prompt_lengths) if prompt_lengths else 0,
                "max": max(prompt_lengths) if prompt_lengths else 0,
            },
            "issues": issues,
        }

    def run_all_checks(self) -> dict:
        """Run all quality checks and return a comprehensive report."""
        completeness = self.check_completeness()
        correctness = self.check_correctness()
        consistency = self.check_consistency()

        total_issues = (
            completeness["issues_found"]
            + correctness["issues_found"]
            + consistency["issues_found"]
        )

        # Overall quality score (simple weighted average)
        max_possible_issues = len(self.questions) * 10  # rough upper bound
        quality_score = max(0, 1.0 - total_issues / max(max_possible_issues, 1))

        return {
            "overall_quality_score": round(quality_score, 4),
            "total_issues": total_issues,
            "completeness": completeness,
            "correctness": correctness,
            "consistency": consistency,
            "grade": (
                "A" if quality_score >= 0.95 else
                "B" if quality_score >= 0.85 else
                "C" if quality_score >= 0.70 else
                "D" if quality_score >= 0.50 else "F"
            ),
        }


# ===========================================================================
# 3. COVERAGE ANALYZER
# ===========================================================================

class CoverageAnalyzer:
    """
    Measures how well an evaluation dataset covers the intended
    evaluation space along multiple dimensions:
      - Topic coverage
      - Difficulty coverage
      - Format coverage
      - Answer distribution coverage

    Analogy: Imagine you are testing a car. You would not just
    test it on a highway. You need city roads, hills, rain,
    night driving, etc. Coverage ensures your test suite
    exercises all important dimensions.
    """

    def __init__(self, questions: list[dict], topic_fn=None, difficulty_fn=None):
        self.questions = questions
        self.topic_fn = topic_fn
        self.difficulty_fn = difficulty_fn

    def topic_coverage(self, expected_topics: Optional[list[str]] = None) -> dict:
        """Measure how many expected topics are represented."""
        detected = [
            self.topic_fn(q["prompt"]) if self.topic_fn else "general"
            for q in self.questions
        ]
        topic_counts = Counter(detected)

        if expected_topics is None:
            expected_topics = list(topic_counts.keys())

        covered = [t for t in expected_topics if topic_counts.get(t, 0) > 0]
        missing = [t for t in expected_topics if topic_counts.get(t, 0) == 0]

        coverage_ratio = len(covered) / max(len(expected_topics), 1)

        # Entropy-based coverage (higher = more uniform distribution)
        total = sum(topic_counts.values())
        entropy = 0.0
        for count in topic_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        max_entropy = math.log2(max(len(topic_counts), 1))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        return {
            "coverage_ratio": round(coverage_ratio, 4),
            "covered_topics": covered,
            "missing_topics": missing,
            "topic_counts": dict(topic_counts),
            "entropy": round(entropy, 4),
            "normalized_entropy": round(normalized_entropy, 4),
            "interpretation": (
                "Excellent" if normalized_entropy > 0.9 else
                "Good" if normalized_entropy > 0.7 else
                "Fair" if normalized_entropy > 0.5 else
                "Poor - topics are heavily imbalanced"
            ),
        }

    def difficulty_coverage(self) -> dict:
        """Measure coverage across difficulty levels."""
        difficulties = [
            self.difficulty_fn(q) if self.difficulty_fn else "medium"
            for q in self.questions
        ]
        counts = Counter(difficulties)
        total = len(difficulties)

        expected_levels = ["easy", "medium", "hard"]
        coverage = {}
        for level in expected_levels:
            count = counts.get(level, 0)
            coverage[level] = {
                "count": count,
                "percentage": round(count / max(total, 1) * 100, 2),
            }

        covered = sum(1 for level in expected_levels if counts.get(level, 0) > 0)
        return {
            "coverage_ratio": round(covered / len(expected_levels), 4),
            "distribution": coverage,
            "total": total,
        }

    def answer_coverage(self) -> dict:
        """Check if answers are distributed across all options."""
        answers = Counter(q["ground_truth"] for q in self.questions)
        expected = {"A", "B", "C", "D", "E"}
        covered = expected & set(answers.keys())
        missing = expected - set(answers.keys())

        total = sum(answers.values())
        balance_score = 0.0
        if total > 0 and len(answers) > 0:
            expected_count = total / len(expected)
            deviations = [
                abs(answers.get(a, 0) - expected_count) for a in expected
            ]
            max_deviation = max(deviations)
            balance_score = 1.0 - (max_deviation / max(total, 1))

        return {
            "coverage_ratio": round(len(covered) / len(expected), 4),
            "covered": sorted(covered),
            "missing": sorted(missing),
            "counts": dict(answers),
            "balance_score": round(max(0, balance_score), 4),
        }

    def overall_coverage(self, expected_topics: Optional[list[str]] = None) -> dict:
        """Compute an overall coverage report."""
        topic = self.topic_coverage(expected_topics)
        difficulty = self.difficulty_coverage()
        answer = self.answer_coverage()

        # Weighted average of coverage scores
        overall = (
            topic["coverage_ratio"] * 0.4
            + difficulty["coverage_ratio"] * 0.3
            + answer["coverage_ratio"] * 0.3
        )

        return {
            "overall_coverage_score": round(overall, 4),
            "topic_coverage": topic,
            "difficulty_coverage": difficulty,
            "answer_coverage": answer,
        }


# ===========================================================================
# 4. CONTAMINATION DETECTOR
# ===========================================================================

class ContaminationDetector:
    """
    Detects data contamination (leakage) between datasets.

    Data contamination occurs when test data appears in training data,
    inflating evaluation scores and giving a false sense of model quality.

    Types of contamination:
      1. Exact match: Same question appears in both train and test
      2. Near-duplicate: Rephrased version of the same question
      3. Answer leakage: Test answers visible during training
      4. Indirect leakage: Training on the source material of test questions

    Analogy: Imagine a student who gets the exam paper before the test.
    Their high score does not reflect true knowledge - it reflects
    memorization of leaked answers. Contamination detection is like
    checking if any students had advance access to the exam.
    """

    def __init__(self, train_data: list[dict], test_data: list[dict]):
        self.train_data = train_data
        self.test_data = test_data

    def _tokenize(self, text: str) -> set:
        """Simple word-level tokenization."""
        return set(text.lower().strip().split())

    def _jaccard_similarity(self, set_a: set, set_b: set) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0

    def _ngram_overlap(self, text_a: str, text_b: str, n: int = 3) -> float:
        """Compute n-gram overlap between two texts."""
        words_a = text_a.lower().split()
        words_b = text_b.lower().split()

        if len(words_a) < n or len(words_b) < n:
            return 0.0

        ngrams_a = set(
            tuple(words_a[i:i+n]) for i in range(len(words_a) - n + 1)
        )
        ngrams_b = set(
            tuple(words_b[i:i+n]) for i in range(len(words_b) - n + 1)
        )

        if not ngrams_a or not ngrams_b:
            return 0.0

        overlap = len(ngrams_a & ngrams_b)
        return overlap / min(len(ngrams_a), len(ngrams_b))

    def detect_exact_matches(self) -> list[dict]:
        """Find exact duplicate questions between train and test sets."""
        train_prompts = {
            q["prompt"].lower().strip(): q for q in self.train_data
        }
        matches = []
        for test_q in self.test_data:
            test_prompt = test_q["prompt"].lower().strip()
            if test_prompt in train_prompts:
                train_q = train_prompts[test_prompt]
                matches.append({
                    "test_id": test_q.get("id", "?"),
                    "train_id": train_q.get("id", "?"),
                    "prompt": test_prompt[:100] + "...",
                    "match_type": "exact",
                    "severity": "critical",
                })
        return matches

    def detect_near_duplicates(self, threshold: float = 0.7) -> list[dict]:
        """Find near-duplicate questions using Jaccard and n-gram overlap."""
        matches = []
        for test_q in self.test_data:
            test_tokens = self._tokenize(test_q["prompt"])
            test_prompt = test_q["prompt"]

            for train_q in self.train_data:
                train_tokens = self._tokenize(train_q["prompt"])
                train_prompt = train_q["prompt"]

                jaccard = self._jaccard_similarity(test_tokens, train_tokens)
                ngram = self._ngram_overlap(test_prompt, train_prompt)

                # Combined score
                combined = 0.5 * jaccard + 0.5 * ngram

                if combined >= threshold:
                    matches.append({
                        "test_id": test_q.get("id", "?"),
                        "train_id": train_q.get("id", "?"),
                        "jaccard_similarity": round(jaccard, 4),
                        "ngram_overlap": round(ngram, 4),
                        "combined_score": round(combined, 4),
                        "match_type": "near_duplicate",
                        "severity": "high",
                        "test_prompt": test_prompt[:80] + "...",
                        "train_prompt": train_prompt[:80] + "...",
                    })
        return matches

    def detect_answer_leakage(self) -> dict:
        """
        Check if test set answers can be inferred from training data patterns.
        Simulates a simple heuristic: if the answer distribution in training
        data strongly predicts test answers, there may be leakage.
        """
        train_answers = Counter(q["ground_truth"] for q in self.train_data)
        test_answers = Counter(
            q.get("ground_truth", "?") for q in self.test_data
            if "ground_truth" in q
        )

        # Check if distributions are suspiciously similar
        if not train_answers or not test_answers:
            return {"leakage_detected": False, "reason": "Insufficient data"}

        all_labels = sorted(
            set(train_answers.keys()) | set(test_answers.keys())
        )
        train_total = sum(train_answers.values())
        test_total = sum(test_answers.values())

        correlation_pairs = []
        for label in all_labels:
            train_pct = train_answers.get(label, 0) / max(train_total, 1)
            test_pct = test_answers.get(label, 0) / max(test_total, 1)
            correlation_pairs.append((train_pct, test_pct))

        return {
            "train_distribution": {
                k: round(v / train_total, 4) for k, v in train_answers.items()
            },
            "test_distribution": {
                k: round(v / test_total, 4) for k, v in test_answers.items()
            },
            "analysis": "Compare distributions - identical distributions may "
                        "indicate systematic leakage",
        }

    def full_contamination_report(self, near_dup_threshold: float = 0.7) -> dict:
        """Run all contamination checks."""
        exact = self.detect_exact_matches()
        near = self.detect_near_duplicates(near_dup_threshold)
        leakage = self.detect_answer_leakage()

        total_issues = len(exact) + len(near)
        contamination_rate = total_issues / max(len(self.test_data), 1)

        return {
            "contamination_rate": round(contamination_rate, 4),
            "total_contaminated": total_issues,
            "exact_matches": exact,
            "near_duplicates": near,
            "answer_leakage_analysis": leakage,
            "risk_level": (
                "CRITICAL" if contamination_rate > 0.1 else
                "HIGH" if contamination_rate > 0.05 else
                "MEDIUM" if contamination_rate > 0.01 else
                "LOW"
            ),
        }


# ===========================================================================
# 5. LABEL NOISE DETECTOR
# ===========================================================================

class LabelNoiseDetector:
    """
    Detects potentially mislabeled examples in an evaluation dataset.

    Label noise = incorrect ground truth labels. Even a small amount
    of label noise (5-10%) can significantly distort evaluation results.

    Detection methods:
      1. Annotator disagreement: If annotators disagree, the label may be wrong
      2. Confidence-based: If models consistently predict a different answer
      3. Consistency checks: If the label contradicts the question semantics

    Analogy: In a classroom test, if the answer key says 2+2=5,
    every student who correctly answers 4 gets marked wrong.
    Label noise is the equivalent of errors in the answer key.
    """

    def __init__(self, questions: list[dict]):
        self.questions = questions

    def detect_by_annotator_disagreement(
        self,
        annotations: list[list[str]],
        disagreement_threshold: float = 0.5,
    ) -> list[dict]:
        """
        Find questions where annotators disagree significantly.

        Args:
            annotations: list of lists, where annotations[i] has labels
                         from multiple annotators for question i
            disagreement_threshold: fraction of annotators that must disagree
        """
        suspicious = []
        for i, (q, labels) in enumerate(zip(self.questions, annotations)):
            if not labels:
                continue
            label_counts = Counter(labels)
            majority_label, majority_count = label_counts.most_common(1)[0]
            agreement_rate = majority_count / len(labels)

            if agreement_rate < (1.0 - disagreement_threshold):
                continue  # not enough disagreement

            # Check if ground truth matches majority vote
            ground_truth = q.get("ground_truth", "")
            if ground_truth != majority_label:
                suspicious.append({
                    "id": q.get("id", i),
                    "ground_truth": ground_truth,
                    "majority_vote": majority_label,
                    "label_distribution": dict(label_counts),
                    "agreement_rate": round(agreement_rate, 4),
                    "issue": "Ground truth differs from majority annotator vote",
                    "confidence": round(agreement_rate, 4),
                })

        return suspicious

    def detect_by_model_consensus(
        self,
        model_predictions: list[list[str]],
        consensus_threshold: float = 0.8,
    ) -> list[dict]:
        """
        Find questions where multiple models agree on a different answer
        than the ground truth.

        Args:
            model_predictions: list of prediction lists from different models
                               model_predictions[i] is the i-th model's full predictions
            consensus_threshold: fraction of models that must agree
        """
        n_models = len(model_predictions)
        if n_models == 0:
            return []

        suspicious = []
        for q_idx, q in enumerate(self.questions):
            # Collect all model predictions for this question
            preds_for_q = []
            for model_preds in model_predictions:
                if q_idx < len(model_preds):
                    preds_for_q.append(model_preds[q_idx])

            if not preds_for_q:
                continue

            pred_counts = Counter(preds_for_q)
            most_common_pred, count = pred_counts.most_common(1)[0]
            consensus_rate = count / len(preds_for_q)

            ground_truth = q.get("ground_truth", "")
            if consensus_rate >= consensus_threshold and most_common_pred != ground_truth:
                suspicious.append({
                    "id": q.get("id", q_idx),
                    "ground_truth": ground_truth,
                    "model_consensus": most_common_pred,
                    "consensus_rate": round(consensus_rate, 4),
                    "model_votes": dict(pred_counts),
                    "issue": "Multiple models agree on a different answer",
                })

        return suspicious

    def estimate_noise_rate(self, annotations: list[list[str]]) -> dict:
        """Estimate the overall label noise rate in the dataset."""
        mismatches = 0
        total = 0

        for q, labels in zip(self.questions, annotations):
            if not labels:
                continue
            total += 1
            majority = Counter(labels).most_common(1)[0][0]
            if q.get("ground_truth", "") != majority:
                mismatches += 1

        noise_rate = mismatches / max(total, 1)
        return {
            "estimated_noise_rate": round(noise_rate, 4),
            "noisy_labels": mismatches,
            "total_checked": total,
            "interpretation": (
                "Clean dataset" if noise_rate < 0.02 else
                "Acceptable noise" if noise_rate < 0.05 else
                "Moderate noise - review recommended" if noise_rate < 0.10 else
                "High noise - significant label issues"
            ),
        }


# ===========================================================================
# 6. COHEN'S KAPPA CALCULATOR
# ===========================================================================

class CohenKappaCalculator:
    """
    Computes Cohen's Kappa - a measure of inter-rater agreement for TWO raters.

    Formula:
        kappa = (P_o - P_e) / (1 - P_e)

    Where:
        P_o = observed agreement (fraction of items where raters agree)
        P_e = expected agreement by chance

    Interpretation:
        kappa < 0.00  : Less than chance agreement
        0.00 - 0.20   : Slight agreement
        0.21 - 0.40   : Fair agreement
        0.41 - 0.60   : Moderate agreement
        0.61 - 0.80   : Substantial agreement
        0.81 - 1.00   : Almost perfect agreement

    Analogy: Imagine two teachers grading the same essays.
    If they agree 80% of the time, that sounds good. But what
    if there are only 2 possible grades (pass/fail) and 90%
    of students pass? Then even random grading would agree
    ~82% of the time! Cohen's Kappa accounts for this chance
    agreement, giving you the TRUE agreement beyond random.
    """

    @staticmethod
    def compute(rater_1: list[str], rater_2: list[str]) -> dict:
        """
        Compute Cohen's Kappa for two raters.

        Args:
            rater_1: list of labels from rater 1
            rater_2: list of labels from rater 2

        Returns:
            dict with kappa value, observed/expected agreement, interpretation
        """
        if len(rater_1) != len(rater_2):
            raise ValueError("Both raters must label the same number of items")

        n = len(rater_1)
        if n == 0:
            return {"kappa": 0.0, "error": "No items to compare"}

        categories = sorted(set(rater_1) | set(rater_2))

        # Step 1: Build confusion matrix
        matrix = {c1: {c2: 0 for c2 in categories} for c1 in categories}
        for r1, r2 in zip(rater_1, rater_2):
            matrix[r1][r2] += 1

        # Step 2: Compute observed agreement P_o
        observed_agreement = sum(matrix[c][c] for c in categories) / n

        # Step 3: Compute expected agreement P_e
        #   P_e = sum over categories of (p_rater1_c * p_rater2_c)
        expected_agreement = 0.0
        for c in categories:
            # Proportion of items rater 1 assigned to category c
            p1_c = sum(matrix[c][c2] for c2 in categories) / n
            # Proportion of items rater 2 assigned to category c
            p2_c = sum(matrix[c1][c] for c1 in categories) / n
            expected_agreement += p1_c * p2_c

        # Step 4: Compute kappa
        if expected_agreement == 1.0:
            kappa = 1.0  # Perfect agreement
        else:
            kappa = (observed_agreement - expected_agreement) / (
                1.0 - expected_agreement
            )

        return {
            "kappa": round(kappa, 4),
            "observed_agreement": round(observed_agreement, 4),
            "expected_agreement": round(expected_agreement, 4),
            "n_items": n,
            "n_categories": len(categories),
            "categories": categories,
            "interpretation": CohenKappaCalculator._interpret(kappa),
            "confusion_matrix": matrix,
        }

    @staticmethod
    def _interpret(kappa: float) -> str:
        if kappa < 0:
            return "Less than chance agreement"
        elif kappa < 0.21:
            return "Slight agreement"
        elif kappa < 0.41:
            return "Fair agreement"
        elif kappa < 0.61:
            return "Moderate agreement"
        elif kappa < 0.81:
            return "Substantial agreement"
        else:
            return "Almost perfect agreement"


# ===========================================================================
# 7. FLEISS' KAPPA CALCULATOR
# ===========================================================================

class FleissKappaCalculator:
    """
    Computes Fleiss' Kappa - a measure of inter-rater agreement for
    MULTIPLE raters (generalizes Cohen's Kappa beyond 2 raters).

    Formula:
        kappa = (P_bar - P_e_bar) / (1 - P_e_bar)

    Where:
        P_bar   = mean of per-item agreement proportions
        P_e_bar = expected agreement by chance

    For each item i with n raters and k categories:
        P_i = (1 / (n*(n-1))) * (sum_j(n_ij^2) - n)

    Where n_ij = number of raters who assigned item i to category j.

    Analogy: You have 5 people taste-testing 10 dishes, each rating
    them "good", "okay", or "bad". Fleiss' Kappa tells you whether
    the tasters genuinely agree or if their agreement is just what
    you would expect from random ratings.
    """

    @staticmethod
    def compute(annotations: list[list[str]], categories: Optional[list[str]] = None) -> dict:
        """
        Compute Fleiss' Kappa.

        Args:
            annotations: list of lists where annotations[i] has the labels
                         from all raters for item i.
                         All items must have the same number of raters.
            categories: list of possible categories (auto-detected if None)

        Returns:
            dict with kappa, observed/expected agreement, interpretation
        """
        if not annotations:
            return {"kappa": 0.0, "error": "No annotations provided"}

        n_raters = len(annotations[0])
        n_items = len(annotations)

        # Auto-detect categories
        if categories is None:
            categories = sorted(set(
                label for item_labels in annotations for label in item_labels
            ))

        k = len(categories)
        cat_index = {c: j for j, c in enumerate(categories)}

        # Step 1: Build the count matrix
        # n_ij = number of raters who assigned item i to category j
        count_matrix = []
        for item_labels in annotations:
            counts = [0] * k
            for label in item_labels:
                if label in cat_index:
                    counts[cat_index[label]] += 1
            count_matrix.append(counts)

        # Step 2: Compute P_i for each item
        #   P_i = (1 / (n*(n-1))) * (sum_j(n_ij^2) - n)
        p_items = []
        for counts in count_matrix:
            sum_sq = sum(c * c for c in counts)
            p_i = (sum_sq - n_raters) / (n_raters * (n_raters - 1)) if n_raters > 1 else 0
            p_items.append(p_i)

        # Step 3: Compute P_bar (mean of P_i)
        p_bar = sum(p_items) / max(n_items, 1)

        # Step 4: Compute p_j (proportion of all assignments to category j)
        #   p_j = (1 / (N*n)) * sum_i(n_ij)
        total_assignments = n_items * n_raters
        p_j = []
        for j in range(k):
            col_sum = sum(count_matrix[i][j] for i in range(n_items))
            p_j.append(col_sum / max(total_assignments, 1))

        # Step 5: Compute P_e_bar (expected agreement)
        #   P_e_bar = sum_j(p_j^2)
        p_e_bar = sum(p ** 2 for p in p_j)

        # Step 6: Compute Fleiss' Kappa
        if p_e_bar == 1.0:
            kappa = 1.0
        else:
            kappa = (p_bar - p_e_bar) / (1.0 - p_e_bar)

        return {
            "kappa": round(kappa, 4),
            "p_bar": round(p_bar, 4),
            "p_e_bar": round(p_e_bar, 4),
            "n_items": n_items,
            "n_raters": n_raters,
            "n_categories": k,
            "categories": categories,
            "category_proportions": {
                categories[j]: round(p_j[j], 4) for j in range(k)
            },
            "interpretation": FleissKappaCalculator._interpret(kappa),
        }

    @staticmethod
    def _interpret(kappa: float) -> str:
        if kappa < 0:
            return "Less than chance agreement"
        elif kappa < 0.21:
            return "Slight agreement"
        elif kappa < 0.41:
            return "Fair agreement"
        elif kappa < 0.61:
            return "Moderate agreement"
        elif kappa < 0.81:
            return "Substantial agreement"
        else:
            return "Almost perfect agreement"


# ===========================================================================
# 8. META-EVALUATOR
# ===========================================================================

class MetaEvaluator:
    """
    Evaluates the evaluation dataset itself — meta-evaluation.

    The central question: "Is our evaluation dataset good enough
    to reliably evaluate models?"

    A bad evaluation dataset leads to wrong conclusions about
    model quality, which leads to bad deployment decisions.

    This class aggregates results from all other checkers into
    a single quality scorecard.

    Analogy: Before you use a ruler to measure a table, you
    should check if the ruler itself is accurate. Meta-evaluation
    is checking the ruler before measuring.
    """

    def __init__(
        self,
        quality_checker: DatasetQualityChecker,
        coverage_analyzer: CoverageAnalyzer,
        label_noise_detector: Optional[LabelNoiseDetector] = None,
    ):
        self.quality_checker = quality_checker
        self.coverage_analyzer = coverage_analyzer
        self.label_noise_detector = label_noise_detector

    def evaluate(
        self,
        annotations: Optional[list[list[str]]] = None,
        expected_topics: Optional[list[str]] = None,
    ) -> dict:
        """Run full meta-evaluation and produce a scorecard."""

        # 1. Quality checks
        quality = self.quality_checker.run_all_checks()

        # 2. Coverage analysis
        coverage = self.coverage_analyzer.overall_coverage(expected_topics)

        # 3. Label noise (if annotations provided)
        noise_report = None
        if self.label_noise_detector and annotations:
            noise_report = self.label_noise_detector.estimate_noise_rate(annotations)

        # 4. Compute dimension scores
        dimensions = {
            "quality": {
                "score": quality["overall_quality_score"],
                "grade": quality["grade"],
                "issues": quality["total_issues"],
            },
            "coverage": {
                "score": coverage["overall_coverage_score"],
                "topic_coverage": coverage["topic_coverage"]["coverage_ratio"],
                "difficulty_coverage": coverage["difficulty_coverage"]["coverage_ratio"],
                "answer_coverage": coverage["answer_coverage"]["coverage_ratio"],
            },
        }

        if noise_report:
            noise_score = max(0, 1.0 - noise_report["estimated_noise_rate"] * 5)
            dimensions["label_quality"] = {
                "score": round(noise_score, 4),
                "noise_rate": noise_report["estimated_noise_rate"],
                "interpretation": noise_report["interpretation"],
            }

        # 5. Overall meta-evaluation score
        scores = [d["score"] for d in dimensions.values()]
        overall_score = sum(scores) / len(scores)

        # 6. Recommendations
        recommendations = []
        if quality["overall_quality_score"] < 0.9:
            recommendations.append(
                "Fix data quality issues (missing fields, invalid labels)"
            )
        if coverage["overall_coverage_score"] < 0.7:
            recommendations.append(
                "Improve coverage - add questions from underrepresented topics/difficulties"
            )
        if noise_report and noise_report["estimated_noise_rate"] > 0.05:
            recommendations.append(
                "Review and correct potentially mislabeled examples"
            )
        if not recommendations:
            recommendations.append(
                "Dataset meets quality standards for reliable evaluation"
            )

        return {
            "overall_score": round(overall_score, 4),
            "overall_grade": (
                "A" if overall_score >= 0.90 else
                "B" if overall_score >= 0.80 else
                "C" if overall_score >= 0.65 else
                "D" if overall_score >= 0.50 else "F"
            ),
            "dimensions": dimensions,
            "recommendations": recommendations,
            "quality_detail": quality,
            "coverage_detail": coverage,
            "noise_detail": noise_report,
        }

    def evaluator_reliability_check(
        self,
        questions: list[dict],
        evaluator_fn,
        n_runs: int = 5,
        seed_start: int = 0,
    ) -> dict:
        """
        Check if the evaluator produces consistent results.

        The 'evaluating the evaluator' problem: if your evaluation
        method gives different results each time, it is unreliable.

        Args:
            questions: test questions
            evaluator_fn: function(questions, seed) -> score
            n_runs: number of evaluation runs
            seed_start: starting seed for reproducibility
        """
        scores = []
        for i in range(n_runs):
            score = evaluator_fn(questions, seed_start + i)
            scores.append(round(score, 4))

        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)

        # Coefficient of variation (lower = more reliable)
        cv = std_dev / mean_score if mean_score != 0 else float("inf")

        return {
            "scores": scores,
            "mean": round(mean_score, 4),
            "std_dev": round(std_dev, 4),
            "coefficient_of_variation": round(cv, 4),
            "is_reliable": cv < 0.1,
            "interpretation": (
                "Highly reliable" if cv < 0.05 else
                "Reliable" if cv < 0.10 else
                "Moderately reliable" if cv < 0.20 else
                "Unreliable - high variance across runs"
            ),
        }
