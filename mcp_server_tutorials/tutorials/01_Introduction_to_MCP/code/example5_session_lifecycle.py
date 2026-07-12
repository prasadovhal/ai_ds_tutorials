"""
Example 5: MCP Session Lifecycle Simulation
=============================================
This file simulates the complete lifecycle of an MCP session.

An MCP session goes through these phases:
  1. CONNECT     -- Transport connection is established
  2. INITIALIZE  -- Client and Server exchange capabilities
  3. READY       -- Session is ready for use
  4. USE         -- Client calls tools, reads resources, gets prompts
  5. SHUTDOWN    -- Either side closes the connection

We simulate this entire lifecycle to show you exactly what happens
at each step.

No external dependencies needed -- just Python's built-in json module.
"""

import json
import time

# ============================================================
# PART 1: Define the Session States
# ============================================================

print("=" * 70)
print("MCP Session Lifecycle Simulation")
print("=" * 70)

# These are the possible states of an MCP session
# A session can only be in one state at a time
SESSION_STATES = {
    "DISCONNECTED": "No connection exists",
    "CONNECTED": "Transport connection established, but not initialized",
    "INITIALIZING": "Initialize request sent, waiting for response",
    "READY": "Session is fully initialized and ready for use",
    "SHUTTING_DOWN": "Shutdown initiated, cleaning up",
    "CLOSED": "Session is closed, cannot be reused"
}

# ============================================================
# PART 2: Build a Simple Session Manager
# ============================================================

# We track the session state and message history
session_state = "DISCONNECTED"
message_log = []
message_id_counter = 0


def log_message(direction, message):
    """Log a message with timestamp and direction."""
    # direction is either "CLIENT -> SERVER" or "SERVER -> CLIENT"
    entry = {
        "time": time.strftime("%H:%M:%S"),
        "direction": direction,
        "message": message
    }
    message_log.append(entry)

    # Print the message for visibility
    print(f"\n  [{entry['time']}] {direction}")
    print(f"  {json.dumps(message, indent=4)}")


def get_next_id():
    """Get the next unique message ID."""
    global message_id_counter
    message_id_counter = message_id_counter + 1
    return message_id_counter


# ============================================================
# PHASE 1: CONNECT
# ============================================================

print("\n" + "-" * 70)
print("PHASE 1: CONNECT")
print("-" * 70)
print("Establishing transport connection...")
print("(In real MCP, this means starting a child process for stdio,")
print(" or opening an HTTP connection for SSE transport)")

# Simulate connection delay
time.sleep(0.3)

session_state = "CONNECTED"
print(f"\nSession state: {session_state}")
print("Transport connection established!")

# ============================================================
# PHASE 2: INITIALIZE
# ============================================================

print("\n" + "-" * 70)
print("PHASE 2: INITIALIZE")
print("-" * 70)
print("Client sends initialize request with its capabilities...")

session_state = "INITIALIZING"
print(f"\nSession state: {session_state}")

# Step 1: Client sends initialize request
initialize_request = {
    "jsonrpc": "2.0",
    "id": get_next_id(),
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "roots": {
                "listChanged": True
            }
        },
        "clientInfo": {
            "name": "MCPTutorialClient",
            "version": "1.0.0"
        }
    }
}
log_message("CLIENT -> SERVER", initialize_request)

# Step 2: Server responds with its capabilities
time.sleep(0.2)  # Simulate processing time
initialize_response = {
    "jsonrpc": "2.0",
    "id": initialize_request["id"],  # Must match the request ID
    "result": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True}
        },
        "serverInfo": {
            "name": "MCPTutorialServer",
            "version": "1.0.0"
        }
    }
}
log_message("SERVER -> CLIENT", initialize_response)

# Step 3: Client sends initialized notification
# This tells the server "I received your capabilities, let's go!"
initialized_notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
log_message("CLIENT -> SERVER", initialized_notification)

session_state = "READY"
print(f"\nSession state: {session_state}")
print("Session initialization complete!")
print(f"  Client: {initialize_request['params']['clientInfo']['name']}")
print(f"  Server: {initialize_response['result']['serverInfo']['name']}")
print(f"  Protocol: {initialize_response['result']['protocolVersion']}")

# Print negotiated capabilities
server_caps = initialize_response["result"]["capabilities"]
print(f"  Server capabilities:")
for cap_name in server_caps:
    print(f"    - {cap_name}: {server_caps[cap_name]}")

# ============================================================
# PHASE 3: READY -- Discover Available Tools
# ============================================================

print("\n" + "-" * 70)
print("PHASE 3: READY -- Discovering Tools")
print("-" * 70)
print("Client asks the server what tools are available...")

# Client sends tools/list
tools_list_request = {
    "jsonrpc": "2.0",
    "id": get_next_id(),
    "method": "tools/list",
    "params": {}
}
log_message("CLIENT -> SERVER", tools_list_request)

# Server responds with available tools
time.sleep(0.2)
tools_list_response = {
    "jsonrpc": "2.0",
    "id": tools_list_request["id"],
    "result": {
        "tools": [
            {
                "name": "greet",
                "description": "Generate a greeting for a person",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Person's name"},
                        "language": {"type": "string", "enum": ["english", "spanish", "french"]}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "calculate",
                "description": "Perform basic arithmetic",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["operation", "a", "b"]
                }
            }
        ]
    }
}
log_message("SERVER -> CLIENT", tools_list_response)

