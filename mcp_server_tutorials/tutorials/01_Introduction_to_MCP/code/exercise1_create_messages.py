"""
Exercise 1: Create JSON-RPC Messages for a Calculator Tool
============================================================

YOUR TASK:
Create the complete set of JSON-RPC messages for a calculator MCP server.

You need to create:

1. An initialize request from a client called "CalculatorClient" version "1.0.0"
2. An initialize response from a server called "CalculatorServer" version "1.0.0"
   (the server supports tools only, no resources or prompts)
3. An initialized notification
4. A tools/list request
5. A tools/list response with these tools:
   - add: adds two numbers (a and b, both required numbers)
   - subtract: subtracts b from a (a and b, both required numbers)
   - multiply: multiplies two numbers (a and b, both required numbers)
   - divide: divides a by b (a and b, both required numbers)
6. A tools/call request to multiply 12 by 5
7. A successful tools/call response with the result "60"
8. A tools/call request to divide 10 by 0
9. A tools/call error response (isError=True) saying division by zero

HINTS:
- Use json.dumps() to print each message
- Follow the JSON-RPC 2.0 format
- Use incrementing IDs for requests (1, 2, 3, ...)
- Notifications do NOT have an "id" field
- Tool results use "content" array with type "text"

Run the solution file to see the expected output:
  python exercise1_solution.py
"""

import json

print("=" * 70)
print("Exercise 1: Create JSON-RPC Messages for a Calculator Tool")
print("=" * 70)

# TODO: Create your messages below
# Each message should be a Python dictionary

# 1. Initialize request
print("\n--- 1. Initialize Request ---")
# initialize_request = { ... }
# print(json.dumps(initialize_request, indent=2))

# 2. Initialize response
print("\n--- 2. Initialize Response ---")
# initialize_response = { ... }
# print(json.dumps(initialize_response, indent=2))

# 3. Initialized notification
print("\n--- 3. Initialized Notification ---")
# initialized_notification = { ... }
# print(json.dumps(initialized_notification, indent=2))

# 4. tools/list request
print("\n--- 4. tools/list Request ---")
# tools_list_request = { ... }
# print(json.dumps(tools_list_request, indent=2))

# 5. tools/list response with 4 calculator tools
print("\n--- 5. tools/list Response ---")
# tools_list_response = { ... }
# print(json.dumps(tools_list_response, indent=2))

# 6. tools/call request: multiply 12 by 5
print("\n--- 6. tools/call Request (multiply) ---")
# multiply_request = { ... }
# print(json.dumps(multiply_request, indent=2))

# 7. tools/call response: result is 60
print("\n--- 7. tools/call Response (success) ---")
# multiply_response = { ... }
# print(json.dumps(multiply_response, indent=2))

# 8. tools/call request: divide 10 by 0
print("\n--- 8. tools/call Request (divide by zero) ---")
# divide_request = { ... }
# print(json.dumps(divide_request, indent=2))

# 9. tools/call error response
print("\n--- 9. tools/call Response (error) ---")
# divide_response = { ... }
# print(json.dumps(divide_response, indent=2))

print("\n" + "=" * 70)
print("Replace the TODO comments with your code!")
print("Run exercise1_solution.py to see the expected output.")
print("=" * 70)


if __name__ == "__main__":
    pass
