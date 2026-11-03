"""
Example 2: Structured Logging for MCP Server
==============================================
This example shows how to set up JSON-based structured logging.

Traditional logs look like this:
    2025-01-15 14:30:22 - INFO - Tool calculator called

Structured logs look like this:
    {"timestamp": "2025-01-15T14:30:22", "level": "INFO", "tool": "calculator"}

Why structured logging?
- Machine-readable: tools can parse, search, and aggregate JSON logs
- Consistent: every log entry has the same fields
- Searchable: find all logs for a specific tool, user, or error type
- Ready for production: works with ELK Stack, Grafana Loki, Datadog

Poetry setup:
    poetry init --name example2-structured-logging --python "^3.11" --no-interaction
    poetry add mcp
    poetry add python-json-logger
    poetry install
    poetry shell
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Create a custom JSON formatter
# ============================================================
# We build a simple JSON formatter ourselves.
# This way you understand exactly how structured logging works.
# In production, you might use the python-json-logger library instead.


class SimpleJsonFormatter(logging.Formatter):
    """
    A custom log formatter that outputs each log message as a JSON object.

    Each log line will look like:
    {"timestamp": "2025-01-15T14:30:22.345Z", "level": "INFO", "message": "...", ...}
    """

    def format(self, record):
        """
        Format a log record as a JSON string.

        Parameters:
            record: The log record object created by Python's logging module.
                    It contains level, message, timestamp, and any extra fields.
        """

        # Start building the JSON object with standard fields
        log_entry = {}

        # Add timestamp in ISO 8601 format (international standard)
        log_entry["timestamp"] = datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).isoformat()

        # Add the log level (INFO, ERROR, etc.)
        log_entry["level"] = record.levelname

        # Add the logger name (identifies which component produced this log)
        log_entry["logger"] = record.name

        # Add the log message
        log_entry["message"] = record.getMessage()

        # Add the source file and line number (useful for debugging)
        log_entry["file"] = record.filename
        log_entry["line"] = record.lineno

        # If the log record has extra fields, add them too
        # Extra fields are added using logger.info("msg", extra={"key": "value"})
        # We check for common extra fields that we add in our MCP server
        extra_fields = [
            "tool_name", "args", "result", "duration_ms",
            "error", "request_id", "client_id"
        ]
        for field in extra_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        # Convert the dictionary to a JSON string
        # ensure_ascii=False allows non-English characters in logs
        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ============================================================
# STEP 2: Set up the structured logger
# ============================================================

# Create a logger
logger = logging.getLogger("mcp_structured")
logger.setLevel(logging.DEBUG)

# Create console handler with our JSON formatter
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(SimpleJsonFormatter())
logger.addHandler(console_handler)

# Create file handler with our JSON formatter
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, "mcp_structured.log")

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(SimpleJsonFormatter())
logger.addHandler(file_handler)

# ============================================================
# STEP 3: Create the MCP server
# ============================================================

server = FastMCP("structured-logging-server")

logger.info(
    "MCP Server initialized with structured logging",
    extra={"tool_name": "server", "args": {}}
)

# ============================================================
# STEP 4: Define tools with structured log fields
# ============================================================


@server.tool()
def calculate(operation: str, a: float, b: float) -> str:
    """Perform a math operation: add, subtract, multiply, or divide."""

    # Log the incoming request with structured fields
    # The 'extra' dict adds custom fields to the JSON output
    logger.info(
        "Tool call received",
        extra={
            "tool_name": "calculate",
            "args": {"operation": operation, "a": a, "b": b}
        }
    )

    start_time = time.time()

    # Perform the requested operation
    result = None
    error_message = None

    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            error_message = "Division by zero"
        else:
            result = a / b
    else:
        error_message = f"Unknown operation: {operation}"

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log the result or error with structured fields
    if error_message:
        logger.error(
            "Tool call failed",
            extra={
                "tool_name": "calculate",
                "args": {"operation": operation, "a": a, "b": b},
                "error": error_message,
                "duration_ms": round(duration_ms, 2)
            }
        )
        return f"Error: {error_message}"

    logger.info(
        "Tool call completed",
        extra={
            "tool_name": "calculate",
            "args": {"operation": operation, "a": a, "b": b},
            "result": result,
            "duration_ms": round(duration_ms, 2)
        }
    )

    return f"Result of {a} {operation} {b} = {result}"


@server.tool()
def analyze_text(text: str) -> str:
    """Analyze a text string and return statistics about it."""

    logger.info(
        "Tool call received",
        extra={
            "tool_name": "analyze_text",
            "args": {"text_length": len(text)}
        }
    )

    start_time = time.time()

    # Count various text properties
    word_count = len(text.split())
    char_count = len(text)
    line_count = text.count("\n") + 1
    sentence_count = text.count(".") + text.count("!") + text.count("?")

    # Build the result
    analysis = {
        "words": word_count,
        "characters": char_count,
        "lines": line_count,
        "sentences": sentence_count
    }

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "Tool call completed",
        extra={
            "tool_name": "analyze_text",
            "result": analysis,
            "duration_ms": round(duration_ms, 2)
        }
    )

    # Format the result as a readable string
    result_text = f"Text Analysis:\n"
    result_text = result_text + f"  Words: {word_count}\n"
    result_text = result_text + f"  Characters: {char_count}\n"
    result_text = result_text + f"  Lines: {line_count}\n"
    result_text = result_text + f"  Sentences: {sentence_count}"

    return result_text


@server.tool()
def validate_email(email: str) -> str:
    """Check if an email address looks valid."""

    logger.info(
        "Tool call received",
        extra={
            "tool_name": "validate_email",
            "args": {"email_domain": email.split("@")[-1] if "@" in email else "invalid"}
        }
    )

    start_time = time.time()

    # Simple email validation (not comprehensive, just for demonstration)
    is_valid = True
    reasons = []

    # Check for @ symbol
    if "@" not in email:
        is_valid = False
        reasons.append("Missing @ symbol")

    # Check for domain part
    if "@" in email:
        parts = email.split("@")
        if len(parts) != 2:
            is_valid = False
            reasons.append("Multiple @ symbols")
        elif "." not in parts[1]:
            is_valid = False
            reasons.append("Domain missing dot")
        elif len(parts[0]) == 0:
            is_valid = False
            reasons.append("Empty username")

    duration_ms = (time.time() - start_time) * 1000

    if is_valid:
        logger.info(
            "Tool call completed",
            extra={
                "tool_name": "validate_email",
                "result": "valid",
                "duration_ms": round(duration_ms, 2)
            }
        )
        return f"'{email}' appears to be a valid email address"
    else:
        logger.warning(
            "Tool call completed with validation failure",
            extra={
                "tool_name": "validate_email",
                "result": "invalid",
                "error": "; ".join(reasons),
                "duration_ms": round(duration_ms, 2)
            }
        )
        return f"'{email}' is not valid. Reasons: {', '.join(reasons)}"


# ============================================================
# STEP 5: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info(
        "Starting MCP server",
        extra={
            "tool_name": "server",
            "args": {"transport": "stdio", "log_file": log_file_path}
        }
    )
    server.run(transport="stdio")
