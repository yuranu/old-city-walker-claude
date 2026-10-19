# s08_damascus: Damascus Gate, Khan ez-Zeit north, Al-Wad north — visual reference

Local frame as in `hero_edges.md` (x east, y north, metres from the Jaffa Gate OSM node;
x = (lon-35.2275435)*94721.7, y = (lat-31.7766282)*110882.9). Edge numbers below are for the
**CCW-normalised OSM ring** of each building in `data/osm_local.json` (edge i = vertex i -> i+1), given with
start/end coordinates and the compass direction the edge faces, so they can be re-matched if rings change.

Photos: `data/photos_ref/s08_damascus/Dnn_*.jpg` (45 Commons photos downloaded for this note, 1280 px;
title, page, author, licence, date, lat/lon and local x/y of geotagged ones in `index.json`). Keys below
are `D:nn`. Scale from people (1.7 m), doors (2.2 m), steps and OSM edge lengths.
Confidence: **H** = seen clearly in 2+ photos or measured on OSM; **M** = one good photo or a consistent
estimate; **L** = inferred / partly hidden / OSM only.
Elevations are from the SRTM-derived terrain tiles in `data/raw/terrain/` (±2-3 m, 30 m cells); step counts from
OSM `step_count`. *[Review: SRTM is superseded. The project's street-level model `data/terrain_street.json`
(calibrated on the OS 1865 spot heights, docs/TERRAIN.md) differs by up to 10 m here. Section 5 now gives
its values, and they are the ones to use.]*

> Status: complete (written incrementally). Independently reviewed 2026-10-20: corrections are marked
> *[Review: ...]* in place and listed in "## Review" at the end.

---------------------------------------------------------------------------------------------------------------

## 0. OSM skeleton and the biggest things to get right

OSM facts (all **H**, measured on `data/osm_local.json`):
- **Damascus Gate** w616186088 (450 m², `layer=1`, centroid (268,557)) is a ~46 m wide block across the north
  wall: a **west tower** (front edge e8 (254.7,556.5)->(245.3,548.2), 12.5 m, faces 318°), a **recessed central
  curtain** (e5 (273.6,565.1)->(265.8,558.2) 10.4 m + e6 (265.8,558.2)->(258.8,551.9) 9.4 m, both face 318°) and an
  **east tower** (front e3 (279.7,578.2)->(269.7,569.4), 13.3 m, faces 318°). Both towers project ~6 m in front of
  the curtain (flanks e4 5.8 m faces 228°, e7 6.1 m faces 48°). **The gate faces NW (318°); a walker enters
  heading SE (138°).**
- The **outer doorway is in the middle of the curtain** at (265.8,558.2) (vertex between e5 and e6; offset
  ~0.5 m from the curtain centre).
