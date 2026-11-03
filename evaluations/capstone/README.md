# Capstone: Production-Grade Evaluation Platform

This capstone project ties together all concepts from the course into a single, end-to-end evaluation platform for a RAG-based multiple-choice question answering system.

## What It Does

1. **Dataset Management** - Loads train data, creates stratified golden sets, generates synthetic questions (Ollama or template fallback), versions datasets with checksums.
2. **RAG Pipeline** - Builds a TF-IDF retriever (with optional FAISS), retrieves relevant passages, and generates answers using Ollama (or keyword-overlap heuristic).
3. **Evaluation Suite** - Measures accuracy, retrieval quality (precision/recall), generation quality (faithfulness/relevance), latency (P50/P95), and LLM-as-judge scoring.
4. **Regression Testing** - Compares v1 vs v2 results, flags regressions beyond a threshold, and enforces quality gates (accuracy, latency, judge score).
5. **Dashboard & Reporting** - Renders an ASCII dashboard and saves a full JSON report.

## How to Run

```bash
cd D:/Study/Git_repo/evaluations/capstone
python main.py
```

### Requirements

- Python 3.8+
- pandas, scikit-learn (recommended)
- Optional: faiss-cpu, requests (for Ollama integration)

All external libraries are wrapped in try/except with graceful fallbacks.

## Project Structure

| File                 | Description                              |
|----------------------|------------------------------------------|
| `main.py`            | Entry point - orchestrates full pipeline |
| `dataset_manager.py` | Data loading, sampling, versioning       |
| `rag_pipeline.py`    | Retrieval and answer generation          |
| `evaluator.py`       | All evaluation metrics                   |
| `regression.py`      | Version comparison and quality gates     |
| `dashboard.py`       | ASCII dashboard and JSON reporting       |

## Output

- Console: step-by-step progress + ASCII dashboard
- File: `capstone_report.json` with all metrics and metadata
