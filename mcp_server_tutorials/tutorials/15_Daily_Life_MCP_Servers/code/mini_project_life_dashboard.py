"""
Mini Project - Life Dashboard MCP Server
==========================================
An all-in-one daily life server combining:
  - Expenses (add, list, summary)
  - Habits (add, log, streaks)
  - Fitness (log, history)
  - Journal (add, search)

All data stored in a single life_dashboard.json file.
12+ tools covering all four areas.
"""

import json
import os
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Life Dashboard")

# Single data file for everything
DATA_FILE = "life_dashboard.json"


def load_data():
    """Load all dashboard data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default structure with all four sections
    return {
        "expenses": [],
        "habits": {},
        "workouts": [],
        "journal": []
    }


def save_data(data):
    """Save all dashboard data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# EXPENSE TOOLS (3 tools)
# ============================================================

@mcp.tool()
def add_expense(amount: float, category: str, description: str) -> str:
    """Add a new expense to track.

    Args:
        amount: The expense amount (e.g., 12.50)
        category: Category like 'food', 'transport', 'entertainment'
        description: Brief description of the expense
    """
    data = load_data()

    expense = {
        "amount": amount,
        "category": category.lower(),
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    }

    data["expenses"].append(expense)
    save_data(data)

    return f"Expense added: ${amount:.2f} ({category}) - {description}"


@mcp.tool()
def list_expenses() -> str:
    """List all recorded expenses."""
    data = load_data()
    expenses = data["expenses"]

    if not expenses:
        return "No expenses yet. Use add_expense to start tracking!"

    lines = [f"Expenses ({len(expenses)}):", ""]
    total = 0.0
    for i, exp in enumerate(expenses, 1):
        lines.append(
            f"  {i}. [{exp['date']}] ${exp['amount']:.2f} "
            f"({exp['category']}) - {exp['description']}"
        )
        total += exp["amount"]

    lines.append(f"\nTotal: ${total:.2f}")
    return "\n".join(lines)


@mcp.tool()
def expense_summary() -> str:
    """Get monthly expense summary grouped by category."""
    data = load_data()
    expenses = data["expenses"]

    if not expenses:
        return "No expenses recorded."

    # Filter current month
    current_month = datetime.now().strftime("%Y-%m")
    monthly = [e for e in expenses if e["date"].startswith(current_month)]

    if not monthly:
        return f"No expenses for {current_month}."

    # Group by category
    categories = {}
    for exp in monthly:
        cat = exp["category"]
        categories[cat] = categories.get(cat, 0.0) + exp["amount"]

    total = sum(categories.values())
    lines = [f"Expense Summary ({current_month}):", ""]

    for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / total) * 100
        lines.append(f"  {cat}: ${amount:.2f} ({pct:.1f}%)")

    lines.append(f"\nTotal: ${total:.2f} across {len(monthly)} transactions")
    return "\n".join(lines)


# ============================================================
# HABIT TOOLS (3 tools)
# ============================================================

@mcp.tool()
def add_habit(name: str) -> str:
    """Add a new habit to track.

    Args:
        name: Name of the habit (e.g., 'Read', 'Meditate', 'Exercise')
    """
    data = load_data()

    # Check for duplicates
    if name.lower() in [h.lower() for h in data["habits"]]:
        return f"Habit '{name}' already exists!"

    data["habits"][name] = {
        "created": datetime.now().strftime("%Y-%m-%d"),
        "dates": []
    }

    save_data(data)
    return f"Habit '{name}' added! Use log_habit to record completions."


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

    if today in data["habits"][habit_key]["dates"]:
        return f"'{habit_key}' already logged for today!"

    data["habits"][habit_key]["dates"].append(today)
    save_data(data)

    # Calculate streak
    dates = sorted(data["habits"][habit_key]["dates"], reverse=True)
    streak = 1
    for i in range(1, len(dates)):
        current = datetime.strptime(dates[i - 1], "%Y-%m-%d")
        previous = datetime.strptime(dates[i], "%Y-%m-%d")
        if (current - previous).days == 1:
            streak += 1
        else:
            break

    return f"'{habit_key}' logged for {today}! Streak: {streak} day(s)"


@mcp.tool()
def habit_streaks() -> str:
    """Show current streaks for all habits."""
    data = load_data()

    if not data["habits"]:
        return "No habits tracked. Use add_habit to start!"

    lines = ["Habit Streaks:", ""]

    for name, habit in data["habits"].items():
        dates = sorted(habit["dates"], reverse=True)
        total = len(dates)

        # Calculate streak
        streak = 0
        if dates:
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if dates[0] == today or dates[0] == yesterday:
                streak = 1
                for i in range(1, len(dates)):
                    current = datetime.strptime(dates[i - 1], "%Y-%m-%d")
                    previous = datetime.strptime(dates[i], "%Y-%m-%d")
                    if (current - previous).days == 1:
                        streak += 1
                    else:
                        break

        status = "Active" if streak > 0 else "Inactive"
        lines.append(f"  {name}: {streak} day streak ({total} total) [{status}]")

    return "\n".join(lines)


# ============================================================
# FITNESS TOOLS (2 tools)
# ============================================================

@mcp.tool()
def log_workout(exercise: str, sets: int, reps: int) -> str:
    """Log a workout exercise.

    Args:
        exercise: Name of the exercise (e.g., 'Push-ups', 'Squats')
        sets: Number of sets
        reps: Number of reps per set
    """
    data = load_data()

    workout = {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "total_reps": sets * reps,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    }

    data["workouts"].append(workout)
    save_data(data)

    return (
        f"Workout logged: {exercise}\n"
        f"  {sets} sets x {reps} reps = {sets * reps} total"
    )


