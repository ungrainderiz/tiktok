"""Sprites pixel art (style « dossiers ») pour le TikTok Fizz. Chaque planche = N frames + copie de la frame 0."""
import math, os
from PIL import Image, ImageDraw

K = (10, 14, 26, 255)
B1, B2, B3 = (70, 178, 214, 255), (36, 112, 156, 255), (20, 70, 110, 255)   # peau de Fizz
BEL = (196, 238, 242, 255)
FIN, FIN2 = (92, 86, 196, 255), (60, 52, 140, 255)
EYE, PUP = (255, 214, 72, 255), (16, 16, 24, 255)
WH = (246, 246, 240, 255)
TRI, TRI2 = (196, 176, 84, 255), (120, 104, 40, 255)
GOLD, GOLD2 = (255, 200, 60, 255), (200, 130, 30, 255)
RED, RED2 = (196, 44, 52, 255), (120, 24, 34, 255)
SKIN, SKIN2 = (232, 180, 140, 255), (190, 130, 96, 255)
BRN, BRN2 = (110, 70, 40, 255), (70, 42, 24, 255)
GRY, GRY2, GRY3 = (150, 160, 176, 255), (96, 106, 124, 255), (60, 66, 82, 255)
TAN, TAN2 = (222, 186, 132, 255), (170, 128, 80, 255)
OR, OR2 = (250, 140, 40, 255), (200, 90, 20, 255)
PUR, PUR2 = (150, 60, 170, 255), (90, 30, 110, 255)
GRN, GRN2 = (90, 190, 110, 255), (40, 120, 70, 255)


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
    fr = [outline(f) for f in frames] + [outline(frames[0])]
    s = Image.new("RGBA", (w * len(fr), h), (0, 0, 0, 0))
    for i, f in enumerate(fr): s.paste(f, (i * w, 0))
    s.save(f"sprites/{name}.png"); print(name, len(fr) - 1, w, h)


def P(d, x, y, c): d.point((x, y), fill=c)


def trident(d, x, top, bot, glint=False):
    d.rectangle([x, top + 5, x + 1, bot], fill=TRI); d.line([x + 1, top + 5, x + 1, bot], fill=TRI2)
    d.rectangle([x - 3, top + 4, x + 4, top + 5], fill=TRI)
    for px in (x - 3, x, x + 4):
        d.line([px, top + 4, px, top + 1 if px == x else top + 2], fill=TRI)
    d.point((x, top), fill=WH if glint else TRI); d.point((x - 3, top + 1), fill=TRI); d.point((x + 4, top + 1), fill=TRI)


