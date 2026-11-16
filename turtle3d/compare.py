"""Build a reference-vs-render comparison sheet: renders/compare.png"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "renders")
ref_side, ref_fb = sys.argv[1], sys.argv[2]
H = 520


def fit(im):
    return im.convert("RGB").resize((int(im.width * H / im.height), H))


fb = Image.open(ref_fb)
w2 = fb.width // 2
refs = [Image.open(ref_side), fb.crop((0, 0, w2, fb.height)), fb.crop((w2, 0, fb.width, fb.height))]
outs = [Image.open(os.path.join(R, n)) for n in ("three_quarter.png", "front.png", "back.png")]
refs, outs = [fit(i) for i in refs], [fit(i) for i in outs]
W = max(sum(i.width for i in refs), sum(i.width for i in outs))
sheet = Image.new("RGB", (W, 2 * H), "white")
x = 0
for i in refs:
    sheet.paste(i, (x, 0)); x += i.width
x = 0
for i in outs:
    sheet.paste(i, (x, H)); x += i.width
sheet.save(os.path.join(R, "compare.png"))
print("ok")
