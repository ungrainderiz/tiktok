#!/usr/bin/env python3
"""Aligne le texte exact (SCRIPT.md) sur les mots horodatés de Whisper tiny → transcript.json.

Whisper tiny se trompe sur beaucoup de mots (« Funécire » → « finit »), mais ses horodatages sont bons :
on aligne les deux suites de mots (difflib) et on interpole les mots non reconnus.
"""
import difflib, json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINDOWS = [("wA.json", 0.0), ("wB.json", 25.55), ("wC.json", 42.12)]  # fenêtres transcrites séparément


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def main(asr_dir):
    heard = []
    for f, off in WINDOWS:
        for c in json.load(open(os.path.join(asr_dir, f)))["chunks"]:
            a, b = c["timestamp"]
            heard.append((c["text"].strip(), off + a, off + (b if b is not None else a + 0.3)))
    text = open(os.path.join(ROOT, "SCRIPT.md"), encoding="utf-8").read().split("\n", 2)[2].split("\n> ")[0]
    words = [w for w in re.split(r"\s+", text.replace("«", "").replace("»", "")) if w.strip()]
    A = [norm(w) for w in words]
    B = [norm(h[0]) for h in heard]
    times = [None] * len(words)
    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = (heard[blk.b + k][1], heard[blk.b + k][2])
    # interpolation des mots non reconnus, au prorata du nombre de lettres
    i = 0
    while i < len(words):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(words) and times[j] is None:
            j += 1
        t0 = times[i - 1][1] if i > 0 else 0.05
        t1 = times[j][0] if j < len(words) else heard[-1][2]
        span = words[i:j]
        tot = sum(len(w) + 1 for w in span)
        t = t0
        for k, w in enumerate(span):
            d = (t1 - t0) * (len(w) + 1) / tot
            times[i + k] = (t, t + d * 0.9)
            t += d
        i = j
    # 2e fichier audio : Whisper rate le début et la fin → on cale chaque phrase sur les silences de la voix
    P2 = 42.12
    SEGMENTS = [(0.02, 0.84), (1.28, 3.94), (4.37, 5.74), (6.22, 8.53), (9.02, 9.62)]
    PHRASES = ["Tu sens plus ton corps.", "Juste la chaleur. Et pour la première fois depuis des heures, t'as plus peur.",
               "Parce que maintenant, toi aussi, tu brilles.", "Et en bas du chemin, un dresseur perdu, trempé, épuisé…",
               "lève les yeux."]
    k0 = len(words) - sum(len(p.split()) for p in PHRASES)
    k = k0
    for (a, b), ph in zip(SEGMENTS, PHRASES):
        pw = ph.split()
        tot = sum(len(w) + 1 for w in pw)
        t = P2 + a
        for w in pw:
            d = (b - a) * (len(w) + 1) / tot
            assert norm(words[k]) == norm(w), (words[k], w)
            times[k] = (t, t + d * 0.9)
            t += d
            k += 1
    out = [{"text": w, "type": "word", "start": round(s, 3), "end": round(max(e, s + 0.05), 3)} for w, (s, e) in zip(words, times)]
    json.dump({"words": out}, open(os.path.join(ROOT, "transcript.json"), "w"), ensure_ascii=False, indent=1)
    matched = sum(1 for blk in sm.get_matching_blocks() for _ in range(blk.size))
    print(f"{len(words)} mots, {matched} reconnus par Whisper, {len(words) - matched} interpolés")


if __name__ == "__main__":
    main(sys.argv[1])
