import asyncio
from collections.abc import AsyncGenerator

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# --- Simple in-memory pub/sub for demo ---


class ReviewPubSub:
    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []

    def publish(self, review: "ReviewEvent"):
        for queue in self._subscribers:
            queue.put_nowait(review)

    async def subscribe(self) -> AsyncGenerator["ReviewEvent", None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            while True:
                review = await queue.get()
                yield review
        finally:
            self._subscribers.remove(queue)


pubsub = ReviewPubSub()


# --- Types ---

BOOKS = {1: "1984", 2: "Dune", 3: "The Hobbit"}

review_counter = 0


@strawberry.type
class ReviewEvent:
    id: int
    rating: int
    comment: str
    book_id: int
    book_title: str


@strawberry.type
class ReviewResult:
    id: int
    rating: int
    comment: str


# --- Query ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[str]:
        return list(BOOKS.values())


# --- Mutation ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_review(self, book_id: int, rating: int, comment: str) -> ReviewResult:
        if book_id not in BOOKS:
            raise ValueError(f"Book {book_id} not found")
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be 1-5")

        global review_counter
        review_counter += 1

        event = ReviewEvent(
            id=review_counter,
            rating=rating,
            comment=comment,
            book_id=book_id,
            book_title=BOOKS[book_id],
        )
        pubsub.publish(event)

        return ReviewResult(id=review_counter, rating=rating, comment=comment)


# --- Subscription ---


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def new_review(
        self, book_id: int | None = None
    ) -> AsyncGenerator[ReviewEvent, None]:
        """Subscribe to new reviews. Optionally filter by book_id."""
        async for review in pubsub.subscribe():
            if book_id is None or review.book_id == book_id:
                yield review


# --- App ---

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Book Review API - Step 10")
app.include_router(graphql_app, prefix="/graphql")
