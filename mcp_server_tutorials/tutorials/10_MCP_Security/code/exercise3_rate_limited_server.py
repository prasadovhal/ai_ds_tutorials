"""
exercise3_rate_limited_server.py - Exercise: Server with Rate Limiting and Logging

EXERCISE:
    Build an MCP server for a quote-of-the-day service.
    The server should:
    1. Have a tool to get a random quote (rate limited: 3 per minute)
    2. Have a tool to add a new quote (rate limited: 1 per minute)
    3. Have a tool to list all quotes (rate limited: 5 per minute)
    4. Log every request with timestamp and result
    5. Have a tool to check current rate limit status

REQUIREMENTS:
    - Implement rate limiting using timestamps in a dictionary
    - Different limits for different tools
    - Log all calls (allowed and blocked) with timestamps
    - Return rate limit info in every response
    - Store quotes in a list

HINTS:
    - Look at example3_rate_limiting.py for the pattern
    - Use time.time() for timestamps
    - Keep a separate log list for audit trail
    - Use random.choice() for random quote selection

YOUR TASK:
    Fill in the code below where you see "TODO" comments.
"""

import json
import time
import random
import logging

from mcp.server.fastmcp import FastMCP

# ============================================================
# TODO Step 1: Define rate limit configuration
# ============================================================
# Create a dictionary mapping tool names to their limits:
# - "get_quote": 3 calls per 60 seconds
# - "add_quote": 1 call per 60 seconds
# - "list_quotes": 5 calls per 60 seconds

# YOUR CODE HERE


# ============================================================
# TODO Step 2: Implement rate limiter
# ============================================================
# Create these functions:
# - check_rate_limit(tool_name) -> (allowed, message)
# - get_all_limits_status() -> dict

# YOUR CODE HERE


# ============================================================
# TODO Step 3: Create audit log
# ============================================================
# Create a list to store audit entries.
# Each entry: {"timestamp": ..., "tool": ..., "allowed": ..., "details": ...}

# YOUR CODE HERE


# ============================================================
# TODO Step 4: Create MCP server and quotes storage
# ============================================================

# YOUR CODE HERE (pre-populate with 5 starter quotes)


# ============================================================
# TODO Step 5: Create tools
# ============================================================
# - get_quote() -> random quote, rate limited
# - add_quote(text, author) -> add new quote, rate limited
# - list_quotes() -> all quotes, rate limited
# - rate_status() -> current limits for all tools
# - view_audit_log() -> last 20 audit entries

# YOUR CODE HERE


# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 3: Rate Limited Quote Server")
    print("=" * 60)
    print()
    print("TODO: Implement the server following the instructions above.")
    print("Look at example3_rate_limiting.py for guidance.")

    # To run as MCP server (uncomment when done):
    # server.run()
