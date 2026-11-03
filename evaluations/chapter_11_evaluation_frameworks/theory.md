# Chapter 11: Evaluation Frameworks

## Overview

This chapter covers 10 major LLM evaluation frameworks, each with a distinct philosophy and ideal use case. The goal is to understand how each framework thinks about evaluation so you can choose the right tool (or combination) for your production system.

**Frameworks covered:**

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

**What it does:** Unit-test style LLM evaluation with metric classes, `measure()` methods, and configurable pass/fail thresholds per metric.

**Key concept:** Each evaluation dimension (faithfulness, relevancy, hallucination) is a separate metric class with a threshold-based pass/fail verdict.

**Strengths:**
- Familiar unit-test paradigm; easy CI/CD integration
- Clear pass/fail verdicts with extensible metric system
- Purpose-built for RAG evaluation

**Weaknesses:**
- Threshold selection is subjective and domain-dependent
- Pass/fail binary can hide nuance in borderline cases
- Requires well-structured test cases with context fields

**Best for:** RAG evaluation and CI/CD pipelines where pass/fail gates are needed.

---

## 2. RAGAS

**What it does:** Decomposes RAG evaluation into four component metrics -- faithfulness, answer relevancy, context precision, and context recall -- measuring retrieval and generation stages independently.

**Key concept:** Each RAG component is evaluated separately so you can pinpoint whether retrieval or generation is the bottleneck.

**Strengths:**
- Industry-standard RAG metrics widely adopted in research
- Separates retrieval quality from generation quality
- Easy to identify which RAG component is failing

**Weaknesses:**
- Focused exclusively on RAG; not general-purpose
- Word-overlap proxies can miss semantic similarity
- Requires both reference answers and retrieved contexts

**Best for:** RAG pipeline development, optimization, and benchmarking retriever/generator combinations.

---

## 3. LangSmith

**What it does:** Run-based evaluation where each LLM call is a "run" with inputs, outputs, timing metadata, and pluggable evaluator functions that produce quality scores.

**Key concept:** Evaluation is organized around named datasets and runs, combining quality scores with latency tracking in one view.

**Strengths:**
- Full observability: quality + performance in one view
- Flexible evaluator functions (any Python callable)
- Natural fit for LangChain applications

**Weaknesses:**
- Freemium pricing model (cloud features cost money)
- Tightly coupled to the LangChain ecosystem
- Custom evaluators require writing Python functions (no declarative config)

**Best for:** LangChain application development and production observability with combined quality + performance tracking.

---

## 4. Phoenix (Arize)

**What it does:** OpenTelemetry-based tracing where evaluation scores are attached directly to traced spans, making evaluation part of the observability stack.

**Key concept:** Every operation (LLM call, retrieval, evaluation) is a traced span with attributes, timing, and inline evaluation scores.

**Strengths:**
- Built on OpenTelemetry standards (interoperable)
- Evaluation lives inside the trace, not a separate system
- Open-source with rich visualization UI

**Weaknesses:**
- Requires understanding of tracing/observability concepts
- UI-dependent for full value
- Heavier setup than simpler evaluation-only tools

**Best for:** Production observability for LLM applications, especially teams already using OpenTelemetry.

---

## 5. OpenAI Evals

**What it does:** Registry-based evaluation where eval specs (with exact/fuzzy/model-graded match types) are registered by name and run against sample sets.

**Key concept:** A registry maps eval names to evaluation functions and match types, producing standardized accuracy/pass-rate results.

**Strengths:**
- Clean, standardized eval specification pattern
- Easy to add new evals to the registry
- Supports both exact match and model-graded criteria

**Weaknesses:**
- Originally designed for OpenAI models, not general-purpose
- Less feature-rich than dedicated RAG evaluation tools
- Registry pattern can become unwieldy with many evals

**Best for:** Standardized eval specs across teams, especially for OpenAI model evaluation and comparison.

---

## 6. Promptfoo

**What it does:** Config-driven prompt testing with declarative assertions (contains, not-contains, is-json, similar, max-length, min-score, llm-rubric) that produce pass/fail results per prompt.

**Key concept:** Tests are defined declaratively with prompts, expected outputs, and assertion lists. A test passes only if ALL assertions pass.

**Strengths:**
- Best CI/CD integration of any framework
- Declarative assertions are easy to write and maintain (YAML config)
- Supports regression testing prompts across versions

**Weaknesses:**
- Less suited for nuanced quality scoring
- Assertions are binary (pass/fail) rather than graded
- Similarity checks are basic (word overlap)

**Best for:** CI/CD integration, regression testing prompts, and automated prompt quality gates in deployment pipelines.

---

## 7. TruLens

**What it does:** Wraps your LLM application with feedback functions that automatically score every interaction, producing per-record quality scores and an aggregated leaderboard.

