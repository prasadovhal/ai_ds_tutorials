"""
Example 3: MCP Message Structure
==================================
This file shows you the exact structure of the most important MCP messages.

MCP defines specific methods (like "initialize", "tools/list", "tools/call")
that are sent as JSON-RPC messages. Each method has a specific structure
for its parameters and results.

We will build these messages by hand so you understand exactly what
the MCP SDK creates for you automatically.

No external dependencies needed -- just Python's built-in json module.
"""

import json

# ============================================================
# PART 1: The Initialize Request
# ============================================================

print("=" * 70)
print("PART 1: The Initialize Request")
print("=" * 70)

# The initialize request is the FIRST message a client sends to a server.
# It tells the server:
#   - What protocol version the client supports
#   - What capabilities the client has
#   - Who the client is (name and version)

initialize_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        # The protocol version the client wants to use
        # Both sides must agree on the version
        "protocolVersion": "2025-03-26",

        # What the client can do
        # This tells the server what features the client supports
        "capabilities": {
            # "roots" means the client can tell the server about
            # filesystem roots (directories) it has access to
            "roots": {
                "listChanged": True  # Client will notify if roots change
            }
        },

        # Information about the client application
        "clientInfo": {
            "name": "MyLearningApp",
            "version": "0.1.0"
        }
    }
}

print("\nInitialize Request (Client -> Server):")
print(json.dumps(initialize_request, indent=2))

print("\nWhat this message means:")
print('  - "I am MyLearningApp version 0.1.0"')
print('  - "I want to use protocol version 2025-03-26"')
print('  - "I support the roots capability"')

# ============================================================
# PART 2: The Initialize Response
# ============================================================

print("\n" + "=" * 70)
print("PART 2: The Initialize Response")
print("=" * 70)

# The server responds with ITS capabilities
# This is "capability negotiation" -- both sides declare what they support

initialize_response = {
    "jsonrpc": "2.0",
    "id": 1,  # Matches the request id
    "result": {
        # The protocol version the server agrees to use
        "protocolVersion": "2025-03-26",

        # What the server can do
        "capabilities": {
            # This server supports tools
            "tools": {
                "listChanged": True  # Server will notify if tools change
            },
            # This server supports resources
            "resources": {
                "subscribe": True,    # Client can subscribe to resource updates
                "listChanged": True   # Server will notify if resources change
            },
            # This server supports prompts
            "prompts": {
                "listChanged": True   # Server will notify if prompts change
            }
        },

        # Information about the server
        "serverInfo": {
            "name": "MyFirstMCPServer",
            "version": "1.0.0"
        }
    }
}

print("\nInitialize Response (Server -> Client):")
print(json.dumps(initialize_response, indent=2))

print("\nWhat this response means:")
print('  - "I am MyFirstMCPServer version 1.0.0"')
print('  - "I agree to use protocol version 2025-03-26"')
print('  - "I provide tools, resources, and prompts"')
print('  - "I will notify you if any of them change"')

# ============================================================
# PART 3: The Initialized Notification
# ============================================================

print("\n" + "=" * 70)
print("PART 3: The Initialized Notification")
print("=" * 70)

# After receiving the initialize response, the client sends a notification
# This tells the server "I'm ready to start working"
# Notice: no "id" field because notifications don't get responses

initialized_notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
    # No "id" -- this is a notification, not a request
    # No "params" -- this notification doesn't need any
}

print("\nInitialized Notification (Client -> Server):")
print(json.dumps(initialized_notification, indent=2))

print("\nWhat this notification means:")
print('  - "I received your capabilities and I am ready"')
print('  - "You can start accepting my requests now"')

# ============================================================
# PART 4: The tools/list Request and Response
# ============================================================

print("\n" + "=" * 70)
print("PART 4: tools/list -- Discovering Available Tools")
print("=" * 70)

# After initialization, the client can ask "what tools do you have?"

tools_list_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}  # No parameters needed
}

print("\ntools/list Request (Client -> Server):")
print(json.dumps(tools_list_request, indent=2))

# The server responds with a list of all available tools
# Each tool has a name, description, and input schema

tools_list_response = {
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "add_numbers",
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
                "name": "search_files",
                "description": "Search for files matching a pattern in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to search in"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "The glob pattern to match (e.g., *.py)"
                        }
                    },
                    "required": ["directory", "pattern"]
                }
            },
            {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name"
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units: celsius or fahrenheit",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["city"]
                }
            }
        ]
    }
}

print("\ntools/list Response (Server -> Client):")
print(json.dumps(tools_list_response, indent=2))

print("\nThe AI model now knows:")
print("  - There are 3 tools available")
print("  - add_numbers: needs 'a' and 'b' (both numbers)")
print("  - search_files: needs 'directory' and 'pattern' (both strings)")
print("  - get_weather: needs 'city' (string), optional 'units' (celsius/fahrenheit)")

# ============================================================
# PART 5: The tools/call Request and Response
# ============================================================

print("\n" + "=" * 70)
print("PART 5: tools/call -- Calling a Tool")
print("=" * 70)

# When the AI model decides to use a tool, it sends a tools/call request
# The request includes the tool name and the arguments

