# Step 12: Error Handling

## GraphQL Error Approaches

### 1. Throwing Exceptions (simple)
```python
@strawberry.mutation
def create_book(self, title: str) -> Book:
    if not title:
        raise ValueError("Title is required")
```

Response:
```json
{
  "data": null,
  "errors": [{ "message": "Title is required" }]
}
```

Problems: errors are untyped strings, client can't switch on error kind.

### 2. Union Error Types (recommended)
Model errors as part of the schema using union types:

```python
@strawberry.type
class BookNotFoundError:
    message: str
    book_id: str

@strawberry.type
class ValidationError:
    message: str
    field: str

CreateBookResult = strawberry.union("CreateBookResult", types=[Book, ValidationError])
```

Response:
```json
{
  "data": {
    "createBook": {
      "__typename": "ValidationError",
      "message": "Title is required",
      "field": "title"
    }
  }
}
```

Benefits: errors are typed, self-documenting, client gets auto-complete.

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_12_error_handling.app.main:app --reload
```

### Try these:

#### Successful creation
```graphql
mutation {
  createBook(input: { title: "New Book", authorId: "1", year: 2025 }) {
    ... on Book {
      id
      title
    }
    ... on ValidationError {
      message
      field
    }
    ... on NotFoundError {
      message
      entityId
    }
  }
}
```

#### Validation error
```graphql
mutation {
  createBook(input: { title: "", authorId: "1", year: 2025 }) {
    ... on Book { id title }
    ... on ValidationError { message field }
  }
}
```

#### Not found error
```graphql
mutation {
  createBook(input: { title: "Test", authorId: "999", year: 2025 }) {
    ... on NotFoundError { message entityId }
  }
}
```

#### Use __typename to check which type was returned
```graphql
mutation {
  createBook(input: { title: "Test", authorId: "1", year: 2025 }) {
    __typename
    ... on Book { id title }
    ... on ValidationError { message field }
    ... on NotFoundError { message }
  }
}
```

Next: [Step 13 - File Uploads](../step_13_file_uploads/README.md)
