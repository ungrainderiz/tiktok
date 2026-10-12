"""Pixel-art iceberg background, 135 x 480 low-res (x8 => 1080 x 3840)."""
import random
from PIL import Image, ImageDraw
W, H, SEA = 135, 480, 150
rnd = random.Random(5)
im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
# sky
for y in range(SEA):
    t = y / SEA
    c = lerp((10, 12, 38), (58, 44, 96), t ** 1.4)
    d.line([0, y, W, y], fill=c)
for _ in range(70):
    x, y = rnd.randrange(W), rnd.randrange(SEA - 30)
    im.putpixel((x, y), (255, 255, 230) if rnd.random() < .3 else (170, 170, 210))
d.ellipse([100, 18, 116, 34], fill=(246, 240, 214)); d.ellipse([105, 16, 121, 32], fill=lerp((10, 12, 38), (58, 44, 96), 0.05))
# sea gradient with dithering bands
for y in range(SEA, H):
    t = (y - SEA) / (H - SEA)
    c1 = lerp((40, 110, 150), (2, 4, 12), min(1, t ** 0.8))
    c2 = lerp((40, 110, 150), (2, 4, 12), min(1, (t + 0.02) ** 0.8))
    for x in range(W):
        im.putpixel((x, y), c1 if (x + y) % 2 else c2)
# iceberg above water (tip)
tip = [(67, 92), (74, 104), (80, 112), (88, 126), (96, 138), (104, SEA), (30, SEA), (40, 136), (50, 120), (58, 106)]
d.polygon(tip, fill=(220, 238, 248))
d.polygon([(67, 92), (74, 104), (80, 112), (88, 126), (96, 138), (104, SEA), (72, SEA), (70, 120)], fill=(170, 206, 228))
for (x, y) in ((56, 120), (60, 112), (46, 136), (84, 132)):
    d.line([x, y, x + 4, y + 2], fill=(255, 255, 255))
# underwater iceberg, widening with depth, darker layers
under = [(30, SEA), (104, SEA), (116, 200), (124, 280), (130, 380), (134, H), (1, H), (6, 380), (12, 280), (20, 200)]
d.polygon(under, fill=(110, 170, 200))
for y in range(SEA, H):
    t = (y - SEA) / (H - SEA)
    for x in range(W):
        p = im.getpixel((x, y))
        if p == (110, 170, 200):
            c = lerp((120, 182, 212), (14, 22, 40), t ** 0.9)
            if (x // 2 + y // 2) % 7 == 0: c = lerp(c, (0, 0, 0), .25)
            im.putpixel((x, y), c)
# water surface highlight
for x in range(0, W, 3):
    d.point((x, SEA), fill=(200, 240, 255)); d.point((x + 1, SEA + 1), fill=(150, 210, 240))
# layer separators
for ly in (230, 320, 410):
    for x in range(0, W, 4): d.line([x, ly, x + 1, ly], fill=(200, 220, 240))
im.save("sprites/iceberg.png"); print("bg ok")
