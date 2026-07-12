"""
Example 5: pyproject.toml Generator
====================================
Generates a properly configured pyproject.toml for MCP projects.
"""


def generate_pyproject(project_name, description="An MCP server", author="Developer"):
    """Generate pyproject.toml content for an MCP project."""

    content = f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "{description}"
authors = ["{author}"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
mcp = "^1.0"
httpx = "^0.27"
pydantic = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
asyncio_mode = "auto"
'''
    return content


if __name__ == "__main__":
    print("=== pyproject.toml Generator ===\n")

    # Generate for a sample project
    project_name = "my-mcp-server"
    description = "A custom MCP server for data analysis"
    author = "Your Name <you@example.com>"

    content = generate_pyproject(project_name, description, author)
    print("Generated pyproject.toml:\n")
    print(content)

    # Save to file
    filename = "pyproject_example.toml"
    with open(filename, "w") as f:
        f.write(content)
    print(f"\nSaved to {filename}")
    print("\nTo use: copy this file to your project root as pyproject.toml")
    print("Then run: poetry install")
