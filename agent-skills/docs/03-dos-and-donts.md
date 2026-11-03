# Skills: Do's and Don'ts

## ✅ DO'S

### 1. Give the Skill One Responsibility
A skill should solve one problem well.

**Examples:**
- ✅ Review a research paper
- ✅ Analyze a CSV
- ✅ Review a pull request

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

**Example:**
- Summary
- Strengths
- Weaknesses
- Recommendations
- Next steps

Consistent outputs make downstream automation easier.

### 5. Break Work into Ordered Steps
Instead of saying:
> Analyze the dataset.

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
- ❌ customer_data.csv

Prefer:
- ✅ "the provided CSV file"

### 9. Explain Reasoning When Appropriate
For analytical tasks, require justification.

Instead of:
> Use XGBoost.

Use:
> Select the model and explain why it fits the dataset.

### 10. Make the Skill Deterministic
If the same input is given twice, the workflow should behave similarly.

---

## ❌ DON'Ts

### 1. Don't Make One Huge Skill
Avoid creating a "Master Data Science Skill" containing 40 different tasks.

**Solution:** Break it into focused skills.

### 2. Don't Hardcode Values
Avoid:
- API keys
- File paths
- Table names
- Dataset names

### 3. Don't Assume Missing Information
Instead of guessing:
> The target column is churn.

Ask for clarification or infer carefully from the data.

### 4. Don't Duplicate Skills
Avoid creating:
- CSV Analyzer
- Dataset Analyzer
- CSV Reviewer

If they do the same thing, consolidate them.

### 5. Don't Force Unnecessary Tools
Don't always call Python or web search if the task can be completed without them.

### 6. Don't Ignore Edge Cases
Consider:
- Empty CSV
- Single-row dataset
- Missing target column
- Invalid SQL

### 7. Don't Mix Business Logic with Tool Logic
❌ **Bad:**
> Call Python and always use Random Forest.

✅ **Better:**
> Choose an appropriate model based on the dataset characteristics.

### 8. Don't Make Outputs Inconsistent
**Bad:** Sometimes returns JSON, sometimes Markdown, sometimes plain text.

**Solution:** Pick one format unless flexibility is required.

### 9. Don't Over-constrain the Model
Avoid instructions like:
> Always use XGBoost.

Prefer:
> Select the most appropriate algorithm and justify the choice.

### 10. Don't Make Skills Dependent on Conversation History
A good skill should work even if it's invoked independently.

---

## Quick Checklist Before Saving a Skill

Ask yourself:

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

---

## Key Principles Summary

| Do This | Don't Do This |
|---------|---------------|
| One clear responsibility | Mix multiple responsibilities |
| Explicit inputs/outputs | Assume user intent |
| Reusable variables | Hardcode paths/names |
| Ordered steps | Vague instructions |
| Handle edge cases | Ignore error conditions |
| Consistent output format | Mix different formats |
| Explain model choices | Force specific models |
| Independent execution | Depend on history |
| Flexible tool usage | Lock to specific tools |
| Deterministic behavior | Random variations |

---

## Context: Why These Matter

These best practices exist because:

1. **Clarity** → Agents can select and execute the right skill
2. **Reusability** → Skills work across different projects
3. **Maintainability** → Other engineers can understand and modify them
4. **Reliability** → Consistent behavior makes testing easier
5. **Scalability** → Well-designed skills compose into larger workflows

For a Principal Data Scientist working on GenAI systems, mastering these principles is essential for building maintainable agent platforms.
