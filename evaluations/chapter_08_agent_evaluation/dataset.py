"""
Chapter 8: Agent Evaluation - Dataset Module
Loads sample agent traces and generates additional test data for evaluation.
"""

import json
import os
import random
import copy

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def load_sample_data(path=None):
    """Load the sample_data.json file and return the parsed dict."""
    if path is None:
        path = os.path.join(DATA_DIR, "sample_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_agent_traces(data=None):
    """Return the list of single-agent traces."""
    if data is None:
        data = load_sample_data()
    return data["agent_traces"]


def get_multi_agent_traces(data=None):
    """Return multi-agent collaboration traces."""
    if data is None:
        data = load_sample_data()
    return data["multi_agent_traces"]


def get_coding_agent_traces(data=None):
    """Return coding-agent traces."""
    if data is None:
        data = load_sample_data()
    return data["coding_agent_traces"]


def get_browser_agent_traces(data=None):
    """Return browser-agent traces."""
    if data is None:
        data = load_sample_data()
    return data["browser_agent_traces"]


def get_tools_catalog(data=None):
    """Return the tools catalog dict."""
    if data is None:
        data = load_sample_data()
    return data["tools_catalog"]


# ---------------------------------------------------------------------------
# Synthetic trace generator
# ---------------------------------------------------------------------------

TOOL_NAMES = [
    "search_knowledge_base", "calculate", "lookup_formula",
    "verify_answer", "ask_human",
]

REASONING_QUALITIES = [
    "focused_and_relevant", "thorough_verification", "vague_result",
    "wrong_tool_for_task", "jumped_to_conclusion", "decisive",
]


def generate_synthetic_trace(
    trace_id="synth_001",
    trace_type="synthetic",
    num_steps=None,
    goal_achieved=None,
    task_completed=None,
    seed=None,
):
    """Generate a single synthetic agent trace for testing evaluators.

    Parameters control the characteristics of the generated trace.
    Randomised values are used for anything left as None.
    """
    rng = random.Random(seed)

    if num_steps is None:
        num_steps = rng.randint(2, 7)
    if goal_achieved is None:
        goal_achieved = rng.random() > 0.3
    if task_completed is None:
        task_completed = goal_achieved or rng.random() > 0.5

    steps = []
    tool_calls_count = 0
    unnecessary = 0
    corrections = 0

    for i in range(1, num_steps + 1):
        is_final = i == num_steps
        tool = None if is_final else rng.choice(TOOL_NAMES)
        quality = rng.choice(REASONING_QUALITIES)

        step = {
            "step": i,
            "thought": f"Synthetic thought for step {i}.",
            "action": "final_answer" if is_final else tool,
            "tool_call": None if is_final else {
                "tool": tool,
                "arguments": {"query": f"synthetic query {i}"},
            },
            "observation": None if is_final else f"Synthetic observation {i}.",
            "reasoning_quality": quality,
        }
        steps.append(step)

        if not is_final:
            tool_calls_count += 1
        if quality in ("vague_result", "wrong_tool_for_task"):
            unnecessary += 1
        if "correction" in quality:
            corrections += 1

    choices = {ch: f"Option {ch}" for ch in "ABCDE"}
    correct = rng.choice("ABCDE")
    answer = correct if goal_achieved else rng.choice([c for c in "ABCDE" if c != correct])

    trace = {
        "trace_id": trace_id,
        "trace_type": trace_type,
        "question_id": rng.randint(100, 999),
        "goal": "Synthetic goal for testing evaluators",
        "question": "Synthetic question?",
        "choices": choices,
        "ground_truth": correct,
        "plan": [f"Plan step {j}" for j in range(1, rng.randint(2, 5))],
        "steps": steps,
        "final_answer": answer,
        "total_tool_calls": tool_calls_count,
        "total_steps": num_steps,
        "task_completed": task_completed,
        "goal_achieved": goal_achieved,
        "self_corrections": corrections,
        "unnecessary_steps": unnecessary,
        "total_latency_ms": rng.randint(100, 2000),
        "total_cost": round(rng.uniform(0.5, 6.0), 2),
    }
    return trace


def generate_synthetic_batch(n=10, seed=42):
    """Generate a batch of n synthetic traces."""
    traces = []
    for i in range(n):
        traces.append(generate_synthetic_trace(
            trace_id=f"synth_{i+1:03d}",
            seed=seed + i,
        ))
    return traces


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data = load_sample_data()
    print(f"Loaded {len(data['agent_traces'])} agent traces")
    print(f"Loaded {len(data['multi_agent_traces'])} multi-agent traces")
    print(f"Loaded {len(data['coding_agent_traces'])} coding-agent traces")
    print(f"Loaded {len(data['browser_agent_traces'])} browser-agent traces")

    batch = generate_synthetic_batch(5)
    print(f"\nGenerated {len(batch)} synthetic traces")
    for t in batch:
        print(f"  {t['trace_id']}: steps={t['total_steps']}, "
              f"goal_achieved={t['goal_achieved']}")
