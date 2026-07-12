"""
Example 2: Hello World MCP Client
==================================
The simplest possible MCP client that connects to a server and calls a tool.

This client will:
1. Start the hello world server as a subprocess
2. Connect to it via STDIO
3. Call the 'hello' tool
4. Print the result

Setup:
  poetry add mcp
  poetry run python example2_hello_world_client.py
"""

import asyncio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters


async def main():
    """Connect to server and call the hello tool."""

    # Step 1: Define how to start the server
    # The client will launch the server as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["example1_hello_world_server.py"],
    )

    # Step 2: Connect to the server via STDIO
    async with stdio_client(server_params) as (read_stream, write_stream):

        # Step 3: Create a session (this handles the MCP protocol)
        async with ClientSession(read_stream, write_stream) as session:

            # Step 4: Initialize the connection
            # This exchanges capabilities between client and server
            await session.initialize()
            print("Connected to server!")

            # Step 5: List available tools
            tools_result = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools_result.tools]}")

            # Step 6: Call the hello tool
            result = await session.call_tool("hello", {"name": "World"})
            print(f"Result: {result.content[0].text}")


# Step 7: Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
