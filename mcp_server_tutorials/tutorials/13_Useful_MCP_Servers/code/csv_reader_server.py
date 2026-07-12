"""
CSV Reader MCP Server
=====================
Provides tools to read and query CSV files.
Uses Python's built-in csv module.
"""

# Import FastMCP and the csv module
from mcp.server.fastmcp import FastMCP
import csv
import os

# Create the MCP server instance
server = FastMCP("CSV Reader Server")


# --- Helper: Read CSV file and return rows ---
def _read_csv(filepath: str) -> tuple:
    """
    Helper function to read a CSV file.
    Returns (headers, rows) or raises an error message.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")

    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    return headers, rows


# --- Tool: Load and display CSV contents ---
@server.tool()
def load_csv(filepath: str) -> str:
    """Load a CSV file and display its contents (first 20 rows)."""
    try:
        headers, rows = _read_csv(filepath)
    except FileNotFoundError as e:
        return str(e)

    # Build output with headers
    result = f"CSV File: {filepath}\n"
    result += f"Columns: {', '.join(headers)}\n"
    result += f"Total Rows: {len(rows)}\n\n"

    # Show first 20 rows
    display_rows = rows[:20]
    for i, row in enumerate(display_rows, 1):
        row_str = " | ".join(f"{k}: {v}" for k, v in row.items())
        result += f"  Row {i}: {row_str}\n"

    if len(rows) > 20:
        result += f"\n  ... and {len(rows) - 20} more rows."

    return result


# --- Tool: Get column names ---
@server.tool()
def get_columns(filepath: str) -> str:
    """Get the column names from a CSV file."""
    try:
        headers, _ = _read_csv(filepath)
    except FileNotFoundError as e:
        return str(e)

    return f"Columns in '{filepath}':\n" + "\n".join(f"  - {col}" for col in headers)


# --- Tool: Get row count ---
@server.tool()
def get_row_count(filepath: str) -> str:
    """Get the number of data rows in a CSV file."""
    try:
        _, rows = _read_csv(filepath)
    except FileNotFoundError as e:
        return str(e)

    return f"'{filepath}' contains {len(rows)} rows."


# --- Tool: Filter rows by column value ---
@server.tool()
def filter_rows(filepath: str, column: str, value: str) -> str:
    """Filter CSV rows where a column matches a given value (case-insensitive)."""
    try:
        headers, rows = _read_csv(filepath)
    except FileNotFoundError as e:
        return str(e)

    # Check if column exists
    if column not in headers:
        return f"Error: Column '{column}' not found. Available: {', '.join(headers)}"

    # Filter rows where the column matches the value (case-insensitive)
    matched = [row for row in rows if row.get(column, "").lower() == value.lower()]

    if not matched:
        return f"No rows found where '{column}' = '{value}'."

    # Build result
    result = f"Found {len(matched)} rows where '{column}' = '{value}':\n\n"
    for i, row in enumerate(matched[:50], 1):
        row_str = " | ".join(f"{k}: {v}" for k, v in row.items())
        result += f"  Row {i}: {row_str}\n"

    if len(matched) > 50:
        result += f"\n  ... and {len(matched) - 50} more rows."

    return result


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
