import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 10 - LLM Application Observability
Main demonstration: tracing, logging, latency analysis, token/cost tracking,
prompt versioning, response quality monitoring, and a unified dashboard.
"""

import os
import json
import random
import math

# Local imports
from dataset import (
    load_sample_data,
    estimate_tokens,
    simulate_llm_response,
)
from evaluator import (
    TraceManager,
    LLMLogger,
    LatencyTracker,
    TokenCounter,
    CostCalculator,
    PromptTracker,
    ResponseMonitor,
    ObservabilityDashboard,
)


def separator(title: str, char: str = "=", width: int = 70):
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def main():
    # Load sample data
    data = load_sample_data()

    # ===================================================================
    # 1. TRACING
    # ===================================================================
    separator("1. DISTRIBUTED TRACING")
    print("Traces capture the full lifecycle of an LLM call as a tree of spans.")

    # Load sample traces and display
    tm = TraceManager()
    tm.load_from_sample(data["sample_traces"])

    print(f"\n  Loaded {len(tm.traces)} sample traces\n")
    for trace_id in tm.traces:
        print(f"  Trace: {trace_id}")
        tm.print_trace(trace_id)
        print()

    # Create a live trace
    print("  --- Creating a live trace ---")
    tid = tm.create_trace("live_demo")
    root = tm.start_span(tid, "pipeline.run", attributes={"demo": True})
    fmt_span = tm.start_span(tid, "prompt.format", parent_span_id=root.span_id)
    tm.end_span(fmt_span)
    llm_span = tm.start_span(tid, "llm.call", parent_span_id=root.span_id,
                             attributes={"model": "gpt-4"})
    tm.end_span(llm_span)
    parse_span = tm.start_span(tid, "response.parse", parent_span_id=root.span_id)
    tm.end_span(parse_span)
    tm.end_span(root)

    print(f"  Live trace ({tid}):")
    tm.print_trace(tid)

    # ===================================================================
    # 2. STRUCTURED LOGGING
    # ===================================================================
    separator("2. STRUCTURED LLM LOGGING")
    print("Structured logs attach metadata (tokens, cost, model) to every event.")

    logger = LLMLogger()
    logger.load_from_sample(data["sample_logs"])

    # Add some more logs from simulated calls
    rng = random.Random(42)
    for i in range(8):
        latency = round(rng.lognormvariate(math.log(1500), 0.5), 1)
        latency = max(400, min(latency, 12000))
        tokens_in = rng.randint(180, 350)
        tokens_out = rng.randint(10, 100)
        model = "gpt-4"
        cost = (tokens_in / 1000) * 0.03 + (tokens_out / 1000) * 0.06
        logger.info("pipeline", f"Query {i} processed",
                    question_id=i, latency_ms=round(latency, 1))
        logger.info("llm", f"LLM call completed",
                    model=model, input_tokens=tokens_in,
                    output_tokens=tokens_out, cost_usd=round(cost, 5))
        if latency > 3000:
            logger.warning("llm", f"Slow call: {latency:.0f}ms",
                           question_id=i, latency_ms=round(latency, 1))
        if rng.random() < 0.1:
            logger.error("evaluation", "Incorrect prediction",
                         question_id=i, expected="A", predicted="C")

    print(f"\n  Total log entries: {len(logger.logs)}")
    summary = logger.summary()
    for level, count in sorted(summary.items()):
        print(f"  {level}: {count}")

    print("\n  --- Recent logs ---")
    logger.print_logs(last_n=8)

    print("\n  --- Errors only ---")
    logger.print_logs(level="ERROR")

    # ===================================================================
    # 3. LATENCY MONITORING
    # ===================================================================
    separator("3. LATENCY MONITORING")
    print("Percentile tracking (P50/P95/P99) reveals tail latency issues.")

    tracker = LatencyTracker(threshold_ms=3000.0)

    # Generate realistic latency data
    rng = random.Random(42)
    latencies = [max(400, min(rng.lognormvariate(math.log(1500), 0.5), 12000))
                 for _ in range(50)]
    tracker.record_batch(latencies)

    print("\n  Latency Statistics:")
    tracker.print_stats()

    print("\n  Latency Distribution:")
    tracker.print_histogram(bins=6)

    slow = tracker.get_slow_calls()
    print(f"\n  Slow calls (>{tracker.threshold_ms}ms): {len(slow)}")
    for s in slow[:3]:
        print(f"    Call #{s['index']}: {s['latency_ms']:.0f}ms")

    # ===================================================================
    # 4. TOKEN USAGE TRACKING
    # ===================================================================
    separator("4. TOKEN USAGE TRACKING")
    print("Token counts drive cost and help optimize prompt length.")

    counter = TokenCounter()
    rng = random.Random(42)
    for i in range(50):
        inp = rng.randint(180, 350)
        out = rng.randint(10, 120)
        counter.record(inp, out, model="gpt-4", question_id=i)

    # A few calls on a cheaper model for comparison
    for i in range(10):
        inp = rng.randint(180, 350)
        out = rng.randint(10, 120)
        counter.record(inp, out, model="gpt-3.5-turbo", question_id=100 + i)

    print("\n  Token Usage Statistics:")
    counter.print_stats()

    print("\n  Usage by model:")
    for model, stats in counter.by_model().items():
        print(f"    {model}: {stats['calls']} calls, "
              f"{stats['input_tokens']:,} in / {stats['output_tokens']:,} out")

    # Token estimation demo
    print("\n  --- Token estimation ---")
    sample_text = "You are an expert scientist. Answer the following multiple choice question."
    estimated = TokenCounter.estimate(sample_text)
    print(f"  Text: \"{sample_text}\"")
    print(f"  Estimated tokens: {estimated}")

    # ===================================================================
    # 5. COST CALCULATION
    # ===================================================================
    separator("5. COST CALCULATION")
    print("Per-model pricing turns token counts into dollar costs.")

    calc = CostCalculator()

    # Calculate costs for all token records
    for rec in counter.records:
        calc.calculate(rec["input_tokens"], rec["output_tokens"], model=rec["model"])

    print("\n  Cost Summary:")
    calc.print_summary()

    # Model comparison
    print("\n  --- Model cost comparison (for 10,000 input + 2,000 output tokens) ---")
    comparison = calc.compare_models(10000, 2000)
    print(f"  {'Model':<20} {'Input':>10} {'Output':>10} {'Total':>10}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
    for c in comparison:
        print(f"  {c['model']:<20} ${c['input_cost']:>8.4f} "
              f"${c['output_cost']:>8.4f} ${c['total_cost']:>8.4f}")

    # ===================================================================
    # 6. PROMPT VERSION TRACKING
    # ===================================================================
    separator("6. PROMPT VERSION TRACKING")
    print("Versioned prompts let you measure which wording works best.")

    pt = PromptTracker()
    pt.load_from_sample(data["prompt_versions"])

    # Simulate results for each version
    rng = random.Random(42)
    version_accuracy = {"v1": 0.58, "v2": 0.68, "v3": 0.72}
    version_tokens = {"v1": 180, "v2": 240, "v3": 290}

    for version, acc in version_accuracy.items():
        for _ in range(50):
            correct = rng.random() < acc
            confidence = rng.uniform(0.75, 0.98) if correct else rng.uniform(0.30, 0.75)
            latency = max(400, min(rng.lognormvariate(math.log(1500), 0.5), 12000))
            tokens = version_tokens[version] + rng.randint(-20, 20)
            pt.record_result(version, correct=correct, confidence=round(confidence, 3),
                             latency_ms=round(latency, 1), tokens=tokens)

    print("\n  Prompt Version Comparison:")
    pt.print_comparison()

    # ===================================================================
    # 7. RESPONSE QUALITY MONITORING
    # ===================================================================
    separator("7. RESPONSE QUALITY MONITORING")
    print("Track accuracy, format errors, and confidence calibration in real time.")

    monitor = ResponseMonitor(confidence_threshold=0.5)

    # Build simulated questions and feed to monitor
    rng = random.Random(42)
    choices = ["A", "B", "C", "D", "E"]
    for i in range(50):
        gt = rng.choice(choices)
        correct = rng.random() < 0.72
        if correct:
            pred = gt
            conf = round(rng.uniform(0.75, 0.98), 3)
        else:
            pred = rng.choice([c for c in choices if c != gt])
            conf = round(rng.uniform(0.30, 0.85), 3)
        fmt_ok = rng.random() > 0.04
        lat = max(400, min(rng.lognormvariate(math.log(1500), 0.5), 12000))
        monitor.record(predicted=pred, ground_truth=gt, confidence=conf,
                       format_ok=fmt_ok, latency_ms=round(lat, 1))

    print("\n  Quality Report:")
    monitor.print_report()

    hce = monitor.high_confidence_errors()
    if hce:
        print(f"\n  High-confidence errors (confident but wrong):")
        for r in hce[:5]:
            print(f"    Predicted={r['predicted']}, Truth={r['ground_truth']}, "
                  f"Confidence={r['confidence']:.2f}")

    # ===================================================================
    # 8. OBSERVABILITY DASHBOARD
    # ===================================================================
    separator("8. UNIFIED OBSERVABILITY DASHBOARD")
    print("A single view combining latency, tokens, cost, quality, and logs.")

    dashboard = ObservabilityDashboard(
        latency_tracker=tracker,
        token_counter=counter,
        cost_calculator=calc,
        response_monitor=monitor,
        llm_logger=logger,
        prompt_tracker=pt,
    )
    dashboard.render()

    # ===================================================================
    # 9. OBSERVABILITY TOOLS OVERVIEW
    # ===================================================================
    separator("9. OBSERVABILITY TOOLS OVERVIEW")
    print("Key platforms for production LLM observability.\n")

    tools = data["tool_comparison"]
    for name, info in tools.items():
        print(f"  {name}")
        print(f"    Focus: {info['focus']}")
        print(f"    Best for: {info['best_for']}")
        strengths = ", ".join(info["strengths"])
        print(f"    Strengths: {strengths}")
        print()

    # Quick reference table
    print("  --- Quick Comparison ---")
    print(f"  {'Tool':<25} {'Focus':<45}")
    print(f"  {'-'*25} {'-'*45}")
    for name, info in tools.items():
        print(f"  {name:<25} {info['focus']:<45}")

    # ===================================================================
    # 10. SUMMARY
    # ===================================================================
    separator("10. KEY TAKEAWAYS", char="=")
    takeaways = [
        "Trace every LLM call: trace_id + span_id give end-to-end visibility.",
        "Log structured data: attach tokens, cost, model to every log entry.",
        "Track percentiles: P50/P95/P99 reveal tail latency that means miss.",
        "Count tokens: they drive cost and help optimize prompt length.",
        "Calculate cost per query: tiny per-call costs compound at scale.",
        "Version your prompts: measure accuracy/latency per version.",
        "Monitor response quality: catch confidence drift and format errors.",
        "Use dashboards: one view for all signals prevents alert fatigue.",
    ]
    for i, t in enumerate(takeaways, 1):
        print(f"  {i}. {t}")

    separator("WHY USE LANGFUSE, LANGGRAPH & TRACING?")
    print("  Langfuse: Open-source observability platform built specifically for LLM apps.")
    print("  Unlike generic APM tools, it understands LLM concepts -- generations, prompts,")
    print("  scores, datasets. You get per-request cost tracking, quality scores, and prompt")
    print("  management in one dashboard. Self-host or use the cloud version.")
    print()
    print("  LangGraph: When your LLM app has multiple steps (retrieve, generate, evaluate),")
    print("  LangGraph makes each step a node in a state graph. The observability benefit:")
    print("  each node emits its own trace span, so you see latency and errors per step,")
    print("  not just per request. This is the difference between 'request took 5s' and")
    print("  'retrieval took 3s, generation took 1.5s, scoring took 0.5s.'")
    print()
    print("  Tracing connects the dots between all these tools -- OpenTelemetry spans flow")
    print("  into Phoenix, Langfuse, and LangSmith. One instrumentation, multiple dashboards.")

    print(f"\n{'=' * 70}")
    print("  Chapter 10 complete.")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
