# Skills vs Agents — Theory & Architecture Patterns

## Core Distinction

### **SKILL** = Fixed Workflow
- No decision making
- Always does the same steps
- Deterministic behavior
- Example: `rag_search_skill()` → always retrieve + generate + return

### **AGENT** = Reasoning System
- Decides what to do based on input
- Dynamic workflow
- Can choose different paths
- Example: `science_agent()` → analyzes → chooses skill → executes

---

## Detailed Comparison

| Characteristic | SKILL | AGENT |
|---|---|---|
| **Decision Making** | No — fixed workflow | Yes — reasons about action |
| **Workflow** | Deterministic (same every time) | Dynamic (depends on input) |
| **Flexibility** | Low — does one thing | High — can choose different paths |
| **Complexity** | Simple to implement | More complex (needs reasoning) |
| **Use Case** | Specific task (RAG search, fact lookup) | General purpose (decides what to do) |
| **Speed** | Fast (no reasoning overhead) | Slower (LLM reasoning needed) |
| **Accuracy** | Predictable (always same steps) | Depends on reasoning quality |

---

## Architecture Patterns

### 1. **Simple (Single Skill)**

```
Query → RAG Skill → Answer
```

**Structure**: Direct execution of one workflow

**Pros**:
- Fast
- Predictable
- Easy to debug

**Cons**:
- Inflexible
- One-size-fits-all
- Doesn't adapt to query type

**When to use**: 
- Simple, well-defined problem
- You know exactly what to do for every query
- Performance critical

**Example**:
```python
def simple_qa(query):
    # Always: retrieve + generate
    chunks = retrieve(query)
    return generate(chunks, query)
```

---

### 2. **Skill Router (Agent)**

```
Query → Agent (chooses skill) → Skill → Answer
```

**Structure**: Agent reasoning + multiple skills

**Pros**:
- Flexible
- Chooses best approach for query
- Adapts to input type

**Cons**:
- Slower (agent reasoning)
- Agent reasoning overhead
- More complex to debug

**When to use**: 
- Multiple task types
- Query complexity varies
- Want best tool for job

**Example**:
```python
def smart_agent(query):
    action = decide_action(query)  # LLM decides
    if action == "fact_lookup":
        return fact_lookup_skill(query)
    elif action == "rag_search":
        return rag_search_skill(query)
    else:
        return explanation_skill(query)
```

**Reasoning examples**:
- "What is X?" → fact_lookup skill
- "Compare A and B" → rag_search skill
- "Explain how X works" → explanation skill

---

### 3. **Supervisor (Multi-Agent)**

```
Query → Supervisor (chooses agent) → Agent → Skills → Answer
```

**Structure**: Hierarchical agent routing

**Pros**:
- Very flexible
- Specialized agents for domains
- Can handle complex flows

**Cons**:
- Complex
- Multiple reasoning steps
- Higher latency
- Expensive (multiple LLM calls)

**When to use**: 
- Enterprise: multiple domains/teams
- Complex reasoning needed
- Different agents handle different domains

**Example**:
```python
def supervisor(query):
    complexity = analyze_complexity(query)
    if "simple" in complexity:
        return simple_qa_agent(query)
    else:
        return deep_analysis_agent(query)
```

**Agent specialization**:
- QA Agent: quick, direct answers
- Analysis Agent: thorough reasoning
- Research Agent: deep investigation
- Support Agent: help desk queries

---

## When to Add Reasoning?

A skill becomes an agent when you add a **decision point**:

### Still a Skill:
```python
def rag_skill(query):
    chunks = retrieve(query)  # Fixed step 1
    return generate(chunks, query)  # Fixed step 2
```

### Now an Agent:
```python
def qa_agent(query):
    # NEW: Decision point
    if is_simple(query):
        return direct_answer(query)  # Path A
    else:
        chunks = retrieve(query)
        return generate(chunks, query)  # Path B
```

---

## Cost-Complexity Trade-off

```
           Supervisor (Multi-Agent)
                  /|
                /  |
              /    |  Complexity ↑
            /      |  Latency ↑
          /        |  Cost ↑
        /          |
    Router (Agent) |
      /            |
    /              |
Simple (Skill) ----+
```

### Latency Comparison

| Pattern | Latency | Reason |
|---|---|---|
| Skill | ~2s | Retrieve + Generate |
| Agent | ~3-4s | +1-2s for LLM decision |
| Supervisor | ~5-6s | +Multiple reasoning steps |

### Cost Comparison

| Pattern | Cost | Reason |
|---|---|---|
| Skill | Low | 1 LLM call (generation) |
| Agent | Medium | 2 LLM calls (decision + generation) |
| Supervisor | High | 3+ LLM calls (supervisor + agent + generation) |

---

## Decision Matrix: Which Pattern?

### Start with **Skill** if:
- ✅ Problem is well-defined
- ✅ You know the workflow
- ✅ Performance matters
- ✅ Cost is critical
- ✅ MVP/prototype phase

### Move to **Agent** if:
- ❌ One workflow doesn't fit all queries
- ❌ Need to choose between 2-3 tools
- ❌ Query types are different
- ✅ Some latency is acceptable
- ✅ Better UX worth the cost

### Reach for **Supervisor** if:
- ❌ Enterprise system
- ❌ Multiple specialized teams
- ❌ Complex domain routing
- ❌ Different agents per domain
- ✅ Cost is not primary concern

---

## Real-World Examples

### Example 1: Support Chatbot (Skill)
```
Customer query
  ↓
FAQ retrieval (always same)
  ↓
Generate response
```

### Example 2: Science Q&A (Agent)
```
Query
  ↓
Analyze: "What is X?" or "Compare X and Y?"
  ↓
Route: fact_lookup vs rag_search
  ↓
Execute chosen skill
```

### Example 3: Enterprise AI Platform (Supervisor)
```
User query
  ↓
Analyze complexity & domain
  ↓
Route: legal_agent vs technical_agent vs general_agent
  ↓
Each agent uses own skills
  ↓
Synthesize response
```

---

## Migration Path

```
Phase 1: Skill (MVP)
  ↓ (as system grows)
Phase 2: Agent (add routing)
  ↓ (as scale increases)
Phase 3: Supervisor (multi-team)
```

This matches real product maturity:
1. **Start simple**: One skill that works
2. **Add flexibility**: Agent that chooses skills
3. **Scale complexity**: Supervisor for multi-agent orchestration

---

## Implementation Checklist

### Building a Skill
- [ ] Define fixed workflow
- [ ] Implement each step
- [ ] Test end-to-end

### Building an Agent
- [ ] Define available skills
- [ ] Implement decision logic (LLM-based)
- [ ] Test routing on diverse queries
- [ ] Monitor agent accuracy

### Building a Supervisor
- [ ] Define specialized agents
- [ ] Implement supervisor logic
- [ ] Add fallback/error handling
- [ ] Monitor end-to-end quality
