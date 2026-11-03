"""
Example 1: Simple MCP Client
==============================
This is the simplest MCP client you can build.
It connects to a server, lists the available tools, and disconnects.

What you will learn:
  - How to import the MCP client classes
  - How to configure the connection to a server
  - How to create a session and initialize it
  - How to list tools from the server

How to run:
  python example1_simple_client.py

IMPORTANT:
  This client connects to the Chapter 4 minimal server.
  Make sure you have the server file at the path shown below.
  Adjust SERVER_SCRIPT_PATH if your file structure is different.
"""

import asyncio
import os
import sys

# ============================================================
# Step 1: Import the MCP client classes
# ============================================================
# stdio_client: creates a connection to a server via stdin/stdout
# StdioServerParameters: configuration for the stdio connection
# ClientSession: manages the protocol-level session with the server
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.session import ClientSession

# ============================================================
# Step 2: Define the path to the server script
# ============================================================
# The client will LAUNCH the server as a child process.
# We need to tell it where the server script is.
# This path is relative to where you run this client from.
#
# We use the AllFeaturesServer from Chapter 4 because it has
# tools, resources, and prompts -- giving us a lot to explore.
SERVER_SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "04_Build_First_MCP_Server",
    "code",
    "example4_server_all_features.py"
)

# Resolve to an absolute path so it works from any directory
SERVER_SCRIPT_PATH = os.path.abspath(SERVER_SCRIPT_PATH)


# ============================================================
# Step 3: Define the main async function
# ============================================================
# MCP clients MUST use async/await because the communication
# with the server involves waiting for responses (I/O).
# If you are new to async, just follow the pattern:
#   async def, await, asyncio.run()
async def main():
    """Connect to the server, list tools, and disconnect."""

    print("=" * 60)
    print("Example 1: Simple MCP Client")
    print("=" * 60)

    # Check that the server script exists before trying to connect
    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"\nERROR: Server script not found at:")
        print(f"  {SERVER_SCRIPT_PATH}")
        print(f"\nMake sure you have completed Chapter 4 first.")
        print(f"The client needs a server to connect to!")
        return

    print(f"\nConnecting to server: {SERVER_SCRIPT_PATH}")

    # Step 4: Configure the connection parameters
    # StdioServerParameters tells the client HOW to launch the server.
    # "command" is the program to run (python).
    # "args" is the list of arguments (the server script path).
    server_params = StdioServerParameters(
        command=sys.executable,  # Use the same Python that is running this script
        args=[SERVER_SCRIPT_PATH]
    )

    # Step 5: Connect to the server using stdio_client
    # "async with" ensures the connection is properly closed when we are done.
    # stdio_client returns two streams: read_stream and write_stream.
    # These are how we communicate with the server process.
    print("Launching server process...")
    async with stdio_client(server_params) as (read_stream, write_stream):

        # Step 6: Create a ClientSession on top of the streams
        # The ClientSession handles the JSON-RPC protocol for us.
        # It sends properly formatted requests and parses responses.
        print("Creating client session...")
        async with ClientSession(read_stream, write_stream) as session:

            # Step 7: Initialize the session
            # This exchanges capabilities with the server.
            # You MUST call initialize() before doing anything else.
            # Without this, all other calls will fail.
            print("Initializing session...")
            init_result = await session.initialize()

            # Print server information from the initialization response
            print(f"\nConnected successfully!")
            print(f"  Server name: {init_result.server_info.name}")

            # Step 8: List all available tools
            # list_tools() sends a tools/list request to the server
            # and returns a ListToolsResult object.
            print("\nListing available tools...")
            tools_result = await session.list_tools()

            # Step 9: Print each tool's name and description
            tool_list = tools_result.tools
            print(f"\nFound {len(tool_list)} tools:")
            print("-" * 50)

            for tool in tool_list:
                print(f"\n  Tool: {tool.name}")
                print(f"  Description: {tool.description}")

                # Print the required arguments from the input schema
                input_schema = tool.inputSchema
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])

                print(f"  Arguments:")
                for arg_name, arg_schema in properties.items():
                    is_required = arg_name in required
                    arg_type = arg_schema.get("type", "unknown")
                    req_label = "(required)" if is_required else "(optional)"
                    print(f"    - {arg_name}: {arg_type} {req_label}")

            print("\n" + "-" * 50)
            print("Done! Session will close automatically.")

    # When we exit the "async with" blocks, the session is closed
    # and the server process is terminated. Everything is cleaned up.
    print("\nClient disconnected.")


# ============================================================
# Step 10: Run the async main function
# ============================================================
# asyncio.run() starts the event loop and runs our main function.
# This is the entry point for all async MCP clients.
if __name__ == "__main__":
    asyncio.run(main())
