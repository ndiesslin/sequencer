import json
import inquirer
from utilities.settings import Settings

# Get settings class
settings = Settings()

# Get our samples available to edit
samples = Settings().samples

# def main_screen_prompt():
#   main_screen = [
#     inquirer.List(
#       'main_screen',
#       message="What would you like to` edit?",
#       choices=['bpm','samples'],
#     ),
    
#   ]
#   return inquirer.prompt(main_screen)

# settings_to_edit = main_screen_prompt()

# NOTE: Here is where we will plan to get settings and sequence imputs to rewrite settings file.
def sample_prompt(samples):
  question_sample = [
    inquirer.List(
      'sample',
      message="What sample to edit?",
      choices=samples.keys(),
    ),
    
  ]
  return inquirer.prompt(question_sample)

#sample_to_edit = sample_prompt(samples)

# Get sequence for selected sample
def sequence_prompt(sample_sequence):
  sample_sequence_with_values = []
  sample_sequence_default_values = []
  for index, step in enumerate(sample_sequence):
    if step == 1:
      sample_sequence_default_values.append(index)
    sample_sequence_with_values.append(index)

  # Preload checked items so we don't lose them
  question_sequence = [
    inquirer.Checkbox(
      'sequence',
      message="Check which values should be on",
      choices=sample_sequence_with_values,
      default=sample_sequence_default_values,
    )
  ]
  return inquirer.prompt(question_sequence)['sequence']

# Get original sequence
#sample_sequence = samples.get(sample_to_edit['sample'])['sequence']

# Get modified sequence from prompt
#sequence = sequence_prompt(sample_sequence)

def write_sequence(sample_sequence, sequence, sample_to_edit):
  # Rewrite sequence
  for index, step in enumerate(sample_sequence):
    if index in sequence:
      sample_sequence[index] = 1
    else:
      sample_sequence[index] = 0

  # Open settings file to add updates
  settings_file = open("settings.json", "r")
  json_object = json.load(settings_file)
  json_object['samples'][sample_to_edit['sample']]['sequence'] = sample_sequence

  # Add our sequence to json
  settings_file = open("settings.json", "w")
  json.dump(json_object, settings_file, indent=2, sort_keys=True)
  settings_file.close()

#write_sequence(sample_sequence, sequence)

# Function for going through settings
def prompt_loop() :
  sample_to_edit = sample_prompt(samples)
  sample_sequence = samples.get(sample_to_edit['sample'])['sequence']
  sequence = sequence_prompt(sample_sequence)
  write_sequence(sample_sequence, sequence, sample_to_edit)

  # Recall function
  prompt_loop()

prompt_loop()

# Got back to start