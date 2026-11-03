"""
Exercise 1 Solution: Calculator Server
=========================================
A calculator MCP server with add, subtract, multiply, and divide.
"""

# ============================================================
# STEP 1: Import FastMCP
# ============================================================
from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 2: Create the server
# ============================================================
# We name it "CalculatorServer" so clients know what it does
server = FastMCP("CalculatorServer")

# ============================================================
# STEP 3: The "add" tool
# ============================================================
@server.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together and return the result."""
    result = a + b
    return str(result)

# ============================================================
# STEP 4: The "subtract" tool
# ============================================================
@server.tool()
def subtract(a: float, b: float) -> str:
    """Subtract b from a and return the result."""
    result = a - b
    return str(result)

# ============================================================
# STEP 5: The "multiply" tool
# ============================================================
@server.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together and return the result."""
    result = a * b
    return str(result)

# ============================================================
# STEP 6: The "divide" tool with validation
# ============================================================
@server.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b. Returns an error message if b is zero."""

    # Always check for division by zero FIRST
    # This prevents a crash and gives a clear error message
    if b == 0:
        return "Error: Cannot divide by zero."

    result = a / b

    # Round to avoid floating point issues
    result = round(result, 10)

    return str(result)

# ============================================================
# STEP 7: Run the server
# ============================================================
if __name__ == "__main__":
    server.run()
