#!/usr/bin/env python3
"""Sprites pixel art « HD » de la vidéo Wakfu, dessinés ici puis agrandis en nearest.

Références données par Matt : arbre pixel art en paquets de feuillage (6 verts, ombres presque noires,
pas de contour), Sadida du jeu (peau brune, cheveux-feuilles verts, bandages beiges), Noxine de la série
(boule de métal olive, carapace brune, piques noires, œil-cadran bleu), Nox (silhouette noire élancée,
yeux et cœur cyan, devant une horloge de pierre à chiffres romains, fond rouge).

Méthode : chaque forme est un masque ; on en tire un relief (distance au bord → profil arrondi), donc
une normale, éclairée par une lumière ; l'intensité est quantifiée sur une rampe de 4 à 6 couleurs avec
un léger tramage (Bayer 4×4) et une texture de « paquets » pour les feuillages. Rendu net, pixel par pixel.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter, zoom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sprites")
META = {}
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def ramp(*hexes):
    return [hexrgb(h) for h in hexes]


LEAF = ramp("#0e171c", "#0b3329", "#174f28", "#2b6e21", "#46901d", "#69b028")
LEAF_BACK = ramp("#0b1418", "#0a2b23", "#123f22", "#22591c", "#367519")
BARK = ramp("#1c1013", "#351d20", "#4f2c29", "#6d3f34", "#8a5640")
SKIN = ramp("#3b1d10", "#5e3119", "#814622", "#a35f30", "#c27d45")
WRAP = ramp("#5a4a33", "#857152", "#b09a73", "#d6c39a", "#efe2c0")
HAIR = ramp("#123512", "#24601a", "#3f8a1f", "#69b028", "#9ad23a")
STONE = ramp("#2c2833", "#47424f", "#68626f", "#8c8592", "#b3acb6", "#d2ccd3")
IRON = ramp("#0b0b10", "#1c1c26", "#30303e", "#4a4a5c", "#6c6c80")
NOX = ramp("#040509", "#0a0c13", "#12151f", "#1d2232", "#2d3550", "#46557a")
OLIVE = ramp("#151a10", "#262f1b", "#3a4628", "#526038", "#6f7f4c", "#9eac74")
CARAPACE = ramp("#1f1810", "#3a2d1c", "#54422a", "#6e5838", "#8a734c")
BLACK = ramp("#050505", "#121214", "#232327", "#3a3a40")
YELLOW = ramp("#6a4310", "#b07a18", "#e0a82a", "#f6cf45", "#fff08a")
WOOL = ramp("#7d7468", "#a99f90", "#cfc6b6", "#ece5d6", "#fffaf0")
SEPIA = ramp("#3a2a1a", "#5e4630", "#86684a", "#ad8d68", "#d4b78e")


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3))
        self.a = np.zeros((h, w))
        self.yy, self.xx = np.mgrid[0:h, 0:w] + 0.5

    # ----- masques
    def circle(self, cx, cy, r):
        return np.hypot(self.xx - cx, self.yy - cy) < r

    def ellipse(self, cx, cy, rx, ry, rot=0.0):
        c, s = math.cos(rot), math.sin(rot)
        x, y = self.xx - cx, self.yy - cy
        u, v = x * c + y * s, -x * s + y * c
        return (u / rx) ** 2 + (v / ry) ** 2 < 1

    def capsule(self, ax, ay, bx, by, ra, rb=None):
        rb = ra if rb is None else rb
        px, py = self.xx - ax, self.yy - ay
        dx, dy = bx - ax, by - ay
        t = np.clip((px * dx + py * dy) / max(1e-6, dx * dx + dy * dy), 0, 1)
        return np.hypot(px - t * dx, py - t * dy) < ra + (rb - ra) * t

    def poly(self, pts):
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
        return np.array(im) > 0

    def blob(self, cx, cy, r, rng, wobble=0.22, fringe=0.35):
        """Paquet de feuillage : cercle au bord irrégulier + franges de pixels."""
        ang = np.arctan2(self.yy - cy, self.xx - cx)
        rr = np.full(ang.shape, float(r))
        for f in (3, 5, 7, 11):
            rr += r * wobble / (f ** 0.6) * np.sin(f * ang + rng.uniform(0, 6.3))
        d = np.hypot(self.xx - cx, self.yy - cy)
        m = d < rr
        edge = (d >= rr - 1.5) & (d < rr + 1.5)
        flip = rng.random(m.shape) < fringe
        return (m & ~(edge & flip & (d > rr - 0.5))) | (edge & flip & (d < rr + 1))

    # ----- rendu ombré
    def shade(self, mask, rmp, thick=6.0, light=(-0.55, -0.8, 0.65), noise=0.0, clumps=0.0, seed=0,
              bias=0.0, ao=0.0, dither=0.6):
        if not mask.any():
            return
        rng = np.random.default_rng(seed)
        d = distance_transform_edt(mask)
        x = np.clip(d / thick, 0, 1)
        hgt = gaussian_filter(np.sqrt(1 - (1 - x) ** 2), 0.9)
        gy, gx = np.gradient(hgt)
        nx, ny, nz = -gx * thick, -gy * thick, np.ones_like(gx)
        n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        L = np.array(light, dtype=float)
        L /= np.linalg.norm(L)
        s = (nx * L[0] + ny * L[1] + nz * L[2]) / n
        s = 0.5 + 0.55 * s + bias
        if clumps:
            g = rng.random((self.h // 3 + 2, self.w // 3 + 2))
            g = zoom(g, 3, order=0)[: self.h, : self.w]
            s += (g - 0.5) * clumps
        if noise:
            s += (rng.random(s.shape) - 0.5) * noise
        if ao:
            ys = np.where(mask.any(axis=1))[0]
            y0, y1 = ys.min(), ys.max() + 1
            s -= ao * np.clip((self.yy - y0) / max(1, y1 - y0), 0, 1)
        k = len(rmp)
        s += BAYER[(self.yy.astype(int) % 4), (self.xx.astype(int) % 4)] * dither / k
        idx = np.clip((s * k).astype(int), 0, k - 1)
        cols = np.array(rmp)[idx]
        self.rgb[mask] = cols[mask]
        self.a[mask] = 255

    def fill(self, mask, col, alpha=255):
        self.rgb[mask] = hexrgb(col)
        self.a[mask] = alpha

    def image(self):
        out = np.dstack([self.rgb, self.a]).clip(0, 255).astype(np.uint8)
        return Image.fromarray(out, "RGBA")


def save(im, name, scale):
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    big.save(os.path.join(OUT, name))
    return big.size


def save_sheet(frames, name, scale, ms):
    w, h = frames[0].size
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    save(sheet, name, scale)
    META[name] = {"w": w * scale, "h": h * scale, "frames": len(frames), "ms": ms}


# ------------------------------------------------------------------ arbres
def tree(seed, W=120, H=210, crown=0.55, face=None, trunk_w=7.0):
    rng = np.random.default_rng(seed)
    c = Canvas(W, H)
    cx = W / 2
    base_y, top_y = H - 1, H * (1 - crown) - 4
    # tronc tordu : chaîne de capsules qui ondulent
    pts, x = [], cx + rng.uniform(-4, 4)
    for i in range(9):
        y = base_y - i * (base_y - top_y + 30) / 8
        pts.append((x, y))
        x += rng.uniform(-5, 5)
    trunk = np.zeros((H, W), bool)
    for i, ((ax, ay), (bx, by)) in enumerate(zip(pts, pts[1:])):
        trunk |= c.capsule(ax, ay, bx, by, trunk_w * (1 - i * 0.07) + 2, trunk_w * (1 - (i + 1) * 0.07) + 2)
    trunk |= c.poly([(cx - trunk_w * 2.6, base_y), (cx + trunk_w * 2.6, base_y), (cx + trunk_w, base_y - 16), (cx - trunk_w, base_y - 16)])
    for k in range(4):  # branches qui partent dans le feuillage
        bx0, by0 = pts[5 + k % 3]
        trunk |= c.capsule(bx0, by0, bx0 + rng.uniform(-30, 30), by0 - rng.uniform(18, 40), 3, 1.5)
    c.shade(trunk, BARK, thick=trunk_w, light=(-0.7, -0.3, 0.6), noise=0.25, seed=seed + 1, dither=0.8)
    # stries d'écorce
    for _ in range(int(H * 0.25)):
        y = int(rng.uniform(top_y + 30, base_y - 4))
        xs = np.where(trunk[y])[0]
        if len(xs) > 4:
            xx = int(rng.uniform(xs[1], xs[-2]))
            c.rgb[y:y + 3, xx] = BARK[0]
    if face is not None:
        face(c, cx, pts)
    # feuillage : paquets du fond (plus sombres) puis paquets de devant, du haut vers le bas
    k = W / 110  # les grands arbres ont des paquets plus gros et plus nombreux
    crown_r = W * 0.5 - 24 * k
    crown_cy = max(top_y + 10, crown_r * 0.85 + 18 * k)
    back, front = [], []
    for i in range(int(10 * k * k)):
        a = rng.uniform(0, math.tau)
        rr = crown_r * math.sqrt(rng.uniform(0.05, 1))
        back.append((cx + math.cos(a) * rr * 1.05, crown_cy + math.sin(a) * rr * 0.85 - 6, rng.uniform(13, 18) * k ** 0.6))
    for i in range(int(12 * k * k)):
        a = rng.uniform(0, math.tau)
        rr = crown_r * math.sqrt(rng.uniform(0, 1))
        front.append((cx + math.cos(a) * rr, crown_cy + math.sin(a) * rr * 0.8, rng.uniform(12, 17) * k ** 0.6))
    front.sort(key=lambda b: b[1])
    for (x, y, r) in back:
        c.shade(c.blob(x, y, r, rng), LEAF_BACK, thick=r * 0.9, light=(-0.4, -0.9, 0.45), noise=0.15, clumps=0.35, seed=int(x * 7 + y), bias=-0.2, ao=0.35)
    for (x, y, r) in front:
        low = (y - (crown_cy - crown_r)) / (2 * crown_r)
        c.shade(c.blob(x, y, r, rng), LEAF, thick=r * 0.85, light=(-0.4, -0.9, 0.45), noise=0.18, clumps=0.4, seed=int(x * 13 + y * 3), bias=0.12 - 0.5 * low, ao=0.4)
    return c.image()


def sadida_face(state):
    def draw(c, cx, pts):
        x, y = pts[2]
        y -= 4
        dark, glow = "#140a0c", "#d8ffb0"
        for ex in (x - 6, x + 6):
            if state == 2:
                c.fill(c.capsule(ex - 2.5, y, ex + 2.5, y + 1, 1.0), dark)
            else:
                c.fill(c.ellipse(ex, y, 3.2, 3.8), dark)
                c.fill(c.circle(ex + 0.6, y - 0.4, 1.4), glow)
        if state == 1:
            c.fill(c.ellipse(x, y + 10, 4, 5), dark)
            c.fill(c.ellipse(x, y + 12, 2.5, 2), "#5a2a24")
        elif state == 0:
            c.fill(c.capsule(x - 4, y + 8, x, y + 10, 0.9) | c.capsule(x, y + 10, x + 4, y + 8, 0.9), dark)
        else:
            c.fill(c.capsule(x - 3.5, y + 9, x + 3.5, y + 9, 0.9), dark)
    return draw


# ------------------------------------------------------------------ horloge de pierre à chiffres romains
GLYPH = {
    "I": ["11", "11", "11", "11", "11", "11", "11", "11", "11"],
    "V": ["11000011", "11000011", "11000011", "01100110", "01100110", "01100110", "00111100", "00111100", "00011000"],
    "X": ["11000011", "11000011", "01100110", "00111100", "00011000", "00111100", "01100110", "11000011", "11000011"],
}


def roman(n):
    return {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}[n]


def stamp(c, text, cx, cy, col):
    ws = [len(GLYPH[ch][0]) for ch in text]
    tw = sum(ws) + (len(ws) - 1)
    x = round(cx - tw / 2)
    y = round(cy - 4.5)
    for ch, w in zip(text, ws):
        for j, row in enumerate(GLYPH[ch]):
            for i, b in enumerate(row):
                if b == "1":
                    c.rgb[y + j, x + i] = hexrgb(col)
                    c.a[y + j, x + i] = 255
        x += w + 1


def clock():
    S = 220
    c = Canvas(S, S)
    m = S / 2
    c.shade(c.circle(m, m, 108), STONE, thick=10, noise=0.12, seed=1, bias=-0.15)
    c.shade(c.circle(m, m, 98), STONE, thick=4, noise=0.1, seed=2, bias=-0.35)
    c.shade(c.circle(m, m, 94), STONE, thick=60, noise=0.14, clumps=0.12, seed=3, bias=0.12)
    c.fill(c.circle(m, m, 76) & ~c.circle(m, m, 73), "#3a3540")
    c.fill(c.circle(m, m, 40) & ~c.circle(m, m, 38), "#47424f")
    for k in range(60):  # graduations des minutes
        a = k * math.tau / 60 - math.pi / 2
        r0 = 86 if k % 5 else 82
        for r in np.arange(r0, 92, 0.5):
            x, y = int(m + math.cos(a) * r), int(m + math.sin(a) * r)
            c.rgb[y, x] = hexrgb("#2c2833")
    for h in range(1, 13):  # chiffres romains, droits
        a = h * math.tau / 12 - math.pi / 2
        stamp(c, roman(h), m + math.cos(a) * 60, m + math.sin(a) * 60, "#26222c")
    # fissures dans la pierre
    rng = np.random.default_rng(5)
    for _ in range(4):
        a = rng.uniform(0, math.tau)
        x, y = m + math.cos(a) * 95, m + math.sin(a) * 95
        for _ in range(26):
            a += rng.uniform(-0.6, 0.6)
            x -= math.cos(a) * 1.2
            y -= math.sin(a) * 1.2
            c.rgb[int(y), int(x)] = hexrgb("#2c2833")
    save(c.image(), "horloge.png", 5)

    def hand(L, W, name, orn):
        w, h = int(W * 2 + 14), L + 30
        c2 = Canvas(w, h)
        px, py = w / 2, L + 4
        body = c2.poly([(px, 2), (px + W, 10), (px + W * 0.5, py), (px - W * 0.5, py), (px - W, 10)])
        body |= c2.circle(px, py, W + 1.5)
        body |= c2.capsule(px, py, px, py + 20, W * 0.6, W * 0.9)
        if orn:  # anneau ornemental près de la pointe (comme sur l'horloge de Nox)
            body |= c2.circle(px, 22, W + 3) & ~c2.circle(px, 22, W)
        c2.shade(body, IRON, thick=3, light=(-0.6, -0.5, 0.7), noise=0.1, seed=len(name))
        c2.fill(c2.circle(px, py, 2), "#9ea0b4")
        save(c2.image(), name, 5)
        META[name] = {"w": w * 5, "h": h * 5, "px": round(px * 5), "py": round(py * 5)}

    hand(50, 5, "aiguille-heure.png", True)
    hand(78, 4, "aiguille-minute.png", True)
    hand(84, 1.6, "aiguille-seconde.png", False)


def gear():
    S = 120
    c = Canvas(S, S)
    m = S / 2
    ang = np.arctan2(c.yy - m, c.xx - m)
    d = np.hypot(c.xx - m, c.yy - m)
    teeth = 50 + 7 * (np.cos(ang * 14) > 0.2)
    mask = (d < teeth) & (d > 16)
    for k in range(5):  # rayons évidés
        a = k * math.tau / 5
        mask &= ~(c.capsule(m + math.cos(a) * 24, m + math.sin(a) * 24, m + math.cos(a) * 36, m + math.sin(a) * 36, 6))
    c.shade(mask, IRON, thick=5, noise=0.1, seed=9)
    save(c.image(), "engrenage.png", 4)


# ------------------------------------------------------------------ Noxine (boule de métal, carapace, œil-cadran)
def noxine(frame):
    W, H = 72, 56
    c = Canvas(W, H)
    tw = [0, 1, 0, -1][frame]
    # piques / pattes noires
    spikes = np.zeros((H, W), bool)
    for (bx, by, tx, ty) in ((16, 34, 6, 46), (20, 40, 12, 54), (56, 34, 66, 46), (52, 40, 60, 54), (18, 22, 6, 14), (54, 22, 66, 14)):
        tt = tw if bx < 36 else -tw
        spikes |= c.poly([(bx - 2, by), (bx + 2, by), (tx + tt, ty + abs(tt))])
    c.shade(spikes, BLACK, thick=1.5, seed=1)
    # carapace brune (derrière, en haut)
    c.shade(c.ellipse(36, 22, 24, 17), CARAPACE, thick=9, noise=0.2, clumps=0.45, seed=3, light=(-0.4, -0.9, 0.5))
    # corps sphérique olive
    c.shade(c.circle(36, 32, 17), OLIVE, thick=12, noise=0.08, seed=5, light=(-0.6, -0.7, 0.6))
    c.fill(c.circle(28, 24, 1.6), "#e8f0d0")  # reflet
    for x in (19, 53):  # petites sphères latérales (articulations)
        c.shade(c.circle(x, 36, 5), OLIVE, thick=4, seed=x)
    # œil-cadran : anneau sombre dentelé + verre bleu lumineux + petite aiguille
    ang = np.arctan2(c.yy - 36, c.xx - 36)
    d = np.hypot(c.xx - 36, c.yy - 36)
    ring = (d < 11 + 1.2 * (np.cos(ang * 10) > 0.3)) & (d >= 6.5)
    c.shade(ring, BLACK, thick=2, seed=7)
    for k in range(12):
        a = k * math.tau / 12
        c.rgb[int(36 + math.sin(a) * 8.6), int(36 + math.cos(a) * 8.6)] = hexrgb("#6c6c80")
    c.fill(c.circle(36, 36, 6.5), ["#1aa6c8", "#2fd0e8", "#56e6f6", "#2fd0e8"][frame])
    c.fill(c.circle(36, 36, 4), "#9ff6ff")
    c.fill(c.circle(35, 35, 1.6), "#ffffff")
    c.fill(c.capsule(36, 36, 39, 33, 0.6), "#0a3a48")
    return c.image()


# ------------------------------------------------------------------ main de Sadida (vue subjective)
def hand():
    W, H = 110, 130
    c = Canvas(W, H)
    fingers = [(36, 50, 33, 16, 5.6), (48, 46, 47, 6, 6.0), (61, 46, 62, 4, 6.0), (73, 50, 77, 12, 5.4)]
    m = c.ellipse(57, 76, 28, 32)
    for (ax, ay, bx, by, r) in fingers:
        m |= c.capsule(ax, ay, bx, by, r, r * 0.9)
    m |= c.capsule(34, 82, 12, 56, 7.5, 6)  # pouce
    m |= c.poly([(36, 96), (80, 96), (82, 130), (34, 130)])  # poignet
    c.shade(m, SKIN, thick=9, light=(-0.55, -0.7, 0.7), noise=0.1, seed=11, ao=0.25)
    for (ax, ay, bx, by, r) in fingers:  # plis des doigts
        for t in (0.42, 0.7):
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            c.fill(c.capsule(x - r * 0.6, y, x + r * 0.6, y, 0.5), "#5e3119")
    c.fill(c.capsule(42, 78, 70, 72, 0.6) | c.capsule(44, 86, 72, 84, 0.6), "#6e3a1e")  # lignes de la main
    # bandage beige au poignet (comme les Sadida du jeu)
    c.shade(c.poly([(32, 104), (84, 100), (85, 122), (31, 126)]), WRAP, thick=6, light=(-0.4, -0.8, 0.7), noise=0.15, seed=12)
    for y0 in (108, 114, 120):
        c.fill(c.capsule(32, y0 + 3, 85, y0 - 1, 0.55), "#857152")
    return c.image()


def tree_of_life():
    save(tree(77, W=230, H=330, crown=0.62, trunk_w=16), "arbre-de-vie.png", 4)


# ------------------------------------------------------------------ Nox (silhouette noire, yeux et cœur cyan)
def nox(frame):
    W, H = 96, 124
    c = Canvas(W, H)
    s = [0, 1.5][frame]
    cx = 48
    body = c.ellipse(cx, 18, 8.5, 10)  # tête ronde
    body |= c.capsule(cx, 26, cx, 32, 3)  # cou
    body |= c.poly([(cx - 11, 32), (cx + 11, 32), (cx + 6, 62), (cx - 6, 62)])  # buste
    body |= c.ellipse(cx, 64, 7, 4)  # taille
    body |= c.poly([(cx - 5, 64), (cx + 5, 64), (cx + 22 + s, 122), (cx - 22 - s, 122)])  # longue jupe évasée
    body |= c.capsule(cx + 10, 34, cx + 26, 20 - s, 3.2, 2.6)  # bras droit levé
    body |= c.capsule(cx + 26, 20 - s, cx + 40, 4 - s * 2, 2.6, 2.0)
    body |= c.capsule(cx - 10, 34, cx - 26, 46 + s, 3.2, 2.6)  # bras gauche tendu
    body |= c.capsule(cx - 26, 46 + s, cx - 42, 44 + s * 2, 2.6, 2.0)
    body |= c.ellipse(cx + 41, 3 - s * 2, 3, 2.4) | c.ellipse(cx - 43, 44 + s * 2, 3, 2.4)
    c.shade(body, NOX, thick=5, light=(0.75, -0.45, 0.45), noise=0.06, seed=21)
    for x0 in (-8, 8):  # fentes de la jupe
        c.fill(c.capsule(cx + x0 * 0.4, 72, cx + x0 * 1.8, 120, 0.6), "#04050a")
    for ex in (cx - 4, cx + 4):  # yeux et cœur cyan
        c.fill(c.circle(ex, 18, 3.2), "#2fd0e8")
        c.fill(c.circle(ex, 18, 1.8), "#d8fcff")
    c.fill(c.circle(cx, 45, 6), "#2fd0e8")
    c.fill(c.circle(cx, 45, 4), "#9ff6ff")
    c.fill(c.circle(cx, 45, 2), "#ffffff")
    c.fill(c.circle(cx, 112, 2.5), "#2fd0e8")
    return c.image()


# ------------------------------------------------------------------ Sadida du village, bêtes, souvenir
def sadida_person(seed, girl):
    W, H = 40, 88
    c = Canvas(W, H)
    rng = np.random.default_rng(seed)
    cx = 20
    skin = c.ellipse(cx, 20, 7, 8)  # tête
    skin |= c.capsule(cx, 27, cx, 31, 2.5)
    skin |= c.poly([(cx - 8, 31), (cx + 8, 31), (cx + 6, 52), (cx - 6, 52)])  # torse
    skin |= c.capsule(cx - 8, 33, cx - 11, 54, 2.6, 2.2) | c.capsule(cx + 8, 33, cx + 11, 54, 2.6, 2.2)  # bras
    skin |= c.capsule(cx - 4, 56, cx - 5, 84, 3.2, 2.6) | c.capsule(cx + 4, 56, cx + 5, 84, 3.2, 2.6)  # jambes
    c.shade(skin, SKIN, thick=3.5, light=(-0.6, -0.6, 0.6), noise=0.08, seed=seed)
    cloth = c.poly([(cx - 7, 50), (cx + 7, 50), (cx + 9, 62), (cx - 9, 62)])
    if girl:
        cloth |= c.poly([(cx - 7, 34), (cx + 7, 34), (cx + 6, 40), (cx - 6, 40)])
    for side in (-1, 1):
        cloth |= c.capsule(cx + side * 10, 46, cx + side * 11, 54, 2.8)  # bandes des bras
        cloth |= c.capsule(cx + side * 4.5, 70, cx + side * 5, 82, 3.4)  # jambières
    c.shade(cloth, WRAP, thick=2.5, noise=0.12, seed=seed + 1)
    hair = c.ellipse(cx, 13, 8, 6)
    for k in range(9):  # cheveux-feuilles en pointes
        a = -math.pi + k * math.pi / 8 + rng.uniform(-0.15, 0.15)
        hair |= c.poly([(cx + math.cos(a) * 5, 16 + math.sin(a) * 5), (cx + math.cos(a) * 13, 14 + math.sin(a) * 12),
                        (cx + math.cos(a + 0.4) * 6, 16 + math.sin(a + 0.4) * 6)])
    hair |= c.poly([(cx + 2, 6), (cx + 8, 0), (cx + 6, 8)])  # mèche relevée
    c.shade(hair, HAIR, thick=3, noise=0.15, clumps=0.3, seed=seed + 2)
    c.fill(c.ellipse(cx - 3, 21, 1, 1.4) | c.ellipse(cx + 3, 21, 1, 1.4), "#1a0c08")
    return c.image()


def tofu(frame):
    c = Canvas(30, 30)
    y = [0, -3][frame]
    c.shade(c.circle(15, 17 + y, 10), YELLOW, thick=7, seed=2)
    c.shade(c.poly([(13, 8 + y), (15, 1 + y), (18, 8 + y)]), YELLOW, thick=1.5, seed=3, bias=-0.15)
    c.fill(c.poly([(24, 15 + y), (29, 17 + y), (24, 19 + y)]), "#e8742a")
    c.fill(c.circle(20, 14 + y, 1.3), "#141414")
    c.shade(c.ellipse(11, 19 + y, 4, 2.6, 0.4), YELLOW, thick=2, seed=4, bias=-0.2)
    for x in (12, 17):
        c.fill(c.capsule(x, 26 + y, x, 29, 0.6), "#e8742a")
    return c.image()


def bouftou():
    c = Canvas(48, 36)
    rng = np.random.default_rng(8)
    for k in range(5):
        c.fill(c.capsule(14 + k * 6, 26, 14 + k * 6, 34, 1.6), "#3b2418")
    wool = np.zeros((36, 48), bool)
    for (x, y, r) in ((18, 16, 9), (28, 13, 10), (36, 18, 8), (24, 22, 8), (32, 23, 7)):
        wool |= c.blob(x, y, r, rng, wobble=0.18, fringe=0.2)
    c.shade(wool, WOOL, thick=6, clumps=0.3, noise=0.1, seed=9)
    c.shade(c.ellipse(9, 20, 7, 6), ramp("#1e110b", "#3b2418", "#5a3a26", "#7a5236"), thick=4, seed=10)
    c.shade(c.capsule(10, 13, 4, 10, 2) | c.capsule(4, 10, 2, 16, 1.6), ramp("#6a5a3a", "#9c8762", "#cdbb8a"), thick=1.5, seed=11)
    c.fill(c.circle(6, 19, 1.1), "#ffffff")
    save(c.image(), "bouftou.png", 5)


def family():
    """Souvenir de Nox : une femme et deux enfants, en sépia (silhouettes ombrées comme les Sadida)."""
    def sepia(im, k):
        a = np.array(im).astype(float)
        g = a[..., :3].mean(axis=2) / 255
        idx = np.clip((g * 1.6 * len(SEPIA)).astype(int), 0, len(SEPIA) - 1)
        a[..., :3] = np.array(SEPIA)[idx]
        im = Image.fromarray(a.astype(np.uint8), "RGBA")
        return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)
    out = Image.new("RGBA", (90, 88), (0, 0, 0, 0))
    for seed, k, x in ((60, 1.0, 4), (61, 0.62, 44), (62, 0.55, 64)):
        f = sepia(sadida_person(seed, True), k)
        out.alpha_composite(f, (x, 88 - f.height))
    save(out, "famille.png", 5)


def leaf_sprite():
    c = Canvas(16, 16)
    rng = np.random.default_rng(3)
    c.shade(c.blob(8, 8, 6, rng, wobble=0.1, fringe=0.0) & c.ellipse(8, 8, 7, 4, -0.7), LEAF, thick=3, seed=4, bias=0.2)
    c.fill(c.capsule(3, 13, 12, 4, 0.5), "#174f28")
    save(c.image(), "feuille.png", 5)


def tile(ramp_hex, seed, flowers):
    """Tuile 64×64 sans couture (bruit périodique) : herbe en paquets ou terre du chemin."""
    rng = np.random.default_rng(seed)
    g = zoom(np.tile(rng.random((16, 16)), (3, 3)), 4, order=1)[64:128, 64:128]
    v = np.clip(g * 0.75 + rng.random((64, 64)) * 0.35, 0, 1)
    P = np.array(ramp(*ramp_hex))
    a = P[np.clip((v * len(P)).astype(int), 0, len(P) - 1)]
    for _ in range(flowers):
        x, y = rng.integers(1, 63, 2)
        col = hexrgb(["#ff9ad0", "#ffe36b", "#bfe8ff"][rng.integers(0, 3)])
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            a[(y + dy) % 64, (x + dx) % 64] = col
        a[y, x] = hexrgb("#fff7d0")
    return Image.fromarray(np.dstack([a, np.full((64, 64), 255)]).astype(np.uint8), "RGBA").resize((256, 256), Image.NEAREST)


def main():
    os.makedirs(OUT, exist_ok=True)
    clock()
    gear()
    save_sheet([tree(5, W=110, H=200, face=sadida_face(s), trunk_w=11) for s in (0, 1, 2)], "arbre-sadida.png", 4, 0)
    for i in range(3):
        save(tree(10 + i * 7, W=110 + i * 10, H=200 + i * 12), f"arbre-{i}.png", 4)
    save_sheet([noxine(f) for f in range(4)], "noxine.png", 6, 90)
    save(hand(), "main.png", 6)
    tree_of_life()
    save_sheet([nox(f) for f in range(2)], "nox.png", 5, 420)
    save_sheet([tofu(f) for f in range(2)], "tofu.png", 5, 220)
    bouftou()
    for i in range(4):
        save(sadida_person(50 + i, i % 2 == 0), f"sadida-{i}.png", 4)
    family()
    leaf_sprite()
    tile(("#0f2a1c", "#174f28", "#22621f", "#2f7a22", "#46901d"), 12, 9).save(os.path.join(OUT, "sol.png"))
    tile(("#3a2a1e", "#56402a", "#6e5434", "#876a44", "#a0845a"), 13, 0).save(os.path.join(OUT, "chemin.png"))
    json.dump(META, open(os.path.join(OUT, "sprites.json"), "w"), indent=1)
    print(json.dumps(META))


if __name__ == "__main__":
    main()
