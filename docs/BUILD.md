# Building and running from source

Everything the game loads is built from the repository plus downloaded inputs that are pinned by
checksum. Nothing prebuilt is fetched: a source build never uses a release archive.

## Requirements

- **Blender 5.2** (LTS; `blender` on the PATH). `build.sh` refuses other major.minor versions,
  since the exported geometry depends on it.
- **Python 3.14** with a virtual environment (`requirements.txt`: shapely, numpy, Pillow). Pillow
  needs libraqm for the shaped Hebrew and Arabic signage (most Linux distributions build it in).
- **Node 22+** for the game (Vite, three.js).
- Several GB of disk for inputs, blend files and outputs, and memory for 4 parallel Blender
  processes (set `JOBS=2` on a laptop that runs hot). Developed on Arch Linux; other Linux
  distributions should work as well.

## 1. Set up

```bash
git clone https://github.com/yuranu/old-city-walker-claude.git && cd old-city-walker-claude
python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r requirements.txt
npm --prefix game install
```

## 2. Fetch the inputs

```bash
./fetch_data.sh             # terrain tiles + Poly Haven textures, verified against data/inputs.sha256
./fetch_data.sh --photos    # optional: the reference photographs (evaluation and research, ~10 min)
```

The OSM snapshot and the 1865 survey transcription are versioned and are not fetched. The
downloads are checked against `data/inputs.sha256`; a mismatch stops the build rather than letting
a changed upstream file change the city silently. See [DATA.md](DATA.md).

The build itself needs no photographs. They serve the evaluation loop, the research notes and the
QA comparisons; the game's **P** key loads them straight from Wikimedia Commons.

## 3. Build

```bash
./build.sh                  # spec -> textures/signs -> Blender, base + 12 sectors in parallel -> game/public
./build.sh --preview ""     # the same without the preview renders
PARTS="base s04_sepulchre" ./build.sh    # rebuild only some parts
PARTS=none ./build.sh       # only the legacy Jaffa Gate scene (city.glb)
JOBS=2 ./build.sh           # fewer parallel Blender processes
```

Stages, all in `build.sh`: OSM to the local frame (`osm_to_local.py`), street levels
(`terrain_street.py`), the scene spec (`make_spec.py`, shapely), generated textures and signage,
the game data (`export_game_data.py`: plan, photo list, evaluation cameras), then Blender builds
the base (terrain, walls, landmarks, materials) and every sector in parallel, `write_manifest.py`
writes the streaming manifest, and `blender/audit.py` reports coplanar overlaps.

Outputs go to `game/public/` (`sectors.json`, `base/`, `sectors/`, `city.glb`, `plan.json`,
`photos.json`, `eval_cams.json`), all ignored by git, and to `build/` (blend files, logs).
The pipeline and its tables are described in [METHODOLOGY.md](METHODOLOGY.md).

## 4. Run

```bash
npm --prefix game run dev   # http://127.0.0.1:5173
```

URL parameters: `?x=60&y=8&h=90` starts at local metres (x east, y north from the Jaffa Gate OSM
node) facing compass heading `h`. `?cam=<name>` loads an evaluation camera and `&clean=1` hides
the HUD. `?sectors=0` forces the single legacy scene (`city.glb`, the Jaffa Gate area). **F3**
shows which sectors are at full detail; integrated GPUs run the city at about 6-10 ms a frame at
1024x768.

## 5. Static build, release, deploy

```bash
npm --prefix game run deploy:build    # game/dist: meshopt-compressed models, large files split
npm --prefix game run preview:dist    # check it at http://127.0.0.1:4173
release/make_release.sh               # build/release/old-city-walker-<version>.zip (see release/README.md)
deploy/upload_staged.sh               # the live site (Cloudflare Worker; needs the author's account)
```

`game/dist` is plain static files: any web server can host it.

## Evaluation and QA

The photo-matched evaluation ([EVALUATION.md](EVALUATION.md)) needs the reference photos
(`./fetch_data.sh --photos`). The QA loop ([QA.md](QA.md)) drives the running game in headless
Chrome and needs the dev server.
