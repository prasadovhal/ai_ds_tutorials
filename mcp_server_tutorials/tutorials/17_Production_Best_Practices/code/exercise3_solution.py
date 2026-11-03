"""
Exercise 3 Solution - MCP Server with Monitoring and Alerting
===============================================================
This server tracks call count, errors, and response times.
It generates alerts when the error rate exceeds a threshold.
"""

import time
import random
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 1: Metrics tracking system
# ============================================================

# Module-level metrics storage
_metrics = {
    "call_count": 0,
    "error_count": 0,
    "total_response_time": 0.0,
    "response_times": [],   # list of individual times
}

# Active alerts list
_alerts = []

# Alert threshold: generate alert if error rate exceeds this
ERROR_RATE_THRESHOLD = 0.3  # 30%


def record_call(elapsed: float, is_error: bool = False) -> None:
    """
    Record metrics for a tool call.
    Checks alert conditions after recording.
    """
    _metrics["call_count"] += 1
    _metrics["total_response_time"] += elapsed
    _metrics["response_times"].append(elapsed)

    if is_error:
        _metrics["error_count"] += 1

    # Check if we should generate an alert
    _check_alerts()


def _check_alerts() -> None:
    """
    Check if any alert conditions are met.
    Generates an alert if error rate exceeds the threshold.
    """
    count = _metrics["call_count"]
    if count < 3:
        # Need at least 3 calls before checking error rate
        return

    error_rate = _metrics["error_count"] / count

    if error_rate > ERROR_RATE_THRESHOLD:
        alert_msg = (
            f"HIGH ERROR RATE: {error_rate:.0%} "
            f"({_metrics['error_count']}/{count} calls failed) "
            f"at {time.strftime('%H:%M:%S')}"
        )
        # Avoid duplicate alerts for the same issue
        if not _alerts or _alerts[-1] != alert_msg:
            _alerts.append(alert_msg)


# ============================================================
# Step 2: MCP server with monitored tools
# ============================================================

mcp = FastMCP("MonitoringServer")


@mcp.tool()
def do_work(task: str) -> str:
    """
    Simulate doing some work. Sometimes fails randomly.
    All calls are tracked in the metrics system.
    """
    start = time.time()

    try:
        # Simulate work with random delay
        time.sleep(random.uniform(0.01, 0.1))

        # Simulate random failures (about 20% of the time)
        if random.random() < 0.2:
            raise RuntimeError(f"Task '{task}' failed unexpectedly")

        elapsed = time.time() - start
        record_call(elapsed, is_error=False)
        return f"Task '{task}' completed successfully in {elapsed*1000:.0f}ms"

    except RuntimeError as e:
        elapsed = time.time() - start
        record_call(elapsed, is_error=True)
        return f"ERROR: {e} (took {elapsed*1000:.0f}ms)"


@mcp.tool()
def get_metrics() -> str:
    """
    Get all collected metrics: call count, error count,
    average response time, and error rate.
    """
    count = _metrics["call_count"]

    if count == 0:
        return "No metrics collected yet. Call do_work() first."

    error_rate = _metrics["error_count"] / count
    avg_time = _metrics["total_response_time"] / count
    min_time = min(_metrics["response_times"])
    max_time = max(_metrics["response_times"])

    return (
        f"Server Metrics:\n"
        f"  Total calls:    {count}\n"
        f"  Errors:         {_metrics['error_count']}\n"
        f"  Error rate:     {error_rate:.1%}\n"
        f"  Avg response:   {avg_time*1000:.1f}ms\n"
        f"  Min response:   {min_time*1000:.1f}ms\n"
        f"  Max response:   {max_time*1000:.1f}ms\n"
        f"  Active alerts:  {len(_alerts)}"
    )


@mcp.tool()
def get_alerts() -> str:
    """
    Get all active alerts. Alerts are generated when
    the error rate exceeds the threshold.
    """
    if not _alerts:
        return "No active alerts. Everything is healthy!"

    lines = [f"Active Alerts ({len(_alerts)}):"]
    for i, alert in enumerate(_alerts, 1):
        lines.append(f"  [{i}] {alert}")

    lines.append(f"\nThreshold: error rate > {ERROR_RATE_THRESHOLD:.0%}")
    return "\n".join(lines)


# ============================================================
# Step 3: Demo and run
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 3 Solution: Monitoring & Alerting Server")
    print("=" * 50)

    # Demo: run several tasks
    print("\n--- Running tasks ---")
    tasks = [
        "process_data", "send_email", "generate_report",
        "update_cache", "sync_database", "validate_input",
        "compress_files", "send_notification", "run_backup",
        "cleanup_temp",
    ]

    for task in tasks:
        result = do_work(task)
        print(f"  {result}")

    # Show metrics
    print("\n--- Metrics ---")
    print(get_metrics())

    # Show alerts
    print("\n--- Alerts ---")
    print(get_alerts())

    print("\n" + "=" * 50)
    print("To run as MCP server, uncomment mcp.run() below")
    print("=" * 50)
    # mcp.run()
