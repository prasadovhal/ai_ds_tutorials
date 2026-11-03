"""
exercise1_secure_server.py - Exercise: Build a Server with Proper Secret Management

EXERCISE:
    Build an MCP server that manages a simple key-value store.
    The server should:
    1. Load an ENCRYPTION_KEY from environment variables
    2. Load a STORAGE_PATH from environment variables (with default)
    3. Validate all required secrets at startup
    4. Never expose secrets in tool responses
    5. Have a tool to store a key-value pair
    6. Have a tool to retrieve a value by key
    7. Have a tool to show server status (without exposing secrets)

REQUIREMENTS:
    - Use os.environ.get() to load secrets
    - Validate secrets at startup (fail fast)
    - Log whether secrets are SET or NOT SET (never log values)
    - All tools must return JSON responses
    - Use the pattern from example1_env_variables.py

HINTS:
    - Look at example1_env_variables.py for the pattern
    - Use a dictionary for the key-value store
    - The ENCRYPTION_KEY is "used" internally but never exposed
    - Return clear error messages

SETUP:
    1. poetry add mcp
    2. Create a .env file:
       ENCRYPTION_KEY=my_secret_key_123
       STORAGE_PATH=./data
    3. Run: python exercise1_secure_server.py

YOUR TASK:
    Fill in the code below where you see "TODO" comments.
"""

import os
import json
import logging

from mcp.server.fastmcp import FastMCP

# ============================================================
# TODO Step 1: Load environment variables
# ============================================================
# Load the following from environment variables:
# - ENCRYPTION_KEY (required, no default)
# - STORAGE_PATH (optional, default: "./data")
# - SERVER_NAME (optional, default: "secure-kv-store")

# YOUR CODE HERE


# ============================================================
# TODO Step 2: Set up logging
# ============================================================
# Set up Python logging. Never log secret values!

# YOUR CODE HERE


# ============================================================
# TODO Step 3: Validate secrets at startup
# ============================================================
# Create a function validate_config() that:
# - Checks if ENCRYPTION_KEY is set
# - Returns True if valid, False if not
# - Logs which secrets are SET vs NOT SET

# YOUR CODE HERE


# ============================================================
# TODO Step 4: Create the MCP server
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO Step 5: Create in-memory key-value store
# ============================================================

# YOUR CODE HERE (use a dictionary)


# ============================================================
# TODO Step 6: Create tool - store_value(key, value)
# ============================================================
# This tool should:
# - Validate key and value are non-empty strings
# - Store the key-value pair
# - Return a JSON success message
# - Register the tool with server.tool()

# YOUR CODE HERE


# ============================================================
# TODO Step 7: Create tool - get_value(key)
# ============================================================
# This tool should:
# - Look up the key in the store
# - Return the value if found
# - Return an error if not found
# - NEVER include ENCRYPTION_KEY in the response

# YOUR CODE HERE


# ============================================================
# TODO Step 8: Create tool - server_status()
# ============================================================
# This tool should return:
# - Server name
# - Number of stored items
# - Whether ENCRYPTION_KEY is configured (True/False, NOT the value!)
# - Storage path

# YOUR CODE HERE


# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 1: Secure Key-Value Store Server")
    print("=" * 60)
    print()
    print("TODO: Implement the server following the instructions above.")
    print("Look at example1_env_variables.py for guidance.")
    print()
    print("Test your implementation by:")
    print("  1. Setting ENCRYPTION_KEY in .env file")
    print("  2. Running this script")
    print("  3. Verifying secrets are never exposed in output")

    # To run as MCP server (uncomment when done):
    # server.run()
