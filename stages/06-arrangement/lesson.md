# Stage 06: arrangement (a loop becomes a song)

**Run it:** `python stages/06-arrangement/render.py` → `out/stage06.wav` (32 bars, about 53 s)

## The plan
| bars | section | what plays |
|---|---|---|
| 1–8 | intro | hook only, low-passed (the "quiet sound"); hats come in at bar 5; bars 7–8: perc pickup |
| 8 (last 2 beats) | silence | nothing at all |
| 9–16 | drop 1, part A | 808 lands, clap, hats, lead, stabs |
| 17–24 | drop 1, part B | hats double (16ths), the answer comes in, open hats |
| 25–32 | outro | drums and 808 out, hook exposed and muffled, snaps open on bar 29, dead stop |

## The ideas

**The arrangement is a function.** `rule(stem, section, bar_in_section, bar)` says, for every part and every bar, whether it plays, how loud, and how filtered. Read the rules and you can read the song.

**The 808 lands on bar 9.** Holding the 808 back for 8 bars makes its entrance THE moment. Under-8-bar intros keep people from skipping.

**Silence is the riser.** Two beats of nothing before the drop hit harder than any whoosh. The measuring tool will list that silence, and that's correct (see AGENTS.md: know which silences are planned).

**Perc pickup.** Two bars before the drop, the claps play the 808's bounce with no 808. Your body learns the rhythm, then the 808 fills it in.

**Two-stage drops.** Drop 1 starts lean and adds the doubled hats + the answer after 8 bars. Rule: never 16 bars untouched, and change one thing at a time.

**Dead stop.** The song ends exactly on the bar line. No fade. A fade says "we ran out of ideas," and a hard stop says "that was on purpose."

**One random generator per part.** `stems_for` gives drums, bass, lead and extras each their own seeded generator, so changing the drums can't reshuffle the melody.

## Check it
The script prints LUFS per section: the intro should sit about 6–10 LU under the drop. Silences: exactly one, at about 12.4–13.2 s (the planned riser).

## Try this
- Make the intro 4 bars: change `PLAN` and the riser bar.
- Let the answer play in part A too, and hear the drop lose its second step.
