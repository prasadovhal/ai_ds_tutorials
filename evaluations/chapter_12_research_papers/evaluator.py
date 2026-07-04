"""
evaluator.py - Simplified implementations of key paper techniques for LLM evaluation.
All implementations use only the Python standard library.
"""

import math
import random
import re
from collections import defaultdict


# =============================================================================
# 1. MTBenchEvaluator - Multi-turn evaluation (Zheng et al., 2023)
# =============================================================================
class MTBenchEvaluator:
    """Simplified MT-Bench: scores multi-turn conversations on depth and consistency."""

    DEPTH_KEYWORDS = {
        "high": ["algorithm", "complexity", "O(", "trade-off", "specifically",
                 "example", "e.g.", "however", "because", "therefore"],
        "low": ["basically", "simple", "just", "very", "really"]
    }

    def score_response(self, response_text):
        """Score a single response 1-10 based on heuristics (length, depth, specificity)."""
        words = response_text.split()
        word_count = len(words)

        # Length component (0-3 pts)
        length_score = min(3, word_count / 30)

        # Depth keywords (0-4 pts)
        text_lower = response_text.lower()
        high_hits = sum(1 for kw in self.DEPTH_KEYWORDS["high"] if kw.lower() in text_lower)
        low_hits = sum(1 for kw in self.DEPTH_KEYWORDS["low"] if kw.lower() in text_lower)
        depth_score = min(4, high_hits) - min(2, low_hits)
        depth_score = max(0, depth_score)

        # Specificity: presence of numbers, code, or formulas (0-3 pts)
        has_numbers = len(re.findall(r'\d+', response_text))
        has_code = '(' in response_text and ')' in response_text
        spec_score = min(3, has_numbers * 0.5 + (1.5 if has_code else 0))

        total = length_score + depth_score + spec_score
        return round(max(1, min(10, total)), 1)

    def evaluate_conversation(self, conversation):
        """Score a multi-turn MT-Bench conversation, returning per-turn and overall scores."""
        results = {"id": conversation["id"], "turns": []}
        scores_a, scores_b = [], []

        for turn_key in ["turn_1", "turn_2"]:
            if turn_key not in conversation:
                continue
            turn = conversation[turn_key]
            sa = self.score_response(turn["response_a"])
            sb = self.score_response(turn["response_b"])
            scores_a.append(sa)
            scores_b.append(sb)
            results["turns"].append({
                "turn": turn_key,
                "score_a": sa,
                "score_b": sb,
                "question": turn["question"][:60] + "..."
            })

        results["avg_a"] = round(sum(scores_a) / len(scores_a), 2) if scores_a else 0
        results["avg_b"] = round(sum(scores_b) / len(scores_b), 2) if scores_b else 0
        results["winner"] = "A" if results["avg_a"] > results["avg_b"] else (
            "B" if results["avg_b"] > results["avg_a"] else "Tie"
        )
        results["human_pref"] = conversation.get("human_pref", "N/A")
        return results


# =============================================================================
# 2. PositionBiasDetector - Detect position bias (Wang et al., 2023)
# =============================================================================
class PositionBiasDetector:
    """Detects whether a judge systematically favors responses in position 1 or 2."""

    def simulate_judge(self, response_1, response_2, bias_strength=0.15):
        """Simulate a biased judge that slightly favors position 1."""
        len_1, len_2 = len(response_1.split()), len(response_2.split())
        base_score_1 = len_1 / max(len_1, len_2)
        base_score_2 = len_2 / max(len_1, len_2)
        # Add position bias toward position 1
        score_1 = base_score_1 + bias_strength
        score_2 = base_score_2
        return {"position_1_score": round(score_1, 3),
                "position_2_score": round(score_2, 3),
                "chosen": 1 if score_1 >= score_2 else 2}

    def detect_bias(self, examples):
        """Run bias detection across multiple equal-quality pairs."""
        results = {"total": len(examples), "pos1_wins": 0, "pos2_wins": 0, "ties": 0,
                   "judgments": []}
        for ex in examples:
            # Original order
            j1 = self.simulate_judge(ex["response_1"], ex["response_2"])
            # Swapped order
            j2 = self.simulate_judge(ex["response_2"], ex["response_1"])

            consistent = (j1["chosen"] == 1 and j2["chosen"] == 2) or \
                         (j1["chosen"] == 2 and j2["chosen"] == 1)
            if j1["chosen"] == 1:
                results["pos1_wins"] += 1
            else:
                results["pos2_wins"] += 1

            results["judgments"].append({
                "id": ex["id"],
                "original_winner": f"Position {j1['chosen']}",
                "swapped_winner": f"Position {j2['chosen']}",
                "consistent": consistent
            })

        total = results["total"]
        results["position_1_rate"] = round(results["pos1_wins"] / total, 3) if total else 0
        results["bias_detected"] = results["position_1_rate"] > 0.6 or results["position_1_rate"] < 0.4
        results["bias_direction"] = "Position 1" if results["position_1_rate"] > 0.6 else (
            "Position 2" if results["position_1_rate"] < 0.4 else "None"
        )
        return results


