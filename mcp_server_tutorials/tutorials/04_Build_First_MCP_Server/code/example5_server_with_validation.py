"""
Example 5: Server with Input Validation
==========================================
This server validates ALL inputs before processing them.

WHY validate inputs?
--------------------
MCP tools can be called by anyone - a human, an LLM, or
another program. You cannot trust that the inputs are correct.

For example, an LLM might:
    - Pass a negative number where you expect positive
    - Pass an empty string where you expect text
    - Pass a number outside the valid range
    - Pass None or null values

Without validation, your tools might:
    - Crash with an unhelpful error message
    - Produce wrong results silently
    - Have security vulnerabilities

What you will learn:
    - How to validate inputs in tool functions
    - How to return meaningful error messages
    - How to handle edge cases

How to run:
    poetry run mcp dev example5_server_with_validation.py

How to test:
    Open MCP Inspector
    Try calling "divide" with b=0 (should get an error message)
    Try calling "calculate_percentage" with values > 100
"""

# ============================================================
# STEP 1: Imports
# ============================================================
from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 2: Create the server
# ============================================================
server = FastMCP("ValidationServer")

# ============================================================
# STEP 3: Tool with division-by-zero validation
# ============================================================
@server.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b. Returns an error if b is zero."""

    # VALIDATION: Check for division by zero
    # We check this BEFORE doing the division to give
    # a clear, helpful error message instead of a crash.
    if b == 0:
        return "Error: Cannot divide by zero. Please provide a non-zero divisor."

    result = a / b

    # Round to avoid floating point weirdness like 0.30000000000000004
    result = round(result, 10)

    return str(result)

# ============================================================
# STEP 4: Tool with range validation
# ============================================================
@server.tool()
def calculate_percentage(value: float, total: float) -> str:
    """Calculate what percentage 'value' is of 'total'."""

    # VALIDATION: Total must be positive
    # You cannot calculate a percentage of zero or negative
    if total <= 0:
        return "Error: Total must be a positive number."

    # VALIDATION: Value should not be negative
    if value < 0:
        return "Error: Value cannot be negative."

    # VALIDATION: Value should not exceed total
    # (This is a business rule - depends on your use case)
    if value > total:
        return (
            f"Warning: Value ({value}) exceeds total ({total}). "
            f"Percentage will be over 100%."
            f"\nResult: {round(value / total * 100, 2)}%"
        )

    # Normal calculation
    percentage = round(value / total * 100, 2)

    return f"{percentage}%"

# ============================================================
# STEP 5: Tool with string validation
# ============================================================
@server.tool()
def count_words(text: str) -> str:
    """Count the number of words in the given text."""

    # VALIDATION: Check for empty or whitespace-only text
    if not text:
        return "Error: Text cannot be empty."

    if text.strip() == "":
        return "Error: Text contains only whitespace."

    # VALIDATION: Check for reasonable length
    # In production, you might want to limit text size
    # to prevent memory issues
    max_length = 100000  # 100K characters
    if len(text) > max_length:
        return f"Error: Text is too long ({len(text)} characters). Maximum is {max_length}."

    # Count words by splitting on whitespace
    words = text.split()
    word_count = len(words)

    return f"Word count: {word_count}"

# ============================================================
# STEP 6: Tool with multiple validations
# ============================================================
@server.tool()
def create_greeting(name: str, age: int) -> str:
    """Create a personalized greeting message."""

    # VALIDATION 1: Name must not be empty
    if not name or name.strip() == "":
        return "Error: Name cannot be empty."

    # VALIDATION 2: Name should be reasonable length
    if len(name) > 100:
        return "Error: Name is too long. Maximum 100 characters."

    # VALIDATION 3: Age must be positive
    if age < 0:
        return "Error: Age cannot be negative."

    # VALIDATION 4: Age must be realistic
    if age > 150:
        return "Error: Age seems unrealistic. Maximum is 150."

    # Clean the name (remove extra whitespace)
    clean_name = name.strip()

    # Create the greeting based on age
    if age < 13:
        greeting = f"Hey {clean_name}! You are {age} years old. You are a kid!"
    elif age < 20:
        greeting = f"Hi {clean_name}! You are {age} years old. You are a teenager!"
    elif age < 65:
        greeting = f"Hello {clean_name}! You are {age} years old. You are an adult!"
    else:
        greeting = f"Hello {clean_name}! You are {age} years old. You are a senior!"

    return greeting

# ============================================================
# STEP 7: Tool with type-aware validation
# ============================================================
@server.tool()
def safe_power(base: float, exponent: int) -> str:
    """Calculate base raised to the power of exponent, safely."""

    # VALIDATION: Prevent extremely large results
    # 2^1000 is a number with 300+ digits - this could freeze the server
    if abs(exponent) > 100:
        return "Error: Exponent too large. Maximum absolute value is 100."

    # VALIDATION: Prevent 0^0 (mathematically undefined in some contexts)
    if base == 0 and exponent == 0:
        return "Warning: 0^0 is conventionally defined as 1, but is mathematically debated. Result: 1"

    # VALIDATION: Prevent 0 to negative power (division by zero)
    if base == 0 and exponent < 0:
        return "Error: Cannot raise 0 to a negative power (would be division by zero)."

    # Safe to calculate
    result = base ** exponent

    # Format large results nicely
    if abs(result) > 1e15:
        return f"{result:.6e}"  # Scientific notation for large numbers
    else:
        return str(round(result, 10))

# ============================================================
# STEP 8: Run the server
# ============================================================
if __name__ == "__main__":
    server.run()
