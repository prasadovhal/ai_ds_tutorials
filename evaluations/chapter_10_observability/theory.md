# Chapter 10 -- LLM Application Observability

## Overview

Observability is the practice of understanding the internal state of a system by examining its external outputs. For LLM applications, this means capturing traces, logs, latency distributions, token usage, cost breakdowns, prompt versions, and response quality signals -- all in a unified view.

Without observability, you are flying blind. A user reports "the chatbot was slow yesterday" and you have no data to investigate. A prompt change rolls out and accuracy drops, but nobody notices for days. Costs silently double because a new feature triggers longer outputs. Observability turns these invisible problems into visible, actionable signals.

This chapter covers eight core pillars of LLM observability:

1. **Distributed Tracing** -- end-to-end visibility across every step of a pipeline
2. **Structured Logging** -- rich, queryable log entries with LLM-specific metadata
3. **Latency Monitoring** -- percentile tracking to catch tail latency issues
4. **Token Usage Tracking** -- counting tokens to understand cost drivers and optimize prompts
5. **Cost Calculation** -- turning token counts into dollar amounts per model
6. **Prompt Version Tracking** -- measuring which prompt wording works best
7. **Response Quality Monitoring** -- catching accuracy drift, format errors, and confidence miscalibration
8. **Unified Dashboards** -- a single pane of glass combining all signals

---

## 1. Distributed Tracing

### Problem

An LLM pipeline has many steps: format the prompt, call the model, parse the response, evaluate correctness. When something is slow or broken, you need to know *which step* caused the issue. A single latency number per request is not enough.

### Intuition

Think of a trace like a receipt at a car repair shop. Instead of just "repair: $500", the receipt breaks down every task: "diagnose: 30 min, order part: 2 hours, install: 45 min, test: 15 min." If the total time is too long, you can immediately see that "order part" was the bottleneck.

A **trace** captures the full lifecycle of an LLM call as a tree of **spans**. Each span represents one unit of work (prompt formatting, LLM call, response parsing, etc.). Spans have parent-child relationships, forming a tree.

### How It Works

- A **trace** is identified by a unique `trace_id` and groups all spans for a single request.
- A **span** represents one step. It has:
  - `span_id` -- unique identifier
  - `trace_id` -- which trace it belongs to
  - `parent_span_id` -- which span is its parent (null for the root span)
  - `name` -- what operation this span represents (e.g., `llm.call`, `prompt.format`)
  - `start_time` / `end_time` -- when the operation started and finished
  - `duration_ms` -- how long it took
  - `status` -- OK, ERROR, IN_PROGRESS, etc.
  - `attributes` -- key-value metadata (model name, token counts, question ID, etc.)

### Key Concepts

- **Root span**: The top-level span with no parent. Represents the entire pipeline execution.
- **Child spans**: Steps within the pipeline. Each child's parent is the root or another child.
- **Span tree**: The hierarchy of spans forms a tree that shows execution flow and timing.
- **Slow traces**: Traces whose root span duration exceeds a threshold (e.g., 3000ms).

### Trace Tree Example

A typical science QA pipeline trace looks like this:

```
pipeline.run [OK] 2345.0ms
|-- prompt.format [OK] 15.0ms
|-- llm.call [OK] 2075.0ms
|-- response.parse [OK] 15.0ms
|-- evaluation.check [OK] 230.0ms
```

The tree immediately shows that `llm.call` dominates latency at 2075ms out of 2345ms total. Optimization efforts should focus there.

A slow trace example:

```
pipeline.run [OK] 5712.0ms
|-- prompt.format [OK] 20.0ms
|-- llm.call [OK] 5470.0ms
|-- response.parse [OK] 20.0ms
|-- evaluation.check [OK] 192.0ms
```

Here `llm.call` took 5470ms, pushing total latency well beyond the 3000ms threshold.

### Span Attributes

Attributes attach rich metadata to each span:

| Span | Typical Attributes |
|------|-------------------|
| `pipeline.run` | `question_id`, `pipeline_version` |
| `prompt.format` | `prompt_version`, `input_tokens` |
| `llm.call` | `model`, `input_tokens`, `output_tokens`, `temperature` |
| `response.parse` | `parsed_answer`, `confidence`, `format_ok` |
| `evaluation.check` | `correct`, `ground_truth`, `predicted` |

### When to Use

