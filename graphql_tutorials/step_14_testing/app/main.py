from uuid import uuid4

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

BOOKS: list[dict] = [
    {"id": "1", "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": "2", "title": "Dune", "author": "Frank Herbert", "year": 1965},
    {"id": "3", "title": "The Hobbit", "author": "J.R.R. Tolkien", "year": 1937},
]


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


@strawberry.input
class BookInput:
    title: str
    author: str
    year: int


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        return [Book(**b) for b in BOOKS]

    @strawberry.field
    def book(self, id: strawberry.ID) -> Book | None:
        for b in BOOKS:
            if b["id"] == id:
                return Book(**b)
        return None

    @strawberry.field
    def search(self, term: str) -> list[Book]:
        term_lower = term.lower()
        return [
            Book(**b)
            for b in BOOKS
            if term_lower in b["title"].lower() or term_lower in b["author"].lower()
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, input: BookInput) -> Book:
        if not input.title.strip():
            raise ValueError("Title cannot be empty")
        if input.year < 0:
            raise ValueError("Year must be positive")

        book_data = {
            "id": str(uuid4())[:8],
            "title": input.title,
            "author": input.author,
            "year": input.year,
        }
        BOOKS.append(book_data)
        return Book(**book_data)

    @strawberry.mutation
    def delete_book(self, id: strawberry.ID) -> DeleteResult:
        for i, b in enumerate(BOOKS):
            if b["id"] == id:
                BOOKS.pop(i)
                return DeleteResult(success=True, message=f"Deleted book {id}")
        return DeleteResult(success=False, message=f"Book {id} not found")


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 14")
app.include_router(graphql_app, prefix="/graphql")
