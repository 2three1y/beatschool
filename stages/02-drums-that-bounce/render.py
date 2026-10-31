"""Stage 02: drums that bounce.

Same 808 and lead as stage 01. Only the drums change:
syncopated clap, hats with holes, one skippy 32nd per bar, ONE roll per 8 bars,
the bounce (0, 6, 12 | 4, 10), and a little human wobble in timing and velocity.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(1)           # build on stage 01
SEED, BPM, BARS = prev.SEED, prev.BPM, prev.BARS
bass, lead = prev.bass, prev.lead

# THE BOUNCE: where the low end hits, over 2 bars of 16ths. bar A: 0, 6, 12 / bar B: 4, 10
BOUNCE = [(0, 0), (0, 6), (0, 12), (1, 4), (1, 10)]


def human(g, rng, bar, step, ms=4):
    """a few milliseconds early/late, so it doesn't sound like a metronome"""
    return g.at(bar, step) + int(rng.normal(0, ms / 1000) * SR)


def drums(g, bars, rng):
    n = g.n(bars)
    k, c, h, oh = silence(n), silence(n), silence(n), silence(n)
    for b in range(bars):
        # kick follows the bounce, but light: the 808 will carry most of it (stage 03)
        for bb, st in BOUNCE:
            if b % 2 == bb and not (st == 12 and b % 4 != 2):
                place(k, kick(0.9 if st == 0 else 0.6), g.at(b, st))
        # syncopated clap: always on 3 (step 8); every 2nd bar it also hits the "and of 4" (14);
        # every 4th bar a ghost clap on step 11. Not a plain 2-and-4.
        place(c, clap(rng, 1.0), human(g, rng, b, 8, 2))
        if b % 2 == 1:
            place(c, clap(rng, 0.75), human(g, rng, b, 14, 2))
        if b % 4 == 3:
            place(c, clap(rng, 0.4), human(g, rng, b, 11, 3))
        # hats: 8ths, but with HOLES around the clap (no hat on 8 or 10) so the clap breathes
        for s in range(0, 16, 2):
            if s in (8, 10):
                continue
            v = (1.0 if s % 4 == 0 else 0.62) * rng.uniform(0.85, 1.0)
            place(h, hat(rng, v), human(g, rng, b, s))
        # the skippy 32nd double once per bar (step 6.5 = a 32nd after step 6)
        place(h, hat(rng, 0.5, tone=1.1), human(g, rng, b, 6.5, 2))
        # an open hat at the end of every 4th bar
        if b % 4 == 3:
            place(oh, hat(rng, 0.7, open_=True), g.at(b, 14))
        # ONE roll per 8 bars: last beat of bar 8 in 32nd triplets, getting louder and brighter
        if b % 8 == 7:
            for i in range(6):
                place(h, hat(rng, 0.35 + 0.1 * i, tone=1.0 + 0.06 * i), g.at(b, 12 + i * (4 / 6)))
    return {"kick": k, "clap": c, "hats": h, "open hat": oh}


MIX = {**prev.MIX, "kick": (-8, 0), "open hat": (-16, -0.2)}


def mixdown(stems, mix=MIX):
    return prev.mixdown(stems, mix)


def render(seed=SEED, bars=BARS):
    rng = np.random.default_rng(seed)
    g = Grid(BPM)
    stems = {**drums(g, bars, rng), **bass(g, bars, rng), **lead(g, bars, rng)}
    return mixdown(stems), g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage02.wav")
    report(x, g, name="stage 02")
