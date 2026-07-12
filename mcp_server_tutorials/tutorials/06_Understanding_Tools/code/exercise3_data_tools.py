"""
Exercise 3: Data Tools Server (Stub)
======================================

YOUR TASK:
Build an MCP server with 5 data processing tools.
All inputs and outputs are strings (numbers passed as comma-separated strings).

  1. sort_numbers(numbers)           - Sort numbers ascending
  2. filter_above(numbers, threshold) - Keep only numbers above threshold
  3. average(numbers)                - Calculate the average
  4. min_max(numbers)                - Find the minimum and maximum
  5. remove_duplicates(numbers)      - Remove duplicate values

REQUIREMENTS:
- 'numbers' is a comma-separated string like "5,3,8,1,3"
- Parse the string into a list of floats
- Return results as descriptive strings
- Handle invalid input gracefully

HINTS:
- Use numbers.split(",") to break the string apart
- Use float() to convert each piece to a number
- sorted() returns a sorted list
- sum(list) / len(list) gives the average
- set() removes duplicates (but loses order)
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("DataToolsExercise")


# TODO: Implement the 5 data tools below


# Tool 1: sort_numbers
# @server.tool()
# def sort_numbers(...) -> str:
#     ...


# Tool 2: filter_above
# @server.tool()
# def filter_above(...) -> str:
#     ...


# Tool 3: average
# @server.tool()
# def average(...) -> str:
#     ...


# Tool 4: min_max
# @server.tool()
# def min_max(...) -> str:
#     ...


# Tool 5: remove_duplicates
# @server.tool()
# def remove_duplicates(...) -> str:
#     ...


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
