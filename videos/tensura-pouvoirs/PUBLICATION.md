# TikTok Tensura — le système de pouvoir de « Moi, quand je me réincarne en Slime »

Motion design + pixel art, 102,5 s. Voix ElevenLabs « Mattyang ».

**Fichiers**
- `renders/TENSURA_SYSTEME_DE_POUVOIR.mp4` : musique originale (fantasy / « explication ») + voix + bruitages. Rien de protégé côté audio.
- `renders/TENSURA_voix_bruitages.mp4` : voix + bruitages sans musique (pour ajouter un son TikTok toi-même).
- La version avec ton OST Naruto « Explanation » arrive dès que tu renvoies le fichier : l'upload est arrivé vide (« Not Found »). Dépose-le en `src/ost.mp3` (ou .mp4), relance `python3 tools/mix.py .`, et `audio/mix_ost.wav` sort tout seul.

**Contenu (dans l'ordre)**
1. Magicules (le « mana ») : énergie magique du monde, les monstres naissent là où elle est concentrée, plus on en a, plus on est fort.
2. Aura (énergie de combat autour du corps / de l'arme), puis Haki (magicules libérées pour écraser).
3. Nomination : transfert de magicules, et Rigurd et les gobelins évoluent en hobgobelins.
4. Les 5 types de compétences : intrinsèque (race), commune, extra (Perception magique), unique (désir / volonté extrême, mort / renaissance : Grand Sage et Prédateur), ultime (éveil en Seigneur Démon : Raphaël et Belzébuth ; seule une ultime résiste à une ultime).

**Sources visuelles**
- Extrait de l'anime (S2, évolution de Grand Sage en Raphaël et de Gluttony en Belzébuth), tiré de ta vidéo. Bandeau de sous-titres anglais et logo rognés.
- Pixel art maison : Rimuru, oni + aura, Seigneur Démon + Haki, gobelin / hobgobelin, fenêtres « [ AVIS ] » façon Grand Sage, échelle des 5 compétences.

## Légende
Le système de pouvoir de Tensura expliqué simplement 🫧 Magicules, aura, haki, nomination et les 5 types de compétences. Tu prendrais laquelle ? 👇
#tensura #rimuru #moiquandjemereincarneenslime #slime #anime #animefr #isekai #pourtoi

## Refaire
```bash
python3 tools/sprites.py    # sprites pixel
./tools/clips.sh            # extraits verticaux depuis src/grand_sage.mp4
python3 tools/build.py .    # index.html + timing.json
python3 tools/mix.py .      # audio/mix.wav, vo-sfx.wav (+ mix_ost.wav si src/ost.* existe)
npx hyperframes render . -o renders/raw.mp4
```
