"""
Chapter 5 - RAG Evaluation
Evaluator module: Heuristic implementations of all RAG evaluation metrics.

This module provides metric classes and functions organized into three tiers:
  1. RETRIEVAL metrics  - evaluate the quality of retrieved contexts
  2. GENERATION metrics - evaluate the quality of generated answers
  3. END-TO-END metrics - evaluate the full RAG pipeline

All implementations are heuristic (keyword overlap, entity matching, etc.)
so they run without any external LLM calls or third-party libraries.
"""

import math
import re
import time
import functools
from collections import Counter
from typing import Optional


# ============================================================================
# UTILITY HELPERS
# ============================================================================

def _tokenize(text: str) -> list[str]:
    """Lowercase tokenizer that strips punctuation."""
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def _token_set(text: str) -> set[str]:
    """Return the set of unique tokens in text."""
    return set(_tokenize(text))


def _ngrams(tokens: list[str], n: int) -> list[tuple]:
    """Return n-grams from a token list."""
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


_STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could of in to for on with "
    "at by from as into about between through during before after above "
    "below up down out off over under it its this that these those he "
    "she they them their we our you your and but or nor not no so if "
    "then than too also very".split()
)


def _content_tokens(text: str) -> list[str]:
    """Tokens with stopwords removed."""
    return [t for t in _tokenize(text) if t not in _STOPWORDS]


def _content_set(text: str) -> set[str]:
    return set(_content_tokens(text))


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _overlap_ratio(reference: set, candidate: set) -> float:
    """Fraction of reference tokens found in candidate."""
    if not reference:
        return 1.0
    if not candidate:
        return 0.0
    return len(reference & candidate) / len(reference)


def _extract_entities(text: str) -> set[str]:
    """
    Simple entity extraction: sequences of capitalized words (2+ chars)
    or known numeric patterns.
    """
    entities = set()
    # Capitalized word sequences
    for m in re.finditer(r"(?:[A-Z][a-z]{1,}(?:\s+[A-Z][a-z]{1,})*)", text):
        entities.add(m.group().lower())
    # Numbers with units
    for m in re.finditer(r"\d+\.?\d*\s*(?:nm|mm|cm|m|km|kg|eV|Hz|K|%)", text):
        entities.add(m.group().strip())
    # Formulas like E = hv
    for m in re.finditer(r"[A-Z]\s*=\s*[a-zA-Z0-9]+", text):
        entities.add(m.group().replace(" ", "").lower())
    return entities


