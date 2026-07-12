"""
Exercise 2: Database Resource Server
======================================
YOUR TASK: Build an MCP server that serves SQLite database data
as resources.

Requirements:
1. Create a SQLite database with a "products" table (in-memory or file)
2. Insert sample product data (at least 5 products)
3. Create a resource that lists all table names
4. Create a resource that shows the schema of the products table
5. Create a resource that returns all products as JSON
6. Create a resource template that returns a single product by ID

Hints:
- Use sqlite3 module (built into Python)
- Use sqlite3.connect(":memory:") for an in-memory database
- Create the database and insert data when the script starts
- Use json.dumps() to return query results as JSON

How to test:
    npx @modelcontextprotocol/inspector python exercise2_database_resource.py
"""

from mcp.server.fastmcp import FastMCP
import json
import sqlite3

# Create the server
server = FastMCP("Database Resource Exercise")

# ============================================================
# TODO: Create a SQLite database connection (in-memory)
# and create a "products" table with columns:
# id (INTEGER PRIMARY KEY), name (TEXT), category (TEXT),
# price (REAL), in_stock (INTEGER as boolean)
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Insert at least 5 sample products into the table
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "db://tables/list" that returns
# a list of all table names in the database
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "db://products/schema" that returns
# the column names and types of the products table
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource at "db://products/all" that returns
# all products as a JSON array
# ============================================================

# YOUR CODE HERE


# ============================================================
# TODO: Create a resource template at "db://products/{product_id}"
# that returns a single product by its ID
# ============================================================

# YOUR CODE HERE


if __name__ == "__main__":
    server.run()
