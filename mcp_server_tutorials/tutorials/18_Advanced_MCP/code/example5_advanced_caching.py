"""
Example 5 - Advanced Caching with LRU Eviction
================================================
An advanced cache using OrderedDict for LRU eviction,
per-entry TTL, and detailed cache statistics.
"""

import time
from collections import OrderedDict
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Advanced LRU Cache class
# ============================================================

class LRUCache:
    """
    A cache with:
    - Maximum size (LRU eviction when full)
    - Per-entry TTL (time-to-live)
    - Statistics tracking (hits, misses, evictions)
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of entries before LRU eviction.
        """
        # OrderedDict maintains insertion order
        # We move items to the end on access (most recently used)
        self._data = OrderedDict()
        self.max_size = max_size

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str, ttl: int = 300) -> str | None:
        """
        Get a value from cache.
        Returns None if missing or expired.
        Moves accessed entry to end (most recently used).
        """
        if key not in self._data:
            self.misses += 1
            return None

        entry = self._data[key]
        age = time.time() - entry["timestamp"]

        # Check if expired
        if age > ttl:
            del self._data[key]
            self.misses += 1
            return None

        # Cache hit -- move to end (most recently used)
        self._data.move_to_end(key)
        self.hits += 1
        return entry["value"]

    def set(self, key: str, value: str) -> None:
        """
        Store a value in the cache.
        If cache is full, evicts the least recently used entry.
        """
        # If key already exists, remove it first (will be re-added at end)
        if key in self._data:
            del self._data[key]

        # Evict LRU entry if at max capacity
        while len(self._data) >= self.max_size:
            # popitem(last=False) removes the FIRST item (least recently used)
            evicted_key, _ = self._data.popitem(last=False)
            self.evictions += 1

        # Add new entry at the end (most recently used)
        self._data[key] = {
            "value": value,
            "timestamp": time.time(),
        }

    def clear(self) -> int:
        """Clear all cache entries. Returns count of removed entries."""
        count = len(self._data)
        self._data.clear()
        return count

    def stats(self) -> dict:
        """Get cache statistics as a dictionary."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "size": len(self._data),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
        }


# ============================================================
# Step 2: Create the global cache instance
# ============================================================

# Small max_size for demo purposes (easy to trigger eviction)
cache = LRUCache(max_size=5)

# ============================================================
# Step 3: MCP server with cached tools
# ============================================================

mcp = FastMCP("AdvancedCachingServer")


@mcp.tool()
def cached_compute(expression: str) -> str:
    """
    Evaluate a simple math expression with LRU caching.
    Supports basic Python math expressions like '2 + 3' or '10 * 5'.
    Results are cached for 60 seconds.
    """
    cache_key = f"compute_{expression}"

    # Try cache first (60 second TTL)
    cached = cache.get(cache_key, ttl=60)
    if cached is not None:
        return f"[CACHED] {expression} = {cached}"

    # Compute the result
    try:
        # Only allow safe math operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return f"Error: Expression contains invalid characters."

        result = eval(expression)  # Safe because we validated chars above
        result_str = str(result)

        # Store in cache
        cache.set(cache_key, result_str)
        return f"[COMPUTED] {expression} = {result_str}"

    except Exception as e:
        return f"Error computing '{expression}': {e}"


@mcp.tool()
def cache_dashboard() -> str:
    """
    Show detailed cache dashboard with stats and current entries.
    """
    stats = cache.stats()

    lines = [
        "Cache Dashboard",
        "=" * 40,
        f"  Size:       {stats['size']} / {stats['max_size']}",
        f"  Hits:       {stats['hits']}",
        f"  Misses:     {stats['misses']}",
        f"  Evictions:  {stats['evictions']}",
        f"  Hit Rate:   {stats['hit_rate']:.1f}%",
        "",
        "Current Entries:",
    ]

    if cache._data:
        for key, entry in cache._data.items():
            age = time.time() - entry["timestamp"]
            display_key = key.replace("compute_", "")
            lines.append(f"  '{display_key}' = {entry['value']} ({age:.0f}s ago)")
    else:
        lines.append("  (empty)")

    lines.append("=" * 40)
    return "\n".join(lines)


# ============================================================
# Step 4: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Advanced LRU Cache Server - Demo")
    print("=" * 50)

    # Compute several expressions (cache max_size = 5)
    print("\n--- Computing expressions ---")
    expressions = ["2 + 3", "10 * 5", "100 / 4", "7 - 2", "3 * 3"]
    for expr in expressions:
        print(cached_compute(expr))

    # These should be cache hits
    print("\n--- Repeating (should be cached) ---")
    print(cached_compute("2 + 3"))
    print(cached_compute("10 * 5"))

    # Show dashboard
    print()
    print(cache_dashboard())

    # Add more to trigger eviction (cache only holds 5)
    print("\n--- Adding more (triggers LRU eviction) ---")
    print(cached_compute("99 + 1"))
    print(cached_compute("50 - 25"))

    # Check if oldest entries were evicted
    print("\n--- Checking evicted entries ---")
    print(cached_compute("100 / 4"))  # Was evicted, should be COMPUTED again

    # Final dashboard
    print()
    print(cache_dashboard())

    print("\nTo run as MCP server, uncomment mcp.run() below")
    # mcp.run()
