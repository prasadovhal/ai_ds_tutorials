"""
Mini Project: Universal MCP Client
=====================================
A universal MCP client that can connect to ANY MCP server.

How it works:
  1. You pass the server script path as a command-line argument
  2. The client connects to that server
  3. It discovers all tools, resources, and prompts
  4. It shows you an interactive menu to explore everything

Usage:
  python mini_project_universal_client.py path/to/any_server.py

Example:
  python mini_project_universal_client.py ../../04_Build_First_MCP_Server/code/example4_server_all_features.py

What you will learn:
  - How to build a reusable client that works with any server
  - How to discover all server capabilities dynamically
  - How to handle command-line arguments
  - How to build a complete interactive client
"""

import asyncio
import json
import os
import sys

from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession


# ============================================================
# Step 1: Parse command-line arguments
# ============================================================
def get_server_path():
    """Get the server script path from command-line arguments."""

    # Check if the user provided a server path
    if len(sys.argv) < 2:
        print("Usage: python mini_project_universal_client.py <server_script_path>")
        print()
        print("Example:")
        print("  python mini_project_universal_client.py ../../04_Build_First_MCP_Server/code/example4_server_all_features.py")
        sys.exit(1)

    # Get the path from the arguments
    server_path = sys.argv[1]

    # Resolve to absolute path
    server_path = os.path.abspath(server_path)

    # Check that the file exists
    if not os.path.exists(server_path):
        print(f"ERROR: Server script not found at: {server_path}")
        sys.exit(1)

    return server_path


# ============================================================
# Step 2: Discovery - show all server capabilities
# ============================================================
async def discover_server(session):
    """Discover and display all server capabilities."""

    print("\n" + "=" * 60)
    print("  SERVER CAPABILITIES")
    print("=" * 60)

    # --- Discover Tools ---
    print("\n  TOOLS:")
    print("  " + "-" * 40)
    try:
        tools_result = await session.list_tools()
        tools = tools_result.tools

        if len(tools) == 0:
            print("    (no tools)")
        else:
            for tool in tools:
                print(f"\n    [{tool.name}]")
                if tool.description:
                    print(f"    {tool.description}")

                # Show arguments
                properties = tool.inputSchema.get("properties", {})
                required = tool.inputSchema.get("required", [])
                if properties:
                    for arg_name, arg_info in properties.items():
                        arg_type = arg_info.get("type", "any")
                        req_label = "*" if arg_name in required else " "
                        print(f"      {req_label} {arg_name}: {arg_type}")
    except Exception as error:
        print(f"    Error listing tools: {error}")
        tools = []

    # --- Discover Resources ---
    print("\n  RESOURCES:")
    print("  " + "-" * 40)
    try:
        resources_result = await session.list_resources()
        resources = resources_result.resources

        if len(resources) == 0:
            print("    (no resources)")
        else:
            for resource in resources:
                print(f"\n    [{resource.uri}]")
                print(f"    {resource.name}")
                if resource.description:
                    print(f"    {resource.description}")
    except Exception as error:
        print(f"    Error listing resources: {error}")
        resources = []

    # --- Discover Prompts ---
    print("\n  PROMPTS:")
    print("  " + "-" * 40)
    try:
        prompts_result = await session.list_prompts()
        prompts = prompts_result.prompts

        if len(prompts) == 0:
            print("    (no prompts)")
        else:
            for prompt in prompts:
                print(f"\n    [{prompt.name}]")
                if prompt.description:
                    print(f"    {prompt.description}")
                if prompt.arguments:
                    for arg in prompt.arguments:
                        req_label = "*" if arg.required else " "
                        print(f"      {req_label} {arg.name}")
    except Exception as error:
        print(f"    Error listing prompts: {error}")
        prompts = []

    # --- Summary ---
    print("\n  " + "-" * 40)
    print(f"  Total: {len(tools)} tools, {len(resources)} resources, {len(prompts)} prompts")
    print(f"  (* = required argument)")

    return tools, resources, prompts


