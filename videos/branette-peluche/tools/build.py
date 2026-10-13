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
    "s01": 0.0, "s02": 2.3, "s03": 8.1, "s04": 17.85, "s05": 24.45, "s06": 29.8, "s07": 32.55, "s08": 35.85,
    "s09": 39.85, "s10": 49.5, "s11": 55.0, "s12": 58.6, "s13": 61.6, "s14": 66.2, "s15": 68.4, "s16": 74.45,
}
NAMES = {
    "s01": "porte", "s02": "peluche", "s03": "souvenir", "s04": "benne", "s05": "lit", "s06": "fermeture",
    "s07": "brulee-enterree-noyee", "s08": "elle-revient", "s09": "pokedex", "s10": "energie-maudite",
    "s11": "elle-s-echappe", "s12": "trois-crans", "s13": "nuit", "s14": "yeux", "s15": "reveil", "s16": "porte-ouverte",
}

FONTS = """
@font-face{font-family:"Pixel";src:url(assets/fonts/sous-titres.ttf) format("truetype")}
"""

PRELUDE_CSS = FONTS + """
.px{position:absolute;display:block;image-rendering:pixelated;image-rendering:crisp-edges}
.abs{position:absolute}
.pix{position:absolute;font-family:"Pixel";line-height:1.3;color:#e8f3ff;text-transform:uppercase}
.cam{position:absolute;inset:0}
/* plans fixes en pixel art sombre */
.bg{position:absolute;left:0;top:0;width:1080px;height:1920px;image-rendering:pixelated}
.spr{position:absolute;image-rendering:pixelated;image-rendering:crisp-edges;background-repeat:repeat-x}
.vignette{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 38%,#000000e6 100%)}
.flash{position:absolute;inset:0;background:#fff;opacity:0}
.black{position:absolute;inset:0;background:#000;opacity:0}
.rain{position:absolute;inset:0;background:url(assets/decor/pluie.png) 0 0/256px 256px repeat;image-rendering:pixelated}
.sepia{filter:sepia(1) brightness(.75) contrast(1.15)}
.film{position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 160px,#00000014 160px 163px,transparent 163px 410px);mix-blend-mode:multiply}
.lid{position:absolute;background:#000;left:0;right:0;height:1100px}
.dex{position:absolute;font-family:"Pixel";color:#bfe8ff;text-transform:uppercase;line-height:1.35}
.drop{position:absolute;width:8px;height:16px;background:#7f9cc8;opacity:0}
.ember{position:absolute;width:10px;height:10px;background:#ff9a3c;box-shadow:0 0 12px #ff6a1a;opacity:0}
.smoke{position:absolute;border-radius:50%;background:radial-gradient(#3a0a4acc,#1a0524 55%,transparent 72%);opacity:0}
[id$="-all"]{position:absolute;inset:0}
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
const breathe = (el, t, dur, amp = 14, period = 1.6) => tl.fromTo(el, { y: 0 }, { y: -amp, duration: period / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (period / 2)) - 1) }, t);
"""


# l'OST est une boucle de 25,87 s : on démarre au début d'un tour (après le silence de 24,75–26,39 s)
OST_START = 26.394


def caption_style():
    """Sous-titres : police pixel (avec accents FR), blanc cassé contour nuit, mot prononcé rouge sang."""
    px = 9
    ring = [(x, y) for x in (-px, 0, px) for y in (-px, 0, px) if (x, y) != (0, 0)]
    outline = ",".join(f"{x}px {y}px 0 #0b1020" for x, y in ring)
    outline += f",0 {2 * px}px 0 #05070d"
    css = ('#cap-wrap{--cap-font:"Pixel";--cap-size:72px;--cap-case:uppercase;'
           f'--cap-gap:.55em;--cap-fill:#dfe9f5;--cap-stroke:0px transparent;--cap-shadow:none;--cap-tshadow:{outline}}}')
    return css, "#e6e2ec", "#ff3b4a"


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
    index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; background: #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(slots)}
    <div id="slot-captions" data-track-kind="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-width="1080" data-height="1920"></div>
    <audio id="musique" src="assets/audio/musique/ost.m4a" data-start="0" data-duration="{TOTAL}" data-media-start="{OST_START}" data-track-index="13" data-volume="0.9"></audio>
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
