"""
Chapter 1 - Foundations of LLM Evaluation
==========================================
Run: python main.py

This chapter covers:
  1. Why evaluation matters
  2. Offline vs Online evaluation
  3. Intrinsic vs Extrinsic evaluation
  4. Human vs Automatic evaluation
  5. Reference vs Reference-free evaluation
  6. Model-based evaluation
  7. Regression testing
  8. Continuous evaluation
  9. Evaluation lifecycle
  10. Evaluation pipelines
  11. Failure analysis & Error taxonomy
  12. Evaluation dashboards
  13. Evaluation in CI/CD
"""

import sys
import io
import json
import random
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from dataset import (
    load_train_data,
    simulate_llm_predictions,
    create_evaluation_pairs,
    get_dataset_summary,
    load_sample_data,
)
from evaluator import (
    compute_accuracy,
    compute_per_class_accuracy,
    build_confusion_matrix,
    OfflineEvaluator,
    OnlineEvaluator,
    ReferenceEvaluator,
    ReferenceFreeEvaluator,
    AutomaticEvaluator,
    SimulatedHumanEvaluator,
    IntrinsicEvaluator,
    ExtrinsicEvaluator,
    ErrorTaxonomy,
    RegressionTester,
    EvaluationPipeline,
    EvaluationLifecycle,
    TextDashboard,
    CICDGate,
    ContinuousEvaluator,
)


def print_section(title: str):
    print("\n")
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_json(data: dict, indent: int = 2):
    print(json.dumps(data, indent=indent, default=str))


# ===================================================================
# SECTION 1: WHY EVALUATION MATTERS
# ===================================================================

def demo_why_evaluation_matters():
    print_section("1. WHY EVALUATION MATTERS")

    print("""
  PROBLEM:
    You deploy an LLM to answer science questions. Users complain
    it's wrong 40% of the time. But you didn't know because you
    never measured it.

  WHY IT EXISTS:
    LLMs are non-deterministic. They can sound confident while being
    completely wrong. Without evaluation, you're flying blind.

  INTUITION:
    Think of evaluation like a speedometer in a car. The car runs
    fine without one — but you'll get a speeding ticket because
    you can't tell how fast you're going.

    Evaluation is your speedometer for AI quality.

  KEY REASONS:
    1. Measure quality    → "How good is my model?"
    2. Compare models     → "Is model A better than model B?"
    3. Detect regressions → "Did my latest change break something?"
    4. Build trust        → "Can I deploy this to production?"
    5. Improve systems    → "Where exactly does my model fail?"
    """)

    questions = load_train_data(limit=50)
    summary = get_dataset_summary(questions)

    print("  Dataset Summary:")
    print(f"    Total questions: {summary['total_questions']}")
    print(f"    Answer distribution: {summary['answer_distribution']}")
    print(f"    Avg prompt length: {summary['avg_prompt_length_chars']} chars")

    sample = load_sample_data()
    models = sample["simulated_llm_responses"]
    ground_truths = [q["ground_truth"] for q in sample["questions"]]

    print("\n  Comparing 4 models WITHOUT evaluation (you'd never know):")
    print("  Comparing 4 models WITH evaluation:")
    print()
    for model_name, model_data in models.items():
        acc = compute_accuracy(ground_truths, model_data["predictions"])
        bar = "█" * int(acc * 30) + "░" * (30 - int(acc * 30))
        print(f"    {model_name:<20s} |{bar}| {acc:.0%}  — {model_data['description']}")

    print("""
  WITHOUT EVALUATION: All 4 models "seem to work" — you can't tell them apart.
  WITH EVALUATION:    Clear quality ranking emerges instantly.

  TAKEAWAY: Evaluation is not optional. It's the difference between
  "I think it works" and "I know it works, here's the data."
    """)


# ===================================================================
# SECTION 2: OFFLINE vs ONLINE EVALUATION
# ===================================================================

