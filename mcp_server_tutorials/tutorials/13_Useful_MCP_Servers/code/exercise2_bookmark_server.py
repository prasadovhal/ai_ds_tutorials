"""
Exercise 2: Bookmark Manager MCP Server (Stub)
================================================
YOUR TASK: Build a bookmark manager that stores bookmarks in a JSON file.

Requirements:
1. Store bookmarks in a JSON file with url, title, category, and timestamp
2. Implement these tools:
   - add_bookmark(url, title, category) -> save a bookmark
   - list_bookmarks(category=None) -> list all or filter by category
   - search_bookmarks(keyword) -> search by keyword in title/url
   - delete_bookmark(url) -> remove a bookmark

Hints:
- Use a JSON file to persist bookmarks between sessions
- Each bookmark should have: url, title, category, added_at
- Use datetime.now().isoformat() for timestamps

See exercise2_solution.py for the complete solution.
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
server = FastMCP("Bookmark Manager")

# TODO: Define the path for the bookmarks JSON file
# BOOKMARKS_FILE = ...

# TODO: Create helper functions to load/save bookmarks

# TODO: Implement add_bookmark tool

# TODO: Implement list_bookmarks tool

# TODO: Implement search_bookmarks tool

# TODO: Implement delete_bookmark tool


if __name__ == "__main__":
    server.run()
