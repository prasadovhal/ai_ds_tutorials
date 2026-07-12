"""
Example 3: JSON-RPC Request/Response Handler
=============================================
This file builds a complete JSON-RPC 2.0 request/response handler.

JSON-RPC is the messaging format that MCP uses for ALL communication.
Every message between client and server is a JSON-RPC message.

Think of JSON-RPC as the language spoken between the waiter (client)
and the kitchen (server). The order slips follow a strict format:
- Every order has a number (id)
- Every order specifies what is wanted (method)
- Every order can have special instructions (params)
- Every response references the order number (id)

This example teaches you to build and parse these messages correctly.

No external dependencies needed -- just Python's built-in json module.
"""

import json
import time


# ============================================================
# PART 1: Request Builder
# ============================================================
# This class builds properly formatted JSON-RPC 2.0 requests.

class JsonRpcRequestBuilder:
    """
    Builds JSON-RPC 2.0 request messages.

    In real MCP, the client SDK builds these automatically.
    We are building them by hand to understand the format.
    """

    def __init__(self):
        # Start with request ID 1 and increment for each request
        self.next_id = 1

    def build_request(self, method, params=None):
        """
        Build a JSON-RPC 2.0 request.

        A request has these fields:
        - jsonrpc: Always "2.0" (identifies the protocol version)
        - id: Unique number for this request (used to match response)
        - method: The name of the method to call
        - params: Optional arguments for the method
        """
        request = {
            "jsonrpc": "2.0",
            "id": self.next_id,
            "method": method,
        }

        # Only add params if they are provided
        # The params field is optional in JSON-RPC
        if params is not None:
            request["params"] = params

        # Save the ID we used so we can return it
        used_id = self.next_id

        # Increment for the next request
        self.next_id = self.next_id + 1

        return request, used_id

    def build_notification(self, method, params=None):
        """
        Build a JSON-RPC 2.0 notification.

        A notification is like a request but has NO id field.
        This means no response is expected.

        Notifications are used for events like:
        - "initialized" (client tells server it is ready)
        - "resources/updated" (server tells client data changed)
        """
        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }

        if params is not None:
            notification["params"] = params

        return notification


# ============================================================
# PART 2: Response Builder
# ============================================================
# This class builds properly formatted JSON-RPC 2.0 responses.

