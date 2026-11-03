# Step 3: Your First Query

## How GraphQL Queries Work

```
Client                    Server
  |                         |
  |--- GraphQL Query ------>|
  |    "Give me books"      |
  |                         |--- Schema: Is this valid?
  |                         |--- Resolver: Fetch the data
  |                         |
  |<-- JSON Response -------|
  |    { data: { ... } }    |
```

1. Client sends a **query string** via HTTP POST
2. Server **validates** the query against the schema
3. Server runs **resolver functions** to fetch data
4. Server returns **JSON** with exactly the requested fields

---

## Building Our First Query

### The Schema (what data is available)

```python
@strawberry.type
class Book:
    title: str
    author: str
    year: int
```

This creates the GraphQL type:
```graphql
type Book {
  title: String!
  author: String!
  year: Int!
}
```

### The Resolver (how to fetch data)

```python
@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return [
            Book(title="1984", author="George Orwell", year=1949),
            Book(title="Dune", author="Frank Herbert", year=1965),
        ]
```

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_03_first_query.app.main:app --reload
```

Open **http://localhost:8000/graphql** and try these queries:

### Query 1: Get all books
```graphql
query {
  books {
    title
    author
    year
  }
}
```

### Query 2: Get only titles (no over-fetching!)
```graphql
query {
  books {
    title
  }
}
```

### Query 3: Get a specific book
```graphql
query {
  book(title: "1984") {
    title
    author
    year
  }
}
```

### Query 4: Use variables (best practice)
```graphql
query GetBook($title: String!) {
  book(title: $title) {
    title
    author
    year
  }
}
```

Variables panel (in GraphiQL):
```json
{
  "title": "Dune"
}
```

### Query 5: Aliases (rename fields in response)
```graphql
query {
  scifi: book(title: "Dune") {
    title
    year
  }
  dystopia: book(title: "1984") {
    title
    year
  }
}
```

### Query 6: Fragments (reuse field selections)
```graphql
fragment BookInfo on Book {
  title
  author
  year
}

query {
  books {
    ...BookInfo
  }
  book(title: "1984") {
    ...BookInfo
  }
}
```

---

## Understanding the Code

### `@strawberry.type` - Defines a GraphQL Type
Strawberry uses Python dataclass-style classes. Each class attribute
becomes a field in the GraphQL schema.

### `@strawberry.field` - Defines a Resolver
Methods decorated with `@strawberry.field` become queryable fields.
The return type annotation tells GraphQL what type the field returns.

### Arguments
Method parameters automatically become GraphQL arguments:

```python
@strawberry.field
def book(self, title: str) -> Book | None:
    #            ^^^^^^^^^^
    # This becomes: book(title: String!): Book
```

### Optional vs Required
```python
# Required argument (no default)
def book(self, title: str) -> Book | None: ...

# Optional argument (has default)
def books(self, limit: int = 10) -> list[Book]: ...
```

---

## What is GraphiQL?

GraphiQL (pronounced "graphical") is an **interactive IDE** for GraphQL that
runs in your browser. It provides:

- **Auto-complete**: Press Ctrl+Space to see available fields
- **Documentation**: Click "Docs" sidebar to explore the schema
- **Validation**: Red underlines for invalid queries
- **History**: Previous queries are saved
- **Variables panel**: Pass dynamic values to queries

Strawberry includes GraphiQL automatically at your `/graphql` endpoint.

Next: [Step 4 - Schema & Types Deep Dive](../step_04_schema_types/README.md)
