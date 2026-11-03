"""
Example 4: MCP Error Handling
=============================
MCP uses JSON-RPC 2.0 error codes. This example shows all standard error
codes and how to create proper error responses.
"""

import json


def create_error_response(request_id, code, message, data=None):
    """Create a JSON-RPC error response.

    MCP uses these standard error codes:
    -32700  Parse error      - Invalid JSON
    -32600  Invalid request  - Not a valid JSON-RPC request
    -32601  Method not found - The method does not exist
    -32602  Invalid params   - Invalid method parameters
    -32603  Internal error   - Internal server error
    """
    # Every error response has the same structure
    error_response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        }
    }

    # Optionally include extra data about the error
    if data is not None:
        error_response["error"]["data"] = data

    return error_response


def handle_request(raw_message):
    """Process a raw message and return success or error response."""

    # Step 1: Try to parse the JSON
    try:
        request = json.loads(raw_message)
    except json.JSONDecodeError:
        # -32700: The message is not valid JSON
        return create_error_response(None, -32700, "Parse error: invalid JSON")

    # Step 2: Check if it is a valid JSON-RPC request
    if "jsonrpc" not in request or request.get("jsonrpc") != "2.0":
        return create_error_response(
            request.get("id"),
            -32600,
            "Invalid request: missing jsonrpc 2.0 field"
        )

    if "method" not in request:
        return create_error_response(
            request.get("id"),
            -32600,
            "Invalid request: missing method field"
        )

    # Step 3: Check if the method exists
    known_methods = ["tools/list", "tools/call", "resources/list", "initialize"]
    method = request["method"]

    if method not in known_methods:
        return create_error_response(
            request["id"],
            -32601,
            f"Method not found: {method}"
        )

    # Step 4: Validate parameters
    if method == "tools/call":
        params = request.get("params", {})
        if "name" not in params:
            return create_error_response(
                request["id"],
                -32602,
                "Invalid params: 'name' is required for tools/call"
            )

    # Step 5: If everything is valid, return success
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {"status": "ok", "method": method}
    }


if __name__ == "__main__":
    print("=== MCP Error Handling Examples ===\n")

    # Test 1: Invalid JSON
    print("Test 1: Invalid JSON")
    result = handle_request("not valid json{{{")
    print(json.dumps(result, indent=2))

    # Test 2: Missing jsonrpc field
    print("\nTest 2: Missing jsonrpc field")
    result = handle_request('{"method": "tools/list", "id": 1}')
    print(json.dumps(result, indent=2))

    # Test 3: Unknown method
    print("\nTest 3: Unknown method")
    result = handle_request('{"jsonrpc": "2.0", "method": "unknown/method", "id": 2}')
    print(json.dumps(result, indent=2))

    # Test 4: Missing required parameter
    print("\nTest 4: Missing required parameter")
    result = handle_request('{"jsonrpc": "2.0", "method": "tools/call", "params": {}, "id": 3}')
    print(json.dumps(result, indent=2))

    # Test 5: Valid request
    print("\nTest 5: Valid request")
    result = handle_request('{"jsonrpc": "2.0", "method": "tools/list", "id": 4}')
    print(json.dumps(result, indent=2))

    print("\n=== All error codes demonstrated! ===")
