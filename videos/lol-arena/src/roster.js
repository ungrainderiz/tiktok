/*
 * Roster des champions disponibles pour l'arène.
 *
 * Chaque champion a :
 *   - name   : nom affiché
 *   - role   : tank | fighter | assassin | mage | marksman | support (fixe les stats de base)
 *   - color  : couleur signature du jeton (utilisée si aucune icône n'est fournie)
 *   - spell  : sort de base  { name, type, ... }
 *   - ult    : ultime        { name, type, ... }
 *
 * Types de sorts gérés par la simulation (voir src/sim.js) :
 *   nuke     gros dégâts sur la cible
 *   aoe      dégâts de zone autour de la cible
 *   spin     dégâts de zone autour du lanceur
 *   dash     bond sur la cible + dégâts
 *   stun     dégâts + étourdissement de la cible
 *   aoestun  dégâts de zone + étourdissement
 *   heal     soin (soi-même, ou l'allié le plus blessé pour un support)
 *   execute  achève une cible sous 35 % de vie, sinon gros dégâts
 *   drain    dégâts + soin du lanceur
 *
 * Champs optionnels d'un sort : power (multiplicateur), radius, stun (secondes), cd (secondes).
 *
 * Pour ajouter un champion : copie une ligne, change l'id (= nom du fichier icône dans
 * assets/champions/<id>.png) et ajoute l'id dans une équipe de battle.config.js.
 */
