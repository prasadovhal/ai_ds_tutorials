"""
Example 1: Minimal MCP Server
==============================
This is the absolute simplest MCP server you can build.
It has ONE tool: add two numbers together.

What you will learn:
    - How to import FastMCP
    - How to create a server instance
    - How to register a tool using the @server.tool() decorator
    - How to run the server

How to run:
    poetry run mcp dev example1_minimal_server.py

How to test:
    Open MCP Inspector in your browser (it opens automatically)
    Go to the Tools tab
    Call the "add" tool with a=5 and b=3
    You should see the result: 8
"""

# ============================================================
# STEP 1: Import FastMCP
# ============================================================
# FastMCP is the main class for building MCP servers.
# It handles all the protocol details for you:
#   - JSON-RPC message parsing
#   - Transport management (stdio by default)
#   - Request routing (tools, resources, prompts)
#   - Error handling
from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 2: Create a server instance
# ============================================================
# Give your server a name. This name is sent to clients
# during the initialization phase so they know who they
# are talking to.
# Think of this as naming your restaurant kitchen.
server = FastMCP("MinimalServer")

# ============================================================
# STEP 3: Register a tool
# ============================================================
# The @server.tool() decorator registers this function as
# an MCP tool. When a client calls "add", this function runs.
#
# IMPORTANT: Type hints (a: int, b: int) are required!
# FastMCP uses them to generate the JSON Schema that tells
# clients what arguments the tool expects.
#
# The docstring becomes the tool's description.
# Clients and LLMs read this description to understand
# what the tool does.
@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together and return the result."""
    # This is the actual logic of the tool.
    # It is just plain Python - nothing special.
    result = a + b
    return result

# ============================================================
# STEP 4: Run the server
# ============================================================
# This starts the server and makes it listen for connections.
# By default, it uses stdio transport (reads from stdin,
# writes to stdout).
#
# The if __name__ == "__main__" guard ensures the server
# only starts when you run this file directly, not when
# it is imported by another file.
if __name__ == "__main__":
    server.run()
