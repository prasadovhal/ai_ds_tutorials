import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os

print("=" * 70)
print("CHAPTER 12: Research Papers - Reproducing Key Ideas")
print("=" * 70)

# -- Load data --
import pandas as pd
import numpy as np

train_df = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\train.csv").head(3)
corpus_df = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\wiki_stem_corpus.csv", nrows=200)

questions = train_df["prompt"].tolist()
answer_texts = [row[row["answer"]] for _, row in train_df.iterrows()]
passages = corpus_df["text"].tolist()[:5]
print(f"Loaded {len(questions)} questions, {len(passages)} passages")

# Helper: call Ollama with fallback
USE_OLLAMA = True
def ask_ollama(prompt, model="llama3.2"):
    global USE_OLLAMA
    if not USE_OLLAMA:
        return None
    try:
        import ollama
        resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return resp["message"]["content"]
    except Exception as e:
        print(f"  Ollama failed: {e}")
        USE_OLLAMA = False
        return None

results_summary = {}

# ============================================================
# PAPER 1: MT-Bench style (Judging LLM-as-a-Judge, Zheng et al.)
# ============================================================
print("\n" + "=" * 70)
print("PAPER 1: MT-Bench - Multi-Turn Judge (Zheng et al. 2023)")
print("=" * 70)

# Ask multi-turn questions, then have LLM judge its own responses
mt_scores = []
mt_turns = [
    ("Explain what a black hole is.", "Now explain how Hawking radiation works in that context."),
    ("What is photosynthesis?", "How does it relate to climate change?"),
    ("Define entropy.", "Give a real-world example of entropy increasing."),
]

for i, (turn1, turn2) in enumerate(mt_turns):
    # Get responses for both turns
    resp1 = ask_ollama(f"Answer briefly: {turn1}")
    resp2 = ask_ollama(f"Given your previous answer about '{turn1}', now answer: {turn2}")
    if resp1 is None:
        resp1 = f"[Simulated answer to: {turn1[:40]}]"
        resp2 = f"[Simulated follow-up to: {turn2[:40]}]"

    # Have LLM judge the quality 1-10
    judge_prompt = (f"Rate this multi-turn conversation 1-10. Reply with ONLY a number.\n"
                    f"Q1: {turn1}\nA1: {resp1[:150]}\nQ2: {turn2}\nA2: {resp2[:150]}")
    score_text = ask_ollama(judge_prompt)
    try:
        score = float(''.join(c for c in (score_text or "7") if c.isdigit() or c == '.')[:3])
        score = min(max(score, 1), 10)
    except:
        score = 7.0
    mt_scores.append(score)
    print(f"  Turn pair {i+1}: score = {score}/10")

avg_mt = np.mean(mt_scores)
print(f"\n  Average MT-Bench score: {avg_mt:.1f}/10")
results_summary["MT-Bench avg"] = f"{avg_mt:.1f}/10"

# ============================================================
# PAPER 2: Position Bias (LLMs are Not Fair Evaluators, Wang et al.)
# ============================================================
print("\n" + "=" * 70)
print("PAPER 2: Position Bias Test (Wang et al. 2023)")
print("=" * 70)

# Test if LLM prefers the first answer regardless of content
answer_a = answer_texts[0][:150]
answer_b = answer_texts[1][:150] if len(answer_texts) > 1 else "This is an alternative answer."
q = questions[0][:200]

# Order 1: A first, B second
prompt_ab = (f"Which answer is better? Reply ONLY 'Answer 1' or 'Answer 2'.\n"
             f"Question: {q}\nAnswer 1: {answer_a}\nAnswer 2: {answer_b}")
choice_ab = ask_ollama(prompt_ab)

# Order 2: B first, A second (swapped)
prompt_ba = (f"Which answer is better? Reply ONLY 'Answer 1' or 'Answer 2'.\n"
             f"Question: {q}\nAnswer 1: {answer_b}\nAnswer 2: {answer_a}")
choice_ba = ask_ollama(prompt_ba)

if choice_ab is None:
    choice_ab, choice_ba = "Answer 1", "Answer 1"
    print("  (Using simulated responses)")

print(f"  Order A,B -> chose: {(choice_ab or '?')[:20]}")
print(f"  Order B,A -> chose: {(choice_ba or '?')[:20]}")

# If it picked "Answer 1" both times, that's position bias
picked_first_ab = "1" in (choice_ab or "")
picked_first_ba = "1" in (choice_ba or "")
bias_detected = picked_first_ab and picked_first_ba
print(f"\n  Position bias detected: {'YES' if bias_detected else 'NO'}")
print(f"  (Picked first position both times: {bias_detected})")
results_summary["Position Bias"] = "Detected" if bias_detected else "Not detected"

