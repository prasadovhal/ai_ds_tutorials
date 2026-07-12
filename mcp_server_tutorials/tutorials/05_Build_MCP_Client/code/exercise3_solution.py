"""
Exercise 3 Solution: Interactive CLI Client
=============================================
This is a menu-driven MCP client that lets you interactively
explore a server: list tools, call tools, list resources,
and read resources.
"""

import asyncio
import json
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


# ============================================================
# Helper: Print the menu
# ============================================================
def print_menu():
    """Print the interactive menu."""
    print("\n" + "=" * 40)
    print("  MCP Interactive Client")
    print("=" * 40)
    print("  1. List tools")
    print("  2. Call a tool")
    print("  3. List resources")
    print("  4. Read a resource")
    print("  5. List prompts")
    print("  6. Get a prompt")
    print("  7. Quit")
    print("-" * 40)


# ============================================================
# Action: List tools
# ============================================================
async def action_list_tools(session):
    """List all tools on the server."""
    print("\n--- Available Tools ---")
    tools_result = await session.list_tools()

    if len(tools_result.tools) == 0:
        print("  No tools found.")
        return

    for tool in tools_result.tools:
        print(f"\n  Name: {tool.name}")
        print(f"  Desc: {tool.description}")

        # Show the arguments this tool expects
        properties = tool.inputSchema.get("properties", {})
        required = tool.inputSchema.get("required", [])
        if properties:
            print(f"  Args:")
            for arg_name, arg_info in properties.items():
                arg_type = arg_info.get("type", "unknown")
                is_req = "(required)" if arg_name in required else "(optional)"
                print(f"    - {arg_name}: {arg_type} {is_req}")


# ============================================================
# Action: Call a tool
# ============================================================
async def action_call_tool(session):
    """Ask the user for a tool name and arguments, then call it."""
    print("\n--- Call a Tool ---")

    # First, show available tools so the user knows what to pick
    tools_result = await session.list_tools()
    tool_names = [tool.name for tool in tools_result.tools]
    print(f"  Available: {', '.join(tool_names)}")

    # Get the tool name from the user
    tool_name = input("  Tool name: ").strip()

    if tool_name not in tool_names:
        print(f"  Tool '{tool_name}' not found!")
        return

    # Get the arguments from the user
    # We ask for JSON input so the user can pass any arguments
    print('  Enter arguments as JSON (e.g. {"a": 5, "b": 3}):')
    args_input = input("  Arguments: ").strip()

    # Parse the JSON arguments
    try:
        arguments = json.loads(args_input)
    except json.JSONDecodeError:
        print("  Invalid JSON! Please use format: {\"key\": value}")
        return

    # Call the tool
    try:
        result = await session.call_tool(tool_name, arguments)

        if result.isError:
            print(f"\n  Tool error: {result.content[0].text}")
        else:
            print(f"\n  Result: {result.content[0].text}")

    except Exception as error:
        print(f"\n  Error calling tool: {error}")


# ============================================================
# Action: List resources
# ============================================================
async def action_list_resources(session):
    """List all resources on the server."""
    print("\n--- Available Resources ---")
    resources_result = await session.list_resources()

    if len(resources_result.resources) == 0:
        print("  No resources found.")
        return

    for resource in resources_result.resources:
        print(f"\n  URI:  {resource.uri}")
        print(f"  Name: {resource.name}")
        if resource.description:
            print(f"  Desc: {resource.description}")


# ============================================================
# Action: Read a resource
# ============================================================
async def action_read_resource(session):
    """Ask the user for a resource URI and read it."""
    print("\n--- Read a Resource ---")

    # Show available resources first
    resources_result = await session.list_resources()
    for resource in resources_result.resources:
        print(f"  - {resource.uri}")

    # Get the URI from the user
    uri = input("\n  Resource URI: ").strip()

    # Read the resource
    try:
        read_result = await session.read_resource(uri)

        print(f"\n  Content:")
        for content in read_result.contents:
            if hasattr(content, "text") and content.text is not None:
                for line in content.text.split("\n"):
                    print(f"    {line}")
            else:
                print("    (Binary content)")

    except Exception as error:
        print(f"\n  Error reading resource: {error}")


# ============================================================
# Action: List prompts
# ============================================================
async def action_list_prompts(session):
    """List all prompts on the server."""
    print("\n--- Available Prompts ---")
    prompts_result = await session.list_prompts()

    if len(prompts_result.prompts) == 0:
        print("  No prompts found.")
        return

    for prompt in prompts_result.prompts:
        print(f"\n  Name: {prompt.name}")
        if prompt.description:
            print(f"  Desc: {prompt.description}")
        if prompt.arguments:
            print(f"  Args:")
            for arg in prompt.arguments:
                req = "(required)" if arg.required else "(optional)"
                print(f"    - {arg.name} {req}")


# ============================================================
# Action: Get a prompt
# ============================================================
async def action_get_prompt(session):
    """Ask the user for a prompt name and arguments, then get it."""
    print("\n--- Get a Prompt ---")

    # Show available prompts
    prompts_result = await session.list_prompts()
    prompt_names = [p.name for p in prompts_result.prompts]
    print(f"  Available: {', '.join(prompt_names)}")

    # Get the prompt name
    prompt_name = input("  Prompt name: ").strip()

    if prompt_name not in prompt_names:
        print(f"  Prompt '{prompt_name}' not found!")
        return

    # Get the arguments as JSON
    print('  Enter arguments as JSON (e.g. {"text": "hello"}):')
    args_input = input("  Arguments: ").strip()

    try:
        arguments = json.loads(args_input)
    except json.JSONDecodeError:
        print("  Invalid JSON!")
        return

    # Get the prompt
    try:
        prompt_result = await session.get_prompt(prompt_name, arguments)

        print(f"\n  Rendered prompt:")
        for message in prompt_result.messages:
            print(f"\n  Role: {message.role}")
            content = message.content
            if hasattr(content, "text"):
                for line in content.text.split("\n"):
                    print(f"    {line}")
            else:
                print(f"    {content}")

    except Exception as error:
        print(f"\n  Error getting prompt: {error}")


# ============================================================
# Main function
# ============================================================
async def main():
    """Run the interactive MCP client."""

    print("=" * 60)
    print("Exercise 3 SOLUTION: Interactive CLI Client")
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
            print("Connected and initialized!")

            # ================================================
            # Main menu loop
            # ================================================
            while True:
                print_menu()
                choice = input("  Your choice (1-7): ").strip()

                if choice == "1":
                    await action_list_tools(session)

                elif choice == "2":
                    await action_call_tool(session)

                elif choice == "3":
                    await action_list_resources(session)

                elif choice == "4":
                    await action_read_resource(session)

                elif choice == "5":
                    await action_list_prompts(session)

                elif choice == "6":
                    await action_get_prompt(session)

                elif choice == "7":
                    print("\nGoodbye!")
                    break

                else:
                    print("\n  Invalid choice. Please enter 1-7.")

    print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
