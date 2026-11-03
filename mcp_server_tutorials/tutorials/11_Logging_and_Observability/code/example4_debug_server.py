"""
Example 4: MCP Server with Verbose DEBUG Logging
=================================================
This example shows how to create an MCP server that logs
EVERYTHING at the DEBUG level for maximum visibility.

When debugging a problem, you want to see:
- Every tool call entry and exit
- All parameter values received
- Execution time for every operation
- Any intermediate steps

This is like turning on "verbose mode" -- you see everything
the server is doing, which helps you find bugs quickly.

WARNING: Debug logging produces A LOT of output.
Only use this level during development or troubleshooting.
In production, use INFO or WARNING level instead.

Poetry setup:
    poetry init --name example4-debug-server --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Set up verbose DEBUG logging
# ============================================================

# Create a logger specifically for our debug server
logger = logging.getLogger("mcp_debug")

# Set the logger level to DEBUG -- this captures EVERYTHING
logger.setLevel(logging.DEBUG)

# Create a detailed format that shows file, function, and line number
# This extra detail helps you find EXACTLY where each log came from
debug_format = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(funcName)-20s | Line %(lineno)-4d | %(message)s"
)

# Console handler -- show DEBUG and above on the console
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(debug_format)
logger.addHandler(console_handler)

# File handler -- save all debug logs to a file for later review
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "mcp_debug.log")

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(debug_format)
logger.addHandler(file_handler)

# ============================================================
# STEP 2: Create the MCP server
# ============================================================

server = FastMCP("debug-server")

logger.debug("FastMCP server instance created")
logger.debug(f"Server name: debug-server")
logger.debug(f"Log file location: {log_file_path}")

# ============================================================
# STEP 3: Create a helper to log tool entry and exit
# ============================================================

# We use a simple counter to track how many calls we have seen
call_counter = 0


def log_tool_entry(tool_name, **kwargs):
    """
    Log when a tool is entered (called).
    Records the tool name, all parameters, and a call number.
    Returns a dict with start_time and call_number for use at exit.
    """
    global call_counter
    call_counter = call_counter + 1

    # Log the entry with a clear marker
    logger.debug(f"{'=' * 50}")
    logger.debug(f"ENTERING tool: '{tool_name}' (call #{call_counter})")

    # Log each parameter individually so they are easy to read
    for param_name, param_value in kwargs.items():
        logger.debug(f"  Param '{param_name}' = {repr(param_value)} (type: {type(param_value).__name__})")

    logger.debug(f"Entry timestamp: {datetime.now().isoformat()}")

    # Return context for the exit log
    return {"start_time": time.time(), "call_number": call_counter}


def log_tool_exit(tool_name, context, result=None, error=None):
    """
    Log when a tool exits (finishes).
    Records the result, execution time, and whether it succeeded.
    """
    # Calculate how long the tool took to run
    duration_ms = (time.time() - context["start_time"]) * 1000

    if error:
        # Log the error at ERROR level
        logger.error(f"EXITING tool: '{tool_name}' (call #{context['call_number']}) -- FAILED")
        logger.error(f"  Error: {error}")
    else:
        # Log successful exit at DEBUG level
        logger.debug(f"EXITING tool: '{tool_name}' (call #{context['call_number']}) -- SUCCESS")
        logger.debug(f"  Result: {repr(result)}")

    # Always log the duration
    logger.debug(f"  Duration: {duration_ms:.4f} ms")
    logger.debug(f"Exit timestamp: {datetime.now().isoformat()}")
    logger.debug(f"{'=' * 50}")


# ============================================================
# STEP 4: Define tools with verbose debug logging
# ============================================================


@server.tool()
def string_transform(text: str, operation: str) -> str:
    """Transform a string: uppercase, lowercase, reverse, or title."""

    # Log entry with all parameters
    ctx = log_tool_entry("string_transform", text=text, operation=operation)

    # Validate the operation
    valid_ops = ["uppercase", "lowercase", "reverse", "title"]
    logger.debug(f"Validating operation '{operation}' against {valid_ops}")

    if operation not in valid_ops:
        error_msg = f"Invalid operation: '{operation}'. Must be one of {valid_ops}"
        log_tool_exit("string_transform", ctx, error=error_msg)
        return f"Error: {error_msg}"

    logger.debug(f"Operation '{operation}' is valid, proceeding...")

    # Perform the transformation
    result = ""
    if operation == "uppercase":
        logger.debug("Converting text to uppercase...")
        result = text.upper()
    elif operation == "lowercase":
        logger.debug("Converting text to lowercase...")
        result = text.lower()
    elif operation == "reverse":
        logger.debug("Reversing text...")
        result = text[::-1]
    elif operation == "title":
        logger.debug("Converting text to title case...")
        result = text.title()

    logger.debug(f"Transformation complete: '{text}' -> '{result}'")

    # Log exit with result
    log_tool_exit("string_transform", ctx, result=result)

    return f"Result: {result}"


@server.tool()
def math_operation(a: float, b: float, op: str) -> str:
    """Perform math: add, subtract, multiply, divide, power."""

    # Log entry with all parameters
    ctx = log_tool_entry("math_operation", a=a, b=b, op=op)

    # Validate the operation
    valid_ops = ["add", "subtract", "multiply", "divide", "power"]
    logger.debug(f"Checking if '{op}' is in {valid_ops}")

    if op not in valid_ops:
        error_msg = f"Unknown operation: '{op}'"
        log_tool_exit("math_operation", ctx, error=error_msg)
        return f"Error: {error_msg}"

    # Perform the operation with debug logging for each step
    result = 0.0

    if op == "add":
        logger.debug(f"Computing {a} + {b}")
        result = a + b
    elif op == "subtract":
        logger.debug(f"Computing {a} - {b}")
        result = a - b
    elif op == "multiply":
        logger.debug(f"Computing {a} * {b}")
        result = a * b
    elif op == "divide":
        if b == 0:
            error_msg = "Division by zero"
            logger.debug(f"Divisor is zero, cannot divide")
            log_tool_exit("math_operation", ctx, error=error_msg)
            return f"Error: {error_msg}"
        logger.debug(f"Computing {a} / {b}")
        result = a / b
    elif op == "power":
        logger.debug(f"Computing {a} ** {b}")
        result = a ** b

    logger.debug(f"Computation result: {result}")

    # Log exit
    log_tool_exit("math_operation", ctx, result=result)

    return f"{a} {op} {b} = {result}"


@server.tool()
def list_operations(items: str, action: str) -> str:
    """Work with comma-separated lists: sort, reverse, unique, count."""

    # Log entry
    ctx = log_tool_entry("list_operations", items=items, action=action)

    # Parse the comma-separated string into a list
    logger.debug(f"Splitting input string by commas...")
    item_list = [item.strip() for item in items.split(",")]
    logger.debug(f"Parsed {len(item_list)} items: {item_list}")

    # Validate action
    valid_actions = ["sort", "reverse", "unique", "count"]
    if action not in valid_actions:
        error_msg = f"Unknown action: '{action}'"
        log_tool_exit("list_operations", ctx, error=error_msg)
        return f"Error: {error_msg}"

    # Perform the action
    result = ""
    if action == "sort":
        logger.debug(f"Sorting {len(item_list)} items alphabetically...")
        sorted_list = sorted(item_list)
        result = ", ".join(sorted_list)
        logger.debug(f"Sorted result: {sorted_list}")
    elif action == "reverse":
        logger.debug(f"Reversing list order...")
        reversed_list = list(reversed(item_list))
        result = ", ".join(reversed_list)
        logger.debug(f"Reversed result: {reversed_list}")
    elif action == "unique":
        logger.debug(f"Finding unique items...")
        # Use dict.fromkeys to preserve order while removing duplicates
        unique_list = list(dict.fromkeys(item_list))
        result = ", ".join(unique_list)
        logger.debug(f"Unique items ({len(unique_list)}): {unique_list}")
    elif action == "count":
        logger.debug(f"Counting items...")
        result = f"The list contains {len(item_list)} items"

    # Log exit
    log_tool_exit("list_operations", ctx, result=result)

    return f"Result: {result}"


# ============================================================
# STEP 5: Run the server
# ============================================================

if __name__ == "__main__":
    logger.debug("=" * 60)
    logger.debug("MCP DEBUG SERVER STARTING")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Log file: {log_file_path}")
    logger.debug(f"Debug level: {logger.level} (10=DEBUG)")
    logger.debug("=" * 60)

    logger.info("Starting debug MCP server on stdio transport...")
    server.run(transport="stdio")
