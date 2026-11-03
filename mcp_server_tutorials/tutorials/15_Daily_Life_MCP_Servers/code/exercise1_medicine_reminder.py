"""
Exercise 1 - Medicine Reminder Server (Stub)
==============================================
GOAL: Build an MCP server to track medicines and reminders.

REQUIREMENTS:
  1. add_medicine(name, dosage, time) - Add a medicine to track
  2. list_medicines() - List all medicines
  3. check_due() - Check which medicines are due now
  4. mark_taken(name) - Mark a medicine as taken today

HINTS:
  - Store data in medicines.json
  - Use datetime to track times and dates
  - The 'time' parameter is a string like '08:00' or '14:30'
  - Track which medicines were taken today with dates
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the server
# mcp = FastMCP("???")

# Step 2: Define load/save functions for medicines.json
# def load_medicines():
#     pass

# Step 3: Implement add_medicine tool
# @mcp.tool()
# def add_medicine(name: str, dosage: str, time: str) -> str:
#     pass

# Step 4: Implement list_medicines tool
# @mcp.tool()
# def list_medicines() -> str:
#     pass

# Step 5: Implement check_due tool
# @mcp.tool()
# def check_due() -> str:
#     pass

# Step 6: Implement mark_taken tool
# @mcp.tool()
# def mark_taken(name: str) -> str:
#     pass


if __name__ == "__main__":
    print("Exercise 1: Build your Medicine Reminder Server!")
    print("Edit this file to complete the exercise.")
