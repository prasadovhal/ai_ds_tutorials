"""
Example 3 - Multi-User MCP Server
====================================
This server manages separate data for different users.
Each user has their own notes list, identified by user_id.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: User data storage
# ============================================================

# Dictionary keyed by user_id
# Format: { user_id: {"name": str, "notes": [str]} }
_users = {}

# ============================================================
# Step 2: Create MCP server with user-scoped tools
# ============================================================

mcp = FastMCP("MultiUserServer")


@mcp.tool()
def create_user(user_id: str, name: str) -> str:
    """
    Create a new user with the given ID and name.
    Each user gets their own empty notes list.
    """
    if user_id in _users:
        return f"Error: User '{user_id}' already exists."

    # Create user with empty notes list
    _users[user_id] = {
        "name": name,
        "notes": [],
    }
    return f"User '{name}' created with ID '{user_id}'."


@mcp.tool()
def add_note(user_id: str, note: str) -> str:
    """
    Add a note to a specific user's notes list.
    The user must exist first (use create_user).
    """
    if user_id not in _users:
        return f"Error: User '{user_id}' not found. Create them first."

    _users[user_id]["notes"].append(note)
    count = len(_users[user_id]["notes"])
    return f"Note added for {_users[user_id]['name']}. Total notes: {count}."


@mcp.tool()
def get_notes(user_id: str) -> str:
    """
    Get all notes for a specific user.
    Returns the user's name and their numbered notes.
    """
    if user_id not in _users:
        return f"Error: User '{user_id}' not found."

    user = _users[user_id]
    notes = user["notes"]

    if not notes:
        return f"{user['name']} has no notes yet."

    # Format notes with numbers
    lines = [f"Notes for {user['name']}:"]
    for i, note in enumerate(notes, 1):
        lines.append(f"  {i}. {note}")
    return "\n".join(lines)


@mcp.tool()
def list_users() -> str:
    """
    List all registered users with their note counts.
    """
    if not _users:
        return "No users registered yet."

    lines = ["Registered Users:"]
    for uid, user in _users.items():
        note_count = len(user["notes"])
        lines.append(f"  {uid}: {user['name']} ({note_count} notes)")
    return "\n".join(lines)


# ============================================================
# Step 3: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Multi-User MCP Server - Demo")
    print("=" * 50)

    # Create some users
    print(create_user("alice", "Alice Smith"))
    print(create_user("bob", "Bob Jones"))

    # Add notes for different users
    print(add_note("alice", "Buy groceries"))
    print(add_note("alice", "Finish MCP tutorial"))
    print(add_note("bob", "Walk the dog"))

    # Try duplicate user
    print(create_user("alice", "Alice Again"))

    # Show notes per user
    print()
    print(get_notes("alice"))
    print()
    print(get_notes("bob"))

    # List all users
    print()
    print(list_users())

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
