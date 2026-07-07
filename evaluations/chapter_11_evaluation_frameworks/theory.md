# Chapter 11: Evaluation Frameworks

## Overview

This chapter provides a deep dive into 10 major LLM evaluation frameworks, each with a distinct philosophy, architecture, and ideal use case. Rather than treating evaluation as a monolithic problem, the industry has produced specialized tools that approach it from different angles: unit-test style metrics, component RAG analysis, run-based tracing, config-driven assertions, feedback loops, task/solver/scorer patterns, drift detection, registry-based eval specs, and end-to-end quality monitoring.

The goal is to understand not just what each framework does, but *how* it thinks about evaluation, so you can choose the right tool (or combination of tools) for your production system.

**Frameworks covered (10 total):**

1. DeepEval
2. RAGAS
3. LangSmith
4. Phoenix (Arize)
5. OpenAI Evals
6. Promptfoo
7. TruLens
8. Inspect AI
9. Evidently AI
10. Maxim AI

---

## 1. DeepEval

### What It Does

Unit-test style LLM evaluation with metric classes and `measure()` methods. DeepEval treats evaluation like software testing: you define test cases, attach metrics, and each metric produces a score with a pass/fail threshold.

### Key Concepts

- **Metric Classes**: Each evaluation dimension (faithfulness, answer relevancy, hallucination) is a separate class inheriting from a base `DeepEvalMetric`.
- **measure() Method**: Every metric exposes a `measure(test_case)` method that computes a score and a human-readable reason.
- **Threshold-Based Pass/Fail**: Each metric has a configurable threshold. A score above the threshold means the test case passes for that metric.
- **Test Case Pattern**: Evaluation data is structured as test cases with fields like `question`, `answer`, `contexts`, `actual_output`.

### Architecture

```
DeepEvalMetric (base)
  |-- FaithfulnessMetric     (threshold=0.7)
  |-- AnswerRelevancyMetric  (threshold=0.7)
  |-- HallucinationMetric    (threshold=0.5)

DeepEvalStyleEvaluator
  |-- metrics: list of DeepEvalMetric
  |-- evaluate(test_cases) -> per-case results with score, passed, reason
```

**Core metrics implemented:**

| Metric | What It Measures | Default Threshold |
|--------|-----------------|-------------------|
| Faithfulness | Whether the answer is grounded in the provided context | 0.7 |
| Answer Relevancy | How relevant the answer is to the question | 0.7 |
| Hallucination | Content not supported by context (lower is better) | 0.5 |

### Output Format

For each test case, DeepEval produces:
- **ID** of the test case
- For each metric: **score** (0-1), **passed** (boolean), **reason** (explanation string)
- Summary: average score and pass count across all test cases per metric

### Strengths

- Familiar unit-test paradigm for developers
- Easy to integrate into CI/CD pipelines
- Clear pass/fail verdicts for each metric
- Extensible metric system (create custom metrics by subclassing)
- Purpose-built for RAG evaluation with standard metrics

### Weaknesses

- Threshold selection is subjective and domain-dependent
- Pass/fail binary can hide nuance in borderline cases
- Requires well-structured test cases with context fields

### Best For

- RAG evaluation and custom evaluation pipelines
- Teams that want evaluation to feel like unit testing
- CI/CD integration where pass/fail gates are needed

---

## 2. RAGAS

### What It Does

Component RAG metrics: faithfulness, answer relevancy, context precision, and context recall. RAGAS breaks RAG evaluation into its constituent parts, measuring both the retrieval and generation stages independently.

### Key Concepts

- **Component Metrics**: Each aspect of RAG is evaluated separately rather than as a single score.
- **Faithfulness**: Measures whether the generated answer is grounded in the retrieved contexts (fraction of answer content found in context).
- **Answer Relevancy**: Measures how relevant the answer is to the original question.
- **Context Precision**: How relevant each retrieved context chunk is to the question (averaged across chunks).
- **Context Recall**: How much of the reference answer's information is covered by the retrieved contexts.

