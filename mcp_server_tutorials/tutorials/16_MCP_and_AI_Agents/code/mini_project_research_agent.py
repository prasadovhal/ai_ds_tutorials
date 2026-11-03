"""
Mini Project: Research Agent Using MCP
=======================================
This project builds a simple research agent that demonstrates
the core agent pattern WITHOUT requiring any specific framework.

The agent:
1. Searches Wikipedia for information on a topic
2. Takes notes on what it finds
3. Creates a summary of its research

HOW IT WORKS:
- We build a simple MCP server with research tools
- We simulate the agent loop: think -> act -> observe -> repeat
- The "thinking" is done with simple rules (not an LLM)
- This shows the PATTERN that all frameworks implement

WHY no LLM?
- This mini project focuses on the MCP integration pattern
- Using an LLM would require Ollama to be running
- The pattern is the same whether you use an LLM or rules

WHAT YOU LEARN:
- How the agent loop works (think -> act -> observe)
- How MCP tools are called in sequence
- How state (notes) accumulates over the agent's lifetime
- The pattern that LangChain, LangGraph, etc. all implement

How to run:
    python mini_project_research_agent.py
"""

# ============================================================
# Step 1: Import required libraries
# ============================================================
from mcp.server.fastmcp import FastMCP

# asyncio for the MCP client communication
import asyncio

# json for formatting data
import json

# os for file paths
import os

# MCP client imports for connecting to our server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# Step 2: Build the Research MCP Server
# ============================================================
# First, we create a simple MCP server script as a string.
# This server provides research tools: search, take notes, summarize.
# We write it to a temporary file so we can connect to it.

RESEARCH_SERVER_CODE = '''
"""Research Tools MCP Server - provides tools for research tasks."""

from mcp.server.fastmcp import FastMCP
import json

# Create the server
server = FastMCP("research-tools")

# Simulated Wikipedia database
# WHY simulated? So we do not need internet access for the demo
wikipedia_data = {
    "python": {
        "title": "Python (programming language)",
        "summary": "Python is a high-level, general-purpose programming language. "
                   "Its design philosophy emphasizes code readability. "
                   "Python was conceived in the late 1980s by Guido van Rossum. "
                   "Python consistently ranks as one of the most popular programming languages.",
        "sections": ["History", "Design philosophy", "Syntax", "Libraries", "Applications"],
    },
    "machine learning": {
        "title": "Machine Learning",
        "summary": "Machine learning is a subset of artificial intelligence that "
                   "focuses on building systems that learn from data. "
                   "It has applications in image recognition, natural language processing, "
                   "recommendation systems, and autonomous vehicles.",
        "sections": ["Supervised learning", "Unsupervised learning", "Reinforcement learning"],
    },
    "mcp": {
        "title": "Model Context Protocol",
        "summary": "The Model Context Protocol (MCP) is an open standard by Anthropic. "
                   "It provides a unified way for AI applications to connect to external "
                   "data sources and tools. MCP uses JSON-RPC 2.0 for communication.",
        "sections": ["Architecture", "Tools", "Resources", "Prompts", "Transport"],
    },
    "artificial intelligence": {
        "title": "Artificial Intelligence",
        "summary": "Artificial intelligence (AI) is intelligence demonstrated by machines. "
                   "AI research has been defined as the field of study of intelligent agents. "
                   "Modern AI techniques include machine learning, deep learning, and "
                   "natural language processing.",
        "sections": ["History", "Goals", "Approaches", "Applications", "Ethics"],
    },
}

# In-memory storage for research notes
research_notes = []


@server.tool()
def search_wikipedia(topic: str) -> str:
    """Search Wikipedia for information about a topic.

    Args:
        topic: The topic to search for.

    Returns:
        Information about the topic, or a not-found message.
    """
    topic_lower = topic.lower()

    # Search for exact match first
    if topic_lower in wikipedia_data:
        article = wikipedia_data[topic_lower]
        result = f"Wikipedia: {article['title']}\\n"
        result = result + f"\\nSummary: {article['summary']}\\n"
        result = result + f"\\nSections: {', '.join(article['sections'])}"
        return result

    # Search for partial matches
    matches = []
    for key, article in wikipedia_data.items():
        if topic_lower in key or key in topic_lower:
            matches.append(article['title'])

    if len(matches) > 0:
        return f"No exact match for '{topic}'. Did you mean: {', '.join(matches)}?"

    return f"No Wikipedia article found for '{topic}'."


@server.tool()
def take_note(title: str, content: str) -> str:
    """Save a research note.

    Args:
        title: The title of the note.
        content: The content of the note.

    Returns:
        Confirmation message.
    """
    note = {
        "id": len(research_notes) + 1,
        "title": title,
        "content": content,
    }
    research_notes.append(note)
    return f"Note #{note['id']} saved: '{title}'"


@server.tool()
def get_all_notes() -> str:
    """Get all research notes taken so far.

    Returns:
        All notes formatted as text.
    """
    if len(research_notes) == 0:
        return "No notes taken yet."

    lines = []
    lines.append(f"Research Notes ({len(research_notes)} total):")
    lines.append("-" * 40)
    for note in research_notes:
        lines.append(f"[{note['id']}] {note['title']}")
        lines.append(f"    {note['content']}")
        lines.append("")
    return "\\n".join(lines)


@server.tool()
def create_summary() -> str:
    """Create a summary of all research notes.

    Returns:
        A formatted research summary.
    """
    if len(research_notes) == 0:
        return "Cannot create summary: no notes taken yet."

    lines = []
    lines.append("=" * 50)
    lines.append("RESEARCH SUMMARY")
    lines.append("=" * 50)
    lines.append(f"Total notes: {len(research_notes)}")
    lines.append("")

    for note in research_notes:
        lines.append(f"Topic: {note['title']}")
        # Show first 100 chars of content as preview
        preview = note['content']
        if len(preview) > 100:
            preview = preview[:100] + "..."
        lines.append(f"  Finding: {preview}")
        lines.append("")

    lines.append("=" * 50)
    lines.append("End of Research Summary")
    lines.append("=" * 50)
    return "\\n".join(lines)


if __name__ == "__main__":
    server.run(transport="stdio")
'''


