"""
Study Planner MCP Server
==========================
Plan study topics by subject and track your learning progress.

Tools:
  - add_topic(subject, topic)
  - mark_completed(topic)
  - get_progress()
  - next_review()

Data is stored in study_plan.json in the current directory.
"""

import json
import os
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Study Planner")

# Path to the JSON data file
DATA_FILE = "study_plan.json"


def load_data():
    """Load study plan from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default structure: list of topics
    return {"topics": []}


def save_data(data):
    """Save study plan to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Tool: add_topic ---
@mcp.tool()
def add_topic(subject: str, topic: str) -> str:
    """Add a new topic to study.

    Args:
        subject: The subject area (e.g., 'Python', 'Math', 'MCP')
        topic: The specific topic to study (e.g., 'Decorators', 'Calculus')
    """
    data = load_data()

    # Check if topic already exists
    for t in data["topics"]:
        if t["topic"].lower() == topic.lower() and t["subject"].lower() == subject.lower():
            return f"Topic '{topic}' already exists in '{subject}'!"

    # Create topic entry
    entry = {
        "subject": subject,
        "topic": topic,
        "completed": False,
        "added_date": datetime.now().strftime("%Y-%m-%d"),
        "completed_date": None,
        "review_date": None  # Set when completed, for spaced repetition
    }

    data["topics"].append(entry)
    save_data(data)

    return f"Added topic: '{topic}' under '{subject}'"


# --- Tool: mark_completed ---
@mcp.tool()
def mark_completed(topic: str) -> str:
    """Mark a topic as completed.

    Args:
        topic: The topic name to mark as done
    """
    data = load_data()

    # Find the topic (case-insensitive)
    for t in data["topics"]:
        if t["topic"].lower() == topic.lower():
            if t["completed"]:
                return f"Topic '{topic}' is already completed!"

            # Mark as completed
            t["completed"] = True
            t["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            # Schedule review in 3 days (spaced repetition)
            review = datetime.now() + timedelta(days=3)
            t["review_date"] = review.strftime("%Y-%m-%d")

            save_data(data)
            return (
                f"Completed: '{topic}' ({t['subject']})\n"
                f"  Completed on: {t['completed_date']}\n"
                f"  Review scheduled: {t['review_date']}"
            )

    return f"Topic '{topic}' not found. Use add_topic to add it first."


# --- Tool: get_progress ---
@mcp.tool()
def get_progress() -> str:
    """Show study progress across all subjects."""
    data = load_data()

    if not data["topics"]:
        return "No topics added yet. Use add_topic to start planning!"

    # Group topics by subject
    subjects = {}
    for t in data["topics"]:
        subj = t["subject"]
        if subj not in subjects:
            subjects[subj] = {"total": 0, "completed": 0, "topics": []}
        subjects[subj]["total"] += 1
        if t["completed"]:
            subjects[subj]["completed"] += 1
        subjects[subj]["topics"].append(t)

    # Build progress report
    total_all = len(data["topics"])
    completed_all = sum(1 for t in data["topics"] if t["completed"])
    overall_pct = (completed_all / total_all * 100) if total_all > 0 else 0

    lines = [f"Study Progress ({completed_all}/{total_all} - {overall_pct:.0f}%):", ""]

    for subj, info in sorted(subjects.items()):
        pct = (info["completed"] / info["total"] * 100) if info["total"] > 0 else 0
        # Progress bar
        bar_filled = int(pct / 10)
        bar = "[" + "#" * bar_filled + "-" * (10 - bar_filled) + "]"
        lines.append(f"  {subj}: {info['completed']}/{info['total']} {bar} {pct:.0f}%")

        # List incomplete topics
        for t in info["topics"]:
            status = "DONE" if t["completed"] else "TODO"
            lines.append(f"    [{status}] {t['topic']}")

        lines.append("")

    return "\n".join(lines)


# --- Tool: next_review ---
@mcp.tool()
def next_review() -> str:
    """Show topics that are due for review (spaced repetition)."""
    data = load_data()

    if not data["topics"]:
        return "No topics added yet."

    today = datetime.now().strftime("%Y-%m-%d")

    # Find topics due for review
    due = []
    upcoming = []

    for t in data["topics"]:
        if not t["completed"] or not t["review_date"]:
            continue
        if t["review_date"] <= today:
            due.append(t)
        else:
            upcoming.append(t)

    lines = ["Review Schedule:", ""]

    # Due now
    if due:
        lines.append(f"  Due for Review ({len(due)}):")
        for t in due:
            lines.append(f"    - {t['topic']} ({t['subject']}) - due {t['review_date']}")
    else:
        lines.append("  No topics due for review right now!")

    # Upcoming reviews
    if upcoming:
        lines.append(f"\n  Upcoming Reviews ({len(upcoming)}):")
        # Sort by review date
        upcoming.sort(key=lambda x: x["review_date"])
        for t in upcoming[:5]:  # Show next 5
            lines.append(f"    - {t['topic']} ({t['subject']}) - review on {t['review_date']}")

    # Incomplete topics (not yet started)
    incomplete = [t for t in data["topics"] if not t["completed"]]
    if incomplete:
        lines.append(f"\n  Still To Study ({len(incomplete)}):")
        for t in incomplete:
            lines.append(f"    - {t['topic']} ({t['subject']})")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Study Planner Server...")
    print("Tools: add_topic, mark_completed, get_progress, next_review")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
