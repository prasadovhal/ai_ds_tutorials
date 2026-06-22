"""Full Book Review API for demonstrating Rover CLI.

Run the server:
    poetry run uvicorn app.main:app --reload

Introspect with Rover:
    rover graph introspect http://localhost:8000/graphql
    rover graph introspect http://localhost:8000/graphql > schema.graphql
"""

from enum import Enum
from uuid import uuid4

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.enum
class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"


@strawberry.type(description="An author in the catalog")
class Author:
    id: strawberry.ID
    name: str = strawberry.field(description="Full name")
    bio: str | None = strawberry.field(default=None, description="Short biography")


@strawberry.type(description="A book in the catalog")
class Book:
    id: strawberry.ID
    title: str = strawberry.field(description="Book title")
    year: int = strawberry.field(description="Year of publication")
    genre: Genre
    author: Author


@strawberry.type
class Review:
    id: strawberry.ID
    rating: int = strawberry.field(description="Rating from 1 to 5")
    comment: str
    book_id: strawberry.ID


@strawberry.input
class BookInput:
    title: str
    author_name: str
    year: int
    genre: Genre


@strawberry.input
class ReviewInput:
    book_id: strawberry.ID
    rating: int
    comment: str


# --- In-Memory Data ---

AUTHORS_DB: dict[str, dict] = {
    "1": {"id": "1", "name": "George Orwell", "bio": "English novelist"},
    "2": {"id": "2", "name": "Frank Herbert", "bio": "Sci-fi author"},
}

BOOKS_DB: dict[str, dict] = {
    "1": {"id": "1", "title": "1984", "year": 1949, "genre": Genre.FICTION, "author_id": "1"},
    "2": {"id": "2", "title": "Dune", "year": 1965, "genre": Genre.SCIENCE_FICTION, "author_id": "2"},
}

REVIEWS_DB: dict[str, dict] = {}


def _make_author(data: dict) -> Author:
    return Author(id=strawberry.ID(data["id"]), name=data["name"], bio=data.get("bio"))


def _make_book(data: dict) -> Book:
    return Book(
        id=strawberry.ID(data["id"]),
        title=data["title"],
        year=data["year"],
        genre=data["genre"],
        author=_make_author(AUTHORS_DB[data["author_id"]]),
    )


@strawberry.type
class Query:
    @strawberry.field(description="Get all books")
    def books(self) -> list[Book]:
        return [_make_book(b) for b in BOOKS_DB.values()]

    @strawberry.field(description="Get a book by ID")
    def book(self, id: strawberry.ID) -> Book | None:
        if id in BOOKS_DB:
            return _make_book(BOOKS_DB[id])
        return None

    @strawberry.field(description="Get all authors")
    def authors(self) -> list[Author]:
        return [_make_author(a) for a in AUTHORS_DB.values()]

    @strawberry.field(description="Get reviews for a book")
    def reviews(self, book_id: strawberry.ID) -> list[Review]:
        return [
            Review(
                id=strawberry.ID(r["id"]),
                rating=r["rating"],
                comment=r["comment"],
                book_id=strawberry.ID(r["book_id"]),
            )
            for r in REVIEWS_DB.values()
            if r["book_id"] == book_id
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Add a new book")
    def create_book(self, input: BookInput) -> Book:
        author_id = str(uuid4())[:8]
        AUTHORS_DB[author_id] = {
            "id": author_id,
            "name": input.author_name,
            "bio": None,
        }
        book_id = str(uuid4())[:8]
        BOOKS_DB[book_id] = {
            "id": book_id,
            "title": input.title,
            "year": input.year,
            "genre": input.genre,
            "author_id": author_id,
        }
        return _make_book(BOOKS_DB[book_id])

    @strawberry.mutation(description="Add a review to a book")
    def add_review(self, input: ReviewInput) -> Review:
        if input.book_id not in BOOKS_DB:
            raise ValueError(f"Book {input.book_id} not found")
        if not 1 <= input.rating <= 5:
            raise ValueError("Rating must be 1-5")
        review_id = str(uuid4())[:8]
        REVIEWS_DB[review_id] = {
            "id": review_id,
            "rating": input.rating,
            "comment": input.comment,
            "book_id": input.book_id,
        }
        return Review(
            id=strawberry.ID(review_id),
            rating=input.rating,
            comment=input.comment,
            book_id=strawberry.ID(input.book_id),
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 15 (Rover CLI)")
app.include_router(graphql_app, prefix="/graphql")
