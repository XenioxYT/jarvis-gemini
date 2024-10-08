import pygame
import time
import threading
import queue
import os
import uuid
from google.cloud import texttospeech
from datetime import datetime
from pathlib import Path
from openai import OpenAI

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
        print("TTSEngine initialized.")
        self.notification_sound = pygame.mixer.Sound("reminder_sound.mp3")

        # Initialize OpenAI client
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY_DIFF'),
            base_url=os.getenv('OPENAI_API_URL_DIFF')
        )

    def speak(self, text):
        if isinstance(text, str) and text.strip():
            self.generation_queue.put(text)
        else:
            print("Error: Invalid or empty text input for TTS.")

    def speak_openai(self, text):
        if isinstance(text, str) and text.strip():
            self.generation_queue.put((text, True))  # True indicates OpenAI TTS
        else:
            print("Error: Invalid or empty text input for TTS.")

    def _process_generation_queue(self):
        while True:
            item = self.generation_queue.get()
            if isinstance(item, tuple):
                text, use_openai = item
            else:
                text, use_openai = item, False
            
            if use_openai:
                audio_file = self._generate_audio_openai(text)
            else:
                audio_file = self._generate_audio(text)
            
            self.play_queue.put((audio_file, text))
            self.generation_queue.task_done()

    def _process_play_queue(self):
        while True:
            audio_file, text = self.play_queue.get()
            self.is_speaking = True
            
            # Wait for any ongoing playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            if audio_file is None:  # Reminder response
                self._play_notification_sound()
                success = self._play_audio(self._generate_audio(text), text)
            else:  # Regular response
                success = self._play_audio(audio_file, text)
            
            self.is_speaking = False
            self.play_queue.task_done()
            if success and audio_file is not None:
                pass
                # os.remove(audio_file)  # Clean up the temporary file

    def _generate_audio(self, text):
        print(f"Converting text to speech: '{text}'")
        
        # Generate a unique filename for this audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.temp_dir, f"{timestamp}.mp3")
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name="en-GB-Neural2-B"
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.05,
            pitch=0.0,
            # effects_profile_id=["headphone-class-device"],
            sample_rate_hertz=24000
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

    def _generate_audio_openai(self, text):
        print(f"Converting text to speech using OpenAI: '{text}'")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.temp_dir, f"{timestamp}_openai.mp3")
        
        try:
            response = self.openai_client.audio.speech.create(
                model="eleven-turbo-v2",
                voice="Lily",  # You can change this or make it configurable
                input=text,
                speed=1.10
            )
            response.stream_to_file(filename)
            print(f"OpenAI speech synthesized and saved to {filename}")
            return filename
        except Exception as e:
            print(f"An error occurred during OpenAI speech synthesis: {str(e)}")
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

    def _play_notification_sound(self):
        """Play the notification sound."""
        self.notification_sound.play()

    def queue_reminder_response(self, response: str) -> None:
        """Queue a reminder response to be read out after the current TTS queue."""
        self.play_queue.put((None, response))  # Use None for audio_file to indicate a reminder response

    def stop(self):
        print("Stopping audio playback...")
        pygame.mixer.music.stop()
        self.generation_queue.queue.clear()
        self.play_queue.queue.clear()
        print("Audio playback stopped.")