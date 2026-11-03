"""
Exercise 1 Solution: Writing Style Prompts
============================================

This solution creates 3 prompts for different writing styles:
formal, casual, and technical.

Each prompt takes text and a context parameter,
then returns instructions for the LLM to rewrite the text
in the specified style.
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("WritingStyleSolution")


# ---- Prompt 1: Formal Style ----
# This prompt rewrites text in a formal, professional tone.
# The "audience" parameter helps tailor the formality level.
@server.prompt()
def formal_style(text: str, audience: str) -> str:
    """Rewrite text in a formal, professional tone."""
    return (
        f"Please rewrite the following text in a formal, "
        f"professional tone suitable for {audience}.\n\n"
        f"Guidelines:\n"
        f"- Use proper grammar and complete sentences\n"
        f"- Avoid contractions (use 'do not' instead of 'don't')\n"
        f"- Use industry-appropriate vocabulary\n"
        f"- Maintain a respectful and authoritative tone\n"
        f"- Keep the core message intact\n\n"
        f"Original text:\n{text}"
    )


# ---- Prompt 2: Casual Style ----
# This prompt rewrites text in a casual, friendly tone.
# The "context" parameter specifies where the text will be used.
@server.prompt()
def casual_style(text: str, context: str) -> str:
    """Rewrite text in a casual, friendly tone."""
    return (
        f"Please rewrite the following text in a casual, "
        f"friendly tone appropriate for {context}.\n\n"
        f"Guidelines:\n"
        f"- Use conversational language\n"
        f"- Contractions are fine (don't, won't, can't)\n"
        f"- Keep it approachable and warm\n"
        f"- Use simple words over complex ones\n"
        f"- Feel free to use common expressions\n\n"
        f"Original text:\n{text}"
    )


# ---- Prompt 3: Technical Style ----
# This prompt rewrites text in a technical, precise tone.
# The "domain" parameter specifies the technical field.
@server.prompt()
def technical_style(text: str, domain: str) -> str:
    """Rewrite text in a technical, precise tone."""
    return (
        f"Please rewrite the following text in a technical, "
        f"precise tone for the {domain} domain.\n\n"
        f"Guidelines:\n"
        f"- Use domain-specific terminology for {domain}\n"
        f"- Be precise and unambiguous\n"
        f"- Include relevant technical details\n"
        f"- Use proper technical formatting (code, formulas, etc.)\n"
        f"- Maintain accuracy above all else\n\n"
        f"Original text:\n{text}"
    )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
