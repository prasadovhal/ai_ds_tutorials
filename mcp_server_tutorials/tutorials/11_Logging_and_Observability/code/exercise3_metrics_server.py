"""
Exercise 3: Build a Server with a Metrics Dashboard Tool
==========================================================
YOUR TASK:
    Build an MCP server that collects metrics about tool usage
    and exposes a "dashboard" tool that shows all statistics.

Requirements:
    1. Track: total_calls, calls_per_tool, response_times, error_count
    2. Create at least 3 business tools (e.g., add, multiply, reverse_text)
    3. Create a "dashboard" tool that returns all collected metrics
    4. Calculate averages and error rates in the dashboard
    5. Store metrics in a simple dictionary

Hints:
    - Use time.time() before and after each tool call to measure duration
    - Store response times in a list per tool to calculate averages
    - The dashboard tool should format metrics as a readable string
    - Remember: the dashboard tool call itself should also be tracked!

Poetry setup:
    poetry init --name exercise3-metrics-server --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================
# TODO: Step 1 - Create the metrics storage dictionary
# ============================================================

# metrics = {
#     "server_start": ???,
#     "total_calls": 0,
#     "calls_per_tool": {},
#     "response_times": {},
#     "error_count": 0,
# }

# ============================================================
# TODO: Step 2 - Create helper functions to record metrics
# ============================================================

# def record_start(tool_name):
#     """Record a tool call start. Return start_time."""
#     pass

# def record_end(tool_name, start_time, error=False):
#     """Record a tool call end with duration."""
#     pass

# ============================================================
# TODO: Step 3 - Create the MCP server
# ============================================================

# server = FastMCP("metrics-exercise-server")

# ============================================================
# TODO: Step 4 - Create business tools that record metrics
# ============================================================

# @server.tool()
# def add(a: float, b: float) -> str:
#     pass

# @server.tool()
# def multiply(a: float, b: float) -> str:
#     pass

# @server.tool()
# def reverse_text(text: str) -> str:
#     pass

# ============================================================
# TODO: Step 5 - Create the dashboard tool
# ============================================================

# @server.tool()
# def dashboard() -> str:
#     """Show all collected metrics."""
#     pass

# ============================================================
# TODO: Step 6 - Run the server
# ============================================================

if __name__ == "__main__":
    print("Exercise 3: Implement the metrics dashboard server above!")
    print("Then run it with: python exercise3_metrics_server.py")
    # server.run(transport="stdio")
