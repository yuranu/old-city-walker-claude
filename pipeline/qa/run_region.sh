#!/usr/bin/env bash
# QA pass over one region (a sector id, a name from data/qa/regions.json, or x0,y0,x1,y1):
# plan views -> capture in the game -> image checks -> geometry checks -> cross-part flicker audit ->
# contact sheets for the vision critic (pipeline/qa/critic_workflow.js) -> ledger.
#   pipeline/qa/run_region.sh <region> <run name> [level]
# Needs the game dev server (npm --prefix game run dev). Results: build/qa/<run>/<region>/
set -euo pipefail
cd "$(dirname "$0")/../.."
R=$1; RUN=$2; LEVEL=${3:-0}
OUT=build/qa/$RUN/$R
mkdir -p "$OUT"
PY=.venv/bin/python
$PY pipeline/qa/plan_views.py "$R" "$OUT/views.json"
node game/scripts/qa_capture.mjs --views "$OUT/views.json" --out "$OUT"
$PY pipeline/qa/analyze.py "$OUT"
$PY pipeline/qa/measure.py "$R" "$OUT/measure.json"
$PY pipeline/qa/audit_region.py "$R" "$OUT/audit.json"
$PY pipeline/qa/sheets.py "$OUT"
F="$OUT/image_findings.json $OUT/measure.json $OUT/audit.json"
[ -f "$OUT/vision_findings.json" ] && F="$F $OUT/vision_findings.json"
$PY pipeline/qa/ledger.py "$R" "$LEVEL" $F
echo "next: vision critic -> Workflow(pipeline/qa/critic_workflow.js, {level: $LEVEL, run: \"$PWD/$OUT\", nbatches: $(( ($(ls $OUT/sheets | wc -l) + 5) / 6 )), per: 6})"
