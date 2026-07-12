"""
Example 4: Using MCP Tools with CrewAI
=======================================

This example shows how to:
1. Connect to an MCP server
2. Wrap MCP tools as CrewAI-compatible tools
3. Create a CrewAI Agent that uses MCP tools
4. Run a Task using the agent

WHY CrewAI + MCP?
- CrewAI is built for multi-agent collaboration
- Each agent can have a different role (researcher, writer, reviewer)
- MCP tools give each agent access to external capabilities
- Together, you can build teams of agents that share MCP tools

HOW CrewAI WORKS:
- You define Agents (each has a role, goal, and tools)
- You define Tasks (each has a description and an assigned agent)
- You create a Crew (a group of agents working on tasks)
- The Crew runs all tasks in order

BEFORE RUNNING:
1. Make sure Ollama is running: ollama serve
2. Pull a model: ollama pull llama3.2
3. Install dependencies:
   poetry add mcp crewai crewai-tools

HOW TO RUN:
    python example4_crewai_mcp.py

NOTE: CrewAI integration with MCP is still evolving.
This example shows the PATTERN for wrapping MCP tools
so they work with CrewAI agents.
"""

# =========================================================
# IMPORTS
# =========================================================

# asyncio for MCP's async communication
import asyncio

# os and sys for file paths
import os
import sys

# json for parsing tool arguments
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# CrewAI imports
# WHY these imports?
# - Agent: Defines an AI agent with a role and tools
# - Task: Defines a job for an agent to do
# - Crew: Groups agents and tasks together
# - Process: How tasks are executed (sequential or hierarchical)
from crewai import Agent, Task, Crew, Process

# CrewAI tool decorator
# WHY @tool? CrewAI uses this to register functions as agent tools
from crewai.tools import tool


# =========================================================
# STEP 1: CONNECT TO MCP AND GET TOOL DEFINITIONS
# =========================================================

async def get_mcp_tool_info(server_script_path):
    """
    Connect to an MCP server and get the list of available tools.
    Returns the tool names and descriptions so we can create
    CrewAI wrappers for them.

    Args:
        server_script_path: Path to the MCP server Python script

    Returns:
        A list of dictionaries with tool name and description
    """

    # Define how to connect to the MCP server
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

    # List available tools
    tools_response = await session.list_tools()

    # Collect tool information
    tool_info_list = []
    for mcp_tool in tools_response.tools:
        tool_info = {
            "name": mcp_tool.name,
            "description": mcp_tool.description or f"MCP tool: {mcp_tool.name}",
        }
        tool_info_list.append(tool_info)

    print(f"Found {len(tool_info_list)} tools from MCP server:")
    for info in tool_info_list:
        print(f"  - {info['name']}: {info['description']}")

    # Clean up the connection
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

    return tool_info_list


# =========================================================
# STEP 2: CREATE CREWAI TOOL WRAPPERS
# =========================================================

# In CrewAI, tools are Python functions decorated with @tool.
# We create wrapper functions that call the MCP server when invoked.
#
# WHY wrapper functions?
# CrewAI expects tools to be simple Python functions.
# MCP tools live on a separate server.
# The wrapper bridges the gap: CrewAI calls the wrapper,
# the wrapper calls the MCP server.

# NOTE: In a real application, you would keep the MCP session
# open and reuse it. Here we reconnect for each tool call
# to keep the example simple.

def create_mcp_caller(server_script_path):
    """
    Create a function that calls an MCP tool by name.
    This function handles connecting to the server,
    calling the tool, and returning the result.

    Args:
        server_script_path: Path to the MCP server script

    Returns:
        A function that takes (tool_name, arguments) and returns a string
    """

    async def call_mcp_tool(tool_name, arguments):
        """Call a specific MCP tool and return its result."""

        # Connect to the MCP server
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )

        stdio_transport = stdio_client(server_params)
        read_stream, write_stream = await stdio_transport.__aenter__()

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()
        await session.initialize()

        # Call the tool
        result = await session.call_tool(tool_name, arguments=arguments)

        # Extract text content
        text_parts = []
        for content in result.content:
            if hasattr(content, "text"):
                text_parts.append(content.text)

        # Clean up
        await session.__aexit__(None, None, None)
        await stdio_transport.__aexit__(None, None, None)

        return "\n".join(text_parts)

    def sync_caller(tool_name, arguments):
        """Synchronous wrapper around the async MCP call."""
        return asyncio.run(call_mcp_tool(tool_name, arguments))

    return sync_caller


