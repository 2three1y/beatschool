# beatschool

**Learn to make beats with code.** A course for AI agents AND people. It starts with a starter beat that doesn't suck and upgrades it one idea at a time until it actually slaps. 8 stages, 1 song, all in Python.

No DAW, no plugins, no samples. Every sound (kick, clap, 808, leads, reverb, risers) is made from math in `kit.py`, using only numpy, scipy and soundfile. Every random choice is seeded, so you get the exact same beat we did.

## Who it's for
- **AI agents** that can write code but can't hear. Read [`AGENTS.md`](AGENTS.md) first: you measure instead of listening (LUFS, true peak, silences, spectrum).
- **People** who want to know *why* a beat slaps, not just which buttons to press. Each stage has a short lesson in plain words.
- **Blind and low-vision producers.** Everything is text: code, lessons, and numbers you can read with a screen reader. No piano roll required.

## Run it
```
pip install -r requirements.txt
python stages/01-starter/render.py      # writes out/stage01.wav
python measure.py out/stage01.wav        # loudness, true peak, silences, spectrum
```
Render every stage (about 1.5 minutes on a laptop):
```
for s in stages/*/; do python "$s/render.py"; done
```
Change the seed to get your own variation: `python stages/04-melody-with-a-brain/render.py --seed 7`

## The stages
Each stage **imports the one before it** and changes one idea. Diff two stages and you see exactly what changed. Every folder has `lesson.md`, `render.py` and a 30-second `preview.mp3`.

| # | stage | the idea |
|---|---|---|
| 01 | [starter](stages/01-starter/) | the grid, one key, the 808 is the bass, a half-time clap: a 16-bar loop that already doesn't suck |
| 02 | [drums that bounce](stages/02-drums-that-bounce/) | the bounce (0, 6, 12 \| 4, 10), a syncopated clap, hats with holes, one roll per 8 bars, a little human wobble |
| 03 | [the 808 that talks](stages/03-808-that-talks/) | an 808 on the bounce, slides, octave pops, the half-step wiggle, saturation for phone speakers, sidechain |
| 04 | [a melody with a brain](stages/04-melody-with-a-brain/) | anchor notes + seeded free notes, the half-step rub, a glide lead, call and response, supersaw stabs |
| 05 | [space](stages/05-space/) | ping-pong delay, reverb, width, mono sub, the filter snap and the width snap |
| 06 | [arrangement](stages/06-arrangement/) | a filtered intro, the 808 landing on bar 9, silence as the riser, two-stage drop, dead-stop outro |
| 07 | [switch-up + drop 2](stages/07-switch-up-and-drop-2/) | a switch with new drums, a new 808 and a grain cloud; tape stop, stutter, impact, reverse swell; drop 2 > drop 1 |
| 08 | [master](stages/08-master/) | glue, saturation, a true-peak limiter: −9 LUFS, ≤ −1 dBTP, and a PASS/FAIL check list |

## The finished beat, by the numbers
Stage 08, seed 1: **1:46**, 145 BPM, C# minor, 64 bars.

| check | result |
|---|---|
| integrated loudness | −9.1 LUFS (ffmpeg ebur128 agrees within 0.1) |
| true peak | −1.3 to −1.4 dBTP (depending on the meter) |
| drop 2 vs drop 1 | +1.1 LU |
| intro vs drop | 8.0 LU quieter |
| sub in the sides | 0.0 % |
| silences | exactly two, both planned (the 2-beat risers before each drop) |

## Files
- `kit.py`: the instruments, effects, mixer, meters and limiter. Read it once, top to bottom.
- `measure.py`: the meters as a command-line tool.
- `stages/NN-name/`: lesson + script + preview.
- `docs/style-guide.md`: the target sound (tempo, keys, drums, 808, arrangement, loudness).
- `AGENTS.md`: the rules for AI agents.

## Rules we follow (and you should too)
- **Original sounds only.** We never sample anyone's audio. References are studied for feel (tempo, structure, levels) and deleted.
- **No cloned or commercial voices.** If a voice is ever added, it'll be public domain or CC0, and labeled.
- **Measure everything.** "It slaps" is a feeling. "Drop 2 is +1.1 LU over drop 1" is a fact.

## Credits
Made by **Chaotic Carter** (2three1y), a blind producer and dev. [Website](https://2three1y.github.io/) · [YouTube](https://www.youtube.com/@chaotic_carter) · [TikTok](https://www.tiktok.com/@chaotic_carter) · [GitHub](https://github.com/2three1y)

Ideas learned from producer tutorials (nightiger's digicore melody guides, k0l's granulizer trick, and more), rewritten in our own words and rebuilt from scratch in code.

## License
Code: [MIT](LICENSE). Lessons, docs and previews: [CC BY 4.0](LICENSE-docs.md).

---
Co-written with Tab
