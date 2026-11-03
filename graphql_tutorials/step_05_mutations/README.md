# Step 5: Mutations

## What are Mutations?

While **queries** read data, **mutations** write data. They are used to:
- **Create** new records
- **Update** existing records
- **Delete** records

Mutations are like POST/PUT/DELETE in REST.

---

## Mutation Syntax

```graphql
mutation {
  createBook(title: "New Book", author: "Someone", year: 2025) {
    id
    title
  }
}
```

Key differences from queries:
- Keyword is `mutation` instead of `query`
- Mutations **always return data** (so the client knows what changed)
- Mutations run **sequentially** (unlike queries which can run in parallel)

---

## Defining Mutations in Strawberry

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, title: str, author: str, year: int) -> Book:
        book = Book(id=strawberry.ID(str(uuid4())), title=title, ...)
        BOOKS.append(book)
        return book
```

Note: Use `@strawberry.mutation` instead of `@strawberry.field`.

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_05_mutations.app.main:app --reload
```

### Try these mutations:

#### Create a book
```graphql
mutation {
  createBook(title: "The Martian", author: "Andy Weir", year: 2011) {
    id
    title
    author
    year
  }
}
```

#### Update a book
```graphql
mutation {
  updateBook(id: "1", year: 1950) {
    id
    title
    year
  }
}
```

#### Delete a book
```graphql
mutation {
  deleteBook(id: "1") {
    success
    message
  }
}
```

#### Verify changes
```graphql
query {
  books {
    id
    title
    author
    year
  }
}
```

---

## Mutation Response Pattern

Always return meaningful responses from mutations:

```python
@strawberry.type
class DeleteResult:
    success: bool
    message: str
```

This lets clients know if the operation succeeded without making another query.

---

## Important: Mutations are Sequential

If you send multiple mutations in one request, they execute **in order**:

```graphql
mutation {
  first: createBook(title: "Book A", author: "X", year: 2025) { id }
  second: createBook(title: "Book B", author: "Y", year: 2025) { id }
}
```

`first` always completes before `second` starts. This prevents race conditions.

Next: [Step 6 - Input Types & Enums](../step_06_input_types_enums/README.md)
