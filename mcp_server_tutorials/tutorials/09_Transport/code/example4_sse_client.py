"""
Example 4: SSE Client
======================
MCP client connecting to a server via SSE (Server-Sent Events) transport.

The SSE client connects to an HTTP endpoint instead of launching a subprocess.
This is useful for remote servers.

Setup:
  1. Start the SSE server first: python example3_sse_server.py
  2. Then run this client: python example4_sse_client.py
"""

import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


async def main():
    """Connect to an SSE server and call tools."""

    # Step 1: Define the SSE server URL
    # The server must be running at this URL already
    server_url = "http://localhost:8000/sse"

    print(f"Connecting to SSE server at {server_url}...")

    try:
        # Step 2: Connect using sse_client
        # Unlike stdio_client, this connects to a running server over HTTP
        async with sse_client(server_url) as (read_stream, write_stream):

            # Step 3: Create a session
            async with ClientSession(read_stream, write_stream) as session:

                # Step 4: Initialize the connection
                await session.initialize()
                print("Connected to SSE server!\n")

                # Step 5: List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Step 6: Call a tool
                print("\nCalling 'hello' tool...")
                result = await session.call_tool("hello", {"name": "SSE Client"})
                print(f"Result: {result.content[0].text}")

    except ConnectionRefusedError:
        print("ERROR: Could not connect to the SSE server.")
        print("Make sure the server is running: python example3_sse_server.py")
    except Exception as e:
        print(f"ERROR: {e}")
        print("Make sure the SSE server is running first.")


if __name__ == "__main__":
    asyncio.run(main())
