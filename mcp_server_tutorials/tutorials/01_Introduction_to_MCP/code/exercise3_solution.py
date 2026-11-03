"""
Exercise 3 Solution: Build a Complete MCP Session Simulation
=============================================================

This solution simulates a complete MCP session between a WeatherClient
and a WeatherServer. It covers all four phases of the MCP lifecycle:
initialization, discovery, usage, and shutdown.

Every message follows the JSON-RPC 2.0 format used by MCP.
"""

import json

print("=" * 70)
print("Exercise 3 SOLUTION: Complete MCP Session Simulation")
print("=" * 70)

# We track message counts for the summary at the end
message_count = 0
request_count = 0
response_count = 0
notification_count = 0

# We use incrementing IDs for each request
request_id = 0


def next_id():
    """Get the next request ID. We increment by 1 each time."""
    global request_id
    request_id = request_id + 1
    return request_id


def send_message(direction, message):
    """Print a message with its direction and update counters."""
    global message_count, request_count, response_count, notification_count

    message_count = message_count + 1

    # Determine what kind of message this is
    has_method = "method" in message
    has_id = "id" in message
    has_result = "result" in message or "error" in message

    if has_method and has_id:
        request_count = request_count + 1
        msg_type = "REQUEST"
    elif has_result:
        response_count = response_count + 1
        msg_type = "RESPONSE"
    elif has_method and not has_id:
        notification_count = notification_count + 1
        msg_type = "NOTIFICATION"
    else:
        msg_type = "UNKNOWN"

    print(f"\n  [{msg_type}] {direction}")
    print(f"  {json.dumps(message, indent=4)}")


# ============================================================
# PHASE 1: INITIALIZATION
# ============================================================

print("\n" + "-" * 70)
print("PHASE 1: INITIALIZATION")
print("-" * 70)
print("The client and server exchange capabilities before doing anything.")

# Step 1: Client sends initialize request
# This is always the FIRST message in any MCP session.
# The client tells the server who it is and what it can do.
initialize_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "roots": {
                "listChanged": True
            }
        },
        "clientInfo": {
            "name": "WeatherClient",
            "version": "1.0.0"
        }
    }
}
send_message("CLIENT -> SERVER", initialize_request)

# Step 2: Server responds with its capabilities
# The server tells the client what features it supports.
# This server supports both tools and resources.
initialize_response = {
    "jsonrpc": "2.0",
    "id": 1,  # Must match the request id
    "result": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "tools": {
                "listChanged": True
            },
            "resources": {
                "subscribe": False,
                "listChanged": True
            }
        },
        "serverInfo": {
            "name": "WeatherServer",
            "version": "2.0.0"
        }
    }
}
send_message("SERVER -> CLIENT", initialize_response)

# Step 3: Client sends initialized notification
# This tells the server "I got your capabilities, let's begin!"
# IMPORTANT: Notifications do NOT have an "id" field.
initialized_notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
send_message("CLIENT -> SERVER", initialized_notification)

print("\nInitialization complete!")
print(f"  Client: {initialize_request['params']['clientInfo']['name']} v{initialize_request['params']['clientInfo']['version']}")
print(f"  Server: {initialize_response['result']['serverInfo']['name']} v{initialize_response['result']['serverInfo']['version']}")

# ============================================================
# PHASE 2: DISCOVERY
# ============================================================

print("\n" + "-" * 70)
print("PHASE 2: DISCOVERY")
print("-" * 70)
print("The client discovers what the server offers.")

# Step 4: Client asks for available tools
tools_list_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "tools/list",
    "params": {}
}
send_message("CLIENT -> SERVER", tools_list_request)

# Step 5: Server responds with its tools
# We include get_weather and get_forecast from Exercise 2
tools_list_response = {
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather conditions for a city",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["city"]
                }
            },
            {
                "name": "get_forecast",
                "description": "Get a multi-day weather forecast for a city",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days (1-14)",
                            "minimum": 1,
                            "maximum": 14
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["city", "days"]
                }
            }
        ]
    }
}
send_message("SERVER -> CLIENT", tools_list_response)

# Print discovered tools
discovered_tools = tools_list_response["result"]["tools"]
print(f"\nDiscovered {len(discovered_tools)} tools:")
for tool in discovered_tools:
    print(f"  - {tool['name']}: {tool['description']}")

# Step 6: Client asks for available resources
resources_list_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "resources/list",
    "params": {}
}
send_message("CLIENT -> SERVER", resources_list_request)

# Step 7: Server responds with its resources
resources_list_response = {
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "resources": [
            {
                "uri": "weather://cities",
                "name": "Supported Cities",
                "description": "List of all cities with weather data available",
                "mimeType": "application/json"
            }
        ]
    }
}
send_message("SERVER -> CLIENT", resources_list_response)

# Print discovered resources
discovered_resources = resources_list_response["result"]["resources"]
print(f"\nDiscovered {len(discovered_resources)} resources:")
for resource in discovered_resources:
    print(f"  - {resource['uri']}: {resource['description']}")

