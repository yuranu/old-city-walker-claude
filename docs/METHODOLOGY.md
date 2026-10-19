# Recreating a part of the Old City — methodology

This is the playbook developed on the Jaffa Gate area. It is written so the same process can be
applied to any other part of the Old City (Damascus Gate, the Muristan, the Jewish Quarter
cardo, …). The goal is a place that is *recognisably that place* when you walk it, built from
open data, and still playable.

The loop: **acquire → reference → specify → build → verify (audit + photo-matched evaluation) →
fix → repeat**. Every judgement call lives in a small number of Python tables that cite the
photograph they came from. The geometry builders are generic and shared.

---

## 0. Pick the area and its detail tiers

Choose an anchor (a gate, a square, a landmark) and draw three zones in `pipeline/make_spec.py`:

| tier | where | what gets built |
|---|---|---|
| **hero** | what the player sees close up: the square, the gate, the first alley | photo-matched facades, every opening dressed (surrounds, sills, keystones, grilles, shutters), string courses and cornices, balconies, signs, lanterns, AC units, cables, drainpipes, spouts with streaks, street furniture, litter, plants |
| **mid** | the rest of the walkable area | rule-based facades (openings, sills, spouts, cables), no hand overrides |
| **context** | the skyline around it (≈100 m beyond) | massing with parapets, domes, rooftop rooms, water heaters/tanks/dishes |

`HERO_ZONE` is a polygon; `POC` and `CONTEXT` are boxes. A building's tier is decided by its
centroid. Budget: hero ≈ 20 buildings per area is manageable by hand.

## 1. Acquire open data (automatic)

`./fetch_data.sh` — OSM through the API `map` call (Overpass is often overloaded), AWS terrain
tiles, Commons geotagged photos, Poly Haven CC0 textures. Change the bounding boxes and origin
node to move to another area; the local frame is metres from a named OSM node, so any point
maps exactly to lat/lon.

What you get and how far it can be trusted:
* **OSM footprints** — excellent in the Old City; overlapping/broken polygons do exist and are
  cleaned automatically (§3).
* **OSM street furniture** — use it where present (trees, benches, boards, bins): real positions
  beat procedural ones.
* **Heights** — almost never in OSM. Must come from photographs (§2).
* **Terrain** — open DEMs (30 m) are useless at street scale. Ground is modelled as regions
  (streets, steps, moats, courtyards) with explicit levels and step runs from OSM `highway=steps`
  and photos.

## 2. Reference research (agents, in parallel)

For each sub-zone of the hero area, one researcher agent:
1. scans the geotagged Commons photos already downloaded (contact sheets), pulls more from the
   relevant Commons categories (polite: 1.5 s between requests, honour 429, standard thumbnail
   widths), keeps author/licence metadata;
2. writes structured notes to `data/reference/<zone>.md`, **mapped onto footprint edges**:
   `data/reference/hero_edges.md` lists every hero building's edges with length and facing, so a
   note reads "w290812336 edge 2 (faces 174°): 7 bays, ground floor shop arches…";
3. ends with a prioritised "model checklist".

Notes record dimensions estimated from people (1.7 m) and doors (2.2 m), counts (bays, storeys),
shapes (round/pointed/segmental arches), materials and colours, signage texts in all three
scripts, street furniture, and a confidence per item with the photo it came from.

## 3. Specify (pure Python, `pipeline/`)

`make_spec.py` turns OSM plus tables into `data/scene_spec.json`. All 2D decisions happen here with
shapely, so Blender only builds what is listed:
* **footprints**: made valid, simplified, overlaps resolved by priority (hero > mid > context,
  then area), clipped against walls/citadel/moat → no coplanar walls or roofs anywhere;
* **heights/styles**: `HEIGHTS`, `ASHLAR`, `SHOPS`, `DOMES`, `HIPPED` tables + `hero.BUILDING`;
* **facades**: `facades.py` lays out every exposed edge (bays, storeys, shop rows, doors,
  windows, balconies, bands, cornice, signs, fixtures, decals, cables) from rules;
  `hero.py` overrides individual facades from the reference notes;
* **ground regions**: street, road (lower by a kerb), moat, courtyard, each triangulated after
  clipping to buildings and steps — the ground never lies under another surface;
* **steps**: step runs along a street centreline, clipped to the open street;
* **dressing** (`dressing.py`): real OSM furniture first, then rules — bollards and lamps along
  kerbs, litter concentrated in corners and at thresholds, boxes/crates/carts by closed shops,
  weeds at wall feet, capers in the walls, rooftop clutter on every flat roof, cables across
  narrow streets.

Textures that open libraries lack are generated (`gen_textures.py`: paving slabs, setts, a
closed-shop door/shutter/window atlas with normals, cut-outs, decals) and signs are rendered
with correct Hebrew/Arabic shaping (`gen_signs.py`).

## 4. Build (`blender/`, headless, ~15 s)

`build_city.py` reads the spec: `facade_build.py` (walls with recessed openings, atlas infill,
fan grilles on dark backing, thresholds, frames, sills, keystones, grilles, open shutters,
bands, cornices, balconies, awnings, signs, decals, cables, fixtures), `fortifications.py`
(walls, gate, citadel), `props.py` (procedural prop library; props are linked duplicates).
Materials are a fixed contract (`materials.py`) shared with the game: stone gets a per-building
tint through vertex colour; `cut` = alpha-tested, `decal` = blended with polygon offset; objects
with `nocol=1` are excluded from collision.

## 5. Verify

1. **Geometry audit** — `blender/audit.py` finds coplanar overlapping faces (the cause of
   flicker), degenerate triangles and open edges, with locations. Target: no overlap above a few
   cm². Common causes and fixes: floors of openings vs ground (thresholds / skip the floor
   reveal), overlapping OSM footprints (priority difference), segment boxes sharing a top plane
   (offset alternate segments by ≥1 cm), decals on top of each other (stagger offsets).
2. **Photo-matched evaluation** — `docs/EVALUATION.md`: a fixed set of real photographs with
   recovered camera poses; every build is rendered from those poses and composed side by side
   (`renders/eval/sheet.jpg`) with an alignment score. Read the sheet, write the differences as
   modelling tasks, fix, rebuild.
3. **In-game checks** — walk tests through every passage and stairway with `window.game.step()`,
   frame-time measurements with `window.game.bench()` at fixed viewpoints, screenshots.

## 6. Iterate

Each pass: pick the biggest visible differences from the evaluation sheet → add or correct
entries in `hero.py`, the tables, or the dressing rules → `./build.sh` → audit + eval sheet +
in-game check. Keep the per-pass notes in the README findings.

## 7. Performance rules of thumb (Intel Iris Xe class GPU)

* merge static geometry per material at load (draw calls ≈ number of materials);
* props are low-poly (litter ≤ 30 tris, furniture ≤ 300) and never collide unless they block
  walking; cut-out cards for foliage, grilles and railings;
* AO at reduced resolution, dynamic resolution scaling, light-space-snapped shadows;
* context tier is massing only.
