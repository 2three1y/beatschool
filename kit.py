"""kit.py: the whole toolbox for beatschool. numpy + scipy + soundfile, nothing else.

Every stage imports this file. Read it top to bottom once: it's the instruments,
the effects, the mixer and the measuring tape. Nothing in here samples anyone else's
audio. Every sound is made from math (sine waves, noise, filters).
"""
import importlib.util
import os
import sys

import numpy as np
from scipy.signal import butter, sosfilt, oaconvolve, resample_poly, lfilter

SR = 44100
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")


# ---------------------------------------------------------------- the grid
class Grid:
    """Turns musical time (bars, 16th-note steps) into sample positions.

    At 145 BPM one beat is 60/145 = 0.414 s, a 16th "step" is a quarter of that,
    and a bar is 16 steps. Everything in a beat lives on this grid."""

    def __init__(self, bpm):
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.step = self.beat / 4
        self.bar = self.beat * 4

    def at(self, bar, step=0.0):
        """sample index of (bar, step)"""
        return int(round((bar * 16 + step) * self.step * SR))

    def n(self, bars):
        """number of samples in `bars` bars"""
        return self.at(bars)

    def secs(self, steps):
        return steps * self.step


def mtof(m):
    """MIDI note number -> Hz. 69 = A4 = 440 Hz. C#1 = 25 = 34.6 Hz."""
    return 440.0 * 2 ** ((np.asarray(m, dtype=float) - 69) / 12)


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def scale(root, kind="minor", lo=0, hi=127):
    """All notes of a scale between lo and hi (MIDI)."""
    steps = {"minor": [0, 2, 3, 5, 7, 8, 10], "major": [0, 2, 4, 5, 7, 9, 11],
             "minor_pent": [0, 3, 5, 7, 10], "phrygian": [0, 1, 3, 5, 7, 8, 10]}[kind]
    return [n for n in range(lo, hi + 1) if (n - root) % 12 in steps]


# ---------------------------------------------------------------- filters
def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2 - 100), "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR / 2 - 100)], "band", fs=SR, output="sos"), x, axis=0)


def sweep_lp(x, f0, f1, chunk=1024):
    """Low-pass whose cutoff glides from f0 to f1 (Hz) across x. Exponential glide."""
    y = np.zeros_like(x)
    n = len(x)
    for a in range(0, n, chunk):
        f = f0 * (f1 / f0) ** (a / max(n - 1, 1))
        y[a:a + chunk] = lp(x[max(0, a - 2048):a + chunk], f)[-(min(a + chunk, n) - a):]
    return y


# ---------------------------------------------------------------- envelopes
def env_exp(n, decay_s):
    t = np.arange(n) / SR
    return np.exp(-t / decay_s)


def adsr(n, a=0.005, d=0.1, s=0.7, r=0.05):
    """attack/decay/sustain/release envelope, n samples long (release at the end)."""
    a_, d_, r_ = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=float)
    a_ = min(a_, n)
    e[:a_] = np.linspace(0, 1, a_, endpoint=False)
    dd = min(d_, max(n - a_, 0))
    e[a_:a_ + dd] = np.linspace(1, s, dd, endpoint=False)
    rr = min(r_, n)
    if rr:
        e[n - rr:] *= np.linspace(1, 0, rr)
    return e


# ---------------------------------------------------------------- oscillators
def phase_from_freq(freq):
    """freq can change every sample (that's how glides work): integrate it into phase."""
    return 2 * np.pi * np.cumsum(freq) / SR


def osc_saw(freq, phase0=0.0):
    ph = (np.cumsum(freq) / SR + phase0) % 1.0
    return 2 * ph - 1


def osc_square(freq, pw=0.5, phase0=0.0):
    ph = (np.cumsum(freq) / SR + phase0) % 1.0
    return np.where(ph < pw, 1.0, -1.0)


def noise(n, rng):
    return rng.uniform(-1, 1, n)


