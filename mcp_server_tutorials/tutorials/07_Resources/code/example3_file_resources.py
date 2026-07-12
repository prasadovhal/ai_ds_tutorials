"""
Example 3: File Resources
===========================
This example shows how to serve local files as MCP resources. This is one
of the most common use cases -- letting an LLM read configuration files,
documentation, data files, and other files from your filesystem.

Think of this like a file server: the MCP server reads files from disk
and delivers their content to the client.

IMPORTANT: Always validate file paths to prevent security issues!

How to run:
    python example3_file_resources.py

How to test:
    npx @modelcontextprotocol/inspector python example3_file_resources.py
"""

# ============================================================
# Step 1: Import Everything We Need
# ============================================================
from mcp.server.fastmcp import FastMCP
import json
import os

# ============================================================
# Step 2: Create the MCP Server
# ============================================================
server = FastMCP("File Resources Demo")

# ============================================================
# Step 3: Figure Out Where Our Data Files Are
# ============================================================
# We need to know the directory where this script lives,
# because our sample data files are in the same directory.
# os.path.dirname gets the directory part of a file path.
# os.path.abspath makes it an absolute path (no relative parts).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# Step 4: Helper Function to Safely Read a File
# ============================================================
# This function reads a file but first checks that:
# 1. The file exists
# 2. The file is within our allowed directory (security!)
# We do NOT use this as a decorator or nested function -- just a
# simple function we call from our resource handlers.
def safe_read_file(filename):
    """
    Read a file safely from our data directory.

    Args:
        filename: Name of the file to read (just the name, not a path)

    Returns:
        The file contents as a string, or an error message
    """
    # Build the full path to the file
    file_path = os.path.join(SCRIPT_DIR, filename)

    # Security check: make sure the resolved path is still in our directory.
    # os.path.realpath resolves any ".." or symlinks in the path.
    real_path = os.path.realpath(file_path)
    real_dir = os.path.realpath(SCRIPT_DIR)

    # Check that the file is inside our allowed directory
    if not real_path.startswith(real_dir):
        return "Error: Access denied. File is outside the allowed directory."

    # Check that the file exists
    if not os.path.exists(file_path):
        return "Error: File '" + filename + "' not found."

    # Check that it is a file (not a directory)
    if not os.path.isfile(file_path):
        return "Error: '" + filename + "' is not a file."

    # Read and return the file contents
    # We use encoding='utf-8' to handle special characters properly
    file_handle = open(file_path, "r", encoding="utf-8")
    content = file_handle.read()
    file_handle.close()

    return content


# ============================================================
# Step 5: Serve the Sample JSON File as a Resource
# ============================================================
# This resource reads sample_data.json from disk and serves its contents.
# The URI tells clients this is a file resource.
@server.resource("file://data/sample-json")
def get_sample_json():
    """Read and return the sample JSON data file."""

    content = safe_read_file("sample_data.json")

    return content


# ============================================================
# Step 6: Serve the Sample CSV File as a Resource
# ============================================================
# This resource reads sample_data.csv from disk and serves its contents.
@server.resource("file://data/sample-csv")
def get_sample_csv():
    """Read and return the sample CSV data file."""

    content = safe_read_file("sample_data.csv")

    return content


# ============================================================
# Step 7: Serve a File Listing Resource
# ============================================================
# This resource scans the data directory and returns a list of
# all available files. This helps clients know what they can read.
@server.resource("file://data/listing")
def get_file_listing():
    """Return a listing of all available data files."""

    # Get all files in the script directory
    all_items = os.listdir(SCRIPT_DIR)

    # Filter to only include data files (not Python scripts)
    data_files = []
    for item in all_items:
        # Skip Python files and hidden files
        if item.endswith(".py"):
            continue
        if item.startswith("."):
            continue

        # Get file info
        file_path = os.path.join(SCRIPT_DIR, item)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            data_files.append({
                "name": item,
                "size_bytes": file_size,
                "type": os.path.splitext(item)[1]  # File extension
            })

    # Build the result
    result = {
        "directory": SCRIPT_DIR,
        "total_files": len(data_files),
        "files": data_files
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 8: Serve a Resource with File Metadata
# ============================================================
# Sometimes clients want to know about a file without reading
# its full contents. This resource provides metadata only.
@server.resource("file://data/sample-json/metadata")
def get_json_metadata():
    """Return metadata about the sample JSON file without its full contents."""

    file_path = os.path.join(SCRIPT_DIR, "sample_data.json")

    # Check if the file exists
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})

    # Gather metadata
    file_stat = os.stat(file_path)

    metadata = {
        "filename": "sample_data.json",
        "size_bytes": file_stat.st_size,
        "last_modified": str(file_stat.st_mtime),
        "file_type": "JSON",
        "mime_type": "application/json",
        "readable": os.access(file_path, os.R_OK)
    }

    return json.dumps(metadata, indent=2)


# ============================================================
# Step 9: Run the Server
# ============================================================
if __name__ == "__main__":
    # Start the server
    server.run()
