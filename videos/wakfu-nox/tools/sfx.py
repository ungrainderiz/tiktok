#!/usr/bin/env python3
"""Bruitages synthétisés de la vidéo Wakfu (tic-tac, forêt, Noxine, wakfu, rembobinage) + piste mixée.

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
TOTAL = 77.61
rng = np.random.default_rng(2020)  # graine fixe : rendu identique à chaque build


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


def s_tic(pitch=1.0):  # tic d'horloge : clic métallique sec
    d = 0.09
    t = t_axis(d)
    click = lowpass(noise(d), 6000) * np.exp(-t / 0.006)
    ring = np.sin(2 * np.pi * 2350 * pitch * t) * np.exp(-t / 0.02) * 0.6 + np.sin(2 * np.pi * 3900 * pitch * t) * np.exp(-t / 0.012) * 0.3
    return norm(click + ring, 0.8)


def s_tac():
    return s_tic(0.78)


def s_tic_grave():  # tic de l'horloge géante (énorme, avec queue grave)
    d = 0.7
    t = t_axis(d)
    click = fastlp(noise(d), 3000) * np.exp(-t / 0.01)
    body = np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.18) + np.sin(2 * np.pi * 1180 * t) * np.exp(-t / 0.05) * 0.3
    return norm(click + body, 0.9)


def s_oiseaux():  # piaillements de forêt (8 s)
    d = 8.0
    x = np.zeros(int(SR * d))
    for k in range(34):
        o = rng.uniform(0, d - 0.3)
        cd = rng.uniform(0.06, 0.16)
        t = t_axis(cd)
        f0 = rng.uniform(2600, 4200)
        sweep = f0 * (1 + 0.35 * np.sin(2 * np.pi * rng.uniform(18, 30) * t))
        c = np.sin(2 * np.pi * np.cumsum(sweep) / SR) * np.sin(np.pi * t / cd)
        i = int(o * SR)
        x[i:i + len(c)] += c * rng.uniform(0.3, 1)
    return norm(x, 0.5)


def s_vent():  # vent doux dans les feuilles
    d = 7.5
    t = t_axis(d)
    x = fastlp(noise(d), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t)) * np.clip(t / 0.5, 0, 1) * np.clip((d - t) / 1.2, 0, 1)
    return norm(x, 0.5)


def s_choeur():  # les arbres chantent : « aaah » grave (accord majeur)
    d = 1.2
    t = t_axis(d)
    x = sum(sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3)) for f in (196, 247, 294))
    x *= (1 + 0.08 * np.sin(2 * np.pi * 5.5 * t))
    return norm(fastlp(x, 1400) * np.clip(t / 0.15, 0, 1) * np.clip((d - t) / 0.3, 0, 1), 0.6)


def s_rire():  # les arbres rigolent : « ho ho ho » boisé
    out = []
    for k in range(4):
        d = 0.14
        t = t_axis(d)
        out += [np.sin(2 * np.pi * (150 - k * 8) * t) * np.sin(np.pi * t / d) + fastlp(noise(d), 600) * 0.3 * np.sin(np.pi * t / d), silence(0.08)]
    return norm(seq(*out), 0.6)


def s_texte():  # bulle de dialogue
    out = []
    for i in range(14):
        out += [square(740 if i % 2 else 830, 0.018, 0.25) * 0.6, silence(0.068)]
    return norm(seq(*out), 0.25)


def s_bzz():  # Noxine en vol : moteur d'horlogerie + battements d'ailes
    d = 1.2
    t = t_axis(d)
    wings = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t))
    x = square(np.full(len(t), 190.0) * (1 + 0.04 * np.sin(2 * np.pi * 7 * t)), d, 0.3) * wings
    gear = (np.sin(2 * np.pi * 40 * t) > 0.95) * lowpass(noise(d), 5000) * 0.6
    return norm(fastlp(x, 2400) + gear, 0.45)


def s_brille():  # reflet métallique : scintillement
    d = 0.5
    t = t_axis(d)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-np.clip(t - o, 0, None) / 0.08) * (t >= o) for f, o in ((2637, 0), (3520, 0.06), (4186, 0.12)))
    return norm(x, 0.4)


def s_carte():  # fiche du bestiaire qui s'ouvre
    return norm(seq(square(660, 0.05, 0.5), square(990, 0.05, 0.5), square(1320, 0.12, 0.5) * env(0.12)), 0.4)


def s_pique():  # piqûre : clic aigu + petit choc
    d = 0.4
    t = t_axis(d)
    x = np.sin(2 * np.pi * np.geomspace(5000, 1800, len(t)) * t) * np.exp(-t / 0.03) + fastlp(noise(d), 4000) * np.exp(-t / 0.015)
    thump = np.sin(2 * np.pi * 80 * t) * np.exp(-t / 0.06)
    return norm(x + thump * 0.6, 0.8)


def s_givre():  # froid : craquements de givre + souffle glacé
    d = 1.8
    x = np.zeros(int(SR * d))
    for _ in range(30):
        o = int(rng.uniform(0, d - 0.03) * SR)
        x[o:o + 400] += rng.uniform(-1, 1, 400) * np.exp(-np.arange(400) / 60) * rng.uniform(0.3, 1)
    t = t_axis(d)
    wind = fastlp(noise(d), 2500) * np.clip(t / 0.8, 0, 1) * 0.5
    return norm(lowpass(x, 8000) * 0.7 + wind * np.clip((d - t) / 0.4, 0, 1), 0.5)


def s_wakfu(d=5.5):  # fil de wakfu : nappe scintillante qui monte
    t = t_axis(d)
    f = 440 * (1 + 0.5 * t / d)
    x = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in (1, 1.5, 2.01, 3))
    shimmer = fastlp(noise(d), 9000) - fastlp(noise(d), 3000)
    sh = np.clip(t / 0.6, 0, 1) * np.clip((d - t) / 0.6, 0, 1)
    return norm((x * 0.6 + shimmer * 0.4) * sh * (1 + 0.15 * np.sin(2 * np.pi * 6 * t)), 0.45)


def s_banniere():  # bannière de zone
    d = 1.4
    t = t_axis(d)
    x = sum(tri(f, d) for f in (293.7, 440, 587.3)) * env(d, attack=0.02, sustain_curve=2.5)
    return norm(x, 0.5)


def s_boom():  # impact grave
    d = 2.0
    t = t_axis(d)
    sub = np.sin(2 * np.pi * np.cumsum(np.geomspace(75, 30, len(t))) / SR) * np.exp(-t / 0.6)
    hit = fastlp(noise(d), 1000) * np.exp(-t / 0.07) * 3
    return norm(sub + hit, 0.95)


def s_grondement(d=2.4):  # l'horloge se lève / tout est aspiré
    t = t_axis(d)
    x = fastlp(noise(d), 220) * (1 + 0.5 * np.sin(2 * np.pi * 7 * t)) * np.clip(t / (d * 0.7), 0, 1) ** 1.5
    return norm(x * np.clip((d - t) / 0.15, 0, 1), 0.8)


def s_rembobine():  # remonter le temps : bande qui rembobine
    d = 1.2
    t = t_axis(d)
    f = np.geomspace(300, 2400, len(t))
    x = square(f, d, 0.5) * 0.3 + fastlp(noise(d), 3000) * 0.5
    chirps = np.sign(np.sin(2 * np.pi * np.cumsum(np.geomspace(8, 40, len(t))) / SR)) * 0.2
    return norm(crush(x * (0.7 + chirps), 3, 6) * np.clip((d - t) / 0.1, 0, 1), 0.55)


def s_compteur():
    out = []
    for i in range(14):
        out += [square(880 + i * 30, 0.015, 0.25), silence(0.035)]
    return norm(seq(*out), 0.3)


def s_souvenir():  # boîte à musique triste
    notes = [659.3, 587.3, 523.3, 493.9, 440.0]
    out = []
    for f in notes:
        d = 0.42
        t = t_axis(d)
        out.append((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)) * np.exp(-t / 0.25))
    return norm(seq(*out), 0.4)


def s_aspiration():  # TOUT : aspiration ascendante
    d = 2.6
    t = t_axis(d)
    x = fastlp(noise(d), 1500) * (t / d) ** 0.5 * np.clip((d - t) / 0.2, 0, 1)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(80, 400, len(t))) / SR) * 0.5
    return norm(x + tone * (t / d), 0.8)


def s_craque():  # bois qui craque
    d = 0.6
    x = np.zeros(int(SR * d))
    for k in range(12):
        o = int((k * 0.035 + rng.uniform(0, 0.02)) * SR)
        x[o:o + 300] += rng.uniform(-1, 1, 300) * np.exp(-np.arange(300) / 50)
    t = t_axis(d)
    return norm(fastlp(x, 3500) + np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.1) * 0.5, 0.85)


def s_poussiere():  # effritement
    d = 1.6
    t = t_axis(d)
    x = (fastlp(noise(d), 6000) - fastlp(noise(d), 1500)) * (rng.random(len(t)) > 0.6)
    return norm(x * np.exp(-t / 0.8), 0.5)


def s_pierre():  # la main devient grise : frottement minéral
    d = 1.2
    t = t_axis(d)
    return norm(fastlp(noise(d), 700) * (0.5 + 0.5 * (rng.random(len(t)) > 0.97).astype(float)) * np.sin(np.pi * t / d), 0.5)


def s_engrenage():  # l'horloge se met à tourner : gros clonk d'engrenage
    d = 0.9
    t = t_axis(d)
    x = square(70, d, 0.4) * np.exp(-t / 0.15) * 0.6 + fastlp(noise(d), 2500) * np.exp(-t / 0.03)
    return norm(x, 0.85)


def s_tourbillon():  # à l'envers : tourbillon qui accélère (2,4 s)
    d = 2.4
    t = t_axis(d)
    x = fastlp(noise(d), 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(np.geomspace(2, 14, len(t))) / SR))
    return norm(x * (t / d), 0.7)


def s_coupe():  # coupe sèche sur plan gris
    d = 0.7
    t = t_axis(d)
    return norm(np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.2) + fastlp(noise(d), 800) * np.exp(-t / 0.05), 0.7)


SOUNDS = {
    "tic": s_tic, "tac": s_tac, "tic-grave": s_tic_grave, "oiseaux": s_oiseaux, "vent": s_vent, "choeur": s_choeur,
    "rire": s_rire, "texte": s_texte, "bzz": s_bzz, "brille": s_brille, "carte": s_carte, "pique": s_pique,
    "givre": s_givre, "wakfu": s_wakfu, "banniere": s_banniere, "boom": s_boom, "grondement": s_grondement,
    "rembobine": s_rembobine, "compteur": s_compteur, "souvenir": s_souvenir, "aspiration": s_aspiration,
    "craque": s_craque, "poussiere": s_poussiere, "pierre": s_pierre, "engrenage": s_engrenage,
    "tourbillon": s_tourbillon, "coupe": s_coupe,
}

# (son, temps global, gain)
CUES = [
    # horloge du début : un tic par seconde (le 1er à 0 s, juste après le dernier tic de la fin)
    ("tic-grave", 0.0, 0.5), ("tic-grave", 1.0, 0.4), ("tic-grave", 2.0, 0.4), ("tic-grave", 3.0, 0.4),
    ("tic", 4.08, 1.0), ("tac", 4.99, 1.0),
    ("vent", 5.25, 0.6), ("oiseaux", 5.3, 0.7), ("choeur", 8.8, 0.7), ("rire", 9.98, 0.7), ("texte", 10.75, 0.8),
    ("tic", 14.19, 0.9), ("tac", 14.9, 0.9), ("brille", 14.95, 0.6),
    ("bzz", 15.6, 0.7), ("bzz", 16.8, 0.35), ("bzz", 18.0, 0.35), ("bzz", 19.2, 0.35), ("bzz", 20.4, 0.35),
    ("brille", 17.9, 0.7), ("carte", 21.6, 0.8), ("tic", 22.6, 0.6), ("tac", 23.0, 0.6),
    ("pique", 23.72, 1.0), ("givre", 25.4, 0.8),
    ("bzz", 27.65, 0.5), ("wakfu", 28.4, 0.7),
    ("wakfu", 33.95, 0.6), ("banniere", 40.2, 0.6), ("grondement", 40.5, 0.4),
    ("boom", 44.64, 0.9), ("grondement", 46.5, 0.8), ("tic-grave", 47.0, 0.6), ("tic-grave", 48.0, 0.6),
    ("rembobine", 50.7, 0.8), ("compteur", 52.0, 0.8), ("souvenir", 53.36, 0.6),
    ("wakfu", 54.75, 0.7), ("boom", 57.59, 1.0), ("aspiration", 57.65, 0.9),
    ("craque", 62.73, 1.0), ("poussiere", 63.46, 0.8), ("pierre", 65.0, 0.7),
    ("tic-grave", 66.72, 0.7), ("tic-grave", 67.22, 0.6), ("tic-grave", 67.72, 0.5), ("engrenage", 68.04, 0.9),
    ("tourbillon", 69.9, 0.8), ("grondement", 70.0, 0.6),
    ("coupe", 72.43, 0.8), ("coupe", 73.46, 0.8), ("coupe", 74.62, 0.9),
]
# horloge qui recule puis ralentit jusqu'au raccord : tics de plus en plus espacés, le dernier ~0,5 s avant la fin
for k in range(26):
    t = 70.2 + 2.1 * (k / 26) ** 0.7
    CUES.append(("tic", round(t, 3), 0.5))
p = 75.95
for k, gap in enumerate([0.08, 0.09, 0.11, 0.13, 0.15, 0.18, 0.2, 0.22]):
    p += gap
    CUES.append(("tic-grave" if k > 4 else "tic", round(p, 3), 0.5))


def bed():
    """Grondement sous-grave cyclique (période = durée totale → boucle parfaite), plus fort quand ça tourne mal."""
    n = int(SR * TOTAL)
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * round(f * TOTAL) / TOTAL * t) / (i + 1) for i, f in enumerate((49, 73.5, 98.3)))
    g = np.interp(t, [0, 5, 12.5, 15, 27, 42, 54, 57.6, 60, 66, 72, 77.61], [0.05, 0.03, 0.02, 0.06, 0.08, 0.1, 0.1, 0.14, 0.12, 0.1, 0.08, 0.05])
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
