"""
Exercise 3 SOLUTION: Server with Metrics Dashboard Tool
=========================================================
This solution creates an MCP server that tracks all tool calls
and provides a dashboard tool to view the collected statistics.

Poetry setup:
    poetry init --name exercise3-solution --python "^3.11" --no-interaction
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
# Step 1: Set up basic logging
# ============================================================

logger = logging.getLogger("metrics_exercise")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# ============================================================
# Step 2: Create the metrics storage dictionary
# ============================================================

metrics = {
    # When the server started
    "server_start": datetime.now().isoformat(),

    # Total tool calls
    "total_calls": 0,

    # Calls broken down by tool name
    "calls_per_tool": {},

    # Response times in ms, stored per tool
    "response_times": {},

    # Total error count
    "error_count": 0,

    # Errors per tool
    "errors_per_tool": {},
}

# ============================================================
# Step 3: Create helper functions to record metrics
# ============================================================


def record_start(tool_name):
    """
    Record that a tool call started.
    Increments counters and returns the start time.
    """
    # Increment total calls
    metrics["total_calls"] = metrics["total_calls"] + 1

    # Increment per-tool calls
    if tool_name not in metrics["calls_per_tool"]:
        metrics["calls_per_tool"][tool_name] = 0
    metrics["calls_per_tool"][tool_name] = metrics["calls_per_tool"][tool_name] + 1

    logger.info(f"[Metrics] Tool '{tool_name}' called (total: {metrics['total_calls']})")

    return time.time()


def record_end(tool_name, start_time, error=False):
    """
    Record that a tool call ended.
    Stores duration and optionally increments error counters.
    """
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Store response time
    if tool_name not in metrics["response_times"]:
        metrics["response_times"][tool_name] = []
    metrics["response_times"][tool_name].append(duration_ms)

    # Track errors
    if error:
        metrics["error_count"] = metrics["error_count"] + 1
        if tool_name not in metrics["errors_per_tool"]:
            metrics["errors_per_tool"][tool_name] = 0
        metrics["errors_per_tool"][tool_name] = metrics["errors_per_tool"][tool_name] + 1

    logger.info(f"[Metrics] Tool '{tool_name}' finished in {duration_ms:.2f}ms (error={error})")


# ============================================================
# Step 4: Create the MCP server
# ============================================================

server = FastMCP("metrics-exercise-server")

logger.info("Metrics exercise server initialized")

# ============================================================
# Step 5: Create business tools that record metrics
# ============================================================


@server.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together."""

    start_time = record_start("add")
    result = a + b
    record_end("add", start_time)

    return f"{a} + {b} = {result}"


@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together."""

    start_time = record_start("multiply")
    result = a * b
    record_end("multiply", start_time)

    return f"{a} * {b} = {result}"


@server.tool()
def reverse_text(text: str) -> str:
    """Reverse the given text string."""

    start_time = record_start("reverse_text")
    result = text[::-1]
    record_end("reverse_text", start_time)

    return f"Reversed: {result}"


@server.tool()
def safe_divide(a: float, b: float) -> str:
    """Divide a by b with error handling."""

    start_time = record_start("safe_divide")

    if b == 0:
        record_end("safe_divide", start_time, error=True)
        return "Error: Cannot divide by zero"

    result = a / b
    record_end("safe_divide", start_time)

    return f"{a} / {b} = {result}"


# ============================================================
# Step 6: Create the dashboard tool
# ============================================================


@server.tool()
def dashboard() -> str:
    """
    Show all collected server metrics in a readable format.
    Displays call counts, average response times, and error rates.
    """

    start_time = record_start("dashboard")

    # Build the dashboard output
    output = "========== METRICS DASHBOARD ==========\n\n"

    # Server info
    output = output + f"Server started:  {metrics['server_start']}\n"
    output = output + f"Current time:    {datetime.now().isoformat()}\n"
    output = output + f"Total calls:     {metrics['total_calls']}\n"
    output = output + f"Total errors:    {metrics['error_count']}\n\n"

    # Per-tool call counts
    output = output + "--- Calls Per Tool ---\n"
    for name, count in sorted(metrics["calls_per_tool"].items()):
        output = output + f"  {name}: {count}\n"
    output = output + "\n"

    # Average response times
    output = output + "--- Avg Response Time (ms) ---\n"
    for name, times in sorted(metrics["response_times"].items()):
        if len(times) > 0:
            avg = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            output = output + f"  {name}: avg={avg:.2f}, min={min_time:.2f}, max={max_time:.2f}\n"
    output = output + "\n"

    # Error breakdown
    output = output + "--- Errors Per Tool ---\n"
    if len(metrics["errors_per_tool"]) == 0:
        output = output + "  No errors recorded.\n"
    else:
        for name, count in sorted(metrics["errors_per_tool"].items()):
            output = output + f"  {name}: {count}\n"
    output = output + "\n"

    # Error rate
    if metrics["total_calls"] > 0:
        rate = (metrics["error_count"] / metrics["total_calls"]) * 100
        output = output + f"Overall error rate: {rate:.1f}%\n"

    output = output + "\n========================================"

    record_end("dashboard", start_time)

    return output


# ============================================================
# Step 7: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info("Starting metrics exercise server...")
    logger.info("Use the 'dashboard' tool to view metrics")
    server.run(transport="stdio")
