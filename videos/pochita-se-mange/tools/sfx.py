#!/usr/bin/env python3
"""Bruitages de la vidéo Pochita : sons de la banque partagée (bruitages/) + sons synthétisés, mixés en une piste.

Génère assets/audio/bruitages/<nom>.wav (un fichier par son) et
assets/audio/bruitages/bruitages-stem.wav : tous les sons posés aux temps
de la liste CUES (temps globaux de la vidéo, en secondes). Pas de nappe continue : la musique suffit.
"""
import json
import os
import subprocess
import wave

import numpy as np
from scipy.signal import lfilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio", "bruitages")
BANK = os.path.join(ROOT, "..", "..", "bruitages")
SR = 44100
TOTAL = 68.873
rng = np.random.default_rng(1)  # graine fixe : rendu identique à chaque build


def t_axis(d):
    return np.arange(int(SR * d)) / SR


def noise(d):
    return rng.uniform(-1, 1, int(SR * d))


def lp(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([a], [1, -(1 - a)], x)


def hp(x, cutoff):
    return x - lp(x, cutoff)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def saw(freq, d):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(SR * d),))
    ph = np.cumsum(f) / SR
    return 2 * (ph % 1.0) - 1


def bank(key):
    """Son de la banque partagée (index.json) → mono 44,1 kHz."""
    idx = json.load(open(os.path.join(BANK, "index.json")))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(BANK, idx[key]["fichier"]), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(float)


# ---------------------------------------------------------------- les sons
def s_whoosh(d=0.5):  # entrée de carte / de titre 3D
    t = t_axis(d)
    sweep = np.interp(t, [0, d], [600, 3500])
    x = np.zeros(len(t))
    n = noise(d)
    # passe-bas qui s'ouvre : on filtre par blocs
    for k in range(0, len(t), 512):
        x[k:k + 512] = lp(n[max(0, k - 2048):k + 512], sweep[k])[-len(x[k:k + 512]):]
    return norm(hp(x, 200) * np.sin(np.pi * t / d) ** 2, 0.6)


def s_slam():  # titre qui tombe : coup sec grave + claquement
    d = 0.5
    t = t_axis(d)
    thump = np.sin(2 * np.pi * np.geomspace(140, 45, len(t)) * t) * np.exp(-t / 0.09)
    snap = hp(noise(d), 1500) * np.exp(-t / 0.012)
    return norm(thump + snap * 0.6, 0.9)


def s_tick():  # puce / étiquette qui apparaît
    d = 0.06
    t = t_axis(d)
    return norm(np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.01) + hp(noise(d), 4000) * np.exp(-t / 0.003), 0.5)


def s_trait():  # barre rouge qui raye le mot
    d = 0.35
    t = t_axis(d)
    return norm(hp(lp(noise(d), 6000), 1200) * np.exp(-t / 0.12) * np.clip(t / 0.01, 0, 1), 0.6)


def s_tronco(d=1.6, f0=70, f1=190):  # tronçonneuse qui monte en régime
    t = t_axis(d)
    f = np.interp(t, [0, d * 0.35, d], [f0, f1, f1 * 1.05])
    eng = saw(f, d) + 0.5 * saw(f * 2.01, d)
    puls = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * (f / 3.2) * t))
    x = lp(eng * puls, 2500) + hp(noise(d), 3000) * 0.15
    envl = np.clip(t / 0.05, 0, 1) * np.clip((d - t) / 0.25, 0, 1)
    return norm(x * envl, 0.8)


def s_glitch():
    d = 0.4
    t = t_axis(d)
    x = noise(d) * (np.sin(2 * np.pi * 19 * t) > 0) + saw(np.where(t < 0.2, 220, 110), d) * 0.6
    y = np.repeat(x[::8], 8)[: len(x)]
    return norm(np.round(y * 4) / 4 * np.clip((d - t) / 0.05, 0, 1), 0.5)


def s_riser(d=1.2):  # aspiration avant l'impact
    t = t_axis(d)
    x = hp(noise(d), 800) * (t / d) ** 2.5 + np.sin(2 * np.pi * np.geomspace(200, 900, len(t)) * t) * (t / d) ** 3 * 0.3
    return norm(x, 0.6)


def s_souffle(d=2.0):  # tourbillon des « PEUR »
    t = t_axis(d)
    x = lp(noise(d), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.5 * t)) * np.sin(np.pi * t / d)
    return norm(x, 0.6)