# ============================================================
# Step 3: The Agent Loop
# ============================================================
# This is the heart of ANY agent system. The loop is:
#
#   1. THINK: Decide what to do next
#   2. ACT:   Call a tool
#   3. OBSERVE: Look at the result
#   4. REPEAT: Go back to step 1
#
# In real frameworks (LangChain, etc.), the LLM does the thinking.
# Here we use simple rules to demonstrate the pattern.

async def run_research_agent(topics):
    """
    Run a simple research agent that:
    1. Searches Wikipedia for each topic
    2. Takes notes on findings
    3. Creates a final summary

    Args:
        topics: A list of topics to research
    """

    # Write the server code to a temporary file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_file = os.path.join(current_dir, "_temp_research_server.py")

    file_handle = open(server_file, "w", encoding="utf-8")
    file_handle.write(RESEARCH_SERVER_CODE)
    file_handle.close()

    print("=" * 60)
    print("RESEARCH AGENT - Mini Project")
    print("=" * 60)
    print(f"\nResearch topics: {topics}")
    print(f"Server script: {server_file}")

    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=[server_file],
    )

    stdio_transport = stdio_client(server_params)
    read_stream, write_stream = await stdio_transport.__aenter__()

    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    # List available tools
    tools_response = await session.list_tools()
    print(f"\nAvailable tools: {len(tools_response.tools)}")
    for tool in tools_response.tools:
        print(f"  - {tool.name}: {tool.description}")

    # ========================================
    # THE AGENT LOOP
    # ========================================
    # This simulates what an LLM-powered agent does.
    # The agent has a plan and executes it step by step.

    print("\n" + "=" * 60)
    print("AGENT LOOP STARTING")
    print("=" * 60)

    step_number = 0

    # Phase 1: Research each topic
    for topic in topics:
        step_number = step_number + 1
        print(f"\n--- Step {step_number}: THINK ---")
        print(f"Agent thinks: 'I should search for information about {topic}'")

        # ACT: Call the search tool
        print(f"\n--- Step {step_number}: ACT ---")
        print(f"Agent calls: search_wikipedia(topic='{topic}')")

        result = await session.call_tool(
            "search_wikipedia",
            arguments={"topic": topic}
        )

        # OBSERVE: Look at the result
        search_text = ""
        for content in result.content:
            if hasattr(content, "text"):
                search_text = search_text + content.text

        print(f"\n--- Step {step_number}: OBSERVE ---")
        print(f"Search result:\n{search_text}")

        # Phase 2: Take a note on what we found
        step_number = step_number + 1
        print(f"\n--- Step {step_number}: THINK ---")
        print(f"Agent thinks: 'I found information. I should save a note.'")

        print(f"\n--- Step {step_number}: ACT ---")
        print(f"Agent calls: take_note(title='{topic}', content='...')")

        note_result = await session.call_tool(
            "take_note",
            arguments={
                "title": f"Research: {topic}",
                "content": search_text,
            }
        )

        note_text = ""
        for content in note_result.content:
            if hasattr(content, "text"):
                note_text = note_text + content.text

        print(f"\n--- Step {step_number}: OBSERVE ---")
        print(f"Note result: {note_text}")

    # Phase 3: Review all notes
    step_number = step_number + 1
    print(f"\n--- Step {step_number}: THINK ---")
    print("Agent thinks: 'I have researched all topics. Let me review my notes.'")

    print(f"\n--- Step {step_number}: ACT ---")
    print("Agent calls: get_all_notes()")

    notes_result = await session.call_tool("get_all_notes", arguments={})

    notes_text = ""
    for content in notes_result.content:
        if hasattr(content, "text"):
            notes_text = notes_text + content.text

    print(f"\n--- Step {step_number}: OBSERVE ---")
    print(f"All notes:\n{notes_text}")

    # Phase 4: Create summary
    step_number = step_number + 1
    print(f"\n--- Step {step_number}: THINK ---")
    print("Agent thinks: 'Now I should create a final summary.'")

    print(f"\n--- Step {step_number}: ACT ---")
    print("Agent calls: create_summary()")

    summary_result = await session.call_tool("create_summary", arguments={})

    summary_text = ""
    for content in summary_result.content:
        if hasattr(content, "text"):
            summary_text = summary_text + content.text

    print(f"\n--- Step {step_number}: OBSERVE ---")
    print(f"\n{summary_text}")

    # Agent is done
    print("\n" + "=" * 60)
    print("AGENT LOOP COMPLETED")
    print(f"Total steps: {step_number}")
    print("=" * 60)

    # Clean up
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

    # Remove the temporary server file
    try:
        os.remove(server_file)
        print(f"\nCleaned up temporary server file.")
    except Exception:
        pass

    print("\nKEY INSIGHT:")
    print("  This agent followed the SAME pattern as LangChain, LangGraph, etc.:")
    print("  THINK -> ACT -> OBSERVE -> REPEAT")
    print("  The only difference is that real frameworks use an LLM for THINKING.")
    print("  The MCP tools (ACT) and results (OBSERVE) work exactly the same way.")


# ============================================================
# Step 4: Run the agent
# ============================================================

if __name__ == "__main__":
    # Define the research topics
    research_topics = ["python", "machine learning", "mcp"]

    # Run the research agent
    asyncio.run(run_research_agent(research_topics))
