# Old City Walker

A walkable, geo-registered recreation of Jerusalem's walled Old City built from open data. It is
modelled in Blender from OpenStreetMap footprints, an 1865 survey of street levels and photo-based
research, and walked in a browser (three.js). Every point in the game maps to a real lat/lon.
Shops are closed and there are no people.

![the walled city from the Mount of Olives](docs/img/city_from_olives.jpg)

* **The whole walled city**, streamed by sector: 2,600 buildings, 0.86 km², 35 m of fall from
  Jaffa Gate to the Western Wall plaza. Market streets have closed shopfronts and canopies,
  covered souqs and passages are vaulted, and steep lanes are stepped. Domed roofscapes, gates
  and the wall circuit are built, along with the landmarks: the Holy Sepulchre, the Temple Mount,
  the Redeemer, the Hurva, minarets and churches.
* **The Jaffa Gate area** (the first, hero area): photo-matched facades, signage, fortifications.

![Christian Quarter from above](docs/img/city_aerial.jpg)
![in the game: Khan ez-Zeit and the Holy Sepulchre parvis](docs/img/ingame_streets.jpg)
![hero area](docs/img/hero_views.jpg)

The process is a reusable playbook in [docs/METHODOLOGY.md](docs/METHODOLOGY.md) (§9: scaling to
the whole city). The photo-matched evaluation loop is in [docs/EVALUATION.md](docs/EVALUATION.md),
and the street-level terrain in [docs/TERRAIN.md](docs/TERRAIN.md).

## Play

```bash
cd game && npm install && npm run dev        # http://127.0.0.1:5173
```

Click to walk: **WASD** + mouse, **Shift** run, **Space** jump.
**P** shows the nearest real geotagged photo (Wikimedia Commons, with author and licence) and **N** the next one.
**G** opens the same spot and heading in Google Maps Street View. **O** toggles ambient occlusion and
**F3** shows performance.
URL `?x=60&y=8&h=90` starts at local metres (x east, y north from the Jaffa Gate OSM node) facing
compass heading `h`. `?cam=<name>` loads an evaluation camera and `&clean=1` hides the HUD.

`game/public/city.glb` (the Jaffa Gate area) is committed (Git LFS), so the game runs without the
build pipeline; it is refreshed at milestones. The streamed whole city (`game/public/sectors.json`,
`base/*.glb`, `sectors/*.glb`, ~440 MB) is built locally by `./build.sh`. The game uses it when
present and falls back to `city.glb` otherwise. Integrated GPUs run it at about 6-10 ms per frame at
1024x768. F3 shows which sectors are at full detail, and `?sectors=0` forces the single scene.

## Rebuild

Requirements: Blender 5.x (with system Python 3.14, as on Arch), Python 3.14 with a venv, Node.

```bash
python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r requirements.txt
./fetch_data.sh          # textures (Poly Haven, CC0), photo metadata; the OSM snapshot is versioned
./build.sh               # terrain -> spec -> textures/signs -> Blender: city.glb + base and 12 sectors
                         # in parallel (~2 min) -> sectors.json -> audit
PARTS="s04_sepulchre" ./build.sh --preview ""   # rebuild only some parts
./build.sh --preview ""  # skip preview renders
```

Optional: `.venv/bin/python pipeline/fetch_ref_photos.py` restores the research photographs listed
in the `index.json` files (only those used by the evaluation loop are versioned).

## Pipeline

```
data/raw/osm_oldcity.osm (pinned OSM snapshot)
  pipeline/osm_to_local.py      OSM -> metres around the Jaffa Gate node (incl. multipolygons)
  pipeline/make_spec.py         shapely: footprints (overlaps resolved), tiers, ground regions,
                                kerbs, steps, facades (facades.py + hero.py), plaques from OSM
                                street names, dressing (dressing.py)  ->  data/scene_spec.json
  pipeline/gen_textures.py      paving, setts, closed-shop door/shutter atlas, cut-outs, decals
  pipeline/gen_signs.py         signage atlas with shaped Hebrew/Arabic (Pillow + raqm)
  blender/build_city.py         facade_build.py, fortifications.py, props.py -> city.glb
  blender/audit.py              coplanar-overlap / degenerate / open-edge audit
  pipeline/eval_set.py, blender/render_eval.py, pipeline/eval_compare.py
                                photo-matched evaluation renders and scores
game/                           Vite + three.js + three-mesh-bvh walker
```

| Detail tier | Area | Content |
|---|---|---|
| hero | gate, square, east end | photo-matched facades, full dressing |
| mid | rest of the walkable area | rule-based facades |
| context | ~100 m around | massing, window cards, domes, rooftop rooms and clutter |

## Repository layout and what is versioned

```
pipeline/  blender/  game/  docs/       code and documentation
data/raw/                               pinned inputs (OSM snapshot, terrain tiles) - LFS
data/reference/                         research notes, edge tables, evaluation cameras
data/photos*/**/index.json              photo metadata (source, author, licence)
data/photos*/  (selected .jpg)          photos used by the evaluation loop - LFS
game/public/                            runtime data: city.glb, plan/photos JSON, in-game photos - LFS
```

Not versioned (regenerated): `.venv`, `node_modules`, `build/`, `renders/`, `data/textures/`,
`data/scene_spec.json`, `data/osm_local.json`, bulk research photos.

## Data and licences

- Map data © OpenStreetMap contributors, ODbL (`data/raw/osm_oldcity.osm`).
- Photographs: Wikimedia Commons, each under its own licence (CC BY, CC BY-SA, public domain).
  Author, licence and source page are recorded in each `index.json` and in `game/public/photos.json`,
  and shown in the game.
- Textures: Poly Haven (CC0), downloaded at build time. Elevation: AWS Terrain Tiles (SRTM, public domain).
- Google Maps / Street View is used only as a deep link. Nothing is scraped or downloaded.

## Findings so far

- OSM footprints, walls, gates, steps and street furniture are excellent. Heights are almost
  absent and come from photos.
- Open DEMs are useless at street scale. The ground is modelled as regions (streets, road below
  kerbs, moat, courtyard) with step runs.
- Flicker came from coplanar geometry, mostly opening floors against the ground and overlapping
  OSM footprints. The audit drove it from 180 m² to ~1 m² of overlap.
- Commons GPS is ±5–15 m. Camera poses for evaluation are refined visually against the model.
- The photo-matched comparison is the most useful signal: it showed, for example, that the plaza
  uses modern grey lamp poles and slatted bins rather than the expected black lanterns.

| | |
|---|---|
| ![eval](docs/img/eval_back_to_gate.jpg) | ![eval](docs/img/eval_citadel_moat.jpg) |
| ![props](docs/img/props_lineup.jpg) | ![signs](docs/img/signs_atlas.jpg) |
