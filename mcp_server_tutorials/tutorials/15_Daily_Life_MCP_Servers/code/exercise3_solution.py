"""
Exercise 3 Solution - Shopping List Server
============================================
Manage a shopping list with categories and purchase tracking.

Tools:
  - add_item(item, quantity, category)
  - remove_item(item)
  - list_items()
  - mark_bought(item)
  - shopping_summary()

Data is stored in shopping_list.json.
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Shopping List")

# Path to the JSON data file
DATA_FILE = "shopping_list.json"


def load_shopping_list():
    """Load shopping list from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_shopping_list(items):
    """Save shopping list to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(items, f, indent=2)


# --- Tool: add_item ---
@mcp.tool()
def add_item(item: str, quantity: int, category: str) -> str:
    """Add an item to the shopping list.

    Args:
        item: Name of the item (e.g., 'Milk', 'Bread')
        quantity: How many to buy (e.g., 2)
        category: Category like 'dairy', 'produce', 'bakery', 'snacks'
    """
    items = load_shopping_list()

    # Check if item already exists
    for existing in items:
        if existing["item"].lower() == item.lower():
            # Update quantity instead of adding duplicate
            existing["quantity"] += quantity
            save_shopping_list(items)
            return (
                f"Updated '{item}' quantity to {existing['quantity']} "
                f"(added {quantity} more)"
            )

    # Create new item entry
    entry = {
        "item": item,
        "quantity": quantity,
        "category": category.lower(),
        "bought": False,
        "added": datetime.now().strftime("%Y-%m-%d")
    }

    items.append(entry)
    save_shopping_list(items)

    return f"Added to shopping list: {item} x{quantity} [{category}]"


# --- Tool: remove_item ---
@mcp.tool()
def remove_item(item: str) -> str:
    """Remove an item from the shopping list.

    Args:
        item: Name of the item to remove
    """
    items = load_shopping_list()

    # Find and remove the item (case-insensitive)
    for i, entry in enumerate(items):
        if entry["item"].lower() == item.lower():
            removed = items.pop(i)
            save_shopping_list(items)
            return f"Removed '{removed['item']}' from shopping list."

    return f"Item '{item}' not found on the list."


# --- Tool: list_items ---
@mcp.tool()
def list_items() -> str:
    """Show all items on the shopping list, grouped by category."""
    items = load_shopping_list()

    if not items:
        return "Shopping list is empty. Use add_item to start!"

    # Group items by category
    categories = {}
    for entry in items:
        cat = entry["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)

    # Build the list display
    remaining = sum(1 for i in items if not i["bought"])
    bought = sum(1 for i in items if i["bought"])

    lines = [f"Shopping List ({remaining} to buy, {bought} bought):", ""]

    for cat, cat_items in sorted(categories.items()):
        lines.append(f"  [{cat.upper()}]")
        for entry in cat_items:
            status = "x" if entry["bought"] else " "
            lines.append(f"    [{status}] {entry['item']} x{entry['quantity']}")
        lines.append("")

    return "\n".join(lines)


# --- Tool: mark_bought ---
@mcp.tool()
def mark_bought(item: str) -> str:
    """Mark an item as bought/purchased.

    Args:
        item: Name of the item to mark as bought
    """
    items = load_shopping_list()

    for entry in items:
        if entry["item"].lower() == item.lower():
            if entry["bought"]:
                return f"'{entry['item']}' is already marked as bought."

            entry["bought"] = True
            entry["bought_date"] = datetime.now().strftime("%Y-%m-%d")
            save_shopping_list(items)

            # Count remaining
            remaining = sum(1 for i in items if not i["bought"])
            return (
                f"Marked '{entry['item']}' as bought!\n"
                f"  {remaining} item(s) remaining on the list."
            )

    return f"Item '{item}' not found on the list."


# --- Tool: shopping_summary ---
@mcp.tool()
def shopping_summary() -> str:
    """Show a summary of the shopping list: bought vs remaining."""
    items = load_shopping_list()

    if not items:
        return "Shopping list is empty."

    # Calculate statistics
    total = len(items)
    bought = [i for i in items if i["bought"]]
    remaining = [i for i in items if not i["bought"]]

    bought_count = len(bought)
    remaining_count = len(remaining)
    pct = (bought_count / total * 100) if total > 0 else 0

    # Count by category
    categories_remaining = {}
    for entry in remaining:
        cat = entry["category"]
        categories_remaining[cat] = categories_remaining.get(cat, 0) + 1

    # Build summary
    lines = ["Shopping Summary:", ""]
    lines.append(f"  Total Items:     {total}")
    lines.append(f"  Bought:          {bought_count}")
    lines.append(f"  Remaining:       {remaining_count}")

    # Progress bar
    bar_filled = int(pct / 10)
    bar = "[" + "#" * bar_filled + "-" * (10 - bar_filled) + "]"
    lines.append(f"  Progress:        {bar} {pct:.0f}%")

    if remaining:
        lines.append(f"\n  Still Need to Buy:")
        for entry in remaining:
            lines.append(f"    - {entry['item']} x{entry['quantity']} [{entry['category']}]")

    if categories_remaining:
        lines.append(f"\n  Remaining by Category:")
        for cat, count in sorted(categories_remaining.items()):
            lines.append(f"    {cat}: {count} item(s)")

    if bought_count == total:
        lines.append(f"\n  All items purchased! Shopping complete!")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Shopping List Server...")
    print("Tools: add_item, remove_item, list_items, mark_bought, shopping_summary")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