- Always in production LLM pipelines
- During development to identify bottlenecks
- For debugging slow or failed requests
- For comparing latency across pipeline versions

### Common Mistakes

- Not tracing at all -- relying on overall request latency only
- Missing child spans -- tracing the LLM call but not prompt formatting or parsing
- Not recording attributes -- traces without metadata are hard to debug
- Not setting thresholds for slow trace alerting

---

## 2. Structured LLM Logging

### Problem

Traditional application logs (`print("Query processed")`) tell you almost nothing useful for LLM debugging. You need to know: which model was used, how many tokens were consumed, what was the cost, how long did it take, which prompt version was active.

### Intuition

Structured logs attach metadata (tokens, cost, model, latency) to every event. Instead of a flat text line, each log entry is a dictionary with queryable fields. This is the difference between searching a haystack of text and querying a database.

### How It Works

Each structured log entry contains:

- **timestamp** -- when the event occurred (ISO 8601 format, UTC)
- **level** -- severity: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **component** -- which part of the system generated the log (pipeline, llm, evaluation)
- **message** -- human-readable description
- **metadata** -- key-value pairs with LLM-specific data

### Log Levels

| Level | Marker | Use |
|-------|--------|-----|
| DEBUG | `[ ]` | Verbose development details |
| INFO | `[*]` | Normal operation events |
| WARNING | `[!]` | Potential issues (slow calls, low confidence) |
| ERROR | `[X]` | Failures (incorrect predictions, API errors) |
| CRITICAL | `[!!!]` | System-breaking failures |

### Example Log Entries

```
[*] 2026-07-03T10:00:00 [pipeline] Starting science QA pipeline | question_id=0, model=gpt-4, prompt_version=v3
[*] 2026-07-03T10:00:02 [llm] LLM call completed | question_id=0, latency_ms=2075, input_tokens=245, output_tokens=38, model=gpt-4, cost_usd=0.00961
[!] 2026-07-03T10:00:08 [llm] LLM call exceeded latency threshold | question_id=1, latency_ms=5470, threshold_ms=3000, model=gpt-4
[X] 2026-07-03T10:00:08 [evaluation] Incorrect prediction detected | question_id=1, expected=A, predicted=B, confidence=0.65
```

### Key Concepts

- **Log filtering**: Query logs by level (show only errors) or component (show only LLM calls).
- **Log summary**: Count entries by level to get a quick health check (e.g., 15 INFO, 3 WARNING, 1 ERROR).
- **Error isolation**: Filter to ERROR/CRITICAL to quickly find what went wrong.
- **Warning tracking**: WARNINGs often precede failures -- slow calls may become timeouts.

### Best Practices

- Always log model name, token counts, and cost with every LLM call
- Use WARNING level for latency threshold violations
- Use ERROR level for incorrect predictions or API failures
- Include `question_id` or `request_id` in metadata so you can correlate logs with traces
- Store logs in a structured format (JSON) for querying

---

## 3. Latency Monitoring

### Problem

Average latency is misleading. If 95% of your calls take 1.5 seconds and 5% take 10 seconds, the average might be 2 seconds -- which hides the fact that 1 in 20 users has a terrible experience. You need percentile tracking.

### Intuition

Percentile tracking (P50/P95/P99) reveals tail latency issues. P50 is the median -- half your calls are faster, half are slower. P95 means 95% of calls are faster than this value. P99 catches the worst 1%.

Think of it like a restaurant: if 99 out of 100 customers get served in 10 minutes but 1 customer waits 2 hours, the "average" wait of 11 minutes hides a serious problem. P99 exposes it.

### How It Works

1. Record every latency measurement
2. Sort all measurements
3. Calculate percentiles by finding the value at a specific position in the sorted list
4. Set thresholds (e.g., P95 < 3000ms) and alert when exceeded

### Key Metrics

| Metric | What It Tells You |
|--------|-------------------|
| **P50 (median)** | Typical user experience |
| **P95** | Worst experience for most users |
| **P99** | Edge-case worst experience |
| **Mean** | Overall average (can be misleading) |
| **Min/Max** | Absolute bounds |
| **Slow calls** | Count of calls exceeding threshold |

### Latency Distribution

LLM call latencies typically follow a log-normal distribution: most calls cluster around the median, but there is a long right tail of slow calls. A histogram reveals this pattern:

