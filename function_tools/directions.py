import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

from function_tools.place_info import get_place_information

def get_directions(origin: str, destination: str, travel_mode: str = "DRIVE") -> dict:
    GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not GOOGLE_CLOUD_API_KEY:
        return {"error": "Google Cloud API key not found"}

    base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_CLOUD_API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.navigationInstruction"
    }
    
    def get_top_result_address(query):
        place_info = get_place_information(query)
        if place_info.get("status") == "OK" and place_info.get("results"):
            return place_info["results"][0]["address"]
        return query

    origin_address = get_top_result_address(origin)
    destination_address = get_top_result_address(destination)
    
    valid_modes = {"DRIVE", "WALK", "BICYCLE", "TRANSIT"}
    travel_mode = travel_mode.upper()
    if travel_mode not in valid_modes:
        return {"error": f"Invalid travel mode. Choose from {', '.join(valid_modes)}."}
    
    data = {
        "origin": {"address": origin_address},
        "destination": {"address": destination_address},
        "travelMode": travel_mode,
        "computeAlternativeRoutes": False,
        "languageCode": "en-US",
        "units": "IMPERIAL"
    }

    if travel_mode == "DRIVE":
        data["routingPreference"] = "TRAFFIC_AWARE"
        data["routeModifiers"] = {
            "avoidTolls": True
        }
    
    try:
        response = requests.post(base_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        return {"error": f"Directions API request failed: {str(e)}"}
    
    if 'routes' in result and result['routes']:
        route = result['routes'][0]
        duration_seconds = int(route.get('duration', '0').rstrip('s'))
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m {seconds}s"
        output = {
            "origin": origin_address,
            "destination": destination_address,
            "duration": duration_str,
            "distance": f"{route.get('distanceMeters', 0) / 1609.34:.2f} miles"
        }

        steps = []
        for leg in route.get('legs', []):
            for step in leg.get('steps', []):
                if 'navigationInstruction' in step:
                    steps.append(step['navigationInstruction'].get('instructions', ''))
        output["steps"] = steps
        
        return output
    else:
        return {"error": "No routes found"}