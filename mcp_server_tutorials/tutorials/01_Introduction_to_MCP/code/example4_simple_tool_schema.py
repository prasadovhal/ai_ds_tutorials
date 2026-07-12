"""
Example 4: Simple Tool Schema
===============================
This file teaches you how MCP tools are defined using JSON Schema.

Every MCP tool has:
  - name: A unique identifier (like a function name)
  - description: What the tool does (the AI reads this to decide when to use it)
  - inputSchema: A JSON Schema that defines what arguments the tool accepts

The inputSchema follows the JSON Schema standard (https://json-schema.org/).
This is the SAME schema format used by OpenAI function calling, so if you
know that, you already know this.

No external dependencies needed -- just Python's built-in json module.
"""

import json

# ============================================================
# PART 1: The Simplest Possible Tool
# ============================================================

print("=" * 70)
print("PART 1: The Simplest Possible Tool")
print("=" * 70)

# A tool that takes no arguments
# Example: "What time is it?"
get_time_tool = {
    "name": "get_current_time",

    # The description is CRITICAL -- the AI model reads this to decide
    # when to use the tool. Write it clearly and specifically.
    "description": "Get the current date and time in UTC",

    # Even with no arguments, we still define the schema
    "inputSchema": {
        "type": "object",
        "properties": {},   # No properties -- no arguments needed
        "required": []       # Nothing is required
    }
}

print("\nSimplest tool (no arguments):")
print(json.dumps(get_time_tool, indent=2))

# ============================================================
# PART 2: A Tool with Required Arguments
# ============================================================

print("\n" + "=" * 70)
print("PART 2: A Tool with Required Arguments")
print("=" * 70)

# A calculator tool that adds two numbers
# Both arguments are REQUIRED -- the tool cannot work without them
add_numbers_tool = {
    "name": "add_numbers",
    "description": "Add two numbers together and return the sum",
    "inputSchema": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "The first number to add"
            },
            "b": {
                "type": "number",
                "description": "The second number to add"
            }
        },
        # "required" lists the arguments that MUST be provided
        # If the AI model doesn't provide these, the server should reject the call
        "required": ["a", "b"]
    }
}

print("\nTool with required arguments:")
print(json.dumps(add_numbers_tool, indent=2))

# ============================================================
# PART 3: A Tool with Optional Arguments
# ============================================================

print("\n" + "=" * 70)
print("PART 3: A Tool with Optional Arguments")
print("=" * 70)

# A weather tool where "city" is required but "units" is optional
# If "units" is not provided, the server can use a default value
get_weather_tool = {
    "name": "get_weather",
    "description": "Get the current weather for a specified city. Returns temperature, humidity, and conditions.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name (e.g., 'London', 'New York', 'Tokyo')"
            },
            "units": {
                "type": "string",
                "description": "Temperature units to use. Default is 'celsius'.",
                # "enum" restricts the value to a specific set of options
                # The AI model knows it can ONLY use these values
                "enum": ["celsius", "fahrenheit"]
            }
        },
        # Only "city" is required -- "units" is optional
        "required": ["city"]
    }
}

print("\nTool with optional arguments:")
print(json.dumps(get_weather_tool, indent=2))

# ============================================================
# PART 4: A Tool with Complex Arguments
# ============================================================

print("\n" + "=" * 70)
print("PART 4: A Tool with Complex Arguments")
print("=" * 70)

# A file search tool with multiple argument types
search_files_tool = {
    "name": "search_files",
    "description": "Search for files in a directory matching a pattern. Can filter by file size and modification date.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "The directory path to search in (e.g., '/home/user/projects')"
            },
            "pattern": {
                "type": "string",
                "description": "The glob pattern to match file names (e.g., '*.py', '*.txt')"
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search subdirectories. Default is true."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return. Default is 50.",
                "minimum": 1,      # Must be at least 1
                "maximum": 1000    # Cannot exceed 1000
            },
            "file_type": {
                "type": "string",
                "description": "Filter by file type",
                "enum": ["file", "directory", "symlink", "any"]
            }
        },
        "required": ["directory", "pattern"]
    }
}

print("\nTool with complex arguments:")
print(json.dumps(search_files_tool, indent=2))

# ============================================================
# PART 5: A Tool with Nested Objects
# ============================================================

print("\n" + "=" * 70)
print("PART 5: A Tool with Nested Objects")
print("=" * 70)

# Sometimes a tool needs structured input (an object inside an object)
# Example: A database query tool that needs connection info and a query
run_query_tool = {
    "name": "run_database_query",
    "description": "Execute a SQL query against a database and return the results",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SQL query to execute (SELECT only for safety)"
            },
            "database": {
                "type": "string",
                "description": "The database name to query"
            },
            "options": {
                # This is a NESTED object -- an object within the main object
                "type": "object",
                "description": "Optional query settings",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum rows to return",
                        "minimum": 1,
                        "maximum": 10000
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Query timeout in seconds",
                        "minimum": 1,
                        "maximum": 300
                    },
                    "format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["table", "json", "csv"]
                    }
                }
            }
        },
        "required": ["query", "database"]
    }
}

print("\nTool with nested objects:")
print(json.dumps(run_query_tool, indent=2))

# ============================================================
# PART 6: A Tool with Array Arguments
# ============================================================

