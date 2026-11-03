"""
Example 2: Dynamic Resources
==============================
This example shows dynamic resources -- resources whose content changes
each time they are read. Unlike static resources, dynamic resources compute
their content at read time.

Think of dynamic resources like a clock on the wall -- every time you look
at it, it shows a different time.

How to run:
    python example2_dynamic_resources.py

How to test:
    npx @modelcontextprotocol/inspector python example2_dynamic_resources.py
"""

# ============================================================
# Step 1: Import Everything We Need
# ============================================================
from mcp.server.fastmcp import FastMCP
import json
import random
import platform
from datetime import datetime

# ============================================================
# Step 2: Create the MCP Server
# ============================================================
server = FastMCP("Dynamic Resources Demo")

# ============================================================
# Step 3: Define Some Data for Our Dynamic Resources
# ============================================================
# This list of quotes will be used by the random quote resource.
# The resource picks a different quote each time it is read.
QUOTES = [
    "The best way to predict the future is to invent it. - Alan Kay",
    "Talk is cheap. Show me the code. - Linus Torvalds",
    "Any sufficiently advanced technology is indistinguishable from magic. - Arthur C. Clarke",
    "First, solve the problem. Then, write the code. - John Johnson",
    "Code is like humor. When you have to explain it, it is bad. - Cory House",
    "Simplicity is the soul of efficiency. - Austin Freeman",
    "Make it work, make it right, make it fast. - Kent Beck",
    "Programming is not about typing, it is about thinking. - Rich Hickey",
    "The most dangerous phrase in the language is: We have always done it this way. - Grace Hopper",
    "Premature optimization is the root of all evil. - Donald Knuth"
]

# This counter tracks how many times resources have been read.
# It demonstrates that dynamic resources can maintain state.
read_counter = {"count": 0}


# ============================================================
# Step 4: Current Time Resource
# ============================================================
# This resource returns the current date and time.
# Every time you read it, you get a different result because
# time keeps moving forward.
@server.resource("data://time/current")
def get_current_time():
    """Return the current date and time."""

    # Get the current time
    now = datetime.now()

    # Format it as a readable string
    time_info = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timestamp": now.isoformat(),
        "timezone": "local"
    }

    return json.dumps(time_info, indent=2)


# ============================================================
# Step 5: Random Quote Resource
# ============================================================
# This resource picks a random quote from our list.
# Each read will likely return a different quote.
@server.resource("data://quotes/random")
def get_random_quote():
    """Return a random inspirational quote about programming."""

    # Pick a random quote from the list
    quote = random.choice(QUOTES)

    # Also include metadata about the selection
    result = {
        "quote": quote,
        "total_quotes_available": len(QUOTES),
        "generated_at": datetime.now().isoformat()
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 6: System Information Resource
# ============================================================
# This resource returns current system information.
# Some parts are static (like OS name) but others change
# (like the current time the info was gathered).
@server.resource("data://system/info")
def get_system_info():
    """Return current system information."""

    system_info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "gathered_at": datetime.now().isoformat()
    }

    return json.dumps(system_info, indent=2)


# ============================================================
# Step 7: Read Counter Resource
# ============================================================
# This resource tracks how many times ANY resource has been read.
# It demonstrates that dynamic resources can maintain state
# across multiple reads.
@server.resource("data://server/read-count")
def get_read_count():
    """Return how many times this resource has been read."""

    # Increment the counter each time this resource is read
    read_counter["count"] = read_counter["count"] + 1

    result = {
        "total_reads": read_counter["count"],
        "message": "This counter increases each time you read this resource.",
        "read_at": datetime.now().isoformat()
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 8: Random Number Resource
# ============================================================
# This resource generates a random number with some statistics.
# Each read produces a different random number.
@server.resource("data://random/number")
def get_random_number():
    """Return a random number between 1 and 100."""

    # Generate a random number
    number = random.randint(1, 100)

    result = {
        "number": number,
        "is_even": number % 2 == 0,
        "is_prime": all(number % i != 0 for i in range(2, int(number**0.5) + 1)) and number > 1,
        "generated_at": datetime.now().isoformat()
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 9: Run the Server
# ============================================================
if __name__ == "__main__":
    # Start the server -- dynamic resources are computed on each read
    server.run()
