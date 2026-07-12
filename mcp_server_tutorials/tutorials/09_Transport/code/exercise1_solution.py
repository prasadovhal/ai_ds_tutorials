"""
Exercise 1 Solution: STDIO Server-Client Pair
==============================================
This file contains both a server and a client.
Run with --server flag to start server mode.
Run without flags to start client mode (which launches server as subprocess).
"""

import sys
import asyncio
from mcp.server.fastmcp import FastMCP


# ============================================================
# SERVER PART
# ============================================================

server = FastMCP("stdio-exercise-server")


@server.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! This message came via STDIO transport."


@server.tool()
def reverse(text: str) -> str:
    """Reverse a string."""
    reversed_text = text[::-1]
    return reversed_text


# ============================================================
# CLIENT PART
# ============================================================

async def run_client():
    """Connect to the server and test both tools."""
    from mcp.client.stdio import stdio_client
    from mcp.client.session import ClientSession
    from mcp import StdioServerParameters

    # Launch THIS file as the server (with --server flag)
    server_params = StdioServerParameters(
        command="python",
        args=[__file__, "--server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize
            await session.initialize()
            print("Connected via STDIO!\n")

            # List tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}")

            # Call greet tool
            print("\nCalling greet('MCP Student')...")
            result = await session.call_tool("greet", {"name": "MCP Student"})
            print(f"Result: {result.content[0].text}")

            # Call reverse tool
            print("\nCalling reverse('Hello MCP')...")
            result = await session.call_tool("reverse", {"text": "Hello MCP"})
            print(f"Result: {result.content[0].text}")

            print("\nAll tests passed!")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # If --server flag is passed, run as server
    if "--server" in sys.argv:
        server.run()
    else:
        # Otherwise, run as client (which will launch the server)
        asyncio.run(run_client())
