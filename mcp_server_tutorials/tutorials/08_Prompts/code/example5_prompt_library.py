"""
Example 5: Prompt Library
==========================

This example creates a LIBRARY of useful, reusable prompts.

In a real project, you might have many prompts organized by
purpose. This server provides 6 different prompts covering
common use cases:
  1. Code Review
  2. Bug Report
  3. Feature Request
  4. Meeting Notes
  5. Email Draft
  6. Data Analysis

Each prompt is a carefully crafted template that produces
consistent, high-quality results from the LLM.

Key concepts:
- Building a collection of related prompts
- Each prompt focused on a specific task
- Using parameters to customize each prompt
- Consistent formatting across all prompts
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("PromptLibrary")


# ---- Prompt 1: Code Review ----
# A thorough code review prompt that checks multiple aspects.
@server.prompt()
def code_review(code: str, language: str = "Python") -> str:
    """Perform a thorough code review."""
    return (
        f"Please perform a thorough code review of the following "
        f"{language} code.\n\n"
        f"Check for:\n"
        f"1. Correctness - Does the code do what it should?\n"
        f"2. Readability - Is the code easy to understand?\n"
        f"3. Performance - Are there any slow operations?\n"
        f"4. Security - Are there any vulnerabilities?\n"
        f"5. Best Practices - Does it follow {language} conventions?\n\n"
        f"Code:\n```{language}\n{code}\n```\n\n"
        f"Provide specific suggestions with code examples where possible."
    )


# ---- Prompt 2: Bug Report ----
# Helps create a structured bug report from raw information.
@server.prompt()
def bug_report(
    title: str,
    description: str,
    steps_to_reproduce: str,
    expected_behavior: str = "Not specified",
    actual_behavior: str = "Not specified",
) -> str:
    """Create a structured bug report."""
    return (
        f"Please create a well-structured bug report from the "
        f"following information.\n\n"
        f"Title: {title}\n\n"
        f"Description: {description}\n\n"
        f"Steps to Reproduce:\n{steps_to_reproduce}\n\n"
        f"Expected Behavior: {expected_behavior}\n\n"
        f"Actual Behavior: {actual_behavior}\n\n"
        f"Format the report with clear sections. "
        f"Add a severity assessment (Critical/High/Medium/Low). "
        f"Suggest possible causes if apparent."
    )


# ---- Prompt 3: Feature Request ----
# Helps write a clear feature request document.
@server.prompt()
def feature_request(
    feature_name: str,
    problem: str,
    proposed_solution: str = "Not specified",
) -> str:
    """Write a clear feature request document."""
    return (
        f"Please write a feature request document for:\n\n"
        f"Feature Name: {feature_name}\n\n"
        f"Problem it solves: {problem}\n\n"
        f"Proposed Solution: {proposed_solution}\n\n"
        f"Please include:\n"
        f"1. A clear problem statement\n"
        f"2. The proposed solution with details\n"
        f"3. User stories (As a user, I want to...)\n"
        f"4. Acceptance criteria\n"
        f"5. Potential alternatives considered\n"
        f"6. Impact assessment"
    )


# ---- Prompt 4: Meeting Notes ----
# Helps organize raw meeting notes into a structured format.
@server.prompt()
def meeting_notes(
    raw_notes: str,
    meeting_type: str = "general",
) -> str:
    """Organize raw meeting notes into a structured format."""
    return (
        f"Please organize the following raw meeting notes into a "
        f"clear, structured format.\n\n"
        f"Meeting Type: {meeting_type}\n\n"
        f"Raw Notes:\n{raw_notes}\n\n"
        f"Please structure the notes with:\n"
        f"1. Meeting Summary (2-3 sentences)\n"
        f"2. Key Discussion Points\n"
        f"3. Decisions Made\n"
        f"4. Action Items (with owners if mentioned)\n"
        f"5. Follow-up Items\n"
        f"6. Next Meeting Topics (if any)"
    )


# ---- Prompt 5: Email Draft ----
# Helps draft professional emails.
@server.prompt()
def email_draft(
    recipient: str,
    subject: str,
    key_points: str,
    tone: str = "professional",
) -> str:
    """Draft a professional email."""
    return (
        f"Please draft an email with the following details:\n\n"
        f"To: {recipient}\n"
        f"Subject: {subject}\n"
        f"Tone: {tone}\n\n"
        f"Key points to cover:\n{key_points}\n\n"
        f"Please write a complete email that is:\n"
        f"- Clear and concise\n"
        f"- Appropriate for the {tone} tone\n"
        f"- Well-structured with proper greeting and sign-off\n"
        f"- Free of jargon unless necessary"
    )


# ---- Prompt 6: Data Analysis ----
# Helps analyze data and provide insights.
@server.prompt()
def data_analysis(
    data_description: str,
    analysis_goal: str,
    data_format: str = "CSV",
) -> str:
    """Guide data analysis for a given dataset."""
    return (
        f"Please help analyze the following data:\n\n"
        f"Data Description: {data_description}\n"
        f"Data Format: {data_format}\n"
        f"Analysis Goal: {analysis_goal}\n\n"
        f"Please provide:\n"
        f"1. Recommended analysis approach\n"
        f"2. Key metrics to calculate\n"
        f"3. Suggested visualizations\n"
        f"4. Potential insights to look for\n"
        f"5. Python code using pandas to perform the analysis\n"
        f"6. How to interpret the results"
    )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