@mcp.tool()
def fitness_history() -> str:
    """View workout history."""
    data = load_data()
    workouts = data["workouts"]

    if not workouts:
        return "No workouts logged. Use log_workout to start!"

    lines = [f"Fitness History ({len(workouts)} sessions):", ""]

    # Group by date
    current_date = None
    for w in workouts:
        if w["date"] != current_date:
            current_date = w["date"]
            lines.append(f"  [{current_date}]")
        lines.append(
            f"    {w['exercise']}: {w['sets']}x{w['reps']} "
            f"({w['total_reps']} total)"
        )

    return "\n".join(lines)


# ============================================================
# JOURNAL TOOLS (2 tools)
# ============================================================

@mcp.tool()
def add_journal_entry(text: str, mood: str) -> str:
    """Add a journal entry with mood.

    Args:
        text: The journal entry text
        mood: Your current mood (e.g., 'happy', 'sad', 'neutral')
    """
    data = load_data()

    entry = {
        "text": text,
        "mood": mood.lower(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "id": len(data["journal"]) + 1
    }

    data["journal"].append(entry)
    save_data(data)

    return (
        f"Journal entry #{entry['id']} saved!\n"
        f"  Mood: {mood} | Date: {entry['date']}"
    )


@mcp.tool()
def search_journal(keyword: str) -> str:
    """Search journal entries by keyword.

    Args:
        keyword: Word or phrase to search for
    """
    data = load_data()
    entries = data["journal"]

    if not entries:
        return "No journal entries. Use add_journal_entry to start!"

    # Search in text and mood
    matches = []
    for entry in entries:
        if (keyword.lower() in entry["text"].lower() or
                keyword.lower() in entry["mood"].lower()):
            matches.append(entry)

    if not matches:
        return f"No entries matching '{keyword}'."

    lines = [f"Found {len(matches)} entry/entries for '{keyword}':", ""]
    for entry in matches:
        preview = entry["text"][:80]
        if len(entry["text"]) > 80:
            preview += "..."
        lines.append(f"  #{entry['id']} [{entry['date']}] ({entry['mood']})")
        lines.append(f"    {preview}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# DASHBOARD OVERVIEW (2 tools)
# ============================================================

@mcp.tool()
def daily_overview() -> str:
    """Get a daily overview of all tracked areas."""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [f"Daily Overview ({today}):", ""]

    # Today's expenses
    today_expenses = [e for e in data["expenses"] if e["date"] == today]
    total_spent = sum(e["amount"] for e in today_expenses)
    lines.append(f"  Expenses Today: ${total_spent:.2f} ({len(today_expenses)} transactions)")

    # Today's habits
    habits_done = 0
    habits_total = len(data["habits"])
    for name, habit in data["habits"].items():
        if today in habit["dates"]:
            habits_done += 1
    lines.append(f"  Habits Today: {habits_done}/{habits_total} completed")

    # Today's workouts
    today_workouts = [w for w in data["workouts"] if w["date"] == today]
    total_reps = sum(w["total_reps"] for w in today_workouts)
    lines.append(f"  Workouts Today: {len(today_workouts)} sessions, {total_reps} total reps")

    # Today's journal entries
    today_journal = [j for j in data["journal"] if j["date"] == today]
    lines.append(f"  Journal Today: {len(today_journal)} entries")

    return "\n".join(lines)


@mcp.tool()
def dashboard_stats() -> str:
    """Show overall statistics across all areas."""
    data = load_data()

    lines = ["Life Dashboard Statistics:", ""]

    # Expense stats
    total_expenses = sum(e["amount"] for e in data["expenses"])
    lines.append(f"  EXPENSES:")
    lines.append(f"    Total Spent: ${total_expenses:.2f}")
    lines.append(f"    Transactions: {len(data['expenses'])}")

    # Habit stats
    total_logs = sum(len(h["dates"]) for h in data["habits"].values())
    lines.append(f"\n  HABITS:")
    lines.append(f"    Habits Tracked: {len(data['habits'])}")
    lines.append(f"    Total Completions: {total_logs}")

    # Fitness stats
    total_reps = sum(w["total_reps"] for w in data["workouts"])
    workout_days = len(set(w["date"] for w in data["workouts"]))
    lines.append(f"\n  FITNESS:")
    lines.append(f"    Workout Sessions: {len(data['workouts'])}")
    lines.append(f"    Active Days: {workout_days}")
    lines.append(f"    Total Reps: {total_reps}")

    # Journal stats
    mood_counts = {}
    for j in data["journal"]:
        mood_counts[j["mood"]] = mood_counts.get(j["mood"], 0) + 1
    most_common = max(mood_counts, key=mood_counts.get) if mood_counts else "N/A"
    lines.append(f"\n  JOURNAL:")
    lines.append(f"    Total Entries: {len(data['journal'])}")
    lines.append(f"    Most Common Mood: {most_common}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Life Dashboard Server...")
    print()
    print("Available Tools (14 total):")
    print()
    print("  EXPENSES:")
    print("    - add_expense(amount, category, description)")
    print("    - list_expenses()")
    print("    - expense_summary()")
    print()
    print("  HABITS:")
    print("    - add_habit(name)")
    print("    - log_habit(name)")
    print("    - habit_streaks()")
    print()
    print("  FITNESS:")
    print("    - log_workout(exercise, sets, reps)")
    print("    - fitness_history()")
    print()
    print("  JOURNAL:")
    print("    - add_journal_entry(text, mood)")
    print("    - search_journal(keyword)")
    print()
    print("  DASHBOARD:")
    print("    - daily_overview()")
    print("    - dashboard_stats()")
    print()
    print(f"Data file: {os.path.abspath(DATA_FILE)}")

    # Run the server
    mcp.run()
