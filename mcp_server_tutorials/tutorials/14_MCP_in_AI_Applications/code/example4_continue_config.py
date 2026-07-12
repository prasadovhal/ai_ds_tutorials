"""
Example 4 - Continue.dev MCP Configuration Generator
====================================================
Generates the Continue.dev config (~/.continue/config.json) with
the mcpServers section. Continue.dev is an open-source AI coding
assistant that supports MCP server integration.
"""

import json
import os


def generate_continue_config(server_path, server_name="my-server"):
    """Generate Continue.dev config.json with MCP section.

    Args:
        server_path: Path to the Python server file
        server_name: Name to identify the server

    Returns:
        The configuration dictionary
    """
    # Continue.dev uses ~/.continue/config.json
    # The mcpServers section is added to the existing config
    config = {
        "mcpServers": [
            {
                "name": server_name,
                "command": "python",
                "args": [server_path]
            }
        ]
    }

    # Continue.dev config location
    config_path = os.path.expanduser("~/.continue/config.json")

    # Print the config for the user
    print("=" * 60)
    print("Continue.dev MCP Configuration")
    print("=" * 60)
    print(f"\nServer Name: {server_name}")
    print(f"Server Path: {server_path}")
    print(f"\nAdd this section to: {config_path}")
    print(f"\nMCP Servers JSON (add to your existing config.json):")
    print(json.dumps(config, indent=2))
    print(f"\nSteps:")
    print(f"  1. Open ~/.continue/config.json")
    print(f"  2. Add the 'mcpServers' section to your config")
    print(f"  3. Save and reload your editor")
    print(f"  4. Continue.dev will auto-discover the MCP tools")
    print("=" * 60)

    return config


if __name__ == "__main__":
    # Generate a sample Continue.dev config
    generate_continue_config("src/server.py", "my-mcp-server")
