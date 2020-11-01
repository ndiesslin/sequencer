# Visualize the current step playback
def print_step(current_step, steps):
  sequence_track = ''
  step_color = '\033[31m'
  reset_color = '\033[32m'
  for step in steps:
    if step == current_step:
      sequence_track += f'[{step_color}█{reset_color}]'
    else:
      sequence_track += '[_]'
  print(sequence_track, end="\r")