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
      # Trigger sample play
      play_step = player.sample_player(step)
      play_step._process_samples()

      # Trigger synth play
      synth_step = player.synth_player(step)
      synth_step._play_tone()

      # Visualize playback
      visualizer.print_step(step, settings.steps)

      # Update settings when changes are made, needed to track bpm changes
      settings.update_settings()

      # Bpm is set each time to adjust while playing
      seconds = controls.bpm_to_seconds(settings.bpm)

      # Time until next step in sequence
      time.sleep(seconds)
sequence_runner()