```
    400-  1400ms | ######################## (12)
   1400-  2400ms | ############################## (15)
   2400-  3400ms | ############## (7)
   3400-  4400ms | ######## (4)
   4400-  5400ms | ###### (3)
   5400-  6400ms | ## (1)
```

This shape is typical: most calls are fast (under 2400ms), but a tail extends to 6000ms+.

### Threshold Alerting

Set a threshold (e.g., 3000ms) and count how many calls exceed it. In the example above, roughly 8 out of 42 calls (19%) exceeded 3000ms. These slow calls degrade user experience and may indicate:

- Model provider throttling
- Complex prompts requiring more computation
- Network issues
- Cold starts

### Common Mistakes

- Using only mean latency (hides tail issues)
- Not tracking percentiles over time (P95 drift is an early warning)
- Setting thresholds too tight (alerts fire constantly) or too loose (problems go unnoticed)
- Not correlating slow latency with specific question types or prompt versions

---

## 4. Token Usage Tracking

### Problem

Tokens are the currency of LLM APIs. Every input token and output token costs money. Without tracking, you cannot optimize prompt length, predict costs, or catch runaway usage.

### Intuition

Token counts drive cost and help optimize prompt length. By tracking input vs. output tokens per call, per model, and over time, you can:

- Identify which prompts are too verbose
- Spot unexpectedly long outputs
- Compare models on token efficiency
- Budget and forecast API costs

### How It Works

For each LLM call, record:

- **input_tokens** -- tokens in the prompt sent to the model
- **output_tokens** -- tokens in the model's response
- **total_tokens** -- input + output
- **model** -- which model was used (different models have different pricing)

### Token Estimation

When exact token counts are not available (e.g., before sending to the API), use the heuristic:

```
estimated_tokens = len(text) // 4
```

This approximation of ~4 characters per token is rough but useful for planning. In production, use `tiktoken` for exact counts.

### Key Statistics

| Metric | Description |
|--------|-------------|
| Total calls | Number of LLM invocations |
| Total input tokens | Sum of all input tokens |
| Total output tokens | Sum of all output tokens |
| Total tokens | Input + output combined |
| Avg input/call | Average prompt size |
| Avg output/call | Average response size |

### Usage by Model

Breaking down token usage by model reveals cost optimization opportunities:

```
gpt-4:          50 calls, 13,250 in / 3,150 out
gpt-3.5-turbo:  10 calls,  2,650 in /   620 out
```

If the cheaper model (gpt-3.5-turbo) achieves similar accuracy for some tasks, routing those tasks to it saves significant cost.

### Best Practices

- Track tokens per call, not just totals
- Compare input token counts across prompt versions (shorter prompts = lower cost)
- Monitor output token trends (suddenly longer outputs may indicate model behavior changes)
- Use exact token counting libraries in production (`tiktoken` for OpenAI, model-specific tokenizers for others)

---

## 5. Cost Calculation

### Problem

A single LLM call costs fractions of a cent. This seems negligible until you scale to thousands or millions of calls. Without cost tracking, budgets explode silently.

### Intuition

Per-model pricing turns token counts into dollar costs. Different models have very different pricing, and input tokens vs. output tokens are priced differently. Tracking cost per query, per model, and per time period is essential for budgeting.

### How It Works

Cost formula:

```
input_cost  = (input_tokens / 1000) * input_price_per_1k
output_cost = (output_tokens / 1000) * output_price_per_1k
total_cost  = input_cost + output_cost
```

### Model Pricing Reference

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|----------------------|
| gpt-4 | $0.0300 | $0.0600 |
| gpt-4-turbo | $0.0100 | $0.0300 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| claude-3-opus | $0.0150 | $0.0750 |
| claude-3-sonnet | $0.0030 | $0.0150 |
| claude-3-haiku | $0.00025 | $0.00125 |

### Model Cost Comparison

For 10,000 input tokens + 2,000 output tokens:

| Model | Input Cost | Output Cost | Total Cost |
|-------|-----------|-------------|------------|
| claude-3-haiku | $0.0025 | $0.0025 | $0.0050 |
| gpt-3.5-turbo | $0.0050 | $0.0030 | $0.0080 |
| claude-3-sonnet | $0.0300 | $0.0300 | $0.0600 |
| gpt-4-turbo | $0.1000 | $0.0600 | $0.1600 |
| claude-3-opus | $0.1500 | $0.1500 | $0.3000 |
| gpt-4 | $0.3000 | $0.1200 | $0.4200 |

