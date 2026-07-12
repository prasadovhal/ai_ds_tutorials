"""
Example 1 - Claude Desktop MCP Configuration Generator
======================================================
Generates the JSON configuration needed to connect an MCP server
to Claude Desktop. The config file tells Claude Desktop how to
start and communicate with your MCP server.
"""

import json
import os


def generate_claude_config(server_path, server_name="my-server"):
    """Generate Claude Desktop MCP configuration.

    Args:
        server_path: Path to the Python server file
        server_name: Name to identify the server in Claude Desktop

    Returns:
        The configuration dictionary
    """
    # Claude Desktop config structure
    # Each server needs a command (how to run it) and args (what to pass)
    config = {
        "mcpServers": {
            server_name: {
                "command": "python",
                "args": [server_path]
            }
        }
    }

    # Claude Desktop looks for config in this location
    config_path = os.path.expanduser("~/.config/claude/claude_desktop_config.json")

    # Print the config so user can copy it
    print("=" * 60)
    print("Claude Desktop MCP Configuration")
    print("=" * 60)
    print(f"\nServer Name: {server_name}")
    print(f"Server Path: {server_path}")
    print(f"\nConfiguration JSON:")
    print(json.dumps(config, indent=2))
    print(f"\nSave this to: {config_path}")
    print(f"\nOn Windows, the path is typically:")
    print(f"  %APPDATA%\\Claude\\claude_desktop_config.json")
    print(f"\nOn macOS:")
    print(f"  ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("=" * 60)

    return config


if __name__ == "__main__":
    # Generate a sample config for a server file
    generate_claude_config("src/server.py", "my-mcp-server")
