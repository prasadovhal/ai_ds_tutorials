import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 6 Hands-On: Golden Dataset Engineering
Uses: pandas, sklearn, ollama
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter

# ── 1. Load dataset ──────────────────────────────────────────────────
train = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\train.csv")
print("=== 1. DATASET LOADED ===")
print(f"Shape: {train.shape}")
print(train.head(3).to_string(max_colwidth=60))

# ── 2. Dataset analysis ─────────────────────────────────────────────
print("\n=== 2. DATASET ANALYSIS ===")

# Answer distribution
print("\n-- Answer Distribution --")
ans_dist = train["answer"].value_counts().sort_index()
print(ans_dist.to_string())

# Prompt length distribution
train["prompt_len"] = train["prompt"].str.len()
print("\n-- Prompt Length Stats --")
print(train["prompt_len"].describe().round(1).to_string())

# Topic detection via simple keyword matching
topic_keywords = {
    "physics": ["force", "energy", "momentum", "gravity", "quantum", "wave", "electric", "magnetic", "newton"],
    "biology": ["cell", "dna", "gene", "organism", "evolution", "protein", "species", "enzyme", "mitosis"],
    "chemistry": ["atom", "molecule", "reaction", "bond", "acid", "element", "compound", "ion", "electron"],
    "math": ["equation", "theorem", "function", "integral", "matrix", "probability", "algebra", "geometry"],
    "astronomy": ["planet", "star", "galaxy", "orbit", "universe", "solar", "telescope", "cosmic"],
}

