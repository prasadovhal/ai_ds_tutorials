"""
Example 5 - Test Server for AI App Integration
===============================================
A simple MCP server with an echo tool, a server_info resource,
and a greeting prompt. Use this server to verify that any AI
application (Claude Desktop, VS Code, Cursor, etc.) can correctly
connect to and interact with an MCP server.
"""

from mcp.server.fastmcp import FastMCP

# Create the test server
mcp = FastMCP("Test Server")


# --- Tool: echo ---
# A simple tool that echoes back whatever text you send
# Great for testing if tools work in your AI app
@mcp.tool()
def echo(text: str) -> str:
    """Echo back the given text. Use this to test tool connectivity."""
    return f"Echo: {text}"


# --- Resource: server_info ---
# A resource that returns info about this server
# Tests if your AI app can read MCP resources
@mcp.resource("info://server")
def server_info() -> str:
    """Return information about this test server."""
    return (
        "Server Name: Test Server\n"
        "Version: 1.0.0\n"
        "Purpose: Testing MCP integration with AI applications\n"
        "Tools: echo\n"
        "Resources: info://server\n"
        "Prompts: greeting"
    )


# --- Prompt: greeting ---
# A prompt template for generating greetings
# Tests if your AI app can use MCP prompts
@mcp.prompt()
def greeting(name: str) -> str:
    """Generate a friendly greeting for the given name."""
    return f"Please write a warm, friendly greeting for {name}. Be creative and cheerful!"


if __name__ == "__main__":
    # Run the server using stdio transport
    # AI apps will start this server and communicate via stdin/stdout
    print("Starting Test Server...")
    print("This server provides:")
    print("  - Tool: echo(text) - echoes back text")
    print("  - Resource: info://server - server information")
    print("  - Prompt: greeting(name) - greeting template")
    mcp.run()