### Architecture

```
RAGASStyleEvaluator
  |-- faithfulness(question, answer, contexts) -> float
  |-- answer_relevancy(question, answer, contexts) -> float
  |-- context_precision(question, contexts) -> float
  |-- context_recall(answer, reference, contexts) -> float
  |-- evaluate(dataset) -> per-example scores for all 4 metrics
```

### Output Format

Per-example tabular scores:

```
ID         Faith   Relev  CtxPre  CtxRec
---------- ------- ------- ------- -------
rag_001      0.95    0.92    0.90    0.85
rag_002      0.70    0.90    0.85    0.80
...
```

Plus aggregate means across all examples for each metric.

### How Each Metric Works

| Metric | Inputs | Measures |
|--------|--------|----------|
| Faithfulness | question, answer, contexts | Fraction of answer grounded in context |
| Answer Relevancy | question, answer, contexts | Word overlap between question and answer |
| Context Precision | question, contexts | Average relevance of each context chunk to the question |
| Context Recall | answer, reference, contexts | Overlap between reference answer and contexts |

### Strengths

- Purpose-built for RAG pipeline evaluation
- Separates retrieval quality from generation quality
- Industry-standard metrics widely adopted in research
- Easy to identify which RAG component is failing

### Weaknesses

- Focused exclusively on RAG; not general-purpose
- Word-overlap proxies can miss semantic similarity
- Requires both reference answers and retrieved contexts

### Best For

- RAG pipeline development and optimization
- Diagnosing whether retrieval or generation is the bottleneck
- Benchmarking different retriever/generator combinations

---

## 3. LangSmith

### What It Does

Run-based evaluation with datasets, custom evaluators, and latency tracking. LangSmith models evaluation as a series of "runs" (LLM invocations), each of which can be scored by pluggable evaluator functions.

### Key Concepts

- **Runs**: Each LLM call is a "run" with inputs, outputs, and timing metadata.
- **Custom Evaluators**: Functions that take a run and return a score. You register evaluators by name.
- **Latency Tracking**: Every run records start/end time, giving you latency metrics alongside quality scores.
- **Dataset-Driven**: Evaluation is organized around named datasets.

### Architecture

```
LangSmithRun
  |-- run_id, inputs, outputs
  |-- start_time, end_time
  |-- latency_ms (property)

LangSmithStyleEvaluator
  |-- dataset_name
  |-- runs: list of LangSmithRun
  |-- evaluators: list of {name, func}
  |-- create_run(inputs, outputs)
  |-- add_evaluator(name, func)
  |-- evaluate_runs() -> per-run scores + latency
```

### Output Format

```
Run        Latency  Correct   Concise
---------- -------- --------- ---------
run_001     123.4ms      0.85      0.72
run_002     234.1ms      0.91      0.68
...
```

### Strengths

- Full observability: quality + performance in one view
- Flexible evaluator functions (any Python callable)
- Natural fit for LangChain applications
- Tracks latency alongside quality metrics

### Weaknesses

- Freemium pricing model (cloud-hosted features cost money)
- Tightly coupled to the LangChain ecosystem
- Custom evaluators require writing Python functions (no declarative config)

### Best For

- LangChain application development and monitoring
- Teams that need combined quality + performance tracking
- Production observability for LLM applications

---

## 4. Phoenix (Arize)

### What It Does

OpenTelemetry-based tracing with inline evaluation spans. Phoenix treats evaluation as part of the observability stack, attaching evaluation scores directly to traced spans.

### Key Concepts

- **Spans**: Every operation (LLM call, retrieval, evaluation) is a traced span with attributes and timing.
- **Span Types**: Spans are categorized (LLM, EVALUATOR, RETRIEVER, etc.) for filtering and analysis.
- **Inline Evaluations**: Evaluation scores are attached directly to spans as named evaluations with scores and labels.
- **Project-Based Organization**: Traces are grouped by project for multi-application monitoring.