def detect_topic(prompt):
    prompt_lower = prompt.lower()
    scores = {t: sum(1 for kw in kws if kw in prompt_lower) for t, kws in topic_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"

train["topic"] = train["prompt"].apply(detect_topic)
print("\n-- Topic Distribution --")
print(train["topic"].value_counts().to_string())

# ── 3. Stratified sampling ──────────────────────────────────────────
print("\n=== 3. STRATIFIED SAMPLING ===")
from sklearn.model_selection import train_test_split

train_split, test_split = train_test_split(train, test_size=0.2, stratify=train["answer"], random_state=42)
print(f"Train: {len(train_split)} | Test: {len(test_split)}")
print("\n-- Answer distribution in splits --")
comp = pd.DataFrame({
    "full": train["answer"].value_counts(normalize=True).sort_index().round(4),
    "train_split": train_split["answer"].value_counts(normalize=True).sort_index().round(4),
    "test_split": test_split["answer"].value_counts(normalize=True).sort_index().round(4),
})
print(comp.to_string())

# ── 4. Deduplication via Jaccard similarity ──────────────────────────
print("\n=== 4. NEAR-DUPLICATE DETECTION ===")

def jaccard(a, b):
    sa, sb = set(a.lower().split()), set(b.lower().split())
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union > 0 else 0.0

# Check first 200 pairs to keep it fast
sample_prompts = train["prompt"].head(200).tolist()
duplicates = []
for i in range(len(sample_prompts)):
    for j in range(i + 1, min(i + 20, len(sample_prompts))):
        sim = jaccard(sample_prompts[i], sample_prompts[j])
        if sim > 0.6:
            duplicates.append((i, j, round(sim, 4)))

print(f"Checked: {len(sample_prompts)} prompts (sliding window of 20)")
print(f"Near-duplicates found (Jaccard > 0.6): {len(duplicates)}")
for i, j, sim in duplicates[:5]:
    print(f"  [{i}]-[{j}] sim={sim}: {sample_prompts[i][:60]}...")

# ── 5. Balance analysis with chi-squared ─────────────────────────────
print("\n=== 5. BALANCE ANALYSIS ===")
try:
    from scipy.stats import chisquare
    observed = train["answer"].value_counts().sort_index().values
    expected_freq = np.full_like(observed, observed.mean(), dtype=float)
    chi2, p_value = chisquare(observed, f_exp=expected_freq)
except ImportError:
    # Manual chi-squared if scipy unavailable
    observed = train["answer"].value_counts().sort_index().values
    expected_freq = np.full_like(observed, observed.mean(), dtype=float)
    chi2 = float(np.sum((observed - expected_freq) ** 2 / expected_freq))
    k = len(observed) - 1
    p_value = 1.0 if chi2 < k else 0.01  # rough approximation
print(f"Observed counts: {dict(zip(sorted(train['answer'].unique()), observed))}")
print(f"Chi-squared: {chi2:.4f} | p-value: {p_value:.4f}")
print(f"Balanced: {'Yes' if p_value > 0.05 else 'No'} (p > 0.05 means balanced)")

# ── 6. Inter-annotator agreement (simulated) ────────────────────────
print("\n=== 6. INTER-ANNOTATOR AGREEMENT ===")
from sklearn.metrics import cohen_kappa_score

rng = np.random.RandomState(42)
ground_truth = train["answer"].values
choices = sorted(train["answer"].unique())

# Simulate 3 annotators with different accuracy levels
def simulate_annotator(gt, accuracy, rng):
    labels = []
    for g in gt:
        if rng.random() < accuracy:
            labels.append(g)
        else:
            labels.append(rng.choice([c for c in choices if c != g]))
    return labels

ann1 = simulate_annotator(ground_truth, 0.90, rng)
ann2 = simulate_annotator(ground_truth, 0.85, rng)
ann3 = simulate_annotator(ground_truth, 0.80, rng)

kappa_12 = cohen_kappa_score(ann1, ann2)
kappa_13 = cohen_kappa_score(ann1, ann3)
kappa_23 = cohen_kappa_score(ann2, ann3)
avg_kappa = (kappa_12 + kappa_13 + kappa_23) / 3

print(f"Annotator accuracies: 90%, 85%, 80%")
print(f"Cohen's Kappa (1 vs 2): {kappa_12:.4f}")
print(f"Cohen's Kappa (1 vs 3): {kappa_13:.4f}")
print(f"Cohen's Kappa (2 vs 3): {kappa_23:.4f}")
print(f"Average Kappa: {avg_kappa:.4f}")
interp = "substantial" if avg_kappa > 0.6 else "moderate" if avg_kappa > 0.4 else "fair"
print(f"Interpretation: {interp} agreement")

# ── 7. Synthetic question generation with ollama ─────────────────────
print("\n=== 7. SYNTHETIC QUESTION GENERATION ===")
try:
    import ollama
    model_name = "llama3.2"
    try:
        available = [m.model for m in ollama.list().models]
        if not any(model_name in m for m in available):
            model_name = available[0] if available else "llama3.2"
    except Exception:
        pass

    # Show a sample question as example for the LLM
    sample_q = train.iloc[0]
    example = (
        f"prompt: {sample_q['prompt'][:200]}\n"
        f"A: {sample_q['A'][:80]}\nB: {sample_q['B'][:80]}\n"
        f"C: {sample_q['C'][:80]}\nD: {sample_q['D'][:80]}\n"
        f"answer: {sample_q['answer']}"
    )
    prompt = (
        f"Generate 3 science multiple-choice questions similar to this example:\n\n"
        f"{example}\n\n"
        f"Format each as:\nQ: <question>\nA: <option>\nB: <option>\nC: <option>\nD: <option>\nAnswer: <letter>"
    )
    resp = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    print(resp["message"]["content"][:800])
except Exception as e:
    print(f"ollama unavailable ({e}), showing template instead")
    print("Template: Q: What is [concept]? A: ... B: ... C: ... D: ... Answer: B")

# ── 8. Version tracking ─────────────────────────────────────────────
print("\n=== 8. DATASET VERSION TRACKING ===")
versions = [
    {"version": "1.0.0", "date": "2026-01-15", "rows": 200, "action": "Initial dataset", "answer_balance": "A:42 B:38 C:40 D:41 E:39"},
    {"version": "1.1.0", "date": "2026-03-10", "rows": 200, "action": "Removed 3 duplicates, added 3 new", "answer_balance": "A:40 B:40 C:40 D:40 E:40"},
    {"version": "2.0.0", "date": "2026-06-01", "rows": len(train), "action": "Full dataset release", "answer_balance": str(dict(train["answer"].value_counts().sort_index()))},
]
versions_df = pd.DataFrame(versions)
print(versions_df.to_string(index=False))

# ── 9. Summary of all results ───────────────────────────────────────
print("\n=== 9. RESULTS SUMMARY ===")
summary = pd.DataFrame({
    "Metric": ["Total rows", "Unique answers", "Most common topic", "Stratified test size",
               "Near-duplicates found", "Chi-squared (balance)", "Avg Cohen's Kappa"],
    "Value": [len(train), train["answer"].nunique(), train["topic"].mode()[0], len(test_split),
              len(duplicates), f"{chi2:.2f} (p={p_value:.4f})", f"{avg_kappa:.4f} ({interp})"],
})
print(summary.to_string(index=False))

# ── 10. Langfuse tracing ──────────────────────────────────────────────
print("\n=== 10. LANGFUSE TRACING ===")
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
    trace = langfuse.trace(name="ch6-golden-dataset-eng", metadata={
        "total_rows": len(train), "topics": dict(train["topic"].value_counts()),
    })
    trace.score(name="avg_kappa", value=avg_kappa)
    trace.score(name="chi_squared", value=float(chi2))
    trace.score(name="near_duplicates", value=float(len(duplicates)))

    span = trace.span(name="stratified-split",
                      output={"train_size": len(train_split), "test_size": len(test_split)})
    span.end()

    langfuse.flush()
    print("  Dataset quality metrics traced to Langfuse. View at: https://cloud.langfuse.com")
except Exception as e:
    print(f"  Langfuse not available ({e}), skipping.")

print("\nChapter 6 hands-on complete.")
