"""
Exercise 1 Solution: Configuration Resource Server
====================================================
This solution creates an MCP server that serves application
configuration files as resources. Each configuration is served
as a JSON resource with realistic settings.

How to run:
    python exercise1_solution.py

How to test:
    npx @modelcontextprotocol/inspector python exercise1_solution.py
"""

from mcp.server.fastmcp import FastMCP
import json

# ============================================================
# Step 1: Create the MCP Server
# ============================================================
server = FastMCP("Config Resource Server")


# ============================================================
# Step 2: Main Application Configuration Resource
# ============================================================
# This resource returns the main application settings.
# In a real app, these might come from a config file or
# environment variables. Here we define them as a dictionary.
@server.resource("config://app/main")
def get_main_config():
    """Return the main application configuration."""

    config = {
        "app_name": "MCP Demo Application",
        "version": "2.1.0",
        "environment": "development",
        "debug_mode": True,
        "max_connections": 100,
        "log_level": "INFO",
        "allowed_hosts": ["localhost", "127.0.0.1"],
        "cors_origins": ["http://localhost:3000"],
        "session_timeout_minutes": 30,
        "rate_limit_per_minute": 60
    }

    return json.dumps(config, indent=2)


# ============================================================
# Step 3: Database Configuration Resource
# ============================================================
# This resource returns database connection settings.
# IMPORTANT: Never include actual passwords in resources!
# Here we use placeholder values.
@server.resource("config://app/database")
def get_database_config():
    """Return the database configuration."""

    config = {
        "host": "localhost",
        "port": 5432,
        "database_name": "mcp_demo_db",
        "pool_size": 10,
        "max_overflow": 20,
        "timeout_seconds": 30,
        "ssl_enabled": False,
        "auto_migrate": True,
        "echo_sql": False,
        "connection_string_template": "postgresql://{user}:{password}@{host}:{port}/{database}"
    }

    return json.dumps(config, indent=2)


# ============================================================
# Step 4: Logging Configuration Resource
# ============================================================
# This resource returns logging settings.
@server.resource("config://app/logging")
def get_logging_config():
    """Return the logging configuration."""

    config = {
        "log_level": "INFO",
        "log_file": "logs/app.log",
        "max_file_size_mb": 10,
        "backup_count": 5,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "console_output": True,
        "json_format": False,
        "log_rotation": "daily",
        "modules": {
            "mcp_server": "DEBUG",
            "database": "WARNING",
            "http": "INFO"
        }
    }

    return json.dumps(config, indent=2)


# ============================================================
# Step 5: Configuration Index Resource
# ============================================================
# This resource lists all available configurations.
# It helps clients discover what configs are available
# without having to guess URIs.
@server.resource("config://app/index")
def get_config_index():
    """Return an index of all available configurations."""

    index = {
        "available_configurations": [
            {
                "name": "Main Application Config",
                "uri": "config://app/main",
                "description": "Core application settings including version, debug mode, and connection limits"
            },
            {
                "name": "Database Config",
                "uri": "config://app/database",
                "description": "Database connection settings including host, port, pool size, and SSL"
            },
            {
                "name": "Logging Config",
                "uri": "config://app/logging",
                "description": "Logging settings including log level, file paths, rotation, and format"
            }
        ],
        "total_configs": 3,
        "note": "Use the URI to read each configuration resource"
    }

    return json.dumps(index, indent=2)


# ============================================================
# Step 6: Run the Server
# ============================================================
if __name__ == "__main__":
    server.run()