def demo_offline_vs_online():
    print_section("2. OFFLINE vs ONLINE EVALUATION")

    print("""
  PROBLEM:
    When should you evaluate? Before deployment? After? Both?

  INTUITION:
    - OFFLINE = exam before graduation (controlled, complete, pre-deployment)
    - ONLINE  = performance review at work (real-world, continuous, post-deployment)

  ASCII DIAGRAM:

    OFFLINE EVALUATION                 ONLINE EVALUATION
    ┌──────────────────┐               ┌──────────────────┐
    │  Fixed Dataset   │               │  Live Traffic    │
    │  (train.csv)     │               │  (user queries)  │
    │       │          │               │       │          │
    │       ▼          │               │       ▼          │
    │  Run Model       │               │  Run Model       │
    │       │          │               │       │          │
    │       ▼          │               │       ▼          │
    │  Compare with    │               │  Log Response    │
    │  Ground Truth    │               │  + User Feedback │
    │       │          │               │       │          │
    │       ▼          │               │       ▼          │
    │  Batch Report    │               │  Rolling Metrics │
    └──────────────────┘               └──────────────────┘
    Before deployment                  After deployment
    """)

    questions = load_train_data(limit=30)
    preds = simulate_llm_predictions(questions, accuracy=0.75)

    # --- Offline ---
    print("  --- OFFLINE EVALUATION (Batch) ---")
    offline = OfflineEvaluator(questions, preds)
    result = offline.run()
    print(f"    Total questions: {result['total_questions']}")
    print(f"    Accuracy: {result['accuracy']:.2%}")
    print(f"    Total errors: {result['total_errors']}")
    print(f"    First error: {result['errors'][0] if result['errors'] else 'None'}")

    # --- Online ---
    print("\n  --- ONLINE EVALUATION (Streaming) ---")
    online = OnlineEvaluator()
    for q, pred in zip(questions, preds):
        latency = random.uniform(50, 200)
        online.record(q["ground_truth"], pred, latency_ms=latency)

    status = online.get_status()
    print(f"    Total evaluated: {status['total_evaluated']}")
    print(f"    Cumulative accuracy: {status['cumulative_accuracy']:.2%}")
    print(f"    Rolling accuracy (last 20): {status['rolling_accuracy']:.2%}")
    print(f"    Avg latency: {status['avg_latency_ms']:.1f} ms")
    print(f"    P95 latency: {status['p95_latency_ms']:.1f} ms")

    print("""
  COMPARISON TABLE:
  ┌─────────────────┬──────────────────────┬──────────────────────┐
  │ Aspect          │ Offline              │ Online               │
  ├─────────────────┼──────────────────────┼──────────────────────┤
  │ When            │ Before deployment    │ After deployment     │
  │ Data            │ Fixed dataset        │ Live traffic         │
  │ Speed           │ Batch (minutes)      │ Real-time (ms)       │
  │ Ground truth    │ Usually available    │ Often unavailable    │
  │ Coverage        │ Pre-selected cases   │ Real distribution    │
  │ Use case        │ Model selection      │ Monitoring & alerts  │
  └─────────────────┴──────────────────────┴──────────────────────┘

  BEST PRACTICE: Use BOTH. Offline to validate before deploy,
  Online to catch issues that only appear with real users.
    """)


# ===================================================================
# SECTION 3: INTRINSIC vs EXTRINSIC EVALUATION
# ===================================================================

def demo_intrinsic_vs_extrinsic():
    print_section("3. INTRINSIC vs EXTRINSIC EVALUATION")

    print("""
  PROBLEM:
    Your model gets 90% accuracy on the test set, but users are unhappy.
    How is that possible?

  INTUITION:
    - INTRINSIC = "How well does the model answer questions?" (task quality)
    - EXTRINSIC = "Are users actually satisfied?" (real-world impact)

    A model can be intrinsically good but extrinsically bad:
    → 90% accurate but takes 10 seconds per response (too slow)
    → 90% accurate but fails on the 10% that matters most to users
    """)

    questions = load_train_data(limit=30)
    preds = simulate_llm_predictions(questions, accuracy=0.80)
    ground_truths = [q["ground_truth"] for q in questions]

    intrinsic = IntrinsicEvaluator()
    intrinsic_result = intrinsic.evaluate(ground_truths, preds)
    print("  --- INTRINSIC EVALUATION ---")
    print(f"    Accuracy: {intrinsic_result['accuracy']:.2%}")
    print(f"    Metrics focus: {intrinsic_result['metrics_focus']}")

    rng = random.Random(42)
    latencies = [rng.uniform(100, 5000) for _ in questions]
    satisfaction = [
        rng.uniform(3.5, 5.0) if gt == pred else rng.uniform(1.0, 3.0)
        for gt, pred in zip(ground_truths, preds)
    ]

    extrinsic = ExtrinsicEvaluator()
    extrinsic_result = extrinsic.evaluate(
        ground_truths, preds, latencies, satisfaction
    )
    print("\n  --- EXTRINSIC EVALUATION ---")
    print(f"    Task completion rate: {extrinsic_result['task_completion_rate']:.2%}")
    print(f"    Avg latency: {extrinsic_result['avg_latency_ms']:.0f} ms")
    print(f"    Avg user satisfaction: {extrinsic_result['avg_user_satisfaction']:.2f}/5.0")
    print(f"    Metrics focus: {extrinsic_result['metrics_focus']}")

    print("""
  KEY INSIGHT:
    The model is 80% accurate (intrinsic = good), but avg latency
    is ~2500ms and user satisfaction is only ~3.5/5 (extrinsic = mediocre).

    In production, extrinsic metrics often matter MORE than intrinsic ones.
    Users don't care about your F1 score — they care about their experience.
    """)


# ===================================================================
# SECTION 4: HUMAN vs AUTOMATIC EVALUATION
# ===================================================================

