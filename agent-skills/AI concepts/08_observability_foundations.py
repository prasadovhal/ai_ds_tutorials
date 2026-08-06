"""
File 8: Observability Foundations
Concepts: Tracing, spans, structured logging, correlation IDs, timing decorators, context propagation

Observability = ability to understand system behavior from outputs (logs, traces, metrics).
This file builds a minimal custom tracer from scratch (pure Python, no external libraries).

Key concepts: trace_id (links all steps in one request), span_id (individual step),
correlation (trace_id passed through all functions), structured JSON logs.
"""

import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Any, Dict

@dataclass
class Span:
    """
    Represents one logical unit of work (a span).
    Spans nest: a trace has multiple spans, spans can have children.
    """
    trace_id: str
    span_id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: str = "in_progress"  # in_progress, success, error
    attributes: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.metadata is None:
            self.metadata = {}

    def end(self):
        """Mark span as complete."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = "success"

    def to_dict(self):
        """Convert to JSON-serializable dict."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2) if self.duration_ms else None,
            "status": self.status,
            "attributes": self.attributes,
            "metadata": self.metadata
        }


class Tracer:
    """
    Minimal tracer: manages traces and spans.
    In production, this would export to LangFuse, Jaeger, or cloud backend.
    """

    def __init__(self):
        self.traces = {}  # trace_id -> list of spans
        self.current_trace_id = None

    def start_trace(self, name="request"):
        """Start a new trace. Returns trace_id."""
        trace_id = str(uuid.uuid4())[:8]
        self.current_trace_id = trace_id
        self.traces[trace_id] = []
        return trace_id

    def start_span(self, name, trace_id=None, attributes=None):
        """
        Start a new span within a trace.
        Span tracks: name, start/end time, duration, status.
        """
        if trace_id is None:
            trace_id = self.current_trace_id

        span_id = str(uuid.uuid4())[:8]
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            name=name,
            start_time=time.time(),
            attributes=attributes or {}
        )

        self.traces[trace_id].append(span)
        return span

    def end_span(self, span):
        """Mark span as complete."""
        span.end()

    def get_trace(self, trace_id):
        """Retrieve all spans for a trace."""
        return self.traces.get(trace_id, [])


def log_structured(trace_id, span_id, event, level="INFO", **kwargs):
    """
    Log structured JSON with trace context.
    This makes it easy to filter logs by trace_id in production.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": trace_id,
        "span_id": span_id,
        "event": event,
        "level": level,
        **kwargs  # add any additional fields
    }

    print(json.dumps(log_entry, indent=2))
    return log_entry


def timed(func):
    """
    Decorator to measure function latency.
    Useful for profiling bottlenecks.
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        latency_ms = (end - start) * 1000

        print(f"[TIMING] {func.__name__} took {latency_ms:.2f}ms")
        return result

    return wrapper


def trace_query_flow(query):
    """
    Example: trace a query through intent classification → domain routing → LLM call.
    Shows how trace_id propagates through all steps.
    """

    tracer = Tracer()
    trace_id = tracer.start_trace("query_processing")

    log_structured(trace_id, "root", "Query received", query=query)

    # Step 1: Intent classification
    span_intent = tracer.start_span("intent_classification", attributes={"query": query})
    time.sleep(0.1)  # simulate work
    log_structured(trace_id, span_intent.span_id, "Intent classified", intent="factual")
    tracer.end_span(span_intent)

    # Step 2: Complexity routing
    span_complexity = tracer.start_span("complexity_estimation", attributes={"query": query})
    time.sleep(0.05)
    log_structured(trace_id, span_complexity.span_id, "Complexity scored", complexity=3)
    tracer.end_span(span_complexity)

    # Step 3: LLM call
    span_llm = tracer.start_span("llm_inference", attributes={"model": "mistral"})
    time.sleep(0.2)  # simulate LLM latency
    log_structured(trace_id, span_llm.span_id, "LLM response received", tokens=150)
    tracer.end_span(span_llm)

    # Print trace summary
    trace = tracer.get_trace(trace_id)
    print(f"\n=== Trace Summary (ID: {trace_id}) ===")
    total_duration = sum(s.duration_ms for s in trace)
    print(f"Total duration: {total_duration:.2f}ms")
    print(f"Spans: {len(trace)}")
    for span in trace:
        print(f"  - {span.name}: {span.duration_ms:.2f}ms")

    return trace_id, trace


def context_propagation_example():
    """
    Show how trace_id is passed between functions.
    All functions receive trace_id, ensuring correlation.
    """

    def classify_intent(query, trace_id):
        """Step 1: classify intent."""
        log_structured(trace_id, "step1", "Classifying intent", query=query)
        return "factual"

    def estimate_complexity(query, intent, trace_id):
        """Step 2: estimate complexity."""
        log_structured(trace_id, "step2", "Estimating complexity", intent=intent)
        return 3

    def call_llm(query, complexity, trace_id):
        """Step 3: call LLM."""
        log_structured(trace_id, "step3", "Calling LLM", complexity=complexity)
        return "Answer: photosynthesis is..."

    # Execute flow with context propagation
    print("\n=== Context Propagation Example ===")
    trace_id = str(uuid.uuid4())[:8]

    intent = classify_intent("What is photosynthesis?", trace_id)
    complexity = estimate_complexity("What is photosynthesis?", intent, trace_id)
    answer = call_llm("What is photosynthesis?", complexity, trace_id)

    print(f"\nAll operations share trace_id: {trace_id}")
    print("This allows correlating all logs for one user request.")


if __name__ == "__main__":
    print("File 8: Observability Foundations")
    print("=" * 60)

    print("\n--- Span Structure ---")
    span = Span(
        trace_id="abc123",
        span_id="xyz789",
        name="llm_inference",
        start_time=time.time(),
        attributes={"model": "mistral", "tokens": 150}
    )
    time.sleep(0.1)
    span.end()
    print(json.dumps(span.to_dict(), indent=2))

    print("\n\n--- Query Flow Tracing ---")
    trace_id, trace = trace_query_flow("What is photosynthesis?")

    context_propagation_example()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Trace = one user request end-to-end")
    print("2. Span = one logical unit of work (e.g., LLM call)")
    print("3. Trace_id links all steps together for correlation")
    print("4. Structured JSON logs are queryable and filterable")
    print("5. Context propagation: pass trace_id through all functions")
    print("6. This foundation enables debugging and performance analysis")
