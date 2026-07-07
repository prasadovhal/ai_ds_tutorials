# Chapter 5: RAG Evaluation - Comprehensive Theory

Evaluating Retrieval-Augmented Generation pipelines using heuristic metrics (keyword overlap, entity matching, statistics). All metrics run without external LLM calls or third-party libraries.

---

## Overview

RAG (Retrieval-Augmented Generation) pipelines combine two stages -- retrieval and generation -- and each must be evaluated independently as well as together. This chapter implements **17 RAG evaluation metrics** organized into three tiers:

1. **Retrieval Metrics** -- evaluate the quality of retrieved contexts
2. **Generation Metrics** -- evaluate the quality of generated answers
3. **End-to-End Metrics** -- evaluate the full RAG pipeline

All implementations are heuristic (keyword overlap, entity matching, etc.) so they run without any external LLM calls or third-party libraries.

```
 RAG EVALUATION ARCHITECTURE
 ============================

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

Retrieval metrics evaluate the quality of retrieved contexts -- are the right documents being pulled from the knowledge base, and are they ranked appropriately?

---

## Context Precision (Average Precision)

### Problem
When a retriever returns a mix of relevant and irrelevant documents, we need to know whether the relevant documents are ranked higher than the irrelevant ones. A retriever that buries relevant documents at the bottom of the list forces the generator to wade through noise.

### Intuition
Context Precision uses the Average Precision formulation: for each position k where a relevant document appears, compute precision@k (the fraction of documents up to position k that are relevant), then average those values over all relevant documents.

### How It Works
1. Walk through the ranked list of retrieved documents.
2. At each position k where a relevant document appears, compute `precision@k = cumulative_relevant / k`.
3. Average all such precision@k values over the total number of relevant documents.

### Formula

```
                   1       K
Context Precision = --- * SUM  [ rel(k) * (cumulative_relevant(k) / k) ]
                   R     k=1

Where:
  R   = total number of relevant documents
  K   = total number of retrieved documents
  rel(k) = 1 if document at position k is relevant, 0 otherwise
  cumulative_relevant(k) = number of relevant docs in positions 1..k
```

### Interpretation
- **1.0** = all relevant docs come before all irrelevant docs (perfect ranking)
- **0.0** = no relevant documents retrieved
- Values between 0 and 1 indicate mixed ranking quality

### Advantages
- Sensitive to ranking order, not just set membership
- Rewards retrievers that place relevant documents first
- Well-established metric from information retrieval

### Limitations
- Binary relevance labels (relevant/irrelevant) may oversimplify
- Does not account for the degree of relevance
- Requires ground-truth relevance labels for each retrieved document

---

## Context Recall

### Problem
Even if a retriever ranks relevant documents well, it may miss important information. Context Recall measures what fraction of the ground-truth information is actually covered by the retrieved contexts.

### Intuition
Compare the content words in the ground-truth answer against the content words in the concatenated relevant retrieved contexts. The overlap ratio tells us how much of the ground truth the retriever captured.

### How It Works
1. Extract content words (removing stopwords) from the ground-truth answer.
2. Extract content words from all relevant retrieved contexts (concatenated).
3. Compute the fraction of ground-truth content words found in the retrieved contexts.

### Formula

```
                           |GT_tokens INTERSECT Context_tokens|
Context Recall = -------------------------------------------
                              |GT_tokens|

Where:
  GT_tokens      = set of content words in the ground-truth answer
  Context_tokens = set of content words in concatenated relevant contexts
```

### Interpretation
- **1.0** = all ground-truth information is present in retrieved contexts
- **0.0** = no ground-truth information was retrieved
- Fraction of ground-truth information covered by retrieved contexts

### Advantages
- Directly measures information coverage
- Independent of ranking order (focuses on completeness)

### Limitations
- Depends on ground-truth quality
- Token overlap is a proxy -- misses paraphrased content
- Does not distinguish between important and trivial information

---

## Context Relevance

### Problem
Each retrieved chunk should be topically related to the query. Irrelevant chunks waste context window space and can mislead the generator.

### Intuition
For each retrieved chunk, compute how much its vocabulary overlaps with the query vocabulary. Chunks with high overlap are likely relevant; those with low overlap are noise.

### How It Works
1. Extract content words from the query.
2. For each retrieved chunk, extract content words and compute the Jaccard similarity with the query content words.
3. Report per-chunk scores and the mean relevance across all chunks.

### Formula

```
                              |Query_tokens INTERSECT Chunk_tokens|
