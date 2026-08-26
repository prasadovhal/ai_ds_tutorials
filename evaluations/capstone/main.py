import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os, copy

# --- Module imports ---
from dataset_manager import load_data, create_golden_set, generate_synthetic, version_dataset, get_stats
from rag_pipeline import build_retriever, run_pipeline
from evaluator import full_evaluation
from regression import compare_versions, check_gates
from dashboard import render_dashboard, save_report


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, "..", "data")
    train_path = os.path.join(data_dir, "train.csv")
    corpus_path = os.path.join(data_dir, "wiki_stem_corpus.csv")

    # ---- Step 1: Load dataset ----
    print("[1/7] Loading dataset...")
    df = load_data(train_path, nrows=50)
    corpus = load_data(corpus_path, nrows=200)
    passages = corpus["text"].dropna().tolist()
    stats = get_stats(df)
    print(f"  Loaded {stats['num_rows']} questions, {len(passages)} passages")
    print(f"  Answer distribution: {stats.get('answer_distribution', {})}")

    # ---- Step 2: Create golden set ----
    print("\n[2/7] Creating golden set...")
    golden = create_golden_set(df, n=30)
    version_info = version_dataset(golden, version="v1.0")
    print(f"  Golden set: {len(golden)} questions (version {version_info['version']})")

    # Generate synthetic data (demo)
    synth = generate_synthetic(n=3)
    print(f"  Synthetic samples generated: {len(synth)}")

    # ---- Step 3: Build RAG pipeline ----
    print("\n[3/7] Building RAG pipeline...")
    retriever = build_retriever(passages)
    print(f"  Retriever type: {retriever['type']}")

    print("\n[4/7] Running RAG pipeline on golden set...")
    results = run_pipeline(golden, retriever)
    print(f"  Processed {len(results)} questions")

    # ---- Step 4: Run full evaluation ----
    print("\n[5/7] Running evaluation suite...")
    eval_results = full_evaluation(results)
    acc = eval_results["accuracy"]["accuracy"]
    print(f"  Accuracy: {acc:.2%}")
    print(f"  Avg latency: {eval_results['latency']['avg']:.4f}s")

    # ---- Step 5: Regression check ----
    print("\n[6/7] Running regression check (v1 vs v2)...")
    # Simulate v2: flip some predictions to create different accuracy
    results_v2 = copy.deepcopy(results)
    for i, r in enumerate(results_v2):
        if i % 5 == 0:
            r["predicted"] = "X"  # intentionally wrong
        r["latency"] = r["latency"] * 1.1  # slightly slower
    eval_v2 = full_evaluation(results_v2)

    regression = compare_versions(eval_results, eval_v2)
    gates = check_gates(eval_results)
    print(f"  Regression verdict: {regression['verdict']}")
    print(f"  Quality gates: {gates['verdict']}")

    # ---- Step 6: Render dashboard ----
    print("\n[7/7] Rendering dashboard...\n")
    dashboard = render_dashboard(eval_results, gate_results=gates, regression=regression)
    print(dashboard)

    # ---- Step 7: Save report ----
    report_path = os.path.join(base, "capstone_report.json")
    combined = {
        "dataset": {"stats": stats, "version": version_info},
        "evaluation_v1": eval_results,
        "evaluation_v2": eval_v2,
        "regression": regression,
        "quality_gates": gates,
    }
    save_report(combined, report_path)

    # ---- Langfuse observability ----
    print("\n[BONUS] Sending traces to Langfuse...")
    try:
        from langfuse import Langfuse
        sys.path.insert(0, os.path.join(base, ".."))
        from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

        langfuse = Langfuse(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_BASE_URL,
        )

        trace = langfuse.trace(
            name="capstone-full-pipeline",
            metadata={"dataset_version": version_info["version"],
                       "retriever": retriever["type"],
                       "num_questions": len(results)},
        )

        for r in results:
            gen = trace.generation(
                name=f"question-{r.get('question_id', 'unknown')}",
                model="ollama",
                input=r.get("question", "")[:200],
                output=r.get("predicted", ""),
                metadata={"gold": r.get("gold", ""), "latency": r.get("latency", 0)},
            )
            gen.score(name="correct", value=1.0 if r.get("predicted") == r.get("gold") else 0.0)

        trace.score(name="accuracy", value=acc)
        trace.score(name="avg_latency", value=eval_results["latency"]["avg"])
        trace.score(name="gate_result", value=1.0 if gates["verdict"] == "PASS" else 0.0)

        langfuse.flush()
        print("  Langfuse traces sent. View at https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")

    # ---- LangGraph pipeline demo ----
    print("\n[BONUS] LangGraph pipeline demo...")
    try:
        from langgraph.graph import StateGraph, START, END
        from typing import TypedDict, List

        class PipelineState(TypedDict):
            questions: List[dict]
            results: List[dict]
            accuracy: float

        def eval_node(state: PipelineState) -> PipelineState:
            correct = sum(1 for r in state["results"] if r.get("predicted") == r.get("gold"))
            return {**state, "accuracy": correct / len(state["results"]) if state["results"] else 0.0}

        def gate_node(state: PipelineState) -> PipelineState:
            return state

        g = StateGraph(PipelineState)
        g.add_node("evaluate", eval_node)
        g.add_node("gate", gate_node)
        g.add_edge(START, "evaluate")
        g.add_edge("evaluate", "gate")
        g.add_edge("gate", END)
        pipeline = g.compile()

        pipe_result = pipeline.invoke({
            "questions": [{"q": r.get("question", "")[:50]} for r in results[:5]],
            "results": results[:5],
            "accuracy": 0.0,
        })
        print(f"  LangGraph pipeline accuracy: {pipe_result['accuracy']:.2%}")
        print("  LangGraph state graph works.")
    except Exception as e:
        print(f"  LangGraph not available ({e}), skipping.")

    print("\nCapstone pipeline complete!")


if __name__ == "__main__":
    main()