def fizz_body(d, ox, oy, i, mouth="grin", eyes="open", arm_up=False):
    """Fizz ~ 22x28 dans une boîte, origine (ox, oy) = coin haut-gauche de la tête."""
    # crête (nageoire dorsale) sur la tête
    d.polygon([(ox + 5, oy + 4), (ox + 8, oy - 2), (ox + 10, oy + 2), (ox + 12, oy - 4), (ox + 14, oy + 2), (ox + 17, oy - 1), (ox + 17, oy + 5)], fill=FIN)
    # nageoires latérales (oreilles)
    d.polygon([(ox + 1, oy + 7), (ox - 4, oy + 4 + (i % 2)), (ox - 2, oy + 11), (ox + 2, oy + 11)], fill=FIN2)
    d.polygon([(ox + 21, oy + 7), (ox + 26, oy + 4 + (i % 2)), (ox + 24, oy + 11), (ox + 20, oy + 11)], fill=FIN2)
    # tête
    d.ellipse([ox, oy + 1, ox + 22, oy + 18], fill=B1)
    d.chord([ox, oy + 6, ox + 22, oy + 18], 20, 160, fill=B2)
    d.ellipse([ox + 2, oy + 2, ox + 20, oy + 15], fill=B1)
    # yeux
    if eyes == "open":
        for ex in (ox + 4, ox + 12):
            d.ellipse([ex, oy + 5, ex + 6, oy + 11], fill=EYE)
            d.rectangle([ex + 3, oy + 7, ex + 4, oy + 9], fill=PUP); d.point((ex + 2, oy + 6), fill=WH)
        d.line([ox + 4, oy + 4, ox + 9, oy + 5], fill=B3); d.line([ox + 13, oy + 5, ox + 18, oy + 4], fill=B3)
    elif eyes == "closed":
        for ex in (ox + 4, ox + 12): d.line([ex, oy + 9, ex + 3, oy + 7], fill=K); d.line([ex + 3, oy + 7, ex + 6, oy + 9], fill=K)
    else:  # demi-fermés (malicieux)
        for ex in (ox + 4, ox + 12):
            d.rectangle([ex, oy + 7, ex + 6, oy + 10], fill=EYE); d.line([ex, oy + 7, ex + 6, oy + 7], fill=B3); d.rectangle([ex + 3, oy + 8, ex + 4, oy + 9], fill=PUP)
    # bouche
    if mouth == "grin":
        d.line([ox + 6, oy + 13, ox + 16, oy + 13], fill=K); d.line([ox + 7, oy + 14, ox + 15, oy + 14], fill=WH)
        d.point((ox + 5, oy + 12), fill=K); d.point((ox + 17, oy + 12), fill=K)
    else:  # ouverte (rire)
        d.rectangle([ox + 7, oy + 12, ox + 15, oy + 16], fill=(120, 20, 40, 255)); d.line([ox + 7, oy + 12, ox + 15, oy + 12], fill=WH)
    # corps
    by = oy + 18
    d.rectangle([ox + 6, by, ox + 16, by + 7], fill=B1); d.rectangle([ox + 8, by + 1, ox + 14, by + 6], fill=BEL)
    # jambes
    d.rectangle([ox + 6, by + 7, ox + 9, by + 10], fill=B2); d.rectangle([ox + 13, by + 7, ox + 16, by + 10], fill=B2)
    d.rectangle([ox + 5, by + 10, ox + 9, by + 11], fill=B3); d.rectangle([ox + 13, by + 10, ox + 17, by + 11], fill=B3)
    # bras
    d.rectangle([ox + 3, by + 1, ox + 5, by + 5], fill=B2)
    if arm_up: d.rectangle([ox + 17, by - 4, ox + 19, by + 1], fill=B2)
    else: d.rectangle([ox + 17, by + 1, ox + 19, by + 4], fill=B2)


