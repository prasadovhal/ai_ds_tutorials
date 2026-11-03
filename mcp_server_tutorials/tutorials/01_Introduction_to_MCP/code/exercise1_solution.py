"""
Exercise 1 Solution: Create JSON-RPC Messages for a Calculator Tool
=====================================================================

This is the complete solution for Exercise 1.
Each message follows the JSON-RPC 2.0 format used by MCP.
"""

import json

print("=" * 70)
print("Exercise 1 SOLUTION: JSON-RPC Messages for a Calculator Tool")
print("=" * 70)

# ============================================================
# 1. Initialize Request
# ============================================================

print("\n--- 1. Initialize Request ---")

# The client introduces itself and declares its capabilities
# This is always the FIRST message in any MCP session
initialize_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "roots": {
                "listChanged": True
            }
        },
        "clientInfo": {
            "name": "CalculatorClient",
            "version": "1.0.0"
        }
    }
}
print(json.dumps(initialize_request, indent=2))

# ============================================================
# 2. Initialize Response
# ============================================================

print("\n--- 2. Initialize Response ---")

# The server responds with its capabilities
# This calculator server only supports tools (no resources or prompts)
initialize_response = {
    "jsonrpc": "2.0",
    "id": 1,  # Must match the request id
    "result": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            # Only tools capability -- this is a simple calculator server
            "tools": {
                "listChanged": True
            }
            # No "resources" or "prompts" -- this server doesn't support them
        },
        "serverInfo": {
            "name": "CalculatorServer",
            "version": "1.0.0"
        }
    }
}
print(json.dumps(initialize_response, indent=2))

# ============================================================
# 3. Initialized Notification
# ============================================================

print("\n--- 3. Initialized Notification ---")

# The client acknowledges initialization is complete
# Notice: NO "id" field -- this is a notification, not a request
initialized_notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
print(json.dumps(initialized_notification, indent=2))

# ============================================================
# 4. tools/list Request
# ============================================================

print("\n--- 4. tools/list Request ---")

# The client asks what tools are available
tools_list_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
print(json.dumps(tools_list_request, indent=2))

# ============================================================
# 5. tools/list Response
# ============================================================

print("\n--- 5. tools/list Response ---")

# The server returns all 4 calculator tools
# Each tool has a name, description, and inputSchema
tools_list_response = {
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "add",
                "description": "Add two numbers together and return the sum",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number"
                        },
                        "b": {
                            "type": "number",
                            "description": "The second number"
                        }
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "subtract",
                "description": "Subtract the second number from the first (a - b)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The number to subtract from"
                        },
                        "b": {
                            "type": "number",
                            "description": "The number to subtract"
                        }
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "multiply",
                "description": "Multiply two numbers and return the product",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number"
                        },
                        "b": {
                            "type": "number",
                            "description": "The second number"
                        }
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "divide",
                "description": "Divide the first number by the second (a / b)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The dividend (number to divide)"
                        },
                        "b": {
                            "type": "number",
                            "description": "The divisor (number to divide by, must not be zero)"
                        }
                    },
                    "required": ["a", "b"]
                }
            }
        ]
    }
}
print(json.dumps(tools_list_response, indent=2))

# ============================================================
# 6. tools/call Request: Multiply 12 by 5
# ============================================================

print("\n--- 6. tools/call Request (multiply 12 x 5) ---")

multiply_request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "multiply",  # Which tool to call
        "arguments": {        # The arguments to pass
            "a": 12,
            "b": 5
        }
    }
}
print(json.dumps(multiply_request, indent=2))

# ============================================================
# 7. tools/call Response: Success (60)
# ============================================================

print("\n--- 7. tools/call Response (success: 60) ---")

multiply_response = {
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "12 x 5 = 60"
            }
        ],
        "isError": False  # The tool executed successfully
    }
}
print(json.dumps(multiply_response, indent=2))

# ============================================================
# 8. tools/call Request: Divide 10 by 0
# ============================================================

print("\n--- 8. tools/call Request (divide 10 / 0) ---")

divide_request = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "divide",
        "arguments": {
            "a": 10,
            "b": 0  # Division by zero!
        }
    }
}
print(json.dumps(divide_request, indent=2))

# ============================================================
# 9. tools/call Response: Error (division by zero)
# ============================================================

print("\n--- 9. tools/call Response (error: division by zero) ---")

# Note: This is a TOOL-LEVEL error, not a JSON-RPC error
# The JSON-RPC request was valid, but the tool itself reported an error
# We use isError=True to indicate this

divide_response = {
    "jsonrpc": "2.0",
    "id": 4,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Error: Cannot divide by zero. The divisor (b) must be a non-zero number."
            }
        ],
        "isError": True  # The tool ran but encountered an error
    }
}
print(json.dumps(divide_response, indent=2))

# ============================================================
# Summary
# ============================================================

print("\n" + "=" * 70)
print("SOLUTION SUMMARY")
print("=" * 70)
print("""
Messages created:
  1. initialize request      -- Client introduces itself
  2. initialize response     -- Server responds with capabilities
  3. initialized notification -- Client confirms ready (no id!)
  4. tools/list request      -- Client asks for available tools
  5. tools/list response     -- Server lists 4 calculator tools
  6. tools/call request      -- Client calls multiply(12, 5)
  7. tools/call response     -- Server returns 60 (isError=False)
  8. tools/call request      -- Client calls divide(10, 0)
  9. tools/call response     -- Server returns error (isError=True)

Key patterns to remember:
  - Requests have "id", "method", and optionally "params"
  - Responses have "id" (matching request) and "result" or "error"
  - Notifications have "method" but NO "id"
  - Tool results use "content" array with "type" and "text"
  - Tool errors use isError=True (NOT JSON-RPC error format)
""")


if __name__ == "__main__":
    pass
