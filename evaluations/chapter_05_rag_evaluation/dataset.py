"""
Chapter 5 - RAG Evaluation
Dataset module: Load and prepare RAG evaluation data.

This module loads science questions from train.csv and creates simulated
RAG pipeline outputs (queries, retrieved contexts, generated answers)
for evaluation. In a real system, these would come from an actual RAG
pipeline; here we simulate them to focus on evaluation methodology.
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
# 1. LOAD RAG SAMPLE DATA
# ---------------------------------------------------------------------------

def load_sample_data() -> dict:
    """Load pre-built RAG evaluation examples from sample_data.json."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_rag_examples() -> list[dict]:
    """Load RAG examples as a flat list for evaluation."""
    data = load_sample_data()
    return data["rag_examples"]


# ---------------------------------------------------------------------------
# 2. LOAD TRAIN DATA (Science Questions)
# ---------------------------------------------------------------------------

def load_train_data(data_dir: str = DATA_DIR, limit: Optional[int] = None) -> list[dict]:
    """Load MCQ science questions from train.csv."""
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
# 3. SIMULATED KNOWLEDGE BASE (from wiki_stem_corpus.csv style)
# ---------------------------------------------------------------------------

# These are representative STEM passages mimicking wiki_stem_corpus.csv format.
# In production, you would retrieve from the actual 4.1M-row corpus.

SIMULATED_CORPUS = [
    {
        "content_id": "sim_001",
        "page_title": "Diffraction",
        "section_title": "Single-slit diffraction",
        "text": "The angular spacing of features in a diffraction pattern is inversely "
                "proportional to the dimensions of the object causing the diffraction. "
                "Thus, narrower slits produce broader diffraction patterns."
    },
    {
        "content_id": "sim_002",
        "page_title": "Gauss's law",
        "section_title": "Integral form",
        "text": "Gauss's law states that the net electric flux through any closed surface "
                "is proportional to the enclosed electric charge. The law is most useful "
                "for calculating electric fields when the charge distribution has spherical, "
                "cylindrical, or planar symmetry."
    },
    {
        "content_id": "sim_003",
        "page_title": "Roche limit",
        "section_title": "Summary",
        "text": "The Roche limit is the distance within which a celestial body held "
                "together only by its own gravity will disintegrate due to tidal forces "
                "from a more massive body exceeding the satellite's self-gravitation."
    },
    {
        "content_id": "sim_004",
        "page_title": "Butterfly effect",
        "section_title": "Definition",
        "text": "In chaos theory, the butterfly effect is the sensitive dependence on "
                "initial conditions in which a small change in one state of a deterministic "
                "nonlinear system can result in large differences in a later state."
    },
    {
        "content_id": "sim_005",
        "page_title": "Black-body radiation",
        "section_title": "Ultraviolet catastrophe",
        "text": "The ultraviolet catastrophe was the prediction of classical physics that "
                "an ideal black body at thermal equilibrium would emit unbounded energy "
                "as wavelength decreases. This was resolved by Planck's quantum hypothesis."
    },
    {
        "content_id": "sim_006",
        "page_title": "Leidenfrost effect",
        "section_title": "Summary",
        "text": "The Leidenfrost effect is a phenomenon where a liquid near a surface "
                "much hotter than its boiling point produces an insulating vapor layer "
                "that keeps it from boiling rapidly, causing droplets to hover."
    },
    {
        "content_id": "sim_007",
        "page_title": "Spin valve",
        "section_title": "Blocking temperature",
        "text": "A spin valve consists of magnetic layers whose electrical resistance "
                "changes depending on relative magnetization alignment, a result of "
                "the giant magnetoresistance effect."
    },
    {
        "content_id": "sim_008",
        "page_title": "Gravitoelectromagnetism",
        "section_title": "Summary",
        "text": "In general relativity, gravitomagnetism refers to analogies between "
                "electromagnetism and relativistic gravitation. Gravitomagnetic effects "
                "arise from the motion or rotation of massive objects."
    },
    {
        "content_id": "sim_009",
        "page_title": "Propagation constant",
        "section_title": "Definition",
        "text": "The propagation constant of a sinusoidal electromagnetic wave is a "
                "complex quantity. The real part is the attenuation constant and the "
                "imaginary part is the phase constant."
    },
    {
        "content_id": "sim_010",
        "page_title": "Dynamic scaling",
        "section_title": "Self-similar systems",
        "text": "Dynamic scaling describes the evolution of self-similar systems where "
                "data from snapshots at fixed times shows similarity to data from "
                "snapshots at other times, tested by time-dependent stochastic variables."
    },
]


