#!/usr/bin/env python3
"""Bruitages synthétisés façon GBA (ondes carrées, bruit, bitcrush) + piste mixée.

Génère assets/audio/bruitages/<nom>.wav (un fichier par son) et
assets/audio/bruitages/bruitages-stem.wav : tous les sons posés aux temps
de la liste CUES (temps globaux de la vidéo, en secondes).
"""
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio", "bruitages")
SR = 44100
TOTAL = 86.4
rng = np.random.default_rng(384)  # graine fixe : rendu identique à chaque build


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
def s_coup():  # attaque « super efficace »
    d = 0.32
    t = t_axis(d)
    body = square(np.linspace(420, 70, len(t)), d, 0.5) * env(d, decay=0.08)
    crack = lowpass(noise(d), np.linspace(9000, 600, len(t))) * env(d, decay=0.05) * 1.6
    return norm(crush(body * 0.6 + crack, 3, 6))


def s_pv():  # PV qui descendent
    out = []
    for i in range(14):
        f = 1320 - i * 45
        out.append(square(f, 0.03, 0.25) * 0.5)
        out.append(silence(0.018))
    return norm(crush(seq(*out), 2, 5), 0.6)


def s_pv_bas():  # alarme PV bas
    out = []
    for _ in range(3):
        out += [square(1046, 0.12, 0.5), silence(0.04), square(784, 0.12, 0.5), silence(0.16)]
    return norm(crush(seq(*out), 2, 5), 0.45)


def s_dialogue():  # défilement du texte
    out = []
    for i in range(9):
        out += [square(1568 if i % 2 else 1760, 0.018, 0.125), silence(0.034)]
    return norm(seq(*out), 0.35)


def s_menu():  # bip d'interface
    return norm(seq(square(1318, 0.05, 0.5) * env(0.05, sustain_curve=1), square(1975, 0.09, 0.5) * env(0.09)), 0.45)


def s_flash():  # transition « début de combat »
    d = 0.45
    t = t_axis(d)
    sweep = square(np.geomspace(200, 3200, len(t)), d, 0.5) * np.linspace(0.2, 1, len(t))
    hiss = lowpass(noise(d), np.geomspace(500, 12000, len(t))) * np.linspace(0, 1, len(t))
    x = (sweep * 0.5 + hiss) * np.where(t > d - 0.03, (d - t) / 0.03, 1)
    return norm(crush(x, 3, 6), 0.7)


def s_tampon():  # tampon qui s'écrase
    d = 0.4
    t = t_axis(d)
    thump = np.sin(2 * np.pi * np.cumsum(np.linspace(140, 45, len(t))) / SR) * env(d, decay=0.09)
    click = lowpass(noise(d), 4000) * env(d, decay=0.012) * 1.5
    return norm(thump + click)


def s_whoosh():
    d = 0.42
    t = t_axis(d)
    shape = np.sin(np.pi * t / d) ** 2
    return norm(lowpass(noise(d), np.geomspace(400, 5000, len(t))) * shape, 0.6)


def s_pop():  # apparition d'un élément
    d = 0.12
    return norm(square(np.geomspace(500, 1500, int(SR * d)), d, 0.5) * env(d, sustain_curve=3), 0.4)


def s_pop_bas():
    d = 0.3
    return norm(square(np.geomspace(700, 160, int(SR * d)), d, 0.5) * env(d, sustain_curve=2), 0.45)


def s_explosion():
    d = 1.3
    t = t_axis(d)
    x = lowpass(noise(d), np.geomspace(6000, 150, len(t))) * env(d, decay=0.35)
    boom = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 30, len(t))) / SR) * env(d, decay=0.25)
    return norm(crush(x * 1.8 + boom, 4, 6))


def s_grondement():  # la ville s'effondre
    d = 1.6
    t = t_axis(d)
    x = lowpass(noise(d), 260) * (1 + 0.5 * np.sin(2 * np.pi * 9 * t))
    crash = sum(lowpass(noise(d), 2500) * np.exp(-np.clip(t - o, 0, None) / 0.07) * (t >= o) for o in (0.0, 0.25, 0.55, 0.8, 1.05))
    return norm(x * env(d, attack=0.05, sustain_curve=2.5) * 2 + crash * 0.5)


