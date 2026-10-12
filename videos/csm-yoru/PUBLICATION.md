# TikTok Chainsaw Man — Comment Yoru a déclenché la 3e guerre mondiale

Motion design 2D + pixel art, 76,6 s. Voix ElevenLabs « Mattyang ».

**Fichiers**
- `renders/YORU_3E_GUERRE_MONDIALE.mp4` : version complète avec l'OST « Kingdom of Predators » (Hunter x Hunter 2011)
- `renders/YORU_voix_bruitages_sans_OST.mp4` : voix + bruitages sans musique (si TikTok coupe l'OST, publie celle-ci et ajoute le son depuis TikTok)

**Sources visuelles**
- Cases du manga tirées de ta vidéo (chap. 176 « transformer mes propres enfants en armes », « gant droit flingue / gant gauche tank », couverture du chap. 178, panneau « énergie atomique ») : recadrées pour enlever tes sous-titres incrustés. L'audio de ta vidéo n'est pas utilisé.
- Extraits de l'animation fan « War Devil vs Chainsaw Man » (YT : JOJ / IG : @josh_yey.cg) : Golfe du Mexique, Mont Elbrouz, Statue de la Liberté-arme, index perdus, BANG, explosions. → crédite-le dans la légende.
- Pixel art maison : carte polaire réelle (USA / URSS / Japon, trajectoire New York → Japon en grand cercle au-dessus de l'URSS), Yoru, missiles, champignon nucléaire, radar, DEFCON.

## Légende
Yoru a déclenché la 3e guerre mondiale… pour un power up 💀 Génie ou catastrophe ? 👇
Animations : @josh_yey.cg (War Devil vs Chainsaw Man) · OST : Kingdom of Predators (HxH 2011)
#chainsawman #yoru #asamitaka #chainsawmanpart2 #manga #anime #animefr #pourtoi

## Refaire
```bash
python3 tools/sprites.py    # carte + sprites pixel
./tools/clips.sh            # extraits verticaux depuis src/extra.mp4
python3 tools/build.py .    # index.html + timing.json
python3 tools/mix.py .      # audio/mix.wav (+ vo-sfx.wav)
npx hyperframes render . -o renders/raw.mp4
```
