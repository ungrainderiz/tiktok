"""Pixel art : carte polaire (USA / URSS / Japon), Yoru, missiles, champignon nucléaire, explosions, drapeaux."""
import json, math, os
from PIL import Image, ImageDraw

K = (12, 8, 14, 255)
RED, RED2, RED3 = (232, 35, 59, 255), (150, 16, 34, 255), (255, 120, 120, 255)
WH, GRY, GRY2 = (240, 236, 232, 255), (150, 146, 156, 255), (80, 76, 90, 255)
SKIN, SKIN2 = (246, 222, 206, 255), (214, 180, 166, 255)
HAIR, HAIR2 = (22, 18, 28, 255), (48, 40, 58, 255)
BLUE, BLUE2 = (61, 107, 255, 255), (30, 60, 170, 255)
GOLD, OR, OR2, YEL = (255, 210, 60, 255), (255, 140, 40, 255), (210, 70, 20, 255), (255, 240, 150, 255)


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


# ---------- carte polaire pixel ----------
LAT_MIN, SZ, LON0 = 12.0, 200, -170.0
USSR = {"Russia", "Ukraine", "Belarus", "Kazakhstan", "Uzbekistan", "Turkmenistan", "Kyrgyzstan", "Tajikistan", "Georgia", "Armenia", "Azerbaijan", "Moldova", "Lithuania", "Latvia", "Estonia"}
def proj(lon, lat):
    r = (90 - lat) / (90 - LAT_MIN) * (SZ / 2 - 2); a = math.radians(lon - LON0)
    return SZ / 2 - r * math.sin(a), SZ / 2 - r * math.cos(a)
def polys(geom):
    if geom["type"] == "Polygon": return [geom["coordinates"]]
    return geom["coordinates"]
def build_map():
    geo = json.load(open("src/geo/countries.geo.json"))
    im = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([1, 1, SZ - 2, SZ - 2], fill=(14, 22, 40, 255))
    for lat in (30, 50, 70):
        r = (90 - lat) / (90 - LAT_MIN) * (SZ / 2 - 2); d.ellipse([SZ / 2 - r, SZ / 2 - r, SZ / 2 + r, SZ / 2 + r], outline=(30, 44, 70, 255))
    order = sorted(geo["features"], key=lambda f: (f["properties"]["name"] in USSR or f["properties"]["name"] in ("United States of America", "Japan")))
    for f in order:
        n = f["properties"]["name"]
        col = RED if n in USSR else BLUE if n == "United States of America" else WH if n == "Japan" else (70, 66, 82, 255)
        for p in polys(f["geometry"]):
            ring = [(lo, la) for lo, la in p[0] if la > LAT_MIN - 6]
            if len(ring) < 3: continue
            pts = [proj(lo, max(la, LAT_MIN - 6)) for lo, la in ring]
            d.polygon(pts, fill=col)
    mask = Image.new("L", (SZ, SZ), 0); ImageDraw.Draw(mask).ellipse([1, 1, SZ - 2, SZ - 2], fill=255)
    out = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0)); out.paste(im, (0, 0), mask)
    d = ImageDraw.Draw(out); d.ellipse([0, 0, SZ - 1, SZ - 1], outline=(200, 40, 60, 255), width=2)
    out.save("sprites/map.png")
    # trajectoire grand cercle NY -> Tokyo
    def xyz(lo, la): lo, la = math.radians(lo), math.radians(la); return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
    A, B = xyz(-74.0, 40.71), xyz(139.69, 35.68); om = math.acos(sum(a * b for a, b in zip(A, B)))
    path = []
    for i in range(41):
        t = i / 40; s1, s2 = math.sin((1 - t) * om) / math.sin(om), math.sin(t * om) / math.sin(om)
        v = [s1 * a + s2 * b for a, b in zip(A, B)]; la = math.degrees(math.asin(v[2])); lo = math.degrees(math.atan2(v[1], v[0]))
        path.append([round(c / SZ, 4) for c in proj(lo, la)])
    pts = {k: [round(c / SZ, 4) for c in proj(*v)] for k, v in {"ny": (-74.0, 40.71), "tokyo": (139.69, 35.68), "moscow": (37.6, 55.75), "washington": (-77.0, 38.9), "gulf": (-90.0, 25.0), "elbrus": (42.4, 43.35)}.items()}
    json.dump({"path": path, "pts": pts}, open("sprites/map.json", "w")); print("map", pts)


