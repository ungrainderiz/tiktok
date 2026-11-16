"""Reference-vs-render sheet: renders/compare.png   usage: compare.py <reference.png>"""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "renders")
ref = Image.open(sys.argv[1]).convert("RGB"); w, h = ref.size
crops = [ref.crop((0, 0, w, h // 2)), ref.crop((0, h // 2, w // 2, h)), ref.crop((w // 2, h // 2, w, h))]
outs = [Image.open(os.path.join(R, n)).convert("RGB") for n in ("front.png", "side.png", "back.png")]
W = 1500; half = W // 2
def fitw(im, ww): return im.resize((ww, int(im.height * ww / im.width)))
cells = [(fitw(crops[0], half), fitw(outs[0], half)), (fitw(crops[1], half), fitw(outs[1], half)), (fitw(crops[2], half), fitw(outs[2], half))]
sheet = Image.new("RGB", (W, sum(max(a.height, b.height) for a, b in cells) + 20), "white")
y = 0
for a, b in cells:
    sheet.paste(a, (0, y)); sheet.paste(b, (half, y)); y += max(a.height, b.height) + 10
sheet.save(os.path.join(R, "compare.png")); print("ok")
