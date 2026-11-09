# Arène LoL : simulation de bataille pour TikTok/Reels

Deux armées de champions de League of Legends s'affrontent toutes seules dans une arène,
jusqu'au dernier survivant. Le format reprend la vidéo de référence (Gen 1 vs Gen 3).
La vidéo est verticale (1080×1920) et dure environ 60 à 75 s :

1. **Intro** : titre multicolore (« Anciens vs Nouveaux ! — Qui gagne ? »), les champions
   apparaissent dans des orbes, puis « COMBAT ! »
2. **Bataille** : les noms des sorts s'affichent, les ultimes ont un grand titre doré avec le
   portrait, et les barres de vie des champions les plus dangereux sont en haut.
3. **Ralenti** sur le dernier coup.
4. **Écran de victoire** : survivants, MVP et appel à commenter.

## Affiches prêtes à l'emploi (`battles/`)

| Fichier | Affiche | Style |
| --- | --- | --- |
| `anciens-vs-nouveaux.config.js` | 67 champions 2009-2010 vs 60 champions 2013-2025 | terre + herbe, barres de boss (comme la référence) |
| `demacia-vs-noxus.config.js` | 15 champions + 40 sbires par région | arène sombre, grand tableau de score |

Pour en utiliser une : copie-la à la place de `battle.config.js`, puis lance `npm run seed`.

Réglages utiles dans `battle.config.js` :

- `champions` : une liste d'ids, ou une période de sortie, ex. `{ from: 2009, to: 2010 }`
- `arena` : `"dirt"` (terre + herbe) ou `"hextech"` (arène sombre)
- `hud` : `"boss"` (barres des plus forts) ou `"score"` (grand tableau)
- `unitScale` : taille des unités (plus petit pour les grandes armées)
- `hpScale` : multiplicateur de PV (plus grand = combat plus long)

## Faire une nouvelle vidéo

```bash
cd videos/lol-arena
# 1. Modifie battle.config.js : titre, équipes, champions, nombre de sbires
# 2. Équilibre les équipes et choisis le combat le plus serré (met aussi la durée à jour) :
npm run seed
# 3. Regarde le résultat dans le navigateur :
npm run dev
# 4. Exporte le MP4 (renders/arena.mp4) :
npm run render
```

`npm run seed` équilibre d'abord les deux armées : il donne un bonus de PV et de dégâts
(`boost`) à l'équipe la plus faible, jusqu'à ce que chaque camp gagne environ 1 combat sur 2.
Ensuite il garde la graine la plus spectaculaire : renversements, dernier coup sur un
champion, durée entre 45 et 75 s.

Options de `npm run seed` :

- `-- --winner 1` : la 2e équipe gagne
- `-- --tries 1000` : cherche plus longtemps
- `-- --seed 42` : force la graine 42
- `-- --no-balance` : garde les stats brutes, sans bonus d'équilibrage
- `-- --min 45 --max 75` : durée visée de la vidéo, en secondes

## Vraies icônes des champions

Sans icônes, chaque champion est un jeton à ses initiales et à sa couleur. Pour utiliser les
vraies icônes, lance cette commande sur ta machine (elle a besoin d'Internet) :

```bash
npm run icons
```

Elle télécharge les icônes depuis Data Dragon, le CDN public de Riot, dans `assets/champions/`.
Tu peux aussi déposer tes propres images `assets/champions/<id>.png` et ajouter leur id dans
`assets/champions/manifest.js`.

> Contenu de fans : Riot autorise ses assets dans des vidéos non commerciales. Mets cette mention
> dans la description : *« Created under Riot Games' "Legal Jibber Jabber" policy using assets
> owned by Riot Games. Riot Games does not endorse or sponsor this project. »*

## Ajouter des champions

Dans `src/roster.js` (détaillé) ou `src/roster-all.js` (une ligne par champion, avec son année
de sortie), chaque champion a un rôle (tank, combattant, assassin, mage, tireur ou
support), qui fixe ses stats, puis un sort et un ultime avec un type d'effet :
`nuke`, `aoe`, `spin`, `dash`, `stun`, `aoestun`, `heal`, `execute` ou `drain`.
Environ 140 champions sont déjà décrits : tous ceux de 2009-2010 et de 2013-2025, plus Demacia,
Noxus et quelques autres (Ahri, Zed, Lee Sin...). Il manque surtout ceux de 2011-2012.

Idées d'affiches : Ionia vs Zaun, Tanks vs Assassins, Champions de 2009 vs Champions récents,
Yordles vs Le reste du monde, 1 Malphite vs 60 sbires...

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `battle.config.js` | **la bataille** : équipes, champions, textes, graine |
| `src/roster.js` | champions détaillés, stats des rôles et des sbires |
| `src/roster-all.js` | roster étendu avec les années de sortie |
| `battles/` | affiches prêtes à l'emploi |
| `src/sim.js` | moteur de simulation, déterministe (même graine = même combat) |
| `src/render.js` | dessin canvas : arène, unités, effets, interface, intro et outro |
| `index.html` | composition HyperFrames (charge le reste et pilote le temps) |
| `scripts/pick-seed.mjs` | équilibrage et choix de la graine |
| `scripts/fetch-icons.mjs` | téléchargement des icônes officielles |

## Son

La vidéo est muette. Ajoute la musique dans TikTok ou CapCut, avec un son tendance.
