"""
File 13: LangSmith Introduction
Concepts: @traceable decorator, runs, datasets, feedback, fetching runs

LangSmith is an observability platform by LangChain.
Key difference from Langfuse: tracing uses the @traceable decorator
instead of manually creating spans — much less boilerplate.

What this file covers:
1. Setup and connection test
2. @traceable decorator — the primary way to trace
3. Nested traces — parent/child runs
4. Tracing a real Ollama LLM call
5. Creating a dataset
6. Adding feedback to runs
7. Fetching runs back to local Python

Prerequisites:
- pip install langsmith
- LANGSMITH_API_KEY in .env
"""

import os
import time
from dotenv import load_dotenv
import ollama
from langsmith import Client, traceable

load_dotenv()

# Enable tracing and point to your project
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "ai-concepts-tutorial"

client = Client()
ollama_client = ollama.Client()


# ─────────────────────────────────────────────
# 1. Connection Test
# ─────────────────────────────────────────────

def test_connection():
    """Verify API key works and show account info."""
    print("\n=== 1. Connection Test ===")
    try:
        # list_projects confirms auth is working
        projects = list(client.list_projects())
        print(f"Connected. Projects found: {len(projects)}")
        for p in projects[:3]:
            print(f"  - {p.name}")
    except Exception as e:
        print(f"Connection failed: {e}")


# ─────────────────────────────────────────────
# 2. @traceable — simplest tracing
# ─────────────────────────────────────────────
#
# @traceable wraps a function. Every call is automatically logged
# to LangSmith as a "run" — inputs, outputs, duration, errors.
# No manual span start/end needed (unlike Langfuse).

@traceable(name="classify_intent", run_type="chain")
def classify_intent(query: str) -> dict:
    """Simulate intent classification."""
    time.sleep(0.02)
    keywords = ["what", "how", "why", "explain"]
    intent = "factual" if any(k in query.lower() for k in keywords) else "other"
    return {"intent": intent, "confidence": 0.9}


@traceable(name="estimate_complexity", run_type="chain")
def estimate_complexity(query: str) -> int:
    """Simulate complexity scoring."""
    time.sleep(0.01)
    return min(len(query.split()) // 5, 5)


def simple_traceable_example():
    print("\n=== 2. @traceable Decorator ===")

    result = classify_intent("What is photosynthesis?")
    print(f"Intent: {result}")

    complexity = estimate_complexity("What is the mechanism behind DNA replication?")
    print(f"Complexity: {complexity}")

    print("→ View runs at: https://smith.langchain.com/projects/ai-concepts-tutorial")


# ─────────────────────────────────────────────
# 3. Nested Traces — parent/child runs
# ─────────────────────────────────────────────
#
# When a @traceable function calls another @traceable function,
# LangSmith automatically nests them as parent → child runs.
# Same trace_id flows through — no manual linking needed.

@traceable(name="full_pipeline", run_type="chain")
def full_pipeline(query: str) -> dict:
    """
    Calling @traceable functions inside another @traceable
    creates a nested run tree automatically:

    full_pipeline
     ├── classify_intent
     └── estimate_complexity
    """
    intent = classify_intent(query)
    complexity = estimate_complexity(query)
    return {"query": query, "intent": intent, "complexity": complexity}


def nested_trace_example():
    print("\n=== 3. Nested Traces ===")
    result = full_pipeline("How does quantum entanglement work?")
    print(f"Pipeline result: {result}")
    print("→ Check LangSmith UI for nested run tree")


# ─────────────────────────────────────────────
# 4. Tracing a Real LLM Call (Ollama)
# ─────────────────────────────────────────────
#
# run_type="llm" tells LangSmith this is an LLM call.
# LangSmith renders input/output in a chat-friendly format.

@traceable(name="ollama_mistral", run_type="llm")
def call_mistral(system_prompt: str, user_prompt: str) -> str:
    """Traced Ollama call."""
    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response['message']['content']


@traceable(name="science_qa", run_type="chain")
def science_qa(query: str) -> dict:
    """Full Q&A chain — parent run containing the LLM child run."""
    system = "You are a science expert. Answer concisely in 2-3 sentences."
    answer = call_mistral(system, query)
    return {"query": query, "answer": answer}


def llm_trace_example():
    print("\n=== 4. Tracing Real LLM Call ===")
    result = science_qa("What is the role of mitochondria?")
    print(f"Q: {result['query']}")
    print(f"A: {result['answer'][:150]}...")
    print("→ LangSmith shows input/output in chat format under 'science_qa' run")


# ─────────────────────────────────────────────
# 5. Creating a Dataset
# ─────────────────────────────────────────────
#
# Datasets store input/output pairs for evaluation.
# You build a dataset once, then run evals against it repeatedly.

def create_dataset_example():
    print("\n=== 5. Creating a Dataset ===")

    dataset_name = "science_qa_eval"

    # Delete if already exists (for re-running this tutorial)
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        client.delete_dataset(dataset_id=existing.id)
        print("Deleted existing dataset")
    except Exception:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Science Q&A pairs for evaluating RAG answers"
    )

    examples = [
        {
            "inputs":  {"query": "What is photosynthesis?"},
            "outputs": {"answer": "Photosynthesis converts light energy into chemical energy stored as glucose."}
        },
        {
            "inputs":  {"query": "What is the role of mitochondria?"},
            "outputs": {"answer": "Mitochondria produce ATP through cellular respiration — the cell's energy currency."}
        },
        {
            "inputs":  {"query": "What is quantum entanglement?"},
            "outputs": {"answer": "Quantum entanglement links two particles so measuring one instantly affects the other."}
        },
    ]

    client.create_examples(
        inputs=[e["inputs"] for e in examples],
        outputs=[e["outputs"] for e in examples],
        dataset_id=dataset.id
    )

    print(f"Dataset '{dataset_name}' created with {len(examples)} examples")
    print("→ View at: https://smith.langchain.com/datasets")
    return dataset


