"""
Example 1: STDIO Transport Server
====================================

This example creates an MCP server that uses STDIO transport.

STDIO (Standard Input/Output) is the DEFAULT transport for MCP.
When you call server.run() without any arguments, it uses STDIO.

How STDIO works:
  - The CLIENT starts the server as a subprocess
  - Communication happens through stdin (input) and stdout (output)
  - Messages are JSON-RPC formatted
  - One message per line

When to use STDIO:
  - Local development and testing
  - When the client launches the server directly
  - Claude Desktop, Cursor, VS Code use STDIO
  - Simple, no network configuration needed

STDIO is like a phone call:
  - Direct connection between two parties
  - One-to-one communication
  - Ends when either party hangs up

Key concepts:
- STDIO is the default transport (no extra config needed)
- server.run() = server.run(transport="stdio")
- Client must start the server as a child process
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
# The name identifies this server to clients
server = FastMCP("StdioServer")


# Step 2: Add a simple tool so we can test the server
# Tools give the LLM something to call on this server
@server.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! This response came via STDIO transport."


# Step 3: Add another tool for demonstration
@server.tool()
def add_numbers(a: int, b: int) -> str:
    """Add two numbers together."""
    result = a + b
    return f"{a} + {b} = {result} (calculated via STDIO server)"


# Step 4: Add a resource so we can verify it works too
@server.resource("info://server-transport")
def get_transport_info() -> str:
    """Return information about the transport being used."""
    return "This server uses STDIO transport (the default)."


# Step 5: Run the server
# server.run() uses STDIO by default.
# This is exactly the same as server.run(transport="stdio").
# The server will read from stdin and write to stdout.
if __name__ == "__main__":
    # STDIO is the default - no need to specify transport
    # Both of these lines do exactly the same thing:
    #   server.run()              <-- uses STDIO (default)
    #   server.run(transport="stdio")  <-- explicitly STDIO
    server.run()