Context Relevance(chunk) = -------------------------------------------
                              |Query_tokens UNION Chunk_tokens|

(Jaccard similarity between query and chunk content words)
```

### Interpretation
- Per-chunk scores show which chunks are topically related and which are noise
- Mean relevance summarizes the overall quality of the retrieved set

### Advantages
- Per-chunk granularity allows diagnosing individual retrieval failures
- Simple and fast to compute

### Limitations
- Jaccard similarity is vocabulary-based, not semantic
- Short queries produce noisy scores
- Cannot detect semantic relevance without shared vocabulary

---

## Hit Rate & Mean Reciprocal Rank (MRR)

### Problem
At the most basic level, we need to know: did the retriever find *anything* relevant? And if so, how quickly?

### Intuition
- **Hit Rate**: Binary -- 1 if any relevant document is retrieved, 0 otherwise.
- **MRR**: 1 divided by the rank of the first relevant document. If the first relevant doc is at position 1, MRR = 1.0. If at position 3, MRR = 0.333.

### How It Works
1. Walk through the ranked list of retrieved documents.
2. As soon as a relevant document is found, record its rank.
3. Hit Rate = 1 (a relevant doc was found). MRR = 1/rank.
4. If no relevant document is found, Hit Rate = 0 and MRR = 0.

### Formula

```
Hit Rate = 1 if any rel(k) == 1, else 0

         1
MRR = -------
       rank_first_relevant

Where:
  rank_first_relevant = position of the first relevant document in the ranked list
```

### Interpretation
- Hit Rate = 1 means at least one relevant doc was retrieved
- MRR = 1.0 means the first relevant doc is at rank 1 (best case)
- MRR < 1.0 means the user/generator has to look past irrelevant docs first

### Advantages
- Extremely simple and interpretable
- Hit Rate is the minimum bar for retrieval quality
- MRR captures user experience (finding relevant info quickly)

### Limitations
- Hit Rate ignores how many relevant docs are found or their positions
- MRR only considers the first relevant doc, ignoring the rest
- Both are binary and do not support graded relevance

---

## Normalized Discounted Cumulative Gain (NDCG)

### Problem
Some documents are more relevant than others. We need a metric that accounts for both graded relevance and the position of each document in the ranking.

### Intuition
Documents at the top of the list are more valuable. NDCG discounts relevance by the logarithm of the position, then normalizes by the ideal (best possible) ranking.

### How It Works
1. Compute DCG (Discounted Cumulative Gain): sum of relevance scores, each divided by log2(position + 1).
2. Compute Ideal DCG: sort documents by relevance (best first) and compute DCG again.
3. NDCG = DCG / Ideal DCG.

### Formula

```
              K   rel(k)
DCG = SUM   ---------
             k=1  log2(k + 1)

              DCG
NDCG = ---------------
            Ideal_DCG

Where:
  rel(k)     = relevance score of document at position k
  K          = number of documents (or cutoff)
  Ideal_DCG  = DCG computed on the ideal (sorted by relevance desc) ranking
