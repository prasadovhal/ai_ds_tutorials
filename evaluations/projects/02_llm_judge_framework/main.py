import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv, json, random, os

# --- Optional: requests for Ollama ---
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")
OLLAMA_URL = "http://localhost:11434/api/generate"
NUM_QUESTIONS = 5
CRITERIA = ["correctness", "completeness", "clarity"]

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
        print("[INFO] Ollama not available — using simulated responses")

# ── 1. Load questions ────────────────────────────────────────────────────────
def load_questions(path, n):
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            if len(rows) >= n:
                break
    return rows

# ── 2. Get answer from Ollama (fallback: simulated) ──────────────────────────
def query_ollama(prompt, model="mistral"):
    if not OLLAMA_AVAILABLE:
        return None
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": model, "prompt": prompt, "stream": False
        }, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass
    return None

def get_answer(question_row):
    prompt = question_row["prompt"] + "\nChoices:\n"
    for ch in "ABCDE":
        prompt += f"  {ch}: {question_row[ch]}\n"
    prompt += "Reply with just the letter of the best answer."
    result = query_ollama(prompt)
    if result:
        return result
    # Fallback: simulate a decent answer
    return random.choice(["A", "B", "C", "D", "E"])

def get_bad_answer(question_row):
    """Generate a deliberately wrong answer."""
    correct = question_row["answer"]
    wrong = [l for l in "ABCDE" if l != correct]
    return random.choice(wrong)

# ── 3. Judge an answer (LLM or simulated) ────────────────────────────────────
def judge_answer(question_row, answer_letter):
    """Score an answer on correctness, completeness, clarity (1-5)."""
    judge_prompt = (
        f"Question: {question_row['prompt'][:200]}...\n"
        f"Correct answer: {question_row['answer']}\n"
        f"Given answer: {answer_letter}\n"
        f"Rate the given answer on correctness, completeness, clarity (1-5 each).\n"
        f"Reply as JSON: {{\"correctness\": N, \"completeness\": N, \"clarity\": N}}"
    )
    result = query_ollama(judge_prompt)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            pass
    # Fallback: simulated scoring
    is_correct = (answer_letter == question_row["answer"])
    if is_correct:
        return {c: random.randint(4, 5) for c in CRITERIA}
    else:
        return {c: random.randint(1, 3) for c in CRITERIA}

# ── 4. Pairwise comparison ───────────────────────────────────────────────────
def pairwise_compare(question_row, answer_a, answer_b):
    """Return which answer is better: 'A', 'B', or 'tie'."""
    scores_a = judge_answer(question_row, answer_a)
    scores_b = judge_answer(question_row, answer_b)
    total_a = sum(scores_a.values())
    total_b = sum(scores_b.values())
    if total_a > total_b:
        return "A", scores_a, scores_b
    elif total_b > total_a:
        return "B", scores_a, scores_b
    return "tie", scores_a, scores_b

# ── 5. Inter-judge agreement ─────────────────────────────────────────────────
def compute_agreement(question_row, answer_letter, n_runs=3):
    """Run the judge n_runs times, compute consistency."""
    all_scores = [judge_answer(question_row, answer_letter) for _ in range(n_runs)]
    agreement = {}
    for c in CRITERIA:
        vals = [s[c] for s in all_scores]
        spread = max(vals) - min(vals)
        agreement[c] = 1.0 if spread == 0 else max(0, 1.0 - spread / 4.0)
    agreement["overall"] = sum(agreement.values()) / len(CRITERIA)
    return agreement, all_scores

# ── 6. Main ──────────────────────────────────────────────────────────────────
def main():
    print("Loading questions ...")
    questions = load_questions(DATA_PATH, NUM_QUESTIONS)
    print(f"Loaded {len(questions)} questions\n")

    all_results = []
    for i, q in enumerate(questions):
        print(f"--- Question {i+1} ---")
        print(f"  {q['prompt'][:100]}...")

        # Get good and bad answers
        good_ans = get_answer(q)
        bad_ans = get_bad_answer(q)
        print(f"  Good answer: {good_ans}  |  Bad answer: {bad_ans}  |  Gold: {q['answer']}")

        # Judge the good answer
        score = judge_answer(q, good_ans)
        print(f"  Judge scores (good): {score}")

        # Pairwise comparison
        winner, sa, sb = pairwise_compare(q, good_ans, bad_ans)
        print(f"  Pairwise winner: {'Good' if winner == 'A' else 'Bad' if winner == 'B' else 'Tie'}")
        print(f"    Good scores: {sa}  |  Bad scores: {sb}")

        # Inter-judge agreement
        agreement, multi_scores = compute_agreement(q, good_ans)
        print(f"  Agreement (3 runs): {', '.join(f'{k}={v:.2f}' for k, v in agreement.items())}")

        all_results.append({
            "question_id": q["id"],
            "good_answer": good_ans, "bad_answer": bad_ans, "gold": q["answer"],
            "judge_score": score, "pairwise_winner": winner,
            "agreement": agreement
        })

    # Summary scorecard
    print(f"\n{'='*60}")
    print(f"  SCORECARD SUMMARY")
    print(f"{'='*60}")
    avg_agreement = sum(r["agreement"]["overall"] for r in all_results) / len(all_results)
    pairwise_correct = sum(1 for r in all_results if r["pairwise_winner"] == "A")
    print(f"  Questions evaluated     : {len(all_results)}")
    print(f"  Pairwise (good wins)    : {pairwise_correct}/{len(all_results)}")
    print(f"  Avg inter-judge agree.  : {avg_agreement:.2f}")
    for c in CRITERIA:
        avg = sum(r["judge_score"][c] for r in all_results) / len(all_results)
        print(f"  Avg {c:<14}    : {avg:.2f}/5")

if __name__ == "__main__":
    main()
