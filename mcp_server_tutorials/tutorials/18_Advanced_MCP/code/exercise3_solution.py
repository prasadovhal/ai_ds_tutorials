"""
Exercise 3 Solution - Federation of 3 Sub-Servers
===================================================
A hub with math_server, text_server, and data_server.
Routes calls based on "server.tool" prefix format.
Each sub-server has real implemented logic.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Sub-server implementations
# ============================================================

# --- Math Server ---

def math_add(args: str) -> str:
    """Add two numbers. Args format: 'a,b'"""
    a, b = _parse_two_numbers(args)
    return str(a + b)


def math_subtract(args: str) -> str:
    """Subtract b from a. Args format: 'a,b'"""
    a, b = _parse_two_numbers(args)
    return str(a - b)


def math_multiply(args: str) -> str:
    """Multiply two numbers. Args format: 'a,b'"""
    a, b = _parse_two_numbers(args)
    return str(a * b)


def math_divide(args: str) -> str:
    """Divide a by b. Args format: 'a,b'"""
    a, b = _parse_two_numbers(args)
    if b == 0:
        return "Error: Division by zero"
    return str(a / b)


def _parse_two_numbers(args: str) -> tuple:
    """Helper: parse 'a,b' into two floats."""
    parts = args.split(",")
    if len(parts) != 2:
        raise ValueError("Expected format: 'a,b' (two numbers)")
    return float(parts[0].strip()), float(parts[1].strip())


# --- Text Server ---

def text_uppercase(args: str) -> str:
    """Convert text to uppercase."""
    return args.upper()


def text_lowercase(args: str) -> str:
    """Convert text to lowercase."""
    return args.lower()


def text_reverse(args: str) -> str:
    """Reverse a string."""
    return args[::-1]


def text_length(args: str) -> str:
    """Get the length of a string."""
    return str(len(args))


# --- Data Server ---

# Simple in-memory key-value store
_data_store = {}


def data_store(args: str) -> str:
    """Store a key-value pair. Args format: 'key,value'"""
    parts = args.split(",", 1)
    if len(parts) != 2:
        return "Error: Expected format 'key,value'"
    key = parts[0].strip()
    value = parts[1].strip()
    _data_store[key] = value
    return f"Stored '{key}' = '{value}'"


def data_retrieve(args: str) -> str:
    """Retrieve a value by key."""
    key = args.strip()
    if key not in _data_store:
        return f"Error: Key '{key}' not found"
    return _data_store[key]


def data_delete(args: str) -> str:
    """Delete a key-value pair."""
    key = args.strip()
    if key not in _data_store:
        return f"Error: Key '{key}' not found"
    del _data_store[key]
    return f"Deleted '{key}'"


def data_list_keys(args: str) -> str:
    """List all keys in the store."""
    if not _data_store:
        return "Store is empty"
    return ", ".join(sorted(_data_store.keys()))


# ============================================================
# Step 2: Server registry mapping
# ============================================================

# Maps server_name -> {tool_name -> handler_function}
SERVERS = {
    "math": {
        "add": math_add,
        "subtract": math_subtract,
        "multiply": math_multiply,
        "divide": math_divide,
    },
    "text": {
        "uppercase": text_uppercase,
        "lowercase": text_lowercase,
        "reverse": text_reverse,
        "length": text_length,
    },
    "data": {
        "store": data_store,
        "retrieve": data_retrieve,
        "delete": data_delete,
        "list_keys": data_list_keys,
    },
}

# ============================================================
# Step 3: MCP hub server
# ============================================================

mcp = FastMCP("FederationHub")


@mcp.tool()
def route_call(command: str, args: str = "") -> str:
    """
    Route a call to a sub-server.
    Command format: 'server.tool' (e.g., 'math.add').
    Args are passed as a string to the tool handler.

    Examples:
        route_call('math.add', '5,3')        -> '8.0'
        route_call('text.uppercase', 'hello') -> 'HELLO'
        route_call('data.store', 'key,value') -> stored
    """
    # Parse the command into server and tool
    if "." not in command:
        return (
            f"Error: Invalid format '{command}'. "
            f"Use 'server.tool' format (e.g., 'math.add')."
        )

    server_name, tool_name = command.split(".", 1)

    # Find the server
    if server_name not in SERVERS:
        available = ", ".join(SERVERS.keys())
        return f"Error: Server '{server_name}' not found. Available: {available}"

    # Find the tool
    server_tools = SERVERS[server_name]
    if tool_name not in server_tools:
        available = ", ".join(server_tools.keys())
        return (
            f"Error: Tool '{tool_name}' not found on '{server_name}'. "
            f"Available: {available}"
        )

    # Execute the tool
    try:
        handler = server_tools[tool_name]
        result = handler(args)
        return f"[{server_name}.{tool_name}] {result}"
    except Exception as e:
        return f"Error in {command}: {e}"


@mcp.tool()
def list_all() -> str:
    """
    List all sub-servers and their available tools.
    """
    lines = ["Federation Hub - Available Commands:"]
    total_tools = 0

    for server_name, tools in SERVERS.items():
        lines.append(f"\n  {server_name}:")
        for tool_name in sorted(tools.keys()):
            lines.append(f"    {server_name}.{tool_name}")
            total_tools += 1

    lines.append(f"\nTotal: {total_tools} tools across {len(SERVERS)} servers")
    return "\n".join(lines)


# ============================================================
# Step 4: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 3 Solution: Federation of 3 Servers")
    print("=" * 50)

    # List all available tools
    print(list_all())

    # Demo math operations
    print("\n--- Math Server ---")
    print(route_call("math.add", "10, 5"))
    print(route_call("math.subtract", "10, 5"))
    print(route_call("math.multiply", "10, 5"))
    print(route_call("math.divide", "10, 3"))

    # Demo text operations
    print("\n--- Text Server ---")
    print(route_call("text.uppercase", "hello world"))
    print(route_call("text.reverse", "hello"))
    print(route_call("text.length", "hello world"))

    # Demo data operations
    print("\n--- Data Server ---")
    print(route_call("data.store", "name, Alice"))
    print(route_call("data.store", "city, London"))
    print(route_call("data.retrieve", "name"))
    print(route_call("data.list_keys", ""))
    print(route_call("data.delete", "name"))
    print(route_call("data.list_keys", ""))

    # Error cases
    print("\n--- Error Cases ---")
    print(route_call("unknown.tool", ""))
    print(route_call("math.unknown", ""))
    print(route_call("bad_format", ""))

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
