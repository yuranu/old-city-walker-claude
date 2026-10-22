#!/usr/bin/env bash
# QA pass over one iconic place (data/qa/iconic.json): plan views -> capture -> image checks -> contact
# sheets for the vision critic. Needs the game dev server.  pipeline/qa/run_iconic.sh <place id> <run name>
set -euo pipefail
cd "$(dirname "$0")/../.."
P=$1; RUN=$2
OUT=build/qa/$RUN/$P
mkdir -p "$OUT"
PY=$PWD/.venv/bin/python
(cd pipeline/qa && $PY plan_iconic.py "$P" "$OLDPWD/$OUT/views.json")
node game/scripts/qa_capture.mjs --views "$OUT/views.json" --out "$OUT"
$PY pipeline/qa/analyze.py "$OUT"
$PY pipeline/qa/sheets.py "$OUT"
echo "next: vision critic -> Workflow(pipeline/qa/critic_workflow.js, {level: 0, run: \"$PWD/$OUT\", nbatches: $(( ($(ls $OUT/sheets | wc -l) + 5) / 6 )), per: 6})"
