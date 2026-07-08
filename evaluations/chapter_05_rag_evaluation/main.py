import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 5 - RAG Evaluation
Main entry point: demonstrates every RAG evaluation metric, runs the full
evaluation pipeline on sample data, and compares popular evaluation frameworks.

Run:
    cd chapter_05_rag_evaluation
    python main.py
"""

import json
import time

from dataset import load_sample_data, load_rag_examples
from evaluator import (
    RetrievalMetrics,
    GenerationMetrics,
    EndToEndMetrics,
    RAGEvaluationPipeline,
)

# ============================================================================
# PRETTY PRINTING HELPERS
# ============================================================================

SEPARATOR = "=" * 72
THIN_SEP = "-" * 72


def heading(title: str, level: int = 1) -> None:
    if level == 1:
        print(f"\n{SEPARATOR}")
        print(f"  {title}")
        print(SEPARATOR)
    else:
        print(f"\n{THIN_SEP}")
        print(f"  {title}")
        print(THIN_SEP)


def kv(key: str, value, indent: int = 2) -> None:
    prefix = " " * indent
    if isinstance(value, float):
        print(f"{prefix}{key}: {value:.4f}")
    else:
        print(f"{prefix}{key}: {value}")


# ============================================================================
# 1. DEMONSTRATE RETRIEVAL METRICS
# ============================================================================

def demo_retrieval_metrics(example: dict) -> None:
    heading("1. RETRIEVAL METRICS")

    ret = RetrievalMetrics()
    contexts = example["retrieved_contexts"]
    ctx_texts = [c["text"] for c in contexts]
    rel_labels = [c.get("relevance_label", 0) for c in contexts]
    query = example["query"]
    gt = example.get("ground_truth_answer", "")

    print(f"\n  Query: {query}")
    print(f"  Retrieved chunks: {len(contexts)}")
    print(f"  Relevance labels: {rel_labels}")

    # Context Precision
    heading("1a. Context Precision (Average Precision)", level=2)
    cp = ret.context_precision(ctx_texts, rel_labels)
    print(f"  Score: {cp:.4f}")

    # Context Recall
    heading("1b. Context Recall", level=2)
    cr = ret.context_recall(ctx_texts, gt, rel_labels)
    print(f"  Score: {cr:.4f}")

    # Context Relevance
    heading("1c. Context Relevance", level=2)
    crel = ret.context_relevance(query, ctx_texts)
    kv("Mean relevance", crel["mean_relevance"])
    for i, s in enumerate(crel["per_chunk_scores"]):
        label_str = "RELEVANT" if rel_labels[i] == 1 else "noise"
        print(f"    Chunk {i+1} ({label_str}): {s:.4f}")

    # Hit Rate / MRR
    heading("1d. Hit Rate & MRR", level=2)
    hr_mrr = ret.hit_rate_and_mrr(rel_labels)
    kv("Hit Rate", hr_mrr["hit_rate"])
    kv("MRR", hr_mrr["mrr"])

    # NDCG
    heading("1e. NDCG", level=2)
    ndcg_score = ret.ndcg(rel_labels)
    print(f"  NDCG: {ndcg_score:.4f}")
    ndcg_at_2 = ret.ndcg(rel_labels, k=2)
    print(f"  NDCG@2: {ndcg_at_2:.4f}")


# ============================================================================
# 2. DEMONSTRATE GENERATION METRICS
# ============================================================================

def demo_generation_metrics(example: dict) -> None:
    heading("2. GENERATION METRICS")

    gen = GenerationMetrics()
    query = example["query"]
    generated = example["generated_answer"]
    gt = example.get("ground_truth_answer", "")
    contexts = example["retrieved_contexts"]
    ctx_texts = [c["text"] for c in contexts]
    citations = example.get("citations", [])

    print(f"\n  Query: {query}")
    print(f"  Answer (first 120 chars): {generated[:120]}...")
    print(f"  Quality label: {example.get('quality_label', '?')}")

    # Answer Relevance
    heading("2a. Answer Relevance", level=2)
    ar = gen.answer_relevance(query, generated)
    kv("Score", ar["score"])
    kv("Unigram overlap", ar["unigram_overlap"])
    kv("Bigram overlap", ar["bigram_overlap"])

    # Faithfulness
    heading("2b. Faithfulness", level=2)
    faith = gen.faithfulness(generated, ctx_texts)
    kv("Score", faith["score"])
    print(f"  Supported claims: {faith['supported_claims']}/{faith['total_claims']}")
    for d in faith["details"]:
        status = "SUPPORTED" if d["supported"] else "UNSUPPORTED"
        print(f"    [{status}] (overlap={d['overlap']:.2f}) {d['claim']}")

    # Groundedness
    heading("2c. Groundedness", level=2)
    grd = gen.groundedness(generated, ctx_texts)
    kv("Score", grd["score"])
    kv("Entity coverage", grd["entity_coverage"])
    kv("Token coverage", grd["token_coverage"])

    # Citation Correctness
    heading("2d. Citation Correctness", level=2)
    cc = gen.citation_correctness(generated, citations, ctx_texts)
    kv("Score", cc["score"])
    print(f"  Correct citations: {cc['correct_citations']}/{cc['total_citations']}")
    for d in cc["details"]:
        status = "CORRECT" if d["correct"] else "INCORRECT"
        print(f"    [{status}] Citation [{d['citation']}] overlap={d['overlap']:.2f}")

    # Source Attribution
    heading("2e. Source Attribution", level=2)
    sa = gen.source_attribution(generated, citations, ctx_texts)
    kv("Coverage", sa["coverage"])
    kv("Accuracy", sa["accuracy"])
    kv("Combined score", sa["score"])

    # Hallucination Detection
    heading("2f. Hallucination Detection", level=2)
    hd = gen.hallucination_detection(generated, ctx_texts, gt)
    kv("Risk score", hd["risk_score"])
    print(f"  Hallucination detected: {hd['hallucination_detected']}")
    if hd["flagged_claims"]:
        print("  Flagged claims:")
        for fc in hd["flagged_claims"]:
            print(f"    - ctx_overlap={fc['context_overlap']:.2f}, "
                  f"gt_overlap={fc['gt_overlap']:.2f}: {fc['claim']}")
    else:
        print("  No claims flagged.")


# ============================================================================
# 3. DEMONSTRATE END-TO-END METRICS
# ============================================================================

def demo_end_to_end_metrics(example: dict) -> None:
    heading("3. END-TO-END METRICS")

    e2e = EndToEndMetrics()
    generated = example["generated_answer"]
    gt = example.get("ground_truth_answer", "")
    contexts = example["retrieved_contexts"]
    ctx_texts = [c["text"] for c in contexts]
    rel_labels = [c.get("relevance_label", 0) for c in contexts]
    query = example["query"]

    # Context Utilization
    heading("3a. Context Utilization", level=2)
    cu = e2e.context_utilization(generated, ctx_texts)
    kv("Score (mean utilization)", cu["score"])
    print(f"  Chunks used: {cu['chunks_used']}/{cu['total_chunks']}")
    for i, u in enumerate(cu["per_chunk_utilization"]):
        label = "RELEVANT" if rel_labels[i] == 1 else "noise"
        print(f"    Chunk {i+1} ({label}): utilization = {u:.4f}")

    # Answer Correctness
    heading("3b. Answer Correctness", level=2)
    ac = e2e.answer_correctness(generated, gt)
    kv("Composite score", ac["score"])
    kv("Token F1", ac["f1"])
    kv("Precision", ac["precision"])
    kv("Recall", ac["recall"])
    kv("Jaccard", ac["jaccard"])
    kv("Entity overlap", ac["entity_overlap"])

    # Chunk Evaluation
    heading("3c. Chunk Evaluation", level=2)
    ce = e2e.chunk_evaluation(ctx_texts, rel_labels, query)
    kv("Avg query relevance", ce["avg_query_relevance"])
    kv("Avg info density", ce["avg_info_density"])
    for c in ce["per_chunk"]:
        label = "RELEVANT" if c["label"] == 1 else "noise"
        print(f"    Chunk {c['chunk_index']+1} ({label}): "
              f"relevance={c['query_relevance']:.3f}, "
              f"density={c['info_density']:.3f}, "
              f"redundancy={c['max_redundancy']:.3f}, "
              f"tokens={c['token_count']}")

    # Latency Tracking
    heading("3d. Latency Tracking", level=2)
    timer = e2e.measure_latency("simulated_pipeline")
    timer["start"]()
    _ = sum(range(100000))
    timer["stop"]()
    print(f"  Simulated pipeline latency: {timer['latency_seconds']:.6f}s")

    @EndToEndMetrics.latency_tracker
    def sample_retrieval():
        return [1, 2, 3]

    lr = sample_retrieval()
    print(f"  Decorated function latency: {lr['latency_seconds']:.6f}s")

    # Cost Tracking
    heading("3e. Cost Tracking", level=2)
    models = ["gpt-4", "gpt-4o", "claude-3-sonnet", "claude-3-haiku"]
    input_tokens = 4000
    output_tokens = 500
    print(f"  Scenario: {input_tokens} input tokens, {output_tokens} output tokens\n")
    print(f"  {'Model':<22} {'Input $':>10} {'Output $':>10} {'Total $':>10}")
    print(f"  {'-'*22} {'-'*10} {'-'*10} {'-'*10}")
    for model in models:
        cost = e2e.cost_tracker(input_tokens, output_tokens, model)
        print(f"  {model:<22} {cost['input_cost_usd']:>10.5f} "
              f"{cost['output_cost_usd']:>10.5f} {cost['total_cost_usd']:>10.5f}")


# ============================================================================
# 4. FULL PIPELINE EVALUATION ON ALL EXAMPLES
# ============================================================================

def demo_full_pipeline(examples: list[dict]) -> None:
    heading("4. FULL PIPELINE EVALUATION - ALL EXAMPLES")

    pipeline = RAGEvaluationPipeline()

    print(f"\n  Evaluating {len(examples)} RAG examples with all metrics...")
    start = time.perf_counter()
    report = pipeline.evaluate_dataset(examples)
    elapsed = time.perf_counter() - start
    print(f"  Completed in {elapsed:.4f}s\n")

    # Per-example summary table
    heading("4a. Per-Example Summary", level=2)
    header = (f"  {'ID':>3} {'Quality':<18} {'Ctx-Prec':>9} {'Ctx-Rec':>9} "
              f"{'NDCG':>6} {'Faith':>7} {'Ground':>7} {'Halluc':>7} "
              f"{'Correct':>8}")
    print(header)
    print("  " + "-" * len(header.strip()))
    for r in report["per_example"]:
        print(
            f"  {r['id']:>3} {r['quality_label']:<18} "
            f"{r['retrieval']['context_precision']:>9.4f} "
            f"{r['retrieval']['context_recall']:>9.4f} "
            f"{r['retrieval']['ndcg']:>6.4f} "
            f"{r['generation']['faithfulness']['score']:>7.4f} "
            f"{r['generation']['groundedness']['score']:>7.4f} "
            f"{r['generation']['hallucination_detection']['risk_score']:>7.4f} "
            f"{r['end_to_end']['answer_correctness']['score']:>8.4f}"
        )

    # Aggregates
    heading("4b. Aggregate Metrics", level=2)
    agg = report["aggregates"]
    print(f"  Number of examples:         {agg['num_examples']}")
    print("\n  RETRIEVAL AVERAGES:")
    print(f"    Context Precision:         {agg['avg_context_precision']:.4f}")
    print(f"    Context Recall:            {agg['avg_context_recall']:.4f}")
    print(f"    NDCG:                      {agg['avg_ndcg']:.4f}")
    print(f"    Hit Rate:                  {agg['avg_hit_rate']:.4f}")
    print(f"    MRR:                       {agg['avg_mrr']:.4f}")
    print("\n  GENERATION AVERAGES:")
    print(f"    Answer Relevance:          {agg['avg_answer_relevance']:.4f}")
    print(f"    Faithfulness:              {agg['avg_faithfulness']:.4f}")
    print(f"    Groundedness:              {agg['avg_groundedness']:.4f}")
    print(f"    Citation Correctness:      {agg['avg_citation_correctness']:.4f}")
    print(f"    Hallucination Risk:        {agg['avg_hallucination_risk']:.4f}")
    print("\n  END-TO-END AVERAGES:")
    print(f"    Answer Correctness:        {agg['avg_answer_correctness']:.4f}")
    print(f"    Context Utilization:       {agg['avg_context_utilization']:.4f}")

    # Identify worst performers
    heading("4c. Diagnostic Insights", level=2)
    worst_faith = min(report["per_example"],
                      key=lambda r: r["generation"]["faithfulness"]["score"])
    worst_halluc = max(report["per_example"],
                       key=lambda r: r["generation"]["hallucination_detection"]["risk_score"])
    worst_correct = min(report["per_example"],
                        key=lambda r: r["end_to_end"]["answer_correctness"]["score"])
    print(f"  Lowest faithfulness:    ID {worst_faith['id']} "
          f"(quality={worst_faith['quality_label']}, "
          f"score={worst_faith['generation']['faithfulness']['score']:.4f})")
    print(f"  Highest halluc. risk:   ID {worst_halluc['id']} "
          f"(quality={worst_halluc['quality_label']}, "
          f"score={worst_halluc['generation']['hallucination_detection']['risk_score']:.4f})")
    print(f"  Lowest correctness:     ID {worst_correct['id']} "
          f"(quality={worst_correct['quality_label']}, "
          f"score={worst_correct['end_to_end']['answer_correctness']['score']:.4f})")


# ============================================================================
# 5. COMPARE GOOD vs. HALLUCINATED ANSWERS
# ============================================================================

def demo_quality_comparison(examples: list[dict]) -> None:
    heading("5. QUALITY COMPARISON: GOOD vs. HALLUCINATED ANSWERS")

    pipeline = RAGEvaluationPipeline()

    good_examples = [e for e in examples if e.get("quality_label") == "good"]
    bad_examples = [e for e in examples
                    if e.get("quality_label") in ("poor_hallucinated", "poor_fabricated")]

    if not good_examples or not bad_examples:
        print("  Not enough variety in quality labels for comparison.")
        return

    good_report = pipeline.evaluate_dataset(good_examples)
    bad_report = pipeline.evaluate_dataset(bad_examples)

    ga = good_report["aggregates"]
    ba = bad_report["aggregates"]

    metrics = [
        ("Faithfulness",        ga["avg_faithfulness"],        ba["avg_faithfulness"]),
        ("Groundedness",        ga["avg_groundedness"],        ba["avg_groundedness"]),
        ("Hallucination Risk",  ga["avg_hallucination_risk"],  ba["avg_hallucination_risk"]),
        ("Answer Correctness",  ga["avg_answer_correctness"],  ba["avg_answer_correctness"]),
        ("Citation Correctness",ga["avg_citation_correctness"],ba["avg_citation_correctness"]),
        ("Context Utilization", ga["avg_context_utilization"], ba["avg_context_utilization"]),
    ]

    print(f"\n  {'Metric':<24} {'Good (n={0})'.format(len(good_examples)):>14} "
          f"{'Halluc (n={0})'.format(len(bad_examples)):>14} {'Delta':>10}")
    print(f"  {'-'*24} {'-'*14} {'-'*14} {'-'*10}")
    for name, good_val, bad_val in metrics:
        delta = good_val - bad_val
        direction = "+" if delta >= 0 else ""
        print(f"  {name:<24} {good_val:>14.4f} {bad_val:>14.4f} {direction}{delta:>9.4f}")


# ============================================================================
# 6. FRAMEWORK COMPARISON
# ============================================================================

def demo_framework_comparison() -> None:
    heading("6. RAG EVALUATION FRAMEWORK COMPARISON")

    frameworks = [
        ("RAGAS",          6, "LLM-as-judge with structured decomposition"),
        ("DeepEval",       7, "LLM-as-judge with pytest integration"),
        ("TruLens",        5, "Feedback functions with LLM or embedding models"),
        ("LangSmith",      4, "Human + LLM annotation platform with tracing"),
        ("Phoenix (Arize)",3, "Observability-first with embedding analysis"),
    ]

    print(f"\n  {'Framework':<18} {'# Metrics':>10} {'Approach'}")
    print(f"  {'-'*18} {'-'*10} {'-'*40}")
    for name, n_metrics, approach in frameworks:
        print(f"  {name:<18} {n_metrics:>10} {approach}")

    print("\n  See theory.md for detailed per-framework strengths/limitations.")


# ============================================================================
# 7. METRIC TAXONOMY SUMMARY
# ============================================================================

def print_metric_taxonomy() -> None:
    heading("7. COMPLETE RAG METRIC TAXONOMY")

    taxonomy = {
        "RETRIEVAL METRICS": {
            "Context Precision": "Are relevant docs ranked higher than irrelevant ones?",
            "Context Recall": "Do retrieved docs cover the ground-truth information?",
            "Context Relevance": "How topically related is each chunk to the query?",
            "Hit Rate": "Was at least one relevant doc retrieved?",
            "MRR": "How high is the first relevant doc ranked?",
            "NDCG": "Overall ranking quality with position discount.",
        },
        "GENERATION METRICS": {
            "Answer Relevance": "Does the answer address the query?",
            "Faithfulness": "Is every claim in the answer supported by context?",
            "Groundedness": "Is the answer grounded in entity and content overlap?",
            "Citation Correctness": "Do citations point to the right sources?",
            "Source Attribution": "Are claims properly attributed to sources?",
            "Hallucination Detection": "Are there fabricated/unsupported claims?",
        },
        "END-TO-END METRICS": {
            "Context Utilization": "How much retrieved context is actually used?",
            "Answer Correctness": "Does the answer match the ground truth?",
            "Chunk Evaluation": "Per-chunk quality (relevance, density, redundancy).",
            "Latency Tracking": "Pipeline execution time measurement.",
            "Cost Tracking": "Estimated dollar cost per model.",
        },
    }

    for category, metrics in taxonomy.items():
        print(f"\n  {category}:")
        for name, description in metrics.items():
            print(f"    {name:<26} {description}")

    total = sum(len(m) for m in taxonomy.values())
    print(f"\n  Total metrics implemented: {total}")


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    heading("CHAPTER 5: RAG EVALUATION", level=1)

    # Load data
    examples = load_rag_examples()
    print(f"\n  Loaded {len(examples)} RAG examples from sample_data.json")

    # Pick representative examples for detailed demos
    good_example = next(e for e in examples if e["quality_label"] == "good")
    halluc_example = next(
        (e for e in examples if "halluc" in e.get("quality_label", "").lower()
         or "fabricat" in e.get("quality_label", "").lower()),
        examples[-1],
    )

    # --- Detailed metric demos on a good example ---
    print(f"\n  Demonstrating all metrics on Example {good_example['id']} (quality=good)")
    demo_retrieval_metrics(good_example)
    demo_generation_metrics(good_example)
    demo_end_to_end_metrics(good_example)

    # --- Show a hallucinated example for contrast ---
    heading("HALLUCINATED EXAMPLE - Metric Contrast", level=2)
    print(f"\n  Evaluating Example {halluc_example['id']} "
          f"(quality={halluc_example['quality_label']})")
    gen = GenerationMetrics()
    ctx_texts = [c["text"] for c in halluc_example["retrieved_contexts"]]
    gt = halluc_example.get("ground_truth_answer", "")
    generated = halluc_example["generated_answer"]

    faith = gen.faithfulness(generated, ctx_texts)
    halluc = gen.hallucination_detection(generated, ctx_texts, gt)
    print(f"  Faithfulness score:     {faith['score']:.4f}")
    print(f"  Hallucination risk:     {halluc['risk_score']:.4f}")
    print(f"  Flagged claims:         {len(halluc['flagged_claims'])}")

    # --- Full pipeline on all examples ---
    demo_full_pipeline(examples)

    # --- Quality comparison ---
    demo_quality_comparison(examples)

    # --- Framework comparison ---
    demo_framework_comparison()

    # --- Taxonomy ---
    print_metric_taxonomy()

    print("\n  Chapter 5 complete.")


if __name__ == "__main__":
    main()
