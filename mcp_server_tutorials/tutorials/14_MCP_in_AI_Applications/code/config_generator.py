"""
Config Generator - Generate MCP Configs for ALL AI Apps
========================================================
Takes a server path as input and generates configuration files
for all supported AI applications: Claude Desktop, VS Code,
Cursor, and Continue.dev. Prints all configs so you can copy
them to the right location.
"""

import json
import os
import sys


def generate_claude_desktop_config(server_path, server_name):
    """Generate Claude Desktop configuration."""
    return {
        "mcpServers": {
            server_name: {
                "command": "python",
                "args": [server_path]
            }
        }
    }


def generate_vscode_config(server_path, server_name):
    """Generate VS Code (GitHub Copilot Chat) configuration."""
    return {
        "github.copilot.chat.mcp": {
            "servers": {
                server_name: {
                    "command": "python",
                    "args": [server_path],
                    "env": {}
                }
            }
        }
    }


def generate_cursor_config(server_path, server_name):
    """Generate Cursor configuration."""
    return {
        "mcpServers": {
            server_name: {
                "command": "python",
                "args": [server_path]
            }
        }
    }


def generate_continue_config(server_path, server_name):
    """Generate Continue.dev configuration."""
    return {
        "mcpServers": [
            {
                "name": server_name,
                "command": "python",
                "args": [server_path]
            }
        ]
    }


def generate_all_configs(server_path, server_name="my-server"):
    """Generate and print configs for ALL supported AI applications.

    Args:
        server_path: Path to the Python MCP server file
        server_name: Name to identify the server
    """
    # Define all apps with their config generators and file paths
    apps = [
        {
            "name": "Claude Desktop",
            "config": generate_claude_desktop_config(server_path, server_name),
            "path": "~/.config/claude/claude_desktop_config.json (Linux)\n"
                    "    ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)\n"
                    "    %APPDATA%\\Claude\\claude_desktop_config.json (Windows)"
        },
        {
            "name": "VS Code (GitHub Copilot Chat)",
            "config": generate_vscode_config(server_path, server_name),
            "path": ".vscode/settings.json (in project root)"
        },
        {
            "name": "Cursor",
            "config": generate_cursor_config(server_path, server_name),
            "path": ".cursor/mcp.json (in project root)"
        },
        {
            "name": "Continue.dev",
            "config": generate_continue_config(server_path, server_name),
            "path": "~/.continue/config.json"
        }
    ]

    # Print header
    print("=" * 70)
    print(f"MCP Configuration Generator")
    print(f"Server: {server_name} ({server_path})")
    print("=" * 70)

    # Print each app's config
    for app in apps:
        print(f"\n{'─' * 70}")
        print(f"  {app['name']}")
        print(f"{'─' * 70}")
        print(f"\n  Config file: {app['path']}")
        print(f"\n  JSON:")
        # Indent the JSON output for readability
        config_json = json.dumps(app["config"], indent=2)
        for line in config_json.split("\n"):
            print(f"    {line}")

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"Generated configs for {len(apps)} AI applications.")
    print(f"Copy the JSON for your app and paste it into the config file.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    # Allow server path from command line, default to "src/server.py"
    if len(sys.argv) > 1:
        path = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else "my-server"
    else:
        path = "src/server.py"
        name = "my-mcp-server"

    generate_all_configs(path, name)
