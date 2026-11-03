"""
Exercise 1: Currency Converter MCP Server (Stub)
=================================================
YOUR TASK: Build a currency converter MCP server with hardcoded exchange rates.

Requirements:
1. Create a dictionary of exchange rates (base: USD)
2. Implement these tools:
   - convert(amount, from_currency, to_currency) -> converted amount
   - list_currencies() -> show all available currencies
   - get_rate(from_currency, to_currency) -> show the exchange rate

Hints:
- Store rates relative to USD, e.g., {"EUR": 0.85, "GBP": 0.73, ...}
- To convert between non-USD currencies, first convert to USD, then to target
- Use upper() on currency codes for case-insensitive matching

See exercise1_solution.py for the complete solution.
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
server = FastMCP("Currency Converter")

# TODO: Define exchange rates dictionary (base: USD)
# RATES = { "USD": 1.0, "EUR": 0.85, ... }

# TODO: Implement convert tool
# @server.tool()
# def convert(amount: float, from_currency: str, to_currency: str) -> str:
#     pass

# TODO: Implement list_currencies tool
# @server.tool()
# def list_currencies() -> str:
#     pass

# TODO: Implement get_rate tool
# @server.tool()
# def get_rate(from_currency: str, to_currency: str) -> str:
#     pass


if __name__ == "__main__":
    server.run()
