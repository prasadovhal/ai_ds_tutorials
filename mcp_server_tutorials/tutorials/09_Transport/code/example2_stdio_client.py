"""
Example 2: STDIO Transport Client
====================================

This example creates a client that connects to an MCP server
using STDIO transport.

How it works:
  1. The client specifies the server command (python script path)
  2. The MCP SDK starts the server as a subprocess
  3. Communication happens through the subprocess's stdin/stdout
  4. When the client disconnects, the server process ends

The key class is StdioServerParameters which tells the client
HOW to start the server process.

To run this example:
  1. Make sure example1_stdio_server.py exists
  2. Run: python example2_stdio_client.py

Key concepts:
- StdioServerParameters configures how to launch the server
- stdio_client() creates the connection
- ClientSession manages the conversation with the server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Connect to an MCP server via STDIO and call its tools."""

    # Step 1: Define how to start the server
    # StdioServerParameters tells the client what command to run.
    # "command" is the executable (python)
    # "args" is the list of arguments (the server script path)
    server_params = StdioServerParameters(
        command="python",
        args=["example1_stdio_server.py"],
    )

    # Step 2: Connect to the server using STDIO
    # stdio_client() starts the server process and connects to it.
    # It returns two streams: one for reading, one for writing.
    print("Connecting to STDIO server...")
    async with stdio_client(server_params) as (read_stream, write_stream):

        # Step 3: Create a client session
        # ClientSession wraps the streams into a high-level API.
        # It handles JSON-RPC message formatting automatically.
        async with ClientSession(read_stream, write_stream) as session:

            # Step 4: Initialize the session
            # This performs the MCP handshake:
            #   - Client sends its capabilities
            #   - Server responds with its capabilities
            #   - Both sides agree on protocol version
            await session.initialize()
            print("Connected successfully!\n")

            # Step 5: List available tools
            # Ask the server what tools it has
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # Step 6: Call the greet tool
            # We send a tool call request to the server
            # The server runs the function and sends back the result
            print("Calling 'greet' tool...")
            result = await session.call_tool("greet", {"name": "Alice"})
            print(f"Result: {result.content[0].text}")
            print()

            # Step 7: Call the add_numbers tool
            print("Calling 'add_numbers' tool...")
            result = await session.call_tool("add_numbers", {"a": 10, "b": 25})
            print(f"Result: {result.content[0].text}")
            print()

            # Step 8: Read the resource
            print("Reading resource...")
            result = await session.read_resource("info://server-transport")
            print(f"Resource: {result.contents[0].text}")
            print()

            print("Done! The STDIO connection will close automatically.")


# Run the async main function
# asyncio.run() starts the event loop and runs our async code
if __name__ == "__main__":
    asyncio.run(main())
