# Chapter 10 - LLM Application Observability

Observability tools for monitoring LLM pipelines: tracing, logging, latency analysis, token/cost tracking, prompt versioning, and response quality monitoring.

## Files

| File | Description |
|------|-------------|
| `dataset.py` | Data loading, token estimation, simulated LLM responses and traces |
| `sample_data.json` | Pre-built sample traces, logs, metrics, pricing, and prompt versions |
| `evaluator.py` | Observability tool implementations (8 classes) |
| `theory.md` | All theory, intuition, diagrams, and interview questions |
| `main.py` | Demonstrates all tools with output |

## Evaluator Classes

- **TraceManager** - Distributed traces with parent-child spans
- **LLMLogger** - Structured logging with level filtering
- **LatencyTracker** - P50/P95/P99 percentile calculations
- **TokenCounter** - Token usage tracking and estimation
- **CostCalculator** - Per-model pricing and cost comparison
- **PromptTracker** - Prompt versioning with effectiveness metrics
- **ResponseMonitor** - Accuracy, confidence, and format error tracking
- **ObservabilityDashboard** - Unified text-based dashboard

## Run

```bash
cd chapter_10_observability
python main.py
```

No external dependencies required -- uses Python standard library only.
