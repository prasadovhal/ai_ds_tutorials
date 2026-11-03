"""
example4_permission_model.py - MCP Server with Tool-Level Permissions

PURPOSE:
    This example shows how to implement a permission model where
    some tools require an authorization token and others are public.

WHAT YOU WILL LEARN:
    1. How to define public vs. protected tools
    2. How to check authorization tokens before tool execution
    3. How to implement role-based access (admin vs. user)
    4. How to return proper error messages for unauthorized access

WHY PERMISSIONS MATTER:
    Not all tools should be available to everyone.
    - Read tools might be public
    - Write tools should require authentication
    - Admin tools should require elevated privileges

SETUP:
    1. poetry add mcp
    2. Run: python example4_permission_model.py
"""

import json

# Import MCP SDK
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Define the permission system
# ============================================================
# We use a simple dictionary to map tokens to roles.
# In production, you would use a proper auth system (OAuth, JWT, etc.)

# Valid tokens and their roles
# WHY a dictionary? It is the simplest way to map tokens to roles.
# In production, use a database or auth service.
VALID_TOKENS = {
    "user-token-abc123": "user",
    "admin-token-xyz789": "admin",
}

# Tool permissions: which role is required for each tool
# "public" means no token needed
# "user" means any valid token works
# "admin" means only admin tokens work
TOOL_PERMISSIONS = {
    "list_items": "public",
    "get_item": "public",
    "create_item": "user",
    "update_item": "user",
    "delete_item": "admin",
    "manage_users": "admin",
}

# Role hierarchy: admin has all permissions of user
ROLE_HIERARCHY = {
    "admin": ["admin", "user", "public"],
    "user": ["user", "public"],
    "public": ["public"],
}


def check_permission(token, tool_name):
    """
    Check if a token has permission to use a specific tool.

    How it works:
    1. Look up the required permission level for the tool
    2. If public, allow without checking the token
    3. If not public, validate the token
    4. Check if the token's role includes the required permission

    Args:
        token: The authorization token (can be None for public tools)
        tool_name: The name of the tool to check

    Returns:
        Tuple of (is_allowed, role_or_error_message)
    """
    # Step 1: Get the required permission level for this tool
    required_level = TOOL_PERMISSIONS.get(tool_name, "admin")

    # Step 2: If the tool is public, allow without checking token
    if required_level == "public":
        return True, "public"

    # Step 3: Check if a token was provided
    if token is None or token == "":
        return False, f"Tool '{tool_name}' requires authentication. Please provide a valid token."

    # Step 4: Validate the token
    if token not in VALID_TOKENS:
        return False, f"Invalid token. Access denied to '{tool_name}'."

    # Step 5: Get the role for this token
    role = VALID_TOKENS[token]

    # Step 6: Check if the role has the required permission
    allowed_levels = ROLE_HIERARCHY.get(role, [])

    if required_level in allowed_levels:
        return True, role
    else:
        return False, (
            f"Insufficient permissions. Tool '{tool_name}' requires '{required_level}' role, "
            f"but your token has '{role}' role."
        )


# ============================================================
# Step 2: Create the MCP server
# ============================================================

server = FastMCP("permission-server")


# ============================================================
# Step 3: In-memory data store
# ============================================================
# A simple list to store items for our CRUD operations

items_store = [
    {"id": 1, "name": "Widget A", "price": 9.99, "owner": "admin"},
    {"id": 2, "name": "Widget B", "price": 19.99, "owner": "user1"},
    {"id": 3, "name": "Widget C", "price": 29.99, "owner": "user2"},
]

next_id = 4


# ============================================================
# Step 4: Define tools with permission checks
# ============================================================

# Tool 1: List items (PUBLIC - no token needed)

def list_items() -> str:
    """
    List all items in the store. This is a PUBLIC tool.
    No authentication token is required.

    Returns:
        JSON string with all items
    """
    # No permission check needed - this tool is public
    result = {
        "items": items_store,
        "total": len(items_store),
        "permission": "public (no token required)",
    }

    return json.dumps(result, indent=2)


# Register the tool
server.tool()(list_items)


# Tool 2: Get a single item (PUBLIC)

def get_item(item_id: int) -> str:
    """
    Get a specific item by ID. This is a PUBLIC tool.

    Args:
        item_id: The ID of the item to retrieve

    Returns:
        JSON string with the item or error
    """
    # Search for the item
    for item in items_store:
        if item["id"] == item_id:
            return json.dumps({
                "item": item,
                "permission": "public",
            }, indent=2)

    return json.dumps({"error": f"Item with ID {item_id} not found"})


