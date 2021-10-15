# Cheat sheet with different SoX playback combinations

## SoX documentation and resources:
[SoX Main website](http://sox.sourceforge.net/sox.html)
[man SoX](https://linux.die.net/man/1/sox)

## [SoX Cheatsheet](./documentation/SOX_CHEATSHEET.md)

## Sox (play) merged sample and audio playback
play -m -r 44100 "|sox -r 44100 -n -p synth 1 trapezium %1" "|sox -r 44100 -n -p synth 1 trapezium %3" ./samples/snare.wav ./samples/kick.wav

## Sox merged sample and audio playback
sox --combine mix -r 44100 "|sox -r 44100 -n -p synth 1 trapezium %1" "|sox -r 44100 -n -p synth 1 trapezium %3" ./samples/snare.wav ./samples/kick.wav -d

## Simple sample playback
sox ./samples/snare.wav -d

## Alternate form of merge with pipe
sox -m ./samples/hihat.wav <(sox -n -r44100 -p synth 2 sine F chorus .7 .5 20 1 1 2 -t) <(sox -n -r44100 -p synth 2 sine 200 vol 0.5) <(sox -n -r44100 -p synth 2 sine 900 vol 0.25) -d

## Output the pipe signal as a visual, cool!
sox -r 44100 -n -p synth 0.21 square 100 vol 0.15 gain 1 contrast 10 downsample 1

## Play a synthesized guitar pluck
play -n synth pl G2 pl B2 pl D3 pl G3 pl D4 pl G4 delay 0 .05 .1 .15 .2 .25 remix - fade 0 4 .1 norm -1

## Return a visual spectrogram
sox -n -n synth 6 tri 10k:14k spectrogram -z 100 -w kaiser

## Play samples with their own effects and global effects
sox --combine mix "|sox -v 1 ./samples/snare.wav -p overdrive 80" "|sox -v 0.2 ./samples/kick.wav -p overdrive 10" -d overdrive 80

## NOTE: When piping the sox sample data it takes longer to process than combining samples together
time sox --combine mix "|sox ./samples/snare.wav -p" "|sox ./samples/kick.wav -p" -d overdrive 80
0.03s user 0.03s system 7% cpu 0.741 total

time sox --combine mix ./samples/snare.wav ./samples/kick.wav -d overdrive 80
0.01s user 0.02s system 4% cpu 0.707 total

---
Using mp3 files

time sox --combine mix "|sox ./samples/snare.mp3 -p" "|sox ./samples/kick.mp3 -p" -d overdrive 80
0.04s user 0.04s system 10% cpu 0.727 total

time sox --combine mix ./samples/snare.mp3 ./samples/kick.mp3 -d overdrive 80
0.02s user 0.02s system 5% cpu 0.676 total

sox ./samples/joey.wav -d trim 0 1

sox --combine mix "|sox ./samples/joey.wav -d -p trim 0 0.1" "|sox -v 1 ./samples/snare.wav -p overdrive 80" "|sox -v 0.2 ./samples/kick.wav -p overdrive 10" -d overdrive 80

time sox --combine mix "|sox ./samples/snare.mp3 -p trim 0 0.05" "|sox ./samples/kick.mp3 -p trim 0 0.05" -d overdrive 2
0.02s user 0.03s system 36% cpu 0.134 total

time sox --combine mix ./samples/snare.mp3 ./samples/kick.mp3 -d overdrive 2
0.01s user 0.02s system 7% cpu 0.413 total