def demo_human_vs_automatic():
    print_section("4. HUMAN vs AUTOMATIC EVALUATION")

    print("""
  PROBLEM:
    Some qualities (helpfulness, creativity, safety) are hard to
    measure automatically. But human evaluation is slow and expensive.

  INTUITION:
    - AUTOMATIC = Calculator (fast, cheap, consistent, limited)
    - HUMAN     = Expert reviewer (slow, expensive, nuanced, subjective)

  When to use which:
    ┌─────────────────────────────┬────────────┬───────────┐
    │ What you're evaluating      │ Automatic  │ Human     │
    ├─────────────────────────────┼────────────┼───────────┤
    │ Exact match / accuracy      │ ✓ Best     │           │
    │ Format compliance           │ ✓ Best     │           │
    │ Helpfulness                 │            │ ✓ Best    │
    │ Creativity                  │            │ ✓ Best    │
    │ Safety / toxicity           │ ✓ Partial  │ ✓ Best    │
    │ Factual correctness         │ ✓ Partial  │ ✓ Best    │
    │ Regression testing (CI/CD)  │ ✓ Best     │           │
    │ User preference (A vs B)    │            │ ✓ Best    │
    └─────────────────────────────┴────────────┴───────────┘
    """)

    questions = load_train_data(limit=30)
    preds = simulate_llm_predictions(questions, accuracy=0.75)
    ground_truths = [q["ground_truth"] for q in questions]

    auto = AutomaticEvaluator()
    auto_result = auto.evaluate_batch(ground_truths, preds)
    print("  --- AUTOMATIC EVALUATION ---")
    print(f"    Accuracy: {auto_result['accuracy']:.2%}")
    print(f"    Time: {auto_result['evaluation_time_seconds']:.6f} seconds")
    print(f"    Scalability: {auto_result['scalability']}")
    print(f"    Consistency: {auto_result['consistency']}")

    human = SimulatedHumanEvaluator(agreement_rate=0.85, time_per_item_sec=30)
    human_result = human.evaluate_batch(ground_truths, preds)
    print("\n  --- HUMAN EVALUATION (Simulated) ---")
    print(f"    Annotator 1 accuracy: {human_result['annotator_1_accuracy']:.2%}")
    print(f"    Annotator 2 accuracy: {human_result['annotator_2_accuracy']:.2%}")
    print(f"    Inter-annotator agreement: {human_result['inter_annotator_agreement']:.2%}")
    print(f"    Estimated time: {human_result['estimated_time_seconds']:.0f} seconds")
    print(f"    Estimated cost: ${human_result['estimated_cost_usd']:.2f}")
    print(f"    Scalability: {human_result['scalability']}")

    print("""
  KEY INSIGHT:
    Automatic evaluation: < 0.001 seconds, $0 cost
    Human evaluation:     ~900 seconds, ~$9 cost (for just 30 questions!)

    At scale (10,000 questions), human evaluation would cost ~$3,000
    and take ~83 hours. That's why automatic metrics are essential
    for day-to-day evaluation, with human evaluation reserved for
    high-stakes decisions.
    """)


# ===================================================================
# SECTION 5: REFERENCE vs REFERENCE-FREE EVALUATION
# ===================================================================

def demo_reference_vs_referencefree():
    print_section("5. REFERENCE vs REFERENCE-FREE EVALUATION")

    print("""
  PROBLEM:
    Sometimes you have the correct answer (ground truth).
    Sometimes you don't. How do you evaluate in each case?

  INTUITION:
    - REFERENCE-BASED = Grading an exam with an answer key
    - REFERENCE-FREE  = Grading an essay without a rubric (just: "is it good?")

  ASCII DIAGRAM:

    REFERENCE-BASED                    REFERENCE-FREE
    ┌────────────┐                     ┌────────────┐
    │  Question  │                     │  Question  │
    │     +      │                     │     +      │
    │  Answer    │                     │  Answer    │
    │     +      │                     │     │      │
    │  Ground    │                     │     ▼      │
    │  Truth     │                     │  Quality   │
    │     │      │                     │  Checks    │
    │     ▼      │                     │  (format,  │
    │  Compare   │                     │   length,  │
    │  Match?    │                     │   valid?)  │
    └────────────┘                     └────────────┘
    """)

    sample = load_sample_data()
    questions = sample["questions"]

    ref_eval = ReferenceEvaluator()
    free_eval = ReferenceFreeEvaluator()

    print("  --- REFERENCE-BASED EVALUATION ---")
    for q in questions[:3]:
        prediction = sample["simulated_llm_responses"]["good_model"]["predictions"][q["id"]]
        result = ref_eval.evaluate(q["ground_truth"], prediction)
        match = "✓" if result["exact_match"] else "✗"
        print(f"    Q{q['id']}: expected={result['ground_truth']}, "
              f"predicted={result['prediction']} → {match}")

    print("\n  --- REFERENCE-FREE EVALUATION ---")
    for q in questions[:3]:
        prediction = sample["simulated_llm_responses"]["good_model"]["predictions"][q["id"]]
        result = free_eval.evaluate(q["prompt"], prediction, q["choices"])
        print(f"    Q{q['id']}: prediction={result['prediction']}, "
              f"valid_choice={result['is_valid_choice']}, "
              f"answer_length={result['answer_length']} chars")

    print("""
  COMPARISON:
  ┌──────────────────┬─────────────────────┬─────────────────────────┐
  │ Aspect           │ Reference-based     │ Reference-free          │
  ├──────────────────┼─────────────────────┼─────────────────────────┤
  │ Requires         │ Ground truth        │ Nothing                 │
  │ Measures         │ Correctness         │ Quality signals         │
  │ Precision        │ High                │ Lower                   │
  │ Cost             │ Needs labeled data  │ No labeling needed      │
  │ Use case         │ Exact tasks (MCQ)   │ Open-ended generation   │
  │ Example metrics  │ Accuracy, F1, BLEU  │ Fluency, coherence,     │
  │                  │                     │ LLM-as-a-Judge          │
  └──────────────────┴─────────────────────┴─────────────────────────┘
    """)


