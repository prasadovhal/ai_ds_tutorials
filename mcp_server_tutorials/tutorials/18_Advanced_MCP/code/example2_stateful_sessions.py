"""
Example 2: Stateful MCP Server with File-Based Persistence
============================================================
This server remembers data between sessions by saving state
to a JSON file on disk.

When the server starts, it loads existing state from a file.
When state changes, it saves back to the file immediately.
When the server restarts, all data is still there.

What you will learn:
    - How to load state from a JSON file at startup
    - How to save state to a JSON file after every change
    - How to handle missing or corrupted state files
    - How to build tools that read and write persistent state

Real-world analogy:
    Think of this like a notebook.
    - When you open the notebook (server starts), you read what is there.
    - When you write something new, you write it in the notebook.
    - When you close the notebook (server stops), nothing is lost.
    - When you open it again later, everything is still there.

How to run:
    poetry run mcp dev example2_stateful_sessions.py

How to test:
    1. Open MCP Inspector
    2. Call "add_note" with title="Shopping" and content="Buy milk"
    3. Call "list_notes" to see your note
    4. STOP the server (Ctrl+C)
    5. START the server again
    6. Call "list_notes" again - your note is still there!
"""

# ============================================================
# STEP 1: Import required libraries
# ============================================================
from mcp.server.fastmcp import FastMCP

# json module for reading and writing JSON files
import json

# os module to check if the state file exists
import os

# datetime module to timestamp our notes
import datetime

# ============================================================
# STEP 2: Define the state file path
# ============================================================
# This is where we will save our state.
# The file will be created in the same directory as this script.
# We use os.path to build the path properly for any operating system.

# Get the directory where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# The state file will be called "server_state.json"
STATE_FILE = os.path.join(SCRIPT_DIR, "server_state.json")


# ============================================================
# STEP 3: Define functions to load and save state
# ============================================================

def load_state():
    """
    Load the server state from the JSON file.

    If the file does not exist, return a fresh empty state.
    If the file is corrupted (bad JSON), return a fresh empty state.

    Returns:
        A dictionary containing the server state.
    """

    # Check if the state file exists
    if not os.path.exists(STATE_FILE):
        # No state file found. This is the first time running.
        # Return an empty state with a default structure.
        print(f"No state file found at {STATE_FILE}. Starting fresh.")
        empty_state = {
            "notes": [],
            "next_id": 1,
            "created_at": datetime.datetime.now().isoformat(),
            "total_notes_ever_created": 0
        }
        return empty_state

    # The file exists, try to read it
    try:
        file_handle = open(STATE_FILE, "r", encoding="utf-8")
        file_contents = file_handle.read()
        file_handle.close()

        # Parse the JSON string into a Python dictionary
        state = json.loads(file_contents)
        print(f"State loaded from {STATE_FILE}. Found {len(state.get('notes', []))} notes.")
        return state

    except json.JSONDecodeError:
        # The file exists but contains invalid JSON (corrupted)
        print(f"Warning: State file is corrupted. Starting fresh.")
        empty_state = {
            "notes": [],
            "next_id": 1,
            "created_at": datetime.datetime.now().isoformat(),
            "total_notes_ever_created": 0
        }
        return empty_state

    except Exception as e:
        # Some other error occurred (permissions, etc.)
        print(f"Warning: Could not read state file: {e}. Starting fresh.")
        empty_state = {
            "notes": [],
            "next_id": 1,
            "created_at": datetime.datetime.now().isoformat(),
            "total_notes_ever_created": 0
        }
        return empty_state


def save_state(state):
    """
    Save the server state to the JSON file.

    We write the state as formatted JSON so it is easy
    to read if you open the file manually.

    Args:
        state: The dictionary containing the server state.
    """

    try:
        # Convert the state dictionary to a formatted JSON string
        json_string = json.dumps(state, indent=2, ensure_ascii=False)

        # Write the JSON string to the file
        file_handle = open(STATE_FILE, "w", encoding="utf-8")
        file_handle.write(json_string)
        file_handle.close()

        print(f"State saved to {STATE_FILE}.")

    except Exception as e:
        # If saving fails, print a warning but do not crash
        print(f"Warning: Could not save state: {e}")


# ============================================================
# STEP 4: Load the state at startup
# ============================================================
# This runs when the module is first loaded.
# The state dictionary lives in memory for fast access.
# It gets saved to disk whenever it changes.
state = load_state()


# ============================================================
# STEP 5: Create the server
# ============================================================
server = FastMCP("StatefulNotesServer")


# ============================================================
# STEP 6: Define tools for managing notes
# ============================================================

@server.tool()
def add_note(title: str, content: str) -> str:
    """
    Add a new note. The note is saved to disk immediately
    so it survives server restarts.

    Args:
        title: The title of the note
        content: The content/body of the note

    Returns:
        Confirmation message with the note ID.
    """

    # Create the note as a dictionary
    note = {
        "id": state["next_id"],
        "title": title,
        "content": content,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }

    # Add the note to our state
    state["notes"].append(note)

    # Increment the next ID counter
    state["next_id"] = state["next_id"] + 1

    # Increment the total counter
    state["total_notes_ever_created"] = state["total_notes_ever_created"] + 1

    # Save the updated state to disk immediately
    save_state(state)

    # Return confirmation
    return f"Note added with ID {note['id']}: '{title}'"