# ---------------------------------------------------------------- drums
def kick(vel=1.0, dur=0.32):
    """sine that falls fast from 160 Hz to 48 Hz + a tiny click."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 48 + 112 * np.exp(-t / 0.03)
    x = np.sin(phase_from_freq(f)) * env_exp(n, 0.11)
    x[:80] += np.linspace(0.6, 0, 80)  # click
    return np.tanh(1.6 * x) * vel


def clap(rng, vel=1.0, thin=True):
    """3 quick noise bursts (hands not landing at once) + a short tail."""
    n = int(0.22 * SR)
    x = np.zeros(n)
    for i, off in enumerate((0, 0.009, 0.019)):
        a = int(off * SR)
        m = n - a
        x[a:] += noise(m, rng) * env_exp(m, 0.006 if i < 2 else 0.07)
    x = bp(x, 1100 if thin else 700, 6500)
    return x / (np.abs(x).max() + 1e-9) * vel


def hat(rng, vel=1.0, open_=False, tone=1.0):
    n = int((0.22 if open_ else 0.06) * SR)
    x = hp(noise(n, rng), 7000 * tone, 2) * env_exp(n, 0.07 if open_ else 0.013)
    return x / (np.abs(x).max() + 1e-9) * vel


def snare(rng, vel=1.0):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 190 * t) * env_exp(n, 0.04)
    x = 0.6 * body + bp(noise(n, rng), 1500, 9000) * env_exp(n, 0.05)
    return x / (np.abs(x).max() + 1e-9) * vel


# ---------------------------------------------------------------- 808
def b808(notes, total, drive=1.0, decay=1.2, glide=0.07):
    """A whole 808 line in one go.

    notes: list of (start_sample, midi, length_samples, slide_to_midi_or_None).
    One continuous phase across notes so slides are smooth (no clicks).
    drive > 1 = tanh saturation: adds harmonics (100-400 Hz) so the 808 is heard
    on phone speakers that can't play 35 Hz."""
    freq = np.zeros(total)
    amp = np.zeros(total)
    notes = sorted(notes)
    for i, (a, m, ln, slide) in enumerate(notes):
        b = min(a + ln, total)
        if b <= a:
            continue
        k = b - a
        f = np.full(k, mtof(m))
        # the punch: start a little sharp and fall into the note in ~25 ms
        f *= 1 + 0.35 * np.exp(-np.arange(k) / (0.008 * SR))
        if slide is not None:
            g = int(glide * SR)
            s = max(k - g, 0)
            ramp = np.linspace(0, 1, k - s)
            f[s:] = mtof(m) * (mtof(slide) / mtof(m)) ** ramp
        freq[a:b] = f
        e = env_exp(k, decay)
        e[:64] *= np.linspace(0, 1, 64)
        e[-200:] *= np.linspace(1, 0, min(200, k))[-len(e[-200:]):]
        amp[a:b] = e
    freq[freq == 0] = 40.0
    x = np.sin(phase_from_freq(freq)) * amp
    if drive > 1:
        x = np.tanh(drive * x) / np.tanh(drive)
    return lp(x, 3500)


# ---------------------------------------------------------------- melodic synths
def saw_pluck(m, dur, vel=1.0, cutoff=3000):
    n = int(dur * SR)
    x = 0.5 * (osc_saw(np.full(n, mtof(m))) + osc_saw(np.full(n, mtof(m) * 1.006), 0.3))
    x = lp(x * adsr(n, 0.003, 0.18, 0.25, 0.04), cutoff)
    return x * vel