The cheapest model (claude-3-haiku) is **84x cheaper** than the most expensive (gpt-4) for the same token volume. This is why cost tracking and model routing matter enormously at scale.

### Cost Breakdown by Model

In a typical pipeline, cost breaks down by model:

```
Total cost: $0.5980
  gpt-4:          50 calls, $0.5980 (in: $0.4275, out: $0.1734)
  gpt-3.5-turbo:  10 calls, $0.0012 (in: $0.0013, out: $0.0009)
```

Even though gpt-3.5-turbo handled 10 calls, it cost less than 1% of what gpt-4 cost for 50 calls.

### Key Concepts

- **Cost per query**: total_cost / number_of_queries -- essential for pricing your product
- **Cost by model**: identify which model is driving spend
- **Input vs output cost**: output tokens are usually more expensive (2x for GPT-4)
- **Cost projection**: multiply cost_per_query by expected volume to forecast monthly spend

### Common Mistakes

- Ignoring output token costs (they are often 2-5x more expensive than input tokens)
- Not updating pricing tables when providers change rates
- Not tracking cost per feature or endpoint (some features may be unprofitable)
- Forgetting that retries double costs

---

## 6. Prompt Version Tracking

### Problem

Changing a prompt can dramatically alter accuracy, latency, and cost. Without version tracking, you cannot tell which prompt version performs best, or worse, you cannot roll back when a change causes regression.

### Intuition

Versioned prompts let you measure which wording works best. Just like software versioning, every prompt change gets a version number. You then measure accuracy, latency, token usage, and confidence per version.

### How It Works

1. **Register** each prompt version with its template text and description
2. **Record results** for each version: whether the response was correct, confidence score, latency, and token count
3. **Compare** versions side by side on all metrics

### Prompt Version Evolution Example

| Version | Template | Description |
|---------|----------|-------------|
| v1 | `Answer the following question: {question} Choices: {choices} Answer:` | Minimal prompt, no instructions |
| v2 | `You are a science expert. Answer the following multiple choice question by selecting the best option (A, B, C, D, or E). Question: {question} {choices} Answer (letter only):` | Added role and format instruction |
| v3 | `You are an expert scientist with deep knowledge across physics, chemistry, biology, and earth sciences. Carefully read the following multiple choice question. Consider each option thoroughly before selecting the best answer. Question: {question} Options: {choices} Provide ONLY the letter (A, B, C, D, or E) of the correct answer:` | Added chain-of-thought encouragement and expertise framing |

### Version Comparison Metrics

| Version | Accuracy | Confidence | Latency | Tokens | Description |
|---------|----------|------------|---------|--------|-------------|
| v1 | 58.0% | 0.650 | 1500ms | 180 | Minimal prompt, no instructions |
| v2 | 68.0% | 0.720 | 1600ms | 240 | Added role and format instruction |
| v3 | 72.0% | 0.780 | 1700ms | 290 | Added chain-of-thought encouragement |

### Key Insights from Version Tracking

- **v1 to v2**: Adding a role ("You are a science expert") and format instruction ("letter only") boosted accuracy by 10 percentage points
- **v2 to v3**: More detailed expertise framing gained another 4 points, but at the cost of 50 more tokens per call
- **Trade-off**: Each version improvement costs more tokens (and therefore more money). Version tracking quantifies this trade-off.

### Best Practices

- Never change a prompt in production without creating a new version
- A/B test new versions on a subset of traffic before full rollout
- Track all four dimensions: accuracy, confidence, latency, and tokens
- Keep old versions registered so you can compare or roll back
- Document what changed in each version's description

---

## 7. Response Quality Monitoring

### Problem

An LLM pipeline may work correctly for weeks, then silently degrade. Model updates, prompt changes, or shifting input distributions can all cause quality drops. Without continuous monitoring, you find out from angry users instead of dashboards.

### Intuition

Track accuracy, format errors, and confidence calibration in real time. Quality monitoring treats the LLM like a production service: it has SLOs (Service Level Objectives) and triggers alerts when metrics drift.

### How It Works

For each response, record:

- **predicted** -- what the model answered
- **ground_truth** -- the correct answer (when available)
- **confidence** -- how confident the model was
- **format_ok** -- whether the response was in the expected format
- **latency_ms** -- how long the response took

### Key Quality Metrics

