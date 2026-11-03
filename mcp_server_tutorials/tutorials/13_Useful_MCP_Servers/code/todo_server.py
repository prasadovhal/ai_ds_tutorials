"""
Todo MCP Server
===============
A simple todo list manager that stores todos in a JSON file.
Supports adding, listing, completing, deleting, and searching todos.
"""

# Import FastMCP and standard library modules
from mcp.server.fastmcp import FastMCP
import json
import os
from datetime import datetime

# Create the MCP server instance
server = FastMCP("Todo Server")

# Path to the JSON file for storing todos
TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


# --- Helper: Load todos from file ---
def _load_todos() -> list:
    """Load the todo list from the JSON file."""
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Helper: Save todos to file ---
def _save_todos(todos: list):
    """Save the todo list to the JSON file."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)


# --- Tool: Add a new todo ---
@server.tool()
def add_todo(title: str, priority: str = "medium") -> str:
    """
    Add a new todo item. Priority can be 'low', 'medium', or 'high'.
    """
    todos = _load_todos()

    # Create a new todo item
    todo = {
        "id": len(todos) + 1,
        "title": title,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }

    todos.append(todo)
    _save_todos(todos)

    return f"Todo added: '{title}' (priority: {priority}, id: {todo['id']})"


# --- Tool: List all todos ---
@server.tool()
def list_todos(show_completed: bool = False) -> str:
    """List all todos. Set show_completed=True to include completed items."""
    todos = _load_todos()

    if not todos:
        return "No todos found. Add one with add_todo!"

    # Filter based on completion status
    if not show_completed:
        display = [t for t in todos if not t["completed"]]
    else:
        display = todos

    if not display:
        return "No pending todos. All done!"

    # Build the display
    result = f"Todo List ({len(display)} items):\n\n"
    for todo in display:
        status = "[x]" if todo["completed"] else "[ ]"
        result += f"  {status} #{todo['id']} - {todo['title']} (priority: {todo['priority']})\n"

    return result


# --- Tool: Mark a todo as complete ---
@server.tool()
def complete_todo(todo_id: int) -> str:
    """Mark a todo item as completed by its ID."""
    todos = _load_todos()

    # Find the todo by ID
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = True
            todo["completed_at"] = datetime.now().isoformat()
            _save_todos(todos)
            return f"Todo #{todo_id} marked as complete: '{todo['title']}'"

    return f"Error: Todo #{todo_id} not found."


# --- Tool: Delete a todo ---
@server.tool()
def delete_todo(todo_id: int) -> str:
    """Delete a todo item by its ID."""
    todos = _load_todos()

    # Find and remove the todo
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            removed = todos.pop(i)
            _save_todos(todos)
            return f"Todo #{todo_id} deleted: '{removed['title']}'"

    return f"Error: Todo #{todo_id} not found."


# --- Tool: Search todos ---
@server.tool()
def search_todos(keyword: str) -> str:
    """Search todos by keyword in the title (case-insensitive)."""
    todos = _load_todos()

    # Search for matching todos
    matches = [t for t in todos if keyword.lower() in t["title"].lower()]

    if not matches:
        return f"No todos found matching '{keyword}'."

    result = f"Search results for '{keyword}' ({len(matches)} found):\n\n"
    for todo in matches:
        status = "[x]" if todo["completed"] else "[ ]"
        result += f"  {status} #{todo['id']} - {todo['title']} (priority: {todo['priority']})\n"

    return result


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
