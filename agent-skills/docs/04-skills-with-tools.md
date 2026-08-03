# Skills and Tools: Questions and Discussions

## Q1: When Should Something Be a Tool Instead of a Skill?

This is one of the **hardest design decisions** in agent architecture.

### The Distinction

**Tool:** Performs one atomic action
- Example: SQL generation, API call, file read

**Skill:** Orchestrates multiple tools to solve a business problem
- Example: Experiment review (reads experiment, compares metrics, generates report)

### Decision Framework

Ask these questions:

1. **Can it be a single function or API call?**
   - Yes → Probably a **tool**
   - No → Probably a **skill**

2. **Does it require domain expertise or decision-making?**
   - Yes → Probably a **skill**
   - No → Probably a **tool**

3. **Will it be reused in multiple different workflows?**
   - Yes → Could be either (but favors **tool** for simplicity)
   - No → Probably a **skill**

### Example: SQL Generation

**Should it be:**
- A tool? ✅
- A skill? ❌

**Why:** SQL generation is an atomic capability. A skill that "reviews SQL" would use the SQL generation tool internally.

---

## Q2: How Do Skills Use Tools?

Skills **describe the workflow** without specifying exact implementation.

### Good Pattern

**Skill Name:** Research Paper Reviewer

The skill says:
1. Read the paper
2. Identify sections
3. Extract key facts
4. Compare with related work

When it needs a capability, the **agent** chooses which tool to use.

### Bad Pattern

**Skill says:**
> "Call the Python tool at endpoint /api/python and execute this code..."

**Why it's bad:**
- Too specific about implementation
- Breaks if tools change
- Not portable across platforms

### Good Pattern

**Skill says:**
> "Perform statistical analysis. Use Python if available, SQL if analyzing a database table, or web search if external data is needed."

**Why it's good:**
- Describes what's needed, not how
- Flexible about tool choices
- Agent can pick the best available tool

---

## Q3: What Should a Skill Contain?

Instead of this:
```
Call REST endpoint:
POST /api/search
```

Write:
```
Search for the research paper.

If a Paper Search tool is available, use it.
Otherwise ask the user.
```

This makes the skill **portable**.

### Think of It Like Python

You don't write:
```python
import numpy.core._methods as c
c._mean(df, axis=0)
```

You write:
```python
df.describe()
```

You don't care whether pandas uses C++, NumPy, SIMD, or threads internally.

Similarly, your skill shouldn't care whether a tool comes from:
- MCP
- REST API
- SDK
- Local tool

---

## Q4: How Does the Agent Choose Which Tool to Use?

### The Flow

1. **User asks a question**
2. **Agent selects the appropriate skill**
3. **Skill describes what's needed** (e.g., "Search for papers")
4. **Agent reads available tools** from connected MCP servers or tool registry
5. **Agent chooses ONE tool** based on:
   - Skill guidance
   - Tool descriptions
   - User request
   - Current context
6. **Agent calls that tool**
7. **Tool returns result**
8. **Skill continues execution**

### Example

**Available tools:**
- search_arxiv
- search_pubmed
- search_github

**Skill says:**
> Find related research papers. Use ArXiv for computer science papers, PubMed for biomedical topics.

**User asks:**
> Find papers on Graph Neural Networks

**Agent reasons:**
- This is a CS topic
- Use search_arxiv
- Call: search_arxiv(query="Graph Neural Networks")

**Important:** The MCP server doesn't choose the tool. The **agent** does.

### Think of MCP as a Restaurant Waiter

You say:
> I'd like Paneer Butter Masala.

The waiter doesn't think:
> I'll bring Pizza instead.

The waiter simply takes your order to the kitchen.

The waiter (MCP) doesn't choose. The customer (agent) chooses.

---

## Q5: When Should Logic Go Into Code vs the Skill?

### Where Each Belongs

**In Code (Python, SQL, etc.):**
- Atomic operations
- Data transformations
- Algorithm implementations
- File I/O
- API calls

**In Skill (Instructions):**
- Decision logic
- Workflow orchestration
- Error handling strategy
- Tool selection guidance
- Output formatting rules

### Example

**❌ Don't put this in the skill:**
```
Run this Python code: 
  import pandas as pd
  df.drop_duplicates()
```

**✅ Put this in the skill:**
```
1. Check for duplicate rows
2. If duplicates exist:
   - Log which columns have duplicates
   - Remove duplicates
   - Document how many rows were removed
3. Report the result
```

The **how** (Python code) goes in tools. The **what and when** goes in skills.

---

## Q6: Should Tools Be Local or Through MCP?

### Considerations

**Use Local Tools When:**
- Tool is only used by one skill
- Tool is frequently changing
- Tool needs access to local resources
- You want simplicity