available_tools = tools_list_response["result"]["tools"]
print(f"\nDiscovered {len(available_tools)} tools:")
for tool in available_tools:
    print(f"  - {tool['name']}: {tool['description']}")

# ============================================================
# PHASE 4: USE -- Calling Tools
# ============================================================

print("\n" + "-" * 70)
print("PHASE 4: USE -- Calling Tools")
print("-" * 70)

# Call 1: Use the greet tool
print("\n--- Call 1: Greeting tool ---")
call1_request = {
    "jsonrpc": "2.0",
    "id": get_next_id(),
    "method": "tools/call",
    "params": {
        "name": "greet",
        "arguments": {
            "name": "Alice",
            "language": "spanish"
        }
    }
}
log_message("CLIENT -> SERVER", call1_request)

time.sleep(0.2)
call1_response = {
    "jsonrpc": "2.0",
    "id": call1_request["id"],
    "result": {
        "content": [
            {"type": "text", "text": "Hola, Alice! Bienvenida!"}
        ],
        "isError": False
    }
}
log_message("SERVER -> CLIENT", call1_response)

# Call 2: Use the calculate tool
print("\n--- Call 2: Calculate tool ---")
call2_request = {
    "jsonrpc": "2.0",
    "id": get_next_id(),
    "method": "tools/call",
    "params": {
        "name": "calculate",
        "arguments": {
            "operation": "multiply",
            "a": 7,
            "b": 8
        }
    }
}
log_message("CLIENT -> SERVER", call2_request)

time.sleep(0.2)
call2_response = {
    "jsonrpc": "2.0",
    "id": call2_request["id"],
    "result": {
        "content": [
            {"type": "text", "text": "7 x 8 = 56"}
        ],
        "isError": False
    }
}
log_message("SERVER -> CLIENT", call2_response)

# Call 3: A tool call that fails
print("\n--- Call 3: Tool call that fails ---")
call3_request = {
    "jsonrpc": "2.0",
    "id": get_next_id(),
    "method": "tools/call",
    "params": {
        "name": "calculate",
        "arguments": {
            "operation": "divide",
            "a": 10,
            "b": 0
        }
    }
}
log_message("CLIENT -> SERVER", call3_request)

time.sleep(0.2)
call3_response = {
    "jsonrpc": "2.0",
    "id": call3_request["id"],
    "result": {
        "content": [
            {"type": "text", "text": "Error: Division by zero is not allowed."}
        ],
        "isError": True  # The tool ran but reported an error
    }
}
log_message("SERVER -> CLIENT", call3_response)

print("\nNote: isError=True means the tool executed but encountered an error")
print("This is different from a JSON-RPC protocol error")

# ============================================================
# PHASE 5: SHUTDOWN
# ============================================================

print("\n" + "-" * 70)
print("PHASE 5: SHUTDOWN")
print("-" * 70)
print("Client initiates graceful shutdown...")

session_state = "SHUTTING_DOWN"
print(f"\nSession state: {session_state}")

# In a real MCP session, the client would close the transport connection
# For stdio: close stdin/stdout
# For HTTP: close the HTTP connection
time.sleep(0.3)

session_state = "CLOSED"
print(f"\nSession state: {session_state}")
print("Session closed successfully!")

# ============================================================
# SESSION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SESSION SUMMARY")
print("=" * 70)

print(f"\nTotal messages exchanged: {len(message_log)}")

# Count by direction
client_to_server = 0
server_to_client = 0
for entry in message_log:
    if "CLIENT -> SERVER" in entry["direction"]:
        client_to_server = client_to_server + 1
    else:
        server_to_client = server_to_client + 1

print(f"  Client -> Server: {client_to_server}")
print(f"  Server -> Client: {server_to_client}")

# Count by type
requests = 0
responses = 0
notifications = 0
for entry in message_log:
    msg = entry["message"]
    if "method" in msg and "id" in msg:
        requests = requests + 1
    elif "result" in msg or "error" in msg:
        responses = responses + 1
    elif "method" in msg and "id" not in msg:
        notifications = notifications + 1

print(f"\n  Requests: {requests}")
print(f"  Responses: {responses}")
print(f"  Notifications: {notifications}")

print(f"\nSession lifecycle states traversed:")
for state_name, state_desc in SESSION_STATES.items():
    print(f"  {state_name}: {state_desc}")

print("\n" + "=" * 70)
print("KEY TAKEAWAYS")
print("=" * 70)
print("""
1. Every MCP session follows the same lifecycle:
   CONNECT -> INITIALIZE -> READY -> USE -> SHUTDOWN

2. Initialization MUST happen before any tool calls

3. The client and server exchange capabilities during initialization

4. Tool discovery (tools/list) happens AFTER initialization

5. Tool calls include the tool name and arguments

6. Tool results include content blocks and an isError flag

7. Either side can initiate shutdown

8. The session is STATEFUL -- the server can remember things
   between requests within the same session
""")


if __name__ == "__main__":
    # This file runs automatically when executed
    # All the code above runs at module level for simplicity
    pass
