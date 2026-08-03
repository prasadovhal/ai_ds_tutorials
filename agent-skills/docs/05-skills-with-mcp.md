# Skills and MCP Servers: Questions and Discussions

## Key Architectural Hierarchy

Remember this hierarchy:
```
User
  │
  ▼
Agent
  │
  ▼
Skill
  │
  ▼
Tool
  │
  ▼
MCP Server (optional)
```

**Critical principle:** A skill does not talk directly to an MCP server. It asks the agent to use a tool, and that tool may be provided by an MCP server.

---

## Without MCP

Suppose you have a skill called **Research Paper Reviewer**.

The workflow might be:
1. Read PDF
2. Extract text
3. Summarize
4. Evaluate methodology
5. Generate report

The tools are **built into your application**.

## With MCP

Now imagine your organization exposes these tools through an MCP server:

**MCP Server Tools:**
- Paper Search Tool
- PDF Reader Tool
- ArXiv Tool
- Citation Tool
- CrossRef Tool
- GitHub Tool

Your skill doesn't care where they come from.

It simply says:
1. Search for the paper
2. Read the PDF
3. Extract citations
4. Compare with related papers

**The agent discovers** that these tools are available via MCP and calls them.

---

## Real-World Example: Data Scientist Workflow

### Company Setup

Your company has an MCP server exposing:
- Snowflake
- Feature Store
- MLflow
- Jira
- Slack
- GitHub

### Skill: Experiment Reviewer

**Workflow:**
1. Read experiment from MLflow
2. Read dataset metadata from Feature Store
3. Fetch code from GitHub
4. Compare metrics
5. Generate review
6. Post summary to Slack
7. Create Jira ticket if performance drops

**Notice something important:**

The skill **never says:**
> Call http://mlflow.company.com/api/...

Instead it says:
> Read experiment from MLflow.

**The agent figures out which MCP tool implements that capability.**

---

## Another Example: Customer Churn Investigation

### Skill Workflow

**Today (without MCP):**
- SQL Tool
- Python Tool
- Email Tool

**Tomorrow (with MCP):**
- Snowflake MCP
- Python MCP
- Outlook MCP

**The skill doesn't change.** Only the available tools change.

This separation is one of the **biggest benefits of MCP**.

---

## Q1: What Should a Skill Contain?

### Instead of This:
```
Call REST endpoint:
POST /api/search
```

### Write This:
```
Search for the research paper.

If a Paper Search tool is available, use it.
Otherwise ask the user.
```

This makes the skill **portable**.

### Think of It Like Python

Imagine writing:
```python
df.describe()
```

You don't care whether pandas uses:
- C++
- NumPy
- SIMD
- Threads

Similarly:
```
Read GitHub repository.
```

The skill doesn't care whether that happens through:
- MCP
- REST API
- SDK
- Local tool

---

## Q2: The Most Important Misconception About MCP

**Many people think:** "Skills belong inside MCP."

**They don't.**

Think of them as **separate layers**:

- **MCP** answers: "What capabilities are available?"
- **Tools** provide those capabilities
- **Skills** answer: "How do I solve this task using whatever capabilities are available?"
- **Agent** decides which skill to invoke and which tool to call at each step

---

## Q3: Can MCP Call a Skill?

### In Standard MCP Design: No

An MCP server exposes tools/resources/prompts, **not business workflows**.

Think of it like a database.

A database doesn't decide:
> "Oh, this looks like a research paper. I'll start the Paper Review skill."

It simply answers requests.

---

## Q4: Could You Build a Tool That Triggers Another Skill?

### Yes, But With Caveats

**Example:**

1. **Skill A** runs
2. Calls **Tool X**
3. **Tool X** internally invokes another agent
4. That agent executes **Skill B**

This is technically possible but requires careful design.

### Example: Patent Search

**Research Review Skill**
↓
**Translation Tool** (for non-English papers)
↓
**Translation Agent**
↓
**Translation Skill**

But notice:
- The MCP server is not calling the skill
- The tool implementation happens to invoke another agent

### When Is This Useful?

Suppose you have:

**Research Review Skill**
↓
**Patent Search Tool**
↓
**Patent Search Service**
↓
**Specialized Patent Agent**
↓
**Patent Analysis Skill**

Your main agent doesn't need to know how patent analysis works. It simply asks the tool.

This is common in **multi-agent systems** but adds complexity.

---

## Q5: The Actual Flow: Who Decides Which Tool?

### The Critical Point

**The MCP server does NOT decide which tool to use.**

**The agent (Claude/ChatGPT) decides.**

### The Actual Flow
```
User
  │
  ▼
Claude
  │
Chooses Skill
  │
Reads available tools
  │
Chooses ONE tool
  │
Calls MCP Server
  │
MCP Server executes that tool
  │
Returns result
```

**Notice the decision point:** Claude chooses the tool. MCP simply executes it.

---

## Q6: Example of Tool Discovery

### Scenario

Your MCP server exposes:
- search_arxiv
- search_pubmed
- search_github

### Your Skill Says:
> Find related research papers. Use ArXiv for computer science papers. Only use PubMed for biomedical topics. Never use GitHub for literature search.

### Claude Reasons:
The user is asking about a computer science paper.

↓

The search_arxiv tool is the best match.

↓

So Claude sends:
```
search_arxiv(
    query="Graph RAG"
)
```

### MCP Server Receives:
> Execute search_arxiv.

**It does NOT think:**
> Hmm... should I use PubMed instead?

That decision has already been made.

