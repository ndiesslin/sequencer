import numpy as np
import threading
from utilities import controls, dsp

# Queue to merge all of our sounds together in each step and play
# Now this just gathers audio buffers and mixes them
class player_queue:
  def __init__(self, audio_engine, settings):
    self.settings = settings
    self.audio_engine = audio_engine
    
    # List of audio arrays to mix
    self.audio_layers = []

  def _play_sounds(self):
    if not self.audio_layers:
        return
        
    # Find max length
    max_len = max(len(layer) for layer in self.audio_layers)
    
    # Mix buffers
    mixed = np.zeros(max_len, dtype=np.float32)
    for layer in self.audio_layers:
        # Pad if shorter
        if len(layer) < max_len:
            padded = np.zeros(max_len, dtype=np.float32)
            padded[:len(layer)] = layer
            mixed += padded
        else:
            mixed += layer
    
    # Global Effects
    global_effects = self.settings.global_effects
    # Pitch/Speed
    if 'pitch' in global_effects:
        try:
            pitch_cents = float(global_effects['pitch'])
            speed = dsp.sox_pitch_to_speed(pitch_cents)
            if 'speed' in global_effects:
                speed *= float(global_effects['speed'])
            mixed = dsp.apply_pitch_speed(mixed, speed)
        except:
             pass
    
    # Clip to -1.0 to 1.0 to avoid distortion
    mixed = np.clip(mixed, -1.0, 1.0)
    
    # Add to engine
    self.audio_engine.add_audio(mixed)

  def add_layer(self, audio_data):
    if audio_data is not None and len(audio_data) > 0:
        self.audio_layers.append(audio_data)

class sample_player:
  def __init__(self, step, audio_engine, settings):
    self.settings = settings
    self.step = step
    self.audio_engine = audio_engine
    
  def _process_samples(self):
    # Get current samples
    current_step_samples = self.check_samples()
    
    mixed_sample = np.zeros(0, dtype=np.float32)

    for sample_name in current_step_samples:
        # Load sample
        sample_config = self.settings.samples.get(sample_name)
        effects = sample_config.get('effects', {})
        
        # Volume
        vol_str = effects.get('vol', '1.0')
        try:
            vol = float(vol_str)
        except:
            vol = 1.0
            
        sample_data = self.audio_engine.load_sample(f'./samples/{sample_name}.wav', volume=vol)
        
        # Apply Pitch (sox pitch)
        if 'pitch' in effects:
             try:
                 speed = dsp.sox_pitch_to_speed(float(effects['pitch']))
                 sample_data = dsp.apply_pitch_speed(sample_data, speed)
             except:
                 pass
        
        # Apply Echo?
        # Note: In original code, sample effects were complex. 
        # We'll just stick to vol and pitch for now unless requested.
        
        # Mix
        if len(mixed_sample) == 0:
            mixed_sample = sample_data
        else:
            # Resize
            if len(sample_data) > len(mixed_sample):
                new_mix = np.zeros(len(sample_data), dtype=np.float32)
                new_mix[:len(mixed_sample)] = mixed_sample
                mixed_sample = new_mix
            elif len(sample_data) < len(mixed_sample):
                padded = np.zeros(len(mixed_sample), dtype=np.float32)
                padded[:len(sample_data)] = sample_data
                sample_data = padded
                
            mixed_sample += sample_data
            
    return mixed_sample

  # Check samples and return which samples are on
  def check_samples(self):
    step = self.step
    samples = self.settings.samples
    on_samples = []

    # Get Mute/Solo state
    track_state = getattr(self.settings, 'track_state', {'muted': set(), 'solo': None})
    muted = track_state['muted']
    solo = track_state['solo']

    for sample in samples:
      # Check Mute/Solo logic
      if sample in muted: continue
      if solo and solo != sample: continue
      
      sample_on = samples.get(sample)['sequence'][step]

      if sample_on == 1:
        on_samples.append(sample)

    return on_samples


# Trigger synth play each step we may be able to merge with sample play
class synth_player:
  def __init__(self, synth, step, audio_engine, settings):
    self.settings = settings
    self.synth = synth
    self.step = step
    self.audio_engine = audio_engine

  # Check if synth is on and play tone
  def _process_synth(self):
    step = self.step
    synth = self.synth
    enabled = synth.get('enabled')
    sequence_note = synth.get('sequence')[step]

    # If we have no frequency or not enabled return empty list
    if sequence_note == "" or enabled != True:
      return np.zeros(0, dtype=np.float32)

    synth_type = synth.get('type')
    effects = synth.get('effects', {})

    # Parse frequency
    freqs = []
    if '+' in str(sequence_note):
        parts = str(sequence_note).split('+')
        for p in parts:
            freqs.append(controls.note_to_freq(p))
    else:
        freqs.append(controls.note_to_freq(str(sequence_note)))

    play_length = self.tempo_to_playlength()
    
    # Generate audio
    mixed_synth = np.zeros(int(self.audio_engine.sample_rate * play_length), dtype=np.float32)
    
    # Get volume
    vol_str = effects.get('vol', '1.0')
    try:
        vol = float(vol_str)
    except:
        vol = 0.5 
        
    vol = vol / len(freqs)

    for f in freqs:
        wave = self.audio_engine.generate_waveform(synth_type, f, play_length, volume=vol)
        if len(wave) > len(mixed_synth):
             mixed_synth.resize(len(wave))
        elif len(wave) < len(mixed_synth):
             pass 
             
        l = min(len(wave), len(mixed_synth))
        mixed_synth[:l] += wave[:l]

    # Apply Effects
    
    # Tremolo: "speed depth" e.g. "10 40"
    if 'tremolo' in effects:
        try:
            parts = str(effects['tremolo']).split()
            speed = float(parts[0])
            depth = float(parts[1])
            mixed_synth = dsp.apply_tremolo(mixed_synth, speed, depth, self.audio_engine.sample_rate)
        except:
            pass

    # Echo: "gain_in gain_out delay_ms decay" e.g. "0.8 0.2 250 0.2"
    # Note: JSON allows multiple 'echo' keys but python dict only stores one.
    # The original json had duplicates. We only process the one that survived json parsing.
    if 'echo' in effects:
        try:
            parts = str(effects['echo']).split()
            # Handle variable args
            gain_in = float(parts[0])
            gain_out = float(parts[1])
            delay_ms = float(parts[2])
            decay = float(parts[3])
            mixed_synth = dsp.apply_echo(mixed_synth, gain_in, gain_out, delay_ms, decay, self.audio_engine.sample_rate)
        except:
            pass
            
    # Apply simple decay envelopes for cleanup
    # Only if no echo tails? Echo makes it longer.
    if len(mixed_synth) > 1000 and 'echo' not in effects:
        decay = np.linspace(1.0, 0.0, 500)
        mixed_synth[-500:] *= decay

    return mixed_synth

  # Play synth as long as tempo step
  def tempo_to_playlength(self):
    bpm = self.settings.bpm
    length = 60/bpm/self.settings.nth_notes
    length = round(length, 2)

    # Shorten slightly (staccato) to separate notes
    return length * 0.9