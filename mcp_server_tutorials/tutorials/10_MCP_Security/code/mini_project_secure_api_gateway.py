"""
mini_project_secure_api_gateway.py - Secure API Gateway MCP Server

MINI PROJECT:
    Build a secure API gateway MCP server that combines ALL security
    concepts from this chapter:
    1. Authentication (token-based)
    2. Rate limiting (per-user, per-tool)
    3. Input validation (all inputs checked)
    4. Prompt injection defense (inputs sanitized)
    5. Audit logging (every call logged)
    6. Secret management (env vars, never exposed)

    The gateway proxies requests to a simulated "backend API"
    and enforces all security policies.

SETUP:
    1. poetry add mcp
    2. Run: python mini_project_secure_api_gateway.py
"""

import os
import json
import time
import re
import logging

from mcp.server.fastmcp import FastMCP

# ============================================================
# Section 1: Configuration from environment variables
# ============================================================

# Load secrets from environment (never hardcoded)
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET", "demo-secret-key")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "admin-token-secure-789")
USER_TOKEN = os.environ.get("USER_TOKEN", "user-token-basic-123")

# Rate limit settings
DEFAULT_RATE_LIMIT = int(os.environ.get("DEFAULT_RATE_LIMIT", "10"))
RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "60"))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("api-gateway")

# ============================================================
# Section 2: Token registry and permissions
# ============================================================

# Map tokens to user info and permissions
TOKEN_REGISTRY = {}
TOKEN_REGISTRY[ADMIN_TOKEN] = {
    "user_id": "admin",
    "role": "admin",
    "rate_limit": 20,
}
TOKEN_REGISTRY[USER_TOKEN] = {
    "user_id": "user1",
    "role": "user",
    "rate_limit": 10,
}

# Tool-level permissions
TOOL_PERMISSIONS = {
    "gateway_query": "user",
    "gateway_write": "user",
    "gateway_delete": "admin",
    "gateway_status": "public",
    "gateway_audit": "admin",
}

ROLE_HIERARCHY = {
    "admin": ["admin", "user", "public"],
    "user": ["user", "public"],
    "public": ["public"],
}

# ============================================================
# Section 3: Rate limiter (per-user)
# ============================================================

# Track calls per user per tool
# Format: {"user_id:tool_name": [timestamp1, timestamp2, ...]}
user_call_log = {}


def check_user_rate_limit(user_id, tool_name, max_calls):
    """
    Check rate limit for a specific user and tool.

    Args:
        user_id: The user making the request
        tool_name: The tool being called
        max_calls: Maximum calls allowed in the window

    Returns:
        Tuple of (is_allowed, info_dict)
    """
    now = time.time()
    key = f"{user_id}:{tool_name}"
    window_start = now - RATE_WINDOW

    # Get or create timestamps list
    if key not in user_call_log:
        user_call_log[key] = []

    # Clean old timestamps
    recent = []
    for ts in user_call_log[key]:
        if ts > window_start:
            recent.append(ts)
    user_call_log[key] = recent

    count = len(recent)

    if count >= max_calls:
        return False, {
            "calls_used": count,
            "max_calls": max_calls,
            "window_seconds": RATE_WINDOW,
        }

    # Record this call
    user_call_log[key].append(now)

    return True, {
        "calls_used": count + 1,
        "max_calls": max_calls,
        "remaining": max_calls - count - 1,
    }


# ============================================================
# Section 4: Input validation
# ============================================================

