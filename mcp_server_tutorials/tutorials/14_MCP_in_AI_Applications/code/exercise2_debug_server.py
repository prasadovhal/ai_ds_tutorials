"""
Exercise 2 - Debug Server (Stub)
=================================
GOAL: Build a server with debugging tools that help you verify
your MCP server is working correctly in any AI application.

REQUIREMENTS:
  1. echo(text) - Returns the text back (test basic tool calls)
  2. ping() - Returns "pong" with a timestamp (test connectivity)
  3. server_status() - Returns uptime and total tool call count
  4. list_capabilities() - Lists all available tools and their descriptions

HINTS:
  - Use datetime module for timestamps and uptime tracking
  - Store server start time and call count in module-level variables
  - Track calls by incrementing a counter in each tool function
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the server
# mcp = FastMCP("???")

# Step 2: Track server state
# _start_time = ???
# _call_count = ???

# Step 3: Implement the tools
# @mcp.tool()
# def echo(text: str) -> str:
#     pass

# @mcp.tool()
# def ping() -> str:
#     pass

# @mcp.tool()
# def server_status() -> str:
#     pass

# @mcp.tool()
# def list_capabilities() -> str:
#     pass


if __name__ == "__main__":
    print("Exercise 2: Build your debug MCP server!")
    print("Edit this file to complete the exercise.")
