"""
Example 5: Dockerized MCP Server
==================================
This MCP server is designed to run inside a Docker container.
It reads all configuration from environment variables,
which is the standard way to configure Docker containers.

To build and run with Docker:

    # Build the image
    docker build -t mcp-server .

    # Run the container
    docker run -e MCP_ENVIRONMENT=production \\
               -e MCP_LOG_LEVEL=INFO \\
               mcp-server

See the Dockerfile and docker-compose.yml in this directory
for the complete containerization setup.

----- Dockerfile Contents -----

    FROM python:3.11-slim
    WORKDIR /app
    RUN pip install poetry && poetry config virtualenvs.create false
    COPY pyproject.toml poetry.lock ./
    RUN poetry install --no-dev
    COPY src/ ./src/
    ENV MCP_ENVIRONMENT=production
    CMD ["python", "src/server.py"]

----- docker-compose.yml Contents -----

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

Poetry setup (for local development):
    poetry init --name example5-dockerized --python "^3.11" --no-interaction
    poetry add mcp
    poetry install
    poetry shell
"""

import logging
import os
import sys
import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 1: Load configuration from environment variables
# ============================================================

# In Docker, configuration comes from environment variables
# set in the Dockerfile or docker-compose.yml

SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "dockerized-mcp-server")
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")
ENVIRONMENT = os.environ.get("MCP_ENVIRONMENT", "development")
DATA_DIR = os.environ.get("MCP_DATA_DIR", "/app/data")
SERVER_VERSION = os.environ.get("MCP_VERSION", "1.0.0")

# ============================================================
# STEP 2: Set up logging (Docker-friendly format)
# ============================================================

# In Docker, logs should go to stdout/stderr
# The container runtime (Docker, Kubernetes) captures them

logger = logging.getLogger(SERVER_NAME)
logger.setLevel(getattr(logging, LOG_LEVEL))

# Use a simple format that works well with Docker log collectors
# Docker adds its own timestamps, but we include ours for completeness
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(getattr(logging, LOG_LEVEL))
console_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
logger.addHandler(console_handler)

# ============================================================
# STEP 3: Log startup information
# ============================================================

SERVER_START_TIME = time.time()

logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
logger.info(f"Environment: {ENVIRONMENT}")
logger.info(f"Log level: {LOG_LEVEL}")
logger.info(f"Data directory: {DATA_DIR}")

# ============================================================
# STEP 4: Create the MCP server
# ============================================================

server = FastMCP(SERVER_NAME)

# ============================================================
# STEP 5: Define tools
# ============================================================


@server.tool()
def health() -> str:
    """
    Health check endpoint for Docker/Kubernetes.

    Container orchestrators call this to verify
    the server is alive and ready to handle requests.
    """

    uptime = time.time() - SERVER_START_TIME

    report = f"Status: healthy\n"
    report = report + f"Server: {SERVER_NAME}\n"
    report = report + f"Version: {SERVER_VERSION}\n"
    report = report + f"Environment: {ENVIRONMENT}\n"
    report = report + f"Uptime: {uptime:.0f}s\n"
    report = report + f"Python: {sys.version.split()[0]}\n"
    report = report + f"PID: {os.getpid()}"

    logger.info(f"Health check: healthy (uptime={uptime:.0f}s)")

    return report


@server.tool()
def read_data(filename: str) -> str:
    """
    Read a data file from the data directory.

    In Docker, the data directory is mounted as a volume,
    so data persists even if the container is restarted.
    """

    logger.info(f"Reading data file: {filename}")

    # Build the full path within the data directory
    filepath = os.path.join(DATA_DIR, filename)

    # Security: make sure the path stays within the data directory
    # This prevents directory traversal attacks (e.g., "../../etc/passwd")
    real_data_dir = os.path.realpath(DATA_DIR)
    real_filepath = os.path.realpath(filepath)

    if not real_filepath.startswith(real_data_dir):
        logger.warning(f"Path traversal attempt blocked: {filename}")
        return "Error: Invalid file path"

    # Check if the file exists
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return f"Error: File '{filename}' not found in data directory"

    # Read and return the file contents
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        logger.info(f"Read {len(content)} characters from {filename}")
        return content

    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return f"Error: Could not read file: {e}"


@server.tool()
def server_info() -> str:
    """Return information about the server and its Docker environment."""

    logger.info("Server info requested")

    info = f"Docker MCP Server Info\n"
    info = info + f"{'=' * 30}\n"
    info = info + f"Name:        {SERVER_NAME}\n"
    info = info + f"Version:     {SERVER_VERSION}\n"
    info = info + f"Environment: {ENVIRONMENT}\n"
    info = info + f"Log Level:   {LOG_LEVEL}\n"
    info = info + f"Data Dir:    {DATA_DIR}\n"
    info = info + f"Python:      {sys.version.split()[0]}\n"
    info = info + f"Platform:    {sys.platform}\n"
    info = info + f"PID:         {os.getpid()}\n"
    info = info + f"Started:     {datetime.fromtimestamp(SERVER_START_TIME).isoformat()}\n"

    return info


@server.tool()
def echo(message: str) -> str:
    """Echo a message back. Simple tool for testing connectivity."""

    logger.info(f"Echo: {message[:50]}...")
    return f"[{ENVIRONMENT}] {message}"


# ============================================================
# STEP 6: Run the server
# ============================================================

if __name__ == "__main__":
    logger.info("Server ready, waiting for connections on stdio...")
    server.run(transport="stdio")
