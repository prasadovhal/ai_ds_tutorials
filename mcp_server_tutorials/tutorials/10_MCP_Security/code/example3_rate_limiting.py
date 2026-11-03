"""
example3_rate_limiting.py - MCP Server with Rate Limiting

PURPOSE:
    This example shows how to add rate limiting to an MCP server.
    Rate limiting prevents abuse by restricting how many times
    a tool can be called within a time window.

WHAT YOU WILL LEARN:
    1. How to track call counts per time window
    2. How to reject requests that exceed the limit
    3. How to implement per-tool rate limits
    4. How to clean up old tracking data

WHY RATE LIMITING MATTERS:
    Without rate limiting, a single client could:
    - Overload your server with thousands of requests
    - Use up expensive API quotas in seconds
    - Cause denial of service for other clients
    - Run up your cloud costs

SETUP:
    1. poetry add mcp
    2. Run: python example3_rate_limiting.py
"""

import time
import json

# Import MCP SDK
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Build a simple rate limiter using a dictionary
# ============================================================
# We track timestamps of calls in a dictionary.
# Key = tool name (or client ID), Value = list of timestamps.
# WHY a dict? Because it is the simplest way to track per-tool usage.

# This dictionary stores all call timestamps
# Format: {"tool_name": [timestamp1, timestamp2, ...]}
call_timestamps = {}

# Configuration: how many calls allowed per window
RATE_LIMIT_MAX_CALLS = 5  # Maximum 5 calls
RATE_LIMIT_WINDOW_SECONDS = 60  # Per 60-second window


def check_rate_limit(tool_name):
    """
    Check if a tool call is allowed under the rate limit.

    How it works:
    1. Get the list of timestamps for this tool
    2. Remove timestamps older than the window
    3. If the remaining count is >= max, reject the call
    4. Otherwise, record this call and allow it

    Args:
        tool_name: The name of the tool being called

    Returns:
        Tuple of (is_allowed, message)
        - is_allowed: True if the call is permitted
        - message: Description of the result
    """
    # Get the current time
    now = time.time()

    # Calculate the start of the current time window
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    # Get existing timestamps for this tool, or create empty list
    if tool_name not in call_timestamps:
        call_timestamps[tool_name] = []

    # Remove timestamps that are older than the time window
    # WHY? Because old calls should not count against the current limit
    recent_calls = []
    for timestamp in call_timestamps[tool_name]:
        if timestamp > window_start:
            recent_calls.append(timestamp)

    # Update the stored timestamps (only keep recent ones)
    call_timestamps[tool_name] = recent_calls

    # Check if the limit has been reached
    current_count = len(recent_calls)
    if current_count >= RATE_LIMIT_MAX_CALLS:
        # Calculate when the oldest call in the window will expire
        oldest_call = recent_calls[0]
        wait_seconds = round(oldest_call - window_start, 1)

        message = (
            f"Rate limit exceeded for '{tool_name}'. "
            f"Limit: {RATE_LIMIT_MAX_CALLS} calls per {RATE_LIMIT_WINDOW_SECONDS} seconds. "
            f"Current calls in window: {current_count}. "
            f"Try again in {wait_seconds} seconds."
        )
        return False, message

    # The call is allowed, record the timestamp
    call_timestamps[tool_name].append(now)

    # Calculate remaining calls
    remaining = RATE_LIMIT_MAX_CALLS - current_count - 1

    message = (
        f"Rate limit OK for '{tool_name}'. "
        f"Calls in window: {current_count + 1}/{RATE_LIMIT_MAX_CALLS}. "
        f"Remaining: {remaining}."
    )
    return True, message


