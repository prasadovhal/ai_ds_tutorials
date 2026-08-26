import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 4 Hands-On: LLM-as-a-Judge with Real Ollama + Mistral
==============================================================
Loads questions from train.csv, generates good/bad answers,
then demonstrates pointwise, pairwise, rubric-based judging,
and position bias testing -- all using real Ollama calls.
"""

import random
import pandas as pd

# -- Check Ollama availability --
OLLAMA_AVAILABLE = False
try:
    import ollama
    ollama.chat(model="mistral", messages=[{"role": "user", "content": "Say OK"}],
                options={"num_predict": 5})
    OLLAMA_AVAILABLE = True
    print("Ollama + Mistral connected successfully.\n")
except Exception as e:
    print(f"Ollama not available ({e}). Using simulated responses.")
    print("To use real LLM: pip install ollama && ollama pull mistral\n")


def ask_mistral(prompt, max_tokens=300):
    if OLLAMA_AVAILABLE:
        resp = ollama.chat(model="mistral",
                           messages=[{"role": "user", "content": prompt}],
                           options={"num_predict": max_tokens})
        return resp["message"]["content"].strip()
    return _simulate_response(prompt)


def _simulate_response(prompt):
    if "Pick the correct letter" in prompt:
        return f"The answer is {random.choice('ABCDE')}. Based on the scientific principles involved."
    if "rate" in prompt.lower() and "1-5" in prompt:
        s = random.randint(1, 5)
        return f"Score: {s}\nReason: The answer demonstrates {'strong' if s > 3 else 'limited'} understanding."
    if "which" in prompt.lower() and "better" in prompt.lower():
        pick = random.choice(["A", "B"])
        return f"Winner: {pick}\nReason: Answer {pick} provides a more complete explanation."
    if "accuracy" in prompt.lower() and "completeness" in prompt.lower():
        return f"Accuracy: {random.randint(1,5)}\nCompleteness: {random.randint(1,5)}\nClarity: {random.randint(1,5)}"
    return f"Score: {random.randint(2,4)}\nReason: Adequate response."


def main():
    print("=" * 70)
    print("  CHAPTER 4 HANDS-ON: LLM-as-a-Judge Techniques")
    print("=" * 70)

    # 1. Load 3 questions from train.csv
    df = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\train.csv", nrows=3)
    print(f"\nLoaded {len(df)} questions from train.csv\n")

    # 2. Generate two answers per question: good (Mistral) and bad (deliberately short/wrong)
    print("-" * 70)
    print("STEP 1: Generate good and bad answers")
    print("-" * 70)

    qa_pairs = []
    for idx, row in df.iterrows():
        question = row["prompt"]
        choices = "\n".join(f"  {L}) {row[L][:80]}..." for L in "ABCDE")
        full_prompt = f"{question}\n\nChoices:\n{choices}\nPick the correct letter and explain why."

        # Good answer: let Mistral answer properly
        good_answer = ask_mistral(full_prompt)

        # Bad answer: deliberately short and wrong
        wrong_letters = [L for L in "ABCDE" if L != row["answer"]]
        bad_answer = f"The answer is {wrong_letters[0]}. I think so."

        qa_pairs.append({
            "id": row["id"],
            "question": question,
            "correct": row["answer"],
            "good_answer": good_answer,
            "bad_answer": bad_answer,
        })
        print(f"\n  Q{idx+1} (id={row['id']}): {question[:80]}...")
        print(f"    Good answer: {good_answer[:100]}...")
        print(f"    Bad  answer: {bad_answer}")

    # 3. Pointwise judging: rate each answer 1-5
    print("\n" + "-" * 70)
    print("STEP 2: Pointwise Judging (rate each answer 1-5)")
    print("-" * 70)

    pointwise_results = []
    for qa in qa_pairs:
        for label, answer in [("Good", qa["good_answer"]), ("Bad", qa["bad_answer"])]:
            prompt = (
                f"You are an expert evaluator. Rate this answer on a scale of 1-5.\n\n"
                f"Question: {qa['question'][:200]}\n\n"
                f"Answer: {answer[:300]}\n\n"
                f"Reply in this exact format:\nScore: X\nReason: your reason here"
            )
            verdict = ask_mistral(prompt, max_tokens=100)
            pointwise_results.append({
                "question_id": qa["id"],
                "type": label,
                "verdict": verdict[:120],
            })
            print(f"  Q{qa['id']} ({label:4s}): {verdict[:100]}")

    # 4. Pairwise judging: which answer is better?
    print("\n" + "-" * 70)
    print("STEP 3: Pairwise Judging (which is better, A or B?)")
    print("-" * 70)

    pairwise_results = []
    for qa in qa_pairs:
        prompt = (
            f"You are an expert judge. Compare these two answers.\n\n"
            f"Question: {qa['question'][:200]}\n\n"
            f"Answer A: {qa['good_answer'][:250]}\n\n"
            f"Answer B: {qa['bad_answer'][:250]}\n\n"
            f"Which answer is better, A or B? Reply:\nWinner: A or B\nReason: your reason"
        )
        verdict = ask_mistral(prompt, max_tokens=100)
        pairwise_results.append({
            "question_id": qa["id"],
            "verdict": verdict[:120],
        })
        print(f"  Q{qa['id']}: {verdict[:100]}")

    # 5. Rubric-based judging: score on accuracy, completeness, clarity
    print("\n" + "-" * 70)
    print("STEP 4: Rubric-Based Judging (accuracy, completeness, clarity)")
    print("-" * 70)

    rubric_results = []
    for qa in qa_pairs:
        for label, answer in [("Good", qa["good_answer"]), ("Bad", qa["bad_answer"])]:
            prompt = (
                f"You are an expert evaluator. Score this answer using the rubric below.\n\n"
                f"Question: {qa['question'][:200]}\n"
                f"Correct answer: {qa['correct']}\n\n"
                f"Answer to evaluate: {answer[:300]}\n\n"
                f"Rubric (rate each 1-5):\n"
                f"- Accuracy: Is the answer factually correct?\n"
                f"- Completeness: Does it fully address the question?\n"
                f"- Clarity: Is it clearly written and easy to understand?\n\n"
                f"Reply in this format:\nAccuracy: X\nCompleteness: X\nClarity: X"
            )
            verdict = ask_mistral(prompt, max_tokens=100)
            rubric_results.append({
                "question_id": qa["id"],
                "type": label,
                "rubric_scores": verdict[:120],
            })
            print(f"  Q{qa['id']} ({label:4s}): {verdict[:100]}")

    # 6. Bias test: swap answer order and check if pairwise judgment changes
    print("\n" + "-" * 70)
    print("STEP 5: Position Bias Test (swap A/B order)")
    print("-" * 70)

    bias_results = []
    for qa in qa_pairs:
        # Original order: good=A, bad=B
        prompt_original = (
            f"Compare these two answers.\n\n"
            f"Question: {qa['question'][:200]}\n\n"
            f"Answer A: {qa['good_answer'][:250]}\n\n"
            f"Answer B: {qa['bad_answer'][:250]}\n\n"
            f"Which is better, A or B? Reply: Winner: A or B"
        )
        original_verdict = ask_mistral(prompt_original, max_tokens=50)

        # Swapped order: bad=A, good=B
        prompt_swapped = (
            f"Compare these two answers.\n\n"
            f"Question: {qa['question'][:200]}\n\n"
            f"Answer A: {qa['bad_answer'][:250]}\n\n"
            f"Answer B: {qa['good_answer'][:250]}\n\n"
            f"Which is better, A or B? Reply: Winner: A or B"
        )
        swapped_verdict = ask_mistral(prompt_swapped, max_tokens=50)

        # Check consistency: original should pick A, swapped should pick B
        consistent = ("A" in original_verdict and "B" in swapped_verdict) or \
                     ("B" in original_verdict and "A" in swapped_verdict)

        bias_results.append({
            "question_id": qa["id"],
            "original": original_verdict[:60],
            "swapped": swapped_verdict[:60],
            "consistent": consistent,
        })
        status = "CONSISTENT" if consistent else "POSITION BIAS DETECTED"
        print(f"  Q{qa['id']}: Original={original_verdict[:40]}  Swapped={swapped_verdict[:40]}  [{status}]")

    # 7. Print all results with pandas
    print("\n" + "=" * 70)
    print("  FINAL RESULTS SUMMARY")
    print("=" * 70)

    pd.set_option("display.max_colwidth", 60)
    pd.set_option("display.width", 200)

    print("\n--- Pointwise Scores ---")
    print(pd.DataFrame(pointwise_results).to_string(index=False))

    print("\n--- Pairwise Judgments ---")
    print(pd.DataFrame(pairwise_results).to_string(index=False))

    print("\n--- Rubric-Based Scores ---")
    print(pd.DataFrame(rubric_results).to_string(index=False))

    print("\n--- Position Bias Test ---")
    bias_df = pd.DataFrame(bias_results)
    print(bias_df.to_string(index=False))
    bias_count = len(bias_df[~bias_df["consistent"]])
    print(f"\n  Position bias detected in {bias_count}/{len(bias_df)} comparisons")

    mode = "Ollama + Mistral" if OLLAMA_AVAILABLE else "Simulated"
    print(f"\n  LLM mode: {mode}")

    # 8. Langfuse tracing
    print("\n" + "-" * 70)
    print("  LANGFUSE TRACING")
    print("-" * 70)
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
        trace = langfuse.trace(name="ch4-llm-as-judge", metadata={"mode": mode})

        for r in pointwise_results:
            span = trace.span(name=f"pointwise-{r['question_id']}-{r['type']}",
                              input={"type": r["type"]}, output={"verdict": r["verdict"]})
            span.end()

        for r in pairwise_results:
            span = trace.span(name=f"pairwise-{r['question_id']}",
                              output={"verdict": r["verdict"]})
            span.end()

        for r in bias_results:
            span = trace.span(name=f"bias-{r['question_id']}",
                              output={"original": r["original"], "swapped": r["swapped"],
                                      "consistent": r["consistent"]})
            span.score(name="position_bias_free", value=1.0 if r["consistent"] else 0.0)
            span.end()

        langfuse.flush()
        print("  Traces sent to Langfuse. View at: https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")

    print("\n" + "=" * 70)
    print("  Chapter 4 Hands-On Complete!")
    print("  Techniques demonstrated: Pointwise, Pairwise, Rubric-Based, Position Bias")
    print("=" * 70)


if __name__ == "__main__":
    main()
