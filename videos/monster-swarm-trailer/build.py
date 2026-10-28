#!/usr/bin/env python3
"""Generates index.html for the Monster Swarm trailer from shots.json + the copy plan below.

Times are seconds on the 31.58s cut (assets/bgm.mp3), snapped to the audiomap beat grid.
Re-run after editing shots.json or COPY:  python3 build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
DUR = 31.58
shots = json.loads((ROOT / "shots.json").read_text())

# (id, start, end, kind, lines)  kind: big = stacked slam words, kick = small caps line + big word
COPY = [
    ("t01", 0.07, 1.67, "kick", ["A NEW", "ROGUELIKE"]),
    ("t02", 1.67, 3.37, "kick", ["ON", "ROBLOX"]),
    ("t03", 5.06, 6.76, "big", ["FIGHT", "THE SWARM"]),
    ("t04", 6.76, 8.45, "big", ["ENDLESS", "WAVES"]),
    ("t05", 8.45, 10.12, "big", ["LEVEL", "UP"]),
    ("t06", 10.12, 11.82, "big", ["PICK YOUR", "POWERS"]),
    ("t07", 13.51, 16.88, "big", ["HOW LONG", "CAN YOU", "SURVIVE?"]),
    ("t08", 16.88, 18.58, "kick", ["CHOOSE", "YOUR HERO"]),
    ("t09", 18.58, 21.97, "big", ["GIANT", "BOSSES"]),
    ("t10", 21.97, 25.36, "big", ["EVERY RUN", "IS DIFFERENT"]),
    ("t11", 25.36, 27.03, "big", ["SOLO OR", "WITH FRIENDS"]),
    ("t12", 27.03, 28.72, "kick", ["ARE YOU", "READY?"]),
]
# per-line reveal beats for multi-beat cards (else all lines land on the first beat, staggered)
LINE_BEATS = {
    "t03": [5.06, 5.48],
    "t07": [13.51, 14.35, 15.21],
    "t09": [18.58, 18.99],
    "t10": [21.97, 23.66],
    "t11": [25.36, 25.77],
    "t12": [27.03, 27.89],
}
# words that get the accent colour
ACCENT = {"SWARM", "THE SWARM", "UP", "POWERS", "SURVIVE?", "BOSSES", "ROGUELIKE", "ROBLOX",
          "YOUR HERO", "IS DIFFERENT", "WITH FRIENDS", "READY?", "WAVES"}
FLASHES = [(3.37, 0.35), (4.18, 0.9), (5.06, 0.5), (16.88, 0.6), (18.58, 0.8), (28.72, 1.0)]
SHAKES = [(4.18, 1.0), (7.15, 0.5), (8.41, 0.5), (12.21, 0.6), (12.63, 0.6), (16.86, 0.6),
          (18.55, 0.9), (18.97, 0.7), (25.31, 0.6), (25.73, 0.6), (28.72, 1.0)]


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
        if ln in ACCENT:
            cls += " accent"
        rows.append(f'        <div class="{cls}"><span class="w">{ln}</span></div>')
    body = "\n".join(rows)
    return (
        f'      <div class="clip card" id="{tid}" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
        f'data-track-index="2">\n{body}\n      </div>'
    )


js = []
for sid, a, b, *_ in shots:
    # punch-out on every cut + slow drift for the held shots
    js.append(f'tl.fromTo("#w-{sid}", {{scale: 1.14}}, {{scale: 1.0, duration: 0.32, ease: "expo.out"}}, {a:.2f});')
    if b - a > 1.2:
        js.append(f'tl.to("#w-{sid}", {{scale: 1.06, duration: {b - a - 0.32:.2f}, ease: "none"}}, {a + 0.32:.2f});')

for tid, a, b, kind, lines in COPY:
    beats = LINE_BEATS.get(tid)
    for i in range(len(lines)):
        t = beats[i] if beats else a + i * 0.12
        sel = f"#{tid} .ln:nth-child({i + 1}) .w"
        js.append(
            f'tl.fromTo("{sel}", {{opacity: 0, scale: 1.9, rotation: {(-4 if i % 2 else 3)}}}, '
            f'{{opacity: 1, scale: 1, rotation: 0, duration: 0.16, ease: "power4.out"}}, {t:.2f});'
        )
    js.append(f'tl.to("#{tid} .w", {{opacity: 0, y: -40, duration: 0.12, ease: "power2.in"}}, {b - 0.12:.2f});')

for t, k in FLASHES:
    js.append(f'tl.fromTo("#flash", {{opacity: {0.95 * k:.2f}}}, {{opacity: 0, duration: {0.25 + 0.3 * k:.2f}, ease: "power2.out", immediateRender: false}}, {t:.2f});')
for t, k in SHAKES:
    a = 26 * k
    js.append(
        f'tl.fromTo("#cam", {{x: {a:.0f}, y: {-a * 0.7:.0f}, rotation: {0.8 * k:.2f}}}, '
        f'{{x: 0, y: 0, rotation: 0, duration: 0.35, ease: "elastic.out(1.2, 0.3)", immediateRender: false}}, {t:.2f});'
    )

TITLE_JS = """
// ---- title slam on the drop
tl.fromTo("#title1 .tw1", {opacity: 0, scale: 3, y: -80}, {opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power4.out"}, 3.37);
tl.fromTo("#title1 .tw2", {opacity: 0, scale: 3, y: 80}, {opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power4.out"}, 3.79);
tl.fromTo("#title1 .tbox", {scale: 1}, {scale: 1.12, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false}, 4.18);
tl.fromTo("#title1 .tbox", {filter: "drop-shadow(0 0 0px #ff2bd6)"}, {filter: "drop-shadow(0 0 60px #ff2bd6)", duration: 0.74, ease: "none", immediateRender: false}, 4.18);
tl.to("#title1 .tbox", {scale: 0.2, opacity: 0, duration: 0.14, ease: "power3.in"}, 4.92);
tl.fromTo("#dim3", {opacity: 0.25}, {opacity: 0.6, duration: 0.4, ease: "power2.out"}, 3.37);

// ---- end card
tl.fromTo("#endcard .tw1", {opacity: 0, scale: 3}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 28.72);
tl.fromTo("#endcard .tw2", {opacity: 0, scale: 3}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 29.14);
tl.fromTo("#endcard .tbox", {filter: "drop-shadow(0 0 0px #ff2bd6)"}, {filter: "drop-shadow(0 0 50px #ff2bd6)", duration: 1.2, ease: "power1.out"}, 29.14);
tl.fromTo("#endcard .cta", {opacity: 0, y: 60}, {opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)"}, 29.35);
tl.fromTo("#endcard .sub", {opacity: 0}, {opacity: 1, duration: 0.2, ease: "power1.out"}, 29.4);
tl.fromTo("#endcard .cta", {scale: 1}, {scale: 1.08, duration: 0.21, yoyo: true, repeat: 3, ease: "sine.inOut"}, 30.0);
tl.fromTo("#dim25", {opacity: 0}, {opacity: 0.55, duration: 0.5, ease: "power1.out"}, 28.72);
tl.fromTo("#fade", {opacity: 0}, {opacity: 1, duration: 0.5, ease: "power1.in"}, 31.08);
"""

html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Monster Swarm — Trailer</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); font-weight: 400; }}
      @font-face {{ font-family: "Inter"; src: url("assets/fonts/inter-latin-900-normal.woff2") format("woff2"); font-weight: 900; }}
      :root {{
        --ink: #0b0710;
        --white: #ffffff;
        --magenta: #ff2bd6;
        --yellow: #ffd21f;
        --cyan: #2ef2ff;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--ink); }}
      #cam {{ position: absolute; inset: 0; }}
      .shot {{ position: absolute; inset: 0; }}
      .shot video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .layer {{ position: absolute; inset: 0; pointer-events: none; }}
      #grade {{ background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(8,0,20,0.55) 100%),
                 linear-gradient(180deg, rgba(10,0,25,0.35) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 70%, rgba(10,0,25,0.5) 100%); }}
      #flash {{ background: #fff; opacity: 0; mix-blend-mode: screen; }}
      #fade {{ background: #000; opacity: 0; }}
      .dim {{ background: #07000f; opacity: 0; }}
      .card {{ position: absolute; left: 70px; right: 70px; top: 560px; height: 760px;
               display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; }}
      .ln {{ display: block; text-align: center; }}
      .w {{ display: inline-block; font-family: "Anton", sans-serif; font-size: 172px; line-height: 0.98; color: var(--white);
            letter-spacing: 0.01em; -webkit-text-stroke: 10px var(--ink); paint-order: stroke fill;
            text-shadow: 10px 12px 0 var(--magenta), 0 0 40px rgba(0,0,0,0.5); white-space: nowrap; }}
      .accent .w {{ color: var(--yellow); }}
      .kicker .w {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 74px; letter-spacing: 0.08em;
                    text-shadow: 6px 7px 0 var(--magenta); -webkit-text-stroke: 7px var(--ink); }}
      #t10 .w, #t11 .w {{ font-size: 140px; }}
      #t11 {{ top: 900px; }}
      .title {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
      .tbox {{ display: flex; flex-direction: column; align-items: center; }}
      .tw {{ display: block; font-family: "Anton", sans-serif; line-height: 0.9; color: var(--white);
             -webkit-text-stroke: 14px var(--ink); paint-order: stroke fill; text-shadow: 14px 16px 0 var(--magenta); }}
      .tw1 {{ font-size: 230px; letter-spacing: 0.02em; }}
      .tw2 {{ font-size: 300px; color: var(--yellow); letter-spacing: 0.04em; }}
      #endcard .tbox {{ margin-top: -220px; }}
      .cta {{ margin-top: 70px; padding: 26px 64px; background: var(--yellow); border: 8px solid var(--ink);
              box-shadow: 12px 14px 0 var(--magenta); font-family: "Inter", sans-serif; font-weight: 900;
              font-size: 70px; letter-spacing: 0.04em; color: var(--ink); }}
      .sub {{ margin-top: 34px; font-family: "Inter", sans-serif; font-weight: 900; font-size: 52px; letter-spacing: 0.18em;
              color: var(--white); -webkit-text-stroke: 6px var(--ink); paint-order: stroke fill; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="cam">
{chr(10).join(shot_html(s[0], s[1], s[2]) for s in shots)}
      </div>
      <div id="grade" class="layer"></div>
      <div id="dim3" class="clip layer dim" data-start="3.37" data-duration="1.69" data-track-index="1"></div>
      <div id="dim25" class="clip layer dim" data-start="28.72" data-duration="2.86" data-track-index="1"></div>

{chr(10).join(copy_html(*c) for c in COPY)}

      <div id="title1" class="clip title" data-start="3.37" data-duration="1.69" data-track-index="3">
        <div class="tbox"><span class="tw tw1">MONSTER</span><span class="tw tw2">SWARM</span></div>
      </div>
      <div id="endcard" class="clip title" data-start="28.72" data-duration="2.86" data-track-index="3">
        <div class="tbox">
          <span class="tw tw1">MONSTER</span><span class="tw tw2">SWARM</span>
          <div class="cta">PLAY NOW</div>
          <div class="sub">ON ROBLOX</div>
        </div>
      </div>

      <div id="flash" class="layer"></div>
      <div id="fade" class="layer"></div>
      <audio id="bgm" class="clip" src="assets/bgm.mp3" data-start="0" data-duration="{DUR}" data-track-index="10"></audio>
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
(ROOT / "index.html").write_text(html)
print("wrote index.html")
