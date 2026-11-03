import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# --- Data Layer (in-memory for now) ---

BOOKS_DATA = [
    {"title": "1984", "author": "George Orwell", "year": 1949},
    {"title": "Dune", "author": "Frank Herbert", "year": 1965},
    {"title": "Neuromancer", "author": "William Gibson", "year": 1984},
    {"title": "Foundation", "author": "Isaac Asimov", "year": 1951},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "year": 1937},
]


# --- GraphQL Types ---


@strawberry.type
class Book:
    title: str
    author: str
    year: int


# --- Query Resolvers ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self, limit: int | None = None) -> list[Book]:
        """Get all books, optionally limited to N results."""
        data = BOOKS_DATA[:limit] if limit else BOOKS_DATA
        return [Book(**b) for b in data]

    @strawberry.field
    def book(self, title: str) -> Book | None:
        """Get a single book by title."""
        for b in BOOKS_DATA:
            if b["title"].lower() == title.lower():
                return Book(**b)
        return None

    @strawberry.field
    def books_by_author(self, author: str) -> list[Book]:
        """Get all books by a specific author."""
        return [
            Book(**b)
            for b in BOOKS_DATA
            if author.lower() in b["author"].lower()
        ]


# --- App Setup ---

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 03")
app.include_router(graphql_app, prefix="/graphql")
