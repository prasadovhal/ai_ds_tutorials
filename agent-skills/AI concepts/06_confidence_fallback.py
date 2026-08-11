"""
File 6: Confidence-Based Fallback & Retry
Concepts: Self-evaluation, confidence scoring, escalation, retry with enrichment

After getting an LLM response, how do we know if it's good? We ask the LLM itself!
If confidence is low, we retry with additional context. If still low, escalate.

This is critical for production reliability.
"""

import os
from dotenv import load_dotenv
import ollama

load_dotenv()

client = ollama.Client()

def get_confidence_score(query, answer):
    """
    Ask the LLM to self-evaluate confidence in its answer (1-10).

    The LLM judges its own response. This is surprisingly effective:
    the model knows when it's guessing vs. when it's confident.
    """

    system_prompt = """You are an evaluator. The user asked a question, and I provided an answer.
    Rate my confidence in this answer on a scale of 1-10:
    1-3: Uncertain, likely contains errors or hallucinations
    4-6: Moderately confident, some aspects unclear
    7-10: Very confident, well-grounded and accurate

    Return ONLY a number (1-10)."""

    evaluation_prompt = f"""User question: {query}

    My answer: {answer}

    Rate my confidence (1-10):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(1, min(10, score))
    except:
        score = 5

    return score


def retry_with_enriched_context(query, original_answer, context):
    """
    If first answer had low confidence, retry with additional context.

    Context might be: domain facts, similar examples, or expert knowledge.
    This gives the model a second chance with better information.
    """

    enriched_prompt = f"""User's question: {query}

    Additional context that might help:
    {context}

    Please provide a more confident answer using this context:"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a science expert. Use the provided context to give a confident answer."},
            {"role": "user", "content": enriched_prompt}
        ]
    )

    return response['message']['content']


def confidence_fallback_pipeline(query, initial_answer, confidence_threshold=6):
    """
    Full pipeline:
    1. Get initial answer
    2. Score confidence
    3. If low confidence: retry with context
    4. If still low: flag for human review

    This ensures quality: low-confidence answers get a second chance.
    """

    # Step 1: Check initial confidence
    confidence_1 = get_confidence_score(query, initial_answer)

    result = {
        "query": query,
        "initial_answer": initial_answer,
        "initial_confidence": confidence_1,
        "final_answer": initial_answer,
        "final_confidence": confidence_1,
        "retried": False,
        "escalated": False
    }

    # Step 2: If low, add context and retry
    if confidence_1 < confidence_threshold:
        # In real system, fetch context from RAG or domain knowledge base
        # Here, we use a generic context for demo
        context = """Key science facts:
        - Complex concepts require multi-step explanation
        - Uncertainty is better than false confidence
        - Domain knowledge improves answer quality"""

        retry_answer = retry_with_enriched_context(query, initial_answer, context)
        confidence_2 = get_confidence_score(query, retry_answer)

        result["retried"] = True
        result["final_answer"] = retry_answer
        result["final_confidence"] = confidence_2

        # Step 3: If still low after retry, escalate
        if confidence_2 < confidence_threshold:
            result["escalated"] = True
            result["escalation_reason"] = "Low confidence after retry; needs human review"

    return result


def handle_low_confidence_answer(query):
    """
    Generate an initial answer, then run through confidence pipeline.
    """

    # Generate initial answer
    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a science expert. Answer concisely."},
            {"role": "user", "content": query}
        ]
    )

    initial_answer = response['message']['content']

    # Run confidence pipeline
    result = confidence_fallback_pipeline(query, initial_answer, confidence_threshold=6)

    return result


if __name__ == "__main__":

    test_queries = [
        "What is the role of mitochondria in cells?",
        "Explain the mechanism of quantum tunneling in semiconductors",
        "What are the latest discoveries in exoplanet detection?",
    ]

    print("\n--- Confidence Pipeline (with Retry) ---")
    for query in test_queries:
        print(f"\nQuery: {query}")

        result = handle_low_confidence_answer(query)

        print(f"Initial answer: {result['initial_answer'][:150]}...")
        print(f"Initial confidence: {result['initial_confidence']}/10")

        if result['retried']:
            print(f"[RETRY with context]")
            print(f"Retry answer: {result['final_answer'][:150]}...")
            print(f"Retry confidence: {result['final_confidence']}/10")

        if result['escalated']:
            print(f"[ESCALATION FLAGGED]: {result['escalation_reason']}")
        else:
            print(f"[ACCEPTED] Final confidence: {result['final_confidence']}/10")

    # ===== FAILURE CASE: Confident Hallucination =====
    print("\n" + "="*70)
    print("FAILURE CASE: Confident Hallucination (No Escalation)")
    print("="*70)

    failure_query = "What is the current CEO of OpenAI as of 2026?"
    print(f"\nQuery: {failure_query}")
    print("(Note: Model was trained in Feb 2025, so it may hallucinate about 2026)")

    result = handle_low_confidence_answer(failure_query)

    print(f"\nInitial answer: {result['initial_answer']}")
    print(f"Initial confidence: {result['initial_confidence']}/10")

    if result['retried']:
        print(f"\n[RETRY with context]")
        print(f"Retry answer: {result['final_answer']}")
        print(f"Retry confidence: {result['final_confidence']}/10")

    if result['escalated']:
        print(f"[ESCALATION FLAGGED]: {result['escalation_reason']}")
    else:
        print(f"\n[ACCEPTED] Final confidence: {result['final_confidence']}/10")
        print("⚠️  PROBLEM: Model is confident about 2026 info it doesn't actually know!")
        print("    Confidence score ≠ Accuracy. Model hallucinated with high confidence.")
        print("    No escalation triggered because confidence stayed above threshold.")

    # ===== FAILURE CASE 2: Escalation Without Resolution =====
    print("\n" + "="*70)
    print("FAILURE CASE 2: Escalation Triggered But No Human Handler")
    print("="*70)

    failure_query_2 = "Describe the protein folding algorithm discovered in 2024 at my company"
    print(f"\nQuery: {failure_query_2}")
    print("(Note: Proprietary/specialized knowledge the model won't know)")

    result2 = handle_low_confidence_answer(failure_query_2)

    print(f"\nInitial answer: {result2['initial_answer'][:100]}...")
    print(f"Initial confidence: {result2['initial_confidence']}/10")

    if result2['retried']:
        print(f"\n[RETRY with context]")
        print(f"Retry answer: {result2['final_answer'][:100]}...")
        print(f"Retry confidence: {result2['final_confidence']}/10")

    if result2['escalated']:
        print(f"\n[ESCALATION FLAGGED]: {result2['escalation_reason']}")
        print("⚠️  PROBLEM: Escalation triggered, but then what?")
        print("    - No human is actually reviewing this")
        print("    - Generic context didn't help with proprietary knowledge")
        print("    - System flags it but can't resolve it")
        print("    - User gets an escalation message instead of an answer")
    else:
        print(f"\n[ACCEPTED] Final confidence: {result2['final_confidence']}/10")
