"""
Example 3: Multiple String Tools
=================================

This example shows a server with 6 string manipulation tools.
Having multiple related tools on one server is a common pattern --
it groups related functionality together.

Key concepts:
- Registering many tools on a single server
- Each tool does one small, focused thing
- Tools are simple wrappers around Python string methods
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("StringToolsDemo")


# ---- Tool 1: Convert to uppercase ----
@server.tool()
def uppercase(text: str) -> str:
    """Convert text to UPPERCASE."""
    return text.upper()


# ---- Tool 2: Convert to lowercase ----
@server.tool()
def lowercase(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()


# ---- Tool 3: Reverse a string ----
@server.tool()
def reverse(text: str) -> str:
    """Reverse the characters in the text."""
    # Python slice notation: [::-1] reverses a string
    return text[::-1]


# ---- Tool 4: Count words ----
@server.tool()
def count_words(text: str) -> str:
    """Count the number of words in the text."""
    # split() with no args splits on any whitespace
    words = text.split()
    count = len(words)
    return f"The text has {count} word(s)."


# ---- Tool 5: Replace text ----
@server.tool()
def replace_text(text: str, old: str, new: str) -> str:
    """Replace all occurrences of 'old' with 'new' in the text."""
    result = text.replace(old, new)
    return result


# ---- Tool 6: Count characters ----
@server.tool()
def char_count(text: str) -> str:
    """Count the total number of characters in the text (including spaces)."""
    count = len(text)
    return f"The text has {count} character(s)."


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
