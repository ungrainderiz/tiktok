#!/usr/bin/env bash
# Reconstruit tout le projet : bruitages -> compositions/index -> carve de l'OST sous la voix.
# Usage : tools/make.sh [dossier contenant node_modules/@hyperframes/core]
set -euo pipefail
cd "$(dirname "$0")/.."
CORE="${1:-.}"
python3 tools/sfx.py
python3 tools/build.py
node ../../.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed musique --voice voix --strength 0.6 --core "$CORE"
