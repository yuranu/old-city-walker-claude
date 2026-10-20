# s01_armenian: Armenian Quarter (St James, Armenian Patriarchate Rd): visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (as in `citadel_east.md`).
Sector polygon: `data/sectors.json` id `s01_armenian` (x 8-250, y -42 to -300; west edge = city wall,
north edge y = -42 just south of the Citadel moat / Christ Church gate).
Photos: `data/photos/NNN_*.jpg` (project set) and `data/photos_ref/s01_armenian/NN_*.jpg`
(downloaded for this note; title, author, licence, date, lat/lon in `index.json` there).
Scale from people (~1.7 m), doors (~2.1-2.2 m) and OSM edge lengths.
Confidence: **high** = seen clearly in 2+ photos or measured in OSM; **med** = one clear photo or a
consistent estimate; **low** = inferred.

> Status: complete (written incrementally, 2026-10-19). 45 Commons photos downloaded for it (43 used) + 2 project photos (006, 137).
> Independent review 2026-10-19: corrections are made in place and tagged **[Rn]**; the old value is kept as "(was ...)".
> Every correction, with its evidence, is listed in **## Review** at the end, together with the claims that could not be verified.

---------------------------------------------------------------------------------------------------------------

## 0. Layout from OSM (what the walker meets, north to south)

Armenian Patriarchate Rd = OSM ways 265414845 (`The Armenian Patriarchate Street`, sett, from the gate),
26506007, 44376249 (covered, `layer -1`, `maxheight 2.9`), 44376240, 290669005 (`tunnel=yes`), 26492736
(continues south of the sector to Zion Gate). Wall-to-wall widths measured by casting perpendicular rays from
the OSM centre line to the nearest building footprint or wall (script in the session scratchpad):

| stretch (y) | centre line x | east side | west side | wall-to-wall |
|---|---|---|---|---|
| -42 to -78 | 113 → 109 | Christ Church compound (w1394456869, w1394456870, gate node (123.5,-46.4)) | Citadel/Kishle retaining wall (way 290669977) | 12-13 m at y -51..-63; **~8 m at y -67..-72.5** beside the projecting south end of w1394456869; 17-18 m at the gate-passage mouth y -43..-47 **[R3]** (was 10-13 m) |
| -78 to -90 | jogs SE to (114,-86) | w1550194749 | police compound gate (node 9937882129 at (102.8,-89.4)), w290669980 | 15-23 m: small widening / police forecourt |
| -90 to -165 | 117.5 → 116 | continuous row w1394456871/73/74, w1392907916 (Armenian Tavern node (124.1,-131.5)), w1392907908/09/10 | row of buildings w290669980 (16 m deep), w1394899938 (10 m), w1394458560, w1394458561 (5-6 m) backing on the big police/Kishle parking **[R4]** | **4.0-5.9 m** (min 4.0 m at y ≈ -116, 4.5 m at y ≈ -92); OSM gaps in the east row at y ≈ -148 and y -160..-164 (unverified) **[R4]** (was 4.7-5.8 m) |
| -165 to -183 | 115 → 113 | w1392907911 | opens west (Bulghourji restaurant node (108.5,-175.9), w1545817482) | 7-34 m: junction space at the head of St James St **[R4]** (was 11-35 m) |
| -183 to -211 | 113 → 108 | inside **w1392907903** (road passes under it: way 44376249 layer -1, maxheight 2.9 m) | — | covered passage ~28 m long |
| -211 to -265 | 108 → 106 | St James Monastery: w290678899, then **w612002272 Patriarchate Administration**, gate/ATM at y ≈ -223 | open to the west (garden w1394066412, seminary grounds 290670297); wall not in OSM | 4.4-5.5 m from the centre line to the convent wall |
| -265 to -293 | 106.5 → 107 | under **w1394456881** (`building=roof`, layer 1) between w612002272/w290668993 (E) and w1394456882 (W) | | covered ~28 m |
| -293 to -300 | 107 | w290668993 | w290669003 / residents' parking | 16 m, sector edge |

Other streets in the sector (OSM `name:en`): **Saint James Street** (way 26492729, pedestrian, sett,
from (113,-183) east to (217.7,-152.4), 122 m; 13-32 m between footprints in its west half where it skirts
open plots and the St Toros / convent block, **3.2-4.5 m** in its east half x 186-213 (was 3.4-6 m). The wide OSM gaps
are unmapped garden walls: photos geotagged at x 152-172 show a ~3-3.5 m walled lane **[R13]**); **Or HaHayim** (26506008,
continues east, 6 m); **Ararat** (44376205 tunnel, steps 44376214, 44376246); **HaMalakh** (26506016,
290677051; 2.6-5.5 m); **HaShofar** (123255617); **HaKinor** (254576592); **Maronite Convent** (north of the
sector edge); **Biqqur Holim** (290692959, 616359702 steps).

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and street profiles

**Character.** Unlike the souqs, the Armenian Quarter is a *walled-compound* quarter: the walker moves along
a single asphalt service road (Armenian Patriarchate Rd) between **very long, tall, almost blind convent and
compound walls** of pale grey-white ashlar, pierced by small grilled windows, with a few heavy arched gates.
There are almost no shop fronts (a handful of ceramics/souvenir shops, two restaurants). It is quiet, cleaner
and brighter than the souqs, with **black steel bollards, parked cars and real kerbs/pavements**, and with
greenery spilling over walls (pines, olive, bougainvillea, ivy). Two **vaulted tunnels carry buildings over the
road** (y -185..-211 and y -265..-293) and are the strongest set pieces. East of the road the lanes (St James St,
Ararat, HaMalakh) are narrow **paved pedestrian lanes with flying arches** between high walls. **high**
(01-05, 13, 15, 17, 20-28)

### P1. Armenian Patriarchate Rd, "Christ Church stretch" (y -42 to -80) — OSM `The Armenian Patriarchate Street` (265414845)
- Wall-to-wall 12-13 m along most of the block, narrowing to **~8 m at y -67..-72.5** (OSM) (was 10-13 m): Citadel retaining wall / moat railing on the west, Christ Church compound
  frontage on the east (w1394456869 = post office + Christ Church café, w1394456870). The frontage is not straight:
  the south 5.5 m of w1394456869 (edges e5/e6) **projects ~5 m west to x 112.3**. Its north face (e6, faces 355) holds the
  café entrance (a round arch and a stone roundel), and the café terrace sits in the angle with the main west face
  (x ≈ 117). The café node (116.2,-64.6) falls exactly in that angle **[R3]**. **high** (OSM, 33, 34)
- Carriageway ~6 m of **small dark grey setts** (same as the square, 10 x 10-20 cm) with a pale limestone
  kerb band; east pavement ~1.5-2 m of pale slabs at almost the same level. **high** (34, 33)