# =============================================================================
# 3. GEvalScorer - Chain-of-thought scoring (Liu et al., 2023)
# =============================================================================
class GEvalScorer:
    """Simplified G-Eval: scores summaries on coherence, consistency, fluency, relevance."""

    def _word_overlap(self, text_a, text_b):
        """Jaccard similarity between word sets."""
        set_a = set(text_a.lower().split())
        set_b = set(text_b.lower().split())
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def _sentence_count(self, text):
        return max(1, len(re.split(r'[.!?]+', text.strip())))

    def score_coherence(self, summary):
        """Score logical flow (1-5) based on sentence structure."""
        sents = self._sentence_count(summary)
        words = len(summary.split())
        avg_sent_len = words / sents
        # Well-structured summaries have moderate sentence length
        if 8 <= avg_sent_len <= 25:
            return 5
        elif 5 <= avg_sent_len <= 35:
            return 4
        else:
            return 3

    def score_consistency(self, source, summary):
        """Score factual alignment (1-5) using word overlap as proxy."""
        overlap = self._word_overlap(source, summary)
        return min(5, max(1, round(overlap * 10)))

    def score_fluency(self, summary):
        """Score language quality (1-5) based on basic heuristics."""
        words = summary.split()
        if len(words) < 5:
            return 2
        # Check capitalization, punctuation
        starts_cap = summary[0].isupper() if summary else False
        ends_punct = summary.rstrip()[-1] in '.!?' if summary.rstrip() else False
        score = 3
        if starts_cap:
            score += 1
        if ends_punct:
            score += 1
        return min(5, score)

    def score_relevance(self, source, summary):
        """Score topical relevance (1-5) using keyword coverage."""
        source_words = set(source.lower().split())
        summary_words = set(summary.lower().split())
        # Remove stopwords approximately
        stopwords = {"the", "a", "an", "is", "was", "are", "were", "in", "on", "at",
                     "to", "for", "of", "and", "or", "it", "its", "by", "with", "as",
                     "that", "this", "from", "which", "about"}
        source_keywords = source_words - stopwords
        summary_keywords = summary_words - stopwords
        if not source_keywords:
            return 3
        coverage = len(summary_keywords & source_keywords) / len(source_keywords)
        return min(5, max(1, round(coverage * 7)))

    def evaluate(self, source_text, summary):
        """Full G-Eval scoring pipeline with chain-of-thought steps."""
        steps = [
            "Step 1: Read the source document carefully.",
            "Step 2: Read the generated summary.",
            "Step 3: Check coherence - does the summary flow logically?",
            "Step 4: Check consistency - are all facts in the summary supported by the source?",
            "Step 5: Check fluency - is the summary grammatically correct and natural?",
            "Step 6: Check relevance - does the summary capture the main points?",
        ]
        scores = {
            "coherence": self.score_coherence(summary),
            "consistency": self.score_consistency(source_text, summary),
            "fluency": self.score_fluency(summary),
            "relevance": self.score_relevance(source_text, summary),
        }
        scores["average"] = round(sum(scores.values()) / 4, 2)
        return {"chain_of_thought_steps": steps, "scores": scores}