| Metric | Description | Why It Matters |
|--------|-------------|---------------|
| **Accuracy** | Fraction of correct predictions | Core quality signal |
| **Avg confidence** | Mean confidence score | Calibration indicator |
| **Format error rate** | Fraction of responses with wrong format | Usability issue |
| **Low confidence count** | Responses below confidence threshold | Uncertain predictions |
| **High-confidence errors** | Wrong but confident predictions | Most dangerous failure mode |

### High-Confidence Errors

The most dangerous failure mode is when the model is **wrong but confident**. These are responses where:

- The prediction is incorrect (`predicted != ground_truth`)
- The confidence is high (e.g., >= 0.80)

These are dangerous because downstream systems (or users) trust high-confidence answers. A model that says "I'm 95% sure the answer is B" when the answer is actually A will cause more harm than one that says "I'm 40% sure."

Example high-confidence errors:

```
Predicted=C, Truth=E, Confidence=0.92
Predicted=B, Truth=D, Confidence=0.85
Predicted=A, Truth=C, Confidence=0.81
```

### Quality Report Example

```
Total responses:         50
Accuracy:                72.0%
Avg confidence:          0.720
Format errors:           2 (4.0%)
Low confidence (<0.5):   3
High-confidence errors:  4
```

### Confidence Calibration

A well-calibrated model's confidence should match its accuracy:
- When it says 90% confident, it should be correct ~90% of the time
- When it says 50% confident, it should be correct ~50% of the time

Monitoring the gap between average confidence and actual accuracy reveals miscalibration. If confidence is 0.85 but accuracy is 0.60, the model is overconfident.

### Common Mistakes

- Monitoring accuracy only, ignoring confidence and format errors
- Not alerting on high-confidence errors (the most dangerous failure mode)
- Not tracking format error rates (broken outputs frustrate users)
- Waiting for user complaints instead of proactive monitoring

---

## 8. Unified Observability Dashboard

### Problem

Having traces in one tool, logs in another, costs in a spreadsheet, and accuracy in a notebook creates information silos. When something goes wrong, you waste time switching between tools instead of diagnosing the issue.

### Intuition

A single view combining latency, tokens, cost, quality, and logs prevents alert fatigue and enables rapid diagnosis. One dashboard, all signals.

### How It Works

The dashboard aggregates data from all observability components:

```
======================================================================
                    LLM OBSERVABILITY DASHBOARD
======================================================================

  --- LATENCY METRICS ------------------------------------------------
  Requests:  50
  Mean:      1850.0ms
  P50:       1620.0ms
  P95:       4200.0ms
  P99:       5800.0ms
  Slow (>3000ms): 8

  --- TOKEN USAGE ----------------------------------------------------
  Total calls:         60
  Total input tokens:  15,900
  Total output tokens: 3,770
  Avg input/call:      265.0
  Avg output/call:     62.8

  --- COST ANALYSIS --------------------------------------------------
  Total cost: $0.5992
  gpt-4: 50 calls, $0.5980
  gpt-3.5-turbo: 10 calls, $0.0012

  --- RESPONSE QUALITY -----------------------------------------------
  Accuracy:                72.0%
  Avg confidence:          0.720
  Format errors:           2 (4.0%)
  High-confidence errors:  4

  --- PROMPT VERSION COMPARISON --------------------------------------
  Version    Accuracy   Confidence   Latency    Tokens
  v1            58.0%        0.650     1500ms      180
  v2            68.0%        0.720     1600ms      240
  v3            72.0%        0.780     1700ms      290

  --- LOG SUMMARY ----------------------------------------------------
  INFO      : 24
  WARNING   :  3
  ERROR     :  1

======================================================================
  Dashboard generated: 2026-07-05 12:00:00 UTC
======================================================================
```

### Dashboard Sections

| Section | Data Source | Key Signals |
|---------|-----------|-------------|
| Latency Metrics | LatencyTracker | P50, P95, P99, slow call count |
| Token Usage | TokenCounter | Total tokens, per-call averages |
| Cost Analysis | CostCalculator | Total cost, cost by model |
| Response Quality | ResponseMonitor | Accuracy, confidence, format errors |
| Prompt Versions | PromptTracker | Per-version accuracy and cost |
| Log Summary | LLMLogger | Count by level, recent errors |

### Best Practices

