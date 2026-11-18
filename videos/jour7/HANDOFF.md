# Passation — vidéo TikTok « Jour 7 » (Grab a Bird)

## Où est le travail
- Dépôt GitHub `ungrainderiz/tiktok`, branche `claude/gifted-ritchie-17mqif`
- `scripts/grab-a-bird-devlog.md` : les 8 textes de vidéos (celle-ci = vidéo n°1)
- `videos/jour7/` : projet HyperFrames (HTML rendu en vidéo), 1080×1920, 30 i/s, 23,5 s

## Fichiers du projet
- `index.html` : racine ; monte 3 scènes + la voix off
- `compositions/world.html` : scène 3D Three.js (`assets/lib/three.module.min.js`), pilotée par `hf-seek` :
  - 0–4,5 s monde en blocs « Jour 1 » (4 plateaux gris + oiseau en cubes), explosion 4,5–4,95 s
  - 4,95–9,5 s plongée dans le gouffre en voxels, 8 zones (couleurs dans `ZONES`)
  - 9,5–12,25 s boss : portail rose, serpent (Gardien de la Brèche), ciel rose, laser
  - 12,25–17,15 s boucle de jeu : saut, lasso + explosion dorée à 15,5 s, créature remontée
  - 17,15–19,35 s plongée « plus profond = plus rare », 19,35–23,5 s vue aérienne (abonne-toi)
  - Caméra : tableau `K` [temps, position, cible] ; un temps répété = coupe franche
- `compositions/titres.html` : gros titres animés (GSAP)
- `compositions/soustitres.html` : sous-titres de la voix off (tableau `G`)
- `assets/audio/voix.mp3` : voix off ElevenLabs (22,1 s)

## Calage de la voix (pauses mesurées, pas de transcription possible ici)
0,1–2,7 « Il y a 7 jours, mon jeu Roblox ressemblait à ça » · 2,9–4,5 « 4 zones faites avec des blocs » ·
4,9–5,4 « Aujourd'hui ? » · 5,7–9,4 « 8 zones, une soixantaine de créatures animées, une nouvelle interface » ·
9,65–12,1 « et un premier événement avec un boss géant » · 12,4–13,3 « Le principe est simple » ·
13,6–16,9 « tu sautes… tu attrapes… au lasso, et tu la ramènes » · 17,2–19,1 « Plus tu descends, plus elles sont rares » ·
19,4–21,9 « Abonne-toi, je te montre chaque zone une par une »
→ À vérifier à l'oreille / avec `npx hyperframes transcribe assets/audio/voix.mp3 --model small --language fr`.

## Fait le 18/11 (vrais modèles Blender)
- `assets/models/` : `cloudowl.glb` (CloudOwl zone 2, Fly/Idle/Roar), `gardien.glb` (Gardien de la Brèche v3, Fly/Idle/Roar/Laser),
  `pinson.glb` (vieux Pinson à studs de la zone 1, statique). Produits par `JEUX 2\blender\export_glb_video.py`
  (`D:\Blender\blender.exe -b --factory-startup --python blender\export_glb_video.py -- cloudowl|gardien|pinson <sortie.glb>`).
- Les vraies couleurs sont dans COLOR_1 (calque « Col ») : `useColor1()` les recopie dans `color` au chargement.
- `world.html` : `GLTFLoader` local (`assets/lib/GLTFLoader.js`, r170, import réécrit), chargement dans `window.__hf.buildReady["world-models"]`,
  `seekClip()` = un seul clip actif + `mixer.setTime(temps local)`. Gardien coupé par un plan de clipping au portail
  (seul ce qui a traversé est dessiné), Laser vers le ciel à `LASER_FIRE` (~11,5 s), ciel rose ensuite.
- Sous-titres recalés sur les pauses mesurées (ffmpeg silencedetect) ; ils étaient invisibles (style scopé non appliqué aux
  éléments créés en JS) → style inline. « et tu la ramènes » = 16,26 s (titre « ramène » et remontée du hibou décalés).
- Rendu : `renders/jour7.mp4`.

## Fait le 19/11 : rendu Blender (remplace la scène three.js)
- Le décor 3D vient maintenant d'un rendu Blender de la VRAIE carte et des vrais monstres : `assets/video/monde.mp4`
  (705 images, sans son), posé en `<video id="monde">` dans `index.html` sous les titres et sous-titres.
  `compositions/world.html`, three.js et les .glb sont retirés (ils restent dans le commit c1a8358).
- Scripts dans `JEUX 2\blender\video_jour7\` : `carte.py` (import des FBX zones 1-8, plateaux, cascades, décor + arbres v3
  replacés depuis les .lua de `roblox/`, brume par zone + halo Neon dans le compositeur), `rendu_plan.py -- <A|B|D|E|F> [apercu|tout]`,
  `rendu_breche.py` (plan C = cinématique de la Brèche retimée), `rendre_tout.ps1` (~9 min pour tout).
  Images dans `JEUX 2\apercus_video\frames\f_####.png` (n = temps × 30), puis
  `ffmpeg -framerate 30 -start_number 0 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -g 30 monde.mp4`.
- Plans : A 0–4,95 Jour 1 (carte v1 + Pinson à studs, explosion) · B 4,95–9,5 plongée 8 zones (+ monstres Fly) ·
  C 9,5–12,25 Brèche · D 12,25–17,15 bord, saut, CloudOwl + lasso · E 17,15–19,35 plus profond · F 19,35–23,5 vue aérienne.

## Reste à faire
1. **Remplacer les créatures faites en code par les vrais modèles Blender** de `JEUX 2\exports_blender\`
   (exporter en .glb avec animations, copier dans `videos/jour7/assets/models/`, charger avec `GLTFLoader`
   de three@0.170.0, jouer les actions Idle/Fly/Roar avec un `AnimationMixer` réglé sur `mixer.setTime(t)`
   dans `renderAt(t)` — jamais d'horloge). Cibles :
   - `bird` (makeBird) → une créature de la zone 2 (capture au lasso)
   - le serpent `serpent[]` → Gardien de la Brèche (`gardien_breche.py`)
   - option : l'oiseau en cubes du « Jour 1 » → le vieux modèle à studs de la zone 1
   - enregistrer le chargement dans `window.__hf.buildReady` et ne déclarer la timeline qu'après
2. `npx hyperframes check` (pas encore lancé : il a été interrompu) et corriger les erreurs
3. `npx hyperframes snapshot --review` puis regarder les images (lisibilité sur téléphone, zone TikTok 168–1330 px)
4. Pas de musique pour l'instant (aucune source disponible) : en ajouter une sous la voix à ~0,14 de volume
5. `npx hyperframes render` → MP4
