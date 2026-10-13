#!/usr/bin/env python3
"""Génère compositions/*.html et index.html à partir de tools/scenes/*.src.

Chaque fichier .src contient une ou plusieurs scènes :

    @@@ s01
    @bg <css background>
    <style>…</style>
    …markup…
    @@@js
    …corps du timeline (tl, S0, W(t), hash, shake, glitch, pop disponibles)…

W(t) convertit un temps de mot du transcript (voix brute) en temps local de la scène.
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO_OFFSET = 0.0  # la voix démarre dès 0 s (boucle)
# = 3 tours exacts de la boucle de l'OST (25,87 s) : la musique se raccorde à la relance
TOTAL = 77.61

# début (global) de chaque scène ; la suivante démarre à la fin de la précédente
STARTS = {
    "s01": 0.0, "s02": 4.0, "s03": 5.25, "s04": 12.5, "s05": 15.55, "s06": 21.55, "s07": 23.25, "s08": 27.55,
    "s09": 33.9, "s10": 38.15, "s11": 42.5, "s12": 49.05, "s13": 54.7, "s14": 60.25, "s15": 66.55, "s16": 72.35,
}
NAMES = {
    "s01": "horloge", "s02": "tictac", "s03": "foret", "s04": "silence", "s05": "main", "s06": "noxine",
    "s07": "piqure", "s08": "fil", "s09": "milliers", "s10": "arbre-de-vie", "s11": "nox", "s12": "deux-cents-ans",
    "s13": "tout", "s14": "gris", "s15": "envers", "s16": "offert",
}

FONTS = """
@font-face{font-family:"Pixel";src:url(assets/fonts/sous-titres.ttf) format("truetype")}
"""

PRELUDE_CSS = FONTS + """
.px{position:absolute;display:block;image-rendering:pixelated;image-rendering:crisp-edges}
.abs{position:absolute}
.pix{position:absolute;font-family:"Pixel";line-height:1.3;color:#e8f3ff;text-transform:uppercase}
.cam{position:absolute;inset:0}
/* monde 3D façon Noir/Blanc : sol en perspective + panneaux posés en profondeur */
.stage{position:absolute;inset:0;perspective:700px;perspective-origin:50% 36%;overflow:hidden}
.world{position:absolute;left:540px;top:691px;transform-style:preserve-3d}
.ground{position:absolute;left:-2500px;top:260px;width:5000px;height:9000px;transform-origin:50% 0;
  transform:translateZ(650px) rotateX(-90deg);image-rendering:pixelated;
  background:url(assets/sprites/chemin.png) 50% 0/512px 256px repeat-y,url(assets/sprites/sol.png) 0 0/256px 256px repeat}
.bb{position:absolute;left:0;top:0;image-rendering:pixelated;image-rendering:crisp-edges}
.spr{position:absolute;image-rendering:pixelated;image-rendering:crisp-edges;background-repeat:repeat-x}
.sky{position:absolute;inset:0;background:linear-gradient(#7fd3e8 0%,#b9ecd0 26%,#e8f6c8 36%,#4f8f4a 37%,#2c5a30 100%)}
.canopy{position:absolute;left:-40px;right:-40px;top:-60px;height:520px;background:
  radial-gradient(circle at 10% 60%,#2f7d3c 0 120px,transparent 122px),radial-gradient(circle at 32% 30%,#3a8f44 0 150px,transparent 152px),
  radial-gradient(circle at 58% 55%,#2c7438 0 140px,transparent 142px),radial-gradient(circle at 84% 35%,#3a8f44 0 160px,transparent 162px),
  radial-gradient(circle at 100% 70%,#2f7d3c 0 120px,transparent 122px),linear-gradient(#245f30,#2f7d3c 60%,transparent)}
.rays{position:absolute;inset:0;background:repeating-linear-gradient(105deg,transparent 0 120px,#fff8c81a 120px 180px,transparent 180px 300px);mix-blend-mode:screen}
.mote{position:absolute;width:12px;height:12px;background:#9ff7d8;box-shadow:0 0 14px 4px #5fe3c088}
.vignette{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 50%,#000000b0 100%)}
.frost{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 40%,#bfe9ff66 72%,#effbffdd 100%)}
.clock{position:absolute;left:-10px;top:410px;width:1100px;height:1100px}
.clock .face{position:absolute;inset:0;image-rendering:pixelated}
.clock .hand{position:absolute;image-rendering:pixelated}
.card{position:absolute;background:#1b2238ee;border:8px solid #e0b04a;border-radius:18px;box-shadow:0 10px 0 #00000088,inset 0 0 0 4px #6b4a1a;padding:24px 32px}
.flash{position:absolute;inset:0;background:#fff;opacity:0}
[id$="-all"]{position:absolute;inset:0}
.tsvg{position:absolute;left:0;top:0;overflow:visible;filter:drop-shadow(0 0 8px #39c8ff) drop-shadow(0 0 22px #8a6cff)}
.thread{fill:none;stroke:#c8f4ff;stroke-linecap:round}
.pulse{fill:none;stroke:#ffffff;stroke-linecap:round}
.dust{position:absolute;width:14px;height:14px;background:#a7a7a7}
"""

PRELUDE_JS = """
const SPR = __SPRITES__;
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const shake = (target, start, dur, amp, seed = 1) => {
  const n = Math.max(2, Math.round(dur / 0.04));
  for (let i = 0; i < n; i++) {
    const k = 1 - i / n;
    tl.to(target, { x: (hash(seed * 31 + i * 7) * 2 - 1) * amp * k, y: (hash(seed * 17 + i * 13) * 2 - 1) * amp * k, duration: dur / n, ease: "none" }, start + (i * dur) / n);
  }
  tl.to(target, { x: 0, y: 0, duration: 0.04, ease: "none" }, start + dur);
};
const glitch = (stackSel, start, dur, maxSplit) => {
  const copies = gsap.utils.toArray(stackSel + " .gc");
  const amp = { a: 0 };
  tl.set(amp, { a: 1 }, start);
  tl.set(copies, { opacity: 0.85 }, start);
  tl.to(amp, { a: 0, duration: dur, ease: "power3.in", onUpdate: () => {
    const step = Math.floor(tl.time() / 0.05);
    copies.forEach((el, l) => gsap.set(el, { x: (hash(step * 13 + l * 7) * 2 - 1) * maxSplit * amp.a, y: (hash(step * 29 + l * 11) * 2 - 1) * maxSplit * 0.35 * amp.a }));
  } }, start);
  tl.set(copies, { x: 0, y: 0, opacity: 0 }, start + dur);
};
const pop = (el, t, d = 0.45, from = 0) => tl.fromTo(el, { scale: from, opacity: 0 }, { scale: 1, opacity: 1, duration: d, ease: "back.out(2.2)" }, t);
const slam = (el, t, from = 2.6, rot = 0) => tl.fromTo(el, { scale: from, opacity: 0, rotation: rot }, { scale: 1, opacity: 1, rotation: rot, duration: 0.24, ease: "power4.in" }, t);
// anime une planche de sprites (GIF officiel découpé) image par image, de façon déterministe
const sheet = (el, name, scale, start, dur) => {
  const m = SPR[name + ".png"]; const w = m.w * scale;
  gsap.set(el, { width: w, height: m.h * scale, backgroundImage: `url(assets/sprites/${name}.png)`, backgroundSize: `${m.frames * w}px ${m.h * scale}px` });
  const cyc = (m.frames * m.ms) / 1000; const n = Math.max(1, Math.ceil(dur / cyc));
  tl.fromTo(el, { backgroundPositionX: "0px" }, { backgroundPositionX: `${-m.frames * w}px`, duration: cyc, ease: `steps(${m.frames})`, repeat: n - 1 }, start);
};
// caméra subjective : props = [{ el, x, z, dy }] ; camZ > 0 = on avance ; le sol défile en même temps
const world = (groundSel, props) => {
  const ground = document.querySelector(groundSel);
  return (camZ, camX = 0) => {
    if (ground) gsap.set(ground, { backgroundPosition: `${50}% ${camZ}px, ${-camX}px ${camZ}px` });
    props.forEach((p) => {
      const zz = p.z + camZ;
      const fog = Math.min(1, Math.max(0, 1 - (-zz - 1500) / 4500));
      const near = zz > 200 ? Math.max(0, 1 - (zz - 200) / 200) : 1;
      gsap.set(p.el, { x: p.x - camX, y: 260 + (p.dy || 0), z: zz, xPercent: -50, yPercent: -100, opacity: fog * near * (p.alpha ?? 1) });
    });
  };
};
const walk = (update, start, dur, z0, z1, ease = "none", x0 = 0, x1 = 0) => {
  const cam = { z: z0, x: x0 };
  update(z0, x0);
  tl.fromTo(cam, { z: z0, x: x0 }, { z: z1, x: x1, duration: dur, ease, immediateRender: false, onUpdate: () => update(cam.z, cam.x) }, start);
};
// une seule mise à jour par image, calculée à partir du temps local (caméra + apparitions sans décalage d'ordre)
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const drive = (start, dur, fn) => { const o = { t: 0 }; fn(0); tl.fromTo(o, { t: 0 }, { t: dur, duration: dur, ease: "none", immediateRender: false, onUpdate: () => fn(o.t) }, start); };
const bob = (el, start, dur, amp = 10, step = 0.55) => tl.fromTo(el, { y: 0 }, { y: amp, duration: step / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (step / 2)) - 1), immediateRender: false }, start);
const flicker = (el, start, dur, lo = 0.7, seed = 1) => {
  const n = Math.max(2, Math.round(dur / 0.09));
  for (let i = 0; i < n; i++) tl.to(el, { opacity: lo + (1 - lo) * hash(seed * 13 + i * 7), duration: dur / n, ease: "none" }, start + (i * dur) / n);
};
// rangées de sapins de chaque côté du chemin (positions pseudo-aléatoires mais fixes)
const forest = (worldId, n, seed = 1, z0 = -200, gap = 420, xMin = 420, xRange = 520, w = 300) => {
  const Wd = document.getElementById(worldId); const out = [];
  for (let i = 0; i < n; i++) {
    [-1, 1].forEach((side) => {
      const img = document.createElement("img"); img.className = "bb"; img.src = `assets/sprites/arbre-${i % 3}.png`; img.alt = "";
      img.style.width = Math.round(w * (0.8 + hash(seed * 7 + i * 3 + side) * 0.7)) + "px";
      Wd.appendChild(img);
      out.push({ el: img, x: side * (xMin + hash(seed * 11 + i * 5 + side * 3) * xRange), z: z0 - i * gap - hash(seed + i) * gap * 0.5 });
    });
  }
  return out;
};
const rain = (el, start, dur) => tl.fromTo(el, { backgroundPosition: "0px 0px" }, { backgroundPosition: `${-Math.round(dur * 160)}px ${Math.round(dur * 1400)}px`, duration: dur, ease: "none" }, start);
// image fixe d'une planche : f(frame, t) pose la case voulue au temps t
const still = (el, name, scale = 1) => {
  const m = SPR[name + ".png"]; const w = m.w * scale;
  gsap.set(el, { width: w, height: m.h * scale, backgroundImage: `url(assets/sprites/${name}.png)`, backgroundSize: `${m.frames * w}px ${m.h * scale}px`, backgroundPositionX: "0px" });
  return (frame, t) => tl.set(el, { backgroundPositionX: `${-frame * w}px` }, t);
};
// fils de wakfu (SVG) : tracé progressif + impulsions qui remontent le long du fil
const NS = "http://www.w3.org/2000/svg";
const threadSvg = (parent, w = 1080, h = 1920, id = "") => {
  const s = document.createElementNS(NS, "svg");
  s.setAttribute("width", w); s.setAttribute("height", h); s.setAttribute("viewBox", `0 0 ${w} ${h}`);
  s.setAttribute("class", "tsvg"); if (id) s.id = id;
  parent.appendChild(s); return s;
};
const thread = (svg, d, w, start, dur, ease = "power1.inOut") => {
  const p = document.createElementNS(NS, "path");
  p.setAttribute("d", d); p.setAttribute("class", "thread"); p.setAttribute("stroke-width", w);
  svg.appendChild(p);
  const L = Math.ceil(p.getTotalLength());
  gsap.set(p, { strokeDasharray: `${L} ${L}`, strokeDashoffset: L });
  tl.to(p, { strokeDashoffset: 0, duration: dur, ease }, start);
  return p;
};
const pulse = (svg, d, w, start, dur, speed = 520, seed = 1) => {
  const p = document.createElementNS(NS, "path");
  p.setAttribute("d", d); p.setAttribute("class", "pulse"); p.setAttribute("stroke-width", w);
  svg.appendChild(p);
  const off = Math.round(hash(seed) * 90);
  gsap.set(p, { strokeDasharray: "22 90", strokeDashoffset: off });
  tl.fromTo(p, { strokeDashoffset: off }, { strokeDashoffset: off - Math.round(dur * speed), duration: dur, ease: "none" }, start);
  return p;
};
// courbe d'un fil qui monte en ondulant de (x0,y0) vers (x1,y1)
const wavy = (x0, y0, x1, y1, amp = 60, seed = 1) => {
  const n = 5; let d = `M${x0} ${y0}`;
  for (let i = 1; i <= n; i++) {
    const t = i / n; const x = x0 + (x1 - x0) * t; const y = y0 + (y1 - y0) * t;
    const s = (hash(seed * 7 + i) * 2 - 1) * amp * (1 - t * 0.6);
    const tp = (i - 0.5) / n; const cx = x0 + (x1 - x0) * tp + s; const cy = y0 + (y1 - y0) * tp;
    d += ` Q${cx.toFixed(1)} ${cy.toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)}`;
  }
  return d;
};
// texte qui s'écrit lettre par lettre entre a et b
const typeText = (el, str, a, b, cls = "") => {
  const chars = [...str];
  chars.forEach((ch, i) => {
    const sp = document.createElement("span"); sp.textContent = ch; sp.style.opacity = 0; if (cls) sp.className = cls;
    el.appendChild(sp); tl.set(sp, { opacity: 1 }, a + ((b - a) * i) / chars.length);
  });
};
// particules carrées (poussière, wakfu) posées au hasard mais de façon fixe
const motes = (parent, n, seed, box, cls = "mote") => {
  const out = [];
  for (let i = 0; i < n; i++) {
    const m = document.createElement("div"); m.className = cls;
    m.style.left = Math.round(box[0] + hash(seed * 13 + i * 3) * box[2]) + "px";
    m.style.top = Math.round(box[1] + hash(seed * 29 + i * 5) * box[3]) + "px";
    parent.appendChild(m); out.push(m);
  }
  return out;
};
const breathe = (el, t, dur, amp = 14, period = 1.6) => tl.fromTo(el, { y: 0 }, { y: -amp, duration: period / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (period / 2)) - 1) }, t);
"""


# horloge géante : cadran + 3 aiguilles qui tournent autour de leur pivot (sprites.json)
CLOCK_JS = """
const clockSet = (root) => {
  const H = {};
  [["heure", ".h-heure", "aiguille-heure.png"], ["minute", ".h-minute", "aiguille-minute.png"], ["seconde", ".h-seconde", "aiguille-seconde.png"]].forEach(([k, sel, file]) => {
    const m = SPR[file]; const el = root.querySelector(sel);
    gsap.set(el, { width: m.w, height: m.h, left: 550 - m.px, top: 550 - m.py, transformOrigin: `${m.px}px ${m.py}px` });
    H[k] = el;
  });
  // t = minutes depuis midi (négatif = avant midi) → angles des aiguilles
  return (min) => {
    gsap.set(H.minute, { rotation: (min * 6) % 360 });
    gsap.set(H.heure, { rotation: (min * 0.5) % 360 });
    gsap.set(H.seconde, { rotation: (min * 360) % 360 });
  };
};
"""

# l'OST est une boucle de 25,87 s : on démarre au début d'un tour (après le silence de 24,75–26,39 s)
OST_START = 26.394


def caption_style():
    """Sous-titres : police pixel (avec accents FR), blanc contour nuit, mot prononcé bleu wakfu."""
    px = 9
    ring = [(x, y) for x in (-px, 0, px) for y in (-px, 0, px) if (x, y) != (0, 0)]
    outline = ",".join(f"{x}px {y}px 0 #0b1020" for x, y in ring)
    outline += f",0 {2 * px}px 0 #05070d"
    css = ('#cap-wrap{--cap-font:"Pixel";--cap-size:72px;--cap-case:uppercase;'
           f'--cap-gap:.55em;--cap-fill:#dfe9f5;--cap-stroke:0px transparent;--cap-shadow:none;--cap-tshadow:{outline}}}')
    return css, "#eef6ff", "#7fe8ff"


def parse_sources():
    scenes = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "tools", "scenes", "*.src"))):
        text = open(path, encoding="utf-8").read()
        for block in re.split(r"^@@@ ", text, flags=re.M)[1:]:
            sid, rest = block.split("\n", 1)
            sid = sid.strip()
            bg = ""
            m = re.match(r"@bg (.*)\n", rest)
            if m:
                bg = m.group(1).strip()
                rest = rest[m.end():]
            markup, js = rest.split("@@@js\n", 1)
            scenes[sid] = (bg, markup.strip(), js.strip())
    return scenes


def ends():
    ids = sorted(STARTS, key=STARTS.get)
    out = {}
    for i, sid in enumerate(ids):
        nxt = STARTS[ids[i + 1]] if i + 1 < len(ids) else TOTAL
        out[sid] = round(nxt - STARTS[sid], 3)
    return out


SPRITES_JSON = json.dumps(json.load(open(os.path.join(ROOT, "assets", "sprites", "sprites.json"))))


def wrap(cid, bg, markup, js, start):
    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="UTF-8" /></head>
<body>
<template id="{cid}-template">
<style>
{PRELUDE_CSS}
#{cid}{{position:absolute;inset:0;overflow:hidden;background:{bg or 'transparent'}}}
</style>
<div id="{cid}" data-composition-id="{cid}" data-width="1080" data-height="1920">
{markup}
</div>
<script>
(() => {{
const tl = gsap.timeline({{ paused: true }});
const S0 = {start};
const W = (t) => +(t + {VO_OFFSET} - S0).toFixed(3);
const G = (g) => +(g - S0).toFixed(3);
{PRELUDE_JS.replace("__SPRITES__", SPRITES_JSON)}
{CLOCK_JS}
{js}
window.__timelines["{cid}"] = tl;
}})();
</script>
</template>
</body>
</html>
"""


def main():
    scenes = parse_sources()
    durs = ends()
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    slots = []
    for sid in sorted(STARTS, key=STARTS.get):
        fname = f"compositions/{sid}-{NAMES[sid]}.html"
        bg, markup, js = scenes.get(sid, ("#222", f'<div class="disp" style="left:60px;top:800px;font-size:90px">{sid} (à venir)</div>', ""))
        open(os.path.join(ROOT, fname), "w", encoding="utf-8").write(wrap(sid, bg, markup, js, STARTS[sid]))
        slots.append(f'    <div id="slot-{sid}" data-composition-id="{sid}" data-composition-src="{fname}" data-start="{STARTS[sid]}" data-duration="{durs[sid]}" data-track-index="1" data-width="1080" data-height="1920"></div>')
    words = json.load(open(os.path.join(ROOT, "transcript.json"), encoding="utf-8"))["words"]
    merged = []  # ponctuation isolée (« ? », « : ») recollée au mot précédent
    for w in words:
        if w["type"] != "word":
            continue
        if merged and re.fullmatch(r"[?:!…]+", w["text"]):
            merged[-1]["t"] += " " + w["text"] if w["text"] in "?:!" else w["text"]
            merged[-1]["e"] = round(w["end"] + VO_OFFSET, 3)
            continue
        merged.append({"t": w["text"], "s": round(w["start"] + VO_OFFSET, 3), "e": round(w["end"] + VO_OFFSET, 3)})
    for sid in ("overlay", "captions"):
        if sid in scenes:
            bg, markup, js = scenes[sid]
            js = js.replace("__WORDS__", json.dumps(merged, ensure_ascii=False))
            if sid == "captions":
                css, fill, hl = caption_style()
                markup = markup.replace("__CAPFONT__", css)
                js = js.replace("__CAP_FILL__", json.dumps(fill)).replace("__CAP_HL__", json.dumps(hl))
            open(os.path.join(ROOT, f"compositions/{sid}.html"), "w", encoding="utf-8").write(wrap(sid, bg, markup, js, 0))
    index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0b1020; }}
      #root {{ position: relative; width: 100%; height: 100%; background: #0b1020; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(slots)}
    <div id="slot-captions" data-track-kind="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-width="1080" data-height="1920"></div>
    <audio id="musique" src="assets/audio/musique/ost.m4a" data-start="0" data-duration="{TOTAL}" data-media-start="{OST_START}" data-track-index="13" data-volume="0.9"></audio>
    <audio id="bruitages" src="assets/audio/bruitages/bruitages-stem.wav" data-start="0" data-duration="{TOTAL}" data-track-index="14" data-volume="0.45"></audio>
    <audio id="voix" src="assets/audio/voix/voix.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(index)
    print("ok:", len(scenes), "sources;", json.dumps(durs))


if __name__ == "__main__":
    main()
