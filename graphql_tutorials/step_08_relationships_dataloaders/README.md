# Step 8: Relationships & DataLoaders

## The N+1 Problem

This is the **most important performance concept** in GraphQL.

Consider this query:
```graphql
query {
  books {          # 1 SQL query: SELECT * FROM books
    title
    author {       # N SQL queries: SELECT * FROM authors WHERE id = ?
      name         #   (one per book!)
    }
  }
}
```

If you have 100 books, this makes **101 SQL queries** (1 + 100). That's the N+1 problem.

### The Solution: DataLoaders

A DataLoader **batches** multiple individual lookups into a single query:

```
Without DataLoader:
  SELECT * FROM authors WHERE id = 1
  SELECT * FROM authors WHERE id = 2
  SELECT * FROM authors WHERE id = 3
  ... (100 queries)

With DataLoader:
  SELECT * FROM authors WHERE id IN (1, 2, 3, ...)
  ... (1 query!)
```

---

## How DataLoaders Work

```
Resolver 1: "I need author 1"  ─┐
Resolver 2: "I need author 2"  ─┼── DataLoader collects all requests
Resolver 3: "I need author 1"  ─┘         │
                                           ▼
                              Batch function runs ONCE:
                              SELECT * FROM authors WHERE id IN (1, 2)
                                           │
                                           ▼
                              Results distributed back to each resolver
```

Key rules:
1. **Batch**: Multiple requests are combined into one
2. **Cache**: Same ID in one request is fetched once (author 1 above)
3. **Per-request**: Each GraphQL request gets a fresh DataLoader

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run python -m step_08_relationships_dataloaders.app.seed
poetry run uvicorn step_08_relationships_dataloaders.app.main:app --reload
```

Watch the SQL logs - you'll see batched queries instead of N+1:

```graphql
query {
  books {
    title
    author {
      name
      books {        # This would be another N+1 without DataLoader!
        title
      }
    }
    reviews {
      rating
      comment
    }
  }
}
```

---

## Relationship Types Covered

### One-to-Many: Author -> Books
One author has many books.

### Many-to-One: Book -> Author
Many books belong to one author.

### One-to-Many: Book -> Reviews
One book has many reviews.

Next: [Step 9 - Authentication & Authorization](../step_09_authentication/README.md)
