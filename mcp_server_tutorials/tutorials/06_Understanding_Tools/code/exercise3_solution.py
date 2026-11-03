"""
Exercise 3: Data Tools Server (Solution)
==========================================

This is the complete solution for the data tools exercise.
All tools accept numbers as comma-separated strings and return strings.
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
server = FastMCP("DataToolsSolution")


# -- Helper function to parse comma-separated numbers --
# This is NOT a tool -- just a regular Python function used by the tools.
def parse_numbers(numbers: str) -> list:
    """Parse a comma-separated string into a list of floats."""
    parts = numbers.split(",")
    return [float(part.strip()) for part in parts]


# ---- Tool 1: Sort numbers ----
@server.tool()
def sort_numbers(numbers: str) -> str:
    """Sort a comma-separated list of numbers in ascending order."""
    try:
        nums = parse_numbers(numbers)
        sorted_nums = sorted(nums)
        result = ", ".join(str(n) for n in sorted_nums)
        return f"Sorted: {result}"
    except ValueError:
        return "Error: Could not parse numbers. Use comma-separated values like '5,3,8,1'."


# ---- Tool 2: Filter numbers above a threshold ----
@server.tool()
def filter_above(numbers: str, threshold: float) -> str:
    """Keep only numbers above the given threshold."""
    try:
        nums = parse_numbers(numbers)
        # Keep numbers strictly greater than the threshold
        filtered = [n for n in nums if n > threshold]
        if not filtered:
            return f"No numbers are above {threshold}."
        result = ", ".join(str(n) for n in filtered)
        return f"Numbers above {threshold}: {result} ({len(filtered)} found)"
    except ValueError:
        return "Error: Could not parse numbers. Use comma-separated values like '5,3,8,1'."


# ---- Tool 3: Calculate the average ----
@server.tool()
def average(numbers: str) -> str:
    """Calculate the average (mean) of a comma-separated list of numbers."""
    try:
        nums = parse_numbers(numbers)
        if not nums:
            return "Error: No numbers provided."
        avg = sum(nums) / len(nums)
        return f"Average of {len(nums)} numbers: {avg}"
    except ValueError:
        return "Error: Could not parse numbers. Use comma-separated values like '5,3,8,1'."


# ---- Tool 4: Find min and max ----
@server.tool()
def min_max(numbers: str) -> str:
    """Find the minimum and maximum of a comma-separated list of numbers."""
    try:
        nums = parse_numbers(numbers)
        if not nums:
            return "Error: No numbers provided."
        minimum = min(nums)
        maximum = max(nums)
        return f"Minimum: {minimum}, Maximum: {maximum}"
    except ValueError:
        return "Error: Could not parse numbers. Use comma-separated values like '5,3,8,1'."


# ---- Tool 5: Remove duplicates ----
@server.tool()
def remove_duplicates(numbers: str) -> str:
    """Remove duplicate values from a comma-separated list of numbers."""
    try:
        nums = parse_numbers(numbers)
        # Use dict.fromkeys to preserve order while removing duplicates
        unique = list(dict.fromkeys(nums))
        removed_count = len(nums) - len(unique)
        result = ", ".join(str(n) for n in unique)
        return f"Unique values: {result} ({removed_count} duplicate(s) removed)"
    except ValueError:
        return "Error: Could not parse numbers. Use comma-separated values like '5,3,8,1'."


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
