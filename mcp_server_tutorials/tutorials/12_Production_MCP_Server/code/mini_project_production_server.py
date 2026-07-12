"""
Mini Project: Complete Production-Grade MCP Server
===================================================
A fully production-ready server with:
- Configuration management (env vars)
- Structured logging (file + console)
- Error handling
- Health checks
- Version info
- Multiple tools
- Metrics tracking
"""

import os
import json
import time
import logging
from mcp.server.fastmcp import FastMCP

# ============================================================
# CONFIGURATION
# ============================================================

SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "production-server")
VERSION = "1.0.0"
ENVIRONMENT = os.environ.get("MCP_ENVIRONMENT", "development")
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")
DATA_DIR = os.environ.get("MCP_DATA_DIR", "./data")

# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(SERVER_NAME)
logger.setLevel(getattr(logging, LOG_LEVEL))

# Console handler
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console)

# File handler
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/server.log")
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))
logger.addHandler(file_handler)

# ============================================================
# METRICS
# ============================================================

START_TIME = time.time()
metrics = {
    "total_calls": 0,
    "errors": 0,
    "calls_per_tool": {},
}


def track_call(tool_name, is_error=False):
    """Track a tool call in metrics."""
    metrics["total_calls"] += 1
    if tool_name not in metrics["calls_per_tool"]:
        metrics["calls_per_tool"][tool_name] = 0
    metrics["calls_per_tool"][tool_name] += 1
    if is_error:
        metrics["errors"] += 1


# ============================================================
# SERVER
# ============================================================

server = FastMCP(SERVER_NAME)

logger.info(f"Server '{SERVER_NAME}' v{VERSION} starting ({ENVIRONMENT})")


# --- Health and Status Tools ---

@server.tool()
def health_check() -> str:
    """Check server health and status."""
    track_call("health_check")
    uptime = round(time.time() - START_TIME, 1)
    health = {
        "status": "healthy",
        "server": SERVER_NAME,
        "version": VERSION,
        "environment": ENVIRONMENT,
        "uptime_seconds": uptime,
    }
    logger.info("Health check: healthy")
    return json.dumps(health, indent=2)


@server.tool()
def get_version() -> str:
    """Get server version information."""
    track_call("get_version")
    return f"{SERVER_NAME} v{VERSION} ({ENVIRONMENT})"


@server.tool()
def get_metrics() -> str:
    """Get server metrics."""
    track_call("get_metrics")
    uptime = round(time.time() - START_TIME, 1)
    result = {
        "uptime_seconds": uptime,
        "total_calls": metrics["total_calls"],
        "errors": metrics["errors"],
        "calls_per_tool": metrics["calls_per_tool"],
    }
    return json.dumps(result, indent=2)


# --- Business Tools ---

@server.tool()
def add(a: int, b: int) -> str:
    """Add two numbers."""
    track_call("add")
    logger.info(f"add({a}, {b})")
    try:
        result = a + b
        return str(result)
    except Exception as e:
        track_call("add", is_error=True)
        logger.error(f"add error: {e}")
        return f"Error: {str(e)}"


@server.tool()
def divide(a: float, b: float) -> str:
    """Divide two numbers with error handling."""
    track_call("divide")
    logger.info(f"divide({a}, {b})")
    try:
        if b == 0:
            track_call("divide", is_error=True)
            logger.warning("Division by zero attempted")
            return "Error: Cannot divide by zero"
        result = a / b
        return str(round(result, 4))
    except Exception as e:
        track_call("divide", is_error=True)
        logger.error(f"divide error: {e}")
        return f"Error: {str(e)}"


@server.tool()
def uppercase(text: str) -> str:
    """Convert text to uppercase."""
    track_call("uppercase")
    logger.info(f"uppercase called, length={len(text)}")
    try:
        return text.upper()
    except Exception as e:
        track_call("uppercase", is_error=True)
        logger.error(f"uppercase error: {e}")
        return f"Error: {str(e)}"


@server.tool()
def word_count(text: str) -> str:
    """Count words in text."""
    track_call("word_count")
    logger.info(f"word_count called, length={len(text)}")
    words = text.split()
    return str(len(words))


# --- Resources ---

@server.resource("info://about")
def get_about() -> str:
    """Server information."""
    return f"{SERVER_NAME} v{VERSION} - A production-grade MCP server"


@server.resource("info://config")
def get_config() -> str:
    """Current configuration."""
    config = {
        "server": SERVER_NAME,
        "version": VERSION,
        "environment": ENVIRONMENT,
        "log_level": LOG_LEVEL,
    }
    return json.dumps(config, indent=2)


# --- Prompts ---

@server.prompt()
def analyze(text: str) -> str:
    """Prompt for analyzing text."""
    return f"Please analyze the following text and provide key insights:\n\n{text}"


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info("Server ready to accept connections")
    server.run()
