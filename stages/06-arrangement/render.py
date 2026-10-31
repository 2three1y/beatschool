"""Stage 06: arrangement (turning a loop into a song).

Everything from stage 05, laid out over 32 bars with a PLAN:
  intro   bars 1-8    hook only, low-passed (the "quiet sound"). Bars 7-8: perc pickup
                      (claps play the 808's bounce, no 808). Last 2 beats of bar 8: SILENCE.
  drop 1  bars 9-24   the 808 lands on bar 9. Two stages: 9-16 = 808 + clap + hats + lead + stabs,
                      17-24 = the hats double and the answer comes in.
  outro   bars 25-32  drums and 808 leave, the hook is exposed: low-passed, then snapped open
                      on bar 29, DEAD STOP on the last bar line. No fade.
Rule: never 16 bars untouched, change one thing at a time. Mutes happen on bar lines.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(5)
s01, s02 = load_stage(1), load_stage(2)
SEED, BPM, ROOTS = prev.SEED, prev.BPM, prev.ROOTS
BARS = 32
PLAN = [("intro", 0, 8), ("drop 1", 8, 24), ("outro", 24, 32)]


def section(b, plan=PLAN):
    for name, a, e in plan:
        if a <= b < e:
            return name, b - a
    return plan[-1][0], b - plan[-1][1]


def rule(stem, sec, i, b):
    """-> None (muted this bar) or (gain_db, lowpass_hz_or_None). This IS the arrangement."""
    if sec == "intro":
        if stem in ("lead", "stabs"):
            return (-2, 1700)
        if stem == "hats" and i >= 4:
            return (-6, None)
        if stem == "pickup" and i >= 6:
            return (0, None)
        return None
    if sec == "drop 1":
        if stem in ("pickup",):
            return None
        if stem in ("answer", "hats 16", "open hat") and i < 8:
            return None                      # stage 1 of the drop: hold these back
        return (0, None)
    if sec == "outro":
        if stem in ("lead", "stabs", "answer"):
            return (0, 1200) if i < 4 else (0, None)
        return None
    return (0, None)


def extra(g, bars, rng):
    """parts that only exist for the arrangement: 16th hats (the 'double') and the perc pickup."""
    n = g.n(bars)
    h16, pk = silence(n), silence(n)
    for b in range(bars):
        for s in range(1, 16, 2):
            if s not in (7, 9):
                place(h16, hat(rng, 0.35 * rng.uniform(0.8, 1.0)), g.at(b, s))
    for b in range(bars):                     # bounce claps, used only where the rules allow
        for bb, st in s02.BOUNCE:
            if b % 2 == bb:
                place(pk, clap(rng, 0.8), g.at(b, st))
    return {"hats 16": h16, "pickup": pk}


def stems_for(g, bars, seed):
    """one random generator PER PART: changing the drums can't reshuffle the melody."""
    r = lambda k: np.random.default_rng([seed, k])
    return {**prev.drums(g, bars, r(1)), **prev.bass(g, bars, r(2)), **prev.lead(g, bars, r(3)),
            **extra(g, bars, r(4))}


def arrange(stems, g, bars, plan=PLAN, rule=rule):
    """apply the rules bar by bar: mute, set level, low-pass. Gain changes get a 4 ms ramp (no clicks)."""
    out = {}
    ramp = int(0.004 * SR)
    for k, x in stems.items():
        x = stereo(x).copy()
        gain = np.ones(len(x))
        for b in range(bars):
            sec, i = section(b, plan)
            r = rule(k, sec, i, b)
            a, e = g.at(b), min(g.at(b + 1), len(x))
            if r is None:
                gain[a:e] = 0
                continue
            gdb, cut = r
            gain[a:e] = db(gdb)
            if cut:
                x[a:e] = lp(x[max(0, a - 4096):e], cut, 4)[-(e - a):]
        gain = np.convolve(gain, np.ones(ramp) / ramp, "same")
        out[k] = x * gain[:, None]
    return out


def silence_riser(x, g, bar, beats=2):
    """mute everything for the last `beats` beats before `bar`: silence is the riser."""
    a, e = g.at(bar, -4 * beats), g.at(bar)
    x[a:e] = 0
    return x


def dead_stop(x, g, bar):
    x = x[: g.at(bar)].copy()
    x[-64:] *= np.linspace(1, 0, 64)[:, None]   # 1.5 ms: a hard stop without a click
    return x


MIX = {**prev.MIX, "hats 16": (-12, -0.15), "pickup": (-8, 0)}


def mixdown(stems, mix=MIX, g=None, bars=BARS, plan=PLAN, rule=rule):
    s = prev.ducked(stems, g, bars)
    s["pickup"] = stereo(s["pickup"])
    s = prev.space(s, g, bars)
    s = arrange(s, g, bars, plan, rule)
    return mono_below(s01.mixdown(s, mix), 120)


def render(seed=SEED, bars=BARS):
    g = Grid(BPM)
    x = mixdown(stems_for(g, bars, seed), g=g, bars=bars)
    x = silence_riser(x, g, 8)
    return dead_stop(x, g, bars), g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage06.wav")
    report(x, g, sections=[(n, a, e) for n, a, e in PLAN], name="stage 06")
