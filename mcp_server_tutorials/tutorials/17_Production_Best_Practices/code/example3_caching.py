"""
Example 3 - MCP Server with TTL Caching
=========================================
This example shows how to add time-based caching to an MCP server.
Caching avoids re-computing expensive results within a time window.
"""

import time
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Create a simple cache system
# ============================================================

# Module-level cache dictionary
# Format: { key: {"value": ..., "timestamp": ...} }
_cache = {}

# Track cache statistics
_cache_stats = {"hits": 0, "misses": 0}


def set_cache(key: str, value: str) -> None:
    """
    Store a value in the cache with the current timestamp.
    """
    _cache[key] = {
        "value": value,
        "timestamp": time.time(),
    }


def get_cache(key: str, ttl: int = 300) -> str | None:
    """
    Get a value from cache if it exists and hasn't expired.

    Args:
        key: The cache key to look up.
        ttl: Time-to-live in seconds (default: 300 = 5 minutes).

    Returns:
        The cached value, or None if expired/missing.
    """
    if key not in _cache:
        # Cache miss -- key doesn't exist
        _cache_stats["misses"] += 1
        return None

    entry = _cache[key]
    age = time.time() - entry["timestamp"]

    if age > ttl:
        # Cache miss -- entry has expired
        del _cache[key]
        _cache_stats["misses"] += 1
        return None

    # Cache hit!
    _cache_stats["hits"] += 1
    return entry["value"]


# ============================================================
# Step 2: Create MCP server with cached tools
# ============================================================

mcp = FastMCP("CachingServer")


@mcp.tool()
def get_time(label: str = "default") -> str:
    """
    Get the current time, cached for 10 seconds.
    Multiple calls within 10 seconds return the same result.
    The label lets you test separate cache entries.
    """
    cache_key = f"time_{label}"

    # Try to get from cache (10 second TTL)
    cached = get_cache(cache_key, ttl=10)
    if cached is not None:
        return f"[CACHED] {cached}"

    # Not in cache -- compute fresh result
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    result = f"Time for '{label}': {current_time}"

    # Store in cache
    set_cache(cache_key, result)
    return f"[FRESH] {result}"


@mcp.tool()
def get_cache_stats() -> str:
    """
    Get statistics about cache usage.
    Shows hits, misses, and current cache size.
    """
    total = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total * 100) if total > 0 else 0.0

    return (
        f"Cache Statistics:\n"
        f"  Hits:       {_cache_stats['hits']}\n"
        f"  Misses:     {_cache_stats['misses']}\n"
        f"  Hit Rate:   {hit_rate:.1f}%\n"
        f"  Entries:    {len(_cache)}"
    )


# ============================================================
# Step 3: Demo the caching behavior
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("MCP Server with TTL Caching - Demo")
    print("=" * 50)

    # Demonstrate caching behavior locally
    print("\nCall 1 (should be FRESH):")
    print(" ", get_time("demo"))

    print("\nCall 2 immediately (should be CACHED):")
    print(" ", get_time("demo"))

    print("\nCall with different label (should be FRESH):")
    print(" ", get_time("other"))

    print("\nCache stats:")
    print(" ", get_cache_stats())

    # To run as MCP server, uncomment the line below:
    # mcp.run()
    print("\nTo run as MCP server, use: mcp.run()")
