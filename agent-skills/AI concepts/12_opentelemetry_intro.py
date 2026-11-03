"""
File 12: OpenTelemetry Introduction
Concepts: OpenTelemetry (OTel), traces, spans, context propagation, exporters

OpenTelemetry is an open-source standard for observability (like HTTP for telemetry).
LangFuse and LangSmith use OTel under the hood.

This file shows OTel basics:
- Create tracer
- Start/end spans
- Pass context between functions
- Export to console (in prod: send to LangFuse, Jaeger, Datadog, etc.)
"""

import os
from dotenv import load_dotenv
import time
from opentelemetry import trace, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.resources import Resource

load_dotenv()

# Configure OpenTelemetry
# Create a resource (identifies your service)
resource = Resource.create({
    "service.name": "science_gateway",
    "service.version": "1.0.0"
})

# Create a tracer provider
tracer_provider = TracerProvider(resource=resource)

# Use in-memory exporter for local testing (no backend needed)
span_exporter = InMemorySpanExporter()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))

# Set as global tracer provider
trace.set_tracer_provider(tracer_provider)

# Get a tracer (one per module/service)
tracer = trace.get_tracer(__name__)


def simple_span_example():
    """
    Create a simple span.
    A span represents one unit of work with start/end times.
    """

    print("\n=== Simple Span Example ===")

    with tracer.start_as_current_span("intent_classification") as span:
        span.set_attribute("query", "What is photosynthesis?")
        span.set_attribute("method", "keyword_rules")

        # Simulate work
        time.sleep(0.05)

        span.set_attribute("result", "factual")

    print("Span completed. Check exporter for details.")


def nested_spans_example():
    """
    Spans can nest: parent span contains child spans.
    This represents hierarchical work flow.
    """

    print("\n=== Nested Spans Example ===")

    with tracer.start_as_current_span("process_query") as parent_span:
        parent_span.set_attribute("query", "What is DNA?")

        # Child span 1: intent classification
        with tracer.start_as_current_span("classify_intent") as child1:
            time.sleep(0.02)
            child1.set_attribute("intent", "factual")

        # Child span 2: complexity estimation
        with tracer.start_as_current_span("estimate_complexity") as child2:
            time.sleep(0.03)
            child2.set_attribute("complexity", 3)

        # Child span 3: LLM call
        with tracer.start_as_current_span("llm_inference") as child3:
            time.sleep(0.1)
            child3.set_attribute("model", "mistral")
            child3.set_attribute("tokens", 150)

    print("Nested spans completed.")


def context_propagation_otel():
    """
    OTel context propagation: pass context between functions.
    This ensures all spans in a request are linked.

    Use case: request comes in → calls function A → calls function B.
    All spans should share the same trace_id.
    """

    print("\n=== Context Propagation ===")

    def classify_intent_otel(query):
        """Function 1: classify intent."""
        # Current span is captured in context
        with tracer.start_as_current_span("classify_intent"):
            time.sleep(0.01)
            return "factual"

    def estimate_complexity_otel(query, intent):
        """Function 2: estimate complexity."""
        # Start a new span; it's automatically linked to parent via context
        with tracer.start_as_current_span("estimate_complexity"):
            time.sleep(0.02)
            return 3

    def call_llm_otel(query, complexity):
        """Function 3: call LLM."""
        with tracer.start_as_current_span("call_llm"):
            time.sleep(0.05)
            return "Answer: photosynthesis is..."

    # Wrap entire flow in one trace
    with tracer.start_as_current_span("end_to_end_query") as root_span:
        root_span.set_attribute("query", "What is photosynthesis?")

        intent = classify_intent_otel("What is photosynthesis?")
        complexity = estimate_complexity_otel("What is photosynthesis?", intent)
        answer = call_llm_otel("What is photosynthesis?", complexity)

    print("End-to-end query with context propagation completed.")


