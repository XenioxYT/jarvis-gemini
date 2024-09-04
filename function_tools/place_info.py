import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_place_information(query: str, open_now: bool = False) -> dict:
    GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not GOOGLE_CLOUD_API_KEY:
        return {"error": "Google Cloud API key not found"}

    base_url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_CLOUD_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.types,places.rating"
    }
    
    data = {
        "textQuery": query,
        "maxResultCount": 5
    }
    
    if open_now:
        data["openNow"] = open_now
    
    try:
        response = requests.post(base_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        return {"error": f"Places API request failed: {str(e)}"}
    
    return {
        "status": "OK",
        "results": [
            {
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "types": place.get("types", []),
                "rating": place.get("rating")
            } for place in result.get("places", [])
        ]
    }