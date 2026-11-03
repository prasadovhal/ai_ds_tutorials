"""
Mini Project: Complete MCP Protocol Simulator
================================================

This mini project builds a complete MCP protocol simulator with:
  - A simulated MCP Server that has tools, resources, and prompts
  - A simulated MCP Client that connects, discovers, and uses them
  - Message validation to ensure all messages follow JSON-RPC 2.0
  - A message log that records every message exchanged
  - A full session lifecycle from connect to shutdown

This is a SIMULATION -- no actual network connections are made.
Everything runs in memory using Python dictionaries.

The goal is to deeply understand the MCP protocol by building
every piece of it yourself.

No external dependencies needed -- just Python's built-in modules.
"""

import json
import time

print("=" * 70)
print("MCP Protocol Simulator")
print("=" * 70)

# ============================================================
# PART 1: Message Validator
# ============================================================
# Every MCP message must follow JSON-RPC 2.0 format.
# This validator checks that messages are well-formed.

print("\n" + "=" * 70)
print("PART 1: Building the Message Validator")
print("=" * 70)


def validate_message(message):
    """
    Validate that a message follows JSON-RPC 2.0 format.
    Returns a list of errors. Empty list means the message is valid.
    """
    errors = []

    # Rule 1: Must be a dictionary
    if not isinstance(message, dict):
        errors.append("Message must be a JSON object (dictionary)")
        return errors

    # Rule 2: Must have "jsonrpc": "2.0"
    if "jsonrpc" not in message:
        errors.append("Missing 'jsonrpc' field")
    elif message["jsonrpc"] != "2.0":
        errors.append("'jsonrpc' must be '2.0', got: " + str(message["jsonrpc"]))

    # Rule 3: Determine message type and validate accordingly
    has_method = "method" in message
    has_id = "id" in message
    has_result = "result" in message
    has_error = "error" in message

    # A request has "method" AND "id"
    if has_method and has_id:
        # This is a request -- validate it
        if not isinstance(message["method"], str):
            errors.append("'method' must be a string")
        if not isinstance(message["id"], (int, str)):
            errors.append("'id' must be a number or string")

    # A notification has "method" but NO "id"
    elif has_method and not has_id:
        # This is a notification -- validate it
        if not isinstance(message["method"], str):
            errors.append("'method' must be a string")

    # A response has "result" OR "error" AND "id"
    elif (has_result or has_error) and has_id:
        # This is a response -- validate it
        if has_result and has_error:
            errors.append("Response cannot have both 'result' and 'error'")

    # If none of the above patterns match, it is invalid
    else:
        errors.append("Message must be a request (method+id), notification (method only), or response (result/error+id)")

    return errors


# Test the validator
print("\nTesting message validator...")

# Test 1: Valid request
test_request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
errors = validate_message(test_request)
print(f"\n  Valid request: {'PASS' if len(errors) == 0 else 'FAIL'}")

# Test 2: Valid notification (no id)
test_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
errors = validate_message(test_notification)
print(f"  Valid notification: {'PASS' if len(errors) == 0 else 'FAIL'}")

# Test 3: Valid response
test_response = {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}
errors = validate_message(test_response)
print(f"  Valid response: {'PASS' if len(errors) == 0 else 'FAIL'}")

# Test 4: Invalid -- missing jsonrpc
test_invalid = {"id": 1, "method": "tools/list"}
errors = validate_message(test_invalid)
print(f"  Missing jsonrpc: {'PASS' if len(errors) > 0 else 'FAIL'} (caught {len(errors)} errors)")

# Test 5: Invalid -- not a dict
errors = validate_message("hello")
print(f"  Not a dict: {'PASS' if len(errors) > 0 else 'FAIL'} (caught {len(errors)} errors)")


# ============================================================
# PART 2: Simulated MCP Server
# ============================================================
# The server holds tools, resources, and prompts.
# It processes incoming messages and returns responses.

print("\n" + "=" * 70)
print("PART 2: Building the Simulated Server")
print("=" * 70)

# Server state
server_name = "SimulatorServer"
server_version = "1.0.0"
server_initialized = False

# Define the tools this server offers
server_tools = [
    {
        "name": "add",
        "description": "Add two numbers together",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "greet",
        "description": "Generate a greeting for a person",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name"},
                "language": {
                    "type": "string",
                    "description": "Greeting language",
                    "enum": ["english", "spanish", "french"]
                }
            },
            "required": ["name"]
        }
    }
]

# Define the resources this server offers
server_resources = [
    {
        "uri": "info://server/status",
        "name": "Server Status",
        "description": "Current status of the server",
        "mimeType": "text/plain"
    },
    {
        "uri": "data://server/config",
        "name": "Server Configuration",
        "description": "Server configuration in JSON format",
        "mimeType": "application/json"
    }
]

