import os
from dotenv import load_dotenv
from wake_word_detector import WakeWordDetector
from gemini_api import GeminiAPI
from tts_engine import TTSEngine
from tools import Tools
import time
import threading
import json

class VoiceAssistant:
    def __init__(self):
        load_dotenv()
        self.access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        self.wake_word_detector = WakeWordDetector(self.access_key)
        self.gemini_api = GeminiAPI()
        self.tts_engine = TTSEngine()
        self.tools = Tools()

    def run(self):
        print("Voice Assistant is running. Say 'Jarvis' to activate.")
        reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
        reminder_thread.start()
        while True:
            # Wait for wake word
            audio_file = self.wake_word_detector.listen()
            
            if audio_file:
                # Send audio to Gemini API
                response = self.gemini_api.process_audio(audio_file, tts_engine=self.tts_engine)
                # Response is already spoken by the TTS engine in a separate thread
            else:
                print("No audio was recorded. Listening for wake word again.")

    def _check_reminders(self):
        while True:
            reminders = self.tools.get_reminders()
            current_time = time.time()
            reminders_to_remove = []
            for reminder in reminders:
                if reminder["reminder_at"] <= current_time:
                    response = self.gemini_api.generate_reminder_response(reminder)
                    self.tts_engine.queue_reminder_response(response)
                    reminders_to_remove.append(reminder)
            for reminder in reminders_to_remove:
                reminders.remove(reminder)
            with open("reminders.json", "w") as f:
                json.dump(reminders, f)
            time.sleep(1)  # Check reminders every second

    def test_audio_input(self, audio_file):
        # Send audio to Gemini API
        response = self.gemini_api.process_audio(audio_file, tts_engine=self.tts_engine)
        
        # Wait for user input to keep the program running and allow the TTS response to be read out
        input("Press Enter to continue...")

    def test_text_input(self, text):
        # Send text to Gemini API
        response = self.gemini_api.process_text(text, tts_engine=self.tts_engine)
        
        # Wait for user input to keep the program running and allow the TTS response to be read out
        input("Press Enter to continue...")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()