def _sentence_split(text: str) -> list[str]:
    """Split text into sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


# ============================================================================
# 1. RETRIEVAL METRICS
# ============================================================================

class RetrievalMetrics:
    """Metrics that evaluate the quality of retrieved contexts."""

    @staticmethod
    def context_precision(
        retrieved_texts: list[str],
        relevance_labels: list[int],
    ) -> float:
        """
        Context Precision (Average Precision variant).

        Measures whether relevant documents are ranked higher than irrelevant
        ones.  For each position k with a relevant document, compute
        precision@k and average over all relevant documents.

        Returns a value in [0, 1]; 1.0 means all relevant docs come first.
        """
        if not relevance_labels:
            return 0.0
        total_relevant = sum(relevance_labels)
        if total_relevant == 0:
            return 0.0

        cumulative_relevant = 0
        precision_sum = 0.0
        for k, label in enumerate(relevance_labels, start=1):
            if label == 1:
                cumulative_relevant += 1
                precision_at_k = cumulative_relevant / k
                precision_sum += precision_at_k

        return precision_sum / total_relevant

    @staticmethod
    def context_recall(
        retrieved_texts: list[str],
        ground_truth: str,
        relevance_labels: Optional[list[int]] = None,
    ) -> float:
        """
        Context Recall.

        Estimates what fraction of the ground-truth information is covered
        by the retrieved contexts.  Uses content-word overlap between the
        ground truth and the concatenated relevant contexts.
        """
        gt_tokens = _content_set(ground_truth)
        if not gt_tokens:
            return 1.0

        if relevance_labels is not None:
            relevant_texts = [
                t for t, lab in zip(retrieved_texts, relevance_labels) if lab == 1
            ]
        else:
            relevant_texts = retrieved_texts

        if not relevant_texts:
            return 0.0

        combined = _content_set(" ".join(relevant_texts))
        return _overlap_ratio(gt_tokens, combined)

    @staticmethod
    def context_relevance(
        query: str,
        retrieved_texts: list[str],
    ) -> dict:
        """
        Context Relevance.

        Scores each retrieved chunk for relevance to the query using
        content-word Jaccard similarity.  Also returns the mean score.
        """
        query_set = _content_set(query)
        scores = []
        for text in retrieved_texts:
            chunk_set = _content_set(text)
            scores.append(round(_jaccard(query_set, chunk_set), 4))

        mean_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "per_chunk_scores": scores,
            "mean_relevance": round(mean_score, 4),
        }

    @staticmethod
    def hit_rate_and_mrr(
        relevance_labels: list[int],
    ) -> dict:
        """
        Hit Rate and Mean Reciprocal Rank (MRR) for a single query.

        Hit Rate: 1 if at least one relevant document is retrieved, else 0.
        MRR: 1/rank of the first relevant document.
        """
        hit = 0
        mrr = 0.0
        for rank, label in enumerate(relevance_labels, start=1):
            if label == 1:
                hit = 1
                mrr = 1.0 / rank
                break
        return {"hit_rate": hit, "mrr": round(mrr, 4)}

    @staticmethod
    def ndcg(
        relevance_labels: list[int],
        k: Optional[int] = None,
    ) -> float:
        """
        Normalized Discounted Cumulative Gain (NDCG@k).

        Measures ranking quality accounting for graded relevance and
        position discount.
        """
        if k is None:
            k = len(relevance_labels)
        labels = relevance_labels[:k]

        def dcg(rels: list[int]) -> float:
            return sum(
                rel / math.log2(pos + 2) for pos, rel in enumerate(rels)
            )

        actual_dcg = dcg(labels)
        ideal_labels = sorted(labels, reverse=True)
        ideal_dcg = dcg(ideal_labels)

        if ideal_dcg == 0:
            return 0.0
        return round(actual_dcg / ideal_dcg, 4)


# ============================================================================
# 2. GENERATION METRICS
# ============================================================================

class GenerationMetrics:
    """Metrics that evaluate the quality of generated answers."""

    @staticmethod
    def answer_relevance(
        query: str,
        generated_answer: str,
    ) -> dict:
        """
        Answer Relevance.

        Measures how well the generated answer addresses the query.
        Uses content-word overlap and bigram overlap.
        """
        query_tokens = _content_tokens(query)
        answer_tokens = _content_tokens(generated_answer)

        query_set = set(query_tokens)
        answer_set = set(answer_tokens)

        unigram_overlap = _jaccard(query_set, answer_set)

        query_bigrams = set(_ngrams(query_tokens, 2))
        answer_bigrams = set(_ngrams(answer_tokens, 2))
        bigram_overlap = _jaccard(query_bigrams, answer_bigrams) if query_bigrams else 0.0

        # Weighted combination
        score = 0.7 * unigram_overlap + 0.3 * bigram_overlap
        return {
            "score": round(score, 4),
            "unigram_overlap": round(unigram_overlap, 4),
            "bigram_overlap": round(bigram_overlap, 4),
        }

    @staticmethod
    def faithfulness(
        generated_answer: str,
        context_texts: list[str],
    ) -> dict:
        """
        Faithfulness (a.k.a. Groundedness at the claim level).

        Splits the answer into sentences (claims) and checks what fraction
        of claims are supported by at least one context passage, using
        content-word overlap as a proxy for entailment.

        Returns overall score and per-claim details.
        """
        claims = _sentence_split(generated_answer)
        if not claims:
            return {"score": 1.0, "supported_claims": 0, "total_claims": 0, "details": []}

        context_combined = " ".join(context_texts)
        context_set = _content_set(context_combined)

        supported = 0
        details = []
        for claim in claims:
            claim_tokens = _content_set(claim)
            if not claim_tokens:
                details.append({"claim": claim, "supported": True, "overlap": 1.0})
                supported += 1
                continue
            overlap = _overlap_ratio(claim_tokens, context_set)
            is_supported = overlap >= 0.5
            if is_supported:
                supported += 1
            details.append({
                "claim": claim[:80] + ("..." if len(claim) > 80 else ""),
                "supported": is_supported,
                "overlap": round(overlap, 4),
            })

        score = supported / len(claims)
        return {
            "score": round(score, 4),
            "supported_claims": supported,
            "total_claims": len(claims),
            "details": details,
        }

    @staticmethod
    def groundedness(
        generated_answer: str,
        context_texts: list[str],
    ) -> dict:
        """
        Groundedness.

        Measures to what extent the answer is grounded in the provided
        contexts.  Uses entity-level and content-word-level overlap.
        A complementary view to faithfulness.
        """
        answer_entities = _extract_entities(generated_answer)
        context_blob = " ".join(context_texts)
        context_entities = _extract_entities(context_blob)

        entity_coverage = _overlap_ratio(answer_entities, context_entities) if answer_entities else 1.0

        answer_content = _content_set(generated_answer)
        context_content = _content_set(context_blob)
        token_coverage = _overlap_ratio(answer_content, context_content)

        score = 0.5 * entity_coverage + 0.5 * token_coverage
        return {
            "score": round(score, 4),
            "entity_coverage": round(entity_coverage, 4),
            "token_coverage": round(token_coverage, 4),
            "answer_entities_found": len(answer_entities),
            "context_entities_found": len(context_entities),
        }

    @staticmethod
    def citation_correctness(
        generated_answer: str,
        citations: list[int],
        context_texts: list[str],
    ) -> dict:
        """
        Citation Correctness.

        For each citation [k] in the answer, check whether the cited context
        actually supports the claim near the citation marker.  Uses keyword
        overlap as a proxy.
        """
        if not citations:
            return {
                "score": 0.0,
                "correct_citations": 0,
                "total_citations": 0,
                "details": [],
            }

        # Split answer around citation markers [1], [2], ...
        # Each segment before a citation is the claim for that citation
        pattern = r"\[(\d+)\]"
        parts = re.split(pattern, generated_answer)

        # parts alternates: text, citation_num, text, citation_num, ...
        claim_citation_pairs = []
        for i in range(1, len(parts), 2):
            cite_idx = int(parts[i])
            claim_text = parts[i - 1].strip() if i - 1 >= 0 else ""
            claim_citation_pairs.append((claim_text, cite_idx))

        correct = 0
        details = []
        for claim_text, cite_idx in claim_citation_pairs:
            if 1 <= cite_idx <= len(context_texts):
                ctx = context_texts[cite_idx - 1]
                claim_set = _content_set(claim_text)
                ctx_set = _content_set(ctx)
                overlap = _overlap_ratio(claim_set, ctx_set) if claim_set else 0.0
                is_correct = overlap >= 0.4
            else:
                overlap = 0.0
                is_correct = False

            if is_correct:
                correct += 1
            details.append({
                "citation": cite_idx,
                "claim_snippet": claim_text[:60] + ("..." if len(claim_text) > 60 else ""),
                "correct": is_correct,
                "overlap": round(overlap, 4),
            })

        total = len(claim_citation_pairs)
        score = correct / total if total > 0 else 0.0
        return {
            "score": round(score, 4),
            "correct_citations": correct,
            "total_citations": total,
            "details": details,
        }

    @staticmethod
    def source_attribution(
        generated_answer: str,
        citations: list[int],
        context_texts: list[str],
    ) -> dict:
        """
        Source Attribution.

        Evaluates whether the answer properly attributes information to its
        sources.  Checks:
          1. Attribution coverage: fraction of answer sentences with a citation
          2. Attribution accuracy: fraction of citations pointing to relevant contexts
        """
        sentences = _sentence_split(generated_answer)
        if not sentences:
            return {"coverage": 1.0, "accuracy": 1.0, "score": 1.0}

        cited_sentences = 0
        for sent in sentences:
            if re.search(r"\[\d+\]", sent):
                cited_sentences += 1

        coverage = cited_sentences / len(sentences)

        # Accuracy: each cited context should be relevant to the answer
        accurate_citations = 0
        for cite_idx in citations:
            if 1 <= cite_idx <= len(context_texts):
                ctx_set = _content_set(context_texts[cite_idx - 1])
                answer_set = _content_set(generated_answer)
                overlap = _jaccard(ctx_set, answer_set)
                if overlap >= 0.1:
                    accurate_citations += 1

        accuracy = accurate_citations / len(citations) if citations else 1.0

        score = 0.5 * coverage + 0.5 * accuracy
        return {
            "coverage": round(coverage, 4),
            "accuracy": round(accuracy, 4),
            "score": round(score, 4),
        }

    @staticmethod
    def hallucination_detection(
        generated_answer: str,
        context_texts: list[str],
        ground_truth: str = "",
    ) -> dict:
        """
        Hallucination Detection.

        Identifies potential hallucinations by finding claims in the answer
        that are not supported by any context AND contradict or are absent
        from the ground truth.

        Returns a hallucination risk score (0 = no hallucination, 1 = all hallucinated).
        """
        claims = _sentence_split(generated_answer)
        if not claims:
            return {"risk_score": 0.0, "flagged_claims": [], "total_claims": 0}

        context_blob = " ".join(context_texts)
        context_set = _content_set(context_blob)
        gt_set = _content_set(ground_truth) if ground_truth else set()

        flagged = []
        for claim in claims:
            claim_set = _content_set(claim)
            if not claim_set:
                continue

            ctx_overlap = _overlap_ratio(claim_set, context_set)
            gt_overlap = _overlap_ratio(claim_set, gt_set) if gt_set else 0.5  # neutral if no GT

            # Claim is flagged if poorly supported by context AND ground truth
            if ctx_overlap < 0.4 and gt_overlap < 0.4:
                flagged.append({
                    "claim": claim[:100] + ("..." if len(claim) > 100 else ""),
                    "context_overlap": round(ctx_overlap, 4),
                    "gt_overlap": round(gt_overlap, 4),
                })

        risk_score = len(flagged) / len(claims) if claims else 0.0
        return {
            "risk_score": round(risk_score, 4),
            "flagged_claims": flagged,
            "total_claims": len(claims),
            "hallucination_detected": risk_score > 0.0,
        }


# ============================================================================
# 3. END-TO-END METRICS
# ============================================================================

class EndToEndMetrics:
    """Metrics that evaluate the full RAG pipeline."""

    @staticmethod
    def context_utilization(
        generated_answer: str,
        context_texts: list[str],
    ) -> dict:
        """
        Context Utilization.

        Measures how much of the retrieved context is actually used in the
        generated answer.  High utilization suggests the retriever is
        bringing in relevant material; low utilization suggests noise.
        """
        if not context_texts:
            return {"score": 0.0, "per_chunk_utilization": [], "chunks_used": 0}

        answer_set = _content_set(generated_answer)
        per_chunk = []
        chunks_used = 0

        for i, ctx in enumerate(context_texts):
            ctx_set = _content_set(ctx)
            if not ctx_set:
                per_chunk.append(0.0)
                continue
            # How much of this chunk appears in the answer
            util = len(ctx_set & answer_set) / len(ctx_set)
            per_chunk.append(round(util, 4))
            if util >= 0.15:
                chunks_used += 1

        mean_util = sum(per_chunk) / len(per_chunk)
        return {
            "score": round(mean_util, 4),
            "per_chunk_utilization": per_chunk,
            "chunks_used": chunks_used,
            "total_chunks": len(context_texts),
        }

    @staticmethod
    def answer_correctness(
        generated_answer: str,
        ground_truth: str,
    ) -> dict:
        """
        Answer Correctness.

        Compares the generated answer to the ground-truth answer using
        multiple similarity measures:
          - Token-level F1
          - Jaccard similarity
          - Entity overlap
        """
        gen_tokens = _content_tokens(generated_answer)
        gt_tokens = _content_tokens(ground_truth)

        gen_counter = Counter(gen_tokens)
        gt_counter = Counter(gt_tokens)

        common = sum((gen_counter & gt_counter).values())
        precision = common / sum(gen_counter.values()) if gen_counter else 0.0
        recall = common / sum(gt_counter.values()) if gt_counter else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        jaccard = _jaccard(set(gen_tokens), set(gt_tokens))

        gen_ents = _extract_entities(generated_answer)
        gt_ents = _extract_entities(ground_truth)
        entity_overlap = _jaccard(gen_ents, gt_ents) if (gen_ents or gt_ents) else 1.0

        # Weighted composite
        score = 0.5 * f1 + 0.3 * jaccard + 0.2 * entity_overlap
        return {
            "score": round(score, 4),
            "f1": round(f1, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "jaccard": round(jaccard, 4),
            "entity_overlap": round(entity_overlap, 4),
        }

    @staticmethod
    def chunk_evaluation(
        retrieved_texts: list[str],
        relevance_labels: list[int],
        query: str,
    ) -> dict:
        """
        Chunk Evaluation.

        Comprehensive per-chunk quality assessment:
          - Relevance to query
          - Information density (unique content words / total words)
          - Redundancy between chunks
        """
        query_set = _content_set(query)
        chunk_reports = []

        all_chunk_sets = [_content_set(t) for t in retrieved_texts]

        for i, text in enumerate(retrieved_texts):
            chunk_set = all_chunk_sets[i]
            all_tokens = _tokenize(text)

            # Relevance
            relevance = _jaccard(query_set, chunk_set) if query_set else 0.0

            # Information density
            density = len(chunk_set) / len(all_tokens) if all_tokens else 0.0

            # Redundancy: max overlap with any other chunk
            max_redundancy = 0.0
            for j, other_set in enumerate(all_chunk_sets):
                if i != j:
                    redundancy = _jaccard(chunk_set, other_set)
                    max_redundancy = max(max_redundancy, redundancy)

            chunk_reports.append({
                "chunk_index": i,
                "label": relevance_labels[i] if i < len(relevance_labels) else 0,
                "query_relevance": round(relevance, 4),
                "info_density": round(density, 4),
                "max_redundancy": round(max_redundancy, 4),
                "token_count": len(all_tokens),
            })

        avg_relevance = (
            sum(c["query_relevance"] for c in chunk_reports) / len(chunk_reports)
            if chunk_reports else 0.0
        )
        avg_density = (
            sum(c["info_density"] for c in chunk_reports) / len(chunk_reports)
            if chunk_reports else 0.0
        )

        return {
            "per_chunk": chunk_reports,
            "avg_query_relevance": round(avg_relevance, 4),
            "avg_info_density": round(avg_density, 4),
        }

    @staticmethod
    def latency_tracker(func):
        """
        Latency Tracking decorator.

        Wraps a function to measure its execution time.  Useful for
        tracking retrieval latency, generation latency, and total
        pipeline latency.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            return {
                "result": result,
                "latency_seconds": round(elapsed, 6),
            }
        return wrapper

    @staticmethod
    def measure_latency(label: str = "operation"):
        """
        Context-manager style latency measurement.
        Returns a dict you can inspect after the block.

        Usage:
            timer = EndToEndMetrics.measure_latency("retrieval")
            timer["start"]()
            # ... do work ...
            timer["stop"]()
            print(timer["latency_seconds"])
        """
        record = {"label": label, "latency_seconds": 0.0, "_start": 0.0}

        def start():
            record["_start"] = time.perf_counter()

        def stop():
            record["latency_seconds"] = round(
                time.perf_counter() - record["_start"], 6
            )

        record["start"] = start
        record["stop"] = stop
        return record

    @staticmethod
    def cost_tracker(
        num_input_tokens: int,
        num_output_tokens: int,
        model_name: str = "gpt-4",
    ) -> dict:
        """
        Cost Tracking.

        Estimates the dollar cost of a RAG pipeline call based on
        approximate per-token pricing for common models.
        """
        # Approximate pricing per 1K tokens (USD) as of mid-2025
        PRICING = {
            "gpt-4":          {"input": 0.03,   "output": 0.06},
            "gpt-4-turbo":    {"input": 0.01,   "output": 0.03},
            "gpt-4o":         {"input": 0.005,  "output": 0.015},
            "gpt-3.5-turbo":  {"input": 0.0005, "output": 0.0015},
            "claude-3-opus":  {"input": 0.015,  "output": 0.075},
            "claude-3-sonnet":{"input": 0.003,  "output": 0.015},
            "claude-3-haiku": {"input": 0.00025,"output": 0.00125},
            "claude-3.5-sonnet":{"input": 0.003,"output": 0.015},
        }

        prices = PRICING.get(model_name, PRICING["gpt-4"])
        input_cost = (num_input_tokens / 1000) * prices["input"]
        output_cost = (num_output_tokens / 1000) * prices["output"]
        total_cost = input_cost + output_cost

        return {
            "model": model_name,
            "input_tokens": num_input_tokens,
            "output_tokens": num_output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
        }


