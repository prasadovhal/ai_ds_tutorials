"""
Example 2: Configuration Management for MCP Server
====================================================
This example shows how to load configuration from environment
variables with sensible defaults.

In production, you NEVER hardcode configuration values like:
- Server names
- Log levels
- Database URLs
- API keys
- Rate limits

Instead, you read them from environment variables.
This lets you change settings without modifying code.

Poetry setup:
    poetry init --name example2-config-management --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import os
import sys
import logging

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Define configuration with defaults
# ============================================================

# Read each config value from environment variables
# os.environ.get("NAME", "default") returns the env var if set,
# otherwise returns the default value

# Server name -- identifies this server instance
SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "my-mcp-server")

# Log level -- controls how much logging output you see
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")

# Database URL -- where to connect for data storage
# Default is a local SQLite file
DB_URL = os.environ.get("MCP_DB_URL", "sqlite:///data/local.db")

# Rate limit -- max tool calls per minute per client
# Prevents abuse of the server
RATE_LIMIT = int(os.environ.get("MCP_RATE_LIMIT", "60"))

# Environment name -- development, staging, or production
ENVIRONMENT = os.environ.get("MCP_ENVIRONMENT", "development")

# Max response size in characters
MAX_RESPONSE_SIZE = int(os.environ.get("MCP_MAX_RESPONSE_SIZE", "10000"))

# ============================================================
# STEP 2: Collect all config into a dictionary for easy access
# ============================================================

config = {
    "server_name": SERVER_NAME,
    "log_level": LOG_LEVEL,
    "db_url": DB_URL,
    "rate_limit": RATE_LIMIT,
    "environment": ENVIRONMENT,
    "max_response_size": MAX_RESPONSE_SIZE,
}

# ============================================================
# STEP 3: Set up logging based on config
# ============================================================

logger = logging.getLogger(SERVER_NAME)
logger.setLevel(getattr(logging, LOG_LEVEL))

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(getattr(logging, LOG_LEVEL))
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# ============================================================
# STEP 4: Log the current configuration
# ============================================================

logger.info("=" * 50)
logger.info("MCP Server Configuration")
logger.info("=" * 50)
for key, value in config.items():
    # Mask sensitive values like database URLs
    if "url" in key.lower() or "key" in key.lower():
        # Show only the first 10 characters for security
        masked = str(value)[:10] + "***"
        logger.info(f"  {key}: {masked}")
    else:
        logger.info(f"  {key}: {value}")
logger.info("=" * 50)

# ============================================================
# STEP 5: Create the MCP server using config
# ============================================================

server = FastMCP(config["server_name"])

logger.info(f"Server '{config['server_name']}' created in {config['environment']} mode")

# ============================================================
# STEP 6: Define tools that use the configuration
# ============================================================


@server.tool()
def get_config() -> str:
    """
    Show the current server configuration.
    Sensitive values like DB URLs are masked.
    """

    logger.info("Tool 'get_config' called")

    output = "Current Server Configuration:\n\n"

    for key, value in config.items():
        # Mask sensitive fields
        if "url" in key.lower() or "key" in key.lower():
            display_value = str(value)[:10] + "***"
        else:
            display_value = str(value)

        output = output + f"  {key}: {display_value}\n"

    return output


@server.tool()
def echo(message: str) -> str:
    """
    Echo a message back, respecting the max response size config.
    Demonstrates how tools can use configuration values.
    """

    logger.info(f"Tool 'echo' called with message length {len(message)}")

    # Use the config to limit response size
    if len(message) > config["max_response_size"]:
        logger.warning(
            f"Message too long ({len(message)}), truncating to {config['max_response_size']}"
        )
        message = message[:config["max_response_size"]] + "... (truncated)"

    return f"[{config['environment']}] Echo: {message}"


@server.tool()
def server_info() -> str:
    """Return basic server information."""

    logger.info("Tool 'server_info' called")

    info = f"Server: {config['server_name']}\n"
    info = info + f"Environment: {config['environment']}\n"
    info = info + f"Log Level: {config['log_level']}\n"
    info = info + f"Rate Limit: {config['rate_limit']} calls/min\n"

    return info


# ============================================================
# STEP 7: Print config summary and run
# ============================================================

if __name__ == "__main__":
    # Print a summary of how to set environment variables
    print("=" * 55)
    print("  Configuration Management Example")
    print("=" * 55)
    print()
    print("Current config loaded from environment variables:")
    for key, value in config.items():
        print(f"  {key} = {value}")
    print()
    print("To change config, set environment variables:")
    print("  export MCP_SERVER_NAME=my-server")
    print("  export MCP_LOG_LEVEL=DEBUG")
    print("  export MCP_DB_URL=postgresql://localhost/mydb")
    print("  export MCP_RATE_LIMIT=100")
    print("  export MCP_ENVIRONMENT=production")
    print()
    print("Starting server...")
    server.run(transport="stdio")
