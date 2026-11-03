"""
Exercise 1 Solution: Production-Ready Server
"""

import os
import logging
import time
from mcp.server.fastmcp import FastMCP

# ============================================================
# CONFIGURATION
# ============================================================

SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "prod-server")
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")
ENVIRONMENT = os.environ.get("MCP_ENVIRONMENT", "development")

# ============================================================
# LOGGING SETUP
# ============================================================

logger = logging.getLogger(SERVER_NAME)
logger.setLevel(getattr(logging, LOG_LEVEL))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler("server.log")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# ============================================================
# SERVER
# ============================================================

server = FastMCP(SERVER_NAME)

logger.info(f"Server '{SERVER_NAME}' starting in {ENVIRONMENT} mode")


@server.tool()
def add(a: int, b: int) -> str:
    """Add two numbers."""
    logger.info(f"add called with a={a}, b={b}")
    try:
        result = a + b
        logger.info(f"add result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"add error: {e}")
        return f"Error: {str(e)}"


@server.tool()
def divide(a: float, b: float) -> str:
    """Divide two numbers."""
    logger.info(f"divide called with a={a}, b={b}")
    try:
        if b == 0:
            logger.warning("Division by zero attempted")
            return "Error: Cannot divide by zero"
        result = a / b
        logger.info(f"divide result: {result}")
        return str(round(result, 4))
    except Exception as e:
        logger.error(f"divide error: {e}")
        return f"Error: {str(e)}"


@server.tool()
def server_info() -> str:
    """Get server information."""
    logger.info("server_info called")
    info = f"Server: {SERVER_NAME}\nEnvironment: {ENVIRONMENT}\nLog Level: {LOG_LEVEL}"
    return info


if __name__ == "__main__":
    server.run()
