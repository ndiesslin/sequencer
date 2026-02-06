
import curses
import threading
import queue
import time
import sys
import re

# Connect to sequencer
from sequence_player import sequence_runner, settings

# Track definitions for the grid
TRACKS = [
    {'type': 'synth', 'key': 'synth_1', 'label': 'Synth 1'},
    {'type': 'synth', 'key': 'synth_2', 'label': 'Synth 2'},
    {'type': 'sample', 'key': 'kick', 'label': 'Kick   '},
    {'type': 'sample', 'key': 'snare', 'label': 'Snare  '},
    {'type': 'sample', 'key': 'hihat', 'label': 'Hi-Hat '},
]

# Mixer Parameters definition
# (Label, key in effects dict, step size)
MIXER_PARAMS = [
    {'label': 'Vol', 'key': 'vol', 'step': 0.05, 'default': '1.0'},
    {'label': 'Type', 'key': 'type', 'step': 0, 'default': 'saw'}, # Synth type
    {'label': 'Pitch', 'key': 'pitch', 'step': 100, 'default': '0'}, # For samples/synths? Both?
    # Synth specific
    {'label': 'Trem Spd', 'key': 'tremolo_speed', 'step': 1, 'default': '0'},
    {'label': 'Trem Dep', 'key': 'tremolo_depth', 'step': 5, 'default': '0'}, 
    {'label': 'Echo Dly', 'key': 'echo_delay', 'step': 10, 'default': '0'},
    {'label': 'Echo Fbk', 'key': 'echo_decay', 'step': 0.05, 'default': '0'}
]

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
WAVEFORMS = ['saw', 'square', 'sine', 'triangle']

def increment_note(note_str, semitones):
    # Handle empty
    if not note_str: return "C3"
    
    # Handle chords (just take first for now or ignore?)
    if '+' in note_str: return note_str 
    
    # Parse note
    match = re.match(r"([A-G]#?)(-?\d+)", note_str)
    if not match: return note_str
    
    note_name = match.group(1)
    octave = int(match.group(2))
    
    try:
        idx = NOTES.index(note_name)
    except ValueError:
        return note_str
        
    # Calculate new index
    total_idx = idx + (octave * 12) + semitones
    
    new_octave = total_idx // 12
    new_note_idx = total_idx % 12
    
    return f"{NOTES[new_note_idx]}{new_octave}"

def draw_header(stdscr, width, view_mode, msg=""):
    title = f" SEQUENCER TUI - {view_mode} VIEW "
    if msg: title += f" [{msg}] "
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(0, 0, title.center(width))
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

def draw_controls(stdscr, row, width, view_mode):
    # Draw control hints
    if view_mode == "SEQUENCER":
        hints = "ARROWS: Move | SPACE: Toggle | [ / ]: Note | TAB: Mixer | S: Save | M/L: Mute/Solo | Q: Quit"
    else:
        hints = "ARROWS: Move | [ / ]: Adjust | TAB: Sequencer | S: Save | M/L: Mute/Solo | Q: Quit"
        
    stdscr.addstr(row, 2, hints, curses.color_pair(4))
    
    # Status Line
    status = f"BPM: {settings.bpm} (+/-) | Swing: {getattr(settings, 'swing', 0.5):.2f}"
    stdscr.addstr(row + 1, 2, status)
    
    # Effects Status
    efx = settings.global_effects
    efx_str = f"Global Pitch: {efx.get('pitch', '0')}c (W/S) | Speed: {efx.get('speed', '1')}x (A/D)"
    stdscr.addstr(row + 2, 2, efx_str)

