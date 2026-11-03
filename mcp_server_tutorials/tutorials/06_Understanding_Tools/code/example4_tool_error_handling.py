"""
Example 4: Tool Error Handling
===============================

This example shows how to handle errors gracefully inside tools.
Instead of letting exceptions crash the server, we catch them
and return helpful error messages to the LLM.

Key concepts:
- try/except blocks inside tools
- Catching specific exception types (FileNotFoundError, ValueError, etc.)
- Returning descriptive error messages so the LLM can recover
"""

import json
from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("ErrorHandlingDemo")


# ---- Tool 1: File reader with error handling ----
# This tool tries to read a file and handles the case where
# the file does not exist.
@server.tool()
def file_reader(file_path: str) -> str:
    """
    Read the contents of a text file.
    Returns the file contents or an error message if the file is not found.
    """
    try:
        # Attempt to open and read the file
        with open(file_path, "r", encoding="utf-8") as f:
            contents = f.read()
        return f"File contents ({len(contents)} characters):\n{contents}"

    except FileNotFoundError:
        # The file does not exist
        return f"Error: File not found at '{file_path}'. Please check the path."

    except PermissionError:
        # We don't have permission to read the file
        return f"Error: Permission denied when trying to read '{file_path}'."

    except Exception as e:
        # Catch any other unexpected error
        return f"Error: Could not read file. Reason: {str(e)}"


# ---- Tool 2: JSON parser with error handling ----
# This tool tries to parse a JSON string and handles invalid JSON.
@server.tool()
def json_parser(json_string: str) -> str:
    """
    Parse a JSON string and return its contents in a readable format.
    Returns an error message if the JSON is invalid.
    """
    try:
        # Attempt to parse the JSON string
        data = json.loads(json_string)

        # Format it nicely with indentation
        formatted = json.dumps(data, indent=2)
        return f"Parsed JSON successfully:\n{formatted}"

    except json.JSONDecodeError as e:
        # The string is not valid JSON
        return (
            f"Error: Invalid JSON string. "
            f"Problem at line {e.lineno}, column {e.colno}: {e.msg}"
        )

    except Exception as e:
        # Catch any other unexpected error
        return f"Error: Could not parse JSON. Reason: {str(e)}"


# ---- Tool 3: Number converter with error handling ----
# This tool converts a string to different number formats and
# handles the case where the string is not a valid number.
@server.tool()
def number_converter(value: str) -> str:
    """
    Convert a string to integer, float, binary, and hex representations.
    Returns an error if the value is not a valid number.
    """
    try:
        # Try to convert to integer first
        int_value = int(value)

        # Build a report of all conversions
        lines = [
            f"Integer:     {int_value}",
            f"Float:       {float(int_value)}",
            f"Binary:      {bin(int_value)}",
            f"Hexadecimal: {hex(int_value)}",
            f"Octal:       {oct(int_value)}",
        ]
        return "\n".join(lines)

    except ValueError:
        # Maybe it's a float string like "3.14"
        try:
            float_value = float(value)
            return (
                f"Float value: {float_value}\n"
                f"Rounded integer: {round(float_value)}\n"
                f"Note: Binary/hex conversion requires a whole number."
            )
        except ValueError:
            # Not a number at all
            return (
                f"Error: '{value}' is not a valid number. "
                f"Please provide an integer (e.g., 42) or a float (e.g., 3.14)."
            )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
