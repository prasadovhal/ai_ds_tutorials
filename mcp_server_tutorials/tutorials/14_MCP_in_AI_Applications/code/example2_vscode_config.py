"""
Example 2 - VS Code MCP Configuration Generator
================================================
Generates .vscode/settings.json with the github.copilot.chat.mcp
section configured for your MCP server. This allows GitHub Copilot
Chat in VS Code to use your MCP server's tools.
"""

import json
import os


def generate_vscode_config(server_path, server_name="my-server"):
    """Generate VS Code settings.json with MCP configuration.

    Args:
        server_path: Path to the Python server file
        server_name: Name to identify the server

    Returns:
        The configuration dictionary
    """
    # VS Code uses github.copilot.chat.mcp section in settings.json
    # The "servers" key maps server names to their launch config
    config = {
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

    # The config goes in .vscode/settings.json in your project
    config_path = os.path.join(".vscode", "settings.json")

    # Print the config for the user
    print("=" * 60)
    print("VS Code MCP Configuration (GitHub Copilot Chat)")
    print("=" * 60)
    print(f"\nServer Name: {server_name}")
    print(f"Server Path: {server_path}")
    print(f"\nAdd this to: {config_path}")
    print(f"\nConfiguration JSON:")
    print(json.dumps(config, indent=2))
    print(f"\nSteps:")
    print(f"  1. Create .vscode/ folder in your project root")
    print(f"  2. Add this to .vscode/settings.json")
    print(f"  3. Reload VS Code window (Ctrl+Shift+P > Reload Window)")
    print(f"  4. Open Copilot Chat and use your MCP tools")
    print("=" * 60)

    return config


if __name__ == "__main__":
    # Generate a sample VS Code config
    generate_vscode_config("src/server.py", "my-mcp-server")
