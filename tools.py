import time
import random
import inspect
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
import datetime
from google.oauth2.credentials import Credentials
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

    # @staticmethod
    # def get_news(category='general', country='us'):
    #     """
    #     Get top news headlines for a specified category and country.
    #     Args:
    #         category (str): News category (default: 'general').
    #         country (str): Country code (default: 'us').
    #     Returns:
    #         list: A list of news articles.
    #     """
    #     NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    #     url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={NEWS_API_KEY}"
    #     response = requests.get(url)
    #     data = response.json()
    #     return data['articles']

    # @staticmethod
    # def send_email(to: str, subject: str, body: str):
    #     """
    #     Send an email (placeholder function).
    #     Args:
    #         to (str): Recipient email address.
    #         subject (str): Email subject.
    #         body (str): Email body.
    #     Returns:
    #         str: Confirmation message.
    #     """
    #     # Placeholder for email sending logic (e.g., using smtplib)
    #     return f"Email sent to {to} with subject: {subject}"

    # @staticmethod
    # def get_directions(origin: str, destination: str):
    #     """
    #     Get directions between two locations (placeholder function).
    #     Args:
    #         origin (str): Starting location.
    #         destination (str): Ending location.
    #     Returns:
    #         str: Directions information.
    #     """
    #     # Placeholder for Google Maps API call
    #     return f"Directions from {origin} to {destination}"

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