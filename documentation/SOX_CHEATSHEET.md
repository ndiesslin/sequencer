play -n synth pluck G2 pluck B2 pluck D3 pluck G3 pluck D4 pluck G4 delay 0 .05 .1 .15 .2 .25 remix - fade 0 4 .1 norm -1

play -m -r 44100 "|sox -r 44100 -n -p synth 1 trapezium %1" "|sox -r 44100 -n -p synth 1 trapezium %3" ./samples/snare.wav ./samples/kick.wav

sox --combine mix -r 44100 "|sox -r 44100 -n -p synth 1 trapezium %1" "|sox -r 44100 -n -p synth 1 trapezium %3" ./samples/snare.wav ./samples/kick.wav -d
