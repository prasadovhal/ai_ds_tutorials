"""
Chapter 3 - Modern LLM Evaluation Dimensions
Dataset module: Load and prepare evaluation data from multiple sources.

Provides data loading utilities for:
  - train.csv (199 MCQ science questions)
  - wiki_stem_corpus.csv (Wikipedia STEM text for context-based evaluation)
  - sample_data.json (curated LLM responses showing quality dimensions)
"""

import csv
import json
import os
import random
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "sample_data.json")


# ---------------------------------------------------------------------------
# SAMPLE DATA (curated LLM responses)
# ---------------------------------------------------------------------------

def load_sample_data() -> dict:
    """Load the curated sample data with good/bad LLM responses."""
    with open(SAMPLE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# TRAIN.CSV (MCQ science questions)
# ---------------------------------------------------------------------------

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
# WIKI STEM CORPUS (context passages for faithfulness/groundedness)
# ---------------------------------------------------------------------------

def load_wiki_contexts(
    data_dir: str = DATA_DIR,
    limit: int = 20,
    seed: int = 42,
) -> list[dict]:
    """
    Load a sample of Wikipedia STEM passages from wiki_stem_corpus.csv.

    These serve as 'context' passages for evaluating:
      - Faithfulness: Is the LLM response faithful to this context?
      - Groundedness: Is the response grounded in this context?
      - Hallucination: Did the LLM make up facts not in this context?

    The full corpus has ~4.1M rows; we sample a small subset.
    """
    path = os.path.join(data_dir, "wiki_stem_corpus.csv")
    if not os.path.exists(path):
        # Return synthetic contexts if the file is not available
        return _generate_synthetic_contexts(limit, seed)

    # Read a larger sample then randomly pick from it
    all_rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 500:  # Read first 500 to sample from
                    break
                if len(row.get("text", "").strip()) > 100:
                    all_rows.append({
                        "content_id": row.get("content_id", f"c_{i}"),
                        "page_title": row.get("page_title", "Unknown"),
                        "section_title": row.get("section_title", ""),
                        "text": row.get("text", "").strip(),
                    })
    except Exception:
        return _generate_synthetic_contexts(limit, seed)

    rng = random.Random(seed)
    if len(all_rows) > limit:
        all_rows = rng.sample(all_rows, limit)

    return all_rows


def _generate_synthetic_contexts(limit: int, seed: int) -> list[dict]:
    """Fallback: generate synthetic STEM contexts if wiki corpus unavailable."""
    contexts = [
        {
            "content_id": "synth_001",
            "page_title": "Photosynthesis",
            "section_title": "Overview",
            "text": "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water. In most cases, oxygen is released as a waste product. Most plants, algae, and cyanobacteria perform photosynthesis.",
        },
        {
            "content_id": "synth_002",
            "page_title": "Newton's Laws of Motion",
            "section_title": "First Law",
            "text": "Newton's first law states that every object will remain at rest or in uniform motion in a straight line unless compelled to change its state by the action of an external force. This tendency is called inertia. The first law is often called the law of inertia. It was first formulated by Isaac Newton in his work Principia Mathematica, published in 1687.",
        },
        {
            "content_id": "synth_003",
            "page_title": "DNA",
            "section_title": "Structure",
            "text": "DNA is a molecule composed of two polynucleotide chains that coil around each other to form a double helix. The structure carries genetic instructions for the development, functioning, growth, and reproduction of all known organisms and many viruses. The two DNA strands are known as polynucleotides as they are composed of simpler monomeric units called nucleotides.",
        },
        {
            "content_id": "synth_004",
            "page_title": "Black Hole",
            "section_title": "Formation",
            "text": "A black hole is a region of spacetime where gravity is so strong that nothing, not even light or other electromagnetic waves, has enough energy to escape the event horizon. The theory of general relativity predicts that a sufficiently compact mass can deform spacetime to form a black hole. The boundary of no escape is called the event horizon.",
        },
        {
            "content_id": "synth_005",
            "page_title": "Periodic Table",
            "section_title": "History",
            "text": "The periodic table is a tabular display of the chemical elements organized by atomic number, electron configuration, and recurring chemical properties. The structure of the table shows periodic trends. Dmitri Mendeleev published the first widely recognized periodic table in 1869, developed mainly to illustrate periodic trends in the properties of the then-known elements.",
        },
    ]
    rng = random.Random(seed)
    while len(contexts) < limit:
        base = rng.choice(contexts[:5])
        contexts.append({
            "content_id": f"synth_{len(contexts)+1:03d}",
            "page_title": base["page_title"],
            "section_title": base["section_title"] + " (extended)",
            "text": base["text"],
        })
    return contexts[:limit]


# ---------------------------------------------------------------------------
# SIMULATED LLM RESPONSES
# ---------------------------------------------------------------------------

def generate_simulated_responses(
    contexts: list[dict],
    seed: int = 42,
) -> list[dict]:
    """
    Generate simulated LLM responses for context passages.

    For each context, generates:
      - A faithful response (stays close to the source)
      - A hallucinated response (adds fabricated details)
      - A partially faithful response (some real, some made up)

    In production, these would be actual LLM outputs.
    Here we simulate them heuristically to demonstrate evaluation.
    """
    rng = random.Random(seed)
    results = []

    for ctx in contexts:
        text = ctx["text"]
        title = ctx["page_title"]
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        # Faithful: paraphrase the source by rearranging sentences
        if len(sentences) >= 2:
            faithful = f"{title}: {sentences[-1]}. {sentences[0]}."
        else:
            faithful = f"{title}: {text}"

        # Hallucinated: keep some real info, add made-up details
        hallucination_phrases = [
            f"According to a 2023 study by MIT researchers, {title.lower()} is considered the most important discovery of the century.",
            f"The concept of {title.lower()} was first proposed by Leonardo da Vinci in 1492.",
            f"Recent experiments at CERN have proven that {title.lower()} violates the second law of thermodynamics.",
            f"NASA has confirmed that {title.lower()} plays a critical role in dark matter formation.",
            f"A groundbreaking paper in Nature (2024) showed that {title.lower()} can be observed at temperatures below 4 Kelvin.",
        ]
        hallucinated_detail = rng.choice(hallucination_phrases)
        if sentences:
            hallucinated = f"{sentences[0]}. {hallucinated_detail}"
        else:
            hallucinated = hallucinated_detail

        # Partially faithful: one real sentence + one hallucinated
        partial = f"{sentences[0] if sentences else text}. Additionally, this phenomenon was independently discovered by three separate teams in Antarctica in 1998."

        results.append({
            "context_id": ctx["content_id"],
            "page_title": title,
            "source_text": text,
            "faithful_response": faithful,
            "hallucinated_response": hallucinated,
            "partial_response": partial,
        })

    return results


# ---------------------------------------------------------------------------
# PRODUCTION-LIKE EVALUATION DATASET
# ---------------------------------------------------------------------------

def build_evaluation_dataset(
    n_questions: int = 20,
    seed: int = 42,
) -> dict:
    """
    Build a complete evaluation dataset combining:
      - MCQ questions from train.csv
      - Wiki contexts for faithfulness testing
      - Simulated good/bad LLM responses

    Returns a dict ready for comprehensive multi-dimension evaluation.
    """
    questions = load_train_data(limit=n_questions)
    contexts = load_wiki_contexts(limit=10, seed=seed)
    simulated = generate_simulated_responses(contexts, seed=seed)
    sample = load_sample_data()

    return {
        "mcq_questions": questions,
        "wiki_contexts": contexts,
        "simulated_responses": simulated,
        "curated_examples": sample,
        "summary": {
            "n_mcq_questions": len(questions),
            "n_wiki_contexts": len(contexts),
            "n_simulated_responses": len(simulated),
            "dimensions_covered": [
                "correctness", "relevance", "helpfulness", "completeness",
                "consistency", "hallucination", "faithfulness", "groundedness",
                "instruction_following", "fluency", "coherence", "safety",
                "toxicity", "bias", "creativity", "readability", "reasoning",
            ],
        },
    }


def simulate_mcq_predictions(
    questions: list[dict],
    accuracy: float = 0.7,
    seed: int = 42,
) -> list[str]:
    """Simulate model predictions for MCQ questions at a given accuracy."""
    rng = random.Random(seed)
    predictions = []
    choices = ["A", "B", "C", "D", "E"]
    for q in questions:
        if rng.random() < accuracy:
            predictions.append(q["ground_truth"])
        else:
            wrong = [c for c in choices if c != q["ground_truth"]]
            predictions.append(rng.choice(wrong))
    return predictions


# ---------------------------------------------------------------------------
# MODULE SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("CHAPTER 3 DATASET MODULE - Quick Test")
    print("=" * 60)

    train = load_train_data(limit=5)
    print(f"\nLoaded {len(train)} training questions")
    print(f"First question: {train[0]['prompt'][:80]}...")

    contexts = load_wiki_contexts(limit=5)
    print(f"\nLoaded {len(contexts)} wiki contexts")
    for ctx in contexts[:3]:
        print(f"  - {ctx['page_title']}: {ctx['text'][:60]}...")

    simulated = generate_simulated_responses(contexts[:3])
    print(f"\nGenerated {len(simulated)} simulated response sets")
    for sim in simulated[:2]:
        print(f"  - {sim['page_title']}:")
        print(f"    Faithful: {sim['faithful_response'][:60]}...")
        print(f"    Hallucinated: {sim['hallucinated_response'][:60]}...")

    sample = load_sample_data()
    print(f"\nSample data keys: {list(sample.keys())}")

    dataset = build_evaluation_dataset(n_questions=10)
    print(f"\nFull evaluation dataset:")
    for k, v in dataset["summary"].items():
        print(f"  {k}: {v}")
