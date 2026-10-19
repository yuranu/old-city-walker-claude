# s04_sepulchre: Holy Sepulchre, Muristan, Christian Quarter Rd: visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (lat 31.7766282, lon 35.2275435).
Sector box (data/sectors.json): x 160..400, y 48..430. You get in from Jaffa Gate along David St (s05), then
north up Christian Quarter Rd (x ≈ 160-176) or into the Muristan (Suq Aftimos / Muristan St, x ≈ 200-269).
Photos: `data/photos_ref/s04_sepulchre/KNN_<pageid>.jpg`, cited below as **A01**, **D07** and so on. Titles,
authors, licences, dates and GPS are in `index.json` there. Camera positions come from EXIF GPS where the file
has it (listed as "cam (x,y)"). Directions come from EXIF compass, or from bearings fitted to OSM landmarks.
Scale comes from people (1.7 m), doors (2.2 m) and OSM edge lengths. Heights at the important points were solved
with a pinhole model: horizon taken from the heads of standing people, focal length from EXIF 35 mm-equivalent,
distance from OSM. The script is persp.py in the session scratchpad.
Confidence: **high** = seen clearly in 2+ photos, or OSM geometry plus one photo; **med** = one clear photo or a
consistent estimate; **low** = inferred or seen only at an angle.

> Status: complete (written incrementally). 45 photos downloaded for this note (index.json).
> Coverage: the Holy Sepulchre parvis, St Helena Rd, Christian Quarter Rd, the Muristan, Suq ed-Dabbagha and the
> Redeemer are photo-backed. The north-east part of the box (Aqabat el-Khanqa, Beit HaBad / Khan ez-Zeit,
> Suq al-Lahhamin north, Via Dolorosa VII-IX) is described from OSM only, except for the Hospice portal.
> Reviewed independently on 2026-10-19: 21 corrections or flags, listed in `## Review` at the end and tagged
> [Review Rn] in the text.

---------------------------------------------------------------------------------------------------------------

## 0. Key facts and likely model errors (summary)

1. **The Holy Sepulchre is entered only through its south parvis.** The parvis is a sunken courtyard with a clear
   width of **~17-17.5 m E-W** (12-14 m at the north end) and ~27 m N-S; x 204-226, y 157-184 is only its bounding
   box [Review R3]. The famous double portal is in its NORTH side (w1022672085 e55, y ≈ 183.5,
   facing south). The bell tower stands at its NW corner, west of the portal, and **projects ~11 m south of the
   facade line** along the parvis west side [Review R1]. The Chapel of the Franks, with its
   small lead dome, juts ~5 m into the parvis at the NE corner. **high** (A01-A05, A09, F01-F03, OSM)
2. **The Mosque of Omar minaret is just south of the parvis' SW corner**, at OSM node (206.9,145.8), on the
   south side of St Helena Rd. It has a **square stone shaft** (not cylindrical) with a corbelled gallery and a
   small domed lantern. Its top is ~23-25 m above the parvis. **high** for position (A06, A09, D07, F01, G04 +
   OSM node), **med** for height.
3. **The Redeemer's bell tower is at the SW corner of the church**, at the west front on Muristan St, south of the
   portal, around (268.5,136.3). It is **~47 m to the cross** above the Muristan pavement, the tallest thing in
   the sector, with a square stone spire. **high** for position (D04 and D07 bearings, E04, F01-F03 taken from its
   top), **med** for height (two independent solves: 47 m and 47 m).
4. **The golden dome that closes every southward view in the Muristan is St John the Baptist** (w166965387,
   (200,42)). It is just outside the box (y < 48) but must be modelled: a gold scale-clad dome with a gilt cross.
   A 2004 Commons caption calls it silver; the 2019-2026 photos show gold.
   **high** (D01, D02, D05, D06; in D05 the dome sits exactly behind the fountain, as OSM predicts)
5. **Christian Quarter Rd is a roofed souq** about 4-5 m wall to wall. Green steel arch ribs span the sky slot
   above timber-boarded shed canopies on large green hoop brackets. In 2014 the ribs are **open** (sky and upper
   walls visible between them, B05, B06); translucent sheeting is at most local (B03?, a blue section far off in
   B05) [Review R6]. Closed shops show **teal panelled steel doors**. **high** for the profile (B03, B05, B06),
   **low** for any sheeting.
6. **The Muristan fountain square is paved dark grey with pale concentric arcs.** The Aftimos fountain is an
   obelisk-like pedestal with four columns inside an iron railing (green in 2015-16, blue in 2022). The square
   is ringed by 2-storey blocks with **red-tile hipped roofs**. **high** (D07, D08, F01, OSM)
7. Terrain: CQR and the Mosque of Omar sit high. St Helena Rd steps down east to the parvis. The Muristan and
   Suq ed-Dabbagha are lower, but only **~2 m (fountain square) to ~4 m (Muristan St / Dabbagha by the Redeemer)
   below the parvis** per the OS 1865 survey in `data/terrain_street.json`, not 7-9 m [Review R7]. **med**
   (see section 5)

---------------------------------------------------------------------------------------------------------------

## G. OSM geometry of the core (from data/osm_local.json)

| feature | OSM | position (local m) | notes |
|---|---|---|---|
| Church of the Holy Sepulchre | w1022672085 | bounds x 160.7-265.7, y 151.3-229.0; 5778 m² | polygon includes the monastic ranges up to CQR; its west edge overlaps the CQR centreline at y 150-205 |
| Parvis (courtyard) | way 612045223 (pedestrian area "ساحة") | x 204-226, y 157-184 | paving_stones, lit |
| Main entrance node | n2390928720 | (208.2,183.4) | west end of the south facade |
| South (portal) facade | w1022672085 e52-e55 | (204.1,183.1)->(218.4,184.3), faces 176° | double portal, ~14 m between the bell tower and the Franks projection |
| Chapel of the Franks projection | w1022672085 e57/e58; part w1022663509 | (218.7,179.1)->(224.2,179.5), faces S | external stair way 1547245013 (215.2,181.5)->(218.6,181.9); stations X/XI nodes at (223.6,185.1), (230,187) |
| Parvis west side (Greek chapels) | w1022672085 e43-e51 | x 204-209, y 158-183, faces E | chapels St James (207.1,161.4), Mary Magdalene (206.2,169.9), Forty Martyrs (205.4,179.1) |
| Parvis east side | w1022672085 e0 | (224.2,179.5)->(225.6,164.0), faces W | Ethiopian / St Michael chapels, Monastery of Abraham above |
| Bell tower | way 1022663529 (building:part, height 30, pyramidal roof 4 m) | x 193.1-204.9, y 172.6-184.0 | NW corner of the parvis; its NORTH side is on the portal-facade line (y ≈ 183-184) and the tower projects ~11 m south of it; its east face (x ≈ 204-205, y 172.6-184) is the parvis NW corner [Review R1] |
| Rotunda (Anastasis) dome | way 1022663528 (height 34, min_height 20, roof 10, dome) | centre (188,203), ~21 m across | Edicule (Kouvouklion) way 529720482 at (187,204) |
| Katholikon dome | way 1022663527 (height 34, min_height 24, roof 5, dome) | centre (211,208), ~12 m across | Omphalos node at (206.2,207.4) |
| Main roofs | parts 1022663520 (h 20), 1022663526 (h 24), 1022663525 (h 23), 1022663502 (small dome, h 22) | | |
| St Helena chapel dome (Ethiopian roof) | way 1022663497 (dome) | (254,208) | Deir es-Sultan (layer 1) way 744697161 at x 267-277, y 199-216 |
| Arch of the Virgin Mary (blocked Crusader west portal) | n7056393666 | (167.8,221.9) | on Christian Quarter St; the node is ~7 m east of the street centreline (x ≈ 160.6 at y 222), inside the HS footprint; model the arch in the street's east wall at y ≈ 222, facing W [Review R11] |
| Mosque of Omar | w290821793 | x 184.7-214.6, y 128.7-147.7 | minaret node n12893656140 at (206.9,145.8); street gate node n6779484570 (195.6,150.6) |
| Lutheran Church of the Redeemer | w29268902 | x 265.0-306.3, y 128.0-152.2 | tower viewpoint node n9840842282 at (270.9,136.8) (fee, Mo-Sa 10-17); the west front e16+e17 is only 13.4 m wide (y 133.5-146.9) |
| Redeemer bell tower (added in review) | w375040918 (building:part, man_made tower, bell_tower) | x 265.1-272.5, y 133.7-139.4 | the southern 5.7 m of the west front, i.e. its SW corner; directly confirms the tower position [Review R21] |
| Propstei | r3864634 (4 levels) | x 265.6-311.0, y 94.3-131.2 | Muristan St east side, south of the Redeemer; Johanniterkapelle node (295.7,101.2), level 1 |
| Alexander Nevsky Church (entrance block) | w612045244 | x 300.4-310.1, y 158.5-173.2 | Alexander Compound landuse way 612045222 covers x 226-320, y 156-207 |
| Alexander compound main block | w1022672084 | x 225.6-292.5, y 156.1-174.0 | north side of Suq ed-Dabbagha |
| Muristan market | way 620317519 | x 198-268, y 56-120 | fountain node n3757325200 (226.7,91.5); round square way 620317524 x 217-233, y 82-105 |
| Hospice of the Order of St John (Johanniter-Hospiz) | w53474876 | x 282.4-303.7, y 272.3-285.7 | Aqabat el-Khanqa, by Station VIII (299,287) |
| Church of St John the Baptist (outside box) | w166965387 | (200,42) | golden dome, see A4 |

Streets (OSM centrelines):
- Christian Quarter St way 26492706: (176,9) → (173,54) → (170,99) → (168,133) → (167,148) → (165,181) → (160,221) → (159,261).
- Muristan St way 26492713: (269,16) → (267,58) → (265,98) → (264,119) → (264,153).
- Suq Aftimos: ways 26492715 (fountain → NE diagonal to Dabbagha at (258,155)), 26492717 (SE diagonal), 26492716,
  26492718, plus unnamed 126868372-76 and 620317525 (the Muristan grid).
- Suq ed-Dabbagha way 256298883: (225,156) → (258,155) → (264,153) → (300,154) → (312,154) → (312,171) → (321,171).
- Saint Helena Rd: steps 26492712 (167,148)→(194,150), going DOWN eastwards (incline up = westwards). A 3 m jog north
  at x ≈ 194 (steps 168888828 + footway 722734610) has a gate n1783564002 at (193.6,153.7). Then steps 166967365
  (194,154)→(206,155) go down eastwards (handrail, lit), then the level way 612045234 runs to (225,156).
- Parvis entry steps way 616344391: 4 steps (with ramp) from St Helena Rd (y 155) down north into the parvis (y 157).
- Gate n2390928717 (224.5,156.4): parvis SE corner, the passage to Suq ed-Dabbagha.

OSM wall-to-wall widths (perpendicular rays from the centreline to the nearest footprint, every 5-8 m. The
Holy Sepulchre polygon overlaps Christian Quarter St between y 150 and 205, so widths there come from photos):
- Christian Quarter St: 4.0-5.5 m for most of its length (y 20-140: 4.4, 4.6, 4.9, 5.1, 4.7, 4.0, 4.1).
  3.0 m at y 208-214 (next to the HS west range), 5.4-5.6 m at y 243-256. Wider pockets at y 94-106
  (7.8-13.8 m, side lanes into the Muristan).
