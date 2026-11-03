# Chapter 10 -- LLM Application Observability

## Overview

Observability means understanding your LLM system's internal state from its external outputs -- traces, logs, latency, token usage, costs, prompt versions, and response quality. Without it, slow calls, accuracy drops, and cost spikes go unnoticed until users complain.

**Eight pillars**: (1) Distributed Tracing, (2) Structured Logging, (3) Latency Monitoring, (4) Token Usage Tracking, (5) Cost Calculation, (6) Prompt Version Tracking, (7) Response Quality Monitoring, (8) Unified Dashboards.

---

## 1. Distributed Tracing

A **trace** captures the full lifecycle of an LLM request as a tree of **spans**. Each span is one unit of work (prompt formatting, LLM call, parsing). Think of it like an itemized receipt -- instead of "total: 5s," you see which step was the bottleneck.

**Span fields**: `span_id`, `trace_id`, `parent_span_id`, `name`, `start_time`, `end_time`, `duration_ms`, `status`, `attributes` (model, tokens, etc.).

### Trace Tree Example

```
pipeline.run [OK] 2345.0ms
|-- prompt.format [OK] 15.0ms
|-- llm.call [OK] 2075.0ms      <-- bottleneck
|-- response.parse [OK] 15.0ms
|-- evaluation.check [OK] 230.0ms
```

### Span Attributes

| Span | Typical Attributes |
|------|-------------------|
| `pipeline.run` | `question_id`, `pipeline_version` |
| `prompt.format` | `prompt_version`, `input_tokens` |
| `llm.call` | `model`, `input_tokens`, `output_tokens`, `temperature` |
| `response.parse` | `parsed_answer`, `confidence`, `format_ok` |
| `evaluation.check` | `correct`, `ground_truth`, `predicted` |

**Pros**: Pinpoints bottlenecks, enables per-step debugging, essential for multi-step pipelines.
**Cons**: Adds instrumentation overhead; traces without attributes are hard to debug.

**Common mistakes**: Not tracing at all; missing child spans; no slow-trace alerting threshold.

---

## 2. Structured LLM Logging

Structured logs attach queryable metadata (tokens, cost, model, latency) to every event, unlike flat `print()` statements. Each entry has: `timestamp`, `level`, `component`, `message`, `metadata`.

### Log Levels

| Level | Marker | Use |
|-------|--------|-----|
| DEBUG | `[ ]` | Verbose development details |
| INFO | `[*]` | Normal operation events |
| WARNING | `[!]` | Potential issues (slow calls, low confidence) |
| ERROR | `[X]` | Failures (incorrect predictions, API errors) |
| CRITICAL | `[!!!]` | System-breaking failures |

### Example Entries

```
[*] 2026-07-03T10:00:02 [llm] LLM call completed | latency_ms=2075, input_tokens=245, output_tokens=38, model=gpt-4, cost_usd=0.00961
[!] 2026-07-03T10:00:08 [llm] LLM call exceeded threshold | latency_ms=5470, threshold_ms=3000
[X] 2026-07-03T10:00:08 [evaluation] Incorrect prediction | expected=A, predicted=B, confidence=0.65
```

**Best practices**: Always log model name, token counts, and cost; include `request_id` for trace correlation; store as JSON for querying.

---

## 3. Latency Monitoring

Average latency is misleading -- if 5% of calls take 10s, the average hides it. **Percentile tracking** (P50/P95/P99) exposes tail latency.

### Key Metrics

| Metric | What It Tells You |
|--------|-------------------|
| P50 (median) | Typical user experience |
| P95 | Worst experience for most users |
| P99 | Edge-case worst experience |
| Slow calls | Count exceeding threshold |

### Latency Distribution (typical log-normal shape)

```
    400-  1400ms | ######################## (12)
   1400-  2400ms | ############################## (15)
   2400-  3400ms | ############## (7)
   3400-  4400ms | ######## (4)
   4400-  5400ms | ###### (3)
   5400-  6400ms | ## (1)
```

