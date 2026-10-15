#!/usr/bin/env python3
"""Extrait de la vidéo d'origine (assets/source/original.mp4, 576×1024) les plans réutilisables, recadrés
au-dessus de la bande des anciens sous-titres incrustés (y ≈ 740–870), agrandis ×2 (lanczos + netteté) :
  - images fixes → assets/images/plans/<nom>.jpg
  - extraits animés → assets/clips/<nom>.mp4 (muets) + une image d'appui (première image) pour le fond flou
et la bande-son d'origine (voix + musique) coupée à la durée de la boucle → assets/audio/source/original.wav.
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "source", "original.mp4")
TOTAL = 67.81  # fin sur un temps de la musique d'origine, calée pour que le temps suivant tombe juste après le raccord
VF = "scale=iw*2:ih*2:flags=lanczos,unsharp=5:5:0.8"

# nom : (temps, (x, y, w, h))
STILLS = {
    "fan-a": (1.0, (0, 290, 576, 734)),        # illustration Sukuna vs Kusakabe (sous le titre)
    "manga-voiture": (8.5, (0, 0, 576, 735)),
    "fan-comic": (13.5, (0, 30, 576, 705)),
    "illus-duo": (16.5, (0, 0, 576, 735)),
    "manga-noir": (19.5, (0, 0, 576, 735)),
    "manga-rayon": (21.0, (0, 0, 576, 735)),
    "manga-ecole": (28.5, (0, 0, 576, 735)),
    "manga-tchac": (31.5, (0, 0, 576, 735)),
    "manga-gang": (34.5, (0, 0, 576, 735)),
    "manga-gang2": (36.5, (0, 0, 576, 735)),
    "sukuna-orange": (40.0, (0, 0, 576, 735)),
    "manga-haha": (42.5, (0, 0, 576, 735)),
    "manga-close": (44.5, (0, 0, 576, 735)),
    "manga-action": (46.5, (0, 0, 576, 735)),
    "manga-atsuya": (60.5, (0, 0, 576, 735)),
    "manga-atsuya2": (62.0, (0, 0, 576, 735)),
    "fan-b": (64.0, (0, 0, 576, 735)),
    "portraits": (70.0, (10, 230, 556, 540)),
}
# nom : (début, fin, (x, y, w, h))
CLIPS = {
    "anime-ville": (3.75, 5.15, (0, 145, 576, 590)),
    "anime-glitch": (5.15, 7.05, (0, 145, 576, 590)),
    "anime-face": (10.0, 12.45, (0, 0, 576, 735)),
    "anime-rouge": (23.9, 24.65, (0, 145, 576, 590)),
    "anime-bouche": (24.95, 25.7, (0, 145, 576, 590)),
    "anime-feu": (25.75, 27.95, (0, 145, 576, 590)),
    "contre": (37.8, 38.85, (0, 0, 576, 735)),
    "meme": (48.3, 51.0, (0, 230, 576, 505)),
    "anime-sombre": (51.0, 52.45, (0, 145, 576, 590)),
    "anime-bleu": (52.45, 54.45, (0, 145, 576, 590)),
    "anime-main": (54.45, 55.75, (0, 145, 576, 590)),
    "anime-lumiere": (55.75, 57.0, (0, 145, 576, 590)),
    "anime-yeux": (57.0, 57.72, (0, 145, 576, 590)),
    "anime-oeil": (57.72, 58.9, (0, 145, 576, 590)),
    "anime-ombre": (58.9, 60.25, (0, 145, 576, 590)),
}


def run(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True)


def main():
    out_i = os.path.join(ROOT, "assets", "images", "plans")
    out_c = os.path.join(ROOT, "assets", "clips")
    os.makedirs(out_i, exist_ok=True)
    os.makedirs(out_c, exist_ok=True)
    for name, (t, (x, y, w, h)) in STILLS.items():
        run(["-ss", str(t), "-i", SRC, "-frames:v", "1", "-vf", f"crop={w}:{h}:{x}:{y},{VF}", "-q:v", "2",
             os.path.join(out_i, name + ".jpg")])
    for name, (a, b, (x, y, w, h)) in CLIPS.items():
        dst = os.path.join(out_c, name + ".mp4")
        run(["-ss", str(a), "-t", str(round(b - a, 3)), "-i", SRC, "-an", "-vf", f"crop={w}:{h}:{x}:{y},{VF}",
             "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "30", dst])
        run(["-i", dst, "-frames:v", "1", "-q:v", "3", os.path.join(out_i, name + "-poster.jpg")])
    run(["-i", SRC, "-t", str(TOTAL), "-vn", "-ac", "2", "-ar", "48000",
         os.path.join(ROOT, "assets", "audio", "source", "original.wav")])
    print(len(STILLS), "images,", len(CLIPS), "extraits")


if __name__ == "__main__":
    main()
