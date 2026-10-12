      // ---- inject drawings
      document.querySelectorAll(".maxx").forEach((d) => (d.innerHTML = MAXX));
      document.querySelectorAll(".stand").forEach((d) => (d.innerHTML = STAND));
      document.querySelectorAll(".ermes").forEach((d) => (d.innerHTML = ERMES));
      $("gframe").innerHTML = GLORIA(true); $("gmini").innerHTML = GLORIA(false);
      [["z1", ZHUM], ["z2", ZDOG], ["z3", ZBIRD]].forEach(([id, f]) => { $(id).querySelector(".sol").innerHTML = f(SOLID); $(id).querySelector(".gh").innerHTML = f(GHOST); });
      tl.set("#gframe .crk", { opacity: 0 }, 0);
      // single big onomatopoeia
      let onoS = 0;
      const ono1 = (txt, x, y, t, size = 170, col = "#c04dff", rot = -8, d = 1.0) => { const id = "os" + onoS++; $("onos").insertAdjacentHTML("beforeend", `<div class="ono" id="${id}" style="left:${x}px;top:${y}px;font-size:${size}px;color:${col}">${txt}</div>`); tl.fromTo("#" + id, { scale: 2.6, opacity: 0, rotation: rot * 2 }, { scale: 1, opacity: 1, rotation: rot, duration: 0.14, ease: "power4.in" }, t); tl.to("#" + id, { opacity: 0, scale: 1.15, duration: 0.25 }, t + d); };

      // ===== S1 cold open: prison -> LIMP BIZKIT
      { const B = $("bars"); let h = "";
        for (let i = 0; i < 8; i++) { const x = 30 + i * 140; h += `<rect x="${x}" y="-20" width="50" height="1960" fill="#55525e" stroke="#0b0b10" stroke-width="8"/><rect x="${x + 10}" y="-20" width="10" height="1960" fill="#8c8898"/>`; }
        h += `<rect x="-20" y="250" width="1120" height="46" fill="#55525e" stroke="#0b0b10" stroke-width="8"/><rect x="-20" y="1560" width="1120" height="46" fill="#55525e" stroke="#0b0b10" stroke-width="8"/>`;
        B.innerHTML = `<g id="barsg">${h}</g>`;
        const D = $("drips"); for (let i = 0; i < 9; i++) D.insertAdjacentHTML("beforeend", `<div class="drip" id="dr${i}" style="left:${40 + i * 120}px;height:${300 + ((i * 137) % 260)}px"></div>`);
        tl.set("#lightcone", { opacity: 1 }, 0.1); tl.fromTo("#lightcone", { rotation: -28 }, { rotation: 28, duration: 1.6, ease: "sine.inOut", repeat: 3, yoyo: true }, 0.1);
        menace(0.05, 2.0, 11);
        tl.fromTo("#barsg", { x: -1100 }, { x: 0, duration: 0.18, ease: "power4.in" }, 0.42); impact(0.6, 1.2);
        rise("#pname .s", 0.95); slam("#pname .b", 1.35, 3, -3); impact(1.5, 0.8);
        const ts = W("stone"); out("#pname", ts - 0.15, 0.15); tl.to("#lightcone", { opacity: 0, duration: 0.3 }, ts);
        pop("#so", ts - 0.05);
        const tp = W("prison"); shake("#barsg", tp, 18, 7); flash(tp, 0.35);
        const tf = W("film"); tl.to("#redwash", { opacity: 0.55, duration: 0.2 }, tf);
        for (let i = 0; i < 9; i++) tl.fromTo("#dr" + i, { scaleY: 0 }, { scaleY: 1, duration: 1.0 + (i % 3) * 0.3, ease: "power2.in" }, tf + (i % 4) * 0.08);
        slam("#horror", W("horreur") - 0.05, 2.6, -4); glitch("#horror", W("horreur") + 0.35, 6);
        const tl1 = W("limp") - 0.08;
        tl.set(["#barsg", "#so", "#drips", "#horror"], { opacity: 0 }, tl1); tl.set("#redwash", { opacity: 0 }, tl1); bg("#bgC", tl1, 0.05);
        slam("#t1", tl1, 4, -5); impact(tl1 + 0.12, 1.5); focus(tl1 + 0.12, 1.6); flash(tl1 + 0.1, 0.8);
        menace(tl1 + 0.1, 2.4, 13, "ド", "#b6ff3c");
        tl.fromTo("#title .kana", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, W("bizkit") + 0.1);
        tl.fromTo("#standS1", { y: 700, opacity: 0 }, { y: 0, opacity: 0.95, duration: 0.6, ease: "power3.out" }, tl1 + 0.1);
        tl.fromTo("#standS1", { filter: "drop-shadow(0 0 0px #b6ff3c)" }, { filter: "drop-shadow(0 0 30px #b6ff3c)", duration: 0.5, repeat: 3, yoyo: true }, tl1 + 0.4);
        tl.fromTo("#t1", { y: 0 }, { y: -10, duration: 0.6, repeat: 3, yoyo: true, ease: "sine.inOut" }, tl1 + 0.3);
        rise("#user1", W("sports") - 0.1); }

      // ===== S2 Sports Maxx dossier
      { bg("#bgB", S(2));
        tl.fromTo("#dossier", { x: 1150, rotation: 6 }, { x: 0, rotation: -2, duration: 0.3, ease: "power3.out" }, S(2));
        tl.fromTo("#mx2", { y: 900 }, { y: 0, duration: 0.35, ease: "back.out(1.3)" }, S(2) + 0.1); impact(S(2) + 0.3, 0.8);
        slam("#gang", W("gangster") - 0.05, 2.5, -6); impact(W("gangster") + 0.08, 0.7);
        rise("#gds", W("green") - 0.1, 60);
        tl.fromTo("#disc", { x: -600, rotation: -540, opacity: 1 }, { x: 0, rotation: 0, duration: 0.45, ease: "power3.out" }, W("homme") - 0.1);
        tl.to("#disc", { rotation: 360, duration: 2.4, ease: "none" }, W("homme") + 0.35);
        pop("#ws", W("whitesnake")); glitch(["#mx2", "#disc"], W("whitesnake") + 0.2, 7); ono1("ズン", 700, 330, W("whitesnake"), 120, "#ffffff", 6, 0.8);
        const tsu = W("surtout"); tl.to("#mx2", { scale: 1.22, y: -40, duration: 0.8, ease: "power2.inOut" }, tsu); focus(tsu, 0.9, true); out(["#gang", "#gds", "#disc", "#ws"], tsu, 0.2);
        const tc = W("celui"); out(["#dossier", "#mx2"], tc - 0.1, 0.12);
        tl.fromTo("#gframe", { scale: 0.5, opacity: 0, rotation: 4 }, { scale: 1, opacity: 1, rotation: -2, duration: 0.35, ease: "back.out(1.6)" }, tc);
        const tt = W("tué"); tl.set("#gframe .crk", { opacity: 1 }, tt); impact(tt, 1.3); flash(tt, 0.7); tl.set("#redwash", { opacity: 0.5 }, tt); tl.to("#redwash", { opacity: 0, duration: 0.8 }, tt + 0.1);
        tl.fromTo("#tuee", { scale: 3, opacity: 0, rotation: -30 }, { scale: 1, opacity: 1, rotation: -14, duration: 0.14, ease: "power4.in" }, tt + 0.05);
        pop("#gl1", W("gloria")); pop("#gl2", W("sœur"));
        tl.fromTo("#gframe", { y: 0 }, { y: 18, duration: 0.5, repeat: 2, yoyo: true, ease: "sine.inOut" }, W("gloria")); }

      // ===== S3 power: resurrection -> invisible
      { bg("#bgC", S(3));
        tl.fromTo("#stand3", { y: 900, opacity: 0 }, { y: 0, opacity: 0.95, duration: 0.45, ease: "power3.out" }, S(3)); impact(S(3) + 0.35, 0.9);
        tl.fromTo("#stand3", { filter: "drop-shadow(0 0 0px #b6ff3c)" }, { filter: "drop-shadow(0 0 34px #b6ff3c)", duration: 0.45, repeat: 5, yoyo: true }, S(3) + 0.3);
        slam("#pow", W("pouvoir") - 0.05, 2.4, -3);
        tl.fromTo("#ground", { y: 900 }, { y: 0, duration: 0.35, ease: "power3.out" }, W("ramène") - 0.1);
        const H = $("hands"); const hx = [190, 330, 600, 760, 900];
        hx.forEach((x, i) => { H.insertAdjacentHTML("beforeend", `<div class="hand" id="hd${i}" style="left:${x - 60}px;top:${930 + (i % 2) * 30}px">${HAND}</div>`); tl.fromTo("#hd" + i, { y: 260, opacity: 0, rotation: (i % 2 ? 8 : -8) }, { y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }, W("morts") + i * 0.07); });
        impact(W("morts") + 0.1, 0.6); menace(W("morts"), 2.2, 21, "ゴ", "#b6ff3c");
        tl.to("#stand3", { opacity: 0.35, duration: 0.3 }, W("humains") - 0.2); out("#pow", W("humains") - 0.2);
        tl.fromTo("#z1", { y: 500, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "power3.out" }, W("humains") - 0.1); pop("#hum", W("humains"));
        tl.fromTo("#z2", { y: 300, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, W("animaux") - 0.1);
        tl.fromTo("#z3", { x: 300, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, W("animaux")); pop("#ani", W("animaux"));
        tl.fromTo("#peu", { scale: 3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.14, ease: "power4.in" }, W("importe") - 0.1); out("#peu", W("importe") + 0.9);
        const tr = W("relèvent"); ["#z1", "#z2", "#z3"].forEach((z, i) => tl.to(z, { y: -40, duration: 0.12, yoyo: true, repeat: 3, ease: "power1.inOut" }, tr + i * 0.05)); impact(tr + 0.1, 0.9); ono1("ズズ…", 300, 380, tr, 150, "#b6ff3c", -6, 1.0);
        const td = W("détail"); out(["#hum", "#ani"], td - 0.2); tl.fromTo("#mag", { opacity: 0, x: -340, scale: 0.6 }, { opacity: 1, x: 0, scale: 1, duration: 0.35, ease: "power3.out" }, td - 0.1);
        tl.to("#mag", { x: 220, y: -80, duration: 1.2, ease: "sine.inOut" }, td + 0.3); focus(W("tout", 25) - 0.1, 0.9, true);
        const ti = W("invisibles"); out("#mag", ti - 0.3, 0.15);
        ["#z1", "#z2", "#z3"].forEach((z) => { tl.to(z + " .sol", { opacity: 0, duration: 0.5 }, ti); tl.to(z + " .gh", { opacity: 1, duration: 0.3 }, ti); });
        glitch(["#z1", "#z2", "#z3"], ti, 8); tl.to("#stand3", { opacity: 0.18, duration: 0.4 }, ti);
        slam("#invis", ti - 0.05, 3, -3); impact(ti + 0.08, 1.2); flash(ti + 0.05, 0.5);
        tl.to("#t3", { opacity: 0.25, duration: 0.12, repeat: 5, yoyo: true }, ti + 0.4); }

      // ===== S4 invisible army
      { bg("#bgE", S(4), 0.05);
        tl.fromTo("#corr", { scale: 1.35, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.5, ease: "power2.out" }, S(4));
        const F = $("fps"); const t0 = W("imagine"); const n = 12;
        for (let i = 0; i < n; i++) { const k = i / (n - 1); const sc = 0.35 + k * 1.3, y = 700 + k * 560, x = 540 + (i % 2 ? 1 : -1) * (24 + k * 70) - 35;
          F.insertAdjacentHTML("beforeend", `<div class="fp" id="fp${i}" style="left:${x}px;top:${y}px">${FOOT}</div>`);
          tl.fromTo("#fp" + i, { opacity: 0, scale: sc * 1.4, rotation: i % 2 ? 8 : -8 }, { opacity: 1, scale: sc, duration: 0.08 }, t0 + 0.2 + i * 0.48); tl.to("#fp" + i, { opacity: 0, duration: 0.5 }, t0 + 1.4 + i * 0.48); }
        const A = $("army"); const ta = W("armée") - 0.1; const rr = rng(44);
        for (let i = 0; i < 14; i++) { const row = Math.floor(i / 5), x = 20 + (i % 5) * 190 + (row % 2) * 90 + rr() * 30, y = 40 + row * 170;
          A.insertAdjacentHTML("beforeend", `<div class="ga" id="ga${i}" style="left:${x}px;top:${y}px">${ZHUM(GHOST)}</div>`);
          tl.fromTo("#ga" + i, { opacity: 0, scale: 0.6 }, { opacity: 0.9, scale: 1, duration: 0.15, ease: "back.out(2)" }, ta + i * 0.045); tl.to("#ga" + i, { opacity: 0, duration: 0.18 }, W("vois") - 0.05 + rr() * 0.15); }
        glitch("#army", W("vois") - 0.1, 6);
        pop("#see", W("vois") - 0.05); impact(W("vois"), 0.6); out("#see", W("entends") - 0.2);
        pop("#hear", W("entends") - 0.05); tl.to("#hear", { x: -14, duration: 0.08, repeat: 7, yoyo: true }, W("entends") + 0.2);
        pop("#feel", W("sens", 30) - 0.05); tl.to("#feel", { y: -20, duration: 0.15, repeat: 5, yoyo: true }, W("sens", 30) + 0.2);
        out(["#hear", "#feel"], W("peux") - 0.35);
        slam("#cant", W("peux") - 0.1, 2.4, -2);
        const tv = W("voir", 33); const P = $("hps"); const hp = [[80, 340, -18], [700, 280, 14], [430, 560, -4]];
        hp.forEach(([x, y, r], i) => { P.insertAdjacentHTML("beforeend", `<div class="hp" id="hp${i}" style="left:${x}px;top:${y}px">${HPRINT}</div>`); tl.fromTo("#hp" + i, { opacity: 0, scale: 1.6, rotation: r }, { opacity: 1, scale: 1, rotation: r, duration: 0.08 }, tv + i * 0.12); impact(tv + i * 0.12, 0.7); });
        flash(tv, 0.5); }

      // ===== S5 Maxx dies -> invisible zombie -> head detach
      { bg("#bgB", S(5), 0.05);
        const tfo = W("fou") - 0.1; slam("#fou", tfo, 3, -4); impact(tfo + 0.12, 1); focus(tfo + 0.12, 0.8);
        const tq = W("quand"); out("#fou", tq - 0.1, 0.12);
        tl.fromTo("#mx5", { y: 1500 }, { y: 0, duration: 0.3, ease: "power3.out" }, tq - 0.1);
        tl.set("#ecg", { opacity: 0 }, 0); tl.set("#ecgp", { strokeDasharray: 1500, strokeDashoffset: 1500 }, 0); tl.set("#ecg", { opacity: 1 }, tq);
        tl.to("#ecgp", { strokeDashoffset: 0, duration: 0.55, ease: "none" }, tq);
        const tm = W("meurt"); tl.set("#ecgp", { opacity: 0 }, tm); tl.set("#ecgf", { opacity: 1 }, tm); impact(tm, 1.4); flash(tm, 0.6);
        tl.set("#mx5", { filter: "grayscale(1) brightness(0.7)" }, tm);
        tl.fromTo("#skull", { opacity: 0, scale: 2 }, { opacity: 1, scale: 1, duration: 0.12, ease: "power4.in" }, tm + 0.02); out("#skull", W("devient") - 0.1, 0.15);
        const tdv = W("devient"); out("#ecg", tdv, 0.2); bg("#bgC", tdv, 0.3);
        tl.to("#mx5", { opacity: 0.5, duration: 0.6 }, tdv); tl.set("#mx5", { filter: "grayscale(0.4) drop-shadow(0 0 22px #b6ff3c) drop-shadow(0 0 6px #b6ff3c)" }, tdv);
        glitch("#mx5", tdv + 0.1, 6); glitch("#mx5", W("invisible", 37), 6);
        rise("#zi", W("zombie", 37) - 0.1); menace(W("zombie", 37), 2.5, 31, "ゴ", "#b6ff3c");
        const tdt = W("détacher"); shake("#mx5 .head", tdt, 10, 10);
        const tte = W("tête"); tl.to("#mx5 .head", { y: -230, rotation: -22, duration: 0.25, ease: "power3.out" }, tte - 0.05); impact(tte, 1.2); ono1("ボキッ", 600, 300, tte - 0.05, 160, "#ffffff", 10, 0.7);
        const tat = W("attaquer"); out("#zi", tat - 0.1);
        tl.fromTo("#angle", { opacity: 0, rotation: -90, scale: 0.6 }, { opacity: 1, rotation: 0, scale: 1, duration: 0.5, ease: "power3.out" }, tat - 0.1);
        tl.to("#mx5 .head", { keyframes: [{ x: 210, y: -320, rotation: 90, duration: 0.3 }, { x: 260, y: 40, rotation: 200, duration: 0.3 }, { x: -120, y: 120, rotation: 300, duration: 0.3 }, { x: -60, y: -260, rotation: 340, duration: 0.25 }], ease: "power2.inOut" }, tat);
        tl.to("#angle", { rotation: 40, duration: 1.6, ease: "none" }, tat + 0.4);
        const tim = W("impossible"); slam("#imp", tim - 0.05, 3, -3); impact(tim + 0.08, 1.3); focus(tim + 0.08, 0.8); }

      // ===== S6 Ermes: vengeance
      { bg("#bgD", S(6), 0.1);
        tl.fromTo("#split", { x: 900 }, { x: 0, duration: 0.25, ease: "power3.out" }, S(6));
        tl.fromTo("#mx6", { x: -500 }, { x: 0, duration: 0.3, ease: "power3.out" }, S(6) + 0.05);
        tl.set("#mx6", { filter: "grayscale(0.4) drop-shadow(0 0 18px #b6ff3c)" }, 0);
        const te = W("ermes", 43); tl.fromTo("#er6", { x: 800, opacity: 0 }, { x: 0, opacity: 1, duration: 0.18, ease: "power4.in" }, te - 0.12);
        impact(te + 0.06, 1.5); flash(te + 0.05, 0.8); focus(te + 0.06, 1.2, true); ono1("ドォーン", 120, 1080, te, 140, "#ff2fa8", -6, 1.4);
        slam("#ername", te + 0.15, 2.5, -4); rise("#kiss", te + 0.55);
        const L = $("lips"); const lp = [[620, 330, -14], [140, 760, 10], [820, 1000, -6], [260, 1120, 12]];
        const tk = W("ermes", 45); lp.forEach(([x, y, r], i) => { L.insertAdjacentHTML("beforeend", `<div class="lip" id="lp${i}" style="left:${x}px;top:${y}px">${LIP}</div>`); tl.fromTo("#lp" + i, { opacity: 0, scale: 2.2, rotation: r * 2 }, { opacity: 1, scale: 1, rotation: r, duration: 0.1, ease: "power4.in" }, tk + i * 0.22); });
        out(["#ername", "#kiss"], W("chose", 44) - 0.1);
        tl.fromTo("#gmini", { opacity: 0, scale: 0.4, rotation: -10 }, { opacity: 1, scale: 1, rotation: -6, duration: 0.3, ease: "back.out(2)" }, W("tête", 45) - 0.2);
        const tvg = W("venger"); out("#lips", tvg - 0.1, 0.15); slam("#veng", tvg - 0.05, 3.2, -4); impact(tvg + 0.1, 1.6); tl.set("#redwash", { opacity: 0.4 }, tvg + 0.05); tl.to("#redwash", { opacity: 0, duration: 0.6 }, tvg + 0.3);
        menace(tvg, 1.6, 41, "ド", "#e3122f"); tl.to("#gmini", { scale: 1.12, duration: 0.18, repeat: 3, yoyo: true }, W("sœur", 46)); }

      // ===== S7 the name: nu metal band
      { bg("#bgE", S(7), 0.1);
        tl.fromTo("#amp", { y: -900 }, { y: 0, duration: 0.35, ease: "back.out(1.2)" }, S(7)); impact(S(7) + 0.3, 1);
        rise("#eq", S(7) + 0.3); const r = rng(77);
        document.querySelectorAll("#eq i").forEach((b, i) => { tl.set(b, { scaleY: 0.2 }, 0); for (let t = S(7) + 0.4; t < W("donné") - 0.2; t += 0.16) tl.to(b, { scaleY: 0.15 + r() * 0.85, duration: 0.14, ease: "power2.out" }, t); });
        slam("#nu", W("groupe") - 0.05, 2.4, -3); impact(W("metal"), 1.1); menace(W("metal"), 1.4, 51, "ド", "#ff2fa8");
        const tdn = W("donné"); tl.to(["#amp", "#eq", "#nu"], { y: -1400, duration: 0.3, ease: "power3.in" }, tdn - 0.15);
        pop("#meter", tdn + 0.05, 0.6);
        { const m = { v: 0 }; tl.fromTo("#mfill", { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "power2.in" }, W("combats")); tl.to(m, { v: 100, duration: 0.8, ease: "power2.in", onUpdate: () => ($("mval").textContent = Math.round(m.v) + "%") }, W("combats")); }
        const tg = W("glauques"); slam("#glau", tg - 0.05, 3, -4); impact(tg + 0.1, 1.3); tl.set("#redwash", { opacity: 0.35 }, tg); tl.to("#redwash", { opacity: 0, duration: 0.5 }, tg + 0.2);
        shake("#meter", tg + 0.1, 16, 8); flash(W("jojo"), 0.5); }

      // ===== S8 CTA + To Be Continued freeze
      { bg("#bgA", S(8), 0.1);
        slam("#sub", W("abonne") - 0.05, 2.2, -2); impact(W("abonne") + 0.08, 0.9);
        tl.to("#sub", { scale: 0.9, duration: 0.08, yoyo: true, repeat: 1 }, W("abonne") + 0.6); tl.set("#sub1", { opacity: 0 }, W("abonne") + 0.68); tl.set("#sub2", { opacity: 1 }, W("abonne") + 0.68); tl.set("#sub", { background: "#2a2a34" }, W("abonne") + 0.68);
        rise("#next", W("commentaire") - 0.4, 120);
        document.querySelectorAll("#grid .c").forEach((c, i) => tl.fromTo(c, { opacity: 0, x: i % 2 ? 80 : -80 }, { opacity: 1, x: 0, duration: 0.2, ease: "power3.out" }, W("commentaire") - 0.2 + i * 0.1));
        tl.to("#grid .c", { background: "#3b1470", duration: 0.15, stagger: 0.12, yoyo: true, repeat: 1 }, W("ensuite"));
        const tb = E(8) - 2.3; tl.set("#sepia", { opacity: 0.9 }, tb); tl.set("#sepia2", { opacity: 1 }, tb); tl.set("#root", { scale: 1.03 }, tb);
        tl.fromTo("#tbc", { x: -800, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, tb + 0.05); }

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
