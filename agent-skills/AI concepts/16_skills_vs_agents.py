"""
File 16: Skills vs Agents & Multi-Agent Architecture
Concepts: Skills, agents, supervisor pattern, decision making, tool selection

This file clarifies a critical distinction in LLM systems:

SKILL = fixed workflow (always does the same steps)
  Example: RAG_search_skill(query) → retrieve → generate → return

AGENT = reasoning system (decides what to do)
  Example: science_agent(query) → decides → choose tool → execute → repeat

When does a skill become an agent? When it starts REASONING about what to do.

This file shows both patterns and when to use each.
"""

import ollama

client = ollama.Client()


# ============================================================================
# PART 1: SKILLS (Fixed Workflows)
# ============================================================================

def rag_search_skill(query, context):
    """
    RAG Search Skill: fixed workflow
    Always: retrieve → generate → return
    No decision making; always does the same thing.
    """

    # Step 1: Retrieve (simulated)
    retrieved_chunks = [
        f"Chunk about {query[:20]}... (simulated)",
        f"Another chunk about {query[:20]}..."
    ]

    # Step 2: Generate
    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "Answer based on context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )

    return {
        "skill": "rag_search",
        "query": query,
        "retrieved": len(retrieved_chunks),
        "answer": response['message']['content'][:100]
    }


def fact_lookup_skill(query):
    """
    Fact Lookup Skill: simple, deterministic
    Always: look up → return fact
    No reasoning; just retrieves known facts.
    """

    facts = {
        "photosynthesis": "Photosynthesis is the process plants use to convert light to chemical energy",
        "DNA": "DNA is the molecule that carries genetic instructions",
        "quantum": "Quantum mechanics describes behavior of matter at atomic scale"
    }

    for key, fact in facts.items():
        if key.lower() in query.lower():
            return {"skill": "fact_lookup", "fact": fact}

    return {"skill": "fact_lookup", "fact": "Fact not found"}


def explanation_skill(query):
    """
    Explanation Skill: explain a concept
    Always: generate explanation
    Fixed workflow, no decision making.
    """

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "Explain science concepts clearly."},
            {"role": "user", "content": f"Explain: {query}"}
        ]
    )

    return {
        "skill": "explanation",
        "query": query,
        "explanation": response['message']['content'][:150]
    }


# ============================================================================
# PART 2: AGENTS (Reasoning Systems)
# ============================================================================

def science_agent_decide_action(query):
    """
    Science Agent: decides which action to take
    NOT a fixed workflow; reasons about what to do.

    Flow:
    1. Analyze query
    2. Decide: use fact_lookup, rag_search, or explanation?
    3. Execute decision
    4. Return result
    """

    # Step 1: Analyze query type
    analysis_prompt = f"""Analyze this science query and decide the best action:
    Query: {query}

    Actions available:
    1. "fact_lookup" - for simple facts (What is X?, Define X?)
    2. "rag_search" - for complex analysis (Compare, Analyze, Evaluate)
    3. "explanation" - for conceptual understanding (Explain, How does)

    Return ONLY the action name (fact_lookup, rag_search, or explanation):"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are an agent router. Decide the best action."},
            {"role": "user", "content": analysis_prompt}
        ]
    )

    action = response['message']['content'].strip().lower()

    # Validate action
    valid_actions = ["fact_lookup", "rag_search", "explanation"]
    if action not in valid_actions:
        action = "explanation"  # default

    # Step 2: Execute the chosen skill
    if action == "fact_lookup":
        result = fact_lookup_skill(query)
    elif action == "rag_search":
        result = rag_search_skill(query, "Sample context")
    else:  # explanation
        result = explanation_skill(query)

    return {
        "agent": "science_agent",
        "query": query,
        "reasoning": f"Chose action: {action}",
        "result": result
    }


# ============================================================================
# PART 3: SUPERVISOR PATTERN (Multi-Agent Architecture)
# ============================================================================

def simple_qa_agent(query, context):
    """Simple QA agent: answer directly"""
    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "Answer questions concisely."},
            {"role": "user", "content": f"Q: {query}\nContext: {context}"}
        ]
    )
    return response['message']['content'][:80]


def deep_analysis_agent(query, context):
    """Deep analysis agent: thorough reasoning"""
    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "Provide deep, thorough analysis."},
            {"role": "user", "content": f"Analyze: {query}\nContext: {context}"}
        ]
    )
    return response['message']['content'][:80]


def supervisor_agent(query):
    """
    Supervisor Agent: routes to specialized agents
    Decides which agent to use based on query complexity.

    This is multi-agent architecture:
    Supervisor → [Simple QA Agent, Deep Analysis Agent, RAG Agent]
    """

    # Step 1: Analyze complexity
    complexity_prompt = f"""Analyze this query's complexity:
    Query: {query}

    Is it:
    1. "simple" - straightforward, factual (What is X?)
    2. "complex" - requires analysis, reasoning (Compare, Analyze)

    Return ONLY: simple or complex"""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You route queries to appropriate agents."},
            {"role": "user", "content": complexity_prompt}
        ]
    )

    complexity = response['message']['content'].strip().lower()
    if "simple" not in complexity and "complex" not in complexity:
        complexity = "simple"

    # Step 2: Route to appropriate agent
    context = "Sample scientific context"

    if "simple" in complexity:
        result = simple_qa_agent(query, context)
        agent_used = "simple_qa_agent"
    else:
        result = deep_analysis_agent(query, context)
        agent_used = "deep_analysis_agent"

    return {
        "supervisor": "supervisor_agent",
        "query": query,
        "complexity": complexity,
        "routed_to": agent_used,
        "result": result
    }


# ============================================================================
# PART 4: COMPARISON & DECISION MATRIX
# ============================================================================

# Theory moved to: 16_skills_vs_agents_theory.md
# (See markdown doc for detailed skill vs agent comparison)


# Theory moved to: 16_skills_vs_agents_theory.md
# (See markdown doc for architecture patterns: Simple, Agent, Supervisor)


if __name__ == "__main__":
    print("File 16: Skills vs Agents & Multi-Agent Architecture")

    print("\n--- Testing Individual Skills ---")
    print("\n1. RAG Search Skill:")
    result = rag_search_skill("What is photosynthesis?", "Sample context about photosynthesis")
    print(f"   {result['skill']}: {result['answer'][:80]}...")

    print("\n2. Fact Lookup Skill:")
    result = fact_lookup_skill("Define DNA")
    print(f"   {result['skill']}: {result['fact'][:80]}...")

    print("\n3. Explanation Skill:")
    result = explanation_skill("Quantum mechanics")
    print(f"   {result['skill']}: {result['explanation'][:80]}...")

    print("\n\n--- Testing Agents ---")
    print("\n1. Science Agent (chooses which skill):")
    result = science_agent_decide_action("What is photosynthesis?")
    print(f"   Decision: {result['reasoning']}")
    print(f"   Result: {result['result']}")

    print("\n2. Supervisor Agent (chooses which agent):")
    result = supervisor_agent("Compare photosynthesis and cellular respiration")
    print(f"   Complexity: {result['complexity']}")
    print(f"   Routed to: {result['routed_to']}")
    print(f"   Result: {result['result'][:80]}...")

    print("\n" + "=" * 60)
    print("For detailed theory on skills, agents, and architecture:")
    print("→ See 16_skills_vs_agents_theory.md")
    print("=" * 60)