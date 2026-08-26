"""
Project 4: Golden Dataset Generator

Generates and validates golden datasets from seed data.
Creates synthetic questions using Ollama (or templates as fallback).
Validates format, detects duplicates, and generates quality reports with versioning.
"""
import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv, json, random, os, hashlib
from collections import Counter
from datetime import datetime

# --- Ollama ---
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset_v1.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
NUM_SYNTHETIC = 5

# Quick check: is Ollama reachable?
import socket, select
OLLAMA_AVAILABLE = False
if HAS_REQUESTS:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        err = s.connect_ex(("127.0.0.1", 11434))
        if err == 0:
            OLLAMA_AVAILABLE = True
        else:
            _, w, _ = select.select([], [s], [], 0.5)
            if w:
                OLLAMA_AVAILABLE = (s.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0)
        s.close()
    except Exception:
        pass
    if not OLLAMA_AVAILABLE:
        print("[INFO] Ollama not available — using template-based generation")

# ── 1. Load seed data ────────────────────────────────────────────────────────
def load_seed(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

# ── 2. Analyze seed data ─────────────────────────────────────────────────────
def analyze_seed(rows):
    answer_dist = Counter(r["answer"] for r in rows)
    prompt_lengths = [len(r["prompt"].split()) for r in rows]
    avg_len = sum(prompt_lengths) / len(prompt_lengths)
    topics = set()
    for r in rows:
        words = r["prompt"].lower().split()
        for kw in ["physics", "biology", "chemistry", "math", "history",
                    "geology", "astronomy", "computer", "engineering", "medical"]:
            if kw in " ".join(words):
                topics.add(kw)
    balance_score = min(answer_dist.values()) / max(answer_dist.values()) if answer_dist else 0
    stats = {
        "total_questions": len(rows),
        "answer_distribution": dict(answer_dist),
        "avg_prompt_length_words": round(avg_len, 1),
        "topics_detected": sorted(topics) if topics else ["general STEM"],
        "balance_score": round(balance_score, 3),
    }
    return stats

# ── 3. Generate synthetic questions ──────────────────────────────────────────
TEMPLATES = [
    ("Which of the following best describes {concept}?",
     "A precise description of {concept}", "A vague description", "An incorrect claim",
     "A partially correct statement", "An unrelated fact"),
    ("What is the primary function of {concept} in {field}?",
     "The correct primary function", "A secondary function described as primary",
     "An incorrect function", "A function of a related concept", "None of the above"),
    ("In the context of {field}, which statement about {concept} is most accurate?",
     "The scientifically accurate statement", "A common misconception",
     "An outdated theory", "A partially correct observation", "An unrelated claim"),
    ("How does {concept} relate to {concept2} in {field}?",
     "The correct relationship", "An inverse relationship",
     "No relationship exists", "A causal relationship that is incorrect", "An indirect link only"),
    ("Which experiment best demonstrates {concept}?",
     "The classic well-known experiment", "A thought experiment only",
     "An experiment from a different field", "A disproven experimental setup",
     "An experiment that tests something else"),
]

CONCEPTS = ["wave-particle duality", "entropy", "mitosis", "catalysis",
            "gravitational lensing", "neural networks", "plate tectonics",
            "quantum entanglement", "photosynthesis", "genetic drift"]
FIELDS = ["physics", "biology", "chemistry", "computer science",
          "geology", "astronomy", "mathematics"]

def generate_with_ollama(seed_row):
    prompt = (
        f"Create a new STEM multiple choice question similar to this one:\n"
        f"{seed_row['prompt'][:200]}...\n"
        f"Format: JSON with keys: prompt, A, B, C, D, E, answer\n"
        f"Reply with ONLY the JSON."
    )
    if OLLAMA_AVAILABLE:
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": "mistral", "prompt": prompt, "stream": False
            }, timeout=30)
            if resp.status_code == 200:
                text = resp.json().get("response", "")
                # Try to extract JSON
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
        except Exception:
            pass
    return None

def generate_template_question(idx):
    template = TEMPLATES[idx % len(TEMPLATES)]
    concept = random.choice(CONCEPTS)
    concept2 = random.choice([c for c in CONCEPTS if c != concept])
    field = random.choice(FIELDS)
    prompt_text = template[0].format(concept=concept, concept2=concept2, field=field)
    choices = list(template[1:])
    for i, c in enumerate(choices):
        choices[i] = c.format(concept=concept, concept2=concept2, field=field)
    # Shuffle choices, track correct answer
    correct_text = choices[0]
    random.shuffle(choices)
    correct_idx = choices.index(correct_text)
    answer_label = "ABCDE"[correct_idx]
    return {
        "prompt": prompt_text,
        "A": choices[0], "B": choices[1], "C": choices[2],
        "D": choices[3], "E": choices[4],
        "answer": answer_label, "source": "template"
    }

