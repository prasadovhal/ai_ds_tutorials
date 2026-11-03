"""
Example 1: Tool with Different Argument Types
==============================================

This example shows how to create MCP tools that accept different
Python types as arguments: str, int, float.

The MCP framework automatically handles type conversion and
generates the correct JSON schema for each parameter type.

Key concepts:
- String arguments for text processing
- Integer arguments for whole number math
- Float arguments for decimal math
- Return values are always strings sent back to the LLM
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("ToolTypesDemo")

# ---- Tool 1: String argument ----
# This tool takes a single string argument and returns a greeting.
@server.tool()
def greet(name: str) -> str:
    """Greet someone by name. Pass a person's name to get a friendly greeting."""
    return f"Hello, {name}! Welcome to the MCP tools tutorial."


# ---- Tool 2: Integer arguments ----
# This tool takes two integer arguments and returns their sum.
@server.tool()
def add(a: int, b: int) -> str:
    """Add two whole numbers together. Returns the sum of a and b."""
    result = a + b
    return f"{a} + {b} = {result}"


# ---- Tool 3: Integer argument with boolean-style result ----
# This tool takes an integer and returns whether it is even or odd.
# Note: We return a string because MCP tools communicate via text.
@server.tool()
def is_even(n: int) -> str:
    """Check if a number is even or odd. Returns 'True' or 'False' as text."""
    # Compute the boolean result
    even = (n % 2 == 0)
    # Return it as a descriptive string
    return f"{n} is even: {even}"


# ---- Tool 4: Float arguments ----
# This tool takes two float arguments and returns their product.
# Floats allow decimal numbers like 3.14, 2.5, etc.
@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two decimal numbers. Returns the product of a and b."""
    result = a * b
    return f"{a} * {b} = {result}"


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
