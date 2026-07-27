import threading
import wave
from pathlib import Path

import numpy as np
try:
    import pyaudio
except ImportError:  # Let non-audio utilities and tests import cleanly.
    pyaudio = None


class AudioEngine:
    def __init__(self, sample_rate=44100, buffer_size=1024, max_buffer_seconds=2):
        if pyaudio is None:
            raise RuntimeError("PyAudio is not installed. Install project dependencies before playback.")
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.max_buffer_frames = int(sample_rate * max_buffer_seconds)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate,
                                  output=True, frames_per_buffer=buffer_size)
        self.audio_buffer = np.zeros(0, dtype=np.float32)
        self.buffer_lock = threading.Lock()
        self.sample_cache = {}
        self.running = True
        self.thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.thread.start()

    def _audio_loop(self):
        while self.running:
            with self.buffer_lock:
                chunk = self.audio_buffer[:self.buffer_size]
                self.audio_buffer = self.audio_buffer[self.buffer_size:]
                if len(chunk) < self.buffer_size:
                    chunk = np.pad(chunk, (0, self.buffer_size - len(chunk)))
            self.stream.write(chunk.astype(np.float32, copy=False).tobytes())

    def add_audio(self, audio_data):
        """Mix sound at the current playhead without allowing unbounded latency."""
        if audio_data is None or len(audio_data) == 0:
            return
        with self.buffer_lock:
            available = self.max_buffer_frames - len(self.audio_buffer)
            if available <= 0:
                return
            data = np.asarray(audio_data[:available], dtype=np.float32)
            overlap = min(len(self.audio_buffer), len(data))
            if overlap:
                self.audio_buffer[:overlap] += data[:overlap]
            if len(data) > overlap:
                self.audio_buffer = np.concatenate((self.audio_buffer, data[overlap:]))

    def generate_waveform(self, wave_type, frequency, duration, volume=1.0):
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        if wave_type == "saw":
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "triangle":
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        return (wave * volume).astype(np.float32)

    def load_sample(self, filepath, volume=1.0):
        """Load PCM WAV once, downmix it, and resample it to the output rate."""
        path = Path(filepath).resolve()
        try:
            stamp = path.stat().st_mtime_ns
            cached = self.sample_cache.get(path)
            if cached and cached[0] == stamp:
                return cached[1] * volume
            with wave.open(str(path), "rb") as source:
                channels, width, rate = source.getnchannels(), source.getsampwidth(), source.getframerate()
                raw = source.readframes(source.getnframes())
            if width != 2:
                raise ValueError(f"only 16-bit PCM WAV is supported (got {width * 8}-bit)")
            audio = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
            if channels > 1:
                audio = audio.reshape(-1, channels).mean(axis=1)
            if rate != self.sample_rate:
                length = max(1, round(len(audio) * self.sample_rate / rate))
                audio = np.interp(np.linspace(0, len(audio) - 1, length), np.arange(len(audio)), audio)
            audio = np.asarray(audio, dtype=np.float32)
            self.sample_cache[path] = (stamp, audio)
            return audio * volume
        except (OSError, ValueError, wave.Error) as error:
            print(f"Error loading sample {path}: {error}")
            return np.zeros(0, dtype=np.float32)

    def close(self):
        self.running = False
        self.thread.join(timeout=1.0)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
