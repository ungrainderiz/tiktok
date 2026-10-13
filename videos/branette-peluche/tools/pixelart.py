#!/usr/bin/env python3
"""Décors pixel art « HD » de la vidéo Branette (nuit, horreur), même moteur que Wakfu (relief → lumière → rampe).

Ambiance : SOMBRE. Une seule source par plan (lune, lampadaire, écran du Pokédex), noirs bleutés, grain.
Le sprite de Branette est le sprite officiel Noir/Blanc (assets/sprites/branette-anim.gif), jamais redessiné.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageSequence
from scipy.ndimage import distance_transform_edt, gaussian_filter, zoom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "decor")
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def ramp(*hexes):
    return [hexrgb(h) for h in hexes]


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




W, H = 270, 480  # résolution native (×4 → 1080×1920)
SC = 4
NIGHT = ramp("#020307", "#06080f", "#0b0f1a", "#121a2a", "#1c2840", "#2a3a58")
WOOD = ramp("#050304", "#0d0807", "#170e0b", "#241610", "#352116")
DOORW = ramp("#070405", "#120a08", "#1d110c", "#2a1a12", "#3b2619", "#4e3322")
CLOTH = ramp("#030408", "#080b14", "#0f1524", "#182238", "#25344f", "#3a4d6e")
MOON = ramp("#3d4c6a", "#6d80a6", "#a9bad8", "#dfe8f6")
WARM = ramp("#120804", "#2a1308", "#4a240c", "#7a4214", "#b8701e", "#f0b050")
SEPIA = ramp("#120b06", "#2a1c10", "#4a3220", "#6e4f34", "#957050", "#c49c70")
METAL = ramp("#040506", "#0b0e12", "#151a20", "#222a33", "#334050", "#4a5a6e")
SEA = ramp("#010205", "#03060d", "#060c18", "#0b1526", "#13213a", "#22355a")
DIRT = ramp("#040302", "#0b0806", "#140f0b", "#1f1812", "#2c231a")
RED = ramp("#1a0204", "#3a060a", "#6a0c12", "#a8141c", "#e0262e")
FUR = ramp("#120c1c", "#1f1630", "#2e2246", "#40325e", "#564678")


def light(c, x, y, r, k=1.0):
    """Carte de lumière (0–1) autour d'une source : biais à ajouter à l'ombrage."""
    d = np.hypot(c.xx - x, c.yy - y) / r
    return k * np.clip(1 - d, 0, 1) ** 1.6


def finish(img, seed, vig=0.85, gr=6):
    """Vignette lourde + grain : la touche « horreur » commune à tous les plans."""
    a = np.array(img).astype(float)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot((xx - w / 2) / (w / 2), (yy - h * 0.45) / (h / 2))
    a[..., :3] *= np.clip(1 - vig * np.clip(d - 0.45, 0, 1) ** 1.4, 0, 1)[..., None]
    r = np.random.default_rng(seed).normal(0, gr, a.shape[:2])
    a[..., :3] = np.clip(a[..., :3] + r[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def add_light(img, mask_or_map, rgb):
    a = np.array(img).astype(float)
    m = mask_or_map.astype(float)
    a[..., :3] = np.clip(a[..., :3] + m[..., None] * np.array(rgb), 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def rain(c, seed, n=260, col=(120, 140, 175), alpha=1.0):
    r = np.random.default_rng(seed)
    a = np.zeros((H, W))
    for _ in range(n):
        x, y, L = int(r.integers(0, W)), int(r.integers(0, H)), int(r.integers(4, 10))
        for k in range(L):
            yy, xx = y + k, x - k // 3
            if 0 <= yy < H and 0 <= xx < W:
                a[yy, xx] = alpha
    return a


def save_scene(img, name):
    img.resize((W * SC, H * SC), Image.NEAREST).save(os.path.join(OUT, name))


# ------------------------------------------------------------------ sprites officiels → planches
def sheets():
    meta = {}
    sp = os.path.join(ROOT, "assets", "sprites")
    for f in sorted(os.listdir(sp)):
        if not f.endswith("-anim.gif"):
            continue
        im = Image.open(os.path.join(sp, f))
        frames, durs = [], []
        for fr in ImageSequence.Iterator(im):
            frames.append(fr.convert("RGBA").copy())
            durs.append(fr.info.get("duration", 60) or 60)
        w, h = frames[0].size
        sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
        for i, fr in enumerate(frames):
            sheet.paste(fr, (i * w, 0))
        name = f.replace("-anim.gif", "-sheet.png")
        sheet.save(os.path.join(sp, name))
        meta[name] = {"w": w, "h": h, "frames": len(frames), "ms": round(sum(durs) / len(durs))}
    json.dump(meta, open(os.path.join(sp, "sprites.json"), "w"), indent=1)


# ------------------------------------------------------------------ porte d'entrée (fond sans battant ni peluche)
def porte_fond():
    c = Canvas(W, H)
    lamp = light(c, 150, 150, 230, 0.5)
    c.shade(np.ones((H, W), bool), NIGHT, thick=400, noise=0.08, seed=11, bias=-0.66)
    door = c.poly([(60, 60), (210, 60), (210, 470), (60, 470)])
    c.shade(door, NIGHT, thick=200, noise=0.1, seed=12, bias=-0.55 + lamp)
    # maisons d'en face : silhouettes, une fenêtre allumée
    for (x0, x1, top) in ((60, 120, 210), (126, 210, 190)):
        c.shade(c.poly([(x0, top), (x1, top), (x1, 300), (x0, 300)]), NIGHT, thick=30, seed=x0, bias=-0.62)
    c.fill(c.poly([(86, 236), (96, 236), (96, 250), (86, 250)]), "#3a2a12")
    c.fill(c.capsule(150, 128, 150, 300, 1.4), "#04060a")  # lampadaire
    c.shade(c.circle(150, 124, 5), WARM, thick=3, seed=13, bias=0.35)
    road = c.poly([(60, 300), (210, 300), (210, 470), (60, 470)])
    c.shade(road, NIGHT, thick=60, noise=0.18, seed=14, bias=-0.55 + light(c, 150, 330, 140, 0.55))
    # flaques qui reflètent le lampadaire
    for (x, y, rx) in ((150, 340, 22), (110, 380, 14), (175, 400, 16)):
        c.shade(c.ellipse(x, y, rx, 3), NIGHT, thick=3, seed=x + y, bias=-0.2 + light(c, 150, 330, 120, 0.5))
    mat = c.poly([(78, 420), (192, 420), (204, 470), (66, 470)])
    c.shade(mat, WOOD, thick=4, noise=0.28, clumps=0.2, seed=15, bias=-0.1 + light(c, 135, 430, 120, 0.4))
    # intérieur : murs et chambranle (noir), sol du couloir
    frame_ = c.poly([(52, 52), (60, 52), (60, 480), (52, 480)]) | c.poly([(52, 52), (218, 52), (218, 60), (52, 60)]) | c.poly([(210, 52), (218, 52), (218, 480), (210, 480)])
    c.shade(frame_, DOORW, thick=2, seed=17, bias=-0.3)
    img = c.image()
    img = add_light(img, light(c, 150, 124, 70, 1.0), (90, 60, 20))
    img = add_light(img, rain(c, 3, 220) * door, (70, 80, 100))
    return finish(img, 21)


def porte_battant():
    """Battant de porte vu de face (fermée), à animer en rotation autour de ses gonds (bord droit)."""
    w, h = 150, 410
    c = Canvas(w, h)
    c.shade(np.ones((h, w), bool), DOORW, thick=8, noise=0.12, clumps=0.08, seed=31, bias=-0.25, light=(-0.4, -0.3, 0.8))
    for (x0, y0, x1, y1) in ((16, 20, 134, 180), (16, 210, 134, 390)):  # panneaux moulurés
        c.shade(c.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), DOORW, thick=6, seed=x0 + y0, bias=-0.32, light=(0.5, 0.6, 0.6))
    c.shade(c.circle(20, 205, 5), ramp("#1a1408", "#3a2c12", "#6a5226", "#a08040"), thick=3, seed=33, bias=-0.1)
    img = c.image()
    img.resize((w * SC, h * SC), Image.NEAREST).save(os.path.join(OUT, "porte-battant.png"))


# ------------------------------------------------------------------ chambre de nuit (lit vide)
def chambre(warm=False):
    c = Canvas(W, H)
    N, CL, WD = (SEPIA, SEPIA, SEPIA) if warm else (NIGHT, CLOTH, WOOD)
    src = (230, 300) if warm else (120, 300)
    lit = light(c, src[0], src[1], 260, 0.45)
    c.shade(np.ones((H, W), bool), N, thick=400, noise=0.08, clumps=0.05, seed=1, bias=-0.58 + lit)
    win = c.poly([(22, 70), (112, 70), (112, 200), (22, 200)])
    c.fill(win, "#14100a" if warm else "#0a1222")
    if not warm:
        c.shade(c.circle(62, 120, 16), MOON, thick=8, seed=2, light=(-0.3, -0.4, 0.8))
    else:
        for (x, y) in ((40, 90), (90, 110), (70, 160), (50, 140)):
            c.fill(c.circle(x, y, 1.2), "#a08a60")
    c.fill(c.capsule(66, 70, 66, 200, 1.6) | c.capsule(22, 135, 112, 135, 1.6), "#04050a")
    c.fill(c.poly([(18, 66), (116, 66), (116, 72), (18, 72)]) | c.poly([(18, 198), (116, 198), (116, 206), (18, 206)]), "#07090f")
    for (x0, x1, s) in ((8, 30, 1), (104, 126, -1)):
        cur = c.poly([(x0, 60), (x1, 60), (x1 + s * 4, 230), (x0 - s * 2, 236)])
        c.shade(cur, CL, thick=6, noise=0.1, seed=3 + x0, bias=-0.38, light=(-s * 0.6, -0.4, 0.6))
    shaft = c.poly([(22, 200), (112, 200), (230, 470), (90, 470)])
    frame_ = c.poly([(36, 330), (250, 330), (250, 420), (36, 420)])
    c.shade(frame_, WD, thick=4, noise=0.12, seed=5, bias=-0.25 + light(c, src[0], src[1], 200, 0.4))
    head = c.poly([(200, 230), (252, 230), (252, 340), (200, 340)])
    c.shade(head, WD, thick=5, noise=0.12, seed=6, bias=-0.25)
    blanket = c.poly([(30, 300), (246, 296), (256, 352), (24, 360)])
    c.shade(blanket, CL, thick=12, noise=0.1, clumps=0.15, seed=7, bias=-0.25 + light(c, 110, 320, 170, 0.55))
    c.shade(c.ellipse(222, 292, 26, 12), CL, thick=8, seed=8, bias=-0.1 + light(c, 110, 320, 170, 0.35))
    c.fill(c.poly([(40, 420), (48, 420), (48, 460), (40, 460)]) | c.poly([(238, 420), (246, 420), (246, 460), (238, 460)]), "#030203")
    c.shade(c.poly([(4, 300), (30, 300), (30, 380), (4, 380)]), WD, thick=3, seed=9, bias=-0.4)
    c.fill(c.poly([(8, 286), (28, 286), (28, 299), (8, 299)]), "#08090c")
    img = c.image()
    a = np.array(img).astype(float)
    if not warm:
        a[..., :3] = np.where(shaft[..., None], a[..., :3] * 1.35 + np.array([6, 9, 16]), a[..., :3])
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    if warm:  # veilleuse étoile sur la table de nuit
        img = add_light(img, light(c, 18, 280, 90, 1.0), (120, 80, 30))
    return finish(img, 22 + warm)


# ------------------------------------------------------------------ rue + benne sous le lampadaire
def rue():
    c = Canvas(W, H)
    c.shade(np.ones((H, W), bool), NIGHT, thick=400, noise=0.08, seed=41, bias=-0.66)
    for (x0, x1, top) in ((0, 70, 120), (70, 160, 160), (160, 270, 100)):
        c.shade(c.poly([(x0, top), (x1, top), (x1, 330), (x0, 330)]), NIGHT, thick=30, seed=x0 + 1, bias=-0.6)
    for (x, y) in ((24, 160), (200, 140), (232, 200)):
        c.fill(c.poly([(x, y), (x + 10, y), (x + 10, y + 14), (x, y + 14)]), "#0d0f14")
    road = c.poly([(0, 330), (270, 330), (270, 480), (0, 480)])
    c.shade(road, NIGHT, thick=80, noise=0.18, seed=42, bias=-0.55 + light(c, 190, 360, 160, 0.6))
    c.fill(c.capsule(214, 110, 214, 340, 1.8), "#04060a")
    c.fill(c.capsule(214, 112, 196, 112, 1.2), "#04060a")
    c.shade(c.circle(194, 116, 5), WARM, thick=3, seed=43, bias=0.35)
    bin_ = c.poly([(110, 300), (210, 300), (204, 380), (116, 380)])
    c.shade(bin_, METAL, thick=10, noise=0.15, clumps=0.1, seed=44, bias=-0.2 + light(c, 194, 116, 300, 0.5), light=(0.6, -0.6, 0.5))
    lid = c.poly([(106, 290), (214, 290), (214, 302), (106, 302)])
    c.shade(lid, METAL, thick=3, seed=45, bias=-0.05 + light(c, 194, 116, 260, 0.4))
    for x in (120, 200):
        c.fill(c.circle(x, 384, 4), "#050608")
    img = c.image()
    img = add_light(img, light(c, 194, 116, 80, 1.0), (100, 66, 22))
    cone = c.poly([(194, 120), (130, 420), (270, 420), (240, 120)])
    img = add_light(img, cone * 0.18, (60, 40, 14))
    img = add_light(img, rain(c, 4, 320), (60, 70, 90))
    return finish(img, 24)


def poubelle():
    """Souvenir : la petite poubelle de ta chambre d'enfant (sépia)."""
    c = Canvas(W, H)
    c.shade(np.ones((H, W), bool), SEPIA, thick=400, noise=0.1, seed=51, bias=-0.55 + light(c, 135, 200, 260, 0.4))
    floor = c.poly([(0, 360), (270, 360), (270, 480), (0, 480)])
    c.shade(floor, SEPIA, thick=40, noise=0.15, seed=52, bias=-0.5)
    body = c.poly([(85, 240), (185, 240), (175, 400), (95, 400)])
    c.shade(body, SEPIA, thick=14, noise=0.1, seed=53, bias=-0.1, light=(-0.6, -0.4, 0.6))
    for x in range(96, 178, 12):
        c.fill(c.capsule(x, 250, x + 3, 392, 0.5), "#2a1c10")
    img = c.image()
    return finish(img, 25, vig=1.0)


