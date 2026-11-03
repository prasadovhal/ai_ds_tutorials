"""
Exercise 2 Solution: SSE Server-Client Pair
============================================
Run with --server to start the SSE server.
Run with --client to connect and test.

Usage:
  Terminal 1: python exercise2_solution.py --server
  Terminal 2: python exercise2_solution.py --client
"""

import sys
import asyncio
from mcp.server.fastmcp import FastMCP

# ============================================================
# SERVER
# ============================================================

server = FastMCP("sse-exercise-server")


@server.tool()
def echo(message: str) -> str:
    """Echo a message back."""
    return f"Echo: {message}"


@server.tool()
def word_count(text: str) -> str:
    """Count words in text."""
    words = text.split()
    count = len(words)
    return f"Word count: {count}"


def run_server():
    """Start the server with SSE transport."""
    print("Starting SSE server on http://localhost:8000...")
    print("Press Ctrl+C to stop.\n")
    # Run with SSE transport on port 8000
    server.run(transport="sse")


# ============================================================
# CLIENT
# ============================================================

async def run_client():
    """Connect to the SSE server and test tools."""
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession

    server_url = "http://localhost:8000/sse"
    print(f"Connecting to {server_url}...")

    try:
        async with sse_client(server_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Connected via SSE!\n")

                # List tools
                tools = await session.list_tools()
                print("Available tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}")

                # Test echo
                print("\nCalling echo('Hello SSE!')...")
                result = await session.call_tool("echo", {"message": "Hello SSE!"})
                print(f"Result: {result.content[0].text}")

                # Test word_count
                print("\nCalling word_count('MCP is great for AI')...")
                result = await session.call_tool("word_count", {"text": "MCP is great for AI"})
                print(f"Result: {result.content[0].text}")

                print("\nAll SSE tests passed!")

    except ConnectionRefusedError:
        print("ERROR: Server not running. Start it first with --server flag.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    if "--server" in sys.argv:
        run_server()
    elif "--client" in sys.argv:
        asyncio.run(run_client())
    else:
        print("Usage:")
        print("  python exercise2_solution.py --server   (start SSE server)")
        print("  python exercise2_solution.py --client   (connect and test)")