```

### Interpretation
- **1.0** = perfect ranking (documents are in optimal relevance order)
- **0.0** = no relevant documents
- Accounts for graded relevance and ranking position
- NDCG@k evaluates only the top-k positions

### Advantages
- Handles graded relevance (not just binary)
- Position-sensitive with logarithmic discount
- Industry-standard metric for search ranking

### Limitations
- Requires relevance labels (ideally graded, not just binary)
- Logarithmic discount may not match actual user behavior
- Normalized score can mask absolute quality differences

---

# Tier 2: Generation Metrics

Generation metrics evaluate the quality of the generated answer -- is it relevant, faithful to the retrieved context, properly grounded, and free of hallucinations?

---

## Answer Relevance

### Problem
The generated answer should actually address what the query asked. An answer that is well-written but off-topic is useless.

### Intuition
Compare the vocabulary of the query and the answer. If the answer shares significant content words with the query, it is likely addressing the right topic.

### How It Works
1. Extract content words (stopwords removed) from both query and answer.
2. Compute unigram Jaccard overlap (shared words / all words).
3. Compute bigram Jaccard overlap (shared 2-word phrases / all 2-word phrases).
4. Combine with a weighted score: 0.7 * unigram + 0.3 * bigram.

### Formula

```
Answer Relevance = 0.7 * Jaccard(query_unigrams, answer_unigrams)
                 + 0.3 * Jaccard(query_bigrams, answer_bigrams)

Where:
  Jaccard(A, B) = |A INTERSECT B| / |A UNION B|
```

### Interpretation
- Does the answer address what the query asked?
- Higher scores indicate better topical alignment between query and answer

### Advantages
- Fast and deterministic
- Bigram overlap captures phrase-level relevance, not just individual words

### Limitations
- Vocabulary-based, so misses semantic relevance via paraphrasing
- Short queries or generic answers may produce misleading scores

---

## Faithfulness

### Problem
The most critical requirement for a RAG answer is that every claim must be supported by the retrieved context. Claims not grounded in the context are potential hallucinations.

### Intuition
Split the answer into sentences (treating each as a "claim"). For each claim, check if enough of its content words appear in the combined context. If a claim shares less than 50% of its content words with the context, it is flagged as unsupported.

### How It Works
1. Split the generated answer into sentences (claims).
2. For each claim, extract content words and compute the overlap ratio with the combined context content words.
3. A claim is "supported" if overlap >= 0.5 (50% of claim words found in context).
4. Faithfulness score = fraction of supported claims.

### Formula

```
                        Number of Supported Claims
Faithfulness = ------------------------------------------
                        Total Number of Claims

A claim is supported if:
  overlap_ratio(claim_tokens, context_tokens) >= 0.5

                    |claim_tokens INTERSECT context_tokens|
overlap_ratio = -------------------------------------------
                            |claim_tokens|
```

### Interpretation
- **1.0** = all claims in the answer are supported by retrieved context
- **0.0** = no claims are supported
- Per-claim details show exactly which sentences are unsupported

### Advantages
- Pinpoints exactly which claims are unsupported
- Per-claim breakdown enables targeted debugging
- Directly measures the core RAG requirement

### Limitations
- Token overlap is not true entailment (misses logical inference)
- Threshold (0.5) is a heuristic and may need tuning per domain
- Cannot detect contradictions, only missing support

---

## Groundedness

### Problem
Beyond individual claim support, we want to know if the answer as a whole is grounded in the retrieved context. This is a complementary view to faithfulness.

### Intuition
Check two things: (1) Are the entities mentioned in the answer also found in the context? (2) Are the content words in the answer also found in the context? Average both.

### How It Works
1. Extract entities (capitalized word sequences, numbers with units, formulas) from both the answer and the context.
2. Compute entity coverage: fraction of answer entities found in context entities.
3. Compute token coverage: fraction of answer content words found in context content words.
4. Groundedness = 0.5 * entity_coverage + 0.5 * token_coverage.

### Formula

```
Groundedness = 0.5 * Entity_Coverage + 0.5 * Token_Coverage

                        |Answer_Entities INTERSECT Context_Entities|
Entity_Coverage = ---------------------------------------------------
                                 |Answer_Entities|

                      |Answer_Content INTERSECT Context_Content|
Token_Coverage = ---------------------------------------------------
                              |Answer_Content|