def feu():
    c = Canvas(W, H)
    c.shade(np.ones((H, W), bool), NIGHT, thick=400, noise=0.08, seed=61, bias=-0.7)
    ground = c.poly([(0, 380), (270, 380), (270, 480), (0, 480)])
    c.shade(ground, DIRT, thick=40, noise=0.2, seed=62, bias=-0.3 + light(c, 135, 380, 160, 0.6))
    c.shade(c.ellipse(135, 392, 70, 12), METAL, thick=6, seed=63, bias=-0.2)  # baril / foyer
    img = add_light(c.image(), light(c, 135, 330, 210, 1.0), (150, 70, 18))
    return finish(img, 26)


def tombe():
    c = Canvas(W, H)
    c.shade(np.ones((H, W), bool), NIGHT, thick=400, noise=0.08, seed=71, bias=-0.66 + light(c, 200, 80, 300, 0.3))
    c.shade(c.circle(205, 80, 12), MOON, thick=6, seed=72, bias=-0.15)
    hill = c.poly([(0, 330), (270, 300), (270, 480), (0, 480)])
    c.shade(hill, DIRT, thick=60, noise=0.2, clumps=0.2, seed=73, bias=-0.35 + light(c, 160, 380, 200, 0.35))
    mound = c.ellipse(135, 400, 80, 24)
    c.shade(mound, DIRT, thick=14, noise=0.25, clumps=0.3, seed=74, bias=-0.1 + light(c, 170, 360, 160, 0.4), light=(0.5, -0.8, 0.5))
    c.fill(c.capsule(205, 300, 225, 420, 1.6), "#0b0a08")  # pelle plantée
    c.shade(c.poly([(216, 400), (234, 400), (236, 430), (214, 430)]), METAL, thick=3, seed=75, bias=-0.1)
    return finish(c.image(), 27)


