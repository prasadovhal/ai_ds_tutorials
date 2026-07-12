"""
Example 4: Server with Tools + Resources + Prompts
====================================================
This server combines ALL THREE building blocks of MCP:
    - Tools: actions the server can perform
    - Resources: data the server exposes (read-only)
    - Prompts: reusable LLM interaction templates

This is what a real MCP server looks like - it exposes
multiple capabilities that clients can discover and use.

What you will learn:
    - How to combine tools, resources, and prompts
    - How clients discover all server capabilities
    - A realistic server structure

How to run:
    poetry run mcp dev example4_server_all_features.py

How to test:
    Open MCP Inspector
    Check the Tools tab - you should see "add" and "multiply"
    Check the Resources tab - you should see "info://server" and "info://help"
    Check the Prompts tab - you should see "summarize" and "translate"
"""

# ============================================================
# STEP 1: Imports
# ============================================================
from mcp.server.fastmcp import FastMCP
import platform
import datetime

# ============================================================
# STEP 2: Create the server
# ============================================================
# This single server instance will hold all our tools,
# resources, and prompts. Think of it as a kitchen that
# can cook food (tools), display information (resources),
# and provide recipe templates (prompts).
server = FastMCP("AllFeaturesServer")

# ============================================================
# TOOLS SECTION
# ============================================================
# Tools are actions. They take inputs and produce outputs.
# They can have side effects (but these two are pure math).

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    result = a + b
    return result

@server.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    result = a * b
    return result

@server.tool()
def get_length(text: str) -> int:
    """Get the length of a text string."""
    length = len(text)
    return length

# ============================================================
# RESOURCES SECTION
# ============================================================
# Resources are read-only data. Clients can list them
# and read their contents, but cannot modify them.

@server.resource("info://server")
def get_server_info() -> str:
    """Get information about this MCP server."""

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    python_version = platform.python_version()
    os_name = platform.system()

    info = f"""Server: AllFeaturesServer
Time: {current_time}
Python: {python_version}
OS: {os_name}
Capabilities: tools, resources, prompts"""

    return info

@server.resource("info://help")
def get_help() -> str:
    """Get help about using this server."""

    help_text = """AllFeaturesServer Help
======================

Tools available:
  - add(a, b): Add two numbers
  - multiply(a, b): Multiply two numbers
  - get_length(text): Get string length

Resources available:
  - info://server: Server information
  - info://help: This help text

Prompts available:
  - summarize: Summarize text
  - translate: Translate text"""

    return help_text

# ============================================================
# PROMPTS SECTION
# ============================================================
# Prompts are reusable templates for LLM interactions.
# They help standardize how clients interact with LLMs.

@server.prompt()
def summarize(text: str) -> str:
    """Summarize the given text."""

    prompt = f"""Please provide a concise summary of the following text.
Keep it to 2-3 sentences.

Text:
{text}

Summary:"""

    return prompt

@server.prompt()
def translate(text: str, target_language: str) -> str:
    """Translate text to a target language."""

    prompt = f"""Translate the following text to {target_language}.
Keep the meaning and tone as close to the original as possible.

Original text:
{text}

Translation to {target_language}:"""

    return prompt

# ============================================================
# RUN THE SERVER
# ============================================================
if __name__ == "__main__":
    server.run()
