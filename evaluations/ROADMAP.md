# LLM Evaluation Course — 30-Day Learning Roadmap

## Prerequisites
You should already know: Python, Transformers, LLMs, Prompt Engineering, Embeddings, Vector DBs, LangChain, LangGraph, RAG, Ollama, Mistral

## Schedule: 30 Days, 2 Hours/Day = 60 Hours

No topics dropped. Chapters are compressed by reading `theory.md` for concepts and running `main.py` for demos. Projects are integrated alongside related chapters.

```
Week 1 (Day 1-6)     Week 2 (Day 7-12)     Week 3 (Day 13-19)    Week 4 (Day 20-25)    Week 5 (Day 26-30)
FOUNDATIONS           LLM JUDGING           RAG + DATASETS        AGENTS + PROD         MASTERY + CAPSTONE
Ch 1,2                Ch 4                  Ch 5,6,7              Ch 8,9,10             Ch 11,12
Projects 1,2          Project 2             Projects 3,4,5        Projects 6,7,8        Capstone
Ch 3                                                                                     
```

---

## Day-by-Day Plan

### Week 1: Foundations & Classical Metrics (Days 1-6)

| Day | Time | What to Do | Key Skills |
|-----|------|-----------|-----------|
| **1** | 2h | Ch 1 — Read `theory.md` (all 13 topics). Run `main.py` to see demos. | Evaluation types, offline/online, reference/reference-free, lifecycle |
| **2** | 2h | Ch 2 — Read `theory.md` metrics 1-9 (Accuracy through CIDEr). Run `main.py`, study `evaluator.py` implementations. | Accuracy, Precision, Recall, F1, Confusion Matrix, BLEU, ROUGE, METEOR, CIDEr |
| **3** | 2h | Ch 2 — Read `theory.md` metrics 10-17 (BERTScore through Calibration). Complete interview questions. | BERTScore, BLEURT, MoverScore, Exact Match, Token F1, Perplexity, Cross Entropy, Calibration |
| **4** | 2h | Ch 3 — Read `theory.md` (all 17 dimensions). Run `main.py`. Focus on hallucination vs faithfulness vs groundedness distinction. | Correctness, relevance, helpfulness, safety, toxicity, bias, reasoning quality |
| **5** | 2h | **Project 1**: Build simple evaluator. Then start `hands_on.py` exercises from Ch 1-3. | Accuracy + BLEU + ROUGE evaluator from scratch |
| **6** | 2h | **Project 2**: Build LLM-as-a-Judge framework (pointwise + pairwise). Review Ch 1-3 interview questions. | Ollama judge integration, scoring pipelines |

### Week 2: LLM-as-a-Judge Deep Dive (Days 7-12)

| Day | Time | What to Do | Key Skills |
|-----|------|-----------|-----------|
| **7** | 2h | Ch 4 — Read `theory.md` topics 1-7 (History through Rubric-Based). Run corresponding demos. | History, BLEU/ROUGE failures, prompt engineering, pointwise, pairwise, pass/fail, Likert, rubrics |
| **8** | 2h | Ch 4 — Read `theory.md` topics 8-14 (G-Eval through Reflexion). Run demos. | G-Eval, arena-style, Elo tournament, constitutional, self-eval, reflexion, multi-agent judging |
| **9** | 2h | Ch 4 — Read `theory.md` topics 15-21 (Agreement through Production Best Practices). Study bias detection. | Judge agreement, reliability, bias detection, meta-evaluation, human agreement, production checklist |
| **10** | 2h | Ch 4 — Study `evaluator.py` implementations. Run `hands_on.py`. | Build judge classes, understand prompt templates |
| **11** | 2h | Refine **Project 2** with rubrics + G-Eval + bias testing. Run Ollama integration if available. | End-to-end judge pipeline |
| **12** | 2h | Review Ch 4 interview questions. Compare all judging techniques. Write notes on when to use each. | Technique selection, trade-off analysis |

### Week 3: RAG + Dataset Engineering (Days 13-19)

