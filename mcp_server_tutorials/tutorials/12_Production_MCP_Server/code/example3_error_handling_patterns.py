"""
Example 3: Error Handling Patterns for MCP Server
===================================================
This example shows how to create custom error classes and
handle errors gracefully in MCP tools.

Good error handling means:
- Users get clear, helpful error messages
- Errors are logged for debugging
- The server does NOT crash on bad input
- Different error types get different treatment

We define three custom error classes:
1. ToolError     -- general tool failure
2. ValidationError -- bad input from the user
3. NotFoundError   -- requested item does not exist

Poetry setup:
    poetry init --name example3-error-handling --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Set up logging
# ============================================================

logger = logging.getLogger("mcp_errors")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# ============================================================
# STEP 2: Define custom error classes
# ============================================================

# Python lets you create your own error types by inheriting from Exception.
# Custom errors make it clear WHAT went wrong and WHY.


class ToolError(Exception):
    """
    General tool error.
    Use this when a tool fails for any reason.
    """

    def __init__(self, tool_name, message):
        self.tool_name = tool_name
        self.message = message
        # Call the parent Exception constructor
        super().__init__(f"[{tool_name}] {message}")


class ValidationError(Exception):
    """
    Input validation error.
    Use this when the user provides bad input
    (wrong type, out of range, missing field, etc.)
    """

    def __init__(self, field_name, message):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Validation error on '{field_name}': {message}")


class NotFoundError(Exception):
    """
    Resource not found error.
    Use this when a requested item does not exist.
    """

    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} not found: '{resource_id}'")


# ============================================================
# STEP 3: Create sample data
# ============================================================

# A simple in-memory database of users
user_database = {
    "user001": {"name": "Alice", "email": "alice@example.com", "role": "admin"},
    "user002": {"name": "Bob", "email": "bob@example.com", "role": "user"},
    "user003": {"name": "Charlie", "email": "charlie@example.com", "role": "user"},
}

# ============================================================
# STEP 4: Create the MCP server
# ============================================================

server = FastMCP("error-handling-server")

logger.info("Error handling example server initialized")

# ============================================================
# STEP 5: Define tools that demonstrate each error type
# ============================================================


@server.tool()
def get_user(user_id: str) -> str:
    """
    Look up a user by ID.
    Demonstrates NotFoundError when user does not exist.
    """

    logger.info(f"Tool 'get_user' called with user_id='{user_id}'")

    # Validate input
    if not user_id:
        logger.error("Empty user_id provided")
        return "Error: user_id cannot be empty"

    if len(user_id) < 3:
        logger.error(f"user_id too short: '{user_id}'")
        return "Error: user_id must be at least 3 characters"

    # Look up the user
    try:
        if user_id not in user_database:
            # Raise our custom NotFoundError
            raise NotFoundError("User", user_id)

        user = user_database[user_id]
        result = f"User found:\n"
        result = result + f"  ID:    {user_id}\n"
        result = result + f"  Name:  {user['name']}\n"
        result = result + f"  Email: {user['email']}\n"
        result = result + f"  Role:  {user['role']}"

        logger.info(f"User '{user_id}' found successfully")
        return result

    except NotFoundError as e:
        # Handle the not-found case gracefully
        logger.warning(f"User not found: {e}")
        return f"Error: {e}"

    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error looking up user: {e}")
        return f"Error: An unexpected error occurred"


@server.tool()
def create_user(user_id: str, name: str, email: str) -> str:
    """
    Create a new user.
    Demonstrates ValidationError for bad input.
    """

    logger.info(f"Tool 'create_user' called: id='{user_id}', name='{name}', email='{email}'")

    try:
        # Validate user_id
        if not user_id:
            raise ValidationError("user_id", "cannot be empty")

        if not user_id.startswith("user"):
            raise ValidationError("user_id", "must start with 'user'")

        if len(user_id) < 5:
            raise ValidationError("user_id", "must be at least 5 characters")

        # Validate name
        if not name:
            raise ValidationError("name", "cannot be empty")

        if len(name) < 2:
            raise ValidationError("name", "must be at least 2 characters")

        # Validate email
        if not email:
            raise ValidationError("email", "cannot be empty")

        if "@" not in email:
            raise ValidationError("email", "must contain @")

        if "." not in email.split("@")[-1]:
            raise ValidationError("email", "must have a valid domain")

        # Check if user already exists
        if user_id in user_database:
            raise ToolError("create_user", f"User '{user_id}' already exists")

        # Create the user
        user_database[user_id] = {
            "name": name,
            "email": email,
            "role": "user",
        }

        logger.info(f"User '{user_id}' created successfully")
        return f"User '{user_id}' ({name}) created successfully!"

    except ValidationError as e:
        # Handle validation errors
        logger.warning(f"Validation failed: {e}")
        return f"Validation Error: {e}"

    except ToolError as e:
        # Handle tool errors (like duplicate user)
        logger.warning(f"Tool error: {e}")
        return f"Error: {e}"

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in create_user: {e}")
        return f"Error: An unexpected error occurred"


@server.tool()
def divide_safely(a: float, b: float) -> str:
    """
    Divide two numbers with comprehensive error handling.
    Demonstrates ToolError for operation failures.
    """

    logger.info(f"Tool 'divide_safely' called: a={a}, b={b}")

    try:
        # Validate inputs
        if not isinstance(a, (int, float)):
            raise ValidationError("a", f"must be a number, got {type(a).__name__}")

        if not isinstance(b, (int, float)):
            raise ValidationError("b", f"must be a number, got {type(b).__name__}")

        # Check for division by zero
        if b == 0:
            raise ToolError("divide_safely", "Cannot divide by zero")

        # Perform the division
        result = a / b

        # Check for very large results (potential overflow)
        if abs(result) > 1e15:
            logger.warning(f"Very large result: {result}")

        logger.info(f"Division result: {a} / {b} = {result}")
        return f"{a} / {b} = {result}"

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return f"Validation Error: {e}"

    except ToolError as e:
        logger.error(f"Tool error: {e}")
        return f"Error: {e.message}"

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: An unexpected error occurred"


@server.tool()
def list_users() -> str:
    """
    List all users in the database.
    Demonstrates normal operation with error boundary.
    """

    logger.info("Tool 'list_users' called")

    try:
        if len(user_database) == 0:
            return "No users found in the database"

        output = f"Users ({len(user_database)} total):\n"
        for uid, user in user_database.items():
            output = output + f"  [{uid}] {user['name']} ({user['email']}) - {user['role']}\n"

        logger.info(f"Listed {len(user_database)} users")
        return output

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return f"Error: Could not list users"


# ============================================================
# STEP 6: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info("Starting error handling example server...")
    logger.info("Custom error classes: ToolError, ValidationError, NotFoundError")
    server.run(transport="stdio")
