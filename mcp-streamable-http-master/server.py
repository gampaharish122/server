
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Dict, List



  
# Tavily API key
TAVILY_API_KEY = "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"

# Initialize Tavily client
tavily_client = TavilyClient(TAVILY_API_KEY)



# Create an MCP server
mcp = FastMCP("web-search", host="0.0.0.0", port=1000)

# Add a tool that uses Tavily
@mcp.tool()
def web_search(query: str) -> List[Dict]:
    """
    Use this tool to search the web for information.

    Args:
        query: The search query.

    Returns:
        The search results.
    """
    try:
        response = tavily_client.search(query)
        return response["results"]
    except:
        return "No results found"

# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
