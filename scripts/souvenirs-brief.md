# Brief — vidéo « Souvenirs » (Dive-Catch)

**Histoire :** « J'ai retrouvé une vieille photo du gouffre… et j'ai plongé dedans. »
**Héros :** mon perso Roblox (skin exporté dans `JEUX 2\avatar\` : .obj + .mtl + .png).
**Format :** TikTok vertical 1080×1920, 30 i/s, 16–18 s, calé sur `JEUX 2\avatar\musique.mp3`.
**Niveau visé :** au moins aussi propre que la vidéo d'exemple (animation Minecraft cinématique, lumière douce, textes 3D en blocs qui éclatent, effet cassette). Mieux si possible.

---

## 1. Préparer le perso (avant tout plan)
- Importer le .obj, garder les textures en pixels nets : interpolation **Closest** sur chaque image, pas de flou.
- Accrocher chaque pièce (tête, torse, bras, jambes, accessoires) au **squelette R15** des anims joueur (`JoueurAnims`), avec un poids rigide par os (pas de déformation molle).
- Vérifier les cheveux et accessoires (orientation, pivots). Ajouter un os par mèche ou accessoire qui bouge, pour l'animation secondaire.
- Faire un rendu de contrôle face / profil / dos avant de continuer.

## 2. Qualité d'animation (le plus important)
Animation **faite à la main, pose par pose**, pas des boucles génériques :
- **Anticipation** avant chaque action (il se baisse avant de sauter, recule avant de plonger).
- **Arcs** : bras, tête et trajectoire du corps suivent des courbes, jamais des lignes droites.
- **Retard et chevauchement** : cheveux, accessoires et bras arrivent 2 à 4 images après le corps.
- **Amorti et rebond** à l'arrivée au sol (compression puis retour).
- **Rythme** : poses tenues 6 à 10 images sur les moments forts, mouvements rapides entre deux.
- Courbes nettoyées dans le Graph Editor, aucune saccade, aucun pied qui glisse.
- Plonger dans le vide : corps étiré en plongeon, puis rotation lente, bras écartés, vêtements et cheveux qui flottent.

## 3. Rendu
- **Cycles**, 128 à 256 échantillons + débruitage (OpenImageDenoise). EEVEE seulement si les aperçus sont validés et que le temps manque.
- Gestion des couleurs **AgX** (ou Filmic), contraste moyen, exposition réglée plan par plan.
- **Lumière** : soleil chaud bas sur l'horizon + ciel HDRI ou Nishita, une lumière de contour froide derrière le perso, volume léger (brume) dans le gouffre.
- **Caméra** : 35–50 mm, **profondeur de champ** sur le perso (f/2.8 à f/4), **flou de mouvement** activé (shutter 0,5).
- Compositing : glare léger sur les points lumineux, vignette 5–8 %, pas de bloom fort.
- Exporter des **PNG** par plan (`plans/pNN/f_####.png`), puis un .mp4 par plan pour HyperFrames.

## 4. Les plans (à recaler sur les temps forts de la musique)
| # | ~Durée | Plan | Texte 3D en blocs |
|---|---|---|---|
| 1 | 2 s | La volière, lumière dorée de fin d'après-midi. Mon perso trouve un **vieux cadre photo du gouffre** posé sur un établi, le prend, le regarde | « souvenirs » |
| 2 | 1,5 s | Gros plan sur la photo : la caméra **plonge dedans**, l'image devient le vrai gouffre | — |
| 3 | 2 s | Il **saute** du bord du plateau (anticipation, impulsion, plongeon) | « plonge » |
| 4 | 1,5 s | Chute dans la zone 2, brume et Mist Heron qui passe tout près | « brume » |
| 5 | 1,5 s | Zone 3, cristaux qui scintillent, rotation lente | « cristal » |
| 6 | 1,5 s | Zone 4, braise et étincelles, chute rapide | « braise » |
| 7 | 1,5 s | Zone 6, lanternes de jade | « jade » |
| 8 | 2,5 s | Il croise le **Dragon doré céleste** qui l'entoure. Moment le plus beau du film | « secret » |
| 9 | 2 s | Retour dans la volière : il tient la photo, et le dragon est maintenant dessus | — |
| 10 | 1,5 s | Fondu au blanc | « à suivre… » |

**Textes 3D :** lettres en voxels (police en blocs), lumière du décor dessus. Ils apparaissent bloc par bloc, tiennent 0,8 s puis **éclatent en petits cubes** qui tombent avec la physique. Simulation précalculée pour qu'elle soit identique à chaque rendu.

## 5. Montage HyperFrames (`videos/souvenirs/`)
- Coupes sur les temps de la musique (`npx hyperframes beats`).
- Effet **cassette** avant le plan 8 : « REWIND ◀◀ 0:00:07 », lignes de balayage, léger décalage des couleurs, image qui saute 3–4 fois.
- Accroche lisible dès la première image (le cadre photo + « souvenirs »).
- Pas de texte sous 1330 px ni à droite (zones cachées par TikTok).
- `npx hyperframes check`, `npx hyperframes snapshot --review`, rendu, puis commit et push sur `claude/gifted-ritchie-17mqif`.

## 6. Étapes de validation (me montrer avant de continuer)
1. Le perso importé et accroché au squelette (rendu face / profil / dos).
2. L'animation de chaque plan en **aperçu rapide** (EEVEE ou Cycles à 16 échantillons, basse résolution).
3. Une image finale par plan en qualité max.
4. Seulement ensuite : le rendu complet et le montage.