def supersaw(m, dur, rng, voices=7, detune=0.18, vel=1.0, cutoff=5000, a=0.004, d=0.15, s=0.5, r=0.08):
    """7 detuned saws spread across the stereo field = the big "stacked" sound. Returns stereo."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for v in range(voices):
        cents = (v - (voices - 1) / 2) / ((voices - 1) / 2) * detune * 100
        f = mtof(m) * 2 ** (cents / 1200)
        x = osc_saw(np.full(n, f), rng.random())
        p = (v - (voices - 1) / 2) / ((voices - 1) / 2)
        out[:, 0] += x * np.sqrt((1 - p) / 2)
        out[:, 1] += x * np.sqrt((1 + p) / 2)
    out = lp(out, cutoff) * adsr(n, a, d, s, r)[:, None]
    return out / voices * 2 * vel


def square_pluck(m, dur, vel=1.0, pw=0.3, cutoff=4000):
    n = int(dur * SR)
    x = osc_square(np.full(n, mtof(m)), pw) * adsr(n, 0.002, 0.09, 0.15, 0.03)
    return lp(x, cutoff) * vel * 0.5


def glide_line(events, total, port=0.025, wave="sawsq", cutoff=4200):
    """A mono lead that SLIDES between notes (portamento, ~25 ms like the tutorials say).

    events: list of (start_sample, midi, length_samples). The pitch never jumps:
    it bends to each new note over `port` seconds. Gaps are silent."""
    events = sorted(events)
    freq = np.full(total, mtof(events[0][1]) if events else 440.0)
    gate = np.zeros(total)
    cur = freq[0]
    p = int(port * SR)
    for a, m, ln in events:
        b = min(a + ln, total)
        tgt = mtof(m)
        k = b - a
        if k <= 0:
            continue
        g = min(p, k)
        freq[a:a + g] = cur * (tgt / cur) ** np.linspace(0, 1, g)
        freq[a + g:b] = tgt
        if b < total:
            freq[b:] = tgt
        cur = tgt
        e = adsr(k, 0.004, 0.12, 0.6, 0.03)
        gate[a:b] = np.maximum(gate[a:b], e)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * np.arange(total) / SR)
    f = freq * vib
    if wave == "square":
        x = osc_square(f, 0.5)
    elif wave == "saw":
        x = osc_saw(f)
    else:
        x = 0.6 * osc_saw(f) + 0.4 * osc_square(f * 1.003, 0.4)
    return lp(x, cutoff) * gate


def ks_pluck(m, dur, rng, vel=1.0, bright=0.6, decay=0.996):
    """Karplus-Strong: a burst of noise in a tiny feedback loop = a plucked string / harp."""
    n = int(dur * SR)
    period = max(int(SR / mtof(m)), 2)
    buf = rng.uniform(-1, 1, period)
    buf = lp(buf, 1000 + 9000 * bright, 1)
    out = np.zeros(n)
    for a in range(0, n, period):            # one whole trip around the loop at a time
        k = min(period, n - a)
        out[a:a + k] = buf[:k]
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
    return out * vel * adsr(n, 0.001, 0.05, 1.0, 0.02)


def bitcrush(x, bits=6, down=4):
    """old video game color: fewer volume steps + sample-and-hold downsampling."""
    q = 2 ** (bits - 1)
    y = np.round(x * q) / q
    idx = (np.arange(len(y)) // down) * down
    return y[idx]


def granulate(src, n_out, rng, grain=(0.03, 0.09), hop=0.012, jitter=0.12, octave_prob=0.25, spread=0.8):
    """Grain cloud (lesson 7): many tiny overlapping slices of `src`, read near the playhead
    with random jitter, random pan, and sometimes an octave up/down. Returns stereo, n_out long.
    The notes of the source survive; the way they are played never repeats exactly."""
    out = np.zeros((n_out, 2))
    h = int(hop * SR)
    for t in range(0, n_out, h):
        ln = int(rng.uniform(*grain) * SR)
        ratio = 1.0
        if rng.random() < octave_prob:
            ratio = 2.0 if rng.random() < 0.6 else 0.5
        c = int(np.clip(t + rng.uniform(-jitter, jitter) * SR, 0, len(src) - ln * ratio - 2))
        span = src[c:c + int(ln * ratio) + 2]
        piece = np.interp(np.arange(ln) * ratio, np.arange(len(span)), span) * np.hanning(ln)
        p = rng.uniform(-spread, spread)
        k = min(ln, n_out - t)
        out[t:t + k, 0] += piece[:k] * np.sqrt((1 - p) / 2)
        out[t:t + k, 1] += piece[:k] * np.sqrt((1 + p) / 2)
    return out / (np.abs(out).max() + 1e-9)


def gate16(n, g, pattern, start_bar=0):
    """a volume shape on the 16th grid (what a 'shaper' plugin does): pattern = 16 levels 0..1."""
    e = np.zeros(n)
    b = start_bar
    while g.at(b) < n:
        for s in range(16):
            a, z = g.at(b, s), min(g.at(b, s + 1), n)
            if a >= n:
                break
            k = z - a
            e[a:z] = pattern[s] * np.minimum(1, np.linspace(1.6, 0.35, k))
        b += 1
    ramp = int(0.003 * SR)
    return np.convolve(e, np.ones(ramp) / ramp, "same")


# ---------------------------------------------------------------- mixing helpers
def silence(n, ch=1):
    return np.zeros((n, 2)) if ch == 2 else np.zeros(n)


def place(dst, x, at, gain=1.0):
    """add sound x into buffer dst starting at sample `at` (clips at the end)."""
    if at < 0:
        x, at = x[-at:], 0
    if at >= len(dst):
        return
    k = min(len(x), len(dst) - at)
    dst[at:at + k] += x[:k] * gain


def stereo(x, pan=0.0):
    """mono -> stereo with equal-power pan (-1 left .. +1 right)."""
    if x.ndim == 2:
        return x
    return np.stack([x * np.sqrt((1 - pan) / 2), x * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)


def db(x):
    return 10 ** (x / 20)


def saturate(x, drive=1.5):
    return np.tanh(drive * x) / np.tanh(drive)


def duck(n, hits, depth=0.4, release=0.12):
    """Sidechain envelope: dips by `depth` at every hit sample, recovers over `release` s."""
    g = np.ones(n)
    r = int(release * 5 * SR)
    curve = 1 - depth * np.exp(-np.arange(r) / (release * SR))
    curve[:120] = np.linspace(1, curve[120], 120)  # 3 ms, no click
    for h in hits:
        k = min(r, n - h)
        if k > 0:
            g[h:h + k] = np.minimum(g[h:h + k], curve[:k])
    return g


# ---------------------------------------------------------------- space
def delay_pingpong(x, g, steps=6, fb=0.32, wet=0.3, taps=6, tone=3500):
    """Echoes bouncing left/right every `steps` 16ths (6 = dotted 1/8, 12 = dotted 1/4)."""
    x = stereo(x)
    d = int(g.secs(steps) * SR)
    y = x.copy()
    mono = lp(x.mean(1), tone)
    for k in range(1, taps + 1):
        side = 0 if k % 2 else 1
        a = d * k
        if a >= len(x):
            break
        y[a:, side] += mono[:len(x) - a] * wet * fb ** (k - 1)
    return y


_IR_CACHE = {}


def reverb(x, size=1.6, wet=0.22, seed=7, tone=6000, predelay=0.012):
    """Convolution with a made-up room: decaying stereo noise (no recorded rooms used)."""
    key = (size, seed, tone)
    if key not in _IR_CACHE:
        rng = np.random.default_rng(seed)
        n = int(size * SR)
        ir = rng.standard_normal((n, 2)) * env_exp(n, size / 6.9)[:, None]
        ir = lp(ir, tone)
        ir[: int(predelay * SR)] = 0
        _IR_CACHE[key] = ir / np.sqrt((ir ** 2).sum(0))
    ir = _IR_CACHE[key]
    x = stereo(x)
    w = np.stack([oaconvolve(x[:, c], ir[:, c])[: len(x)] for c in (0, 1)], 1)
    return x + wet * w


def width(x, amount=1.0):
    """mid/side: amount 0 = mono, 1 = as is, 1.5 = wider."""
    x = stereo(x)
    m = (x[:, 0] + x[:, 1]) / 2
    s = (x[:, 0] - x[:, 1]) / 2 * amount
    return np.stack([m + s, m - s], 1)


def mono_below(x, f=120):
    """Keep everything under f Hz in the middle (sub bass must be mono)."""
    m = (x[:, 0] + x[:, 1]) / 2
    s = (x[:, 0] - x[:, 1]) / 2
    s = hp(s, f, 4)
    return np.stack([m + s, m - s], 1)


# ---------------------------------------------------------------- transition FX
def riser(dur, rng, f0=300, f1=9000):
    n = int(dur * SR)
    x = noise(n, rng)
    y = np.zeros(n)
    ch = 2048
    for a in range(0, n, ch):
        fc = f0 * (f1 / f0) ** (a / n)
        y[a:a + ch] = bp(x[max(0, a - 4096):a + ch], fc * 0.7, fc * 1.3)[-(min(a + ch, n) - a):]
    return y * np.linspace(0, 1, n) ** 2


def reverse_swell(dur, rng):
    """a reversed cymbal-ish noise wash: swells INTO the downbeat."""
    n = int(dur * SR)
    x = hp(noise(n, rng), 3000) * env_exp(n, dur / 4)
    return x[::-1]


def impact(rng):
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    boom = np.sin(phase_from_freq(38 + 60 * np.exp(-t / 0.05))) * env_exp(n, 0.45)
    hiss = lp(noise(n, rng), 5000) * env_exp(n, 0.25) * 0.4
    return np.tanh(1.5 * (boom + hiss))


def tape_stop(x, start, length):
    """slow the audio from x[start] to a halt over `length` samples, like pulling the plug on a turntable."""
    seg = x[start:start + length].copy()
    n = len(seg)
    rate = np.linspace(1, 0, n) ** 1.3
    pos = np.cumsum(rate)
    pos = np.clip(pos, 0, n - 1)
    out = np.stack([np.interp(pos, np.arange(n), seg[:, c]) for c in (0, 1)], 1) if seg.ndim == 2 \
        else np.interp(pos, np.arange(n), seg)
    fade = np.linspace(1, 0, n) ** 0.5
    x[start:start + n] = out * (fade[:, None] if seg.ndim == 2 else fade)
    return x


def stutter(x, start, length, slice_len):
    """repeat the first `slice_len` samples of the region over and over (the glitch roll)."""
    piece = x[start:start + slice_len].copy()
    k = 0
    while k < length:
        m = min(slice_len, length - k)
        x[start + k:start + k + m] = piece[:m]
        k += m
    return x


# ---------------------------------------------------------------- measuring (we can't hear, so we measure)
def _biquad(fc, Q, G, kind):
    A = 10 ** (G / 40)
    w0 = 2 * np.pi * fc / SR
    alpha = np.sin(w0) / (2 * Q)
    c = np.cos(w0)
    if kind == "shelf":
        b = [A * ((A + 1) + (A - 1) * c + 2 * np.sqrt(A) * alpha), -2 * A * ((A - 1) + (A + 1) * c),
             A * ((A + 1) + (A - 1) * c - 2 * np.sqrt(A) * alpha)]
        a = [(A + 1) - (A - 1) * c + 2 * np.sqrt(A) * alpha, 2 * ((A - 1) - (A + 1) * c),
             (A + 1) - (A - 1) * c - 2 * np.sqrt(A) * alpha]
    else:
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
        a = [1 + alpha, -2 * c, 1 - alpha]
    return np.array(b) / a[0], np.array(a) / a[0]


def lufs(x):
    """Integrated loudness, ITU-R BS.1770-4 (K-weighting, 400 ms blocks, -70 / -10 gates).
    Matches ffmpeg's ebur128 filter to about 0.1 LU."""
    x = stereo(np.asarray(x, dtype=float))
    b1, a1 = _biquad(1681.974450955533, 0.7071752369554196, 3.999843853973347, "shelf")
    b2, a2 = _biquad(38.13547087602444, 0.5003270373238773, 0.0, "hp")
    y = lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    if len(y) < blk:
        return -70.0
    ms = np.array([(y[i:i + blk] ** 2).mean(0).sum() for i in range(0, len(y) - blk + 1, hop)])
    ld = -0.691 + 10 * np.log10(ms + 1e-12)
    ms = ms[ld > -70]
    if not len(ms):
        return -70.0
    rel = -0.691 + 10 * np.log10(ms.mean()) - 10
    ms = ms[(-0.691 + 10 * np.log10(ms)) > rel]
    return float(-0.691 + 10 * np.log10(ms.mean()))


