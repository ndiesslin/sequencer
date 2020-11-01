# sequencer
| :warning: **WARNING**: for the safety of your ears and hardware, please set your volume to low before playing! |
| --- |

Python sequencer that runs in your terminal

![Demo playback of sequencer](./documentation/images/demo.gif)

## Dependencies
- Python 3
- inquirer (pip3 install inquirer)
- sox (for audio processing)

## To run
- python3 sequence_player.py
- Change settings in settings.json for live changes

## To add more sounds
- Add your sample file in the samples folder
  - mp3 playback should be a little faster since the files are more compressed, but feel free to try other file types
- Add you sample file name and settings in the settings.json file

## Sound effects
All sound effects are based on sox [checkout the sox documentation for more info](http://sox.sourceforge.net/sox.html)

## [SoX Cheatsheet](./documentation/SOX_CHEATSHEET.md)

## [Future updates](./documentation/FUTURE_FEATURES.md)