# =============================================================================
# 4. RAGASMetrics - Simplified RAGAS (Es et al., 2023)
# =============================================================================
class RAGASMetrics:
    """Simplified RAGAS: faithfulness and answer relevancy for RAG pipelines."""

    def _extract_claims(self, text):
        """Split text into sentence-level claims."""
        claims = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        return claims if claims else [text]

    def _claim_supported(self, claim, contexts):
        """Check if a claim is supported by any context (word overlap heuristic)."""
        claim_words = set(claim.lower().split())
        for ctx in contexts:
            ctx_words = set(ctx.lower().split())
            if not claim_words:
                return True
            overlap = len(claim_words & ctx_words) / len(claim_words)
            if overlap > 0.4:
                return True
        return False

    def faithfulness(self, answer, contexts):
        """Fraction of answer claims supported by retrieved contexts."""
        claims = self._extract_claims(answer)
        if not claims:
            return 1.0
        supported = sum(1 for c in claims if self._claim_supported(c, contexts))
        return round(supported / len(claims), 3)

    def answer_relevancy(self, question, answer):
        """Measure how relevant the answer is to the question (keyword overlap)."""
        q_words = set(question.lower().split()) - {"what", "is", "the", "a", "an", "how",
                                                    "does", "do", "of", "?", "when", "was"}
        a_words = set(answer.lower().split())
        if not q_words:
            return 1.0
        return round(len(q_words & a_words) / len(q_words), 3)

    def context_precision(self, question, contexts, ground_truth):
        """How many retrieved contexts are actually relevant to answering the question."""
        gt_words = set(ground_truth.lower().split())
        relevant = 0
        for ctx in contexts:
            ctx_words = set(ctx.lower().split())
            if gt_words & ctx_words:
                relevant += 1
        return round(relevant / len(contexts), 3) if contexts else 0.0

    def evaluate(self, question, contexts, answer, ground_truth):
        """Run all RAGAS metrics."""
        return {
            "faithfulness": self.faithfulness(answer, contexts),
            "answer_relevancy": self.answer_relevancy(question, answer),
            "context_precision": self.context_precision(question, contexts, ground_truth),
        }


# =============================================================================
# 5. ARESEvaluator - Prediction-Powered Inference (Saad-Falcon et al., 2023)
# =============================================================================
class ARESEvaluator:
    """Simplified ARES: automated RAG evaluation with confidence intervals."""

    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
        # z-score for 95% CI
        self.z = 1.96 if confidence_level == 0.95 else 1.645

    def compute_ppi_estimate(self, labeled_scores, unlabeled_predictions):
        """
        Prediction-Powered Inference: combine small labeled set with large
        unlabeled predictions to get tighter confidence intervals.
        """
        n_labeled = len(labeled_scores)
        n_unlabeled = len(unlabeled_predictions)

        # Labeled mean and std
        mean_labeled = sum(labeled_scores) / n_labeled
        var_labeled = sum((x - mean_labeled) ** 2 for x in labeled_scores) / max(1, n_labeled - 1)

        # Unlabeled predictions mean
        mean_unlabeled = sum(unlabeled_predictions) / n_unlabeled

        # PPI estimate: weighted combination
        weight = n_labeled / (n_labeled + n_unlabeled)
        ppi_estimate = weight * mean_labeled + (1 - weight) * mean_unlabeled

        # Confidence interval
        se = math.sqrt(var_labeled / n_labeled)
        ci_lower = round(ppi_estimate - self.z * se, 4)
        ci_upper = round(ppi_estimate + self.z * se, 4)

        return {
            "ppi_estimate": round(ppi_estimate, 4),
            "labeled_mean": round(mean_labeled, 4),
            "unlabeled_mean": round(mean_unlabeled, 4),
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "confidence_level": self.confidence_level,
            "n_labeled": n_labeled,
            "n_unlabeled": n_unlabeled,
        }

    def evaluate_rag_system(self, labeled_data, unlabeled_data):
        """Evaluate a RAG system using ARES-style PPI for each metric."""
        metrics = {}
        for metric_name in ["faithfulness", "relevancy", "completeness"]:
            labeled = [d.get(metric_name, random.uniform(0.5, 1.0)) for d in labeled_data]
            unlabeled = [d.get(metric_name, random.uniform(0.4, 0.9)) for d in unlabeled_data]
            metrics[metric_name] = self.compute_ppi_estimate(labeled, unlabeled)
        return metrics


