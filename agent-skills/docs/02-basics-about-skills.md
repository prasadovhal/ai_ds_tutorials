# Basics About Skills

## Best Practices for Writing Skills

This is one of the most important things to learn if you want to build production-quality agents. Think of an agent skill like writing a reusable Python library—you want it to be clear, predictable, and easy to maintain.

### 1. Give the Skill One Responsibility

A skill should solve **one problem well**.

**✅ Good examples:**
- Review a research paper
- Analyze a CSV
- Review a pull request

**❌ Bad examples:**
- Analyze CSV + train model + deploy model + email stakeholders

### 2. Clearly Define When to Use It

Tell the agent when this skill is appropriate.

**Example:**
- Use this skill when the user uploads a research paper and asks for a technical review
- Do not use it for blog posts or news articles

### 3. Define the Expected Input

State what the skill expects.

**Examples:**
- CSV file
- PDF
- SQL query
- Python code
- GitHub repository

### 4. Define the Expected Output

Specify exactly what the result should look like.

**Example output:**
- Summary
- Strengths
- Weaknesses
- Recommendations
- Next steps

Consistent outputs make downstream automation easier.

### 5. Break Work into Ordered Steps

Instead of saying:
> "Analyze the dataset."

Write:
1. Validate input
2. Check missing values
3. Detect duplicates
4. Identify outliers
5. Summarize findings
6. Recommend next actions

### 6. Tell the Agent Which Tools to Use

**Example:**
- Use Python for statistics
- Use SQL for database queries
- Use web search only when external information is required

### 7. Handle Common Failure Cases

Include guidance such as:
- Missing columns
- Empty files
- Corrupted PDFs
- Unsupported formats

### 8. Keep Skills Reusable

Avoid references like:
- ❌ `customer_data.csv`

Prefer:
- ✅ "the provided CSV file"

### 9. Explain Reasoning When Appropriate

For analytical tasks, require justification.

Instead of:
> "Use XGBoost."

Use:
> "Select the model and explain why it fits the dataset."

### 10. Make the Skill Deterministic

If the same input is given twice, the workflow should behave similarly.

## Skill Components Checklist

Before saving a skill, ask yourself these questions:

### Core Questions
- ✅ Does it solve one problem?
- ✅ Is the purpose clear?
- ✅ Are inputs defined?
- ✅ Are outputs defined?
- ✅ Are the steps easy to follow?
- ✅ Are tool choices explained?
- ✅ Are error cases handled?
- ✅ Is it reusable?
- ✅ Will it behave consistently?
- ✅ Could another engineer understand and maintain it?

## Recommended Model Selection

Should the skill enforce which model to use?

**Usually no.**

Instead of:
> "Use Opus."

Prefer:
> "Recommended: Opus (or the strongest available reasoning model).
> Fallback: Sonnet if Opus is unavailable."

This keeps the skill portable.

### Rule of Thumb: Task to Model Mapping

| Task | Recommended Model Class |
|------|------------------------|
| Summarize article | Small/Fast (e.g., Haiku) |
| Rewrite email | Small/Fast |
| Translate text | Small/Fast |
| Generate SQL | Medium |
| Debug code | Medium–Large |
| Review pull request | Large |
| Research paper review | Large (e.g., Opus) |
| Design an agent architecture | Large |
| Evaluate LLM outputs | Large |

**The principle:** The more the task depends on reasoning and judgment, the stronger the model should generally be.

## Skill vs Agent vs Orchestration

For someone at your level (aiming for Principal Data Scientist), think of it this way:

- **Tool** = a Python function (small, focused capability)
- **Skill** = a reusable pipeline (orchestrates multiple tools with domain knowledge)
- **Agent workflow** = a system that coordinates multiple skills to solve larger business problems

This mental model maps well across Claude, Cursor, ChatGPT, and most modern agent frameworks.

## Anti-patterns to Avoid

### 1. One Huge Skill
Avoid creating a "Master Data Science Skill" containing 40 different tasks.

**Solution:** Break it into focused skills.

### 2. Hardcoded Values
Avoid hardcoding:
- API keys
- File paths
- Table names
- Dataset names

### 3. Assumption of Missing Information
Instead of guessing "The target column is churn," ask for clarification or infer carefully from the data.

### 4. Duplicate Skills
Avoid creating:
- CSV Analyzer
- Dataset Analyzer
- CSV Reviewer

If they do the same thing, consolidate them.

### 5. Forcing Unnecessary Tools
Don't always call Python or web search if the task can be completed without them.

### 6. Ignoring Edge Cases
Consider:
- Empty CSV
- Single-row dataset
- Missing target column
- Invalid SQL

### 7. Mixing Business Logic with Tool Logic
**❌ Bad:** "Call Python and always use Random Forest."

**✅ Good:** "Choose an appropriate model based on the dataset characteristics."

### 8. Inconsistent Output Formats
**Bad:** Sometimes returns JSON, sometimes Markdown, sometimes plain text.

**Solution:** Pick one format unless flexibility is required.

### 9. Over-constraining the Model
Avoid instructions like:
> "Always use XGBoost."

Prefer:
> "Select the most appropriate algorithm and justify the choice."

### 10. Dependencies on Conversation History
A good skill should work even if it's invoked independently.

## Key Principle: Separation of Concerns

Three different concepts should remain separate:

1. **Skill** = "How should this task be done?"
2. **Model Selection** = "Which model is best suited to execute it?"
3. **Tool Implementation** = "What capability does this perform?"

These are separate concerns and should be designed independently.

---

## Summary

A well-written skill is:
- **Clear** about its purpose and scope
- **Reusable** across different contexts
- **Deterministic** and predictable
- **Maintainable** by other engineers
- **Independent** of conversation history
- **Flexible** about underlying tools and models
