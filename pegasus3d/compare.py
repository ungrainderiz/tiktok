"""Reference-vs-render sheet: renders/compare.png   usage: compare.py <reference.png>"""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "renders")
ref = Image.open(sys.argv[1]).convert("RGB")
crops = [ref.crop((0, 0, 1254, 620)), ref.crop((0, 610, 850, 1254)), ref.crop((690, 620, 1254, 1254))]
outs = [Image.open(os.path.join(R, n)).convert("RGB") for n in ("front.png", "side.png", "back.png")]
half = 750
def fitw(im, ww): return im.resize((ww, int(im.height * ww / im.width)))
cells = [(fitw(a, half), fitw(b, half)) for a, b in zip(crops, outs)]
sheet = Image.new("RGB", (2 * half, sum(max(a.height, b.height) for a, b in cells) + 20), "white")
y = 0
for a, b in cells:
    sheet.paste(a, (0, y)); sheet.paste(b, (half, y)); y += max(a.height, b.height) + 10
sheet.save(os.path.join(R, "compare.png")); print("ok")
