"""
Exercise 1: Build a LangChain Agent with MCP Calculator
=========================================================
YOUR TASK: Create a LangChain agent that connects to the
test MCP server and uses its calculator tools to solve
a multi-step math problem.

Requirements:
1. Connect to the test_server_for_agents.py MCP server
2. Create LangChain Tool wrappers for the calculator tools
   (add_numbers, subtract_numbers, multiply_numbers, divide_numbers)
3. Create a LangChain ReAct agent with Ollama
4. Ask the agent to solve: "What is (10 + 5) * 3 - 7?"
   The agent should use multiple tool calls to solve this step by step.

Hints:
- Look at example1_langchain_mcp.py for the pattern
- Use StdioServerParameters to connect to the MCP server
- Create a wrapper function for each MCP tool
- Use ChatOllama with model="llama3.2"
- The agent should call tools in sequence: add, multiply, subtract

BEFORE RUNNING:
1. Make sure Ollama is running: ollama serve
2. Pull a model: ollama pull llama3.2
3. Install: poetry add mcp langchain langchain-ollama

HOW TO RUN:
    python exercise1_langchain_agent.py
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
# TODO: Create an async function that connects to the MCP server
# and returns LangChain Tool objects for the calculator tools.
#
# Steps:
#   1. Use StdioServerParameters with the server script path
#   2. Connect with stdio_client
#   3. Create a ClientSession and initialize it
#   4. List the available tools
#   5. For each MCP tool, create a LangChain Tool wrapper
#   6. Return the tools, session, and transport
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create an async function that builds and runs the agent.
#
# Steps:
#   1. Get the path to test_server_for_agents.py
#   2. Call your function above to get the LangChain tools
#   3. Create a ChatOllama LLM
#   4. Create a ReAct prompt template
#   5. Create the agent with create_react_agent()
#   6. Create an AgentExecutor
#   7. Ask: "What is (10 + 5) * 3 - 7? Solve step by step."
#   8. Print the result
#   9. Clean up the MCP connection
# ============================================================

# YOUR CODE HERE


# ============================================================
# Main entry point
# ============================================================
if __name__ == "__main__":
    # TODO: Run your async function with asyncio.run()
    pass
