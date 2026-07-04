# Chapter 5 - RAG Evaluation

Comprehensive evaluation of Retrieval-Augmented Generation (RAG) pipelines using heuristic metrics that run without external LLM calls or third-party libraries.

## Overview

This chapter implements **17 RAG evaluation metrics** across three tiers:

### Retrieval Metrics
| Metric | Description |
|---|---|
| Context Precision | Are relevant documents ranked above irrelevant ones? (Average Precision) |
| Context Recall | Do retrieved documents cover the ground-truth information? |
| Context Relevance | How topically related is each chunk to the query? |
| Hit Rate | Was at least one relevant document retrieved? |
| MRR | How high is the first relevant document ranked? |
| NDCG | Overall ranking quality with graded relevance and position discount |

### Generation Metrics
| Metric | Description |
|---|---|
| Answer Relevance | Does the generated answer address the query? |
| Faithfulness | Is every claim in the answer supported by retrieved context? |
| Groundedness | Is the answer grounded via entity and content overlap? |
| Citation Correctness | Do inline citations point to the correct source passages? |
| Source Attribution | Are claims properly attributed with adequate coverage? |
| Hallucination Detection | Are there fabricated or unsupported claims in the answer? |

### End-to-End Metrics
| Metric | Description |
|---|---|
| Context Utilization | How much of the retrieved context is actually used? |
| Answer Correctness | Does the answer match the ground truth (F1, Jaccard, entity overlap)? |
| Chunk Evaluation | Per-chunk quality: relevance, density, redundancy |
| Latency Tracking | Pipeline execution time measurement |
| Cost Tracking | Estimated dollar cost per model and token count |

## Files

| File | Description |
|---|---|
| `dataset.py` | Data loading, simulated RAG pipeline, extraction utilities |
| `sample_data.json` | 10 curated RAG examples with varied quality labels |
| `evaluator.py` | All metric implementations (RetrievalMetrics, GenerationMetrics, EndToEndMetrics, RAGEvaluationPipeline) |
| `main.py` | Entry point demonstrating every metric with sample data |
| `requirements.txt` | Dependencies (standard library only; optional frameworks listed) |

## Quick Start

```bash
cd chapter_05_rag_evaluation
python main.py
```

No installation required -- runs on the Python standard library only.

## Approach

All metrics use **heuristic implementations** (keyword overlap, entity matching, statistical measures) rather than LLM-as-judge. This provides:

- **Zero cost** -- no API calls needed
- **Deterministic** -- same inputs always produce same outputs
- **Fast** -- evaluates thousands of examples per second
- **Transparent** -- metric logic is readable and debuggable

For production use, complement these with LLM-based frameworks (RAGAS, DeepEval, TruLens) for deeper semantic analysis.

## Framework Comparison

The demo includes a conceptual comparison of five popular RAG evaluation frameworks:

1. **RAGAS** -- LLM-as-judge with structured decomposition
2. **DeepEval** -- pytest-style LLM evaluation with CI/CD integration
3. **TruLens** -- Feedback functions with experiment tracking dashboard
4. **LangSmith** -- Human + LLM annotation platform with tracing
5. **Phoenix (Arize)** -- Observability-first with embedding analysis
