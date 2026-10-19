# Street-level terrain for the walled Old City

`pipeline/terrain_street.py` builds the walkable ground level for the whole walled city and its
surroundings. Run it again whenever its inputs change:

    .venv/bin/python pipeline/terrain_street.py          # writes data/terrain_street.json + .png, prints validation
    .venv/bin/python pipeline/terrain_street.py explore  # parameter search (leave-one-out)

```python
from terrain_street import street_z, street_z_asl
street_z(x, y)               # m relative to the street at the Jaffa Gate node (local 0,0); scalars or arrays
street_z(x, y, under=True)   # lower level where a street runs underneath another (Al-Wad under Chain St)
street_z_asl(x, y)           # same, metres above sea level
```

## Output: `data/terrain_street.json`

| key | content |
|---|---|
| `x0, y0, step, nx, ny` | grid -360..1008 (x) by -508..852 (y), 4 m; `z[j][i]` is at `x0+i*step, y0+j*step` |
| `datum_asl` | 770.58: the height above sea level of z = 0 (the street at the Jaffa Gate node) |
| `z` | walkable street level, with the flats burned in |
| `z_ground` | the same continuous field without the flats; use it for the foot of a flat's retaining walls |
| `flats` | polygons kept exactly level: `name, z, z_asl, area_m2, source, polygon` |
| `underpasses` | lower streets that pass beneath another street (`street_z` returns the upper level) |
| `pinned_profiles` | street profiles held to surveyed levels (the Chain Street causeway) |
| `platforms_info` | the Dome of the Rock's upper platform, measured but deliberately **not** a flat (see below) |
| `anchors_os1865`, `anchors_modern` | every anchor and its source |
| `sources`, `method` | provenance |

`street_z()` checks the flats first, then interpolates bilinearly on `z_ground`, clamped at the grid
edge. `data/terrain_street.png` is a preview, git-ignored like the other `data/*.png` files. It shows
a hillshade with contours every 2 m (bold every 10 m), the city walls, the sectors, the flats (cyan),
OSM steps (red), the anchors (yellow inside the walls, orange outside), the transects A–E (magenta)
and the modelled level at each gate.

## Why not the DEM directly

The only open DEM, AWS Terrain Tiles (terrarium, z15, derived from SRTM), is a surface model with
~30 m effective resolution. Old City streets are 3–6 m wide, so the DEM records roofs and domes.
Compared with the surveyed street anchors, the **raw DEM is a median 7.0 m too high** inside the
walls: +5.6 m at Jaffa Gate, +7.1 m on the Haram, +8.9 m at the Holy Sepulchre parvis, +9.9 m at the
Western Wall prayer area. A lower envelope (morphological opening over an 84 m window, then a 16 m
Gaussian) is still a median 6.3 m too high, with 3.5 m scatter. Calibrating it against a handful of
landmark elevations would not have been enough, so most of the model's information comes from survey
spot heights.

## Method

1. **Regional trend.** Sample the DEM on the 4 m grid. Take its lower envelope: a min filter then a
   max filter, half-width 10 cells, followed by a Gaussian with σ = 4 cells. This removes bumps
   narrower than ~80 m, such as buildings and domes.
2. **Anchors.** There are 425 spot heights and bench marks from the **Ordnance Survey of Jerusalem,
   1:2500, surveyed 1864–65 by Capt. C. W. Wilson R.E.** It is public domain; the scan used is
   Princeton University Library ark:/88435/p8418q700. Heights are in feet above the Mediterranean.
   - Transcribed by eye from 875×950 px tiles of the IIIF scan, then checked by drawing every
     transcribed position back onto the scan.
   - Cross-validation flagged two values for re-reading. One misread was corrected (2434 → 2464 ft;
     a seam runs through the figure), and one with an illegible digit is excluded
     (`data/raw/terrain/os1865_spot_heights.csv`).
   - Georeferenced with an affine transform fitted to 18 OSM control points: gates, Haram corners,
     wall corners, the Edicule, Hezekiah's Pool and St Anne's (`os1865_control_points.csv`). The
     RMS residual is 6.2 m, from a cloth-mounted folding map with linen seams. Overlaying OSM streets
     on the georeferenced scan shows that the streets line up.
   - Bench marks are cut into walls. Compared with the spot-height surface, they sit a median
     **0.34 m** above the ground, and that amount is subtracted from them.
   - **Datum check:** Warren's levels, which are on the OS 1865 datum, agree with the modern Caspi
     values: Mughrabi Gate 736.4 vs 736.5, Double and Triple Gates 725.4 vs 725.9. The old and
     modern datums therefore agree to about 0.5 m.
