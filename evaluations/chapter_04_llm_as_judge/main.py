import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 4 - LLM-as-a-Judge: Entry Point
========================================
Demonstrates ALL 21 LLM-as-a-Judge techniques:

 1. History of LLM-as-a-Judge
 2. Why BLEU/ROUGE Are Insufficient
 3. Judge Prompt Engineering
 4. Pointwise Evaluation
 5. Pairwise Evaluation
 6. Pass/Fail Evaluation
 7. Likert Scale Evaluation
 8. Rubric-Based Evaluation
 9. G-Eval (Chain-of-Thought)
10. Arena-Style Evaluation
11. Tournament / Elo Ratings
12. Constitutional Evaluation
13. Self-Evaluation
14. Reflexion (Iterative Improvement)
15. Multi-Agent Judging
16. Judge Agreement Metrics
17. Judge Reliability
18. Bias Detection
19. Meta-Evaluation
20. Human Agreement Analysis
21. Production Best Practices

All evaluations use simulated judge responses so the code runs without
external dependencies. See evaluator.py for commented-out Ollama/Mistral
integration.
"""

import json
import random
import statistics

from dataset import (
    get_bias_test_data,
    get_dataset_summary,
    get_pairwise_items,
    get_questions_with_responses,
    generate_arena_matchups,
)
from evaluator import (
    ArenaEvaluator,
    BiasDetector,
    ClassicalMetricsDemonstrator,
    ConstitutionalJudge,
    EloRatingSystem,
    GEvalJudge,
    JudgeAgreement,
    JudgeReliability,
    LikertJudge,
    MetaEvaluator,
    MultiJudgePanel,
    PairwiseJudge,
    PassFailJudge,
    PointwiseJudge,
    ReflexionEvaluator,
    RubricJudge,
    SelfEvaluator,
)

# ============================================================================
# Helpers
# ============================================================================
SECTION_WIDTH = 78


def banner(number, title):
    """Print a numbered section banner."""
    header = f"  {number}. {title}  "
    print("\n" + "=" * SECTION_WIDTH)
    print(header.center(SECTION_WIDTH))
    print("=" * SECTION_WIDTH)


def sub(title):
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def show(obj, indent=2):
    """Pretty-print a dict or list."""
    print(json.dumps(obj, indent=indent, default=str))


# ============================================================================
# 1. History of LLM-as-a-Judge
# ============================================================================
def topic_01_history():
    banner(1, "History of LLM-as-a-Judge")
    print("  See theory.md for full timeline. Key: BLEU/ROUGE (2002) -> "
          "neural metrics (2015) -> LLM judges (2023) -> hybrid pipelines (2024+).")


# ============================================================================
# 2. Why BLEU/ROUGE Are Insufficient
# ============================================================================
def topic_02_bleu_rouge_insufficient():
    banner(2, "Why BLEU/ROUGE Are Insufficient")

    demo = ClassicalMetricsDemonstrator()
    cases = demo.demonstrate_failures()

    for i, case in enumerate(cases, 1):
        sub(f"Failure case {i}: {case['name']}")
        print(f"  Question   : {case['question']}")
        print(f"  Expected   : {case['expected']}")
        print(f"  Good answer BLEU   : {case['good_answer_bleu']:.4f}")
        print(f"  Bad  answer BLEU   : {case['bad_answer_bleu']:.4f}")
        print(f"  BLEU picks correctly: {case['bleu_correct']}")
        print(f"  Good answer ROUGE-L: {case['good_answer_rouge_l']:.4f}")
        print(f"  Bad  answer ROUGE-L: {case['bad_answer_rouge_l']:.4f}")
        print(f"  ROUGE picks correctly: {case['rouge_correct']}")

    correct_bleu = sum(1 for c in cases if c["bleu_correct"])
    correct_rouge = sum(1 for c in cases if c["rouge_correct"])
    print(f"\nSummary: BLEU correct {correct_bleu}/{len(cases)}, "
          f"ROUGE-L correct {correct_rouge}/{len(cases)}")
    print("Conclusion: n-gram metrics frequently disagree with human quality "
          "judgments, especially for paraphrases and factual errors.")


# ============================================================================
# 3. Judge Prompt Engineering
# ============================================================================
def topic_03_prompt_engineering():
    banner(3, "Judge Prompt Engineering")

    from evaluator import POINTWISE_PROMPT, PAIRWISE_PROMPT, GEVAL_PROMPT

    sub("Pointwise prompt (first 200 chars)")
    print(POINTWISE_PROMPT[:200], "...")

    sub("Pairwise prompt (first 200 chars)")
    print(PAIRWISE_PROMPT[:200], "...")

    sub("G-Eval prompt (first 200 chars)")
    print(GEVAL_PROMPT[:200], "...")


# ============================================================================
# 4. Pointwise Evaluation
# ============================================================================
def topic_04_pointwise():
    banner(4, "Pointwise Evaluation")

    items = get_questions_with_responses(limit=3)
    judge = PointwiseJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        for model_key, model_data in item["model_responses"].items():
            result = judge.simulate_judgment(
                item["prompt"],
                model_data["response"],
                item["reference_answer"],
            )
            print(f"  {model_key} ({model_data['model_name']}): "
                  f"Score={result['score']}/5 -- {result['reasoning'][:80]}")


# ============================================================================
# 5. Pairwise Evaluation
# ============================================================================
def topic_05_pairwise():
    banner(5, "Pairwise Evaluation")

    pairs = get_pairwise_items(limit=5)
    judge = PairwiseJudge(seed=42)

    for pair in pairs:
        result = judge.simulate_judgment(
            pair["prompt"],
            pair["response_a"],
            pair["response_b"],
            pair["reference_answer"],
        )
        print(f"  Q{pair['id']}: Judge winner = Response {result['winner']}  "
              f"| Human preference = {pair['human_preference']}")
        print(f"         Scores: A={result['score_a']} B={result['score_b']}  "
              f"| Reason: {result['reasoning'][:70]}")


# ============================================================================
# 6. Pass/Fail Evaluation
# ============================================================================
def topic_06_pass_fail():
    banner(6, "Pass/Fail Evaluation")

    items = get_questions_with_responses(limit=3)
    judge = PassFailJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        for model_key, model_data in item["model_responses"].items():
            result = judge.simulate_judgment(
                item["prompt"],
                model_data["response"],
            )
            print(f"  {model_key}: {result['verdict']}  "
                  f"({result['word_count']} words)  "
                  f"Reasons: {'; '.join(result['reasons'][:2])}")


# ============================================================================
# 7. Likert Scale Evaluation
# ============================================================================
def topic_07_likert():
    banner(7, "Likert Scale Evaluation")

    items = get_questions_with_responses(limit=2)
    judge = LikertJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        for model_key, model_data in item["model_responses"].items():
            result = judge.simulate_judgment(
                item["prompt"],
                model_data["response"],
                item["reference_answer"],
            )
            scores = result["scores"]
            dims = " | ".join(
                f"{d}={scores[d]}" for d in result["dimensions"]
            )
            print(f"  {model_key}: {dims}  Avg={scores['average']}")


# ============================================================================
# 8. Rubric-Based Evaluation
# ============================================================================
def topic_08_rubric():
    banner(8, "Rubric-Based Evaluation")

    items = get_questions_with_responses(limit=2)
    judge = RubricJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        for model_key, model_data in item["model_responses"].items():
            result = judge.simulate_judgment(
                item["prompt"],
                model_data["response"],
                item["reference_answer"],
            )
            parts = " | ".join(
                f"{k}={v}" for k, v in result["scores"].items()
            )
            print(f"  {model_key}: {parts}  "
                  f"Total={result['total']}/{result['max_total']} "
                  f"({result['percentage']}%)")


# ============================================================================
# 9. G-Eval (Chain-of-Thought Evaluation)
# ============================================================================
def topic_09_geval():
    banner(9, "G-Eval (Chain-of-Thought Evaluation)")

    items = get_questions_with_responses(limit=2)
    judge = GEvalJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        # Show detailed G-Eval for first model only to keep output manageable
        first_model_key = list(item["model_responses"].keys())[0]
        model_data = item["model_responses"][first_model_key]
        result = judge.simulate_judgment(
            item["prompt"],
            model_data["response"],
            item["reference_answer"],
        )
        print(f"  Model: {first_model_key} ({model_data['model_name']})")
        print(f"  Chain-of-thought steps ({result['num_steps']}):")
        for step in result["chain_of_thought"]:
            print(f"    Step '{step['step']}': {step['analysis'][:70]}... "
                  f"(confidence={step['confidence']})")
        print(f"  Final Score: {result['final_score']}/5  "
              f"Avg Confidence: {result['avg_confidence']}")


# ============================================================================
# 10. Arena-Style Evaluation
# ============================================================================
def topic_10_arena():
    banner(10, "Arena-Style Evaluation")

    items = get_questions_with_responses(limit=5)
    arena = ArenaEvaluator(seed=42)
    model_keys = list(items[0]["model_responses"].keys())

    # Run round-robin matches
    for item in items:
        responses = item["model_responses"]
        for i in range(len(model_keys)):
            for j in range(i + 1, len(model_keys)):
                mk_a, mk_b = model_keys[i], model_keys[j]
                arena.simulate_match(
                    mk_a, mk_b, item["id"],
                    responses[mk_a]["response"],
                    responses[mk_b]["response"],
                )

    sub("Win Rates")
    for model, stats in arena.get_win_rates().items():
        print(f"  {model}: {stats['wins']}/{stats['total']} wins "
              f"({stats['win_rate']:.1%})")

    sub("Leaderboard")
    for entry in arena.get_leaderboard():
        print(f"  #{entry['rank']} {entry['model']}  "
              f"Win rate: {entry['win_rate']:.1%}")


# ============================================================================
# 11. Tournament / Elo Ratings
# ============================================================================
def topic_11_elo():
    banner(11, "Tournament / Elo Ratings")

    items = get_questions_with_responses(limit=5)
    elo = EloRatingSystem(k_factor=32, initial_rating=1500)
    model_keys = list(items[0]["model_responses"].keys())
    pairwise_judge = PairwiseJudge(seed=99)

    for item in items:
        responses = item["model_responses"]
        for i in range(len(model_keys)):
            for j in range(i + 1, len(model_keys)):
                mk_a, mk_b = model_keys[i], model_keys[j]
                result = pairwise_judge.simulate_judgment(
                    item["prompt"],
                    responses[mk_a]["response"],
                    responses[mk_b]["response"],
                    item["reference_answer"],
                )
                winner = mk_a if result["winner"] == "A" else mk_b
                loser = mk_b if winner == mk_a else mk_a
                elo.update_ratings(winner, loser)

    sub("Elo Leaderboard")
    for entry in elo.get_leaderboard():
        print(f"  #{entry['rank']} {entry['model']}  "
              f"Elo={entry['elo_rating']}  Matches={entry['matches']}")

    sub("Sample match history (last 5)")
    for h in elo.history[-5:]:
        print(f"  {h['winner']} beat {h['loser']}  "
              f"(expected {h['expected_win_prob']:.3f})  "
              f"Ratings: {h['winner_rating_before']}->{h['winner_rating_after']} "
              f"/ {h['loser_rating_before']}->{h['loser_rating_after']}")


# ============================================================================
# 12. Constitutional Evaluation
# ============================================================================
def topic_12_constitutional():
    banner(12, "Constitutional Evaluation")
    print("Check responses against a set of core principles (accuracy, "
          "helpfulness, harmlessness, honesty, completeness).\n")

    items = get_questions_with_responses(limit=3)
    judge = ConstitutionalJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        first_key = list(item["model_responses"].keys())[0]
        model_data = item["model_responses"][first_key]
        result = judge.simulate_judgment(
            item["prompt"],
            model_data["response"],
        )
        print(f"  Model: {first_key} ({model_data['model_name']})")
        for principle, info in result["results"].items():
            print(f"    {principle:15s}: {info['verdict']:8s} -- {info['reason'][:60]}")
        print(f"  Overall: {result['overall_verdict']}  "
              f"Violations: {result['violations'] if result['violations'] else 'None'}")


# ============================================================================
# 13. Self-Evaluation
# ============================================================================
def topic_13_self_evaluation():
    banner(13, "Self-Evaluation")
    print("A model evaluates its own output, identifying strengths and "
          "weaknesses.\n")

    items = get_questions_with_responses(limit=2)
    judge = SelfEvaluator(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        first_key = list(item["model_responses"].keys())[0]
        model_data = item["model_responses"][first_key]
        result = judge.simulate_judgment(
            item["prompt"],
            model_data["response"],
        )
        print(f"  Self-Score: {result['self_score']}/5")
        print(f"  Strengths : {'; '.join(result['strengths'])}")
        print(f"  Weaknesses: {'; '.join(result['weaknesses'])}")
        print(f"  Improvements: {'; '.join(result['improvements'])}")
        print(f"  Bias warning: {result['bias_warning']}")


# ============================================================================
# 14. Reflexion (Iterative Improvement)
# ============================================================================
def topic_14_reflexion():
    banner(14, "Reflexion (Iterative Improvement)")
    print("Write -> Evaluate -> Get feedback -> Revise -> Repeat.\n")

    items = get_questions_with_responses(limit=2)
    reflexion = ReflexionEvaluator(max_iterations=3, seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        first_key = list(item["model_responses"].keys())[0]
        initial_resp = item["model_responses"][first_key]["response"]
        result = reflexion.simulate_full_reflexion(
            item["prompt"],
            initial_resp,
        )
        print(f"  Score trajectory: {result['score_trajectory']}")
        print(f"  Initial score: {result['initial_score']} -> "
              f"Final score: {result['final_score']}")
        for it in result["iterations"]:
            print(f"    Iteration {it['iteration']}: score={it['score']}  "
                  f"feedback: {it['feedback'][:60]}")


# ============================================================================
# 15. Multi-Agent Judging
# ============================================================================
def topic_15_multi_agent():
    banner(15, "Multi-Agent Judging")
    print("A panel of specialist judges (accuracy, clarity, completeness) "
          "evaluates and reaches consensus.\n")

    items = get_questions_with_responses(limit=3)
    panel = MultiJudgePanel(num_judges=3, seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        first_key = list(item["model_responses"].keys())[0]
        model_data = item["model_responses"][first_key]
        result = panel.simulate_judgment(
            item["prompt"],
            model_data["response"],
            item["reference_answer"],
        )
        for j in result["individual_scores"]:
            print(f"    Judge {j['judge_id']} ({j['expertise'][:30]}): "
                  f"Score={j['score']}/5")
        print(f"  Consensus: {result['consensus_score']}  "
              f"Median: {result['median_score']}  "
              f"StdDev: {result['std_dev']}  "
              f"Agreement: {result['agreement']}")


# ============================================================================
# 16. Judge Agreement Metrics
# ============================================================================
def topic_16_judge_agreement():
    banner(16, "Judge Agreement Metrics")
    print("Quantify how consistently different judges score the same items.\n")

    # Simulate scores from two judges across 10 items
    rng = random.Random(42)
    judge1_scores = [rng.randint(2, 5) for _ in range(10)]
    judge2_scores = [max(1, min(5, s + rng.choice([-1, 0, 0, 1])))
                     for s in judge1_scores]

    print(f"  Judge 1 scores: {judge1_scores}")
    print(f"  Judge 2 scores: {judge2_scores}")

    agreement = JudgeAgreement()

    pct = agreement.percent_agreement(judge1_scores, judge2_scores)
    print(f"\n  Percent agreement     : {pct:.2%}")

    kappa = agreement.cohens_kappa(judge1_scores, judge2_scores)
    print(f"  Cohen's Kappa         : {kappa:.4f}")
    if kappa > 0.8:
        interp = "almost perfect"
    elif kappa > 0.6:
        interp = "substantial"
    elif kappa > 0.4:
        interp = "moderate"
    elif kappa > 0.2:
        interp = "fair"
    else:
        interp = "slight"
    print(f"    Interpretation      : {interp} agreement")

    corr = agreement.correlation(
        [float(s) for s in judge1_scores],
        [float(s) for s in judge2_scores],
    )
    print(f"  Pearson correlation   : {corr:.4f}")

    mad = agreement.mean_absolute_difference(
        [float(s) for s in judge1_scores],
        [float(s) for s in judge2_scores],
    )
    print(f"  Mean absolute diff    : {mad:.4f}")


# ============================================================================
# 17. Judge Reliability
# ============================================================================
def topic_17_judge_reliability():
    banner(17, "Judge Reliability")
    print("Test-retest: does the same judge give consistent scores for the "
          "same input?\n")

    items = get_questions_with_responses(limit=2)
    reliability = JudgeReliability(seed=42)
    judge = PointwiseJudge(seed=42)

    for item in items:
        sub(f"Q{item['id']}: {item['prompt'][:70]}...")
        first_key = list(item["model_responses"].keys())[0]
        model_data = item["model_responses"][first_key]
        result = reliability.test_retest_reliability(
            judge,
            item["prompt"],
            model_data["response"],
            item["reference_answer"],
            num_trials=5,
        )
        print(f"  Scores across {result['num_trials']} trials: {result['scores']}")
        print(f"  Mean={result['mean']}  StdDev={result['std_dev']}  "
              f"Range={result['range']}")
        print(f"  Consistent: {result['is_consistent']}  "
              f"Rating: {result['consistency_rating']}")

    sub("Calibration test")
    calibration_items = [
        {
            "label": "excellent",
            "question": "What is gravity?",
            "response": ("Gravity is a fundamental force of nature described by "
                         "Einstein's general relativity as the curvature of spacetime "
                         "caused by mass and energy. Newton approximated it as "
                         "F = GMm/r^2. It governs planetary orbits, tides, and the "
                         "large-scale structure of the universe."),
            "reference": "Gravity is the fundamental force of attraction between masses.",
        },
        {
            "label": "good",
            "question": "What is gravity?",
            "response": ("Gravity is the force that attracts objects with mass toward "
                         "each other. It keeps planets in orbit and causes objects to "
                         "fall to the ground."),
            "reference": "Gravity is the fundamental force of attraction between masses.",
        },
        {
            "label": "poor",
            "question": "What is gravity?",
            "response": "Gravity is a thing that pulls stuff down.",
            "reference": "Gravity is the fundamental force of attraction between masses.",
        },
    ]
    cal_result = reliability.calibration_test(
        judge, calibration_items, ["excellent", "good", "poor"],
    )
    print(f"  Scores: {cal_result['scores']}")
    print(f"  Expected order : {cal_result['expected_order']}")
    print(f"  Actual order   : {cal_result['actual_order']}")
    print(f"  Correctly ordered: {cal_result['is_correctly_ordered']}  "
          f"Calibration: {cal_result['calibration']}")


# ============================================================================
# 18. Bias Detection
# ============================================================================
def topic_18_biases():
    banner(18, "Bias Detection")
    print("Detect verbosity bias, position bias, length bias, and "
          "self-favoritism.\n")

    bias_data = get_bias_test_data()
    detector = BiasDetector(seed=42)
    judge_pw = PointwiseJudge(seed=42)
    judge_pair = PairwiseJudge(seed=42)

    # --- Verbosity bias ---
    sub("Verbosity Bias")
    vb = bias_data.get("verbosity_bias", {})
    if vb:
        result = detector.test_verbosity_bias(
            judge_pw,
            vb["question"],
            vb["concise_response"],
            vb["verbose_response"],
        )
        print(f"  Concise score : {result['concise_score']}  "
              f"({result['concise_word_count']} words)")
        print(f"  Verbose score : {result['verbose_score']}  "
              f"({result['verbose_word_count']} words)")
        print(f"  Bias detected : {result['bias_detected']}  "
              f"Magnitude: {result['bias_magnitude']}")
        print(f"  Recommendation: {result['recommendation']}")

    # --- Position bias ---
    sub("Position Bias")
    pb = bias_data.get("position_bias", {})
    if pb:
        result = detector.test_position_bias(
            judge_pair,
            pb["question"],
            pb["response_a"],
            pb["response_b"],
            num_swaps=5,
        )
        print(f"  First-position win rate: {result['first_position_win_rate']:.3f}  "
              f"(expected 0.500)")
        print(f"  Bias detected : {result['bias_detected']}  "
              f"Direction: {result['bias_direction']}")
        print(f"  Recommendation: {result['recommendation']}")

    # --- Length bias ---
    sub("Length Bias")
    result = detector.test_length_bias(
        judge_pw,
        "What is the Roche limit?",
        "The Roche limit is the distance at which tidal forces disintegrate a body.",
        num_lengths=5,
    )
    print(f"  Length-score correlation: {result['length_score_correlation']:.4f}")
    print(f"  Bias detected : {result['bias_detected']}")
    for r in result["results"]:
        print(f"    {r['word_count']:4d} words -> score {r['score']}")
    print(f"  Recommendation: {result['recommendation']}")

    # --- Self-favoritism ---
    sub("Self-Favoritism Bias")
    sf = bias_data.get("self_favoritism", {})
    if sf:
        result = detector.test_self_favoritism(
            judge_pw,
            sf["question"],
            sf["own_model_response"],
            sf["other_model_response"],
        )
        print(f"  Own model score   : {result['own_model_score']}")
        print(f"  Other model score : {result['other_model_score']}")
        print(f"  Bias detected     : {result['bias_detected']}  "
              f"Magnitude: {result['bias_magnitude']}")
        print(f"  Recommendation    : {result['recommendation']}")


# ============================================================================
# 19. Meta-Evaluation
# ============================================================================
def topic_19_meta_evaluation():
    banner(19, "Meta-Evaluation")
    print("Evaluate the evaluator: compare judge scores with human scores.\n")

    meta = MetaEvaluator()

    # Simulate judge vs human scores for 15 items
    rng = random.Random(42)
    human_scores_list = [rng.randint(1, 5) for _ in range(15)]
    for hs in human_scores_list:
        # Judge is slightly noisy around human score
        js = max(1, min(5, hs + rng.choice([-1, 0, 0, 0, 1])))
        meta.add_evaluation(judge_score=float(js), human_score=float(hs))

    result = meta.compute_agreement()
    print(f"  Evaluations compared : {result['num_evaluations']}")
    print(f"  Exact agreement      : {result['exact_agreement']:.2%}")
    print(f"  Within-1 agreement   : {result['within_1_agreement']:.2%}")
    print(f"  Pearson correlation  : {result['correlation']:.4f}")
    print(f"  Mean absolute error  : {result['mean_absolute_error']:.4f}")
    print(f"  Direction agreement  : {result['direction_agreement']:.2%}")
    print(f"  Judge mean           : {result['judge_mean']}")
    print(f"  Human mean           : {result['human_mean']}")
    print(f"  Judge tendency       : {result['judge_tends']}")


# ============================================================================
# 20. Human Agreement Analysis
# ============================================================================
def topic_20_human_agreement():
    banner(20, "Human Agreement Analysis")
    print("Measure how well the LLM judge agrees with human preferences "
          "on pairwise comparisons.\n")

    pairs = get_pairwise_items(limit=5)
    judge = PairwiseJudge(seed=42)

    agreements = 0
    total = 0
    results_table = []

    for pair in pairs:
        result = judge.simulate_judgment(
            pair["prompt"],
            pair["response_a"],
            pair["response_b"],
            pair["reference_answer"],
        )
        judge_pref = "model_a" if result["winner"] == "A" else "model_b"
        human_pref = pair["human_preference"]
        # Count ties as half-agreement
        if human_pref == "tie":
            agrees = True  # Accept either answer when human says tie
        else:
            agrees = (judge_pref == human_pref)

        if agrees:
            agreements += 1
        total += 1
        results_table.append({
            "question_id": pair["id"],
            "judge_preference": judge_pref,
            "human_preference": human_pref,
            "agrees": agrees,
            "human_reason": pair["human_reason"][:50],
        })

    for row in results_table:
        status = "AGREE" if row["agrees"] else "DISAGREE"
        print(f"  Q{row['question_id']}: Judge={row['judge_preference']:8s}  "
              f"Human={row['human_preference']:8s}  [{status}]  "
              f"Reason: {row['human_reason']}")

    agreement_rate = agreements / total if total > 0 else 0
    print(f"\n  Overall judge-human agreement: {agreements}/{total} "
          f"({agreement_rate:.0%})")
    print("  Note: Ties counted as agreement with either judge pick.")
    print("  Industry benchmark: GPT-4 achieves ~80% agreement with humans "
          "on open-ended tasks.")


# ============================================================================
# 21. Production Best Practices
# ============================================================================
def topic_21_production_best_practices():
    banner(21, "Production Best Practices")
    print("""
