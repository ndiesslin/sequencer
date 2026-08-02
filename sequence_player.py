import time
import logging
from utilities.settings import Settings
from utilities import controls
from utilities import player
from utilities import visualizer

# If running as script, use local. If imported, use passed.
local_settings = Settings()
logger = logging.getLogger(__name__)

from utilities.audio_engine import AudioEngine

def sequence_runner(stop_event=None, ui_queue=None, settings=None):
  # Use passed settings or fallback to local
  if settings is None:
      settings = local_settings
  # Initialize Audio Engine
  # Start with standard sample rate
  try:
      engine = AudioEngine()
  except Exception:
      logger.exception("Failed to initialize the audio engine")
      return

  # Timing state
  next_wake_time = time.perf_counter()
  
  try:
      while True:
        # Check stop event
        if stop_event and stop_event.is_set():
            break
            
        # Capture current length. Playback takes an isolated settings snapshot for
        # each step, so UI edits cannot partially mutate audio state.
        current_steps = settings.steps

        for step in current_steps:
          # Check stop event inside loop for faster response
          if stop_event and stop_event.is_set():
            break

          playback = settings.get_playback_snapshot(step)
          pq = player.player_queue(engine, playback)
    
          # Check Mute/Solo State
          muted = playback.track_state['muted']
          solo = playback.track_state['solo']

          # Synth tracks are data-driven, rather than limited to two names.
          for synth_name, synth in playback.synths.items():
              if (not solo or solo == synth_name) and synth_name not in muted:
                  synth_step = player.synth_player(synth, step, engine, playback)
                  pq.add_layer(synth_step._process_synth())

          # Play Samples (Kick/Snare/etc)
          # Logic is handled in player.sample_player logic now
          play_step = player.sample_player(step, engine, playback)
          pq.add_layer(play_step._process_samples())

          # Mix and add to engine buffer
          pq._play_sounds()
        
          # Send UI update if queue provided
          if ui_queue:
              ui_queue.put({'step': step, 'total_steps': len(current_steps)})
          else:
              # Legacy visualizer if running standalone
              visualizer.print_step(step, current_steps)

          # Calculate duration
          bpm_duration = controls.bpm_to_seconds(playback.bpm, playback.nth_notes)
          
          # Apply Swing
          swing = settings.swing
          
          if step % 2 == 0:
            actual_duration = bpm_duration * 2 * swing
          else:
            actual_duration = bpm_duration * 2 * (1.0 - swing)
            
          # Advance target time
          next_wake_time += actual_duration
          
          # QUEUE LOGIC: If we are at the last step, switch pattern for next loop
          if step == len(current_steps) - 1:
              settings.advance_pattern()
          
          # Sleep until target time
          sleep_time = next_wake_time - time.perf_counter()
          
          if sleep_time > 0:
            time.sleep(sleep_time)
            
  except KeyboardInterrupt:
      pass # Clean exit on Ctrl+C in standalone mode
  except Exception:
      logger.exception("Sequencer playback failed")
      raise
  finally:
      print("\nStopping Audio Engine...")
      engine.close()

if __name__ == "__main__":
    sequence_runner()
