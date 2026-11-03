"""
Bookmark Manager MCP Server
==============================
Save, organize, and search web bookmarks by category.

Tools:
  - add_bookmark(url, title, category)
  - list_bookmarks(category)
  - search_bookmarks(keyword)
  - delete_bookmark(url)

Data is stored in bookmarks.json in the current directory.
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Bookmark Manager")

# Path to the JSON data file
DATA_FILE = "bookmarks.json"


def load_bookmarks():
    """Load bookmarks from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_bookmarks(bookmarks):
    """Save bookmarks to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(bookmarks, f, indent=2)


# --- Tool: add_bookmark ---
@mcp.tool()
def add_bookmark(url: str, title: str, category: str) -> str:
    """Add a new bookmark.

    Args:
        url: The URL to bookmark (e.g., 'https://example.com')
        title: A title for the bookmark
        category: Category to organize it (e.g., 'python', 'news', 'tools')
    """
    bookmarks = load_bookmarks()

    # Check if URL already exists
    for bm in bookmarks:
        if bm["url"] == url:
            return f"Bookmark already exists: '{bm['title']}' ({url})"

    # Create bookmark entry
    bookmark = {
        "url": url,
        "title": title,
        "category": category.lower(),
        "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    bookmarks.append(bookmark)
    save_bookmarks(bookmarks)

    return f"Bookmark added: '{title}' [{category}]\n  URL: {url}"


# --- Tool: list_bookmarks ---
@mcp.tool()
def list_bookmarks(category: str = "all") -> str:
    """List bookmarks, optionally filtered by category.

    Args:
        category: Category to filter by, or 'all' for everything (default: 'all')
    """
    bookmarks = load_bookmarks()

    if not bookmarks:
        return "No bookmarks saved yet. Use add_bookmark to start!"

    # Filter by category if specified
    if category.lower() != "all":
        filtered = [b for b in bookmarks if b["category"] == category.lower()]
        if not filtered:
            return f"No bookmarks in category '{category}'."
        bookmarks = filtered
        header = f"Bookmarks in '{category}' ({len(bookmarks)}):"
    else:
        header = f"All Bookmarks ({len(bookmarks)}):"

    lines = [header, ""]

    # Group by category for better readability
    categories = {}
    for bm in bookmarks:
        cat = bm["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(bm)

    for cat, bms in sorted(categories.items()):
        lines.append(f"  [{cat}]")
        for bm in bms:
            lines.append(f"    - {bm['title']}")
            lines.append(f"      {bm['url']}")
        lines.append("")

    return "\n".join(lines)


# --- Tool: search_bookmarks ---
@mcp.tool()
def search_bookmarks(keyword: str) -> str:
    """Search bookmarks by keyword in title, URL, or category.

    Args:
        keyword: Word or phrase to search for
    """
    bookmarks = load_bookmarks()

    if not bookmarks:
        return "No bookmarks saved yet."

    # Search in title, URL, and category (case-insensitive)
    matches = []
    for bm in bookmarks:
        if (keyword.lower() in bm["title"].lower() or
                keyword.lower() in bm["url"].lower() or
                keyword.lower() in bm["category"].lower()):
            matches.append(bm)

    if not matches:
        return f"No bookmarks found matching '{keyword}'."

    lines = [f"Found {len(matches)} bookmark(s) matching '{keyword}':", ""]

    for bm in matches:
        lines.append(f"  - {bm['title']} [{bm['category']}]")
        lines.append(f"    {bm['url']}")
        lines.append("")

    return "\n".join(lines)


# --- Tool: delete_bookmark ---
@mcp.tool()
def delete_bookmark(url: str) -> str:
    """Delete a bookmark by its URL.

    Args:
        url: The URL of the bookmark to delete
    """
    bookmarks = load_bookmarks()

    # Find the bookmark to delete
    for i, bm in enumerate(bookmarks):
        if bm["url"] == url:
            removed = bookmarks.pop(i)
            save_bookmarks(bookmarks)
            return f"Deleted bookmark: '{removed['title']}'\n  URL: {url}"

    return f"No bookmark found with URL: {url}"


if __name__ == "__main__":
    print("Starting Bookmark Manager Server...")
    print("Tools: add_bookmark, list_bookmarks, search_bookmarks, delete_bookmark")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
