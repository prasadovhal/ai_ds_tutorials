"""
Mini Project: Document Library Server
=======================================
This MCP server acts as a document library. It serves files from
a "documents" directory and provides tools to list and search
documents by keyword.

What this server does:
    1. Serves each file in the "documents" folder as a resource
    2. Provides a "list_documents" tool that shows all available files
    3. Provides a "search_documents" tool that searches file contents
       for a keyword and returns matching files with snippets

How it works:
    - On startup, the server scans a "documents" directory
    - Each file becomes a resource at "docs://library/<filename>"
    - The list_documents tool returns a summary of all files
    - The search_documents tool reads each file and checks for
      the search keyword (case-insensitive)

How to run:
    1. Create a "documents" folder next to this script
    2. Put some .txt or .md files in it
    3. Run: python mini_project_document_server.py

How to test:
    npx @modelcontextprotocol/inspector python mini_project_document_server.py
"""

# ============================================================
# Step 1: Import required libraries
# ============================================================
from mcp.server.fastmcp import FastMCP

# os module to work with files and directories
import os

# json module to format data nicely
import json

# ============================================================
# Step 2: Set up the documents directory
# ============================================================
# We look for a "documents" folder in the same directory as this script.
# If the folder does not exist, we create it and add some sample files.

# Get the directory where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# The documents folder path
DOCUMENTS_DIR = os.path.join(SCRIPT_DIR, "documents")


def ensure_documents_directory():
    """
    Make sure the documents directory exists.
    If it does not exist, create it and add sample files
    so the server has something to serve.
    """

    # Create the directory if it does not exist
    if not os.path.exists(DOCUMENTS_DIR):
        os.makedirs(DOCUMENTS_DIR)
        print(f"Created documents directory: {DOCUMENTS_DIR}")

        # Create some sample documents so the demo works right away
        create_sample_documents()
    else:
        print(f"Documents directory found: {DOCUMENTS_DIR}")


def create_sample_documents():
    """
    Create a few sample text files in the documents directory.
    These are just for demonstration purposes.
    """

    # Sample document 1: Python introduction
    python_doc = """Introduction to Python
======================

Python is a high-level, interpreted programming language.
It was created by Guido van Rossum and first released in 1991.

Key Features:
- Easy to read and write
- Dynamic typing
- Extensive standard library
- Large community and ecosystem

Python is widely used in web development, data science,
machine learning, automation, and scripting.
"""

    # Sample document 2: MCP overview
    mcp_doc = """Model Context Protocol (MCP) Overview
=======================================

The Model Context Protocol (MCP) is an open standard created
by Anthropic. It provides a standardized way for AI applications
to connect to external data sources and tools.

Key Concepts:
- Server: Provides tools, resources, and prompts
- Client: Connects to servers and uses their capabilities
- Transport: The communication channel (STDIO, HTTP, SSE)
- Tools: Functions the AI can call
- Resources: Data the AI can read

MCP uses JSON-RPC 2.0 for all communication.
"""

    # Sample document 3: Getting started guide
    guide_doc = """Getting Started Guide
======================

Welcome to the Document Library Server!

This server demonstrates how MCP resources can serve files
from a directory on your computer.

How to use:
1. Add .txt or .md files to the 'documents' folder
2. Start the server
3. Connect with an MCP client
4. Browse and search your documents

Tips:
- The server scans the documents folder on startup
- Use the search_documents tool to find content
- Use the list_documents tool to see all files
"""

    # Write the sample files
    samples = {
        "python_intro.txt": python_doc,
        "mcp_overview.txt": mcp_doc,
        "getting_started.txt": guide_doc,
    }

    for filename, content in samples.items():
        file_path = os.path.join(DOCUMENTS_DIR, filename)
        file_handle = open(file_path, "w", encoding="utf-8")
        file_handle.write(content)
        file_handle.close()
        print(f"  Created sample document: {filename}")


# ============================================================
# Step 3: Helper functions to read and list documents
# ============================================================

def get_all_document_names():
    """
    Get a list of all file names in the documents directory.
    Only includes files (not subdirectories).

    Returns:
        A list of file name strings.
    """
    all_names = []

    # List everything in the documents directory
    if not os.path.exists(DOCUMENTS_DIR):
        return all_names

    for item in os.listdir(DOCUMENTS_DIR):
        # Build the full path to check if it is a file
        full_path = os.path.join(DOCUMENTS_DIR, item)

        # Only include files, not directories
        if os.path.isfile(full_path):
            all_names.append(item)

    # Sort alphabetically for consistent ordering
    all_names.sort()

    return all_names