3. **Correction field.** A Gaussian process (Matérn-3/2, length 45 m, prior σ 4 m) fits the residual
   between each anchor and the envelope.
   - Noise σ: 0.6 m inside the walls, 1.5 m outside (1865 open ground has been landscaped since), and
     0.3 m for the pseudo-anchors.
   - Prior mean: the median residual of the anchors outside the walls (−1.8 m). Far from any anchor,
     the field returns to the envelope minus 1.8 m.
   - Pseudo-anchors:
     - every 8 m along the edges of the Western Wall plaza flats, except along the Haram wall and
       under Wilson's Arch;
     - along the Chain Street causeway (`PINNED`), where Al-Wad passes 8 m below.
   - Leave-one-out cross-validation chose the parameters (`explore`). The envelope settings barely
     matter: LOO RMS changed by less than 0.2 m between no envelope and a 160 m window, because the
     anchors dominate.
4. **Flats.** The flats are burned into `z`. Excluded from the fit:
   - Haram anchors (the Haram is a flat);
   - the 1865 Mughrabi Quarter and Wailing Place anchors (cleared and regraded in 1967);
   - the raised Omariya rock court;
   - the one illegible value.
5. **Datum.** z = 0 is the modelled street at the Jaffa Gate node, 770.58 m asl. The Jaffa Gate
   bench mark is 2528.2 ft = 770.60 m on the jamb, ~770.26 m at the ground; the field adds ~0.3 m
   from the slightly higher square.

## Anchors table (key points; all 425 OS values are in the CSV)

| anchor | value (m asl) | source | confidence | model |
|---|---|---|---|---|
| Jaffa Gate, bench mark on the jamb | 770.60 (2528.2 ft) | OS 1865 | high | 770.39 ground |
| Omar Ibn el-Khattab Sq. bench mark | 769.68 (2525.2 ft) | OS 1865 | high | 769.42 ground |
| David St top, bench mark | 763.07 (2503.5 ft) | OS 1865 | high | 763.18 |
| David St / Suq al-Lahamin bench mark | 755.29 (2478.0 ft) | OS 1865 | high | 754.94 |
| Chain St at the Gate of the Chain | 737.31 (2419 ft) | OS 1865 | high | 736.95 |
| Gate of the Chain level | 737.3 | Warren 1884 map XXXIV (templemount.org Table I) | high | 737.1 (flat) |
| Mughrabi Gate sill | 736.5 (Warren 736.4) | Caspi survey, quoted in templemount.org Table I | high | 737.1 (flat) |
| Haram surface at the northern gates | 737.0 (2418 ft) | Wilson, OS notes 1865 | high | 737.1 (flat) |
| Haram esplanade (mean of 15 of the 19 Haram spots) | 737.07 (2412–2423 ft) | OS 1865 | high (±1.5 m real variation) | flat 737.07 |
| Dome of the Rock upper court | 742.0 / 742.2 (2434–2439 ft) | Warren map XII; OS 1865 | high | not a flat (see below) |
| Sakhra summit | 743.7 (2440 ft) | Warren; Wilson 1865 | high | info |
| Damascus Gate, bench mark | 753.86 (2473.3 ft) | OS 1865 | high | 753.32 |
| Damascus Gate, inside / outside | 750.42 / 757.43 | OS 1865 (the gate sits in a dip) | high | 750.57 / 756.50 |
| Herod's Gate, bench mark / inside | 759.74 / 761.09 | OS 1865 | high | 759.59 / 760.98 |
| Lions' Gate, bench mark | 734.35 (2409.3 ft) | OS 1865 | high | 734.02 |
| Zion Gate inside / outside BM | 769.62 / 769.44 | OS 1865 | high | 769.61 / 768.87 |
| Inside the Dung Gate | 726.34 (2383 ft) | OS 1865 | medium (gate widened 1952) | 726.42 |
| Austrian Hospice front (Al-Wad x Via Dolorosa) | 737.01 (2418 ft) | OS 1865; Wilson's notes | high | 736.99 |
| 1865 Wailing Place alley | 728.8–729.4 (2391–2393 ft) | OS 1865 | high (for 1865) | superseded |
| **Western Wall prayer area** | **727.0** | 1865 level minus the ~2 m (two Herodian courses) lowering of 1967–68: bibleplaces.com "Then and Now: Western Wall Plaza", Lancaster 1998, Encyclopedia.com | medium (±0.8) | flat |
| **Western Wall plaza (main)** | **729.0** | 1865 Mughrabi Quarter 727.5–732.7 regraded; elevator cross-check | low (±1.5) | flat |
| Western Wall elevator: Misgav Ladach St to plaza | 22–26 m drop | Hebrew Wikipedia "מעלית הכותל"; AP / Times of Israel | medium | 27.1 m |
| New Gate | 790 (Wikipedia, uncited) | en.wikipedia | low | **784.4**; nearby OS spots 785.2 / 779.7 |
| Herod's Gate | 755 (Wikipedia, uncited) | en.wikipedia | low | **759.2**; the OS bench mark says 759.7 |