def draw_grid(stdscr, start_row, cursor_row, cursor_col, current_step):
    # Draw tracks
    for t_idx, track in enumerate(TRACKS):
        row = start_row + t_idx
        key = track['key']
        
        # Check Mute/Solo
        track_state = getattr(settings, 'track_state', {})
        is_muted = key in track_state.get('muted', set())
        is_solo = track_state.get('solo') == key
        
        # Label
        label = track['label']
        if is_muted: label = f"{label} (M)"
        if is_solo:  label = f"{label} (S)"
        
        if t_idx == cursor_row:
            stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(row, 2, label)
        if t_idx == cursor_row:
            stdscr.attroff(curses.A_REVERSE)
            
        # Steps
        # Get sequence data
        if track['type'] == 'synth':
            seq = settings.synths[track['key']]['sequence']
        else:
            seq = settings.samples[track['key']]['sequence']
            
        # Draw steps
        for step in range(16): # Assuming 16 steps max for now
            val = seq[step]
            
            # Check if active (playing)
            is_playing = (step == current_step)
            is_cursor = (t_idx == cursor_row and step == cursor_col)
            
            # Widen grid for notes (5 chars per step)
            x_pos = 12 + (step * 5)
            
            symbol = "[   ]"
            
            # Dim if muted
            display_attr = curses.A_DIM if is_muted else curses.A_NORMAL
            
            if track['type'] == 'sample':
                if val == 1:
                    symbol = "[ █ ]"
            else:
                if val != "":
                    # Center note
                    note_str = str(val)
                    if len(note_str) > 3: note_str = note_str[:3] # truncate if too long
                    symbol = f"[{note_str.center(3)}]" 

            # Colors
            attr = display_attr
            if is_cursor:
                attr = curses.A_REVERSE
            if is_playing:
                attr = curses.color_pair(2) # Green background/text
                
            try:
                stdscr.addstr(row, x_pos, symbol, attr)
            except curses.error:
                pass

def draw_mixer(stdscr, start_row, cursor_row, cursor_col):
    # Draw headers
    headers = ["Track"] + [p['label'] for p in MIXER_PARAMS]
    header_str = "  ".join([h.center(10) for h in headers])
    stdscr.addstr(start_row, 2, header_str, curses.A_UNDERLINE)
    
    for t_idx, track in enumerate(TRACKS):
        row = start_row + 2 + t_idx
        
        # Track Name
        label = track['label']
        # Mute/Solo indicators
        track_state = getattr(settings, 'track_state', {})
        is_muted = track['key'] in track_state.get('muted', set())
        is_solo = track_state.get('solo') == track['key']
        if is_muted: label += " M"
        elif is_solo: label += " S"
        
        stdscr.addstr(row, 2, label.center(10))
        
        # Get Config
        if track['type'] == 'synth':
            config = settings.synths[track['key']]
            effects = config.get('effects', {})
        else:
            config = settings.samples[track['key']]
            effects = config.get('effects', {})
            
        # Draw Params
        for p_idx, param in enumerate(MIXER_PARAMS):
            is_selected = (t_idx == cursor_row and p_idx == cursor_col)
            attr = curses.A_REVERSE if is_selected else curses.A_NORMAL
            
            val = "N/A"
            key = param['key']
            
            # WAVEFORM TYPE
            if key == 'type':
                if track['type'] == 'synth':
                    val = config.get('type', 'saw')
                else:
                    val = "---"
            
            # COMPOSITE KEYS
            elif key.startswith('tremolo_'):
                raw = effects.get('tremolo', '0 0')
                parts = raw.split()
                if len(parts) < 2: parts = ['0', '0']
                if key == 'tremolo_speed': val = parts[0]
                else: val = parts[1]
            
            elif key.startswith('echo_'):
                # parse "0.8 0.2 250 0.2" -> In, Out, Delay, Decay
                raw = effects.get('echo', '0 0 0 0')
                parts = raw.split()
                if len(parts) < 4: parts = ['0', '0', '0', '0']
                if key == 'echo_delay': val = parts[2]
                elif key == 'echo_decay': val = parts[3]
                else: val = "N/A"
                
            else:
                val = effects.get(key, param['default'])
            
            # VISUALIZER FOR VOLUME
            display_val = str(val)
            if key == 'vol':
                 # Add ascii bar
                 try:
                     fv = float(val)
                     bars = int(fv * 5)
                     bar_str = "|" * bars
                     display_val = f"{val} {bar_str}"
                 except: pass
                 
            # Formatting
            x_pos = 14 + (p_idx * 12) # 2 chars padding + 10 width
            
            try:
                stdscr.addstr(row, x_pos, display_val.center(10), attr)
            except curses.error:
                pass

