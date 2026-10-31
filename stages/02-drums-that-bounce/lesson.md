# Stage 02: drums that bounce

**Run it:** `python stages/02-drums-that-bounce/render.py` → `out/stage02.wav`

Same 808 and lead as stage 01 (the script imports them). Only the drums change.

## The ideas

**The bounce: 0, 6, 12 | 4, 10.** Over two bars of 16ths, the low end hits on steps 0, 6, 12 of bar A and 4, 10 of bar B. It's the backbone of the genre: it pulls against the straight beat, so your head nods. The kick follows it lightly here. In stage 03 the 808 takes it over.

**Syncopated clap.** A plain clap on 2 and 4 sounds like a drum machine demo. Here it's always on beat 3, plus "the and of 4" every second bar, plus a quiet ghost clap every fourth bar.

**Hats with holes.** No hats on steps 8 and 10, right where the clap lands, so the clap has room to breathe. Busy is not the same as good.

**One skippy 32nd per bar.** A quiet extra hat a 32nd note after step 6. It's tiny, and it's the "skip" you hear in PXI-style drums.

**One roll per 8 bars, max.** A hat roll every bar is the oldest trap cliché. One roll at the end of each 8-bar block (32nd-note triplets that get louder and brighter) is the punctuation.

**Human wobble.** Each hit moves a few milliseconds early or late (seeded), and velocities vary by about 15 %. That's enough to stop it sounding like a metronome, small enough to stay tight.

## Why it matters
The drums are the groove. Same notes on top, and stage 02 already moves where stage 01 marched.

## Check it
Same loudness as stage 01 (−14 LUFS), same 808 and lead. The numbers barely move, because a groove is about timing, not level. That's a limit of measuring: an agent checks the pattern itself (print the hit list), not just the meter.

## Try this
- Remove the `if s in (8, 10): continue` line and hear the clap get buried.
- Move the ghost clap from step 11 to step 13.
