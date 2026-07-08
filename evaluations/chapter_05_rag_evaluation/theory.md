# Chapter 5: RAG Evaluation - Comprehensive Theory

Evaluating Retrieval-Augmented Generation pipelines using heuristic metrics (keyword overlap, entity matching, statistics). All metrics run without external LLM calls or third-party libraries.

---

## Overview

RAG pipelines combine retrieval and generation -- each must be evaluated independently and together. This chapter implements **17 RAG evaluation metrics** in three tiers:

1. **Retrieval Metrics** -- quality of retrieved contexts
2. **Generation Metrics** -- quality of generated answers
3. **End-to-End Metrics** -- full pipeline evaluation

```
 RAG EVALUATION ARCHITECTURE

 +-----------+     +-------------+     +------------+
 |   Query   |---->|  Retriever  |---->|  Generator  |----> Answer
 +-----------+     +-------------+     +------------+
       |                  |                   |
       v                  v                   v
  +---------+      +-------------+     +-------------+
  | Context |      |  Retrieval  |     |  Generation  |
  | Relevance|     |   Metrics   |     |   Metrics    |
  +---------+      +-------------+     +-------------+
                          |                   |
                          v                   v
                   +-----------------------------+
                   |    End-to-End Metrics        |
                   +-----------------------------+
```

---

## Metric Taxonomy Summary

```
RETRIEVAL METRICS:
  Context Precision        Are relevant docs ranked higher than irrelevant ones?
  Context Recall           Do retrieved docs cover the ground-truth information?
  Context Relevance        How topically related is each chunk to the query?
  Hit Rate                 Was at least one relevant doc retrieved?
  MRR                      How high is the first relevant doc ranked?
  NDCG                     Overall ranking quality with position discount.

GENERATION METRICS:
  Answer Relevance         Does the answer address the query?
  Faithfulness             Is every claim in the answer supported by context?
  Groundedness             Is the answer grounded in entity and content overlap?
  Citation Correctness     Do citations point to the right sources?
  Source Attribution       Are claims properly attributed to sources?
  Hallucination Detection  Are there fabricated/unsupported claims?

END-TO-END METRICS:
  Context Utilization      How much retrieved context is actually used?
  Answer Correctness       Does the answer match the ground truth?
  Chunk Evaluation         Per-chunk quality (relevance, density, redundancy).
  Latency Tracking         Pipeline execution time measurement.
  Cost Tracking            Estimated dollar cost per model.

Total metrics implemented: 17
```

---

# Tier 1: Retrieval Metrics

## Context Precision (Average Precision)

**What it measures:** Whether relevant documents are ranked higher than irrelevant ones.
**Intuition:** For each position where a relevant doc appears, compute precision@k, then average over all relevant docs.

```
Context Precision = (1/R) * SUM_k [ rel(k) * cumulative_relevant(k) / k ]
  R = total relevant docs, rel(k) = 1 if doc at k is relevant
```

**Interpretation:** 1.0 = perfect ranking (all relevant before irrelevant). 0.0 = no relevant docs retrieved.

**Pros:** Sensitive to ranking order; rewards placing relevant docs first; well-established IR metric.
**Cons:** Binary relevance only; requires ground-truth labels; ignores degree of relevance.

---

## Context Recall

**What it measures:** Fraction of ground-truth information covered by retrieved contexts.
**Intuition:** Compare content words in ground-truth vs. concatenated relevant contexts.

```
Context Recall = |GT_tokens INTERSECT Context_tokens| / |GT_tokens|
  GT_tokens = content words in ground-truth, Context_tokens = content words in relevant contexts
```

**Interpretation:** 1.0 = all ground-truth info present. 0.0 = nothing retrieved.

**Pros:** Directly measures information coverage; independent of ranking.
**Cons:** Depends on ground-truth quality; misses paraphrased content.

---

## Context Relevance