- Refresh dashboards at regular intervals (every minute for real-time, hourly for batch)
- Include the timestamp of when the dashboard was generated
- Show recent errors prominently -- they are the most actionable
- Add time-series charts in production (accuracy over time, cost over time)
- Set up alerts that trigger when metrics cross thresholds

---

## 9. Observability Tools Overview

### Key Platforms for Production LLM Observability

Five major tools serve the LLM observability space, each with different strengths.

### Phoenix (Arize)

- **Focus**: Tracing and evaluation for LLM apps
- **Best for**: Teams wanting open-source observability with strong tracing
- **Strengths**: Open-source, rich tracing UI, evaluation built-in, works with any LLM
- **How it fits**: Phoenix provides a visual UI for exploring traces, evaluating responses, and tracking experiments. Being open-source, it can be self-hosted for data privacy.

### LangSmith

- **Focus**: Tracing, testing, evaluation for LangChain
- **Best for**: Teams heavily using LangChain framework
- **Strengths**: Deep LangChain integration, dataset management, online evaluation, playground
- **How it fits**: If your stack is built on LangChain/LangGraph, LangSmith gives you native tracing, prompt playground, and evaluation datasets tightly integrated with the framework.

### OpenTelemetry

- **Focus**: Vendor-neutral observability standard
- **Best for**: Enterprise teams needing vendor-neutral instrumentation
- **Strengths**: Industry standard, vendor agnostic, rich ecosystem, traces + metrics + logs
- **How it fits**: OpenTelemetry is not LLM-specific -- it is the industry standard for distributed tracing. Instrument your pipeline once with OTel, then send traces to any backend (Phoenix, Jaeger, Datadog, etc.). This avoids vendor lock-in.

### MLflow

- **Focus**: ML experiment tracking and model management
- **Best for**: Teams tracking ML experiments alongside LLM evaluation
- **Strengths**: Experiment comparison, model registry, artifact storage, wide adoption
- **How it fits**: MLflow excels at experiment tracking -- comparing runs with different parameters, storing artifacts, and managing model versions. It bridges traditional ML workflows and LLM evaluation.

### Weights & Biases (W&B)

- **Focus**: Experiment tracking, monitoring, collaboration
- **Best for**: Teams needing rich visualization and team collaboration
- **Strengths**: Beautiful dashboards, real-time monitoring, team collaboration, sweeps
- **How it fits**: W&B offers the best visualization capabilities and is designed for team collaboration. Its sweeps feature automates hyperparameter search, useful for prompt optimization.

### Tools Quick Comparison

```
Tool                      Focus
------------------------- ---------------------------------------------
Phoenix (Arize)           Tracing and evaluation for LLM apps
LangSmith                 Tracing, testing, evaluation for LangChain
OpenTelemetry             Vendor-neutral observability standard
MLflow                    ML experiment tracking and model management
Weights & Biases          Experiment tracking, monitoring, collaboration
```

### Choosing the Right Tool

| Criterion | Best Choice |
|-----------|------------|
| Open-source, self-hosted | Phoenix |
| LangChain-based stack | LangSmith |
| Enterprise, vendor-neutral | OpenTelemetry |
| ML experiment tracking | MLflow |
| Team collaboration + visualization | Weights & Biases |
| Multiple tools needed | OpenTelemetry (instrumentation) + Phoenix or LangSmith (UI) |

---

## Langfuse, LangGraph, and Tracing

### Langfuse

Langfuse is an open-source observability platform built specifically for LLM apps. Unlike generic APM tools, it understands LLM concepts -- generations, prompts, scores, datasets. You get per-request cost tracking, quality scores, and prompt management in one dashboard. Self-host or use the cloud version.

### LangGraph

When your LLM app has multiple steps (retrieve, generate, evaluate), LangGraph makes each step a node in a state graph. The observability benefit: each node emits its own trace span, so you see latency and errors per step, not just per request. This is the difference between "request took 5s" and "retrieval took 3s, generation took 1.5s, scoring took 0.5s."

### How Tracing Connects Everything

Tracing connects the dots between all these tools -- OpenTelemetry spans flow into Phoenix, Langfuse, and LangSmith. One instrumentation, multiple dashboards. Instrument your code with OpenTelemetry once, then route traces to whichever backend you prefer.

---

## Architecture Overview