def mer():
    c = Canvas(W, H)
    c.shade(np.ones((H, W), bool), SEA, thick=400, noise=0.06, seed=81, bias=-0.62 + light(c, 70, 140, 300, 0.3))
    c.shade(c.circle(70, 140, 10), MOON, thick=5, seed=82, bias=-0.2)
    sea = c.poly([(0, 230), (270, 230), (270, 480), (0, 480)])
    c.shade(sea, SEA, thick=40, noise=0.25, clumps=0.4, seed=83, bias=-0.45)
    img = c.image()
    a = np.array(img).astype(float)
    r = np.random.default_rng(84)
    for _ in range(140):  # reflet de lune en traits
        y = int(r.integers(232, 470))
        x = int(70 + r.normal(0, 6 + (y - 230) * 0.12))
        L = int(r.integers(2, 8))
        if 0 <= x < W - L:
            a[y, x:x + L, :3] = np.minimum(255, a[y, x:x + L, :3] + 70)
    return finish(Image.fromarray(a.astype(np.uint8), "RGBA"), 28)


def pokedex():
    """Pokédex rouge (boîtier) avec une fenêtre d'écran vide (contenu en HTML)."""
    w, h = 230, 330
    c = Canvas(w, h)
    body = c.poly([(6, 10), (224, 10), (224, 322), (6, 322)])
    c.shade(body, RED, thick=12, noise=0.08, seed=91, bias=-0.15, light=(-0.6, -0.6, 0.6))
    c.shade(c.poly([(22, 70), (208, 70), (208, 250), (22, 250)]), METAL, thick=4, seed=92, bias=-0.1)
    c.fill(c.poly([(32, 80), (198, 80), (198, 240), (32, 240)]), "#03060a")
    c.shade(c.circle(36, 36, 16), ramp("#0a2a3a", "#1a5a7a", "#3aa0c8", "#9ff0ff"), thick=8, seed=93)
    for i, col in enumerate(("#ff3b3b", "#ffd23a", "#3bd16b")):
        c.fill(c.circle(70 + i * 16, 26, 4), col)
    c.shade(c.poly([(30, 270), (110, 270), (110, 300), (30, 300)]), ramp("#05070a", "#11161d", "#1e2630"), thick=3, seed=94)
    c.shade(c.circle(180, 285, 14), ramp("#05070a", "#11161d", "#1e2630", "#2e3946"), thick=5, seed=95)
    img = c.image()
    img.resize((w * SC, h * SC), Image.NEAREST).save(os.path.join(OUT, "pokedex.png"))


