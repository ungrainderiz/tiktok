# TikToks de Matt — mémoire du projet

Chaque vidéo vit dans `videos/<nom>/` (projets HyperFrames). Ce fichier garde ce qui doit rester
d'une vidéo à l'autre : **le style de narration** et les préférences de production.

## Style de narration (à respecter pour tout nouveau script)

Références : `videos/rayquaza-fraude/BRIEF.md` (script « Rayquaza la fraude ») et
`videos/anohana/SCRIPT.md` (script AnoHana).

**Ton et registre**
- Français oral, familier, comme un pote qui raconte : « t'es », « t'as », « y a », « j'vais »,
  négation sans « ne » (« Personne sait », « Tu sors plus »).
- Argot et petites insultes affectueuses quand le sujet s'y prête (« ce ptit con », « son taf »,
  « une ola », « bam »).
- Deux registres selon le sujet :
  - **réquisitoire de mauvaise foi, drôle** (Rayquaza) : on accuse, on démonte avec des preuves ;
  - **récit émotionnel en « tu »** (AnoHana) : on met le spectateur dans la peau du héros.

**Structure**
1. **Hook dès la 1re phrase** : soit une accusation choc + promesse (« … est la plus grosse fraude
   des légendaires. Et j'vais te le prouver. »), soit une immersion (« Imagine, t'es le boss de la
   récréation en primaire. »).
2. **Mise en place rapide** : ce qu'on croit savoir / la situation de départ.
3. **Retournement** avec les mêmes connecteurs : « Sauf que… », « Mais le pire, c'est… »,
   « Ok. Maintenant on regarde son bilan. », « Et puis un jour… ».
4. **Montée** par étapes ou preuves successives, chacune finie par une punchline.
5. **Chute** : punchline ironique (« Ceux qu'il était venu exterminer. ») ou teaser émotionnel
   (« Et tu sais que t'es pas prêt pour ce qui arrive. »).

**Procédés récurrents**
- Phrases très courtes, souvent nominales. Une idée par phrase.
- **Rythme en trois** : « C'est doux, c'est triste, c'est puissant. » / « Tu sors plus, tu parles
  plus, tu vis enfermé avec tes regrets. » / « prient, supplient, fassent tout le rituel ».
- **Question rhétorique + réponse sèche** : « Il est où, Rayquaza ? Personne sait. » /
  « Est-ce qu'il intervient de lui-même ? Non. »
- **Concession puis contre-attaque** : « Alors ok, soyons honnêtes : … Sauf que … »
- **Points de suspension pour le suspense** : « Et puis un jour… accident. », « Jusqu'à ce que… bam. »
- **Mots en MAJUSCULES** pour l'emphase orale : « AUCUN légendaire », « LE gardien », « Son SEUL taf ».
- Références pop culture / anime glissées en passant (« comme Rudeus »).
- Une petite image concrète et absurde pour résumer (« il bouge que si tu lui construis un autel
  et que tu lui fais une ola »).

**Boucle (obligatoire)** — la fin ne doit pas se remarquer : la vidéo repart au début comme si c'était la suite.
- **Texte** : la dernière phrase reste en suspens et se complète avec la 1re phrase du script.
  Ex. AnoHana : « …Et si tu comprends toujours pas pourquoi tout le monde pleure devant AnoHana… »
  → (retour au début) « Imagine, t'es le boss de la récréation en primaire. »
  Ex. Rayquaza : « …Ceux qu'il était venu exterminer. Et c'est pour ça que j'te le dis : » →
  « Ce ptit con de Rayquaza est la plus grosse fraude des légendaires… »
- **Pas d'outro** : pas de carton de fin, pas de fondu au noir, pas de silence. La voix démarre dès 0 s
  et la dernière syllabe tombe sur la toute dernière image.
- **Montage (image)** : la toute dernière image et la toute première doivent se raccorder comme une
  coupe normale du montage. Techniques, au choix :
  - **raccord par le blanc/flash** : la fin monte vers un écran blanc, le début sort de ce même blanc
    (ex. Rayquaza : Chenipan se remet à briller → blanc → Rayquaza surgit du blanc = « il ré-évolue ») ;
  - **même plan** : la vidéo finit sur le plan qui l'ouvre, même cadrage et même zoom ;
  - **mouvement continu** : le zoom / travelling de fin continue dans le même sens que celui du début.
  - Les éléments d'interface (HUD, sous-titres) doivent être dans le même état à la fin et au début
    (masqués des deux côtés).
- **Son** : la musique ne fait ni fade-in ni fade-out ; la vidéo se termine sur un temps fort du morceau
  et le début de la musique repart sur un temps fort, pour que le raccord tombe en rythme.

**Format**
- 60 à 90 s de voix (≈ 200–260 mots), TikTok vertical 1080×1920.
- Ne pas lisser le texte en français écrit : garder les élisions et le parlé.

## Préférences de production

- **Voix off** : ElevenLabs, voix clonée « Mattyang » (voice_id `LJyZNyC1T0VPHgeMjROb`), modèle eleven_v4.
  Une prise coûte ≈ 1 crédit par caractère du script : vérifier le solde avant de lancer.
- **Visuels** : vrais assets (sprites officiels, images de l'œuvre), jamais redessinés. Motion design
  dynamique, coupes sur la voix.
  - **Horreur = SOMBRE** : nuit, noirs profonds, peu de lumière (une seule source : lampe, flamme, écran),
    couleurs désaturées, grain, vignette lourde. Pas de décors de jour colorés : l'atmosphère doit faire peur.
  - **Pas de plans « marche à la 1re personne sur une route »** (sol en perspective qui défile) : jugés ratés
    (Funécire, Wakfu). Préférer des plans fixes ou lents, cadrés serré, en intérieur/gros plans.
  - Pixel art « HD » si on dessine : paquets de formes ombrées, 5–6 tons par matière, sans contour
    (références : arbre pixel art, Nox fan art, Sadida du jeu — voir `videos/wakfu-nox/tools/pixelart.py`).
- **Sous-titres** : mot à mot, style TikTok, mot prononcé mis en valeur.
- **Audio** : musique sous la voix (creusée/duckée), cris de Pokémon discrets (≈ 10–20 %),
  bruitages présents mais jamais au-dessus de la voix. Copie finale normalisée à -14 LUFS.
  - **Banque de bruitages partagée : `bruitages/`** (sons envoyés par Matt, un fichier par son, `index.json`
    + `BRUITAGES.md` avec ambiance et usage). La consulter à chaque vidéo et y piocher aux moments
    appropriés (horreur → horreur/tension/impact ; drôle → memes). Nouvelle compilation reçue →
    `python3 bruitages/tools/importer.py <video> <coupes.json>`. Compléter avec des sons synthétisés si besoin.
  - Voix clonée souvent basse : la remonter vers -20 LUFS par gain linéaire (pas de loudnorm, qui raccourcit
    la piste et casse la boucle).
- **Livraison** : envoyer une copie compressée (< 30 Mo) ; les rendus restent hors de git.
