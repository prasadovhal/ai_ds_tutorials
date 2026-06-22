# Step 10: Subscriptions (Real-Time Data)

## What are Subscriptions?

Subscriptions let clients **receive real-time updates** when data changes.
Unlike queries (request-response), subscriptions use **WebSockets** to
maintain an open connection.

```
Client                          Server
  |                               |
  |-- Subscribe to new reviews -->|
  |   (WebSocket connection)      |
  |                               |
  |<-- New review added! ---------|  (push)
  |<-- Another review! -----------|  (push)
  |<-- And another! --------------|  (push)
  |                               |
  |-- Unsubscribe -------------->|
```

---

## Use Cases

- Chat messages
- Live notifications
- Real-time dashboards
- Collaborative editing
- Live sports scores

---

## How It Works in Strawberry

Strawberry uses Python's `async generators` for subscriptions:

```python
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def new_review(self, book_id: int | None = None) -> AsyncGenerator[Review, None]:
        async for review in review_stream():
            if book_id is None or review.book_id == book_id:
                yield review
```

The `yield` statement pushes data to the client each time
new data is available.

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_10_subscriptions.app.main:app --reload
```

### 1. Open TWO browser tabs to http://localhost:8000/graphql

### 2. In Tab 1 - Subscribe:
```graphql
subscription {
  newReview {
    rating
    comment
    bookTitle
  }
}
```
Click play - it will show "Listening..." and wait for data.

### 3. In Tab 2 - Add a review:
```graphql
mutation {
  addReview(bookId: 1, rating: 5, comment: "Amazing book!") {
    id
    rating
    comment
  }
}
```

### 4. Watch Tab 1 - the new review appears in real-time!

### 5. Subscribe with filter (only reviews for book 1):
```graphql
subscription {
  newReview(bookId: 1) {
    rating
    comment
    bookTitle
  }
}
```

---

## Important Notes

- Subscriptions require WebSocket support (Uvicorn has it built-in)
- Each subscription creates a persistent connection (be mindful of scale)
- In production, consider using Redis pub/sub or a message broker
- Strawberry handles the WebSocket protocol automatically

Next: [Step 11 - Pagination & Filtering](../step_11_pagination_filtering/README.md)
