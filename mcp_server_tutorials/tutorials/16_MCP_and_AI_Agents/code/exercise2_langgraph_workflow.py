"""
Exercise 2: Build a LangGraph Workflow with MCP Tools
=======================================================
YOUR TASK: Create a LangGraph workflow that uses MCP tools
to perform a research-and-save workflow:

1. Search for information about a topic using search_web
2. Save the results as a note using save_note
3. List all notes to confirm the save

Requirements:
1. Connect to test_server_for_agents.py
2. Create LangChain tool wrappers for search_web, save_note, list_notes
3. Build a LangGraph StateGraph with:
   - An "agent" node (uses the LLM to decide actions)
   - A "tools" node (executes tool calls)
   - Conditional routing between them
4. Run the workflow with a research task

Hints:
- Look at example2_langgraph_mcp.py for the pattern
- Use StateGraph with MessagesState
- Use ToolNode from langgraph.prebuilt
- The routing function checks if the last message has tool_calls

BEFORE RUNNING:
    1. ollama serve
    2. ollama pull llama3.2
    3. poetry add mcp langchain langchain-ollama langgraph

HOW TO RUN:
    python exercise2_langgraph_workflow.py
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
# TODO: Create a function to connect to MCP and create
# LangChain tool wrappers for search_web, save_note, list_notes.
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a function that builds the LangGraph state graph.
#
# The graph should have:
#   - An "agent" node that calls the LLM
#   - A "tools" node that executes tool calls (use ToolNode)
#   - A conditional edge from agent -> tools or agent -> END
#   - An edge from tools -> agent (loop back)
#
# Hint: Use should_continue() to check for tool_calls
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create an async function to run the workflow.
#
# Steps:
#   1. Connect to MCP server
#   2. Create tools
#   3. Build the graph
#   4. Run with message: "Search for Python, save results as a note,
#      then list all notes"
#   5. Print the conversation
#   6. Clean up
# ============================================================

# YOUR CODE HERE


# ============================================================
# Main entry point
# ============================================================
if __name__ == "__main__":
    # TODO: Run your async function with asyncio.run()
    pass
