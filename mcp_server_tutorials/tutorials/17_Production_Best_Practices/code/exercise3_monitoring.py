"""
Exercise 3 - Add Monitoring and Alerting
==========================================
TASK: Build an MCP server with monitoring and alerting.

You need to:
1. Track metrics for each tool call:
   - Total call count
   - Error count
   - Response times
2. Generate alerts when error rate exceeds a threshold
3. Create tools:
   - do_work(task): simulated work that sometimes fails
   - get_metrics(): shows all collected metrics
   - get_alerts(): shows any active alerts

Hint: Use time.time() to measure response times.
Hint: Store metrics in a module-level dictionary.
"""

from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Create metrics tracking system
# ============================================================

# TODO: Create a module-level metrics dict to track:
#   - call_count
#   - error_count
#   - total_response_time
#   - alerts list

# TODO: Create a function to record a metric
# TODO: Create a function to check alert conditions

# ============================================================
# Step 2: Create MCP server with monitored tools
# ============================================================

mcp = FastMCP("MonitoringServer")

# TODO: Create do_work(task) tool
# TODO: Create get_metrics() tool
# TODO: Create get_alerts() tool

# ============================================================
# Step 3: Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 3: Monitoring and Alerting Server")
    print("=" * 50)
    print("TODO: Implement the metrics system and tools above!")
    print("=" * 50)

    # TODO: Demo by calling do_work several times and checking metrics
    # mcp.run()
