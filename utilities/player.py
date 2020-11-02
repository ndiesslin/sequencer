import os
from utilities import controls
from utilities.settings import Settings

# Queue to merge all of our sounds together in each step and play
class player_queue:
  def __init__(self):
    # Get settings class
    self.settings = Settings()
    # Set initial player queue
    self.queue = ''
    self.queue_addition = ''
    self.merge_sound_counter = 0
    self.merge = ''

  def _play_sounds(self):
    self.global_effects_string = controls.sound_effects_to_string(self.settings.global_effects)
    # Check for merge before triggering sample
    self.check_merge()
    # Default buffer is 8192
    os.system(f'sox --buffer 2000 -q -V0 {self.merge} -r 44100 {self.queue} {self.global_effects_string} remix - &')

  def add_to_queue(self):
    # Check if we need to add a count to our merge
    if self.queue_addition != '':
      self.merge_sound_counter += 1
    # Add to queue, and add a space so we don't clash with other additions to string
    self.queue += self.queue_addition + ' '

  def check_merge(self):
    if self.merge_sound_counter >= 2:
      self.merge = '--combine mix'

class sample_player:
  def __init__(self, step):
    # Get settings class
    self.settings = Settings()
    self.step = step
    self.sample_string = ''
    self.current_step_samples = ''

  def _process_samples(self):
    # Get current samples
    self.current_step_samples = self.check_samples()

    # Return final samples
    return self.play_samples()

  # Check samples and return which samples are on
  def check_samples(self):
    step = self.step
    samples = self.settings.samples
    on_samples = []

    for sample in samples:
      sample_on = samples.get(sample)['sequence'][step]

      if sample_on == 1:
        on_samples.append(sample)

    return on_samples

  # Merge samples and return once
  def play_samples(self):
    current_step_samples = self.current_step_samples
    samples = self.settings.samples
    merged_samples = ''

    for sample in current_step_samples:
      # It seems as though effects can be added after each sample, if we want them per channel
      sample_effects_string = controls.sound_effects_to_string(samples.get(sample)['effects'])
      # For some reason the default non-pipe seems to work smoother here
      #merged_samples += f'./samples/{sample}.wav '
      merged_samples += (f'"|sox ./samples/{sample}.wav -p {sample_effects_string}" ')

    merge = ''
    if len(current_step_samples) >= 2:
      merge = '-m'
    
    # Return sample string
    return f'{merge} {merged_samples} -d norm -1'

# Trigger synth play each step we may be able to merge with sample play
class synth_player:
  def __init__(self, synth, step):
    # Get settings class
    self.settings = Settings()
    self.synth = synth
    self.step = step

  # Check if synth is on and play tone
  def _process_synth(self):
    step = self.step
    synth = self.synth
    enabled = synth.get('enabled')
    sequence_frequency = synth.get('sequence')[step]

    # If we have no frequency or not enabled return
    if sequence_frequency == "" or enabled != True:
      return ''

    synth_type = synth.get('type')
    effects = synth.get('effects')
    effects_string = controls.sound_effects_to_string(effects)
    play_length = self.tempo_to_playlength()

    self.play_string = f'"|sox -r 44100 -n -p synth {play_length} {synth_type} {sequence_frequency} {effects_string}"'

    # Return synth string
    return self.play_string

  # Play synth as long as tempo step
  def tempo_to_playlength(self):
    bpm = self.settings.bpm
    length = 60/bpm/self.settings.nth_notes
    length = round(length, 2)

    return length