# ============================================================
# Step 3: Interactive menu
# ============================================================
def print_menu():
    """Print the interactive menu."""
    print("\n" + "=" * 40)
    print("  UNIVERSAL MCP CLIENT")
    print("=" * 40)
    print("  1. Show server capabilities")
    print("  2. Call a tool")
    print("  3. Read a resource")
    print("  4. Get a prompt")
    print("  5. Quit")
    print("-" * 40)


# ============================================================
# Step 4: Call a tool interactively
# ============================================================
async def interactive_call_tool(session, tools):
    """Let the user pick a tool and call it."""

    # Show available tools
    print("\n--- Call a Tool ---")
    if len(tools) == 0:
        print("  No tools available on this server.")
        return

    print("  Available tools:")
    for i, tool in enumerate(tools):
        print(f"    {i + 1}. {tool.name}")

    # Let the user pick by number or name
    choice = input("\n  Enter tool number or name: ").strip()

    # Find the chosen tool
    selected_tool = None
    # Try matching by number first
    try:
        index = int(choice) - 1
        if 0 <= index < len(tools):
            selected_tool = tools[index]
    except ValueError:
        pass

    # Try matching by name if number did not work
    if selected_tool is None:
        for tool in tools:
            if tool.name == choice:
                selected_tool = tool
                break

    if selected_tool is None:
        print(f"  Tool not found: {choice}")
        return

    print(f"\n  Selected: {selected_tool.name}")

    # Show what arguments are needed
    properties = selected_tool.inputSchema.get("properties", {})
    required = selected_tool.inputSchema.get("required", [])

    # Build arguments by asking the user for each one
    arguments = {}

    if len(properties) == 0:
        print("  This tool takes no arguments.")
    else:
        print("  Enter arguments:")
        for arg_name, arg_info in properties.items():
            arg_type = arg_info.get("type", "string")
            is_required = arg_name in required
            req_label = "(required)" if is_required else "(optional, press Enter to skip)"

            value = input(f"    {arg_name} ({arg_type}) {req_label}: ").strip()

            # Skip empty optional arguments
            if value == "" and not is_required:
                continue

            # Skip empty required arguments (will likely cause an error)
            if value == "" and is_required:
                print(f"    WARNING: {arg_name} is required but was left empty")
                continue

            # Convert to the right type
            if arg_type == "number" or arg_type == "integer":
                try:
                    # Try integer first, then float
                    if "." in value:
                        arguments[arg_name] = float(value)
                    else:
                        arguments[arg_name] = int(value)
                except ValueError:
                    print(f"    WARNING: Could not convert '{value}' to {arg_type}")
                    arguments[arg_name] = value
            elif arg_type == "boolean":
                arguments[arg_name] = value.lower() in ("true", "1", "yes")
            else:
                # Default: treat as string
                arguments[arg_name] = value

    # Call the tool
    print(f"\n  Calling {selected_tool.name}({arguments})...")

    try:
        result = await session.call_tool(selected_tool.name, arguments)

        if result.isError:
            print(f"\n  TOOL ERROR: {result.content[0].text}")
        else:
            print(f"\n  RESULT:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(f"    {content.text}")
                else:
                    print(f"    (non-text content: {content.type})")

    except Exception as error:
        print(f"\n  ERROR: {error}")


# ============================================================
# Step 5: Read a resource interactively
# ============================================================
async def interactive_read_resource(session, resources):
    """Let the user pick a resource and read it."""

    print("\n--- Read a Resource ---")
    if len(resources) == 0:
        print("  No resources available on this server.")
        return

    print("  Available resources:")
    for i, resource in enumerate(resources):
        print(f"    {i + 1}. {resource.uri}")

    # Let the user pick by number or URI
    choice = input("\n  Enter resource number or URI: ").strip()

    # Find the chosen resource
    selected_uri = None
    # Try matching by number first
    try:
        index = int(choice) - 1
        if 0 <= index < len(resources):
            selected_uri = str(resources[index].uri)
    except ValueError:
        pass

    # Try matching by URI
    if selected_uri is None:
        for resource in resources:
            if str(resource.uri) == choice:
                selected_uri = choice
                break

    if selected_uri is None:
        # User may have typed a URI directly
        selected_uri = choice

    print(f"\n  Reading: {selected_uri}")

    try:
        read_result = await session.read_resource(selected_uri)

        print(f"\n  CONTENT:")
        for content in read_result.contents:
            if hasattr(content, "text") and content.text is not None:
                for line in content.text.split("\n"):
                    print(f"    {line}")
            else:
                print(f"    (binary content, {content.uri})")

    except Exception as error:
        print(f"\n  ERROR: {error}")


# ============================================================
# Step 6: Get a prompt interactively
# ============================================================
async def interactive_get_prompt(session, prompts):
    """Let the user pick a prompt and render it."""

    print("\n--- Get a Prompt ---")
    if len(prompts) == 0:
        print("  No prompts available on this server.")
        return

    print("  Available prompts:")
    for i, prompt in enumerate(prompts):
        print(f"    {i + 1}. {prompt.name}")

    # Let the user pick by number or name
    choice = input("\n  Enter prompt number or name: ").strip()

    # Find the chosen prompt
    selected_prompt = None
    try:
        index = int(choice) - 1
        if 0 <= index < len(prompts):
            selected_prompt = prompts[index]
    except ValueError:
        pass

    if selected_prompt is None:
        for prompt in prompts:
            if prompt.name == choice:
                selected_prompt = prompt
                break

    if selected_prompt is None:
        print(f"  Prompt not found: {choice}")
        return

    print(f"\n  Selected: {selected_prompt.name}")

    # Build arguments
    arguments = {}
    if selected_prompt.arguments:
        print("  Enter arguments:")
        for arg in selected_prompt.arguments:
            req_label = "(required)" if arg.required else "(optional)"
            value = input(f"    {arg.name} {req_label}: ").strip()
            if value:
                arguments[arg.name] = value

    # Get the prompt
    print(f"\n  Getting prompt...")

    try:
        prompt_result = await session.get_prompt(selected_prompt.name, arguments)

        print(f"\n  RENDERED PROMPT:")
        print("  " + "-" * 40)
        for message in prompt_result.messages:
            print(f"\n  Role: {message.role}")
            content = message.content
            if hasattr(content, "text"):
                for line in content.text.split("\n"):
                    print(f"    {line}")
            else:
                print(f"    {content}")

    except Exception as error:
        print(f"\n  ERROR: {error}")


# ============================================================
# Step 7: Main function
# ============================================================
async def main():
    """Run the universal MCP client."""

    # Get the server path from command-line arguments
    server_path = get_server_path()

    print("=" * 60)
    print("  UNIVERSAL MCP CLIENT")
    print("=" * 60)
    print(f"\n  Server: {server_path}")

    # Configure the connection
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path]
    )

    # Connect to the server
    print("\n  Connecting...")

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:

                # Initialize the session
                init_result = await session.initialize()
                print(f"  Connected to: {init_result.server_info.name}")

                # Step A: Discover all capabilities
                tools, resources, prompts = await discover_server(session)

                # Step B: Interactive menu loop
                while True:
                    print_menu()
                    choice = input("  Your choice (1-5): ").strip()

                    if choice == "1":
                        # Re-discover (in case server added capabilities)
                        tools, resources, prompts = await discover_server(session)

                    elif choice == "2":
                        await interactive_call_tool(session, tools)

                    elif choice == "3":
                        await interactive_read_resource(session, resources)

                    elif choice == "4":
                        await interactive_get_prompt(session, prompts)

                    elif choice == "5":
                        print("\n  Goodbye!")
                        break

                    else:
                        print("\n  Invalid choice. Please enter 1-5.")

    except KeyboardInterrupt:
        print("\n\n  Interrupted by user.")
    except Exception as error:
        print(f"\n  Connection error: {type(error).__name__}: {error}")

    print("  Disconnected.")


# ============================================================
# Step 8: Entry point
# ============================================================
if __name__ == "__main__":
    asyncio.run(main())
