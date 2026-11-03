"""
JSON Tools MCP Server
=====================
Provides tools for working with JSON data:
validate, format/pretty-print, extract values, and compare JSON objects.
"""

# Import FastMCP and json module
from mcp.server.fastmcp import FastMCP
import json

# Create the MCP server instance
server = FastMCP("JSON Tools Server")


# --- Tool: Validate JSON ---
@server.tool()
def validate_json(json_str: str) -> str:
    """Check if a string is valid JSON."""
    try:
        json.loads(json_str)
        return "Valid JSON!"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"


# --- Tool: Format/pretty-print JSON ---
@server.tool()
def format_json(json_str: str, indent: int = 2) -> str:
    """Pretty-print a JSON string with indentation."""
    try:
        data = json.loads(json_str)
        formatted = json.dumps(data, indent=indent, ensure_ascii=False)
        return f"Formatted JSON:\n\n{formatted}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {str(e)}"


# --- Tool: Get a value by key ---
@server.tool()
def get_value(json_str: str, key: str) -> str:
    """
    Get a value from a JSON object by key.
    Supports dot notation for nested keys, e.g., 'user.name'.
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {str(e)}"

    # Support dot notation for nested access
    keys = key.split(".")
    current = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        elif isinstance(current, list):
            # Try to use the key as an index
            try:
                index = int(k)
                current = current[index]
            except (ValueError, IndexError):
                return f"Key '{key}' not found. Failed at '{k}'."
        else:
            return f"Key '{key}' not found. Failed at '{k}'."

    # Format the result
    if isinstance(current, (dict, list)):
        return f"Value at '{key}':\n{json.dumps(current, indent=2, ensure_ascii=False)}"
    else:
        return f"Value at '{key}': {current}"


# --- Tool: Compare two JSON objects ---
@server.tool()
def compare_json(json1: str, json2: str) -> str:
    """Compare two JSON strings and show the differences."""
    try:
        data1 = json.loads(json1)
    except json.JSONDecodeError as e:
        return f"Error in first JSON: {str(e)}"

    try:
        data2 = json.loads(json2)
    except json.JSONDecodeError as e:
        return f"Error in second JSON: {str(e)}"

    # Check if they are equal
    if data1 == data2:
        return "The two JSON objects are identical."

    # Find differences (works for dict comparisons)
    differences = []

    if isinstance(data1, dict) and isinstance(data2, dict):
        # Keys only in first
        only_in_1 = set(data1.keys()) - set(data2.keys())
        if only_in_1:
            differences.append(f"Keys only in JSON 1: {', '.join(only_in_1)}")

        # Keys only in second
        only_in_2 = set(data2.keys()) - set(data1.keys())
        if only_in_2:
            differences.append(f"Keys only in JSON 2: {', '.join(only_in_2)}")

        # Keys with different values
        common_keys = set(data1.keys()) & set(data2.keys())
        for key in sorted(common_keys):
            if data1[key] != data2[key]:
                differences.append(
                    f"Different value for '{key}': {json.dumps(data1[key])} vs {json.dumps(data2[key])}"
                )
    else:
        differences.append(f"JSON 1 type: {type(data1).__name__}, JSON 2 type: {type(data2).__name__}")
        differences.append(f"JSON 1: {json.dumps(data1)}")
        differences.append(f"JSON 2: {json.dumps(data2)}")

    return "Differences found:\n" + "\n".join(f"  - {d}" for d in differences)


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
