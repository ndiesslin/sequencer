
import numpy as np

def apply_vol(audio, volume):
    """Apply volume scaling"""
    return audio * volume

def apply_echo(audio, gain_in, gain_out, delay_ms, decay, sample_rate=44100):
    """
    Apply simple echo/delay.
    audio: numpy array
    gain_in: input gain (usually < 1.0)
    gain_out: output gain (usually < 1.0)
    delay_ms: delay in milliseconds
    decay: decay factor for feedback (0.0 to 1.0)
    """
    delay_samples = int((delay_ms / 1000.0) * sample_rate)
    
    if delay_samples <= 0:
        return audio
        
    # Calculate total length needed including tails
    # We'll estimate tail length based on decay til -60dB (0.001)
    # decay^n < 0.001 => n > log(0.001)/log(decay)
    # decay^n < 0.001 => n > log(0.001)/log(decay)
    # Avoid div by zero if decay is 1 or 0
    if decay <= 0:
        num_echoes = 1
    elif decay >= 1.0:
        num_echoes = 10 # Cap it
    else:
        try:
            num_echoes = int(np.log(0.001) / np.log(decay))
        except:
            num_echoes = 5
        
    # Cap echoes to avoid excessively long buffers
    num_echoes = min(num_echoes, 10)
    
    extra_samples = delay_samples * num_echoes
    output_len = len(audio) + extra_samples
    output = np.zeros(output_len, dtype=np.float32)
    
    # Place initial signal
    output[:len(audio)] = audio * gain_in
    
    # Add echoes
    current_delay = delay_samples
    current_gain = gain_out
    
    # Iterative delay
    # Actually standard Echo is: y[n] = x[n]*gain_in + y[n-delay]*decay
    # But for a fixed buffer effect (non-recursive filter approx for simplicity 
    # and stability in this "one-shot" generation context:
    # y = x*gain_in + Echo1 + Echo2 ...
    
    # We will just do a few taps
    source = audio * gain_out
    
    for i in range(num_echoes):
        # Calculate start and end indices in output
        start = current_delay
        end = start + len(audio)
        
        if start >= output_len:
            break
            
        # Add delayed signal
        # Handle case where end > output_len
        l = min(len(audio), output_len - start)
        output[start:start+l] += source[:l] * (decay ** i) # decay^0 is first echo? Usually decay applies to feedback
        # If sox "decay" means relative to previous:
        # Echo 1: gain_out
        # Echo 2: gain_out * decay
        # Echo 3: gain_out * decay^2
        
        current_delay += delay_samples
        
    # Trim silence? No, we might want the tail.
    # But we should probably not make it infinitely long.
    return output

def apply_tremolo(audio, speed_hz, depth, sample_rate=44100):
    """
    Apply amplitude modulation.
    depth: 0-100 (percent)
    """
    t = np.linspace(0, len(audio)/sample_rate, len(audio), endpoint=False)
    
    # Modulator: sine wave offset to be positive
    # Tremolo formula: y(t) = x(t) * (1 - depth/2 + (depth/2)*sin(2*pi*f*t))
    # depth is usually 0-1.
    
    d = depth / 100.0
    modulator = (1.0 - d/2.0) + (d/2.0) * np.sin(2 * np.pi * speed_hz * t)
    
    return audio * modulator

def apply_pitch_speed(audio, speed_factor):
    """
    Resample audio to change speed and pitch.
    speed_factor > 1.0 = faster and higher pitch
    """
    if speed_factor == 1.0:
        return audio
        
    # New length
    new_len = int(len(audio) / speed_factor)
    
    # Simple linear interpolation resampling
    indices = np.linspace(0, len(audio)-1, new_len)
    resampled = np.interp(indices, np.arange(len(audio)), audio)
    
    return resampled.astype(np.float32)

def sox_pitch_to_speed(pitch_cents):
    """
    Convert cents to speed factor.
    +1200 cents = 2x speed
    factor = 2^(cents/1200)
    """
    return 2.0 ** (pitch_cents / 1200.0)
