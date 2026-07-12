"""
Exercise 2 Solution: Database Resource Server
===============================================
This solution creates an MCP server that serves SQLite database
data as resources. It creates an in-memory database, populates it
with sample data, and exposes it through various resources.

How to run:
    python exercise2_solution.py

How to test:
    npx @modelcontextprotocol/inspector python exercise2_solution.py
"""

from mcp.server.fastmcp import FastMCP
import json
import sqlite3

# ============================================================
# Step 1: Create the MCP Server
# ============================================================
server = FastMCP("Database Resource Server")

# ============================================================
# Step 2: Create and Populate the Database
# ============================================================
# We use an in-memory SQLite database for simplicity.
# In production, you would connect to a real database file.
# We use check_same_thread=False because MCP may read from
# different threads.
db_connection = sqlite3.connect(":memory:", check_same_thread=False)

# Enable row_factory so we get dictionaries instead of tuples.
# This makes it easier to convert results to JSON.
db_connection.row_factory = sqlite3.Row

# Create a cursor to execute SQL commands
cursor = db_connection.cursor()

# Create the products table
cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        in_stock INTEGER NOT NULL DEFAULT 1,
        description TEXT
    )
""")

# Insert sample products
# We use executemany to insert multiple rows at once
sample_products = [
    (1, "Laptop Pro", "Electronics", 1299.99, 1, "High-performance laptop with 16GB RAM"),
    (2, "Wireless Mouse", "Electronics", 29.99, 1, "Ergonomic wireless mouse with USB receiver"),
    (3, "Python Cookbook", "Books", 45.99, 1, "Comprehensive Python programming recipes"),
    (4, "Standing Desk", "Furniture", 549.99, 0, "Adjustable height standing desk"),
    (5, "Mechanical Keyboard", "Electronics", 89.99, 1, "Cherry MX Blue switches, RGB backlit"),
    (6, "Data Science Handbook", "Books", 39.99, 1, "Essential guide to data science practices"),
    (7, "Monitor 27 inch", "Electronics", 399.99, 1, "4K IPS display with USB-C"),
    (8, "Office Chair", "Furniture", 349.99, 1, "Ergonomic mesh office chair")
]

cursor.executemany(
    "INSERT INTO products (id, name, category, price, in_stock, description) VALUES (?, ?, ?, ?, ?, ?)",
    sample_products
)

# Save the changes
db_connection.commit()


# ============================================================
# Step 3: Table Listing Resource
# ============================================================
# This resource returns a list of all tables in the database.
# We query the sqlite_master system table to get this info.
@server.resource("db://tables/list")
def get_table_list():
    """Return a list of all tables in the database."""

    # Query sqlite_master for all tables
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    # Collect all table names
    tables = []
    for row in cursor.fetchall():
        tables.append(row[0])

    result = {
        "database": "in-memory SQLite",
        "total_tables": len(tables),
        "tables": tables
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 4: Table Schema Resource
# ============================================================
# This resource returns the column definitions of the products table.
# We use PRAGMA table_info() which is SQLite's way of describing columns.
@server.resource("db://products/schema")
def get_products_schema():
    """Return the schema of the products table."""

    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(products)")

    columns = []
    for row in cursor.fetchall():
        # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
        column_info = {
            "column_id": row[0],
            "name": row[1],
            "type": row[2],
            "not_null": bool(row[3]),
            "default_value": row[4],
            "is_primary_key": bool(row[5])
        }
        columns.append(column_info)

    result = {
        "table": "products",
        "total_columns": len(columns),
        "columns": columns
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 5: All Products Resource
# ============================================================
# This resource returns all products from the database as JSON.
@server.resource("db://products/all")
def get_all_products():
    """Return all products from the database."""

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM products")

    # Convert each row to a dictionary
    products = []
    for row in cursor.fetchall():
        product = {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": row[3],
            "in_stock": bool(row[4]),
            "description": row[5]
        }
        products.append(product)

    result = {
        "table": "products",
        "total_rows": len(products),
        "data": products
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 6: Single Product Resource Template
# ============================================================
# This resource template lets clients request a specific product
# by its ID. The {product_id} in the URI is a parameter.
@server.resource("db://products/{product_id}")
def get_product_by_id(product_id: str):
    """Return a single product by its ID."""

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))

    row = cursor.fetchone()

    if row is None:
        # Product not found -- return helpful error
        cursor.execute("SELECT id, name FROM products")
        available = []
        for r in cursor.fetchall():
            available.append({"id": r[0], "name": r[1]})

        result = {
            "error": "Product not found",
            "requested_id": product_id,
            "available_products": available
        }
        return json.dumps(result, indent=2)

    # Build the product dictionary
    product = {
        "id": row[0],
        "name": row[1],
        "category": row[2],
        "price": row[3],
        "in_stock": bool(row[4]),
        "description": row[5]
    }

    return json.dumps(product, indent=2)


# ============================================================
# Step 7: Products by Category Resource Template
# ============================================================
# Bonus: A template that filters products by category.
@server.resource("db://products/category/{category_name}")
def get_products_by_category(category_name: str):
    """Return all products in a specific category."""

    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE LOWER(category) = LOWER(?)",
        (category_name,)
    )

    products = []
    for row in cursor.fetchall():
        product = {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": row[3],
            "in_stock": bool(row[4]),
            "description": row[5]
        }
        products.append(product)

    if not products:
        # List available categories
        cursor.execute("SELECT DISTINCT category FROM products")
        categories = [r[0] for r in cursor.fetchall()]

        result = {
            "error": "No products found in category: " + category_name,
            "available_categories": categories
        }
        return json.dumps(result, indent=2)

    result = {
        "category": category_name,
        "total_products": len(products),
        "products": products
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 8: Run the Server
# ============================================================
if __name__ == "__main__":
    server.run()
