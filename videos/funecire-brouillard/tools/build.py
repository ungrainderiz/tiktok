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
# = 2 tours exacts de la boucle de l'OST (25,87 s) : la musique se raccorde à la relance
TOTAL = 51.74

# début (global) de chaque scène ; la suivante démarre à la fin de la précédente
STARTS = {
    "s01": 0.0, "s02": 2.2, "s03": 8.2, "s04": 13.45, "s05": 15.8, "s06": 20.85, "s07": 21.6,
    "s08": 28.75, "s09": 34.5, "s10": 40.35, "s11": 41.95, "s12": 46.3, "s13": 48.15,
}
# cris officiels (PokéAPI) : (fichier, début global, durée, volume)
CRIES = [
    ("funecire-legacy", 12.6, 1.0, 0.12),
    ("caninos-legacy", 18.0, 1.0, 0.25),
    ("funecire-legacy", 39.4, 1.0, 0.1),
]
NAMES = {
    "s01": "lumiere", "s02": "perdu", "s03": "funecire", "s04": "recule", "s05": "caninos", "s06": "erreur",
    "s07": "froid", "s08": "pokedex", "s09": "genoux", "s10": "visage", "s11": "chaleur", "s12": "brilles",
    "s13": "dresseur",
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
  background:url(assets/decor/chemin.png) 50% 0/512px 256px repeat-y,url(assets/decor/herbe.png) 0 0/256px 256px repeat}
.bb{position:absolute;left:0;top:0;image-rendering:pixelated;image-rendering:crisp-edges}
.spr{position:absolute;image-rendering:pixelated;image-rendering:crisp-edges;background-repeat:repeat-x}
.sky{position:absolute;inset:0;background:linear-gradient(#070b16 0%,#141c30 26%,#2a3448 36%,#151b28 60%,#0a0e17 100%)}
.fogband{position:absolute;left:0;right:0;top:520px;height:420px;background:linear-gradient(transparent,#3a465ccc 45%,#2a3346aa 60%,transparent)}
.fogcloud{position:absolute;border-radius:50%;background:radial-gradient(#8fa0b866,transparent 70%)}
.vignette{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 45%,#000000d0 100%)}
.rain{position:absolute;inset:-200px;background:repeating-linear-gradient(100deg,transparent 0 46px,#b9c9e026 46px 49px),repeating-linear-gradient(100deg,transparent 0 83px,#b9c9e01a 83px 85px);pointer-events:none}
.loopcard{position:absolute;inset:0;background:radial-gradient(circle at 50% 700px,#ffd27a 0,#ff9a3c88 9px,#ffb34722 26px,transparent 60px),radial-gradient(ellipse at 50% 690px,#3a465c 0,#202839 45%,#0a0e17 100%)}
.flamebox{position:absolute;inset:0;box-shadow:inset 0 0 160px 40px #ff8a2a88;pointer-events:none}
.glow{position:absolute;border-radius:50%;background:radial-gradient(#ffd27acc 0,#ff9a3c66 25%,transparent 65%)}
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
  const m = SPR[name + "-sheet.png"]; const w = m.w * scale;
  gsap.set(el, { width: w, height: m.h * scale, backgroundImage: `url(assets/sprites/${name}-sheet.png)`, backgroundSize: `${m.frames * w}px ${m.h * scale}px` });
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
      const near = zz > 420 ? Math.max(0, 1 - (zz - 420) / 160) : 1;
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
      const img = document.createElement("img"); img.className = "bb"; img.src = "assets/decor/sapin.png"; img.alt = "";
      img.style.width = Math.round(w * (0.8 + hash(seed * 7 + i * 3 + side) * 0.7)) + "px";
      Wd.appendChild(img);
      out.push({ el: img, x: side * (xMin + hash(seed * 11 + i * 5 + side * 3) * xRange), z: z0 - i * gap - hash(seed + i) * gap * 0.5 });
    });
  }
  return out;
};
const rain = (el, start, dur) => tl.fromTo(el, { backgroundPosition: "0px 0px" }, { backgroundPosition: `${-Math.round(dur * 160)}px ${Math.round(dur * 1400)}px`, duration: dur, ease: "none" }, start);
const breathe = (el, t, dur, amp = 14, period = 1.6) => tl.fromTo(el, { y: 0 }, { y: -amp, duration: period / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (period / 2)) - 1) }, t);
"""


# l'OST est une boucle de 25,87 s : on démarre au début d'un tour (après le silence de 24,75–26,39 s)
OST_START = 26.394


def caption_style():
    """Sous-titres : police pixel (avec accents FR), blanc bleuté contour nuit, mot prononcé couleur flamme."""
    px = 9
    ring = [(x, y) for x in (-px, 0, px) for y in (-px, 0, px) if (x, y) != (0, 0)]
    outline = ",".join(f"{x}px {y}px 0 #0b1020" for x, y in ring)
    outline += f",0 {2 * px}px 0 #05070d"
    css = ('#cap-wrap{--cap-font:"Pixel";--cap-size:72px;--cap-case:uppercase;'
           f'--cap-gap:.55em;--cap-fill:#dfe9f5;--cap-stroke:0px transparent;--cap-shadow:none;--cap-tshadow:{outline}}}')
    return css, "#dfe9f5", "#ffb347"


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
    cries = "\n".join(
        f'    <audio id="cri-{i:02d}-{f}" src="assets/audio/cris/{f}.ogg" data-start="{t}" data-duration="{d}" data-track-index="11" data-volume="{v}"></audio>'
        for i, (f, t, d, v) in enumerate(CRIES)
    )
    index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0B1F17; }}
      #root {{ position: relative; width: 100%; height: 100%; background: #0B1F17; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(slots)}
    <div id="slot-captions" data-track-kind="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-width="1080" data-height="1920"></div>
{cries}
    <audio id="musique" src="assets/audio/musique/ost.m4a" data-start="0" data-duration="{TOTAL}" data-media-start="{OST_START}" data-track-index="13" data-volume="0.55"></audio>
    <audio id="bruitages" src="assets/audio/bruitages/bruitages-stem.wav" data-start="0" data-duration="{TOTAL}" data-track-index="14" data-volume="0.6"></audio>
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