# ===================================================================
# SECTION 6: MODEL-BASED EVALUATION
# ===================================================================

def demo_model_based_evaluation():
    print_section("6. MODEL-BASED EVALUATION (LLM-as-a-Judge Preview)")

    print("""
  PROBLEM:
    Human evaluation is expensive. Automatic metrics like BLEU
    don't capture meaning. Is there a middle ground?

  INTUITION:
    Use a STRONGER LLM to evaluate a WEAKER LLM's outputs.
    Like having a senior engineer review a junior's code.

  HOW IT WORKS:
    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
    │ Question │───▶│ Model Under  │───▶│ Response     │
    └──────────┘    │ Test (e.g.   │    └──────┬───────┘
                    │ Mistral 7B)  │           │
                    └──────────────┘           │
                                              ▼
                    ┌──────────────┐    ┌──────────────┐
                    │ Judge Model  │◀───│ Judge Prompt │
                    │ (e.g. GPT-4 │    │ "Rate this   │
                    │  or Mistral  │    │  response    │
                    │  Large)      │    │  1-5..."     │
                    └──────┬───────┘    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Score: 4/5   │
                    │ Reason: ...  │
                    └──────────────┘

  NOTE: We'll do a DEEP DIVE in Chapter 4 (LLM-as-a-Judge).
  Here we'll simulate it to understand the concept.
    """)

    sample = load_sample_data()
    questions = sample["questions"]
    good_preds = sample["simulated_llm_responses"]["good_model"]["predictions"]
    poor_preds = sample["simulated_llm_responses"]["poor_model"]["predictions"]
    ground_truths = [q["ground_truth"] for q in questions]

    print("  --- SIMULATED LLM-AS-A-JUDGE SCORING ---")
    print()
    rng = random.Random(42)

    for q in questions[:5]:
        good_pred = good_preds[q["id"]]
        poor_pred = poor_preds[q["id"]]
        gt = q["ground_truth"]

        good_correct = good_pred == gt
        poor_correct = poor_pred == gt

        good_score = rng.randint(4, 5) if good_correct else rng.randint(1, 3)
        poor_score = rng.randint(4, 5) if poor_correct else rng.randint(1, 2)

        print(f"    Q{q['id']}: {q['prompt'][:60]}...")
        print(f"      Good model: pred={good_pred}, correct={good_correct}, judge_score={good_score}/5")
        print(f"      Poor model: pred={poor_pred}, correct={poor_correct}, judge_score={poor_score}/5")
        print()

    print("""
  KEY TYPES OF MODEL-BASED EVALUATION:
    1. Pointwise  — Score one response at a time (1-5)
    2. Pairwise   — Compare two responses: "Which is better?"
    3. Pass/Fail  — Binary: "Is this acceptable?"
    4. Rubric     — Score against specific criteria

  ADVANTAGES:
    - Cheaper than human evaluation
    - More nuanced than exact match
    - Scalable to thousands of examples
    - Can evaluate open-ended responses

  LIMITATIONS:
    - Judge model can have biases (prefers longer answers, etc.)
    - Only as good as the judge model
    - Can be gamed (model learns what judge likes, not what's correct)

  We'll build a full LLM-as-a-Judge system in Chapter 4.
    """)


# ===================================================================
# SECTION 7: REGRESSION TESTING
# ===================================================================

