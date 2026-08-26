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
from langfuse import Langfuse

load_dotenv()

lf_client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
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

    print(f"Name     : {trace.name}")
    print(f"Input    : {trace.input}")
    print(f"Output   : {trace.output}")
    print(f"\nObservations ({len(trace.observations)}):")

    for obs in trace.observations:
        print(f"\n  [{obs.type}] {obs.name}")
        print(f"    Input    : {str(obs.input)[:120]}")
        print(f"    Output   : {str(obs.output)[:120]}")
        if obs.start_time and obs.end_time:
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

    # 1. Pull recent traces
    recent = fetch_recent_traces(limit=5)

    # 2. Inspect the most recent trace in detail
    if recent:
        fetch_trace_by_id(recent[0].id)

    # 3. If you know a session_id from a file 11 run, pass it here
    #    e.g. session_id = "rag-session-a1b2c3d4"
    session_id = input("\nPaste a session_id from file 11 (or press Enter to skip): ").strip()
    if session_id:
        fetch_traces_by_session(session_id)
        summarise_retrieval_scores(session_id)
