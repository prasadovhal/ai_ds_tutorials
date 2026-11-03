"""
Example 4 - Performance Measurement
=====================================
This script measures execution time of functions
to compare cached vs uncached performance.
"""

import time

# ============================================================
# Step 1: Simple cache for performance testing
# ============================================================

# In-memory cache
_perf_cache = {}


def cached_compute(n: int) -> int:
    """
    Compute the sum of 1..n with caching.
    First call is slow (simulated), subsequent calls are instant.
    """
    if n in _perf_cache:
        return _perf_cache[n]

    # Simulate slow computation
    time.sleep(0.1)
    result = sum(range(1, n + 1))
    _perf_cache[n] = result
    return result


def uncached_compute(n: int) -> int:
    """
    Compute the sum of 1..n WITHOUT caching.
    Always slow (simulated).
    """
    time.sleep(0.1)
    return sum(range(1, n + 1))


# ============================================================
# Step 2: Timing utility
# ============================================================

def measure_time(func, *args):
    """
    Measure how long a function takes to execute.
    Returns (result, elapsed_seconds).
    """
    start = time.time()
    result = func(*args)
    elapsed = time.time() - start
    return result, elapsed


# ============================================================
# Step 3: Run benchmarks and print results
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Performance Comparison: Cached vs Uncached")
    print("=" * 60)

    # Test values
    test_values = [10, 50, 100, 10, 50, 100]

    # ---- Benchmark uncached ----
    print("\n--- Uncached Performance ---")
    print(f"{'Call':<10} {'Input':<10} {'Result':<15} {'Time (ms)':<10}")
    print("-" * 45)

    uncached_total = 0.0
    for i, n in enumerate(test_values, 1):
        result, elapsed = measure_time(uncached_compute, n)
        uncached_total += elapsed
        print(f"#{i:<9} {n:<10} {result:<15} {elapsed*1000:.1f}")

    print(f"{'TOTAL':<10} {'':<10} {'':<15} {uncached_total*1000:.1f}")

    # Clear cache before cached test
    _perf_cache.clear()

    # ---- Benchmark cached ----
    print("\n--- Cached Performance ---")
    print(f"{'Call':<10} {'Input':<10} {'Result':<15} {'Time (ms)':<10}")
    print("-" * 45)

    cached_total = 0.0
    for i, n in enumerate(test_values, 1):
        result, elapsed = measure_time(cached_compute, n)
        cached_total += elapsed
        print(f"#{i:<9} {n:<10} {result:<15} {elapsed*1000:.1f}")

    print(f"{'TOTAL':<10} {'':<10} {'':<15} {cached_total*1000:.1f}")

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Uncached total: {uncached_total*1000:.1f} ms")
    print(f"  Cached total:   {cached_total*1000:.1f} ms")
    if uncached_total > 0:
        speedup = uncached_total / cached_total if cached_total > 0 else float("inf")
        print(f"  Speedup:        {speedup:.1f}x faster with cache")
    print(f"\nNote: First 3 cached calls are cache misses (slow).")
    print(f"      Last 3 cached calls are cache hits (fast).")
    print("=" * 60)
