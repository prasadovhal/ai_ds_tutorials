"""
Exercise 2 SOLUTION: Server with UUID Request Tracing
======================================================
This solution creates an MCP server where every tool call
gets a unique UUID, making it easy to trace requests in logs.

Poetry setup:
    poetry init --name exercise2-solution --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time
import uuid

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Set up logging
# ============================================================

logger = logging.getLogger("mcp_traced")
logger.setLevel(logging.DEBUG)

# Format includes a placeholder for request_id
log_format = logging.Formatter(
    "%(asctime)s [%(request_id)s] %(levelname)-8s %(message)s",
    defaults={"request_id": "--------"}
)

# Console handler
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# File handler
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "exercise2_traced.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# ============================================================
# Step 2: Create a function to generate request IDs
# ============================================================


def new_request_id():
    """
    Generate a short unique request ID.
    Uses first 8 characters of a UUID4 for readability.
    Example: "a1b2c3d4"
    """
    return str(uuid.uuid4()).replace("-", "")[:8]


# ============================================================
# Step 3: Create a traced logging helper
# ============================================================


def traced_log(level, request_id, message):
    """
    Log a message with a request ID attached.

    The request_id will appear in the log output between brackets,
    making it easy to filter and follow specific requests.
    """
    numeric_level = getattr(logging, level.upper())
    logger.log(numeric_level, message, extra={"request_id": request_id})


# ============================================================
# Step 4: Create the MCP server
# ============================================================

server = FastMCP("trace-exercise-server")

logger.info("Traced server initialized", extra={"request_id": "startup"})

# ============================================================
# Step 5: Create a tool with request tracing
# ============================================================


@server.tool()
def process_text(text: str, action: str) -> str:
    """Process text: uppercase, lowercase, reverse, or word_count."""

    # Generate a unique ID for this request
    req_id = new_request_id()

    # Log entry
    traced_log("INFO", req_id, f"Tool 'process_text' called")
    traced_log("DEBUG", req_id, f"Params: text='{text[:30]}...', action='{action}'")

    start_time = time.time()

    # Validate the action
    valid_actions = ["uppercase", "lowercase", "reverse", "word_count"]
    if action not in valid_actions:
        traced_log("ERROR", req_id, f"Invalid action: '{action}'")
        return f"Error: action must be one of {valid_actions}"

    traced_log("DEBUG", req_id, f"Processing with action '{action}'...")

    # Perform the action
    result = ""
    if action == "uppercase":
        result = text.upper()
    elif action == "lowercase":
        result = text.lower()
    elif action == "reverse":
        result = text[::-1]
    elif action == "word_count":
        count = len(text.split())
        result = f"{count} words"

    # Log exit
    duration_ms = (time.time() - start_time) * 1000
    traced_log("INFO", req_id, f"Tool completed in {duration_ms:.2f}ms")
    traced_log("DEBUG", req_id, f"Result: '{result[:50]}'")

    return f"[{req_id}] Result: {result}"


# ============================================================
# Step 6: Create another traced tool
# ============================================================


@server.tool()
def lookup_info(topic: str) -> str:
    """Look up information about a topic from sample data."""

    req_id = new_request_id()

    traced_log("INFO", req_id, f"Tool 'lookup_info' called")
    traced_log("DEBUG", req_id, f"Topic: '{topic}'")

    start_time = time.time()

    # Sample knowledge base (in a real server, this would be a database)
    knowledge = {
        "python": "Python is a high-level programming language created by Guido van Rossum.",
        "mcp": "MCP (Model Context Protocol) is a standard for AI tool integration.",
        "logging": "Logging records events that happen during program execution.",
        "tracing": "Tracing follows a request through all processing steps using a unique ID.",
    }

    traced_log("DEBUG", req_id, f"Searching {len(knowledge)} topics...")

    # Search for the topic (case-insensitive)
    result = None
    for key, value in knowledge.items():
        if topic.lower() == key.lower():
            result = value
            traced_log("DEBUG", req_id, f"Found exact match for '{key}'")
            break

    # If no exact match, try partial match
    if result is None:
        traced_log("DEBUG", req_id, "No exact match, trying partial match...")
        for key, value in knowledge.items():
            if topic.lower() in key.lower() or key.lower() in topic.lower():
                result = value
                traced_log("DEBUG", req_id, f"Found partial match: '{key}'")
                break

    duration_ms = (time.time() - start_time) * 1000

    if result is None:
        traced_log("WARNING", req_id, f"No information found for '{topic}'")
        return f"[{req_id}] No information found for '{topic}'"

    traced_log("INFO", req_id, f"Lookup completed in {duration_ms:.2f}ms")

    return f"[{req_id}] {topic}: {result}"


# ============================================================
# Step 7: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info("Starting traced server on stdio transport...", extra={"request_id": "startup"})
    logger.info(f"Log file: {log_file_path}", extra={"request_id": "startup"})
    server.run(transport="stdio")
