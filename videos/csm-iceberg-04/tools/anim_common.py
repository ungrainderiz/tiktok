"""Animated pixel-art sprite sheets for episode 2 (Octopus Devil).
Each sheet = N frames + a copy of frame 0 appended (so a steps(N) tween can loop cleanly)."""
import math
from PIL import Image, ImageDraw

K = (20, 14, 26, 255)
SK, SK2 = (248, 206, 172, 255), (220, 160, 124, 255)
HAIR = (30, 26, 36, 255)
GOLD = (255, 210, 40, 255)
NAVY, NAVY2 = (34, 40, 66, 255), (22, 26, 44, 255)
WH, BK = (246, 244, 240, 255), (20, 14, 26, 255)
TEN, TEN2, SUCK = (122, 52, 104, 255), (84, 30, 74, 255), (236, 150, 190, 255)
BLOND, BLOND2 = (246, 214, 104, 255), (206, 160, 52, 255)
OR, OR2, GR, GR2 = (240, 132, 36, 255), (190, 86, 24, 255), (168, 176, 186, 255), (102, 108, 120, 255)


def outline(im, col=K):
    w, h = im.size; src = im.load(); out = im.copy(); o = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0 and src[nx, ny] != col:
                        o[x, y] = col; break
    return out


def sheet(frames, name):
    w, h = frames[0].size
    frames = [outline(f) for f in frames] + [outline(frames[0])]
    s = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0))
    s.save(f"sprites/{name}.png")
    print(name, len(frames) - 1, "frames", w, "x", h)


# ---------------- YOSHIDA (idle: breathe + blink + earring glint) ----------------
def yoshida_frame(i):
    im = Image.new("RGBA", (44, 54), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    by = 1 if i in (2, 3, 4, 5) else 0  # breathing
    # body (dark gakuran, high collar)
    d.polygon([(5, 54), (9, 41 + by), (35, 41 + by), (39, 54)], fill=NAVY2)
    d.rectangle([17, 39 + by, 27, 43 + by], fill=NAVY)
    for y in (46, 50):
        d.point((22, y + by), fill=GOLD)
    d.rectangle([18, 33, 25, 40 + by], fill=SK2)
    d.ellipse([11, 10, 32, 36], fill=SK)
    # hair: messy black, bangs over forehead, side locks
    d.pieslice([8, 4, 35, 30], 180, 360, fill=HAIR)
    sway = [0, 0, 1, 1, 0, 0, -1, -1][i]
    d.polygon([(9, 16), (12, 25), (15, 16), (18, 23), (21, 15), (24, 22), (27, 15), (31, 24), (34, 16), (34, 13), (9, 13)], fill=HAIR)
    d.rectangle([8, 14, 11, 28], fill=HAIR); d.rectangle([32, 14, 35, 28], fill=HAIR)
    d.polygon([(20, 4), (23 + sway, -1), (26, 5)], fill=HAIR)
    # ears + piercings
    d.rectangle([9, 23, 11, 28], fill=SK2); d.rectangle([32, 23, 34, 28], fill=SK2)
    for (x, y) in ((9, 24), (9, 27), (34, 24), (34, 26), (34, 28)):
        d.point((x, y), fill=GOLD if not (i == 6 and x == 34) else WH)
    # eyes: calm half-closed, blink on frame 7
    for ex in (14, 25):
        if i == 7:
            d.line([ex, 26, ex + 4, 26], fill=K)
        else:
            d.line([ex - 1, 24, ex + 5, 24], fill=K)
            d.rectangle([ex, 25, ex + 4, 26], fill=(60, 56, 80, 255))
            d.point((ex + 1, 25), fill=WH)
    # calm smile
    d.line([19, 31, 24, 31], fill=SK2); d.point((18, 30), fill=SK2); d.point((25, 30), fill=SK2)
    return im


# ---------------- DENJI (idle: breathe + blink + grin) ----------------
def denji_frame(i):
    im = Image.new("RGBA", (44, 54), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    by = 1 if i in (2, 3, 4, 5) else 0
    d.polygon([(5, 54), (9, 41 + by), (35, 41 + by), (39, 54)], fill=NAVY2)
    d.polygon([(17, 41 + by), (22, 49), (27, 41 + by)], fill=WH)
    # starter cord on chest
    d.line([22, 44 + by, 22, 49 + by], fill=GR); d.rectangle([19, 49 + by, 25, 50 + by], fill=GR2)
    d.rectangle([18, 33, 25, 41 + by], fill=SK2)
    d.ellipse([11, 10, 32, 36], fill=SK)
    # spiky blond hair
    spk = [0, 1, 0, -1, 0, 1, 0, -1][i]
    d.polygon([(7, 20), (9, 8), (5, 4 + spk), (13, 6), (14, 0), (19, 5), (23, -1 + spk), (26, 5), (32, 0), (31, 7), (38, 5 - spk), (34, 12), (37, 20), (33, 16), (30, 22), (27, 15), (22, 21), (18, 15), (14, 22), (11, 15)], fill=BLOND)
    d.polygon([(11, 15), (14, 22), (18, 15), (22, 21)], fill=BLOND2)
    for ex in (14, 25):
        if i == 7:
            d.line([ex, 25, ex + 4, 25], fill=K)
        else:
            d.rectangle([ex, 23, ex + 4, 26], fill=WH); d.rectangle([ex + 1, 24, ex + 3, 26], fill=(214, 120, 30, 255)); d.point((ex + 2, 25), fill=K)
            d.line([ex - 1, 22, ex + 5, 22], fill=K)
    # shark-tooth grin
    d.rectangle([16, 29, 27, 32], fill=BK)
    for x in range(16, 28, 2):
        d.polygon([(x, 29), (x + 1, 29), (x, 31)], fill=WH)
    return im


# ---------------- TENTACLE (rising, waving) ----------------
def tentacle_frame(i, n=8, h=96, w=40):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ph = i / n * math.tau
    segs = 26
    pts = []
    for k in range(segs + 1):
        t = k / segs
        y = h - 2 - t * (h - 8)
        amp = 3 + 9 * t
        x = w / 2 + math.sin(ph + t * 4.2) * amp
        r = 8.5 * (1 - t) + 1.5
        pts.append((x, y, r))
    for x, y, r in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=TEN)
    for k, (x, y, r) in enumerate(pts):
        if k % 2 == 0 and r > 3:
            d.ellipse([x + r * 0.15, y - r * 0.35, x + r * 0.75, y + r * 0.25], fill=SUCK)
        d.point((int(x - r * 0.6), int(y)), fill=TEN2)
    return im


# ---------------- OCTOPUS DEVIL silhouette (deep water) ----------------
def octo_frame(i, n=8):
    w, h = 110, 90
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body = (52, 20, 50, 255); body2 = (74, 30, 70, 255)
    ph = i / n * math.tau
    for a in range(8):
        base = 18 + a * 10.5
        for k in range(22):
            t = k / 21
            x = base + math.sin(ph + a * 0.9 + t * 3.5) * (2 + 10 * t) + (a - 3.5) * 5 * t
            y = 44 + t * 44
            r = 5.5 * (1 - t) + 1
            d.ellipse([x - r, y - r, x + r, y + r], fill=body)
    pulse = [0, 1, 2, 1, 0, -1, -2, -1][i]
    d.ellipse([22 - pulse, 4 - pulse, 88 + pulse, 58], fill=body)
    d.ellipse([32, 10, 66, 34], fill=body2)
    # many eyes
    for (x, y) in ((36, 34), (48, 30), (60, 30), (72, 34), (54, 40)):
        glow = i in (3, 4) and (x == 54)
        d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=(255, 220, 60, 255) if not glow else (255, 255, 200, 255))
        d.point((x, y), fill=BK)
    return im