def true_peak(x):
    """dBTP: peak after 4x oversampling (catches the peaks BETWEEN samples)."""
    up = resample_poly(stereo(np.asarray(x, dtype=float)), 4, 1, axis=0)
    return float(20 * np.log10(np.abs(up).max() + 1e-12))


def silences(x, thresh_db=-35, min_len=0.4):
    """stretches quieter than thresh_db (dBFS, 50 ms windows) lasting > min_len seconds."""
    m = stereo(x).mean(1)
    w = int(0.05 * SR)
    k = len(m) // w
    r = 20 * np.log10(np.sqrt((m[:k * w].reshape(k, w) ** 2).mean(1)) + 1e-12)
    quiet = r < thresh_db
    out, start = [], None
    for i, q in enumerate(list(quiet) + [False]):
        if q and start is None:
            start = i
        if not q and start is not None:
            if (i - start) * 0.05 >= min_len:
                out.append((round(start * 0.05, 2), round(i * 0.05, 2)))
            start = None
    return out


def bands(x):
    """share of energy per band, in percent. A beat in this style is mostly sub/low (the 808)."""
    m = stereo(x).mean(1)
    spec = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2
    f = np.fft.rfftfreq(len(m), 1 / SR)
    edges = [("sub <60", 0, 60), ("low 60-250", 60, 250), ("mid 250-2k", 250, 2000),
             ("high 2k-8k", 2000, 8000), ("air >8k", 8000, SR / 2)]
    tot = spec.sum() + 1e-12
    return {name: round(100 * spec[(f >= a) & (f < b)].sum() / tot, 1) for name, a, b in edges}


