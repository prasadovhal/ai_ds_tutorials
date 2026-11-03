"""
Exercise 3 Solution - Comprehensive App Tester
================================================
A client script that connects to any MCP server, tests all its
tools, resources, and prompts, and reports pass/fail results.

Usage:
    python exercise3_solution.py <server_script.py>

Example:
    python exercise3_solution.py example5_test_server_for_apps.py
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_tools(session):
    """List and test all available tools.

    Returns:
        Tuple of (passed_count, failed_count, results_list)
    """
    passed = 0
    failed = 0
    results = []

    try:
        # List all tools
        tools_response = await session.list_tools()
        tools = tools_response.tools
        print(f"\n  Found {len(tools)} tool(s)")

        for tool in tools:
            tool_name = tool.name
            try:
                # Build simple test arguments based on parameter types
                test_args = {}
                if tool.inputSchema and "properties" in tool.inputSchema:
                    for param_name, param_info in tool.inputSchema["properties"].items():
                        param_type = param_info.get("type", "string")
                        # Provide simple test values for each type
                        if param_type == "string":
                            test_args[param_name] = "test"
                        elif param_type == "integer":
                            test_args[param_name] = 1
                        elif param_type == "number":
                            test_args[param_name] = 1.0
                        elif param_type == "boolean":
                            test_args[param_name] = True

                # Call the tool with test arguments
                result = await session.call_tool(tool_name, test_args)
                results.append(("PASS", f"Tool: {tool_name}"))
                print(f"    PASS - {tool_name}({test_args})")
                passed += 1
            except Exception as e:
                results.append(("FAIL", f"Tool: {tool_name} - {e}"))
                print(f"    FAIL - {tool_name}: {e}")
                failed += 1

    except Exception as e:
        print(f"    ERROR listing tools: {e}")
        results.append(("FAIL", f"List tools: {e}"))
        failed += 1

    return passed, failed, results


async def test_resources(session):
    """List and read all available resources.

    Returns:
        Tuple of (passed_count, failed_count, results_list)
    """
    passed = 0
    failed = 0
    results = []

    try:
        # List all resources
        resources_response = await session.list_resources()
        resources = resources_response.resources
        print(f"\n  Found {len(resources)} resource(s)")

        for resource in resources:
            resource_uri = str(resource.uri)
            try:
                # Try to read the resource
                content = await session.read_resource(resource.uri)
                results.append(("PASS", f"Resource: {resource_uri}"))
                print(f"    PASS - {resource_uri}")
                passed += 1
            except Exception as e:
                results.append(("FAIL", f"Resource: {resource_uri} - {e}"))
                print(f"    FAIL - {resource_uri}: {e}")
                failed += 1

    except Exception as e:
        print(f"    ERROR listing resources: {e}")
        results.append(("FAIL", f"List resources: {e}"))
        failed += 1

    return passed, failed, results


async def test_prompts(session):
    """List and test all available prompts.

    Returns:
        Tuple of (passed_count, failed_count, results_list)
    """
    passed = 0
    failed = 0
    results = []

    try:
        # List all prompts
        prompts_response = await session.list_prompts()
        prompts = prompts_response.prompts
        print(f"\n  Found {len(prompts)} prompt(s)")

        for prompt in prompts:
            prompt_name = prompt.name
            try:
                # Build test arguments for the prompt
                test_args = {}
                if prompt.arguments:
                    for arg in prompt.arguments:
                        test_args[arg.name] = "test"

                # Get the prompt
                result = await session.get_prompt(prompt_name, test_args)
                results.append(("PASS", f"Prompt: {prompt_name}"))
                print(f"    PASS - {prompt_name}({test_args})")
                passed += 1
            except Exception as e:
                results.append(("FAIL", f"Prompt: {prompt_name} - {e}"))
                print(f"    FAIL - {prompt_name}: {e}")
                failed += 1

    except Exception as e:
        print(f"    ERROR listing prompts: {e}")
        results.append(("FAIL", f"List prompts: {e}"))
        failed += 1

    return passed, failed, results


async def test_server(server_script):
    """Connect to an MCP server and run all tests.

    Args:
        server_script: Path to the Python server script
    """
    print("=" * 60)
    print(f"MCP Server Tester")
    print(f"Testing: {server_script}")
    print("=" * 60)

    # Set up connection parameters
    server_params = StdioServerParameters(
        command="python",
        args=[server_script]
    )

    total_passed = 0
    total_failed = 0

    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                print("\n  Connected to server successfully!")

                # Test tools
                print("\n--- Testing Tools ---")
                p, f, _ = await test_tools(session)
                total_passed += p
                total_failed += f

                # Test resources
                print("\n--- Testing Resources ---")
                p, f, _ = await test_resources(session)
                total_passed += p
                total_failed += f

                # Test prompts
                print("\n--- Testing Prompts ---")
                p, f, _ = await test_prompts(session)
                total_passed += p
                total_failed += f

    except Exception as e:
        print(f"\n  FATAL: Could not connect to server: {e}")
        total_failed += 1

    # Print summary
    total = total_passed + total_failed
    print(f"\n{'=' * 60}")
    print(f"Test Summary")
    print(f"{'=' * 60}")
    print(f"  Total Tests: {total}")
    print(f"  Passed:      {total_passed}")
    print(f"  Failed:      {total_failed}")
    status = "ALL TESTS PASSED" if total_failed == 0 else "SOME TESTS FAILED"
    print(f"  Status:      {status}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    # Get server script from command line
    if len(sys.argv) < 2:
        print("Usage: python exercise3_solution.py <server_script.py>")
        print("Example: python exercise3_solution.py example5_test_server_for_apps.py")
        sys.exit(1)

    server_script = sys.argv[1]
    asyncio.run(test_server(server_script))
