"""
Mini Project: MCP Project Scaffolder
=====================================
A CLI tool that creates new MCP projects with:
- Proper directory structure
- pyproject.toml with dependencies
- Sample server with tool, resource, and prompt
- Sample client for testing
- .gitignore and .env.example
- README with instructions
"""

import os
import sys


def create_directory(path):
    """Create a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def write_file(path, content):
    """Write content to a file."""
    with open(path, "w") as f:
        f.write(content)


def scaffold_project(project_name, author="Developer"):
    """Create a complete MCP project scaffold."""

    print(f"Scaffolding MCP project: {project_name}\n")

    # Step 1: Create directory structure
    directories = [
        project_name,
        f"{project_name}/src",
        f"{project_name}/src/tools",
        f"{project_name}/src/resources",
        f"{project_name}/tests",
    ]
    for d in directories:
        create_directory(d)
        print(f"  [DIR] {d}/")

    # Step 2: Create pyproject.toml
    pyproject_content = f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "An MCP server built with the MCP Python SDK"
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
'''
    write_file(f"{project_name}/pyproject.toml", pyproject_content)
    print(f"  [FILE] pyproject.toml")

    # Step 3: Create server.py
    server_content = '''"""
MCP Server
==========
Main entry point for the MCP server.
"""

from mcp.server.fastmcp import FastMCP

# Create the server
server = FastMCP("''' + project_name + '''")


# --- Tools ---

@server.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


@server.tool()
def add(a: int, b: int) -> str:
    """Add two numbers together."""
    result = a + b
    return str(result)


# --- Resources ---

@server.resource("info://about")
def get_about() -> str:
    """Get information about this server."""
    return "This is a sample MCP server created with the project scaffolder."


# --- Prompts ---

@server.prompt()
def summarize(text: str) -> str:
    """Create a prompt to summarize text."""
    return f"Please summarize the following text in 2-3 sentences:\\n\\n{text}"


# Run the server
if __name__ == "__main__":
    server.run()
'''
    write_file(f"{project_name}/src/server.py", server_content)
    print(f"  [FILE] src/server.py")

    # Step 4: Create client.py
    client_content = '''"""
MCP Client (for testing)
========================
Connects to the server and tests all tools.
"""

import asyncio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters


async def main():
    """Connect to the server and test all features."""

    # Start the server as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["src/server.py"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize connection
            await session.initialize()
            print("Connected to server!\\n")

            # List and call tools
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

            result = await session.call_tool("hello", {"name": "World"})
            print(f"hello result: {result.content[0].text}")

            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"add result: {result.content[0].text}")

            print("\\nAll tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
'''
    write_file(f"{project_name}/src/client.py", client_content)
    print(f"  [FILE] src/client.py")

    # Step 5: Create __init__.py files
    for d in ["src", "src/tools", "src/resources", "tests"]:
        write_file(f"{project_name}/{d}/__init__.py", "")

    # Step 6: Create .gitignore
    gitignore_content = """.venv/
__pycache__/
*.pyc
.env
dist/
*.egg-info/
.pytest_cache/
"""
    write_file(f"{project_name}/.gitignore", gitignore_content)
    print(f"  [FILE] .gitignore")

    # Step 7: Create .env.example
    env_content = """# Copy to .env and fill in your values
# HUGGINGFACE_API_KEY=your_key_here
"""
    write_file(f"{project_name}/.env.example", env_content)
    print(f"  [FILE] .env.example")

    # Step 8: Create README
    readme_content = f"""# {project_name}

An MCP server built with the MCP Python SDK.

## Setup

```bash
cd {project_name}
poetry install
```

## Run Server

```bash
poetry run python src/server.py
```

## Test

```bash
poetry run python src/client.py
```
"""
    write_file(f"{project_name}/README.md", readme_content)
    print(f"  [FILE] README.md")

    # Summary
    print(f"\nProject '{project_name}' scaffolded successfully!")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  poetry install")
    print(f"  poetry run python src/server.py")


if __name__ == "__main__":
    # Get project name from command line or use default
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "my_mcp_server"

    scaffold_project(name)