- Muristan St: 2.8-5.7 m beside the Redeemer (y 135-141; conflicts with E05, which shows ~6-7 m, see Review R13)
  and 6.4-6.5 m beside the Propstei (y 105-111).
  An 18 m forecourt at y ≈ 122-133, between the Propstei and the Redeemer.
- Suq ed-Dabbagha: 1.9-5.0 m at its west end (x 229-249, the parvis approach). ~9.4 m between the Redeemer and
  the Alexander compound (x 268-289): the Redeemer wall is 6.5 m from the centreline behind a fenced strip.
  6.3 m at x 309.
- St Helena Rd: 5.4-5.6 m at the Christian Quarter St end (x 169-174), 8.2-8.3 m at x 184-189.
- Suq Aftimos: 6.4-7.1 m (NE diagonal), 10.3-10.4 m (SE diagonal), 3.2-5.3 m (east-west lane at y 118), 6.0 m
  (west lane at x 198).
- Aqabat el-Khanqa: 3.0-4.4 m, with a 1.5-1.6 m pinch at x 271-280 (probably a sabat or an OSM overlap; unchecked).
- Beit HaBad / Khan ez-Zeit spine (x ≈ 318-321): 3.4-4.3 m, 6.5 m at y 244. North of y ≈ 300 the centreline
  runs under mapped buildings (w1393408273), so the street is vaulted there.

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and STREET PROFILES

### 1.0 Character
A dense Christian-Quarter souq, made of narrow roofed market streets lined with closed teal steel doors, around three
very different open spaces:
(a) the **sunken stone parvis** of the Holy Sepulchre, enclosed by medieval walls, with the Romanesque portal,
the bell tower, the minaret of Omar behind its south wall, and a cypress and palm on a terrace;
(b) the **Muristan**, a 1900s Greek-Orthodox market grid of 2-storey arcaded blocks with red-tile hipped roofs,
round-arched shopfronts with fanlights, big beige fabric awnings, and a circular dark-paved fountain square;
(c) the **Lutheran precinct** on Muristan St: clean pale 1890s Romanesque-revival ashlar, the 47 m Redeemer tower,
square stone bollards and trees.
The skyline is set by the two grey HS domes, the Redeemer spire, the Omar minaret and the golden dome of St John
the Baptist. Stone is cream to honey limestone. The HS and the minaret are heavily weathered, the Lutheran and
Russian buildings are clean, and pink mizzi stone is used for trims (Aftimos piers, Alexanderhof bands).

### 1.1 Profile table (which OSM street gets which profile)

| profile | OSM streets (name:en) | key look |
|---|---|---|
| P1 roofed main souq | Christian Quarter Street (y 48-150); probably also Suq Al La'h'hamin north of y 48 (layer -1, retail landuse, unseen) | 4-5 m, teal doors, timber shed canopies on hoop brackets, open green arch ribs over the sky slot (translucent sheeting only locally, unverified [Review R6]) |
| P1b vaulted souq / passage | Christian Quarter Street north of St Helena Rd (y 150-230, under the HS ranges, Arch of Mary); Beit HaBad / Suq Khan al-Zeit where they run under buildings (y > 300) | the same shops, but under stone vaults or deep sabats, with less sky |
| P2 stepped lane | Saint Helena Road (both step runs); Aqabat El-Khanqa, Via Dolorosa steps, Ethiopian Monastery steps, Al-Battikh Ascent, HaTut, Al-Karmi Court (OSM-only) | broad low steps of worn polished stone, raised shop platforms at both sides |
| P3 enclosed plaza | Courtyard (HS parvis, way 612045223) | sunken, walled, big polished slabs, steps along the south side |
| P4 market square | Muristan fountain square (way 620317524; unnamed pedestrian ways around the fountain) | dark-grey disc with pale arcs, central fountain, café tables, 2-storey red-roof blocks |
| P5 open market lane | Suq Aftimos (all four ways), Suq Ed-Dabbagha (x 225-312), the unnamed Muristan lanes 126868372-76, 620317525 | 6-10 m, beige retractable awnings or green steel canopies, pale smooth slabs |
| P6 institutional street | Muristan Street (y 95-153) | clean Lutheran ashlar on the east, shops on the west, square stone bollards, trees, raised sidewalk |

### 1.2 P1: Christian Quarter Rd (roofed souq)
Photos: B03 (2015, cam (171.6,44.9), looking ~200°), B05 (2014, all shops closed, house plate "109"), B06 (2014),
B01 (2017, near the HS), B02 (2016, cam ≈ (166,110)), C06 (St Helena Rd steps off CQR).
- **Width**: wall to wall 4.0-5.0 m (OSM, B03, B05). The clear walking width between goods and stalls is
  2.5-3.0 m. **high**
- **Plan**: almost straight N-S, with a gentle bend at y ≈ 180-220 where it passes the HS west ranges. **high** (OSM)
- **Paving**: two types.
  (1) Most of the length: rectangular limestone slabs ~0.3-0.4 x 0.6-0.8 m in courses across the street,
  heavily rough-picked (speckled grey-white), with round cast-iron manhole covers (~0.7 m, concentric rings) on
  the centre line every ~8-12 m and small square drain grates near the walls. **high** (B03, B05, B01)
  (2) At y ≈ 105-125: **very large old slabs (0.8-1.3 m, irregular rectangles), glossy and worn into dips**,
  pinkish cream, set in dark grey mortar and asphalt patches ("roman pavement"). **high** (B02, B06)
- **Steps**: none in the photographed parts. The street climbs gently northwards to the St Helena junction
  (see section 5). **med**
- **Closed shop fronts (target state)**: dukkan openings ~2.0-3.0 m wide x ~2.8-3.2 m tall between rough stone
  piers 0.4-0.8 m. The doors are **teal / blue-green painted steel, 2-4 leaves**, each leaf in 3-4 tall panels
  framed by flat bars, with **two horizontal hasp bars with padlocks** at ~1.0 and ~1.9 m. Paint is chipped at
  the bottom. Some openings have teal roll-down shutters with a box at the top, or **olive-green** and **royal
  blue** steel doors (C06). **high** (B05, B03, C06)
  Some old openings keep **tall round-arched heads with green-painted wooden boarded leaves** (two narrow arched
  doors side by side, B01 left). **med**
- **Canopies**: every frontage has a shed canopy at ~2.9-3.2 m (front edge), projecting ~1.2-1.5 m, made of
  **timber boards on dark green steel channels**. The canopy is carried by **large green steel hoop brackets
  (full circles ~1.0-1.2 m in diameter with S-hooks)** fixed to the wall. Fluorescent tubes hang under the front
  edge. **high** (B03, B05)
- **Roof**: above the slot between the canopies runs a row of **green steel arch ribs**. Each rib is a double
  semicircular ring with **radial "sunburst" bars** and knob finials, crowning at ~6-7 m (spacing ~1.5-2 m,
  unverified). **Correction [Review R6]:** in B05 and B06 (2014, y ≈ 110 and house no. 109) the ribs are OPEN: sky,
  the upper house walls and a tree show between them. Only B03 (2015, y ≈ 45, overexposed) may show white
  sheeting, and B05 has a short blue translucent section far down the street. **high** for the ribs (B03, B05,
  B06), **low** for any sheeting. B01 shows a high white-arched roof near the HS (P1b).
- **Lighting**: fluorescent tubes under the canopies, warm bulbs in the shops. At night the street is lit only
  from the canopies. **med** (B05, B01)
- **Signs**: blade signs and light boxes high up ("MONEY CHANGE" orange box, "HOLY SEPULCHRE ..." shop
  light box). **Strings of small flags** cross the street (white flags with a red Jerusalem cross, Armenian
  tricolour, Vatican yellow-white). House-number plates are white squares with black numerals ("86", "109",
  "43") at ~3 m. **high** (B01, B03, B05)
- **Clutter (closed)**: grey steel AC cabinets, framed pictures and boards leaning on shutters, blue plastic crates,
  baskets. The red **Goldoni mini tractor** with a yellow Israeli plate uses the street (B01). **med**
- **Cables**: a few black and blue cables along the walls under the canopies, hidden by the roof. **med**

### 1.3 P1b: Christian Quarter Rd beside the Holy Sepulchre (y ≈ 150-230)
- Narrower (3.0 m at y 208-214, OSM). It runs partly under heavy stone arches and vaults (OSM also has the
  centreline under building w1393169897 at y 231-237). At y ≈ 222 the **Arch of
  the Virgin Mary** survives: a blocked Crusader arch (round or slightly pointed: the apex is hidden by a later
  pier in B04, **unverified**) with **cushion (pulvinated) voussoirs**, an inner
  moulded arch on columns (one pink marble with a Corinthian capital), standing in a vaulted bay of the street.
  In front of it is a grey tube railing (~1.1 m) with a black heritage plaque with a teal band ("קשת מרים /
  قوس مريم / Arch of the Virgin Mary"). **high** for the object (B04), **med** for position (OSM node 7056393666
  at (167.8,221.9) plus B04 only; the node sits ~7 m east of the CQR centreline inside the HS footprint, while B04
  shows the arch facing the street pavement with only a ~1 m railed strip in front: put it in the east wall of
  CQR at y ≈ 222, facing W [Review R11])
- Shops continue (teal/grey steel doors, a yellow gas pipe, cables slung under the vault). **med** (B04, B01)

### 1.4 P2: St Helena Rd (stepped lane) and the parvis approach
Photos: C06 (2011, Sunday, all closed), C04 (2015), C05 (2014), A07 (2019), C02 (2023), A06/A09 (from the parvis).
- **Sequence** (OSM + photos): from CQR at (167,148), an **upper step run** of 27 m goes down east
  (shops on both sides; w290821801 on the south, the HS polygon on the north). At x ≈ 194 there is a 3 m jog
  north through an **arched gate with heavy timber doors** (n1783564002). A **lower step run** of 12.5 m with a
  handrail runs along the foot of the Mosque of Omar terrace wall. A level stretch follows, then **4 steps with a
  ramp** down into the parvis SW corner. **high** for the sequence, **med** for which photo shows which part.
- **Steps**: broad full-width steps with low risers **~0.12-0.18 m** and long treads **~1.0-1.6 m**, made of large
  dark-polished limestone blocks. Between the steps the paving is small squared setts (0.2-0.35 m), glossy and
  worn. **high** (C06)
- **Raised shop platforms**: at both sides **stone platforms ~0.35-0.45 m high and ~0.8-1.0 m deep** with smooth
  slab tops run in front of the shop doors, so the walking strip is ~3.0-3.5 m. Closed doors are olive-green and
  blue steel. **high** (C06)
