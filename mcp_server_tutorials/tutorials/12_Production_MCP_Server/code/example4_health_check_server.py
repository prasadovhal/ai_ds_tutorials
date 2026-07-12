"""
Example 4: MCP Server with Health Check and Version Info
=========================================================
This example shows how to add health checking and version
information to your MCP server.

In production, health checks are used to:
- Monitor if the server is running and responsive
- Check server uptime and memory usage
- Verify that the server is healthy before sending traffic

Version info helps you:
- Know which version is deployed in production
- Track compatibility between clients and servers
- Debug issues by knowing the exact server version

Poetry setup:
    poetry init --name example4-health-check --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Set up logging
# ============================================================

logger = logging.getLogger("mcp_health")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# ============================================================
# STEP 2: Define server metadata
# ============================================================

# Version information -- update these when you release new versions
SERVER_VERSION = "1.0.0"
SERVER_BUILD_DATE = "2025-01-15"
SERVER_DESCRIPTION = "Production MCP Server with Health Checks"

# Record when the server started (used for uptime calculation)
SERVER_START_TIME = time.time()
SERVER_START_DATETIME = datetime.now().isoformat()

# ============================================================
# STEP 3: Create the MCP server
# ============================================================

server = FastMCP("health-check-server")

logger.info(f"Server v{SERVER_VERSION} initialized")

# ============================================================
# STEP 4: Define the health check tool
# ============================================================


@server.tool()
def health_check() -> str:
    """
    Check server health and return status information.

    Returns:
    - Status: healthy or unhealthy
    - Uptime: how long the server has been running
    - Memory: current memory usage (approximate)
    - Python version
    - Server version
    """

    logger.info("Health check requested")

    # Calculate uptime
    uptime_seconds = time.time() - SERVER_START_TIME
    uptime_hours = uptime_seconds / 3600
    uptime_minutes = (uptime_seconds % 3600) / 60

    # Get memory usage (approximate, using os module)
    # Note: This is a simple approach. In production, use psutil for accurate memory info.
    try:
        # Try to get process memory (works on Linux/Mac)
        import resource
        memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except ImportError:
        # On Windows, resource module is not available
        # Use a simple approximation
        memory_mb = sys.getsizeof(globals()) / (1024 * 1024)

    # Determine health status
    # In a real server, you would check database connections,
    # disk space, memory limits, etc.
    status = "healthy"
    checks = []

    # Check 1: Uptime (server should have started)
    if uptime_seconds > 0:
        checks.append("uptime: OK")
    else:
        checks.append("uptime: FAIL")
        status = "unhealthy"

    # Check 2: Memory (should be under 500MB)
    if memory_mb < 500:
        checks.append(f"memory: OK ({memory_mb:.1f} MB)")
    else:
        checks.append(f"memory: WARNING ({memory_mb:.1f} MB)")
        status = "degraded"

    # Build the health report
    report = f"Health Check Report\n"
    report = report + f"{'=' * 35}\n"
    report = report + f"Status:       {status.upper()}\n"
    report = report + f"Server:       {SERVER_DESCRIPTION}\n"
    report = report + f"Version:      {SERVER_VERSION}\n"
    report = report + f"Started:      {SERVER_START_DATETIME}\n"
    report = report + f"Uptime:       {int(uptime_hours)}h {int(uptime_minutes)}m {int(uptime_seconds % 60)}s\n"
    report = report + f"Memory:       ~{memory_mb:.1f} MB\n"
    report = report + f"Python:       {sys.version.split()[0]}\n"
    report = report + f"PID:          {os.getpid()}\n"
    report = report + f"\nHealth Checks:\n"
    for check in checks:
        report = report + f"  - {check}\n"

    logger.info(f"Health check result: {status}")

    return report


# ============================================================
# STEP 5: Define the version info tool
# ============================================================


@server.tool()
def server_version() -> str:
    """
    Return detailed server version information.

    Useful for debugging and ensuring clients connect
    to the correct server version.
    """

    logger.info("Version info requested")

    version_info = f"Server Version Information\n"
    version_info = version_info + f"{'=' * 35}\n"
    version_info = version_info + f"Name:         health-check-server\n"
    version_info = version_info + f"Version:      {SERVER_VERSION}\n"
    version_info = version_info + f"Build date:   {SERVER_BUILD_DATE}\n"
    version_info = version_info + f"Description:  {SERVER_DESCRIPTION}\n"
    version_info = version_info + f"Python:       {sys.version.split()[0]}\n"
    version_info = version_info + f"Platform:     {sys.platform}\n"

    return version_info


# ============================================================
# STEP 6: Define a simple business tool
# ============================================================


@server.tool()
def greet(name: str) -> str:
    """Greet someone by name. A simple tool to test the server."""

    logger.info(f"Greeting '{name}'")
    return f"Hello, {name}! Server v{SERVER_VERSION} is running."


# ============================================================
# STEP 7: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info(f"Starting server v{SERVER_VERSION}...")
    logger.info(f"Use 'health_check' tool to monitor server health")
    logger.info(f"Use 'server_version' tool to see version info")
    server.run(transport="stdio")