# ─────────────────────────────────────────────
# 6. Adding Feedback to Runs
# ─────────────────────────────────────────────
#
# Feedback attaches a quality score to a specific run.
# Useful for human review or programmatic scoring.

def feedback_example():
    print("\n=== 6. Adding Feedback to Runs ===")

    # Run something and capture the run_id
    # langsmith_extra={"metadata": ...} passes extra info to the run
    result = science_qa("What is DNA replication?")

    # Fetch the most recent run for this function to get its ID
    runs = list(client.list_runs(
        project_name="ai-concepts-tutorial",
        filter='eq(name, "science_qa")',
        limit=1
    ))

    if runs:
        run = runs[0]
        client.create_feedback(
            run_id=run.id,
            key="correctness",
            score=0.9,
            comment="Answer is accurate and concise"
        )
        print(f"Feedback added to run: {run.id}")
        print(f"Answer was: {result['answer'][:100]}...")
    else:
        print("No runs found yet — run llm_trace_example() first")


# ─────────────────────────────────────────────
# 7. Fetching Runs Back to Local Python
# ─────────────────────────────────────────────
#
# Like Langfuse's fetch_traces(), LangSmith lets you pull
# run data back for offline analysis or reporting.

def fetch_runs_example():
    print("\n=== 7. Fetching Runs Locally ===")

    runs = list(client.list_runs(
        project_name="ai-concepts-tutorial",
        limit=5
    ))

    print(f"Found {len(runs)} recent runs:\n")
    for run in runs:
        duration_ms = (
            (run.end_time - run.start_time).total_seconds() * 1000
            if run.end_time and run.start_time else 0
        )
        print(f"  [{run.run_type}] {run.name}")
        print(f"    Input  : {str(run.inputs)[:80]}")
        print(f"    Output : {str(run.outputs)[:80]}")
        print(f"    Duration: {duration_ms:.0f}ms")
        print()


# ─────────────────────────────────────────────
# Theory moved to: 13_langsmith_vs_langfuse.md
# ─────────────────────────────────────────────
# See markdown for detailed comparison and trade-offs


if __name__ == "__main__":
    print("File 13: LangSmith Introduction")

    test_connection()
    simple_traceable_example()
    nested_trace_example()
    llm_trace_example()
    create_dataset_example()
    feedback_example()
    fetch_runs_example()