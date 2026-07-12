"""
exercise2_validated_server.py - Exercise: Server with Comprehensive Input Validation

EXERCISE:
    Build an MCP server for a simple contacts manager.
    Every input must be thoroughly validated.

    The server should have these tools:
    1. add_contact(name, email, phone, age) - with validation for ALL fields
    2. search_contacts(query) - with injection protection
    3. get_contact(contact_id) - with numeric validation

    Validation rules:
    - name: 2-100 chars, no injection patterns
    - email: valid email format
    - phone: digits, spaces, hyphens, parentheses only, 7-20 chars
    - age: integer between 1 and 150
    - query: 1-500 chars, no injection patterns
    - contact_id: positive integer

REQUIREMENTS:
    - Validate ALL inputs before processing
    - Return clear JSON error messages
    - Check for SQL injection and command injection
    - Prevent path traversal in any string field
    - Use the patterns from example2_input_validation.py

HINTS:
    - Create helper validation functions first
    - Use regex for email and phone validation
    - Check every field separately and collect all errors
    - Return ALL errors at once (not just the first one)

YOUR TASK:
    Fill in the code below where you see "TODO" comments.
"""

import json
import re

from mcp.server.fastmcp import FastMCP

# ============================================================
# TODO Step 1: Create validation helper functions
# ============================================================
# Create these functions:
# - validate_name(name) -> (is_valid, error_message)
# - validate_email(email) -> (is_valid, error_message)
# - validate_phone(phone) -> (is_valid, error_message)
# - validate_age(age) -> (is_valid, error_message)
# - validate_query(query) -> (is_valid, error_message)
# - check_injection(text, field_name) -> (is_safe, error_message)

# YOUR CODE HERE


# ============================================================
# TODO Step 2: Create the MCP server and contact storage
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO Step 3: Create tool - add_contact(name, email, phone, age)
# ============================================================
# Validate ALL four fields. Collect ALL errors and return them.

# YOUR CODE HERE


# ============================================================
# TODO Step 4: Create tool - search_contacts(query)
# ============================================================
# Validate the query, check for injection, then search.

# YOUR CODE HERE


# ============================================================
# TODO Step 5: Create tool - get_contact(contact_id)
# ============================================================
# Validate that contact_id is a positive integer.

# YOUR CODE HERE


# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 2: Validated Contacts Server")
    print("=" * 60)
    print()
    print("TODO: Implement the server following the instructions above.")
    print("Look at example2_input_validation.py for guidance.")
    print()
    print("Test cases to verify:")
    print("  1. Valid contact: name='Alice', email='alice@test.com', phone='555-1234', age=30")
    print("  2. Invalid email: email='not-an-email'")
    print("  3. SQL injection in name: name=\"'; DROP TABLE contacts; --\"")
    print("  4. Invalid age: age=-5 or age=200")
    print("  5. Invalid phone: phone='abc123'")

    # To run as MCP server (uncomment when done):
    # server.run()