def side_in_sub(x):
    """how much of the <120 Hz energy is in the sides (should be ~0%: mono sub)."""
    x = stereo(x)
    m = lp((x[:, 0] + x[:, 1]) / 2, 120, 4)
    s = lp((x[:, 0] - x[:, 1]) / 2, 120, 4)
    return round(100 * (s ** 2).sum() / ((m ** 2).sum() + (s ** 2).sum() + 1e-12), 2)


def report(x, g=None, sections=None, name=""):
    """Print the numbers an agent uses instead of ears."""
    x = stereo(x)
    lines = [f"== {name}  {len(x) / SR:.2f} s",
             f"integrated loudness {lufs(x):.1f} LUFS   true peak {true_peak(x):.1f} dBTP   "
             f"crest {20 * np.log10(np.abs(x).max() / (np.sqrt((x ** 2).mean()) + 1e-12)):.1f} dB",
             f"bands % {bands(x)}   side-in-sub {side_in_sub(x)}%",
             f"silences (< -35 dB, > 0.4 s) {silences(x) or 'none'}"]
    if g is not None and sections:
        parts = []
        for nm, a, b in sections:
            parts.append(f"{nm} {lufs(x[g.at(a):g.at(b)]):.1f}")
        lines.append("section LUFS: " + " | ".join(parts))
    print("\n".join(lines))


