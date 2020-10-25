import os
from utilities import controls

# Check samples and return which samples are on
def check_samples(step, samples):
  on_samples = []

  for sample in samples:
    sample_on = samples.get(sample)['sequence'][step]

    if sample_on == 1:
      on_samples.append(sample)

  return on_samples

def play_samples(current_step_samples, samples, global_effects):
  print('Notes playing:')
  print(current_step_samples)
  for sample in current_step_samples:
    sample_effects_string = controls.sound_effects_to_string(samples.get(sample)['effects'])
    global_effects_string = controls.sound_effects_to_string(global_effects)
    # Play sound file with sox
    # https://unix.stackexchange.com/questions/39714/why-do-nohup-and-disown-not-work-on-sox-invoked-as-play
    os.system(f'play -q -V0 ./samples/{sample}.mp3 {sample_effects_string} {global_effects_string} &')