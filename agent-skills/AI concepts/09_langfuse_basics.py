"""
File 9: LangFuse Basics
Concepts: LangFuse setup, manual traces, spans, generations, token tracking

LangFuse is a commercial platform for tracing LLM applications.
Unlike file 8 (custom tracer), we now use the real LangFuse SDK.

This shows: connect to cloud, create traces, log generations, view in dashboard.
You need: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY in .env
"""

import os
from dotenv import load_dotenv
import time
import ollama
from langfuse import Langfuse

load_dotenv()

# Initialize LangFuse client (connects to cloud.langfuse.com)
lf_client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    baseurl=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
)

ollama_client = ollama.Client()


def simple_trace_example():
    """
    Simplest LangFuse trace: one trace, one span, one generation.
    This shows the basic hierarchy: trace > span > generation.
    """

    query = "What is photosynthesis?"

    # Create a trace (represents one user request)
    trace = lf_client.trace(name="science_qa", input={"query": query})

    # Create a span (represents one step: LLM call)
    span = trace.span(name="llm_generation", input={"query": query})

    # Call LLM
    start_time = time.time()

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a science expert. Answer concisely."},
            {"role": "user", "content": query}
        ]
    )

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    answer = response['message']['content']

    # Log the generation to LangFuse
    # In real usage, token counts come from LLM metadata
    generation = span.generation(
        name="mistral_inference",
        model="mistral",
        input=query,
        output=answer,
        usage={
            "input": 50,  # approximate token count
            "output": 100,
            "total": 150
        },
        metadata={
            "latency_ms": latency_ms,
            "temperature": 0.7
        }
    )

    # End the span
    span.end()

    print(f"Trace created: {trace.id}")
    print(f"View in LangFuse: https://cloud.langfuse.com/traces/{trace.id}")

    return trace.id


def multi_step_trace():
    """
    More complex trace: multiple spans representing different steps.

    Flow:
    1. Intent classification (span)
    2. Complexity estimation (span)
    3. LLM generation (span with generation)

    All spans linked via one trace.
    """

    query = "Compare mitochondrial and chloroplast structure"

    # Create trace
    trace = lf_client.trace(
        name="complex_query_processing",
        input={"query": query},
        metadata={"user_tier": "researcher"}
    )

    # Step 1: Intent classification
    span_intent = trace.span(name="intent_classification")
    time.sleep(0.05)
    intent = "research_analysis"
    span_intent.end(output={"intent": intent})

    # Step 2: Complexity estimation
    span_complexity = trace.span(name="complexity_estimation")
    time.sleep(0.05)
    complexity = 7
    span_complexity.end(output={"complexity": complexity})

    # Step 3: LLM generation with retrieval context
    span_llm = trace.span(name="llm_generation_with_context")

    # In real RAG, context comes from vector store (file 10)
    context = "Mitochondria: double-membrane organelle, cristae, ATP synthesis..."

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a biology expert. Compare structures."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )

    answer = response['message']['content']

    # Log generation
    span_llm.generation(
        name="mistral_comparison",
        model="mistral",
        input=query,
        output=answer,
        usage={"input": 200, "output": 300, "total": 500}
    )

    span_llm.end()

    print(f"\nMulti-step trace created: {trace.id}")
    print(f"View in LangFuse: https://cloud.langfuse.com/traces/{trace.id}")

    return trace.id


def metadata_and_context():
    """
    Show how to attach metadata and context to traces/spans.
    Metadata is searchable in LangFuse dashboard.
    """

    query = "What is quantum entanglement?"

    trace = lf_client.trace(
        name="physics_question",
        input={"query": query},
        metadata={
            "domain": "physics",
            "complexity": 8,
            "user_tier": "professor",
            "session_id": "sess_abc123"
        }
    )

    span = trace.span(
        name="llm_response",
        metadata={
            "model": "mistral",
            "temperature": 0.7,
            "max_tokens": 500
        }
    )

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a physics expert."},
            {"role": "user", "content": query}
        ]
    )

    answer = response['message']['content']

    span.generation(
        name="mistral_answer",
        model="mistral",
        input=query,
        output=answer,
        metadata={
            "attempted_retries": 0,
            "confidence_score": 8,
            "grounding": "textbook knowledge"
        }
    )

    span.end()

    print(f"\nTrace with metadata: {trace.id}")
    print("Metadata is indexed and searchable in LangFuse dashboard")

    return trace.id


if __name__ == "__main__":
    print("File 9: LangFuse Basics")
    print("=" * 60)

    print("\n--- Simple Trace Example ---")
    trace_id_1 = simple_trace_example()

    print("\n\n--- Multi-Step Trace Example ---")
    trace_id_2 = multi_step_trace()

    print("\n\n--- Metadata and Context ---")
    trace_id_3 = metadata_and_context()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. LangFuse hierarchy: Trace > Span > Generation")
    print("2. Trace = one user request end-to-end")
    print("3. Span = one step (e.g., LLM call, retrieval)")
    print("4. Generation = LLM output (model, tokens, metadata)")
    print("5. Metadata is searchable: domain, user_tier, complexity, etc.")
    print("6. Visit cloud.langfuse.com and search by trace_id to view traces")
    print("7. All traces are persisted; view latency, tokens, metadata in dashboard")