Set a threshold (e.g., 3000ms) and alert when exceeded. Slow calls may indicate throttling, complex prompts, network issues, or cold starts.

**Common mistakes**: Using only mean; not tracking percentiles over time; thresholds too tight or too loose.

---

## 4. Token Usage Tracking

Tokens are the currency of LLM APIs. Track `input_tokens`, `output_tokens`, `total_tokens`, and `model` per call to optimize prompts and forecast costs.

**Token estimation** (when exact counts unavailable): `estimated_tokens = len(text) // 4`. Use `tiktoken` in production.

### Key Statistics

| Metric | Description |
|--------|-------------|
| Total input/output tokens | Sum across all calls |
| Avg input/call | Average prompt size |
| Avg output/call | Average response size |

### Usage by Model Example

```
gpt-4:          50 calls, 13,250 in / 3,150 out
gpt-3.5-turbo:  10 calls,  2,650 in /   620 out
```

If the cheaper model achieves similar accuracy for some tasks, routing those tasks saves significant cost.

**Best practices**: Track per call, not just totals; compare across prompt versions; monitor for sudden output length changes.

---

## 5. Cost Calculation

A single LLM call costs fractions of a cent, but at scale costs explode silently.

### Cost Formula

```
input_cost  = (input_tokens / 1000) * input_price_per_1k
output_cost = (output_tokens / 1000) * output_price_per_1k
total_cost  = input_cost + output_cost
```

### Model Pricing Reference

| Model | Input (per 1K) | Output (per 1K) |
|-------|---------------|-----------------|
| gpt-4 | $0.0300 | $0.0600 |
| gpt-4-turbo | $0.0100 | $0.0300 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| claude-3-opus | $0.0150 | $0.0750 |
| claude-3-sonnet | $0.0030 | $0.0150 |
| claude-3-haiku | $0.00025 | $0.00125 |

### Model Cost Comparison (10,000 input + 2,000 output tokens)

| Model | Input Cost | Output Cost | Total Cost |
|-------|-----------|-------------|------------|
| claude-3-haiku | $0.0025 | $0.0025 | $0.0050 |
| gpt-3.5-turbo | $0.0050 | $0.0030 | $0.0080 |
| claude-3-sonnet | $0.0300 | $0.0300 | $0.0600 |
| gpt-4-turbo | $0.1000 | $0.0600 | $0.1600 |
| claude-3-opus | $0.1500 | $0.1500 | $0.3000 |
| gpt-4 | $0.3000 | $0.1200 | $0.4200 |

The cheapest model (claude-3-haiku) is **84x cheaper** than gpt-4 for the same token volume.

**Key concepts**: Cost per query = total_cost / num_queries; output tokens often 2-5x more expensive; retries double costs.

**Common mistakes**: Ignoring output token costs; not updating pricing tables; not tracking cost per feature/endpoint.

---

## 6. Prompt Version Tracking

Changing a prompt alters accuracy, latency, and cost. Version tracking lets you compare, A/B test, and roll back.

### Version Comparison Example

| Version | Accuracy | Confidence | Latency | Tokens | Change |
|---------|----------|------------|---------|--------|--------|
| v1 | 58.0% | 0.650 | 1500ms | 180 | Minimal prompt |
| v2 | 68.0% | 0.720 | 1600ms | 240 | Added role + format instruction |
| v3 | 72.0% | 0.780 | 1700ms | 290 | Chain-of-thought + expertise framing |

Each improvement costs more tokens. Version tracking quantifies this trade-off.

**Best practices**: Never change production prompts without a new version; A/B test before full rollout; track accuracy, confidence, latency, and tokens; keep old versions for rollback.

---

## 7. Response Quality Monitoring

LLM pipelines can silently degrade. Monitor accuracy, format errors, and confidence calibration continuously.

### Key Quality Metrics

