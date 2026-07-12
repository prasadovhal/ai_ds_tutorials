"""
Example 1: JSON-RPC 2.0 Basics
================================
This file teaches you what JSON-RPC messages look like.
MCP uses JSON-RPC 2.0 as its message format.

JSON-RPC is a simple protocol for calling functions remotely using JSON.
Think of it as "calling a function on another computer using a JSON message."

We will create and parse JSON-RPC messages by hand so you understand
exactly what happens under the hood when MCP clients talk to servers.

No external dependencies needed -- just Python's built-in json module.
"""

import json

# ============================================================
# PART 1: Understanding JSON-RPC Request Messages
# ============================================================

# A JSON-RPC request has 4 fields:
# - "jsonrpc": Always "2.0" (the version)
# - "id": A unique number to match requests with responses
# - "method": The name of the function you want to call
# - "params": The arguments to pass to the function (optional)

print("=" * 60)
print("PART 1: Creating a JSON-RPC Request")
print("=" * 60)

# Let's create a simple request that asks for a list of tools
# This is what an MCP client sends when it wants to know what tools are available

request_message = {
    "jsonrpc": "2.0",       # Always "2.0" -- this identifies the protocol version
    "id": 1,                 # Unique ID for this request -- used to match the response
    "method": "tools/list",  # The method we want to call -- "tools/list" is an MCP method
    "params": {}             # No parameters needed for listing tools
}

# Convert the Python dictionary to a JSON string
# This is what actually gets sent over the wire (via stdio or HTTP)
request_json = json.dumps(request_message, indent=2)

print("\nJSON-RPC Request (tools/list):")
print(request_json)

# ============================================================
# PART 2: Understanding JSON-RPC Response Messages
# ============================================================

print("\n" + "=" * 60)
print("PART 2: Creating a JSON-RPC Response")
print("=" * 60)

# A successful response has 3 fields:
# - "jsonrpc": Always "2.0"
# - "id": Must match the request's id
# - "result": The return value of the function

response_message = {
    "jsonrpc": "2.0",   # Same version
    "id": 1,             # Matches the request id -- this is how we know which request this answers
    "result": {          # The actual result data
        "tools": [
            {
                "name": "add_numbers",
                "description": "Add two numbers together"
            },
            {
                "name": "search_files",
                "description": "Search for files by name"
            }
        ]
    }
}

response_json = json.dumps(response_message, indent=2)

print("\nJSON-RPC Response (success):")
print(response_json)

# ============================================================
# PART 3: Understanding JSON-RPC Error Messages
# ============================================================

print("\n" + "=" * 60)
print("PART 3: Creating a JSON-RPC Error Response")
print("=" * 60)

# An error response has 3 fields:
# - "jsonrpc": Always "2.0"
# - "id": Must match the request's id
# - "error": An object with "code" and "message"
#
# Standard JSON-RPC error codes:
# -32700  Parse error       (invalid JSON)
# -32600  Invalid request   (not a valid JSON-RPC request)
# -32601  Method not found  (the method does not exist)
# -32602  Invalid params    (wrong arguments)
# -32603  Internal error    (server crashed)

error_response = {
    "jsonrpc": "2.0",
    "id": 99,            # Matches the request that caused the error
    "error": {
        "code": -32601,                    # Standard error code for "method not found"
        "message": "Method not found",     # Human-readable error message
        "data": "The method 'foo/bar' does not exist on this server"  # Optional extra info
    }
}

error_json = json.dumps(error_response, indent=2)

print("\nJSON-RPC Error Response:")
print(error_json)

# ============================================================
# PART 4: Understanding JSON-RPC Notifications
# ============================================================

print("\n" + "=" * 60)
print("PART 4: Creating a JSON-RPC Notification")
print("=" * 60)

# A notification is a message that does NOT expect a response.
# It looks like a request but WITHOUT the "id" field.
# This tells the other side "I'm telling you something, but I don't need a reply."

notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"  # No "id" field! That's what makes it a notification
    # No "params" either -- this notification doesn't need any
}

notification_json = json.dumps(notification, indent=2)

print("\nJSON-RPC Notification (no id, no response expected):")
print(notification_json)

# ============================================================
# PART 5: Parsing JSON-RPC Messages
# ============================================================

