"""
Weather MCP Server
==================
Fetches real weather data from wttr.in (no API key needed).
Uses httpx for async HTTP requests.
"""

# Import FastMCP and httpx for HTTP requests
from mcp.server.fastmcp import FastMCP
import httpx

# Create the MCP server instance
server = FastMCP("Weather Server")


# --- Tool: Get weather for a city ---
@server.tool()
async def get_weather(city: str) -> str:
    """
    Get current weather for a given city.
    Uses the free wttr.in API (no API key required).
    """
    # Build the URL for wttr.in JSON format
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # Make an async HTTP GET request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract current condition info
        current = data["current_condition"][0]

        # Build a readable weather report
        weather_report = f"""
Weather for {city}:
  Temperature: {current['temp_C']}°C ({current['temp_F']}°F)
  Feels Like: {current['FeelsLikeC']}°C ({current['FeelsLikeF']}°F)
  Condition: {current['weatherDesc'][0]['value']}
  Humidity: {current['humidity']}%
  Wind: {current['windspeedKmph']} km/h {current['winddir16Point']}
  Visibility: {current['visibility']} km
  UV Index: {current['uvIndex']}
"""
        return weather_report.strip()

    except httpx.HTTPStatusError as e:
        return f"Error: Could not fetch weather data. HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error: Could not connect to weather service. {str(e)}"
    except (KeyError, IndexError):
        return f"Error: Could not parse weather data for '{city}'. Check the city name."


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
