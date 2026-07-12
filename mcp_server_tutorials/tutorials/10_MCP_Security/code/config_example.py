"""
config_example.py - Safe Configuration Management for MCP Servers

PURPOSE:
    This file shows how to manage API keys, secrets, and configuration
    values safely. NEVER hardcode secrets in your Python files.

HOW IT WORKS:
    1. We try to load secrets from a .env file (for development)
    2. We fall back to environment variables (for production)
    3. We validate that all required secrets are present
    4. We provide clear error messages if anything is missing

USAGE:
    1. Create a .env file in your project root with your secrets
    2. Import this config module in your MCP server
    3. Use config values like: config.HUGGINGFACE_API_KEY

IMPORTANT:
    - NEVER commit .env files to Git
    - NEVER print or log secret values
    - ALWAYS validate secrets at startup
"""

import os
import sys

# ============================================================
# Step 1: Try to load .env file using python-dotenv
# ============================================================
# python-dotenv reads key-value pairs from a .env file
# and sets them as environment variables.
# This is ONLY for development. In production, use real
# environment variables set by your deployment system.

try:
    from dotenv import load_dotenv
    # load_dotenv() looks for a .env file in the current directory
    # or parent directories and loads the values
    load_dotenv()
    print("[CONFIG] Loaded .env file successfully")
except ImportError:
    # If python-dotenv is not installed, that's OK
    # We will just use environment variables directly
    print("[CONFIG] python-dotenv not installed, using environment variables only")


# ============================================================
# Step 2: Define all configuration values
# ============================================================
# We read each value from environment variables.
# os.environ.get() returns None if the variable is not set.
# We provide default values where it makes sense (never for secrets).

# --- API Keys (SECRETS - no defaults) ---
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# --- Langfuse Observability Keys (SECRETS - no defaults) ---
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")

# --- Server Configuration (non-secret, has defaults) ---
SERVER_HOST = os.environ.get("SERVER_HOST", "localhost")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))
SERVER_NAME = os.environ.get("SERVER_NAME", "my-mcp-server")

# --- Security Configuration (non-secret, has defaults) ---
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
MAX_INPUT_LENGTH = int(os.environ.get("MAX_INPUT_LENGTH", "10000"))
ALLOWED_FILE_EXTENSIONS = os.environ.get(
    "ALLOWED_FILE_EXTENSIONS", ".txt,.csv,.json,.md"
).split(",")

# --- Database Configuration ---
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local.db")

# --- Logging Configuration ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE", "mcp_server.log")


# ============================================================
# Step 3: Validation function
# ============================================================
# This function checks that all REQUIRED secrets are present.
# Call this at server startup. If anything is missing, fail fast
# with a clear error message.

def validate_required_secrets():
    """
    Check that all required secrets are set.
    Returns a list of missing secret names.
    Call this at server startup.
    """
    # Define which secrets are required for your server
    required_secrets = {
        "HUGGINGFACE_API_KEY": HUGGINGFACE_API_KEY,
        # Add more required secrets here as needed
        # "LANGFUSE_PUBLIC_KEY": LANGFUSE_PUBLIC_KEY,
        # "LANGFUSE_SECRET_KEY": LANGFUSE_SECRET_KEY,
    }

    # Check each required secret
    missing = []
    for name, value in required_secrets.items():
        if value is None or value == "":
            missing.append(name)

    return missing


def validate_optional_secrets():
    """
    Check optional secrets and warn if they are not set.
    The server can still start without these, but some
    features may not work.
    """
    optional_secrets = {
        "LANGFUSE_PUBLIC_KEY": LANGFUSE_PUBLIC_KEY,
        "LANGFUSE_SECRET_KEY": LANGFUSE_SECRET_KEY,
    }

    missing = []
    for name, value in optional_secrets.items():
        if value is None or value == "":
            missing.append(name)
            print(f"[CONFIG] WARNING: Optional secret '{name}' is not set")

    return missing


# ============================================================
# Step 4: Safe printing (for debugging config, not secrets)
# ============================================================

def print_config():
    """
    Print the current configuration for debugging.
    IMPORTANT: This NEVER prints secret values.
    It only shows whether secrets are set or not.
    """
    print("=" * 50)
    print("MCP Server Configuration")
    print("=" * 50)

    # Show whether secrets are set (but never their values)
    print(f"  HUGGINGFACE_API_KEY: {'SET' if HUGGINGFACE_API_KEY else 'NOT SET'}")
    print(f"  LANGFUSE_PUBLIC_KEY: {'SET' if LANGFUSE_PUBLIC_KEY else 'NOT SET'}")
    print(f"  LANGFUSE_SECRET_KEY: {'SET' if LANGFUSE_SECRET_KEY else 'NOT SET'}")

    # Show non-secret configuration values
    print(f"  SERVER_HOST: {SERVER_HOST}")
    print(f"  SERVER_PORT: {SERVER_PORT}")
    print(f"  SERVER_NAME: {SERVER_NAME}")
    print(f"  RATE_LIMIT_PER_MINUTE: {RATE_LIMIT_PER_MINUTE}")
    print(f"  MAX_INPUT_LENGTH: {MAX_INPUT_LENGTH}")
    print(f"  ALLOWED_FILE_EXTENSIONS: {ALLOWED_FILE_EXTENSIONS}")
    print(f"  DATABASE_URL: {DATABASE_URL}")
    print(f"  LOG_LEVEL: {LOG_LEVEL}")
    print(f"  LOG_FILE: {LOG_FILE}")

    print("=" * 50)


# ============================================================
# Step 5: Example .env file content
# ============================================================

EXAMPLE_ENV_FILE = """
# .env file - NEVER commit this to Git!
# Copy this content to a file named .env in your project root.

# API Keys
HUGGINGFACE_API_KEY=hf_your_key_here

# Langfuse (optional - for observability)
LANGFUSE_PUBLIC_KEY=pk-your-key-here
LANGFUSE_SECRET_KEY=sk-your-key-here

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8000
SERVER_NAME=my-mcp-server

# Security
RATE_LIMIT_PER_MINUTE=60
MAX_INPUT_LENGTH=10000

# Logging
LOG_LEVEL=INFO
LOG_FILE=mcp_server.log
"""

EXAMPLE_GITIGNORE = """
# .gitignore - Add these entries to prevent committing secrets

# Environment files
.env
.env.local
.env.production
.env.staging

# Secret files
*.key
*.pem
*.p12
credentials.json
service-account.json

# Python
__pycache__/
*.pyc
.venv/
"""


# ============================================================
# Main: Demonstrate the config module
# ============================================================

if __name__ == "__main__":
    print("Config Example - Safe Secret Management")
    print()

    # Step 1: Print the current configuration
    print_config()
    print()

    # Step 2: Validate required secrets
    missing_required = validate_required_secrets()
    if missing_required:
        print(f"[ERROR] Missing required secrets: {missing_required}")
        print("[ERROR] Create a .env file with these values.")
        print("[ERROR] Example .env file content:")
        print(EXAMPLE_ENV_FILE)
        # In a real server, you would exit here:
        # sys.exit(1)
    else:
        print("[OK] All required secrets are present")

    # Step 3: Check optional secrets
    print()
    missing_optional = validate_optional_secrets()
    if missing_optional:
        print(f"[WARN] Missing optional secrets: {missing_optional}")
        print("[WARN] Some features may not work without these.")
    else:
        print("[OK] All optional secrets are present")

    # Step 4: Show example files
    print()
    print("Example .env file:")
    print(EXAMPLE_ENV_FILE)

    print("Example .gitignore entries:")
    print(EXAMPLE_GITIGNORE)
