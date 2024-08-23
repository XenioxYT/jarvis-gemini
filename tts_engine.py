import pygame
import time
import threading
import queue
import os
import uuid
from google.cloud import texttospeech
from datetime import datetime

class TTSEngine:
    def __init__(self):
        print("Initializing TTSEngine...")
        
        # Initialize Google Cloud Text-to-Speech
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_CREDENTIALS')
        self.client = texttospeech.TextToSpeechClient()
        
        pygame.mixer.init()
        self.generation_queue = queue.Queue()
        self.play_queue = queue.Queue()
        self.is_speaking = False
        self.generation_thread = threading.Thread(target=self._process_generation_queue, daemon=True)
        self.playback_thread = threading.Thread(target=self._process_play_queue, daemon=True)
        self.generation_thread.start()
        self.playback_thread.start()
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.on_speech_end_callback = None
        print("TTSEngine initialized.")

    def speak(self, text, on_speech_end_callback=None):
        self.on_speech_end_callback = on_speech_end_callback
        self.generation_queue.put(text)

    def _process_generation_queue(self):
        while True:
            text = self.generation_queue.get()
            audio_file = self._generate_audio(text)
            self.play_queue.put((audio_file, text))
            self.generation_queue.task_done()

    def _process_play_queue(self):
        while True:
            audio_file, text = self.play_queue.get()
            self.is_speaking = True
            success = self._play_audio(audio_file, text)
            self.is_speaking = False
            self.play_queue.task_done()
            if success and self.on_speech_end_callback:
                self.on_speech_end_callback()
                self.on_speech_end_callback = None

    def _generate_audio(self, text):
        print(f"Converting text to speech: '{text}'")
        
        # Ensure text is a string
        if not isinstance(text, str):
            print(f"Error: Expected text to be a string but got {type(text)}")
            return None
        
        # Generate a unique filename for this audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.temp_dir, f"{timestamp}.mp3")
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name="en-GB-Neural2-A"
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.10,
        )

        try:
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            # The response's audio_content is binary
            with open(filename, "wb") as out:
                out.write(response.audio_content)
            print(f"Speech synthesized and saved to {filename}")
            return filename
        except Exception as e:
            print(f"An error occurred during speech synthesis: {str(e)}")
            return None

    def _play_audio(self, audio_file, text, retry_count=0):
        if audio_file is None:
            print("No audio file to play.")
            return False
        
        print(f"Playing audio: {audio_file}")
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("Finished playing audio.")
            return True
        except pygame.error as e:
            print(f"Error playing audio: {e}")
            if retry_count < 2:
                print(f"Regenerating audio and trying again (attempt {retry_count + 1})...")
                new_audio_file = self._generate_audio(text)
                return self._play_audio(new_audio_file, text, retry_count + 1)
            else:
                print("Max retry limit reached. Skipping this response.")
                return False

    def stop(self):
        print("Stopping audio playback...")
        pygame.mixer.music.stop()
        self.generation_queue.queue.clear()
        self.play_queue.queue.clear()
        print("Audio playback stopped.")