def fizz_idle(i):
    im = Image.new("RGBA", (40, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bob = [0, 0, 1, 1, 1, 0, 0, -1][i]
    trident(d, 31, 2 + bob, 41, glint=i in (2, 3))
    fizz_body(d, 8, 12 + bob, i, eyes="closed" if i == 6 else "open")
    return im


def fizz_laugh(i):
    im = Image.new("RGBA", (40, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    j = [0, -3, -1, 0, -3, -1, 0, -2][i]
    trident(d, 32, 4 + j, 43)
    fizz_body(d, 8, 14 + j, i, mouth="open", eyes="closed", arm_up=i % 2 == 0)
    return im


def fizz_sly(i):
    im = Image.new("RGBA", (40, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bob = [0, 0, 1, 1, 1, 0, 0, -1][i]
    trident(d, 31, 2 + bob, 41, glint=i in (4, 5))
    fizz_body(d, 8, 12 + bob, i, eyes="sly")
    return im


def fizz_hop(i):
    """Fizz en équilibre sur son trident (E)."""
    im = Image.new("RGBA", (36, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sw = [0, 1, 1, 0, 0, -1, -1, 0][i]
    d.rectangle([17, 32, 18, 63], fill=TRI); d.line([18, 32, 18, 63], fill=TRI2)
    d.rectangle([14, 30, 21, 31], fill=TRI)
    fizz_body(d, 6 + sw, 2, i, eyes="sly", arm_up=True)
    return im


def fizz_swim(i):
    im = Image.new("RGBA", (44, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = [0, 1, 2, 1, 0, -1, -2, -1][i]
    d.polygon([(0, 14 + k), (8, 11), (8, 18), (0, 18 - k)], fill=B2)           # jambes / palmes
    d.ellipse([6, 9, 26, 21], fill=B1); d.rectangle([10, 15, 24, 19], fill=BEL)
    d.polygon([(14, 9), (17, 3), (20, 9)], fill=FIN)
    d.ellipse([22, 4, 40, 22], fill=B1); d.polygon([(28, 4), (31, -1 + 2), (34, 4)], fill=FIN)
    d.ellipse([31, 8, 37, 14], fill=EYE); d.rectangle([34, 10, 35, 12], fill=PUP)
    d.line([30, 17, 37, 17], fill=K)
    return im


def shark(i):
    """Requin qui jaillit, gueule ouverte (0-3) puis fermée (4-7)."""
    im = Image.new("RGBA", (48, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    op = i < 4
    d.polygon([(8, 46), (6, 20), (14, 6), (24, 0), (34, 6), (42, 20), (40, 46)], fill=GRY)
    d.polygon([(14, 46), (16, 24), (24, 14), (32, 24), (34, 46)], fill=(214, 220, 228, 255))
    if op:
        d.polygon([(12, 22), (24, 8), (36, 22), (30, 34), (18, 34)], fill=(110, 20, 40, 255))
        for x in range(14, 35, 4): d.polygon([(x, 22 - (2 if 18 < x < 30 else 0)), (x + 2, 22 - (2 if 18 < x < 30 else 0)), (x + 1, 26)], fill=WH)
        for x in range(18, 31, 4): d.polygon([(x, 34), (x + 2, 34), (x + 1, 30)], fill=WH)
    else:
        d.line([12, 24, 36, 24], fill=K);
        for x in range(14, 35, 3): d.line([x, 23, x + 1, 25], fill=WH)
    d.rectangle([12, 14, 14, 16], fill=K); d.rectangle([34, 14, 36, 16], fill=K)
    for y in (30, 34, 38): d.line([8, y, 11, y - 1], fill=GRY2); d.line([40, y, 37, y - 1], fill=GRY2)
    return im


def fish(i):
    im = Image.new("RGBA", (16, 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = [0, 1, 0, -1][i % 4]
    d.ellipse([3, 2, 13, 8], fill=OR); d.polygon([(4, 5), (0, 2 + k), (0, 8 + k)], fill=OR2)
    d.point((10, 4), fill=K); d.line([6, 3, 8, 7], fill=OR2)
    return im


def captain(i):
    im = Image.new("RGBA", (30, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 0, 1, 1, 1, 0, 0, -1][i]
    d.polygon([(4, 9 + b), (26, 9 + b), (22, 3 + b), (15, 1 + b), (8, 3 + b)], fill=(34, 30, 40, 255))   # tricorne
    d.line([6, 8 + b, 24, 8 + b], fill=GOLD)
    d.rectangle([9, 10 + b, 21, 19 + b], fill=SKIN); d.rectangle([9, 15 + b, 21, 22 + b], fill=(150, 150, 160, 255))  # barbe grise
    d.point((12, 13 + b), fill=K); d.point((18, 13 + b), fill=K); d.line([11, 11 + b, 13, 11 + b], fill=K); d.line([17, 11 + b, 19, 11 + b], fill=K)
    d.rectangle([7, 22 + b, 23, 36], fill=RED); d.rectangle([14, 22 + b, 16, 36], fill=GOLD2); d.rectangle([7, 30, 23, 31], fill=BRN2)
    d.rectangle([4, 23 + b, 6, 32], fill=RED2); d.rectangle([24, 23 + b, 26, 32], fill=RED2)
    d.rectangle([9, 37, 13, 44], fill=BRN2); d.rectangle([17, 37, 21, 44], fill=BRN2)
    d.rectangle([17, 37, 18, 45], fill=BRN)  # jambe de bois
    return im


def captain_throw(i):
    im = captain(0); d = ImageDraw.Draw(im)
    d.rectangle([24, 14, 26, 24], fill=RED2); d.rectangle([24, 12, 27, 14], fill=SKIN)
    return im


def mage(i):
    im = Image.new("RGBA", (30, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = [0, 1, 1, 0, 0, -1, -1, 0][i]
    d.polygon([(15, 0), (24, 14), (26, 44), (4, 44), (6, 14)], fill=PUR)
    d.polygon([(15 + s, 30), (22, 44), (8, 44)], fill=PUR2)
    d.ellipse([8, 8, 22, 20], fill=(20, 10, 30, 255)); d.rectangle([11, 13, 12, 14], fill=(255, 90, 90, 255)); d.rectangle([17, 13, 18, 14], fill=(255, 90, 90, 255))
    g = (255, 120, 220, 255) if i % 2 else (255, 200, 250, 255)
    d.ellipse([0, 22 + s, 6, 28 + s], fill=g); d.ellipse([24, 22 - s, 30, 28 - s], fill=g)
    return im


def ally(i):
    im = Image.new("RGBA", (26, 36), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    b = [0, 0, 1, 1, 1, 0, 0, -1][i]
    d.ellipse([4, 2 + b, 22, 18 + b], fill=(240, 200, 160, 255)); d.chord([3, 0 + b, 23, 16 + b], 180, 360, fill=GRY)   # casque
    d.rectangle([12, -1 + b, 14, 3 + b], fill=RED)
    d.point((9, 10 + b), fill=K); d.point((16, 10 + b), fill=K); d.line([10, 14 + b, 15, 14 + b], fill=K)
    d.rectangle([6, 18 + b, 20, 30], fill=GRN); d.rectangle([6, 23, 20, 24], fill=GRN2)
    d.rectangle([7, 30, 11, 35], fill=BRN2); d.rectangle([15, 30, 19, 35], fill=BRN2)
    d.rectangle([20, 19 + b, 22, 27], fill=GRY2)   # bouclier
    return im


def dog(i):
    """Fizz version chien."""
    im = Image.new("RGBA", (40, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = [0, 1, 2, 1, 0, -1, -2, -1][i]
    d.polygon([(4, 14), (0, 8 + w), (2, 7 + w), (7, 13)], fill=TAN2)  # queue
    d.rectangle([5, 14, 27, 24], fill=TAN); d.rectangle([7, 20, 25, 24], fill=(246, 230, 200, 255))
    d.rectangle([6, 24, 9, 31], fill=TAN2); d.rectangle([22, 24, 25, 31], fill=TAN2)
    d.ellipse([20, 2, 38, 18], fill=TAN)
    d.polygon([(21, 4), (18, 14), (24, 10)], fill=BRN); d.polygon([(36, 4), (39, 14), (33, 10)], fill=BRN)
    d.ellipse([24, 6, 29, 11], fill=EYE); d.rectangle([26, 8, 27, 9], fill=PUP)
    d.ellipse([31, 6, 36, 11], fill=EYE); d.rectangle([33, 8, 34, 9], fill=PUP)
    d.rectangle([28, 12, 31, 13], fill=K); d.rectangle([27, 14, 33, 16], fill=(246, 230, 200, 255))
    if i in (2, 3, 6): d.rectangle([30, 16, 31, 18], fill=(230, 90, 110, 255))  # langue
    d.rectangle([12, 13, 22, 15], fill=(60, 150, 200, 255)); d.point((17, 16), fill=GOLD)    # collier
    return im


def jelly(i):
    im = Image.new("RGBA", (18, 22), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    p = [0, 1, 2, 1][i % 4]
    d.chord([1 + p, 0, 17 - p, 12], 180, 360, fill=(170, 120, 230, 255)); d.rectangle([1 + p, 6, 17 - p, 7], fill=(130, 90, 200, 255))
    for x in range(4, 15, 3): d.line([x, 8, x + (1 if (x + i) % 2 else -1), 20], fill=(200, 160, 250, 255))
    return im


def static():
    def save(im, name): outline(im).save(f"sprites/{name}.png"); print(name, im.size)
    im = Image.new("RGBA", (8, 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.ellipse([0, 0, 7, 7], fill=GOLD); d.rectangle([3, 2, 4, 5], fill=GOLD2); save(im, "coin")
    im = Image.new("RGBA", (22, 18), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([1, 6, 20, 17], fill=BRN); d.chord([1, 0, 20, 12], 180, 360, fill=BRN2); d.rectangle([1, 9, 20, 10], fill=GOLD2); d.rectangle([9, 8, 12, 12], fill=GOLD); save(im, "chest")
    im = Image.new("RGBA", (10, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([3, 0, 6, 4], fill=BRN); d.rectangle([1, 4, 8, 15], fill=(80, 160, 110, 255)); d.rectangle([2, 7, 7, 11], fill=(230, 220, 190, 255)); save(im, "bottle")
    # navire de Bilgewater
    im = Image.new("RGBA", (80, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(4, 44), (76, 44), (68, 60), (12, 60)], fill=BRN); d.rectangle([4, 44, 76, 46], fill=BRN2)
    for x in range(16, 66, 10): d.rectangle([x, 50, x + 3, 53], fill=(40, 24, 14, 255))
    d.rectangle([38, 4, 40, 44], fill=BRN2); d.rectangle([20, 18, 30, 44], fill=BRN2)
    d.polygon([(41, 6), (66, 10), (64, 36), (41, 38)], fill=(40, 36, 48, 255)); d.polygon([(22, 18), (21, 40), (35, 38), (35, 20)], fill=(52, 46, 60, 255))
    d.ellipse([49, 15, 57, 23], fill=WH); d.rectangle([51, 23, 55, 26], fill=WH); d.point((51, 18), fill=K); d.point((55, 18), fill=K)
    d.polygon([(39, 0), (39, 5), (48, 2)], fill=RED)
    save(im, "ship")
    # aileron de requin (pour les cercles)
    im = Image.new("RGBA", (16, 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.polygon([(0, 11), (10, 0), (15, 11)], fill=GRY2); save(im, "fin")
    # gouttes d'eau
    im = Image.new("RGBA", (6, 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.polygon([(3, 0), (5, 5), (3, 7), (1, 5)], fill=(120, 210, 250, 255)); save(im, "drop")
    # cœur cassé / colère
    im = Image.new("RGBA", (11, 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(0, 3), (2, 0), (5, 2), (8, 0), (10, 3), (5, 9)], fill=RED); d.line([5, 2, 4, 5, 6, 7], fill=K); save(im, "heartbreak")
    im = Image.new("RGBA", (11, 11), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for a, b in ((0, 3), (3, 0)): d.rectangle([a, b, a + 3, b + 3], fill=RED)
    d.rectangle([7, 3, 10, 6], fill=RED); d.rectangle([3, 7, 6, 10], fill=RED); save(im, "anger")


if __name__ == "__main__":
    os.makedirs("sprites", exist_ok=True)
    sheet([fizz_idle(i) for i in range(8)], "fizz_idle")
    sheet([fizz_laugh(i) for i in range(8)], "fizz_laugh")
    sheet([fizz_sly(i) for i in range(8)], "fizz_sly")
    sheet([fizz_hop(i) for i in range(8)], "fizz_hop")
    sheet([fizz_swim(i) for i in range(8)], "fizz_swim")
    sheet([shark(i) for i in range(8)], "shark")
    sheet([fish(i) for i in range(4)], "fish")
    sheet([captain(i) for i in range(8)], "captain")
    sheet([mage(i) for i in range(8)], "mage")
    sheet([ally(i) for i in range(8)], "ally")
    sheet([dog(i) for i in range(8)], "dog")
    sheet([jelly(i) for i in range(4)], "jelly")
    outline(captain_throw(0)).save("sprites/captain_throw.png")
    static()
