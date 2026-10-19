# Sector s10_herod_lions — Herod's Gate, Bab Hutta, Lions' Gate: visual reference

Local frame as in `hero_edges.md` (x east, y north, metres from the Jaffa Gate OSM node;
x = (lon-35.2275435)*94721.7, y = (lat-31.7766282)*110882.9). Sector polygon from `data/sectors.json`
(bounds x 560-899, y 400-781; its south edge is y = 430 west of x = 700 and y = 400 east of it, so the
Via Dolorosa itself is the boundary with the next sector). Edge numbers are **raw OSM ring indices** from
`data/osm_local.json` (`buildings[].outer`, edge i = vertex i to i+1), given as
`id / eN (start->end, length, compass direction it faces)` so they can be re-matched after a spec rebuild.

Photo keys: `R:NN` = `data/photos_ref/s10_herod_lions/NN_*.jpg` (45 Commons photos downloaded for this note,
1280 px; `index.json` there has title, page, author, licence, date, lat/lon and local x/y where geotagged).
Camera positions quoted as "cam (x,y)" are the Commons geotags converted to the local frame (phone GPS,
treat as ±10 m). Confidence: **H** = seen clearly in 2+ photos or measured on OSM geometry; **M** = one good
photo or a consistent estimate; **L** = inferred. Scale from people (1.7 m), doors (2.1-2.2 m), stone courses
and OSM edge lengths.

Terrain numbers are from the 1865 Ordnance Survey spot heights (`data/raw/terrain/os1865_spot_heights.csv`,
projected with the control points in `os1865_control_points.csv`; position rms ~6 m) unless marked DEM.

> Status: complete (written incrementally). Independently reviewed 2026-10-20. Corrections are marked **[Rev. n]** in
> the text and listed under "## Review" at the end.

---------------------------------------------------------------------------------------------------------------

## 0. Sector at a glance, and the biggest things to get right

**What the sector is.** The north-east quarter of the Old City: a shallow **valley (the Bethesda / St Anne
valley) running north-south at x ≈ 740-800**, with the floor at ~733-737 m, rising west to Herod's Gate
(~761 m) and north-east to the Burj Laqlaq corner (~752-755 m). It is much **quieter and greener** than the
souq sectors: institutional compounds with gardens (St Anne / Bethesda, the seminary, the Greek Orthodox
monastery), residential lanes of the Bab Hutta and Sa'diyya quarters, schools, a few shops near the two gates
and at the Bab Hutta junction. **There is no covered souq here.** (H, OSM + all photos)

1. **Lions' Gate is a flush gate in the east wall, not a projecting tower**, with a straight E-W vehicle
   passage ~10 m long (OSM w288395731, passage way 288395746 from (894,468) outside to (882,466) inside).
   Outer face: crenellated, machicolation box over the arch, **two pairs of carved felines** flanking the
   pointed arch at ~7 m. (H: R:04, R:07, R:02, R:05, R:06)
2. **Lions' Gate Street is a narrow vehicular street (4.6-6.4 m), not a souq**, nearly flat for the first
   ~110 m west of the gate, then climbing ~5 % to x ≈ 722 and **~10-13 % through the Muazzamiyya passage**
   (**[Rev. 6]**); it **opens into a 12-14 m wide plaza** in front of the St Anne seminary at x ≈ 795-831 (the
   north edge is a front-garden wall, the south edge a raised terrace with a broad stair, **[Rev. 3]**) and
   **passes under buildings twice**: an arch at x ≈ 784-789 and the 27 m vaulted
   passage of the Madrasa al-Muazzamiyya at x 688-715. (H for widths/passage from OSM; M for the arch)
3. **Herod's Gate is a square tower ~11 x 12 m projecting ~5 m north of the wall at x 575-587, y 700-709**
   (wall way 137726904 vertices 50-53); the modern entrance is a pointed arch in its **north face**, the passage
   runs through a groin-vaulted chamber and leaves by a low arch in the **south (inner) face** onto a small plaza
   (x ≈ 576-602, y ≈ 689-700) from which **Herod's Gate Ascent** (625317891) runs east then SSE and
   **Zawiyat al-Hunud** (246593338) runs SW. The original Ottoman entrance in the tower's east face is
   blocked and holds a small shop. (H for tower, faces and plaza; M for the east-face arch)
4. **Herod's Gate Ascent / Aqabat Darwish is the sector's stepped spine**: 3-4.5 m wide, ~21 m of climb from
   the Lions' Gate Street junction (~740 m) up to the gate (~761 m), with a 20 m **stair under a building** at
   the bottom (way 744670522) and long shallow steps with **twin cart ramps** above. (H)
5. **Green elements are a defining feature**: the St Anne gardens (fan palms, cypresses, pepper tree, flower
   beds), the Bethesda excavation (grass, poppies, olive), El-Ghazali Square's trees, the gardens at the NE
   corner, and caper bushes on every gate and wall. (H)
6. The **Bab al-Asbat minaret** on the Haram's north wall (outside the sector, at ≈ (835±10, 395)) and the
   **gold Dome of the Rock** are the skyline landmarks seen south from Lions' Gate Street and El-Ghazali Square;
   the **white dome of St Anne** is the landmark inside. (M)

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and street profiles

### 1.0 Measured widths along the main streets (OSM footprints, wall-to-wall, every 6 m)
(`open` = a footprint missing on one side in OSM; `cov` = covered passage)

| street (OSM name:en, way ids) | section | wall-to-wall |
|---|---|---|
| Lions' Gate Street (290986904, 744664057) | inside the gate x 855-878 | **4.6-5.6 m** |
|  | St Anne gate x 843 | 5.5 m |
|  | plaza in front of the seminary x 795-831 | **11.5-14.2 m** from the front-garden wall 288395751/752 (north) to w290986927 (south); this includes the raised south terrace and its stair, the open carriageway is ~6-8 m (**[Rev. 3]**; to the seminary façade itself it is 19.5-21.9 m) |
|  | x 766-790 (arch zone, Bab Hutta junction at 763) | **5.3-6.4 m** |
|  | x 748-760 | ~6 m |
|  | ~~x 713-740 (garden / "Group Meeting Point" on the north) / open, 24-28 m to the garden wall~~ **corrected [Rev. 1]:** x 714-730 | **~5 m**: north = shops of w1393164309 at 2.1-2.2 m from the centreline (R:14 right); south not mapped in OSM (next mapped building r3865791 is 22-25 m away) but built: R:14 left shows a continuous tall ashlar wall |
|  | x 731-745 | north side open to the "Group Meeting Point" stage and garden 1393176148; south w1394480978 / w1393176149 at 2.6-2.8 m from the centreline |
|  | x 688-715 (744664059) | **covered passage, ~4.5-5 m** |
| Bab Hutta Street (291836762) + Bab Hutta (744665958/9) | built both sides | **4.1-5.3 m** (6.5-8 m where a lot is open; **[Rev. 9]** OSM gives 9.5-11.4 m at y ≈ 476-511, where the west-side buildings stand 7.5-9.5 m back; not photographed, unverified) |
| Herod's Gate Ascent (625317891) + Aqabat Darwish (26496670) | south 180 m | **2.7-4.3 m**, a few 8-9 m bays (**[Rev. 10]**: 2.7-4.3 m only where both sides are mapped; at about a third of the 6 m samples one side is open in OSM, giving 8-15 m, and a few give 16-32 m. The photos show a continuous 3-4 m lane, so treat these as unmapped frontage); north 95 m has no OSM footprints |
| Via Dolorosa (44830379, boundary) | Flagellation to Ecce Homo | 4.3-6.3 m, typically **5.0 m** |
| Al Umari (36948406) | x 785-830 | 3.5-5.8 m |
| Salahiya (123254017) | x 740-840 | 2.4-5.7 m between gardens |
| Burj Laqlaq (36948405 steps + 625346030) | y 470-520 | 4-11 m, then 16-23 m along the parks |
| El-Ghazali Square (291836760) | y 406-461 | ~~11.6-24.3 m (median 21 m)~~ **[Rev. 2]** y 406-445: **~13.5-14 m** from the park edge 290986911 (x 883-887) to the OSM wall line (x 896.5-901), ≈ 12 m to the wall's inner face; y 446-461: **16-18 m** between w290986909 e9 (x ≈ 877) and the wall |

### 1.1 Profile A — "gate street" (vehicular, institutional): **Lions' Gate Street**
Applies to: Lions' Gate Street (OSM 290986904, 744664057; outside part 288395745 is the road down to the Kidron),
"Lions' Gate" (26492728, the 10 m stub at the Via Dolorosa junction).
- **Width** 4.6-6.4 m wall-to-wall, with the 12-14 m plaza at x 795-831 (table 1.0). Cars, police jeeps,
  garbage tractors and taxis use it (OSM `living_street`/`residential`, `surface=sett`). (H: OSM, R:09, R:12)
- **Paving**: **rough-faced grey-cream limestone setts ~0.2-0.3 x 0.3-0.45 m in rows across the street**, darker
  and rougher than the souq slabs, with **smooth large slabs forming kerb strips and a drainage line**, round
  cast-iron manhole covers ~0.7 m with concentric rings every ~8-12 m, square steel grates at the gate. (H: R:12,
  R:09, R:06, R:13)
- **Kerbs / steps at the edges**: along the south side at x ≈ 795-810 a **raised pavement of 2 shallow steps
  (~0.15 m each, ~0.4 m treads) of long smooth slabs** (R:12); elsewhere the setts run wall to wall. (M)
  **[Rev. 3] Correction:** these 2 steps are only the west end of a longer feature. The south side of the seminary plaza
  (x ≈ 795-835) is a **raised paved terrace**, the OSM pedestrian area 1544948036 in front of w290986927 with the
  Stations-of-the-Cross plaques. It is reached by a **broad flight of long steps running along the street**: 2 steps at the
  west end beside the stone gate pillars (R:12, looking west), rising to **~10 risers (≈1.5 m) in two runs** further east
  (R:18, left side, between the w290986909 terrace and the same gate pillars). The street itself is ~0.5-1 m lower at the
  east end. (M for the stair, L-M for its exact x)
- **Gradient**: nearly flat from the gate (~733.5-734 m) to x ≈ 800 (~734 m), then ~5 % up to the Via
  Dolorosa junction (~740 m at (697,427)). No steps on the street itself east of the Muazzamiyya passage. (M-H, OS 1865
  spots at (850,458) 733.0, (768,445) 734.9, (722,434) 737.3, BM (697,427) 740.7)
  **[Rev. 6] Correction:** the same spots give **+2.4 m over 47 m (5 %) from x 768 to x 722**, then **+3.4 m over 26 m
  from x 722 to the BM at x 697 (13 %; ~10 % if the wall BM is ~0.5 m above the ground)**. The steep part therefore lies
  inside the Muazzamiyya passage. This fits the visibly ramped floor and the handrail in R:13. Model: flat to x ≈ 765, 5 % to
  x ≈ 718, ~10-12 % ramp through the passage.