Comprehensive checklist for deploying LLM-as-a-Judge in production:

JUDGE SELECTION & SETUP
  [1] Use a stronger model as judge than the model being evaluated
  [2] Keep judge model version pinned (avoid silent upgrades changing scores)
  [3] Use low temperature (0.0-0.2) for consistent, reproducible judging
  [4] Set max_tokens high enough for full reasoning + score

PROMPT DESIGN
  [5] Include reference/gold answers when available
  [6] Ask for reasoning BEFORE the final score (reduces anchoring)
  [7] Use structured output (JSON or fixed format) for reliable parsing
  [8] Define score levels explicitly in the prompt (anchored rubrics)

BIAS MITIGATION
  [9] Swap response positions in pairwise and average (counter position bias)
 [10] Normalize or control for response length (counter verbosity bias)
 [11] Do NOT use the same model as both generator and judge (self-favoritism)
 [12] Randomize presentation order across evaluations

RELIABILITY & CALIBRATION
 [13] Run test-retest checks: same input should get same score
 [14] Use multi-judge panels for high-stakes decisions (3+ judges)
 [15] Calibrate against human annotations on a held-out set (>100 items)
 [16] Monitor judge drift over time (scores may shift with model updates)

METRICS & MONITORING
 [17] Track Cohen's Kappa and Pearson correlation with human scores
 [18] Set alert thresholds: kappa < 0.4 or correlation < 0.5 = investigate
 [19] Log all judge prompts and outputs for auditability
 [20] Periodically re-run meta-evaluation with fresh human annotations

