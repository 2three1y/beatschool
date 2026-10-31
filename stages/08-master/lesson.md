# Stage 08: the master

**Run it:** `python stages/08-master/render.py` → `out/stage08.wav`, then a PASS/FAIL list (the script exits 1 if any check fails)

## The ideas

**Loudness is measured, not guessed.** LUFS (loudness units, full scale) measures how loud music *feels*, using a filter shaped like human hearing and gating out silence. Streaming apps turn everything to about −14 LUFS, but beats in this style are mastered around **−9 LUFS** (the references we measured sit at −7 to −10).

**True peak.** Samples can be under 0 dB while the real waveform between them goes over. When the track is turned into an MP3, that becomes distortion. Oversample 4×, measure the peak there, and keep it **≤ −1 dBTP**. We limit to −1.4, because different meters disagree by 0.1–0.2 dB.

**The chain** (in this order, each in plain numpy):
1. high-pass at 25 Hz: rumble nobody hears still uses up loudness
2. glue compressor, 2:1, slow: the parts move together
3. soft saturation (`tanh`): rounds off peaks before the limiter has to
4. look-ahead true-peak limiter, with the gain raised step by step until the song reads −9 LUFS

**Don't crush it.** Crest factor (peak vs average) around 6–9 dB in the drops keeps the punch. Ours is about 7.5 dB.

## The checks it prints
- integrated loudness about −9 LUFS
- true peak ≤ −1 dBTP
- drop 2 is +1 to +2 LU louder than drop 1
- intro 6–10 LU under the drop
- sub is mono (side energy under 120 Hz < 1 %)
- no silences except the two planned risers
- length 1:20–2:15

Cross-check with a second, independent meter:
```
ffmpeg -hide_banner -nostats -i out/stage08.wav -af ebur128=peak=true -f null - 2>&1 | tail -12
```

## Try this
- `master(x, target=-6)`: louder, but the crest drops and the drops stop hitting. Loudness costs punch.
- Remove the saturation step and watch how hard the limiter has to work.
