#!/usr/bin/env node
/*
 * Cherche une graine qui donne un combat spectaculaire et serré, puis :
 *   - écrit la graine dans battle.config.js
 *   - met à jour la durée de la vidéo (data-duration) dans index.html
 *
 * Usage :
 *   node scripts/pick-seed.mjs            -> teste les graines 1..300 et garde la meilleure
 *   node scripts/pick-seed.mjs --tries 1000
 *   node scripts/pick-seed.mjs --seed 42  -> force la graine 42 (met juste la durée à jour)
 *   node scripts/pick-seed.mjs --winner 1 -> veut que la 2e équipe gagne
 *   node scripts/pick-seed.mjs --no-balance -> garde les « boost » actuels de battle.config.js
 *
 * Équilibrage : par défaut, le script règle d'abord le « boost » (PV et dégâts) de l'équipe
 * la plus faible pour que chaque camp gagne environ 1 combat sur 2. Sans ça, une compo avec
 * plus de tanks ou de contrôles gagne presque toujours et la vidéo n'a aucun suspense.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

await import(path.join(root, "src/roster.js"));
await import(path.join(root, "src/sim.js"));
await import(path.join(root, "battle.config.js"));
const LOL = globalThis.LOL;
const BATTLE = globalThis.BATTLE;

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf("--" + name);
  return i >= 0 ? Number(args[i + 1]) : def;
};
const tries = opt("tries", 300);
const forced = opt("seed", null);
const wantWinner = opt("winner", null);
const minLen = opt("min", 40);
const maxLen = opt("max", 75);

function score(res) {
  const survivors = res.units.filter((u) => u.alive && u.team === res.winner);
  const champs = survivors.filter((u) => u.kind === "champ");
  const len = res.timing.total;
  let s = 0;
  if (len < minLen || len > maxLen) s -= 100 + Math.abs(len - (minLen + maxLen) / 2);
  if (wantWinner != null && res.winner !== wantWinner) s -= 1000;
  if (champs.length === 0) s -= 30; // gagner avec seulement des sbires, c'est moins drôle
  s -= Math.abs(survivors.length - 1.5) * 8; // fin à 1-2 survivants = suspense
  s -= Math.max(0, champs.length - 2) * 6;
  const last = champs[0];
  if (champs.length === 1 && last.hp / last.maxHp < 0.35) s += 12; // survivant à l'agonie
  s += Math.min(res.leadChanges, 6) * 4; // l'avantage change de camp
  if (res.lastVictim >= 0 && res.units[res.lastVictim].kind === "champ") s += 25; // le coup final tombe sur un champion
  const mvp = res.units.reduce((a, b) => (b.champKills > a.champKills ? b : a));
  s += Math.min(mvp.champKills, 6) * 1.5;
  return s;
}

function describe(seed, res) {
  const survivors = res.units.filter((u) => u.alive && u.team === res.winner);
  const mvp = res.units.filter((u) => u.kind === "champ").reduce((a, b) => (b.kills > a.kills ? b : a));
  return `graine ${seed} | gagnant ${BATTLE.teams[res.winner].name} | ${res.timing.total}s | ` +
    `survivants: ${survivors.map((u) => `${u.name} ${Math.round((100 * u.hp) / u.maxHp)}%`).join(", ")} | ` +
    `changements d'avantage: ${res.leadChanges} | MVP ${mvp.name} (${mvp.kills} kills, ${mvp.champKills} champions)`;
}

const teams = BATTLE.teams.map((t) => ({ ...t, boost: t.boost || 1 }));
if (!args.includes("--no-balance") && forced == null) {
  // cherche r tel que l'équipe 1 gagne ~50 % des combats ; r > 1 renforce l'équipe 1, r < 1 l'équipe 0
  const N = 30;
  const rate = (r) => {
    teams[0].boost = r < 1 ? Math.round((1 / r) * 1000) / 1000 : 1;
    teams[1].boost = r >= 1 ? Math.round(r * 1000) / 1000 : 1;
    let w = 0;
    for (let s = 1000; s < 1000 + N; s++) w += LOL.simulate({ ...BATTLE, teams, seed: s }, LOL).winner;
    return w / N;
  };
  let lo = 0.6, hi = 1.6;
  for (let k = 0; k < 9; k++) {
    const mid = Math.sqrt(lo * hi);
    if (rate(mid) < 0.5) lo = mid; else hi = mid;
  }
  const r = Math.sqrt(lo * hi);
  rate(r);
  console.log(`Équilibrage : boost ${BATTLE.teams[0].name} = ${teams[0].boost}, ${BATTLE.teams[1].name} = ${teams[1].boost}`);
}
BATTLE.teams = teams;

let best = null;
const seeds = forced != null ? [forced] : Array.from({ length: tries }, (_, i) => i + 1);
for (const seed of seeds) {
  const res = LOL.simulate({ ...BATTLE, seed }, LOL);
  const sc = score(res);
  if (!best || sc > best.sc) best = { seed, sc, res };
}
console.log("Meilleure : " + describe(best.seed, best.res));

// écrit la graine dans battle.config.js
const cfgPath = path.join(root, "battle.config.js");
let cfg = fs.readFileSync(cfgPath, "utf8").replace(/seed:\s*\d+/, `seed: ${best.seed}`);
let bi = 0;
cfg = cfg.replace(/boost:\s*[\d.]+/g, () => `boost: ${teams[bi++].boost}`);
fs.writeFileSync(cfgPath, cfg);

// met à jour la durée dans index.html (root + clips)
const htmlPath = path.join(root, "index.html");
const dur = best.res.timing.total;
let html = fs.readFileSync(htmlPath, "utf8");
html = html.replace(/data-duration="[\d.]+"/g, `data-duration="${dur}"`);
fs.writeFileSync(htmlPath, html);
console.log(`battle.config.js -> seed: ${best.seed}   index.html -> data-duration="${dur}"`);
