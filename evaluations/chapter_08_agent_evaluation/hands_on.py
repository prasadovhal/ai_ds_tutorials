"""
Chapter 8: Agent Evaluation - Hands-On
Builds a real LangGraph ReAct agent, runs it on science questions,
captures full traces, and evaluates agent trajectories.
"""
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os, re
import pandas as pd

DATA_PATH = r"D:\Study\Git_repo\evaluations\data\train.csv"

# LangSmith tracing setup (optional - needs a real API key)
os.environ.setdefault("LANGSMITH_TRACING", "false")
os.environ.setdefault("LANGSMITH_API_KEY", "your-key-here")

# Try to import LangGraph + LangChain
LANGGRAPH_AVAILABLE = False
try:
    from langgraph.prebuilt import create_react_agent
    from langchain_ollama import ChatOllama
    from langchain_core.tools import tool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    pass

KNOWLEDGE_BANK = {
    "physics": "Newton's laws: F=ma. Einstein: E=mc^2. PV=nRT for ideal gases.",
    "chemistry": "pH = -log[H+]. Molarity = moles/litre. Water autoionises at Kw=1e-14.",
    "biology": "DNA bases pair A-T and G-C. Central dogma: DNA -> RNA -> Protein.",
    "astrophysics": "Redshift measures recession velocity. Hubble law: v = H0*d.",
    "math": "Quadratic formula: x = (-b +/- sqrt(b^2 - 4ac)) / 2a.",
    "optics": "Diffraction angular spacing is inversely proportional to slit width.",
    "electromagnetism": "Gauss's law: flux through closed surface = Q_enc / epsilon_0.",
}

if LANGGRAPH_AVAILABLE:
    @tool
    def search_knowledge(query: str) -> str:
        """Search a knowledge bank for science facts related to the query."""
        for key, fact in KNOWLEDGE_BANK.items():
            if key in query.lower():
                return fact
        return f"General knowledge: query is about '{query[:60]}'. Check standard references."

    @tool
    def calculate(expression: str) -> str:
        """Evaluate a simple math expression (e.g. '2+2', '3*5/2')."""
        clean = expression.strip()
        if all(c in "0123456789.+-*/() " for c in clean):
            try:
                return str(eval(clean, {"__builtins__": {}}, {}))
            except Exception as e:
                return f"Error: {e}"
        return "Cannot evaluate: expression contains unsupported characters."

    @tool
    def get_hint(topic: str) -> str:
        """Return a helpful hint for a given science topic."""
        hints = {
            "dynamics": "MOND modifies Newton's second law at low accelerations.",
            "scaling": "Self-similar systems show dynamic scaling across time snapshots.",
            "diffraction": "Smaller objects produce wider diffraction patterns.",
            "thermodynamics": "Entropy always increases in an isolated system.",
            "quantum": "Heisenberg uncertainty: delta-x * delta-p >= hbar/2.",
        }
        for key, hint in hints.items():
            if key in topic.lower():
                return hint
        return f"Hint for '{topic}': review fundamental principles and dimensional analysis."

def build_langgraph_agent():
    """Build and return a LangGraph ReAct agent with ChatOllama."""
    llm = ChatOllama(model="mistral")
    return create_react_agent(llm, tools=[search_knowledge, calculate, get_hint])

# --- Simulated agent fallback ---
def _sim_tool(name, inp):
    if name == "search_knowledge":
        for key, fact in KNOWLEDGE_BANK.items():
            if key in inp.lower():
                return fact
        return f"General knowledge about '{inp[:50]}'."
    if name == "calculate":
        return "4"
    if name == "get_hint":
        return f"Hint: review core concepts related to {inp[:40]}."
    return "Unknown tool."

def run_simulated_agent(question_prompt, idx):
    """Return a simulated trace (list of step dicts) and a predicted letter."""
    tool_names = ["search_knowledge", "get_hint", "calculate"]
    chosen = tool_names[idx % 3]
    inp = question_prompt[:50] if chosen != "calculate" else "2+2"
    steps = [
        {"role": "human", "content": question_prompt[:120]},
        {"role": "ai", "content": f"I should use {chosen} to help answer this.",
         "tool_calls": [{"tool": chosen, "args": inp}]},
        {"role": "tool", "tool": chosen, "content": _sim_tool(chosen, inp)},
        {"role": "ai", "content": "Based on the tool result, the answer is D."},
    ]
    return "D", steps

# --- Trace extraction ---
def extract_trace_from_messages(messages):
    """Convert LangGraph message objects into a simple list of step dicts."""
    steps = []
    for msg in messages:
        entry = {"role": msg.type, "content": getattr(msg, "content", "")}
        if msg.type == "ai" and getattr(msg, "tool_calls", None):
            entry["tool_calls"] = [
                {"tool": tc["name"], "args": tc.get("args", {})} for tc in msg.tool_calls
            ]
        if msg.type == "tool":
            entry["tool"] = getattr(msg, "name", "unknown")
        steps.append(entry)
    return steps

def extract_answer_letter(steps):
    """Pull the final answer letter (A-E) from the last AI message."""
    for step in reversed(steps):
        if step["role"] == "ai" and not step.get("tool_calls"):
            match = re.search(r"\b([A-E])\b", step["content"])
            if match:
                return match.group(1)
    return "X"

