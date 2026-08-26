"""
Chapter 7: Evaluation Dataset Engineering - Hands-On
Uses: pandas, sklearn, numpy
"""
import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

np.random.seed(42)
DATA_DIR = r"D:\Study\Git_repo\evaluations\data"
TRAIN_PATH, TEST_PATH = f"{DATA_DIR}\\train.csv", f"{DATA_DIR}\\test.csv"


def main():
    print("=" * 60)
    print("CHAPTER 7: EVALUATION DATASET ENGINEERING")
    print("=" * 60)

    # Load the dataset
    df = pd.read_csv(TRAIN_PATH)
    print(f"\nLoaded train.csv: {df.shape[0]} rows, {df.shape[1]} columns")

    # --- 2. Dataset quality checks ---
    print("\n--- Quality Checks ---")
    missing = df.isnull().sum()
    print(f"Missing values:\n{missing}")
    dup_count = df.duplicated(subset="prompt").sum()
    print(f"\nDuplicate prompts: {dup_count}")

    # Answer distribution with bar chart description
    ans_dist = df["answer"].value_counts().sort_index()
    print(f"\nAnswer distribution:\n{ans_dist}")
    print(f"[Bar Chart] Tallest: {ans_dist.idxmax()} ({ans_dist.max()}), Shortest: {ans_dist.idxmin()} ({ans_dist.min()})")

    # --- 3. Coverage analysis ---
    print("\n--- Coverage Analysis ---")
    lengths = df["prompt"].str.len().values
    pctiles = np.percentile(lengths, [10, 25, 50, 75, 90])
    print("Prompt length percentiles (chars):")
    for p, v in zip([10, 25, 50, 75, 90], pctiles):
        print(f"  P{p}: {v:.0f}")

    # Chi-squared class balance test (manual)
    observed = ans_dist.values.astype(float)
    expected = np.full_like(observed, observed.mean())
    chi2 = np.sum((observed - expected) ** 2 / expected)
    print(f"\nChi-squared balance: chi2={chi2:.3f}, dof={len(observed)-1} (lower=more balanced)")

    # --- 4. Contamination check ---
    print("\n--- Contamination Check ---")
    df_test = pd.read_csv(TEST_PATH)
    overlap = set(df["prompt"]) & set(df_test["prompt"])
    print(f"Train: {len(df)}, Test: {len(df_test)}, Overlapping prompts: {len(overlap)}")

    # --- 5. Cohen's Kappa (2 simulated annotators) ---
    print("\n--- Cohen's Kappa ---")
    choices = ["A", "B", "C", "D", "E"]
    true = df["answer"].tolist()
    n = len(true)
    ann1 = [t if np.random.random() < 0.8 else np.random.choice(choices) for t in true]
    ann2 = [t if np.random.random() < 0.7 else np.random.choice(choices) for t in true]
    kappa = cohen_kappa_score(ann1, ann2)
    print(f"Ann1 acc: {sum(a==t for a,t in zip(ann1,true))/n:.2f}, Ann2 acc: {sum(a==t for a,t in zip(ann2,true))/n:.2f}")
    print(f"Cohen's Kappa: {kappa:.4f}  (0.61-0.80=substantial, 0.81-1.0=perfect)")

    # --- 6. Fleiss' Kappa (3 annotators, 20 items, manual formula) ---
    print("\n--- Fleiss' Kappa ---")
    n_items, n_raters, n_cats = 20, 3, 5
    mat = np.zeros((n_items, n_cats), dtype=int)
    for i in range(n_items):
        for _ in range(n_raters):
            gt = choices.index(true[i])
            mat[i, gt if np.random.random() < 0.75 else np.random.randint(0, n_cats)] += 1

    p_j = mat.sum(axis=0) / (n_items * n_raters)
    Pi = (np.sum(mat ** 2, axis=1) - n_raters) / (n_raters * (n_raters - 1))
    P_bar, Pe_bar = Pi.mean(), np.sum(p_j ** 2)
    fleiss = (P_bar - Pe_bar) / (1 - Pe_bar) if Pe_bar < 1 else 1.0
    print(f"Rating matrix (first 5):\n{pd.DataFrame(mat[:5], columns=choices)}")
    print(f"P_bar={P_bar:.4f}, Pe_bar={Pe_bar:.4f}, Fleiss' Kappa={fleiss:.4f}")

    # --- 7. Label noise detection (keyword overlap heuristic) ---
    print("\n--- Label Noise Detection ---")
    stops = {"the","a","an","of","in","is","to","that","and","for","it","on","with","as","by"}
    flagged = []
    for _, row in df.head(50).iterrows():
        prompt_w = set(row["prompt"].lower().split())
        answer_w = set(str(row[row["answer"]]).lower().split())
        overlap_w = (prompt_w & answer_w) - stops
        if len(overlap_w) < 2:
            flagged.append({"id": row["id"], "answer": row["answer"], "overlap": len(overlap_w)})
    print(f"Checked 50 questions, flagged: {len(flagged)}")
    if flagged:
        print(pd.DataFrame(flagged[:5]).to_string(index=False))

    # --- 8. Summary report ---
    print(f"\n{'='*60}\nSUMMARY REPORT\n{'='*60}")
    summary = pd.DataFrame([
        {"Metric": "Total samples", "Value": str(n)},
        {"Metric": "Missing values", "Value": str(missing.sum())},
        {"Metric": "Duplicate prompts", "Value": str(dup_count)},
        {"Metric": "Prompt length median", "Value": f"{pctiles[2]:.0f} chars"},
        {"Metric": "Chi-squared (balance)", "Value": f"{chi2:.3f}"},
        {"Metric": "Train-test overlap", "Value": str(len(overlap))},
        {"Metric": "Cohen's Kappa", "Value": f"{kappa:.4f}"},
        {"Metric": "Fleiss' Kappa", "Value": f"{fleiss:.4f}"},
        {"Metric": "Label noise flagged", "Value": f"{len(flagged)}/50"},
    ])
    print(f"\n{summary.to_string(index=False)}")

    # --- 9. Langfuse tracing ---
    print(f"\n{'='*60}")
    print("LANGFUSE TRACING")
    print(f"{'='*60}")
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
        trace = langfuse.trace(name="ch7-dataset-engineering", metadata={
            "total_samples": n, "overlap": len(overlap),
        })
        trace.score(name="cohens_kappa", value=kappa)
        trace.score(name="fleiss_kappa", value=fleiss)
        trace.score(name="chi_squared", value=float(chi2))
        trace.score(name="label_noise_ratio", value=len(flagged) / 50.0)

        langfuse.flush()
        print("  Dataset quality metrics traced to Langfuse. View at: https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")

    print("\nDone!")


if __name__ == "__main__":
    main()
