      // ---- fx helpers
      const bg = (id, t) => { ["#bgalt", "#bgred"].forEach((b) => tl.to(b, { opacity: b === id ? 1 : 0, duration: 0.2 }, t)); };
      // menacing ゴ particles
      const GO = document.getElementById("gos"); const goN = 10;
      for (let i = 0; i < goN; i++) GO.insertAdjacentHTML("beforeend", `<div class="go" id="go${i}">ゴ</div>`);
      const menace = (t, d = 2.5, seed = 1) => { const r = rng(seed); for (let i = 0; i < goN; i++) { const x = (i % 2 ? 760 : 40) + r() * 220, y = 300 + r() * 800; tl.fromTo("#go" + i, { x, y, opacity: 0, scale: 0.6 }, { x: x + (r() - 0.5) * 60, y: y - 160, opacity: 1, scale: 1, duration: d * 0.5, ease: "power1.out" }, t + i * 0.08); tl.to("#go" + i, { opacity: 0, duration: 0.3 }, t + d); } };

      // HUD: timer counts down, right HP shakes on hits
      { const tm = { v: 99 }; tl.to(tm, { v: 0, duration: TOTAL, ease: "none", onUpdate: () => (document.getElementById("timer").textContent = String(Math.max(0, Math.round(tm.v))).padStart(2, "0")) }, 0); }
      tl.fromTo("#hud", { y: -200 }, { y: 0, duration: 0.3, ease: "steps(5)" }, 0.1);
      tl.fromTo("#hpL", { scaleX: 1 }, { scaleX: 1, duration: 0.01 }, 0);
      tl.fromTo("#hpR", { scaleX: 1 }, { scaleX: 1, duration: 0.01 }, 0);

      // ===== S1 time stop -> Diver Down
      { const tt = W("temps");
        tl.fromTo("#clock", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, W("stands") - 0.2);
        tl.fromTo("#hand1", { rotation: 0 }, { rotation: 300, duration: 1.2, ease: "none" }, W("stands") - 0.2);
        tl.set("#gray", { opacity: 1 }, tt); tl.set("#hand1", { rotation: 300 }, tt); impact(tt, 0.8);
        tl.fromTo("#stop", { opacity: 0, scale: 2 }, { opacity: 1, scale: 1, duration: 0.15, ease: "power4.in" }, tt + 0.05);
        const tc = W("celui"); tl.set("#gray", { opacity: 0 }, tc); tl.to(["#clock", "#stop"], { opacity: 0, scale: 0.5, duration: 0.2 }, tc);
        const td = W("diver"); tl.fromTo("#title .t", { scale: 4, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -4, duration: 0.2, ease: "power4.in" }, td - 0.1); impact(td + 0.1, 1.4); speed(td + 0.1, 1.2); menace(td, 3.5, 3);
        tl.fromTo("#title .k", { opacity: 0, x: -300 }, { opacity: 1, x: 0, duration: 0.25, ease: "steps(5)" }, W("down") - 0.1);
        pop("#standon", W("down") + 0.2);
        tl.fromTo("#dd1", { y: 1300 }, { y: 0, duration: 0.35, ease: "back.out(1.4)" }, W("down")); anim("#dd1", 8, 10, W("down"), E(1));
        tl.fromTo("#user1", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.25, ease: "steps(4)" }, W("narciso") - 0.1);
        tl.to("#title", { y: -40, duration: 0.3 }, W("narciso")); }

      // ===== S2 Anasui
      { bg("#bgred", S(2)); tl.fromTo("#an2", { x: -700 }, { x: 0, duration: 0.3, ease: "steps(6)" }, S(2)); anim("#an2", 8, 8, S(2), E(2)); impact(S(2) + 0.3, 0.8);
        tl.fromTo("#biz", { scale: 3, opacity: 0, rotation: 8 }, { scale: 1, opacity: 1, rotation: -3, duration: 0.15, ease: "power4.in" }, W("bizarre") - 0.05); impact(W("bizarre") + 0.1, 0.7); impact(W("bizarre", 13) + 0.1, 1); glitch("#biz", W("bizarre", 13) + 0.15);
        pop("#tg1", W("cheveux") - 0.05); pop("#tg2", W("androgyne") - 0.05);
        const tm = W("meurtrier"); tl.to(["#tg1", "#tg2", "#biz"], { opacity: 0, duration: 0.15 }, tm - 0.2);
        tl.fromTo("#bars", { y: -1200 }, { y: 0, duration: 0.25, ease: "power4.in" }, tm - 0.1); impact(tm + 0.15, 1.2);
        tl.fromTo("#mug", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.2, ease: "back.out(3)" }, tm + 0.1);
        const tv = W("vingt"); tl.to(["#bars", "#mug", "#an2"], { opacity: 0, duration: 0.2 }, tv - 0.2);
        tl.fromTo(["#silA", "#silB"], { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.25, ease: "steps(4)" }, W("copine") - 0.3);
        tl.fromTo("#crack", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.2, ease: "back.out(3)" }, W("homme") - 0.1);
        const tdm = W("démonte"); const px = document.getElementById("pxs"); const r = rng(77);
        for (let i = 0; i < 28; i++) { const sx = (i < 14 ? 340 : 680) + r() * 80, sy = 540 + r() * 260; px.insertAdjacentHTML("beforeend", `<div class="px" id="px${i}" style="left:${Math.round(sx)}px;top:${Math.round(sy)}px"></div>`); tl.fromTo("#px" + i, { opacity: 0, x: 0, y: 0, rotation: 0 }, { opacity: 1, duration: 0.01 }, tdm); tl.to("#px" + i, { x: (r() - 0.5) * 900, y: (r() - 0.3) * 900, rotation: (r() - 0.5) * 720, opacity: 0, duration: 1.2, ease: "power2.out" }, tdm + 0.02); }
        tl.set(["#silA", "#silB", "#crack"], { opacity: 0 }, tdm); impact(tdm, 1.6); speed(tdm, 0.8);
        tl.fromTo("#litt", { scale: 3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.15, ease: "power4.in" }, W("littéralement") - 0.05); glitch("#litt", W("littéralement") + 0.2, 8); }

      // ===== S3 Stand card
      { bg("#bgalt", S(3)); rise("#card", S(3) + 0.05, -80);
        tl.fromTo("#dd3", { y: 900, scale: 0.6 }, { y: 0, scale: 1, duration: 0.4, ease: "back.out(1.3)" }, W("plongeur") - 0.3); anim("#dd3", 8, 8, S(3), E(3)); menace(W("plongeur"), 3, 7);
        impact(W("plongeur") + 0.05, 0.8);
        ["#rg1", "#rg2", "#rg3", "#rg4", "#rg5"].forEach((g, i) => tl.fromTo(g, { scale: 2.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.15, ease: "power3.out" }, W("partout") - 0.25 + i * 0.1));
        tl.to(".ring", { scale: 1.2, duration: 0.15, yoyo: true, repeat: 5, ease: "steps(2)" }, W("partout") + 0.4); }

      // ===== S4 store energy
      { bg("#bgred", S(4)); rise("#gauge", S(4) + 0.05, -60);
        tl.fromTo("#wall", { x: 600 }, { x: 0, duration: 0.3, ease: "steps(6)" }, S(4) + 0.1);
        tl.fromTo("#dd4", { x: -500 }, { x: 0, duration: 0.3, ease: "steps(6)" }, S(4) + 0.2);
        const tp = W("poing"); tl.fromTo("#dd4 img", { x: 0 }, { x: -1792, duration: 0.32, ease: "steps(4)" }, tp - 0.25); impact(tp + 0.07, 1.3); speed(tp, 0.5);
        tl.to("#hpR", { scaleX: 0.75, duration: 0.2, ease: "steps(3)" }, tp + 0.07);
        tl.fromTo("#core", { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.3 }, W("impact") - 0.1);
        tl.to("#core", { scale: 1.25, duration: 0.2, yoyo: true, repeat: 7, ease: "sine.inOut" }, W("impact") + 0.2);
        tl.fromTo("#gfill", { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: "steps(10)" }, W("impact") - 0.1);
        const te = W("exploser"); const bk = document.getElementById("bricks"); const r = rng(31);
        for (let i = 0; i < 18; i++) { bk.insertAdjacentHTML("beforeend", `<div class="brick" id="bk${i}" style="left:${620 + (i % 5) * 80}px;top:${540 + Math.floor(i / 5) * 140}px"></div>`); tl.fromTo("#bk" + i, { opacity: 0 }, { opacity: 1, duration: 0.01 }, te); tl.to("#bk" + i, { x: (r() - 0.6) * 1000, y: (r() - 0.4) * 900, rotation: (r() - 0.5) * 540, opacity: 0, duration: 1, ease: "power2.out" }, te + 0.02); }
        tl.set(["#wall", "#core"], { opacity: 0 }, te); impact(te, 1.8); speed(te, 0.9);
        tl.fromTo("#boom", { scale: 4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.15, ease: "power4.in" }, te); tl.to("#hpR", { scaleX: 0.35, duration: 0.25, ease: "steps(4)" }, te + 0.05); }

      // ===== S5 dive
      { bg("#bgalt", S(5)); tl.fromTo("#crate", { y: 900 }, { y: 0, duration: 0.3, ease: "back.out(1.5)" }, S(5)); anim("#dd5", 8, 8, S(5), E(5));
        tl.fromTo("#dd5", { opacity: 0, y: -400 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, S(5) + 0.1);
        const tdv = W("plonge", 38); tl.to("#dd5", { y: 520, scaleY: 0.2, opacity: 0, duration: 0.3, ease: "power3.in" }, tdv - 0.1); speed(tdv, 0.5);
        ["#rp1", "#rp2", "#rp3"].forEach((p, i) => tl.fromTo(p, { scale: 1, opacity: 1 }, { scale: 9, opacity: 0, duration: 0.8, ease: "power2.out" }, tdv + 0.15 + i * 0.15));
        tl.to("#crate", { scaleX: 1.08, scaleY: 0.92, duration: 0.1, yoyo: true, repeat: 3 }, tdv + 0.2);
        const tpe = W("personne", 41); tl.to("#crate", { opacity: 0, duration: 0.2 }, tpe - 0.3);
        tl.fromTo("#jx", { opacity: 0, x: 500 }, { opacity: 1, x: 0, duration: 0.3, ease: "steps(5)" }, tpe - 0.3); anim("#jx", 8, 8, tpe - 0.3, E(5));
        tl.fromTo("#xray", { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.25, ease: "steps(4)" }, W("intérieur", 42.5) - 0.1); impact(W("intérieur", 42.5), 0.7);
        ["#g1", "#g2", "#g3"].forEach((g, i) => tl.fromTo(g, { rotation: 0 }, { rotation: i % 2 ? -720 : 720, duration: 4, ease: "none" }, W("modifier") - 0.4));
        tl.to("#xray", { x: 12, duration: 0.05, yoyo: true, repeat: 7 }, W("réassembler"));
        pop("#wrench", W("mécanicien") - 0.1); }

      // ===== S6 Jolyne + Jotaro
      { bg("#bgred", S(6)); tl.fromTo("#an6", { x: -500 }, { x: 0, duration: 0.3, ease: "steps(5)" }, S(6)); anim("#an6", 8, 8, S(6), E(6));
        tl.fromTo("#jo6", { x: 500 }, { x: 0, duration: 0.3, ease: "steps(5)" }, W("jolyne") - 0.25); anim("#jo6", 8, 8, S(6), E(6)); impact(W("jolyne") + 0.05, 0.8);
        ["#h1", "#h2", "#h3"].forEach((h, i) => { tl.fromTo(h, { scale: 0, opacity: 0, y: 0 }, { scale: 1, opacity: 1, y: -60, duration: 0.3, ease: "back.out(3)" }, W("épouser") - 0.2 + i * 0.12); tl.to(h, { scale: 1.2, duration: 0.15, yoyo: true, repeat: 3 }, W("épouser") + 0.3 + i * 0.1); });
        pop("#ringbox", W("épouser"));
        const tj = W("jotaro"); tl.to(["#an6", "#jo6", ".heart", "#ringbox"], { opacity: 0.15, duration: 0.15 }, tj - 0.2);
        tl.fromTo("#jt6", { y: -1400 }, { y: 0, duration: 0.2, ease: "power4.in" }, tj - 0.15); anim("#jt6", 8, 6, tj - 0.15, E(6)); impact(tj + 0.05, 1.6); menace(tj, 1.8, 11);
        tl.fromTo("#dots3", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "steps(3)" }, tj + 0.4); }

      // ===== S7 verdict
      { bg("#bgalt", S(7)); tl.fromTo("#an7", { x: -500 }, { x: 0, duration: 0.3, ease: "steps(5)" }, S(7)); anim("#an7", 8, 8, S(7), E(7));
        tl.fromTo("#dd7", { x: 600 }, { x: 0, duration: 0.3, ease: "steps(5)" }, S(7) + 0.1); anim("#dd7", 8, 10, S(7), E(7)); impact(S(7) + 0.35, 1); menace(S(7), 3, 21);
        rise("#ratings", W("discret") - 0.2, 60);
        tl.fromTo("#ra1", { opacity: 0 }, { opacity: 1, duration: 0.01 }, W("discret"));
        tl.fromTo("#ra2", { opacity: 0 }, { opacity: 1, duration: 0.01 }, W("créatifs") - 0.1); impact(W("créatifs"), 0.8);
        tl.to("#hpR", { scaleX: 0, duration: 0.3, ease: "steps(4)" }, W("créatifs")); }

      // ===== S8 CTA + To Be Continued
      { bg("#bgred", S(8)); pop("#sub", S(8) + 0.05);
        tl.fromTo("#ptr", { x: 200, y: 200 }, { x: 0, y: 0, duration: 0.5, ease: "steps(8)" }, S(8) + 0.3);
        tl.to("#sub", { scale: 0.92, duration: 0.08, yoyo: true, repeat: 1 }, S(8) + 0.85);
        tl.set("#sub", { backgroundColor: "#555a70" }, S(8) + 0.95); tl.set("#sub1", { opacity: 0 }, S(8) + 0.95); tl.set("#sub2", { opacity: 1 }, S(8) + 0.95);
        rise("#next", W("commentaire") - 0.5, 80);
        document.querySelectorAll("#grid .c").forEach((c, i) => tl.fromTo(c, { opacity: 0, x: i % 2 ? 60 : -60 }, { opacity: 1, x: 0, duration: 0.2, ease: "steps(3)" }, W("commentaire") - 0.3 + i * 0.1));
        const tb = E(8) - 1.6; tl.fromTo("#tbc", { x: -700 }, { x: 0, duration: 0.35, ease: "power3.out" }, tb); tl.set("#gray", { opacity: 1 }, tb + 0.4); }

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
