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
# = 28 mesures de la musique (97,6 BPM) : la musique repart sur un premier temps au raccord de boucle
TOTAL = 68.873
BEAT = 0.6149366
MUSIC_START = 0.2392  # premier temps de la mesure 1 dans le morceau

# début (global) de chaque scène ; la suivante démarre à la fin de la précédente
STARTS = {
    "s01": 0.0, "s02": 4.6, "s03": 11.3, "s04": 17.9, "s05": 23.3, "s06": 30.8, "s07": 44.7,
    "s08": 53.95, "s09": 61.6,
}
NAMES = {
    "s01": "accroche", "s02": "rappel", "s03": "question", "s04": "preuves", "s05": "preuve-tronconneuses",
    "s06": "preuve-oubli", "s07": "chainsaw-man", "s08": "verdict", "s09": "ouroboros",
}

FONTS = """
@font-face{font-family:"Anton";src:url(assets/fonts/anton.woff2) format("woff2")}
@font-face{font-family:"Inter";font-weight:600;src:url(assets/fonts/inter-latin-600-normal.woff2) format("woff2")}
@font-face{font-family:"Inter";font-weight:800;src:url(assets/fonts/inter-latin-800-normal.woff2) format("woff2")}
@font-face{font-family:"Inter";font-weight:900;src:url(assets/fonts/inter-latin-900-normal.woff2) format("woff2")}
"""

# direction artistique : noir profond, blanc, un seul accent rouge ; 3D CSS (perspective, preserve-3d)
PRELUDE_CSS = FONTS + """
.abs{position:absolute}
.cam{position:absolute;inset:0}
.persp{position:absolute;inset:0;perspective:1600px;perspective-origin:50% 42%}
.p3{position:absolute;transform-style:preserve-3d}
.bgfx{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 38%,#1c0d10 0,#0d0b0e 45%,#050506 100%)}
.floor{position:absolute;left:-1200px;top:1180px;width:3480px;height:2400px;transform-origin:50% 0;transform:rotateX(78deg);
  background-image:linear-gradient(#ffffff10 2px,transparent 2px),linear-gradient(90deg,#ffffff10 2px,transparent 2px);background-size:120px 120px;
  -webkit-mask-image:radial-gradient(ellipse at 50% 0,#000 0,transparent 70%);mask-image:radial-gradient(ellipse at 50% 0,#000 0,transparent 70%)}
.t{position:absolute;font-family:"Anton";color:#f4f1ee;text-transform:uppercase;letter-spacing:2px;line-height:.95;white-space:nowrap;
  text-shadow:1px 1px 0 #b9b4ae,2px 2px 0 #a39e98,3px 3px 0 #8c8781,4px 4px 0 #75716b,5px 5px 0 #5f5b56,6px 6px 0 #4a4642,0 18px 40px #000000cc}
.t.red{color:#ff2e2e;text-shadow:1px 1px 0 #d81f1f,2px 2px 0 #c01a1a,3px 3px 0 #a71515,4px 4px 0 #8e1111,5px 5px 0 #750d0d,6px 6px 0 #5c0909,0 18px 40px #000000cc}
.chip{position:absolute;font-family:"Inter";font-weight:800;font-size:34px;letter-spacing:6px;color:#ff2e2e;text-transform:uppercase;
  padding:12px 24px;border:3px solid #ff2e2e;border-radius:999px;background:#ff2e2e14;white-space:nowrap}
.card{position:absolute;border-radius:28px;overflow:hidden;background:#000;box-shadow:0 50px 90px #000000e0,0 0 0 2px #ffffff1c;backface-visibility:hidden}
.card video,.card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.card .shine{position:absolute;inset:0;background:linear-gradient(115deg,#ffffff1f 0,transparent 35%);pointer-events:none}
.strike{position:absolute;height:16px;background:#ff2e2e;border-radius:8px;box-shadow:0 0 30px #ff2e2e88;transform-origin:0 50%}
.flash{position:absolute;inset:0;background:#fff;opacity:0}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 50%,#000000d8 100%);pointer-events:none}
.ring{position:absolute;left:540px;top:820px;transform-style:preserve-3d}
.tooth{position:absolute;left:-26px;top:-470px;width:52px;height:70px;clip-path:polygon(0 100%,18% 22%,62% 0,100% 100%);
  background:linear-gradient(180deg,#ffffff 0,#cfc9c3 45%,#6f6a65 100%)}
.link{position:absolute;left:-20px;top:-408px;width:40px;height:46px;border-radius:10px;background:linear-gradient(180deg,#3a3a40,#16161a);box-shadow:inset 0 0 0 3px #ff2e2e55}
[id$="-all"]{position:absolute;inset:0}
"""