**What it measures:** How topically related each retrieved chunk is to the query.
**Intuition:** Jaccard similarity between query and chunk content words.

```
Context Relevance(chunk) = |Query_tokens INTERSECT Chunk_tokens| / |Query_tokens UNION Chunk_tokens|
```

**Interpretation:** Per-chunk scores show topical relevance; mean summarizes retrieved set quality.

**Pros:** Per-chunk granularity for diagnosing individual retrieval failures; fast.
**Cons:** Vocabulary-based, not semantic; short queries produce noisy scores.

---

## Hit Rate & Mean Reciprocal Rank (MRR)

**What it measures:** Hit Rate = did the retriever find anything relevant? MRR = how quickly?
**Intuition:** Hit Rate is binary (1 if any relevant doc found). MRR = 1/rank of first relevant doc.

```
Hit Rate = 1 if any rel(k) == 1, else 0
MRR = 1 / rank_first_relevant
```

**Interpretation:** Hit Rate=1 means at least one relevant doc retrieved. MRR=1.0 means first relevant doc is at rank 1.

**Pros:** Simple, interpretable; Hit Rate is the minimum bar; MRR captures user experience.
**Cons:** Hit Rate ignores position; MRR only considers first relevant doc; both are binary.

---

## Normalized Discounted Cumulative Gain (NDCG)

**What it measures:** Overall ranking quality accounting for graded relevance and position.
**Intuition:** Discount relevance by log of position, then normalize by ideal ranking.

```
DCG = SUM_k [ rel(k) / log2(k+1) ]
NDCG = DCG / Ideal_DCG
  rel(k) = relevance score at position k, Ideal_DCG = DCG of best possible ranking
```

**Interpretation:** 1.0 = perfect ranking. Handles graded relevance. NDCG@k evaluates top-k only.

**Pros:** Handles graded relevance; position-sensitive; industry-standard for search ranking.
**Cons:** Requires relevance labels; log discount may not match real user behavior.

---

# Tier 2: Generation Metrics

## Answer Relevance

**What it measures:** Whether the answer addresses the query's topic.
**Intuition:** Weighted Jaccard overlap of unigrams (0.7) and bigrams (0.3) between query and answer.

```
Answer Relevance = 0.7 * Jaccard(query_unigrams, answer_unigrams)
                 + 0.3 * Jaccard(query_bigrams, answer_bigrams)
```

**Interpretation:** Higher scores = better topical alignment between query and answer.

**Pros:** Fast, deterministic; bigram overlap captures phrase-level relevance.
**Cons:** Vocabulary-based, misses semantic paraphrasing; short queries may mislead.

---

## Faithfulness

**What it measures:** Whether every claim in the answer is supported by the retrieved context.
**Intuition:** Split answer into sentences (claims). A claim is supported if >= 50% of its content words appear in the context.

```
Faithfulness = Supported_Claims / Total_Claims
A claim is supported if: |claim_tokens INTERSECT context_tokens| / |claim_tokens| >= 0.5
```

**Interpretation:** 1.0 = all claims supported. Per-claim details show exactly which sentences lack support.

**Pros:** Pinpoints unsupported claims; directly measures core RAG requirement.
**Cons:** Token overlap is not true entailment; 0.5 threshold needs per-domain tuning; misses contradictions.

---

## Groundedness

**What it measures:** Whether the answer as a whole is grounded in retrieved context (entity + token coverage).
**Intuition:** Average of entity coverage and token coverage between answer and context.

```
Groundedness = 0.5 * Entity_Coverage + 0.5 * Token_Coverage
Entity_Coverage = |Answer_Entities INTERSECT Context_Entities| / |Answer_Entities|
Token_Coverage  = |Answer_Content INTERSECT Context_Content| / |Answer_Content|
```

**Interpretation:** High entity coverage = same named entities; high token coverage = shared vocabulary.

**Pros:** Entity-level analysis catches factual grounding; complementary to faithfulness.
**Cons:** Regex-based entity extraction; does not verify correctness of entity usage.

