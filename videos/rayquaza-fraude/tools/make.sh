#!/usr/bin/env bash
# Reconstruit tout le projet : bruitages -> compositions/index -> carve de la musique sous la voix.
# Usage : tools/make.sh [dossier contenant node_modules/@hyperframes/core]
set -euo pipefail
cd "$(dirname "$0")/.."
CORE="${1:-.}"
python3 tools/sfx.py
python3 tools/build.py
CARVE=../../.claude/skills/hyperframes-audio/scripts/carve.mjs
for bed in musique-a musique-b; do
  node "$CARVE" --comp index.html --bed "$bed" --voice voix --strength 0.65 --core "$CORE"
done
