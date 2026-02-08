# Sequencer Project Context

## 📝 Project Overview
A terminal-based Python step sequencer (TUI) that plays audio using `PyAudio` and `numpy`. It features a 16-step grid, real-time synthesis, sample playback, and a pattern management system.

## 🛠️ Tech Stack
-   **Language**: Python 3
-   **Audio Engine**: `PyAudio` + `numpy` (Continuous stream, low latency)
-   **Interface**: `curses` (Terminal UI)
-   **Configuration**: JSON (`settings.json`)

## 📂 Core Architecture
-   **`tui.py`**: Main entry point. Handles user input, drawing, and thread coordination.
-   **`sequence_player.py`**: Audio thread runner. Manages playback loop and timing.
-   **`utilities/audio_engine.py`**: Persistent audio stream handler.
-   **`utilities/settings.py`**: Manages state, persistence, and pattern migration.

## 🧱 Key Patterns
-   **Dual-Threaded**: TUI runs in main thread; Audio runs in a daemon thread.
-   **Shared State**: Both threads read/write to a shared `Settings` instance.
-   **Pattern Queuing**: Supports 4 patterns. Changes can be queued to switch at the end of a loop.

## 🚀 Improvement Opportunities
-   **Features**:
    -   **Probability**: Random chance for steps to trigger.
    -   **More Effects**: Reverb, Distortion, Filters.
    -   **Export**: Render pattern to WAV file.