COST & LATENCY
 [21] Batch judge calls to reduce API overhead
 [22] Cache judge results -- same input should not be re-judged
 [23] Use smaller/faster judge for initial screening, premium for borderline
 [24] Budget: judge calls typically cost 2-5x the generation call

HYBRID HUMAN-LLM PIPELINE
 [25] Use LLM judge for initial triage (pass/fail/borderline)
 [26] Route borderline cases to human reviewers
 [27] Feed human corrections back to improve judge prompts
 [28] Maintain a golden dataset of human-scored examples for calibration
""")

    sub("Quick reference: when to use which technique")
    print("""
  Use case                          Recommended technique
  --------------------------------  --------------------------------
  Grade a single response           Pointwise (Sec 4)
  Compare two models                Pairwise (Sec 5)
  Quality gate before deployment    Pass/Fail (Sec 6)
  Detailed diagnostic feedback      Likert multi-dimension (Sec 7)
  Standardized, reproducible eval   Rubric-based (Sec 8)
  Better human correlation          G-Eval chain-of-thought (Sec 9)
  Rank many models at once          Arena + Elo (Sec 10-11)
  Safety & alignment checking       Constitutional (Sec 12)
  Quick self-check during gen       Self-evaluation (Sec 13)
  Iterative response improvement    Reflexion (Sec 14)
  High-stakes, high-reliability     Multi-agent panel (Sec 15)
