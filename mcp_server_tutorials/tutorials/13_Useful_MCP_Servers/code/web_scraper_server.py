"""
Web Scraper MCP Server
======================
Fetch web pages and extract basic information using httpx
and simple string parsing (no external HTML parsing libraries needed).
"""

# Import FastMCP and httpx
from mcp.server.fastmcp import FastMCP
import httpx
import re

# Create the MCP server instance
server = FastMCP("Web Scraper Server")


# --- Helper: Fetch HTML from a URL ---
async def _fetch_html(url: str) -> str:
    """Fetch HTML content from a URL."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=15.0)
        response.raise_for_status()
        return response.text


# --- Tool: Fetch a web page ---
@server.tool()
async def fetch_page(url: str) -> str:
    """Fetch the raw HTML content of a web page (first 5000 chars)."""
    try:
        html = await _fetch_html(url)

        # Limit output to first 5000 characters
        if len(html) > 5000:
            return f"Page content from '{url}' (first 5000 chars):\n\n{html[:5000]}\n\n... truncated ({len(html)} total chars)"
        return f"Page content from '{url}':\n\n{html}"

    except httpx.HTTPStatusError as e:
        return f"HTTP Error: {e.response.status_code} for '{url}'"
    except httpx.RequestError as e:
        return f"Error fetching '{url}': {str(e)}"


# --- Tool: Extract the page title ---
@server.tool()
async def extract_title(url: str) -> str:
    """Extract the <title> tag from a web page."""
    try:
        html = await _fetch_html(url)

        # Use regex to find the title tag
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)

        if match:
            title = match.group(1).strip()
            return f"Title of '{url}': {title}"
        else:
            return f"No <title> tag found on '{url}'."

    except httpx.HTTPStatusError as e:
        return f"HTTP Error: {e.response.status_code} for '{url}'"
    except httpx.RequestError as e:
        return f"Error fetching '{url}': {str(e)}"


# --- Tool: Extract all links from a page ---
@server.tool()
async def extract_links(url: str) -> str:
    """Extract all hyperlinks (<a href>) from a web page."""
    try:
        html = await _fetch_html(url)

        # Use regex to find all href attributes in <a> tags
        links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\']', html, re.IGNORECASE)

        if not links:
            return f"No links found on '{url}'."

        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        # Build result (limit to first 50 links)
        result = f"Links found on '{url}' ({len(unique_links)} unique):\n\n"
        for i, link in enumerate(unique_links[:50], 1):
            result += f"  {i}. {link}\n"

        if len(unique_links) > 50:
            result += f"\n  ... and {len(unique_links) - 50} more links."

        return result

    except httpx.HTTPStatusError as e:
        return f"HTTP Error: {e.response.status_code} for '{url}'"
    except httpx.RequestError as e:
        return f"Error fetching '{url}': {str(e)}"


# Run the server when this file is executed directly
if __name__ == "__main__":
    server.run()
