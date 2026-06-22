import datetime
from enum import Enum

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON


# --- Enum Types ---


@strawberry.enum
class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"


# --- Object Types ---


@strawberry.type(description="An author who writes books")
class Author:
    id: strawberry.ID
    name: str = strawberry.field(description="Author's full name")
    bio: str | None = None


@strawberry.type(description="A book in the library catalog")
class Book:
    id: strawberry.ID
    title: str = strawberry.field(description="The book's title")
    year: int = strawberry.field(description="Year of first publication")
    author: Author
    genre: Genre
    tags: list[str]
    published_date: datetime.date | None = None
    metadata: JSON | None = None


# --- Union Type for Search ---

SearchResult = strawberry.union("SearchResult", types=(Book, Author))


# --- In-Memory Data ---

AUTHORS = [
    Author(id=strawberry.ID("1"), name="George Orwell", bio="English novelist"),
    Author(id=strawberry.ID("2"), name="Frank Herbert", bio="American sci-fi author"),
    Author(id=strawberry.ID("3"), name="J.R.R. Tolkien", bio="Father of modern fantasy"),
    Author(id=strawberry.ID("4"), name="Agatha Christie", bio="Queen of Mystery"),
]

BOOKS = [
    Book(
        id=strawberry.ID("1"),
        title="1984",
        year=1949,
        author=AUTHORS[0],
        genre=Genre.FICTION,
        tags=["dystopia", "politics"],
        published_date=datetime.date(1949, 6, 8),
    ),
    Book(
        id=strawberry.ID("2"),
        title="Dune",
        year=1965,
        author=AUTHORS[1],
        genre=Genre.SCIENCE_FICTION,
        tags=["space", "ecology", "politics"],
        published_date=datetime.date(1965, 8, 1),
    ),
    Book(
        id=strawberry.ID("3"),
        title="The Hobbit",
        year=1937,
        author=AUTHORS[2],
        genre=Genre.FANTASY,
        tags=["adventure", "dragons"],
        published_date=datetime.date(1937, 9, 21),
    ),
    Book(
        id=strawberry.ID("4"),
        title="Murder on the Orient Express",
        year=1934,
        author=AUTHORS[3],
        genre=Genre.MYSTERY,
        tags=["detective", "train"],
        published_date=datetime.date(1934, 1, 1),
    ),
]


# --- Query Resolvers ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return BOOKS

    @strawberry.field
    def book(self, id: strawberry.ID) -> Book | None:
        return next((b for b in BOOKS if b.id == id), None)

    @strawberry.field
    def books_by_genre(self, genre: Genre) -> list[Book]:
        """Filter books by their genre."""
        return [b for b in BOOKS if b.genre == genre]

    @strawberry.field
    def authors(self) -> list[Author]:
        return AUTHORS

    @strawberry.field
    def search(self, term: str) -> list[SearchResult]:
        """Search across books and authors. Returns a union type."""
        results: list[SearchResult] = []
        term_lower = term.lower()
        for book in BOOKS:
            if term_lower in book.title.lower():
                results.append(book)
        for author in AUTHORS:
            if term_lower in author.name.lower():
                results.append(author)
        return results


# --- App Setup ---

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 04")
app.include_router(graphql_app, prefix="/graphql")
