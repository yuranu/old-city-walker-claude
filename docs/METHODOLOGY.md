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

## 8. Lessons from the Jaffa Gate pass (apply them to the next area)

**Street profiles.** A street with a strong character (a souq) gets a *profile*: a default facade
override applied to every facade that fronts its centreline, e.g. `souq_profile()` in
`make_spec.py` for David Street (closed dukkan shops with teal panelled steel doors and padlock
bars, raised stone thresholds, shed canopies on scroll brackets, blade boards; tie-beams and
centre-line manholes from `dressing.py`). Hand overrides for named buildings still take
precedence. Write one profile per street type (souq, residential alley, market square) from the
reference notes and reuse it.

**Manual buildings for OSM gaps.** When every photo shows a continuous street wall that OSM does
not map, add a polygon to `MANUAL_BUILDINGS` with the reason and the photos. It is given the
lowest priority, so it only fills space the OSM footprints leave free.

**Verify the reference against the plan, not just the photos.** The Phasael tower had been placed
at the wrong corner of the Citadel, and the gate tower was 2 m too tall. Have researchers check
named landmarks against several photos and record the camera position for each claim.

**Depth precision.** Anything that sits just in front of a surface (window cards, signs, plaques)
must be offset enough for the distance it is seen from: about 1–2 cm close up, 5 cm for context
buildings 150–300 m away (near plane 0.2 m, 24-bit depth). Blended decals instead use polygon
offset in the engine and need no physical offset.

**Weathering and vegetation: less is more.** Generic dark streak and damp decals and ground stains
read as smears and were removed after review. Grime comes from the shader (a gradient at the
wall foot) and from texture variation. Vegetation goes only where it grows: small dry tufts in
the joint between wall and paving, capers high on old wall faces. Never put it in open paving or
in passages.

**Untextured surfaces stand out immediately.** Every large surface needs a texture: doors (atlas
cells), canopies (corrugated sheet), lawns. Flat colours are fine only for thin things such as
cables, tubes and small fittings.

**Walk the build, not only the renders.** The user's in-game screenshots found issues that the
evaluation renders did not (floating tufts, black streaks, flat doors). After each build, check
the fixed viewpoints in the game, including viewpoints that face away from the hero area: the
horizon has to be filled too, using context massing from an extra OSM extract if needed.

## 9. Scaling to the whole walled city: sectors

The Jaffa Gate area was one scene. The walled city (2,600 buildings, 0.86 km², 35 m of fall) is
built, loaded and worked on **by sector**.

**Sectors** (`pipeline/sectors.py`, `data/sectors.json`). The walled-city polygon
(`data/oldcity_polygon.json`, derived from the OSM wall circuit, including the Haram) is cut into 12
sectors along quarter lines, gates and main streets. The Haram is its own sector, using the exact
enclosure. A building belongs to the sector holding its centroid; anything outside every sector
goes to the nearest one (`FORCE_SECTOR` for exceptions). Each sector is a unit of research (notes
`data/reference/<sector>.md`), building and streaming.

**Spec → parts.** `make_spec.py` writes:
* `data/spec/base.json`: ground, kerbs, Jaffa Gate fortifications, the OSM wall circuit, context.
* `data/spec/<sector>.json`: buildings, props, steps, cables, beams, decals.
* `data/spec/index.json`.
* The legacy single scene (base + Jaffa Gate) for the evaluation loop.

`build_city.py --part base|<sector>` builds one part. A sector exports `sectors/<id>.glb` at full
detail plus `sectors/<id>_lo.glb`, a massing LOD (plain walls, roofs, window cards, domes;
landmarks keep their silhouette). Textures live once in `base/materials.glb`; every other GLB is
exported without images, and the game swaps materials by name. `build.sh` builds base + 12 sectors
in parallel (~40 s) and `write_manifest.py` writes `game/public/sectors.json` for streaming.