### Architecture

```
PhoenixSpan
  |-- name, span_type (LLM, EVALUATOR, etc.)
  |-- start_time, end_time
  |-- attributes: dict
  |-- evaluations: dict of {name: {score, label}}

PhoenixStyleEvaluator
  |-- project_name
  |-- spans: list of PhoenixSpan
  |-- start_span(name, span_type)
  |-- evaluate_rag(dataset) -> per-item evaluations
  |-- get_trace_summary() -> project stats
```

### Output Format

```
[rag_001] faithfulness=0.95 (PASS)  relevance=0.87 (PASS)
[rag_002] faithfulness=0.70 (FAIL)  relevance=0.82 (PASS)

Trace summary:
  Project: rag_project  |  Total spans: 5
  Span types: {'EVALUATOR': 5}
```

### Strengths

- Built on OpenTelemetry standards (interoperable)
- Evaluation is part of the trace, not a separate system
- Rich visualization through the Phoenix UI
- Open-source with strong community

### Weaknesses

- Requires understanding of tracing/observability concepts
- UI-dependent for full value (not just a library)
- Heavier setup than simpler evaluation-only tools

### Best For

- Production observability for LLM applications
- Teams already using OpenTelemetry
- When you need tracing and evaluation in one system

---

## 5. OpenAI Evals

### What It Does

Registry-based evals with exact/fuzzy match and model-graded criteria. OpenAI Evals uses a registry pattern where evaluation specifications are registered by name and can be run against sample sets.

### Key Concepts

- **Eval Registry**: A dictionary mapping eval names to evaluation functions and match types.
- **Eval Specs**: Each registered eval has a function and a match type (exact, fuzzy, model-graded).
- **Sample-Based Execution**: Evals run against lists of samples, each with inputs and expected outputs.
- **Standardized Results**: Every eval returns accuracy, total count, passed count, and per-sample details.

### Architecture

```
OpenAIEvalsStyleEvaluator
  |-- registry: dict of {name: {func, match_type}}
  |-- register_eval(name, eval_func, match_type)
  |-- run_eval(eval_name, samples) -> {accuracy, total, passed, details}
```

### Output Format

```
MCQ accuracy eval:
  Accuracy: 70.0%  (7/10)
    Q0: PASS
    Q1: FAIL
    ...

RAG faithfulness eval:
  Pass rate: 80.0%  (4/5)
```

### Strengths

- Clean, standardized eval specification pattern
- Easy to add new evals to the registry
- Supports both exact match and model-graded criteria
- Open-source and well-documented

### Weaknesses

- Originally designed for OpenAI model evaluation (not general-purpose)
- Less feature-rich than dedicated RAG evaluation tools
- Registry pattern can become unwieldy with many evals

### Best For

- OpenAI model evaluation and comparison
- Standardized eval specs across teams
- Simple accuracy and pass/fail evaluations

---

## 6. Promptfoo

### What It Does

Config-driven test assertions with pass/fail results per prompt. Promptfoo treats prompt testing like integration testing, with declarative assertions that check output properties.

### Key Concepts

- **Assertions**: Declarative checks on model output (contains, not-contains, is-json, similar, max-length, min-score, llm-rubric).
- **Config-Driven**: Tests are defined with prompts, expected outputs, and assertion lists (YAML in the real tool).
- **Multiple Assertion Types**: Each assertion checks a different property of the output.
- **All-Pass Logic**: A test case passes only if ALL its assertions pass.

### Assertion Types

| Type | What It Checks |
|------|---------------|
| `contains` | Output contains a specific string |
| `not-contains` | Output does not contain a specific string |
| `is-json` | Output is valid JSON |
| `similar` | Word overlap similarity above a threshold |
| `max-length` | Output length is within a limit |
| `min-score` | Quality score meets a minimum |
| `llm-rubric` | LLM-based rubric scoring |

### Architecture

