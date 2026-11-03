# Step 1: What is GraphQL?

## The Problem with REST

Imagine you're building a social media app. You need to show a user's profile page with:
- User's name and bio
- Their last 5 posts
- Number of followers

### With REST, you'd need multiple requests:

```
GET /api/users/123           -> { name, bio, email, phone, address, ... }
GET /api/users/123/posts     -> [{ title, body, date, likes, comments, ... }, ...]
GET /api/users/123/followers -> { count: 542, followers: [...] }
```

**Problems:**
1. **Over-fetching**: You get `phone`, `address` etc. that you don't need
2. **Under-fetching**: You need 3 separate requests to build one page
3. **Rigid endpoints**: Backend must create new endpoints for new UI needs

---

## What is GraphQL?

GraphQL is a **query language for APIs**. Instead of the server deciding what data to
send, the **client asks for exactly what it needs**.

### Same profile page with GraphQL - ONE request:

```graphql
query {
  user(id: "123") {
    name
    bio
    posts(last: 5) {
      title
      date
    }
    followersCount
  }
}
```

**Response** (exactly what you asked for):
```json
{
  "data": {
    "user": {
      "name": "Alice",
      "bio": "Python developer",
      "posts": [
        { "title": "GraphQL is awesome", "date": "2025-01-15" },
        { "title": "Learning Strawberry", "date": "2025-01-10" }
      ],
      "followersCount": 542
    }
  }
}
```

---

## Key Concepts

### 1. Schema
The **contract** between client and server. It defines what data is available
and what operations are possible.

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
}
```

- `!` means **non-nullable** (required)
- `[Post!]!` means a **non-nullable list of non-nullable Posts**

### 2. Queries (Read data)
```graphql
query {
  user(id: "1") {
    name
    email
  }
}
```

### 3. Mutations (Write data)
```graphql
mutation {
  createUser(name: "Bob", email: "bob@example.com") {
    id
    name
  }
}
```

### 4. Subscriptions (Real-time data)
```graphql
subscription {
  newMessage(chatId: "42") {
    text
    sender {
      name
    }
  }
}
```

### 5. Resolvers
Functions on the server that **fetch the actual data** for each field.

```python
# Pseudocode
def resolve_user(id):
    return database.get_user(id)

def resolve_posts(user):
    return database.get_posts_by_user(user.id)
```

---

## REST vs GraphQL - When to Use What

| Feature | REST | GraphQL |
|---------|------|---------|
| Data fetching | Server decides | Client decides |
| Endpoints | Multiple (`/users`, `/posts`) | Single (`/graphql`) |
| Over-fetching | Common | Never |
| Under-fetching | Common (need multiple calls) | Never (one query) |
| Caching | Easy (HTTP caching) | More complex |
| File uploads | Native | Requires extra setup |
| Learning curve | Lower | Higher |
| Best for | Simple CRUD, public APIs | Complex UIs, mobile apps |

### Use GraphQL when:
- Your UI needs data from multiple resources in one view
- Different clients (web, mobile) need different data shapes
- You want a strongly-typed API contract
- You have complex, nested data relationships

### Stick with REST when:
- Simple CRUD operations
- File-heavy APIs
- You need aggressive HTTP caching
- Your team is small and the API is simple

---

## GraphQL Ecosystem in Python

| Library | Style | Notes |
|---------|-------|-------|
| **Strawberry** | Code-first, type hints | Modern, well-maintained, our choice |
| **Graphene** | Code-first, classes | Older, large community |
| **Ariadne** | Schema-first | Write SDL, bind resolvers |

We use **Strawberry** because:
- It uses Python type hints (clean, Pythonic)
- Built-in FastAPI integration
- Active development and great docs
- Type-safe by design

---

## What You'll Build

Through this tutorial, you'll build a **Book Review API** with:
- Users who can register and log in
- Books with authors and genres
- Reviews with ratings
- Real-time notifications for new reviews
- Full CRUD operations
- Authentication and authorization

Let's start building in [Step 2: Project Setup](../step_02_setup_project/README.md).
