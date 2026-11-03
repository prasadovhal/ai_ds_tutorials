"""
Exercise 3: Build an Interactive CLI Client
=============================================

YOUR TASK:
Build an interactive menu-driven MCP client that lets the user
choose what to do from a menu:

  1. List tools
  2. Call a tool
  3. List resources
  4. Read a resource
  5. Quit

Requirements:
  1. Connect to the AllFeaturesServer
  2. Show a menu in a loop
  3. Let the user pick an option by typing a number
  4. Execute the chosen action
  5. Repeat until the user chooses "Quit"

HINTS:
  - Use a while True loop for the menu
  - Use input() to get user choices (input works inside async)
  - For "Call a tool": ask the user for the tool name and arguments
  - For "Read a resource": ask the user for the resource URI
  - Break out of the loop when user picks "Quit"

Run the solution file to see the expected behavior:
  python exercise3_solution.py
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
    """Interactive MCP client with a menu."""

    print("=" * 60)
    print("Exercise 3: Interactive CLI Client")
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

            # TODO: Build the interactive menu loop
            #
            # while True:
            #     print("\n--- Menu ---")
            #     print("1. List tools")
            #     print("2. Call a tool")
            #     print("3. List resources")
            #     print("4. Read a resource")
            #     print("5. Quit")
            #
            #     choice = input("\nYour choice: ").strip()
            #
            #     if choice == "1":
            #         # TODO: list tools
            #         pass
            #     elif choice == "2":
            #         # TODO: ask for tool name and arguments, call the tool
            #         pass
            #     elif choice == "3":
            #         # TODO: list resources
            #         pass
            #     elif choice == "4":
            #         # TODO: ask for resource URI, read the resource
            #         pass
            #     elif choice == "5":
            #         print("Goodbye!")
            #         break
            #     else:
            #         print("Invalid choice. Try again.")

            print("Replace the TODO comments with your code!")
            print("Run exercise3_solution.py to see the expected behavior.")

    print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