def generate_synthetic(seed_rows, n):
    synthetic = []
    for i in range(n):
        # Try Ollama first
        seed = random.choice(seed_rows)
        result = generate_with_ollama(seed)
        if result and all(k in result for k in ["prompt", "A", "B", "C", "D", "E", "answer"]):
            result["source"] = "ollama"
            synthetic.append(result)
        else:
            synthetic.append(generate_template_question(i))
    return synthetic

# ── 4. Validate synthetic questions ──────────────────────────────────────────
def validate(questions, seed_rows):
    issues = []
    valid = []
    seed_prompts = set(r["prompt"][:50] for r in seed_rows)
    seen_prompts = set()

    for i, q in enumerate(questions):
        errs = []
        # Format check
        for key in ["prompt", "A", "B", "C", "D", "E", "answer"]:
            if key not in q or not q[key]:
                errs.append(f"missing field '{key}'")
        if q.get("answer") not in "ABCDE":
            errs.append(f"invalid answer '{q.get('answer')}'")
        # Uniqueness check
        short = q.get("prompt", "")[:50]
        if short in seen_prompts:
            errs.append("duplicate prompt")
        if short in seed_prompts:
            errs.append("too similar to seed data")
        seen_prompts.add(short)

        if errs:
            issues.append({"index": i, "errors": errs})
        else:
            valid.append(q)
    return valid, issues

# ── 5. Build golden dataset ──────────────────────────────────────────────────
def build_golden(seed_rows, synthetic_valid, stats):
    # Use a subset of seed for the golden dataset
    seed_sample = random.sample(seed_rows, min(20, len(seed_rows)))
    entries = []
    for r in seed_sample:
        entry = {k: r[k] for k in ["id", "prompt", "A", "B", "C", "D", "E", "answer"]}
        entry["source"] = "seed"
        entries.append(entry)
    for i, q in enumerate(synthetic_valid):
        q["id"] = f"syn_{i}"
        entries.append(q)

    dataset = {
        "version": "v1",
        "created": datetime.now().isoformat(),
        "total_entries": len(entries),
        "seed_count": len(seed_sample),
        "synthetic_count": len(synthetic_valid),
        "seed_analysis": stats,
        "checksum": hashlib.md5(json.dumps(entries, sort_keys=True).encode()).hexdigest(),
        "entries": entries
    }
    return dataset

# ── 6. Main ──────────────────────────────────────────────────────────────────
def main():
    print("Loading seed data ...")
    seed = load_seed(DATA_PATH)
    print(f"Loaded {len(seed)} seed questions\n")

    # Analyze
    stats = analyze_seed(seed)
    print("=== Seed Data Analysis ===")
    print(f"  Total questions   : {stats['total_questions']}")
    print(f"  Answer distribution: {stats['answer_distribution']}")
    print(f"  Avg prompt length : {stats['avg_prompt_length_words']} words")
    print(f"  Topics detected   : {', '.join(stats['topics_detected'])}")
    print(f"  Balance score     : {stats['balance_score']} (1.0 = perfect)")

    # Generate synthetic
    print(f"\nGenerating {NUM_SYNTHETIC} synthetic questions ...")
    synthetic = generate_synthetic(seed, NUM_SYNTHETIC)
    for i, q in enumerate(synthetic):
        print(f"  [{i+1}] ({q.get('source','?')}) {q['prompt'][:80]}...")

    # Validate
    valid, issues = validate(synthetic, seed)
    print(f"\nValidation: {len(valid)} valid, {len(issues)} issues")
    for iss in issues:
        print(f"  Question {iss['index']}: {', '.join(iss['errors'])}")

    # Build and save
    dataset = build_golden(seed, valid, stats)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"\nGolden dataset saved to {OUTPUT_PATH}")

    # Quality report
    print(f"\n{'='*60}")
    print(f"  DATASET QUALITY REPORT")
    print(f"{'='*60}")
    print(f"  Version           : {dataset['version']}")
    print(f"  Total entries     : {dataset['total_entries']}")
    print(f"  From seed         : {dataset['seed_count']}")
    print(f"  Synthetic         : {dataset['synthetic_count']}")
    print(f"  Checksum (MD5)    : {dataset['checksum']}")
    ans_dist = Counter(e["answer"] for e in dataset["entries"])
    print(f"  Answer balance    : {dict(ans_dist)}")
    src_dist = Counter(e.get("source", "unknown") for e in dataset["entries"])
    print(f"  Source breakdown   : {dict(src_dist)}")

if __name__ == "__main__":
    main()
