"""
Exercise 1 Solution: Currency Converter MCP Server
====================================================
A currency converter using hardcoded exchange rates (base: USD).
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
server = FastMCP("Currency Converter")

# Hardcoded exchange rates relative to USD
RATES = {
    "USD": 1.0,
    "EUR": 0.85,
    "GBP": 0.73,
    "JPY": 110.0,
    "INR": 83.0,
    "CAD": 1.36,
    "AUD": 1.53,
    "CHF": 0.88,
    "CNY": 7.24,
    "KRW": 1320.0,
    "MXN": 17.15,
    "BRL": 4.95,
}


# --- Tool: Convert between currencies ---
@server.tool()
def convert(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another."""
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    # Validate currencies
    if from_code not in RATES:
        return f"Error: Unknown currency '{from_code}'. Use list_currencies to see available ones."
    if to_code not in RATES:
        return f"Error: Unknown currency '{to_code}'. Use list_currencies to see available ones."

    # Convert: from_currency -> USD -> to_currency
    usd_amount = amount / RATES[from_code]
    result = usd_amount * RATES[to_code]

    return f"{amount:.2f} {from_code} = {result:.2f} {to_code}"


# --- Tool: List all available currencies ---
@server.tool()
def list_currencies() -> str:
    """List all available currencies and their USD exchange rates."""
    result = "Available Currencies (rate vs 1 USD):\n\n"
    for code, rate in sorted(RATES.items()):
        result += f"  {code}: {rate}\n"
    return result


# --- Tool: Get exchange rate ---
@server.tool()
def get_rate(from_currency: str, to_currency: str) -> str:
    """Get the exchange rate between two currencies."""
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    if from_code not in RATES:
        return f"Error: Unknown currency '{from_code}'."
    if to_code not in RATES:
        return f"Error: Unknown currency '{to_code}'."

    # Calculate the cross rate
    rate = RATES[to_code] / RATES[from_code]
    return f"1 {from_code} = {rate:.4f} {to_code}"


if __name__ == "__main__":
    server.run()
