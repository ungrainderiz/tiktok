# Arène LoL : simulation de bataille pour TikTok/Reels

Deux armées de champions de League of Legends s'affrontent toutes seules dans une arène,
jusqu'au dernier survivant. Le format reprend la vidéo de référence (Gen 1 vs Gen 3).
La vidéo est verticale (1080×1920) et dure environ 70 s :

1. **Intro** : « DEMACIA vs NOXUS — Qui gagne ? », les unités apparaissent dans des orbes, puis « COMBAT ! »
2. **Bataille** : les noms des sorts s'affichent, les ultimes ont un grand titre doré avec le portrait,
   la caméra suit la mêlée, avec chiffres de dégâts, fil des éliminations et barre de rapport de force.
3. **Ralenti** sur le dernier coup.
4. **Écran de victoire** : survivants, MVP et appel à commenter.

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

Options de `npm run seed` :

- `-- --winner 1` : la 2e équipe gagne
- `-- --tries 1000` : cherche plus longtemps
- `-- --seed 42` : force la graine 42
- `-- --no-balance` : garde les stats brutes, sans bonus d'équilibrage

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

Dans `src/roster.js`, chaque champion a un rôle (tank, combattant, assassin, mage, tireur ou
support), qui fixe ses stats, puis un sort et un ultime avec un type d'effet :
`nuke`, `aoe`, `spin`, `dash`, `stun`, `aoestun`, `heal`, `execute` ou `drain`.
Le fichier liste déjà Demacia, Noxus et quelques champions célèbres (Ahri, Yasuo, Zed, Jinx,
Thresh, Lee Sin, Malphite, Teemo).

Idées d'affiches : Ionia vs Zaun, Tanks vs Assassins, Champions de 2009 vs Champions récents,
Yordles vs Le reste du monde, 1 Malphite vs 60 sbires...

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `battle.config.js` | **la bataille** : équipes, champions, textes, graine |
| `src/roster.js` | champions, stats des rôles et des sbires |
| `src/sim.js` | moteur de simulation, déterministe (même graine = même combat) |
| `src/render.js` | dessin canvas : arène, unités, effets, interface, intro et outro |
| `index.html` | composition HyperFrames (charge le reste et pilote le temps) |
| `scripts/pick-seed.mjs` | équilibrage et choix de la graine |
| `scripts/fetch-icons.mjs` | téléchargement des icônes officielles |

## Son

La vidéo est muette. Ajoute la musique dans TikTok ou CapCut, avec un son tendance.
