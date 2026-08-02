import json
import shutil
import tempfile
import unittest
from pathlib import Path

from utilities.controls import note_to_freq
from utilities.settings import Settings

try:
    import numpy as np
    from utilities.audio_engine import AudioEngine
except ImportError:
    np = None
    AudioEngine = None


ROOT = Path(__file__).resolve().parents[1]


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "settings.json"
        shutil.copy(ROOT / "settings.json", self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_legacy_file_migrates_and_persists_all_patterns(self):
        current = json.loads(self.path.read_text())
        first = current.pop("patterns")["1"]
        current["_synths"] = first["synths"]
        current["samples"] = first["samples"]
        self.path.write_text(json.dumps(current))
        settings = Settings(self.path)
        self.assertEqual([1, 2, 3, 4], sorted(settings.patterns))
        saved = json.loads(self.path.read_text())
        self.assertIn("patterns", saved)
        self.assertNotIn("_synths", saved)

    def test_clear_uses_configured_step_count(self):
        data = json.loads(self.path.read_text())
        data["_steps"] = 8
        self.path.write_text(json.dumps(data))
        settings = Settings(self.path)
        settings.clear_editing_pattern()
        self.assertTrue(all(len(track["sequence"]) == 8
                            for track in settings.get_editing_pattern()["samples"].values()))

    def test_copy_and_paste_pattern_are_independent(self):
        settings = Settings(self.path)
        settings.get_editing_pattern()["samples"]["kick"]["sequence"][0] = 1
        settings.copy_editing_pattern()
        settings.editing_pattern_idx = 2
        self.assertTrue(settings.paste_editing_pattern())
        settings.get_editing_pattern()["samples"]["kick"]["sequence"][0] = 0
        self.assertEqual(1, settings.patterns[1]["samples"]["kick"]["sequence"][0])

    def test_song_mode_advances_through_the_saved_chain(self):
        settings = Settings(self.path)
        settings.song_chain = [1, 3, 2]
        settings.song_mode = True
        settings.playing_pattern_idx = 1
        settings.song_position = 0
        settings.advance_pattern()
        self.assertEqual(3, settings.playing_pattern_idx)
        settings.advance_pattern()
        self.assertEqual(2, settings.playing_pattern_idx)

    def test_step_controls_and_automation_are_saved_in_the_pattern(self):
        settings = Settings(self.path)
        self.assertEqual(0.75, settings.cycle_step_parameter("kick", 0, "probability",
                                                               [1.0, 0.75, 0.5]))
        self.assertEqual("0.5", settings.toggle_track_automation("kick", "vol", 0))
        snapshot = settings.get_playback_snapshot(0)
        self.assertEqual("0.5", snapshot.samples["kick"]["effects"]["vol"])


class AudioUtilityTests(unittest.TestCase):
    def test_note_parser_supports_multi_digit_and_negative_octaves(self):
        self.assertGreater(note_to_freq("C10"), note_to_freq("C4"))
        self.assertGreater(note_to_freq("C-1"), 0)

    @unittest.skipUnless(AudioEngine is not None, "requires NumPy")
    def test_stereo_wav_is_downmixed(self):
        engine = AudioEngine.__new__(AudioEngine)
        engine.sample_rate = 44100
        engine.sample_cache = {}
        mono = engine.load_sample(ROOT / "samples" / "kick.wav")
        self.assertEqual(18595, len(mono))
        self.assertEqual(np.float32, mono.dtype)


if __name__ == "__main__":
    unittest.main()
