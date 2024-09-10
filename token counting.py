# Testing tools
from tools import Tools
import time
from datetime import datetime, timedelta

# print (Tools.get_news(headlines_only=True))

# print(Tools.get_place_information("The five swans"))

# print(Tools.get_weather("Newcastle upon tyne"))

# print(Tools.get_directions("Newcastle upon tyne", "London"))

# print(Tools.take_notes(notes = "I am testing the notes tool"))

# print(Tools.google_search("I am testing the google search tool"))

# print(Tools.send_message_to_phone("1234", "I am testing the send message to phone tool"))

# Set a reminder for 5 minutes from now
reminder_name = "Take a break"
reminder_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

Tools.set_reminder(reminder_name, reminder_time)

print(f"Reminder '{reminder_name}' set for {reminder_time}")

# Set a reminder for tomorrow at 9:00 AM
tomorrow_9am = (datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
reminder_name = "Morning meeting"

Tools.set_reminder(reminder_name, tomorrow_9am)

print(f"Reminder '{reminder_name}' set for {tomorrow_9am}")

# Print all current reminders
current_reminders = Tools.get_reminders()
print("\nCurrent reminders:")
for reminder in current_reminders:
    reminder_time = datetime.fromtimestamp(reminder['reminder_at']).strftime("%Y-%m-%d %H:%M:%S")
    print(f"- {reminder['name']} at {reminder_time}")

# Test TTS engine

# from tts_engine import TTSEngine

# def test_tts_engine():
#     tts = TTSEngine()
#     print("TTS Engine Test")
#     print("Enter text to convert to speech. Type 'exit' to quit.")
    
#     while True:
#         user_input = input("Enter text: ").strip()
#         if user_input.lower() == 'exit':
#             break
#         if user_input:
#             tts.speak(user_input)
#         else:
#             print("Please enter some text.")
    
#     print("Test completed.")

# # Run the test function
# test_tts_engine()

# from pathlib import Path
# from openai import OpenAI
# client = OpenAI()

# speech_file_path = Path(__file__).parent / "speech.mp3"
# voices = ['Alice', 'George', 'Lily']

# response = client.audio.speech.create(
#     model="eleven-turbo-v2",
#     voice="Alice",
#     input="Today is a wonderful day to build something people love!"
# )
# voice_file_path = Path(__file__).parent / f"speech.mp3"
# response.stream_to_file(voice_file_path)