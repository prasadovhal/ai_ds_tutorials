"""
Wikipedia MCP Server
====================
Search and fetch articles from Wikipedia using its REST API.
Uses httpx for async HTTP requests. No API key needed.
"""

# Import FastMCP and httpx
from mcp.server.fastmcp import FastMCP
import httpx

# Create the MCP server instance
server = FastMCP("Wikipedia Server")

# Wikipedia API base URL
WIKI_API = "https://en.wikipedia.org/api/rest_v1"
WIKI_SEARCH_API = "https://en.wikipedia.org/w/api.php"


# --- Tool: Search Wikipedia ---
@server.tool()
async def search(query: str) -> str:
    """Search Wikipedia for articles matching a query. Returns top 5 results."""
    # Build the search URL using the MediaWiki API
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 5,
        "format": "json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WIKI_SEARCH_API, params=params, timeout=10.0)
            response.raise_for_status()

        data = response.json()
        results = data.get("query", {}).get("search", [])

        if not results:
            return f"No Wikipedia articles found for '{query}'."

        # Build results list
        output = f"Wikipedia search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            title = result["title"]
            # Remove HTML tags from snippet
            snippet = result["snippet"]
            snippet = snippet.replace("<span class=\"searchmatch\">", "")
            snippet = snippet.replace("</span>", "")
            snippet = snippet.replace("&quot;", '"')
            output += f"  {i}. {title}\n     {snippet}...\n\n"

        return output.strip()

    except httpx.RequestError as e:
        return f"Error connecting to Wikipedia: {str(e)}"


# --- Tool: Get a Wikipedia article ---
@server.tool()
async def get_article(title: str) -> str:
    """Get the summary of a Wikipedia article by its title."""
    # Use the REST API summary endpoint
    url = f"{WIKI_API}/page/summary/{title}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()

        data = response.json()

        # Extract the article info
        article_title = data.get("title", title)
        extract = data.get("extract", "No content available.")
        description = data.get("description", "No description.")
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        output = f"""
Wikipedia: {article_title}
Description: {description}

{extract}

Link: {page_url}
"""
        return output.strip()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Article '{title}' not found on Wikipedia."
        return f"HTTP Error: {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to Wikipedia: {str(e)}"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