# =============================================================================
# 6. AgentBenchScorer - Multi-environment agent scoring (Liu et al., 2023)
# =============================================================================
class AgentBenchScorer:
    """Simplified AgentBench: evaluate agent trajectories across environments."""

    def score_trajectory(self, trajectory_data):
        """Score a single agent trajectory on completion, efficiency, and accuracy."""
        steps = trajectory_data.get("trajectory", [])
        completed = trajectory_data.get("task_completed", False)
        optimal = trajectory_data.get("optimal_steps", len(steps))

        # Completion score
        completion = 1.0 if completed else 0.0

        # Efficiency: optimal / actual steps
        actual_steps = len(steps) if steps else 1
        efficiency = round(min(1.0, optimal / actual_steps), 3)

        # Accuracy: fraction of correct steps
        correct_steps = sum(1 for s in steps if s.get("correct", False))
        accuracy = round(correct_steps / actual_steps, 3) if actual_steps else 0.0

        # Overall score
        overall = round(0.4 * completion + 0.3 * efficiency + 0.3 * accuracy, 3)

        return {
            "id": trajectory_data.get("id", "unknown"),
            "environment": trajectory_data.get("environment", "unknown"),
            "task": trajectory_data.get("task", "")[:60],
            "completed": completed,
            "steps_taken": actual_steps,
            "optimal_steps": optimal,
            "efficiency": efficiency,
            "accuracy": accuracy,
            "overall_score": overall,
        }

    def score_across_environments(self, agent_examples):
        """Aggregate scores across different environments."""
        env_scores = defaultdict(list)
        all_results = []

        for ex in agent_examples:
            result = self.score_trajectory(ex)
            all_results.append(result)
            env_scores[result["environment"]].append(result["overall_score"])

        env_summary = {}
        for env, scores in env_scores.items():
            env_summary[env] = {
                "count": len(scores),
                "avg_score": round(sum(scores) / len(scores), 3),
                "min_score": round(min(scores), 3),
                "max_score": round(max(scores), 3),
            }

        return {"trajectories": all_results, "environment_summary": env_summary}


# =============================================================================
# 7. SWEBenchScorer - Pass@k for code tasks (Jimenez et al., 2023)
# =============================================================================
class SWEBenchScorer:
    """Simplified SWE-Bench: pass@k metric for code generation/repair tasks."""

    @staticmethod
    def pass_at_k(n, c, k):
        """
        Calculate pass@k: probability that at least one of k samples passes.
        n = total samples, c = correct samples, k = number selected.
        Uses the unbiased estimator from Chen et al. (Codex paper).
        """
        if n - c < k:
            return 1.0
        result = 1.0
        for i in range(k):
            result *= (n - c - i) / (n - i)
        return round(1.0 - result, 4)

    def evaluate_models(self, swe_examples):
        """Evaluate which models solve which issues, compute pass@k stats."""
        model_results = defaultdict(lambda: {"solved": 0, "total": 0, "issues": []})

        all_models = set()
        for ex in swe_examples:
            for m in ex.get("resolved_by", []):
                all_models.add(m)
            for m in ex.get("not_resolved_by", []):
                all_models.add(m)

        for ex in swe_examples:
            resolved = set(ex.get("resolved_by", []))
            not_resolved = set(ex.get("not_resolved_by", []))
            for model in all_models:
                model_results[model]["total"] += 1
                if model in resolved:
                    model_results[model]["solved"] += 1
                    model_results[model]["issues"].append(
                        {"id": ex["id"], "difficulty": ex.get("difficulty", "?"), "solved": True})
                elif model in not_resolved:
                    model_results[model]["issues"].append(
                        {"id": ex["id"], "difficulty": ex.get("difficulty", "?"), "solved": False})

        summary = {}
        for model, data in model_results.items():
            n = data["total"]
            c = data["solved"]
            summary[model] = {
                "solved": c,
                "total": n,
                "pass_at_1": self.pass_at_k(max(n, 1), c, 1),
                "pass_at_3": self.pass_at_k(max(n, 3), c, 3) if n >= 3 else "N/A",
            }
        return summary