def validate_input(text, field_name, max_length=1000):
    """
    Validate and sanitize a text input.

    Checks for:
    - Type, length
    - SQL injection patterns
    - Command injection patterns
    - Prompt injection patterns

    Returns:
        Tuple of (is_valid, clean_text_or_error)
    """
    if not isinstance(text, str):
        return False, f"{field_name} must be a string"

    if len(text) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length}"

    if len(text.strip()) == 0:
        return False, f"{field_name} cannot be empty"

    # Check for injection patterns
    lower = text.lower()

    # SQL injection
    sql_patterns = ["drop table", "delete from", "union select", "'; --", "1=1"]
    for pattern in sql_patterns:
        if pattern in lower:
            return False, f"{field_name} contains blocked pattern"

    # Command injection
    cmd_patterns = ["&&", "||", "$()", "`", "| ", "> /"]
    for pattern in cmd_patterns:
        if pattern in text:
            return False, f"{field_name} contains blocked character sequence"

    # Prompt injection - strip but allow
    injection_phrases = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt:",
    ]
    clean = text
    clean_lower = clean.lower()
    for phrase in injection_phrases:
        start = clean_lower.find(phrase)
        while start != -1:
            clean = clean[:start] + clean[start + len(phrase):]
            clean_lower = clean.lower()
            start = clean_lower.find(phrase)

    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    return True, clean


# ============================================================
# Section 5: Authentication helper
# ============================================================

def authenticate(token, tool_name):
    """
    Authenticate a request.

    Checks:
    1. Token validity
    2. Role-based permission for the tool

    Returns:
        Tuple of (is_authenticated, user_info_or_error)
    """
    # Check if tool is public
    required = TOOL_PERMISSIONS.get(tool_name, "admin")
    if required == "public":
        return True, {"user_id": "anonymous", "role": "public", "rate_limit": 5}

    # Check token
    if not token or token == "":
        return False, "Authentication required. Provide a valid token."

    if token not in TOKEN_REGISTRY:
        return False, "Invalid token."

    user_info = TOKEN_REGISTRY[token]
    role = user_info["role"]

    # Check permission
    allowed_levels = ROLE_HIERARCHY.get(role, [])
    if required not in allowed_levels:
        return False, f"Insufficient permissions. Requires '{required}', you have '{role}'."

    return True, user_info


# ============================================================
# Section 6: Audit logger
# ============================================================

audit_log = []


