"""
SQLite MCP Server
=================
Provides tools to interact with a SQLite database.
Uses Python's built-in sqlite3 module.
The database file is stored locally as 'mcp_database.db'.
"""

# Import FastMCP and sqlite3
from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Create the MCP server instance
server = FastMCP("SQLite Server")

# Path to the database file (same directory as this script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_database.db")


# --- Helper: Get a database connection ---
def _get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    return conn


# --- Tool: Create a table ---
@server.tool()
def create_table(table_name: str, columns: str) -> str:
    """
    Create a new table. Columns should be a comma-separated string like:
    'name TEXT, age INTEGER, email TEXT'
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Build and execute the CREATE TABLE query
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        cursor.execute(sql)
        conn.commit()
        conn.close()

        return f"Table '{table_name}' created successfully with columns: {columns}"
    except sqlite3.Error as e:
        return f"Error creating table: {str(e)}"


# --- Tool: Insert a row ---
@server.tool()
def insert_row(table_name: str, values: str) -> str:
    """
    Insert a row into a table. Values should be comma-separated like:
    'John, 30, john@example.com'
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Split values and create placeholders
        value_list = [v.strip() for v in values.split(",")]
        placeholders = ", ".join(["?" for _ in value_list])

        # Execute the INSERT query
        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.execute(sql, value_list)
        conn.commit()
        conn.close()

        return f"Row inserted into '{table_name}': {values}"
    except sqlite3.Error as e:
        return f"Error inserting row: {str(e)}"


# --- Tool: Run a query ---
@server.tool()
def query(sql: str) -> str:
    """Run a SQL query (SELECT, UPDATE, DELETE, etc.) and return results."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(sql)

        # If it's a SELECT query, fetch and display results
        if sql.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()

            if not rows:
                conn.close()
                return "Query returned no results."

            # Get column names
            col_names = [desc[0] for desc in cursor.description]
            result = f"Query results ({len(rows)} rows):\n"
            result += "  " + " | ".join(col_names) + "\n"
            result += "  " + "-" * 40 + "\n"

            # Display each row
            for row in rows[:100]:
                row_str = " | ".join(str(val) for val in row)
                result += f"  {row_str}\n"

            if len(rows) > 100:
                result += f"\n  ... and {len(rows) - 100} more rows."

            conn.close()
            return result
        else:
            # For non-SELECT queries, commit and report affected rows
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return f"Query executed. Rows affected: {affected}"

    except sqlite3.Error as e:
        return f"SQL Error: {str(e)}"


# --- Tool: List all tables ---
@server.tool()
def list_tables() -> str:
    """List all tables in the database."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Query sqlite_master for table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        conn.close()

        if not tables:
            return "No tables found in the database."

        result = "Tables in database:\n"
        for table in tables:
            result += f"  - {table[0]}\n"

        return result
    except sqlite3.Error as e:
        return f"Error listing tables: {str(e)}"


# --- Tool: Describe a table ---
@server.tool()
def describe_table(table_name: str) -> str:
    """Show the structure (columns and types) of a table."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Use PRAGMA to get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()

        if not columns:
            return f"Table '{table_name}' not found or has no columns."

        result = f"Structure of '{table_name}':\n"
        for col in columns:
            # col format: (id, name, type, notnull, default, pk)
            pk_marker = " [PRIMARY KEY]" if col[5] else ""
            nullable = " NOT NULL" if col[3] else ""
            result += f"  - {col[1]} ({col[2]}{nullable}{pk_marker})\n"

        return result
    except sqlite3.Error as e:
        return f"Error describing table: {str(e)}"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