def fermeture():
    """Gros plan de la bouche-fermeture : planche de 10 images, de 0 à 9 crans ouverts."""
    w, h = 270, 140
    frames = []
    for k in range(10):
        c = Canvas(w, h)
        c.shade(np.ones((h, w), bool), FUR, thick=60, noise=0.18, clumps=0.25, seed=101, bias=-0.15)
        y0 = 70
        open_x = 250 - k * 22  # le curseur recule vers la gauche à chaque cran
        gap = np.zeros((h, w), bool)
        if k:
            gap = c.poly([(open_x, y0), (252, y0 - 4 - k * 1.6), (262, y0), (252, y0 + 4 + k * 1.6)])
            c.fill(gap, "#050106")
            inner = c.ellipse((open_x + 258) / 2, y0, (258 - open_x) / 2.4, 2 + k)
            c.fill(inner & gap, "#3a0610")
        for i in range(24):  # dents dorées
            x = 12 + i * 10
            opened = x > open_x
            dy = (4 + k * 1.6) * min(1, (x - open_x) / 30) if opened else 0
            for side, oy in ((-1, -3), (1, 3)):
                xx = x + (5 if side > 0 else 0)
                tooth = c.poly([(xx, y0 + oy * 0.5 + side * dy), (xx + 5, y0 + oy * 0.5 + side * dy),
                                (xx + 5, y0 + oy * 2 + side * dy), (xx, y0 + oy * 2 + side * dy)])
                c.shade(tooth, ramp("#3a2a08", "#7a5a12", "#c0901e", "#f0c84a"), thick=2, seed=i * 2 + side + 1, bias=0.05)
        # curseur + tirette
        cur = c.poly([(open_x - 14, y0 - 9), (open_x + 4, y0 - 6), (open_x + 4, y0 + 6), (open_x - 14, y0 + 9)])
        c.shade(cur, ramp("#2a2a30", "#55555e", "#8a8a96", "#c8c8d4"), thick=3, seed=200 + k)
        tab = c.poly([(open_x - 10, y0 + 6), (open_x - 2, y0 + 6), (open_x, y0 + 40), (open_x - 12, y0 + 40)])
        c.shade(tab, ramp("#2a2a30", "#55555e", "#8a8a96", "#c8c8d4"), thick=3, seed=300 + k)
        c.fill(c.ellipse(open_x - 6, y0 + 33, 2.5, 3.5), "#1a1a20")
        frames.append(finish(c.image(), 400 + k, vig=0.6, gr=5))
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    sheet.resize((sheet.width * SC, h * SC), Image.NEAREST).save(os.path.join(OUT, "fermeture.png"))


def rain_tile():
    """Tuile de pluie 64×64 transparente (×4 = 256 px) à faire défiler en boucle."""
    r = np.random.default_rng(5)
    a = np.zeros((64, 64, 4), dtype=np.uint8)
    for _ in range(26):
        x, y, L = int(r.integers(0, 64)), int(r.integers(0, 64)), int(r.integers(3, 7))
        for k in range(L):
            a[(y + k) % 64, (x - k // 3) % 64] = (150, 170, 205, 110)
    Image.fromarray(a, "RGBA").resize((256, 256), Image.NEAREST).save(os.path.join(OUT, "pluie.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    sheets()
    rain_tile()
    save_scene(porte_fond(), "porte-fond.png")
    porte_battant()
    save_scene(chambre(), "chambre-fond.png")
    save_scene(chambre(True), "souvenir-chambre.png")
    save_scene(rue(), "rue.png")
    save_scene(poubelle(), "poubelle.png")
    save_scene(feu(), "feu.png")
    save_scene(tombe(), "tombe.png")
    save_scene(mer(), "mer.png")
    pokedex()
    fermeture()


if __name__ == "__main__":
    main()
