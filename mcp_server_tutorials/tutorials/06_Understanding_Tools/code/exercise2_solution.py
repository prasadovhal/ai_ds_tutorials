"""
Exercise 2: Text Tools Server (Solution)
==========================================

This is the complete solution for the text tools exercise.
It implements 5 text processing tools.
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("TextToolsSolution")


# ---- Tool 1: Convert to Title Case ----
@server.tool()
def title_case(text: str) -> str:
    """Convert text to Title Case (capitalize the first letter of each word)."""
    result = text.title()
    return f"Title case: {result}"


# ---- Tool 2: Convert to snake_case ----
@server.tool()
def snake_case(text: str) -> str:
    """Convert text to snake_case (lowercase with underscores)."""
    # Lowercase everything, then replace spaces with underscores
    result = text.lower().replace(" ", "_")
    return f"Snake case: {result}"


# ---- Tool 3: Word frequency ----
@server.tool()
def word_frequency(text: str) -> str:
    """Count how often each word appears in the text."""
    # Split text into words (lowercase for consistent counting)
    words = text.lower().split()

    # Count each word using a dictionary
    freq = {}
    for word in words:
        if word in freq:
            freq[word] += 1
        else:
            freq[word] = 1

    # Build the output
    lines = [f"Word frequencies ({len(freq)} unique words):"]
    for word, count in sorted(freq.items()):
        lines.append(f"  '{word}': {count}")

    return "\n".join(lines)


# ---- Tool 4: Truncate text ----
@server.tool()
def truncate(text: str, max_length: int) -> str:
    """Shorten text to max_length characters, adding '...' if truncated."""
    # If the text is already short enough, return it as-is
    if len(text) <= max_length:
        return f"Text is already within {max_length} characters: {text}"

    # Truncate and add ellipsis
    truncated = text[:max_length] + "..."
    return f"Truncated ({max_length} chars): {truncated}"


# ---- Tool 5: Pad text ----
@server.tool()
def pad(text: str, width: int, char: str) -> str:
    """Center the text within the given width, padded with the specified character."""
    # Use only the first character if multiple were provided
    pad_char = char[0] if char else " "

    # Center the text
    result = text.center(width, pad_char)
    return f"Padded: '{result}'"


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