```
PromptfooAssertion
  |-- assert_type, value, threshold
  |-- check(output, context) -> {type, passed, reason}

PromptfooStyleEvaluator
  |-- test_cases: list
  |-- add_test(prompt, expected_output, assertions, context)
  |-- run_tests(model_outputs) -> per-test assertion results
```

### Output Format

```
Test 0: "What causes rain?"  [ALL PASS]
  [PASS] contains        -> Output contains 'What'
  [PASS] max-length      -> Length 89 vs max 500
  [PASS] similar         -> Similarity 0.45 vs threshold 0.3

Test 1: "How does CRISPR work?"  [SOME FAIL]
  [PASS] contains        -> Output contains 'How'
  [FAIL] similar         -> Similarity 0.22 vs threshold 0.3
```

### Strengths

- Best CI/CD integration of any framework
- Declarative assertions are easy to write and maintain
- No code needed for basic tests (YAML config)
- Clear pass/fail per assertion with reasons
- Supports regression testing prompts across versions

### Weaknesses

- Less suited for nuanced quality scoring
- Assertions are binary (pass/fail) rather than graded
- Similarity checks are basic (word overlap)

### Best For

- CI/CD integration and regression testing prompts
- Teams that prefer declarative test configuration
- Automated prompt quality gates in deployment pipelines

---

## 7. TruLens

### What It Does

Feedback functions wrapping an app to compute quality scores per record. TruLens instruments your LLM application and attaches feedback functions that automatically score every interaction.

### Key Concepts

- **Feedback Functions**: Named scoring functions that take an output and context, returning a quality score.
- **App Wrapping**: TruLens wraps your application so every call is automatically recorded and scored.
- **Records**: Each LLM interaction becomes a record with input, output, contexts, and feedback scores.
- **Leaderboard**: Aggregated statistics (mean, min, max) across all records for each feedback function.
- **Higher-is-Better Flag**: Each feedback function can specify whether higher scores are better.

### Architecture

```
TruLensFeedbackFunction
  |-- name, func, higher_is_better
  |-- __call__(*args) -> float

TruLensStyleEvaluator
  |-- app_name
  |-- feedback_functions: list
  |-- records: list
  |-- add_feedback(name, func, higher_is_better)
  |-- record(input, output, contexts) -> record dict
  |-- get_leaderboard() -> aggregate stats
```

### Output Format

```
Per-record feedback:
  [rec_001] groundedness=0.95  relevance=0.87  sentiment=0.80
  [rec_002] groundedness=0.70  relevance=0.82  sentiment=0.70

Leaderboard:
  App: RAG Pipeline v1  |  Records: 5
    groundedness     mean=0.850  min=0.70  max=0.95
    relevance        mean=0.840  min=0.78  max=0.92
    sentiment        mean=0.767  min=0.70  max=0.90
```

### Strengths

- Automatic instrumentation of LLM apps
- Feedback loops enable iterative quality improvement
- Leaderboard provides at-a-glance quality overview
- Flexible feedback function design

### Weaknesses

- Requires wrapping your application
- Feedback computation adds latency to each call
- Open-source version has fewer features than hosted

### Best For

- Iterative application quality improvement
- Monitoring quality over time with leaderboard tracking
- Teams that want automatic scoring of every LLM interaction

---

## 8. Inspect AI

### What It Does

Task/solver/scorer pattern for structured evaluations. Developed by the UK AI Safety Institute (AISI), Inspect AI separates evaluation into three clean components: what to evaluate (task/dataset), how to generate answers (solver), and how to score them (scorer).

### Key Concepts

- **Tasks**: Named evaluation tasks containing a dataset of items to evaluate.
- **Solvers**: Functions that generate outputs for each dataset item (simulating or wrapping an LLM).
- **Scorers**: Functions that score solver outputs against dataset items. Multiple scorers per task.
- **Aggregate Scores**: Automatic averaging of scorer results across all samples in a task.

### Architecture

