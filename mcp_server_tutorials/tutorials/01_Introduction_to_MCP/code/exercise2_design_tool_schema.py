"""
Exercise 2: Design Tool Schemas for a Weather Service
======================================================

YOUR TASK:
Design JSON Schema tool definitions for a weather service MCP server.

You need to create tool schemas for:

1. get_weather
   - Returns current weather for a city
   - Required: city (string)
   - Optional: units (string, enum: "celsius" or "fahrenheit")

2. get_forecast
   - Returns a multi-day weather forecast
   - Required: city (string), days (integer, between 1 and 14)
   - Optional: units (string, enum: "celsius" or "fahrenheit")

3. get_alerts
   - Returns active weather alerts for a region
   - Required: region (string)
   - Optional: severity (string, enum: "minor", "moderate", "severe", "extreme")
   - Optional: active_only (boolean)

For each tool, you need:
  - name: unique identifier
  - description: clear description the AI reads to decide when to use it
  - inputSchema: JSON Schema with properties, types, and required fields

HINTS:
- Use "type": "object" as the top-level type for inputSchema
- Use "enum" to restrict values to a specific set
- Use "minimum" and "maximum" for integer bounds
- List required fields in the "required" array
- Print each schema with json.dumps(schema, indent=2)

Run the solution file to see the expected output:
  python exercise2_solution.py
"""

import json

print("=" * 70)
print("Exercise 2: Design Tool Schemas for a Weather Service")
print("=" * 70)

# TODO: Create your tool schemas below
# Each schema should be a Python dictionary

# ============================================================
# 1. get_weather tool schema
# ============================================================
print("\n--- 1. get_weather ---")

# get_weather_tool = {
#     "name": "get_weather",
#     "description": "...",
#     "inputSchema": {
#         "type": "object",
#         "properties": { ... },
#         "required": [ ... ]
#     }
# }
# print(json.dumps(get_weather_tool, indent=2))

# ============================================================
# 2. get_forecast tool schema
# ============================================================
print("\n--- 2. get_forecast ---")

# get_forecast_tool = {
#     "name": "get_forecast",
#     "description": "...",
#     "inputSchema": {
#         "type": "object",
#         "properties": { ... },
#         "required": [ ... ]
#     }
# }
# print(json.dumps(get_forecast_tool, indent=2))

# ============================================================
# 3. get_alerts tool schema
# ============================================================
print("\n--- 3. get_alerts ---")

# get_alerts_tool = {
#     "name": "get_alerts",
#     "description": "...",
#     "inputSchema": {
#         "type": "object",
#         "properties": { ... },
#         "required": [ ... ]
#     }
# }
# print(json.dumps(get_alerts_tool, indent=2))

# ============================================================
# BONUS: Build a tool registry and simulate a tools/list response
# ============================================================
print("\n--- BONUS: tools/list response ---")

# tool_registry = [get_weather_tool, get_forecast_tool, get_alerts_tool]
# tools_list_response = {
#     "jsonrpc": "2.0",
#     "id": 1,
#     "result": {
#         "tools": tool_registry
#     }
# }
# print(json.dumps(tools_list_response, indent=2))

print("\n" + "=" * 70)
print("Replace the TODO comments with your code!")
print("Run exercise2_solution.py to see the expected output.")
print("=" * 70)


if __name__ == "__main__":
    pass
