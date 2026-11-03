"""
Example 5: Using MCP Tools with Pydantic AI
=============================================

This example shows how to:
1. Connect to an MCP server
2. Wrap MCP tools as Pydantic AI tools
3. Create a Pydantic AI Agent with MCP tools
4. Run the agent to answer questions

WHY Pydantic AI + MCP?
- Pydantic AI is built on top of Pydantic (the data validation library)
- It provides TYPE-SAFE agent development
- Tool inputs and outputs are validated using Pydantic models
- Best choice when you want strict type checking and validation
- Clean, Pythonic API that feels natural to Python developers

HOW Pydantic AI WORKS:
- You create an Agent with a model and tools
- Tools are Python functions with type hints
- Pydantic AI validates inputs/outputs automatically
- The agent uses the LLM to decide which tools to call

BEFORE RUNNING:
1. Make sure Ollama is running: ollama serve
2. Pull a model: ollama pull llama3.2
3. Install dependencies:
   poetry add mcp pydantic-ai

HOW TO RUN:
    python example5_pydantic_ai_mcp.py

NOTE: Pydantic AI is a newer framework. This example shows
the integration PATTERN. The exact API may evolve.
"""

# =========================================================
# IMPORTS
# =========================================================

# asyncio for MCP async communication
import asyncio

# os for file paths
import os

# json for parsing arguments
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Pydantic AI imports
# WHY these imports?
# - Agent: The main class for creating AI agents
# - RunContext: Provides context to tool functions during execution
from pydantic_ai import Agent, RunContext

# Pydantic for data models
# WHY Pydantic? Because Pydantic AI uses Pydantic models
# for type-safe tool definitions
from pydantic import BaseModel


# =========================================================
# STEP 1: DEFINE PYDANTIC MODELS FOR TOOL INPUTS
# =========================================================
# Pydantic AI uses Pydantic models to validate tool inputs.
# This means if the LLM sends wrong types, Pydantic catches
# the error BEFORE the tool runs.

class AddNumbersInput(BaseModel):
    """Input model for the add_numbers tool."""
    a: float  # The first number
    b: float  # The second number


class SearchInput(BaseModel):
    """Input model for the search_web tool."""
    query: str  # The search query


class SaveNoteInput(BaseModel):
    """Input model for the save_note tool."""
    title: str    # Note title
    content: str  # Note content


# =========================================================
# STEP 2: CREATE AN MCP CLIENT HELPER
# =========================================================
# This helper connects to the MCP server and calls tools.
# Pydantic AI tool functions will use this to communicate
# with the MCP server.

class MCPClient:
    """
    A simple helper class that connects to an MCP server
    and calls tools on it.

    WHY a class? Because we need to manage the connection
    lifecycle (connect, call tools, disconnect).
    """

    def __init__(self, server_script_path):
        """Store the server script path for later use."""
        self.server_script_path = server_script_path
        self.session = None
        self.transport = None

    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
        )

        # Open the connection
        self.transport = stdio_client(server_params)
        read_stream, write_stream = await self.transport.__aenter__()

        # Create and initialize the session
        self.session = ClientSession(read_stream, write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

        # List available tools
        tools_response = await self.session.list_tools()
        print(f"Connected to MCP server. Found {len(tools_response.tools)} tools:")
        for tool in tools_response.tools:
            print(f"  - {tool.name}: {tool.description}")

    async def call_tool(self, tool_name, arguments):
        """
        Call an MCP tool and return its text result.

        Args:
            tool_name: The name of the tool to call
            arguments: A dictionary of arguments for the tool

        Returns:
            The text result from the tool
        """
        if self.session is None:
            return "Error: Not connected to MCP server."

        # Call the tool on the MCP server
        result = await self.session.call_tool(tool_name, arguments=arguments)

        # Extract text from the response
        text_parts = []
        for content in result.content:
            if hasattr(content, "text"):
                text_parts.append(content.text)
        return "\n".join(text_parts)

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.transport:
            await self.transport.__aexit__(None, None, None)
        print("Disconnected from MCP server.")


# =========================================================
# STEP 3: CREATE THE PYDANTIC AI AGENT WITH MCP TOOLS
# =========================================================

async def run_pydantic_ai_agent():
    """
    Create a Pydantic AI agent that uses MCP tools.
    """

    print("=" * 60)
    print("Pydantic AI + MCP Integration Example")
    print("=" * 60)

    # Step 3a: Connect to the MCP server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    mcp_client = MCPClient(server_path)
    await mcp_client.connect()

    # Step 3b: Create the Pydantic AI agent
    # WHY 'ollama:llama3.2'? Pydantic AI uses a "provider:model" format
    # This tells it to use Ollama with the llama3.2 model
    agent = Agent(
        model="ollama:llama3.2",
        system_prompt=(
            "You are a helpful assistant. You can add numbers, "
            "search the web, and save notes. Always use the available "
            "tools when asked to perform these tasks."
        ),
    )

    # Step 3c: Register MCP tools with the agent
    # WHY @agent.tool? This decorator registers a function as a tool
    # that the agent can call. Pydantic AI validates the inputs
    # using the type hints we provide.

    @agent.tool
    async def add_numbers(ctx: RunContext, a: float, b: float) -> str:
        """Add two numbers together.

        Args:
            ctx: The run context (provided by Pydantic AI)
            a: The first number
            b: The second number

        Returns:
            The result of adding a and b
        """
        # Call the MCP tool through our client
        result = await mcp_client.call_tool("add_numbers", {"a": a, "b": b})
        return result

    @agent.tool
    async def search_web(ctx: RunContext, query: str) -> str:
        """Search the web for information.

        Args:
            ctx: The run context
            query: The search query

        Returns:
            Search results
        """
        result = await mcp_client.call_tool("search_web", {"query": query})
        return result

    @agent.tool
    async def save_note(ctx: RunContext, title: str, content: str) -> str:
        """Save a note with a title and content.

        Args:
            ctx: The run context
            title: The note title
            content: The note content

        Returns:
            Confirmation message
        """
        result = await mcp_client.call_tool(
            "save_note", {"title": title, "content": content}
        )
        return result

    # Step 3d: Run the agent with a query
    print("\n" + "-" * 60)
    print("Task 1: Calculate 42 + 58")
    print("-" * 60)

    try:
        result = await agent.run("What is 42 + 58? Use the add_numbers tool.")
        print(f"\nAgent Response: {result.data}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 3e: Run another query
    print("\n" + "-" * 60)
    print("Task 2: Search for MCP information")
    print("-" * 60)

    try:
        result = await agent.run(
            "Search for information about MCP using the search_web tool."
        )
        print(f"\nAgent Response: {result.data}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 3f: Clean up
    await mcp_client.disconnect()

    print("\n" + "=" * 60)
    print("Pydantic AI + MCP session completed!")
    print("=" * 60)


# =========================================================
# MAIN ENTRY POINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(run_pydantic_ai_agent())
