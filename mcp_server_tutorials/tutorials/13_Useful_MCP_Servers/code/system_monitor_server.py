"""
System Monitor MCP Server
==========================
Provides tools to get system information like CPU, memory, disk, and platform.
Uses only standard library modules: os, platform, shutil.
"""

# Import FastMCP and system modules
from mcp.server.fastmcp import FastMCP
import os
import platform
import shutil

# Create the MCP server instance
server = FastMCP("System Monitor Server")


# --- Tool: Get CPU information ---
@server.tool()
def cpu_info() -> str:
    """Get CPU information for this system."""
    info = f"""
CPU Information:
  Processor: {platform.processor() or 'Unknown'}
  Architecture: {platform.machine()}
  CPU Count (logical): {os.cpu_count()}
  Platform: {platform.platform()}
"""
    return info.strip()


# --- Tool: Get memory information ---
@server.tool()
def memory_info() -> str:
    """
    Get basic memory info. Uses os module for portable info.
    Note: Detailed memory stats require psutil (not included).
    """
    info = "Memory Information:\n"

    # Try to get memory info from different OS methods
    try:
        # Works on many systems
        if hasattr(os, "sysconf"):
            # Linux/Unix systems
            page_size = os.sysconf("SC_PAGE_SIZE")
            total_pages = os.sysconf("SC_PHYS_PAGES")
            total_mem = page_size * total_pages
            total_gb = total_mem / (1024 ** 3)
            info += f"  Total Physical Memory: {total_gb:.2f} GB\n"
        else:
            info += "  Note: Detailed memory info requires the psutil package.\n"
            info += "  Install with: pip install psutil\n"
    except (ValueError, OSError):
        info += "  Could not retrieve memory information on this platform.\n"

    # Show the current process working set (approximate)
    info += f"  Python Process ID: {os.getpid()}\n"

    return info.strip()


# --- Tool: Get disk information ---
@server.tool()
def disk_info(path: str = "/") -> str:
    """Get disk usage information for a given path (default: root)."""
    try:
        # shutil.disk_usage works on all platforms
        usage = shutil.disk_usage(path)

        # Convert bytes to GB
        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        percent_used = (usage.used / usage.total) * 100

        info = f"""
Disk Usage for '{path}':
  Total: {total_gb:.2f} GB
  Used:  {used_gb:.2f} GB ({percent_used:.1f}%)
  Free:  {free_gb:.2f} GB ({100 - percent_used:.1f}%)
"""
        return info.strip()

    except FileNotFoundError:
        return f"Error: Path '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied for '{path}'."


# --- Tool: Get platform information ---
@server.tool()
def platform_info() -> str:
    """Get detailed platform and OS information."""
    info = f"""
Platform Information:
  System: {platform.system()}
  Release: {platform.release()}
  Version: {platform.version()}
  Machine: {platform.machine()}
  Processor: {platform.processor() or 'Unknown'}
  Python Version: {platform.python_version()}
  Python Implementation: {platform.python_implementation()}
  Platform: {platform.platform()}
  Node (Hostname): {platform.node()}
"""
    return info.strip()


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
