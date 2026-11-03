"""
Chapter 10: Observability

Covers monitoring and observability for LLM systems:
- Tracing: end-to-end request tracking and span hierarchies
- Structured logging: formatted logs for easy parsing and analysis
- Latency monitoring: tracking response times and bottlenecks
- Token tracking: counting input/output tokens for cost analysis
- Cost monitoring: calculating and tracking expenses
- Prompt tracking: versioning and monitoring prompt changes
- Response monitoring: quality metrics on generated outputs
- Quality alerts: thresholds for quality metrics
- Toxicity alerts: detecting harmful content
- Dashboards: aggregated metrics and visualizations
- Tools: Phoenix, LangSmith, OpenTelemetry, MLflow, Weights & Biases
- Correlation analysis: identifying factors affecting performance
- Root cause analysis: investigating quality degradations

Simple walkthrough of observability components and their integration.
"""

from statistics import mean


TRACE = [
    {"span": "request.start", "duration_ms": 5},
    {"span": "retrieve.context", "duration_ms": 40},
    {"span": "llm.call", "duration_ms": 900},
    {"span": "response.parse", "duration_ms": 20},
]

LOGS = [
    {"level": "INFO", "message": "request received"},
    {"level": "INFO", "message": "retrieval complete"},
    {"level": "WARNING", "message": "llm call is slow"},
]

RESPONSES = [
    {"quality": 0.90, "toxicity": 0.02, "latency_ms": 920, "tokens": 320, "cost": 0.012},
    {"quality": 0.84, "toxicity": 0.01, "latency_ms": 1010, "tokens": 280, "cost": 0.011},
    {"quality": 0.70, "toxicity": 0.08, "latency_ms": 1400, "tokens": 500, "cost": 0.020},
]


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def total_trace_time(spans):
    return sum(span["duration_ms"] for span in spans)


def log_summary(logs):
    summary = {}
    for log in logs:
        summary[log["level"]] = summary.get(log["level"], 0) + 1
    return summary


def average_latency(responses):
    return mean(item["latency_ms"] for item in responses)


def total_tokens(responses):
    return sum(item["tokens"] for item in responses)


def total_cost(responses):
    return sum(item["cost"] for item in responses)


def prompt_versions():
    return [
        {"version": "v1", "prompt": "Answer the question."},
        {"version": "v2", "prompt": "Answer clearly in two sentences."},
    ]


def quality_alerts(responses):
    alerts = []
    for index, item in enumerate(responses, start=1):
        if item["quality"] < 0.75:
            alerts.append(f"response {index} quality is low")
        if item["toxicity"] > 0.05:
            alerts.append(f"response {index} toxicity is high")
    return alerts


def dashboard(responses):
    return {
        "average_quality": mean(item["quality"] for item in responses),
        "average_latency_ms": average_latency(responses),
        "total_tokens": total_tokens(responses),
        "total_cost": total_cost(responses),
    }


def main():
    section("Chapter 10: Observability")

    section("1. Tracing")
    print(f"Trace time: {total_trace_time(TRACE)} ms")
    for span in TRACE:
        print(span)

    section("2. Structured Logging")
    print(log_summary(LOGS))

    section("3. Latency")
    print(f"Average latency: {average_latency(RESPONSES):.1f} ms")

    section("4. Token Tracking")
    print(f"Total tokens: {total_tokens(RESPONSES)}")

    section("5. Cost Tracking")
    print(f"Total cost: ${total_cost(RESPONSES):.4f}")

    section("6. Prompt Tracking")
    for version in prompt_versions():
        print(version)

    section("7. Response Monitoring")
    print(quality_alerts(RESPONSES))

    section("8. Dashboard")
    print(dashboard(RESPONSES))


if __name__ == "__main__":
    main()