```
InspectTask
  |-- name, dataset
  |-- solver: function(item) -> output
  |-- scorers: list of {name, func(item, output) -> score}

InspectStyleEvaluator
  |-- tasks: list of InspectTask
  |-- add_task(task)
  |-- run() -> per-task results with per-sample scores + aggregates
```

### Output Format

```
Task: mcq_science
  [0] exact_match=1.00  partial=1.00
  [1] exact_match=0.00  partial=0.50
  [2] exact_match=1.00  partial=1.00
  Aggregate: {'exact_match': 0.800, 'partial': 0.900}

Task: rag_faithfulness
  [rag_001] faithfulness=0.95  relevance=0.87
  [rag_002] faithfulness=0.70  relevance=0.82
  Aggregate: {'faithfulness': 0.840, 'relevance': 0.850}
```

### Strengths

- Clean separation of concerns (task, solver, scorer)
- Designed for rigorous AI safety benchmarks
- Supports multiple scorers per task
- Automatic aggregation of results

### Weaknesses

- More ceremony/boilerplate than simpler tools
- Primarily designed for safety research, not production monitoring
- Smaller community than other frameworks

### Best For

- AI safety research and benchmarking
- Structured evaluation with clear separation of concerns
- Running multiple scoring criteria on the same task

---

## 9. Evidently AI

### What It Does

Data drift detection and LLM output monitoring between reference and current data. Evidently applies statistical monitoring techniques to detect when your LLM's behavior changes over time.

### Key Concepts

- **Reference Data**: A baseline dataset representing expected/acceptable behavior.
- **Current Data**: Recent production data to compare against the reference.
- **Drift Detection**: Statistical comparison between reference and current distributions.
- **Drift Score**: Quantified measure of how much the current data has shifted from the reference.
- **Is-Drifted Flag**: Boolean indicator when drift exceeds a threshold (default: 0.2).

### Monitored Dimensions

| Dimension | What It Tracks |
|-----------|---------------|
| Text Length Drift | Changes in answer length distribution |
| Answer Quality Drift | Changes in answer quality scores (question-answer overlap) |

### Architecture

```
EvidentlyStyleEvaluator
  |-- reference_data, current_data
  |-- set_reference(data), set_current(data)
  |-- text_length_drift() -> drift stats
  |-- quality_drift() -> drift stats
  |-- generate_report() -> full drift report
```

### Output Format

```
Drift report:
  Reference size: 3  |  Current size: 2

  Text Length Drift:
    Reference mean: 245.3  std: 42.1
    Current mean:   198.5  std: 31.7
    Drift score:    0.191  Drifted: False

  Answer Quality Drift:
    Reference mean: 0.152  std: 0.034
    Current mean:   0.178  std: 0.021
    Drift score:    0.171  Drifted: False
```

### Strengths

- Statistical approach to monitoring LLM behavior
- Catches subtle degradation that point metrics miss
- Familiar to ML ops teams (extends existing Evidently patterns)
- Open-source with strong documentation

### Weaknesses

- Requires sufficient data volume for statistical significance
- Not an evaluation tool per se; more of a monitoring tool
- Drift detection is reactive, not preventive

### Best For

- Production monitoring and drift detection
- Detecting when model or prompt changes cause behavioral shifts
- ML ops teams extending existing monitoring to LLM outputs

---

## 10. Maxim AI

### What It Does

End-to-end quality monitoring with pluggable check functions. Maxim AI provides a pipeline-centric view where quality checks are attached to an evaluation pipeline and run against all entries.

### Key Concepts

- **Pipeline-Based**: Evaluations are organized around named pipelines (e.g., "production_rag").
- **Quality Checks**: Named functions that score individual entries on specific dimensions.
- **Pluggable Architecture**: Add any scoring function as a quality check.
- **Automatic Aggregation**: Pipeline-level aggregate scores computed from individual entry scores.

### Architecture

```
MaximAIStyleEvaluator
  |-- pipeline_name
  |-- quality_checks: list of {name, func}
  |-- add_quality_check(name, func)
  |-- evaluate(entries) -> {pipeline, results, aggregate}
```

