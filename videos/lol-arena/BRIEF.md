---
workflow: general-video
flow: automation
storyboard: no
message: "Deux armées de champions LoL s'affrontent seules dans une arène : qui gagne ?"
destination: tiktok
aspect: "9:16"
language: fr
length: "~70s"
---

## Intent

Reprendre le format « simulation de bataille en arène » de la vidéo de référence (Gen 1 vs Gen 3,
deux armées d'unités qui se battent toutes seules jusqu'au dernier survivant, noms des attaques
qui s'affichent, barres de vie, coup final) avec des champions de League of Legends.
Première affiche : Demacia vs Noxus.

## Decisions (inferred)

- Visuels originaux (jetons aux initiales) tant que les icônes officielles ne sont pas
  téléchargées (`npm run icons`, Data Dragon bloqué dans la session cloud).
- Noms des sorts en anglais (noms officiels du kit), textes d'interface en français.
- Pas de musique : à ajouter dans TikTok/CapCut (son tendance).
- Équilibrage automatique + choix de la graine la plus serrée (`npm run seed`).
