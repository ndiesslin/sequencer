import time
import json
from utilities.settings import Settings
from utilities import controls
from utilities import player
from utilities import visualizer

# Get settings class
settings = Settings()

from utilities.audio_engine import AudioEngine

from utilities.audio_engine import AudioEngine

def sequence_runner(stop_event=None, ui_queue=None):
  # Initialize Audio Engine
  # Start with standard sample rate
  try:
      engine = AudioEngine()
  except Exception as e:
      with open("crash.log", "w") as f:
          f.write(f"Failed to init AudioEngine: {e}\n")
      return

  # Timing state
  next_wake_time = time.perf_counter()
  
  with open("trace.log", "w") as tf:
      tf.write("Entering loop...\n")
  
  try:
      while True:
        # Check stop event
        if stop_event and stop_event.is_set():
            break
            
        # Capture current steps
        current_steps = settings.steps
        
        with open("trace.log", "a") as tf:
            tf.write(f"Looping... Steps: {len(current_steps)}\n")

        for step in current_steps:
          # Check stop event inside loop for faster response
          if stop_event and stop_event.is_set():
            break

          # Create playback queue
          # Pass engine and settings
          pq = player.player_queue(engine, settings)
    
          # Check Mute/Solo State
          muted = settings.track_state['muted']
          solo = settings.track_state['solo']

          # Play Synth 1
          if (not solo or solo == 'synth_1') and 'synth_1' not in muted:
              synth = settings.synths.get('synth_1')
              synth_step = player.synth_player(synth, step, engine, settings)
              pq.add_layer(synth_step._process_synth())
        
          # Play Synth 2
          if (not solo or solo == 'synth_2') and 'synth_2' not in muted:
              synth = settings.synths.get('synth_2')
              synth_step = player.synth_player(synth, step, engine, settings)
              pq.add_layer(synth_step._process_synth())

          # Play Samples (Kick/Snare/etc)
          # Logic is handled in player.sample_player logic now
          play_step = player.sample_player(step, engine, settings)
          pq.add_layer(play_step._process_samples())

          # Mix and add to engine buffer
          pq._play_sounds()
        
          # Send UI update if queue provided
          if ui_queue:
              ui_queue.put({'step': step, 'total_steps': len(current_steps)})
          else:
              # Legacy visualizer if running standalone
              visualizer.print_step(step, current_steps)

          # Update settings
          # In TUI mode, TUI updates settings in memory. File watch might fight it.
          # For TUI, we might want to disable file watching or make it optional?
          # But for now, let's keep it.
          settings.update_settings()

          # Calculate duration
          bpm_duration = controls.bpm_to_seconds(settings.bpm, settings.nth_notes)
          
          # Apply Swing
          swing = getattr(settings, 'swing', 0.5)
          
          if step % 2 == 0:
            actual_duration = bpm_duration * 2 * swing
          else:
            actual_duration = bpm_duration * 2 * (1.0 - swing)
            
          # Advance target time
          next_wake_time += actual_duration
          
          # Sleep until target time
          sleep_time = next_wake_time - time.perf_counter()
          
          if sleep_time > 0:
            time.sleep(sleep_time)
            
  except KeyboardInterrupt:
      pass # Clean exit on Ctrl+C in standalone mode
  except Exception as e:
      with open("crash.log", "w") as f:
          import traceback
          f.write(traceback.format_exc())
      raise
  finally:
      print("\nStopping Audio Engine...")
      engine.close()

if __name__ == "__main__":
    sequence_runner()