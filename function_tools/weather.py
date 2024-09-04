# Import necessary modules and load environment variables

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()

from function_tools.place_info import get_place_information

def get_weather(location: str, forecast_type: str = 'current', time_range: int = 3) -> dict:
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    if not OPENWEATHER_API_KEY:
        return {"error": "OpenWeather API key not found"}

    location = location.strip()
    forecast_type = forecast_type.strip().lower()
    try:
        time_range = int(time_range)
    except ValueError:
        return {"error": "Invalid time_range. Must be an integer."}

    if forecast_type not in ['current', 'hourly', 'daily']:
        return {"error": "Invalid forecast type. Choose 'current', 'hourly', or 'daily'."}
    country_code = "GB"
    
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location},{country_code}&limit=1&appid={OPENWEATHER_API_KEY}"
    try:
        geocoding_response = requests.get(geocoding_url)
        geocoding_response.raise_for_status()
        geocoding_data = geocoding_response.json()
        address = location
    except requests.RequestException as e:
        return {"error": f"Geocoding API request failed: {str(e)}"}

    if not geocoding_data:
        place_info = get_place_information(location)
        if place_info.get("status") == "OK" and place_info.get("results"):
            address = place_info["results"][0].get("address")
            if not address:
                return {"error": "Address not found in place information"}
            
            match = re.search(r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b', address)
            if not match:
                return {"error": "Postcode not found in address"}
            
            postcode = match.group(0)
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/zip?zip={postcode},{country_code}&appid={OPENWEATHER_API_KEY}"
            try:
                geocoding_response = requests.get(geocoding_url)
                geocoding_response.raise_for_status()
                geocoding_data = geocoding_response.json()
            except requests.RequestException as e:
                return {"error": f"Geocoding API request failed: {str(e)}"}
        else:
            return {"error": "location not found"}

    try:
        if 'zip' in geocoding_data:
            lat = geocoding_data['lat']
            lon = geocoding_data['lon']
        else:
            lat = geocoding_data[0]['lat']
            lon = geocoding_data[0]['lon']
    except (IndexError, KeyError):
        return {"error": "Invalid response from Geocoding API"}

    exclude = 'minutely,alerts'
    if forecast_type == 'current':
        exclude += ',hourly,daily'
    elif forecast_type == 'hourly':
        exclude += ',daily'
    elif forecast_type == 'daily':
        exclude += ',hourly'
    
    weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
    except requests.RequestException as e:
        return {"error": f"Weather API request failed: {str(e)}"}

    if forecast_type == 'current':
        current_weather = weather_data.get('current', {})
        return {
            "location": address,
            "temperature": current_weather.get('temp'),
            "feels_like": current_weather.get('feels_like'),
            "humidity": current_weather.get('humidity'),
            "description": current_weather.get('weather', [{}])[0].get('description'),
            "wind_speed": current_weather.get('wind_speed'),
            "pressure": current_weather.get('pressure')
        }
    elif forecast_type == 'hourly':
        hourly_forecast = weather_data.get('hourly', [])[:time_range]
        return {
            "location": address,
            "hourly_forecast": [
                {
                    "time": datetime.fromtimestamp(hour['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                    "temperature": hour.get('temp'),
                    "feels_like": hour.get('feels_like'),
                    "humidity": hour.get('humidity'),
                    "description": hour.get('weather', [{}])[0].get('description'),
                    "wind_speed": hour.get('wind_speed'),
                    "pressure": hour.get('pressure')
                } for hour in hourly_forecast
            ]
        }
    elif forecast_type == 'daily':
        daily_forecast = weather_data.get('daily', [])[:time_range]
        return {
            "location": address,
            "daily_forecast": [
                {
                    "date": datetime.fromtimestamp(day['dt']).strftime('%Y-%m-d'),
                    "temperature": {
                        "min": day['temp'].get('min'),
                        "max": day['temp'].get('max')
                    },
                    "humidity": day.get('humidity'),
                    "description": day.get('weather', [{}])[0].get('description'),
                    "wind_speed": day.get('wind_speed'),
                    "pressure": day.get('pressure')
                } for day in daily_forecast
            ]
        }
    else:
        return {"error": "Invalid forecast type. Choose 'current', 'hourly', or 'daily'."}