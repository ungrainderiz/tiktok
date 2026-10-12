# TikTok JoJo — Limp Bizkit (Sports Maxx, Stone Ocean)

Style : manga encré / motion design vectoriel (plus de pixel art). Durée : 61,5 s.

**Fichiers**
- `renders/JOJO_LIMP_BIZKIT.mp4` : version complète (voix ElevenLabs « Kev » + musique nu metal originale + bruitages)
- `renders/JOJO_LIMP_BIZKIT_voix_bruitages.mp4` : voix + bruitages, **sans musique** → tu ajoutes un OST de JoJo dans TikTok et tu gardes les bruitages
- `renders/JOJO_LIMP_BIZKIT_voix_seule.mp4` : voix seule → pour ajouter tes propres sons dans TikTok

## Bruitages
Les bruitages (grondement « ゴゴゴ », invocation de Stand, impacts, râles de zombies, pas, os qui craque, porte de prison, battements de cœur, glitch, jingle de fin façon « To Be Continued ») ont été **générés avec ElevenLabs (text-to-sound)** dans le style JoJo.
Ce ne sont pas les sons originaux de l'anime : ceux-là sont protégés (risque de son coupé), et je ne peux pas les télécharger depuis mon environnement (freesound.org et les sites de sons sont bloqués par le réseau).
Fichiers dans `audio/sfx/` (4 variations par son).

## Ajouter un OST de JoJo (sans risque de son coupé)
Publie la version `voix_bruitages` (ou `voix_seule`), puis « Ajouter un son » dans TikTok :
- « Awaken » (Pillar Men theme) : ambiance menaçante, parfait pour les zombies invisibles
- l'opening de Stone Ocean (« STONE OCEAN », ichigo from Kishida Kyoudan & The Akeboshi Rockets)
- « Break Stuff » de Limp Bizkit : clin d'œil au nom du Stand
- « Roundabout » (Yes) : à caler pour que le riff tombe sur la flèche TO BE CONTINUED (≈ 59 s)
Volume du son ajouté : ~10-15 % pour garder la voix claire.

## Légende
Le Stand le plus glauque de Stone Ocean 🧟 Limp Bizkit, le pouvoir de Sports Maxx ! Quel Stand je fais ensuite ? 👇
#jojo #jojosbizarreadventure #stoneocean #limpbizkit #sportsmaxx #ermes #ermescostello #anime #manga #animefr #pourtoi

## Refaire la vidéo
```bash
python3 tools/build.py .   # index.html + timing.json depuis audio/words.json
python3 tools/mix.py .     # audio/mix.wav, vo-sfx.wav, vo-only.wav
npx hyperframes render . -o renders/raw.mp4
```
Pour mettre tes propres images : remplace le contenu des blocs `.maxx`, `.ermes`, `.stand` (SVG dans `tools/_generic.js`) par une balise `<img>`.