```

### Interpretation
- Measures to what extent the answer is grounded in the provided contexts
- High entity coverage means the answer uses the same named entities as the context
- High token coverage means the answer draws vocabulary from the context

### Advantages
- Entity-level analysis catches specific factual grounding
- Complementary to faithfulness (whole-answer vs. per-claim)
- Combines two different signals for robustness

### Limitations
- Entity extraction is regex-based, not NER-model-based
- May miss entities in non-standard formats
- Does not verify correctness of entity usage, only presence

---

## Citation Correctness

### Problem
When a RAG answer includes citations like [1], [2], we need to verify that each citation actually points to a context chunk that supports the adjacent claim.

### Intuition
Split the answer around citation markers. For each citation [k], check if the claim text near it overlaps with the content of context chunk k. If the overlap is >= 40%, the citation is considered correct.

### How It Works
1. Parse the answer to find citation markers [1], [2], etc.
2. For each citation, extract the claim text preceding it.
3. Compare claim content words against the cited context chunk's content words.
4. A citation is "correct" if overlap >= 0.4.
5. Score = fraction of correct citations.

### Formula

```
                              Number of Correct Citations
Citation Correctness = -----------------------------------------
                              Total Number of Citations

A citation is correct if:
  overlap_ratio(claim_tokens, cited_context_tokens) >= 0.4
```

### Interpretation
- **1.0** = all citations correctly reference supporting context
- **0.0** = no citations are correct
- Per-citation details show which citations are verified

### Advantages
- Verifies that citations are not just present but actually meaningful
- Catches the common failure mode of fabricated citations

### Limitations
- Threshold (0.4) is a heuristic
- Cannot verify if the citation is the *best* source, only if it is *a* source
- Depends on citation markers being in a predictable format [k]

---

## Source Attribution

### Problem
Beyond individual citation correctness, we want to know if the answer properly attributes information to its sources overall. Are most sentences cited? Are the cited sources actually relevant?

### Intuition
Two dimensions:
1. **Coverage**: What fraction of answer sentences contain a citation?
2. **Accuracy**: What fraction of cited contexts are actually relevant to the answer?

### How It Works
1. Count how many answer sentences contain a citation marker [k].
2. Coverage = cited_sentences / total_sentences.
3. For each cited context index, compute Jaccard overlap with the full answer. If overlap >= 0.1, the citation is considered accurate.
4. Accuracy = accurate_citations / total_citations.
5. Score = 0.5 * coverage + 0.5 * accuracy.

### Formula

```
Source Attribution = 0.5 * Coverage + 0.5 * Accuracy

                  Sentences with citations
Coverage = -----------------------------------
                  Total sentences

                  Accurate citations
Accuracy = -----------------------------------
                  Total citations

A citation is accurate if:
  Jaccard(cited_context_tokens, answer_tokens) >= 0.1
```

### Interpretation
- Coverage measures how thoroughly the answer attributes its claims
- Accuracy measures whether cited sources are actually relevant

### Advantages
- Captures both breadth (coverage) and quality (accuracy) of attribution
- Identifies answers that cite heavily but inaccurately, or accurately but sparsely

### Limitations
- Coverage rewards citation density, which may not always be desirable
- Accuracy threshold (0.1) is very lenient
- Does not check if the most important claims are the ones cited

---

## Hallucination Detection

### Problem
Hallucinations are claims in the answer that are neither supported by the retrieved context nor consistent with the ground truth. They are the most dangerous failure mode in RAG.

### Intuition
For each claim in the answer, check two things:
1. Is the claim supported by the context? (context overlap)
2. Is the claim consistent with the ground truth? (ground-truth overlap)
If both are low (< 0.4), the claim is flagged as a potential hallucination.

### How It Works
1. Split the answer into sentences (claims).
2. For each claim, compute overlap with context content words and ground-truth content words.
3. A claim is flagged if context_overlap < 0.4 AND gt_overlap < 0.4.
4. Hallucination risk score = fraction of flagged claims.

### Formula

```
                        Number of Flagged Claims
Risk Score = ------------------------------------------
                      Total Number of Claims

A claim is flagged if:
  overlap(claim, context) < 0.4  AND  overlap(claim, ground_truth) < 0.4

Returns:
  risk_score (0 = no hallucination, 1 = all hallucinated)
  hallucination_detected (True/False)
  flagged_claims (list of suspicious claims with overlap scores)
