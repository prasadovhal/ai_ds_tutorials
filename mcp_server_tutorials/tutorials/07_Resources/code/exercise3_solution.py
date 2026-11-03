"""
Exercise 3 Solution: Multi-Format Resource Server
===================================================
This solution creates an MCP server that serves the same user data
in three different formats: plain text, JSON, and CSV.

This is a very common pattern in real-world APIs -- the same data
is available in multiple formats so different clients can pick the
format that works best for them.

How to run:
    python exercise3_solution.py

How to test:
    npx @modelcontextprotocol/inspector python exercise3_solution.py
"""

from mcp.server.fastmcp import FastMCP
import json

# ============================================================
# Step 1: Create the MCP Server
# ============================================================
server = FastMCP("Multi-Format Resource Server")


# ============================================================
# Step 2: Define the shared user data
# ============================================================
# This is the SINGLE SOURCE OF TRUTH for user data.
# All three resources read from this same list.
# WHY a shared list? Because we want all formats to always
# return exactly the same data -- if one changes, they all change.
USERS = [
    {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "role": "admin"
    },
    {
        "id": 2,
        "name": "Bob Smith",
        "email": "bob@example.com",
        "role": "developer"
    },
    {
        "id": 3,
        "name": "Carol Williams",
        "email": "carol@example.com",
        "role": "designer"
    },
    {
        "id": 4,
        "name": "Dave Brown",
        "email": "dave@example.com",
        "role": "developer"
    },
    {
        "id": 5,
        "name": "Eve Davis",
        "email": "eve@example.com",
        "role": "manager"
    },
]


# ============================================================
# Step 3: Text Format Resource
# ============================================================
# This resource returns the user data as a human-readable
# plain-text table. This format is good for display in
# terminals or simple text-based clients.
@server.resource("data://users/text")
def get_users_text():
    """Return all users as a formatted text table."""

    # Build the header row
    # We use fixed-width columns so the table lines up nicely
    lines = []
    lines.append(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Role':<12}")
    lines.append(f"{'--':<5} {'----':<20} {'-----':<25} {'----':<12}")

    # Add a row for each user
    for user in USERS:
        row = f"{user['id']:<5} {user['name']:<20} {user['email']:<25} {user['role']:<12}"
        lines.append(row)

    # Add a footer with the total count
    lines.append("")
    lines.append(f"Total users: {len(USERS)}")

    # Join all lines into a single string
    return "\n".join(lines)


# ============================================================
# Step 4: JSON Format Resource
# ============================================================
# This resource returns the user data as a JSON array.
# JSON is the most common format for structured data.
# It is easy to parse in any programming language.
@server.resource("data://users/json")
def get_users_json():
    """Return all users as a JSON array."""

    # json.dumps converts the Python list to a JSON string
    # indent=2 makes it human-readable with nice formatting
    return json.dumps(USERS, indent=2)


# ============================================================
# Step 5: CSV Format Resource
# ============================================================
# This resource returns the user data as CSV (Comma-Separated Values).
# CSV is a simple format that can be opened in Excel, Google Sheets,
# or any spreadsheet application.
@server.resource("data://users/csv")
def get_users_csv():
    """Return all users as CSV with a header row."""

    # Start with the header row
    # The header lists the column names separated by commas
    lines = []
    lines.append("id,name,email,role")

    # Add a row for each user
    for user in USERS:
        # Build the CSV row by joining values with commas
        row = f"{user['id']},{user['name']},{user['email']},{user['role']}"
        lines.append(row)

    # Join all lines with newline characters
    return "\n".join(lines)


# ============================================================
# Step 6: Run the Server
# ============================================================
if __name__ == "__main__":
    server.run()
