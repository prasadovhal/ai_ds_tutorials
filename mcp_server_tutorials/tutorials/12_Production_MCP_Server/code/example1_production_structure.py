"""
Example 1: Creating a Production Directory Structure
=====================================================
This script creates the recommended folder layout for a
production-grade MCP server project.

A good directory structure keeps your code organized:
- src/         --> your server source code
- src/tools/   --> individual tool implementations
- src/resources/ --> resource handlers
- tests/       --> unit and integration tests
- config/      --> configuration files
- logs/        --> log files (git-ignored)
- docs/        --> documentation

This is NOT an MCP server itself -- it is a helper script
that sets up the project skeleton for you.

Poetry setup:
    poetry init --name example1-production-structure --python "^3.11" --no-interaction
    poetry install
    poetry shell
"""

import os

# ============================================================
# STEP 1: Define the directory structure
# ============================================================

# The base directory where we will create the project
# We create it inside the same folder as this script
base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(base_dir, "my_production_server")

# List of all directories to create
# Each entry is a relative path from the project root
directories = [
    # Source code
    "src",
    "src/tools",
    "src/resources",
    "src/prompts",
    "src/utils",

    # Tests
    "tests",
    "tests/unit",
    "tests/integration",

    # Configuration
    "config",

    # Logs (will be git-ignored)
    "logs",

    # Documentation
    "docs",
]

# ============================================================
# STEP 2: Define template files to create
# ============================================================

# Each entry is (relative_path, file_content)
# These are starter files with basic content
template_files = {
    # Main server entry point
    "src/server.py": '''"""
Main MCP Server Entry Point
============================
This is the main file that starts the MCP server.
All tools, resources, and prompts are registered here.
"""

from mcp.server.fastmcp import FastMCP

# Create the server instance
server = FastMCP("my-production-server")

# Import and register tools
# from tools.calculator import register_calculator_tools
# from tools.text import register_text_tools

if __name__ == "__main__":
    server.run(transport="stdio")
''',

    # Example tool module
    "src/tools/__init__.py": '# Tools package\n',

    "src/tools/calculator.py": '''"""
Calculator Tools
================
Math tools for the MCP server.
"""


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b
''',

    # Resources package
    "src/resources/__init__.py": '# Resources package\n',

    # Prompts package
    "src/prompts/__init__.py": '# Prompts package\n',

    # Utils package
    "src/utils/__init__.py": '# Utils package\n',

    "src/utils/logging_setup.py": '''"""
Logging Setup
=============
Centralized logging configuration for the server.
"""

import logging
import sys


def setup_logging(level="INFO"):
    """Set up logging with console and file handlers."""
    logger = logging.getLogger("mcp_server")
    logger.setLevel(getattr(logging, level))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
''',

    # Test files
    "tests/__init__.py": '# Tests package\n',

    "tests/unit/__init__.py": '# Unit tests\n',

    "tests/unit/test_calculator.py": '''"""
Unit Tests for Calculator Tools
================================
"""

from src.tools.calculator import add, subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    print("test_add passed!")


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 0) == 0
    print("test_subtract passed!")


if __name__ == "__main__":
    test_add()
    test_subtract()
    print("All tests passed!")
''',

    "tests/integration/__init__.py": '# Integration tests\n',

    # Configuration
    "config/default.json": '{\n    "server_name": "my-production-server",\n    "log_level": "INFO",\n    "transport": "stdio"\n}\n',

    # Git ignore for logs
    "logs/.gitkeep": '',

    # README
    "README.md": '# My Production MCP Server\n\nA production-grade MCP server.\n\n## Setup\n\n```bash\npoetry install\npoetry shell\npython src/server.py\n```\n',

    # Environment template
    ".env.example": '# Environment variables\nMCP_SERVER_NAME=my-production-server\nMCP_LOG_LEVEL=INFO\nMCP_ENVIRONMENT=development\n',
}

# ============================================================
# STEP 3: Create the directories
# ============================================================


def create_project():
    """Create the production project structure."""

    print("=" * 50)
    print("Creating Production MCP Server Structure")
    print("=" * 50)
    print(f"\nProject location: {project_dir}\n")

    # Create base directory
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        print(f"Created: {project_dir}")
    else:
        print(f"Directory already exists: {project_dir}")

    # Create all subdirectories
    print("\n--- Creating directories ---")
    for directory in directories:
        dir_path = os.path.join(project_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"  Created: {directory}/")
        else:
            print(f"  Exists:  {directory}/")

    # Create all template files
    print("\n--- Creating template files ---")
    for file_path, content in template_files.items():
        full_path = os.path.join(project_dir, file_path)

        # Make sure the parent directory exists
        parent_dir = os.path.dirname(full_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # Write the file
        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Created: {file_path}")
        else:
            print(f"  Exists:  {file_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("Project structure created successfully!")
    print("=" * 50)
    print(f"\nNext steps:")
    print(f"  cd {project_dir}")
    print(f"  poetry init --name my-production-server --python \"^3.11\" --no-interaction")
    print(f"  poetry add mcp")
    print(f"  poetry install")
    print(f"  poetry shell")
    print(f"  python src/server.py")


# ============================================================
# STEP 4: Run the script
# ============================================================

if __name__ == "__main__":
    create_project()
