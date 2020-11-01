def sound_effects_to_string(effects):
  # Check if effects are empty
  if not effects:
    return ''
  else:
    # Join all effects to string which we apply on play
    effects_string = ''.join('{} {} '.format(key, val) for key, val in effects.items())
    return effects_string

def bpm_to_seconds(bpm, nth_notes):
  frequency = bpm/60
  seconds = 1/frequency
  seconds = seconds/nth_notes
  return seconds