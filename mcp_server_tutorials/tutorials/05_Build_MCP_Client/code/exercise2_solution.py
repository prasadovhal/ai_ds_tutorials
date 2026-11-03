"""
Exercise 2 Solution: Build a Resource Reader Client
======================================================
This client connects to the AllFeaturesServer, lists all
resources, reads each one, and prints the contents.
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
    """Connect to the server, list resources, and read each one."""

    print("=" * 60)
    print("Exercise 2 SOLUTION: Resource Reader Client")
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

            # Initialize the session
            await session.initialize()
            print("Connected and initialized!\n")

            # ================================================
            # Step 1: List all available resources
            # ================================================
            resources_result = await session.list_resources()
            resource_list = resources_result.resources

            print(f"Found {len(resource_list)} resources:")
            print("-" * 50)

            # Print a summary of each resource
            for resource in resource_list:
                print(f"  URI:  {resource.uri}")
                print(f"  Name: {resource.name}")
                if resource.description:
                    print(f"  Desc: {resource.description}")
                print()

            # ================================================
            # Step 2: Read each resource
            # ================================================
            print("=" * 50)
            print("Reading all resources:")
            print("=" * 50)

            # Keep count of successfully read resources
            read_count = 0

            for resource in resource_list:
                print(f"\n{'=' * 40}")
                print(f"Resource: {resource.uri}")
                print(f"{'=' * 40}\n")

                # Read the resource content
                try:
                    read_result = await session.read_resource(resource.uri)

                    # Each result has a "contents" list
                    for content in read_result.contents:
                        # Print the text content
                        if hasattr(content, "text") and content.text is not None:
                            # Print each line with indentation
                            for line in content.text.split("\n"):
                                print(f"  {line}")
                        else:
                            print("  (Binary content, cannot display)")

                    read_count = read_count + 1

                except Exception as error:
                    print(f"  ERROR reading resource: {error}")

            # ================================================
            # Step 3: Print summary
            # ================================================
            print("\n" + "=" * 50)
            print("SUMMARY")
            print("=" * 50)
            print(f"  Total resources found: {len(resource_list)}")
            print(f"  Successfully read:     {read_count}")
            print(f"  Failed:                {len(resource_list) - read_count}")

    print("\n" + "=" * 60)
    print("Done! Client disconnected.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
