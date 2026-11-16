"""Reference-vs-render sheet: renders/compare.png   usage: compare.py <reference.png>"""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "renders")
ref = Image.open(sys.argv[1]).convert("RGB")
crops = [ref.crop((0, 0, 550, 615)), ref.crop((550, 0, 1254, 615)), ref.crop((0, 615, 700, 1254)), ref.crop((700, 615, 1254, 1254))]
outs = [Image.open(os.path.join(R, n)).convert("RGB") for n in ("face.png", "profil.png", "trois_quarts.png", "dos.png")]
Hh = 520
fit = lambda im: im.resize((int(im.width * Hh / im.height), Hh))
cells = [(fit(a), fit(b)) for a, b in zip(crops, outs)]
rows = [cells[:2], cells[2:]]
W = max(sum(a.width + b.width for a, b in r) for r in rows) + 30
sheet = Image.new("RGB", (W, 2 * Hh + 10), "white")
for ri, r in enumerate(rows):
    x = 0
    for a, b in r:
        sheet.paste(a, (x, ri * (Hh + 10))); x += a.width
        sheet.paste(b, (x, ri * (Hh + 10))); x += b.width + 15
sheet.save(os.path.join(R, "compare.png")); print("ok")
