# Visualize the current step playback
def print_step(current_step, steps):
  sequence_track = ''
  for step in steps:
    if step == current_step:
      sequence_track += '[█]'
    else:
      sequence_track += '[_]'
  print(sequence_track, end="\r")