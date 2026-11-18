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
