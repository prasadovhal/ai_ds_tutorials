# Evaluation Projects

Progressive projects for learning LLM evaluation techniques.

## Projects

| # | Folder | Description | Status |
|---|--------|-------------|--------|
| 1 | `01_simple_evaluator/` | Basic evaluator with accuracy, BLEU, ROUGE, confusion matrix | Ready |
| 2 | `02_llm_judge_framework/` | LLM-as-a-Judge with pairwise comparison and inter-judge agreement | Ready |
| 3 | `03_rag_eval_platform/` | RAG evaluation with TF-IDF retrieval and context/faithfulness metrics | Ready |
| 4 | `04_golden_dataset_generator/` | Golden dataset generator with synthetic question creation and validation | Ready |
| 5 | `05_benchmark_suite/` | Comprehensive benchmark suite | See below |
| 6 | `06_bias_fairness_audit/` | Bias and fairness auditing framework | See below |
| 7 | `07_human_eval_interface/` | Human evaluation interface with annotation tools | See below |
| 8 | `08_eval_dashboard/` | Interactive evaluation dashboard with visualizations | See below |

## How to Run

Each project is standalone. Navigate to the project folder and run:

```bash
python main.py
```

## Data

All projects use data from `../data/`:
- `train.csv` -- 199 STEM multiple-choice questions (id, prompt, A-E, answer)
- `wiki_stem_corpus.csv` -- Wikipedia STEM passages (used by Project 3, first 200 rows)

## Dependencies

Core: Python 3.8+, standard library only (csv, json, random, os, re, collections, hashlib)

Optional (graceful fallback if missing):
- `scikit-learn` -- TF-IDF vectorizer, confusion matrix, accuracy
- `nltk` -- BLEU score
- `rouge-score` -- ROUGE metrics
- `requests` -- Ollama/LLM API calls
