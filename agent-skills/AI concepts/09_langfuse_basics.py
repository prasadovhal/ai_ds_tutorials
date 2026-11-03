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

# Initialize LangFuse client (Langfuse 2.0+ reads from env vars)
public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
secret_key = os.getenv('LANGFUSE_SECRET_KEY')
base_url = os.getenv('LANGFUSE_BASE_URL')  # Note: underscore, not camelCase

print(f"[DEBUG] LANGFUSE_PUBLIC_KEY: {public_key[:10] if public_key else 'NOT SET'}...")
print(f"[DEBUG] LANGFUSE_SECRET_KEY: {secret_key[:10] if secret_key else 'NOT SET'}...")
print(f"[DEBUG] LANGFUSE_BASE_URL: {base_url if base_url else 'NOT SET (will default to EU cloud)'}")

try:
    # Use 'host' parameter (confirmed working earlier)
    if base_url and not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    lf_client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=base_url
    )
    print("[DEBUG] Langfuse client initialized successfully\n")
except Exception as e:
    print(f"[ERROR] Failed to initialize Langfuse: {e}")
    exit(1)

ollama_client = ollama.Client()


def simple_trace_example():
    """
    Simplest LangFuse trace: one trace, one span, one generation.
    This shows the basic hierarchy: trace > span > generation.
    """

    query = "Explain machine learning in simple terms"

    try:
        # Create a trace (represents one user request)
        trace = lf_client.trace(name="science_qa", input={"query": query})
        print(f"✓ Trace created: {trace.id}")

        # Create a span (represents one step: LLM call)
        span = trace.span(name="llm_generation", input={"query": query})
        print(f"✓ Span created: {span.id}")

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
        print(f"✓ LLM response received ({len(answer)} chars)")
        print(f"[DEBUG] Answer: {answer[:50]}...")

        # Log the generation to LangFuse
        try:
            # Create generation with output as string
            gen = span.generation(
                name="mistral_inference",
                model="mistral",
                input=query,
                output=str(answer) if answer else "",  # Ensure it's a string
                usage={
                    "input": 50,
                    "output": 100,
                    "total": 150
                },
                metadata={
                    "latency_ms": latency_ms,
                    "temperature": 0.7
                }
            )
            # Try to save/end the generation
            if hasattr(gen, 'end'):
                gen.end()
            print(f"✓ Generation logged with output")
        except Exception as e:
            print(f"✗ Error logging generation: {e}")
            import traceback
            traceback.print_exc()

        # End the span
        span.end()
        print(f"✓ Span ended")

        # Flush to send to cloud
        lf_client.flush()
        print(f"✓ Flushed to Langfuse")
        time.sleep(1)  # Wait for async send

        print(f"✓ Trace created: {trace.id}")
        print(f"View in LangFuse: https://us.cloud.langfuse.com/project/cmshi3anw05jpad0it1pqaib8/traces/{trace.id}\n")

        return trace.id

    except Exception as e:
        print(f"✗ Error in simple_trace_example: {e}")
        import traceback
        traceback.print_exc()
        return None


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

    # Flush to send to cloud
    lf_client.flush()

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

    # Flush to send to cloud
    lf_client.flush()

    print(f"\nTrace with metadata: {trace.id}")
    print("Metadata is indexed and searchable in LangFuse dashboard")

    return trace.id


def trace_user_query(user_query):
    """Trace a user query through the system"""

    query = user_query

    try:
        # Create a trace
        trace = lf_client.trace(name="user_query", input={"query": query})
        print(f"✓ Trace created: {trace.id}")

        # Create a span for LLM call
        span = trace.span(name="llm_inference", input={"query": query})
        print(f"✓ Span created")

        # Call LLM
        start_time = time.time()

        response = ollama_client.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        answer = response['message']['content']
        print(f"✓ LLM response received")

        # Log the generation
        span.generation(
            name="mistral_response",
            model="mistral",
            input=query,
            output=answer,
            usage={
                "input": 50,
                "output": len(answer.split()),
                "total": 50 + len(answer.split())
            },
            metadata={
                "latency_ms": latency_ms,
                "temperature": 0.7
            }
        )

        span.end()
        lf_client.flush()

        print(f"\n📊 Answer:")
        print(f"{answer}\n")
        print(f"View trace: {base_url}/project/cmshi3anw05jpad0it1pqaib8/traces/{trace.id}")

        return trace.id

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("File 9: LangFuse Basics")
    print("=" * 60)

    # Verify API keys are set
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        print("ERROR: LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set in .env")
        exit(1)

    print("\n--- Simple Trace Example ---")
    simple_trace_example()

    print("\n--- Multi-Step Trace Example ---")
    # multi_step_trace()

    print("\n--- Metadata and Context ---")
    # metadata_and_context()

    # Final flush
    try:
        lf_client.flush()
        print("\n✓ All traces flushed to Langfuse cloud")
        time.sleep(2)
        print("✓ Check Langfuse dashboard now!")
    except Exception as e:
        print(f"\n✗ Error flushing: {e}")