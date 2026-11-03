"""
Exercise 3 - Shopping List Server (Stub)
==========================================
GOAL: Build an MCP server to manage a shopping list.

REQUIREMENTS:
  1. add_item(item, quantity, category) - Add item to list
  2. remove_item(item) - Remove item from list
  3. list_items() - Show all items grouped by category
  4. mark_bought(item) - Mark an item as purchased
  5. shopping_summary() - Show bought vs remaining items

HINTS:
  - Store data in shopping_list.json
  - Each item has: name, quantity, category, bought (bool)
  - Group items by category when listing (e.g., 'dairy', 'produce')
  - Summary should show total items, bought, remaining, and cost if tracked
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the server
# mcp = FastMCP("???")

# Step 2: Define load/save functions for shopping_list.json
# def load_shopping_list():
#     pass

# Step 3: Implement add_item tool
# @mcp.tool()
# def add_item(item: str, quantity: int, category: str) -> str:
#     pass

# Step 4: Implement remove_item tool
# @mcp.tool()
# def remove_item(item: str) -> str:
#     pass

# Step 5: Implement list_items tool
# @mcp.tool()
# def list_items() -> str:
#     pass

# Step 6: Implement mark_bought tool
# @mcp.tool()
# def mark_bought(item: str) -> str:
#     pass

# Step 7: Implement shopping_summary tool
# @mcp.tool()
# def shopping_summary() -> str:
#     pass


if __name__ == "__main__":
    print("Exercise 3: Build your Shopping List Server!")
    print("Edit this file to complete the exercise.")
