#!/usr/bin/env bash
# Regenerate the spec and rebuild base + all sectors with modest parallelism (the laptop overheats at 6).
#   pipeline/qa/rebuild.sh [JOBS]
set -euo pipefail
cd "$(dirname "$0")/../.."
J=${1:-3}
PY=.venv/bin/python
$PY pipeline/make_spec.py 2>&1 | grep -E "Error|Traceback|^buildings" || true
$PY pipeline/export_game_data.py | tail -1
printf "base\n%s\n" "$($PY -c 'import json;print("\n".join(s["id"] for s in json.load(open("data/spec/index.json"))["sectors"]))')" \
  | DRI_PRIME=1 xargs -P "$J" -I{} sh -c 'blender -b --factory-startup --python-exit-code 1 -P blender/build_city.py -- --part {} > build/logs/{}.log 2>&1 || echo "FAILED {}"'
grep -h "LANDMARKS WARNING\|WALLS WARNING" build/logs/*.log | sort | uniq -c | head -5 || true
$PY pipeline/write_manifest.py | head -1
