"""
Example 6: Framework Comparison for MCP Integration
=====================================================

This script prints a detailed comparison table showing how
each major AI agent framework integrates with MCP.

This is NOT a runnable agent -- it is a reference guide that
helps you choose the right framework for your project.

HOW TO RUN:
    python example6_comparison.py

The output shows:
1. A comparison table of all frameworks
2. Key differences in how each one integrates with MCP
3. When to use which framework
4. Code pattern summaries
"""


def print_comparison_table():
    """
    Print a formatted comparison table of AI agent frameworks
    and how they integrate with MCP.
    """

    print("=" * 80)
    print("AI AGENT FRAMEWORK COMPARISON FOR MCP INTEGRATION")
    print("=" * 80)
    print()

    # =========================================================
    # TABLE 1: Framework Overview
    # =========================================================
    print("-" * 80)
    print("TABLE 1: FRAMEWORK OVERVIEW")
    print("-" * 80)
    print()
    print(f"{'Framework':<15} {'Best For':<25} {'Complexity':<12} {'MCP Support':<15}")
    print(f"{'─' * 15} {'─' * 25} {'─' * 12} {'─' * 15}")
    print(f"{'LangChain':<15} {'General agents':<25} {'Medium':<12} {'Via wrappers':<15}")
    print(f"{'LangGraph':<15} {'Complex workflows':<25} {'High':<12} {'Via wrappers':<15}")
    print(f"{'LlamaIndex':<15} {'RAG + agents':<25} {'Medium':<12} {'Via wrappers':<15}")
    print(f"{'CrewAI':<15} {'Multi-agent teams':<25} {'Low':<12} {'Via wrappers':<15}")
    print(f"{'Pydantic AI':<15} {'Type-safe agents':<25} {'Low':<12} {'Via wrappers':<15}")
    print()

    # =========================================================
    # TABLE 2: MCP Integration Details
    # =========================================================
    print("-" * 80)
    print("TABLE 2: MCP INTEGRATION DETAILS")
    print("-" * 80)
    print()
    print(f"{'Framework':<15} {'Tool Wrapper':<20} {'Async Support':<15} {'Connection Mgmt':<20}")
    print(f"{'─' * 15} {'─' * 20} {'─' * 15} {'─' * 20}")
    print(f"{'LangChain':<15} {'langchain Tool':<20} {'Sync wrapper':<15} {'Manual':<20}")
    print(f"{'LangGraph':<15} {'langchain Tool':<20} {'Sync wrapper':<15} {'Manual':<20}")
    print(f"{'LlamaIndex':<15} {'FunctionTool':<20} {'Sync wrapper':<15} {'Manual':<20}")
    print(f"{'CrewAI':<15} {'@tool decorator':<20} {'Sync only':<15} {'Per-call':<20}")
    print(f"{'Pydantic AI':<15} {'@agent.tool':<20} {'Native async':<15} {'Manual':<20}")
    print()

    # =========================================================
    # TABLE 3: Key Differences
    # =========================================================
    print("-" * 80)
    print("TABLE 3: KEY DIFFERENCES")
    print("-" * 80)
    print()

    frameworks = [
        {
            "name": "LangChain",
            "agent_type": "ReAct Agent",
            "tool_format": "Tool(name, description, func)",
            "llm_config": "ChatOllama(model=...)",
            "strengths": "Largest ecosystem, most examples online",
            "weaknesses": "Can be verbose, many abstractions",
        },
        {
            "name": "LangGraph",
            "agent_type": "StateGraph with nodes",
            "tool_format": "Tool(name, description, func)",
            "llm_config": "ChatOllama(model=...)",
            "strengths": "Fine-grained control, conditional routing",
            "weaknesses": "Higher complexity, steeper learning curve",
        },
        {
            "name": "LlamaIndex",
            "agent_type": "ReActAgent",
            "tool_format": "FunctionTool.from_defaults(fn, name, desc)",
            "llm_config": "Ollama(model=...)",
            "strengths": "Best RAG integration, query engines",
            "weaknesses": "Less flexible for non-RAG use cases",
        },
        {
            "name": "CrewAI",
            "agent_type": "Agent with role/goal/backstory",
            "tool_format": "@tool decorated functions",
            "llm_config": "Uses Ollama via config or env vars",
            "strengths": "Multi-agent collaboration, simple API",
            "weaknesses": "Less control over individual steps",
        },
        {
            "name": "Pydantic AI",
            "agent_type": "Agent with system prompt",
            "tool_format": "@agent.tool with type hints",
            "llm_config": "Agent(model='ollama:llama3.2')",
            "strengths": "Type safety, clean Pythonic API",
            "weaknesses": "Newer, smaller ecosystem",
        },
    ]

    for fw in frameworks:
        print(f"  {fw['name']}")
        print(f"    Agent Type   : {fw['agent_type']}")
        print(f"    Tool Format  : {fw['tool_format']}")
        print(f"    LLM Config   : {fw['llm_config']}")
        print(f"    Strengths    : {fw['strengths']}")
        print(f"    Weaknesses   : {fw['weaknesses']}")
        print()

    # =========================================================
    # TABLE 4: When to Use Which Framework
    # =========================================================
    print("-" * 80)
    print("TABLE 4: WHEN TO USE WHICH FRAMEWORK")
    print("-" * 80)
    print()
    print("  USE LangChain WHEN:")
    print("    - You need a general-purpose agent")
    print("    - You want the largest community and most examples")
    print("    - You are already using LangChain in your project")
    print()
    print("  USE LangGraph WHEN:")
    print("    - You need complex workflows with branching logic")
    print("    - You want fine-grained control over the agent loop")
    print("    - You are building production-grade agent systems")
    print()
    print("  USE LlamaIndex WHEN:")
    print("    - Your primary use case is RAG (Retrieval Augmented Generation)")
    print("    - You want to combine document search with MCP tools")
    print("    - You are already using LlamaIndex for document indexing")
    print()
    print("  USE CrewAI WHEN:")
    print("    - You need multiple agents collaborating on a task")
    print("    - Each agent has a different role (researcher, writer, etc.)")
    print("    - You want the simplest multi-agent setup")
    print()
    print("  USE Pydantic AI WHEN:")
    print("    - You want type-safe, validated tool inputs/outputs")
    print("    - You prefer a clean, modern Pythonic API")
    print("    - You are already using Pydantic in your project")
    print()

    # =========================================================
    # TABLE 5: MCP Integration Pattern Summary
    # =========================================================
    print("-" * 80)
    print("TABLE 5: COMMON MCP INTEGRATION PATTERN")
    print("-" * 80)
    print()
    print("  All frameworks follow the same basic pattern:")
    print()
    print("  1. CONNECT to the MCP server")
    print("     - Use StdioServerParameters to define connection")
    print("     - Use stdio_client() to create the transport")
    print("     - Use ClientSession to manage the session")
    print()
    print("  2. LIST tools from the MCP server")
    print("     - Call session.list_tools() to get available tools")
    print("     - Each tool has a name, description, and input schema")
    print()
    print("  3. WRAP each MCP tool in the framework's tool format")
    print("     - LangChain/LangGraph: Tool(name, description, func)")
    print("     - LlamaIndex: FunctionTool.from_defaults(fn, name, desc)")
    print("     - CrewAI: @tool decorated function")
    print("     - Pydantic AI: @agent.tool decorated function")
    print()
    print("  4. CREATE the agent with the wrapped tools")
    print("     - Each framework has its own agent creation API")
    print("     - Bind the LLM and tools together")
    print()
    print("  5. RUN the agent")
    print("     - Send a user message / task")
    print("     - The agent reasons, calls tools, and responds")
    print()
    print("  6. CLEAN UP the MCP connection")
    print("     - Close the session and transport")
    print()

    # =========================================================
    # TABLE 6: Installation Commands
    # =========================================================
    print("-" * 80)
    print("TABLE 6: INSTALLATION COMMANDS")
    print("-" * 80)
    print()
    print("  LangChain:")
    print("    poetry add mcp langchain langchain-ollama")
    print()
    print("  LangGraph:")
    print("    poetry add mcp langchain langchain-ollama langgraph")
    print()
    print("  LlamaIndex:")
    print("    poetry add mcp llama-index llama-index-llms-ollama")
    print()
    print("  CrewAI:")
    print("    poetry add mcp crewai crewai-tools")
    print()
    print("  Pydantic AI:")
    print("    poetry add mcp pydantic-ai")
    print()

    print("=" * 80)
    print("END OF COMPARISON")
    print("=" * 80)


# =========================================================
# MAIN ENTRY POINT
# =========================================================

if __name__ == "__main__":
    print_comparison_table()
