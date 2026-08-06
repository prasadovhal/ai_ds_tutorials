"""
File 15: Evaluation Metrics
Concepts: LLM-as-judge, hallucination scoring, groundedness, faithfulness, relevance, latency, cost

Evaluation answers: "Is the answer good?"
Unlike confidence (model's self-rating), evaluation uses objective criteria.

This file implements multiple metrics:
- Hallucination score: does answer contradict context?
- Groundedness score: is answer supported by facts?
- Faithfulness score: does answer match retrieved context?
- Relevance score: does answer address the question?
- Latency and cost tracking
"""

import os
from dotenv import load_dotenv
import ollama
import time
from typing import Dict, Any

load_dotenv()

client = ollama.Client()


def hallucination_score(query, context, answer):
    """
    Detect hallucinations: claim facts not in context.

    LLM judges: "Does the answer contain any claims contradicted by the context?"
    Returns 0-100 score (100 = no hallucinations, 0 = entirely hallucinated)
    """

    evaluation_prompt = f"""Evaluate the following answer for hallucinations.
    A hallucination is when the answer claims facts not supported by the context.

    Context: {context[:300]}

    Question: {query}

    Answer: {answer}

    Rate the answer for hallucinations (0-100):
    0 = entirely hallucinated (contradicts context)
    50 = partially accurate (some claims contradicted)
    100 = fully grounded (no contradictions)

    Return ONLY a number (0-100):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a critical evaluator. Rate for hallucinations."},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(0, min(100, score))
    except:
        score = 50

    return score


def groundedness_score(query, context, answer):
    """
    Groundedness: what % of the answer is supported by the context?

    Returns 0-100 score (100 = fully grounded, 0 = no grounding)
    """

    evaluation_prompt = f"""Evaluate the groundedness of this answer.
    Groundedness measures what % of the answer is supported by the retrieved context.

    Context: {context[:300]}

    Answer: {answer}

    Score groundedness (0-100):
    0 = no claims supported by context
    50 = ~50% of claims supported
    100 = all claims well-supported by context

    Return ONLY a number (0-100):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You evaluate information retrieval quality."},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(0, min(100, score))
    except:
        score = 50

    return score


def faithfulness_score(query, context, answer):
    """
    Faithfulness: does the answer accurately reflect the context?

    This is similar to hallucination but focuses on accuracy rather than contradiction.
    Returns 0-100 score (100 = faithful, 0 = unfaithful)
    """

    evaluation_prompt = f"""Evaluate the faithfulness of this answer to the context.
    Faithfulness means: the answer accurately represents information in the context.

    Context: {context[:300]}

    Question: {query}

    Answer: {answer}

    Score faithfulness (0-100):
    0 = answer misrepresents context
    50 = partially faithful (some inaccuracies)
    100 = highly faithful (accurate representation)

    Return ONLY a number (0-100):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You evaluate answer faithfulness."},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(0, min(100, score))
    except:
        score = 50

    return score


def relevance_score(query, answer):
    """
    Relevance: does the answer address the question?

    Returns 0-100 score (100 = highly relevant, 0 = irrelevant)
    """

    evaluation_prompt = f"""Evaluate the relevance of this answer to the question.

    Question: {query}

    Answer: {answer}

    Score relevance (0-100):
    0 = answer is off-topic, doesn't address question
    50 = partially relevant (some connection)
    100 = directly addresses the question

    Return ONLY a number (0-100):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You evaluate answer relevance."},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(0, min(100, score))
    except:
        score = 50

    return score