def s_radar():
    d = 0.6
    t = t_axis(d)
    ping = np.sin(2 * np.pi * 1180 * t) * env(d, decay=0.09)
    echo = np.roll(ping, int(0.18 * SR)) * 0.35
    echo[: int(0.18 * SR)] = 0
    return norm(ping + echo, 0.5)


def s_compteur():
    out = []
    for i in range(16):
        out += [square(880 + i * 40, 0.015, 0.25), silence(0.028)]
    return norm(seq(*out), 0.35)


def s_coche():
    return norm(seq(square(988, 0.05, 0.5), square(1480, 0.1, 0.5) * env(0.1)), 0.45)


def s_arret():  # la musique coupe net (arrêt de bande)
    d = 0.35
    t = t_axis(d)
    return norm(square(np.geomspace(330, 40, len(t)), d, 0.5) * env(d, sustain_curve=1.5) * 0.6, 0.5)


def s_ko():  # le Pokémon tombe K.O.
    d = 1.1
    t = t_axis(d)
    glide = square(np.geomspace(880, 60, len(t)), d, 0.5) * env(d, sustain_curve=1.2)
    thud = np.sin(2 * np.pi * 55 * t) * np.exp(-np.clip(t - 0.85, 0, None) / 0.1) * (t > 0.85)
    return norm(crush(glide * 0.7 + thud, 3, 6), 0.8)


def s_evolution_inverse():  # arpège d'évolution… à l'envers
    notes = [1568, 1318, 1175, 1046, 988, 880, 784, 659, 587, 523, 494, 440, 392, 330]
    out = []
    for i, f in enumerate(notes):
        dur = 0.15 - i * 0.005
        out.append((tri(f, dur) * 0.7 + square(f * 2, dur, 0.125) * 0.2) * env(dur, sustain_curve=2.5))
    shimmer = seq(*out)
    t = t_axis(len(shimmer) / SR)
    shimmer = shimmer * (1 + 0.3 * np.sin(2 * np.pi * 12 * t))
    return norm(shimmer, 0.6)


def s_evolution_fin():  # accord final
    d = 1.2
    t = t_axis(d)
    chord = sum(tri(f, d) for f in (523.25, 659.25, 783.99, 1046.5))
    sparkle = sum(np.sin(2 * np.pi * f * t) * np.exp(-np.clip(t - o, 0, None) / 0.12) * (t >= o) for f, o in ((2093, 0.0), (2637, 0.08), (3136, 0.16)))
    return norm((chord / 4) * env(d, sustain_curve=3) + sparkle * 0.4, 0.7)


def s_robots():  # pluie de robots qui s'empilent (18 chocs métalliques)
    d = 1.6
    x = np.zeros(int(SR * d))
    for k in range(18):
        o = int((k * 0.065) * SR)
        cd = 0.12
        tt = t_axis(cd)
        clank = (square(320 + (k % 5) * 37, cd, 0.3) * square(1210 + (k % 3) * 90, cd, 0.5)) * np.exp(-tt / 0.03)
        clank += lowpass(noise(cd), 3000) * np.exp(-tt / 0.015)
        x[o:o + len(clank)] += clank[: len(x) - o]
    return norm(crush(x, 2, 6), 0.7)


def s_montee():  # ré-évolution qui monte jusqu'au blanc (raccord de la boucle)
    d = 0.45
    t = t_axis(d)
    sweep = tri(np.geomspace(330, 2600, len(t)), d) * np.linspace(0.3, 1, len(t))
    shimmer = lowpass(noise(d), np.geomspace(1500, 12000, len(t))) * np.linspace(0, 0.6, len(t))
    return norm(sweep * 0.7 + shimmer, 0.6)


SOUNDS = {
    "coup": s_coup, "pv": s_pv, "pv-bas": s_pv_bas, "dialogue": s_dialogue, "menu": s_menu,
    "flash": s_flash, "tampon": s_tampon, "whoosh": s_whoosh, "pop": s_pop, "pop-bas": s_pop_bas,
    "explosion": s_explosion, "grondement": s_grondement, "radar": s_radar, "compteur": s_compteur,
    "coche": s_coche, "arret": s_arret, "ko": s_ko, "evolution-inverse": s_evolution_inverse,
    "evolution-fin": s_evolution_fin, "robots": s_robots, "montee": s_montee,
}

