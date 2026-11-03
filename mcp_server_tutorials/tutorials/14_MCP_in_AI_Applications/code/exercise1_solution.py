"""
Exercise 1 Solution - Multi-App MCP Server
===========================================
A server with multiple tools, a resource, and a prompt that
works seamlessly across Claude Desktop and VS Code.
"""

import json
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Multi-App Server")


# --- Tool 1: greet ---
@mcp.tool()
def greet(name: str) -> str:
    """Generate a friendly greeting for someone."""
    return f"Hello, {name}! Welcome to the Multi-App MCP Server!"


# --- Tool 2: calculate ---
@mcp.tool()
def calculate(expression: str) -> str:
    """Safely evaluate a math expression (e.g., '2 + 3 * 4').

    Args:
        expression: A math expression using +, -, *, /, **, (, )
    """
    # Only allow safe math characters
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: Only numbers and +, -, *, /, **, (, ) are allowed."
    try:
        result = eval(expression)  # Safe because we filtered characters
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# --- Tool 3: word_count ---
@mcp.tool()
def word_count(text: str) -> str:
    """Count words, characters, and lines in the given text."""
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())
    return f"Words: {words}, Characters: {chars}, Lines: {lines}"


# --- Resource: server help ---
@mcp.resource("info://server/help")
def server_help() -> str:
    """Return help information about this server and its capabilities."""
    return (
        "Multi-App MCP Server - Help\n"
        "===========================\n\n"
        "Tools:\n"
        "  - greet(name): Generate a greeting\n"
        "  - calculate(expression): Evaluate math expressions\n"
        "  - word_count(text): Count words, chars, lines\n\n"
        "Resources:\n"
        "  - info://server/help: This help text\n\n"
        "Prompts:\n"
        "  - review_code(code): Code review prompt template"
    )


# --- Prompt: code review ---
@mcp.prompt()
def review_code(code: str) -> str:
    """Generate a prompt to review the given code."""
    return (
        f"Please review the following code for:\n"
        f"1. Bugs and potential errors\n"
        f"2. Code style and readability\n"
        f"3. Performance improvements\n"
        f"4. Security concerns\n\n"
        f"Code to review:\n```\n{code}\n```"
    )


def print_configs():
    """Print configuration for both Claude Desktop and VS Code."""
    server_path = __file__

    # Claude Desktop config
    claude_config = {
        "mcpServers": {
            "multi-app-server": {
                "command": "python",
                "args": [server_path]
            }
        }
    }

    # VS Code config
    vscode_config = {
        "github.copilot.chat.mcp": {
            "servers": {
                "multi-app-server": {
                    "command": "python",
                    "args": [server_path],
                    "env": {}
                }
            }
        }
    }

    print("=" * 60)
    print("Claude Desktop Config:")
    print(json.dumps(claude_config, indent=2))
    print("\nVS Code Config (.vscode/settings.json):")
    print(json.dumps(vscode_config, indent=2))
    print("=" * 60)


if __name__ == "__main__":
    # Print configs for both apps
    print_configs()
    # Start the server
    mcp.run()