```
+-------------------+
|   User Request    |
+--------+----------+
         |
         v
+--------+----------+     +------------------+
|  Prompt Formatting | --> | Prompt Tracker   |
|  (span: prompt)    |     | (version, tokens)|
+--------+----------+     +------------------+
         |
         v
+--------+----------+     +------------------+
|    LLM Call        | --> | Token Counter    |
|  (span: llm.call)  |     | Cost Calculator  |
+--------+----------+     +------------------+
         |
         v
+--------+----------+     +------------------+
| Response Parsing   | --> | Response Monitor |
| (span: parse)      |     | (quality, format)|
+--------+----------+     +------------------+
         |
         v
+--------+----------+
|   Evaluation       |
| (span: eval.check) |
+--------+----------+
         |
         v
+--------+----------+     +------------------+
|   Return Response  | --> | LLM Logger       |
|                    |     | Latency Tracker  |
+--------+----------+     +------------------+
         |
         v
+--------+----------+
|    Dashboard       |
| (all signals)      |
+--------------------+
```

Each step emits a **trace span** and feeds data into the appropriate observability component. The dashboard aggregates everything.

---

## 10. Key Takeaways

1. **Trace every LLM call**: `trace_id` + `span_id` give end-to-end visibility.
2. **Log structured data**: attach tokens, cost, model to every log entry.
3. **Track percentiles**: P50/P95/P99 reveal tail latency that means miss.
4. **Count tokens**: they drive cost and help optimize prompt length.
5. **Calculate cost per query**: tiny per-call costs compound at scale.
6. **Version your prompts**: measure accuracy/latency per version.
7. **Monitor response quality**: catch confidence drift and format errors.
8. **Use dashboards**: one view for all signals prevents alert fatigue.

---

## Summary Table

| Pillar | What It Tracks | Key Metric | Alert On |
|--------|---------------|------------|----------|
| Tracing | Request lifecycle | Span duration | Slow traces (>3s) |
| Logging | All pipeline events | Error count | ERROR/CRITICAL entries |
| Latency | Call timing | P95 latency | P95 exceeds threshold |
| Tokens | Prompt/response size | Avg tokens/call | Sudden token increase |
| Cost | Dollar spend | Cost per query | Budget exceeded |
| Prompts | Version effectiveness | Accuracy per version | Accuracy regression |
| Quality | Response correctness | Accuracy + confidence | High-confidence errors |
| Dashboard | All of the above | Combined view | Any signal crossing threshold |

---

## Common Mistakes

1. **No observability at all** -- "it works on my machine" does not scale to production
2. **Logging only errors** -- you miss slow calls, cost spikes, and accuracy drift
3. **Using mean latency** -- it hides tail latency; always use percentiles
4. **Ignoring output tokens** -- they are often 2-5x more expensive than input tokens
5. **Not versioning prompts** -- you cannot roll back or compare without versions
6. **Monitoring accuracy but not confidence** -- high-confidence errors are the most dangerous
7. **Separate dashboards for each signal** -- context-switching slows diagnosis
8. **Not correlating signals** -- a slow call that is also wrong and expensive tells a different story than each signal alone
9. **Not setting thresholds** -- without thresholds, you have data but no alerts
10. **Forgetting that retries double cost** -- retry logic should be tracked separately

---

## Best Practices

1. **Instrument once, export everywhere** -- use OpenTelemetry for vendor-neutral tracing
2. **Structured logs from day one** -- retrofitting structured logging is painful
3. **Track all four dimensions of every LLM call**: latency, tokens, cost, quality
4. **Set SLOs** (Service Level Objectives) for P95 latency, accuracy, and cost per query
5. **Alert on thresholds**, not just anomalies -- know your baseline and alert when metrics drift
6. **Version everything**: prompts, models, datasets, pipeline code
7. **Store traces for at least 30 days** -- you need history for regression analysis
8. **Include request IDs in all logs and traces** for end-to-end correlation
9. **Monitor in real time** -- batch analysis misses transient issues
10. **Review dashboards daily** -- observability only works if someone looks at it

---

## Interview Questions

1. **What is the difference between a trace and a span?**
   A trace represents the entire lifecycle of a request and is identified by a `trace_id`. A span represents a single unit of work within that trace (e.g., one LLM call, one database query). Spans have parent-child relationships forming a tree. A trace contains multiple spans.

2. **Why should you track P95 and P99 latency instead of just average latency?**
   Average latency can be misleading because a few extremely slow calls get averaged out with many fast calls. P95 tells you the latency experienced by 95% of users, and P99 catches the worst 1%. These percentiles reveal tail latency issues that the average hides.