# Register the tool
server.tool()(get_item)


# Tool 3: Create item (REQUIRES USER token)

def create_item(name: str, price: float, token: str = "") -> str:
    """
    Create a new item. Requires USER-level authentication.

    Args:
        name: Name of the new item
        price: Price of the item
        token: Authorization token (required)

    Returns:
        JSON string with created item or permission error
    """
    global next_id

    # Check permission BEFORE doing any work
    is_allowed, role_or_error = check_permission(token, "create_item")

    if not is_allowed:
        return json.dumps({
            "error": "permission_denied",
            "message": role_or_error,
        }, indent=2)

    # Permission granted - create the item
    new_item = {
        "id": next_id,
        "name": name,
        "price": price,
        "owner": role_or_error,
    }
    items_store.append(new_item)
    next_id = next_id + 1

    return json.dumps({
        "status": "created",
        "item": new_item,
        "authenticated_as": role_or_error,
    }, indent=2)


# Register the tool
server.tool()(create_item)


# Tool 4: Delete item (REQUIRES ADMIN token)

def delete_item(item_id: int, token: str = "") -> str:
    """
    Delete an item by ID. Requires ADMIN-level authentication.

    Args:
        item_id: The ID of the item to delete
        token: Authorization token (admin required)

    Returns:
        JSON string with result or permission error
    """
    # Check permission BEFORE doing any work
    is_allowed, role_or_error = check_permission(token, "delete_item")

    if not is_allowed:
        return json.dumps({
            "error": "permission_denied",
            "message": role_or_error,
        }, indent=2)

    # Permission granted - find and delete the item
    for i in range(len(items_store)):
        if items_store[i]["id"] == item_id:
            deleted_item = items_store.pop(i)
            return json.dumps({
                "status": "deleted",
                "item": deleted_item,
                "authenticated_as": role_or_error,
            }, indent=2)

    return json.dumps({"error": f"Item with ID {item_id} not found"})


# Register the tool
server.tool()(delete_item)


# Tool 5: Show permissions info

def show_permissions() -> str:
    """
    Show the permission model for all tools.
    This is a PUBLIC tool that helps clients understand access levels.

    Returns:
        JSON string with permission details
    """
    result = {
        "tool_permissions": TOOL_PERMISSIONS,
        "roles": {
            "public": "No authentication needed",
            "user": "Any valid user token required",
            "admin": "Admin token required",
        },
        "example_usage": {
            "public_tool": "list_items() - no token needed",
            "user_tool": "create_item(name='X', price=10, token='user-token-abc123')",
            "admin_tool": "delete_item(item_id=1, token='admin-token-xyz789')",
        },
    }

    return json.dumps(result, indent=2)


# Register the tool
server.tool()(show_permissions)


# ============================================================
# Step 5: Demonstrate the permission model
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server with Tool-Level Permissions - Demonstration")
    print("=" * 60)
    print()

    # Show permissions
    print("--- Permission Model ---")
    print(show_permissions())
    print()

    # Test 1: Public tool (no token needed)
    print("--- Test 1: Public tool (list_items) ---")
    print(list_items())
    print()

    # Test 2: User tool WITHOUT token (should fail)
    print("--- Test 2: Create item WITHOUT token (should fail) ---")
    result = create_item("New Widget", 15.99)
    print(result)
    print()

    # Test 3: User tool WITH valid user token (should succeed)
    print("--- Test 3: Create item WITH user token (should succeed) ---")
    result = create_item("New Widget", 15.99, token="user-token-abc123")
    print(result)
    print()

    # Test 4: Admin tool with USER token (should fail)
    print("--- Test 4: Delete item with USER token (should fail) ---")
    result = delete_item(1, token="user-token-abc123")
    print(result)
    print()

    # Test 5: Admin tool with ADMIN token (should succeed)
    print("--- Test 5: Delete item with ADMIN token (should succeed) ---")
    result = delete_item(1, token="admin-token-xyz789")
    print(result)
    print()

    # Test 6: Invalid token
    print("--- Test 6: Create item with INVALID token (should fail) ---")
    result = create_item("Hacked Widget", 0.01, token="fake-token")
    print(result)
    print()

    print("=" * 60)
    print("Key Takeaways:")
    print("  1. Define clear permission levels for each tool")
    print("  2. Check permissions BEFORE processing the request")
    print("  3. Public tools need no token")
    print("  4. Use role hierarchy (admin > user > public)")
    print("  5. Return clear error messages for permission failures")
    print("  6. In production, use proper auth (OAuth, JWT)")
    print("=" * 60)

    # To run as MCP server (uncomment):
    # server.run()