---

## Citation Correctness

**What it measures:** Whether each citation [k] in the answer points to a context chunk that supports the adjacent claim.
**Intuition:** For each citation marker, check if claim text overlaps with cited context chunk (threshold >= 0.4).

```
Citation Correctness = Correct_Citations / Total_Citations
Correct if: overlap(claim_tokens, cited_context_tokens) >= 0.4
```

**Interpretation:** 1.0 = all citations verified. Per-citation details show which are correct.

**Pros:** Catches fabricated citations; verifies citations are meaningful.
**Cons:** 0.4 threshold is heuristic; cannot verify if citation is the *best* source; depends on [k] format.

---

## Source Attribution

**What it measures:** Whether the answer properly attributes information to sources (coverage + accuracy).
**Intuition:** Coverage = fraction of sentences with citations. Accuracy = fraction of cited contexts relevant to answer.

```
Source Attribution = 0.5 * Coverage + 0.5 * Accuracy
Coverage = Sentences_with_citations / Total_sentences
Accuracy = Accurate_citations / Total_citations  (accurate if Jaccard >= 0.1)
```

**Interpretation:** Captures both breadth (coverage) and quality (accuracy) of attribution.

**Pros:** Identifies answers that cite heavily but inaccurately, or accurately but sparsely.
**Cons:** Coverage rewards density which may not always be desirable; 0.1 threshold is lenient.

---

## Hallucination Detection

**What it measures:** Claims in the answer unsupported by both context and ground truth.
**Intuition:** A claim is flagged if context overlap < 0.4 AND ground-truth overlap < 0.4.

```
Risk Score = Flagged_Claims / Total_Claims
Flagged if: overlap(claim, context) < 0.4 AND overlap(claim, ground_truth) < 0.4
Returns: risk_score, hallucination_detected (bool), flagged_claims (list)
```

**Interpretation:** 0.0 = no hallucinations. 1.0 = all claims potentially hallucinated.

**Pros:** Dual-check reduces false positives; per-claim flagging enables targeted correction.
**Cons:** Cannot detect subtle or contradictory hallucinations; depends on ground-truth availability.

---

# Tier 3: End-to-End Metrics

## Context Utilization

**What it measures:** How much of the retrieved context the generator actually used.
**Intuition:** For each chunk, compute fraction of its content words that appear in the answer.

```
Utilization(chunk) = |Chunk_tokens INTERSECT Answer_tokens| / |Chunk_tokens|
Score = mean(Utilization) across all chunks
Chunk is "used" if utilization >= 0.15
```

**Interpretation:** Low utilization suggests noisy retrieval or generator ignoring context.

**Pros:** Diagnoses retrieval-generation alignment; per-chunk granularity.
**Cons:** Low utilization may be acceptable for backup sources; common words inflate overlap.

---

## Answer Correctness

**What it measures:** Whether the generated answer matches the ground-truth answer.
**Intuition:** Composite of token F1 (0.5), Jaccard similarity (0.3), and entity overlap (0.2).

```
F1 = 2 * Precision * Recall / (Precision + Recall)
Jaccard = |Gen_set INTERSECT GT_set| / |Gen_set UNION GT_set|
Entity_Overlap = Jaccard(Gen_entities, GT_entities)
Answer Correctness = 0.5 * F1 + 0.3 * Jaccard + 0.2 * Entity_Overlap
```

**Interpretation:** Multi-dimensional score; F1 balances precision/recall, entity overlap catches factual accuracy.

**Pros:** Multi-dimensional reduces single-measure bias; weighted combination is configurable.
**Cons:** Token-based misses semantic equivalence; regex-based entities; volatile on short answers.

---

## Chunk Evaluation

**What it measures:** Per-chunk quality across relevance, information density, and redundancy.
**Intuition:** Good chunk = high query relevance + high info density + low redundancy.

