import sys, io
if sys.stdout.encoding != "utf-8" and hasattr(sys.stdout, "buffer"): sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os, json, random, hashlib
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    pd = None
    print("[WARN] pandas not installed. Install with: pip install pandas")

try:
    import requests
except ImportError:
    requests = None


def load_data(path, nrows=None):
    """Load CSV data into a DataFrame."""
    if pd is None:
        raise ImportError("pandas is required")
    return pd.read_csv(path, nrows=nrows)


def create_golden_set(df, n=30):
    """Create a stratified sample of n questions from the dataset."""
    if n >= len(df):
        return df.copy().reset_index(drop=True)
    # Stratify by answer column
    if "answer" in df.columns:
        groups = df.groupby("answer")
        per_group = max(1, n // len(groups))
        samples = []
        for _, group in groups:
            take = min(per_group, len(group))
            samples.append(group.sample(n=take, random_state=42))
        result = pd.concat(samples).head(n).reset_index(drop=True)
        return result
    return df.sample(n=n, random_state=42).reset_index(drop=True)


def generate_synthetic(n=5):
    """Generate synthetic questions using Ollama; fallback to templates."""
    templates = [
        {"prompt": "What is the primary function of mitochondria in cells?",
         "A": "Protein synthesis", "B": "Energy production via ATP",
         "C": "DNA replication", "D": "Cell division", "E": "Waste removal",
         "answer": "B"},
        {"prompt": "Which planet has the strongest magnetic field?",
         "A": "Earth", "B": "Mars", "C": "Jupiter",
         "D": "Saturn", "E": "Venus", "answer": "C"},
        {"prompt": "What is the speed of light in vacuum approximately?",
         "A": "3 x 10^6 m/s", "B": "3 x 10^8 m/s", "C": "3 x 10^10 m/s",
         "D": "3 x 10^12 m/s", "E": "3 x 10^4 m/s", "answer": "B"},
    ]
    # Try Ollama
    if requests:
        try:
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": (
                    "Generate a multiple choice science question with options "
                    "A-E and answer. Return JSON with keys: prompt,A,B,C,D,E,answer"
                ), "stream": False}, timeout=10)
            if resp.status_code == 200:
                data = json.loads(resp.json().get("response", "{}"))
                if "prompt" in data:
                    return [data] * n
        except Exception:
            pass
    # Fallback: cycle through templates
    return [templates[i % len(templates)] for i in range(n)]


def version_dataset(df, version="v1.0"):
    """Create a versioned snapshot of the dataset with metadata."""
    content = df.to_csv(index=False)
    checksum = hashlib.md5(content.encode()).hexdigest()
    return {
        "version": version,
        "num_samples": len(df),
        "columns": list(df.columns),
        "checksum": checksum,
        "created_at": datetime.now().isoformat(),
    }


def get_stats(df):
    """Get basic statistics about the dataset."""
    stats = {"num_rows": len(df), "columns": list(df.columns)}
    if "answer" in df.columns:
        stats["answer_distribution"] = df["answer"].value_counts().to_dict()
    if "prompt" in df.columns:
        lengths = df["prompt"].str.len()
        stats["avg_prompt_length"] = round(float(lengths.mean()), 1)
    return stats
