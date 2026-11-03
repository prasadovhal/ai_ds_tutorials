# Chapter 12: Production MCP Server

## Learning Objectives

By the end of this chapter, you will be able to:

1. Design a production-ready folder structure for MCP servers
2. Implement proper configuration management with environment-specific settings
3. Set up comprehensive error handling patterns
4. Create health check endpoints for monitoring
5. Implement graceful shutdown
6. Containerize MCP servers with Docker
7. Write unit and integration tests for MCP servers
8. Apply versioning strategies

---

## Why Production Matters

Building an MCP server that works on your laptop is easy. Building one that runs reliably for months serving thousands of requests is hard. This chapter bridges that gap.

### Real-World Analogy

Think of the difference between cooking dinner at home vs running a commercial kitchen. At home you can improvise — in a restaurant you need:
- Standard recipes (configuration)
- Health inspections (health checks)
- Opening/closing procedures (graceful startup/shutdown)
- Ingredient tracking (logging)
- Emergency protocols (error handling)

---

## Production Folder Structure

```
my_mcp_server/
├── pyproject.toml
├── poetry.lock
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── server.py              # Main server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── calculator.py      # Calculator tools
│   │   └── text.py            # Text tools
│   ├── resources/
│   │   ├── __init__.py
│   │   └── data.py            # Resource handlers
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── templates.py       # Prompt templates
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration loading
│       ├── logging_setup.py    # Logging configuration
│       └── errors.py           # Custom error types
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_integration.py
└── scripts/
    ├── start.sh
    └── health_check.sh
```

```mermaid
graph TD
    A[Project Root] --> B[src/]
    A --> C[tests/]
    A --> D[scripts/]
    A --> E[Config Files]
    
    B --> F[server.py]
    B --> G[tools/]
    B --> H[resources/]
    B --> I[prompts/]
    B --> J[utils/]
    
    G --> G1[calculator.py]
    G --> G2[text.py]
    
    J --> J1[config.py]
    J --> J2[logging_setup.py]
    J --> J3[errors.py]
    
    C --> C1[test_tools.py]
    C --> C2[test_integration.py]
    
    E --> E1[pyproject.toml]
    E --> E2[Dockerfile]
    E --> E3[.env]
```

---

## Configuration Management

Good configuration management means your server behaves differently in development, staging, and production WITHOUT changing code.

### The Three Environments

| Environment | Purpose | Database | Logging | Debug |
|------------|---------|----------|---------|-------|
| Development | Local testing | SQLite | DEBUG | On |
| Staging | Pre-production testing | PostgreSQL | INFO | Off |
| Production | Real users | PostgreSQL | WARNING | Off |

### Configuration Pattern

Use environment variables with sensible defaults:

```python
import os

# Load from environment with defaults
SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "my-server")
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")
ENVIRONMENT = os.environ.get("MCP_ENVIRONMENT", "development")
DATABASE_URL = os.environ.get("MCP_DATABASE_URL", "sqlite:///local.db")
MAX_REQUESTS_PER_MINUTE = int(os.environ.get("MCP_RATE_LIMIT", "60"))
```

### .env File

```
MCP_SERVER_NAME=my-production-server
MCP_LOG_LEVEL=WARNING
MCP_ENVIRONMENT=production
MCP_DATABASE_URL=postgresql://user:pass@host/db
MCP_RATE_LIMIT=100
```

Never commit `.env` files. Commit `.env.example` with placeholder values.

---

## Error Handling Patterns

### Error Categories

```mermaid
graph TD
    A[MCP Errors] --> B[Client Errors]
    A --> C[Server Errors]
    A --> D[Transport Errors]
    
    B --> B1[Invalid Parameters]
    B --> B2[Tool Not Found]
    B --> B3[Resource Not Found]
    
    C --> C1[Internal Error]
    C --> C2[Database Error]
    C --> C3[External API Error]
    
    D --> D1[Connection Lost]
    D --> D2[Timeout]
    D --> D3[Parse Error]
```

### Custom Error Classes

Define simple error classes that map to MCP error codes:

```python
class MCPToolError(Exception):
    def __init__(self, message, tool_name="unknown"):
        self.message = message
        self.tool_name = tool_name

class MCPValidationError(MCPToolError):
    pass

class MCPNotFoundError(MCPToolError):
    pass

class MCPRateLimitError(MCPToolError):
    pass
```

### Error Handling in Tools

Every tool should catch errors and return helpful messages:

```python
def my_tool(param: str) -> str:
    # Step 1: Validate input
    if not param:
        return "Error: parameter cannot be empty"
    
    # Step 2: Try the operation
    try:
        result = do_something(param)
        return result
    except FileNotFoundError:
        return f"Error: file '{param}' not found"
    except Exception as e:
        return f"Error: unexpected problem - {str(e)}"
```

---

## Health Checks

Health checks let monitoring systems know if your server is working.

```python
@server.tool()
def health_check() -> str:
    checks = {}
    
    # Check 1: Server is running
    checks["server"] = "healthy"
    
    # Check 2: Database connection
    try:
        # Try a simple database query
        checks["database"] = "healthy"
    except Exception:
        checks["database"] = "unhealthy"
    
    # Check 3: Disk space
    import shutil
    total, used, free = shutil.disk_usage("/")
    if free / total > 0.1:
        checks["disk"] = "healthy"
    else:
        checks["disk"] = "low disk space"
    
    return str(checks)
```

