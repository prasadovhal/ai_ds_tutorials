"""
exercise3_solution.py - Solution: Server with Rate Limiting and Logging

Solution for exercise3_rate_limited_server.py.
A quote-of-the-day MCP server with rate limiting and audit logging.
"""

import json
import time
import random
import logging

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Rate limit configuration
# ============================================================

# Each tool has its own rate limit
# Format: {"tool_name": {"max_calls": N, "window_seconds": N}}
RATE_LIMITS = {
    "get_quote": {"max_calls": 3, "window_seconds": 60},
    "add_quote": {"max_calls": 1, "window_seconds": 60},
    "list_quotes": {"max_calls": 5, "window_seconds": 60},
}

# Storage for call timestamps
# Format: {"tool_name": [timestamp1, timestamp2, ...]}
call_log = {}

# ============================================================
# Step 2: Rate limiter implementation
# ============================================================

def check_rate_limit(tool_name):
    """
    Check if a tool call is allowed under its rate limit.

    Args:
        tool_name: Name of the tool being called

    Returns:
        Tuple of (is_allowed, info_dict)
    """
    now = time.time()

    # Get the limit for this tool
    limit_config = RATE_LIMITS.get(tool_name)
    if limit_config is None:
        # No limit configured, allow the call
        return True, {"message": "No rate limit configured"}

    max_calls = limit_config["max_calls"]
    window = limit_config["window_seconds"]
    window_start = now - window

    # Get timestamps for this tool
    if tool_name not in call_log:
        call_log[tool_name] = []

    # Remove old timestamps
    recent = []
    for ts in call_log[tool_name]:
        if ts > window_start:
            recent.append(ts)
    call_log[tool_name] = recent

    current_count = len(recent)

    # Check limit
    if current_count >= max_calls:
        oldest = recent[0]
        wait = round(oldest + window - now, 1)
        info = {
            "allowed": False,
            "message": f"Rate limit exceeded: {current_count}/{max_calls} in {window}s window",
            "retry_after_seconds": wait,
            "calls_in_window": current_count,
            "max_calls": max_calls,
        }
        return False, info

    # Allow and record
    call_log[tool_name].append(now)
    remaining = max_calls - current_count - 1

    info = {
        "allowed": True,
        "message": f"OK: {current_count + 1}/{max_calls} calls used",
        "remaining": remaining,
        "calls_in_window": current_count + 1,
        "max_calls": max_calls,
    }
    return True, info


def get_all_limits_status():
    """Get rate limit status for all tools."""
    now = time.time()
    status = {}

    for tool_name, config in RATE_LIMITS.items():
        window_start = now - config["window_seconds"]

        if tool_name in call_log:
            count = 0
            for ts in call_log[tool_name]:
                if ts > window_start:
                    count = count + 1
        else:
            count = 0

        status[tool_name] = {
            "calls_used": count,
            "max_calls": config["max_calls"],
            "remaining": config["max_calls"] - count,
            "window_seconds": config["window_seconds"],
        }

    return status


# ============================================================
# Step 3: Audit log
# ============================================================

audit_entries = []


def log_audit(tool_name, allowed, details=""):
    """
    Record an audit entry for a tool call.

    Args:
        tool_name: Name of the tool called
        allowed: Whether the call was allowed
        details: Additional details about the call
    """
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tool": tool_name,
        "allowed": allowed,
        "details": details,
    }
    audit_entries.append(entry)

    # Keep only last 100 entries to prevent memory issues
    if len(audit_entries) > 100:
        audit_entries.pop(0)


# ============================================================
# Step 4: Create MCP server and quotes
# ============================================================

server = FastMCP("rate-limited-quotes")

# Pre-populated quotes
quotes = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
    {"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    {"text": "Life is what happens when you are busy making other plans.", "author": "John Lennon"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
]

# ============================================================
# Step 5: Define tools
# ============================================================

