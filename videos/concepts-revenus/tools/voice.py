#!/usr/bin/env python3
"""Monte la voix (2 fichiers) en une seule piste de la durée exacte de la vidéo + transcript.json.

- les deux prises sont mises bout à bout, avec une respiration entre les deux (et des pauses si PAUSES en liste) ;
  la somme des pauses est calculée pour que la voix dure exactement 31 mesures de la musique (76,25 s) :
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
TOTAL = 76.252  # 31 mesures de la musique (97,6 BPM) : la boucle retombe sur un premier temps
P1_TRIM = 0.0
P1_END = 47.62  # fin de « Tout revient. » (la prise continue sur « La preuve… », reprise en partie 2)
P2_END = 25.85  # fin de « Tu sais ce que ça veut dire ? »

# pauses ajoutées (partie, temps dans la prise, durée) ; la pause entre les deux parties prend le reste
PAUSES = [
    (1, 4.86, 0.3),    # « Rappel express. » … Makima
    (1, 16.70, 0.3),   # « Effacés du monde. » … « Elle est la seule »
    (1, 18.57, 0.3),   # « …s'en souvenir. » … « Et dans le lot »
    (1, 35.22, 0.35),  # « …ressemblaient. » … « Sauf que… »
    (1, 38.00, 0.3),   # « …lui-même. » … « Un univers »
    (2, 12.00, 0.3),   # « ça donne quoi ? » …
]

P1_SEGMENTS = [
    ("Trois peurs qui avaient disparu de Chainsaw Man viennent de revenir.", 0.08, 3.10),
    ("Et personne en parle.", 3.22, 3.95),
    ("Rappel express.", 4.00, 4.72),
    ("Makima l'a dit à Kishibe :", 5.00, 6.32),
    ("Chainsaw Man a dévoré les nazis.", 6.71, 8.47),
    ("La Deuxième Guerre mondiale.", 8.80, 10.09),
    ("Le sida.", 10.42, 11.05),
    ("La SOA.", 11.12, 11.61),
    ("Le syndrome d'Arnolone.", 11.84, 13.09),
    ("L'éruption du mont Hio.", 13.32, 14.38),
    ("Les armes nucléaires.", 14.62, 15.75),
    ("Effacés du monde.", 15.86, 16.53),
    ("Elle est la seule à s'en souvenir.", 16.86, 18.32),
    ("Et dans le lot, y a trois trucs que personne a jamais expliqués.", 18.82, 22.03),
    ("Un sixième sens que les humains avaient.", 22.46, 24.21),
    ("Une étoile dont la lumière brisait l'esprit des enfants.", 24.93, 27.42),
    ("Et quatre autres voies que la mort, quand une vie se termine.", 28.12, 30.85),
    ("Trois peurs tellement énormes que le manga nous a jamais montré à quoi elles ressemblaient.", 31.16, 35.01),
    ("Sauf que…", 35.44, 36.01),
    ("Pochita s'est mangé lui-même.", 36.45, 37.72),
    ("« Un univers où je n'aurai jamais existé. »", 38.28, 40.54),
    ("Pas de Héros de l'Enfer, donc personne pour les avaler.", 41.12, 43.95),
    ("Les nazis, la guerre, les bombes…", 44.00, 45.79),
    ("et nos trois mystères.", 46.00, 46.84),
    ("Tout revient.", 47.12, 47.56),
]

P2_SEGMENTS = [
    ("La preuve ?", 0.00, 0.75),
    ("Dans le dernier chapitre, on reparle de la mort.", 1.23, 3.48),
    ("Si les gens y pensent, c'est qu'ils l'ont pas oubliée.", 3.80, 6.15),
    ("Elle existe à nouveau.", 6.76, 7.58),
    ("Et si elle est revenue… les autres aussi.", 8.11, 9.84),
    ("Concrètement, ça donne quoi ?", 10.47, 11.78),
    ("Quelque part dans le nouveau monde, y a des humains qui ont un sens en plus.", 12.23, 15.47),
    ("Une étoile qui brille à nouveau au-dessus des gosses.", 15.73, 18.13),
    ("Et des gens qui meurent… avec quatre autres portes de sortie.", 18.51, 21.57),
    ("Et Chainsaw Man est plus là pour les bouffer.", 22.18, 24.09),
    ("Tu sais ce que ça veut dire ?", 24.87, 25.80),
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
