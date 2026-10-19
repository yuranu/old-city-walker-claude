# s07_kotel: Western Wall plaza, Mughrabi bridge, Dung Gate, archaeological park edge: visual reference

Local frame as in `hero_edges.md` (x east, y north, metres from the Jaffa Gate OSM node).
OSM ids from `data/osm_local.json`. Photos: `data/photos_ref/s07_kotel/NNN_*.jpg` (key `K:NNN`; title,
page, author, licence, date, camera lat/lon and `local_xy` in `index.json` there; 47 photos, all
2015-2026 except K:043, 2013). Scale comes from people (~1.7 m), doors (~2.2 m), the 3.85 m height-limit signs at the gate and
OSM edge lengths. Confidence: **H** = seen clearly in 2+ photos or fixed by OSM geometry; **M** = one clear
photo or a consistent estimate; **L** = inferred or measured with poor perspective.

> Status: complete (written incrementally). Independently reviewed 2026-10-19; corrections are made in place and listed in "## Review" at the end (R1-R15).

**Geotags are often wrong here** (phones inside the walled plaza): K:003, K:004, K:010, K:031, K:032, K:045 are
10-80 m off. Every viewpoint used to confirm a position below was re-derived from what the photo shows
(the wall, the mechitza, the bridge, the minarets) against OSM; the corrected viewpoint is in the photo table (§7).

---------------------------------------------------------------------------------------------------

## 0. Sector geometry: what is where, and how each position was confirmed

