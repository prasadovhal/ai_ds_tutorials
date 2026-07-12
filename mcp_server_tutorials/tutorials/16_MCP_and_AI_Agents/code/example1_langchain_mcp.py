"""
Example 1: Using MCP Tools with LangChain
==========================================

This example shows how to:
1. Connect to an MCP server
2. Wrap MCP tools as LangChain tools
3. Create a LangChain agent with Ollama
4. Let the agent use MCP tools to answer questions

WHY LangChain + MCP?
- LangChain is the most popular agent framework
- MCP provides a standardized way to define tools
- Together, they let you build agents that use ANY MCP server

BEFORE RUNNING:
1. Make sure Ollama is running: ollama serve
2. Pull a model: ollama pull llama3.2
3. Install dependencies:
   poetry add mcp langchain langchain-ollama

HOW TO RUN:
    python example1_langchain_mcp.py
"""

# =========================================================
# IMPORTS
# =========================================================

# asyncio is needed because MCP uses async communication
import asyncio

# sys helps us find the path to the test server
import sys
import os

# MCP client tools for connecting to servers
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain imports for building the agent
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate


# =========================================================
# STEP 1: DEFINE THE MCP-TO-LANGCHAIN ADAPTER
# =========================================================

# This function connects to an MCP server and returns LangChain tools
# WHY a function? Because we need to do this async (MCP uses async)

async def get_langchain_tools_from_mcp(server_script_path):
    """
    Connect to an MCP server and create LangChain Tool objects
    for each tool the server provides.

    Args:
        server_script_path: Path to the MCP server Python script

    Returns:
        A tuple of (list of LangChain tools, MCP session, context managers)
    """

    # Step 1a: Define how to connect to the MCP server
    # WHY StdioServerParameters? Because the server runs as a subprocess
    # and communicates via stdin/stdout
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Step 1b: Create the connection to the MCP server
    # WHY context manager? Because we need to properly close the connection
    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    # Step 1c: Create and initialize the MCP session
    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # Step 1d: List all available tools from the MCP server
    tools_response = await session.list_tools()
    mcp_tools = tools_response.tools

    print(f"Found {len(mcp_tools)} tools from MCP server:")
    for tool in mcp_tools:
        print(f"  - {tool.name}: {tool.description}")

    # Step 1e: Create a LangChain tool for each MCP tool
    langchain_tools = []

    for mcp_tool in mcp_tools:
        # We need to capture the tool name in the closure
        # WHY? Because Python closures capture by reference, not by value
        tool_name = mcp_tool.name

        # Create a wrapper function that calls the MCP tool
        # This is the bridge between LangChain and MCP
        def make_tool_func(name, mcp_session):
            """Create a function that calls an MCP tool."""
            def tool_func(input_str):
                """Call the MCP tool with the given input."""
                # Parse the input string into arguments
                # LangChain passes tool input as a string
                import json
                try:
                    # Try to parse as JSON first
                    args = json.loads(input_str)
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, use as a single argument
                    args = {"query": input_str}

                # Call the MCP tool using asyncio
                # WHY asyncio.get_event_loop()? Because LangChain tools are sync
                # but MCP is async, so we need to bridge the gap
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    mcp_session.call_tool(name, arguments=args)
                )

                # Extract the text content from the MCP response
                # MCP returns a list of content objects
                text_parts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        text_parts.append(content.text)
                return "\n".join(text_parts)

            return tool_func

        # Create the LangChain Tool object
        lc_tool = Tool(
            name=tool_name,
            description=mcp_tool.description or f"MCP tool: {tool_name}",
            func=make_tool_func(tool_name, session),
        )

        langchain_tools.append(lc_tool)

    return langchain_tools, session, stdio_transport


# =========================================================
# STEP 2: CREATE THE LANGCHAIN AGENT
# =========================================================

async def run_langchain_agent():
    """
    Create and run a LangChain agent that uses MCP tools.
    """

    # Step 2a: Find the test server script
    # WHY os.path? Because the server is in the same directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    print("=" * 60)
    print("LangChain + MCP Agent Example")
    print("=" * 60)
    print(f"\nConnecting to MCP server: {server_path}")

    # Step 2b: Get LangChain tools from the MCP server
    tools, session, transport = await get_langchain_tools_from_mcp(server_path)

    # Step 2c: Create the Ollama LLM
    # WHY Ollama? Because it is free and runs locally
    # Make sure you have pulled the model: ollama pull llama3.2
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,  # WHY 0? For deterministic, reproducible results
    )

    # Step 2d: Create a simple ReAct prompt
    # WHY ReAct? It is the simplest agent pattern:
    # the LLM Reasons about what to do, then Acts by calling a tool
    react_prompt = PromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be valid JSON)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
    )

    # Step 2e: Create the agent
    agent = create_react_agent(llm, tools, react_prompt)

    # Step 2f: Create the agent executor
    # WHY AgentExecutor? It manages the agent loop
    # (think -> act -> observe -> repeat)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # WHY verbose? So we can see each step
        handle_parsing_errors=True,  # WHY? To handle LLM output format errors
        max_iterations=5,  # WHY limit? To prevent infinite loops
    )

    # Step 2g: Run the agent with a question
    print("\n" + "=" * 60)
    print("Asking the agent to do a calculation...")
    print("=" * 60)

    try:
        result = agent_executor.invoke(
            {"input": "What is 15 + 27? Use the add_numbers tool."}
        )
        print(f"\nFinal Answer: {result['output']}")
    except Exception as e:
        print(f"Agent encountered an error: {e}")

    # Step 2h: Try another question
    print("\n" + "=" * 60)
    print("Asking the agent to search for information...")
    print("=" * 60)

    try:
        result = agent_executor.invoke(
            {"input": "Search for information about MCP using the search_web tool."}
        )
        print(f"\nFinal Answer: {result['output']}")
    except Exception as e:
        print(f"Agent encountered an error: {e}")

    # Step 2i: Clean up the MCP connection
    # WHY clean up? Because leaving connections open wastes resources
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)

    print("\n" + "=" * 60)
    print("Agent session completed!")
    print("=" * 60)


# =========================================================
# MAIN ENTRY POINT
# =========================================================

if __name__ == "__main__":
    # Run the async function
    # WHY asyncio.run()? Because our main function is async
    # (MCP requires async communication)
    asyncio.run(run_langchain_agent())
