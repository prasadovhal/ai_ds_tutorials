"""
exercise2_solution.py - Solution: Server with Comprehensive Input Validation

This is the solution for exercise2_validated_server.py.
A contacts manager MCP server with thorough input validation.
"""

import json
import re

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Validation helper functions
# ============================================================

def check_injection(text, field_name):
    """
    Check a string for SQL and command injection patterns.

    Args:
        text: The string to check
        field_name: Name of the field (for error messages)

    Returns:
        Tuple of (is_safe, error_message)
    """
    if not isinstance(text, str):
        return False, f"{field_name} must be a string"

    lower_text = text.lower()

    # SQL injection patterns
    sql_dangers = [
        "drop table", "drop database", "delete from",
        "insert into", "union select", "'; --",
        "' or '1'='1", "1=1",
    ]
    for pattern in sql_dangers:
        if pattern in lower_text:
            return False, f"{field_name} contains suspicious SQL pattern: '{pattern}'"

    # Command injection patterns
    cmd_dangers = ["&&", "||", "; rm", "; cat", "$()", "`", "| ", "> /"]
    for pattern in cmd_dangers:
        if pattern in lower_text:
            return False, f"{field_name} contains suspicious command pattern: '{pattern}'"

    # Path traversal
    if ".." in text or "~/" in text:
        return False, f"{field_name} contains path traversal pattern"

    return True, None


def validate_name(name):
    """
    Validate a contact name.
    Must be 2-100 characters, no injection.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(name, str):
        return False, "name must be a string"

    stripped = name.strip()
    if len(stripped) < 2:
        return False, "name must be at least 2 characters"
    if len(stripped) > 100:
        return False, "name must be at most 100 characters"

    # Check for injection
    is_safe, error = check_injection(name, "name")
    if not is_safe:
        return False, error

    return True, None


def validate_email(email):
    """
    Validate an email address format.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(email, str):
        return False, "email must be a string"

    if len(email) > 254:
        return False, "email is too long (max 254 characters)"

    # Simple but effective email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, f"'{email}' is not a valid email address"

    return True, None


def validate_phone(phone):
    """
    Validate a phone number.
    Allows digits, spaces, hyphens, parentheses, and plus sign.
    Must be 7-20 characters.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(phone, str):
        return False, "phone must be a string"

    # Check length
    if len(phone) < 7:
        return False, "phone must be at least 7 characters"
    if len(phone) > 20:
        return False, "phone must be at most 20 characters"

    # Check characters: only digits, spaces, hyphens, parens, and plus
    allowed_pattern = r'^[0-9\s\-\(\)\+]+$'
    if not re.match(allowed_pattern, phone):
        return False, "phone can only contain digits, spaces, hyphens, parentheses, and +"

    # Must contain at least 7 digits
    digits_only = re.sub(r'[^0-9]', '', phone)
    if len(digits_only) < 7:
        return False, "phone must contain at least 7 digits"

    return True, None


def validate_age(age):
    """
    Validate an age value.
    Must be an integer between 1 and 150.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(age, int):
        return False, f"age must be an integer, got {type(age).__name__}"

    if age < 1:
        return False, "age must be at least 1"
    if age > 150:
        return False, "age must be at most 150"

    return True, None


