# Step 16: Deployment

## Production Checklist

Before deploying your GraphQL API, address these concerns:

### 1. Security
- [ ] Use environment variables for secrets (no hardcoded keys!)
- [ ] Enable CORS properly
- [ ] Disable GraphiQL in production
- [ ] Add query depth limiting
- [ ] Add query complexity limiting
- [ ] Rate limit the endpoint
- [ ] Validate and sanitize all inputs

### 2. Performance
- [ ] Use DataLoaders for all relationships
- [ ] Add database connection pooling
- [ ] Enable query caching where appropriate
- [ ] Use persistent queries (hash queries on client)
- [ ] Monitor N+1 queries

### 3. Observability
- [ ] Structured logging
- [ ] Request tracing
- [ ] Error tracking (Sentry, etc.)
- [ ] Metrics (request count, latency, error rate)

---

## Environment Configuration

```python
# app/config.py
import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./books.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev deps, no venv needed in container)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction

# Copy app code
COPY app/ app/

# Expose port
EXPOSE 8000

# Run with production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/bookreviews
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=bookreviews
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

### Build and Run

```bash
# Build
docker compose build

# Start
docker compose up -d

# Check logs
docker compose logs -f api

# Stop
docker compose down
```

---

## Production Configuration

### CORS (Cross-Origin Resource Sharing)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Not "*" in production!
    allow_credentials=True,
    allow_methods=["POST"],  # GraphQL only needs POST
    allow_headers=["*"],
)
```

### Disable GraphiQL in Production

```python
graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql" if settings.DEBUG else None,
)
```

### Query Depth Limiting

Prevent deeply nested queries that could DoS your server:

```python
from strawberry.extensions import QueryDepthLimiter

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=10)],
)
```

---

## Deployment Platforms

### Option 1: Railway / Render / Fly.io (easiest)
```bash
# Railway
railway login
railway init
railway up

# Render: connect your GitHub repo, set build command:
#   pip install poetry && poetry install --no-dev
# Start command:
#   poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Option 2: AWS / GCP / Azure
Use Docker + container registry + orchestration (ECS, Cloud Run, AKS).

### Option 3: VPS (DigitalOcean, Linode)
```bash
# On the server:
git clone <repo>
cd <repo>
docker compose up -d

# Set up Nginx reverse proxy for SSL
```

---

## Running This Step

```bash
# From the project root (graphql_tutorials/)
poetry run uvicorn step_16_deployment.app.main:app --reload
```

### Or with Docker:
```bash
docker compose up --build
```

---

## Congratulations!

You've completed the full GraphQL with Python tutorial, covering:

1. GraphQL fundamentals and how it compares to REST
2. Project setup with Poetry
3. Queries and resolvers
4. Schema types (scalars, objects, enums, unions, interfaces)
5. Mutations (create, update, delete)
6. Input types and validation
7. Database integration with SQLAlchemy
8. DataLoaders for solving the N+1 problem
9. Authentication with JWT
10. Real-time subscriptions via WebSockets
11. Pagination (offset and cursor-based)
12. Error handling with union types
13. File uploads
14. Testing with pytest
15. Schema management with Rover CLI
16. Production deployment with Docker

**Next steps:**
- Build your own GraphQL API for a real project
- Explore GraphQL Federation for microservices
- Try Apollo GraphOS for schema management at scale
- Look into Strawberry's advanced features (extensions, plugins, directives)
