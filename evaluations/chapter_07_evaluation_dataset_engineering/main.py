"""
Chapter 7 - Evaluation Dataset Engineering
Benchmark design, dataset quality, coverage, contamination,
label noise, Cohen's/Fleiss' Kappa, and meta-evaluation.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json
import random
from collections import Counter

from dataset import (
    load_sample_data,
    detect_topic,
    estimate_difficulty,
    analyze_answer_distribution,
    analyze_topic_coverage,
    analyze_difficulty_distribution,
    analyze_prompt_lengths,
    find_duplicates,
    simulate_llm_predictions,
    generate_annotator_labels,
)
from evaluator import (
    BenchmarkDesigner,
    DatasetQualityChecker,
    CoverageAnalyzer,
    ContaminationDetector,
    LabelNoiseDetector,
    CohenKappaCalculator,
    FleissKappaCalculator,
    MetaEvaluator,
)


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)

def sub(title: str) -> None:
    print(f"\n--- {title} ---")

def dump(obj, indent: int = 2) -> None:
    def _trim(o, depth=0):
        if isinstance(o, dict):
            return {k: _trim(v, depth + 1) for k, v in o.items()}
        if isinstance(o, list):
            if len(o) > 8 and depth > 1:
                return o[:4] + [f"... ({len(o)} items total)"]
            return [_trim(v, depth + 1) for v in o]
        return o
    print(json.dumps(_trim(obj), indent=indent, default=str))


# ============================================================================
# Load data
# ============================================================================
banner("LOADING SAMPLE DATA")
data = load_sample_data()
questions = data["questions"]
contamination_test = data["contamination_test_set"]
fleiss_annotations = data["annotation_simulation"]["annotations"]
fleiss_categories = data["annotation_simulation"]["categories"]
print(f"Loaded {len(questions)} questions, "
      f"{len(contamination_test)} contamination-test items, "
      f"{len(fleiss_annotations)} annotation rows for Fleiss' Kappa")

# ============================================================================
# 1. BENCHMARK DESIGN
# ============================================================================
banner("1. BENCHMARK DESIGN")
designer = BenchmarkDesigner(
    questions=questions, topic_fn=detect_topic, difficulty_fn=estimate_difficulty,
)
benchmark = designer.design_benchmark(
    target_size=15,
    difficulty_distribution={"easy": 0.4, "medium": 0.4, "hard": 0.2},
    seed=42,
)
sub("Benchmark metadata")
dump(benchmark["metadata"])
sub("Benchmark validation")
dump(designer.validate_benchmark(benchmark))

# ============================================================================
# 2. DATASET QUALITY CHECKS
# ============================================================================
banner("2. DATASET QUALITY CHECKS")
checker = DatasetQualityChecker(questions)
quality = checker.run_all_checks()

sub("Overall quality")
print(f"  Score : {quality['overall_quality_score']}")
print(f"  Grade : {quality['grade']}")
print(f"  Issues: {quality['total_issues']}")

sub("Completeness")
comp = quality["completeness"]
print(f"  Score : {comp['completeness_score']}")
print(f"  Issues: {comp['issues_found']}")
for issue in comp["issues"][:5]:
    print(f"    [{issue['severity']}] id={issue['id']}: {issue['issue']}")

sub("Correctness")
corr = quality["correctness"]
print(f"  Issues: {corr['issues_found']}")
for issue in corr["issues"][:5]:
    print(f"    [{issue['severity']}] id={issue['id']}: {issue['issue']}")

sub("Consistency")
cons = quality["consistency"]
print(f"  Issues: {cons['issues_found']}")
print(f"  Prompt lengths: {cons['prompt_length_stats']}")

# ============================================================================
# 3. COVERAGE METRICS
# ============================================================================
banner("3. COVERAGE METRICS")
coverage_analyzer = CoverageAnalyzer(
    questions=questions, topic_fn=detect_topic, difficulty_fn=estimate_difficulty,
)
expected_topics = ["physics", "chemistry", "biology", "astronomy",
                   "mathematics", "earth_science"]
overall_cov = coverage_analyzer.overall_coverage(expected_topics)

sub("Overall coverage score")
print(f"  {overall_cov['overall_coverage_score']}")

sub("Topic coverage")
tc = overall_cov["topic_coverage"]
print(f"  Ratio    : {tc['coverage_ratio']}")
print(f"  Entropy  : {tc['normalized_entropy']} ({tc['interpretation']})")
print(f"  Covered  : {tc['covered_topics']}")
print(f"  Missing  : {tc['missing_topics']}")
print(f"  Counts   : {tc['topic_counts']}")

sub("Difficulty coverage")
dc = overall_cov["difficulty_coverage"]
print(f"  Ratio: {dc['coverage_ratio']}")
for level, info in dc["distribution"].items():
    print(f"    {level:8s}: {info['count']} ({info['percentage']}%)")

sub("Answer coverage")
ac = overall_cov["answer_coverage"]
print(f"  Ratio   : {ac['coverage_ratio']}")
print(f"  Balance : {ac['balance_score']}")
print(f"  Counts  : {ac['counts']}")
print(f"  Missing : {ac['missing']}")

# ============================================================================
# 4. FAILURE-MODE COVERAGE & DATASET BALANCING
# ============================================================================
banner("4. FAILURE-MODE COVERAGE & DATASET BALANCING")

sub("Duplicate detection")
dupes = find_duplicates(questions, threshold=0.6)
print(f"  Found {len(dupes)} near-duplicates (Jaccard >= 0.6):")
for d in dupes:
    print(f"    ids ({d['id_1']}, {d['id_2']}): similarity={d['similarity']}")
    print(f"      Q1: {d['prompt_1']}")
    print(f"      Q2: {d['prompt_2']}")

sub("Answer distribution analysis")
ans_dist = analyze_answer_distribution(questions)
print(f"  Total: {ans_dist['total']}, Expected: {ans_dist['expected_pct_if_balanced']}%")
print(f"  Max deviation: {ans_dist['max_deviation_from_expected']}%, Chi-sq: {ans_dist['chi_squared']}")
for label, info in ans_dist["distribution"].items():
    bar = "#" * int(info["percentage"] / 2)
    print(f"    {label}: {info['count']:2d} ({info['percentage']:5.1f}%)  {bar}")

sub("Prompt length analysis")
wl = analyze_prompt_lengths(questions)["word_lengths"]
print(f"  Words -> min={wl['min']}, max={wl['max']}, "
      f"mean={wl['mean']}, median={wl['median']}, std={wl['std']}")

# ============================================================================
# 5. CONTAMINATION DETECTION & DATA LEAKAGE
# ============================================================================
banner("5. CONTAMINATION DETECTION & DATA LEAKAGE")
detector = ContaminationDetector(train_data=questions, test_data=contamination_test)
report = detector.full_contamination_report(near_dup_threshold=0.5)

sub("Contamination summary")
print(f"  Rate: {report['contamination_rate']}, Risk: {report['risk_level']}")
print(f"  Exact: {len(report['exact_matches'])}, Near-dupes: {len(report['near_duplicates'])}")

for m in report["exact_matches"]:
    print(f"    test_id={m['test_id']} <-> train_id={m['train_id']}  [{m['severity']}]")
for m in report["near_duplicates"]:
    print(f"    test_id={m['test_id']} <-> train_id={m['train_id']}  score={m['combined_score']}")

sub("Answer leakage analysis")
leak = report["answer_leakage_analysis"]
print(f"  Train dist: {leak['train_distribution']}")
print(f"  Test dist : {leak['test_distribution']}")

# ============================================================================
# 6. LABEL NOISE DETECTION
# ============================================================================
banner("6. LABEL NOISE DETECTION")
annotator_labels = [q.get("annotator_labels", []) for q in questions]
noise_detector = LabelNoiseDetector(questions)

sub("Noise rate estimate (annotator disagreement)")
noise_rate = noise_detector.estimate_noise_rate(annotator_labels)
dump(noise_rate)

sub("Suspicious items (annotator disagreement)")
suspicious = noise_detector.detect_by_annotator_disagreement(
    annotator_labels, disagreement_threshold=0.5,
)
for s in suspicious:
    print(f"  id={s['id']}: ground_truth={s['ground_truth']}, "
          f"majority={s['majority_vote']}, dist={s['label_distribution']}")
if not suspicious:
    print("  None found at threshold=0.5")

sub("Suspicious items (model consensus)")
model_preds = [
    simulate_llm_predictions(questions, accuracy=0.85, seed=10),
    simulate_llm_predictions(questions, accuracy=0.80, seed=20),
    simulate_llm_predictions(questions, accuracy=0.75, seed=30),
]
model_suspicious = noise_detector.detect_by_model_consensus(
    model_preds, consensus_threshold=0.66,
)
for s in model_suspicious[:5]:
    print(f"  id={s['id']}: ground_truth={s['ground_truth']}, "
          f"models_say={s['model_consensus']}, "
          f"rate={s['consensus_rate']}, votes={s['model_votes']}")
if not model_suspicious:
    print("  No model-consensus noise detected")

# ============================================================================
# 7. COHEN'S KAPPA (from scratch)
# ============================================================================
banner("7. COHEN'S KAPPA -- Inter-Rater Agreement (2 Raters)")

sub("Scenario A: Two annotators on our 20 questions")
rater_1 = [q["ground_truth"] for q in questions]
rater_2 = simulate_llm_predictions(questions, accuracy=0.80, seed=99)
cohen_result = CohenKappaCalculator.compute(rater_1, rater_2)
print(f"  Kappa: {cohen_result['kappa']}, Observed: {cohen_result['observed_agreement']}, "
      f"Expected: {cohen_result['expected_agreement']}, {cohen_result['interpretation']}")

sub("Scenario B: Perfect agreement")
perfect = CohenKappaCalculator.compute(rater_1, rater_1)
print(f"  Kappa = {perfect['kappa']}  ({perfect['interpretation']})")

sub("Scenario C: Near-random agreement")
random_rater = [random.choice(["A", "B", "C"]) for _ in rater_1]
rand_result = CohenKappaCalculator.compute(rater_1, random_rater)
print(f"  Kappa = {rand_result['kappa']}  ({rand_result['interpretation']})")

# ============================================================================
# 8. FLEISS' KAPPA (from scratch)
# ============================================================================
banner("8. FLEISS' KAPPA -- Inter-Rater Agreement (Multiple Raters)")

sub("Scenario A: 5 raters on 10 items (from sample_data)")
fleiss_result = FleissKappaCalculator.compute(fleiss_annotations, categories=fleiss_categories)
print(f"  Kappa: {fleiss_result['kappa']}, P_bar: {fleiss_result['p_bar']}, "
      f"P_e_bar: {fleiss_result['p_e_bar']}, {fleiss_result['interpretation']}")
for cat, prop in fleiss_result["category_proportions"].items():
    print(f"    {cat:20s}: {prop}")

sub("Scenario B: 3 annotators on our 20 questions")
ann_labels = generate_annotator_labels(questions, n_annotators=3, agreement_rate=0.85, seed=7)
fleiss_q = FleissKappaCalculator.compute(ann_labels)
print(f"  Kappa: {fleiss_q['kappa']}  ({fleiss_q['interpretation']})")

sub("Scenario C: Perfect agreement")
perfect_ann = [[q["ground_truth"]] * 4 for q in questions]
fleiss_perf = FleissKappaCalculator.compute(perfect_ann)
print(f"  Kappa = {fleiss_perf['kappa']}  ({fleiss_perf['interpretation']})")

# ============================================================================
# 9. META-EVALUATION -- Evaluating the Evaluator
# ============================================================================
banner("9. META-EVALUATION")
meta = MetaEvaluator(
    quality_checker=checker, coverage_analyzer=coverage_analyzer,
    label_noise_detector=noise_detector,
)
scorecard = meta.evaluate(annotations=annotator_labels, expected_topics=expected_topics)

sub("Scorecard")
print(f"  Overall: {scorecard['overall_score']} (Grade {scorecard['overall_grade']})")
for dim, info in scorecard["dimensions"].items():
    print(f"  {dim:16s}: {info['score']}")

sub("Recommendations")
for rec in scorecard["recommendations"]:
    print(f"  - {rec}")

sub("Evaluator reliability check")

def mock_evaluator(qs, seed):
    preds = simulate_llm_predictions(qs, accuracy=0.75, seed=seed)
    correct = sum(1 for p, q in zip(preds, qs) if p == q["ground_truth"])
    return correct / max(len(qs), 1)

reliability = meta.evaluator_reliability_check(
    questions=questions, evaluator_fn=mock_evaluator, n_runs=10, seed_start=0,
)
print(f"  Mean: {reliability['mean']}, Std: {reliability['std_dev']}, "
      f"CV: {reliability['coefficient_of_variation']}")
print(f"  Reliable: {reliability['is_reliable']}, {reliability['interpretation']}")

# ============================================================================
# SUMMARY TABLE
# ============================================================================
banner("SUMMARY")
rows = [
    ("Dataset quality score",       f"{quality['overall_quality_score']}"),
    ("Dataset quality grade",       quality["grade"]),
    ("Coverage score",              f"{overall_cov['overall_coverage_score']}"),
    ("Topic coverage",              f"{tc['coverage_ratio']}"),
    ("Difficulty coverage",         f"{dc['coverage_ratio']}"),
    ("Answer balance",              f"{ac['balance_score']}"),
    ("Contamination rate",          f"{report['contamination_rate']}"),
    ("Label noise rate",            f"{noise_rate['estimated_noise_rate']}"),
    ("Cohen's Kappa (2 raters)",    f"{cohen_result['kappa']}"),
    ("Fleiss' Kappa (5 raters)",    f"{fleiss_result['kappa']}"),
    ("Meta-eval overall",           f"{scorecard['overall_score']}"),
    ("Evaluator reliability (CV)",  f"{reliability['coefficient_of_variation']}"),
]
print(f"\n  {'Metric':<30s}  {'Value':>10s}")
print(f"  {'-'*30}  {'-'*10}")
for label, val in rows:
    print(f"  {label:<30s}  {val:>10s}")

print("\nDone.")
