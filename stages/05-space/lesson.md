# Stage 05: space

**Run it:** `python stages/05-space/render.py` → `out/stage05.wav`

Same notes as stage 04. Every part gets a place to live.

## The ideas

**Delay vs reverb.** Delay is distinct echoes (ping-pong = they bounce left and right). Reverb is a wash of thousands of echoes, which sounds like a room. Here:
- answer: ping-pong delay every dotted 8th (6 steps), so it bounces
- stabs: 1.8 s reverb, pushed back and big
- lead: a touch of reverb, stays center. The hook is the middle of the song.
- clap: a tiny room so it isn't bone dry

The reverb is convolution with a made-up room (decaying noise). No recorded spaces, nothing sampled.

**Width.** Mid/side: "mid" is what's the same in both ears, "side" is the difference. Turning up the side widens a sound.

**Mono under 120 Hz.** `mono_below` removes all side energy under 120 Hz. Reverb and stereo tricks love to smear the bass into the sides, and this undoes it.

**Free "new": the filter snap and the width snap.** Bar 8 of each 8-bar block is low-passed at 1.5 kHz (muffled, like it's in the next room), then bar 9 snaps fully open. The stabs are narrow in bars 1–8 and wide in 9–16. Same notes, but the second half sounds like something new happened. That's the cheapest trick in arrangement.

## Check it
`side-in-sub` must stay at 0.0 %. Run `python measure.py out/stage05.wav` and compare the "mid" and "high" shares to stage 04: the space adds a little, not a lot.

## Try this
- `reverb(..., wet=0.8)` on the lead: it drowns. More space isn't better.
- Change the delay to `steps=4` (a straight 1/4 note) and hear it lock to the beat instead of bouncing against it.