SOUNDS = {
    "whoosh": s_whoosh, "slam": s_slam, "tick": s_tick, "trait": s_trait, "tronco": s_tronco,
    "tronco-court": lambda: s_tronco(0.9, 110, 200), "glitch": s_glitch, "riser": s_riser, "souffle": s_souffle,
    # banque partagée (sons envoyés par Matt)
    "impact-grave": lambda: bank("impact-grave"), "bass-drop": lambda: bank("bass-drop"),
    "ralenti": lambda: bank("slow-motion"), "os": lambda: bank("bone-crack"),
}

# (son, temps global, gain)
CUES = [
    # accroche
    ("whoosh", 0.02, 0.5), ("slam", 0.85, 0.6), ("whoosh", 0.95, 0.5), ("whoosh", 2.25, 0.4), ("slam", 3.0, 0.6),
    ("whoosh", 4.2, 0.6),
    # rappel
    ("tick", 4.7, 0.8), ("whoosh", 5.45, 0.5), ("glitch", 8.35, 0.5), ("whoosh", 8.9, 0.5), ("whoosh", 10.05, 0.4),
    # question
    ("whoosh", 11.35, 0.6), ("impact-grave", 13.68, 0.7), ("whoosh", 14.3, 0.5), ("tronco-court", 15.35, 0.45),
    ("glitch", 17.22, 0.8), ("ralenti", 17.25, 0.25),
    # preuves
    ("whoosh", 18.95, 0.4), ("whoosh", 19.2, 0.4), ("whoosh", 19.32, 0.35), ("whoosh", 19.44, 0.35),
    ("tronco", 20.45, 0.5), ("impact-grave", 22.55, 0.8), ("bass-drop", 22.55, 0.45),
    # preuve 1
    ("tick", 23.4, 0.8), ("whoosh", 24.15, 0.4), ("whoosh", 25.05, 0.5), ("tick", 26.1, 0.7), ("tronco-court", 26.85, 0.35),
    ("whoosh", 27.6, 0.3), ("trait", 29.3, 0.8), ("slam", 29.35, 0.7),
    # preuve 2
    ("tick", 31.0, 0.8), ("slam", 32.05, 0.7), ("whoosh", 32.85, 0.5), ("tick", 34.2, 0.6), ("slam", 35.0, 0.6),
    ("whoosh", 35.85, 0.4), ("slam", 37.9, 0.6), ("whoosh", 39.6, 0.5), ("whoosh", 40.95, 0.5), ("trait", 43.1, 0.8),
    # Chainsaw Man
    ("whoosh", 44.85, 0.4), ("slam", 45.5, 0.6), ("whoosh", 46.25, 0.5), ("riser", 46.4, 0.5),
    ("impact-grave", 47.58, 0.9), ("tronco", 47.6, 0.45), ("whoosh", 48.75, 0.45), ("whoosh", 50.4, 0.45),
    ("whoosh", 52.1, 0.45), ("slam", 52.7, 0.7), ("os", 52.75, 0.35),
    # verdict
    ("whoosh", 54.45, 0.4), ("trait", 55.4, 0.8), ("riser", 55.4, 0.5), ("impact-grave", 56.58, 0.9), ("bass-drop", 56.6, 0.5),
    ("souffle", 58.4, 0.6), ("whoosh", 60.4, 0.5), ("slam", 61.0, 0.6),
    # ouroboros
    ("whoosh", 61.75, 0.45), ("slam", 62.6, 0.5), ("whoosh", 63.75, 0.4), ("tronco", 64.0, 0.4), ("whoosh", 66.05, 0.4),
    ("slam", 66.9, 0.5), ("whoosh", 67.55, 0.35),
]
for i in range(8):  # « mémoires » : les lettres s'effacent une à une
    CUES.append(("tick", round(10.75 + i * 0.05, 3), 0.35))


def write(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    cache = {}
    for name, fn in SOUNDS.items():
        cache[name] = fn()
        write(os.path.join(OUT, f"{name}.wav"), cache[name])
    stem = np.zeros(int(SR * TOTAL))
    for name, t, g in CUES:
        x = cache[name] * g
        o = int(t * SR)
        stem[o:o + len(x)] += x[: len(stem) - o]
        if o + len(x) > len(stem):  # ce qui déborde repart au début : la boucle reste continue
            rest = x[len(stem) - o:]
            stem[: len(rest)] += rest
    peak = np.max(np.abs(stem))
    if peak > 0.98:
        stem = stem / peak * 0.98
    write(os.path.join(OUT, "bruitages-stem.wav"), stem)
    print(f"{len(SOUNDS)} sons, {len(CUES)} placements, crête {peak:.2f}")


if __name__ == "__main__":
    main()
