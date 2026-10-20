# s03_christian_w: Christian Quarter west (New Gate, Latin Patriarchate, St Saviour, Greek Patriarchate): visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (lat 31.7766282, lon 35.2275435).
Sector (data/sectors.json): polygon x -170..160, y 48..430, area 91 300 m². It is bounded by the city wall on the
west and north (Jaffa Gate north to the NW corner at (-170,200), New Gate (-128,297), then ENE to (140,420)), by
x = 160 (the west frontage of Christian Quarter St, CQR) on the east, and by y = 48 (the s00 hero area / David St)
on the south. 300 spec records (data/spec/s03_christian_w.json): 237 OSM ways, 12 relations, 51 infill pieces.
Landmarks inside (built by landmark modules, only described here): St Saviour monastery r1515591 and church
w106249447, the Co-Cathedral w1392261827, New Gate w1393450805.
Photos: `data/photos_ref/s03_christian_w/<KEY>_<pageid>.jpg`, cited as **A01**, **D07** and so on. Titles,
authors, licences, dates and GPS are in `index.json` there (80 photos). Photos already downloaded by other passes
are cited by path (`gates/n12`, `landmarks_city/sav_08`, ...). "cam (x,y)" = EXIF/Commons camera position; several
Commons positions are place geocodes, flagged `loc_note` in index.json and in Provenance.
Scale from people (1.7 m), doors (2.2 m), cars (1.45 m high, 4.5 m long) and OSM edge lengths.
Confidence: **H** = seen clearly in 2+ photos, or OSM geometry plus one photo; **M** = one clear photo or a
consistent estimate; **L** = inferred, OSM only, or seen only at an angle.
Edges are spec ring edges (`eN`), with the outward facing bearing and the edge midpoint `at (x,y)` so they can be
used as override anchors directly.

> Status: research pass, 2026-10-20. Renders of the current build from street level are in
> `renders/sectors/s03_christian_w/r1_baseline_abs/` (bje, sf_mid, gop_w). Note: `render_city.py` without `--abs`
> currently finds no ground (the ray cast against `base/ground.glb` misses), so cameras end at absolute z ≈ 1.6
> below the street (r0_baseline is useless; s04's r0 renders show the same). r1 was rendered with `--abs` and
> z = street_z + 1.6 (see Provenance).

---------------------------------------------------------------------------------------------------------------

## 0. Key facts and likely model errors (summary)

1. **The sector falls ~23 m from NW to E.** New Gate / Les Frères / the Collège corner are the highest streets of
   the Old City (+16..+17 m over the Jaffa Gate node), CQR at GOP St is -6, Copts Ascent at CQR -7.
   `terrain_street` matches the 36 OS 1865 spot heights inside the sector (median |residual| 0.13 m, 28 within
   0.3 m, max 1.05 m at two wall bench marks), so the levels are right; the **stairs** that carry this fall
   are St Francis St (43 + 11 steps, ~10 m), Casa Nova Rd (23 steps), GOP St east end and Copts Ascent (~8.5 m
   in 76 m). **H** (OSM, survey, B04, B08, D04, D07, E01)
2. **Bab el-Jadid Rd (New Gate St) is a wide car street, and its east side is a ONE-storey shop row with a long
   red Marseille-tile roof** (eaves ~4.5 m, ridge ~6 m), grey steel shed canopies and dark green round-arched shop
   doors, from the gate (y 297) to y ≈ 232 (w1392271953 + w1392271954, ~65 m). The spec makes these 14.4 m and
   10.5 m flat-roofed blocks (the first with 3 domes and a roof room), so the street reads as a 14 m canyon (render bje). **H**
   (A01, A02, A03, A10, gates/n13, gates/n14)
3. **St Francis St is blocked in the model.** OSM w1393428497 is `building=roof` (13.8 x 3.5 m at x -9..4.5,
   y 233-239): the groin-vaulted passage that carries the street under the St Saviour compound (B01). The spec
   builds it as an 11.7 m solid building across the street (13.3 m of the centreline inside it; render sf_mid
   ends in its wall). Same on St George St: w1394034708 (`building=roof`, 7.1 m) covers 3.2 m of the centreline
   at (96.5,126). Both must become passages (request R2). **H** (OSM, B01, B08, render sf_mid)
4. **Infill slivers hide the real street fronts.** All 51 infill pieces here are 1-4 m wide slivers between the
   OSM footprints and the street corridor (mean width 2A/P = 0.7-5 m), 6.5-9.4 m high, with generic facades.
   They cover, among others, the Greek Orthodox Patriarchate's whole north front on GOP St (w290810608 e0,
   behind f173), the 40 m arcaded front of w1392902286 opposite it (behind f171), the Co-Cathedral's two
   street sides on LPR (f14), Casa Nova (f220/f221) and the St Francis north side (f27). Photos show these facades standing on
   the street, 12-16 m high (render gop_w vs D01). Request R3 (merge narrow slivers into the building they front).
   **H** (spec, D01, D06, D12, B04, C01)
5. **St Saviour's bell tower stands at OSM r21355050 (-12.5,269.3), on the church's east side near its north end,
   not at (-3.6,250.4)** where `landmarks_city.SAV_TOWER` puts it (a Commons object location, ~21 m SE). OSM maps
   the tower explicitly (`man_made=tower, tower:type=bell_tower`, 5.5 x 6 m). A08 (Les Frères St, Commons tag
   (-54.7,217.1), i.e. the centreline at ≈ (-55..-62, 220-224), looking 59° down the straight street) shows the
   tower ~10° LEFT of the street axis: bearing ~49°, against 43-45° for the OSM tower and 62° (right of the axis)
   for the current position. Request R1. **M** (OSM + A08)
6. **Hezekiah's Pool (way 126086870, x 116-163, y 23-99) is a sunken, dry basin**, ~40 x 75 m, floor of gravel
   and weeds (a pond in wet winters, E08), enclosed on all four sides by the BACK walls of 3-5 storey houses that
   rise straight from the pool floor, with box rooms and balconies hanging over it. The floor is ~4-6 m below the
   ground floors around it. In the spec it is only kept free of infill: base.json covers it with ordinary
   `paving` triangles at the street level (-2.1 at (125,60), -3.8 at (140,70), -4.4 at (150,90)), i.e. a flat paved
   plaza in the middle of a block. Request R4 (sunken area, earth/weeds). **H** for the form (E08-E12), **L** for
   the depth.
7. **Institutional palazzi, not vernacular houses, dominate the west half**: the Collège des Frères (w91624550,
   4 storeys ~18 m), the Latin Patriarchate (r3864586, 3 storeys round-arched, courtyards with red-tile pentices),
   Casa Nova (r19228634), the Greek Orthodox Patriarchate (w290810608, smooth ashlar with a rounded NW corner),
   the St Saviour monastery blocks along the north wall (window grids, rooftop railings), Terra Sancta High School
   (w290824723, 3 storeys on pilotis over a basketball court). All have flat roofs with railings and rooftop
   clutter, **no vernacular domes**; the spec gives 8 domes each to w91624550, r3864586, r19228633 and w290818505.
   **H** (A11, C06, C07, F02, F03, F04, F08, sav_08, sav_09)
8. **Red-tile roofs are part of this sector's skyline**: the St Saviour church (hipped, with gabled dormers, OSM
   roof tags), the Co-Cathedral (pitched gables), the Bab el-Jadid shop row, many 2-3 storey houses (hipped,
   A02, F01, F07), and the Latin Patriarchate pentices. Shallow white domes appear on the older houses between
   (A01, A02, F01). **H**
9. **GOP St has a stone arch (sabat) across it at x ≈ 88-95**, with the Patriarchate's gate under it on the south
   side, flags (Greek, Patriarchate) and a hanging lantern (D02, D03, 28848423 not kept). Enclosed timber/metal box
   oriels (mashrabiya) project over the middle stretch (D02, D08, D09). Not in OSM. **M**
10. **Street materials**: cobbled small setts (OSM surface=sett on every named street) with darker bands; rough
    picked rectangular slabs on the stepped lanes; red-white painted stone bollards and square stone bollards;
    cars park on Bab el-Jadid Rd, Latin Patriarchate Rd and GOP St west end (A01, C09-C11, D01). **H**

---------------------------------------------------------------------------------------------------------------

## G. OSM geometry of the core (from data/osm_local.json and data/spec/s03_christian_w.json)

