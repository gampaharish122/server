from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Dict
import os
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

# Validate required environment variables
if "API_TOKEN" not in os.environ or "API_ENDPOINT" not in os.environ:
    raise Exception("API_TOKEN or API_ENDPOINT environment variable not set")

API_TOKEN = os.environ["API_TOKEN"]
API_ENDPOINT = os.environ["API_ENDPOINT"]
PORT = int(os.environ.get("PORT", 10000))

# Initialize MCP server
mcp = FastMCP("web-search", host="0.0.0.0", port=PORT)

# Validate DD-MM-YYYY format
def validate_date_format(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Use DD-MM-YYYY.")

# Function to build and call the API
def fetch_data(DisplayName: str, Keyword: str, FromDate: str, ToDate: str) -> Dict:
    try:
        from_date = validate_date_format(FromDate)
        to_date = validate_date_format(ToDate)
    except ValueError as e:
        return {"error": str(e)}

    # Keyword placed last
    url = (
        f"{API_ENDPOINT}?"
        f"TokenID={API_TOKEN}"
        f"&DisplayName={DisplayName}"
        f"&SiteName=Disruptor"
        f"&Source=All"
        f"&Sentiment=All"
        f"&FromDate={from_date}"
        f"&ToDate={to_date}"
        f"&Keyword={Keyword}"  # MUST be last
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Exposed tool
@mcp.tool()
def web_search(DisplayName: str, Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """
    Query the external API using DD-MM-YYYY dates and specified parameters.
    """
    return fetch_data(DisplayName, Keyword, FromDate, ToDate)

# Start server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
