import pvrecorder
import pvcobra
import wave
from datetime import datetime
import struct
from dotenv import load_dotenv
import os
import time

class AudioRecorder:
    def __init__(self, access_key):
        self.cobra = pvcobra.create(access_key=access_key)
        self.recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=self.cobra.frame_length)
        self.rate = self.recorder.sample_rate
        self.channels = 1
        self.sample_width = 2  # 16-bit audio

    def record(self, silence_duration=0.5, wait_for_speech=False, timeout=2.0):
        print("Listening for follow-up..." if wait_for_speech else "Recording... Speak now.")
        
        self.recorder.start()

        frames = []
        voice_probability_threshold = 0.5
        silent_frames = 0
        max_silent_frames = int(silence_duration * self.rate / self.cobra.frame_length)
        speech_detected = not wait_for_speech
        start_time = time.time()
        
        try:
            while True:
                pcm = self.recorder.read()
                voice_probability = self.cobra.process(pcm)
                
                if wait_for_speech and not speech_detected:
                    if voice_probability >= voice_probability_threshold:
                        speech_detected = True
                        print("Speech detected, recording...")
                    elif time.time() - start_time > timeout:
                        print("No speech detected within timeout.")
                        return None
                    else:
                        continue
                
                frames.extend(pcm)
                
                if voice_probability >= voice_probability_threshold:
                    silent_frames = 0
                else:
                    silent_frames += 1
                
                if silent_frames >= max_silent_frames and speech_detected:
                    break
                
        finally:
            self.recorder.stop()

        if not frames:
            print("No speech detected.")
            return None

        # Save the recorded audio to a WAV file
        os.makedirs("voice_recordings", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        wav_filename = os.path.join("voice_recordings", f"recording_{timestamp}.wav")
        
        with wave.open(wav_filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sample_width)
            wf.setframerate(self.rate)
            wf.writeframes(struct.pack(f"{len(frames)}h", *frames))

        print(f"Audio saved as {wav_filename}")
        return wav_filename

    def __del__(self):
        self.recorder.delete()
        self.cobra.delete()

def test_audio_recorder():
    load_dotenv()
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    recorder = AudioRecorder(access_key)
    
    print("This test will record your voice until 1 seconds of silence is detected.")
    print("Press Enter to start recording...")
    input()
    
    wav_file = recorder.record(silence_duration=1.0)
    
    if wav_file:
        print(f"Recording saved as {wav_file}")
    else:
        print("No audio was recorded.")

if __name__ == "__main__":
    test_audio_recorder()