| feature | OSM | position (local m) | notes |
|---|---|---|---|
| New Gate (landmark, gates module) | w1393450805 (gate node n561085431) | (-128.3,296.8) | 8.4 x 3.7 m, layer 1, on wall way 391433919; FORCE_SECTOR s03 |
| Monastery of St Saviour (landmark) | r1515591 | x -40..34, y 235..351, 3618 m² (inner court) | Custodia; north yard = parking 1392902285 (x -57..1, y 295-343) |
| St Saviour church (landmark) | w106249447 | x -23.7..-4.7, y 240.9..286.2 | roof:shape hipped, roof_tiles (OSM); S end on St Francis St |
| St Saviour bell tower | r21355050 (layer 1, man_made tower, bell_tower) | x -15.6..-9.5, y 265.9..272.7, centre (-12.5,269.3) | NOT in the spec (skipped as a part); see 0.5 / R1 |
| Custodia Terrae Sanctae (offices) | w290818507 (layer -1) | x -87..-33, y 269..314, 1224 m² | layer -1, so NOT in the spec; probably the monastery's west blocks seen above ground in sav_08/F03 (L) |
| Monastery north block (on the wall) | w290818505 | x -70..-20, y 318..345, c (-43,332) | spec h 12.4, 8 domes (wrong) |
| Co-Cathedral of the Most Holy Name (landmark) | w1392261827 | x -65..-36, y 104..133 | Latin cross; LPR side e5 at (-40.7,128.5) faces 44° |
| Latin Patriarchate compound | office area way 137726895 (x -156..-29, y 65..197); main block r3864586 | r3864586 x -150..-70, y 107..196, c (-110,154), 2630 m² | 3 storeys; Knights' Palace hotel at its N end, entrance n12921775165 (-112,190) on Les Frères/Jawalida |
| Collège des Frères (De La Salle) | w91624550; school area 290813206 (x -173..-86, y 168..259) | x -162..-111, y 189..248 | spec h 15.2 (photo ~18); yards: pitches 290813204, 1084515000 |
| Casa Nova (Franciscan pilgrims' house) | r19228634; entrance n14067445573 (-3,185.5) | x -46..15, y 151..193 | spec h 13.0 |
| Greek Orthodox Patriarchate | w290810608 | x 27..87, y 94..183, 1956 m² | rounded NW corner at (27,160-167); courtyard garden 1390876172; spec h 12.2 |
| Gloria Hotel / "former Greek Patriarchate Hospital" | multipolygon 290812330 (x -14..39, y 50..104); block r19228633 (building=hotel) | r19228633 c (13,77), 1406 m² | 4 storeys (C12); spec h 12.8 with 8 domes (wrong) |
| Greek Catholic (Melkite) Patriarchate + Annunciation cathedral | w290810613, w1394461451 | x 45..89, y 62..93 | cathedral bell gable seen from St Dimitri (D15) |
| St Panteleimon monastery / St Dimitri school | nodes n4308698494 (30.9,114.8), n5835948786 (47.8,116.8); school area 1546570915 | x 31..87, y 91..159 | garden 1392275778 (x 15-43, y 86-123) |
| Holy Archangels (Serbian) church / Archangels monastery | w1392256448 | x 56..75, y 256..277 | north side of St Francis St |
| Terra Sancta High School | w290824723; area 488482585; pitch 290824729 | c (106,391) | under the north wall; F04 |
| Hezekiah's Pool | way 126086870 (water=basin, intermittent, surface gravel, historic=archaeological_site); meadow 1549495722 | x 116.4..162.8, y 23.5..98.6, 2003 m² in sector | sunken basin, see 2.6 |
| Tancred's Tower remains | n11076108410 | (-153.0,225.5) | NW corner, ruins in grass (F06) |
| Agioi Theodoroi (Greek chapel) | n13587995701 | (-11.0,196.3) | on Casa Nova Rd |
| Megali Panagia monastery | n4296490589 | (134.1,134.3) | on Copts Ascent |
| Mosque Al-Huda (outside the polygon) | w298277800 | (-150,288) | W of New Gate, not in this spec |

Streets (OSM centrelines, all surface=sett unless stated):
- **Bab El-Jadid Road (New Gate St)** living_street 26491282: (-127,294) → (-126,290) → (-123,273) → (-117,254) →
  (-113,247) → (-107,239) → (-83,207). Service 26491284 (-127,294) → (-96,311) runs along the inside of the wall to
  the St Saviour north yard (gate n2943338898 (-95.7,310.8)). Lift gates n6915140442 (-126.6,292.2) and
  n6920771030 (-117,298.9) just inside the gate.
- **Les Frères St** 26491283 (-83,207) → (-110,192) and 26491279 (-20,219) → (-46,229) → (-83,207) (named
  "סנט פרנציס" in Hebrew on the second piece).
- **El-Jawalida Rd** living_street 1546559596 (-110,192) → (-75,162); **St Peter St** 26491281 (-38,147) →
  (-49,165) → (-75,162).
- **Latin Patriarchate Rd** 26491278 (48,0) → (12,44) → (-20,70) → (-49,94), then 1548979887 (-49,94) → (-28,120) →
  (-31,124) and 1548979886 (-31,124) → (-47,139) → (-38,147).
- **Tanners** footway 290812020 (19,167) → (-17,152) → (-38,147).
- **Casa Nova Rd** steps 26492709 (19,167) → (2,194) → (-1,196) (23 steps, handrail, lit), then 1005635986 (-1,196) →
  (-20,219).
- **St Francis St** steps 1005635988 (-12,234) → (-14,223) → (-20,219) (11 steps, ramp), steps 1005635990 (108,256) →
  (46,246) → (12,239) → (-12,234) (43 steps, ramp, handrail, lit; incline up = westwards), steps 26492707 (159,261) →
  (108,256) (east end, from CQR).
- **Greek Orthodox Patriarchate St** pedestrian 26492708: (160,221) → (127,209) → (102,199) → (22,168) → (19,167).
- **St Dimitri's Rd** 78325491 (39,83) → (45,93) → (35,123) → (28,148) → (19,167).
- **Greek Catholic Patriarchate St** 26492711 (69,7) → (65,24) → (60,52) → (42,73) → (39,83) (in s00 south of y 48).
- **St George St** 229846305 (60,52) → (83,72) → (90,83) → (97,131) → (98,134).
- **Copts Ascent (Suq Al-Aqbat / Aqabat Khan el-Aqbat)** steps 229756029 (98,134) → (121,136) → (123,129) → (168,133).
- **Ar-Rusul (Apostles St)** 617363476 (3 steps) + 1005635989 (108,262) → (114,299) → (124,320) → (161,336) → east (s04).
- North block lanes: unnamed footways 26491291, 257617650-79, 1394034697-99 (x 23-130, y 280-380); footway
  617363469 runs along the monastery garden's east side (x 41-46, y 246-300) and on to the north wall.
- Passages with layer -1 (ignored by covered_ways, mostly private): 257617656 (12,239) → (15,214) from St Francis to
  the GOP garden; 738489021 (-73,244) → (-46,229) under the monastery; 1395896903 (service, the Latin Patriarchate
  gate C02 at (-53.3,97.7)); 257617651 (127,209) → (126,215) north off GOP St.

Wall-to-wall widths (perpendicular rays every 8 m to the spec footprints, `build/spec_s03_christian_w/widths.py`;
"no infill" = the same without the f-pieces):

| street | with infill (as built) | no infill (OSM footprints only) | photos |
|---|---|---|---|
| Bab el-Jadid Rd y 210-250 | 4.7-6.0 m | same | A01: ~8-9 m incl. a parking lane |
| Bab el-Jadid Rd y 255-292 | 8.4-16.8 m (inner gate square) | same | A01, A04, gates/n13 |
| Les Frères St (26491279) | 4.1-4.9 m | 4.5-6.7 m | A08: ~4.5-5 m |
| Les Frères (26491283) by the Collège | 6.3-6.4 m | same | A06 |
| El-Jawalida Rd | 3.2-3.6 m, 15-17 m by the park 290812021 | same | C14 |
| St Peter St | 4.1-4.2 m | same | C13 |
| Latin Patriarchate Rd S (x -10..9) | 6.5 m | same | C10, C11: ~5-6 m incl. parked cars |
| LPR by the Co-Cathedral (1548979886) | 3.7-4.1 m | 4.8-15 m | C01: ~5 m |
| Tanners | 2.7-2.8 m | 3.5-4.2 m (26 m at x -5) | — |
| Casa Nova Rd | 2.3-2.9 m | — | B11, 157342670: ~2.5-3 m |
| St Francis St x 12-74 | 3.0-3.3 m | 3.6-17 m | B04: ~4 m; B09: ~3 m |
| St Francis St x 80-106 | 18-50 m (gardens on both sides) | same | B06: ~4 m between garden walls |
| St Francis St x 110-157 (to CQR) | 3.4-3.5 m | — | B05 |
| GOP St x 24-106 | 4.2-4.3 m | 7.3-7.6 m (x 24-69), 6-12 m (x 76-121) | D01: ~5-6 m at the W end; D02: ~3.5 m at x ≈ 75 |
| GOP St x 121-158 | 3.4-4.3 m | 5.2 m | D04, D07: ~4 m |
| St Dimitri x 129-160 | 3.5-4.2 m | 4.4-6.5 m | D10-D12: ~5-6 m |
| St Dimitri y 92-122 | 12-30 m (garden + open court) | same | D14 |
| St George St | 2.2-3.3 m | — | E01, E05: ~2.5-3 m |
| Copts Ascent | 2.4-2.9 m | — | E07 |
| Ar-Rusul | 2.0-4.3 m | — | — |

Open areas mapped in OSM (kept free of infill by `infill.OPEN_TAGS`): parks 290812021 (Jawalida), 290818503 (south
of St Francis x 47-119, y 207-252, the GOP garden), 290818512 (monastery garden x 15-44, y 279-346), 290824732;
gardens 1390876172 (GOP courtyard), 1390978749 and 1392275775/76 (Latin Patriarchate), 1392275778 (St Dimitri
school), 290824743 (north of St Francis x 67-106, y 253-285), 1392257367, 1549774037 (St Saviour cloister),
1394864927; parking 1392275777 (LPR, x -20..3, y 71-96), 1392731552, 1392902285 (St Saviour north yard),
1549771270, 290818508 (inside New Gate); pitches 290813204, 1084515000 (Collège), 290824729 (Terra Sancta);
meadow 1549495722 and basin 126086870 (Hezekiah's Pool).

Mapped walls (barrier=wall, not built by the spec today): 1396048476 (4 m stone, (-124,261) → (-108,234), the
Collège boundary on Bab el-Jadid Rd), 1396050324-26 (Jawalida park), 1549774036 ((-30,231) → (-15,231), Les Frères
S side), 1549203673 (LPR), 1393938074 ((45,86) → (68,63), GCP St), 1005635993 (Casa Nova).

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and STREET PROFILES

### 1.0 Character
The Christian Quarter's institutional half. Three worlds:
(a) **the NW plateau** (New Gate, Les Frères, the Latin Patriarchate): the highest and newest part of the Old City,
built after 1860 by the Catholic orders: big pale-ashlar palazzi of 3-4 storeys with regular window grids, string
courses and cornices, flat roofs with railings, red-tile pentices and church gables, palms and cypresses in walled
gardens, a car street from New Gate with parking;
(b) **the monastic stepped lanes** that fall east from the plateau to the souq (St Francis St, Casa Nova Rd, GOP St,
St Dimitri, St George, Copts Ascent): narrow, stepped or ramped, between high blank walls of rough stone with few
doors, vaults and arches over the street, box oriels, lanterns, handrails, pennant strings, and a few souvenir and
grocery shops near the bottom ends;
(c) **the dense residential block** north of St Francis St (Ar-Rusul and its lanes, x 40-160, y 255-430): 2-4 storey
houses with domes, rooftop rooms and red-tile hipped roofs, seen only from the ramparts (A02, F01).
Stone: cream to honey limestone, smooth dressed ashlar on the 19th-century institutions (Collège, Latin
Patriarchate, Casa Nova, GOP Patriarchate) and rough rubble or rock-faced blocks on the older houses and lane walls;
some warm orange-honey ashlar (St Francis north side, B04). Few shops: the quarter is closed and quiet.

### 1.1 Profile table

| profile | OSM streets | key look |
|---|---|---|
| P1 gate street | Bab El-Jadid Road (26491282) + service 26491284 inside New Gate | 8-17 m wide, cars, one-storey red-tile shop row (E side), arcaded shops (W side near the gate), institutional blocks further S, square stone bollards |
| P2 institutional street | Latin Patriarchate Road (all three ways), Les Frères Street, St Peter Street, El-Jawalida Rd, Greek Catholic Patriarchate Street, St Dimitri's Road | 4-6 m, 3-4 storey smooth ashlar facades with tall windows, iron gates, few shopfronts (blue/green steel doors), parked cars on LPR |
| P3 monastic stepped lane | Saint Francis Street (upper, x -20..74), Casa Nova Road, Greek Orthodox Patriarchate Street (x 24-121), Tanners, Saint George Street, Suq Al-Aqbat (Copts Ascent), Ar-Rusul | 2.5-4.5 m, steps/ramps, high blank rubble walls, vaults and arches, box oriels, lanterns, handrails |
| P4 lower souvenir lane | St Francis St x 106-160 (26492707), GOP St x 121-160, Copts Ascent at CQR, LPR south end (x 9-48) | shops on one or both sides, green steel canopies on hoop brackets, hanging textiles, teal/blue doors |
| P5 sunken basin | Hezekiah's Pool (126086870) | dry floor 4-6 m down, back walls of houses on all sides |

SOUQ_STREETS today: Latin Patriarchate Road (0.25, 0.2), Greek Orthodox Patriarchate Street (0.3, 0.2), Christian
Quarter Street (0.9, 0.35). Suggested (profile, next pass): Latin Patriarchate Road ~0.3 / 0.15 (shops only at the
south end and as arched blue-door rooms, C10, C11); GOP St 0.25 / 0.4 but **only x 121-160** (north side, D04, D05,
D07; the west half is blank Patriarchate walls); way 26492707 (St Francis lower) 0.7 / 0.6 (B05); way 26491282 (Bab
el-Jadid) 0.6 / 0.8 (A01-A04: shop rows with canopies on both sides near the gate).

### 1.2 P1: Bab el-Jadid Rd (New Gate St), from New Gate (y 297) to Les Frères (y 207)
Photos: A01 (2009, from the top of New Gate looking SSE), A02, A03 (2019, from the ramparts), A04 (2019, night,
cam (-135.7,281.5) looking SE), A10 (2011, from Notre Dame), gates/n13, gates/n14, gates/n12, A05 (gate inner face).
- **Width and use**: a car street. At y 255-292 it opens into an inner gate square 8-17 m wide (parking 290818508
  just west, lift gates at the gate); at y 210-250 it is 5-6 m with a parking lane along the west side (A01, n13).
  **H**
- **Paving**: small grey setts (OSM sett), a darker diagonal band of larger stones in the square (A01), concrete
  kerb strips. **H**
- **East side, y 232-297: one-storey shop row** (w1392271953 e0 (-121.2,280.0) 22.9 m faces 256 and e9 (-118.5,296.5)
  faces 335 to the gate square; w1392271954 e8 (-116.7,264.1), e0 (-112.7,254.5), e1 (-104.6,240.7) 21.4 m, faces
  236-250): **H** (A01, A02, A03, A10)
  - ~12-14 shops; round-arched openings ~2.4 m wide x ~3.0 m in ashlar piers ~0.6 m; **dark green panelled steel
    doors** in 2019 (A02), in 2009 also red-and-yellow panelled leaves, brown and green steel (A01).
  - stone threshold steps 0.15-0.3 m; square stone bollards (~0.4 x 0.4 x 0.5 m) and red-white striped steel posts
    along the kerb, ~3 m apart (A01).
  - **shed canopies** of corrugated or slatted grey steel with a scalloped valance, ~1.2-1.5 m deep at ~2.9-3.2 m
    (A01, A02); some brown sheet.
  - **roof: one long pent/hipped roof of red Marseille tiles** running the whole row (A02 2019; in 2009 the north
    half was grey-coated, A01), eaves ~4.3-4.8 m above the street, ridge ~6-6.5 m, tile overhang ~0.4 m. The row is
    ~9 m deep (272 m² / 30 m). Behind it rise 2-3 storey houses with white domes and red-tile hipped roofs.
  - spec now: w1392271953 14.4 m flat, 3 domes, 1 roof room; w1392271954 10.5 m flat. Both should be ~4.5 m with
    `roof: hipped`, `shops: true`, `domes: 0`, `wall: ashlar`.
- **West side near the gate (y 256-292)**: w1396048477 e2 (-126.5,266.8) 12.3 m faces 71 and w290813203 e1
  (-130.0,274.9) faces 56: an **arcade of tall round-arched shops** (~2.5 x 3.5 m openings with iron fan grilles in
  the arch heads, green and brown panelled doors) under a continuous green steel and glass canopy, raised on a
  platform reached by **3 steps** (A04); a 3-storey block with an arcaded ground floor and a shop fascia (A01 right
  edge). 2 storeys ~8-9 m. **M** (A04 at night, A01 edge)
- **West side y 210-250**: the Collège des Frères precinct: the 4 m stone boundary wall 1396048476 ((-124,261) →
  (-108,234)), then the Collège buildings and the Al-Hayat centre with a 3-storey ashlar facade (A04; 23764894,
  not kept, shows its Christmas tree "in front of the Collège des Frères"). **M**
- **East side y 210-232**: w1392271952 e7 (-89.6,219.7) 21.4 m faces 236, 13.2 m in the spec. A12 shows a
  3-storey corner of the Les Frères junction in large rough-dressed ashlar with a tall round-arched grilled window
  and the ceramic signs "BAB EL-JADID RD" / "FRERES ST." (which of the junction corners is not certain). **M/L**
- **South end**: the street ends at the Les Frères junction against w290813202 e7 (-98.2,222.5) 31.7 m faces 52 (3
  storeys, 11.1 m in spec; "Christmas tree" building of A04 is at the end of the view). **M**
- Christmas: big Christmas tree and ball lights across the street in December (A04). Out of season: none.

### 1.3 P2: Les Frères St, El-Jawalida Rd, St Peter St (the NW plateau lanes)
Photos: A06, A07, A08, A12, C13, C14.
- **Les Frères St (26491279)**, x -83..-20, falls 15.6 → 10.6 m eastwards (terrain); 4.5-5 m wide. North side:
  w1390876171 e2 (-70.1,211.8) 22.9 m faces 329, w1393168509 e3-e7 (x -54..-28) faces 339-17; south side f23
  (infill sliver, 41.5 m, 8.2 m high) in front of r3864606 and w1392276716. A08 (looking ENE): left (north)
  3-storey rubble/ashlar houses with an **enclosed white aluminium box balcony** on a concrete bracket at ~5 m,
  grilled windows, a satellite dish; right (south) a café with two **beige scalloped fabric awnings** and blade
  signs ("Arab Orthodox Society", "Fair Trade Women Cooperative"); at the bend (x ≈ -40) the 3-storey block
  w1393168509; the St Saviour tower rises over it. Paving small setts. **H** (A08)
- **Les Frères St (26491283)** x -110..-83, 6.3-6.4 m, level (~16 m): north side w290813202 e6 (-94.7,205.8)
  15.2 m faces 146 and small infill; south side w290812017 e5 (-93.7,197.1) 26.1 m faces 332 (13.5 m, between Les
  Frères and Jawalida). At its west end (-110,192) the street meets the Collège yard (pitch 1084515000) and the
  Knights' Palace entrance. A06 (cam ≈ (-100,202), looking W) is the Collège's SE-facing front (w91624550 e2-e8,
  faces 128): 3 storeys + attic, a central niche with a statue under a carved crest, a flagpole with the Vatican
  flag, a wrought-iron cross on a balcony railing in front. **M**
- **El-Jawalida Rd** (-110,192) → (-75,162): Knights' Palace entrance (A07: segmental door with "KNIGHTS' PALACE /
  LATIN PATRIARCHATE" sign in three scripts, two black wall lanterns, house no. 237, arched grilled window,
  potted shrubs, a red-tile canopy) at n12921775165 (-112,190), r3864586 e17 (-114.9,192.3) faces 40. Further SE the
  street runs past park 290812021 behind a rubble wall topped by cactus and palms (C14: ceramic sign
  "AL-JAWALIDA ST."). **M**
- **St Peter St**: 4 m, quiet, potted plants, smooth ashlar walls, Santa's House door (red, at w1392731549, C13
  and 94933174 not kept). **M**