### Output Format

```
Per-entry quality checks:
  ID          Ground  Complete   Concise
  ---------- -------- --------- ---------
  rag_001        0.95      0.87      0.35
  rag_002        0.70      0.82      0.25
  ...

Aggregate:
  groundedness     0.850
  completeness     0.840
  conciseness      0.320
```

### Strengths

- Simple, clean API for pipeline evaluation
- Enterprise SaaS with end-to-end pipeline monitoring
- Easy to add custom quality dimensions
- Automatic aggregation reduces boilerplate

### Weaknesses

- SaaS pricing model (not fully open-source)
- Less community adoption than other frameworks
- Simpler feature set compared to dedicated tools

### Best For

- Enterprise pipeline monitoring
- Teams that want simple, pluggable quality scoring
- End-to-end production quality dashboards

---

## Framework Comparison Table

```
Framework      Approach               Pricing        Best For
-------------- ---------------------- -------------- ------------------------
DeepEval       Unit-test metrics      Open-source    RAG + custom evals
RAGAS          Component RAG metrics  Open-source    RAG pipelines
LangSmith      Run-based + tracing    Freemium       LangChain apps
Phoenix        OTel tracing + evals   Open-source    Observability
OpenAI Evals   Registry-based         Open-source    OpenAI model evals
Promptfoo      Config-driven asserts  Open-source    CI/CD prompt testing
TruLens        Feedback functions     Open-source    App quality monitoring
Inspect AI     Task/solver/scorer     Open-source    AI safety research
Evidently AI   Drift + monitoring     Open-source    Production monitoring
Maxim AI       E2E quality scoring    SaaS           Enterprise pipelines
```

### Key Differentiators

- **DeepEval / RAGAS**: Purpose-built for RAG evaluation with standard metrics.
- **LangSmith / Phoenix**: Full observability (tracing + evals) for production LLM apps.
- **Promptfoo**: Best for CI/CD integration and regression testing prompts.
- **TruLens**: Feedback loops for iterative quality improvement.
- **Inspect AI**: Designed for AI safety benchmarks (UK AISI).
- **Evidently AI**: Statistical drift detection applied to LLM outputs.
- **OpenAI Evals**: Standardized eval specs, model-graded criteria.
- **Maxim AI**: Enterprise SaaS with end-to-end pipeline monitoring.

---

## Why Langfuse for Evaluation?

Langfuse bridges the gap between offline evaluation (DeepEval, RAGAS) and production monitoring (Phoenix, LangSmith). You can run your evaluation suite, send the scores to Langfuse as trace annotations, and track how metrics change across prompt versions and model updates. It also supports datasets and prompt management, so your evaluation workflow lives alongside your production traces.

---

## Choosing the Right Framework

### Decision Guide

```
                    What is your primary need?
                            |
           +----------------+----------------+
           |                |                |
     RAG Evaluation    Observability    CI/CD Testing
           |                |                |
     +-----+-----+    +----+----+       Promptfoo
     |           |     |         |
  DeepEval    RAGAS  Phoenix  LangSmith
     |                               
  (unit-test     (tracing +      
   style)         inline evals)  

                            |
           +----------------+----------------+
           |                |                |
    Quality Monitoring  Safety Research  Drift Detection
           |                |                |
     +-----+-----+    Inspect AI      Evidently AI
     |           |
  TruLens    Maxim AI
  (open)     (enterprise)
```

### When to Use Multiple Frameworks

In production, you often need a combination:

1. **Development phase**: DeepEval or RAGAS for RAG metric development
2. **Testing phase**: Promptfoo for CI/CD prompt regression tests
3. **Production phase**: Phoenix or LangSmith for tracing + observability
4. **Monitoring phase**: Evidently AI for drift detection
5. **Quality tracking**: TruLens for ongoing feedback loops

---

## Summary

