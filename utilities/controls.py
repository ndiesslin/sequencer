def sound_effects_to_string(effects):
  # Check if effects are empty
  if not effects:
    return ''
  else:
    # Join all effects to string which we apply on play
    effects_string = ''.join('{} {} '.format(key, val) for key, val in effects.items())
    return effects_string

def bpm_to_seconds(bpm):
  frequency = bpm/60
  seconds = 1/frequency
  # Half time since we are playing in 8th notes
  seconds = seconds/2
  return seconds