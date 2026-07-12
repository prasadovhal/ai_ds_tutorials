"""
Datetime MCP Server
===================
Provides tools for date and time operations:
current time, timezone conversion, days between dates, and date arithmetic.
"""

# Import FastMCP and datetime modules
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta, timezone

# Create the MCP server instance
server = FastMCP("Datetime Server")

# Common timezone offsets (UTC offset in hours)
TIMEZONE_OFFSETS = {
    "UTC": 0, "GMT": 0,
    "EST": -5, "EDT": -4,
    "CST": -6, "CDT": -5,
    "MST": -7, "MDT": -6,
    "PST": -8, "PDT": -7,
    "IST": 5.5,
    "CET": 1, "CEST": 2,
    "JST": 9,
    "AEST": 10, "AEDT": 11,
    "CST_CHINA": 8,
    "KST": 9,
}


# --- Tool: Get current time ---
@server.tool()
def current_time() -> str:
    """Get the current date and time in UTC and local time."""
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()

    return f"""
Current Time:
  UTC:   {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}
  Local: {now_local.strftime('%Y-%m-%d %H:%M:%S')}
  Date:  {now_local.strftime('%A, %B %d, %Y')}
  Week:  {now_local.strftime('Week %W of %Y')}
""".strip()


# --- Tool: Get time in a specific timezone ---
@server.tool()
def time_in_timezone(tz: str) -> str:
    """
    Get the current time in a specific timezone.
    Supported: UTC, GMT, EST, EDT, CST, CDT, MST, MDT, PST, PDT,
    IST, CET, CEST, JST, AEST, AEDT, CST_CHINA, KST.
    """
    tz_upper = tz.upper()

    if tz_upper not in TIMEZONE_OFFSETS:
        available = ", ".join(sorted(TIMEZONE_OFFSETS.keys()))
        return f"Unknown timezone '{tz}'. Available: {available}"

    # Calculate the offset
    offset_hours = TIMEZONE_OFFSETS[tz_upper]
    tz_obj = timezone(timedelta(hours=offset_hours))

    # Get current time in that timezone
    now = datetime.now(tz_obj)

    return f"Current time in {tz_upper} (UTC{offset_hours:+.1f}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


# --- Tool: Calculate days between two dates ---
@server.tool()
def days_between(date1: str, date2: str) -> str:
    """
    Calculate the number of days between two dates.
    Date format: YYYY-MM-DD (e.g., '2024-01-15').
    """
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
    except ValueError:
        return f"Error: '{date1}' is not a valid date. Use YYYY-MM-DD format."

    try:
        d2 = datetime.strptime(date2, "%Y-%m-%d")
    except ValueError:
        return f"Error: '{date2}' is not a valid date. Use YYYY-MM-DD format."

    # Calculate the difference
    delta = abs((d2 - d1).days)

    return f"Days between {date1} and {date2}: {delta} days"


# --- Tool: Add days to a date ---
@server.tool()
def add_days(date: str, n: int) -> str:
    """
    Add (or subtract) days from a date.
    Date format: YYYY-MM-DD. Use negative n to subtract days.
    """
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return f"Error: '{date}' is not a valid date. Use YYYY-MM-DD format."

    # Add the days
    result = d + timedelta(days=n)

    direction = "Adding" if n >= 0 else "Subtracting"
    return f"{direction} {abs(n)} days to {date}: {result.strftime('%Y-%m-%d')} ({result.strftime('%A')})"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