PRELUDE_JS = """
const SPR = {};\nconst TOTAL_ = __TOTAL__;
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
// une seule mise à jour par image, calculée à partir du temps local
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const drive = (start, dur, fn) => { const o = { t: 0 }; fn(0); tl.fromTo(o, { t: 0 }, { t: dur, duration: dur, ease: "none", immediateRender: false, onUpdate: () => fn(o.t) }, start); };
const bob = (el, start, dur, amp = 10, step = 0.55) => tl.fromTo(el, { y: 0 }, { y: amp, duration: step / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (step / 2)) - 1), immediateRender: false }, start);
const flicker = (el, start, dur, lo = 0.7, seed = 1) => {
  const n = Math.max(2, Math.round(dur / 0.09));
  for (let i = 0; i < n; i++) tl.to(el, { opacity: lo + (1 - lo) * hash(seed * 13 + i * 7), duration: dur / n, ease: "none" }, start + (i * dur) / n);
};
// image fixe d'une planche : f(frame, t) pose la case voulue au temps t
const still = (el, name, scale = 1) => {
  const m = SPR[name + ".png"]; const w = m.w * scale;
  gsap.set(el, { width: w, height: m.h * scale, backgroundImage: `url(assets/sprites/${name}.png)`, backgroundSize: `${m.frames * w}px ${m.h * scale}px`, backgroundPositionX: "0px" });
  return (frame, t) => tl.set(el, { backgroundPositionX: `${-frame * w}px` }, t);
};
// texte qui s'écrit lettre par lettre entre a et b
const typeText = (el, str, a, b, cls = "") => {
  const chars = [...str];
  chars.forEach((ch, i) => {
    const sp = document.createElement("span"); sp.textContent = ch; sp.style.opacity = 0; if (cls) sp.className = cls;
    el.appendChild(sp); tl.set(sp, { opacity: 1 }, a + ((b - a) * i) / chars.length);
  });
};
// particules carrées (gouttes, braises, fumée) posées au hasard mais de façon fixe
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
// anneau de chaîne de tronçonneuse (ouroboros) : N dents sur un cercle, couché en perspective.
// L'angle ne dépend que du temps GLOBAL et fait un nombre entier de crans sur toute la vidéo → boucle parfaite.
const RING_N = 40, RING_W = (360 / RING_N) * 153 / TOTAL_;
const ringBuild = (parent, id) => {
  const tilt = document.createElement("div"); tilt.className = "ring"; tilt.id = id;
  const spin = document.createElement("div"); spin.className = "p3"; spin.id = id + "-spin";
  for (let i = 0; i < RING_N; i++) {
    const l = document.createElement("div"); l.className = "link"; l.style.transform = `rotateZ(${i * 360 / RING_N + 4.5}deg)`; l.style.transformOrigin = "20px 408px"; spin.appendChild(l);
    const d = document.createElement("div"); d.className = "tooth"; d.style.transform = `rotateZ(${i * 360 / RING_N}deg)`; d.style.transformOrigin = "26px 470px"; spin.appendChild(d);
  }
  tilt.appendChild(spin); parent.appendChild(tilt);
  return { tilt, spin, at: (g) => gsap.set(spin, { rotationZ: (g * RING_W) % 360 }) };
};
// entrées / sorties 3D propres (perspective appliquée à chaque élément)
const flipIn = (el, t, d = 0.45, from = -90) => tl.fromTo(el, { rotationX: from, opacity: 0, y: 30, transformPerspective: 1200 }, { rotationX: 0, opacity: 1, y: 0, duration: d, ease: "back.out(1.4)" }, t);
const flipOut = (el, t, d = 0.3) => tl.to(el, { rotationX: 80, opacity: 0, y: -30, duration: d, ease: "power2.in", transformPerspective: 1200 }, t);
const slamIn = (el, t, from = 2.2) => tl.fromTo(el, { scale: from, opacity: 0, z: 300 }, { scale: 1, opacity: 1, z: 0, duration: 0.22, ease: "power4.in" }, t);
const cardIn = (el, t, rx = 18, ry = -35, d = 0.7) => tl.fromTo(el, { rotationX: rx, rotationY: ry, z: -700, opacity: 0 }, { rotationX: 0, rotationY: 0, z: 0, opacity: 1, duration: d, ease: "power3.out" }, t);
const cardOut = (el, t, ry = 35, d = 0.45) => tl.to(el, { rotationY: ry, z: -900, opacity: 0, duration: d, ease: "power2.in" }, t);
const strike = (el, t, d = 0.3) => tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: d, ease: "power3.out" }, t);
const fadeIn = (el, t, d = 0.3) => tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: d, ease: "power1.out" }, t);
const fadeOut = (el, t, d = 0.3) => tl.to(el, { opacity: 0, duration: d, ease: "power1.in" }, t);
const drift = (el, t, d, ry = 6, rx = 3) => tl.fromTo(el, { rotationY: -ry, rotationX: rx }, { rotationY: ry, rotationX: -rx, duration: d, ease: "sine.inOut" }, t);
const breathe = (el, t, dur, amp = 14, period = 1.6) => tl.fromTo(el, { y: 0 }, { y: -amp, duration: period / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (period / 2)) - 1) }, t);
"""




