#!/usr/bin/env python3
"""Roblox video-ad cut on "Good rock for gaming" (Roblox Creator Store asset 133167080481954, recorded from
Studio), horizontal 1920x1080, 28.03s. Same ad rules as build_ads.py: unretouched footage, no flashes or
shake, no voiceover, game title plus short gameplay captions only, no call to action.

assets/music-rock.wav = the recording from 1.70s (first downbeat) to 29.73s (last full bar), 117 BPM,
bar ~2.0s. Local downbeats: 0 2.15 4.01 6.03 8.03 10.03 12.02 14.02 16.02 18.01 20.03 22.03 24.03 26.03.
The track lifts at 6.03, where the gameplay starts.

  compositions/trailer-ad-rock-en-16x9.html
Re-run after editing shots-rock.json:  python3 build_rock_ad.py
"""
import json
import re

import build
import build_ads

DUR = 28.03
build.DUR = DUR
build.shots = json.loads((build.ROOT / "shots-rock.json").read_text())
build.FORMATS["16x9-rock"] = dict(build.FORMATS["16x9"], shots="shots-rock")
build.SEAM = {"s01", "s24"}  # opening drift; end-title bed holds still
build.FLASHES = []
build.SHAKES = []
build.LINE_BEATS = {}
build.COPY = [
    ("c1", 6.15, 9.90, "big", {"en": ["Survive waves of monsters"]}),
    ("c2", 10.15, 13.90, "big", {"en": ["Level up and pick new skills"]}),
    ("c3", 16.15, 17.90, "big", {"en": ["Choose your class"]}),
    ("c4", 20.15, 23.90, "big", {"en": ["Battle bosses"]}),
    ("c5", 24.15, 25.90, "big", {"en": ["Team up with friends"]}),
]
build.SFX = [
    ("whoosh.wav", 3.86, 0.6),   # MONSTER
    ("whoosh.wav", 4.37, 0.6),   # SWARM
    ("impact.wav", 4.52, 0.7),
    ("sparkle.wav", 10.03, 0.45),  # level-up cards
    ("impact.wav", 18.01, 0.6),  # Leviathan intro
    ("impact.wav", 26.03, 0.7),  # end title
    ("whoosh.wav", 26.38, 0.6),
]
build.TITLE_JS = """
// ---- game title over the intro's last bar
tl.fromTo("#title1 .tw1", {opacity: 0, scale: 2.2, y: -60}, {opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "power4.out"}, 4.01);
tl.fromTo("#title1 .tw2", {opacity: 0, scale: 2.2, y: 60}, {opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "power4.out"}, 4.52);
tl.fromTo("#title1 .tbox", {scale: 1}, {scale: 1.06, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false}, 5.02);
tl.to("#title1 .tbox", {opacity: 0, duration: 0.18, ease: "power2.in"}, 5.83);
tl.fromTo("#dim3", {opacity: 0}, {opacity: 0.35, duration: 0.3, ease: "power1.out"}, 4.01);

// ---- end title (brand only), then fade out with the music
tl.fromTo("#endcard .tw1", {opacity: 0, scale: 2.2}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 26.03);
tl.fromTo("#endcard .tw2", {opacity: 0, scale: 2.2}, {opacity: 1, scale: 1, duration: 0.2, ease: "power4.out"}, 26.53);
tl.fromTo("#dimEnd", {opacity: 0}, {opacity: 0.3, duration: 0.3, ease: "power1.out"}, 26.03);
tl.to("#endcard .tbox", {opacity: 0, duration: 0.45, ease: "power1.in"}, 27.55);
tl.to("#dimEnd", {opacity: 1, duration: 0.45, ease: "power1.in"}, 27.55);
"""


def main():
    html = build.build("en", "16x9-rock")
    html = html.replace("\n    </style>", build_ads.AD_CSS, 1)
    html = html.replace('src="assets/bgm.wav"', 'src="assets/music-rock.wav"')
    # title/end-card windows are authored for the Ouroboros grid in build.py; move them to this track's bars
    html = re.sub(r'(id="(?:dim3|title1)" class="[^"]*" )data-start="3.37" data-duration="1.69"',
                  r'\1data-start="4.01" data-duration="2.02"', html)
    html = re.sub(r'(id="(?:dimEnd|endcard)" class="[^"]*" )data-start="27.03" data-duration="[\d.]+"',
                  rf'\1data-start="26.03" data-duration="{DUR - 26.03:.2f}"', html)
    html = re.sub(r"scale: 1\.9, rotation: -?\d+\}", "y: 24}", html)
    html = html.replace('{opacity: 1, scale: 1, rotation: 0, duration: 0.16, ease: "power4.out"}',
                        '{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}')
    html = html.replace('"assets/', '"../assets/').replace("url(\"assets/", "url(\"../assets/")
    (build.ROOT / "compositions" / "trailer-ad-rock-en-16x9.html").write_text(html)
    print("wrote compositions/trailer-ad-rock-en-16x9.html")


if __name__ == "__main__":
    main()
