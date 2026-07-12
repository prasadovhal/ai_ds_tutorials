"""
Exercise 2 Solution - Project Tracker Server
==============================================
Track projects and their tasks with completion status.

Tools:
  - add_project(name)
  - add_task(project, task)
  - complete_task(project, task)
  - project_status(project)

Data is stored in projects.json.
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Project Tracker")

# Path to the JSON data file
DATA_FILE = "projects.json"


def load_projects():
    """Load projects data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"projects": {}}


def save_projects(data):
    """Save projects data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Tool: add_project ---
@mcp.tool()
def add_project(name: str) -> str:
    """Create a new project.

    Args:
        name: Name of the project (e.g., 'Website Redesign')
    """
    data = load_projects()

    # Check if project already exists (case-insensitive)
    for proj_name in data["projects"]:
        if proj_name.lower() == name.lower():
            return f"Project '{name}' already exists!"

    # Create the project
    data["projects"][name] = {
        "created": datetime.now().strftime("%Y-%m-%d"),
        "tasks": []
    }

    save_projects(data)
    return f"Project '{name}' created! Use add_task to add tasks."


# --- Tool: add_task ---
@mcp.tool()
def add_task(project: str, task: str) -> str:
    """Add a task to a project.

    Args:
        project: Name of the project
        task: Description of the task
    """
    data = load_projects()

    # Find the project (case-insensitive)
    proj_key = None
    for name in data["projects"]:
        if name.lower() == project.lower():
            proj_key = name
            break

    if proj_key is None:
        return f"Project '{project}' not found. Use add_project first."

    # Check for duplicate task
    for t in data["projects"][proj_key]["tasks"]:
        if t["name"].lower() == task.lower():
            return f"Task '{task}' already exists in '{proj_key}'!"

    # Add the task
    task_entry = {
        "name": task,
        "status": "pending",
        "added": datetime.now().strftime("%Y-%m-%d"),
        "completed": None
    }

    data["projects"][proj_key]["tasks"].append(task_entry)
    save_projects(data)

    total = len(data["projects"][proj_key]["tasks"])
    return f"Task added to '{proj_key}': {task} (total tasks: {total})"


# --- Tool: complete_task ---
@mcp.tool()
def complete_task(project: str, task: str) -> str:
    """Mark a task as completed.

    Args:
        project: Name of the project
        task: Name of the task to complete
    """
    data = load_projects()

    # Find the project
    proj_key = None
    for name in data["projects"]:
        if name.lower() == project.lower():
            proj_key = name
            break

    if proj_key is None:
        return f"Project '{project}' not found."

    # Find the task
    for t in data["projects"][proj_key]["tasks"]:
        if t["name"].lower() == task.lower():
            if t["status"] == "completed":
                return f"Task '{task}' is already completed!"

            t["status"] = "completed"
            t["completed"] = datetime.now().strftime("%Y-%m-%d")

            save_projects(data)

            # Count progress
            tasks = data["projects"][proj_key]["tasks"]
            done = sum(1 for x in tasks if x["status"] == "completed")
            total = len(tasks)

            return (
                f"Task completed: '{task}' in '{proj_key}'\n"
                f"  Progress: {done}/{total} tasks done"
            )

    return f"Task '{task}' not found in '{proj_key}'."


# --- Tool: project_status ---
@mcp.tool()
def project_status(project: str) -> str:
    """Show the status of a project and all its tasks.

    Args:
        project: Name of the project (use 'all' to see all projects)
    """
    data = load_projects()

    if not data["projects"]:
        return "No projects yet. Use add_project to create one."

    # Show all projects if requested
    if project.lower() == "all":
        lines = [f"All Projects ({len(data['projects'])}):", ""]
        for name, proj in data["projects"].items():
            tasks = proj["tasks"]
            done = sum(1 for t in tasks if t["status"] == "completed")
            total = len(tasks)
            pct = (done / total * 100) if total > 0 else 0
            bar_filled = int(pct / 10)
            bar = "[" + "#" * bar_filled + "-" * (10 - bar_filled) + "]"
            lines.append(f"  {name}: {done}/{total} {bar} {pct:.0f}%")
        return "\n".join(lines)

    # Find specific project
    proj_key = None
    for name in data["projects"]:
        if name.lower() == project.lower():
            proj_key = name
            break

    if proj_key is None:
        return f"Project '{project}' not found."

    proj = data["projects"][proj_key]
    tasks = proj["tasks"]
    done = sum(1 for t in tasks if t["status"] == "completed")
    total = len(tasks)
    pct = (done / total * 100) if total > 0 else 0

    lines = [f"Project: {proj_key}", ""]
    lines.append(f"  Created: {proj['created']}")
    lines.append(f"  Progress: {done}/{total} ({pct:.0f}%)")

    if tasks:
        lines.append(f"\n  Tasks:")
        for t in tasks:
            status = "DONE" if t["status"] == "completed" else "TODO"
            lines.append(f"    [{status}] {t['name']}")
    else:
        lines.append(f"\n  No tasks yet. Use add_task to add some.")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Project Tracker Server...")
    print("Tools: add_project, add_task, complete_task, project_status")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