def demo_regression_testing():
    print_section("7. REGRESSION TESTING")

    print("""
  PROBLEM:
    You update your prompt, fine-tune your model, or change your
    retrieval pipeline. How do you know you didn't break something?

  INTUITION:
    Like running your test suite after every code change.
    If the tests pass → safe to deploy.
    If tests fail → something broke, investigate before deploying.

  HOW IT WORKS:
    ┌──────────┐     ┌──────────┐     ┌──────────────┐
    │ Golden   │────▶│ Model v1 │────▶│ Predictions  │──┐
    │ Dataset  │     └──────────┘     │ (baseline)   │  │
    │          │                      └──────────────┘  │  COMPARE
    │          │     ┌──────────┐     ┌──────────────┐  │  ───────▶ PASS/FAIL
    │          │────▶│ Model v2 │────▶│ Predictions  │──┘
    └──────────┘     └──────────┘     │ (candidate)  │
                                      └──────────────┘
    """)

    questions = load_train_data(limit=50)
    ground_truths = [q["ground_truth"] for q in questions]
    preds_v1 = simulate_llm_predictions(questions, accuracy=0.78, seed=100)
    preds_v2_better = simulate_llm_predictions(questions, accuracy=0.84, seed=200)
    preds_v2_worse = simulate_llm_predictions(questions, accuracy=0.68, seed=300)

    tester = RegressionTester(threshold=0.02)

    print("  --- SCENARIO A: Model v2 is BETTER ---")
    result_a = tester.compare(ground_truths, preds_v1, preds_v2_better)
    print(f"    v1 accuracy: {result_a['v1_accuracy']:.2%}")
    print(f"    v2 accuracy: {result_a['v2_accuracy']:.2%}")
    print(f"    Delta: {result_a['delta']:+.2%}")
    print(f"    Status: {result_a['status']}")
    print(f"    Regressions: {result_a['regressions_count']} questions got worse")
    print(f"    Improvements: {result_a['improvements_count']} questions got better")

    print("\n  --- SCENARIO B: Model v2 is WORSE (regression!) ---")
    result_b = tester.compare(ground_truths, preds_v1, preds_v2_worse)
    print(f"    v1 accuracy: {result_b['v1_accuracy']:.2%}")
    print(f"    v2 accuracy: {result_b['v2_accuracy']:.2%}")
    print(f"    Delta: {result_b['delta']:+.2%}")
    print(f"    Status: {result_b['status']}")
    print(f"    Regressions: {result_b['regressions_count']} questions got worse")
    print(f"    Improvements: {result_b['improvements_count']} questions got better")

    print("""
  BEST PRACTICES:
    1. Maintain a "golden dataset" of critical test cases
    2. Set a clear regression threshold (e.g., max 2% drop allowed)
    3. Run regression tests automatically in CI/CD
    4. Track not just overall accuracy, but PER-QUESTION regressions
    5. A question that v1 got right but v2 gets wrong is a RED FLAG
       — even if v2's overall accuracy is higher
    """)


# ===================================================================
# SECTION 8: CONTINUOUS EVALUATION
# ===================================================================

def demo_continuous_evaluation():
    print_section("8. CONTINUOUS EVALUATION")

    print("""
  PROBLEM:
    Your model was great when you deployed it. But the world changes.
    User queries change. Knowledge becomes outdated. How do you know
    when your model starts degrading?

  INTUITION:
    Like regular health checkups. You don't wait until you're sick
    to see a doctor. You check regularly to catch problems early.

  CONTINUOUS EVALUATION LOOP:
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │   Deploy ──▶ Monitor ──▶ Evaluate ──▶ Alert     │
    │     ▲                                   │        │
    │     │                                   ▼        │
    │   Improve ◀── Diagnose ◀── Triage ◀── Issue     │
    │                                                  │
    └──────────────────────────────────────────────────┘
    """)

    tracker = ContinuousEvaluator()
    tracker.add_version("v1.0", 0.72, "2024-01-15")
    tracker.add_version("v1.1", 0.75, "2024-02-01")
    tracker.add_version("v1.2", 0.78, "2024-03-01")
    tracker.add_version("v1.3", 0.76, "2024-04-01")
    tracker.add_version("v2.0", 0.83, "2024-05-01")
    tracker.add_version("v2.1", 0.81, "2024-06-01")
    tracker.add_version("v2.2", 0.85, "2024-07-01")

    trend = tracker.get_trend()
    print(f"  Trend: {trend['trend']}")
    print(f"  Avg delta per version: {trend['avg_delta_per_version']:+.2%}")
    print(f"  Best: {trend['best_version']['version']} ({trend['best_version']['accuracy']:.1%})")
    print(f"  Worst: {trend['worst_version']['version']} ({trend['worst_version']['accuracy']:.1%})")

    print(tracker.render_trend_chart())

    print("""
  WHAT TO MONITOR:
    1. Accuracy / quality metrics    — Are we getting better or worse?
    2. Latency trends                — Is the model getting slower?
    3. Error rate distribution       — Are new error types appearing?
    4. Input distribution shift      — Are users asking different things?
    5. Cost per query                — Is inference getting more expensive?

  ALERT TRIGGERS:
    - Accuracy drops more than 2% in a week
    - P95 latency exceeds 3 seconds
    - New error category appears
    - Input distribution shifts significantly
    """)


# ===================================================================
# SECTION 9: EVALUATION LIFECYCLE
# ===================================================================

