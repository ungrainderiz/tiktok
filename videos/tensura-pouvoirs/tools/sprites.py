"""Pixel art : Rimuru (slime), guerrier oni + aura, seigneur démon, gobelin / hobgobelin, humain, villageois, icônes."""
import math
from PIL import Image, ImageDraw

K = (10, 12, 26, 255)
SL, SL2, SL3, SLW = (92, 186, 255, 255), (50, 120, 220, 255), (170, 225, 255, 255), (235, 250, 255, 255)
WH, GRY, GRY2 = (240, 240, 248, 255), (150, 156, 176, 255), (80, 84, 104, 255)
SKIN, SKIN2 = (246, 214, 190, 255), (214, 170, 146, 255)
RED, RED2, OR, OR2, YEL = (232, 50, 60, 255), (150, 20, 34, 255), (255, 140, 40, 255), (210, 70, 20, 255), (255, 236, 140, 255)
GOLD, GOLD2 = (255, 210, 60, 255), (190, 130, 20, 255)
GRN, GRN2, GRN3 = (110, 190, 70, 255), (60, 130, 40, 255), (170, 230, 120, 255)
PUR, PUR2, PUR3 = (150, 70, 230, 255), (80, 30, 140, 255), (210, 150, 255, 255)
BRN, BRN2 = (140, 90, 50, 255), (90, 56, 30, 255)
NAV, NAV2 = (30, 34, 60, 255), (50, 56, 96, 255)


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


def sheet(frames, name, ol=True):
    w, h = frames[0].size
    fr = [outline(f) if ol else f for f in frames]; fr.append(fr[0])
    s = Image.new("RGBA", (w * len(fr), h), (0, 0, 0, 0))
    for i, f in enumerate(fr): s.paste(f, (i * w, 0))
    s.save(f"sprites/{name}.png"); print(name, len(fr) - 1, w, h)


def single(im, name, ol=True):
    (outline(im) if ol else im).save(f"sprites/{name}.png"); print(name, im.size)