**Use MCP Servers When:**
- Tool is used by multiple skills
- Tool needs to be discoverable
- You want infrastructure to manage tool versions
- You need multiple tools grouped together

### Example

**Local tool:**
```
Python function: clean_csv()
Used by: Dataset Quality Analyzer skill
```

**MCP-exposed tool:**
```
MCP Server: snowflake-server
Tools:
  - query_snowflake()
  - fetch_table_schema()
  - execute_stored_procedure()

Used by: Multiple skills
```

---

## Q7: How Small Should a Skill Be?

### The Sizing Question

**Example:** Should "RAG Evaluation" be one skill?

Or separate skills for:
- Retrieval evaluation
- Answer evaluation
- Hallucination analysis

### Decision Framework

**Keep it as one skill if:**
- All steps share the same purpose
- They're always done together
- The user requests them as one task
- They produce one unified output

**Split into separate skills if:**
- They solve different problems
- They're used independently
- They have different tool requirements
- They produce separate outputs

### Example: Research Paper Review

**Could split into:**
- Paper Metadata Extractor (tools: PDF parsing)
- Methodology Reviewer (tools: analysis, reasoning)
- Citation Checker (tools: database lookup)
- Novelty Evaluator (tools: literature search)

**Keep as one skill if:**
- User always asks: "Review this paper" (all at once)
- Each step informs the next
- Produces one comprehensive review

**Split if:**
- User sometimes asks for just citation checking
- Each can be used independently
- Different teams need different reviewers

---

## Q8: When Should I Create a New Skill Instead of Extending an Existing One?

### Examples

Consider these three skills:
- Research Paper Reviewer
- Research Proposal Reviewer
- Conference Paper Reviewer

**Should they be:**
- Separate skills?
- Variants of one skill with parameters?

### Decision Framework

**Use One Skill if:**
- Core workflow is identical
- Only minor variations needed (e.g., "check for citations" → "check for preliminary results")
- Users can't distinguish between them

**Use Separate Skills if:**
- Different workflows
- Different tool requirements
- Different output formats
- Users explicitly name them differently

### General Rule

If 80% of the workflow is identical but 20% varies, consider:
- One skill with a "skill type" parameter
- Shared tool library with skill-specific wrappers
- Inheritance (if your skill framework supports it)

But if workflows diverge significantly, separate skills are cleaner.

---

## Q9: Can One Skill Call Another Skill?

### The Architecture Question

**In standard architecture:** Not directly.

Instead:
1. **Skill A** runs and calls a **Tool**
2. That **Tool** (implementation) might internally:
   - Invoke another agent
   - Execute another skill
   - Call external services

### Example: Patent Search

**Main Skill:** Research Review Skill
↓
**Calls Tool:** Patent Search Tool
↓
**Inside the tool:**
- Specialized Patent Agent
- Patent Analysis Skill

Your main agent doesn't need to know how patent analysis works. It simply calls the tool.

This is common in **multi-agent systems**.

### When Is This Useful?

When:
- A sub-task is complex enough to warrant its own agent
- Multiple teams own different agents
- You want to encapsulate expertise
- You need specialized reasoning at multiple levels

---

## Q10: Can This Create Infinite Loops?

### Yes, If You're Not Careful

**Example loop:**
```
Skill A
  ↓
Tool A
  ↓
Agent B
  ↓
Skill B
  ↓
Tool B
  ↓
Agent A
  ↓
Skill A
  ↓
... infinite loop
```

### Prevention Strategies

1. **Depth limits** → "No more than 3 levels of agent nesting"
2. **Timeout policies** → "Each tool call has a 30-second timeout"
3. **Loop detection** → "Track visited states and stop if we're repeating"
4. **Clear termination conditions** → "Each skill must have explicit success/failure states"
5. **Testing** → "Test skill compositions before production"

### Best Practice

**Design skills so they always terminate:**
- Each skill has a clear success condition
- Each tool call produces new information
- No circular dependencies between skills
- Timeouts and retry limits are set

---

## Summary: Skills and Tools Relationship

| Aspect | Best Practice |
|--------|---------------|
| **Specification** | Describe workflow, not implementation |
| **Tool Choice** | Let agent decide based on availability |
| **Granularity** | Single tool = atomic action; single skill = workflow |
| **Reusability** | Avoid hardcoding tools; reference by capability |
| **Composition** | Tools compose into skills; skills into workflows |
| **Error Handling** | Skill defines strategy; tool implements detail |
| **Portability** | Skill works with different tool implementations |

---

## Key Insight for Your Career

As a Principal Data Scientist working on GenAI systems, understanding the boundary between skills and tools is critical. Good separation of concerns makes agent systems:
- **Testable** → Mock tools for skill testing
- **Reusable** → Skills work with any compatible tool
- **Scalable** → Can swap tool implementations without changing skills
- **Maintainable** → Clear responsibilities make debugging easier
