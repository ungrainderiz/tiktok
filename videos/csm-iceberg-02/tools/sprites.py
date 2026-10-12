"""Pixel-art sprites for the Chainsaw Man devils iceberg (original fan-art, drawn procedurally)."""
import sys
from PIL import Image, ImageDraw

OUT = sys.argv[1] if len(sys.argv) > 1 else "sprites"
K = (20, 14, 26, 255)  # outline

C = {
    "or": (240, 132, 36, 255), "or2": (190, 86, 24, 255), "or3": (255, 182, 92, 255),
    "gr": (168, 176, 186, 255), "gr2": (102, 108, 120, 255), "gr3": (222, 228, 236, 255),
    "wh": (246, 244, 240, 255), "bk": (20, 14, 26, 255),
    "sk": (248, 206, 172, 255), "sk2": (220, 160, 124, 255),
    "bl": (246, 214, 104, 255), "bl2": (206, 160, 52, 255), "bl3": (255, 240, 170, 255),
    "rd": (214, 32, 44, 255), "rd2": (140, 16, 28, 255), "rd3": (255, 92, 92, 255),
    "mk": (226, 104, 92, 255), "mk2": (170, 62, 60, 255), "mk3": (246, 150, 128, 255),
    "ye": (255, 210, 40, 255), "ye2": (214, 150, 20, 255),
    "nv": (34, 40, 66, 255), "nv2": (22, 26, 44, 255),
    "sh": (238, 236, 228, 255), "sh2": (196, 196, 206, 255),
    "fx": (232, 112, 40, 255), "fx2": (176, 64, 22, 255), "fx3": (255, 226, 190, 255),
    "fu": (70, 56, 66, 255), "fu2": (44, 34, 44, 255), "fu3": (104, 86, 98, 255),
    "ag": (236, 228, 214, 255), "ag2": (200, 190, 176, 255), "an": (226, 220, 236, 255),
    "bu": (110, 170, 230, 255), "pk": (230, 120, 140, 255), "fl": (196, 86, 96, 255),
}


