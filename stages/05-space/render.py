"""Stage 05: space (delay, reverb, width, the filter snap).

Same notes as stage 04. Now each part gets a PLACE:
  answer  ping-pong delay (dotted 8th) so it bounces left/right
  stabs   reverb + extra width: big and behind
  lead    a little reverb, stays in the middle (the hook is the center)
  clap    a tiny room
  sub     forced MONO under 120 Hz (bass in the sides falls apart on phones and in clubs)
Plus two "free new" moves: the FILTER SNAP (bar 8 low-passed at 1.5 kHz, then fully open on
bar 9) and the WIDTH SNAP (stabs narrow in bars 1-8, wide in bars 9-16).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(4)
s01, s03 = load_stage(1), load_stage(3)
SEED, BPM, BARS, ROOTS = prev.SEED, prev.BPM, prev.BARS, prev.ROOTS
drums, bass, lead = prev.drums, prev.bass, prev.lead
MELODIC = ("lead", "answer", "stabs")


def ducked(stems, g, bars):
    """sidechain: everything melodic dips under each 808 hit (from stages 03/04)."""
    stems = dict(stems)
    d = duck(g.n(bars), s03.sidechain_hits(g, bars), depth=0.35)
    for k in MELODIC:
        if k in stems:
            stems[k] = stems[k] * (d[:, None] if stems[k].ndim == 2 else d)
    return stems


def space(stems, g, bars):
    s = dict(stems)
    s["answer"] = delay_pingpong(s["answer"], g, steps=6, fb=0.4, wet=0.55)
    s["stabs"] = reverb(s["stabs"], size=1.8, wet=0.35)
    s["lead"] = reverb(s["lead"], size=1.2, wet=0.12)
    s["clap"] = reverb(s["clap"], size=0.5, wet=0.12, seed=3)
    return s


def snaps(stems, g, bars):
    """filter snap on the last bar of every 8 + width snap on the stabs."""
    s = dict(stems)
    for k in MELODIC:
        x = stereo(s[k]).copy()
        for b in range(7, bars, 8):
            a, e = g.at(b), g.at(b + 1)
            x[a:e] = lp(x[a:e], 1500, 4)
        s[k] = x
    st = s["stabs"]
    for b in range(bars):
        a, e = g.at(b), g.at(b + 1)
        st[a:e] = width(st[a:e], 0.6 if (b // 8) % 2 == 0 else 1.5)
    return s


MIX = {**prev.MIX, "stabs": (-12, 0)}


def mixdown(stems, mix=MIX, g=None, bars=BARS):
    s = ducked(stems, g, bars)
    s = space(s, g, bars)
    s = snaps(s, g, bars)
    return mono_below(s01.mixdown(s, mix), 120)


def render(seed=SEED, bars=BARS):
    rng = np.random.default_rng(seed)
    g = Grid(BPM)
    stems = {**drums(g, bars, rng), **bass(g, bars, rng), **lead(g, bars, rng)}
    return mixdown(stems, g=g, bars=bars), g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage05.wav")
    report(x, g, name="stage 05")