def toggle_step(track_idx, step_idx):
    track = TRACKS[track_idx]
    if track['type'] == 'sample':
        seq = settings.samples[track['key']]['sequence']
        # Toggle 0/1
        seq[step_idx] = 1 if seq[step_idx] == 0 else 0
    else:
        seq = settings.synths[track['key']]['sequence']
        # Toggle Note/Empty
        if seq[step_idx] == "":
            seq[step_idx] = "C3"
        else:
            seq[step_idx] = ""

def adjust_note(track_idx, step_idx, semitones):
    track = TRACKS[track_idx]
    if track['type'] != 'synth': return
    
    seq = settings.synths[track['key']]['sequence']
    current = seq[step_idx]
    if current == "":
        seq[step_idx] = "C3"
    else:
        seq[step_idx] = increment_note(str(current), semitones)

def format_effect_val(val, delta):
    # Helper to increment numeric string
    try:
        n = float(val)
        n += delta
        if n.is_integer():
            return str(int(n))
        return str(round(n, 2))
    except:
        return val

def adjust_mixer_param(track_idx, param_idx, direction):
    track = TRACKS[track_idx]
    param = MIXER_PARAMS[param_idx]
    key = param['key']
    
    # Get Dicts
    if track['type'] == 'synth':
        config = settings.synths[track['key']]
        if 'effects' not in config: config['effects'] = {}
        effects = config['effects']
    else:
        config = settings.samples[track['key']]
        if 'effects' not in config: config['effects'] = {}
        effects = config['effects']
    
    # TYPE SWITCHING
    if key == 'type':
        if track['type'] == 'synth':
            current = config.get('type', 'saw')
            try:
                idx = WAVEFORMS.index(current)
            except: idx = 0
            
            new_idx = (idx + direction) % len(WAVEFORMS)
            config['type'] = WAVEFORMS[new_idx]
        return

    # COMPOSITE KEYS
    if key.startswith('tremolo_'):
        raw = effects.get('tremolo', '0 0')
        parts = raw.split()
        if len(parts) < 2: parts = ['0', '0']
        
        speed = float(parts[0])
        depth = float(parts[1])
        
        if key == 'tremolo_speed':
            speed += (param['step'] * direction)
            speed = max(0, speed)
        else:
            depth += (param['step'] * direction)
            depth = max(0, depth)
            
        effects['tremolo'] = f"{speed} {depth}"
        
    elif key.startswith('echo_'):
        raw = effects.get('echo', '0.8 0.5 0 0')
        parts = raw.split()
        if len(parts) < 4: parts = ['0.8', '0.5', '0', '0']
        
        delay = float(parts[2])
        decay = float(parts[3])
        
        if key == 'echo_delay':
            delay += (param['step'] * direction)
            delay = max(0, delay)
        else:
            decay += (param['step'] * direction)
            decay = max(0, min(1.0, decay))
            
        effects['echo'] = f"{parts[0]} {parts[1]} {int(delay)} {decay:.2f}"
        
    else:
        # Standard key
        val = effects.get(key, param['default'])
        new_val = format_effect_val(val, param['step'] * direction)
        effects[key] = new_val

def toggle_mute(track_idx):
    key = TRACKS[track_idx]['key']
    track_state = getattr(settings, 'track_state')
    
    if key in track_state['muted']:
        track_state['muted'].remove(key)
    else:
        track_state['muted'].add(key)

def toggle_solo(track_idx):
    key = TRACKS[track_idx]['key']
    track_state = getattr(settings, 'track_state')
    
    if track_state['solo'] == key:
        track_state['solo'] = None # Unsalo
    else:
        track_state['solo'] = key # Solo this

