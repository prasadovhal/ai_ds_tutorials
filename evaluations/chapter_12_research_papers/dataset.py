"""
dataset.py - Data loaders for Chapter 12: Research Papers on LLM Evaluation.
Loads sample_data.json (paper-specific examples) and train.csv (MCQA benchmark).
"""

import json
import csv
import os


def load_sample_data(path=None):
    """Load sample_data.json containing paper-specific evaluation examples."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "sample_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_train_csv(path=None, limit=None):
    """Load train.csv MCQA dataset. Returns list of dicts with keys: id, prompt, A-E, answer."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "train.csv")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            rows.append(row)
    return rows


def get_mt_bench_conversations(data):
    """Extract MT-Bench multi-turn conversations."""
    return data.get("mt_bench_conversations", [])


def get_position_bias_examples(data):
    """Extract position bias test pairs."""
    return data.get("position_bias_examples", [])


def get_geval_examples(data):
    """Extract G-Eval summarization examples."""
    return data.get("g_eval_examples", [])


def get_rag_examples(data):
    """Extract RAG evaluation examples."""
    return data.get("rag_evaluation_examples", [])


def get_agent_examples(data):
    """Extract agent evaluation trajectories."""
    return data.get("agent_evaluation_examples", [])


def get_reflexion_examples(data):
    """Extract Reflexion self-improvement examples."""
    return data.get("reflexion_examples", [])


def get_calibration_examples(data):
    """Extract calibration/judge reliability examples."""
    return data.get("calibration_examples", [])


def get_swe_bench_examples(data):
    """Extract SWE-Bench code repair examples."""
    return data.get("swe_bench_examples", [])


def get_meta_evaluation_examples(data):
    """Extract meta-evaluation (evaluator comparison) examples."""
    return data.get("meta_evaluation_examples", [])


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    data = load_sample_data()
    print(f"Sample data keys: {list(data.keys())}")
    for key, val in data.items():
        print(f"  {key}: {len(val)} items")

    rows = load_train_csv(limit=5)
    print(f"\nTrain CSV: loaded {len(rows)} rows (limit=5)")
    if rows:
        print(f"  Columns: {list(rows[0].keys())}")
        print(f"  First prompt (truncated): {rows[0]['prompt'][:80]}...")
