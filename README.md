# 🎹 Python Sequencer

> ⚠️ **WARNING**: For the safety of your ears and hardware, please set your volume to **low** before playing!

A terminal-based music sequencer built in Python. Edit patterns, tweak effects, and jam—all from your keyboard.

---

## ✨ Interface Preview

```
 PATTERNS: [1]P [2]EQ [3] [4]                             SEQUENCER TUI - SEQUENCER VIEW
                     1                     2                     3                     4
  Synth 1   [   ][   ][   ][   ]  [   ][   ][   ][   ]  [   ][   ][   ][   ]  [   ][   ][   ][   ]
  Synth 2   [   ][   ][   ][   ]  [   ][   ][   ][   ]  [   ][   ][   ][   ]  [   ][   ][   ][   ]
  Kick      [ █ ][   ][ █ ][   ]  [ █ ][ █ ][   ][   ]  [ █ ][   ][ █ ][ █ ]  [ █ ][   ][   ][   ]
  Snare     [   ][   ][   ][   ]  [ █ ][   ][   ][   ]  [   ][   ][   ][   ]  [ █ ][   ][   ][   ]
  Hi-Hat    [ █ ][ █ ][ █ ][ █ ]  [   ][   ][ █ ][ █ ]  [ █ ][   ][ █ ][   ]  [ █ ][   ][ █ ][   ]

  ARROWS: Move | SPACE: Toggle | [ / ]: Note | TAB: Mixer | S: Save | M/L: Mute/Solo | Q: Quit
  BPM: 100 (+/-) | Swing: 0.50
  Global Pitch: -700c (W/S) | Speed: 1.0x (A/D)
```

---

## Dependencies
- Python 3
- `pyaudio` (Low-latency audio)
- `numpy` (DSP effects)
- `curses` (Standard library)

Install the Python dependencies in an isolated environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

On Debian/Ubuntu, install the PortAudio development package first if PyAudio needs
to compile: `sudo apt install portaudio19-dev python3-dev`.

## Usage

To start the sequencer with the interactive TUI:
```bash
python3 tui.py
```

### Controls
## 🎛 Controls

### 🎹 Patterns (New!)
*   **Switch Editing View**: `1` `2` `3` `4` (Switch between patterns 1-4)
*   **Queue Pattern**: `ENTER` (Queues currently editing pattern to play next)
*   **Clear Pattern**: `BACKSPACE` (Clears all notes in current pattern)
*   **Copy / Paste Pattern**: `C` / `V` (Copies a complete pattern, including its sound settings)
*   **Reload Saved File**: `R` (Reloads `settings.json` deliberately; playback never reloads it mid-step)
*   **Song Mode**: `J` adds the editing pattern to the song chain, `K` removes its final item, and `X` toggles playback of the chain. The chain loops at pattern boundaries.

### 🎹 Sequencer View
*   **Navigation**: `ARROWS` to move cursor.
*   **Toggle Step**: `SPACE`
*   **Edit Note**: `[` / `]` to change pitch, `{` / `}` to change octave (Synths only).
*   **Chance / Velocity**: `p` / `o` cycle the selected step's trigger chance; `v` / `b` cycle its velocity.
*   **Mute Track**: `M`
*   **Solo Track**: `L`

### 🎚 Mixer View (`TAB` to toggle)
*   **Navigation**: `ARROWS` to select parameters.
*   **Adjust Value**: `[` / `]`
*   **Switch Waveform**: Select `Type` column and use `[` / `]` (Saw, Square, Sine, Triangle).
*   **Mute/Solo**: `M` / `L`
*   **Automation**: Select `Vol` or `Pitch`, then press `R` while playing to record a keyframe at the current step. `BACKSPACE` erases it. Keyframes override that effect only at their recorded step.

### 🌍 Global Controls
*   **Save Settings**: `S` (Saves to `settings.json`)
*   **BPM**: `+` / `-`
*   **Global Pitch**: `W` / `S` (+/- 100 cents)
*   **Global Speed**: `D` / `A` (+/- 10%)
*   **Quit**: `Q`

## Legacy Mode
To run without the TUI (just audio playback):
```bash
python3 sequence_player.py
```

## To add more sounds
- Add your sample file in the samples folder
  - WAV files must currently be 16-bit PCM; stereo files are downmixed safely to mono.
- Add the sample name and settings in the active pattern in `settings.json`. It automatically appears in the TUI after reload.

## Sound effects
All sound effects are based on sox [checkout the sox documentation for more info](http://sox.sourceforge.net/sox.html)

## [SoX Cheatsheet](./documentation/SOX_CHEATSHEET.md)

## [Future updates](./documentation/FUTURE_FEATURES.md)
