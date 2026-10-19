#!/usr/bin/env bash
# Rebuild the scene from data/raw:
#   OSM -> local frame -> spec (shapely) -> textures/signs -> Blender -> game/public/city.glb -> audit
#   ./build.sh                 # export GLB + preview renders
#   ./build.sh --preview ""    # export only
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
# render on the discrete GPU when there is one (Mesa PRIME offload; harmless otherwise)
if [ "$(ls /dev/dri | grep -c renderD)" -gt 1 ]; then export DRI_PRIME=1; fi
$PY pipeline/osm_to_local.py
$PY pipeline/make_spec.py
[ -f data/textures/gen/manifest.json ] || $PY pipeline/gen_textures.py
[ -f pipeline/gen_signs.py ] && [ ! -f data/textures/gen/signs.png ] && $PY pipeline/gen_signs.py
$PY pipeline/export_game_data.py
blender -b --factory-startup --python-exit-code 1 -P blender/build_city.py -- "$@" 2>&1 \
  | grep -E "objects|exported|rendered|saved|Error|Traceback|unavailable"
blender -b build/city.blend --python-exit-code 1 -P blender/audit.py -- --top 8 2>&1 | grep -E "^AUDIT" | head -3