V = 0.2  # la voix démarre à 0.2 s
HITS = [26.2, 41.32, 56.84, 67.5, 77.5]

# (son, temps global, gain)
CUES = [
    ("whoosh", 0.0, 0.7), ("tampon", 2.64, 1.0), ("whoosh", 3.35, 0.5), ("pop", 4.4, 0.8), ("menu", 5.7, 0.8),
    ("flash", 6.12, 0.8), ("pop", 8.04, 0.7), ("tampon", 8.55, 0.6), ("whoosh", 10.6, 0.5), ("pop", 12.2, 0.7),
    ("arret", 14.12, 0.9), ("tampon", 14.28, 0.7), ("whoosh", 15.08, 0.6), ("tampon", 16.29, 0.9),
    ("compteur", 17.1, 0.8), ("pop", 17.96, 0.6), ("whoosh", 18.4, 0.6), ("explosion", 19.08, 0.6),
    ("whoosh", 20.8, 0.7), ("explosion", 20.8, 0.5), ("explosion", 23.4, 0.9),
    ("radar", 24.55, 0.8), ("pop", 24.8, 0.7), ("radar", 25.35, 0.6), ("tampon", 26.14, 0.9),
    ("whoosh", 28.04, 0.6), ("tampon", 29.24, 0.9), ("tampon", 31.24, 0.8), ("tampon", 32.16, 0.8), ("tampon", 33.04, 0.8), ("pop-bas", 33.64, 0.8),
    ("whoosh", 36.9, 0.6), ("whoosh", 37.15, 0.5), ("pop", 38.76, 0.8),
    ("flash", 41.62, 0.8), ("grondement", 42.3, 0.5), ("grondement", 43.1, 0.4),
    ("tampon", 48.54, 1.0), ("coche", 50.0, 0.8), ("coche", 50.63, 0.8), ("coche", 51.19, 0.8),
    ("tampon", 55.08, 0.5), ("tampon", 55.21, 0.5), ("tampon", 55.34, 0.5), ("pop", 55.8, 0.7), ("whoosh", 56.6, 0.6),
    ("flash", 56.82, 0.8), ("whoosh", 57.2, 0.5), ("pop", 60.16, 0.6), ("tampon", 61.34, 0.9),
    ("whoosh", 63.4, 0.7), ("explosion", 64.04, 0.8), ("whoosh", 65.0, 0.6), ("explosion", 65.6, 0.9),
    ("pop", 66.44, 0.7), ("whoosh", 67.28, 0.4), ("pop", 67.5, 0.7),
    ("pop", 70.12, 0.7), ("whoosh", 71.32, 0.8), ("grondement", 72.92, 0.9), ("explosion", 72.92, 0.6), ("tampon", 74.14, 1.0),
    ("tampon", 75.84, 0.9), ("robots", 76.32, 0.8),
    ("whoosh", 80.1, 0.6), ("whoosh", 81.1, 0.6), ("explosion", 81.1, 0.3),
    ("ko", 82.6, 0.9), ("dialogue", 83.3, 0.8), ("evolution-inverse", 83.6, 0.9), ("evolution-fin", 85.64, 1.0), ("montee", 85.95, 0.9),
]
for t in HITS:
    CUES += [("coup", t, 1.0), ("pv", t + 0.1, 0.8), ("dialogue", t + 0.2, 0.7)]
CUES += [("coup", 82.35, 1.0), ("pv", 82.45, 0.8), ("pv-bas", 68.3, 0.7), ("pv-bas", 78.3, 0.7)]


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
    peak = np.max(np.abs(stem))
    if peak > 0.98:
        stem = stem / peak * 0.98
    write(os.path.join(OUT, "bruitages-stem.wav"), stem)
    print(f"{len(SOUNDS)} sons, {len(CUES)} placements, crête {peak:.2f}")


if __name__ == "__main__":
    main()
