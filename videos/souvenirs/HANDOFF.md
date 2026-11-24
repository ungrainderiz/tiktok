# Passation — vidéo « Souvenirs » (Dive-Catch), version « VHS » 30 s

Brief : `scripts/souvenirs-brief.md`. Résultat : `souvenirs.mp4` (1080×1920, 30 i/s, 30,6 s).
Musique : « VHS » (Mattyeux), extrait 18,4 s → 49,0 s (`assets/audio/vhs.mp3`). Les mots 3D sont les paroles, un plan par ligne.

## Plans (rendus dans Blender, `JEUX 2\blender\souvenirs\`, images dans `apercus_souvenirs\plans_vhs\`)
| t (s) | clip | paroles (mot 3D) | contenu |
|---|---|---|---|
| 0 | p1 | « riait », « la peine » | volière, il prend le cadre, vue par-dessus l'épaule sur la photo |
| 2,5 | p2 | « souvenirs » | la caméra plonge dans la photo |
| 3,567 | p3 | « enlève » | saut du plateau |
| 4,8 → 16,5 | z2…z8 | amour, fille, s'écarte, adieu, tu pleures, je rêve, mirages | une zone par ligne, une créature par zone (héron, aigle de cristal, léviathan de braise, papillon comète, phénix de jade, cygne aurore, serpent de mer) |
| 16,5 | rewind | — | REWIND ◀◀ (zones à l'envers, VHS) |
| 17,1 | p8 | « mon cœur », « la peur » | Dragon d'or autour de lui, ciel couchant |
| 23,4 | p9 | « les yeux », « regard », « souviens-toi » | volière : il montre la photo du dragon, le Pinson se pose sur sa tête ; fondu au blanc + « à suivre… » |

Scripts : `gouffre.py -- <P3|Z2..Z8|P8> [apercu|tout|images f,..]` (zones = table `ZCFG`), `voliere.py -- <P1|P2|P9> [... | tout reprise]`,
`perso.py`, `texte_blocs.py` (police blocs, glyphes accentués), `commun.py` (`eviter_tete` : le Pinson ne rentre jamais dans la tête),
`rendre_tout.ps1 -plans Z2,Z3` (lancer via `-Command`, sinon seul le 1er plan passe). Ne pas rendre deux Blender en parallèle (plantage GPU).