# =============================================================================
# 8. ReflexionLoop - Self-reflection with retry (Shinn et al., 2023)
# =============================================================================
class ReflexionLoop:
    """Simplified Reflexion: iterative self-improvement through reflection."""

    def run_reflexion(self, task_data):
        """Analyze a reflexion trajectory: how many attempts, improvement per step."""
        attempts = task_data.get("attempts", [])
        ground_truth = task_data.get("ground_truth")

        analysis = {
            "task": task_data.get("task", ""),
            "ground_truth": ground_truth,
            "total_attempts": len(attempts),
            "attempts_detail": [],
            "solved": False,
            "solved_at_attempt": None,
        }

        for att in attempts:
            detail = {
                "attempt": att["attempt"],
                "answer": att["answer"],
                "correct": att["correct"],
                "reflection_summary": att.get("reflection", "")[:100],
            }
            analysis["attempts_detail"].append(detail)
            if att["correct"] and not analysis["solved"]:
                analysis["solved"] = True
                analysis["solved_at_attempt"] = att["attempt"]

        analysis["improvement_shown"] = (
            len(attempts) > 1 and
            not attempts[0].get("correct", False) and
            any(a.get("correct", False) for a in attempts[1:])
        )
        return analysis

    def simulate_reflexion(self, problem, initial_answer, correct_answer, max_attempts=3):
        """Simulate a reflexion loop with self-correction."""
        attempts = []
        current_answer = initial_answer

        for i in range(1, max_attempts + 1):
            is_correct = (str(current_answer) == str(correct_answer))
            reflection = ""
            if not is_correct:
                reflection = f"Answer {current_answer} != {correct_answer}. Re-examining..."
                # Simulate correction: converge toward correct answer
                current_answer = correct_answer
            else:
                reflection = "Answer verified as correct."

            attempts.append({
                "attempt": i,
                "answer": current_answer,
                "correct": is_correct or i > 1,
                "reflection": reflection,
            })
            if is_correct or i > 1:
                break

        return {
            "problem": problem,
            "total_attempts": len(attempts),
            "final_answer": current_answer,
            "solved": True,
            "attempts": attempts,
        }


# =============================================================================
# 9. MetaEvaluator - Evaluate the evaluator (Various, 2023-2024)
# =============================================================================
class MetaEvaluator:
    """Meta-evaluation: measure how reliable an LLM judge is vs. human judgments."""

    def agreement_rate(self, human_scores, judge_scores):
        """Exact agreement rate between human and judge."""
        assert len(human_scores) == len(judge_scores)
        n = len(human_scores)
        agree = sum(1 for h, j in zip(human_scores, judge_scores) if h == j)
        return round(agree / n, 4) if n else 0.0

    def cohens_kappa(self, human_scores, judge_scores):
        """Cohen's Kappa: agreement adjusted for chance."""
        n = len(human_scores)
        if n == 0:
            return 0.0

        labels = sorted(set(human_scores) | set(judge_scores))
        po = sum(1 for h, j in zip(human_scores, judge_scores) if h == j) / n

        # Expected agreement
        pe = 0.0
        for label in labels:
            p_human = sum(1 for h in human_scores if h == label) / n
            p_judge = sum(1 for j in judge_scores if j == label) / n
            pe += p_human * p_judge

        if pe == 1.0:
            return 1.0
        return round((po - pe) / (1 - pe), 4)

    def spearmans_rho(self, human_scores, judge_scores):
        """Spearman's rank correlation (simplified)."""
        n = len(human_scores)
        if n < 2:
            return 0.0

        def rank(arr):
            sorted_indices = sorted(range(len(arr)), key=lambda i: arr[i])
            ranks = [0.0] * len(arr)
            for rank_val, idx in enumerate(sorted_indices, 1):
                ranks[idx] = float(rank_val)
            return ranks

        r_human = rank(human_scores)
        r_judge = rank(judge_scores)

        d_squared = sum((rh - rj) ** 2 for rh, rj in zip(r_human, r_judge))
        rho = 1 - (6 * d_squared) / (n * (n ** 2 - 1))
        return round(rho, 4)

    def bias_analysis(self, human_scores, judge_scores):
        """Detect systematic bias in judge scores."""
        n = len(human_scores)
        mean_h = sum(human_scores) / n
        mean_j = sum(judge_scores) / n
        diff = mean_j - mean_h

        if diff > 0.3:
            direction = "positive (judge scores higher)"
        elif diff < -0.3:
            direction = "negative (judge scores lower)"
        else:
            direction = "minimal"

        return {
            "human_mean": round(mean_h, 3),
            "judge_mean": round(mean_j, 3),
            "mean_difference": round(diff, 3),
            "bias_direction": direction,
        }

    def evaluate(self, evaluator_name, human_scores, judge_scores):
        """Full meta-evaluation of a judge."""
        return {
            "evaluator": evaluator_name,
            "agreement_rate": self.agreement_rate(human_scores, judge_scores),
            "cohens_kappa": self.cohens_kappa(human_scores, judge_scores),
            "spearmans_rho": self.spearmans_rho(human_scores, judge_scores),
            "bias": self.bias_analysis(human_scores, judge_scores),
            "n_samples": len(human_scores),
        }


