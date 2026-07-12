"""
Example 4: CSV Resource
========================
This example shows how to read a CSV file and serve it as a resource
in multiple useful formats: raw CSV, formatted table, and JSON.

CSV (Comma-Separated Values) is one of the most common data formats.
Being able to serve CSV data through MCP lets LLMs analyze tabular data.

How to run:
    python example4_csv_resource.py

How to test:
    npx @modelcontextprotocol/inspector python example4_csv_resource.py
"""

# ============================================================
# Step 1: Import Everything We Need
# ============================================================
from mcp.server.fastmcp import FastMCP
import csv
import json
import os
import io

# ============================================================
# Step 2: Create the MCP Server
# ============================================================
server = FastMCP("CSV Resources Demo")

# ============================================================
# Step 3: Set Up the Path to Our CSV File
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "sample_data.csv")


# ============================================================
# Step 4: Helper Function to Read and Parse CSV
# ============================================================
# This function reads our CSV file and returns the data as a list
# of dictionaries. Each dictionary represents one row, with column
# names as keys.
def read_csv_data():
    """
    Read the sample CSV file and return parsed data.

    Returns:
        A tuple of (headers, rows) where headers is a list of column names
        and rows is a list of dictionaries.
    """
    # Check if the file exists
    if not os.path.exists(CSV_FILE):
        return [], []

    # Open and read the CSV file
    file_handle = open(CSV_FILE, "r", encoding="utf-8")
    reader = csv.DictReader(file_handle)

    # Get the column headers
    headers = reader.fieldnames

    # Read all rows into a list
    rows = []
    for row in reader:
        rows.append(row)

    file_handle.close()

    return headers, rows


# ============================================================
# Step 5: Raw CSV Resource
# ============================================================
# This resource returns the CSV file as-is, in its original format.
# Useful when clients want to process the raw CSV data themselves.
@server.resource("data://csv/raw")
def get_raw_csv():
    """Return the raw CSV file contents."""

    if not os.path.exists(CSV_FILE):
        return "Error: CSV file not found at " + CSV_FILE

    file_handle = open(CSV_FILE, "r", encoding="utf-8")
    content = file_handle.read()
    file_handle.close()

    return content


# ============================================================
# Step 6: CSV as JSON Resource
# ============================================================
# This resource reads the CSV and converts it to JSON format.
# JSON is often easier for LLMs to understand and work with.
@server.resource("data://csv/as-json")
def get_csv_as_json():
    """Return the CSV data converted to JSON format."""

    headers, rows = read_csv_data()

    if not rows:
        return json.dumps({"error": "No data found", "file": CSV_FILE})

    result = {
        "columns": headers,
        "total_rows": len(rows),
        "data": rows
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 7: CSV Summary Resource
# ============================================================
# This resource provides a summary of the CSV data without
# returning all the rows. Useful for large CSV files where
# you want an overview first.
@server.resource("data://csv/summary")
def get_csv_summary():
    """Return a summary of the CSV data."""

    headers, rows = read_csv_data()

    if not rows:
        return json.dumps({"error": "No data found"})

    # Build the summary
    summary = {
        "file": "sample_data.csv",
        "columns": headers,
        "total_rows": len(rows),
        "column_count": len(headers),
        "first_row": rows[0] if rows else None,
        "last_row": rows[-1] if rows else None
    }

    return json.dumps(summary, indent=2)


# ============================================================
# Step 8: CSV as Formatted Table Resource
# ============================================================
# This resource formats the CSV data as a readable text table.
# This is great for LLMs because they can easily read tabular
# data in this format.
@server.resource("data://csv/formatted-table")
def get_csv_formatted():
    """Return the CSV data as a formatted text table."""

    headers, rows = read_csv_data()

    if not rows:
        return "No data found in CSV file."

    # Calculate column widths
    # Start with header lengths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)

    # Check each row for wider values
    for row in rows:
        for header in headers:
            value = str(row.get(header, ""))
            if len(value) > col_widths[header]:
                col_widths[header] = len(value)

    # Build the header line
    header_parts = []
    for header in headers:
        # Pad each header to its column width
        padded = header.ljust(col_widths[header])
        header_parts.append(padded)
    header_line = " | ".join(header_parts)

    # Build the separator line
    separator_parts = []
    for header in headers:
        separator_parts.append("-" * col_widths[header])
    separator_line = "-+-".join(separator_parts)

    # Build the data lines
    data_lines = []
    for row in rows:
        row_parts = []
        for header in headers:
            value = str(row.get(header, ""))
            padded = value.ljust(col_widths[header])
            row_parts.append(padded)
        data_lines.append(" | ".join(row_parts))

    # Combine everything
    table = header_line + "\n" + separator_line + "\n"
    for line in data_lines:
        table = table + line + "\n"

    return table


# ============================================================
# Step 9: CSV Column Stats Resource
# ============================================================
# This resource tries to compute basic statistics on numeric columns.
# It shows how you can process data before serving it.
@server.resource("data://csv/column-stats")
def get_csv_column_stats():
    """Return basic statistics for numeric columns in the CSV."""

    headers, rows = read_csv_data()

    if not rows:
        return json.dumps({"error": "No data found"})

    # Try to find numeric columns and compute stats
    stats = {}

    for header in headers:
        # Collect all values for this column
        values = []
        for row in rows:
            value_str = row.get(header, "")
            # Try to convert to a number
            try:
                number = float(value_str)
                values.append(number)
            except ValueError:
                # Not a number, skip it
                pass

        # If we found numeric values, compute stats
        if len(values) > 0:
            values.sort()
            total = sum(values)
            count = len(values)
            average = total / count
            minimum = values[0]
            maximum = values[-1]

            stats[header] = {
                "type": "numeric",
                "count": count,
                "min": minimum,
                "max": maximum,
                "average": round(average, 2),
                "sum": total
            }
        else:
            # Non-numeric column -- just count unique values
            unique_values = set()
            for row in rows:
                unique_values.add(row.get(header, ""))

            stats[header] = {
                "type": "text",
                "count": len(rows),
                "unique_values": len(unique_values)
            }

    result = {
        "file": "sample_data.csv",
        "column_statistics": stats
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 10: Run the Server
# ============================================================
if __name__ == "__main__":
    server.run()
