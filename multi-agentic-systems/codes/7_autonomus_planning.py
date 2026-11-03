"""
Autonomous Planning & Dynamic Reasoning (ReAct + ToT + self-correction + replanning)
Persistent & Working Memory (agentic memory beyond RAG)
LLM Inference Optimization (model routing, KV-style caching, prompt trimming, speculative-style draft → verify pattern)

"""

# =========================================================
# 🔷 IMPORTS
# =========================================================

import os, json, time, uuid, pickle, hashlib
import numpy as np
import faiss
import ollama
from typing import TypedDict, List, Dict
from sentence_transformers import SentenceTransformer

# =========================================================
# 🔷 LLM ROUTER (INFERENCE OPTIMIZATION)
# - route small vs large
# - KV-like cache (prompt hashing)
# - prompt trimming
# =========================================================

LLM_CACHE: Dict[str, str] = {}

def hash_prompt(prompt: str):
    return hashlib.md5(prompt.encode()).hexdigest()

def trim_prompt(text: str, max_chars=2000):
    return text[-max_chars:]  # keep most recent context

def llm_router(prompt: str, task_type="general"):
    prompt = trim_prompt(prompt)

    key = hash_prompt(prompt)
    if key in LLM_CACHE:
        return LLM_CACHE[key]

    # model routing
    model = "mistral"
    if task_type == "simple":
        model = "mistral"  # (replace with smaller model if available)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )["message"]["content"]

    LLM_CACHE[key] = response
    return response

# =========================================================
# 🔷 EMBEDDING + MEMORY
# =========================================================

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

class Memory:
    def __init__(self, path="agent_memory.pkl"):
        self.path = path

        # semantic
        self.texts = []
        self.index = faiss.IndexFlatL2(384)

        # episodic
        self.episodes = []

        # procedural
        self.rules = []

        if os.path.exists(path):
            self.load()

    def add_semantic(self, text, score=1.0):
        emb = embed_model.encode([text])
        self.index.add(np.array(emb))
        self.texts.append((text, score))

    def retrieve(self, query, k=3):
        if not self.texts:
            return []
        q_emb = embed_model.encode([query])
        D, I = self.index.search(np.array(q_emb), k)
        return [self.texts[i][0] for i in I[0]]

    def add_episode(self, data):
        self.episodes.append(data)

    def add_rule(self, rule):
        self.rules.append(rule)

    def prune(self):
        self.texts = [t for t in self.texts if t[1] > 0.3]

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.__dict__, f)

    def load(self):
        with open(self.path, "rb") as f:
            self.__dict__.update(pickle.load(f))

memory = Memory()

# =========================================================
# 🔷 TRACE / OBSERVABILITY
# =========================================================

TRACE = []

def trace(agent, input_data, output):
    TRACE.append({
        "id": str(uuid.uuid4()),
        "agent": agent,
        "input": input_data,
        "output": output,
        "time": time.time()
    })

def replay():
    for t in TRACE:
        print(f"{t['agent']} → {t['output']}")

# =========================================================
# 🔷 STATE (WORKING MEMORY)
# =========================================================

class State(TypedDict):
    query: str
    context: str
    thoughts: List[str]
    candidates: List[str]
    final: str
    iteration: int

# =========================================================
# 🔷 TOOLS
# =========================================================

def retrieval_tool(query):
    return "\n".join(memory.retrieve(query))

# =========================================================
# 🔷 AUTONOMOUS PLANNING (ReAct)
# =========================================================

def planner(state):
    plan = llm_router(f"""
    Break this into steps:

    {state['query']}

    Include:
    - retrieval
    - reasoning
    - decision
    """)
    trace("planner", state["query"], plan)
    return plan

# =========================================================
# 🔷 TREE OF THOUGHTS (MULTI PATH)
# =========================================================

def generate_thoughts(state):
    thoughts = []
    for _ in range(3):
        t = llm_router(f"""
        Reason step-by-step:

        Context:
        {state['context']}

        Query:
        {state['query']}
        """)
        thoughts.append(t)
    return thoughts

def score_thoughts(thoughts):
    scored = []
    for t in thoughts:
        s = llm_router(f"Score reasoning 0-1:\n{t}", task_type="simple")
        try:
            s = float(s.strip())
        except:
            s = 0.5
        scored.append((t, s))
    return sorted(scored, key=lambda x: x[1], reverse=True)

def prune(thoughts):
    return [t for t, _ in thoughts[:2]]

# =========================================================
# 🔷 SELF-CORRECTION LOOP
# =========================================================

def self_correct(thought):
    critique = llm_router(f"""
    Critique this reasoning:

    {thought}

    Identify issues.
    """)
    improved = llm_router(f"""
    Improve using critique:

    {thought}

    Critique:
    {critique}
    """)
    return improved

# =========================================================
# 🔷 MAIN AGENT LOOP (AUTONOMOUS + REPLANNING)
# =========================================================

def run(query):

    state: State = {
        "query": query,
        "context": "",
        "thoughts": [],
        "candidates": [],
        "final": "",
        "iteration": 0
    }

    plan = planner(state)

    while state["iteration"] < 3:

        # dynamic retrieval
        if "retrieval" in plan.lower():
            state["context"] = retrieval_tool(query)

        # ToT
        thoughts = generate_thoughts(state)
        scored = score_thoughts(thoughts)
        best = prune(scored)

        # self-correction
        corrected = [self_correct(t) for t in best]

        # final synthesis
        final = llm_router(f"""
        Combine best reasoning:

        {corrected}

        Answer:
        """)

        trace("final", query, final)

        state["final"] = final

        # replanning condition
        if "not enough" in final.lower():
            plan = planner(state)
            state["iteration"] += 1
            continue

        break

    # memory update
    memory.add_semantic(state["final"], score=0.8)
    memory.add_episode({"q": query, "a": state["final"]})
    memory.save()

    return state

# =========================================================
# 🔷 SPECULATIVE STYLE (FAST DRAFT → VERIFY)
# =========================================================

def speculative_answer(query):
    draft = llm_router(query, task_type="simple")  # fast guess
    verified = llm_router(f"""
    Verify and correct if needed:

    Draft:
    {draft}
    """)
    return verified

# =========================================================
# 🔷 BENCHMARK + REGRESSION
# =========================================================

benchmark = [
    {"q": "What is waiting period?", "expected": "years"},
    {"q": "Is surgery covered?", "expected": "depends"}
]

def evaluate():
    scores = []
    for b in benchmark:
        res = run(b["q"])
        score = llm_router(f"""
        Compare:
        Expected: {b['expected']}
        Got: {res['final']}

        Score 0-1
        """)
        try:
            score = float(score)
        except:
            score = 0.5
        scores.append(score)

    print("Avg Score:", sum(scores)/len(scores))

# =========================================================
# 🔷 RUN
# =========================================================

if __name__ == "__main__":

    query = "If I have pre-existing condition and surgery, what about waiting and reimbursement?"

    result = run(query)

    print("\nFINAL:\n", result["final"])

    print("\n--- TRACE ---")
    replay()

    print("\n--- SPECULATIVE ---")
    print(speculative_answer(query))

    print("\n--- EVAL ---")
    evaluate()