# =============================================================================
# 10. EloRatingSystem - Tournament ranking (Zheng et al., 2023)
# =============================================================================
class EloRatingSystem:
    """Elo rating system for pairwise model comparisons (as used in Chatbot Arena)."""

    def __init__(self, k=32, default_rating=1200):
        self.k = k
        self.default_rating = default_rating
        self.ratings = {}

    def _ensure_player(self, name):
        if name not in self.ratings:
            self.ratings[name] = float(self.default_rating)

    def expected_score(self, rating_a, rating_b):
        """Expected probability of A winning against B."""
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))

    def update(self, winner, loser, draw=False):
        """Update ratings after a match."""
        self._ensure_player(winner)
        self._ensure_player(loser)

        ea = self.expected_score(self.ratings[winner], self.ratings[loser])
        eb = 1.0 - ea

        if draw:
            sa, sb = 0.5, 0.5
        else:
            sa, sb = 1.0, 0.0

        self.ratings[winner] += self.k * (sa - ea)
        self.ratings[loser] += self.k * (sb - eb)

    def get_leaderboard(self):
        """Return sorted leaderboard."""
        board = sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
        return [{"rank": i + 1, "model": name, "elo": round(rating, 1)}
                for i, (name, rating) in enumerate(board)]

    def simulate_tournament(self, models, matchups):
        """Run a simulated tournament from a list of (winner, loser) pairs."""
        for m in models:
            self._ensure_player(m)
        for winner, loser in matchups:
            self.update(winner, loser)
        return self.get_leaderboard()


# =============================================================================
# 11. CalibratedJudge - Judge calibration analysis (Various, 2023-2024)
# =============================================================================
class CalibratedJudge:
    """Analyze calibration of LLM judge confidence vs actual accuracy."""

    def expected_calibration_error(self, predictions):
        """
        ECE: group predictions by confidence bins, measure gap between
        confidence and actual accuracy per bin.
        """
        n_bins = 5
        bins = [[] for _ in range(n_bins)]

        for pred in predictions:
            conf = pred.get("judge_confidence", 0.5)
            correct = pred.get("human_agreement", False)
            bin_idx = min(int(conf * n_bins), n_bins - 1)
            bins[bin_idx].append((conf, 1.0 if correct else 0.0))

        ece = 0.0
        total = len(predictions)
        bin_details = []

        for i, b in enumerate(bins):
            if not b:
                continue
            avg_conf = sum(c for c, _ in b) / len(b)
            avg_acc = sum(a for _, a in b) / len(b)
            gap = abs(avg_conf - avg_acc)
            ece += (len(b) / total) * gap
            bin_details.append({
                "bin": f"{i / n_bins:.1f}-{(i + 1) / n_bins:.1f}",
                "count": len(b),
                "avg_confidence": round(avg_conf, 3),
                "avg_accuracy": round(avg_acc, 3),
                "gap": round(gap, 3),
            })

        return {
            "ece": round(ece, 4),
            "n_bins": n_bins,
            "bin_details": bin_details,
            "interpretation": "well-calibrated" if ece < 0.1 else (
                "moderately calibrated" if ece < 0.2 else "poorly calibrated"
            ),
        }
