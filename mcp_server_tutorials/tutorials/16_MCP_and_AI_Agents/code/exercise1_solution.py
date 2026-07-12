"""
Exercise 1 Solution: LangChain Agent with MCP Calculator
==========================================================
This solution creates a LangChain ReAct agent that connects
to the test MCP server and uses its calculator tools to solve
a multi-step math problem.

The agent breaks down "(10 + 5) * 3 - 7" into individual
tool calls: first add, then multiply, then subtract.

How to run:
    python exercise1_solution.py

BEFORE RUNNING:
    1. ollama serve
    2. ollama pull llama3.2
    3. poetry add mcp langchain langchain-ollama
"""

import asyncio
import os
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain imports
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate


# ============================================================
# Step 1: Connect to MCP server and create LangChain tools
# ============================================================

async def get_calculator_tools(server_script_path):
    """
    Connect to the MCP server and create LangChain Tool wrappers
    for the calculator tools only.

    Args:
        server_script_path: Path to the MCP server script

    Returns:
        Tuple of (tools list, session, transport)
    """

    # Define the connection to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Connect to the server
    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    # Create and initialize the session
    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # List all tools from the MCP server
    tools_response = await session.list_tools()
    mcp_tools = tools_response.tools

    print(f"Found {len(mcp_tools)} tools from MCP server:")
    for tool in mcp_tools:
        print(f"  - {tool.name}: {tool.description}")

    # Only keep calculator tools
    # WHY filter? Because we only need the math tools for this exercise
    calculator_tool_names = [
        "add_numbers",
        "subtract_numbers",
        "multiply_numbers",
        "divide_numbers",
    ]

    # Create LangChain wrappers for each calculator tool
    langchain_tools = []

    for mcp_tool in mcp_tools:
        # Skip non-calculator tools
        if mcp_tool.name not in calculator_tool_names:
            continue

        tool_name = mcp_tool.name

        # Create a wrapper function
        # WHY make_tool_func? To properly capture tool_name in the closure
        def make_tool_func(name, mcp_session):
            def tool_func(input_str):
                """Call the MCP calculator tool."""
                # Parse input as JSON
                try:
                    args = json.loads(input_str)
                except (json.JSONDecodeError, TypeError):
                    args = {"a": 0, "b": 0}

                # Call the MCP tool
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    mcp_session.call_tool(name, arguments=args)
                )

                # Extract text from response
                text_parts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        text_parts.append(content.text)
                return "\n".join(text_parts)

            return tool_func

        # Create the LangChain Tool
        lc_tool = Tool(
            name=tool_name,
            description=mcp_tool.description or f"Calculator: {tool_name}",
            func=make_tool_func(tool_name, session),
        )

        langchain_tools.append(lc_tool)

    print(f"\nCreated {len(langchain_tools)} LangChain calculator tools.")
    return langchain_tools, session, stdio_transport


# ============================================================
# Step 2: Build and run the agent
# ============================================================

async def run_calculator_agent():
    """
    Create a LangChain agent with MCP calculator tools
    and ask it to solve a multi-step math problem.
    """

    # Find the test server script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    print("=" * 60)
    print("LangChain Calculator Agent (Exercise 1 Solution)")
    print("=" * 60)

    # Get calculator tools from the MCP server
    tools, session, transport = await get_calculator_tools(server_path)

    # Create the Ollama LLM
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,  # Deterministic results
    )

    # Create the ReAct prompt
    # WHY this prompt? ReAct is the simplest agent pattern.
    # The LLM reasons about what to do, then acts by calling a tool.
    react_prompt = PromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be valid JSON like {{"a": 5, "b": 3}})
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
    )

    # Create the agent
    agent = create_react_agent(llm, tools, react_prompt)

    # Create the executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,  # Allow enough steps for multi-step math
    )

    # Ask the agent to solve the math problem
    print("\n" + "-" * 60)
    print("Problem: What is (10 + 5) * 3 - 7?")
    print("Expected: (10 + 5) = 15, then 15 * 3 = 45, then 45 - 7 = 38")
    print("-" * 60)

    try:
        result = agent_executor.invoke(
            {
                "input": (
                    "Calculate (10 + 5) * 3 - 7 step by step. "
                    "First use add_numbers to add 10 and 5. "
                    "Then use multiply_numbers to multiply that result by 3. "
                    "Then use subtract_numbers to subtract 7 from that result."
                )
            }
        )
        print(f"\nFinal Answer: {result['output']}")
    except Exception as e:
        print(f"Error: {e}")

    # Clean up
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)

    print("\n" + "=" * 60)
    print("Calculator agent completed!")
    print("=" * 60)


# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(run_calculator_agent())