print("\n" + "=" * 60)
print("PART 5: Parsing JSON-RPC Messages")
print("=" * 60)

# In real MCP, you receive JSON strings and need to parse them
# Let's simulate receiving and parsing messages

# This is a raw JSON string we "received" from a server
raw_message = '{"jsonrpc": "2.0", "id": 42, "result": {"content": [{"type": "text", "text": "Hello from MCP!"}]}}'

# Step 1: Parse the JSON string into a Python dictionary
parsed = json.loads(raw_message)

# Step 2: Check if it's a response (has "result"), error (has "error"), or request (has "method")
if "result" in parsed:
    print(f"Received a SUCCESS response for request id={parsed['id']}")
    print(f"Result: {parsed['result']}")
elif "error" in parsed:
    print(f"Received an ERROR response for request id={parsed['id']}")
    print(f"Error code: {parsed['error']['code']}")
    print(f"Error message: {parsed['error']['message']}")
elif "method" in parsed:
    if "id" in parsed:
        print(f"Received a REQUEST: method={parsed['method']}, id={parsed['id']}")
    else:
        print(f"Received a NOTIFICATION: method={parsed['method']}")
else:
    print("Unknown message type!")

# ============================================================
# PART 6: Building a Simple Message Factory
# ============================================================

print("\n" + "=" * 60)
print("PART 6: Building a Simple Message Factory")
print("=" * 60)

# Let's create simple functions to build JSON-RPC messages
# This is NOT how you'd do it in production (you'd use the MCP SDK)
# But it shows you exactly what's happening under the hood

# We need a counter to generate unique message IDs
message_id_counter = 0

def create_request(method, params=None):
    """Create a JSON-RPC 2.0 request message."""
    # We use a global counter to generate unique IDs
    # In production, the MCP SDK handles this for you
    global message_id_counter
    message_id_counter = message_id_counter + 1

    message = {
        "jsonrpc": "2.0",
        "id": message_id_counter,
        "method": method
    }

    # Only add params if they were provided
    if params is not None:
        message["params"] = params

    return message

def create_response(request_id, result):
    """Create a JSON-RPC 2.0 success response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,       # Must match the request's id
        "result": result
    }

def create_error(request_id, code, message, data=None):
    """Create a JSON-RPC 2.0 error response."""
    error_obj = {
        "code": code,
        "message": message
    }
    if data is not None:
        error_obj["data"] = data

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error_obj
    }

def create_notification(method, params=None):
    """Create a JSON-RPC 2.0 notification (no id, no response expected)."""
    message = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params is not None:
        message["params"] = params

    return message


# Let's use our factory functions to create some messages
print("\n--- Creating messages with our factory ---\n")

# Create a tools/list request
req1 = create_request("tools/list")
print("Request 1 (tools/list):")
print(json.dumps(req1, indent=2))

# Create a tools/call request
req2 = create_request("tools/call", {
    "name": "add_numbers",
    "arguments": {"a": 5, "b": 3}
})
print("\nRequest 2 (tools/call):")
print(json.dumps(req2, indent=2))

# Create a success response for request 2
resp2 = create_response(req2["id"], {
    "content": [{"type": "text", "text": "The sum is 8"}]
})
print("\nResponse for request 2:")
print(json.dumps(resp2, indent=2))

# Create an error response
err = create_error(99, -32601, "Method not found")
print("\nError response:")
print(json.dumps(err, indent=2))

# Create a notification
notif = create_notification("notifications/initialized")
print("\nNotification:")
print(json.dumps(notif, indent=2))

# ============================================================
# PART 7: Key Takeaways
# ============================================================

print("\n" + "=" * 60)
print("KEY TAKEAWAYS")
print("=" * 60)
print("""
1. JSON-RPC 2.0 is the message format MCP uses for ALL communication
2. There are 4 message types: Request, Response, Error, Notification
3. Requests have an "id" -- Notifications do NOT
4. Responses must include the same "id" as the request they answer
5. Error responses use standard error codes (-32700 to -32603)
6. Everything is plain JSON -- simple and language-agnostic
7. In real MCP, the SDK handles message creation for you
   But understanding the format helps you debug issues
""")


if __name__ == "__main__":
    # This file runs automatically when executed
    # All the code above runs at module level for simplicity
    pass
