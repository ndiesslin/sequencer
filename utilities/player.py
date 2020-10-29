import os
from utilities import controls
from utilities.settings import Settings

class sample_player:
  def __init__(self, step):
    # Get settings class
    self.settings = Settings()
    self.step = step

  def _process_samples(self):
    # Get current samples
    self.current_step_samples = self.check_samples()

    # Play samples in step
    self.play_samples()

  # Check samples and return which sapulseaudio -kmples are on
  def check_samples(self):
    step = self.step
    samples = self.settings.samples
    on_samples = []

    for sample in samples:
      sample_on = samples.get(sample)['sequence'][step]

      if sample_on == 1:
        on_samples.append(sample)

    return on_samples

  # Merge samples and play once
  def play_samples_merged(self):
    current_step_samples = self.current_step_samples
    samples = self.settings.samples
    global_effects = self.settings.global_effects
    merged_samples = ''

    for sample in current_step_samples:
      sample_volume = samples[sample].get('volume')
      if not sample_volume:
        sample_volume = ''
      else:
        sample_volume = (f'-v {sample_volume}')
      merged_samples += (f'{sample_volume} ./samples/{sample}.wav ')

    merge = ''
    if len(current_step_samples) >= 2:
      merge = '-m'

    global_effects_string = controls.sound_effects_to_string(global_effects)
    os.system(f'play -q -V0 {merge} {merged_samples} {global_effects_string} &')

  # Loop through all samples and play seperately
  def play_samples_seperately(self):
    current_step_samples = self.current_step_samples
    samples = self.settings.samples
    global_effects = self.settings.global_effects

    for sample in current_step_samples:
        sample_volume = samples[sample].get('volume')
        if not sample_volume:
          sample_volume = ''
        else:
          sample_volume = (f'-v {sample_volume}')
        sample_effects_string = controls.sound_effects_to_string(samples.get(sample)['effects'])
        global_effects_string = controls.sound_effects_to_string(global_effects)
        # Play sound file with sox
        os.system(f'play -q -V0 {sample_volume} ./samples/{sample}.wav {sample_effects_string} {global_effects_string} &')

  # Play samples
  def play_samples(self):
    play_individual_samples = self.settings.play_individual_samples

    # Play samples independently from eachother, allows global effects
    if play_individual_samples:
      self.play_samples_seperately()

    else: 
      # Check if multiple samples then we should merge for playback optimization
      self.play_samples_merged()

# Trigger synth play each step we may be able to merge with sample play
class synth_player:
  def __init__(self, step):
    # Get settings class
    self.settings = Settings()
    self.step = step

  # Play synth as long as tempo step
  def tempo_to_playlength(self):
    bpm = self.settings.bpm
    length = 60/bpm/2
    length = round(length, 2)
    return length

  # Check if synth is on and play tone
  def _play_tone(self):
    step = self.step
    synth = self.settings.synth
    enabled = synth.get('enabled')
    sequence_frequency = synth.get('sequence')[step]

    # If we have no frequency or not enabled return
    if sequence_frequency == 0 or enabled != True:
      return

    synth_type = synth.get('type')
    volume = synth.get('volume')
    global_effects = self.settings.global_effects
    global_effects_string = controls.sound_effects_to_string(global_effects)
    effects = synth.get('effects')
    effects_string = controls.sound_effects_to_string(effects)
    play_length = self.tempo_to_playlength()

    os.system(f'play -q -V0 -r 44100 -n synth {play_length} {synth_type} {sequence_frequency} vol {volume} {effects_string} {global_effects_string} &')