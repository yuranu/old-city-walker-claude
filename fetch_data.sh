#!/usr/bin/env bash
# Fetch the inputs that are not versioned, and check every pinned input against data/inputs.sha256
# (docs/DATA.md). Files already present are not downloaded again.
#   ./fetch_data.sh             terrain tiles + Poly Haven textures (what ./build.sh needs)
#   ./fetch_data.sh --photos    also the reference photographs (evaluation, research notes, QA)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
mkdir -p data/raw/terrain

# OpenStreetMap (ODbL): a frozen snapshot, versioned. Building ids in the pipeline tables refer to
# it, so it is never refreshed here. These calls only document how it was taken (2026-10-19).
[ -f data/raw/osm_oldcity.osm ] || curl -sS -A "old-city-walker-poc/0.2" -o data/raw/osm_oldcity.osm \
  'https://api.openstreetmap.org/api/0.6/map?bbox=35.2255,31.7700,35.2385,31.7825'

[ -f data/raw/osm_west.osm ] || curl -sS -A "old-city-walker-poc/0.2" -o data/raw/osm_west.osm \
  'https://api.openstreetmap.org/api/0.6/map?bbox=35.2215,31.7715,35.2256,31.7815'

# Elevation: AWS Terrain Tiles (terrarium encoding, SRTM-derived here), z15
for t in 15/19590/13329 15/19591/13329 15/19590/13330 15/19591/13330 15/19590/13331 15/19591/13331; do
  f="data/raw/terrain/$(echo $t | tr / _).png"
  [ -f "$f" ] || curl -sS -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$t.png"
done

$PY pipeline/fetch_textures.py 2k        # Poly Haven CC0 stone textures (+ tinted copies)

check() {      # check the pinned files whose paths match $1
  grep -v '^#' data/inputs.sha256 | grep -E "$1" | sha256sum -c --quiet \
    || { echo "pinned inputs differ from data/inputs.sha256 (see docs/DATA.md)" >&2; exit 1; }
}
check ' data/(raw|textures)/'

if [ "${1:-}" = --photos ]; then
  $PY pipeline/fetch_ref_photos.py       # restore the photographs listed in the index.json files
  # photos are not build inputs: one deleted or replaced on Commons only costs its evaluation cameras
  bad=$(grep -v '^#' data/inputs.sha256 | grep ' data/photos' | sha256sum -c 2>/dev/null | grep -v ': OK$' | cut -d: -f1) || true
  if [ -n "$bad" ]; then
    echo "WARNING: pinned photos missing or changed upstream; the evaluation skips their cameras:"
    $PY -c 'import json, sys
cams = json.load(open("data/reference/eval_cams.json"))["cams"]
for f in sys.argv[1:]:
    print("  %s  (cameras: %s)" % (f, ", ".join(n for n, c in cams.items() if c.get("photo") == f) or "none"))' $bad
  fi
  # To discover new geotagged photos around the area (rewrites data/photos/index.json):
  #   $PY pipeline/fetch_photos.py 150
fi
echo "inputs ok"