**Key concept:** Feedback functions are attached to the app so every call is automatically recorded and scored, enabling iterative quality improvement via a leaderboard.

**Strengths:**
- Automatic instrumentation of LLM apps
- Leaderboard provides at-a-glance quality overview
- Flexible feedback function design

**Weaknesses:**
- Requires wrapping your application
- Feedback computation adds latency to each call
- Open-source version has fewer features than hosted

**Best for:** Iterative application quality improvement and monitoring quality over time with leaderboard tracking.

---

## 8. Inspect AI

**What it does:** Developed by the UK AI Safety Institute (AISI), it separates evaluation into three components: Tasks (dataset), Solvers (answer generators), and Scorers (scoring functions).

**Key concept:** Clean separation of concerns -- what to evaluate, how to generate answers, and how to score them -- allowing independent mixing and matching.

**Strengths:**
- Clean separation of concerns (task, solver, scorer)
- Designed for rigorous AI safety benchmarks
- Supports multiple scorers per task with automatic aggregation

**Weaknesses:**
- More ceremony/boilerplate than simpler tools
- Primarily designed for safety research, not production monitoring
- Smaller community than other frameworks

**Best for:** AI safety research, structured benchmarking, and running multiple scoring criteria on the same task.

---

## 9. Evidently AI

**What it does:** Statistical drift detection that compares current production data against a reference baseline to detect when LLM behavior changes over time.

**Key concept:** Drift scores quantify how much current data has shifted from reference, with a boolean "is-drifted" flag when drift exceeds a threshold.

**Strengths:**
- Catches subtle degradation that point metrics miss
- Familiar to ML ops teams (extends existing Evidently patterns)
- Open-source with strong documentation

**Weaknesses:**
- Requires sufficient data volume for statistical significance
- More of a monitoring tool than an evaluation tool
- Drift detection is reactive, not preventive

**Best for:** Production monitoring, detecting behavioral shifts from model/prompt changes, and extending ML ops monitoring to LLM outputs.

---

## 10. Maxim AI

**What it does:** Enterprise SaaS platform providing end-to-end quality monitoring with pluggable check functions organized around named evaluation pipelines.

**Key concept:** Quality checks are attached to a pipeline and run against all entries, with automatic aggregation of pipeline-level scores.

**Strengths:**
- Simple, clean API for pipeline evaluation
- Enterprise SaaS with end-to-end monitoring
- Easy to add custom quality dimensions

**Weaknesses:**
- SaaS pricing model (not fully open-source)
- Less community adoption than other frameworks
- Simpler feature set compared to dedicated tools

**Best for:** Enterprise teams needing managed pipeline monitoring with SLA guarantees and no self-hosting.

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

## Choosing the Right Framework

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

           +----------------+----------------+
           |                |                |
    Quality Monitoring  Safety Research  Drift Detection
           |                |                |
     +-----+-----+    Inspect AI      Evidently AI
     |           |
  TruLens    Maxim AI
