import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_URL = "https://techport.nasa.gov"
API_KEY = os.getenv("NASA_API_KEY", "")

# request header
# simulating a web browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def _make_request(endpoint: str, params: dict = None):
    """
    Helper function to send GET requests with browser headers and API Key query params.
    """
    if params is None:
        params = {}
    
    """add "api_key=NASA_API_KEY" as a url param"""
    if API_KEY:
        params["api_key"] = API_KEY

    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def fetch_status_values():
    """Fetches project status types from /api/enums."""
    data = _make_request("/api/enums")
    return data.get("enums", {}).get("projectStatusType", [])


def fetch_technologies():
    """Fetches technology taxonomies from /api/taxonomies/8817."""
    data = _make_request("/api/taxonomies/8817")
    return data.get("children", [])


def fetch_destinations():
    """Fetches destination types from /api/enums."""
    data = _make_request("/api/enums")
    return data.get("enums", {}).get("destinationTypes", [])


def fetch_nasa_pjs_attributes():
    return {
        "statuses": fetch_status_values(),
        "technologies": fetch_technologies(),
        "destinations": fetch_destinations()
    }


# def fetch_nasa_relevant_projects():
