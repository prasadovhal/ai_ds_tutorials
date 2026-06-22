# Step 15: Rover CLI

## What is Rover?

**Rover** is the official CLI tool from **Apollo** for managing GraphQL schemas.
It's the Swiss Army knife for GraphQL schema management.

Think of it as:
- **Schema linter** - catches mistakes before they reach production
- **Schema validator** - ensures backward compatibility
- **Schema publisher** - pushes schemas to Apollo GraphOS (schema registry)
- **Schema introspector** - fetches schemas from running servers
- **Subgraph manager** - for federated GraphQL (microservices)

---

## Install Rover

```bash
# Windows (PowerShell)
iwr 'https://rover.apollo.dev/win/latest' | iex

# macOS
curl -sSL https://rover.apollo.dev/nix/latest | sh

# npm (cross-platform)
npm install -g @apollo/rover

# Verify
rover --version
```

---

## Core Rover Commands

### 1. `rover graph introspect` - Fetch Schema from Running Server

```bash
# Start your server first, then:
rover graph introspect http://localhost:8000/graphql
```

This connects to your running server and outputs the full SDL (Schema Definition
Language). Useful to:
- See your schema in SDL format
- Save it to a file for version control
- Compare schemas between environments

```bash
# Save to file
rover graph introspect http://localhost:8000/graphql > schema.graphql

# Output:
# type Query {
#   books: [Book!]!
#   book(id: ID!): Book
# }
# type Book {
#   id: ID!
#   title: String!
#   ...
# }
```

### 2. `rover graph check` - Validate Schema Changes

```bash
# Check schema against Apollo GraphOS registry
rover graph check my-graph@production --schema schema.graphql
```

This compares your local schema against the published schema and reports:
- **Breaking changes** (removed fields, changed types)
- **Non-breaking changes** (added fields, new types)
- **Usage data** (if connected to Apollo Studio, shows which clients use changed fields)

### 3. `rover graph publish` - Publish Schema

```bash
# Publish schema to Apollo GraphOS
rover graph publish my-graph@production --schema schema.graphql
```

### 4. `rover supergraph compose` - Federation

```bash
# Compose multiple subgraph schemas into a supergraph
rover supergraph compose --config supergraph.yaml > supergraph.graphql
```

### 5. `rover dev` - Local Development

```bash
# Start a local router that watches for schema changes
rover dev --supergraph-config supergraph.yaml
```

---

## Using Rover Without Apollo GraphOS

You don't need an Apollo account to use Rover's most useful features:

### Introspect any GraphQL API
```bash
# Your local server
rover graph introspect http://localhost:8000/graphql

# Any public GraphQL API
rover graph introspect https://countries.trevorblades.com/graphql

# With headers (for authenticated APIs)
rover graph introspect http://localhost:8000/graphql \
  --header "Authorization: Bearer <token>"
```

### Lint your schema file
```bash
# Export your schema
rover graph introspect http://localhost:8000/graphql > schema.graphql

# Check the schema file is valid SDL
rover graph lint --schema schema.graphql
```

---

## Practical Workflow with Rover

### Step 1: Export your schema
```bash
# From the project root (graphql_tutorials/)

# Start the server
poetry run uvicorn step_15_rover_cli.app.main:app --port 8000 &

# Introspect and save
rover graph introspect http://localhost:8000/graphql > schema.graphql
```

### Step 2: Review the schema
```bash
cat schema.graphql
```

### Step 3: Make changes to your code

Edit `app/main.py` - add a new field, change a type, etc.

### Step 4: Compare schemas
```bash
# Get the new schema
rover graph introspect http://localhost:8000/graphql > schema_new.graphql

# Diff them
diff schema.graphql schema_new.graphql
```

### Step 5: Validate in CI/CD
```bash
# In your CI pipeline:
rover graph introspect http://localhost:8000/graphql > current.graphql
# Compare against the committed schema
diff schema.graphql current.graphql
```

---

## Rover in CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/schema-check.yml
name: Schema Check

on: [pull_request]

jobs:
  check-schema:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rover
        run: |
          curl -sSL https://rover.apollo.dev/nix/latest | sh
          echo "$HOME/.rover/bin" >> $GITHUB_PATH

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Start server
        run: |
          poetry run uvicorn step_15_rover_cli.app.main:app --port 8000 &
          sleep 3

      - name: Introspect and compare
        run: |
          rover graph introspect http://localhost:8000/graphql > current_schema.graphql
          diff schema.graphql current_schema.graphql || echo "Schema has changed!"
```

### With Apollo GraphOS (optional, paid)

```yaml
      - name: Check schema
        env:
          APOLLO_KEY: ${{ secrets.APOLLO_KEY }}
        run: |
          rover graph check my-graph@production \
            --schema schema.graphql
```

---

## Federation with Rover (Advanced)

When your GraphQL API grows, you might split it into **subgraphs**
(microservices), each owning part of the schema.

```yaml
# supergraph.yaml
federation_version: =2.7.1
subgraphs:
  books:
    routing_url: http://books-service:4001/graphql
    schema:
      file: ./books/schema.graphql
  reviews:
    routing_url: http://reviews-service:4002/graphql
    schema:
      file: ./reviews/schema.graphql
  users:
    routing_url: http://users-service:4003/graphql
    schema:
      file: ./users/schema.graphql
```

```bash
# Compose into a supergraph schema
rover supergraph compose --config supergraph.yaml > supergraph.graphql

# Start a local federated gateway
rover dev --supergraph-config supergraph.yaml
```

---

## Quick Reference

| Command | What it does | Needs Apollo account? |
|---------|-------------|----------------------|
| `rover graph introspect <url>` | Fetch schema from server | No |
| `rover graph introspect <url> > schema.graphql` | Save schema to file | No |
| `rover graph lint --schema <file>` | Validate schema syntax | No |
| `rover graph check <graph>@<variant> --schema <file>` | Check for breaking changes | Yes |
| `rover graph publish <graph>@<variant> --schema <file>` | Publish to registry | Yes |
| `rover supergraph compose --config <file>` | Compose federated schema | No |
| `rover dev` | Local federated dev server | No |

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_15_rover_cli.app.main:app --reload --port 8000

# In another terminal:
rover graph introspect http://localhost:8000/graphql
rover graph introspect http://localhost:8000/graphql > schema.graphql
cat schema.graphql
```

The `schema.graphql` file in this directory is the exported schema from our API.
Compare it with the running server's schema to verify they match.

Next: [Step 16 - Deployment](../step_16_deployment/README.md)
