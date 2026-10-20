# s02_zion: Zion Gate and the southern walls: visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (lat 31.7766282, lon 35.2275435).
Sector polygon (`data/sectors.json`, id `s02_zion`): x 23..330, y -300 down to the south wall (y -412 at the SW
corner, -422 at Zion Gate, -395 at x 328); 34,500 m². The spec (`data/spec/s02_zion.json`) holds 36 records: 24 OSM
footprints (Zion Gate w290671706 is a landmark, owned by `landmarks_gates.py`) and 12 infill pieces (f3, f4, f12,
f113-f117, f159-f161, f339).
Photos: `data/photos_ref/s02_zion/KNN_<pageid>.jpg`, cited as **A06**, **B01** and so on. Titles, authors, licences,
dates and GPS are in `index.json` there. Groups: A = Zion Gate Square and Zion Gate Street, B = Armenian
Patriarchate Rd, C = the Armenian compound buildings (church hall, museum, library, Holy Archangels), D = the
Jewish-Quarter edge (al-Disi mosque, Ayyubid ruins), E = views from the ramparts and over the wall, G = wall plants.
Also cited: `data/photos_ref/gates/` **GZ:nn** (Zion Gate set, see `gates.md` §3).
Scale from people (1.7 m), doors (2.2 m) and OSM edge lengths. Many Commons geotags here are not camera positions
(see Provenance); the camera positions quoted below were re-derived from what each photo shows against OSM.
Confidence: **H** = 2+ photos, or OSM geometry plus a photo; **M** = one clear photo or a consistent estimate;
**L** = inferred or seen only at an angle.

> Status: research pass complete, 2026-10-20. 64 Commons photos kept (index.json), 41 more were downloaded and
> rejected (wrong place, interiors, duplicates; kept in `build/spec_s02_zion/rejected/`). Two render batches of the
> current model: `renders/sectors/s02_zion/r0_initial/` (6 street views) and `r1_photomatch/` (6 views matched to
> photos A16, B01, A19, A25, C03, A23; side by side in `sbs_1.jpg`, `sbs_2.jpg`).
> Coverage: Zion Gate Square, Zion Gate Street, Armenian Patriarchate Rd (south stretch and the stretch along the
> wall), the church hall by the pitch, the Mardigian museum, the Gulbenkian library and the Habad end are
> photo-backed. The private lanes (HaMalakh, the convent lane 290677066), the block between Ararat and HaMalakh and
> the parking lot's north part are OSM only or seen from far.

---------------------------------------------------------------------------------------------------------------

## 0. Key facts and likely model errors (summary)

1. **This is a quarter of walls, not of facades.** Every street is a road between high blind walls: the city wall
   (~11 m inner face) on one side and 3-8 m compound and retaining walls on the other. The OSM `barrier=wall` ways
   that make these walls (1056503910, 1056503911, 1546332724-26) are **not built at all** today (base and sector specs
   have no trace of them), and the parking lot's road wall is not in OSM. In the renders the roads run past open
   paving and the far-off generic blocks behind (r1 `B01`, `A19`). **H** (B01, B04, B18, A06, A29, A19; OSM)
2. **Zion Gate Street's north side is a single-storey shop row**, ~4.5 m high, under one continuous shed canopy,
   not the 14.5 m four-storey block of the model (w290677065, e8/e9/e11 facing S). The taller rock-faced blocks
   (3-4 storeys) only start at the east end near Habad Rd. **H** (A16, A15, A25, A28; r1 `A16`, `A25`, `A23`)
3. **Both roads are asphalt.** Armenian Patriarchate Rd (APR) is a ~5 m asphalt road with a ~2.5 m sidewalk and
   black-and-white banded bollards; Zion Gate Street is ~6 m of asphalt with pay parking along the city wall and a
   4-5 m slab sidewalk with young trees on the north. The model paves them in pale slabs. **H** (B01, B04, B18,
   A16, A25, A29, A14)
4. **Zion Gate Square** (inside the gate, x 196-230, y -400..-416) is paved in honey limestone slabs with a curved
   band of pale setts (a turning circle) and black bollards, closed on the north by a **~5.5 m rubble retaining wall
   topped by a ~4 m steel-mesh fence** with floodlights: the raised Armenian sports pitch. **H** (A06, A07, A29,
   A02, GZ:15, GZ:16)
5. **The pitch (290679221) and the church hall beside it stand on a terrace ~5-6 m above the road**, not at street
   level as `street_z` has it (-1.5). **H** for the step (A06, A29, C03, C06, C07), **M** for the value.
6. **West of the gate tower** the APR wall stretch ends at the tower's west face (w290671706 e0), with a
   **semicircular three-step seating platform**, white stone posts, benches and a pointed niche in the curtain wall in
   the angle between tower and curtain (~(186-194, -406..-413)). **H** (A19, A11, B04, GZ:14, GZ:17)
7. **The domed neoclassical church hall (w290679226)** beside the pitch (pediments, oculus, central stone dome,
   two tiers of round-arched windows) is the one big building that reads from the gate, the square and the ramparts.
   The model has a generic flat block. Commons calls it the Church of the Holy Archangels (C04, A28); OSM tags it
   only with a school node, and maps the (medieval) Holy Archangels church at w290677052. **H** for the form and
   position (C03, C04, C06, C07, A02, A28), **L** for the name.
8. **The Mardigian Museum (r3862591) is a two-storey arcaded quadrangle with a glass-roofed courtyard**, ~10-11 m
   high, not a 15 m solid block; the spec drops OSM's inner ring. **M** (C09, C10, C11, C15, C16; OSM inner ring)
9. **The Gulbenkian Library is in this sector** at OSM w265410576 ((128,-327)), with its khachkar-flanked stair on
   the east face. Two geotags (C17, C18) agree with OSM; the position in `s01_armenian.md` L11 (a court at
   (142,-255), from one geotag) is wrong. **M**
10. **The Dormition Abbey and its bell tower (outside the walls, base context r3925223)** rise over the south wall
    in every view to the south and west (B01, E01, E13, A30). The base has a 9 m flat block for it. **H**
11. **The Ayyubid tower (r9453421)** is a sunken ruin garden (walls 1-2.5 m high, ~3 m below the street, stairs
    and railings), not a 7 m building. **H** (D06-D09, D14, D05)
12. **al-Disi mosque and its cylindrical minaret** (~18-20 m) stand on the Habad loop at the sector's NE corner; no
    OSM feature. **M** for the form (D01, D10, D11, D12, D13), **L** for the exact position.
13. **Infill slivers are mostly walls or gardens, not buildings**: f160 (the museum's north garden, C18), f4 (a 2 m
    strip south of the library and along the convent lane), f161 (the pitch's north and east edges), f339 (the edge of
    the Jewish-Quarter parking), f159 (park edges). Their facades also hide real faces (museum e0, library e4 are
    "not exposed"). **M** (C18, C04, OSM areas)
14. **No steps on Zion Gate Street's north sidewalk** (footway 1546610953): the model puts a 12-tread run there,
    while the photos show a sidewalk sloping with the road. **H** (A16, A25; r1 `A23`)
15. **"Habad" is in `SOUQ_STREETS` at 0.7 shop share.** The two OSM ways named "Habad" are only the asphalt one-way
    loop at the sector's NE corner (residential blocks, the mosque, the parking); the photos show no shop rows.
    **M** (D11, D13, A14)

---------------------------------------------------------------------------------------------------------------

## G. OSM geometry of the core (from data/osm_local.json and data/spec/s02_zion.json)

