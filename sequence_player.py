import time
import json
from utilities.settings import Settings
from utilities import controls
from utilities import player
from utilities import visualizer

# Get settings class
settings = Settings()

def sequence_runner():
  while True:
    for step in settings.steps:
      # Bpm is set each time to adjust while playing
      seconds = controls.bpm_to_seconds(settings.bpm)

      # Get samples before checking and playing, this allows the check for file reload
      samples = Settings().samples

      # Get samples in step to play
      current_step_samples = player.check_samples(step, samples)

      # Play samples in step
      player.play_samples(current_step_samples, samples, settings.global_effects)

      # Update settings when changes are made
      settings.update_settings()

      # Visualize playback
      visualizer.print_step(step, settings.steps)

      # Time until next step in sequence
      time.sleep(seconds)
sequence_runner()