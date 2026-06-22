# Step 7: Database with SQLAlchemy

## Why a Real Database?

So far we used in-memory lists/dicts. Problems:
- Data disappears when the server restarts
- No concurrent access safety
- No relationships or constraints

Now we'll use **SQLAlchemy** (Python's most popular ORM) with **SQLite**.

---

## Architecture

```
GraphQL Query/Mutation
        |
   Strawberry Resolver
        |
   SQLAlchemy Session
        |
   SQLite Database (books.db)
```

---

## Project Structure

```
step_07_database_sqlalchemy/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI + Strawberry setup
│   ├── database.py        # SQLAlchemy engine & session
│   ├── models.py          # Database models (tables)
│   ├── schema.py          # GraphQL types, queries, mutations
│   └── seed.py            # Seed data for testing
└── pyproject.toml
```

---

## Key Concepts

### 1. Database Models (SQLAlchemy)
These define your **database tables**:

```python
class BookModel(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    year = Column(Integer)
```

### 2. GraphQL Types (Strawberry)
These define your **API response shape**:

```python
@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
```

### 3. The Resolver bridges them:
```python
@strawberry.field
def books(self, info: strawberry.types.Info) -> list[Book]:
    db = info.context["db"]
    rows = db.query(BookModel).all()
    return [Book(id=r.id, title=r.title, year=r.year) for r in rows]
```

### 4. Context
The `info.context` dict is how we pass the database session to resolvers.
FastAPI sets it up via a custom context getter.

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)

# Seed the database with sample data
poetry run python -m step_07_database_sqlalchemy.app.seed

# Start the server
poetry run uvicorn step_07_database_sqlalchemy.app.main:app --reload
```

### Queries to try:

```graphql
# All books with their authors
query {
  books {
    id
    title
    year
    genre
    author {
      name
    }
  }
}

# Create a new author
mutation {
  createAuthor(input: { name: "Andy Weir", bio: "Sci-fi author" }) {
    id
    name
  }
}

# Create a book for that author (use the ID returned above)
mutation {
  createBook(input: {
    title: "The Martian"
    authorId: "5"
    year: 2011
    genre: SCIENCE_FICTION
  }) {
    id
    title
    author { name }
  }
}
```

### Restart the server - your data persists!

Next: [Step 8 - Relationships & DataLoaders](../step_08_relationships_dataloaders/README.md)
