"""
Exercise 2 Solution - Persistent MCP Server
=============================================
An MCP server that saves its state to a JSON file.
State survives server restarts.
"""

import json
import os
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: State file path (same directory as this script)
# ============================================================

STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "state.json"
)

# ============================================================
# Step 2: State persistence functions
# ============================================================

def load_state() -> dict:
    """
    Load state from state.json.
    Returns empty dict if file doesn't exist.
    """
    if not os.path.exists(STATE_FILE):
        # First run -- no state file yet
        return {"items": {}}

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # File is corrupted or unreadable -- start fresh
        return {"items": {}}


def save_state(data: dict) -> None:
    """
    Save state to state.json.
    Writes with indentation for readability.
    """
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# Step 3: MCP server with persistent tools
# ============================================================

mcp = FastMCP("PersistentServer")


@mcp.tool()
def add_item(name: str, description: str = "") -> str:
    """
    Add an item to the persistent list.
    The item is saved to disk immediately.

    Args:
        name: Name of the item (used as key).
        description: Optional description.
    """
    # Load current state
    state = load_state()

    # Check for duplicates
    if name in state["items"]:
        return f"Error: Item '{name}' already exists. Remove it first."

    # Add the item
    state["items"][name] = {
        "description": description,
    }

    # Save to disk
    save_state(state)
    return f"Added '{name}' to the list. Total items: {len(state['items'])}"


@mcp.tool()
def list_items() -> str:
    """
    List all items in the persistent store.
    """
    state = load_state()
    items = state["items"]

    if not items:
        return "No items in the list. Use add_item to add some."

    lines = [f"Items ({len(items)} total):"]
    for i, (name, info) in enumerate(items.items(), 1):
        desc = info.get("description", "")
        if desc:
            lines.append(f"  {i}. {name} - {desc}")
        else:
            lines.append(f"  {i}. {name}")

    lines.append(f"\nState file: {STATE_FILE}")
    return "\n".join(lines)


@mcp.tool()
def remove_item(name: str) -> str:
    """
    Remove an item from the persistent list by name.
    Changes are saved to disk immediately.
    """
    state = load_state()

    if name not in state["items"]:
        available = ", ".join(state["items"].keys()) if state["items"] else "none"
        return f"Error: Item '{name}' not found. Available: {available}"

    # Remove the item
    del state["items"][name]

    # Save to disk
    save_state(state)
    return f"Removed '{name}'. Remaining items: {len(state['items'])}"


# ============================================================
# Step 4: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 2 Solution: Persistent Server")
    print("=" * 50)

    # Demo: add items
    print("\n--- Adding items ---")
    print(add_item("laptop", "Work laptop, 16GB RAM"))
    print(add_item("keyboard", "Mechanical keyboard"))
    print(add_item("monitor", "27 inch 4K display"))

    # List items
    print("\n--- Listing items ---")
    print(list_items())

    # Remove an item
    print("\n--- Removing item ---")
    print(remove_item("keyboard"))

    # List again
    print("\n--- After removal ---")
    print(list_items())

    # Clean up demo state file
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f"\n(Cleaned up demo state file)")

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
