"""
Mini Project - Production Pipeline
====================================
A complete MCP server demonstrating production best practices:
- Tool functions with caching
- Inline unit tests (run with --test flag)
- Metrics collection
- CI config generation
- Health check tool

Usage:
  python mini_project_production_pipeline.py           # Run as MCP server
  python mini_project_production_pipeline.py --test    # Run unit tests
  python mini_project_production_pipeline.py --ci      # Generate CI config
"""

import sys
import time
import os
from mcp.server.fastmcp import FastMCP

# ============================================================
# Section 1: Cache System
# ============================================================

# Cache storage: { key: {"value": ..., "timestamp": ...} }
_cache = {}
_cache_stats = {"hits": 0, "misses": 0}


def cache_set(key: str, value: str) -> None:
    """Store a value in cache with current timestamp."""
    _cache[key] = {"value": value, "timestamp": time.time()}


def cache_get(key: str, ttl: int = 60) -> str | None:
    """Get a cached value if it exists and hasn't expired."""
    if key not in _cache:
        _cache_stats["misses"] += 1
        return None

    entry = _cache[key]
    if time.time() - entry["timestamp"] > ttl:
        del _cache[key]
        _cache_stats["misses"] += 1
        return None

    _cache_stats["hits"] += 1
    return entry["value"]


def cache_clear() -> int:
    """Clear the cache. Returns number of entries removed."""
    count = len(_cache)
    _cache.clear()
    return count


# ============================================================
# Section 2: Metrics System
# ============================================================

# Metrics storage
_metrics = {
    "calls": {},       # { tool_name: count }
    "errors": {},      # { tool_name: count }
    "times": {},       # { tool_name: [elapsed_seconds] }
    "start_time": time.time(),
}


def record_metric(tool_name: str, elapsed: float, is_error: bool = False) -> None:
    """Record a metric for a tool call."""
    # Increment call count
    _metrics["calls"][tool_name] = _metrics["calls"].get(tool_name, 0) + 1

    # Record response time
    if tool_name not in _metrics["times"]:
        _metrics["times"][tool_name] = []
    _metrics["times"][tool_name].append(elapsed)

    # Record error if applicable
    if is_error:
        _metrics["errors"][tool_name] = _metrics["errors"].get(tool_name, 0) + 1


# ============================================================
# Section 3: Tool Functions (testable without MCP)
# ============================================================

