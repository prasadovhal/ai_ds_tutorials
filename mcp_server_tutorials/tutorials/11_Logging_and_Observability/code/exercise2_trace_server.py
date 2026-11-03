"""
Exercise 2: Build a Server with UUID Request Tracing
=====================================================
YOUR TASK:
    Build an MCP server that assigns a unique UUID to every
    tool call and includes it in all log messages for that call.

Requirements:
    1. Use uuid.uuid4() to generate unique request IDs
    2. Include the request ID in every log message for a tool call
    3. Create at least 2 tools
    4. Log entry, processing steps, and exit with the request ID
    5. Make it easy to follow one request through the logs

Hints:
    - import uuid
    - request_id = str(uuid.uuid4())[:8]  # Short ID for readability
    - Pass request_id to every log message
    - Consider creating a helper function for traced logging

Poetry setup:
    poetry init --name exercise2-trace-server --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import sys
import uuid

from mcp.server.fastmcp import FastMCP

# ============================================================
# TODO: Step 1 - Set up logging
# ============================================================

# logger = ???

# ============================================================
# TODO: Step 2 - Create a function to generate request IDs
# ============================================================

# def new_request_id():
#     """Generate a short unique request ID."""
#     pass

# ============================================================
# TODO: Step 3 - Create a traced logging helper
# ============================================================

# def traced_log(level, request_id, message):
#     """Log a message with a request ID prefix."""
#     pass

# ============================================================
# TODO: Step 4 - Create the MCP server
# ============================================================

# server = FastMCP("trace-exercise-server")

# ============================================================
# TODO: Step 5 - Create a tool with request tracing
# ============================================================

# @server.tool()
# def process_text(text: str, action: str) -> str:
#     """Process text with tracing."""
#     # Generate request ID
#     # Log entry with ID
#     # Do work
#     # Log exit with ID
#     pass

# ============================================================
# TODO: Step 6 - Create another traced tool
# ============================================================

# @server.tool()
# def calculate(expression: str) -> str:
#     """Parse and calculate a simple expression with tracing."""
#     pass

# ============================================================
# TODO: Step 7 - Run the server
# ============================================================

if __name__ == "__main__":
    print("Exercise 2: Implement UUID request tracing above!")
    print("Then run it with: python exercise2_trace_server.py")
    # server.run(transport="stdio")
