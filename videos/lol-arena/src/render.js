/*
 * Rendu canvas de la bataille. draw(v) dessine l'image au temps vidéo v (secondes).
 * Tout est une fonction pure du temps : aucune horloge, aucun hasard non seedé.
 */
(function (root) {
  const LOL = root.LOL;
  const W = 1080, H = 1920;
  let ARENA = { x: 40, y: 410, w: 1000, h: 1460 };
  const DISPLAY = "Cinzel", UI = "Rubik";

  // ------------------------------------------------------------------ utilitaires couleur
  function hexToRgb(h) {
    h = h.replace("#", "");
    if (h.length === 3) h = h.split("").map((c) => c + c).join("");
    const n = parseInt(h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function mix(hex, other, k) {
    const a = hexToRgb(hex), b = hexToRgb(other);
    return "rgb(" + a.map((v, i) => Math.round(v + (b[i] - v) * k)).join(",") + ")";
  }
  function rgba(hex, a) { const c = hexToRgb(hex); return `rgba(${c[0]},${c[1]},${c[2]},${a})`; }
  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const easeOut = (x) => 1 - Math.pow(1 - clamp01(x), 3);
  const easeBack = (x) => { x = clamp01(x); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  function hash(n) { let x = Math.imul(n ^ 0x9e3779b9, 0x85ebca6b); x ^= x >>> 13; x = Math.imul(x, 0xc2b2ae35); x ^= x >>> 16; return (x >>> 0) / 4294967296; }

  function createRenderer(canvas, res, battle, icons) {
    const ctx = canvas.getContext("2d");
    const teams = battle.teams;
    const DIRT = battle.arena === "dirt"; // arène en terre battue entourée d'herbe
    const BOSS = battle.hud === "boss"; // barres de vie des plus forts au lieu du tableau de score
    ARENA = DIRT ? { x: 40, y: 380, w: 1000, h: 1460 } : { x: 40, y: 410, w: 1000, h: 1460 };
    const RAINBOW = ["#ff6b6b", "#ffb347", "#ffe66b", "#7dff8a", "#5ad1ff", "#c38bff"];
    const U = res.units.length;
    const S = res.stride;
    const champs = res.units.filter((u) => u.kind === "champ");
    const maxHpTeam = [0, 0];
    res.units.forEach((u) => (maxHpTeam[u.team] += u.maxHp));
    const evT = res.events.map((e) => e.t);
    const T = res.timing;

    // ---------------------------------------------------------------- sprites pré-rendus
    function makeCanvas(w, h) { const c = document.createElement("canvas"); c.width = w; c.height = h; return c; }

    const TOKEN = 128; // résolution des jetons de champion
    const tokens = {}; // key -> { color, grey }
    champs.forEach((u) => {
      if (tokens[u.key]) return;
      const mk = (grey) => {
        const c = makeCanvas(TOKEN, TOKEN), g = c.getContext("2d");
        const r = TOKEN / 2;
        g.save();
        g.beginPath(); g.arc(r, r, r, 0, Math.PI * 2); g.clip();
        const img = icons[u.key];
        if (img) {
          const s = Math.max(TOKEN / img.width, TOKEN / img.height) * 1.12; // recadre la bordure des icônes
          g.drawImage(img, r - (img.width * s) / 2, r - (img.height * s) / 2, img.width * s, img.height * s);
        } else {
          const gr = g.createRadialGradient(r * 0.65, r * 0.55, r * 0.1, r, r, r);
          gr.addColorStop(0, mix(u.color, "#ffffff", 0.45));
          gr.addColorStop(0.55, u.color);
          gr.addColorStop(1, mix(u.color, "#000000", 0.6));
          g.fillStyle = gr; g.fillRect(0, 0, TOKEN, TOKEN);
          // motif : chevrons discrets
          g.strokeStyle = "rgba(255,255,255,0.10)"; g.lineWidth = 6;
          for (let k = -2; k < 4; k++) { g.beginPath(); g.moveTo(-10, r + k * 28); g.lineTo(r, r + k * 28 - 22); g.lineTo(TOKEN + 10, r + k * 28); g.stroke(); }
          const ini = initials(u.name);
          g.font = `900 ${ini.length > 1 ? 54 : 66}px ${DISPLAY}`;
          g.textAlign = "center"; g.textBaseline = "middle";
          g.lineWidth = 7; g.strokeStyle = "rgba(0,0,0,0.55)"; g.strokeText(ini, r, r + 4);
          g.fillStyle = "#fff"; g.fillText(ini, r, r + 4);
        }
        g.restore();
        if (grey) {
          const d = g.getImageData(0, 0, TOKEN, TOKEN);
          for (let i = 0; i < d.data.length; i += 4) { const l = (d.data[i] * 0.3 + d.data[i + 1] * 0.59 + d.data[i + 2] * 0.11) * 0.55; d.data[i] = d.data[i + 1] = d.data[i + 2] = l; }
          g.putImageData(d, 0, 0);
        }
        return c;
      };
      tokens[u.key] = { color: mk(false), grey: mk(true) };
    });
    function initials(name) {
      const special = { "Jarvan IV": "J4", "Xin Zhao": "XZ", "Lee Sin": "LS", "LeBlanc": "LB", "Mordekaiser": "Mo", "Cassiopeia": "Ca" };
      return special[name] || name.slice(0, 2);
    }

    // sbires : un sprite par équipe et par type
    const minionSprites = teams.map((tm) => {
      const out = {};
      ["melee", "caster", "siege"].forEach((type) => {
        const c = makeCanvas(64, 64), g = c.getContext("2d");
        const base = tm.color, dark = mix(tm.color, "#000000", 0.55), light = mix(tm.color, "#ffffff", 0.5);
        g.translate(32, 32);
        g.lineWidth = 5; g.strokeStyle = dark;
        const gr = g.createLinearGradient(0, -28, 0, 28); gr.addColorStop(0, light); gr.addColorStop(1, base);
        g.fillStyle = gr;
        g.beginPath();
        if (type === "melee") g.arc(0, 0, 26, 0, Math.PI * 2);
        else if (type === "caster") { g.moveTo(0, -29); g.lineTo(27, 0); g.lineTo(0, 29); g.lineTo(-27, 0); g.closePath(); }
        else { roundRect(g, -27, -27, 54, 54, 12); }
        g.fill(); g.stroke();
        // petit détail central
        g.fillStyle = dark;
        g.beginPath();
        if (type === "melee") { g.moveTo(-9, 8); g.lineTo(9, -10); g.lineTo(12, -7); g.lineTo(-6, 11); g.closePath(); }
        else if (type === "caster") g.arc(0, 0, 8, 0, Math.PI * 2);
        else { g.arc(0, 0, 11, 0, Math.PI * 2); }
        g.fill();
        out[type] = c;
      });
      return out;
    });

    function roundRect(g, x, y, w, h, r) {
      g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
      g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
    }

    // sol de l'arène (2x pour rester net quand la caméra zoome)
    const FS = 2;
    const MG = res.world.margin || 0;
    const floor = makeCanvas((res.world.w + MG * 2) * FS, (res.world.h + MG * 2) * FS);
    (function paintFloor() {
      const g = floor.getContext("2d");
      const w = res.world.w, h = res.world.h;
      g.scale(FS, FS);
      if (DIRT) { paintDirt(g, w, h); return; }
      // décor extérieur : roche sombre autour de l'arène
      g.fillStyle = "#0d0e13"; g.fillRect(0, 0, w + MG * 2, h + MG * 2);
      for (let k = 0; k < 1400; k++) {
        const x = hash(k * 5 + 11) * (w + MG * 2), y = hash(k * 5 + 12) * (h + MG * 2), r = 4 + hash(k * 5 + 13) * 22;
        g.fillStyle = `rgba(255,255,255,${0.015 + hash(k * 5 + 14) * 0.025})`;
        g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
      }
      g.translate(MG, MG);
      g.shadowColor = "rgba(0,0,0,0.8)"; g.shadowBlur = 40; g.fillStyle = "#000"; g.fillRect(0, 0, w, h); g.shadowBlur = 0;
      const base = g.createLinearGradient(0, 0, 0, h);
      base.addColorStop(0, "#1b2233"); base.addColorStop(0.5, "#1d1b22"); base.addColorStop(1, "#2a1a1d");
      g.fillStyle = base; g.fillRect(0, 0, w, h);
      // lueurs des deux camps
      const glow = (y, col) => { const r = g.createRadialGradient(w / 2, y, 40, w / 2, y, 760); r.addColorStop(0, rgba(col, 0.22)); r.addColorStop(1, rgba(col, 0)); g.fillStyle = r; g.fillRect(0, 0, w, h); };
      glow(0, teams[0].color); glow(h, teams[1].color);
      // dalles hexagonales
      const R = 42, hx = R * Math.sqrt(3);
      g.lineWidth = 1.5;
      for (let row = -1; row * R * 1.5 < h + R; row++) {
        for (let col = -1; col * hx < w + hx; col++) {
          const cx = col * hx + (row % 2 ? hx / 2 : 0), cy = row * R * 1.5;
          const n = hash(row * 977 + col * 131);
          g.beginPath();
          for (let k = 0; k < 6; k++) { const a = Math.PI / 6 + (k * Math.PI) / 3; g.lineTo(cx + Math.cos(a) * (R - 2), cy + Math.sin(a) * (R - 2)); }
          g.closePath();
          g.fillStyle = `rgba(255,255,255,${0.012 + n * 0.03})`; g.fill();
          g.strokeStyle = "rgba(0,0,0,0.35)"; g.stroke();
        }
      }
      // fissures / gravillons
      for (let k = 0; k < 900; k++) {
        const x = hash(k * 3 + 1) * w, y = hash(k * 3 + 2) * h, s = 1 + hash(k * 3 + 3) * 2.5;
        g.fillStyle = `rgba(255,255,255,${0.03 + hash(k) * 0.05})`; g.fillRect(x, y, s, s);
      }
      // emblème central
      g.save(); g.translate(w / 2, h / 2);
      g.strokeStyle = "rgba(243,210,122,0.22)"; g.lineWidth = 4;
      [170, 150].forEach((r) => { g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.stroke(); });
      g.lineWidth = 3;
      g.beginPath(); for (let k = 0; k <= 6; k++) { const a = (k * Math.PI) / 3; g.lineTo(Math.cos(a) * 128, Math.sin(a) * 128); } g.stroke();
      g.beginPath(); for (let k = 0; k <= 6; k++) { const a = Math.PI / 6 + (k * Math.PI) / 3; g.lineTo(Math.cos(a) * 128, Math.sin(a) * 128); } g.stroke();
      for (let k = 0; k < 24; k++) { const a = (k * Math.PI) / 12; g.beginPath(); g.moveTo(Math.cos(a) * 152, Math.sin(a) * 152); g.lineTo(Math.cos(a) * 168, Math.sin(a) * 168); g.stroke(); }
      g.restore();
      // ligne médiane
      g.setLineDash([18, 16]); g.strokeStyle = "rgba(243,210,122,0.16)"; g.lineWidth = 3;
      g.beginPath(); g.moveTo(0, h / 2); g.lineTo(w / 2 - 175, h / 2); g.moveTo(w / 2 + 175, h / 2); g.lineTo(w, h / 2); g.stroke();
      g.setLineDash([]);
      // bordure
      g.lineWidth = 14; g.strokeStyle = "#2c2a2f"; g.strokeRect(7, 7, w - 14, h - 14);
      g.lineWidth = 3; g.strokeStyle = "rgba(243,210,122,0.55)"; g.strokeRect(15, 15, w - 30, h - 30);
    })();

    function paintDirt(g, w, h) {
      const TW = w + MG * 2, TH = h + MG * 2;
      // herbe
      g.fillStyle = "#4e9a36"; g.fillRect(0, 0, TW, TH);
      for (let k = 0; k < 9000; k++) {
        const x = hash(k * 7 + 1) * TW, y = hash(k * 7 + 2) * TH, n = hash(k * 7 + 3);
        g.fillStyle = n < 0.45 ? "#3f8a2c" : n < 0.85 ? "#5fae43" : "#79c45a";
        g.fillRect(x, y, 3, 6 + n * 4);
      }
      for (let k = 0; k < 160; k++) {
        const x = hash(k * 11 + 5) * TW, y = hash(k * 11 + 6) * TH;
        g.fillStyle = hash(k) < 0.5 ? "#fff6c8" : "#ffd84a";
        g.beginPath(); g.arc(x, y, 3, 0, Math.PI * 2); g.fill();
      }
      g.translate(MG, MG);
      // rebord de terre (falaise)
      g.fillStyle = "rgba(0,0,0,0.25)"; g.beginPath(); roundRect(g, -14, -6, w + 28, h + 30, 40); g.fill();
      g.fillStyle = "#6e4a2a"; g.beginPath(); roundRect(g, -16, -16, w + 32, h + 32, 40); g.fill();
      g.fillStyle = "#8d6238"; g.beginPath(); roundRect(g, -10, -10, w + 20, h + 20, 34); g.fill();
      // terre battue
      g.fillStyle = "#b9895a"; g.beginPath(); roundRect(g, 0, 0, w, h, 28); g.fill();
      g.save(); g.beginPath(); roundRect(g, 0, 0, w, h, 28); g.clip();
      for (let k = 0; k < 900; k++) {
        const x = hash(k * 5 + 21) * w, y = hash(k * 5 + 22) * h, r = 10 + hash(k * 5 + 23) * 34;
        g.fillStyle = hash(k * 5 + 24) < 0.55 ? "rgba(120,82,48,0.10)" : "rgba(220,178,126,0.10)";
        g.beginPath(); g.ellipse(x, y, r, r * 0.6, hash(k) * 3, 0, Math.PI * 2); g.fill();
      }
      // petites traces en grille (motif de sol)
      for (let yy = 30; yy < h; yy += 64) for (let xx = 30 + ((yy / 64) % 2) * 32; xx < w; xx += 64) {
        g.fillStyle = "rgba(110,74,42,0.18)";
        g.beginPath(); g.ellipse(xx, yy, 7, 4, 0.4, 0, Math.PI * 2); g.fill();
        g.beginPath(); g.ellipse(xx + 9, yy + 7, 4, 3, 0.4, 0, Math.PI * 2); g.fill();
      }
      for (let k = 0; k < 1500; k++) {
        const x = hash(k * 3 + 41) * w, y = hash(k * 3 + 42) * h, r = 1 + hash(k * 3 + 43) * 2.6;
        g.fillStyle = hash(k + 99) < 0.6 ? "rgba(96,64,36,0.55)" : "rgba(236,204,160,0.55)";
        g.beginPath(); g.ellipse(x, y, r * 1.3, r, 0, 0, Math.PI * 2); g.fill();
      }
      // ombre portée du rebord
      const sh = g.createLinearGradient(0, 0, 0, 40); sh.addColorStop(0, "rgba(60,36,16,0.45)"); sh.addColorStop(1, "rgba(60,36,16,0)");
      g.fillStyle = sh; g.fillRect(0, 0, w, 40);
      g.restore();
      // pierres sur le rebord
      for (let k = 0; k < 140; k++) {
        const p = hash(k * 13 + 7);
        const per = 2 * (w + h);
        let d = p * per, x, y;
        if (d < w) { x = d; y = -8; } else if ((d -= w) < h) { x = w + 8; y = d; } else if ((d -= h) < w) { x = w - d; y = h + 8; } else { x = -8; y = h - (d - w); }
        g.fillStyle = hash(k) < 0.5 ? "#5a3c22" : "#a27448";
        g.beginPath(); g.ellipse(x, y, 5 + hash(k * 3) * 6, 4 + hash(k * 5) * 4, hash(k * 7) * 3, 0, Math.PI * 2); g.fill();
      }
    }

    // ---------------------------------------------------------------- lecture des images de simulation
    const nF = res.frames.length;
    function sample(s) {
      const f = Math.max(0, Math.min(nF - 1, s * res.fps));
      const i0 = Math.floor(f), i1 = Math.min(nF - 1, i0 + 1), k = f - i0;
      const a = res.frames[i0], b = res.frames[i1];
      const pos = new Float32Array(U * 2);
      for (let i = 0; i < U; i++) {
        const o = i * S;
        // pas d'interpolation à travers une mort / un bond terminé
        const kk = b[o + 3] & LOL.ST_ALIVE ? k : 0;
        pos[i * 2] = a[o] + (b[o] - a[o]) * kk;
        pos[i * 2 + 1] = a[o + 1] + (b[o + 1] - a[o + 1]) * kk;
      }
      const c = res.cams;
      const cam = { x: c[i0 * 3] + (c[i1 * 3] - c[i0 * 3]) * k, y: c[i0 * 3 + 1] + (c[i1 * 3 + 1] - c[i0 * 3 + 1]) * k, z: c[i0 * 3 + 2] + (c[i1 * 3 + 2] - c[i0 * 3 + 2]) * k };
      return { frame: a, pos, cam };
    }

    function lowerBound(t) {
      let lo = 0, hi = evT.length;
      while (lo < hi) { const m = (lo + hi) >> 1; if (evT[m] < t) lo = m + 1; else hi = m; }
      return lo;
    }

    // ---------------------------------------------------------------- dessin
    function draw(v) {
      const s = LOL.simTimeAt(res, v);
      const sc = Math.max(0, s);
      curS = sc;
      const smp = sample(sc);
      const { frame, pos } = smp;
      const intro = v < T.intro;

      // événements actifs
      const evs = [];
      for (let k = lowerBound(sc - 2.2); k < res.events.length && evT[k] <= sc; k++) evs.push(res.events[k]);

      // tremblement de caméra (ultimes)
      let shx = 0, shy = 0;
      evs.forEach((e) => {
        if (e.k !== "shake") return;
        const p = (sc - e.t) / 0.35;
        if (p < 0 || p > 1) return;
        const a = e.m * (1 - p) * (1 - p);
        shx += a * Math.sin(p * 47 + e.t * 13);
        shy += a * Math.cos(p * 39 + e.t * 7);
      });
      const cam = smp.cam;
      const z = cam.z;
      const toX = (wx) => ARENA.x + ARENA.w / 2 + (wx - cam.x) * z + shx;
      const toY = (wy) => ARENA.y + ARENA.h / 2 + (wy - cam.y) * z + shy;

      // fond
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      const bg = ctx.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, mix(teams[0].color, "#07080c", 0.82)); bg.addColorStop(0.5, "#07080c"); bg.addColorStop(1, mix(teams[1].color, "#07080c", 0.82));
      ctx.fillStyle = DIRT ? "#4e9a36" : bg; ctx.fillRect(0, 0, W, H);

      // arène
      ctx.save();
      if (!DIRT) { ctx.beginPath(); roundRect(ctx, ARENA.x, ARENA.y, ARENA.w, ARENA.h, 28); ctx.clip(); }
      ctx.drawImage(floor, toX(-MG), toY(-MG), (res.world.w + MG * 2) * z, (res.world.h + MG * 2) * z);

      // effets au sol
      evs.forEach((e) => { if (e.k === "ring") drawRing(e, sc, toX, toY, z); });

      // unités (triées par profondeur)
      const order = [];
      for (let i = 0; i < U; i++) if (frame[i * S + 3] & LOL.ST_ALIVE) order.push(i);
      order.sort((a, b) => pos[a * 2 + 1] - pos[b * 2 + 1]);
      const summon = intro ? clamp01((v - (T.intro - 0.75)) / 0.3) : 1; // ouverture des orbes
      order.forEach((i) => drawUnit(i, frame, pos, sc, toX, toY, z, v, summon));

      // morts
      evs.forEach((e) => { if (e.k === "death") drawDeath(e, sc, toX, toY, z); });
      // traînées de bond, projectiles, coups
      evs.forEach((e) => {
        if (e.k === "dash") drawDash(e, sc, toX, toY, z);
        else if (e.k === "proj") drawProj(e, sc, toX, toY, z);
        else if (e.k === "slash") drawSlash(e, sc, toX, toY, z);
      });
      // barres de vie et noms (après les unités pour rester lisibles)
      const showNames = !DIRT || order.length <= 40;
      if (!intro) order.forEach((i) => drawUnitHud(i, frame, pos, toX, toY, z, showNames));
      // chiffres et étiquettes de sorts
      evs.forEach((e) => {
        if (e.k === "dmg" && (!DIRT || e.big)) drawDmg(e, sc, toX, toY, z);
        else if (e.k === "heal") drawHeal(e, sc, pos, toX, toY, z);
      });
      evs.forEach((e) => { if (e.k === "label" && !e.ult) drawLabel(e, sc, frame, pos, toX, toY, z); });
      evs.forEach((e) => { if (e.k === "label" && e.ult) drawLabel(e, sc, frame, pos, toX, toY, z); });
      ctx.restore();

      // cadre de l'arène
      if (!DIRT) {
        ctx.lineWidth = 4; ctx.strokeStyle = "rgba(243,210,122,0.6)";
        ctx.beginPath(); roundRect(ctx, ARENA.x, ARENA.y, ARENA.w, ARENA.h, 28); ctx.stroke();
      }

      if (BOSS) drawBossHud(frame, v); else drawHud(frame, sc, v);
      if (!intro && !BOSS) drawKillFeed(sc);
      if (v < T.intro + 0.6) drawIntro(v);
      if (s >= T.s0 && s < T.s1 + 0.1 && v < T.outroStart) drawSlowMo(v, s);
      if (v >= T.outroStart - 0.05) drawOutro(v - T.outroStart);
    }

    function teamColor(t) { return teams[t].color; }

    function drawUnit(i, frame, pos, s, toX, toY, z, v, summon) {
      const u = res.units[i], o = i * S;
      const x = toX(pos[i * 2]), y = toY(pos[i * 2 + 1]);
      const r = u.r * z;
      const col = teamColor(u.team);
      // ombre
      ctx.fillStyle = "rgba(0,0,0,0.35)";
      ctx.beginPath(); ctx.ellipse(x, y + r * 0.85, r * 0.95, r * 0.35, 0, 0, Math.PI * 2); ctx.fill();

      if (summon < 1) {
        // intro : orbes d'invocation qui flottent puis éclatent
        const bob = Math.sin(v * 3 + i * 0.7) * 3 * z;
        const orbR = Math.max(9, u.r * 0.75) * z;
        if (summon <= 0) {
          const g = ctx.createRadialGradient(x - orbR * 0.3, y - orbR * 0.4 + bob, orbR * 0.1, x, y + bob, orbR);
          g.addColorStop(0, "#ffffff"); g.addColorStop(0.35, mix(col, "#ffffff", 0.3)); g.addColorStop(1, mix(col, "#000000", 0.4));
          ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y + bob, orbR, 0, Math.PI * 2); ctx.fill();
          ctx.strokeStyle = rgba("#ffffff", 0.6); ctx.lineWidth = 1.5; ctx.stroke();
          return;
        }
        // éclat
        ctx.fillStyle = rgba("#ffffff", 0.9 * (1 - summon));
        ctx.beginPath(); ctx.arc(x, y, orbR + r * 1.2 * summon, 0, Math.PI * 2); ctx.fill();
        const sc = easeBack(summon);
        drawBody(u, x, y, r * sc, col, frame, o, s);
        return;
      }
      drawBody(u, x, y, r, col, frame, o, s);
      // étourdi : petites étoiles
      if (frame[o + 3] & LOL.ST_STUN) {
        for (let k = 0; k < 3; k++) {
          const a = s * 6 + (k * Math.PI * 2) / 3;
          ctx.fillStyle = "#ffe066";
          ctx.beginPath(); ctx.arc(x + Math.cos(a) * r * 0.8, y - r * 1.05 + Math.sin(a) * r * 0.25, 3.2 * Math.sqrt(z), 0, Math.PI * 2); ctx.fill();
        }
      }
    }

    function drawBody(u, x, y, r, col, frame, o, s) {
      const hitAgo = s - frame[o + 4];
      if (u.kind === "champ") {
        // halo d'équipe
        ctx.fillStyle = rgba(col, 0.28);
        ctx.beginPath(); ctx.arc(x, y, r * 1.28, 0, Math.PI * 2); ctx.fill();
        ctx.drawImage(tokens[u.key].color, x - r, y - r, r * 2, r * 2);
        ctx.lineWidth = Math.max(2.5, r * 0.16); ctx.strokeStyle = col;
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
        if (frame[o + 3] & LOL.ST_DASH) { ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, r * 1.18, 0, Math.PI * 2); ctx.stroke(); }
      } else {
        const sp = minionSprites[u.team][u.key];
        ctx.drawImage(sp, x - r * 1.15, y - r * 1.15, r * 2.3, r * 2.3);
      }
      if (hitAgo >= 0 && hitAgo < 0.12) {
        ctx.fillStyle = `rgba(255,255,255,${0.75 * (1 - hitAgo / 0.12)})`;
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      }
    }

    function drawUnitHud(i, frame, pos, toX, toY, z, showNames) {
      const u = res.units[i], o = i * S;
      const hp = frame[o + 2];
      const x = toX(pos[i * 2]), y = toY(pos[i * 2 + 1]);
      const r = u.r * z;
      const col = teamColor(u.team);
      if (u.kind === "minion" && hp >= 0.999) return;
      const bw = u.kind === "champ" ? Math.max(46, r * 2.4) : r * 2.2;
      const bh = u.kind === "champ" ? Math.max(6, 5 * Math.sqrt(z)) : 4;
      const by = y - r - (u.kind === "champ" ? 12 : 7) * Math.sqrt(z);
      ctx.fillStyle = "rgba(0,0,0,0.75)"; ctx.fillRect(x - bw / 2 - 1.5, by - 1.5, bw + 3, bh + 3);
      ctx.fillStyle = hp < 0.3 ? "#ff5a4f" : u.kind === "champ" ? mix(col, "#ffffff", 0.15) : col;
      ctx.fillRect(x - bw / 2, by, bw * hp, bh);
      if (u.kind === "champ" && showNames) {
        const fs = Math.round(15 * Math.sqrt(z));
        ctx.font = `700 ${fs}px ${UI}`;
        ctx.textAlign = "center"; ctx.textBaseline = "bottom";
        ctx.lineWidth = 4; ctx.strokeStyle = "rgba(0,0,0,0.85)"; ctx.lineJoin = "round";
        ctx.strokeText(u.name, x, by - 3);
        ctx.fillStyle = "#ffffff"; ctx.fillText(u.name, x, by - 3);
      }
    }

    function unitXY(i, frame, pos) { return [pos[i * 2], pos[i * 2 + 1], frame[i * S + 3] & LOL.ST_ALIVE]; }

    function drawRing(e, s, toX, toY, z) {
      const dur = e.small ? 0.28 : e.ult ? 0.75 : 0.5;
      const p = (s - e.t) / dur;
      if (p < 0 || p > 1) return;
      const x = toX(e.x), y = toY(e.y);
      const col = e.heal ? "#5dff9b" : e.stun ? "#ffe066" : e.color || teamColor(e.team);
      const rr = e.r * z * (0.35 + 0.65 * easeOut(p));
      ctx.fillStyle = rgba(col, 0.28 * (1 - p));
      ctx.beginPath(); ctx.arc(x, y, rr, 0, Math.PI * 2); ctx.fill();
      ctx.lineWidth = (e.ult ? 6 : 3.5) * (1 - p) + 1;
      ctx.strokeStyle = rgba(col, 0.9 * (1 - p));
      ctx.stroke();
      if (e.ult) {
        ctx.strokeStyle = `rgba(255,255,255,${0.7 * (1 - p)})`; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(x, y, rr * 0.7, 0, Math.PI * 2); ctx.stroke();
      }
    }

    function drawProj(e, s, toX, toY, z) {
      if (s < e.t || s > e.t1) return;
      const p = (s - e.t) / (e.t1 - e.t);
      const wx = e.x0 + (e.x1 - e.x0) * p, wy = e.y0 + (e.y1 - e.y0) * p;
      const x = toX(wx), y = toY(wy);
      const ang = Math.atan2(e.y1 - e.y0, e.x1 - e.x0);
      const col = e.color || (e.siege ? "#ffb347" : teamColor(e.team));
      const size = (e.big ? 9 : e.minion ? (e.siege ? 6 : 3.5) : 5.5) * Math.sqrt(z);
      const tail = (e.big ? 46 : e.minion ? 14 : 26) * z;
      const g = ctx.createLinearGradient(x, y, x - Math.cos(ang) * tail, y - Math.sin(ang) * tail);
      g.addColorStop(0, rgba(col, 0.9)); g.addColorStop(1, rgba(col, 0));
      ctx.strokeStyle = g; ctx.lineWidth = size * 1.4; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - Math.cos(ang) * tail, y - Math.sin(ang) * tail); ctx.stroke();
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, size, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(x, y, size * 0.45, 0, Math.PI * 2); ctx.fill();
    }

    function drawSlash(e, s, toX, toY, z) {
      const dur = e.big ? 0.3 : 0.18;
      const p = (s - e.t) / dur;
      if (p < 0 || p > 1) return;
      const x = toX(e.x), y = toY(e.y);
      const r = (e.big ? 34 : 20) * z;
      const a0 = hash(Math.round(e.t * 1000)) * Math.PI * 2;
      ctx.strokeStyle = e.big ? `rgba(255,240,200,${1 - p})` : `rgba(255,255,255,${0.85 * (1 - p)})`;
      ctx.lineWidth = (e.big ? 5 : 3) * (1 - p) + 1;
      ctx.beginPath(); ctx.arc(x, y, r * (0.6 + 0.4 * p), a0, a0 + Math.PI * 0.8); ctx.stroke();
      if (e.big) { ctx.beginPath(); ctx.arc(x, y, r * (0.4 + 0.4 * p), a0 + Math.PI, a0 + Math.PI * 1.7); ctx.stroke(); }
    }

    function drawDash(e, s, toX, toY, z) {
      const p = (s - e.t0) / 0.45;
      if (p < 0 || p > 1) return;
      const k = clamp01((s - e.t0) / (e.t1 - e.t0));
      const x0 = toX(e.x0), y0 = toY(e.y0);
      const x1 = toX(e.x0 + (e.x1 - e.x0) * k), y1 = toY(e.y0 + (e.y1 - e.y0) * k);
      ctx.lineCap = "round";
      ctx.strokeStyle = rgba(e.color || teamColor(e.team), 0.55 * (1 - p)); ctx.lineWidth = 22 * z * (1 - p * 0.5);
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
      ctx.strokeStyle = `rgba(255,255,255,${0.7 * (1 - p)})`; ctx.lineWidth = 4 * z;
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    }

    function drawDeath(e, s, toX, toY, z) {
      const dur = e.champ ? 0.9 : 0.55;
      const p = (s - e.t) / dur;
      if (p < 0 || p > 1) return;
      const x = toX(e.x), y = toY(e.y);
      const col = teamColor(e.team);
      const u = res.units[e.u];
      if (e.champ) {
        // le jeton s'efface en gris en rétrécissant
        const r = u.r * z * (1 - 0.5 * p);
        ctx.globalAlpha = 1 - p;
        ctx.drawImage(tokens[u.key].grey, x - r, y - r, r * 2, r * 2);
        ctx.globalAlpha = 1;
        ctx.strokeStyle = `rgba(255,255,255,${1 - p})`; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(x, y, u.r * z * (1 + 1.6 * easeOut(p)), 0, Math.PI * 2); ctx.stroke();
      }
      const n = e.champ ? 12 : 6;
      for (let k = 0; k < n; k++) {
        const h1 = hash(e.u * 31 + k * 7), h2 = hash(e.u * 17 + k * 13);
        const a = h1 * Math.PI * 2, d = (20 + h2 * (e.champ ? 70 : 34)) * easeOut(p) * z;
        ctx.fillStyle = k % 3 === 0 ? `rgba(255,255,255,${1 - p})` : rgba(col, 1 - p);
        const sz = (e.champ ? 5 : 3) * (1 - p) * Math.sqrt(z) + 1;
        ctx.fillRect(x + Math.cos(a) * d - sz / 2, y + Math.sin(a) * d - sz / 2, sz, sz);
      }
    }

    function outlinedText(text, x, y, font, fill, stroke, lw) {
      ctx.font = font; ctx.lineJoin = "round";
      ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.strokeText(text, x, y);
      ctx.fillStyle = fill; ctx.fillText(text, x, y);
    }

    function drawDmg(e, s, toX, toY, z) {
      const p = (s - e.t) / 0.8;
      if (p < 0 || p > 1) return;
      const x = toX(e.x) + (hash(Math.round(e.t * 997) + e.v) - 0.5) * 30, y = toY(e.y) - 10 - 40 * easeOut(p);
      ctx.globalAlpha = 1 - p * p;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      const fs = (e.big ? 30 : 20) * (p < 0.15 ? 0.7 + 2 * p : 1);
      outlinedText(String(e.v), x, y, `900 ${Math.round(fs)}px ${UI}`, e.big ? "#ffd54a" : "#ffffff", "rgba(0,0,0,0.9)", 5);
      ctx.globalAlpha = 1;
    }

    function drawHeal(e, s, pos, toX, toY, z) {
      const p = (s - e.t) / 0.9;
      if (p < 0 || p > 1) return;
      const x = toX(pos[e.u * 2]), y = toY(pos[e.u * 2 + 1]) - 30 - 40 * easeOut(p);
      ctx.globalAlpha = 1 - p * p;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      outlinedText("+" + e.v, x, y, `900 22px ${UI}`, "#5dff9b", "rgba(0,0,0,0.9)", 5);
      ctx.globalAlpha = 1;
    }

    function drawLabel(e, s, frame, pos, toX, toY, z) {
      const dur = e.ult ? 1.7 : 1.15;
      const p = (s - e.t) / dur;
      if (p < 0 || p > 1) return;
      const u = res.units[e.u];
      const [wx, wy, alive] = unitXY(e.u, frame, pos);
      const bx = alive ? wx : e.x, byw = alive ? wy - u.r : e.y;
      const x = toX(bx);
      const col = teamColor(e.team);
      const fadeIn = clamp01(p / 0.12), fadeOut = 1 - clamp01((p - 0.75) / 0.25);
      const a = Math.min(fadeIn, fadeOut);
      if (!e.ult) {
        const y = toY(byw) - 42 * Math.sqrt(z) - 22 * easeOut(p);
        const text = e.text.toUpperCase();
        ctx.font = `800 ${DIRT ? 15 : 17}px ${UI}`;
        const tw = ctx.measureText(text).width;
        const pw = tw + 18, ph = DIRT ? 23 : 26;
        const cx = Math.max(ARENA.x + pw / 2 + 6, Math.min(ARENA.x + ARENA.w - pw / 2 - 6, x));
        ctx.globalAlpha = a;
        ctx.fillStyle = DIRT ? mix(u.color || col, "#000000", 0.25) : "rgba(8,9,14,0.88)";
        ctx.beginPath(); roundRect(ctx, cx - pw / 2, y - ph / 2, pw, ph, DIRT ? 5 : 7); ctx.fill();
        ctx.strokeStyle = DIRT ? "rgba(255,255,255,0.75)" : col; ctx.lineWidth = 2; ctx.stroke();
        ctx.fillStyle = "#ffffff"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText(text, cx, y + 1);
        ctx.globalAlpha = 1;
        return;
      }
      // ULTIME : grand titre doré + portrait
      const y = toY(byw) - 70 * Math.sqrt(z) - 30 * easeOut(p);
      const pop = easeBack(p / 0.2);
      const text = e.text.toUpperCase();
      const fs = 30;
      ctx.font = `900 ${fs}px ${DISPLAY}`;
      const tw = ctx.measureText(text).width;
      const pr = 26;
      const total = pr * 2 + 12 + tw;
      const cx = Math.max(ARENA.x + total / 2 + 8, Math.min(ARENA.x + ARENA.w - total / 2 - 8, x));
      ctx.save();
      ctx.globalAlpha = a;
      ctx.translate(cx, y); ctx.scale(pop, pop);
      const left = -total / 2;
      // portrait
      ctx.fillStyle = col; ctx.beginPath(); roundRect(ctx, left - 4, -pr - 4, pr * 2 + 8, pr * 2 + 8, 10); ctx.fill();
      ctx.drawImage(tokens[u.key].color, left, -pr, pr * 2, pr * 2);
      // texte
      ctx.textAlign = "left"; ctx.textBaseline = "middle";
      const g = ctx.createLinearGradient(0, -fs / 2, 0, fs / 2);
      g.addColorStop(0, "#fff6d6"); g.addColorStop(0.5, "#f3d27a"); g.addColorStop(1, "#c08a2e");
      ctx.shadowColor = rgba(col, 0.9); ctx.shadowBlur = 18;
      ctx.lineWidth = 7; ctx.strokeStyle = "rgba(10,8,6,0.95)"; ctx.lineJoin = "round";
      ctx.strokeText(text, left + pr * 2 + 12, 2);
      ctx.shadowBlur = 0;
      ctx.fillStyle = g; ctx.fillText(text, left + pr * 2 + 12, 2);
      ctx.restore();
    }

    // ---------------------------------------------------------------- interface
    function drawHud(frame, s, v) {
      const alive = [{ c: 0, m: 0, hp: 0 }, { c: 0, m: 0, hp: 0 }];
      for (let i = 0; i < U; i++) {
        const u = res.units[i], o = i * S;
        if (!(frame[o + 3] & LOL.ST_ALIVE)) continue;
        alive[u.team][u.kind === "champ" ? "c" : "m"]++;
        alive[u.team].hp += frame[o + 2] * u.maxHp;
      }
      const nChamp = [0, 1].map((t) => champs.filter((u) => u.team === t).length);
      const nMin = [0, 1].map((t) => res.units.filter((u) => u.team === t && u.kind === "minion").length);
      const enter = easeOut(v / 0.6);
      ctx.save();
      ctx.globalAlpha = enter;
      ctx.translate(0, (1 - enter) * -40);

      // panneau
      ctx.fillStyle = "rgba(6,7,11,0.82)";
      ctx.beginPath(); roundRect(ctx, 30, 140, W - 60, 255, 24); ctx.fill();
      ctx.strokeStyle = "rgba(243,210,122,0.35)"; ctx.lineWidth = 2; ctx.stroke();

      [0, 1].forEach((t) => {
        const right = t === 1;
        const x = right ? W - 62 : 62;
        ctx.textAlign = right ? "right" : "left"; ctx.textBaseline = "alphabetic";
        ctx.shadowColor = rgba(teams[t].color, 0.8); ctx.shadowBlur = 16;
        ctx.font = `900 50px ${DISPLAY}`; ctx.fillStyle = teams[t].color;
        ctx.fillText(teams[t].name, x, 205);
        ctx.shadowBlur = 0;
        ctx.font = `700 22px ${UI}`; ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.fillText(`${alive[t].c}/${nChamp[t]} champions  ·  ${alive[t].m}/${nMin[t]} sbires`, x, 240);
      });
      ctx.textAlign = "center"; ctx.font = `900 34px ${DISPLAY}`; ctx.fillStyle = "#f3d27a";
      ctx.fillText("VS", W / 2, 200);

      // barre de rapport de force (PV totaux restants)
      const a = alive[0].hp / maxHpTeam[0], b = alive[1].hp / maxHpTeam[1];
      const frac = a + b > 0 ? a / (a + b) : 0.5;
      const bx = 62, bw = W - 124, by = 260, bh = 20;
      ctx.fillStyle = "rgba(255,255,255,0.08)"; ctx.beginPath(); roundRect(ctx, bx, by, bw, bh, 10); ctx.fill();
      ctx.save(); ctx.beginPath(); roundRect(ctx, bx, by, bw, bh, 10); ctx.clip();
      const g0 = ctx.createLinearGradient(bx, 0, bx + bw * frac, 0); g0.addColorStop(0, mix(teams[0].color, "#000000", 0.35)); g0.addColorStop(1, teams[0].color);
      ctx.fillStyle = g0; ctx.fillRect(bx, by, bw * frac, bh);
      const g1 = ctx.createLinearGradient(bx + bw * frac, 0, bx + bw, 0); g1.addColorStop(0, teams[1].color); g1.addColorStop(1, mix(teams[1].color, "#000000", 0.35));
      ctx.fillStyle = g1; ctx.fillRect(bx + bw * frac, by, bw * (1 - frac), bh);
      ctx.restore();
      const jx = bx + bw * frac;
      ctx.fillStyle = "#ffffff"; ctx.shadowColor = "#ffffff"; ctx.shadowBlur = 14;
      ctx.beginPath(); ctx.moveTo(jx, by - 6); ctx.lineTo(jx + 7, by + bh / 2); ctx.lineTo(jx, by + bh + 6); ctx.lineTo(jx - 7, by + bh / 2); ctx.closePath(); ctx.fill();
      ctx.shadowBlur = 0;
      ctx.font = `800 16px ${UI}`; ctx.fillStyle = "#ffffff"; ctx.textBaseline = "middle";
      ctx.textAlign = "left"; ctx.fillText(Math.round(frac * 100) + "%", bx + 10, by + bh / 2 + 1);
      ctx.textAlign = "right"; ctx.fillText(Math.round((1 - frac) * 100) + "%", bx + bw - 10, by + bh / 2 + 1);

      // portraits des champions (gris quand éliminés)
      [0, 1].forEach((t) => {
        const list = champs.filter((u) => u.team === t);
        const r = 14, step = 31;
        list.forEach((u, k) => {
          const x = t === 0 ? 62 + r + k * step : W - 62 - r - k * step;
          const y = 330;
          const isAlive = frame[u.i * S + 3] & LOL.ST_ALIVE;
          const hp = frame[u.i * S + 2];
          ctx.drawImage(isAlive ? tokens[u.key].color : tokens[u.key].grey, x - r, y - r, r * 2, r * 2);
          ctx.lineWidth = 2.5; ctx.strokeStyle = isAlive ? teams[t].color : "rgba(120,120,120,0.8)";
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
          if (isAlive) {
            ctx.fillStyle = "rgba(0,0,0,0.8)"; ctx.fillRect(x - r, y + r + 4, r * 2, 4);
            ctx.fillStyle = hp < 0.3 ? "#ff5a4f" : "#5fd16b"; ctx.fillRect(x - r, y + r + 4, r * 2 * hp, 4);
          } else {
            ctx.strokeStyle = "#ff4d4d"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(x - 7, y - 7); ctx.lineTo(x + 7, y + 7); ctx.moveTo(x + 7, y - 7); ctx.lineTo(x - 7, y + 7); ctx.stroke();
          }
        });
      });
      ctx.restore();
    }

    // Texte « bulle » multicolore (style titre de la vidéo de référence)
    function bubbleText(text, x, y, size, maxW) {
      ctx.font = `900 ${size}px ${UI}`;
      let tw = ctx.measureText(text).width;
      if (maxW && tw > maxW) { size = Math.floor((size * maxW) / tw); ctx.font = `900 ${size}px ${UI}`; tw = ctx.measureText(text).width; }
      ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.lineJoin = "round";
      let cx = x - tw / 2;
      // contour épais commun, puis chaque lettre dans sa couleur
      ctx.lineWidth = size * 0.2; ctx.strokeStyle = "#2a1838"; ctx.strokeText(text, cx, y);
      ctx.lineWidth = size * 0.07; ctx.strokeStyle = "#ffffff"; ctx.strokeText(text, cx, y);
      [...text].forEach((ch, k) => {
        const g = ctx.createLinearGradient(0, y - size / 2, 0, y + size / 2);
        const c = RAINBOW[k % RAINBOW.length];
        g.addColorStop(0, mix(c, "#ffffff", 0.45)); g.addColorStop(1, c);
        ctx.fillStyle = g; ctx.fillText(ch, cx, y);
        cx += ctx.measureText(ch).width;
      });
      ctx.textAlign = "center";
    }

    // HUD « boss » : compteurs d'équipe + barres de vie des champions les plus dangereux
    function drawBossHud(frame, v) {
      const alive = [0, 0];
      const list = [];
      for (const u of champs) {
        const o = u.i * S;
        if (!(frame[o + 3] & LOL.ST_ALIVE)) continue;
        alive[u.team]++;
        list.push(u);
      }
      const enter = easeOut((v - 0.2) / 0.5);
      if (enter <= 0) return;
      ctx.save();
      ctx.globalAlpha = enter;
      // compteurs
      ctx.textBaseline = "middle";
      [0, 1].forEach((t) => {
        const right = t === 1;
        ctx.textAlign = right ? "right" : "left";
        const x = right ? W - 50 : 50;
        outlinedText(`${right ? alive[t] + "  " : ""}${teams[t].name}${right ? "" : "  " + alive[t]}`, x, 200, `900 40px ${UI}`, teams[t].color, "#1a1020", 8);
      });
      ctx.textAlign = "center";
      outlinedText("VS", W / 2, 200, `900 34px ${UI}`, "#ffffff", "#1a1020", 7);
      // les plus dangereux encore en vie (au début : les plus costauds)
      const fs = (u) => killsAt(u) * 10000 + u.maxHp;
      list.sort((a, b) => fs(b) - fs(a));
      const top = list.slice(0, 4);
      const bar = (u, x, y, w, h, fsz) => {
        const hp = frame[u.i * S + 2];
        const col = teams[u.team].color;
        ctx.textAlign = "left";
        outlinedText(u.name.toUpperCase(), x + 4, y - fsz * 0.75, `900 ${fsz}px ${UI}`, "#ffffff", "#1a1020", 5);
        ctx.fillStyle = "rgba(20,12,24,0.85)"; ctx.fillRect(x - 3, y - 3, w + 6, h + 6);
        ctx.fillStyle = "#3a2a2a"; ctx.fillRect(x, y, w, h);
        const g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, mix(col, "#ffffff", 0.35)); g.addColorStop(1, col);
        ctx.fillStyle = hp < 0.25 ? "#ff4d4d" : g; ctx.fillRect(x, y, w * hp, h);
        ctx.textAlign = "right";
        outlinedText(Math.max(hp > 0 ? 1 : 0, Math.round(hp * 100)) + "%", x + w - 4, y + h / 2 + 1, `900 ${Math.round(h * 0.8)}px ${UI}`, "#ffffff", "#1a1020", 4);
      };
      if (top[0]) {
        const u = top[0];
        ctx.drawImage(tokens[u.key].color, 46, 246, 64, 64);
        ctx.lineWidth = 4; ctx.strokeStyle = teams[u.team].color; ctx.strokeRect(46, 246, 64, 64);
        bar(u, 128, 280, W - 128 - 50, 24, 22);
      }
      const rest = top.slice(1);
      const cw = (W - 100 - 2 * 24) / 3;
      rest.forEach((u, k) => bar(u, 50 + k * (cw + 24), 352, cw, 16, 16));
      ctx.restore();
    }
    // éliminations d'un champion jusqu'à l'image courante (pré-calculé)
    const killTimes = {};
    res.events.forEach((e) => { if (e.k === "death" && e.killer != null) (killTimes[e.killer] = killTimes[e.killer] || []).push(e.t); });
    let curS = 0;
    function killsAt(u) { const arr = killTimes[u.i]; if (!arr) return 0; let n = 0; for (const t of arr) if (t <= curS) n++; return n; }

    function drawKillFeed(s) {
      const kills = [];
      for (let k = lowerBound(s - 3.2); k < res.events.length && evT[k] <= s; k++) if (res.events[k].k === "kill") kills.push(res.events[k]);
      const show = kills.slice(-3);
      show.forEach((e, idx) => {
        const age = s - e.t;
        const a = Math.min(easeOut(age / 0.2), 1 - clamp01((age - 2.8) / 0.4));
        const A = res.units[e.a], B = res.units[e.b];
        const y = 448 + (show.length - 1 - idx) * 48;
        const x = 60 - (1 - easeOut(age / 0.25)) * 40;
        ctx.globalAlpha = a;
        ctx.font = `800 19px ${UI}`;
        const wa = ctx.measureText(A.name).width, wb = ctx.measureText(B.name).width;
        const w = 18 + 30 + 8 + wa + 34 + wb + 8 + 30 + 14;
        ctx.fillStyle = "rgba(6,7,11,0.85)";
        ctx.beginPath(); roundRect(ctx, x, y - 20, w, 40, 20); ctx.fill();
        ctx.strokeStyle = rgba(teams[A.team].color, 0.9); ctx.lineWidth = 2; ctx.stroke();
        let cx = x + 12;
        const iconA = A.kind === "champ" ? tokens[A.key].color : minionSprites[A.team][A.key];
        ctx.drawImage(iconA, cx, y - 15, 30, 30); cx += 38;
        ctx.textAlign = "left"; ctx.textBaseline = "middle";
        ctx.fillStyle = teams[A.team].color; ctx.fillText(A.name, cx, y + 1); cx += wa + 8;
        // épée
        ctx.strokeStyle = "#f3d27a"; ctx.lineWidth = 3; ctx.lineCap = "round";
        ctx.beginPath(); ctx.moveTo(cx + 2, y + 7); ctx.lineTo(cx + 16, y - 7); ctx.moveTo(cx + 3, y - 2); ctx.lineTo(cx + 8, y + 3); ctx.stroke();
        cx += 26;
        ctx.fillStyle = teams[B.team].color; ctx.fillText(B.name, cx, y + 1); cx += wb + 8;
        ctx.drawImage(tokens[B.key].grey, cx, y - 15, 30, 30);
        ctx.globalAlpha = 1;
      });
    }

    function drawIntro(v) {
      if (DIRT) return drawIntroBubble(v);
      const out = 1 - clamp01((v - (T.intro - 1.0)) / 0.35);
      if (out > 0) {
        ctx.fillStyle = `rgba(4,5,8,${0.55 * out})`;
        ctx.fillRect(0, ARENA.y, W, ARENA.h);
        const cy = ARENA.y + ARENA.h / 2;
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        const p1 = easeBack((v - 0.1) / 0.45), p2 = easeBack((v - 0.35) / 0.45), p3 = easeBack((v - 0.6) / 0.45);
        ctx.globalAlpha = out;
        const line = (text, y, size, color, p, glow) => {
          if (p <= 0) return;
          ctx.save(); ctx.translate(W / 2, y); ctx.scale(p, p);
          ctx.shadowColor = glow; ctx.shadowBlur = 30;
          outlinedText(text, 0, 0, `900 ${size}px ${DISPLAY}`, color, "rgba(0,0,0,0.9)", 10);
          ctx.restore();
        };
        line(teams[0].name, cy - 150, 120, teams[0].color, p1, teams[0].color);
        line("VS", cy - 30, 80, "#f3d27a", p2, "#f3d27a");
        line(teams[1].name, cy + 90, 120, teams[1].color, p3, teams[1].color);
        const q = clamp01((v - 1.0) / 0.3);
        if (q > 0) {
          ctx.globalAlpha = out * q;
          outlinedText(battle.question, W / 2, cy + 225, `900 56px ${UI}`, "#ffffff", "rgba(0,0,0,0.9)", 8);
          outlinedText(battle.subtitle, W / 2, cy + 290, `700 30px ${UI}`, "rgba(255,255,255,0.85)", "rgba(0,0,0,0.9)", 6);
        }
        ctx.globalAlpha = 1;
      }
      // « COMBAT ! »
      const f = (v - (T.intro - 0.7)) / 1.1;
      if (f > 0 && f < 1) {
        const a = 1 - clamp01((f - 0.6) / 0.4);
        const sc = 0.6 + easeBack(f / 0.35) * 0.4 + f * 0.15;
        ctx.save(); ctx.globalAlpha = a;
        ctx.translate(W / 2, ARENA.y + ARENA.h / 2); ctx.scale(sc, sc);
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.shadowColor = "#ffcf5a"; ctx.shadowBlur = 40;
        outlinedText("COMBAT !", 0, 0, `900 150px ${DISPLAY}`, "#fff3cf", "rgba(0,0,0,0.95)", 14);
        ctx.restore();
      }
    }

    function drawIntroBubble(v) {
      const cy = ARENA.y + ARENA.h / 2;
      const out = 1 - clamp01((v - (T.intro - 0.9)) / 0.3);
      if (out > 0) {
        ctx.save(); ctx.globalAlpha = out;
        const p = easeBack((v - 0.15) / 0.5);
        if (p > 0) { ctx.save(); ctx.translate(W / 2, cy - 40); ctx.scale(p, p); bubbleText(battle.title, 0, 0, 96, 960); ctx.restore(); }
        const q = clamp01((v - 0.8) / 0.3);
        if (q > 0) {
          ctx.globalAlpha = out * q;
          ctx.textAlign = "center"; ctx.textBaseline = "middle";
          outlinedText(battle.subtitle, W / 2, cy + 50, `800 30px ${UI}`, "#ffffff", "#2a1838", 7);
          outlinedText(battle.question, W / 2, cy + 115, `900 54px ${UI}`, "#ffe66b", "#2a1838", 9);
        }
        ctx.restore();
      }
      const f = (v - (T.intro - 0.65)) / 1.0;
      if (f > 0 && f < 1) {
        const a = 1 - clamp01((f - 0.6) / 0.4);
        const sc = 0.6 + easeBack(f / 0.35) * 0.4 + f * 0.12;
        ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, cy); ctx.scale(sc, sc);
        bubbleText("COMBAT !", 0, 0, 150);
        ctx.restore();
      }
    }

    function drawSlowMo(v, s) {
      const into = (s - T.s0) / (T.s1 - T.s0);
      const a = Math.min(clamp01(into / 0.1), 1 - clamp01((into - 0.85) / 0.15));
      ctx.save();
      // vignette et bandeau « ralenti »
      const g = ctx.createRadialGradient(W / 2, ARENA.y + ARENA.h / 2, 300, W / 2, ARENA.y + ARENA.h / 2, 1000);
      g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, `rgba(0,0,0,${0.55 * a})`);
      ctx.fillStyle = g; ctx.fillRect(0, ARENA.y, W, ARENA.h);
      ctx.globalAlpha = a;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      outlinedText("DERNIER COUP", W / 2, ARENA.y + 70, `900 44px ${DISPLAY}`, "#f3d27a", "rgba(0,0,0,0.9)", 8);
      ctx.restore();
    }

    function drawOutro(t) {
      if (t < 0) return;
      const win = res.winner, col = teams[win].color;
      const a = easeOut(t / 0.5);
      ctx.fillStyle = `rgba(4,5,8,${0.94 * a})`; ctx.fillRect(0, 0, W, H);
      ctx.textAlign = "center"; ctx.textBaseline = "middle";

      const p1 = easeBack((t - 0.1) / 0.5);
      if (p1 > 0) {
        ctx.save(); ctx.translate(W / 2, 640); ctx.scale(p1, p1);
        ctx.shadowColor = col; ctx.shadowBlur = 50;
        outlinedText("VICTOIRE", 0, 0, `900 128px ${DISPLAY}`, "#fff3cf", "rgba(0,0,0,0.95)", 12);
        ctx.shadowBlur = 30;
        outlinedText(teams[win].name, 0, 125, `900 96px ${DISPLAY}`, col, "rgba(0,0,0,0.95)", 10);
        ctx.restore();
      }
      // survivants
      const surv = res.units.filter((u) => u.alive && u.team === win);
      const sc = surv.filter((u) => u.kind === "champ").sort((a, b) => b.hp / b.maxHp - a.hp / a.maxHp).slice(0, 5);
      const sm = surv.filter((u) => u.kind === "minion").length;
      const p2 = clamp01((t - 0.7) / 0.4);
      if (p2 > 0) {
        ctx.globalAlpha = p2;
        outlinedText(sc.length === 1 && sm === 0 ? "SEUL SURVIVANT" : "SURVIVANTS", W / 2, 900, `800 30px ${UI}`, "rgba(255,255,255,0.8)", "rgba(0,0,0,0.9)", 5);
        const r = 50, step = 140;
        sc.forEach((u, k) => {
          const x = W / 2 + (k - (sc.length - 1) / 2) * step, y = 1000;
          const pp = easeBack((t - 0.75 - k * 0.08) / 0.35);
          if (pp <= 0) return;
          ctx.save(); ctx.translate(x, y); ctx.scale(pp, pp);
          ctx.fillStyle = rgba(col, 0.35); ctx.beginPath(); ctx.arc(0, 0, r * 1.25, 0, Math.PI * 2); ctx.fill();
          ctx.drawImage(tokens[u.key].color, -r, -r, r * 2, r * 2);
          ctx.lineWidth = 6; ctx.strokeStyle = col; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
          outlinedText(u.name, 0, r + 26, `800 24px ${UI}`, "#ffffff", "rgba(0,0,0,0.9)", 5);
          outlinedText(Math.max(1, Math.round((100 * u.hp) / u.maxHp)) + "% PV", 0, r + 54, `700 20px ${UI}`, u.hp / u.maxHp < 0.3 ? "#ff7a70" : "#7dff9f", "rgba(0,0,0,0.9)", 4);
          ctx.restore();
        });
        if (sm > 0) outlinedText(`+ ${sm} sbire${sm > 1 ? "s" : ""}`, W / 2, sc.length ? 1125 : 1000, `700 26px ${UI}`, "rgba(255,255,255,0.85)", "rgba(0,0,0,0.9)", 5);
        ctx.globalAlpha = 1;
      }
      // MVP
      const mvp = champs.reduce((a, b) => (b.kills > a.kills || (b.kills === a.kills && b.champKills > a.champKills) ? b : a));
      const p3 = easeBack((t - 1.4) / 0.45);
      if (p3 > 0) {
        ctx.save(); ctx.translate(W / 2, 1290); ctx.scale(p3, p3);
        const mc = teams[mvp.team].color;
        ctx.fillStyle = "rgba(10,10,16,0.92)"; ctx.beginPath(); roundRect(ctx, -400, -78, 800, 156, 26); ctx.fill();
        ctx.strokeStyle = "#f3d27a"; ctx.lineWidth = 3; ctx.stroke();
        ctx.drawImage(tokens[mvp.key].color, -380, -56, 112, 112);
        ctx.lineWidth = 5; ctx.strokeStyle = mc; ctx.beginPath(); ctx.arc(-324, 0, 56, 0, Math.PI * 2); ctx.stroke();
        ctx.textAlign = "left";
        outlinedText("MVP", -246, -36, `900 34px ${DISPLAY}`, "#f3d27a", "rgba(0,0,0,0.9)", 5);
        outlinedText(mvp.name, -246, 10, `900 44px ${UI}`, mc, "rgba(0,0,0,0.9)", 6);
        outlinedText(`${mvp.kills} éliminations dont ${mvp.champKills} champion${mvp.champKills > 1 ? "s" : ""}`, -246, 52, `700 24px ${UI}`, "rgba(255,255,255,0.85)", "rgba(0,0,0,0.9)", 4);
        ctx.restore();
      }
      // appel à commenter
      const p4 = clamp01((t - 2.1) / 0.4);
      if (p4 > 0) {
        ctx.globalAlpha = p4;
        ctx.textAlign = "center";
        wrapText(battle.outro, W / 2, 1460, 860, 50, `800 40px ${UI}`);
        ctx.globalAlpha = 1;
      }
    }

    function wrapText(text, x, y, maxW, lh, font) {
      ctx.font = font;
      const words = text.split(" ");
      const lines = [];
      let cur = "";
      words.forEach((w) => { const t = cur ? cur + " " + w : w; if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; });
      if (cur) lines.push(cur);
      lines.forEach((l, k) => outlinedText(l, x, y + k * lh, font, "#ffffff", "rgba(0,0,0,0.9)", 6));
    }

    return { draw };
  }

  LOL.createRenderer = createRenderer;
})(window);
