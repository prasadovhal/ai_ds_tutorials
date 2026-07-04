"""
Chapter 9: Production Evaluation Systems - Hands-On
Uses: pandas, sklearn, mlflow, numpy
"""
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score
from scipy.stats import chi2_contingency

np.random.seed(42)

DATA_PATH = r"D:\Study\Git_repo\evaluations\data\train.csv"
CHOICES = ["A", "B", "C", "D", "E"]


def main():
    print("=" * 60)
    print("CHAPTER 9: PRODUCTION EVALUATION SYSTEMS")
    print("=" * 60)

    # 1. Load data, split into golden_set (first 50) and eval_set (next 50)
    df = pd.read_csv(DATA_PATH)
    golden_set = df.iloc[:50].copy()
    eval_set = df.iloc[50:100].copy()
    print(f"\nGolden set: {len(golden_set)} rows | Eval set: {len(eval_set)} rows")

    golden_truth = golden_set["answer"].tolist()
    eval_truth = eval_set["answer"].tolist()

    # 2. Simulate 3 model versions with different accuracies
    def make_preds(truth, correct_rate, seed):
        rng = np.random.RandomState(seed)
        preds = []
        for ans in truth:
            if rng.random() < correct_rate:
                preds.append(ans)
            else:
                preds.append(rng.choice(CHOICES))
        return preds

    models = {
        "v1.0": make_preds(golden_truth, 0.50, seed=10),
        "v2.0": make_preds(golden_truth, 0.45, seed=20),
        "v3.0": make_preds(golden_truth, 0.65, seed=30),
    }
    print(f"Simulated {len(models)} model versions on golden set")

    # 3. MLflow tracking - log metrics for each model version
    metrics_log = []
    try:
        import mlflow
        mlflow.set_experiment("llm_eval_course")
        print("\n--- MLflow Tracking ---")

        for version, preds in models.items():
            acc = accuracy_score(golden_truth, preds)
            f1 = f1_score(golden_truth, preds, labels=CHOICES, average="macro", zero_division=0)
            prec = precision_score(golden_truth, preds, labels=CHOICES, average="macro", zero_division=0)

            with mlflow.start_run(run_name=f"model_{version}"):
                mlflow.log_param("model_version", version)
                mlflow.log_metric("accuracy", round(acc, 4))
                mlflow.log_metric("f1_macro", round(f1, 4))
                mlflow.log_metric("precision_macro", round(prec, 4))

            metrics_log.append({"version": version, "accuracy": acc, "f1": f1, "precision": prec})
            print(f"  {version} logged -> acc={acc:.4f}  f1={f1:.4f}  prec={prec:.4f}")

        # Compare runs
        experiment = mlflow.get_experiment_by_name("llm_eval_course")
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        print(f"\n  MLflow runs recorded: {len(runs)}")
        print(f"  View UI: mlflow ui  (default http://127.0.0.1:5000)")

    except Exception as e:
        print(f"\n[MLflow unavailable: {e}] -- falling back to pandas tracking")
        for version, preds in models.items():
            acc = accuracy_score(golden_truth, preds)
            f1 = f1_score(golden_truth, preds, labels=CHOICES, average="macro", zero_division=0)
            prec = precision_score(golden_truth, preds, labels=CHOICES, average="macro", zero_division=0)
            metrics_log.append({"version": version, "accuracy": acc, "f1": f1, "precision": prec})
            print(f"  {version} -> acc={acc:.4f}  f1={f1:.4f}  prec={prec:.4f}")

    metrics_df = pd.DataFrame(metrics_log)

    # 4. Regression testing: compare v1 vs v2, flag if accuracy drops > 2%
    print("\n--- Regression Testing ---")
    v1_acc = metrics_df.loc[metrics_df["version"] == "v1.0", "accuracy"].values[0]
    v2_acc = metrics_df.loc[metrics_df["version"] == "v2.0", "accuracy"].values[0]
    drop = v1_acc - v2_acc
    status = "REGRESSION DETECTED" if drop > 0.02 else "OK"
    print(f"  v1.0 accuracy: {v1_acc:.4f}")
    print(f"  v2.0 accuracy: {v2_acc:.4f}")
    print(f"  Drop: {drop:+.4f}  -> {status}")

    # 5. Drift detection: compare answer distributions across two data windows
    print("\n--- Drift Detection ---")
    window1 = df.iloc[:50]["answer"].value_counts().sort_index()
    window2 = df.iloc[50:100]["answer"].value_counts().sort_index()
    all_labels = sorted(set(window1.index) | set(window2.index))
    w1 = [window1.get(c, 0) for c in all_labels]
    w2 = [window2.get(c, 0) for c in all_labels]
    contingency = np.array([w1, w2])
    chi2, p_value, _, _ = chi2_contingency(contingency)
    drift_detected = p_value < 0.05
    print(f"  Window 1 distribution: {dict(zip(all_labels, w1))}")
    print(f"  Window 2 distribution: {dict(zip(all_labels, w2))}")
    print(f"  Chi-squared: {chi2:.4f}  p-value: {p_value:.4f}")
    print(f"  Drift detected (p<0.05): {drift_detected}")

    # 6. CI/CD gate simulation: accuracy must exceed threshold
    print("\n--- CI/CD Gate Simulation ---")
    threshold = 0.55
    for _, row in metrics_df.iterrows():
        gate = "PASS" if row["accuracy"] >= threshold else "FAIL"
        print(f"  {row['version']}: accuracy={row['accuracy']:.4f}  threshold={threshold}  -> {gate}")

    # 7. Summary comparison
    print(f"\n{'=' * 60}")
    print("PRODUCTION EVALUATION SUMMARY")
    print(f"{'=' * 60}")
    print(metrics_df.to_string(index=False, float_format="%.4f"))
    best = metrics_df.loc[metrics_df["accuracy"].idxmax()]
    print(f"\nBest model: {best['version']} with accuracy {best['accuracy']:.4f}")

    # 8. Langfuse tracing for production monitoring
    print(f"\n{'=' * 60}")
    print("LANGFUSE PRODUCTION TRACING")
    print(f"{'=' * 60}")
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

        for version, preds in models.items():
            trace = langfuse.trace(name=f"production-eval-{version}", metadata={"model_version": version})

            row_metrics = metrics_df[metrics_df["version"] == version].iloc[0]
            trace.score(name="accuracy", value=float(row_metrics["accuracy"]))
            trace.score(name="f1_macro", value=float(row_metrics["f1"]))

            gate_result = "PASS" if row_metrics["accuracy"] >= threshold else "FAIL"
            span = trace.span(name="cicd_gate", input={"threshold": threshold},
                              output={"result": gate_result, "accuracy": float(row_metrics["accuracy"])})
            span.end()

            print(f"  {version}: traced (accuracy={row_metrics['accuracy']:.4f}, gate={gate_result})")

        drift_trace = langfuse.trace(name="drift-detection")
        drift_trace.span(name="chi2_test",
                         input={"window1": dict(zip(all_labels, w1)), "window2": dict(zip(all_labels, w2))},
                         output={"chi2": float(chi2), "p_value": float(p_value), "drift": drift_detected})
        langfuse.flush()
        print("  Langfuse traces sent. View at: https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")
        print("  pip install langfuse  # then set keys in constant.py")

    print("\n--- Key Takeaways ---")
    print("- Track every model version with metrics (MLflow or equivalent)")
    print("- Regression tests catch accuracy drops before deployment")
    print("- Drift detection flags distribution shifts in incoming data")
    print("- CI/CD gates enforce minimum quality thresholds")
    print("- Langfuse/LangSmith provide production-grade observability")
    print("\nDone!")


if __name__ == "__main__":
    main()