| Metric | Why It Matters |
|--------|---------------|
| Accuracy | Core quality signal |
| Avg confidence | Calibration indicator |
| Format error rate | Usability issue |
| Low confidence count | Uncertain predictions |
| High-confidence errors | **Most dangerous failure mode** |

**High-confidence errors**: Wrong answer + high confidence (>=0.80). Dangerous because users/systems trust confident outputs. Monitor the gap between avg confidence and actual accuracy to detect overconfidence.

### Quality Report Example

```
Total responses:         50
Accuracy:                72.0%
Avg confidence:          0.720
Format errors:           2 (4.0%)
Low confidence (<0.5):   3
High-confidence errors:  4
```

**Common mistakes**: Monitoring only accuracy; not alerting on high-confidence errors; waiting for user complaints.

---

## 8. Unified Observability Dashboard

Separate tools for traces, logs, costs, and accuracy create silos. A single dashboard combining all signals enables rapid diagnosis.

### Dashboard Sections

| Section | Key Signals |
|---------|-------------|
| Latency | P50, P95, P99, slow call count |
| Tokens | Total tokens, per-call averages |
| Cost | Total cost, cost by model |
| Quality | Accuracy, confidence, format errors |
| Prompts | Per-version accuracy and cost |
| Logs | Count by level, recent errors |

**Best practices**: Refresh at regular intervals; show recent errors prominently; add time-series charts in production; set alerts on threshold crossings.

---

## 9. Observability Tools Overview

### Tool Comparison

| Tool | Focus | Best For | Key Strengths |
|------|-------|----------|---------------|
| Phoenix (Arize) | Tracing + evaluation | Open-source, self-hosted | Rich tracing UI, evaluation built-in |
| LangSmith | Tracing, testing, evaluation | LangChain-based stacks | Deep LangChain integration, playground |
| OpenTelemetry | Vendor-neutral standard | Enterprise, vendor-neutral | Industry standard, any backend |
| MLflow | Experiment tracking | ML experiments + LLM eval | Model registry, artifact storage |
| Weights & Biases | Experiment tracking + monitoring | Team collaboration | Beautiful dashboards, sweeps |

### Choosing the Right Tool

| Criterion | Best Choice |
|-----------|------------|
| Open-source, self-hosted | Phoenix |
| LangChain-based stack | LangSmith |
| Enterprise, vendor-neutral | OpenTelemetry |
| ML experiment tracking | MLflow |
| Team collaboration + visualization | Weights & Biases |
| Multiple tools needed | OpenTelemetry (instrumentation) + Phoenix or LangSmith (UI) |

### Langfuse & LangGraph

**Langfuse**: Open-source LLM observability platform with per-request cost tracking, quality scores, and prompt management. Self-host or use cloud.

**LangGraph**: Makes each pipeline step a graph node, each emitting its own trace span -- giving per-step latency/error visibility instead of per-request only.

**Tracing connects everything**: Instrument with OpenTelemetry once, route traces to any backend (Phoenix, Langfuse, LangSmith).

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
+--------+----------+     +------------------+
         |
         v
+--------+----------+     +------------------+
|    LLM Call        | --> | Token Counter    |
|                    |     | Cost Calculator  |
+--------+----------+     +------------------+
         |
         v
+--------+----------+     +------------------+
| Response Parsing   | --> | Response Monitor |
+--------+----------+     +------------------+
         |
         v
+--------+----------+     +------------------+
|   Evaluation       | --> | LLM Logger       |
|                    |     | Latency Tracker  |
+--------+----------+     +------------------+
         |
         v
