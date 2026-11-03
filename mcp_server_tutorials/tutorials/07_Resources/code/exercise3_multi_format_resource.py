"""
Exercise 3: Multi-Format Resource Server
==========================================
YOUR TASK: Build an MCP server that serves the SAME user data
in three different formats via different resource URIs:
  - Text (plain readable text)
  - JSON (structured JSON)
  - CSV (comma-separated values)

This is a common real-world pattern: different clients need
different formats of the same data.

Requirements:
1. Define a list of user dictionaries (at least 3 users)
   Each user should have: id, name, email, role
2. Create a resource at "data://users/text" that returns users as
   a human-readable text table
3. Create a resource at "data://users/json" that returns users as
   a JSON array
4. Create a resource at "data://users/csv" that returns users as
   CSV with a header row

Hints:
- Use the same source list of users for all three resources
- For CSV, build the string manually (no csv module needed)
- For JSON, use json.dumps() with indent=2
- For text, use string formatting to align columns

How to test:
    npx @modelcontextprotocol/inspector python exercise3_multi_format_resource.py
"""

from mcp.server.fastmcp import FastMCP
import json

# Create the server
server = FastMCP("Multi-Format Resource Exercise")

# ============================================================
# TODO: Define a list of user dictionaries.
# Each user should have: id, name, email, role
# Example:
#   users = [
#       {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
#       ...
#   ]
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "data://users/text"
# Return users as a nicely formatted plain-text table.
# Example output:
#   ID  Name     Email               Role
#   --  ----     -----               ----
#   1   Alice    alice@example.com    admin
#   ...
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "data://users/json"
# Return users as a JSON string using json.dumps()
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "data://users/csv"
# Return users as CSV with a header row.
# Example output:
#   id,name,email,role
#   1,Alice,alice@example.com,admin
#   ...
# ============================================================

# YOUR CODE HERE


if __name__ == "__main__":
    server.run()
