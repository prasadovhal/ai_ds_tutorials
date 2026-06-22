"""Production-ready GraphQL API.

Development:
    poetry run uvicorn app.main:app --reload

Production:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Docker:
    docker compose up --build
"""

from contextlib import asynccontextmanager
from enum import Enum
from uuid import uuid4

import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.extensions import QueryDepthLimiter
from strawberry.fastapi import GraphQLRouter

from .config import settings


# --- Schema ---


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
    bio: str | None = None


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int
    genre: Genre
    author: Author


@strawberry.type
class Review:
    id: strawberry.ID
    rating: int
    comment: str
    book_id: strawberry.ID


@strawberry.input
class BookInput:
    title: str
    author_name: str
    year: int
    genre: Genre


BOOKS_DB: dict[str, dict] = {
    "1": {"id": "1", "title": "1984", "year": 1949, "genre": Genre.FICTION,
           "author": {"id": "1", "name": "George Orwell", "bio": "English novelist"}},
    "2": {"id": "2", "title": "Dune", "year": 1965, "genre": Genre.SCIENCE_FICTION,
           "author": {"id": "2", "name": "Frank Herbert", "bio": "Sci-fi author"}},
}


def _make_book(data: dict) -> Book:
    return Book(
        id=strawberry.ID(data["id"]),
        title=data["title"],
        year=data["year"],
        genre=data["genre"],
        author=Author(**data["author"]),
    )


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return [_make_book(b) for b in BOOKS_DB.values()]

    @strawberry.field
    def book(self, id: strawberry.ID) -> Book | None:
        if id in BOOKS_DB:
            return _make_book(BOOKS_DB[id])
        return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, input: BookInput) -> Book:
        book_id = str(uuid4())[:8]
        author_id = str(uuid4())[:8]
        BOOKS_DB[book_id] = {
            "id": book_id,
            "title": input.title,
            "year": input.year,
            "genre": input.genre,
            "author": {"id": author_id, "name": input.author_name, "bio": None},
        }
        return _make_book(BOOKS_DB[book_id])


# --- App Setup ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=settings.MAX_QUERY_DEPTH)],
)

graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql" if settings.DEBUG else None,
)

app = FastAPI(
    title="Book Review API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")
