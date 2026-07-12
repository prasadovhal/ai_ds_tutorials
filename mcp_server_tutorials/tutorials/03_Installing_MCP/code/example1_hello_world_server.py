"""
Example 1: Hello World MCP Server
==================================
The simplest possible MCP server with one tool.

Setup:
  poetry add mcp
  poetry run python example1_hello_world_server.py
"""

# Step 1: Import FastMCP - this is the main class for creating MCP servers
from mcp.server.fastmcp import FastMCP

# Step 2: Create the server with a name
# The name identifies your server to clients
server = FastMCP("hello-world-server")


# Step 3: Create a tool
# Tools are functions that clients (and AI models) can call
@server.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    # This function receives a name and returns a greeting
    greeting = f"Hello, {name}! Welcome to MCP!"
    return greeting


# Step 4: Run the server
if __name__ == "__main__":
    # This starts the server using STDIO transport
    # The server will wait for messages on stdin and respond on stdout
    print("Starting Hello World MCP Server...")
    server.run()
