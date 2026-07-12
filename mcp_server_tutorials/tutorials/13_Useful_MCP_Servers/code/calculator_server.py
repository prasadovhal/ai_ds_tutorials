"""
Calculator MCP Server
=====================
A simple calculator server with basic math operations.
Uses the math module for advanced operations like sqrt.
"""

# Import FastMCP to create our server
from mcp.server.fastmcp import FastMCP
import math

# Create the MCP server instance
server = FastMCP("Calculator Server")


# --- Tool: Add two numbers ---
@server.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together."""
    result = a + b
    return f"{a} + {b} = {result}"


# --- Tool: Subtract two numbers ---
@server.tool()
def subtract(a: float, b: float) -> str:
    """Subtract b from a."""
    result = a - b
    return f"{a} - {b} = {result}"


# --- Tool: Multiply two numbers ---
@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together."""
    result = a * b
    return f"{a} * {b} = {result}"


# --- Tool: Divide two numbers ---
@server.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b. Returns error if b is zero."""
    # Check for division by zero
    if b == 0:
        return "Error: Cannot divide by zero!"
    result = a / b
    return f"{a} / {b} = {result}"


# --- Tool: Raise a to the power of b ---
@server.tool()
def power(base: float, exponent: float) -> str:
    """Raise base to the power of exponent."""
    result = math.pow(base, exponent)
    return f"{base} ^ {exponent} = {result}"


# --- Tool: Square root ---
@server.tool()
def sqrt(number: float) -> str:
    """Calculate the square root of a number."""
    # Check for negative numbers
    if number < 0:
        return "Error: Cannot take square root of a negative number!"
    result = math.sqrt(number)
    return f"sqrt({number}) = {result}"


# --- Tool: Calculate percentage ---
@server.tool()
def percentage(value: float, percent: float) -> str:
    """Calculate what percent of a value is. E.g., percentage(200, 15) = 30."""
    result = (value * percent) / 100
    return f"{percent}% of {value} = {result}"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
