"""
Exercise 2 Solution - Debug Server
====================================
A server with debugging tools: echo, ping, server_status,
and list_capabilities. Useful for verifying MCP integration
with any AI application.
"""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the debug server
mcp = FastMCP("Debug Server")

# Track server state
_start_time = datetime.now()  # When the server started
_call_count = 0               # Total number of tool calls


# --- Tool: echo ---
@mcp.tool()
def echo(text: str) -> str:
    """Echo back the given text. Tests basic tool call functionality."""
    global _call_count
    _call_count += 1
    return f"Echo: {text}"


# --- Tool: ping ---
@mcp.tool()
def ping() -> str:
    """Return 'pong' with a timestamp. Tests server connectivity."""
    global _call_count
    _call_count += 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"pong (timestamp: {now})"


# --- Tool: server_status ---
@mcp.tool()
def server_status() -> str:
    """Return server uptime and total call count."""
    global _call_count
    _call_count += 1

    # Calculate uptime
    uptime = datetime.now() - _start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    return (
        f"Server Status:\n"
        f"  Name: Debug Server\n"
        f"  Started: {_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"  Uptime: {hours}h {minutes}m {seconds}s\n"
        f"  Total Tool Calls: {_call_count}\n"
        f"  Status: Running"
    )


# --- Tool: list_capabilities ---
@mcp.tool()
def list_capabilities() -> str:
    """List all available tools and their descriptions."""
    global _call_count
    _call_count += 1

    # Manually list the tools since we know them
    tools = [
        ("echo(text)", "Echo back text - test basic tool calls"),
        ("ping()", "Return pong with timestamp - test connectivity"),
        ("server_status()", "Show uptime and call count"),
        ("list_capabilities()", "List all tools (this one)"),
    ]

    lines = ["Available Tools:", ""]
    for name, desc in tools:
        lines.append(f"  - {name}: {desc}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Debug Server...")
    print("Tools: echo, ping, server_status, list_capabilities")
    mcp.run()