```

### When to Use Multiple Frameworks

1. **Development**: DeepEval or RAGAS for RAG metric development
2. **Testing**: Promptfoo for CI/CD prompt regression tests
3. **Production**: Phoenix or LangSmith for tracing + observability
4. **Monitoring**: Evidently AI for drift detection
5. **Quality tracking**: TruLens for ongoing feedback loops

---

## Why Langfuse for Evaluation?

Langfuse bridges offline evaluation (DeepEval, RAGAS) and production monitoring (Phoenix, LangSmith). Run your evaluation suite, send scores to Langfuse as trace annotations, and track metric changes across prompt versions and model updates. It also supports datasets and prompt management.

---

## Summary

- **10 frameworks** compared, each with a distinct evaluation philosophy.
- **No single framework** covers all needs; production systems typically combine multiple tools.
- **DeepEval/RAGAS**: Go-to for RAG evaluation. **LangSmith/Phoenix**: Production observability.
- **Promptfoo**: CI/CD prompt testing. **TruLens**: Feedback loops.
- **Inspect AI**: Safety benchmarks. **Evidently AI**: Drift detection.
- **OpenAI Evals**: Registry pattern. **Maxim AI**: Enterprise SaaS.

---

## Key Takeaways

1. Evaluation frameworks are not interchangeable -- each solves a different part of the problem.
2. Choice depends on your stage (development, testing, production, monitoring).
3. Most production systems use 2-3 frameworks in combination.
4. Open-source options cover most needs; LangSmith and Maxim AI offer commercial features.
5. Langfuse bridges offline evaluation and production monitoring.

---

## Common Mistakes

1. **Using only one framework**: No single tool covers evaluation end-to-end.
2. **Ignoring latency tracking**: Quality metrics alone are insufficient.
3. **Skipping drift detection**: LLM quality can degrade silently.
4. **Hardcoding thresholds**: Calibrate per domain, not defaults.
5. **Not versioning evaluations**: Re-run evaluations on prompt/model changes.
6. **Treating evaluation as one-time**: Evaluation is continuous.
7. **Conflating retrieval and generation quality**: RAGAS separates these deliberately.

---

## Best Practices

1. Start with RAGAS or DeepEval for RAG evaluation during development.
2. Add Promptfoo for CI/CD integration and prompt regression testing.
3. Use Phoenix or LangSmith for production tracing and observability.
4. Set up Evidently AI for drift detection in production.
5. Use TruLens feedback functions for iterative quality improvement.
6. Define clear metrics and thresholds before choosing a framework.
7. Run evaluations on golden datasets representing your production distribution.
8. Track metrics across prompt and model versions.
9. Combine automated evaluation with periodic human review.
10. Use Langfuse to bridge offline evaluation and production monitoring.

---

## Interview Questions

1. **Q: What is the difference between DeepEval and RAGAS?**
   A: DeepEval uses a unit-test pattern with metric classes and pass/fail thresholds; RAGAS decomposes RAG into four component metrics (faithfulness, answer relevancy, context precision, context recall). DeepEval is more general-purpose; RAGAS is RAG-specific.

2. **Q: Why would you use Promptfoo instead of DeepEval?**
   A: Promptfoo is config-driven (YAML) and designed for CI/CD with declarative assertions. DeepEval is code-first with Python metric classes. Use Promptfoo for deployment pipeline regression testing; DeepEval for detailed development analysis.

3. **Q: How does Phoenix differ from LangSmith?**
   A: Phoenix is built on OpenTelemetry and fully open-source. LangSmith is freemium and tightly coupled to LangChain. Both provide tracing + evaluation, but Phoenix is more interoperable with existing observability infrastructure.

4. **Q: What is drift detection and why does it matter?**
   A: Drift detection (Evidently AI) statistically compares current data against a reference baseline to detect behavioral shifts. It matters because LLM quality can degrade silently from data changes, prompt modifications, or model updates.

5. **Q: Explain the task/solver/scorer pattern in Inspect AI.**
   A: Task defines the dataset, Solver generates outputs, Scorers score them. This separation allows independent mixing and matching of components.

6. **Q: How does TruLens' feedback function pattern work?**
   A: TruLens wraps your app with feedback functions that auto-score every interaction. A leaderboard aggregates statistics (mean, min, max) across all records.

7. **Q: What is the OpenAI Evals registry pattern?**
   A: Eval specs are registered by name with a function and match type. Evals run against sample sets, producing standardized accuracy/pass-rate results.

8. **Q: When would you use Maxim AI over open-source alternatives?**
   A: When your organization needs enterprise SaaS with managed infrastructure, SLA guarantees, and does not want to self-host evaluation infrastructure.

9. **Q: How would you design a multi-framework evaluation pipeline?**
   A: RAGAS/DeepEval for development, Promptfoo in CI/CD, Phoenix/LangSmith for production tracing, Evidently AI for drift monitoring, TruLens for feedback loops, Langfuse for unified tracking.

10. **Q: What are the four RAGAS metrics?**
    A: Faithfulness (answer grounded in context), Answer Relevancy (answer relevant to question), Context Precision (contexts relevant to question), Context Recall (reference answer covered by contexts).

---

## Hands-On Exercises

1. Run `python main.py` and compare scores across all 10 frameworks for the same RAG dataset. Identify where frameworks agree and disagree.
2. Add a custom "conciseness" metric to the DeepEval evaluator that penalizes overly long answers.
3. Add a "starts-with" assertion type to the Promptfoo evaluator.
4. Create a new Inspect AI task for evaluating agent traces.
5. Add a vocabulary diversity drift dimension to the Evidently evaluator.

---

## Mini Project

**Build a Multi-Framework Evaluation Dashboard**

Create a Python script that:
1. Loads a RAG dataset (use the provided sample data)
2. Runs evaluation using all 10 framework-style evaluators
3. Collects results into a unified format
4. Generates a side-by-side comparison report
5. Identifies consensus and disagreement across frameworks
6. Outputs a recommendation for which framework to use based on the task

---

## Further Reading

- **DeepEval**: https://docs.confident-ai.com/
- **RAGAS**: https://docs.ragas.io/
- **LangSmith**: https://docs.smith.langchain.com/
- **Phoenix**: https://docs.arize.com/phoenix
- **OpenAI Evals**: https://github.com/openai/evals
- **Promptfoo**: https://www.promptfoo.dev/docs/
- **TruLens**: https://www.trulens.org/
- **Inspect AI**: https://inspect.ai-safety-institute.org.uk/
- **Evidently AI**: https://docs.evidentlyai.com/
- **Maxim AI**: https://www.getmaxim.ai/
- **Langfuse**: https://langfuse.com/docs