```
Relevance(chunk) = Jaccard(query_content, chunk_content)
Info_Density(chunk) = |unique_content_words| / |all_words|
Max_Redundancy(chunk) = max over j != i of Jaccard(chunk_i, chunk_j)
```

**Interpretation:** High relevance + high density + low redundancy = ideal chunk.

**Pros:** Per-chunk diagnosis; identifies redundancy (common chunking failure).
**Cons:** Vocabulary-based; info density is a rough proxy; does not assess factual accuracy.

---

## Latency Tracking

**What it measures:** Wall-clock time of each pipeline component.
**Intuition:** Supports decorator-style (`@latency_tracker`) and manual start/stop tracking.

**Pros:** Simple, zero-overhead; essential for production monitoring.
**Cons:** Wall-clock not CPU time; does not separate network latency; single-request only.

---

## Cost Tracking

**What it measures:** Estimated dollar cost per query based on token counts and model pricing.
**Intuition:** `(input_tokens/1000) * input_price + (output_tokens/1000) * output_price`.

```
Model                 Input $/1K    Output $/1K
gpt-4                 0.03000       0.06000
gpt-4-turbo           0.01000       0.03000
gpt-4o                0.00500       0.01500
gpt-3.5-turbo         0.00050       0.00150
claude-3-opus          0.01500       0.07500
claude-3-sonnet        0.00300       0.01500
claude-3-haiku         0.00025       0.00125
claude-3.5-sonnet      0.00300       0.01500
```

**Pros:** Enables cost-aware model selection; covers major providers.
**Cons:** Pricing is approximate and changes; no batch/enterprise discounts; token costs only.

---

# Quality Comparison: Good vs. Hallucinated Answers

If metrics work correctly, good answers should consistently outscore hallucinated ones:

| Metric | Good Answers | Hallucinated Answers | Direction |
|---|---|---|---|
| Faithfulness | Higher | Lower | Good > Halluc |
| Groundedness | Higher | Lower | Good > Halluc |
| Hallucination Risk | Lower | Higher | Good < Halluc |
| Answer Correctness | Higher | Lower | Good > Halluc |
| Citation Correctness | Higher | Lower | Good > Halluc |
| Context Utilization | Higher | Lower | Good > Halluc |

---

# RAG Evaluation Framework Comparison

```
Framework      # Metrics  Approach
-------------- ---------- ----------------------------------------
RAGAS                   6  LLM-as-judge with structured decomposition
DeepEval                7  LLM-as-judge with pytest integration
TruLens                 5  Feedback functions with LLM or embedding models
LangSmith               4  Human + LLM annotation platform with tracing
Phoenix (Arize)         3  Observability-first with embedding analysis
```

**RAGAS** (github.com/explodinggradients/ragas) -- Metrics: Faithfulness, Answer Relevance, Context Precision/Recall, Context Utilization, Answer Correctness. Pros: strong IR grounding, sub-question decomposition, active community. Cons: requires LLM calls (cost/latency), faithfulness noisy for long answers.

**DeepEval** (github.com/confident-ai/deepeval) -- Metrics: Faithfulness, Answer Relevancy, Contextual Precision/Recall, Hallucination, Bias, Toxicity. Pros: pytest CI/CD integration, built-in bias/toxicity, custom metrics. Cons: heavier dependencies, some metrics mirror RAGAS.

**TruLens** (github.com/truera/trulens) -- Metrics: Groundedness, Answer/Context Relevance, Comprehensiveness, Harmful content. Pros: experiment-tracking dashboard, multi-provider support, chain-of-thought traces. Cons: dashboard adds complexity, initially LangChain/LlamaIndex-coupled.

**LangSmith** (smith.langchain.com) -- Metrics: Correctness, Helpfulness, Harmlessness, Custom evaluators. Pros: deep LangChain integration with tracing, human-in-the-loop, dataset versioning. Cons: LangChain-ecosystem focused, SaaS dependency.