def validate_query(query):
    """
    Validate a search query.
    Must be 1-500 characters, no injection.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(query, str):
        return False, "query must be a string"

    stripped = query.strip()
    if len(stripped) < 1:
        return False, "query cannot be empty"
    if len(stripped) > 500:
        return False, "query must be at most 500 characters"

    is_safe, error = check_injection(query, "query")
    if not is_safe:
        return False, error

    return True, None


# ============================================================
# Step 2: Create the MCP server and storage
# ============================================================

server = FastMCP("validated-contacts-server")

# In-memory contacts storage
contacts = []
next_contact_id = 1

# ============================================================
# Step 3: Tool - add_contact
# ============================================================

def add_contact(name: str, email: str, phone: str, age: int) -> str:
    """
    Add a new contact with comprehensive validation.

    Args:
        name: Contact name (2-100 chars)
        email: Valid email address
        phone: Phone number (digits, spaces, hyphens)
        age: Age (1-150)

    Returns:
        JSON with result or ALL validation errors
    """
    global next_contact_id

    # Collect ALL errors, do not stop at the first one
    errors = []

    # Validate name
    is_valid, error = validate_name(name)
    if not is_valid:
        errors.append(error)

    # Validate email
    is_valid, error = validate_email(email)
    if not is_valid:
        errors.append(error)

    # Validate phone
    is_valid, error = validate_phone(phone)
    if not is_valid:
        errors.append(error)

    # Validate age
    is_valid, error = validate_age(age)
    if not is_valid:
        errors.append(error)

    # If there are ANY errors, return them all
    if len(errors) > 0:
        return json.dumps({
            "error": "validation_failed",
            "error_count": len(errors),
            "errors": errors,
        }, indent=2)

    # All validation passed - create the contact
    contact = {
        "id": next_contact_id,
        "name": name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "age": age,
    }
    contacts.append(contact)
    next_contact_id = next_contact_id + 1

    return json.dumps({
        "status": "created",
        "contact": contact,
    }, indent=2)


# Register the tool
server.tool()(add_contact)

# ============================================================
# Step 4: Tool - search_contacts
# ============================================================

def search_contacts(query: str) -> str:
    """
    Search contacts by name or email.

    Args:
        query: Search term (1-500 chars, no injection)

    Returns:
        JSON with matching contacts or error
    """
    # Validate query
    is_valid, error = validate_query(query)
    if not is_valid:
        return json.dumps({"error": error})

    # Search through contacts
    query_lower = query.lower().strip()
    matches = []

    for contact in contacts:
        name_match = query_lower in contact["name"].lower()
        email_match = query_lower in contact["email"].lower()
        if name_match or email_match:
            matches.append(contact)

    return json.dumps({
        "query": query,
        "matches": matches,
        "total_found": len(matches),
    }, indent=2)


# Register the tool
server.tool()(search_contacts)

# ============================================================
# Step 5: Tool - get_contact
# ============================================================

def get_contact(contact_id: int) -> str:
    """
    Get a contact by ID.

    Args:
        contact_id: Positive integer ID

    Returns:
        JSON with contact or error
    """
    # Validate contact_id
    if not isinstance(contact_id, int):
        return json.dumps({"error": "contact_id must be an integer"})

    if contact_id < 1:
        return json.dumps({"error": "contact_id must be a positive integer"})

    # Find the contact
    for contact in contacts:
        if contact["id"] == contact_id:
            return json.dumps({"contact": contact}, indent=2)

    return json.dumps({"error": f"Contact with ID {contact_id} not found"})


# Register the tool
server.tool()(get_contact)

# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 2 Solution: Validated Contacts Server")
    print("=" * 60)
    print()

    # Test 1: Valid contact
    print("--- Test 1: Valid contact ---")
    print(add_contact("Alice Smith", "alice@example.com", "555-123-4567", 30))
    print()

    # Test 2: Invalid email
    print("--- Test 2: Invalid email ---")
    print(add_contact("Bob", "not-an-email", "555-1234567", 25))
    print()

    # Test 3: SQL injection in name
    print("--- Test 3: SQL injection ---")
    print(add_contact("'; DROP TABLE contacts; --", "x@x.com", "555-1234567", 25))
    print()

    # Test 4: Multiple errors at once
    print("--- Test 4: Multiple errors ---")
    print(add_contact("A", "bad-email", "abc", -5))
    print()

    # Test 5: Valid search
    print("--- Test 5: Valid search ---")
    print(search_contacts("alice"))
    print()

    # Test 6: Injection in search
    print("--- Test 6: Injection in search ---")
    print(search_contacts("'; DROP TABLE contacts; --"))
    print()

    # Test 7: Get contact by ID
    print("--- Test 7: Get contact ---")
    print(get_contact(1))
    print()

    # Test 8: Invalid ID
    print("--- Test 8: Invalid ID ---")
    print(get_contact(-1))

    # To run as MCP server (uncomment):
    # server.run()