| Day | Time | What to Do | Key Skills |
|-----|------|-----------|-----------|
| **13** | 2h | Ch 5 — Read `theory.md` Retrieval Metrics (6 metrics). Run retrieval demos. | Context precision, recall, relevance, hit rate, MRR, NDCG |
| **14** | 2h | Ch 5 — Read `theory.md` Generation + End-to-End Metrics (11 metrics). Run full pipeline demo. | Faithfulness, groundedness, hallucination detection, citation correctness, latency, cost |
| **15** | 2h | Ch 5 — Framework comparison (RAGAS, DeepEval, TruLens, LangSmith, Phoenix). **Project 3**: Start RAG eval platform. | Framework selection, TF-IDF retriever + evaluation pipeline |
| **16** | 2h | Complete **Project 3**. Run `hands_on.py` from Ch 5. | End-to-end RAG evaluation |
| **17** | 2h | Ch 6 — Read `theory.md` (golden datasets: types, creation, annotation, versioning, synthetic data). Run `main.py`. | Dataset types, sampling, deduplication, annotation, Cohen's Kappa, versioning, drift |
| **18** | 2h | **Project 4**: Golden dataset generator. Ch 7 — Read `theory.md` (benchmark design, contamination, label noise, Fleiss' Kappa, meta-eval). | Synthetic dataset creation, dataset quality validation |
| **19** | 2h | Ch 7 — Run `main.py` and `hands_on.py`. **Project 5**: Continuous evaluation system. | Contamination detection, inter-annotator agreement, drift detection + alerting |

### Week 4: Agents + Production + Observability (Days 20-25)

| Day | Time | What to Do | Key Skills |
|-----|------|-----------|-----------|
| **20** | 2h | Ch 8 — Read `theory.md` (task completion, goal achievement, trajectory, tool use, planning). Run demos. | Agent trace evaluation, tool correctness, planning quality |
| **21** | 2h | Ch 8 — Read `theory.md` (memory, reflection, multi-agent, coding agents, browser agents, Elo). Run `hands_on.py`. | Multi-agent eval, coding agent eval, Elo tournament |
| **22** | 2h | **Project 6**: Agent evaluation framework. Ch 9 — Read `theory.md` (regression, canary, shadow deploy). | Trace eval + Elo tournament, deployment strategies |
| **23** | 2h | Ch 9 — Read `theory.md` (drift detection, monitoring, alerting, CI/CD gates, versioning). Run `main.py`. **Project 7**: Start eval dashboard. | Production monitoring, quality gates, prompt versioning |
| **24** | 2h | Complete **Project 7**. Ch 10 — Read `theory.md` (tracing, logging, latency, tokens, cost, prompt tracking). | ASCII dashboard, observability pillars |
| **25** | 2h | Ch 10 — Read `theory.md` (response monitoring, dashboards, tool comparison). Run `main.py`. **Project 8**: CI/CD pipeline. | OpenTelemetry, Phoenix, LangSmith, W&B, MLflow, quality gates |

### Week 5: Frameworks + Research + Capstone (Days 26-30)

| Day | Time | What to Do | Key Skills |
|-----|------|-----------|-----------|
| **26** | 2h | Ch 11 — Read `theory.md` (DeepEval, RAGAS, LangSmith, Phoenix, OpenAI Evals). Run demos. | Framework APIs, when to use which |
| **27** | 2h | Ch 11 — Read `theory.md` (Promptfoo, TruLens, Inspect AI, Evidently AI, Maxim AI). Compare all 10 frameworks. | Config-driven testing, drift monitoring, framework selection matrix |
| **28** | 2h | Ch 12 — Read `theory.md` (all papers: MT-Bench, G-Eval, RAGAS, SWE-Bench, Reflexion, bias papers). Run `main.py`. | Research literacy, paper-to-practice translation |
| **29** | 2h | **Capstone** — Start: dataset management, RAG pipeline, evaluation suite. Read `capstone/README.md`, study architecture. | End-to-end platform design |
| **30** | 2h | **Capstone** — Complete: regression testing, dashboard, reporting. Run full pipeline. Final review of all interview questions. | Production-grade evaluation platform |

---

## Time Budget Summary

| Block | Days | Hours | Content |
|-------|------|-------|---------|
| Foundations & Metrics (Ch 1-3) | 1-4 | 8h | 13 foundation topics + 17 classical metrics + 17 modern dimensions |
| Projects 1-2 | 5-6 | 4h | Simple evaluator + LLM judge |
| LLM-as-a-Judge (Ch 4) | 7-12 | 12h | 21 techniques + Project 2 refinement |
| RAG + Datasets (Ch 5-7) | 13-19 | 14h | 17 RAG metrics + golden/eval datasets + Projects 3-5 |
| Agents + Production (Ch 8-10) | 20-25 | 12h | Agent eval + production + observability + Projects 6-8 |
| Mastery + Capstone (Ch 11-12) | 26-30 | 10h | 10 frameworks + 10 papers + capstone |
| **Total** | **30** | **60h** | **All 12 chapters, 8 projects, capstone** |

---

## How to Stay on Track

1. **Read `theory.md` first** — concepts, intuition, formulas, diagrams (faster than running Python to see print output)
2. **Run `main.py` second** — see metrics in action with real data
3. **Study `evaluator.py` third** — understand implementations (only when time allows)
4. **Do `hands_on.py` exercises** — skip if behind schedule, return later
5. **Interview questions** — review at end of each chapter block, not every day

## If You Fall Behind

- Ch 6+7 can be combined into 1 day (read both `theory.md`, run both `main.py`)
- Ch 11 frameworks: read comparison table first, deep-dive only into 3-4 you'll actually use
- Capstone: the 2-day allocation is tight — extend to day 31-32 if needed
- Projects: can be shortened by studying existing code rather than building from scratch

---

## Topics Covered (None Dropped)

### Part 1: Foundations (Ch 1)
Offline/online, intrinsic/extrinsic, human/automatic, reference/reference-free, model-based, regression testing, continuous evaluation, lifecycle, pipelines, error taxonomy, dashboards, CI/CD

### Part 2: Classical Metrics (Ch 2)
Accuracy, Precision, Recall, F1, Confusion Matrix, BLEU, ROUGE, METEOR, CIDEr, BERTScore, BLEURT, MoverScore, Exact Match, Token F1, Perplexity, Cross Entropy, Calibration

### Part 3: Modern LLM Evaluation (Ch 3)
Correctness, Relevance, Helpfulness, Completeness, Consistency, Hallucination, Faithfulness, Groundedness, Instruction Following, Fluency, Coherence, Safety, Toxicity, Bias, Creativity, Readability, Reasoning Quality

### Part 4: LLM-as-a-Judge (Ch 4)
History, BLEU/ROUGE failures, prompt engineering, pointwise, pairwise, pass/fail, Likert, rubric-based, G-Eval, arena-style, Elo, constitutional, self-eval, reflexion, multi-agent, agreement, reliability, bias, meta-eval, human agreement, production best practices

### Part 5: RAG Evaluation (Ch 5)
Context precision/recall/relevance, hit rate, MRR, NDCG, answer relevance, faithfulness, groundedness, citation correctness, source attribution, hallucination detection, context utilization, answer correctness, chunk eval, latency, cost, RAGAS, DeepEval, TruLens, LangSmith, Phoenix

### Part 6: Golden Dataset Engineering (Ch 6)
Dataset types, creation sources, sampling, deduplication, balancing, annotation, rubrics, inter-annotator agreement, versioning, drift, synthetic generation

### Part 7: Evaluation Dataset Engineering (Ch 7)
Benchmark design, quality checks, coverage metrics, contamination, leakage, label noise, Cohen's Kappa, Fleiss' Kappa, meta-evaluation

### Part 8: Agent Evaluation (Ch 8)
Task completion, goal achievement, planning, trajectory, tool use, memory, reflection, multi-agent, coding agents, browser agents, Elo, AgentBench, SWE-Bench, GAIA, WebArena

### Part 9: Production Evaluation (Ch 9)
Regression testing, canary testing, shadow deployment, drift detection, monitoring, alerting, CI/CD gates, prompt versioning, dataset versioning, continuous benchmarking

### Part 10: Observability (Ch 10)
Tracing, logging, latency, token usage, cost monitoring, prompt tracking, response monitoring, dashboards, OpenTelemetry, Phoenix, LangSmith, MLflow, W&B

### Part 11: Evaluation Frameworks (Ch 11)
DeepEval, RAGAS, LangSmith, Phoenix, OpenAI Evals, Promptfoo, TruLens, Inspect AI, Evidently AI, Maxim AI

### Part 12: Research Papers (Ch 12)
MT-Bench, G-Eval, RAGAS paper, SWE-Bench, ARES, AgentBench, Reflexion, calibration, bias, meta-evaluation

### Projects (1-8) + Capstone
All 8 projects + full capstone platform

---

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