**Phoenix** (github.com/Arize-ai/phoenix) -- Metrics: MRR, NDCG, Precision@k, Hallucination, QA, Toxicity, Embedding drift. Pros: embedding visualization and drift detection, open-source, production monitoring. Cons: evaluation secondary to observability, fewer decomposed RAG metrics.

**Our Heuristic Approach (This Chapter):** Zero cost, deterministic, fast, educational. Trade-off: less semantic depth than LLM-based methods. Recommendation: heuristic metrics for CI/CD; LLM-based (RAGAS, DeepEval) for release decisions.

---

# Why Use LangGraph, Langfuse & Tracing for RAG?

**LangGraph:** Models the RAG pipeline as a state graph with testable, swappable nodes and conditional routing (e.g., re-retrieve if context score is low).

**Langfuse:** Production dashboard where every query becomes a trace with nested spans. Attach scores to filter by low-faithfulness queries and debug silently failing answers.

**Tracing:** Captures per-request latency, token usage, and retrieval quality. Finds the 5% of queries that take 10x longer or retrieve irrelevant context.

---

# Summary

17 RAG evaluation metrics across three tiers:
- **RETRIEVAL**: Context Precision, Recall, Relevance, Hit Rate, MRR, NDCG
- **GENERATION**: Answer Relevance, Faithfulness, Groundedness, Citation Correctness, Source Attribution, Hallucination
- **END-TO-END**: Context Utilization, Answer Correctness, Chunk Evaluation, Latency, Cost

## Key Takeaways

1. Good answers consistently outscore hallucinated ones across metrics
2. Heuristic metrics provide fast, cheap, deterministic evaluation
3. LLM-based frameworks (RAGAS, DeepEval, TruLens) add semantic depth
4. Use heuristic metrics in CI/CD; LLM-based for release decisions
5. No single metric is sufficient -- use a balanced scorecard

## Best Practices

- Evaluate retrieval and generation **separately** -- a good generator cannot save a bad retriever
- Use **multiple metrics** for a balanced scorecard; never rely on one number
- Include **hallucinated examples** in test sets to validate metric discrimination
- Track **per-query** metrics, not just aggregates
- Monitor **latency and cost** alongside quality in production

## Common Mistakes

- Relying on a single metric while ignoring others
- Evaluating generation without evaluating retrieval
- Using only aggregate scores without per-query breakdowns
- Not including adversarial examples in the evaluation dataset
- Assuming high faithfulness means high correctness (faithful to bad context is still wrong)

## Interview Questions

1. **What are the three tiers of RAG evaluation?** Retrieval, Generation, and End-to-End -- each evaluates a different pipeline component.

2. **Difference between faithfulness and groundedness?** Faithfulness checks per-claim support; groundedness checks overall entity + token coverage. Complementary views.

3. **Why is context precision more useful than hit rate?** Hit rate is binary; context precision accounts for ranking order of relevant documents.

4. **How to detect hallucinations in RAG?** Check each claim against both context and ground truth; low overlap on both = potential hallucination.

5. **Heuristic vs. LLM-based evaluation -- when?** Heuristic for CI/CD and rapid iteration; LLM-based for release decisions and semantic analysis.

6. **What does NDCG measure that MRR does not?** NDCG accounts for graded relevance and positions of all relevant docs; MRR only considers the first.

7. **How to evaluate citation correctness?** Parse citation markers, extract adjacent claims, verify cited chunk supports the claim via content overlap.

8. **What is context utilization?** Fraction of retrieved context actually used in the answer. Low = noisy retrieval or generator ignoring context.

9. **Three strengths and limitations of RAGAS?** Strengths: IR grounding, sub-question decomposition, active community. Limitations: LLM cost/latency, noisy faithfulness on long answers.

10. **How to build a balanced RAG evaluation scorecard?** Include one metric per tier minimum (e.g., NDCG + faithfulness + hallucination detection + answer correctness + latency). Validate with good and bad examples.
