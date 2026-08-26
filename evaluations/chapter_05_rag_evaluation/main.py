"""
Chapter 5: RAG Evaluation

Covers evaluation for RAG (Retrieval-Augmented Generation) systems:
- Retrieval evaluation: assessing quality of retrieved context
  * Context precision: are retrieved docs actually relevant?
  * Context recall: what % of answer facts appear in context?
  * Context relevance: how well does context match the query?
  * Hit rate: is at least one relevant doc retrieved?
  * MRR (Mean Reciprocal Rank): rank position of first relevant doc
  * NDCG (Normalized DCG): ranking quality metric
- Generation evaluation: assessing quality of generated answers
  * Answer relevance: does answer address the query?
  * Faithfulness: is answer grounded in retrieved context?
  * Groundedness: factual consistency with evidence
  * Citation correctness: are citations accurate?
  * Hallucination rate: % of ungrounded claims
- End-to-end evaluation: combined retrieval + generation metrics
- Framework comparison: RAGAS, DeepEval, LangSmith, Phoenix, TruLens

Single-file, beginner-friendly walkthrough of RAG evaluation components.
"""

from statistics import mean


RAG_EXAMPLE = {
    "query": "Why is the sky blue?",
    "ground_truth": "The sky looks blue because air scatters short blue wavelengths more strongly than red wavelengths.",
    "answer": "The sky looks blue because molecules in the air scatter blue light more strongly than red light.",
    "contexts": [
        {"text": "Rayleigh scattering makes short wavelengths scatter more in the atmosphere.", "relevant": 1},
        {"text": "Blue light has a shorter wavelength than red light.", "relevant": 1},
        {"text": "Bananas are rich in potassium.", "relevant": 0},
    ],
    "citations": [1, 2],
}


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def words(text):
    return set(text.lower().replace(".", "").split())


def overlap_ratio(left_text, right_text):
    left_words = words(left_text)
    right_words = words(right_text)
    if not left_words:
        return 0.0
    return len(left_words & right_words) / len(left_words)


def context_precision(contexts):
    relevant_so_far = 0
    precision_sum = 0
    for index, context in enumerate(contexts, start=1):
        if context["relevant"] == 1:
            relevant_so_far += 1
            precision_sum += relevant_so_far / index
    if relevant_so_far == 0:
        return 0.0
    return precision_sum / relevant_so_far


def context_recall(contexts):
    relevant_found = sum(context["relevant"] for context in contexts)
    total_relevant_available = 2
    return relevant_found / total_relevant_available


def context_relevance(query, contexts):
    scores = []
    for context in contexts:
        scores.append(overlap_ratio(query, context["text"]))
    return scores


def hit_rate(contexts):
    for context in contexts:
        if context["relevant"] == 1:
            return 1.0
    return 0.0


def mrr(contexts):
    for index, context in enumerate(contexts, start=1):
        if context["relevant"] == 1:
            return 1 / index
    return 0.0


def ndcg(contexts):
    dcg = 0
    for index, context in enumerate(contexts, start=1):
        gain = context["relevant"]
        dcg += gain / index
    ideal = 1 / 1 + 1 / 2
    return dcg / ideal


def answer_relevance(query, answer):
    return overlap_ratio(query, answer)


def faithfulness(answer, contexts):
    combined_context = " ".join(context["text"] for context in contexts)
    return overlap_ratio(answer, combined_context)


def groundedness(answer, contexts):
    return faithfulness(answer, contexts)


def citation_correctness(citations, contexts):
    correct = 0
    for citation in citations:
        if contexts[citation - 1]["relevant"] == 1:
            correct += 1
    return correct / len(citations)


def hallucination_rate(answer, contexts):
    return 1 - faithfulness(answer, contexts)


def end_to_end_score(example):
    scores = [
        context_precision(example["contexts"]),
        context_recall(example["contexts"]),
        answer_relevance(example["query"], example["answer"]),
        faithfulness(example["answer"], example["contexts"]),
        citation_correctness(example["citations"], example["contexts"]),
    ]
    return mean(scores)


def compare_frameworks():
    frameworks = {
        "RAGAS": "strong for RAG-specific metrics",
        "DeepEval": "strong for test suites",
        "LangSmith": "strong for tracing plus evals",
        "Phoenix": "strong for observability",
        "TruLens": "strong for feedback functions",
    }
    for name, note in frameworks.items():
        print(f"{name}: {note}")


def main():
    section("Chapter 5: RAG Evaluation")
    print(f"Query: {RAG_EXAMPLE['query']}")

    section("1. Retrieval Metrics")
    print(f"Context precision: {context_precision(RAG_EXAMPLE['contexts']):.2f}")
    print(f"Context recall: {context_recall(RAG_EXAMPLE['contexts']):.2f}")
    print(f"Context relevance per chunk: {context_relevance(RAG_EXAMPLE['query'], RAG_EXAMPLE['contexts'])}")
    print(f"Hit rate: {hit_rate(RAG_EXAMPLE['contexts']):.2f}")
    print(f"MRR: {mrr(RAG_EXAMPLE['contexts']):.2f}")
    print(f"NDCG: {ndcg(RAG_EXAMPLE['contexts']):.2f}")

    section("2. Generation Metrics")
    print(f"Answer relevance: {answer_relevance(RAG_EXAMPLE['query'], RAG_EXAMPLE['answer']):.2f}")
    print(f"Faithfulness: {faithfulness(RAG_EXAMPLE['answer'], RAG_EXAMPLE['contexts']):.2f}")
    print(f"Groundedness: {groundedness(RAG_EXAMPLE['answer'], RAG_EXAMPLE['contexts']):.2f}")
    print(f"Citation correctness: {citation_correctness(RAG_EXAMPLE['citations'], RAG_EXAMPLE['contexts']):.2f}")
    print(f"Hallucination rate: {hallucination_rate(RAG_EXAMPLE['answer'], RAG_EXAMPLE['contexts']):.2f}")

    section("3. End-to-End RAG Score")
    print(f"Overall score: {end_to_end_score(RAG_EXAMPLE):.2f}")

    section("4. Framework Comparison")
    compare_frameworks()


if __name__ == "__main__":
    main()