@server.tool()
def list_notes() -> str:
    """
    List all notes with their IDs, titles, and creation dates.

    Returns:
        A formatted list of all notes, or a message if no notes exist.
    """

    notes = state["notes"]

    # Check if there are any notes
    if len(notes) == 0:
        return "No notes found. Use 'add_note' to create one."

    # Build a formatted list
    lines = []
    lines.append(f"Found {len(notes)} note(s):")
    lines.append("-" * 40)

    for note in notes:
        note_id = note["id"]
        title = note["title"]
        created = note["created_at"]

        # Show a preview of the content (first 50 characters)
        content_preview = note["content"]
        if len(content_preview) > 50:
            content_preview = content_preview[:50] + "..."

        lines.append(f"[{note_id}] {title}")
        lines.append(f"    Content: {content_preview}")
        lines.append(f"    Created: {created}")
        lines.append("")

    return "\n".join(lines)


@server.tool()
def get_note(note_id: int) -> str:
    """
    Get the full content of a specific note by its ID.

    Args:
        note_id: The ID of the note to retrieve.

    Returns:
        The full note content, or an error message if not found.
    """

    # Search for the note with the given ID
    for note in state["notes"]:
        if note["id"] == note_id:
            # Found it! Build the full display
            lines = []
            lines.append(f"Note #{note['id']}: {note['title']}")
            lines.append("=" * 40)
            lines.append(note["content"])
            lines.append("")
            lines.append(f"Created: {note['created_at']}")
            lines.append(f"Updated: {note['updated_at']}")
            return "\n".join(lines)

    # Note not found
    return f"Error: Note with ID {note_id} not found."


@server.tool()
def update_note(note_id: int, new_content: str) -> str:
    """
    Update the content of an existing note.

    Args:
        note_id: The ID of the note to update.
        new_content: The new content for the note.

    Returns:
        Confirmation message or error if note not found.
    """

    # Search for the note
    for note in state["notes"]:
        if note["id"] == note_id:
            # Found it! Update the content
            old_content = note["content"]
            note["content"] = new_content
            note["updated_at"] = datetime.datetime.now().isoformat()

            # Save to disk
            save_state(state)

            return f"Note #{note_id} updated. Old content: '{old_content[:30]}...'"

    # Note not found
    return f"Error: Note with ID {note_id} not found."


@server.tool()
def delete_note(note_id: int) -> str:
    """
    Delete a note by its ID.

    Args:
        note_id: The ID of the note to delete.

    Returns:
        Confirmation message or error if note not found.
    """

    # Search for the note and remove it
    for i in range(len(state["notes"])):
        if state["notes"][i]["id"] == note_id:
            # Found it! Remove it from the list
            deleted_note = state["notes"].pop(i)

            # Save to disk
            save_state(state)

            return f"Note #{note_id} ('{deleted_note['title']}') deleted."

    # Note not found
    return f"Error: Note with ID {note_id} not found."


@server.tool()
def search_notes(query: str) -> str:
    """
    Search notes by title or content.

    Args:
        query: The search text to look for (case-insensitive).

    Returns:
        List of matching notes or message if none found.
    """

    # Convert query to lowercase for case-insensitive search
    query_lower = query.lower()

    # Search through all notes
    matches = []
    for note in state["notes"]:
        title_lower = note["title"].lower()
        content_lower = note["content"].lower()

        # Check if query appears in title or content
        if query_lower in title_lower or query_lower in content_lower:
            matches.append(note)

    # Report results
    if len(matches) == 0:
        return f"No notes matching '{query}' found."

    lines = []
    lines.append(f"Found {len(matches)} note(s) matching '{query}':")
    lines.append("-" * 40)

    for note in matches:
        lines.append(f"[{note['id']}] {note['title']}")
        content_preview = note["content"]
        if len(content_preview) > 50:
            content_preview = content_preview[:50] + "..."
        lines.append(f"    Content: {content_preview}")
        lines.append("")

    return "\n".join(lines)


@server.tool()
def get_stats() -> str:
    """
    Get statistics about the notes database.

    Returns:
        Statistics including note count, total characters, etc.
    """

    notes = state["notes"]
    total_notes = len(notes)

    # Calculate total characters across all notes
    total_characters = 0
    for note in notes:
        total_characters = total_characters + len(note["content"])

    # Build stats report
    lines = []
    lines.append("Notes Database Statistics")
    lines.append("=" * 40)
    lines.append(f"Current notes: {total_notes}")
    lines.append(f"Total notes ever created: {state['total_notes_ever_created']}")
    lines.append(f"Total characters stored: {total_characters}")
    lines.append(f"State file: {STATE_FILE}")
    lines.append(f"Database created: {state.get('created_at', 'Unknown')}")

    if total_notes > 0:
        avg_length = total_characters // total_notes
        lines.append(f"Average note length: {avg_length} characters")

    return "\n".join(lines)


# ============================================================
# STEP 7: Run the server
# ============================================================
if __name__ == "__main__":
    print(f"Starting StatefulNotesServer...")
    print(f"State file: {STATE_FILE}")
    print(f"Current notes: {len(state['notes'])}")
    server.run()
