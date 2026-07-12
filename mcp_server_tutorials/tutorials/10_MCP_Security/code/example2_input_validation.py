"""
example2_input_validation.py - MCP Server with Thorough Input Validation

PURPOSE:
    This example shows how to validate ALL inputs to your MCP tools.
    Never trust input from the client. Always validate before processing.

WHAT YOU WILL LEARN:
    1. How to validate string inputs (length, content, format)
    2. How to validate numeric inputs (range, type)
    3. How to prevent path traversal attacks
    4. How to prevent injection attacks (SQL, command)
    5. How to return clear error messages

SETUP:
    1. poetry add mcp
    2. Run: python example2_input_validation.py

WHY INPUT VALIDATION MATTERS:
    MCP tools receive input from AI models, which get input from users.
    A malicious user could craft input that:
    - Reads sensitive files (path traversal)
    - Executes database commands (SQL injection)
    - Runs system commands (command injection)
    - Crashes the server (oversized input)
"""

import os
import re
import json

# Import MCP SDK
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Define validation helper functions
# ============================================================
# These functions check different types of input.
# Each returns a tuple: (is_valid, error_message)
# If valid, error_message is None.


def validate_string(value, field_name, min_length=1, max_length=1000):
    """
    Validate a string input.

    Checks:
    - Is it actually a string?
    - Is it within length limits?
    - Is it not empty (after stripping whitespace)?

    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check type
    if not isinstance(value, str):
        return False, f"{field_name} must be a string, got {type(value).__name__}"

    # Strip whitespace and check minimum length
    stripped = value.strip()
    if len(stripped) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"

    # Check maximum length
    if len(value) > max_length:
        return False, f"{field_name} must be at most {max_length} characters"

    return True, None


def validate_integer(value, field_name, min_value=None, max_value=None):
    """
    Validate an integer input.

    Checks:
    - Is it actually an integer?
    - Is it within the allowed range?

    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check type
    if not isinstance(value, int):
        return False, f"{field_name} must be an integer, got {type(value).__name__}"

    # Check minimum
    if min_value is not None and value < min_value:
        return False, f"{field_name} must be at least {min_value}, got {value}"

    # Check maximum
    if max_value is not None and value > max_value:
        return False, f"{field_name} must be at most {max_value}, got {value}"

    return True, None


def validate_file_path(path, field_name, base_directory="/app/data"):
    """
    Validate a file path to prevent path traversal attacks.

    Path traversal is when an attacker uses ".." to escape
    the allowed directory and access sensitive files.

    Example attack: "../../etc/passwd"

    Checks:
    - Is the path a valid string?
    - Does it contain path traversal sequences?
    - Does the resolved path stay within the base directory?

    Args:
        path: The file path to validate
        field_name: Name of the field (for error messages)
        base_directory: The directory that paths must stay within

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First, validate as a string
    is_valid, error = validate_string(path, field_name, max_length=500)
    if not is_valid:
        return False, error

    # Check for obvious path traversal patterns
    # These patterns try to escape the allowed directory
    dangerous_patterns = [
        "..",          # Parent directory traversal
        "~",           # Home directory reference
        "$",           # Environment variable expansion
        "|",           # Pipe command
        ";",           # Command separator
        "&",           # Background command
        "`",           # Command substitution
        "\x00",        # Null byte (can truncate paths)
    ]

    for pattern in dangerous_patterns:
        if pattern in path:
            return False, f"{field_name} contains forbidden character: '{pattern}'"

    # Resolve the full path and check it stays in the base directory
    # os.path.realpath resolves all symlinks and ".." components
    full_path = os.path.realpath(os.path.join(base_directory, path))
    real_base = os.path.realpath(base_directory)

    if not full_path.startswith(real_base):
        return False, f"{field_name} must be within {base_directory} (path traversal detected)"

    return True, None


def validate_no_injection(value, field_name):
    """
    Check for common injection patterns in a string.

    This catches:
    - SQL injection attempts
    - Command injection attempts
    - Script injection attempts

    Args:
        value: The string to check
        field_name: Name of the field (for error messages)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"

    # Convert to lowercase for pattern matching
    lower_value = value.lower()

    # SQL injection patterns
    sql_patterns = [
        "drop table",
        "drop database",
        "delete from",
        "insert into",
        "update set",
        "union select",
        "'; --",
        "' or '1'='1",
        "' or 1=1",
        "1=1",
        "' or ''='",
    ]

    for pattern in sql_patterns:
        if pattern in lower_value:
            return False, f"{field_name} contains potential SQL injection: '{pattern}'"

    # Command injection patterns
    command_patterns = [
        "&&",          # Chain commands
        "||",          # Chain commands
        "; rm ",       # Delete files
        "; cat ",      # Read files
        "$()",         # Command substitution
        "`",           # Command substitution
        "| ",          # Pipe to another command
        "> /",         # Redirect output
        "< /",         # Redirect input
    ]

    for pattern in command_patterns:
        if pattern in lower_value:
            return False, f"{field_name} contains potential command injection: '{pattern}'"

    return True, None