def canvas(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def outline(im, col=K):
    w, h = im.size
    src = im.load()
    out = im.copy()
    o = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0 and src[nx, ny] != col:
                        o[x, y] = col
                        break
    return out


def px(d, pts, col):
    for p in pts:
        d.point(p, fill=C[col] if isinstance(col, str) else col)


def save(im, name):
    im = outline(im)
    im.save(f"{OUT}/{name}.png")


# ---------------- POCHITA ----------------
def pochita():
    im, d = canvas(44, 40)
    # blade (chainsaw bar from forehead)
    d.rectangle([19, 1, 25, 17], fill=C["gr"])
    d.rectangle([20, 2, 21, 16], fill=C["gr3"])
    for y in range(2, 17, 3):
        px(d, [(18, y), (26, y + 1)], "gr2")
    d.rectangle([18, 15, 26, 18], fill=C["gr2"])
    # body
    d.ellipse([6, 14, 38, 36], fill=C["or"])
    d.ellipse([9, 15, 30, 26], fill=C["or3"])
    d.ellipse([8, 28, 36, 36], fill=C["or2"])
    # legs
    for x in (10, 16, 26, 32):
        d.rectangle([x, 34, x + 3, 38], fill=C["or2"])
    # pull cord handle (tail)
    d.line([38, 26, 42, 22], fill=C["gr2"], width=1)
    d.rectangle([40, 19, 43, 21], fill=C["gr"])
    # eyes
    d.rectangle([14, 22, 16, 24], fill=C["bk"]); px(d, [(14, 22)], "wh")
    d.rectangle([27, 22, 29, 24], fill=C["bk"]); px(d, [(27, 22)], "wh")
    # mouth + teeth
    d.rectangle([17, 27, 26, 30], fill=C["bk"])
    for x in range(17, 27, 2):
        px(d, [(x, 27), (x + 1, 30)], "wh")
    px(d, [(12, 27), (31, 27)], "rd3")
    save(im, "pochita")


# ---------------- POWER ----------------
def power():
    im, d = canvas(44, 52)
    # hair back (long)
    d.rectangle([7, 12, 36, 46], fill=C["bl2"])
    # body / jacket
    d.polygon([(6, 52), (10, 40), (34, 40), (38, 52)], fill=C["nv"])
    d.polygon([(17, 40), (22, 50), (27, 40)], fill=C["sh"])
    d.rectangle([21, 42, 22, 50], fill=C["bk"])
    # neck
    d.rectangle([18, 34, 25, 40], fill=C["sk2"])
    # face
    d.ellipse([11, 10, 32, 36], fill=C["sk"])
    # hair front + bangs
    d.pieslice([8, 4, 35, 30], 180, 360, fill=C["bl"])
    d.polygon([(10, 17), (14, 23), (17, 16), (21, 22), (24, 16), (28, 23), (31, 16), (34, 20), (34, 14), (9, 14)], fill=C["bl"])
    d.rectangle([7, 14, 11, 44], fill=C["bl"])
    d.rectangle([32, 14, 36, 44], fill=C["bl"])
    px(d, [(13, 8), (14, 7), (20, 6), (21, 6), (28, 8)], "bl3")
    # horns
    d.polygon([(11, 6), (13, 0), (16, 5)], fill=C["rd"])
    d.polygon([(27, 5), (30, 0), (32, 6)], fill=C["rd"])
    px(d, [(13, 1), (30, 1)], "rd3")
    # eyes (amber with red cross)
    for ex in (14, 25):
        d.rectangle([ex, 24, ex + 4, 27], fill=C["ye"])
        px(d, [(ex + 2, 24), (ex + 2, 25), (ex + 2, 26), (ex + 2, 27), (ex + 1, 25), (ex + 3, 25), (ex, 25), (ex + 4, 25)], "rd")
        d.line([ex - 1, 23, ex + 5, 23], fill=K)
    # grin with fang
    d.rectangle([17, 30, 26, 32], fill=C["bk"])
    d.rectangle([18, 30, 25, 30], fill=C["wh"])
    px(d, [(19, 31), (24, 31)], "wh")
    px(d, [(13, 29), (30, 29)], "pk")
    save(im, "power")


# ---------------- MAKIMA ----------------
def makima():
    im, d = canvas(44, 52)
    d.rectangle([9, 12, 34, 38], fill=C["mk2"])
    # coat
    d.polygon([(5, 52), (9, 40), (35, 40), (39, 52)], fill=C["nv2"])
    d.polygon([(16, 40), (22, 52), (28, 40)], fill=C["sh"])
    d.rectangle([21, 42, 23, 52], fill=C["bk"])
    d.rectangle([18, 33, 26, 40], fill=C["sk2"])
    d.ellipse([11, 9, 33, 35], fill=C["sk"])
    # hair
    d.pieslice([8, 3, 36, 30], 180, 360, fill=C["mk"])
    d.polygon([(9, 16), (12, 22), (15, 15), (20, 19), (22, 14), (25, 19), (30, 15), (33, 22), (35, 16), (35, 13), (9, 13)], fill=C["mk"])
    d.rectangle([8, 14, 12, 34], fill=C["mk"])
    d.rectangle([32, 14, 36, 30], fill=C["mk"])
    px(d, [(15, 7), (16, 6), (22, 5), (23, 5), (29, 7)], "mk3")
    # braid over right shoulder
    for i, y in enumerate(range(32, 50, 3)):
        d.ellipse([32 - (i % 2), y, 37 - (i % 2), y + 3], fill=C["mk"] if i % 2 else C["mk2"])
    # ringed eyes
    for ex in (14, 25):
        d.rectangle([ex, 22, ex + 4, 26], fill=C["ye"])
        d.rectangle([ex + 1, 23, ex + 3, 25], fill=C["ye2"])
        px(d, [(ex + 2, 24)], "ye")
        d.line([ex - 1, 21, ex + 5, 21], fill=K)
    # calm smile
    d.line([19, 30, 24, 30], fill=C["mk2"])
    px(d, [(18, 29), (25, 29)], "mk2")
    save(im, "makima")


# ---------------- FOX DEVIL ----------------
def fox():
    im, d = canvas(56, 46)
    d.polygon([(4, 2), (20, 14), (8, 24)], fill=C["fx"])
    d.polygon([(52, 2), (36, 14), (48, 24)], fill=C["fx"])
    d.polygon([(7, 7), (16, 14), (10, 19)], fill=C["fx2"])
    d.polygon([(49, 7), (40, 14), (46, 19)], fill=C["fx2"])
    d.ellipse([6, 10, 50, 40], fill=C["fx"])
    d.polygon([(14, 28), (28, 44), (42, 28), (28, 22)], fill=C["fx3"])
    d.ellipse([8, 24, 18, 36], fill=C["fx3"])
    d.ellipse([38, 24, 48, 36], fill=C["fx3"])
    # slit eyes
    d.polygon([(14, 20), (23, 22), (15, 24)], fill=C["ye"])
    d.polygon([(42, 20), (33, 22), (41, 24)], fill=C["ye"])
    px(d, [(18, 22), (38, 22)], "bk")
    # red marks
    d.line([27, 12, 27, 18], fill=C["rd"]); d.line([29, 12, 29, 18], fill=C["rd"])
    # open jaw with teeth
    d.polygon([(19, 32), (37, 32), (33, 41), (23, 41)], fill=C["rd2"])
    for x in range(20, 37, 3):
        d.polygon([(x, 32), (x + 2, 32), (x + 1, 35)], fill=C["wh"])
    d.ellipse([26, 27, 30, 30], fill=C["bk"])
    save(im, "fox")


# ---------------- FUTURE DEVIL ----------------
def future():
    im, d = canvas(40, 60)
    # long head
    d.ellipse([12, 1, 28, 26], fill=C["fu"])
    d.ellipse([14, 3, 22, 14], fill=C["fu3"])
    for (x, y) in ((16, 6), (22, 8), (15, 12), (21, 14), (18, 18), (24, 20)):
        d.ellipse([x, y, x + 3, y + 2], fill=C["ye"])
        px(d, [(x + 1, y + 1)], "bk")
    d.rectangle([16, 22, 24, 24], fill=C["bk"])
    for x in range(16, 25, 2):
        px(d, [(x, 22)], "wh")
    # body
    d.rectangle([17, 25, 23, 29], fill=C["fu"])
    d.polygon([(8, 30), (32, 30), (29, 50), (11, 50)], fill=C["fu"])
    d.ellipse([14, 34, 26, 46], fill=C["fu2"])  # stomach hole
    d.ellipse([16, 36, 24, 44], fill=C["bk"])
    # long arms spread
    d.line([8, 31, 1, 44], fill=C["fu"], width=3)
    d.line([32, 31, 39, 44], fill=C["fu"], width=3)
    # legs
    d.rectangle([12, 50, 16, 59], fill=C["fu"])
    d.rectangle([24, 50, 28, 59], fill=C["fu"])
    save(im, "future")


# ---------------- ANGEL DEVIL ----------------
def angel():
    im, d = canvas(60, 56)
    # wings
    for side in (-1, 1):
        cx = 30 + side * 14
        pts = [(cx, 26), (cx + side * 16, 6), (cx + side * 26, 14), (cx + side * 24, 30), (cx + side * 18, 44), (cx + side * 6, 40)]
        d.polygon(pts, fill=C["wh"])
        for k in range(3):
            d.line([cx + side * (6 + k * 6), 30 + k * 3, cx + side * (14 + k * 4), 14 + k * 6], fill=C["ag2"])
    # halo
    d.ellipse([18, 1, 42, 7], outline=C["ye"], width=2)
    # body
    d.polygon([(16, 56), (20, 44), (40, 44), (44, 56)], fill=C["sh"])
    d.rectangle([29, 46, 30, 56], fill=C["sh2"])
    d.rectangle([26, 38, 33, 44], fill=C["sk2"])
    d.ellipse([19, 14, 41, 40], fill=C["sk"])
    # hair (light, long, messy)
    d.pieslice([16, 8, 44, 36], 180, 360, fill=C["ag"])
    d.polygon([(17, 20), (21, 27), (24, 20), (28, 25), (31, 19), (35, 25), (39, 20), (43, 26), (43, 18), (17, 18)], fill=C["ag"])
    d.rectangle([16, 20, 20, 46], fill=C["ag"])
    d.rectangle([40, 20, 44, 46], fill=C["ag"])
    # sleepy eyes
    for ex in (23, 33):
        d.rectangle([ex, 28, ex + 4, 29], fill=C["bu"])
        d.line([ex - 1, 27, ex + 5, 27], fill=K)
    d.line([28, 35, 31, 35], fill=C["sk2"])
    save(im, "angel")


# ---------------- GUN DEVIL ----------------
def gun():
    im, d = canvas(64, 64)
    import math
    # barrels radiating
    for i in range(14):
        a = i / 14 * math.tau + 0.2
        x1, y1 = 32 + math.cos(a) * 14, 34 + math.sin(a) * 14
        x2, y2 = 32 + math.cos(a) * (28 + (i % 3) * 2), 34 + math.sin(a) * (27 + (i % 3) * 2)
        d.line([x1, y1, x2, y2], fill=C["gr2"], width=3)
        d.line([x1, y1, x2, y2], fill=C["gr"], width=1)
        d.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=C["bk"])
    # flesh mass
    d.ellipse([14, 16, 50, 52], fill=C["fl"])
    d.ellipse([18, 20, 40, 40], fill=C["pk"])
    # embedded pistols
    for (x, y) in ((20, 22), (34, 36), (22, 40), (38, 22)):
        d.rectangle([x, y, x + 8, y + 2], fill=C["gr2"]); d.rectangle([x, y + 2, x + 2, y + 6], fill=C["gr2"])
    # eyes cluster
    for (x, y) in ((26, 28), (32, 26), (29, 32)):
        d.ellipse([x, y, x + 4, y + 3], fill=C["ye"])
        px(d, [(x + 2, y + 1)], "rd")
    save(im, "gun")


