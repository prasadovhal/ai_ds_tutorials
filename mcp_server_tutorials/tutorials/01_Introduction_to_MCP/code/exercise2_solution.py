"""
Exercise 2 Solution: Design Tool Schemas for a Weather Service
===============================================================

This is the complete solution for Exercise 2.
Each tool schema follows the JSON Schema format used by MCP.

Key concepts demonstrated:
  - Required vs optional parameters
  - Enum constraints (restricting to specific values)
  - Integer bounds (minimum/maximum)
  - Boolean parameters
  - Building a tool registry for a tools/list response
"""

import json

print("=" * 70)
print("Exercise 2 SOLUTION: Tool Schemas for a Weather Service")
print("=" * 70)

# ============================================================
# 1. get_weather Tool Schema
# ============================================================

print("\n--- 1. get_weather ---")

# This tool returns current weather for a given city.
# "city" is required because we cannot get weather without knowing where.
# "units" is optional because we can default to celsius.
get_weather_tool = {
    "name": "get_weather",

    # The description tells the AI WHEN to use this tool.
    # Be specific about what it returns so the AI can decide correctly.
    "description": "Get the current weather conditions for a specified city. Returns temperature, humidity, wind speed, and weather description.",

    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                # Good descriptions help the AI provide correct values
                "description": "The name of the city to get weather for (e.g., 'London', 'New York', 'Tokyo')"
            },
            "units": {
                "type": "string",
                "description": "Temperature units to use. Defaults to 'celsius' if not specified.",
                # enum means ONLY these two values are allowed
                # The AI will only ever send one of these
                "enum": ["celsius", "fahrenheit"]
            }
        },
        # Only city is required -- units has a default
        "required": ["city"]
    }
}
print(json.dumps(get_weather_tool, indent=2))

# ============================================================
# 2. get_forecast Tool Schema
# ============================================================

print("\n--- 2. get_forecast ---")

# This tool returns a multi-day forecast.
# Both "city" and "days" are required because the tool needs
# to know WHERE and for HOW LONG to forecast.
get_forecast_tool = {
    "name": "get_forecast",

    "description": "Get a multi-day weather forecast for a specified city. Returns daily high/low temperatures, precipitation chance, and conditions for each day.",

    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city to get the forecast for (e.g., 'Paris', 'Berlin', 'Sydney')"
            },
            "days": {
                "type": "integer",
                "description": "Number of days to forecast (1 to 14). For example, 7 gives a week-long forecast.",
                # minimum and maximum set the allowed range
                # The server should reject values outside this range
                "minimum": 1,
                "maximum": 14
            },
            "units": {
                "type": "string",
                "description": "Temperature units to use. Defaults to 'celsius' if not specified.",
                "enum": ["celsius", "fahrenheit"]
            }
        },
        # Both city and days are required for a forecast
        "required": ["city", "days"]
    }
}
print(json.dumps(get_forecast_tool, indent=2))

# ============================================================
# 3. get_alerts Tool Schema
# ============================================================

print("\n--- 3. get_alerts ---")

# This tool returns active weather alerts for a region.
# "region" is required. "severity" and "active_only" are optional filters.
get_alerts_tool = {
    "name": "get_alerts",

    "description": "Get active weather alerts and warnings for a specified region. Returns alert type, severity, description, and time range for each active alert.",

    "inputSchema": {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "The region or area to check for alerts (e.g., 'California', 'Southeast England', 'Hokkaido')"
            },
            "severity": {
                "type": "string",
                "description": "Filter alerts by minimum severity level. If not specified, all alerts are returned.",
                # Four severity levels from least to most severe
                "enum": ["minor", "moderate", "severe", "extreme"]
            },
            "active_only": {
                "type": "boolean",
                "description": "If true, only return currently active alerts. If false, include recently expired alerts. Defaults to true."
            }
        },
        # Only region is required -- severity and active_only are filters
        "required": ["region"]
    }
}
print(json.dumps(get_alerts_tool, indent=2))

# ============================================================
# BONUS: Build a Tool Registry and tools/list Response
# ============================================================

print("\n--- BONUS: Complete tools/list Response ---")

# In an MCP server, all tools are kept in a registry.
# When a client sends a tools/list request, the server
# returns all the tool schemas in the response.
tool_registry = [get_weather_tool, get_forecast_tool, get_alerts_tool]

# This is exactly what the server would send back
tools_list_response = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "tools": tool_registry
    }
}

print(json.dumps(tools_list_response, indent=2))

# ============================================================
# Summary
# ============================================================

print("\n" + "=" * 70)
print("SOLUTION SUMMARY")
print("=" * 70)

print(f"\nTotal tools defined: {len(tool_registry)}")
print("-" * 50)

# Print a summary of each tool
for tool in tool_registry:
    properties = tool["inputSchema"].get("properties", {})
    required = tool["inputSchema"].get("required", [])
    optional_count = len(properties) - len(required)

    print(f"\n  Tool: {tool['name']}")
    print(f"  Description: {tool['description'][:60]}...")
    print(f"  Required args: {required}")
    print(f"  Optional args: {optional_count}")

    # Show which properties use enum constraints
    for prop_name, prop_schema in properties.items():
        if "enum" in prop_schema:
            print(f"  Enum constraint on '{prop_name}': {prop_schema['enum']}")

print("\n" + "=" * 70)
print("""
Key patterns to remember:
  1. Every tool needs: name, description, inputSchema
  2. inputSchema is always "type": "object" at the top level
  3. Use "required" array to mark mandatory parameters
  4. Use "enum" to restrict string values to a set of options
  5. Use "minimum"/"maximum" for integer bounds
  6. Use "boolean" type for true/false flags
  7. Good descriptions help the AI choose the right tool
""")


if __name__ == "__main__":
    pass
