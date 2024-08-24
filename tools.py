
import inspect
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
import json
from fuzzywuzzy import fuzz
import discord
import asyncio

load_dotenv()

class Tools:
    
    @staticmethod
    def get_weather(city: str, forecast_type: str = 'current', time_range: int = 3) -> dict:
        """Get weather information for a specified city using OpenWeatherMap API.
        Args:
            city: The name of the city to get weather information for.
            forecast_type: Type of forecast - 'current', 'hourly', or 'daily'. Default is 'current'.
            time_range: Number of hours ahead for hourly forecast or days ahead for daily forecast. Default is 3."""
        OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
        if not OPENWEATHER_API_KEY:
            return {"error": "OpenWeather API key not found"}

        # Clean data
        city = city.strip()
        forecast_type = forecast_type.strip().lower()
        try:
            time_range = int(time_range)
        except ValueError:
            return {"error": "Invalid time_range. Must be an integer."}

        if forecast_type not in ['current', 'hourly', 'daily']:
            return {"error": "Invalid forecast type. Choose 'current', 'hourly', or 'daily'."}

        # Step 1: Geocoding API to get coordinates
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        try:
            geocoding_response = requests.get(geocoding_url)
            geocoding_response.raise_for_status()
            geocoding_data = geocoding_response.json()
        except requests.RequestException as e:
            return {"error": f"Geocoding API request failed: {str(e)}"}

        if not geocoding_data:
            return {"error": "City not found"}

        try:
            lat = geocoding_data[0]['lat']
            lon = geocoding_data[0]['lon']
        except (IndexError, KeyError):
            return {"error": "Invalid response from Geocoding API"}

        # Step 2: One Call API 3.0 to get weather data
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
                "city": city,
                "daily_forecast": [
                    {
                        "date": datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
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
    def google_search(query: str) -> list:
        """Use Google search and return the top 5 results."""
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cse_id:
            return [{"error": "Google API key or CSE ID not found"}]

        try:
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=query, cx=cse_id, gl="uk", num=5).execute()
        except Exception as e:
            return [{"error": f"Google Search API request failed: {str(e)}"}]
        
        results = []
        for item in res.get("items", []):
            try:
                results.append({
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item["snippet"]
                })
            except KeyError:
                results.append({"error": "Invalid response from Google Search API"})
        
        return results

    @staticmethod
    def get_news(query: str) -> dict:
        """Get news articles. If no query is provided, the top news is fetched.
        Args:
            query: The search query. If not provided the top news is fetched."""
        NEWS_API_KEY = os.getenv('NEWS_API_KEY')
        if not NEWS_API_KEY:
            return {"error": "News API key not found"}

        base_url = "https://newsdata.io/api/1/latest"
        
        params = {
            'apikey': NEWS_API_KEY,
            'country': "gb",
            'prioritydomain': 'top',
            'size': 5,
            'domainurl': "bbc.com",
            'language': 'en'
        }
        
        if query:
            params['q'] = query.strip()
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            return {"error": f"News API request failed: {str(e)}"}
        
        if response.status_code == 200:
            # Extract only title, link, and description from each result
            simplified_results = [
                {
                    "title": article.get("title"),
                    "link": article.get("link"),
                    "description": article.get("description")
                }
                for article in data.get('results', [])[:5]
            ]
            return {
                "status": data.get("status"),
                "totalResults": data.get("totalResults"),
                "results": simplified_results
            }
        else:
            return {"error": f"API request failed with status code {response.status_code}"}

    @staticmethod
    def get_directions(origin: str, destination: str, travel_mode: str = "DRIVE") -> dict:
        """Get directions, include time and steps, between two locations.
        Args:
            origin: Starting location.
            destination: Ending location.
            travel_mode: Mode of travel - "DRIVE", "WALK", "BICYCLE", or "TRANSIT" (default: "DRIVE")."""
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
            place_info = Tools.get_place_information(query)
            if place_info.get("status") == "OK" and place_info.get("results"):
                return place_info["results"][0]["address"]
            return query  # Return original query if no results found

        # Get the top result addresses for origin and destination
        origin_address = get_top_result_address(origin)
        destination_address = get_top_result_address(destination)
        
        # Validate and normalize travel mode
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

    @staticmethod
    async def send_discord_message(user_id: int, message: str) -> str:
        """Send a direct message to a Discord user asynchronously as an embed."""
        DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        if not DISCORD_BOT_TOKEN:
            return "Error: Discord bot token not found"

        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            try:
                user = await client.fetch_user(user_id)
                embed = discord.Embed(
                    description=message,
                    color=discord.Color.from_rgb(100, 200, 200)  # Light bluey-green color
                )
                await user.send(embed=embed)
                print(f"Message sent to user {user_id}")
            except discord.errors.NotFound:
                print(f"User {user_id} not found")
            except discord.errors.Forbidden:
                print(f"Cannot send DM to user {user_id}")
            finally:
                await client.close()

        try:
            await client.start(DISCORD_BOT_TOKEN)
        except Exception as e:
            return f"Error: Failed to send message: {str(e)}"
        return f"Message sent to Discord user {user_id}"

    @staticmethod
    def send_message_to_phone(user_id: str, message: str) -> str:
        """Send a text message to the user."""
        try:
            user_id_int = int(user_id)
        except ValueError:
            return "Error: Invalid user ID. Must be an integer."

        # Replace escaped newlines with actual newlines
        message = message.replace('\\\\n', '\n').replace('\\n', '\n')
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(Tools.send_discord_message(user_id_int, message))
        except Exception as e:
            result = f"Error: Failed to send message: {str(e)}"
        finally:
            if not loop.is_running():
                loop.close()
        return result

    @staticmethod
    def get_place_information(query: str, open_now: bool = False) -> dict:
        """Perform a Place Search using the Google Maps Places API.
        open_now: Optional. Return only places that are open for business at the time the query is sent."""
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
        
    @staticmethod
    def take_notes(notes: str = None, search: bool = False, query: str = None) -> str:
        """Take notes or search existing notes.
        Args:
            notes: The notes to take (if None, assumes search mode).
            search: Whether to search existing notes.
            query: The search query (for text or date (YYYY-MM-DD))."""
        notes_file = "user_notes.json"
        
        # Ensure the JSON file exists
        if not os.path.exists(notes_file):
            with open(notes_file, "w") as f:
                json.dump([], f)
        
        if not search:
            # Taking a new note
            if not notes:
                return "Error: No notes provided to save."
            
            timestamp = datetime.now().isoformat()
            new_note = {"date": timestamp, "content": notes}
            
            try:
                with open(notes_file, "r+") as f:
                    data = json.load(f)
                    data.append(new_note)
                    f.seek(0)
                    json.dump(data, f, indent=2)
            except json.JSONDecodeError:
                return "Error: Failed to read notes file."
            except IOError:
                return "Error: Failed to write to notes file."
            
            return f"Note saved: {notes}"
        
        else:
            # Searching notes
            if not query:
                return "Error: No search query provided."
            
            try:
                with open(notes_file, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                return "Error: Failed to read notes file."
            except IOError:
                return "Error: Failed to open notes file."
            
            results = []
            for note in data:
                date_match = fuzz.partial_ratio(query, note["date"])
                content_match = fuzz.partial_ratio(query, note["content"])
                
                if date_match > 70 or content_match > 70:
                    results.append(note)
            
            # Sort results by date and limit to 5
            results.sort(key=lambda x: x["date"], reverse=True)
            results = results[:5]
            
            if not results:
                return "No matching notes found."
            
            output = "Matching notes (up to 5 most recent):\n\n"
            for note in results:
                date = datetime.fromisoformat(note["date"]).strftime("%Y-%m-%d %H:%M:%S")
                output += f"Date: {date}\nContent: {note['content']}\n\n"
            
            return output.strip()

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