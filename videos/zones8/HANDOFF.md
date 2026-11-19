# Passation — vidéo TikTok n°2 « Les 8 zones du gouffre » (Grab a Bird)

- Script : `scripts/grab-a-bird-devlog.md`, vidéo 2. Voix off ElevenLabs « Hugo » (19/11) : `assets/audio/voix.mp3`, 32,1 s.
- Projet HyperFrames 1080×1920, 30 i/s, 34 s : `index.html` (vidéo `assets/video/chute.mp4` + titres + voix),
  `compositions/titres.html` (accroche, 8 titres de zone, sous-titres, jauge de profondeur à gauche, question finale).
- Minutage (pauses mesurées avec ffmpeg silencedetect) : accroche 0–3,0 ; « Zone k » à 3,80 / 7,07 / 9,88 / 12,59 /
  16,68 / 19,39 / 23,07 / 27,53 s ; question 30,86 s. Les mêmes temps sont dans `rendu_zones.py` (TZ, T_FIN) :
  la caméra franchit chaque frontière de zone quand la voix la nomme. Changer la voix ⇒ changer les deux.
- Images : rendu Blender de la vraie carte, une chute continue avec 16 monstres animés (Fly) :
  `JEUX 2\blender\video_jour7\rendu_zones.py -- apercu|tout` → `JEUX 2\apercus_video\zones8\f_####.png` (12 min),
  monstres tirés de `apercus_video\biblio\*.blend` (`construire_biblio.py`). Le dragon de récif n'y est pas
  (son script attend reef_dragon.blend ouvert).
- Encodage : `ffmpeg -framerate 30 -start_number 0 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 22 -g 30 chute.mp4`.
  Le rendu final HyperFrames sort à ~100 Mo : le recompresser (`-crf 23`) avant le commit (limite GitHub 100 Mo).
- Rendu : `renders/zones8.mp4`.

## Reste à faire
- Musique / son tendance (à ajouter sur TikTok, ou en `<audio>` ici à ~0,14 de volume sous la voix).
