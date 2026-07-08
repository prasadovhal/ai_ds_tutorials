"""
Chapter 6 - Golden Dataset Engineering
=======================================
Run: python main.py

Topics:
  1. Why golden datasets & dataset types comparison
  2. Creating from sources, sampling, deduplication, balancing
  3. Annotation workflow, rubrics, inter-annotator agreement
  4. Using for regression testing & prompt comparison
  5. Versioning, drift detection, maintenance
  6. Synthetic data generation
  7. Full quality evaluation
"""

import sys
import io
import json
import random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from dataset import (
    load_sample_data,
    GoldenDatasetBuilder,
    AnnotationManager,
    DatasetVersionManager,
    SyntheticDataGenerator,
)
from evaluator import (
    CoverageAnalyzer,
    BalanceChecker,
    DuplicateDetector,
    IAACalculator,
    DatasetQualityScorer,
    DriftDetector,
    RegressionComparator,
    MaintenanceTracker,
)


def print_section(title: str):
    print("\n")
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_json(data, indent=2):
    print(json.dumps(data, indent=indent, default=str))


# ===================================================================
# SECTION 1: WHY GOLDEN DATASETS & DATASET TYPES
# ===================================================================

def demo_why_golden_datasets():
    print_section("1. WHY GOLDEN DATASETS & DATASET TYPES")

    sample = load_sample_data()
    meta = sample["metadata"]
    stats = sample["dataset_statistics"]

    print(f"  Loaded golden dataset: v{meta['version']}")
    print(f"    Items: {meta['total_items']}")
    print(f"    Domain: {meta['domain']}")
    print(f"    Quality tier: {meta['quality_tier']}")
    print(f"    Categories: {json.dumps(stats['category_distribution'])}")
    print(f"    Difficulties: {json.dumps(stats['difficulty_distribution'])}")
    print(f"    Edge cases: {stats['edge_case_count']}")
    print(f"    Avg annotator agreement: {stats['avg_annotator_agreement']}")


# ===================================================================
# SECTION 2: CREATING FROM SOURCES, SAMPLING, DEDUP, BALANCING
# ===================================================================

def demo_dataset_creation():
    print_section("2. CREATING: SAMPLING, DEDUPLICATION, BALANCING")

    builder = GoldenDatasetBuilder(name="science_golden_v1", seed=42)

    sample = load_sample_data()
    source_items = []
    for item in sample["items"]:
        source_items.append({
            "id": item["source_id"],
            "prompt": item["prompt"],
            "choices": item["choices"],
            "ground_truth": item["ground_truth"],
        })

    print(f"  Source items: {len(source_items)}")

    # --- Categorization ---
    categorized = builder.categorize_questions(source_items)
    print(f"\n  --- CATEGORIZATION ---")
    for cat, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
        print(f"    {cat:<15s}: {len(items)} items")

    # --- Difficulty Estimation ---
    print(f"\n  --- DIFFICULTY ESTIMATION ---")
    for q in source_items[:5]:
        diff = builder.estimate_difficulty(q)
        print(f"    Q{q['id']}: {diff:<8s} | {q['prompt'][:55]}...")

    # --- Deduplication ---
    dedup = builder.deduplicate(source_items, threshold=0.8)
    print(f"\n  --- DEDUPLICATION ---")
    print(f"    Original: {dedup['original_count']}")
    print(f"    After dedup: {dedup['unique_count']}")
    print(f"    Duplicates removed: {dedup['duplicates_found']}")

    # --- Stratified Sampling ---
    for q in source_items:
        if "category" not in q:
            q["category"] = "general"
    sampled = builder.stratified_sample(source_items, n=10, stratify_by="category")
    print(f"\n  --- STRATIFIED SAMPLING ---")
    print(f"    Requested: 10, Got: {len(sampled)}")
    cat_counts = {}
    for s in sampled:
        cat_counts[s.get("category", "?")] = cat_counts.get(s.get("category", "?"), 0) + 1
    print(f"    Category distribution: {json.dumps(cat_counts)}")

    # --- Balancing ---
    balance_result = builder.balance_categories(source_items, target_per_category=3)
    print(f"\n  --- CATEGORY BALANCING ---")
    print(f"    Before: {balance_result['total_before']}")
    print(f"    After: {balance_result['total_after']}")
    for cat, info in balance_result["balance_report"].items():
        print(f"    {cat:<15s}: {info['original']} -> {info['after_balancing']} ({info['action']})")

    # --- Edge Cases ---
    edge_result = builder.identify_edge_cases(source_items)
    print(f"\n  --- EDGE CASE DETECTION ---")
    print(f"    Edge cases: {edge_result['edge_case_count']}")
    print(f"    Normal: {edge_result['normal_count']}")
    print(f"    Edge ratio: {edge_result['edge_case_ratio']:.1%}")
    for ec in edge_result["edge_cases"][:3]:
        print(f"    Q{ec['id']}: reasons={ec['edge_case_reasons']}")


