#!/usr/bin/env python3
"""Assets pixel art du décor (style Pokémon Noir/Blanc de nuit, dans le brouillard).

- planches de sprites : chaque GIF animé officiel → PNG horizontal + sprites.json (images, durée)
  (un GIF s'anime à l'horloge du navigateur : non déterministe au rendu, donc on l'anime nous-mêmes) ;
- décor dessiné ici, pixel par pixel : sol, chemin, sapins, tombes, Tour Céleste, dresseur au loin.
Tout est agrandi en « nearest » pour garder des pixels nets.
"""
import json
import os

import numpy as np
from PIL import Image, ImageSequence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = os.path.join(ROOT, "assets", "sprites")
DECOR = os.path.join(ROOT, "assets", "decor")
rng = np.random.default_rng(607)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def save(arr, name, scale):
    im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(os.path.join(DECOR, name))
    return im.size


def sheets():
    meta = {}
    for f in sorted(os.listdir(SP)):
        if not f.endswith("-anim.gif"):
            continue
        im = Image.open(os.path.join(SP, f))
        frames, durs = [], []
        for fr in ImageSequence.Iterator(im):
            frames.append(fr.convert("RGBA").copy())
            durs.append(fr.info.get("duration", 60) or 60)
        w, h = frames[0].size
        sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
        for i, fr in enumerate(frames):
            sheet.paste(fr, (i * w, 0))
        name = f.replace("-anim.gif", "-sheet.png")
        sheet.save(os.path.join(SP, name))
        meta[name] = {"w": w, "h": h, "frames": len(frames), "ms": round(sum(durs) / len(durs))}
    json.dump(meta, open(os.path.join(SP, "sprites.json"), "w"), indent=1)
    return meta


def ground():
    """Herbe de nuit, tuile 32x32 (se répète sans couture)."""
    base = np.array(hexrgb("#14281f"))
    a = np.zeros((32, 32, 4))
    a[..., :3] = base
    a[..., 3] = 255
    for _ in range(70):
        x, y = rng.integers(0, 32, 2)
        c = hexrgb(["#1d3a2c", "#0e1d17", "#24452f"][rng.integers(0, 3)])
        a[y, x, :3] = c
        if rng.random() < 0.5:
            a[(y - 1) % 32, x, :3] = c
    return save(a, "herbe.png", 8)


def path():
    """Chemin de terre mouillée, tuile 32x32."""
    a = np.zeros((32, 32, 4))
    a[..., :3] = hexrgb("#3a3540")
    a[..., 3] = 255
    for _ in range(60):
        x, y = rng.integers(0, 32, 2)
        a[y, x, :3] = hexrgb(["#4a4452", "#2c2833", "#57505f"][rng.integers(0, 3)])
    for _ in range(6):  # flaques
        x, y = rng.integers(2, 28, 2)
        a[y:y + 2, x:x + 4, :3] = hexrgb("#2b3346")
        a[y, x + 1:x + 3, :3] = hexrgb("#41506a")
    return save(a, "chemin.png", 8)


def pine():
    """Sapin sombre 24x48 (billboard)."""
    a = np.zeros((48, 24, 4))
    dark, mid, edge = hexrgb("#0b1f19"), hexrgb("#12302a"), hexrgb("#1b4036")
    for tier in range(5):
        top = 2 + tier * 8
        for y in range(top, top + 12):
            half = int((y - top) * 0.9) + 2 + tier
            half = min(half, 11)
            for x in range(12 - half, 12 + half):
                a[y, x, :3] = mid if x < 12 else dark
                a[y, x, 3] = 255
            a[y, 12 - half, :3] = edge
    a[44:48, 10:14, :3] = hexrgb("#24181a")
    a[44:48, 10:14, 3] = 255
    return save(a, "sapin.png", 8)


