# GraphQL with Python - Complete Tutorial (Basic to Advanced)

A hands-on, step-by-step tutorial to learn GraphQL using Python, Strawberry, FastAPI, and Poetry.

## Prerequisites

- Python 3.10+
- Basic Python knowledge
- Familiarity with REST APIs (helpful, not required)

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Programming language |
| **Poetry** | Dependency management |
| **Strawberry** | Python GraphQL library (type-safe, modern) |
| **FastAPI** | Web framework |
| **SQLAlchemy** | ORM / Database |
| **SQLite** | Database (for learning; swap for PostgreSQL in production) |
| **Rover CLI** | GraphQL schema management and validation |
| **Docker** | Containerization for deployment |

## Tutorial Steps

| # | Topic | What You'll Learn |
|---|-------|-------------------|
| 01 | [What is GraphQL?](step_01_what_is_graphql/README.md) | GraphQL concepts, REST vs GraphQL, when to use it |
| 02 | [Project Setup with Poetry](step_02_setup_project/README.md) | Poetry init, dependencies, project structure |
| 03 | [Your First Query](step_03_first_query/README.md) | Schema, resolvers, running the server, GraphiQL |
| 04 | [Schema & Types Deep Dive](step_04_schema_types/README.md) | Scalar types, object types, lists, optionals, interfaces |
| 05 | [Mutations](step_05_mutations/README.md) | Creating, updating, deleting data |
| 06 | [Input Types & Enums](step_06_input_types_enums/README.md) | Input validation, enums, custom scalars |
| 07 | [Database with SQLAlchemy](step_07_database_sqlalchemy/README.md) | Models, sessions, CRUD with real database |
| 08 | [Relationships & DataLoaders](step_08_relationships_dataloaders/README.md) | One-to-many, many-to-many, solving N+1 problem |
| 09 | [Authentication & Authorization](step_09_authentication/README.md) | JWT auth, context, permission classes |
| 10 | [Subscriptions](step_10_subscriptions/README.md) | Real-time data with WebSockets |
| 11 | [Pagination & Filtering](step_11_pagination_filtering/README.md) | Cursor/offset pagination, search, sorting |
| 12 | [Error Handling](step_12_error_handling/README.md) | Custom errors, validation, union error types |
| 13 | [File Uploads](step_13_file_uploads/README.md) | Multipart uploads via GraphQL |
| 14 | [Testing](step_14_testing/README.md) | Unit tests, integration tests, pytest |
| 15 | [Rover CLI](step_15_rover_cli/README.md) | Schema validation, linting, publishing, CI/CD |
| 16 | [Deployment](step_16_deployment/README.md) | Docker, environment config, production checklist |

## Quick Start

```bash
# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and install all dependencies once
git clone <this-repo-url>
cd graphql_tutorials
poetry install

# Run any step (e.g., step 03)
poetry run uvicorn step_03_first_query.app.main:app --reload

# Open GraphiQL playground
# http://localhost:8000/graphql
```

## How to Use This Tutorial

1. **Read each step's README.md** - it explains the concepts
2. **Look at the code** - each step has working, runnable code
3. **Run it yourself** - use `poetry run uvicorn step_XX_name.app.main:app --reload`
4. **Experiment** - modify the code, break things, learn

There is a single `pyproject.toml` at the project root with all dependencies.
Run `poetry install` once, then run any step using its module path.
