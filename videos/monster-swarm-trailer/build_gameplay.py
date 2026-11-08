#!/usr/bin/env python3
"""Gameplay cut of the Monster Swarm trailer: same 30.4s Ouroboros x HardTekk edit (beat grid, copy, SFX,
seamless loop) as build.py, with the middle rebuilt from the new top-down gameplay captures and the
Leviathan of the Abyss boss. Horizontal 1920x1080.

  compositions/trailer-gameplay-en-16x9.html   (render with: npx hyperframes render -c compositions/<name>.html ...)

Shots come from shots-gameplay.json -> assets/shots-gameplay/ ("old" rows are copies of assets/shots-h/).
Re-run after editing shots-gameplay.json:  python3 build_gameplay.py
"""
import json

import build

build.shots = json.loads((build.ROOT / "shots-gameplay.json").read_text())
build.FORMATS["16x9-gameplay"] = dict(build.FORMATS["16x9"], shots="shots-gameplay")

# the Leviathan's in-game title card owns 18.58-20.27, so "GIANT BOSSES" lands one bar later
build.COPY = [c if c[0] != "t09" else ("t09", 20.27, 21.97, c[3], c[4]) for c in build.COPY]
build.LINE_BEATS = dict(build.LINE_BEATS, t09=[20.27, 20.69])


def main():
    for lang in ("en",):
        name = f"trailer-gameplay-{lang}-16x9"
        html = build.build(lang, "16x9-gameplay").replace('"assets/', '"../assets/').replace("url(\"assets/", "url(\"../assets/")
        (build.ROOT / "compositions" / f"{name}.html").write_text(html)
        print(f"wrote compositions/{name}.html")


if __name__ == "__main__":
    main()