# ===================================================================
# SECTION 3: ANNOTATION WORKFLOW, RUBRICS, IAA
# ===================================================================

def demo_annotation_workflow():
    print_section("3. ANNOTATION WORKFLOW, RUBRICS, INTER-ANNOTATOR AGREEMENT")

    # --- Annotation Guidelines ---
    ann_mgr = AnnotationManager(num_annotators=3, seed=42)
    guidelines = ann_mgr.create_annotation_guidelines()

    print("  --- ANNOTATION RUBRIC ---")
    for level, desc in guidelines["rubric"].items():
        print(f"    {level}: {desc}")

    # --- Simulate Annotations ---
    sample = load_sample_data()
    questions = []
    for item in sample["items"][:10]:
        questions.append({
            "id": item["source_id"],
            "prompt": item["prompt"],
            "choices": item["choices"],
            "ground_truth": item["ground_truth"],
        })

    ann_result = ann_mgr.simulate_annotations(
        questions,
        annotator_accuracies=[0.92, 0.87, 0.85],
    )

    print(f"\n  --- SIMULATED ANNOTATIONS ---")
    print(f"    Items annotated: {ann_result['total_items']}")
    print(f"    Annotators: {ann_result['num_annotators']}")
    print(f"    Unanimous agreement: {ann_result['unanimous_agreement']}/{ann_result['total_items']}")
    print(f"    Unanimous rate: {ann_result['unanimous_rate']:.1%}")
    print(f"    Consensus accuracy: {ann_result['consensus_accuracy']:.1%}")

    # Show example annotation
    example = ann_result["annotations"][0]
    print(f"\n  Example (Q{example['question_id']}):")
    print(f"    Ground truth: {example['ground_truth']}")
    for ann_id, data in example["annotator_labels"].items():
        match = "Y" if data["label"] == example["ground_truth"] else "N"
        print(f"    {ann_id}: label={data['label']} conf={data['confidence']:.2f} "
              f"time={data['time_seconds']:.0f}s correct={match}")
    print(f"    Consensus: {example['consensus']['label']} "
          f"({example['consensus']['agreement_count']}/{example['consensus']['total_annotators']})")

    # --- Cohen's Kappa ---
    print(f"\n  --- COHEN'S KAPPA (Pairwise) ---")
    kappa_result = ann_mgr.compute_all_pairwise_kappa()
    for pair, result in kappa_result["pairwise_kappas"].items():
        print(f"    {pair}: kappa={result['cohens_kappa']:.4f} ({result['interpretation']})")
    print(f"    Average kappa: {kappa_result['average_kappa']:.4f}")

    # --- IAA from golden dataset (sample_data.json) ---
    print(f"\n  --- IAA FROM GOLDEN DATASET (sample_data.json) ---")
    iaa = IAACalculator()
    iaa_result = iaa.analyze_from_golden_items(sample["items"])

    fleiss = iaa_result["fleiss_kappa"]
    print(f"    Fleiss' Kappa: {fleiss['fleiss_kappa']:.4f} ({fleiss['interpretation']})")
    print(f"    Items: {iaa_result['num_items']}, Annotators: {iaa_result['num_annotators']}")

    for pair, result in iaa_result["pairwise_kappa"]["pairwise_results"].items():
        print(f"    {pair}: kappa={result['cohens_kappa']:.4f} ({result['interpretation']})")

    # --- Quality Control Report ---
    print(f"\n  --- ANNOTATOR QUALITY CONTROL ---")
    qc = ann_mgr.quality_control_report()
    for ann_id, stats in qc["annotator_performance"].items():
        print(f"    {ann_id}: accuracy={stats['accuracy']:.1%} "
              f"avg_conf={stats['avg_confidence']:.2f} "
              f"avg_time={stats['avg_time_seconds']:.0f}s")
    print(f"    Items needing review: {len(qc['items_needing_review'])} "
          f"({qc['review_rate']:.1%})")


