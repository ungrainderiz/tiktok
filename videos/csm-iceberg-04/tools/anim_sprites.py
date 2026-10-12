"""Animated pixel sheets for episode 4 (Doll Devil). N frames + copy of frame 0."""
import sys
sys.path.insert(0, "tools")
from PIL import Image, ImageDraw
from anim_common import outline, K, SK, SK2, GOLD, NAVY2, WH, BK, GR, GR2

RED = (224, 40, 58, 255); RED2 = (140, 16, 28, 255)
COAT = (110, 24, 34, 255); COAT2 = (70, 14, 22, 255)
PORC, PORC2 = (240, 226, 214, 255), (200, 180, 170, 255)
WOOD, WOOD2 = (176, 120, 72, 255), (120, 76, 42, 255)


def sheet(frames, name):
    w, h = frames[0].size
    fr = [outline(f) for f in frames] + [outline(frames[0])]
    s = Image.new("RGBA", (w * len(fr), h), (0, 0, 0, 0))
    for i, f in enumerate(fr): s.paste(f, (i * w, 0))
    s.save(f"sprites/{name}.png"); print(name, len(fr) - 1, w, h)


def santa(i):
    im = Image.new("RGBA", (48, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    by = 1 if i in (2, 3, 4, 5) else 0
    d.polygon([(4, 60), (9, 44 + by), (39, 44 + by), (44, 60)], fill=COAT2)
    d.rectangle([22, 46 + by, 25, 60], fill=GOLD)
    d.ellipse([13, 14, 35, 40], fill=SK)
    # long white beard
    d.polygon([(13, 30), (35, 30), (32, 50), (24, 56), (16, 50)], fill=WH)
    d.rectangle([17, 33, 31, 35], fill=(220, 220, 220, 255))
    # hat
    d.polygon([(11, 18), (37, 18), (30, 2), (20, 4)], fill=COAT); d.rectangle([10, 16, 38, 20], fill=WH)
    d.ellipse([28, 0, 33, 5], fill=WH)
    # eyes: dark, glow red on frames 3-5
    glow = i in (3, 4, 5)
    for ex in (17, 27):
        d.rectangle([ex, 25, ex + 4, 27], fill=RED if glow else BK)
        if glow: d.point((ex + 2, 26), fill=(255, 220, 200, 255))
    d.line([16, 23, 22, 24], fill=WH); d.line([26, 24, 32, 23], fill=WH)
    return im


def doll(i):
    im = Image.new("RGBA", (36, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tilt = [0, 0, 2, 2, 0, -2, -2, 0][i]
    arm = [0, 0, 0, 4, 4, 0, 0, 0][i]
    # strings from top
    for x in (10, 18, 26): d.line([x, 0, x + tilt // 2, 14], fill=(220, 220, 230, 255))
    # head (porcelain), tilted by shifting
    hx = 8 + tilt
    d.ellipse([hx, 10, hx + 20, 30], fill=PORC)
    d.line([hx + 4, 18, hx + 8, 22], fill=BK); d.line([hx + 8, 18, hx + 4, 22], fill=BK)
    d.line([hx + 12, 18, hx + 16, 22], fill=BK); d.line([hx + 16, 18, hx + 12, 22], fill=BK)
    d.line([hx + 6, 26, hx + 14, 26], fill=RED2)
    for x in range(hx + 7, hx + 14, 2): d.line([x, 25, x, 27], fill=BK)
    d.ellipse([hx + 2, 22, hx + 4, 24], fill=(240, 150, 160, 255)); d.ellipse([hx + 16, 22, hx + 18, 24], fill=(240, 150, 160, 255))
    # body with joints
    d.rectangle([12, 31, 24, 46], fill=(90, 70, 110, 255))
    d.ellipse([16, 30, 20, 33], fill=WOOD)
    # arms (one becomes blade)
    d.line([12, 33, 6, 44 - arm], fill=WOOD, width=3); d.ellipse([10, 32, 13, 35], fill=WOOD2)
    d.line([24, 33, 30, 40 - arm], fill=WOOD, width=3)
    d.polygon([(30, 40 - arm), (35, 30 - arm), (31, 42 - arm)], fill=(222, 228, 236, 255))
    # legs
    d.line([15, 46, 13, 59], fill=WOOD, width=3); d.line([21, 46, 23, 59], fill=WOOD, width=3)
    d.ellipse([12, 50, 15, 53], fill=WOOD2); d.ellipse([21, 50, 24, 53], fill=WOOD2)
    return im


def marionette(i):
    im = Image.new("RGBA", (60, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sw = [0, 2, 4, 2, 0, -2, -4, -2][i]
    # control cross
    d.rectangle([18 + sw, 2, 42 + sw, 5], fill=WOOD); d.rectangle([28 + sw, 0, 31 + sw, 12], fill=WOOD)
    sil = (24, 10, 30, 255)
    for (x0, x1) in ((19, 16), (41, 44), (29, 30)):
        d.line([x0 + sw, 4, x1, 30], fill=(200, 200, 220, 255))
    # silhouette doll with glowing eyes
    d.ellipse([20, 24, 40, 44], fill=sil)
    d.ellipse([24, 31, 28, 35], fill=RED); d.ellipse([32, 31, 36, 35], fill=RED)
    d.polygon([(22, 44), (38, 44), (42, 64), (18, 64)], fill=sil)
    d.line([20, 46, 12 - sw // 2, 58], fill=sil, width=4); d.line([40, 46, 48 - sw // 2, 58], fill=sil, width=4)
    d.line([25, 64, 23, 78], fill=sil, width=4); d.line([35, 64, 37, 78], fill=sil, width=4)
    d.text((26, 48), "?", fill=GOLD)
    return im


if __name__ == "__main__":
    sheet([santa(i) for i in range(8)], "santa_anim")
    sheet([doll(i) for i in range(8)], "doll_anim")
    sheet([marionette(i) for i in range(8)], "marionette_anim")
