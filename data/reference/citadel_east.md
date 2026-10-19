# Citadel (from the street), east end of the square, top of David Street: visual reference

Local frame as in `hero_edges.md` (x east, y north, metres from the Jaffa Gate OSM node).
**Edge numbers follow the current `data/scene_spec.json` `buildings[].ring`** (CCW, edge i = vertex i to i+1);
they differ from `hero_edges.md` for several buildings (the table in section B maps them).
Photos: `data/photos/NNN_*.jpg` (project set) and `data/photos_ref/citadel_east/{A,B,C,P}NN_*.jpg`
(downloaded for this note, metadata and licences in `index.json` there). Scale is estimated from people
(~1.7 m) and doors (~2.2 m). Confidence: **high** = seen clearly in 2+ photos; **med** = one clear photo or a
consistent estimate; **low** = inferred or measured with poor perspective.

> Status: complete (written incrementally; the session was interrupted once).

---------------------------------------------------------------------------------------------------------------

## 0. Biggest corrections for the current model (summary)

1. **Phasael is the NE tower, not the NW one** (high). Every photo that names it shows it directly
   west of the entrance barbican and right above the square/moat corner: A01 ("seen from Omar ibn el-Khattab Sq.:
   the Tower of Phasael"), A07, A12, A14, A19, 112. The aerial 022 was taken from its top looking at the
   SCSC. The model's big box at (29,-28) with rot 35 sits at the NW corner; it belongs at roughly
   **centre (63,-17) ± 5 m, ~20 x 17 m, sides parallel to the north wall (bearing ~66 deg, i.e. rot ~24 deg)**
   (med): east face at x ≈ 72 with the east moat in front of it (glacis toe ≈ x 76-78, OSM outline vertex
   (67.9,-3.1)-(74.5,-19.1)), barbican SE of it at x ≈ 80-92, y ≈ -14..-30 (OSM outline lobe).
   The NW corner has no tall tower: the curtain wall keeps its height there (low-med, 113).
2. **Moat floor is a mown green lawn**, not stone (high): A12, A19, A17, 140. Round concrete inspection
   covers (~0.8 m) sit in the grass. Glacis (scarp) on the citadel side, a vertical drafted-ashlar counterscarp
   on the street side.
3. **The entrance is a barbican on a raised stone podium reached by a broad stair from the square** (high,
   A07, A03): pointed-arch wooden door in a tall pointed recess; crenellations with pointed finials.
4. **David Street is only ~3.5-5 m wall-to-wall and ~2.5-3.5 m clear between the goods/stalls**
   (high), steps are long and shallow, and the sky is mostly hidden by **steel-framed shed canopies from both
   sides** that leave a 0.5-1.5 m slot (high). With shops closed the walls read as rows of **teal/green
   steel doors with horizontal padlock bars** (high). The model's 7 m street width is far too wide.

---------------------------------------------------------------------------------------------------------------

## A. The Citadel seen from the square and the road

### A1. Moat (north and east sides)
- Floor: **flat mown grass lawn**, bright green when watered, ~4-5 m wide at the bottom; round concrete
  manhole/inspection covers (~0.8 m) in the lawn every ~10-15 m. **high** (A12, A19, A17, 140)
- Depth below the street: **~4.5-5 m** at the east moat (counterscarp ≈ 13 drafted courses of ~0.35 m,
  railing 1.1 m for scale). Model value 5 m is fine. **med** (A19)
- Width at street level (counterscarp coping to the glacis toe) ~6-8 m; the glacis then climbs ~4-5 m
  horizontally into the citadel, so wall-face to railing is ~10-12 m. **med** (A19, A12, 113)
- Counterscarp (street side): near-vertical wall of **pale cream tooled ashlar with strongly drafted
  horizontal joints** (each course reads as a horizontal band, ~0.35 m high), slightly battered, curved in plan
  following the road; flat coping ~0.35-0.4 m wide raised ~0.15 m above the pavement. **high** (A19)
- South of the entrance bridge the moat floor is **exposed bedrock and excavated wall stubs** with cypresses,
  not lawn. **high** (A16, A18)
- At the NE corner the pavement **projects over the moat on a deck carried by square concrete piers** (dark
  underside visible from inside the moat), with the same black railing. **med** (A12, A19)
- At the east end of the north moat (x ≈ 65-80, in front of Phasael's north side): a stair down from the street enclosed by a ~1.0-1.2 m ashlar parapet
  with flat coping (people sit on it), black tube handrails, a steel gate, and two upright teal/white
  "Ramparts Walk" (Hebrew טיילת) boards with opening hours **09:00-17:00**. A fan palm grows in the moat there.
  **high** for the objects, **med** for the position (113, 141)

### A2. Glacis (scarp, citadel side)
- Steep talus of **rough, irregular limestone blocks** (0.4-1.0 m, roughly coursed, weathered white-grey),
  slope **~60-70 deg** from horizontal, rising from the lawn to the base of the vertical wall; height from moat
  floor ~8-10 m under Phasael, ~5-7 m under the curtain wall. **high** for material and slope, **med** for heights
  (A12, A19, 112, A01)
- **Many small green shrubs (capers) growing out of the joints**, scattered evenly, ~0.3-0.6 m clumps, one
  per ~2-4 m². This is the most recognisable texture of the citadel from the square. **high**
- Under Phasael, between glacis and the Herodian blocks, there is a vertical band (~4 m) of smaller ashlar with
  3-4 small rectangular grilled windows (~0.6 x 0.8 m). **high** (A12, A07)

### A3. Street-edge railing (along the whole moat)
- **Black-painted steel**: square posts ~60 mm at ~2.0-2.5 m centres, top rail + second rail ~0.15 m below it,
  bottom rail ~0.1 m above the coping, **round vertical balusters ~12 mm at ~0.12 m centres**; height
  **~1.1 m**. Posts are fixed on top of the counterscarp coping. **high** (140, A19, A01, 113)
- Along the NE/east podium the railing is a simpler vertical-bar type ~1.0 m with flat top rail (A07, A03). **high**

### A4. North curtain wall
- Height of merlon tops **~11-14 m above the street, i.e. ~16-19 m above the moat floor**; about half of
  Phasael's height in A01. If `citadel.wall_h` (13 m) is measured from the moat floor it is ~3-5 m too low; from
  street level it is in range. From the street the visible part (glacis top to merlon top) is ~8-9 m.
  **med-low** (113, A01)
- Crenellation: **rectangular merlons ~1.6-1.8 m wide x ~1.6 m tall, embrasures ~0.6-0.8 m wide**, flat tops
  (no caps) on the curtain wall; each merlon has a narrow vertical slit. **high** (113, A01, 140)
- Arrow slits in the wall body: **narrow vertical slits (~0.15 x 1.2 m) ending in a small round oillet at the
  bottom ("keyhole")**, two rows: one ~1.5 m below the parapet walk and one lower. **high** (113, 055)
- Masonry: medium ashlar courses 0.4-0.6 m, honey/ochre and grey patchy weathering, darker streaks below
  slits and spouts. **high**

### A5. Phasael tower (NE tower, "David's Tower")
- Position: see section 0. **high** that it is the NE tower next to the barbican; **med** for the numbers.
- Plan ~21 x 17 m at the base (Herodian base), upper part flush (no setback seen). **med/low**
- Total height above the street **~24 m** (≈2x the curtain-wall merlon height in A01). **med**
- Three zones above the glacis (A07, 112, A24):
  1. lower outer wall/glacis with stepped merlons in front of the base (a lower crenellated wall wraps the
     foot of the tower, ~1/3 of tower height) **high** (112, A24)
  2. **Herodian zone: ~9-10 courses of huge blocks ~1.0-1.2 m high and 1.5-3 m long with drafted margins and
     rough projecting bosses**, honey-orange colour, deeply weathered **high** (A13, A07, 112, A24)
  3. **upper zone: ~18 courses of smaller ashlar 0.4-0.6 m**, paler/greyer, roughly equal in height to the
     Herodian zone **high**
- Openings on the north and east faces: two rectangular windows with square iron grilles (~0.8 x 1.0 m) in
  the upper zone about 1/3 down from the top; one narrow vertical slit; **two small round oculi (~0.5 m)**
  near the top of the north face; a few protruding spout stones. **high** (112, A07, A24)
- Top: low parapet with small irregular notches and a modern **black steel railing**; **two or three flagpoles
  (Israeli flag + Jerusalem flag)** at the SE part of the roof; a small corner turret/booth with a pointed
  window at the SE corner. **high** (A24, A07)

### A6. Entrance: barbican, podium, stair and bridge (east side)
- Barbican = square gate tower ~8 m wide on its north face, ~9-10 m from the square to the merlon tops. **med**
- North face (A07, A03): a **tall pointed-arch recess (~4.5 m wide, apex ~6.5 m above the podium)** framing a
  **pointed-arch doorway ~2.4 m wide x ~3.5 m** with **heavy double wooden doors, weathered olive-brown with
  iron studs and straps**; to its left a smaller blind pointed niche; a black framed notice plaque beside the
  door. **high**
- Upper part: a band of small decorative corbels/zigzag frieze at ~8 m, then the parapet with **6 merlons
  topped by pointed (stepped-pyramid) finials with a knob**. **high** (A07, A18)
- The doorway stands on a **stone podium ~1.6-1.8 m above the square**, faced with ashlar and a flat coping,
  black vertical-bar railing on top; **a broad stair of ~8-9 steps with a black handrail rises from the west
  (from the moat corner) up along the podium**. **high** (A07, A03, A18)
- In front of the podium in 2017-2021: a white free-standing exhibition board ("NOW AT THE TOWER OF DAVID
  MUSEUM" / Hebrew / "ההר الحرم The Mount"), a small black plaque, a grey utility box, short black bollards on the
  pavement. In 2021-2026 two upright teal "Entrance" totems with Hebrew text stand at the moat railing near
  Phasael. **high** for the objects, they change yearly (A07, A01, 113)
- Inside the barbican a **bridge deck (dark, flat, with black steel railings) crosses the moat westwards into the
  citadel gate**; its side carries a **teal sign with white lettering "מוזיאון מגדל דוד / The Tower of David Museum"**.
  **high** (A18, A19)
- Below/inside: a dark grey kiosk (ticket/shop box with a flat overhanging roof) on the paved inner court. **med** (A18)
- Blue museum plaque near the NW entrance stair: "מוזיאון מגדל דוד / Tower of David Museum / متحف برج داود /
  Tod.org.il | *2884" (white text on blue, white border). **high** (109)

### A7. Road and pavement between square and citadel
- The roadway (Armenian Patriarchate Rd / Omar ibn el-Khattab Sq. road) is paved with **small grey granite/basalt
  setts (~10 x 10 cm)** in fan/arc patterns, darker than the plaza; the plaza is **large cream-grey limestone
  slabs** (0.4-0.6 x 0.6-1.0 m). **high** (140, A19, 022, 041)
- The separating kerb is a **flush or very low (≤5 cm) band of long pale limestone kerb stones (~0.4 m wide)**
  following the curve; a parallel pale band runs along the railing side too (sidewalk ~2-3 m wide along the
  moat). In 140 the band is a gentle raised strip ~0.1 m, not a vertical kerb. **high** (140, 022)
- Bollards: short black/dark-grey steel bollards (~0.8 m, ~0.12 m dia.) at the barbican podium and the
  plaza/road edge. **med** (A07)
- Lamp posts: tall slender dark-grey square-section poles (~6-8 m) with flat rectangular LED heads, some
  double-headed, along the square and the road near Jaffa Gate. **high** (063, 064, 072, 033)
- Moving traffic: taxis (white) and service vehicles use the road along the east moat. (A19)

### A8. Other towers and the minaret as seen from the square
- From the NE corner of the square looking west (eval cam `citadel_moat`, photo 113): Phasael fills the left
  edge, then the north curtain wall with tall flat merlons and keyhole slits runs west towards Jaffa Gate; its
  crenellated top line is level, no tall tower interrupts it until the NW corner, where the wall turns. **high** (113)
- The minaret (SW corner) is mostly hidden behind Phasael and the north wall from the east end; it shows above
  the walls from the west part of the square and from outside the gate: **slender cylindrical stone shaft, one
  balcony ring with a parapet near the top, a short upper drum and a small pointed cap with a finial**, rising
  ~8-10 m above the citadel walls. **med** (136, 108)
- Barbican (A6) and Phasael are the only towers one sees close up from the east end. **high**

### A9. Ground near the citadel (east end)
- The road surface in front of the barbican and along the east moat is the grey sett paving of A7; there are
  no painted road markings in the square; a white "bus stop" pole (HaKishle/Armenian Patriarchate, OSM node at
  (109,-29)) stands on the east kerb south of the CIC. **med**

---------------------------------------------------------------------------------------------------------------

## B. East end of the square

Edge map (scene_spec edge → old hero_edges edge):
| building | facade | scene_spec edge | hero_edges edge |
|---|---|---|---|
| w126781854 SCSC | west, on the square (12.2 m, faces 269) | **0** | 8 |
| w126781854 SCSC | south, towards CIC (19.7 m) | **1** | 0 |
| w126781854 SCSC | north, on David St (6.1 m) | **5** | 4 |
| w1549766140 white corner bldg | west, on the square (5.3 m) | **1** | 3 |
| w1549766140 | north, on David St (7.0 m) | **0** | 2 |
| w126782745 CIC | west main facade (16.8 m, faces 266) | **1** | 7 |
| w126782745 CIC | north (22.3 m, faces 355) | **0** | 6 |
| w126782745 CIC | south (12.4 m) | **2** | 0 |

### B1. Swedish Christian Study Centre, w126781854 edge 0 (west facade on the square)
Photos: 144 (2019, frontal), 041 (Dec 2025), 022 (aerial, ~2010), B03/B01 (roof).
- **2 storeys + parapet; total ~10.5-11 m above the terrace**. Ground storey ~5.0 m (arches), upper storey
  ~3.8 m, parapet band ~1.3 m. **med**
- The facade stands on a **raised terrace ~0.6-0.8 m above the square** with 3-4 curved steps at the north end
  and grey tubular steel handrails; café tables/umbrellas on it in 2019. **high** (144, 041, 022)
- Ground floor, 4 bays (N→S), **4 large semicircular arches ~2.5-2.6 m wide, springing ~3.2 m, apex ~4.5 m**,
  stone voussoirs flush with the wall:
  - tympanum (above ~3.2 m) filled with a **black steel radial "sunburst" fan grille** (~18-22 spokes from a
    small semicircular hub) **high** (041, 144)
  - at the springing, a **continuous flat black steel canopy ~0.8-1.0 m deep** across all 4 bays, with a black
    fascia; fluorescent/LED strip under it **high**
  - below the canopy the shop fronts: bay 1 (north) **grey steel roll-down shutter / grey steel doors**
    (closed in 2025); bays 2-3 open souvenir shops (goods hung outside); bay 4 a glazed shop/café front with
    dark frames. With shops closed: grey or teal-green roll-down shutters. **med**
- Upper floor: **4 semicircular-arched windows ~1.4 m wide x ~2.3 m tall** aligned over the arches; arched
  heads filled with a **light (white/cream) radial fanlight grille**, lower part a light grid of panes
  (3 columns x 2 rows); stone surrounds flush; no balconies, no shutters. **high** (041, 144)
- **Black rectangular wall floodlights on short arms** between the upper windows (3), angled down. **high**
- An orange/terracotta box awning (~3 m long, 0.4 m tall) above bay 1 at the upper-floor sill level (2025);
  in 2019 three of them plus a large orange sloped awning over bay 4. **high** (041, 144)
- Upper band: plain ashlar parapet band with **dark bronze/grey serif capitals "SWEDISH CHRISTIAN CENTER"**
  (~0.25 m tall, one line) centred over bays 3-4 just below the coping; a thin string course at the window-head
  level and another below the parapet. **high** (041, 022)
- Roof (B03, B02, 022): flat roof with a **perimeter black steel railing** carrying a **frame of large dark
  letters "SWEDISH CHRISTIAN STUDY CENTRE"** (~0.6 m tall) facing south-west over the citadel (seen from the
  Citadel and Petra Hotel); **black cylindrical water tanks** (~1 m dia., 1.3 m tall) with a **Swedish flag**
  on a pole; solar water-heater panels; antenna masts; a floodlight mast with two lamps; an AC unit cluster.
  **high**
- Stone: cream-white limestone ashlar, courses ~0.35-0.45 m, fairly clean, grey streaks under the parapet
  spouts; several black cables run along the springing line and up the corners. **high**

### B2. White corner building at the mouth of David St, w1549766140 edges 1 (square) and 0 (David St)
Photos: C03 (2016), 144, 022.
- 2 storeys, **very clean near-white new ashlar**; **hipped roof of grey standing-seam metal with deep eaves
  (~0.8 m) and a timber-boarded soffit** — the only pitched metal roof on the square. **high**
- West face (edge 1): upper floor **3 round-arched windows (~1.0 x 1.8 m) with raised voussoir surrounds and dark
  frames, plus a round oculus (~0.7 m) with a radial grille at the south end**; centred below the windows the
  ceramic square plaque (see B5). Ground floor: shop under a **flat grey steel canopy at ~3.3 m**, a clothes rail
  with goods; a **yellow fire hydrant** at the NW corner. **high** (C03)
- North face (edge 0, on David St): shop openings under the canopy, goods hung on a steel rail. **med**

### B3. Christian Information Centre (former Austrian post office), w126782745 edge 1 (west main facade)
Photos: B09 (2021 frontal), 145 (2019 oblique), 041 (2025), B05/B06 (2015).
- **Main block 2 storeys, ~13 m wide, + a 1-storey annex ~3.7 m at the south end**. Height to the cornice
  ~9 m, to the top of the parapet piers ~10-10.5 m; tall ground floor (~5.3 m), upper ~3.3 m. **med**
- Three bays divided by **flat full-height pilaster strips**; projecting **rusticated grey plinth (~0.9 m)** that
  forms the ground-floor window sills; string course between floors; **heavy moulded cornice**; above it a
  **parapet of square stone piers (~0.5 m, 6 piers) with black steel railings** between them (roof terrace,
  planters with shrubs along the inside). **high**
- Ground floor N→S: (1) **big round-arched gateway ~3.5 m wide x ~5 m** with a black wrought-iron gate in a
  **diamond / fish-scale lattice**, 1-2 low steps; (2) centre bay **3 round-arched windows (narrow ~0.8 m, wide
  ~1.1 m, narrow)**; (3) south bay the same triplet. All windows have **black iron grilles in a scale pattern**,
  **moulded archivolts with a carved keystone boss**. **high**
- **Red serif metal letters, 3 lines: "CHRISTIAN / INFORMATION / CENTRE"** (~0.3 m tall) centred above the
  centre-bay windows. White marble plaque with a black inscription above the south bay (commemorates the k.k.
  Austrian post office; text not legible). **high** for letters, **low** for the plaque text.
- Upper floor: **9 round-arched windows in 3 groups of 3**, ~1.0 m wide x 2.0 m, **white modern frames** with
  two vertical mullions, moulded surrounds with keystones; a **carved coat-of-arms relief panel** under the centre
  group. **high** (B09, 145)
- **Black rectangular box lamps on arms** at both upper corners. White AC units on the annex. **high**
- South annex: pinkish stone, a round-arched opening closed by a **cream/beige roll-down shutter (~2.8 x 3.5 m)**,
  white ceramic square plaque at the junction, cables and a grey meter box. **high** (B09, 145)
- Stone: warm honey-ochre limestone, more weathered than SCSC; darker grey plinth. **high**

### B4. CIC north face (edge 0) and SCSC south face (edge 1)
- They face each other across a **gap of only ~2.5-3.5 m** (y −9 vs −12); no clear photo. Treat as a narrow
  passage with plain walls, cables and pipes. **low**

### B5. Ceramic square-name plaques (east end)
- White glazed tiles, **3 lines: Hebrew "כיכר עומר בן אל-ח'טאב", Arabic "ميدان عمر بن الخطاب", English
  "OMAR IBN AL-KHATTAB SQ." (or "OMAR IBN EL-KHATTAB SQ.")**, dark lettering, thin brown/green framed border,
  ~1.0 x 0.5 m; one on w1549766140 edge 1 (left of centre, below the upper-floor sill ledge, ~4 m up) and one at
  the south end of the CIC facade (~3.5 m up). **high** (C03, 142, 145)

### B6. Ground-level details at the east end (from 142, the eval photo `east_end_david`)
- **SCSC terrace front**: a stone retaining edge ~0.6-0.7 m high (3 courses, flat coping), **3 curved steps at
  its north end** leading up from the mouth of David St, and a **grey tubular steel railing (~1.0 m, two
  horizontal rails on round posts)** along the terrace edge; carpets/goods are hung over it when open. **high** (142, 144, 041)
- **No bollards in front of the SCSC/white building** in 2019-2025 photos (the model has a row of black bollards
  there). **high** (142, 041, 144)
- White corner building w1549766140 (142 crop): upper-floor windows have **dark grey two-leaf frames with a
  transom** under **raised relieving-arch rings**; a stone ledge at the upper-floor sill; below it a plain band
  with the ceramic square plaque; ground floor: a **quarter-round dark-grey metal awning** over its west door,
  a **white wrought-iron scroll door grille**, a **dark grey downpipe** at the SW corner. **high**
- Petra block (w1393928801 edge 0, north corner of the mouth): balconies with black railings, "WELCOME TO THE
  OLD CITY" fascia letters, grey-green curved awnings, a cream striped fabric awning at its west end. **high** (142, C15)
- Neighbours further east (w290692953, w1393938082, w1393938083) are only seen as David Street frontages: see C.

---------------------------------------------------------------------------------------------------------------

## C. David Street, first ~60 m east of the square (x ≈ 97 → 160)

Main photos: C01/C02 (2017, from the mouth looking E; C01 is the eval photo `david_street`), C03 (2016, mouth
from the square), C04/C05 (2016, first 30 m), C15 (2011, mouth), B10 (2016, closed shops), C18 (2010, closed),
C22 (2007, night, closed), C19 (2009, closed, vaulted part just beyond 60 m), C20 (2005, steps with ramps),
C08/C13/C14 (traffic sign), C10/C11 (street plaques), C23 (Petra entrance), 142 (mouth from the square).
Compare: `renders/eval/david_street_compare.jpg` (model: ~7 m wide open lane, plain slabs, tall pointed arches,
nothing overhead) vs photo (narrow, roofed by canopies, signs, thresholds, pitted paving).

Facades lining the first 60 m (scene_spec edges):
| side | x range | building / edge |
|---|---|---|
| north | 84.6-109 | w1393928801 edge 0 (Petra Hotel block, the north corner of the mouth) |
| north | 110.7-116.6 | w1393938083 edge 2 |
| north | 117.7-138.2 | w1393938082 edges 2, 4, 6, 8 (stepped frontage y 11.4 / 14.0 / 12.3 / 16.8) |
| north | 153.7-166.4 | w1393928811 edge 2 |
| south | 111.4-118.3 | w1549766140 edge 0 (white corner building) |
| south | 118.3-124.4 | w126781854 SCSC edge 5 |
| south | 124.4-130.8 | **gap in OSM** (see C1) |
| south | 130.8-149.3 | w290692953 edges 0 and 6 |
| south | 151.4-157.8 | w1394458564 edge 0 |

### C1. Width and plan
- **Wall-to-wall 3.5-5 m; clear walking width between the raised shop thresholds 3-3.5 m, and 2.5-3 m where
  goods, crates and stools stand out (most of the day)**. **high** (C01, C04, C05, B10, C22). OSM agrees:
  y 8.4-8.7 (south) vs 13.7-14.0 (north) gives 5.3 m at x 111-117 and x 123-130, ~4.9 m at x 130-136, and
  only ~2.8 m at x 118-123 where w1393938082 edge 2 juts out to y 11.4.
- **The model's 7 m street (DAVID.width) is ~2x too wide**; the steps should be clipped to the building faces and
  the street should feel like a corridor. **high**
- Straight for the first ~40 m, then a slight bend to the left (north) around x ≈ 155-165 where taller houses
  close the view. **high** (C01, C05, C17)
- South side x 124.4-130.8: OSM has no building there, but all eastward photos show **continuous shopfronts
  on the south side**, no 6 m side lane. Treat as an unmapped building with shops (or at most a doorway to a
  courtyard). **low-med** (C01, C04, C05)

### C2. Floor: paving, steps, thresholds
- **Paving: large limestone slabs ~0.4-0.6 m x 0.7-1.2 m laid in courses across the street (long side across,
  joints staggered)**. Mix of **smooth glossy worn slabs and heavily pitted rough-picked slabs** (pitting for
  grip, gives a speckled white-on-grey look), cream/grey with ochre and pinkish ones. Polished to a sheen in the
  middle where people walk. **high** (C01 crop, C02, C04, C19, B10)
- **Round cast-iron manhole covers ~0.7 m with concentric ring pattern**, roughly in the centre line every
  ~6-10 m, plus small round drains (~0.3 m) and occasional square grates. **high** (C01, C02, C04, B10, C22)
- **Steps**: the first ~10-15 m from the mouth is a gentle ramp with at most 1-2 low steps; from there on,
  **full-width shallow steps, risers 0.10-0.15 m, treads mostly 1.5-3 m near the top and ~1.0-1.5 m further
  down**; step edges are just the slab edges (square, worn round), no separate nosing, no contrasting stone.
  **med** (C01, C02, C04, C05, C17). The model's 0.16 m riser / 1.9 m tread is about right; start the steps a
  little later (≈ x 110-112) and make risers 0.12-0.14 m.
- **Cart ramps**: further down (x ≳ 155) the steps carry **smooth sloping ramp strips ~0.6-1.2 m wide** for
  hand carts (one or two per step run), made of pitted slabs. Not clearly visible in the first 40 m. **med**
  (C20, C09; C20 caption: "the ramps in the middle of the streets are to accommodate carts")
- **Raised shop thresholds**: along both sides a **stone platform/step 0.15-0.30 m high and 0.4-0.7 m deep**
  in front of the shop openings (often two stepped levels), with worn square edges; goods sit on it. This is
  what makes the walking width 3-3.5 m. **high** (C04 crop, C01, B10, C18, C22)
- No central gutter; water runs down the middle to drains. **med**

### C3. Shop fronts when closed (the target state)
- Shops are **one bay deep vaulted rooms (dukkan), openings ~2.0-3.0 m wide and ~2.8-3.2 m tall**, separated by
  stone piers ~0.4-0.8 m. The opening heads are hidden behind the canopies; where visible they are **flat steel
  lintels inside segmental or pointed stone arches** (not tall free-standing pointed arches as in the model).
  **high** (B10, C19, C22, C18)
- **Doors: steel sheet doors painted pale teal / verdigris green (also olive-grey, a few white or grey)**, 2-4
  leaves per opening, each leaf divided into **3 tall rectangular panels by flat-bar frames**; the full
  opening height (2.8-3.2 m); **two horizontal locking bars (hasps) at ~1.0 m and ~1.9 m with padlocks**,
  hinges outside; paint chipped and rust-streaked at the bottom. **high** (B10, C19, C22, C18)
- Some openings have **corrugated roll-down shutters** (teal, green or grey) with a box at the top. **high** (B10, C03)
- A few shops have a **black steel grid/lattice gate** instead (C22 left side: black vertical-bar folding gates
  with square panels). **med**
- Graffiti: occasional small tags/scribbles on the doors (B10 right). Stickers. **med**
- Above each door: **a projecting steel rail or bracket set (hooks, short horizontal bars) for hanging goods**,
  ~0.3-0.5 m deep, at ~2.8-3.2 m. **high** (C19, C16)

### C4. Canopies and awnings (the main thing missing in the model)
- **Every shop has a steel-framed shed canopy projecting ~1.2-1.6 m into the street, front edge at ~3.0-3.4 m,
  rising to ~3.8-4.2 m at the wall**, both sides, nearly continuous. Roofing: corrugated metal or
  translucent corrugated sheet; frames painted **dark green / teal or black**. **high** (C01, C02, B10, C18, C19)
- The triangular brackets carry **decorative wrought-iron scrollwork (rings and C-scrolls)**; a horizontal tube
  along the front edge carries **fluorescent tubes / LED bars** on the underside and hooks for goods.
  **high** (C01 top crop, C02, C22)
- Canopies from the two sides **leave only a 0.5-1.5 m slot of sky** along the street centre; in places they
  overlap. **high** (C01, C18, B10)
- Some canopies are **canvas with a scalloped white/cream valance** (C04, C05, C21) and some are **quarter-round
  curved sheet-metal awnings in grey-green** (the north side at the mouth, C15; also on w1549766140, 142).
  **high**
- At the mouth: w1549766140 has a flat black steel canopy + a small quarter-round dark grey awning; the Petra
  block has two long grey-green curved sheet-metal awnings and a balcony above. **high** (C15, 142, C03)

### C5. Overhead: cables, beams, coverings
- **Green-painted steel beams/tubes span the street at ~4.5 m** tying the two canopy rows together (one every
  ~5-8 m). **high** (C01 top crop)
- **Many sagging black cables** criss-cross at 4-7 m; **bare light bulbs and small lamps on wires** hang over
  the stalls; string lights for holidays. **high** (C01, C05, C06)
- **Projecting upper rooms**: a boxy enclosed bay/room on corbels (rust-coloured) on the south side at ~6-7 m,
  and a **white glazed box-bay with many small panes** on the north side at ~5-6 m, both visible from the mouth.
  **med** (C01 top crop, C21)
- **Covered (vaulted) parts**: none in the first ~60 m; the first whitewashed **pointed barrel/groin vault** over
  the street is at about x ≈ 175-185 (C19 geotag 180,9; low confidence on position). A perforated-metal arched
  roof (C06) is further east (location unknown). Within the 60 m the "roof" is the canopy layer plus sky. **med**
- Walls above the canopies: old, darker honey/grey rough ashlar, small windows with grilles, AC units, pipes,
  cables; a tall pointed-arch window on the north side near x ≈ 120-130. **high** (C01, C21)

### C6. Signs
- **Street-name plaque (upper David St)**: Armenian ceramic tiles, white ground with dark blue lettering, framed by
  a **green leaf / yellow ornamental tile border**; 3 rows: Hebrew **"רחוב דוד"**, Arabic **"طريق سويقة علون"**
  (Tariq Suwayqat Allun), English **"DAVID ST."**; ~0.8 x 0.6 m, at ~3 m on a wall. A variant further east reads
  "רחוב דוד / طريق الباذار / SUQ EL-BAZAAR RD.". **high** for design, **med** for which one is in the first 60 m
  (C10, C11). Historic British-Mandate "DAVID STREET" glass sign (C12) is not current.
- **Round prohibition sign "no tractors"** (red ring, white disc, black tractor, ~0.6 m) on a pole/bracket at
  ~3-3.5 m at the mouth, **with two white CCTV cameras** next to it, plus a blank brown board. **high** (C03, C08,
  C13, C14)
- **"A.T.M MACHINE / MONEY CHANGER" board**: tall white board, black side panels with white "ATM" letters, red
  vertical lettering and a red arrow, at the Petra entrance on the north side (x ≈ 105-110). **high** (C01, C23)
- **"REX / SOUVENIRS & JEWELRY"** white light box with red letters, hung perpendicular at ~3 m (north side,
  x ≈ 115). **high** (C01, C03, C07)
- **"New PETRA Guest House"** red-and-white sign over the hostel stair door (north side, near the mouth). **high** (C23)
- **"Souvenirs / DIVINA TIERRA / СУВЕНИРЫ И ИКОНЫ"** shop sign (white with red band) and a "REX ←" painted
  arrow board, first shops on the north side; blue enamel/ceramic **house-number plaques** ("3"). **high** (C04)
- **Hanging shop boards** perpendicular to the street at ~2.8-3.0 m: cream/white rectangles ~1.2 x 0.6 m in a
  **black steel frame with inward-curved (ogee) corners**, Arabic + English text (e.g. "JAWAD ABDEEN FOR
  LEATHER", "SINOKROT BAZAAR"), many blank or empty frames. **high** (C22, B10, C19)
- Multilingual "Jewellery & Souvenirs" boards (English/Spanish/Russian). **med** (C01)
- At the very mouth, on the Petra balcony fascia: large letters **"WELCOME TO THE OLD CITY"**. **med** (C03, C15, 142)

### C7. Clutter (closed state)
- Even when shops are closed: **plastic crates, cardboard boxes, a white plastic chair or two, a stool, the odd
  hand cart (blue wooden cart with car wheels, C09)**, rubbish bags by the doors, water bottles. **med**
- Typical open-shop goods (for reference only): rugs, scarves, keffiyehs, tallits, ceramics, postcard racks.

### C8. Lighting
- At night: warm wall lamps and bare bulbs under canopies, fluorescent tubes, very dark doors; the street floor
  glows from lamps on wet stone. **high** (C22, C24)

---------------------------------------------------------------------------------------------------------------

## Model checklist

Prioritised by how much each closes the gap in the eval comparisons (`david_street`, `east_end_david`,
`citadel_moat`), all shops closed.

1. **David St width**: clip the street to the building faces, 3.5-5 m wall-to-wall (≈2.8 m at x 118-123),
   instead of the 7 m lane; add the **0.15-0.30 m x 0.4-0.7 m raised stone thresholds** along both sides so the
   walkable strip is 3-3.5 m. (C1, C2)
2. **Shed canopies on both sides of David St**: steel frames, front edge ~3.0-3.4 m, projection 1.2-1.6 m,
   corrugated roofing, dark green/teal frames with scrollwork brackets, leaving a 0.5-1.5 m sky slot; plus green
   steel tie-beams across at ~4.5 m and sagging cables. This alone fixes most of the sky/skyline mismatch. (C4, C5)
3. **Closed shop bays**: 2.0-3.0 m wide x 2.8-3.2 m tall openings with flat steel heads (arches hidden or
   segmental), filled with **pale teal 2-4-leaf panelled steel doors with two padlock bars**, some corrugated
   roll-downs; replace the tall free-standing pointed arches with blue/green doors. (C3)
4. **Move Phasael to the NE corner** (centre ≈ (63,-17), ~20 x 17 m, rot ≈ 24 deg, ~24 m above the street) with
   the three-zone masonry: glacis + small-window band, ~10 courses of 1.0-1.2 m Herodian bossed blocks, ~18
   smaller courses, oculi and two grilled windows, railing + flags on top. Remove the big box at the NW corner. (0, A5)
5. **Moat floor = mown lawn** with round covers; counterscarp of drafted horizontal-band ashlar; steep rough
   glacis with scattered caper shrubs in the joints. (A1, A2)
6. **David St paving texture**: large cross-laid slabs, mix of glossy and pitted rough-picked stone, plus round
   cast-iron manhole covers on the centre line every 6-10 m. (C2)
7. **Hanging sign boards**: cream boards in black ogee-cornered frames perpendicular to the street at ~2.8-3 m
   (several blank), REX light box, ATM/MONEY CHANGER board at the Petra door, no-tractors sign + 2 CCTV cameras
   at the mouth, ceramic "DAVID ST." plaque. (C6)
8. **Barbican entrance**: stone podium ~1.7 m with a broad 8-9-step stair and black railings, tall pointed recess
   with olive-brown studded wooden doors, corbel frieze and 6 merlons with pointed finials; bridge with teal
   "The Tower of David Museum" sign. (A6)
9. **Black moat railing** (1.1 m, square posts ~2-2.5 m, double top rail, round balusters at 0.12 m) on the
   raised coping, following the curve. (A3)
10. **SCSC west facade (edge 0)**: 4 round arches with black sunburst fan grilles, continuous black flat canopy
    at the springing, 4 upper arched windows with light fanlights, black floodlights, "SWEDISH CHRISTIAN CENTER"
    letters in the parapet band, orange box awning; raised terrace with curved steps and grey tube railing; no
    bollards in front. (B1, B6)
11. **CIC west facade (edge 1)**: 3 pilastered bays, big arched gate with black scale-lattice grille, two triplets
    of grilled arched windows on a grey rusticated plinth, red "CHRISTIAN / INFORMATION / CENTRE" letters, 9
    upper windows in triplets, cornice + piered parapet with black railings; south annex with cream roll-down. (B3)
12. **Road vs plaza surfaces**: small grey setts on the roadway along the moat, large pale slabs on the plaza,
    separated by a flush pale kerb band (not a tall kerb). (A7)
13. **White corner building w1549766140**: near-white ashlar, dark standing-seam hipped roof with deep eaves,
    3 arched windows + oculus on the square side, ceramic square plaque, quarter-round grey awning. (B2, B6)
14. **Rooftop dressing of SCSC**: big dark "SWEDISH CHRISTIAN STUDY CENTRE" letters on the roof railing, black
    water tanks, Swedish flag, solar panels, antenna and floodlight masts. Visible from the whole square. (B1)
15. **Curtain-wall crenellation and slits**: flat rectangular merlons ~1.7 m wide with slits, keyhole arrow
    slits in two rows, merlon tops ~11-14 m above the street; Ramparts-Walk stair enclosure with teal boards at
    the east end of the north moat. (A4, A1)