- **Gate arch (n1783564002, ≈ (193.6,153.7))**: a round arch ~3 m wide in rough ashlar. Above it a **white marble
  plaque with a pink-red moulded frame, "HOLY SEPULCHRE"** (black sans capitals, ~1.3 x 0.3 m). To the right a
  **ceramic street sign** (white tiles, yellow-green border: "רחוב סנט הלנה / طريق القديسة هيلانة /
  ST. HELENA RD."), and below it a **black municipal heritage plaque with a teal band** and a white line drawing
  of the church ("כנסיית הקבר / كنيسة القيامة / Church of the Holy Sepulchre"). House number "243 / 127" is
  painted black on the arch. An **orange-and-brown striped retractable awning** with a scalloped valance hangs
  above, and a grapevine trails over the wall. **high** for the objects (C05, A07), **med** for the position.
- **Mosque frontage on the south side**: a stone retaining wall ~1.5-2 m high topped by a **green-painted steel
  fence with razor wire** and pink geranium boxes, with the minaret rising behind (C02). **high**
- **Overhead**: steel slats or pergola bars across the street at ~4-5 m and a hanging round lamp on a wire
  (C04). Black cables. **med**
- **Shop signs**: yellow board "PAPA ANDREA" (rooftop restaurant; OSM node Papa Andrea gift at (187.4,145.2) and
  Papa George (177.8,145.3) on this street). Green-white striped awnings. **high** (C04)

### 1.5 P3: Holy Sepulchre parvis (enclosed plaza)
Photos: A01-A06, A09, A10, F01-F03 (from above).
- **Size and level**: ~27 m N-S; clear E-W width **17.2-17.5 m** for y 160-171 and y 177-178 (from the west
  chapels at x ≈ 208 to the east side at x ≈ 225), ~20 m at y 172-176 (the tower's east face at x ≈ 205), and
  only **12-14 m** at y 179-184 between the bell-tower projection and the Chapel of the Franks; 447 m² (OSM way
  612045223). The earlier "~22 m" was the bounding box [Review R3]. It is sunken about 4 steps (~0.6-0.7 m)
  below St Helena Rd at the SW entrance and enclosed on all sides by 5-20 m walls. **high**
- **Paving**: large irregular rectangular limestone slabs 0.6-1.2 m, grey-cream to honey with **scattered
  pink/reddish slabs**, polished by feet and dark at the joints. No pattern or bands. **high** (A04, A06, A09)
- **Column stumps**: two or three **broken column bases/drums (~0.6 m diameter, 0.3-0.8 m high)** stand in the
  southern half of the parvis, remains of the medieval colonnade. **med** (A04 foreground; Commons captions
  "old column on Holy Sepulchre parvis")
- **South side**: a long wall ~4.5 m high of coursed ashlar with 2-3 small round-arched grilled windows and
  black rectangular floodlights on brackets. **3-4 broad steps run along its whole foot**, which people use as
  seating. They are the drop from the St Helena-level strip (OSM way 612045234, y 155-156) into the parvis, i.e.
  the same feature as OSM steps 616344391 (4 steps, ramp=yes). The **grey steel ramp** lies over the steps at
  x ≈ 211, in the **west-centre** of the south side, not the SE third. The doorway marked
  "ΜΕΤΟΧΙΟΝ ΓΕΘΣΗΜΑΝΗ" (Metochion of Gethsemane, OSM POI (213.4,154.6)) is just east of the ramp, near the middle,
  where the low terrace wall (west part, x ≈ 206-215) meets a taller 2-storey building with arched windows (east
  part, x ≈ 215-226) [Review R4]. On top of the west part of the wall
  is a **terrace with a white tubular railing**, a **tall cypress (~15-17 m above the terrace; its top level with
  the minaret gallery, ~19-21 m above the parvis)**, a **date palm (~7-8 m)** and a
  broadleaf tree (OSM trees (218.4,147.4), (218.3,142.5), (215.4,136.7); positions ±5 m, see Review R18), and
  small white domed kiosks. **high** for the objects (A06, A09, A10, F03), **med** for the ramp and door positions.
- **West side**: the Greek chapels (St James, St John/Mary Magdalene, Forty Martyrs). A plain ashlar wall with
  **one big blind round arch**, small arched grilled windows, and at the junction with the bell tower a
  **projecting block of very dark, weathered, rock-faced stones with a sloping cap** (~4 x 4 m in plan, ~7 m
  high). Black floodlights. **high** (A05, A09, A10)
- **East side**: plain ashlar 2-3 storeys (the St Michael / Ethiopian chapels, with the Monastery of Abraham
  above). A **triple round-arched window with grilles** sits at ~7 m and a **pointed doorway** at the parvis
  level near the NE corner. An **olive tree** grows on the upper terrace and a stone stair parapet climbs
  diagonally. **high** (A01, A03)
- **Entrances**: SW, from St Helena Rd (4 steps + ramp, arched passage). SE, from Suq ed-Dabbagha through a
  segmental-arched passage with a **black steel sign "HOLY SEPULCHRE"** (white stencil capitals, ~1.3 x 0.6 m),
  a blue arrow sign and bundles of black/yellow cables (A08). **high** (A07, A08, OSM gate n2390928717)
- **Lighting**: black wall floodlights on all four sides at ~4-6 m (A09 shows them lit warm at dusk). **high**

### 1.6 P4: Muristan fountain square (market square)
Photos: D07 (2016-10, cam (225.9,81.3), looking N), D08 (2022), D01/D02 (2025, cam (220.7,91.8)), F01 (from above).
- **Size**: the square is ~16 m (E-W) x ~23 m (N-S) (OSM sett area 620317524, x 217-233, y 82-105). Review: that
  area is roughly rectangular with a chamfered SW corner; the round element is the 9.4 m footway ring 620317521
  around the fountain. The lanes open off it. **high**
- **Paving**: a **disc of dark grey stone** (basalt-like) ~14-16 m across, laid with **pale limestone bands
  forming concentric arcs and radial strips**. Outside the disc, pale cream slabs, plus a **curving dark band**
  that continues into the SW lane (D03, D04). Round cast-iron covers. **high** (D07, D08, D03, D04, F01)
- **Fountain** (Aftimos fountain, node (226.7,91.5)): **high** (D07, D08)
  - a square stepped base on a low octagonal kerb. The central **square stone pedestal** (~1.4 m square, ~3 m)
    has a **lion-head spout** and carries a stone bowl and an urn finial at **~5.5 m** (solved height 5.5 m
    above the paving from D07). Review: scaling by the 1.75 m man standing beside the fountain in D07 gives
    ~4.5-5 m. Use 4.5-5.5 m (**med**); D07's vertical geometry is unreliable (R7).
  - **four tall columns** (~4.5 m) on square pedestals at the corners, with capitals and urn/finial tops.
  - an **iron railing ~1.2 m** of vertical bars with scroll tops around the basin: **green in 2015-16 (D07),
    blue in 2022 (D08)**. The 2022 state is the current one.
  - festoon string lights radiating from the fountain top to the surrounding roofs (D08).
- **Edges** (corrected in review, see R5): north (w620317526, south face e0 (218.7,104.8)->(228.0,105.0) plus its
  SW face e3) the 2-storey block seen directly behind the fountain in D07/D08: a **red-tile hipped roof** (OSM has
  no roof tags for it), an upper balcony with black railings, ground-floor cafés with blue/teal awnings. East, at
  the mouth of the east lane (footway 26492718, y ≈ 98, between w620317534 and w620317532, x ≈ 234.5): a
  **two-bay round-arched arcade on pink-stone piers** with pilasters, a gateway into the lane, with the Redeemer
  tower rising beyond it. East, south of the arcade (w620317532 e12, faces W) the single-storey
  "YASSER T. BARAKAT" shop block: round-arched openings with **radial fanlights**, pale grey steel doors, a white
  sign fascia, a quarter-round translucent awning. West (w620317527 e3) a 2-storey block with a red-tile hipped
  roof (OSM tags); its square face is outside the D07 frame, and only its north end shows at the left edge with
  blue awnings. **high** (D07 bearings, D08)
- **Furniture**: café tables (rattan bistro chairs, blue Pepsi umbrellas, white parasols), a green ka'ak bread
  cart, wooden slat benches on black cast-iron legs, a black iron fence round a small garden, a grey bin.
  **high** (D01, D07, D08)

### 1.7 P5: Suq Aftimos lanes and Suq ed-Dabbagha (open market lanes)
Photos: D03, D04 (2025), D05 (2026, cam (259.3,155.2), looking ~207° down the lane axis; the EXIF compass value
of 222.5° magnetic is ~15° off [Review R12]), D06 (2019), D09 (2016), G04 (2016, Dabbagha
looking W), G05 (2017).
- **Width**: Aftimos NE diagonal ~6.5-7 m, SE diagonal ~10 m, Dabbagha ~9 m by the Redeemer and 2-5 m at the
  parvis end (OSM). **high**
- **Paving**: smooth pale limestone slabs in courses (Muristan), with a raised **kerb/threshold 0.12-0.18 m**
  in front of the shops. Large steel trench grates across the lane at the Aftimos north gate (D06). Dabbagha has
  rectangular slabs in courses with occasional pink ones (G04). **high**
- **Shop fronts (Aftimos, 1900s)**: tall **round-arched openings with fanlights** (radial muntin fans, painted
  teal or green), **teal/turquoise boarded doors or green steel doors with padlock hasps**, and grey roll-down
  shutters on the bigger shops. The piers are ashlar, some in **pink stone with moulded bases and capitals**.
  **high** (D03, D04, D06)
- **Canopies**: three kinds. (1) **Big beige retractable fabric awnings** on folding arms at ~3.5-4 m projecting
  2-3 m from both sides, nearly closing the sky (D05, current 2026). (2) **Quarter-round (barrel) awnings of
  translucent grey/white corrugated sheet** on steel frames (D04, D06, D09). (3) **Deep dark-red/maroon steel
  canopies on iron hoop brackets** wrapping a corner shop (D03), plus cream scalloped fabric awnings and green-white
  striped awnings. **high**
- **Dabbagha**: the south side is the Redeemer's north wall, behind a **low wall with stone piers and an iron
  railing** enclosing a ~3.5 m strip, with the deep medieval north portal of the Redeemer. The north side has shops
  under **green steel canopies on hoop brackets with beige canvas**, and teal shopfronts. The street is framed at
  its west end by the **Omar minaret and cypress** rising over the parvis gate. **high** (G04)
- **Clutter**: suitcases and leather goods, rattan café chairs, Coca-Cola fridges, green "artificial grass"
  counter fronts, a blue ATM kiosk ("משיכת מזומנים"), a **blue steel hand cart on bicycle wheels** and blue
  crowd barriers (G05), a red tractor-trailer (G04). **high**

### 1.8 P6: Muristan Street (institutional street)
Photos: E05 (2015, looking S from the Redeemer), E01, E04, D04 (distance).
- **Width** 6-7 m. A **raised sidewalk (kerb ~0.15 m, ~2.5 m wide)** runs along the Redeemer/Propstei side (east)
  in large old flags. The carriageway is in small rectangular setts/slabs (~0.2 x 0.4 m), "cobblestone" in OSM.
  **high** for the surface (E05). The width is **high** beside the Propstei (OSM 6.4-6.5 m) but **unverified**
  beside the Redeemer: OSM gives only 3.0-5.7 m there (w290821789 is 2-5 m from the west front), while E05 looks
  like ~6-7 m. E05's camera position is unknown (its coordinates are a place geocode) [Review R13].
- **Three square limestone bollards (~0.4 x 0.4 x 0.9 m, pyramidal caps)** stand across the street at the north
  end by the Redeemer. **high** (E05)
- The east side is clean pale ashlar walls with buttresses (Redeemer, Propstei) and a **row of tall pines and
  cypresses** beyond (Martin Luther School garden; OSM trees at (272-294, 66-120)). The west side has shops with
  canopies, café tables and folded white parasols. **high** (E05)

### 1.9 P2/P1b in the north-east part (OSM only, low)
- **Aqabat el-Khanqa** (y ≈ 261-286): a lane 3-4.4 m wide climbing west from Khan ez-Zeit to CQR, with shops
  (barber, bakeries, supermarket nodes) and the Johanniter Hospice. Use the P2 profile without the big steps
  (no steps way is mapped). **low**
- **Beit HaBad / Khan ez-Zeit spine** (x ≈ 318-321): 3.4-4.3 m souq. North of y 300 it runs under buildings,
  i.e. vaulted. **Via Dolorosa steps** (ways 616344389/90, 25 + 27 steps, sett) climb east→west from (404,310)
  to (317,292). The **Ethiopian Monastery steps** (way 617363483, 22 steps with ramp) start on Aqabat el-Khanqa at (266,280)
  and climb NW to (256,311). The way is drawn (266,280)→(256,311) with incline=up; the original note had the
  direction reversed [Review R15]. **low**
- **Suq al-Lahhamin north of y 48** (layer -1, inside retail landuse 1544948792): the continuation of the
  covered triple souq. Treat as P1b (vaulted). **low**

---------------------------------------------------------------------------------------------------------------

## 2. LANDMARKS

### 2.1 Church of the Holy Sepulchre (w1022672085)

**Massing** (OSM parts + F01-F03 from the Redeemer tower):
- An irregular cluster ~105 x 78 m. Main roofs are flat terraces at **~20 m** (part 1022663520) and ~23-24 m
  (Katholikon nave). Lower monastic ranges at 10-15 m fill out to CQR and St Helena Rd. **med**
- **Rotunda (Anastasis) dome**: centre (188,203), ~21 m across, lead/blue-grey with **dense radial standing-seam
  ribs**, a small oculus ring and a gilt finial on top, sitting on a short drum. Top at ~34 m (OSM). The bigger of
  the two domes. **high** for form and position (F01 crop, F02, F03; bearings from the Redeemer tower match OSM:
  Rotunda 309° observed vs 308° OSM), **med** for height.
- **Katholikon dome**: centre (211,208), ~12 m across, grey hemisphere on a **tall cylindrical drum with
  ~8-10 round-arched windows**, crowned by a **gilt Orthodox double-barred cross**. Drum ~24-29 m, dome top
  ~34 m (OSM). **high** (F02, F03, A02 shows the gilt cross above the facade), **med** for heights.
- **Roof clutter**: black steel railings round the flat roof terraces. A **large white membrane tent roof on a
  steel frame with blue tarps** covers the Calvary/Chapel of the Franks roof zone (2015 and 2021, F01, F02, F03).
  In 2025 there is a **steel scaffold canopy ("Layher")** in the same place (A01, A03). It is long-lived but
  temporary: model it or leave it out deliberately. **high**

**South (portal) facade, e52-e55, faces 176°** (A01-A05; A01/A03 cam (223.9,160.5)/(215.2,157.5) 2025):
- Width ~14 m between the bell tower's east face (x ≈ 204.5) and the Franks projection (x ≈ 218.6). Two equal
  bays. **high**
- **Lower storey**: two **pointed portals** with deep stepped archivolts. The outer roll has radial grooved
  voussoirs, the inner orders rest on clusters of **3 marble columns each side** with carved capitals.
  Each opening is rectangular below a blank stone tympanum. The **west (left) doorway is the working entrance**
  (n2390928720), with tall dark timber double doors. The **east one is walled up**. Apex of the portal arches
  **~8-9 m**. Door opening ~2.6 x 4.5 m. **high** for form (A04, A05, A03), **med** for dimensions.
- **Carved string course / frieze** at ~9-10 m across both bays. **high**
- **Upper storey**: two **pointed-arch windows**, glazed with a dark iron grid of small square panes (~1.2 m wide,
  ~3 m tall), framed by 3 orders: moulded archivolts with a carved outer hood (foliage and billets) and flanking
  colonnettes with acanthus capitals. A projecting ledge at the sill has a thin black railing, and the
  **famous wooden ladder** leans under the RIGHT (east) window. **high** (A02, A01, A03)
- **Top cornice** richly carved (acanthus/egg-and-dart) at **~18-19 m**. Above it a **steel railing ~1.2 m**
  round the roof terrace, i.e. a flat skyline at ~20 m. It is dark grey/black in 2025 (A01-A03) but white/silver
  in 2019 (A04, in sun); match the target year [Review R10]. Behind, the gilt cross on top of the Katholikon dome is
  just visible over the centre. **high** for form, **med** for height (A04 scaled from the 14 m width; OSM
  part height 20).
- Material: warm honey-ochre limestone, strongly weathered, darker in the lower half. The marble columns are grey,
  white and pinkish. **high**

**Bell tower** (way 1022663529, x 193-205, y 172.6-184; the NW corner of the parvis): A04, A05, F01 crop, F02, F03.
- A square tower ~11 x 11 m. **Correction [Review R1]:** its NORTH side is on the portal-facade line
  (y ≈ 183-184); the tower stands ~11 m forward (south) of the facade, so its east face (x ≈ 204-205,
  y 172.6-184, with the oculus) closes the NW corner of the parvis and meets the facade at the west portal. It
  rises **~2 storeys above the facade roof line**. **high** (OSM way 1022663529; A04/A05 show the east face down
  to the parvis-level blocks left of the west portal; F03)
- Stages: (1) the lower part merges with the Greek chapels. (2) A stage with a **large round-arched blind arch**,
  a small round-arched window and a **round oculus**. (3) Stage 3 has **paired round-arched windows with a
  central column** on each face. (4) The belfry has **two round-arched openings with bells visible behind low
  iron grilles** on the SOUTH face (the face with the big blind arch below it, A04/A05; the original "east face"
  is corrected, see Review R2). (5) A short top stage with small square grilled windows. **high** (A05, F03)
  for the stages, **med** for which face shows the bells.
- **Roof: a low hipped/pyramidal roof of red tiles with dark red-brown eaves projecting ~0.5 m**, plus a
  flagpole with a **white flag with a red Jerusalem cross** (2019). **high** (A04, A05, F01 crop 2015)
- Height: eaves ~23-24 m, roof apex ~26 m above the parvis (A04 scaled). OSM gives 30 m. **med-low**
- Stone: the lower part is weathered honey colour, the upper stages paler and cleaner (restored). **high**

**Chapel of the Franks** (e57/e58, NE corner of the parvis): a projecting block at the east end of the facade.
At parvis level there is a **twin pointed opening with a central column and a large iron grille** (Chapel of
St Mary of Egypt). Above, at the Calvary level (~5 m), is a pointed arched window, and on top a **small lead dome
on a short drum** (~3.5 m across, top ~13 m) with a cornice. An external stair rises against the facade to the
chapel door (OSM steps 1547245013). **high** for the dome and openings (A01, A03), **low** for the stair (hidden
by scaffold pipes in 2025).

**West side on Christian Quarter St** (e24-e31): mostly the monastic ranges and shops. The visible medieval piece
is the Arch of the Virgin Mary at (167.8,221.9) (see 1.3). **high**

**North side of St Helena Rd** (e32-e40, faces S): plain monastic walls above shopfronts. The gate arch with the
"HOLY SEPULCHRE" plaque is at x ≈ 194. **med**

### 2.2 Mosque of Omar (w290821793) and its minaret
Photos: C01, C02 (2023), C03 (2019), C04 (2015), A06, A09, A10 (from the parvis), F01 crop, F03, D07, G04.
- **Footprint**: x 185-215, y 129-148. The north faces are e0 (190.9,140.5)->(206.9,141.8) onto a small
  **forecourt** and e4 (204.8,147.1)->(214.3,147.7) directly onto the lower St Helena Rd run. **high** (OSM)
- **Street gate** (node n6779484570 (195.6,150.6), on the south side of St Helena Rd at the foot of the upper
  steps): a white-limestone **neo-classical portal**, ~4.5 m wide and ~9 m to the pediment apex. It has a
  **triangular pediment with an oculus**, an entablature with a **carved rosette**, and a round arch with a
  **scalloped/zigzag archivolt**. A **large carved rosette** fills the tympanum. A marble plaque reads "مسجد عمر
  بن الخطاب / Mosque of Omar / for prayers only" with crescents, and a black iron grille gate sits below.
  **high** for the object (C04), **med** for the position (C04's own GPS/compass are unreliable. The position is
  from the OSM gate node plus the Papa Andrea sign beside it).
  **Orientation [Review R8]:** the gate probably faces **W/WNW, up the upper St Helena steps**, closing the view
  down them, rather than N across the street. The OSM gate node is 1.8 m beyond the last node of the upper step
  run and in line with it. In C04 the minaret (206.9,145.8) stands on the gate's axis directly behind the
  pediment, and the prayer hall's semicircular gable shows on the right. Both are consistent only with a view
  towards ESE. **med** (one photo plus OSM).
- **Forecourt** (between e0 and the street, ~15 x 8 m, sunk below the gate landing, C03): pale slabs with pink
  ones and a **green-painted steel stair with railing** up the EAST side, at the foot of the minaret block. In C03
  it is on the left when you face the glazed entrance arch on the north face e0, so the original "west side" is
  corrected [Review R9]. The mosque entrance is a **large pointed arch filled with white-framed
  glazing**, with **"مسجد عمر بن الخطاب" painted in green** round the arch, crescents and stars, a green
  lantern on a bracket, a marble plaque engraved as an unrolled scroll, octagonal ceramic star roundels on the
  walls, green doors, and a large "La ilaha illa Allah ... islam-guide.com" banner. A **green-and-white striped
  fabric awning** is over the entrance. **high** (C01, C03)
- **Prayer hall above**: a tall block whose north facade ends in a **large semicircular gable/arch** framing a
  **quatrefoil oculus** over **three round-arched grilled windows**. Behind it is a **grey ribbed dome on a
  drum**. **high** (C01, C02, F01 crop, A09)
- **Minaret** (node (206.9,145.8), the NE corner by St Helena Rd):
  - a **square limestone shaft ~3.0-3.5 m wide**, slightly tapering, pale cream with dark grey weathering. From the
    bottom: a plain lower shaft; a stage with a **round-arched blind arch under a zigzag hood** holding a
    narrow single-light window; a stage with **twin round-arched lights with a colonnette**; then **two small
    round discs (sundial/clock roundels) on each face**; string courses between all stages. **high** (C02, A10,
    A06)
  - a **corbelled gallery on stone brackets (muqarnas-like)** with a polygonal parapet and a green-painted
    railing, sheltered by a **light timber pent canopy on slender posts**. Green neon light strips on the gallery
    at night. **high** (C02, A10, A09)
  - above the gallery, a small **cylindrical/octagonal lantern with small arched openings and a ribbed cap/dome
    with a finial**. **high** (A06, A10)
  - **Height**: top ~23-25 m above the parvis and gallery floor ~19-20 m (A09, cam (219.7,163.8) EXIF GPS, 24 mm,
    solved). The review re-solved it with the camera pitch taken into account and got 23.0 m. The uncertainty is
    ±3 m: A09 is a Sony NEX-6, which has no GPS, so its coordinates were added afterwards. The minaret rises
    from the mosque terrace, ~1.5-2 m above St Helena Rd (C02), i.e. ~+2.2..2.7 m above the parvis, so the shaft
    is ~21-22 m tall from its own base [Review R19]. The D07 figure of 33 m above the Muristan square is
    **rejected**: D07 has no camera or focal-length EXIF and is a processed image, and the survey puts the square
    only ~2 m below the parvis (section 5, Review R7). **med**
- OSM tags roof "roof_tiles, hipped" for the mosque. No photo shows a tiled roof on the prayer hall (dome +
  flat roofs, a green-grass-covered water tank, C02). **med**: do not use a tiled hip roof.

### 2.3 Lutheran Church of the Redeemer (w29268902)
Photos: E01-E05, D04, D07, D08, G04, F01-F03 (taken from its tower).
- **Footprint** 41 x 24 m bounding box (x 265-306, y 128-152); the nave is only ~13.4 m wide (y 133.5-146.9),
  and the 24 m comes from the eastern transept bits. The **west front (e16+e17, x = 265, faces 270°)** is on Muristan
  St. North (e0) faces Dabbagha behind the fenced strip, and e2 (x 291-299) reaches Dabbagha directly. The south
  (e14/e15) faces the Propstei/cloister. **high** (OSM)
- **Tower at the SW corner** of the west front, south of the portal (E04: the tower is right of the portal when
  facing east), centre ≈ (268.5,136.3), ~6.5 m square. Confirmed by the viewpoint node (270.9,136.8) and two GPS
  photos: D04 (cam (211.9,63.6)) puts it 10.4° right of the fountain against 9.9° predicted, and the D07 (cam
  (225.9,81.3)) 3-point fit leaves a 2.8° residual. If the tower stood at the NW corner instead, D04 would show
  only ~4°. **high**. Review: OSM also maps the tower itself as building:part w375040918 (x 265.1-272.5,
  y 133.7-139.4, bell_tower). The D04 angle was re-measured from the 27 mm-equivalent EXIF at 10.2°, against 10.0°
  from OSM.
  - stages (E04, D07): (1) a plain shaft with two tall round-arched windows on the side faces; (2) a **Lombard
    band (row of small corbel arches)**; (3) a stage with one round-arched opening; (4) the **belfry with two
    big round-arched openings separated by a colonnette**, bells behind low railings, and a Lombard band above;
    (5) a gallery of **4 small round-arched grilled windows per face**; a corbelled cornice; and a **steep square
    stone spire** with a small cross. Pale cream, very clean ashlar. **high**
  - **Height**: spire cross **~47 m** above the Muristan pavement (D04 solve 45.3 + 1.6 m eye; D07 solve
    45.6 + 1.6 m), with belfry eaves at **~35 m**. **med**. Review: the D04 solve reproduces (46.9-48.4 m,
    depending on where the horizon is put). The D07 solve is not independent evidence (see 2.2 and R7). The figure
    is relative to the camera ground in the Muristan lanes. terrain_street puts Muristan St at the tower's foot
    ~1-2 m lower than the fountain square, so allow **47-49 m above the street at its foot** [Review R21].
- **West front**: a gabled nave front with a **dark grey metal roof edge**, a **rose window** (round, 6-8 lobed
  tracery round a central disc with 8 holes) in the gable, and a corbel table over the portal. The **portal** is
  ~5.5 m wide x ~7.5 m: round-arched with stepped archivolts; a **tympanum with the Lamb of God medallion
  (beaded frame) on a carved 6-petal geometric ground**; twin doorways split by a trumeau column; two columns per
  side with Corinthian capitals; **dark brown timber double doors with brass handles**; shields in the
  spandrels (**Prussian eagle left, Maltese cross right**). Small round in-ground uplights in the pavement in
  front. **high** (E01, E02, E03, E04)
- **Nave side walls**: large round-arched windows with **dotted/dentilled archivolts**. Buttresses. **high** (E04)
- **Dome**: a **grey lead dome** over the eastern part (crossing/apse), seen to the right of the tower from the
  fountain. **UNVERIFIED** (D08 only) [Review R14]: the ribbed grey dome with a cross shows only above the YASSER
  block roof in D08. OSM maps no dome part on w29268902, and no other photo shows a dome on the Redeemer. It may
  belong to a building beyond. Do not model it without a second photo.
- **North side (Dabbagha)**: a deep, richly carved medieval-style round portal in the north wall, set back behind
  a stone-pier fence ~3.5 m deep. **high** (G04)
- Signage: none prominent besides the opening-hours board. Icicle string lights hang across the portal (2021,
  E01). **med**

### 2.4 Propstei (r3864634)
- A 4-storey block (OSM levels 4) on the east side of Muristan St, south of the Redeemer. Its west facade e0
  (266.0,94.3)->(265.7,119.7) faces 269°, 25 m long. Plain pale ashlar with small windows and a **red-tile roof
  eave** at the top, continuing the Lutheran look. An inner courtyard (inner ring) holds the medieval cloister.
  The forecourt at y 122-133 lies between it and the Redeemer. **low-med** (E05, distant)

### 2.5 Alexander Nevsky Church / Alexanderhof (w612045244, block w1022672084, landuse 612045222)
Photos: G01 (2026, cam (297.9,157.0), looking N), G02 (2026, cam (312.1,171.2), looking ~292°), F02/F03 (roofs).
- **Entrance facade on Suq ed-Dabbagha (w612045244 e4, x 300.8-310.1, faces S)**: 2 storeys, neo-Renaissance,
  ~11 m to the parapet, **pale cream ashlar with pink-banded rusticated pilasters**. The central entrance bay
  carries a **small triangular pediment with a monogram roundel**, twin engaged columns framing the upper window,
  a **black plaque with gold Cyrillic letters "АЛЕКСАНДРОВСКОЕ ПОДВОРЬЕ"**, an ornate **black wrought-iron
  fanlight with a gilt monogram and crowns**, and tall **pale-pink two-leaf panelled doors**, with 4-5 steps
  inside. Windows have **pink stone frames with carved rosettes** and **brown louvred wooden shutters**. A
  black iron railing runs on the roof, with a white flag on a pole. House number 25 and a ceramic street sign
  "SUQ ED-DABBAGHA" are on the facade. **Black steel bollards linked by chains** stand along the base. **high**
- **East facade and NE corner** (e3, faces E onto the N-S leg of Dabbagha): same style, with a **rounded
  (bow) corner tower** with shuttered windows, basement grilles and a yellow fire hydrant. **med** for the
  corner position.
- **Main block w1022672084** (north of Dabbagha, x 226-292): 3 storeys with rows of rectangular windows and a
  **red-tile hipped roof**. AC units. **med** (F02/F03 lower right)
- Neighbour west of the entrance: "DAJANI'S ORIENT BAZAAR" with a black roll-down shutter, a timber-boarded
  canopy on green brackets, and upper round-arched windows with grey louvred shutters. **high** (G01)

### 2.6 Muristan blocks (Aftimos market, w620317527, w620317532, w620317534, w620317526, w620317530)
- 2-storey blocks (ground-floor arcaded shops, upper rooms) with **long red-tile hipped roofs**, some with small
  dormers. OSM roof tags agree for w620317527/32/34. **high** (F01, D01, D03, D07)
- Ground floor: round-arched shop openings with fanlights, pink-stone piers at the gateways, teal/green doors
  (see 1.7). The upper floor has paired round-arched or rectangular windows with black grilles and small
  balconies with black railings. **high** (D04, D03)

### 2.7 Hospice of the Order of St John (w53474876)
- The entrance portal on Aqabat el-Khanqa (north edge e6, 21 m, faces 349°; low confidence on which edge) is a
  **narrow stone frontispiece with a triangular pediment**. It carries a **dark weathered plank sign "Johanniter
  Ordens-Hospiz" in white Fraktur letters** in a stone frame, a **large red disc (~1.2 m) with a white Maltese
  cross** in a moulded stone ring, and a segmental-arched doorway below. Corrugated canopies, cables and AC
  units crowd in front of it. **high** for the object (H01), **low-med** for the position. Review: the street
  edge itself is **med**. Aqabat el-Khanqa (ways 26491285/256298877) runs 1-2 m north of e6 along its whole
  length, and the building's addr:street is Aqabat El-Khanga. Where the portal sits along the 21 m edge is still
  unknown [Review R16].

### 2.8 Church of St John the Baptist (w166965387, (200,42), just outside the box)
(Review: the footprint spans y 31.9-54.0, so its north part, y 48-54, is inside the box. The dome itself, at
about (200,43), is outside it [R20].)
- A **gold-coloured dome clad in diamond/scale panels, with a gilt cross on a ball** (bulbous-hemispherical) on a
  plain ashlar drum block. A red-tile hipped roof building stands in front of it. It closes the SW vista from the
  fountain square and from Suq Aftimos. **high**: D05 (cam (259.3,155.2)) sees it right behind the fountain on
  a bearing of 207°, and OSM gives 207.6°. D01/D02 (cam (220.7,91.8)) and D06 also show it.

### 2.9 How landmark positions were confirmed

| landmark | position used | evidence |
|---|---|---|
| HS portal facade on the parvis north side | e55, y ≈ 183.5 | A01/A03 (GPS in the parvis, looking N), A04, A05; OSM entrance node |
| HS bell tower at the parvis NW corner (west of portal) | way 1022663529 | A04, A05 (tower left of the portals when facing N); F01 bearing from the Redeemer tower 300° vs OSM 300°. Review: the tower projects ~11 m south of the facade line (OSM y 172.6-184; A04/A05 show its east face full height beside the west portal) [R1] |
| Chapel of the Franks at the parvis NE corner | e57/e58 | A01, A03 (right end of the facade); stations X/XI nodes |
| Rotunda vs Katholikon domes | (188,203) / (211,208) | F01 bearings 309°/318° vs OSM 308°/320°; F02/F03 |
| Omar minaret S of the parvis SW corner | node (206.9,145.8) | A09 (GPS cam (219.7,163.8)): the minaret stands just left of (east of) the SW entrance steps, as OSM predicts within GPS error (~4 m); A06 (seen over the south wall); D07 (3-point fit residual 341° vs 344°); F01 (fan of bearings from the Redeemer tower consistent with minaret 278°, bell tower 300°, domes 308°/320°); G04 (closes the west vista of Dabbagha, slightly left of the street axis) |
| Redeemer tower at the SW corner of the church | ≈ (268.5,136.3) | D04 (GPS): angle between fountain and tower 10.4° observed vs 9.9° from OSM; D07 (3-point fit, residual 2.8°); E04 (south of the west portal); viewpoint node |
| Aftimos fountain | node (226.7,91.5) | D07 (GPS, residual 0.6°), D04 (relative angle above) |
| St John the Baptist golden dome | (200,42) | D05 (GPS cam (259.3,155.2)): the dome sits exactly behind the fountain, as OSM predicts (bearings 207.0° and 207.6°); D01/D02 (GPS at the fountain, looking SSW); D06 |
| Alexanderhof entrance on Dabbagha | w612045244 e4 | G01 (GPS (297.9,157.0), compass N). The facade is seen nearly head-on, so the GPS is probably a few metres west of the true camera |
| (review) Pink-pier arcade at the fountain square | east side, mouth of footway 26492718 at x ≈ 234.5, y 93-100 | D07 (GPS + 3 landmark bearings, ~14.8 px/°): arcade at 23-34° vs lane mouth 24-37°; the north block w620317526 sits at -17..+5°, behind the fountain; it abuts the YASSER block (D07 zoom, D08) [R5] |
| (review) Mosque of Omar street gate | n6779484570, facing ~W/WNW | C04 (minaret on the gate axis, prayer-hall gable on the right) + OSM (node in line with the end of the upper step run) [R8] |

---------------------------------------------------------------------------------------------------------------

## 3. GATES of the sector

The sector has **no city gate**; it is entered from David St (s05) at y ≈ 48. The gates that read as such:
1. **Parvis entrances** (see 1.4, 1.5): the St Helena Rd arch at ~(193.6,153.7) with timber doors, marble
   "HOLY SEPULCHRE" plaque and ceramic street sign; the inner SW passage and its 4 steps; the SE arched passage
   from Dabbagha (n2390928717) with the black steel "HOLY SEPULCHRE" sign. **high** (C05, A07, A08)
2. **Aftimos market gateways**: ashlar gateways with **pink-stone pilasters** (moulded bases, capitals) at the
   north end of the NE lane (≈ (258,155), D06, with the ceramic sign "שוק אבטימוס / سوق افتيموس / SUQ AFTIMOS"
   and a black heritage plaque "Aftimos Market"). A two-bay round-arched arcade on pink piers stands on the EAST
   side of the fountain square, over the mouth of the east lane (footway 26492718) next to the YASSER block. The
   original said "north side" [Review R5] (D07, D08). **high** for form, **med** for exact positions.
3. **Muristan St south gate** ("William's Gate", at the David St end, ≈ (261,41-48), on the s04/s05 boundary): a
   gate arch with a carved **imperial German eagle** (Commons captions: "Relief of eagle on Muristan Road gate").
   No photo was downloaded. **low**
4. **Mosque of Omar street gate** (2.2) and the **Alexanderhof portal** (2.5) are the most gate-like facades on
   their streets.

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Lighting
- **Black rectangular LED floodlights on short brackets** at 4-6 m on all parvis walls (warm light at dusk). **high**
  (A06, A09, A10)
- Fluorescent tubes under all souq canopies (CQR, Aftimos). **high** (B03, B05)
- **Hanging round "saucer" lamps on catenary wires** over St Helena Rd. **med** (C04)
- Green wall lantern on a curved bracket at the mosque (C03). Small round in-ground uplights in front of the
  Redeemer portal (E01). **high**
- Festive: radial festoon lights over the fountain (D08), icicle lights at the Redeemer (E01), strings of
  flags across CQR (B01). **med**

Signs and plaques
- **Ceramic street signs** (white glazed tiles, coloured border, 3 lines Hebrew/Arabic/English):
  "ST. HELENA RD." (C05), "SUQ AFTIMOS" (D06), "SUQ ED-DABBAGHA" (G01). ~0.6 x 0.5 m at 2.5-3 m. **high**
- **Black heritage plaques with a teal band** (municipal, 3 languages + line drawing): Holy Sepulchre (C05),
  Arch of the Virgin Mary (B04), Aftimos Market (D06). ~0.5 x 0.7 m. **high**
- **"HOLY SEPULCHRE"** white marble plaque in a pink frame (C05, A07). The same text in white stencil on a black
  steel sheet over the Dabbagha passage (A08), next to a **blue arrow plate**. **high**
- House-number plates: white squares with black numerals (B03 "86", B05 "109", B01 "43"); numbers painted
  directly on stone ("243 127", C05). **high**
- Shop signs: "MONEY CHANGE" orange light box (B01), "YASSER T. BARAKAT" white fascia with Arabic calligraphy
  (D07), "PAPA ANDREA" yellow board (C04), "DAJANI'S ORIENT BAZAAR" (G01), "Aladdin Restaurant" (D05).
  **high**

Bollards, railings, barriers
- **Square limestone bollards with pyramidal caps (~0.4 x 0.9 m)**, a row of 3 across Muristan St at the
  Redeemer (E05). **high**
- **Black steel bollards linked by chains** along the Alexanderhof (G01, G02). **high**
- Grey tube railings at the Arch of Mary (B04); the white tubular railing on the parvis south terrace (A06, A09);
  the green steel fence with razor wire on the mosque terrace (C02); the **fountain railing, blue (2022)**
  (D08); the stone-pier fence with railing along the Redeemer's north side (G04). **high**
- Galvanised/blue crowd barriers (G05), a steel ramp over the parvis steps (A06). **high**

Bins and others
- Green municipal wheelie bins (E05, G02), a grey cylindrical bin by the Muristan benches (D01), a yellow fire
  hydrant (G02). Wooden slat benches on black cast-iron legs in the Muristan (D01). **high**
- Vehicles and props: the red Goldoni mini tractor (B01, G04), a blue steel hand cart on bicycle wheels (G05),
  a green ka'ak bread cart (D07), stacked suitcases at the Aftimos shops (D05, D06). **high**

Flags
- **White flag with a red Jerusalem cross** on the HS bell tower (A04, 2019). A Greek Orthodox flag has also been
  recorded there (Commons title, 2012). **med**
- A white flag with an emblem on the Alexanderhof roof (G01). **high**

Vegetation
- **Parvis south terrace**: one tall **cypress (~15-17 m above the terrace; its top level with the minaret
  gallery in A06/A10)**, a **date palm (~7-8 m)** and a broadleaf tree.
  OSM trees at (218.4,147.4), (218.3,142.5), (215.4,136.7); another at (200.4,146.5) by the mosque forecourt.
  Review: bearings from A09 (GPS) and A06 (camera solved) put the cypress ~4-5 m west of the OSM tree nodes,
  near the mosque's NE corner at about (213,147). Treat the tree positions as ±5 m (**low**, R18).
  They are seen from the parvis, from Dabbagha and from the Redeemer tower. **high** (A06, A09, A10, F01, F03, G04)
- **Olive tree** on the Monastery of Abraham terrace above the parvis east side (A01, A03). **high**
- **Pines and cypresses** of the Martin Luther School garden along Muristan St (E05; OSM trees at (272-294,
  66-120), forest landuse 1085708308). **high**
- Tree at the Deir es-Sultan roof (OSM (270.1,217.4); F02 right). **med**
- Wall plants: **capers and weeds** in the joints of the HS walls, the minaret and the parvis chapels (A05, A07,
  A10); a grapevine at the St Helena gate (C05); pink geraniums in boxes on the mosque terrace (C02); potted
  plants at café fronts (D04). **high**

---------------------------------------------------------------------------------------------------------------

## 5. TERRAIN

Relative levels (z = 0 at the parvis paving), with how each was obtained:

| place | z (m) | basis | confidence |
|---|---|---|---|
| HS parvis | 0 | datum | |
| St Helena Rd at the parvis SW entrance (y 155) | +0.6..0.7 | OSM steps 616344391: 4 steps | high |
| St Helena Rd, foot of the upper step run at the jog (x ≈ 194) | ~+2.5 | lower run 12.5 m of low steps (C06 risers 0.12-0.18 m, treads 1-1.6 m → ~10 steps) | med-low |
| CQR at the St Helena junction (167,148) | ~+6..7 | upper run 27 m of steps (~20-25 steps at 0.15-0.18 m) | low-med |
| Minaret base (St Helena Rd, x ≈ 207) | +0.7 (street); the minaret itself stands on the mosque terrace, ~+2.2..2.7 | OSM; C02 terrace wall 1.5-2 m [Review R19] | med |
| Suq ed-Dabbagha at the parvis SE gate (224.5,156.4) | ~-1..+0.5 (**unverified**) | A08 passage, no flight of steps visible; terrain_street gives -0.8 against +0.65 for the strip inside the gate | low |
| Suq ed-Dabbagha at x ≈ 237 | **~-2.5** | OS 1865 spot height (237.6,152.1) 2476 ft = 754.7 m [Review R7] | med |
| Suq Aftimos north entrance (259,155) | ≈ fountain square level, **~-3.0** | D05: far people's heads stay on the horizon along the 70 m lane; terrain_street -16.3 (street datum) | med |
| Muristan fountain square (227,91) | **~-2 (±2)** (replaces ~-7..-9) | terrain_street -15.5 (street datum). The Muristan has no 1865 spot height (it was a ruin field then), but the surrounding ones do: Dabbagha 754.7 / 753.5, Propstei 754.4. The D07 minaret solve behind the old value is rejected [Review R7] | med-low |
| Muristan St at the Redeemer (264,140) | **~-3.9**, i.e. ~1.8 m below the fountain square | terrain_street -17.3; OS 1865 spot heights (285.8,152.2) 753.5 m on Dabbagha and (298.7,122.3) 754.4 m | med |

Notes
- **CQR climbs gently northwards** from David St to the St Helena junction (no steps in the photos). Review: the
  DSM figures (+9 m) were wrong. The OS 1865 spot heights are 762.3 m at (179,53) and 761.7 m at (173,132), i.e.
  nearly level. terrain_street gives 761.9 → 763.7 m from y 9 to y 148, about +1.8 m in 140 m, and 764.1 m at
  y 221. So CQR is ~4.5 m (David St end) to ~7 m (y 221) above the parvis. **med**
- **St Helena Rd is the main stair of the sector**: two runs, ~40 m together, going down east from CQR to the
  parvis. It is the visible drop between the high CQR ridge and the sunken parvis. **high** for the stairs,
  **med** for the totals.
- The Dabbagha / Muristan level vs the parvis was the main open question. Two height solves (A09 and D07) had
  implied the Muristan square is ~8 m below the parvis. **Resolved in review [R7]:** use `street_z()` from
  `pipeline/terrain_street.py`, which is fitted to the OS 1865 survey. Dabbagha falls ~3 m from the parvis SE
  gate to the Redeemer (754.7 m at x 237, 753.5 m at x 286), about 5%, which matches G04 and D05 showing no big
  stairs. The Aftimos NE lane is nearly level (D05), and the fountain square sits ~2 m below the parvis. The D07
  vertical solve was the outlier: D07 carries no camera or focal-length EXIF and is a processed image.
  The parvis itself has no 1865 spot height. Its level (~757.2 m asl ≈ street_z -13.35) follows from St Helena at
  the SW entry (street_z -12.7) minus the 4 steps. street_z returns the smooth street surface and does not know
  that the parvis is sunken, so flatten the parvis at that level.
- Raised platforms: **shop platforms 0.35-0.45 m on St Helena Rd** (C06), **0.12-0.18 m thresholds** in the
  Muristan (D05), a **raised east sidewalk ~0.15 m** on Muristan St (E05), a **mosque terrace ~1.5-2 m** above
  St Helena Rd (C02), and the **parvis south terrace ~4.5 m** above the parvis (A06, A09).
- Other OSM stair runs in the box (OSM only): Via Dolorosa 25 + 27 steps (x 317-405, y 292-310), Ethiopian
  Monastery steps 22 (from Aqabat el-Khanqa at (266,280) UP to (256,311), going north-west, away from Deir
  es-Sultan; direction corrected per the incline tag [Review R15]), Al-Battikh Ascent
  (108 m, layer -1), HaTut 40 steps, At Takiyyeh Rd (tunnel), steps 744696592 beside the Alexanderhof
  (300,154)→(301,164).

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **HS parvis as a sunken walled courtyard** (OSM way 612045223: ~17 m clear E-W, 12-14 m at the north end,
   27 m N-S; bounding box x 204-226, y 157-184): big polished irregular slabs with pink ones,
   3-4 seating steps along the south wall with the ramp at x ≈ 211, column stumps, black wall floodlights, entries
   at SW (4 steps) and SE (arched passage). (1.5)
2. **HS south facade**: two pointed portals on clustered marble columns (east one walled up), carved string
   course, two pointed upper windows with small-pane iron grids and hoods, the ladder under the east window,
   carved cornice at ~18-19 m and a black roof railing at ~20 m. (2.1)
3. **HS bell tower** at the parvis NW corner, standing ~11 m forward (south) of the facade line with its east face
   on the parvis (OSM y 172.6-184): ~11 m square, paired round-arched windows, belfry with bells (south face), low
   red-tile hipped roof with eaves (~26 m), red-cross flag. (2.1)
4. **Rotunda + Katholikon domes**: a big ribbed grey dome (~21 m, top ~34 m) and a smaller grey dome on a
   windowed drum with a gilt cross. Seen from everywhere above the roofs. (2.1)
5. **Omar minaret** at (206.9,145.8): square pale shaft ~3.2 m, twin-light and blind-arch stages, roundels,
   corbelled gallery with timber pent canopy and green railing, small domed lantern, top ~23-25 m above the
   parvis; plus the **cypress + palm** on the parvis south terrace next to it. (2.2, 4)
6. **Redeemer tower** at the church's SW corner: ~47 m, Lombard bands, twin-arched belfry, small-arch gallery,
   steep square stone spire, all very clean pale stone. (2.3)
7. **Christian Quarter Rd roofed-souq profile**: 4-5 m, teal panelled steel doors with padlock bars, timber
   shed canopies on big green hoop brackets, open green sunburst arch ribs over the sky slot (sheeting only
   locally, if at all), centre-line manholes; the polished giant slabs at y ≈ 105-125. (1.2)
8. **St Helena Rd stair**: two runs of broad low steps (risers 0.12-0.18, treads 1-1.6 m) between 0.4 m shop
   platforms; the arched gate with timber doors, the marble "HOLY SEPULCHRE" plaque and the ceramic street sign;
   the mosque terrace wall with green fence and razor wire. (1.4)
9. **Muristan fountain square**: dark-grey disc with pale concentric arcs, the Aftimos fountain (pedestal,
   lion spout, urn at ~4.5-5.5 m, 4 columns, blue railing), café tables, the 2-storey red-roof north block behind
   the fountain, and the pink-pier arcade on the EAST side over the east-lane mouth. (1.6)
10. **Aftimos market blocks**: 2 storeys, long red-tile hipped roofs, round-arched shopfronts with teal fanlights,
    pink-stone piers; big beige retractable awnings over the NE lane and quarter-round translucent awnings. (1.7, 2.6)
11. **Golden dome of St John the Baptist** at (200,42), closing the SW vistas from the fountain and Suq
    Aftimos. (2.8)
12. **Redeemer west front on Muristan St**: Lamb-of-God tympanum, twin doors on a trumeau, Prussian-eagle and
    Maltese-cross shields, corbel table, rose window. Square stone bollards and pines along Muristan St. (2.3, 1.8)
13. **Suq ed-Dabbagha**: 9 m wide by the Redeemer (fenced strip and deep north portal), green-hoop canopies
    on the north side; the Alexanderhof facade with pink-banded pilasters, gold Cyrillic plaque, pink doors and
    chained black bollards. (1.7, 2.5)
14. **Mosque of Omar street front**: the white neo-classical gate (pediment, rosette, "Mosque of Omar" plaque)
    and the forecourt with the green-lettered pointed glazed arch; the prayer hall's semicircular gable with
    quatrefoil and grey dome. (2.2)
15. **Roofscape and the temporary HS roof tent/scaffold**: black railings on the HS terraces, the white membrane
    tent (2015-21) or the 2025 scaffold canopy over Calvary, red-tile hipped roofs of the Muristan, Alexanderhof
    and Propstei, solar heaters and dishes elsewhere. Choose one state and keep it consistent. (2.1)

---------------------------------------------------------------------------------------------------------------

## Provenance

45 Commons photos in `data/photos_ref/s04_sepulchre/` (1280 px thumbnails; `index.json` has title, page,
author, licence, date, lat/lon and local x/y where geotagged). Groups: A = parvis/facade/bell tower, B = Christian
Quarter Rd, C = St Helena Rd and Mosque of Omar, D = Muristan, E = Redeemer and Muristan St, F = views from the
Redeemer tower, G = Dabbagha and Alexanderhof, H = Johanniter Hospice. The most useful: A01-A03, D01-D04 (a GPS
walk by מקף־עברי, 21 Dec 2025, CC BY-SA 4.0); A04/A05/A07/A08/B04/H01 (Fallaner 2018-19, CC BY-SA 4.0); A09
(eugene_o 2016, CC BY 2.0, GPS); D07 (Ludvig14 2016, CC BY-SA 4.0, GPS); F02/F03/E01/C03 (Bukvoed 2019-21,
CC BY 4.0); D05/G01/G02 (PikiWiki 2026, CC BY 2.5, GPS + compass); B05 (Zairon 2014, all shops closed).
G03 turned out to be an interior shot (not used). C06 is a 2011 photo kept because the shops are closed and the
steps are clear.
Review caveat on the `index.json` coordinates [R17]: several x/y values there are not camera positions.
- F01: iPhone panorama tagged (211.7,130.6), ~57 m west of the Redeemer tower it was taken from.
- D06, E04, E05: share the identical rounded coordinate (259.0,158.3), a place geocode.
- E03: (286.6,146.2), inside the church footprint, ~20 m from the west portal it shows.
- C06: (6.1,-53.1), outside the sector.
- A09: a Sony NEX-6, which has no GPS, so its coordinates were added afterwards (±10 m).
Positions checked in review: A01-A03 and D01-D04 (Fujifilm X-S20 EXIF GPS, 27-41 mm equivalent), D05 (iPhone 16
Pro Max GPS; its compass is ~15° off), D07 (GPS position consistent with three landmark bearings), and B02/B06 (two
photographers give the same spot). G01/G02 come from the same PikiWiki 2026 batch as D05; their EXIF was not
checked.

---------------------------------------------------------------------------------------------------------------

## Review

Independent review, 2026-10-19. Method:
- Opened all 45 photos and zoomed where needed.
- Looked up every cited OSM id in `data/osm_local.json` (edges, outward normals, tags).
- Recomputed street widths with perpendicular rays to building footprints, skipping building:part.
- Re-read the Commons EXIF (camera, focal length, GPS, compass) for A01, A06, A09, D01, D04, D05, D07 and F01.
- Took levels from the project's OS 1865-based `data/terrain_street.json` (docs/TERRAIN.md).
No code was edited and git was not run.

### Corrections (body text changed in place; tags [Review Rn] / [Rn] mark the spots)

**R1. HS bell tower: wrong side on the facade line (position/orientation, major).**
- The notes said the tower's "south face is flush with the portal facade" (G table, 2.1).
- OSM way 1022663529 spans y 172.6-184.0. The facade edges e54/e55 run at y 183.1-184.3. So the tower's NORTH
  side lies on the facade line, and the tower stands ~11 m forward (south) of it, along the parvis west side.
  Its east face (x ≈ 204-205, y 172.6-184) is the parvis NW corner.
- Photos confirm it. In A04 and A05 (camera in the parvis, SE of the tower) both the south and the east face are
  visible. The east face, with its oculus and a lower window, runs down below the facade cornice to the
  parvis-level blocks next to the west portal. That cannot happen if the south face is in the facade plane.
- F03 (from the Redeemer tower) shows the tower standing in front of the facade.
- Fixed in: section 0 item 1, the G table, 2.1, the 2.9 table and checklist item 3.

**R2. Bell tower: the bells show on the south face, not the east face.**
- A04 shows which face is which. The face with the big blind arch is the south face. The east face is the one
  that carries the oculus and meets the facade.
- A05 shows the bells in the paired openings above the big blind arch, i.e. on the south face. **med**

**R3. Parvis width.**
- "~22 m E-W" is the bounding box of OSM way 612045223.
- The clear width is 17.2-17.5 m for y 160-171 and y 177-178, and ~20 m at y 172-176 (the tower's east face).
  It narrows to 12.0-13.9 m at y 179-184, between the Chapel of the Franks (x 218.7) and the projection on the
  tower's east face (x 204.7-206.8). Area 447 m².
- The Franks projection is 5.2 m deep (y 184.3 → 179.1), not ~4.5 m.

**R4. Ramp and Metochion doorway on the parvis south side.**
- The notes put the ramp at the "SE third" and the doorway at the "east part".
- OSM puts the ramp on steps way 616344391 (4 steps, ramp=yes) at x ≈ 211, in the west-centre. The Metochion
  POI is at (213.4,154.6).
- A06 (Panasonic DMC-FS10, 5 mm ≈ 28 mm equivalent per EXIF) fits these: with the camera solved at ≈(207,172),
  the door, ramp and minaret bearings match within ~5°. The ramp sits just right of (west of) the door, and the
  door sits where the low terrace wall meets a taller building on the east.
- A09 puts that junction at x ≈ 213-217.
- The "4 steps + ramp" SW entrance and the "3-4 seating steps along the south wall" are the same feature: the
  drop from the St Helena-level strip (way 612045234) into the parvis.
- The terrace with railing, cypress and palm sits behind the west part of the south side. The east part is a
  taller 2-storey building (white domed kiosk on top in A09).

**R5. Muristan fountain square: two misidentifications.**
- (a) The 2-storey red-tile-roofed block with the black-railed balcony, directly behind the fountain in D07 and
  D08, is the north block w620317526 (south face e0 plus SW face e3), not the west block w620317527.
- (b) The two-bay arcade on pink piers is on the EAST side, not the north side. It is a gateway over the mouth of
  the east lane (footway 26492718, x ≈ 234.5, y 93-100), between w620317534 and the YASSER block w620317532.
- Evidence: D07 has a GPS camera at (225.9,81.3), and its image positions are fitted to three OSM landmarks:
  minaret 343.6° (x ≈ 150), fountain 4.5° (x ≈ 460) and Redeemer tower 37.8° (x ≈ 950), about 14.8 px/°.
  - w620317526 e0 spans -17°..+5° (x 160-470): directly behind the fountain.
  - The west block's square face lies at bearings below -29°, out of frame.
  - The arcade at x 730-900 means 23-34°, which matches the east-lane mouth at 24-37°.
  - A zoom on D07 shows the arcade abutting the YASSER block.
  - D08 shows the same arrangement, with the Redeemer tower rising above the arcade.
- Fixed in: 1.6, section 3 item 2, the 2.9 table and checklist item 9.

**R6. Christian Quarter Rd roof.**
- The notes described a "translucent barrel roof ... runs continuously" as **high** (B03, B05, B06).
- B06 (2014, y ≈ 110) clearly shows open rib arches, with the upper house walls and a tree visible between them.
- B05 (2014) shows the same open ribs against the sky, with a short blue translucent section far down the street.
- Only B03 (2015, y ≈ 45, overexposed) could show white sheeting.
- The ribs stay high-confidence. Sheeting is now **low / unverified**. Fixed in: 0.5, 1.1, 1.2, checklist 7.

**R7. Terrain: the Muristan is ~2 m below the parvis, not 7-9 m.**
- The −7..−9 m figure rested on the D07 solve: minaret top 33 m above the square. D07's Commons metadata has no
  camera, focal length or valid date. It is a processed image, possibly stitched, so its vertical geometry
  cannot be trusted.
- OS 1865 spot heights (anchors in `data/terrain_street.json`):
  - (195.5,146.3) 759.0 m, at the St Helena jog / mosque forecourt
  - (237.6,152.1) 754.7 m, Dabbagha
  - (285.8,152.2) 753.5 m, Dabbagha by the Redeemer
  - (298.7,122.3) 754.4 m, Propstei
  - (173.4,132.2) 761.7 m and (179.0,53.2) 762.3 m, CQR
  - (161.5,220.7) 764.1 m, CQR
- Model values (`street_z`):
  - fountain −15.5
  - Aftimos north entrance −16.3
  - Muristan St at the Redeemer −17.3
  - St Helena at the parvis SW entry −12.7, so the parvis is ≈ −13.35 (757.2 m asl)
  - St Helena jog −10.9
  - CQR at the St Helena junction −6.9
- Relative to the parvis that gives: fountain ~−2, Dabbagha −2.5 to −3.7, Muristan St at the Redeemer ~−3.9,
  CQR +4.5 to +7.
- The A09 minaret solve is kept (23-25 m above the parvis). The review's own solve with camera pitch gives 23.0 m.
- The old "CQR rises 767 → 776 (DSM)" is replaced by the survey: nearly level, +1.8 m from y 9 to y 148.
- Fixed in: section 0 item 7, 2.2, 5 (table and notes).
- Still unresolved: terrain_street gives −0.8 at the Dabbagha SE gate, against +0.65 for the strip inside it.
  Check A08 / the passage for a step there.

**R8. Mosque of Omar street gate orientation.**
- The gate node n6779484570 (195.6,150.6) is 1.8 m beyond the last node (193.8,150.4) of the upper St Helena step
  run, and in line with it.
- C04 shows the minaret (206.9,145.8) directly on the gate's axis behind the pediment, with the prayer hall's
  semicircular gable on the right. Both point to a view towards ESE.
- So the gate faces ~W/WNW, up the steps, closing the vista. It does not face N across the street.
- **med** (one photo plus OSM). The route turns left (north) here through the HS arch with the "HOLY SEPULCHRE"
  plaque (C05) onto the lower run.

**R9. Mosque forecourt stair: on the east side, not the west.**
- In C03 the green steel stair is on the left of the glazed entrance arch. That arch is on the north face e0, so
  the camera looks south and left is east.
- C01 confirms it: the minaret and the "La ilaha illa Allah" banner wall sit on that same left side. **med**

**R10. HS roof railing colour depends on the year.**
- It is white/silver in 2019 (A04, zoomed, in sun) and dark grey/black in 2025 (A01-A03). Pick by target year.

**R11. Arch of the Virgin Mary position.**
- OSM node n7056393666 (167.8,221.9) is ~7 m east of the CQR centreline (x ≈ 160.6 at y 222). It sits inside the
  HS footprint, at the corner of a notch that opens north (edges e22/e23).
- B04 shows the arch facing the street pavement, with only a ~1 m railed strip in front.
- Model it in CQR's east wall at y ≈ 222, facing W. Position downgraded high → **med**: one node and one photo,
  with no second viewpoint.
- "Round" arch: the apex is hidden by a later pier in B04, so the shape is **unverified**.

**R12. D05 heading.**
- The note's ~227° comes from the EXIF compass (222.5° magnetic, iPhone).
- The image centre is on the lane axis and the gold dome, i.e. ~207°.
- The conclusion (dome behind the fountain, bearings 207.0° vs 207.6°) is unaffected.

**R13. Muristan St width beside the Redeemer: conflict (unverified).**
- OSM gives 3.0-5.7 m at y 137-141: the centreline is 1 m from the west front, and w290821789 is 2-5 m away.
- E05 shows ~6-7 m, including a ~2 m raised sidewalk.
- E05's camera position is unknown (its coordinates are a place geocode). One of the two is wrong; check before
  modelling. The 6.4-6.5 m beside the Propstei is confirmed.

**R14. Redeemer "dome": unverified.**
- It rests on D08 alone: a grey ribbed dome with a cross, showing above the YASSER block roof.
- No dome part is mapped on w29268902, and no other photo shows one on the Redeemer. Downgraded med →
  **unverified**; do not model it without a second photo.

**R15. Ethiopian Monastery steps direction.**
- Way 617363483 is drawn (266.5,280.0)→(255.7,311.3) with incline=up. It climbs NW from Aqabat el-Khanqa, away from
  Deir es-Sultan. The notes had the direction reversed (1.9, 5).

**R16. Hospice: the street edge is better supported than stated.**
- Aqabat el-Khanqa runs 1-2 m north of e6 along its whole length, and the building's addr:street matches.
- The edge is now **med** via OSM. Where the portal sits along e6 is still unknown.

**R17. Photo index coordinates.**
- F01: the panorama is tagged (211.7,130.6), ~57 m west of the tower it was taken from.
- D06, E04, E05: share the place geocode (259.0,158.3).
- E03: inside the church footprint.
- C06: outside the sector.
- A09: the NEX-6 has no GPS, so the tag was added later (±10 m).
- The notes relied on none of these for positions except A09 (minaret height ±3 m). Added under Provenance.
  `index.json` itself was not edited.

**R18. Parvis trees (low).**
- A09 (GPS) and A06 (solved camera) bearings intersect at ≈(213,147) for the cypress, ~5 m west of OSM tree
  n12893656142.
- Treat the tree nodes as ±5 m.
- The cypress top is level with the minaret gallery (A06, A10), ~19-21 m above the parvis. So the "15-17 m"
  is its height above the terrace.

**R19. Minaret base.**
- The minaret stands on the mosque terrace, ~1.5-2 m above St Helena Rd (C02), not at street level.
- The top stays 23-25 m above the parvis. The shaft is ~21-22 m tall from its own base.

**R20. St John the Baptist.**
- The footprint (y 31.9-54.0) reaches into the box. The dome itself, at about (200,43), is outside it.

**R21. Redeemer tower.**
- Added the OSM tower part w375040918 (x 265.1-272.5, y 133.7-139.4), which confirms the SW corner directly.
- The D04 angular check reproduces: 10.2° measured against 10.0° predicted, using the 27 mm-equivalent EXIF.
- The D04 height solve reproduces at 46.9-48.4 m above the camera ground.
- The D07 solve is not independent (R7). Muristan St at the tower's foot may be ~1-2 m lower than the Muristan
  lanes, so use 47-49 m. **med**
- Also noted: the nave/west front is only 13.4 m wide; the 41 x 24 m is a bounding box.

### Checked and confirmed (no change)
- HS portal facade on the parvis north side, e54+e55, faces 176°. The west door is the working entrance and the
  east door is walled up (A04, A05). The ladder is under the east upper window (A02). The Chapel of the Franks
  and its small dome are at the NE (A01, A03; OSM w1022663509).
- Rotunda vs Katholikon: the bigger ribbed dome is the Rotunda (188,203). The smaller dome on a windowed drum,
  with the gilt cross, is the Katholikon (211,208). From the Redeemer tower they bear 309° and 321° and appear in
  that order in F02, F03 and F01. The A02 gilt cross over the facade centre is the Katholikon's.
- Omar minaret at OSM n12893656140, the mosque's NE corner, with the forecourt to its west (C01, C03). It has a
  square shaft, a blind-arch stage, a twin-light stage, roundels, a corbelled gallery and a lantern (C02, A06,
  A09, A10). It closes the west vista of Dabbagha (G04).
- Redeemer: the west front is on Muristan St and the tower is right of (south of) the portal (E04). Portal
  details confirmed: Lamb of God tympanum, trumeau, eagle on the left, Maltese cross on the right (E01, E03).
  The medieval north portal is behind a pier-and-railing fence on Dabbagha (G04).
- St John the Baptist gold dome on the D05 lane axis behind the fountain; D01/D02 look SSW at it (bearing 203° from
  the EXIF camera).
- Alexanderhof entrance facade (e4, faces S) and its details (G01). The bow corner (G02) is consistent with the NE
  corner.
- OSM widths reproduce:
  - CQR 4.0-5.6 m, 3.0 m at y 208-214, pockets at y 94-106
  - Dabbagha 1.8-5.0 m at the west end, 9.1-9.5 m by the Redeemer
  - Aftimos NE lane 6.4-8.4 m (9.8 m at the y 118 junction), SE lane 10.3-10.4 m, E-W lane at y 118 3.2-5.3 m
  - St Helena upper run 5.4-5.6 m and 8.2-8.3 m; the lower run is open to the south (9.8-15.1 m to the mosque)
- St Helena step directions (incline tags) and the gate nodes are as stated. The street-level heights, +2.5 at the
  jog and +6..7 at CQR, agree with terrain_street.

### Claims resting on one photo or none (left in, flagged)
- Muristan St "William's Gate" eagle relief: no photo.
- Propstei massing and roof: E05, distant only; 4 storeys is from OSM levels alone.
- Redeemer dome: D08 only (R14).
- Mosque gate orientation: C04 only (R8).
- Arch of Mary shape (B04).
- Column stumps in the parvis: A04 only.
- Strings of flags across CQR: B01 only.
- Chapel of the Franks external stair: hidden in 2025.
- The dark rock-faced block at the tower/west-side junction: "~4 x 4 m" against OSM's ~2 x 6 m projection
  (e50-e52); unverified.
- HS bell tower height (eaves 23-24 m, apex ~26 m): one scaled photo against OSM's 30 m; not re-solved.
- The north-east part of the box: OSM only, as the author stated.
