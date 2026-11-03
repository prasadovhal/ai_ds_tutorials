import base64
from enum import Enum

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


@strawberry.enum
class SortField(Enum):
    TITLE = "title"
    YEAR = "year"


@strawberry.enum
class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


# --- Data ---

BOOKS = [
    {"id": 1, "title": "1984", "year": 1949, "genre": Genre.FICTION},
    {"id": 2, "title": "Dune", "year": 1965, "genre": Genre.SCIENCE_FICTION},
    {"id": 3, "title": "The Hobbit", "year": 1937, "genre": Genre.FANTASY},
    {"id": 4, "title": "Foundation", "year": 1951, "genre": Genre.SCIENCE_FICTION},
    {"id": 5, "title": "Neuromancer", "year": 1984, "genre": Genre.SCIENCE_FICTION},
    {"id": 6, "title": "Animal Farm", "year": 1945, "genre": Genre.FICTION},
    {"id": 7, "title": "The Lord of the Rings", "year": 1954, "genre": Genre.FANTASY},
    {"id": 8, "title": "Brave New World", "year": 1932, "genre": Genre.FICTION},
    {"id": 9, "title": "Fahrenheit 451", "year": 1953, "genre": Genre.FICTION},
    {"id": 10, "title": "The Left Hand of Darkness", "year": 1969, "genre": Genre.SCIENCE_FICTION},
    {"id": 11, "title": "Murder on the Orient Express", "year": 1934, "genre": Genre.MYSTERY},
    {"id": 12, "title": "The Big Sleep", "year": 1939, "genre": Genre.MYSTERY},
]


# --- Types ---


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
    genre: Genre


# --- Offset Pagination Types ---


@strawberry.type
class BookPage:
    items: list[Book]
    total_count: int
    has_more: bool


# --- Cursor Pagination Types (Relay-style) ---


@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str | None
    end_cursor: str | None


@strawberry.type
class BookEdge:
    cursor: str
    node: Book


@strawberry.type
class BookConnection:
    edges: list[BookEdge]
    page_info: PageInfo
    total_count: int


# --- Input Types for Filtering/Sorting ---


@strawberry.input
class BookFilter:
    genre: Genre | None = None
    year_from: int | None = None
    year_to: int | None = None
    search: str | None = None


@strawberry.input
class BookSort:
    field: SortField = SortField.TITLE
    direction: SortDirection = SortDirection.ASC


# --- Cursor Helpers ---


def encode_cursor(id: int) -> str:
    return base64.b64encode(f"book:{id}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    decoded = base64.b64decode(cursor.encode()).decode()
    return int(decoded.split(":")[1])


def apply_filters(books: list[dict], filter: BookFilter | None) -> list[dict]:
    if not filter:
        return books
    result = books
    if filter.genre is not None:
        result = [b for b in result if b["genre"] == filter.genre]
    if filter.year_from is not None:
        result = [b for b in result if b["year"] >= filter.year_from]
    if filter.year_to is not None:
        result = [b for b in result if b["year"] <= filter.year_to]
    if filter.search:
        term = filter.search.lower()
        result = [b for b in result if term in b["title"].lower()]
    return result


def apply_sort(books: list[dict], sort: BookSort | None) -> list[dict]:
    if not sort:
        return books
    reverse = sort.direction == SortDirection.DESC
    return sorted(books, key=lambda b: b[sort.field.value], reverse=reverse)


# --- Queries ---


@strawberry.type
class Query:
    @strawberry.field
    def books_offset(
        self,
        offset: int = 0,
        limit: int = 10,
        filter: BookFilter | None = None,
        sort: BookSort | None = None,
    ) -> BookPage:
        """Offset-based pagination (simple)."""
        filtered = apply_filters(BOOKS, filter)
        sorted_books = apply_sort(filtered, sort)
        page = sorted_books[offset : offset + limit]
        return BookPage(
            items=[
                Book(id=strawberry.ID(str(b["id"])), title=b["title"], year=b["year"], genre=b["genre"])
                for b in page
            ],
            total_count=len(sorted_books),
            has_more=offset + limit < len(sorted_books),
        )

    @strawberry.field
    def books(
        self,
        first: int | None = None,
        after: str | None = None,
        last: int | None = None,
        before: str | None = None,
        filter: BookFilter | None = None,
        sort: BookSort | None = None,
    ) -> BookConnection:
        """Cursor-based pagination (Relay-style)."""
        filtered = apply_filters(BOOKS, filter)
        sorted_books = apply_sort(filtered, sort)

        start_idx = 0
        if after:
            after_id = decode_cursor(after)
            for i, b in enumerate(sorted_books):
                if b["id"] == after_id:
                    start_idx = i + 1
                    break

        end_idx = len(sorted_books)
        if before:
            before_id = decode_cursor(before)
            for i, b in enumerate(sorted_books):
                if b["id"] == before_id:
                    end_idx = i
                    break

        sliced = sorted_books[start_idx:end_idx]

        if first is not None:
            sliced = sliced[:first]
        elif last is not None:
            sliced = sliced[-last:]

        edges = [
            BookEdge(
                cursor=encode_cursor(b["id"]),
                node=Book(
                    id=strawberry.ID(str(b["id"])),
                    title=b["title"],
                    year=b["year"],
                    genre=b["genre"],
                ),
            )
            for b in sliced
        ]

        return BookConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=(start_idx + len(sliced)) < len(sorted_books),
                has_previous_page=start_idx > 0,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=len(filtered),
        )


# --- App ---

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 11")
app.include_router(graphql_app, prefix="/graphql")
