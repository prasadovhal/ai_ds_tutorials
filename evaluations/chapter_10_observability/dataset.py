"""
Chapter 10 - LLM Application Observability
Dataset module: Load science questions and generate simulated observability data
(traces, logs, metrics) for a realistic LLM pipeline scenario.
"""

import csv
import json
import os
import random
import math
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


# ---------------------------------------------------------------------------
# 1. DATA LOADING
# ---------------------------------------------------------------------------

def load_sample_data() -> dict:
    """Load the pre-built sample observability data."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load science MCQ questions from train.csv."""
    rows = []
    path = os.path.join(data_dir, "train.csv")
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            rows.append({
                "id": int(row["id"]),
                "prompt": row["prompt"],
                "choices": {
                    "A": row["A"],
                    "B": row["B"],
                    "C": row["C"],
                    "D": row["D"],
                    "E": row["E"],
                },
                "ground_truth": row["answer"],
            })
    return rows


# ---------------------------------------------------------------------------
# 2. TOKEN ESTIMATION
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """
    Estimate token count using the ~4 chars per token heuristic.
    In production, use tiktoken for exact counts.
    """
    return max(1, len(text) // 4)


def estimate_question_tokens(question: dict) -> dict:
    """Estimate input and output tokens for a science question."""
    # Build the full prompt text
    prompt_parts = [
        "You are an expert scientist.",
        "Question: " + question["prompt"],
    ]
    for letter, text in question["choices"].items():
        prompt_parts.append(f"  {letter}: {text}")
    prompt_parts.append("Answer (letter only):")

    full_prompt = "\n".join(prompt_parts)
    input_tokens = estimate_tokens(full_prompt)

    # Output is typically short for MCQ: the letter plus some reasoning
    output_tokens = random.randint(5, 120)

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }


# ---------------------------------------------------------------------------
# 3. SIMULATED LLM PIPELINE RESPONSES
# ---------------------------------------------------------------------------

def simulate_llm_response(question: dict, accuracy: float = 0.72,
                          seed: Optional[int] = None) -> dict:
    """
    Simulate an LLM answering a science question.
    Returns a response dict with answer, confidence, latency, tokens, etc.
    """
    if seed is not None:
        rng = random.Random(seed + question["id"])
    else:
        rng = random.Random()

    # Decide correctness based on target accuracy
    is_correct = rng.random() < accuracy
    choices = list(question["choices"].keys())

    if is_correct:
        predicted = question["ground_truth"]
        confidence = round(rng.uniform(0.75, 0.98), 3)
    else:
        wrong_choices = [c for c in choices if c != question["ground_truth"]]
        predicted = rng.choice(wrong_choices)
        confidence = round(rng.uniform(0.30, 0.75), 3)

    # Simulate latency: most calls are fast, some are slow
    # Log-normal distribution gives realistic tail latency
    base_latency = rng.lognormvariate(math.log(1500), 0.5)
    latency_ms = round(max(400, min(base_latency, 12000)), 1)

    # Token counts
    token_info = estimate_question_tokens(question)

    # Occasionally simulate format errors (response is not just a letter)
    format_ok = rng.random() > 0.04  # 4% format error rate

    return {
        "question_id": question["id"],
        "predicted": predicted,
        "ground_truth": question["ground_truth"],
        "is_correct": is_correct,
        "confidence": confidence,
        "latency_ms": latency_ms,
        "input_tokens": token_info["input_tokens"],
        "output_tokens": token_info["output_tokens"],
        "total_tokens": token_info["total_tokens"],
        "format_ok": format_ok,
        "model": "gpt-4",
        "prompt_version": "v3",
    }


def simulate_pipeline_batch(questions: list[dict], accuracy: float = 0.72,
                            seed: int = 42) -> list[dict]:
    """
    Simulate processing a batch of questions through the LLM pipeline.
    Returns a list of response dicts with full observability data.
    """
    responses = []
    for q in questions:
        resp = simulate_llm_response(q, accuracy=accuracy, seed=seed)
        responses.append(resp)
    return responses


# ---------------------------------------------------------------------------
# 4. TRACE GENERATION
# ---------------------------------------------------------------------------

def generate_trace_for_response(response: dict, base_timestamp: float) -> dict:
    """
    Generate a distributed trace with spans for a single pipeline execution.
    Mimics real OpenTelemetry trace structure.
    """
    trace_id = f"trace-{response['question_id']:04d}"
    total_latency = response["latency_ms"]

    # Break total latency into span durations
    prompt_format_ms = round(random.uniform(5, 25), 1)
    parse_ms = round(random.uniform(8, 30), 1)
    eval_ms = round(random.uniform(10, 50), 1)
    llm_ms = round(total_latency - prompt_format_ms - parse_ms - eval_ms, 1)
    llm_ms = max(llm_ms, 100)

    # Timestamps (in seconds from base)
    t0 = base_timestamp
    t1 = t0 + prompt_format_ms / 1000
    t2 = t1 + llm_ms / 1000
    t3 = t2 + parse_ms / 1000
    t4 = t3 + eval_ms / 1000

    return {
        "trace_id": trace_id,
        "name": "science_qa_pipeline",
        "total_latency_ms": total_latency,
        "status": "SLOW" if total_latency > 3000 else "OK",
        "spans": [
            {
                "span_id": f"{trace_id}-root",
                "parent_span_id": None,
                "name": "pipeline.run",
                "duration_ms": round(total_latency, 1),
                "attributes": {
                    "question_id": response["question_id"],
                    "pipeline_version": "1.0.0",
                },
            },
            {
                "span_id": f"{trace_id}-prompt",
                "parent_span_id": f"{trace_id}-root",
                "name": "prompt.format",
                "duration_ms": prompt_format_ms,
                "attributes": {
                    "prompt_version": response["prompt_version"],
                    "input_tokens": response["input_tokens"],
                },
            },
            {
                "span_id": f"{trace_id}-llm",
                "parent_span_id": f"{trace_id}-root",
                "name": "llm.call",
                "duration_ms": llm_ms,
                "attributes": {
                    "model": response["model"],
                    "input_tokens": response["input_tokens"],
                    "output_tokens": response["output_tokens"],
                    "temperature": 0.0,
                },
            },
            {
                "span_id": f"{trace_id}-parse",
                "parent_span_id": f"{trace_id}-root",
                "name": "response.parse",
                "duration_ms": parse_ms,
                "attributes": {
                    "parsed_answer": response["predicted"],
                    "confidence": response["confidence"],
                    "format_ok": response["format_ok"],
                },
            },
            {
                "span_id": f"{trace_id}-eval",
                "parent_span_id": f"{trace_id}-root",
                "name": "evaluation.check",
                "duration_ms": eval_ms,
                "attributes": {
                    "correct": response["is_correct"],
                    "ground_truth": response["ground_truth"],
                    "predicted": response["predicted"],
                },
            },
        ],
    }


def generate_all_traces(responses: list[dict]) -> list[dict]:
    """Generate traces for all pipeline responses."""
    random.seed(42)
    traces = []
    base_time = 1000.0
    for resp in responses:
        trace = generate_trace_for_response(resp, base_time)
        traces.append(trace)
        base_time += resp["latency_ms"] / 1000 + random.uniform(0.1, 0.5)
    return traces
