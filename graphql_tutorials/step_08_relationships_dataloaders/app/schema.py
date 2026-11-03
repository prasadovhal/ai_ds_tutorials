from enum import Enum

import strawberry
from strawberry.types import Info

from .dataloaders import Loaders
from .models import AuthorModel, BookModel, ReviewModel


@strawberry.enum
class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"


@strawberry.type
class Author:
    id: strawberry.ID
    name: str
    bio: str | None

    @strawberry.field
    async def books(self, info: Info) -> list["Book"]:
        loaders: Loaders = info.context["loaders"]
        rows = await loaders.books_by_author_loader.load(int(self.id))
        return [_book_from_row(r) for r in rows]


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
    genre: Genre
    _author_id: strawberry.Private[int]

    @strawberry.field
    async def author(self, info: Info) -> Author:
        loaders: Loaders = info.context["loaders"]
        row = await loaders.author_loader.load(self._author_id)
        return _author_from_row(row)

    @strawberry.field
    async def reviews(self, info: Info) -> list["Review"]:
        loaders: Loaders = info.context["loaders"]
        rows = await loaders.reviews_by_book_loader.load(int(self.id))
        return [_review_from_row(r) for r in rows]

    @strawberry.field
    async def average_rating(self, info: Info) -> float | None:
        loaders: Loaders = info.context["loaders"]
        rows = await loaders.reviews_by_book_loader.load(int(self.id))
        if not rows:
            return None
        return sum(r.rating for r in rows) / len(rows)


@strawberry.type
class Review:
    id: strawberry.ID
    rating: int
    comment: str
    _book_id: strawberry.Private[int]

    @strawberry.field
    async def book(self, info: Info) -> Book:
        db = info.context["db"]
        row = db.query(BookModel).get(self._book_id)
        return _book_from_row(row)


# --- Helpers ---


def _author_from_row(row: AuthorModel) -> Author:
    return Author(id=strawberry.ID(str(row.id)), name=row.name, bio=row.bio)


def _book_from_row(row: BookModel) -> Book:
    return Book(
        id=strawberry.ID(str(row.id)),
        title=row.title,
        year=row.year,
        genre=Genre(row.genre),
        _author_id=row.author_id,
    )


def _review_from_row(row: ReviewModel) -> Review:
    return Review(
        id=strawberry.ID(str(row.id)),
        rating=row.rating,
        comment=row.comment,
        _book_id=row.book_id,
    )


# --- Input Types ---


@strawberry.input
class BookInput:
    title: str
    author_id: strawberry.ID
    year: int
    genre: Genre


@strawberry.input
class ReviewInput:
    book_id: strawberry.ID
    rating: int
    comment: str


# --- Queries ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self, info: Info) -> list[Book]:
        db = info.context["db"]
        rows = db.query(BookModel).all()
        return [_book_from_row(r) for r in rows]

    @strawberry.field
    def book(self, info: Info, id: strawberry.ID) -> Book | None:
        db = info.context["db"]
        row = db.query(BookModel).get(int(id))
        return _book_from_row(row) if row else None

    @strawberry.field
    def authors(self, info: Info) -> list[Author]:
        db = info.context["db"]
        rows = db.query(AuthorModel).all()
        return [_author_from_row(r) for r in rows]


# --- Mutations ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, info: Info, input: BookInput) -> Book:
        db = info.context["db"]
        book = BookModel(
            title=input.title,
            year=input.year,
            genre=input.genre.value,
            author_id=int(input.author_id),
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return _book_from_row(book)

    @strawberry.mutation
    def add_review(self, info: Info, input: ReviewInput) -> Review:
        db = info.context["db"]
        if not 1 <= input.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        review = ReviewModel(
            rating=input.rating,
            comment=input.comment,
            book_id=int(input.book_id),
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return _review_from_row(review)
