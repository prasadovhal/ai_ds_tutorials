"""
Example 2: Using MCP Tools with LangGraph
==========================================

This example shows how to:
1. Build a LangGraph state graph that uses MCP tools
2. Create agent and tool nodes
3. Route between agent reasoning and tool execution
4. Run a multi-step workflow with MCP tools

WHY LangGraph + MCP?
- LangGraph gives you fine-grained control over the agent loop
- You can add conditional logic, branching, and cycles
- MCP provides the tools; LangGraph provides the workflow
- Together, they are the best choice for production agents

BEFORE RUNNING:
1. Make sure Ollama is running: ollama serve
2. Pull a model: ollama pull llama3.2
3. Install dependencies:
   poetry add mcp langchain langchain-ollama langgraph

HOW TO RUN:
    python example2_langgraph_mcp.py
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

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

# LangChain imports (LangGraph uses LangChain under the hood)
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


# =========================================================
# STEP 1: CONNECT TO MCP SERVER AND CREATE TOOLS
# =========================================================

async def create_mcp_tools(server_script_path):
    """
    Connect to MCP server and create LangChain-compatible tools.
    LangGraph uses LangChain tools, so we create the same wrappers.

    Returns:
        Tuple of (tools list, session, transport)
    """

    # Define the server connection parameters
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Connect to the MCP server
    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    # Create and initialize the session
    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # List available tools
    tools_response = await session.list_tools()
    mcp_tools = tools_response.tools

    print(f"Connected to MCP server. Found {len(mcp_tools)} tools.")

    # Create LangChain tools from MCP tools
    langchain_tools = []

    for mcp_tool in mcp_tools:
        tool_name = mcp_tool.name

        # Create a wrapper function for each tool
        def make_tool_func(name, mcp_session):
            def tool_func(input_str):
                # Parse input
                try:
                    args = json.loads(input_str)
                except (json.JSONDecodeError, TypeError):
                    args = {"query": input_str}

                # Call MCP tool
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
            description=mcp_tool.description or f"Tool: {tool_name}",
            func=make_tool_func(tool_name, session),
        )
        langchain_tools.append(lc_tool)

    return langchain_tools, session, stdio_transport


# =========================================================
# STEP 2: BUILD THE LANGGRAPH WORKFLOW
# =========================================================

def build_agent_graph(tools, llm):
    """
    Build a LangGraph state graph with agent and tool nodes.

    The graph looks like this:

        START --> agent --> should_continue? --> tools --> agent
                                             --> END

    WHY this pattern?
    - The agent node uses the LLM to decide what to do
    - If the LLM wants to call a tool, we route to the tools node
    - After the tool runs, we go back to the agent for more reasoning
    - If the LLM is done, we route to END
    """

    # Step 2a: Bind tools to the LLM
    # WHY bind? So the LLM knows what tools are available
    # and can generate tool call messages
    llm_with_tools = llm.bind_tools(tools)

    # Step 2b: Define the agent node
    # This is the "brain" - it uses the LLM to decide what to do
    def agent_node(state):
        """
        The agent node takes the current state (messages),
        passes them to the LLM, and returns the LLM's response.
        """
        # Get the current messages from state
        messages = state["messages"]

        # Call the LLM with the messages
        response = llm_with_tools.invoke(messages)

        # Return the response as a new message
        # LangGraph will add this to the state automatically
        return {"messages": [response]}

    # Step 2c: Define the routing function
    # WHY routing? Because we need to decide:
    # "Did the LLM want to call a tool, or is it done?"
    def should_continue(state):
        """
        Check if the last message contains tool calls.
        If yes, route to the tools node.
        If no, route to END.
        """
        # Get the last message
        last_message = state["messages"][-1]

        # Check if it has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"  # Route to tools node
        else:
            return END  # Route to end

    # Step 2d: Create the ToolNode
    # WHY ToolNode? It is a pre-built LangGraph node that executes tools
    tool_node = ToolNode(tools)

    # Step 2e: Build the graph
    # WHY StateGraph? It manages state (messages) flowing through nodes
    graph = StateGraph(MessagesState)

    # Add nodes to the graph
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Add edges (connections between nodes)
    # START -> agent: The graph always starts at the agent
    graph.add_edge(START, "agent")

    # agent -> conditional: After agent, check if we need tools
    graph.add_conditional_edges("agent", should_continue)

    # tools -> agent: After tools run, go back to agent
    graph.add_edge("tools", "agent")

    # Step 2f: Compile the graph
    # WHY compile? It validates the graph and creates a runnable
    compiled_graph = graph.compile()

    return compiled_graph


# =========================================================
# STEP 3: RUN THE AGENT
# =========================================================

async def run_langgraph_agent():
    """
    Create and run a LangGraph agent with MCP tools.
    """

    # Find the test server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "test_server_for_agents.py")

    print("=" * 60)
    print("LangGraph + MCP Agent Example")
    print("=" * 60)

    # Step 3a: Create MCP tools
    tools, session, transport = await create_mcp_tools(server_path)

    # Step 3b: Create the Ollama LLM
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )

    # Step 3c: Build the graph
    graph = build_agent_graph(tools, llm)

    # Step 3d: Run the graph with a question
    print("\n" + "-" * 60)
    print("Task: Calculate 25 + 17, then save the result as a note")
    print("-" * 60)

    # Create the initial message
    initial_message = HumanMessage(
        content="First, use add_numbers to calculate 25 + 17. "
                "Then use save_note to save the result with title 'Calculation Result'."
    )

    # Run the graph
    # WHY invoke? It runs the graph from start to end
    try:
        result = graph.invoke({"messages": [initial_message]})

        # Print the conversation
        print("\n--- Conversation ---")
        for message in result["messages"]:
            role = message.__class__.__name__
            if hasattr(message, "content") and message.content:
                print(f"\n[{role}]: {message.content}")
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    print(f"\n[Tool Call]: {tc['name']}({tc['args']})")
    except Exception as e:
        print(f"Error running graph: {e}")

    # Step 3e: Run another query
    print("\n" + "-" * 60)
    print("Task: Search for information about Python")
    print("-" * 60)

    search_message = HumanMessage(
        content="Use the search_web tool to search for information about Python programming."
    )

    try:
        result = graph.invoke({"messages": [search_message]})

        print("\n--- Conversation ---")
        for message in result["messages"]:
            role = message.__class__.__name__
            if hasattr(message, "content") and message.content:
                print(f"\n[{role}]: {message.content}")
    except Exception as e:
        print(f"Error running graph: {e}")

    # Step 3f: Clean up
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)

    print("\n" + "=" * 60)
    print("LangGraph agent session completed!")
    print("=" * 60)


# =========================================================
# MAIN ENTRY POINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(run_langgraph_agent())
