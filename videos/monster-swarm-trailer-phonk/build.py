#!/usr/bin/env python3
"""Generates the Monster Swarm phonk trailer (horizontal 1920x1080) from shots.json + the copy below.

  index.html                French
  compositions/trailer-en.html  English  (render with: npx hyperframes render -c compositions/trailer-en.html ...)

Times are seconds on the 23.6s cut (assets/bgm.wav = the phonk track from 0.40s; 136 BPM, bar 1.765s).
Downbeats (local): 1.41 3.15 4.92 6.68 8.45 10.21 11.95 13.72 15.48 17.25 19.01 20.68.
The track drops out at ~20.1 and lands its last hit at 20.64 -> end card; music decays by ~22,
the card holds and the picture fades out at the end.

Re-run after editing shots.json or COPY:  python3 build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
DUR = 23.6
W, H = 1920, 1080
shots = json.loads((ROOT / "shots.json").read_text())

# (id, start, end, kind, {lang: lines})  kind: big = stacked slam words, kick = small caps line + big word.
# The last line of every card takes the accent colour.
COPY = [
    ("t01", 0.06, 1.41, "kick", {"fr": ["UN NOUVEAU", "ROGUELIKE"], "en": ["WELCOME TO", "THE SANCTUARY"]}),
    ("t02", 1.41, 3.15, "kick", {"fr": ["SUR", "ROBLOX"], "en": ["BUT OUTSIDE", "IT’S CHAOS"]}),
    ("t03", 4.92, 6.68, "big", {"fr": ["AFFRONTE", "LA HORDE"], "en": ["THOUSANDS", "OF MONSTERS"]}),
    ("t04", 6.68, 8.45, "big", {"fr": ["MONTE DE", "NIVEAU"], "en": ["LEVEL UP", "DRAW YOUR CARDS"]}),
    ("t05", 8.45, 10.21, "big", {"fr": ["DES VAGUES", "SANS FIN"], "en": ["STACK", "YOUR BUILD"]}),
    ("t06", 10.21, 11.95, "kick", {"fr": ["CHOISIS", "TON HÉROS"], "en": ["PICK", "YOUR CLASS"]}),
    ("t07", 11.95, 13.72, "big", {"fr": ["JUSQU’OÙ", "VAS-TU", "SURVIVRE ?"], "en": ["THE HORDE", "NEVER", "STOPS"]}),
    ("t08", 13.72, 15.48, "big", {"fr": ["EN SOLO OU", "ENTRE AMIS"], "en": ["BRING", "YOUR SQUAD"]}),
    ("t09", 17.25, 19.01, "big", {"fr": ["DES BOSS", "GÉANTS"], "en": ["FACE THE", "TITANS"]}),
]
END_CARD = {"fr": ("JOUE MAINTENANT", "SUR ROBLOX"), "en": ("PLAY NOW", "ON ROBLOX")}
LINE_BEATS = {
    "t03": [4.92, 5.36],
    "t07": [11.95, 12.39, 12.83],
    "t08": [13.72, 14.16],
    "t09": [17.25, 17.69],
}
# boss rush 15.48-19.01 cuts every beat, so it flashes on every cut
FLASHES = [(3.15, 1.0), (4.92, 0.5), (10.21, 0.4), (15.48, 0.9), (15.92, 0.35), (16.37, 0.35), (16.81, 0.35),
           (17.25, 0.6), (19.01, 0.5), (20.64, 1.0)]
SHAKES = [(3.15, 1.0), (4.92, 0.5), (8.45, 0.5), (11.95, 0.5), (15.48, 1.0), (15.92, 0.5), (16.37, 0.5),
          (16.81, 0.5), (17.25, 0.8), (18.13, 0.6), (19.01, 0.7), (20.64, 1.0), (20.94, 0.6)]
# shots that hold: no punch-in (opening establishing shot, end card bed)
CALM = {"h01", "h21"}

# sound effects: (file in assets/sfx, start, volume). Whooshes peak 0.15s in -> start 0.15s before the hit.
# Source: media-use bundled Pixabay library (assets/sfx/CREDITS.md).
SFX = [
    ("whoosh.wav", 1.26, 2.3),           # SUR ROBLOX
    ("riser-build.wav", 0.15, 1.2),      # build into the title hit
    ("impact.wav", 3.15, 1.0),           # MONSTER SWARM
    ("whoosh.wav", 4.77, 2.7),           # AFFRONTE LA HORDE
    ("sparkle.wav", 6.68, 1.5),          # MONTE DE NIVEAU
    ("whoosh.wav", 8.30, 2.5),           # DES VAGUES SANS FIN
    ("glitch.wav", 10.19, 1.2),          # CHOISIS TON HÉROS
    ("whoosh.wav", 11.80, 2.5),          # JUSQU'OÙ
    ("whoosh.wav", 12.68, 2.7),          # SURVIVRE
    ("whoosh.wav", 13.57, 2.5),          # EN SOLO OU ENTRE AMIS
    ("impact.wav", 15.48, 1.0),          # boss rush
    ("whoosh.wav", 15.77, 1.9),
    ("whoosh.wav", 16.22, 1.9),
    ("whoosh.wav", 16.66, 1.9),
    ("whoosh.wav", 17.10, 2.7),          # DES BOSS GÉANTS
    ("glitch.wav", 20.08, 1.4),          # drop-out before the last hit
    ("impact.wav", 20.64, 1.0),          # end card
    ("whoosh.wav", 20.79, 2.8),          # SWARM
    ("pop.wav", 21.30, 1.2),             # JOUE MAINTENANT
]
SFX_LEN = {"whoosh.wav": 0.57, "whoosh-reverse.wav": 0.57, "riser-build.wav": 3.0, "impact.wav": 1.4,
           "sparkle.wav": 1.8, "pop.wav": 0.72, "glitch.wav": 0.65}


def sfx_html():
    rows = []
    for i, (f, t, vol) in enumerate(SFX):
        d = min(SFX_LEN[f], DUR - t)
        rows.append(
            f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{t:.2f}" '
            f'data-duration="{d:.2f}" data-volume="{vol}" data-track-index="{11 + i % 3}"></audio>'
        )
    return "\n".join(rows)


def shot_html(sid, a, b):
    return (
        f'      <div class="shot" id="w-{sid}">\n'
        f'        <video id="v-{sid}" class="clip" src="assets/shots/{sid}.mp4" muted playsinline '
        f'data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="0"></video>\n'
        f"      </div>"
    )


def copy_html(tid, a, b, kind, lines):
    rows = []
    for i, ln in enumerate(lines):
        cls = "ln"
        if kind == "kick" and i == 0:
            cls += " kicker"
        if i == len(lines) - 1:
            cls += " accent"
        rows.append(f'        <div class="{cls}"><span class="w">{ln}</span></div>')
    body = "\n".join(rows)
    return (
        f'      <div class="clip card" id="{tid}" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
        f'data-track-index="2">\n{body}\n      </div>'
    )


def timeline_js():
    js = []
    for sid, a, b, *_ in shots:
        if sid in CALM:
            js.append(f'tl.fromTo("#w-{sid}", {{scale: 1.0}}, {{scale: 1.06, duration: {b - a:.2f}, ease: "none"}}, {a:.2f});')
            continue
        # punch-out on every cut + slow drift for the held shots
        js.append(f'tl.fromTo("#w-{sid}", {{scale: 1.14}}, {{scale: 1.0, duration: 0.3, ease: "expo.out"}}, {a:.2f});')
        if b - a > 1.2:
            js.append(f'tl.to("#w-{sid}", {{scale: 1.06, duration: {b - a - 0.3:.2f}, ease: "none"}}, {a + 0.3:.2f});')

    for tid, a, b, kind, lines in COPY:
        beats = LINE_BEATS.get(tid)
        for i in range(len(lines["fr"])):
            t = beats[i] if beats else a + i * 0.12
            sel = f"#{tid} .ln:nth-child({i + 1}) .w"
            js.append(
                f'tl.fromTo("{sel}", {{opacity: 0, scale: 1.9, rotation: {(-4 if i % 2 else 3)}}}, '
                f'{{opacity: 1, scale: 1, rotation: 0, duration: 0.16, ease: "power4.out"}}, {t:.2f});'
            )
        js.append(f'tl.to("#{tid} .w", {{opacity: 0, y: -40, duration: 0.12, ease: "power2.in"}}, {b - 0.12:.2f});')

    for t, k in FLASHES:
        js.append(f'tl.fromTo("#flash", {{opacity: {0.95 * k:.2f}}}, {{opacity: 0, duration: {0.2 + 0.3 * k:.2f}, ease: "power2.out", immediateRender: false}}, {t:.2f});')
    for t, k in SHAKES:
        a = 30 * k
        js.append(
            f'tl.fromTo("#cam", {{x: {a:.0f}, y: {-a * 0.6:.0f}, rotation: {0.6 * k:.2f}}}, '
            f'{{x: 0, y: 0, rotation: 0, duration: 0.35, ease: "elastic.out(1.2, 0.3)", immediateRender: false}}, {t:.2f});'
        )
    return js


TITLE_JS = """
// ---- title slam on the first big hit
tl.fromTo("#title1 .tw1", {opacity: 0, scale: 3, y: -80}, {opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power4.out"}, 3.15);
tl.fromTo("#title1 .tw2", {opacity: 0, scale: 3, y: 80}, {opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power4.out"}, 3.59);
tl.fromTo("#title1 .tbox", {scale: 1}, {scale: 1.1, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false}, 4.03);
tl.fromTo("#title1 .tbox", {filter: "drop-shadow(0 0 0px #ff2bd6)"}, {filter: "drop-shadow(0 0 60px #ff2bd6)", duration: 1.0, ease: "none", immediateRender: false}, 3.59);
tl.to("#title1 .tbox", {scale: 0.2, opacity: 0, duration: 0.14, ease: "power3.in"}, 4.78);
tl.fromTo("#dim3", {opacity: 0.3}, {opacity: 0.6, duration: 0.4, ease: "power2.out"}, 3.15);

// ---- drop-out: blackout between the last boss shot and the final hit
tl.fromTo("#blackout", {opacity: 0}, {opacity: 1, duration: 0.06, ease: "none"}, 20.10);

// ---- end card on the last hit, holds, picture fades out
tl.fromTo("#endcard .tw1", {opacity: 0, scale: 3}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 20.64);
tl.fromTo("#endcard .tw2", {opacity: 0, scale: 3}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 20.94);
tl.fromTo("#endcard .tbox", {filter: "drop-shadow(0 0 0px #ff2bd6)"}, {filter: "drop-shadow(0 0 50px #ff2bd6)", duration: 1.2, ease: "power1.out", immediateRender: false}, 20.94);
tl.fromTo("#endcard .cta", {opacity: 0, y: 60}, {opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)"}, 21.30);
tl.fromTo("#endcard .sub", {opacity: 0}, {opacity: 1, duration: 0.2, ease: "power1.out"}, 21.40);
tl.fromTo("#endcard .cta", {scale: 1}, {scale: 1.06, duration: 0.44, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false}, 21.70);
tl.fromTo("#dimEnd", {opacity: 0.2}, {opacity: 0.5, duration: 0.6, ease: "power1.out"}, 20.64);
tl.fromTo("#fade", {opacity: 0}, {opacity: 1, duration: 0.7, ease: "power1.in"}, 22.9);
"""


def build(lang):
    cta, sub = END_CARD[lang]
    js = timeline_js()
    return f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Monster Swarm — Phonk Trailer ({lang.upper()})</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); font-weight: 400; }}
      @font-face {{ font-family: "Inter"; src: url("assets/fonts/inter-latin-900-normal.woff2") format("woff2"); font-weight: 900; }}
      :root {{
        --ink: #0b0710;
        --white: #ffffff;
        --magenta: #ff2bd6;
        --yellow: #ffd21f;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: var(--ink); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--ink); }}
      #cam {{ position: absolute; inset: 0; }}
      .shot {{ position: absolute; inset: 0; }}
      .shot video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .layer {{ position: absolute; inset: 0; pointer-events: none; }}
      #grade {{ background: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 40%, rgba(8,0,20,0.6) 100%); }}
      #flash {{ background: #fff; opacity: 0; mix-blend-mode: screen; }}
      #fade {{ background: #000; opacity: 0; }}
      .dim {{ background: #07000f; opacity: 0; }}
      #blackout {{ background: #000; opacity: 0; }}
      .card {{ position: absolute; left: 120px; right: 120px; top: 160px; height: 760px;
               display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; }}
      .ln {{ display: block; text-align: center; }}
      .w {{ display: inline-block; font-family: "Anton", sans-serif; font-size: 150px; line-height: 0.98; color: var(--white);
            letter-spacing: 0.01em; -webkit-text-stroke: 10px var(--ink); paint-order: stroke fill;
            text-shadow: 10px 12px 0 var(--magenta), 0 0 40px rgba(0,0,0,0.5); white-space: nowrap; }}
      .accent .w {{ color: var(--yellow); }}
      .kicker .w {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 62px; letter-spacing: 0.08em;
                    text-shadow: 6px 7px 0 var(--magenta); -webkit-text-stroke: 7px var(--ink); }}
      #t08 {{ top: 330px; }}
      #t08 .w {{ font-size: 124px; }}
      .title {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
      .tbox {{ display: flex; flex-direction: column; align-items: center; }}
      .tw {{ display: block; font-family: "Anton", sans-serif; line-height: 0.9; color: var(--white);
             -webkit-text-stroke: 14px var(--ink); paint-order: stroke fill; text-shadow: 14px 16px 0 var(--magenta); }}
      .tw1 {{ font-size: 190px; letter-spacing: 0.02em; }}
      .tw2 {{ font-size: 250px; color: var(--yellow); letter-spacing: 0.04em; }}
      #endcard .tbox {{ margin-top: -40px; }}
      .cta {{ margin-top: 60px; padding: 24px 56px; background: var(--yellow); border: 8px solid var(--ink);
              box-shadow: 12px 14px 0 var(--magenta); font-family: "Inter", sans-serif; font-weight: 900;
              font-size: {60 if len(cta) <= 10 else 54}px; letter-spacing: 0.04em; color: var(--ink); white-space: nowrap; }}
      .sub {{ margin-top: 30px; font-family: "Inter", sans-serif; font-weight: 900; font-size: 44px; letter-spacing: 0.18em;
              color: var(--white); -webkit-text-stroke: 6px var(--ink); paint-order: stroke fill; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
      <div id="cam">
{chr(10).join(shot_html(s[0], s[1], s[2]) for s in shots)}
      </div>
      <div id="grade" class="layer"></div>
      <div id="dim3" class="clip layer dim" data-start="3.15" data-duration="1.77" data-track-index="1"></div>
      <div id="blackout" class="clip layer" data-start="20.10" data-duration="0.54" data-track-index="1"></div>
      <div id="dimEnd" class="clip layer dim" data-start="20.64" data-duration="{DUR - 20.64:.2f}" data-track-index="1"></div>

{chr(10).join(copy_html(tid, a, b, kind, lines[lang]) for tid, a, b, kind, lines in COPY)}

      <div id="title1" class="clip title" data-start="3.15" data-duration="1.77" data-track-index="3">
        <div class="tbox"><span class="tw tw1">MONSTER</span><span class="tw tw2">SWARM</span></div>
      </div>
      <div id="endcard" class="clip title" data-start="20.64" data-duration="{DUR - 20.64:.2f}" data-track-index="3">
        <div class="tbox">
          <span class="tw tw1">MONSTER</span><span class="tw tw2">SWARM</span>
          <div class="cta">{cta}</div>
          <div class="sub">{sub}</div>
        </div>
      </div>

      <div id="flash" class="layer"></div>
      <div id="fade" class="layer"></div>
      <audio id="bgm" class="clip" src="assets/bgm.wav" data-start="0" data-duration="{DUR}" data-track-index="10"></audio>
{sfx_html()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.set("#flash", {{opacity: 0}}, 0);
      tl.set("#cam", {{x: 0, y: 0, rotation: 0}}, 0);
{chr(10).join("      " + l for l in js)}
{chr(10).join("      " + l for l in TITLE_JS.strip().splitlines())}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


(ROOT / "index.html").write_text(build("fr"))
print("wrote index.html")
# the second language lives in compositions/ (one root per project folder), so its asset paths go up a level
(ROOT / "compositions").mkdir(exist_ok=True)
(ROOT / "compositions" / "trailer-en.html").write_text(
    build("en").replace('"assets/', '"../assets/').replace("url(\"assets/", "url(\"../assets/")
)
print("wrote compositions/trailer-en.html")
