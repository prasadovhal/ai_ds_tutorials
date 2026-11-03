"""
Example 2: Call a Tool from the Client
========================================
This client connects to a server, calls the "add" tool with a=5 and b=3,
and prints the result.

What you will learn:
  - How to call a tool on the server using session.call_tool()
  - How to pass arguments to the tool
  - How to read the result from the response

How to run:
  python example2_call_tool.py

IMPORTANT:
  This client connects to the Chapter 4 AllFeaturesServer.
  Make sure you have that server file before running this.
"""

import asyncio
import os
import sys

# ============================================================
# Step 1: Import the MCP client classes
# ============================================================
# These are the same three imports you will use in EVERY MCP client.
# stdio_client: creates a connection to a server via stdin/stdout
# StdioServerParameters: configuration for the stdio connection
# ClientSession: manages the protocol-level session with the server
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

# ============================================================
# Step 2: Define the path to the server script
# ============================================================
# The client will launch the server as a subprocess.
# We point to the AllFeaturesServer from Chapter 4.
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
# MCP clients MUST be async because communication with the
# server involves waiting for responses over stdin/stdout.
async def main():
    """Connect to the server, call the add tool, and print the result."""

    print("=" * 60)
    print("Example 2: Call a Tool from the Client")
    print("=" * 60)

    # Check that the server script exists
    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"\nERROR: Server script not found at:")
        print(f"  {SERVER_SCRIPT_PATH}")
        print(f"\nMake sure you have completed Chapter 4 first.")
        return

    print(f"\nServer: {SERVER_SCRIPT_PATH}")

    # Step 4: Configure how to launch the server process
    # "command" is the Python interpreter to use.
    # "args" is the server script to run.
    server_params = StdioServerParameters(
        command=sys.executable,  # Use the same Python running this script
        args=[SERVER_SCRIPT_PATH]
    )

    # Step 5: Connect to the server
    # stdio_client launches the server subprocess and gives us
    # two streams: one for reading, one for writing.
    print("Connecting to server...")
    async with stdio_client(server_params) as (read_stream, write_stream):

        # Step 6: Create a session on top of the streams
        # The session handles the JSON-RPC protocol for us.
        async with ClientSession(read_stream, write_stream) as session:

            # Step 7: Initialize the session
            # This MUST be called before any other operation.
            # It exchanges capabilities between client and server.
            await session.initialize()
            print("Connected and initialized!\n")

            # ================================================
            # Step 8: Call the "add" tool
            # ================================================
            # session.call_tool() sends a tools/call request.
            # First argument: the name of the tool (string).
            # Second argument: a dictionary of the tool's arguments.
            #
            # The AllFeaturesServer has an "add" tool that takes
            # two integers "a" and "b" and returns their sum.
            print("Calling tool: add(a=5, b=3)")
            print("-" * 40)

            result = await session.call_tool("add", {"a": 5, "b": 3})

            # Step 9: Read the result
            # The result object has a "content" list.
            # Each item in the list has a "type" and "text" field.
            # For simple tools, there is usually one item.
            print(f"Raw result object: {result}")
            print(f"Number of content items: {len(result.content)}")

            # Get the text from the first content item
            first_content = result.content[0]
            print(f"Content type: {first_content.type}")
            print(f"Content text: {first_content.text}")

            # Step 10: Check if the tool reported an error
            # result.isError is True if the tool itself had an error.
            # This is different from a connection error.
            if result.isError:
                print("\nThe tool reported an error!")
            else:
                print("\nTool executed successfully!")

            # ================================================
            # Step 11: Call another tool to show the pattern
            # ================================================
            # Let's also call the "multiply" tool to reinforce the pattern.
            print("\n" + "-" * 40)
            print("Calling tool: multiply(a=4, b=7)")
            print("-" * 40)

            result2 = await session.call_tool("multiply", {"a": 4, "b": 7})
            print(f"Result: {result2.content[0].text}")

            # ================================================
            # Step 12: Call the get_length tool (string argument)
            # ================================================
            print("\n" + "-" * 40)
            print('Calling tool: get_length(text="Hello MCP")')
            print("-" * 40)

            result3 = await session.call_tool("get_length", {"text": "Hello MCP"})
            print(f"Result: {result3.content[0].text}")

    # Connection is automatically closed when we exit the "async with" blocks
    print("\n" + "=" * 60)
    print("Done! Client disconnected.")
    print("=" * 60)


# ============================================================
# Step 13: Run the async main function
# ============================================================
# asyncio.run() starts the event loop and runs our main function.
if __name__ == "__main__":
    asyncio.run(main())
