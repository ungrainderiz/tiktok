"""JoJo-arcade-style animated pixel sheets: Anasui, Diver Down (idle/punch), Jolyne, Jotaro."""
import sys, math
sys.path.insert(0, "tools")
from PIL import Image, ImageDraw
from anim_common import outline, K, SK, SK2, WH, BK

PINK, PINK2 = (246, 196, 214, 255), (210, 140, 176, 255)
PURP, PURP2 = (120, 60, 160, 255), (80, 36, 112, 255)
TEAL, TEAL2, TEAL3 = (40, 170, 190, 255), (20, 110, 140, 255), (140, 230, 240, 255)
YEL = (255, 214, 40, 255)
GRN, GRN2 = (60, 190, 110, 255), (30, 120, 70, 255)
DARK = (34, 30, 44, 255)
COAT, COAT2 = (236, 236, 228, 255), (190, 190, 182, 255)


def sheet(frames, name):
    w, h = frames[0].size
    fr = [outline(f) for f in frames] + [outline(frames[0])]
    s = Image.new("RGBA", (w * len(fr), h), (0, 0, 0, 0))
    for i, f in enumerate(fr): s.paste(f, (i * w, 0))
    s.save(f"sprites/{name}.png"); print(name, len(fr) - 1, w, h)


def anasui(i):
    im = Image.new("RGBA", (52, 84), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 1, 2, 1, 0, 1, 2, 1][i]; sw = [0, 1, 2, 1, 0, -1, -2, -1][i]
    # legs (black) in stance
    d.polygon([(18, 54 + b), (24, 54 + b), (20, 83), (13, 83)], fill=DARK); d.polygon([(28, 54 + b), (34, 54 + b), (40, 83), (33, 83)], fill=DARK)
    d.polygon([(14, 10 + b), (38, 10 + b), (42 + sw, 46 + b), (10 + sw, 46 + b)], fill=PINK2)
    # torso purple with cutouts
    d.polygon([(16, 30 + b), (36, 30 + b), (34, 56 + b), (18, 56 + b)], fill=PURP)
    for y in (36, 44): d.ellipse([22, y + b, 30, y + 5 + b], fill=SK)
    # arms crossed-ish pose
    d.line([16, 32 + b, 8, 46 + b], fill=PURP2, width=4); d.line([36, 32 + b, 44, 44 + b], fill=PURP2, width=4)
    d.ellipse([5, 44 + b, 11, 50 + b], fill=SK); d.ellipse([41, 42 + b, 47, 48 + b], fill=SK)
    # long hair behind
    d.rectangle([22, 26 + b, 29, 31 + b], fill=SK2)
    d.ellipse([16, 8 + b, 36, 30 + b], fill=SK)
    d.polygon([(15, 12 + b), (37, 12 + b), (36, 22 + b), (32, 16 + b), (26, 20 + b), (20, 16 + b), (16, 22 + b)], fill=PINK)
    d.rectangle([13, 14 + b, 16, 34 + b], fill=PINK); d.rectangle([36, 14 + b, 39, 34 + b], fill=PINK)
    # studded beanie
    d.pieslice([14, 1 + b, 38, 22 + b], 180, 360, fill=DARK)
    for x in range(17, 37, 4): d.point((x, 8 + b), fill=YEL)
    # eyes + lipstick
    d.rectangle([20, 19 + b, 23, 20 + b], fill=(80, 60, 140, 255)); d.rectangle([29, 19 + b, 32, 20 + b], fill=(80, 60, 140, 255))
    d.line([19, 18 + b, 24, 18 + b], fill=K); d.line([28, 18 + b, 33, 18 + b], fill=K)
    d.line([24, 25 + b, 28, 25 + b], fill=(200, 60, 110, 255))
    return im


