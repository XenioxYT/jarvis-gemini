import time
import random
import inspect
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
import datetime
from google.oauth2.credentials import Credentials
import json
# import discord

load_dotenv()

class Tools:
    @staticmethod
    def test_function(test: bool):
        """
        A simple test function to check if the function calling system works.
        Args:
            test (bool): A boolean value to determine the return message.
        Returns:
            str: A message indicating whether the function works or not.
        """
        if test:
            return "This works"
        else:
            return "This does not work"
    
    @staticmethod
    def get_weather(city: str, forecast_type: str = 'current', time_range: int = 3):
        """
        Get weather information for a specified city using OpenWeatherMap API.
        Args:
            city (str): The name of the city to get weather information for.
            forecast_type (str): Type of forecast - 'current', 'hourly', or 'daily'. Default is 'current'.
            time_range (int): Number of hours ahead for hourly forecast or days ahead for daily forecast. Default is 3.
        Returns:
            dict: Weather data for the specified city and forecast type.
        """
        OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

        # Clean data
        city = city.strip()
        forecast_type = forecast_type.strip()
        time_range = int(time_range)
        
        # Step 1: Geocoding API to get coordinates
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        geocoding_response = requests.get(geocoding_url)
        geocoding_data = geocoding_response.json()
        
        if not geocoding_data:
            return {"error": "City not found"}
        
        lat = geocoding_data[0]['lat']
        lon = geocoding_data[0]['lon']
        
        # Step 2: One Call API 3.0 to get weather data
        exclude = 'minutely,alerts'
        if forecast_type == 'current':
            exclude += ',hourly,daily'
        elif forecast_type == 'hourly':
            exclude += ',daily'
        elif forecast_type == 'daily':
            exclude += ',hourly'
        
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={OPENWEATHER_API_KEY}&units=metric"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        
        # Process and return the weather data based on forecast type
        if forecast_type == 'current':
            current_weather = weather_data.get('current', {})
            return {
                "city": city,
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
                "city": city,
                "hourly_forecast": [
                    {
                        "time": datetime.datetime.fromtimestamp(hour['dt']).strftime('%Y-%m-%d %H:%M:%S'),
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
                "city": city,
                "daily_forecast": [
                    {
                        "date": datetime.datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
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

    @staticmethod
    def google_search(query: str):
        """
        Perform a Google search and return the top 5 results from the UK.
        Args:
            query (str): The search query.
        Returns:
            list: A list of dictionaries containing the top 5 search results.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, gl="uk", num=5).execute()
        
        results = []
        for item in res.get("items", []):
            results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item["snippet"]
            })
        
        return results

    # @staticmethod
    # def get_calendar_events(days=7):
    #     """
    #     Get calendar events for the next specified number of days.
    #     Args:
    #         days (int): Number of days to fetch events for (default: 7).
    #     Returns:
    #         list: A list of calendar events.
    #     """
    #     GOOGLE_CALENDAR_CREDS = Credentials.from_authorized_user_file('path/to/credentials.json', ['https://www.googleapis.com/auth/calendar.readonly'])
    #     service = build('calendar', 'v3', credentials=GOOGLE_CALENDAR_CREDS)
    #     now = datetime.datetime.utcnow().isoformat() + 'Z'
    #     events_result = service.events().list(calendarId='primary', timeMin=now,
    #                                           maxResults=10, singleEvents=True,
    #                                           orderBy='startTime').execute()
    #     return events_result.get('items', [])

    @staticmethod
    def get_news(query: str = None, country: str = 'gb', limit: int = 5, source: str = 'bbc.com'):
        """
        Get news articles using the NewsData.io API.
        Args:
            query (str): The search query. If None, fetches top news. (default: None)
            country (str): The country code (default: 'gb').
            limit (int): The number of results to return (default: 5).
            source (str): The source of the news (default: 'bbc.com') Either choose 'bbc.com' or 'news.google.com'.
        Returns:
            dict: A dictionary containing the news articles and metadata.
        """
        NEWS_API_KEY = os.getenv('NEWS_API_KEY')
        base_url = "https://newsdata.io/api/1/latest"
        
        params = {
            'apikey': NEWS_API_KEY,
            'country': country,
            'prioritydomain': 'top',
            'size': limit,
            'domainurl': source,
            'language': 'en'
        }
        
        if query:
            params['q'] = query
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Extract only title, link, and description from each result
            simplified_results = [
                {
                    "title": article.get("title"),
                    "link": article.get("link"),
                    "description": article.get("description")
                }
                for article in data.get('results', [])[:limit]
            ]
            return {
                "status": data.get("status"),
                "totalResults": data.get("totalResults"),
                "results": simplified_results
            }
        else:
            return {"error": f"API request failed with status code {response.status_code}"}

    @staticmethod
    def get_directions(origin: str, destination: str, include_steps: bool = False, travel_mode: str = "DRIVE"):
        """
        Get directions between two locations using Google Maps Routes API.
        Args:
            origin (str): Starting location.
            destination (str): Ending location.
            include_steps (bool): Whether to include navigation steps in the output (default: False).
            travel_mode (str): Mode of travel - "DRIVE", "WALK", "BICYCLE", or "TRANSIT" (default: "DRIVE").
        Returns:
            dict: Directions information including duration and distance, and optionally steps.
        """
        GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
        base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_CLOUD_API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.navigationInstruction"
        }
        
        # Validate and normalize travel mode
        valid_modes = {"DRIVE", "WALK", "BICYCLE", "TRANSIT"}
        travel_mode = travel_mode.upper()
        if travel_mode not in valid_modes:
            return {"error": f"Invalid travel mode. Choose from {', '.join(valid_modes)}."}
        
        data = {
            "origin": {"address": origin},
            "destination": {"address": destination},
            "travelMode": travel_mode,
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "languageCode": "en-US",
            "units": "IMPERIAL",
            "routeModifiers": {
                "avoidTolls": True
            }
        }
        
        response = requests.post(base_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            if 'routes' in result and result['routes']:
                route = result['routes'][0]
                output = {
                    "duration": route.get('duration', ''),
                    "distance": f"{route.get('distanceMeters', 0) / 1609.34:.2f} miles"
                }
                
                if include_steps:
                    steps = []
                    for leg in route.get('legs', []):
                        for step in leg.get('steps', []):
                            if 'navigationInstruction' in step:
                                steps.append(step['navigationInstruction'].get('instructions', ''))
                    output["steps"] = steps
                
                return output
            else:
                return {"error": "No routes found"}
        else:
            return {"error": f"API request failed with status code {response.status_code}"}

    # @staticmethod
    # def check_flight_status(flight_number: str):
    #     """
    #     Check the status of a flight (placeholder function).
    #     Args:
    #         flight_number (str): The flight number to check.
    #     Returns:
    #         str: Flight status information.
    #     """
    #     # Placeholder for flight status API call
    #     return f"Status for flight {flight_number}: On time"

    # @staticmethod
    # def send_discord_message(channel_id: int, message: str):
    #     """
    #     Send a message to a Discord channel.
    #     Args:
    #         channel_id (int): The ID of the Discord channel.
    #         message (str): The message to send.
    #     Returns:
    #         str: Confirmation message.
    #     """
    #     DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    #     client = discord.Client()

    #     @client.event
    #     async def on_ready():
    #         channel = client.get_channel(channel_id)
    #         await channel.send(message)
    #         await client.close()

    #     client.run(DISCORD_BOT_TOKEN)
    #     return f"Message sent to Discord channel {channel_id}"

    @staticmethod
    def get_place_information(query: str, open_now: bool = False):
        """
        Perform a Place Search using the Google Maps Places API.
        Args:
            query (str): The text string on which to search.
            open_now (bool): Optional. Return only places that are open for business at the time the query is sent.
        Returns:
            dict: A dictionary containing the search results and metadata.
        """
        GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
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
        
        response = requests.post(base_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
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
        else:
            return {"error": f"API request failed with status code {response.status_code}"}

    @classmethod
    def get_available_tools(cls):
        """
        Dynamically returns a list of available tool methods in the Tools class.
        
        Returns:
            list: A list of method references for the available tools.
        """
        return [
            value for name, value in inspect.getmembers(cls, predicate=inspect.isfunction)
            if not name.startswith('_') and name != 'get_available_tools' and name != 'call_function'
        ]

    @classmethod
    def call_function(cls, function_name, **kwargs):
        if hasattr(cls, function_name):
            return getattr(cls, function_name)(**kwargs)
        else:
            return f"Unknown function: {function_name}"