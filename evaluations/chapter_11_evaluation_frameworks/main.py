import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 11 - Evaluation Frameworks
Main demo: run all 10 framework-style evaluators on the same dataset.
"""

from dataset import (
    get_rag_examples,
    get_mcq_examples,
    get_agent_traces,
    get_framework_test_cases,
    build_rag_dataset_for_framework,
)
from evaluator import (
    DeepEvalStyleEvaluator,
    RAGASStyleEvaluator,
    LangSmithStyleEvaluator,
    PromptfooStyleEvaluator,
    TruLensStyleEvaluator,
    InspectStyleEvaluator,
    InspectTask,
    PhoenixStyleEvaluator,
    EvidentlyStyleEvaluator,
    OpenAIEvalsStyleEvaluator,
    MaximAIStyleEvaluator,
    _word_overlap,
    _contains_extra_info,
    _context_as_str,
)


def header(num: int, title: str):
    print(f"\n{'='*70}")
    print(f"  {num}. {title}")
    print(f"{'='*70}")


def sub(text: str):
    print(f"\n--- {text} ---")


# Load data once
rag_examples = get_rag_examples()
rag_dataset = build_rag_dataset_for_framework(rag_examples)
mcq_examples = get_mcq_examples()
test_cases = get_framework_test_cases()
agent_traces = get_agent_traces()

print("=" * 70)
print("  CHAPTER 11: EVALUATION FRAMEWORKS - FULL DEMO")
print("=" * 70)
print(f"\nDataset: {len(rag_examples)} RAG examples, {len(mcq_examples)} MCQs, "
      f"{len(agent_traces)} agent traces, {len(test_cases)} test cases")


# =====================================================================
# 1. DeepEval
# =====================================================================
header(1, "DeepEval-Style Evaluation")
print("Unit-test style LLM evaluation with metric classes and measure() methods.")

evaluator = DeepEvalStyleEvaluator()
results = evaluator.evaluate(rag_dataset)

sub("Results per test case")
for r in results:
    print(f"\n  [{r['id']}]")
    for metric_name, m in r["metrics"].items():
        status = "PASS" if m["passed"] else "FAIL"
        print(f"    {metric_name:20s}  {m['score']:.2f}  [{status}]  {m['reason']}")

sub("Summary")
for metric in evaluator.metrics:
    scores = [r["metrics"][metric.name]["score"] for r in results]
    avg = sum(scores) / len(scores)
    passed = sum(1 for r in results if r["metrics"][metric.name]["passed"])
    print(f"  {metric.name:20s}  avg={avg:.2f}  passed={passed}/{len(results)}")


# =====================================================================
# 2. RAGAS
# =====================================================================
header(2, "RAGAS-Style Evaluation")
print("Component RAG metrics: faithfulness, relevancy, context precision/recall.")

ragas = RAGASStyleEvaluator()
ragas_results = ragas.evaluate(rag_dataset)

sub("Per-example scores")
print(f"  {'ID':<10} {'Faith':>7} {'Relev':>7} {'CtxPre':>7} {'CtxRec':>7}")
print(f"  {'-'*10} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
for r in ragas_results:
    print(f"  {r['id']:<10} {r['faithfulness']:>7.2f} {r['answer_relevancy']:>7.2f} "
          f"{r['context_precision']:>7.2f} {r['context_recall']:>7.2f}")

sub("Aggregate")
for key in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
    vals = [r[key] for r in ragas_results]
    print(f"  {key:22s}  mean={sum(vals)/len(vals):.3f}")


# =====================================================================
# 3. LangSmith
# =====================================================================
header(3, "LangSmith-Style Evaluation")
print("Run-based evaluation with datasets, custom evaluators, and latency tracking.")

langsmith = LangSmithStyleEvaluator(dataset_name="rag_eval")

for item in rag_dataset:
    langsmith.create_run(
        inputs={"question": item["question"]},
        outputs={"answer": item["answer"]},
    )

langsmith.add_evaluator("correctness", lambda run: _word_overlap(
    run.outputs["answer"], run.inputs["question"]) + 0.4)
langsmith.add_evaluator("conciseness", lambda run: min(
    1.0, 50.0 / max(len(run.outputs["answer"]), 1)))

ls_results = langsmith.evaluate_runs()

sub("Run evaluations")
print(f"  {'Run':<10} {'Latency':>8} {'Correct':>9} {'Concise':>9}")
print(f"  {'-'*10} {'-'*8} {'-'*9} {'-'*9}")
for r in ls_results:
    print(f"  {r['run_id']:<10} {r['latency_ms']:>7.1f}ms "
          f"{r['evaluations']['correctness']:>8.2f} "
          f"{r['evaluations']['conciseness']:>8.2f}")


# =====================================================================
# 4. Phoenix (Arize)
# =====================================================================
header(4, "Phoenix-Style Evaluation (Arize)")
print("OpenTelemetry-based tracing with inline evaluation spans.")

phoenix = PhoenixStyleEvaluator(project_name="rag_project")
phoenix_results = phoenix.evaluate_rag(rag_dataset)

sub("Traced evaluations")
for r in phoenix_results:
    evals = r["evaluations"]
    faith_s = evals["faithfulness"]["score"]
    rel_s = evals["relevance"]["score"]
    faith_l = evals["faithfulness"]["label"]
    rel_l = evals["relevance"]["label"]
    print(f"  [{r['id']}] faithfulness={faith_s:.2f} ({faith_l})  "
          f"relevance={rel_s:.2f} ({rel_l})")

sub("Trace summary")
summary = phoenix.get_trace_summary()
print(f"  Project: {summary['project']}  |  Total spans: {summary['total_spans']}")
print(f"  Span types: {summary['span_types']}")


# =====================================================================
# 5. OpenAI Evals
# =====================================================================
header(5, "OpenAI Evals-Style Evaluation")
print("Registry-based evals with exact/fuzzy match and model-graded criteria.")

oai_evals = OpenAIEvalsStyleEvaluator()

# Register MCQ accuracy eval
oai_evals.register_eval("mcq_accuracy", lambda s: s.get("prediction") == s.get("ground_truth"))

# Register RAG faithfulness eval
oai_evals.register_eval("rag_faithfulness", lambda s: (
    1.0 - _contains_extra_info(
        s.get("answer", ""),
        _context_as_str(s.get("contexts", ""))
    )) > 0.6)

# Prepare MCQ samples with simulated predictions
import random
rng = random.Random(42)
mcq_samples = []
for q in mcq_examples:
    pred = q["ground_truth"] if rng.random() < 0.7 else rng.choice(
        [c for c in "ABCDE" if c != q["ground_truth"]])
    mcq_samples.append({"id": q["id"], "prediction": pred, "ground_truth": q["ground_truth"]})

sub("MCQ accuracy eval")
mcq_result = oai_evals.run_eval("mcq_accuracy", mcq_samples)
print(f"  Accuracy: {mcq_result['accuracy']:.1%}  ({mcq_result['passed']}/{mcq_result['total']})")
for d in mcq_result["details"]:
    print(f"    Q{d['id']}: {'PASS' if d['passed'] else 'FAIL'}")

sub("RAG faithfulness eval")
rag_samples = [{"id": r["id"], "answer": r["answer"], "contexts": r["contexts"]}
               for r in rag_dataset]
faith_result = oai_evals.run_eval("rag_faithfulness", rag_samples)
print(f"  Pass rate: {faith_result['accuracy']:.1%}  ({faith_result['passed']}/{faith_result['total']})")


# =====================================================================
# 6. Promptfoo
# =====================================================================
header(6, "Promptfoo-Style Evaluation")
print("Config-driven test assertions with pass/fail results per prompt.")

promptfoo = PromptfooStyleEvaluator()

for tc in test_cases[:3]:
    assertions = [
        {"type": "contains", "value": tc["input"].split()[0]},
        {"type": "max-length", "value": 500},
        {"type": "similar", "value": tc["context"], "threshold": 0.3},
    ]
    promptfoo.add_test(tc["input"], tc["output"], assertions, context=tc["context"])

outputs = [tc["output"] for tc in test_cases[:3]]
pf_results = promptfoo.run_tests(outputs)

sub("Assertion results")
for r in pf_results:
    status = "ALL PASS" if r["all_passed"] else "SOME FAIL"
    print(f"\n  Test {r['test_index']}: \"{r['prompt']}\"  [{status}]")
    for a in r["assertions"]:
        mark = "PASS" if a["passed"] else "FAIL"
        print(f"    [{mark}] {a['type']:15s} -> {a['reason']}")


# =====================================================================
# 7. TruLens
# =====================================================================
header(7, "TruLens-Style Evaluation")
print("Feedback functions wrapping an app to compute quality scores per record.")

trulens = TruLensStyleEvaluator(app_name="RAG Pipeline v1")

trulens.add_feedback(
    "groundedness",
    lambda output, ctx: 1.0 - _contains_extra_info(output, ctx),
)
trulens.add_feedback(
    "relevance",
    lambda output, ctx: min(_word_overlap(output, ctx) + 0.4, 1.0),
)
trulens.add_feedback(
    "sentiment",
    lambda output, ctx: 0.7 + 0.1 * (len(output) % 3),  # mock
    higher_is_better=True,
)

for item in rag_dataset:
    trulens.record(item["question"], item["answer"], item["contexts"])

sub("Per-record feedback")
for rec in trulens.records:
    fb = rec["feedback"]
    print(f"  [{rec['record_id']}] groundedness={fb['groundedness']:.2f}  "
          f"relevance={fb['relevance']:.2f}  sentiment={fb['sentiment']:.2f}")

sub("Leaderboard")
lb = trulens.get_leaderboard()
print(f"  App: {lb['app']}  |  Records: {lb['num_records']}")
for name, stats in lb["metrics"].items():
    print(f"    {name:15s}  mean={stats['mean']:.3f}  "
          f"min={stats['min']:.2f}  max={stats['max']:.2f}")


# =====================================================================
# 8. Inspect AI
# =====================================================================
header(8, "Inspect AI-Style Evaluation")
print("Task/solver/scorer pattern for structured evaluations.")

# MCQ task
mcq_task = InspectTask("mcq_science", mcq_examples)
mcq_task.set_solver(lambda item: item["ground_truth"] if random.Random(
    item["id"]).random() < 0.8 else "A")

mcq_task.add_scorer("exact_match", lambda item, output: 1.0 if output == item["ground_truth"] else 0.0)
mcq_task.add_scorer("partial", lambda item, output: 0.5 if output != item["ground_truth"] else 1.0)

# RAG task
rag_task = InspectTask("rag_faithfulness", rag_dataset)
rag_task.set_solver(lambda item: item["answer"])
rag_task.add_scorer("faithfulness", lambda item, output: round(
    1.0 - _contains_extra_info(output, " ".join(item["contexts"])), 2))
rag_task.add_scorer("relevance", lambda item, output: round(
    min(_word_overlap(item["question"], output) + 0.45, 1.0), 2))

inspect_eval = InspectStyleEvaluator()
inspect_eval.add_task(mcq_task)
inspect_eval.add_task(rag_task)
inspect_results = inspect_eval.run()

for tr in inspect_results:
    sub(f"Task: {tr['task']}")
    for s in tr["samples"]:
        scores_str = "  ".join(f"{k}={v:.2f}" for k, v in s["scores"].items())
        print(f"  [{s['id']}] {scores_str}")
    print(f"\n  Aggregate: {tr['aggregate']}")


# =====================================================================
# 9. Evidently AI
# =====================================================================
header(9, "Evidently AI-Style Evaluation")
print("Data drift detection and LLM output monitoring between reference/current.")

evidently = EvidentlyStyleEvaluator()

# Use first 3 examples as reference, last 2 as "current" (simulating production shift)
evidently.set_reference(rag_dataset[:3])
evidently.set_current(rag_dataset[3:])

report = evidently.generate_report()

sub("Drift report")
print(f"  Reference size: {report['reference_size']}  |  Current size: {report['current_size']}")

tl = report["text_length_drift"]
print(f"\n  Text Length Drift:")
print(f"    Reference mean: {tl['reference']['mean']:.1f}  std: {tl['reference']['std']:.1f}")
print(f"    Current mean:   {tl['current']['mean']:.1f}  std: {tl['current']['std']:.1f}")
print(f"    Drift score:    {tl['drift_score']:.3f}  Drifted: {tl['is_drifted']}")

qd = report["quality_drift"]
print(f"\n  Answer Quality Drift:")
print(f"    Reference mean: {qd['reference']['mean']:.3f}  std: {qd['reference']['std']:.3f}")
print(f"    Current mean:   {qd['current']['mean']:.3f}  std: {qd['current']['std']:.3f}")
print(f"    Drift score:    {qd['drift_score']:.3f}  Drifted: {qd['is_drifted']}")


# =====================================================================
# 10. Maxim AI
# =====================================================================
header(10, "Maxim AI-Style Evaluation")
print("End-to-end quality monitoring with pluggable check functions.")

maxim = MaximAIStyleEvaluator(pipeline_name="production_rag")

maxim.add_quality_check("groundedness", lambda e: 1.0 - _contains_extra_info(
    e.get("answer", ""), " ".join(e.get("contexts", []))))
maxim.add_quality_check("completeness", lambda e: min(
    _word_overlap(e.get("answer", ""), e.get("reference", "")) + 0.35, 1.0))
maxim.add_quality_check("conciseness", lambda e: min(
    1.0, 80.0 / max(len(e.get("answer", "")), 1)))

maxim_results = maxim.evaluate(rag_dataset)

sub("Per-entry quality checks")
print(f"  {'ID':<10} {'Ground':>8} {'Complete':>9} {'Concise':>9}")
print(f"  {'-'*10} {'-'*8} {'-'*9} {'-'*9}")
for r in maxim_results["results"]:
    c = r["checks"]
    print(f"  {r['id']:<10} {c['groundedness']:>8.2f} {c['completeness']:>8.2f} "
          f"{c['conciseness']:>8.2f}")

sub("Aggregate")
for name, val in maxim_results["aggregate"].items():
    print(f"  {name:15s}  {val:.3f}")


# =====================================================================
# COMPARISON TABLE
# =====================================================================
print(f"\n\n{'='*70}")
print("  FRAMEWORK COMPARISON TABLE")
print(f"{'='*70}")

frameworks = [
    ("DeepEval",      "Unit-test metrics",    "Open-source",   "RAG + custom evals"),
    ("RAGAS",         "Component RAG metrics", "Open-source",  "RAG pipelines"),
    ("LangSmith",     "Run-based + tracing",   "Freemium",     "LangChain apps"),
    ("Phoenix",       "OTel tracing + evals",  "Open-source",  "Observability"),
    ("OpenAI Evals",  "Registry-based",        "Open-source",  "OpenAI model evals"),
    ("Promptfoo",     "Config-driven asserts",  "Open-source", "CI/CD prompt testing"),
    ("TruLens",       "Feedback functions",     "Open-source",  "App quality monitoring"),
    ("Inspect AI",    "Task/solver/scorer",     "Open-source",  "AI safety research"),
    ("Evidently AI",  "Drift + monitoring",     "Open-source",  "Production monitoring"),
    ("Maxim AI",      "E2E quality scoring",    "SaaS",         "Enterprise pipelines"),
]

print(f"\n  {'Framework':<14} {'Approach':<22} {'Pricing':<14} {'Best For'}")
print(f"  {'-'*14} {'-'*22} {'-'*14} {'-'*24}")
for name, approach, pricing, best_for in frameworks:
    print(f"  {name:<14} {approach:<22} {pricing:<14} {best_for}")

print(f"\n  Key differentiators:")
print(f"  - DeepEval/RAGAS   : Purpose-built for RAG evaluation with standard metrics")
print(f"  - LangSmith/Phoenix: Full observability (tracing + evals) for production LLM apps")
print(f"  - Promptfoo        : Best for CI/CD integration and regression testing prompts")
print(f"  - TruLens          : Feedback loops for iterative quality improvement")
print(f"  - Inspect AI       : Designed for AI safety benchmarks (UK AISI)")
print(f"  - Evidently AI     : Statistical drift detection applied to LLM outputs")
print(f"  - OpenAI Evals     : Standardized eval specs, model-graded criteria")
print(f"  - Maxim AI         : Enterprise SaaS with end-to-end pipeline monitoring")

print(f"\n  WHY LANGFUSE FOR EVALUATION?")
print(f"  Langfuse bridges the gap between offline evaluation (DeepEval, RAGAS) and")
print(f"  production monitoring (Phoenix, LangSmith). You can run your evaluation suite,")
print(f"  send the scores to Langfuse as trace annotations, and track how metrics change")
print(f"  across prompt versions and model updates. It also supports datasets and prompt")
print(f"  management, so your evaluation workflow lives alongside your production traces.")

print(f"\n{'='*70}")
print(f"  Demo complete.")
print(f"{'='*70}\n")