| feature | OSM id | local position | confirmed by |
|---|---|---|---|
| Western Wall Plaza (pedestrian area) | w26492734 | x 563-656, y -96..35 (5564 m²) | OSM |
| Western Wall prayer face (west face of the Haram wall) | w817206833 west edge | x 646 (y 35) → 652 (y -2) → 656 (y -23); 59 m long | OSM + K:003, K:012, K:016 (wall as backdrop, north building at its N end) **H** |
| North end block over Wilson's Arch (closes the men's section) | w499210296 (S edge) | facade on y ≈ 31-35, x 619-646, faces S | K:002 from (587,-29) looking NE, K:016 from the bridge looking N, K:014/K:017 **H** |
| Mechitza (men N / women S) | fence w45081551 | (618,-7) → (652,-2) | K:003 (from ≈(615,5) looking E: mechitza on the right running to the wall), K:016/K:017 (from the bridge, diagonal), K:019 **H** |
| Prayer-area boundary (parapet + railing) | wall w45081552 | (604,-32) → (627,18), so the area is ~22 m deep at the N end, ~40 m at the S end. *Review (R13): not a straight line; OSM vertices (603.5,-32.0) → (620.0,-20.4) → (617.7,-7.3) [mechitza W end] → (613.9,15.7) → (627.3,18.0); the men's section is ~33-36 m deep for most of its length* | K:009, K:012, K:015 **H** for the object, OSM for the line |
| Men's / women's sections | n4905269168 / n4905269169 | (633,10) / (637,-10) | OSM + mechitza above **H** |
| Mughrabi Gate (on the Haram) | w291836692 | (656-664, -33..-22); passage w748953237 | K:007 (gate arch at the bridge's upper end), K:013, K:021 **H** |
| Mughrabi bridge, ground-level approach | w44172764 | (615,-95) → (613,-42), along x ≈ 612-616 | OSM; K:045 (the bridge seen behind the south entrance) **M** |
| Mughrabi bridge, covered timber bridge | w277508271 | timber stair tower at (613,-42), *first 9 m due N to (613.6,-33.3) (review, R12)*, then (626,-23) → (649,-16), short return (652,-27) → gate (657,-27) | K:013 from the men's section: rises right(SW) → left(SE); K:021 from the SW: rises left → right; K:007 from the W **H** |
| South entrance + security check ("Access to the Western Wall Area") | n2915691087, roof w277508272 | checkpoints (604-615, -95..-100), roof over x 584-617, y -109..-94 | K:045 (MEN / WOMEN ENTRANCE portal), K:018/K:020 (bridge-entrance signs) **H** |
| Ma'alot HaRav Goren steps | w288065154 | (602,-109) → (614,-107), down eastwards to the checkpoint | OSM **M** |
| Kotel bus terminus loop | w288065153 (+ bus stop n1803023878) | loop x 581-613, y -142..-118 | K:025 (oval island with olive tree), K:041 (through the gate) **H** |
| Police parking | w1044731109 | ~~x 575-600, y -121..-95~~ **x 565-604, y -107..-64** (review, R3: OSM polygon; W of the south corridor, S of the plaza's main body, N of the entrance roof; 95 % of it lies in s06) | K:021 (full of white police vans) **H** |
| Robinson's Arch springer | n9351437161 | (668,-89), on the west face, ~19 m N of the SW corner | K:030 (frontal), K:044 and K:033 (springer on the left/west face next to the corner) **H** |
| SW corner of the Haram / Southern Wall | w1080613975 | corner (671,-108), wall runs to (948,-61) | K:044, K:032, K:033 **H** |
| Fakhriyya minaret | ~~not in OSM~~ **n13792233802** (man_made=tower, tower:type=minaret) | ~~on the SW corner block, ≈ (670,-100) ± 8 m~~ **(686.7,-81.5)**: on the Islamic Museum block w291836691, ~17 m E of the west face and ~26 m N of the south face, NOT on the corner (review, R1) | K:024 panorama: minaret at x≈1117 between the Mughrabi Gate (x≈907) and Robinson's springer (x≈1140-1193); OSM position predicts x≈1112, (670,-100) would predict x≈1204. K:007 agrees. K:044 and K:032 cannot fix the depth: both look along the corner→minaret line (bearing ~31° from the corner) **H** |
| Davidson Center | w147608624 | (639..679, -194..-165) | OSM; K:046/K:047 interior only **L** for the exterior |
| Ophel park ticket office | n1608094099 | (613,-182) | OSM **M** |
| Dung Gate | n29944308 / w1545285986 | (628,-200); the wall runs (597,-205) → (628.8,-199.6) → (759.6,-178.7), i.e. bearing ~81°, gate faces ~~SSE~~ S (171°, S by E; review R9). OSM passage w1545285986 is 4.3 m wide × 2.3 m deep | K:041 frontal from (634,-223) looking N, K:039 along the outer face from the W, K:037 inner face **H** |
| Tanners' Gate (pedestrian passage) | n5003920349 | (597,-205) | K:039 (flat-lintel passage W of the Dung Gate, gate in the distance) **H** |
| Umayyad Palace Square (park) | w44376174 | (702..751, -165..-122), ~~38~~ 34 OSM tree nodes in x 707-770, y -176..-126 (review R11) | OSM **H** (not photographed closely) |
| Western Wall Observation Point (JQ, top of the stairs) | n321745309 | (532,-24) | K:024, K:026 (panoramas from there) **H** |
| JQ steps to the plaza "HaKotel HaMaaravi" | w26493217, w722734608, w722734615, w26493216, w659765488 | x 519-559, y -22..32 | K:010 (from the top of the NW steps), K:024 **M** |

**Sector polygon warning (H, OSM)**: `data/sectors.json` cuts s07 at y = -40 (box (560,-330,800,-40) in
`pipeline/sectors.py`). By area 80 % of the Western Wall Plaza polygon (4431 of 5564 m²) falls in **s09_wad**,
the prayer-wall strip w817206833 in **s11_haram**, and the JQ steps/observation point in s06/s09. s07 as drawn
holds only the plaza's southern lobe (checkpoint, ramp foot), the archaeological park, the Davidson Center and
the Dung Gate. This note documents the whole plaza as the task asks. If the plaza is to be built with s07 the
box top should be ~y +45 (north end block / bottom of Chain St) and x0 ~515 (top of the JQ steps).

*Review (R4), checked against `data/sectors.json`:* s07's effective west edge is **x = 600**, not 560, because
s06_jewish owns everything at x < 600 south of y = -42. So 12 % of the plaza (685 m²), **95 % of the police
parking** w1044731109, **~60 % of the bus loop** w288065153, the café, the top of the Batei Mahase road and the
SW descent are in **s06**; s07 holds only 8 % of the plaza (449 m²). The observation point n321745309 and the NW
steps are in **s09** (not s06/s09). Moving x0 to ~515 would also need s06 and s09 to give up that strip.

---------------------------------------------------------------------------------------------------

## 1. Sector character and street profiles

**Character.** Not a street sector: a huge, bright, almost empty sloping stone plaza (~85 m E-W × ~80 m N-S
plus a southern lobe) closed on the east by the 59 m prayer face of the Western Wall (pale gold, enormous
drafted ashlars, bushes hanging from the joints) and on the west by a 15-20 m high escarpment of Jewish Quarter
buildings with stairs coming down it. A long covered **timber bridge on steel stilts** slants across the
south-east corner up to the Mughrabi Gate. South of it everything drops into the **archaeological park**
(lawns, ruins, cypresses, the SW corner of the Temple Mount with Robinson's Arch), and a ~~~100 m~~ ~60 m road
(gate → bus loop; the walkway continues to the south entrance, ~100 m in all; review R5) runs down to the low,
wide **Dung Gate** in the south wall. Skyline from the plaza: the Dome of the Rock (gold)
and the Bab al-Silsila minaret to the NE, the Al-Aqsa grey dome and the Fakhriyya minaret to the SE, dark
cypresses and stone pines along the top of the wall. No souq streets, covered markets or vaulted lanes; the
only "shops" are a kiosk inside the Dung Gate, a café at the bus loop (n13537071150 Aroma, (600,-156)) and
booths. "Closed" state = no people, folded parasols, stacked chairs, carts parked.

There is no shop-front profile in this sector. The profiles that apply are below.

### P1. Plaza (OSM "Western Wall Plaza", w26492734; prayer area inside it)
- **Size**: upper plaza x ≈ 565-615 (the open, mostly empty part), prayer area x ≈ 604/627 → wall (see §0).
  Southern lobe x 602-614, y -96..-63 (the corridor from the south entrance). **H** (OSM)
- **Paving**: large rectangular limestone slabs, ~0.5-0.6 × 0.8-1.2 m, running bond in rows parallel to the
  wall, very pale cream to white with some honey/pink slabs, polished smooth by feet (shiny in low sun),
  narrow dark joints; the prayer area has larger, whiter, smoother slabs (~0.6 × 1.2 m). **H** (K:001, K:002,
  K:003, K:012, K:017)
- **Drainage**: round cast-iron manhole covers ~0.7 m (K:009, K:012), long straight drainage channels covered
  with **steel chequer plate / grating ~0.3 m wide** set flush in the paving, one running along the
  prayer-area boundary (K:015, K:009 crop). **H**
- **Level steps inside the plaza**: the area west and south of the prayer enclosure is ~0.45 m higher than the
  strip in front of it: a 2-course limestone plinth (~0.2 + 0.25 m) carrying the railing, with a gentle ramp
  of smoother slabs at the gaps (K:009 crop). The whole plaza falls gently toward the wall and toward the
  south. **M**
- **Prayer-area boundary**: low parapet of smooth ashlar ~1.2 m high with recessed vertical slot panels,
  topped by a **black steel fence ~0.5-0.6 m** (vertical bars) between short square posts, with 3-4 openings;
  small white rule signs on it. **H** (K:015, K:012, K:009)
- **Mechitza**: a ~1.8-2.0 m opaque partition running from the boundary to the wall: panels on a low timber
  plinth with a steel rail on top. Colour/material changes over the years: gold-tan perforated or lattice
  panels (2016-2018, K:017, K:019, K:016), dark brown embossed panels (2021, K:013), dark fabric with white
  parasols (2025, K:003). Model: gold-brown lattice panels, 1.9 m. **H** for position and height
- **Overhead**: nothing (open sky). Parasols only (§4). Lighting from tall masts (§4). **H**
- **Typical clutter (empty plaza)**: grey galvanised crowd barriers in lines or stacks, white monobloc
  chairs in stacks, wheeled Torah tables and bookcases pushed against the boundary, folded white parasols,
  a stainless bin every ~20 m, a police buggy or van at the south edge. **H** (K:003, K:010, K:024, K:026, K:021)

### P2. Stairs from the Jewish Quarter down to the plaza (OSM "HaKotel HaMaaravi": w26493217, w722734608, w722734615 steps; w508242247, w722734611, w722871631 footways; unnamed steps w26493216, w659765488, w722871632)
- Two descents seen: (a) the **NW entrance** (n7253096685 "Entrance to Westwall", (533,3)) → steps w659765488
  + w26493216 down east to the plaza at (559,8); K:010 is taken from their top: a broad stone stair ~4-5 m
  wide that turns into a **paved slope with a row of short steel bollards**, flanked on the north by 3-4
  storey ashlar buildings with barred windows; (b) the **observation-point stairs** (n321745309, (532,-24)):
  steel stairs with brown-red treads and galvanised railings zig-zagging down past corrugated-roof booths
  (K:024, K:026 foreground). **M**
- Risers ~0.15-0.17 m, treads ~0.3-0.35 m on the stone stairs (standard, not the long shallow souq steps);
  intermediate landings. **L** (no close photo)
- Total drop from the JQ edge to the plaza **~15-20 m** (camera height of K:024/K:026 above the plaza; the
  west-side buildings, 3-4 storeys, reach just below the viewpoint). **M**
- Furniture: galvanised tube handrails, globe lamps on short posts (K:010 right), security booths and
  magnetometer gates at the bottom (checkpoints n2915691135 (564,-87), n13927003768 (555,31)). **M**
- The SW descent (long stepped street w29388393 "incline up", 94 m, (557,-106) → (504,-136), and w29388395,
  w368474893, w288016710) lies in s06 and arrives at the bus loop / west checkpoint. **M** (OSM)

### P3. Dung Gate road and walkway (OSM "Batei Mahase" w290693162 out-bound, unnamed service road w935501037 in-bound bus/permit, footway w45081550, steps "מעלות הרב גורן" w288065154)
- **Road**: one asphalt lane, **~4 m**, running ~NNW (337°) from the gate ~~100 m~~ **~60 m** up to the bus loop
  (review R5: gate (628,-200) → loop junction (613,-140); 100 m is the footway w45081550 to the south entrance;
  the two one-way centrelines run only 1.8-2.1 m apart, so they describe one carriageway); both one-way OSM ways
  share the single gate opening (alternating traffic). Red-white painted kerbs at the gate. **H** (K:036, K:037,
  K:041, OSM)
- **Walkway** on the **east** side of the road: 2.5-4 m of limestone slab paving behind short **grey steel
  bollards (~0.9 m, reflective band)** at ~1.5 m spacing, rising gently north, bounded on the east by an ashlar
  parapet/wall (~1.2 m; the park wall w394161622) with railings. **H** (K:036, K:041 through the arch)
- West side: the Ophel ticket office (n1608094099) and the outdoor seating of the café (n13537071151, (605,-172)),
  trees and bedrock outcrops. **M** (K:036, OSM)
- At the top: the bus loop with an oval planted island (olive tree, hedge), bus shelters and a pergola of
  **white steel arches** (seen through the gate in K:041 and in K:009, K:025). Then the steps down to the south
  entrance portal. **M**
- Lighting: tall grey square-section poles with a long horizontal arm and flat LED head (same family as at
  Jaffa Gate), ~8 m. **H** (K:035, K:036, K:042)

### P4. Archaeological-park paths (OSM "Herodian" w288016649; wooden footways w147608627, w755420497; steps w147608631, w288016716 (wood), w755420496 (stone, to the "excavations gate" n2915690864 at (770,-133)); "Umayyad Palace Square" w44376174; unnamed footways w44376170/171/178/185)
- **Herodian street** along the foot of the wall south of the Mughrabi ramp: the original 1st-century paving of
  huge worn slabs (~1 × 2 m), with a **heap of fallen Herodian blocks** (1-3 m) along the wall behind
  galvanised barriers; ~5-8 m wide. **H** (K:029, K:033, K:028)
- Paths between the ruins: smooth pale limestone slabs, 2-3 m wide, with stone kerbs, steel tube railings,
  modern steel stairs with timber treads, and **timber boardwalks / bridges** over excavated rooms (vertical
  timber balusters, dark brown) along the Southern Wall (w147608627). **H** (K:028, K:033, K:044)
- Lawns (OSM landuse=grass w288016650-662) between low reconstructed ashlar walls (0.5-1.5 m), scattered
  architectural fragments on the grass, **olive trees, rows of slim cypresses**, steel shade pergolas (dark
  steel frame, slatted roof ~3.5 m). **H** (K:044, K:032)
- Ezrat Yisrael (egalitarian platform at Robinson's Arch, ≈ (650-665, -60..-90), steps w44376173): a raised
  deck of **anthracite composite boards** with black box benches, big white square parasols on stone bases,
  steel tables, black steel railing over the drop to the Herodian street. **M** (K:031)
  *Review: the platform is not in OSM and only K:031 shows it; that photo shows the SW corner at its right edge,
  which puts the camera nearer y ≈ -95..-103 than -80. Position unverified.*

### P5. Outside the gate (OSM "Maale HaShalom" w23255026 / w378233946, sidewalks w1482457502, w1550608913, crossings n3816384169/70)
- Two-lane asphalt road along the outside of the wall, sidewalk of limestone slabs at the wall foot, square
  limestone bollards (~0.4 × 0.4 × 0.7 m) and round stone planters, zebra crossings, bus stops
  (n5210699479 at (661,-208)). **H** (K:035, K:041, OSM)

---------------------------------------------------------------------------------------------------

## 2. Landmarks

### L1. Western Wall prayer face (w817206833 west edge; s11_haram polygon, faces the plaza = west, ~~~265°~~ ~260°: edge bearings 348°/351°, review R10)
Photos: K:003, K:012, K:016, K:017, K:019, K:010, K:005 (close-up), K:015.
- **Length 59 m** along the plaza (OSM), from the north end block (y ≈ 35) to the bridge landing / Mughrabi
  Gate (y ≈ -23). **H**. The face leans back very slightly (Herodian courses step back a few cm each);
  model it plumb or with a ~1° batter. **L**
- **Visible height ~17 m ± 2 above the prayer floor** (photo-scaled 15-17 m in K:003 and K:016 from people at
  the wall; commonly quoted ~19 m; OSM tags w817206833 height=20). *Review: a course-ratio check on K:003 (7
  Herodian courses ≈ 350 of 770 px floor-to-coping) gives 16-17.5 m, so 17 m stands.* The top is a straight, slightly projecting coping; trees of the Haram
  (stone pines, cypresses) show over it. **M**
- **Three masonry zones**, bottom to top (counted in K:003 crop and K:016 crop, **M** for counts, **H** for the
  zoning):
  1. ~7 courses of Herodian blocks, **~1.0-1.2 m high, 1.5-4 m long, drafted margins 8-15 cm round a flat,
     slightly raised boss**, joints dark and deep; 0-8 m.
  2. ~4 courses of large plain blocks (no drafting), paler and squarer, ~1.0 m; 8-12 m.
  3. ~12-16 courses of small squared stones ~0.35-0.45 m, greyer; 12-17 m.
- Colour: pale honey to cream, whiter where cleaned, grey streaks under projections; lowest ~2.5 m polished
  and darkened by hands, the joints there **stuffed with folded paper notes** (white with some yellow/green)
  up to ~2.5 m. Deeply weathered vertical runnels on many Herodian faces. **H** (K:005, K:003)
- **Plants in the joints**: big drooping caper bushes (0.5-1.2 m clumps, grey-green) and smaller hyssop/grass
  tufts, **mostly 4-12 m up** in zones 1-2, about one clump per 15-25 m²; none in the hand-reach zone. **H**
  (K:003, K:012, K:015, K:017, K:019)
- Against the wall: two **dark-wood Torah arks** (~1.2 × 0.7 × 2.5 m) in the men's section (K:017, K:016),
  a few white cabinets/bookstands. **H**
- In front, men's section: wooden-topped steel bench-desks in rows, wheeled Torah tables with burgundy
  velvet covers, lecterns, white monobloc chairs, white square parasols (§4). **H** (K:003, K:013, K:017)

### L2. North end block over Wilson's Arch (w499210296 hall below; facade on y ≈ 31-35, faces S over the men's section)
Photos: K:002 (from (587,-29) looking NE), K:016 (from the bridge looking N), K:017, K:014, K:003 (left edge).
- A masonry block about as high as the wall (~16-18 m), projecting ~25 m west from the wall and closing the
  men's section. Old rough-faced ashlar, buff-grey. **M**
- Facade (S): **two massive buttresses** from the ground to ~2/3 height; at the base a **round-arched doorway**
  between them and a wider **arched opening near the wall = the entrance into the Wilson's Arch prayer hall**
  (dark interior); upper floors: a row of **3 round-arched windows** near the top and **3-4 small rectangular
  windows with iron grilles** below them. **H**
- West part lower (2 storeys) with an **arcade of round-arched openings** at plaza level, a terrace above, a
  canvas awning, and a **round dial ~1.2 m ("12 tribes" clock)** on its face. **H** (K:014, K:016, K:012 left edge)
  *Review: the K:014 crop shows a ring of ~12 small emblems round a blue-white centre and no clock hands; "clock"
  is unverified, model it as a decorative medallion.*
- Roof edge: clusters of grey loudspeakers and floodlight batteries, small Israeli flags. **H** (K:002, K:016)
- Above and behind it, the **Bab al-Silsila minaret** (s09/s11, ~~≈ (640,72)~~ **OSM n13791836098 at (639.7,84.1)**;
  (640,72) is the Chain Gate node n2953455008, 13 m further S; review R2): square stone shaft, a square
  balcony kiosk on corbels with arched openings, a cylindrical drum and a lead-grey dome with finial,
  ~15 m above the block (unverified); Israeli flags at its base (police post). Skyline marker of the plaza's NE. **H** for
  form (K:002, K:016, K:021); ~~**M**~~ **H** for position (OSM node; in the K:024 panorama the minaret stands
  39 px left of the Dome of the Rock, as the OSM node predicts (35 px), whereas (640,72) would put it 4 px right
  of the dome; in K:016, shot northwards from the bridge, it stands just west of the wall line).

### L3. Mughrabi bridge and gate (w44172764 + w277508271, gate w291836692)
Photos: K:021, K:023, K:013, K:007, K:022, K:019, K:004, K:009, K:012, K:024, K:026; entrance K:018, K:020, K:045.
- **Path** (OSM, **H**): ground-level corridor from the south checkpoint north along x ≈ 612-616 (53 m), then a
  **timber stair tower at (613,-42)**, then the covered bridge rising NE over the south end of the women's
  section to (649,-16), with a short return S/E onto the gate (657,-27). Bridge length ~~~45 m~~ ~50 m from the
  stair tower to the NE corner (649,-16) (OSM: 9 m N to (613.6,-33.3), then ~41 m NE), then an 11 m return S and
  5 m E to the gate (review R12).
- **Stair tower**: box ~4 × 4 m, ~5.5 m tall, clad in horizontal honey-brown timber slats, shed roof of grey
  corrugated sheet, timber stair inside. **H** (K:022, K:021)
  *Review (R14): in both K:021 and K:022 the white hoarding beside the tower reaches ~0.88 of the tower's eave
  height. A 3.5 m hoarding means eaves at ~4 m and a ridge at ~4.6 m; a 5.5 m tower means a ~4.7 m hoarding. One
  of the two figures is off; neither is verified. The tower footprint is also unverified (in K:021 its visible
  face is ~0.45 as wide as it is tall).*
- **Bridge**: enclosed walkway ~3 m wide, ~2.5 m from deck to eaves; **low-pitch grey corrugated-metal roof**
  with small eaves; sides of vertical timber posts at ~0.7 m with **raked diagonal timber struts giving a
  saw-tooth/V lattice**, honey-brown varnished, open between the struts; deck on grey steel beams with a row of
  small floodlights under the edge. **H** (K:023, K:013, K:007)
- **Supports**: 4-5 bents of paired grey steel H-columns with X-bracing, ~8-10 m apart. **H** (K:023, K:019, K:012)
- **Deck height**: ~5 m above the plaza at the stair tower rising to ~9-11 m at the upper landing (slope
  ~7-10°). **L-M** (K:013, K:023 scaled from people)
- **Upper landing**: a timber pavilion with a pitched roof (blue tarp over it in 2017) on a masonry block next to
  the wall, in front of the **Mughrabi Gate**: a pointed-arch doorway in a square gate building that rises
  above the wall line (OSM building:levels 5, height 20). **M** (K:007, K:021, K:013)
- Under and south of the bridge: the remains of the old earth ramp (rubble, shrubs, a palm, timber shoring)
  hidden behind a **white hoarding** (~3.5 m: white panels over brown timber boards on steel posts) that lines
  the plaza's south-east edge from the stair tower toward the women's entrance. **H** (K:022, K:021, K:007)
- **Women's entrance** passes under the low end of the bridge: banner "אין כניסה | כניסה" (no entry | entry,
  red/green), a tan stone pillar sign (see §4), a white event tent and timber booths beneath. **H** (K:004, K:022)
- **Bridge entrance** (by the south checkpoint, ≈ (612,-100)): a stone-clad portal with a white soffit, brown
  (2016) / grey aluminium (2022) sign "הודעה ואזהרה / Announcement and Warning / According to Torah Law,
  entering the Temple Mount area is strictly forbidden due to the holiness of the site. / The Chief Rabbinate of
  Israel", a black LED board with red opening hours, anti-climb spikes on the fence. **H** (K:018, K:020)

### L4. South entrance portal, bus loop, police parking (roof w277508272, loop w288065153, parking w1044731109)
Photos: K:045, K:021, K:025, K:041 (through the gate), K:009.
- **Portal** facing S onto the steps down from the bus loop: square **stone-clad columns (~0.8 m)** carrying a
  flat beam/roof grid ~3.5 m up, beam lettered in dark caps **"כניסה לגברים MEN ENTRANCE"** (left/west lane)
  and **"כניסה לנשים WOMEN ENTRANCE"** (right/east lane), a dark info board between, posters
  ("A LOOK INTO THE PAST", thekotel.org), steel lane barriers, wet stone floor. Roof spans x 584-617 (OSM).
  **H** (K:045)
- **Bus loop**: one-way loop round an oval island (low stone kerb wall, olive tree, hedge), bus shelters, a
  pergola of **white steel arches (~5 m)** on the plaza side, tall lamps. **M** (K:025, K:041, K:009)
- **Police parking** W of the corridor: dozens of white police vans/cars (blue-white livery) on stone paving;
  a flat-roofed building with roof vents on its west side (K:021 foreground). **H** (K:021)

### L5. Southern section of the Western Wall, Robinson's Arch, SW corner (w620099941, w1080613975, n9351437161)
Photos: K:029, K:030, K:033, K:044, K:032, K:028, K:031.
- The wall south of the bridge (x ≈ 658-672) stands on the exposed **Herodian street** several metres below the
  plaza: all-Herodian drafted courses in the lower part (more of them visible than at the prayer face), plants,
  the heap of fallen blocks at its foot. **H** (K:029, K:033)
- **Robinson's Arch springer** (668,-89): a projecting row of arch voussoirs ~12-15 m wide with a ledge,
  ~8-10 m above the Herodian street, a later masonry band above with **3-4 small square grilled windows** of
  the Haram buildings, a cypress on top. **H** (K:030, K:033)
- **SW corner** (671,-108): enormous corner stones with drafted margins, ~25 m above the Herodian street (**L**),
  upper part smaller later masonry with small grilled windows; the **Fakhriyya minaret** ~~on top~~ *behind it*: square
  stone shaft (~3 m), a square balcony kiosk with arched openings, slim cylindrical upper drum, small
  lead-ribbed dome with finial, ~12-15 m above the wall top. **H** for form (K:044, K:032), ~~**M** for position~~.
  *Review (R1): the minaret does not stand on the corner. It is OSM n13792233802 at (686.7,-81.5), on the Islamic
  Museum block ~17 m E of the west face and ~26 m N of the south face, and only lines up behind the corner when
  seen from the SW (K:044, K:032, K:038). Position **H** (OSM + K:024 + K:007, see §0).*
- The Southern Wall runs east from the corner: long plain ashlar face with a row of small square windows high
  up, Al-Aqsa's lead-grey ribbed dome above it, the blocked arches of the Double Gate further east (outside the
  Ottoman wall, s07 edge). **H** (K:044, K:032, K:038)

### L6. Davidson Center (w147608624) and park buildings (w288016670, w288016678, w288016669/71/73)
- Footprint 40 × 25 m just inside the Dung Gate, east of the walkway; housed in vaults of an Umayyad-period
  building. From the walkway: a low (1 storey above the path, ~4-5 m) rough ashlar mass with a flat roof and a
  **modern glazed entrance** on the west (glass doors, grey concrete-panel lobby with stone fragments on plinths,
  black chairs). **L** for the exterior (no photo), **H** for the lobby (K:046, K:047, K:034 bronze city model).
- w288016678 (255 m², x 672-722, y -146..-103) and the small blocks along the wall are reconstructed Umayyad
  palace walls: roofless ashlar walls 1-4 m high around lawns. **M** (K:044, K:032)

### L7. West edge of the plaza: the Jewish Quarter escarpment (w1528632636, w394161633, Aish HaTorah; s06/s09)
Photos: K:001, K:027, K:024, K:026, K:010.
- Along x ≈ 565-575 a **5-6 m retaining wall** (concrete and rubble) over an excavation pit (signs
  "חפירה ארכיאולוגית", "אמת מים / Aqueduct", 2016, K:027); hoarded in 2019 with printed panels (menorah, crowd
  scenes, Jerusalem) on **black steel mesh fencing ~2.5 m** and a "שוהם הנדסה ופיתוח" site board (K:001); a new
  building has been going up there since. Model the 2019 hoarding state. **H**
- Above it, w1528632636 (contains n14073003968 "Colel Chabad Free Kitchen"): terraced 3-5 storey ashlar
  buildings with **large semicircular arched glazed windows**, balconies with railings, steel pergolas, white
  domes and vaults on the roofs; letters **"COLEL CHABAD / FREE KITCHEN FOR THE NEEDY"** on a stone band and
  **"SIMCHA HALL.com 02-627-5251"** along the parapet. **H** (K:027)
- Higher up to the west: **Aish HaTorah World Center**, a 5-6 storey ashlar block with tower-like projecting
  bays, paired round-headed windows, a glazed rooftop pavilion, metal letters "AISH HATORAH WORLD CENTER" high
  on the left, Israeli flags on poles below (K:001 crop). Exact footprint uncertain, ≈ x 500-535,
  y -30..5 (OSM's "Aish Torah Yeshiva" w290725352 at (461,-223) is a different building). **L** position, **H** form
- **NW block w394161633** (police station n14073079423 at its W end): ~~2-3 storeys~~ **3 storeys** facing the plaza
  above a raised front terrace, ~12.5 m to the parapet (review: scaled from people standing on the terrace in the
  K:002 crop; the top storey is behind the banner; OSM says building:levels=5, which probably counts levels below
  the plaza; only one photo, **M**), large square
  windows, glazed ground floor, a white steel pergola and banner frame on the roof (Passover banner "חג פסח
  כשר ושמח" in 2019). **M** (K:002)

### L8. Skyline seen from the sector (other sectors, massing only)
- Dome of the Rock (gold dome, blue-tiled drum) NE beyond the wall top; Al-Aqsa (lead-grey ribbed dome) SE;
  Bab al-Silsila and Fakhriyya minarets; the Mount of Olives with its cemetery and the Russian bell tower to the
  E; Silwan to the SE. **H** (K:021, K:024, K:007, K:038)
- Porat Yosef yeshiva (w290726629) closes the SW view above the bus loop (tall ashlar, white domes). **L**

---------------------------------------------------------------------------------------------------

## 3. The Dung Gate (n29944308, (628,-200); "שער האשפות / باب المغاربة / DUNG GATE")

Photos: K:041 (frontal from (634,-223), 2015), K:036 (frontal close, 2025), K:035 (outside looking WNW, 2025),
K:039 (along the outer face from the Tanners' Gate, 2018), K:037 (inner face from the N, 2025), K:040/K:043
(name tiles), K:038 (from the wall walk). Measurements from K:041 at ~49 px/m on the wall plane (scale from the
3.85 m vehicle-clearance signs; consistent with the guard booth).
*Review (R7): K:041 (2015) shows no "3.85" discs (they appear only in the 2025 photos K:036/K:037), so they cannot
be its scale. An independent scale from the soldier by the booth (~107 px for ~1.75 m, standing ~3 m in front of
the wall) gives ~53 px/m at the wall, so figures below carry ±8 %. OSM gives the passage as 4.3 m wide.*

- **Type**: a small Ottoman postern in the straight south wall, **widened in the 20th century into a single
  vehicle arch**; the original decorated head was kept above the new opening. No gate tower, no bend.
  Wall here ~2.5-3 m thick. **H** (form), **M** (thickness)
- **Opening (both faces)**: clear **~4.2 m wide × ~4.0 m to the crown**; vertical jambs to ~~~2.6 m~~ **~3.0-3.2 m**, then a
  **depressed round (basket-handle) arch** with a rise of only ~1.0-1.1 m (review R7: in K:041 the front-face jambs
  stay vertical from the road at y≈772 to y≈611, 160 px, and the intrados crown is at y≈560, 212 px, i.e. 3.0-3.3 m
  and 4.0-4.3 m at 49-53 px/m; with 2.6 m jambs a bus-width vehicle would have only ~3.7 m under the arch, less than
  the posted 3.85 m); arch ring of large smooth voussoirs ~0.45-0.6 m deep projecting
  slightly; height-limit discs **"3.85"** (red ring) on poles on both sides of both faces. **H** (K:041, K:036, K:037)
- **Outer face decoration** (centred over the opening; **H**, K:036 crop, K:041, K:039):
  - a **pointed hood moulding** ~4.1 m wide × ~2 m tall (plain roll) whose ends drop as short vertical returns,
    springing from two small impost blocks at ~5.0 m;
  - inside it a **semicircular arch band of ~25 radial convex lobes ("cushion" voussoirs)** ~3 m wide;
  - the tympanum filled with plain ashlar holding a small worn rectangular carved panel and below it a square
    block with a **hexagram**; beneath, the plain lintel band of the old gate (~4.2-5.0 m);
  - **one rosette** (double ring of 8 petals, ~0.8 m) centred ~7.9 m up, with a blank rectangular panel
    (~1.0 × 0.35 m) above it.
- **Crenellation**: **flat rectangular merlons ~2.2 m wide × ~0.9 m tall**, embrasures ~0.65 m, a narrow slit in
  some merlons; merlon tops **~11.3 m above the road** at the gate. CCTV camera clusters and loudspeakers on
  poles on the merlons (2025). **M** (K:041, K:036)
- **Inner face** (K:037, **H**): no decoration; the same opening framed by a broad plain arch ring; rougher,
  greyer masonry with plants; at the top the **Ramparts Walk** with a black steel railing on the inner edge and
  the backs of the merlons with **pointed-arch embrasure niches**; the green-framed **ceramic name tile
  (≈ 0.9 × 0.6 m [review: 4 × 3 tiles; scaled against the ~0.35 m courses in K:043 it is nearer 0.7 × 0.55 m;
  unverified], white tiles, black Hebrew / Arabic "باب المغاربة" / English "DUNG GATE", green border with
  white guilloche)** left (east) of the arch at ~3.5 m; a dark green info board and a grey bin on the right.
  **M** for which face holds the tile (K:037 shows a framed plaque there; K:040, K:043 show the tile beside large
  arch voussoirs).
- **Stone**: outer face warm honey limestone, large regular courses (~0.5-0.6 m), tooled faces; inner face
  rougher and greyer. **H**
- **Outside (S)**: Ma'ale HaShalom road (asphalt) along the wall; a **white guard booth** (~2 × 2 m, ~2.7 m, flat
  overhanging roof) W of the gate; blue police barriers; no-entry signs with orange plates "EXCEPT AUTHORISED
  VEHICLES"; a blue direction sign; ~~**two**~~ **three date palms (~10-12 m)** E of the gate and an **olive tree** W of it
  (review R6: K:041 shows three trunks, two close together just E of the arch and a third ~4 m further E; K:038
  (2018, from above) shows three in a row. Neither the palms nor the olive appear in the 2025 photos K:035 (taken E
  of the gate looking WNW, with the ground E of the gate in view) or K:036, so they may have been removed. This is
  the 2015-2018 state; the 2025 state is unverified);
  square limestone bollards and round stone planters; a ka'ak cart with red umbrella; a glazed police kiosk
  further W (2025) and a large stone block barrier in front of the gate; tall grey inverted-L LED lamps; Israeli
  flags on short poles fixed to both jambs (2025). **H** (K:041, K:035, K:036)
- **Inside (N)**: the single lane continues N, red-white kerbs, a small **café kiosk ("קפה")** with a flat roof
  and AC unit on the E side right inside the gate, a paved strip with grey bollards, bedrock outcrops and shrubs
  on the W, then the walkway (P3). **M** (K:037, K:036)
- **West of the gate** (outside): the excavated **Tanners' Gate** zone: low reconstructed walls, a fan-patterned
  paving of small stones with a central gutter (K:042), and the flat-lintel passage through the wall with a
  black steel gate (n5003920349, (597,-205); K:039). **H**

---------------------------------------------------------------------------------------------------

## 4. Street furniture, signage, vegetation

### Lighting
- **Plaza**: a few **tall slim grey masts (~15-20 m)** carrying clusters of floodlights and loudspeakers
  (K:001 left, K:009 centre); floodlight batteries and loudspeaker clusters on the north end block roof
  (K:002, K:016); small floodlights under the bridge deck (K:023); **white globe lanterns on short posts** along
  the NW stairs and railings (K:010). Night: the wall is floodlit warm white. **M**
- **Park / ramp area**: black lamp posts with lantern heads (K:007, near the wall south of the bridge). **L**
- **Road and outside the gate**: grey square-section **inverted-L poles with flat LED heads (~8 m)**, single or in
  pairs. **H** (K:035, K:036, K:042)

### Furniture on the plaza and in the prayer area (closed / empty state)
- **White square parasols** (~4 × 4 m canvas, white steel pole ~3 m, square rough stone base ~0.5 m), dozens in
  rows along the mechitza and the wall in both sections; folded when closed. **H** (K:003, K:012, K:013, K:031)
- **White monobloc chairs**, loose and in tall stacks. **H**
- **Torah reading tables**: wheeled steel frames with burgundy/red velvet covers (~1.2 × 0.8 × 1.0 m), and
  wooden-topped bench-desks in rows (men's section). **H** (K:013, K:017, K:003)
- **Bookcases on castors**: brown wooden frames, 2-3 shelves of prayer books, white lower panel printed
  "Reaching Our Essence / The Western Wall Heritage Foundation" with the Foundation logo and the state emblem
  (~1.5 × 0.5 × 1.5 m). **H** (K:006)
- **Two dark-wood Torah arks** against the wall (men's section) and wooden lecterns. **H** (K:017, K:016)
- **Hand-washing fountains** (OSM n6177045582 (601,-28), n14016046564 (599,12)): cream marble quatrefoil basin
  ~1.4 m across on a column pedestal, central pillar with a brass band and 4 chrome taps, stainless two-handled
  washing cups. **H** (K:015, K:009)
- Drinking fountains (n2820132149 (593,27), n6992219960 (590,15)), toilets (n9612921883 (566,15),
  n571603036 (580,29); n1490556693 (609,-160) at the bus loop). **M** (OSM)
- **Bins**: stainless steel rectangular slotted bins with clear bag liners on the plaza (K:001, K:004, K:009);
  dark grey round perforated bins at the Dung Gate (K:036, K:037). **H**
- **Crowd barriers**: grey galvanised steel barriers in lines and stacks (K:010, K:024, K:026, K:029). **H**
- **Event tents**: white gable-roofed tents (~6 × 10 m) near the women's entrance and in the men's section on
  busy days (K:004, K:014). Optional. **M**
- Vehicles: white police vans/cars (blue stripe) in the SW parking and a police buggy at the plaza's south edge
  (K:021, K:009). **H**

### Signs and plaques
- **"Welcome to the Western Wall" sign wall** (≈ (577,-61), position **L**): free-standing wall ~2.8 m × 6.5 m
  clad in beige stone panels with brass trim; centre aluminium panel "ברוכים הבאים אל הכותל המערבי / שריד בית
  המקדש / Welcome to the Western Wall / a remnant of the Temple" + Psalm 122:6-7; four tall frosted-glass
  panels (directions, rules with pictograms, history); three small bronze emblems on top. **H** for the object (K:011)
- **Women's prayer-plaza pillar**: tan stone-clad square pillar ~2.5 m "רחבת תפילה נשים / The Prayer Plaza
  Women" with black triangle arrows, at the women's entrance under the bridge. **H** (K:004)
- **Entrance banners**: white fabric banners "כניסה" (entry, blue or green text with arrows) and "אין כניסה"
  (no entry, red with a red no-entry disc) at the women's entrance and the north end. **H** (K:004, K:022, K:002)
- Black/bronze info monoliths (~0.5 × 0.3 × 2.2 m) at the prayer-enclosure gaps; small white rule signs on the
  parapet; a free-standing "Welcome" rules board ("thekotel.org *5958") at the women's entrance. **H** (K:009, K:004)
- **South entrance**: "כניסה לגברים MEN ENTRANCE" / "כניסה לנשים WOMEN ENTRANCE" on the portal beam. **H** (K:045)
- **Bridge entrance**: Chief Rabbinate "Announcement and Warning" sign + red LED hours board. **H** (K:018, K:020)
- **Dung Gate**: ceramic name tile (see §3), "3.85" discs, no-entry + orange "EXCEPT AUTHORISED VEHICLES"
  plates, blue lane-direction sign. **H** (K:040, K:043, K:036, K:041)
- **West edge lettering**: "AISH HATORAH WORLD CENTER", "COLEL CHABAD / FREE KITCHEN FOR THE NEEDY",
  "SIMCHA HALL.com 02-627-5251"; excavation hoarding prints and a contractor board. **H** (K:001, K:027)

### Flags
- An **Israeli flag on a tall pole (~10-12 m)** at the prayer-enclosure boundary in front of the wall (K:012,
  K:009, K:021); 4-5 flags on poles below the Aish HaTorah building (K:001); flags on the north end block and at
  the Bab al-Silsila minaret (K:002); small flags on both jambs of the Dung Gate (2025, K:036). **H**

### Vegetation
- **On the Western Wall**: caper bushes and tufts in the joints, 4-12 m up, ~1 per 15-25 m² (see L1). **H**
- **Above the wall top**: 3-4 tall dark cypresses and a mass of umbrella pines on the Haram behind the prayer
  face, more cypresses over the SW corner and the Islamic Museum. **H** (K:003, K:012, K:022, K:044)
- **The plaza itself: no trees, no planters.** **H**
- **South-east of the plaza** (old ramp area, behind the hoarding): a palm, shrubs and a cascade of **magenta
  bougainvillea** on the wall south of the bridge. **H** (K:007, K:013, K:029)
- **Archaeological park**: mown lawns (OSM landuse=grass), **olive trees**, **rows of slim cypresses**, a few palms;
  ~~38~~ 34 OSM tree nodes around Umayyad Palace Square (x 707-770, y -126..-176; review R11). **H** (K:044, K:032, OSM)
- **Dung Gate**: ~~two~~ three date palms E and an olive W outside (K:041, K:038; 2015-2018 state, not seen in 2025
  K:035/K:036; review R6). The palms are not in OSM: the OSM trees at (654,-199) etc. are 26-49 m E of the gate; trees along Ma'ale HaShalom (OSM trees at
  (654,-199), (671,-196), (677,-195) and a row y -184..-201 E of x 711); inside, shrubs on bedrock W of the
  road. **H**
- **City wall plants**: tufts and small caper bushes scattered on both faces near the gate, a cypress and
  hanging green at the wall step W of the gate. **H** (K:035, K:037, K:039)
- Bus-loop island: an olive tree and clipped hedge. **M** (K:025)

---------------------------------------------------------------------------------------------------

## 5. Terrain

SRTM (`pipeline/terrain.py` tiles, 30 m, smoothed by the steep JQ slope): JQ observation point 751.8, plaza
centre 736.1, plaza S tip 733.9, bus loop 735.6, Robinson's Arch 724.2, Dung Gate 722.7, outside the gate 719.6,
Umayyad square 720.9, SE corner 711.8 m. Useful for the overall fall to the south-east; not for steps.
Photo-based levels below use the plaza in front of the prayer enclosure as datum **P = 0**.

| place | level vs P | evidence | conf. |
|---|---|---|---|
| Prayer area floor (in front of the wall) | ≈ -0.45 | 2-course plinth with railing and ramp at the gaps (K:009 crop) | M |
| Upper plaza W and S of the enclosure | 0 → +1 rising gently westwards | K:010, K:024 | M |
| JQ observation point / top of the NW stairs | +15..+20 | camera height of K:024/K:026; 3-4 storey west-edge buildings reach just below it | M |
| Wall top (coping) | ≈ +17 | L1 | M |
| Mughrabi Gate sill / upper landing | ≈ +9..+11 → **≈ +9** | bridge deck height (K:013, K:023). *Review: surveyed sill 736.5 m ASL (Caspi / Warren anchor in `data/terrain_street.json`) against prayer floor 727.0 → +9.5 above the prayer floor, ≈ +9 vs P* | ~~L~~ H |
| South entrance portal (610,-95) | ≈ 0 | level corridor into the plaza (K:045) | M |
| Bus loop (595,-130) | ≈ +1.5..+3 | steps w288065154 "incline down" eastwards to the checkpoint; K:045 shot from above the lanes. *Review: OS 1865 spot height at (595.9,-112.4) = 731.5 m (+4 vs P) and the street model gives 733.9 at (597,-130). Both are older or interpolated ground, but they suggest +3..+5; unverified* | M |
| Dung Gate road at the gate | ≈ -4 (±3) | SRTM says ~11 m below the plaza; the view through the arch (K:041) shows the road inside climbing only ~3 %. *Review (R15): `data/terrain_street.json` gives 724.1 m ASL at the gate, i.e. -3 vs the prayer floor, -5 vs the 729.0 plaza flat, so -4 stands. But it rises to ~730 by (617,-165) and ~734 at the bus loop, a ~10-15 % climb. A 3 % climb also contradicts this table's own bus-loop row (+1.5..+3 above P with the gate at -4 means ~6 m in ~60 m). The "3 %" is unverified; use `street_z`* | L |
| Herodian street at the SW corner | ≈ -5..-8 | deck of Ezrat Yisrael (K:031) and stairs down (w44376173, 34 m) above it; many more Herodian courses exposed (K:029, K:033) | L |
| Outside the gate, Ma'ale HaShalom | falls ~6 % eastwards toward the Kidron; rises westwards along the wall toward the Tanners' Gate | K:035, K:038; SRTM 719.6 → 711.8 over 130 m | M |

Stair runs (OSM `highway=steps`):
- w26493216 (20 m) + w659765488 (10 m): JQ → plaza NW entrance at (559,8). w26493217 (13 m), w722734615 (6 m),
  w722734608 (2 m), w722871632 (11 m): the observation-point stairs. Together ~15-20 m of drop (P2). **M**
- w288065154 "מעלות הרב גורן" (13 m): bus loop → south checkpoint, down eastwards, ~1.5-3 m. **M**
- w288016708 (14 m, (605,-153) → (594,-149)): bus loop → Batei Mahase sidewalk / JQ. **L**
- w288016709 (10 m, (628,-126) → (620,-130)): park side → road. **L**
- w44376173 (34 m, (635,-92) → (661,-80)): south corridor → Ezrat Yisrael / Herodian street, ~4-6 m down. **L**
- w44376172 (6 m) in the park near the SW corner; w147608631 (8 m, timber) + w288016716 (20 m, timber) +
  w755420496 (27 m, stone): the SE path climbing onto the wall to the "excavations gate" viewpoint n2915690864
  at (770,-133). **M** (OSM), heights **L**
- The SW descent from the JQ (w29388393 94 m, w29388395 39 m, w368474893 22 m, w288016710 41 m) is in s06. **M**
- w147608622 "Ancient Drainage Tunnel" is underground (layer -1) from the City of David; only its exit near
  Robinson's Arch (663,-89) is on the surface. Do not model the tunnel. **H** (OSM)

Platforms and terraces: the prayer area (one step down), the Ezrat Yisrael deck, the Umayyad palace terraces
stepping down to the south-east, the bus-loop terrace above the south entrance, the stepped JQ escarpment. **M**

---------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **The Western Wall prayer face** (w817206833 W edge, 59 m × ~17 m): three masonry zones (≈7 drafted
   Herodian courses of 1.0-1.2 m, ≈4 big plain courses, 12-16 small courses), pale honey stone, caper bushes
   hanging from the joints 4-12 m up, paper notes in the joints below 2.5 m, straight coping with Haram cypresses
   and pines showing over it. (L1)
2. **The empty plaza**: one huge surface of large pale polished limestone slabs (0.5-0.6 × 0.8-1.2 m, running bond),
   no trees, falling gently to the wall; round manholes and flush steel drainage strips. (P1)
3. **Prayer enclosure and mechitza**: 1.2 m smooth parapet + black fence along (604,-32) → (620,-20) → (618,-7) →
   (614,16) → (627,18) (review R13: OSM w45081552 vertices, not a straight line) with gaps
   and a 0.45 m step down; the 1.9 m gold-brown mechitza from (618,-7) to the wall at (652,-2): men N, women S. (P1, §0)
4. **The Mughrabi bridge**: timber stair tower at (613,-42), then a covered walkway (grey corrugated roof,
   saw-tooth timber lattice sides) on paired grey X-braced steel bents, rising from ~5 m to ~10 m over the south
   end of the women's section to a timber landing at the pointed-arch Mughrabi Gate; white hoarding beneath. (L3)
5. **North end block** over Wilson's Arch: two buttresses, arched doorways, small grilled windows, the round clock,
   loudspeakers on the roof; the Bab al-Silsila minaret above it. (L2)
6. **The Dung Gate**: single depressed-arch opening ~4.2 × 4.0 m (vertical jambs ~3.1 m, arch rise ~1.1 m; review R7) in the straight crenellated wall (merlons
   2.2 × 0.9 m, tops ~11.3 m); outer face with the pointed hood, the lobed (cushion-voussoir) arch, hexagram
   block and rosette; plain inner face with the Ramparts Walk railing; "3.85" discs. (§3)
7. **West edge backdrop**: the hoarded excavation and retaining wall at x ≈ 565-575, terraced JQ buildings with
   big arched windows and the "COLEL CHABAD" / "SIMCHA HALL" lettering, Aish HaTorah's towered block higher up,
   the NW block with its roof pergola; the stairs coming down it. (L7, P2)
8. **Skyline**: gold Dome of the Rock to the NE, grey Al-Aqsa dome and the Fakhriyya minaret to the SE, the Bab
   al-Silsila minaret, the Mount of Olives behind. Review (R1, R2): use the OSM minaret nodes, Fakhriyya
   n13792233802 (686.7,-81.5) on the Islamic Museum block (not on the SW corner) and Bab al-Silsila n13791836098
   (639.7,84.1). Massing only, but always in view. (L8)
9. **Prayer furniture in the closed state**: folded white square parasols in rows, stacked white chairs, wheeled
   Torah tables with burgundy covers, wooden bookcases, two dark Torah arks, the two marble hand-washing
   fountains. (§4)
10. **Dung Gate surroundings**: white guard booth and olive W, ~~two~~ three date palms E (2015-2018 state; not seen in 2025; R6), square stone bollards, red-white
    kerbs, blue barriers, inverted-L lamps outside; kiosk, bollarded walkway and single asphalt lane inside. (§3, P3)
11. **The road and walkway from the gate to the plaza** (~60 m road to the bus loop, ~100 m walkway to the south entrance, climbing; R5), the bus loop with its planted island and
    white steel arch pergola, the police parking full of white vans, then steps down to the **MEN / WOMEN ENTRANCE**
    portal and the corridor into the plaza. (P3, L4)
12. **SW corner and Robinson's Arch** seen from the south corridor and the Ezrat Yisrael deck: huge drafted corner
    stones, the springer, the heap of fallen blocks on the Herodian street 5-8 m below the plaza. (L5)
13. **Archaeological park**: lawns between low ruin walls, olive trees and slim cypress rows, steel pergolas, timber
    boardwalks, the low Davidson Center with its glazed entrance near the gate. (P4, L6)
14. **Levels**: plaza datum, prayer area one step down, JQ 15-20 m up with stairs, bus loop a flight above the south
    entrance, Herodian street 5-8 m down, the road falling to the gate and Ma'ale HaShalom falling east outside. (§5)
15. **Signs and lights**: the "Welcome to the Western Wall" sign wall, the women's prayer-plaza pillar, entry / no-entry
    banners, the Chief Rabbinate warning at the bridge entrance, the Dung Gate tile; tall floodlight masts with
    loudspeakers, globe lanterns on the stairs, the Israeli flag on its tall pole by the prayer enclosure. (§4)

---------------------------------------------------------------------------------------------------

## 7. Photo table (K:NNN = `data/photos_ref/s07_kotel/NNN_*.jpg`)

Viewpoints marked * were corrected from the content (geotag wrong or missing).
*Review (R8): the geotags of K:028, K:029 and K:030 are rounded to whole arc-seconds (they differ by exactly 26.2 m
in x and 30.7 m in y), so treat them as ±15 m. K:023's geotag (647.6,2.4) at the wall contradicts its broadside
view of the bridge; the camera was on the upper plaza W of the bridge.*

| K | year | viewpoint → direction | shows |
|---|---|---|---|
| 001 | 2019 | (585,-11) → W | west edge: hoarding, Aish HaTorah World Center, bin, plaza paving |
| 002 | 2019 | (587,-29) → NE | north end block, Bab al-Silsila minaret, wall, NW block with banner |
| 003 | 2025 | *≈(615,5) → E | men's section furniture, mechitza on the right, wall courses, bridge top |
| 004 | 2025 | *≈(612,-30) → SE | women's entrance under the bridge, "Prayer Plaza Women" pillar, bin |
| 005 | 2025 | at the wall | close-up of Herodian stones, notes in the joints |
| 006 | 2025 | (616,36) | wooden bookcase carts |
| 007 | 2025 | (535,-17) → ESE | bridge and Mughrabi Gate landing, Al-Aqsa, wall S of the bridge, bougainvillea |
| 008 | 2025 | (538,41) | lane near Chain St (minor) |
| 009 | 2018 | (607,-8) → SSW | prayer-enclosure step and railing, fountain, monolith, bridge, south pergola |
| 010 | 2018 | *≈(535,5) → ESE | NW stairs down into the plaza, whole wall, bridge, Al-Aqsa |
| 011 | 2021 | (577,-61) | "Welcome to the Western Wall" sign wall |
| 012 | 2021 | (582,-7) → E | plaza paving, enclosure parapet, flagpole, bridge on steel bents |
| 013 | 2021 | (640,7) → SSW | bridge rising to the gate, men's section tables and parasols |
| 014 | 2021 | *from the bridge, ≈(630,-20) → N | men's section from above, north block facade, clock |
| 015 | 2018 | *at fountain n6177045582 (601,-28) or n14016046564 (599,12) → E | hand-washing fountain, parapet with black fence, drainage strips |
| 016 | 2018 | (634,-18) on the bridge → N | women's and men's sections, mechitza, north block, minaret |
| 017 | 2016 | (623,-28) on the bridge → NNE | men's section, mechitza, Torah arks, north block |
| 018 | 2016 | (618,-107) | bridge-entrance warning sign and LED board |
| 019 | 2016 | (614,7) → SE | women's section, mechitza lattice, bridge end on X-braced steel |
| 020 | 2022 | (604,-90) | warning sign (grey version) |
| 021 | 2017 | (551,-117) → NE | overview: police parking, plaza, bridge path, gate, Dome of the Rock |
| 022 | 2019 | plaza → E | bridge stair tower, white hoarding, women's entrance banner |
| 023 | 2016 | plaza → SE | bridge broadside: lattice sides, roof, steel bents |
| 024 | 2016 | (522,-26) → E | panorama from the observation point: west edge, stairs, plaza, bridge |
| 025 | 2016 | (561,-126) → E | sunset panorama: bus loop island, pergola, park, SW corner |
| 026 | 2016 | (539,-24) → E | panorama from the observation point |
| 027 | 2016 | plaza → W | JQ escarpment, retaining wall, Colel Chabad / Simcha Hall lettering |
| 028 | 2018 | (653,-118) → E along the Southern Wall (wall on the left) | Herodian corner masonry, park stairs, timber walkway |
| 029 | 2018 | (653,-88) → ~~E~~ **N/NNE** along the west face (wall on the right, bridge landing with blue tarp at the far end; review R8) | wall S of the ramp, fallen stones, barriers, plants |
| 030 | 2018 | ~~(627,-88)~~ *≈(658-662,-90), right below the springer, looking up steeply E (review R8: the strong upward perspective rules out a camera 40 m away) | Robinson's Arch springer |
| 031 | 2018 | *≈(655,-80) | Ezrat Yisrael deck, parasols, black benches |
| 032 | 2018 | *≈(640,-150) → ENE | SW corner, Fakhriyya minaret, Southern Wall, park |
| 033 | 2025 | (659,-109) → NE | SW corner close, Robinson's Arch, fallen stones |
| 034 | 2026 | Davidson Center | bronze relief model of the city (interior) |
| 035 | 2025 | outside, E of the gate → WNW | gate outer face, wall to the W, booth, lamps, bollards, hydrant |
| 036 | 2025 | just S of the gate → N | outer face close: arch, Ottoman head, rosette, merlons, 3.85 signs |
| 037 | 2025 | inside, N of the gate → S | inner face, Ramparts Walk railing, name tile, kiosk, bollards |
| 038 | 2018 | on the wall W of the gate → E | wall walk, wall to the E, Al-Aqsa, palms outside |
| 039 | 2018 | outside at the Tanners' Gate → ENE | outer face, Tanners' Gate passage, Dung Gate in the distance |
| 040 | 2016 | at the gate | ceramic name tile |
| 041 | 2015 | (634,-223) → N | gate frontal (measured), booth, palms, olive, through-view to the bus loop |
| 042 | 2025 | (606,-209) | Tanners' Gate excavated court, fan paving, lamps |
| 043 | 2013 | at the gate | ceramic name tile beside the arch voussoirs |
| 044 | 2016 | (631,-176) → NNE | SW corner, Fakhriyya minaret, Robinson's springer, lawns, cypresses, pergola |
| 045 | 2017 | *≈(610,-112) → N | south entrance portal MEN / WOMEN ENTRANCE, bridge beyond |
| 046 | 2025 | Davidson Center lobby | interior (glass doors, concrete panels) |
| 047 | 2025 | Davidson Center lobby | interior, stone fragments |

---------------------------------------------------------------------------------------------------

## Review

Independent review, 2026-10-19. I opened all 47 photos (cropped and measured the key ones) and looked up every
OSM id in §0 in `data/osm_local.json`. I also checked `data/sectors.json` and the survey-based street terrain
`data/terrain_street.json`. Corrections are made in place in the body; struck text is the original, and
*Review* notes mark additions. Verdict: the sector is well documented and most positions hold. Two landmark
positions were wrong (R1, R2), one OSM bbox was wrong (R3), the sector-boundary analysis missed s06 (R4), and the
Dung Gate profile and its surroundings needed fixes (R6, R7).

### Corrections

- **R1 Fakhriyya minaret: wrong position (major).** The notes said "not in OSM, on the SW corner block,
  ≈ (670,-100) ± 8 m". It is in OSM as **n13792233802** (`man_made=tower`, `tower:type=minaret`) at
  **(686.7,-81.5)**. That puts it on the Islamic Museum block w291836691, about 17 m E of the west face and 26 m N
  of the south face, about 25 m from the stated point.
  - K:044 and K:032 cannot confirm the corner position. Both are taken from the SW, close to the line through
    the corner and the minaret (bearing ~31° from the corner), so the minaret lines up behind the corner from
    either spot position.
  - The check that decides it is the K:024 stitched panorama from the observation point (522,-26.6), where pixels
    track bearing. Reference points: the Mughrabi Gate doorway is at x≈907 and the SW corner at x≈1230
    (11.5 px/°). On that scale Robinson's springer should sit at x≈1168; it is observed at 1140-1193.
  - The minaret is observed at x≈1117. The OSM node predicts 1112; (670,-100) would predict 1204, above the right
    half of the springer.
  - K:007 agrees. With the OSM node, K:007's Al-Aqsa dome ray crosses K:024's on the mosque, at about
    (696..735,-60..-68). With (670,-100) the two rays would cross on the plaza at (606,-43).
  - Fixed in §0, L5 and checklist item 8.
- **R2 Bab al-Silsila minaret: wrong point.** The notes placed it at (640,72), which is the Chain Gate node
  n2953455008. The minaret is OSM **n13791836098 at (639.7,84.1)**, 13 m further N.
  - In K:024 it stands 39 px left of the Dome of the Rock. The OSM node predicts 35 px left; (640,72) would put it
    4 px to the right.
  - Fixed in L2 and checklist item 8.
- **R3 Police parking bbox wrong.** w1044731109 spans **x 565-604, y -107..-64**, not x 575-600, y -121..-95. The
  stated box would overlap the bus loop.
  - The true box puts the parking W of the south corridor, which is what K:021 shows.
- **R4 Sector boundary analysis incomplete.** In `data/sectors.json`, s06_jewish owns x < 600 south of y = -42,
  so s07 effectively starts at x = 600.
  - s06 therefore holds 12 % of the plaza (685 m²), 95 % of the police parking, ~60 % of the bus loop, the café
    and the SW descent.
  - The observation point and the NW steps are in s09 only.
  - The suggested x0 ≈ 515 would also need s06 and s09 changed. Added to the §0 warning.
- **R5 Road length.** The road from the gate (628,-200) to the bus-loop junction (613,-140) is **~60 m**, not
  100 m. The 99 m figure is footway w45081550, which runs from the gate to the south entrance (616,-104).
  - The two one-way OSM centrelines are only 1.8-2.1 m apart, so they describe one carriageway.
  - Fixed in §1 and P3.
- **R6 Dung Gate trees.** There are **three date palms** E of the gate, not two. K:041 shows three trunks (two close
  together, a third ~4 m E); K:038 (2018, from above) shows three in a row.
  - Neither the palms nor the olive W of the gate appear in the 2025 photos K:035 (taken from E of the gate,
    looking W along the face) or K:036. They may have been removed.
  - The notes now say "2015-2018 state" and leave 2025 unverified.
  - The OSM trees at (654,-199), (671,-196) and (677,-195) are 26-49 m E of the gate and are not these palms.
- **R7 Dung Gate opening profile and scale.**
  - K:041 (2015) shows no "3.85" discs. They first appear in K:036/K:037 (2025), so they cannot have been the scale
    for K:041.
  - Independent scale: the soldier by the booth (~107 px, ~3 m in front of the wall) gives ~53 px/m at the wall.
    The notes' 49 px/m is within ±8 %.
  - Re-measured on K:041: the front-face jambs stay vertical for 160 px and the crown is 212 px above the road.
    That gives **jambs ~3.0-3.2 m (not 2.6 m), arch rise ~1.0-1.1 m, crown 4.0-4.3 m**.
  - The 2.6 m jambs would leave only ~3.7 m over a bus-width vehicle, less than the posted 3.85 m.
  - OSM w1545285986 gives a 4.3 m wide, 2.3 m deep passage, which supports the ~4.2 m width and a ~2.3 m wall
    thickness at the gate.
- **R8 Photo table.**
  - K:029 looks N/NNE along the west face (wall on the right, blue-tarp landing at the far end), not E.
  - K:030 was taken from right under the springer, looking steeply up. It was not taken from (627,-88).
  - The geotags of K:028-K:030 are rounded to whole arc-seconds (±15 m).
  - K:023's geotag at the wall contradicts its broadside view of the bridge.
- **R9** The Dung Gate faces 171°, which is S by E rather than SSE (157.5°). Label only.
- **R10** The Western Wall prayer face faces ~260° (OSM edge bearings 348° and 351°), not ~265°.
- **R11** There are 34 OSM tree nodes in x 707-770, y -176..-126 around Umayyad Palace Square, not 38.
- **R12** The bridge geometry leaves out an OSM vertex. From the stair tower (613.0,-42.2) the way runs 9 m due N to
  (613.6,-33.3) before turning NE. The length to the NE corner is ~50 m, not ~45 m, and the return to the gate is
  11 m S then 5 m E.
- **R13** The prayer-enclosure boundary w45081552 is not a straight line from (604,-32) to (627,18). Its vertices
  are (603.5,-32.0) → (620.0,-20.4) → (617.7,-7.3) → (613.9,15.7) → (627.3,18.0). Drawing it straight would cut
  through the women's section. Fixed in §0 and checklist item 3.
- **R14** The stair-tower height (~5.5 m) and the hoarding height (~3.5 m) contradict each other. In both K:021 and
  K:022 the hoarding reaches ~0.88 of the tower's eave height. Flagged in L3; neither figure is verified.
- **R15 Levels.** `data/terrain_street.json` (OS 1865 survey plus modern anchors) gives:
  - Mughrabi Gate sill **736.5 m ASL** (surveyed), prayer floor 727.0, plaza flat 729.0, Dung Gate ~724.1.
  - The sill figure confirms ≈ +9 vs P, so that row is upgraded to H. The gate at ≈ -4 also stands.
  - The "road climbs only ~3 %" claim conflicts with the model (~10-15 %) and with the table's own bus-loop row.
    Marked unverified.

### Checked and confirmed (no change)

- **OSM positions:**
  - Mechitza w45081551 (617.7,-7.3)→(651.8,-1.6), seen in K:003, K:016, K:017, K:019 (women S, men N match the
    views).
  - Western Wall west edge: 59.2 m long.
  - North end block: S edge (621.9,30.5)→(646.1,35.2), projecting 24 m from the wall.
  - Mughrabi Gate w291836692 and the bridge's direction (K:007, K:013, K:021, K:024).
  - Robinson's Arch n9351437161 is 19 m N of the SW corner (670.8,-108.0) and on the west face, consistent with
    K:024, K:044 and K:033.
  - Dung Gate, Tanners' Gate, Davidson Center, ticket office (W of the road), café (W of the road), kiosk (E side,
    K:037), walkway (E side, K:036).
  - The plaza area of 5564 m², 80 % of it in s09, is correct.
- **Identifications:**
  - "AISH HATORAH WORLD CENTER" lettering confirmed in the K:001 crop.
  - "COLEL CHABAD / FREE KITCHEN FOR THE NEEDY" and "SIMCHA HALL.com 02-627-5251" confirmed in K:027.
  - The MEN / WOMEN ENTRANCE portal faces S, with men on the W lane (K:045).
  - The name tile is on the inner face, E of the arch (K:037; the K:040/K:043 crops show the arch to the tile's
    right).
- **Heights:**
  - Western Wall ~17 m. A course-ratio check on K:003 gives 16-17.5 m; OSM's height=20 tag should not be used.
  - The north block is as high as the wall (K:016, K:002).
  - The prayer parapet is ~1.2 m with a ~0.5 m fence (K:015, scaled from a person).
  - The mechitza is ~2.0 m (K:003, scaled from a monobloc chair).
  - The south portal beam is ~3.5 m (K:045, scaled from a person).
  - The Dung Gate merlons are 2.3-2.5 × ~0.95 m with tops 10.5-11.4 m up (K:041).
- **Viewpoint corrections** for K:003, K:004, K:010 (resected: (535,5) heading ~87°, consistent), K:014 and K:045
  are plausible.

### Not verified (left as the author's claims)

- Ezrat Yisrael platform position: not in OSM and only K:031 shows it. Its view suggests y ≈ -95..-103 rather
  than -80.
- Aish HaTorah footprint (L). From K:001 the facade bearing is ~279°, which passes near the NW part of
  w1528632636 at about (527..535,-2). It may be part of that OSM building.
- Davidson Center exterior and its entrance side.
- Robinson's springer height (~8-10 m) and the SW corner height (~25 m) above the Herodian street.
- Stair-tower size (R14).
- Bab al-Silsila minaret height above the block.
- "12 tribes clock": it is a medallion of ~12 emblems with no hands visible.
- Name-tile size: ~0.7 × 0.55 m by course scaling, against 0.9 × 0.6 m stated.
- Bus-loop level (+1.5..+3 stated; survey and model suggest +3..+5).
- Road gradient from the Dung Gate (R15).
- Whether the palms and olive at the Dung Gate still exist in 2025 (R6).
- Wall course counts per zone. K:003 at this resolution supports 7 / ~4 / 12-16 but cannot confirm them exactly.
- K:021 is not consistent with the OSM stair-tower vertex under my rough resection. K:009 and K:024 agree with OSM,
  so OSM is kept.
