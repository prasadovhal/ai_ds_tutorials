"""
Expense Tracker MCP Server
============================
Track daily expenses with categories and budgets.

Tools:
  - add_expense(amount, category, description)
  - list_expenses()
  - monthly_summary()
  - budget_check(limit)

Data is stored in expenses.json in the current directory.
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Expense Tracker")

# Path to the JSON data file
DATA_FILE = "expenses.json"


def load_expenses():
    """Load expenses from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Return empty list if file doesn't exist
    return []


def save_expenses(expenses):
    """Save expenses to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


# --- Tool: add_expense ---
@mcp.tool()
def add_expense(amount: float, category: str, description: str) -> str:
    """Add a new expense.

    Args:
        amount: The expense amount (e.g., 15.50)
        category: Category like 'food', 'transport', 'entertainment'
        description: Brief description of the expense
    """
    # Load existing expenses
    expenses = load_expenses()

    # Create new expense entry with timestamp
    expense = {
        "amount": amount,
        "category": category.lower(),
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    }

    # Add and save
    expenses.append(expense)
    save_expenses(expenses)

    return f"Added expense: ${amount:.2f} in '{category}' - {description}"


# --- Tool: list_expenses ---
@mcp.tool()
def list_expenses() -> str:
    """List all recorded expenses."""
    expenses = load_expenses()

    if not expenses:
        return "No expenses recorded yet. Use add_expense to start tracking!"

    # Format each expense as a readable line
    lines = ["All Expenses:", ""]
    total = 0.0
    for i, exp in enumerate(expenses, 1):
        lines.append(
            f"  {i}. [{exp['date']}] ${exp['amount']:.2f} "
            f"({exp['category']}) - {exp['description']}"
        )
        total += exp["amount"]

    lines.append(f"\nTotal: ${total:.2f}")
    lines.append(f"Count: {len(expenses)} expense(s)")

    return "\n".join(lines)


# --- Tool: monthly_summary ---
@mcp.tool()
def monthly_summary() -> str:
    """Get a summary of expenses for the current month, grouped by category."""
    expenses = load_expenses()

    if not expenses:
        return "No expenses recorded yet."

    # Filter for current month
    current_month = datetime.now().strftime("%Y-%m")
    monthly = [e for e in expenses if e["date"].startswith(current_month)]

    if not monthly:
        return f"No expenses found for {current_month}."

    # Group by category
    categories = {}
    for exp in monthly:
        cat = exp["category"]
        if cat not in categories:
            categories[cat] = 0.0
        categories[cat] += exp["amount"]

    # Build summary
    total = sum(categories.values())
    lines = [f"Monthly Summary ({current_month}):", ""]

    # Sort categories by amount (highest first)
    for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total) * 100
        lines.append(f"  {cat}: ${amount:.2f} ({percentage:.1f}%)")

    lines.append(f"\nTotal: ${total:.2f}")
    lines.append(f"Categories: {len(categories)}")
    lines.append(f"Transactions: {len(monthly)}")

    return "\n".join(lines)


# --- Tool: budget_check ---
@mcp.tool()
def budget_check(limit: float) -> str:
    """Check if current month's spending is within a budget limit.

    Args:
        limit: The monthly budget limit in dollars
    """
    expenses = load_expenses()

    # Sum up current month's expenses
    current_month = datetime.now().strftime("%Y-%m")
    monthly_total = sum(
        e["amount"] for e in expenses
        if e["date"].startswith(current_month)
    )

    # Calculate remaining budget
    remaining = limit - monthly_total
    percentage_used = (monthly_total / limit * 100) if limit > 0 else 0

    # Build the report
    lines = [f"Budget Check ({current_month}):", ""]
    lines.append(f"  Budget Limit: ${limit:.2f}")
    lines.append(f"  Spent:        ${monthly_total:.2f}")
    lines.append(f"  Remaining:    ${remaining:.2f}")
    lines.append(f"  Used:         {percentage_used:.1f}%")

    # Add a status message
    if remaining > 0:
        lines.append(f"\n  Status: WITHIN BUDGET - ${remaining:.2f} left to spend")
    elif remaining == 0:
        lines.append(f"\n  Status: EXACTLY AT BUDGET - no more spending!")
    else:
        lines.append(f"\n  Status: OVER BUDGET by ${abs(remaining):.2f}!")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Expense Tracker Server...")
    print("Tools: add_expense, list_expenses, monthly_summary, budget_check")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
