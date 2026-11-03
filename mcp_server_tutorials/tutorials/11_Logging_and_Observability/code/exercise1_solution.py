"""
Exercise 1 SOLUTION: Server with File and Console Logging
==========================================================
This solution creates an MCP server that logs to both
a file and the console with different log levels.

Poetry setup:
    poetry init --name exercise1-solution --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Create a logger named "exercise_server"
# ============================================================

logger = logging.getLogger("exercise_server")
logger.setLevel(logging.DEBUG)

# ============================================================
# Step 2: Create a log format
# ============================================================

log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"
)

# ============================================================
# Step 3: Create a console handler (INFO level)
# ============================================================

# Console handler shows INFO and above
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# ============================================================
# Step 4: Create a file handler (DEBUG level)
# ============================================================

# File handler saves DEBUG and above to a file
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "exercise1.log")

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# ============================================================
# Step 5: Create the MCP server
# ============================================================

server = FastMCP("exercise1-server")

logger.info("Exercise 1 server initialized")
logger.debug(f"Log file: {log_file_path}")

# ============================================================
# Step 6: Create a tool that logs its activity
# ============================================================


@server.tool()
def greet(name: str) -> str:
    """Greet someone by name."""

    # Log the incoming call
    logger.info(f"Tool 'greet' called with name='{name}'")
    logger.debug(f"Name length: {len(name)} characters")

    start_time = time.time()

    # Do the work
    greeting = f"Hello, {name}! Welcome to the MCP server."

    # Log the result
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool 'greet' completed in {duration_ms:.2f}ms")
    logger.debug(f"Greeting result: {greeting}")

    return greeting


# ============================================================
# Step 7: Create another tool with error logging
# ============================================================


@server.tool()
def divide(a: float, b: float) -> str:
    """Divide the first number by the second number."""

    # Log the incoming call
    logger.info(f"Tool 'divide' called with a={a}, b={b}")

    start_time = time.time()

    # Check for errors
    if b == 0:
        logger.error(f"Division by zero attempted: {a} / {b}")
        return "Error: Cannot divide by zero"

    # Do the work
    result = a / b

    # Log the result
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool 'divide' completed: {a} / {b} = {result}")
    logger.debug(f"Duration: {duration_ms:.2f}ms")

    return f"{a} / {b} = {result}"


@server.tool()
def word_count(text: str) -> str:
    """Count words in the given text."""

    logger.info(f"Tool 'word_count' called with text of length {len(text)}")
    logger.debug(f"Text preview: '{text[:50]}...'")

    start_time = time.time()

    # Count the words
    words = text.split()
    count = len(words)

    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool 'word_count' completed: {count} words found in {duration_ms:.2f}ms")

    return f"The text contains {count} words"


# ============================================================
# Step 8: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info("Starting exercise 1 server on stdio transport...")
    logger.info(f"Logging to console (INFO+) and file (DEBUG+)")
    logger.info(f"Log file: {log_file_path}")
    server.run(transport="stdio")
