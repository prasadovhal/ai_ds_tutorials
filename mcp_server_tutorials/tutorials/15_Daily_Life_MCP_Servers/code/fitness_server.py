"""
Fitness Tracker MCP Server
============================
Log workouts and track fitness progress.

Tools:
  - log_workout(exercise, sets, reps)
  - view_history()
  - weekly_summary()
  - personal_records()

Data is stored in fitness.json in the current directory.
"""

import json
import os
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Fitness Tracker")

# Path to the JSON data file
DATA_FILE = "fitness.json"


def load_workouts():
    """Load workout history from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_workouts(workouts):
    """Save workout history to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(workouts, f, indent=2)


# --- Tool: log_workout ---
@mcp.tool()
def log_workout(exercise: str, sets: int, reps: int) -> str:
    """Log a workout exercise.

    Args:
        exercise: Name of the exercise (e.g., 'Push-ups', 'Squats')
        sets: Number of sets performed
        reps: Number of reps per set
    """
    workouts = load_workouts()

    # Create workout entry
    workout = {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "total_reps": sets * reps,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    }

    workouts.append(workout)
    save_workouts(workouts)

    return (
        f"Workout logged!\n"
        f"  Exercise: {exercise}\n"
        f"  Sets: {sets} x Reps: {reps}\n"
        f"  Total Reps: {sets * reps}\n"
        f"  Date: {workout['date']}"
    )


# --- Tool: view_history ---
@mcp.tool()
def view_history() -> str:
    """View all workout history."""
    workouts = load_workouts()

    if not workouts:
        return "No workouts logged yet. Use log_workout to start!"

    lines = [f"Workout History ({len(workouts)} entries):", ""]

    # Group by date for better readability
    current_date = None
    for w in workouts:
        if w["date"] != current_date:
            current_date = w["date"]
            lines.append(f"  [{current_date}]")

        lines.append(
            f"    - {w['exercise']}: {w['sets']} sets x {w['reps']} reps "
            f"({w['total_reps']} total)"
        )

    return "\n".join(lines)


# --- Tool: weekly_summary ---
@mcp.tool()
def weekly_summary() -> str:
    """Get a summary of workouts from the past 7 days."""
    workouts = load_workouts()

    if not workouts:
        return "No workouts logged yet."

    # Calculate the date 7 days ago
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Filter workouts from the past week
    weekly = [w for w in workouts if w["date"] >= week_ago]

    if not weekly:
        return "No workouts in the past 7 days. Time to get moving!"

    # Count exercises and total reps
    exercises = {}
    total_reps = 0
    workout_days = set()

    for w in weekly:
        exercise = w["exercise"]
        if exercise not in exercises:
            exercises[exercise] = 0
        exercises[exercise] += w["total_reps"]
        total_reps += w["total_reps"]
        workout_days.add(w["date"])

    # Build summary
    lines = ["Weekly Summary (Past 7 Days):", ""]
    lines.append(f"  Workout Days: {len(workout_days)}")
    lines.append(f"  Total Sessions: {len(weekly)}")
    lines.append(f"  Total Reps: {total_reps}")
    lines.append(f"\n  By Exercise:")

    for exercise, reps in sorted(exercises.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"    {exercise}: {reps} total reps")

    return "\n".join(lines)


# --- Tool: personal_records ---
@mcp.tool()
def personal_records() -> str:
    """Show personal records (highest total reps) for each exercise."""
    workouts = load_workouts()

    if not workouts:
        return "No workouts logged yet."

    # Find the best session for each exercise
    records = {}
    for w in workouts:
        exercise = w["exercise"]
        if exercise not in records or w["total_reps"] > records[exercise]["total_reps"]:
            records[exercise] = w

    # Build records display
    lines = ["Personal Records:", ""]

    for exercise, record in sorted(records.items()):
        lines.append(
            f"  {exercise}: {record['total_reps']} reps "
            f"({record['sets']}x{record['reps']}) on {record['date']}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Fitness Tracker Server...")
    print("Tools: log_workout, view_history, weekly_summary, personal_records")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
