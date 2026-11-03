"""
Text Processor MCP Server
==========================
Provides tools for common text processing operations:
word count, character count, find & replace, reverse, and dedup lines.
"""

# Import FastMCP
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
server = FastMCP("Text Processor Server")


# --- Tool: Count words in text ---
@server.tool()
def word_count(text: str) -> str:
    """Count the number of words in the given text."""
    words = text.split()
    return f"Word count: {len(words)}"


# --- Tool: Count characters in text ---
@server.tool()
def char_count(text: str, include_spaces: bool = True) -> str:
    """Count characters in text. Optionally exclude spaces."""
    if include_spaces:
        count = len(text)
        return f"Character count (with spaces): {count}"
    else:
        count = len(text.replace(" ", ""))
        return f"Character count (without spaces): {count}"


# --- Tool: Find and replace text ---
@server.tool()
def find_replace(text: str, find: str, replace: str) -> str:
    """Find all occurrences of a string and replace them."""
    # Count occurrences first
    count = text.count(find)

    if count == 0:
        return f"'{find}' not found in the text."

    # Perform the replacement
    result = text.replace(find, replace)
    return f"Replaced {count} occurrence(s) of '{find}' with '{replace}':\n\n{result}"


# --- Tool: Reverse text ---
@server.tool()
def reverse_text(text: str) -> str:
    """Reverse the given text."""
    reversed_text = text[::-1]
    return f"Reversed text:\n{reversed_text}"


# --- Tool: Remove duplicate lines ---
@server.tool()
def remove_duplicate_lines(text: str) -> str:
    """Remove duplicate lines from text while preserving order."""
    lines = text.splitlines()
    seen = set()
    unique_lines = []

    for line in lines:
        # Use stripped version for comparison but keep original
        if line.strip() not in seen:
            seen.add(line.strip())
            unique_lines.append(line)

    removed_count = len(lines) - len(unique_lines)
    result = "\n".join(unique_lines)

    return f"Removed {removed_count} duplicate line(s):\n\n{result}"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