# ---------------- ZOMBIE DEVIL ----------------
def zombie():
    im, d = canvas(60, 60)
    zg, zg2, zg3 = (122, 140, 96, 255), (78, 92, 62, 255), (160, 176, 128, 255)
    # hunched body + long arms
    d.ellipse([6, 26, 54, 60], fill=zg2)
    d.line([10, 34, 2, 58], fill=zg2, width=5)
    d.line([50, 34, 58, 58], fill=zg2, width=5)
    for x in (0, 3, 6):
        d.line([x + 1, 57, x, 60], fill=zg3)
    # huge head
    d.ellipse([8, 2, 52, 44], fill=zg)
    d.ellipse([14, 4, 34, 18], fill=zg3)
    # tiny mismatched eyes
    d.rectangle([18, 14, 21, 17], fill=(255, 240, 200, 255)); px(d, [(19, 15)], "rd")
    d.rectangle([37, 13, 41, 18], fill=(255, 240, 200, 255)); px(d, [(39, 15)], "rd")
    # gaping maw
    d.ellipse([14, 22, 46, 42], fill=C["rd2"])
    d.ellipse([18, 26, 42, 40], fill=C["bk"])
    for x in range(15, 45, 3):
        d.polygon([(x, 25), (x + 2, 25), (x + 1, 29)], fill=(236, 226, 190, 255))
        d.polygon([(x + 1, 40), (x + 3, 40), (x + 2, 36)], fill=(236, 226, 190, 255))
    # stitches / rot
    d.line([30, 3, 33, 12], fill=zg2)
    for y in (5, 8, 11):
        d.line([29, y, 33, y - 1], fill=zg2)
    px(d, [(12, 20), (13, 21), (48, 24), (47, 25), (20, 44), (40, 46)], (96, 60, 70, 255))
    # drool
    d.line([26, 42, 26, 48], fill=(180, 220, 160, 255))
    save(im, "zombie")