**Streaming (game).** The game:
* keeps the base resident;
* keeps every sector's LOD resident, swapping each 96 m cell between hi and lo by distance;
* loads a sector's hi when the player comes within ~150 m;
* builds the collision BVH per chunk in a worker.
Teleports wait for the hi geometry around the destination.

**Street level from a survey** (`pipeline/terrain_street.py`, `docs/TERRAIN.md`). Open DEMs sit
metres above the street inside the walls. The street surface is a Gaussian-process fit through 425
spot heights from the 1865 Ordnance Survey of Jerusalem, with explicit flats (Haram esplanade,
Western Wall plaza) and local flats in `make_spec.LOCAL_FLATS` (the Sepulchre parvis). Everything
reads the ground from `street_z`. Never hard-code absolute heights; landmarks measure from
`bd["ground"]`, and cameras from the ground under them.

**Rules that carry a whole city:**
* `roofscape.py`: heights from OSM where present, otherwise by footprint and quarter, plus the
  vernacular field of shallow lime domes. Weathered grey roof decks with whiter domes are what
  read from the walls and the Mount of Olives.
* `infill.py`: OSM misses buildings, and inside the walls nearly everything is built up. Street
  corridors are measured from the existing street walls, mapped areas are kept open, and a 9 m
  frontage band is filled where nothing is mapped (lowest priority, low heights).
* `SOUQ_STREETS` (`make_spec.py`): every facade fronting a market street gets the souq profile.
  Each street sets its share of shop rows and canopies; covered souqs get no canopies.
* `stairs.py`: lanes steeper than 7 % and every OSM steps way become runs of treads (risers about
  14 cm), clipped to the open street.

**Landmarks** (`blender/landmarks.py` registry). Hand-modelled buildings replace the generic builder
through `LANDMARKS = {osm_id: fn(mbs, bd, gen, place, lod)}` in their own modules:
`landmarks_city.py` (churches, synagogues, minarets), `landmarks_haram.py` (Temple Mount, Western
Wall) and `landmarks_gates.py` (gates, wall circuit). A module that is missing, mid-edit or failing
falls back to the generic building with a warning (`LANDMARKS_STRICT=1` makes it fatal), so
parallel workers never break each other's builds.

**Working in parallel.** One owner per file:
* researchers write `data/reference/<sector|landmark>.md` and photo indexes;
* landmark and gate workers own their module and notes;
* spec changes (records, clips, flats, ground holes, wall heights) go to the spec owner as exact
  requests, with polygons and ids;
* the spec owner keeps `make_spec.py`, `dressing.py`, `build_city.py`.
Every request names its evidence (photo, OSM id, survey value).

**Checking a part of the city.** `blender/render_city.py` loads the exported GLBs near the cameras
(as the game would) and renders named viewpoints with heights relative to the ground. In-game,
`window.game.teleport()` and `bench()`, and the F3 overlay (sectors in hi, memory).

### Lessons from the expansion
* **Key overrides by position, not index.** Footprint cleaning moves where rings start. A facade
  override carries `"at"`, the edge midpoint, and is matched to the nearest edge.
* **Let a photo-matched facade switch off the rules** (`"auto": false`). Otherwise random signs and
  shutters reappear on facades that were measured from photographs.
* **Measure heights against a calibrated camera.** Plain image ratios understate a wall 10 m
  behind the gate face by 20-25 %.
* **Watch for duplicated OSM features**: walls drawn twice, enclosure boundaries tagged as walls,
  marketplace areas over covered souqs. Dedupe and exclude explicitly, with the reason in a comment.
* **Everything at city scale needs an index.** A per-item loop over all steps or all buildings
  turns a 10 s spec into minutes. Use STRtrees, local clipping and vectorised terrain lookups.
* **Budget the whole, not the part.** 5.5M triangles at full detail is fine streamed, but the
  per-frame draw calls and shadow passes decide whether an integrated GPU keeps up.
