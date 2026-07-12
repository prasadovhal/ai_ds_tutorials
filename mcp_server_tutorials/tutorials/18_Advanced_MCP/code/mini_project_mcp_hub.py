"""
Mini Project - Universal MCP Hub
==================================
A universal hub that manages sub-servers, routes calls,
includes caching, and logs all activity.

Features:
- Register sub-servers by name (each has a tools dict)
- Route tool calls to the correct sub-server
- Cache recent results for faster repeated calls
- Log all calls for auditing
- Hub status dashboard

This is the capstone project for Chapter 18.
"""

import time
from mcp.server.fastmcp import FastMCP

# ============================================================
# Section 1: Sub-Server Registry
# ============================================================

# Registry of sub-servers
# Format: { name: {"description": str, "tools": {tool_name: handler_fn}} }
_servers = {}

# ============================================================
# Section 2: Call Logging
# ============================================================

# Log of all tool calls
# Each entry: {"timestamp": float, "server": str, "tool": str, "args": str, "result": str}
_call_log = []
MAX_LOG_SIZE = 100  # Keep the last 100 calls


def _log_call(server: str, tool: str, args: str, result: str) -> None:
    """Log a tool call for auditing."""
    _call_log.append({
        "timestamp": time.time(),
        "server": server,
        "tool": tool,
        "args": args,
        "result": result[:200],  # Truncate long results
    })
    # Trim log to max size
    while len(_call_log) > MAX_LOG_SIZE:
        _call_log.pop(0)


# ============================================================
# Section 3: Result Cache
# ============================================================

# Cache for tool results
# Format: { cache_key: {"value": str, "timestamp": float} }
_cache = {}
_cache_stats = {"hits": 0, "misses": 0}
CACHE_TTL = 120  # 2 minutes


def _cache_get(key: str) -> str | None:
    """Get a cached result if it exists and hasn't expired."""
    if key not in _cache:
        _cache_stats["misses"] += 1
        return None

    entry = _cache[key]
    if time.time() - entry["timestamp"] > CACHE_TTL:
        del _cache[key]
        _cache_stats["misses"] += 1
        return None

    _cache_stats["hits"] += 1
    return entry["value"]


def _cache_set(key: str, value: str) -> None:
    """Store a result in the cache."""
    _cache[key] = {"value": value, "timestamp": time.time()}


# ============================================================
# Section 4: Built-in Sub-Server Implementations
# ============================================================

def _math_handler(tool: str, args: str) -> str:
    """Handle math operations."""
    parts = [p.strip() for p in args.split(",")]

    if tool == "add":
        a, b = float(parts[0]), float(parts[1])
        return str(a + b)
    elif tool == "subtract":
        a, b = float(parts[0]), float(parts[1])
        return str(a - b)
    elif tool == "multiply":
        a, b = float(parts[0]), float(parts[1])
        return str(a * b)
    elif tool == "divide":
        a, b = float(parts[0]), float(parts[1])
        if b == 0:
            return "Error: Division by zero"
        return str(a / b)
    return f"Unknown math tool: {tool}"


def _text_handler(tool: str, args: str) -> str:
    """Handle text operations."""
    if tool == "upper":
        return args.upper()
    elif tool == "lower":
        return args.lower()
    elif tool == "reverse":
        return args[::-1]
    elif tool == "word_count":
        return str(len(args.split()))
    return f"Unknown text tool: {tool}"


def _data_handler(tool: str, args: str) -> str:
    """Handle data operations with a simple key-value store."""
    # Use a dict attached to the function for persistence
    if not hasattr(_data_handler, "store"):
        _data_handler.store = {}

    if tool == "set":
        parts = args.split(",", 1)
        if len(parts) != 2:
            return "Error: Expected 'key,value'"
        key, value = parts[0].strip(), parts[1].strip()
        _data_handler.store[key] = value
        return f"Stored: {key} = {value}"
    elif tool == "get":
        key = args.strip()
        if key in _data_handler.store:
            return _data_handler.store[key]
        return f"Key '{key}' not found"
    elif tool == "keys":
        if _data_handler.store:
            return ", ".join(sorted(_data_handler.store.keys()))
        return "(empty)"
    elif tool == "count":
        return str(len(_data_handler.store))
    return f"Unknown data tool: {tool}"


# ============================================================
# Section 5: MCP Hub Server
# ============================================================

mcp = FastMCP("UniversalMCPHub")

# Track hub start time for uptime
_hub_start_time = time.time()


@mcp.tool()
def register_server(name: str, tools_csv: str, description: str = "") -> str:
    """
    Register a sub-server with the hub.

    Args:
        name: Unique name for the sub-server (e.g., "math").
        tools_csv: Comma-separated tool names (e.g., "add,subtract").
        description: Description of this sub-server.
    """
    tools_list = [t.strip() for t in tools_csv.split(",") if t.strip()]

    if not tools_list:
        return f"Error: No tools provided for '{name}'."

    _servers[name] = {
        "description": description or f"Server: {name}",
        "tools": {t: True for t in tools_list},  # Simple registry
    }

    return f"Registered '{name}' with tools: {', '.join(tools_list)}"