(function (root) {
  const ROSTER = {
    // ------------------------------------------------------------------ DEMACIA
    garen:     { name: "Garen",     role: "fighter",  color: "#3d6fd1", spell: { name: "Judgment", type: "spin", radius: 85 },                  ult: { name: "Demacian Justice", type: "execute" } },
    lux:       { name: "Lux",       role: "mage",     color: "#f6e27a", spell: { name: "Light Binding", type: "stun", stun: 1.4 },             ult: { name: "Final Spark", type: "aoe", radius: 120, power: 3.2 } },
    jarvan:    { name: "Jarvan IV", role: "fighter",  color: "#d9b04a", spell: { name: "Dragon Strike", type: "nuke" },                        ult: { name: "Cataclysm", type: "aoestun", radius: 110, stun: 1.2 } },
    fiora:     { name: "Fiora",     role: "fighter",  color: "#8e5bd6", spell: { name: "Lunge", type: "dash" },                                ult: { name: "Grand Challenge", type: "drain", power: 3.2 } },
    galio:     { name: "Galio",     role: "tank",     color: "#9fb3c8", spell: { name: "Shield of Durand", type: "aoestun", radius: 90 },       ult: { name: "Hero's Entrance", type: "dash", power: 2.4, radius: 120 } },
    shyvana:   { name: "Shyvana",   role: "fighter",  color: "#c4532c", spell: { name: "Flame Breath", type: "aoe", radius: 70 },              ult: { name: "Dragon's Descent", type: "dash", power: 2.6, radius: 110 } },
    xinzhao:   { name: "Xin Zhao",  role: "fighter",  color: "#b8452f", spell: { name: "Audacious Charge", type: "dash" },                     ult: { name: "Crescent Guard", type: "spin", radius: 110, power: 2.4 } },
    quinn:     { name: "Quinn",     role: "marksman", color: "#4f86c6", spell: { name: "Blinding Assault", type: "nuke" },                     ult: { name: "Skystrike", type: "aoe", radius: 100, power: 2.6 } },
    vayne:     { name: "Vayne",     role: "marksman", color: "#5a3e8c", spell: { name: "Condemn", type: "stun", stun: 1.0 },                   ult: { name: "Final Hour", type: "nuke", power: 3.4 } },
    lucian:    { name: "Lucian",    role: "marksman", color: "#e8e4d8", spell: { name: "Piercing Light", type: "nuke" },                       ult: { name: "The Culling", type: "aoe", radius: 90, power: 2.8 } },
    poppy:     { name: "Poppy",     role: "tank",     color: "#6f8fd8", spell: { name: "Heroic Charge", type: "stun", stun: 1.2 },             ult: { name: "Keeper's Verdict", type: "aoestun", radius: 100, stun: 1.0 } },
    sona:      { name: "Sona",      role: "support",  color: "#4fc3c8", spell: { name: "Aria of Perseverance", type: "heal" },                 ult: { name: "Crescendo", type: "aoestun", radius: 120, stun: 1.2 } },
    kayle:     { name: "Kayle",     role: "fighter",  color: "#f2c45a", spell: { name: "Radiant Blast", type: "nuke" },                        ult: { name: "Divine Judgment", type: "aoe", radius: 120, power: 2.6 } },
    sylas:     { name: "Sylas",     role: "fighter",  color: "#5e7bb5", spell: { name: "Kingslayer", type: "drain" },                          ult: { name: "Hijack", type: "nuke", power: 3.4 } },
    morgana:   { name: "Morgana",   role: "mage",     color: "#6b3fa0", spell: { name: "Dark Binding", type: "stun", stun: 1.6 },              ult: { name: "Soul Shackles", type: "aoestun", radius: 110, stun: 1.4 } },

    // ------------------------------------------------------------------ NOXUS
    darius:    { name: "Darius",    role: "fighter",  color: "#a3242b", spell: { name: "Decimate", type: "spin", radius: 85 },                 ult: { name: "Noxian Guillotine", type: "execute" } },
    draven:    { name: "Draven",    role: "marksman", color: "#c0392b", spell: { name: "Spinning Axe", type: "nuke" },                         ult: { name: "Whirling Death", type: "aoe", radius: 110, power: 2.6 } },
    swain:     { name: "Swain",     role: "mage",     color: "#7a1e2c", spell: { name: "Death's Hand", type: "aoe", radius: 80 },              ult: { name: "Demonic Ascension", type: "drain", power: 3.0, radius: 120 } },
    katarina:  { name: "Katarina",  role: "assassin", color: "#d6303a", spell: { name: "Shunpo", type: "dash" },                               ult: { name: "Death Lotus", type: "spin", radius: 115, power: 3.0 } },
    talon:     { name: "Talon",     role: "assassin", color: "#4a4f5c", spell: { name: "Noxian Diplomacy", type: "dash" },                     ult: { name: "Shadow Assault", type: "spin", radius: 100, power: 2.8 } },
    cassio:    { name: "Cassiopeia",role: "mage",     color: "#5fa34a", spell: { name: "Noxious Blast", type: "aoe", radius: 75 },             ult: { name: "Petrifying Gaze", type: "aoestun", radius: 120, stun: 1.4 } },
    leblanc:   { name: "LeBlanc",   role: "assassin", color: "#9b3fa6", spell: { name: "Distortion", type: "dash" },                           ult: { name: "Mimic", type: "nuke", power: 3.4 } },
    sion:      { name: "Sion",      role: "tank",     color: "#8a7a5c", spell: { name: "Decimating Smash", type: "aoestun", radius: 90 },       ult: { name: "Unstoppable Onslaught", type: "dash", power: 2.6, radius: 120 } },
    samira:    { name: "Samira",    role: "marksman", color: "#c85a3c", spell: { name: "Wild Rush", type: "dash" },                            ult: { name: "Inferno Trigger", type: "spin", radius: 120, power: 2.8 } },
    mordekaiser:{name: "Mordekaiser",role: "fighter", color: "#3fa36b", spell: { name: "Obliterate", type: "aoe", radius: 70 },                ult: { name: "Realm of Death", type: "drain", power: 3.2 } },
    vladimir:  { name: "Vladimir",  role: "mage",     color: "#b0102a", spell: { name: "Transfusion", type: "drain" },                         ult: { name: "Hemoplague", type: "aoe", radius: 120, power: 2.6 } },
    kled:      { name: "Kled",      role: "fighter",  color: "#c79a3a", spell: { name: "Beartrap on a Rope", type: "nuke" },                   ult: { name: "Chaaaaaaaarge!!!", type: "dash", power: 2.6, radius: 110 } },
    riven:     { name: "Riven",     role: "fighter",  color: "#7fa36b", spell: { name: "Broken Wings", type: "dash" },                         ult: { name: "Wind Slash", type: "execute" } },
    rell:      { name: "Rell",      role: "support",  color: "#5b5f8c", spell: { name: "Shattering Strike", type: "stun", stun: 1.0 },         ult: { name: "Magnet Storm", type: "aoestun", radius: 110, stun: 1.2 } },
    briar:     { name: "Briar",     role: "fighter",  color: "#c0405a", spell: { name: "Head Rush", type: "stun", stun: 1.0 },                 ult: { name: "Certain Death", type: "dash", power: 3.0 } },

    // ------------------------------------------------------------------ AUTRES (pour d'autres affiches)
    ahri:      { name: "Ahri",      role: "mage",     color: "#d86aa8", spell: { name: "Orb of Deception", type: "nuke" },                     ult: { name: "Spirit Rush", type: "dash", power: 2.6 } },
    yasuo:     { name: "Yasuo",     role: "fighter",  color: "#5d8fc9", spell: { name: "Steel Tempest", type: "nuke" },                        ult: { name: "Last Breath", type: "aoestun", radius: 90, stun: 1.0 } },
    zed:       { name: "Zed",       role: "assassin", color: "#a12a2a", spell: { name: "Razor Shuriken", type: "nuke" },                       ult: { name: "Death Mark", type: "execute" } },
    jinx:      { name: "Jinx",      role: "marksman", color: "#e04aa8", spell: { name: "Flame Chompers!", type: "aoestun", radius: 70 },       ult: { name: "Super Mega Death Rocket!", type: "aoe", radius: 130, power: 3.0 } },
    thresh:    { name: "Thresh",    role: "support",  color: "#3fbf8a", spell: { name: "Death Sentence", type: "stun", stun: 1.4 },            ult: { name: "The Box", type: "aoestun", radius: 110 } },
    leesin:    { name: "Lee Sin",   role: "fighter",  color: "#d6782c", spell: { name: "Sonic Wave", type: "dash" },                           ult: { name: "Dragon's Rage", type: "nuke", power: 3.4 } },
    malphite:  { name: "Malphite",  role: "tank",     color: "#8a6d4a", spell: { name: "Ground Slam", type: "spin", radius: 90 },              ult: { name: "Unstoppable Force", type: "aoestun", radius: 130, stun: 1.4 } },
    teemo:     { name: "Teemo",     role: "marksman", color: "#7ab85a", spell: { name: "Blinding Dart", type: "stun", stun: 1.0 },             ult: { name: "Noxious Trap", type: "aoe", radius: 90, power: 2.4 } },
  };

  // Stats de base par rôle (unités de la simulation : px, px/s, secondes).
  const ROLES = {
    tank:     { hp: 2250, dmg: 34, range: 46,  speed: 72,  atk: 1.05, radius: 28, armor: 0.30 },
    fighter:  { hp: 1580, dmg: 56, range: 44,  speed: 86,  atk: 0.95, radius: 26, armor: 0.15 },
    assassin: { hp: 1300, dmg: 88, range: 40,  speed: 118, atk: 0.85, radius: 24, armor: 0.20 },
    mage:     { hp: 960,  dmg: 62, range: 230, speed: 70,  atk: 1.30, radius: 24, armor: 0.00, projectile: true },
    marksman: { hp: 960,  dmg: 50, range: 270, speed: 76,  atk: 0.75, radius: 24, armor: 0.00, projectile: true },
    support:  { hp: 1140, dmg: 32, range: 210, speed: 74,  atk: 1.20, radius: 24, armor: 0.10, projectile: true },
  };

  // Sbires : la « chair à canon » de chaque armée.
  const MINIONS = {
    melee:  { name: "Sbire mêlée",    hp: 230, dmg: 14, range: 30,  speed: 80, atk: 1.1, radius: 12, armor: 0.0 },
    caster: { name: "Sbire mage",     hp: 150, dmg: 17, range: 170, speed: 76, atk: 1.4, radius: 11, armor: 0.0, projectile: true },
    siege:  { name: "Sbire canon",    hp: 480, dmg: 34, range: 210, speed: 66, atk: 1.9, radius: 16, armor: 0.1, projectile: true },
  };

  const api = { ROSTER, ROLES, MINIONS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.LOL = Object.assign(root.LOL || {}, api);
})(typeof window !== "undefined" ? window : globalThis);
