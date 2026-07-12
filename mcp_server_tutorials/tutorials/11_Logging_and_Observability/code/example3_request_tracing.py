"""
Example 3: Request Tracing for MCP Server
===========================================
This example shows how to assign a unique ID to every incoming request
and include that ID in all related log messages.

Why request tracing?
When multiple clients call your MCP server at the same time,
their log messages get mixed together. Without a request ID,
you cannot tell which log messages belong to which request.

With a request ID, you can filter logs and follow a single
request through the entire processing pipeline.

Example without tracing:
    14:30:22 INFO Tool called: calculator
    14:30:22 INFO Tool called: weather
    14:30:22 DEBUG Querying database
    14:30:22 ERROR Timeout!           <-- which tool caused this?

Example with tracing:
    14:30:22 [req-001] INFO Tool called: calculator
    14:30:22 [req-002] INFO Tool called: weather
    14:30:22 [req-001] DEBUG Querying database
    14:30:22 [req-001] ERROR Timeout!  <-- clearly calculator!

Poetry setup:
    poetry init --name example3-request-tracing --python "^3.11" --no-interaction
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
# STEP 1: Create a helper function to generate unique request IDs
# ============================================================


def generate_request_id():
    """
    Generate a short unique ID for each request.

    We use UUID4 (random) and take the first 8 characters.
    This gives us enough uniqueness for logging purposes.

    Example output: "req-a1b2c3d4"
    """
    # uuid.uuid4() generates a random UUID like "550e8400-e29b-41d4-a716-446655440000"
    # We take just the first 8 hex characters for brevity
    short_id = str(uuid.uuid4()).replace("-", "")[:8]
    return f"req-{short_id}"


# ============================================================
# STEP 2: Set up logging with a format that includes request IDs
# ============================================================

logger = logging.getLogger("mcp_traced")
logger.setLevel(logging.DEBUG)

# Format includes a placeholder where we will insert the request ID
# We use a simple format: timestamp [request_id] LEVEL message
log_format = logging.Formatter(
    "%(asctime)s [%(request_id)s] %(levelname)-8s %(message)s",
    defaults={"request_id": "no-req-id"}
)

# Console handler (INFO and above)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# File handler (DEBUG and above)
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "mcp_traced.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# ============================================================
# STEP 3: Create a helper function for traced logging
# ============================================================

# This function makes it easy to log with a request ID.
# Instead of calling logger.info("msg", extra={"request_id": rid}) every time,
# we create a simple wrapper.


def log_with_trace(level, request_id, message):
    """
    Log a message with a request ID attached.

    Parameters:
        level: The log level string ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        request_id: The unique ID for this request
        message: The log message
    """
    # Get the numeric log level from the string
    numeric_level = getattr(logging, level.upper())

    # Log the message with the request_id as an extra field
    logger.log(numeric_level, message, extra={"request_id": request_id})


# ============================================================
# STEP 4: Create the MCP server
# ============================================================

server = FastMCP("traced-server")

logger.info("MCP Server initialized with request tracing", extra={"request_id": "startup"})

# ============================================================
# STEP 5: Define tools with request tracing
# ============================================================


@server.tool()
def process_data(data: str, operation: str) -> str:
    """Process data with a specified operation (uppercase, lowercase, reverse, count)."""

    # Step 5a: Generate a unique request ID for this tool call
    request_id = generate_request_id()

    # Step 5b: Log the incoming request
    log_with_trace("INFO", request_id, f"Tool 'process_data' called")
    log_with_trace("DEBUG", request_id, f"Arguments: data='{data}', operation='{operation}'")

    # Step 5c: Track timing
    start_time = time.time()

    # Step 5d: Validate the operation
    valid_operations = ["uppercase", "lowercase", "reverse", "count"]
    if operation not in valid_operations:
        log_with_trace(
            "ERROR", request_id,
            f"Invalid operation: '{operation}'. Valid: {valid_operations}"
        )
        return f"Error: Unknown operation '{operation}'. Use one of: {valid_operations}"

    log_with_trace("DEBUG", request_id, f"Operation '{operation}' is valid, processing...")

    # Step 5e: Perform the operation
    result = ""
    if operation == "uppercase":
        result = data.upper()
        log_with_trace("DEBUG", request_id, "Converted text to uppercase")
    elif operation == "lowercase":
        result = data.lower()
        log_with_trace("DEBUG", request_id, "Converted text to lowercase")
    elif operation == "reverse":
        result = data[::-1]
        log_with_trace("DEBUG", request_id, "Reversed the text")
    elif operation == "count":
        result = str(len(data))
        log_with_trace("DEBUG", request_id, f"Counted {len(data)} characters")

    # Step 5f: Log completion with timing
    duration_ms = (time.time() - start_time) * 1000
    log_with_trace(
        "INFO", request_id,
        f"Tool 'process_data' completed in {duration_ms:.2f}ms"
    )

    return f"Result of {operation}: {result}"


@server.tool()
def multi_step_pipeline(text: str) -> str:
    """Run a multi-step processing pipeline on text (clean, analyze, summarize)."""

    # Generate request ID for this entire pipeline
    request_id = generate_request_id()

    log_with_trace("INFO", request_id, "Starting multi-step pipeline")
    log_with_trace("DEBUG", request_id, f"Input text length: {len(text)} characters")

    pipeline_start = time.time()

    # Pipeline Step 1: Clean the text
    step_start = time.time()
    log_with_trace("INFO", request_id, "Pipeline Step 1/3: Cleaning text")

    # Remove extra whitespace
    cleaned_text = " ".join(text.split())
    # Remove leading/trailing whitespace
    cleaned_text = cleaned_text.strip()

    step_duration = (time.time() - step_start) * 1000
    log_with_trace(
        "DEBUG", request_id,
        f"Step 1 completed in {step_duration:.2f}ms. "
        f"Text reduced from {len(text)} to {len(cleaned_text)} chars"
    )

    # Pipeline Step 2: Analyze the text
    step_start = time.time()
    log_with_trace("INFO", request_id, "Pipeline Step 2/3: Analyzing text")

    word_count = len(cleaned_text.split())
    sentence_count = cleaned_text.count(".") + cleaned_text.count("!") + cleaned_text.count("?")
    # Avoid division by zero
    if sentence_count == 0:
        sentence_count = 1
    avg_words_per_sentence = word_count / sentence_count

    step_duration = (time.time() - step_start) * 1000
    log_with_trace(
        "DEBUG", request_id,
        f"Step 2 completed in {step_duration:.2f}ms. "
        f"Words: {word_count}, Sentences: {sentence_count}"
    )

    # Pipeline Step 3: Create summary
    step_start = time.time()
    log_with_trace("INFO", request_id, "Pipeline Step 3/3: Creating summary")

    # Take first 100 characters as a preview
    preview = cleaned_text[:100]
    if len(cleaned_text) > 100:
        preview = preview + "..."

    step_duration = (time.time() - step_start) * 1000
    log_with_trace("DEBUG", request_id, f"Step 3 completed in {step_duration:.2f}ms")

    # Log total pipeline duration
    total_duration = (time.time() - pipeline_start) * 1000
    log_with_trace(
        "INFO", request_id,
        f"Pipeline completed in {total_duration:.2f}ms (3 steps)"
    )

    # Build the final result
    result = f"Pipeline Results:\n"
    result = result + f"  Words: {word_count}\n"
    result = result + f"  Sentences: {sentence_count}\n"
    result = result + f"  Avg words/sentence: {avg_words_per_sentence:.1f}\n"
    result = result + f"  Preview: {preview}"

    return result


@server.tool()
def search_data(query: str, max_results: int) -> str:
    """Search through sample data and return matching results."""

    request_id = generate_request_id()

    log_with_trace("INFO", request_id, f"Tool 'search_data' called")
    log_with_trace("DEBUG", request_id, f"Query: '{query}', max_results: {max_results}")

    start_time = time.time()

    # Sample data to search through (in a real server, this would be a database)
    sample_data = [
        "Python is a programming language",
        "MCP stands for Model Context Protocol",
        "Logging helps debug server issues",
        "FastMCP makes building MCP servers easy",
        "JSON-RPC is the message format used by MCP",
        "Tracing assigns unique IDs to requests",
        "Metrics track server performance over time",
        "Docker containers package applications",
        "Poetry manages Python dependencies",
        "Structured logging uses JSON format",
    ]

    log_with_trace("DEBUG", request_id, f"Searching through {len(sample_data)} records")

    # Search for matching records
    matches = []
    for item in sample_data:
        if query.lower() in item.lower():
            matches.append(item)

    log_with_trace(
        "DEBUG", request_id,
        f"Found {len(matches)} matches before applying max_results limit"
    )

    # Apply the max_results limit
    limited_matches = matches[:max_results]

    duration_ms = (time.time() - start_time) * 1000
    log_with_trace(
        "INFO", request_id,
        f"Search completed: {len(limited_matches)} results in {duration_ms:.2f}ms"
    )

    if len(limited_matches) == 0:
        return f"No results found for query: '{query}'"

    # Format results
    result = f"Search results for '{query}' ({len(limited_matches)} of {len(matches)}):\n"
    for i, match in enumerate(limited_matches):
        result = result + f"  {i + 1}. {match}\n"

    return result


# ============================================================
# STEP 6: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info(
        "Starting MCP server with request tracing on stdio transport",
        extra={"request_id": "startup"}
    )
    logger.info(
        f"Log file: {log_file_path}",
        extra={"request_id": "startup"}
    )
    server.run(transport="stdio")
