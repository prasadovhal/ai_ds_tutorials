"""
Exercise 1: Build a Server with File and Console Logging
=========================================================
YOUR TASK:
    Build an MCP server that logs to BOTH a file AND the console.

Requirements:
    1. Create a logger named "exercise_server"
    2. Set up a console handler at INFO level
    3. Set up a file handler at DEBUG level (file: "exercise1.log")
    4. Create at least 2 tools that log their activity
    5. Log tool entry, parameters, result, and errors

Hints:
    - Use logging.getLogger() to create a named logger
    - Use logging.StreamHandler() for console output
    - Use logging.FileHandler() for file output
    - Use logging.Formatter() to define the log format
    - Remember to add handlers to the logger with addHandler()

Poetry setup:
    poetry init --name exercise1-logged-server --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys

from mcp.server.fastmcp import FastMCP

# ============================================================
# TODO: Step 1 - Create a logger named "exercise_server"
# ============================================================

# logger = ???

# ============================================================
# TODO: Step 2 - Create a log format
# ============================================================

# log_format = ???

# ============================================================
# TODO: Step 3 - Create a console handler (INFO level)
# ============================================================

# console_handler = ???

# ============================================================
# TODO: Step 4 - Create a file handler (DEBUG level)
# ============================================================

# log_file_path = ???
# file_handler = ???

# ============================================================
# TODO: Step 5 - Create the MCP server
# ============================================================

# server = FastMCP("exercise1-server")

# ============================================================
# TODO: Step 6 - Create a tool that logs its activity
# ============================================================

# @server.tool()
# def greet(name: str) -> str:
#     """Greet someone by name."""
#     # Log the call
#     # Do the work
#     # Log the result
#     pass

# ============================================================
# TODO: Step 7 - Create another tool with error logging
# ============================================================

# @server.tool()
# def divide(a: float, b: float) -> str:
#     """Divide two numbers."""
#     # Log the call
#     # Check for errors
#     # Log errors if they happen
#     # Do the work
#     # Log the result
#     pass

# ============================================================
# TODO: Step 8 - Run the server
# ============================================================

if __name__ == "__main__":
    print("Exercise 1: Implement the logged server above!")
    print("Then run it with: python exercise1_logged_server.py")
    # server.run(transport="stdio")
