"""
Recipe Manager MCP Server
===========================
Store and search recipes with ingredients and steps.

Tools:
  - add_recipe(name, ingredients_csv, steps)
  - search_by_ingredient(ingredient)
  - list_recipes()
  - get_recipe(name)

Data is stored in recipes.json in the current directory.
"""

import json
import os
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Recipe Manager")

# Path to the JSON data file
DATA_FILE = "recipes.json"


def load_recipes():
    """Load recipes from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_recipes(recipes):
    """Save recipes to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(recipes, f, indent=2)


# --- Tool: add_recipe ---
@mcp.tool()
def add_recipe(name: str, ingredients_csv: str, steps: str) -> str:
    """Add a new recipe.

    Args:
        name: Name of the recipe (e.g., 'Pasta Carbonara')
        ingredients_csv: Comma-separated ingredients (e.g., 'pasta, eggs, cheese, bacon')
        steps: Cooking steps separated by periods or newlines
    """
    recipes = load_recipes()

    # Check if recipe already exists (case-insensitive)
    for r in recipes:
        if r["name"].lower() == name.lower():
            return f"Recipe '{name}' already exists! Use a different name."

    # Parse ingredients from CSV string
    ingredients = [i.strip() for i in ingredients_csv.split(",") if i.strip()]

    # Parse steps - split by period or newline
    step_list = []
    for step in steps.replace("\n", ".").split("."):
        step = step.strip()
        if step:
            step_list.append(step)

    # Create recipe entry
    recipe = {
        "name": name,
        "ingredients": ingredients,
        "steps": step_list
    }

    recipes.append(recipe)
    save_recipes(recipes)

    return (
        f"Added recipe: {name}\n"
        f"  Ingredients: {len(ingredients)}\n"
        f"  Steps: {len(step_list)}"
    )


# --- Tool: search_by_ingredient ---
@mcp.tool()
def search_by_ingredient(ingredient: str) -> str:
    """Find recipes that use a specific ingredient.

    Args:
        ingredient: Ingredient to search for (e.g., 'chicken')
    """
    recipes = load_recipes()

    if not recipes:
        return "No recipes stored yet. Use add_recipe to add some!"

    # Search for the ingredient (case-insensitive, partial match)
    matches = []
    for recipe in recipes:
        for ing in recipe["ingredients"]:
            if ingredient.lower() in ing.lower():
                matches.append(recipe["name"])
                break  # Don't add the same recipe twice

    if not matches:
        return f"No recipes found with '{ingredient}'."

    lines = [f"Recipes with '{ingredient}':", ""]
    for i, name in enumerate(matches, 1):
        lines.append(f"  {i}. {name}")

    return "\n".join(lines)


# --- Tool: list_recipes ---
@mcp.tool()
def list_recipes() -> str:
    """List all stored recipes."""
    recipes = load_recipes()

    if not recipes:
        return "No recipes stored yet. Use add_recipe to add some!"

    lines = [f"All Recipes ({len(recipes)}):", ""]
    for i, recipe in enumerate(recipes, 1):
        ing_count = len(recipe["ingredients"])
        lines.append(f"  {i}. {recipe['name']} ({ing_count} ingredients)")

    return "\n".join(lines)


# --- Tool: get_recipe ---
@mcp.tool()
def get_recipe(name: str) -> str:
    """Get the full details of a recipe by name.

    Args:
        name: Name of the recipe to look up
    """
    recipes = load_recipes()

    # Find the recipe (case-insensitive)
    recipe = None
    for r in recipes:
        if r["name"].lower() == name.lower():
            recipe = r
            break

    if not recipe:
        return f"Recipe '{name}' not found. Use list_recipes to see all recipes."

    # Format the recipe nicely
    lines = [f"Recipe: {recipe['name']}", ""]

    lines.append("Ingredients:")
    for ing in recipe["ingredients"]:
        lines.append(f"  - {ing}")

    lines.append("\nSteps:")
    for i, step in enumerate(recipe["steps"], 1):
        lines.append(f"  {i}. {step}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Recipe Manager Server...")
    print("Tools: add_recipe, search_by_ingredient, list_recipes, get_recipe")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    mcp.run()
