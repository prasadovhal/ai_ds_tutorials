"""
Exercise 2 Solution: Info Server
===================================
An MCP server that exposes system information as resources.
"""

# ============================================================
# STEP 1: Imports
# ============================================================
from mcp.server.fastmcp import FastMCP
import platform
import datetime
import sys

# ============================================================
# STEP 2: Create the server
# ============================================================
server = FastMCP("InfoServer")

# ============================================================
# STEP 3: Resource - Current Time
# ============================================================
@server.resource("info://time")
def get_current_time() -> str:
    """Get the current date, time, and timezone information."""

    # Get current time
    now = datetime.datetime.now()

    # Format it in multiple ways for usefulness
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_of_week = now.strftime("%A")
    iso_format = now.isoformat()

    info = f"""Current Date: {date_str}
Current Time: {time_str}
Day of Week: {day_of_week}
ISO Format: {iso_format}
Timestamp: {now.timestamp()}"""

    return info

# ============================================================
# STEP 4: Resource - Python Information
# ============================================================
@server.resource("info://python")
def get_python_info() -> str:
    """Get detailed Python version and environment information."""

    # Collect Python details
    version = platform.python_version()
    implementation = platform.python_implementation()
    compiler = platform.python_compiler()
    build_info = platform.python_build()

    # sys module gives us additional info
    executable_path = sys.executable
    prefix = sys.prefix

    info = f"""Python Version: {version}
Implementation: {implementation}
Compiler: {compiler}
Build Number: {build_info[0]}
Build Date: {build_info[1]}
Executable: {executable_path}
Install Prefix: {prefix}"""

    return info

# ============================================================
# STEP 5: Resource - Platform Information
# ============================================================
@server.resource("info://platform")
def get_platform_info() -> str:
    """Get operating system and hardware information."""

    # Collect platform details
    system_name = platform.system()
    node_name = platform.node()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()

    info = f"""Operating System: {system_name}
Computer Name: {node_name}
OS Release: {release}
OS Version: {version}
Machine Type: {machine}
Processor: {processor}"""

    return info

# ============================================================
# STEP 6: Run the server
# ============================================================
if __name__ == "__main__":
    server.run()