| feature | OSM | position (local m) | notes |
|---|---|---|---|
| Zion Gate (landmark) | w290671706 | x 194-213, y -405..-422; 15.2 x 12.2 m | the tower projects ~12 m INTO the city from the wall line; S face on the wall line; e0 (196.2,-410.8) faces 291° (west face, end of the APR wall stretch), e2 (210.4,-416.3) faces 111° (inner door), e3 (205.5,-407.9) faces 21° (onto APR); outer door n5003920348 (198.4,-418.2); passage 722675054 L-shaped to the inner door (210.7,-415.7) |
| Zion Gate Square (no OSM area) | ways 26492736 end, 29881233 (sett), 1546614903/04 | x 196-230, y -400..-416 | open space between the tower's N/E faces, the pitch wall 1056503910 (y ≈ -400..-404) and the start of Zion Gate St |
| Church hall by the pitch | w290679226 (school node n685547952 (187.0,-374.7)) | x 169-196, y -364..-389; 562 m² | e2 (183.4,-389.0) faces S 17.4 m (gable end towards the city wall); e4 (194.5,-377.9) faces E 22.6 m (onto the pitch, central pedimented bay); e5 N 24.2 m; e0 W 19.7 m; e1 SW chamfer 7.5 m |
| Sports pitch | way 290679221 (leisure=pitch) | x 193-223, y -344..-403; 1,387 m² | raised terrace (§5); tennis court 1545547641 (x 201-215, y -361..-386) inside |
| Garden of the church/school | way 290679223 (leisure=park) | x 154-198, y -340..-404 | trees n14084712123-26, n14057425140-43 |
| Mardigian Armenian Museum | r3862591 (OSM inner ring = courtyard) | x 125-160, y -345..-399; 1,479 m² | e1 (128.1,-370.6) W 51.2 m, e2 (139.5,-397.4) S 28.6 m, e3 (156.9,-373.5) E 51.1 m, e0 (145.5,-346.7) N 29.3 m (hidden by infill f160) |
| Cemetery strip | way 157676995 (grave_yard, Armenian) | x 112-131, y -343..-402 | between the APR wall (x ≈ 111.5) and the museum's W face; not seen from the street |
| Galoust Gulbenkian Library | w265410576 | x 113-141, y -319..-335; 419 m² | e5 (141.2,-327.4) faces E 16.0 m (entrance stair, C17); e6 N 25.1 m; e4 S 24.7 m (hidden by f4); e1 W 6.9 m on APR |
| Convent block (s02 part of St James Monastery, landuse 290668987 reaches y -339) | w290677057, w290677071 | x 154-206 / 180-223, y -277..-338 | w290677071 e0 (200.9,-335.4) faces S 42.6 m onto the convent lane 290677066 |
| Holy Archangels church (Deir ez-Zeitun) | w290677052 | x 241-257, y -363..-372; 132 m² | e1 (249.2,-371.3) S 15.5 m, e3 N, e0 W 8.5 m, e2 E; surrounded by w290677063/67, w1546614907 and park 290677059 |
| Zion Gate St north row | w290677065 | x 227-269, y -382..-405; 579 m² | e8 (241.6,-403.2) faces 172° 23.7 m, e9 (256.4,-400.6) 164° 6.4 m, e11 (264.2,-396.7) 165° 9.7 m (all onto Zion Gate St); e7 (228.9,-401.8) 253° and e6 (227.6,-392.7) 267° onto HaMalakh |
| East-end block | w1396126810 | x 269-282, y -383..-395 | e0 (276.1,-393.0) faces 165° 13.0 m; e1 (282.3,-387.0) faces 88° 8.7 m (driveway 1546614906) |
| Habad block | w290677064 | x 284-297, y -333..-389; 526 m² | e4 (295.2,-358.3) faces 93° 50.1 m onto Habad St / Habad; e1 (287.5,-389.0) faces 172° 6.8 m; e0 (285.6,-361.1) faces 273° 56.7 m onto park 290677059 |
| Ayyubid Tower (ruins) | r9453421 (three rings) | main ring x 305-331, y -381..-407; two 10 m² bits | historic=ruins; inside park 290701302 / archaeological site 290701310 ("Garden of the Redemption", x 300-462) |
| Armenian Quarter Residents Parking Lot | way 290669001 (private) | x 24-104, y -300..-406; 6,669 m² | aisles 290668999, 1085710644/45/46, 1394456883, 1085710643 (S edge, exits onto APR at (114.3,-401.8)), 737595669/70 (exit gate n6905949345 (102.3,-339.5)) |
| West-side gardens | ways 1546332714 (private garden), 290669018 | x 58-94, y -275..-337 | building w290669003 (x 78-98, y -296..-332) between them and APR |
| Jewish-Quarter parking (south) | way 1392375524 | x 305-341, y -326..-376; 1,588 m² | east of the Habad loop; park 290701302 (x 307-346, y -376..-391) south of it |
| Park east of Holy Archangels | way 290677059 | x 259-286, y -338..-389 | trees n14057570884-87; footway 1546614905 and driveway 1546614906 from Zion Gate St |
| "Hidden Gate" | n9351289716 | (24.7,-334.1) | historic site in the west wall at the parking lot |

Streets (OSM centrelines, street_z in brackets, metres relative to the Jaffa Gate street datum 770.58 m asl):
- **Armenian Patriarchate Road** way 26492736 (`residential`, asphalt, oneway, sidewalk both): (107.0,-293.1)
  [+4.5] → (108.3,-338.7) [+4.1] → (108.2,-359.5) → (109.1,-385.2) [+2.3] → (111.1,-397.9) → (114.3,-401.8)
  [+0.9] → (122.4,-406.0) → (172.2,-408.0) [-0.4] → (185.9,-406.5) → (196.1,-403.5) → (202.2,-402.9) [-1.3] →
  (209.6,-405.5) → (220.6,-409.8) [-3.2]. North of y -293 it continues as the tunnel 290669005 (s01).
- **Zion Gate Street** way 496167694 (`residential`, asphalt, 2 lanes): (220.6,-409.8) [-3.2] → (235.0,-410.4)
  → (258.4,-406.5) [-6.6] → (279.4,-403.3) → (294.7,-394.9) → (296.6,-392.5) [-7.7]. North sidewalk 1546610953
  (229.0,-405.3) → (290.1,-391.5); crossing 1546614904 and sidewalk 1546614903 to the square.
- **Habad Road** 1545832723 (296.6,-392.5) → (300.0,-379.5) [-8.4]; then the one-way pair **Habad**: 1545832724
  (west carriageway, x 300-305, drawn and driven southbound (309.2,-323.5) → (300.0,-379.5)) and 290677058 (east
  carriageway, x 303-309, northbound (300.0,-379.5) → (309.2,-323.5));
  **Habad Street** 44376195 (pedestrian, sett) ends at (290.1,-391.5) after running down x 295-304; **Batei Mahase**
  290677070 (309.2,-323.5) → (330,-320) [-9.7]; steps 1546610952 (306,-319) → (302,-319).
- **Gate approach** 29881233 (pedestrian, sett) (220.6,-409.8) → (210.7,-415.7) (inner door); gate passage
  722675054 (building_passage) → outer door (198.4,-418.2); 722675053 outside to (202,-425).
