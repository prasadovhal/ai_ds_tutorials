"""
Chapter 10: Observability for LLM Systems - Hands-On
Tools: OpenTelemetry, Arize Phoenix, LangSmith, W&B, MLflow + manual fallback
"""
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import time
import random
import pandas as pd

DATA_PATH = r"D:\Study\Git_repo\evaluations\data\train.csv"
CHOICES = ["A", "B", "C", "D", "E"]
available_tools = []

# ---------------------------------------------------------------------------
# 1. Load 5 questions
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("CHAPTER 10: OBSERVABILITY FOR LLM SYSTEMS")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH, nrows=5)
    print(f"\nLoaded {len(df)} questions from train.csv")

    # Simulate answers and collect raw metrics
    records = []
    latencies = []
    for _, row in df.iterrows():
        t0 = time.time()
        time.sleep(random.uniform(0.03, 0.12))          # simulate LLM call
        pred = random.choice(CHOICES)
        latency_ms = (time.time() - t0) * 1000
        correct = pred == row["answer"]
        prompt_text = row["prompt"]
        input_tok = len(prompt_text.split())
        output_tok = len(pred.split())
        records.append({
            "question_id": row["id"], "prompt": prompt_text[:80],
            "predicted": pred, "expected": row["answer"],
            "correct": correct, "input_tokens": input_tok,
            "output_tokens": output_tok, "latency_ms": round(latency_ms, 2),
        })
        latencies.append(latency_ms)

    accuracy = sum(r["correct"] for r in records) / len(records)
    avg_latency = sum(latencies) / len(latencies)
    print(f"Simulated {len(records)} predictions  |  accuracy={accuracy:.0%}")

    # ------------------------------------------------------------------
    # 2. OpenTelemetry tracing
    # ------------------------------------------------------------------
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            ConsoleSpanExporter, SimpleSpanProcessor,
        )

        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer("ch10-observability")

        with tracer.start_as_current_span("eval_pipeline") as parent:
            parent.set_attribute("num_questions", len(records))
            parent.set_attribute("accuracy", accuracy)
            for rec in records:
                with tracer.start_as_current_span("process_question") as child:
                    child.set_attribute("question_id", int(rec["question_id"]))
                    child.set_attribute("latency_ms", rec["latency_ms"])
                    child.set_attribute("input_tokens", rec["input_tokens"])
                    child.set_attribute("output_tokens", rec["output_tokens"])
                    child.set_attribute("correct", rec["correct"])

        available_tools.append("OpenTelemetry")
        print("[OK] OpenTelemetry  - spans exported to console")
    except Exception as e:
        print(f"[SKIP] OpenTelemetry not installed: {e}")

    # ------------------------------------------------------------------
    # 3. Arize Phoenix tracing
    # ------------------------------------------------------------------
    try:
        import phoenix as px
        from phoenix.otel import register

        tracer_provider = register(project_name="llm-eval-course")
        print("[OK] Phoenix registered - project 'llm-eval-course'")
        print("     Phoenix UI: http://localhost:6006  (run `phoenix serve` to start)")
        print("     Tip: Phoenix auto-instruments LLM calls via OpenTelemetry.")
        available_tools.append("Phoenix")
    except Exception as e:
        print(f"[SKIP] Arize Phoenix not installed: {e}")

    # ------------------------------------------------------------------
    # 4. LangSmith / LangGraph tracing
    # ------------------------------------------------------------------
    try:
        import os
        os.environ.setdefault("LANGSMITH_TRACING", "true")
        os.environ.setdefault("LANGSMITH_API_KEY", "your-key-here")
        os.environ.setdefault("LANGSMITH_PROJECT", "llm-eval-course")

        from langsmith import Client
        client = Client()

        # Log one run manually to show the API
        client.create_run(
            name="eval-question-0",
            run_type="llm",
            inputs={"prompt": records[0]["prompt"]},
            outputs={"answer": records[0]["predicted"]},
            extra={"latency_ms": records[0]["latency_ms"]},
        )
        print("[OK] LangSmith  - manual run logged for question 0")
        print("     Dashboard: https://smith.langchain.com")
        print("     Tip: with env vars set, ALL LangChain/LangGraph calls auto-trace.")
        available_tools.append("LangSmith")
    except Exception as e:
        print(f"[SKIP] LangSmith not installed: {e}")

    # ------------------------------------------------------------------
    # 5. Weights & Biases
    # ------------------------------------------------------------------
    try:
        import wandb

        wandb.init(project="llm-eval-course", mode="offline")
        wandb.log({"accuracy": accuracy, "avg_latency_ms": avg_latency,
                    "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)]})

        table = wandb.Table(columns=["question_id", "predicted", "expected", "correct"])
        for r in records:
            table.add_data(r["question_id"], r["predicted"], r["expected"], r["correct"])
        wandb.log({"results_table": table})

        wandb.finish()
        available_tools.append("W&B")
        print("[OK] W&B  - metrics + table logged (offline mode)")
    except Exception as e:
        print(f"[SKIP] Weights & Biases not installed: {e}")

    # ------------------------------------------------------------------
    # 6. MLflow
    # ------------------------------------------------------------------
    try:
        import mlflow

        mlflow.set_experiment("llm-eval-course")
        with mlflow.start_run(run_name="ch10-observability"):
            mlflow.log_param("num_questions", len(records))
            mlflow.log_param("model", "simulated")
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("avg_latency_ms", avg_latency)
            mlflow.log_metric("latency_p95",
                              sorted(latencies)[int(len(latencies) * 0.95)])

        available_tools.append("MLflow")
        print("[OK] MLflow  - experiment 'llm-eval-course' logged")
        print("     Dashboard: run `mlflow ui` then open http://localhost:5000")
    except Exception as e:
        print(f"[SKIP] MLflow not installed: {e}")

    # ------------------------------------------------------------------
    # 7. Langfuse tracing
    # ------------------------------------------------------------------
    try:
        from langfuse import Langfuse
        import sys as _sys
        _sys.path.insert(0, r"D:\Study\Git_repo\evaluations")
        from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

        langfuse = Langfuse(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_BASE_URL,
        )

        trace = langfuse.trace(
            name="ch10-observability-pipeline",
            metadata={"num_questions": len(records), "accuracy": accuracy},
        )

        for rec in records:
            generation = trace.generation(
                name=f"question-{rec['question_id']}",
                model="simulated",
                input=rec["prompt"],
                output=rec["predicted"],
                metadata={"latency_ms": rec["latency_ms"], "correct": rec["correct"]},
                usage={"input": rec["input_tokens"], "output": rec["output_tokens"]},
            )
            generation.score(name="correct", value=1.0 if rec["correct"] else 0.0)

        trace.score(name="accuracy", value=accuracy)
        trace.score(name="avg_latency_ms", value=avg_latency)
        langfuse.flush()

        available_tools.append("Langfuse")
        print("[OK] Langfuse  - traces + scores sent to cloud")
        print("     Dashboard: https://cloud.langfuse.com")
    except Exception as e:
        print(f"[SKIP] Langfuse not installed: {e}")

    # ------------------------------------------------------------------
    # 8. Manual observability (always works)
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("MANUAL OBSERVABILITY (always available)")
    print("=" * 60)

    # Token counting
    total_in = sum(r["input_tokens"] for r in records)
    total_out = sum(r["output_tokens"] for r in records)
    print(f"\nToken counts -> input: {total_in}  output: {total_out}  total: {total_in + total_out}")

    # Cost estimation
    cost_gpt4 = (total_in * 0.03 + total_out * 0.06) / 1000
    cost_gpt35 = (total_in * 0.0015 + total_out * 0.002) / 1000
    print(f"Est. cost -> GPT-4: ${cost_gpt4:.6f}  GPT-3.5: ${cost_gpt35:.6f}  Local: $0.0000")

    # Percentile computation with sorted list (no numpy needed)
    s = sorted(latencies)
    n = len(s)
    p50 = s[int(n * 0.50)]
    p95 = s[int(n * 0.95)]
    p99 = s[min(int(n * 0.99), n - 1)]
    print(f"\nLatency (ms) -> P50: {p50:.1f}  P95: {p95:.1f}  P99: {p99:.1f}  mean: {avg_latency:.1f}")

    # Per-question results
    print(f"\n{'question_id':>12} {'predicted':>10} {'expected':>10} {'correct':>8} {'latency_ms':>12}")
    print("-" * 56)
    for r in records:
        print(f"{r['question_id']:>12} {r['predicted']:>10} {r['expected']:>10} "
              f"{'Y' if r['correct'] else 'N':>8} {r['latency_ms']:>12.1f}")

    # ------------------------------------------------------------------
    # 9. Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"Tools active : {', '.join(available_tools) if available_tools else 'None (manual only)'}")
    print(f"Accuracy     : {accuracy:.0%}")
    print(f"Avg latency  : {avg_latency:.1f} ms")
    print(f"P95 latency  : {p95:.1f} ms")
    print(f"Total tokens : {total_in + total_out}")
    print(f"\nDashboard URLs (when tools are installed):")
    print(f"  Phoenix   : http://localhost:6006")
    print(f"  LangSmith : https://smith.langchain.com")
    print(f"  Langfuse  : https://cloud.langfuse.com")
    print(f"  MLflow    : http://localhost:5000")
    print(f"  W&B       : https://wandb.ai  (offline logs in ./wandb/)")
    print("\nDone!")


if __name__ == "__main__":
    main()
