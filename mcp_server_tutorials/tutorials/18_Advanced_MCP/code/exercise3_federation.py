"""
Exercise 3 - Build a Federation of 3 Servers
==============================================
TASK: Build a hub that federates 3 sub-servers.

You need to:
1. Create a hub with 3 sub-servers:
   - math_server: add, subtract, multiply, divide
   - text_server: uppercase, lowercase, reverse, length
   - data_server: store, retrieve, delete, list_keys
2. Route tool calls based on a prefix (e.g., "math.add")
3. Implement actual logic for each tool (not just simulation)
4. Handle errors (unknown server, unknown tool)

Hint: Look at example4_server_federation.py for the pattern.
Hint: Parse the prefix with split(".", 1) to get server and tool.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Define sub-server handlers
# ============================================================

# TODO: Create handler functions for math_server tools
# TODO: Create handler functions for text_server tools
# TODO: Create handler functions for data_server tools

# ============================================================
# Step 2: Create hub that routes calls
# ============================================================

mcp = FastMCP("FederationHub")

# TODO: Create route_call(command, args) tool
#   command format: "server.tool" (e.g., "math.add")
#   args: arguments as string

# TODO: Create list_all() tool to show available servers and tools

# ============================================================
# Step 3: Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 3: Federation of 3 Servers")
    print("=" * 50)
    print("TODO: Implement the sub-servers and hub routing!")
    print("Commands should use 'server.tool' format.")
    print("=" * 50)

    # TODO: Demo by calling math.add, text.uppercase, etc.
    # mcp.run()
