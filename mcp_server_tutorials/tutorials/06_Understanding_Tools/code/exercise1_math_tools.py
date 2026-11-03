"""
Exercise 1: Math Tools Server (Stub)
=====================================

YOUR TASK:
Build an MCP server with 8 math tools:
  1. add(a, b)        - Add two numbers
  2. subtract(a, b)   - Subtract b from a
  3. multiply(a, b)   - Multiply two numbers
  4. divide(a, b)     - Divide a by b (handle division by zero!)
  5. power(base, exp) - Raise base to the power of exp
  6. sqrt(n)          - Square root of n (handle negative numbers!)
  7. absolute(n)      - Absolute value of n
  8. factorial(n)     - Factorial of n (handle negative numbers!)

REQUIREMENTS:
- Use float for add, subtract, multiply, divide, power, sqrt
- Use int for factorial
- Return results as descriptive strings
- Validate inputs where needed (division by zero, negative sqrt, etc.)

HINTS:
- import math for sqrt and factorial
- math.sqrt() raises ValueError for negative numbers
- math.factorial() raises ValueError for negative numbers
"""

import math
from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("MathToolsExercise")


# TODO: Implement the 8 math tools below
# Each tool should use the @server.tool() decorator


# Tool 1: add
# @server.tool()
# def add(...) -> str:
#     ...


# Tool 2: subtract
# @server.tool()
# def subtract(...) -> str:
#     ...


# Tool 3: multiply
# @server.tool()
# def multiply(...) -> str:
#     ...


# Tool 4: divide (remember to check for b == 0)
# @server.tool()
# def divide(...) -> str:
#     ...


# Tool 5: power
# @server.tool()
# def power(...) -> str:
#     ...


# Tool 6: sqrt (remember to check for negative numbers)
# @server.tool()
# def sqrt(...) -> str:
#     ...


# Tool 7: absolute
# @server.tool()
# def absolute(...) -> str:
#     ...


# Tool 8: factorial (remember to check for negative numbers)
# @server.tool()
# def factorial(...) -> str:
#     ...


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
