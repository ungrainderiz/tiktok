#!/usr/bin/env bash
# Reconstruit tout : plans extraits de la vidéo d'origine -> plan de montage + transcript -> bruitages -> compositions.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/assets.py
python3 tools/plan.py
python3 tools/sfx.py
python3 tools/build.py
