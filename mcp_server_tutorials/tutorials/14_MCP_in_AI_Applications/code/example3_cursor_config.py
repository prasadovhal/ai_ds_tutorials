"""
Example 3 - Cursor MCP Configuration Generator
===============================================
Generates .cursor/mcp.json config format for integrating an MCP
server with the Cursor AI code editor. Cursor uses its own config
file format to discover and connect to MCP servers.
"""

import json
import os


def generate_cursor_config(server_path, server_name="my-server"):
    """Generate Cursor .cursor/mcp.json configuration.

    Args:
        server_path: Path to the Python server file
        server_name: Name to identify the server

    Returns:
        The configuration dictionary
    """
    # Cursor uses .cursor/mcp.json in the project root
    # Format is similar to Claude Desktop but in a different location
    config = {
        "mcpServers": {
            server_name: {
                "command": "python",
                "args": [server_path]
            }
        }
    }

    # Config file location
    config_path = os.path.join(".cursor", "mcp.json")

    # Print the config for the user
    print("=" * 60)
    print("Cursor MCP Configuration")
    print("=" * 60)
    print(f"\nServer Name: {server_name}")
    print(f"Server Path: {server_path}")
    print(f"\nSave this to: {config_path}")
    print(f"\nConfiguration JSON:")
    print(json.dumps(config, indent=2))
    print(f"\nSteps:")
    print(f"  1. Create .cursor/ folder in your project root")
    print(f"  2. Save this as .cursor/mcp.json")
    print(f"  3. Restart Cursor to pick up the new server")
    print(f"  4. The server tools will appear in Cursor's AI chat")
    print("=" * 60)

    return config


if __name__ == "__main__":
    # Generate a sample Cursor config
    generate_cursor_config("src/server.py", "my-mcp-server")
