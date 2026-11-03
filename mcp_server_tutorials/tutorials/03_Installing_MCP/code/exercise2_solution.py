"""
Exercise 2 Solution: Greeting Server
"""

from mcp.server.fastmcp import FastMCP

# Create the server
server = FastMCP("greeting-server")

# Define greetings in different languages
GREETINGS = {
    "english": "Hello",
    "spanish": "Hola",
    "french": "Bonjour",
    "german": "Hallo",
    "japanese": "Konnichiwa",
    "hindi": "Namaste",
}


@server.tool()
def greet(name: str, language: str = "english") -> str:
    """Greet someone in a specified language."""
    # Convert language to lowercase for matching
    language_lower = language.lower()

    # Check if the language is supported
    if language_lower not in GREETINGS:
        supported = ", ".join(GREETINGS.keys())
        return f"Error: Language '{language}' not supported. Supported: {supported}"

    # Get the greeting word
    greeting_word = GREETINGS[language_lower]

    # Build the full greeting
    result = f"{greeting_word}, {name}!"
    return result


@server.tool()
def list_languages() -> str:
    """List all supported languages."""
    languages = list(GREETINGS.keys())
    return f"Supported languages: {', '.join(languages)}"


if __name__ == "__main__":
    server.run()
