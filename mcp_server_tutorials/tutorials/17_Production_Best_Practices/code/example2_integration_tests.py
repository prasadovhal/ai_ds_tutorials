"""
Example 2 - Integration Testing an MCP Server
===============================================
This example shows how to integration test a full MCP server.
We create a server, connect to it via stdio, and call tools
through the real MCP protocol to verify everything works end-to-end.

Requirements: pip install mcp
"""

import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# ============================================================
# Step 1: Create a simple MCP server to test
# ============================================================

# Create the server
mcp = FastMCP("TestServer")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


# ============================================================
# Step 2: Write async integration test
# ============================================================

async def run_integration_tests():
    """
    Connect to the server via stdio and test tools
    through the real MCP protocol.
    """
    print("Starting integration tests...")

    # Set up server parameters to run THIS file as a server
    server_params = StdioServerParameters(
        command="python",
        args=[__file__, "--server"],  # Run this file in server mode
    )

    # Connect to the server using stdio transport
    async with stdio_client(server_params) as (read_stream, write_stream):
        # Create a client session
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            print("  Connected to server successfully")

            # ---- Test 1: List available tools ----
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            assert "add" in tool_names, "add tool should be available"
            assert "greet" in tool_names, "greet tool should be available"
            print("  PASS: Tools are listed correctly")

            # ---- Test 2: Call the add tool ----
            result = await session.call_tool("add", {"a": 5, "b": 3})
            # The result content is a list of content blocks
            result_text = result.content[0].text
            assert "8" in result_text, f"Expected 8, got {result_text}"
            print("  PASS: add(5, 3) returned 8")

            # ---- Test 3: Call the greet tool ----
            result = await session.call_tool("greet", {"name": "Alice"})
            result_text = result.content[0].text
            assert "Hello, Alice!" in result_text, f"Unexpected: {result_text}"
            print("  PASS: greet('Alice') returned correct greeting")

            # ---- Test 4: Call add with negative numbers ----
            result = await session.call_tool("add", {"a": -10, "b": 3})
            result_text = result.content[0].text
            assert "-7" in result_text, f"Expected -7, got {result_text}"
            print("  PASS: add(-10, 3) returned -7")

    print("\nAll integration tests PASSED!")


# ============================================================
# Step 3: Entry point - run as server or as test
# ============================================================

if __name__ == "__main__":
    import sys

    if "--server" in sys.argv:
        # Run as MCP server (called by the test client)
        mcp.run()
    else:
        # Run the integration tests
        print("=" * 50)
        print("Integration Tests for MCP Server")
        print("=" * 50)
        asyncio.run(run_integration_tests())
        print("=" * 50)
