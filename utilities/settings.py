"""Validated, thread-safe persistence for sequencer state."""

import copy
import json
import os
from pathlib import Path
import threading
from types import SimpleNamespace


class Settings:
    """Own the saved arrangement and the runtime-only playback state."""

    DEFAULT_FILE = Path(__file__).resolve().parent.parent / "settings.json"

    def __init__(self, settings_file=None):
        self.settings_file = Path(settings_file or self.DEFAULT_FILE)
        self.lock = threading.RLock()
        self._last_update = None
        self._load_settings(persist_migration=True)

    @property
    def step_count(self):
        return len(self.steps)

    def _load_settings(self, persist_migration=False):
        with self.lock:
            with self.settings_file.open(encoding="utf-8") as source:
                data = json.load(source)
            self._last_update = self.settings_file.stat().st_mtime_ns

            self.bpm = data["_bpm"]
            self.global_effects = data.get("_global_effects", {})
            self.nth_notes = data["_nth_notes"]
            self.steps = range(data["_steps"])
            self.swing = data.get("_swing", 0.5)
            self.track_state = getattr(self, "track_state", {"muted": set(), "solo": None})
            self.pattern_clipboard = getattr(self, "pattern_clipboard", None)
            self.playing_pattern_idx = getattr(self, "playing_pattern_idx", 1)
            self.editing_pattern_idx = getattr(self, "editing_pattern_idx", 1)
            self.queued_pattern_idx = getattr(self, "queued_pattern_idx", None)
            self.song_chain = [int(item) for item in data.get("_song_chain", [])]
            self.song_mode = data.get("_song_mode", False)
            self.song_position = getattr(self, "song_position", 0)

            migrated = "patterns" not in data
            if migrated:
                first = {"synths": data.get("_synths", {}), "samples": data.get("samples", {})}
                self.patterns = {1: first}
                for number in range(2, 5):
                    self.patterns[number] = self._empty_pattern(first)
            else:
                self.patterns = {int(key): value for key, value in data["patterns"].items()}

            self._normalize_patterns()
            if persist_migration and migrated:
                self.save_settings()

    def _empty_pattern(self, source):
        pattern = copy.deepcopy(source)
        for config in pattern.get("synths", {}).values():
            config["sequence"] = [""] * self.step_count
        for config in pattern.get("samples", {}).values():
            config["sequence"] = [0] * self.step_count
        return pattern

    def _normalize_patterns(self):
        """Keep legacy or hand-edited files from causing index errors in playback."""
        for pattern in self.patterns.values():
            pattern.setdefault("automation", {"global": {}})
            pattern["automation"].setdefault("global", {})
            for group, empty in (("synths", ""), ("samples", 0)):
                for config in pattern.get(group, {}).values():
                    sequence = list(config.get("sequence", []))[: self.step_count]
                    sequence.extend([empty] * (self.step_count - len(sequence)))
                    config["sequence"] = sequence
                    params = list(config.get("step_params", []))[:self.step_count]
                    params.extend({"probability": 1.0, "velocity": 1.0}
                                  for _ in range(self.step_count - len(params)))
                    config["step_params"] = [
                        {"probability": float(item.get("probability", 1.0)),
                         "velocity": float(item.get("velocity", 1.0))}
                        for item in params]
                    config.setdefault("automation", {})
        self.song_chain = [item for item in self.song_chain if item in self.patterns]
        if self.song_chain:
            self.song_position %= len(self.song_chain)
        if self.playing_pattern_idx not in self.patterns:
            self.playing_pattern_idx = min(self.patterns)
        if self.editing_pattern_idx not in self.patterns:
            self.editing_pattern_idx = self.playing_pattern_idx

    def reload(self):
        self._load_settings()

    def update_settings(self):
        """Compatibility helper for explicit callers; playback does not poll files."""
        try:
            if self.settings_file.stat().st_mtime_ns != self._last_update:
                self.reload()
                return True
        except FileNotFoundError:
            return False
        return False

    @property
    def synths(self):
        return self.patterns[self.playing_pattern_idx]["synths"]

    @property
    def samples(self):
        return self.patterns[self.playing_pattern_idx]["samples"]

    def get_editing_pattern(self):
        return self.patterns[self.editing_pattern_idx]

    def get_playback_snapshot(self, step=None):
        """Return one consistent state snapshot for the audio thread."""
        with self.lock:
            pattern = copy.deepcopy(self.patterns[self.playing_pattern_idx])
            global_effects = copy.deepcopy(self.global_effects)
            if step is not None:
                for key, lane in pattern.get("automation", {}).get("global", {}).items():
                    if step < len(lane) and lane[step] is not None:
                        global_effects[key] = str(lane[step])
                for group in ("synths", "samples"):
                    for config in pattern[group].values():
                        for key, lane in config.get("automation", {}).items():
                            if step < len(lane) and lane[step] is not None:
                                config.setdefault("effects", {})[key] = str(lane[step])
            return SimpleNamespace(
                bpm=self.bpm,
                nth_notes=self.nth_notes,
                global_effects=global_effects,
                track_state=copy.deepcopy(self.track_state),
                synths=pattern["synths"],
                samples=pattern["samples"],
            )

    def clear_editing_pattern(self):
        with self.lock:
            pattern = self.get_editing_pattern()
            for config in pattern["synths"].values():
                config["sequence"] = [""] * self.step_count
            for config in pattern["samples"].values():
                config["sequence"] = [0] * self.step_count

    def queue_editing_pattern(self):
        with self.lock:
            self.queued_pattern_idx = self.editing_pattern_idx

    def toggle_song_mode(self):
        with self.lock:
            if not self.song_chain:
                self.song_chain = [self.playing_pattern_idx]
            self.song_mode = not self.song_mode
            if self.playing_pattern_idx in self.song_chain:
                self.song_position = self.song_chain.index(self.playing_pattern_idx)
            return self.song_mode

    def append_editing_to_song(self):
        with self.lock:
            self.song_chain.append(self.editing_pattern_idx)

    def remove_last_song_pattern(self):
        with self.lock:
            if self.song_chain:
                self.song_chain.pop()
                self.song_position = 0

    def cycle_step_parameter(self, track_key, step, parameter, values):
        with self.lock:
            pattern = self.get_editing_pattern()
            config = pattern["synths"].get(track_key) or pattern["samples"].get(track_key)
            current = config["step_params"][step][parameter]
            try:
                index = values.index(current)
            except ValueError:
                index = len(values) - 1
            config["step_params"][step][parameter] = values[(index + 1) % len(values)]
            return config["step_params"][step][parameter]

    def toggle_track_automation(self, track_key, effect, step):
        """Record or erase a volume/pitch keyframe at this pattern position."""
        with self.lock:
            pattern = self.get_editing_pattern()
            config = pattern["synths"].get(track_key) or pattern["samples"].get(track_key)
            lane = config.setdefault("automation", {}).setdefault(effect, [None] * self.step_count)
            lane.extend([None] * (self.step_count - len(lane)))
            lane[step] = None if lane[step] is not None else config.get("effects", {}).get(effect, "0")
            return lane[step]

    def clear_track_automation(self, track_key, effect, step):
        with self.lock:
            pattern = self.get_editing_pattern()
            config = pattern["synths"].get(track_key) or pattern["samples"].get(track_key)
            lane = config.get("automation", {}).get(effect)
            if lane is None or step >= len(lane):
                return False
            lane[step] = None
            return True

    def copy_editing_pattern(self):
        with self.lock:
            self.pattern_clipboard = copy.deepcopy(self.get_editing_pattern())

    def paste_editing_pattern(self):
        with self.lock:
            if self.pattern_clipboard is None:
                return False
            self.patterns[self.editing_pattern_idx] = copy.deepcopy(self.pattern_clipboard)
            return True

    def advance_pattern(self):
        with self.lock:
            if self.queued_pattern_idx is not None:
                self.playing_pattern_idx = self.queued_pattern_idx
                self.queued_pattern_idx = None
                if self.playing_pattern_idx in self.song_chain:
                    self.song_position = self.song_chain.index(self.playing_pattern_idx)
            elif self.song_mode and self.song_chain:
                self.song_position = (self.song_position + 1) % len(self.song_chain)
                self.playing_pattern_idx = self.song_chain[self.song_position]

    def save_settings(self):
        with self.lock:
            data = {
                "_bpm": self.bpm,
                "_global_effects": self.global_effects,
                "_nth_notes": self.nth_notes,
                "_steps": self.step_count,
                "_swing": self.swing,
                "_song_chain": self.song_chain,
                "_song_mode": self.song_mode,
                "patterns": self.patterns,
            }
            temporary = self.settings_file.with_suffix(self.settings_file.suffix + ".tmp")
            with temporary.open("w", encoding="utf-8") as target:
                json.dump(data, target, indent=2)
                target.write("\n")
            os.replace(temporary, self.settings_file)
            self._last_update = self.settings_file.stat().st_mtime_ns
