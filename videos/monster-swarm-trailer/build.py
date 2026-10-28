#!/usr/bin/env python3
"""Generates the Monster Swarm trailer compositions from shots.json + the copy below.

  index.html                         English, vertical 1080x1920 (TikTok)
  compositions/trailer-fr.html       French,  vertical
  compositions/trailer-en-16x9.html  English, horizontal 1920x1080
  compositions/trailer-fr-16x9.html  French,  horizontal
  (render a composition with: npx hyperframes render -c compositions/<name>.html ...)

Times are seconds on the 30.4s cut (assets/bgm.wav = full-track 10.217s -> 40.617s, 18 bars),
snapped to the audiomap beat grid. The cut is a seamless loop: it ends on the downbeat that
starts the next bar, the last shot (s25) runs into the exact source frame where s01 begins,
and the end card exits before the loop point so frame 0 follows without a visible jump.

Re-run after editing shots.json or COPY:  python3 build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
DUR = 30.4
shots = json.loads((ROOT / "shots.json").read_text())

# (id, start, end, kind, {lang: lines})  kind: big = stacked slam words, kick = small caps line + big word.
# The last line of every card takes the accent colour.
COPY = [
    ("t01", 0.07, 1.67, "kick", {"en": ["A NEW", "ROGUELIKE"], "fr": ["UN NOUVEAU", "ROGUELIKE"]}),
    ("t02", 1.67, 3.37, "kick", {"en": ["ON", "ROBLOX"], "fr": ["SUR", "ROBLOX"]}),
    ("t03", 5.06, 6.76, "big", {"en": ["FIGHT", "THE SWARM"], "fr": ["AFFRONTE", "LA HORDE"]}),
    ("t04", 6.76, 8.45, "big", {"en": ["ENDLESS", "WAVES"], "fr": ["DES VAGUES", "SANS FIN"]}),
    ("t05", 8.45, 10.12, "big", {"en": ["LEVEL", "UP"], "fr": ["MONTE DE", "NIVEAU"]}),
    ("t06", 10.12, 11.82, "big", {"en": ["PICK YOUR", "POWERS"], "fr": ["CHOISIS TES", "POUVOIRS"]}),
    ("t07", 13.51, 16.88, "big", {"en": ["HOW LONG", "CAN YOU", "SURVIVE?"], "fr": ["JUSQU’OÙ", "VAS-TU", "SURVIVRE ?"]}),
    ("t08", 16.88, 18.58, "kick", {"en": ["CHOOSE", "YOUR HERO"], "fr": ["CHOISIS", "TON HÉROS"]}),
    ("t09", 18.58, 21.97, "big", {"en": ["GIANT", "BOSSES"], "fr": ["DES BOSS", "GÉANTS"]}),
    ("t10", 21.97, 25.36, "big", {"en": ["EVERY RUN", "IS DIFFERENT"], "fr": ["CHAQUE PARTIE", "EST UNIQUE"]}),
    ("t11", 25.36, 27.03, "big", {"en": ["SOLO OR", "WITH FRIENDS"], "fr": ["EN SOLO OU", "ENTRE AMIS"]}),
]
END_CARD = {"en": ("PLAY NOW", "ON ROBLOX"), "fr": ("JOUE MAINTENANT", "SUR ROBLOX")}
# per-line reveal beats for multi-beat cards (else all lines land on the first beat, staggered)
LINE_BEATS = {
    "t03": [5.06, 5.48],
    "t07": [13.51, 14.35, 15.21],
    "t09": [18.58, 18.99],
    "t10": [21.97, 23.66],
    "t11": [25.36, 25.77],
}
FLASHES = [(3.37, 0.35), (4.18, 0.9), (5.06, 0.5), (16.88, 0.6), (18.58, 0.8), (27.03, 1.0), (28.72, 0.4)]
SHAKES = [(4.18, 1.0), (7.15, 0.5), (8.41, 0.5), (12.21, 0.6), (12.63, 0.6), (16.86, 0.6),
          (18.55, 0.9), (18.97, 0.7), (25.31, 0.6), (25.73, 0.6), (27.03, 1.0), (28.72, 0.5)]
# shots that sit on the loop seam: no punch-in, so the last frame flows into the first
SEAM = {"s01", "s25"}

# sound effects: (file in assets/sfx, start, volume). Whooshes peak 0.15s in, so they start 0.15s
# before the hit; the riser crests at the drop (4.18); the reversed whoosh dies out exactly on the
# loop point so the restart stays seamless. Source: media-use bundled Pixabay library (CREDITS.md).
SFX = [
    ("whoosh.wav", 1.52, 1.26),  # ON ROBLOX
    ("riser-build.wav", 1.18, 1.2),  # build into the drop
    ("whoosh.wav", 3.22, 1.61),  # MONSTER
    ("whoosh.wav", 3.64, 1.61),  # SWARM
    ("impact.wav", 4.18, 1.0),  # drop / title hit
    ("whoosh.wav", 4.91, 1.38),  # FIGHT THE SWARM
    ("whoosh.wav", 6.61, 1.26),  # ENDLESS WAVES
    ("sparkle.wav", 8.45, 1.52),  # LEVEL UP
    ("whoosh.wav", 9.97, 1.26),  # PICK YOUR POWERS
    ("pop.wav", 10.12, 1.08),
    ("whoosh.wav", 13.36, 1.26),  # HOW LONG
    ("whoosh.wav", 14.20, 1.03),  # CAN YOU
    ("whoosh.wav", 15.06, 1.38),  # SURVIVE?
    ("glitch.wav", 16.86, 1.21),  # CHOOSE YOUR HERO
    ("sparkle.wav", 17.05, 0.95),
    ("impact.wav", 18.58, 1.0),  # GIANT BOSSES
    ("whoosh.wav", 18.84, 1.26),
    ("whoosh.wav", 21.82, 1.26),  # EVERY RUN
    ("whoosh.wav", 23.51, 1.15),
    ("whoosh.wav", 25.21, 1.26),  # SOLO OR WITH FRIENDS
    ("impact.wav", 27.03, 1.0),  # end card MONSTER
    ("whoosh.wav", 27.30, 1.61),  # SWARM
    ("pop.wav", 27.89, 1.26),  # PLAY NOW
    ("whoosh-reverse.wav", 29.82, 1.68),  # exit, sucks back into frame 0
]
SFX_LEN = {"whoosh.wav": 0.57, "whoosh-reverse.wav": 0.57, "riser-build.wav": 3.0, "impact.wav": 1.4,
           "sparkle.wav": 1.8, "pop.wav": 0.72, "glitch.wav": 0.65}


def sfx_html(prefix):
    rows = []
    for i, (f, t, vol) in enumerate(SFX):
        d = min(SFX_LEN[f], DUR - t)
        rows.append(
            f'      <audio id="sfx{i:02d}" class="clip" src="{prefix}assets/sfx/{f}" data-start="{t:.2f}" '
            f'data-duration="{d:.2f}" data-volume="{vol}" data-track-index="{11 + i % 3}"></audio>'
        )
    return "\n".join(rows)


# canvas + type scale per format. 9x16 is the TikTok cut; 16x9 is the horizontal (YouTube / Roblox page) cut.
FORMATS = {
    "9x16": dict(w=1080, h=1920, shots="shots", card="left: 50px; right: 50px; top: 560px; height: 760px;",
                 w_px=172, kick_px=74, small_px=140, t11_top=900, tw1=230, tw2=300, end_mt=-220,
                 cta_px=(70, 60), sub_px=52),
    "16x9": dict(w=1920, h=1080, shots="shots-h", card="left: 120px; right: 120px; top: 160px; height: 760px;",
                 w_px=150, kick_px=62, small_px=124, t11_top=330, tw1=190, tw2=250, end_mt=-40,
                 cta_px=(60, 54), sub_px=44),
}


def shot_html(sid, a, b, shots_dir):
    return (
        f'      <div class="shot" id="w-{sid}">\n'
        f'        <video id="v-{sid}" class="clip" src="assets/{shots_dir}/{sid}.mp4" muted playsinline '
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
        if sid in SEAM:
            # s01 drifts in from 1.0; s25 holds at 1.0 so its last frame matches s01's first
            if sid == "s01":
                js.append(f'tl.fromTo("#w-{sid}", {{scale: 1.0}}, {{scale: 1.05, duration: {b - a:.2f}, ease: "none"}}, {a:.2f});')
            continue
        # punch-out on every cut + slow drift for the held shots
        js.append(f'tl.fromTo("#w-{sid}", {{scale: 1.14}}, {{scale: 1.0, duration: 0.32, ease: "expo.out"}}, {a:.2f});')
        if b - a > 1.2:
            js.append(f'tl.to("#w-{sid}", {{scale: 1.06, duration: {b - a - 0.32:.2f}, ease: "none"}}, {a + 0.32:.2f});')

    for tid, a, b, kind, lines in COPY:
        beats = LINE_BEATS.get(tid)
        for i in range(len(lines["en"])):
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
    return js


TITLE_JS = """
// ---- title slam on the drop
tl.fromTo("#title1 .tw1", {opacity: 0, scale: 3, y: -80}, {opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power4.out"}, 3.37);
tl.fromTo("#title1 .tw2", {opacity: 0, scale: 3, y: 80}, {opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power4.out"}, 3.79);
tl.fromTo("#title1 .tbox", {scale: 1}, {scale: 1.12, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false}, 4.18);
tl.fromTo("#title1 .tbox", {filter: "drop-shadow(0 0 0px #ff2bd6)"}, {filter: "drop-shadow(0 0 60px #ff2bd6)", duration: 0.74, ease: "none", immediateRender: false}, 4.18);
tl.to("#title1 .tbox", {scale: 0.2, opacity: 0, duration: 0.14, ease: "power3.in"}, 4.92);
tl.fromTo("#dim3", {opacity: 0.25}, {opacity: 0.6, duration: 0.4, ease: "power2.out"}, 3.37);

// ---- end card (27.03 -> loop point); exits before 30.4 so the loop back to frame 0 is clean
tl.fromTo("#endcard .tw1", {opacity: 0, scale: 3}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 27.03);
tl.fromTo("#endcard .tw2", {opacity: 0, scale: 3}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 27.45);
tl.fromTo("#endcard .tbox", {filter: "drop-shadow(0 0 0px #ff2bd6)"}, {filter: "drop-shadow(0 0 50px #ff2bd6)", duration: 1.2, ease: "power1.out", immediateRender: false}, 27.45);
tl.fromTo("#endcard .cta", {opacity: 0, y: 60}, {opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)"}, 27.89);
tl.fromTo("#endcard .sub", {opacity: 0}, {opacity: 1, duration: 0.2, ease: "power1.out"}, 27.95);
tl.fromTo("#endcard .tbox", {scale: 1}, {scale: 1.08, duration: 0.1, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false}, 28.72);
tl.fromTo("#endcard .cta", {scale: 1}, {scale: 1.08, duration: 0.21, yoyo: true, repeat: 3, ease: "sine.inOut"}, 28.72);
tl.to("#endcard .tbox", {scale: 1.6, opacity: 0, filter: "blur(18px) drop-shadow(0 0 50px #ff2bd6)", duration: 0.34, ease: "power3.in"}, 29.98);
tl.fromTo("#dimEnd", {opacity: 0}, {opacity: 0.5, duration: 0.3, ease: "power1.out"}, 27.03);
tl.to("#dimEnd", {opacity: 0, duration: 0.42, ease: "power1.in"}, 29.98);
"""


def build(lang, fmt):
    F = FORMATS[fmt]
    cta, sub = END_CARD[lang]
    js = timeline_js()
    return f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={F['w']}, height={F['h']}" />
    <title>Monster Swarm — Trailer ({lang.upper()} {fmt})</title>
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
      html, body {{ width: {F['w']}px; height: {F['h']}px; overflow: hidden; background: var(--ink); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--ink); }}
      #cam {{ position: absolute; inset: 0; }}
      .shot {{ position: absolute; inset: 0; }}
      .shot video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .layer {{ position: absolute; inset: 0; pointer-events: none; }}
      #grade {{ background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(8,0,20,0.55) 100%),
                 linear-gradient(180deg, rgba(10,0,25,0.35) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 70%, rgba(10,0,25,0.5) 100%); }}
      #flash {{ background: #fff; opacity: 0; mix-blend-mode: screen; }}
      .dim {{ background: #07000f; opacity: 0; }}
      .card {{ position: absolute; {F['card']}
               display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; }}
      .ln {{ display: block; text-align: center; }}
      .w {{ display: inline-block; font-family: "Anton", sans-serif; font-size: {F['w_px']}px; line-height: 0.98; color: var(--white);
            letter-spacing: 0.01em; -webkit-text-stroke: 10px var(--ink); paint-order: stroke fill;
            text-shadow: 10px 12px 0 var(--magenta), 0 0 40px rgba(0,0,0,0.5); white-space: nowrap; }}
      .accent .w {{ color: var(--yellow); }}
      .kicker .w {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: {F['kick_px']}px; letter-spacing: 0.08em;
                    text-shadow: 6px 7px 0 var(--magenta); -webkit-text-stroke: 7px var(--ink); }}
      #t10 .w, #t11 .w {{ font-size: {F['small_px']}px; }}
      #t11 {{ top: {F['t11_top']}px; }}
      .title {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
      .tbox {{ display: flex; flex-direction: column; align-items: center; }}
      .tw {{ display: block; font-family: "Anton", sans-serif; line-height: 0.9; color: var(--white);
             -webkit-text-stroke: 14px var(--ink); paint-order: stroke fill; text-shadow: 14px 16px 0 var(--magenta); }}
      .tw1 {{ font-size: {F['tw1']}px; letter-spacing: 0.02em; }}
      .tw2 {{ font-size: {F['tw2']}px; color: var(--yellow); letter-spacing: 0.04em; }}
      #endcard .tbox {{ margin-top: {F['end_mt']}px; }}
      .cta {{ margin-top: 70px; padding: 26px 56px; background: var(--yellow); border: 8px solid var(--ink);
              box-shadow: 12px 14px 0 var(--magenta); font-family: "Inter", sans-serif; font-weight: 900;
              font-size: {F['cta_px'][0] if len(cta) <= 10 else F['cta_px'][1]}px; letter-spacing: 0.04em; color: var(--ink); white-space: nowrap; }}
      .sub {{ margin-top: 34px; font-family: "Inter", sans-serif; font-weight: 900; font-size: {F['sub_px']}px; letter-spacing: 0.18em;
              color: var(--white); -webkit-text-stroke: 6px var(--ink); paint-order: stroke fill; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{F['w']}" data-height="{F['h']}">
      <div id="cam">
{chr(10).join(shot_html(s[0], s[1], s[2], F['shots']) for s in shots)}
      </div>
      <div id="grade" class="layer"></div>
      <div id="dim3" class="clip layer dim" data-start="3.37" data-duration="1.69" data-track-index="1"></div>
      <div id="dimEnd" class="clip layer dim" data-start="27.03" data-duration="{DUR - 27.03:.2f}" data-track-index="1"></div>

{chr(10).join(copy_html(tid, a, b, kind, lines[lang]) for tid, a, b, kind, lines in COPY)}

      <div id="title1" class="clip title" data-start="3.37" data-duration="1.69" data-track-index="3">
        <div class="tbox"><span class="tw tw1">MONSTER</span><span class="tw tw2">SWARM</span></div>
      </div>
      <div id="endcard" class="clip title" data-start="27.03" data-duration="{DUR - 27.03:.2f}" data-track-index="3">
        <div class="tbox">
          <span class="tw tw1">MONSTER</span><span class="tw tw2">SWARM</span>
          <div class="cta">{cta}</div>
          <div class="sub">{sub}</div>
        </div>
      </div>

      <div id="flash" class="layer"></div>
      <audio id="bgm" class="clip" src="assets/bgm.wav" data-start="0" data-duration="{DUR}" data-track-index="10"></audio>
{sfx_html("")}
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


# index.html is the English vertical cut; the other versions live in compositions/ (one root per
# project folder), so their asset paths go up a level.
(ROOT / "index.html").write_text(build("en", "9x16"))
print("wrote index.html")
(ROOT / "compositions").mkdir(exist_ok=True)
for lang, fmt, name in (("fr", "9x16", "trailer-fr"), ("en", "16x9", "trailer-en-16x9"), ("fr", "16x9", "trailer-fr-16x9")):
    html = build(lang, fmt).replace('"assets/', '"../assets/').replace("url(\"assets/", "url(\"../assets/")
    (ROOT / "compositions" / f"{name}.html").write_text(html)
    print(f"wrote compositions/{name}.html")
