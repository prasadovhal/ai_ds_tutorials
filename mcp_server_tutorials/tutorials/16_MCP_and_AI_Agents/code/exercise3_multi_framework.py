"""
Exercise 3: Same MCP Server, Multiple Frameworks
==================================================
YOUR TASK: Demonstrate that the SAME MCP server can be used
by different AI agent frameworks.

Create a script that:
1. Defines a simple MCP server with 2 tools (inline or use test server)
2. Shows how to call those tools from LangChain
3. Shows how to call those tools from LlamaIndex
4. Compares the results

This proves the key benefit of MCP: WRITE ONCE, USE EVERYWHERE.
The server does not change -- only the client/framework wrapper changes.

Requirements:
1. Connect to test_server_for_agents.py from both frameworks
2. Use the add_numbers tool from both LangChain and LlamaIndex
3. Both should produce the same result
4. Print a comparison showing both results

Hints:
- You can reuse the MCP connection patterns from examples 1 and 3
- Connect to the server twice (once per framework)
- Call the same tool (add_numbers with a=100, b=200)
- Compare the results

BEFORE RUNNING:
    1. ollama serve
    2. ollama pull llama3.2
    3. poetry add mcp langchain langchain-ollama llama-index llama-index-llms-ollama

HOW TO RUN:
    python exercise3_multi_framework.py
"""

import asyncio
import os
import json

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# TODO: Create a function to call an MCP tool directly
# (without any framework) and return the result.
# This will be our "baseline" to compare against.
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a function that wraps the MCP tool as a
# LangChain Tool and calls it.
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a function that wraps the MCP tool as a
# LlamaIndex FunctionTool and calls it.
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a main async function that:
# 1. Calls add_numbers(100, 200) directly via MCP
# 2. Calls add_numbers(100, 200) via LangChain wrapper
# 3. Calls add_numbers(100, 200) via LlamaIndex wrapper
# 4. Prints a comparison table showing all three results
# ============================================================

# YOUR CODE HERE


# ============================================================
# Main entry point
# ============================================================
if __name__ == "__main__":
    # TODO: Run your async function with asyncio.run()
    pass
