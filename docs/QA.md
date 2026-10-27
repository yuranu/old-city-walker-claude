# QA loop

The city is too large to check by walking it. QA renders planned viewpoints in the real game,
runs automated checks on the images and on the scene spec, has vision critics review contact
sheets, and keeps every finding in a ledger so a fix can never quietly undo another.

## Levels

[`data/qa/levels.md`](../data/qa/levels.md) defines them. A region passes level N when no finding
of severity high or medium is open at level N or below and nothing regressed.

| Level | Meaning |
|---|---|
| 0 | not broken: no holes, flicker, floating or buried objects, blocked walkways, missing textures |
| 1 | structurally plausible: heights, doors at street level, continuous street walls, steps where steep |
| 2 | character: street types, materials, shutters, canopies, signage, rooftops |
| 3 | photo match at the evaluation viewpoints ([EVALUATION.md](EVALUATION.md)) |
| 4, 5+ | material and lighting realism, towards photorealism |

Fixes go to the generating rule (spec, stairs, infill, facades, dressing, builders) so the whole
city improves at once. A data fix for one place (a profile or an override in `data/reference/`)
is only for facts about that place.

## A pass over a region

```bash
npm --prefix game run dev &                       # the captures drive the running game
pipeline/qa/run_region.sh <region> <run> [level]  # region: a sector id, a name in data/qa/regions.json, or x0,y0,x1,y1
pipeline/qa/run_iconic.sh <place> <run>           # one place from data/qa/iconic.json
```

Results land in `build/qa/<run>/<region>/`. The steps:

1. **Plan views** (`plan_views.py`, `plan_iconic.py`): street centrelines every 15 m in both
   directions, squares, stair ends, an aerial grid, and the regression views in
   `data/qa/regression.json`.
2. **Capture** (`game/scripts/qa_capture.mjs`): headless Chrome renders each view three times: the
   normal frame, a frame from 1 cm away, and a sky-keyed frame.
3. **Image checks** (`analyze.py`): magenta below the horizon in the sky-keyed frame is a hole;
   compact clusters that change between the two nearby frames are flicker.
4. **Geometry checks** (`measure.py`) on the spec, exhaustive and without rendering; each finding
   names the generator it most likely comes from.
5. **Flicker audit** (`audit_region.py`): coplanar overlaps across every part in one Blender scene.
6. **Contact sheets** (`sheets.py`) and the **vision critic**: `pipeline/qa/critic_workflow.js` is
   a [Claude Code](https://claude.com/claude-code) workflow. One critic reviews each batch of
   sheets against the levels, and an independent skeptic verifies every finding on the full frame.
7. **Ledger** (`ledger.py`): findings merge into `data/qa/ledger.json` as new, open, fixed or
   REGRESSED.

`pipeline/qa/rebuild.sh [JOBS]` regenerates the spec and rebuilds every part between passes.
Do not edit the game while a capture runs: the dev server reloads and the capture breaks.

## Street View references

A critic without a reference rates plausibility, not truth: one landmark passed review while
missing its compound walls entirely. So critics compare REAL | MODEL pairs from the same spot.

During the research the references were Google Street View stills. The tooling that fetched and
aligned them is not part of this repository; what remains works on any set of reference stills
with known positions and headings:

1. `sv_points.py` proposes lookup points: every 8 m along street-level OSM ways near the place,
   clear of buildings, spread around it (`--region` for a whole sector). Street View is shot
   from where people walk, so these are where panoramas are likely.
2. Each reference is kept only if it is outdoors and lines up with the model: its heading is
   matched against the model's skyline, and indoor panoramas, misplaced photospheres and poor
   matches are dropped. The surviving panoramas are listed in `data/qa/sv_panos.json`.
3. `qa_capture.mjs` renders the game from the same position, heading and field of view, and
   `sv_compare.py` makes the REAL | MODEL pairs and sheets (`build/qa/svcmp/<place>/`).
4. `pipeline/qa/sv_critic_workflow.js` reviews the pairs; `sv_whatsthere.py` traces a finding
   ("invented building on the left") to the spec entry that makes it.

Commons photographs of the iconic places (`pipeline/fetch_iconic_photos.py`) complement them;
note that a famous photograph may show a courtyard no street visitor ever sees.
