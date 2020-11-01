import os
import json

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

      self.bpm = settings['_bpm']
      self.global_effects = settings['_global_effects']
      self.nth_notes = settings['_nth_notes']
      self.steps = range(settings['_steps'])
      self.synths = settings['_synths']        
      self.samples = settings['samples']