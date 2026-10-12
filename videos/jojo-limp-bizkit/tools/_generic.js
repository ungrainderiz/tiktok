      const OFF = {{OFF}};
      const WORDS = {{WORDS}}.filter((w) => w.type === "word").map((w) => ({ t: w.text, s: w.start + OFF, e: w.end + OFF }));
      const SC = {{SCENES}};
      const TOTAL = {{TOTAL}};
      const W = (sub, after = 0) => { for (const w of WORDS) if (w.s >= after && w.t.toLowerCase().includes(sub)) return w.s; throw new Error("word " + sub); };
      function rng(seed) { return function () { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
      const tl = gsap.timeline({ paused: true });
      const S = (i) => SC[i - 1].start, E = (i) => SC[i - 1].start + SC[i - 1].dur;
      const $ = (id) => document.getElementById(id);

      // ---- ink-style characters (original drawings, manga look)
      const MAXX = `<svg viewBox="0 0 400 480" width="100%" height="100%"><g class="body">
        <path d="M10 480 C20 390 80 345 150 334 L250 334 C320 345 380 390 390 480Z" fill="#e0782c" stroke="#0b0b10" stroke-width="9"/>
        <path d="M14 470 C26 392 80 350 150 336 L172 336 L120 480Z" fill="url(#hatch)" opacity="0.3"/>
        <path d="M158 266 L156 344 L244 344 L242 266Z" fill="#d49870" stroke="#0b0b10" stroke-width="8"/>
        <path d="M158 296 L242 296 L242 272 L158 272Z" fill="url(#hatch)" opacity="0.45"/>
        <path d="M148 334 L200 400 L252 334" fill="#e9dfc6" stroke="#0b0b10" stroke-width="8"/>
        <rect x="72" y="402" width="108" height="42" fill="#f3ecdc" stroke="#0b0b10" stroke-width="6"/>
        <text x="126" y="434" text-anchor="middle" font-family="Anton" font-size="30" fill="#0b0b10">MX-036</text></g>
        <g class="head">
        <path d="M114 172 C98 168 94 208 118 224" fill="#e2ad86" stroke="#0b0b10" stroke-width="7"/><path d="M286 172 C302 168 306 208 282 224" fill="#e2ad86" stroke="#0b0b10" stroke-width="7"/>
        <path d="M118 140 C116 90 150 62 200 62 C250 62 284 90 282 140 L278 222 C272 266 242 296 200 300 C158 296 128 266 122 222Z" fill="#e2ad86" stroke="#0b0b10" stroke-width="9"/>
        <path d="M252 150 L279 150 L276 222 C270 262 246 290 214 298 C246 268 260 220 252 150Z" fill="url(#ht)" opacity="0.5"/>
        <path d="M138 246 C160 292 240 292 262 246 C244 304 156 304 138 246Z" fill="url(#ht)" opacity="0.6"/>
        <path d="M108 150 C104 60 150 22 200 22 C250 22 296 60 292 150Z" fill="#2a2a34" stroke="#0b0b10" stroke-width="9"/>
        <path d="M104 156 C140 128 260 128 296 156 L298 120 C262 96 138 96 102 120Z" fill="#3c3c4a" stroke="#0b0b10" stroke-width="8"/>
        <path d="M122 112 L122 142 M140 106 L140 136 M158 102 L158 132 M176 100 L176 130 M194 99 L194 129 M212 99 L212 129 M230 100 L230 130 M248 102 L248 132 M266 106 L266 136 M282 112 L282 142" stroke="#1a1a22" stroke-width="5"/>
        <path d="M132 176 L192 190 L190 205 L130 191Z" fill="#0b0b10"/><path d="M268 176 L208 190 L210 205 L270 191Z" fill="#0b0b10"/>
        <path d="M142 212 Q166 199 190 213 Q166 224 142 212Z" fill="#fff" stroke="#0b0b10" stroke-width="5"/><circle cx="175" cy="212" r="6" fill="#0b0b10"/>
        <path d="M258 212 Q234 199 210 213 Q234 224 258 212Z" fill="#fff" stroke="#0b0b10" stroke-width="5"/><circle cx="225" cy="212" r="6" fill="#0b0b10"/>
        <path d="M146 230 L184 232 M216 232 L254 230 M150 238 L176 240 M224 240 L250 238" stroke="#0b0b10" stroke-width="3"/>
        <path d="M200 216 L190 254 L211 258" fill="none" stroke="#0b0b10" stroke-width="6" stroke-linejoin="round"/>
        <path d="M150 266 Q200 292 252 262 Q242 286 200 290 Q162 288 150 266Z" fill="#fff" stroke="#0b0b10" stroke-width="6"/>
        <path d="M174 273 L175 287 M200 277 L200 290 M226 273 L225 287" stroke="#0b0b10" stroke-width="3"/>
        <path d="M236 160 L264 244" stroke="#8a2020" stroke-width="5"/><path d="M242 184 L256 178 M248 204 L262 198 M254 224 L268 218" stroke="#8a2020" stroke-width="3"/></g></svg>`;

      const STAND = `<svg viewBox="0 0 500 800" width="100%" height="100%"><g stroke="#d8ff9a" stroke-width="6" fill="url(#gStand)" stroke-linejoin="round" stroke-linecap="round">
        <path d="M180 262 C80 240 60 140 112 88" fill="none" stroke-width="16"/><path d="M320 262 C420 240 440 140 388 88" fill="none" stroke-width="16"/>
        <path d="M170 252 C150 330 190 380 200 430 C180 500 170 560 190 650 L310 650 C330 560 320 500 300 430 C310 380 350 330 330 252Z"/>
        <path d="M190 300 Q250 332 310 300 M195 342 Q250 372 305 342 M200 384 Q250 408 300 384" fill="none"/>
        <path d="M172 262 C110 300 92 400 82 520 L72 600" fill="none" stroke-width="22"/><path d="M328 262 C390 300 408 400 418 520 L428 600" fill="none" stroke-width="22"/>
        <path d="M72 600 l-22 44 M72 600 l0 50 M72 600 l22 44 M428 600 l-22 44 M428 600 l0 50 M428 600 l22 44" fill="none" stroke-width="8"/>
        <path d="M250 30 C340 30 380 100 370 170 C362 226 320 266 250 270 C180 266 138 226 130 170 C120 100 160 30 250 30Z"/>
        <g fill="#0b0b10" fill-opacity="0.5" stroke="none"><circle cx="200" cy="90" r="11"/><circle cx="250" cy="80" r="11"/><circle cx="300" cy="90" r="11"/><circle cx="170" cy="130" r="9"/><circle cx="330" cy="130" r="9"/><circle cx="250" cy="120" r="9"/></g>
        <path d="M184 150 L226 162 L222 206 L188 190Z" fill="#eaff6b" stroke="#0b0b10" stroke-width="5"/><path d="M316 150 L274 162 L278 206 L312 190Z" fill="#eaff6b" stroke="#0b0b10" stroke-width="5"/>
        <path d="M196 232 L304 232" fill="none" stroke-dasharray="10 9" stroke-width="8"/></g></svg>`;

      const ERMES = `<svg viewBox="0 0 400 480" width="100%" height="100%">
        <path d="M0 480 C10 390 80 350 150 340 L250 340 C320 350 390 390 400 480Z" fill="#1f8f8a" stroke="#0b0b10" stroke-width="9"/>
        <path d="M300 352 C350 370 390 410 398 470 L330 480Z" fill="url(#hatch)" opacity="0.3"/>
        <path d="M164 276 L162 350 L238 350 L236 276Z" fill="#7b4a33" stroke="#0b0b10" stroke-width="8"/>
        <path d="M150 340 Q200 404 250 340" fill="#7b4a33" stroke="#0b0b10" stroke-width="8"/>
        <path d="M96 210 C66 120 108 30 200 26 C292 30 334 120 304 210 C292 166 108 166 96 210Z" fill="#141018" stroke="#0b0b10" stroke-width="8"/>
        <path d="M126 150 C124 100 156 70 200 70 C244 70 276 100 274 150 L270 220 C264 262 236 292 200 296 C164 292 136 262 130 220Z" fill="#8a5538" stroke="#0b0b10" stroke-width="9"/>
        <path d="M246 150 L273 150 L270 220 C264 260 242 288 214 294 C242 266 254 220 246 150Z" fill="url(#ht)" opacity="0.5"/>
        <path d="M160 46 L148 -26 L186 26 L200 -48 L214 26 L252 -26 L240 46Z" fill="#141018" stroke="#0b0b10" stroke-width="7" stroke-linejoin="round"/>
        <path d="M120 152 C110 92 140 40 200 34 C260 40 290 92 280 152 C260 112 230 102 200 106 C170 102 140 112 120 152Z" fill="#141018" stroke="#0b0b10" stroke-width="8"/>
        <path d="M122 134 C150 106 250 106 278 134 L276 154 C250 126 150 126 124 154Z" fill="#ff5fb8" stroke="#0b0b10" stroke-width="6"/>
        <circle cx="128" cy="240" r="18" fill="none" stroke="#ffcc1a" stroke-width="7"/><circle cx="272" cy="240" r="18" fill="none" stroke="#ffcc1a" stroke-width="7"/>
        <path d="M140 176 L192 186 L190 199 L138 189Z" fill="#0b0b10"/><path d="M260 176 L208 186 L210 199 L262 189Z" fill="#0b0b10"/>
        <path d="M146 208 Q168 194 192 208 Q168 218 146 208Z" fill="#fff" stroke="#0b0b10" stroke-width="5"/><circle cx="172" cy="207" r="7" fill="#0b0b10"/>
        <path d="M254 208 Q232 194 208 208 Q232 218 254 208Z" fill="#fff" stroke="#0b0b10" stroke-width="5"/><circle cx="228" cy="207" r="7" fill="#0b0b10"/>
        <path d="M146 206 L134 198 M254 206 L266 198" stroke="#0b0b10" stroke-width="5" stroke-linecap="round"/>
        <path d="M200 212 L193 248 Q200 254 213 248" fill="none" stroke="#0b0b10" stroke-width="5"/>
        <path d="M166 268 Q184 256 200 263 Q216 256 234 268 Q200 290 166 268Z" fill="#6a1a2e" stroke="#0b0b10" stroke-width="5"/>
        <path d="M150 226 L170 232 M154 236 L172 241 M230 232 L250 226 M228 241 L246 236" stroke="#0b0b10" stroke-width="3"/>
        <g transform="translate(286 412) rotate(-12)"><rect x="-58" y="-38" width="116" height="76" rx="12" fill="#f3ecdc" stroke="#0b0b10" stroke-width="5"/><path d="M-38 0 Q-19 -20 0 -9 Q19 -20 38 0 Q0 28 -38 0Z" fill="#ff2fa8" stroke="#0b0b10" stroke-width="4"/></g></svg>`;

      const LIP = `<svg viewBox="0 0 150 90" width="100%" height="100%"><rect x="4" y="4" width="142" height="82" rx="14" fill="#f3ecdc" stroke="#0b0b10" stroke-width="6"/><path d="M28 45 Q52 18 75 32 Q98 18 122 45 Q75 80 28 45Z" fill="#ff2fa8" stroke="#0b0b10" stroke-width="5"/><path d="M34 45 Q75 52 116 45" stroke="#0b0b10" stroke-width="4" fill="none"/></svg>`;

      const GLORIA = (crack) => `<svg viewBox="0 0 820 860" width="100%" height="100%">
        <rect x="10" y="10" width="800" height="840" fill="#5a3a1e" stroke="#0b0b10" stroke-width="12"/><rect x="34" y="34" width="752" height="792" fill="none" stroke="#a87a3e" stroke-width="10"/>
        <rect x="70" y="70" width="680" height="720" fill="#e9dcc0" stroke="#0b0b10" stroke-width="8"/>
        <path d="M250 520 C220 360 260 200 410 190 C560 200 600 360 570 520 C560 600 600 680 640 790 L180 790 C220 680 260 600 250 520Z" fill="#2c1f1a"/>
        <path d="M200 790 C220 640 300 600 410 600 C520 600 600 640 620 790Z" fill="#c25f8e" stroke="#0b0b10" stroke-width="6"/>
        <path d="M376 520 L372 610 L448 610 L444 520Z" fill="#8a5538"/>
        <ellipse cx="410" cy="390" rx="118" ry="148" fill="#9a6444" stroke="#0b0b10" stroke-width="6"/>
        <path d="M300 330 C320 250 380 236 410 238 C470 236 510 270 522 330 C480 290 340 290 300 330Z" fill="#2c1f1a"/>
        <path d="M352 384 Q372 398 392 384 M428 384 Q448 398 468 384" stroke="#0b0b10" stroke-width="6" fill="none" stroke-linecap="round"/>
        <path d="M372 462 Q410 488 448 462" stroke="#0b0b10" stroke-width="7" fill="none" stroke-linecap="round"/>
        <rect x="70" y="70" width="680" height="720" fill="url(#ht)" opacity="0.12"/>
        <path d="M640 70 L750 70 L750 180Z" fill="#0b0b10"/><path d="M70 680 L70 790 L180 790Z" fill="#0b0b10"/>
        ${crack ? `<g class="crk"><path d="M540 70 L480 230 L560 310 L430 440 L510 530 L380 650 L430 790" fill="none" stroke="#0b0b10" stroke-width="14"/><path d="M540 70 L480 230 L560 310 L430 440 L510 530 L380 650 L430 790" fill="none" stroke="#fff" stroke-width="5"/><path d="M480 230 L380 250 M430 440 L300 470 M510 530 L640 590" fill="none" stroke="#fff" stroke-width="4"/></g>` : ""}</svg>`;

      const ZHUM = (st) => `<svg viewBox="0 0 260 520" width="100%" height="100%"><g ${st}>
        <circle cx="128" cy="74" r="50"/><path d="M95 130 C70 150 70 260 85 330 L70 512 L120 512 L132 384 L145 512 L195 512 L180 330 C195 260 200 160 165 130Z"/>
        <path d="M96 150 C60 170 32 198 8 208 L14 236 C50 226 80 212 102 198Z"/><path d="M164 150 C200 160 238 178 256 186 L250 214 C220 206 190 198 158 196Z"/></g>
        <circle cx="110" cy="72" r="8" fill="#b6ff3c"/><circle cx="146" cy="72" r="8" fill="#b6ff3c"/></svg>`;
      const ZDOG = (st) => `<svg viewBox="0 0 330 230" width="100%" height="100%"><g ${st}>
        <path d="M20 70 L60 40 L74 10 L90 44 L118 70 L110 96 L60 110 L18 98Z"/>
        <path d="M100 80 C140 70 220 70 270 80 C300 60 316 40 326 30 L322 64 C306 86 292 96 286 104 L290 222 L262 222 L250 140 L150 140 L136 222 L108 222 L104 120 C96 110 96 96 100 80Z"/></g>
        <circle cx="62" cy="66" r="7" fill="#b6ff3c"/></svg>`;
      const ZBIRD = (st) => `<svg viewBox="0 0 220 160" width="100%" height="100%"><g ${st}>
        <path d="M10 92 C60 62 90 72 110 82 C130 30 172 8 212 20 C182 40 162 70 152 92 C172 102 192 102 212 98 C182 122 122 132 82 122 C52 117 30 107 10 92Z"/></g>
        <circle cx="40" cy="86" r="6" fill="#b6ff3c"/></svg>`;
      const SOLID = 'fill="#3b3346" stroke="#0b0b10" stroke-width="8" stroke-linejoin="round"';
      const GHOST = 'fill="rgba(182,255,60,0.06)" stroke="#b6ff3c" stroke-width="5" stroke-dasharray="14 10" stroke-linejoin="round"';
      const HAND = `<svg viewBox="0 0 120 200" width="100%" height="100%"><g stroke-linecap="round" fill="none">
        <path d="M60 200 L58 112 M72 200 L72 112 M40 104 L28 52 L22 22 M52 98 L48 40 L46 6 M66 98 L70 38 L72 4 M80 102 L90 48 L96 20 M44 112 L16 86 L6 66" stroke="#0b0b10" stroke-width="20"/>
        <path d="M60 200 L58 112 M72 200 L72 112 M40 104 L28 52 L22 22 M52 98 L48 40 L46 6 M66 98 L70 38 L72 4 M80 102 L90 48 L96 20 M44 112 L16 86 L6 66" stroke="#f3ecdc" stroke-width="10"/>
        <path d="M36 92 Q64 120 90 94" stroke="#0b0b10" stroke-width="26"/><path d="M36 92 Q64 120 90 94" stroke="#f3ecdc" stroke-width="14"/></g></svg>`;
      const FOOT = `<svg viewBox="0 0 70 120" width="100%" height="100%"><g fill="rgba(182,255,60,0.8)"><ellipse cx="36" cy="78" rx="24" ry="38"/><circle cx="14" cy="26" r="8"/><circle cx="28" cy="16" r="8"/><circle cx="43" cy="14" r="8"/><circle cx="56" cy="22" r="7"/><circle cx="63" cy="36" r="6"/></g></svg>`;
      const HPRINT = `<svg viewBox="0 0 260 320" width="100%" height="100%"><g fill="rgba(210,255,190,0.55)" stroke="rgba(182,255,60,0.9)" stroke-width="4"><path d="M60 300 C30 240 40 170 60 150 L54 40 C54 22 78 22 80 40 L88 130 L96 20 C98 0 124 0 124 20 L122 128 L140 26 C144 6 170 10 166 30 L152 138 L184 60 C192 42 214 50 208 70 L178 190 C220 150 246 160 236 182 C200 240 170 300 120 316 C96 322 72 318 60 300Z"/></g></svg>`;

      // ---- animation helpers (smooth, manga-impact style)
      const pop = (sel, t, s = 0) => tl.fromTo(sel, { scale: s, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: "back.out(2.6)" }, t);
      const slam = (sel, t, from = 3, rot = 0) => tl.fromTo(sel, { scale: from, opacity: 0, rotation: rot * 2 }, { scale: 1, opacity: 1, rotation: rot, duration: 0.16, ease: "power4.in" }, t);
      const rise = (sel, t, y = 80) => tl.fromTo(sel, { y, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, t);
      const out = (sel, t, d = 0.2) => tl.to(sel, { opacity: 0, duration: d }, t);
      const shake = (sel, t, a = 16, n = 6) => { const r = rng(Math.floor(t * 97)); for (let k = 0; k < n; k++) tl.to(sel, { x: (r() - 0.5) * 2 * a, y: (r() - 0.5) * 2 * a, duration: 0.045, ease: "none" }, t + k * 0.045); tl.to(sel, { x: 0, y: 0, duration: 0.06 }, t + n * 0.045); };
      const flash = (t, o = 0.9) => { tl.set("#flash", { opacity: o }, t); tl.to("#flash", { opacity: 0, duration: 0.35, ease: "power2.out" }, t + 0.01); };
      const bg = (id, t, d = 0.15) => { ["#bgB", "#bgC", "#bgD", "#bgE"].forEach((b) => tl.to(b, { opacity: b === id ? 1 : 0, duration: d }, t)); };
      const impact = (t, strong = 1) => { tl.set("#invert", { opacity: 1 }, t); tl.set("#invert", { opacity: 0 }, t + 0.06 * strong); tl.fromTo("#root", { scale: 1 + 0.07 * strong }, { scale: 1, duration: 0.3, ease: "power3.out" }, t); shake("#root", t + 0.02, 14 * strong, 5); };
      const focus = (t, d = 0.8, dark = false) => { const f = dark ? "#focusK" : "#focus"; tl.set(f, { opacity: 1 }, t); tl.fromTo(f, { rotation: 0, scale: 1.15 }, { rotation: 6, scale: 1, duration: d, ease: "none" }, t); tl.to(f, { opacity: 0, duration: 0.15 }, t + d); };
      const glitch = (sel, t, n = 6) => { for (let i = 0; i < n; i++) tl.set(sel, { x: i % 2 ? 22 : -22, skewX: (i % 3 - 1) * 16 }, t + i * 0.05); tl.set(sel, { x: 0, skewX: 0 }, t + n * 0.05); };
      // menacing ゴゴゴ / ドドド floating on the sides (each call gets its own glyphs)
      let onoK = 0;
      const menace = (t, d = 2.5, seed = 1, ch = "ゴ", col = "#c04dff", n = 8) => { const r = rng(seed); for (let i = 0; i < n; i++) { const id = "ono" + onoK++; $("onos").insertAdjacentHTML("beforeend", `<div class="ono" id="${id}" style="font-size:${120 + (i % 3) * 30}px;color:${col}">${ch}</div>`); const x = (i % 2 ? 780 : 30) + r() * 160, y = 260 + r() * 900; tl.fromTo("#" + id, { x, y, opacity: 0, scale: 0.5, rotation: (r() - 0.5) * 30 }, { x: x + (r() - 0.5) * 50, y: y - 140, opacity: 1, scale: 1, duration: d * 0.45, ease: "power2.out" }, t + i * 0.07); tl.to("#" + id, { opacity: 0, duration: 0.25 }, t + d); } };

      // ---- captions (manga text, current word in toxic green)
      const cap = $("cap");
      const lines = []; let cur = [];
      WORDS.forEach((w, i) => { if (/^[:?!…»«]+$/.test(w.t)) { if (cur.length) cur[cur.length - 1].t += w.t === "?" || w.t === ":" ? " " + w.t : w.t; else if (lines.length) { const l = lines[lines.length - 1]; l[l.length - 1].t += " " + w.t; } return; } cur.push({ ...w }); const txt = cur.map((x) => x.t).join(" "); const end = /[.?!…]$/.test(w.t) || (/,$/.test(w.t) && txt.length > 12); if (end || txt.length > 20 || i === WORDS.length - 1) { lines.push(cur); cur = []; } });
      if (cur.length) lines.push(cur);
      if (lines.length > 1 && lines[lines.length - 1].length < 3) { const l = lines.pop(); lines[lines.length - 1].push(...l); }
      lines.forEach((ln, i) => {
        const d = document.createElement("div"); d.className = "ln"; d.id = "ln" + i;
        ln.forEach((w, j) => { const s = document.createElement("span"); s.className = "w"; s.id = `w${i}_${j}`; s.textContent = w.t.toUpperCase(); d.appendChild(s); });
        cap.appendChild(d);
        const t0 = ln[0].s - 0.04, t1 = lines[i + 1] ? lines[i + 1][0].s - 0.04 : ln[ln.length - 1].e + 1.0;
        tl.set("#ln" + i, { opacity: 1 }, t0); tl.fromTo("#ln" + i, { scale: 0.85 }, { scale: 1, duration: 0.12, ease: "back.out(3)", immediateRender: false }, t0); tl.set("#ln" + i, { opacity: 0 }, t1);
        ln.forEach((w, j) => { tl.fromTo(`#w${i}_${j}`, { color: "#ffffff" }, { color: "#b6ff3c", duration: 0.01 }, w.s); tl.set(`#w${i}_${j}`, { color: "#ffffff" }, Math.min(w.e + 0.12, t1)); });
      });
      gsap.set(".jt", { xPercent: -50 });

