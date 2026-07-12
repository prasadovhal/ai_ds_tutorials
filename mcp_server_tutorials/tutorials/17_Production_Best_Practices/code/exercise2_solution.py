"""
Exercise 2 Solution - MCP Server with Cached Weather Tool
===========================================================
This server caches weather lookups for 60 seconds,
provides cache status, and allows clearing the cache.
"""

import time
import random
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Cache system
# ============================================================

# Cache storage: { key: {"value": ..., "timestamp": ...} }
_cache = {}

# Cache statistics
_stats = {"hits": 0, "misses": 0}


def set_cache(key: str, value: str) -> None:
    """Store a value in the cache with current timestamp."""
    _cache[key] = {
        "value": value,
        "timestamp": time.time(),
    }


def get_cache(key: str, ttl: int = 60) -> str | None:
    """
    Get a cached value if it exists and hasn't expired.
    Returns None if missing or expired.
    """
    if key not in _cache:
        _stats["misses"] += 1
        return None

    entry = _cache[key]
    age = time.time() - entry["timestamp"]

    if age > ttl:
        # Expired -- remove it
        del _cache[key]
        _stats["misses"] += 1
        return None

    # Cache hit
    _stats["hits"] += 1
    return entry["value"]


# ============================================================
# Step 2: Simulated weather data
# ============================================================

def _simulate_weather(city: str) -> str:
    """
    Simulate fetching weather data for a city.
    Returns a random weather description.
    """
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Windy", "Snowy"]
    temp = random.randint(-10, 40)
    condition = random.choice(conditions)
    return f"{city}: {condition}, {temp}C"


# ============================================================
# Step 3: MCP server with cached tools
# ============================================================

mcp = FastMCP("CachedWeatherServer")


@mcp.tool()
def get_weather(city: str) -> str:
    """
    Get weather for a city. Results are cached for 60 seconds.
    Uses simulated data (no real API).
    """
    cache_key = f"weather_{city.lower()}"

    # Check cache first (60 second TTL)
    cached = get_cache(cache_key, ttl=60)
    if cached is not None:
        return f"[CACHED] {cached}"

    # Cache miss -- fetch fresh data
    weather = _simulate_weather(city)
    set_cache(cache_key, weather)
    return f"[FRESH] {weather}"


@mcp.tool()
def cache_status() -> str:
    """
    Show current cache statistics.
    Includes hit/miss counts and number of cached entries.
    """
    total = _stats["hits"] + _stats["misses"]
    hit_rate = (_stats["hits"] / total * 100) if total > 0 else 0.0

    lines = [
        "Cache Status:",
        f"  Hits:     {_stats['hits']}",
        f"  Misses:   {_stats['misses']}",
        f"  Hit Rate: {hit_rate:.1f}%",
        f"  Entries:  {len(_cache)}",
        "",
        "Cached cities:",
    ]

    # List cached entries with their age
    for key, entry in _cache.items():
        age = time.time() - entry["timestamp"]
        city = key.replace("weather_", "")
        lines.append(f"  {city}: {age:.0f}s old")

    if not _cache:
        lines.append("  (none)")

    return "\n".join(lines)


@mcp.tool()
def clear_cache() -> str:
    """
    Clear all cached weather data and reset statistics.
    """
    count = len(_cache)
    _cache.clear()
    _stats["hits"] = 0
    _stats["misses"] = 0
    return f"Cache cleared! Removed {count} entries. Stats reset."


# ============================================================
# Step 4: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 2 Solution: Cached Weather Server")
    print("=" * 50)

    # Demo the caching behavior
    print("\n--- Demo ---")
    print(get_weather("London"))       # FRESH
    print(get_weather("London"))       # CACHED
    print(get_weather("Paris"))        # FRESH
    print(get_weather("Paris"))        # CACHED
    print()
    print(cache_status())
    print()
    print(clear_cache())
    print()
    print(cache_status())

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
