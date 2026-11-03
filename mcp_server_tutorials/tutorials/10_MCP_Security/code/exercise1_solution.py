"""
exercise1_solution.py - Solution: Server with Proper Secret Management

This is the solution for exercise1_secure_server.py.
It demonstrates a complete MCP server that:
1. Loads secrets from environment variables
2. Validates at startup
3. Never exposes secrets in responses
"""

import os
import json
import logging

# Try to load .env file for development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Load environment variables
# ============================================================

# Required secret - no default value
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

# Optional configuration with defaults
STORAGE_PATH = os.environ.get("STORAGE_PATH", "./data")
SERVER_NAME = os.environ.get("SERVER_NAME", "secure-kv-store")

# ============================================================
# Step 2: Set up logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(SERVER_NAME)

# ============================================================
# Step 3: Validate secrets at startup
# ============================================================

def validate_config():
    """
    Check that all required secrets are present.
    Log the status but NEVER log the actual values.
    Returns True if valid, False if not.
    """
    errors = []

    # Check required secrets
    if not ENCRYPTION_KEY:
        errors.append("ENCRYPTION_KEY is not set")

    # Log configuration status
    logger.info("=" * 40)
    logger.info("Configuration Status:")
    logger.info(f"  ENCRYPTION_KEY: {'SET' if ENCRYPTION_KEY else 'NOT SET'}")
    logger.info(f"  STORAGE_PATH: {STORAGE_PATH}")
    logger.info(f"  SERVER_NAME: {SERVER_NAME}")
    logger.info("=" * 40)

    if errors:
        for error in errors:
            logger.error(f"  MISSING: {error}")
        return False

    logger.info("All required secrets are configured.")
    return True


# ============================================================
# Step 4: Create the MCP server
# ============================================================

server = FastMCP(SERVER_NAME)

# ============================================================
# Step 5: Create in-memory key-value store
# ============================================================

# Simple dictionary to store key-value pairs
kv_store = {}

# ============================================================
# Step 6: Tool - store_value
# ============================================================

def store_value(key: str, value: str) -> str:
    """
    Store a key-value pair in the secure store.

    Args:
        key: The key to store (non-empty string)
        value: The value to store (non-empty string)

    Returns:
        JSON string with result
    """
    # Validate inputs
    if not key or len(key.strip()) == 0:
        return json.dumps({"error": "Key cannot be empty"})

    if not value or len(value.strip()) == 0:
        return json.dumps({"error": "Value cannot be empty"})

    # Store the value
    # In a real server, we would encrypt the value using ENCRYPTION_KEY
    # but we NEVER include the key in the response
    kv_store[key] = value

    logger.info(f"Stored key: '{key}'")

    result = {
        "status": "stored",
        "key": key,
        "total_items": len(kv_store),
        # NEVER include: "encryption_key": ENCRYPTION_KEY
    }

    return json.dumps(result, indent=2)


# Register the tool
server.tool()(store_value)

# ============================================================
# Step 7: Tool - get_value
# ============================================================

def get_value(key: str) -> str:
    """
    Retrieve a value by key from the secure store.

    Args:
        key: The key to look up

    Returns:
        JSON string with the value or error
    """
    if not key or len(key.strip()) == 0:
        return json.dumps({"error": "Key cannot be empty"})

    if key not in kv_store:
        return json.dumps({"error": f"Key '{key}' not found"})

    result = {
        "key": key,
        "value": kv_store[key],
        # NEVER include secrets in the response
    }

    return json.dumps(result, indent=2)


# Register the tool
server.tool()(get_value)

# ============================================================
# Step 8: Tool - server_status
# ============================================================

def server_status() -> str:
    """
    Get server status without exposing secrets.

    Returns:
        JSON string with server status
    """
    status = {
        "server_name": SERVER_NAME,
        "status": "healthy",
        "total_items": len(kv_store),
        "stored_keys": list(kv_store.keys()),
        "configuration": {
            "storage_path": STORAGE_PATH,
            # Show whether secret is configured, not its value
            "encryption_key_configured": ENCRYPTION_KEY is not None,
            # NEVER do this: "encryption_key": ENCRYPTION_KEY
        },
    }

    return json.dumps(status, indent=2)


# Register the tool
server.tool()(server_status)

# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 1 Solution: Secure Key-Value Store")
    print("=" * 60)
    print()

    # Validate configuration
    is_valid = validate_config()

    if not is_valid:
        print("WARNING: Configuration incomplete. Set ENCRYPTION_KEY in .env")
        print("Running with demo mode...")
        print()

    # Demonstrate the tools
    print("--- Store some values ---")
    print(store_value("username", "alice"))
    print(store_value("project", "mcp-tutorial"))
    print()

    print("--- Retrieve a value ---")
    print(get_value("username"))
    print()

    print("--- Try missing key ---")
    print(get_value("nonexistent"))
    print()

    print("--- Server status (no secrets exposed) ---")
    print(server_status())
    print()

    print("NOTICE: The ENCRYPTION_KEY value never appears in any output!")

    # To run as MCP server (uncomment):
    # server.run()
