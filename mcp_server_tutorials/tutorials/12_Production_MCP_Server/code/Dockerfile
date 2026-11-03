FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry && poetry config virtualenvs.create false

# Copy dependency files first (Docker layer caching)
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction

# Copy application code
COPY src/ ./src/
COPY logs/ ./logs/

# Create data directory
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV MCP_ENVIRONMENT=production
ENV MCP_LOG_LEVEL=INFO
ENV MCP_DATA_DIR=/app/data
ENV MCP_SERVER_NAME=production-server

# Run the server
CMD ["python", "src/server.py"]
