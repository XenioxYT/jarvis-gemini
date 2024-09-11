import os
from dotenv import load_dotenv
from wake_word_detector import WakeWordDetector
from gemini_api import GeminiAPI
from tts_engine import TTSEngine
from tools import Tools
import time
import threading
import json
from audio_recorder import AudioRecorder
import pygame
from datetime import datetime
from function_tools.reminders import get_reminders_unix

class VoiceAssistant:
    def __init__(self, enable_follow_up=True):
        load_dotenv()
        self.access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        self.wake_word_detector = WakeWordDetector(self.access_key)
        self.gemini_api = GeminiAPI()
        self.tts_engine = TTSEngine()
        self.tools = Tools()
        self.audio_recorder = AudioRecorder(self.access_key)
        self.enable_follow_up = enable_follow_up

    def run(self):
        print("Voice Assistant is running. Say 'Jarvis' to activate.")
        reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
        reminder_thread.start()
        while True:
            # Wait for wake word
            audio_file = self.wake_word_detector.listen()
            if audio_file:
                self.process_interaction(audio_file)

    def process_interaction(self, audio_file):
        response = self.gemini_api.process_audio(audio_file, tts_engine=self.tts_engine)
        
        if not self.enable_follow_up:
            return  # Exit the method if follow-up is disabled

        while True:
            # Wait for TTS to finish
            while self.tts_engine.is_speaking:
                time.sleep(3)
            
            # Wait for pygame mixer to become idle
            while pygame.mixer.music.get_busy():
                time.sleep(1.5)
            
            # Listen for follow-up
            follow_up_audio = self.audio_recorder.record(silence_duration=2.0, wait_for_speech=True, timeout=2.0)
            if follow_up_audio:
                response = self.gemini_api.process_audio(follow_up_audio, tts_engine=self.tts_engine)
            else:
                print("No follow-up detected. Returning to wake word detection.")
                break  # Exit the loop and return to listening for the wake word

    def _check_reminders(self):
        while True:
            reminders = get_reminders_unix()  # Get all reminders with Unix timestamps
            current_time = time.time()
            print(f"Current time: {datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')}")
            reminders_to_remove = []
            for reminder in reminders:
                print(f"Checking reminder: {reminder}")
                reminder_time = reminder["reminder_at"]
                if isinstance(reminder_time, str):
                    # Convert string timestamp to Unix timestamp if necessary
                    reminder_time = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S").timestamp()
                print(f"Reminder time: {datetime.fromtimestamp(reminder_time).strftime('%Y-%m-%d %H:%M:%S')}")
                if reminder_time <= current_time:
                    print(f"Reminder triggered: {reminder}")
                    response = self.gemini_api.generate_reminder_response(reminder)
                    self.tts_engine.queue_reminder_response(response)
                    reminders_to_remove.append(reminder)
            
            if reminders_to_remove:
                print(f"Reminders to remove: {reminders_to_remove}")
                # Remove triggered reminders
                updated_reminders = [r for r in reminders if r not in reminders_to_remove]
                # Save updated reminders
                with open("reminders.json", "w") as f:
                    json.dump(updated_reminders, f)
                print(f"Updated reminders saved: {updated_reminders}")
            else:
                print("No reminders to remove")
            
            time.sleep(5)  # Check reminders every 5 seconds for debugging

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
    assistant = VoiceAssistant(enable_follow_up=False)
    assistant.run()