# ============================================================================
# 4. RAG EVALUATION PIPELINE (orchestrates all metrics)
# ============================================================================

class RAGEvaluationPipeline:
    """
    Orchestrates all metrics into a single evaluation run.

    Given a RAG example (query, contexts, answer, ground truth), it
    computes every metric and returns a comprehensive report.
    """

    def __init__(self):
        self.retrieval = RetrievalMetrics()
        self.generation = GenerationMetrics()
        self.end_to_end = EndToEndMetrics()

    def evaluate_single(self, example: dict) -> dict:
        """
        Run all metrics on a single RAG example.

        Expected keys in `example`:
          - query, ground_truth_answer, retrieved_contexts (list of dicts
            with 'text' and optionally 'relevance_label'),
          - generated_answer, citations (list of ints)
        """
        query = example["query"]
        ground_truth = example.get("ground_truth_answer", "")
        generated = example.get("generated_answer", "")
        contexts = example.get("retrieved_contexts", [])
        citations = example.get("citations", [])

        ctx_texts = [c["text"] for c in contexts]
        rel_labels = [c.get("relevance_label", 0) for c in contexts]

        # --- Retrieval ---
        retrieval_results = {
            "context_precision": self.retrieval.context_precision(ctx_texts, rel_labels),
            "context_recall": self.retrieval.context_recall(ctx_texts, ground_truth, rel_labels),
            "context_relevance": self.retrieval.context_relevance(query, ctx_texts),
            "hit_rate_mrr": self.retrieval.hit_rate_and_mrr(rel_labels),
            "ndcg": self.retrieval.ndcg(rel_labels),
        }

        # --- Generation ---
        generation_results = {
            "answer_relevance": self.generation.answer_relevance(query, generated),
            "faithfulness": self.generation.faithfulness(generated, ctx_texts),
            "groundedness": self.generation.groundedness(generated, ctx_texts),
            "citation_correctness": self.generation.citation_correctness(generated, citations, ctx_texts),
            "source_attribution": self.generation.source_attribution(generated, citations, ctx_texts),
            "hallucination_detection": self.generation.hallucination_detection(generated, ctx_texts, ground_truth),
        }

        # --- End-to-End ---
        end_to_end_results = {
            "context_utilization": self.end_to_end.context_utilization(generated, ctx_texts),
            "answer_correctness": self.end_to_end.answer_correctness(generated, ground_truth),
            "chunk_evaluation": self.end_to_end.chunk_evaluation(ctx_texts, rel_labels, query),
        }

        return {
            "id": example.get("id", "?"),
            "query": query[:80],
            "quality_label": example.get("quality_label", "unknown"),
            "retrieval": retrieval_results,
            "generation": generation_results,
            "end_to_end": end_to_end_results,
        }

    def evaluate_dataset(self, examples: list[dict]) -> dict:
        """
        Run all metrics on a list of RAG examples and compute aggregates.
        """
        results = [self.evaluate_single(ex) for ex in examples]

        # Aggregate key scalar metrics
        def _safe_mean(values):
            return round(sum(values) / len(values), 4) if values else 0.0

        aggregates = {
            "num_examples": len(results),
            "avg_context_precision": _safe_mean(
                [r["retrieval"]["context_precision"] for r in results]
            ),
            "avg_context_recall": _safe_mean(
                [r["retrieval"]["context_recall"] for r in results]
            ),
            "avg_ndcg": _safe_mean(
                [r["retrieval"]["ndcg"] for r in results]
            ),
            "avg_hit_rate": _safe_mean(
                [r["retrieval"]["hit_rate_mrr"]["hit_rate"] for r in results]
            ),
            "avg_mrr": _safe_mean(
                [r["retrieval"]["hit_rate_mrr"]["mrr"] for r in results]
            ),
            "avg_answer_relevance": _safe_mean(
                [r["generation"]["answer_relevance"]["score"] for r in results]
            ),
            "avg_faithfulness": _safe_mean(
                [r["generation"]["faithfulness"]["score"] for r in results]
            ),
            "avg_groundedness": _safe_mean(
                [r["generation"]["groundedness"]["score"] for r in results]
            ),
            "avg_citation_correctness": _safe_mean(
                [r["generation"]["citation_correctness"]["score"] for r in results]
            ),
            "avg_hallucination_risk": _safe_mean(
                [r["generation"]["hallucination_detection"]["risk_score"] for r in results]
            ),
            "avg_answer_correctness": _safe_mean(
                [r["end_to_end"]["answer_correctness"]["score"] for r in results]
            ),
            "avg_context_utilization": _safe_mean(
                [r["end_to_end"]["context_utilization"]["score"] for r in results]
            ),
        }

        return {
            "per_example": results,
            "aggregates": aggregates,
        }


# ============================================================================
# 5. MODULE SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EVALUATOR MODULE - Quick Self-Test")
    print("=" * 60)

    # Minimal smoke test
    ret = RetrievalMetrics()
    gen = GenerationMetrics()
    e2e = EndToEndMetrics()

    labels = [1, 1, 0, 1]
    print(f"\nContext Precision:  {ret.context_precision([], labels)}")
    print(f"Hit Rate / MRR:    {ret.hit_rate_and_mrr(labels)}")
    print(f"NDCG:              {ret.ndcg(labels)}")

    answer = "The Roche limit is the distance where tidal forces exceed gravity."
    contexts = ["The Roche limit is the distance from a celestial body within which tidal forces dominate."]
    print(f"\nFaithfulness:      {gen.faithfulness(answer, contexts)['score']}")
    print(f"Groundedness:      {gen.groundedness(answer, contexts)['score']}")

    cost = e2e.cost_tracker(5000, 500, "gpt-4")
    print(f"\nCost (gpt-4):      ${cost['total_cost_usd']}")

    print("\nAll self-tests passed.")
