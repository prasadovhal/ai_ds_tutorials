"""
Mini Project: Personal Assistant MCP Server
============================================
Combines multiple useful tools into one server:
- Notes (add, list, search, delete)
- Todos (add, list, complete, delete)
- Calculator (add, subtract, multiply, divide)
- Date/Time (current time, days until, day of week)

All data stored in a single assistant_data.json file.
"""

import json
import os
import time
import math
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

server = FastMCP("personal-assistant")

# Single data file for all features
DATA_FILE = "assistant_data.json"


def load_data():
    """Load all assistant data from file."""
    if not os.path.exists(DATA_FILE):
        return {"notes": [], "todos": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    """Save all assistant data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# NOTES
# ============================================================

@server.tool()
def add_note(title: str, content: str) -> str:
    """Add a new note."""
    data = load_data()
    note = {
        "title": title,
        "content": content,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data["notes"].append(note)
    save_data(data)
    return f"Note '{title}' added. Total notes: {len(data['notes'])}"


@server.tool()
def list_notes() -> str:
    """List all notes."""
    data = load_data()
    notes = data.get("notes", [])
    if len(notes) == 0:
        return "No notes yet."
    result = f"Notes ({len(notes)}):\n"
    for i, note in enumerate(notes):
        result += f"  {i + 1}. [{note['created']}] {note['title']}\n"
    return result


@server.tool()
def search_notes(keyword: str) -> str:
    """Search notes by keyword."""
    data = load_data()
    matches = []
    keyword_lower = keyword.lower()
    for note in data.get("notes", []):
        if keyword_lower in note["title"].lower() or keyword_lower in note["content"].lower():
            matches.append(note)
    if len(matches) == 0:
        return f"No notes found matching '{keyword}'"
    result = f"Found {len(matches)} notes:\n"
    for note in matches:
        result += f"  - {note['title']}: {note['content'][:50]}...\n"
    return result


# ============================================================
# TODOS
# ============================================================

@server.tool()
def add_todo(task: str) -> str:
    """Add a new todo item."""
    data = load_data()
    todo = {
        "task": task,
        "completed": False,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data["todos"].append(todo)
    save_data(data)
    return f"Todo added: {task}"


@server.tool()
def list_todos() -> str:
    """List all todo items."""
    data = load_data()
    todos = data.get("todos", [])
    if len(todos) == 0:
        return "No todos yet."
    result = f"Todos ({len(todos)}):\n"
    for i, todo in enumerate(todos):
        status = "[x]" if todo["completed"] else "[ ]"
        result += f"  {i + 1}. {status} {todo['task']}\n"
    return result


@server.tool()
def complete_todo(task_number: int) -> str:
    """Mark a todo as completed (by number)."""
    data = load_data()
    todos = data.get("todos", [])
    index = task_number - 1
    if index < 0 or index >= len(todos):
        return f"Invalid task number. You have {len(todos)} todos."
    todos[index]["completed"] = True
    save_data(data)
    return f"Completed: {todos[index]['task']}"


# ============================================================
# CALCULATOR
# ============================================================

@server.tool()
def calculate(operation: str, a: float, b: float) -> str:
    """Perform a math operation: add, subtract, multiply, divide."""
    op = operation.lower()
    if op == "add":
        result = a + b
    elif op == "subtract":
        result = a - b
    elif op == "multiply":
        result = a * b
    elif op == "divide":
        if b == 0:
            return "Error: Cannot divide by zero"
        result = a / b
    else:
        return f"Unknown operation: {operation}. Use: add, subtract, multiply, divide"
    return str(round(result, 4))


@server.tool()
def sqrt(number: float) -> str:
    """Calculate square root."""
    if number < 0:
        return "Error: Cannot take square root of negative number"
    result = math.sqrt(number)
    return str(round(result, 4))


# ============================================================
# DATE/TIME
# ============================================================

@server.tool()
def current_time() -> str:
    """Get current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")


@server.tool()
def days_until(target_date: str) -> str:
    """Calculate days until a target date (format: YYYY-MM-DD)."""
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        delta = target - today
        if delta.days < 0:
            return f"{abs(delta.days)} days ago"
        elif delta.days == 0:
            return "That's today!"
        else:
            return f"{delta.days} days from now"
    except ValueError:
        return "Error: Use format YYYY-MM-DD"


# ============================================================
# RESOURCES
# ============================================================

@server.resource("info://assistant")
def get_info() -> str:
    """Information about this assistant."""
    return (
        "Personal Assistant MCP Server\n"
        "Features: Notes, Todos, Calculator, Date/Time\n"
        "All data stored in assistant_data.json"
    )


if __name__ == "__main__":
    server.run()
