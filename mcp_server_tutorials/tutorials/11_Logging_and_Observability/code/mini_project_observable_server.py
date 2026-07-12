"""
Mini Project: Fully Observable MCP Server
==========================================
This server combines ALL observability features:
    1. Logging to both file and console
    2. Request tracing with unique IDs
    3. Metrics collection (calls, timing, errors)
    4. A "dashboard" tool showing all statistics

This is what a well-instrumented MCP server looks like.
In production, you would replace the in-memory metrics with
Prometheus/Grafana, and the file logging with a log aggregator.

Poetry setup:
    poetry init --name mini-project-observable --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time
import uuid
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================
# PART 1: LOGGING SETUP
# ============================================================

# Create the logger
logger = logging.getLogger("observable_server")
logger.setLevel(logging.DEBUG)

# Log format includes a request_id field
log_format = logging.Formatter(
    "%(asctime)s [%(request_id)s] %(levelname)-8s %(message)s",
    defaults={"request_id": "--------"}
)

# Console handler -- shows INFO and above
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# File handler -- saves DEBUG and above to a log file
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "observable_server.log")

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# ============================================================
# PART 2: REQUEST TRACING
# ============================================================


def new_trace_id():
    """
    Generate a short unique trace ID for a request.
    Example: "a1b2c3d4"
    """
    return str(uuid.uuid4()).replace("-", "")[:8]


def trace_log(level, trace_id, message):
    """
    Log a message with a trace ID attached.
    This makes it easy to follow a single request through the logs.
    """
    numeric_level = getattr(logging, level.upper())
    logger.log(numeric_level, message, extra={"request_id": trace_id})


# ============================================================
# PART 3: METRICS COLLECTION
# ============================================================

# In-memory metrics storage
metrics = {
    "server_start_time": datetime.now().isoformat(),
    "total_calls": 0,
    "calls_per_tool": {},
    "response_times": {},
    "errors_count": 0,
    "errors_per_tool": {},
    "last_call_time": None,
    "active_calls": 0,
}


def metrics_start(tool_name, trace_id):
    """
    Record the start of a tool call in metrics.
    Returns start_time for duration calculation.
    """
    metrics["total_calls"] = metrics["total_calls"] + 1
    metrics["active_calls"] = metrics["active_calls"] + 1
    metrics["last_call_time"] = datetime.now().isoformat()

    if tool_name not in metrics["calls_per_tool"]:
        metrics["calls_per_tool"][tool_name] = 0
    metrics["calls_per_tool"][tool_name] = metrics["calls_per_tool"][tool_name] + 1

    trace_log("DEBUG", trace_id, f"Metrics: call #{metrics['total_calls']} started")

    return time.time()


def metrics_end(tool_name, trace_id, start_time, had_error=False):
    """
    Record the end of a tool call in metrics.
    Stores duration and updates error counters if needed.
    """
    duration_ms = (time.time() - start_time) * 1000
    metrics["active_calls"] = metrics["active_calls"] - 1

    # Store response time
    if tool_name not in metrics["response_times"]:
        metrics["response_times"][tool_name] = []
    metrics["response_times"][tool_name].append(duration_ms)

    # Track errors
    if had_error:
        metrics["errors_count"] = metrics["errors_count"] + 1
        if tool_name not in metrics["errors_per_tool"]:
            metrics["errors_per_tool"][tool_name] = 0
        metrics["errors_per_tool"][tool_name] = metrics["errors_per_tool"][tool_name] + 1

    trace_log("DEBUG", trace_id, f"Metrics: completed in {duration_ms:.2f}ms (error={had_error})")


# ============================================================
# PART 4: CREATE THE MCP SERVER
# ============================================================

server = FastMCP("observable-server")

logger.info("Observable MCP server initialized", extra={"request_id": "startup"})

# ============================================================
# PART 5: BUSINESS TOOLS (with full observability)
# ============================================================


@server.tool()
def calculate(a: float, b: float, operation: str) -> str:
    """Perform a math operation: add, subtract, multiply, divide."""

    # Generate trace ID for this request
    tid = new_trace_id()

    # Log entry
    trace_log("INFO", tid, f"Tool 'calculate' called")
    trace_log("DEBUG", tid, f"Params: a={a}, b={b}, operation='{operation}'")

    # Start metrics tracking
    start_time = metrics_start("calculate", tid)

    # Validate operation
    valid_ops = ["add", "subtract", "multiply", "divide"]
    if operation not in valid_ops:
        trace_log("ERROR", tid, f"Invalid operation: '{operation}'")
        metrics_end("calculate", tid, start_time, had_error=True)
        return f"Error: operation must be one of {valid_ops}"

    # Perform the calculation
    result = 0.0
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            trace_log("ERROR", tid, "Division by zero")
            metrics_end("calculate", tid, start_time, had_error=True)
            return "Error: Cannot divide by zero"
        result = a / b

    # Log exit
    trace_log("INFO", tid, f"Result: {result}")
    metrics_end("calculate", tid, start_time)

    return f"{a} {operation} {b} = {result}"


@server.tool()
def text_analyzer(text: str) -> str:
    """Analyze text and return statistics: word count, char count, etc."""

    tid = new_trace_id()

    trace_log("INFO", tid, "Tool 'text_analyzer' called")
    trace_log("DEBUG", tid, f"Text length: {len(text)} chars")

    start_time = metrics_start("text_analyzer", tid)

    # Analyze the text
    trace_log("DEBUG", tid, "Counting words...")
    words = text.split()
    word_count = len(words)

    trace_log("DEBUG", tid, "Counting characters...")
    char_count = len(text)

    trace_log("DEBUG", tid, "Counting sentences...")
    sentence_count = text.count(".") + text.count("!") + text.count("?")
    if sentence_count == 0:
        sentence_count = 1

    trace_log("DEBUG", tid, "Calculating averages...")
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)

    # Build the result
    result = f"Text Analysis:\n"
    result = result + f"  Words: {word_count}\n"
    result = result + f"  Characters: {char_count}\n"
    result = result + f"  Sentences: {sentence_count}\n"
    result = result + f"  Avg word length: {avg_word_length:.1f}"

    trace_log("INFO", tid, f"Analysis complete: {word_count} words, {char_count} chars")
    metrics_end("text_analyzer", tid, start_time)

    return result


@server.tool()
def string_transform(text: str, transform: str) -> str:
    """Transform text: uppercase, lowercase, title, reverse, strip."""

    tid = new_trace_id()

    trace_log("INFO", tid, "Tool 'string_transform' called")
    trace_log("DEBUG", tid, f"Params: text='{text[:30]}', transform='{transform}'")

    start_time = metrics_start("string_transform", tid)

    valid_transforms = ["uppercase", "lowercase", "title", "reverse", "strip"]
    if transform not in valid_transforms:
        trace_log("ERROR", tid, f"Invalid transform: '{transform}'")
        metrics_end("string_transform", tid, start_time, had_error=True)
        return f"Error: transform must be one of {valid_transforms}"

    # Apply the transformation
    result = ""
    if transform == "uppercase":
        result = text.upper()
    elif transform == "lowercase":
        result = text.lower()
    elif transform == "title":
        result = text.title()
    elif transform == "reverse":
        result = text[::-1]
    elif transform == "strip":
        result = text.strip()

    trace_log("INFO", tid, f"Transform '{transform}' applied successfully")
    metrics_end("string_transform", tid, start_time)

    return result


# ============================================================
# PART 6: DASHBOARD TOOL (shows all observability data)
# ============================================================


@server.tool()
def dashboard() -> str:
    """
    View the full observability dashboard.

    Shows logging info, active traces, and collected metrics
    all in one place.
    """

    tid = new_trace_id()
    trace_log("INFO", tid, "Dashboard requested")
    start_time = metrics_start("dashboard", tid)

    # Build the dashboard
    output = ""
    output = output + "=" * 55 + "\n"
    output = output + "       OBSERVABLE SERVER DASHBOARD\n"
    output = output + "=" * 55 + "\n\n"

    # Section 1: Server Info
    output = output + "--- Server Information ---\n"
    output = output + f"  Started:       {metrics['server_start_time']}\n"
    output = output + f"  Current time:  {datetime.now().isoformat()}\n"
    output = output + f"  Log file:      {log_file_path}\n"
    output = output + f"  Active calls:  {metrics['active_calls']}\n\n"

    # Section 2: Call Statistics
    output = output + "--- Call Statistics ---\n"
    output = output + f"  Total calls:   {metrics['total_calls']}\n"
    output = output + f"  Total errors:  {metrics['errors_count']}\n"
    output = output + f"  Last call:     {metrics['last_call_time']}\n\n"

    # Section 3: Per-Tool Breakdown
    output = output + "--- Per-Tool Breakdown ---\n"
    for tool_name in sorted(metrics["calls_per_tool"].keys()):
        calls = metrics["calls_per_tool"][tool_name]
        errors = metrics["errors_per_tool"].get(tool_name, 0)
        times = metrics["response_times"].get(tool_name, [])

        avg_time = 0.0
        if len(times) > 0:
            avg_time = sum(times) / len(times)

        output = output + f"  {tool_name}:\n"
        output = output + f"    Calls:    {calls}\n"
        output = output + f"    Errors:   {errors}\n"
        output = output + f"    Avg time: {avg_time:.2f}ms\n"
    output = output + "\n"

    # Section 4: Error Rate
    if metrics["total_calls"] > 0:
        error_rate = (metrics["errors_count"] / metrics["total_calls"]) * 100
        output = output + f"Overall error rate: {error_rate:.1f}%\n"
    else:
        output = output + "Overall error rate: N/A\n"

    output = output + "\n" + "=" * 55

    trace_log("INFO", tid, "Dashboard generated successfully")
    metrics_end("dashboard", tid, start_time)

    return output


# ============================================================
# PART 7: RUN THE SERVER
# ============================================================

if __name__ == "__main__":
    logger.info("Starting observable MCP server...", extra={"request_id": "startup"})
    logger.info(f"Log file: {log_file_path}", extra={"request_id": "startup"})
    logger.info("Features: logging, tracing, metrics, dashboard", extra={"request_id": "startup"})
    server.run(transport="stdio")
