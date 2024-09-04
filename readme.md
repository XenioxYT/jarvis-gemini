# AI Voice Assistant

This project is an advanced AI voice assistant powered by Google's Gemini language model. It uses voice recognition to detect a wake word, processes user queries, and responds using text-to-speech technology.

## Features

- Wake word detection ("Jarvis")
- Voice input processing
- Natural language understanding and generation using Gemini AI
- Text-to-speech output
- Conversation history management
- Integration with various tools:
  - Setting timers and alarms
  - Calendar management (Google Calendar API)
  - Weather information retrieval (OpenWeatherMap API)
  - News fetching (Google News API)
  - Smart home device control (Home Assistant API)
  - To-do list and reminder management
  - Web search functionality (Google Search API)
  - Message and email sending
  - Music and podcast playback
  - Directions and traffic information (Google Maps API)
  - Flight status checking
  - Phone messaging via Discord API

## Requirements

- Python 3.8+
- pip
- virtualenv

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/xenioxyt/jarvis-gemini.git
   cd jarvis-gemini
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   PICOVOICE_ACCESS_KEY=your_picovoice_access_key
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_CREDENTIALS=path/to/your/google-credentials.json
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   OPENWEATHER_API_KEY=your_openweather_api_key
   GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
   NEWS_API_KEY=your_news_api_key
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ```

5. Ensure you have the necessary credentials file for Google Cloud services.

## Usage

To start the voice assistant, run:

```
python main.py
```

The assistant will listen for the wake word "Jarvis". Once detected, it will record your query, process it using the Gemini AI, and respond using text-to-speech.

## Project Structure

- `main.py`: The entry point of the application.
- `wake_word_detector.py`: Handles wake word detection.
- `audio_recorder.py`: Manages audio recording after wake word detection.
- `gemini_api.py`: Interfaces with the Gemini AI for natural language processing.
- `tts_engine.py`: Handles text-to-speech conversion and audio playback.
- `tools.py`: Contains various tool functions for extended functionality.
- `prompt.py`: Defines the system prompt for the AI assistant.
- `function_tools/`: Directory containing individual tool implementations:
  - `weather.py`: Retrieves weather information.
  - `google_search.py`: Performs web searches.
  - `news.py`: Fetches news articles.
  - `directions.py`: Provides directions and traffic information.
  - `discord_message.py`: Sends messages via Discord.
  - `phone_message.py`: Sends messages to phones.
  - `place_info.py`: Retrieves information about places.
  - `take_notes.py`: Manages note-taking functionality.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.