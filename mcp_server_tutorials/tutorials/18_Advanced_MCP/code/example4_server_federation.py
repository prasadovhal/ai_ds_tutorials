"""
Example 4 - Server Federation (Hub Pattern)
=============================================
A hub server that manages a registry of sub-servers.
Each sub-server has its own set of tools.
The hub routes requests to the appropriate sub-server.
This is a simulated federation -- all in one process.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Sub-server registry
# ============================================================

# Registry of sub-servers
# Format: { server_name: {"tools": [str], "description": str} }
_registry = {}


# ============================================================
# Step 2: Simulated sub-server handlers
# ============================================================

def _handle_tool_call(server_name: str, tool_name: str, args: str) -> str:
    """
    Simulate routing a tool call to a sub-server.
    In a real system, this would make a network call.
    """
    # Simple simulated responses
    return (
        f"[{server_name}] Executed '{tool_name}' "
        f"with args: {args} -> Result: OK"
    )


# ============================================================
# Step 3: MCP hub server
# ============================================================

mcp = FastMCP("FederationHub")


@mcp.tool()
def register_server(name: str, tools_csv: str, description: str = "") -> str:
    """
    Register a sub-server with its available tools.

    Args:
        name: Name of the sub-server (e.g., "math_server").
        tools_csv: Comma-separated list of tool names (e.g., "add,subtract,multiply").
        description: Optional description of the sub-server.
    """
    # Parse the comma-separated tools list
    tools = [t.strip() for t in tools_csv.split(",") if t.strip()]

    if not tools:
        return f"Error: No tools provided for '{name}'."

    _registry[name] = {
        "tools": tools,
        "description": description or f"Sub-server: {name}",
    }
    return f"Registered '{name}' with {len(tools)} tools: {', '.join(tools)}"


@mcp.tool()
def route_request(server_name: str, tool_name: str, args: str = "") -> str:
    """
    Route a tool call to a registered sub-server.

    Args:
        server_name: Name of the target sub-server.
        tool_name: Name of the tool to call.
        args: Arguments to pass to the tool (as string).
    """
    # Check if server exists
    if server_name not in _registry:
        available = ", ".join(_registry.keys()) if _registry else "none"
        return f"Error: Server '{server_name}' not found. Available: {available}"

    # Check if tool exists on that server
    server = _registry[server_name]
    if tool_name not in server["tools"]:
        available = ", ".join(server["tools"])
        return (
            f"Error: Tool '{tool_name}' not found on '{server_name}'. "
            f"Available: {available}"
        )

    # Route the request (simulated)
    return _handle_tool_call(server_name, tool_name, args)


@mcp.tool()
def list_servers() -> str:
    """
    List all registered sub-servers and their tool counts.
    """
    if not _registry:
        return "No sub-servers registered yet."

    lines = ["Registered Sub-Servers:"]
    for name, info in _registry.items():
        tool_count = len(info["tools"])
        lines.append(f"  {name}: {info['description']} ({tool_count} tools)")
    return "\n".join(lines)


@mcp.tool()
def list_all_tools() -> str:
    """
    List all tools across all registered sub-servers.
    Shows which server each tool belongs to.
    """
    if not _registry:
        return "No sub-servers registered yet."

    lines = ["All Available Tools:"]
    total = 0
    for server_name, info in _registry.items():
        for tool in info["tools"]:
            lines.append(f"  {server_name}/{tool}")
            total += 1
    lines.append(f"\nTotal: {total} tools across {len(_registry)} servers")
    return "\n".join(lines)


# ============================================================
# Step 4: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Server Federation Hub - Demo")
    print("=" * 50)

    # Register some sub-servers
    print(register_server("math", "add,subtract,multiply,divide", "Math operations"))
    print(register_server("text", "uppercase,lowercase,reverse", "Text processing"))
    print(register_server("data", "store,retrieve,delete", "Data storage"))

    # List servers
    print()
    print(list_servers())

    # List all tools
    print()
    print(list_all_tools())

    # Route some requests
    print()
    print("--- Routing Requests ---")
    print(route_request("math", "add", "a=2, b=3"))
    print(route_request("text", "uppercase", "hello world"))
    print(route_request("data", "store", "key=name, value=Alice"))

    # Test error cases
    print()
    print("--- Error Cases ---")
    print(route_request("unknown", "tool1", ""))
    print(route_request("math", "unknown_tool", ""))

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