class JsonRpcResponseBuilder:
    """
    Builds JSON-RPC 2.0 response messages.

    In real MCP, the server SDK builds these automatically.
    We are building them by hand to understand the format.
    """

    def build_success(self, request_id, result):
        """
        Build a successful JSON-RPC response.

        A success response has:
        - jsonrpc: Always "2.0"
        - id: Must match the request's id
        - result: The return value (can be any JSON type)
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
        return response

    def build_error(self, request_id, code, message, data=None):
        """
        Build an error JSON-RPC response.

        An error response has:
        - jsonrpc: Always "2.0"
        - id: Must match the request's id
        - error: An object with code, message, and optional data
        """
        error_obj = {
            "code": code,
            "message": message,
        }

        # The data field is optional but very helpful for debugging
        if data is not None:
            error_obj["data"] = data

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error_obj,
        }
        return response


# ============================================================
# PART 3: Message Validator
# ============================================================
# This class validates that JSON-RPC messages are well-formed.

class JsonRpcValidator:
    """
    Validates JSON-RPC 2.0 messages.

    Before processing a message, we should check that it is valid.
    This catches problems early, before they cause confusing errors.
    """

    def validate_request(self, message):
        """
        Validate that a message is a valid JSON-RPC request.

        Returns (is_valid, error_message)
        """
        # Check 1: Is it a dictionary?
        if not isinstance(message, dict):
            return False, "Message must be a JSON object (dictionary)"

        # Check 2: Does it have the jsonrpc field?
        if "jsonrpc" not in message:
            return False, "Missing required field: jsonrpc"

        # Check 3: Is the jsonrpc field "2.0"?
        if message["jsonrpc"] != "2.0":
            return False, f"Invalid jsonrpc version: {message['jsonrpc']} (must be '2.0')"

        # Check 4: Does it have the method field?
        if "method" not in message:
            return False, "Missing required field: method"

        # Check 5: Is the method a string?
        if not isinstance(message["method"], str):
            return False, "Field 'method' must be a string"

        # Check 6: If it has an id, it is a request. If not, it is a notification.
        # Both are valid, but we should note the difference.
        is_notification = "id" not in message

        # Check 7: If params exist, they must be an object or array
        if "params" in message:
            params = message["params"]
            if not isinstance(params, (dict, list)):
                return False, "Field 'params' must be an object or array"

        return True, "Valid " + ("notification" if is_notification else "request")

    def validate_response(self, message):
        """
        Validate that a message is a valid JSON-RPC response.

        Returns (is_valid, error_message)
        """
        # Check 1: Is it a dictionary?
        if not isinstance(message, dict):
            return False, "Response must be a JSON object (dictionary)"

        # Check 2: Does it have the jsonrpc field?
        if "jsonrpc" not in message:
            return False, "Missing required field: jsonrpc"

        # Check 3: Does it have the id field?
        if "id" not in message:
            return False, "Missing required field: id"

        # Check 4: Does it have EITHER result or error (not both, not neither)?
        has_result = "result" in message
        has_error = "error" in message

        if has_result and has_error:
            return False, "Response cannot have both 'result' and 'error'"

        if not has_result and not has_error:
            return False, "Response must have either 'result' or 'error'"

        # Check 5: If it has an error, validate the error structure
        if has_error:
            error = message["error"]
            if not isinstance(error, dict):
                return False, "Error must be a JSON object"
            if "code" not in error:
                return False, "Error must have a 'code' field"
            if "message" not in error:
                return False, "Error must have a 'message' field"
            if not isinstance(error["code"], int):
                return False, "Error code must be an integer"

        return True, "Valid " + ("error response" if has_error else "success response")


# ============================================================
# PART 4: Simple Request Handler (Server Side)
# ============================================================
# This processes incoming requests and generates responses.

class SimpleRequestHandler:
    """
    Processes JSON-RPC requests and returns responses.

    This simulates what happens inside an MCP server when
    it receives a request from a client.
    """

    def __init__(self):
        # Map method names to handler functions
        self.methods = {}
        self.response_builder = JsonRpcResponseBuilder()
        self.validator = JsonRpcValidator()

    def register_method(self, method_name, handler_function):
        """Register a method that can be called."""
        self.methods[method_name] = handler_function
        print(f"[HANDLER] Registered method: {method_name}")

    def handle(self, raw_json):
        """
        Handle a raw JSON string (as it would arrive over the wire).

        Steps:
        1. Parse the JSON
        2. Validate the message structure
        3. Find the handler for the method
        4. Execute the handler
        5. Return the response as JSON
        """
        print(f"\n{'~' * 50}")
        print(f"[HANDLER] Received raw message:")
        print(f"  {raw_json}")

        # Step 1: Parse the JSON
        try:
            message = json.loads(raw_json)
        except json.JSONDecodeError as e:
            # Parse error -- the JSON itself is invalid
            error_response = self.response_builder.build_error(
                request_id=None,  # We cannot know the ID if we cannot parse the JSON
                code=-32700,
                message="Parse error",
                data={"detail": str(e)},
            )
            return json.dumps(error_response)

        # Step 2: Validate the message structure
        is_valid, validation_message = self.validator.validate_request(message)
        if not is_valid:
            error_response = self.response_builder.build_error(
                request_id=message.get("id"),
                code=-32600,
                message="Invalid Request",
                data={"detail": validation_message},
            )
            return json.dumps(error_response)

        # Check if it is a notification (no response needed)
        if "id" not in message:
            print(f"[HANDLER] Notification received: {message['method']}")
            print(f"[HANDLER] No response needed for notifications")
            return None

        request_id = message["id"]
        method = message["method"]
        params = message.get("params", {})

        # Step 3: Find the handler
        if method not in self.methods:
            error_response = self.response_builder.build_error(
                request_id=request_id,
                code=-32601,
                message="Method not found",
                data={"method": method},
            )
            return json.dumps(error_response)

        # Step 4: Execute the handler
        handler = self.methods[method]
        try:
            result = handler(params)
        except TypeError as e:
            # Invalid params -- wrong arguments
            error_response = self.response_builder.build_error(
                request_id=request_id,
                code=-32602,
                message="Invalid params",
                data={"detail": str(e)},
            )
            return json.dumps(error_response)
        except Exception as e:
            # Internal error -- something unexpected went wrong
            error_response = self.response_builder.build_error(
                request_id=request_id,
                code=-32603,
                message="Internal error",
                data={"detail": str(e)},
            )
            return json.dumps(error_response)

        # Step 5: Build and return the success response
        success_response = self.response_builder.build_success(request_id, result)
        response_json = json.dumps(success_response)
        print(f"[HANDLER] Sending response: {response_json}")
        return response_json


# ============================================================
# PART 5: Demo Methods (What the Server Can Do)
# ============================================================

def handle_tools_list(params):
    """Return a list of available tools."""
    return {
        "tools": [
            {"name": "add", "description": "Add two numbers"},
            {"name": "multiply", "description": "Multiply two numbers"},
        ]
    }


def handle_tools_call(params):
    """Execute a tool."""
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})

    if tool_name == "add":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result_value = a + b
        return {"content": [{"type": "text", "text": str(result_value)}]}

    elif tool_name == "multiply":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result_value = a * b
        return {"content": [{"type": "text", "text": str(result_value)}]}

    else:
        # Raise an exception to trigger a -32602 error
        raise ValueError(f"Unknown tool: {tool_name}")


def handle_ping(params):
    """Handle a ping request."""
    return {"status": "pong", "timestamp": time.time()}


# ============================================================
# MAIN: Run the Demo
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("JSON-RPC REQUEST/RESPONSE HANDLER")
    print("=" * 60)

    # Create the request builder (client side)
    request_builder = JsonRpcRequestBuilder()

    # Create the request handler (server side)
    handler = SimpleRequestHandler()

    # Register methods
    handler.register_method("tools/list", handle_tools_list)
    handler.register_method("tools/call", handle_tools_call)
    handler.register_method("ping", handle_ping)

    # --- Test 1: Valid tools/list request ---
    print("\n" + "=" * 60)
    print("TEST 1: Valid tools/list request")
    print("=" * 60)

    request, req_id = request_builder.build_request("tools/list")
    raw = json.dumps(request)
    response = handler.handle(raw)
    print(f"\n[RESULT] Response:\n{json.dumps(json.loads(response), indent=2)}")

    # --- Test 2: Valid tools/call request ---
    print("\n" + "=" * 60)
    print("TEST 2: Valid tools/call request (add 10 + 20)")
    print("=" * 60)

    request, req_id = request_builder.build_request("tools/call", {
        "name": "add",
        "arguments": {"a": 10, "b": 20}
    })
    raw = json.dumps(request)
    response = handler.handle(raw)
    print(f"\n[RESULT] Response:\n{json.dumps(json.loads(response), indent=2)}")

    # --- Test 3: Method not found ---
    print("\n" + "=" * 60)
    print("TEST 3: Method not found (unknown method)")
    print("=" * 60)

    request, req_id = request_builder.build_request("resources/list")
    raw = json.dumps(request)
    response = handler.handle(raw)
    print(f"\n[RESULT] Response:\n{json.dumps(json.loads(response), indent=2)}")

    # --- Test 4: Invalid JSON ---
    print("\n" + "=" * 60)
    print("TEST 4: Invalid JSON (parse error)")
    print("=" * 60)

    bad_json = '{"jsonrpc": "2.0", "id": 99, "method": broken}'  # Not valid JSON
    response = handler.handle(bad_json)
    print(f"\n[RESULT] Response:\n{json.dumps(json.loads(response), indent=2)}")

    # --- Test 5: Notification (no response expected) ---
    print("\n" + "=" * 60)
    print("TEST 5: Notification (no id, no response)")
    print("=" * 60)

    notification = request_builder.build_notification("notifications/initialized")
    raw = json.dumps(notification)
    response = handler.handle(raw)
    print(f"\n[RESULT] Response: {response}")  # Should be None

    # --- Test 6: Ping request ---
    print("\n" + "=" * 60)
    print("TEST 6: Ping request")
    print("=" * 60)

    request, req_id = request_builder.build_request("ping")
    raw = json.dumps(request)
    response = handler.handle(raw)
    print(f"\n[RESULT] Response:\n{json.dumps(json.loads(response), indent=2)}")

    # --- Test 7: Tool call with unknown tool ---
    print("\n" + "=" * 60)
    print("TEST 7: Tool call with unknown tool (triggers error)")
    print("=" * 60)

    request, req_id = request_builder.build_request("tools/call", {
        "name": "divide",
        "arguments": {"a": 10, "b": 0},
    })
    raw = json.dumps(request)
    response = handler.handle(raw)
    print(f"\n[RESULT] Response:\n{json.dumps(json.loads(response), indent=2)}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("We built a complete JSON-RPC 2.0 handler that:")
    print("  1. Parses incoming JSON messages")
    print("  2. Validates message structure")
    print("  3. Routes to the correct method handler")
    print("  4. Returns proper success or error responses")
    print("  5. Handles notifications (no response)")
    print()
    print("This is exactly what the MCP server SDK does internally.")