def validate_email(value, field_name):
    """
    Validate an email address format.

    Uses a simple regex pattern. For production, consider
    using a dedicated email validation library.

    Args:
        value: The email address to validate
        field_name: Name of the field (for error messages)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First validate as a string
    is_valid, error = validate_string(value, field_name, max_length=254)
    if not is_valid:
        return False, error

    # Simple email pattern
    # This catches most invalid emails but is not exhaustive
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        return False, f"{field_name} is not a valid email address"

    return True, None


# ============================================================
# Step 2: Create the MCP server
# ============================================================

server = FastMCP("validated-server")


# ============================================================
# Step 3: Define tools with input validation
# ============================================================

# Tool 1: Search with validated query

def search_documents(query: str, max_results: int = 10) -> str:
    """
    Search for documents with validated inputs.

    Args:
        query: Search query (1-500 characters, no injection)
        max_results: Number of results (1-100)

    Returns:
        JSON string with search results or error
    """
    # Validate the query string
    is_valid, error = validate_string(query, "query", min_length=1, max_length=500)
    if not is_valid:
        return json.dumps({"error": error})

    # Check for injection attempts
    is_valid, error = validate_no_injection(query, "query")
    if not is_valid:
        return json.dumps({"error": error})

    # Validate max_results
    is_valid, error = validate_integer(max_results, "max_results", min_value=1, max_value=100)
    if not is_valid:
        return json.dumps({"error": error})

    # All validation passed - process the request
    results = []
    for i in range(min(max_results, 3)):
        results.append({
            "title": f"Result {i + 1} for: {query}",
            "score": round(0.95 - (i * 0.1), 2)
        })

    return json.dumps({
        "query": query,
        "results": results,
        "total": len(results)
    }, indent=2)


# Register tool
server.tool()(search_documents)


# Tool 2: Read file with path validation

def read_file(file_path: str) -> str:
    """
    Read a file with path traversal protection.

    The file must be within the allowed data directory.
    Attempts to access files outside this directory will be rejected.

    Args:
        file_path: Path to the file (relative to data directory)

    Returns:
        File content or error message
    """
    # Define the base directory that all file paths must be within
    base_directory = os.path.join(os.path.dirname(__file__), "data")

    # Validate the file path
    is_valid, error = validate_file_path(file_path, "file_path", base_directory)
    if not is_valid:
        return json.dumps({"error": error})

    # Build the full path
    full_path = os.path.realpath(os.path.join(base_directory, file_path))

    # Check if the file exists
    if not os.path.exists(full_path):
        return json.dumps({"error": f"File not found: {file_path}"})

    # Check if it's actually a file (not a directory)
    if not os.path.isfile(full_path):
        return json.dumps({"error": f"Path is not a file: {file_path}"})

    # Read and return the file
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return json.dumps({
            "file": file_path,
            "content": content,
            "size": len(content)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read file: {str(e)}"})


# Register tool
server.tool()(read_file)


# Tool 3: Add user with email validation

def add_user(name: str, email: str, age: int) -> str:
    """
    Add a new user with comprehensive input validation.

    Args:
        name: User's name (2-100 characters, no injection)
        email: User's email address (valid email format)
        age: User's age (1-150)

    Returns:
        JSON string with result or error
    """
    # Validate name
    is_valid, error = validate_string(name, "name", min_length=2, max_length=100)
    if not is_valid:
        return json.dumps({"error": error})

    # Check name for injection
    is_valid, error = validate_no_injection(name, "name")
    if not is_valid:
        return json.dumps({"error": error})

    # Validate email
    is_valid, error = validate_email(email, "email")
    if not is_valid:
        return json.dumps({"error": error})

    # Validate age
    is_valid, error = validate_integer(age, "age", min_value=1, max_value=150)
    if not is_valid:
        return json.dumps({"error": error})

    # All validation passed - process the request
    return json.dumps({
        "status": "success",
        "message": f"User '{name}' added successfully",
        "user": {
            "name": name,
            "email": email,
            "age": age
        }
    }, indent=2)


# Register tool
server.tool()(add_user)


# ============================================================
# Step 4: Demonstrate validation
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server with Input Validation - Demonstration")
    print("=" * 60)
    print()

    # --- Test 1: Valid search ---
    print("--- Test 1: Valid search query ---")
    result = search_documents("machine learning", 5)
    print(result)
    print()

    # --- Test 2: Empty query ---
    print("--- Test 2: Empty search query ---")
    result = search_documents("", 5)
    print(result)
    print()

    # --- Test 3: SQL injection attempt ---
    print("--- Test 3: SQL injection attempt ---")
    result = search_documents("'; DROP TABLE users; --", 5)
    print(result)
    print()

    # --- Test 4: Too many results ---
    print("--- Test 4: max_results out of range ---")
    result = search_documents("valid query", 999)
    print(result)
    print()

    # --- Test 5: Path traversal attempt ---
    print("--- Test 5: Path traversal attack ---")
    result = read_file("../../etc/passwd")
    print(result)
    print()

    # --- Test 6: Valid file read ---
    print("--- Test 6: Valid file path ---")
    result = read_file("notes.txt")
    print(result)
    print()

    # --- Test 7: Valid user ---
    print("--- Test 7: Valid user addition ---")
    result = add_user("Alice Smith", "alice@example.com", 30)
    print(result)
    print()

    # --- Test 8: Invalid email ---
    print("--- Test 8: Invalid email ---")
    result = add_user("Bob", "not-an-email", 25)
    print(result)
    print()

    # --- Test 9: Invalid age ---
    print("--- Test 9: Invalid age ---")
    result = add_user("Charlie", "charlie@example.com", -5)
    print(result)
    print()

    # --- Test 10: Injection in name ---
    print("--- Test 10: Injection in name field ---")
    result = add_user("'; DROP TABLE users; --", "attacker@evil.com", 25)
    print(result)
    print()

    print("=" * 60)
    print("Key Takeaways:")
    print("  1. ALWAYS validate type, length, and format")
    print("  2. ALWAYS check for path traversal in file paths")
    print("  3. ALWAYS check for injection patterns")
    print("  4. Return CLEAR error messages")
    print("  5. Validate BEFORE processing (fail fast)")
    print("=" * 60)

    # To run as MCP server (uncomment):
    # server.run()
