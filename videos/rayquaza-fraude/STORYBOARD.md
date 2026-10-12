---
format: 1080x1920
duration: 87s (voix 82.8 s, prise 1)
message: "Rayquaza, le soi-disant gardien de la planète, n'a jamais fait son taf : c'est la plus grosse fraude des légendaires."
arc: Accusation → La pub mensongère → Le bilan (3 chefs d'accusation) → Verdict K.O. → Rétrogradation en Chenipan
audience: fans de Pokémon sur TikTok
mode: collaborative
---

# Rayquaza : la fraude — storyboard v1

## Décisions

- **Message** : Rayquaza n'a jamais fait le seul job qu'il revendique — gardien de la planète.
- **Format** : 1080×1920 (TikTok), ~90 s (calé sur la vraie voix off), voix off ElevenLabs « Mattyang », musique + bruitages Pokémon fournis par l'utilisateur, sous-titres TikTok mot à mot dans le tiers inférieur (zone 1200–1500 px), contenu principal au-dessus.
- **Le fil rouge (spine)** : une **interface de combat Pokémon Gen 3** permanente en haut de l'écran. Rayquaza a une barre de PV renommée **« CRÉDIBILITÉ »**. Chaque preuve est une attaque : la barre chute (vert → jaune → rouge) avec une boîte de dialogue « C'est super efficace ! ». À la fin : 0 PV → « RAYQUAZA est K.O. » → **anti-évolution** (l'animation d'évolution à l'envers) → Chenipan. C'est la promesse du hook payée à la dernière seconde.
- **Look** : ciel nocturne vert émeraude (couleurs de Rayquaza : vert #1E8A55, jaune #F4C430, accents rouges #E23B3B pour les « preuves »), sprites pixel art en *nearest-neighbor* (pas de flou), typo **Archivo Black** pour les punchlines, police pixel (Press Start 2P) pour l'UI de combat, **Space Mono** pour les « dossiers ».
- **Transitions** : coupes sèches sur le rythme + « flash blanc » façon début de combat Pokémon entre les actes, zoom punch sur les mots clés. Direction des seams : vers la gauche.
- **Interdits** : pas de sprites redessinés, pas de sons générés (hors voix off demandée), pas de diaporama (chaque scène doit bouger *avec* la phrase), pas d'écran figé à la fin.
- **Plan fixe** : scène 04 « Ok. Maintenant on regarde son bilan. » — tout s'arrête, la musique coupe, juste le texte.

## Assets à fournir (sprites Gen 3 / pixel)

Dossier : `videos/rayquaza-fraude/assets/sprites/` (PNG fond transparent)

| Fichier | Contenu |
|---|---|
| rayquaza.png | Rayquaza (face, Émeraude) |
| rayquaza-back.png | Rayquaza (dos) — optionnel, pour l'UI de combat |
| chenipan.png | Chenipan |
| arceus.png, dialga.png, palkia.png | sprites DP/Platine (ils n'existent pas en Gen 3) |
| groudon.png, kyogre.png | Gen 3 (je les teinte rouge/bleu avec une aura pour « Primo ») — ou primo-groudon.png / primo-kyogre.png si tu as une version pixel |
| deoxys.png (+ deoxys-attaque/defense/vitesse optionnels) | Deoxys |
| az.png | AZ (sprite XY ou artwork) — optionnel |
| arme-ultime.png | l'Arme Ultime (XY) — optionnel |
| larousse-city.png | Larousse City (film Deoxys) — optionnel |
| robot-securite.png | robot de sécurité du film (optionnel, sinon je fais des silhouettes) |

## Audio à fournir

Dossier : `videos/rayquaza-fraude/assets/audio/`

- **Musique** : 1 à 2 pistes (ex. « Combat Rayquaza / Pilier Céleste » ROSA ou Émeraude, + un thème plus tendu pour la partie Deoxys).
- **Cris** : rayquaza, groudon, kyogre, deoxys, chenipan.
- **Bruitages** : coup « super efficace », barre de PV qui descend, bip PV bas, K.O. (Pokémon qui tombe), évolution (+ son d'évolution annulée), bip de menu / dialogue, sortie de Poké Ball, transition de début de combat.

## Frame 1 — L'accusation

- status: animated
- scene: Rayquaza en gros plan, tampon rouge « FRAUDE » qui s'écrase dessus
- duration: 3.5s
- transition_in: cut
- voiceover: "Ce ptit con de Rayquaza est la plus grosse fraude des légendaires"
- blueprint: kinetic-type-beats
- rules: spring-pop-entrance, chromatic-glitch
- src: compositions/01-accusation.html
- audio: cri de Rayquaza à 0.2s, impact sur « fraude »

Hook : Rayquaza entre en zoom, « LA PLUS GROSSE FRAUDE DES LÉGENDAIRES » claque mot par mot, tampon FRAUDE + glitch RGB.

## Frame 2 — La promesse

- status: animated
- scene: Rayquaza → flèche → Chenipan ; l'UI de combat apparaît avec la barre CRÉDIBILITÉ pleine
- duration: 3.5s
- transition_in: cut
- voiceover: "et devrait redevenir un Chenipan. Et j'vais te le prouver."
- rules: scale-swap-transition, stat-bars-and-fills
- src: compositions/02-promesse.html

Rayquaza rétrécit, Chenipan pop à côté. Sur « prouver », l'UI de combat glisse en haut : « RAYQUAZA N.70 — CRÉDIBILITÉ ██████ 100% ». Elle reste jusqu'à la fin.

## Frame 3 — La pub mensongère

- status: animated
- scene: Rayquaza en majesté façon affiche officielle, trois titres qui claquent
- duration: 7s
- transition_in: flash
- voiceover: "Depuis des générations, on nous le vend comme le gardien ultime de la planète. Le dieu serpent du ciel. Le grand protecteur de l'humanité."
- blueprint: kinetic-type-beats
- rules: ambient-glow-bloom, kinetic-beat-slam
- src: compositions/03-pub.html

Lumière dorée, rayons, Terre qui tourne derrière. « GARDIEN ULTIME », « DIEU SERPENT DU CIEL », « PROTECTEUR DE L'HUMANITÉ » s'empilent comme une pub télé, avec un petit bandeau « ✓ OFFICIEL ».

## Frame 4 — Le bilan (plan fixe)

- status: animated
- scene: Écran noir-vert, « OK. MAINTENANT ON REGARDE SON BILAN. » ; un dossier « BILAN » s'ouvre
- duration: 2.5s
- transition_in: cut
- voiceover: "Ok. Maintenant on regarde son bilan."
- rules: discrete-text-sequence
- src: compositions/04-bilan.html
- audio: la musique coupe net (scratch)

Le seul moment calme du film. Tout s'arrête pour que la phrase tombe.

## Frame 5 — L'Arme Ultime

- status: animated
- scene: Compteur « IL Y A 3 000 ANS », AZ + Arme Ultime, onde de choc qui disperse des sprites, écran qui se déchire
- duration: 7s
- transition_in: cut
- voiceover: "Il y a 3 000 ans, AZ tire avec l'Arme Ultime. Des milliers de Pokémon y passent. Une énergie capable de déchirer la réalité."
- rules: counting-dynamic-scale, particle-burst, chromatic-glitch
- src: compositions/05-arme-ultime.html

Le compteur défile jusqu'à -3000, flash de l'Arme, onde circulaire, l'écran se fend (déchirure) sur « déchirer la réalité ».

## Frame 6 — Absent

- status: animated
- scene: Ciel vide, radar qui cherche, « ? » ; tampon « ABSENT » ; 1re attaque sur la barre
- duration: 3s
- transition_in: cut
- voiceover: "Il est où, Rayquaza ? Personne sait."
- rules: svg-icon-enrichment, stat-bars-and-fills
- src: compositions/06-absent.html
- audio: bip radar, « super efficace », PV qui descendent

Silhouette de Rayquaza en pointillés = place vide. Barre CRÉDIBILITÉ : 100 → 80.

## Frame 7 — Personne n'a bougé

- status: animated
- scene: Arceus, Dialga, Palkia alignés, chacun barré d'une croix ; « AUCUN LÉGENDAIRE N'A BOUGÉ »
- duration: 5.5s
- transition_in: cut
- voiceover: "Alors ok, soyons honnêtes : AUCUN légendaire n'a bougé. Ni Arceus, ni Dialga, ni Palkia. Personne."
- rules: waterfall-entry, css-marker-patterns
- src: compositions/07-personne.html

Les trois tombent en cascade, une croix rouge à chaque nom prononcé. Sur « Personne » : ils s'éteignent en gris.

## Frame 8 — La fiche de poste

- status: animated
- scene: Fiche de poste officielle « POSTE : GARDIEN DE LA PLANÈTE — Titulaire : Rayquaza », surlignée
- duration: 6s
- transition_in: cut
- voiceover: "Sauf que les autres, ils se sont jamais présentés comme LE gardien de la planète. Lui, si. C'est littéralement sa fiche de poste."
- rules: css-marker-patterns, coordinate-target-zoom
- src: compositions/08-fiche-de-poste.html
- audio: « super efficace », PV qui descendent

Les autres légendaires glissent hors champ, Rayquaza reste. Document en Space Mono, zoom sur « GARDIEN DE LA PLANÈTE » surligné jaune. Barre : 80 → 62.

## Frame 9 — Primo-Groudon vs Primo-Kyogre

- status: animated
- scene: Écran coupé en deux : Groudon (lave, rouge) / Kyogre (océan, bleu) ; planète au milieu qui sèche / se noie
- duration: 4.5s
- transition_in: flash
- voiceover: "Primo-Groudon et Primo-Kyogre veulent assécher les océans et noyer la planète."
- rules: split-tilt-cards, sine-wave-loop
- src: compositions/09-primo.html
- audio: cris Groudon + Kyogre

## Frame 10 — Le rituel

- status: animated
- scene: « INTERVIENT DE LUI-MÊME ? » → « NON » qui claque ; checklist « ☑ PRIER ☑ SUPPLIER ☑ RITUEL »
- duration: 6s
- transition_in: cut
- voiceover: "Est-ce que Rayquaza intervient de lui-même ? Non. Il faut que les humains prient, supplient, fassent tout le rituel…"
- rules: kinetic-beat-slam, waterfall-entry
- src: compositions/10-rituel.html

## Frame 11 — L'autel et la ola

- status: animated
- scene: Pilier Céleste / autel, une rangée de petits dresseurs pixel qui font la ola, Rayquaza qui daigne apparaître
- duration: 5s
- transition_in: cut
- voiceover: "En gros, le gardien de la Terre bouge que si tu lui construis un autel et que tu lui fais une ola."
- rules: waterfall-entry, stat-bars-and-fills
- src: compositions/11-ola.html
- audio: « super efficace », PV → zone jaune

Barre : 62 → 40 (passe au jaune).

## Frame 12 — La défense spatiale

- status: animated
- scene: Espace, Terre en bas, Rayquaza en orbite avec un badge « SÉCURITÉ » ; « SON SEUL TAF : SURVEILLER LE CIEL »
- duration: 5s
- transition_in: flash
- voiceover: "Mais le pire, c'est la défense spatiale. Son SEUL taf, c'est surveiller le ciel."
- rules: orbit-3d-entry, kinetic-beat-slam
- src: compositions/12-defense-spatiale.html

## Frame 13 — Le cristal oublié

- status: animated
- scene: Météorite Deoxys qui tombe, Rayquaza l'explose ; un petit cristal qui brille entouré au marqueur « OUBLIÉ »
- duration: 5.5s
- transition_in: cut
- voiceover: "Premier Deoxys : il s'écrase sur Terre. Rayquaza le détruit… mais oublie le cristal."
- rules: motion-blur-streak, particle-burst, css-marker-patterns, coordinate-target-zoom
- src: compositions/13-cristal.html
- audio: cri Deoxys, explosion, « super efficace »

Barre : 40 → 22 (rouge, bip PV bas).

## Frame 14 — Larousse City

- status: animated
- scene: Skyline de Larousse City, Rayquaza qui fonce en furie, bâtiments qui tremblent, « LAROUSSE CITY : RAVAGÉE »
- duration: 6.5s
- transition_in: cut
- voiceover: "Quelques années plus tard : un deuxième Deoxys débarque. Rayquaza arrive en furie, ravage Larousse City entière…"
- rules: multi-phase-camera, chromatic-glitch
- src: compositions/14-larousse.html

## Frame 15 — La montagne de robots

- status: animated
- scene: Des dizaines de robots qui s'empilent sur Rayquaza jusqu'à le recouvrir
- duration: 3.5s
- transition_in: cut
- voiceover: "Et finit coincé sous une montagne de robots de sécurité."
- rules: waterfall-entry, reactive-displacement
- src: compositions/15-robots.html
- audio: bruits d'empilement, PV qui descendent

Barre : 22 → 5.

## Frame 16 — Sauvé par Deoxys → K.O. → Chenipan

- status: animated
- scene: Les Deoxys arrivent et le sauvent ; barre à 0 ; « RAYQUAZA est K.O. » ; anti-évolution en Chenipan
- duration: 6.5s
- transition_in: cut
- voiceover: "Et devine qui vient le sauver ? Les Deoxys. Ceux qu'il était venu exterminer."
- rules: spring-pop-entrance, stat-bars-and-fills, scale-swap-transition
- src: compositions/16-ko-chenipan.html
- audio: cri Deoxys, K.O., évolution, cri Chenipan

Les Deoxys entrent en formation, sur « exterminer » la barre tombe à 0, boîte de dialogue « RAYQUAZA est K.O. ! », puis flash d'évolution inversée : la silhouette blanche alterne Rayquaza/Chenipan et se fige en Chenipan. Dernier carton : « RAYQUAZA → CHENIPAN. Affaire classée. »
