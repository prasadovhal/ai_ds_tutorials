"""
Example 1: Static Resources
============================
This example shows the simplest possible MCP resources: static text and JSON
data that never changes. Static resources return the same content every time
they are read.

Think of static resources like entries in an encyclopedia -- the content is
fixed and does not change between reads.

How to run:
    python example1_static_resources.py

How to test:
    npx @modelcontextprotocol/inspector python example1_static_resources.py
"""

# ============================================================
# Step 1: Import FastMCP
# ============================================================
# FastMCP is the high-level Python framework for building MCP servers.
# It makes creating resources simple with the @server.resource() decorator.
from mcp.server.fastmcp import FastMCP

# We also import json so we can format JSON data nicely
import json

# ============================================================
# Step 2: Create the MCP Server
# ============================================================
# We create a server instance with a name.
# This name is shown to clients when they connect.
server = FastMCP("Static Resources Demo")

# ============================================================
# Step 3: Define a Simple Text Resource
# ============================================================
# The @server.resource() decorator registers a function as a resource.
# The first argument is the URI -- the unique identifier for this resource.
# When a client requests this URI, the function is called and its return
# value becomes the resource content.
#
# This resource returns the application name as plain text.
# It will always return the same value -- that is what makes it "static".
@server.resource("info://app/name")
def get_app_name():
    """Return the name of this application."""
    # Simply return a string -- FastMCP handles the rest
    return "MCP Resources Demo Server"


# ============================================================
# Step 4: Define Another Text Resource
# ============================================================
# This resource returns the application version.
# Again, it is static -- the version does not change while the server runs.
@server.resource("info://app/version")
def get_app_version():
    """Return the current version of the application."""
    return "2.1.0"


# ============================================================
# Step 5: Define a JSON Resource
# ============================================================
# Resources can return structured data too.
# Here we return a JSON string with application statistics.
# We use json.dumps() to convert a Python dictionary to a JSON string.
# The indent=2 makes it human-readable.
@server.resource("data://app/stats")
def get_app_stats():
    """Return application statistics in JSON format."""

    # Create a dictionary with our data
    stats = {
        "total_users": 1250,
        "active_sessions": 42,
        "uptime_hours": 720,
        "version": "2.1.0",
        "server_name": "MCP Resources Demo"
    }

    # Convert to a nicely formatted JSON string
    stats_json = json.dumps(stats, indent=2)

    return stats_json


# ============================================================
# Step 6: Define a Multi-line Text Resource
# ============================================================
# Resources can return longer text too.
# This resource returns a help message with multiple lines.
@server.resource("docs://app/help")
def get_help_text():
    """Return help documentation for this application."""

    help_text = """
Welcome to the MCP Resources Demo Server!

This server demonstrates how MCP resources work.

Available Resources:
- info://app/name      : Get the application name
- info://app/version   : Get the application version
- data://app/stats     : Get application statistics (JSON)
- docs://app/help      : This help text
- data://app/features  : List of features (JSON)

To read a resource, use the resources/read method with the URI.
"""
    return help_text


# ============================================================
# Step 7: Define a JSON List Resource
# ============================================================
# This resource returns a JSON array of features.
# It shows that resources can return any JSON structure.
@server.resource("data://app/features")
def get_features():
    """Return a list of application features in JSON format."""

    features = [
        {
            "name": "Static Resources",
            "description": "Serve unchanging data to clients",
            "status": "active"
        },
        {
            "name": "Dynamic Resources",
            "description": "Serve data that changes on each read",
            "status": "active"
        },
        {
            "name": "Resource Templates",
            "description": "Parameterized resource URIs",
            "status": "active"
        },
        {
            "name": "File Resources",
            "description": "Serve files from the filesystem",
            "status": "active"
        }
    ]

    features_json = json.dumps(features, indent=2)

    return features_json


# ============================================================
# Step 8: Run the Server
# ============================================================
# This starts the MCP server using STDIO transport.
# The server will listen for MCP protocol messages on stdin/stdout.
# Clients (like Claude Desktop or MCP Inspector) connect to this server
# and can list and read all the resources we defined above.
if __name__ == "__main__":
    # Run the server -- this blocks and waits for client connections
    server.run()