def demo_evaluation_lifecycle():
    print_section("9. EVALUATION LIFECYCLE")

    print("""
  PROBLEM:
    Evaluation isn't just "compute accuracy." It's a multi-step process
    that needs to be tracked and reproduced.

  THE 6 STAGES:
    ┌───────────────────┐
    │ 1. Dataset Prep   │  Load, clean, validate data
    │         │         │
    │         ▼         │
    │ 2. Model Inference│  Run model on evaluation set
    │         │         │
    │         ▼         │
    │ 3. Metric Compute │  Calculate accuracy, F1, etc.
    │         │         │
    │         ▼         │
    │ 4. Error Analysis  │  Classify and analyze failures
    │         │         │
    │         ▼         │
    │ 5. Regression Check│  Compare with previous version
    │         │         │
    │         ▼         │
    │ 6. Report Generate │  Create dashboard & artifacts
    └───────────────────┘
    """)

    lifecycle = EvaluationLifecycle("science_qa_eval_v2")

    lifecycle.start_stage("dataset_preparation")
    questions = load_train_data(limit=30)
    lifecycle.complete_stage("dataset_preparation", {"num_questions": len(questions)})

    lifecycle.start_stage("model_inference")
    preds = simulate_llm_predictions(questions, accuracy=0.80)
    lifecycle.complete_stage("model_inference", {"num_predictions": len(preds)})

    lifecycle.start_stage("metric_computation")
    ground_truths = [q["ground_truth"] for q in questions]
    accuracy = compute_accuracy(ground_truths, preds)
    lifecycle.complete_stage("metric_computation", {"accuracy": round(accuracy, 4)})

    lifecycle.start_stage("error_analysis")
    taxonomy = ErrorTaxonomy()
    errors = taxonomy.classify_errors(questions, preds)
    lifecycle.complete_stage("error_analysis", {"total_errors": errors["total_errors"]})

    lifecycle.start_stage("regression_check")
    preds_v1 = simulate_llm_predictions(questions, accuracy=0.70, seed=99)
    tester = RegressionTester()
    reg_result = tester.compare(ground_truths, preds_v1, preds)
    lifecycle.complete_stage("regression_check", {"status": reg_result["status"]})

    lifecycle.start_stage("report_generation")
    report = lifecycle.get_report()
    lifecycle.complete_stage("report_generation", {"report_generated": True})

    final_report = lifecycle.get_report()
    print("  Lifecycle Report:")
    print(f"    Experiment: {final_report['experiment']}")
    print(f"    Completed: {final_report['completed']}")
    for stage, info in final_report["stages"].items():
        status_icon = "✓" if info["status"] == "completed" else "○"
        duration = f"{info['duration']:.4f}s" if info["duration"] else "—"
        print(f"    {status_icon} {stage:<25s} {info['status']:<12s} {duration}")


# ===================================================================
# SECTION 10: EVALUATION PIPELINES
# ===================================================================

def demo_evaluation_pipeline():
    print_section("10. EVALUATION PIPELINES")

    print("""
  PROBLEM:
    You run the same evaluation steps repeatedly. How do you
    automate and standardize this?

  INTUITION:
    Like a CI/CD pipeline but for model evaluation.
    Define once, run many times, compare results.
    """)

    questions = load_train_data(limit=30)
    preds = simulate_llm_predictions(questions, accuracy=0.80)
    ground_truths = [q["ground_truth"] for q in questions]

    pipeline = EvaluationPipeline("science_qa_pipeline")

    pipeline.add_step(
        "accuracy",
        compute_accuracy,
        ground_truths=ground_truths,
        predictions=preds,
    )
    pipeline.add_step(
        "per_class_accuracy",
        compute_per_class_accuracy,
        ground_truths=ground_truths,
        predictions=preds,
    )
    pipeline.add_step(
        "confusion_matrix",
        build_confusion_matrix,
        ground_truths=ground_truths,
        predictions=preds,
    )
    pipeline.add_step(
        "error_analysis",
        ErrorTaxonomy().classify_errors,
        questions=questions,
        predictions=preds,
    )

    results = pipeline.run()

    print(f"  Pipeline: {results['pipeline_name']}")
    print(f"  Timestamp: {results['timestamp']}")
    print(f"  Steps: {results['summary']['total_steps']}")
    print(f"  Successful: {results['summary']['successful']}")
    print(f"  Failed: {results['summary']['failed']}")
    print(f"  Duration: {results['summary']['total_duration_seconds']:.4f}s")

    print("\n  Step Results:")
    for step_name, step_result in results["steps"].items():
        status = step_result["status"]
        icon = "✓" if status == "success" else "✗"
        print(f"    {icon} {step_name}: {status} ({step_result['duration_seconds']:.4f}s)")
        if status == "success" and isinstance(step_result["result"], (int, float)):
            print(f"      → {step_result['result']:.4f}")

    print("""
  PIPELINE BENEFITS:
    1. Reproducibility  — Same steps, same order, every time
    2. Automation       — No manual steps, runs in CI/CD
    3. Comparability    — Same pipeline for all model versions
    4. Extensibility    — Add/remove steps as needed
    5. Auditability     — Track what was run and when
    """)


# ===================================================================
# SECTION 11: FAILURE ANALYSIS & ERROR TAXONOMY
# ===================================================================

