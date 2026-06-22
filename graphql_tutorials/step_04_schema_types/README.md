# Step 4: Schema & Types Deep Dive

## GraphQL Type System

GraphQL has a strong type system. Every field has a type, and the schema
acts as a contract between client and server.

---

## Scalar Types (Primitives)

| GraphQL Type | Python Type | Example |
|-------------|-------------|---------|
| `String` | `str` | `"hello"` |
| `Int` | `int` | `42` |
| `Float` | `float` | `3.14` |
| `Boolean` | `bool` | `True` |
| `ID` | `strawberry.ID` | `"abc-123"` |

```python
@strawberry.type
class Example:
    name: str           # String! (non-nullable)
    age: int            # Int!
    score: float        # Float!
    active: bool        # Boolean!
    id: strawberry.ID   # ID!
```

---

## Nullability

```python
@strawberry.type
class User:
    name: str              # String!  -> REQUIRED, never null
    bio: str | None        # String   -> OPTIONAL, can be null
    posts: list[str]       # [String!]! -> Required list of required strings
    tags: list[str] | None # [String!]  -> Optional list of required strings
```

Key rule: `!` in GraphQL means non-nullable. In Python, use `| None` to make
fields nullable.

---

## Object Types

Object types represent complex objects with multiple fields:

```python
@strawberry.type
class Author:
    id: strawberry.ID
    name: str
    bio: str | None = None

@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
    author: Author         # Nested object type
    genres: list[str]      # List of scalars
```

---

## Enum Types

Enums restrict a field to a fixed set of values:

```python
@strawberry.enum
class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"

@strawberry.type
class Book:
    title: str
    genre: Genre           # Can only be one of the enum values
```

Query:
```graphql
query {
  books {
    title
    genre           # Returns: FICTION, SCIENCE_FICTION, etc.
  }
}
```

---

## Interface Types

Interfaces define a set of fields that multiple types must implement:

```python
@strawberry.interface
class Node:
    id: strawberry.ID
    created_at: str

@strawberry.type
class Book(Node):        # Must have id and created_at
    title: str

@strawberry.type
class Review(Node):      # Must have id and created_at
    body: str
    rating: int
```

---

## Union Types

A field that can return one of several types:

```python
@strawberry.type
class Book:
    title: str

@strawberry.type
class Author:
    name: str

SearchResult = strawberry.union("SearchResult", types=[Book, Author])

@strawberry.type
class Query:
    @strawberry.field
    def search(self, term: str) -> list[SearchResult]:
        ...
```

Query with unions (must use inline fragments):
```graphql
query {
  search(term: "tolkien") {
    ... on Book {
      title
    }
    ... on Author {
      name
    }
  }
}
```

---

## Custom Scalars

Create your own scalar types for domain-specific data:

```python
import datetime
from strawberry.scalars import JSON

# Strawberry has built-in support for datetime
@strawberry.type
class Event:
    name: str
    date: datetime.date        # Serialized as "2025-01-15"
    timestamp: datetime.datetime  # Serialized as ISO 8601

# JSON scalar for arbitrary data
@strawberry.type
class Config:
    settings: JSON             # Any valid JSON
```

---

## Field Descriptions

Add documentation to your schema (visible in GraphiQL):

```python
@strawberry.type(description="A book in the library catalog")
class Book:
    title: str = strawberry.field(description="The book's title")
    year: int = strawberry.field(description="Year of first publication")
```

---

## Deprecation

Mark fields as deprecated to signal they'll be removed:

```python
@strawberry.type
class Book:
    title: str
    name: str = strawberry.field(
        deprecation_reason="Use 'title' instead"
    )
```

---

## Run This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_04_schema_types.app.main:app --reload
```

### Try these queries:

```graphql
# Query with enums
query {
  booksByGenre(genre: SCIENCE_FICTION) {
    title
    author { name }
    genre
  }
}

# Search returning union types
query {
  search(term: "tolkien") {
    ... on Book { title }
    ... on Author { name bio }
  }
}
```

Next: [Step 5 - Mutations](../step_05_mutations/README.md)
