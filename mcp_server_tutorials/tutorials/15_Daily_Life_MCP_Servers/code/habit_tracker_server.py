"""
Habit Tracker MCP Server
==========================
Track daily habits and build streaks.

Tools:
  - add_habit(name)
  - log_habit(name)
  - get_streaks()
  - weekly_report()

Data is stored in habits.json with date tracking for streaks.
"""

import json
import os
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Habit Tracker")

# Path to the JSON data file
DATA_FILE = "habits.json"


def load_data():
    """Load habit data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default structure: dict of habits, each with a list of completion dates
    return {"habits": {}}


def save_data(data):
    """Save habit data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Tool: add_habit ---
@mcp.tool()
def add_habit(name: str) -> str:
    """Add a new habit to track.

    Args:
        name: Name of the habit (e.g., 'Exercise', 'Read', 'Meditate')
    """
    data = load_data()

    # Check if habit already exists
    if name.lower() in [h.lower() for h in data["habits"]]:
        return f"Habit '{name}' already exists!"

    # Add the habit with empty completion dates
    data["habits"][name] = {
        "created": datetime.now().strftime("%Y-%m-%d"),
        "dates": []  # List of dates when the habit was completed
    }

    save_data(data)
    return f"Habit '{name}' added! Use log_habit to record completions."


# --- Tool: log_habit ---
@mcp.tool()
def log_habit(name: str) -> str:
    """Log that a habit was completed today.

    Args:
        name: Name of the habit to log
    """
    data = load_data()

    # Find the habit (case-insensitive)
    habit_key = None
    for h in data["habits"]:
        if h.lower() == name.lower():
            habit_key = h
            break

    if habit_key is None:
        return f"Habit '{name}' not found. Use add_habit first."

    today = datetime.now().strftime("%Y-%m-%d")

    # Check if already logged today
    if today in data["habits"][habit_key]["dates"]:
        return f"'{habit_key}' already logged for today ({today})!"

    # Add today's date
    data["habits"][habit_key]["dates"].append(today)
    save_data(data)

    # Calculate current streak
    streak = _calculate_streak(data["habits"][habit_key]["dates"])

    return f"'{habit_key}' logged for {today}! Current streak: {streak} day(s)"


def _calculate_streak(dates):
    """Calculate the current streak (consecutive days including today)."""
    if not dates:
        return 0

    # Sort dates and work backwards from today
    sorted_dates = sorted(dates, reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if the most recent date is today or yesterday
    if sorted_dates[0] != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if sorted_dates[0] != yesterday:
            return 0  # Streak is broken

    streak = 1
    for i in range(1, len(sorted_dates)):
        # Parse the current and previous dates
        current = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
        previous = datetime.strptime(sorted_dates[i], "%Y-%m-%d")

        # Check if they are consecutive days
        if (current - previous).days == 1:
            streak += 1
        else:
            break  # Streak is broken

    return streak


# --- Tool: get_streaks ---
@mcp.tool()
def get_streaks() -> str:
    """Show current streaks for all habits."""
    data = load_data()

    if not data["habits"]:
        return "No habits being tracked. Use add_habit to start!"

    lines = ["Current Streaks:", ""]

    for name, habit in data["habits"].items():
        streak = _calculate_streak(habit["dates"])
        total = len(habit["dates"])

        # Add a visual indicator based on streak length
        if streak >= 7:
            status = "AMAZING"
        elif streak >= 3:
            status = "Good"
        elif streak >= 1:
            status = "Active"
        else:
            status = "Inactive"

        lines.append(f"  {name}: {streak} day streak ({total} total) [{status}]")

    return "\n".join(lines)


# --- Tool: weekly_report ---
@mcp.tool()
def weekly_report() -> str:
    """Generate a report of habit completion for the past 7 days."""
    data = load_data()

    if not data["habits"]:
        return "No habits being tracked."

    # Generate the past 7 days
    today = datetime.now()
    week_dates = []
    for i in range(6, -1, -1):  # 6 days ago through today
        day = today - timedelta(days=i)
        week_dates.append(day.strftime("%Y-%m-%d"))

    lines = ["Weekly Habit Report:", ""]

    # Header row with abbreviated day names
    day_names = []
    for d in week_dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        day_names.append(dt.strftime("%a"))

    lines.append(f"  {'Habit':<15} " + " ".join(f"{d:>3}" for d in day_names))
    lines.append(f"  {'-' * 15} " + " ".join("---" for _ in day_names))

    # Each habit's completion status
    total_completions = 0
    total_possible = 0

    for name, habit in data["habits"].items():
        row = []
        for date in week_dates:
            if date in habit["dates"]:
                row.append("  Y")
                total_completions += 1
            else:
                row.append("  -")
            total_possible += 1

        # Truncate long habit names
        display_name = name[:15] if len(name) > 15 else name
        lines.append(f"  {display_name:<15} " + " ".join(row))

    # Summary
    if total_possible > 0:
        rate = (total_completions / total_possible) * 100
    else:
        rate = 0

    lines.append(f"\n  Completion Rate: {total_completions}/{total_possible} ({rate:.0f}%)")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Habit Tracker Server...")
    print("Tools: add_habit, log_habit, get_streaks, weekly_report")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
