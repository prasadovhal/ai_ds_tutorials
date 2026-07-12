"""
Exercise 2 Solution: Bookmark Manager MCP Server
==================================================
A bookmark manager that stores bookmarks in a JSON file.
"""

from mcp.server.fastmcp import FastMCP
import json
import os
from datetime import datetime

# Create the MCP server instance
server = FastMCP("Bookmark Manager")

# Path to the bookmarks JSON file
BOOKMARKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.json")


def _load_bookmarks() -> list:
    """Load bookmarks from the JSON file."""
    if not os.path.exists(BOOKMARKS_FILE):
        return []
    with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_bookmarks(bookmarks: list):
    """Save bookmarks to the JSON file."""
    with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)


# --- Tool: Add a bookmark ---
@server.tool()
def add_bookmark(url: str, title: str, category: str = "general") -> str:
    """Add a new bookmark with a URL, title, and category."""
    bookmarks = _load_bookmarks()

    # Check for duplicate URLs
    for bm in bookmarks:
        if bm["url"] == url:
            return f"Bookmark for '{url}' already exists."

    # Create the bookmark
    bookmark = {
        "url": url,
        "title": title,
        "category": category,
        "added_at": datetime.now().isoformat(),
    }

    bookmarks.append(bookmark)
    _save_bookmarks(bookmarks)
    return f"Bookmark added: '{title}' ({url}) in category '{category}'"


# --- Tool: List bookmarks ---
@server.tool()
def list_bookmarks(category: str = "") -> str:
    """List all bookmarks, optionally filtered by category."""
    bookmarks = _load_bookmarks()

    if not bookmarks:
        return "No bookmarks saved yet."

    # Filter by category if provided
    if category:
        bookmarks = [b for b in bookmarks if b["category"].lower() == category.lower()]
        if not bookmarks:
            return f"No bookmarks in category '{category}'."

    result = f"Bookmarks ({len(bookmarks)}):\n\n"
    for bm in bookmarks:
        result += f"  [{bm['category']}] {bm['title']}\n    {bm['url']}\n\n"

    return result.strip()


# --- Tool: Search bookmarks ---
@server.tool()
def search_bookmarks(keyword: str) -> str:
    """Search bookmarks by keyword in title or URL."""
    bookmarks = _load_bookmarks()
    keyword_lower = keyword.lower()

    matches = [
        b for b in bookmarks
        if keyword_lower in b["title"].lower() or keyword_lower in b["url"].lower()
    ]

    if not matches:
        return f"No bookmarks matching '{keyword}'."

    result = f"Search results for '{keyword}' ({len(matches)} found):\n\n"
    for bm in matches:
        result += f"  [{bm['category']}] {bm['title']}\n    {bm['url']}\n\n"

    return result.strip()


# --- Tool: Delete a bookmark ---
@server.tool()
def delete_bookmark(url: str) -> str:
    """Delete a bookmark by its URL."""
    bookmarks = _load_bookmarks()

    for i, bm in enumerate(bookmarks):
        if bm["url"] == url:
            removed = bookmarks.pop(i)
            _save_bookmarks(bookmarks)
            return f"Deleted bookmark: '{removed['title']}' ({url})"

    return f"No bookmark found with URL '{url}'."


if __name__ == "__main__":
    server.run()