+--------+----------+
|    Dashboard       |
+--------------------+
```

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
| Logging | Pipeline events | Error count | ERROR/CRITICAL entries |
| Latency | Call timing | P95 latency | P95 exceeds threshold |
| Tokens | Prompt/response size | Avg tokens/call | Sudden token increase |
| Cost | Dollar spend | Cost per query | Budget exceeded |
| Prompts | Version effectiveness | Accuracy per version | Accuracy regression |
| Quality | Response correctness | Accuracy + confidence | High-confidence errors |
| Dashboard | All of the above | Combined view | Any threshold crossed |

---

## Common Mistakes

1. No observability at all
2. Logging only errors -- missing slow calls, cost spikes, accuracy drift
3. Using mean latency instead of percentiles
4. Ignoring output token costs (often 2-5x more expensive)
5. Not versioning prompts
6. Monitoring accuracy but not confidence -- high-confidence errors are most dangerous
7. Separate dashboards per signal -- context-switching slows diagnosis
8. Not correlating signals (slow + wrong + expensive tells a richer story)
9. No thresholds -- data without alerts
10. Forgetting retries double cost

---

## Best Practices

1. Instrument once, export everywhere (OpenTelemetry)
2. Structured logs from day one
3. Track four dimensions per LLM call: latency, tokens, cost, quality
4. Set SLOs for P95 latency, accuracy, and cost per query
5. Alert on thresholds, not just anomalies
6. Version everything: prompts, models, datasets, pipeline code
7. Store traces for at least 30 days
8. Include request IDs in all logs and traces
9. Monitor in real time
10. Review dashboards daily

---

## Interview Questions

1. **Trace vs span?**
   A trace groups all spans for one request (`trace_id`). A span is one unit of work within that trace. Spans form a parent-child tree.

2. **Why P95/P99 instead of average latency?**
   Averages hide tail latency. P95/P99 expose the slow calls that 5% or 1% of users experience.

3. **What is a high-confidence error?**
   A wrong answer with high confidence (e.g., 90%+). Dangerous because users/systems trust confident outputs.

4. **How to calculate LLM call cost?**
   `cost = (input_tokens/1000)*input_price + (output_tokens/1000)*output_price`. Output tokens are typically more expensive.

5. **Why version prompts?**
   To measure which wording performs best, compare before/after, and roll back on regression.

6. **What is structured logging?**
   Log entries as dictionaries with typed fields (timestamp, level, metadata) instead of flat text. Enables filtering and aggregation.

7. **What is OpenTelemetry?**
   Vendor-neutral observability standard for tracing, metrics, and logs. Instrument once, export to any backend.

8. **What should an LLM dashboard include?**
   Latency (P50/P95/P99), token usage, cost by model, response quality (accuracy, confidence, format errors), prompt version comparison, and log summary.

9. **How to detect accuracy regression?**
   Track accuracy continuously against a baseline. Alert on drops. Monitor confidence calibration -- high confidence + low accuracy = overconfidence.

10. **Langfuse vs LangSmith?**
    Both provide tracing, evaluation, and prompt management. Langfuse is open-source/self-hostable. LangSmith has deep LangChain integration.

---

## Hands-On Exercises

1. **Trace viewer**: Reconstruct and display a trace tree from a list of spans with parent-child indentation.
2. **Percentile calculator**: Compute P50, P95, P99 from raw latencies without external libraries.
3. **Cost comparison**: Calculate costs across 3+ models given token counts and pricing. Find cheapest model meeting an accuracy threshold.
4. **High-confidence error detector**: Flag responses with confidence > 0.8 but incorrect prediction. Alert when count exceeds threshold.
5. **Prompt A/B test**: Compare two prompt versions on accuracy, latency, and cost.

---

## Mini Project

Build an end-to-end LLM observability pipeline that: (1) instruments an LLM pipeline with distributed tracing, (2) logs every call with structured metadata, (3) tracks latency percentiles and alerts on slow calls, (4) counts tokens and calculates cost per model, (5) versions prompts and tracks accuracy per version, (6) monitors response quality including high-confidence errors, (7) renders a unified text dashboard. Process at least 50 simulated queries.

---

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Arize Phoenix](https://github.com/Arize-AI/phoenix)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Langfuse](https://langfuse.com/)
- [MLflow](https://mlflow.org/)
- [Weights & Biases](https://wandb.ai/)
