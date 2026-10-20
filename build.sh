#!/usr/bin/env bash
# Rebuild the scene from data/raw:
#   OSM -> local frame -> spec (shapely) -> textures/signs -> Blender -> game/public -> audit
#
#   ./build.sh                 legacy scene (base + Jaffa Gate -> city.glb, previews, audit)
#                              and the streamed city (base + every sector -> game/public/{base,sectors})
#   ./build.sh --preview ""    the same without preview renders
#   PARTS="base s05_souks" ./build.sh   rebuild only these streamed parts; PARTS=none skips them
#   JOBS=6 ./build.sh          parallel Blender processes for the parts (default 4)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
# render on the discrete GPU when there is one (Mesa PRIME offload; harmless otherwise)
if [ "$(ls /dev/dri | grep -c renderD)" -gt 1 ]; then export DRI_PRIME=1; fi
$PY pipeline/osm_to_local.py
[ -f data/sectors.json ] || $PY pipeline/sectors.py
$PY pipeline/terrain_street.py > /dev/null      # street levels (1865 OS spot heights + DEM; 4 s)
blender -b --factory-startup --python-exit-code 1 -P blender/dump_landmarks.py 2>&1 | grep -E "^landmark ids|failed" || true   # ids for make_spec
$PY pipeline/make_spec.py
[ -f data/textures/gen/manifest.json ] || $PY pipeline/gen_textures.py
[ -f pipeline/gen_signs.py ] && [ ! -f data/textures/gen/signs.png ] && $PY pipeline/gen_signs.py
[ -f data/textures/gen/landmarks/manifest.json ] || $PY pipeline/gen_landmark_textures.py   # gold, lead, faience, Herodian
$PY pipeline/export_game_data.py
mkdir -p build/logs
BL=(blender -b --factory-startup --python-exit-code 1 -P blender/build_city.py --)

# streamed city, in the background while the legacy scene builds
PARTS=${PARTS:-"base $($PY -c 'import json;print(" ".join(s["id"] for s in json.load(open("data/spec/index.json"))["sectors"]))')"}
if [ "$PARTS" != none ]; then
  printf "%s\n" $PARTS | xargs -P "${JOBS:-4}" -I{} sh -c \
    '"$@" --part {} > build/logs/{}.log 2>&1 && echo "built {}" || echo "FAILED {} (build/logs/{}.log)"' _ "${BL[@]}" &
  PARTS_PID=$!
fi

"${BL[@]}" "$@" 2>&1 | grep -E "objects|exported|rendered|saved|Error|Traceback|unavailable"
blender -b build/city.blend --python-exit-code 1 -P blender/audit.py -- --top 8 2>&1 | grep -E "^AUDIT" | head -3

if [ "$PARTS" != none ]; then
  wait "$PARTS_PID"
  $PY pipeline/write_manifest.py
fi
