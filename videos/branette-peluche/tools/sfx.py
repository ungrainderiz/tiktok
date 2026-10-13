#!/usr/bin/env python3
"""Bruitages de la vidéo Branette : sons de la banque partagée (bruitages/) + sons synthétisés, mixés en une piste.

Génère assets/audio/bruitages/<nom>.wav (un fichier par son) et
assets/audio/bruitages/bruitages-stem.wav : tous les sons posés aux temps
de la liste CUES (temps globaux de la vidéo, en secondes).
"""
import json
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio", "bruitages")
SR = 44100
TOTAL = 77.61
rng = np.random.default_rng(354)  # graine fixe : rendu identique à chaque build


def t_axis(d):
    return np.arange(int(SR * d)) / SR


def square(freq, d, duty=0.5):
    n = int(SR * d)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,)) if np.ndim(freq) else np.full(n, float(freq))
    phase = np.cumsum(f) / SR
    return np.where((phase % 1.0) < duty, 1.0, -1.0)


def tri(freq, d):
    n = int(SR * d)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,)) if np.ndim(freq) else np.full(n, float(freq))
    phase = np.cumsum(f) / SR
    return 2 * np.abs(2 * (phase % 1.0) - 1) - 1


def noise(d):
    return rng.uniform(-1, 1, int(SR * d))


def env(d, attack=0.004, decay=None, sustain_curve=4.0):
    t = t_axis(d)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    rel = np.exp(-sustain_curve * t / d) if decay is None else np.exp(-t / decay)
    return a * rel


def lowpass(x, cutoff):
    cut = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape) if np.ndim(cutoff) else np.full(x.shape, float(cutoff))
    a = 1 - np.exp(-2 * np.pi * cut / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def crush(x, hold=4, bits=6):
    """Échantillonnage bas + quantification : le grain « GBA »."""
    y = np.repeat(x[::hold], hold)[: len(x)]
    q = 2 ** (bits - 1)
    return np.round(y * q) / q


def seq(*parts):
    return np.concatenate(parts)


def silence(d):
    return np.zeros(int(SR * d))


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


# ---------------------------------------------------------------- les sons
def fastlp(x, cutoff):
    """Passe-bas un pôle à coupure fixe (rapide, pour les longues nappes)."""
    from scipy.signal import lfilter
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([a], [1, -(1 - a)], x)


BANK = os.path.join(ROOT, "..", "..", "bruitages")


def bank(key):
    """Son de la banque partagée (index.json) → mono 44,1 kHz."""
    idx = json.load(open(os.path.join(BANK, "index.json")))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(BANK, idx[key]["fichier"]), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(float)


def s_goutte():
    d = 0.12
    t = t_axis(d)
    return norm(np.sin(2 * np.pi * np.geomspace(1800, 900, len(t)) * t) * np.exp(-t / 0.025), 0.5)


def s_coeur():
    d = 0.55
    t = t_axis(d)
    def beat(o, g):
        tt = np.clip(t - o, 0, None)
        return np.sin(2 * np.pi * np.maximum(38, 62 - tt * 90) * tt) * np.exp(-tt / 0.06) * (t >= o) * g
    return norm(beat(0, 1.0) + beat(0.17, 0.75), 0.9)


def s_tic():
    d = 0.08
    t = t_axis(d)
    return norm(lowpass(noise(d), 5000) * np.exp(-t / 0.006) + np.sin(2 * np.pi * 2100 * t) * np.exp(-t / 0.015) * 0.5, 0.6)


def s_cran():  # un cran de fermeture éclair : petit clic métallique sec
    d = 0.09
    t = t_axis(d)
    return norm(lowpass(noise(d), 7000) * np.exp(-t / 0.004) + np.sin(2 * np.pi * 3300 * t) * np.exp(-t / 0.01) * 0.6, 0.8)


def s_zip():  # fermeture qu'on ouvre d'un coup (1 s de crans accélérés)
    d = 1.0
    x = np.zeros(int(SR * d))
    c = s_cran()
    p = 0.0
    gap = 0.09
    while p < d - 0.1:
        o = int(p * SR)
        x[o:o + len(c)] += c[: len(x) - o] * 0.8
        p += gap
        gap = max(0.018, gap * 0.86)
    return norm(x, 0.8)


def s_projecteur():  # souvenir : cliquetis de pellicule
    d = 9.7
    x = np.zeros(int(SR * d))
    c = s_tic() * 0.3
    for k in range(int(d * 18)):
        o = int(k / 18 * SR)
        x[o:o + len(c)] += c[: len(x) - o]
    return norm(fastlp(x, 3000) + fastlp(noise(d), 1200) * 0.08, 0.35)


def s_whoosh():
    d = 0.6
    t = t_axis(d)
    return norm(fastlp(noise(d), 2500) * np.sin(np.pi * t / d) ** 2, 0.7)


def s_claque():  # couvercle de benne qui claque
    d = 0.9
    t = t_axis(d)
    clank = (square(180, d, 0.4) * square(527, d, 0.5)) * np.exp(-t / 0.12) * 0.5
    thud = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.1)
    return norm(clank + thud + fastlp(noise(d), 4000) * np.exp(-t / 0.02), 0.9)


