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
    # Preserve runtime state if it exists
    old_state = getattr(self, 'track_state', None)

    with open(self.SETTINGS_FILE) as json_settings:
      settings = json.load(json_settings)
      self._last_update = os.fstat(json_settings.fileno()).st_mtime

      self.bpm = settings['_bpm']
      self.global_effects = settings['_global_effects']
      self.nth_notes = settings['_nth_notes']
      self.steps = range(settings['_steps'])
      self.swing = settings.get('_swing', 0.5)
      self.synths = settings['_synths']        
      self.samples = settings['samples']

      # Restore or initialize runtime state
      if old_state:
          self.track_state = old_state
      else:
          self.track_state = {
              'muted': set(),
              'solo': None
          }

  def save_settings(self):
    data = {
        '_bpm': self.bpm,
        '_global_effects': self.global_effects,
        '_nth_notes': self.nth_notes,
        '_steps': len(self.steps),
        '_swing': self.swing,
        '_synths': self.synths,
        'samples': self.samples
    }
    with open(self.SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        # Update timestamp so we don't reload our own write
        self._last_update = os.fstat(f.fileno()).st_mtime