### 1.4 P2: Latin Patriarchate Rd (from the Jaffa Gate side up to the Co-Cathedral)
Photos: C01-C04, C09-C12, and data/photos/073-076 (Terra Sancta girls' school, s00).
- **South part (x 48 → -20, y 0 → 70)**: 5-6.5 m; it **climbs** NW from 0.6 m (x 44) to 5.9 m (x -23) and
  7.1 m at (-47,93), then 12 m at St Peter St. Cars park along one side (C10, C11, C09 at night); a disabled
  parking bay. Shopfronts: round-arched openings with **blue** panelled steel doors (C11 "OPEN" sign) and green
  doors; 2-3 storeys of mixed ashlar. North side (w290812409 e3 (-5.7,55.2) 37.2 m faces 38; w1396104569,
  w1396104568) and south side (r19228633 e2 (-0.9,59.8) 32.3 m faces 218, the Gloria). **H**
- **Gloria / former Greek hospital (r19228633)**: a 4-storey (ground + 3) pale ashlar block, flat roof with a
  railing, fire-escape stairs and red pipes on the facade, cypresses, iron-fenced front garden, parking forecourt
  (C12, 151742637 not kept). Spec h 12.8 → ~15 m + railing, `domes: 0`. **M**
- The 28 m "gap" at (-23..-16, 67-72) is parking 1392275777 (x -20..3, y 71-96). **H** (OSM, C12)
- **Middle (x -20..-49)**: Greek consulate (n10115810142 (-39,94.7), Greek flag seen through the Patriarchate gate
  in C02), Rosary Sisters (n14088515598), Tala restaurant; the **Latin Patriarchate gate** at n12920645469
  (-53.3,97.7): a pointed arch with an ornate **wrought-iron Gothic tracery tympanum** and black iron gate leaves
  over a vaulted entrance (C02). **M**
- **North part (1548979887/1548979886, y 94-147)**: along the Co-Cathedral and the Patriarchate offices. C01: a long
  **smooth pale ashlar wall** with a pointed-arch gate (iron gate), a row of narrow **lancet windows** high up, a
  gable with pinnacles at the far end, small square stone bollards along the foot (that is the Co-Cathedral
  w1392261827 e5 (-40.7,128.5) faces 44, which the infill sliver f14 hides today). C03 at the St Peter junction
  (-38,147): rough rubble wall left, smooth 4-storey ashlar of w290812335 behind, a honey-stone gabled hall with a
  metal-roofed gable and a grilled arched window, the Co-Cathedral bell tower with the Vatican flag, a balcony with
  colonnette balustrade on the right; ceramic sign "LATIN PATRIARCHATE RD.". w290812335 e6/e7 (-38.7,144)/(-40.7,135.4)
  faces 325/225, 16 m. **H** (C01, C03, C04)

### 1.5 P3: Casa Nova Rd and Tanners
Photos: B10, B11, D11, 157342670 and 39497237 (not kept: children on the steps; night view through the arch).
- **Casa Nova Rd steps (26492709)** climb 23 steps from the Dimitri/GOP junction (19,167) NW to (-1,196): 2.3-2.9 m
  between Casa Nova (r19228634 e11 (8.7,180.5) 28.7 m faces 62) and w1393928794 (e5 (12.9,178.4) faces 244). The
  foot of the stair is under an **arch** at about (17,169) next to the "Old City Clinic" (B11: arch, steps rising
  under it, green door, clinic sign; D11 shows the stair going up left of the Samara building). Steps of rough
  limestone with ~0.15 m risers, walls of rock-faced rubble. **M** (B11, D11, 157342670)
- Casa Nova entrance: n14067445573 (-3,185.5), on the stair's upper part: a 2-storey ashlar frontispiece with a
  round-arched window over a rectangular door, two wall lanterns, the "CASA NOVA" sign, 3 steps (B10). **H**
- Upper part 1005635986 (-1,196) → (-20,219): 2.3-2.9 m, chapel Agioi Theodoroi (n13587995701), souvenir shops
  (St Joseph, Santa Maria) toward St Francis. **L**
- **Tanners** (290812020): a 2.8 m footway between Casa Nova (r19228634 e2 (-28.2,153.3) and e10 (6.7,164.3), faces
  158-164) and w290812335 / w290812334; it climbs 6.9 → 12.3 m in 50 m (stairs.py makes steps). No photo. **L**

### 1.6 P3/P4: St Francis St (St Saviour → CQR)
Photos: B01-B09, B14, sav_03 (landmarks_city), A08 for the tower.
- **Course**: from the Casa Nova junction (-20,219) up 11 steps to (-12,234) [segment 1005635988], then the main run
  falls east 122 m to Ar-Rusul (108,256) [43 steps with ramps], then 52 m down to CQR (159,261) [26492707]. **H** (OSM)
- **The vault (x -9..4.5)**: the street passes under the St Saviour compound in a **groin-vaulted tunnel** ~3 m wide,
  ~4-4.5 m to the crown, ~14 m long (OSM w1393428497, building=roof; B01, cam ≈ (-11,236) looking E out of it).
  Vatican yellow-white and Jerusalem-cross pennant strings hang inside; a house-number plate at ~2 m; dark worn setts.
  B02 shows a **yellow-plastered groin bay with a large red Jerusalem cross painted on the soffit**, probably the
  east portal bay of the same vault (its Commons tag is 25 m E). B08 (IMG 9654) shows a vault end with a short
  flight of 4 steps up to a grey door. **H** for the vault, **M** for B02's position.
- **Upper run x -12..46** (z 8.9 → 4.0): 3.0-3.2 m between the Custodia/St Saviour buildings: the parish office
  door (B03: "OFFICIUM PAROECIAE LATINAE JERUSALEM / CUSTODIA TERRAE SANCTAE", segmental arch, rusticated quoined
  frame, dark doors with red crosses, house no. 5; Commons tag (32,240.3), i.e. south side x ≈ 30-35), the
  "Terra Sancta" compound gates with a stained-glass Jerusalem-cross fanlight (52911358, not kept) and Monastery of
  St George of the Hospital (Greek inscription and a St George relief over a door, 52911354, not kept, (10,241)).
  Walls: pale smooth ashlar with tall round-arched windows (B09, B14). Steps: broad low risers (~0.12-0.15 m) with
  long sloping treads and a **ramp strip** for carts; central or side **handrail** (OSM handrail=yes). **H**
- **Middle x 46-80** (z 4.0 → 0.5): B04 (cam (61,247.8) looking E, Khanqah minaret on the axis): **north side** a big
  institutional building of **warm orange-honey ashlar** with a moulded string course at ~3.5 m, tall round-arched windows (~1.2 x 3 m) above it, octagonal-headed basement windows
  with mesh grilles below it, sunk behind a **grey ornamental steel railing** (circle pattern, ~1.1 m) that guards a
  ~1 m wide light well; beyond, a 5-storey white ashlar block with a Jerusalem-cross banner and a Vatican banner
  (the Custodia girls' orphanage, per B07's caption).
  These are w1392256447 e2 (54.8,249.2) 13.5 m faces 168 and w1392256449 e1 (76,253.3), behind the infill sliver
  f27 (e5 (63.0,250.1) 31.9 m, 8.2 m high) today; the photo shows ≥ 3 storeys, ~12-14 m. **South side**: 2-3 storey
  honey rubble houses with shops, green steel canopies and flower pots. Paving: rough-picked slabs, ramped, no steps
  in this stretch. Width ~4 m. **H** (B04, B07)
- **x 80-106**: between two walled gardens (290824743 N, 290818503 S): high rubble walls with greenery spilling over,
  a bench (n9278423956 (89.9,251.2)), Vatican pennants across (B06, 2022, looking E). In the spec the gardens are open
  ground with no wall (request R6). **M**
- **Lower run x 106-159 (26492707)**, P4: 3.4-3.5 m, souvenir shops on both sides (B05: green and dark steel canopies
  on hoop brackets, display racks of icons and rosaries, blue shutters, a pointed arch across the street further
  down; men sitting on the shop platforms; round cast-iron manhole). 23765750 (not kept) shows a Christmas-decoration
  shop at the Ar-Rusul corner (108,257). **H** (B05, B06)
- Signs: **pink/red metal plates with Bible verses** on the walls (sav_03, Commons "St. FRANCIS Street biblical
  verse"), ceramic street sign "ST. FRANCIS ST." (Commons, not downloaded). **M**

### 1.7 P3/P4: Greek Orthodox Patriarchate St (GOP St)
Photos: D01-D09, D16, G01, 28848423 (night arch, not kept).
- **Profile**: falls east from 6.1 m (x 22) to -6.0 m (x 158), 12 m in 140 m: level/ramped in the west half, stepped
  in the east half (broad low steps with long treads and a **central ramp strip "to accommodate carts"**, D04, D07).
  **H**
- **West end (x 19-70)**, D01 (cam ≈ (21,167) looking ENE): north side w1392902286 e0 (44.1,180.5) 39.9 m faces 158:
  2 storeys, ~10 m, a ground floor of shops (Maria's Groceries n7121620585 (39.6,182.2), Jerusalem Pottery
  n7121620385 (31.4,177)) with green steel canopies and blade signs, an **upper floor with a row of ~12-14 small
  round-arched windows** at even spacing (~2.8 m), satellite dishes on the parapet. South side: the **Greek Orthodox
  Patriarchate's rounded NW corner** (smooth honey ashlar, quarter-cylinder, 3 storeys) then its north front e0
  (49.8,174.8) 43.2 m faces 339. Car parked. Today both fronts are hidden by the infill slivers f171 / f173. **H**
  (D01, D06, D10, D12)
- D06: north-side shopfronts in pale smooth ashlar with dressed frames: a segmental-arched opening with a **dark
  green panelled steel door** (John Paul II Foundation), a **blue** steel door, a carved timber door, a green steel
  canopy on brackets at ~3 m. **H**
- **Middle (x 70-121)**, D02 (2025, cam ≈ (71,190) looking E), D09, D08: 3-4 m between high blank walls of rough
  rock-faced stone; **enclosed box oriels** (timber or grey-painted metal lattice, ~1.5 m wide, 0.8 m deep) project
  at ~5-8 m, stacked two high on the north side; wall lanterns on brackets; a steel **handrail** along the south wall;
  an **arch (sabat) across the street at x ≈ 88-95** carrying the Patriarch's residence (round plaque and tall
  round-arched window above the arch); the Patriarchate gate (pointed doorway, Greek flag, red-white Patriarchate
  flag, hanging lantern) is under the arch on the south side (D03 "entry to the patriarchate compound south of the
  street, under this arch"). Coats of arms of the Patriarchate (gilt bronze relief) over doors (16329041, not kept),
  "MUSEUM OF THE GREEK ORTHODOX PATRIARCHATE" stone plaque (16328905, not kept). r3864607 e13 (75.1,191.5) and e19
  (91.9,200.5) face 162-163 on the north side. **M** (arch position from D02 + D03)
- **East end (x 121-160)**, P4: D04, D07 (2025, cam (154.8,229.1) looking W uphill), D05: south side a **high blank
  wall** with small grilled windows, a blue steel cabinet, green bins, a yellow mailbox (old British Mandate post box,
  33428720 not kept, at the junction); north side shops with **dark brown/black steel shutters** and **corrugated
  grey canopies on curved hoop brackets** (w1392903889 e2 (153.6,215.8), w1392903892, w1392903893, w1393980122/24);
  at the CQR corner textile shops with hanging carpets and clothes (D05). **H**
- Signs: ceramic street sign "GREEK ORTHODOX PATRIARCHATE RD." (white tiles, D16), ceramic "CHRISTIAN QUARTER ST."
  at the corner pier (G01). **H**

### 1.8 P2: St Dimitri's Rd
Photos: D10-D15, 34790833 (not kept).
- (39,83) → (19,167), climbs 4.0 → 6.2 m. Two parts: **south (y 83-122)**: an open court/forecourt 12-30 m wide with
  a parking space (n14066208841 (40.6,101.8)), the St Dimitri school's arcaded loggia with a fenced garden and big
  trees (D14), the Melkite patriarchate doors (E03, 9405246) and an ornate neo-Renaissance portal with columns,
  carved crest and urn balustrade (D13, at ~(35,108)). **North (y 129-167)**: 4.4-6.5 m between w290812334 (W) and
  the Greek Orthodox Patriarchate (E, e10 (38.6,126.8) 69.7 m faces 250, **smooth honey ashlar, 3 storeys ~13-14 m,
  string courses, tall rectangular windows with iron grilles on the ground floor and grey timber shutters above,
  black steel bollards** (D12, D10)). At the top: the Samara travel agency building (w1393928794, e0 (21.4,170.4)
  faces 154): 2 storeys of honey rubble with round-arched grilled windows and a **triangular-patterned pierced
  parapet**, a white plastered dome behind it, the St Saviour tower beyond (D10, D11). **H**
- D15: the Melkite Annunciation cathedral's small **bell gable** with a cross, seen over a 3-storey facade with
  wrought-iron balconies. **M**
- Doors: "Armenian-colour" painted doors (red-blue-orange) at ~(31,144) (34790833). **M**

### 1.9 P2/P3: Greek Catholic Patriarchate St, St George St, Copts Ascent
Photos: E01-E07, data/photos/073-076 (s00 side).
- **GCP St** (in s03 for y > 48): 3.8-4.6 m, pale ashlar, a small square at ~(45,70) with **red-white painted stone
  bollards**, pennants and a Jerusalem-cross flag (E04); the **Versavee passage** where the street runs through a
  house: a covered timber-lattice gateway (E02, cam (42.1,74.9)); Melkite patriarchate gate: grey steel double door in
  a rusticated segmental frame with a crest (E03). **M**
- **St George St** (60,52) → (98,134): 2.2-3.3 m, **steep steps** of rough stone at the GCP corner (E01: 5-6 risers
  of ~0.18 m, a red-white bollard, a green wheelie bin, grey steel doors, a corrugated canopy), then a quiet lane
  between high plain walls (E05), the Coptic patriarchate entrance and St George's (Coptic) church (not downloaded).
  OSM building=roof w1394034708 over it at (96.5,126) (see 0.3). **M**
- **Copts Ascent** (98,134) → (168,133): the Coptic Khan entrance, a vaulted passage into a courtyard (E06 at
  (111,125.6)); a narrow stepped lane under arches with shops (E07); old cream-painted steel doors with graffiti
  (52911377). Falls 8.6 m to CQR; Greek monastery of the Great Panagia (n4296490589 (134,134)). **M**

### 1.10 P3: North residential block (Ar-Rusul and lanes, x 40-160, y 255-430)
OSM and rooftop views only (A02 background, F01, F05). 2-4 storey houses (spec 9-15 m), shallow white domes and
red-tile hipped roofs, rooftop rooms with water tanks, enclosed balconies; lanes 2-4 m with steps (Ar-Rusul falls
1.1 → -3.0 m going north-east). Terra Sancta High School (F04: 3 storeys of ashlar with regular windows over an open
ground-floor colonnade on round columns, the basketball court in front). The stairway up to the ramparts
(F05 at (6.6,350): a steel stair with a rusty gate, out of use) and the monastery garden along footway 617363469.
**L** except F04/F05 (**M**).

### 1.11 CQR west frontage (x < 160)
The souq profile already covers it (Christian Quarter Street 0.9/0.35). w1392902299 e1 (156.6,243) faces 89,
w1392903888 e1 (160.5,199.2), w1392903887 e1 (159.3,187.9): souvenir shops with **pale teal/turquoise steel doors**,
white shop fascias, ceramic street sign on the GOP corner pier (G01). The west side is under the souq's roof at
y 160-230 (s04 notes 1.3). **H** (G01, s04 B01-B06)

---------------------------------------------------------------------------------------------------------------

## 2. LANDMARKS (modelled by landmark modules; described only)

### 2.1 St Saviour (church w106249447, monastery r1515591; landmarks_city.py)
- **Tower position (request R1)**: OSM r21355050 (x -15.6..-9.5, y 265.9..272.7) sits in the re-entrant corner of the
  church ring at its north-east (the nave narrows north of y 272). The landmark builder uses SAV_TOWER = (-3.6,
  250.4), the Commons object location of three photos, 21 m SSE, on the monastery block east of the church's south
  end. A08 bearing check (above) favours OSM. F01 (from the north wall, near New Gate) shows the long red-tile nave
  roof extending to the right (south) of the tower, which also fits a tower near the north end. **M**
- **Tower**: square cream shaft with paired louvred round-arched openings, a balustraded stage, a clock stage with
  clock faces and corner urns, then a **steep octagonal spire clad in dark green diamond-pattern tiles**, a small
  balcony lantern and a cross (A08, F01, F08, B12, B13). Matches the landmark notes. **H**
- **Church roof**: a long **red-tile hipped roof with a row of small gabled dormers** (F01, F08), OSM roof:shape
  hipped / roof_tiles. **H**
- **Monastery blocks**: flat roofs with black geometric railings, AC units, a glass pyramid skylight (F08); along
  the north wall a 2-storey wing with tall rectangular windows in dressed frames and a stepped upper block, lane and
  parking along the wall (sav_09, F03); the **"TERRA SANCTA" gate** (round arch with a Jerusalem cross and the words
  TERRA / SANCTA on the impost band) from the north yard (sav_06, sav_08, 53565731 not kept). Spec w290818505 is
  12.4 m with 8 domes; photos: 3-4 storeys stepped, no domes. **H**

### 2.2 Co-Cathedral of the Most Holy Name of Jesus and the Latin Patriarchate (w1392261827, r3864586)
- Co-Cathedral: neo-Gothic, pale smooth ashlar, steep **gables with stepped pinnacles**, large pointed windows with
  tracery (C04), a square **bell tower with corner pinnacles and the Vatican flag** (C05, C03, C07), red-tile pitched
  roofs (C08). Its LPR wall: lancet windows high, pointed gate (C01). **H**
- Patriarchate (r3864586, not a landmark): 3 storeys of smooth ashlar with **round-arched windows** in rows around
  courtyards; **red-tile pentices on steel posts over the courtyard walks** (C06, C07); flat roofs with solar heaters
  and water tanks; palms in the gardens (C07, F02). Spec 13.8 m with 8 domes → ~14-15 m, domes 0. **H**

### 2.3 New Gate (w1393450805, landmarks_gates.py)
Inner face (A05, 2018): the same broad four-centred arch with rusticated voussoirs and a crenellated parapet with a
steel railing (ramparts walk) as gates.md describes; through it the palms and buildings of Tzahal Square. Inside,
the inner gate square (y 280-297) with lift gates, bollards and the shop arcade (1.2). Nothing to add. **H**

### 2.4 Other notable (non-landmark) buildings, for overrides
| building | OSM | photo facts | conf |
|---|---|---|---|
| Collège des Frères | w91624550 | 4 storeys (~17-19 m) of pale ashlar, dense window grid, attic storey on part, flat roof with railing; statue niche and flagpole on the S front (Les Frères); seen from Notre Dame towering over the wall (A11, A06, F02, A09) | M-H |
| Knights' Palace (Latin Patriarchate, N end) | r3864586 at (-112,190) | entrance A07; castellated corner turrets seen from the NW rampart (F02) may be this block or the Collège | M / L |
| Casa Nova | r19228634 | entrance B10; 3-4 storeys, smooth ashlar (C03 background) | M |
| Greek Orthodox Patriarchate | w290810608 | smooth honey ashlar, 3 storeys ~13-14 m, **rounded NW corner** at (27,160-167), grilled ground-floor windows, grey shutters, black bollards; north front on GOP St | H |
| GOP St north front | w1392902286 e0 | 2 storeys, ground-floor shops, row of ~12-14 small round-arched windows above (D01) | H |
| Gloria / former Greek hospital | r19228633 | 4 storeys, railing, fire escape, garden fence (C12) | M |
| Terra Sancta High School | w290824723 | 3 storeys on an open colonnade (F04) | M |
| St Francis N side (x 46-80) | w1392256447, w1392256449 | orange-honey ashlar, string course, tall arched windows, basement light well with railing (B04) | H |
| Samara building | w1393928794 | honey rubble, 2 storeys, pierced triangular parapet, arched windows; white dome behind (D10, D11) | H |

### 2.5 Neighbouring landmarks that dominate views from this sector
Holy Sepulchre domes (s04) close the east vistas of GOP St and St Francis St; the **Khanqah minaret** (s04,
w620113736 at (175,247.3)) stands exactly on the axis of St Francis St looking east (B04, B06, B07); the Redeemer
tower (s04) and the Dome of the Rock appear over the roofs from the ramparts (F08); the Tower of David (s00) closes
the south view of LPR.

### 2.6 Hezekiah's Pool (way 126086870), the sector's big void
- A rectangular basin ~40 x 75 m (OSM). Floor: pale gravel and dried mud with weed tufts (summer 2017-2021: E09, E10),
  green grass in spring (E12, 2015), a dark pond with reeds after rain (E08, winter 2010). **H**
- **Walls**: on every side the back elevations of 3-5 storey houses rise straight from the floor: rough rubble and
  re-used ashlar, small irregular windows, blocked arches, iron-framed **box rooms and balconies cantilevered over
  the pool**, AC units, pipes, satellite dishes; whitewashed rooftop rooms; the Coptic Khan's tall blank east wall.
  A plain lower band (~3-5 m) without windows runs round the base (the pool's own retaining wall) (E09-E12). **H**
- **Depth**: from E10 the lowest house doors/windows on the north side are ~3-4 m above the floor and the tops of
  the walls 15-18 m above it. With the street field at -2..-5 around it, the floor is plausibly ~-8 (±2) (≈ 4-6 m
  below the ground floors). **L**
- Views: only from roofs (Petra Hotel roof, s00) and from the rooftops of the Christian Quarter; no public access.

---------------------------------------------------------------------------------------------------------------

## 3. GATES and gate-like structures

1. **New Gate** (landmark): inner square with lift gates n6915140442/n6920771030, bollard n6915140443, gate barriers
   at n12921775157 (-135.8,290.8) and n1396048478 (wall gate). **H**
2. **St Francis vault** (w1393428497, x -9..4.5): groin-vaulted street tunnel, ~14 m (0.3). **H**
3. **GOP St arch** at x ≈ 88-95 with the Patriarchate gate under it (1.7). **M**
4. **Casa Nova stair arch** at ~(17,169) (1.5). **M**
5. **Latin Patriarchate gate** n12920645469 (-53.3,97.7): pointed arch with Gothic iron tracery (C02); gates
   n12920625141 (-50,136.6) (Co-Cathedral courtyard, locked metal gate 1395892711) and n12920645472 (-60.4,85.9). **M**
6. **"TERRA SANCTA" gate** of St Saviour from the north yard (sav_06/sav_08). **H**
7. **Versavee through-house passage** on GCP St at ~(42,75) (E02). **M**
8. **Coptic Khan** vaulted entrance off Copts Ascent at ~(111,126) (E06). **M**

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Bollards and barriers
- **Square limestone bollards** (~0.4 x 0.4 x 0.5 m) every ~3 m along the Bab el-Jadid shop row, with **red-white
  striped steel posts** between (A01). **H**
- **Red-white painted stone bollards** (short cylinders/blocks) at lane corners: St George/GCP (E01), GCP square (E04),
  Versavee passage (E02). **H**
- **Black steel bollards** along the Greek Orthodox Patriarchate (D12) and small square stone bollards along the
  Co-Cathedral wall (C01). **H**
- Lift gates at New Gate (OSM). Grey ornamental railing (circle pattern) along the St Francis light well (B04);
  steel handrails on St Francis and GOP St (OSM handrail=yes; D02, D04). **H**

Lighting
- Black wall lanterns on curved brackets (Knights' Palace A07; GOP St D02), hanging lantern in the GOP arch (D03,
  28848423). Plain street lamps on poles along Bab el-Jadid Rd (A01). **H**

Signs
- **Ceramic street signs** (white tiles, coloured border, Hebrew/Arabic/English): "BAB EL-JADID RD", "FRERES ST."
  (A12), "LATIN PATRIARCHATE RD." (C03), "AL-JAWALIDA ST." (C14), "GREEK ORTHODOX PATRIARCHATE RD." (D16), "GREEK
  CATHOLIC PATRIARCHATE RD." (9404979, not kept), "CHRISTIAN QUARTER ST." (G01). **H**
- Institutional plaques: "KNIGHTS' PALACE / LATIN PATRIARCHATE" (A07), "College des Freres Jerusalem / DE LA SALLE
  HIGH SCHOOL" white board (79135131, not kept), "CASA NOVA" (B10), the Officium Paroeciae inscription (B03),
  "PROPERTY OF GREEK ORTHODOX PATRIARCHATE" red-white enamel plates with the Taphos monogram (6214124, not kept),
  pink Bible-verse plates on St Francis St (sav_03). **H**
- House-number plates (white squares, black numerals: "237" A07, "5" B03, "21" St George). **H**

Flags and strings
- **Vatican yellow-white and Jerusalem-cross pennants** strung across St Francis St and in its vault (B01, B02, B06,
  B07); Vatican flags on the Patriarchate, Co-Cathedral and Collège (C05, C07, A06); **Greek flags and the red-white
  Patriarchate (Taphos) flag** on GOP St (D03, D07); Jerusalem-cross flag in the GCP square (E04). **H**
- Christmas (December only): ball and star lights, trees on Bab el-Jadid Rd (A04). **H**

Bins, cabinets, clutter
- Green municipal wheelie bins (E01, D07), blue plastic bins (B14); grey and blue steel electrical cabinets (D07);
  yellow British-era post box at GOP/CQR; satellite dishes, AC units and water heaters on every roof (D01, A02, E09);
  parked cars (Bab el-Jadid, LPR, GOP west end, St Dimitri south). **H**

Vegetation
- Palms, cypresses, pines and olive trees in the Latin Patriarchate gardens and along the wall (C07, F02, 51 OSM
  trees in the sector); a cactus and palm garden behind the Jawalida wall (C14); trees and creepers spilling over the
  St Francis garden walls (B06); big shade trees in the St Dimitri school garden (D14); weeds and grass on the pool
  floor (E09-E12); potted plants at the Knights' Palace and along St Peter St (A07, C13). **H**

---------------------------------------------------------------------------------------------------------------

## 5. TERRAIN

Levels from `terrain_street.street_z` (m above the street at the Jaffa Gate node; datum 770.58 m asl), with the
OS 1865 check:

| place | street_z | OS 1865 anchor (z) | basis |
|---|---|---|---|
| Inner New Gate square (-127,294) | 14.1 | (-99.3,296.8) 14.58 → model 14.41 | H |
| Jawalida / Knights' Palace (-110,192) | 16.5 | (-123.6,190.5) 16.41 → 16.36 | H |
| Les Frères at Bab el-Jadid (-83,207) | 15.6 | (-60.6,234.1) 13.37 → 13.42 | H |
| Les Frères / St Francis / Casa Nova junction (-20,219) | 10.5 | (-9.8,226.2) 9.10 → 9.20 | H |
| St Francis vault (-2,236) | 8.5 | — | H |
| St Francis at Ar-Rusul (108,256) | 0.2 | (110.4,252.8) -0.05 → -0.04 | H |
| St Francis at CQR (159,261) | -4.9 | (161.1,258.4) B -4.83 → -5.17 | H |
| Casa Nova Rd top (-1,196) / foot (19,167) | 9.2 / 6.6 | (25.6,168.8) 5.44 → 5.57 | H |
| GOP St W end (22,168) / E end (160,221) | 6.1 / -6.2 | (70.8,190.4) 1.48 → 1.66; (161.5,220.7) -6.45 → -6.36 | H |
| LPR: Jaffa Gate end (48,0) / Co-Cathedral (-40,128) / St Peter (-38,147) | 0.3 / 10.0 / 12.0 | (-49,115.8) 8.49 → 8.54; (-49.7,94.3) 7.27 → 7.25 | H |
| St Dimitri S (39,83) / N (19,167) | 4.0 / 6.6 | (42.9,125.3) 5.14 → 5.08 | H |
| St George (60,52) / Copts Ascent top (98,134) | 2.6 / 1.0 | (88.4,135) 1.17 → 1.32; (95.4,73.3) 2.39 → 2.30 | H |
| Copts Ascent at CQR (166,133) | -7.2 | (173.4,132.2) -8.9 (s04) | H |
| Hezekiah's Pool floor | street field -2..-5; real floor ~-8 (L) | none (the pool was a basin in 1865) | L |
| North block: Ar-Rusul (128,331) / Terra Sancta (100,390) | -3.0 / -3.0 | (84.2,334) 0.26 → 0.07; (103.1,352.6) -6.14 → -5.58; (105.8,397.5) -3.40 → -3.53 | H |

All 36 anchors inside the sector: median |residual| 0.13 m, 28 within 0.3 m, 33 within 0.6 m, max 1.05 m (two bench
marks cut in walls, (-9.9,141.1) and (120.3,375.6), which sit above the ground by design).

Stairs (OSM steps vs the modelled drop):
| way | steps | length | drop (street_z) | riser if all steps | photo |
|---|---|---|---|---|---|
| St Francis 1005635990 | 43 + ramps | 122 m | 9.4 m | 0.22 m (too high: the rest is taken by the **ramped treads**) | B04 ramped stretch without steps, B09/B14 short flights; model: stairs.py makes ~67 risers of 0.14 m; expect groups of 2-4 low steps (~0.12-0.15 m) between sloping slabs, plus a cart ramp strip |
| St Francis 1005635988 | 11 | 18.7 m | 0.9 m | 0.08 m | the 11 steps include the climb to the vault mouth (B08: 4 steps + landing); the street field misses ~0.7 m here — accept |
| St Francis 26492707 | (no count) | 52 m | 5.0 m | — | stepped souvenir lane (B05) |
| Casa Nova 26492709 | 23 | 36.5 m | 2.7 m | 0.12 m | consistent with ~0.12-0.15 m risers (157342670) |
| Copts Ascent 229756029 | (no count) | 76 m | 8.6 m | — | 11 %: continuous steps (E07) |
| Ar-Rusul 617363476 | 3 | 5.6 m | 0.3 m | 0.09 m | — |
| GOP St (pedestrian, no steps way) | — | 151 m | 12.2 m | — | stepped in the east half with a central cart ramp (D04, D07); stairs.py adds steps where > 7 % |

Raised platforms and sunk areas: shop platforms / thresholds 0.15-0.3 m on Bab el-Jadid Rd (A01) and a 3-step arcade
platform at the gate (A04); the St Francis basement light well ~1 m deep behind a railing (B04); the pool (~4-6 m
down, R4); the Co-Cathedral and Patriarchate courtyards behind gates (not walkable).

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **Open St Francis St and St George St**: turn OSM building=roof w1393428497 (St Francis vault, ~14 m, crown
   ~4.5 m) and w1394034708 (St George) into vaulted passages instead of solid buildings (R2). (0.3, 1.6)
2. **Bab el-Jadid Rd east side as a one-storey red-tile shop row** (w1392271953, w1392271954: ~4.5 m eaves,
   hipped/pent tile roof, dark green round-arched steel doors, grey scalloped canopies, square stone bollards and
   red-white posts), cars in the parking lane, the arcaded shops on a 3-step platform on the west side at the gate.
   (1.2)
3. **Remove the infill slivers in front of real facades** (or merge them into the building behind): GOP St both
   sides (f171, f173), Co-Cathedral (f14), Casa Nova (f220, f221), St Francis N (f27), Latin Patriarchate (f15, f20),
   St Saviour (f23, f24) (R3). (0.4)
4. **Greek Orthodox Patriarchate** (w290810608): smooth honey ashlar, 3 storeys ~13-14 m, rounded NW corner at
   St Dimitri/GOP, grilled windows, black bollards; its north front directly on GOP St. (1.7, 1.8)
5. **GOP St as a monastic stepped lane**: ramped west half, stepped east half with a central cart ramp, high blank
   rough walls, box oriels, the arch at x ≈ 88-95 with the Patriarchate gate and flags, shops with brown shutters
   and hoop-bracket canopies only at x 121-160. (1.7)
6. **St Saviour tower at OSM r21355050** (-12.5,269.3) (R1) and the church's red-tile hipped roof with dormers; the
   tower must be visible on the axis views from Les Frères St (A08) and over every roof. (2.1)
7. **Hezekiah's Pool as a sunken dry basin** with weedy gravel floor and the back walls of houses dropping into it
   (R4). (2.6)
8. **Institutional palazzi without domes**: Collège des Frères ~18 m, Latin Patriarchate ~14-15 m (round-arched
   windows, red-tile courtyard pentices), Gloria/hospital ~15 m, St Saviour monastery blocks, Terra Sancta School on
   pilotis; flat roofs with railings and rooftop clutter, `domes: 0`. (0.7, 2.4)
9. **St Francis St**: the vault, the B02 yellow Jerusalem-cross bay, ramped steps with handrail, the orange-honey
   north facade with string course, tall arched windows and railed light well (B04), garden walls with greenery at
   x 80-106, souvenir lane with canopies x 106-159, the Khanqah minaret on the axis. (1.6)
10. **Latin Patriarchate Rd**: parked cars, blue-door arched shopfronts at the south end; the Patriarchate's Gothic
    iron gate; the Co-Cathedral's long smooth wall with lancets and pinnacled gable on the street (C01). (1.4)
11. **The NW lanes**: Les Frères with box balconies, café awnings and the tower view; Knights' Palace entrance with
    lanterns; Collège south front with statue niche; Jawalida cactus wall. (1.3)
12. **Casa Nova stair** (23 steps under an arch from St Dimitri, Casa Nova entrance, rubble walls) and St Dimitri's
    two halves (open south court with the school loggia and garden, narrow north part along the Patriarchate). (1.5,
    1.8)
13. **Roofscape**: red-tile hipped roofs and shallow white domes on the houses, rooftop rooms, water heaters, the
    Co-Cathedral gables and bell tower, the St Saviour roof and monastery railings. (0.8)
14. **Flags and pennants**: Vatican and Jerusalem-cross pennant strings over St Francis St, Greek and Patriarchate
    flags on GOP St, Vatican flags on the Catholic institutions; ceramic street signs at every corner. (4)
15. **Materials**: smooth pale ashlar (institutions) vs rough rubble (lanes, houses, pool walls) — today all 300
    records are `wall: rubble` with the same flat roof; sett paving with darker bands, red-white bollards. (1.0)

---------------------------------------------------------------------------------------------------------------

## Requests (for the spec owner / landmark owners; to be copied into the profile by the next pass)

- **R1 (landmarks_city, St Saviour)**: move `SAV_TOWER` from (-3.6,250.4) to the OSM tower r21355050, centre
  (-12.5,269.3), footprint x -15.6..-9.5, y 265.9..272.7 (5.5 x 6 m; matches the landmark's 5.6 m shaft). Evidence:
  OSM `man_made=tower, tower:type=bell_tower`; A08 bearing ~49° from the Les Frères centreline at (-55..-62, 220-224) vs 43-45° (OSM) / 62° (current);
  F01.
- **R2 (make_spec, covered streets)**: OSM `building=roof` footprints lying across a street centreline should be
  carved and vaulted like tunnel/covered ways, not built as buildings: w1393428497 over St Francis St (13.3 m of way
  1005635990 inside it; groin vault ~3 m wide, crown ~4.5 m, rooms above to ~11.7 m; B01, B02, B08) and w1394034708
  over St George St (3.2 m of way 229846305). Today the first blocks the St Francis walk (render sf_mid).
- **R3 (infill.py)**: infill pieces with mean width 2A/P < ~3 m that run along a mapped footprint should not be
  separate low buildings in front of it: drop them, or merge them into the footprint they touch (same height and
  style). In s03 all 51 pieces are such slivers (0.7-5 m, 6.5-9.4 m high); the worst: f173 (Greek Orthodox
  Patriarchate front), f171 (w1392902286 front), f14 (Co-Cathedral), f220/f221 (Casa Nova), f27 (St Francis N),
  f175 (spans x 83-225 along GOP/Copts/CQR). If dropped, GOP St widens to 7.3-7.6 m at x 24-69 (photos ~5-6 m), so
  merging (thickening the real facade outward) is the better option there.
- **R4 (make_spec SUNKEN)**: Hezekiah's Pool, way 126086870 (x 116.4-162.8, y 23.5-98.6; partly in s00/s05 south of
  y 48): a sunken area, floor ≈ street_z - 5 (±2, L), ground material dry earth/gravel with weeds (meadow 1549495722),
  surrounding buildings to start their pool-side edges at the floor (edge_ground), back-facade style: rubble, small
  irregular windows, cantilevered box rooms, no shops (E08-E12). Not walkable from the streets.
- **R5 (roofscape / overrides)**: no vernacular domes on the 19th-century institutions: w91624550, r3864586,
  r19228633, w290818505 (8 each today) and w1392271953 (3 domes + a roof room on a one-storey tile-roofed shop row).
  These can be done as building overrides (`domes: 0`, `roof`), listed here so the next pass does them.
- **R6 (make_spec walls)**: build OSM barrier=wall ways (height tag or ~3.5 m default, stone): 1396048476 (4 m,
  Collège on Bab el-Jadid Rd), 1396050324-26 (Jawalida park), 1549774036, 1549203673, 1393938074, 1005635993; and give
  the garden open areas that front St Francis St (290824743, 290818503, x 80-106) a 3-4 m rubble boundary wall
  (B06). Today open areas meet the street with no wall.
- **R7 (render_city.py)**: the ground ray cast finds nothing with the current `base/ground.glb` (01:21 build);
  without `--abs` every camera ends at absolute z ≈ 1.6. Workaround used: `--abs` with z = street_z + 1.6.

---------------------------------------------------------------------------------------------------------------

## Provenance

80 Commons photos in `data/photos_ref/s03_christian_w/` (1280 px thumbnails; `index.json` has title, page, author,
licence, date, lat/lon and local x/y where Commons has a camera position, plus `loc_note` where that position is
known not to be the camera). Groups: A = New Gate, Bab el-Jadid Rd, Les Frères, Collège (12); B = St Francis St,
St Saviour, Casa Nova (14); C = Latin Patriarchate Rd, Co-Cathedral, Patriarchate, St Peter, Jawalida (14); D = GOP
St and St Dimitri (16); E = Greek Catholic Patriarchate St, St George, Copts Ascent, Hezekiah's Pool (12); F =
overviews from the ramparts, Notre Dame and the Redeemer tower (11); G = CQR corner (1). Licences: CC BY-SA 4.0
(23), CC BY-SA 3.0 (19), CC BY 2.0 (13), public domain (8), CC BY 2.5 (6), CC BY 4.0 (5), others (6).
Cited from other passes' folders: `data/photos_ref/gates/` n12, n13, n14 (New Gate street, 2009-2011),
`data/photos_ref/landmarks_city/` sav_03, sav_06, sav_08, sav_09 (St Francis St, Terra Sancta gate, monastery from
the ramparts), `data/photos/073-076` (Terra Sancta girls' school, LPR south end, s00).
Most useful: A01-A03 (the shop row from above), A04 (GPS, 2019), A08 (Les Frères, tower bearing), B01/B04 (St
Francis vault and middle), C01-C07 (Latin Patriarchate, Wiki Loves Monuments 2015-2017 and ramparts), D01/D02/D07
(GOP St; D07 is the 2025 Fujifilm GPS walk also used by s04), D10-D12 (Patriarchate corner), E08-E12 (pool from the
Petra Hotel roof), F01/F07-F09 (rooftops from the north wall and Notre Dame).
Commons positions that are not camera positions: the St Saviour group (-4.1,250.8) is an object geocode (not used);
the Wikimania 2011 group (34.2,100.2), the 2011 "Batch 1" GOP group (108.5-108.6,223.4) and (102.9,200.9) are shared
geocodes; 54675040 (not kept) is tagged outside the wall. A04 (-135.7,281.5) sits ~8 m W of the street centreline;
D02 (71.4,197.1) ~9 m N of it (phone GPS); D07 (154.8,229.1) is on the GOP St steps (Fujifilm EXIF GPS, consistent).
A08 is tagged (-54.7,217.1), 6-7 m south of the Les Frères centreline; for the tower bearing check the camera was put
on the centreline at (-55..-62, 220-224) with the heading along the straight segment (59.3°) (vanishing point at the
image centre, ~28 mm-equivalent assumed), so the check carries ±5° of error; both camera choices favour OSM.
Commons was rate-limited (HTTP 429, Retry-After ~30 s, shared IP with the other sector passes); requests were made at
≥ 3 s intervals, 80 + 30 thumbnails were downloaded in all (unused ones stay in `build/spec_s03_christian_w/dl/`).
Measurements: street widths `build/spec_s03_christian_w/widths.py` (with and without infill), facade edges
`edges.py` / `frontage.py`, plans `plan_*.png`, renders `renders/sectors/s03_christian_w/r1_baseline_abs/` (bje:
(-123.5,276) → (-113,247); sf_mid: (44,245.5) → (12,239); gop_w: (24,169) → (60,182.7); lpr: (0,53.8) → (-47,92);
z = street_z + 1.6, lens 20). What they show: bje, two blank 10-14 m walls and wide flat slabs where A01 has the
one-storey tile-roofed shop row and parked cars; sf_mid, a 3 m canyon of uniform rock-faced blocks ending in the solid
w1393428497 "vault" building; gop_w, two uniform 8.7 m infill walls instead of the arched-window front and the
Patriarchate's rounded corner (D01); lpr, wide smooth slabs, green doors and crates instead of the parked cars and
blue doors of C10/C11. (dimitri_n was placed inside w290812334 by mistake and is not used.)