## Flats

| name | z (rel.) | z asl | area | basis |
|---|---|---|---|---|
| `haram_esplanade` | −33.51 | 737.07 | 141,900 m² | Haram polygon from `data/oldcity_polygon.json`; mean of the OS esplanade spots, agreeing with Warren/Caspi to ±0.6 m |
| `western_wall_prayer_area` | −43.58 | 727.0 | 1,570 m² | men's + women's sections, from the partition (OSM w45081552) to the Wall |
| `western_wall_plaza` | −41.58 | 729.0 | 3,580 m² | rest of OSM w26492734 north of y = −62 |

* **The Haram flat includes the area under the Dome of the Rock's upper platform** (OSM retaining
  wall w137725307), at esplanade level. This follows a coordination note:
  `blender/landmarks_haram.py` builds the platform as a solid. The measured top is **742.2 m, about
  5.1 m above the esplanade** (OS 2434–2439 ft; Warren 742.0), slightly more than the ~4 m that
  agent assumed. It is recorded in `platforms_info`.
* No other plazas qualify as flats. Omar Ibn el-Khattab Square slopes 770.5 → 769.4 → 776 (towards
  the Armenian Patriarchate). Hurva Square, Batei Mahase, the Muristan and the Damascus Gate
  forecourt all vary by 2–7 m in the survey. They stay in the sloped field.

## Validation (from the last run)

* **Anchor fit:** 336 OS anchors inside the walls are reproduced with RMS **0.21 m**, max 1.31 m.
  Every gate value is within 0.6 m.
* **Leave-one-out** (inside the walls): RMS **2.2 m**, median |error| **1.3 m**, 90th percentile
  3.7 m. Read this as the error expected 20–40 m from the nearest anchor. It is large where streets
  sit at different levels a few metres apart, such as causeways, terraces and the Jewish Quarter
  scarp above the plaza.
* **Steps:** the 86 OSM `highway=steps` ways inside the walls sit on a median terrain gradient of
  12.1%, against 9.1% for other streets. Their end-to-end grade is a median 8.8% (other streets
  3.8%), and 87% of them sit on gradients above 6%. The whole city is steep, so the separation is
  real but not dramatic.
* **Relative heights:** esplanade minus Western Wall prayer area = **10.1 m**. Dome platform minus
  prayer area = 15.2 m. Jewish Quarter (Misgav Ladach) minus plaza = 27.1 m.
  The brief expected the plaza to be **~25 m below the platform. The survey data do not support
  that.** The modern Mughrabi Gate sill (736.5) is only ~9.5 m above the prayer area. The ~19 m of
  exposed wall includes the courses rising above the platform. The ~25 m figure matches the drop from
  the Jewish Quarter to the plaza instead (the elevator project).
* **Overall fall:** inside the walls the street level runs from **788 m** (NW, between New Gate and
  Jaffa Gate) to **~724–726 m** at the Dung Gate, and ~711 m in the Ophel garden inside the SE wall.
  It is not the ~792 → 714 m of the brief: the brief's figures look DEM-like, and New Gate is 784 m
  on the survey.

### Transects (m asl, every 50 m along OSM centrelines; see `TRANSECTS`)

**A. Jaffa Gate → David St → Chain St → Gate of the Chain** (660 m). Net fall 33.2 m, total climb
only 1.9 m (across Omar Sq.), steepest 22% over 5 m on the David St steps.

| m | 0 | 50 | 100 | 150 | 200 | 250 | 300 | 350 | 400 | 450 | 500 | 550 | 600 | 650 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z | 770.6 | 770.8 | 769.9 | 767.0 | 760.3 | 757.6 | 755.5 | 754.4 | 752.1 | 747.9 | 744.4 | 739.2 | 737.4 | 737.3 |

The David St steps take it from 770 down to ~757 between 100 and 250 m. It meets the souqs at
~755 (320 m), descends Chain St to the causeway (~739), and reaches the Gate of the Chain at 737.3,
level with the esplanade.

**B. Damascus Gate → Al-Wad → Western Wall plaza** (701 m, using the lower Al-Wad level under
Chain St). Net fall 23.5 m, total climb 1.9 m.

| m | 0 | 50 | 100 | 150 | 200 | 250 | 300 | 350 | 400 | 450 | 500 | 550 | 600 | 650 | 700 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z | 752.5 | 747.6 | 743.2 | 742.4 | 739.1 | 737.4 | 735.5 | 735.6 | 733.8 | 732.8 | 732.2 | 730.9 | 730.6 | 729.9 | 729.0 |

**C. Lions' Gate → Via Dolorosa → Holy Sepulchre parvis** (957 m). It climbs over the Antonia /
Ecce Homo ridge to ~747, drops to Al-Wad at ~735 (Austrian Hospice), then climbs to Khan ez-Zeit
(~753) and the parvis (~758).

