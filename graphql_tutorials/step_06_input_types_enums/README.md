# Step 6: Input Types & Enums

## Why Input Types?

In Step 5, our `createBook` mutation had many individual arguments:
```graphql
mutation {
  createBook(title: "...", author: "...", year: 2025) { ... }
}
```

With **Input Types**, we group related arguments into a single object:
```graphql
mutation {
  createBook(input: { title: "...", author: "...", year: 2025 }) { ... }
}
```

Benefits:
- **Cleaner API** - fewer arguments per mutation
- **Reusable** - same input type for create and update
- **Easier to extend** - add fields without changing the mutation signature
- **Better validation** - validate the entire input object at once

---

## Defining Input Types

```python
@strawberry.input
class BookInput:
    title: str
    author_id: strawberry.ID
    year: int
    genre: Genre
    tags: list[str] = strawberry.field(default_factory=list)

@strawberry.input
class BookUpdateInput:
    title: str | None = None
    year: int | None = None
    genre: Genre | None = None
```

Key difference from `@strawberry.type`:
- `@strawberry.input` = data going **into** the server (arguments)
- `@strawberry.type` = data coming **out of** the server (responses)

---

## Enums in Mutations

```graphql
mutation {
  createBook(input: {
    title: "Dune"
    authorId: "2"
    year: 1965
    genre: SCIENCE_FICTION
    tags: ["space", "ecology"]
  }) {
    id
    title
    genre
  }
}
```

Enums are passed as plain uppercase identifiers (no quotes).

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_06_input_types_enums.app.main:app --reload
```

### Try these:

#### Create with input type
```graphql
mutation {
  createBook(input: {
    title: "Neuromancer"
    authorId: "1"
    year: 1984
    genre: SCIENCE_FICTION
    tags: ["cyberpunk", "AI"]
  }) {
    id
    title
    genre
    tags
    author { name }
  }
}
```

#### Update with partial input
```graphql
mutation {
  updateBook(id: "1", input: {
    year: 1950
    genre: FICTION
  }) {
    id
    title
    year
    genre
  }
}
```

#### Create a review with rating validation
```graphql
mutation {
  addReview(input: {
    bookId: "1"
    rating: 5
    comment: "A masterpiece of dystopian fiction"
  }) {
    id
    rating
    comment
    book { title }
  }
}
```

#### Query using enum filter
```graphql
query {
  booksByGenre(genre: FANTASY) {
    title
    genre
    author { name }
  }
}
```

Next: [Step 7 - Database with SQLAlchemy](../step_07_database_sqlalchemy/README.md)