# ===================================================================
# SECTION 4: REGRESSION TESTING & PROMPT COMPARISON
# ===================================================================

def demo_regression_testing():
    print_section("4. REGRESSION TESTING & PROMPT COMPARISON")

    sample = load_sample_data()
    items = sample["items"]
    choices = ["A", "B", "C", "D", "E"]

    # Simulate two model versions
    preds_v1 = []
    preds_v2 = []
    r1 = random.Random(100)
    r2 = random.Random(200)
    for item in items:
        gt = item["ground_truth"]
        if r1.random() < 0.73:
            preds_v1.append(gt)
        else:
            preds_v1.append(r1.choice([c for c in choices if c != gt]))
        if r2.random() < 0.87:
            preds_v2.append(gt)
        else:
            preds_v2.append(r2.choice([c for c in choices if c != gt]))

    comparator = RegressionComparator()
    result = comparator.compare_predictions(
        items, preds_v1, preds_v2,
        label_a="prompt_v1", label_b="prompt_v2",
    )

    print(f"  --- MODEL COMPARISON ---")
    print(f"    prompt_v1 accuracy: {result['prompt_v1']['accuracy']:.1%} ({result['prompt_v1']['correct']}/{result['total_items']})")
    print(f"    prompt_v2 accuracy: {result['prompt_v2']['accuracy']:.1%} ({result['prompt_v2']['correct']}/{result['total_items']})")
    print(f"    Delta: {result['delta']:+.1%}")
    print(f"    Is regression: {result['is_regression']}")
    print(f"    Regressions (v1 right, v2 wrong): {result['regressions']['count']}")
    print(f"    Improvements (v1 wrong, v2 right): {result['improvements']['count']}")
    print(f"    Stable correct: {result['stable_correct']}")
    print(f"    Stable wrong: {result['stable_wrong']}")

    if result["regressions"]["items"]:
        print(f"\n  Regressed items:")
        for reg in result["regressions"]["items"][:3]:
            print(f"    {reg['id']}: gt={reg['ground_truth']} "
                  f"v1={reg['prompt_v1_pred']} v2={reg['prompt_v2_pred']} "
                  f"cat={reg['category']}")

    print(f"\n  Per-category comparison:")
    for cat, data in result["per_category"].items():
        bar_a = "#" * int(data["prompt_v1_accuracy"] * 20)
        bar_b = "#" * int(data["prompt_v2_accuracy"] * 20)
        print(f"    {cat:<15s} v1={data['prompt_v1_accuracy']:.0%} |{bar_a:<20s}|")
        print(f"    {'':<15s} v2={data['prompt_v2_accuracy']:.0%} |{bar_b:<20s}| delta={data['delta']:+.0%}")

    # --- Prompt Comparison ---
    print(f"\n  --- PROMPT STRATEGY COMPARISON ---")
    prompt_result = comparator.compare_prompts(
        items,
        prompt_configs={
            "zero_shot":    {"accuracy": 0.65, "seed": 10},
            "few_shot":     {"accuracy": 0.78, "seed": 20},
            "chain_of_thought": {"accuracy": 0.85, "seed": 30},
            "self_consistency":  {"accuracy": 0.88, "seed": 40},
        },
        seed=42,
    )

    print(f"    Ranking:")
    for entry in prompt_result["ranking"]:
        bar = "#" * int(entry["accuracy"] * 30)
        print(f"    #{entry['rank']} {entry['name']:<20s} {entry['accuracy']:.1%} |{bar}|")
    print(f"    Best: {prompt_result['best_prompt']}")
    print(f"    Spread: {prompt_result['spread']:.1%}")


# ===================================================================
# SECTION 5: VERSIONING, DRIFT DETECTION, MAINTENANCE
# ===================================================================

