"""
Filesystem MCP Server
=====================
Provides tools for basic file system operations:
listing files, reading, writing, file info, and creating directories.
Uses os and pathlib modules.
"""

# Import FastMCP and file system modules
from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path
from datetime import datetime

# Create the MCP server instance
server = FastMCP("Filesystem Server")


# --- Tool: List files in a directory ---
@server.tool()
def list_files(path: str) -> str:
    """List all files and directories at the given path."""
    target = Path(path)

    # Check if path exists
    if not target.exists():
        return f"Error: Path '{path}' does not exist."

    # Check if it's a directory
    if not target.is_dir():
        return f"Error: '{path}' is not a directory."

    # List all items in the directory
    items = []
    for item in sorted(target.iterdir()):
        # Mark directories with a trailing slash
        if item.is_dir():
            items.append(f"  [DIR]  {item.name}/")
        else:
            # Show file size
            size = item.stat().st_size
            items.append(f"  [FILE] {item.name} ({size} bytes)")

    if not items:
        return f"Directory '{path}' is empty."

    return f"Contents of '{path}':\n" + "\n".join(items)


# --- Tool: Read a file ---
@server.tool()
def read_file(path: str) -> str:
    """Read and return the contents of a text file."""
    target = Path(path)

    # Check if file exists
    if not target.exists():
        return f"Error: File '{path}' does not exist."

    # Check if it's a file (not a directory)
    if not target.is_file():
        return f"Error: '{path}' is not a file."

    try:
        # Read the file contents
        content = target.read_text(encoding="utf-8")
        return f"Contents of '{path}':\n{content}"
    except UnicodeDecodeError:
        return f"Error: '{path}' is not a text file (binary content)."


# --- Tool: Write content to a file ---
@server.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file. Creates the file if it doesn't exist."""
    target = Path(path)

    try:
        # Create parent directories if they don't exist
        target.parent.mkdir(parents=True, exist_ok=True)

        # Write the content to the file
        target.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except PermissionError:
        return f"Error: Permission denied writing to '{path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


# --- Tool: Get file information ---
@server.tool()
def file_info(path: str) -> str:
    """Get detailed information about a file or directory."""
    target = Path(path)

    # Check if path exists
    if not target.exists():
        return f"Error: '{path}' does not exist."

    # Get file stats
    stat = target.stat()

    # Format timestamps
    created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

    # Build the info string
    info = f"""
File Info for '{path}':
  Name: {target.name}
  Type: {'Directory' if target.is_dir() else 'File'}
  Size: {stat.st_size} bytes
  Created: {created}
  Modified: {modified}
  Extension: {target.suffix if target.suffix else 'None'}
  Absolute Path: {target.resolve()}
"""
    return info.strip()


# --- Tool: Create a directory ---
@server.tool()
def create_directory(path: str) -> str:
    """Create a new directory (including parent directories if needed)."""
    target = Path(path)

    # Check if it already exists
    if target.exists():
        return f"'{path}' already exists."

    try:
        # Create the directory and any missing parents
        target.mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory '{path}'."
    except PermissionError:
        return f"Error: Permission denied creating '{path}'."
    except Exception as e:
        return f"Error creating directory: {str(e)}"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