- East frontage (34, 2019; 006 from Phasael): the street block w1394456869 (22.7 x 9.3 m, y -49..-72) is
  **one tall storey (~5 m) with flat roof terraces and a low barrel-vault hump** (006); above and behind it rises
  the 2-storey Christ Church Guest House (w126783156) with a **hipped red clay-tile roof** (006, 33). No solar panels
  are seen on the Guest House roof in 006 or 33. The tiled roof with a solar panel in 34 belongs to another building,
  possibly w290690288 north of the gate (unverified) **[R2]** (was "...roof and solar panels (34, 006, 33)"). Street face: honey ashlar, a **round-arched opening with a black wrought-iron scroll grille**, a small
  oculus, plain rectangular windows with stone surrounds; a **grey corrugated sheet shed awning** over a souvenir shop
  with dark green doors (postcard racks), a **grey fabric awning with a scalloped valance lettered "CHRIST
  CHURCH"** (café, OSM node (116.2,-64.6)), a **red Israel Post parcel-locker kiosk** (OSM node
  (116.2,-54.1)) and wall post box (117.5,-48.7) at the post office (node (118.4,-51.8), "57 Armenian
  Patriarchate Rd"). Green cables slung along the facade at ~3.5-4 m. **high** for objects (34 + OSM nodes),
  **med** for exact order.
- The Christ Church gate (OSM barrier node (123.5,-46.4), fence way 441505559) sits in a short passage leading
  east off the road at y ≈ -46: **white-painted steel bar double gates (~3 m high, spear-head tops)**, a second
  inner gate, raised dark letters **"CHRIST CHURCH GUEST HOUSE"** on the wall right (south) of it above a
  round-arched opening, a CCTV camera. On the north side of that passage (building w290690288, on the s00 edge)
  a **grey scalloped awning "BIBLES STAMPS ANOINTING OIL GIFTS"** over round-arched windows with black grilles.
  **high** for the gate (006 crop, 33, OSM gate node), **med** for the lettering positions.
- At y ≈ -78..-90 the road widens into a **paved forecourt (~20 x 15 m) of large grey setts in front of the
  police station (Kishle) north facade** (w290669980 edge e5, 24 m, faces 356): 2-storey honey ashlar with a
  **hipped red-tile roof**, seven round-arched upper windows, a round-arched vehicle gate ~10 m from its west end,
  blue police barrier panels and flags (see L4). **high** (33 + OSM police polygon 1084488109)

### P2. Armenian Patriarchate Rd, "narrow stretch" (y -90 to -170) — OSM 26506007
- **Wall-to-wall 4.0-5.9 m** (OSM, both sides built up; min 4.0 m at y ≈ -116) **[R4]** (was 4.7-5.8 m); photos agree: one car width plus a ~1.2-2 m pavement.
  **high** (OSM widths, 05, 13, 21)
- **Surface change at the police forecourt**: OSM tags way 265414845 (gate → (113,-83)) `surface=sett` and every
  way south of it `surface=asphalt`; photos agree (setts in 33/34, asphalt in 05, 13, 21, 01-04). **high**
- Section (looking south, 05, 2026): east pavement ~1.6-2.0 m of large pale limestone slabs (0.5 x 0.8-1.0 m,
  running bond) with a **flush/low kerb (≤5 cm) of long pale kerb stones**, asphalt carriageway ~3.2-3.5 m,
  west kerb strip ~0.4 m. Further north (13, 2018) the asphalt runs wall to wall at the Tavern with patched
  trench scars. Black steel bollards (**~0.6-0.7 m** **[R6]** (was ~0.8-0.9 m), ~0.11 m dia., one white reflective band near the top) at
  ~1.5-2 m spacing on the east kerb line south of the Tavern. **high** (05, 13, 21)
- **West side: a continuous blind wall ~6.5-7.5 m high** **[R5]** (was 8-10 m) (the police/Kishle compound row w290669980, w1394899938,
  w1394458560, w1394458561) of regular pale ashlar (courses 0.35-0.45 m) with a row of **tall round-arched
  windows (sills ~2.5-3 m, windows ~1.6 m tall** **[R5]** (was sill ~4.5 m)**) fitted with dark louvred/grilled shutters**, cables along it, and **a 2 m
  steel mesh security fence on brackets along the parapet**. No doors at street level. **high** for form (05, 13, 21),
  **med** for the heights (scaled from a pedestrian beside the wall in 21; wall/sill proportions agree in 05)
- **East side**: 2-3-storey houses and compound walls of rougher, more weathered grey-honey stone, small
  barred windows with sheet-metal hoods, a pointed-arch doorway with a dark steel door; at "83 Armenian
  Orthodox Patriarchate Rd" (≈(116,-141)) a **wall covered by raised cement "pillow" pointing with incised
  reliefs (eagle, dove with olive branch, cross in roundel)** — the most distinctive surface on the stretch.
  **high** for the surface (05, 11). **[R21]** The position is not verified. (116,-141) is only 11's camera geotag, on the
  centre line, and the house number comes from a description that was not downloaded. In 05 the pillow walling runs
  along the east side from the camera to ~10 m short of the north tunnel, i.e. roughly **y -150 → -180**. 05 was taken
  south of the Tavern, since no Tavern canopy or banner shows ahead. North of the Tavern (21, left) the wall is plain
  rubble with flush pointing.
- **Armenian Tavern** (OSM node (124.1,-131.5), "79 Armenian Patriarchate Rd", east side): dark grey flat steel
  canopy ~1.2 m deep at ~3 m on **semicircular "wheel" brackets with radial spokes**, floodlights on the
  canopy edge, ceramic tile name panel "ARMENIAN TAVERN" with a saint figure, a vertical hanging banner
  "ARMENIAN TAVERN / RESTAURANT / מסעדת הטברנה הארמנית" on a black bracket at ~4-6 m, Armenian (red-blue-orange)
  and Russian flags, grey-green steel doors and a grille gate, planters. Closed state: steel doors shut, no
  goods outside. **high** (12, 13, 21)
- Overhead: 3-6 black cables crossing or running diagonally at 5-8 m; seasonal giant hanging lanterns
  (Dec 2017). Street lamps: anthracite inverted-L LED poles on the east kerb (05, 02). **high** **[R22]** In 05 the lamp on
  this stretch is an anthracite LED arm fixed to the east wall at ~6-7 m, not a kerb pole. The pole in 02 stands south
  of the south tunnel, outside P2.
- Vista: the dark low arch of the north tunnel closes the view at the south end. **high** (05, 13, 21)

### P3. Junction space at the head of St James St (y -165 to -185)
- West side opens into a small irregular space (7-34 m between footprints **[R4]**, was 11-35 m): Bulghourji restaurant (see L6; position **low**, **[R17]**),
  ceramic street-name plaque "ARMENIAN ORTHODOX PATRIARCHATE RD." on the building beside its door. St James St
  leaves eastwards at (113,-183). Commons descriptions of 2011 photos (16147901, 16149882, not downloaded) report a
  trilingual street sign and a carved relief of the spies carrying the grapes of Canaan at the corner of St James St
  and the road. **med** (OSM, 08, 19), **low** for the corner details.

### P4. Covered passage north (y -185 to -211) — OSM 44376249 (`layer -1`, `maxheight 2.9`, `sidewalk no`), under w1392907903
- A ~26 m long tunnel through w1392907903 (25.6 x 10.5 m footprint, long axis N-S). The north mouth is a **low
  arch, clear height ~2.9 m** (OSM maxheight; reads as a dark low opening in 05, 13, 21); the building above is
  **3 storeys (~11-12 m)** **[R7]** (was 3-4 storeys) of pale ashlar with round-arched windows (seen end-on from the south in 04, 39). **high** for
  existence and size (OSM + 04, 05, 13), **med** for the facade. **[R7]** 2.9 m is the OSM `maxheight` sign value. At the
  south mouth (04, scaled from a pedestrian standing in it) the arch is ~2.9 m wide with its crown at ~3.5 m.
- Inside: rendered/plastered walls in pinkish-grey, asphalt floor wall to wall (no pavement); shop window
  of the **Sandrouni Armenian ceramics shop** (see L7) in a segmental-headed opening with **dark teal steel-framed glazed doors,
  folding teal bar-grille outer leaves, a teal-painted moulded wooden cornice** and an Armenian inscription
  stone dated 1872 above it, lit at night by an oval bulkhead lamp. **high** for the shop front (10 + its
  geotag (108.7,-206.0) inside the passage; 43, 2014, another author, same geotag and the same 1872 stone).
  **[R8]** The two geotags are identical to 6 decimals (31.77477, 35.228691), so they were copied and do not confirm
  the position independently. The north passage is supported by elimination instead. The only other covered stretch,
  the south tunnel, has ashlar walls with grilled windows at shop height (04, 22, 39), whereas 10 and 43 show smooth
  plastered walls under a rendered vault. Location: **med-high**.

### P5. Armenian Patriarchate Rd along the St James convent wall (y -211 to -265) — OSM 44376240
The signature street of the sector. Looking south from the convent gate (03, 17, 30) the walker has the convent
wall on the left, parked cars and pines on the right and the pedimented arch building closing the vista.
- **East (left going south): one continuous convent wall ~53 m long** = w290678899 edges e18-e19 (x ≈ 112.5,
  y -212.8 → -236.4) then w612002272 edge e1 (x 111.8 → 109.8, y -236.4 → -265.4), facing west (272-274).
  **~11 m high** at the gate (scaled from the gate recess in 15), flat top with a thin coping, no cornice.
  (Review: 16 and 07 both put the wall at 4.4-4.6 x the doorway height, so ~11 m holds only if the doorway is
  ~2.3-2.5 m tall. There is no independent absolute scale at the gate. At the south end the wall top is level with
  the arch building's cornice in 01.)
  **high** for position (OSM + 03, 15, 17, 30 all show it on the east side looking south), **med** for height.
- Masonry: **very regular, pale grey-white limestone ashlar** (courses 0.30-0.40 m, blocks 0.4-0.9 m long,
  thin joints), cleaner and whiter than anywhere on the square; dark streaks only under windows. **high**
- Openings: irregular, sparse. Lower row at ~3-5 m: small square windows 0.5-0.8 m with square bar grilles;
  upper rows at ~6-10 m: larger windows 0.9 x 1.3 m with lozenge/diamond or scroll grilles, several of them
  **projecting iron cage boxes (~0.4 m deep) with flower pots**, and **every window has a small pent hood of
  sheet metal with a scalloped/pierced fringe** (the white-painted metal "lace" valance is a strong Armenian
  Quarter motif). Dark grey downpipes and bundles of black cables run down the wall. **high** (03, 07, 15, 16, 30)
- Street furniture on this side: pavement ~1.5-2.0 m of large pale slabs with a low kerb; **black steel bollards
  with a white band** at ~1.5 m; older **cylindrical white limestone bollards (~0.5 m, domed tops)**; in 2019
  **red-and-white striped steel posts with a hanging chain** in front of the gate (30); **black wrought-iron
  scroll brackets with a cross-shaped tip, each holding a small grey cylindrical lamp**, either side of the gate
  at ~3 m (07, 16, 30); a dark brown framed notice board (~1.8 x 1.0 m) on the wall north of the gate (15). **high**
- Ceramic street plaque **white tiles, black lettering, thin dark frame**, ~0.9 x 0.6 m, Hebrew / Arabic /
  "ARMENIAN ORTHODOX PATRIARCHATE Rd.", on the wall ~4 m north of the gate recess at ~3.5 m (03 crop, 30). **high**
- **West (right going south)**: no building line. A strip of **slab- and sett-paved parking** (cars parked nose-in or
  along the kerb, 03, 04, 17), a raised kerb, then the **Armenian garden / seminary grounds** behind a **dark green
  steel bar fence (~1.8 m) on a low stone wall**, with hedges and **big Aleppo/stone pines** overhanging the road,
  olive trees; a blue disabled-parking sign, no-parking discs, a yellow "reserved parking" plate and a triangular
  warning sign on grey poles. **high** (01, 03, 17, 14; OSM garden 1394066412, trees 14064312089-92)
- Carriageway: asphalt 4.5-5 m, painted white edge line in places; manhole covers. At the south mouth of the north
  tunnel (y ≈ -212) a small **square of rough grey setts with white limestone chamfered bollards** (15). **high**
  **[R10]** The square is on the **west** side of the road: the camera in 15 stands on it with the road and the
  convent wall beyond. The same chamfered bollards line the whole west parking strip as far as the south arch (17).
- Lamps: anthracite inverted-L LED poles on the west kerb (01, 17); the two scroll-bracket lamps at the gate. **high**

### P6. Covered passage south (y -265 to -293) — OSM 290669005 (`tunnel=yes`), under w1394456881
- North face (01, 03, 17, 20): a **neoclassical gate building straddling the road** (a tall arch storey + one upper floor): a big
  **semicircular arch ~5 m wide, crown ~5.5 m**, with a heavy moulded archivolt, plain imposts and a **carved
  keystone console**; above it a **triangular pediment** over three tall rectangular grilled windows (1F); to the
  right (west, w1394456882 north face, **6.6 m** **[R19]** (was ~7.5 m); a lower 1-storey block with a green door continues
  further west, 17 and the far right of 01) a 2-storey block with three grilled windows above, a small
  round-arched grilled window and a **grey door reached by an external stair of ~7 steps with a steel handrail**
  along the facade. Cornice ~11 m, pediment apex ~13 m (scaled from the 2.2 m door in 01). A red-and-white **boom
  barrier** at the arch mouth (2019, 17). **high** for form (4 photos), **med** for dimensions.
- A **low grey (lead/concrete) dome** rises behind the parapet, roughly over the passage: seen behind the pediment
  from the north (03) and above the south facade from the south (02). **med**
- Inside (22, 04, 06): ~28 m long (OSM), **plastered pointed barrel vault in 2-3 bays divided by ashlar
  transverse arches**, walls of ashlar to ~3 m with small **bellied iron window grilles**, a narrow round-arched
  doorway with dark door, iron lantern brackets, one pendant lantern per bay, an AC unit and a CCTV camera; a
  slab pavement ~1.2 m along the west side, asphalt road. **high**
- South face (02): 2 storeys, **three round-arched windows with white louvred shutter pairs** over a round arch
  with a hanging lamp, pale ashlar, a dark downpipe. **high** (one clear photo; orientation proved by 04/20/02
  sequence: the bougainvillea and the fenced wall flank the road south of the tunnel in both 02 and 20)
- **Vista south through the tunnel: the crenellated south city wall and the square Dormition bell tower beyond**
  (18, 20). Keep the tunnel axis open so this view works. **high**

### P7. Saint James Street and the lanes east of the road — OSM 26492729 (`Saint James Street`), Or HaHayim, Ararat, HaMalakh
- **Paved pedestrian lane 3-4 m wide** (OSM 3.2-4.5 m between footprints in the east half **[R13]** (was 3.4-6 m); photos 23, 24, 26-28
  ~3-3.5 m), walls 6-12 m, mostly blind: honey-to-grey rubble-faced ashlar, few small barred windows, a wooden
  or steel door here and there. **high**
- **Series of flying arches** (segmental/slightly pointed, one ring of voussoirs ~0.5 m deep, ~0.6-0.8 m thick)
  spanning wall to wall, springing at ~3-4 m, crown ~4.5-5.5 m, every ~4-8 m; some carry a lamp; dry plants on
  top. This is the image of the lane. **high** (24, 27, 28; 25/26 show the same type but their location is uncertain)
- Paving: **large smooth pale limestone slabs laid in courses across the lane** (OSM says `surface=sett`; the photos
  show slabs), worn glossy, with **round cast-iron
  manholes (~0.7 m)** and square grates on the centre line; no steps (OSM has none on 26492729), gentle grade.
  **high** (23, 24, 26, 27)
- **Galvanised/black tube handrails** fixed to the walls at ~0.9 m (one or both sides), grey electrical boxes,
  conduits. **high** (23, 24, 26, 27)
- The west end of St James St (x 113-155) is wider (13-30 m between footprints in OSM): it runs past the north
  wall of the convent (w290678899 edge e11, y ≈ -184) and the St Toros block; remains of the Crusader church of
  St Thomas (carved stones) are reported in the south wall near (125,-178) (Commons descriptions of 34126173,
  78612557). **med** **[R13]** The OSM gaps are not open space. Photos geotagged inside the "wide" part show a ~3-3.5 m lane
  walled on both sides with flying arches: 28 at (152,-176), 26 at (162,-170) and 24 at (172,-162), by three different
  authors. Model the lane as walled at ~3-3.5 m from x ≈ 150 eastwards; the walls are unmapped garden and courtyard
  walls. Only x 113-150 has no photo (OSM 9-15 m between the convent north face and w1392907910/w1550194751): **unverified**.
  The St Thomas remains rest on descriptions that were not downloaded: **unverified**.

---------------------------------------------------------------------------------------------------------------

## 2. Landmarks

Position checks (lesson from s00): every position below states how it was confirmed.

### L1. St James Convent street front: w290678899 (gate block) + w612002272 (Patriarchate Administration)
- **Position**: the whole east side of P5 (x ≈ 110-113, y -212.8 → -265.4). Confirmed by OSM geometry and by
  four photos taken looking south with the convent on the left and the pedimented south arch ahead (03, 15, 17,
  30), and one looking north from the south tunnel with the convent on the right (04, 39). **high**
- **Massing**: w290678899 is an irregular block 61 x 24 m (MRR) running from St James St (north face e11 at
  y ≈ -184) to y -236; w612002272 is 44 x 29 m (MRR) from y -236 to -281, its west face e1 (29 m) on the road and
  its edge e2 (7.2 m) forming the east wall of the south tunnel. Both read from the street as **one ~11-12 m
  high, flat-topped, 3-storey wall** without cornice or roof visible; thin stone coping, parapet line slightly
  stepped where the blocks change (15). **med** for height (scaled from the gate recess in 15 and the 1.7 m
  figure in 03)
- Street face: see P5 (pale grey-white regular ashlar, sparse grilled windows with scalloped sheet-metal hoods,
  projecting cage windows, downpipes and cable bundles). The **gate** is described in section 3.
- ~~North face of w290678899 (edge e17, 7.6 m, faces 2) closes the small sett square at the south mouth of the
  north tunnel. **med** (15)~~ **[R10]** Wrong. e17 (x 112.9-120.5, y -213) lies **east** of the road. It faces a 1.5 m gap
  against the tunnel building's south face (y -211.5) and a ~4 m light well (x 116-121), and it cannot be seen from the
  street. The sett square in 15 is on the west side of the road (see P5).

### L2. Saint James Cathedral, w265410575 (building=cathedral)
- **Footprint** 37 x 28 m (x 126.9-164.7, y -246.8 → -217.8), long axis E-W, entrance on the **west face** (OSM
  entrance node (127.6,-229.9)), reached from the convent gate by OSM footway 722675052 + building passage
  722675059 into a courtyard. **[R14]** The passage is ~16 m and L-shaped: 7 m east, 6.3 m south, then 2.4 m east (was
  "a ~12 m vaulted vestibule running SE"). Then 5.7 m of open footway (722675049) crosses a court only ~6 m wide
  (x 122-127.6, between w290678899 e1/e2 and the cathedral west face) to the west door. **high** (OSM)
- **Not visible from Armenian Patriarchate Rd**: none of the street photos looking along the convent wall (03,
  15, 17, 30) shows a dome above the ~11 m wall. Model it for rooftop/aerial views only. **high**
- Exterior massing: the 2021 view from the Citadel (33, author's caption "background: the Armenian Cathedral of
  St. James") shows in the background a **hemispherical stone dome on a short drum with a small lantern and
  cross, next to a slender pointed conical cap**, rising only ~3-6 m above the surrounding flat roofs. I could not
  pin the dome down by triangulation (a single distant photo), so treat dome shape and height (≈18-22 m above the
  courtyard) as **low**. **[R15]** Bearing check: solving the camera of 33 from the police block's two ends and the Dormition
  dome gives ≈(90,-35). The ray to the hemispherical dome (bearing ≈162°) crosses the cathedral footprint at x ≈ 155,
  y -232, so the identification fits to within ~2-3°. The slender conical cap to its left points at x ≈ 165-175,
  east of the cathedral footprint, so it is **not** part of the cathedral. Height is still **low**.
- **Courtyard / narthex (what a visitor sees through the gate)**: a vaulted porch (narthex) in front of the west
  door: pointed-arch lunette filled with a large **fresco of Christ in Glory / the apostles** in red-ochre and
  blue, a carved gilded Baroque wooden cartouche with the Holy Face and two angels over the door, door frame of
  white marble, dark panelled wooden door with a **quilted brown leather curtain**, flanking pointed-arch windows
  with wooden lattice set in panels of **blue/turquoise Kütahya-style tiles with cross medallions**; a pendant
  lantern. **high** (31, 29; 2018 and 2024)
- Courtyard walls carry **khachkars**: tall carved cross-stones of red-brown tufa and grey basalt, a red tufa relief
  of a bishop, propped against pale ashlar under a window with a white bar grille. OSM wayside_shrine nodes at
  (123.5,-236.5) and (127.1,-221.0) mark them, the khachkar photo 41 is geotagged (124,-228). **high** for the
  objects, **med** for exact spots.

### L3. Christ Church compound: w126755060 (church), w126783156 (Guest House), w1394456869 (street block)
- **Christ Church** (Anglican, 1849): footprint 27.5 x 19 m (x 144.8-172.3, y -76 → -57), entrance on the west
  face (OSM entrance node (144.9,-66.2)); it stands **~25-30 m east of the road behind the Guest House**, seen from
  the street only through the gate. Pale cream limestone, **neo-Gothic**: a **moderately pitched (~30-35°) gabled west front** **[R23]** (was "steep") with a large
  **three-light lancet window with tracery**, a cross in a roundel in the gable, **one projecting porch at the south end
  of the west front with a low hipped grey roof, a pointed-arch doorway with a dark wooden door and a row of small
  windows** **[R23]** (was a gabled porch plus a separate small side porch: 38 and 006 show one porch). The main door is
  therefore at the south end of the west front, not at the mid-face OSM entrance node. A 3-storey mission
  house with brown louvred shutters adjoins on the north; a small **stone bell-cote (gabled, open arch with bell)**
  over a white door in the courtyard. **high** (38, 006, 137)
- **Guest House** w126783156: 26.5 x 10.3 m, long axis N-S, 2 storeys (~8 m to the eaves), **hipped red clay-tile
  roof** (OSM roof:shape=hipped, roof:material=roof_tiles), a deep **arcaded loggia on square piers with iron
  balustrades along its WEST side** **[R1]** (was "east (courtyard) side"). The loggia looks down onto the flat roof terrace
  of the street block w1394456869 and across to the road. White AC units. Its roof is what one sees above the street block.
  **high** (006, 33 + OSM tags). No solar panels on this roof **[R2]**.
- **Street block** w1394456869 (x 112-122, y -49 → -72, faces 268 onto the road): one ~5 m storey with roof
  terraces; post office (OSM node "57 Armenian Patriarchate Rd"), Christ Church café awning, souvenir shop. See P1.
  **high**. **[R3]** Its main west face is at x ≈ 117 (y -49.5 → -66.5). The south 5.5 m projects to x 112.3, and the café
  entrance is in that projection's north face (33).
- Trees in the compound (OSM trees (149,-62), (147.8,-54.5), (153.5,-75); photos 006, 38, 137): tall pines,
  deciduous ash/acacia-type trees and clipped evergreen shrubs; their crowns show over the street block.

### L4. Kishle / police station north block, w290669980 (inside the OSM police area 1084488109)
- North face e5 (24.2 m, faces 356) closes the forecourt at y ≈ -91; **2 storeys + hipped red-tile roof**, pale
  honey ashlar, **seven round-arched upper windows**, a **round-arched vehicle gate** ~10 m from its west end (OSM
  gate node (102.8,-89.4) and the service tunnel 1085709199 pass through it there), blue police barrier panels.
  **high** (33: the arch is at 41 % of the facade from the west end, matching the OSM gate/tunnel at x ≈ 101-103)
  **[R16]** Storeys, the seven windows and the arch all rest on one photo (33), so **med**. 41 % of 24.2 m puts the arch
  ~9-10 m from the west end, while the OSM gate and tunnel are 12.2-12.7 m from it. They agree only to within ~3 m.
- Its east end (x ≈ 114-116) and the row w1394899938, w1394458560, w1394458561 form the blind **~6.5-7.5 m** **[R5]** (was 8-10 m) west wall of
  the narrow stretch (P2) with the mesh security fence on top. **high** (05, 13, 21)
- Turquoise ceramic direction tiles "WESTERN WALL ← / THE JEWISH QUARTER" (arrow, wall icon, Star of David) on a
  wall at the forecourt (44, geotag (102,-82), described as "near police station"). **med** (2014 photo)

### L5. Armenian Tavern (OSM restaurant node (124.1,-131.5), "79 Armenian Patriarchate Rd"), east side of P2
- Confirmed on the **east** side by OSM and by 13 and 21 (both looking south, tunnel ahead, Tavern on the left).
  Details in P2. **high**

### L6. Bulghourji restaurant (OSM node "Bulghorgij restaurant" (108.5,-175.9)), west side of the junction P3
- Facade (08 2023, 19 2016): pale grey weathered ashlar; **round-arched doorway ~1.25 x 2.8 m** **[R17]** (was ~1.3 x 2.5 m; 19: door 243 x 550 px, plaque 176 px) (scaled from the 0.9 m tile plaque, itself an assumed size) with a carved
  shell/cartouche keystone, **studded steel double doors** with flat-bar panels (pale ochre/beige in 2016, dark
  brown-black in 2023); flanking **round-arched windows with wrought-iron scroll grilles** (orange-gold in 2016,
  black in 2023) and solid beige shutters; above the door a **marble inscription panel** (Armenian, dated 18x3)
  and an **oval oculus with a scroll grille**; LED floodlight; dark brown sign "BULGHOURJI / Armenian Bar
  Restaurant"; two small arched cellar vents at the foot; the white ceramic street plaque left of the door.
  **high** for the facade, **med** for position (OSM node only; the two photos' own geotags disagree)
  **[R17]** Downgraded to **low**. On the plaque scale, 19 shows the door and two windows across ≥6 m of facade. The OSM
  node lies in w1545817482, whose faces are only 4.0 m (east) and 4.9 m (north), so the facade cannot be on that
  building as mapped. The geotags of 08, 09, 19 and 36 scatter over 15 m. The side of the road is **unverified**.

### L7. Armenian ceramics: Sandrouni, inside the north covered passage (w1392907903)
- Two shop openings in the plastered passage wall: a round-arched one and a segmental-headed one, both with
  **dark teal steel-framed glazed doors and folding teal bar-grille outer leaves**, a teal moulded cornice, Armenian
  inscription stone dated 1872, oval bulkhead lamp; a **navy sign "SANDROUNI" with a ceramic rosette and a yellow
  arrow**, a teal arrow painted on the wall. Behind the glass: painted Armenian pottery (white ground, cobalt,
  turquoise, red floral). Closed state: grille leaves shut, lights off. **high** for being in the passage (10 and
  43, different authors 2014/2018, both geotagged (108.7-109, -206), both with asphalt floor and plastered
  passage walls), **low** for which wall (east or west). **[R8]** The geotags are identical and copied, so they are not
  independent. The passage is supported by elimination against the ashlar-walled south tunnel: **med-high**.
- Ceramic culture shows elsewhere as the tile street plaques and the tile name panel of the Tavern.

### L8. North tunnel building, w1392907903 (25.6 x 10.5 m) — see P4
- Seen from the south (04, 39): a tall narrow block, **3 storeys, ~11-12 m** **[R7]** (was ~4 storeys, ~14-15 m). In 04 a
  pedestrian at the south mouth gives the top at ~11.4 m and storeys of ~4.2 / 3.7 / 3.5 m; 39 shows the same 3 storeys
  plus the steel frame on the roof. Pale ashlar, two round-arched windows
  in the top storey, one in the middle, a low arch at the base (~2.9 m wide, crown ~3.5 m); from the north (05, 13, 21) a low dark arch under
  a plainer facade with small windows and a steel frame on the roof. **high** for position (OSM tunnel way + 4
  photos), **med** for the facades (distant views only).

### L9. South arch building, w1394456881 (roof over the road, 28 x 6.4 m) + w1394456882 (west, 25.5 x 10.8 m) — see P6
- Position: OSM tunnel way 290669005 (y -265 → -293) and photos from both ends (01, 03, 17 from the north; 02 from
  the south; 04, 06, 22, 39 inside). **high**

### L10. Armenian Theological Seminary and the khachkar memorial (OSM college area 290670297, west of the road)
- Behind the green fence on the west side of P5: a modern 2-storey pale ashlar building with a **wavy parapet**,
  tall round-arched windows, raised Armenian lettering and a bronze medallion; in front, on a lawn with olive and
  ash trees, a **memorial row of ~7 tall khachkars on a stone plinth** with small yellow plaques. **med** (14,
  geotag (106,-225); OSM area)

### L11. Gulbenkian Library (inside the convent, not on the public street)
- 2-storey rectangular block of honey ashlar with a plain cornice, **five round-arched grilled windows upstairs**,
  rectangular windows with fan grilles below, a central dark grey steel double door under a marble inscription
  panel, reached by a broad flight of ~5 steps from a paved court; **two red tufa khachkar sculptures** flank the
  steps. **high** for the look (35, 2024), **low** for position: only that photo's geotag (142,-255), i.e. a court
  just south of the cathedral's south wall (y -247); not cross-checked.

### L12. St Toros church (OSM node (146.2,-203.3), building w1394467470, 14.8 x 14.4 m) — inside the convent north
of the cathedral; not visible from any street. OSM only. **med** (position), no exterior photo.

---------------------------------------------------------------------------------------------------------------

## 3. The gate of the sector: the St James Convent gate

The sector has **no city gate** of its own: the walker enters from Jaffa Gate (sector s00) and the road leaves the
sector southwards towards Zion Gate (s02). The defining gate is the **entrance of the St James (Armenian) Convent**
on the east side of Armenian Patriarchate Rd; the two road tunnels (P4, P6) act as secondary gates.

- **Position**: in the west face of w290678899 at **(112.5, -223.4)**, where OSM footway 722675052 leaves the road
  ((107,-222.8) → (112.4,-223.2)) and becomes the building passage 722675059 into the convent. Cross-checked: 03
  (taken looking south from just north of it: gate in the left wall roughly midway between the north tunnel exit
  and the pedimented south arch), 15 and 30 (from the north-west, south arch in the background), 07 and 16
  (frontal). The OSM ATM node (103.9,-222.5) is opposite it on the west kerb. **high** **[R9]** It is not "midway". Per OSM
  the gate is **12 m south of the north tunnel's south mouth** (y -211.1) and **42 m north of the south arch's north face**
  (y -265), about a quarter of the way along. 03 could not show this, because the north tunnel is behind its camera.
  The position itself stands.
- **Form** (16 frontal, 07, 30): a tall **pointed (slightly horseshoe) arched recess** set into the flat wall:
  outer moulded archivolt of 2-3 rolls ~5.5-6 m wide, **apex ~7 m**; the recess is ~1 m deep and its back is a
  **plain ashlar half-vault (conch)**; at the springing (~4 m) a band of **carved sawtooth / small muqarnas
  corbelling** runs across the back of the recess and returns onto the jambs; small carved capitals at the
  springing. **high** for form, **med** for dimensions (scaled from the 1.75 m man in 03 and the niche/door ratios
  in 16).
- **Doorway**: in the back wall, centred, **~1.7 m wide x ~2.5 m to the crown**, a low pointed/four-centred arch
  with a plain moulded frame and a heavy lintel band; the door leaves stand open by day (07: a dark vaulted
  vestibule with a floor uplight beyond). Above the door: **white enamel sign with dark blue lettering**, three
  lines: Armenian / Arabic, Armenian, **"COUVENT ARMENIEN St JACQUES"** (~1.6 x 0.5 m). In the tympanum above it a
  rectangular stone **inscription panel** (text illegible in the photos). **high** for elements, **low** for text.
- **Flanking niches**: right of the door a **blind niche ~0.8 x 2.2 m with a carved trefoil/muqarnas hood on
  small colonnettes**; left a narrower niche with a carved cross on a colonnette. Small incised marks (pilgrim
  crosses) on the recess stones. **high** (16, 30, 03)
- **Above the gate**: a **projecting iron cage window (~1.6 m wide x ~1.9 m box, ~2.6 m with canopy and fringe, ~0.4 m deep** **[R18]** (was ~1.2 x 1.6 m; 16, on the same doorway scale)**) with lozenge-and-scroll
  grille and a scalloped tin canopy and base fringe**, flanked by two small hooded windows with diamond grilles.
  **high** (07, 16)
- **Fittings**: two black scroll brackets with cross-shaped tips holding small grey cylindrical lamps at ~3 m on
  either side; CCTV cameras at the springing; black cable bundles down the right edge. **high**
- **Threshold / plaza outside**: the pavement widens to ~2.5 m in front of the recess and is paved with **polished
  cream and pink-red limestone slabs**; a linear steel drain grate along the kerb; two black steel bollards with a
  white band (2026) or two red-and-white posts with a chain (2019) flank the opening; across the 4.5-5 m asphalt
  road the parking strip, the ATM and the green-fenced garden with pines. **high** (07, 16, 30, 03)
- **Inside**: a vaulted vestibule then a ~16 m L-shaped passage (OSM 722675059: 7 m E, 6.3 m S, 2.4 m E) **[R14]** (was ~12 m) turning south-east into the cathedral
  courtyard (L2), where the narthex fresco and khachkars are. Model as a dark vaulted opening with a lit floor;
  the courtyard can be a closed set. **med**

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Furniture
- **Bollards**: (a) black steel tubes **~0.6-0.7 m** **[R6]** (was ~0.9 m) x 0.11 m with one white reflective band near the top, 1.5-2 m apart,
  along the east kerb of the road from the Tavern to the south tunnel and along the convent wall (02, 03, 05, 13,
  30); (b) older **white limestone cylinders ~0.5-0.6 m with domed tops** along the convent pavement (15, 30);
  (c) **white limestone square bollards with chamfered/pyramidal tops** on the sett square south of the north tunnel
  (15), and the same type along the whole west parking strip of P5 as far as the south arch (17) **[R10]**; (d) red-and-white striped steel posts with chains at the convent gate (2019, 16, 30). **high**
- **Street lamps**: anthracite square-section poles ~6-7 m with a flat LED head on a short arm (inverted L), on
  the kerb lines (01, 02, 05); in the tunnels **pendant lanterns** (white enamel shade or black iron lantern on a
  rod) and wall brackets (04, 22, 39); at the convent gate the two scroll-bracket lamps. **high**
- Utility: grey electrical cabinets and meter boxes at wall foot (15, 25), dark grey and white downpipes, many
  black cables in bundles on facades and a few spanning the road at 6-8 m, CCTV cameras at gates and the
  junction (36), AC units in the tunnels. **high**
- Parked cars (white Hyundai i30, Dacia Duster, taxis) along the west side of P5 and south of the south tunnel;
  the yellow-and-green **"Kotel train" road train** uses the road (39, 2024). **high** (for a populated version only)

Signage
- **Ceramic street plaques** (Armenian ceramic tradition): white glazed tiles, black lettering, thin green-leaf /
  yellow ornamental border (08/09 at Bulghourji, **5 x 3 tiles** **[R17]** (was 3 x 6), assumed ~0.9 x 0.5 m) or thin dark frame (03/30 at the gate);
  Hebrew "רחוב הפטריארכיה הארמנית" / Arabic "طريق بطريركية الأرمن الأرثوذكس" / English **"ARMENIAN ORTHODOX
  PATRIARCHATE RD."**, at ~3-3.5 m. **high**
- **Turquoise ceramic direction tiles** "WESTERN WALL / THE JEWISH QUARTER" with a dark-blue arrow, a Western Wall
  icon and a Star of David at the police forecourt (44); **"WELCOME TO THE JEWISH QUARTER / ברוכים הבאים לרובע
  היהודי"** blue-and-white tile plaque with a menorah where St James St reaches Or HaHayim (45, geotag (220,-166)).
  **med** (2014-2015 photos)
- A green/black municipal **wayfinding map panel** on a wall in the lanes ("The Temple Mount", "Zion Gate"; 25).
  **med**
- **Armenian identity signs**: Armenian tricolour flags (Tavern, 12); printed banners for the Genocide
  remembrance with the purple forget-me-not logo, "I REMEMBER AND DEMAND" in Armenian / English / Arabic / Hebrew,
  pinned to walls at the St James St junction (36, 2023; the banner reads "Armenian Genocide Centennial", i.e. a 2015
  banner still up in 2023; its spot rests on 36's geotag alone, so **unverified**); Armenian-script inscription stones over doorways (08, 10,
  43); "COUVENT ARMENIEN St JACQUES" gate sign (16). **high**
- Traffic signs on grey poles: blue/red no-parking discs with a white tow-truck plate, blue disabled-parking
  square with a number plate, yellow "reserved parking" plate, red triangle warning, a yellow
  plate with a red triangle and "האט / SLOW" south of the south tunnel (01, 03, 17, 20). **high**
- Business signs (few): "ARMENIAN TAVERN" tile panel + vertical banner; "BULGHOURJI" dark board; navy
  "SANDROUNI" sign with a yellow arrow; "CHRIST CHURCH" scalloped awning; "BIBLES STAMPS ANOINTING OIL GIFTS"
  awning; red Israel Post parcel locker. **high**
- Window hardware worth a reusable asset: (1) **sheet-metal pent hoods with a scalloped/pierced fringe**, (2)
  **bellied (curved-bar) window grilles**, painted green or grey (06, 37), (3) **projecting iron cage windows**
  with flower pots (15, 16, 30). Seasonal: lit wire stars and bells in windows at Christmas (37). **high**

Vegetation
- **Big pines (Aleppo / stone pine) and an olive** on the west side of P5, crowns overhanging the road and the
  parked cars (01, 03, 17, 30; OSM trees at (93.5,-235.7), (97.6,-244.1), (92.1,-259.5), (105.0,-261.4)). **high**
- **Bougainvillea (magenta)** cascading over the ~3-4 m west boundary wall just south of the south tunnel
  (02, 20, visible through the arch in 30). **high**
- Seminary garden west of the road: lawn, olive, ash-type deciduous trees, a tall cypress (14). **med**
- Christ Church compound: tall pines, deciduous trees and clipped shrubs whose crowns show over the street block
  at y -49..-72 (006, 33, 38). **high**
- Hedges and climbing plants over the low garden wall at the south arch (01). **high**
- **Wall plants**: small ferns/caper tufts in the joints of the rougher east-side walls of the narrow stretch (05)
  and dry grass on parapets (13); dry climbers draped over the flying arches of St James St (24, 28). The convent
  wall itself is clean. **high**
- No trees inside the narrow stretch (P2) or the tunnels. OSM tree nodes further east (e.g. (139.6,-173.7),
  (161.3,-156.8), (175.7,-148.5)) stand in courtyards behind walls along St James St. **med**

---------------------------------------------------------------------------------------------------------------

## 5. Terrain

SRTM-derived terrarium tiles (`data/raw/terrain/15_*.png`, ~30 m effective resolution, includes some building
height, ±2-3 m noise) sampled along the OSM centre lines:

| place | x, y | elev (m), SRTM DSM (original) | **[R12]** ground model `data/terrain_street.json` (OS 1865) |
|---|---|---|---|
| Armenian Patriarchate Rd at the Christ Church gate | (111,-52) | ~776 | **772.8** |
| police forecourt | (116,-89) | ~780 | **775.2** (OS 1865 spots 774.5 at (119,-78), 774.8 at (104,-88)) |
| narrow stretch (Tavern) | (119,-129) | ~780 | **776.8 (actual local high point)** |
| St James St junction / north tunnel | (112,-188) | ~781.5 (local high point) | **775.7** (OS 1865 bench mark 775.7 at (132,-185)) |
| convent gate | (106,-228) | ~780 | **776.1** (OS 1865 spot 775.4 at (107,-249)) |
| south tunnel | (106,-268..-288) | ~777-779 | **775.2** |
| sector edge | (107,-300) | — | **775.0** |
| St James St, middle / east end | (158,-165) / (216,-154) | ~782.5 / ~780 | **776.9 / 773.1** (OS 1865 772.97 at (214,-151)) |
| HaMalakh south end | (233,-259) | ~775 | **771.6** (OS 1865 769.9-770.2 nearby) |
| road at Zion Gate (outside the sector) | (177,-407) | ~771 | **770.1** |

**[R12]** The terrarium tiles are a surface model that includes roofs. In the street they read 3-6 m too high, and they
put the high point on the north tunnel building. Use the project's ground model (OS 1865 spot heights + GP, fit rms
0.2 m, leave-one-out rms 2.2 m) and the OS 1865 spot heights quoted in the right-hand column.

- **Armenian Patriarchate Rd climbs gently south from the square**: ~+4-5 m from the Christ Church gate to the St
  James St junction over ~140 m (≈3 %), steepest between the Christ Church gate and the police forecourt.
  **[R12]** Corrected profile: **+4 m from the Christ Church gate (772.7) to the Tavern (776.8)** over ~85 m. The climb is
  ~5-6 % up to the forecourt and ~4 % from there to the Tavern. **After the Tavern the road is nearly level (±1 m)** all
  the way to the sector edge: junction 775.7, convent gate 776.1, south tunnel 775.2, y -300 775.0. The
  moat-side footway at the north edge needs two short flights to keep up with it: OSM steps 1084488116
  (`step_count 14`, (109.2,-35.7) → (109.2,-41.2), ≈2.2 m rise southwards, handrail, separate ramp) just north of
  the sector edge and 1084488117 ((108.6,-49.0) → (108.8,-45.9), handrail). **med** (SRTM + OSM steps; photos 05 and
  21 show the narrow stretch rising gently towards the north tunnel). **[R12]** The ground model does not support a rise
  towards the tunnel: the road falls ~1 m from the Tavern to the junction. The photo reading is **unverified**.
- From the junction the road is **nearly level past the convent gate and falls ~2-3 m towards the south tunnel**;
  south of the sector it keeps falling to ~771 m at Zion Gate. **low-med** (SRTM only). **[R12]** It falls only ~1 m to the
  south tunnel. The real descent (~775 → ~770) begins south of the sector, at y < -360, where the road turns east to Zion Gate.
- **No steps on Armenian Patriarchate Rd or St James St** (OSM has none; no steps in any photo). Cars use the road
  through both tunnels (maxheight 2.9 m in the north tunnel). **high**
- **St James St** runs almost level then falls ~2-3 m to its east end at Or HaHayim. **[R12]** It rises ~1 m to x ≈ 155
  (776.9), then falls **~4 m** to 773.1 at the east end (OS 1865: 775.7 at (132,-185), 777.2 at (164,-183), 773.0 at (214,-151)) (wall handrails in 23, 24, 26,
  27 mark the grade); the lanes beyond drop towards the Jewish Quarter: **Ararat steps** 44376214 ((228.3,-125.5) →
  (225.4,-133.0), 8 m, sett) and 44376246 (6.8 m, layer -1, inside the Ararat tunnel 44376205); **Biqqur Holim**
  steps 616359702 with a ramp at the NE corner of the sector. **med**
- Platforms and level changes visible in photos: the **external stair of ~7 steps (~1.2 m)** up to the door of
  w1394456882 beside the south arch (01); the **broad 5-step flight (~0.8 m)** up to the Gulbenkian Library door
  (35); ~~the west side of the road south of the south tunnel is bounded by a **3-4 m retaining/boundary wall** with a
  mesh fence (and bougainvillea) on top, i.e. the ground to the west is higher there (02, 18, 20). **med**~~
  **[R11]** Sides corrected. The **3-4 m+ retaining wall with the ~2 m mesh security fence and higher ground behind is on the
  EAST side**. It is w290668993's west face and then OSM barrier=wall 1056503911 (x ≈ 111-114, y -308 → -338), with trees
  and a building standing above its top. The **bougainvillea hangs over the WEST wall** (w290669003 / private garden
  1546332714). Evidence: in 20 (looking S) the mesh-fenced wall is on the left and the bougainvillea on the right; in 02
  (looking N) the bougainvillea is on the left and the mesh fence on the right; in 18 (1997, looking S) the rubble
  retaining wall with a railing and trees above it is on the left. **med** (this stretch is just south of the sector edge).
- The garden/seminary ground west of P5 is roughly at road level (low wall ~0.6 m + fence, 01, 17). **med**

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make this sector read as itself)

1. **The convent wall of P5** (w290678899 e18-e19 + w612002272 e1, x ≈ 110-113, y -212 → -265): one ~11-12 m,
   flat-topped wall of very regular pale grey-white ashlar, sparse small grilled windows with **scalloped tin hoods**,
   a few **projecting iron cage windows**, downpipes and cable bundles. (P5, L1)
2. **St James Convent gate at (112.5,-223.4)**: ~6 m wide x ~7 m pointed recess with conch and sawtooth/muqarnas
   band, small ~1.7 x 2.5 m pointed doorway with the white "COUVENT ARMENIEN St JACQUES" sign, flanking carved niches,
   cage window above, scroll-bracket lamps, polished pink/cream threshold. (3)
3. **South arch building over the road (y -265 → -293)**: pedimented north face with a 5 m semicircular moulded arch
   and keystone, west block with external stair, low dome behind; 28 m plastered pointed barrel vault with transverse
   arches inside; south face with three white-shuttered arched windows. (P6, L9)
4. **North covered passage (y -185 → -211)**: low (2.9 m maxheight, crown ~3.5 m) arch under a tall narrow **3-storey (~11-12 m)** **[R7]** (was 4-storey) block, 26 m plastered
   tunnel with the **teal Sandrouni ceramics shop fronts** and navy "SANDROUNI" sign. (P4, L7, L8)
5. **Correct widths**: 12-13 m at Christ Church, pinching to **~8 m beside the projecting café block (y -67 → -72.5)**,
   **4.0-5.9 m in the narrow stretch (y -90 → -170)**, convent wall to garden edge **~9-11 m** in P5 **[R3, R4, R20]**
   (was 10-13 / 4.7-5.8 / 10-15 m); asphalt carriageway with pale slab pavement and flush kerbs, sett paving only
   north of y ≈ -90, on the small square at y ≈ -212 and on the west parking strip. St James St is a ~3-3.5 m walled
   lane from x ≈ 150 eastwards **[R13]**. (0, P1, P2, P5, P7)
6. **Blind ~6.5-7.5 m west wall of the narrow stretch** **[R5]** (was 8-10 m) (Kishle/police row) with arched shuttered windows (sills ~2.5-3 m) and a
   **2 m mesh security fence on its parapet**; rougher, plant-tufted east houses opposite. (P2, L4)
7. **Black steel bollards (~0.6-0.7 m) with a white band** **[R6]** lining the east kerb from the Tavern to the south tunnel, plus white
   limestone bollards at the convent and on the sett square. (4)
8. **West side of P5**: sett parking strip, dark green bar fence on a low wall, **big pines overhanging the road**,
   seminary building with khachkar memorial behind. (P5, L10, 4)
9. **Kishle forecourt**: ~20 x 15 m sett plaza closed by the 2-storey hipped-roof police block with seven arched
   windows and an arched vehicle gate. (P1, L4)
10. **Christ Church frontage (y -46 → -72)**: white steel gate with "CHRIST CHURCH GUEST HOUSE" letters, 1-storey street
    block with café awning, post office and red parcel locker; its south 5.5 m projects ~5 m into the street, with the café
    entrance in the projection's north face **[R3]**. Behind: the hipped red-tile Guest House roof, with its arcaded loggia facing
    WEST over the street block's roof terrace **[R1]**, and tree crowns;
    Gothic church visible through the gate only. (P1, L3)
11. **St James St**: 3-3.5 m slab-paved lane between tall blind walls with a **series of flying arches**, wall handrails,
    manholes on the centre line; Jewish Quarter welcome plaque at its east end. (P7)
12. **Ceramic signage**: white-tile trilingual "ARMENIAN ORTHODOX PATRIARCHATE RD." plaques (at Bulghourji and at the
    gate), turquoise direction tiles at the forecourt, Tavern tile panel. (4)
13. **Armenian Tavern and Bulghourji fronts** (closed): wheel-bracket steel canopy, vertical banner and flags; arched
    studded doors with scroll-grilled arched windows, inscription panel and oval oculus. (P2, L5, L6)
14. **Vista discipline**: the north tunnel closes the view down the narrow stretch; the pedimented south arch closes
    the view down P5; through the south tunnel the crenellated south wall and the Dormition bell tower must be
    visible; bougainvillea over the west wall south of it. (P2, P5, P6)
15. **Terrain**: ~+4 m climb (5-6 % below the forecourt, ~4 % above it) from the Christ Church gate to the Tavern, then
    nearly level (±1 m) to the sector edge, with no steps. Use `data/terrain_street.json`, not the SRTM values **[R12]**
    (was "gentle 3 % climb to the St James St junction, slight fall to the south tunnel"); Armenian identity dressing (tricolour flags, Genocide-remembrance banners at the junction, Armenian
    inscription stones over doors). (5, 4)

---------------------------------------------------------------------------------------------------------------

## Photo key

Project set: **006** = `data/photos/006_146551207.jpg` (2024, from Phasael looking SE onto the Christ Church
compound); **137** = `data/photos/137_94943919.jpg` (2019, Christ Church courtyard bell-cote).

Downloaded set `data/photos_ref/s01_armenian/NN_<pageid>.jpg` (1280 px Commons thumbnails; page URL, author,
licence, date and lat/lon where geotagged in `index.json`). "APR" = Armenian Patriarchate Rd.

| # | date | author | licence | subject |
|---|---|---|---|---|
| 01 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | APR looking S at the pedimented north face of the south arch |
| 02 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | south face of the south arch, looking N |
| 03 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | APR at the convent gate looking S |
| 04 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | inside the south tunnel looking N |
| 05 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | narrow stretch looking S (cement relief wall left) |
| 06 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | bellied window grille inside the south tunnel |
| 07 | 2026-06-30 | Yair-haklai | CC BY-SA 4.0 | convent gate frontal |
| 08 | 2023-01-26 | israel zeller | CC BY 2.5 | Bulghourji facade + street plaque |
| 09 | 2023-01-26 | israel zeller | CC BY 2.5 | APR ceramic street plaque |
| 10 | 2018-11-06 | Beko | CC BY-SA 4.0 | Sandrouni shop front in the north passage |
| 11 | 2018-11-07 | Beko | CC BY-SA 4.0 | cement relief wall, 83 APR |
| 12 | 2017-05-28 | Djampa | CC BY-SA 4.0 | Armenian Tavern canopy, flags |
| 13 | 2018-11-07 | Beko | CC BY-SA 4.0 | narrow stretch at the Tavern looking S |
| 14 | 2017-05-28 | Djampa | CC BY-SA 4.0 | seminary + khachkar memorial |
| 15 | 2019-04-21 | Bahnfrend | CC BY-SA 4.0 | convent wall from the NW, sett square |
| 16 | 2019-04-21 | Bahnfrend | CC BY-SA 4.0 | convent gate frontal |
| 17 | 2019-04-21 | Bahnfrend | CC BY-SA 4.0 | from the convent gate looking S to the south arch |
| 18 | 1997 | israel zeller | CC BY 2.5 | from the south tunnel looking S (film; used only for the vista) |
| 19 | 2016-10-05 | Morany84 | CC BY-SA 4.0 | Bulghourji facade (2016 colours) |
| 20 | 2019-10-11 | Levi Clancy | CC0 | through the south tunnel looking S |
| 21 | 2017-12-19 | Laliv gal | CC BY-SA 4.0 | narrow stretch looking S (Dec 2017) |
| 22 | 2012-10-11 | Sahar853 | CC BY-SA 3.0 | inside the south tunnel (vault bays) |
| 23 | 2015-10-21 | Ludvig14 | CC BY-SA 4.0 | St James St east part |
| 24 | 2015-10-21 | Ludvig14 | CC BY-SA 4.0 | St James St flying arches |
| 25 | 2026-06-07 | שלמה רודד | CC BY 2.5 | lane with flying arches + wayfinding panel (captioned "St. Mark's Street"; location uncertain) |
| 26 | 2026-06-07 | unknown (PikiWiki) | CC BY 2.5 | lane with flying arches (same caption; location uncertain) |
| 27 | 2017-11-18 | דוידי ורדי | CC BY 2.5 | St James St arch |
| 28 | 2016-12-25 | Morany84 | CC BY-SA 4.0 | St James St, series of arches |
| 29 | 2024-07-26 | Oren Rozen | CC BY-SA 4.0 | cathedral portal cartouche |
| 30 | 2019-08-21 | israel zeller | CC BY 2.5 | convent gate and wall from the N |
| 31 | 2018-11-06 | Beko | CC BY-SA 4.0 | cathedral narthex portal |
| 32 | 2024-06 | unknown (PikiWiki) | CC BY 2.5 | Finn Building panel, Christ Church compound (not used) |
| 33 | 2021-10-23 | Bukvoed | CC BY 4.0 | from the Citadel looking SE: Christ Church cmpd, Kishle forecourt, cathedral dome far |
| 34 | 2019-10-11 | Levi Clancy | CC0 | APR at the Christ Church frontage |
| 35 | 2024-07-26 | Oren Rozen | CC BY-SA 4.0 | Gulbenkian Library |
| 36 | 2023-01-26 | israel zeller | CC BY 2.5 | Genocide-remembrance banner at the junction |
| 37 | 2023-01-26 | israel zeller | CC BY 2.5 | bellied green grilles, Christmas stars |
| 38 | 2019-04-21 | Bahnfrend | CC BY-SA 4.0 | Christ Church west front |
| 39 | 2024-06 | שלמה רודד | CC BY 2.5 | south tunnel looking N, "Kotel train" |
| 40 | 2024-07-26 | Oren Rozen | CC BY-SA 4.0 | cathedral interior (not used) |
| 41 | 2023-01-26 | israel zeller | CC BY 2.5 | khachkars in the cathedral courtyard |
| 42 | 2023-01-26 | israel zeller | CC BY 2.5 | tufa memorial south of the sector (not used) |
| 43 | 2014-05-05 | Pandukht | CC BY-SA 4.0 | Sandrouni shop fronts in the north passage |
| 44 | 2014-05-31 | Djampa | CC BY-SA 4.0 | turquoise direction tiles near the police station |
| 45 | 2015-12-07 | Morany84 | CC BY-SA 4.0 | "Welcome to the Jewish Quarter" plaque |

Gaps worth a later pass: no frontal photo of the north tunnel's north facade or of the St James St junction from
2015+; no photo that fixes the cathedral dome height; Gulbenkian Library position rests on one geotag; Sandrouni's
wall side (E/W) in the passage is unknown.

---------------------------------------------------------------------------------------------------------------

## Review

Independent review, 2026-10-19. Method:
- Looked up every cited OSM id in `data/osm_local.json`: edge lengths, the side of the road and which way each facade faces.
- Re-ran the width measurement myself: perpendicular rays from the OSM centre lines to the nearest footprint or wall, every 4 m.
- Opened all 45 downloaded photos and project photos 006 and 137. Measured scales in pixels on crops, using pedestrians,
  a Hyundai i30 (1.48 m tall), doorways, bollards and the OSM edge lengths.
- Checked the terrain against the project's OS 1865 ground model `data/terrain_street.json`.

Each correction is tagged **[Rn]** in the body. The old value is kept there as "(was ...)" or struck through.

### Corrections

| # | where | what changed | evidence |
|---|---|---|---|
| R1 | L3, checklist 10 | The Guest House's **arcaded loggia is on its WEST side**, overlooking the street block's flat roof terrace and the road. It is not on the east (courtyard) side. | 006 (from Phasael, NW of the building): the loggia is on the long face seen from the NW, i.e. the west face, with the street block's roof terrace and barrel hump directly in front of it. 33 (from the Citadel): the same loggia faces the camera above the café roof. Two photos with known viewpoints + OSM (the Guest House at x 121.6-132.8 sits directly behind the street block at x 112-122). |
| R2 | P1, L3 | Removed "solar panels" from the Guest House roof. | The Guest House roof shows no panels in 006 (north half) or 33 (whole roof, from the NW). The panelled tiled roof in 34 belongs to another building, possibly w290690288 north of the gate, whose roof carries panels in 006. That attribution is unverified. |
| R3 | §0 table, P1, L3, checklist 5/10 | Christ Church stretch: 12-13 m along most of the block, **~8 m at y -67..-72.5**, 17-18 m at the gate-passage mouth (was 10-13 m). The south 5.5 m of w1394456869 projects ~5 m west to x 112.3. The café entrance (round arch + roundel) is in that projection's north face (e6, faces 355), and its terrace sits in the angle with the main face. | OSM edges e5/e6 of w1394456869 and my ray casts. 33 (crop) shows the projecting block with the café awning and tables on its north side. The café node (116.2,-64.6) sits in that angle. |
| R4 | §0 table, P2, checklist 5 | Narrow stretch 4.0-5.9 m (min 4.0 m at y ≈ -116), not 4.7-5.8. The west row is not uniformly 5-6 m deep (w290669980 is 16 m, w1394899938 10 m). Junction space 7-34 m (w1545817482 is 5 m off the centre line). The east row has OSM gaps at y ≈ -148 (3.5 m) and y -160..-164 (5 m, leading ~15 m east to w1392907912). No photo shows whether these are openings or unmapped walls. | Ray casts against the OSM footprints. |
| R5 | P2, L4, checklist 6 | West wall of the narrow stretch **~6.5-7.5 m** (was 8-10 m), window sills **~2.5-3 m** (was ~4.5 m), windows ~1.6 m tall. | 21: a jogger (~1.75 m) walking beside the wall near its south end gives a wall top of ~6.5 m and a sill of ~2.5 m. 05: the sill/wall-top ratio is 0.41 (0.38 in 21), and ~18 courses of the 0.35-0.45 m courses the note gives make 6.5-8 m. med. |
| R6 | P2, §4, checklist 7 | Black steel bollards **~0.6-0.7 m** tall, not 0.8-0.9 m. | 03: a bollard standing at the same ground depth as the 1.75 m man is 56 px against his 152 px, so 0.65 m. 01: against the Hyundai i30 (1.48 m), corrected for depth, ~0.62 m. 02: next to pedestrians, ~0.55-0.6 m. Three photos. |
| R7 | P4, L8, checklist 4 | North tunnel building: **3 storeys, ~11-12 m** (was ~4 storeys, 14-15 m). The south-mouth arch is ~2.9 m wide with its crown at ~3.5 m; "2.9 m" is the OSM `maxheight` sign value. | 04: a pedestrian at the mouth gives the top at ~11.4 m and storeys of ~4.2 / 3.7 / 3.5 m. 39: the same face with a ground arch, one window and two windows above, plus the roof steel frame. |
| R8 | P4, L7 | Sandrouni: 10 and 43 carry **identical** coordinates (31.77477, 35.228691). They were copied, so they are not two independent confirmations. The north passage is still the best fit, by elimination. Downgraded to med-high. | index.json lat/lon. The south tunnel has ashlar walls with grilled windows at shop height (04, 22, 39), whereas 10 and 43 show smooth plastered walls under a rendered vault. |
| R9 | §3 | The convent gate is **12 m south of the north tunnel mouth and 42 m north of the south arch**, about a quarter of the way along, not "roughly midway". 03 cannot show this, because the north tunnel is behind its camera. The position (112.5,-223.4) is confirmed. | OSM: way 44376249 ends at y -211.1, the gate is at y -223.4, the south arch north face is at y -265. Footway 722675052; photos 03, 07, 15, 16, 30. |
| R10 | L1, P5, §4 | "North face of w290678899 (e17) closes the sett square" is wrong. e17 is east of the road, faces a 1.5 m gap and a light well, and is invisible from the street. The sett square is on the **west** side of the road. Chamfered limestone bollards line the whole west parking strip. | OSM: e17 at y -213, x 112.9-120.5; the tunnel building's south face is at y -211.5. 15: the camera stands on the setts with the road and the convent wall beyond. 17: the same bollards near the south arch. |
| R11 | §5 | South of the south tunnel, the **retaining wall with the mesh security fence (higher ground behind) is on the EAST side**: w290668993, then OSM wall 1056503911. The **bougainvillea is on the WEST wall**. The note had both on the west, and inferred higher ground to the west. | 20 (looking S, Dormition tower ahead): fence on the left, bougainvillea on the right. 02 (looking N): the reverse. 18 (1997, looking S): rubble retaining wall with a railing and trees above it on the left. |
| R12 | §5 table and text, checklist 15 | The terrain values came from a surface model that includes roofs: **3-6 m too high, and the profile shape is wrong**. Correct profile: Christ Church gate 772.7 → forecourt 775.2 → **Tavern 776.8 (high point)** → junction 775.7 → convent gate 776.1 → south tunnel 775.2 → y -300 775.0. The descent to Zion Gate (~770) starts south of the sector. St James St falls ~4 m to its east end (was 2-3). HaMalakh S ~771.6 (was 775). | Project ground model `data/terrain_street.json` (OS 1865 + GP). OS 1865 spot heights on or beside the road: 774.5 (119,-78), 774.8 (104,-88), bench mark 775.7 (132,-185), 775.4 (107,-249), 774.2 (121,-317); St James St 777.2 (164,-183), 773.0 (214,-151). |
| R13 | §0, P7, checklist 5 | St James St east part is 3.2-4.5 m (was 3.4-6). The 13-41 m OSM gaps further west are unmapped garden walls: photos at x 152-172 show a ~3-3.5 m walled lane with flying arches. | Ray casts. 28 (152,-176, Morany84), 26 (162,-170, PikiWiki 2026), 24 (172,-162, Ludvig14): three different authors. |
| R14 | L2, §3 | Gate → cathedral passage 722675059 is **~16 m, L-shaped** (7 m E, 6.3 m S, 2.4 m E), then 5.7 m of open footway across a court ~6 m wide. It is not "~12 m running SE". | OSM ways 722675059 and 722675049. |
| R15 | L2 | Added a bearing check on the dome in 33. The camera, solved as ≈(90,-35), puts the hemispherical dome's ray through the cathedral footprint at x ≈ 155, so the identification holds within ~2-3°. The pointed cap beside it lies east of the footprint and is not part of the cathedral. Height stays low. | 33. Police block ends at x 765/1135 px and Dormition dome at 1032 px reproduce the camera position to within ~5 px. |
| R16 | L4 | Kishle storeys, window count and arch all rest on 33 alone, so med, not high. The arch is ~9-10 m from the west end against 12-12.7 m for the OSM gate/tunnel: agreement only within ~3 m. | 33; OSM 9937882129 and 1085709199. |
| R17 | L6, §4 | Bulghourji position downgraded to **low**. The facade (≥6 m: door + two windows) cannot fit w1545817482 (faces 4.0 / 4.9 m), which holds the OSM node. Door ~1.25 x 2.8 m (was 1.3 x 2.5) on the note's own plaque scale. The street plaque is **5 x 3 tiles** (was 3 x 6). | 19 (frontal): door 243 x 550 px, plaque 176 px wide. 09: tile joints. OSM w1545817482. |
| R18 | §3 | Cage window over the gate is ~1.6 m wide x ~1.9 m box (~2.6 m with canopy and fringe), not 1.2 x 1.6 m. | 16, on the same doorway scale the note uses for the recess (cage 230 px against a 240 px doorway). |
| R19 | P6 | w1394456882 north face is 6.6 m (was ~7.5 m). A lower 1-storey block with a green door continues further west. | OSM e0+e1. Photos 17 and 01 (far right). |
| R20 | checklist 5 | Convent wall to garden edge in P5 is ~9-11 m (was 10-15 m). | OSM: wall at x 110-112.5, garden 1394066412 edge at x 101-102.5. |
| R21 | P2 | "Pillow" wall: (116,-141) is only photo 11's camera geotag, and the house number "83" comes from a description that was not downloaded. 05, taken south of the Tavern, shows the pillow walling along the east side roughly from y -150 to y -180. The wall north of the Tavern (21) is plain rubble. | 05 (no Tavern canopy or banner ahead; pillow walling continuous to near the tunnel), 21 (crop of the left wall), 11. |
| R22 | P2 | The P2 street lamp is a wall-mounted LED arm on the east wall (05), not a kerb pole. The pole in 02 is south of the south tunnel. | 05, 02. |
| R23 | L3 | Christ Church: the gable is moderately pitched (~30-35°), not steep. There is **one** porch, with a low hipped grey roof and a pointed-arch door, at the south end of the west front. The "gabled entrance porch" and the "small side porch" were the same porch. | 38 and 006. |

### Checked and confirmed
These were checked against OSM and at least two photos with known viewpoints:
- Armenian Tavern on the east side (13, 21).
- Convent wall on the east side of P5, facing west (03, 15, 17, 30; 04, 39 looking north).
- Pedimented face of the south arch faces north (01, 03, 17, 20). 02 looks north at the south face, proved by which sides the fence and bougainvillea are on (see R11).
- Dome over or near the south arch, seen from both sides (03, 02).
- Dormition tower in the vista through the south tunnel (18, 20).
- Christ Church compound layout (006, 33, 38, 137).
- Kishle north face position (33 + OSM).
- Surface change from setts to asphalt at the forecourt (OSM tags; 33/34 against 05/13).
- Convent gate form and fittings (07, 16, 15, 30, 03).
- South arch cornice ~11 m: the 2.2 m door and the R6-scaled bollards in 01 both give 11-13 m.
- Convent wall ~11 m: holds only on a ~2.3-2.5 m doorway (16, 07); there is no independent absolute scale.

### Could not verify (left in the text, marked)
- Bulghourji's side of the road and building (R17).
- Exact spot of the eagle/dove reliefs and the house number 83 (R21).
- Genocide banner "at the junction" (36's geotag only).
- "Welcome to the Jewish Quarter" plaque position (45's geotag only, 14 m off the end of St James St).
- Turquoise direction tiles position (44 only).
- Seminary facade and khachkar row position (14 only; its geotag is on the road centre line).
- Gulbenkian Library position (35's geotag only, as the author already said).
- St Thomas remains and the 2011 grapes relief (descriptions not downloaded).
- Width of St James St at x 113-150 (no photo; R13).
- The OSM gaps in the east row of P2 (R4).
- The "gentle rise towards the north tunnel" read from 05/21 (R12).
- The panelled roof in 34 (R2).
- Sandrouni's wall side (east or west).
- Whether the south-mouth arch of the south tunnel is round or slightly pointed (02 is ambiguous).
- Cathedral dome height.

---------------------------------------------------------------------------------------------------------------

## Sector pass

Pass of 2026-10-20 (profile + building overrides). Files: `data/reference/profiles/s01_armenian.json` and 25
override files in `data/reference/overrides/` (listed below). Renders and side-by-side sheets (photo left, render
right) are in `renders/sectors/s01_armenian/`: `r0_baseline/` (before), `r1`-`r3` (iterations), `r4/` (final,
`r4/sheet.jpg`, plus `pair_*.jpg` per viewpoint). Scratch generators (the profile and overrides are written by
scripts, so the anchors and the absolute fixture heights come from the spec) are in `build/spec_s01_armenian/`.

### What the baseline showed (r0)

- **The road was blocked twice.** Both road tunnels are OSM `layer -1` (44376249 north, 290669005 south) and
  `covered_ways` skips negative layers, so w1392907903 and w1394456881 stood across Armenian Patriarchate Rd.
- **The infill closed the street.** The infill corridor of 26506007 got the minimum 1.4 m half-width (the OSM
  centre line hugs the east row), so a 3 m band of infill stood in front of the mapped west row. The narrow
  stretch was ~2.8 m wide (05, 13, 21 show 5.2-5.9 m). Infill also covered the moat edge and the Kishle forecourt
  (f11, 6.8 m), the sett square and parking strip on the west side of P5 (15, 17), a sliver 0.5-1 m in front of the
  convent wall north of the gate, and the junction space in front of the north tunnel.
- Rule heights of 11-15 m everywhere: the police row (real 6.5-7.5 m, R5), the seminary buildings and the building
  SE of the south arch (15.4 m) stood above the convent wall and the arch building.

### Profile

- `souq_streets`: none, on purpose. There are no market streets here, and the few shops are hand facades. A souq
  profile would also merge canopy keys into those facades.
- `covered_streets`: 44376249 and 290669005. This opens both tunnels. They become souq-kind vaults (spring 4.4 m,
  top = crown + 0.6), which leaves a notch above each arch, so passage-kind vaults are requested.
- `open_areas` (all photo-backed):
  1. moat edge + Kishle forecourt (33);
  2. the narrow stretch between the faces of the mapped rows, plus the junction space at the head of St James St
     (05, 13, 21; R4). Gaps in the rows are still filled behind that line, which matches the continuous walls in 05.
  3. west side of P5: sett square + parking strip (15, 17, R10/R20);
  4. east half of P5 and the pavement in front of the convent wall (03, 15, 17, 30).
- `remove_buildings` + `manual_buildings`: w1392907903 and w1394456881 are replaced by m_s01_armenian_2 / _1. These
  are the same footprints, trimmed by 0.1-0.6 m at the south end. Carving the tunnels out of the OSM rings left
  sliver walls 0.1-0.2 m thick across both south mouths: 3 of the 4.6 m of the south tunnel closed, and half of the
  north tunnel's mouth. The trimmed rings carve cleanly (requested: a carve that reaches the footprint edge).
- `props`: 14 black steel bollards (scale 0.72, ~0.65 m, R6) on the convent-side kerb ~1.75 m off the wall, two
  of them flanking the gate. 16 white chamfered limestone posts (`barrier_post`) along the west sett strip and the
  sett square (15, 17). Two anthracite LED poles (`lamp_modern`, scale 0.85) on the west kerb of P5, arm over the
  road (01, 03, 17).

### Building overrides (heights, wall, tint, facades; photo-matched facades have `"auto": false`)

| building | what | evidence |
|---|---|---|
| w290678899 (+ piece _1 after the gate passage) | convent street front north and south of the gate: 11.0 m, ashlar, whitest neutral tint. Three sparse rows of grilled windows (small ~3 m, hooded ~5 m, cage ~8-9.5 m), APR plaque ~4 m north of the recess, gate lamps both sides, downpipes | 03, 15, 16, 30, 07 |
| w612002272 | convent front south of the gate (29 m): 11.5 m, same rows, downpipes | 01, 03, 17, 30 |
| m_s01_armenian_1 (was w1394456881) | south arch building: 11 m cornice, cream ashlar. Passage walls with small grilled windows, a doorway, lantern brackets | 01, 17, 02, 22, 04 |
| w1394456882 | west block of the arch: 11 m, three tall grilled windows upstairs, small arched window, grey door, green-door annexe | 01, 17, 03 |
| m_s01_armenian_2 (was w1392907903) | north tunnel building: 11.4 m (R7). South faces with round-arched windows, plain north face. Sandrouni teal shop fronts inside the passage (east wall, position unverified) | 04, 39, 05, 10, 43 |
| w290669980 | Kishle north block: 9 m + hipped tile roof. Forecourt face with 9 round-arched upper windows (7 seen in 33, 2 assumed behind the cypress) and the arched vehicle gate at u 13 (photo ~14, OSM ~11.7) | 33 |
| w1394899938, w1394458560, w1394458561 | police row, the blind west wall of the narrow stretch: 7.0 m, coursed `rubble` texture (matches the weathered courses better than the smooth `ashlar`), sparse tall round-arched windows with brown shutters (sill 2.7 m), spouts | 05, 21, 13; R5 |
| w1392907916 | Armenian Tavern: 9 m, rough rubble, steel doors, canopy u 0.5-8.6 at 3 m (invisible from below, see requests), floodlights, barred windows upstairs | 12, 13, 21 |
| w1392907908/09/10 | east side y -150..-180: 10.5 m, whitish (pillow pointing), few small windows, a green-shuttered one high up | 05, 11 |
| w1392907911 | **Bulghourji**, placed on this building's west face (reasoning in its notes: the node's y matches the face centre, the plaque says APR, and 19's ~5 m distance fits the junction): door, two scroll-grilled arched windows, plaque, oculus, lamp; grey rubble | 19, 08, 09, 36 |
| w1394456869, w1394456870 | Christ Church street block: one 5.5 m storey, honey stone. Post-office door, small window + oculus, big arch with scroll grille, souvenir shop with green doors, cafe entrance and roundel in the projection's north face, awnings | 34, 33, 006 |
| w1550194749, w1550194748, w1394456871 | forecourt east side: 1-storey terraces (5-5.5 m); the white 2-storey house with a hipped tile roof (8 m) | 33 |
| w1394456873, w1394456874 | east side north of the Tavern: 9-9.5 m rough rubble (rule gave 10-13 m) | 13, 21 |
| w1394456878, w290669016 | seminary buildings west of the garden: 9 m (rule 12.8/15.4 m). w1394456878 has tall round-arched windows facing the lawn | 14, 03, 17 |
| w290668993 | building over the east retaining wall south of the arch: 9 m (rule 15.4 m; nothing rises above the arch/convent line in 01/03). The face hidden behind the arch strip is blank | 02, 20, 01, 03 |
| w1084488112 | police guard booth: 2.8 m (rule 5.7 m made a tower in front of the Kishle) | 33 |

Fixture and awning heights in the overrides are absolute (facades.py appends them as given): they were computed
from the spec's edge ground and must be regenerated (`build/spec_s01_armenian/write_overrides.py`) if the terrain
changes.

### Viewpoints (render_city `--cam`, matching photo)

- `v01_arch:104.5,-242,1.6:105.5,-266,4.5` (01); `v03_gate:108.6,-212.5,1.6:106.5,-262,3.5` (03);
  `v05_narrow:119.0,-141,1.6:112,-185,2.5` (05); `v21_tavern:118.6,-122,1.6:113,-184,3` (21);
  `v13_tavern:119.6,-116.5,1.6:114,-160,3` (13); `v20_tunnel:106.5,-258,1.6:107.5,-300,3` (20);
  `v_north_entry:112.5,-36,1.6:111,-85,3` (33 crop / approach from Jaffa Gate);
  `v34_christchurch:109.5,-45,1.6:117.3,-56,3` (34); `aerial33:84,-28,26:122,-92,0` (33);
  `v28_stjames:154.7,-180,1.6:156.3,-163,3.5` (28).
- With `--abs` (z = street level + eye height, from make_spec.street_z; these stand where the not-yet-rebuilt base has
  no ground, or on the generated steps of St James St): `v15_wall:103.0,-213.8,7.25:113,-224,9.9` (15);
  `v04_tunnel_n:106.8,-288,6.2:107.6,-240,7.4` (04); `v02b_southmouth:107.5,-305,5.95:107,-290,8.57` (02);
  `v19_bulghourji:111.4,-176.5,6.86:116.3,-176.3,8.6` (19); `v23_stjames_e:183.2,-164.3,6.91:214,-155.5,5.63` (23).

### Remaining differences (see the profile's requests)

- Ground: no asphalt carriageway, slab pavements or setts (everything is generic paving). Until base.json is
  rebuilt, the renders show holes where the removed infill stood and under both tunnels. There is no moat
  excavation pit west of the road.
- South arch building: no pediment, archivolt or keystone, and no dome. The souq-kind vault top (~8 m) leaves a
  notch between 11 m strips. The north tunnel is likewise taller and narrower than the real 2.9 m-wide, 3.5 m-crown arch.
- Convent: the ashlar texture stays beige and its joints are faint next to the pale grey-white, sharply jointed wall
  of 03/15/30. The scalloped tin hoods and projecting cage windows are plain grilled windows, and the gate is a plain
  3.2 m vault mouth instead of the 5.8 m muqarnas recess.
- St James St: walled 3-3.5 m lane as in 23/28, but without its flying arches. It also gets stair treads east of
  x ~175 that the photos do not show.
- Missing: the mesh security fences on the police row and on the south retaining wall; the green garden fence and
  hedge; Aleppo/stone pines (olives stand in); the flying arches of St James St; the pillow-pointed wall texture;
  the Tavern banner/tile panel/flags; the cafe and Tavern awnings from street level (a build bug); cars and the
  parcel locker.

Audit (`blender/audit.py` on `build/s01_armenian.blend`): leaving out the pairs with `lod_s01_armenian`, one
coplanar overlap remains, 0.05 m2 between infill f451 and w290687982 (yeshiva, x ~227), which this pass did not
touch. Nothing involves the manual buildings, the overridden buildings or the vaults.