# ============================================================
# PHASE 3: USAGE
# ============================================================

print("\n" + "-" * 70)
print("PHASE 3: USAGE")
print("-" * 70)
print("The client calls tools and reads resources.")

# --- Call 1: get_weather for London (success) ---
print("\n--- Call 1: Get weather for London ---")

weather_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "tools/call",
    "params": {
        "name": "get_weather",
        "arguments": {
            "city": "London",
            "units": "celsius"
        }
    }
}
send_message("CLIENT -> SERVER", weather_request)

# The server processes the request and returns weather data
weather_response = {
    "jsonrpc": "2.0",
    "id": 4,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Weather in London: 18C, Partly Cloudy, Humidity: 72%, Wind: 15 km/h SW"
            }
        ],
        "isError": False
    }
}
send_message("SERVER -> CLIENT", weather_response)

# --- Call 2: get_forecast for Tokyo, 3 days (success) ---
print("\n--- Call 2: Get 3-day forecast for Tokyo ---")

forecast_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "tools/call",
    "params": {
        "name": "get_forecast",
        "arguments": {
            "city": "Tokyo",
            "days": 3
        }
    }
}
send_message("CLIENT -> SERVER", forecast_request)

# Server returns a 3-day forecast
forecast_response = {
    "jsonrpc": "2.0",
    "id": 5,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "3-Day Forecast for Tokyo:\nDay 1: 28C/22C, Sunny, 5% rain\nDay 2: 26C/20C, Cloudy, 30% rain\nDay 3: 24C/19C, Rain, 80% rain"
            }
        ],
        "isError": False
    }
}
send_message("SERVER -> CLIENT", forecast_response)

# --- Call 3: Read the weather://cities resource ---
print("\n--- Call 3: Read supported cities resource ---")

resource_read_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "resources/read",
    "params": {
        "uri": "weather://cities"
    }
}
send_message("CLIENT -> SERVER", resource_read_request)

# Server returns the resource contents
# Note: resources/read uses "contents" (plural), not "content"
resource_read_response = {
    "jsonrpc": "2.0",
    "id": 6,
    "result": {
        "contents": [
            {
                "uri": "weather://cities",
                "mimeType": "application/json",
                "text": json.dumps(["London", "Tokyo", "New York", "Paris", "Sydney", "Berlin"], indent=2)
            }
        ]
    }
}
send_message("SERVER -> CLIENT", resource_read_response)

# --- Call 4: get_weather with invalid city (error) ---
print("\n--- Call 4: Get weather with empty city (error) ---")

invalid_request = {
    "jsonrpc": "2.0",
    "id": next_id(),
    "method": "tools/call",
    "params": {
        "name": "get_weather",
        "arguments": {
            "city": ""
        }
    }
}
send_message("CLIENT -> SERVER", invalid_request)

# Server returns an error response
# Note: This is a TOOL-LEVEL error (isError=True), not a JSON-RPC error.
# The request was valid JSON-RPC, but the tool itself rejected the input.
error_response = {
    "jsonrpc": "2.0",
    "id": 7,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Error: City name cannot be empty. Please provide a valid city name (e.g., 'London', 'Tokyo')."
            }
        ],
        "isError": True
    }
}
send_message("SERVER -> CLIENT", error_response)

print("\nNote: isError=True means the tool ran but reported an error.")
print("The JSON-RPC request itself was valid.")

# ============================================================
# PHASE 4: SHUTDOWN
# ============================================================

print("\n" + "-" * 70)
print("PHASE 4: SHUTDOWN")
print("-" * 70)
print("Session is closing. Printing summary.\n")

print("=" * 50)
print("SESSION SUMMARY")
print("=" * 50)

print(f"\nTotal messages exchanged: {message_count}")
print(f"  Requests:      {request_count}")
print(f"  Responses:     {response_count}")
print(f"  Notifications: {notification_count}")

print(f"\nPhases completed:")
print(f"  1. Initialization -- Client and Server exchanged capabilities")
print(f"  2. Discovery      -- Found {len(discovered_tools)} tools, {len(discovered_resources)} resources")
print(f"  3. Usage          -- Called tools, read resources, handled errors")
print(f"  4. Shutdown       -- Session closed cleanly")

print("\n" + "=" * 70)
print("KEY TAKEAWAYS")
print("=" * 70)
print("""
1. Every session starts with initialize -> initialized notification
2. Discovery happens BEFORE usage (list tools, list resources)
3. Tool calls use "tools/call" with name and arguments
4. Resource reads use "resources/read" with a URI
5. Tool results have "content" array; resource results have "contents" array
6. Tool errors use isError=True (not JSON-RPC error format)
7. Requests have "id"; notifications do NOT have "id"
8. Response "id" must match the request "id"
9. The session is stateful -- the server remembers the client
10. Shutdown happens when either side closes the connection
""")


if __name__ == "__main__":
    pass
