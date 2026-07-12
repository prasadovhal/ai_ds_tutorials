"""
Mini Project: Note-Taking MCP Server
=======================================
A complete MCP server for managing notes.

Features:
    Tools:
        - add_note(title, content): Add a new note
        - list_notes(): List all note titles
        - search_notes(keyword): Search notes by keyword
        - delete_note(title): Delete a note by title

    Resources:
        - notes://count: Total number of notes
        - notes://recent: The 5 most recently added notes

    Prompts:
        - organize_notes: Help organize notes into categories

This mini project demonstrates:
    - Combining tools, resources, and prompts
    - State management (notes stored in memory)
    - Input validation on all tools
    - Resources that reflect current state

How to run:
    poetry run mcp dev mini_project_note_server.py

How to test:
    1. Open MCP Inspector
    2. Add some notes using the "add_note" tool
    3. List notes using "list_notes"
    4. Search notes using "search_notes"
    5. Check the notes://count resource
    6. Check the notes://recent resource
    7. Delete a note using "delete_note"
"""

# ============================================================
# STEP 1: Imports
# ============================================================
from mcp.server.fastmcp import FastMCP
import datetime
import json

# ============================================================
# STEP 2: Create the server
# ============================================================
server = FastMCP("NoteServer")

# ============================================================
# STEP 3: In-memory storage for notes
# ============================================================
# We use a simple list to store notes.
# Each note is a dictionary with title, content, and timestamp.
#
# WHY a list and not a database?
# For learning purposes, in-memory storage is simple and clear.
# In production, you would use SQLite or another database.
#
# IMPORTANT: This data is lost when the server restarts!
# This is fine for learning. Production servers use databases.
notes_storage = []

# ============================================================
# TOOL 1: Add a note
# ============================================================
@server.tool()
def add_note(title: str, content: str) -> str:
    """Add a new note with a title and content."""

    # VALIDATION: Title must not be empty
    if not title or title.strip() == "":
        return "Error: Title cannot be empty."

    # VALIDATION: Content must not be empty
    if not content or content.strip() == "":
        return "Error: Content cannot be empty."

    # VALIDATION: Title must be unique
    # We check if a note with the same title already exists
    clean_title = title.strip()
    for note in notes_storage:
        if note["title"].lower() == clean_title.lower():
            return f"Error: A note with title '{clean_title}' already exists."

    # Create the note
    new_note = {
        "title": clean_title,
        "content": content.strip(),
        "created_at": datetime.datetime.now().isoformat()
    }

    # Add it to our storage
    notes_storage.append(new_note)

    return f"Note '{clean_title}' added successfully. Total notes: {len(notes_storage)}"

# ============================================================
# TOOL 2: List all notes
# ============================================================
@server.tool()
def list_notes() -> str:
    """List all notes with their titles and creation times."""

    # Check if there are any notes
    if len(notes_storage) == 0:
        return "No notes found. Use add_note to create one."

    # Build a list of note titles
    lines = []
    lines.append(f"Total notes: {len(notes_storage)}")
    lines.append("---")

    for i, note in enumerate(notes_storage):
        # Number each note starting from 1
        note_number = i + 1
        title = note["title"]
        created = note["created_at"]
        lines.append(f"{note_number}. {title} (created: {created})")

    return "\n".join(lines)

# ============================================================
# TOOL 3: Search notes by keyword
# ============================================================
@server.tool()
def search_notes(keyword: str) -> str:
    """Search notes by keyword in title or content."""

    # VALIDATION: Keyword must not be empty
    if not keyword or keyword.strip() == "":
        return "Error: Search keyword cannot be empty."

    clean_keyword = keyword.strip().lower()

    # Search through all notes
    matches = []
    for note in notes_storage:
        # Check if keyword appears in title OR content
        title_match = clean_keyword in note["title"].lower()
        content_match = clean_keyword in note["content"].lower()

        if title_match or content_match:
            matches.append(note)

    # Report results
    if len(matches) == 0:
        return f"No notes found matching '{keyword}'."

    lines = []
    lines.append(f"Found {len(matches)} note(s) matching '{keyword}':")
    lines.append("---")

    for note in matches:
        lines.append(f"Title: {note['title']}")
        # Show a preview of the content (first 100 characters)
        preview = note["content"][:100]
        if len(note["content"]) > 100:
            preview = preview + "..."
        lines.append(f"Preview: {preview}")
        lines.append("---")

    return "\n".join(lines)

# ============================================================
# TOOL 4: Delete a note by title
# ============================================================
@server.tool()
def delete_note(title: str) -> str:
    """Delete a note by its exact title."""

    # VALIDATION: Title must not be empty
    if not title or title.strip() == "":
        return "Error: Title cannot be empty."

    clean_title = title.strip()

    # Find the note to delete
    for i, note in enumerate(notes_storage):
        if note["title"].lower() == clean_title.lower():
            # Remove the note from the list
            deleted_note = notes_storage.pop(i)
            return f"Note '{deleted_note['title']}' deleted successfully. Remaining notes: {len(notes_storage)}"

    # Note not found
    return f"Error: No note found with title '{clean_title}'."

# ============================================================
# RESOURCE 1: Note count
# ============================================================
@server.resource("notes://count")
def get_note_count() -> str:
    """Get the total number of notes."""

    count = len(notes_storage)
    return f"Total notes: {count}"

# ============================================================
# RESOURCE 2: Recent notes
# ============================================================
@server.resource("notes://recent")
def get_recent_notes() -> str:
    """Get the 5 most recently added notes."""

    if len(notes_storage) == 0:
        return "No notes found."

    # Get the last 5 notes (most recently added)
    # We use slicing: [-5:] gives us the last 5 elements
    recent = notes_storage[-5:]

    # Reverse so the most recent is first
    recent = list(reversed(recent))

    lines = []
    lines.append(f"Recent notes (showing {len(recent)} of {len(notes_storage)}):")
    lines.append("---")

    for note in recent:
        lines.append(f"Title: {note['title']}")
        lines.append(f"Created: {note['created_at']}")
        # Show preview
        preview = note["content"][:80]
        if len(note["content"]) > 80:
            preview = preview + "..."
        lines.append(f"Preview: {preview}")
        lines.append("---")

    return "\n".join(lines)

# ============================================================
# PROMPT 1: Organize notes
# ============================================================
@server.prompt()
def organize_notes() -> str:
    """Help organize all notes into categories."""

    # Build a list of all note titles and content for the LLM
    if len(notes_storage) == 0:
        return "There are no notes to organize yet. Please add some notes first."

    notes_text = ""
    for note in notes_storage:
        notes_text = notes_text + f"\nTitle: {note['title']}\nContent: {note['content']}\n---"

    prompt = f"""I have the following notes that I would like you to organize into categories.

Please:
1. Read through all the notes
2. Identify logical categories (e.g., Work, Personal, Ideas, Tasks)
3. Assign each note to a category
4. Suggest any notes that could be merged or expanded

Notes:
{notes_text}

Please organize these notes:"""

    return prompt

# ============================================================
# RUN THE SERVER
# ============================================================
if __name__ == "__main__":
    server.run()
