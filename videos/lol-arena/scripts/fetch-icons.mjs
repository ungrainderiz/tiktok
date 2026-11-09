#!/usr/bin/env node
/*
 * Télécharge les icônes carrées des champions depuis Data Dragon (le CDN public de Riot pour
 * les développeurs et créateurs de contenu) dans assets/champions/<id>.png, puis met à jour
 * assets/champions/manifest.js. À lancer sur ta machine : `npm run icons`.
 *
 * Sans icônes, la vidéo utilise des jetons dessinés (initiales + couleur du champion).
 *
 * Contenu de fans : Riot autorise l'utilisation de ses assets dans des vidéos non commerciales
 * (« Legal Jibber Jabber »). Ajoute la mention suivante dans ta description :
 *   « [Titre] was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by
 *     Riot Games. Riot Games does not endorse or sponsor this project. »
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
await import(path.join(root, "src/roster.js"));
const { ROSTER } = globalThis.LOL;

// id du roster -> nom de fichier Data Dragon quand ils diffèrent
const DDRAGON_ID = {
  jarvan: "JarvanIV", xinzhao: "XinZhao", cassio: "Cassiopeia", leblanc: "Leblanc",
  leesin: "LeeSin", mordekaiser: "Mordekaiser",
};
const toDD = (id) => DDRAGON_ID[id] || id.charAt(0).toUpperCase() + id.slice(1);

const versions = await (await fetch("https://ddragon.leagueoflegends.com/api/versions.json")).json();
const v = versions[0];
console.log("Data Dragon version " + v);

const outDir = path.join(root, "assets/champions");
fs.mkdirSync(outDir, { recursive: true });
const ok = [];
for (const id of Object.keys(ROSTER)) {
  const url = `https://ddragon.leagueoflegends.com/cdn/${v}/img/champion/${toDD(id)}.png`;
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(r.status);
    fs.writeFileSync(path.join(outDir, id + ".png"), Buffer.from(await r.arrayBuffer()));
    ok.push(id);
    console.log("  ✓ " + id);
  } catch (e) {
    console.log(`  ✗ ${id} (${url} -> ${e.message})`);
  }
}
const manifest = `/*
 * Liste des icônes de champions présentes dans ce dossier (assets/champions/<id>.png).
 * Générée par \`npm run icons\`. Laisse le tableau vide pour utiliser les jetons dessinés.
 */
window.LOL_ICONS = ${JSON.stringify(ok)};
`;
fs.writeFileSync(path.join(outDir, "manifest.js"), manifest);
console.log(`${ok.length} icônes enregistrées. Relance le rendu : npm run render`);