def read_document(filename):
    """
    Read the content of a single document file.

    Args:
        filename: The name of the file to read.

    Returns:
        The file content as a string, or an error message.
    """
    file_path = os.path.join(DOCUMENTS_DIR, filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return f"Error: File '{filename}' not found."

    # Read and return the file content
    try:
        file_handle = open(file_path, "r", encoding="utf-8")
        content = file_handle.read()
        file_handle.close()
        return content
    except Exception as e:
        return f"Error reading '{filename}': {e}"


# ============================================================
# Step 4: Create the MCP Server
# ============================================================
# Make sure the documents directory exists before creating the server
ensure_documents_directory()

server = FastMCP("Document Library Server")


# ============================================================
# Step 5: Create a resource for each document file
# ============================================================
# We use a resource template so that any file in the documents
# directory can be accessed by its name.
# The URI pattern is: docs://library/<filename>
#
# WHY a template? Because we do not know ahead of time how many
# files will be in the directory. A template lets the client
# request any file by name.
@server.resource("docs://library/{filename}")
def get_document(filename: str):
    """Return the content of a specific document by filename."""

    # Read the document file
    content = read_document(filename)
    return content


# ============================================================
# Step 6: Create a resource that lists all documents
# ============================================================
# This resource gives clients a way to discover what documents
# are available without having to guess file names.
@server.resource("docs://library/index")
def get_document_index():
    """Return a JSON index of all available documents."""

    # Get all file names
    file_names = get_all_document_names()

    # Build an index with file info
    index_entries = []
    for name in file_names:
        file_path = os.path.join(DOCUMENTS_DIR, name)

        # Get file size in bytes
        file_size = os.path.getsize(file_path)

        entry = {
            "filename": name,
            "uri": f"docs://library/{name}",
            "size_bytes": file_size,
        }
        index_entries.append(entry)

    # Build the full index
    index = {
        "total_documents": len(index_entries),
        "documents_directory": DOCUMENTS_DIR,
        "documents": index_entries,
    }

    return json.dumps(index, indent=2)


# ============================================================
# Step 7: Create the list_documents tool
# ============================================================
# WHY a tool and not just a resource? Because tools can be
# called by the AI agent to get information during a conversation.
# The resource is for direct client access; the tool is for
# AI-driven access.
@server.tool()
def list_documents() -> str:
    """
    List all documents available in the library.

    Returns:
        A formatted list of all document files with their sizes.
    """

    # Get all file names
    file_names = get_all_document_names()

    # Check if there are any documents
    if len(file_names) == 0:
        return "No documents found. Add .txt or .md files to the 'documents' directory."

    # Build a formatted list
    lines = []
    lines.append(f"Document Library ({len(file_names)} files)")
    lines.append("=" * 50)

    for name in file_names:
        file_path = os.path.join(DOCUMENTS_DIR, name)
        file_size = os.path.getsize(file_path)

        # Show size in a human-friendly way
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        else:
            size_str = f"{file_size / 1024:.1f} KB"

        lines.append(f"  - {name} ({size_str})")
        lines.append(f"    URI: docs://library/{name}")

    lines.append("")
    lines.append("Use search_documents(keyword) to search file contents.")

    return "\n".join(lines)


# ============================================================
# Step 8: Create the search_documents tool
# ============================================================
# This tool searches through all documents for a keyword.
# It returns matching files along with snippets showing
# where the keyword appears.
@server.tool()
def search_documents(keyword: str) -> str:
    """
    Search all documents for a keyword.

    Performs a case-insensitive search across all document files.
    Returns matching files with context snippets showing where
    the keyword was found.

    Args:
        keyword: The text to search for in document contents.

    Returns:
        A report of matching documents with snippets.
    """

    # Validate the keyword
    if not keyword or len(keyword.strip()) == 0:
        return "Error: Please provide a keyword to search for."

    keyword_lower = keyword.lower().strip()

    # Get all file names
    file_names = get_all_document_names()

    if len(file_names) == 0:
        return "No documents to search. Add files to the 'documents' directory."

    # Search each file
    matches = []

    for name in file_names:
        content = read_document(name)
        content_lower = content.lower()

        # Check if the keyword appears in this file
        if keyword_lower in content_lower:
            # Find the position of the first match
            position = content_lower.find(keyword_lower)

            # Extract a snippet around the match (50 chars before and after)
            snippet_start = max(0, position - 50)
            snippet_end = min(len(content), position + len(keyword) + 50)
            snippet = content[snippet_start:snippet_end].strip()

            # Replace newlines in snippet for cleaner display
            snippet = snippet.replace("\n", " ")

            # Count how many times the keyword appears
            count = content_lower.count(keyword_lower)

            match_info = {
                "filename": name,
                "occurrences": count,
                "snippet": snippet,
            }
            matches.append(match_info)

    # Build the results report
    if len(matches) == 0:
        return f"No documents contain the keyword '{keyword}'."

    lines = []
    lines.append(f"Search Results for '{keyword}'")
    lines.append("=" * 50)
    lines.append(f"Found in {len(matches)} document(s):")
    lines.append("")

    for match in matches:
        lines.append(f"  File: {match['filename']}")
        lines.append(f"  Occurrences: {match['occurrences']}")
        lines.append(f"  Snippet: ...{match['snippet']}...")
        lines.append(f"  URI: docs://library/{match['filename']}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# Step 9: Run the Server
# ============================================================
if __name__ == "__main__":
    print("Starting Document Library Server...")
    print(f"Serving documents from: {DOCUMENTS_DIR}")
    server.run()