- **Bridge** w616383626 (`bridge=yes`) 20.4 m long from the plaza (251.9,573.2) to the threshold.
- **Passage** w616186087 (`covered=yes`) is a **double right-angle (S-) bend** with a short sideways offset:
  (265.8,558.2) SE 3.4 m -> turn left ~94° -> (268.0,555.6) NE 2.9 m -> turn right ~92° -> (270.1,557.6) SE 7.8 m ->
  **inner exit (275.4,551.8)**. The overall heading is unchanged (unlike Jaffa Gate's single L-turn), but the
  straight view from the outer doorway is blocked by the end wall with the BIG BEN shop (D13, D02).
  *[Review: corrected; the original said "a shallow zig-zag, not a right-angle turn", but both OSM turns are ~90°.]* A covered side passage
  w616338411 leaves west at (268.0,555.6) through the west tower to a small inner court at (262-272, 540-549).
- **Inner face**: e15 (269.2,546.3)->(275.4,551.8) 8.3 m + e16 (275.4,551.8)->(285.4,560.7) 13.4 m, both face 138°.
- **Damascus Gate street** w616186086 (`surface=sett`) runs SSE ~70 m from the inner exit to the **fork at
  (311.7,496.3)**, through the inner square (pedestrian area w1549494830, x 277-307, y 506-551).
- **Fork**: Suq Khan al-Zeit w256298879 goes S along x ≈ 304-307 (leaves the sector at y 430); Al Wadi w26496070
  goes SE via (321.7,488.9), (342.1,462.7), (363.6,435.1).
- **Sheikh Lulu Ascent** w257604166 (`highway=steps`, `ramp=yes`) starts at the inner exit (276.9,550.2), runs
  along the east tower's inner face and climbs NE/E to (363.8,601.0).
- Outside: **Damascus Gate Plaza** w217547413 (`lit=yes`, paving stones) is the sunken amphitheatre between the
  bridge foot (247.8,577.7) and Sultan Suleiman St (y ≈ 604-632).

Biggest things to get right (summary):
1. **The gate is the sector.** Twin towers + a recessed curtain, a moulded pointed arch with a smaller
   rectangular doorway, a framed window above it, a central box machicolation, corner bartizans and
   **stepped merlons with pointed finials** all along the top. Parapet ~15 m, finials ~17 m above the threshold
   (±1 m; revised in review from ~14 / ~16 m, see 3.2). (H for form, M for heights, section 3)
2. **You reach it by descending.** The plaza outside is a sunken amphitheatre of pale stone terraces ~5 m deep,
   with stair runs and galvanised handrails, and a 20 m bridge, ~7.5 m wide, over the excavated Roman level.
   The Roman side arch shows NE of the bridge. (H, 3.9)
3. **Inside, the main street is split lengthwise**: a grey sett ramp on the west half and limestone steps on the
   east half, falling **~6-7 m** from the inner exit to the fork (street-level terrain, see 5; revised in review). It is lined with canvas and striped awnings, tarps strung across
   and umbrellas. (H, profile C)
4. **The fork** where Khan ez-Zeit (S) and Al-Wad (SE) split. The view is closed by a building and both streets
   leave at an angle. (H, 1.5)
5. **Khan ez-Zeit (north part)** is a 4-4.5 m souq: pointed barrel-vaulted bays alternate with open bays
   under corrugated canopies. When closed it reads as **rows of multi-leaf steel doors** (grey, beige, olive, a few
   yellow, red-orange, blue). (H, profile D)

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and street profiles

### 1.1 Character
- The busiest Palestinian market entrance of the Old City: a **monumental Ottoman gate** facing a **modern
  stone amphitheatre** outside, and inside a dense **market square that funnels downhill into two souq streets**.
  It is not a tourist-souvenir zone like David St. Goods are food, clothes, household items and sweets. The
  shop fronts carry Arabic signs with phone numbers; English is rare. (H: D01, D22, D27, D28, D29, D30, D39, D41)
- Away from the two souqs (NE of Al-Wad, around Sheikh Lulu / Sa'diyya / Malawiya) it is **residential**:
  stepped lanes climbing ~15 m, plastered and ashlar houses with steel balconies, external steel stairs, steel
  doors and many cables. (M: D45, D31, D32; OSM step ways)
- Roofscape seen from the gate roof and the walls: flat roofs with **black plastic water tanks, white
  cylindrical solar water heaters** (many printed "ابراهيم اورجنال"), satellite dishes, TV masts, small
  **white-plastered cross-vault domes**, a few red-tile hipped roofs and roof rooms. Over the souqs there are
  **green and blue-white striped corrugated sheets**. (H: D15, D31, D32, D43)

### 1.2 Street-profile index (OSM `name:en` -> profile)
| OSM way(s) | name:en | profile |
|---|---|---|
| w217547413 (area), steps w617363480/w617363471/w217547844/w616383623 ("Ma'alot Hadar VaHadas"), w616178276/279/282/284, w217547419 | Damascus Gate Plaza (Bab al-Amoud) | **A** outer amphitheatre plaza |
| w616383626 | Damascus Gate (bridge) | **B** gate bridge |
| w616186087, w616338411 | Damascus Gate (covered) | gate passage (section 3.6) |
| w616186086 + area w1549494830 | Damascus Gate | **C** inner square and main souq street (ramp + steps) |
| w256298879 | Suq Khan al-Zeit | **D** semi-covered souq |
| w26496070 | Al Wadi | **E** souq / main street, partly covered |
| w257604166, w257604184, w257604188, w246593337, w257604174, w26578540, w258375962, w582488418, w1393163029, w26506006, w26506005, w26492740, w257604173, w582488417/419, w26496667, w26492738, w246593338 | Sheikh Lulu Ascent, Rassas Ascent, Ibn Jarrah, Al-Sa'Diyya, (شارع السعدية), al-Malawiya, Aqabat Ar-Rahbat / Er-Rahbat, HaTut (40 steps), Aqabat Al-Asseila, Ash Sheikh Rihan, Al-Hilal, Shaddad, Al Bustamy, Zawiyat al-Hunud | **F** stepped residential lane |
| w26496067, w290825080, unnamed w257604182, w257617657, w257617668 | Al-Jabsha, Es-Sayyida Road (west part) | **F** (lower, flatter variant) |
| roofs `building=roof layer=1` over lanes (w1393280745 over Al Wadi at (334,473), w1394054817 over Ash Sheikh Rihan at (436,482), w1394054424 over Ibn Jarrah at (402,557), w1393163043 over al-Malawiya at (492,557)); `layer=-1` footways w257604169, w123254014, w257604180 | — | **G** vaulted passage / sabat |

### 1.3 Profile A — outer amphitheatre plaza (Damascus Gate Plaza)
Photos: D08, D11 (from the wall, whole plaza), D12, D13, D35, D36, D20, D26.
- **Form**: a sunken, roughly fan-shaped plaza ~45 x 40 m. Its **bottom** is a flat paved floor at bridge level in
  front of the gate (around the bridge foot (247.8,577.7)). From it **stepped terraces climb ~5 m** north to Sultan
  Suleiman St and west to the HaNevi'im junction. On the east it climbs to the green strip along the wall. (H: D11,
  D08, D36; OSM steps)
- **Terraces**: pale limestone, ~10-14 rows. Seating terraces have **risers ~0.40-0.45 m and treads ~0.8-1.0 m**
  (people sit on them, D36, D12). They are cut by **stair runs with risers ~0.15 m / treads ~0.35-0.40 m**, two
  stair steps per terrace row. (M: D36, D11, D12)
- **Stair runs (OSM)**: central run N from the bridge foot, w617363480 (22 steps) + w617363471 (14 steps) to
  (249.6,608); west run w217547844 (22) + w616383623 (14) to (217.4,581.4); NE run w616178276 (19) -> w616178279
  (13) -> w616178284 (22, to (262.6,619.1)) and w616178282 (10). The central and west runs have **centre +
  side handrails** (`handrail:center=yes`). Bottom-to-street height ≈ 36 steps x 0.15 m ≈ **5-5.5 m** (SRTM
  757 -> 761). (H for layout, M for heights)
  *[Review: the street-level model has Sultan Suleiman St at ~757.6 at the top of the central run, and the bridge
  is at ~753, which gives ~4.5 m (risers ~0.13 m over 36 steps). The sunken forecourt itself is not in the
  model. Use 4.5-5.5 m. Sultan Suleiman St rises E: the NE run has 19+13+22 steps up to (262.6,619.1).]*
- **Handrails**: **galvanised / light-grey steel tubes** (~1.0 m, round posts, two rails) on the stair runs; black
  steel vertical-bar railings (~1.1 m) along the bridge and the edges of the sunken areas. (H: D12, D13, D35, D08)
- **Retaining walls**: the upper edge is a smooth pale ashlar retaining wall ~3-4 m high with a flat coping and
  black railings on top. In the NW wall, on the bridge axis, sits the **Sabil Bab al-Amud niche** (2.3). Square
  dark openings (passages to the lower level) are set into the walls at the corners. (H: D11, D35, D36)
- **Floor paving**: large pale limestone slabs (~0.5-0.6 x 0.6-1.2 m) in running bond, fanning around the curves.
  The paving includes **round cast-iron grates (~0.8 m, radial slots)**, rectangular steel-framed covers infilled
  with stone, and dark joints. (H: D08, D36, D12)
- **Clutter (closed state)**: a grey slotted cylinder bin, a black monolith sign at the lower west side (D12),
  curved grey vent pipes and black railings on the upper rim (D20),
  festival string lights on cables strung from the gate across the plaza (Ramadan: D20, D26; also plain
  catenaries D10, D11). Herb and grape sellers with crates sit on the steps when open (D34). (H)
- The plaza is **lit** (`lit=yes`): tall grey poles on the upper rim along Sultan Suleiman St (D35). At night
  the gate facade is floodlit warm white from below (D20, D26). (H)

### 1.4 Profile B — the gate bridge (w616383626)
Photos: D13 (best, telephoto from the plaza), D12, D08.
- Deck **~7-8 m between parapets** (scaled from people in D13), **20.4 m long** (OSM), nearly level with a slight
  fall toward the threshold. (M width, H length)
- Paving: **small rectangular slabs ~0.3 x 0.6 m in mixed cream / ochre / pinkish stone, running bond**, a few
  square covers. This is visibly warmer and finer than the plaza slabs. (H: D13)
- Both sides have a **low ashlar parapet (~0.5-0.6 m) carrying a black vertical-bar railing**. The total height is
  ~1.1-1.2 m. (H: D13, D12)
- Left (NE) side near the gate: the **crown of the Roman eastern side arch** shows just below deck level, with
  a stair down to the Roman level beside it (2.2). Right (SW) side: the **police booth** on a raised platform
  (2.4). (H)
- On each jamb of the doorway: a **grey pole with a white "no entry for vehicles" disc (red ring) and one or two
  yellow time plates** (Israeli sign 401). There is a black vertical municipal banner on a pole at the left (2025).
  (H: D13, D12, D17) When open, vendors line the bridge with crates and a red sweets cart (D17). Leave them out
  for the closed state.

### 1.5 Profile C — inner square and main souq street (Damascus Gate street, "Souq Bab al-Amud")
Photos: D01, D27, D29 (looking N to the gate), D30 (2018, looking N from near the fork), D22 (looking S into the
fork), D28 (fork steps), D24 (inner portal), D43, D31 (from above).
- **Plan**: a funnel. The **inner square** just inside the gate is **16-21 m wall-to-wall** for the first ~40 m
  (x 278-300) and is crowded with stalls, umbrellas and tarps. It narrows to **8-10 m** at (303-307, 498-514), just
  before the fork. (H: OSM widths; D29, D01)
- **Section (the signature)**: the street is **split lengthwise**:
  - the **west half (~2.5-3.5 m) is a continuous sloped ramp of small grey setts** (cobbles ~0.10-0.15 m, rough,
    darker than the steps) for tractors and carts. This matches OSM `surface=sett`;
  - the **east half is a flight of full-width limestone steps**: risers **~0.15-0.17 m** (long single blocks
    0.3-0.4 m deep, 1-1.5 m long), treads **~1.0-1.5 m**, with occasional 3-4 m landings. Edges are square and
    worn round, with no nosing.
  (H: D01, D27, D28, D30)
- **Fall**: from the inner exit down to the fork ≈ **6-7 m** *[Review: corrected from 3-4 m]*. The street-level
  terrain gives 751.2 at the inner exit -> 748.0 at (290,530) -> 743.9 at the fork. The OS 1865 spots are 750.42 at
  (288.2,551.8) and B.M. 744.35 at (312.5,501.0), and docs/TERRAIN.md route B has 752.5 / 747.6 / 743.2 at
  0 / 50 / 100 m from the gate. The ~20-25 risers counted in D01, D27, D30 undercount, because crowds and stalls
  hide flights. Model ~35-40 risers of 0.15-0.17 m in total, or fewer risers with sloped landings, plus the sett
  ramp at ~9 %. At the top just below the inner portal, a broad flight of 3-5 steps spans almost the full width
  (D01, D27). (M for the steps, H for the total fall)
- **Paving of the square**: large worn limestone slabs, cross-laid, with round cast-iron manhole covers.
  (H: D27, D24, D30)
- **Shop fronts**: 1-bay vaulted shops ~2.5-3.5 m wide under segmental or pointed relieving arches.
  Steel frames painted **blue, green or ochre**. Above, steel canopy brackets with **wrought-iron
  scrolls** and ornate scroll arms carrying hanging boards (a blank white board on an S-scroll bracket in D30).
  Closed: **multi-leaf steel doors** (blue, grey, green) and some roll-down shutters. (H: D28, D30, D39)
- **Coverings (the street's sky)**:
  - big **tan/khaki canvas shed awnings** on steel frames (~1.5-2.5 m projection, front edge ~3 m) (D30 right,
    D29);
  - **retractable striped awnings with scalloped white valances**: green-white, grey-white, red-white (D01,
    D28, D29, D24);
  - **corrugated metal shed canopies** (D01 left, D29 left);
  - **white tarps stretched across the street** between the canopy fronts at ~4 m (D27, D24, D01);
  - large market umbrellas in **blue (printed), green and rainbow** (D01, D27, D29);
  - *[Review: moved here from profile E]* seen from above, the stretch between the inner square and the fork is
    roofed from both sides by **green corrugated sheets and blue-white striped sheets/awnings** leaving a narrow
    sky slot (D43 from the gate roof, D31 from the ramparts). Both photos show this street, not Al-Wad. Steps
    are under the walkers in D31, and in both the far end has the west-side building with the triangular
    terracotta-pipe parapet that D30 places at the foot of this street.
  When shops are closed the awnings are rolled in but the canopies, frames and tarps stay. (H)
- **Upper floors**: 2-4 storeys of ashlar. On the **west side near the fork**: a **white-framed enclosed timber
  box window (glazed bay with many small panes)** on corbels at the 1st floor. Above it a **parapet screen of
  terracotta pipes laid in triangles** (pigeon-hole pattern), plus a white downpipe. (H: D30, also visible from
  above in D31)
- **Overhead**: sagging black cables, a string of coloured bulbs, catenaries of festival lights. A big old box
  floodlight on an arm hangs at the top of the west wall (D30). (H)
- **Signs** (section 4): green "HALAWANI 052-2532242" fascia (Fuze-tea branded) on the **west** side at the
  foot of the street; "NABIL H. BAKERY" board on the east; the yellow "طه للخضار والفواكه" greengrocer fascia
  at the fork. (H: D22, D28, D30; west/east from D30 looking N and D22 looking S)
  *[Review: the Taha greengrocer is also on the **west** side, immediately S of Halawani and facing E onto the
  street, ~8-10 m N of the fork building. D28 looks W at both shopfronts, with the sett ramp and tractor next to
  the shops and the steps in front rising to the right (N). D39 looks N with the same blue-framed stall on its
  left. OSM greengrocer node 5835977094 (299.0,502.5) is on that side.]*
- **Clutter**: fruit and vegetable crates, cardboard boxes, a **green Holder mini-tractor** (municipal / delivery,
  D28, D27), a yellow electric cargo trike (D13), ka'ak bread stands (D30), women sitting on the steps selling
  herbs (D28, D30, D39). (H)

### 1.6 Profile D — Khan ez-Zeit (north part, y 430-496)
Photos: D41 (2015, 08:59, shops closed, ~y 470-490), D39 (2019, the fork end), D40 (street sign), D42 (Ja'far
Sweets), D38 (2019, the vaulted part further south at y ≈ 398, for the vault type).
*[Review: D39 is mis-identified. Despite its Commons title it shows the **foot of the Damascus Gate street looking
N**: a ~8 m wide street with steps and herb sellers on the right (E) and the blue-framed Taha greengrocer with its
yellow fascia on the left (W), as in D28. It is profile C evidence, not Khan ez-Zeit. KeZ north rests on D41
(plus D40/D42 details, D38 from outside the sector).]*
- **Width**: OSM wall-to-wall **5.5-9.4 m** at the fork mouth (y 482-494), then **4.1-4.3 m** for y 430-466 (H).
  The photos agree: ~3.5-4.5 m with **raised stone thresholds 0.15-0.20 m x 0.4-0.6 m** along the shop fronts on
  both sides (H: D41).
- **Coverings**: **pointed barrel vaults** (rubble/ashlar, plastered and whitewashed, darkened by soot) over
  some bays. Open bays between them are roofed by **corrugated metal shed canopies from both sides** with a sky
  slot. At least one vaulted section lies at the north entrance (D41, taken 50 s after the fork photo D22, so
  within ~40 m of the fork). Further south the souq is fully vaulted with transverse arches. The vaults carry
  **aluminium flexible AC ducts** and cables, and a big dark metal lantern hangs on a chain. (H: D41, D38; position
  of the first vault **M**)
- **Floor**: large rough grey limestone slabs (~0.3-0.4 x 0.6-1.0 m) in courses across the street, with a
  pitted, slightly dished centre. Round **cast-iron manhole covers (~0.7 m, Hebrew/Arabic ring lettering)** sit in
  black asphalt patches, with square steel grates. Gentle slope, no steps in the north part. (H: D41)
  *[Review: the slope rises **southward ~3 m** from the fork (743.9) to y 430 (747.0), ~4-5 %, steepest in the
  first 25 m (744.9 at y 490, 745.7 at y 470; street-level terrain). That is a noticeable ramp, not near-level.]*
- **Closed shop fronts** (D41, the best reference):
  - openings ~2.2-3.0 m wide x ~2.8-3.2 m, flat steel lintels under the vault springing;
  - **multi-leaf steel doors: 4-6 tall narrow leaves (~0.45-0.6 m) each with 2-3 raised rectangular panels**,
    surface hasps and padlocks, painted **grey, beige, olive**; one **bright yellow** with a diagonal two-tone
    paint job;
  - Ja'far Sweets: **orange-red two-leaf steel doors with Z-shaped flat-bar bracing** and a
    **circle-pattern wrought-iron transom** (D42);
  - a projecting old stone corbel block (balcony base) on the east wall, grey downpipes, water meters.
- **Signs**: white boards with black Arabic and phone numbers ("أبو ... 02-6283947"), green tin signs, hung
  flat under the canopies at ~3 m. **Street plaque** at the north entrance: white glazed tiles, gold ornamental
  border, "רחוב בית הבד / سوق خان الزيت / KHAN AZ-ZAIT ST.", plus a **navy PAMI heritage plaque with teal bands**
  ("Souk Khan al-Zeit Street", QR code). Both sit just above a vault springing (D40). (H for design, M for position)

### 1.7 Profile E — Al-Wad north (fork -> y 430)
Photos: D43 (from the gate roof looking SE along it), D31 (from the wall walk), D14 (2019, just south of the
sector at (380,423), looking SE), D44 (vault detail), D15 (minaret at the end of the view).
*[Review: D43 and D31 show the Damascus Gate street, not Al-Wad. The triangular-pipe parapet of the W-side
building at the foot of that street (D30) is at the far end of the covered stretch in both, and D31 has steps
under the walkers. D15 is a rooftop telephoto, not a view along the street. That leaves **D14, 6.8 m outside
the sector**, as the only street-level Al-Wad photo.]*
- **Width (OSM)**: **5.3-7.6 m** in the first 30 m from the fork. Then ~6 m at y 455-461, a **pinch of 3.4 m at
  (341,464)**, open sides at (348-356, 445-455), and 2.4-4.9 m at y 424-438 (the boundary). (H)
  *[Review: re-measured perpendicular building-to-building. It is 8.9-17 m at the mouth, then **4.7-5.5 m** for
  (316-325, 485-493) between w1393419059/58/56 (NE) and w1393172388 (SW). The SW side is then unmapped/open
  for ~6 m at (327-331, 477-482) before the roof. 6.0-6.2 m at (343-345, 458-461) and 3.5-3.7 m at (340-342,
  463-466) confirmed. Caution: OSM building **w1393172389 clips the Al-Wad centreline by ~1 m at (358-361,
  438-442)**. Keep a ≥3 m clear passage there.]*
- **Covered section**: OSM `building=roof layer=1` w1393280745 spans Al-Wad for **7.7 m at (331-337, 469-477)**:
  a sabat or vault over the street (G). From above, the first 60 m are roofed by **green corrugated sheets and
  blue-white striped awnings** from both sides, leaving a narrow slot (D43, D31). (H for the sheet roofs, M for the
  vault)
  *[Review: corrected. D43 and D31 show the **Damascus Gate street** (profile C), not Al-Wad (see 1.5), so the
  sheet-roof claim for Al-Wad has **no photo**, UNVERIFIED. The OSM roof is ~7.5 m along the street x ~4.2 m
  across. `building=roof` means an open-sided roof in OSM, so a vault with a room above is only one reading (L).]*
- **Floor**: limestone slabs, **grey and ochre, smooth and polished, in running bond with paler bands**. No
  sett ramp is visible beyond the fork. The street **descends steadily SE** (SRTM 754 at the fork -> 750 at y 435,
  ≈ 4 m over 75 m ≈ 5 %), with occasional single steps. (M: D14, D43)
  *[Review: street-level terrain gives 743.9 at the fork -> 743.1 at (342,463) -> 740.8 at (363.6,435.1),
  ~3 m over ~80 m ≈ 4 %. D43 does not show Al-Wad. D14 is taken 6.8 m **outside** the sector at (380,423), so
  every ground-level detail of profile E (floor, shop fronts, lighting) is extrapolated from just south of the
  boundary: M-L. No photo in the set shows Al-Wad between the fork and y 430 at street level.]*
- **Closed shop fronts**: **white-painted panelled double doors** (3 raised panels per leaf) in green steel frames,
  ochre/rust steel doors, roll-down shutters. Spice and olive-oil shops have painted fascia boards ("زيت زيتون /
  بهارات"). Loofahs and goods hang on hooks, and **bare-bulb pendant lamps** hang in white shades. (M: D14)
- **Lighting**: black **L-shaped wall brackets with box lamps** at ~4 m. **Black square steel bollards (~1 m)** at
  the wall foot. (M: D14)
- **Vault detail**: the vaults over Al-Wad have **round ventilation holes (~0.6-0.8 m oculi)** with cables strung
  across them (D44, position on Al-Wad unknown, L).
- **View south out of the sector**: the street runs along the **high rubble garden wall of the Austrian Hospice**
  on its NE side, ~8-10 m high, caper plants in the joints, a mesh fence and **palms** on top. The OSM garden
  w291224780 and trees 12890244023/5, 14093263166 lie at (397-406, 421-424). In D15 the **green-capped minaret
  at (412.9,379.3)** (OSM node 5921367466) closes the view. (M: D14 + OSM garden; minaret bearing 132.5° from the
  D15 camera matches)
  *[Review: the minaret ID from D15 is confirmed (bearing 132.5° from the D15 camera; the Dome of the Rock at
  127.8° gives f ≈ 7000 px, which puts the minaret at x ≈ 1150, as observed). But D15 is a rooftop telephoto from
  the northern wall, not a street view. **The street view down Al-Wad, D14, shows no minaret.** Its end is closed
  by a stone building with a roof terrace and a pointed arcade at street level (the Via Dolorosa junction). So
  "closes the view" is unsupported, and the minaret (6 m off Al-Wad, ~50 m south of the sector) is outside the
  sector. The garden wall height ~8-10 m is also doubtful: next to the ~1 m bollard at its foot in D14 it
  reads ~6 m. Use 6-8 m, M-L.]*

### 1.8 Profile F — stepped residential lanes
Photos: D45 (Muna Court at the top of Sheikh Lulu / start of Al-Sa'diyya, camera (368.6,599)), D31, D32 (roofs).
OSM width statistics (wall-to-wall where both sides are mapped): Sheikh Lulu Ascent min 2.2 / p25 3.7 m;
Rassas Ascent 2.5 / 3.4 m; Ibn Jarrah 3.1 / 3.3 m (median 4.7); Al-Sa'diyya 2.9 / 4.3 m (median 5.0); al-Malawiya 3.5 /
4.7 m; Ash Sheikh Rihan 2.1 / 3.8 m; Aqabat Er-Rahbat down to 1.6-2.0 m. Medians are inflated by unmapped
courtyards. **Use 2.5-4.5 m.** (H)
- **Steps**: broad limestone steps with long risers **~0.15-0.18 m** and treads **~0.8-1.5 m**, often in short runs
  of 3-6 with paved landings. They are laid unevenly, some blocks tilted, with manhole covers on the landings.
  Sheikh Lulu Ascent is tagged `ramp=yes`: model a **0.8-1.2 m smooth ramp strip** along one side. **HaTut** w26506006
  is a single run of **40 steps** (`ramp=no`) climbing W from Al-Wad at (364,435) to (345,419). (H: D45, OSM)
  *[Review: HaTut climbs **SW** (bearing ~236°, then SSW), and its upper end (344.7,418.6) is outside the sector.
  The street-level terrain gives a 6.3 m rise (740.8 -> 747.1), consistent with 40 x 0.16 m.]*
- **Edges**: **low rough-faced ashlar parapets (~0.8-1.0 m, thick coping blocks)** where the lane runs along a
  drop, with graffiti scrawls. (H: D45)
- **Houses**: 2-4 storeys; ashlar lower floors, **whitewashed or cream-plastered upper additions**. **External
  steel stairs** (black stringers, open treads, thin railings), **steel-railed balconies and porches with
  corrugated roofs**, round-arched and flat windows with iron grilles, a round-headed window with a fanlight,
  **pointed and round-arched doorways with dark steel doors**, satellite dishes, laundry, potted plants. (H: D45;
  roofs D31, D32)
- **Lighting**: round wall bulkhead lamps on short brackets, cables strung from house to house at 4-6 m. (M: D45)
- **Clutter**: a wooden snack cart on small wheels ("Corn No.1"), a motorbike, plastic crates, plants. (M: D45)

### 1.9 Profile G — vaulted passages and sabats
- OSM roofs `layer=1` over lanes (see 1.2) mark **short covered sections 7-12 m long**: model them as **pointed
  barrel vaults** in rough plastered rubble springing at ~2.5-3 m, crown ~4-4.5 m, with a room above. Some have a
  round vent hole (D44). Lighting: a bulkhead lamp or a bare bulb. (M: D41, D38, D44; positions H from OSM)
  *[Review: the positions are OSM-H, but the form is **L for these specific roofs**. OSM `building=roof` means an
  open-sided roof (a canopy or shelter), not necessarily a vault with a room above. No photo in the set shows any
  of the four tagged roofs; D41/D38 are Khan ez-Zeit vaults and D44's location is unknown.]*
- `layer=-1` footways (w257604169 from the inner court (269.9,544.5) S to (267.1,498.8), w123254014, w257604180)
  are underground or under-building routes. w257604169 is the route under the inner square (Roman level). These
  are **not walkable at street level**. (L)

---------------------------------------------------------------------------------------------------------------

## 2. Landmarks

How each position was confirmed is given as **[pos: ...]**.

### 2.1 Damascus Gate (Bab al-Amud) w616186088
Full description in section 3. **[pos: OSM footprint + D08, D12, D13. All show the entrance centred between two
projecting towers with the police booth in front of the right-hand (west) tower and the Roman arch at the foot
of the left (east) side. D12's camera geotag (248.6,610.6) gives bearings to the east-tower corner (152.9°),
threshold (161.8°) and west-tower corner (173.6°), which reproduce the image order and spacing (~22 px/deg). H]**
*[Review: the position and orientation are confirmed (OSM footprint plus D08, D12, D13, D20, D26). But the D12
spacing claim holds only for the three inner points. At 22.7 px/deg the geotag puts the east tower's outer
corner (279.7,578.2) off-frame at x ≈ -17, while D12 shows it at x ≈ 190, and the west outer corner at
x ≈ 1112 vs ≈ 1012 observed. A free fit at the geotag (corners + police booth + olive tree) gives f ≈ 970 px
(~18 px/m at the threshold, rms ~30 px), not 22.5 px/m. **D20** fits OSM well at its own geotag (231.6,591.0):
5 corners, rms 8 px, f ≈ 910 px, 19.2 px/m at the threshold. A grid search keeps it in 19-21 px/m, so D20 is the
better scale photo (see 3.2).]*
- Facades and what they face:
  - e3, e5, e6, e8 (face 318°): the **outer facade onto the bridge and plaza**;
  - e4 (east tower flank, faces 228°) and e7 (west tower flank, faces 48°): the flanks either side of the bridge;
  - e15, e16 (face 138°): the **inner face onto the inner square** (Damascus Gate street);
  - e10 (251.2,541.6)->(261.0,550.3), 13.0 m, faces 138°: the **west tower's inner face onto the small inner court**
    (D06);
  - e0 (285.4,560.7)->(277.6,569.4), faces 48°: the east tower's inner side along **Sheikh Lulu Ascent**;
  - e9 (faces 228°): the west tower's outer flank above the park outside the wall.

### 2.2 Roman gate (Aelia Capitolina north gate, eastern side arch) and the Roman courtyard
Photos: D18 (2025, arch close-up), D19 (2019, the sunken courtyard), D05 (plaques), D13 (arch crown from the
plaza), D07 (inside the Roman tower).
**[pos: OSM node 9362751619 "Tenth Roman Legion mark - under bridge" at (259.7,567.7), 2.9 m NE of the bridge
centre-line. D13 shows the arch crown on the left (NE) side of the bridge deck at its gate end. D19 shows the
courtyard below a concrete deck with railings (the bridge/terrace). H]**
*[Review: position CORRECTED. Node 9362751619 is a Legio X **inscription** "under bridge", not the arch. It lies
**2.0 m** NE of the centre-line and 11.1 m out from the threshold, i.e. *under* the ~7-7.5 m deck (half-width
~3.7 m). The arch is outside the deck. In D13 its crown shows *beyond* the NE parapet, which places it
further from the camera than the parapet, at the foot of the gate wall left of the door pier. In D19 the deck
is overhead to the *right* of the arch, so the deck is SW of it. Model the arch in the sunken court **NE of the deck,
at or within ~2 m in front of the curtain e5**: centre ≈ (269.5-271, 562-564), about 5.5-7 m NE of the axis,
facing ~318° (NW). OSM exit stair w616178281 starts at the curtain/tower junction (273.6,565.1), which fits a
court there. Position M (two photos, no OSM node for the arch itself).]*
- A **round arch ~2.5 m wide, ~4.5 m to the crown** (M). Voussoirs are large with a projecting keystone under a
  **triple-fascia moulded archivolt**. It springs from **moulded impost blocks on plain pilasters**, with big
  Herodian-style drafted blocks either side and the moulded base of a column pedestal at the left.
  Pale grey-white weathered limestone with moss and plants. (H: D18, D19)
- 2025: a black sign board inside the arch, "שער העיר | City Gate | بوابة البلد", with a gold arch logo, leads to a
  visitor centre. In 2019 the arch had a dark plaque. (H: D18, D19)
- **Sunken courtyard** in front, ~4-5 m below the bridge deck: paving of small limestone slabs, a long steel drain
  grate, loose column fragments, rough rubble walls with plants. Under the deck there is a barred window.
  **Four information plaques** hang on the rubble wall right of the arch: navy "שער שכם / Damascus Gate /
  باب العمود" (x2), a **brown "טיילת החומות / The Wall Walk / متنزه السور"** visitor-hours board (09:00-16:00
  winter / 17:00 summer, Fr closed; 10 / 15 / 20 NIS), and navy "The Roman Gate / השער הרומי / الباب الروماني"
  with a coin image. Each is ~0.6 x 1.5 m. (H: D05, D19)
- Interior of the Roman tower: huge drafted ashlar, 1.0-1.2 m courses, heavily weathered and stained (D07). (M)

### 2.3 Sabil Bab al-Amud (fountain niche in the plaza retaining wall)
Photos: D36 (frontal from the plaza floor), D35, D11 (from the gate top).
**[pos: OSM retaining wall w1547495755 segment (231.7,586.3)->(242.6,595.5): 14.3 m long, its normal faces 140°,
i.e. straight back along the bridge axis (the axis extended NW from the threshold hits this segment at
~(237,591)). D36 shows the niche centred in a wall with a stair run on each side, matching the west run
w217547844 to its left and the central run w617363480/471 to its right. D11 (from the gate) shows it on the far
retaining wall straight ahead. M-H]**
- A **pointed-arch niche ~2.5 m wide x ~3.5-4 m tall** under a **stepped, joggled hood (chevron outline)**: a dark
  recess with a small basin and spout, flush in a smooth pale ashlar retaining wall ~4 m high. It stands on a stone
  platform reached from the terraces. (M: D36, D35)
- *[Review: the position is confirmed. The bridge axis extended meets the segment at (236.2,590.1), 41 % along
  it, and D36 shows the niche at ~51 % of the wall. The **name "Sabil Bab al-Amud" is UNVERIFIED**: OSM has no
  feature here, and no photo caption names it (D36's caption is just "أدراج باب العامود", Damascus Gate
  stairs). The 1536-37 Suleiman sabils are not recorded at this gate. Call it a "fountain niche" (likely part
  of the 1980s forecourt) unless a source is found.]*

### 2.4 Police booth (outer plaza, in front of the west tower)
**[pos: OSM node 5827808684 `amenity=police` (253.6,559.5), SW of the bridge. D08, D12, D13 and D26 all show
it just right (SW) of the bridge in front of the west tower. H]**
- A small **grey steel kiosk ~3 x 3 m** with large windows, mesh panels below, grey posts and a **shallow
  pyramidal grey sheet-metal roof with a white ridge trim**. It stands on a raised stone platform over the sunken
  area, with a short steel stair and handrails. In 2019 it had a white pyramid roof (D08). (H)
- A second police hut (OSM node 5825913081 `building=hut` at (258.8,609.9)) stands at the top NE corner of the
  plaza on Sultan Suleiman St (OSM only, L).

### 2.5 Inner portal and inner square
See 3.7. **[pos: OSM e15/e16 + D01, D29 (looking N up the steps), D24 (oblique from (289,549)). H]**

### 2.6 The fork building (between Khan ez-Zeit and Al-Wad), w1393419054 and neighbours
**[pos: OSM: w1393419054 (305-312, 488-493) sits in the angle of the fork. D22 (looking S from the foot of the
Damascus Gate street) shows the vista closed by this terrace of buildings with the two streets leaving on either
side. M-H]**
- A small 2-3 storey block with a **white-balustered roof terrace**, a tiny **red-tile gable roof** on a roof
  room, a blue tarp, a green-white checked awning at street level and shop signs (the yellow "طه للخضار والفواكه"
  greengrocer and the green Halawani sweets sign face it). The roof carries solar heaters, water tanks, an
  antenna mast and dishes. (H: D22, D28)
- *[Review: the Halawani and Taha shops do not "face" the fork building. They are on the W side of the Damascus
  Gate street at y ≈ 500-506, facing E, at right angles to it (see 1.5). w1393419054 is tiny (24 m², 6.6 x 4.3 m);
  the vista block in D22 probably includes w1393172387 behind it. The fork position is H from OSM, and the
  building identification in D22 is M.]*

### 2.7 Sheikh Loulou Mosque (Masjid ash-Sheikh Lulu)
**[pos: OSM node 5861210088 (302.6,555.9), inside building w1392390329 (296.7-318.0, 554.4-569.0, 120 m²), on the
north side of Sheikh Lulu Ascent ~25 m east of the inner exit. No photo in the set. L]**
- Footprint edges: e0 (298.9,554.4)->(312.5,559.4), 14.5 m, faces 160° onto Sheikh Lulu Ascent; e3 (314.1,569.0)
  ->(296.7,557.2), 21.0 m, faces 326° toward the wall. Model as a 2-storey Mamluk-Ottoman ashlar building with a
  pointed-arch doorway on e0. Add **no minaret** unless confirmed: no nearby minaret shows in the views from
  the gate roof and the wall walk over the roofs SE of the gate (D43, D31). Those views do not cover the mosque
  well, so this stays L.
- *[Review: OSM geometry CORRECTED. w1392390329 is **south** of Sheikh Lulu Ascent, not north of it. The ascent
  runs (283.4,567.3) -> (303.5,583.6), 17-21 m NW of the building, with building w1392390322 (287-313, 557-580)
  between them. e3 (faces 326°) is the side toward the ascent but is 4.0 m from w1392390322. **e0 (faces 160°)
  does not face the ascent.** It faces a 2-5 m unmapped gap along the north side of the big block w291225673,
  and that gap opens W onto the NE corner of the inner square near (290-297, 548-557). The 3.5 m e4 (faces 231°)
  also faces the inner square. So the entrance is most plausibly on e0 or e4, reached from the inner square, and
  stays L. Alternatively the OSM node is misplaced by ~15 m and the mosque is the ascent-fronting w1392390322
  (e3/e4 face 32°/318° onto the ascent). Unresolved without a photo.]*

### 2.8 Masjid al-Mustafa (OSM name "مسجد الهصطفى")
**[pos: OSM node 5835976784 (281.5,469.9) inside w1393419051 (274.7-284.3, 467.8-477.0). It is reached from the
unnamed lane w257604182 west of Khan ez-Zeit. OSM only, L]**. Treat as a plain neighbourhood mosque with a
green-painted door and a small sign. No minaret seen. (L)

### 2.9 Ja'far Sweets, Khan ez-Zeit
**[pos: D42 camera geotag (311.6,435.5), on Khan ez-Zeit (x ≈ 306 at that y), facing the shop. It is a
well-known shop on the street. Position M (one photo with a geotag)]**
- A **blue fascia board with white vertical pinstripes, big red serif letters "JA'FAR SWEETS"** and a red-white
  **eagle emblem with an Arabic scroll** (~4 m long x 1.2 m). Below it **orange-red Z-braced steel doors** and a
  circle-pattern iron transom. Inside: granite cladding and a sweet counter. A corrugated canopy with an LED
  floodlight is above. (H for the look)
- *[Review: position downgraded to **L**. It rests on a single phone geotag taken inside a covered souq, where
  GPS errors of 10-20 m are common. The geotag sits 5.4 m E of the KeZ centre-line, inside east-side building
  w1393280743. The side of the street is unknown, and the shop may lie south of the sector boundary (y 430,
  only 5.5 m away).]*

### 2.10 Backdrops seen from the sector (outside it, but they define the views)
- **Hindiyeh building** across Sultan Suleiman / HaNevi'im junction: 3-4 storey cream stone block with **paired
  and triple round-arched windows**, iron balconies, rooftop signs. It rises above the sabil wall in every view
  leaving the gate. (H: D35, D36, D11) *[Review: the building and its look are confirmed; the name "Hindiyeh" is
  UNVERIFIED (no OSM name, no caption).]*
- **Schmidt's College / Paulus-Haus** NW of the gate: crenellated stone building with a **round corner turret**
  among palms and cypresses (D35 right). (M)
- From the gate roof and the walls: the **Dome of the Rock** gold dome (bearing ~128° from the wall walk), the
  Austrian Hospice roof with the **Austrian (red-white-red) and Vatican flags**, the Lutheran Church tower and the
  Holy Sepulchre domes to the SW (D15, D32, D43). (H)

---------------------------------------------------------------------------------------------------------------

## 3. The gate (Damascus Gate / Bab al-Amud / Sha'ar Shkhem)

Photos: D08 (2019, from the plaza), D12 and D13 (2025-12, from the plaza top; D12 used for measurements), D26
(night, frontal), D04 (2019, upper part from below), D09 and D10 (window close-ups), D21 (bartizan close-up), D03
(door leaf), D02 (passage), D01, D24, D29 (inner face), D06 (west tower inner face), D23, D25, D16, D33 (roof and
wall walk), D17 (ivy).

### 3.1 Plan (from OSM, H)
- Overall front ~46 m along bearing 48°/228°. The west tower front is 12.5 m, the curtain 19.8 m, the east tower
  front 13.3 m. The towers project ~6 m in front of the curtain. The block is ~14-20 m deep (front to the inner
  face). *[Review: measured along 138°, it is **11.1 m from the curtain to the inner face**, ~16.7 m from the east
  tower front to the inner face, and the west tower is 8.8 m deep (e9). The passage path is 14.1 m.]*
- The city wall leaves the **west tower from its SW side** at (251.2,541.6) toward the SW (w391433919). It leaves
  the **east tower from its NE corner** at (285.6,571.6) toward the NE (w137726904). *[Review: w137726904 meets the
  footprint at (283.2,574.3), the e1/e2 vertex on the east tower's NE flank. (285.6,571.6) is the wall's next
  vertex, 3.6 m outside the footprint.]*
- The photos agree: towers + recessed curtain, doorway centred, both towers about equal (H: D08, D12, D26).

### 3.2 Masses and heights (above the outer threshold)
Measured on D12 at ~22.5 px/m at the facade. The scale comes from the angular scale between OSM points and the
distance from the camera geotag. It is cross-checked with people on the bridge and with D13. (M)
| item | value | conf |
|---|---|---|
| doorway (rectangular) | **w 3.6-4.4 m, h ~5.2 m** (flat lintel) | M (D12, D13, D03) |
| outer arch (moulded pointed) | outer width ~5.5-6.5 m, springing ~6.5 m, apex ~9.2 m | M |
| window above the arch | opening **1.1 x 2.0 m**, sill ~11 m | M (D10 scaled by a seated person) |
| curtain parapet (base of merlons) | **~14 m** | M |
| merlon finial tips | **~16 m** | M |
| towers | same parapet height as the curtain or ~0.5 m higher, bartizans at the top | M |
| bridge deck to Roman courtyard | ~4-5 m | M (D19, D13) |

*[Review: the table above is superseded by the one below. The D12 scale of 22.5 px/m is too large, so heights
measured on it come out 6-15 % low. Separately, the 1.1 x 2.0 m window (from a seated person in D10) does not fit
the facade proportions.*
*Method: ratios were measured on three photos, D12, D20 (frontal) and D26 (frontal). They agree, with w = doorway
width: lintel ≈ 1.32-1.40 w; window sill ≈ 2.62-2.64 w; window ≈ 0.21 w x 0.37 w; parapet (crenel bottoms) ≈
3.73 w (D12, D26) or lintel + 2.07 w (D20); finial tips ≈ 4.24 w.*
*Absolute scale: D20 was resected at its geotag, giving 19-21 px/m at the threshold, which makes w = 4.2-4.6 m
(87.5 px). An independent check: a man at the doorway in D13 is 110 px tall against a 272 px opening, which
gives w ≈ 4.1-4.3 m. D12 people near the door, corrected for standing in front of it, give 3.9-4.4 m.]*

| item (review values) | value | conf |
|---|---|---|
| doorway (rectangular) | **w ~4.3 m (4.1-4.5), h ~5.9 m (5.5-6.3)** to the flat lintel | M (D13 people, D20 resection, D12/D26 ratios) |
| outer arch | moulding outer width ~7 m (6.4-7.6), clear opening ~6 m, springing ~7 m, outer apex ~10 m | M (D20, D04) |
| window above the arch | opening **~0.95 x 1.6 m**, sill ~11 m | M (D20, D12, D26 ratios; D10's seated person overstates it) |
| curtain parapet (crenel bottoms) | **~15 m (14.2-15.9)** | M |
| merlon finial tips | **~17 m (15.9-17.9)**; central turret top ~17.5 m | M |
| towers | same parapet height as the curtain or ~0.5 m higher | M |
- **Masonry**: coursed smooth-dressed cream limestone ashlar, courses ~0.4-0.6 m, blocks 0.6-1.5 m long, thin
  joints. Faces are **pitted and honeycombed** by weathering (strong in D21) with grey-brown streaks. There is no
  batter. The lowest courses at the bridge level are darker and older. (H: D04, D21, D12)
- **Ivy (since ~2023)**: a dense ivy mass covers the curtain between the doorway and the west tower. It starts
  ~2 m right of the doorway jamb and runs from about bridge level (it grows up from the sunken area) to ~12 m,
  spilling onto the tower face. It was absent in 2019 (D08, D20). Model the 2025 state with ivy. (H: D12, D13, D17)

### 3.3 Outer portal and doors
- **Arch**: a tall **pointed arch with a broad moulded archivolt** (a roll between flat bands), springing from
  plain jambs. A **small carved rosette sits at the apex** of the moulding. The recess under the arch is
  ~0.8-1.2 m deep. Its tympanum above the doorway lintel is plain ashlar with a horizontal panel. An Ottoman
  foundation inscription (944 AH / 1537-38) is reported there but is not legible in these photos. (H for the
  arch, L for the inscription)
- **Doorway**: rectangular, flat lintel, ~4 x 5.2 m *[Review: ~4.3 x ~5.9 m, see the 3.2 review table]*. It
  opens straight onto a wall with shops ~5-6 m inside, which shows the zig-zag of the passage. (H: D13)
- **Door leaves** (open, folded back inside the passage): **two leaves, each ~2.0 x 5.0 m, of timber clad in
  horizontal iron strips ~0.15-0.2 m wide covered in dense round nail heads** (~10 cm spacing). They are dark
  rust-brown with pale dusty upper parts, a big square lock box, and a vertical iron edge bar. The bottom corner is
  broken away to show the timber frame. The leaf rests in a recess beside a **moulded impost (cyma profile)**.
  (H: D03)
- On the jambs: grey poles with "no entry" discs and yellow time plates, CCTV, small lamps (D13).

### 3.4 Decoration of the outer face
- **Window panel over the arch** (centred, H: D04, D08, D12, D09, D10): a raised rectangular panel ~2.6 m wide
  from just above the arch apex up to the central box machicolation. It contains:
  - the **rectangular window 1.1 x 2.0 m**, open to the sky (it is a screen wall, see 3.8) *[Review: ~0.95 x
    1.6 m. Scale the other panel dimensions in this list by ~0.85, e.g. panel ~2.2 m wide, central
    machicolation ~1.65 m]*;
  - a **pair of engaged colonnettes** with carved **interlace / braided-knot** sections and fluted shafts, under
    **foliate (acanthus) capitals**;
  - a **joggled lintel** above the opening (cusped, interlocking voussoir profile, one colour);
  - above that, a **frieze of 5-6 small cusped (trefoil) arches** on miniature consoles (muqarnas-like corbel
    table), topped by a **band of palmettes**.
- **Roundels and rosettes** (H: D04, D12, D24, D26):
  - **two plain stone discs (~0.7 m)** flank the window panel at window-head height;
  - **two carved rosettes (~0.8 m, geometric star / interlace pattern in a ring)** flank the arch at about its
    haunches;
  - more plain discs are scattered on the tower faces (D12: about 4 per tower at 2-3 levels).
- **Arrow slits**: tall narrow slits (~0.12-0.15 x 1.5-2 m) on both towers and the curtain at two levels, some
  with small round ends. (H: D04, D08, D12)

### 3.5 Top: merlons, machicolations, bartizans
- **Merlons**: rectangular blocks ~1.5-2.0 m wide x ~1.2-1.5 m, each with a **stepped top carrying one or two
  pointed finials** (cone or pyramid on a short drum with a knob, ~0.6-0.8 m). Some merlons have a vertical
  slit. Crenels are ~0.5-0.8 m. Finials are smaller and denser than at Jaffa Gate and give the gate its
  "spiky crown". (H: D04, D08, D12, D16, D21, D33)
- **Central box machicolation** over the window panel: ~1.9 m wide, projecting ~0.6 m, with two openings. It
  rises above the parapet as a small square turret with **its own miniature crenellation (small square
  teeth)**. (H: D04, D12)
- **Small box machicolations** on corbels at parapet level, one each side of the central part, with slits and a
  finial above. (H: D04, D08)
- **Bartizans** (corner box machicolations) at the top **inner corners of both towers**, facing NW: boxes ~2 m
  wide projecting ~0.7-0.8 m on **three or four corbels of 3 stepped courses with a cyma profile**, a slit in
  the front, and a merlon with finial above. (H: D12, D20, D26, D21)
- **Night**: floodlit warm white from the bridge and plaza. During Ramadan there are **green crescent-moon
  rings** on the merlons and many strings of white lights fanning out to the plaza. (H: D26, D20)

### 3.6 Passage interior
- Bent route (3.1). The chamber inside the outer doorway is **vaulted with a pointed cross vault**, washed
  pale yellow / ochre, crown ~7-8 m (L), over large polished limestone floor slabs. (M: D02)
- The chambers are **lined with shops** (phone accessories, bags, sweets) under **slatted timber/steel canopies
  painted orange** and **yellow-painted steel hook racks**. There are **LED floodlight panels** on brackets, bare
  bulbs on wires, CCTV domes on a pipe and white tarps under the vault. A shop at the end wall has the **"BIG BEN"
  fascia** (Arabic "المسك بج بن") under a pointed arch. A white utility cabinet stands by the door leaf. (H: D02, D03,
  D13; OSM shops: bureau de change node 5825980087 (266.3,554.1), confectionery node 5827442885 (271.2,550.4))
- The **side passage** w616338411 to the west tower (gate node 5827442886 at (263.7,550.2), a barrier) leads to
  the inner court (3.7).
- Exits: a **full-height turnstile (exit only)** node 5825913082 at (280.3,565.0) on steps w616178281 links the
  Roman level near the east tower to Sheikh Lulu Ascent. (OSM only, L)

### 3.7 Inner face, inner square and inner court
- **Inner portal** (e15/e16, faces SE): a tall plain ashlar block ~13-14 m wide with **one big pointed arch**,
  opening ~4-5 m wide (M). It has a **double moulded archivolt**, **three small rosettes** in a row above the apex
  and two larger plain discs either side. The parapet at **~10 m** carries a **black steel railing** (roof terrace)
  and small plants. Behind it the taller outer screen with its finials shows above (D29, D01). A low crenellated
  wall with a railing continues NE. Tarps, a striped awning and shop stalls fill the arch. CCTV, a lamp and cables
  are on the face. (H: D01, D24, D29)
  *[Review: in D29, people at the arch are ~70 px tall against a 148 px opening at the springing. That suggests
  an opening of ~3.5-4 m and a cornice at ~8 m, with the railing top at ~9 m. This is one photo with people on
  steps, so use an opening of 3.5-4.5 m and a parapet of 8-10 m (M-L).]*
- **Sign at the inner portal**: a **ceramic tile plaque "שער שכם / باب العامود / DAMASCUS GATE"** (white tiles,
  dark lettering, brown border, ~0.8 x 0.5 m) and a **navy PAMI heritage plaque with a teal accent** ("Damascus Gate",
  three languages, ~0.5 x 0.6 m) on the pier at the top of the steps, ~2.5 m up. (M: D27)
- **Inner court west of the exit** (around (262-272, 535-549), reached by OSM footways w616338413 / steps w616338420 /
  w616338418): the **west tower's inner face e10** (13 m wide, plain ashlar, plants on top, a steel railing on the
  roof edge) and an arched doorway at its east end (the covered side passage). Furniture: a long stone plinth
  bench (~6 x 0.8 m), **grey concrete cylinder bollards (~0.45 m)**, a slotted grey bin, a grey-white drinking-water
  cooler, plastic café chairs and a table, and **three tall light-grey square poles** with stencilled numbers
  "236 201", "236 214". Public toilets node 4438652489 (263.1,537.4). (M: D06 + OSM footprint e10 matches the
  13 m face; position M)

### 3.8 Roof terrace and wall walk (seen from the street as railings and silhouettes)
- The outer facade is a **screen wall rising well above the roof terrace**. Its window (3.4) opens to the sky.
  Behind it the roof is a **paved terrace (small limestone setts)** with arcaded walls, pointed-arch openings
  and stairs to the parapet walk with **galvanised railings**. A wooden pyramid skylight frame and a bronze
  figure sculpture (2025) stand on it. (H: D25, D16, D10, D23)
- The **Ramparts Walk** continues W and E along the wall top with grey/black railings. Visitors' heads show above
  the parapet from the street. (H: D23, D33)

### 3.9 Outside the gate (plaza edges not covered by profile A)
- **East side (left of the bridge)**: a stair and ramp down to the Roman courtyard (2.2), black railings, the
  big olive tree (4.4; it stands ~30 m out on the upper plaza, 25 m NE of the axis, not beside the courtyard) and
  the green strip with benches along the wall NE (OSM park w291225672 and benches).
  (H: D08, D12, D13)
- **West side (right of the bridge)**: the police booth (2.4), the sunken area below it, then the park w290826799
  along the outside of the west wall (lawn, palms, olive trees, tree row w1547527574). (H: D08, D12)

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

### 4.1 Lamps and lighting
- Plaza rim: **tall slender grey poles (~8-10 m)** with small top-mounted LED heads along Sultan Suleiman St, plus
  traffic-signal poles at the crossing (OSM signals 11483219843/4 at (255.6,629.0) and (249.4,623.7)). (H: D35, OSM)
- Inner court: three light-grey square poles (~8 m) with numbers (D06). (M)
- Souqs: **fluorescent tubes and LED floodlight panels** under the canopies, bare bulbs in white shades, festival
  strings. Wall: old box floodlights on arms (D30), black L-bracket box lamps (Al-Wad, D14), round bulkhead lamps
  (residential lanes, D45). (H)
- Gate facade: ground floodlights. Ramadan crescents and strings (D26, D20). (H)

### 4.2 Bins, bollards, benches, booths
- **Grey slotted steel cylinder bins with lids** (~0.5 x 0.9 m, yellow liner bags) on the plaza and in the inner court. (H: D12, D06, D20)
- **Grey concrete cylinder bollards** (inner court). **Black square steel bollards ~1 m** (Al-Wad edge). (M: D06, D14)
- Benches: metal benches with backs and armrests in the green strip NE of the gate (OSM nodes 5900024868 /
  5900026787 / 5900024870 / 5900024874 / 5900026789 at (307-313, 607-628), waste basket 5900024877). No benches on
  the plaza itself: people sit on the terraces. (OSM H; photos M)
- Police booths (2.4). A grey utility box and a water cooler in the inner court. (H)

### 4.3 Signs and plaques (text and design)
| where | text | design | photos |
|---|---|---|---|
| doorway jambs (outer) | Israeli sign 401 "no entry for vehicles" + time plates | white disc, red ring, grey pole; yellow plates | D13, D12 |
| inner portal pier | "שער שכם / باب العامود / DAMASCUS GATE" | ceramic tiles, dark text, brown frame | D27 |
| inner portal pier | "שער שכם / باب العامود / Damascus Gate" + text | navy PAMI plaque, teal accent | D27 |
| Khan ez-Zeit north entrance | "רחוב בית הבד / سوق خان الزيت / KHAN AZ-ZAIT ST." | white tiles, gold ornamental border | D40 |
| same | "Souk Khan al-Zeit Street" + text, QR | navy plaque, teal top and bottom bands | D40 |
| Al-Jabsha corner (near the fork) | "... / طريق الجبشة / AL-JABSHA ST." | tile plaque, darkened, a loudspeaker horn beside it | D39 |
| near the fork, pier (2014) | tourist pictograms "Dome of the Rock", "Via Dolorosa", Western Wall | **faded teal-green glazed tiles with white icons**, 2 x 3 tiles, ~1.0 x 1.4 m, chipped | D37 (geotag (309.4,502.4), M-L) |
| Roman courtyard wall | Damascus Gate (x2), The Wall Walk hours, The Roman Gate | navy and brown boards ~0.6 x 1.5 m | D05, D19 |
| Roman arch (2025) | "שער העיר / City Gate / بوابة البلد" | black board, gold arch logo | D18 |
| plaza west side | black monolith with gold arch logo | black upright panel ~0.8 x 2 m | D12 |
| shop fascias | "HALAWANI 052-2532242" (Fuze tea); "طه للخضار والفواكه"; "NABIL H. BAKERY / نبيل حجازي"; "JA'FAR SWEETS"; "BIG BEN" | green fascia; yellow fascia; cream board on bracket; blue pinstripe + red letters; tan board | D22, D28, D30, D42, D02 |
- Typical shop boards: white or yellow fascia boards with Arabic, an English name and **mobile numbers (05x-...)**;
  blank white boards on scroll brackets; price cards ("80", "50") on A-boards. (H)
- Flags: Israeli flags and a menorah on a few rooftops (seen from the walls, D15). No flags on the gate itself
  in the photos. (M)

### 4.4 Vegetation
- **Olive tree** (large, ~8 m, spreading) at the plaza's east side: OSM tree 5825913094 (262.6,598.1). **[pos: D12
  shows it at the left at bearing ~132° from the camera, 30° left of the gate. D08 also shows it at the left
  foreground. H]**
- **Park outside the west wall** (w290826799 and tree row w1547527574): lawn, **Washingtonia palms**, olive and
  ficus trees (H: D08, D12). Tree row w1547527575 along the outside of the wall NE of the gate (M).
- **Oleander bushes** (pink) in planters on the upper plaza: OSM shrubs 14075308451 (224.8,582.7), 14075308452
  (246.9,601.0) and hedge w1547527573 along the top of the sabil wall. (H: D26, D11, OSM)
- **Ivy** over the curtain right of the doorway (3.2). (H)
- **Wall plants**: caper bushes and grasses on the merlons, parapets and tower tops, and in the joints of the
  Austrian Hospice garden wall. (H: D06, D24, D14)
- Inside the walls: trees at (214-249, 480-534) in courtyards west of the gate (OSM nodes); fig/orange trees in
  courtyards (D32); **potted plants** on porches and balconies (D45). Cypresses and palms on the skyline toward
  the Haram (D15). (M)

---------------------------------------------------------------------------------------------------------------

## 5. Terrain

*[Review: the "street (m)" column is new. It is `data/terrain_street.json` (z_ground + datum 770.58, bilinear),
with OS 1865 anchors in brackets, and it supersedes the SRTM column, which runs 3-10 m high inside the walls.
The 1980s sunken forecourt is not in the street model (docs/TERRAIN.md limitations), so plaza-floor values
come from the bridge and steps.]*

| point | SRTM (m) | street (m) | note |
|---|---|---|---|
| Sultan Suleiman St at the top of the plaza (250,615) | 761 | 757.6 [OS 756.2 at (241.6,617.7)] | the street rises E (OS 761.7 at (278.7,615.1)) |
| plaza floor / bridge foot (250,575) | 757 | ~753 (bridge level; forecourt not modelled) | ~4.5-5.5 m below the street (36 steps) |
| outer threshold (266,558) | 756 | 752.7 [OS B.M. 753.86 at (264.3,561.1)] | bridge nearly level |
| inner exit (275.4,551.8) | — | 751.2 [OS 750.42 at (288.2,551.8)] | the gate sits in a dip (TERRAIN.md) |
| inner square (290,530) | 756 | 748.0 | |
| fork (312,496) | 754 | 743.9 [OS B.M. 744.35 at (312.5,501.0)] | **~6-7 m below the inner exit** (not 3-4 m) |
| Khan ez-Zeit y 490 / 470 / 430 | 755-757 | 744.9 / 745.7 / 747.0 | **rises ~3 m S of the fork (~4-5 %)** |
| Al-Wad (342,463) -> (372,425) | 751 -> 749 | 743.1 -> 739.5 [OS 739.75 at (368.7,425.1)] | steady fall SE (~4 %) |
| HaTut steps (364,435) -> (345,419) | 750 -> 752 (SRTM) | 740.8 -> 747.1 [OS 747.37 at (348.2,413.5)] | 40 steps ≈ 6.3 m, consistent |
| Rassas Ascent (327,509) -> (328,578) | 756 -> 762 | 743.7 -> 760.1 [OS 743.71 / 760.17] | **climbs ~16.5 m over ~93 m (~18 %): stepped** |
| Sheikh Lulu Ascent (277,550) -> (364,601) | 756 -> 769 | 751.2 -> 764.1 | 13 m over 123 m, steps + ramp |
| Al-Sa'diyya (366,596) -> (531,628) | 769 -> 772 | 763.2 -> 768.5 | climbs gently E (~5 m) |
| al-Malawiya (381,500) -> (544,563) | 760 -> 773 | 747.4 -> 762.1 | climbs E ~15 m |
| Ibn Jarrah (418,541) / (366,633) | 769 / 770 | 761.4 / 768.9 | ~7.5 m difference, not level |
| Es-Sayyida Rd (215,470) | 767 | 759.0 [OS B.M. 758.98 at (211.3,475.4)] | west part is higher than the gate (~6 m) |
- **Climbs and descents**: from the gate **everything inside goes down to the fork** and then **down along Al-Wad**
  (the Tyropoeon valley). Khan ez-Zeit stays nearly level. NE of Al-Wad the **residential quarter climbs ~15 m**
  to the Sa'diyya / Malawiya ridge. Muna Court at the top of Sheikh Lulu is called the "highest point of the Old
  City" in the D45 caption (the SRTM figure 770 m agrees it is high). (M)
  *[Review: the caption's claim is wrong. The street-level model gives ~764 m at Muna Court, below the Jaffa
  Gate datum (770.6 m) and the NW Christian Quarter. Treat it only as the local high point of the NE (Bezetha)
  ridge. Khan ez-Zeit is not "nearly level": it rises ~3 m S of the fork.]*
- **Stair runs matched to OSM steps ways**: the plaza runs (1.3); HaTut w26506006 (40 steps, no ramp); Sheikh Lulu
  Ascent w257604166 (steps with ramp); w616178281 (exit stair at the turnstile); w616338420 (2-3 steps in the inner
  court); w616178280 (5 steps, at (310.6,614.4), in the park outside the wall). The Damascus Gate street steps are
  not mapped as steps in OSM (the way is `pedestrian`, `surface=sett`). Model them from 1.5. (H for OSM, M for the
  street)
- **Terraces and platforms**: the amphitheatre terraces (1.3), the raised platform under the police booth, the
  sunken Roman courtyard (~4-5 m below the bridge, 2.2), the inner court a few steps below the inner exit, and raised
  shop thresholds in the souqs (0.15-0.2 m). (H)

---------------------------------------------------------------------------------------------------------------

## Model checklist (prioritised: the 15 things that make the sector read as Damascus Gate)

1. **Gate massing from OSM w616186088**: two ~13 m towers projecting ~6 m either side of a ~20 m recessed curtain,
   facing 318°, doorway centred at (265.8,558.2). Parapet ~15 m, finials ~17 m above the threshold (±1 m; review
   values). The passage is a double right-angle bend with a 2.9 m offset. (3.1, 3.2)
2. **The spiky crown**: stepped merlons each with one or two pointed finials along the whole top. Add the central
   crenellated box machicolation over the arch, the side box machicolations and the corbelled bartizans at the
   towers' inner corners. (3.5)
3. **Outer portal**: tall moulded pointed arch (apex ~10 m, moulding ~7 m wide) with a small apex rosette over a
   rectangular ~4.3 x 5.9 m doorway (review values). Add the open nail-studded iron door leaves folded inside. (3.3)
4. **Window panel over the arch**: ~0.95 x 1.6 m opening (review value) open to the sky, braided colonnettes, joggled lintel, row of
   small cusped arches and palmettes. Add the two plain discs beside it and two carved rosettes at the arch haunches.
   (3.4)
5. **Sunken amphitheatre plaza**: pale stone terraces (0.4 m seats, 0.15 m stair runs) dropping ~5 m from Sultan
   Suleiman St, with galvanised handrails and the stair runs where OSM puts them. (1.3)
6. **Bridge**: 20 m x ~7.5 m, warm mixed small slabs, low ashlar parapets with black railings, no-entry poles at
   the jambs. Add the Roman arch and sunken courtyard to its NE and the grey pyramid-roofed police booth to its
   SW. The arch sits outside the deck at the foot of the curtain, ≈ (270,563), not at OSM node 9362751619, which
   is an inscription under the deck. (1.4, 2.2, 2.4)
7. **Inner street split**: grey sett ramp on the west half, limestone steps (0.15-0.17 / 1.0-1.5 m) on the east
   half. It falls **~6-7 m** (review value; was 3-4 m) from the inner portal to the fork, widening to a 16-21 m
   inner square at the top. (1.5, 5)
8. **Market coverings of the inner square**: canvas sheds, striped scalloped awnings, corrugated canopies, white
   tarps strung across and coloured umbrellas. Add the green corrugated and blue-white striped sheets seen from
   above (D43, D31). Keep the frames, rolled awnings and tarps even with shops closed. (1.5)
9. **The fork**: the island building closing the vista, Khan ez-Zeit leaving S and Al-Wad SE. Add the green
   HALAWANI and yellow greengrocer fascias, crates, the herb sellers' step and the green mini-tractor. (2.6, 1.5)
   Both fascias are on the W side of the street, just N of the fork, facing E.
10. **Khan ez-Zeit closed**: 4-4.3 m wide and rising ~3 m southward from the fork, pointed whitewashed vault bays
    alternating with corrugated canopy bays.
    Rows of multi-leaf panelled steel doors (grey, beige, olive, one yellow), raised thresholds, rough slab floor
    with asphalt-patched manholes, the hanging lantern, the tile street plaque and Ja'far Sweets. (1.6, 2.9)
11. **Al-Wad north**: 4.7-6 m (3.5 m pinch at (341,464)), descending ~4 %. The covering is unverified: no photo
    shows this stretch, and the sheet roofs in D43/D31 belong to the Damascus Gate street. The OSM roof at
    (331-337, 469-477) may be a canopy or an arch (L). Keep the street clear where w1393172389 clips it at
    (358-361, 438-442). South of the sector, D14 shows the Austrian Hospice garden wall on the NE side and a
    terrace-roofed building with a pointed arcade closing the view, with no minaret. (1.7)
12. **Inner portal**: plain block ~13-14 m wide with a parapet at ~8-10 m, one big double-moulded pointed arch
    and three small rosettes, a railing
    on top, the taller outer screen and finials showing behind. Add the tile and PAMI "Damascus Gate" plaques. (3.7)
13. **Masonry and weathering**: honeycombed cream ashlar with grey streaks, plants on the merlons, and the 2025
    ivy mass on the curtain west of the doorway. (3.2, 4.4)
14. **Stepped residential lanes NE of Al-Wad**: 2.5-4.5 m, 0.15-0.18 m risers with deep treads, rough parapets,
    plastered upper storeys with external steel stairs, balconies, dishes and cables. Add HaTut's 40-step run and
    Sheikh Lulu's ramp strip. Rassas Ascent climbs ~16.5 m (stepped). (1.8, 5)
15. **Plaza dressing and backdrops**: the big olive on the east side, the palms in the park west, oleander planters,
    the fountain niche on the bridge axis (the name "Sabil Bab al-Amud" is unverified), the Hindiyeh building and Schmidt's College on the skyline, and
    roofs with black tanks and white solar heaters seen from the gate. (2.3, 2.10, 4.4, 1.1)

---------------------------------------------------------------------------------------------------------------

Provenance: 45 Commons photos in `data/photos_ref/s08_damascus/` (2014-2025, 1280 px thumbnails;
`index.json` has title, page URL, author, licence, date and lat/lon where geotagged). Most useful: D12/D13
(מקף־עברי, Dec 2025, CC BY-SA 4.0), D08 (Bahnfrend 2019, CC BY-SA 4.0), D01-D05 (Bukvoed 2019, CC BY 4.0),
D09/D10 (B. Núñez González 2017, CC BY-SA 4.0), D27/D28 (R. Roletschek 2016, GFDL), D30 (Fallaner 2018,
CC BY-SA 4.0), D41/D22 (Юкатан 2015, CC BY-SA 4.0), D36 (جنان مريش 2018, CC BY-SA 4.0), D18/D15/D16 (PikiWiki
2025, CC BY 2.5). Several Commons geotags are wrong (D08, D11, D26, D35, D43 put the camera on or near the gate);
positions above rely on OSM geometry and image content, not on those geotags.
*[Review: D11 and D43 are captioned "view from Old City Walls" / "view from Damascus Gate" and were taken 24 s
apart, so their on-gate geotag (259.0,558.7) is plausible, not wrong. D08 (on the east tower front), D26 (inside
the walls) and D35 (a ground shot carrying D11's coordinates) are wrong. D20's geotag (231.6,591.0) fits the
OSM gate corners to 8 px rms and is the best scale reference.]*

---------------------------------------------------------------------------------------------------------------

## Review

Independent review, 2026-10-20. Method:
- Every cited OSM id was looked up in `data/osm_local.json`, with CCW rings and edge facings recomputed.
- Street widths were re-measured as perpendicular building-to-building rays every 2-3 m.
- Elevations were sampled from `data/terrain_street.json`, the OS 1865-calibrated street model.
- All cited photos were opened. Camera positions and focal lengths were resected from the OSM gate corners
  (D12, D20, D08), and facade proportions were measured on D12, D20, D26 and D04.

Corrections were made in place, marked *[Review: ...]*. The original text was kept except where it is
superseded.

### Corrections (most important first)

1. **Damascus Gate street fall: 3-4 m changed to ~6-7 m** (1.5, "biggest things" #3, checklist #7, section 5).
   - The street-level model gives 751.2 at the inner exit and 743.9 at the fork.
   - OS 1865: 750.42 at (288.2,551.8) and B.M. 744.35 at (312.5,501.0).
   - docs/TERRAIN.md route B: 752.5 / 747.6 / 743.2 at 0 / 50 / 100 m from the gate.
   - The note used SRTM (756 -> 754), which the project already replaced. The photo riser count is an
     undercount.
2. **Section 5 elevations re-based on the street model** (new column; SRTM kept but marked superseded). Notable
   changes:
   - Rassas Ascent climbs **~16.5 m**, not 6 m (OS 743.71 -> 760.17).
   - Khan ez-Zeit **rises ~3 m S of the fork** (4-5 %), not "nearly level".
   - Ibn Jarrah ends differ by ~7.5 m.
   - Al-Wad falls ~4 % (743.9 -> 739.5).
   - Absolute values drop 3-10 m everywhere.
   - The "highest point of the Old City" caption claim (D45) is false: ~764 m vs the Jaffa Gate datum of 770.6.
3. **Roman arch position** (2.2, checklist #6).
   - OSM node 9362751619 is a Legio X *inscription* "under bridge". It lies 2.0 m (not 2.9 m) NE of the
     centre-line, i.e. under the ~7.5 m deck, so it cannot be the arch.
   - D13 shows the arch crown beyond the NE parapet, at the foot of the gate wall left of the door pier.
   - D19 shows the deck overhead to the arch's right (SW).
   - Moved to the sunken court NE of the deck at the foot of the curtain e5, ≈ (269.5-271, 562-564), facing
     ~318°. M.
4. **Al-Wad covering mis-attributed** (1.7, checklist #11; moved to 1.5).
   - D43 (gate roof) and D31 (ramparts) show the **Damascus Gate street**, not Al-Wad. In both, the covered
     stretch ends at the W-side building with the triangular terracotta-pipe parapet, which D30 places at the
     foot of that street. D31 also has steps under the walkers.
   - Green/blue-white sheet roofs are now a profile C feature. Al-Wad's covering is UNVERIFIED.
   - D14, the only street-level Al-Wad photo, is 6.8 m outside the sector, so profile E ground details are M-L.
5. **Gate heights and the window** (3.2 review table, 3.3, 3.4, "biggest things" #1, checklist #1, #3, #4).
   - The D12 scale (22.5 px/m from the geotag at ~22.7 px/deg) does not reproduce the image beyond the three
     inner points: the east outer corner is predicted off-frame at x ≈ -17 but is visible at x ≈ 190.
   - The best fit at the geotag gives ~18 px/m (rms ~30 px).
   - D20 resected at its geotag fits five OSM corners to 8 px rms (f ≈ 910, 19-21 px/m in a grid search),
     which makes the doorway 4.2-4.6 m.
   - D13 people at the doorway give 4.1-4.3 m.
   - Facade ratios agree across D12, D20 and D26.
   - Revised values: doorway ~4.3 x ~5.9 m (was 3.6-4.4 x 5.2), parapet ~15 m (was 14), finial tips ~17 m
     (was 16), outer arch ~7 m wide with apex ~10 m.
   - The **window is ~0.95 x 1.6 m, not 1.1 x 2.0**. The note's own D12 scale gives a 1.5 m window height, and
     the window-to-doorway ratio is 0.37 w in all three facade photos. The seated-person scaling in D10
     overstates it. Still M.
6. **Sheikh Loulou Mosque geometry** (2.7).
   - w1392390329 is **south** of Sheikh Lulu Ascent, not north. The ascent passes 17-21 m to the NW, behind
     building w1392390322.
   - e0 (faces 160°) faces an unmapped 2-5 m gap along w291225673 that opens W onto the inner square. It does
     not face "onto Sheikh Lulu Ascent".
   - Either the entrance is from the inner square (e0/e4), or the OSM node is ~15 m off and the mosque is
     w1392390322. L, unresolved.
7. **Gate passage** (section 0, checklist #1). The OSM centreline turns ~94° then ~92° (SE -> NE 2.9 m -> SE), a
   double right-angle bend, not "a shallow zig-zag, not a right-angle turn". The view through is blocked by
   the BIG BEN end wall (D13, D02).
8. **D39 mis-identified** (1.6). It shows the foot of the Damascus Gate street looking N:
   - steps and herb sellers on the E side;
   - the blue-framed Taha greengrocer with its yellow fascia on the W side, matching D28.
   It does not show Khan ez-Zeit.
9. **Minaret "closes the view" down Al-Wad: unsupported** (1.7, checklist #11).
   - D15's minaret ID is confirmed: bearing 132.5°, with x ≈ 1150 predicted and observed.
   - But D15 is a rooftop telephoto. The actual street view D14 ends at a terrace-roofed building with a
     pointed arcade and shows no minaret.
   - The garden wall reads ~6 m next to the 1 m bollard in D14, not 8-10 m.
10. **Al-Wad widths** (1.7).
    - First stretch: 4.7-5.5 m, not 5.3-7.6, then an open SW side before the roof.
    - The roof w1393280745 is ~7.5 m along the street x 4.2 m across.
    - w1393172389 clips the Al-Wad centreline by ~1 m at (358-361, 438-442).
11. **Taha greengrocer and Halawani**: both are on the W side of the Damascus Gate street at y ≈ 500-506,
    facing E. They do not "face" the fork building (1.5, 2.6, checklist #9).
12. **Ja'far Sweets**: position M changed to **L**. It rests on one in-souq phone geotag, which falls inside an
    east-side building. The side of the street is unknown, and the shop may lie south of the sector (2.9).
13. **OSM roof ways as vaulted sabats**: form M changed to **L**. `building=roof` means an open-sided roof in OSM,
    and no photo shows any of the four tagged roofs (1.9).
14. **Inner portal** (3.7). D29 people-scaling suggests an opening of ~3.5-4 m and a cornice at ~8 m. Range now
    8-10 m / 3.5-4.5 m, M-L. Checklist #12 said "~10 m block", which conflicted with "13-14 m wide"; clarified.
15. **Gate depth** (3.1).
    - Curtain to inner face: 11.1 m (not 14-20).
    - East tower front to inner face: ~16.7 m. The west tower is 8.8 m deep.
    - The east city wall meets the footprint at (283.2,574.3), not (285.6,571.6).
16. **Smaller items**:
    - HaTut climbs SW, not W, and its top is outside the sector.
    - The 3.9 cross-reference to the olive tree pointed to 4.3; it is 4.4.
    - Plaza depth: use 4.5-5.5 m.
    - Geotags: D11 and D43 on the gate are plausible (captions say "from the walls/gate"), not wrong.

### Verified as written (spot checks)

- Gate footprint w616186088: area 450 m², centroid (268.4,557.4), all 17 edges and facings; doorway at
  (265.8,558.2), 0.5 m off the curtain centre.
- Bridge w616383626: 20.4 m. Deck ~7-8 m (D13 people; the OSM plaza polygon's ~11 m includes the booth
  platform).
- Police booth node 5827808684: 8.0 m SW of the axis, 9 m out, in front of the west tower's inner corner. Seen
  there in D08, D12, D13 and D26, and fits the D12 geotag fit.
- Olive tree 5825913094: fits D12 at its geotag (x ≈ 56 predicted vs ~90 observed).
- Fountain niche: on the bridge axis extended, (236.2,590.1) on retaining-wall segment w1547495755, facing 140°.
  D36 shows it with the W and central stair runs on either side.
- Khan ez-Zeit widths: 4.0-4.3 m for y 430-468, 5.4-9.6 m at the mouth.
- Damascus Gate street: 8.3-9.2 m at (303-307, 499-514); inner square 16-24 m.
- Profile F width statistics (re-measured; consistent).
- Inner court furniture and pole numbers "236 201" / "236 214" (D06).
- Plaques (D05, D18, D27, D40). Ja'far facade (D42). Ivy absent in 2019 (D08, D20) and present by 2023 (D17).
- Masjid al-Mustafa node inside w1393419051, with its E face 7.7 m from lane w257604182 across open ground.
- Minaret node 5921367466 in D15.
- Stair-run step counts and handrail tags.

### Still unverified / single-source (flag for modellers)

- Name "Sabil Bab al-Amud" (no OSM or caption source). Name "Hindiyeh building".
- Al-Wad north: covering, floor, shop fronts and lighting. No in-sector photo; D14 is just outside.
- Sheikh Loulou Mosque: which building, entrance side, minaret. Masjid al-Mustafa appearance. Both OSM only.
- Ja'far Sweets position and street side (one geotag).
- The four OSM `building=roof` "vaults" over lanes: form unknown.
- Inner court layout and orientation (D06 only). D06's view direction was not independently resolved against
  e10.
- Absolute gate heights remain **M** (±1 m): photogrammetric, with no measured drawing or published figure
  consulted.
- First vault position in Khan ez-Zeit (D41 only). Tower parapets ~0.5 m above the curtain (single view).
- Plaza depth: modern 1980s forecourt, not in the terrain model; 4.5-5.5 m from step counts.
