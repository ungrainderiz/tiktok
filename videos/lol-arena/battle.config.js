/*
 * ⚔  CONFIGURATION DE LA BATAILLE  ⚔
 *
 * C'est le seul fichier à modifier pour faire une nouvelle vidéo :
 *   - change le titre, les noms et couleurs des équipes
 *   - choisis les champions (ids de src/roster.js)
 *   - règle le nombre de sbires
 *   - puis lance `npm run seed` pour trouver une graine qui donne un combat serré
 *     (ça met aussi à jour la durée de la vidéo dans index.html).
 */
(function (root) {
  const BATTLE = {
    title: "DEMACIA vs NOXUS",
    subtitle: "15 champions + 40 sbires chacun",
    question: "Qui gagne ?",
    outro: "Quelle région la prochaine fois ? Dis-le en commentaire",

    // Graine aléatoire : même graine = même combat, image par image.
    // (choisie automatiquement par `npm run seed`)
    seed: 187,

    teams: [
      {
        name: "DEMACIA",
        color: "#4aa3ff", // couleur principale
        accent: "#f3d27a", // couleur secondaire (or)
        champions: ["garen", "lux", "jarvan", "fiora", "galio", "shyvana", "xinzhao", "quinn",
                    "vayne", "lucian", "poppy", "sona", "kayle", "sylas", "morgana"],
        minions: { melee: 20, caster: 14, siege: 6 },
        boost: 1, // bonus de PV/dégâts réglé automatiquement par `npm run seed` (équilibrage)
      },
      {
        name: "NOXUS",
        color: "#ff3b3b",
        accent: "#2a0d10",
        champions: ["darius", "draven", "swain", "katarina", "talon", "cassio", "leblanc", "sion",
                    "samira", "mordekaiser", "vladimir", "kled", "riven", "rell", "briar"],
        minions: { melee: 20, caster: 14, siege: 6 },
        boost: 1.077,
      },
    ],
  };

  if (typeof module !== "undefined" && module.exports) module.exports = BATTLE;
  else root.BATTLE = BATTLE;
})(typeof window !== "undefined" ? window : globalThis);
