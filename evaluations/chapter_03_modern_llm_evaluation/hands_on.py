import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 3 Hands-On: Modern LLM Evaluation with Real Ollama + Mistral
=====================================================================
Loads questions from train.csv, gets Mistral answers via Ollama,
then uses Ollama as a judge to evaluate correctness, relevance,
completeness, and hallucination.
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
        letter = random.choice("ABCDE")
        return f"The answer is {letter}. This option best matches the scientific definition described."
    if "correct?" in prompt.lower():
        return random.choice(["YES - The answer correctly identifies the concept.",
                              "NO - The answer misidentifies the key mechanism."])
    if "rate 1-5" in prompt.lower() or "Rate 1-5" in prompt:
        score = random.randint(2, 5)
        return f"Score: {score} - The response addresses the core question adequately."
    if "hallucin" in prompt.lower() or "fabricat" in prompt.lower():
        return random.choice(["NO - The answer stays within established facts.",
                              "YES - The answer includes unsupported claims."])
    return "Score: 3 - Adequate response."


def judge(question, answer, criteria_prompt):
    prompt = (f"You are an evaluation judge.\n\nQuestion: {question}\n\n"
              f"Answer to evaluate: {answer}\n\n{criteria_prompt}\n\nBe concise. Reply in one line.")
    return ask_mistral(prompt, max_tokens=100)


def main():
    print("=" * 70)
    print("  CHAPTER 3 HANDS-ON: Multi-Dimension LLM Evaluation")
    print("=" * 70)

    # 1. Load 3 questions from train.csv
    df = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\train.csv", nrows=3)
    print(f"\nLoaded {len(df)} questions from train.csv")
    print(f"Columns: {list(df.columns)}\n")

    results = []

    for idx, row in df.iterrows():
        print("-" * 70)
        print(f"Question {idx + 1} (id={row['id']}): {row['prompt'][:90]}...")

        # Build the MCQ prompt for Mistral
        choices = ""
        for letter in ["A", "B", "C", "D", "E"]:
            choices += f"  {letter}) {row[letter][:80]}...\n"

        question_prompt = (
            f"{row['prompt']}\n\n"
            f"Choices:\n{choices}\n"
            f"Pick the correct letter and briefly explain why."
        )

        # 2. Get Mistral's answer
        print("\n  Asking Mistral...")
        answer = ask_mistral(question_prompt)
        print(f"  Mistral answered: {answer[:120]}...")
        print(f"  Correct answer:   {row['answer']}")

        # 3. Evaluate on 4 dimensions using Ollama judge calls
        print("\n  Judging on 4 dimensions...")

        # Correctness
        correctness = judge(
            row["prompt"], answer,
            f"The correct answer is {row['answer']}. Is this answer correct? Reply YES or NO, then explain briefly."
        )
        print(f"    Correctness:    {correctness[:100]}")

        # Relevance
        relevance = judge(
            row["prompt"], answer,
            "Is this answer relevant to the question? Rate 1-5 (1=irrelevant, 5=perfectly relevant). Format: Score: X - reason"
        )
        print(f"    Relevance:      {relevance[:100]}")

        # Completeness
        completeness = judge(
            row["prompt"], answer,
            "Does this answer fully address the question? Rate 1-5 (1=incomplete, 5=fully complete). Format: Score: X - reason"
        )
        print(f"    Completeness:   {completeness[:100]}")

        # Hallucination check
        hallucination = judge(
            row["prompt"], answer,
            "Does this answer contain made-up or fabricated information? Reply YES or NO, then explain briefly."
        )
        print(f"    Hallucination:  {hallucination[:100]}")

        # 4. Collect results
        results.append({
            "question_id": row["id"],
            "correct_answer": row["answer"],
            "mistral_answer": answer[:80],
            "correctness": correctness[:80],
            "relevance": relevance[:80],
            "completeness": completeness[:80],
            "hallucination": hallucination[:80],
        })

    # 5. Print results table
    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY TABLE")
    print("=" * 70)

    results_df = pd.DataFrame(results)
    pd.set_option("display.max_colwidth", 60)
    pd.set_option("display.width", 200)
    print(results_df.to_string(index=False))

    mode = "Ollama + Mistral" if OLLAMA_AVAILABLE else "Simulated"
    print(f"\n  LLM mode: {mode}")

    # 6. Langfuse tracing
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
        trace = langfuse.trace(name="ch3-modern-llm-eval", metadata={"mode": mode})

        for r in results:
            gen = trace.generation(
                name=f"question-{r['question_id']}",
                model="mistral" if OLLAMA_AVAILABLE else "simulated",
                input=r.get("correct_answer", ""),
                output=r.get("mistral_answer", ""),
            )
            gen.score(name="correctness", value=1.0 if "YES" in str(r.get("correctness", "")).upper() else 0.0)

        langfuse.flush()
        print("  Traces sent to Langfuse. View at: https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")

    print("\n" + "=" * 70)
    print("  Chapter 3 Hands-On Complete!")
    print("  Evaluated 3 questions on: Correctness, Relevance, Completeness, Hallucination")
    print("=" * 70)


if __name__ == "__main__":
    main()