```

### Interpretation
- **0.0** risk = no claims flagged as hallucinated
- **1.0** risk = all claims are potentially hallucinated
- Each flagged claim includes its context overlap and ground-truth overlap for debugging

### Advantages
- Dual-check (context + ground truth) reduces false positives
- Per-claim flagging enables targeted correction
- Directly addresses the most critical RAG failure mode

### Limitations
- Token overlap cannot detect subtle or contradictory hallucinations
- Depends on ground-truth availability for the second check
- If no ground truth is available, uses a neutral score (0.5), reducing detection power

---

# Tier 3: End-to-End Metrics

End-to-End metrics evaluate the full RAG pipeline by examining how the retriever and generator work together.

---

## Context Utilization

### Problem
If the retriever returns 5 chunks but the generator only uses 1, the other 4 are wasted context window space. Low utilization suggests either noisy retrieval or poor generation.

### Intuition
For each retrieved chunk, measure how much of it appears in the generated answer. Chunks with high utilization contributed to the answer; chunks with low utilization were noise.

### How It Works
1. Extract content words from the generated answer.
2. For each retrieved chunk, extract content words and compute: `utilization = |chunk_words INTERSECT answer_words| / |chunk_words|`.
3. A chunk is considered "used" if utilization >= 0.15.
4. Score = mean utilization across all chunks.

### Formula

```
                      |Chunk_tokens INTERSECT Answer_tokens|
Utilization(chunk) = -----------------------------------------
                               |Chunk_tokens|

Score = mean(Utilization) across all chunks
Chunks_used = count of chunks with utilization >= 0.15
```

### Interpretation
- High utilization means the answer draws from the retrieved context effectively
- Low utilization suggests noisy retrieval or that the generator is ignoring context
- Per-chunk utilization identifies which specific chunks contributed

### Advantages
- Diagnoses retrieval-generation alignment
- Per-chunk granularity
- Helps optimize the retriever (remove low-utilization patterns)

### Limitations
- Low utilization may be acceptable if the chunk is a backup source
- Token overlap may overcount common words
- Does not measure whether utilization improved answer quality

---

## Answer Correctness

### Problem
Ultimately, does the generated answer match the ground-truth answer? This is the bottom-line metric for the entire RAG pipeline.

### Intuition
Compare the generated answer to the ground truth using multiple similarity measures: token-level F1, Jaccard similarity, and entity overlap. Combine them with weights.

### How It Works
1. Extract content tokens from both generated and ground-truth answers.
2. Compute token-level precision, recall, and F1 using Counter intersection.
3. Compute Jaccard similarity on content token sets.
4. Extract entities from both and compute entity Jaccard overlap.
5. Composite score = 0.5 * F1 + 0.3 * Jaccard + 0.2 * Entity_Overlap.

### Formula

```
                 Common_tokens
Precision = -----------------------
             Generated_token_count

                 Common_tokens
Recall = -----------------------
          Ground_truth_token_count

         2 * Precision * Recall
F1 = ---------------------------
         Precision + Recall

Jaccard = |Gen_set INTERSECT GT_set| / |Gen_set UNION GT_set|

Entity_Overlap = Jaccard(Gen_entities, GT_entities)

Answer Correctness = 0.5 * F1 + 0.3 * Jaccard + 0.2 * Entity_Overlap
```

### Interpretation
- Composite score captures multiple dimensions of correctness
- F1 accounts for both precision (not saying wrong things) and recall (covering key information)
- Entity overlap catches factual accuracy on named entities and quantities

### Advantages
- Multi-dimensional (F1 + Jaccard + entities) reduces bias from any single measure
- Weighted combination is configurable
- Provides breakdown for debugging (which component is failing?)

### Limitations
- Token-based comparison misses semantic equivalence
- Entity extraction is regex-based
- Short ground-truth answers (e.g., a single word MCQ option) may produce volatile scores

---

## Chunk Evaluation

### Problem
Not all chunks are created equal. We need to assess each chunk's individual quality to diagnose retrieval problems.

### Intuition
For each chunk, measure three things:
1. **Relevance to query**: Does this chunk address the user's question?
2. **Information density**: Is this chunk information-rich or full of filler?
3. **Redundancy**: Does this chunk duplicate another chunk?

### How It Works
1. Relevance: Jaccard similarity between chunk content words and query content words.
2. Information density: unique content words / total words in the chunk.
3. Redundancy: maximum Jaccard overlap between this chunk and any other chunk.

### Formula

```
Relevance(chunk) = Jaccard(query_content, chunk_content)

                      |unique_content_words|