def demo_error_taxonomy():
    print_section("11. FAILURE ANALYSIS & ERROR TAXONOMY")

    print("""
  PROBLEM:
    Knowing your model is 80% accurate tells you 20% of answers
    are wrong — but WHY are they wrong? Different errors need
    different fixes.

  ERROR TAXONOMY FOR MCQ:
    ┌─────────────────┬─────────────────────────────────────────┐
    │ Error Type      │ Description                             │
    ├─────────────────┼─────────────────────────────────────────┤
    │ wrong_choice    │ Model picked an incorrect option        │
    │ hallucination   │ Model invented an answer not in choices │
    │ no_response     │ Model failed to respond                 │
    │ format_error    │ Response couldn't be parsed             │
    │ partial_correct │ Right reasoning, wrong final pick       │
    └─────────────────┴─────────────────────────────────────────┘

  WHY IT MATTERS:
    - "wrong_choice" → improve the model/prompt
    - "hallucination" → add output constraints
    - "no_response" → fix timeout/retry logic
    - "format_error" → fix output parsing
    Each error type has a DIFFERENT fix.
    """)

    questions = load_train_data(limit=50)
    preds = simulate_llm_predictions(questions, accuracy=0.72)

    taxonomy = ErrorTaxonomy()
    result = taxonomy.classify_errors(questions, preds)

    print(f"  Total errors: {result['total_errors']}")
    print(f"  Error rate: {result['error_rate']:.1%}")
    print(f"\n  Error Distribution:")
    for error_type, count in result["error_distribution"].items():
        bar = "█" * count
        print(f"    {error_type:<18s} {count:>3d} {bar}")

    if result["error_examples"]:
        print(f"\n  Example Errors:")
        for error_type, examples in result["error_examples"].items():
            for ex in examples[:1]:
                print(f"    [{error_type}] Q{ex['id']}: expected={ex['expected']}, "
                      f"got={ex['predicted']}")
                print(f"      → {ex['prompt_preview']}...")

    print("""
  FAILURE ANALYSIS PROCESS:
    1. CLASSIFY  — Put each error into a category
    2. QUANTIFY  — How many of each type?
    3. PRIORITIZE — Which error type hurts the most?
    4. ROOT CAUSE — Why does this error happen?
    5. FIX       — Apply targeted fix for that error type
    6. VERIFY    — Run regression test to confirm the fix works

  COMMON MISTAKE:
    Trying to fix all errors at once. Instead, fix the most
    common/impactful error category FIRST, then re-evaluate.
    """)


# ===================================================================
# SECTION 12: EVALUATION DASHBOARD
# ===================================================================

def demo_dashboard():
    print_section("12. EVALUATION DASHBOARD")

    print("""
  PROBLEM:
    You've computed 20 metrics. How do you present them so that
    a stakeholder can understand the model's health at a glance?

  INTUITION:
    Like a car dashboard — the key gauges are front and center.
    Details available if you look deeper, but the summary is immediate.
    """)

    questions = load_train_data(limit=50)
    preds = simulate_llm_predictions(questions, accuracy=0.78)
    ground_truths = [q["ground_truth"] for q in questions]

    dashboard_data = {
        "accuracy": compute_accuracy(ground_truths, preds),
        "per_class_accuracy": compute_per_class_accuracy(ground_truths, preds),
        "total_errors": sum(1 for gt, p in zip(ground_truths, preds) if gt != p),
        "confusion_matrix": build_confusion_matrix(ground_truths, preds),
    }

    dashboard = TextDashboard()
    print(dashboard.render_summary(dashboard_data))


# ===================================================================
# SECTION 13: EVALUATION IN CI/CD
# ===================================================================

def demo_cicd_evaluation():
    print_section("13. EVALUATION IN CI/CD")

    print("""
  PROBLEM:
    How do you automatically block bad models from reaching production?

  INTUITION:
    Like unit tests in CI. If tests fail, the PR can't merge.
    If evaluation fails, the model can't deploy.

  CI/CD PIPELINE WITH EVALUATION GATES:
    ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
    │ Code     │──▶ │ Build    │──▶ │ Evaluation   │──▶ │ Deploy   │
    │ Change   │    │ & Test   │    │ Gate         │    │          │
    └──────────┘    └──────────┘    │              │    └──────────┘
                                    │ ✓ accuracy   │
                                    │   >= 75%     │
                                    │ ✓ regression │
                                    │   <= 2%      │
                                    │              │
                                    │ PASS → deploy│
                                    │ FAIL → block │
                                    └──────────────┘
    """)

    gate = CICDGate(min_accuracy=0.75, max_regression=0.02)

    print("  --- SCENARIO 1: Good model, no baseline ---")
    result1 = gate.check(current_accuracy=0.82)
    print(f"    Gate status: {result1['gate_status']}")
    print(f"    Deploy allowed: {result1['deploy_allowed']}")
    for check in result1["checks"]:
        icon = "✓" if check["status"] == "PASS" else "✗"
        print(f"    {icon} {check['check']}: {check['status']}")

    print("\n  --- SCENARIO 2: Good model, better than baseline ---")
    result2 = gate.check(current_accuracy=0.82, previous_accuracy=0.78)
    print(f"    Gate status: {result2['gate_status']}")
    for check in result2["checks"]:
        icon = "✓" if check["status"] == "PASS" else "✗"
        detail = f"actual={check.get('actual', check.get('actual_delta'))}"
        print(f"    {icon} {check['check']}: {check['status']} ({detail})")

    print("\n  --- SCENARIO 3: Model regressed too much ---")
    result3 = gate.check(current_accuracy=0.74, previous_accuracy=0.80)
    print(f"    Gate status: {result3['gate_status']}")
    for check in result3["checks"]:
        icon = "✓" if check["status"] == "PASS" else "✗"
        detail = f"actual={check.get('actual', check.get('actual_delta'))}"
        print(f"    {icon} {check['check']}: {check['status']} ({detail})")

    print("\n  --- SCENARIO 4: Model below minimum threshold ---")
    result4 = gate.check(current_accuracy=0.60, previous_accuracy=0.65)
    print(f"    Gate status: {result4['gate_status']}")
    for check in result4["checks"]:
        icon = "✓" if check["status"] == "PASS" else "✗"
        detail = f"actual={check.get('actual', check.get('actual_delta'))}"
        print(f"    {icon} {check['check']}: {check['status']} ({detail})")

    print("""
  CI/CD EVALUATION BEST PRACTICES:
    1. Define clear pass/fail thresholds BEFORE deployment
    2. Test against a golden dataset (not random samples)
    3. Check BOTH absolute quality AND regression
    4. Log all evaluation results for audit trail
    5. Alert on failures — don't just silently block
    6. Include evaluation time in your deployment budget
    """)