def get_rate_limit_status(tool_name):
    """
    Get the current rate limit status for a tool without making a call.

    Args:
        tool_name: The name of the tool to check

    Returns:
        Dictionary with rate limit status
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    # Count recent calls
    if tool_name not in call_timestamps:
        current_count = 0
    else:
        current_count = 0
        for timestamp in call_timestamps[tool_name]:
            if timestamp > window_start:
                current_count = current_count + 1

    remaining = RATE_LIMIT_MAX_CALLS - current_count

    status = {
        "tool_name": tool_name,
        "max_calls": RATE_LIMIT_MAX_CALLS,
        "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
        "calls_in_window": current_count,
        "remaining_calls": remaining,
        "is_limited": remaining <= 0,
    }

    return status


# ============================================================
# Step 2: Create the MCP server
# ============================================================

server = FastMCP("rate-limited-server")


# ============================================================
# Step 3: Define tools with rate limiting
# ============================================================

# Tool 1: A search tool protected by rate limiting

def search(query: str) -> str:
    """
    Search for information (rate limited).

    This tool is limited to 5 calls per 60 seconds.

    Args:
        query: The search query

    Returns:
        Search results or rate limit error
    """
    # Check rate limit BEFORE doing any work
    is_allowed, rate_message = check_rate_limit("search")

    if not is_allowed:
        # Return an error response with rate limit details
        return json.dumps({
            "error": "rate_limit_exceeded",
            "message": rate_message,
            "status": get_rate_limit_status("search"),
        }, indent=2)

    # Rate limit OK - process the request
    # In a real server, this would call an API or database
    results = {
        "query": query,
        "results": [
            {"title": f"Result 1 for '{query}'", "score": 0.95},
            {"title": f"Result 2 for '{query}'", "score": 0.87},
        ],
        "rate_limit": rate_message,
    }

    return json.dumps(results, indent=2)


# Register the tool
server.tool()(search)


# Tool 2: A translate tool with its own rate limit

def translate(text: str, target_language: str = "es") -> str:
    """
    Translate text to another language (rate limited).

    This tool has its own separate rate limit counter.

    Args:
        text: The text to translate
        target_language: Target language code (default: es for Spanish)

    Returns:
        Translated text or rate limit error
    """
    # Check rate limit for this specific tool
    is_allowed, rate_message = check_rate_limit("translate")

    if not is_allowed:
        return json.dumps({
            "error": "rate_limit_exceeded",
            "message": rate_message,
        }, indent=2)

    # Simulate translation (in production, call a translation API)
    result = {
        "original": text,
        "translated": f"[{target_language}] {text} (simulated translation)",
        "target_language": target_language,
        "rate_limit": rate_message,
    }

    return json.dumps(result, indent=2)


# Register the tool
server.tool()(translate)


# Tool 3: Check rate limit status

def check_limits() -> str:
    """
    Check the current rate limit status for all tools.

    Returns:
        JSON with rate limit status for each tool
    """
    # Get status for all known tools
    all_status = {}
    tool_names = ["search", "translate"]

    for name in tool_names:
        all_status[name] = get_rate_limit_status(name)

    return json.dumps(all_status, indent=2)


# Register the tool
server.tool()(check_limits)


# ============================================================
# Step 4: Demonstrate rate limiting
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server with Rate Limiting - Demonstration")
    print("=" * 60)
    print()
    print(f"Configuration: {RATE_LIMIT_MAX_CALLS} calls per {RATE_LIMIT_WINDOW_SECONDS} seconds")
    print()

    # Make several search calls to show rate limiting in action
    print("--- Making 7 search calls (limit is 5) ---")
    print()

    for i in range(7):
        print(f"Call {i + 1}:")
        result = search(f"query {i + 1}")
        # Parse the result to show a summary
        parsed = json.loads(result)
        if "error" in parsed:
            print(f"  BLOCKED: {parsed['message']}")
        else:
            print(f"  OK: {parsed['rate_limit']}")
        print()

    # Check status
    print("--- Rate Limit Status ---")
    status = check_limits()
    print(status)
    print()

    # Show that translate has its own counter
    print("--- Translate tool has a separate counter ---")
    result = translate("Hello world", "fr")
    parsed = json.loads(result)
    if "error" in parsed:
        print(f"  BLOCKED: {parsed['message']}")
    else:
        print(f"  OK: {parsed['rate_limit']}")
    print()

    print("=" * 60)
    print("Key Takeaways:")
    print("  1. Check rate limits BEFORE processing the request")
    print("  2. Each tool can have its own rate limit counter")
    print("  3. Old timestamps are cleaned up automatically")
    print("  4. Return clear messages about remaining calls")
    print("  5. In production, use client IDs for per-user limits")
    print("=" * 60)

    # To run as MCP server (uncomment):
    # server.run()
