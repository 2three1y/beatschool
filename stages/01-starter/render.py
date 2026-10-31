"""Stage 01: a starter beat that doesn't suck.

16 bars, 145 BPM, C# minor. Kick, clap, hats, an 808 and a simple lead.
Run:  python stages/01-starter/render.py        (writes out/stage01.wav)
      python stages/01-starter/render.py --seed 7
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

SEED = 1
BPM = 145
BARS = 16
KEY_ROOT = 61                    # C#4. The key: C# minor.
ROOTS = [25, 33, 30, 32]         # 808 notes, one per bar: C#1, A1, F#1, G#1  (i - VI - iv - V)
# The lead's 2-bar idea, as (step, midi, length in steps). Steps are 16ths: 0..31 over 2 bars.
MOTIF = [(0, 73, 3), (3, 76, 3), (6, 75, 2), (8, 73, 4), (14, 71, 2),
         (16, 73, 3), (19, 76, 3), (22, 78, 2), (24, 76, 4), (30, 75, 2)]


def drums(g, bars, rng):
    """Kick on 1 (and a pickup kick), clap on beat 3 (= half-time feel), straight 8th hats."""
    n = g.n(bars)
    k, c, h = silence(n), silence(n), silence(n)
    for b in range(bars):
        place(k, kick(), g.at(b, 0))
        if b % 2 == 1:
            place(k, kick(0.8), g.at(b, 10))
        place(c, clap(rng), g.at(b, 8))
        for s in range(0, 16, 2):
            place(h, hat(rng, 1.0 if s % 4 == 0 else 0.6), g.at(b, s))
    return {"kick": k, "clap": c, "hats": h}


def bass(g, bars, rng):
    """One long 808 note per bar on the chord's root. The 808 IS the bass line."""
    notes = [(g.at(b), ROOTS[b % 4], g.n(1) - 200, None) for b in range(bars)]
    return {"808": b808(notes, g.n(bars), drive=1.3, decay=1.0)}


def lead(g, bars, rng):
    n = g.n(bars)
    x = silence(n)
    for b in range(0, bars, 2):
        for st, m, ln in MOTIF:
            place(x, saw_pluck(m, g.secs(ln) + 0.05), g.at(b, st))
    return {"lead": x}


# how loud each part sits, in dB, and where it sits left/right (-1..1)
MIX = {"kick": (-6, 0), "clap": (-5, 0), "hats": (-11, 0.15), "808": (-3, 0), "lead": (-5, 0)}


def mixdown(stems, mix=MIX):
    out = 0
    for name, x in stems.items():
        gain, pan = mix.get(name, (-12, 0))
        out = out + stereo(x, pan) * db(gain)
    return out


def render(seed=SEED, bars=BARS):
    rng = np.random.default_rng(seed)
    g = Grid(BPM)
    stems = {**drums(g, bars, rng), **bass(g, bars, rng), **lead(g, bars, rng)}
    return mixdown(stems), g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage01.wav")
    report(x, g, name="stage 01")
