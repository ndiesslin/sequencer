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
      # Create playback queue to add our sounds in this step
      player_queue = player.player_queue()

      # Trigger synth 1 play
      synth = settings.synths.get('synth_1')
      synth_step = player.synth_player(synth, step)
      player_queue.queue_addition = synth_step._process_synth()
      player_queue.add_to_queue()

      # Trigger synth 2 play
      synth = settings.synths.get('synth_2')
      synth_step = player.synth_player(synth, step)
      player_queue.queue_addition = synth_step._process_synth()
      player_queue.add_to_queue()

      # Trigger sample play
      play_step = player.sample_player(step)
      player_queue.queue_addition = play_step._process_samples()
      player_queue.add_to_queue()

      # Trigger all sound playback
      player_queue._play_sounds()

      # Visualize playback
      visualizer.print_step(step, settings.steps)

      # Update settings when changes are made, needed to track bpm changes
      settings.update_settings()

      # Bpm is set each time to adjust while playing
      seconds = controls.bpm_to_seconds(settings.bpm, settings.nth_notes)

      # Time until next step in sequence
      time.sleep(seconds)
sequence_runner()