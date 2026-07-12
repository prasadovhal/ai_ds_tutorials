"""
Exercise 2: Build a Resource Reader Client
=============================================

YOUR TASK:
Build a client that connects to the AllFeaturesServer,
lists ALL available resources, reads EACH one, and prints
the contents nicely.

Requirements:
  1. Connect to the AllFeaturesServer (Chapter 4)
  2. Initialize the session
  3. List all available resources using session.list_resources()
  4. Loop through each resource and read it using session.read_resource()
  5. Print the resource URI and its text content for each
  6. Print a summary at the end (how many resources were read)

HINTS:
  - session.list_resources() returns a result with a .resources list
  - Each resource has .uri, .name, and .description
  - session.read_resource(uri) returns a result with a .contents list
  - Each content item has .text (for text resources)
  - Use a for loop to iterate over all resources

Run the solution file to see the expected output:
  python exercise2_solution.py
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
    """Connect to the server, list resources, and read each one."""

    print("=" * 60)
    print("Exercise 2: Resource Reader Client")
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

            # TODO: List all resources
            # resources_result = await session.list_resources()
            # resource_list = resources_result.resources
            # print(f"Found {len(resource_list)} resources\n")

            # TODO: Loop through each resource and read it
            # for resource in resource_list:
            #     print(f"--- {resource.uri} ---")
            #     read_result = await session.read_resource(resource.uri)
            #     content = read_result.contents[0].text
            #     print(content)
            #     print()

            # TODO: Print a summary
            # print(f"\nSummary: Read {len(resource_list)} resources.")

            print("Replace the TODO comments with your code!")
            print("Run exercise2_solution.py to see the expected output.")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
