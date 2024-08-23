import os
import json
from dotenv import load_dotenv
from wake_word_detector import WakeWordDetector
from gemini_api import GeminiAPI
from tts_engine import TTSEngine
class VoiceAssistant:
    def __init__(self):
        load_dotenv()
        self.access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        self.wake_word_detector = WakeWordDetector(self.access_key)
        self.gemini_api = GeminiAPI()
        self.tts_engine = TTSEngine()
        self.is_speaking = False

    def run(self):
        print("Voice Assistant is running. Say 'Jarvis' to activate.")
        while True:
            # Wait for wake word
            audio_file = self.wake_word_detector.listen()
            
            if audio_file:
                # Send audio to Gemini API
                response = self.gemini_api.process_audio(audio_file, tts_engine=self.tts_engine)
                # Response is already spoken by the TTS engine in a separate thread
            else:
                print("No audio was recorded. Listening for wake word again.")

    def interrupt(self):
        if self.is_speaking:
            self.tts_engine.stop()
            self.is_speaking = False

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

    def run_assistant():
        assistant = VoiceAssistant()
        assistant.run()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()