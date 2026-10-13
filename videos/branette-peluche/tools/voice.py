#!/usr/bin/env python3
"""Monte la voix (2 fichiers) en une seule piste de la durée exacte de la vidéo + transcript.json.

- les deux prises sont mises bout à bout, avec une respiration entre les deux (et des pauses si PAUSES en liste) ;
  la somme des pauses est calculée pour que la voix dure exactement 3 tours de l'OST (77,61 s) :
  la dernière syllabe tombe sur la dernière image, et la musique repart en rythme au raccord de boucle ;
- horodatage : chaque phrase est calée à la main sur les plages de parole de la prise (silencedetect -40 dB,
  recoupé avec Whisper tiny), puis les mots sont répartis dans la phrase au prorata de leur nombre de lettres.
"""
import json
import os
import re
import subprocess
import unicodedata
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOIX = os.path.join(ROOT, "assets", "audio", "voix")
SR = 44100
TOTAL = 77.61  # 3 × 25,87 s (période de l'OST)
P1_TRIM = 0.0  # la 1re prise démarre directement sur la voix
P1_END = 57.70  # fin de « elle s'échappe. » (on coupe le souffle d'après)
P2_END = 18.91  # « …prendre l'air… » va jusqu'au bout de la 2e prise

PAUSES = []  # la seule respiration est entre les deux prises (≈ 1 s), calculée pour tomber pile sur 77,61 s

P1_SEGMENTS = [
    ("Y a une peluche devant ta porte.", 0.02, 1.64),
    ("Une petite poupée noire,", 2.37, 3.56),
    ("trempée,", 3.99, 4.54),
    ("avec une fermeture éclair à la place de la bouche.", 5.31, 7.68),
    ("Et tu la reconnais.", 8.23, 8.99),
    ("C'est la TIENNE.", 9.65, 10.29),
    ("Celle que t'avais à six ans.", 10.60, 11.70),
    ("Celle que tu serrais tous les soirs.", 11.90, 13.30),
    ("Celle que t'as jetée à la poubelle", 13.57, 15.04),
    ("le jour où t'as eu ton premier Pokémon.", 15.87, 17.60),
    ("Qui l'a ramenée ? Personne.", 17.91, 19.15),
    ("Un voisin.", 19.56, 20.03),
    ("Une blague.", 20.58, 21.05),
    ("Alors tu la jettes.", 21.45, 22.00),
    ("Dans la benne,", 22.12, 22.81),
    ("au bout de la rue.", 23.45, 24.15),
    ("Le lendemain matin…", 24.64, 25.48),
    ("elle est sur ton lit.", 26.33, 27.19),
    ("Assise.", 27.55, 28.02),
    ("Tournée vers toi.", 28.62, 29.29),
    ("Et la fermeture éclair est un tout petit peu plus ouverte.", 29.85, 32.62),
    ("Tu la brûles.", 32.62, 33.19),
    ("Tu l'enterres.", 33.42, 33.95),
    ("Tu la jettes dans la mer.", 34.10, 35.19),
    ("Chaque fois, elle revient.", 35.91, 37.26),
    ("Chaque fois, un cran de plus.", 37.77, 39.34),
    ("Alors tu sors ton Pokédex.", 39.90, 41.17),
    ("Tu la scannes.", 41.57, 42.15),
    ("Et l'écran affiche un nom :", 42.69, 43.77),
    ("Branette.", 44.22, 44.96),
    ("Une peluche abandonnée, rongée par la rancune.", 45.31, 47.11),
    ("Elle cherche l'enfant qui l'a jetée.", 48.01, 49.13),
    ("Et en dessous,", 49.62, 50.26),
    ("une ligne que t'aurais préféré pas lire :", 50.56, 52.29),
    ("sa bouche retient une énergie maudite.", 52.56, 54.54),
    ("Si la fermeture s'ouvre…", 55.10, 56.30),
    ("elle s'échappe.", 57.13, 57.62),
]