def demo_versioning_and_maintenance():
    print_section("5. VERSIONING, DRIFT DETECTION, MAINTENANCE")

    sample = load_sample_data()

    # --- Versioning ---
    ver_mgr = DatasetVersionManager("science_golden")

    v1_items = sample["items"][:10]
    v1_result = ver_mgr.create_version("1.0.0", v1_items, author="team_lead",
                                       description="Initial golden dataset")

    # Simulate v2: modify some items, add new ones
    v2_items = sample["items"][:8]
    for item in sample["items"][10:13]:
        v2_items.append(item)
    import copy
    v2_items_copy = copy.deepcopy(v2_items)
    if v2_items_copy:
        v2_items_copy[0]["ground_truth"] = "E"

    v2_result = ver_mgr.create_version("2.0.0", v2_items_copy, author="reviewer",
                                       description="Corrected labels, added items")

    print(f"  --- VERSION HISTORY ---")
    for v in ver_mgr.get_version_history():
        print(f"    v{v['version']} | {v['date']} | {v['item_count']} items | "
              f"hash={v['hash']} | {v['description']}")

    # --- Version Diff ---
    diff = ver_mgr.compute_diff("1.0.0", "2.0.0")
    print(f"\n  --- VERSION DIFF (1.0.0 -> 2.0.0) ---")
    print(f"    Summary: {diff['summary']}")
    print(f"    Added: {diff['added_count']}")
    print(f"    Removed: {diff['removed_count']}")
    print(f"    Modified: {diff['modified_count']}")
    print(f"    Unchanged: {diff['unchanged_count']}")
    if diff["modifications"]:
        for mod in diff["modifications"][:3]:
            print(f"    Changed: {mod['id']} {mod['field']}: {mod['old']} -> {mod['new']}")

    # --- Drift Detection ---
    print(f"\n  --- DRIFT DETECTION ---")
    drift = DriftDetector()

    baseline = sample["items"]
    drifted = []
    rng = random.Random(42)
    for item in sample["items"]:
        new_item = dict(item)
        if rng.random() < 0.3:
            new_item["category"] = rng.choice(["physics", "biology", "chemistry"])
        if rng.random() < 0.2:
            new_item["difficulty"] = rng.choice(["easy", "medium", "hard"])
        drifted.append(new_item)

    drift_result = drift.detect_drift(baseline, drifted)
    print(f"    Overall drift: {drift_result['overall_drift']:.4f}")
    print(f"    Severity: {drift_result['severity']}")
    print(f"    Needs update: {drift_result['needs_update']}")
    print(f"    Category drift: {drift_result['category_drift']['distance']:.4f}")
    print(f"    Difficulty drift: {drift_result['difficulty_drift']['distance']:.4f}")
    print(f"    Answer drift: {drift_result['answer_drift']['distance']:.4f}")

    # --- Maintenance Tracker ---
    print(f"\n  --- MAINTENANCE TRACKING ---")
    tracker = MaintenanceTracker()
    tracker.add_checkpoint("1.0.0", "2026-01-15", 0.72, 10, "Initial release")
    tracker.add_checkpoint("1.1.0", "2026-02-10", 0.78, 12, "Added biology items")
    tracker.add_checkpoint("1.2.0", "2026-03-05", 0.82, 14, "Fixed labels")
    tracker.add_checkpoint("2.0.0", "2026-04-01", 0.85, 15, "Major revision")

    health = tracker.get_health_report()
    print(f"    Current version: {health['current_version']}")
    print(f"    Quality score: {health['current_quality']:.1%}")
    print(f"    Trend: {health['trend']}")
    print(f"    Best ever: {health['best_quality']:.1%}")
    print(tracker.render_quality_chart())
    for action in health["maintenance_actions"]:
        print(f"    -> {action}")


# ===================================================================
# SECTION 6: SYNTHETIC DATA GENERATION
# ===================================================================

def demo_synthetic_data():
    print_section("6. SYNTHETIC DATA GENERATION")

    gen = SyntheticDataGenerator(seed=42)

    result = gen.generate_synthetic_questions(n=8, categories=["physics", "biology", "chemistry"])

    print(f"  --- GENERATED QUESTIONS ---")
    print(f"    Total: {result['total_generated']}")
    print(f"    Categories: {json.dumps(result['categories'])}")

    for item in result["items"][:3]:
        print(f"    {item['id']}: {item['prompt'][:60]}...")
        print(f"      category={item['category']} gt={item['ground_truth']} "
              f"status={item['quality_status']}")

    print(f"\n  Warnings:")
    for w in result["warnings"]:
        print(f"    ! {w}")

    # --- Validate ---
    validation = gen.validate_synthetic_data(result["items"])
    print(f"\n  --- VALIDATION ---")
    print(f"    Valid: {validation['valid']}/{validation['total_checked']}")
    print(f"    Validation rate: {validation['validation_rate']:.1%}")

    # --- Simulated Human Review ---
    review = gen.simulate_human_review(result["items"])
    print(f"\n  --- HUMAN REVIEW (Simulated) ---")
    print(f"    Approved: {review['approved']}")
    print(f"    Needs revision: {review['needs_revision']}")
    print(f"    Rejected: {review['rejected']}")
    print(f"    Approval rate: {review['approval_rate']:.1%}")

    for item in review["reviewed_items"][:3]:
        print(f"    {item['id']}: {item['review_status']} "
              f"(score={item['quality_score']:.1f}/5) - {item['feedback']}")