def s_feu():
    d = 0.95
    t = t_axis(d)
    roar = fastlp(noise(d), 700) * 1.5
    crack = np.zeros(len(t))
    for _ in range(30):
        o = int(rng.uniform(0, d - 0.01) * SR)
        crack[o:o + 60] += rng.uniform(-1, 1, 60) * rng.uniform(0.3, 1)
    return norm((roar + crack) * np.clip(t / 0.05, 0, 1) * np.clip((d - t) / 0.2, 0, 1), 0.7)


def s_terre():  # pelletées de terre
    out = np.zeros(int(SR * 0.7))
    for k in range(3):
        d = 0.18
        t = t_axis(d)
        x = fastlp(noise(d), 900) * np.exp(-t / 0.05) + np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.05)
        o = int(k * 0.22 * SR)
        out[o:o + len(x)] += x[: len(out) - o]
    return norm(out, 0.8)


def s_plouf():
    d = 1.2
    t = t_axis(d)
    splash = fastlp(noise(d), 3000) * np.exp(-t / 0.15)
    bloop = np.sin(2 * np.pi * np.geomspace(300, 120, len(t)) * t) * np.exp(-t / 0.3) * 0.5
    return norm(splash + bloop, 0.8)


def s_dex():
    return norm(seq(square(1046, 0.05, 0.5), silence(0.02), square(1568, 0.05, 0.5), silence(0.02), square(2093, 0.12, 0.5) * env(0.12)), 0.4)


def s_scan():
    d = 0.95
    t = t_axis(d)
    return norm(np.sin(2 * np.pi * np.cumsum(np.where(t < d / 2, np.linspace(600, 1800, len(t)), np.linspace(1800, 600, len(t)))) / SR) * 0.5
                + square(60, d, 0.5) * 0.05, 0.4)


def s_texte():
    out = []
    for i in range(10):
        out += [square(880 if i % 2 else 988, 0.016, 0.125), silence(0.03)]
    return norm(seq(*out), 0.25)


def s_glitch():
    d = 0.5
    t = t_axis(d)
    x = crush(noise(d) * (np.sin(2 * np.pi * 23 * t) > 0) + square(110, d, 0.5) * 0.5, 6, 3)
    return norm(x * np.clip((d - t) / 0.05, 0, 1), 0.6)


def s_fumee():  # l'énergie maudite s'échappe
    d = 1.6
    t = t_axis(d)
    x = fastlp(noise(d), 600) * np.clip(t / 0.3, 0, 1) * np.exp(-np.clip(t - 0.6, 0, None) / 0.5)
    moan = sum(np.sin(2 * np.pi * f * (1 + 0.03 * np.sin(2 * np.pi * 4 * t)) * t) for f in (110, 116.5, 164.8)) / 3
    return norm(x * 1.5 + moan * 0.5 * np.sin(np.pi * t / d), 0.8)


def s_souffle(inhale=True):
    d = 0.9
    t = t_axis(d)
    shape = np.sin(np.pi * t / d) ** (0.6 if inhale else 1.4)
    return norm((fastlp(noise(d), 2400) - fastlp(noise(d), 500)) * shape, 0.5)


def s_drone():  # paupières qui se ferment : nappe grave qui monte
    d = 1.6
    t = t_axis(d)
    x = sum(np.sin(2 * np.pi * f * t) for f in (55, 58.3, 82.4)) * (t / d) ** 2
    return norm(x, 0.6)


def s_poignee():
    d = 0.3
    t = t_axis(d)
    return norm(lowpass(noise(d), 4000) * np.exp(-t / 0.01) + square(240, d, 0.4) * np.exp(-t / 0.04) * 0.4, 0.7)


def s_grince(d=2.0):  # porte qui grince en s'ouvrant
    t = t_axis(d)
    f = 340 + 120 * np.sin(2 * np.pi * 0.6 * t) + 40 * np.sin(2 * np.pi * 7 * t)
    x = square(f, d, 0.2) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 11 * t)))
    return norm(fastlp(x, 1800) * np.clip(t / 0.2, 0, 1), 0.5)


