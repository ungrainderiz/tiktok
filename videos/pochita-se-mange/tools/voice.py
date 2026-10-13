#!/usr/bin/env python3
"""Monte la voix (2 fichiers) en une seule piste de la durée exacte de la vidéo + transcript.json.

- les deux prises sont mises bout à bout, avec une respiration entre les deux (et des pauses si PAUSES en liste) ;
  la somme des pauses est calculée pour que la voix dure exactement 28 mesures de la musique (68,87 s) :
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
TOTAL = 68.873  # 28 mesures de la musique (97,6 BPM) : la boucle retombe sur un premier temps
P1_TRIM = 0.0
P1_END = 42.95  # fin de « non plus. »
P2_END = 23.55  # fin de « j'te le dis : »

# pauses ajoutées (partie, temps dans la prise, durée) ; la pause entre les deux parties prend le reste
PAUSES = [
    (1, 16.52, 0.5),   # « la tronçonneuse. » … « Sauf que… »
    (1, 21.44, 0.45),  # « Pochita se dévore lui-même. » … bam
    (2, 12.82, 0.45),  # « C'est la peur de CHAINSAW MAN. » …
]

P1_SEGMENTS = [
    ("Pochita s'est mangé lui-même.", 0.02, 1.33),
    ("Et ça prouve que tout le monde se trompait sur lui depuis le début.", 1.71, 4.23),
    ("Petit rappel.", 4.67, 5.22),
    ("Quand Pochita mange un démon, ce que ce démon représente disparaît.", 5.56, 8.75),
    ("Du monde.", 9.01, 9.61),
    ("Et de toutes les mémoires.", 10.07, 11.05),
    ("Alors la vraie question, c'est : Pochita, c'est le démon de QUOI ?", 11.43, 13.94),
    ("La réponse évidente : la tronçonneuse.", 14.23, 16.27),
    ("Sauf que…", 16.78, 17.24),
    ("Ok.", 17.66, 18.03),
    ("Maintenant on regarde les preuves.", 18.53, 19.95),
    ("Pochita se dévore lui-même.", 19.98, 21.26),
    ("Bam. Le monde est réécrit.", 21.62, 22.45),
    ("Première preuve : les tronçonneuses.", 22.50, 23.95),
    ("Dans le nouveau monde, elles existent toujours.", 24.21, 25.74),
    ("Partout.", 25.98, 26.24),
    ("Comme si de rien n'était.", 26.57, 27.45),
    ("Donc c'était PAS la peur des tronçonneuses.", 27.73, 29.71),
    ("Deuxième preuve :", 30.03, 30.76),
    ("l'oubli.", 31.11, 31.51),
    ("Certains disaient que Pochita, c'était le démon de l'Oubli.", 31.91, 34.59),
    ("Sauf que s'il avait mangé l'oubli,", 34.99, 36.57),
    ("plus personne pourrait oublier quoi que ce soit.", 36.90, 38.51),
    ("Et dans le nouveau monde ?", 38.79, 39.65),
    ("Tout le monde a oublié l'ancien.", 40.19, 41.37),
    ("Donc c'est pas l'oubli non plus.", 41.69, 42.93),
]

P2_SEGMENTS = [
    ("Alors qu'est-ce qui a disparu ?", 0.02, 1.16),
    ("Une seule chose.", 1.39, 2.19),
    ("Chainsaw Man.", 2.73, 3.69),
    ("Le Héros de l'Enfer. Celui que les démons appellent quand ils vont mourir…", 4.08, 7.42),
    ("et qui vient tous les massacrer.", 7.78, 8.86),
    ("Pochita, c'est pas la peur des tronçonneuses.", 9.66, 11.15),
    ("C'est la peur de CHAINSAW MAN.", 11.22, 12.57),
    ("Les démons avaient tellement peur de lui…", 13.08, 14.42),
    ("que leur peur l'a fait exister.", 14.71, 16.02),
    ("Un démon né de la peur qu'il inspire.", 16.43, 18.09),
    ("Qui disparaît en se dévorant lui-même.", 18.52, 20.23),
    ("Comme un serpent qui se mord la queue.", 20.74, 22.09),
    ("Et c'est pour ça que j'te le dis :", 22.55, 23.51),
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
