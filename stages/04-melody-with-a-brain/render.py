"""Stage 04: a melody with a brain.

Drums + 808 from stage 03. The plain lead is replaced by THREE melodic parts:
  lead     a mono glide lead (25 ms slides) built from ANCHOR notes (locked) + FREE notes
           (seeded random, re-rolled every 4 bars), with the C#-D half-step rub on an anchor.
  answer   a bitcrushed square, an octave up, that ONLY plays in the lead's gaps (call and response).
  stabs    7-voice detuned saw chord stabs on a syncopated 8th grid, quiet, for size.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(3)
SEED, BPM, BARS, ROOTS = prev.SEED, prev.BPM, prev.BARS, prev.ROOTS
drums, bass = prev.drums, prev.bass

PALETTE = [68, 71, 73, 74, 76, 78, 80]         # C# minor around C#5, plus D (74) for the rub
ANCHORS = {0: 73, 6: 74, 16: 71, 22: 73}       # 2-bar slots that never change (the hook's spine)
SLOTS = [0, 3, 6, 8, 11, 14, 16, 19, 22, 24, 27, 30]
CHORDS = {25: [61, 64, 68], 33: [57, 61, 64], 30: [57, 61, 66], 32: [59, 63, 68]}   # C#m, A, F#m, G#m


def phrase(rng):
    """one 2-bar phrase: anchors fixed, free slots get a seeded note or a rest."""
    out = []
    for s in SLOTS:
        if s in ANCHORS:
            out.append((s, ANCHORS[s]))
        elif rng.random() < 0.65:
            out.append((s, int(rng.choice(PALETTE))))
    return out


def lead_events(g, bars, rng, transpose=0):
    ev, rests = [], []
    for b0 in range(0, bars, 2):
        if b0 % 4 == 0:
            ph = phrase(np.random.default_rng(rng.integers(1 << 30)))   # new free notes every 4 bars
        for i, (s, m) in enumerate(ph):
            nxt = ph[i + 1][0] if i + 1 < len(ph) else 32
            ln = max(nxt - s, 1)
            if ln >= 3 and s not in ANCHORS:    # leave a gap for the answer
                rests.append((b0, s + 2, ln - 2))
                ln = 2
            ev.append((g.at(b0, s), m + transpose, int(g.secs(ln) * SR) - 300))
    return ev, rests


def lead(g, bars, rng, transpose=0):
    ev, rests = lead_events(g, bars, rng, transpose)
    n = g.n(bars)
    ld = glide_line(ev, n, port=0.025, cutoff=4500)
    ans = silence(n)
    for b0, s, ln in rests:                   # the answer: only inside the lead's gaps
        m = int(rng.choice([85, 88, 90, 92])) + transpose
        for k in range(min(ln, 2)):
            place(ans, square_pluck(m - 12 * k, g.secs(1)), g.at(b0, s + k))
    ans = bitcrush(ans, bits=5, down=3)
    st = silence(n, 2)
    for b in range(bars):
        for s in (0, 3, 6, 10, 12):
            for m in CHORDS[ROOTS[b % 4]]:
                place(st, supersaw(m + transpose, g.secs(1.5), rng, cutoff=3800, d=0.1, s=0.2), g.at(b, s))
    return {"lead": ld, "answer": ans, "stabs": st}


MIX = {**prev.MIX, "lead": (-9, 0), "answer": (-10, 0.35), "stabs": (-13, 0)}


def mixdown(stems, mix=MIX, g=None, bars=BARS):
    if g is not None:
        stems = dict(stems)
        d = duck(g.n(bars), prev.sidechain_hits(g, bars), depth=0.35)
        for k in ("answer", "stabs"):
            stems[k] = stems[k] * (d[:, None] if stems[k].ndim == 2 else d)
    return prev.mixdown(stems, mix, g, bars)


def render(seed=SEED, bars=BARS):
    rng = np.random.default_rng(seed)
    g = Grid(BPM)
    stems = {**drums(g, bars, rng), **bass(g, bars, rng), **lead(g, bars, rng)}
    return mixdown(stems, g=g, bars=bars), g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage04.wav")
    report(x, g, name="stage 04")
