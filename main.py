import threading
from wake_word_detector import WakeWordDetector
from audio_recorder import AudioRecorder
from gemini_api import GeminiAPI
from tts_engine import TTSEngine

class VoiceAssistant:
    def __init__(self):
        self.wake_word_detector = WakeWordDetector()
        self.audio_recorder = AudioRecorder()
        self.gemini_api = GeminiAPI()
        self.tts_engine = TTSEngine()
        self.is_speaking = False

    def run(self):
        while True:
            # Wait for wake word
            self.wake_word_detector.listen()
            
            # Record audio
            audio_file = self.audio_recorder.record()
            
            # Send audio to Gemini API
            response = self.gemini_api.process_audio(audio_file)
            
            # Speak the response
            self.speak(response)

    def speak(self, text):
        self.is_speaking = True
        self.tts_engine.speak(text)
        self.is_speaking = False

    def interrupt(self):
        if self.is_speaking:
            self.tts_engine.stop()
            self.is_speaking = False

if __name__ == "__main__":
    assistant = VoiceAssistant()
    
    # Start a separate thread for interrupt detection
    interrupt_thread = threading.Thread(target=assistant.wake_word_detector.listen_for_interrupt, args=(assistant.interrupt,))
    interrupt_thread.start()
    
    assistant.run()