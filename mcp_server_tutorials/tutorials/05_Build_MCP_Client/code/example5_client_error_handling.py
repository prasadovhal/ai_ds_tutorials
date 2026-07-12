"""
Example 5: Client Error Handling
==================================
This client demonstrates how to handle errors that can occur
when communicating with an MCP server.

What you will learn:
  - How to handle connection errors (server not found)
  - How to handle tool-not-found errors
  - How to handle invalid parameter errors
  - How to use try/except around all MCP operations
  - The difference between connection errors and tool errors

How to run:
  python example5_client_error_handling.py

IMPORTANT:
  This client connects to the Chapter 4 AllFeaturesServer.
"""

import asyncio
import os
import sys

# ============================================================
# Step 1: Import the MCP client classes
# ============================================================
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

# ============================================================
# Step 2: Define the path to the server script
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


# ============================================================
# Step 3: Demonstrate connection error handling
# ============================================================
async def demo_connection_error():
    """Show what happens when the server script does not exist."""

    print("\n" + "=" * 60)
    print("Demo 1: Connection Error (bad server path)")
    print("=" * 60)

    # Point to a server script that does NOT exist
    bad_path = "/this/path/does/not/exist/server.py"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[bad_path]
    )

    try:
        # Try to connect to the non-existent server
        print(f"Trying to connect to: {bad_path}")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("This line should NOT be reached!")

    except Exception as error:
        # The connection will fail because the server script does not exist
        print(f"\nCaught error: {type(error).__name__}")
        print(f"Message: {error}")
        print("\nThis is expected! The server script does not exist.")


# ============================================================
# Step 4: Demonstrate tool-not-found error
# ============================================================
async def demo_tool_not_found():
    """Show what happens when you call a tool that does not exist."""

    print("\n" + "=" * 60)
    print("Demo 2: Tool Not Found Error")
    print("=" * 60)

    # Check that the server exists for this demo
    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"Skipping: Server not found at {SERVER_SCRIPT_PATH}")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected successfully.\n")

            try:
                # Try to call a tool that does NOT exist on the server
                print("Calling non-existent tool: 'divide'...")
                result = await session.call_tool("divide", {"a": 10, "b": 2})

                # If the server returns a result with isError=True
                if result.isError:
                    print(f"Tool error: {result.content[0].text}")
                else:
                    print(f"Result: {result.content[0].text}")

            except Exception as error:
                # Some servers raise an exception for unknown tools
                print(f"\nCaught error: {type(error).__name__}")
                print(f"Message: {error}")
                print("\nThis is expected! The 'divide' tool does not exist.")


# ============================================================
# Step 5: Demonstrate invalid parameter error
# ============================================================
async def demo_invalid_params():
    """Show what happens when you pass wrong arguments to a tool."""

    print("\n" + "=" * 60)
    print("Demo 3: Invalid Parameters Error")
    print("=" * 60)

    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"Skipping: Server not found at {SERVER_SCRIPT_PATH}")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected successfully.\n")

            # --- Case A: Missing required parameter ---
            try:
                print("Case A: Missing required parameter")
                print("  Calling add(a=5) -- missing 'b'...")
                result = await session.call_tool("add", {"a": 5})

                # Check if the tool reported an error
                if result.isError:
                    print(f"  Tool error: {result.content[0].text}")
                else:
                    print(f"  Result: {result.content[0].text}")

            except Exception as error:
                print(f"  Caught error: {type(error).__name__}")
                print(f"  Message: {error}")

            # --- Case B: Wrong parameter type ---
            try:
                print("\nCase B: Wrong parameter type")
                print('  Calling add(a="hello", b=3) -- "a" should be int...')
                result = await session.call_tool("add", {"a": "hello", "b": 3})

                if result.isError:
                    print(f"  Tool error: {result.content[0].text}")
                else:
                    print(f"  Result: {result.content[0].text}")

            except Exception as error:
                print(f"  Caught error: {type(error).__name__}")
                print(f"  Message: {error}")

            # --- Case C: Extra unexpected parameter ---
            try:
                print("\nCase C: Extra unexpected parameter")
                print("  Calling add(a=5, b=3, c=99) -- 'c' is extra...")
                result = await session.call_tool("add", {"a": 5, "b": 3, "c": 99})

                if result.isError:
                    print(f"  Tool error: {result.content[0].text}")
                else:
                    print(f"  Result: {result.content[0].text}")
                    print("  (Server may ignore extra parameters)")

            except Exception as error:
                print(f"  Caught error: {type(error).__name__}")
                print(f"  Message: {error}")


# ============================================================
# Step 6: Demonstrate a safe client pattern
# ============================================================
async def demo_safe_client():
    """Show the recommended pattern: wrap everything in try/except."""

    print("\n" + "=" * 60)
    print("Demo 4: Safe Client Pattern (recommended)")
    print("=" * 60)

    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"Skipping: Server not found at {SERVER_SCRIPT_PATH}")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    try:
        # Wrap the ENTIRE client in a try/except
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:

                # Initialize with error handling
                try:
                    await session.initialize()
                    print("Connected successfully.\n")
                except Exception as error:
                    print(f"Failed to initialize: {error}")
                    return

                # List tools with error handling
                try:
                    tools_result = await session.list_tools()
                    print(f"Found {len(tools_result.tools)} tools")
                except Exception as error:
                    print(f"Failed to list tools: {error}")
                    return

                # Call a tool with error handling
                try:
                    result = await session.call_tool("add", {"a": 10, "b": 20})
                    if result.isError:
                        print(f"Tool error: {result.content[0].text}")
                    else:
                        print(f"add(10, 20) = {result.content[0].text}")
                except Exception as error:
                    print(f"Failed to call tool: {error}")

                # Read a resource with error handling
                try:
                    resource = await session.read_resource("info://server")
                    print(f"\nServer info: {resource.contents[0].text[:50]}...")
                except Exception as error:
                    print(f"Failed to read resource: {error}")

                print("\nAll operations completed safely!")

    except Exception as error:
        # This catches connection-level errors
        print(f"\nConnection error: {type(error).__name__}: {error}")


# ============================================================
# Step 7: Main function that runs all demos
# ============================================================
async def main():
    """Run all error handling demos."""

    print("=" * 60)
    print("Example 5: Client Error Handling")
    print("=" * 60)
    print("\nThis example shows how to handle various errors")
    print("that can occur when communicating with an MCP server.")

    # Demo 1: Connection error
    await demo_connection_error()

    # Demo 2: Tool not found
    await demo_tool_not_found()

    # Demo 3: Invalid parameters
    await demo_invalid_params()

    # Demo 4: Safe client pattern
    await demo_safe_client()

    # Summary
    print("\n" + "=" * 60)
    print("ERROR HANDLING SUMMARY")
    print("=" * 60)
    print("""
Key takeaways:
  1. Always wrap connections in try/except
  2. Check result.isError after calling tools
  3. Handle specific errors: connection, tool-not-found, invalid params
  4. Use the safe pattern: try/except around each operation
  5. Always check server exists before connecting

Common error types:
  - FileNotFoundError: server script not found
  - ConnectionError: server crashed or refused connection
  - Exception: tool not found, invalid params, etc.
""")


# ============================================================
# Step 8: Run the async main function
# ============================================================
if __name__ == "__main__":
    asyncio.run(main())
