"""
Journal MCP Server
====================
A personal journaling server with mood tracking.

Tools:
  - add_entry(text, mood)
  - search_entries(keyword)
  - mood_stats()
  - recent_entries(count)

Data is stored in journal.json in the current directory.
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Journal")

# Path to the JSON data file
DATA_FILE = "journal.json"


def load_journal():
    """Load journal entries from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_journal(entries):
    """Save journal entries to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2)


# --- Tool: add_entry ---
@mcp.tool()
def add_entry(text: str, mood: str) -> str:
    """Add a new journal entry with a mood.

    Args:
        text: The journal entry text
        mood: Your current mood (e.g., 'happy', 'sad', 'neutral', 'excited', 'anxious')
    """
    entries = load_journal()

    # Create journal entry
    entry = {
        "text": text,
        "mood": mood.lower(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "id": len(entries) + 1
    }

    entries.append(entry)
    save_journal(entries)

    return (
        f"Journal entry #{entry['id']} saved!\n"
        f"  Date: {entry['date']} {entry['time']}\n"
        f"  Mood: {mood}\n"
        f"  Text: {text[:50]}{'...' if len(text) > 50 else ''}"
    )


# --- Tool: search_entries ---
@mcp.tool()
def search_entries(keyword: str) -> str:
    """Search journal entries by keyword.

    Args:
        keyword: Word or phrase to search for in entries
    """
    entries = load_journal()

    if not entries:
        return "No journal entries yet. Use add_entry to start writing!"

    # Search in text and mood (case-insensitive)
    matches = []
    for entry in entries:
        if (keyword.lower() in entry["text"].lower() or
                keyword.lower() in entry["mood"].lower()):
            matches.append(entry)

    if not matches:
        return f"No entries found matching '{keyword}'."

    lines = [f"Found {len(matches)} entry/entries matching '{keyword}':", ""]

    for entry in matches:
        # Show a preview of the entry (first 80 characters)
        preview = entry["text"][:80]
        if len(entry["text"]) > 80:
            preview += "..."

        lines.append(f"  #{entry['id']} [{entry['date']}] ({entry['mood']})")
        lines.append(f"    {preview}")
        lines.append("")

    return "\n".join(lines)


# --- Tool: mood_stats ---
@mcp.tool()
def mood_stats() -> str:
    """Show statistics about your mood patterns."""
    entries = load_journal()

    if not entries:
        return "No journal entries yet."

    # Count moods
    mood_counts = {}
    for entry in entries:
        mood = entry["mood"]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    total = len(entries)

    # Build stats display
    lines = ["Mood Statistics:", ""]

    # Sort by frequency (most common first)
    for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        bar = "#" * int(percentage / 5)  # Simple bar chart
        lines.append(f"  {mood:<12} {count:>3} ({percentage:>5.1f}%) {bar}")

    lines.append(f"\n  Total entries: {total}")
    lines.append(f"  Unique moods:  {len(mood_counts)}")

    # Find most common mood
    most_common = max(mood_counts, key=mood_counts.get)
    lines.append(f"  Most common:   {most_common}")

    return "\n".join(lines)


# --- Tool: recent_entries ---
@mcp.tool()
def recent_entries(count: int = 5) -> str:
    """Show the most recent journal entries.

    Args:
        count: Number of recent entries to show (default: 5)
    """
    entries = load_journal()

    if not entries:
        return "No journal entries yet. Use add_entry to start writing!"

    # Get the most recent entries
    recent = entries[-count:] if count < len(entries) else entries
    recent = list(reversed(recent))  # Show newest first

    lines = [f"Recent Entries (showing {len(recent)} of {len(entries)}):", ""]

    for entry in recent:
        lines.append(f"  #{entry['id']} [{entry['date']} {entry['time']}] Mood: {entry['mood']}")
        lines.append(f"    {entry['text']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Journal Server...")
    print("Tools: add_entry, search_entries, mood_stats, recent_entries")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
