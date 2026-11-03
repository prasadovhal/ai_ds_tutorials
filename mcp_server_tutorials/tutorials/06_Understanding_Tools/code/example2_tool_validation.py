"""
Example 2: Tool Input Validation
=================================

This example shows how to validate inputs inside your tools.
Good tools check their inputs before processing and return
clear error messages when something is wrong.

Key concepts:
- Checking for division by zero
- Checking index bounds before accessing a list
- Returning helpful error messages instead of crashing
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("ValidationDemo")


# ---- Tool 1: Division with zero check ----
# We must check that the divisor is not zero before dividing.
@server.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b. Returns an error message if b is zero."""

    # Validate: b must not be zero
    if b == 0:
        return "Error: Cannot divide by zero. Please provide a non-zero divisor."

    # Safe to divide
    result = a / b
    return f"{a} / {b} = {result}"


# ---- Tool 2: List item access with bounds check ----
# We parse a comma-separated string into a list, then check
# that the requested index is within bounds.
@server.tool()
def get_item(items: str, index: int) -> str:
    """
    Get an item from a comma-separated list by index.
    Example: items="apple,banana,cherry", index=1 returns "banana".
    Returns an error if the index is out of bounds.
    """

    # Split the string into a list
    item_list = [item.strip() for item in items.split(",")]

    # Validate: check that the index is within bounds
    if index < 0 or index >= len(item_list):
        return (
            f"Error: Index {index} is out of bounds. "
            f"Valid range is 0 to {len(item_list) - 1}. "
            f"The list has {len(item_list)} items: {item_list}"
        )

    # Safe to access the item
    selected = item_list[index]
    return f"Item at index {index}: {selected}"


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
