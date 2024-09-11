import inspect
from function_tools import weather, google_search, news, directions, discord_message, phone_message, place_info, take_notes, reminders
import json
from datetime import datetime

class Tools:
    
    @staticmethod
    def get_weather(location: str, forecast_type: str = 'current', time_range: int = 3) -> dict:
        """Get weather information for a specified location using OpenWeatherMap API.
        Args:
            location: The name of the location/postcode to get weather information for.
            forecast_type: Type of forecast - 'current', 'hourly', or 'daily'. Default is 'current'.
            time_range: Number of hours ahead for hourly forecast or days ahead for daily forecast. Default is 3."""
        return weather.get_weather(location, forecast_type, time_range)

    @staticmethod
    def google_search(query: str) -> list:
        """Use Google search and return the top 5 results."""
        return google_search.google_search(query)

    @staticmethod
    def get_news(query: str = "", headlines_only: bool = False) -> dict:
        """Get news articles. If headlines_only is True, fetch top headlines without a query.
        Args:
            query: The search query. Ignored if headlines_only is True.
            headlines_only: If True, fetch top headlines without a query."""
        return news.get_news(query, headlines_only)

    @staticmethod
    def get_directions(origin: str, destination: str, travel_mode: str = "DRIVE") -> dict:
        """Get directions, include time and steps, between two locations.
        Args:
            origin: Starting location.
            destination: Ending location.
            travel_mode: Mode of travel - "DRIVE", "WALK", "BICYCLE", or "TRANSIT" (default: "DRIVE")."""
        return directions.get_directions(origin, destination, travel_mode)

    @staticmethod
    async def send_discord_message(user_id: int, message: str) -> str:
        """Send a direct message to a Discord user asynchronously as an embed."""
        return await discord_message.send_discord_message(user_id, message)

    @staticmethod
    def send_message_to_phone(user_id: str, message: str) -> str:
        """Send a text message to the user."""
        return phone_message.send_message_to_phone(user_id, message)

    @staticmethod
    def get_place_information(query: str, open_now: bool = False) -> dict:
        """Perform a Place Search using the Google Maps Places API.
        open_now: Optional. Return only places that are open for business at the time the query is sent."""
        return place_info.get_place_information(query, open_now)
        
    @staticmethod
    def take_notes(notes: str = None, search: bool = False, query: str = None) -> str:
        """Take notes or search existing notes.
        Args:
            notes: The notes to take (if None, assumes search mode).
            search: Whether to search existing notes.
            query: The search query (for text or date (YYYY-MM-DD))."""
        return take_notes.take_notes(notes, search, query)

    @staticmethod
    def set_reminder(name: str, timestamp: str) -> str:
        """Set a reminder with the given name and timestamp. Timestamp needs to be provided in the format YYYY-MM-DD HH:MM:SS"""
        return reminders.set_reminder(name, timestamp)

    @staticmethod
    def get_reminders(mode: str = 'upcoming', start_date: str = None, end_date: str = None, limit: int = 10) -> list:
        """Get a list of reminders based on specified criteria.
        
        Args:
            mode: 'upcoming' (default) for soon-to-come reminders, 'recent' for recently created reminders
            start_date: Start date for date range search (format: YYYY-MM-DD)
            end_date: End date for date range search (format: YYYY-MM-DD)
            limit: Maximum number of reminders to return (default: 10)
        
        Returns:
            list: A list of reminders matching the criteria
        """
        return reminders.get_reminders(mode, start_date, end_date, limit)
        
    @classmethod
    def get_available_tools(cls):
        """
        Dynamically returns a list of available tool methods in the Tools class.
        
        Returns:
            list: A list of method references for the available tools.
        """
        return [
            value for name, value in inspect.getmembers(cls, predicate=inspect.isfunction)
            if not name.startswith('_') and name != 'get_available_tools' and name != 'call_function' and name != 'send_discord_message'
        ]

    @classmethod
    def call_function(cls, function_name, **kwargs):
        if hasattr(cls, function_name):
            return getattr(cls, function_name)(**kwargs)
        else:
            return f"Unknown function: {function_name}"