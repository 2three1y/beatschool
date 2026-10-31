"""measure.py: the ears of an agent that can't hear.

    python measure.py out/stage08.wav
    python measure.py out/stage08.wav --bpm 145 --sections "intro:0:8,drop 1:8:24,switch:24:40,drop 2:40:56,outro:56:64"

Prints integrated loudness (LUFS), true peak (dBTP), crest, energy per band, how much
of the sub is in the sides, every silence longer than 0.4 s, and LUFS per section.
"""
import argparse

import soundfile as sf

import kit

ap = argparse.ArgumentParser()
ap.add_argument("wav")
ap.add_argument("--bpm", type=float, default=145)
ap.add_argument("--sections", default="", help='"name:startbar:endbar,..."')
a = ap.parse_args()
x, sr = sf.read(a.wav, always_2d=True)
assert sr == kit.SR, f"expected {kit.SR} Hz, got {sr}"
secs = [(p.split(":")[0], float(p.split(":")[1]), float(p.split(":")[2])) for p in a.sections.split(",") if p]
kit.report(x, kit.Grid(a.bpm), secs or None, name=a.wav)
