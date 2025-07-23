from mcp.server.fastmcp import FastMCP
from typing import Dict, Optional
import requests
from datetime import datetime
import os

# Configuration - Load from environment variables for better security and flexibility
API_TOKEN = os.getenv("API_TOKEN", "jSUS2ZMHsdRF7seneARayXzrs2H5pqwdeU4qwSxDq=")
BASE_URL = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content"
PORT = int(os.getenv("PORT", "10000"))

# API endpoints
ENDPOINTS = {
    "overall": f"{BASE_URL}/GetOverallData",
    "timeline": f"{BASE_URL}/GetTimelineData", 
    "concepts": f"{BASE_URL}/GetTopConcepts",
    "companies": f"{BASE_URL}/GetTopCompanies",
    "themes": f"{BASE_URL}/GetTopThemes",
    "hashtags": f"{BASE_URL}/GetTopHashtags",
    "contributors": f"{BASE_URL}/GetTopContributors",
    "posts": f"{BASE_URL}/GetSocialMediaPosts",
    "influencers": f"{BASE_URL}/GetInfluencerListing"
}

# Initialize MCP server with stateless configuration
mcp = FastMCP("web-search",stateless_http=True, host="0.0.0.0", port=PORT)

def validate_date_format(date_str: str) -> str:
    """Validate DD-MM-YYYY format - pure function, no state."""
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Use DD-MM-YYYY.")

def build_url(endpoint: str, **params) -> str:
    """Build URL with parameters - pure function, no state."""
    url = f"{endpoint}?TokenID={API_TOKEN}&DisplayName=POC"
    
    # Add frequency if specified
    if params.get('add_frequency'):
        url += "&Frequency=Day"
    
    # Add keyword-related parameters
    if params.get('Keyword'):
        url += "&SiteName=Disruptor&Source=All&Sentiment=All"
        
        # Handle different parameter orders
        if params.get('keyword_before_dates') and params.get('FromDate') and params.get('ToDate'):
            url += f"&Keyword={params['Keyword']}&FromDate={params['FromDate']}&ToDate={params['ToDate']}"
        elif params.get('FromDate') and params.get('ToDate'):
            url += f"&FromDate={params['FromDate']}&ToDate={params['ToDate']}&Keyword={params['Keyword']}"
    
    return url

def make_api_request(url: str) -> Dict:
    """Make HTTP request - stateless operation."""
    try:
        response = requests.get(url, timeout=30)  # Add timeout for better reliability
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def fetch_data(endpoint_key: str, **params) -> Dict:
    """Generic data fetcher - completely stateless."""
    # Validate dates if provided
    for date_field in ['FromDate', 'ToDate']:
        if params.get(date_field):
            try:
                params[date_field] = validate_date_format(params[date_field])
            except ValueError as e:
                return {"error": str(e)}
    
    # Build URL and make request
    endpoint = ENDPOINTS[endpoint_key]
    url = build_url(endpoint, **params)
    return make_api_request(url)

# Stateless tool functions - each request is independent
@mcp.tool()
def web_search(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Search overall data - stateless operation."""
    return fetch_data("overall", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

@mcp.tool()
def GetTimelineData(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get timeline data - stateless operation."""
    return fetch_data("timeline", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate, add_frequency=True)

@mcp.tool()
def GetTopConcepts(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get top concepts - stateless operation."""
    return fetch_data("concepts", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate, keyword_before_dates=True)

@mcp.tool()
def GetTopCompanies(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get top companies - stateless operation."""
    return fetch_data("companies", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

@mcp.tool()
def GetTopThemes(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get top themes - stateless operation."""
    return fetch_data("themes", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

@mcp.tool()
def GetTopHashtags(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get top hashtags - stateless operation."""
    return fetch_data("hashtags", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

@mcp.tool()
def GetTopContributors(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get top contributors - stateless operation."""
    return fetch_data("contributors", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

@mcp.tool()
def GetSocialMediaPosts(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    """Get social media posts - stateless operation."""
    return fetch_data("posts", Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

@mcp.tool()
def GetInfluencerListing() -> Dict:
    """Get influencer listing - stateless operation."""
    url = f"{ENDPOINTS['influencers']}?TokenID={API_TOKEN}&DisplayName=POC"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Normalize response format
        if isinstance(data, list):
            return {"result": {"influencers": data}}
        elif isinstance(data, dict):
            return {"result": data}
        else:
            return {"result": {}}
    except requests.RequestException as e:
        return {"result": {"error": str(e)}}

# Health check endpoint for stateless verification
@mcp.tool()
def health_check() -> Dict:
    """Health check - demonstrates stateless operation."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": len(ENDPOINTS),
        "stateless": True
    }

# Start server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
