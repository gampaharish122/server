from mcp.server.fastmcp import FastMCP
from typing import Dict, Optional
import requests
from datetime import datetime

# Constants (config only, not context-sensitive)
API_TOKEN = "jSUS2ZMHsdRF7seneARayXzrs2H5pqwdeU4qwSxDq="
PORT = 10000
DISPLAY_NAME = "POC"

# API Endpoints
ENDPOINTS = {
    "overall": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetOverallData",
    "timeline": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTimelineData",
    "top_concepts": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopConcepts",
    "top_companies": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopCompanies",
    "top_themes": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopThemes",
    "top_hashtags": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopHashtags",
    "top_contributors": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopContributors",
    "social_posts": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetSocialMediaPosts",
    "influencers": "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetInfluencerListing",
}

# Initialize MCP server (stateless by design)
mcp = FastMCP("web-search", host="0.0.0.0", port=PORT)

def validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Use DD-MM-YYYY.")

def build_url(
    endpoint: str,
    Keyword: Optional[str] = None,
    FromDate: Optional[str] = None,
    ToDate: Optional[str] = None,
    add_frequency: bool = False,
    keyword_before_dates: bool = False
) -> str:
    # Validate dates
    if FromDate:
        FromDate = validate_date(FromDate)
    if ToDate:
        ToDate = validate_date(ToDate)

    url = f"{endpoint}?TokenID={API_TOKEN}&DisplayName={DISPLAY_NAME}"

    if add_frequency:
        url += "&Frequency=Day"

    if Keyword:
        url += "&SiteName=Disruptor&Source=All&Sentiment=All"
        if keyword_before_dates and FromDate and ToDate:
            url += f"&Keyword={Keyword}&FromDate={FromDate}&ToDate={ToDate}"
        elif FromDate and ToDate:
            url += f"&FromDate={FromDate}&ToDate={ToDate}&Keyword={Keyword}"

    return url

def call_api(url: str) -> Dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Register tools (each request must provide all inputs)
@mcp.tool()
def web_search(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["overall"], Keyword, FromDate, ToDate)
    return call_api(url)

@mcp.tool()
def GetTimelineData(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["timeline"], Keyword, FromDate, ToDate, add_frequency=True)
    return call_api(url)

@mcp.tool()
def GetTopConcepts(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["top_concepts"], Keyword, FromDate, ToDate, keyword_before_dates=True)
    return call_api(url)

@mcp.tool()
def GetTopCompanies(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["top_companies"], Keyword, FromDate, ToDate)
    return call_api(url)

@mcp.tool()
def GetTopThemes(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["top_themes"], Keyword, FromDate, ToDate)
    return call_api(url)

@mcp.tool()
def GetTopHashtags(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["top_hashtags"], Keyword, FromDate, ToDate)
    return call_api(url)

@mcp.tool()
def GetTopContributors(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["top_contributors"], Keyword, FromDate, ToDate)
    return call_api(url)

@mcp.tool()
def GetSocialMediaPosts(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    url = build_url(ENDPOINTS["social_posts"], Keyword, FromDate, ToDate)
    return call_api(url)

@mcp.tool()
def GetInfluencerListing() -> Dict:
    url = build_url(ENDPOINTS["influencers"])
    data = call_api(url)

    if isinstance(data, list):
        return {"result": {"influencers": data}}
    elif isinstance(data, dict):
        return {"result": data}
    return {"result": {}}

# Start the stateless HTTP server
if __name__ == "__main__":
    mcp.run(transport="http")