- **10 frameworks** were compared, each with a distinct evaluation philosophy.
- **No single framework** covers all evaluation needs; production systems typically combine multiple tools.
- **DeepEval and RAGAS** are the go-to choices for RAG-specific evaluation.
- **LangSmith and Phoenix** excel at production observability with integrated evaluation.
- **Promptfoo** is the clear winner for CI/CD prompt testing.
- **TruLens** provides the best feedback loop pattern for iterative improvement.
- **Inspect AI** is purpose-built for AI safety benchmarks.
- **Evidently AI** brings statistical drift detection to LLM monitoring.
- **OpenAI Evals** offers a clean registry pattern for standardized evaluations.
- **Maxim AI** targets enterprise teams needing SaaS pipeline monitoring.

---

## Key Takeaways

1. Evaluation frameworks are not interchangeable -- each solves a different part of the evaluation problem.
2. The choice of framework depends on your stage (development, testing, production, monitoring).
3. Most production systems use 2-3 frameworks in combination.
4. Open-source options (DeepEval, RAGAS, Phoenix, Promptfoo, TruLens, Inspect AI, Evidently AI) cover most needs.
5. LangSmith and Maxim AI offer commercial features for enterprise teams.
6. Langfuse serves as a bridge between offline evaluation and production monitoring.

---

## Common Mistakes