| m | 0 | 100 | 200 | 250 | 350 | 450 | 550 | 650 | 700 | 750 | 900 | 955 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z | 734.6 | 734.2 | 739.2 | 745.1 | 746.9 | 740.7 | 734.8 | 745.7 | 751.4 | 753.6 | 754.0 | 758.2 |

**D. New Gate → Jaffa Gate → Armenian Patriarchate Rd → Zion Gate** (1053 m). New Gate 784.4, high
point 787 just inside, Jaffa Gate 770.5 (500 m), Armenian Quarter ~776 (650–750 m), Zion Gate 767.7.

| m | 0 | 50 | 150 | 250 | 350 | 450 | 500 | 600 | 700 | 800 | 900 | 1000 | 1050 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z | 784.4 | 787.2 | 784.2 | 777.9 | 773.7 | 771.0 | 770.5 | 773.3 | 776.3 | 775.3 | 774.3 | 770.2 | 767.7 |

**E. Zion Gate → Jewish Quarter (Batei Mahase) → Dung Gate** (622 m). Net fall 48.2 m, total climb
2.6 m.

| m | 0 | 50 | 100 | 200 | 300 | 350 | 400 | 450 | 500 | 550 | 600 | 620 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z | 767.3 | 763.5 | 761.8 | 761.3 | 757.0 | 751.2 | 751.4 | 743.6 | 738.6 | 731.8 | 723.6 | 719.1 |

## Known limitations

* **The survey is from 1865.** Streets have changed little, but some areas have not:
  - the Western Wall plaza: created 1967, here two flats from indirect evidence;
  - the Jewish Quarter: rebuilt 1967–80s on the old street levels, with the sunken Cardo excavated;
  - the Jaffa Gate breach (1898, moat filled);
  - Damascus Gate forecourt (1980s);
  - New Gate (1889; the map predates it);
  - the Dung Gate (widened 1952) and the **Ophel / Davidson Centre**, excavated down to Herodian
    levels after 1968. The model there is probably several metres too high.
  - Typical repaving since 1865 adds a few tenths of a metre.
* **A single-valued field cannot hold two levels.** Where a street runs under another, `street_z`
  gives the upper one. `underpasses` lists the main case: Al-Wad beneath the Chain Street causeway.
  `street_z(..., under=True)` returns its lower level. Covered souqs (OSM `layer=-1`) are not
  two-level streets and need nothing. Steps are smoothed into ramps at 4 m resolution; the builder
  should take the step risers from the OSM step runs.
* **Uncertainty.**
  - Georeference: ±6 m RMS, worse near the linen seams of the scan.
  - Transcription: ~425 values read by eye. One misread was caught and one illegible value
    dropped; others may remain, and LOO outliers above 5 m are the place to look.
  - Leave-one-out: ~1.3 m median, 3.7 m at the 90th percentile.
  - Outside the walls the field is mostly the DEM envelope (55 'out' anchors at 1.5 m noise), so
    expect several metres of error there: Mamilla, the Kidron, north of Sultan Suleiman.
* **Flats are idealised.** The real esplanade varies about ±1.5 m: the NW rock is at ~741, and the
  Golden Gate hollow at ~731–734 (both lie inside the flat here). The real Western Wall plaza slopes
  2–3 m down towards the prayer area; here it is two terraces at 729.0 and 727.0.
* **Wikipedia's gate elevations disagree with the survey.** New Gate is given as 790 and Herod's Gate
  as 755, both uncited round numbers; the survey says ~784 and ~760. The survey is used.

## How to refine later

1. **A licensed DTM**, which would replace both the DEM envelope and most of the error budget:
   - Survey of Israel (MAPI) or Jerusalem Municipality 1 m DTM / LiDAR, or municipal GIS spot
     heights (GovMap).
   - Put it in `data/raw/terrain/` and use it as the trend in `build()`. Keep the GP with the OS
     anchors as a check, or drop the OS anchors where the DTM sees the ground.
2. **More of the 1865 map.**
   - The 1:2500 sheet also has 10 ft contours across the city (the dashed lines with 2xx9 labels),
     and the outskirts beyond the crop.
   - Vectorising the contours would densify the anchors several-fold.
   - A seam-aware or piecewise georeference, or automatic alignment of OSM centrelines to the
     scan's street corridors, would cut the ±6 m.
3. **Modern spot checks** at places that changed since 1865: the Western Wall plaza levels, the Dung
   Gate road, the Davidson Centre / Ophel, the Jaffa Gate breach, and the Damascus Gate forecourt.
   Add them to `MODERN` as anchors, and to `flats` / `PINNED` where they set a level.
4. **Two-level places:** extend `UNDERPASSES` and `PINNED` as the builder meets them, for example
   other `layer=-1` passages under houses, and arches.