# ---------- Yoru ----------
def yoru(i):
    im = Image.new("RGBA", (40, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sw = [0, 1, 1, 0, 0, -1, -1, 0][i]; b = [0, 0, 1, 1, 1, 0, 0, 0][i]
    d.polygon([(9, 12), (31, 12), (34 + sw, 44), (6 + sw, 44)], fill=HAIR)                     # cheveux longs (dos)
    d.rectangle([12, 30 + b, 28, 50], fill=WH); d.rectangle([12, 30 + b, 13, 50], fill=GRY)   # chemise
    d.polygon([(18, 31 + b), (22, 31 + b), (20, 38 + b)], fill=RED)                           # nœud
    d.rectangle([11, 46, 29, 54], fill=(40, 36, 56, 255))                                     # jupe
    d.rectangle([14, 54, 17, 59], fill=SKIN2); d.rectangle([23, 54, 26, 59], fill=SKIN2)
    d.rectangle([8, 31 + b, 11, 46], fill=WH); d.rectangle([29, 31 + b, 32, 46], fill=WH)     # bras
    d.rectangle([8, 46, 11, 49], fill=SKIN); d.rectangle([29, 46, 32, 49], fill=SKIN)
    d.ellipse([11, 8 + b, 29, 30 + b], fill=SKIN)                                              # visage
    d.chord([9, 4 + b, 31, 22 + b], 180, 360, fill=HAIR); d.polygon([(10, 13 + b), (14, 18 + b), (17, 13 + b), (21, 18 + b), (24, 13 + b), (28, 17 + b), (30, 12 + b), (10, 11 + b)], fill=HAIR)
    d.rectangle([9, 12 + b, 12, 32 + b], fill=HAIR); d.rectangle([28, 12 + b, 31, 32 + b], fill=HAIR)
    glow = RED3 if i in (2, 3, 6) else RED
    for ex in (14, 22):                                                                         # yeux à anneaux
        d.ellipse([ex, 17 + b, ex + 4, 21 + b], fill=WH); d.ellipse([ex + 1, 18 + b, ex + 3, 20 + b], fill=glow); d.point((ex + 2, 19 + b), fill=K)
    for k in range(3): d.line([12 + k, 23 + b + k % 2, 15 + k, 23 + b + k % 2], fill=RED2); d.line([25 + k, 23 + b + k % 2, 28 + k, 23 + b + k % 2], fill=RED2)  # cicatrices
    d.line([18, 26 + b, 22, 26 + b], fill=RED2)
    return im


def missile(i, n=4):
    im = Image.new("RGBA", (14, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(7, 0), (11, 7), (3, 7)], fill=RED); d.rectangle([3, 7, 10, 30], fill=WH); d.rectangle([3, 14, 10, 16], fill=RED)
    d.polygon([(3, 24), (0, 32), (3, 30)], fill=GRY2); d.polygon([(10, 24), (13, 32), (10, 30)], fill=GRY2)
    fl = [8, 12, 9, 13][i % n]
    d.polygon([(4, 31), (9, 31), (6.5, 31 + fl)], fill=OR); d.polygon([(5, 31), (8, 31), (6.5, 31 + fl * 0.6)], fill=YEL)
    return im


def nuke(i, n=8):
    im = Image.new("RGBA", (80, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g = (i + 1) / n
    sh = int(10 + 50 * g); cw = int(14 + 44 * g); ch = int(10 + 22 * g)
    d.rectangle([40 - 5, 80 - sh, 40 + 5, 79], fill=(250, 170, 80, 255)); d.rectangle([40 - 3, 80 - sh, 40 + 3, 79], fill=YEL)
    cy = 80 - sh
    d.ellipse([40 - cw // 2, cy - ch, 40 + cw // 2, cy + ch // 2], fill=OR); d.ellipse([40 - cw // 2 + 4, cy - ch + 3, 40 + cw // 2 - 4, cy], fill=YEL)
    d.ellipse([40 - cw // 2 - 4, cy - ch // 3, 40 - cw // 4, cy + ch // 2], fill=OR2); d.ellipse([40 + cw // 4, cy - ch // 3, 40 + cw // 2 + 4, cy + ch // 2], fill=OR2)
    d.ellipse([40 - cw // 2 - 6, 70, 40 + cw // 2 + 6, 79], fill=(200, 80, 40, 255))
    return im


def boom(i, n=8):
    im = Image.new("RGBA", (40, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = 4 + i * 2.2; c = 20
    if i < n - 1:
        d.ellipse([c - r, c - r, c + r, c + r], fill=OR if i > 2 else YEL); d.ellipse([c - r * 0.6, c - r * 0.6, c + r * 0.6, c + r * 0.6], fill=YEL if i > 2 else WH)
        for k in range(8):
            a = k / 8 * math.tau; d.rectangle([c + math.cos(a) * (r + 3) - 1, c + math.sin(a) * (r + 3) - 1, c + math.cos(a) * (r + 3) + 1, c + math.sin(a) * (r + 3) + 1], fill=OR2)
    else:
        d.ellipse([c - r, c - r, c + r, c + r], outline=(120, 110, 110, 255))
    return im


def flags():
    im = Image.new("RGBA", (30, 18), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(7): d.rectangle([0, k * 18 / 7, 29, (k + 1) * 18 / 7 - 1], fill=RED if k % 2 == 0 else WH)
    d.rectangle([0, 0, 12, 9], fill=BLUE2)
    for x in range(2, 12, 3):
        for y in range(2, 9, 3): d.point((x, y), fill=WH)
    outline(im).save("sprites/flag_usa.png")
    im = Image.new("RGBA", (30, 18), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 29, 17], fill=RED)
    d.polygon([(5, 2), (6, 4), (8, 4), (6.5, 5.5), (7, 7.5), (5, 6.3), (3, 7.5), (3.5, 5.5), (2, 4), (4, 4)], fill=GOLD)
    d.arc([3, 7, 10, 14], 200, 340, fill=GOLD); d.line([4, 13, 9, 8], fill=GOLD)
    outline(im).save("sprites/flag_ussr.png")


def finger():
    im = Image.new("RGBA", (16, 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([5, 0, 9, 12], fill=SKIN); d.rectangle([2, 10, 14, 23], fill=SKIN); d.rectangle([2, 10, 14, 11], fill=SKIN2)
    for x in (4, 8, 12): d.line([x, 12, x, 16], fill=SKIN2)
    outline(im).save("sprites/finger.png")
    im2 = im.copy(); d = ImageDraw.Draw(im2); d.rectangle([4, 0, 10, 9], fill=(0, 0, 0, 0)); d.rectangle([5, 8, 9, 10], fill=RED); outline(im2).save("sprites/finger_cut.png")


def radiation():
    im = Image.new("RGBA", (40, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 39, 39], fill=GOLD)
    for a in (90, 210, 330): d.pieslice([4, 4, 35, 35], a - 30, a + 30, fill=K)
    d.ellipse([15, 15, 24, 24], fill=GOLD); d.ellipse([17, 17, 22, 22], fill=K)
    outline(im).save("sprites/radiation.png")


if __name__ == "__main__":
    os.makedirs("sprites", exist_ok=True)
    build_map()
    sheet([yoru(i) for i in range(8)], "yoru")
    sheet([missile(i) for i in range(4)], "missile")
    sheet([nuke(i) for i in range(8)], "nuke")
    sheet([boom(i) for i in range(8)], "boom", ol=False)
    flags(); finger(); radiation()
