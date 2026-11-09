/*
 * Moteur de simulation de l'arène.
 *
 * Toute la bataille est calculée une seule fois, à l'avance, avec un générateur pseudo-aléatoire
 * à graine : même graine = même combat. Le résultat est une suite d'images (positions, vie, état
 * de chaque unité) + une liste d'événements datés (projectiles, sorts, morts...). Le rendu
 * (src/render.js) ne fait que dessiner l'instant demandé : la vidéo peut donc être lue, rembobinée
 * ou rendue image par image sans jamais changer.
 *
 * Fonctionne dans le navigateur (window.LOL.simulate) et dans Node (require("./sim.js")).
 */
(function (root) {
  const FPS = 30;
  const DT = 1 / FPS;
  const WORLD = { w: 1000, h: 1460, margin: 320 }; // margin : décor visible au-delà des murs
  const STRIDE = 5; // x, y, hpFrac, state, lastHitTime
  const ST_ALIVE = 1, ST_STUN = 2, ST_DASH = 4;

  const INTRO = 3.4; // secondes avant le début du combat
  const SLOW = 0.35; // vitesse du ralenti sur le coup final
  const OUTRO = 5.5; // durée de l'écran de victoire
  const TAIL = 1.4; // secondes de simulation conservées après le dernier coup

  const SPELL_DEFAULTS = {
    nuke: { power: 2.6, range: 230 },
    aoe: { power: 1.8, range: 230, radius: 80 },
    spin: { power: 1.8, radius: 85 },
    dash: { power: 2.0, range: 270 },
    stun: { power: 1.2, range: 240, stun: 1.2 },
    aoestun: { power: 1.3, range: 200, radius: 90, stun: 1.1 },
    heal: { power: 0.24, range: 260 },
    execute: { power: 2.8, range: 170 },
    drain: { power: 2.2, range: 200 },
  };

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function makeSpell(def, isUlt, rng) {
    const base = SPELL_DEFAULTS[def.type];
    if (!base) throw new Error("Type de sort inconnu : " + def.type);
    const s = Object.assign({}, base, def);
    s.ult = isUlt;
    if (isUlt) {
      s.power = def.power != null ? def.power : base.power * 1.5;
      if (s.radius) s.radius = def.radius != null ? def.radius : base.radius * 1.3;
      s.cd = def.cd != null ? def.cd : 17;
      s.t = 8 + rng() * 22; // premier lancer de l'ultime (étalé pour éviter un feu d'artifice illisible)
    } else {
      s.cd = def.cd != null ? def.cd : 5.2 + rng() * 1.6;
      s.t = 1 + rng() * 3.5;
    }
    return s;
  }

  function buildUnits(battle, lib, rng) {
    const units = [];
    battle.teams.forEach((team, ti) => {
      const dir = ti === 0 ? 1 : -1; // l'équipe 0 est en haut et avance vers le bas
      const frontY = ti === 0 ? 520 : WORLD.h - 520;
      const rows = [];
      const minionRow = (type, n) => { const out = []; for (let k = 0; k < n; k++) out.push({ kind: "minion", type }); return out; };
      const melee = minionRow("melee", team.minions.melee || 0);
      const back = minionRow("caster", team.minions.caster || 0).concat(minionRow("siege", team.minions.siege || 0));
      const champs = championList(team.champions, lib).map((key) => ({ kind: "champ", key }));
      const sc = battle.unitScale || 1;
      const perRow = Math.max(8, Math.floor(8 / sc));
      // Ordre des rangs depuis le front : sbires de mêlée, champions, sbires à distance.
      chunk(melee, 10).forEach((r) => rows.push({ items: r, gap: 62 * sc }));
      chunk(champs, perRow).forEach((r) => rows.push({ items: r, gap: 82 * sc }));
      chunk(back, 10).forEach((r) => rows.push({ items: r, gap: 56 * sc }));
      let y = frontY;
      rows.forEach((row) => {
        const n = row.items.length;
        const spacing = Math.min(96 * (battle.unitScale || 1), (WORLD.w - 80) / Math.max(1, n));
        row.items.forEach((it, k) => {
          const x = WORLD.w / 2 + (k - (n - 1) / 2) * spacing + (rng() - 0.5) * 8;
          const u = makeUnit(it, ti, x, y + (rng() - 0.5) * 6, lib, rng);
          u.r *= battle.unitScale || 1;
          const boost = team.boost || 1; // équilibrage (voir scripts/pick-seed.mjs)
          u.maxHp = u.hp = Math.round(u.maxHp * boost * (battle.hpScale || 1));
          u.dmg *= boost;
          units.push(u);
        });
        y -= dir * row.gap;
      });
    });
    units.forEach((u, i) => (u.i = i));
    return units;
  }

  // `champions` peut être une liste d'ids ou une période : { from: 2009, to: 2010 }
  function championList(spec, lib) {
    if (Array.isArray(spec)) return spec;
    const ids = Object.keys(lib.ROSTER).filter((id) => {
      const y = lib.ROSTER[id].year;
      return y && y >= (spec.from || 0) && y <= (spec.to || 9999);
    });
    // tri par année puis mélange déterministe dans la formation
    const r = mulberry32(ids.length * 7919);
    return ids.map((id) => [r(), id]).sort((a, b) => a[0] - b[0]).map((x) => x[1]);
  }

  function chunk(arr, n) {
    const out = [];
    for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n));
    return out;
  }

  function makeUnit(it, team, x, y, lib, rng) {
    if (it.kind === "champ") {
      const c = lib.ROSTER[it.key];
      if (!c) throw new Error("Champion inconnu dans battle.config.js : " + it.key);
      const r = lib.ROLES[c.role];
      return {
        team, kind: "champ", key: it.key, name: c.name, role: c.role, color: c.color,
        x, y, maxHp: r.hp, hp: r.hp, dmg: r.dmg, range: r.range, speed: r.speed, atkCd: r.atk,
        atkT: rng() * r.atk, r: r.radius, armor: r.armor, projectile: !!r.projectile,
        spell: makeSpell(c.spell, false, rng), ult: makeSpell(c.ult, true, rng),
        stun: 0, dash: null, alive: true, kills: 0, champKills: 0, lastHit: -99, target: -1, retarget: 0, deathT: -1,
      };
    }
    const m = lib.MINIONS[it.type];
    return {
      team, kind: "minion", key: it.type, name: m.name, role: it.type, color: null,
      x, y, maxHp: m.hp, hp: m.hp, dmg: m.dmg, range: m.range, speed: m.speed, atkCd: m.atk,
      atkT: rng() * m.atk, r: m.radius, armor: m.armor, projectile: !!m.projectile,
      spell: null, ult: null, stun: 0, dash: null, alive: true, kills: 0, champKills: 0, lastHit: -99, target: -1, retarget: 0, deathT: -1,
    };
  }

  function simulate(battle, lib, opts) {
    opts = opts || {};
    const maxTime = opts.maxTime || 110;
    const rng = mulberry32((battle.seed || 1) * 2654435761);
    const units = buildUnits(battle, lib, rng);
    const U = units.length;
    const order = units.map((u, i) => i);
    const events = [];
    const pending = []; // projectiles en vol
    const frames = [];
    const cams = [];
    let t = 0;
    let endT = -1;
    let winner = -1;
    let lead = 0, leadChanges = 0;
    const cam = { x: WORLD.w / 2, y: WORLD.h / 2, z: 1 };

    const d2 = (a, b) => (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y);
    const dist = (a, b) => Math.sqrt(d2(a, b));
    const enemiesOf = (u) => units.filter((v) => v.alive && v.team !== u.team);

    function hurt(src, tgt, amount, opts2) {
      if (!tgt.alive) return 0;
      // mort subite : passé `fury.after` secondes, les dégâts montent pour éviter les duels sans fin
      const fury = 1 + Math.max(0, t - (battle.furyAfter != null ? battle.furyAfter : 30)) * (battle.furyRate != null ? battle.furyRate : 0.07);
      let a = amount * fury * (1 - tgt.armor) * (0.88 + rng() * 0.24);
      if (src && src.kind === "minion" && tgt.kind === "champ") a *= 0.6;
      a = Math.round(a);
      tgt.hp -= a;
      tgt.lastHit = t;
      if (opts2 && opts2.show) events.push({ k: "dmg", t, x: tgt.x, y: tgt.y - tgt.r, v: a, big: !!opts2.big });
      if (tgt.hp <= 0) kill(src, tgt);
      return a;
    }

    function kill(src, tgt) {
      tgt.hp = 0;
      tgt.alive = false;
      tgt.deathT = t;
      events.push({ k: "death", t, u: tgt.i, x: tgt.x, y: tgt.y, team: tgt.team, champ: tgt.kind === "champ", killer: src ? src.i : null });
      if (src) {
        src.kills++;
        if (tgt.kind === "champ") {
          src.champKills++;
          if (src.role === "assassin" && src.spell) src.spell.t = 0; // réinitialisation sur élimination

          events.push({ k: "kill", t, a: src.i, b: tgt.i });
        }
      }
    }

    function heal(u, amount) {
      if (!u.alive) return;
      const before = u.hp;
      u.hp = Math.min(u.maxHp, u.hp + amount);
      if (u.hp - before > 4) events.push({ k: "heal", t, u: u.i, v: Math.round(u.hp - before) });
    }

    function chooseTarget(u) {
      let best = -1, bestScore = Infinity;
      for (const v of units) {
        if (!v.alive || v.team === u.team) continue;
        const dd = dist(u, v);
        let s = dd + rng() * 70;
        // les assassins traquent les champions fragiles... quand ils sont à portée de saut
        if (u.role === "assassin" && v.kind === "champ" && dd < 380 && (v.role === "mage" || v.role === "marksman" || v.role === "support")) s -= 260;
        if (u.kind === "champ" && v.kind === "champ") s -= 60;
        if (s < bestScore) { bestScore = s; best = v.i; }
      }
      u.target = best;
      u.retarget = 0.45 + rng() * 0.3;
    }

    function label(u, s) {
      events.push({ k: "label", t, u: u.i, x: u.x, y: u.y - u.r, text: s.name, ult: s.ult, team: u.team });
      if (s.ult) events.push({ k: "shake", t, m: 9 });
    }

    function areaHit(src, cx, cy, radius, power, stun, ult) {
      let n = 0;
      for (const v of units) {
        if (!v.alive || v.team === src.team) continue;
        const dd = Math.hypot(v.x - cx, v.y - cy);
        if (dd > radius + v.r) continue;
        hurt(src, v, src.dmg * power, { show: v.kind === "champ", big: ult });
        if (stun && v.alive) { v.stun = Math.max(v.stun, stun); }
        n++;
      }
      events.push({ k: "ring", t, x: cx, y: cy, r: radius, team: src.team, ult, stun: !!stun, color: src.color });
      return n;
    }

    function countEnemiesNear(u, x, y, radius) {
      let n = 0, champ = false;
      for (const v of units) {
        if (!v.alive || v.team === u.team) continue;
        if (Math.hypot(v.x - x, v.y - y) <= radius + v.r) { n++; if (v.kind === "champ") champ = true; }
      }
      return { n, champ };
    }

    function tryCast(u, s, tgt) {
      if (s.t > 0) return false;
      const dt = tgt ? dist(u, tgt) - tgt.r - u.r : Infinity;
      switch (s.type) {
        case "heal": {
          let who = null;
          if (u.role === "support") {
            let worst = 0.78;
            for (const v of units) {
              if (!v.alive || v.team !== u.team || v.kind !== "champ") continue;
              const f = v.hp / v.maxHp;
              if (f < worst && dist(u, v) < s.range) { worst = f; who = v; }
            }
          } else if (u.hp / u.maxHp < 0.6) who = u;
          if (!who) return false;
          label(u, s);
          // les soins suivent les PV de base (hpScale allonge le combat sans rendre les soigneurs immortels)
          const hs = 1 / (battle.hpScale || 1);
          heal(who, who.maxHp * hs * s.power * (s.ult ? 1.6 : 1));
          // les soins de zone d'un support soignent aussi un peu les voisins
          if (u.role === "support") for (const v of units) if (v.alive && v.team === u.team && v !== who && dist(v, who) < 140) heal(v, v.maxHp * hs * s.power * 0.4);
          events.push({ k: "ring", t, x: who.x, y: who.y, r: 70, team: u.team, heal: true, color: "#5dff9b" });
          return true;
        }
        case "spin": {
          const c = countEnemiesNear(u, u.x, u.y, s.radius);
          if (c.n < (s.ult ? 2 : 1) && !c.champ) return false;
          label(u, s);
          areaHit(u, u.x, u.y, s.radius, s.power, 0, s.ult);
          return true;
        }
        case "execute": {
          let victim = null;
          for (const v of units) {
            if (!v.alive || v.team === u.team || v.kind !== "champ") continue;
            if (v.hp / v.maxHp < 0.4 && dist(u, v) - v.r - u.r < s.range) { victim = v; break; }
          }
          if (!victim) return false;
          label(u, s);
          events.push({ k: "slash", t, x: victim.x, y: victim.y, big: true, team: u.team });
          if (victim.hp / victim.maxHp < 0.35) hurt(u, victim, victim.hp + 9999, { show: true, big: true });
          else hurt(u, victim, u.dmg * s.power, { show: true, big: true });
          return true;
        }
        default:
          break;
      }
      if (!tgt || !tgt.alive) return false;
      if (s.ult && tgt.kind !== "champ" && s.t > -4) return false; // l'ultime attend une cible champion (4 s max)
      if (dt > s.range) return false;
      if (s.type === "dash" && !s.ult) {
        // un bond n'est lancé que sur une cible isolée ou déjà bien entamée
        const crowd = countEnemiesNear(u, tgt.x, tgt.y, 150).n;
        if (crowd > 3 && tgt.hp / tgt.maxHp > 0.5) return false;
      }
      label(u, s);
      switch (s.type) {
        case "nuke":
          fire(u, tgt, u.dmg * s.power, { color: u.color, big: true, show: true, ult: s.ult });
          break;
        case "stun":
          fire(u, tgt, u.dmg * s.power, { color: u.color, big: true, show: true, stun: s.stun, ult: s.ult });
          break;
        case "drain": {
          const got = hurt(u, tgt, u.dmg * s.power, { show: true, big: s.ult });
          events.push({ k: "slash", t, x: tgt.x, y: tgt.y, big: s.ult, team: u.team });
          heal(u, got * 0.7);
          if (s.radius) areaHit(u, tgt.x, tgt.y, s.radius, s.power * 0.4, 0, s.ult);
          break;
        }
        case "aoe":
          areaHit(u, tgt.x, tgt.y, s.radius, s.power, 0, s.ult);
          break;
        case "aoestun":
          areaHit(u, tgt.x, tgt.y, s.radius, s.power, s.stun, s.ult);
          break;
        case "dash": {
          const ang = Math.atan2(tgt.y - u.y, tgt.x - u.x);
          const stop = tgt.r + u.r + 4;
          const tx = tgt.x - Math.cos(ang) * stop, ty = tgt.y - Math.sin(ang) * stop;
          u.dash = { x0: u.x, y0: u.y, x1: tx, y1: ty, t0: t, t1: t + 0.2, tgt: tgt.i, power: s.power, radius: s.radius || 0, ult: s.ult };
          events.push({ k: "dash", t0: t, t1: t + 0.2, t, x0: u.x, y0: u.y, x1: tx, y1: ty, team: u.team, color: u.color, ult: s.ult });
          break;
        }
      }
      return true;
    }

    function fire(u, tgt, amount, o) {
      if (!u.projectile && !o.big) {
        // corps à corps : dégâts immédiats
        events.push({ k: "slash", t, x: tgt.x, y: tgt.y, big: false, team: u.team });
        hurt(u, tgt, amount, { show: o.show, big: o.ult });
        if (o.stun && tgt.alive) tgt.stun = Math.max(tgt.stun, o.stun);
        return;
      }
      const d = dist(u, tgt);
      const speed = o.big ? 760 : 620;
      pending.push({ src: u.i, tgt: tgt.i, t0: t, t1: t + Math.max(0.08, d / speed), x0: u.x, y0: u.y, amount, o });
    }

    function step() {
      // 1. projectiles qui arrivent
      for (let k = pending.length - 1; k >= 0; k--) {
        const p = pending[k];
        if (t < p.t1) continue;
        pending.splice(k, 1);
        const tgt = units[p.tgt], src = units[p.src];
        events.push({ k: "proj", t: p.t0, t1: p.t1, x0: p.x0, y0: p.y0, x1: tgt.x, y1: tgt.y, team: src.team, color: p.o.color, big: !!p.o.big, minion: src.kind === "minion", siege: src.key === "siege" });
        if (!tgt.alive) continue;
        hurt(src.alive ? src : src, tgt, p.amount, { show: p.o.show, big: p.o.ult });
        if (p.o.stun && tgt.alive) tgt.stun = Math.max(tgt.stun, p.o.stun);
        if (p.o.big) events.push({ k: "ring", t, x: tgt.x, y: tgt.y, r: 34, team: src.team, ult: false, small: true, color: p.o.color });
      }

      // 2. décisions et déplacements — ordre mélangé à chaque tick, sinon l'équipe traitée
      //    en second frappe toujours la première (biais énorme dans les grandes armées)
      for (let k = U - 1; k > 0; k--) { const j = Math.floor(rng() * (k + 1)); const tmp = order[k]; order[k] = order[j]; order[j] = tmp; }
      for (const idx of order) {
        const u = units[idx];
        if (!u.alive) continue;
        if (u.spell) { u.spell.t -= DT; u.ult.t -= DT; }
        u.atkT -= DT;
        if (u.dash) {
          const d = u.dash;
          const k = Math.min(1, (t - d.t0) / (d.t1 - d.t0));
          u.x = d.x0 + (d.x1 - d.x0) * k;
          u.y = d.y0 + (d.y1 - d.y0) * k;
          if (k >= 1) {
            const tgt = units[d.tgt];
            u.dash = null;
            if (d.radius) areaHit(u, u.x, u.y, d.radius, d.power, d.ult ? 0.8 : 0, d.ult);
            else if (tgt.alive) { events.push({ k: "slash", t, x: tgt.x, y: tgt.y, big: true, team: u.team }); hurt(u, tgt, u.dmg * d.power, { show: true, big: d.ult }); }
            u.atkT = Math.min(u.atkT, 0.1);
          }
          continue;
        }
        if (u.stun > 0) { u.stun -= DT; continue; }
        u.retarget -= DT;
        let tgt = u.target >= 0 ? units[u.target] : null;
        if (!tgt || !tgt.alive || u.retarget <= 0) { chooseTarget(u); tgt = u.target >= 0 ? units[u.target] : null; }

        if (u.spell) {
          if (tryCast(u, u.ult, tgt)) { u.ult.t = u.ult.cd; u.atkT = Math.max(u.atkT, 0.25); continue; }
          if (tryCast(u, u.spell, tgt)) { u.spell.t = u.spell.cd; u.atkT = Math.max(u.atkT, 0.25); continue; }
        }
        if (!tgt) continue;
        const gap = dist(u, tgt) - u.r - tgt.r;
        if (gap > u.range) {
          const ang = Math.atan2(tgt.y - u.y, tgt.x - u.x);
          const sp = u.speed * DT;
          u.x += Math.cos(ang) * sp;
          u.y += Math.sin(ang) * sp;
        } else if (u.atkT <= 0) {
          u.atkT = u.atkCd * (0.92 + rng() * 0.16);
          fire(u, tgt, u.dmg, { color: u.kind === "champ" ? u.color : null, big: false, show: false });
        }
      }

      // 3. séparation (les unités ne se superposent pas) + bords de l'arène
      for (let a = 0; a < U; a++) {
        const ua = units[a];
        if (!ua.alive) continue;
        for (let b = a + 1; b < U; b++) {
          const ub = units[b];
          if (!ub.alive) continue;
          const dx = ub.x - ua.x, dy = ub.y - ua.y;
          const min = ua.r + ub.r + 2;
          const dd = dx * dx + dy * dy;
          if (dd >= min * min) continue;
          const d = Math.sqrt(dd) || 0.01;
          const push = (min - d) / 2;
          const nx = dd ? dx / d : 1, ny = dd ? dy / d : 0;
          const wa = ua.dash ? 0 : ub.dash ? 2 : 1, wb = ub.dash ? 0 : ua.dash ? 2 : 1;
          ua.x -= nx * push * wa; ua.y -= ny * push * wa;
          ub.x += nx * push * wb; ub.y += ny * push * wb;
        }
      }
      for (const u of units) {
        if (!u.alive) continue;
        u.x = Math.max(u.r + 6, Math.min(WORLD.w - u.r - 6, u.x));
        u.y = Math.max(u.r + 6, Math.min(WORLD.h - u.r - 6, u.y));
      }
    }

    function snapshot() {
      const f = new Float32Array(U * STRIDE);
      for (let i = 0; i < U; i++) {
        const u = units[i];
        const o = i * STRIDE;
        f[o] = u.x; f[o + 1] = u.y; f[o + 2] = Math.max(0, u.hp / u.maxHp);
        f[o + 3] = (u.alive ? ST_ALIVE : 0) | (u.stun > 0 ? ST_STUN : 0) | (u.dash ? ST_DASH : 0);
        f[o + 4] = u.lastHit;
      }
      frames.push(f);
      // caméra : cadre doucement le cœur de la mêlée (on ignore les 10 % d'unités les plus excentrées)
      const xs = [], ys = [];
      for (const u of units) if (u.alive) { xs.push(u.x); ys.push(u.y); }
      if (xs.length) {
        xs.sort((a, b) => a - b); ys.sort((a, b) => a - b);
        const q = (arr, p) => arr[Math.min(arr.length - 1, Math.max(0, Math.round(p * (arr.length - 1))))];
        const lo = xs.length > 12 ? 0.12 : 0, hi = 1 - lo;
        const x0 = q(xs, lo), x1 = q(xs, hi), y0 = q(ys, lo), y1 = q(ys, hi);
        const pad = 130;
        const bw = x1 - x0 + pad * 2, bh = y1 - y0 + pad * 2;
        const zt = Math.max(1, Math.min(2.1, Math.min(WORLD.w / bw, WORLD.h / bh)));
        const k = t < 1 ? 0 : 0.03;
        cam.z += (zt - cam.z) * k;
        cam.x += ((x0 + x1) / 2 - cam.x) * k * 1.5;
        cam.y += ((y0 + y1) / 2 - cam.y) * k * 1.5;
      }
      const hw = WORLD.w / 2 / cam.z, hh = WORLD.h / 2 / cam.z;
      const M = WORLD.margin;
      cam.x = Math.max(hw - M, Math.min(WORLD.w - hw + M, cam.x));
      cam.y = Math.max(hh - M, Math.min(WORLD.h - hh + M, cam.y));
      cams.push(cam.x, cam.y, cam.z);
    }

    snapshot();
    while (true) {
      t += DT;
      step();
      snapshot();
      const alive = [0, 0], hp = [0, 0];
      for (const u of units) if (u.alive) { alive[u.team]++; hp[u.team] += u.hp; }
      const l = Math.sign(alive[0] - alive[1]);
      if (l !== 0 && l !== lead) { if (lead !== 0) leadChanges++; lead = l; }
      if (endT < 0 && (alive[0] === 0 || alive[1] === 0 || t >= maxTime)) {
        endT = t;
        winner = alive[0] === alive[1] ? (hp[0] >= hp[1] ? 0 : 1) : alive[0] > alive[1] ? 0 : 1;
      }
      if (endT >= 0 && t >= endT + TAIL) break;
    }

    events.sort((a, b) => a.t - b.t);
    const lastDeath = events.filter((e) => e.k === "death").pop();
    const result = {
      lastVictim: lastDeath ? lastDeath.u : -1,
      fps: FPS, world: WORLD, stride: STRIDE, frames, cams, events, endT, winner, leadChanges,
      units: units.map((u) => ({
        i: u.i, team: u.team, kind: u.kind, key: u.key, name: u.name, role: u.role, color: u.color,
        r: u.r, maxHp: u.maxHp, kills: u.kills, champKills: u.champKills, alive: u.alive, hp: Math.max(0, u.hp), deathT: u.deathT,
      })),
    };
    result.timing = timing(result);
    return result;
  }

  // Correspondance temps vidéo -> temps de simulation (intro, ralenti final, écran de fin).
  function timing(res) {
    const s0 = Math.max(0, res.endT - 1.1);
    const s1 = res.endT + 0.25;
    const simEnd = res.endT + TAIL;
    const slowLen = (s1 - s0) / SLOW;
    const outroStart = INTRO + s0 + slowLen + (simEnd - s1);
    const total = Math.ceil((outroStart + OUTRO) * 10) / 10;
    return { intro: INTRO, s0, s1, slow: SLOW, slowLen, simEnd, outroStart, total };
  }

  function simTimeAt(res, v) {
    const T = res.timing;
    const u = v - T.intro;
    if (u < T.s0) return u; // négatif pendant l'intro
    if (u < T.s0 + T.slowLen) return T.s0 + (u - T.s0) * T.slow;
    return Math.min(T.simEnd, T.s1 + (u - T.s0 - T.slowLen));
  }

  const api = { simulate, simTimeAt, championList, timing, WORLD, FPS, STRIDE, ST_ALIVE, ST_STUN, ST_DASH, mulberry32 };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.LOL = Object.assign(root.LOL || {}, api);
})(typeof window !== "undefined" ? window : globalThis);
