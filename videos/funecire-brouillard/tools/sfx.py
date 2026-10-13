#!/usr/bin/env python3
"""Bruitages d'horreur synthétisés (pluie, pas, battements, souffles, sons d'interface DS) + piste mixée.

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
TOTAL = 51.74
rng = np.random.default_rng(607)  # graine fixe : rendu identique à chaque build


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


def s_pas():  # un pas sur le gravier mouillé
    d = 0.18
    t = t_axis(d)
    crunch = lowpass(noise(d), 2200) * np.exp(-t / 0.035)
    thud = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.04)
    return norm(crunch + thud * 0.8, 0.6)


def s_coeur():  # battement (double coup sourd)
    d = 0.55
    t = t_axis(d)
    def beat(o, g):
        tt = np.clip(t - o, 0, None)
        return np.sin(2 * np.pi * np.maximum(38, 62 - tt * 90) * tt) * np.exp(-tt / 0.06) * (t >= o) * g
    return norm(beat(0, 1.0) + beat(0.17, 0.75), 0.9)


def s_bip_reseau():  # « pas de réseau » : deux bips descendants
    return norm(seq(square(988, 0.09, 0.5) * env(0.09, sustain_curve=1), silence(0.05), square(659, 0.16, 0.5) * env(0.16, sustain_curve=1.5)), 0.4)


def s_lampe():  # la lampe grésille puis meurt
    d = 0.7
    t = t_axis(d)
    buzz = square(120, d, 0.5) * (rng.random(len(t)) > 0.25) * np.linspace(1, 0, len(t)) ** 2
    click = np.zeros(len(t))
    click[int(0.62 * SR):int(0.625 * SR)] = 1
    return norm(lowpass(buzz, 1800) * 0.5 + click, 0.5)


def s_rencontre():  # transition « Pokémon sauvage » : balayage + coup
    d = 0.9
    t = t_axis(d)
    sweep = square(np.geomspace(1400, 180, len(t)), d, 0.5) * env(d, sustain_curve=2)
    hiss = lowpass(noise(d), np.geomspace(9000, 400, len(t))) * env(d, sustain_curve=3)
    return norm(crush(sweep * 0.5 + hiss * 0.7, 3, 6), 0.75)


def s_boom():  # « Grosse erreur. » : impact grave
    d = 2.2
    t = t_axis(d)
    sub = np.sin(2 * np.pi * np.cumsum(np.geomspace(70, 28, len(t))) / SR) * np.exp(-t / 0.7)
    hit = fastlp(noise(d), 900) * np.exp(-t / 0.08) * 3
    return norm(sub + hit, 0.95)


def s_rappel():  # rayon rouge du rappel dans la Poké Ball
    d = 0.5
    t = t_axis(d)
    return norm(crush(square(np.geomspace(2000, 300, len(t)), d, 0.25) * env(d, sustain_curve=2), 2, 5), 0.45)


def s_ball():  # la Poké Ball qui tremble (clic + rebond)
    d = 0.22
    t = t_axis(d)
    return norm(lowpass(noise(d), 3500) * np.exp(-t / 0.02) + square(330, d, 0.5) * np.exp(-t / 0.03) * 0.3, 0.5)


def s_givre():  # givre qui craque sur l'écran
    d = 2.5
    x = np.zeros(int(SR * d))
    for k in range(40):
        o = int(rng.uniform(0, d - 0.05) * SR)
        cd = 0.02
        c = noise(cd) * np.exp(-t_axis(cd) / 0.004)
        x[o:o + len(c)] += c * rng.uniform(0.3, 1)
    t = t_axis(d)
    return norm(lowpass(x, 7000) * np.linspace(0.2, 1, len(t)), 0.4)


def s_acouphene():  # vue brouillée : sifflement aigu
    d = 2.2
    t = t_axis(d)
    tone = np.sin(2 * np.pi * 6200 * t) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t))
    shape = np.clip(t / 0.6, 0, 1) * np.clip((d - t) / 0.8, 0, 1)
    return norm(tone * shape, 0.18)


def s_flamme():  # souffle d'une flamme (crépitement doux)
    d = 2.0
    t = t_axis(d)
    roar = fastlp(noise(d), 500) * (0.7 + 0.3 * np.sin(2 * np.pi * 2.3 * t))
    crack = np.zeros(len(t))
    for _ in range(25):
        o = int(rng.uniform(0, d - 0.01) * SR)
        crack[o:o + 60] += rng.uniform(-1, 1, 60) * rng.uniform(0.2, 0.8)
    shape = np.sin(np.pi * t / d)
    return norm((roar * 2 + crack) * shape, 0.6)


def s_dex_ouvre():  # Pokédex : ouverture + bips
    return norm(seq(square(1046, 0.05, 0.5), silence(0.02), square(1568, 0.05, 0.5), silence(0.02), square(2093, 0.12, 0.5) * env(0.12)), 0.4)


def s_texte():  # défilement du texte (un tic par lettre, grave)
    out = []
    for i in range(10):
        out += [square(880 if i % 2 else 988, 0.016, 0.125), silence(0.03)]
    return norm(seq(*out), 0.25)


def s_alerte():  # « énergie vitale » : distorsion rouge
    d = 0.7
    t = t_axis(d)
    x = square(np.where((t * 12).astype(int) % 2, 220, 233), d, 0.5) * env(d, sustain_curve=2.5)
    return norm(crush(x + noise(d) * 0.3 * env(d), 4, 4), 0.55)


def s_chute():  # tomber à genoux
    d = 0.6
    t = t_axis(d)
    thud = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 40, len(t))) / SR) * np.exp(-t / 0.12)
    grit = lowpass(noise(d), 1500) * np.exp(-t / 0.06)
    return norm(thud + grit * 0.7, 0.9)


def s_allume():  # une petite flamme qui s'allume (fft)
    d = 0.35
    t = t_axis(d)
    return norm(lowpass(noise(d), np.geomspace(600, 4000, len(t))) * np.exp(-t / 0.1) + np.sin(2 * np.pi * 1760 * t) * np.exp(-t / 0.08) * 0.15, 0.35)


def s_inverse():  # aspiration à l'envers avant le visage
    d = 1.1
    t = t_axis(d)
    x = fastlp(noise(d), 2500) * (t / d) ** 3
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 900, len(t))) / SR) * (t / d) ** 4
    return norm(x * 2 + tone * 0.5, 0.8)


def s_visage():  # apparition du visage : cri spectral filtré
    d = 1.0
    t = t_axis(d)
    vox = sum(np.sin(2 * np.pi * f * (1 + 0.02 * np.sin(2 * np.pi * 7 * t)) * t) / (i + 1) for i, f in enumerate((440, 466, 880, 1320)))
    hit = fastlp(noise(d), 3000) * np.exp(-t / 0.05) * 2
    return norm(vox * np.exp(-t / 0.35) + hit, 0.8)


def s_chaleur():  # nappe chaude et douce (accord majeur lent)
    d = 4.2
    t = t_axis(d)
    pad = sum(np.sin(2 * np.pi * f * t) for f in (220, 277.2, 329.6, 440))
    shape = np.clip(t / 1.2, 0, 1) * np.clip((d - t) / 1.0, 0, 1)
    return norm(pad * shape * (1 + 0.1 * np.sin(2 * np.pi * 0.7 * t)), 0.5)


def s_allumage():  # tu t'enflammes à ton tour
    d = 1.0
    t = t_axis(d)
    whoosh = fastlp(noise(d), 1200) * np.exp(-t / 0.25) * np.clip(t / 0.03, 0, 1)
    bell = np.sin(2 * np.pi * 659 * t) * np.exp(-t / 0.4) * 0.4
    return norm(whoosh * 2 + bell, 0.85)


def s_montee():  # montée vers le raccord de la boucle
    d = 1.2
    t = t_axis(d)
    x = fastlp(noise(d), 1800) * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 330, len(t))) / SR) * (t / d) ** 2
    return norm(x + tone * 0.4, 0.6)


SOUNDS = {
    "pas": s_pas, "coeur": s_coeur, "bip-reseau": s_bip_reseau, "lampe": s_lampe, "rencontre": s_rencontre,
    "boom": s_boom, "rappel": s_rappel, "ball": s_ball, "givre": s_givre, "acouphene": s_acouphene,
    "flamme": s_flamme, "dex-ouvre": s_dex_ouvre, "texte": s_texte, "alerte": s_alerte, "chute": s_chute,
    "allume": s_allume, "inverse": s_inverse, "visage": s_visage, "chaleur": s_chaleur, "allumage": s_allumage,
    "montee": s_montee,
}

# (son, temps global, gain)
CUES = [
    ("bip-reseau", 4.45, 0.8), ("lampe", 5.35, 0.9), ("rencontre", 10.0, 0.9), ("flamme", 11.0, 0.5),
    ("rappel", 20.0, 0.8), ("ball", 20.55, 0.7), ("boom", 20.95, 1.0), ("ball", 21.3, 0.6),
    ("givre", 22.6, 0.7), ("acouphene", 25.9, 1.0), ("chaleur", 26.8, 0.35),
    ("dex-ouvre", 28.75, 0.9), ("alerte", 33.8, 0.9),
    ("chute", 34.75, 1.0),
    ("inverse", 40.4, 0.9), ("visage", 41.47, 0.9),
    ("chaleur", 41.95, 0.55),
    ("allumage", 47.5, 0.9),
    ("montee", 50.54, 0.8),
]
# pas : on marche (s01–s05 puis s07), puis le rythme ralentit, les jambes sont lourdes
for t in np.arange(0.1, 20.0, 0.55):
    if not 10.0 <= t < 13.4:
        CUES.append(("pas", round(float(t), 3), 0.45))
for t in np.arange(21.7, 24.4, 0.55):
    CUES.append(("pas", round(float(t), 3), 0.45))
for t in np.arange(24.4, 28.7, 1.0):
    CUES.append(("pas", round(float(t), 3), 0.5))
# texte du Pokédex
for t in np.arange(30.9, 34.2, 0.45):
    CUES.append(("texte", round(float(t), 3), 0.7))
# les flammes s'allument rangée par rangée
for r in range(6):
    CUES.append(("allume", round(35.7 + r * 0.32, 3), 0.6))
# cœur : s'accélère après « Grosse erreur », puis ralentit et s'arrête dans la chaleur
beats = list(np.arange(21.4, 34.5, 0.8)) + list(np.arange(34.8, 41.9, 0.62)) + [42.1, 43.0, 44.2, 45.8]
CUES += [("coeur", round(float(t), 3), 0.8) for t in beats]


def rain_bed():
    """Pluie continue, même niveau au début et à la fin (raccord de boucle inaudible)."""
    n = int(SR * TOTAL)
    x = fastlp(rng.uniform(-1, 1, n), 3500) - fastlp(rng.uniform(-1, 1, n), 300) * 0.5
    drops = np.zeros(n)
    for o in rng.integers(0, n - 200, 1800):
        drops[o:o + 200] += np.exp(-np.arange(200) / 40) * rng.uniform(-1, 1)
    x = x / np.max(np.abs(x)) + fastlp(drops, 5000) * 0.6
    t = np.arange(n) / SR
    g = np.interp(t, [0, 28.5, 28.9, 34.4, 34.8, 40.3, 40.6, 46.2, 46.6, 51.74], [0.22, 0.22, 0.06, 0.06, 0.22, 0.22, 0.05, 0.05, 0.22, 0.22])
    return x * g


def drone_bed():
    """Grondement sous-grave cyclique (période = durée totale → boucle parfaite)."""
    n = int(SR * TOTAL)
    t = np.arange(n) / SR
    f0 = 55
    x = sum(np.sin(2 * np.pi * round(f * TOTAL) / TOTAL * t) / (i + 1) for i, f in enumerate((f0, f0 * 1.5, f0 * 2.01)))
    g = np.interp(t, [0, 10, 21, 34.5, 41.9, 46.3, 51.74], [0.06, 0.08, 0.12, 0.14, 0.03, 0.05, 0.06])
    return x * g * 0.7


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
    stem = rain_bed() + drone_bed()
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