def calculate(operation: str, a: float, b: float) -> float:
    """Perform a calculation. Supports add, subtract, multiply, divide."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")


def format_number(value: float) -> str:
    """Format a number nicely (remove trailing zeros)."""
    if value == int(value):
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


# ============================================================
# Section 4: MCP Server with Cached Tools
# ============================================================

mcp = FastMCP("ProductionPipeline")


@mcp.tool()
def calc(operation: str, a: float, b: float) -> str:
    """
    Perform a calculation with caching and metrics.
    Supports: add, subtract, multiply, divide.
    """
    start = time.time()
    cache_key = f"calc_{operation}_{a}_{b}"

    try:
        # Check cache
        cached = cache_get(cache_key, ttl=300)
        if cached is not None:
            record_metric("calc", time.time() - start)
            return f"[CACHED] {cached}"

        # Compute
        result = calculate(operation, a, b)
        formatted = f"{a} {operation} {b} = {format_number(result)}"

        # Cache the result
        cache_set(cache_key, formatted)
        record_metric("calc", time.time() - start)
        return f"[COMPUTED] {formatted}"

    except ValueError as e:
        record_metric("calc", time.time() - start, is_error=True)
        return f"Error: {e}"


@mcp.tool()
def health_check() -> str:
    """
    Check server health. Reports uptime, cache status, and metrics.
    """
    uptime = time.time() - _metrics["start_time"]
    total_calls = sum(_metrics["calls"].values())
    total_errors = sum(_metrics["errors"].values())
    error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0.0

    # Determine health status
    if error_rate > 50:
        status = "UNHEALTHY"
    elif error_rate > 20:
        status = "DEGRADED"
    else:
        status = "HEALTHY"

    return (
        f"Health Check: {status}\n"
        f"  Uptime:      {uptime:.0f}s\n"
        f"  Total calls: {total_calls}\n"
        f"  Errors:      {total_errors}\n"
        f"  Error rate:  {error_rate:.1f}%\n"
        f"  Cache size:  {len(_cache)} entries\n"
        f"  Cache hits:  {_cache_stats['hits']}\n"
        f"  Cache misses:{_cache_stats['misses']}"
    )


@mcp.tool()
def get_dashboard() -> str:
    """
    Get a full dashboard showing metrics per tool.
    """
    if not _metrics["calls"]:
        return "No metrics yet. Call some tools first!"

    lines = ["Dashboard:", "=" * 40]

    for tool_name in sorted(_metrics["calls"].keys()):
        calls = _metrics["calls"][tool_name]
        errors = _metrics["errors"].get(tool_name, 0)
        times = _metrics["times"].get(tool_name, [])
        avg_time = sum(times) / len(times) if times else 0

        lines.append(f"\n  {tool_name}:")
        lines.append(f"    Calls:     {calls}")
        lines.append(f"    Errors:    {errors}")
        lines.append(f"    Avg time:  {avg_time*1000:.1f}ms")

    lines.append("\n" + "=" * 40)
    return "\n".join(lines)


# ============================================================
# Section 5: Inline Unit Tests
# ============================================================

def run_tests() -> bool:
    """Run all unit tests. Returns True if all pass."""
    print("Running unit tests...")
    passed = 0
    failed = 0

    # ---- Test calculate() ----
    tests = [
        ("add basic", lambda: calculate("add", 2, 3) == 5),
        ("add zero", lambda: calculate("add", 0, 0) == 0),
        ("subtract", lambda: calculate("subtract", 10, 3) == 7),
        ("multiply", lambda: calculate("multiply", 4, 5) == 20),
        ("multiply zero", lambda: calculate("multiply", 0, 99) == 0),
        ("divide", lambda: calculate("divide", 10, 2) == 5.0),
        ("divide float", lambda: calculate("divide", 7, 2) == 3.5),
    ]

    for name, test_fn in tests:
        try:
            assert test_fn(), f"{name} returned wrong value"
            print(f"  PASS: {name}")
            passed += 1
        except (AssertionError, Exception) as e:
            print(f"  FAIL: {name} - {e}")
            failed += 1

    # Test divide by zero
    try:
        calculate("divide", 1, 0)
        print("  FAIL: divide_by_zero - no exception raised")
        failed += 1
    except ValueError:
        print("  PASS: divide_by_zero")
        passed += 1

    # Test unknown operation
    try:
        calculate("modulus", 1, 1)
        print("  FAIL: unknown_op - no exception raised")
        failed += 1
    except ValueError:
        print("  PASS: unknown_op")
        passed += 1

    # ---- Test format_number() ----
    fmt_tests = [
        ("format int", lambda: format_number(5.0) == "5"),
        ("format float", lambda: format_number(3.14) == "3.14"),
        ("format zero", lambda: format_number(0.0) == "0"),
    ]

    for name, test_fn in fmt_tests:
        try:
            assert test_fn(), f"{name} returned wrong value"
            print(f"  PASS: {name}")
            passed += 1
        except (AssertionError, Exception) as e:
            print(f"  FAIL: {name} - {e}")
            failed += 1

    # ---- Test cache system ----
    cache_clear()
    _cache_stats["hits"] = 0
    _cache_stats["misses"] = 0

    cache_set("test_key", "test_value")
    assert cache_get("test_key", ttl=60) == "test_value"
    print("  PASS: cache_set_get")
    passed += 1

    assert cache_get("nonexistent", ttl=60) is None
    print("  PASS: cache_miss")
    passed += 1

    cache_clear()

    # Summary
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


# ============================================================
# Section 6: CI Config Generator
# ============================================================

def generate_ci_config() -> str:
    """Generate GitHub Actions CI config as a YAML string."""
    return """\
name: MCP Production Pipeline CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install mcp
      - name: Run unit tests
        run: python mini_project_production_pipeline.py --test
"""


# ============================================================
# Section 7: Entry point
# ============================================================

if __name__ == "__main__":
    if "--test" in sys.argv:
        # Run unit tests
        print("=" * 50)
        print("Production Pipeline - Unit Tests")
        print("=" * 50)
        success = run_tests()
        print("=" * 50)
        sys.exit(0 if success else 1)

    elif "--ci" in sys.argv:
        # Generate CI config
        print("=" * 50)
        print("Production Pipeline - CI Config Generator")
        print("=" * 50)
        config = generate_ci_config()
        print(config)

        # Save to file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "ci_config.yml")
        with open(output_path, "w") as f:
            f.write(config)
        print(f"Saved to: {output_path}")
        print("=" * 50)

    else:
        # Run as MCP server
        print("Production Pipeline MCP Server")
        print("  Use --test to run unit tests")
        print("  Use --ci to generate CI config")
        print("  Starting MCP server...")
        mcp.run()