""")


# ============================================================================
# Dataset overview
# ============================================================================
def show_dataset_overview():
    banner("0", "Dataset Overview")
    summary = get_dataset_summary()
    print(f"  Total questions        : {summary['total_questions']}")
    print(f"  Topics                 : {summary['topics']}")
    print(f"  Pairwise comparisons   : {summary['pairwise_comparisons']}")
    print(f"  Bias test categories   : {summary['bias_tests']}")
    print(f"  Models:")
    for key, info in summary["models"].items():
        print(f"    {key}: {info['name']} -- {info['description']}")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * SECTION_WIDTH)
    print("  CHAPTER 4 -- LLM-AS-A-JUDGE: COMPLETE DEMONSTRATION".center(SECTION_WIDTH))
    print("  All 21 Techniques with Simulated Judges".center(SECTION_WIDTH))
    print("=" * SECTION_WIDTH)

    show_dataset_overview()

    topic_01_history()
    topic_02_bleu_rouge_insufficient()
    topic_03_prompt_engineering()
    topic_04_pointwise()
    topic_05_pairwise()
    topic_06_pass_fail()
    topic_07_likert()
    topic_08_rubric()
    topic_09_geval()
    topic_10_arena()
    topic_11_elo()
    topic_12_constitutional()
    topic_13_self_evaluation()
    topic_14_reflexion()
    topic_15_multi_agent()
    topic_16_judge_agreement()
    topic_17_judge_reliability()
    topic_18_biases()
    topic_19_meta_evaluation()
    topic_20_human_agreement()
    topic_21_production_best_practices()

    print("\n" + "=" * SECTION_WIDTH)
    print("  ALL 21 TOPICS DEMONSTRATED SUCCESSFULLY".center(SECTION_WIDTH))
    print("=" * SECTION_WIDTH)


if __name__ == "__main__":
    main()