def get_quote() -> str:
    """
    Get a random quote. Rate limited to 3 calls per minute.

    Returns:
        JSON with a random quote or rate limit error
    """
    # Check rate limit
    allowed, limit_info = check_rate_limit("get_quote")
    log_audit("get_quote", allowed, limit_info["message"])

    if not allowed:
        return json.dumps({
            "error": "rate_limit_exceeded",
            "rate_limit": limit_info,
        }, indent=2)

    # Pick a random quote
    quote = random.choice(quotes)

    return json.dumps({
        "quote": quote,
        "rate_limit": limit_info,
    }, indent=2)


# Register the tool
server.tool()(get_quote)


def add_quote(text: str, author: str) -> str:
    """
    Add a new quote. Rate limited to 1 call per minute.

    Args:
        text: The quote text
        author: Who said it

    Returns:
        JSON with result or rate limit error
    """
    # Check rate limit
    allowed, limit_info = check_rate_limit("add_quote")
    log_audit("add_quote", allowed, f"text='{text[:50]}', {limit_info['message']}")

    if not allowed:
        return json.dumps({
            "error": "rate_limit_exceeded",
            "rate_limit": limit_info,
        }, indent=2)

    # Validate inputs
    if not text or len(text.strip()) < 5:
        return json.dumps({"error": "Quote text must be at least 5 characters"})
    if not author or len(author.strip()) < 2:
        return json.dumps({"error": "Author name must be at least 2 characters"})

    # Add the quote
    new_quote = {"text": text.strip(), "author": author.strip()}
    quotes.append(new_quote)

    return json.dumps({
        "status": "added",
        "quote": new_quote,
        "total_quotes": len(quotes),
        "rate_limit": limit_info,
    }, indent=2)


# Register the tool
server.tool()(add_quote)


def list_quotes() -> str:
    """
    List all quotes. Rate limited to 5 calls per minute.

    Returns:
        JSON with all quotes or rate limit error
    """
    allowed, limit_info = check_rate_limit("list_quotes")
    log_audit("list_quotes", allowed, limit_info["message"])

    if not allowed:
        return json.dumps({
            "error": "rate_limit_exceeded",
            "rate_limit": limit_info,
        }, indent=2)

    return json.dumps({
        "quotes": quotes,
        "total": len(quotes),
        "rate_limit": limit_info,
    }, indent=2)


# Register the tool
server.tool()(list_quotes)


def rate_status() -> str:
    """
    Check rate limit status for all tools.

    Returns:
        JSON with current rate limit status
    """
    return json.dumps(get_all_limits_status(), indent=2)


# Register the tool
server.tool()(rate_status)


def view_audit_log() -> str:
    """
    View the last 20 audit log entries.

    Returns:
        JSON with recent audit entries
    """
    # Get the last 20 entries
    recent = audit_entries[-20:]

    return json.dumps({
        "entries": recent,
        "total_entries": len(audit_entries),
        "showing": len(recent),
    }, indent=2)


# Register the tool
server.tool()(view_audit_log)


# ============================================================
# Main block
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 3 Solution: Rate Limited Quote Server")
    print("=" * 60)
    print()

    # Get quotes (should work 3 times, then fail)
    print("--- Getting quotes (limit: 3/minute) ---")
    for i in range(5):
        print(f"\nCall {i + 1}:")
        result = get_quote()
        parsed = json.loads(result)
        if "error" in parsed:
            print(f"  BLOCKED: {parsed['rate_limit']['message']}")
        else:
            print(f"  OK: \"{parsed['quote']['text'][:50]}...\"")
            print(f"  Rate: {parsed['rate_limit']['message']}")
    print()

    # Add quotes (should work 1 time, then fail)
    print("--- Adding quotes (limit: 1/minute) ---")
    for i in range(3):
        print(f"\nCall {i + 1}:")
        result = add_quote(f"Test quote number {i + 1}", "Test Author")
        parsed = json.loads(result)
        if "error" in parsed:
            print(f"  BLOCKED")
        else:
            print(f"  OK: Added quote")

    print()
    print("--- Rate limit status ---")
    print(rate_status())

    print()
    print("--- Audit log ---")
    print(view_audit_log())

    # To run as MCP server (uncomment):
    # server.run()