---

## Q7: Think of MCP as a Restaurant Waiter

You say:
> I'd like Paneer Butter Masala.

The waiter doesn't think:
> I'll bring Pizza instead.

The waiter simply takes the order to the kitchen.

**The waiter (MCP) doesn't choose.**

**The customer (agent) chooses.**

---

## Q8: What Does MCP Actually Do?

It only:
1. **Advertises available tools**
2. **Accepts a tool call**
3. **Executes it**
4. **Returns the result**

That's it.

---

## Q9: How Does Claude Know Which Tools Exist?

When Claude connects to an MCP server, the server announces available tools:

```
Available tools:

search_arxiv
Description: Search ArXiv papers.
Inputs: query

---

search_pubmed
Description: Search biomedical papers.
Inputs: query

---

search_github
Description: Search GitHub repositories.
Inputs: query
```

**Claude reads these descriptions** exactly like reading Python function docstrings.

Then Claude decides which to use based on:
- Skill guidance
- Tool descriptions
- Current user request
- Available context

---

## Q10: Where Does the Skill Help in Tool Selection?

### Skill Influence

Suppose your skill contains:
```
When searching for research papers:
- Prefer ArXiv
- Only use PubMed for biomedical topics
- Never use GitHub for literature search
```

### Agent Reasoning

Claude reasons:
> This is a computer science paper

↓

> Use search_arxiv

**The skill influences the decision.**

**The MCP server doesn't.**

---

## Q11: Which Is Bigger: MCP or Skill?

### The Answer

**MCP and Skills solve different problems, so one is not "bigger" than the other.**

However, if we look at the complete AI system:
- **MCP** = Infrastructure
- **Skills** = Application/Business logic

Think of it like building a web application:

```
Business Logic (Skills)
        ↑
Infrastructure (MCP)
```

The business logic sits on top of the infrastructure.

### Think of a House

**MCP = Electricity + Water + Plumbing**

It provides services.

It doesn't know whether you're:
- Cooking
- Watching TV
- Taking a shower

It simply provides capabilities.

**Skill = Recipe**

A recipe says:
1. Boil water
2. Cut vegetables
3. Add spices
4. Cook for 20 minutes

It uses electricity, gas, water, and utensils.

- Without utilities, you can't cook
- Without a recipe, you don't know what to cook

---

## Q12: MCP Servers Manage Tools, Not Skills

### The Correct Mental Model

**MCP servers expose and manage tools. They do not manage skills.**

### Architecture

```
User
  │
  ▼
Agent
  │
Chooses Skill
  │
Uses Tool
  │
MCP Server
```

**Notice:**
- **Skill** = "How do I solve this problem?"
- **Tool** = "Perform this one action"
- **MCP Server** = "Here are the tools I provide"

### Example

Your company has an MCP server that exposes:
- GitHub Tool
- Slack Tool
- Snowflake Tool
- MLflow Tool
- Jira Tool

**You write a skill:** Research Paper Reviewer

**The skill says:**
1. Read paper
2. Search related papers
3. Compare methods
4. Generate review

When it needs GitHub or a database, **the agent** asks the corresponding MCP tool.

**The MCP server doesn't know** it's helping a research review. It only knows:
> "Someone called the GitHub tool."

Think of an electrician in a house:

**Electricity (MCP) powers:**
- TV
- Fridge
- Oven
- Washing machine

**Electricity doesn't know:**
> "Today you're making tea."

**That's your recipe (the skill).**

---

## Q13: Can MCP Call a Skill and Can a Skill Call MCP? When to Use What?

### The Short Answer

- ✅ A skill can use tools that are exposed through an MCP server
- ❌ An MCP server should not directly call a skill (in standard architecture)

### Why This Matters

**Separation of concerns:**
- MCP = infrastructure layer
- Skills = business logic layer
- Agent = orchestration layer

Crossing these boundaries creates tight coupling and makes systems hard to maintain.

### Could You Break This Rule?

**Technically yes**, but it's not recommended for:
- Maintainability
- Testability
- Clarity
- Reusability

---

## Q14: One Advanced Point

**You've asked how a skill chooses a tool.** In production systems, the agent doesn't rely only on the skill's instructions. It usually combines three sources of information:

1. **The skill** → "Prefer ArXiv for CS papers"
2. **The tool descriptions** → "This tool searches ArXiv"
3. **The current user request** → "Find biomedical papers on Alzheimer's"

**The agent reasons over all three** and selects the best tool.

**That's why writing good tool descriptions is almost as important as writing good skills.**

Poorly described tools are often ignored or misused, even if they expose the right functionality.

This is an area that's becoming increasingly important for AI engineers and Principal Data Scientists building agent platforms.

---

## Summary: Skills + MCP Relationship

| Component | Purpose | Responsibility |
|-----------|---------|-----------------|
| **MCP Server** | Publish tools | Advertise, execute, return results |
| **Tool** | Atomic action | Perform one capability |
| **Skill** | Orchestration | Define workflow, guide tool selection |
| **Agent** | Orchestration | Choose skills, select tools, reason |

---

## Key Insight for Your Career

**MCP enables:**
- Tool discoverability
- Infrastructure decoupling
- Multi-agent coordination
- Scalable tool management

**Skills enable:**
- Business logic encoding
- Workflow definition
- Domain expertise capture
- Reusable automation

**Together they form the backbone of modern agentic AI systems.**

For a Principal Data Scientist, understanding how these layers interact is essential for designing enterprise-grade agent platforms.
