"""
Example 3: SSE (Server-Sent Events) Transport Server
======================================================

This example creates an MCP server that uses SSE transport.

SSE (Server-Sent Events) runs the server as an HTTP server.
Clients connect to it over the network using HTTP.

How SSE works:
  - The server starts an HTTP server on a host and port
  - Clients connect via HTTP (like a web browser)
  - The server sends events to the client over a long-lived connection
  - The client sends requests via HTTP POST

When to use SSE:
  - Remote servers (server runs on a different machine)
  - Multiple clients need to connect to the same server
  - Web-based MCP clients
  - Server needs to stay running independently

SSE is like a radio station:
  - The server broadcasts on a specific address (host:port)
  - Any client can tune in if they know the address
  - The server runs independently of any client

STDIO vs SSE:
  - STDIO: Client starts server, 1-to-1, local only
  - SSE:   Server runs independently, many-to-1, can be remote

Key concepts:
- server.run(transport="sse") starts an HTTP server
- Default host is "0.0.0.0" (all interfaces), default port is 8000
- Clients connect via HTTP to the server's URL
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
# We can set the host and port when creating the server
server = FastMCP(
    "SSEServer",
    host="0.0.0.0",   # Listen on all network interfaces
    port=8000,         # Listen on port 8000
)


# Step 2: Add tools (same as any MCP server)
# The tools work exactly the same regardless of transport
@server.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! This response came via SSE transport."


@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together."""
    result = a * b
    return f"{a} * {b} = {result} (calculated via SSE server)"


# Step 3: Add a resource
@server.resource("info://server-transport")
def get_transport_info() -> str:
    """Return information about the transport being used."""
    return "This server uses SSE transport on http://0.0.0.0:8000"


# Step 4: Run the server with SSE transport
# This starts an HTTP server that listens for connections.
# The server will keep running until you press Ctrl+C.
#
# After starting, clients can connect to:
#   http://localhost:8000/sse
#
# To test, run this script in one terminal,
# then run example4_sse_client.py in another terminal.
if __name__ == "__main__":
    print("Starting SSE server on http://0.0.0.0:8000")
    print("Press Ctrl+C to stop the server")
    print()

    # The key difference: transport="sse"
    # This tells FastMCP to start an HTTP server instead of using STDIO
    server.run(transport="sse")
