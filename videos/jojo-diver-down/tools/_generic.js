

      const OFF = {{OFF}};
      const WORDS = {{WORDS}}.filter((w) => w.type === "word").map((w) => ({ t: w.text, s: w.start + OFF, e: w.end + OFF }));
      const SC = {{SCENES}};
      const TOTAL = {{TOTAL}};
      const W = (sub, after = 0) => { for (const w of WORDS) if (w.s >= after && w.t.toLowerCase().includes(sub)) return w.s; throw new Error("word " + sub); };
      function rng(seed) { return function () { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
      const tl = gsap.timeline({ paused: true });
      const S = (i) => SC[i - 1].start, E = (i) => SC[i - 1].start + SC[i - 1].dur;
      const pop = (sel, t) => tl.fromTo(sel, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2.5)" }, t);
      const rise = (sel, t, y = 60) => tl.fromTo(sel, { y, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "steps(5)" }, t);
      const shake = (sel, t, a = 16, n = 6) => { const r = rng(Math.floor(t * 97)); for (let k = 0; k < n; k++) tl.to(sel, { x: Math.round((r() - 0.5) * 2 * a / 8) * 8, y: Math.round((r() - 0.5) * 2 * a / 8) * 8, duration: 0.05, ease: "none" }, t + k * 0.05); tl.to(sel, { x: 0, y: 0, duration: 0.05 }, t + n * 0.05); };
      const flash = (t, o = 0.9) => { tl.set("#flash", { opacity: o }, t); tl.to("#flash", { opacity: 0, duration: 0.35, ease: "power2.out" }, t + 0.01); };
      // frame-by-frame sprite animation: sheet has N frames + copy of frame 0
      const anim = (sel, n, fps, t0, t1) => { const img = document.querySelector(sel + " img"); const w = parseFloat(img.style.width) / (n + 1); const cyc = n / fps; const reps = Math.max(1, Math.floor((t1 - t0) / cyc)); tl.fromTo(sel + " img", { x: 0 }, { x: -n * w, duration: cyc, ease: `steps(${n})`, repeat: reps - 1 }, t0); };

      // ---- captions
      const cap = document.getElementById("cap");
      const lines = []; let cur = [];
      WORDS.forEach((w, i) => { if (/^[:?!…»«]+$/.test(w.t)) { if (cur.length) cur[cur.length - 1].t += w.t === "?" || w.t === ":" ? " " + w.t : w.t; else if (lines.length) { const l = lines[lines.length - 1]; l[l.length - 1].t += " " + w.t; } return; } cur.push({ ...w }); const txt = cur.map((x) => x.t).join(" "); const end = /[.?!…]$/.test(w.t) || (/,$/.test(w.t) && txt.length > 14); if (end || txt.length > 22 || i === WORDS.length - 1) { lines.push(cur); cur = []; } });
      if (cur.length) lines.push(cur);
      if (lines.length > 1 && lines[lines.length - 1].length < 3) { const l = lines.pop(); lines[lines.length - 1].push(...l); }
      lines.forEach((ln, i) => {
        const d = document.createElement("div"); d.className = "ln"; d.id = "ln" + i;
        ln.forEach((w, j) => { const s = document.createElement("span"); s.className = "w"; s.id = `w${i}_${j}`; s.textContent = w.t.toUpperCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); d.appendChild(s); });
        cap.appendChild(d);
        const t0 = ln[0].s - 0.04, t1 = lines[i + 1] ? lines[i + 1][0].s - 0.04 : ln[ln.length - 1].e + 1.2;
        tl.set("#ln" + i, { opacity: 1 }, t0); tl.set("#ln" + i, { opacity: 0 }, t1);
        ln.forEach((w, j) => { tl.fromTo(`#w${i}_${j}`, { opacity: 0.25, color: "#f4f2ee" }, { opacity: 1, color: "#ffd228", duration: 0.01 }, w.s); tl.set(`#w${i}_${j}`, { color: "#f4f2ee" }, Math.min(w.e + 0.15, t1)); });
      });
      tl.fromTo("#cap", { y: 300 }, { y: 0, duration: 0.3, ease: "steps(6)" }, 0.1);
      tl.fromTo("#tri", { opacity: 1 }, { opacity: 0, duration: 0.3, repeat: Math.floor(TOTAL / 0.6) - 1, yoyo: true, ease: "steps(1)" }, 0);

      // ---- impact helpers ("montage qui en jette")
      const impact = (t, strong = 1) => { tl.set("#invert", { opacity: 1 }, t); tl.set("#invert", { opacity: 0 }, t + 0.07 * strong); tl.fromTo("#root", { scale: 1 + 0.08 * strong }, { scale: 1, duration: 0.25, ease: "power3.out" }, t); shake("#root", t + 0.02, 14 * strong, 5); };
      const speed = (t, d = 0.6) => { tl.set("#speed", { opacity: 1 }, t); tl.fromTo("#speed", { rotation: 0 }, { rotation: 25, duration: d, ease: "none" }, t); tl.set("#speed", { opacity: 0 }, t + d); };
      const glitch = (sel, t, n = 6) => { for (let i = 0; i < n; i++) tl.set(sel, { x: i % 2 ? 18 : -18, skewX: (i % 3 - 1) * 14 }, t + i * 0.06); tl.set(sel, { x: 0, skewX: 0 }, t + n * 0.06); };

