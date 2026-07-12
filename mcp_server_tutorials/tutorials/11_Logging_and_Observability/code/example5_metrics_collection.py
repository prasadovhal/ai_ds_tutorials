"""
Example 5: MCP Server with Metrics Collection
==============================================
This example shows how to collect and track metrics about
your MCP server's performance and usage.

Metrics tell you:
- How many times each tool has been called (usage patterns)
- How long each tool takes on average (performance)
- How many errors have occurred (reliability)
- Overall server health (uptime, total calls)

We store metrics in a simple Python dictionary.
In production, you would use Prometheus, StatsD, or Datadog.

Poetry setup:
    poetry init --name example5-metrics --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import sys
import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Set up basic logging
# ============================================================

logger = logging.getLogger("mcp_metrics")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# ============================================================
# STEP 2: Create the metrics storage
# ============================================================

# This dictionary holds ALL our metrics
# In a real application, you might use a time-series database
metrics = {
    # When the server started
    "server_start_time": datetime.now().isoformat(),

    # Total number of tool calls across all tools
    "total_calls": 0,

    # Number of calls per tool -- we add entries as tools are called
    # Example: {"add": 5, "multiply": 3}
    "calls_per_tool": {},

    # Total response times per tool -- used to calculate averages
    # Example: {"add": [12.3, 15.1, 10.8]}
    "response_times_per_tool": {},

    # Total number of errors
    "errors_count": 0,

    # Errors broken down by tool
    # Example: {"divide": 2}
    "errors_per_tool": {},

    # The last time any tool was called
    "last_call_time": None,
}


# ============================================================
# STEP 3: Create helper functions to update metrics
# ============================================================


def record_call_start(tool_name):
    """
    Record that a tool call has started.
    Updates total_calls and calls_per_tool counters.
    Returns the start time for duration measurement.
    """
    # Increment total calls
    metrics["total_calls"] = metrics["total_calls"] + 1

    # Increment per-tool counter
    if tool_name not in metrics["calls_per_tool"]:
        metrics["calls_per_tool"][tool_name] = 0
    metrics["calls_per_tool"][tool_name] = metrics["calls_per_tool"][tool_name] + 1

    # Update last call time
    metrics["last_call_time"] = datetime.now().isoformat()

    logger.info(f"[Metrics] Call #{metrics['total_calls']} to tool '{tool_name}'")

    # Return start time for measuring duration
    return time.time()


def record_call_end(tool_name, start_time, had_error=False):
    """
    Record that a tool call has finished.
    Updates response times and error counters.
    """
    # Calculate duration in milliseconds
    duration_ms = (time.time() - start_time) * 1000

    # Store the response time
    if tool_name not in metrics["response_times_per_tool"]:
        metrics["response_times_per_tool"][tool_name] = []
    metrics["response_times_per_tool"][tool_name].append(duration_ms)

    # If there was an error, update error counters
    if had_error:
        metrics["errors_count"] = metrics["errors_count"] + 1
        if tool_name not in metrics["errors_per_tool"]:
            metrics["errors_per_tool"][tool_name] = 0
        metrics["errors_per_tool"][tool_name] = metrics["errors_per_tool"][tool_name] + 1

    logger.info(f"[Metrics] Tool '{tool_name}' completed in {duration_ms:.2f}ms (error={had_error})")


def get_average_response_time(tool_name):
    """
    Calculate the average response time for a specific tool.
    Returns 0.0 if no calls have been recorded yet.
    """
    times = metrics["response_times_per_tool"].get(tool_name, [])
    if len(times) == 0:
        return 0.0

    total = sum(times)
    average = total / len(times)
    return round(average, 2)


# ============================================================
# STEP 4: Create the MCP server
# ============================================================

server = FastMCP("metrics-server")

logger.info("Metrics collection server initialized")

# ============================================================
# STEP 5: Define business tools (the actual work tools)
# ============================================================


@server.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together."""

    # Record that this call started
    start_time = record_call_start("add")

    # Do the work
    result = a + b

    # Record that this call ended successfully
    record_call_end("add", start_time, had_error=False)

    return f"{a} + {b} = {result}"


@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together."""

    start_time = record_call_start("multiply")

    result = a * b

    record_call_end("multiply", start_time, had_error=False)

    return f"{a} * {b} = {result}"


@server.tool()
def divide(a: float, b: float) -> str:
    """Divide the first number by the second."""

    start_time = record_call_start("divide")

    # Check for division by zero
    if b == 0:
        # Record the error
        record_call_end("divide", start_time, had_error=True)
        return "Error: Cannot divide by zero"

    result = a / b

    record_call_end("divide", start_time, had_error=False)

    return f"{a} / {b} = {result}"


@server.tool()
def uppercase(text: str) -> str:
    """Convert text to uppercase."""

    start_time = record_call_start("uppercase")

    result = text.upper()

    record_call_end("uppercase", start_time, had_error=False)

    return result


# ============================================================
# STEP 6: Define the metrics tool (view server stats)
# ============================================================


@server.tool()
def get_metrics() -> str:
    """
    View server metrics and statistics.

    Returns a dashboard showing:
    - Total calls made
    - Calls per tool
    - Average response time per tool
    - Error counts
    - Server uptime
    """

    # Record this call too (even viewing metrics is a tool call)
    start_time = record_call_start("get_metrics")

    # Build the metrics dashboard as a formatted string
    dashboard = "===== SERVER METRICS DASHBOARD =====\n\n"

    # Section 1: Overview
    dashboard = dashboard + f"Server started: {metrics['server_start_time']}\n"
    dashboard = dashboard + f"Last call:      {metrics['last_call_time']}\n"
    dashboard = dashboard + f"Total calls:    {metrics['total_calls']}\n"
    dashboard = dashboard + f"Total errors:   {metrics['errors_count']}\n\n"

    # Section 2: Calls per tool
    dashboard = dashboard + "--- Calls Per Tool ---\n"
    for tool_name, count in metrics["calls_per_tool"].items():
        dashboard = dashboard + f"  {tool_name}: {count} calls\n"
    dashboard = dashboard + "\n"

    # Section 3: Average response times
    dashboard = dashboard + "--- Average Response Times ---\n"
    for tool_name in metrics["response_times_per_tool"]:
        avg_time = get_average_response_time(tool_name)
        dashboard = dashboard + f"  {tool_name}: {avg_time} ms\n"
    dashboard = dashboard + "\n"

    # Section 4: Errors per tool
    dashboard = dashboard + "--- Errors Per Tool ---\n"
    if len(metrics["errors_per_tool"]) == 0:
        dashboard = dashboard + "  No errors recorded!\n"
    else:
        for tool_name, count in metrics["errors_per_tool"].items():
            dashboard = dashboard + f"  {tool_name}: {count} errors\n"
    dashboard = dashboard + "\n"

    # Section 5: Error rate
    if metrics["total_calls"] > 0:
        error_rate = (metrics["errors_count"] / metrics["total_calls"]) * 100
        dashboard = dashboard + f"Error rate: {error_rate:.1f}%\n"
    else:
        dashboard = dashboard + "Error rate: N/A (no calls yet)\n"

    dashboard = dashboard + "\n===== END OF DASHBOARD ====="

    # Record this call's completion
    record_call_end("get_metrics", start_time, had_error=False)

    return dashboard


# ============================================================
# STEP 7: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info("Starting metrics collection MCP server...")
    logger.info("Use the 'get_metrics' tool to view collected metrics")
    server.run(transport="stdio")