print("\n" + "=" * 70)
print("PART 6: A Tool with Array Arguments")
print("=" * 70)

# Some tools accept arrays (lists) as arguments
# Example: A tool that sends messages to multiple Slack channels
send_message_tool = {
    "name": "send_slack_message",
    "description": "Send a message to one or more Slack channels",
    "inputSchema": {
        "type": "object",
        "properties": {
            "channels": {
                # "array" type means a list of values
                "type": "array",
                "description": "List of channel names to send the message to",
                "items": {
                    # Each item in the array must be a string
                    "type": "string"
                },
                "minItems": 1   # At least one channel required
            },
            "message": {
                "type": "string",
                "description": "The message text to send"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "normal", "high", "urgent"],
                "description": "Message priority level. Default is 'normal'."
            }
        },
        "required": ["channels", "message"]
    }
}

print("\nTool with array arguments:")
print(json.dumps(send_message_tool, indent=2))

# ============================================================
# PART 7: Validating Tool Arguments
# ============================================================

print("\n" + "=" * 70)
print("PART 7: Validating Tool Arguments (Simple Approach)")
print("=" * 70)

# In production, you would use a JSON Schema validator library
# But let's build a simple validator to understand the concept

def validate_arguments(tool_schema, arguments):
    """
    Validate arguments against a tool's input schema.
    This is a simplified version -- production code uses proper JSON Schema validation.
    """
    input_schema = tool_schema["inputSchema"]
    properties = input_schema.get("properties", {})
    required_fields = input_schema.get("required", [])

    errors = []

    # Check that all required fields are present
    for field_name in required_fields:
        if field_name not in arguments:
            errors.append(f"Missing required field: '{field_name}'")

    # Check that provided fields have the correct type
    type_mapping = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict
    }

    for field_name, field_value in arguments.items():
        if field_name in properties:
            expected_type_name = properties[field_name].get("type")
            if expected_type_name and expected_type_name in type_mapping:
                expected_type = type_mapping[expected_type_name]
                if not isinstance(field_value, expected_type):
                    errors.append(
                        f"Field '{field_name}' should be {expected_type_name}, "
                        f"got {type(field_value).__name__}"
                    )

            # Check enum constraints
            allowed_values = properties[field_name].get("enum")
            if allowed_values and field_value not in allowed_values:
                errors.append(
                    f"Field '{field_name}' must be one of {allowed_values}, "
                    f"got '{field_value}'"
                )

    return errors


# Test the validator with the weather tool
print("\nTest 1: Valid arguments for get_weather")
errors = validate_arguments(get_weather_tool, {"city": "London", "units": "celsius"})
if errors:
    print(f"  Validation FAILED: {errors}")
else:
    print("  Validation PASSED")

print("\nTest 2: Missing required 'city' argument")
errors = validate_arguments(get_weather_tool, {"units": "celsius"})
if errors:
    print(f"  Validation FAILED: {errors}")
else:
    print("  Validation PASSED")

print("\nTest 3: Invalid enum value for 'units'")
errors = validate_arguments(get_weather_tool, {"city": "London", "units": "kelvin"})
if errors:
    print(f"  Validation FAILED: {errors}")
else:
    print("  Validation PASSED")

print("\nTest 4: Wrong type for 'city' (number instead of string)")
errors = validate_arguments(get_weather_tool, {"city": 12345})
if errors:
    print(f"  Validation FAILED: {errors}")
else:
    print("  Validation PASSED")

# ============================================================
# PART 8: Building a Tool Registry
# ============================================================

print("\n" + "=" * 70)
print("PART 8: Building a Tool Registry")
print("=" * 70)

# An MCP server maintains a registry of all its tools
# When a client calls tools/list, the server returns this registry

tool_registry = [
    get_time_tool,
    add_numbers_tool,
    get_weather_tool,
    search_files_tool,
    run_query_tool,
    send_message_tool
]

print(f"\nTool Registry contains {len(tool_registry)} tools:")
print("-" * 50)

for tool in tool_registry:
    # Count required and optional arguments
    properties = tool["inputSchema"].get("properties", {})
    required = tool["inputSchema"].get("required", [])
    optional_count = len(properties) - len(required)

    print(f"  {tool['name']}")
    print(f"    Description: {tool['description'][:60]}...")
    print(f"    Required args: {len(required)}, Optional args: {optional_count}")
    print()

# Simulate a tools/list response with the full registry
tools_list_response = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "tools": tool_registry
    }
}

print(f"Full tools/list response size: {len(json.dumps(tools_list_response))} characters")

# ============================================================
# PART 9: Key Takeaways
# ============================================================

print("\n" + "=" * 70)
print("KEY TAKEAWAYS")
print("=" * 70)

print("""
1. Every MCP tool has: name, description, and inputSchema
2. The inputSchema uses JSON Schema format (same as OpenAI function calling)
3. Descriptions are CRITICAL -- the AI model reads them to choose tools
4. Arguments can be: string, number, integer, boolean, array, object
5. Use "required" to specify which arguments must be provided
6. Use "enum" to restrict values to a specific set
7. Use "minimum"/"maximum" to set numeric bounds
8. Nested objects allow complex structured input
9. Arrays allow list-type inputs
10. Always validate arguments on the server side before executing tools
""")


if __name__ == "__main__":
    # This file runs automatically when executed
    # All the code above runs at module level for simplicity
    pass