- **HaMalakh** (`foot=private`): 1056503912 (231.4,-287.6) → (222.2,-308.9) [+0.1] (gate n5732626537 (222.2,-308.9));
  290677053 → (229.9,-329.7) [-2.8]; 383484416 → (222.8,-352.5) → (224.6,-388.0) → (226.0,-403.0) (gate
  n9707887912 in the square's north wall) → (226.2,-410.8) [-3.9].
- **Convent lane** 290677066 (footway, `foot=private`): (224.2,-341.2) [-3.0] → (156.9,-336.4) → (142.4,-341.3) →
  (111.4,-339.6) (gate n9707887913) → (108.3,-338.7) [+4.1] on APR. Model has 35 treads on it (§5).
- **Ararat** 26492744 runs along the sector's north edge: (303.3,-302.0) [-8.8] → (266.1,-297.5) → (231.4,-287.6)
  [+1.9] (mostly s01/s06).
- Footways 290677055 (270,-330) → (266,-298), 1546614905 (283,-382) → (271,-366).

Walls (`barrier=wall`, none of them built today):
- **1056503910** `wall=stone`: (110.9,-337.9) → (111.4,-339.6) → (111.8,-386.0) → (112.6,-392.1) → (114.5,-399.0) →
  (116.1,-401.2) → (120.7,-402.8) → (180.0,-404.6) → (186.3,-403.4) → (189.3,-399.7) → (223.0,-403.7) →
  (226.0,-403.0) → (228.8,-401.6). It is the east wall of the APR south stretch, the north wall of the APR wall
  stretch, and the pitch's retaining wall along the square.
- **1056503911**: (114.2,-307.9) → (111.4,-315.2) → (110.9,-337.9): the convent's road wall, APR east side y -308..-338.
- **1546332724** (103.7,-323.6) → (103.8,-336.6) → (98.7,-336.4); **1546332725** (65.0,-303.8) → (66.6,-335.9);
  **1546332726** (66.6,-335.9) → (95.1,-336.7): garden walls west of APR.
- Missing from OSM: the **parking lot's road wall** along APR's west side, x ≈ 104-105, y -340..-400 (B01).

City wall (OSM line = outer face): (18.9,-412.2) SW corner → (102.0,-413.1) → (185.6,-413.6) → gate (194.0,-416.5)
… (208.2,-422.0) → (217.9,-420.6) → (293.6,-408.6) → tower jog (293.8,-411.4) (299.7,-410.4) (305.9,-409.5)
(305.8,-406.1) → (328.4,-399.4) → jog (327.6,-395.7) → (374.7,-385.3) (ways 511655207, 391433911).

OSM wall-to-wall widths (perpendicular rays every 6 m to OSM footprints, `barrier=wall` lines and the city-wall line;
script `build/spec_s02_zion/scripts/widths.py`, output `widths.txt`):
- APR south stretch (y -340..-400): the east wall 1056503910 is **2.7-3.5 m** from the centreline; nothing on the
  west in OSM (parking). With the unmapped west wall at x ≈ 104.5 (B01) the road is **~7-7.5 m wall to wall**
  (≈ 5 m asphalt + 2.5 m east sidewalk). **M**
- APR north part (y -293..-338): 16-20 m between w290668993/wall 1056503911 (E) and w290669003 (W); infill f3/f12
  narrows it to ~11 m. A junction space with the parking and convent-lane gates at y ≈ -339.
- APR wall stretch (x 120-185): **9.2-10.2 m** from wall 1056503910 to the city wall's OSM (outer) line, i.e.
  ~6.5-7 m clear between the walls (wall ~3 m thick). Widens to 17 m at x ≈ 190 (the seating pocket).
- APR north of the gate tower (x 196-212): **5.2-8.3 m** between the pitch wall and the tower's N face.
- Zion Gate St: **13.3-13.8 m** from w290677065 to the city-wall line at x 234-258 (≈ 10.5-11 m clear), 16-18 m at
  x 264-282, 20-25 m at the Habad end.
- Convent lane 290677066: 3.4-6.0 m between w290677071 and the gardens (x 175-222); 9.9-10.6 m between the museum and
  the library (x 133-139).
- HaMalakh: 1.9-2.6 m from the centreline to w290677067 on the east (x 223-226, y -348..-384); the west side is the
  pitch (open). A 5.0 m pinch at w1546612711 (layer 1, (224,-385)), probably a bridge or arch over the lane.

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and STREET PROFILES

### 1.0 Character
The south-west of the walled city is its emptiest corner. Two quiet **asphalt service roads** run inside the walls:
APR down the west side and along the south wall to Zion Gate, then Zion Gate Street east to the Jewish Quarter.
They pass **long blind walls**: the crenellated city wall (~11 m), rubble and ashlar compound walls of the Armenian
Patriarchate (3-8 m, trees and cypresses over the top), and the pitch's retaining wall with a high steel-mesh fence.
Buildings are few and set back: the domed church hall and the two-storey museum quadrangle inside the compound, a
single-storey souvenir row on Zion Gate Street, and 3-4 storey rock-faced blocks at the Habad end. Open ground is
everywhere: the big Armenian residents' car park in the SW corner, gardens, the sports pitch, the Jewish-Quarter car
park and the sunken Ayyubid ruins. Cars, pay-parking signs, bollards, lamp posts, a ka'ak cart, tour groups and the
odd donkey are the street life. Stone is pale cream to grey limestone; the compound walls are rough rubble, the city
wall big weathered ashlar, the newer buildings rock-faced (rusticated) ashlar. Over everything to the south and
west rise the Dormition Abbey's conical roof and bell tower outside the walls. **H** (all groups)

### 1.1 Profile table (which OSM street gets which profile)

| profile | OSM streets (way id / name:en) | key look |
|---|---|---|
| P1 walled service road | APR south stretch (26492736, y -293..-400) | asphalt ~5 m + 2.5 m east sidewalk with black/white bollards; 6-8 m rubble wall E, ~3 m dark rubble wall W (parking); no doors, no shops |
| P2 road along the city wall | APR wall stretch (26492736, x 114-196) | asphalt 5-6 m between the city wall (lanterns on scroll brackets) and a 5-6 m compound wall with trees over it; ends at the gate tower's west face and the seating niche |
| P3 gate square | Zion Gate Square: 26492736 x 196-221, 29881233, 1546614903/04 | pale honey slabs with a pale-sett turning circle, black bollards, modern dark grey lamp posts, benches; 5.5 m retaining wall + 4 m mesh fence on the N; the gate's inner door on the W |
| P4 shop street along the wall | Zion Gate Street (496167694) | asphalt 6 m, pay parking along the city wall; 4-5 m north sidewalk with tree pits; single-storey souvenir row with a continuous shed canopy; 3-4 storey blocks at the E end |
| P5 Jewish-Quarter service loop | Habad Road (1545832723), Habad (1545832724, 290677058), Batei Mahase (290677070) | asphalt, red-and-white kerbs, fences on retaining walls, 4-storey residential blocks, car park, the al-Disi mosque |
| P6 private compound lanes | HaMalakh (1056503912, 290677053, 383484416), convent lane 290677066, footways 290677055, 1546614905 | 2-5 m paved lanes between garden walls and convent buildings, gated at both ends (OSM gates); trees; mostly unseen (L) |

### 1.2 P1: Armenian Patriarchate Rd, south stretch (y -293..-400)
Photos: **B01** (2010, cam ≈ (107,-352) on the east sidewalk, looking S, geotag (105.4,-350.1)), B05 (from the
south tunnel mouth, looking N into s01), B08 (L, position unconfirmed), E13 (from the west wall, parking lot).
- **Width and plan**: almost straight N-S at x ≈ 108-109, bending SE at y ≈ -395 into the wall stretch. Asphalt
  carriageway **~5 m**, with a **~2.5 m sidewalk on the EAST side only** (concrete/asphalt, square drain grates),
  separated from the road by **black-and-white banded steel bollards (~1.0 m, Ø 0.12 m, every ~2.5-3 m)**. **H** (B01;
  B04, B18 show the same bollards along the wall stretch)
- **East wall** (1056503910 x ≈ 111.5, faces W): **pale rough-faced limestone blocks set in thick grey pointed mortar**
  (raised mortar joints, whitish stones 0.3-0.6 m), **≥6 m high** (out of frame near the camera; trees overhang it at
  ~6-8 m). No openings except, at the south end, a small steel-and-glass shelter canopy on posts. Trees (broadleaf,
  dark green) over the wall from the cemetery strip and museum garden. **H** for form, **M** for height (B01)
- **West wall** (not in OSM; x ≈ 104.5, y -340..-400, faces E): **dark brown-grey rubble masonry, ~2.5-3 m**, with a
  slight batter, trees of the parking lot behind. **M** (B01)
- **Vista south**: the crenellated south city wall with a **tower with a round-arched window**, and over it the
  **Dormition bell tower** (domed top). A blue one-way sign at the bend. **H** (B01; E13 from the west wall)
- **North part** (y -293..-340): a wider junction south of the tunnel w1394456881 (s01) with the parking-lot exit gate
  n6905949345 (102.3,-339.5) on the west and the convent-lane gate n9707887913 (111.4,-339.6) on the east (arched
  gateway, C18 from the inside). Black bollards and parked cars (B05, 2024). The west side (f12 infill, w290669003)
  is unphotographed; B08 shows a long pale ashlar building with round-arched mesh-grilled windows and a Y-post fence
  with concertina razor wire, from the same 2009 series as the geotag (106.4,-326.1) (L).
- No shops, no house doors. **H**

### 1.3 P2: APR along the south wall (x 114-196, y ≈ -402..-408)
Photos: **B04** (2012, cam ≈ (135,-406), looking ESE at the gate tower's west face), **B18** (2011, same view with a
taxi and a tour group), B03 (2007, the bend at (112,-398)), E10 (from the ramparts, looking W), **A19**, A11.
- **Width**: asphalt ~5-6 m, no sidewalks, between the city wall's inner face (S) and the compound wall 1056503910
  (N). Clear width ~6.5-7 m. **H** (B04, B18; OSM)
- **City-wall side**: the inner face of big weathered ashlar, ~10-11 m to the wall walk, with **white glass lanterns on
  black scroll brackets at ~5-6 m, every ~10 m**, small plants in the joints. **H** (B04)
- **Compound side**: a rough rubble/ashlar wall **~5-6 m** (sunlit, slightly battered), trees and the church hall
  behind it. **H** (B04, B18)
- At the east end: **black-and-white bollards and white stone blocks** across the mouth of the seating pocket, then the
  tower's **west face** (rubble-faced, arrow slits). **H** (B04, A19)
- The road falls ~2 m from the SW bend (+0.9) to the gate (-1.3). The parking lot's south exit (1085710643) joins at
  (114.3,-401.8). **M**

### 1.4 P3: Zion Gate Square (x 196-230, y -400..-416)
Photos: **A06**, **A07**, A08 (2024), **A01**, **A02** (2008/2010, cam (219.5,-405.7), looking WSW at the inner face),
A21, A22, B15 (2012-2024), A29 (2012), A17, A03, GZ:15, GZ:16; from above A15, A16, C03.
- **Paving (current, 2022-2026)**: large **honey/beige limestone slabs (~0.4 x 0.8 m) in courses**, with a **curved band
  ~0.3 m wide of small pale setts** describing a turning circle of ~10-12 m radius in front of the gate's east face.
  **H** (A06, GZ:15, GZ:16). In 2008-2012 the area in front of the inner door was **dark grey setts laid in fans**
  (A01, A02, A29); use the current state.
- **North side** = wall 1056503910 (189.3,-399.7) → (223.0,-403.7) → (228.8,-401.6), faces S: a **rubble retaining wall
  ~5.5 m** (person 1.7 m stands at its foot in A06; wall ≈ 3.3 person heights), coping on top, then a **steel-mesh
  fence ~4 m on square posts** with **floodlights on poles**; a few square putlog holes and dry plants in the wall.
  At its east end, the **HaMalakh gate** (n9707887912, (226,-403)): a **pointed-arch doorway ~2.2 m wide with grey
  steel double doors**, and further east the wall steps down to ~4 m with a railing/barbed wire on top. **H** (A06,
  A07, A29, A02)
- **West/south side**: the gate tower's east face e2 with the inner door and the north face e3 (gate module). A tiled
  sign on the tower: **"כיכר שער ציון / ساحة النبي داود / NABI DAOUD SQUARE"** (white tiles, ~0.6 x 0.3 m, ~2.5 m
  up, right of the door) next to blue one-way and red no-entry signs. **M** (A02 zoom)
- **Furniture**: **black steel bollards (~0.9 m, reflective band) every ~2-3 m** along the wall foot and the sidewalk
  edge; **two dark grey square-section lamp posts (~6-7 m) with a flat arm luminaire**; a **wooden slat bench** on black
  legs; a **round black slatted bin**; a wooden utility pole. **H** (A06, A07, A16)
- Street life: a **blue ka'ak bread cart** with a vendor (A02), a donkey (A06-A08). **M**

### 1.5 P4: Zion Gate Street (496167694, x 221-297)
Photos: **A16** (2022, from the ramparts over the gate, looking ENE), **A15** (same, wider), **A25** (2011, cam ≈
(222,-409), looking E), **A29** (2012, from the inner door, looking E), **A23** (2013, cam ≈ (252,-406), looking W at
the gate), **A28** (cam on the ramparts ≈ (298,-406), looking W), A13, A08, A14, A27, A26, A20.
- **Section** (A16, west part): **parallel parking along both kerbs** (pay parking, signs on the wall side), a
  ~1-1.5 m slab footway at the city-wall foot with black bollards, **asphalt carriageway ~6 m between the parked
  rows** (single dashed centre line in parts), and a **4-5 m north sidewalk of pale slabs**, kerb ~0.15 m. **H**
  (A16, A25)
- **Grade**: falls ~4.5 m east over 80 m (5.6 %, street_z -3.2 → -7.7); the photos show a continuous slope with no
  steps on either side. **H** (A25, A29, A16)
- **North sidewalk furniture**: **young trees in ~1 m square pits every ~12-15 m**, the same **dark grey lamp posts**
  as the square (in 2011: silver poles with a lantern head, A25), a **wooden bench**, **round grey slatted bins**, a
  white concrete planter cylinder (2011). **H** (A16, A25)
- **North frontage, west to east**:
  - x 221-229: the end of wall 1056503910 / HaMalakh gate (see 1.4); in 2011 a rubble wall with a **round-arched grey
    steel door** and a **green double door with a small arched panel over it** and a little round-arched window (A25).
  - **w290677065 e8 / e9 / e11 (x 230-269, facing 164-172°)**: a **single-storey shop row ~4.5 m high**, flat roofs
    with AC units and water heaters set back. **Continuous shed canopy ~2 m deep at ~2.6-2.8 m**, of **white/grey
    corrugated sheet on steel brackets** (one stretch of pale fabric awning; in 2011 brown fabric awnings). Shops:
    Armenian ceramics and embroidered textiles hung on the wall, T-shirts and souvenirs, a kiosk with a Pepsi
    umbrella. Closed shopfronts: **pale grey panelled steel double doors/roll-down shutters** (A08), one old studded
    timber door. Sign **"BERJ GEJEKOUSHIAN ARMENIAN SOUVENIR SHOP «YEREVAN»"** (white board, Armenian flag, Ararat
    painting) at ≈ (250,-402) (A13); house number plate "15". **H** (A16, A15, A25, A28, A13, A08)
  - **w1396126810 (e0 faces 165°, e1 faces 88°)** and the east end of w290677065: **2-4 storey rock-faced
    (rusticated) ashlar blocks**: the corner block has **4 storeys, round-arched top-floor windows with small iron
    balconies**, rectangular windows below with railings, ground-floor windows with grilles, a **green steel gate**,
    water heaters and dishes on the roof (A28, A20). A lower 2-storey rock-faced block with a round-arched door
    between it and the shop row (A28). **M** for which footprint is which.
- **South side** = the city wall: ~10-11 m inner face with crenellations and the grey ramparts railing on brackets;
  a **blind pointed arch** in the wall face ~10-15 m east of the gate; a **diagonal stone stair without railing**
  climbing the wall face to the wall walk east of the gate (x ≈ 215-235). **H** (A23, A25, A29)
- **Signs**: blue **"P" pay-parking signs with yellow plates** ("PAYMENT SUN-THU 8-18, FRI 8-13") on poles along
  the wall; ceramic street sign **"רחוב שער ציון / طريق باب النبي داود / ZION GATE ST."** (white tiles, olive-green
  border) on the masonry; convex traffic mirror on a pole at the east end (A14); red-and-white painted kerbs at the
  Habad end. **H** (A23, A16, A27, A14)

### 1.6 P5: Habad Road / Habad loop / Batei Mahase (x 296-330, y -300..-393)
Photos: D11 (2018, the mosque across the road), D10, D01, D12, D13 (elevated view), A14, A28, A20.
- Asphalt one-way loop round a central island, **red-and-white kerbs**, a raised pavement with a **black steel fence on
  a low retaining wall** (with a painted mural in 2018, D11). **M** (D11, A14)
- **West**: the 4-storey block w290677064 (e4 faces 93°, 50 m): pale-to-grey ashlar, regular rectangular windows, a
  roof covered with **solar water heaters and tanks** (D13). No shop rows visible (D13 at a distance, D11). **M**
- **al-Disi mosque** on the loop's west side (see 2.6). **East**: the Jewish-Quarter car park 1392375524 behind a low
  wall, with cypresses (D13). **M**
- The `SOUQ_STREETS` entry "Habad" (0.7, 0.1) gives these two ways a shop row; this does not match the photos.

### 1.7 P6: private compound lanes (OSM only, low)
- **Convent lane 290677066** (`foot=private`): its west part (x 110-155) is a **~4-5 m paved lane** between the
  Gulbenkian library (N) and a **garden behind a low wall with an iron railing** (S, the museum's north garden, infill
  f160), cypresses and pines, the red tufa khachkar sculpture at the library corner, and an **arched gateway** at the
  west end onto APR (C18, cam ≈ (151,-338) looking W). East of x 156 it runs between w290677071 (N, a 2-3 storey block
  with an arcaded ground floor? C04 background) and the church garden/pitch. **M** for the west part, **L** east.
- **HaMalakh** (383484416, 290677053, 1056503912): private, gated at the square (n9707887912) and at (222.2,-308.9);
  2-3 m between w290677067 (E) and the pitch's east fence (W). No photo. **L**
- Steps: OSM maps none on either lane. The model has 35 treads on the convent lane (x 169-217, +2.3 → -3.0) and 15 on
  HaMalakh 290677053: plausible for the grades (6-10 %) but unverified.

### 1.8 Open areas (keep them open)
- **Armenian Quarter Residents Parking Lot** (290669001, x 24-104, y -300..-406): a large asphalt car park packed
  with cars, a few trees, bounded by the west and south city walls and the low rubble wall on APR. **H** (E10, E13,
  E01). (This is the "Cows' Garden" plot of the 2023-24 land dispute; no structures to model.)
- **Pitch + tennis court** (290679221, 1545547641): raised terrace, **artificial green turf with white lines** (2017,
  C04; grey asphalt with white lines and basketball hoops in 2012-15, C06, C07, C03), **~4 m steel-mesh fence**,
  floodlight poles. **H**
- **Church garden** (290679223) and the **museum's north garden** (f160 area): trees, cypresses, lawns, railings.
  **M** (C18, C03, B04)
- **Cemetery strip** 157676995: behind the 6-8 m APR wall; only the tree tops show (B01). **M**
- **Park east of Holy Archangels** (290677059) and **Ayyubid ruins / Garden of the Redemption** (r9453421, 290701302,
  290701310): sunken ruins with grass (§2.7). **H**
- **Jewish-Quarter car park** 1392375524. **M** (D13)

---------------------------------------------------------------------------------------------------------------

## 2. LANDMARKS and notable buildings (described only; the gate is modelled by `landmarks_gates.py`)

### 2.1 Zion Gate (w290671706, landmark; see `gates.md` §3)
What this pass adds, seen from the sector side:
- **Inner (east) face e2**: flat-lintel inner door under a relieving arch, two small square windows above (A01,
  A02, A21, A22, B15). In render r1 `A23` the inner door does not read from Zion Gate Street (only a narrow dark slot
  shows); check against A23.
- **West face e0** (faces 291°), which closes the APR wall stretch: plain rubble-faced ashlar of smaller blocks than
  the curtain, **two arrow slits at ~9-10 m, a parapet with two crenel openings**, a single slit lower (A19, B04).
- **The seating pocket** in the angle of e0 and the curtain's inner face (~(186-194, -406..-413)): a **semicircular
  platform of 3 risers (~0.15 m each, ~5 m radius)** with **4 white stone cube posts with ball tops**, two **black tube
  handrails**, two **wooden benches** and a bin, in front of a **pointed-arch niche (~2 m wide, ~3 m high, slit in the
  back)** in the curtain; above it a round-arched opening with an iron grille and the ramparts railing. **H** (A19,
  A11, GZ:14, GZ:17)
- **Harel Brigade memorial** (bronze of two soldiers with a machine gun on sandbags): on the rampart level at the
  gate, in a small paved court with an embrasure and a black plaque, with the **green turf pitch and its fence
  directly behind** (E09). `gates.md` puts it "outside"; E09 places it on the city side of the gate's roof/wall walk.
  **M**
- **External stair to the ramparts** on the curtain's inner face just east of the gate (A23) and the rampart walk
  itself (big irregular flagstones, black railings, steps up to the towers: A20, A28, A15).

### 2.2 Domed church hall by the pitch (w290679226)
Photos: **C03** (2015, from the ramparts/square edge ≈ (222,-410) high, looking NW), **C04** (2017, from a high
point, looking W), **C06**, **C07** (2012, from the court, looking SW), **A02** (zoom, gable end over the pitch wall),
**A28** (from the east, over Zion Gate St).
- A **neoclassical cross-plan hall church**: **E face e4 (22.6 m, onto the pitch) with a projecting central bay under a
  big pediment**, a **large round-arched tympanum with a traceried oculus**, and two tiers of **round-arched windows**
  (5 + 2 + 2 per tier on that face); the **S gable end e2 (17.4 m)** has its own pediment with a smaller rose window
  and a big round arch; lower side bays with flat roofs and small domes; a **central stone dome on a low square drum**
  (~6-7 m across), a second smaller dome. Pilaster strips at the corners, a moulded string course between the tiers.
  **H** (C03, C04, C06, C07)
- **Heights** (above the court, scaled from the window and door heights in C03): cornice **~11-13 m**, pediment apex
  **~16-18 m**, dome top **~18-20 m**. The court itself is ~5-6 m above the road (§5). **M**
- Stone: clean pale cream-to-honey ashlar, warm in sun, a little rust staining at the base. **H**
- Behind it to the N/NW (C04): a long 3-storey block with a ground-floor arcade of round arches and a flat roof
  (w290677071 or w290677057, unverified).

### 2.3 Mardigian Armenian Museum (r3862591)
Photos: C09, C10 (2024, courtyard from the upper gallery), C11 (2023, stair), C12 (plaque), C15, C16 (2009,
entrance).
- A **two-storey quadrangle** (the 1843 seminary) around a long courtyard: **arcades of round/slightly pointed arches on
  both storeys**, an upper gallery with iron railings, external stone stairs with wrought-iron balustrades. The
  courtyard is now **roofed with a pitched steel-and-glass skylight** (2023-24) over a floor mosaic. **H** (C09, C10,
  C11)
- Height ~10-11 m to the roof (two storeys of ~4.5-5 m; C10). The spec's 15 m is too tall. **M**
- **Entrance**: a round-arched doorway with **pale grey steel double doors with black ironwork (crosses, Armenian
  double-headed eagles, pointed panels)**, pilaster strips, a paved forecourt with red-and-white posts and cypresses
  (C15, C16); a **maroon plaque with gold lettering "EDWARD & HELEN MARDIGIAN ARMENIAN MUSEUM"** in Armenian, English,
  Arabic and Hebrew (C12). Which face carries it is not certain: probably the north face e0 on the convent-lane garden
  (C15 courtyard with cypresses), possibly e1 facing the cemetery strip. **L**
- The exterior long faces (e1 W, e3 E, 51 m) are not photographed; they are behind walls and gardens.

### 2.4 Gulbenkian Library (w265410576)
- Two-storey pale ashlar block; **ground-floor rectangular windows with "wheat-ear" iron grilles**, upper
  **round-arched windows**, a downpipe on the south face; **a broad stair of ~5 steps with a large red tufa khachkar
  sculpture (~3 m, carved flames/vines)** at the entrance. **M** (C17, C18; matches `s01_armenian.md` L11's description)
- Position: OSM w265410576 ((128,-327)) and two geotags (C17 (149.5,-328) east of e5; C18 (150.9,-340.2) on the
  convent lane) agree; the entrance stair is probably on the **east face e5 (141.2,-327.4), facing 90°**. The s01 note
  placed the library in a court at (142,-255) from one geotag: that is wrong. **M**
- Height ~9-10 m (two storeys). **M** (C18)

### 2.5 Holy Archangels church (Deir ez-Zeitun, w290677052) and the HaMalakh cluster
- From the ramparts by the gate (E15, 2025, looking NE), the cluster east of the pitch reads as: a **long low hall with
  a low-hipped grey roof, buttressed walls and round-arched windows**, a **small stone bell-cote with an iron cross** at
  its west end (the same bell-cote as the church entrance in C05, which also shows a pointed doorway in a lane
  overgrown with ivy and bougainvillea); around it **2-3 storey cubic houses** with **yellow-brown shutters**, flat
  roofs with railings, **solar water heaters, white water tanks and satellite dishes**, a small red-tile roof, a
  grapevine pergola, cypresses and pines. **M** (E15, C05). Which footprint is the long hall (w290677052, 15.5 m E-W,
  or w290677067 along HaMalakh) is not settled. **L**
- Heights: hall ~7-8 m; houses 7-11 m. The spec's 10-13 m for w290677062/63/67, w1546614907 is at the top of the range.
  **L-M**

### 2.6 al-Disi mosque and minaret (no OSM feature)
Photos: D01 (2014), D10 (2016), D11 (2018), D12 (2013), D13 (2014, elevated).
- A **cylindrical minaret of drafted honey ashlar, Ø ~3 m**, with two narrow slit windows, **one projecting circular
  gallery with a steel railing**, a short upper cylinder under a **round projecting canopy slab**, a **low stone dome
  with a crescent finial**. Gallery ~13-15 m and top ~18-20 m above the road (scaled from the 2.4 m door in D01,
  upward view: **L-M**). **H** for the form (D01, D10, D11, D12)
- The mosque: a single-storey block raised ~1.5 m above the road behind a black fence, a **pointed-arched doorway with
  green steel double doors with diamond panels** in a moulded surround, a small grilled window, an Awqaf plaque "مسجد
  الديسي", house number **92**; **magenta bougainvillea** spilling over the wall; a 3-storey rock-faced house with white
  iron window grilles next to it. **H** (D01, D11)
- Position: the three geotags share one coordinate (308.4,-318.8), a geocode at the Habad/Batei Mahase junction. D11
  and D13 show it on the **west side of the Habad loop at its north bend**, i.e. in the unmapped gap between
  w290677064 (y > -333) and w290677056 (y < -322), which infill f116 fills: **≈ (293-299, -322..-333), front facing
  E onto Habad St**. **L**

### 2.7 Ayyubid tower ruins (r9453421) and the Garden of the Redemption
Photos: D06 (2023, cam (294.3,-376.4), looking SE), D07, D08, D09, D14 (2016), D05 (2009, just east of the sector).
- A **sunken excavation ~3-4 m below the street**: low walls and piers of **large white ashlar blocks (1-2.5 m high)**,
  grass and weeds, a grated shaft, a **concrete ramp and steel stairs with brown railings** down into it, wild petunia
  and shrubs, a pine; the crenellated city wall with a tower (round-arched window) as backdrop. **H** (D06-D09, D14)
- Not a building: the spec's 7 m blocks for r9453421 should be ruins in a ground hole (request).

### 2.8 Dormition Abbey (outside the walls, base context r3925223 / w135470294)
- A round neo-Romanesque basilica with a **conical grey roof and four corner turrets**, and a **tall square bell tower
  with a domed, lantern-topped spire (~45-50 m)**; together with the Cenacle/David's Tomb buildings it fills the sky
  over the south wall from APR (B01), the parking lot (E01, E13) and the ramparts. The base context has a 9 m flat
  block. **H** for the form (E01, E13, A30, B01)

### 2.9 How positions were confirmed

| element | position used | evidence |
|---|---|---|
| Seating pocket W of the gate | angle of w290671706 e0 and the curtain, ≈ (186-194, -406..-413) | A19 (tower face with the pitch fence on the left and the curtain on the right; only possible looking E along APR), B04/B18 (the same face closing the APR wall stretch), A11 geotag (194.3,-409), OSM widening to 17 m at x ≈ 190 |
| Pitch retaining wall on the square | 1056503910 (189.3,-399.7)-(223.0,-403.7) | A06 (wall + fence + HaMalakh gate at its E end), A29 (from the inner door looking E: fence wall on the left, city wall on the right), A02 (fence over the wall right of the gate tower) |
| Church hall | w290679226 | C03 from the square edge looks NW over the pitch wall and court (bearing to w290679226 ≈ 305°); C06/C07 from the court with the city wall to the left; A02 shows its S gable over the pitch fence (bearing ≈ 300° from the square); A28 from the E shows the dome right of the gate tower (≈ 15° right, as OSM predicts) |
| Single-storey row on Zion Gate St | w290677065 e8/e9/e11 | A16/A15 (from the gate's rampart, the whole row in one frame), A13 geotag (250.6,-402.9) at the Yerevan shop, A08 (238,-409), A25/A28 from both ends |
| Gulbenkian Library | w265410576 | C17/C18 geotags (149.5,-328), (150.9,-340.2); C18 shows the convent lane with the arched gate onto APR at its W end, as OSM has it (n9707887913) |
| Ayyubid ruins | r9453421 + park 290701302 | D06 geotag (294.3,-376.4) looking SE with the wall behind; D14 |
| al-Disi mosque | ≈ (293-299, -322..-333) | D11 (on the asphalt loop with red-white kerbs), D13 (minaret at the N end of the long 4-storey block next to the car park); shared geocode (308.4,-318.8). **L** |

---------------------------------------------------------------------------------------------------------------

## 3. GATES of the sector

1. **Zion Gate** (w290671706): the sector's gate, modelled by `landmarks_gates.py` (bent passage, outer face with shell
   niches and bullet scars). From inside, see 2.1. Tiled signs: **"ZION GATE / باب النبي داود / שער ציון"** (white tiles,
   dark green interlace border; A03) and "NABI DAOUD SQUARE" (A02). Plaque and mezuzah in the passage. **H**
2. **HaMalakh gate** n9707887912 (226,-403): pointed-arch doorway with grey steel double doors in the square's north
   wall (A06, A07). **H**
3. **Convent lane gate** n9707887913 (111.4,-339.6): arched gateway from APR into the lane (C18 from inside). **M**
4. **Parking gate** n6905949345 (102.3,-339.5) and the south exit at (114.3,-401.8): openings in the parking wall (no
   photo). **L**
5. Gate n5732626537 (222.2,-308.9) at the north end of HaMalakh (no photo). **L**

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Bollards, posts, railings
- **Black-and-white banded steel bollards** (~1.0 m) along the APR sidewalk and at the mouth of the seating pocket
  (B01, B04, B18). **H**
- **Black steel bollards with a reflective band** (~0.9 m) round Zion Gate Square and along Zion Gate St (A06, A07,
  A16, A19). **H**
- **White stone cube posts with ball tops** on the seating platform (A19, GZ:17); **black tube handrails** there. **H**
- **Steel-mesh fence ~4 m on square posts** along the pitch, with floodlights (A06, A29, C03). **H**
- Black steel fence on a low retaining wall at the al-Disi mosque (D11); brown railings at the Ayyubid ruins (D07). **M**

Lighting
- **Dark grey square lamp posts (~6-7 m) with flat arm luminaires** on the square and Zion Gate St (A06, A16; 2022-24).
  **H**. Old silver poles with lantern heads in 2011 (A25).
- **White glass lanterns on black scroll brackets** at ~5-6 m on the city wall along APR (B04). **H**
- Floodlights on poles over the pitch (A06, C03). **H**

Signs and plaques
- **Ceramic street signs** (white tiles, olive-green border, Hebrew/Arabic/English): "ARMENIAN ORTHODOX PATRIARCHATE
  ST." (A17, on a wall near the square), "ZION GATE ST." (A27), "ZION GATE" (A03), "NABI DAOUD SQUARE" (A02). **H**
- **Blue "P" pay-parking signs with yellow time plates** along the city wall on Zion Gate St (A16, A23). **H**
- Blue one-way and red no-entry discs at the gate (A01, A02, A21, B15); a yellow road sign and a convex mirror at the
  east end (A14). **H**
- Shop sign "BERJ GEJEKOUSHIAN … «YEREVAN»" (A13); hanging textiles and ceramics at the souvenir row (A16). **H**
- Large hanging banners on the gate's inner face in 2024 (B15; temporary). **M**

Bins, benches, others
- Round black/grey slatted bins (A06, A07, A16), wooden slat benches (A06, A16, A19), a white concrete planter (A25,
  2011). Parked cars and taxis on Zion Gate St and APR (A16, A23, B18). A blue ka'ak cart at the gate (A02). **H**

Vegetation
- **Trees over the compound walls**: broadleaf trees, olives, pines and cypresses in the cemetery strip, the museum and
  church gardens (B01, B04, C03, C18; OSM trees n14057425133-43, n14084712123-26). **H**
- **Young street trees in square pits** on the Zion Gate St north sidewalk (A16). **H**
- **Cypress and pine** behind the square (A02, A28) and in the HaMalakh cluster (E15). **H**
- **Bougainvillea** on the al-Disi mosque (D01, D11) and at the Holy Archangels entrance (C05); ivy (C05). **H**
- **Capers (Capparis spinosa)** and golden henbane in the joints of the walls near Zion Gate (G01, G02); small dry
  tufts along the city-wall face (A23, A25). Grass and shrubs in the Ayyubid ruins (D06). **H**

---------------------------------------------------------------------------------------------------------------

## 5. TERRAIN

Street levels from `pipeline/terrain_street.py` (`street_z`, relative to the Jaffa Gate street, 770.58 m asl), with the
OS 1865 spot heights in the sector:

| place | street_z (m) | OS 1865 / evidence | confidence |
|---|---|---|---|
| APR at the tunnel exit (107,-293) | +4.5 | | |
| APR (120.8,-316.9) | +3.6 | spot 2540 ft = 774.2 m (= +3.64) | high |
| APR at the convent-lane junction (108,-339) | +4.1 | | |
| Parking lot centre (64,-353) / NE (100,-305) / SW (36,-400) | +4.3 / +4.7 / +2.6 | spots 774.5 m (34.5,-315.1), 776.3 m (68.3,-298.6), 773.6 m (34.5,-410.5) | high |
| APR at the SW bend (114,-402) | +0.9 | spot 771.4 m (105.8,-406.2) (= +0.93) | high |
| APR wall stretch (172,-408) | -0.4 | | |
| Inside Zion Gate (191.5,-410.9) | -1.0 | spot 769.6 m "zion-inside" | high |
| Zion Gate Square (215,-408) / inner door (210.7,-415.7) | -2.6 / -2.4 | outer threshold: bench mark 769.4 m (201.1,-425.5) = -1.7 | med |
| Zion Gate St (258,-406) / Habad Rd (297,-393) | -6.6 / -7.7 | spots 765.4 m (246.8,-394.0), 764.1 m (254.8,-402.8), 762.3 m (312.7,-389.1) | high |
| Habad loop / Batei Mahase (309,-323) | -9.2 | BM 761.9 m (295.7,-370.8); 762.9 m (289.8,-319.0) | high |
| Holy Archangels (249,-367) / park E (272,-375) | -5.1 / -7.0 | 766.9 m (248.6,-320.3) | med |
| **Pitch** (208,-375) | **-1.5 (model)** vs **~+3 (photos)** | A06/A29: 5.5 m retaining wall from the square (-2.6) to the fence foot; C06/C07: the city wall shows only ~5-6 m above the court | **med** |
| Church hall court (183,-375) | +0.8 (model) | at the pitch level per C03/C06 | low-med |
| Ayyubid ruins (317,-395) | -9.0 (model) | a sunken pit ~3-4 m below the street (D06, D14) | med |

Notes
- **APR falls ~5.5 m over 220 m** (+4.5 → -1.3, ~2.5 %), gently, and the photos agree (B01, B04); no steps. **H**
- **Zion Gate St falls 4.5 m over 80 m** (5.6 %) to Habad Rd; continuous slope, no steps, the sidewalks follow the
  road (A16, A25, A29). The spec's 12-tread run on the north sidewalk 1546610953 (x 233-249) comes from the 7 % rule
  (the sidewalk's own street_z slope is 9-15 %); it is wrong. **H**
- **Raised terraces**: the pitch and the church-hall court sit **~5-6 m above the square and the APR wall stretch**
  behind the retaining wall 1056503910 (A06, A29, C03, C06, C07). The APR south stretch's 6-8 m east wall may also
  retain the cemetery and museum ground, but nothing shows it (L). The al-Disi mosque floor is ~1.5 m above the road
  (D11). The rampart walk is ~10 m above Zion Gate St.
- **Sunken**: the Ayyubid ruins (~3-4 m down, stairs and ramp; D06, D14).
- Other step runs in the spec (OSM steps or the 7 % rule): convent lane 290677066 (35 treads, x 169-217), HaMalakh
  290677053 (15), Ararat (31, at the north edge, x 271-301), footway 290677055 (9), steps 1546610952 (2). No photos.

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **Walls along the roads**: the compound wall 1056503910 (≥6 m on the APR south stretch, ~5-6 m along the city
   wall, 5.5 m retaining wall on the square), 1056503911, the ~3 m dark rubble parking wall on APR's west side
   (x ≈ 104.5, y -340..-400), the west garden walls 1546332724-26. Blind, rubble or pale pointed ashlar, trees over the
   top. (0.1, 1.2, 1.3, 1.4)
2. **Zion Gate Street's north side as a single-storey shop row** (~4.5 m) with a continuous corrugated shed canopy,
   grey steel shutters, souvenir displays; the 3-4 storey rock-faced corner blocks only at the east end. (1.5)
3. **Asphalt roads** with sidewalks: APR ~5 m + 2.5 m east sidewalk with black/white bollards; Zion Gate St 6 m with a
   parking lane along the city wall and a 4-5 m north sidewalk with tree pits. Cars parked along both. (1.2, 1.5)
4. **Zion Gate Square**: honey slabs with the pale-sett turning circle, black bollards, dark grey lamp posts, benches,
   the pitch's retaining wall with the 4 m mesh fence and floodlights, the HaMalakh gate. (1.4)
5. **The raised pitch terrace** (~5-6 m up) with green turf, white lines and the mesh fence. (1.8, 5)
6. **The domed church hall** (w290679226): pediments, oculus, two tiers of arched windows, central stone dome ~18-20
   m, seen from the square, the ramparts and Zion Gate St. (2.2)
7. **The gate tower's west face and the seating pocket**: three-step semicircle, white ball-topped posts, benches,
   pointed niche, closing the APR wall stretch. (2.1, 1.3)
8. **The city wall's inner face** along both roads: crenellations and the grey rampart railing, wall lanterns on APR,
   the diagonal stair and blind arch east of the gate. (1.3, 1.5)
9. **Dormition Abbey and bell tower** over the south wall: the conical roof and the tall domed tower close every
   southward vista. (2.8)
10. **The Armenian residents' parking lot**: a big open asphalt field full of cars inside the SW corner. (1.8)
11. **Mardigian museum quadrangle**: two storeys (~10-11 m), courtyard with glass roof, grey eagle-and-cross doors,
    maroon plaque; Gulbenkian Library with the red khachkar stair on the convent lane. (2.3, 2.4)
12. **Habad corner**: 4-storey rock-faced blocks with roofs of solar heaters, the cylindrical al-Disi minaret with its
    gallery and bougainvillea, red-and-white kerbs, the Jewish-Quarter car park. (1.6, 2.6)
13. **Ayyubid ruins** as a sunken grassy excavation with stairs and railings by the wall corner. (2.7)
14. **Roofscape of the HaMalakh cluster**: 2-3 storey cubic houses, flat roofs with railings, solar heaters, white
    tanks, dishes, a small red-tile roof, the low grey hipped roof and bell-cote of the Holy Archangels hall,
    cypresses and pines. (2.5)
15. **Signage and furniture**: the four ceramic street/gate signs, pay-parking signs, one-way/no-entry discs,
    bins, benches, street trees; vegetation in the wall joints (capers). (4)

---------------------------------------------------------------------------------------------------------------

## 7. Values for the profile/override pass and requests

Building settings suggested by the photos (edge = current spec index, `at` = edge midpoint, faces = outward bearing):

| building | settings | facades | evidence |
|---|---|---|---|
| w290677065 | height ~4.5 (single storey), shops true, wall ashlar (rubble at the W end), tint ~[1.02,0.98,0.92] | e8 "at" [241.6,-403.2] faces 172°, e9 [256.4,-400.6] 164°, e11 [264.2,-396.7] 165°: shop row 2.5-3 m bays, grey steel shutters/doors, awning true (continuous corrugated canopy ~2 m at 2.7 m); e7 [228.9,-401.8] 253° and e6 [227.6,-392.7] 267°: blind rubble with one grey arched door | A16, A15, A25, A28, A13, A08 (H) |
| w1396126810 | height ~13 (4 storeys), wall ashlar (rock-faced), shops false | e0 [276.1,-393.0] 165°: rectangular grilled windows, top floor round-arched with small balconies; e1 [282.3,-387.0] 88°: same, green steel gate | A28, A20 (M; footprint identity M) |
| w290677064 | height ~13 (4 storeys), shops false (or few), roof clutter: many water heaters | e4 [295.2,-358.3] 93°: regular windows, no shop row | D13, D11 (M) |
| w290679226 | height ~12 to the cornice, wall ashlar, tint warm cream ~[1.05,0.99,0.90], arched windows; real form needs a landmark-style builder (request) | e4 [194.5,-377.9] 97°: 2 tiers of round-arched windows, central pedimented bay with oculus; e2 [183.4,-389.0] 182°: gable with rose window | C03, C04, C06, C07 (H) |
| r3862591 | height ~10.5 (2 storeys), wall ashlar, courtyard (request) | e0 [145.5,-346.7] (N): entrance with grey steel doors (L) | C09, C10, C15, C16 (M) |
| w265410576 | height ~9.5 (2 storeys), wall ashlar | e5 [141.2,-327.4] 90°: entrance stair ~5 steps, khachkar; upper round-arched windows, lower windows with wheat-ear grilles | C17, C18 (M) |
| w290677052 | height ~7.5, roof hipped (low, grey), wall ashlar | arched windows, buttresses | E15, C05 (L-M) |

Profile (for the pass): `open_areas` over the pitch + tennis court, the church garden, the museum's north garden
(f160 area), the strip f4 along the convent lane, the pitch edges (f161), the park edges (f159), the JQ-parking edge
(f339) (evidence C18, C04, A06, D13); `souq_streets`: set way 1545832724 and 290677058 ("Habad") to ~[0.1, 0.0]
(D11, D13); keep `Zion Gate Street` as a shop street only on its north side (it is not in SOUQ_STREETS today; the
w290677065 override covers it); `props`: lamp_modern ×2 on the square (~(208,-402), (218,-405)), bench, bin_slatted,
bollards along the square and Zion Gate St, tree_young in pits on the north sidewalk every ~13 m (x 235-285),
wall_lantern on the city wall along APR (x 125-185, every ~10 m).

Requests (need code, terrain or the spec/landmark owners):
- R1 (spec owner): **build OSM `barrier=wall` ways** as free-standing/retaining walls with heights: 1056503910 = 6-7 m
  (x ≈ 111.5, y -339..-399), 5-6 m (APR wall stretch x 116-189), 5.5 m retaining (square, x 189-229); 1056503911 ≈ 5 m;
  1546332724-26 ≈ 3 m; plus a **manual wall** along APR's west side (104.5,-340) → (104.5,-398) → (110,-401), ~3 m,
  dark rubble. Evidence B01, B04, B18, A06, A29, A19. (Fallback for the pass: thin manual_buildings with blank facades.)
- R2 (terrain): a **raised flat for the pitch 290679221 + church court** (polygon = pitch ∪ the S part of park
  290679223, ~x 160-223, y -344..-403) at **street_z ≈ +3.0** (≈ 5.5 m above the square), with the retaining wall on
  its S and W sides. Evidence A06, A29, C03, C06, C07.
- R3 (spec owner): **road surfaces**: APR (26492736) and Zion Gate St (496167694), the Habad loop and Batei Mahase are
  **asphalt** with kerbs; Zion Gate Square honey slabs with a pale-sett ring (~10-12 m radius, centred ≈ (216,-410));
  north sidewalk of Zion Gate St pale slabs 4-5 m; APR east sidewalk 2.5 m. Evidence B01, A16, A25, A06.
- R4 (spec owner): **no steps on footway 1546610953** (Zion Gate St north sidewalk); it follows the road grade.
  Evidence A16, A25; render r1 `A23`.
- R5 (spec owner): keep **r3862591's inner ring** as a courtyard (glass skylight roof at ~10 m, or open). Evidence
  C09, C10, OSM.
- R6 (landmark/spec owner): a **domed church-hall builder for w290679226** (pediments on e4 and e2, oculus, central
  dome Ø 6-7 m to ~18-20 m above the court). Evidence C03, C04, C06, C07, A28.
- R7 (spec owner): **r9453421 as ruins in a ground hole** (sunken ~3.5 m over the main ring x 305-331, y -381..-407,
  walls 1-2.5 m, stairs on the W side). Evidence D06-D09, D14.
- R8 (landmark owner, `landmarks_city`?): an **al-Disi minaret** at ≈ (296,-327) (position L): cylinder Ø 3 m, gallery
  at ~14 m, canopy and dome to ~19 m above the road; mosque block ~5 m with a green arched door facing E. Evidence D01,
  D10, D11, D12, D13.
- R9 (base/context owner): **Dormition Abbey (r3925223) and its bell tower** as a context landmark (conical roof,
  four turrets, ~45-50 m domed bell tower): it dominates the south skyline of this sector. Evidence E01, E13, A30, B01.
- R10 (gate owner, `landmarks_gates.py`): the **seating pocket** at the tower's west face (A19, A11, GZ:14, GZ:17);
  the **external stair and blind arch** on the curtain east of the gate (A23); the **Harel memorial** is on the
  rampart level on the city side, with the pitch fence behind (E09), not outside; the inner door is hard to read in
  render r1 `A23`.
- R11 (s01 owner, FYI): `s01_armenian.md` L11 places the Gulbenkian Library at (142,-255); C17/C18 and OSM put it at
  w265410576 (128,-327) in s02.

---------------------------------------------------------------------------------------------------------------

## Provenance

64 Commons photos in `data/photos_ref/s02_zion/` (1280 px thumbnails; `index.json` has title, page, author, licence,
date, lat/lon and local x/y where the file has coordinates). The most useful: A16/A15/E09/E10/E03/E05 (Israel Preker,
PikiWiki 2022, CC BY 2.5, from the rampart walk over the gate); A06-A08, C09, C10, B05, E13, E15 (שלמה רודד, PikiWiki
2024-25, CC BY 2.5); A19, B15, D06-D09 (Bukvoed 2023-24, CC BY 4.0); B01 (Emmanuel Dyan 2010, CC BY 2.0); B04, A14
(zeevveez 2012, CC BY 2.0); C03 (Ludvig14 2015, CC BY-SA 4.0); C04, D01, D05, A03 (Djampa, CC BY-SA 4.0); C06, C07,
C15, C16 (Deror avi, CC BY-SA 3.0); C17, C18 (Oren Rozen 2024, CC BY-SA 4.0); A25, B18 (Rodrigo Argenton 2011, CC BY-SA
3.0); A23 (Episcopal Diocese of Southern Ohio 2013, CC BY 2.0); A28 (buzzard525, panoramio, CC BY 3.0).
Commons access in this pass was rate-limited (shared IP, HTTP 429 with Retry-After 25-600 s); all requests waited the
Retry-After. Scripts and listings: `build/spec_s02_zion/scripts/` (commons.py, gather_geo.py, cats.py,
fetch1-3.py, widths.py, edges.py, plan.py), `build/spec_s02_zion/geo_candidates.txt`, `cats.json`, `edges.txt`,
`widths.txt`, `terrain.txt`, plans `plan.png`, `plan_w.png`.

Coordinates in `index.json` that are **not** camera positions (do not use them as cameras):
- A19 (288.9,-392.0) and B15 (150.9,-404.0) (Bukvoed TM series, same day): A19 was taken on APR at ≈ (176,-407)
  looking ESE; B15 in the square at ≈ (225,-404) looking WSW. GZ:17 (288.7,-392.9) in the gates set is the same error
  (it shows the seating pocket W of the gate).
- A06 (208.7,-417.7) and A07 (216.4,-417.4): inside the gate tower / on the wall line; both were taken in the square
  looking N/NE.
- C04 (183.5,-371.9): on the church hall itself; the camera was high, east of the pitch.
- A28 (534.5,-121.3): a panoramio misplacement; the camera was on the rampart walk at ≈ (298,-406) looking W.
- D01, D10, D11 (308.4,-318.8): a shared geocode.
- D13 (-8008,-34710): nonsense; the photo is an elevated view from the south-east or south.
- A01/A02 (219.5,-405.7), A13, A08, A11, B01, B04, C17, C18, D06 are consistent with what they show.

Rejected after viewing (moved to `build/spec_s02_zion/rejected/`): A12, D02, B19, B20, E11, E12, E14 (Jaffa Gate /
Citadel, geotags wrong), D04 (Jewish Quarter Cardo), E02 (Kishle, s01), B09-B14, B16, B17 (APR in s01), F01 (Old Yishuv
Court Museum, Jewish Quarter), C01, C02, C08, C13, C14, C19 (interiors, exhibits), B21, B22 (duplicate signs), A05,
A09, A10, E04, E07, E08, G03 (details/duplicates), A18, A24, B02, B06, B07, B23, D03, E06 (low value or unknown place).
