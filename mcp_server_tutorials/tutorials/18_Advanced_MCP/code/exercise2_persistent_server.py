"""
Exercise 2 - Build a Server that Saves State to Disk
======================================================
TASK: Build an MCP server that persists its state to a JSON file.

You need to:
1. Create a FastMCP server with these tools:
   - add_item(name, description): Add an item to the list
   - list_items(): Show all items
   - remove_item(name): Remove an item by name
2. Load state from state.json when the server starts
3. Save state to state.json after every operation
4. The state should survive server restarts

Hint: Use json.load() and json.dump() for reading/writing JSON.
Hint: Handle the case where state.json doesn't exist yet.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: State persistence functions
# ============================================================

# TODO: Create load_state() function that reads from state.json
# TODO: Create save_state(data) function that writes to state.json

# ============================================================
# Step 2: Create MCP server with persistent tools
# ============================================================

mcp = FastMCP("PersistentServer")

# TODO: Create add_item(name, description) tool
# TODO: Create list_items() tool
# TODO: Create remove_item(name) tool

# ============================================================
# Step 3: Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 2: Persistent Server")
    print("=" * 50)
    print("TODO: Implement state persistence and tools above!")
    print("Data should survive server restarts via state.json.")
    print("=" * 50)

    # TODO: Demo by adding items, listing, removing
    # mcp.run()