# ============================================================
# PAPER 3: G-Eval CoT Scoring (Liu et al. 2023)
# ============================================================
print("\n" + "=" * 70)
print("PAPER 3: G-Eval - Chain-of-Thought Scoring (Liu et al. 2023)")
print("=" * 70)

# Compare direct scoring vs CoT scoring
eval_q = questions[0][:200]
eval_a = answer_texts[0][:200]

# Direct scoring (no CoT)
direct_prompt = f"Rate this answer 1-5. Reply with ONLY a number.\nQuestion: {eval_q}\nAnswer: {eval_a}"
direct_text = ask_ollama(direct_prompt)
try:
    direct_score = float(''.join(c for c in (direct_text or "3") if c.isdigit() or c == '.')[:3])
    direct_score = min(max(direct_score, 1), 5)
except:
    direct_score = 3.0

# CoT scoring (G-Eval style)
cot_prompt = (f"Think step by step about the quality of this answer.\n"
              f"Consider: relevance, accuracy, completeness, clarity.\n"
              f"Question: {eval_q}\nAnswer: {eval_a}\n\n"
              f"Step-by-step reasoning, then final score 1-5 on the last line as 'Score: N'")
cot_text = ask_ollama(cot_prompt)
try:
    import re
    nums = re.findall(r'[Ss]core[:\s]*(\d)', cot_text or "Score: 4")
    cot_score = float(nums[-1]) if nums else 4.0
    cot_score = min(max(cot_score, 1), 5)
except:
    cot_score = 4.0

print(f"  Direct score (no CoT):    {direct_score}/5")
print(f"  G-Eval score (with CoT):  {cot_score}/5")
print(f"  Difference:               {abs(cot_score - direct_score):.1f}")
results_summary["G-Eval Direct"] = f"{direct_score}/5"
results_summary["G-Eval CoT"] = f"{cot_score}/5"

# ============================================================
# PAPER 4: RAGAS-style Faithfulness (Es et al. 2023)
# ============================================================
print("\n" + "=" * 70)
print("PAPER 4: RAGAS Faithfulness Score (Es et al. 2023)")
print("=" * 70)

# Extract claims from answer, check each against context
context = passages[0][:500]
answer_to_check = answer_texts[0][:300]

claim_prompt = (f"Extract individual factual claims from this answer as a numbered list. "
                f"Keep each claim to one sentence.\nAnswer: {answer_to_check}")
claims_text = ask_ollama(claim_prompt)
if claims_text is None:
    claims_text = "1. MOND reduces the discrepancy.\n2. The factor goes from 10 to 2.\n3. It affects galaxy clusters."

# Parse claims from numbered list
import re
claims = re.findall(r'\d+\.\s*(.+)', claims_text)
claims = claims[:5]  # limit to 5 claims
print(f"  Extracted {len(claims)} claims from answer")

# Check each claim against context
supported = 0
for i, claim in enumerate(claims):
    check_prompt = (f"Is this claim supported by the context? Reply ONLY 'Yes' or 'No'.\n"
                    f"Claim: {claim}\nContext: {context}")
    verdict = ask_ollama(check_prompt)
    is_supported = "yes" in (verdict or "no").lower()
    if is_supported:
        supported += 1
    print(f"  Claim {i+1}: {'SUPPORTED' if is_supported else 'NOT SUPPORTED'} - {claim[:60]}...")

faithfulness_score = supported / len(claims) if claims else 0.0
print(f"\n  Faithfulness = {supported}/{len(claims)} = {faithfulness_score:.2f}")
results_summary["RAGAS Faithfulness"] = f"{faithfulness_score:.2f}"

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY: Paper Reproduction Results")
print("=" * 70)
print(f"  {'Paper/Metric':<25s} {'Result':<20s}")
print(f"  {'-'*25} {'-'*20}")
for key, val in results_summary.items():
    print(f"  {key:<25s} {val:<20s}")

print(f"\n  Ollama used: {'Yes' if USE_OLLAMA else 'No (simulated responses)'}")

# ── Langfuse tracing ──
print("\n" + "=" * 70)
print("LANGFUSE TRACING")
print("=" * 70)
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
    trace = langfuse.trace(name="ch12-research-papers", metadata={"ollama": USE_OLLAMA})

    for key, val in results_summary.items():
        span = trace.span(name=key, output={"result": val})
        span.end()

    trace.score(name="mt_bench_avg", value=avg_mt / 10.0)
    trace.score(name="faithfulness", value=faithfulness_score)
    trace.score(name="position_bias_free", value=0.0 if bias_detected else 1.0)

    langfuse.flush()
    print("  Paper reproduction results traced to Langfuse. View at: https://cloud.langfuse.com")
except Exception as e:
    print(f"  Langfuse not available ({e}), skipping.")

print("\n" + "=" * 70)
print("Chapter 12 hands-on complete.")
print("=" * 70)