- **Frontages**: long **institutional facades of smooth pale ashlar** (St Anne gatehouse and seminary,
  Greek Orthodox monastery), high **garden and compound walls with iron railings**, a few **3-4-storey houses with
  arched windows** and a handful of **shops at the Bab Hutta junction** (x 715-790): souvenir/juice stalls,
  cafés ("The Message Café" #14 at (748.8,437.1), "Abo Al-Halaweh coffee shop" (770.7,437.1), pomegranate juice
  (722.2,441.2) — OSM nodes). (H)
- **Closed shop fronts** (junction zone, R:15, R:32): **pale teal multi-leaf steel doors** (4-6 tall panelled
  leaves, ~2.8-3.2 m high, padlock hasps), some with a **semicircular fanlight grille** in a round-arched opening;
  **black wrought-iron scroll brackets** carrying a shallow green/grey sheet canopy ~1 m deep at ~3 m. (H)
- **Overhead**: few canopies; **sagging black cables** between facades, **CCTV clusters and loudspeaker horns** on
  corners (R:32, R:14), occasional shade sails at the gate (R:04). Sky open except at the two crossings. (H)
- **Lighting**: wall-mounted lamps on the facades (black box lanterns on short arms, R:09), floodlights on the
  gate; no free-standing lamp posts inside the gate. (M)
- **Typical clutter**: grey galvanised crowd barriers (stacked or in lines) near the gate, short black steel
  bollards (~0.6 m, R:15), square stone block bollards (~0.45 m cube, R:06), the red **Goldoni** mini tractor
  with a **yellow caged trailer** (municipal waste, R:12), postcard stands, a toy/bread cart, mopeds. (H)

