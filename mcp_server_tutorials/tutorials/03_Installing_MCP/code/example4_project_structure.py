"""
Example 4: MCP Project Structure Generator
===========================================
Creates the recommended directory structure for an MCP project.
"""

import os


def create_project_structure(project_name):
    """Create the directory structure for a new MCP project."""

    # Define all directories to create
    directories = [
        project_name,
        os.path.join(project_name, "src"),
        os.path.join(project_name, "src", "tools"),
        os.path.join(project_name, "src", "resources"),
        os.path.join(project_name, "src", "prompts"),
        os.path.join(project_name, "tests"),
    ]

    # Create each directory
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    # Define files to create with their content
    files = {
        os.path.join(project_name, "src", "__init__.py"): "",
        os.path.join(project_name, "src", "tools", "__init__.py"): "",
        os.path.join(project_name, "src", "resources", "__init__.py"): "",
        os.path.join(project_name, "src", "prompts", "__init__.py"): "",
        os.path.join(project_name, "tests", "__init__.py"): "",
        os.path.join(project_name, "src", "server.py"): (
            'from mcp.server.fastmcp import FastMCP\n\n'
            'server = FastMCP("' + project_name + '")\n\n\n'
            '@server.tool()\n'
            'def hello(name: str) -> str:\n'
            '    """Say hello."""\n'
            '    return f"Hello, {name}!"\n\n\n'
            'if __name__ == "__main__":\n'
            '    server.run()\n'
        ),
        os.path.join(project_name, ".gitignore"): (
            ".venv/\n__pycache__/\n*.pyc\n.env\n*.egg-info/\ndist/\n"
        ),
        os.path.join(project_name, ".env.example"): (
            "# Copy this to .env and fill in your values\n"
            "# HUGGINGFACE_API_KEY=your_key_here\n"
        ),
    }

    # Create each file
    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created file: {filepath}")

    print(f"\nProject '{project_name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  poetry init")
    print(f"  poetry add mcp httpx pydantic")
    print(f"  poetry run python src/server.py")


if __name__ == "__main__":
    project_name = "my_mcp_project"
    print(f"Creating MCP project: {project_name}\n")
    create_project_structure(project_name)
