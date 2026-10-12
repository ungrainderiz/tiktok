#!/usr/bin/env python3
"""Ajoute les lettres accentuées françaises à la police Minecraft (pixel art, sans accents).

Entrée : assets/fonts/minecraft.ttf (fournie par l'utilisateur, CC BY-SA, Pwnage_Block)
Sortie : assets/fonts/sous-titres.ttf — même police + É È Ê Ë À Â Ç Ô Ù Û Ü Î Ï et minuscules.
Les accents sont dessinés sur la grille de la police : 1 pixel = 128 unités.
"""
import os

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "fonts", "minecraft.ttf")
DST = os.path.join(ROOT, "assets", "fonts", "sous-titres.ttf")
U = 128  # taille d'un pixel

# accents en pixels (colonne, rangée) ; colonne 2 = centre d'une lettre de 5 px
CAP = {  # au-dessus des majuscules (7 px de haut) : rangées 8-9
    "acute": [(2, 8), (3, 9)], "grave": [(2, 8), (1, 9)],
    "circ": [(1, 8), (2, 9), (3, 8)], "diaer": [(1, 8), (3, 8)],
}
LOW = {  # au-dessus des minuscules (5 px de haut) : rangées 6-7
    "acute": [(2, 6), (3, 7)], "grave": [(2, 6), (1, 7)],
    "circ": [(1, 6), (2, 7), (3, 6)], "diaer": [(1, 6), (3, 6)],
}
CEDILLA = [(2, -1), (1, -2)]

LETTERS = {
    "É": ("E", CAP["acute"]), "È": ("E", CAP["grave"]), "Ê": ("E", CAP["circ"]), "Ë": ("E", CAP["diaer"]),
    "À": ("A", CAP["grave"]), "Â": ("A", CAP["circ"]), "Ô": ("O", CAP["circ"]),
    "Ù": ("U", CAP["grave"]), "Û": ("U", CAP["circ"]), "Ü": ("U", CAP["diaer"]),
    "Ç": ("C", CEDILLA),
    "é": ("e", LOW["acute"]), "è": ("e", LOW["grave"]), "ê": ("e", LOW["circ"]), "ë": ("e", LOW["diaer"]),
    "à": ("a", LOW["grave"]), "â": ("a", LOW["circ"]), "ô": ("o", LOW["circ"]),
    "ù": ("u", LOW["grave"]), "û": ("u", LOW["circ"]), "ü": ("u", LOW["diaer"]),
    "ç": ("c", CEDILLA),
}
# I fait 3 px de large : accents recentrés sur la colonne 1
I_CAP = {"Î": [(0, 8), (1, 9), (2, 8)], "Ï": [(0, 8), (2, 8)]}


def rect(pen, cx, cy):
    x0, y0, x1, y1 = cx * U, cy * U, (cx + 1) * U, (cy + 1) * U
    pen.moveTo((x0, y0))
    pen.lineTo((x0, y1))
    pen.lineTo((x1, y1))
    pen.lineTo((x1, y0))
    pen.closePath()


def main():
    font = TTFont(SRC)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    order = list(font.getGlyphOrder())
    new = {}
    todo = dict(LETTERS)
    for ch, px in I_CAP.items():
        todo[ch] = ("I", px)
    added = []
    for ch, (base, pixels) in todo.items():
        if ord(ch) in cmap or ord(base) not in cmap:
            continue
        bname = cmap[ord(base)]
        name = f"uni{ord(ch):04X}"
        pen = TTGlyphPen(gs)
        gs[bname].draw(pen)
        for cx, cy in pixels:
            rect(pen, cx, cy)
        new[name] = pen.glyph()
        font["hmtx"][name] = font["hmtx"][bname]
        for table in font["cmap"].tables:
            if table.isUnicode() or table.platformID == 3:
                table.cmap[ord(ch)] = name
        added.append(ch)
    order += list(new)
    font.setGlyphOrder(order)
    glyf = font["glyf"]
    glyf.glyphOrder = order
    for name, g in new.items():
        glyf.glyphs[name] = g
    font["maxp"].numGlyphs = len(order)
    # place pour les accents au-dessus des majuscules
    for t, k in (("hhea", "ascent"), ("OS/2", "usWinAscent"), ("OS/2", "sTypoAscender")):
        setattr(font[t], k, max(getattr(font[t], k), 10 * U))
    for t, k in (("hhea", "descent"),):
        setattr(font[t], k, min(getattr(font[t], k), -2 * U))
    font["OS/2"].usWinDescent = max(font["OS/2"].usWinDescent, 2 * U)
    font.save(DST)
    print("ajoutés :", "".join(added))


if __name__ == "__main__":
    main()
