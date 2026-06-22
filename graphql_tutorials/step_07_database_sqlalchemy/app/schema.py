from enum import Enum

import strawberry
from strawberry.types import Info

from .models import AuthorModel, BookModel, ReviewModel


# --- Enums ---


@strawberry.enum
class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"


# --- GraphQL Types ---


@strawberry.type
class Author:
    id: strawberry.ID
    name: str
    bio: str | None

    @strawberry.field
    def books(self, info: Info) -> list["Book"]:
        db = info.context["db"]
        rows = db.query(BookModel).filter(BookModel.author_id == int(self.id)).all()
        return [_book_from_row(row) for row in rows]


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
    genre: Genre

    _author_id: strawberry.Private[int]

    @strawberry.field
    def author(self, info: Info) -> Author:
        db = info.context["db"]
        row = db.query(AuthorModel).get(self._author_id)
        return Author(id=strawberry.ID(str(row.id)), name=row.name, bio=row.bio)

    @strawberry.field
    def reviews(self, info: Info) -> list["Review"]:
        db = info.context["db"]
        rows = db.query(ReviewModel).filter(ReviewModel.book_id == int(self.id)).all()
        return [_review_from_row(row) for row in rows]


@strawberry.type
class Review:
    id: strawberry.ID
    rating: int
    comment: str
    _book_id: strawberry.Private[int]

    @strawberry.field
    def book(self, info: Info) -> Book:
        db = info.context["db"]
        row = db.query(BookModel).get(self._book_id)
        return _book_from_row(row)


@strawberry.type
class DeleteResult:
    success: bool
    message: str


# --- Input Types ---


@strawberry.input
class AuthorInput:
    name: str
    bio: str | None = None


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


# --- Helpers ---


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
    def books_by_genre(self, info: Info, genre: Genre) -> list[Book]:
        db = info.context["db"]
        rows = db.query(BookModel).filter(BookModel.genre == genre.value).all()
        return [_book_from_row(r) for r in rows]

    @strawberry.field
    def authors(self, info: Info) -> list[Author]:
        db = info.context["db"]
        rows = db.query(AuthorModel).all()
        return [
            Author(id=strawberry.ID(str(r.id)), name=r.name, bio=r.bio) for r in rows
        ]


# --- Mutations ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_author(self, info: Info, input: AuthorInput) -> Author:
        db = info.context["db"]
        author = AuthorModel(name=input.name, bio=input.bio)
        db.add(author)
        db.commit()
        db.refresh(author)
        return Author(
            id=strawberry.ID(str(author.id)), name=author.name, bio=author.bio
        )

    @strawberry.mutation
    def create_book(self, info: Info, input: BookInput) -> Book:
        db = info.context["db"]
        author = db.query(AuthorModel).get(int(input.author_id))
        if not author:
            raise ValueError(f"Author with id {input.author_id} not found")

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
        book = db.query(BookModel).get(int(input.book_id))
        if not book:
            raise ValueError(f"Book with id {input.book_id} not found")
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

    @strawberry.mutation
    def delete_book(self, info: Info, id: strawberry.ID) -> DeleteResult:
        db = info.context["db"]
        book = db.query(BookModel).get(int(id))
        if not book:
            return DeleteResult(success=False, message=f"Book '{id}' not found")
        title = book.title
        db.delete(book)
        db.commit()
        return DeleteResult(success=True, message=f"Deleted '{title}'")
