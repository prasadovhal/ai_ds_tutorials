"""
Exercise 2: Text Tools Server (Stub)
======================================

YOUR TASK:
Build an MCP server with 5 text processing tools:
  1. title_case(text)            - Convert text to Title Case
  2. snake_case(text)            - Convert text to snake_case
  3. word_frequency(text)        - Count how often each word appears
  4. truncate(text, max_length)  - Shorten text to max_length with "..."
  5. pad(text, width, char)      - Pad text to a given width with a character

REQUIREMENTS:
- title_case: use Python's built-in .title() method
- snake_case: lowercase, replace spaces with underscores
- word_frequency: return each word and its count
- truncate: if text is longer than max_length, cut and add "..."
- pad: center the text within the given width using the pad character

HINTS:
- str.title() converts to title case
- str.lower().replace(" ", "_") gives snake_case
- Use a dict to count word frequencies
- str.center(width, char) pads a string
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("TextToolsExercise")


# TODO: Implement the 5 text tools below


# Tool 1: title_case
# @server.tool()
# def title_case(...) -> str:
#     ...


# Tool 2: snake_case
# @server.tool()
# def snake_case(...) -> str:
#     ...


# Tool 3: word_frequency
# @server.tool()
# def word_frequency(...) -> str:
#     ...


# Tool 4: truncate
# @server.tool()
# def truncate(...) -> str:
#     ...


# Tool 5: pad
# @server.tool()
# def pad(...) -> str:
#     ...


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