---

## Graceful Shutdown

When your server receives a shutdown signal, it should:
1. Stop accepting new requests
2. Finish processing current requests
3. Close database connections
4. Flush logs
5. Exit cleanly

```python
import signal
import sys

def handle_shutdown(signum, frame):
    print("Shutting down gracefully...")
    # Close database connections
    # Flush log buffers
    # Clean up temporary files
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
```

---

## Docker Containerization

### Why Docker?

- Consistent environment across machines
- Easy deployment to cloud
- Isolation from host system
- Reproducible builds

### Dockerfile for MCP Server

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Copy dependency files first (Docker layer caching)
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV MCP_ENVIRONMENT=production
ENV MCP_LOG_LEVEL=INFO

# Run the server
CMD ["python", "src/server.py"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    environment:
      - MCP_ENVIRONMENT=production
      - MCP_LOG_LEVEL=INFO
      - MCP_DATABASE_URL=sqlite:///data/server.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

```mermaid
graph LR
    A[Docker Image] --> B[Container]
    B --> C[MCP Server]
    C --> D[Tools]
    C --> E[Resources]
    C --> F[Prompts]
    
    G[Volume: /data] --> C
    H[Env Variables] --> C
```

---

## Testing MCP Servers

### Unit Tests

Test individual tools in isolation:

```python
def test_calculator_add():
    result = add(2, 3)
    assert result == "5"

def test_calculator_divide_by_zero():
    result = divide(10, 0)
    assert "error" in result.lower()
```

### Integration Tests

Test the full server-client flow:

```python
async def test_server_tools_list():
    # Start server, connect client
    # Call tools/list
    # Verify expected tools are present
    pass
```

---

## Versioning

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes (removed tools, changed schemas)
- **MINOR** (1.0.0 → 1.1.0): New features (added tools, new resources)
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

Add a version tool to your server:

```python
@server.tool()
def server_version() -> str:
    return "1.0.0"
```

---

## Deployment Checklist

```mermaid
graph TD
    A[Pre-Deployment] --> A1[All tests pass]
    A --> A2[Config reviewed]
    A --> A3[Secrets secured]
    A --> A4[Logs configured]
    
    B[Deployment] --> B1[Build Docker image]
    B --> B2[Push to registry]
    B --> B3[Deploy container]
    B --> B4[Run health check]
    
    C[Post-Deployment] --> C1[Monitor logs]
    C --> C2[Check metrics]
    C --> C3[Verify tools work]
    C --> C4[Test error handling]
```

---

## Summary

| Topic | Key Takeaway |
|-------|-------------|
| Folder Structure | Separate concerns: tools/, resources/, prompts/, utils/ |
| Configuration | Use environment variables with sensible defaults |
| Error Handling | Catch errors in every tool, return helpful messages |
| Health Checks | Expose a health_check tool for monitoring |
| Graceful Shutdown | Handle SIGTERM/SIGINT, clean up resources |
| Docker | Containerize for consistent deployment |
| Testing | Unit test tools, integration test server-client flow |
| Versioning | Use semantic versioning (MAJOR.MINOR.PATCH) |

---

## Interview Questions

1. **What is the ideal folder structure for a production MCP server?** — Separate src/ with tools/, resources/, prompts/, utils/ subdirectories, plus tests/ and configuration files.

2. **How do you manage different environments?** — Use environment variables loaded from .env files, with different values for dev, staging, and production.

3. **Why should you never commit .env files?** — They contain secrets. Commit .env.example with placeholder values instead.

4. **What should a health check verify?** — Server is running, database is connected, disk space is adequate, external APIs are reachable.

5. **What is graceful shutdown?** — Finishing current requests, closing connections, and flushing logs before exiting, instead of abruptly terminating.

6. **Why use Docker for MCP servers?** — Consistent environment, easy deployment, isolation, and reproducibility.

7. **What is Docker layer caching?** — Docker caches each build step. By copying pyproject.toml before code, dependencies are only reinstalled when they change.

8. **How do you test MCP tools?** — Unit tests call the tool function directly. Integration tests start a server and connect a client.

9. **What is semantic versioning?** — MAJOR.MINOR.PATCH where major = breaking changes, minor = new features, patch = bug fixes.

10. **What should happen when a tool encounters an error?** — Return a helpful error message string instead of raising an exception that crashes the server.

---

## Common Mistakes

1. **No error handling in tools** — One unhandled exception crashes the entire server.
2. **Hardcoding configuration** — Makes it impossible to change behavior without code changes.
3. **No health checks** — You cannot monitor what you cannot observe.
4. **Skipping tests** — Bugs in production are 10x more expensive than bugs caught in testing.
5. **Not using Docker** — "Works on my machine" is not a deployment strategy.

---

## Production Tips

1. **Log every tool call** — You need an audit trail for debugging production issues.
2. **Set up alerts** — Health check failures should notify your team immediately.
3. **Use restart policies** — `restart: unless-stopped` in Docker keeps your server running after crashes.
4. **Rate limit everything** — Protect your server from abuse and runaway clients.
5. **Keep secrets out of images** — Use environment variables or secrets managers, never bake secrets into Docker images.
