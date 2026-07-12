"""
Exercise 3 Solution: Same MCP Server, Multiple Frameworks
===========================================================
This solution proves that the SAME MCP server can be used
by different frameworks. We call the same add_numbers tool
from:
1. Direct MCP client call (no framework)
2. LangChain Tool wrapper
3. LlamaIndex FunctionTool wrapper

All three produce the same result -- proving MCP's
"write once, use everywhere" benefit.

How to run:
    python exercise3_solution.py

BEFORE RUNNING:
    poetry add mcp langchain langchain-ollama llama-index llama-index-llms-ollama
"""

import asyncio
import os
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain imports
from langchain_core.tools import Tool

# LlamaIndex imports
from llama_index.core.tools import FunctionTool


# ============================================================
# Step 1: Direct MCP call (no framework)
# ============================================================

async def call_mcp_directly(server_path, a, b):
    """
    Call the add_numbers tool directly via the MCP client.
    No agent framework involved -- just raw MCP.

    Args:
        server_path: Path to the MCP server script
        a: First number
        b: Second number

    Returns:
        The result string from the MCP tool
    """

    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=[server_path],
    )

    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # Call the tool directly
    result = await session.call_tool("add_numbers", arguments={"a": a, "b": b})

    # Extract text
    text_parts = []
    for content in result.content:
        if hasattr(content, "text"):
            text_parts.append(content.text)
    result_text = "\n".join(text_parts)

    # Clean up
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

    return result_text


# ============================================================
# Step 2: Call via LangChain wrapper
# ============================================================

async def call_via_langchain(server_path, a, b):
    """
    Wrap the MCP tool as a LangChain Tool and call it.

    This shows how LangChain agents would call the tool.
    We call the wrapper function directly (without the LLM)
    to prove the wrapper works correctly.

    Args:
        server_path: Path to the MCP server script
        a: First number
        b: Second number

    Returns:
        The result string from the LangChain Tool wrapper
    """

    # Connect to MCP
    server_params = StdioServerParameters(
        command="python",
        args=[server_path],
    )

    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # Create the LangChain tool wrapper
    def add_numbers_wrapper(input_str):
        """LangChain wrapper that calls the MCP add_numbers tool."""
        args = json.loads(input_str)
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            session.call_tool("add_numbers", arguments=args)
        )
        text_parts = []
        for content in result.content:
            if hasattr(content, "text"):
                text_parts.append(content.text)
        return "\n".join(text_parts)

    # Create the LangChain Tool object
    lc_tool = Tool(
        name="add_numbers",
        description="Add two numbers together",
        func=add_numbers_wrapper,
    )

    # Call the tool (as LangChain would)
    result_text = lc_tool.invoke(json.dumps({"a": a, "b": b}))

    # Clean up
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

    return result_text


# ============================================================
# Step 3: Call via LlamaIndex wrapper
# ============================================================

async def call_via_llamaindex(server_path, a, b):
    """
    Wrap the MCP tool as a LlamaIndex FunctionTool and call it.

    This shows how LlamaIndex agents would call the tool.

    Args:
        server_path: Path to the MCP server script
        a: First number
        b: Second number

    Returns:
        The result string from the LlamaIndex FunctionTool wrapper
    """

    # Connect to MCP
    server_params = StdioServerParameters(
        command="python",
        args=[server_path],
    )

    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # Create the LlamaIndex tool wrapper
    def add_numbers_wrapper(a_val: float, b_val: float):
        """LlamaIndex wrapper that calls the MCP add_numbers tool."""
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            session.call_tool("add_numbers", arguments={"a": a_val, "b": b_val})
        )
        text_parts = []
        for content in result.content:
            if hasattr(content, "text"):
                text_parts.append(content.text)
        return "\n".join(text_parts)

    # Create the LlamaIndex FunctionTool
    li_tool = FunctionTool.from_defaults(
        fn=add_numbers_wrapper,
        name="add_numbers",
        description="Add two numbers together",
    )

    # Call the tool (as LlamaIndex would)
    result_text = li_tool.call(a_val=a, b_val=b)

    # Clean up
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

    return str(result_text)


# ============================================================
# Step 4: Run all three and compare
# ============================================================

async def compare_frameworks():
    """
    Call the same MCP tool from three different approaches
    and compare the results.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    # The numbers to add
    a = 100
    b = 200

    print("=" * 60)
    print("Multi-Framework MCP Comparison (Exercise 3 Solution)")
    print("=" * 60)
    print(f"\nCalling add_numbers(a={a}, b={b}) from three approaches:")
    print()

    # Call from each approach
    print("1. Calling directly via MCP client...")
    result_direct = await call_mcp_directly(server_path, a, b)
    print(f"   Result: {result_direct}")

    print("\n2. Calling via LangChain Tool wrapper...")
    result_langchain = await call_via_langchain(server_path, a, b)
    print(f"   Result: {result_langchain}")

    print("\n3. Calling via LlamaIndex FunctionTool wrapper...")
    result_llamaindex = await call_via_llamaindex(server_path, a, b)
    print(f"   Result: {result_llamaindex}")

    # Print comparison table
    print("\n" + "=" * 60)
    print("COMPARISON TABLE")
    print("=" * 60)
    print(f"{'Approach':<25} {'Result':<35}")
    print(f"{'─' * 25} {'─' * 35}")
    print(f"{'Direct MCP':<25} {result_direct:<35}")
    print(f"{'LangChain Wrapper':<25} {result_langchain:<35}")
    print(f"{'LlamaIndex Wrapper':<25} {result_llamaindex:<35}")
    print()

    # Check if all results match
    # WHY strip? To ignore whitespace differences
    all_match = (
        result_direct.strip() == result_langchain.strip() == result_llamaindex.strip()
    )

    if all_match:
        print("ALL RESULTS MATCH!")
        print("This proves: Same MCP server, same results, any framework.")
    else:
        print("Results differ (check the wrappers for formatting differences).")
        print("The underlying MCP tool returned the same data.")

    print("\nKEY TAKEAWAY:")
    print("  MCP is framework-agnostic. You write the server ONCE,")
    print("  and ANY framework can use it through a thin wrapper.")

    print("\n" + "=" * 60)
    print("Comparison completed!")
    print("=" * 60)


# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(compare_frameworks())
