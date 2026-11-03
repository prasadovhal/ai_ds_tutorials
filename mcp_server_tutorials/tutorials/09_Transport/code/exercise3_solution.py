"""
Exercise 3 Solution: Transport Switcher
========================================
Server that chooses transport based on CLI args or env var.

Usage:
  python exercise3_solution.py                    # STDIO (default)
  python exercise3_solution.py --transport=sse    # SSE
  MCP_TRANSPORT=sse python exercise3_solution.py  # SSE via env var
"""

import sys
import os
from mcp.server.fastmcp import FastMCP

# Create the server
server = FastMCP("transport-switcher")


@server.tool()
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"


@server.tool()
def get_transport_info() -> str:
    """Return which transport this server is using."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    return f"This server is running with {transport} transport"


def get_transport():
    """Determine which transport to use from CLI args or env var."""

    # Step 1: Check command-line arguments
    for arg in sys.argv:
        if arg.startswith("--transport="):
            transport = arg.split("=")[1].lower()
            return transport

    # Step 2: Check environment variable
    env_transport = os.environ.get("MCP_TRANSPORT", "")
    if env_transport:
        return env_transport.lower()

    # Step 3: Default to STDIO
    return "stdio"


if __name__ == "__main__":
    # Determine the transport
    transport = get_transport()

    # Validate the transport choice
    valid_transports = ["stdio", "sse"]
    if transport not in valid_transports:
        print(f"ERROR: Unknown transport '{transport}'")
        print(f"Valid options: {valid_transports}")
        sys.exit(1)

    # Set env var so tools can report it
    os.environ["MCP_TRANSPORT"] = transport

    print(f"Starting server with {transport.upper()} transport...")

    # Run with the chosen transport
    server.run(transport=transport)
