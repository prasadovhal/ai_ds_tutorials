# Step 9: Authentication & Authorization

## Concepts

- **Authentication** = "Who are you?" (login, JWT tokens)
- **Authorization** = "What can you do?" (permissions, roles)

---

## How Auth Works in GraphQL

```
Client                          Server
  |                               |
  |-- login(email, password) ---->|
  |                               |-- Verify credentials
  |<---- JWT token ---------------|
  |                               |
  |-- query { me { name } } ---->|
  |   Header: Authorization:      |-- Decode JWT
  |   Bearer <token>              |-- Set user in context
  |                               |-- Resolver checks permissions
  |<---- { data: { ... } } ------|
```

### The Flow:
1. User calls `login` mutation with credentials
2. Server returns a **JWT token**
3. Client sends token in `Authorization` header for all future requests
4. Server decodes token and puts user info in **context**
5. Resolvers check context for permissions

---

## Strawberry Permission Classes

```python
from strawberry.permission import BasePermission

class IsAuthenticated(BasePermission):
    message = "You must be logged in"

    def has_permission(self, source, info, **kwargs):
        return info.context.get("user") is not None

# Use it on fields:
@strawberry.field(permission_classes=[IsAuthenticated])
def me(self, info: Info) -> User:
    return info.context["user"]
```

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run python -m step_09_authentication.app.seed
poetry run uvicorn step_09_authentication.app.main:app --reload
```

### 1. Register a new user
```graphql
mutation {
  register(input: {
    username: "alice"
    email: "alice@example.com"
    password: "secret123"
  }) {
    user { id username email }
    token
  }
}
```

### 2. Login
```graphql
mutation {
  login(email: "alice@example.com", password: "secret123") {
    user { id username }
    token
  }
}
```

### 3. Use the token
In GraphiQL, add an HTTP header:
```json
{
  "Authorization": "Bearer <paste-your-token-here>"
}
```

### 4. Access protected fields
```graphql
query {
  me {
    id
    username
    email
  }
}
```

### 5. Try without token (will fail)
```graphql
query {
  me {
    username
  }
}
# Error: "You must be logged in"
```

Next: [Step 10 - Subscriptions](../step_10_subscriptions/README.md)
