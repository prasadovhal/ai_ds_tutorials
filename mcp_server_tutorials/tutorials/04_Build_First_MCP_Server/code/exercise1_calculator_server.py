"""
Exercise 1: Calculator Server
================================
YOUR TASK: Build a calculator MCP server with 4 tools:
    1. add(a, b) - Add two numbers
    2. subtract(a, b) - Subtract b from a
    3. multiply(a, b) - Multiply two numbers
    4. divide(a, b) - Divide a by b (handle division by zero!)

Requirements:
    - All tools take two float parameters
    - All tools return a string with the result
    - The divide tool MUST handle division by zero gracefully
    - Each tool MUST have a clear docstring description

Test your server:
    poetry run mcp dev exercise1_calculator_server.py

Then test each tool in the MCP Inspector:
    - add(10, 5) should return "15.0"
    - subtract(10, 5) should return "5.0"
    - multiply(10, 5) should return "50.0"
    - divide(10, 5) should return "2.0"
    - divide(10, 0) should return an error message

HINTS:
    - Import FastMCP from mcp.server.fastmcp
    - Create a server with FastMCP("CalculatorServer")
    - Use @server.tool() to register each tool
    - Use type hints: def add(a: float, b: float) -> str
    - Remember to call server.run() at the end
"""

# YOUR CODE HERE
# ==============
#
# Step 1: Import FastMCP
#
# Step 2: Create the server
#
# Step 3: Register the "add" tool
#
# Step 4: Register the "subtract" tool
#
# Step 5: Register the "multiply" tool
#
# Step 6: Register the "divide" tool (with validation!)
#
# Step 7: Run the server
#
# Good luck!