def caption_style():
    """Sous-titres : Inter extra-gras, blanc cassé avec ombre portée, mot prononcé rouge Chainsaw Man."""
    px = 9
    ring = [(x, y) for x in (-px, 0, px) for y in (-px, 0, px) if (x, y) != (0, 0)]
    outline = ",".join(f"{x}px {y}px 0 #0b1020" for x, y in ring)
    outline += f",0 {2 * px}px 0 #05070d"
    css = ('#cap-wrap{--cap-font:"Inter";--cap-size:70px;--cap-case:uppercase;'
           '--cap-gap:.32em;--cap-fill:#f4f1ee;--cap-stroke:0px transparent;--cap-shadow:none;'
           '--cap-tshadow:0 6px 0 #000,0 0 26px #000000cc}')
    return css, "#f4f1ee", "#ff2e2e"


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
{PRELUDE_JS.replace("__TOTAL__", str(TOTAL))}
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
        n = iter(range(1, 99))  # le moteur de rendu exige un id sur chaque <video> (sinon image figée)
        markup = re.sub(r'<video class="clip"', lambda m: f'<video id="{sid}-v{next(n)}" class="clip"', markup)
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
    for sid in ("fx", "captions"):
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #050506; }}
      #root {{ position: relative; width: 100%; height: 100%; background: #050506; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(slots)}
    <div id="slot-fx" data-composition-id="fx" data-composition-src="compositions/fx.html" data-start="0" data-duration="{TOTAL}" data-track-index="3" data-width="1080" data-height="1920"></div>
    <div id="slot-captions" data-track-kind="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-width="1080" data-height="1920"></div>
    <audio id="musique" src="assets/audio/musique/musique.m4a" data-start="0" data-duration="{TOTAL}" data-media-start="{MUSIC_START}" data-track-index="13" data-volume="0.55"></audio>
    <audio id="bruitages" src="assets/audio/bruitages/bruitages-stem.wav" data-start="0" data-duration="{TOTAL}" data-track-index="14" data-volume="0.4"></audio>
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
