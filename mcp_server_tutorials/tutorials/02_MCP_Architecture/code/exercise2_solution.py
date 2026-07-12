"""
Exercise 2 Solution: Comprehensive Error Handler
"""

import json
import time


# Map error codes to names and descriptions
ERROR_CODES = {
    -32700: {
        "name": "Parse Error",
        "description": "Invalid JSON was received by the server",
    },
    -32600: {
        "name": "Invalid Request",
        "description": "The JSON is not a valid JSON-RPC request",
    },
    -32601: {
        "name": "Method Not Found",
        "description": "The requested method does not exist",
    },
    -32602: {
        "name": "Invalid Params",
        "description": "Invalid method parameters were provided",
    },
    -32603: {
        "name": "Internal Error",
        "description": "An internal server error occurred",
    },
}


class ErrorHandler:
    """Handles all MCP JSON-RPC errors with logging."""

    def __init__(self):
        # Store all errors that have occurred
        self.error_log = []

    def create_error_response(self, request_id, error_code, details=None):
        """Create a properly formatted JSON-RPC error response."""
        # Look up the error info
        error_info = ERROR_CODES.get(error_code, {
            "name": "Unknown Error",
            "description": "An unknown error occurred",
        })

        # Build the error response
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": error_code,
                "message": error_info["name"],
            }
        }

        # Add extra details if provided
        if details:
            response["error"]["data"] = {
                "description": error_info["description"],
                "details": details,
            }

        # Log this error
        self._log_error(error_code, error_info["name"], details)

        return response

    def _log_error(self, code, name, details):
        """Record the error in the log with a timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "code": code,
            "name": name,
            "details": details,
        }
        self.error_log.append(entry)

    def get_error_log(self):
        """Return all logged errors."""
        return self.error_log

    def get_error_count(self):
        """Return the total number of errors."""
        return len(self.error_log)

    def get_errors_by_code(self, code):
        """Return all errors with a specific code."""
        matching = []
        for error in self.error_log:
            if error["code"] == code:
                matching.append(error)
        return matching


if __name__ == "__main__":
    print("=== Error Handler Solution ===\n")

    handler = ErrorHandler()

    # Test each error code
    print("--- Testing all error codes ---\n")

    # Parse Error
    response = handler.create_error_response(1, -32700, "Unexpected token at position 5")
    print(f"Parse Error:\n{json.dumps(response, indent=2)}\n")

    # Invalid Request
    response = handler.create_error_response(2, -32600, "Missing 'method' field")
    print(f"Invalid Request:\n{json.dumps(response, indent=2)}\n")

    # Method Not Found
    response = handler.create_error_response(3, -32601, "Method 'foo/bar' not found")
    print(f"Method Not Found:\n{json.dumps(response, indent=2)}\n")

    # Invalid Params
    response = handler.create_error_response(4, -32602, "Parameter 'name' is required")
    print(f"Invalid Params:\n{json.dumps(response, indent=2)}\n")

    # Internal Error
    response = handler.create_error_response(5, -32603, "Database connection failed")
    print(f"Internal Error:\n{json.dumps(response, indent=2)}\n")

    # Print error log summary
    print(f"--- Error Log Summary ---")
    print(f"Total errors: {handler.get_error_count()}")
    for entry in handler.get_error_log():
        print(f"  [{entry['timestamp']}] {entry['name']}: {entry['details']}")
