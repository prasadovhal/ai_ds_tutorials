"""
Exercise 1 Solution - Server with Progress Reporting
======================================================
An MCP server with a long_task tool that simulates work
and reports progress as text status updates.
"""

import time
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Create MCP server
# ============================================================

mcp = FastMCP("ProgressServer")

# ============================================================
# Step 2: Long task tool with progress reporting
# ============================================================

@mcp.tool()
def long_task(steps: int = 5) -> str:
    """
    Simulate a long-running task with progress updates.
    Each step takes about 0.5 seconds.

    Args:
        steps: Number of steps to perform (default: 5).
    """
    if steps < 1:
        return "Error: steps must be at least 1."
    if steps > 20:
        return "Error: steps must be 20 or less (to avoid long waits)."

    # Collect status messages as we go
    status_lines = []
    status_lines.append(f"Starting task with {steps} steps...")

    start_time = time.time()

    for i in range(1, steps + 1):
        # Simulate work
        time.sleep(0.5)

        # Calculate progress
        percent = (i / steps) * 100
        elapsed = time.time() - start_time

        # Add status update
        status_lines.append(
            f"  Step {i}/{steps} ({percent:.0f}%) - "
            f"elapsed: {elapsed:.1f}s"
        )

    # Final summary
    total_time = time.time() - start_time
    status_lines.append(f"\nTask complete! {steps} steps in {total_time:.1f}s")

    # Return all status updates as a single string
    return "\n".join(status_lines)


@mcp.tool()
def quick_task(name: str) -> str:
    """
    A quick task for comparison -- returns immediately.
    """
    return f"Quick task '{name}' completed instantly!"


# ============================================================
# Step 3: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 1 Solution: Progress Reporting Server")
    print("=" * 50)

    # Demo the long task
    print("\n--- Long Task (5 steps) ---")
    print(long_task(5))

    # Demo quick task for comparison
    print("\n--- Quick Task ---")
    print(quick_task("hello"))

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
