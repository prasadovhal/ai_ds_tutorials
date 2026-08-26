import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 12: Research Papers on LLM Evaluation
=============================================
Code demos of 10 landmark evaluation papers.
"""

import json
from dataset import (
    load_sample_data, load_train_csv,
    get_mt_bench_conversations, get_position_bias_examples,
    get_geval_examples, get_rag_examples, get_agent_examples,
    get_reflexion_examples, get_calibration_examples,
    get_swe_bench_examples, get_meta_evaluation_examples,
)
from evaluator import (
    MTBenchEvaluator, PositionBiasDetector, GEvalScorer,
    RAGASMetrics, ARESEvaluator, AgentBenchScorer,
    SWEBenchScorer, ReflexionLoop, MetaEvaluator,
    EloRatingSystem, CalibratedJudge,
)


def divider(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def sub_divider(title):
    print(f"\n--- {title} ---")


# =========================================================================
# Load data
# =========================================================================
divider("LOADING DATA")
data = load_sample_data()
print(f"Sample data sections: {list(data.keys())}")
for k, v in data.items():
    print(f"  {k}: {len(v)} items")

train = load_train_csv(limit=5)
print(f"\nTrain CSV: {len(train)} rows loaded (limit=5)")
if train:
    print(f"  Columns: {list(train[0].keys())}")
    print(f"  Sample: id={train[0]['id']}, answer={train[0]['answer']}")


# =========================================================================
# Paper 1: MT-Bench (Zheng et al., 2023)
# =========================================================================
divider("PAPER 1: MT-Bench (Zheng et al., 2023)")

mt_eval = MTBenchEvaluator()
conversations = get_mt_bench_conversations(data)

for conv in conversations:
    result = mt_eval.evaluate_conversation(conv)
    print(f"\n  [{result['id']}] Category: {conv.get('category', 'N/A')}")
    for turn in result["turns"]:
        print(f"    {turn['turn']}: A={turn['score_a']:.1f}  B={turn['score_b']:.1f}  | {turn['question']}")
    print(f"    Avg: A={result['avg_a']}  B={result['avg_b']}  Winner={result['winner']}  Human={result['human_pref']}")

sub_divider("Elo Rating Tournament")
elo = EloRatingSystem(k=32)
matchups = [
    ("GPT-4", "Claude-3"), ("GPT-4", "Llama-2-70B"),
    ("Claude-3", "Llama-2-70B"), ("GPT-4", "Gemini-Pro"),
    ("Claude-3", "Gemini-Pro"), ("GPT-4", "Mixtral-8x7B"),
    ("Gemini-Pro", "Mixtral-8x7B"), ("Claude-3", "Mixtral-8x7B"),
    ("GPT-4", "Llama-2-70B"), ("Gemini-Pro", "Llama-2-70B"),
]
models = ["GPT-4", "Claude-3", "Gemini-Pro", "Llama-2-70B", "Mixtral-8x7B"]
leaderboard = elo.simulate_tournament(models, matchups)
print(f"  {'Rank':<6} {'Model':<20} {'Elo':>8}")
print(f"  {'-'*6} {'-'*20} {'-'*8}")
for entry in leaderboard:
    print(f"  {entry['rank']:<6} {entry['model']:<20} {entry['elo']:>8.1f}")


# =========================================================================
# Paper 2: Bias Detection (Wang et al., 2023)
# =========================================================================
divider("PAPER 2: LLMs are not Fair Evaluators (Wang et al., 2023)")

detector = PositionBiasDetector()
bias_examples = get_position_bias_examples(data)
bias_result = detector.detect_bias(bias_examples)

print(f"\n  Total pairs tested:    {bias_result['total']}")
print(f"  Position 1 win rate:   {bias_result['position_1_rate']:.1%}")
print(f"  Bias detected:         {bias_result['bias_detected']}")
print(f"  Bias direction:        {bias_result['bias_direction']}")

for j in bias_result["judgments"]:
    print(f"    {j['id']}: original={j['original_winner']}  swapped={j['swapped_winner']}  consistent={j['consistent']}")


# =========================================================================
# Paper 3: G-Eval (Liu et al., 2023)
# =========================================================================
divider("PAPER 3: G-Eval (Liu et al., 2023)")

geval = GEvalScorer()
geval_examples = get_geval_examples(data)

for ex in geval_examples:
    result = geval.evaluate(ex["source_text"], ex["summary"])
    print(f"\n  [{ex['id']}]")
    print(f"    Source: {ex['source_text'][:70]}...")
    print(f"    Summary: {ex['summary'][:70]}...")
    print(f"    CoT steps: {len(result['chain_of_thought_steps'])} steps executed")
    scores = result["scores"]
    gt = ex["criteria"]
    print(f"    {'Criterion':<14} {'Computed':>8} {'Ground-Truth':>12}")
    for crit in ["coherence", "consistency", "fluency", "relevance"]:
        gt_key = crit if crit != "relevance" else "relevance"
        gt_score = gt.get(gt_key, gt.get("relevancy", {}) ).get("score", "?")
        print(f"    {crit:<14} {scores[crit]:>8} {gt_score:>12}")
    print(f"    {'average':<14} {scores['average']:>8}")


# =========================================================================
# Paper 4: RAGAS (Es et al., 2023)
# =========================================================================
divider("PAPER 4: RAGAS (Es et al., 2023)")

ragas = RAGASMetrics()
rag_examples = get_rag_examples(data)

print(f"\n  {'ID':<10} {'Faithfulness':>12} {'Relevancy':>10} {'Ctx-Prec':>9}  | {'GT-Faith':>9} {'GT-Rel':>7}")
print(f"  {'-'*10} {'-'*12} {'-'*10} {'-'*9}  | {'-'*9} {'-'*7}")
for ex in rag_examples:
    result = ragas.evaluate(ex["question"], ex["contexts"], ex["answer"], ex["ground_truth"])
    gt_f = ex.get("faithfulness", "?")
    gt_r = ex.get("answer_relevancy", "?")
    print(f"  {ex['id']:<10} {result['faithfulness']:>12.3f} {result['answer_relevancy']:>10.3f} "
          f"{result['context_precision']:>9.3f}  | {gt_f:>9} {gt_r:>7}")
    if ex.get("note"):
        print(f"             Note: {ex['note']}")


# =========================================================================
# Paper 5: ARES (Saad-Falcon et al., 2023)
# =========================================================================
divider("PAPER 5: ARES (Saad-Falcon et al., 2023)")

ares = ARESEvaluator(confidence_level=0.95)

labeled = [
    {"faithfulness": 1.0, "relevancy": 1.0, "completeness": 0.9},
    {"faithfulness": 0.0, "relevancy": 1.0, "completeness": 0.3},
    {"faithfulness": 1.0, "relevancy": 1.0, "completeness": 1.0},
    {"faithfulness": 0.8, "relevancy": 0.7, "completeness": 0.6},
    {"faithfulness": 0.9, "relevancy": 0.9, "completeness": 0.8},
]
unlabeled = [
    {"faithfulness": 0.85, "relevancy": 0.90, "completeness": 0.75},
    {"faithfulness": 0.78, "relevancy": 0.82, "completeness": 0.68},
    {"faithfulness": 0.92, "relevancy": 0.88, "completeness": 0.80},
    {"faithfulness": 0.70, "relevancy": 0.95, "completeness": 0.72},
    {"faithfulness": 0.88, "relevancy": 0.86, "completeness": 0.77},
    {"faithfulness": 0.82, "relevancy": 0.91, "completeness": 0.70},
    {"faithfulness": 0.75, "relevancy": 0.84, "completeness": 0.65},
    {"faithfulness": 0.90, "relevancy": 0.87, "completeness": 0.82},
    {"faithfulness": 0.80, "relevancy": 0.93, "completeness": 0.73},
    {"faithfulness": 0.86, "relevancy": 0.89, "completeness": 0.78},
]

ares_results = ares.evaluate_rag_system(labeled, unlabeled)
print(f"\n  Labeled samples: {len(labeled)},  Unlabeled samples: {len(unlabeled)}")
print(f"\n  {'Metric':<15} {'PPI Estimate':>12} {'95% CI Lower':>13} {'95% CI Upper':>13} {'Labeled Mean':>13}")
print(f"  {'-'*15} {'-'*12} {'-'*13} {'-'*13} {'-'*13}")
for metric, vals in ares_results.items():
    print(f"  {metric:<15} {vals['ppi_estimate']:>12.4f} {vals['ci_lower']:>13.4f} "
          f"{vals['ci_upper']:>13.4f} {vals['labeled_mean']:>13.4f}")


# =========================================================================
# Paper 6: AgentBench (Liu et al., 2023)
# =========================================================================
divider("PAPER 6: AgentBench (Liu et al., 2023)")

agent_scorer = AgentBenchScorer()
agent_examples = get_agent_examples(data)
agent_results = agent_scorer.score_across_environments(agent_examples)

print(f"\n  {'ID':<12} {'Env':<10} {'Done':>5} {'Steps':>6} {'Optimal':>8} {'Efficiency':>10} {'Accuracy':>9} {'Overall':>8}")
print(f"  {'-'*12} {'-'*10} {'-'*5} {'-'*6} {'-'*8} {'-'*10} {'-'*9} {'-'*8}")
for t in agent_results["trajectories"]:
    print(f"  {t['id']:<12} {t['environment']:<10} {str(t['completed']):>5} {t['steps_taken']:>6} "
          f"{t['optimal_steps']:>8} {t['efficiency']:>10.3f} {t['accuracy']:>9.3f} {t['overall_score']:>8.3f}")

print(f"\n  Environment Summary:")
for env, summary in agent_results["environment_summary"].items():
    print(f"    {env}: count={summary['count']}, avg={summary['avg_score']:.3f}, "
          f"range=[{summary['min_score']:.3f}, {summary['max_score']:.3f}]")


# =========================================================================
# Paper 7: SWE-Bench (Jimenez et al., 2023)
# =========================================================================
divider("PAPER 7: SWE-Bench (Jimenez et al., 2023)")

swe_scorer = SWEBenchScorer()
swe_examples = get_swe_bench_examples(data)
swe_results = swe_scorer.evaluate_models(swe_examples)

print(f"\n  {'Model':<20} {'Solved':>7} {'Total':>6} {'Pass@1':>8}")
print(f"  {'-'*20} {'-'*7} {'-'*6} {'-'*8}")
for model in sorted(swe_results.keys()):
    r = swe_results[model]
    print(f"  {model:<20} {r['solved']:>7} {r['total']:>6} {r['pass_at_1']:>8.3f}")

sub_divider("Pass@k Demonstration")
for n, c in [(10, 3), (10, 5), (10, 1), (50, 10)]:
    for k in [1, 5, 10]:
        if k <= n:
            val = SWEBenchScorer.pass_at_k(n, c, k)
            print(f"    n={n}, c={c}, k={k}  =>  pass@{k} = {val:.4f}")


# =========================================================================
# Paper 8: Calibration (Various, 2023-2024)
# =========================================================================
divider("PAPER 8: Calibrating LLM-Based Evaluators")

calibrator = CalibratedJudge()
cal_examples = get_calibration_examples(data)
cal_result = calibrator.expected_calibration_error(cal_examples)

print(f"\n  ECE = {cal_result['ece']:.4f}  ({cal_result['interpretation']})")
print(f"\n  {'Bin':<12} {'Count':>6} {'Avg Conf':>9} {'Avg Acc':>8} {'Gap':>6}")
print(f"  {'-'*12} {'-'*6} {'-'*9} {'-'*8} {'-'*6}")
for b in cal_result["bin_details"]:
    print(f"  {b['bin']:<12} {b['count']:>6} {b['avg_confidence']:>9.3f} {b['avg_accuracy']:>8.3f} {b['gap']:>6.3f}")

sub_divider("Individual Predictions")
print(f"  {'ID':<10} {'True':>5} {'Pred':>5} {'Conf':>6} {'Agree':>6}")
for ex in cal_examples:
    print(f"  {ex['id']:<10} {ex['true_label']:>5} {ex['judge_prediction']:>5} "
          f"{ex['judge_confidence']:>6.2f} {str(ex['human_agreement']):>6}")


# =========================================================================
# Paper 9: Reflexion (Shinn et al., 2023)
# =========================================================================
divider("PAPER 9: Reflexion (Shinn et al., 2023)")

reflexion = ReflexionLoop()
refl_examples = get_reflexion_examples(data)

for ex in refl_examples:
    analysis = reflexion.run_reflexion(ex)
    print(f"\n  Task: {analysis['task']}")
    print(f"  Ground truth: {analysis['ground_truth']}")
    print(f"  Total attempts: {analysis['total_attempts']}")
    print(f"  Solved: {analysis['solved']} (at attempt {analysis['solved_at_attempt']})")
    print(f"  Improvement shown: {analysis['improvement_shown']}")
    for att in analysis["attempts_detail"]:
        status = "CORRECT" if att["correct"] else "WRONG"
        print(f"    Attempt {att['attempt']}: {att['answer']} [{status}]")
        print(f"      Reflection: {att['reflection_summary']}")

sub_divider("Simulated Reflexion")
sim = reflexion.simulate_reflexion(
    problem="What is 15 * 13?",
    initial_answer=185,
    correct_answer=195,
    max_attempts=3,
)
print(f"  Problem: {sim['problem']}")
print(f"  Attempts: {sim['total_attempts']}, Solved: {sim['solved']}")
for att in sim["attempts"]:
    print(f"    Attempt {att['attempt']}: answer={att['answer']} correct={att['correct']}")
    print(f"      {att['reflection']}")


# =========================================================================
# Paper 10: Meta-Evaluation Research
# =========================================================================
divider("PAPER 10: Meta-Evaluation Research")

meta = MetaEvaluator()
meta_examples = get_meta_evaluation_examples(data)

print(f"\n  {'Evaluator':<20} {'Agree%':>7} {'Kappa':>7} {'Spearman':>9} {'Bias':>18}")
print(f"  {'-'*20} {'-'*7} {'-'*7} {'-'*9} {'-'*18}")
for ex in meta_examples:
    result = meta.evaluate(ex["evaluator"], ex["human_scores"], ex["judge_scores"])
    print(f"  {result['evaluator']:<20} {result['agreement_rate']:>7.2%} {result['cohens_kappa']:>7.4f} "
          f"{result['spearmans_rho']:>9.4f} {result['bias']['bias_direction']:>18}")

sub_divider("Detailed Bias Analysis")
for ex in meta_examples:
    result = meta.evaluate(ex["evaluator"], ex["human_scores"], ex["judge_scores"])
    bias = result["bias"]
    print(f"  {ex['evaluator']}: human_mean={bias['human_mean']}, judge_mean={bias['judge_mean']}, "
          f"diff={bias['mean_difference']:+.3f}")


# =========================================================================
# Comparison Table
# =========================================================================
divider("COMPARISON TABLE: Paper Techniques")

papers = [
    ("MT-Bench / LLM-as-Judge", "Pairwise + Elo",      "Multi-turn",   "Ranking models",           "Human pref needed"),
    ("Unfair Evaluators",       "Swap test",            "Pairwise",     "Detect bias",              "Only finds bias"),
    ("G-Eval",                  "CoT + form-fill",      "Pointwise",    "NLG quality",              "Prompt-sensitive"),
    ("RAGAS",                   "Claim decomposition",  "Component",    "RAG pipelines",            "Heuristic claims"),
    ("ARES",                    "PPI + confidence",     "Statistical",  "RAG with few labels",      "Needs some labels"),
    ("AgentBench",              "Trajectory scoring",   "Multi-env",    "Agent capabilities",       "Env-specific"),
    ("SWE-Bench",               "Pass@k",              "Execution",    "Code repair",              "Binary pass/fail"),
    ("Calibration",             "ECE bins",            "Reliability",  "Judge trustworthiness",    "Needs ground truth"),
    ("Reflexion",               "Reflect + retry",     "Iterative",    "Self-improvement",         "Extra compute"),
    ("Meta-Evaluation",         "Kappa/Spearman",      "Agreement",    "Evaluator reliability",    "Needs human refs"),
]

print(f"\n  {'Paper':<24} {'Technique':<20} {'Type':<12} {'Best For':<22} {'Limitation'}")
print(f"  {'-'*24} {'-'*20} {'-'*12} {'-'*22} {'-'*20}")
for paper, technique, eval_type, best_for, limitation in papers:
    print(f"  {paper:<24} {technique:<20} {eval_type:<12} {best_for:<22} {limitation}")


# =========================================================================
# Train.csv Integration Demo
# =========================================================================
divider("BONUS: Train.csv MCQA Evaluation Demo")

train_rows = load_train_csv(limit=3)
if train_rows:
    geval_mcqa = GEvalScorer()
    for row in train_rows:
        prompt = row["prompt"]
        correct = row["answer"]
        options = {k: row[k] for k in ["A", "B", "C", "D", "E"] if row.get(k)}
        print(f"\n  Q{row['id']}: {prompt[:80]}...")
        print(f"  Correct answer: {correct}")

        best_option, best_score = "", 0
        for opt_key, opt_text in options.items():
            rel = geval_mcqa.score_relevance(prompt, opt_text)
            if rel > best_score:
                best_score = rel
                best_option = opt_key
            marker = " <-- correct" if opt_key == correct else ""
            print(f"    {opt_key}: relevance={rel}  (first 60 chars: {opt_text[:60]}...){marker}")
        print(f"  Highest scoring option: {best_option} (score={best_score})")


divider("CHAPTER 12 COMPLETE")
print("All 10 paper techniques demonstrated.\n")
