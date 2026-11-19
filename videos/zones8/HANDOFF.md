# Passation — vidéo TikTok n°2 « Les 8 zones du gouffre » (Grab a Bird)

- Script : `scripts/grab-a-bird-devlog.md`, vidéo 2. **Sans voix off** (choix du 19/11) : le texte est à l'écran.
- Projet HyperFrames 1080×1920, 30 i/s, 38 s : `index.html` (vidéo `assets/video/chute.mp4` + titres),
  `compositions/titres.html` (accroche, 8 titres de zone, jauge de profondeur à gauche, question finale).
- Minutage : accroche 0–2,6 s ; zone k de 2,6 + 4(k−1) à +4 s ; question 34,6–38 s.
- Images : rendu Blender de la vraie carte, une chute continue avec 16 monstres animés (Fly) :
  `JEUX 2\blender\video_jour7\rendu_zones.py -- apercu|tout` → `JEUX 2\apercus_video\zones8\f_####.png` (12 min),
  monstres tirés de `apercus_video\biblio\*.blend` (`construire_biblio.py`). Le dragon de récif n'y est pas
  (son script attend reef_dragon.blend ouvert).
- Encodage : `ffmpeg -framerate 30 -start_number 0 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 22 -g 30 chute.mp4`.
  Le rendu final HyperFrames sort à ~100 Mo : le recompresser (`-crf 23`) avant le commit (limite GitHub 100 Mo).
- Rendu : `renders/zones8.mp4`.

## Reste à faire
- Musique / son tendance (à ajouter sur TikTok ou en `<audio>` ici).
- Voix off ElevenLabs si tu en veux une : recaler les titres sur la voix.
