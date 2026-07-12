"""
Example 2: Parameterized Prompts
=================================

This example shows how to create prompts that accept multiple
parameters, including parameters with default values.

Parameters let you customize how the prompt behaves.
For example, a translation prompt needs to know:
  - What text to translate
  - What language to translate to

Default values make some parameters optional.
The client can override them or use the defaults.

Key concepts:
- Multiple parameters in a prompt
- Default parameter values
- Different prompt purposes (translate, summarize, analyze)
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("ParameterizedPrompts")


# ---- Prompt 1: Translate Text ----
# This prompt takes TWO parameters:
#   - text: the text to translate (required)
#   - target_language: the language to translate into (required)
# Both parameters are required because they have no default values.
@server.prompt()
def translate(text: str, target_language: str) -> str:
    """Translate text to a target language."""
    return (
        f"Please translate the following text to {target_language}.\n"
        f"Keep the meaning and tone as close to the original as possible.\n\n"
        f"Text to translate:\n{text}"
    )


# ---- Prompt 2: Summarize with Length Control ----
# This prompt has a DEFAULT VALUE for max_length.
# If the client doesn't specify max_length, it defaults to "short".
# This makes the parameter optional.
@server.prompt()
def summarize(text: str, max_length: str = "short") -> str:
    """Summarize text with a specified length (short, medium, long)."""

    # Build different instructions based on the length parameter
    if max_length == "short":
        length_instruction = "Provide a brief 1-2 sentence summary."
    elif max_length == "medium":
        length_instruction = "Provide a summary of about one paragraph."
    else:
        length_instruction = "Provide a detailed summary covering all key points."

    return (
        f"Please summarize the following text.\n"
        f"{length_instruction}\n\n"
        f"Text:\n{text}"
    )


# ---- Prompt 3: Analyze Sentiment ----
# This prompt takes just one parameter: the text to analyze.
# It asks the LLM to determine the emotional tone of the text.
@server.prompt()
def analyze_sentiment(text: str) -> str:
    """Analyze the sentiment/emotion in the given text."""
    return (
        f"Please analyze the sentiment of the following text.\n"
        f"Identify whether it is positive, negative, or neutral.\n"
        f"Also note any specific emotions detected "
        f"(joy, anger, sadness, etc.).\n\n"
        f"Text to analyze:\n{text}"
    )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
