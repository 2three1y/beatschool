# AGENTS.md: rules for AI agents making beats with this repo

You (an AI agent) are going to write code that makes music you can't hear. That's fine. Producers trust their meters as much as their ears. This file is how you work without ears.

## 0. The hard rules
1. **Original synthesis only.** Every sound comes from math: oscillators, noise, filters, envelopes, our own renders fed back into themselves. **Never sample, chop, resample, or "reference-load" third-party audio** (songs, YouTube/TikTok rips, sample packs you don't have rights to, other people's stems). References are for *feel*: tempo, structure, levels, measured from a copy you delete afterwards. Their audio never enters your mix.
2. **No cloned or commercial voices.** No TTS voice of a real artist, no voice-cloning, no vocals from a commercial voice product. If you use a voice at all, it must be public domain or CC0, and you say which in the README.
3. **Seed everything.** Every random choice goes through `np.random.default_rng(seed)`. Same seed, same file, byte for byte. One generator per part (see stage 06), so changing the drums can't reshuffle the melody.
4. **numpy + scipy + soundfile.** No DAW, no plugins, no hidden binaries. Anyone can run `pip install -r requirements.txt` and get your exact beat.
5. **Don't claim what you didn't measure.** "It slaps" isn't a measurement. "Drop 2 is +1.2 LU over drop 1, true peak −1.4 dBTP" is.

## 1. You can't hear, so measure
Run after EVERY render:
```
python measure.py out/your.wav --bpm 145 --sections "intro:0:8,drop 1:8:24,drop 2:40:56"
```
and cross-check with an independent meter:
```
ffmpeg -hide_banner -nostats -i out/your.wav -af ebur128=peak=true -f null - 2>&1 | tail -12
ffmpeg -hide_banner -i out/your.wav -af silencedetect=noise=-35dB:d=0.4 -f null - 2>&1 | grep silence_
```

| what | target (this style) | why |
|---|---|---|
| integrated loudness | about −9 LUFS (refs −7 to −10) | competitive with the genre without crushing it |
| true peak | ≤ −1 dBTP (limit at −1.4) | MP3/AAC encoding adds overs between samples |
| crest factor in the drops | 6–9 dB | under 6 = squashed flat; over 10 = not finished |
| intro vs drop | intro 6–10 LU quieter | the drop needs somewhere to land |
| drop 2 vs drop 1 | +1 to +2 LU | the second drop must feel bigger |
| side energy under 120 Hz | < 1 % | the sub must be mono |
| silences > 0.4 s | ONLY the ones you planned | an unplanned hole is a bug (a dead stem, a bad slice) |
| energy in sub (<60 Hz) | roughly 70–90 % | it's an 808 genre; under 60 % = thin, over 95 % = only bass |
| length | 1:20–2:15 | the length these beats live at |

**Spectral checks** (`kit.bands`): if your "brighter" version doesn't move the 2–8 kHz share, it isn't brighter. If saturation on the 808 doesn't raise the 60–250 Hz share, phone speakers won't hear it.

**Duration is the container's word, not the music's.** A 30-second file can hold 13 seconds of music and 17 of silence. Always run the silence check.

**Section LUFS beat whole-file LUFS** for arrangement questions. Is the switch-up weaker than the drop? Measure the two sections.

**What meters can't tell you:** whether a groove grooves, whether a melody is catchy. For those, check the *structure*: print the hit list and the note list, confirm the bounce is on 0, 6, 12 | 4, 10, the anchors are where you put them, and no two leads play at once where they shouldn't. When a human listener gives a note ("the switch is boring"), that note outranks every number here.

## 2. How to work
1. **Change one thing per render.** Then measure. If you change five things and the numbers move, you don't know why.
2. **Build on the previous stage.** Import it (`kit.load_stage(n)`), override one function. Don't fork the whole file.
3. **Keep the arrangement in one function** (`rule()` in stages 06–07). The song should be readable.
4. **Render, then measure, then report the numbers.** Every message about a beat carries its LUFS, true peak and silences.
5. **Mind the disk and the clock.** A 2-minute stereo float file is about 40 MB in RAM and 28 MB as 24-bit WAV. Delete renders you don't need. Wrap long renders in a timeout (`timeout -k 5 120 python ...`).
6. **Previews are MP3, short and small.** `ffmpeg -i out/x.wav -t 30 -b:a 64k preview.mp3` is about 240 KB.

## 3. The style target
See `docs/style-guide.md`: tempo, keys, drum rules, 808 rules, arrangement rules, loudness. The stages implement it step by step.

## 4. If you're asked to "make it slap"
That means, in order: the 808 moves and is heard on a phone (saturated), the drums bounce (syncopated clap, hats with holes), the melody has a hook plus variation, there's a switch-up with new drums + a new 808 + a new melodic idea, drop 2 beats drop 1, it ends dead on the bar line, and it's mastered to the table above. Stages 01→08 are exactly that list.
