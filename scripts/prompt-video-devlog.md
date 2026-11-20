# Prompt — vidéo TikTok devlog « Grab a Bird » (rendu Blender + HyperFrames)

Copier ce prompt, remplacer les [crochets], et le donner à Claude dans le dossier `JEUX 2`.

---

Fais la vidéo TikTok n°[NUMÉRO] de `tiktok/scripts/grab-a-bird-devlog.md` (« [TITRE] »), dans le dépôt
`ungrainderiz/tiktok`, branche `claude/gifted-ritchie-17mqif`, dossier `videos/[DOSSIER]`.

**Format** : vertical 1080×1920, 30 i/s, [DURÉE] s. Projet HyperFrames sur le modèle de `videos/zones8`
(index.html + compositions/titres.html, version `hyperframes@0.9.68`).

**Voix off** : [« aucune » → tout le texte du script est à l'écran | « D:\<fichier ElevenLabs>.mp3 » → la caler
avec ffmpeg silencedetect, sous-titres phrase par phrase posés sur les pauses].

**Images** : PAS de scène three.js. Tout le décor est un rendu Blender (EEVEE) de la VRAIE carte du jeu et des
VRAIS monstres, avec les scripts de `blender/video_jour7/` :
- `carte.py` : zones 1 à 8 (exports FBX v2), plateaux, cascades, décor + arbres v3 replacés depuis les .lua de
  `roblox/`, brume par zone et halo des Neon ;
- monstres animés (Fly/Idle/Roar) depuis `apercus_video/biblio/<nom>.blend`
  (sinon `construire_biblio.py -- <nom>` qui lance `blender/<nom>_rig.py`) ;
- boss : cinématique de la Brèche (`rendu_breche.py`) ;
- un script de rendu par vidéo comme `rendu_zones.py` (chemin de caméra par temps, monstres placés par
  rapport à la caméra), mode `apercu` (10 images en 270×480) avant `tout`.

**Plans** : [reprendre la liste « Plans » du script, avec pour chacun : début–fin en secondes, lieu
(zone / plateau / vitrine), monstres visibles, mouvement de caméra].

**Texte à l'écran** : [reprendre « Texte à l'écran »]. Style de la série : Archivo Black en majuscules, contour
#1a1633, une couleur par zone (Z1 #8ee05f, Z2 #d2b6ff, Z3 #6ef0fb, Z4 #ff8a3a, Z5 #ff8ee0, Z6 #5ff0b0,
Z7 #b8eeff, Z8 #ff9fb0), accent jaune #ffd23f ; l'accroche est lisible dès l'image 0 ; la fin est une question.
Textes entre 300 et 1330 px de haut (zone TikTok), rien sous les boutons à droite.

**Étapes et vérifications** :
1. Aperçu Blender des plans → me montrer une planche avant le rendu complet.
2. Rendu complet → `apercus_video/<dossier>/f_####.png` (n = temps × 30) →
   `ffmpeg -framerate 30 -start_number 0 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -g 30 <video>.mp4`.
3. `npx hyperframes@0.9.68 check` sans erreur, `snapshot` à chaque changement de plan, regarder les images.
4. `npx hyperframes@0.9.68 render -o renders/<nom>.mp4`.
5. Commit + push (Git portable : `JEUX 2\outils\MinGit\cmd\git.exe` ; FFmpeg dans
   `%LOCALAPPDATA%\ffmpeg\ffmpeg-master-latest-win64-gpl\bin`).

Réponds en français.
