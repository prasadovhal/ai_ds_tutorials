"""
Exercise 3 Solution: Quiz/Flashcard Server
"""

import json
import os
import random
from mcp.server.fastmcp import FastMCP

server = FastMCP("quiz-server")

# File to store flashcards
CARDS_FILE = "flashcards.json"

# Track quiz statistics in memory
quiz_stats = {
    "total_attempts": 0,
    "correct": 0,
    "wrong": 0,
}


def load_cards():
    """Load flashcards from JSON file."""
    if not os.path.exists(CARDS_FILE):
        return []
    with open(CARDS_FILE, "r") as f:
        return json.load(f)


def save_cards(cards):
    """Save flashcards to JSON file."""
    with open(CARDS_FILE, "w") as f:
        json.dump(cards, f, indent=2)


@server.tool()
def add_card(question: str, answer: str) -> str:
    """Add a new flashcard."""
    cards = load_cards()

    # Check if question already exists
    for card in cards:
        if card["question"].lower() == question.lower():
            return f"Card already exists for: {question}"

    new_card = {"question": question, "answer": answer}
    cards.append(new_card)
    save_cards(cards)
    return f"Card added! Total cards: {len(cards)}"


@server.tool()
def get_random_card() -> str:
    """Get a random flashcard question."""
    cards = load_cards()
    if len(cards) == 0:
        return "No cards yet. Add some with add_card first!"

    card = random.choice(cards)
    return f"Question: {card['question']}"


@server.tool()
def check_answer(question: str, user_answer: str) -> str:
    """Check if the user's answer is correct."""
    cards = load_cards()

    # Find the card
    for card in cards:
        if card["question"].lower() == question.lower():
            quiz_stats["total_attempts"] += 1

            # Compare answers (case-insensitive)
            if user_answer.lower().strip() == card["answer"].lower().strip():
                quiz_stats["correct"] += 1
                return f"Correct! The answer is: {card['answer']}"
            else:
                quiz_stats["wrong"] += 1
                return f"Wrong! Your answer: {user_answer}. Correct answer: {card['answer']}"

    return f"Card not found for question: {question}"


@server.tool()
def get_stats() -> str:
    """Get quiz statistics."""
    total = quiz_stats["total_attempts"]
    correct = quiz_stats["correct"]
    wrong = quiz_stats["wrong"]

    if total == 0:
        accuracy = 0
    else:
        accuracy = round((correct / total) * 100, 1)

    result = f"Quiz Stats:\n"
    result += f"  Total attempts: {total}\n"
    result += f"  Correct: {correct}\n"
    result += f"  Wrong: {wrong}\n"
    result += f"  Accuracy: {accuracy}%"
    return result


@server.tool()
def list_cards() -> str:
    """List all flashcards."""
    cards = load_cards()
    if len(cards) == 0:
        return "No cards yet."

    result = f"Flashcards ({len(cards)} total):\n"
    for i, card in enumerate(cards):
        result += f"  {i + 1}. Q: {card['question']} | A: {card['answer']}\n"
    return result


if __name__ == "__main__":
    server.run()