def attributes_vs_events():
    """
    Spans can have:
    - Attributes: metadata (key-value pairs)
    - Events: timestamped markers (things that happened)
    """

    print("\n=== Attributes vs Events ===")

    with tracer.start_as_current_span("rag_pipeline") as span:
        # Attributes: static metadata
        span.set_attribute("domain", "biology")
        span.set_attribute("user_tier", "researcher")

        # Event 1: retrieval started
        span.add_event("retrieval_started", {"method": "vector_search"})
        time.sleep(0.03)

        # Event 2: retrieval completed
        span.add_event("retrieval_completed", {"num_chunks": 3, "top_score": 0.92})
        time.sleep(0.05)

        # Event 3: LLM call started
        span.add_event("llm_inference_started", {"model": "mistral"})
        time.sleep(0.1)

        # Event 4: LLM call completed
        span.add_event("llm_inference_completed", {"tokens_used": 250})

    print("Span with attributes and events completed.")


def get_exported_spans():
    """
    Retrieve exported spans from in-memory exporter.
    In production, exporter sends to backend (LangFuse, Jaeger, etc.)
    """

    print("\n=== Exported Spans Summary ===")

    spans = span_exporter.get_finished_spans()
    print(f"Total spans: {len(spans)}\n")

    for span in spans[-5:]:  # Last 5 spans
        print(f"Span: {span.name}")
        print(f"  Duration: {(span.end_time - span.start_time)*1000:.2f}ms")
        print(f"  Attributes: {dict(span.attributes) if span.attributes else {}}")
        print()


if __name__ == "__main__":
    print("File 12: OpenTelemetry Introduction")

    simple_span_example()
    nested_spans_example()
    context_propagation_otel()
    attributes_vs_events()
    get_exported_spans()
    
    
"""

Trace = Complete journey of one request
Span  = One operation in that journey
Context	= Keeps spans connected
Attribute = Metadata about a span
Event = Something that happened during a span
Exporter = Sends/stores telemetry somewhere
=======================================================

Nested spans = structure
Context propagation = connection

Nested spans describe the hierarchy.
Context propagation makes that hierarchy/trace relationship possible across execution boundaries.


Trace ID = the whole journey.
Span ID = one operation.
Parent Span ID = who called/contained this operation.
Context propagation = carries the Trace ID and relevant span context from one service to the next.

                         CONTEXT PROPAGATION
          Trace ID = ABC123 is propagated across services
        ─────────────────────────────────────────────────────►

┌──────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
│   API SERVICE    │      │      RAG SERVICE         │      │      LLM SERVICE         │
│                  │      │                          │      │                          │
│ API Request      │      │ process_query            │      │ generate_answer          │
│                  │      │                          │      │                          │
│ Trace ID:        │─────►│ Trace ID: ABC123         │─────►│ Trace ID: ABC123         │
│ ABC123           │      │ Span ID: S2              │      │ Span ID: S8              │
│                  │      │ Parent: S1               │      │ Parent: S2*              │
│ Span ID: S1      │      │                          │      │                          │
│                  │      │  ├── classify_intent     │      │  ├── prompt_processing   │
│                  │      │  │   Span ID: S3         │      │  │   Span ID: S9         │
│                  │      │  │   Parent: S2          │      │  │   Parent: S8          │
│                  │      │      │                   │      │      │                   │
│                  │      │  ├── retrieve            │      │  ├── model_call          │
│                  │      │  │   Span ID: S4         │      │  │   Span ID: S10        │
│                  │      │  │   Parent: S2          │      │  │   Parent: S8          │
│                  │      │  │      │                │      │      │                   │
│                  │      │  │      ├── vector_search│      │  └── parse_response      │
│                  │      │  │      │   Span ID: S5  │      │      Span ID: S11        │
│                  │      │  │      │   Parent: S4   │      │      Parent: S8          │
│                  │      │  │      │                │      │                          │
│                  │      │  │      └── rerank       │      │                          │
│                  │      │  │          Span ID: S6  │      │                          │
│                  │      │  │          Parent: S4   │      │                          │
│                  │      │  │                       │      │                          │
│                  │      │  └── build_prompt        │      │                          │
│                  │      │      Span ID: S7         │      │                          │
│                  │      │      Parent: S2          │      │                          │
└──────────────────┘      └──────────────────────────┘      └──────────────────────────┘

"""