tools_call_request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "add_numbers",      # Which tool to call
        "arguments": {               # The arguments to pass
            "a": 42,
            "b": 17
        }
    }
}

print("\ntools/call Request (Client -> Server):")
print(json.dumps(tools_call_request, indent=2))

# The server executes the tool and returns the result
# The result always has a "content" array with typed content blocks

tools_call_response = {
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [
            {
                "type": "text",          # Content type: "text", "image", or "resource"
                "text": "The sum of 42 and 17 is 59"
            }
        ],
        "isError": False  # Indicates the tool executed successfully
    }
}

print("\ntools/call Response (Server -> Client):")
print(json.dumps(tools_call_response, indent=2))

# ============================================================
# PART 6: Tool Call with Error
# ============================================================

print("\n" + "=" * 70)
print("PART 6: tools/call -- When a Tool Fails")
print("=" * 70)

# Sometimes a tool call fails (bad arguments, service down, etc.)
# The server can return an error in the tool result (not a JSON-RPC error)

tools_call_error_response = {
    "jsonrpc": "2.0",
    "id": 4,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Error: City 'Atlantis' not found. Please provide a valid city name."
            }
        ],
        "isError": True  # This tells the AI model that the tool failed
    }
}

print("\ntools/call Error Response (Server -> Client):")
print(json.dumps(tools_call_error_response, indent=2))

print("\nImportant distinction:")
print("  - isError=True: The tool ran but encountered a business logic error")
print("  - JSON-RPC error: The protocol itself failed (method not found, etc.)")

# ============================================================
# PART 7: resources/list and resources/read
# ============================================================

print("\n" + "=" * 70)
print("PART 7: Resources -- Listing and Reading Data")
print("=" * 70)

# Resources are data the server provides (files, database records, etc.)

resources_list_response = {
    "jsonrpc": "2.0",
    "id": 5,
    "result": {
        "resources": [
            {
                "uri": "file:///home/user/notes.txt",
                "name": "My Notes",
                "description": "Personal notes file",
                "mimeType": "text/plain"
            },
            {
                "uri": "db://myapp/users",
                "name": "Users Table",
                "description": "All users in the application database",
                "mimeType": "application/json"
            }
        ]
    }
}

print("\nresources/list Response:")
print(json.dumps(resources_list_response, indent=2))

# Reading a specific resource
resources_read_request = {
    "jsonrpc": "2.0",
    "id": 6,
    "method": "resources/read",
    "params": {
        "uri": "file:///home/user/notes.txt"
    }
}

print("\nresources/read Request:")
print(json.dumps(resources_read_request, indent=2))

resources_read_response = {
    "jsonrpc": "2.0",
    "id": 6,
    "result": {
        "contents": [
            {
                "uri": "file:///home/user/notes.txt",
                "mimeType": "text/plain",
                "text": "These are my notes about MCP.\nMCP is a universal protocol for AI tools."
            }
        ]
    }
}

print("\nresources/read Response:")
print(json.dumps(resources_read_response, indent=2))

# ============================================================
# PART 8: prompts/list and prompts/get
# ============================================================

print("\n" + "=" * 70)
print("PART 8: Prompts -- Listing and Getting Templates")
print("=" * 70)

prompts_list_response = {
    "jsonrpc": "2.0",
    "id": 7,
    "result": {
        "prompts": [
            {
                "name": "summarize_code",
                "description": "Generate a summary of a code file",
                "arguments": [
                    {
                        "name": "language",
                        "description": "Programming language of the code",
                        "required": True
                    },
                    {
                        "name": "detail_level",
                        "description": "How detailed: brief, normal, or detailed",
                        "required": False
                    }
                ]
            }
        ]
    }
}

print("\nprompts/list Response:")
print(json.dumps(prompts_list_response, indent=2))

# Getting a specific prompt
prompts_get_response = {
    "jsonrpc": "2.0",
    "id": 8,
    "result": {
        "description": "Generate a summary of a code file",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": "Please summarize the following Python code. Provide a brief overview of what it does, its main functions, and any notable patterns."
                }
            }
        ]
    }
}

print("\nprompts/get Response:")
print(json.dumps(prompts_get_response, indent=2))

# ============================================================
# PART 9: Complete Message Flow Summary
# ============================================================

print("\n" + "=" * 70)
print("PART 9: Complete Message Flow Summary")
print("=" * 70)

print("""
Complete MCP Session Message Flow:

1. Client -> Server:  initialize (capabilities, version, client info)
2. Server -> Client:  initialize response (capabilities, version, server info)
3. Client -> Server:  notifications/initialized (no response needed)
   --- Session is now READY ---
4. Client -> Server:  tools/list (discover available tools)
5. Server -> Client:  tools list response
6. Client -> Server:  tools/call (call a specific tool)
7. Server -> Client:  tool result response
8. Client -> Server:  resources/list (discover available resources)
9. Server -> Client:  resources list response
10. Client -> Server: resources/read (read specific resource)
11. Server -> Client: resource content response
    --- Repeat steps 4-11 as needed ---
12. Either side closes the connection
""")


if __name__ == "__main__":
    # This file runs automatically when executed
    # All the code above runs at module level for simplicity
    pass
