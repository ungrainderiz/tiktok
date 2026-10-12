# Remake TikTok — BECK Mongolian Chop Squad

Remake motion design du TikTok d'origine (`src/original.mp4`) : même voix et même audio, images d'origine réutilisées (extraites, détourées, agrandies), montage refait en style « fanzine rock » (papier, scotch, stickers, marqueur, tampons) avec sous-titres mot à mot.

**Fichier** : `renders/BECK_REMAKE.mp4` (86 s, 1080×1920)

## Ce qui change par rapport à l'original
- 12 scènes rythmées sur la voix (une idée = une animation) au lieu d'images posées sur fond blanc
- sous-titres dynamiques (mot prononcé en jaune)
- bruitages ElevenLabs : guitare, foule, batterie, scratch, tampons, pops, whoosh (dans `library/`)
- titres des morceaux corrigés à l'écran : Moon on the Water, Slip Out, Face

## Légende
Le manga rock qu'il faut absolument découvrir 🎸 BECK Mongolian Chop Squad, dispo en VF ! Tu l'as vu ou lu ? 👇
#beck #mongolianchopsquad #anime #manga #animefr #mangafr #rock #pourtoi

## Refaire
```bash
python3 tools/build.py .   # index.html + timing.json
python3 tools/mix.py .     # audio/mix.wav (audio d'origine + bruitages)
npx hyperframes render . -o renders/raw.mp4
```
