"""
Example 2: Server with a Resource
===================================
This server exposes a RESOURCE - read-only data that clients
can access. Think of resources as files or documents the
server shares.

In this example, we expose server information as a resource.

What you will learn:
    - How to register a resource with @server.resource()
    - How resources have URIs (like URLs)
    - How resources differ from tools (read-only, no side effects)

How to run:
    poetry run mcp dev example2_server_with_resource.py

How to test:
    Open MCP Inspector
    Go to the Resources tab
    Click on "info://server"
    You should see the server information text
"""

# ============================================================
# STEP 1: Import what we need
# ============================================================
from mcp.server.fastmcp import FastMCP

# We import platform and datetime to get real system info
# for our resource. This makes the resource dynamic and useful.
import platform
import datetime

# ============================================================
# STEP 2: Create the server
# ============================================================
server = FastMCP("ResourceServer")

# ============================================================
# STEP 3: Register a resource
# ============================================================
# The @server.resource() decorator registers this function
# as an MCP resource.
#
# The string "info://server" is the resource URI.
# URI = Uniform Resource Identifier (like a URL).
# Clients use this URI to READ the resource.
#
# Think of the URI as the "address" of the resource.
# Just like a URL points to a web page, a resource URI
# points to data on the server.
#
# Common URI patterns:
#   info://server      -> server information
#   file:///path/to    -> file content
#   db://table/count   -> database query result
#   config://settings  -> configuration data
@server.resource("info://server")
def get_server_info() -> str:
    """Get information about this MCP server."""

    # Build the info string with real system data
    # We use a simple multi-line string for readability
    server_name = "ResourceServer"
    python_version = platform.python_version()
    operating_system = platform.system()
    os_version = platform.version()
    machine_type = platform.machine()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build the response as a simple text string
    info_text = f"""Server Name: {server_name}
Python Version: {python_version}
Operating System: {operating_system}
OS Version: {os_version}
Machine: {machine_type}
Current Time: {current_time}
Status: Running
MCP Protocol: Supported"""

    return info_text

# ============================================================
# STEP 4: Add a second resource to show you can have many
# ============================================================
# You can register as many resources as you want.
# Each one needs a unique URI.
@server.resource("info://help")
def get_help_info() -> str:
    """Get help information about using this server."""

    help_text = """Welcome to ResourceServer!

This server provides information resources.

Available Resources:
  - info://server  : Get server information (OS, Python version, etc.)
  - info://help    : This help text

How to use:
  1. Connect to this server using an MCP client
  2. List available resources using resources/list
  3. Read a resource using resources/read with the URI

This is a read-only server. Resources cannot be modified."""

    return help_text

# ============================================================
# STEP 5: Run the server
# ============================================================
if __name__ == "__main__":
    server.run()
