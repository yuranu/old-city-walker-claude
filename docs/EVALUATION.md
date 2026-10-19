# Photo evaluation loop

The goal of the model is to *feel like the real place*. The evaluation loop makes that measurable:
render the model from exactly where real photographs were taken, put photo and render side by
side, score how well they line up, fix the model, repeat.

```
          build/city.blend  (rebuilt by blender/build_city.py at any time)
                 │
data/reference/eval_cams.json ──► blender/render_eval.py ──► renders/eval/<cam>_model.png, _mask.png, _model.json
   (photo + pose per cam)                                          │
                 └──────────────► pipeline/eval_compare.py ◄───────┘
                                        │
       renders/eval/<cam>_compare.jpg, <cam>_overlay.jpg, sheet.jpg, scores.json, history.jsonl
```

| File | Role |
|---|---|
| `pipeline/eval_set.py` | find / download photos, EXIF → FOV, solve poses from landmarks (`resect`), edit cams, `sync` to the game |
| `blender/render_eval.py` | open any `.blend` read-only and render every eval cam (EEVEE, afternoon sun from the SW, sky fill, photo aspect) |
| `pipeline/eval_compare.py` | compare images, contact sheet, alignment scores, history; `overlay` and `refine` for pose work; `plan` for a top-down camera map |
| `data/reference/eval_cams.json` | the evaluation set (source of truth); `game/public/eval_cams.json` is a copy for the game |
| `data/photos_ref/eval/` | photos downloaded for the set, with `index.json` (author, licence, page, date, GPS) |

## Conventions

Local frame as everywhere in the project: **x east, y north, metres from the Jaffa Gate OSM node
561157424** (lat 31.7766282, lon 35.2275435; `x = (lon − 35.2275435) · 94721.7`,
`y = (lat − 31.7766282) · 110882.9`).

Each cam in `eval_cams.json`:

| key | meaning |
|---|---|
| `photo` | path relative to the project root |
| `credit` | author, licence, Commons page URL (shown on every compare image) |
| `x`, `y` | camera position in the local frame |
| `z_eye` | eye height above the ground **under the camera** (1.5–1.7 m for a standing photographer). The ground is found by ray-casting the model's ground/steps meshes, so cams follow terrain changes in rebuilds. Optional `z_ground` forces the ground height (use it when the model has a pit/moat where the photographer stood). |
| `heading` | compass degrees of the optical axis (0 N, 90 E) |
| `pitch` | degrees above the horizon (phone shots of buildings are often tilted up 5–20°) |
| `fov` | **vertical** field of view in degrees of the photo as published (crop included) |
| optional | `roll` (deg, + turns the image content clockwise), `shift_x`/`shift_y` (lens shift for perspective-corrected or off-centre crops), `covers`, `notes` |

Top-level `"render"` (optional) overrides the lighting: `sun_azimuth` (compass direction the sun is
in, default 240 = WSW), `sun_elevation` (32), `sun_strength`, `sun_color`, `sky_color`, `sky_top`,
`sky_horizon`.

## 1. Choosing photos

Aim for 8–12 photos that together cover the area, each from a distinct, walkable viewpoint. For a
street scene the minimum set is: approach from outside, the threshold (gate/passage), the first
view into the space, each long facade, each corner where a street leaves, and one view back.

Prefer, in this order:

1. **Recent** (the last ~5 years: shopfronts, paving, trees and signs change).
2. **Eye level, rectilinear lens**, not panoramas or fisheyes (`exif` tells you the focal
   length; Samsung "13 mm" = ultra-wide, fine but keep its FOV ~80–90°).
3. **Sharp, daylight, clear sky.** Night shots and crowds hide the geometry; a sky with a
   clean skyline makes the automatic score reliable.
4. **Long building edges and corners visible** (they pin the pose); tight close-ups of
   details are reference material, not eval photos.
5. Known camera model in EXIF (gives the FOV) and a free licence (CC BY / BY-SA / PD).

Commands:

```bash
python3 pipeline/eval_set.py candidates --near 60,8 --radius 30 --sheet /tmp/cand.jpg   # all downloaded photos near a point
python3 pipeline/eval_set.py candidates --grep "photos_ref/gate/" --sheet /tmp/gate.jpg
python3 pipeline/eval_set.py search "David Street Jerusalem"            # Commons full-text search (files)
python3 pipeline/eval_set.py category "Jaffa Gate"                       # files in a Commons category
python3 pipeline/eval_set.py fetch "File:David Street (20041).jpg" ...   # -> data/photos_ref/eval/ + index.json
```

