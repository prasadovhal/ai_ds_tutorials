"""
example1_env_variables.py - MCP Server That Loads Secrets from Environment Variables

PURPOSE:
    This example shows how to build an MCP server that safely loads
    all its secrets and configuration from environment variables.
    No secrets are ever hardcoded in the source code.

WHAT YOU WILL LEARN:
    1. How to load secrets from environment variables
    2. How to use python-dotenv for development
    3. How to validate secrets at startup
    4. How to fail fast if required secrets are missing
    5. How to use secrets in tools without exposing them

SETUP:
    1. poetry add mcp python-dotenv
    2. Create a .env file with your secrets (see below)
    3. Run: python example1_env_variables.py

EXAMPLE .env FILE:
    API_KEY=your_api_key_here
    DATABASE_URL=sqlite:///mydata.db
    MAX_RESULTS=50
"""

import os
import sys
import json
import logging

# ============================================================
# Step 1: Load environment variables from .env file
# ============================================================
# In development, we use a .env file to store secrets.
# In production, secrets come from the deployment environment.

try:
    from dotenv import load_dotenv
    # load_dotenv() reads the .env file and sets the values
    # as environment variables in the current process
    load_dotenv()
    print("[STARTUP] Loaded .env file")
except ImportError:
    print("[STARTUP] python-dotenv not installed, using system environment variables")

# Import MCP SDK
from mcp.server.fastmcp import FastMCP

# ============================================================
# Step 2: Read all configuration from environment variables
# ============================================================
# IMPORTANT: We read secrets here but NEVER print or log their values.
# We only check whether they are set or not.

# Required secrets (server cannot start without these)
API_KEY = os.environ.get("API_KEY")

# Optional configuration with defaults
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///default.db")
MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "50"))
SERVER_NAME = os.environ.get("SERVER_NAME", "secure-server")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# ============================================================
# Step 3: Set up logging
# ============================================================
# We use Python's built-in logging module.
# IMPORTANT: Never log secret values!

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(SERVER_NAME)

# ============================================================
# Step 4: Validate required secrets at startup
# ============================================================
# This is critical. If a required secret is missing, we want
# to know immediately, not when the first request comes in.

def validate_startup():
    """
    Check that all required secrets and configuration are present.
    This runs ONCE at server startup.
    """
    errors = []

    # Check required secrets
    if not API_KEY:
        errors.append("API_KEY is not set")

    # Check configuration values
    if MAX_RESULTS < 1 or MAX_RESULTS > 1000:
        errors.append(f"MAX_RESULTS must be between 1 and 1000, got {MAX_RESULTS}")

    # If there are errors, print them and exit
    if errors:
        logger.error("=" * 50)
        logger.error("STARTUP VALIDATION FAILED")
        logger.error("=" * 50)
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("")
        logger.error("Please set the required environment variables.")
        logger.error("You can create a .env file with these values:")
        logger.error("  API_KEY=your_api_key_here")
        logger.error("=" * 50)
        # In production, you would exit here:
        # sys.exit(1)
        return False

    # Log successful startup (but never log secret values!)
    logger.info("=" * 50)
    logger.info("STARTUP VALIDATION PASSED")
    logger.info("=" * 50)
    logger.info(f"  API_KEY: {'SET' if API_KEY else 'NOT SET'}")
    logger.info(f"  DATABASE_URL: {DATABASE_URL}")
    logger.info(f"  MAX_RESULTS: {MAX_RESULTS}")
    logger.info(f"  SERVER_NAME: {SERVER_NAME}")
    logger.info("=" * 50)
    return True


# ============================================================
# Step 5: Create the MCP server
# ============================================================

# Create the MCP server instance
server = FastMCP(SERVER_NAME)


# ============================================================
# Step 6: Define tools that use secrets safely
# ============================================================

# Tool 1: A search tool that uses the API key internally
# The API key is NEVER exposed to the client

