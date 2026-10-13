#!/usr/bin/env python3
"""Monte la voix (2 fichiers) en une seule piste de la durée exacte de la vidéo + transcript.json.

- les deux prises sont mises bout à bout, avec des silences dramatiques ajoutés entre certaines phrases ;
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
P1_TRIM = 0.20  # on coupe le blanc du début : la voix démarre dès la 1re image
P2_END = 15.42  # fin de « offert… » dans la partie 2

# pauses ajoutées (partie, temps dans la prise, durée) ; la pause entre les deux parties prend le reste
PAUSES = [
    (1, 22.60, 0.8),  # Une Noxine. …
    (1, 26.00, 0.9),  # C'est juste… froid. …
    (1, 39.70, 1.1),  # … en haut de l'Arbre de Vie. …
    (1, 42.90, 0.7),  # Nox. …
    (2, 10.55, 1.4),  # À l'envers. …
    (2, 13.50, 0.6),  # Toi. …
]

P1_SEGMENTS = [
    ("Vingt minutes.", 0.27, 0.96),
    ("C'est le temps qu'il te reste.", 1.38, 3.93),
    ("Tic.", 4.28, 4.63),
    ("Tac.", 5.19, 5.45),
    ("T'es un petit Sadida, au fond de la forêt.", 5.50, 7.19),
    ("Ici, les arbres parlent.", 7.67, 8.63),
    ("Ils chantent,", 8.99, 9.69),
    ("ils rigolent, ils te racontent des histoires.", 10.18, 11.90),
    ("Sauf qu'aujourd'hui… ils se taisent.", 12.82, 14.12),
    ("Tic.", 14.39, 14.73),
    ("Tac.", 15.10, 15.40),
    ("Un truc se pose sur ta main.", 15.88, 17.03),
    ("Un insecte.", 17.41, 17.77),
    ("Sauf qu'il est en métal,", 18.06, 19.08),
    ("avec une petite horloge à la place du ventre.", 19.40, 21.40),
    ("Une Noxine.", 21.83, 22.42),
    ("Elle te pique.", 22.78, 23.41),
    ("Ça fait pas mal.", 23.88, 24.44),
    ("C'est juste… froid.", 24.73, 25.81),
    ("Et là, tu vois un fil bleu sortir de ta peau.", 26.17, 28.03),
    ("Ton wakfu.", 29.02, 29.51),
    ("Ta vie. Il s'envole.", 30.08, 30.96),
    ("Et il est pas tout seul.", 31.48, 32.26),
    ("Y en a des milliers.", 32.52, 33.19),
    ("Ils sortent des feuilles, des bêtes, de ta famille.", 33.46, 36.24),
    ("Et ils montent tous au même endroit : en haut de l'Arbre de Vie.", 36.73, 39.34),
    ("Là-haut, y a un vieux Xélor.", 40.07, 41.74),
    ("Nox.", 42.04, 42.62),
    ("Derrière lui, une horloge grande comme le ciel.", 43.22, 45.50),
    ("Tu sais ce qu'il veut, Nox ?", 45.88, 47.08),
    ("Remonter le temps.", 47.40, 48.09),
    ("Deux cents ans en arrière.", 48.71, 49.75),
    ("Revoir sa femme et ses gosses.", 50.06, 51.40),
    ("Et pour ça, il lui faut du wakfu.", 51.50, 53.03),
    ("Pas un peu.", 53.39, 53.77),
    ("TOUT.", 54.29, 54.70),
]

P2_SEGMENTS = [
    ("Autour de toi, les arbres deviennent gris.", 0.15, 2.08),
    ("Ils craquent.", 2.54, 3.09),
    ("Ils tombent en poussière.", 3.27, 4.10),
    ("Ta main aussi devient grise.", 4.36, 5.96),
    ("Tic… Tac…", 6.53, 6.84),
    ("Et puis l'horloge géante se met à tourner.", 7.85, 9.30),
    ("À l'envers.", 9.78, 10.28),
    ("Une forêt entière.", 10.84, 11.72),
    ("Un peuple entier.", 11.87, 12.64),
    ("Toi.", 13.03, 13.18),
    ("Et tout ce wakfu… ça lui a offert…", 13.98, 15.39),
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

    a1 = decode(os.path.join(VOIX, "partie-1.mp3"))[int(P1_TRIM * SR):]
    a2 = decode(os.path.join(VOIX, "partie-2.mp3"))[: int(P2_END * SR)]
    fixed = sum(d for _, _, d in PAUSES)
    gap = TOTAL - len(a1) / SR - len(a2) / SR - fixed  # pause entre « TOUT. » et « Autour de toi »
    assert gap > 0.3, gap

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
