import os
import json

# https://stackoverflow.com/questions/54120030/how-can-i-constantly-check-if-a-json-file-is-updated-in-python
class Settings:
  SETTINGS_FILE = 'settings.json'

  def __init__(self):
    self._load_settings()

  def update_settings(self):
    if self._last_update != os.stat(self.SETTINGS_FILE).st_mtime:
      self._load_settings()
      return True
    return False

  def _load_settings(self):
    with open(self.SETTINGS_FILE) as json_settings:
      settings = json.load(json_settings)
      self._last_update = os.fstat(json_settings.fileno()).st_mtime

      self.bpm = settings['bpm']
      self.steps = range(settings['steps'])
      self.samples = settings['samples']
      self.global_effects = settings['global_effects']