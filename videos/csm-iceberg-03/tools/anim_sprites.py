"""Animated pixel-art sheets for episode 3 (Curse Devil). N frames + copy of frame 0."""
import math, sys
sys.path.insert(0, "tools")
from PIL import Image, ImageDraw
from anim_common import outline, K, SK, SK2, GOLD, NAVY, NAVY2, WH, BK, GR, GR2

HAIR = (30, 26, 36, 255)
BONE, BONE2, BONE3 = (226, 218, 196, 255), (170, 160, 138, 255), (120, 110, 96, 255)
RED, RED2 = (224, 40, 58, 255), (140, 16, 28, 255)


def sheet(frames, name):
    w, h = frames[0].size
    fr = [outline(f) for f in frames] + [outline(frames[0])]
    s = Image.new("RGBA", (w * len(fr), h), (0, 0, 0, 0))
    for i, f in enumerate(fr): s.paste(f, (i * w, 0))
    s.save(f"sprites/{name}.png"); print(name, len(fr) - 1, w, h)


def aki(i):
    im = Image.new("RGBA", (48, 58), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    by = 1 if i in (2, 3, 4, 5) else 0
    # nail-sword over the shoulder (behind)
    d.line([38, 2, 30, 40], fill=GR2, width=3); d.line([38, 2, 31, 36], fill=GR, width=1)
    d.rectangle([37, 0, 41, 3], fill=GR2)
    d.polygon([(7, 58), (11, 44 + by), (37, 44 + by), (41, 58)], fill=NAVY2)
    d.polygon([(19, 44 + by), (24, 54), (29, 44 + by)], fill=WH); d.rectangle([23, 46 + by, 24, 54], fill=BK)
    d.rectangle([20, 36, 27, 44 + by], fill=SK2)
    d.ellipse([13, 13, 34, 39], fill=SK)
    d.pieslice([11, 9, 36, 33], 180, 360, fill=HAIR)
    d.polygon([(12, 20), (15, 25), (18, 18), (22, 23), (24, 18), (28, 23), (32, 18), (35, 24), (36, 18), (12, 17)], fill=HAIR)
    d.rectangle([11, 17, 14, 27], fill=HAIR); d.rectangle([33, 17, 36, 27], fill=HAIR)
    sw = [0, 0, 1, 1, 1, 0, 0, -1][i]
    d.ellipse([20 + sw, 2, 27 + sw, 9], fill=HAIR)
    for ex in (16, 27):
        if i == 6:
            d.line([ex, 29, ex + 4, 29], fill=K)
        else:
            d.rectangle([ex, 27, ex + 4, 28], fill=(110, 170, 230, 255)); d.line([ex - 1, 26, ex + 5, 25 if ex > 20 else 26], fill=K)
    d.line([21, 34, 26, 34], fill=SK2)
    return im


def curse(i):
    w, h = 96, 96
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    jaw = [0, 1, 3, 5, 5, 3, 1, 0][i]
    glow = RED if i in (3, 4) else (255, 120, 60, 255)
    # ribcage / torso
    d.ellipse([22, 44, 74, 92], fill=BONE2)
    for k in range(5):
        y = 52 + k * 7
        d.arc([26, y - 6, 70, y + 10], 200, 340, fill=BONE, width=3)
    d.rectangle([46, 46, 50, 92], fill=BONE)
    # claws raised
    sway = [0, 1, 2, 1, 0, -1, -2, -1][i]
    for side in (-1, 1):
        x0 = 48 + side * 26
        d.line([x0, 58, x0 + side * 14, 30 + sway], fill=BONE2, width=5)
        for f in range(3):
            d.line([x0 + side * 14, 30 + sway, x0 + side * (12 + f * 4), 20 + sway - f], fill=BONE, width=2)
    # left head (human skull)
    d.ellipse([18, 8, 46, 40], fill=BONE)
    d.ellipse([22, 18, 29, 26], fill=BK); d.ellipse([34, 18, 41, 26], fill=BK)
    d.point((25, 22), fill=glow); d.point((37, 22), fill=glow)
    d.polygon([(30, 27), (32, 31), (28, 31)], fill=BK)
    d.rectangle([24, 33 + jaw // 2, 40, 38 + jaw], fill=BONE2)
    for x in range(24, 41, 3): d.line([x, 33, x, 35], fill=BK)
    # right head (3 eye slits, long teeth)
    d.ellipse([50, 6, 80, 40], fill=BONE)
    for k in range(3): d.line([56 + k * 7, 16, 59 + k * 7, 22], fill=glow, width=2)
    d.rectangle([54, 30, 76, 34 + jaw], fill=BK)
    for x in range(55, 76, 3): d.polygon([(x, 30), (x + 2, 30), (x + 1, 38 + jaw)], fill=BONE)
    # horns
    d.polygon([(20, 14), (10, 0), (24, 10)], fill=BONE3); d.polygon([(78, 12), (90, 0), (74, 8)], fill=BONE3)
    d.polygon([(42, 10), (46, 0), (48, 10)], fill=BONE3)
    return im


def himeno(i):
    im = Image.new("RGBA", (44, 54), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    by = 1 if i in (2, 3, 4, 5) else 0
    d.polygon([(5, 54), (9, 41 + by), (35, 41 + by), (39, 54)], fill=NAVY2)
    d.polygon([(17, 41 + by), (22, 50), (27, 41 + by)], fill=WH); d.rectangle([21, 43, 22, 50], fill=BK)
    d.rectangle([18, 33, 25, 41 + by], fill=SK2)
    d.ellipse([11, 10, 32, 36], fill=SK)
    hair = (40, 36, 52, 255)
    d.pieslice([8, 5, 35, 31], 180, 360, fill=hair)
    d.polygon([(9, 15), (12, 24), (16, 17), (20, 22), (24, 15), (34, 15), (34, 13), (9, 13)], fill=hair)
    d.rectangle([7, 14, 11, 34], fill=hair); d.rectangle([32, 14, 36, 34], fill=hair)
    # eyepatch over right eye (viewer's left)
    d.rectangle([13, 22, 20, 28], fill=BK); d.line([11, 20, 33, 17], fill=BK)
    if i == 6: d.line([25, 26, 29, 26], fill=K)
    else:
        d.rectangle([25, 24, 29, 26], fill=(150, 110, 200, 255)); d.line([24, 23, 30, 23], fill=K)
    d.line([19, 31, 24, 31], fill=(200, 110, 110, 255))
    return im


def katana(i):
    im = Image.new("RGBA", (44, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    gl = i in (2, 3)
    d.polygon([(5, 60), (9, 46), (35, 46), (39, 60)], fill=(60, 60, 70, 255))
    d.rectangle([18, 38, 25, 46], fill=SK2)
    d.ellipse([11, 18, 32, 42], fill=SK)
    # katana blade through head
    d.polygon([(20, 0), (24, 0), (24, 22), (20, 22)], fill=(222, 228, 236, 255))
    d.line([21, 1, 21, 20], fill=WH if gl else GR)
    d.rectangle([16, 20, 28, 22], fill=GOLD)
    d.rectangle([14, 30, 18, 32], fill=BK); d.rectangle([26, 30, 30, 32], fill=BK)
    d.rectangle([17, 36, 27, 38], fill=RED2)
    # arm blades
    d.line([8, 58, 3, 42], fill=(222, 228, 236, 255), width=2); d.line([36, 58, 41, 42], fill=(222, 228, 236, 255), width=2)
    return im


def hourglass(i, n=8):
    im = Image.new("RGBA", (28, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    wood = (140, 90, 50, 255); sand = (240, 200, 90, 255); glass = (190, 230, 250, 255)
    d.rectangle([2, 0, 25, 3], fill=wood); d.rectangle([2, 36, 25, 39], fill=wood)
    d.polygon([(5, 4), (22, 4), (15, 19), (15, 21), (22, 35), (5, 35), (12, 21), (12, 19)], fill=glass)
    t = i / n
    top = int(14 * (1 - t))
    if top > 0: d.polygon([(13.5 - top * 0.55, 19 - top), (13.5 + top * 0.55, 19 - top), (13.5, 19)], fill=sand)
    bot = int(12 * t) + 2
    d.polygon([(6, 35), (21, 35), (13.5, 35 - bot)], fill=sand)
    if i % 2 == 0: d.line([13, 20, 13, 34], fill=sand)
    else: d.line([14, 20, 14, 34], fill=sand)
    return im


def nail():
    im = Image.new("RGBA", (16, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(6, 0), (9, 0), (9, 58), (7, 66), (6, 58)], fill=(200, 206, 214, 255))
    d.line([7, 1, 7, 56], fill=WH)
    d.rectangle([1, 58, 14, 61], fill=(120, 124, 132, 255))
    d.rectangle([5, 62, 10, 79], fill=(60, 40, 40, 255))
    for y in range(64, 79, 3): d.line([5, y, 10, y + 1], fill=RED2)
    outline(im).save("sprites/nail.png")


if __name__ == "__main__":
    sheet([aki(i) for i in range(8)], "aki_anim")
    sheet([curse(i) for i in range(8)], "curse_anim")
    sheet([himeno(i) for i in range(8)], "himeno_anim")
    sheet([katana(i) for i in range(8)], "katana_anim")
    sheet([hourglass(i) for i in range(8)], "hourglass_anim")
    nail()
