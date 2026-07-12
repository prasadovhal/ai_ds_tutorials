"""
Example 1: Basic Logging for MCP Server
========================================
This example shows how to set up Python's built-in logging module
for an MCP server with both file and console handlers.

Why logging matters:
- print() statements cannot be turned off without removing them
- print() has no severity levels (DEBUG, INFO, ERROR, etc.)
- print() cannot write to files automatically
- Logging gives you all of these features built-in

We will set up:
1. A console handler (shows INFO and above on screen)
2. A file handler (saves DEBUG and above to a file)
3. Proper formatting with timestamps and log levels

Poetry setup:
    poetry init --name example1-basic-logging --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time

# ============================================================
# STEP 1: Import FastMCP to create our MCP server
# ============================================================
from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 2: Set up the logging configuration
# ============================================================

# Create a logger with a specific name
# Using a name helps you identify which part of your code produced each log
logger = logging.getLogger("mcp_server")

# Set the logger's level to DEBUG
# This means the logger ITSELF will accept all messages
# The HANDLERS will then filter based on their own levels
logger.setLevel(logging.DEBUG)

# Create a formatter that defines how each log message looks
# %(asctime)s    --> timestamp like "2025-01-15 14:30:22,345"
# %(name)s       --> logger name, which is "mcp_server"
# %(levelname)s  --> log level like "INFO" or "ERROR"
# %(message)s    --> the actual log message
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ============================================================
# STEP 3: Create a console handler (prints to terminal)
# ============================================================

# StreamHandler sends log messages to the console (stdout)
console_handler = logging.StreamHandler(sys.stdout)

# Set console handler to INFO level
# This means the console will show INFO, WARNING, ERROR, CRITICAL
# but will NOT show DEBUG messages (too verbose for console)
console_handler.setLevel(logging.INFO)

# Apply the formatter to the console handler
console_handler.setFormatter(log_format)

# Add the handler to our logger
logger.addHandler(console_handler)

# ============================================================
# STEP 4: Create a file handler (writes to a log file)
# ============================================================

# Determine the log file path
# We put it in the same directory as this script
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "mcp_server.log")

# FileHandler writes log messages to a file on disk
file_handler = logging.FileHandler(log_file_path)

# Set file handler to DEBUG level
# This means the file will contain ALL messages including DEBUG
# This is useful for troubleshooting -- you can always check the file
file_handler.setLevel(logging.DEBUG)

# Apply the formatter to the file handler
file_handler.setFormatter(log_format)

# Add the handler to our logger
logger.addHandler(file_handler)

# ============================================================
# STEP 5: Create the MCP server
# ============================================================

# Log the startup event
logger.info("Initializing MCP Server with basic logging...")

# Create the FastMCP server instance
server = FastMCP("logging-example-server")

logger.info("MCP Server instance created successfully")

# ============================================================
# STEP 6: Define tools with logging at every step
# ============================================================

# Register a simple addition tool
# We log: when the tool is called, what arguments it received,
# the result, and how long it took
@server.tool()
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together and return the result."""

    # Log that the tool was called (INFO level -- normal operation)
    logger.info(f"Tool 'add_numbers' called with a={a}, b={b}")

    # Log the detailed processing step (DEBUG level -- for troubleshooting)
    logger.debug(f"Computing {a} + {b}")

    # Record the start time so we can measure how long it takes
    start_time = time.time()

    # Perform the actual computation
    result = a + b

    # Calculate how long the computation took
    duration_ms = (time.time() - start_time) * 1000

    # Log the result (INFO level)
    logger.info(f"Tool 'add_numbers' completed: result={result}, duration={duration_ms:.2f}ms")

    # Return the result as a string
    return f"The sum of {a} and {b} is {result}"


# Register a division tool (this one can fail!)
@server.tool()
def divide_numbers(a: float, b: float) -> str:
    """Divide the first number by the second number."""

    logger.info(f"Tool 'divide_numbers' called with a={a}, b={b}")

    # Check for division by zero BEFORE attempting it
    if b == 0:
        # Log the error (ERROR level -- operation failed)
        logger.error(f"Tool 'divide_numbers' failed: division by zero (a={a}, b={b})")
        return "Error: Cannot divide by zero"

    start_time = time.time()

    result = a / b

    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool 'divide_numbers' completed: result={result}, duration={duration_ms:.2f}ms")

    return f"{a} divided by {b} is {result}"


# Register a tool that processes text
@server.tool()
def count_words(text: str) -> str:
    """Count the number of words in a text string."""

    logger.info(f"Tool 'count_words' called with text of length {len(text)}")

    # Log the actual text at DEBUG level (might be sensitive in production)
    logger.debug(f"Full text received: '{text}'")

    start_time = time.time()

    # Split the text into words and count them
    words = text.split()
    word_count = len(words)

    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool 'count_words' completed: {word_count} words found, duration={duration_ms:.2f}ms")

    return f"The text contains {word_count} words"


# ============================================================
# STEP 7: Log all registered tools
# ============================================================

logger.info("All tools registered successfully")
logger.info("Registered tools: add_numbers, divide_numbers, count_words")

# ============================================================
# STEP 8: Run the server
# ============================================================

if __name__ == "__main__":
    # Log that we are starting the server
    logger.info("Starting MCP server on stdio transport...")
    logger.info(f"Log file location: {log_file_path}")
    logger.info("Server is ready to accept connections")

    # Run the MCP server using stdio transport
    # All communication happens through stdin/stdout
    server.run(transport="stdio")