### 1.2 Profile B — "vaulted passage" (street under buildings)
Applies to: **Lions' Gate Street x 688-715** (744664059, under w1393740933 + the Madrasa al-Muazzamiyya),
**Bab Hutta tunnel** (744665958, (737,560)->(732,577), 18 m), **Aqabat Darwish stair tunnel** (744670522,
(674,448)->(679,429), 20 m), **King Faisal** (123254013 / 744664359, tunnel south to the Haram's Bab al-Atm),
and the short vaults on Herod's Gate Ascent near Al-Bustami (R:39, R:40).
- **Entry arch**: **pointed (two-centred) arch ~4-4.5 m wide, apex ~5-5.5 m**, voussoirs of pale ashlar, the
  building rising another 6-8 m above it with **small rectangular grilled windows** and **caper/fig bushes on the
  parapet** (R:14). (H: R:14, R:15, R:13)
- **Inside**: **pointed barrel vault**, partly **whitewashed/plastered (cream, stained grey)**, with transverse
  arches every ~5-8 m; floor of setts with a smooth central strip; a **steel handrail** along one wall where the
  floor ramps (R:13); shop doors and house doors in the side walls, electricity meter boxes, a **wall drinking
  fountain** with a framed Arabic inscription at the east pier of the Muazzamiyya arch (R:14). (H)
- **Lighting**: bare bulbs / small lamps on cables under the vault, a ceiling fixture every bay, **festoons of
  coloured bulbs** in the Herod's Gate Ascent vaults (R:42). (H)
- **Signs**: ceramic street plaques at the mouths ("KING FAISAL ST." in R:13/R:14), **blue or white boards with
  Arabic religious texts fixed above the arches** (R:40, R:42), graffiti in green/red Arabic script on the
  whitewash (R:39, R:40). (H)

### 1.3 Profile C — "stepped market-residential lane": **Herod's Gate Ascent / Aqabat Darwish**
Applies to: Herod's Gate Ascent (625317891), Aqabat Darwish (26496670), Aqabat Darwish / Herod's Gate Ascent
(744670522, the stair tunnel), and in part Al Bustamy (26492738) and Hab Ra'aman (291743318).
- **Width** 2.7-4.3 m wall-to-wall over most of the south 180 m (table 1.0). (H, OSM; R:39, R:42)
- **Lower stair** (744670522, under a building, ~20 m): **straight flights of ~16 steps, riser ~0.15-0.17 m,
  tread ~0.35-0.45 m**, worn smooth, with **two smooth ramp strips ~0.5-0.6 m wide** set into the steps for carts
  (the strips read as darker polished stripes); a landing, then flights with longer treads. (H: R:41, caption
  "the ramps in the middle of the streets are to accommodate carts") (**[Rev. 15]**: R:41's geotag (680.8,453.4) lies
  6-8 m off the lane near the tunnel's *north* end, and the photo looks up-slope (north) through a vault. It may show the
  vaulted stretch just north of 744670522 rather than the tunnel stair itself. The stair form is H; placing it in the
  tunnel is M.)
- **Upper lane**: **long shallow steps, riser 0.10-0.15 m, treads 1.2-3 m**, of large pitted limestone slabs,
  alternating with gently ramped stretches; the same twin cart ramps. (M: R:41 background, R:42, R:39)
- **Covered stretches**: pointed vaults at the Al-Bustami junction ((649,590)) and further south (R:39, R:40, R:42). (H)
- **Shop fronts**: green, teal or grey **steel doors**, a few wooden doors; a butcher, a pita bakery and
  greengrocers near Herod's Gate and at Al-Bustami (Commons captions 2007-2009); house doors **raised 2-4 steps**
  above the lane with stone stoops. (M)
- **Overhead**: **blue tarpaulins and small sheet canopies** (R:42), cables, bulbs; sabats/arches every 20-40 m. (H)
- **Clutter**: trash bags at door sills, a small folding table, plastic crates, carts. (H: R:39, R:42)

### 1.4 Profile D — "residential alley"
Applies to: **Bab Hutta Street** (291836762), **Bab Hutta** (744665959), **Al Umari** (36948406), **Salahiya**
(123254017), **Riman** (257604186), **Hab Ra'aman** (291743318), **Ha'Chasidut** (288396517), **Shaddad** (26496667),
**Ash Sheikh Hasan** (26496669), **Ash Sheikh Rihan** (26492740), **Al Bustamy** (26492738), **Zawiyat al-Hunud**
(246593338), **Aqabat Al-Quds** (257604168), **Aqabat Er-Rahbat** (582488418/1393163029), **Al-Hilal** (582488419).
- **Width 3-5 m wall-to-wall**, often ~3.5 m clear (R:30); walls **3-4 storeys, ~10-15 m**, so the lanes are
  canyon-like. (H: R:30, R:32, OSM)
- **Masonry**: a mix of **very coarse rock-faced bossed blocks (0.5-1.0 m, deeply weathered and pitted)** in the
  lower storeys and **smoother coursed ashlar** above; patches of render. (H: R:30, R:31, R:32)
- **Paving**: limestone slabs ~0.3-0.5 x 0.5-0.9 m, a smoother central band, round manholes; no steps in Bab
  Hutta Street over most of its length (gentle slope, ~3-4 %), steps where lanes cut across contours. (H: R:30)
- **Ground floors**: house doors (wood or steel, often with an **Armenian-style ceramic name plaque** in a blue
  floral tile frame over the lintel and a **pointed relieving arch** above, R:31), a few kiosks and shops (red or
  teal steel doors), barred windows. Doors frequently **up 2-3 big worn steps** (R:31). (H)
- **Canopies**: **timber-rafter lean-to canopies on curved iron brackets** and small sheet-metal hoods (R:30). (H)
- **Overhead**: very dense **cable bundles** (black, grey, green), meter boxes, satellite cables, CCTV, house
  numbers on small blue/white plates, AC units, potted plants on window grilles. (H: R:30, R:31, R:40)
- **Clutter**: **mopeds and scooters** parked along the wall, food carts under plastic covers ("FRESH CORN" cart,
  a knafeh display case, R:31), crates, yellow fire hydrants at corners (R:32, R:40). (H)

### 1.5 Profile E — plazas
- **El-Ghazali Square** (291836760): a long **paved esplanade ~56 m N-S x 12-24 m** (**[Rev. 2]**: ~12-14 m from the wall's
  inner face to the garden edge for most of its length, 16-18 m at the north end) along the inner face of the east
  wall, from just inside Lions' Gate (890,461) south to the Haram's **Bab al-Asbat** at (890,406). Paving: **large
  pinkish-cream limestone slabs** in long rows; along the wall a ~1.5 m **grass strip with young trees in square stone
  planters**; the wall's inner face has a **ground-level arcade of blind pointed recesses (~2.5-3 m wide, ~3 m high)**
  and a stone stair up to the rampart at the south end; on the west a **terraced garden** (olive trees, palms, low
  stone retaining walls; OSM leisure=park 290986911 at (843,442)). The surface falls gently south (~734 m DEM at the
  south end). (H: R:20, OSM) (**[Rev. 14]** the slope is unverified: no OS spot lies on the square, and the DEM reads
  3-6 m high here, see section 5.)
- **Lions' Gate inner mouth** (~(870-882, 460-470)): a small widening where the street, the Burj Laqlaq stair and
  El-Ghazali Square meet; pale slabs, square stone bollards, the Sabil (section 2.3). (H: R:06, R:10)
- **Plaza in front of the St Anne seminary** (x 795-831, y ≈ 445-462): the street widens to 12-14 m; south side
  the low compound w290986927 with a **row of 14 metal Stations-of-the-Cross plaques** (OSM memorial node
  14052572780 at (816.8,445.1), facing north) (L-M, OSM only), north side the seminary front. (M)
  **[Rev. 3] Correction:** the north edge of the plaza is the **front-garden wall** 288395751 / 288395752 (y 452.5-460). It
  continues the line of w288395736's street face from the same vertex (788.6,452.5). The seminary façade (e3, y 460.7-466.8)
  stands 5-8 m behind the landscaped garden 288395717, which has a palm 2919578844 at (821.6,461.5) and a tree at
  (802.0,458.9). The south edge is the raised terrace (pedestrian area 1544948036) with its long stair along the street (see 1.1).
- **Herod's Gate inner plaza** (~(576-602, 689-700)): irregular, ~25 x 10 m, paved with slabs, lanes leaving east and
  SW; vegetable/fruit sellers and kiosks; a tree overhangs the tower. (H: R:35, R:36)
- **"Group Meeting Point"** (OSM 744670112 at (732,441)): an **elevated paved stage** on the north side of Lions'
  Gate Street with a semicircle of steps, a 15-step stair (1395044677) and a wheelchair ramp (1395044676), two stone
  benches with backrests (1395046838/9); public toilets at (747.3,445.0) and (755.2,455.9), trees at
  (741-748, 456-467), a small garden/playground behind (1393176148). (M, OSM description only; no photo)
  **[Rev. 20]** OSM also has a node "Paved street from Second Temple period" (9351417415) at (738.0,439.7), at the foot
  of the stage. It is probably exposed ancient paving, but this is unverified (OSM only).

### 1.6 Profile F — gardens and compounds
- **St Anne / Bethesda** (French national domain, entered from Lions' Gate Street at (844,462)): paved forecourt of
  pale setts with a **painted yellow guide line** in front of the church (R:24), gravel paths with stone kerbs,
  flower beds (roses, geraniums, white flowers), fan palms, cypresses, a weeping pepper tree, the Lavigerie bust; the
  Bethesda excavation 5-8 m deep to the west of the church with galvanised railings and steel stairs. (H: R:22-R:25,
  R:28, R:29)
- **NE corner (Burj Laqlaq)**: OSM parks 291742570 (875,581), 291749462 (843,570), 291749459 (761,600), fenced
  plots and schools; seen from the wall as **gardens with cypress and pine groves between low flat-roofed houses**
  (R:46). OSM maps no buildings north of y ≈ 670, but the 1865 survey has street spot heights there and photos from
  the wall show houses: model as **low 1-3-storey houses with gardens and many trees**, not as an empty strip. (L-M)
  **[Rev. 8] Correction:** R:46 was taken at (886.5,631.3) on the east wall looking SSW towards the Dome of the Rock
  (bearing ~198°). It shows the houses and gardens around the Burj Laqlaq lane, Salahiya and St Anne (y ≈ 450-630),
  **not** the strip north of y ≈ 670. No photo in the set shows the NE corner, and the 1865 spot heights only show that
  streets existed then. What stands north of y ≈ 670 today is **unverified (L)**.

---------------------------------------------------------------------------------------------------------------

## 2. Landmarks (massing, street facades, materials)

### 2.1 Lions' Gate — w288395731 (see section 3 for the gate itself)
| edge | segment | faces | onto |
|---|---|---|---|
| e1 | (882.4,472.4)->(884.6,460.6), 12.0 m | 259 | inner face, Lions' Gate Street mouth |
| e4+e5 | (894.6,462.0)->(892.5,474.4), 12.6 m | 80 | outer face, road to the Kidron |
| e2+e3 | (884.6,460.6)->(894.6,462.0), 10.2 m | 170-173 | El-Ghazali Square |
| e0 | (892.5,474.4)->(882.4,472.4), 10.3 m | 348 | Burj Laqlaq steps |

### 2.2 Greek Orthodox Monastery of St Anne ("Birthplace of the Virgin Mary"), no. 21 — w288395734
- Position: the portal is at **(866.7,467.6)** on **w288395734 e4 (880.6,467.4)->(855.3,463.7), 25.6 m, faces 172**,
  north side of Lions' Gate Street, 15-25 m inside the gate. Confirmed by OSM place_of_worship node 4410141990 at
  that point and by two geotagged photos taken right in front of it (R:08 cam (866.8,466.3), Commons "Palm procession
  (34)" cam (867,466), both showing the portal). (H)
- Facade (R:08, 2019): **west part smooth large ashlar**, then the **portal: round-arched doorway ~1.8 x 3.2 m in a
  deep frame flanked by pairs of engaged columns with Corinthian capitals** carrying an entablature; above the door
  **bronze/dark capitals "BIRTH PLACE OF VIRGIN MARY"** on the frieze and a Greek inscription above (Commons caption);
  house number **21** on a small plate right of the portal; a **white marble plaque with a Greek inscription** right of
  the columns at ~1.5 m. **East part rusticated rock-faced ashlar with tall round-arched windows with dark louvred
  shutters and grilles**. Two storeys visible from the street, ~9-10 m. (H for elements, M for sizes)
  **[Rev. 16]** R:08 shows only the ground floor. The storey count comes from R:18 (from the gate top, right side), which
  shows a rusticated ground floor and a tall smooth-ashlar **upper floor** with tall dark-shuttered windows under a frieze of
  small blind round arches. It also has **cantilevered balconies with grey iron railings with cross motifs** and a cornice
  on consoles. The crosses support the identification as the Greek Orthodox house. (M, one photo for the upper floor)
- e0-e3 (x ≈ 879-881) face east onto the **Burj Laqlaq steps**; the **Sabil Bab al-Asbat** is at the east end of e4
  (section 2.3).

### 2.3 Sabil Bab al-Asbat (Ottoman public fountain, 1536)
- Position: **south face of w288395734 at its east end, x ≈ 873-880, facing 172**, immediately west of the mouth of the
  Burj Laqlaq stair. Confirmed by R:10 (cam (880.2,467.5), the stair passage with steps going up is visible right of
  the fountain) and the Commons geotag of "Sabil IMG 1537" (cam (881,471), caption "on Lions Gate Street, near the
  Lions Gate"), plus the OSM steps way 36948405 starting at (882,466). (M-H)
- Form (R:10, 2026): a **pointed-arch niche ~2.0 m wide inside a moulded pointed frame ~3.2 m wide, apex ~4.7 m**;
  in the tympanum a **2-line carved Arabic panel ~0.75 x 0.45 m**, below it a **3-line white marble inscription panel
  ~1.2 x 0.55 m** in a moulded frame; a **small arched recess with a spout** at ~1.2 m and a **long stone trough ~0.4 m
  high** at the foot; a carved roundel at the right foot; a **black heritage sign with a teal top band** ("רהט (סביל) /
  سبيل / Sabil") on the right pier. Stone: honey limestone, heavily pitted. Cables run across the top. (H for form, M for sizes)
  **[Rev. 12]** The sign has teal bands at **top and bottom**. Its English text calls the fountain "Sabil Sitt Mariam",
  named for its nearness to the Virgin's birthplace. This independently supports its place on the Orthodox
  "Birthplace of Mary" building w288395734. The other two photos cited for this note ("Sabil IMG 1537", "Palm procession
  (34)") are not in the local set and were not re-checked.

### 2.4 St Anne compound gatehouse, no. 19 — w288395720 (entrance to the Church of St Anne and Bethesda)
- Position: the **pedestrian entrance is at (844,462)** (OSM entrance node 2919578846 "House and Birthplace of Virgin
  Mary (Entrance)" and the passage way 288395740 (843,471)->(844,462) through this building), on
  **e8 (844.0,462.0)->(830.3,459.9) 13.8 m and e7 (855.3,463.7)->(844.0,462.0) 11.4 m, both facing 171**. R:09
  (cam (830,463), looking east) shows the arched gate frontage on the left (north) side at this point. (H for position)
- Facade (R:26, 2021; R:16): **two storeys of smooth pale ashlar, ~10-11 m**:
  - ground floor: a **pointed-arch pedestrian passage ~1.4 x 2.8 m** (open, garden visible through it) under a
    **round-arched tympanum with carved capitals "SAINTE ANNE / PÈRES BLANCS / SÉMINAIRE GREC-CATHOLIQUE"**; house
    number **19** on a small plate; right of it a **big pointed arch ~3.5 m wide** framing **double wooden doors ~2.4 x
    4.2 m, dark brown, with black iron straps and studs**; white marble plaques ("Basilique Sainte Anne / Piscine de
    Bethesda"); right again a **small pointed window with a grille** in which a mosaic of the Nativity of Mary is set,
    and under it a **ceramic tile sign "Bethesda"** (black script on cream tiles, green border) (H: R:26 + R:16 show
    the same window and sign)
  - a **string course with large square dentil blocks** at ~5 m
  - upper floor: **tall rectangular windows with moulded architraves and pale mint/blue louvred shutters**; over the
    big gate a **balcony on three carved stone consoles with a mint-green iron railing of pointed-arch pattern** (H)
  - top: a plain parapet band with **small oval medallions** below the cornice (M) (**[Rev. 17]** unverified. R:22 shows
    the courtyard side of this frontage with a parapet **pierced by a row of small round-headed openings**. The "medallions"
    seen steeply from below in R:26 are probably the same openings. L-M)
- Order of openings W→E: pedestrian passage at x ≈ 843-845, big gate at ≈ 846-851, Bethesda window ≈ 852-854 (M; R:26
  looks along the facade towards the east).

### 2.5 St Anne Seminary — w288395732
- **e3 (829.6,466.8)->(788.5,460.7), 41.5 m, faces 172** = the long front on the street plaza; **e0 (781.7,476.8)->
  (828.1,483.9), 46.9 m, faces 351** onto the garden; e5 (16.8 m, faces 263) west end.
- Seen from the garden (R:25): **2 storeys + attic band, ~11-12 m**, pale ashlar, **round-arched windows with pale
  blue louvred shutters** (tall ground-floor arched French windows, smaller upper ones), a **cornice on small consoles**,
  solar panels and a railed roof terrace. The street front is in the same 19th-century French style (smooth ashlar,
  shutters, consoles) as 2.4. (M; no frontal photo of e3)
- **[Rev. 7] Mis-identification:** the façade in R:25 (and behind the bust in R:23) is most likely **not this building**.
  The seminary's garden front e0 runs x 782-828, i.e. 17-60 m *west* of the Lavigerie bust (844.6,502.6). In R:25 the
  façade's left end meets a pale domed building: the Church of St Anne, whose south face (158°) is sunlit in this
  October-noon shot. The bust stands right in front of that junction. This matches **w288395735's west front e8
  (864.3,487.2)->(852.2,516.4), 31.6 m, faces 248**, whose NW corner (852.2,516.4) is 4 m from the church's SE corner
  (848.1,517.8). It also matches a camera SW of the bust looking NE: the façade recedes to the left, with the cornice
  rising to the right. So the R:25 description above belongs to **w288395735 (east side of the St Anne garden)**. The
  seminary w288395732's own façades (garden e0 and street e3) appear in no photo of the set. Their height and style are
  **unverified** (assume the same style as a guess). (M-H)

### 2.6 Church of St Anne — w126864879 (Crusader basilica, 12th c.)
- Footprint ~37 x 14-20 m, axis **WSW-ENE (~70°)**. **West facade = e16 (827.8,513.3)->(822.5,525.6), 13.4 m, faces 247**,
  onto the paved forecourt (OSM pedestrian area 1545241932 at (810,529)); north side **e0 (822.5,525.6)->(842.8,533.0)
  21.6 m, faces 340** (towards the Bethesda path 755420518); south side **e14 (846.5,520.7)->(830.9,514.5) 16.8 m, faces
  158** (garden); **three apses at the east end** (e3-e11, x 850-861). (H, OSM; R:24 frontal on the west front, R:27
  from the rampart behind the apses, cam (888.3,531.3))
- Massing (R:24, R:27): a **tall nave with a low-pitched gable**, lower aisles, **a small dome on a cylindrical drum**
  over the crossing (drum with small pointed lattice windows), and **stepped stone roofs** — the aisle and apse roofs are
  covered in **stepped/terraced stone slabs** (horizontal courses like shallow stairs) rather than tiles; the dome is
  faced in stone (grey-white, a coursed grid). Heights: nave gable apex ~17-19 m, aisle walls ~11-13 m, dome apex
  ~22-24 m above the forecourt. (H for form; L-M for heights)
- West front (R:24): **pointed portal with stepped roll mouldings on slender colonnettes, door ~2.0 x 3.5 m** (dark,
  set back); above it a **string course with a band of carved dentils/zigzag**; a small pointed window, and high in the
  gable a **larger pointed window within a roll-moulded arch, filled with a stone lattice/grille** (**[Rev. 16]**: the
  heights given in the massing bullet above are unverified; no photo gives a usable scale for the church); the north-aisle front
  to the left has one pointed lattice window; a **square tower/porch at the SW corner** with an open pointed arch at the
  base (~2.5 x 4.5 m) and two small lattice windows near the top. Stone: **pale grey-white limestone with strong
  grey-black weathering patches, coursed ashlar 0.4-0.6 m**. A **stone well-head with a wrought-iron cross arch** stands on
  the forecourt at the SW (R:24). (H)
- **French tricolour on a tall pole at the south-west** of the church (R:24 shows it behind the south part of the west
  front; R:27, looking west from behind the apses, shows it on the left = south). (H)

### 2.7 Pool of Bethesda — OSM area way 126864878 (765-815, 515-560)
- An **open excavation west of the church**, ~50 x 45 m, 5-8 m deep: tumbled pale limestone ruins, cistern mouths,
  vault springers, a **re-erected column on a cross-carved pedestal**, a **Crusader/Byzantine apse wall**, rock-cut
  basins; **galvanised steel railings** around the rim and **steel stairs** down; a **small steel-and-glass shelter**
  (info / display box) at the NW; vegetation: **grass, red poppies, ivy, an olive tree**, ruins overgrown in spring,
  bare dusty in summer. The rim walls are **rubble masonry with gardens and railings on top** (the compound lies higher
  on the north and west). (H: R:28 cam (803.6,524.8), R:29)
- OSM steps 288395744 (810,530)->(800,540) (17 m, incline down) and 743659267 / 755420520 / 288395739 / 288395742
  are the stairs down into the site from the forecourt and the paths. (H, OSM)

### 2.8 Lavigerie memorial — OSM node 6885910385 (844.6,502.6)
- In the garden between the seminary and the church (**[Rev. 7]**: more exactly, in the garden enclosed by the gatehouse
  w288395720 to the S, w288395735 to the E and the church to the N; the seminary lies to the SW; the bust stands in front of
  the church / w288395735 junction in R:25): **white marble bust on a tall tapering pedestal (~3.5-4 m in all)**,
  inscription "AU CARDINAL LAVIGERIE / L'ÉPISCOPAT ET LE CLERGÉ GRECS-CATHOLIQUES", a carved cross medallion on the
  capital; framed by **fan palms, a cypress and clipped shrubs**, round flower beds edged with stone. (H: R:23, R:25, OSM)

### 2.9 The arch over Lions' Gate Street at x ≈ 784-789 (attached to w288395736)
- A **pointed arch spanning the street** where it narrows from the seminary plaza (north frontage steps from y ≈ 461 to
  y ≈ 453 at **w288395736 e1 (788.5,459.4)->(788.6,453.4), faces 89**); above it a room with a **large round-arched
  window filled with a white/grey iron grille**, and **two low domes** on the roof behind; a free-standing **ancient
  column (~2.5 m, on a square stone base ~0.9 m)** stands in the re-entrant corner at its north-east pier.
  Position confirmed by R:12 (cam (803,456), looking west: the arch with people coming through, the tile-roofed
  w290986908 seen beyond to the left over the car park) and R:18 (cam (882,484), from the rampart: arch, column, and the
  seminary's mint balcony on the right); R:17 shows the column beside the arch. **OSM does not map a passage here.** (M)
- **[Rev. 4] Corrections to the geometry above:**
  - w288395736 e1 (faces 89) faces the seminary's *front garden*, not the street. The street's north edge does not step
    here. w288395736's street face e3 and the garden wall 288395751 leave the same vertex (788.6,452.5) on one line. The
    narrowing at the arch comes from the **south** side: east of x ≈ 792 the plaza runs south to the raised terrace in front
    of w290986927 (y ≈ 442-445).
  - The **arch's south pier is not in OSM**. The nearest mapped building on the south, w1545560831, is at y ≤ 441.7, which
    is 10.8 m from the north pier. Model the south pier at y ≈ 446-448, giving a ~4.5-5 m opening (L-M).
  - The column stands in the corner between the arch's east face (x ≈ 788.5) and the garden wall running east. R:17 shows
    it against the pier face, with a perpendicular rough-stone wall on its right. This confirms the NE-pier position from a
    second photo (R:17 + R:18).
  - In R:18 the near balconies on the right, with cross-pattern railings, are on w288395734 (Greek Orthodox). The mint
    balcony further on is the gatehouse w288395720's balcony on consoles (R:26), not the seminary's.
- Width ~4-5 m, apex ~5 m; the arch pier is coursed ashlar; the room above ~4 m; total ~10 m. (L-M)

### 2.10 w288395736 (north side at the Bab Hutta junction) and w290986908 (south-east corner)
- **w288395736**: e3 (788.6,452.5)->(762.1,446.6), 27.2 m, faces 167 on Lions' Gate Street; e4 (762.1,446.6)->(760.2,456.8),
  10.4 m, faces 260 on Bab Hutta Street. A **4-storey (~14-15 m) block of rough-faced ashlar** with the **corner CCTV cluster
  (3 cameras + loudspeaker horn), a yellow fire hydrant at the foot, and the two street plaques** (section 4.2) is at a
  corner of this junction (R:32: plaques "BAB HUTTA ST." on the left face, "LIONS' GATE RD." on the right face; either the
  NE corner = w288395736's SW corner, or the SW corner = w1393176149). Shop on the Lions' Gate face with a scrolled iron
  canopy. (H for the plaques at this junction, M for which corner) (**[Rev. 16]** "4-storey (~14-15 m)" is
  **unverified**. R:32 shows at least 3 storeys on the corner building before the frame cuts off, and which corner it is
  remains unresolved. I re-checked the left/right logic: only the NE and SW corners put "Bab Hutta" on the left face.)
- **w290986908**: e2 (764.2,422.5)->(762.5,441.7), 19.3 m, faces 265 on Bab Hutta Street; e3 6.1 m faces 353 on Lions' Gate
  Street; e0 19.7 m faces 84 over the car park. **3 storeys (~11 m) with a hipped red-tile roof** (OSM roof:shape=hipped,
  roof:material=roof_tiles; R:12 shows the east face with 5 windows per floor, a small arched window, a satellite dish,
  the tiled roof). (H)

### 2.11 Madrasa al-Muazzamiyya passage — w1393740933 (roof, layer 1) over 744664059
- The **27 m covered passage x 688-715**; east entrance = **pointed arch ~4.5 m wide at x ≈ 715** facing east; the building
  above has **2 storeys of small rectangular grilled windows**, a parapet with caper bushes, ~13 m in all; a **wall
  fountain** with a green framed Arabic inscription and a small basin on the north pier; King Faisal Street (123254013) leaves
  south from inside the passage at (715,436). (**[Rev. 11]**: (715.0,436.3) is the passage's **east mouth**, the last vertex of
  744664059. King Faisal is itself an 18 m covered passage (123254013, building_passage) opening off the south side just
  inside the east arch. R:13 shows its "…L ST." plaque on the south pier, looking west up the ramped passage.) Camera R:14 at (729.1,439.9) looking west, 14 m from the arch; R:13 inside. (H)

### 2.12 Bab Hutta Street frontages (291836762)
- West side: r3865791 (e9, e5, faces 86), w1393176150, w1393176149 (e1), w291741653 (e1), w1393176153, w1393164285; east side:
  w290986908 (e2), w288395736 (e4), **w291742572 e0 (17.9 m)**, **w1392503038 e0 (25.7 m)**, w1393176154, **w291742568**
  (hipped tile roof per OSM; e4/e6 face 256 onto the street), w291742571, w1545862306, w291749460 (e7 faces 246).
- Character (R:30, R:31): **tall plain walls, 3-4 storeys**, east side of massive **rock-faced bossed blocks**, west side
  smoother; few ground-floor openings; at the north end an **arch/sabat over the lane** with a building with **pointed twin
  windows and a red-tile roof** beyond (R:30). (H for character; position of R:30 along the street L)

### 2.13 Herod's Gate (Bab al-Zahra) tower — wall way 137726904 vertices 50-53 (section 3)

### 2.14 Church of the Flagellation and Terra Sancta Museum (boundary, Via Dolorosa start)
- **w744674450 Flagellation**: e3 (621.0,418.5)->(642.1,423.8), 21.7 m, faces 166 on the Via Dolorosa (the compound wall);
  the church's **portal faces west onto the Franciscan courtyard** (e1/e2, faces 255-257, towards the pedestrian area
  1549915373): a **Crusader-revival portal**: semicircular-pointed arch with a **roll of radial cushion voussoirs**, an outer
  band of **carved triangles enclosing thorn/crown motifs**, a smaller pointed inner arch with a **dog-tooth edge**, a
  **lunette window with a black iron grid studded with iron stars**, volute stops at the springing. (H for the portal: R:47;
  only 8 % of the footprint is in this sector)
- **w744674896 Terra Sancta Museum** (3 levels, OSM): e10 (649.5,425.8)->(658.2,427.6), 8.9 m faces 168 on the Via Dolorosa;
  its long north side **e14 (643.6,451.0)->(600.2,442.5), 44.2 m, faces 349** on **Aqabat Al-Quds**; entrances at the OSM
  nodes (619.7,423.6) main, (602.2,428.4), (592.7,418.4). Station II node at (589.3,419.5). (H for geometry; no facade photo, L
  for appearance: pale ashlar, 3 storeys, ~12 m)

### 2.15 Smaller landmarks (OSM, not photographed for this note)
- **Apostle Peter's Prison / St Nicodemus (Greek Orthodox)**: node (653.9,479.7) in w1392508814 (e1-e5 face 87 onto Aqabat
  Darwish). (L)
- **Indian Hospice (Zawiyat al-Hunud)**: node (576.7,636.1), west edge of the sector, on the lane of the same name. (L)
- **Schools**: w291745079 (671,616) and the Khalil Sakakini girls' school node (661.2,617.4) on Herod's Gate Ascent; Dia
  Al-Quds School (783,640); a sports pitch 291745071 (644,652). Expect plain 2-3-storey school blocks with yards and high
  walls with railings. (L)

### 2.16 Skyline elements seen from the sector (outside it)
- **Bab al-Asbat minaret** at ≈ **(835±10, 395)** on the Haram's north wall (w291836706): **cylindrical ashlar shaft with a
  thin dark band, a muqarnas corbel ring carrying a balcony with a stone parapet of small arched openings, a wide flat
  canopy roof over the balcony, a short upper drum and a ribbed lead-grey dome with a crescent finial**; ~25-28 m tall.
  Position from R:20 (cam (889.7,474.9), looking south: the minaret ~8° west of the Dome of the Rock's bearing of 206°, hence
  bearing ~214° and x ≈ 835 on the Haram wall line y ≈ 391-398) and consistent with R:11 (cam (797.7,452.2), minaret to the
  SSE over the compound walls). (M for position, H for form) **[Rev. 8] Second viewpoint:** from R:46 (cam (886.5,631.3)),
  (835,395) predicts the minaret 5.5° east (left) of the Dome of the Rock. It appears ~115 px left of the Dome, ≈ 5-6° at
  an assumed ~65° field of view. Position now rests on two cross-bearing viewpoints plus R:11: **M-H**.
- **Dome of the Rock** gold dome (734,154) visible above the Haram wall and cypresses from El-Ghazali Square and from the
  ramparts. (H: R:20, R:46)

---------------------------------------------------------------------------------------------------------------

## 3. The gates

### 3.1 Lions' Gate (Bab al-Asbat, St Stephen's Gate) — w288395731
Photos: R:07 (2015, frontal, ortho-like; measured), R:04 (2026, cam (903.6,468.4)), R:02 (2025, lion reliefs), R:01/R:05 (door
leaves, passage), R:06 (2012, inner face, cam (878.7,465.0)), R:09 (inner face from the street), R:20 (from the rampart).

**Scale.** In R:07 the 1280 px frame spans the whole gate block; taking the doorway as 3.3 m wide (the same Suleimanic design
as Jaffa Gate, whose doorway is 3.2-3.5 m in `gate.md`) gives ~105 px/m and a frame width of 12.2 m, matching the OSM outer
face e4+e5 = 12.6 m. The doorway proportion (height/width 1.41) also matches Jaffa Gate (1.45). All sizes below are from that
scale (M).

Outer (east) face, bottom to top:
- **Doorway**: ~**3.3 m wide x ~4.7 m** to the crown, jambs of large ashlar, the head a **very flat segmental arch of big
  voussoirs**, directly under a **curved convex moulded band** that follows it (~0.8 m tall). (M)
- **Tympanum** above the band: a recessed field with a **rectangular inscription panel ~1.9 x 0.6 m** centred at ~6.6 m
  (Ottoman Arabic, eroded) flanked by **two plain roundels ~0.45 m**, and a small carved boss at the apex. (H for elements)
- **Pointed arch frame**: a two-centred pointed arch of plain voussoirs with an outer moulding, **outer width ~4.7 m, apex
  ~8.0 m**. (M)
- **Lion reliefs**: **two pairs of striding felines (Mamluk lions/panthers)** in low relief, each beast ~1.1 x 0.6 m, a pair
  on each side of the arch at **~7 m**, occupying ~2.7 m of wall each side, with a small roundel between the beasts. The
  north (left) pair is often hidden by a green shade sail (R:04). (H: R:07, R:02, R:04)
- **Roundel/rosette ~0.85 m** centred over the arch apex at ~8.9 m. (H)
- **Machicolation box** centred over the door: ~2.3 m wide, projecting ~0.6-0.8 m, bottom at ~9.3 m, carried on **4 stepped
  corbels with 3 dark drop-openings**; above its top a narrow vertical slit and a small carved boss; its top rises into the
  central merlon. (H)
- Upper corners: at ~11.5-12 m on each side a **semicircular hood with radial (scalloped) mouldings over a roundel**, and
  another roundel ~1.5 m below it — four decorative discs in all. (H) (**[Rev. 19]** on the same R:07 scale the hoods sit at
  ~12.2-12.9 m and the lower roundels at ~11.0 m; the tympanum panel centre is at ~6.3 m rather than 6.6 m)
- **Crenellation**: wall top (merlon base) ~13.1 m, **flat-topped rectangular merlons ~1.9-2.1 m wide x ~1.0 m tall** (**[Rev. 19]**
  the second merlon from the left (north) is narrower, ~1.6 m, in R:07) with a
  narrow vertical slit, crenels ~0.5-0.6 m; the **central merlon (~1.9 m) is crowned by a stepped base and a pointed
  bud-shaped finial** reaching ~15.1 m. A grey antenna mast and a floodlight bracket on the top. (H for form, M for heights)
- Slit windows: one tall narrow slit (~0.15 x 1.6 m) in the wall on each side at ~4-5 m (R:04). (H)
- Masonry: **honey/ochre and cream ashlar 0.35-0.5 m courses, strongly patchy** (some blocks near-white, others orange),
  heavily pitted lower down. (H)

Passage and doors:
- **Straight E-W passage ~10 m long** (OSM 288395746); inside, a **cross-vaulted chamber** with **yellow-cream plastered
  vaults** and transverse arches of ashlar, then the larger **inner pointed arch**. (H: R:05, R:06)
- **Door leaves**: two leaves, each ~1.7 x 4.5 m, **timber clad in horizontal iron strips with dense rows of round nail
  heads**, weathered grey-brown, with a big box lock and bar; **permanently folded back** against the side walls in shallow
  recesses. (H: R:01, R:05)
- Floor: large worn limestone slabs inside; at the outer threshold a change to **small dark grey setts** of the outer road. (H: R:05)

Inner (west) face (R:06, R:09):
- A broad **plain pointed arch ~4.5-5 m wide, apex ~7 m**, with a single moulding; flat top with a **black steel railing**
  of the wall walk; caper bushes in the joints. Total ~10-11 m above the inner street. (M-L for sizes)
- On the north pier a **black sign "לטיילת החומות / إلى متنزه السور / To The Ramparts Walk" with a left arrow** at ~3 m,
  CCTV dome and conduit; on the south pier a **ceramic plaque "LIONS GATE / باب الأسباط / שער האריות"** (white tiles, dark
  text, ornamental border) at ~3 m. (H: R:06)
- Ground: **square stone block bollards (~0.45 m cubes)** and a low stone bench at the pier, a drainage grate. (H: R:06)

Outside the gate (the plaza at x ≈ 895-915, y ≈ 455-480; outside the sector):
- Road/plaza of **small dark grey setts**, steeply falling east to the Kidron (Lions' Gate Street outside, `incline=up`
  westwards); a **large fan palm** just north of the gate; **green shade sails** stretched across the gate front; galvanised
  crowd barriers and a police post; **no-parking discs** (blue, red ring and slash) on grey poles each side; a red-white
  warning triangle over **yellow plates "BARRIER AHEAD!" (Hebrew/Arabic/English) and "Authorized vehicles only"**; a drinking
  fountain node (900.8,455.0); bollards at (889.5,461.2) and (883.1,463.1); a car park (900.6,461.8). (H: R:04, R:02, R:05, OSM)

Inside the gate (the mouth, x ≈ 865-882):
- Street 4.6-5.6 m wide between w288395734 (north) and w290986909 (south); the **Sabil Bab al-Asbat** (2.3) on the north
  side by the **Burj Laqlaq stair** (rampart access); El-Ghazali Square opening south along the wall. On the south side
  **w290986909 e10 (876.7,462.5)->(852.7,457.6), faces 348**: a **~3 m pale ashlar terrace/retaining wall with plants on top**
  and a house above with **two round-arched windows with white grilles**; a blue disabled-parking sign on a pole. (M: R:09)

### 3.2 Herod's Gate (Bab al-Zahra / Flower Gate)
Photos: R:43 (2019, frontal from the north), R:44 (2026, cam (578,719)), R:45 (2023, from the road), R:33 (2025, outside), R:34
(2025, passage vault), R:35 (2025, inner face), R:36 (2026, inner exit, cam (577.4,692.4)), R:38 (2018, east face).

Geometry and orientation (H):
- Tower footprint from the wall way: north face **(585.5,709.0)->(574.7,706.1), 11.2 m, facing ~345°**; east face
  (586.8,704.2)->(585.5,709.0), 5.0 m, facing ~75°; west face (574.7,706.1)->(576.1,700.7), 5.6 m. The gate building continues
  south of the wall line by ~5-8 m (not mapped).
- The modern entrance is in the **north face** — confirmed by R:44 (camera 10 m north of the tower: the east curtain, which runs
  ENE towards the camera's latitude, appears on the left coming forward, the west curtain recedes on the right) and R:45 (from
  the road, with the trees of the sector's gardens behind the lower wall on the left = east). (H)

Outer (north) face (scaled on the 11.2 m OSM face in R:43, ~79 px/m; M):
- **Pointed arch with a moulded roll archivolt, ~2.6 m wide, apex ~5.1 m**, centred on the face (slightly west of centre).
- A **small window ~0.85 x 1.3 m with a pointed head and an iron grid** at ~7.5 m, centred over the arch.
- A **carved rosette disc ~0.9 m with a central hole** at ~10.8 m; a couple of small roundels on the face.
- **Crenellation**: wall top ~12 m, **low merlons ~0.6-0.9 m tall and 0.9-1.6 m wide, wider/taller corner merlons**, a **black
  steel railing** of the rampart walk behind them; **a black steel stair climbs the east side** of the tower from the wall walk
  (R:43, R:44). Total height **~12.5-13 m**.
- Stone: **pale cream-white ashlar, courses 0.4-0.6 m**, cleaner and whiter than Lions' Gate.
- Signs: a **red-ring no-entry disc (~0.6 m) on a grey pole** at the right (west) jamb with **yellow time plates**
  (Hebrew/Arabic/English) below. Hanging lanterns and **festoon strings of white lights** (Ramadan) across the arch in some years.
  A greengrocer's/greens stall sits in the arch mouth. (H)

Curtains either side (outside): east curtain lower (~8-9 m from the plaza), west curtain about as tall as the tower; both
crenellated with plain merlons. (M: R:33, R:45)

Passage: a **groin-vaulted chamber, vaults rendered pale cream-yellow**, an **octagonal stone-framed opening (~1.2 m) in the centre
of the vault**, transverse pointed arches of pale ashlar leading on, **hexagonal glass wall lanterns**; vendors' goods and black
shutters in the side bays. (H: R:34)

Inner (south) face (R:35, R:36):
- A tall plain face of rough cream ashlar with **four carved roundels (~0.6 m)**, a small grilled window at ~6 m, plants in the
  joints, a tree overhanging; the **exit is a low round/segmental arch (~2.2 m wide x ~2.8 m)** at the right (east) part of the
  face (**[Rev. 13]**: in R:35 the arch centre lies ~54 % of the way across the face from the west, i.e. just east of
  centre, not in the east part), **flanked above by two roundels carved with six-pointed stars**, with a **plain grey steel door leaf** folded back; a
  **black heritage sign with a teal top band** (title in Hebrew/Arabic/English, small text illegible; same design as the
  Sabil sign) right of the arch; a kiosk with a **red
  corrugated roof** abuts the face. On the west part of the face, at ~2.5 m, the **ceramic plaque "ZAWIYAT AL-HUNUD"** (3
  languages). Inner ground ~761 m (OS 1865 "herods-inside" spot at (586,693): 761.1 m). (H for elements; M for sizes)
- Inside plaza: see 1.5.

East face (outside, R:38): the **original Ottoman entrance**: a **tall pointed-arch recess (~2.6 m wide, apex ~6 m) with a moulded
archivolt, a carved rosette above the apex and a pair of curved mouldings**; its tympanum filled with masonry; in the lower part
a **rectangular doorway (~1.5 x 2.4 m) now a small shop** with crates of goods; a **grilled window with carved stone brackets** at
~9 m. The black steel stair (above) adjoins this face. (M: R:38 is geotagged inside but the stair railing at its top-left and
the receding curtain identify the east face from outside)

Outside plaza (north, outside the sector): **large grey limestone slabs** with a ~3 m band of small setts, ~~stone steps down
to the west~~ **stone steps with a steel handrail down to the EAST** (**[Rev. 5]**). The steps sit at the foot of the tower's
NE corner / east curtain, and the ground along the east curtain is ~1-1.5 m lower. Evidence: in R:43 and R:44, both looking
south, the black rampart stair is on the left, so left = east. Both show the steps bottom-left, with the R:43 handrail
falling to the left and a moped parked at the lower level by the east curtain in R:44. OS 1865 also has the gate BM
(578,714) at 759.7 m and the outside spot (634,727) at 751.6 m, so the ground falls east. **Raised lawn beds along the
west curtain with a stone kerb used as a bench** (R:33 right, R:44 right), grey slotted
steel litter bins, a **black wayfinding totem**, stone block benches, rows of **galvanised crowd barriers**, mopeds and a
police vehicle; trees (deciduous and cypress) behind the east curtain. (H: R:33, R:43, R:44, R:45)

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage, vegetation

### 4.1 Lighting and services
- **Wall lanterns**: black box lanterns on short arms fixed at ~4-5 m on facades along Lions' Gate Street (R:09); white or
  grey **hexagonal glass wall lanterns** in the Herod's Gate vault (R:34); bare bulbs and ceiling fittings in the vaulted
  passages (R:13, R:41); **strings of coloured bulbs** in the lanes (R:42) and **white festoon strings / hanging lanterns**
  over Herod's Gate in Ramadan (R:43). (H)
- **Floodlights / poles**: outside Herod's Gate, tall grey poles carrying **CCTV cameras and twin floodlight heads** (R:45); a
  white globe lamp on a pole at the north end of El-Ghazali Square (R:20). No lamp posts inside the lanes. (M)
- **CCTV and loudspeakers**: clusters of **2-3 white box cameras plus a grey horn loudspeaker** on brackets at junction corners
  (Bab Hutta / Lions' Gate corner, R:32; Muazzamiyya arch, R:14); dome cameras at Lions' Gate (R:06). (H)
- **Cables**: thick bundles of black, grey and green cables along every facade at 3-6 m and sagging across lanes; grey steel
  meter boxes and conduit; **copper/orange-brown downpipes** (R:30, R:32). (H)
- **Yellow fire hydrants** (~0.8 m) at corners (R:32, R:40). (H)

### 4.2 Signs and plaques
- **Ceramic street-name plaques**: white glazed tiles (~0.6 x 0.5 m), three lines Hebrew / Arabic / English, at ~2.5-3 m, thin
  dark border: "רחוב באב חוטה / طريق باب حطة / BAB HUTTA ST." and "רחוב שער האריות / طريق الأسباط / LIONS' GATE RD." at the Bab
  Hutta junction (R:32); "ZAWIYAT AL-HUNUD" on the inner face of Herod's Gate (R:35); "AL-BUSTAMI" at the Al-Bustami vault (R:40);
  "KING FAISAL" at the Muazzamiyya passage (R:13, R:14). (H)
- **Gate plaque** "LIONS GATE / باب الأسباط / שער האריות" (white tiles, ornamental border) on the inner south pier of Lions' Gate
  (R:06). (H)
- **Heritage interpretation signs**: black panels ~0.6 x 0.8 m with a **teal top band** and trilingual title, at ~2 m: the Sabil
  (R:10), Herod's Gate inner face (R:36). (H)
- **Wayfinding**: black sign "To The Ramparts Walk" with arrow (Lions' Gate inner face, R:06); black wayfinding totem outside
  Herod's Gate (R:33). (H)
- **Traffic signs**: no-parking discs, red-white warning triangle with yellow "BARRIER AHEAD!" and "Authorized vehicles only"
  plates outside Lions' Gate (R:04); **no-entry disc + yellow time plates** at Herod's Gate (R:43, R:44); blue disabled-parking
  sign inside Lions' Gate (R:09). (H)
- **Institutional inscriptions**: "SAINTE ANNE / PÈRES BLANCS / SÉMINAIRE GREC-CATHOLIQUE" carved in a lunette, house number
  19, white marble plaques, the "Bethesda" tile sign and the mosaic niche (R:26, R:16); "BIRTH PLACE OF VIRGIN MARY" letters
  and house number 21 on the Orthodox portal (R:08); the 14 Stations-of-the-Cross metal plaques on the seminary plaza (OSM,
  L-M). (H unless noted)
- **Arabic religious boards** over the vault mouths on Herod's Gate Ascent: a **blue enamel board with white Arabic text**
  (R:40), a **white board with red Arabic text** and a **black board with white text** (R:42), ~1.5 x 0.8 m. (H)
- **House-name tiles**: Armenian-style ceramic plaque, blue floral border, Arabic calligraphy, over a house door on Bab Hutta
  Street (R:31). House numbers on small square plates. (H)
- **Shop posters**: printed food posters (knafeh) on boards, paper notices on doors. (H: R:31, R:30)

### 4.3 Flags and seasonal dressing
- **French tricolour** on a tall white pole at the SW of St Anne (R:24, R:27). (H)
- **Green shade sails** over the outer face of Lions' Gate (R:04, R:02, R:05). (H)
- Ramadan decorations (lanterns, light strings) at Herod's Gate and in the lanes; Palm Sunday processions end inside Lions'
  Gate (not modelled). (M)

### 4.4 Bins, bollards, barriers, carts (closed-shop clutter)
- **Litter bins**: grey slotted steel cylinders with lids (~0.5 m Ø x 0.9 m) outside Herod's Gate (R:33), a black slotted bin
  by the inner face (R:35). (H)
- **Bollards**: square stone cubes ~0.45 m inside Lions' Gate (R:06); short black steel bollards ~0.6 m on Lions' Gate Street
  (R:15); OSM bollards at (889.5,461.2) and (883.1,463.1). (H)
- **Crowd barriers**: grey galvanised barriers in lines or stacked at both gates (R:04, R:45, R:44). (H)
- **Vehicles**: red Goldoni mini tractor with yellow caged trailer (R:12); mopeds and scooters in Bab Hutta Street and outside
  Herod's Gate (R:30, R:33); a white van/taxi on Lions' Gate Street (R:18). (H)
- **Carts and stalls**: "FRESH CORN" cart (white with green trim), a knafeh display case under plastic sheeting (R:31), toy and
  bread carts (R:20), a vegetable/greens stall at Herod's Gate (R:33, R:43), plastic crates, pallets and a pallet truck at
  Herod's Gate (R:43), small folding tables and black rubbish bags at door sills (R:39, R:42). (H)

### 4.5 Vegetation
- **St Anne domain** (OSM trees): **fan palms** at (821.6,461.5), (840.4,490.4), (847.5,501.9), (833.2,537.4); a row of trees
  along x ≈ 762-768, y 482-511 (west edge of the domain, behind Bab Hutta Street); many trees at (784-825, 446-511) and in the
  garden around the Lavigerie bust; grass plots 288395714-19. Species in photos: **Chinese fan palms (Washingtonia/Chamaerops)**,
  **tall Italian cypresses**, a **weeping pepper tree (Schinus)** in the courtyard (R:22), clipped bay/box shrubs, roses,
  geraniums, white annuals; **bougainvillea/geraniums on the balcony** over the courtyard arcade (R:22). (H: OSM + R:22-R:25)
- **Bethesda**: grass, red poppies, ivy, an olive tree, wild shrubs in the ruins (R:28, R:29). (H)
- **El-Ghazali Square**: young trees in square stone planters along the east wall, a terraced garden with **olive trees, fan
  palms and shrubs** on the west (OSM trees at (850-879, 408-436) and (812-839, 417-444)); **cypresses** behind the Haram wall (R:20). (H)
- **Garden at the "Group Meeting Point"**: trees at (741.2,456.0), (748.4,455.9), (744.5,466.9); garden 1393176148. (M, OSM)
- **Outside Lions' Gate**: a big **fan palm** just north of the gate (R:04, R:02); cypresses and olives down the Kidron slope (R:05). (H)
- **Herod's Gate**: a deciduous tree (ash/ailanthus type) overhanging the inner face (R:35); deciduous trees and cypresses behind
  the east curtain, raised lawn beds along the west curtain outside (R:33, R:45). (H)
- **NE corner**: cypress and pine groves among the houses (R:46). (M) (**[Rev. 8]**: R:46 looks SSW from (886.5,631.3), so
  it shows the Burj Laqlaq lane / Salahiya / St Anne area, not the NE corner north of y ≈ 670. NE corner unverified, L)
- **Flagellation courtyard**: trees at (613.4,428.3), (593.4,424.0), (595.6,418.1) (orange trees per Commons titles). (M)
- **Wall plants**: **caper bushes** (rounded clumps 0.3-0.8 m, grey-green) every few metres on the inner faces of both gates
  (R:06, R:35), on the Muazzamiyya arch parapet with a fig (R:14), on the rampart parapets (R:46: grass tufts, lichen); a
  **grapevine** trained over the arch on the Aqabat Darwish stair (R:41); trailing plants from window grilles and balconies
  (R:30, R:40); grass strips at the foot of the east wall inside (R:20). (H)

### 4.6 The city wall along the sector (OSM wall way 137726904)
- **East wall** (inner face along El-Ghazali Square and Burj Laqlaq): rectangular towers projecting outwards at y ≈ 527-544
  (x 888-896, 16 m), 563-592 (x 888-892), 606-636 (x 886-892), 691-699 (x 876-881); NE corner tower **Burj Laqlaq** at
  (863-875, 777-790). Inner face: ground-level blind arcade (El-Ghazali), the wall walk with black railing on top. (H for
  geometry, M for the inner face)
- **North wall**: Herod's Gate tower (575-587, 700-709); towers at x 661-677 (y 723-732), x 700-719 (y 733-753, where the wall
  angles), x 786-793 (y 766-771), x 822-831 (y 775-781). (H, OSM)
- Wall height from inside ~8-10 m along the north, crenellated with flat merlons and a railing of the Ramparts Walk (R:46, R:45). (M)
  (**[Rev. 18]**: R:46 is taken on the *east* wall and R:45 is *outside* the north wall, so no photo shows the north wall
  from inside. The inner height is unverified, L)

---------------------------------------------------------------------------------------------------------------

## 5. Terrain

Ground heights (m above sea level; OS 1865 spots unless marked; ±0.5 m vertical, ±6 m position):

| place | height | source |
|---|---|---|
| Lions' Gate (bench mark on the gate) | 734.4 | OS BM |
| Lions' Gate Street (850,458) | 733.0 | OS |
| Lions' Gate Street (768,445), Bab Hutta junction | 734.9 | OS |
| Lions' Gate Street (722,434) | 737.3 | OS |
| Lions' Gate Street / Via Dolorosa junction (697,427) | 740.7 | OS BM (on a wall) |
| Via Dolorosa (630,415) / (574,408) | 745.2 / 746.2 | OS |
| Aqabat Darwish (663,478), above the stair tunnel | 746.8 | OS |
| Aqabat Darwish (650,560) | 754.4 | OS |
| Herod's Gate Ascent (661,586) / (656,622) | 755.6 / 756.8 | OS |
| Herod's Gate inside (586,693) | 761.1 | OS |
| Zawiyat al-Hunud (553,687) | 766.6 | OS |
| Al Bustamy (585,567) / (637,577) | 763.2 / 759.0 | OS |
| Bab Hutta Street (761,478) / (732,512) | 736.7 / 739.7 | OS |
| Bab Hutta (717,616) / (733,636) | 744.3 / 743.1 | OS BM / OS |
| St Anne forecourt area (787,529) / (793,509) | 736.1 / 734.3 | OS (**[Rev. 14]**: (787,529) lies inside the Bethesda excavation area 126864878; it is the 1865 ground before the dig, so use it as rim/garden level, not pit floor; the forecourt itself is at (810,529)) |
| Salahiya (813,586) / (843,571) | 737.9 / 741.3 | OS |
| Al Umari (782,607) → (812,613) → (858,629) | 739.4 → 741.3 → 748.9 | OS |
| NE corner area (867,674) / (810,699) | 752.2 / 754.4 | OS |
| El-Ghazali Square south end (890,410) | ~734 | DEM |

- **Note**: the current `data/terrain.json` grid (x -150..300, y -200..200) does not reach this sector, and the SRTM-derived
  tiles smooth the valley by 3-6 m (e.g. DEM 738.4 vs OS ~734 inside Lions' Gate, DEM 742 vs OS ~736 at St Anne); use the OS
  1865 spots (as `pipeline/terrain_street.py` does). (H)

Where streets climb or descend:
- **Lions' Gate Street**: ~flat (733-735 m) from the gate to the Bab Hutta junction (x ≈ 765), then **~5 % up** to the Via
  Dolorosa junction (~740 m), the last 27 m inside the Muazzamiyya passage (floor ramps visibly, handrail on the north wall,
  R:13). No steps. (H) **[Rev. 6]**: ~5 % holds only from x 768 to x 722 (+2.4 m in 47 m). From x 722 to the BM at
  x 697 it is +3.4 m in 26 m, **~10-13 %**, so the passage is a steep ramp, not a 5 % slope.
- **Aqabat Darwish / Herod's Gate Ascent**: from the junction (~740 m) **a stair of ~5-7 m rise inside the 20 m tunnel**
  (744670522), then ~9 % up to (650,560) (754 m) in shallow stepped runs with cart ramps, then ~4 % up to the gate (761 m).
  Total **+21 m over ~270 m**. (H for heights, M for the stair split) (**[Rev. 15]**: the split is unconstrained. OS has only
  the BM at (697,427), 740.7 m on a wall, and (663,478) at 746.8 m, giving +6 m over ~52 m in all. Putting 5-7 m inside the
  20 m tunnel would leave the next 32 m flat. Treat the split as L; spreading the rise as ~3-4 m in the tunnel plus 2-3 m
  beyond is equally consistent.)
- **Bab Hutta Street / Bab Hutta**: gentle **3-5 % up northwards** (735 → 744 m over ~180 m), mostly ramped paving. (M)
- **Al Umari**: **~12 % up eastwards** from (782,607) to (858,629): expect stepped runs. (M)
- **Zawiyat al-Hunud**: **~14 % up south-westwards** from the Herod's Gate plaza (761 → 767 m in ~35 m): steps. (M)
- **Burj Laqlaq**: the stair (36948405, 30 m, `incline=up`) from the gate mouth north along the inner wall face, flights of
  ~0.15 m risers / ~0.35 m treads with an ashlar parapet and black railing (R:21), then a lane climbing to ~746-752 m in the NE
  corner. (M)
- **El-Ghazali Square**: falls gently south towards Bab al-Asbat (~1 m over 55 m). (M) (**[Rev. 14]**: unverified, with no OS
  spot on the square and a biased DEM; L)

Terraces, platforms and level differences seen in photos:
- **Bethesda excavation 5-8 m below the St Anne paths**, with steel stairs (288395744 down 17 m from the forecourt) and railings. (H: R:28, R:29)
- **Retaining/terrace wall ~3 m** on the south side of Lions' Gate Street just inside the gate (w290986909), houses on top. (M: R:09)
- The **St Anne courtyard** (R:22) and **church forecourt** are level paved platforms; the church floor is a few steps below the
  forecourt (Crusader level) (L).
- **El-Ghazali's west garden terraces** 1-2 m above the square, retained by low stone walls (R:20). (H)
- **Group Meeting Point stage** raised ~2 m (15 steps, 1395044677) on the north side of Lions' Gate Street. (M, OSM)
- **Herod's Gate outside plaza ~1-1.5 m above the road** to the west (steps, R:43, R:44); the inner exit has a low step (R:36). (H)
  (**[Rev. 5]**: the steps descend to the **east**, along the east curtain, not the west; see 3.2)
- **House doors 2-4 steps above the lanes** throughout (R:31, R:42). (H)
- OSM steps ways matched: 744670522 (Aqabat Darwish tunnel stair), 36948405 (Burj Laqlaq), 288395744 / 743659267 / 755420520 /
  288395739 / 288395742 (St Anne / Bethesda), 1395044677 (meeting-point stage), 1007230559 (5 steps outside Lions' Gate),
  843833394 (outside, along the east wall). (H)

---------------------------------------------------------------------------------------------------------------

## Model checklist

Prioritised by how much each makes the sector read as itself (shops closed, no people):

1. **Terrain bowl from the OS 1865 spots**: Lions' Gate / El-Ghazali / St Anne at ~733-736 m, Herod's Gate ~761 m, NE corner
   ~752 m; Lions' Gate Street flat for ~90 m then ~5 % up (**[Rev. 6]** steepening to ~10-12 % through the Muazzamiyya
   passage); Herod's Gate Ascent +21 m with the tunnel stair at its foot. (5)
2. **Lions' Gate outer face** (w288395731 e4/e5, 12.6 m): flush crenellated gate ~13 m to the wall top, 3.3 x 4.7 m doorway
   with a flat segmental head under a curved band, inscription tympanum, pointed frame to ~8 m, **two pairs of lion reliefs at
   ~7 m**, rosette, 4-corbel machicolation, scalloped hoods with roundels, central finial merlon (~15 m). (3.1)
3. **Lions' Gate passage and inner face**: straight 10 m passage, cream plastered cross vault, two iron-studded door leaves folded
   open, big plain pointed inner arch with the rampart railing, the trilingual ceramic plaque, "To The Ramparts Walk" sign, stone
   cube bollards. (3.1)
4. **Lions' Gate Street at the right width**: 4.6-6.4 m, opening to the **12-14 m seminary plaza at x 795-831** (**[Rev. 3]**
   north edge = front-garden wall with the seminary 5-8 m behind; south edge = raised terrace with a long stair of 2→~10 steps
   along the street), rough grey
   setts with smooth slab strips and round manholes, no canopies; **the arch at x ≈ 784-789** with the grilled arched window and
   the ancient column; **the 27 m Muazzamiyya vaulted passage** at x 688-715 with its pointed east arch and wall fountain. (1.1, 2.9, 2.11)
5. **St Anne gatehouse frontage** (w288395720 e7/e8): two-storey pale ashlar, pointed pedestrian passage with the "SAINTE ANNE /
   PÈRES BLANCS" lunette, big pointed gate with dark studded doors, mint balcony on consoles, mint shutters, dentil string course,
   the "Bethesda" tile and mosaic niche. (2.4)
6. **Church of St Anne** (w126864879): WSW-facing Romanesque-Gothic west front with pointed roll-moulded portal and lattice
   windows, small stone dome on a drum, stepped stone-slab roofs, three apses, SW porch tower, French flag; paved forecourt
   with yellow guide line and well-head. (2.6)
7. **Herod's Gate tower** (575-587, 700-709): pale ashlar, ~12.5-13 m, pointed arch in the **north** face, grilled pointed window
   and holed rosette above, low merlons with railing, black steel stair on the east side; groin-vaulted passage with the
   octagonal oculus; low inner exit in the south face with the two star roundels and grey door leaf; small inner plaza;
   outside, the steps with handrail go down to the **east** and the lawn beds run along the west curtain (**[Rev. 5]**). (3.2)
8. **Herod's Gate Ascent / Aqabat Darwish**: 3-4.3 m stepped lane, tunnel stair (risers ~0.16, treads ~0.4) with twin cart ramps,
   shallow long steps above, pointed vaults at Al-Bustami with Arabic boards, bulb strings and tarps, green/teal steel doors. (1.3)
9. **Greek Orthodox "Birthplace of Mary" portal and the Sabil** on w288395734 e4: paired Corinthian columns, round-arched door,
   "BIRTH PLACE OF VIRGIN MARY" letters, no. 21; rusticated east part with arched shuttered windows; the Sabil's pointed niche
   with two inscription panels and trough at the mouth of the Burj Laqlaq stair. (2.2, 2.3)
10. **Pool of Bethesda excavation**: 5-8 m deep ruin field with the re-erected column, apse wall, cisterns, grass and poppies,
    galvanised railings and stairs. (2.7)
11. **Residential alleys (Bab Hutta and the rest)**: 3-5 m canyons of 3-4-storey rough-faced walls, dense cable bundles, few
    openings, raised doorsteps, ceramic name plaques, timber-rafter canopies, mopeds and covered carts. (1.4, 2.12)
12. **Greenery**: fan palms, cypresses and the pepper tree in St Anne; trees in planters and the terraced garden at El-Ghazali;
    caper bushes on both gates and on arches; the fan palm outside Lions' Gate; garden/tree pockets in the NE quarter
    (**[Rev. 8]** NE corner unphotographed). (4.5)
13. **El-Ghazali Square**: 56 x 12-24 m (**[Rev. 2]** ~55 x 12-14 m, 16-18 m at the north end) pinkish slab esplanade along the wall's blind arcade, grass strip with trees, rampart
    stair, view south to Bab al-Asbat, the **Bab al-Asbat minaret** (≈ (835,395)) and the gold Dome of the Rock. (1.5, 2.16)
14. **Signage set**: trilingual ceramic street plaques (Bab Hutta St., Lions' Gate Rd., Zawiyat al-Hunud, Al-Bustami, King
    Faisal), black/teal heritage panels, yellow "BARRIER AHEAD!" plates and no-entry discs at the gates, CCTV + loudspeaker
    clusters on corners. (4.2, 4.1)
15. **Gate clutter (closed state)**: galvanised crowd barriers, green shade sails at Lions' Gate, the red Goldoni tractor with
    yellow trailer, crates/pallets and a greens stall at Herod's Gate, scooters, grey slotted bins. (4.4)

---------------------------------------------------------------------------------------------------------------

Provenance: 45 Commons photos downloaded to `data/photos_ref/s10_herod_lions/` (1280 px thumbnails, `index.json` with
title, page, author, licence, date, lat/lon, local x/y); 44 were inspected (R:19 is an interior icon view, unused). Most useful:
R:07 (Lions' Gate frontal, Godot13 2015), R:04/R:05/R:10 (Lions' Gate 2026, PikiWiki), R:06 (inner face 2012), R:12/R:18
(Lions' Gate Street), R:14/R:13 (Muazzamiyya passage), R:20 (El-Ghazali from the rampart), R:24/R:26/R:27 (St Anne), R:28/R:29
(Bethesda), R:43/R:44/R:35/R:36/R:38 (Herod's Gate), R:41/R:39/R:40/R:42 (Herod's Gate Ascent), R:30/R:31/R:32 (Bab Hutta).

---------------------------------------------------------------------------------------------------------------

## Review

Independent review, 2026-10-20. I re-read every landmark position and orientation against `data/osm_local.json`: edge
lists and outward normals, recomputed from the rings including the closing edge. I re-measured street widths by casting
perpendicular rays every 4-6 m from the OSM centrelines to building footprints, and re-projected all OS 1865 spot heights
with the affine fit from `os1865_control_points.csv` (rms 6.2 m). I opened 39 of the 45 photos, with crops where needed.
Corrections are marked **[Rev. n]** in the body. Struck-through text is the original wording, kept for traceability.

### Corrections (most important first)

1. **[Rev. 5] Herod's Gate outer plaza: the steps go down to the EAST, not the west** (3.2, 5, checklist 7). The notes said
   "stone steps down to the west". R:43 (cam (574.7,743.4), 38 m north) and R:44 (cam (578.2,718.8), 14 m north) both look
   south: the black rampart stair is on the left of the tower, so left = east. Both show the steps bottom-left. In R:43 the
   steel handrail falls to the left. In R:44 a moped stands at the lower level by the east curtain. OS 1865 agrees: the gate
   BM (578,714) is 759.7 m and the outside spot (634,727) is 751.6 m, so the ground falls ~8 m eastward. The lawn beds
   stay on the west curtain (R:33, R:44).
2. **[Rev. 1] Lions' Gate Street x 713-740 had its sides swapped** (table 1.0). The notes said the north side was open
   (garden / Group Meeting Point), 24-28 m. Ray casting from the centreline:
   - x 714-730: the north side is built (w1393164309 at 2.1-2.2 m). The 22-25 m gap is on the **south**, to r3865791.
   - R:14 (cam (729.1,439.9), looking west) shows that south side is in fact a continuous tall wall that OSM does not
     map. The street there is ~5 m.
   - x 731-745: here the north side is open (the stage and garden), and the south is w1394480978 / w1393176149 at 2.6-2.8 m.
3. **[Rev. 7] R:25 shows a different building, not the seminary** (2.5, 2.8). The façade behind the Lavigerie bust in R:25
   (and R:23) cannot be the seminary w288395732's garden front: that front lies 17-60 m west of the bust. In R:25 the
   façade's left end meets the sunlit south side of the domed St Anne church, with the bust right in front of the junction.
   That matches **w288395735's west front e8 (852.2-864.3, 487-516; faces 248)**, whose NW corner is 4 m from the church's
   SE corner, seen by a camera SW of the bust. The receding direction of the cornice confirms it. The description was moved
   to w288395735. The seminary's own façades appear in no photo, so their height and style are unverified.
4. **[Rev. 3] The seminary "plaza" was mis-described** (0.2, 1.0, 1.1, 1.5, checklist 4).
   - North edge: it is the **front-garden wall** 288395751/752, in line with w288395736's street face. The seminary façade
     is 5-8 m behind the garden 288395717.
   - South edge: it is a **raised terrace** (pedestrian area 1544948036, Stations-of-the-Cross plaques) with a **broad stair
     of long steps along the street**. It has 2 steps at the west end beside the stone gate pillars (R:12) and ~10 risers in
     two runs further east (R:18). The notes had only "a raised pavement of 2 shallow steps".
   - The 11.5-14.2 m width runs from wall to building and includes the terrace. The carriageway is ~6-8 m (L-M, from R:18).
5. **[Rev. 2] El-Ghazali Square width overstated** (1.0, 1.5, checklist 13). The notes gave 11.6-24.3 m (median 21) / 12-24 m.
   - The only OSM building east of the square's centreline is w702079358, an *amenity=shelter outside the wall* (x 900-908).
     West of the centreline lies the park, not buildings.
   - Measured to the real edges: ~13.5-14 m from the park edge to the OSM wall line for y 406-445 (≈12 m to the inner face),
     and 16-18 m at the north end, wall to w290986909. R:20 is consistent with ~12-14 m of paving.
6. **[Rev. 6] Lions' Gate Street gradient** (0.2, 1.1, 5, checklist 1). The notes said "~5 % up to the Via Dolorosa
   junction". The cited spots give 5 % only from x 768 to x 722. From 737.3 m at x 722 to the 740.7 m BM at x 697 the rise is
   3.4 m in 26 m, i.e. **13 %, or ~10 % allowing for a wall BM**. The steep stretch is the Muazzamiyya passage, which fits
   its visibly ramped floor and handrail in R:13.
7. **[Rev. 4] Arch at x ≈ 784-789: geometry corrected** (2.9).
   - w288395736 e1 faces the garden, not the street. The street's north edge does not step there: e3 and the garden wall
     share the vertex (788.6,452.5).
   - The narrowing is on the south side, where the arch's south pier is **not in OSM**. The nearest mapped building,
     w1545560831, is 10.8 m from the north pier.
   - The column's NE-pier position is now confirmed by two photos: R:17 (pier face plus the perpendicular garden wall) and
     R:18.
   - "The seminary's mint balcony" in R:18 is the gatehouse w288395720's balcony. The nearer balconies with cross railings
     are w288395734.
8. **[Rev. 8] R:46 does not show the NE corner** (1.6, 4.5, 4.6). It was taken at (886.5,631.3) looking SSW towards the Dome of
   the Rock, so it shows y ≈ 450-630. "Photos from the wall show houses" north of y ≈ 670 is unsupported, and that area is
   unverified. On the plus side, R:46 gives a **second cross-bearing for the Bab al-Asbat minaret**: (835,395) predicts 5.5°
   left of the Dome, and the photo shows ~5-6°. The minaret position is upgraded to M-H (2.16).
9. **[Rev. 9] / [Rev. 10] Widths in the OSM table.** Bab Hutta Street is 9.5-11.4 m by OSM at y 476-511, where the west-side
   buildings stand 7.5-9.5 m back, not "6.5-8 m". On Herod's Gate Ascent / Aqabat Darwish, 2.7-4.3 m holds only where both
   frontages are mapped, about a third of the samples. Elsewhere a side is open in OSM, giving 8-32 m, while R:40 (and,
   per the author, R:39 and R:42) shows a continuous 3-4 m lane. Whether the Bab Hutta setback is real or an unmapped yard wall is
   unverified.
10. **[Rev. 11] King Faisal Street** leaves at the passage's **east mouth** (715.0,436.3), the last vertex of 744664059, not
    from inside it. It is itself an 18 m building_passage, and R:13 shows its plaque on the south pier.
11. **[Rev. 15] Aqabat Darwish stair split and R:41 location.** OS gives only +6 m over ~52 m (from the BM at (697,427) to
    (663,478)). Putting 5-7 m of that inside the 20 m tunnel is not constrained by any spot height, so the split is L. R:41's
    geotag lies near the tunnel's north end, off the lane, and the photo looks up-slope through a vault, so placing that
    stair in 744670522 is M rather than H.
12. **[Rev. 13] Herod's Gate inner exit** is just east of centre, ~54 % across the face in R:35, not "at the right (east) part".
13. **[Rev. 14] Terrain caveats.** The spot (787,529) at 736.1 m lies inside the Bethesda excavation area: it is the 1865
    pre-dig ground, not the forecourt. "El-Ghazali falls gently south" has no OS spot and rests on a DEM the notes themselves
    say reads 3-6 m high, so it is unverified.
14. **[Rev. 12] Sabil sign.** The sign has teal bands top and bottom. Its English text names the fountain "Sabil Sitt Mariam"
    after the nearby birthplace of Mary, which is extra support for its position on w288395734.
15. **[Rev. 16] Heights and storeys checked against photos:**
    - Greek Orthodox house: 2 storeys rests on R:18, since R:08 shows only the ground floor. Upper-floor elements were added
      from R:18: balconies with cross railings, a frieze of blind arches, a cornice.
    - w288395736 "4 storeys, 14-15 m": unverified. R:32 shows at least 3 storeys, and which corner it is remains unresolved.
    - St Anne church heights: unverified (no usable scale in any photo).
    - Seminary height: unverified (see item 3).
16. **[Rev. 17] Gatehouse parapet.** The "oval medallions" are probably the pierced round-headed parapet openings seen on the
    courtyard side in R:22. Marked L-M.
17. **[Rev. 18] North wall inner height** is unverified: no photo shows the north wall from inside.
18. **[Rev. 19] Lions' Gate minor scale readings on R:07.** Corner hoods are at ~12.2-12.9 m, not 11.5-12 m. One merlon is
    ~1.6 m wide. The tympanum panel centre is at ~6.3 m. All of these remain single-photo measurements, M.
19. **[Rev. 20] Addition (OSM only):** the node "Paved street from Second Temple period" at (738.0,439.7), at the foot of the
    Group Meeting Point stage. Unverified.

### Checked and confirmed (no change)
- **Greek Orthodox "Birthplace of Mary" portal** on w288395734 e4 (faces 172), north side of the street. Confirmed by the
  OSM place_of_worship node (866.7,467.6) and R:08 (cam on the façade). R:08 also shows the west part smooth and the east
  part rusticated, consistent with a camera facing north.
- **Sabil Bab al-Asbat:** on the south face of w288395734 at its east end. R:10 shows the stair opening and steps to its
  right, the OSM steps 36948405 start at (882,466), and the sign text supports it (item 14). A sabil facing east onto
  the stair is ruled out because the ground in front of it is flat in R:10.
- **St Anne gatehouse no. 19:** the opening order W→E (passage, big gate, Bethesda window) holds. In R:26 the façade recedes
  to the right, so the camera is at the west end. The passage at (844,462) matches footway 288395740.
- **Church of St Anne:**
  - West front e16 faces 247.
  - The porch tower is on the right (south) in R:24; the well-head is at the SW.
  - The flag is on the south side: R:24, and R:27 from the east with the flag on the left.
  - The apses (e3-e11) and the north and south faces are as stated.
- **Herod's Gate:**
  - The entrance is in the north face. R:44 (east curtain coming forward on the left, west curtain receding) and R:33/R:45
    (taken from the NW, showing the west side face) are consistent only with that.
  - The black stair is on the east side, and the blocked original entrance is on the east face (R:38).
  - The sizes check out: on 79 px/m in R:43, policemen against the face measure 1.84 m and the wall top is ~11.8-12.7 m.
- **Lions' Gate:**
  - Outer face e4+e5 faces 80 and the inner face e1 faces 259.
  - R:06 shows the ramparts sign on the north pier and the ceramic plaque on the south pier.
  - Outer-face heights re-measured on R:07: doorway 4.76 m, lions at 7.0 m, apex 8.1 m, wall top 13.1 m, finial 15.1 m.
  - The passage is straight (R:07 sees through to the street).
- **Bab Hutta junction plaques (R:32):** only the NE or SW corner puts the Bab Hutta face on the left. The author's
  either/or is correct and remains unresolved.
- **Widths re-measured:** Lions' Gate Street at the gate (4.4-5.5 m), x 748-790 (5.2-6.7 m) and Via Dolorosa (4.3-6.5 m)
  match the table.
- **Terrain table:** all 20 OS 1865 values re-projected and match within 0.1 m.
- **Flagellation and Terra Sancta:**
  - The Flagellation is on the north side of the Via Dolorosa (its e3 runs 2.0 m north of the centreline). Its west portal
    faces the courtyard 1549915373, and R:47 matches that portal.
  - Terra Sancta: e10 is on the Via Dolorosa and e14 on Aqabat Al-Quds.

### Not verifiable from the local data (left as the author's, now marked)
- Commons "Palm procession (34)" and "Sabil IMG 1537" are not in the local set and were not opened.
- Group Meeting Point stage, the 14 Stations plaques, the Indian Hospice and the schools are OSM only, as the author marked.
- Church, seminary and Bab al-Asbat minaret heights; the NE-corner buildings; the north wall's inner face.
- El-Ghazali slope; Lions' Gate inner-arch size (M-L as given).
- The exact x of the south-side stair on the plaza (L-M).
- The photos not opened in this review: R:01, R:02, R:05, R:19 (unused), R:39 and R:42. R:04 was checked only on a crop
  of the doorway and signs. The author's descriptions of these photos were left as written.