# ===================================================================
# FINAL SUMMARY
# ===================================================================

def print_final_summary():
    print_section("CHAPTER 1 SUMMARY — FOUNDATIONS OF LLM EVALUATION")

    print("""
  KEY TAKEAWAYS:
  ─────────────
  1. Evaluation is mandatory, not optional — it's your AI speedometer
  2. Use OFFLINE evaluation before deployment, ONLINE after
  3. INTRINSIC measures the task, EXTRINSIC measures the impact
  4. AUTOMATIC is fast and cheap; HUMAN captures nuance
  5. REFERENCE-BASED needs ground truth; REFERENCE-FREE doesn't
  6. LLM-as-a-Judge bridges the gap between automatic and human
  7. REGRESSION TESTING catches broken models before deployment
  8. CONTINUOUS EVALUATION catches degradation after deployment
  9. PIPELINES standardize and automate evaluation
  10. ERROR TAXONOMY guides targeted improvements
  11. DASHBOARDS communicate results to stakeholders
  12. CI/CD GATES prevent bad models from reaching production

  COMPARISON TABLE:
  ┌──────────────────┬──────────────┬──────────────┬──────────────┐
  │ Method           │ Cost         │ Speed        │ Nuance       │
  ├──────────────────┼──────────────┼──────────────┼──────────────┤
  │ Automatic        │ Near zero    │ Milliseconds │ Low          │
  │ Human            │ $$$          │ Hours/days   │ High         │
  │ LLM-as-a-Judge   │ $            │ Seconds      │ Medium-High  │
  │ Reference-based  │ Labeling $$  │ Fast         │ Medium       │
  │ Reference-free   │ Zero         │ Fast         │ Low-Medium   │
  └──────────────────┴──────────────┴──────────────┴──────────────┘

  COMMON MISTAKES:
  ────────────────
  ✗ Only evaluating once (before deployment)
  ✗ Only using one metric (accuracy is not enough)
  ✗ No regression testing (changes break things silently)
  ✗ No error analysis (you can't fix what you don't classify)
  ✗ Manual evaluation only (doesn't scale)
  ✗ Ignoring latency and cost (users care about these too)

  INTERVIEW QUESTIONS:
  ────────────────────
  Q1: What's the difference between offline and online evaluation?
  Q2: When would you use reference-free evaluation?
  Q3: How do you prevent model regressions in production?
  Q4: What is LLM-as-a-Judge and when would you use it?
  Q5: Design an evaluation pipeline for a RAG-based Q&A system.
  Q6: What metrics would you track for continuous evaluation?
  Q7: How would you set up evaluation gates in a CI/CD pipeline?

  WHAT'S NEXT:
  ────────────
  Chapter 2: Classical NLP Metrics — we'll implement Accuracy, Precision,
  Recall, F1, BLEU, ROUGE, BERTScore, Perplexity, and more from scratch.
    """)


# ===================================================================
# MAIN ENTRY POINT
# ===================================================================

def main():
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  CHAPTER 1: FOUNDATIONS OF LLM EVALUATION".center(68) + "█")
    print("█" + "  Comprehensive LLM Evaluation Course".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    demo_why_evaluation_matters()
    demo_offline_vs_online()
    demo_intrinsic_vs_extrinsic()
    demo_human_vs_automatic()
    demo_reference_vs_referencefree()
    demo_model_based_evaluation()
    demo_regression_testing()
    demo_continuous_evaluation()
    demo_evaluation_lifecycle()
    demo_evaluation_pipeline()
    demo_error_taxonomy()
    demo_dashboard()
    demo_cicd_evaluation()
    print_final_summary()

    print("\n  Run complete! All 13 foundation topics covered.")
    print("  Next: Chapter 2 — Classical NLP Metrics\n")


if __name__ == "__main__":
    main()
