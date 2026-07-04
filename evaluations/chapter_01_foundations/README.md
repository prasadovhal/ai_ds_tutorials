# Chapter 1: Foundations of LLM Evaluation

## Overview

This chapter teaches the foundational concepts of LLM evaluation — the "why" and "what" before we dive into the "how" in later chapters.

## Topics Covered

| # | Topic | Description |
|---|-------|-------------|
| 1 | Why Evaluation Matters | The case for systematic evaluation |
| 2 | Offline vs Online Evaluation | Pre-deployment vs post-deployment |
| 3 | Intrinsic vs Extrinsic | Task quality vs real-world impact |
| 4 | Human vs Automatic | Nuance vs scalability tradeoffs |
| 5 | Reference vs Reference-Free | With or without ground truth |
| 6 | Model-Based Evaluation | LLM-as-a-Judge preview |
| 7 | Regression Testing | Catching broken models |
| 8 | Continuous Evaluation | Monitoring over time |
| 9 | Evaluation Lifecycle | The 6 stages of evaluation |
| 10 | Evaluation Pipelines | Automation and standardization |
| 11 | Failure Analysis & Error Taxonomy | Classifying and fixing errors |
| 12 | Evaluation Dashboards | Communicating results |
| 13 | Evaluation in CI/CD | Quality gates for deployment |

## Project Structure

```
chapter_01_foundations/
├── main.py           # Run this — walks through all 13 topics
├── evaluator.py      # Core evaluation classes and logic
├── dataset.py        # Data loading and preparation
├── sample_data.json  # 10 sample questions with simulated predictions
├── requirements.txt  # No external deps (stdlib only)
└── README.md         # This file
```

## How to Run

```bash
cd chapter_01_foundations
python main.py
```

No external packages needed — Chapter 1 uses only the Python standard library.

## Data Used

- `data/train.csv` — 199 science MCQ questions with ground truth answers
- `data/test.csv` — 199 science MCQ questions (no answers)
- `sample_data.json` — 10 curated questions with 4 simulated model predictions

## Key Concepts

### Evaluation Types Matrix

```
                    Has Ground Truth?
                    YES              NO
                ┌────────────────┬────────────────┐
  Automatic     │ Reference-based│ Reference-free │
  (programmatic)│ Accuracy, F1,  │ Fluency,       │
                │ BLEU, ROUGE    │ coherence      │
                ├────────────────┼────────────────┤
  Human         │ Correctness    │ Helpfulness,   │
  (manual)      │ grading        │ preference     │
                ├────────────────┼────────────────┤
  Model-based   │ LLM-as-Judge   │ LLM-as-Judge   │
  (LLM judge)   │ with reference │ without ref    │
                └────────────────┴────────────────┘
```

### Evaluation Lifecycle

```
Dataset Prep → Inference → Metrics → Error Analysis → Regression → Report
```

## What's Next

Chapter 2: Classical NLP Metrics — Accuracy, Precision, Recall, F1, BLEU, ROUGE, BERTScore, Perplexity, and more, all implemented from scratch.