def context_precision_score(retrieved_chunks, answer):
    """
    RAGAS Metric: Context Precision

    Measures: what % of retrieved chunks are actually relevant to the answer?

    Problem it solves: Retriever might return irrelevant chunks.
    Example: Query "What is photosynthesis?"
    Retrieved: [correct chunk, travel policy, laptop policy]
    Context Precision = 1/3 = 33% (only 1 out of 3 chunks was useful)

    Returns 0-100 score (100 = all chunks relevant, 0 = no chunks relevant)
    """

    if not retrieved_chunks:
        return 0

    evaluation_prompt = f"""Evaluate which retrieved chunks are relevant to the answer.
    A chunk is relevant if it supports or relates to the answer.

    Retrieved chunks:
    {chr(10).join([f'{i+1}. {chunk[:100]}' for i, chunk in enumerate(retrieved_chunks[:5])])}

    Generated answer: {answer[:300]}

    For each chunk, decide: is it relevant to the answer? (yes/no)
    Then calculate: (relevant chunks) / (total chunks) * 100

    Return ONLY a number (0-100):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You evaluate retrieval quality."},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(0, min(100, score))
    except:
        score = 50

    return score


def context_recall_score(query, retrieved_chunks):
    """
    RAGAS Metric: Context Recall

    Measures: did we retrieve ALL the chunks needed to answer the question?

    Problem it solves: Retriever might miss relevant chunks.
    Example: Query "Compare Python and Java"
    Retrieved: [Python info]
    Context Recall = 50% (missing Java info)

    Returns 0-100 score (100 = all necessary chunks retrieved, 0 = missed everything)
    """

    evaluation_prompt = f"""Evaluate whether the retrieved context is sufficient to answer the question.
    Context Recall measures: did we retrieve ALL chunks needed to fully answer?

    Question: {query}

    Retrieved chunks:
    {chr(10).join([f'{i+1}. {chunk[:100]}' for i, chunk in enumerate(retrieved_chunks[:5])])}

    Score context recall (0-100):
    0 = missing almost all needed information
    50 = retrieved some info, but gaps remain
    100 = retrieved all necessary information to answer

    Return ONLY a number (0-100):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You evaluate if context is complete."},
            {"role": "user", "content": evaluation_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(0, min(100, score))
    except:
        score = 50

    return score


def comprehensive_evaluation(query, context, answer, latency_ms, tokens_used, retrieved_chunks=None):
    """
    Full evaluation: all metrics + latency + cost + RAGAS metrics (if chunks provided).

    Returns a dict with all scores and metadata.
    """

    print(f"Evaluating query: {query[:50]}...")

    # Quality metrics
    halluc_score = hallucination_score(query, context, answer)
    ground_score = groundedness_score(query, context, answer)
    faith_score = faithfulness_score(query, context, answer)
    relev_score = relevance_score(query, answer)

    # RAGAS metrics (if retrieved chunks provided)
    context_prec_score = None
    context_rec_score = None
    if retrieved_chunks:
        context_prec_score = context_precision_score(retrieved_chunks, answer)
        context_rec_score = context_recall_score(query, retrieved_chunks)

    # Compute overall score (weighted average)
    # Weights: hallucination most important, then groundedness, then RAGAS, then relevance
    weights = {
        "hallucination": 0.35,
        "groundedness": 0.25,
        "faithfulness": 0.15,
        "relevance": 0.10,
        "ragas": 0.15  # Split between context precision and recall
    }

    overall_score = (
        halluc_score * weights["hallucination"] +
        ground_score * weights["groundedness"] +
        faith_score * weights["faithfulness"] +
        relev_score * weights["relevance"]
    )

    if context_prec_score is not None and context_rec_score is not None:
        ragas_avg = (context_prec_score + context_rec_score) / 2
        overall_score += ragas_avg * weights["ragas"]

    # Cost estimation
    estimated_cost = (tokens_used / 1000) * 0.003  # assuming $0.003 per 1K tokens

    quality_metrics = {
        "hallucination_score": halluc_score,
        "groundedness_score": ground_score,
        "faithfulness_score": faith_score,
        "relevance_score": relev_score,
        "overall_score": round(overall_score, 1)
    }

    # Add RAGAS metrics if available
    if context_prec_score is not None:
        quality_metrics["context_precision_score"] = context_prec_score
        quality_metrics["context_recall_score"] = context_rec_score

    return {
        "query": query[:50],
        "context_length": len(context),
        "answer_length": len(answer),
        "retrieved_chunks_count": len(retrieved_chunks) if retrieved_chunks else 0,
        "quality_metrics": quality_metrics,
        "performance_metrics": {
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "estimated_cost": round(estimated_cost, 6)
        }
    }


def evaluate_batch_responses(eval_dataset):
    """
    Evaluate a batch of query-answer pairs.

    Input: list of dicts with query, context, answer, latency_ms, tokens_used
    Output: list of evaluation results + summary
    """

    results = []

    for i, item in enumerate(eval_dataset):
        print(f"\n[{i+1}/{len(eval_dataset)}] Evaluating...")
        result = comprehensive_evaluation(
            query=item["query"],
            context=item["context"],
            answer=item["answer"],
            latency_ms=item["latency_ms"],
            tokens_used=item["tokens_used"],
            retrieved_chunks=item.get("retrieved_chunks")
        )
        results.append(result)

    # Compute summary stats
    scores = [r["quality_metrics"]["overall_score"] for r in results]
    latencies = [r["performance_metrics"]["latency_ms"] for r in results]
    costs = [r["performance_metrics"]["estimated_cost"] for r in results]

    summary = {
        "total_evaluations": len(results),
        "quality_summary": {
            "avg_overall_score": round(sum(scores) / len(scores), 1),
            "min_score": min(scores),
            "max_score": max(scores)
        },
        "performance_summary": {
            "avg_latency_ms": round(sum(latencies) / len(latencies), 1),
            "avg_cost": round(sum(costs) / len(costs), 6),
            "total_cost": round(sum(costs), 6)
        }
    }

    return results, summary


if __name__ == "__main__":
    print("File 15: Evaluation Metrics")
    print("=" * 60)

    # Sample evaluation data (with retrieved chunks for RAGAS metrics)
    eval_dataset = [
        {
            "query": "What is photosynthesis?",
            "context": "Photosynthesis is the process by which plants convert light energy into chemical energy. The light-dependent reactions occur in the thylakoid, producing ATP and NADPH. The Calvin cycle uses these to fix CO2.",
            "answer": "Photosynthesis is the process plants use to convert light into chemical energy. It occurs in two stages: light reactions in the thylakoid and the Calvin cycle in the stroma.",
            "latency_ms": 450,
            "tokens_used": 80,
            "retrieved_chunks": [
                "Light reactions in thylakoid membrane produce ATP and NADPH from water photolysis.",
                "Calvin cycle (light-independent reactions) fixes CO2 into glucose using ATP and NADPH.",
                "Photosystem I and II coordinate electron transport in photosynthesis."
            ]
        },
        {
            "query": "Explain DNA replication",
            "context": "DNA replication is semi-conservative and bidirectional. DNA polymerase III synthesizes the leading strand continuously and the lagging strand as Okazaki fragments.",
            "answer": "DNA replication uses RNA polymerase to copy the DNA strand. The process is quick and happens in one direction.",
            "latency_ms": 520,
            "tokens_used": 90,
            "retrieved_chunks": [
                "DNA polymerase III is the main replicative enzyme, not RNA polymerase.",
                "Leading strand is synthesized continuously; lagging strand uses Okazaki fragments.",
                "Semi-conservative replication: each new DNA molecule has one old and one new strand."
            ]
        },
        {
            "query": "What is quantum entanglement?",
            "context": "Quantum entanglement occurs when two particles are correlated such that measuring one instantly affects the other. Bell's theorem proves no local hidden variable theory can explain this.",
            "answer": "Quantum entanglement is when two particles remain connected and measuring one affects the other instantaneously, regardless of distance. This violates local realism.",
            "latency_ms": 680,
            "tokens_used": 120,
            "retrieved_chunks": [
                "Bell's theorem disproves local hidden variable theories of quantum mechanics.",
                "Entangled particles show correlations stronger than classical physics allows.",
                "Measurement of one entangled particle instantaneously affects measurement outcomes of the other."
            ]
        }
    ]

    print("\n--- Evaluating Batch of Responses ---")
    results, summary = evaluate_batch_responses(eval_dataset)

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    import json
    print(json.dumps(summary, indent=2))

    print("\n" + "=" * 60)
    print("INDIVIDUAL RESULTS")
    print("=" * 60)

    for i, result in enumerate(results, 1):
        print(f"\nEvaluation {i}: {result['query']}")
        print(f"  Overall score: {result['quality_metrics']['overall_score']}/100")
        print(f"  Hallucination: {result['quality_metrics']['hallucination_score']}")
        print(f"  Groundedness: {result['quality_metrics']['groundedness_score']}")
        print(f"  Faithfulness: {result['quality_metrics']['faithfulness_score']}")
        print(f"  Relevance: {result['quality_metrics']['relevance_score']}")

        # RAGAS metrics (if available)
        if "context_precision_score" in result['quality_metrics']:
            print(f"  Context Precision (RAGAS): {result['quality_metrics']['context_precision_score']}")
            print(f"  Context Recall (RAGAS): {result['quality_metrics']['context_recall_score']}")

        print(f"  Latency: {result['performance_metrics']['latency_ms']}ms")
        print(f"  Cost: ${result['performance_metrics']['estimated_cost']}")

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Hallucination score: detects factual contradictions")
    print("2. Groundedness score: % of answer supported by context")
    print("3. Faithfulness score: accuracy of context representation")
    print("4. Relevance score: does answer address question")
    print("5. RAGAS Context Precision: % of retrieved chunks actually useful")
    print("6. RAGAS Context Recall: were all necessary chunks retrieved?")
    print("7. Overall score: weighted combination including RAGAS metrics")
    print("8. Performance metrics: latency and estimated cost")
    print("9. Evaluation enables data-driven improvements to RAG systems")
