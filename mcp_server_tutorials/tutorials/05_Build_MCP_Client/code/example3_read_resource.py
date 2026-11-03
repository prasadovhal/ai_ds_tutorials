"""
Example 3: Read a Resource from the Client
============================================
This client connects to a server, lists all available resources,
and reads each one using session.read_resource().

What you will learn:
  - How to list resources from the server
  - How to read a resource using session.read_resource()
  - How to access the resource content

How to run:
  python example3_read_resource.py

IMPORTANT:
  This client connects to the Chapter 4 AllFeaturesServer.
  That server exposes two resources:
    - info://server  (server information)
    - info://help    (help text)
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
# Step 3: Define the main async function
# ============================================================
async def main():
    """Connect to the server, list resources, and read each one."""

    print("=" * 60)
    print("Example 3: Read a Resource from the Client")
    print("=" * 60)

    # Check that the server script exists
    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"\nERROR: Server script not found at:")
        print(f"  {SERVER_SCRIPT_PATH}")
        print(f"\nMake sure you have completed Chapter 4 first.")
        return

    print(f"\nServer: {SERVER_SCRIPT_PATH}")

    # Step 4: Configure and connect
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    print("Connecting to server...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            # Step 5: Initialize the session (always required first)
            await session.initialize()
            print("Connected and initialized!\n")

            # ================================================
            # Step 6: List all available resources
            # ================================================
            # session.list_resources() sends a resources/list request.
            # It returns a ListResourcesResult object.
            print("Listing available resources...")
            print("-" * 50)

            resources_result = await session.list_resources()
            resource_list = resources_result.resources

            print(f"Found {len(resource_list)} resources:\n")

            # Print each resource's URI and description
            for resource in resource_list:
                print(f"  URI:  {resource.uri}")
                print(f"  Name: {resource.name}")
                if resource.description:
                    print(f"  Desc: {resource.description}")
                print()

            # ================================================
            # Step 7: Read each resource
            # ================================================
            # session.read_resource() sends a resources/read request.
            # It takes a URI (string) and returns the resource content.
            print("=" * 50)
            print("Reading each resource:")
            print("=" * 50)

            for resource in resource_list:
                print(f"\n--- Reading: {resource.uri} ---\n")

                # read_resource takes the URI as a string
                read_result = await session.read_resource(resource.uri)

                # The result has a "contents" list
                # Each item has a "uri", "text" (or "blob"), and optional "mimeType"
                for content in read_result.contents:
                    print(f"  URI: {content.uri}")

                    # Check if the content has text (most common)
                    if hasattr(content, "text") and content.text is not None:
                        print(f"  Content:\n")
                        # Print each line with indentation for readability
                        for line in content.text.split("\n"):
                            print(f"    {line}")
                    else:
                        print(f"  (Binary content, not displayed)")

                    print()

    # Connection is automatically closed
    print("=" * 60)
    print("Done! Client disconnected.")
    print("=" * 60)


# ============================================================
# Step 8: Run the async main function
# ============================================================
if __name__ == "__main__":
    asyncio.run(main())