# Define the prompts this server offers
server_prompts = [
    {
        "name": "summarize",
        "description": "Summarize a piece of text",
        "arguments": [
            {
                "name": "text",
                "description": "The text to summarize",
                "required": True
            }
        ]
    }
]

# Tool implementations -- these are the actual functions the tools run
def execute_tool(tool_name, arguments):
    """Execute a tool and return the result as a content block."""

    if tool_name == "add":
        # Validate arguments
        if "a" not in arguments or "b" not in arguments:
            return {"text": "Error: Both 'a' and 'b' are required", "isError": True}

        # Calculate the sum
        result = arguments["a"] + arguments["b"]
        return {"text": str(arguments["a"]) + " + " + str(arguments["b"]) + " = " + str(result), "isError": False}

    elif tool_name == "greet":
        # Validate arguments
        if "name" not in arguments:
            return {"text": "Error: 'name' is required", "isError": True}

        name = arguments["name"]
        language = arguments.get("language", "english")

        # Generate greeting based on language
        if language == "spanish":
            greeting = "Hola, " + name + "! Bienvenido!"
        elif language == "french":
            greeting = "Bonjour, " + name + "! Bienvenue!"
        else:
            greeting = "Hello, " + name + "! Welcome!"

        return {"text": greeting, "isError": False}

    else:
        return {"text": "Error: Unknown tool '" + tool_name + "'", "isError": True}


# Resource implementations
def read_resource(uri):
    """Read a resource and return its content."""

    if uri == "info://server/status":
        status_text = "Server: " + server_name + "\n"
        status_text = status_text + "Version: " + server_version + "\n"
        status_text = status_text + "Status: Running\n"
        status_text = status_text + "Initialized: " + str(server_initialized) + "\n"
        status_text = status_text + "Tools: " + str(len(server_tools)) + "\n"
        status_text = status_text + "Resources: " + str(len(server_resources))
        return {"text": status_text, "mimeType": "text/plain"}

    elif uri == "data://server/config":
        config = {
            "server_name": server_name,
            "version": server_version,
            "max_connections": 10,
            "timeout_seconds": 30,
            "debug_mode": True
        }
        return {"text": json.dumps(config, indent=2), "mimeType": "application/json"}

    else:
        return None


def process_request(message):
    """
    Process an incoming request and return a response.
    This simulates what a real MCP server does internally.
    """
    global server_initialized

    method = message.get("method", "")
    msg_id = message.get("id")
    params = message.get("params", {})

    # Handle initialize
    if method == "initialize":
        server_initialized = True
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "serverInfo": {
                    "name": server_name,
                    "version": server_version
                }
            }
        }
        return response

    # Handle tools/list
    elif method == "tools/list":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": server_tools
            }
        }
        return response

    # Handle tools/call
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        # Execute the tool
        result = execute_tool(tool_name, arguments)

        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result["text"]
                    }
                ],
                "isError": result["isError"]
            }
        }
        return response

    # Handle resources/list
    elif method == "resources/list":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "resources": server_resources
            }
        }
        return response

    # Handle resources/read
    elif method == "resources/read":
        uri = params.get("uri", "")
        resource_data = read_resource(uri)

        if resource_data is None:
            # Resource not found -- return a JSON-RPC error
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": "Resource not found: " + uri
                }
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": resource_data["mimeType"],
                            "text": resource_data["text"]
                        }
                    ]
                }
            }
        return response

    # Handle prompts/list
    elif method == "prompts/list":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "prompts": server_prompts
            }
        }
        return response

    # Handle prompts/get
    elif method == "prompts/get":
        prompt_name = params.get("name", "")
        prompt_args = params.get("arguments", {})

        if prompt_name == "summarize":
            text = prompt_args.get("text", "")
            prompt_content = "Please summarize the following text in 2-3 sentences:\n\n" + text + "\n\nSummary:"

            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "description": "Summarize text",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": prompt_content
                            }
                        }
                    ]
                }
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": "Unknown prompt: " + prompt_name
                }
            }
        return response

    # Unknown method
    else:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": "Method not found: " + method
            }
        }
        return response


print("Server built successfully!")
print(f"  Tools: {len(server_tools)}")
print(f"  Resources: {len(server_resources)}")
print(f"  Prompts: {len(server_prompts)}")


# ============================================================
# PART 3: Simulated MCP Client
# ============================================================
# The client sends requests and processes responses.

print("\n" + "=" * 70)
print("PART 3: Building the Simulated Client")
print("=" * 70)

# Client state
client_name = "SimulatorClient"
client_version = "1.0.0"
client_request_id = 0

# Message log records every message for the session summary
message_log = []