SOUNDS = {
    "goutte": s_goutte, "coeur": s_coeur, "tic": s_tic, "cran": s_cran, "zip": s_zip, "projecteur": s_projecteur,
    "whoosh": s_whoosh, "claque": s_claque, "feu": s_feu, "terre": s_terre, "plouf": s_plouf, "dex": s_dex,
    "scan": s_scan, "texte": s_texte, "glitch": s_glitch, "fumee": s_fumee, "inspire": lambda: s_souffle(True),
    "expire": lambda: s_souffle(False), "drone": s_drone, "poignee": s_poignee, "grince": lambda: s_grince(1.95),
    # banque partagée (sons envoyés par Matt)
    "impact-grave": lambda: bank("impact-grave"), "rire-jouet": lambda: bank("laugh-toy-world-animation"),
    "suspense": lambda: bank("hells-kitchen-suspense"), "cloche": lambda: bank("undertakers-bell"),
    "piano": lambda: bank("dark-piano-dexter"), "bass-drop": lambda: bank("bass-drop"),
    "souvenir": lambda: bank("grandma-house"), "ralenti": lambda: bank("slow-motion"), "os": lambda: bank("bone-crack"),
}

# (son, temps global, gain)
CUES = [
    ("impact-grave", 0.0, 0.45),
    ("projecteur", 8.1, 0.6), ("souvenir", 10.6, 0.3), ("whoosh", 14.2, 0.5), ("claque", 14.95, 0.35),
    ("suspense", 18.65, 0.55), ("whoosh", 21.5, 0.7), ("claque", 22.4, 0.9), ("os", 22.45, 0.4),
    ("coeur", 24.7, 0.6), ("coeur", 25.5, 0.6), ("impact-grave", 26.33, 0.8), ("rire-jouet", 26.45, 0.45),
    ("cran", 32.4, 1.0),
    ("feu", 32.55, 0.8), ("terre", 33.42, 0.9), ("plouf", 34.15, 0.8),
    ("impact-grave", 35.85, 0.5), ("impact-grave", 36.55, 0.55), ("impact-grave", 37.1, 0.6),
    ("cran", 37.77, 1.0), ("cran", 38.58, 1.0), ("cran", 38.9, 1.0), ("cran", 39.4, 1.0),
    ("dex", 39.95, 0.8), ("scan", 41.6, 0.7), ("texte", 42.7, 0.6), ("cloche", 44.22, 0.7),
    ("texte", 45.3, 0.6), ("texte", 45.9, 0.6), ("texte", 46.5, 0.6), ("texte", 48.0, 0.6), ("texte", 48.6, 0.6),
    ("piano", 49.7, 0.8), ("texte", 52.56, 0.6), ("texte", 53.2, 0.6), ("texte", 53.8, 0.6), ("glitch", 53.68, 0.7),
    ("zip", 55.5, 0.9), ("fumee", 56.6, 0.9), ("bass-drop", 57.13, 0.9),
    ("cran", 60.43, 1.0), ("cran", 60.65, 1.0), ("cran", 60.87, 1.0),
    ("ralenti", 66.6, 0.35), ("drone", 66.6, 0.6), ("inspire", 68.45, 0.8), ("expire", 73.8, 0.7),
    ("poignee", 75.45, 0.8), ("grince", 75.66, 0.6),
]
for t in (3.95, 4.3, 4.9, 5.4, 6.1, 6.8, 7.4):  # gouttes qui tombent de la peluche
    CUES.append(("goutte", t, 0.5))
for k in range(9):  # cœur qui bat pendant qu'on la regarde
    CUES.append(("coeur", round(58.7 + k * 0.75, 3), 0.55))
for k in range(5):  # la nuit : le réveil fait tic… tac…
    CUES.append(("tic", round(61.7 + k, 3), 0.5))
for k in range(5):
    CUES.append(("coeur", round(61.9 + k * 0.95, 3), 0.45))


def bed():
    """Pluie continue : forte dehors (porte, rue), étouffée dedans ; même niveau au début et à la fin (boucle)."""
    n = int(SR * TOTAL)
    t = np.arange(n) / SR
    x = fastlp(rng.uniform(-1, 1, n), 3200) - fastlp(rng.uniform(-1, 1, n), 250) * 0.5
    x /= np.max(np.abs(x))
    muffled = fastlp(x, 500) * 2.2
    out_ = np.interp(t, [0, 8.0, 8.2, 17.8, 18.0, 24.3, 24.5, 74.4, 74.6, TOTAL], [1, 1, 0, 0, 1, 1, 0, 0, 1, 1])
    g_in = np.interp(t, [0, 8.1, 8.2, 17.8, 17.9, 24.4, 24.5, 39.8, 40, 58, 61.5, 74.4, 74.5, TOTAL],
                     [0, 0, 0.0, 0.0, 0, 0, 0.6, 0.6, 0.3, 0.3, 0.6, 0.6, 0, 0])
    return x * out_ * 0.16 + muffled * g_in * 0.12


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
    stem = bed()
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