# ---------------- small icons ----------------
def icons():
    im, d = canvas(11, 10)
    d.polygon([(5, 9), (0, 4), (0, 2), (2, 0), (4, 0), (5, 2), (6, 0), (8, 0), (10, 2), (10, 4)], fill=C["rd"])
    px(d, [(2, 2), (3, 1)], "rd3")
    save(im, "heart")
    im, d = canvas(16, 14)  # cat Nyako
    d.polygon([(2, 0), (5, 4), (1, 6)], fill=C["wh"]); d.polygon([(13, 0), (10, 4), (14, 6)], fill=C["wh"])
    d.ellipse([1, 3, 14, 13], fill=C["wh"])
    px(d, [(5, 7), (10, 7)], "bk"); px(d, [(7, 9), (8, 9)], "pk")
    save(im, "cat")
    im, d = canvas(10, 30)  # sword
    d.rectangle([4, 0, 5, 21], fill=C["gr3"]); d.rectangle([3, 2, 3, 20], fill=C["wh"])
    d.rectangle([0, 21, 9, 22], fill=C["ye"]); d.rectangle([4, 23, 5, 28], fill=C["ye2"])
    save(im, "sword")
    im, d = canvas(14, 9)  # eye
    d.ellipse([0, 0, 13, 8], fill=C["wh"]); d.ellipse([4, 1, 9, 7], fill=C["ye"]); d.rectangle([6, 3, 7, 5], fill=C["bk"])
    save(im, "eye")
    im, d = canvas(12, 12)  # drop
    d.polygon([(6, 0), (11, 7), (6, 11), (1, 7)], fill=C["rd"]); px(d, [(4, 6)], "rd3")
    save(im, "drop")


