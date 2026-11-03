"""
Exercise 3: Build a Complete MCP Session Simulation
=====================================================

YOUR TASK:
Build a complete MCP session simulation that covers ALL phases
of the MCP lifecycle, from initialization to shutdown.

You need to simulate:

1. INITIALIZATION PHASE
   - Client sends initialize request
     (client name: "WeatherClient", version: "1.0.0")
   - Server sends initialize response
     (server name: "WeatherServer", version: "2.0.0",
      capabilities: tools and resources)
   - Client sends initialized notification

2. DISCOVERY PHASE
   - Client sends tools/list request
   - Server responds with 2 tools: get_weather and get_forecast
     (use the schemas from Exercise 2)
   - Client sends resources/list request
   - Server responds with 1 resource: "weather://cities"

3. USAGE PHASE
   - Client calls get_weather tool with city="London"
   - Server responds with weather data (success)
   - Client calls get_forecast tool with city="Tokyo", days=3
   - Server responds with forecast data (success)
   - Client reads the "weather://cities" resource
   - Server responds with a list of supported cities
   - Client calls get_weather with an invalid city (city="")
   - Server responds with an error (isError=True)

4. SHUTDOWN PHASE
   - Print a session summary with message counts

REQUIREMENTS:
  - Use incrementing IDs for requests (1, 2, 3, ...)
  - Notifications do NOT have an "id" field
  - Print each message with json.dumps(message, indent=2)
  - Label each message with its direction: CLIENT -> SERVER or SERVER -> CLIENT
  - Keep a count of total messages exchanged

HINTS:
  - Tool results use "content" array with "type": "text"
  - Resource results use "contents" array with "uri", "mimeType", and "text"
  - Use isError=True for tool-level errors
  - Refer to example5_session_lifecycle.py for the message format

Run the solution to see expected output:
  python exercise3_solution.py
"""

import json

print("=" * 70)
print("Exercise 3: Complete MCP Session Simulation")
print("=" * 70)

# TODO: Create a message counter
# message_count = 0
# request_id = 0

# ============================================================
# PHASE 1: INITIALIZATION
# ============================================================
print("\n" + "-" * 70)
print("PHASE 1: INITIALIZATION")
print("-" * 70)

# TODO: Create and print the initialize request
print("\n  CLIENT -> SERVER: initialize request")
# initialize_request = { ... }
# print(json.dumps(initialize_request, indent=2))

# TODO: Create and print the initialize response
print("\n  SERVER -> CLIENT: initialize response")
# initialize_response = { ... }
# print(json.dumps(initialize_response, indent=2))

# TODO: Create and print the initialized notification
print("\n  CLIENT -> SERVER: initialized notification")
# initialized_notification = { ... }
# print(json.dumps(initialized_notification, indent=2))

# ============================================================
# PHASE 2: DISCOVERY
# ============================================================
print("\n" + "-" * 70)
print("PHASE 2: DISCOVERY")
print("-" * 70)

# TODO: tools/list request and response
print("\n  CLIENT -> SERVER: tools/list request")
# ...

print("\n  SERVER -> CLIENT: tools/list response")
# ...

# TODO: resources/list request and response
print("\n  CLIENT -> SERVER: resources/list request")
# ...

print("\n  SERVER -> CLIENT: resources/list response")
# ...

# ============================================================
# PHASE 3: USAGE
# ============================================================
print("\n" + "-" * 70)
print("PHASE 3: USAGE")
print("-" * 70)

# TODO: Call get_weather for London (success)
print("\n  CLIENT -> SERVER: tools/call get_weather")
# ...
print("\n  SERVER -> CLIENT: tools/call response (success)")
# ...

# TODO: Call get_forecast for Tokyo, 3 days (success)
print("\n  CLIENT -> SERVER: tools/call get_forecast")
# ...
print("\n  SERVER -> CLIENT: tools/call response (success)")
# ...

# TODO: Read weather://cities resource
print("\n  CLIENT -> SERVER: resources/read")
# ...
print("\n  SERVER -> CLIENT: resources/read response")
# ...

# TODO: Call get_weather with invalid city (error)
print("\n  CLIENT -> SERVER: tools/call get_weather (invalid)")
# ...
print("\n  SERVER -> CLIENT: tools/call response (error)")
# ...

# ============================================================
# PHASE 4: SHUTDOWN
# ============================================================
print("\n" + "-" * 70)
print("PHASE 4: SHUTDOWN")
print("-" * 70)

# TODO: Print session summary
# print(f"Total messages exchanged: {message_count}")
# print(f"  Requests: ...")
# print(f"  Responses: ...")
# print(f"  Notifications: ...")

print("\n" + "=" * 70)
print("Replace the TODO comments with your code!")
print("Run exercise3_solution.py to see the expected output.")
print("=" * 70)


if __name__ == "__main__":
    pass
