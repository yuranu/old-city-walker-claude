#!/usr/bin/env bash
# Package the built game as a release archive: build/release/old-city-walker-<version>.zip
# (README.md from this folder, serve.py, game/ = the static build, LICENSE, ATTRIBUTION.md, VERSION).
# Build the city first (./build.sh); this only packages what game/public holds.
#   release/make_release.sh [version]        # default: git describe
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f game/public/sectors.json ] || { echo "game/public/sectors.json missing: run ./build.sh first" >&2; exit 1; }
VER=${1:-$(git describe --tags --always --dirty)}
NAME=old-city-walker-$VER
OUT=build/release/$NAME
# no splitting: the per-file cap is the live host's, a local server has none
npm --prefix game run deploy:build -- --max-mib 4096
rm -rf "$OUT" "$OUT.zip"; mkdir -p "$OUT"
cp -r game/dist "$OUT/game"
cp release/README.md release/serve.py release/ATTRIBUTION.md LICENSE "$OUT/"
printf "%s\nsource: https://github.com/yuranu/old-city-walker-claude/tree/%s\n" "$VER" "$(git rev-parse HEAD)" > "$OUT/VERSION"
git diff --quiet HEAD || echo "built from a working tree with uncommitted changes" >> "$OUT/VERSION"
(cd build/release && zip -qr "$NAME.zip" "$NAME")
echo "$OUT.zip  $(du -h "$OUT.zip" | cut -f1)"
