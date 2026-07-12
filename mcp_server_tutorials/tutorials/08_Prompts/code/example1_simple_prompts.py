"""
Example 1: Simple Prompts
=========================

This example shows how to create simple prompts using the
@server.prompt() decorator in MCP.

Prompts are reusable text templates that the LLM can use.
Think of them like "saved instructions" that a client can
request from the server.

Unlike tools (which DO something), prompts just RETURN TEXT
that guides the LLM on how to respond.

Key concepts:
- Creating prompts with @server.prompt()
- Returning a simple string from a prompt
- Each prompt takes parameters and returns formatted text
- The client can list and use these prompts
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
# The name "PromptDemo" identifies this server to clients
server = FastMCP("PromptDemo")


# ---- Prompt 1: Summarize Text ----
# This prompt takes some text and asks the LLM to summarize it.
# The @server.prompt() decorator registers this function as a prompt.
# When a client requests this prompt with some text,
# it returns a formatted instruction string.
@server.prompt()
def summarize_text(text: str) -> str:
    """Summarize the given text concisely."""
    # We simply return a string that tells the LLM what to do
    # The LLM will receive this string as its instruction
    return f"Please summarize the following text:\n\n{text}"


# ---- Prompt 2: Explain Code ----
# This prompt takes a code snippet and asks the LLM to explain it.
# This is useful when you want the LLM to break down what code does.
@server.prompt()
def explain_code(code: str) -> str:
    """Explain the given code in simple terms."""
    # Return a clear instruction for the LLM
    # The code is embedded in the prompt text
    return f"Please explain this code in simple terms:\n\n```\n{code}\n```"


# ---- Run the server ----
# When this script runs, it starts the MCP server.
# Clients can then connect and use these prompts.
# The server uses STDIO transport by default.
if __name__ == "__main__":
    server.run()