3. **What is a high-confidence error and why is it dangerous?**
   A high-confidence error occurs when the model gives a wrong answer but reports high confidence (e.g., 90%+ confident but incorrect). It is dangerous because downstream systems and users trust high-confidence outputs, so these errors are more likely to cause real-world harm than low-confidence mistakes.

4. **How do you calculate the cost of an LLM call?**
   Cost = (input_tokens / 1000) * input_price_per_1K + (output_tokens / 1000) * output_price_per_1K. Different models have different pricing, and output tokens are typically more expensive than input tokens.

5. **Why should you version your prompts?**
   Prompt versioning lets you measure which wording performs best across accuracy, latency, token usage, and cost. Without versions, you cannot compare performance before and after a change, and you cannot roll back when a change causes regression.

6. **What is structured logging and why is it important for LLM applications?**
   Structured logging means each log entry is a dictionary with typed fields (timestamp, level, component, message, metadata) rather than a flat text string. For LLM apps, metadata includes model name, token counts, cost, and latency. This enables filtering, querying, and aggregation -- for example, "show me all LLM calls that cost more than $0.05 in the last hour."

7. **What is OpenTelemetry and how does it relate to LLM observability?**
   OpenTelemetry is a vendor-neutral observability standard for distributed tracing, metrics, and logs. It provides a single instrumentation API that can export data to any backend (Phoenix, Jaeger, Datadog, etc.). For LLM apps, you instrument your pipeline with OTel spans once, then view traces in whichever tool your team prefers, avoiding vendor lock-in.

8. **What signals should an LLM observability dashboard include?**
   A comprehensive dashboard should include: latency metrics (P50/P95/P99), token usage (input/output per call), cost analysis (total and per model), response quality (accuracy, confidence, format errors), prompt version comparison, and log summary (error counts and recent errors). All signals in one view prevents context-switching during diagnosis.

9. **How do you detect accuracy regression in a production LLM system?**
   Track accuracy continuously using ground truth labels (when available) or LLM-as-a-judge scores. Compare current accuracy against a baseline (previous version or historical average). Alert when accuracy drops below a threshold. Also monitor confidence calibration -- if confidence stays high but accuracy drops, the model is becoming overconfident.

10. **What is the difference between Langfuse and LangSmith?**
    Both are LLM observability platforms with tracing, evaluation, and prompt management. Langfuse is open-source and can be self-hosted, making it suitable for teams with data privacy requirements. LangSmith is developed by LangChain and offers deep integration with the LangChain/LangGraph framework, making it the natural choice for teams building on that stack.

---

## Hands-On Exercises

1. **Build a trace viewer**: Given a list of spans, reconstruct and display the trace tree with indentation showing parent-child relationships.

2. **Implement percentile calculation**: Write a function that takes a list of latencies and returns P50, P95, and P99 without using external libraries.

3. **Cost comparison calculator**: Given token counts and a pricing table, calculate and compare costs across 3+ models. Identify the cheapest model that meets an accuracy threshold.

4. **High-confidence error detector**: Build a monitor that flags responses where confidence > 0.8 but the prediction is incorrect. Track these over time and alert when the count exceeds a threshold.

5. **Prompt A/B test analyzer**: Track results for two prompt versions, then determine which version is statistically better using accuracy, latency, and cost as criteria.

---

## Mini Project

**Build an end-to-end LLM observability pipeline** that:

1. Instruments an LLM call pipeline with distributed tracing (trace ID, span per step)
2. Logs every call with structured metadata (model, tokens, cost, latency)
3. Tracks latency percentiles and alerts on slow calls
4. Counts tokens and calculates cost per model
5. Versions prompts and tracks accuracy per version
6. Monitors response quality including high-confidence errors
7. Renders a unified text dashboard with all signals

The pipeline should process at least 50 simulated queries and produce a complete observability report.

---

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/) -- the vendor-neutral observability standard
- [Arize Phoenix](https://github.com/Arize-AI/phoenix) -- open-source LLM observability
- [LangSmith Documentation](https://docs.smith.langchain.com/) -- LangChain's observability platform
- [Langfuse](https://langfuse.com/) -- open-source LLM engineering platform
- [MLflow](https://mlflow.org/) -- ML experiment tracking and model management
- [Weights & Biases](https://wandb.ai/) -- experiment tracking and visualization
