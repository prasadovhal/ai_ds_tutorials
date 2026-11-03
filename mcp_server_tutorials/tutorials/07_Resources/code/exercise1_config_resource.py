"""
Exercise 1: Configuration Resource Server
==========================================
YOUR TASK: Build an MCP server that serves application configuration
files as resources.

Requirements:
1. Create a resource for the main application config (JSON)
2. Create a resource for the database config (JSON)
3. Create a resource for the logging config (JSON)
4. Create a resource that lists all available configs
5. Each config should contain realistic settings

Hints:
- Use @server.resource("config://...") for each config
- Return JSON strings with json.dumps()
- The config listing resource should tell clients what configs exist

How to test:
    npx @modelcontextprotocol/inspector python exercise1_config_resource.py
"""

from mcp.server.fastmcp import FastMCP
import json

# Create the server
server = FastMCP("Config Resource Exercise")

# ============================================================
# TODO: Create a resource at "config://app/main" that returns
# the main application configuration as JSON.
# Include settings like: app_name, version, debug_mode,
# max_connections, log_level, allowed_hosts
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "config://app/database" that returns
# the database configuration as JSON.
# Include settings like: host, port, database_name, pool_size,
# timeout_seconds, ssl_enabled
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "config://app/logging" that returns
# the logging configuration as JSON.
# Include settings like: log_level, log_file, max_file_size_mb,
# backup_count, format, console_output
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "config://app/index" that returns
# a list of all available configurations with their URIs
# and descriptions.
# ============================================================

# YOUR CODE HERE


if __name__ == "__main__":
    server.run()
