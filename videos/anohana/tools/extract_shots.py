#!/usr/bin/env python3
"""Extrait une image propre par plan de la vidéo de référence (sous-titres incrustés effacés).

1. détection des plans (ffmpeg scene) ;
2. pour chaque plan, l'image avec le moins de texte incrusté (jaune + sous-titres blancs) ;
3. effacement du texte restant par inpainting OpenCV, puis agrandissement x2.
Sortie : assets/shots/shot-NN.png + assets/shots/shots.json (début/fin de chaque plan dans la référence).
"""
import json
import os
import re
import subprocess

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "source", "reference.mp4")
OUT = os.path.join(ROOT, "assets", "shots")


def scene_cuts():
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", SRC, "-vf", "select='gt(scene,0.12)',showinfo", "-vsync", "vfr", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", log)]
    merged = []
    for c in cuts:
        if not merged or c - merged[-1] > 0.25:
            merged.append(c)
    return merged


def text_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    yellow = cv2.inRange(hsv, (20, 120, 170), (38, 255, 255))
    h = img.shape[0]
    white = np.zeros(yellow.shape, np.uint8)
    band = img[int(h * 0.62):, :]
    wb = cv2.inRange(band, (225, 225, 225), (255, 255, 255))
    white[int(h * 0.62):, :] = wb
    m = cv2.bitwise_or(yellow, white)
    # inclut le contour noir des lettres
    return cv2.dilate(m, np.ones((9, 9), np.uint8), iterations=1)


def clean_plate(frames, k, mask, lo, hi):
    """Remplit le texte avec les vrais pixels d'autres images du plan où cette zone est dégagée.

    Les sous-titres s'écrivent lettre par lettre : sur un plan fixe, chaque zone couverte à un instant
    est visible à un autre. On ne prend que des images quasi identiques hors texte (plan fixe).
    """
    img = frames[k].copy()
    todo = mask > 0
    ref = frames[k].astype(np.int16)
    order = sorted(range(max(0, lo - 15), min(len(frames), hi + 15)), key=lambda j: abs(j - k))
    for j in order:
        if not todo.any():
            break
        if j == k:
            continue
        mj = text_mask(frames[j]) > 0
        free = ~(mj | todo)
        diff = np.abs(frames[j].astype(np.int16) - ref).mean(axis=2)
        if free.sum() == 0 or diff[free].mean() > 5:
            continue
        take = todo & ~mj
        img[take] = frames[j][take]
        todo &= ~take
    left = (todo.astype(np.uint8)) * 255
    if left.any():
        img = cv2.inpaint(img, left, 7, cv2.INPAINT_TELEA)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    cap = cv2.VideoCapture(SRC)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    dur = len(frames) / fps
    bounds = [0.0] + scene_cuts() + [dur]
    shots = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        if b - a < 0.2:
            continue
        lo, hi = int((a + 0.08) * fps), max(int((a + 0.08) * fps) + 1, int((b - 0.08) * fps))
        best, best_score, best_mask = None, None, None
        for k in range(lo, min(hi, len(frames))):
            m = text_mask(frames[k])
            # peu de texte, et une image nette (pas en plein fondu)
            sharp = cv2.Laplacian(cv2.cvtColor(frames[k], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            score = m.mean() - 0.002 * min(sharp, 400)
            if best_score is None or score < best_score:
                best, best_score, best_mask = k, score, m
        img = clean_plate(frames, best, best_mask, lo, min(hi, len(frames)))
        big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        blur = cv2.GaussianBlur(big, (0, 0), 1.2)
        big = cv2.addWeighted(big, 1.5, blur, -0.5, 0)
        name = f"shot-{len(shots):02d}.png"
        cv2.imwrite(os.path.join(OUT, name), big)
        shots.append({"file": name, "start": round(a, 3), "end": round(b, 3), "frame_t": round(best / fps, 3),
                      "text_left": round(float(best_mask.mean()) / 255, 4)})
    json.dump(shots, open(os.path.join(OUT, "shots.json"), "w"), indent=1)
    print(len(shots), "plans ;", n, "images")


if __name__ == "__main__":
    main()
