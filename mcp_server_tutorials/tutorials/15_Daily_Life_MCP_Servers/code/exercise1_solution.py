"""
Exercise 1 Solution - Medicine Reminder Server
================================================
Track medicines, dosages, schedules, and mark them as taken.

Tools:
  - add_medicine(name, dosage, time)
  - list_medicines()
  - check_due()
  - mark_taken(name)

Data is stored in medicines.json.
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Medicine Reminder")

# Path to the JSON data file
DATA_FILE = "medicines.json"


def load_medicines():
    """Load medicines data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default structure: list of medicines with taken log
    return {"medicines": [], "taken_log": []}


def save_medicines(data):
    """Save medicines data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Tool: add_medicine ---
@mcp.tool()
def add_medicine(name: str, dosage: str, time: str) -> str:
    """Add a medicine to track.

    Args:
        name: Name of the medicine (e.g., 'Aspirin')
        dosage: Dosage info (e.g., '500mg', '1 tablet')
        time: Scheduled time (e.g., '08:00', '14:30', '21:00')
    """
    data = load_medicines()

    # Check if medicine already exists
    for med in data["medicines"]:
        if med["name"].lower() == name.lower():
            return f"Medicine '{name}' already exists!"

    # Validate time format
    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return f"Invalid time format: '{time}'. Use HH:MM format (e.g., '08:00')."

    # Add the medicine
    medicine = {
        "name": name,
        "dosage": dosage,
        "time": time
    }

    data["medicines"].append(medicine)
    save_medicines(data)

    return (
        f"Medicine added:\n"
        f"  Name: {name}\n"
        f"  Dosage: {dosage}\n"
        f"  Time: {time}"
    )


# --- Tool: list_medicines ---
@mcp.tool()
def list_medicines() -> str:
    """List all tracked medicines."""
    data = load_medicines()

    if not data["medicines"]:
        return "No medicines being tracked. Use add_medicine to start."

    today = datetime.now().strftime("%Y-%m-%d")

    lines = [f"Your Medicines ({len(data['medicines'])}):", ""]

    for med in data["medicines"]:
        # Check if taken today
        taken_today = any(
            log["name"].lower() == med["name"].lower() and log["date"] == today
            for log in data["taken_log"]
        )
        status = "TAKEN" if taken_today else "PENDING"

        lines.append(f"  - {med['name']} ({med['dosage']}) at {med['time']} [{status}]")

    return "\n".join(lines)


# --- Tool: check_due ---
@mcp.tool()
def check_due() -> str:
    """Check which medicines are due now or overdue."""
    data = load_medicines()

    if not data["medicines"]:
        return "No medicines being tracked."

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    due = []
    taken = []
    upcoming = []

    for med in data["medicines"]:
        # Check if already taken today
        taken_today = any(
            log["name"].lower() == med["name"].lower() and log["date"] == today
            for log in data["taken_log"]
        )

        if taken_today:
            taken.append(med)
        elif med["time"] <= current_time:
            due.append(med)
        else:
            upcoming.append(med)

    lines = [f"Medicine Check ({current_time}):", ""]

    if due:
        lines.append(f"  DUE NOW ({len(due)}):")
        for med in due:
            lines.append(f"    - {med['name']} ({med['dosage']}) - scheduled {med['time']}")
    else:
        lines.append("  No medicines due right now.")

    if taken:
        lines.append(f"\n  ALREADY TAKEN ({len(taken)}):")
        for med in taken:
            lines.append(f"    - {med['name']} ({med['dosage']})")

    if upcoming:
        lines.append(f"\n  UPCOMING ({len(upcoming)}):")
        for med in upcoming:
            lines.append(f"    - {med['name']} ({med['dosage']}) at {med['time']}")

    return "\n".join(lines)


# --- Tool: mark_taken ---
@mcp.tool()
def mark_taken(name: str) -> str:
    """Mark a medicine as taken today.

    Args:
        name: Name of the medicine to mark as taken
    """
    data = load_medicines()

    # Find the medicine
    found = None
    for med in data["medicines"]:
        if med["name"].lower() == name.lower():
            found = med
            break

    if not found:
        return f"Medicine '{name}' not found. Use list_medicines to see all."

    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    # Check if already taken today
    already_taken = any(
        log["name"].lower() == name.lower() and log["date"] == today
        for log in data["taken_log"]
    )

    if already_taken:
        return f"'{found['name']}' already marked as taken today!"

    # Log as taken
    log_entry = {
        "name": found["name"],
        "date": today,
        "time_taken": now,
        "dosage": found["dosage"]
    }

    data["taken_log"].append(log_entry)
    save_medicines(data)

    return (
        f"Marked '{found['name']}' as taken!\n"
        f"  Dosage: {found['dosage']}\n"
        f"  Scheduled: {found['time']}\n"
        f"  Taken at: {now}"
    )


if __name__ == "__main__":
    print("Starting Medicine Reminder Server...")
    print("Tools: add_medicine, list_medicines, check_due, mark_taken")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
