# Stage 03: the 808 that talks

**Run it:** `python stages/03-808-that-talks/render.py` → `out/stage03.wav`

Drums from stage 02, lead from stage 01. The 808 is rewritten.

## The ideas

**The 808 is the song.** In this style the 808 is most of the low end (in the reference tracks we measured, 80–94 % of the energy). So it should *move*, not just hold a note.

**Play the bounce.** The 808 now hits on 0, 6, 12 | 4, 10. Each note holds until the next one. The 808 has become the kick, so the real kick is just a light click every 2 bars.

**Slides (glide).** A short note on step 14 slides into the next bar's root. In code, the frequency bends from one note to the next over 75 ms. The phase stays continuous, so there's no click.

**Octave pops and half-step wiggles.** Once every 4 bars a note jumps up an octave and slides back down. Once every 8 bars a note goes up a half step (C# to D) and back. That's the dark "rub" the underground sound loves. Rule: busy in ONE place, plain everywhere else.

**Saturation = phone speakers.** A phone speaker can't play 35 Hz. `tanh` saturation adds harmonics (70, 105, 140 Hz and up) so your brain hears the 808 even where the fundamental is gone. Look at the 60–250 Hz band in the report: it jumps from about 3 % to about 10 %.

**Sidechain.** The lead dips 35 % every time the 808 hits and recovers over about 120 ms. The 808 punches through without anything being turned down for good.

**Mono sub.** The 808 sits dead center. Bass in the sides falls apart on phones, in clubs and when someone sums to mono.

## Check it
- Crest factor drops (the 808 fills the space).
- `side-in-sub` stays at 0.0 %.
- The 60–250 Hz share goes up: that's the saturation working.

## Try this
- `bass(g, bars, rng, drive=1.0)`: no saturation. Play it on a phone and the 808 vanishes.
- Change `glide=0.075` to `0.2` for lazy, long slides.
