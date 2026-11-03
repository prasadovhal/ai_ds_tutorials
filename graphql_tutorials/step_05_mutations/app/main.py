from uuid import uuid4

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# --- In-Memory Data ---

BOOKS_DATA: list[dict] = [
    {"id": "1", "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": "2", "title": "Dune", "author": "Frank Herbert", "year": 1965},
    {"id": "3", "title": "The Hobbit", "author": "J.R.R. Tolkien", "year": 1937},
]


# --- GraphQL Types ---


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    author: str
    year: int


@strawberry.type
class DeleteResult:
    success: bool
    message: str


# --- Queries ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return [Book(**b) for b in BOOKS_DATA]

    @strawberry.field
    def book(self, id: strawberry.ID) -> Book | None:
        for b in BOOKS_DATA:
            if b["id"] == id:
                return Book(**b)
        return None


# --- Mutations ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, title: str, author: str, year: int) -> Book:
        """Create a new book and return it."""
        book_data = {
            "id": str(uuid4()),
            "title": title,
            "author": author,
            "year": year,
        }
        BOOKS_DATA.append(book_data)
        return Book(**book_data)

    @strawberry.mutation
    def update_book(
        self,
        id: strawberry.ID,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
    ) -> Book | None:
        """Update an existing book. Only provided fields are changed."""
        for book_data in BOOKS_DATA:
            if book_data["id"] == id:
                if title is not None:
                    book_data["title"] = title
                if author is not None:
                    book_data["author"] = author
                if year is not None:
                    book_data["year"] = year
                return Book(**book_data)
        return None

    @strawberry.mutation
    def delete_book(self, id: strawberry.ID) -> DeleteResult:
        """Delete a book by ID."""
        for i, book_data in enumerate(BOOKS_DATA):
            if book_data["id"] == id:
                BOOKS_DATA.pop(i)
                return DeleteResult(success=True, message=f"Book '{id}' deleted")
        return DeleteResult(success=False, message=f"Book '{id}' not found")


# --- App Setup ---

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 05")
app.include_router(graphql_app, prefix="/graphql")
