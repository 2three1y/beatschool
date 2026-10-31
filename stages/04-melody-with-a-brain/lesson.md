# Stage 04: a melody with a brain

**Run it:** `python stages/04-melody-with-a-brain/render.py` → `out/stage04.wav`

Drums and 808 from stage 03. The lead is replaced by three parts.

## The ideas

**Anchors + free notes.** A melody that repeats exactly gets boring. A melody that's fully random has no hook. So we lock four "anchor" notes in each 2-bar phrase (`ANCHORS`). Those are the hook's spine. The other slots get seeded random notes from the scale, re-rolled every 4 bars. You recognize it every time, and it's never exactly the same.

**The half-step rub.** One anchor is D over a C# minor beat. D is a half step above the root. That tension is the dark, slightly wrong flavor of the underground sound.

**Glide lead.** The lead is mono and slides between notes in 25 ms (portamento), like the digicore tutorials do. It's a saw mixed with a square for bite.

**Call and response.** A second lead (the "answer") plays ONLY in the gaps the first one leaves: an octave up, a square wave, bitcrushed to 5 bits for that old video game color. Two leads talking beats two leads shouting at once.

**Stacked stabs.** Each chord stab is 7 saws detuned against each other and spread left to right. That's the "supersaw" size. They're quiet, on a syncopated 8th grid, and they duck under the 808 too.

## Why it matters
"The synths need something interesting" is the most common note on a beat. Anchors + seeded variation + a second voice in the gaps is the cheapest way to get interesting without getting messy.

## Check it
The 250 Hz–2 kHz share goes up (the melody now has weight). The integrated loudness stays −14, so any difference you hear is the music.

## Try this
- Change the anchor at step 6 from 74 (D) to 75 (D#) and lose the rub.
- `--seed 3` gives new free notes, same hook.
- Set the free-note chance (`0.65` in `phrase`) to 1.0 and hear how the gaps (and the answer) disappear.
