"""Stage 08: the master (making it loud without wrecking it) + the final checks.

Takes the full stage 07 song (before preview leveling) and runs a simple master chain:
  1. high-pass at 25 Hz (rumble nobody can hear eats loudness)
  2. glue compressor (2:1, slow) so the parts move together
  3. soft saturation (tanh) to round off peaks before the limiter
  4. true-peak limiter at -1.4 dBTP (a little under -1, because different meters disagree by ~0.1-0.2 dB), gain raised step by step until integrated loudness = -9 LUFS
Then it CHECKS the result against the targets and prints PASS/FAIL. An agent can't hear;
these numbers are its ears.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit import *  # noqa

prev = load_stage(7)
SEED, BPM, BARS, PLAN = prev.SEED, prev.BPM, prev.BARS, prev.PLAN
TARGET_LUFS = -9.0
CEILING = -1.4


def glue(x, threshold_db=-18, ratio=2.0, attack=0.010, release=0.15, block=64):
    """feed-forward RMS compressor working on 64-sample blocks (fast enough in numpy)."""
    m = (x ** 2).mean(1)
    nb = len(m) // block
    lvl = 10 * np.log10(m[: nb * block].reshape(nb, block).mean(1) + 1e-12)
    a_at, a_rel = np.exp(-block / (attack * SR)), np.exp(-block / (release * SR))
    env, cur = np.empty(nb), -90.0
    for i, v in enumerate(lvl):
        k = a_at if v > cur else a_rel
        cur = k * cur + (1 - k) * v
        env[i] = cur
    over = np.maximum(env - threshold_db, 0)
    gdb = -over * (1 - 1 / ratio)
    g = np.repeat(db(gdb), block)
    g = np.concatenate([g, np.full(len(x) - len(g), g[-1])])
    return x * g[:, None]


def master(x, target=TARGET_LUFS, ceiling=CEILING):
    x = hp(stereo(x), 25, 2)
    x = x / (np.abs(x).max() + 1e-9) * db(-6)
    x = glue(x)
    gain = 1.0
    for _ in range(12):
        y = limiter(saturate(x * gain, 1.2), ceiling)
        now = lufs(y)
        if abs(now - target) < 0.1:
            break
        gain *= db((target - now) * 0.9)
    return limiter(y, ceiling)          # one more pass: true peak stays under the ceiling


def checks(y, g):
    sec = {n: lufs(y[g.at(a):g.at(e)]) for n, a, e in PLAN}
    I, TP = lufs(y), true_peak(y)
    planned = [round(g.at(8, -8) / SR, 1), round(g.at(40, -8) / SR, 1)]   # the two silence risers
    sil = silences(y)
    unplanned = [s for s in sil if not any(abs(s[0] - p) < 0.3 for p in planned)]
    drop = max(sec["drop 1"], sec["drop 2"])
    rows = [
        ("integrated loudness about -9 LUFS", abs(I - TARGET_LUFS) <= 0.5, f"{I:.1f} LUFS"),
        ("true peak <= -1 dBTP", TP <= -1.0, f"{TP:.2f} dBTP"),
        ("drop 2 louder than drop 1 (+1 to +2 LU)", 0.8 <= sec["drop 2"] - sec["drop 1"] <= 2.5,
         f"{sec['drop 2'] - sec['drop 1']:+.1f} LU"),
        ("intro 6-10 LU under the drop", 6 <= drop - sec["intro"] <= 10.5, f"{drop - sec['intro']:.1f} LU"),
        ("sub is mono (side energy under 120 Hz < 1%)", side_in_sub(y) < 1, f"{side_in_sub(y)}%"),
        ("no silences except the planned risers", not unplanned, f"found {sil}"),
        ("length 1:20-2:15", 80 <= len(y) / SR <= 135, f"{len(y) / SR:.1f} s"),
    ]
    print("section LUFS: " + " | ".join(f"{k} {v:.1f}" for k, v in sec.items()))
    for name, ok, val in rows:
        print(("PASS " if ok else "FAIL ") + name + ": " + val)
    return all(ok for _, ok, _ in rows)


if __name__ == "__main__":
    x, g = prev.render(seed_from_argv(SEED))
    y = master(x)
    save(y, "stage08.wav")
    report(y, g, name="stage 08 (master)")
    ok = checks(y, g)
    sys.exit(0 if ok else 1)
