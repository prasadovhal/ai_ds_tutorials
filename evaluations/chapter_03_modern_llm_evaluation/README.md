# Chapter 3 - Modern LLM Evaluation: 17 Dimensions

## Overview

This chapter implements heuristic/rule-based evaluators for **17 evaluation dimensions** used in modern LLM assessment. All evaluators run without external models or API calls, using only the Python standard library.

## Dimensions Covered

| # | Dimension | Core Question |
|---|-----------|---------------|
| 1 | Correctness | Is the answer factually correct? |
| 2 | Relevance | Does the response address the question asked? |
| 3 | Helpfulness | Is the response useful to the user? |
| 4 | Completeness | Does it cover all aspects of the question? |
| 5 | Consistency | Does the model give consistent answers? |
| 6 | Hallucination | Did the model fabricate information? |
| 7 | Faithfulness | Is the response faithful to the source? |
| 8 | Groundedness | Can every claim be traced to the context? |
| 9 | Instruction Following | Did the model follow the instructions? |
| 10 | Fluency | Is the language natural and grammatical? |
| 11 | Coherence | Does the response flow logically? |
| 12 | Safety | Is the response free from harmful content? |
| 13 | Toxicity | Is it free from toxic language? |
| 14 | Bias | Is the response fair and unbiased? |
| 15 | Creativity | Does it use creative elements where appropriate? |
| 16 | Readability | How easy is it to understand? |
| 17 | Reasoning Quality | Does it show sound logical reasoning? |

## Files

- **main.py** - Entry point that demonstrates all 17 dimensions with explanations, sample evaluations, advantages/limitations, a summary table, and interview questions.
- **evaluator.py** - All 17 evaluator classes plus a `MultiDimensionEvaluator` orchestrator.
- **dataset.py** - Data loading utilities for sample data, wiki contexts, and simulated LLM responses.
- **sample_data.json** - Curated good/bad LLM responses for demonstration.
- **requirements.txt** - Dependencies (standard library only).

## Usage

```bash
cd chapter_03_modern_llm_evaluation
python main.py
```

No external packages are required.

## Key Concepts

- **Heuristic evaluation** serves as a fast baseline; production systems use LLM-as-Judge (Chapter 4).
- **Hallucination vs Faithfulness vs Groundedness**: three related but distinct dimensions measuring source fidelity.
- **Multi-dimensional evaluation**: no single metric captures LLM output quality.
