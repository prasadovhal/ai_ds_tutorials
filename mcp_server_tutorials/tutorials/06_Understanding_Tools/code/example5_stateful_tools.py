"""
Example 5: Stateful Tools
==========================

This example shows tools that share state using module-level variables.
The shopping list and counter persist across tool calls within the
same server session.

Key concepts:
- Module-level lists and dicts to hold state
- Multiple tools reading and writing shared state
- State resets when the server restarts
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("StatefulToolsDemo")

# ---- Shared state: Shopping list ----
# This list persists across tool calls as long as the server is running.
shopping_list = []

# ---- Shared state: Counter ----
# A simple dictionary to hold a counter value.
counter = {"value": 0}


# ==================================================
#  Shopping List Tools
# ==================================================

# ---- Tool: Add an item to the shopping list ----
@server.tool()
def add_item(item: str) -> str:
    """Add an item to the shopping list."""
    shopping_list.append(item)
    return f"Added '{item}' to the list. Total items: {len(shopping_list)}."


# ---- Tool: List all items in the shopping list ----
@server.tool()
def list_items() -> str:
    """Show all items currently on the shopping list."""
    # Check if the list is empty
    if not shopping_list:
        return "The shopping list is empty."

    # Build a numbered list
    lines = []
    for i, item in enumerate(shopping_list, start=1):
        lines.append(f"  {i}. {item}")

    header = f"Shopping List ({len(shopping_list)} items):"
    return header + "\n" + "\n".join(lines)


# ---- Tool: Clear the shopping list ----
@server.tool()
def clear_items() -> str:
    """Remove all items from the shopping list."""
    count = len(shopping_list)
    shopping_list.clear()
    return f"Cleared {count} item(s) from the shopping list."


# ==================================================
#  Counter Tools
# ==================================================

# ---- Tool: Increment the counter ----
@server.tool()
def increment_counter(amount: int) -> str:
    """Increment the counter by the given amount (default 1)."""
    counter["value"] += amount
    return f"Counter incremented by {amount}. Current value: {counter['value']}."


# ---- Tool: Get the current counter value ----
@server.tool()
def get_counter() -> str:
    """Get the current value of the counter."""
    return f"Current counter value: {counter['value']}."


# ---- Tool: Reset the counter to zero ----
@server.tool()
def reset_counter() -> str:
    """Reset the counter back to zero."""
    old_value = counter["value"]
    counter["value"] = 0
    return f"Counter reset from {old_value} to 0."


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
