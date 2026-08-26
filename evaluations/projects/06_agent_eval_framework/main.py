"""
Project 6: Agent Evaluation Framework

Evaluates simulated agent traces across task completion, planning quality, tool correctness,
and answer accuracy. Computes individual metrics and runs Elo tournament ranking.
"""
import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import random

# === Define 3 simulated agent traces ===
# Each step: (thought, tool, tool_input, observation, final_answer_or_None)
def S(thought, tool, inp, obs, ans=None):
    return {"thought": thought, "tool": tool, "tool_input": inp, "observation": obs, "final_answer": ans}

TRACES = [
    {"name": "AlphaAgent", "ground_truth": "Paris", "optimal_steps": 2, "steps": [
        S("Need the capital of France.", "knowledge_base", "capital of France", "France's capital is Paris."),
        S("Got the answer.", "none", "", "", "Paris"),
    ]},
    {"name": "BetaAgent", "ground_truth": "Paris", "optimal_steps": 2, "steps": [
        S("Search the web first.", "web_search", "France info", "France is a country in Europe."),
        S("Not direct enough, try again.", "web_search", "France capital city", "The capital is Paris."),
        S("Verify with calculator.", "calculator", "verify Paris", "Error: not a math query."),
        S("Have enough info.", "none", "", "", "Paris"),
    ]},
    {"name": "GammaAgent", "ground_truth": "Paris", "optimal_steps": 2, "steps": [
        S("I think I know this.", "calculator", "capital of France", "Error: not a math query."),
        S("Try calculator again.", "calculator", "France = ?", "Error: invalid expression."),
        S("Calculator broken, search.", "web_search", "France", "France is a European country."),
        S("Guess based on what I know.", "none", "", "", "Lyon"),
        S("Try once more.", "web_search", "capital France", "Paris is the capital."),
        S("Already answered, sticking.", "none", "", "", "Lyon"),
    ]},
]

CORRECT_TOOLS = {"knowledge_base", "web_search"}

# === Evaluate each trace ===
print("=" * 75)
print("AGENT EVALUATION FRAMEWORK")
print("=" * 75)

def evaluate_trace(trace):
    steps = trace["steps"]
    gt, optimal = trace["ground_truth"], trace["optimal_steps"]
    # 1. Task completion
    finals = [s["final_answer"] for s in steps if s["final_answer"] is not None]
    completion = 1.0 if finals else 0.0
    # 2. Tool efficiency
    efficiency = min(1.0, optimal / len(steps)) if steps else 0.0
    # 3. Tool correctness
    tool_uses = [s for s in steps if s["tool"] != "none"]
    correctness = sum(1 for s in tool_uses if s["tool"] in CORRECT_TOOLS) / len(tool_uses) if tool_uses else 0.0
    # 4. Answer accuracy
    answer = finals[-1] if finals else ""
    accuracy = 1.0 if answer.strip().lower() == gt.strip().lower() else 0.0
    # 5. Trajectory score
    trajectory = 0.30 * completion + 0.20 * efficiency + 0.20 * correctness + 0.30 * accuracy
    return {"name": trace["name"], "completion": completion, "efficiency": efficiency,
            "tool_correctness": correctness, "accuracy": accuracy, "trajectory": trajectory,
            "steps_taken": len(steps), "final_answer": answer}

results = []
for trace in TRACES:
    r = evaluate_trace(trace)
    results.append(r)
    print(f"\n--- {r['name']} ---")
    print(f"  Steps taken:       {r['steps_taken']}  (optimal: {trace['optimal_steps']})")
    print(f"  Final answer:      '{r['final_answer']}'  (ground truth: '{trace['ground_truth']}')")
    print(f"  Task completion:   {r['completion']:.2f}")
    print(f"  Tool efficiency:   {r['efficiency']:.2f}")
    print(f"  Tool correctness:  {r['tool_correctness']:.2f}")
    print(f"  Answer accuracy:   {r['accuracy']:.2f}")
    print(f"  Trajectory score:  {r['trajectory']:.2f}")

# === Elo Tournament ===
print("\n" + "=" * 75)
print("ELO TOURNAMENT (pairwise comparisons)")
print("=" * 75)

K = 32
elo = {r["name"]: 1500.0 for r in results}
random.seed(42)

def expected(ra, rb):
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))

def match(a, b):
    sa = a["trajectory"] + random.uniform(-0.05, 0.05)
    sb = b["trajectory"] + random.uniform(-0.05, 0.05)
    return (1.0, 0.0) if sa > sb else ((0.0, 1.0) if sb > sa else (0.5, 0.5))

ROUNDS = 10
print(f"\nRunning {ROUNDS} rounds of round-robin matches...\n")
for _ in range(ROUNDS):
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            a, b = results[i], results[j]
            sa, sb = match(a, b)
            ea = expected(elo[a["name"]], elo[b["name"]])
            elo[a["name"]] += K * (sa - ea)
            elo[b["name"]] += K * (sb - (1.0 - ea))

# === Leaderboard ===
print("=" * 75)
print("FINAL LEADERBOARD")
print("=" * 75)
ranked = sorted(results, key=lambda r: elo[r["name"]], reverse=True)

print(f"\n{'Rank':<6}{'Agent':<15}{'Elo':>8}{'Traj':>8}{'Acc':>7}{'Eff':>7}{'Steps':>7}")
print("-" * 58)
for rank, ag in enumerate(ranked, 1):
    bl = int(ag["trajectory"] * 20)
    bar = "#" * bl + "." * (20 - bl)
    print(f"  {rank:<4}{ag['name']:<15}{elo[ag['name']]:>8.1f}{ag['trajectory']:>7.2f}{ag['accuracy']:>7.2f}{ag['efficiency']:>7.2f}{ag['steps_taken']:>6}")
    print(f"       [{bar}]")

# === Score breakdown ===
print("\n" + "=" * 75)
print("SCORE BREAKDOWN")
print("=" * 75)
for metric in ["completion", "efficiency", "tool_correctness", "accuracy", "trajectory"]:
    print(f"\n  {metric}:")
    for ag in ranked:
        v = ag[metric]
        print(f"    {ag['name']:<15} {'=' * int(v * 30):<30} {v:.2f}")

# === Langfuse Tracing ===
print("\n" + "=" * 75)
print("LANGFUSE TRACING")
print("=" * 75)
try:
    from langfuse import Langfuse
    import os, sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

    langfuse = Langfuse(
        secret_key=LANGFUSE_SECRET_KEY,
        public_key=LANGFUSE_PUBLIC_KEY,
        host=LANGFUSE_BASE_URL,
    )
    trace = langfuse.trace(name="project6-agent-eval-elo")

    for ag in ranked:
        span = trace.span(
            name=ag["name"],
            input={"steps_taken": ag["steps_taken"], "final_answer": ag["final_answer"]},
            output={"elo": round(elo[ag["name"]], 1)},
        )
        span.score(name="trajectory", value=ag["trajectory"])
        span.score(name="accuracy", value=ag["accuracy"])
        span.score(name="efficiency", value=ag["efficiency"])
        span.score(name="elo_rating", value=elo[ag["name"]] / 2000.0)
        span.end()

    langfuse.flush()
    print(f"  {len(ranked)} agent traces sent. View at https://cloud.langfuse.com")
except Exception as e:
    print(f"  Langfuse not available ({e}), skipping.")

print("\nDone.")
