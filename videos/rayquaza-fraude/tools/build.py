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
VO_OFFSET = 0.2  # la voix démarre à 0.2 s dans la vidéo
TOTAL = 87.0

# début (global) de chaque scène ; la suivante démarre à la fin de la précédente
STARTS = {
    "s01": 0.0, "s02": 3.35, "s03": 6.5, "s04": 14.2, "s05": 16.75, "s06": 24.5,
    "s07": 27.0, "s08": 34.5, "s09": 42.0, "s10": 46.2, "s11": 52.6, "s12": 57.2,
    "s13": 62.35, "s14": 68.15, "s15": 75.0, "s16": 78.2,
}
# cris officiels (PokéAPI) : (fichier, début global, durée, volume)
CRIES = [
    ("rayquaza-legacy", 0.0, 1.37, 0.1),
    ("chenipan-legacy", 4.45, 0.39, 0.2),
    ("groudon-legacy", 42.1, 1.74, 0.2),
    ("kyogre-legacy", 42.9, 1.68, 0.2),
    ("rayquaza-legacy", 56.7, 1.37, 0.18),
    ("deoxys-legacy", 64.0, 0.98, 0.22),
    ("deoxys-legacy", 70.1, 0.98, 0.2),
    ("rayquaza-legacy", 71.3, 1.37, 0.2),
    ("deoxys-legacy", 80.15, 0.98, 0.22),
    ("chenipan-legacy", 85.75, 0.39, 0.5),
]
NAMES = {
    "s01": "accusation", "s02": "promesse", "s03": "pub", "s04": "bilan", "s05": "arme-ultime",
    "s06": "absent", "s07": "personne", "s08": "fiche-de-poste", "s09": "primo", "s10": "rituel",
    "s11": "ola", "s12": "defense-spatiale", "s13": "cristal", "s14": "larousse", "s15": "robots",
    "s16": "ko-chenipan",
}

FONTS = """
@font-face{font-family:"Archivo Black";src:url(assets/fonts/ArchivoBlack.woff2) format("woff2")}
@font-face{font-family:"Press Start 2P";src:url(assets/fonts/PressStart2P.woff2) format("woff2")}
@font-face{font-family:"Space Mono";font-weight:400;src:url(assets/fonts/SpaceMono-Regular.woff2) format("woff2")}
@font-face{font-family:"Space Mono";font-weight:700;src:url(assets/fonts/SpaceMono-Bold.woff2) format("woff2")}
"""

PRELUDE_CSS = FONTS + """
.px{position:absolute;display:block;image-rendering:pixelated;image-rendering:crisp-edges}
.abs{position:absolute}
.disp{position:absolute;font-family:"Archivo Black";text-transform:uppercase;line-height:.92;letter-spacing:-.03em;color:#F3F1E4}
.pix{position:absolute;font-family:"Press Start 2P";line-height:1.35;color:#F3F1E4}
.mono{font-family:"Space Mono"}
.stamp{position:absolute;font-family:"Archivo Black";text-transform:uppercase;color:#E23B3B;border:16px solid #E23B3B;border-radius:22px;padding:4px 34px;letter-spacing:.02em;line-height:1.05}
.ghost{position:absolute;font-family:"Archivo Black";color:#fff;opacity:.07;white-space:nowrap;line-height:.8;text-transform:uppercase}
.gstack{display:grid}
.gstack>*{grid-area:1/1}
.gb{position:relative;z-index:2}
.gc{z-index:1;opacity:0;mix-blend-mode:screen}
.gc.w{color:#ff3b6b}.gc.c{color:#3bd5ff}
.cam{position:absolute;inset:0}
"""

PRELUDE_JS = """
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
const breathe = (el, t, dur, amp = 14, period = 1.6) => tl.fromTo(el, { y: 0 }, { y: -amp, duration: period / 2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / (period / 2)) - 1) }, t);
"""


def lane(points):
    """Lane de volume au format data-automation, échappée pour un attribut HTML."""
    js = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": t, "v": v} for t, v in points]}]})
    return js.replace('"', "&quot;")


# musique A : de 0 à « Ok. » (coupe nette) ; musique B : reprend après le plan fixe
MUSIC_A = lane([(0, 0.36), (13.95, 0.36), (14.15, 0)])
# t en secondes depuis le début du clip B (16.75 s) : on baisse pendant l'anti-évolution,
# on remonte après la révélation de Chenipan, puis fondu final
MUSIC_B = lane([(0, 0.36), (66.4, 0.36), (66.9, 0.25), (68.9, 0.25), (69.0, 0.62), (69.85, 0.62), (70.25, 0)])


def caption_style():
    """Sous-titres : police Pokémon (logo) si un fichier assets/fonts/pokemon*.{ttf,otf,woff,woff2} existe."""
    found = sorted(glob.glob(os.path.join(ROOT, "assets", "fonts", "[Pp]okemon*")))
    if found:
        rel = os.path.relpath(found[0], ROOT).replace(os.sep, "/")
        fmt = {"ttf": "truetype", "otf": "opentype", "woff": "woff", "woff2": "woff2"}[rel.rsplit(".", 1)[1].lower()]
        css = (f'@font-face{{font-family:"Pokemon Sous-titres";src:url({rel}) format("{fmt}")}}\n'
               '#cap-wrap{--cap-font:"Pokemon Sous-titres","Archivo Black";--cap-size:84px;--cap-case:none;'
               '--cap-fill:#FFCB05;--cap-stroke:12px #2A75BB;--cap-shadow:drop-shadow(0 7px 0 #1d3c7a)}')
        return css, "#FFCB05", "#ffffff"
    css = ('#cap-wrap{--cap-font:"Archivo Black";--cap-size:76px;--cap-case:uppercase;'
           '--cap-fill:#fff;--cap-stroke:13px #0a0a0a;--cap-shadow:none}')
    return css, "#ffffff", "#F4C430"


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
{PRELUDE_JS}
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
        f'    <audio id="cri-{i:02d}-{f}" src="assets/audio/cris/{f}.ogg" data-start="{t}" data-duration="{d}" data-track-index="{12 if f.startswith('kyogre') else 11}" data-volume="{v}"></audio>'
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
    <div id="slot-overlay" data-composition-id="overlay" data-composition-src="compositions/overlay.html" data-start="0" data-duration="{TOTAL}" data-track-index="3" data-width="1080" data-height="1920"></div>
    <div id="slot-captions" data-track-kind="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-width="1080" data-height="1920"></div>
{cries}
    <audio id="musique-a" src="assets/audio/musique/rayquaza-battle.mp3" data-start="0" data-duration="14.15" data-media-start="14.0" data-track-index="13" data-volume="0.36" data-automation="{MUSIC_A}"></audio>
    <audio id="musique-b" src="assets/audio/musique/rayquaza-battle.mp3" data-start="16.75" data-duration="70.25" data-media-start="28.15" data-track-index="13" data-volume="0.36" data-automation="{MUSIC_B}"></audio>
    <audio id="bruitages" src="assets/audio/bruitages/bruitages-stem.wav" data-start="0" data-duration="{TOTAL}" data-track-index="14" data-volume="0.55"></audio>
    <audio id="voix" src="assets/audio/voix/prise-1.mp3" data-start="{VO_OFFSET}" data-duration="82.76" data-track-index="10" data-volume="1"></audio>
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
