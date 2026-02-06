# Sequencer Project Context

## 📝 Project Overview
A terminal-based Python step sequencer that plays audio using `sox` (Sound eXchange). It supports synthesized tones and sample playback, configurable via a JSON file.

## 🛠️ Tech Stack
-   **Language**: Python 3
-   **Audio Backend**: `sox` (via command line)
-   **Configuration**: JSON (`settings.json`)


## 📂 Core Architecture
-   **`settings.json`**: Defines BPM, synth patterns, sample patterns, and effects.

## 🧱 Key Patterns & Limitations
-   **Process-Based Audio**: Each step spawns a new `sox` process via `os.system`. This introduces significant overhead and latency.
-   **Blocking Timing**: Uses `time.sleep()` for sequencing, which is subject to drift and OS scheduling jitter.
-   **Hot Reloading**: Checks file modification time of `settings.json` on every step, adding I/O overhead.

## 🚀 Improvement Opportunities
-   **Performance**: 
    -   Replace `os.system` with `subprocess.Popen` to avoid shell overhead.
    -   Implement drift-correcting timer loop.
    -   Optimize `settings.json` reloading.
-   **Features**:
    -   **Swing/Groove**: Add rhythmic variation.
    -   **TUI**: Real-time control interface.
    -   **Probability**: Random chance for steps to trigger.