@mcp.tool()
def list_servers() -> str:
    """
    List all registered sub-servers.
    """
    if not _servers:
        return "No servers registered. Use register_server() first."

    lines = ["Registered Servers:"]
    for name, info in _servers.items():
        tool_count = len(info["tools"])
        lines.append(f"  {name}: {info['description']} ({tool_count} tools)")
    return "\n".join(lines)


@mcp.tool()
def list_all_tools() -> str:
    """
    List all tools across all registered sub-servers.
    """
    if not _servers:
        return "No servers registered."

    lines = ["All Available Tools:"]
    total = 0
    for server_name, info in _servers.items():
        for tool_name in sorted(info["tools"].keys()):
            lines.append(f"  {server_name}.{tool_name}")
            total += 1
    lines.append(f"\nTotal: {total} tools across {len(_servers)} servers")
    return "\n".join(lines)


@mcp.tool()
def route_call(command: str, args: str = "") -> str:
    """
    Route a tool call to a sub-server.
    Uses caching for repeated calls. Logs all calls.

    Args:
        command: Format 'server.tool' (e.g., 'math.add').
        args: Arguments as a string (e.g., '5,3').
    """
    # Parse command
    if "." not in command:
        return f"Error: Use 'server.tool' format (e.g., 'math.add')."

    server_name, tool_name = command.split(".", 1)

    # Check if server is registered
    if server_name not in _servers:
        available = ", ".join(_servers.keys()) if _servers else "none"
        return f"Error: Server '{server_name}' not found. Available: {available}"

    # Check if tool exists on that server
    if tool_name not in _servers[server_name]["tools"]:
        available = ", ".join(_servers[server_name]["tools"].keys())
        return f"Error: Tool '{tool_name}' not on '{server_name}'. Available: {available}"

    # Check cache
    cache_key = f"{command}:{args}"
    cached = _cache_get(cache_key)
    if cached is not None:
        _log_call(server_name, tool_name, args, f"[CACHED] {cached}")
        return f"[CACHED] {cached}"

    # Route to the appropriate handler
    try:
        handlers = {
            "math": _math_handler,
            "text": _text_handler,
            "data": _data_handler,
        }

        if server_name in handlers:
            result = handlers[server_name](tool_name, args)
        else:
            # For dynamically registered servers without handlers
            result = f"[{server_name}.{tool_name}] Simulated with args: {args}"

        # Cache the result
        _cache_set(cache_key, result)

        # Log the call
        _log_call(server_name, tool_name, args, result)

        return f"[{server_name}.{tool_name}] {result}"

    except Exception as e:
        error_msg = f"Error: {e}"
        _log_call(server_name, tool_name, args, error_msg)
        return error_msg


@mcp.tool()
def hub_status() -> str:
    """
    Get the hub status dashboard showing servers, cache, and activity.
    """
    uptime = time.time() - _hub_start_time
    total_calls = len(_call_log)
    cache_total = _cache_stats["hits"] + _cache_stats["misses"]
    cache_hit_rate = (_cache_stats["hits"] / cache_total * 100) if cache_total > 0 else 0.0

    lines = [
        "Universal MCP Hub - Status Dashboard",
        "=" * 45,
        f"  Uptime:         {uptime:.0f}s",
        f"  Servers:        {len(_servers)}",
        f"  Total calls:    {total_calls}",
        "",
        "Cache:",
        f"  Entries:        {len(_cache)}",
        f"  Hits:           {_cache_stats['hits']}",
        f"  Misses:         {_cache_stats['misses']}",
        f"  Hit Rate:       {cache_hit_rate:.1f}%",
        "",
        "Recent Activity (last 5 calls):",
    ]

    # Show last 5 calls
    recent = _call_log[-5:] if _call_log else []
    if recent:
        for entry in reversed(recent):
            elapsed = time.time() - entry["timestamp"]
            lines.append(
                f"  {entry['server']}.{entry['tool']}({entry['args']}) "
                f"-> {entry['result'][:50]} ({elapsed:.0f}s ago)"
            )
    else:
        lines.append("  (no calls yet)")

    lines.append("=" * 45)
    return "\n".join(lines)


# ============================================================
# Section 6: Entry point
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  Universal MCP Hub - Mini Project")
    print("=" * 55)

    # Pre-register the built-in sub-servers
    print("\n--- Registering built-in servers ---")
    print(register_server("math", "add,subtract,multiply,divide", "Math operations"))
    print(register_server("text", "upper,lower,reverse,word_count", "Text tools"))
    print(register_server("data", "set,get,keys,count", "Key-value store"))

    # List everything
    print()
    print(list_all_tools())

    # Route some calls
    print("\n--- Routing calls ---")
    print(route_call("math.add", "10, 20"))
    print(route_call("math.multiply", "6, 7"))
    print(route_call("text.upper", "hello hub"))
    print(route_call("text.reverse", "hello"))
    print(route_call("data.set", "user, Alice"))
    print(route_call("data.get", "user"))

    # Test caching (repeat a call)
    print("\n--- Testing cache ---")
    print(route_call("math.add", "10, 20"))  # Should be CACHED

    # Show hub status
    print()
    print(hub_status())

    print("\n" + "=" * 55)
    print("To run as MCP server: uncomment mcp.run() below")
    print("=" * 55)
    # mcp.run()
