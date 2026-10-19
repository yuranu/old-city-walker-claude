#!/usr/bin/env bash
# Fetch the inputs that are not versioned. Pinned inputs (data/raw: OSM snapshot, terrain tiles)
# are only downloaded when missing; delete them deliberately to refresh from OSM.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
mkdir -p data/raw/terrain

# OpenStreetMap (ODbL), Old City bbox. Overpass is often overloaded; the main API map call is fine
# for an area this small (~9 MB). Building ids in pipeline tables refer to this snapshot.
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
$PY pipeline/fetch_ref_photos.py         # restore reference photos listed in the index.json files
# To discover new geotagged photos around the area (rewrites data/photos/index.json):
#   $PY pipeline/fetch_photos.py 150
