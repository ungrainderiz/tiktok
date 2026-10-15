# Jujutsu Kaisen — « Le jour où Kusakabe a choqué tout le monde » (remontage)

Remontage d'un TikTok existant de Matt (`assets/source/original.mp4`, 576×1024, 72 s), en beaucoup plus dynamique.
La bande-son d'origine (voix + musique) est gardée telle quelle ; tout le visuel est refait.

## Pipeline

- `tools/assets.py` : extrait de la vidéo d'origine les images et extraits animés réutilisables, recadrés au-dessus de
  la bande des anciens sous-titres incrustés, agrandis ×2 ; coupe la bande-son à 67,81 s (fin sur un temps de la musique,
  le temps suivant tombe juste après le raccord de boucle). L'outro muette d'origine (67,5 → 72 s) est supprimée.
- `tools/plan.py` : texte + minutage mot à mot (relevé sur le surlignage jaune des sous-titres d'origine), liste des
  38 plans (entrées whip / slam / zoom, poussée continue, fond flou) et des 52 mots-clés qui claquent → génère
  `tools/scenes/01-montage.src` et `transcript.json`.
- `tools/sfx.py` : bruitages posés automatiquement sur les entrées de plans et les mots-clés (volume 0,25).
- `tools/build.py` : compositions + index.html. `tools/make.sh` enchaîne tout.

## Boucle

Fin et début sur la même illustration (Kusakabe vs Sukuna), même cadrage, même poussée de caméra ;
« …ce qu'il faut pour changer une bataille. » → « Le jour où Kusakabe a choqué tout le monde… ».

## Texte (d'après les sous-titres d'origine)

Le jour où Kusakabe a choqué tout le monde avec la maîtrise de son […]. Dans l'univers de Jujutsu Kaisen, tout le
monde connaissait Kusakabe comme un simple exorciste de rang 1. Quelqu'un de fiable, respecté, mais loin d'être une
légende vivante. Pourtant, ce jour-là, il s'est dressé face à Sukuna, le roi des fléaux, sans trembler. Alors que tous
les exorcistes tombaient un à un sous la puissance écrasante de Sukuna, Kusakabe est entré en scène. Pas avec une
extension de territoire, pas avec une technique occulte dévastatrice. Non, juste avec sa maîtrise parfaite du domaine
simple, son sang-froid et sa détermination inébranlable. Il a tenu tête à Sukuna bien plus longtemps que personne
n'aurait jamais osé l'imaginer. Il a esquivé, contré, frappé, pas pour le vaincre, mais pour protéger, pour ralentir
l'inévitable. Et pendant ce combat, même Sukuna a reconnu, ne serait-ce qu'un instant, que ce professeur ordinaire
était un vrai sorcier. Ce qui est intéressant avec cet affrontement, c'est que tout le monde a compris ce jour-là que
Kusakabe n'était pas un prodige béni par l'énergie maudite, ni un monstre comme Satoru Gojo. C'était juste un homme
prêt à faire face à l'enfer avec ce qu'il avait. Et parfois, c'est exactement ce qu'il faut pour changer une bataille.

Le dernier mot de la 1re phrase (non sous-titré dans l'original) n'est pas sûr : sous-titré « avec la maîtrise… ».