def client_send(message):
    """
    Send a message from client to server.
    Validates the message, logs it, and processes it through the server.
    Returns the server's response (or None for notifications).
    """
    global client_request_id

    # Step 1: Validate the outgoing message
    errors = validate_message(message)
    if len(errors) > 0:
        print(f"\n  VALIDATION ERROR in outgoing message:")
        for error in errors:
            print(f"    - {error}")
        return None

    # Step 2: Log the message
    log_entry = {
        "direction": "CLIENT -> SERVER",
        "message": message
    }
    message_log.append(log_entry)

    # Step 3: Print the message
    method = message.get("method", "response")
    print(f"\n  CLIENT -> SERVER [{method}]")
    print(f"  {json.dumps(message, indent=4)}")

    # Step 4: If it is a notification, there is no response
    if "method" in message and "id" not in message:
        print("  (notification -- no response expected)")
        return None

    # Step 5: Process through the server and get response
    response = process_request(message)

    # Step 6: Validate the response
    errors = validate_message(response)
    if len(errors) > 0:
        print(f"\n  VALIDATION ERROR in server response:")
        for error in errors:
            print(f"    - {error}")

    # Step 7: Log the response
    log_entry = {
        "direction": "SERVER -> CLIENT",
        "message": response
    }
    message_log.append(log_entry)

    # Step 8: Print the response
    print(f"\n  SERVER -> CLIENT [response]")
    print(f"  {json.dumps(response, indent=4)}")

    return response


def get_next_client_id():
    """Get the next client request ID."""
    global client_request_id
    client_request_id = client_request_id + 1
    return client_request_id


print("Client built successfully!")


# ============================================================
# PART 4: Run the Complete Session
# ============================================================

print("\n" + "=" * 70)
print("PART 4: Running the Complete MCP Session")
print("=" * 70)

# --- Phase 1: Initialize ---
print("\n" + "-" * 50)
print("Phase 1: Initialize")
print("-" * 50)

# Send initialize request
init_request = {
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "roots": {"listChanged": True}
        },
        "clientInfo": {
            "name": client_name,
            "version": client_version
        }
    }
}
init_response = client_send(init_request)

# Send initialized notification
init_notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
client_send(init_notification)

# Print what we learned about the server
if init_response and "result" in init_response:
    server_info = init_response["result"]["serverInfo"]
    caps = init_response["result"]["capabilities"]
    print(f"\nConnected to: {server_info['name']} v{server_info['version']}")
    print(f"Server capabilities: {list(caps.keys())}")

# --- Phase 2: Discover ---
print("\n" + "-" * 50)
print("Phase 2: Discover Capabilities")
print("-" * 50)

# List tools
tools_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "tools/list",
    "params": {}
})

if tools_response and "result" in tools_response:
    tools = tools_response["result"]["tools"]
    print(f"\nFound {len(tools)} tools:")
    for tool in tools:
        required = tool["inputSchema"].get("required", [])
        print(f"  - {tool['name']}: {tool['description']} (required: {required})")

# List resources
resources_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "resources/list",
    "params": {}
})

if resources_response and "result" in resources_response:
    resources = resources_response["result"]["resources"]
    print(f"\nFound {len(resources)} resources:")
    for resource in resources:
        print(f"  - {resource['uri']}: {resource['description']}")

# List prompts
prompts_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "prompts/list",
    "params": {}
})

if prompts_response and "result" in prompts_response:
    prompts = prompts_response["result"]["prompts"]
    print(f"\nFound {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"  - {prompt['name']}: {prompt['description']}")

# --- Phase 3: Use ---
print("\n" + "-" * 50)
print("Phase 3: Use Server Capabilities")
print("-" * 50)

# Call the add tool
print("\n--- Calling 'add' tool ---")
add_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "tools/call",
    "params": {
        "name": "add",
        "arguments": {"a": 42, "b": 18}
    }
})

if add_response and "result" in add_response:
    content = add_response["result"]["content"][0]["text"]
    is_error = add_response["result"]["isError"]
    print(f"\nTool result: {content} (error: {is_error})")

# Call the greet tool with Spanish
print("\n--- Calling 'greet' tool (Spanish) ---")
greet_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "tools/call",
    "params": {
        "name": "greet",
        "arguments": {"name": "Alice", "language": "spanish"}
    }
})

if greet_response and "result" in greet_response:
    content = greet_response["result"]["content"][0]["text"]
    print(f"\nTool result: {content}")

# Call the greet tool with French
print("\n--- Calling 'greet' tool (French) ---")
greet_fr_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "tools/call",
    "params": {
        "name": "greet",
        "arguments": {"name": "Bob", "language": "french"}
    }
})

if greet_fr_response and "result" in greet_fr_response:
    content = greet_fr_response["result"]["content"][0]["text"]
    print(f"\nTool result: {content}")

