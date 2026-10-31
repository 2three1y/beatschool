# Stage 07: the switch-up, drop 2 and transition FX

**Run it:** `python stages/07-switch-up-and-drop-2/render.py` → `out/stage07.wav` (64 bars, about 1:46)

## The plan
| bars | section | what happens |
|---|---|---|
| 1–8 | intro | as stage 06 |
| 9–24 | drop 1 | as stage 06, then a **tape stop** on the last 2 beats |
| 25–40 | switch-up | new drums, new 808, new roots, new melody (a grain cloud). Bars 33–40 add a harp arp + hats. Riser, **stutter**, 2 beats of silence |
| 41–56 | drop 2 | **impact**; drop 1 but bigger: lead doubled an octave up, dirtier 808 with more pops, wider stabs, the cloud stays. Ends with a **reverse swell** |
| 57–64 | outro | hook alone, muffled, snaps open on bar 61, dead stop |

## The ideas

**The switch must be the coolest part.** A switch that's just the same loop with a filter is a letdown. It needs THREE new things:
1. new drums: a jersey-club kick bounce (0, 6, 10, 12, 14 / 0, 4, 7, 10, 13) and claps on 2 and 4
2. a new 808 pattern on new roots (F#, A, E, G#), two long notes per bar, the second one sliding
3. a new melodic idea: the **grain cloud** (lesson 7 below)

**The grain cloud (lesson 7, learned from a producer's granulizer tutorial).** Write a SIMPLE line. Wreck it on purpose: heavy saturation, then a 1/32 stutter every 2 bars. Then granulate it: thousands of 30–90 ms slices, each read near the playhead with random jitter, random pan, and sometimes shifted an octave up or down. Then gate it on the 16th grid so it grooves. The notes survive, but they're never played the same way twice. All seeded, all our own audio.

**Drop 2 > drop 1.** Same hook, more of everything: an octave-up double, a dirtier 808 (drive 4.5, more octave pops), wider stabs, the cloud as a new layer. Then the script MEASURES both drops and rides drop 2 up to +2.6 LU over drop 1. The master squeezes about 1 LU of that back, landing around +1.2. Measure, don't guess.

**Transition FX, one or two of each, max.**
- tape stop: the audio slows to a halt, like pulling the plug on a turntable (out of drop 1)
- riser + stutter + silence + impact (into drop 2)
- reverse swell (into the outro)
Stack every FX at every transition and they stop meaning anything.

## Check it
Section LUFS: drop 2 above drop 1, the switch about as loud as drop 1, intro and outro well under. Silences: exactly two, the planned risers before bar 9 and bar 41.

## Try this
- Set `octave_prob=0` in the cloud and hear it lose its sparkle.
- Swap the tape stop for a second stutter. (Then remove it again. One of each is the point.)