def main(stdscr):
    # Setup colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Active Playhead
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Cursor
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK) # Hints
    
    # Hide cursor
    curses.curs_set(0)
    
    # Non-blocking input
    stdscr.nodelay(True)
    stdscr.timeout(50) # Refresh input every 50ms
    
    # Communication queues
    stop_event = threading.Event()
    ui_queue = queue.Queue()
    
    # Start Audio Thread
    audio_thread = threading.Thread(
        target=sequence_runner,
        args=(stop_event, ui_queue),
        daemon=True
    )
    audio_thread.start()
    
    current_step = -1
    total_steps = 16
    
    view_mode = "SEQUENCER" 
    cursor_row = 0
    cursor_col = 0 
    
    flash_msg = ""
    flash_timer = 0
    
    try:
        while True:
            # Handle UI Updates
            try:
                latest = None
                while True:
                    latest = ui_queue.get_nowait()
            except queue.Empty:
                pass
            if latest:
                current_step = latest['step']
                total_steps = latest['total_steps']
                
            # Draw UI
            height, width = stdscr.getmaxyx()
            stdscr.erase()
            
            # Flash handling
            if time.time() > flash_timer:
                flash_msg = ""
            
            draw_header(stdscr, width, view_mode, flash_msg)
            
            if view_mode == "SEQUENCER":
                draw_grid(stdscr, 2, cursor_row, cursor_col, current_step)
            else:
                draw_mixer(stdscr, 2, cursor_row, cursor_col)
            
            # Controls
            draw_controls(stdscr, 10 + len(TRACKS), width, view_mode)
            stdscr.refresh()
            
            # Input
            key = stdscr.getch()
            
            if key == ord('q'):
                break
            elif key == 9: # TAB
                view_mode = "MIXER" if view_mode == "SEQUENCER" else "SEQUENCER"
                cursor_col = 0 
            
            elif key == ord('S'): # Save
                settings.save_settings()
                flash_msg = "SAVED!"
                flash_timer = time.time() + 2
                
            elif key == ord('m') or key == ord('M'): # Mute
                toggle_mute(cursor_row)
            elif key == ord('l') or key == ord('L'): # Solo
                toggle_solo(cursor_row)
                
            elif key == curses.KEY_UP:
                cursor_row = max(0, cursor_row - 1)
            elif key == curses.KEY_DOWN:
                cursor_row = min(len(TRACKS) - 1, cursor_row + 1)
            elif key == curses.KEY_LEFT:
                cursor_col = max(0, cursor_col - 1)
            elif key == curses.KEY_RIGHT:
                if view_mode == "SEQUENCER":
                    limit = total_steps - 1
                else:
                    limit = len(MIXER_PARAMS) - 1
                cursor_col = min(limit, cursor_col + 1)
                
            # Editing
            elif view_mode == "SEQUENCER":
                if key == 32: # SPACE
                    toggle_step(cursor_row, cursor_col)
                elif key == ord(']'): 
                    adjust_note(cursor_row, cursor_col, 1)
                elif key == ord('['): 
                    adjust_note(cursor_row, cursor_col, -1)
                elif key == ord('}'): 
                    adjust_note(cursor_row, cursor_col, 12)
                elif key == ord('{'): 
                    adjust_note(cursor_row, cursor_col, -12)
            else: # MIXER
                if key == ord(']'):
                    adjust_mixer_param(cursor_row, cursor_col, 1)
                elif key == ord('['):
                    adjust_mixer_param(cursor_row, cursor_col, -1)
                    
            # Global
            if key == ord('='): settings.bpm += 5
            elif key == ord('-'): settings.bpm = max(10, settings.bpm - 5)
            # Global Effects
            elif key == ord('w'):
                p = settings.global_effects.get('pitch', '0')
                settings.global_effects['pitch'] = format_effect_val(p, 100)
            elif key == ord('s'):
                p = settings.global_effects.get('pitch', '0')
                settings.global_effects['pitch'] = format_effect_val(p, -100)
            elif key == ord('d'):
                s = settings.global_effects.get('speed', '1')
                settings.global_effects['speed'] = format_effect_val(s, 0.1)
            elif key == ord('a'):
                s = settings.global_effects.get('speed', '1')
                settings.global_effects['speed'] = format_effect_val(s, -0.1)
            
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        audio_thread.join(timeout=1.0)

if __name__ == "__main__":
    curses.wrapper(main)
