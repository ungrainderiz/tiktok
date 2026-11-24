# Passation — vidéo « Souvenirs » (Dive-Catch)

Brief : `scripts/souvenirs-brief.md`. Résultat : `souvenirs.mp4` (1080×1920, 30 i/s, 17,1 s).

## Plans (rendus dans Blender, `JEUX 2\blender\souvenirs\`)
- `perso.py` : skin Roblox (`JEUX 2\avatar\Roblox skin.obj` + PNG) monté sur le squelette R15 de `joueur_anims.py`,
  pièces rigides + 4 os de mèches (animation secondaire). Tête « dynamic head » en overlay sur la peau.
- `texte_blocs.py` : textes 3D en voxels (police 5×9), apparition bloc par bloc, éclatement en 8 sous-cubes
  (balistique à graine fixe, clés à chaque image → identique à chaque rendu, flou de mouvement).
- `gouffre.py -- <P3..P8> [apercu|tout|images f,..|photo f|fenetre]` : vraie carte (`video_jour7/carte.py`),
  monstres de `apercus_video/biblio` (héron, aigle de cristal, léviathan de braise, lanternes, carpe de jade, Dragon d'or).
- `voliere.py -- <P1|P2|P9>` : volière en blocs, cadre photo (photos = rendus de P3 et P8), vue par la fenêtre.
- `commun.py` (EEVEE 64 éch., AgX, flou de mouvement, DOF, glare léger), `rendre_tout.ps1` (~40 min, tout + .mp4 par plan).

## Montage (`index.html`)
Coupes sur la musique (104 BPM, `assets/audio/musique.mp3` = son de la vidéo de référence) :
P1 0 · P2 2,335 · P3 3,485 · P4 5,205 · P5 6,375 · P6 7,525 · P7 8,685 · REWIND 9,825 · P8 10,405 · P9 13,295 · fin 17,11.
`assets/clips/rewind.mp4` = P3→P7 à l'envers ×10 + effets VHS (ffmpeg), `compositions/cassette.html` = OSD REWIND, lignes.
Fondu au blanc 15,75 s puis `assets/images/a-suivre.png` (même police blocs, `blender/souvenirs/texte_png.py`).
