from enum import Enum
from uuid import uuid4

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# --- Enums ---


@strawberry.enum
class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    HORROR = "horror"


# --- Object Types (Output) ---


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
    genre: Genre
    tags: list[str]
    author: Author


@strawberry.type
class Review:
    id: strawberry.ID
    rating: int
    comment: str
    book: Book


@strawberry.type
class DeleteResult:
    success: bool
    message: str


# --- Input Types ---


@strawberry.input(description="Input for creating a new book")
class BookInput:
    title: str
    author_id: strawberry.ID
    year: int
    genre: Genre
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input(description="Input for updating a book (all fields optional)")
class BookUpdateInput:
    title: str | None = None
    year: int | None = None
    genre: Genre | None = None
    tags: list[str] | None = None


@strawberry.input(description="Input for adding a review")
class ReviewInput:
    book_id: strawberry.ID
    rating: int = strawberry.field(description="Rating from 1 to 5")
    comment: str


# --- In-Memory Data ---

AUTHORS_DB: dict[str, dict] = {
    "1": {"id": "1", "name": "George Orwell", "bio": "English novelist"},
    "2": {"id": "2", "name": "Frank Herbert", "bio": "American sci-fi author"},
    "3": {"id": "3", "name": "J.R.R. Tolkien", "bio": "Father of modern fantasy"},
}

BOOKS_DB: dict[str, dict] = {
    "1": {
        "id": "1",
        "title": "1984",
        "year": 1949,
        "genre": Genre.FICTION,
        "tags": ["dystopia", "politics"],
        "author_id": "1",
    },
    "2": {
        "id": "2",
        "title": "Dune",
        "year": 1965,
        "genre": Genre.SCIENCE_FICTION,
        "tags": ["space", "ecology"],
        "author_id": "2",
    },
    "3": {
        "id": "3",
        "title": "The Hobbit",
        "year": 1937,
        "genre": Genre.FANTASY,
        "tags": ["adventure", "dragons"],
        "author_id": "3",
    },
}

REVIEWS_DB: dict[str, dict] = {}


# --- Helpers ---


def get_author_type(author_id: str) -> Author:
    a = AUTHORS_DB[author_id]
    return Author(**a)


def get_book_type(book_id: str) -> Book:
    b = BOOKS_DB[book_id]
    return Book(
        id=strawberry.ID(b["id"]),
        title=b["title"],
        year=b["year"],
        genre=b["genre"],
        tags=b["tags"],
        author=get_author_type(b["author_id"]),
    )


# --- Query ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return [get_book_type(bid) for bid in BOOKS_DB]

    @strawberry.field
    def book(self, id: strawberry.ID) -> Book | None:
        if id in BOOKS_DB:
            return get_book_type(id)
        return None

    @strawberry.field
    def books_by_genre(self, genre: Genre) -> list[Book]:
        return [
            get_book_type(bid)
            for bid, b in BOOKS_DB.items()
            if b["genre"] == genre
        ]

    @strawberry.field
    def reviews(self, book_id: strawberry.ID) -> list[Review]:
        return [
            Review(
                id=strawberry.ID(r["id"]),
                rating=r["rating"],
                comment=r["comment"],
                book=get_book_type(r["book_id"]),
            )
            for r in REVIEWS_DB.values()
            if r["book_id"] == book_id
        ]


# --- Mutation ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, input: BookInput) -> Book:
        if input.author_id not in AUTHORS_DB:
            raise ValueError(f"Author '{input.author_id}' not found")

        book_id = str(uuid4())
        BOOKS_DB[book_id] = {
            "id": book_id,
            "title": input.title,
            "year": input.year,
            "genre": input.genre,
            "tags": input.tags,
            "author_id": input.author_id,
        }
        return get_book_type(book_id)

    @strawberry.mutation
    def update_book(self, id: strawberry.ID, input: BookUpdateInput) -> Book | None:
        if id not in BOOKS_DB:
            return None

        book = BOOKS_DB[id]
        if input.title is not None:
            book["title"] = input.title
        if input.year is not None:
            book["year"] = input.year
        if input.genre is not None:
            book["genre"] = input.genre
        if input.tags is not None:
            book["tags"] = input.tags
        return get_book_type(id)

    @strawberry.mutation
    def delete_book(self, id: strawberry.ID) -> DeleteResult:
        if id in BOOKS_DB:
            title = BOOKS_DB.pop(id)["title"]
            return DeleteResult(success=True, message=f"Deleted '{title}'")
        return DeleteResult(success=False, message=f"Book '{id}' not found")

    @strawberry.mutation
    def add_review(self, input: ReviewInput) -> Review:
        if input.book_id not in BOOKS_DB:
            raise ValueError(f"Book '{input.book_id}' not found")
        if not 1 <= input.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        review_id = str(uuid4())
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
            book=get_book_type(input.book_id),
        )


# --- App Setup ---

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 06")
app.include_router(graphql_app, prefix="/graphql")
