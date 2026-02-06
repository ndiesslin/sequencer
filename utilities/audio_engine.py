
import pyaudio
import numpy as np
import threading
import time

class AudioEngine:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sample_rate,
            output=True,
            frames_per_buffer=buffer_size
        )
        
        # Audio buffer for upcoming audio
        # We will write to this, and playing thread will consume it
        self.audio_buffer = np.zeros(0, dtype=np.float32)
        self.buffer_lock = threading.Lock()
        
        # Background thread to feed PyAudio
        self.running = True
        self.thread = threading.Thread(target=self._audio_loop)
        self.thread.daemon = True
        self.thread.start()

    def _audio_loop(self):
        while self.running:
            # How many frames do we need to write?
            # We want to keep the buffer somewhat full but not too full (to avoid latency)
            # Actually, let's just write whatever is in our buffer to the stream
            # The stream.write call is blocking if the OS buffer is full
            
            with self.buffer_lock:
                if len(self.audio_buffer) >= self.buffer_size:
                    # Take chunk
                    chunk = self.audio_buffer[:self.buffer_size]
                    self.audio_buffer = self.audio_buffer[self.buffer_size:]
                else:
                    # Not enough data, pad with silence if needed or just wait?
                    # If we write nothing, we might underrun.
                    # Let's write silence if buffer is empty
                    if len(self.audio_buffer) == 0:
                        chunk = np.zeros(self.buffer_size, dtype=np.float32)
                    else:
                         # Write what we have + silence
                         chunk = np.concatenate([
                             self.audio_buffer, 
                             np.zeros(self.buffer_size - len(self.audio_buffer), dtype=np.float32)
                         ])
                         self.audio_buffer = np.zeros(0, dtype=np.float32)
            
            # Write key: This blocks if stream is full
            self.stream.write(chunk.astype(np.float32).tobytes())

    def add_audio(self, audio_data):
        """Mix audio data into the buffer to play immediately"""
        if audio_data is None or len(audio_data) == 0:
            return

        with self.buffer_lock:
            # Current buffer length
            current_len = len(self.audio_buffer)
            add_len = len(audio_data)
            
            # Length to mix (overlap)
            mix_len = min(current_len, add_len)
            
            if mix_len > 0:
                self.audio_buffer[:mix_len] += audio_data[:mix_len]
            
            # If new audio is longer, append the rest
            if add_len > current_len:
                remaining = audio_data[mix_len:]
                self.audio_buffer = np.concatenate([self.audio_buffer, remaining])
            
    def generate_waveform(self, wave_type, frequency, duration, volume=1.0):
        """Generate a waveform as numpy array"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'saw':
            # simple saw approximation or signal.sawtooth if scipy was available
            # using numpy logic: 2 * (t * f - floor(t * f + 0.5))
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif wave_type == 'square':
             wave = np.sign(np.sin(2 * np.pi * frequency * t))
        else:
            wave = np.sin(2 * np.pi * frequency * t) # default sine
            
        return wave * volume

    def load_sample(self, filepath, volume=1.0):
        # We can use soundfile or librosa, or just basic wave module for now?
        # Trying to minimize deps, but reading wav with numpy is tricky without scipy/librosa.
        # Let's use standard library 'wave' and convert to numpy
        import wave
        
        try:
            with wave.open(filepath, 'rb') as wf:
                # Assuming 16-bit PCM for now
                frames = wf.readframes(wf.getnframes())
                # Convert to float32
                audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                
                # Normalize 16-bit to -1..1
                audio = audio / 32768.0
                
                # Resample if needed? Ignoring for now (assuming 44100 wavs)
                return audio * volume
        except Exception as e:
            print(f"Error loading sample {filepath}: {e}")
            return np.zeros(100, dtype=np.float32)

    def close(self):
        self.running = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
