"""Stage 03: the 808 that talks.

Drums from stage 02, lead from stage 01. The 808 gets rewritten:
it plays THE BOUNCE, slides between notes, pops up an octave once in a while,
wiggles a half step once per 8 bars, and gets saturated so a phone speaker can hear it.
The lead now ducks out of the 808's way (sidechain).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(2)
SEED, BPM, BARS = prev.SEED, prev.BPM, prev.BARS
ROOTS = load_stage(1).ROOTS
BOUNCE = prev.BOUNCE
lead = prev.lead


def bass_notes(g, bars, roots=ROOTS, busy=lambda b: True):
    """-> list of (start, midi, length, slide_to) on the bounce grid."""
    hits = []
    for b in range(bars):
        for bb, st in BOUNCE:
            if b % 2 == bb:
                hits.append((b, st))
        if b % 2 == 1:
            hits.append((b, 14))          # a short note right before the bar line = the slide setup
    notes = []
    for i, (b, st) in enumerate(hits):
        nb, nst = hits[i + 1] if i + 1 < len(hits) else (bars, 0)
        ln = g.at(nb, nst) - g.at(b, st) - 64
        m = roots[b % 4]
        slide = None
        if st == 14:                          # slide into the next bar's root
            slide = roots[(b + 1) % 4] if b + 1 < bars else None
        if busy(b) and b % 4 == 3 and st == 10:
            m, slide = m + 12, m              # octave pop, sliding back down
        if busy(b) and b % 8 == 5 and st == 4:
            m, slide = m + 1, m               # half-step wiggle (the dark rub)
        notes.append((g.at(b, st), m, ln, slide))
    return notes


def bass(g, bars, rng, drive=2.6):
    notes = bass_notes(g, bars)
    return {"808": b808(notes, g.n(bars), drive=drive, decay=1.6, glide=0.075)}


def drums(g, bars, rng):
    d = prev.drums(g, bars, rng)
    # the 808 is the kick now: keep only a light kick on each 2-bar downbeat to add click
    k = silence(g.n(bars))
    for b in range(0, bars, 2):
        place(k, kick(0.7), g.at(b, 0))
    d["kick"] = k
    return d


def sidechain_hits(g, bars):
    return [a for a, *_ in bass_notes(g, bars)]


MIX = {**prev.MIX, "808": (-7, 0), "hats": (-9, 0.15)}


def mixdown(stems, mix=MIX, g=None, bars=BARS):
    if g is not None:   # duck the lead under each 808 hit so the low end punches through
        stems = dict(stems)
        stems["lead"] = stems["lead"] * duck(len(stems["lead"]), sidechain_hits(g, bars), depth=0.35)
    return prev.mixdown(stems, mix)


def render(seed=SEED, bars=BARS):
    rng = np.random.default_rng(seed)
    g = Grid(BPM)
    stems = {**drums(g, bars, rng), **bass(g, bars, rng), **lead(g, bars, rng)}
    return mixdown(stems, g=g, bars=bars), g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage03.wav")
    report(x, g, name="stage 03")
