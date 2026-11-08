#!/usr/bin/env python3
"""Roblox video-ad cut of the gameplay trailer (horizontal 1920x1080, 30.4s), built to the Roblox ad video
guidelines:
  - footage is unretouched game capture (assets/shots-ads: crop + scale only, no grade/sharpen/vignette),
    no white flashes or camera shake; cuts and punch-ins are kept (camera work)
  - no music: the Ouroboros track is not from the Roblox catalog and may carry vocals. Only light SFX,
    no voiceover. Add a Roblox-catalog track before uploading.
  - text: the game title (brand) plus a few short captions that only describe gameplay; no call to action,
    no claims, no promotion
Shot order and timing follow shots-gameplay.json (same beat grid as the music cuts).

  compositions/trailer-ad-en-16x9.html   (render with: npx hyperframes render -c compositions/trailer-ad-en-16x9.html ...)
"""
import re

import build
import build_gameplay  # noqa: F401  (sets build.shots to the gameplay shot list)

build.FORMATS["16x9-ad"] = dict(build.FORMATS["16x9"], shots="shots-ads")
build.FLASHES = []
build.SHAKES = []
build.LINE_BEATS = {}
# single-line captions describing what the player is doing on screen
build.COPY = [
    ("c1", 5.20, 8.30, "big", {"en": ["Survive waves of monsters"]}),
    ("c2", 8.60, 11.70, "big", {"en": ["Level up and pick new skills"]}),
    ("c3", 17.00, 18.45, "big", {"en": ["Choose your class"]}),
    ("c4", 20.40, 23.55, "big", {"en": ["Battle bosses"]}),
]
build.SFX = [
    ("riser-build.wav", 1.18, 0.6),
    ("whoosh.wav", 3.22, 0.7),
    ("whoosh.wav", 3.64, 0.7),
    ("impact.wav", 4.18, 0.8),
    ("sparkle.wav", 8.45, 0.5),
    ("impact.wav", 18.58, 0.7),
    ("impact.wav", 27.03, 0.8),
    ("whoosh.wav", 27.30, 0.7),
]
build.TITLE_JS = """
// ---- game title on the 4.18 hit
tl.fromTo("#title1 .tw1", {opacity: 0, scale: 2.2, y: -60}, {opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "power4.out"}, 3.37);
tl.fromTo("#title1 .tw2", {opacity: 0, scale: 2.2, y: 60}, {opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "power4.out"}, 3.79);
tl.fromTo("#title1 .tbox", {scale: 1}, {scale: 1.08, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false}, 4.18);
tl.to("#title1 .tbox", {opacity: 0, duration: 0.18, ease: "power2.in"}, 4.86);
tl.fromTo("#dim3", {opacity: 0}, {opacity: 0.35, duration: 0.3, ease: "power1.out"}, 3.37);

// ---- end title (brand only), clears before the loop point
tl.fromTo("#endcard .tw1", {opacity: 0, scale: 2.2}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 27.03);
tl.fromTo("#endcard .tw2", {opacity: 0, scale: 2.2}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 27.45);
tl.to("#endcard .tbox", {opacity: 0, duration: 0.35, ease: "power2.in"}, 29.98);
tl.fromTo("#dimEnd", {opacity: 0}, {opacity: 0.3, duration: 0.3, ease: "power1.out"}, 27.03);
tl.to("#dimEnd", {opacity: 0, duration: 0.4, ease: "power1.in"}, 29.98);
"""

AD_CSS = """
      /* ad cut: no grade over the footage; captions as a small lower-third */
      #grade { display: none; }
      .card { top: auto; bottom: 90px; height: auto; }
      .card .w { font-family: "Inter", sans-serif; font-weight: 900; font-size: 54px; letter-spacing: 0.01em; line-height: 1.2;
                 color: #fff; -webkit-text-stroke: 0; text-shadow: 0 2px 10px rgba(0,0,0,0.7);
                 background: rgba(11,7,16,0.62); padding: 12px 30px; border-radius: 10px; }
      #endcard .cta, #endcard .sub { display: none; }
    </style>"""


def main():
    html = build.build("en", "16x9-ad")
    html = html.replace("\n    </style>", AD_CSS, 1)
    html = re.sub(r'\n\s*<audio id="bgm"[^\n]*</audio>', "", html)
    # captions slide up gently instead of the slam used for the big type
    html = re.sub(r"scale: 1\.9, rotation: -?\d+\}", "y: 24}", html)
    html = html.replace('{opacity: 1, scale: 1, rotation: 0, duration: 0.16, ease: "power4.out"}',
                        '{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}')
    html = html.replace('"assets/', '"../assets/').replace("url(\"assets/", "url(\"../assets/")
    (build.ROOT / "compositions" / "trailer-ad-en-16x9.html").write_text(html)
    print("wrote compositions/trailer-ad-en-16x9.html")


if __name__ == "__main__":
    main()
