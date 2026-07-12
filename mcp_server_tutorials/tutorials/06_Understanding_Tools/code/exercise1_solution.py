"""
Exercise 1: Math Tools Server (Solution)
==========================================

This is the complete solution for the math tools exercise.
It implements 8 math tools with proper input validation.
"""

import math
from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("MathToolsSolution")


# ---- Tool 1: Add two numbers ----
@server.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together."""
    result = a + b
    return f"{a} + {b} = {result}"


# ---- Tool 2: Subtract b from a ----
@server.tool()
def subtract(a: float, b: float) -> str:
    """Subtract b from a."""
    result = a - b
    return f"{a} - {b} = {result}"


# ---- Tool 3: Multiply two numbers ----
@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together."""
    result = a * b
    return f"{a} * {b} = {result}"


# ---- Tool 4: Divide a by b ----
@server.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b. Returns an error if b is zero."""
    # Validate: cannot divide by zero
    if b == 0:
        return "Error: Cannot divide by zero."

    result = a / b
    return f"{a} / {b} = {result}"


# ---- Tool 5: Raise base to power of exp ----
@server.tool()
def power(base: float, exp: float) -> str:
    """Raise base to the power of exp."""
    result = base ** exp
    return f"{base} ^ {exp} = {result}"


# ---- Tool 6: Square root ----
@server.tool()
def sqrt(n: float) -> str:
    """Calculate the square root of n. Returns an error for negative numbers."""
    # Validate: cannot take square root of a negative number
    if n < 0:
        return f"Error: Cannot calculate square root of negative number {n}."

    result = math.sqrt(n)
    return f"sqrt({n}) = {result}"


# ---- Tool 7: Absolute value ----
@server.tool()
def absolute(n: float) -> str:
    """Return the absolute value of n."""
    result = abs(n)
    return f"|{n}| = {result}"


# ---- Tool 8: Factorial ----
@server.tool()
def factorial(n: int) -> str:
    """Calculate n! (factorial). Returns an error for negative numbers."""
    # Validate: factorial is not defined for negative numbers
    if n < 0:
        return f"Error: Factorial is not defined for negative number {n}."

    result = math.factorial(n)
    return f"{n}! = {result}"


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