`fetch` is polite (User-Agent `old-city-walker-poc/0.2 (evaluation)`, 1.5 s between requests,
honours 429 Retry-After, 1280 px thumbnails) and records author, licence, page URL, date and GPS.
`data/photos/index.json` (geosearch around the PoC) and `data/photos_ref/*/index.json` (other
agents' reference downloads) are read the same way, so `add` can fill in the credit automatically.

Commons GPS is only good to ±5–15 m and is often the place *photographed*, not the camera. Use it
as a hint at most.

## 2. Estimating a pose

Work from coarse to fine. Keep `renders/eval/cams_plan.png` open
(`python3 pipeline/eval_compare.py plan`): footprints, hero heights and every cam's position and
horizontal FOV wedge.

1. **FOV from EXIF.** `python3 pipeline/eval_set.py exif <photo>` prints make, model, focal length
   and the 35 mm equivalent, and converts it to the vertical FOV of the published image (it assumes
   a 4:3 native frame for phones / Micro Four Thirds, 3:2 otherwise, and that only the short side
   was cropped). Panoramas and heavy crops need the FOV to be fitted instead.
2. **Pitch from the horizon.** People's heads at a distance are at eye level, so the horizon is at
   the height of distant heads (for a 1.6 m eye height). With `v_h` the horizon's fraction of the
   image height from the top: `pitch = atan((2·v_h − 1) · tan(fov/2))`.
3. **Position and heading.** Identify 3–5 points whose local coordinates you know: building corners
   from `data/reference/hero_edges.md` / `data/scene_spec.json` footprints (OSM footprints are
   good; heights are not), the gate tower corners, ends of the Citadel walls. Read their image
   positions off `python3 pipeline/eval_set.py grid <cam>` (0..1 grid). Then

   ```bash
   python3 pipeline/eval_set.py resect inside_square --search 20 \
       --pt 33,13.2,0.09 --pt 38.9,15,0.166 --pt 60.4,17.7,0.367 --pt 109,13.8,0.516
   ```

   `X,Y,u` uses a vertical edge (only its column); `X,Y,Z,u,v` a full 3D point. `--search R`
   grid-searches x, y within R metres first (avoids mirror solutions), then a least-squares solve of
   `--free` (default `x,y,heading,pitch`; add `fov`, `z_eye` with enough points). The per-point
   residuals show a misidentified landmark immediately. `--write` stores the result.
4. **Render and overlay.** Try a pose without touching the JSON:

   ```bash
   blender -b build/city.blend --python-exit-code 1 -P blender/render_eval.py -- \
       --only inside_square --set inside_square.heading=83 --set inside_square.x=12 --suffix _try --fast
   python3 pipeline/eval_compare.py overlay inside_square --suffix _try
   ```

   Look at `renders/eval/inside_square_overlay_try.jpg`: top photo | model, bottom 50 % blend |
   edges (green photo, magenta model, white both) with the photo skyline (cyan) and model skyline
   (yellow). Align things the model is *sure* about first: footprint corners at street level,
   the gate tower, the Citadel wall line, the street edge / kerb, the moat railing. Do not
   align roof lines of buildings whose heights are guessed - that is what we are evaluating.
   Rules of thumb: everything shifted sideways → heading; everything too high/low → pitch;
   near objects shifted more than far ones → position; sizes wrong uniformly → FOV.
5. **Polish automatically (optional).**
   `python3 pipeline/eval_compare.py refine <cam> --params x,y,heading,pitch [--scale 2] [--write]`
   does a coordinate search on low-res renders against the score below (±1 and ±2 steps per
   parameter per iteration, halving the steps when nothing improves; ~20 s per iteration). It
   can trade pose error for model error (e.g. tilt the camera to hide a too-tall building), so
   start it close, restrict `--params`, and always check the overlay afterwards.

Pitfalls seen in this area:

- The model's moat extends under parts of the square; a camera there lands 5 m down
  (`render_eval.py` prints `EVAL WARNING ... ground under the camera`). Move the cam to where the
  photographer could stand, or set `z_ground`.
- Props (olive trees, lamp posts) sit where the real photo has none or small ones; they can hide
  the facade you are aligning. Pick viewpoints where they do not.
- Phone photos of tall facades are tilted up a lot (15–22°); verticals converge in both photo and
  render, which is correct - do not "fix" it with roll.
- Portrait photos: `fov` is still the vertical (long side) angle.

When a pose is good, record it (`eval_set.py set <cam> x=… heading=…` or `resect --write`) and run
`python3 pipeline/eval_set.py sync` to validate and copy the file to `game/public/eval_cams.json`.

## 3. Running the loop

```bash
# after every rebuild of build/city.blend (~1.5 min for 11 cams at 1280 px)
blender -b build/city.blend --python-exit-code 1 -P blender/render_eval.py
python3 pipeline/eval_compare.py            # compare images, sheet, scores, history
```

Options: `--only cam1,cam2`, `--long 1920` (resolution), `--samples 64`, `--fast` (4 samples, no
labels), `--no-labels`; any `.blend` can be evaluated (`blender -b other.blend ...`). The `.blend`
is never saved. Only the eval cams need to exist; nothing in the build has to know about them.

## 4. Reading the sheet

`renders/eval/sheet.jpg` has one cell per cam: **photo | model | overlay**, with the scores on top.
Each `renders/eval/<cam>_compare.jpg` is the large version (photo | model at 720 px) with the
credit, the blend file, the pose, the scores and the names of the labelled model objects visible
in the frame (`label` property of the build: building names or OSM ids), so a remark like "the
third building is too tall" can be traced to an OSM id.

Scores (computed at 480 px, numpy only):

| score | meaning | good |
|---|---|---|
| `sky IoU` | overlap of the sky regions. Photo sky is segmented automatically (smooth bright/blue region flood-filled from the top edge; the mask is saved as `<cam>_photo_sky.png` - check it once per photo); model sky comes from the render's alpha. | > 0.85 |
| `skyline err` | median vertical distance between the two skylines over the columns that show sky, in % of the image height. Directly readable as "the roofline is 4 % of the frame too high". | < 3 % |
| `edges F1` | Canny-like edge maps of photo and render matched within 1 % of the diagonal. Photos have far more edges (people, signs, stone joints) so it never gets near 1. | > 0.75 |
| `align` | 0.5 · sky + 0.5 · edges (edges only when the photo has no sky); the number to track. | > 0.8 |

`scores.json` holds the latest run, `history.jsonl` one line per run (time, blend path and
mtime, per-cam scores, mean). How to read changes:

- **All cams drop together after a rebuild** → something global moved: the local frame / origin,
  the ground height, a scale error, or a lighting/camera convention change. That is registration
  drift; fix it before judging geometry.
- **One cam drops** → a local modelling change near that view (a height, a footprint, a prop).
  Open its overlay: the yellow vs cyan skyline shows where.
- **Score improves while the image looks worse** (or vice versa): the scores only see
  silhouettes and strong edges, not materials, colour or detail - always look at the images.

The overlay colours: green = photo edges only, magenta = model edges only, white = both,
cyan = photo skyline, yellow = model skyline. A uniform horizontal offset of all magenta vs green
lines means the heading is off; buildings whose yellow line sits above the cyan line are too tall
(or too close).

## 5. Reusing the method elsewhere in the city

1. Pick the area's hero zone and list the views it needs (section 1).
2. `fetch_photos.py`-style geosearch or `eval_set.py search/category/fetch` into
   `data/photos_ref/<area>/` with an `index.json` (author, licence, page, date).
3. Choose 8–12 photos; `eval_set.py add <cam> <photo> --x --y --heading --fov` with first
   guesses (GPS, EXIF FOV, horizon pitch).
4. `eval_set.py grid` + `resect` on footprint corners; `render_eval.py --set ... --suffix _try`
   + `eval_compare.py overlay` until street-level corners line up; optionally `refine`.
5. Run the loop after every rebuild; turn the differences into modelling tasks, worst
   score/most visible first; keep `history.jsonl` to show progress.

Cam names should describe the view (`imperial_west`, `david_street`), not the photo, so a cam can be
re-pointed at a better photo later.

## 6. The current set (Jaffa Gate hero zone)

| cam | view | photo |
|---|---|---|
| `outside_gate` | outer plaza, gate tower, the 1898 breach and the Citadel's west tower | Bukvoed 2024, CC BY 4.0 |
| `gate_outer` | the gate's outer face with the entrance and the blocked arch | Bukvoed 2024, CC BY 4.0 |
| `passage` | inside the L-shaped passage looking out through the inner arch | Bukvoed 2024, CC BY 4.0 |
| `inside_square` | just inside: New Imperial Hotel left, Citadel north wall right | Israel Preker 2022, CC BY 2.5 |
| `imperial_west` | New Imperial Hotel facade, looking west to the gate | Israel Preker 2022, CC BY 2.5 |
| `north_side` | the north side (hotel, arched shopfronts) from the moat | Bahnfrend 2019, CC BY-SA 4.0 |
| `east_end_david` | the east end: Swedish centre and the David Street entrance | Bahnfrend 2019, CC BY-SA 4.0 |
| `citadel_moat` | Citadel NE tower, north wall and moat, looking back west | Sasha1506 2021, CC BY-SA 4.0 |
| `back_to_gate` | from the Citadel's NE corner back to the gate | Bukvoed 2024, CC BY 4.0 |
| `citadel_east` | Citadel east side / entrance and Christian Information Centre, looking south | מקף־עברי 2025, CC BY-SA 4.0 |
| `david_street` | top of David Street looking east (dusk) | Rhododendrites 2017, CC BY-SA 4.0 |

Full credits and page links are in `eval_cams.json` and on each compare image.

## Limitations

- Poses are hand/auto-fitted against a model that is itself approximate; expect ~1–2 m and
  ~1° error. Re-fit a pose only when the *reference* geometry (footprints, gate, Citadel walls)
  changes, never to make a guessed height look right.
- The photo sky mask fails on white overcast skies behind pale stone; the per-cam
  `<cam>_photo_sky.png` shows it. Low-sky photos (passage, David Street) rely on edges only.
- Lighting is a fixed afternoon sun; photos at other times of day differ in shadows, which the
  edge score partly sees.