# --- Evaluation metrics ---
def evaluate_trace(steps, predicted, ground_truth):
    """Score a single agent trajectory."""
    tool_calls = sum(len(s.get("tool_calls", [])) for s in steps if s["role"] == "ai")
    tools_used = [tc["tool"] for s in steps if s["role"] == "ai" for tc in s.get("tool_calls", [])]
    has_final = any(s["role"] == "ai" and not s.get("tool_calls") and s["content"] for s in steps)
    return {
        "task_complete": has_final, "tool_calls": tool_calls,
        "tools_used": ", ".join(tools_used) if tools_used else "none",
        "tool_correct": tool_calls > 0, "answer_correct": predicted == ground_truth,
        "trajectory_len": len(steps),
    }

# --- Main ---
def main():
    print("=" * 60)
    print("CHAPTER 8: AGENT EVALUATION (LangGraph ReAct Agent)")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)
    sample = df.head(3)
    print(f"\nLoaded {len(df)} questions, using first 3 for agent evaluation.\n")

    # Build agent
    agent = None
    if LANGGRAPH_AVAILABLE:
        try:
            agent = build_langgraph_agent()
            print("LangGraph ReAct agent built successfully (ChatOllama/mistral).\n")
        except Exception as e:
            print(f"Failed to build LangGraph agent: {e}\nFalling back to simulated agent traces.\n")
    else:
        print("LangGraph/LangChain not installed - using simulated agent traces.\n")

    # Run agent on each question
    all_results = []
    for idx, row in sample.iterrows():
        question, gt = row["prompt"], row["answer"]
        choices = "\n".join(f"  {c}: {str(row[c])[:90]}" for c in "ABCDE")
        question_prompt = (
            f"Answer this multiple-choice science question. Use the available tools if "
            f"helpful, then pick exactly one letter (A/B/C/D/E).\n\n"
            f"Question: {question}\n\nChoices:\n{choices}\n\n"
            f"Reply with your reasoning and end with the correct letter."
        )
        print(f"--- Question {idx + 1} (id={row['id']}) ---")
        print(f"Q: {question[:110]}...")
        print(f"Ground truth: {gt}\n")

        if agent is not None:
            try:
                result = agent.invoke({"messages": [("user", question_prompt)]})
                steps = extract_trace_from_messages(result["messages"])
                predicted = extract_answer_letter(steps)
            except Exception as e:
                print(f"  Agent error: {e}  -> falling back to simulation.\n")
                predicted, steps = run_simulated_agent(question_prompt, idx)
        else:
            predicted, steps = run_simulated_agent(question_prompt, idx)

        # Print full trace
        print("  Full Trace:")
        for i, s in enumerate(steps, 1):
            print(f"    Step {i} [{s['role'].upper()}]: {str(s['content'])[:100]}")
            for tc in s.get("tool_calls", []):
                print(f"      -> tool_call: {tc['tool']}({str(tc['args'])[:80]})")
            if s.get("tool"):
                print(f"      <- tool_result from: {s['tool']}")
        print()

        ev = evaluate_trace(steps, predicted, gt)
        ev.update({"question_id": row["id"], "predicted": predicted, "ground_truth": gt})
        all_results.append(ev)
        print(f"  Predicted: {predicted} | Correct: {ev['answer_correct']}\n")

    # Evaluation summary
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    rdf = pd.DataFrame(all_results)
    print(f"\n{rdf.to_string(index=False)}\n")
    print("--- Aggregate Metrics ---")
    print(f"Task completion rate : {rdf['task_complete'].mean():.2%}")
    print(f"Avg tool calls/quest: {rdf['tool_calls'].mean():.1f}")
    print(f"Tool correctness     : {rdf['tool_correct'].mean():.2%}")
    print(f"Answer accuracy      : {rdf['answer_correct'].mean():.2%}")
    print(f"Avg trajectory length: {rdf['trajectory_len'].mean():.1f} steps")
    mode = "LangGraph ReAct (ChatOllama/mistral)" if agent else "Simulated"
    print(f"\nAgent mode: {mode}")

    # LangSmith note
    print("\n--- LangSmith Tracing ---")
    if os.environ.get("LANGSMITH_TRACING") == "true":
        print("LangSmith tracing is ENABLED. View traces at https://smith.langchain.com")
    else:
        print("LangSmith tracing is disabled. To enable, set:")
        print('  os.environ["LANGSMITH_TRACING"] = "true"')
        print('  os.environ["LANGSMITH_API_KEY"] = "<your-api-key>"')
        print("Then re-run. Traces will appear on the LangSmith dashboard.")

    # Langfuse tracing
    print("\n--- Langfuse Tracing ---")
    try:
        from langfuse import Langfuse
        sys.path.insert(0, r"D:\Study\Git_repo\evaluations")
        from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

        langfuse = Langfuse(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_BASE_URL,
        )

        trace = langfuse.trace(name="ch8-agent-evaluation", metadata={"agent": mode})

        for res in all_results:
            span = trace.span(
                name=f"question-{res['question_id']}",
                input={"ground_truth": res["ground_truth"]},
                output={"predicted": res["predicted"], "correct": res["answer_correct"]},
            )
            span.score(name="answer_correct", value=1.0 if res["answer_correct"] else 0.0)
            span.score(name="tool_calls", value=float(res["tool_calls"]))
            span.score(name="trajectory_len", value=float(res["trajectory_len"]))
            span.end()

        langfuse.flush()
        print("  Langfuse traces sent. View at: https://cloud.langfuse.com")
    except Exception as e:
        print(f"  Langfuse not available ({e}), skipping.")
        print("  pip install langfuse  # then set keys in constant.py")

    print("\nDone!")

if __name__ == "__main__":
    main()