# ---------------- CHAINSAW MAN head (blade buzz) ----------------
def csm_frame(i):
    im = Image.new("RGBA", (40, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    j = i % 2
    d.rectangle([16, 0, 24, 22], fill=GR); d.rectangle([17, 1, 18, 20], fill=(222, 228, 236, 255))
    for y in range(1 + j, 22, 3):
        d.point((15, y), fill=GR2); d.point((25, y + 1), fill=GR2)
    d.ellipse([6, 14, 34, 42], fill=OR)
    d.ellipse([9, 16, 26, 28], fill=(255, 182, 92, 255))
    d.rectangle([10, 30, 30, 36], fill=BK)
    for x in range(10, 30, 3):
        d.polygon([(x, 30), (x + 2, 30), (x + 1, 33 + j)], fill=WH)
        d.polygon([(x + 1, 36), (x + 3, 36), (x + 2, 33 - j)], fill=WH)
    d.ellipse([12, 22, 16, 26], fill=(255, 240, 200, 255)); d.ellipse([24, 22, 28, 26], fill=(255, 240, 200, 255))
    d.rectangle([3, 36, 37, 46], fill=NAVY2)
    return im


if False:
    sheet([yoshida_frame(i) for i in range(8)], "yoshida_anim")
    sheet([denji_frame(i) for i in range(8)], "denji_anim")
    sheet([tentacle_frame(i) for i in range(8)], "tentacle_anim")
    sheet([octo_frame(i) for i in range(8)], "octo_anim")
    sheet([csm_frame(i) for i in range(4)], "csm_anim")