# ---------------------------------------------------------------- finishing
def limiter(x, ceiling_db=-1.2, release=0.08, look=0.002):
    """Look-ahead brickwall limiter on 4x-oversampled peaks (so TRUE peak stays under the ceiling)."""
    from scipy.ndimage import maximum_filter1d
    c = db(ceiling_db)
    pk = np.abs(resample_poly(x, 4, 1, axis=0)).max(1)[: len(x) * 4].reshape(-1, 4).max(1)[: len(x)]
    if len(pk) < len(x):
        pk = np.concatenate([pk, np.zeros(len(x) - len(pk))])
    L = int(look * SR)
    env = maximum_filter1d(pk, size=2 * L + 1)
    want = np.minimum(1.0, c / np.maximum(env, 1e-9))
    # smooth: instant attack (already looked ahead), exponential release, run on 32-sample blocks
    ds = 32
    nb = int(np.ceil(len(want) / ds))
    wb = np.pad(want, (0, nb * ds - len(want)), constant_values=1).reshape(nb, ds).min(1)
    a = np.exp(-ds / (release * SR))
    gb = np.empty(nb)
    cur = 1.0
    for i in range(nb):
        v = wb[i]
        cur = v if v < cur else cur * a + (1 - a) * v
        gb[i] = cur
    gain = np.minimum(np.repeat(gb, ds)[: len(x)], want)
    k = np.hanning(2 * L + 1)
    gain = np.convolve(gain, k / k.sum(), "same")
    gain = -maximum_filter1d(-gain, size=2 * L + 1)
    return x * gain[:, None]


def preview_level(x, target=-14.0):
    """Stages 01-07 are all set to the same loudness so you compare the MUSIC, not the volume."""
    x = stereo(x)
    x = x * db(target - lufs(x))
    return limiter(x, -1.5)


def save(x, name):
    import soundfile as sf
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    sf.write(path, np.asarray(x, dtype=np.float32), SR, subtype="PCM_24")
    print("wrote", os.path.relpath(path, ROOT))
    return path


def load_stage(num):
    """Import an earlier stage's render.py as a module, so a stage can build on the one before."""
    d = [p for p in os.listdir(os.path.join(ROOT, "stages")) if p.startswith(f"{num:02d}-")][0]
    path = os.path.join(ROOT, "stages", d, "render.py")
    name = f"stage{num:02d}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def seed_from_argv(default):
    for i, a in enumerate(sys.argv):
        if a == "--seed" and i + 1 < len(sys.argv):
            return int(sys.argv[i + 1])
    return default