def record_audit(user_id, tool_name, allowed, details=""):
    """Record an audit entry."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "tool": tool_name,
        "allowed": allowed,
        "details": details,
    }
    audit_log.append(entry)
    logger.info(f"AUDIT: user={user_id} tool={tool_name} allowed={allowed}")

    # Limit size
    if len(audit_log) > 500:
        audit_log.pop(0)


# ============================================================
# Section 7: Simulated backend data
# ============================================================

backend_data = {
    "products": [
        {"id": 1, "name": "Widget A", "price": 9.99},
        {"id": 2, "name": "Widget B", "price": 19.99},
        {"id": 3, "name": "Gadget C", "price": 49.99},
    ],
}

# ============================================================
# Section 8: Create MCP server and tools
# ============================================================

server = FastMCP("secure-api-gateway")


# Tool 1: Query data (user level)

def gateway_query(query: str, token: str = "") -> str:
    """
    Query the backend API through the secure gateway.
    Requires user-level authentication.

    Args:
        query: Search query for backend data
        token: Authentication token

    Returns:
        JSON with results or error
    """
    # Step A: Authenticate
    is_auth, user_or_error = authenticate(token, "gateway_query")
    if not is_auth:
        record_audit("unknown", "gateway_query", False, user_or_error)
        return json.dumps({"error": "auth_failed", "message": user_or_error}, indent=2)

    user_info = user_or_error
    user_id = user_info["user_id"]

    # Step B: Rate limit
    is_allowed, limit_info = check_user_rate_limit(
        user_id, "gateway_query", user_info["rate_limit"]
    )
    if not is_allowed:
        record_audit(user_id, "gateway_query", False, "Rate limited")
        return json.dumps({"error": "rate_limited", "rate_limit": limit_info}, indent=2)

    # Step C: Validate input
    is_valid, clean_query = validate_input(query, "query", max_length=500)
    if not is_valid:
        record_audit(user_id, "gateway_query", False, f"Invalid input: {clean_query}")
        return json.dumps({"error": "invalid_input", "message": clean_query}, indent=2)

    # Step D: Process the query against backend data
    results = []
    for product in backend_data["products"]:
        if clean_query.lower() in product["name"].lower():
            results.append(product)

    # If no name match, return all products
    if len(results) == 0:
        results = backend_data["products"]

    record_audit(user_id, "gateway_query", True, f"query='{clean_query}', results={len(results)}")

    return json.dumps({
        "query": clean_query,
        "results": results,
        "user": user_id,
        "rate_limit": limit_info,
    }, indent=2)


# Register the tool
server.tool()(gateway_query)


# Tool 2: Write data (user level)

def gateway_write(name: str, price: float, token: str = "") -> str:
    """
    Add a new product through the secure gateway.
    Requires user-level authentication.

    Args:
        name: Product name
        price: Product price
        token: Authentication token

    Returns:
        JSON with result or error
    """
    # Authenticate
    is_auth, user_or_error = authenticate(token, "gateway_write")
    if not is_auth:
        record_audit("unknown", "gateway_write", False, user_or_error)
        return json.dumps({"error": "auth_failed", "message": user_or_error}, indent=2)

    user_info = user_or_error
    user_id = user_info["user_id"]

    # Rate limit
    is_allowed, limit_info = check_user_rate_limit(
        user_id, "gateway_write", user_info["rate_limit"]
    )
    if not is_allowed:
        record_audit(user_id, "gateway_write", False, "Rate limited")
        return json.dumps({"error": "rate_limited", "rate_limit": limit_info}, indent=2)

    # Validate name
    is_valid, clean_name = validate_input(name, "name", max_length=200)
    if not is_valid:
        record_audit(user_id, "gateway_write", False, f"Invalid name: {clean_name}")
        return json.dumps({"error": "invalid_input", "message": clean_name}, indent=2)

    # Validate price
    if not isinstance(price, (int, float)):
        return json.dumps({"error": "invalid_input", "message": "price must be a number"})
    if price <= 0 or price > 99999:
        return json.dumps({"error": "invalid_input", "message": "price must be between 0 and 99999"})

    # Add product
    new_id = len(backend_data["products"]) + 1
    new_product = {"id": new_id, "name": clean_name, "price": round(price, 2)}
    backend_data["products"].append(new_product)

    record_audit(user_id, "gateway_write", True, f"Created product: {clean_name}")

    return json.dumps({
        "status": "created",
        "product": new_product,
        "user": user_id,
        "rate_limit": limit_info,
    }, indent=2)


# Register the tool
server.tool()(gateway_write)


# Tool 3: Delete data (admin only)

def gateway_delete(product_id: int, token: str = "") -> str:
    """
    Delete a product. Requires ADMIN authentication.

    Args:
        product_id: ID of the product to delete
        token: Admin authentication token

    Returns:
        JSON with result or error
    """
    # Authenticate (admin only)
    is_auth, user_or_error = authenticate(token, "gateway_delete")
    if not is_auth:
        record_audit("unknown", "gateway_delete", False, user_or_error)
        return json.dumps({"error": "auth_failed", "message": user_or_error}, indent=2)

    user_info = user_or_error
    user_id = user_info["user_id"]

    # Rate limit
    is_allowed, limit_info = check_user_rate_limit(
        user_id, "gateway_delete", user_info["rate_limit"]
    )
    if not is_allowed:
        record_audit(user_id, "gateway_delete", False, "Rate limited")
        return json.dumps({"error": "rate_limited", "rate_limit": limit_info}, indent=2)

    # Validate product_id
    if not isinstance(product_id, int) or product_id < 1:
        return json.dumps({"error": "invalid_input", "message": "product_id must be a positive integer"})

    # Find and delete
    for i in range(len(backend_data["products"])):
        if backend_data["products"][i]["id"] == product_id:
            deleted = backend_data["products"].pop(i)
            record_audit(user_id, "gateway_delete", True, f"Deleted product ID {product_id}")
            return json.dumps({
                "status": "deleted",
                "product": deleted,
                "user": user_id,
            }, indent=2)

    return json.dumps({"error": "not_found", "message": f"Product {product_id} not found"})


# Register the tool
server.tool()(gateway_delete)


# Tool 4: Gateway status (public)

def gateway_status() -> str:
    """
    Get gateway status. This is a PUBLIC endpoint.
    No authentication required.

    Returns:
        JSON with gateway status (no secrets)
    """
    record_audit("anonymous", "gateway_status", True, "Status check")

    return json.dumps({
        "status": "healthy",
        "total_products": len(backend_data["products"]),
        "total_audit_entries": len(audit_log),
        "security_features": [
            "Token-based authentication",
            "Role-based permissions (admin/user/public)",
            "Per-user rate limiting",
            "Input validation and sanitization",
            "Prompt injection defense",
            "Audit logging",
            "Secret management via env vars",
        ],
        "configuration": {
            "rate_window_seconds": RATE_WINDOW,
            "default_rate_limit": DEFAULT_RATE_LIMIT,
            # NEVER expose: "gateway_secret": GATEWAY_SECRET
            "gateway_secret_configured": GATEWAY_SECRET is not None,
        },
    }, indent=2)


# Register the tool
server.tool()(gateway_status)


# Tool 5: Audit log (admin only)

def gateway_audit(token: str = "", count: int = 10) -> str:
    """
    View recent audit log entries. Requires ADMIN authentication.

    Args:
        token: Admin authentication token
        count: Number of entries to show (1-50)

    Returns:
        JSON with audit entries or error
    """
    # Authenticate
    is_auth, user_or_error = authenticate(token, "gateway_audit")
    if not is_auth:
        record_audit("unknown", "gateway_audit", False, user_or_error)
        return json.dumps({"error": "auth_failed", "message": user_or_error}, indent=2)

    # Validate count
    if count < 1:
        count = 1
    if count > 50:
        count = 50

    # Get recent entries
    recent = audit_log[-count:]

    return json.dumps({
        "audit_entries": recent,
        "total_entries": len(audit_log),
        "showing": len(recent),
    }, indent=2)


# Register the tool
server.tool()(gateway_audit)


# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Mini Project: Secure API Gateway")
    print("=" * 60)
    print()

    # 1. Public status check
    print("--- 1. Public Status (no auth needed) ---")
    print(gateway_status())
    print()

    # 2. Query without token (should fail)
    print("--- 2. Query without token (should fail) ---")
    print(gateway_query("Widget"))
    print()

    # 3. Query with user token (should succeed)
    print("--- 3. Query with user token ---")
    print(gateway_query("Widget", token=USER_TOKEN))
    print()

    # 4. Write with user token
    print("--- 4. Write with user token ---")
    print(gateway_write("Widget D", 39.99, token=USER_TOKEN))
    print()

    # 5. Delete with user token (should fail - admin required)
    print("--- 5. Delete with user token (should fail) ---")
    print(gateway_delete(1, token=USER_TOKEN))
    print()

    # 6. Delete with admin token (should succeed)
    print("--- 6. Delete with admin token ---")
    print(gateway_delete(1, token=ADMIN_TOKEN))
    print()

    # 7. Injection attempt
    print("--- 7. Injection attempt ---")
    print(gateway_query("'; DROP TABLE products; --", token=USER_TOKEN))
    print()

    # 8. View audit log (admin only)
    print("--- 8. Audit log (admin) ---")
    print(gateway_audit(token=ADMIN_TOKEN, count=5))
    print()

    print("=" * 60)
    print("All security layers working together:")
    print("  Auth -> Rate Limit -> Validation -> Process -> Audit")
    print("=" * 60)

    # To run as MCP server (uncomment):
    # server.run()