# ---------------------------------------------------------------------------
# 4. SIMULATE RAG PIPELINE OUTPUTS
# ---------------------------------------------------------------------------

def simulate_retrieval(
    query: str,
    corpus: list[dict] = None,
    top_k: int = 4,
    noise_ratio: float = 0.3,
    seed: int = 42,
) -> list[dict]:
    """
    Simulate a retrieval step: returns top_k passages with some relevant
    and some noise (irrelevant) passages to mimic real retrieval quality.

    In production, this would be a vector similarity search over embeddings.
    Here we use keyword overlap as a simple proxy.
    """
    if corpus is None:
        corpus = SIMULATED_CORPUS

    rng = random.Random(seed)
    query_words = set(query.lower().split())

    scored = []
    for doc in corpus:
        doc_words = set(doc["text"].lower().split())
        overlap = len(query_words & doc_words)
        scored.append((overlap, doc))

    scored.sort(key=lambda x: -x[0])

    results = []
    for rank, (score, doc) in enumerate(scored[:top_k], 1):
        is_noise = rng.random() < noise_ratio and rank > 1
        results.append({
            "chunk_id": f"ret_{doc['content_id']}",
            "text": doc["text"],
            "source": doc["page_title"],
            "rank": rank,
            "retrieval_score": round(score / max(len(query_words), 1), 4),
            "relevance_label": 0 if is_noise else (1 if score > 0 else 0),
        })

    return results


def simulate_generation(
    query: str,
    contexts: list[dict],
    quality: str = "good",
    seed: int = 42,
) -> dict:
    """
    Simulate a generation step: creates an answer from retrieved contexts.

    quality options:
      - "good": Faithful answer grounded in contexts
      - "partial": Mostly grounded but adds some unverifiable claims
      - "hallucinated": Fabricates information not in contexts
      - "irrelevant": Does not address the query
    """
    rng = random.Random(seed)

    relevant_texts = [c["text"] for c in contexts if c.get("relevance_label", 0) == 1]
    all_texts = [c["text"] for c in contexts]

    if quality == "good" and relevant_texts:
        # Use first two relevant passages
        answer = " ".join(relevant_texts[:2])
        citations = [i + 1 for i, c in enumerate(contexts)
                     if c.get("relevance_label", 0) == 1][:2]
        has_hallucination = False
    elif quality == "partial" and all_texts:
        answer = all_texts[0] + " Additionally, this phenomenon was first described in 1847 by an unnamed researcher."
        citations = [1]
        has_hallucination = True
    elif quality == "hallucinated":
        answer = ("According to recent studies published in Nature, this concept "
                  "was completely disproven in 2023 by researchers at MIT who showed "
                  "that the underlying assumptions were flawed.")
        citations = []
        has_hallucination = True
    else:
        answer = "I cannot determine the answer from the available context."
        citations = []
        has_hallucination = False

    return {
        "generated_answer": answer,
        "citations": citations,
        "has_hallucination": has_hallucination,
        "quality": quality,
    }


