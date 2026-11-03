"""
Example 4: Dynamic Prompts
===========================

This example shows how prompts can include DYNAMIC content -
information that changes each time the prompt is called.

Static prompts always return the same template.
Dynamic prompts include live data like:
  - Current date and time
  - System information
  - Data from files or databases

This makes prompts context-aware and more useful.

Key concepts:
- Using datetime to include current date/time
- Using platform/os to include system info
- Prompts that adapt based on when/where they run
"""

import datetime
import platform

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("DynamicPrompts")


# ---- Prompt 1: Daily Report ----
# This prompt includes the CURRENT date and time.
# Every time a client requests this prompt, it gets
# the latest date/time - not a hardcoded value.
@server.prompt()
def daily_report(tasks_completed: str, blockers: str = "None") -> str:
    """Generate a daily standup report with current date/time."""

    # Get the current date and time dynamically
    # This changes every time the prompt is called
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    day_of_week = now.strftime("%A")

    return (
        f"Generate a daily standup report with the following details:\n\n"
        f"Date: {current_date} ({day_of_week})\n"
        f"Time: {current_time}\n\n"
        f"Tasks Completed:\n{tasks_completed}\n\n"
        f"Blockers:\n{blockers}\n\n"
        f"Please format this as a professional standup update. "
        f"Include a brief summary and any action items."
    )


# ---- Prompt 2: System Prompt ----
# This prompt includes information about the SYSTEM it's running on.
# Useful when you want the LLM to know the environment context.
@server.prompt()
def system_prompt(task: str) -> str:
    """Create a system-aware prompt that includes platform info."""

    # Get system information dynamically
    os_name = platform.system()           # e.g., "Windows", "Linux", "Darwin"
    os_version = platform.version()       # e.g., "10.0.22621"
    python_version = platform.python_version()  # e.g., "3.11.5"
    machine_type = platform.machine()     # e.g., "AMD64", "x86_64"

    return (
        f"You are helping a user on the following system:\n\n"
        f"- Operating System: {os_name}\n"
        f"- OS Version: {os_version}\n"
        f"- Python Version: {python_version}\n"
        f"- Architecture: {machine_type}\n\n"
        f"The user needs help with:\n{task}\n\n"
        f"Please provide instructions that are specific to their "
        f"operating system and environment. Use the correct commands "
        f"and file paths for {os_name}."
    )


# ---- Prompt 3: Time-Aware Greeting ----
# This prompt changes its tone based on the time of day.
# Morning gets an energetic prompt, evening gets a calm one.
@server.prompt()
def time_aware_greeting(user_name: str) -> str:
    """Generate a greeting that changes based on time of day."""

    # Get the current hour to determine time of day
    current_hour = datetime.datetime.now().hour

    # Choose greeting based on time of day
    if current_hour < 12:
        time_greeting = "Good morning"
        mood = "energetic and productive"
    elif current_hour < 17:
        time_greeting = "Good afternoon"
        mood = "focused and helpful"
    else:
        time_greeting = "Good evening"
        mood = "calm and supportive"

    return (
        f"{time_greeting}, {user_name}!\n\n"
        f"You are an AI assistant with a {mood} tone. "
        f"Help the user with whatever they need. "
        f"Be friendly and professional."
    )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
