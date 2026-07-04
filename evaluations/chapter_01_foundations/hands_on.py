"""
Chapter 1: Foundations of LLM Evaluation - Hands-On
Uses: pandas, scikit-learn
"""
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import random
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

random.seed(42)
np.random.seed(42)

DATA_PATH = r"D:\Study\Git_repo\evaluations\data\train.csv"


def main():
    # --- 1. Load the dataset ---
    print("=" * 60)
    print("CHAPTER 1: FOUNDATIONS OF LLM EVALUATION")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # --- 2. Dataset statistics ---
    print("\n--- Dataset Statistics ---")
    print(df.describe())

    print("\n--- Answer Distribution ---")
    answer_counts = df["answer"].value_counts().sort_index()
    print(answer_counts)
    print(f"\nTotal questions: {len(df)}")

    # --- 3. Simulate predictions from 3 models ---
    choices = ["A", "B", "C", "D", "E"]
    true_answers = df["answer"].tolist()

    # Model 1: pure random guessing
    pred_random = [random.choice(choices) for _ in range(len(df))]

    # Model 2: weighted random (slightly favors common answers)
    weights = [answer_counts.get(c, 0) for c in choices]
    total_w = sum(weights)
    weights = [w / total_w for w in weights]
    pred_weighted = random.choices(choices, weights=weights, k=len(df))

    # Model 3: "smarter" model - correct 40% of the time, random otherwise
    pred_smart = []
    for ans in true_answers:
        if random.random() < 0.4:
            pred_smart.append(ans)
        else:
            pred_smart.append(random.choice(choices))

    # --- 4. Evaluate with sklearn metrics ---
    models = {
        "Random Guess": pred_random,
        "Weighted Random": pred_weighted,
        "Smart Model (40%)": pred_smart,
    }

    for name, preds in models.items():
        print(f"\n{'=' * 60}")
        print(f"MODEL: {name}")
        print(f"{'=' * 60}")

        acc = accuracy_score(true_answers, preds)
        print(f"Accuracy: {acc:.4f}")

        print("\nClassification Report:")
        print(classification_report(true_answers, preds, labels=choices, zero_division=0))

        print("Confusion Matrix:")
        cm = confusion_matrix(true_answers, preds, labels=choices)
        print(pd.DataFrame(cm, index=choices, columns=choices))

    # --- 5. Save confusion matrix plot for the smart model ---
    cm_smart = confusion_matrix(true_answers, pred_smart, labels=choices)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm_smart, display_labels=choices)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, cmap="Blues")
    ax.set_title("Confusion Matrix - Smart Model (40% correct)")
    output_path = r"D:\Study\Git_repo\evaluations\chapter_01_foundations\confusion_matrix.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    print(f"\nConfusion matrix plot saved to: {output_path}")

    # --- 6. Compare all 3 models side-by-side ---
    print(f"\n{'=' * 60}")
    print("MODEL COMPARISON")
    print(f"{'=' * 60}")

    results = []
    for name, preds in models.items():
        acc = accuracy_score(true_answers, preds)
        report = classification_report(true_answers, preds, labels=choices, output_dict=True, zero_division=0)
        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Macro Precision": round(report["macro avg"]["precision"], 4),
            "Macro Recall": round(report["macro avg"]["recall"], 4),
            "Macro F1": round(report["macro avg"]["f1-score"], 4),
        })

    # --- 7. Print results table ---
    comparison_df = pd.DataFrame(results)
    print("\n", comparison_df.to_string(index=False))

    print("\n--- Key Takeaways ---")
    print("- Random guessing gives ~20% accuracy (1/5 choices)")
    print("- Weighted random barely improves over uniform random")
    print("- Even a 40%-correct model significantly outperforms random")
    print("- F1 score balances precision and recall for each class")

    # --- 8. Langfuse tracing ---
    print(f"\n{'=' * 60}")
    print("LANGFUSE TRACING")
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
        trace = langfuse.trace(name="ch1-foundations-eval", metadata={"num_models": len(models)})

        for res in results:
            span = trace.span(name=f"model-{res['Model']}", output=res)
            span.score(name="accuracy", value=res["Accuracy"])
            span.score(name="macro_f1", value=res["Macro F1"])
            span.end()

        langfuse.flush()
        print("  Model comparison traced to Langfuse. View at: https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")

    print("\nDone!")


if __name__ == "__main__":
    main()
