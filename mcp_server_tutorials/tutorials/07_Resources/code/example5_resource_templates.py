"""
Example 5: Resource Templates
===============================
This example shows resource templates -- resources with parameterized URIs.
Instead of registering a separate resource for every user, product, or item,
you register a URI template with placeholders.

Think of resource templates like a form with blanks to fill in:
    "user://{user_id}/profile"
    becomes "user://42/profile" when filled with user_id=42

How to run:
    python example5_resource_templates.py

How to test:
    npx @modelcontextprotocol/inspector python example5_resource_templates.py
"""

# ============================================================
# Step 1: Import Everything We Need
# ============================================================
from mcp.server.fastmcp import FastMCP
import json

# ============================================================
# Step 2: Create the MCP Server
# ============================================================
server = FastMCP("Resource Templates Demo")

# ============================================================
# Step 3: Set Up Sample Data
# ============================================================
# In a real application, this data would come from a database.
# Here we use dictionaries to simulate database tables.

# Sample user data -- keyed by user ID
USERS = {
    "1": {
        "id": "1",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "role": "Engineer",
        "department": "Backend",
        "active": True
    },
    "2": {
        "id": "2",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "role": "Designer",
        "department": "Frontend",
        "active": True
    },
    "3": {
        "id": "3",
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "role": "Data Scientist",
        "department": "ML Team",
        "active": False
    },
    "4": {
        "id": "4",
        "name": "Diana Prince",
        "email": "diana@example.com",
        "role": "DevOps Engineer",
        "department": "Infrastructure",
        "active": True
    }
}

# Sample product data -- keyed by product ID
PRODUCTS = {
    "laptop-1": {
        "id": "laptop-1",
        "name": "ProBook Laptop",
        "category": "Electronics",
        "price": 999.99,
        "in_stock": True,
        "description": "High-performance laptop for professionals"
    },
    "phone-1": {
        "id": "phone-1",
        "name": "SmartPhone X",
        "category": "Electronics",
        "price": 699.99,
        "in_stock": True,
        "description": "Latest smartphone with AI features"
    },
    "book-1": {
        "id": "book-1",
        "name": "MCP Programming Guide",
        "category": "Books",
        "price": 49.99,
        "in_stock": True,
        "description": "Complete guide to Model Context Protocol"
    },
    "book-2": {
        "id": "book-2",
        "name": "Python for Data Science",
        "category": "Books",
        "price": 39.99,
        "in_stock": False,
        "description": "Comprehensive Python data science book"
    }
}


# ============================================================
# Step 4: User Profile Template
# ============================================================
# The URI "user://{user_id}/profile" is a template.
# {user_id} is a parameter that gets filled in by the client.
#
# When a client requests "user://1/profile", FastMCP extracts
# user_id="1" and passes it to this function.
@server.resource("user://{user_id}/profile")
def get_user_profile(user_id: str):
    """Return the profile for a specific user."""

    # Look up the user in our data
    user = USERS.get(user_id)

    # If user not found, return an error message
    if user is None:
        result = {
            "error": "User not found",
            "user_id": user_id,
            "available_ids": list(USERS.keys())
        }
        return json.dumps(result, indent=2)

    # Return the user profile
    return json.dumps(user, indent=2)


# ============================================================
# Step 5: Product Details Template
# ============================================================
# This template lets clients request any product by its ID.
@server.resource("product://{product_id}/details")
def get_product_details(product_id: str):
    """Return details for a specific product."""

    product = PRODUCTS.get(product_id)

    if product is None:
        result = {
            "error": "Product not found",
            "product_id": product_id,
            "available_ids": list(PRODUCTS.keys())
        }
        return json.dumps(result, indent=2)

    return json.dumps(product, indent=2)


# ============================================================
# Step 6: Department Listing Template
# ============================================================
# This template lists all users in a given department.
# It shows that templates can filter data, not just look up by ID.
@server.resource("dept://{department}/members")
def get_department_members(department: str):
    """Return all users in a specific department."""

    # Find all users in this department (case-insensitive)
    members = []
    for user_id in USERS:
        user = USERS[user_id]
        if user["department"].lower() == department.lower():
            members.append(user)

    if not members:
        # List available departments to help the client
        all_departments = set()
        for user_id in USERS:
            all_departments.add(USERS[user_id]["department"])

        result = {
            "error": "No members found in department: " + department,
            "available_departments": list(all_departments)
        }
        return json.dumps(result, indent=2)

    result = {
        "department": department,
        "member_count": len(members),
        "members": members
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 7: Product Category Template
# ============================================================
# This template lists all products in a given category.
@server.resource("category://{category_name}/products")
def get_category_products(category_name: str):
    """Return all products in a specific category."""

    # Find products in this category (case-insensitive)
    matching_products = []
    for product_id in PRODUCTS:
        product = PRODUCTS[product_id]
        if product["category"].lower() == category_name.lower():
            matching_products.append(product)

    if not matching_products:
        all_categories = set()
        for product_id in PRODUCTS:
            all_categories.add(PRODUCTS[product_id]["category"])

        result = {
            "error": "No products found in category: " + category_name,
            "available_categories": list(all_categories)
        }
        return json.dumps(result, indent=2)

    result = {
        "category": category_name,
        "product_count": len(matching_products),
        "products": matching_products
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 8: Static Resource for Listing All Available Data
# ============================================================
# This is a regular (non-template) resource that lists all
# available users and products. It helps clients know what
# IDs they can use with the templates.
@server.resource("data://catalog/index")
def get_catalog_index():
    """Return an index of all available data."""

    # Build user index
    user_index = []
    for user_id in USERS:
        user = USERS[user_id]
        user_index.append({
            "id": user_id,
            "name": user["name"],
            "uri": "user://" + user_id + "/profile"
        })

    # Build product index
    product_index = []
    for product_id in PRODUCTS:
        product = PRODUCTS[product_id]
        product_index.append({
            "id": product_id,
            "name": product["name"],
            "uri": "product://" + product_id + "/details"
        })

    result = {
        "users": user_index,
        "products": product_index,
        "template_uris": [
            "user://{user_id}/profile",
            "product://{product_id}/details",
            "dept://{department}/members",
            "category://{category_name}/products"
        ]
    }

    return json.dumps(result, indent=2)


# ============================================================
# Step 9: Run the Server
# ============================================================
if __name__ == "__main__":
    server.run()
