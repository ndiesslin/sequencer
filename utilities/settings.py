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
      self.swing = settings.get('_swing', 0.5)
      # self.synths and self.samples are now Properties that read from self.patterns
      # We don't assign them here anymore.

      # Restore or initialize runtime state
      if old_state:
          self.track_state = old_state
      else:
          self.track_state = {
              'muted': set(),
              'solo': None
          }
      
      # Runtime Pattern State
      # 1-indexed (1, 2, 3, 4)
      self.playing_pattern_idx = 1
      self.editing_pattern_idx = 1
      self.queued_pattern_idx = None
      
      # Load or Migrate Patterns
      if 'patterns' in settings:
          self.patterns = settings['patterns']
          # Ensure keys are integers (json keys are strings)
          self.patterns = {int(k): v for k, v in self.patterns.items()}
      else:
          # Migration: Move root synths/samples to Pattern 1
          print("Migrating settings to Pattern format...")
          
          # 1. capture old data
          p1_data = {
              'synths': settings.get('_synths', {}),
              'samples': settings.get('samples', {})
          }
          
          # 2. Assign patterns dict first
          self.patterns = {
              1: p1_data
          }
          
          # 3. Create others using the now-existing P1
          self.patterns[2] = self._create_empty_pattern()
          self.patterns[3] = self._create_empty_pattern()
          self.patterns[4] = self._create_empty_pattern()

  def _create_empty_pattern(self):
      # Create default empty structure
      # We need a copy of the structure from pattern 1 but empty sequences
      # For now, let's just create a basic template or copy pattern 1 and clear it?
      # Copying P1 structure is safer to preserve synth settings (vol/effects)
      # But we want to clear the sequence notes.
      import copy
      if 1 in self.patterns:
          template = copy.deepcopy(self.patterns[1])
          # Clear sequences
          for k in template['synths']:
              template['synths'][k]['sequence'] = [""] * 16
          for k in template['samples']:
              template['samples'][k]['sequence'] = [0] * 16
          return template
      return {} # Fallback

  # Properties to proxy access to the "Active" data
  # The Audio Engine reads properties. We need to redirect them to the playing pattern.
  # BUT: The TUI reads them to edit. 
  # Actually, safest is to expose explicit methods or properties.
  
  # For Audio Engine (READ ONLY usually)
  @property
  def synths(self):
      return self.patterns[self.playing_pattern_idx]['synths']

  @property
  def samples(self):
      return self.patterns[self.playing_pattern_idx]['samples']

  # For TUI (Editing)
  def get_editing_pattern(self):
      return self.patterns[self.editing_pattern_idx]

  def clear_editing_pattern(self):
      p = self.get_editing_pattern()
      for k in p['synths']:
          p['synths'][k]['sequence'] = [""] * 16
      for k in p['samples']:
          p['samples'][k]['sequence'] = [0] * 16

  def save_settings(self):
    data = {
        '_bpm': self.bpm,
        '_global_effects': self.global_effects,
        '_nth_notes': self.nth_notes,
        '_steps': len(self.steps),
        '_swing': self.swing,
        'patterns': self.patterns # Save all patterns
    }
    with open(self.SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        # Update timestamp so we don't reload our own write
        self._last_update = os.fstat(f.fileno()).st_mtime