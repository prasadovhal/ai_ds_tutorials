"""
Mini Project - Universal Demo MCP Server
==========================================
A comprehensive demo server with:
  - 5 tools: echo, add, uppercase, timestamp, random_number
  - 2 resources: about, help
  - 2 prompts: summarize, translate

Plus: config generation for all supported AI applications
(Claude Desktop, VS Code, Cursor, Continue.dev).
"""

import json
import random
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the universal demo server
mcp = FastMCP("Universal Demo Server")


# ============================================================
# TOOLS (5 tools)
# ============================================================

@mcp.tool()
def echo(text: str) -> str:
    """Echo back the given text. Great for testing connectivity."""
    return f"Echo: {text}"


@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    result = a + b
    return f"{a} + {b} = {result}"


@mcp.tool()
def uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


@mcp.tool()
def timestamp() -> str:
    """Get the current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """Generate a random number between min_val and max_val.

    Args:
        min_val: Minimum value (default: 1)
        max_val: Maximum value (default: 100)
    """
    number = random.randint(min_val, max_val)
    return f"Random number ({min_val}-{max_val}): {number}"


# ============================================================
# RESOURCES (2 resources)
# ============================================================

@mcp.resource("info://about")
def about() -> str:
    """Information about this universal demo server."""
    return (
        "Universal Demo MCP Server v1.0\n"
        "==============================\n\n"
        "A comprehensive demo server for testing MCP integration\n"
        "with any AI application.\n\n"
        "Features:\n"
        "  - 5 tools for various operations\n"
        "  - 2 resources for information\n"
        "  - 2 prompts for common tasks\n\n"
        "Compatible with: Claude Desktop, VS Code, Cursor, Continue.dev"
    )


@mcp.resource("info://help")
def help_text() -> str:
    """Help guide for using this server."""
    return (
        "Universal Demo Server - Help\n"
        "============================\n\n"
        "Tools:\n"
        "  1. echo(text)       - Echo back text\n"
        "  2. add(a, b)        - Add two numbers\n"
        "  3. uppercase(text)  - Convert to uppercase\n"
        "  4. timestamp()      - Get current time\n"
        "  5. random_number()  - Generate random number\n\n"
        "Resources:\n"
        "  - info://about - Server information\n"
        "  - info://help  - This help text\n\n"
        "Prompts:\n"
        "  - summarize(text)           - Summarize text\n"
        "  - translate(text, language)  - Translate text"
    )


# ============================================================
# PROMPTS (2 prompts)
# ============================================================

@mcp.prompt()
def summarize(text: str) -> str:
    """Create a prompt to summarize the given text."""
    return (
        f"Please provide a concise summary of the following text. "
        f"Keep the summary to 2-3 sentences:\n\n{text}"
    )


@mcp.prompt()
def translate(text: str, language: str) -> str:
    """Create a prompt to translate text to another language.

    Args:
        text: The text to translate
        language: Target language (e.g., 'Spanish', 'French')
    """
    return (
        f"Please translate the following text to {language}. "
        f"Preserve the original meaning and tone:\n\n{text}"
    )


# ============================================================
# CONFIG GENERATION
# ============================================================

def generate_all_configs():
    """Print configuration for all AI applications."""
    server_path = __file__
    server_name = "universal-demo"

    configs = {
        "Claude Desktop (~/.config/claude/claude_desktop_config.json)": {
            "mcpServers": {
                server_name: {
                    "command": "python",
                    "args": [server_path]
                }
            }
        },
        "VS Code (.vscode/settings.json)": {
            "github.copilot.chat.mcp": {
                "servers": {
                    server_name: {
                        "command": "python",
                        "args": [server_path],
                        "env": {}
                    }
                }
            }
        },
        "Cursor (.cursor/mcp.json)": {
            "mcpServers": {
                server_name: {
                    "command": "python",
                    "args": [server_path]
                }
            }
        },
        "Continue.dev (~/.continue/config.json)": {
            "mcpServers": [
                {
                    "name": server_name,
                    "command": "python",
                    "args": [server_path]
                }
            ]
        }
    }

    print("=" * 60)
    print("Universal Demo Server - Configuration")
    print("=" * 60)

    for app_name, config in configs.items():
        print(f"\n--- {app_name} ---")
        print(json.dumps(config, indent=2))

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    # Print all configs for all AI apps
    generate_all_configs()

    # Print server capabilities
    print("\nServer Capabilities:")
    print("  Tools:     echo, add, uppercase, timestamp, random_number")
    print("  Resources: info://about, info://help")
    print("  Prompts:   summarize, translate")
    print("\nStarting Universal Demo Server...")

    # Run the server
    mcp.run()
