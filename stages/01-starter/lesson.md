# Stage 01: a starter beat that doesn't suck

**Run it:** `python stages/01-starter/render.py` → `out/stage01.wav` (16 bars, about 26 s)

## What you hear
A kick, a clap, hi-hats, an 808 and a simple saw lead. 145 BPM, C# minor. It's plain, but nothing in it is wrong.

## The ideas

**The grid.** Music in this style lives on 16th notes. At 145 BPM a beat lasts 60 / 145 = 0.414 s. A 16th note ("step") is a quarter of that, and a bar is 16 steps. `Grid.at(bar, step)` turns "bar 3, step 8" into a sample number. Every hit in the course is placed this way, so nothing drifts.

**One key.** Every pitched sound uses C# minor. The 808 plays the ROOT of each chord (C#, A, F#, G#: i, VI, iv, V), one note per bar. The lead only uses notes from the scale. That's why it already sounds "together."

**The 808 is the bass.** In this style there's no separate bass synth. The 808 (a long sine with a quick pitch drop at the start) covers the bass AND most of the low end. The kick just adds a click on top.

**Half-time clap.** The clap on beat 3 of each bar (step 8) makes 145 BPM feel like 72.5. That's the laid-back bounce of trap, plugg and underground beats.

**Seeds.** Every random choice in this course comes from a seeded random generator. Same seed, same beat, every time. Change `--seed` to get a different version you can still reproduce.

## Why it doesn't suck
Tempo in the genre's pocket (140–155). Everything is in one key. The 808 follows the chords. There's a clear backbeat. Nothing clips.

## What's still wrong (the rest of the course fixes it)
- The drums are stiff: straight 8th hats, the clap in the same spot every bar.
- The 808 just sits there.
- The lead repeats the same 2 bars forever.
- Everything is dry and in the middle.
- It's a loop, not a song.

## Check it (numbers, not ears)
`python measure.py out/stage01.wav`: about −14 LUFS (all stages 01–07 are set to −14 so you compare music, not volume), true peak under −1 dBTP, no silences, side energy in the sub = 0 %.

## Try this
- `--seed 7`: the hats' tiny random variations change.
- Change `BPM` to 160 and listen to how the same notes feel more hyper.
- Change `ROOTS` to `[25, 30, 33, 32]` (i, iv, VI, V).
