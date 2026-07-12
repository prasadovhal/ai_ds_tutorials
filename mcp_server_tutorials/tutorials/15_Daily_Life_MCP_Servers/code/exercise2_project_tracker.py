"""
Exercise 2 - Project Tracker Server (Stub)
============================================
GOAL: Build an MCP server to track projects and their tasks.

REQUIREMENTS:
  1. add_project(name) - Create a new project
  2. add_task(project, task) - Add a task to a project
  3. complete_task(project, task) - Mark a task as done
  4. project_status(project) - Show project progress

HINTS:
  - Store data in projects.json
  - Each project has a name, creation date, and list of tasks
  - Each task has a name, status (pending/completed), and dates
  - Use nested structure: {"projects": {"name": {"tasks": [...]}}}
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the server
# mcp = FastMCP("???")

# Step 2: Define load/save functions for projects.json
# def load_projects():
#     pass

# Step 3: Implement add_project tool
# @mcp.tool()
# def add_project(name: str) -> str:
#     pass

# Step 4: Implement add_task tool
# @mcp.tool()
# def add_task(project: str, task: str) -> str:
#     pass

# Step 5: Implement complete_task tool
# @mcp.tool()
# def complete_task(project: str, task: str) -> str:
#     pass

# Step 6: Implement project_status tool
# @mcp.tool()
# def project_status(project: str) -> str:
#     pass


if __name__ == "__main__":
    print("Exercise 2: Build your Project Tracker Server!")
    print("Edit this file to complete the exercise.")
