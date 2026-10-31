"""Stage 07: the switch-up, drop 2 and transition FX (the full song, 64 bars, about 1:46).

  intro    1-8    (stage 06)
  drop 1   9-24   (stage 06)                         -> TAPE STOP on the last 2 beats of bar 24
  switch   25-40  NEW drums (jersey bounce kick, clap on 2 and 4), NEW 808 pattern on NEW roots,
                  NEW melodic idea: a GRAIN CLOUD (lesson 7) made from our own lead, wrecked and
                  granulated. Bars 33-40 add a harp arp + hats.  -> riser, STUTTER, 2 beats of
                  silence, IMPACT on bar 41
  drop 2   41-56  drop 1 but bigger: lead doubled an octave up, dirtier 808 with more pops,
                  wider stabs, hats doubled the whole time, the cloud stays as a new layer.
                  Measured, then ridden to +2.6 LU over drop 1 before the master (about +1.5 after it).  -> reverse swell into bar 57
  outro    57-64  the hook alone, low-passed, snapped open on bar 61, dead stop.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(6)
s01, s03, s04 = load_stage(1), load_stage(3), load_stage(4)
SEED, BPM = prev.SEED, prev.BPM
BARS = 64
PLAN = [("intro", 0, 8), ("drop 1", 8, 24), ("switch", 24, 40), ("drop 2", 40, 56), ("outro", 56, 64)]
SWITCH_ROOTS = [30, 33, 28, 32]        # F#1, A1, E1, G#1: new roots = the switch feels like a new room
SWITCH_CHORDS = {30: [57, 61, 66], 33: [57, 61, 64], 28: [56, 59, 64], 32: [56, 59, 63]}
SWITCH = ("kick jersey", "clap jersey", "808 switch", "cloud", "harp")
DROP2 = ("lead up", "808 dirty")


def rule(stem, sec, i, b):
    if stem == "fx":
        return (0, None)
    if sec in ("intro", "drop 1", "outro"):
        if stem in SWITCH + DROP2:
            return None
        return prev.rule(stem, sec, i, b)
    if sec == "switch":
        if stem in ("harp", "hats", "hats 16") and i < 8:
            return None
        if stem in SWITCH or stem in ("hats", "hats 16"):
            return (0, None)
        return None
    if sec == "drop 2":
        if stem in SWITCH[:3] or stem in ("808", "pickup"):
            return None                       # the dirty 808 replaces the clean one
        if stem == "cloud":
            return (-7, None) if i >= 8 else None
        if stem == "harp":
            return None
        return (0, None)
    return (0, None)


def switch_parts(g, bars, rng):
    n = g.n(bars)
    a0 = 24
    kj, cj = silence(n), silence(n)
    for b in range(a0, a0 + 16):
        for s in ((0, 6, 10, 12, 14) if b % 2 == 0 else (0, 4, 7, 10, 13)):
            place(kj, kick(0.95 if s == 0 else 0.75, dur=0.22), g.at(b, s))
        for s in (4, 12):
            place(cj, clap(rng, 1.0), g.at(b, s))
    # new 808 pattern: two long notes per bar, the second slides into the next bar
    notes = []
    for b in range(a0, a0 + 16):
        r, nxt = SWITCH_ROOTS[b % 4], SWITCH_ROOTS[(b + 1) % 4]
        notes.append((g.at(b, 0), r, g.at(b, 10) - g.at(b, 0) - 64, None))
        notes.append((g.at(b, 10), r + (12 if b % 4 == 3 else 0), g.at(b + 1) - g.at(b, 10) - 64, nxt))
    b8 = b808(notes, n, drive=3.0, decay=1.4, glide=0.06)
    # the cloud: write a SIMPLE line, wreck it, grain it, gate it (lesson 7)
    ev = []
    line = [73, 76, 80, 78, 76, 73, 71, 73]
    for b in range(a0, 56):
        for k, s in enumerate((0, 3, 6, 10)):
            ev.append((g.at(b, s), line[(b * 4 + k) % len(line)] + (12 if b % 8 == 7 else 0), int(g.secs(3) * SR)))
    raw = saturate(glide_line(ev, n, port=0.03, wave="square", cutoff=7000), 4.0)
    for b in range(a0, 56, 2):
        raw = stutter(raw, g.at(b, 12), g.at(b, 16) - g.at(b, 12), int(g.secs(0.5) * SR))
    cloud = granulate(raw, n, rng, octave_prob=0.3)
    cloud = bp(cloud, 300, 7000) * gate16(n, g, [1, .3, .8, .25, 1, .3, .9, .2, 1, .25, .7, .3, 1, .5, .8, .4])[:, None]
    cloud[: g.at(a0)] = 0
    # harp arp (Karplus-Strong) on the switch chords, 16ths, bars 33-40
    hp_ = silence(n)
    for b in range(a0 + 8, a0 + 16):
        ch = SWITCH_CHORDS[SWITCH_ROOTS[b % 4]]
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24]
        for s in range(16):
            place(hp_, ks_pluck(arp[(s * 3) % 4], 0.35, rng, 0.5), g.at(b, s))
    return {"kick jersey": kj, "clap jersey": cj, "808 switch": b8, "cloud": cloud, "harp": hp_}


def drop2_parts(g, bars, seed):
    r3 = np.random.default_rng([seed, 3])        # SAME seed as the lead -> same notes, octave up
    up = s04.lead(g, bars, r3, transpose=12)["lead"]
    notes = s03.bass_notes(g, bars)
    notes = [(a, m + 12 if (i % 7 == 3) else m, ln, sl if sl else (m if i % 7 == 3 else None))
             for i, (a, m, ln, sl) in enumerate(notes)]        # more octave pops
    return {"lead up": up, "808 dirty": b808(notes, g.n(bars), drive=4.5, decay=1.6, glide=0.075)}


def fx(g, bars, rng):
    n = g.n(bars)
    f = silence(n, 2)
    place(f, stereo(riser(g.secs(16 * 4) - g.secs(8), rng)) * 0.5, g.at(36))      # bars 37-40
    place(f, stereo(impact(rng)), g.at(40))
    place(f, stereo(reverse_swell(g.secs(16), rng)) * 0.6, g.at(55))               # into bar 57
    place(f, stereo(impact(rng)) * 0.5, g.at(8))
    return {"fx": f}


MIX = {**prev.MIX, "kick jersey": (-7, 0), "clap jersey": (-6, 0), "808 switch": (-7, 0),
       "cloud": (-11, 0), "harp": (-12, -0.2), "lead up": (-15, 0), "808 dirty": (-7, 0), "fx": (-10, 0)}


def space2(s, g, bars):
    s = dict(s)
    s["cloud"] = reverb(delay_pingpong(s["cloud"], g, steps=3, fb=0.3, wet=0.3), size=1.4, wet=0.2)
    s["harp"] = reverb(s["harp"], size=1.6, wet=0.3)
    s["lead up"] = reverb(s["lead up"], size=1.6, wet=0.25)
    s["clap jersey"] = reverb(s["clap jersey"], size=0.5, wet=0.12, seed=3)
    return s


def render(seed=SEED, bars=BARS, raw=False):
    g = Grid(BPM)
    rng = np.random.default_rng([seed, 9])
    st = {**prev.stems_for(g, bars, seed), **switch_parts(g, bars, rng), **drop2_parts(g, bars, seed),
          **fx(g, bars, rng)}
    st = prev.prev.ducked(st, g, bars)
    st["pickup"] = stereo(st["pickup"])
    st = space2(prev.prev.space(st, g, bars), g, bars)
    # drop 2 is WIDER
    a, e = g.at(40), g.at(56)
    st["stabs"][a:e] = width(st["stabs"][a:e], 1.6)
    st = prev.arrange(st, g, bars, PLAN, rule)
    x = mono_below(s01.mixdown(st, MIX), 120)
    # transitions on the full mix
    x = tape_stop(x, g.at(23, 8), g.at(24) - g.at(23, 8))                 # end of drop 1
    x = stutter(x, g.at(39, 0), g.at(39, 8) - g.at(39, 0), int(g.secs(1) * SR))  # bar 40, beats 1-2
    x = prev.silence_riser(x, g, 8)
    x[g.at(39, 8):g.at(40)] = 0                                            # silence before drop 2
    # measure, don't guess: push drop 2 to sit +2.6 LU over drop 1 (the master squeezes about 1 LU of that back)
    d1, d2 = lufs(x[g.at(8):g.at(24)]), lufs(x[a:e])
    boost = max(0.0, 2.6 - (d2 - d1))
    x[a:e] *= db(boost)
    print(f"drop 1 {d1:.1f} LUFS, drop 2 {d2:.1f} LUFS before ride, +{boost:.1f} dB on drop 2")
    x = prev.dead_stop(x, g, bars)
    return x, g


if __name__ == "__main__":
    x, g = render(seed_from_argv(SEED))
    x = preview_level(x)
    save(x, "stage07.wav")
    report(x, g, sections=PLAN, name="stage 07")