def diver(i, punch=False):
    w, h = 64, 96
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = [0, 1, 2, 3, 2, 1, 0, -1][i] if not punch else 0
    # legs
    d.rectangle([22, 60 + f, 29, 94], fill=TEAL2); d.rectangle([35, 60 + f, 42, 94], fill=TEAL2)
    d.rectangle([22, 74, 29, 80], fill=TEAL); d.rectangle([35, 74, 42, 80], fill=TEAL)
    for x in (24, 37): d.text((x, 73), "D", fill=YEL)
    # torso
    d.polygon([(18, 30 + f), (46, 30 + f), (42, 62 + f), (22, 62 + f)], fill=TEAL)
    d.rectangle([24, 34 + f, 40, 46 + f], fill=TEAL2)
    d.text((22, 35 + f), "D", fill=YEL); d.text((36, 35 + f), "D", fill=YEL)
    # tank on back + hoses
    d.rectangle([44, 30 + f, 50, 52 + f], fill=(200, 200, 210, 255)); d.line([47, 30 + f, 40, 22 + f], fill=(90, 90, 100, 255), width=2)
    # arms
    if punch:
        ext = [0, 10, 22, 22][i % 4]
        d.line([20, 34, 8, 52], fill=TEAL2, width=6)
        d.line([44, 34, 48 + ext // 2, 34], fill=TEAL2, width=7); d.rectangle([48 + ext // 2, 30, 56 + ext // 2, 38], fill=TEAL3)
        if ext > 15:
            for k in range(3): d.line([40 - k * 6, 26 + k * 6, 30 - k * 6, 26 + k * 6], fill=WH)
    else:
        d.line([20, 34 + f, 10, 50 + f], fill=TEAL2, width=6); d.line([44, 34 + f, 54, 50 + f], fill=TEAL2, width=6)
        d.ellipse([6, 48 + f, 14, 56 + f], fill=TEAL3); d.ellipse([50, 48 + f, 58, 56 + f], fill=TEAL3)
    # helmet
    d.ellipse([18, 4 + f, 46, 32 + f], fill=TEAL)
    d.ellipse([22, 10 + f, 42, 28 + f], fill=(20, 40, 60, 255))
    for (x, y) in ((27, 16), (36, 16), (31, 22)): d.ellipse([x - 2, y - 2 + f, x + 2, y + 2 + f], fill=TEAL3)
    d.text((29, 4 + f), "D", fill=YEL)
    if not punch: d.point((32, 18 + f), fill=WH if i in (3, 4) else TEAL3)
    return im


def jolyne(i):
    im = Image.new("RGBA", (48, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 1, 1, 0, 0, 1, 1, 0][i]
    d.rectangle([16, 52 + b, 22, 79], fill=GRN2); d.rectangle([26, 52 + b, 32, 79], fill=GRN2)
    d.polygon([(14, 30 + b), (34, 30 + b), (32, 54 + b), (16, 54 + b)], fill=GRN)
    for y in range(32, 52, 5): d.line([16, y + b, 32, y + 4 + b], fill=GRN2)
    d.line([14, 32 + b, 8, 48 + b], fill=SK, width=3); d.line([34, 32 + b, 40, 48 + b], fill=SK, width=3)
    d.rectangle([21, 26 + b, 27, 31 + b], fill=SK2)
    d.ellipse([14, 8 + b, 34, 30 + b], fill=SK)
    hair = (40, 30, 50, 255)
    d.pieslice([12, 5 + b, 36, 26 + b], 180, 360, fill=hair)
    d.ellipse([8, 0 + b, 18, 10 + b], fill=(70, 160, 90, 255)); d.ellipse([30, 0 + b, 40, 10 + b], fill=(70, 160, 90, 255))
    d.line([35, 12 + b, 40 + (i % 2), 40 + b], fill=(230, 200, 60, 255), width=3)
    d.rectangle([18, 18 + b, 21, 19 + b], fill=(60, 120, 200, 255)); d.rectangle([27, 18 + b, 30, 19 + b], fill=(60, 120, 200, 255))
    d.line([22, 24 + b, 26, 24 + b], fill=(200, 80, 90, 255))
    return im


def jotaro(i):
    im = Image.new("RGBA", (52, 84), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = 1 if i in (2, 3, 4, 5) else 0
    d.polygon([(10, 30 + b), (42, 30 + b), (46, 83), (6, 83)], fill=COAT)
    d.line([26, 34 + b, 26, 83], fill=COAT2)
    d.rectangle([20, 30 + b, 32, 44 + b], fill=DARK)
    d.rectangle([22, 24, 30, 31 + b], fill=SK2)
    d.ellipse([16, 8, 36, 30], fill=SK)
    d.polygon([(12, 14), (40, 14), (38, 4), (16, 2)], fill=COAT); d.rectangle([12, 12, 40, 15], fill=DARK)
    d.polygon([(36, 14), (42, 20), (38, 26)], fill=DARK)
    if i == 6: d.line([20, 20, 24, 20], fill=K); d.line([28, 20, 32, 20], fill=K)
    else:
        d.rectangle([20, 19, 24, 20], fill=(40, 120, 110, 255)); d.rectangle([28, 19, 32, 20], fill=(40, 120, 110, 255)); d.line([19, 17, 25, 18], fill=K); d.line([27, 18, 33, 17], fill=K)
    d.line([23, 26, 29, 26], fill=SK2)
    return im


if __name__ == "__main__":
    sheet([anasui(i) for i in range(8)], "anasui_anim")
    sheet([diver(i) for i in range(8)], "diver_anim")
    sheet([diver(i, True) for i in range(4)], "diver_punch")
    sheet([jolyne(i) for i in range(8)], "jolyne_anim")
    sheet([jotaro(i) for i in range(8)], "jotaro_anim")
