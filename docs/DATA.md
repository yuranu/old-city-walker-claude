# Data: sources, pinning and licences

## What is versioned, and why

The rule: **version what was authored, or what cannot be obtained again as it was; reference
everything else.**

| | Where | Why it is in git |
|---|---|---|
| OSM snapshot | `data/raw/osm_oldcity.osm`, `osm_west.osm` | the tables refer to building ids and geometry in this exact snapshot; the OSM API cannot return it again |
| terrain tiles | `data/raw/terrain/*.png` (6 tiles, 0.6 MB) | build input; a snapshot keeps the build offline and immune to upstream changes |
| Poly Haven textures | `data/raw/polyhaven/<id>/` (9 maps at 2k, 21 MB) | build input, as above; `info.json` records each file's source URL and MD5 |
| 1865 survey transcription | `data/raw/terrain/os1865_*.csv` | transcribed by hand from the scan |
| research notes, overrides, profiles | `data/reference/` | authored |
| evaluation cameras | `data/reference/eval_cams.json` | authored (poses solved and refined against photos) |
| photo provenance | `data/photos/index.json`, `data/photos_ref/*/index.json` | title, Commons page, author, licence, date, position: the bibliography |
| QA levels, regions, findings, Street View panoramas | `data/qa/` | authored |
| sector layout | `data/sectors.json` | generated once, then kept so sector ids stay stable |
| figures | `docs/img/` | the README shows them |

Not versioned:

| | How you get it |
|---|---|
| photographs | `./fetch_data.sh --photos` (from the URLs in the `index.json` files); the game loads them from Commons |
| Street View stills | used during the research for QA comparisons; never stored, and the tooling that fetched them is not included |
| the built city | `./build.sh`; the live site and the release archives carry it |

The snapshots never change, so they cost their size once (about 32 MB with the OSM files, much
less compressed) and never grow the history. Built models do change with every rebuild, so they
are never versioned.

`data/inputs.sha256` holds the SHA-256 of every pinned file:

- **Build inputs** (`data/raw/`): `build.sh` stops on a mismatch, since an altered file would
  change the city silently. To replace a snapshot deliberately, update its line
  (`sha256sum <file>`) in the same commit.
- **Photographs**: an upload can be deleted or replaced on Commons at any time.
  `fetch_data.sh --photos` skips what it cannot download and lists it, then warns about missing
  or changed pinned photos and names the evaluation cameras that depend on them. The evaluation
  skips those cameras; the game shows a notice in place of the photo, with its credit and link.

## Sources and licences

- **OpenStreetMap**: map data © OpenStreetMap contributors, available under the
  [Open Database Licence](https://opendatacommons.org/licenses/odbl/). The built models are derived
  works and carry the same attribution. The snapshot is frozen: taken on 2026-10-19 with the API
  `map` call (newest edit in it: 2026-10-19 14:58 UTC), and never refreshed since.

  | File | Bounds (lat, lon) | Size |
  |---|---|---|
  | `data/raw/osm_oldcity.osm` | 31.7700-31.7825, 35.2255-35.2385 | 8.5 MB |
  | `data/raw/osm_west.osm` | 31.7715-31.7815, 35.2215-35.2256 | 2.3 MB |

  Both are listed in `data/inputs.sha256`, so an accidental change is caught. `fetch_data.sh`
  never overwrites them. Refreshing from live OSM is a deliberate step: building ids, overrides
  and tables in `data/reference/` refer to this snapshot and must be re-checked after it.
- **Ordnance Survey of Jerusalem, 1864-65** (1:2500, Capt. C. W. Wilson R.E.; public domain):
  spot heights and bench marks transcribed from the Princeton University Library scan (the IIIF
  source is in the CSV header). See [TERRAIN.md](TERRAIN.md).
- **Elevation**: [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) (terrarium
  encoding, zoom 15; SRTM-derived for this area).
- **Textures**: [Poly Haven](https://polyhaven.com), CC0, snapshotted in `data/raw/polyhaven/`
  (asset ids and roles in `pipeline/fetch_textures.py`). The generated textures (paving,
  shutters, signage, landmark finishes) are made by the pipeline.
- **Photographs**: [Wikimedia Commons](https://commons.wikimedia.org), each under its own licence
  (CC BY, CC BY-SA, GFDL, CC0, public domain). Author, licence and source page are recorded per
  photo in the `index.json` files, shown in the game, and printed on every evaluation comparison.
- **Google Street View**: the game only links to it (**G**). During the research, Street View
  stills served as references for side-by-side QA comparisons ([QA.md](QA.md)). No stills are
  stored here, and the tooling that fetched them is not part of this repository.

## The local frame

Everything uses metres from the Jaffa Gate OSM node 561157424 (lat 31.7766282, lon 35.2275435):
x east, y north, z up. `pipeline/osm_to_local.py` projects the OSM data into it; the conversion
formulas are in [EVALUATION.md](EVALUATION.md#conventions).