# Call a non-existent tool (should get an error)
print("\n--- Calling non-existent tool ---")
bad_tool_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "tools/call",
    "params": {
        "name": "nonexistent_tool",
        "arguments": {}
    }
})

if bad_tool_response and "result" in bad_tool_response:
    content = bad_tool_response["result"]["content"][0]["text"]
    is_error = bad_tool_response["result"]["isError"]
    print(f"\nTool result: {content} (error: {is_error})")

# Read a resource
print("\n--- Reading server status resource ---")
status_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "resources/read",
    "params": {
        "uri": "info://server/status"
    }
})

if status_response and "result" in status_response:
    content = status_response["result"]["contents"][0]["text"]
    print(f"\nResource content:\n{content}")

# Read the config resource
print("\n--- Reading server config resource ---")
config_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "resources/read",
    "params": {
        "uri": "data://server/config"
    }
})

if config_response and "result" in config_response:
    content = config_response["result"]["contents"][0]["text"]
    print(f"\nResource content:\n{content}")

# Read a non-existent resource (should get an error)
print("\n--- Reading non-existent resource ---")
bad_resource_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "resources/read",
    "params": {
        "uri": "info://nonexistent"
    }
})

if bad_resource_response and "error" in bad_resource_response:
    error_msg = bad_resource_response["error"]["message"]
    print(f"\nError: {error_msg}")

# Use a prompt
print("\n--- Getting 'summarize' prompt ---")
prompt_response = client_send({
    "jsonrpc": "2.0",
    "id": get_next_client_id(),
    "method": "prompts/get",
    "params": {
        "name": "summarize",
        "arguments": {
            "text": "MCP is a protocol that lets AI models interact with external tools and data. It uses JSON-RPC 2.0 for communication and supports tools, resources, and prompts."
        }
    }
})

if prompt_response and "result" in prompt_response:
    prompt_messages = prompt_response["result"]["messages"]
    print(f"\nPrompt generated {len(prompt_messages)} messages:")
    for msg in prompt_messages:
        print(f"  Role: {msg['role']}")
        print(f"  Content: {msg['content']['text'][:100]}...")


# ============================================================
# PART 5: Session Summary
# ============================================================

print("\n" + "=" * 70)
print("PART 5: Session Summary")
print("=" * 70)

# Count messages by type
total_messages = len(message_log)
client_messages = 0
server_messages = 0
requests_sent = 0
responses_received = 0
notifications_sent = 0
errors_received = 0

for entry in message_log:
    msg = entry["message"]
    direction = entry["direction"]

    if "CLIENT" in direction:
        client_messages = client_messages + 1

        # Check if request or notification
        if "id" in msg and "method" in msg:
            requests_sent = requests_sent + 1
        elif "method" in msg:
            notifications_sent = notifications_sent + 1

    else:
        server_messages = server_messages + 1
        responses_received = responses_received + 1

        # Check if error response
        if "error" in msg:
            errors_received = errors_received + 1

print(f"\nTotal messages exchanged: {total_messages}")
print(f"  Client -> Server: {client_messages}")
print(f"    Requests:      {requests_sent}")
print(f"    Notifications: {notifications_sent}")
print(f"  Server -> Client: {server_messages}")
print(f"    Responses:     {responses_received}")
print(f"    Errors:        {errors_received}")

print(f"\nServer capabilities used:")
print(f"  Tools called:     {4} (add, greet x2, nonexistent)")
print(f"  Resources read:   {3} (status, config, nonexistent)")
print(f"  Prompts used:     {1} (summarize)")

print("\n" + "=" * 70)
print("KEY TAKEAWAYS")
print("=" * 70)
print("""
This simulator demonstrates the COMPLETE MCP protocol:

1. MESSAGE VALIDATION
   - All messages must follow JSON-RPC 2.0 format
   - Requests have method + id, notifications have method only
   - Responses have result OR error, plus matching id

2. SESSION LIFECYCLE
   - Initialize -> Initialized notification -> Ready
   - Discovery: list tools, resources, prompts
   - Usage: call tools, read resources, get prompts
   - Shutdown: close connection

3. ERROR HANDLING
   - Tool errors: isError=True in result (tool ran but failed)
   - Protocol errors: JSON-RPC error object (bad request)
   - Resource not found: JSON-RPC error with code -32602

4. CAPABILITIES
   - Tools: actions that take arguments and return results
   - Resources: read-only data identified by URI
   - Prompts: reusable LLM prompt templates

5. In production, the transport layer (stdio, HTTP) handles
   the actual sending/receiving of these messages.
   The message FORMAT stays the same regardless of transport.
""")


if __name__ == "__main__":
    pass
