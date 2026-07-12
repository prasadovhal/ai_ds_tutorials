"""
Exercise 2 Solution: LangGraph Workflow with MCP Tools
========================================================
This solution creates a LangGraph workflow that:
1. Searches for information using MCP's search_web tool
2. Saves the results as a note using MCP's save_note tool
3. Lists all notes to confirm the save

The workflow uses a state graph with agent and tool nodes.

How to run:
    python exercise2_solution.py

BEFORE RUNNING:
    1. ollama serve
    2. ollama pull llama3.2
    3. poetry add mcp langchain langchain-ollama langgraph
"""

import asyncio
import os
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

# LangChain imports
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


# ============================================================
# Step 1: Connect to MCP and create tool wrappers
# ============================================================

async def create_research_tools(server_script_path):
    """
    Connect to MCP server and create LangChain tools for
    the research workflow: search, save notes, list notes.

    Returns:
        Tuple of (tools, session, transport)
    """

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

    # Get available tools
    tools_response = await session.list_tools()
    mcp_tools = tools_response.tools

    print(f"Connected to MCP server. Found {len(mcp_tools)} tools.")

    # Only keep the tools we need for the research workflow
    needed_tools = ["search_web", "save_note", "list_notes"]

    # Create LangChain wrappers
    langchain_tools = []

    for mcp_tool in mcp_tools:
        if mcp_tool.name not in needed_tools:
            continue

        tool_name = mcp_tool.name

        def make_tool_func(name, mcp_session):
            def tool_func(input_str):
                """Call the MCP tool."""
                try:
                    args = json.loads(input_str)
                except (json.JSONDecodeError, TypeError):
                    # For tools like list_notes that take no args,
                    # or for search_web with a plain string query
                    if name == "list_notes":
                        args = {}
                    else:
                        args = {"query": input_str}

                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    mcp_session.call_tool(name, arguments=args)
                )

                text_parts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        text_parts.append(content.text)
                return "\n".join(text_parts)

            return tool_func

        lc_tool = Tool(
            name=tool_name,
            description=mcp_tool.description or f"Tool: {tool_name}",
            func=make_tool_func(tool_name, session),
        )
        langchain_tools.append(lc_tool)

    print(f"Created {len(langchain_tools)} LangChain tools for research workflow.")
    return langchain_tools, session, stdio_transport


# ============================================================
# Step 2: Build the LangGraph state graph
# ============================================================

def build_research_graph(tools, llm):
    """
    Build a LangGraph state graph for the research workflow.

    Graph structure:
        START --> agent --> should_continue? --> tools --> agent
                                             --> END
    """

    # Bind tools to the LLM so it knows what is available
    llm_with_tools = llm.bind_tools(tools)

    # Define the agent node
    # This is where the LLM reasons about what to do
    def agent_node(state):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define the routing function
    # WHY? To decide whether the agent wants to call a tool or is done
    def should_continue(state):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return END

    # Create the tool node
    tool_node = ToolNode(tools)

    # Build the graph
    graph = StateGraph(MessagesState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    # Compile and return
    return graph.compile()


# ============================================================
# Step 3: Run the research workflow
# ============================================================

async def run_research_workflow():
    """
    Run the LangGraph research workflow:
    Search -> Save Note -> List Notes
    """

    # Find the test server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    print("=" * 60)
    print("LangGraph Research Workflow (Exercise 2 Solution)")
    print("=" * 60)

    # Create tools from MCP server
    tools, session, transport = await create_research_tools(server_path)

    # Create the LLM
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )

    # Build the graph
    graph = build_research_graph(tools, llm)

    # Run the workflow
    print("\n" + "-" * 60)
    print("Task: Search, Save, and List")
    print("-" * 60)

    task_message = HumanMessage(
        content=(
            "Please do the following steps in order: "
            "1. Use search_web to search for 'python programming'. "
            "2. Use save_note to save the search results with "
            "title 'Python Research' and the search results as content. "
            "3. Use list_notes to show all saved notes."
        )
    )

    try:
        result = graph.invoke({"messages": [task_message]})

        # Print the conversation
        print("\n--- Workflow Conversation ---")
        for message in result["messages"]:
            role = message.__class__.__name__
            if hasattr(message, "content") and message.content:
                content_preview = str(message.content)
                if len(content_preview) > 200:
                    content_preview = content_preview[:200] + "..."
                print(f"\n[{role}]: {content_preview}")
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    print(f"\n[Tool Call]: {tc['name']}({tc['args']})")

    except Exception as e:
        print(f"Error running workflow: {e}")

    # Clean up
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)

    print("\n" + "=" * 60)
    print("Research workflow completed!")
    print("=" * 60)


# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(run_research_workflow())
