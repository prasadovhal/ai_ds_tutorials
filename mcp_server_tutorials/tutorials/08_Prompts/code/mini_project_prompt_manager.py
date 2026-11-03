"""
Mini Project: Prompt Manager Server
=====================================

This mini project creates a Prompt Manager - an MCP server that
organizes prompts into CATEGORIES and lets clients:

1. Use prompts from different categories (writing, analysis, code)
2. Search prompts by keyword
3. List all available prompts by category

This demonstrates how to build a real-world prompt library
that a team or organization might use.

Categories:
  - Writing: email, report, summary
  - Analysis: data analysis, comparison, trend analysis
  - Code: code review, documentation, refactoring

The server also includes TOOL functions for searching and
listing prompts, since prompts themselves cannot search.

Key concepts:
- Organizing prompts by category
- Combining prompts with tools for discoverability
- Building a practical prompt management system
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("PromptManager")


# ======================================================
# PROMPT CATALOG
# ======================================================
# We store our prompt metadata in a simple dictionary.
# This lets us search and list prompts using tools.
# Each entry has: name, category, description, and keywords.

PROMPT_CATALOG = [
    {
        "name": "write_email",
        "category": "writing",
        "description": "Draft a professional email",
        "keywords": ["email", "message", "communication", "writing"],
    },
    {
        "name": "write_report",
        "category": "writing",
        "description": "Write a structured report",
        "keywords": ["report", "document", "writing", "formal"],
    },
    {
        "name": "write_summary",
        "category": "writing",
        "description": "Summarize text concisely",
        "keywords": ["summary", "summarize", "brief", "writing"],
    },
    {
        "name": "analyze_data",
        "category": "analysis",
        "description": "Analyze a dataset and provide insights",
        "keywords": ["data", "analysis", "statistics", "insights"],
    },
    {
        "name": "compare_options",
        "category": "analysis",
        "description": "Compare multiple options with pros and cons",
        "keywords": ["compare", "comparison", "pros", "cons", "analysis"],
    },
    {
        "name": "analyze_trend",
        "category": "analysis",
        "description": "Analyze trends in time-series data",
        "keywords": ["trend", "time-series", "growth", "analysis"],
    },
    {
        "name": "review_code",
        "category": "code",
        "description": "Review code for bugs and improvements",
        "keywords": ["code", "review", "bugs", "quality"],
    },
    {
        "name": "document_code",
        "category": "code",
        "description": "Generate documentation for code",
        "keywords": ["code", "documentation", "docstring", "comments"],
    },
    {
        "name": "refactor_code",
        "category": "code",
        "description": "Suggest refactoring improvements",
        "keywords": ["code", "refactor", "improve", "clean"],
    },
]


# ======================================================
# WRITING PROMPTS
# ======================================================

@server.prompt()
def write_email(recipient: str, subject: str, key_points: str, tone: str = "professional") -> str:
    """Draft a professional email."""
    return (
        f"Please draft an email:\n\n"
        f"To: {recipient}\n"
        f"Subject: {subject}\n"
        f"Tone: {tone}\n\n"
        f"Key points to cover:\n{key_points}\n\n"
        f"Write a clear, {tone} email with proper greeting and sign-off."
    )


@server.prompt()
def write_report(topic: str, audience: str, sections: str = "introduction, findings, conclusion") -> str:
    """Write a structured report."""
    return (
        f"Please write a structured report:\n\n"
        f"Topic: {topic}\n"
        f"Target Audience: {audience}\n"
        f"Required Sections: {sections}\n\n"
        f"Write a clear, well-organized report with headings "
        f"for each section. Use data and evidence where possible."
    )


@server.prompt()
def write_summary(text: str, max_sentences: str = "3") -> str:
    """Summarize text concisely."""
    return (
        f"Please summarize the following text in {max_sentences} "
        f"sentences or fewer:\n\n"
        f"{text}\n\n"
        f"Focus on the key points and main takeaways."
    )


# ======================================================
# ANALYSIS PROMPTS
# ======================================================

@server.prompt()
def analyze_data(data_description: str, goal: str) -> str:
    """Analyze a dataset and provide insights."""
    return (
        f"Please analyze the following data:\n\n"
        f"Data: {data_description}\n"
        f"Goal: {goal}\n\n"
        f"Provide:\n"
        f"1. Key statistics and metrics\n"
        f"2. Patterns and trends\n"
        f"3. Actionable insights\n"
        f"4. Python code for the analysis\n"
        f"5. Suggested visualizations"
    )


@server.prompt()
def compare_options(options: str, criteria: str) -> str:
    """Compare multiple options with pros and cons."""
    return (
        f"Please compare the following options:\n\n"
        f"Options: {options}\n"
        f"Criteria: {criteria}\n\n"
        f"For each option provide:\n"
        f"1. Pros\n"
        f"2. Cons\n"
        f"3. Best use case\n"
        f"4. Overall recommendation\n\n"
        f"Present as a comparison table if possible."
    )


@server.prompt()
def analyze_trend(data_description: str, time_period: str, metric: str) -> str:
    """Analyze trends in time-series data."""
    return (
        f"Please analyze the following trend:\n\n"
        f"Data: {data_description}\n"
        f"Time Period: {time_period}\n"
        f"Metric: {metric}\n\n"
        f"Provide:\n"
        f"1. Overall trend direction (up, down, stable)\n"
        f"2. Key inflection points\n"
        f"3. Seasonal patterns if any\n"
        f"4. Forecast for the next period\n"
        f"5. Python code for trend analysis"
    )


# ======================================================
# CODE PROMPTS
# ======================================================

@server.prompt()
def review_code(code: str, language: str = "Python") -> str:
    """Review code for bugs and improvements."""
    return (
        f"Please review this {language} code:\n\n"
        f"```{language}\n{code}\n```\n\n"
        f"Check for:\n"
        f"1. Bugs and errors\n"
        f"2. Performance issues\n"
        f"3. Security concerns\n"
        f"4. Code style improvements\n"
        f"5. Suggested refactoring"
    )


@server.prompt()
def document_code(code: str, language: str = "Python") -> str:
    """Generate documentation for code."""
    return (
        f"Please generate documentation for this {language} code:\n\n"
        f"```{language}\n{code}\n```\n\n"
        f"Include:\n"
        f"1. Module/file docstring\n"
        f"2. Function/class docstrings\n"
        f"3. Inline comments for complex logic\n"
        f"4. Usage examples\n"
        f"5. Parameter and return type descriptions"
    )


@server.prompt()
def refactor_code(code: str, goal: str = "improve readability") -> str:
    """Suggest refactoring improvements."""
    return (
        f"Please suggest refactoring for this code:\n\n"
        f"```python\n{code}\n```\n\n"
        f"Goal: {goal}\n\n"
        f"Provide:\n"
        f"1. Issues with the current code\n"
        f"2. Refactored version\n"
        f"3. Explanation of each change\n"
        f"4. Before and after comparison"
    )


# ======================================================
# TOOLS FOR PROMPT DISCOVERY
# ======================================================
# These tools let clients search and browse the prompt catalog.
# Prompts can't search themselves, so we use tools for this.

@server.tool()
def search_prompts(keyword: str) -> str:
    """Search for prompts by keyword. Returns matching prompt names and descriptions."""

    # Convert keyword to lowercase for case-insensitive search
    keyword_lower = keyword.lower()

    # Search through all prompts in the catalog
    matches = []
    for prompt_info in PROMPT_CATALOG:
        # Check if keyword appears in name, description, or keywords list
        name_match = keyword_lower in prompt_info["name"].lower()
        desc_match = keyword_lower in prompt_info["description"].lower()
        keyword_match = any(keyword_lower in kw for kw in prompt_info["keywords"])

        if name_match or desc_match or keyword_match:
            matches.append(prompt_info)

    # Format the results
    if not matches:
        return f"No prompts found matching '{keyword}'."

    result = f"Found {len(matches)} prompt(s) matching '{keyword}':\n\n"
    for match in matches:
        result += f"  - {match['name']} [{match['category']}]\n"
        result += f"    {match['description']}\n\n"

    return result


@server.tool()
def list_prompts_by_category(category: str = "all") -> str:
    """List all prompts, optionally filtered by category (writing, analysis, code, or all)."""

    # Convert category to lowercase for matching
    category_lower = category.lower()

    # Filter prompts by category (or show all)
    if category_lower == "all":
        filtered = PROMPT_CATALOG
    else:
        filtered = [p for p in PROMPT_CATALOG if p["category"] == category_lower]

    # Format the results
    if not filtered:
        return f"No prompts found in category '{category}'."

    result = f"Prompts in '{category}' category:\n\n"

    # Group by category for display
    current_category = ""
    for prompt_info in filtered:
        # Print category header when it changes
        if prompt_info["category"] != current_category:
            current_category = prompt_info["category"]
            result += f"=== {current_category.upper()} ===\n"

        result += f"  - {prompt_info['name']}: {prompt_info['description']}\n"

    result += f"\nTotal: {len(filtered)} prompt(s)"
    return result


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
