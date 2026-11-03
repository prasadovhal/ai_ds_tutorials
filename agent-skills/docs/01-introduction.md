# Introduction to Agent Skills

## What is an Agent Skill?

A skill is a **reusable instruction** that teaches an agent how to perform a specific task consistently. Think of it as giving the agent a **Standard Operating Procedure (SOP)**.

### Tools vs Skills: Core Distinction

The key distinction is that a **tool** is a single capability, while a **skill** is an orchestrated workflow.

#### Tool
A tool performs **one well-defined action**.

**Examples:**
- Read a CSV
- Clean a CSV
- Train a Random Forest model
- Plot a confusion matrix
- Save results to a database

Each of these can be a separate tool.

#### Skill
A skill **combines multiple steps** (and often multiple tools) to accomplish a meaningful business task.

**Example: "Build Churn Prediction Model" Skill**

The skill might internally use:
1. Read the CSV (Read CSV tool)
2. Clean the data (Data Cleaning tool)
3. Perform feature engineering (Feature Engineering tool)
4. Split train/test (Split Data tool)
5. Train the model (Model Training tool)
6. Evaluate metrics (Evaluation tool)
7. Generate an HTML/PDF report (Report Generation tool)

The user simply says: *"Build a churn prediction model from this dataset."*

The agent invokes the skill, which internally uses all those tools.

### The Granularity Rule

The distinction is not based on the task name; it's based on **granularity**:

- **Tool** = one atomic capability
- **Skill** = a reusable workflow that coordinates multiple capabilities

### Rule of Thumb

- If it can be expressed as **one function or API call**, it's usually a **tool**
- If it requires **multiple decisions and multiple function/tool calls**, it's usually a **skill**

This way of thinking scales well whether you're building agents in LangGraph, OpenAI Agents SDK, or other agent frameworks.

## What Does a Skill Usually Contain?

A good skill typically includes:

1. **Purpose** – What this skill does
2. **When to use it** – The situations where it should be chosen
3. **Inputs** – What it expects (CSV, PDF, SQL table, etc.)
4. **Steps** – The workflow to follow
5. **Tools to use** – Python, SQL, web search, etc.
6. **Rules** – Things to avoid or always do
7. **Output format** – How to present the answer

### Example: Customer Churn Analysis Skill

**Purpose:** Predict which customers may churn

**Workflow:**
1. Load CSV
2. Validate columns
3. Clean missing values
4. Engineer features
5. Train model
6. Evaluate accuracy
7. Explain important features
8. Save report

**Expected Output:**
- Accuracy
- Precision/Recall
- Feature importance
- Business recommendations

## Does a Skill Need Code?

It depends.

### Simple Skills
**No code required.**

Examples:
- Summarize meeting notes
- Rewrite an email
- Explain a research paper

These can often be just instructions.

### Technical Skills
**Usually yes.**

Examples:
- Query SQL
- Train an ML model
- Call an API
- Generate plots

These typically involve code or tool calls.

## Is a Skill Just a Prompt?

**No.**

A prompt might be:
> "Summarize this PDF."

A skill is more like:
1. Read the PDF
2. Identify sections
3. Extract key facts
4. Ignore references
5. Summarize each section
6. Produce an executive summary

The prompt invokes the skill, but the skill defines **how the task should be carried out**.

## Skills Across Platforms

The idea is the same across platforms, but the implementation differs:

| Platform | How Skills Are Defined |
|----------|----------------------|
| **Claude** | Native Markdown skill files with instructions, examples, and tool guidance |
| **Cursor** | Rules, project instructions, and MCP/tool integrations |
| **ChatGPT** | Custom GPT instructions, agent workflows, or SDK-based skills/tool definitions |

The concept of a skill is universal:
- Purpose
- Workflow
- Tool usage
- Output format

But each platform has its own way of packaging those instructions.

## Why This Matters for Your Career

Since you're aiming for Principal Data Scientist and working on agentic AI, learning to write high-quality skills is becoming as important as writing ML pipelines was a few years ago.

### Useful Progression
1. **Learn to build tools** → Python functions, APIs, MCP servers
2. **Learn to write skills** → Orchestrate those tools
3. **Learn to compose skills** → Into agent workflows using frameworks like LangGraph

That progression mirrors how production AI agents are increasingly being built in industry.

---

## Key Takeaway

A skill is like a **reusable Python library**—you want it to be clear, predictable, and easy to maintain. Skills are much more than prompts; they are **structured, reusable workflows that encode domain expertise**.
