"""
Exercise 1 - Build a Server with Progress Reporting
=====================================================
TASK: Build an MCP server that reports progress during long tasks.

You need to:
1. Create a FastMCP server
2. Add a long_task(steps) tool that:
   - Takes a number of steps to perform
   - Simulates work for each step (short sleep)
   - Collects progress updates as text
   - Returns the final result with all status updates
3. The tool should report what percentage is complete at each step

Hint: You can use time.sleep() to simulate work.
Hint: Build up a list of status messages and return them all at the end.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Create MCP server
# ============================================================

mcp = FastMCP("StreamingServer")

# ============================================================
# Step 2: Create the long_task tool
# ============================================================

# TODO: Create a long_task(steps) tool that:
#   - Loops through each step
#   - Simulates work with time.sleep(0.5)
#   - Tracks progress as percentage
#   - Returns all status updates as a single string

# ============================================================
# Step 3: Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 1: Server with Progress Reporting")
    print("=" * 50)
    print("TODO: Implement the long_task tool above!")
    print("It should simulate work and report progress.")
    print("=" * 50)

    # TODO: Demo by calling long_task(5)
    # mcp.run()
