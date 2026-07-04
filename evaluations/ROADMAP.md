# LLM Evaluation Course — Learning Roadmap

## Prerequisites
You should already know: Python, Transformers, LLMs, Prompt Engineering, Embeddings, Vector DBs, LangChain, LangGraph, RAG, Ollama, Mistral

## Roadmap: Beginner to Expert

```
Week 1-2          Week 3-4          Week 5-6          Week 7-8          Week 9-10
FOUNDATIONS       METRICS           JUDGING           SYSTEMS           MASTERY
Ch 1,2            Ch 3,4            Ch 5,6,7          Ch 8,9,10         Ch 11,12
Projects 1-2      Projects 3-4      Projects 5-6      Projects 7-8      Capstone
```

## Per-Chapter Study Guide

| Ch | Topic | Study Time | Key Skills You'll Gain |
|----|-------|-----------|----------------------|
| 1 | Foundations | 3-4 hours | Evaluation types, lifecycle, pipelines, CI/CD gates |
| 2 | Classical NLP Metrics | 5-6 hours | BLEU, ROUGE, METEOR, BERTScore, F1, perplexity — from scratch |
| 3 | Modern LLM Evaluation | 4-5 hours | Hallucination, faithfulness, safety, bias detection |
| 4 | LLM-as-a-Judge | 6-8 hours | Pointwise, pairwise, G-Eval, Elo, bias testing, rubrics |
| 5 | RAG Evaluation | 6-8 hours | FAISS, context precision/recall, faithfulness, RAGAS, DeepEval |
| 6 | Golden Dataset Engineering | 4-5 hours | Dataset creation, annotation, versioning, synthetic generation |
| 7 | Evaluation Dataset Engineering | 4-5 hours | Cohen's/Fleiss' Kappa, contamination, label noise, meta-eval |
| 8 | Agent Evaluation | 5-6 hours | LangGraph agents, tool eval, trajectory scoring, Elo ranking |
| 9 | Production Evaluation | 4-5 hours | Regression testing, canary, shadow deploy, drift, CI/CD |
| 10 | Observability | 4-5 hours | OpenTelemetry, Phoenix, LangSmith, W&B, MLflow tracing |
| 11 | Evaluation Frameworks | 5-6 hours | DeepEval, RAGAS, LangSmith, Promptfoo, Phoenix — real code |
| 12 | Research Papers | 4-5 hours | MT-Bench, G-Eval, RAGAS paper, SWE-Bench, Reflexion |

**Total chapters: ~60-70 hours**

## Projects Study Time

| Project | Topic | Time | What You Build |
|---------|-------|------|---------------|
| 1 | Simple Evaluator | 2-3 hours | Accuracy + BLEU + ROUGE evaluator |
| 2 | LLM-as-a-Judge | 3-4 hours | Pointwise + pairwise judge with Ollama |
| 3 | RAG Eval Platform | 4-5 hours | TF-IDF retriever + evaluation pipeline |
| 4 | Golden Dataset Generator | 3-4 hours | Synthetic dataset creation + validation |
| 5 | Continuous Eval System | 3-4 hours | Drift detection + alerting + trend tracking |
| 6 | Agent Eval Framework | 3-4 hours | Trace evaluation + Elo tournament |
| 7 | Eval Dashboard | 3-4 hours | ASCII dashboard with all metrics |
| 8 | CI/CD Pipeline | 3-4 hours | Quality gates + regression checking |

**Total projects: ~25-30 hours**

## Capstone: ~15-20 hours
Full production evaluation platform with RAG pipeline, LLM judging, regression testing, observability, and reporting.

## Total Course: ~100-120 hours

## State-of-the-Art Techniques (2024-2025)

| Technique | Status | Where in Course |
|-----------|--------|----------------|
| LLM-as-a-Judge | Industry standard | Ch 4, Project 2 |
| RAGAS for RAG evaluation | Widely adopted | Ch 5, Ch 11, Project 3 |
| DeepEval test suites | Growing adoption | Ch 11 |
| G-Eval (CoT scoring) | Research → production | Ch 4, Ch 12 |
| LangSmith tracing | Industry standard | Ch 10, Ch 11 |
| LangGraph agents | Rapidly growing | Ch 8 |
| Elo-based model ranking | Standard (Chatbot Arena) | Ch 4, Ch 12 |
| Position bias detection | Active research | Ch 4, Ch 12 |
| Promptfoo testing | Growing in DevOps | Ch 11 |
| Phoenix observability | Growing adoption | Ch 10, Ch 11 |
| Continuous evaluation | Industry best practice | Ch 9, Project 5 |
| Evaluation gates in CI/CD | Industry best practice | Ch 1, Ch 9, Project 8 |

## Recommended Learning Path

**If you have 1 week:** Ch 1 → Ch 2 → Ch 4 → Project 1 → Project 2

**If you have 2 weeks:** Add Ch 5 → Ch 3 → Project 3 → Ch 11

**If you have 1 month:** Full course chapters 1-12 + all 8 projects

**If you have 2 months:** Full course + capstone + experiment with all frameworks

## Tools You'll Use

| Tool | Purpose | Chapters |
|------|---------|----------|
| Ollama + Mistral | Local LLM inference + judging | Ch 3,4,5,6,8 |
| scikit-learn | Classification metrics, Kappa | Ch 1,2,6,7 |
| NLTK | BLEU, METEOR | Ch 2 |
| rouge-score | ROUGE metrics | Ch 2 |
| bert-score | Semantic similarity | Ch 2 |
| FAISS | Vector retrieval | Ch 5 |
| LangChain | Chains, evaluation | Ch 5,8,11 |
| LangGraph | Agent + RAG state graphs | Ch 5,8, Projects 3,6, Capstone |
| Langfuse | Production tracing + scoring | Ch 3,4,5,8,9,10,11, Projects 3,6, Capstone |
| RAGAS | RAG evaluation | Ch 5,11 |
| DeepEval | LLM test suites | Ch 11 |
| OpenTelemetry | Distributed tracing | Ch 10 |
| Phoenix (Arize) | LLM observability | Ch 10,11 |
| LangSmith | Tracing + evaluation | Ch 10,11 |
| MLflow | Experiment tracking | Ch 9,10 |
| W&B | Experiment tracking | Ch 10 |
| Promptfoo | Prompt testing | Ch 11 |
| matplotlib | Visualizations | Ch 1 |
| pandas | Data handling | All chapters |
