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
NIGHT = ramp("#020307", "#06080f", "#0b0f1a", "#121a2a", "#1c2840", "#2a3a58")
WOOD = ramp("#050304", "#0d0807", "#170e0b", "#241610", "#352116")
CLOTH = ramp("#030408", "#080b14", "#0f1524", "#182238", "#25344f", "#3a4d6e")
MOON = ramp("#3d4c6a", "#6d80a6", "#a9bad8", "#dfe8f6")
WARM = ramp("#120804", "#2a1308", "#4a240c", "#7a4214", "#b8701e", "#f0b050")


def light(c, x, y, r, k=1.0):
    """Carte de lumière (0–1) autour d'une source : biais à ajouter à l'ombrage."""
    d = np.hypot(c.xx - x, c.yy - y) / r
    return k * np.clip(1 - d, 0, 1) ** 1.6


def grain(img, seed, amt=10):
    a = np.array(img).astype(float)
    r = np.random.default_rng(seed).normal(0, amt, a.shape[:2])
    a[..., :3] = np.clip(a[..., :3] + r[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def branette_frame(i=0, scale=2, tint=(0.55, 0.62, 0.9)):
    im = Image.open(os.path.join(ROOT, "assets", "sprites", "branette-anim.gif"))
    fr = [f.convert("RGBA").copy() for f in ImageSequence.Iterator(im)][i]
    a = np.array(fr).astype(float)
    red = (a[..., 0] > a[..., 1] * 1.6) & (a[..., 0] > 120)  # yeux rouges : on les garde vifs
    a[..., :3] *= np.array(tint)
    a[red, 0] = np.minimum(255, a[red, 0] / tint[0] * 1.1)
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return out.resize((out.width * scale, out.height * scale), Image.NEAREST)


def chambre():
    c = Canvas(W, H)
    mx, my = 62, 120  # lune derrière la fenêtre
    moonlit = light(c, 120, 300, 260, 0.45)
    c.shade(np.ones((H, W), bool), NIGHT, thick=400, noise=0.08, clumps=0.05, seed=1, bias=-0.55 + moonlit)
    # fenêtre + ciel + lune
    win = c.poly([(22, 70), (112, 70), (112, 200), (22, 200)])
    c.fill(win, "#0a1222")
    c.shade(c.circle(mx, my, 16), MOON, thick=8, seed=2, light=(-0.3, -0.4, 0.8))
    for x in (66,):
        c.fill(c.capsule(x, 70, x, 200, 1.6), "#04050a")
    c.fill(c.capsule(22, 135, 112, 135, 1.6), "#04050a")
    c.fill(c.poly([(18, 66), (116, 66), (116, 72), (18, 72)]) | c.poly([(18, 198), (116, 198), (116, 206), (18, 206)]), "#07090f")
    # rideaux
    for (x0, x1, s) in ((8, 30, 1), (104, 126, -1)):
        cur = c.poly([(x0, 60), (x1, 60), (x1 + s * 4, 230), (x0 - s * 2, 236)])
        c.shade(cur, CLOTH, thick=6, noise=0.1, seed=3 + x0, bias=-0.35, light=(-s * 0.6, -0.4, 0.6))
    # rai de lune au sol et sur le lit
    shaft = c.poly([(22, 200), (112, 200), (230, 470), (90, 470)])
    # lit
    frame_ = c.poly([(36, 330), (250, 330), (250, 420), (36, 420)])
    c.shade(frame_, WOOD, thick=4, noise=0.12, seed=5, bias=-0.2 + light(c, 120, 300, 200, 0.4))
    head = c.poly([(200, 230), (252, 230), (252, 340), (200, 340)])
    c.shade(head, WOOD, thick=5, noise=0.12, seed=6, bias=-0.2)
    blanket = c.poly([(30, 300), (246, 296), (256, 352), (24, 360)])
    c.shade(blanket, CLOTH, thick=12, noise=0.1, clumps=0.15, seed=7, bias=-0.2 + light(c, 110, 320, 170, 0.55))
    pillow = c.ellipse(222, 292, 26, 12)
    c.shade(pillow, CLOTH, thick=8, seed=8, bias=-0.05 + light(c, 110, 320, 170, 0.35))
    for y in range(420, 480):  # pieds du lit dans le noir
        pass
    c.fill(c.poly([(40, 420), (48, 420), (48, 460), (40, 460)]) | c.poly([(238, 420), (246, 420), (246, 460), (238, 460)]), "#030203")
    # table de nuit + réveil 03:33
    stand = c.poly([(4, 300), (30, 300), (30, 380), (4, 380)])
    c.shade(stand, WOOD, thick=3, seed=9, bias=-0.35)
    c.fill(c.poly([(8, 286), (28, 286), (28, 299), (8, 299)]), "#08090c")
    img = c.image()
    a = np.array(img).astype(float)
    sh = shaft[..., None]
    a[..., :3] = np.where(sh, a[..., :3] * 1.35 + np.array([6, 9, 16]), a[..., :3])  # rai de lune
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate(((10, 289), (15, 289), (21, 289))):  # chiffres du réveil (pixels rouges)
        d.rectangle((x, y, x + 3, y + 6), outline=(200, 30, 30, 255))
    # Branette assise sur le lit, tournée vers toi
    b = branette_frame(0, 2)
    img.alpha_composite(b, (92, 300 - b.height + 18))
    return img


def porte():
    c = Canvas(W, H)
    lamp = light(c, 150, 150, 230, 0.5)
    c.shade(np.ones((H, W), bool), NIGHT, thick=400, noise=0.08, seed=11, bias=-0.62)
    # encadrement de porte (intérieur, noir) et ouverture sur la rue
    door = c.poly([(60, 60), (210, 60), (210, 470), (60, 470)])
    out = np.zeros((H, W), bool) | door
    c.shade(out, NIGHT, thick=200, noise=0.1, seed=12, bias=-0.5 + lamp)
    # lampadaire au loin
    c.fill(c.capsule(150, 120, 150, 300, 1.4), "#05070c")
    c.shade(c.circle(150, 118, 5), WARM, thick=3, seed=13, bias=0.35)
    halo = light(c, 150, 118, 70, 1.0)
    # trottoir mouillé + reflets
    road = c.poly([(60, 300), (210, 300), (210, 470), (60, 470)])
    c.shade(road, NIGHT, thick=60, noise=0.15, seed=14, bias=-0.5 + light(c, 150, 330, 140, 0.55))
    # paillasson
    mat = c.poly([(78, 420), (192, 420), (204, 470), (66, 470)])
    c.shade(mat, WOOD, thick=4, noise=0.25, seed=15, bias=-0.15 + light(c, 135, 430, 120, 0.4))
    # battant de porte entrouvert (au premier plan, à droite)
    leaf = c.poly([(210, 60), (270, 30), (270, 480), (210, 470)])
    c.shade(leaf, WOOD, thick=8, noise=0.1, seed=16, bias=-0.3, light=(-0.8, -0.2, 0.5))
    c.fill(c.circle(222, 280, 3), "#2a2418")
    frame_ = c.poly([(52, 52), (60, 52), (60, 480), (52, 480)]) | c.poly([(52, 52), (218, 52), (218, 60), (52, 60)])
    c.shade(frame_, WOOD, thick=2, seed=17, bias=-0.3)
    img = c.image()
    a = np.array(img).astype(float)
    a[..., :3] += (halo[..., None] * np.array([90, 60, 20]))
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    b = branette_frame(0, 2, tint=(0.5, 0.48, 0.5))
    img.alpha_composite(b, (135 - b.width // 2, 452 - b.height))
    return img


def vignette(img, k=0.85):
    a = np.array(img).astype(float)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot((xx - w / 2) / (w / 2), (yy - h * 0.45) / (h / 2))
    a[..., :3] *= np.clip(1 - k * np.clip(d - 0.45, 0, 1) ** 1.4, 0, 1)[..., None]
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn, seed in (("chambre", chambre, 1), ("porte", porte, 2)):
        img = grain(vignette(fn()), seed, 6)
        save(img, f"{name}.png", 4)


if __name__ == "__main__":
    main()