1. **Using only one framework**: No single tool covers evaluation end-to-end. Combine frameworks for development, CI/CD, and production.
2. **Ignoring latency tracking**: Quality metrics alone are insufficient. LangSmith and Phoenix track latency alongside quality.
3. **Skipping drift detection**: Model quality can degrade silently. Use Evidently AI or similar tools to catch drift.
4. **Hardcoding thresholds**: Pass/fail thresholds (like DeepEval's 0.7) should be calibrated per domain, not used as defaults.
5. **Not versioning evaluations**: When prompt or model changes, re-run evaluations. Use Promptfoo or LangSmith for version-tracked eval results.
6. **Treating evaluation as a one-time activity**: Evaluation is continuous. Set up automated pipelines, not manual checks.
7. **Conflating retrieval and generation quality**: RAGAS separates these deliberately. A low faithfulness score may be a generation issue, while low context precision is a retrieval issue.

---

## Best Practices

1. **Start with RAGAS or DeepEval** for RAG evaluation during development.
2. **Add Promptfoo** for CI/CD integration and prompt regression testing.
3. **Use Phoenix or LangSmith** for production tracing and observability.
4. **Set up Evidently AI** for drift detection in production.
5. **Use TruLens feedback functions** for iterative quality improvement.
6. **Define clear metrics and thresholds** before choosing a framework.
7. **Run evaluations on golden datasets** that represent your production distribution.
8. **Track metrics across prompt and model versions** to catch regressions.
9. **Combine automated evaluation with periodic human review** for calibration.
10. **Use Langfuse** to bridge offline evaluation and production monitoring.

---

## Interview Questions

1. **Q: What is the difference between DeepEval and RAGAS?**
   A: DeepEval follows a unit-test pattern with metric classes, `measure()` methods, and pass/fail thresholds. RAGAS focuses specifically on decomposing RAG evaluation into four component metrics (faithfulness, answer relevancy, context precision, context recall). DeepEval is more general-purpose; RAGAS is RAG-specific.

2. **Q: Why would you use Promptfoo instead of DeepEval?**
   A: Promptfoo is config-driven (YAML) and designed for CI/CD integration with declarative assertions. DeepEval is code-first with Python metric classes. Use Promptfoo for regression testing prompts in deployment pipelines; use DeepEval for detailed metric analysis during development.

3. **Q: How does Phoenix differ from LangSmith?**
   A: Phoenix is built on OpenTelemetry standards and is fully open-source. LangSmith is freemium and tightly coupled to the LangChain ecosystem. Both provide tracing + evaluation, but Phoenix is more interoperable with existing observability infrastructure.

4. **Q: What is drift detection and why does it matter for LLM evaluation?**
   A: Drift detection (Evidently AI) statistically compares current production data against a reference baseline to detect behavioral shifts. It matters because LLM quality can degrade silently due to data distribution changes, prompt modifications, or model updates.

5. **Q: Explain the task/solver/scorer pattern in Inspect AI.**
   A: Inspect AI separates evaluation into three components: a Task (dataset of items), a Solver (function that generates outputs), and Scorers (functions that score outputs). This clean separation allows mixing and matching solvers and scorers independently.

6. **Q: How does TruLens' feedback function pattern work?**
   A: TruLens wraps your application and attaches feedback functions that automatically score every interaction. Each record (input/output pair) gets feedback scores, and a leaderboard aggregates statistics across all records.

7. **Q: What is the OpenAI Evals registry pattern?**
   A: OpenAI Evals uses a registry where evaluation specifications are registered by name with an evaluation function and match type. Evals are then run against sample sets, producing standardized accuracy/pass-rate results.

8. **Q: When would you use Maxim AI over open-source alternatives?**
   A: Maxim AI is an enterprise SaaS platform offering end-to-end pipeline monitoring with managed infrastructure. Use it when your organization needs enterprise support, SLA guarantees, and does not want to self-host evaluation infrastructure.

9. **Q: How would you design an evaluation pipeline using multiple frameworks?**
   A: Use RAGAS/DeepEval during development for metric design, Promptfoo in CI/CD for regression testing, Phoenix/LangSmith in production for tracing, Evidently AI for drift monitoring, and TruLens for feedback loops. Connect them through Langfuse for unified tracking.

10. **Q: What are the four RAGAS metrics and what does each measure?**
    A: Faithfulness (answer grounded in context), Answer Relevancy (answer relevant to question), Context Precision (retrieved contexts relevant to question), Context Recall (reference answer covered by contexts). Together they evaluate both retrieval and generation quality.

---

## Hands-On Exercises

1. **Exercise 1**: Run the demo (`python main.py`) and compare scores across all 10 frameworks for the same RAG dataset. Identify which frameworks agree and which disagree on quality.

2. **Exercise 2**: Add a new custom metric to the DeepEval evaluator (e.g., "conciseness" that penalizes overly long answers) and re-run the evaluation.

3. **Exercise 3**: Add a new assertion type to the Promptfoo evaluator (e.g., "starts-with" that checks if the output begins with a specific string).

4. **Exercise 4**: Create a new Inspect AI task for evaluating agent traces using the agent trace data in the sample dataset.

5. **Exercise 5**: Modify the Evidently evaluator to add a third drift dimension (e.g., vocabulary diversity drift) and test with reference vs. current data.

---

## Mini Project

**Build a Multi-Framework Evaluation Dashboard**

Create a Python script that:
1. Loads a RAG dataset (use the provided sample data)
2. Runs evaluation using all 10 framework-style evaluators
3. Collects results into a unified format
4. Generates a side-by-side comparison report showing how each framework scores the same examples
5. Identifies consensus (where frameworks agree) and disagreement (where they diverge)
6. Outputs a summary recommendation for which framework to use based on the evaluation task

This project reinforces the key lesson: different frameworks measure different things, and understanding their perspectives is essential for production evaluation design.

---

## Further Reading

- **DeepEval**: https://docs.confident-ai.com/
- **RAGAS**: https://docs.ragas.io/
- **LangSmith**: https://docs.smith.langchain.com/
- **Phoenix (Arize)**: https://docs.arize.com/phoenix
- **OpenAI Evals**: https://github.com/openai/evals
- **Promptfoo**: https://www.promptfoo.dev/docs/
- **TruLens**: https://www.trulens.org/
- **Inspect AI**: https://inspect.ai-safety-institute.org.uk/
- **Evidently AI**: https://docs.evidentlyai.com/
- **Maxim AI**: https://www.getmaxim.ai/
- **Langfuse**: https://langfuse.com/docs
