"""
Mini Project: Multi-Transport MCP Server
==========================================
A full-featured MCP server that supports both STDIO and SSE transport.
Includes multiple tools, resources, and a prompt.
Transport is configurable via CLI args, env var, or config file.

Usage:
  python mini_project_multi_transport_server.py                  # STDIO
  python mini_project_multi_transport_server.py --transport=sse  # SSE
  python mini_project_multi_transport_server.py --help           # Show help
"""

import sys
import os
import json
import time
from mcp.server.fastmcp import FastMCP

# Create the server
server = FastMCP("multi-transport-server")

# Track server start time for uptime calculation
SERVER_START_TIME = time.time()


# ============================================================
# TOOLS
# ============================================================

@server.tool()
def echo(message: str) -> str:
    """Echo a message back. Useful for testing connectivity."""
    return f"Echo: {message}"


@server.tool()
def add(a: int, b: int) -> str:
    """Add two numbers."""
    result = a + b
    return str(result)


@server.tool()
def uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


@server.tool()
def server_status() -> str:
    """Get current server status including uptime and transport."""
    uptime = time.time() - SERVER_START_TIME
    transport = os.environ.get("MCP_TRANSPORT", "stdio")

    status = {
        "server": "multi-transport-server",
        "transport": transport,
        "uptime_seconds": round(uptime, 1),
        "status": "healthy",
    }
    return json.dumps(status, indent=2)


@server.tool()
def get_config() -> str:
    """Get current server configuration."""
    config = {
        "transport": os.environ.get("MCP_TRANSPORT", "stdio"),
        "host": os.environ.get("MCP_HOST", "localhost"),
        "port": os.environ.get("MCP_PORT", "8000"),
    }
    return json.dumps(config, indent=2)


# ============================================================
# RESOURCES
# ============================================================

@server.resource("info://about")
def get_about() -> str:
    """About this server."""
    return "Multi-Transport MCP Server v1.0 - Supports STDIO and SSE"


@server.resource("info://help")
def get_help() -> str:
    """Usage instructions."""
    return (
        "Tools: echo, add, uppercase, server_status, get_config\n"
        "Transports: stdio (default), sse\n"
        "Use --transport=sse to run with SSE transport."
    )


# ============================================================
# PROMPTS
# ============================================================

@server.prompt()
def test_prompt(text: str) -> str:
    """A test prompt for verifying integrations."""
    return f"Please analyze the following and provide a summary:\n\n{text}"


# ============================================================
# TRANSPORT CONFIGURATION
# ============================================================

def get_transport_config():
    """Determine transport configuration from multiple sources."""

    transport = "stdio"
    host = "localhost"
    port = 8000

    # Priority 1: Command-line arguments
    for arg in sys.argv[1:]:
        if arg.startswith("--transport="):
            transport = arg.split("=")[1].lower()
        elif arg.startswith("--host="):
            host = arg.split("=")[1]
        elif arg.startswith("--port="):
            port = int(arg.split("=")[1])

    # Priority 2: Environment variables (if CLI didn't set them)
    if "--transport=" not in " ".join(sys.argv):
        env_transport = os.environ.get("MCP_TRANSPORT", "")
        if env_transport:
            transport = env_transport.lower()

    # Priority 3: Config file
    config_file = "transport_config.json"
    if os.path.exists(config_file) and "--transport=" not in " ".join(sys.argv):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
            if "transport" in file_config:
                transport = file_config["transport"]
            if "host" in file_config:
                host = file_config["host"]
            if "port" in file_config:
                port = file_config["port"]
        except Exception:
            pass  # Ignore config file errors

    return transport, host, port


def print_help():
    """Print usage information."""
    print("Multi-Transport MCP Server")
    print("=" * 40)
    print()
    print("Usage:")
    print("  python mini_project_multi_transport_server.py [options]")
    print()
    print("Options:")
    print("  --transport=stdio   Use STDIO transport (default)")
    print("  --transport=sse     Use SSE transport")
    print("  --host=HOST         SSE host (default: localhost)")
    print("  --port=PORT         SSE port (default: 8000)")
    print("  --help              Show this help message")
    print()
    print("Environment Variables:")
    print("  MCP_TRANSPORT       Transport type (stdio or sse)")
    print("  MCP_HOST            SSE host")
    print("  MCP_PORT            SSE port")
    print()
    print("Config File:")
    print("  Create transport_config.json with:")
    print('  {"transport": "sse", "host": "localhost", "port": 8000}')


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Check for help flag
    if "--help" in sys.argv:
        print_help()
        sys.exit(0)

    # Get transport configuration
    transport, host, port = get_transport_config()

    # Save to env for tools to read
    os.environ["MCP_TRANSPORT"] = transport
    os.environ["MCP_HOST"] = host
    os.environ["MCP_PORT"] = str(port)

    # Validate
    if transport not in ["stdio", "sse"]:
        print(f"ERROR: Unknown transport '{transport}'. Use 'stdio' or 'sse'.")
        sys.exit(1)

    # Start the server
    print(f"Starting server with {transport.upper()} transport...")
    if transport == "sse":
        print(f"SSE endpoint: http://{host}:{port}/sse")

    server.run(transport=transport)
