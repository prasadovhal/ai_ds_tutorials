"""
Exercise 1: Build a Multi-Tool Client
=======================================

YOUR TASK:
Build a client that connects to the AllFeaturesServer and calls
MULTIPLE tools one after another, printing the result of each.

Requirements:
  1. Connect to the AllFeaturesServer (Chapter 4)
  2. Initialize the session
  3. Call the "add" tool with a=10, b=20
  4. Call the "multiply" tool with a=6, b=7
  5. Call the "get_length" tool with text="Model Context Protocol"
  6. Print all three results clearly

HINTS:
  - Use session.call_tool(name, arguments) for each call
  - Each result has result.content[0].text
  - You can call tools one after another (they are independent)
  - Use await for each call

Run the solution file to see the expected output:
  python exercise1_solution.py
"""

import asyncio
import os
import sys

from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

# Path to the server
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
    print("Exercise 1: Multi-Tool Client")
    print("=" * 60)

    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"\nERROR: Server not found at: {SERVER_SCRIPT_PATH}")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected!\n")

            # TODO: Call the "add" tool with a=10, b=20
            # result1 = await session.call_tool(...)
            # print(f"add(10, 20) = {result1.content[0].text}")

            # TODO: Call the "multiply" tool with a=6, b=7
            # result2 = await session.call_tool(...)
            # print(f"multiply(6, 7) = {result2.content[0].text}")

            # TODO: Call the "get_length" tool with text="Model Context Protocol"
            # result3 = await session.call_tool(...)
            # print(f'get_length("Model Context Protocol") = {result3.content[0].text}')

            print("\nReplace the TODO comments with your code!")
            print("Run exercise1_solution.py to see the expected output.")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
