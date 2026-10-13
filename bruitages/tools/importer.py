#!/usr/bin/env python3
"""Découpe une compilation de bruitages (vidéo « un son par carton ») en fichiers séparés + index.json.

Usage : python3 bruitages/tools/importer.py <video.mp4> <coupes.json>
coupes.json = [[début, nom], …] (débuts des cartons, détectés par changement d'image du titre).
Chaque son est recadré sur sa partie audible (silences en tête et en queue retirés) et normalisé en crête.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100


def slug(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def decode(path, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim(x, thr_db=-42, pad=0.03):
    win = int(0.01 * SR)
    env = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
    on = np.where(20 * np.log10(env + 1e-9) > thr_db)[0]
    if not len(on):
        return x[:0]
    a, b = max(0, on[0] - int(pad * SR)), min(len(x), on[-1] + int(pad * SR))
    y = x[a:b].copy()
    f = min(len(y) // 4, int(0.008 * SR))  # micro fondus anti-clic
    if f:
        y[:f] *= np.linspace(0, 1, f)
        y[-f:] *= np.linspace(1, 0, f)
    return y


def main(video, cuts_path, sub="memes"):
    cuts = json.load(open(cuts_path))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    idx_path = os.path.join(ROOT, "index.json")
    index = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
    os.makedirs(os.path.join(ROOT, sub), exist_ok=True)
    for (a, name), nxt in zip(cuts, cuts[1:] + [[dur, None]]):
        y = trim(decode(video, a, nxt[0]))
        if len(y) < SR * 0.05:
            continue
        y = y / (np.abs(y).max() or 1) * 0.89
        key = slug(name)
        rel = f"{sub}/{key}.ogg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "libvorbis",
                        "-q:a", "5", os.path.join(ROOT, rel)], input=y.astype(np.float32).tobytes(), check=True)
        old = index.get(key, {})
        index[key] = {"nom": name, "fichier": rel, "duree": round(len(y) / SR, 2),
                      "ambiance": old.get("ambiance", []), "usage": old.get("usage", "")}
        print(f"{key:32s} {len(y) / SR:5.2f} s")
    json.dump(index, open(idx_path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