# =========================================================
# STEP 3: DEFINE CREWAI TOOLS THAT WRAP MCP
# =========================================================

# We define CrewAI tools that call our MCP test server.
# Each tool uses the @tool decorator so CrewAI recognizes it.
#
# NOTE: We define these as module-level functions because
# CrewAI expects tool functions to be importable.

# Get the path to our test server
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(CURRENT_DIR, "test_server_for_agents.py")

# Create the MCP caller function
mcp_call = create_mcp_caller(SERVER_PATH)


@tool
def mcp_add_numbers(input_text: str) -> str:
    """Add two numbers using the MCP calculator server.
    Input should be JSON like: {"a": 5, "b": 3}"""

    # Parse the input
    try:
        args = json.loads(input_text)
    except json.JSONDecodeError:
        return "Error: Input must be JSON with 'a' and 'b' keys."

    # Call the MCP tool
    return mcp_call("add_numbers", args)


@tool
def mcp_search_web(query: str) -> str:
    """Search the web for information using the MCP search server.
    Input should be the search query as a string."""

    # Call the MCP tool
    return mcp_call("search_web", {"query": query})


@tool
def mcp_save_note(input_text: str) -> str:
    """Save a note using the MCP notes server.
    Input should be JSON like: {"title": "My Note", "content": "Note body"}"""

    try:
        args = json.loads(input_text)
    except json.JSONDecodeError:
        return "Error: Input must be JSON with 'title' and 'content' keys."

    return mcp_call("save_note", args)


# =========================================================
# STEP 4: CREATE THE CREWAI AGENT AND CREW
# =========================================================

def run_crewai_with_mcp():
    """
    Create a CrewAI crew with an agent that uses MCP tools.
    """

    print("=" * 60)
    print("CrewAI + MCP Integration Example")
    print("=" * 60)

    # Step 4a: Create a research agent
    # WHY role, goal, backstory? CrewAI uses these to guide the agent's
    # behavior. The LLM reads these to understand how to act.
    researcher = Agent(
        role="Research Assistant",
        goal="Find information and perform calculations accurately",
        backstory=(
            "You are a helpful research assistant. You use tools "
            "to search for information and perform calculations. "
            "You always use the available tools rather than guessing."
        ),
        tools=[mcp_add_numbers, mcp_search_web, mcp_save_note],
        verbose=True,  # WHY verbose? To see the agent's reasoning
    )

    # Step 4b: Create a task for the agent
    # WHY Task? CrewAI organizes work into tasks.
    # Each task has a description and an assigned agent.
    research_task = Task(
        description=(
            "Use the mcp_search_web tool to search for information about "
            "'python programming'. Then use mcp_add_numbers to calculate "
            "25 + 37. Finally, save a note summarizing what you found."
        ),
        expected_output="A summary of the research and calculation results.",
        agent=researcher,
    )

    # Step 4c: Create the crew
    # WHY Crew? It orchestrates the agents and tasks.
    # Process.sequential means tasks run one after another.
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        process=Process.sequential,
        verbose=True,
    )

    # Step 4d: Run the crew
    print("\nStarting CrewAI crew with MCP tools...\n")

    try:
        result = crew.kickoff()
        print("\n" + "=" * 60)
        print("CREW RESULT:")
        print("=" * 60)
        print(result)
    except Exception as e:
        print(f"\nError running crew: {e}")
        print("Make sure Ollama is running and crewai is installed.")

    print("\n" + "=" * 60)
    print("CrewAI + MCP session completed!")
    print("=" * 60)


# =========================================================
# MAIN ENTRY POINT
# =========================================================

if __name__ == "__main__":
    run_crewai_with_mcp()
