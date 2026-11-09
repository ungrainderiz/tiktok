/*
 * ⚔  CONFIGURATION DE LA BATAILLE  ⚔
 *
 * C'est le seul fichier à modifier pour faire une nouvelle vidéo :
 *   - change le titre, les noms et couleurs des équipes
 *   - choisis les champions : une liste d'ids (src/roster.js, src/roster-all.js)
 *     ou une période de sortie, ex. { from: 2009, to: 2010 }
 *   - règle le nombre de sbires (0 = que des champions)
 *   - puis lance `npm run seed` pour équilibrer et trouver un combat serré
 *     (ça met aussi à jour la durée de la vidéo dans index.html).
 *
 * D'autres affiches toutes prêtes sont dans battles/ : copie-en une à la place de ce fichier.
 */
(function (root) {
  const BATTLE = {
    title: "Anciens vs Nouveaux !",
    subtitle: "Champions 2009-2010 contre champions 2013-2025",
    question: "Qui gagne ?",
    outro: "Quelle bataille la prochaine fois ? Dis-le en commentaire",

    // Apparence : arena "dirt" (terre + herbe) ou "hextech" (arène sombre)
    //             hud "boss" (barres des plus forts) ou "score" (grand tableau)
    arena: "dirt",
    hud: "boss",
    unitScale: 0.7, // taille des unités (armées géantes = plus petit)
    hpScale: 2.6, // multiplie les PV : plus grand = combat plus long

    // Graine aléatoire : même graine = même combat, image par image.
    // (choisie automatiquement par `npm run seed`)
    seed: 12,

    teams: [
      {
        name: "ANCIENS",
        color: "#ffb02e",
        accent: "#7a4a00",
        champions: { from: 2009, to: 2010 },
        minions: { melee: 0, caster: 0, siege: 0 },
        boost: 1, // bonus de PV/dégâts réglé automatiquement par `npm run seed` (équilibrage)
      },
      {
        name: "NOUVEAUX",
        color: "#b24dff",
        accent: "#2b0a4a",
        champions: { from: 2013, to: 2025 },
        minions: { melee: 0, caster: 0, siege: 0 },
        boost: 1.317,
      },
    ],
  };

  if (typeof module !== "undefined" && module.exports) module.exports = BATTLE;
  else root.BATTLE = BATTLE;
})(typeof window !== "undefined" ? window : globalThis);
