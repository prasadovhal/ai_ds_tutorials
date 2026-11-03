"""
File 18: Pulling Traces from Langfuse (Online → Local)
Concepts: Trace fetching, offline evaluation, observation inspection

OTel is write-only (push). To READ traces back, use the backend's own API.
Langfuse SDK provides fetch_* methods to pull traces into local Python.

Use cases:
- Inspect what was retrieved and generated after a run
- Run offline evaluation on past traces
- Compare retrieval scores across sessions
- Export trace data for reporting

Prerequisites:
- Traces already created (run file 11 first)
- LANGFUSE_* vars set in .env
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from langfuse import Langfuse

# Load .env from the AI concepts directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Initialize Langfuse client with explicit credentials
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
base_url = os.getenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")

if not public_key or not secret_key:
    print(f"ERROR: Missing credentials")
    print(f"  LANGFUSE_PUBLIC_KEY: {public_key}")
    print(f"  LANGFUSE_SECRET_KEY: {secret_key}")
    print(f"  .env path: {env_path}")
    print(f"  .env exists: {env_path.exists()}")
    raise ValueError("Missing LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY in .env")

lf_client = Langfuse(
    public_key=public_key,
    secret_key=secret_key,
    host=base_url
)


def fetch_recent_traces(limit=5):
    """
    Pull the most recent traces from Langfuse.
    Each trace = one top-level operation (e.g. one RAG query).
    """
    print(f"\n=== Recent {limit} Traces ===")

    response = lf_client.fetch_traces(limit=limit)

    for t in response.data:
        print(f"\nTrace ID : {t.id}")
        print(f"Name     : {t.name}")
        print(f"Input    : {t.input}")
        print(f"Output   : {t.output}")
        print(f"Created  : {t.timestamp}")
        if t.session_id:
            print(f"Session  : {t.session_id}")

    return response.data


def fetch_trace_by_id(trace_id):
    """
    Fetch a single trace and all its observations (spans + generations).
    observations = every child span/generation recorded under that trace.
    """
    print(f"\n=== Trace Detail: {trace_id} ===")

    trace = lf_client.fetch_trace(trace_id)

    # Print trace-level info (handle both dict and object responses)
    if hasattr(trace, '__dict__'):
        trace_dict = trace.__dict__
    else:
        trace_dict = trace

    for key in ['id', 'name', 'input', 'output', 'timestamp', 'session_id']:
        if key in trace_dict or hasattr(trace, key):
            val = getattr(trace, key, trace_dict.get(key, "N/A"))
            if val:
                print(f"{key.capitalize():<12}: {str(val)[:100]}")

    # Print observations
    if hasattr(trace, 'observations'):
        observations = trace.observations
    else:
        observations = trace_dict.get('observations', [])

    print(f"\nObservations ({len(observations)}):")

    for obs in observations:
        obs_type = getattr(obs, 'type', obs.get('type', 'unknown')) if hasattr(obs, 'get') else getattr(obs, 'type', 'unknown')
        obs_name = getattr(obs, 'name', obs.get('name', 'unknown')) if hasattr(obs, 'get') else getattr(obs, 'name', 'unknown')

        print(f"\n  [{obs_type}] {obs_name}")

        if hasattr(obs, 'input'):
            print(f"    Input    : {str(obs.input)[:120]}")
        if hasattr(obs, 'output'):
            print(f"    Output   : {str(obs.output)[:120]}")
        if hasattr(obs, 'start_time') and hasattr(obs, 'end_time') and obs.start_time and obs.end_time:
            latency_ms = (obs.end_time - obs.start_time).total_seconds() * 1000
            print(f"    Latency  : {latency_ms:.1f}ms")
        if hasattr(obs, 'model') and obs.model:
            print(f"    Model    : {obs.model}")
        if hasattr(obs, 'usage') and obs.usage:
            print(f"    Usage    : {obs.usage}")

    return trace


def fetch_traces_by_session(session_id):
    """
    Pull all traces that belong to one session.
    Useful to review an entire script run at once.
    """
    print(f"\n=== Traces for Session: {session_id} ===")

    response = lf_client.fetch_traces(session_id=session_id)

    print(f"Found {len(response.data)} traces\n")
    for t in response.data:
        print(f"  {t.name:<20} | input: {str(t.input)[:60]}")

    return response.data


def extract_comprehensive_metrics(trace_id):
    """
    Extract ALL available metrics from a trace:
    - Latencies per span
    - Token usage & costs
    - Scores & feedback
    - Errors & status codes
    - Model info
    - User context
    """
    print(f"\n=== Comprehensive Trace Metrics: {trace_id} ===")

    trace = lf_client.fetch_trace(trace_id)

    # Trace-level metadata
    print("\n[TRACE METADATA]")
    for key in ['id', 'name', 'user_id', 'session_id', 'tags', 'release', 'timestamp']:
        if hasattr(trace, key):
            val = getattr(trace, key)
            if val:
                print(f"  {key}: {val}")

    # Observations with detailed metrics
    print(f"\n[OBSERVATIONS] ({len(trace.observations)} total)")

    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    total_latency_ms = 0

    for obs in trace.observations:
        obs_type = getattr(obs, 'type', 'unknown')
        obs_name = getattr(obs, 'name', 'unknown')

        print(f"\n  • [{obs_type}] {obs_name}")

        # Latency
        if hasattr(obs, 'start_time') and hasattr(obs, 'end_time') and obs.start_time and obs.end_time:
            latency_ms = (obs.end_time - obs.start_time).total_seconds() * 1000
            total_latency_ms += latency_ms
            print(f"    ⏱ Latency: {latency_ms:.1f}ms")

        # Token usage
        if hasattr(obs, 'usage') and obs.usage:
            usage = obs.usage
            if hasattr(usage, 'input'):
                total_input_tokens += usage.input
                print(f"    📥 Input tokens: {usage.input}")
            if hasattr(usage, 'output'):
                total_output_tokens += usage.output
                print(f"    📤 Output tokens: {usage.output}")
            if hasattr(usage, 'cost') and usage.cost:
                total_cost += float(usage.cost)
                print(f"    💰 Cost: ${usage.cost:.6f}")

        # Model info
        if hasattr(obs, 'model') and obs.model:
            print(f"    🤖 Model: {obs.model}")

        # Status/Errors
        if hasattr(obs, 'status_code') and obs.status_code:
            print(f"    ⚠️  Status: {obs.status_code}")
        if hasattr(obs, 'error') and obs.error:
            print(f"    ❌ Error: {obs.error}")

        # Level (DEBUG, WARNING, ERROR)
        if hasattr(obs, 'level') and obs.level:
            print(f"    📊 Level: {obs.level}")

    # Summary
    print(f"\n[SUMMARY]")
    print(f"  Total latency: {total_latency_ms:.1f}ms")
    print(f"  Total input tokens: {total_input_tokens}")
    print(f"  Total output tokens: {total_output_tokens}")
    print(f"  Total cost: ${total_cost:.6f}")


def summarise_retrieval_scores(session_id):
    """
    For each trace in a session, extract the retrieval scores logged
    in the vector_retrieval span and print a summary.

    This is the offline evaluation pattern:
    run queries → fetch traces → score retrieval quality.
    """
    print(f"\n=== Retrieval Score Summary for Session: {session_id} ===")

    traces = lf_client.fetch_traces(session_id=session_id).data

    for t in traces:
        detail = lf_client.fetch_trace(t.id)
        for obs in detail.observations:
            if obs.name == "vector_retrieval" and obs.output:
                chunks = obs.output.get("chunks", [])
                scores = [c["score"] for c in chunks if "score" in c]
                if scores:
                    print(f"\n  Query trace : {t.name}")
                    print(f"  Chunks      : {len(scores)}")
                    print(f"  Top score   : {min(scores):.4f}  (lower = more relevant)")
                    print(f"  Worst score : {max(scores):.4f}")


if __name__ == "__main__":
    print("File 18: Pulling Traces from Langfuse")

    # Option 1: Fetch a specific trace by ID with comprehensive metrics
    trace_id = input("\nPaste a trace ID (or press Enter to skip): ").strip()
    if trace_id:
        fetch_trace_by_id(trace_id)
        extract_comprehensive_metrics(trace_id)

    # Option 2: Pull recent traces
    recent = fetch_recent_traces(limit=5)

    # Option 3: Inspect the most recent trace in detail
    if recent and not trace_id:
        print("\nFetching most recent trace...")
        fetch_trace_by_id(recent[0].id)

    # Option 4: Fetch by session_id
    session_id = input("\nPaste a session_id from file 11 (or press Enter to skip): ").strip()
    if session_id:
        fetch_traces_by_session(session_id)
        summarise_retrieval_scores(session_id)
