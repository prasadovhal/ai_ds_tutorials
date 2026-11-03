"""
Exercise 3 Solution: Docker-Ready MCP Server

Dockerfile (save as 'Dockerfile' in project root):
---------------------------------------------------
FROM python:3.11-slim
WORKDIR /app
RUN pip install poetry && poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction
COPY src/ ./src/
ENV MCP_ENVIRONMENT=production
ENV MCP_LOG_LEVEL=INFO
CMD ["python", "src/server.py"]

docker-compose.yml:
---------------------------------------------------
version: '3.8'
services:
  mcp-server:
    build: .
    environment:
      - MCP_ENVIRONMENT=production
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped

Build and run:
  docker build -t my-mcp-server .
  docker run --rm my-mcp-server
"""

import os
import json
import time
from mcp.server.fastmcp import FastMCP

# All config from environment variables (Docker-friendly)
SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "docker-server")
ENVIRONMENT = os.environ.get("MCP_ENVIRONMENT", "development")
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")
DATA_DIR = os.environ.get("MCP_DATA_DIR", "./data")

# Create the server
server = FastMCP(SERVER_NAME)

# Track start time
START_TIME = time.time()


@server.tool()
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello from {SERVER_NAME} ({ENVIRONMENT})!"


@server.tool()
def health_check() -> str:
    """Check server health."""
    uptime = round(time.time() - START_TIME, 1)
    health = {
        "status": "healthy",
        "server": SERVER_NAME,
        "environment": ENVIRONMENT,
        "uptime_seconds": uptime,
    }
    return json.dumps(health, indent=2)


@server.tool()
def server_config() -> str:
    """Show current server configuration."""
    config = {
        "server_name": SERVER_NAME,
        "environment": ENVIRONMENT,
        "log_level": LOG_LEVEL,
        "data_dir": DATA_DIR,
    }
    return json.dumps(config, indent=2)


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    server.run()
