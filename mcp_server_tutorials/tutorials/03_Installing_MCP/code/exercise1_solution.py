"""
Exercise 1 Solution: Set Up a New MCP Project
"""

import os


def setup_mcp_project(name):
    """Create a complete MCP project with all necessary files."""

    # Create directories
    dirs = [name, f"{name}/src", f"{name}/tests"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created: {d}/")

    # Create pyproject.toml
    pyproject = f'''[tool.poetry]
name = "{name}"
version = "0.1.0"
description = "MCP Server"
authors = ["Developer"]

[tool.poetry.dependencies]
python = "^3.10"
mcp = "^1.0"
httpx = "^0.27"
pydantic = "^2.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
    with open(f"{name}/pyproject.toml", "w") as f:
        f.write(pyproject)
    print(f"Created: {name}/pyproject.toml")

    # Create server.py
    server_code = '''from mcp.server.fastmcp import FastMCP

server = FastMCP("my-server")


@server.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to MCP!"


@server.tool()
def add(a: int, b: int) -> str:
    """Add two numbers."""
    result = a + b
    return str(result)


if __name__ == "__main__":
    server.run()
'''
    with open(f"{name}/src/server.py", "w") as f:
        f.write(server_code)
    print(f"Created: {name}/src/server.py")

    # Create .gitignore
    gitignore = ".venv/\n__pycache__/\n*.pyc\n.env\ndist/\n"
    with open(f"{name}/.gitignore", "w") as f:
        f.write(gitignore)
    print(f"Created: {name}/.gitignore")

    # Print instructions
    print(f"\nProject '{name}' is ready!")
    print(f"\nSetup commands:")
    print(f"  cd {name}")
    print(f"  poetry install")
    print(f"  poetry run python src/server.py")


if __name__ == "__main__":
    setup_mcp_project("my_mcp_project")