if __name__ == "__main__":
    for f in (zombie, pochita, power, makima, fox, future, angel, gun, icons):
        f()
    print("ok")


# ---------------- extra sprites for the Angel episode ----------------
def extras():
    # Aki (black hair topknot, suit)
    im, d = canvas(44, 52)
    d.polygon([(6, 52), (10, 40), (34, 40), (38, 52)], fill=C["nv2"])
    d.polygon([(17, 40), (22, 50), (27, 40)], fill=C["sh"])
    d.rectangle([21, 42, 22, 50], fill=C["bk"])
    d.rectangle([18, 33, 25, 40], fill=C["sk2"])
    d.ellipse([11, 10, 32, 36], fill=C["sk"])
    hair = (34, 30, 40, 255)
    d.pieslice([9, 6, 34, 30], 180, 360, fill=hair)
    d.polygon([(10, 17), (13, 22), (16, 15), (20, 20), (22, 15), (26, 20), (30, 15), (33, 21), (34, 15), (10, 14)], fill=hair)
    d.rectangle([9, 14, 12, 24], fill=hair); d.rectangle([31, 14, 34, 24], fill=hair)
    d.ellipse([18, 0, 25, 7], fill=hair)  # topknot
    for ex in (14, 25):
        d.rectangle([ex, 24, ex + 4, 25], fill=C["bu"]); d.line([ex - 1, 23, ex + 5, 22 if ex > 20 else 23], fill=K)
    d.line([19, 31, 24, 31], fill=C["sk2"])
    save(im, "aki")
    # lance
    im, d = canvas(12, 48)
    d.polygon([(6, 0), (11, 10), (6, 14), (1, 10)], fill=C["gr3"]); d.line([6, 1, 6, 12], fill=C["wh"])
    d.rectangle([5, 14, 6, 47], fill=C["ye2"]); d.rectangle([2, 14, 9, 15], fill=C["ye"])
    save(im, "lance")
    # hand reaching (pointing right)
    im, d = canvas(30, 14)
    d.rectangle([0, 3, 14, 11], fill=C["nv"])
    d.rectangle([14, 3, 22, 11], fill=C["sk"])
    d.rectangle([22, 4, 29, 6], fill=C["sk"])
    d.rectangle([22, 7, 27, 8], fill=C["sk2"]); d.rectangle([22, 9, 26, 10], fill=C["sk2"])
    save(im, "hand")
    # villager silhouette
    im, d = canvas(10, 20)
    d.ellipse([2, 0, 7, 5], fill=(60, 50, 70, 255)); d.polygon([(1, 20), (2, 7), (7, 7), (8, 20)], fill=(60, 50, 70, 255))
    save(im, "villager")
    # grave
    im, d = canvas(12, 16)
    d.rectangle([5, 0, 6, 15], fill=(150, 140, 130, 255)); d.rectangle([1, 4, 10, 5], fill=(150, 140, 130, 255))
    save(im, "grave")
    # house
    im, d = canvas(28, 24)
    d.polygon([(0, 11), (14, 0), (27, 11)], fill=(150, 64, 54, 255))
    d.rectangle([3, 11, 24, 23], fill=(214, 188, 150, 255))
    d.rectangle([11, 15, 16, 23], fill=(90, 60, 50, 255)); d.rectangle([5, 14, 8, 17], fill=(255, 220, 120, 255)); d.rectangle([19, 14, 22, 17], fill=(255, 220, 120, 255))
    save(im, "house")


extras()
