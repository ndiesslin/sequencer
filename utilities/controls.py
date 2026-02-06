def sound_effects_to_string(effects):
  # Check if effects are empty
  if not effects:
    return ''
  else:
    # Join all effects to string which we apply on play
    effects_string = ''.join('{} {} '.format(key, val) for key, val in effects.items())
    return effects_string

def sound_effects_to_list(effects):
  # Check if effects are empty
  if not effects:
    return []
  else:
    # Join all effects to list
    effects_list = []
    for key, val in effects.items():
        effects_list.append(key)
        # Handle multiple values in string (e.g. "0.8 0.2") by splitting
        # Or just append as single string if sox expects it?
        # sox args: effect_name arg1 arg2 ...
        # If val is "0.8 0.2", we need to split it.
        effects_list.extend(str(val).split())
    return effects_list

def bpm_to_seconds(bpm, nth_notes):
  frequency = bpm/60
  seconds = 1/frequency
  seconds = seconds/nth_notes
  return seconds

def note_to_freq(note):
    # Convert note string (e.g. "A4") to frequency
    # Base reference A4 = 440Hz
    # Notes: C C# D D# E F F# G G# A A# B
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if not note or note == "":
        return 0.0
        
    try:
        # Extract octave
        octave = int(note[-1])
        name = note[:-1]
        
        index = NOTES.index(name)
        
        # Calculate steps from A4
        # A4 is index 9 in octave 4
        # midi note for A4 is 69
        # midi note for C4 is 60
        
        # midi number = (octave + 1) * 12 + index
        midi_num = (octave + 1) * 12 + index
        
        # freq = 440 * 2^((midi - 69) / 12)
        freq = 440.0 * (2.0 ** ((midi_num - 69.0) / 12.0))
        return freq
    except:
        # If parsing fails or custom freq passed (e.g. "100+200"), try to parse as float or just return 0 for now
        # The original code supported "100+200" for multi-tone. 
        # We will basic support float or int string
        try:
             return float(note)
        except:
             return 0.0