def build_rag_evaluation_dataset(
    num_examples: int = 10,
    seed: int = 42,
) -> list[dict]:
    """
    Build a complete RAG evaluation dataset by:
    1. Loading science questions from train.csv
    2. Simulating retrieval from knowledge base
    3. Simulating answer generation
    4. Including ground truth for evaluation

    Returns a list of dicts, each with:
      - query, ground_truth_answer, retrieved_contexts,
        generated_answer, citations, quality_label
    """
    questions = load_train_data(limit=num_examples)
    rng = random.Random(seed)

    quality_distribution = ["good"] * 6 + ["partial"] * 2 + ["hallucinated"] * 1 + ["irrelevant"] * 1
    rng.shuffle(quality_distribution)

    dataset = []
    for i, q in enumerate(questions):
        quality = quality_distribution[i % len(quality_distribution)]

        # Use the question prompt as the query
        query = q["prompt"]

        # Simulate retrieval
        contexts = simulate_retrieval(
            query=query,
            top_k=4,
            noise_ratio=0.3 if quality != "hallucinated" else 0.8,
            seed=seed + i,
        )

        # Simulate generation
        gen_result = simulate_generation(
            query=query,
            contexts=contexts,
            quality=quality,
            seed=seed + i,
        )

        # Ground truth from the MCQ answer
        correct_key = q["ground_truth"]
        ground_truth_text = q["choices"].get(correct_key, "")

        dataset.append({
            "id": q["id"],
            "query": query,
            "ground_truth_answer": ground_truth_text,
            "correct_option": correct_key,
            "retrieved_contexts": contexts,
            "generated_answer": gen_result["generated_answer"],
            "citations": gen_result["citations"],
            "quality_label": quality,
            "has_hallucination": gen_result["has_hallucination"],
        })

    return dataset


# ---------------------------------------------------------------------------
# 5. UTILITY: FLATTEN RAG EXAMPLE FOR METRICS
# ---------------------------------------------------------------------------

def extract_for_retrieval_eval(example: dict) -> dict:
    """Extract fields needed for retrieval evaluation."""
    return {
        "query": example["query"],
        "retrieved_texts": [c["text"] for c in example["retrieved_contexts"]],
        "relevance_labels": [c.get("relevance_label", 0) for c in example["retrieved_contexts"]],
        "ranks": [c["rank"] for c in example["retrieved_contexts"]],
        "sources": [c.get("source", "") for c in example["retrieved_contexts"]],
    }


def extract_for_generation_eval(example: dict) -> dict:
    """Extract fields needed for generation evaluation."""
    return {
        "query": example["query"],
        "generated_answer": example["generated_answer"],
        "ground_truth_answer": example["ground_truth_answer"],
        "context_texts": [c["text"] for c in example["retrieved_contexts"]],
        "citations": example.get("citations", []),
        "has_hallucination": example.get("has_hallucination", False),
    }


# ---------------------------------------------------------------------------
# 6. MODULE SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("DATASET MODULE - RAG Evaluation Data Quick Test")
    print("=" * 60)

    # Test sample data loading
    sample = load_sample_data()
    print(f"\nLoaded {len(sample['rag_examples'])} RAG examples from sample_data.json")
    ex = sample["rag_examples"][0]
    print(f"  Example 0 query: {ex['query'][:60]}...")
    print(f"  Retrieved contexts: {len(ex['retrieved_contexts'])}")
    print(f"  Quality label: {ex['quality_label']}")

    # Test building evaluation dataset
    dataset = build_rag_evaluation_dataset(num_examples=5)
    print(f"\nBuilt evaluation dataset with {len(dataset)} examples")
    for d in dataset:
        print(f"  ID={d['id']}: quality={d['quality_label']}, "
              f"contexts={len(d['retrieved_contexts'])}, "
              f"hallucination={d['has_hallucination']}")

    # Test extraction helpers
    ret_data = extract_for_retrieval_eval(dataset[0])
    gen_data = extract_for_generation_eval(dataset[0])
    print(f"\nRetrieval eval fields: {list(ret_data.keys())}")
    print(f"Generation eval fields: {list(gen_data.keys())}")
