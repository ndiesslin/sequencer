# 🎹 Python Sequencer

> ⚠️ **WARNING**: For the safety of your ears and hardware, please set your volume to **low** before playing!

A terminal-based music sequencer built in Python. Edit patterns, tweak effects, and jam—all from your keyboard.

---

## ✨ Interface Preview

```
                         SEQUENCER TUI - SEQUENCER VIEW

  Synth 1   [100][ C3][200][100][   ][C#2][200][125][%-1][   ][ E2][   ][A2+][   ][ D3][F#3]
  Synth 2   [ G4][ G4][ G4][   ][ G4][ C3][ G4][ B4][ G4][   ][ B4][ B4][   ][ D4][ F4][F#4]
  Kick      [ █ ][ █ ][ █ ][   ][   ][ █ ][ █ ][   ][ █ ][   ][ █ ][   ][ █ ][   ][ █ ][   ]
  Snare     [   ][   ][ █ ][   ][   ][   ][ █ ][   ][   ][   ][ █ ][   ][   ][   ][ █ ][   ]
  Hi-Hat    [ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ][ █ ]

  ARROWS: Move | SPACE: Toggle | [ / ]: Note | TAB: Mixer | S: Save | M/L: Mute/Solo | Q: Quit
  BPM: 95 (+/-) | Swing: 0.50
  Global Pitch: -700c (W/S) | Speed: 5.9x (A/D)
```

---

## Dependencies
- Python 3
- inquirer (pip3 install inquirer)
- sox (for audio processing)

## Usage

To start the sequencer with the interactive TUI:
```bash
python3 tui.py
```

### Controls
## 🎛 Controls

### 🎹 Sequencer View
*   **Navigation**: `ARROWS` to move cursor.
*   **Toggle Step**: `SPACE`
*   **Edit Note**: `[` / `]` to change pitch, `{` / `}` to change octave (Synths only).
*   **Mute Track**: `M`
*   **Solo Track**: `L`

### 🎚 Mixer View (`TAB` to toggle)
*   **Navigation**: `ARROWS` to select parameters.
*   **Adjust Value**: `[` / `]`
*   **Switch Waveform**: Select `Type` column and use `[` / `]` (Saw, Square, Sine, Triangle).
*   **Mute/Solo**: `M` / `L`

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
  - mp3 playback should be a little faster since the files are more compressed, but feel free to try other file types
- Add you sample file name and settings in the settings.json file

## Sound effects
All sound effects are based on sox [checkout the sox documentation for more info](http://sox.sourceforge.net/sox.html)

## [SoX Cheatsheet](./documentation/SOX_CHEATSHEET.md)

## [Future updates](./documentation/FUTURE_FEATURES.md)