import pvporcupine
import pvrecorder
import time
from audio_recorder import AudioRecorder
import pygame

class WakeWordDetector:
    def __init__(self, access_key):
        self.access_key = access_key
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keywords=["jarvis"]
        )
        self.recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=self.porcupine.frame_length)
        self.audio_recorder = AudioRecorder(self.access_key)

    def listen(self):
        print("Listening for wake word 'Jarvis'...")
        self.recorder.start()

        try:
            while True:
                pcm = self.recorder.read()
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    # Stop the playback
                    pygame.mixer.music.stop()
                    print("Wake word detected!")
                    self.recorder.stop()
                    # Add a short delay to allow the user to speak
                    time.sleep(0.1)
                    
                    # Hand off to audio recorder
                    wav_file = self.audio_recorder.record(silence_duration=1.0)
                    
                    if wav_file:
                        print(f"Recording saved as {wav_file}")
                        return wav_file
                    else:
                        print("No audio was recorded.")
                        return None

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.recorder.stop()

    def __del__(self):
        if self.porcupine is not None:
            self.porcupine.delete()
        if self.recorder is not None:
            self.recorder.delete()