"""
Example 3: Using MCP Tools with LlamaIndex
===========================================

This example shows how to:
1. Connect to an MCP server
2. Wrap MCP tools as LlamaIndex FunctionTools
3. Create a LlamaIndex ReAct agent with Ollama
4. Let the agent use MCP tools for computation and search

WHY LlamaIndex + MCP?
- LlamaIndex excels at RAG (Retrieval Augmented Generation)
- MCP tools extend LlamaIndex agents beyond document retrieval
- You can combine LlamaIndex's query engines with MCP's external tools
- Best choice when your app is already built on LlamaIndex

BEFORE RUNNING:
1. Make sure Ollama is running: ollama serve
2. Pull a model: ollama pull llama3.2
3. Install dependencies:
   poetry add mcp llama-index llama-index-llms-ollama

HOW TO RUN:
    python example3_llamaindex_mcp.py
"""

# =========================================================
# IMPORTS
# =========================================================

import asyncio
import os
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LlamaIndex imports
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama


# =========================================================
# STEP 1: CONNECT TO MCP AND CREATE LLAMAINDEX TOOLS
# =========================================================

async def create_llamaindex_tools_from_mcp(server_script_path):
    """
    Connect to an MCP server and create LlamaIndex FunctionTool objects.

    WHY FunctionTool?
    - LlamaIndex uses FunctionTool to wrap Python functions as agent tools
    - Each FunctionTool has a name, description, and callable function
    - The agent's LLM uses these to decide which tool to call

    Returns:
        Tuple of (tools list, session, transport)
    """

    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Open the connection
    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    # Create session
    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # Get available tools
    tools_response = await session.list_tools()
    mcp_tools = tools_response.tools

    print(f"Connected to MCP server. Found {len(mcp_tools)} tools:")
    for tool in mcp_tools:
        print(f"  - {tool.name}: {tool.description}")

    # Create LlamaIndex tools from MCP tools
    llamaindex_tools = []

    for mcp_tool in mcp_tools:
        tool_name = mcp_tool.name
        tool_description = mcp_tool.description or f"MCP tool: {tool_name}"

        # Create a wrapper function
        # WHY a factory function? To properly capture tool_name in the closure
        def make_tool_func(name, mcp_session):
            def tool_func(**kwargs):
                """Call the MCP tool with keyword arguments."""
                # If no kwargs provided, check for a single string arg
                if not kwargs:
                    return "No arguments provided."

                # Call the MCP tool
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    mcp_session.call_tool(name, arguments=kwargs)
                )

                # Extract text content
                text_parts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        text_parts.append(content.text)
                return "\n".join(text_parts)

            return tool_func

        # Create the LlamaIndex FunctionTool
        # WHY FunctionTool.from_defaults? It is the simplest way
        # to create a tool in LlamaIndex
        li_tool = FunctionTool.from_defaults(
            fn=make_tool_func(tool_name, session),
            name=tool_name,
            description=tool_description,
        )

        llamaindex_tools.append(li_tool)

    return llamaindex_tools, session, stdio_transport


# =========================================================
# STEP 2: CREATE AND RUN THE LLAMAINDEX AGENT
# =========================================================

async def run_llamaindex_agent():
    """
    Create a LlamaIndex ReAct agent with MCP tools and run it.
    """

    # Find the test server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    print("=" * 60)
    print("LlamaIndex + MCP Agent Example")
    print("=" * 60)

    # Step 2a: Create tools from MCP server
    tools, session, transport = await create_llamaindex_tools_from_mcp(server_path)

    # Step 2b: Create the Ollama LLM for LlamaIndex
    # WHY Ollama class from llama_index? Because LlamaIndex has
    # its own LLM interface, separate from LangChain
    llm = Ollama(
        model="llama3.2",
        temperature=0,
        request_timeout=120.0,  # WHY timeout? LLM inference can be slow
    )

    # Step 2c: Create the ReAct agent
    # WHY ReAct? It is the simplest agent pattern
    # The agent: Reasons -> Acts -> Observes -> Repeats
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=True,  # WHY verbose? To see the agent's reasoning steps
        max_iterations=5,  # WHY limit? To prevent infinite loops
    )

    # Step 2d: Run a calculation query
    print("\n" + "-" * 60)
    print("Task 1: Calculate 100 * 5")
    print("-" * 60)

    try:
        response = agent.chat("Use the multiply_numbers tool to calculate 100 * 5")
        print(f"\nAgent Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 2e: Run a search query
    print("\n" + "-" * 60)
    print("Task 2: Search for information about AI agents")
    print("-" * 60)

    try:
        response = agent.chat(
            "Use the search_web tool to find information about ai agents"
        )
        print(f"\nAgent Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 2f: Run a notes query
    print("\n" + "-" * 60)
    print("Task 3: Save a note and list all notes")
    print("-" * 60)

    try:
        response = agent.chat(
            "Use save_note to save a note with title 'LlamaIndex Test' "
            "and content 'This note was created by a LlamaIndex agent using MCP tools'"
        )
        print(f"\nAgent Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 2g: Clean up
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)

    print("\n" + "=" * 60)
    print("LlamaIndex agent session completed!")
    print("=" * 60)


# =========================================================
# MAIN ENTRY POINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(run_llamaindex_agent())
