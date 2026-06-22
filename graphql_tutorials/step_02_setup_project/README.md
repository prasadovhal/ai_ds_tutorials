# Step 2: Project Setup with Poetry

## What is Poetry?

Poetry is a **dependency management and packaging tool** for Python.
Think of it as `npm` for Python - it handles:
- Virtual environments automatically
- Dependency resolution (no conflicts)
- Lock files for reproducible builds
- Building and publishing packages

---

## Install Poetry

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

---

## Create the Project

All dependencies are managed by a single `pyproject.toml` at the project root.

```bash
# From the project root (graphql_tutorials/)
poetry install    # Install everything once
```

### What Gets Installed

```bash
# Core dependencies (already in root pyproject.toml)
strawberry-graphql[fastapi]   # GraphQL library + FastAPI integration
fastapi                       # Web framework
uvicorn[standard]             # ASGI server
sqlalchemy                    # ORM
aiosqlite                     # Async SQLite driver
pyjwt                         # JWT authentication
passlib[bcrypt]               # Password hashing
python-multipart              # File uploads

# Development dependencies
pytest                        # Testing
pytest-asyncio                # Async test support
httpx                         # Test client
ruff                          # Linter + formatter
```

---

## Project Structure

```
graphql_tutorials/
├── pyproject.toml              # Single Poetry config for all steps
├── step_02_setup_project/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI + Strawberry entry point
│   └── README.md
├── step_03_first_query/
│   └── ...
└── ...
```

---

## Understanding pyproject.toml

```toml
[tool.poetry]
name = "book-review-api"
description = "GraphQL Book Review API"
version = "0.1.0"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"                        # Python 3.10 or higher
strawberry-graphql = {extras = ["fastapi"], version = "*"}
fastapi = "*"
uvicorn = {extras = ["standard"], version = "*"}

[tool.poetry.group.dev.dependencies]
pytest = "*"
ruff = "*"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Key Poetry Commands

```bash
poetry install          # Install all dependencies
poetry add <package>    # Add a new dependency
poetry remove <package> # Remove a dependency
poetry shell            # Activate virtual environment
poetry run <command>    # Run a command inside the virtual env
poetry show             # List installed packages
poetry update           # Update dependencies
poetry lock             # Regenerate lock file
```

---

## Run the Server

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_02_setup_project.app.main:app --reload
```

Open your browser to **http://localhost:8000/graphql** - you'll see the
GraphiQL playground where you can write and test queries.

Try this query:
```graphql
query {
  hello
}
```

---

## What Just Happened?

1. **Poetry** created a virtual environment and installed all dependencies
2. **Uvicorn** started an ASGI web server
3. **FastAPI** handles HTTP requests
4. **Strawberry** processes GraphQL queries and returns responses
5. **GraphiQL** gives you an interactive playground in the browser

The `--reload` flag means the server auto-restarts when you change code.

Next: [Step 3 - Your First Query](../step_03_first_query/README.md)
