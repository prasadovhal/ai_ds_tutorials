from uuid import uuid4

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# --- Data ---

AUTHORS = {"1": "George Orwell", "2": "Frank Herbert"}
BOOKS: dict[str, dict] = {
    "1": {"id": "1", "title": "1984", "year": 1949, "author_id": "1"},
    "2": {"id": "2", "title": "Dune", "year": 1965, "author_id": "2"},
}


# --- Error Types ---


@strawberry.type
class ValidationError:
    """Returned when input data fails validation."""

    message: str
    field: str


@strawberry.type
class NotFoundError:
    """Returned when a referenced entity doesn't exist."""

    message: str
    entity_id: str


@strawberry.type
class PermissionError:
    """Returned when the user lacks permission."""

    message: str


# --- Success Types ---


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
    author_name: str


@strawberry.type
class DeleteSuccess:
    message: str
    deleted_id: str


# --- Union Result Types ---

CreateBookResult = strawberry.union(
    "CreateBookResult", types=(Book, ValidationError, NotFoundError)
)

DeleteBookResult = strawberry.union(
    "DeleteBookResult", types=(DeleteSuccess, NotFoundError, PermissionError)
)


# --- Input ---


@strawberry.input
class BookInput:
    title: str
    author_id: str
    year: int


# --- Query ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return [
            Book(
                id=strawberry.ID(b["id"]),
                title=b["title"],
                year=b["year"],
                author_name=AUTHORS.get(b["author_id"], "Unknown"),
            )
            for b in BOOKS.values()
        ]


# --- Mutation ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, input: BookInput) -> CreateBookResult:
        if not input.title.strip():
            return ValidationError(message="Title cannot be empty", field="title")

        if input.year < 0 or input.year > 2030:
            return ValidationError(
                message="Year must be between 0 and 2030", field="year"
            )

        if input.author_id not in AUTHORS:
            return NotFoundError(
                message=f"Author with id '{input.author_id}' not found",
                entity_id=input.author_id,
            )

        book_id = str(uuid4())[:8]
        BOOKS[book_id] = {
            "id": book_id,
            "title": input.title.strip(),
            "year": input.year,
            "author_id": input.author_id,
        }
        return Book(
            id=strawberry.ID(book_id),
            title=input.title.strip(),
            year=input.year,
            author_name=AUTHORS[input.author_id],
        )

    @strawberry.mutation
    def delete_book(self, id: str) -> DeleteBookResult:
        if id not in BOOKS:
            return NotFoundError(
                message=f"Book '{id}' not found", entity_id=id
            )

        title = BOOKS.pop(id)["title"]
        return DeleteSuccess(message=f"Deleted '{title}'", deleted_id=id)


# --- App ---

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 12")
app.include_router(graphql_app, prefix="/graphql")
