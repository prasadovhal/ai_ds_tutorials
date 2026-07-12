"""
Exercise 1 - Multi-App MCP Server (Stub)
=========================================
GOAL: Build a server that works seamlessly across Claude Desktop
and VS Code. It should have multiple tools, at least one resource,
and at least one prompt.

REQUIREMENTS:
  1. Create at least 3 tools (e.g., greet, calculate, word_count)
  2. Create at least 1 resource (e.g., server info or help text)
  3. Create at least 1 prompt (e.g., a code review prompt)
  4. Print the config JSON for both Claude Desktop and VS Code

HINTS:
  - Use `from mcp.server.fastmcp import FastMCP`
  - Use @mcp.tool() for tools
  - Use @mcp.resource("uri://...") for resources
  - Use @mcp.prompt() for prompts
  - The server should work with both apps without changes
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the server
# mcp = FastMCP("???")

# Step 2: Add your tools
# @mcp.tool()
# def greet(name: str) -> str:
#     """..."""
#     pass

# Step 3: Add a resource
# @mcp.resource("info://???")
# def server_help() -> str:
#     """..."""
#     pass

# Step 4: Add a prompt
# @mcp.prompt()
# def review_code(code: str) -> str:
#     """..."""
#     pass

# Step 5: Print configs for Claude Desktop and VS Code


if __name__ == "__main__":
    # TODO: Print configs, then run the server
    print("Exercise 1: Build your multi-app MCP server!")
    print("Edit this file to complete the exercise.")
