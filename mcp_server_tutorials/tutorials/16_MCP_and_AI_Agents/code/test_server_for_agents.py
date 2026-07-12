"""
Test MCP Server for AI Agent Integration Examples
==================================================

This server provides simple tools that all agent framework examples
in Chapter 16 will connect to. It has:

1. Calculator tools (add, subtract, multiply, divide)
2. Notes tools (save_note, list_notes, search_notes)
3. Search tool (simulated web search for testing)

WHY this server exists:
- We need ONE consistent server that all agent examples use
- It keeps the examples focused on the AGENT side, not the SERVER side
- The tools are simple enough to test agent behavior clearly

HOW to run:
    python test_server_for_agents.py

The server uses STDIO transport so agent frameworks can start it
as a subprocess and communicate via stdin/stdout.
"""

# =========================================================
# IMPORTS
# =========================================================

# mcp is the Python SDK for building MCP servers
from mcp.server.fastmcp import FastMCP

# json helps us format data nicely
import json

# datetime gives us timestamps for notes
from datetime import datetime


# =========================================================
# CREATE THE MCP SERVER
# =========================================================

# We create a FastMCP server with a descriptive name
# This name shows up when clients connect and list servers
server = FastMCP("test-agent-tools")


# =========================================================
# IN-MEMORY STORAGE FOR NOTES
# =========================================================

# We store notes in a simple list (in-memory, not persistent)
# WHY a list? Because it is the simplest data structure
# In production, you would use a database
notes_storage = []


# =========================================================
# SIMULATED SEARCH DATA
# =========================================================

# We store some fake search results for testing
# WHY fake data? Because we want deterministic tests
# Real search would need API keys or web scraping
search_database = {
    "python": [
        "Python is a high-level programming language created by Guido van Rossum in 1991.",
        "Python is known for its simple syntax and readability.",
        "Python is widely used in data science, web development, and AI.",
    ],
    "mcp": [
        "Model Context Protocol (MCP) is an open standard by Anthropic.",
        "MCP allows AI applications to connect to external data sources and tools.",
        "MCP uses JSON-RPC 2.0 for communication between clients and servers.",
    ],
    "langchain": [
        "LangChain is a framework for building applications with large language models.",
        "LangChain provides tools, memory, and chain abstractions for LLM apps.",
        "LangChain supports multiple LLM providers including Ollama.",
    ],
    "ai agents": [
        "AI agents are autonomous systems that can perceive, decide, and act.",
        "Modern AI agents use LLMs as their reasoning engine.",
        "AI agents can use tools to interact with external systems.",
    ],
    "machine learning": [
        "Machine learning is a subset of AI that learns patterns from data.",
        "Common ML techniques include supervised, unsupervised, and reinforcement learning.",
        "Deep learning uses neural networks with many layers.",
    ],
}


# =========================================================
# CALCULATOR TOOLS
# =========================================================

# Each tool is registered with server.tool()
# We use simple function definitions (no decorators as per course rules)
# Instead, we register them at the bottom of the file

def add_numbers(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: The first number
        b: The second number

    Returns:
        A string with the result of a + b
    """
    # Perform the addition
    result = a + b

    # Return as a formatted string
    # WHY string? Because MCP tool results are always text content
    return f"The result of {a} + {b} = {result}"


def subtract_numbers(a: float, b: float) -> str:
    """Subtract the second number from the first.

    Args:
        a: The first number
        b: The second number to subtract

    Returns:
        A string with the result of a - b
    """
    result = a - b
    return f"The result of {a} - {b} = {result}"


def multiply_numbers(a: float, b: float) -> str:
    """Multiply two numbers together.

    Args:
        a: The first number
        b: The second number

    Returns:
        A string with the result of a * b
    """
    result = a * b
    return f"The result of {a} * {b} = {result}"


def divide_numbers(a: float, b: float) -> str:
    """Divide the first number by the second.

    Args:
        a: The numerator
        b: The denominator (cannot be zero)

    Returns:
        A string with the result of a / b
    """
    # Check for division by zero
    # WHY check? Because dividing by zero crashes the program
    if b == 0:
        return "Error: Cannot divide by zero"

    result = a / b
    return f"The result of {a} / {b} = {result}"


# =========================================================
# NOTES TOOLS
# =========================================================

def save_note(title: str, content: str) -> str:
    """Save a note with a title and content.

    Args:
        title: The title of the note
        content: The body text of the note

    Returns:
        A confirmation message with the note ID
    """
    # Create a note dictionary with metadata
    note = {
        "id": len(notes_storage) + 1,
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat(),
    }

    # Add the note to our in-memory storage
    notes_storage.append(note)

    # Return a confirmation
    return f"Note saved successfully! ID: {note['id']}, Title: '{title}'"


def list_notes() -> str:
    """List all saved notes.

    Returns:
        A JSON string with all saved notes
    """
    # Check if there are any notes
    if len(notes_storage) == 0:
        return "No notes saved yet."

    # Format the notes as a readable string
    result = f"Found {len(notes_storage)} note(s):\n\n"

    for note in notes_storage:
        result = result + f"[{note['id']}] {note['title']}\n"
        result = result + f"    {note['content']}\n"
        result = result + f"    Created: {note['created_at']}\n\n"

    return result


def search_notes(query: str) -> str:
    """Search notes by keyword.

    Args:
        query: The search term to look for in note titles and content

    Returns:
        A string with matching notes
    """
    # Convert query to lowercase for case-insensitive search
    query_lower = query.lower()

    # Find matching notes
    matches = []
    for note in notes_storage:
        # Check if query appears in title or content
        title_match = query_lower in note["title"].lower()
        content_match = query_lower in note["content"].lower()

        if title_match or content_match:
            matches.append(note)

    # Format results
    if len(matches) == 0:
        return f"No notes found matching '{query}'."

    result = f"Found {len(matches)} note(s) matching '{query}':\n\n"
    for note in matches:
        result = result + f"[{note['id']}] {note['title']}\n"
        result = result + f"    {note['content']}\n\n"

    return result


# =========================================================
# SEARCH TOOL
# =========================================================

def search_web(query: str) -> str:
    """Search for information on a topic (simulated for testing).

    Args:
        query: The search query

    Returns:
        A string with search results
    """
    # Convert query to lowercase for matching
    query_lower = query.lower()

    # Look for matching results in our database
    results = []
    for keyword, entries in search_database.items():
        # Check if the keyword appears in the query
        if keyword in query_lower:
            results.extend(entries)

    # If no exact matches, return a generic response
    if len(results) == 0:
        return f"No results found for '{query}'. Try searching for: python, mcp, langchain, ai agents, or machine learning."

    # Format results
    output = f"Search results for '{query}':\n\n"
    for i, result in enumerate(results):
        output = output + f"{i + 1}. {result}\n"

    return output


# =========================================================
# REGISTER ALL TOOLS WITH THE SERVER
# =========================================================

# WHY register separately? Because we want simple function definitions
# without decorators (as per course coding rules)

# Register calculator tools
server.tool()(add_numbers)
server.tool()(subtract_numbers)
server.tool()(multiply_numbers)
server.tool()(divide_numbers)

# Register notes tools
server.tool()(save_note)
server.tool()(list_notes)
server.tool()(search_notes)

# Register search tool
server.tool()(search_web)


# =========================================================
# RUN THE SERVER
# =========================================================

if __name__ == "__main__":
    # Start the server using STDIO transport
    # WHY STDIO? Because agent frameworks start MCP servers as subprocesses
    # and communicate via stdin/stdout pipes
    print("Starting test MCP server for agent examples...", flush=True)
    server.run(transport="stdio")