P2_SEGMENTS = [
    ("Tu regardes la poupée.", 0.02, 1.03),
    ("Il reste trois crans.", 1.60, 2.41),
    ("Cette nuit, tu dors pas. Tu la fixes.", 2.94, 4.84),
    ("Elle bouge pas.", 5.09, 5.67),
    ("Toi non plus.", 6.19, 6.66),
    ("Et à un moment…", 7.55, 8.18),
    ("tes yeux se ferment.", 8.72, 9.36),
    ("Quand tu te réveilles, elle est plus là.", 9.79, 11.05),
    ("Plus sur le lit.", 11.45, 12.02),
    ("Plus dans la chambre.", 12.27, 13.26),
    ("Nulle part.", 14.24, 14.77),
    ("Tu souffles.", 15.09, 15.60),
    ("C'est fini.", 15.86, 16.24),
    ("Alors tu ouvres ta porte pour aller prendre l'air…", 16.52, 18.85),
]


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def script_words():
    t = open(os.path.join(ROOT, "SCRIPT.md"), encoding="utf-8").read().split("## Texte")[1].split("## Boucle")[0]
    return [w for w in re.split(r"\s+", t) if w.strip()]


def spread(phrase, a, b):
    pw = phrase.split()
    tot = sum(len(w) + 1 for w in pw)
    out, t = [], a
    for w in pw:
        d = (b - a) * (len(w) + 1) / tot
        out.append((w, t, t + d * 0.9))
        t += d
    return out


def main():
    words = script_words()
    n1 = sum(len(p.split()) for p, _, _ in P1_SEGMENTS)
    w1, w2 = words[:n1], words[n1:]
    t1, t2 = [], []
    for segs, ts, ws in ((P1_SEGMENTS, t1, w1), (P2_SEGMENTS, t2, w2)):
        for p, a, b in segs:
            ts += [(s, e) for _, s, e in spread(p, a, b)]
        assert [norm(w) for w in ws] == [norm(w) for p, _, _ in segs for w in p.split()], "texte ≠ SCRIPT.md"

    a1 = decode(os.path.join(VOIX, "partie-1.mp3"))[int(P1_TRIM * SR): int(P1_END * SR)]
    a2 = decode(os.path.join(VOIX, "partie-2.mp3"))[: int(P2_END * SR)]
    fixed = sum(d for _, _, d in PAUSES)
    gap = TOTAL - len(a1) / SR - len(a2) / SR - fixed  # pause entre « TOUT. » et « Autour de toi »
    assert gap > 0.3, gap
    assert gap < 3, gap

    def place(part, t):  # temps dans la prise → temps dans la vidéo
        if part == 1:
            return t - P1_TRIM + sum(d for p, c, d in PAUSES if p == 1 and c <= t)
        return len(a1) / SR + sum(d for p, _, d in PAUSES if p == 1) + gap + t + sum(d for p, c, d in PAUSES if p == 2 and c <= t)

    out = np.zeros(int(round(TOTAL * SR)), dtype=np.float32)
    for part, audio, trim in ((1, a1, P1_TRIM), (2, a2, 0.0)):
        cuts = [0.0] + [c - trim for p, c, _ in PAUSES if p == part] + [len(audio) / SR]
        for a, b in zip(cuts, cuts[1:]):
            seg = audio[int(a * SR): int(b * SR)]
            o = int(round(place(part, a + trim + 1e-6) * SR))
            out[o: o + len(seg)] += seg[: len(out) - o]
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(VOIX, "voix.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

    # la voix clonée sort basse (≈ -27 LUFS) : gain linéaire vers -20 LUFS + écrêtage doux des crêtes
    # (pas de loudnorm : il raccourcit la piste de ~0,1 s et décalerait la fin de la boucle)
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", os.path.join(VOIX, "voix.wav"), "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", meas)[-1])
    g = 10 ** ((-20 - lufs) / 20)
    x = out * g
    x = np.where(np.abs(x) > 0.85, np.sign(x) * (0.85 + 0.14 * np.tanh((np.abs(x) - 0.85) / 0.14)), x)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(VOIX, "voix.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

    res = []
    for part, ws, ts in ((1, w1, t1), (2, w2, t2)):
        for w, (s, e) in zip(ws, ts):
            s2, e2 = place(part, s), place(part, e)
            res.append({"text": w, "type": "word", "start": round(s2, 3), "end": round(max(e2, s2 + 0.05), 3)})
    json.dump({"words": res}, open(os.path.join(ROOT, "transcript.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(words)} mots ; pause centrale {gap:.2f} s ; durée {len(out) / SR:.2f} s")


if __name__ == "__main__":
    main()
