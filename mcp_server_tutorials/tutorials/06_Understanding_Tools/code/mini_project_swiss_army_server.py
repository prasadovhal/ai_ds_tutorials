"""
Mini Project: Swiss Army Server
================================

A single MCP server packed with 15 useful tools organized into
four categories: String, Math, Data, and Utility.

This demonstrates how a real-world MCP server might bundle
many related tools into one convenient package.

Categories:
  STRING (4 tools): upper, lower, reverse, count_chars
  MATH   (4 tools): add, subtract, multiply, divide
  DATA   (3 tools): sort_list, filter_list, unique_list
  UTILITY(4 tools): generate_uuid, timestamp, random_number, coin_flip
"""

import uuid
import random
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("SwissArmyServer")


# ==================================================
#  STRING TOOLS
# ==================================================

@server.tool()
def upper(text: str) -> str:
    """Convert text to UPPERCASE."""
    return text.upper()


@server.tool()
def lower(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()


@server.tool()
def reverse(text: str) -> str:
    """Reverse the characters in the text."""
    return text[::-1]


@server.tool()
def count_chars(text: str) -> str:
    """Count the number of characters in the text."""
    total = len(text)
    no_spaces = len(text.replace(" ", ""))
    return f"Total characters: {total}, Without spaces: {no_spaces}"


# ==================================================
#  MATH TOOLS
# ==================================================

@server.tool()
def add(a: float, b: float) -> str:
    """Add two numbers."""
    result = a + b
    return f"{a} + {b} = {result}"


@server.tool()
def subtract(a: float, b: float) -> str:
    """Subtract b from a."""
    result = a - b
    return f"{a} - {b} = {result}"


@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers."""
    result = a * b
    return f"{a} * {b} = {result}"


@server.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b. Returns an error if b is zero."""
    if b == 0:
        return "Error: Cannot divide by zero."
    result = a / b
    return f"{a} / {b} = {result}"


# ==================================================
#  DATA TOOLS
# ==================================================

@server.tool()
def sort_list(items: str) -> str:
    """
    Sort a comma-separated list of items alphabetically.
    Example input: "banana,apple,cherry"
    """
    # Split, strip whitespace, sort
    item_list = [item.strip() for item in items.split(",")]
    sorted_items = sorted(item_list)
    return "Sorted: " + ", ".join(sorted_items)


@server.tool()
def filter_list(items: str, keyword: str) -> str:
    """
    Filter a comma-separated list, keeping only items that contain the keyword.
    Example: items="apple,banana,apricot", keyword="ap" returns "apple, apricot"
    """
    item_list = [item.strip() for item in items.split(",")]
    # Keep items that contain the keyword (case-insensitive)
    matched = [item for item in item_list if keyword.lower() in item.lower()]

    if not matched:
        return f"No items contain '{keyword}'."

    return f"Matched ({len(matched)}): " + ", ".join(matched)


@server.tool()
def unique_list(items: str) -> str:
    """
    Remove duplicates from a comma-separated list while preserving order.
    Example: items="a,b,a,c,b" returns "a, b, c"
    """
    item_list = [item.strip() for item in items.split(",")]
    # Use dict.fromkeys to preserve insertion order while removing duplicates
    unique_items = list(dict.fromkeys(item_list))

    removed = len(item_list) - len(unique_items)
    return f"Unique items: {', '.join(unique_items)} ({removed} duplicate(s) removed)"


# ==================================================
#  UTILITY TOOLS
# ==================================================

@server.tool()
def generate_uuid() -> str:
    """Generate a new random UUID (version 4)."""
    new_uuid = str(uuid.uuid4())
    return f"Generated UUID: {new_uuid}"


@server.tool()
def timestamp() -> str:
    """Get the current date and time as a formatted timestamp."""
    now = datetime.now()
    # ISO format: 2024-01-15T14:30:00
    iso = now.isoformat()
    # Human-readable format
    human = now.strftime("%B %d, %Y at %I:%M:%S %p")
    return f"ISO format: {iso}\nHuman readable: {human}"


@server.tool()
def random_number(low: int, high: int) -> str:
    """Generate a random integer between low and high (inclusive)."""
    # Validate that low <= high
    if low > high:
        return f"Error: low ({low}) must be less than or equal to high ({high})."

    result = random.randint(low, high)
    return f"Random number between {low} and {high}: {result}"


@server.tool()
def coin_flip() -> str:
    """Flip a coin and return Heads or Tails."""
    result = random.choice(["Heads", "Tails"])
    return f"Coin flip result: {result}"


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
