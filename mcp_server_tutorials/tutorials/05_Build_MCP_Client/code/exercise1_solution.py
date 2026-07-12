"""
Exercise 1 Solution: Build a Multi-Tool Client
=================================================
This client connects to the AllFeaturesServer and calls
multiple tools one after another, printing each result.
"""

import asyncio
import os
import sys

from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

# ============================================================
# Path to the server
# ============================================================
SERVER_SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "04_Build_First_MCP_Server",
    "code",
    "example4_server_all_features.py"
)
SERVER_SCRIPT_PATH = os.path.abspath(SERVER_SCRIPT_PATH)


async def main():
    """Connect to the server and call multiple tools."""

    print("=" * 60)
    print("Exercise 1 SOLUTION: Multi-Tool Client")
    print("=" * 60)

    # Check the server exists
    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"\nERROR: Server not found at: {SERVER_SCRIPT_PATH}")
        return

    # Configure the connection
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    # Connect to the server
    print("\nConnecting to server...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            # Initialize the session (always required)
            await session.initialize()
            print("Connected and initialized!\n")

            # ================================================
            # Step 1: First, list all available tools
            # ================================================
            # This is good practice: check what is available
            # before calling tools.
            tools_result = await session.list_tools()
            print(f"Available tools: {len(tools_result.tools)}")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # ================================================
            # Step 2: Call the "add" tool
            # ================================================
            print("-" * 40)
            print("Calling: add(a=10, b=20)")
            result1 = await session.call_tool("add", {"a": 10, "b": 20})
            print(f"Result:  {result1.content[0].text}")

            # ================================================
            # Step 3: Call the "multiply" tool
            # ================================================
            print("\nCalling: multiply(a=6, b=7)")
            result2 = await session.call_tool("multiply", {"a": 6, "b": 7})
            print(f"Result:  {result2.content[0].text}")

            # ================================================
            # Step 4: Call the "get_length" tool
            # ================================================
            print('\nCalling: get_length(text="Model Context Protocol")')
            result3 = await session.call_tool(
                "get_length",
                {"text": "Model Context Protocol"}
            )
            print(f"Result:  {result3.content[0].text}")

            # ================================================
            # Bonus: Call tools with different arguments
            # ================================================
            print("\n" + "-" * 40)
            print("Bonus: More tool calls\n")

            # add with negative numbers
            result4 = await session.call_tool("add", {"a": -5, "b": 15})
            print(f"add(-5, 15) = {result4.content[0].text}")

            # multiply with zero
            result5 = await session.call_tool("multiply", {"a": 100, "b": 0})
            print(f"multiply(100, 0) = {result5.content[0].text}")

            # get_length with empty string
            result6 = await session.call_tool("get_length", {"text": ""})
            print(f'get_length("") = {result6.content[0].text}')

    # Summary
    print("\n" + "=" * 60)
    print("All tool calls completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