Info_Density(chunk) = -------------------------
                         |all_words|

Max_Redundancy(chunk) = max over j != i of Jaccard(chunk_i, chunk_j)
```

### Interpretation
- High relevance + high density + low redundancy = ideal chunk
- Low relevance chunks are noise from the retriever
- High redundancy means multiple chunks carry the same information (wasteful)

### Advantages
- Per-chunk diagnosis enables targeted retrieval improvement
- Identifies redundancy (a common chunking strategy failure)
- Combines multiple quality dimensions

### Limitations
- Vocabulary-based, not semantic
- Information density is a rough proxy
- Does not assess factual accuracy of chunk content

---

## Latency Tracking

### Problem
RAG pipelines have multiple stages (retrieval, generation, evaluation), and each contributes to total latency. Slow pipelines degrade user experience.

### Intuition
Measure the wall-clock time of each pipeline component. Supports both decorator-style tracking (wrap a function) and manual start/stop tracking.

### How It Works
- **Decorator**: Wrap a function with `@EndToEndMetrics.latency_tracker` to automatically measure execution time.
- **Manual**: Call `measure_latency("label")` to get a timer with `start()` and `stop()` methods.

### Advantages
- Simple and zero-overhead measurement
- Supports both decorator and manual styles
- Essential for production monitoring

### Limitations
- Measures wall-clock time, not CPU time
- Does not account for network latency separately
- Single-request latency, not throughput

---

## Cost Tracking

### Problem
RAG pipelines that use LLMs for generation incur per-token costs. Understanding cost per query is essential for budgeting and optimization.

### Intuition
Given the number of input and output tokens and the model name, estimate the dollar cost based on published per-token pricing.

### How It Works
1. Look up per-1K-token pricing for the specified model.
2. Input cost = (input_tokens / 1000) * input_price.
3. Output cost = (output_tokens / 1000) * output_price.
4. Total cost = input_cost + output_cost.

### Supported Models and Approximate Pricing (per 1K tokens, USD, mid-2025)

```
Model                 Input $/1K    Output $/1K
-----                 ----------    -----------
gpt-4                 0.03000       0.06000
gpt-4-turbo           0.01000       0.03000
gpt-4o                0.00500       0.01500
gpt-3.5-turbo         0.00050       0.00150
claude-3-opus          0.01500       0.07500
claude-3-sonnet        0.00300       0.01500
claude-3-haiku         0.00025       0.00125
claude-3.5-sonnet      0.00300       0.01500
```

### Advantages
- Enables cost-aware model selection
- Supports budget estimation before deployment
- Covers major model providers

### Limitations
- Pricing is approximate and changes over time
- Does not account for batch discounts or enterprise pricing
- Only covers token costs, not infrastructure costs

---

# Quality Comparison: Good vs. Hallucinated Answers

A critical validation step is comparing metric scores between good and hallucinated answers. If the metrics are working correctly, good answers should consistently outscore hallucinated ones.

### Expected Behavior

| Metric | Good Answers | Hallucinated Answers | Direction |
|---|---|---|---|
| Faithfulness | Higher | Lower | Good > Halluc |
| Groundedness | Higher | Lower | Good > Halluc |
| Hallucination Risk | Lower | Higher | Good < Halluc |
| Answer Correctness | Higher | Lower | Good > Halluc |
| Citation Correctness | Higher | Lower | Good > Halluc |
| Context Utilization | Higher | Lower | Good > Halluc |

Good answers consistently score higher on faithfulness, groundedness, and correctness, while hallucinated answers show higher hallucination risk -- exactly what the metrics should detect.

---

# RAG Evaluation Framework Comparison

Five major frameworks exist for RAG evaluation in production. Each takes a different approach and has distinct strengths.

## Summary Table

```
Framework      # Metrics  Approach
-------------- ---------- ----------------------------------------
RAGAS                   6  LLM-as-judge with structured decomposition
DeepEval                7  LLM-as-judge with pytest integration
TruLens                 5  Feedback functions with LLM or embedding models
LangSmith               4  Human + LLM annotation platform with tracing
Phoenix (Arize)         3  Observability-first with embedding analysis
```

---

## RAGAS

- **URL**: https://github.com/explodinggradients/ragas
- **Approach**: LLM-as-judge with structured decomposition
- **Key Metrics**: Faithfulness, Answer Relevance, Context Precision, Context Recall, Context Utilization, Answer Correctness

### Strengths
- Strong theoretical grounding in information retrieval
- Decomposes metrics into verifiable sub-questions
- Active open-source community and frequent updates

### Limitations
- Requires LLM calls (cost + latency)
- Faithfulness can be noisy for long answers

---

## DeepEval

- **URL**: https://github.com/confident-ai/deepeval
- **Approach**: LLM-as-judge with pytest integration
- **Key Metrics**: Faithfulness, Answer Relevancy, Contextual Precision, Contextual Recall, Hallucination, Bias, Toxicity

### Strengths
- pytest-style test runner for CI/CD integration
- Built-in bias and toxicity checks
- Supports custom metric definitions

### Limitations
- Heavier dependency footprint
- Some metrics closely mirror RAGAS

---

## TruLens

- **URL**: https://github.com/truera/trulens
- **Approach**: Feedback functions with LLM or embedding models
- **Key Metrics**: Groundedness, Answer Relevance, Context Relevance, Comprehensiveness, Harmful/Controversial content

### Strengths
- Excellent dashboard for tracking experiments over time
- Supports multiple LLM providers as evaluators
- Traces full chain-of-thought for debugging

### Limitations
- Dashboard adds operational complexity
- Tightly coupled to LangChain/LlamaIndex initially

---

## LangSmith

- **URL**: https://smith.langchain.com/
- **Approach**: Human + LLM annotation platform with tracing
- **Key Metrics**: Correctness, Helpfulness, Harmlessness, Custom evaluators

### Strengths
- Deep LangChain integration with automatic tracing
- Supports human-in-the-loop evaluation workflows
- Dataset management and versioning built in

### Limitations
- Primarily designed for LangChain ecosystem
- SaaS dependency for full feature set

---

## Phoenix (Arize)

- **URL**: https://github.com/Arize-ai/phoenix
- **Approach**: Observability-first with embedding analysis
- **Key Metrics**: Retrieval metrics (MRR, NDCG, Precision@k), LLM Evals (Hallucination, QA, Toxicity), Embedding drift

### Strengths
- Strong embedding visualization and drift detection
- Open-source with notebook-friendly interface
- Good for production monitoring beyond evaluation

### Limitations
- Evaluation is secondary to observability focus
- Fewer RAG-specific decomposed metrics

---

## Our Heuristic Approach (This Chapter)

This chapter implements all core RAG metrics using keyword overlap, entity matching, and statistical measures -- no LLM calls needed.

### Advantages
- Zero cost -- runs on standard library only
- Deterministic -- same inputs always produce same outputs
- Fast -- evaluates thousands of examples per second
- Educational -- makes the metric logic transparent

### Trade-offs
- Less semantically rich than LLM-based evaluation
- Cannot detect subtle paraphrasing or logical entailment
- Entity extraction is regex-based, not NER-model-based

### Recommendation
Use heuristic metrics for rapid iteration and CI/CD gates, then validate with LLM-based frameworks (RAGAS, DeepEval) for release decisions and deeper analysis.

---

# Why Use LangGraph, Langfuse & Tracing for RAG?

**LangGraph**: Models the RAG pipeline (retrieve -> generate -> evaluate) as a state graph. Each node is a step you can test, swap, or retry independently. Unlike a linear chain, LangGraph lets you add conditional routing (e.g., re-retrieve if context score is low) and parallel branches without rewriting the pipeline.

**Langfuse**: Gives you a production dashboard where every RAG query becomes a trace with nested spans (retrieval, generation, evaluation). You attach scores to each span, so you can filter by low-faithfulness queries and debug exactly which step failed. This is critical because RAG failures are often silent -- the LLM returns a confident but wrong answer, and without per-query metrics you never notice.

**Tracing**: Captures latency, token usage, and retrieval quality per request. Without it, you only have aggregate accuracy. With it, you can find the 5% of queries that take 10x longer or retrieve irrelevant context, and fix them specifically.

---

# Summary

This chapter demonstrated 17 RAG evaluation metrics across three tiers:

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

- Always evaluate retrieval and generation **separately** -- a good generator cannot save a bad retriever
- Use **multiple metrics** to form a balanced scorecard, never rely on a single number
- Include **hallucinated examples** in your test set to validate that metrics detect failures
- Run heuristic metrics in **CI/CD** for speed; LLM-based metrics for **release gates**
- Track **per-query** metrics, not just aggregates -- aggregate accuracy can mask systematic failures
- Monitor **latency and cost** alongside quality metrics in production
- Use **per-chunk evaluation** to diagnose retrieval problems (irrelevant chunks, redundancy)
- Compare **good vs. bad examples** to validate that your metric suite discriminates correctly

## Common Mistakes

- Relying on a single metric (e.g., only faithfulness) while ignoring others (e.g., relevance)
- Evaluating generation without evaluating retrieval -- the answer quality ceiling is set by retrieval quality
- Using only aggregate scores without examining per-query breakdowns
- Not including hallucinated/adversarial examples in the evaluation dataset
- Ignoring latency and cost as evaluation dimensions
- Assuming high faithfulness means high correctness (an answer can be faithful to bad context)
- Using LLM-based evaluation in tight development loops where speed matters (use heuristics instead)
- Not validating that metrics actually discriminate between good and bad answers

## Interview Questions

1. **What are the three tiers of RAG evaluation?** Retrieval, Generation, and End-to-End. Each tier evaluates a different component of the pipeline.

2. **What is the difference between faithfulness and groundedness?** Faithfulness checks per-claim support (is each sentence backed by context?). Groundedness checks overall grounding through entity and token coverage. They are complementary views.

3. **Why is context precision more useful than hit rate?** Hit rate is binary (yes/no), while context precision accounts for the ranking order of relevant documents. A retriever with Hit Rate=1 may still bury the relevant doc at position 10.

4. **How would you detect hallucinations in a RAG pipeline?** Check each answer claim against both the retrieved context and the ground truth. Claims with low overlap on both are potential hallucinations. Use faithfulness + hallucination detection together.

5. **When would you use heuristic metrics vs. LLM-based evaluation?** Heuristic metrics for CI/CD, rapid iteration, and development. LLM-based (RAGAS, DeepEval) for release decisions, deeper semantic analysis, and cases where paraphrasing is common.

6. **What does NDCG measure that MRR does not?** NDCG accounts for graded relevance and the positions of all relevant documents. MRR only considers the first relevant document.

7. **How do you evaluate citation correctness?** Parse citation markers from the answer, extract the claim near each citation, and verify that the cited context chunk supports that claim through content overlap.

8. **What is context utilization and why does it matter?** Context utilization measures how much of the retrieved context is actually used in the answer. Low utilization suggests noisy retrieval (wasted context window) or poor generation (ignoring provided context).

9. **Name three strengths and limitations of RAGAS.** Strengths: theoretical grounding, structured decomposition, active community. Limitations: requires LLM calls (cost/latency), faithfulness can be noisy for long answers.

10. **How would you build a balanced RAG evaluation scorecard?** Include at least one metric from each tier: retrieval (NDCG or context precision), generation (faithfulness + hallucination detection), and end-to-end (answer correctness + latency). Compare against both good and bad examples to validate discrimination.
