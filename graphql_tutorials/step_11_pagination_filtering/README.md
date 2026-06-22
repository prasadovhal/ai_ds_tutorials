# Step 11: Pagination & Filtering

## Why Pagination?

Without pagination, `books` returns ALL books. With 10,000 books, that's
a massive response. Pagination returns data in **pages/chunks**.

---

## Two Styles of Pagination

### 1. Offset Pagination (simple)
```graphql
query {
  books(offset: 0, limit: 10) { ... }   # Page 1
  books(offset: 10, limit: 10) { ... }  # Page 2
  books(offset: 20, limit: 10) { ... }  # Page 3
}
```
- Easy to understand and implement
- Problems: skipped/duplicate items if data changes between requests

### 2. Cursor Pagination (robust) - Relay-style
```graphql
query {
  books(first: 10) {
    edges {
      cursor
      node {
        title
        author
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# Next page:
query {
  books(first: 10, after: "cursor_from_previous_response") {
    edges {
      cursor
      node { title }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```
- Stable across data changes
- Industry standard (used by GitHub, Shopify, etc.)
- Required by Relay client

---

## Filtering & Sorting

```graphql
query {
  books(
    filter: { genre: SCIENCE_FICTION, yearFrom: 1960, search: "dune" }
    sort: { field: YEAR, direction: DESC }
    first: 10
  ) {
    edges {
      node {
        title
        year
        genre
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_11_pagination_filtering.app.main:app --reload
```

### Try these queries:

#### Offset pagination
```graphql
query {
  booksOffset(offset: 0, limit: 3) {
    items {
      title
      year
    }
    totalCount
    hasMore
  }
}
```

#### Cursor pagination
```graphql
query {
  books(first: 2) {
    edges {
      cursor
      node {
        title
        year
        genre
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

#### With filtering and sorting
```graphql
query {
  books(
    first: 5
    filter: { genre: FICTION }
    sort: { field: YEAR, direction: ASC }
  ) {
    edges {
      node {
        title
        year
      }
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

#### Search
```graphql
query {
  books(first: 10, filter: { search: "the" }) {
    edges {
      node { title }
    }
  }
}
```

Next: [Step 12 - Error Handling](../step_12_error_handling/README.md)