def search_documents(query: str, max_results: int = 10) -> str:
    """
    Search for documents using the configured API.

    This tool uses the API_KEY internally to authenticate
    with the search service. The key is never exposed to the client.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 10)

    Returns:
        JSON string with search results
    """
    # Log the request (but never log the API key!)
    logger.info(f"Search request: query='{query}', max_results={max_results}")

    # Validate inputs
    if not query or len(query.strip()) == 0:
        return json.dumps({"error": "Query cannot be empty"})

    if max_results < 1:
        max_results = 1
    if max_results > MAX_RESULTS:
        max_results = MAX_RESULTS

    # In a real server, you would use API_KEY to call an external API:
    # response = requests.get(
    #     "https://api.example.com/search",
    #     headers={"Authorization": f"Bearer {API_KEY}"},
    #     params={"q": query, "limit": max_results}
    # )

    # For this example, we simulate a search result
    results = []
    for i in range(min(max_results, 3)):
        results.append({
            "title": f"Document {i + 1}: {query}",
            "snippet": f"This is a simulated result for '{query}'",
            "score": round(0.95 - (i * 0.1), 2)
        })

    # Build the response
    response = {
        "query": query,
        "total_results": len(results),
        "results": results,
        # IMPORTANT: We include metadata but NEVER the API key
        "metadata": {
            "server": SERVER_NAME,
            "max_results_config": MAX_RESULTS,
            # NEVER do this: "api_key": API_KEY
        }
    }

    logger.info(f"Search completed: {len(results)} results returned")
    return json.dumps(response, indent=2)


# Register the tool with the MCP server
server.tool()(search_documents)


# Tool 2: A tool that reports server status (without exposing secrets)

def server_status() -> str:
    """
    Get the current server status and configuration.

    This tool reports server health and configuration
    but NEVER exposes secret values.

    Returns:
        JSON string with server status
    """
    status = {
        "server_name": SERVER_NAME,
        "status": "healthy",
        "configuration": {
            # Safe to expose: non-secret configuration
            "max_results": MAX_RESULTS,
            "database_url": DATABASE_URL,
            "log_level": LOG_LEVEL,
            # Show whether secrets are configured (but not their values!)
            "api_key_configured": API_KEY is not None and len(API_KEY) > 0,
            # NEVER do this:
            # "api_key": API_KEY,
        }
    }

    logger.info("Status check requested")
    return json.dumps(status, indent=2)


# Register the tool with the MCP server
server.tool()(server_status)


# Tool 3: A tool that shows what environment variables are set
# (This is useful for debugging, but be careful in production)

def check_config() -> str:
    """
    Check which configuration values are set.

    This tool helps verify that the server is properly configured.
    It shows whether each config value is set, but NEVER shows
    the actual values of secrets.

    Returns:
        JSON string with configuration status
    """
    config_status = {
        "required_secrets": {
            "API_KEY": "SET" if API_KEY else "NOT SET",
        },
        "optional_config": {
            "DATABASE_URL": DATABASE_URL,
            "MAX_RESULTS": MAX_RESULTS,
            "SERVER_NAME": SERVER_NAME,
            "LOG_LEVEL": LOG_LEVEL,
        },
        "all_required_set": API_KEY is not None,
        "recommendation": (
            "All configuration is valid"
            if API_KEY
            else "Please set missing required secrets in your .env file"
        )
    }

    return json.dumps(config_status, indent=2)


# Register the tool with the MCP server
server.tool()(check_config)


# ============================================================
# Step 7: Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server with Environment Variable Configuration")
    print("=" * 60)
    print()

    # Validate configuration before starting
    is_valid = validate_startup()

    if not is_valid:
        print()
        print("Server configuration is incomplete.")
        print("Create a .env file with the following content:")
        print()
        print("  API_KEY=your_api_key_here")
        print("  DATABASE_URL=sqlite:///mydata.db")
        print("  MAX_RESULTS=50")
        print("  SERVER_NAME=secure-server")
        print("  LOG_LEVEL=INFO")
        print()
        print("Then run this script again.")
        print()
        print("For demonstration, running with simulated values...")
        print()

    # Run the MCP server
    # In production, this would start the server and listen for connections
    print("Starting MCP server...")
    print(f"Server name: {SERVER_NAME}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    print()

    # Demonstrate the tools
    print("--- Demonstrating Tools ---")
    print()

    print("1. search_documents('machine learning'):")
    result = search_documents("machine learning", 3)
    print(result)
    print()

    print("2. server_status():")
    result = server_status()
    print(result)
    print()

    print("3. check_config():")
    result = check_config()
    print(result)
    print()

    print("--- Key Takeaways ---")
    print("1. Secrets are loaded from environment variables, never hardcoded")
    print("2. Secrets are validated at startup (fail fast)")
    print("3. Secrets are NEVER printed, logged, or returned in responses")
    print("4. Non-secret configuration has safe defaults")
    print("5. The .env file is for development only")

    # To actually run as an MCP server (uncomment when ready):
    # server.run()