# ---------- Rimuru (slime bleu, yeux fermés en arc) ----------
def slime(i, crown=False):
    im = Image.new("RGBA", (36, 38), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sq = [0, 1, 2, 1, 0, -1, -2, -1][i]          # écrasement / étirement
    w = 14 + sq; h = 11 - sq; cx, by = 18, 36
    top = by - 2 * h
    d.ellipse([cx - w, top, cx + w, by + 2], fill=SL2)
    d.ellipse([cx - w + 1, top, cx + w - 1, by - 1], fill=SL)
    d.ellipse([cx - w + 4, top + 2, cx - w + 10, top + 6], fill=SL3)
    d.point([(cx - w + 5, top + 3), (cx - w + 6, top + 3)], fill=SLW)
    ey = top + h + 1
    for ex in (cx - 5, cx + 5):                    # yeux fermés « ^ ^ »
        d.line([(ex - 2, ey + 1), (ex, ey - 1), (ex + 2, ey + 1)], fill=K)
    d.rectangle([0, by + 1, 35, 37], fill=(0, 0, 0, 0))
    if crown:
        d.polygon([(cx - 7, top + 1), (cx - 7, top - 6), (cx - 4, top - 3), (cx, top - 8), (cx + 4, top - 3), (cx + 7, top - 6), (cx + 7, top + 1)], fill=GOLD)
        d.point([(cx, top - 4)], fill=RED); d.line([(cx - 7, top), (cx + 7, top)], fill=GOLD2)
    return im


# ---------- guerrier oni (cheveux rouges, cornes, katana) ----------
def oni(i):
    im = Image.new("RGBA", (40, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 0, 1, 1][i]
    d.rectangle([14, 26 + b, 26, 46], fill=NAV); d.rectangle([14, 26 + b, 15, 46], fill=NAV2)           # kimono
    d.polygon([(18, 26 + b), (22, 26 + b), (20, 33 + b)], fill=WH)                                       # col
    d.rectangle([14, 36, 26, 37], fill=RED)                                                               # ceinture
    d.rectangle([15, 47, 18, 57], fill=K); d.rectangle([22, 47, 25, 57], fill=K)                          # jambes
    d.rectangle([14, 56, 18, 58], fill=GRY2); d.rectangle([22, 56, 26, 58], fill=GRY2)
    d.rectangle([15, 13 + b, 25, 25 + b], fill=SKIN); d.rectangle([15, 22 + b, 25, 25 + b], fill=SKIN2)  # visage
    d.polygon([(13, 16 + b), (14, 8 + b), (20, 5 + b), (27, 8 + b), (27, 18 + b), (24, 12 + b), (17, 12 + b)], fill=RED)  # cheveux
    d.polygon([(16, 8 + b), (15, 1 + b), (18, 7 + b)], fill=WH); d.polygon([(24, 8 + b), (25, 1 + b), (22, 7 + b)], fill=WH)  # cornes
    d.point([(18, 18 + b), (22, 18 + b)], fill=RED2)
    d.rectangle([26, 30 + b, 29, 38 + b], fill=NAV); d.rectangle([27, 38 + b, 29, 40 + b], fill=SKIN)     # bras
    d.line([(29, 39 + b), (38, 12 + b)], fill=WH, width=2); d.line([(29, 39 + b), (31, 34 + b)], fill=K, width=2)  # katana
    d.rectangle([11, 30 + b, 13, 40 + b], fill=NAV)
    return im


# ---------- aura (flammes autour du corps) ----------
def aura(i, c1=OR, c2=YEL, c3=RED):
    im = Image.new("RGBA", (60, 76), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        x = 30 + 22 * math.sin(a); y = 44 + 26 * math.cos(a) * 0.9
        ph = (i + k * 3) % 6; hgt = 8 + [0, 3, 6, 8, 5, 2][ph]
        d.polygon([(x - 4, y), (x + 4, y), (x + [-1, 1, 2, 0, -2, 1][ph], y - hgt - 6)], fill=c3)
        d.polygon([(x - 2, y), (x + 2, y), (x, y - hgt)], fill=c1)
    for k in range(5):
        x = 10 + (k * 11 + i * 7) % 40; y = 64 - ((i * 9 + k * 13) % 60)
        d.rectangle([x, y, x + 1, y + 1], fill=c2)
    return im


# ---------- seigneur démon (cape, cornes, yeux rouges) ----------
def lord(i):
    im = Image.new("RGBA", (48, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sw = [0, 1, 2, 1][i]
    d.polygon([(14, 22), (34, 22), (42 + sw, 62), (6 - sw, 62)], fill=(40, 16, 60, 255))                  # cape
    d.polygon([(16, 22), (32, 22), (36 + sw, 62), (12 - sw, 62)], fill=(70, 28, 100, 255))
    d.rectangle([18, 24, 30, 54], fill=K); d.rectangle([22, 24, 26, 40], fill=PUR2)
    d.rectangle([17, 8, 31, 22], fill=(220, 220, 240, 255)); d.rectangle([17, 19, 31, 22], fill=GRY)    # visage pâle
    d.polygon([(16, 12), (14, 10), (16, 4), (22, 2), (30, 3), (34, 9), (32, 14), (30, 9), (18, 9)], fill=(230, 236, 255, 255))  # cheveux argent
    d.polygon([(18, 6), (12, 0), (16, 1), (20, 5)], fill=K); d.polygon([(30, 6), (36, 0), (32, 1), (28, 5)], fill=K)           # cornes
    d.rectangle([20, 14, 21, 15], fill=RED); d.rectangle([27, 14, 28, 15], fill=RED)
    return im


# ---------- gobelin / hobgobelin ----------
def gob(i):
    im = Image.new("RGBA", (26, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 1][i % 2]
    d.ellipse([7, 4 + b, 19, 16 + b], fill=GRN); d.polygon([(7, 9 + b), (2, 6 + b), (7, 12 + b)], fill=GRN); d.polygon([(19, 9 + b), (24, 6 + b), (19, 12 + b)], fill=GRN)
    d.point([(10, 9 + b), (16, 9 + b)], fill=YEL); d.line([(11, 13 + b), (15, 13 + b)], fill=GRN2)
    d.rectangle([8, 16 + b, 18, 24], fill=BRN); d.rectangle([8, 16 + b, 9, 24], fill=BRN2)                # pagne
    d.rectangle([9, 25, 11, 29], fill=GRN2); d.rectangle([15, 25, 17, 29], fill=GRN2)
    d.rectangle([5, 17 + b, 7, 22 + b], fill=GRN); d.rectangle([19, 17 + b, 21, 22 + b], fill=GRN)
    return im


def hob(i):
    im = Image.new("RGBA", (32, 52), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 1][i % 2]
    d.rectangle([10, 6 + b, 22, 18 + b], fill=GRN3); d.rectangle([10, 15 + b, 22, 18 + b], fill=GRN)    # visage plus humain
    d.polygon([(10, 10 + b), (5, 7 + b), (10, 13 + b)], fill=GRN3); d.polygon([(22, 10 + b), (27, 7 + b), (22, 13 + b)], fill=GRN3)
    d.polygon([(9, 8 + b), (10, 2 + b), (16, 0 + b), (23, 2 + b), (23, 8 + b), (20, 5 + b), (12, 5 + b)], fill=(40, 40, 50, 255))  # cheveux
    d.point([(13, 11 + b), (19, 11 + b)], fill=K)
    d.rectangle([9, 19 + b, 23, 38], fill=GRY); d.rectangle([9, 19 + b, 10, 38], fill=GRY2)             # armure
    d.rectangle([9, 28, 23, 29], fill=BRN); d.rectangle([14, 22 + b, 18, 26 + b], fill=GOLD)
    d.rectangle([10, 39, 14, 50], fill=BRN2); d.rectangle([18, 39, 22, 50], fill=BRN2)
    d.rectangle([5, 20 + b, 8, 32 + b], fill=GRY); d.rectangle([24, 20 + b, 27, 32 + b], fill=GRY)
    d.line([(27, 33 + b), (31, 8 + b)], fill=WH, width=2)                                                # lance/épée
    return im


# ---------- humain (salaryman Satoru) ----------
def human(i):
    im = Image.new("RGBA", (24, 48), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 1][i % 2]
    d.rectangle([7, 5 + b, 17, 16 + b], fill=SKIN); d.rectangle([6, 3 + b, 18, 7 + b], fill=(40, 30, 30, 255))
    d.point([(10, 11 + b), (14, 11 + b)], fill=K)
    d.rectangle([6, 17 + b, 18, 33], fill=(60, 64, 80, 255)); d.polygon([(11, 17 + b), (13, 17 + b), (12, 25 + b)], fill=WH); d.line([(12, 18 + b), (12, 24 + b)], fill=RED)
    d.rectangle([7, 34, 11, 46], fill=(40, 44, 60, 255)); d.rectangle([13, 34, 17, 46], fill=(40, 44, 60, 255))
    d.rectangle([3, 18 + b, 5, 30 + b], fill=(60, 64, 80, 255)); d.rectangle([19, 18 + b, 21, 30 + b], fill=(60, 64, 80, 255))
    return im


# ---------- villageois qui s'entraîne (coup d'épée) ----------
def villager(i):
    im = Image.new("RGBA", (40, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([14, 6, 22, 14], fill=SKIN); d.rectangle([13, 4, 23, 7], fill=BRN)
    d.point([(16, 10), (20, 10)], fill=K)
    d.rectangle([13, 15, 23, 30], fill=(70, 120, 200, 255)); d.rectangle([13, 24, 23, 25], fill=BRN2)
    d.rectangle([14, 31, 17, 42], fill=BRN2); d.rectangle([19, 31, 22, 42], fill=BRN2)
    ang = [-60, -20, 30, 60][i]; a = math.radians(ang)
    hx, hy = 24, 18 + [0, 1, 3, 4][i]
    d.rectangle([22, 16, 25, hy], fill=(70, 120, 200, 255))
    d.line([(hx, hy), (hx + 14 * math.cos(a), hy + 14 * math.sin(a))], fill=WH, width=2)
    if i == 2:
        d.arc([16, 0, 40, 36], -70, 40, fill=SL3)
    return im


# ---------- icônes ----------
def heart(broken=False):
    im = Image.new("RGBA", (16, 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 8, 8], fill=RED); d.ellipse([7, 0, 15, 8], fill=RED); d.polygon([(1, 6), (14, 6), (8, 13)], fill=RED)
    d.point([(3, 2), (4, 2), (3, 3)], fill=(255, 170, 170, 255))
    if broken:
        d.line([(8, 1), (6, 5), (9, 8), (7, 12)], fill=(0, 0, 0, 0), width=2)
    return im


def eye():
    im = Image.new("RGBA", (24, 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 1, 23, 12], fill=WH); d.ellipse([7, 1, 16, 12], fill=SL); d.ellipse([10, 4, 13, 9], fill=K); d.point([(11, 4)], fill=WH)
    return im


def egg(i):
    im = Image.new("RGBA", (20, 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if i < 2:
        d.ellipse([2, 2 + i, 17, 23], fill=(250, 244, 226, 255)); d.ellipse([4, 6, 8, 11], fill=WH)
        d.point([(12, 14), (13, 15), (6, 17)], fill=GRN)
        if i == 1: d.line([(4, 12), (8, 10), (11, 13), (15, 11)], fill=K)
    else:
        d.polygon([(2, 14), (5, 11), (8, 14), (11, 11), (14, 14), (17, 12), (17, 23), (2, 23)], fill=(250, 244, 226, 255))
        d.ellipse([5, 4, 15, 14], fill=GRN); d.point([(8, 8), (12, 8)], fill=K)
    return im


def crown():
    im = Image.new("RGBA", (24, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(1, 15), (1, 3), (6, 8), (12, 0), (18, 8), (23, 3), (23, 15)], fill=GOLD)
    d.rectangle([1, 12, 23, 15], fill=GOLD2); d.rectangle([11, 5, 13, 7], fill=RED); d.point([(5, 12), (12, 12), (19, 12)], fill=SL)
    return im


if __name__ == "__main__":
    sheet([slime(i) for i in range(8)], "slime")
    sheet([slime(i, True) for i in range(8)], "slime_king")
    sheet([oni(i) for i in range(4)], "oni")
    sheet([aura(i) for i in range(6)], "aura", ol=False)
    sheet([aura(i, PUR3, (255, 220, 255, 255), PUR) for i in range(6)], "aura_p", ol=False)
    sheet([lord(i) for i in range(4)], "lord")
    sheet([gob(i) for i in range(2)], "gob")
    sheet([hob(i) for i in range(2)], "hob")
    sheet([human(i) for i in range(2)], "human")
    sheet([villager(i) for i in range(4)], "villager")
    sheet([egg(i) for i in range(3)], "egg")
    single(heart(), "heart"); single(heart(True), "heart_broken"); single(eye(), "eye"); single(crown(), "crown")