# ===================================================================
# SECTION 7: FULL QUALITY EVALUATION
# ===================================================================

def demo_quality_evaluation():
    print_section("7. FULL DATASET QUALITY EVALUATION")

    sample = load_sample_data()
    items = sample["items"]

    # --- Coverage Analysis ---
    coverage = CoverageAnalyzer()
    cov_result = coverage.analyze(items)

    print(f"  --- COVERAGE ANALYSIS ---")
    print(f"    Coverage score: {cov_result['coverage_score']:.1%}")
    print(f"    Categories present: {', '.join(cov_result['category_coverage']['present'])}")
    print(f"    Categories missing: {', '.join(cov_result['category_coverage']['missing']) or 'none'}")
    print(f"    Category distribution:")
    for cat, count in cov_result["category_coverage"]["distribution"].items():
        bar = "#" * count
        print(f"      {cat:<15s}: {count:>2d} {bar}")

    print(f"    Difficulty coverage: {cov_result['difficulty_coverage']['score']:.1%}")
    for diff, count in cov_result["difficulty_coverage"]["distribution"].items():
        print(f"      {diff:<10s}: {count}")

    print(f"    Answer balance: {cov_result['answer_distribution']['balance_score']:.1%}")
    print(f"    Edge cases: {cov_result['edge_cases']['count']} ({cov_result['edge_cases']['percentage']:.0f}%)")
    print(f"    Subcategories: {cov_result['subcategory_count']}")

    print(f"\n    Recommendations:")
    for rec in cov_result["gaps"]["recommendations"]:
        print(f"      -> {rec}")

    # --- Balance Check ---
    balance = BalanceChecker()
    bal_result = balance.full_balance_report(items)

    print(f"\n  --- BALANCE CHECK ---")
    print(f"    Overall balanced: {bal_result['overall_balanced']}")
    for dim, data in bal_result["results"].items():
        status = "BALANCED" if data["is_balanced"] else "IMBALANCED"
        print(f"    {dim}: {status} (gini={data['gini_coefficient']:.3f}, "
              f"ratio={data['imbalance_ratio']:.1f})")

    # --- Duplicate Detection ---
    dupes = DuplicateDetector()
    dup_result = dupes.detect(items)

    print(f"\n  --- DUPLICATE DETECTION ---")
    print(f"    Total: {dup_result['total_items']}")
    print(f"    Unique: {dup_result['unique_items']}")
    print(f"    Exact duplicates: {dup_result['exact_duplicates']['count']}")
    print(f"    Near duplicates: {dup_result['near_duplicates']['count']}")
    print(f"    Uniqueness score: {dup_result['quality_score']:.1%}")

    # --- Composite Quality Score ---
    scorer = DatasetQualityScorer()
    score_result = scorer.score(items)

    print(f"\n  --- COMPOSITE QUALITY SCORE ---")
    print(f"    Grade: {score_result['grade']}")
    print(f"    Score: {score_result['composite_score']:.1f}/100")
    print(f"    Breakdown:")
    for component, value in score_result["component_scores"].items():
        weight = score_result["weights"][component]
        bar = "#" * int(value / 100 * 25)
        print(f"      {component:<22s}: {value:5.1f}/100 (weight={weight}) |{bar}|")


# ===================================================================
# MAIN
# ===================================================================

def main():
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  CHAPTER 6: GOLDEN DATASET ENGINEERING".center(68) + "#")
    print("#" + "  Comprehensive LLM Evaluation Course".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)

    demo_why_golden_datasets()
    demo_dataset_creation()
    demo_annotation_workflow()
    demo_regression_testing()
    demo_versioning_and_maintenance()
    demo_synthetic_data()
    demo_quality_evaluation()

    print("\n  Run complete! All 7 golden dataset engineering topics covered.")
    print("  Next: Chapter 7 -- Evaluation Dataset Engineering\n")


if __name__ == "__main__":
    main()
