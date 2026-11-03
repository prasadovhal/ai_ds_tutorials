"""
Exercise 2 - Add Caching to an Existing Server
================================================
TASK: Build an MCP server with caching for a weather tool.

You need to:
1. Create a cache system (dict with timestamps)
2. Create a FastMCP server with these tools:
   - get_weather(city): returns weather (cached for 60 seconds)
   - cache_status(): shows cache hits, misses, and entries
   - clear_cache(): clears all cached data
3. Use simulated weather data (no real API needed)

Hint: Look at example3_caching.py for the caching pattern.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Create cache system
# ============================================================

# TODO: Create a module-level cache dict
# TODO: Create set_cache(key, value) function
# TODO: Create get_cache(key, ttl) function

# ============================================================
# Step 2: Create MCP server with cached weather tool
# ============================================================

mcp = FastMCP("CachedWeatherServer")

# TODO: Create get_weather(city) tool that uses caching
# TODO: Create cache_status() tool
# TODO: Create clear_cache() tool

# ============================================================
# Step 3: Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 2: Cached Weather Server")
    print("=" * 50)
    print("TODO: Implement the cache and tools above!")
    print("Then test by calling get_weather multiple times.")
    print("=" * 50)

    # TODO: Add a demo that shows caching in action
    # mcp.run()