def tomb(cross=False):
    """Tombe 16x22 (pierre grise mouillée)."""
    a = np.zeros((22, 16, 4))
    light, mid, dark = hexrgb("#8b93a3"), hexrgb("#626a7a"), hexrgb("#3f4554")
    if cross:
        a[0:22, 6:10, :3] = mid
        a[0:22, 6:10, 3] = 255
        a[5:9, 1:15, :3] = mid
        a[5:9, 1:15, 3] = 255
        a[0:22, 6, :3] = light
        a[5, 1:15, :3] = light
    else:
        for y in range(22):
            for x in range(16):
                r = 6
                if y < r and (x - 8) ** 2 + (y - r) ** 2 > 8 * 8:
                    continue
                a[y, x, :3] = mid
                a[y, x, 3] = 255
        a[2:22, 1:3, :3] = light
        a[8:9, 4:12, :3] = dark
        a[11:12, 5:11, :3] = dark
        a[14:15, 4:12, :3] = dark
    a[20:22, :, :3] = dark
    a[20:22, :, 3] = np.where(a[20:22, :, 3] > 0, 255, 0)
    return save(a, "tombe-croix.png" if cross else "tombe.png", 8)


def tower():
    """Tour Céleste au loin, 40x130, silhouette bleu nuit avec une fenêtre allumée."""
    a = np.zeros((130, 40, 4))
    body, rim, win = hexrgb("#1a2238"), hexrgb("#27304d"), hexrgb("#f6c56b")
    floors = [(0, 14, 10), (14, 34, 12), (34, 58, 14), (58, 86, 16), (86, 130, 18)]
    for y0, y1, half in floors:
        a[y0:y1, 20 - half:20 + half, :3] = body
        a[y0:y1, 20 - half:20 + half, 3] = 255
        a[y0:y0 + 2, 20 - half - 1:20 + half + 1, :3] = rim
        a[y0:y0 + 2, 20 - half - 1:20 + half + 1, 3] = 255
    a[0:4, 19:21, :3] = rim  # cloche au sommet
    a[4:9, 17:23, :3] = hexrgb("#3a4260")
    for y, x in [(22, 18), (44, 24), (70, 15), (100, 22)]:
        a[y:y + 3, x:x + 2, :3] = win if (y, x) == (22, 18) else hexrgb("#2f3858")
        a[y:y + 3, x:x + 2, 3] = 255
    return save(a, "tour-celeste.png", 6)


def trainer():
    """Dresseur au loin vu de face, 12x22, trempé, tête levée."""
    p = {
        ".": None, "c": "#b03a3a", "h": "#2a1f1c", "s": "#e2b58f", "e": "#1a1a1a",
        "j": "#355a8c", "J": "#27466e", "p": "#2b2b38", "b": "#151515", "k": "#d9d9d9",
    }
    rows = [
        "...cccccc...",
        "..cccccccc..",
        ".cccccccccc.",
        "..hhsssshh..",
        "..hseesesh..",
        "...ssssss...",
        "....ssss....",
        "..jjjkkjjj..",
        ".jjjjkkjjjj.",
        ".jJjjjjjjJj.",
        ".jJjjjjjjJj.",
        ".sJjjjjjjJs.",
        "..jjjjjjjj..",
        "..pppppppp..",
        "..ppp..ppp..",
        "..ppp..ppp..",
        "..ppp..ppp..",
        "..ppp..ppp..",
        "..bbb..bbb..",
        ".bbbb..bbbb.",
        "............",
        "............",
    ]
    a = np.zeros((22, 12, 4))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if p[ch]:
                a[y, x, :3] = hexrgb(p[ch])
                a[y, x, 3] = 255
    return save(a, "dresseur.png", 8)


def face():
    """Visage fantôme pâle (yeux creux, bouche ouverte) qu'on voit dans les flammes, 10x12."""
    rows = [
        "...wwww...",
        "..wwwwww..",
        ".wwwwwwww.",
        ".ww..ww..w",
        ".ww..ww..w",
        ".wwwwwwww.",
        ".wwwwwwww.",
        "..ww..ww..",
        "..ww..ww..",
        "...wwww...",
        "....ww....",
        "..........",
    ]
    a = np.zeros((12, 10, 4))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "w":
                a[y, x] = (*hexrgb("#e8f3ff"), 230)
    return save(a, "visage.png", 8)


def main():
    os.makedirs(DECOR, exist_ok=True)
    meta = sheets()
    out = {
        "herbe": ground(), "chemin": path(), "sapin": pine(), "tombe": tomb(), "tombe-croix": tomb(True),
        "tour": tower(), "dresseur": trainer(), "visage": face(),
    }
    print(json.dumps(meta))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
