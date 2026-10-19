# Jaffa Gate tower, adjacent city wall, passage and plazas: modelling reference

Status: **v3, complete** (numbers table in section 9, model checklist at the end).

Scope: the Jaffa Gate tower (OSM w391433915), the city wall NW of it, the 1898 breach to the
Citadel, the outer plaza (W) and the strip just inside (E/NE). Local frame as in `hero_edges.md`
(x east, y north, metres from the Jaffa Gate node 561157424). For the buildings on the square
(the "Ramparts Walk" building w1393747403 at (12,7) and the Tourist Information office
w1393420835) see `square_north.md`. That file already covers them; this file only notes how they
meet the gate.

Photo keys: `P:NNN` = `data/photos/NNN_*.jpg`; `R:gNN` = `data/photos_ref/gate/gNN_*.jpg`
(`index.json` there has title, page URL, author, licence, date, lat/lon). Prefer 2015+ evidence.
Commons GPS is often 10–30 m off here (several "outside" photos are tagged inside the walls), so
camera positions were re-derived from what is visible.
Confidence: **H** = clear in 2+ photos or measured with a good ruler; **M** = one good photo or
scaled from people; **L** = inferred, partly hidden or contradictory.

Rulers: people 1.7 m; OSM gate-tower edges (all ~10 m: e0 9.97, e1 9.98, e2 9.19, e3 9.98); the
wicket door in a gate leaf (~0.8 m). R:g33 (2015, near-frontal on the NW face) is the best
measuring photo: face width 546 px = 10.0 m gives 54.6 px/m on the face plane. This agrees with the
walkers at the threshold once their ~3 m distance in front of the face is corrected for.

Already modelled elsewhere and not repeated in detail: modern plaza furniture (grey square
lamp poles, disc-head lamps on the outer plaza, slatted bins, stone benches, stone blocks along the
breach road, young trees in square pits).

## 0. Plan: how the pieces fit (read this first)

- **Gate tower**: a ~10 x 10 m square rotated 45 deg (faces NW / SW / SE / NE). It projects ~10 m
  OUTWARD (SW) from the line of the city wall. Edge 3 (D->A, inner face, faces NE ~52 deg) lies
  roughly on the wall line. Edge 0 (A->B) is the tower's NW flank, perpendicular to the wall. (H: OSM + photos)
- **Outer entrance**: middle of edge 0, i.e. in the NW flank, facing along the wall towards the NW.
  You reach it from the plaza through the re-entrant angle between the tower flank and the wall
  face. From the W plaza the entrance face is seen at ~40 deg. From the SW it is edge-on: only the
  profile of its box machicolation shows, and the big plain SW face (edge 1) dominates the view.
  (H: P:062, P:065, R:g10, R:g14, R:g33, R:g22)
- **Passage**: L-shaped. In through edge 0 heading SE into one vaulted chamber, turn 90 deg
  **left**, out through edge 3 heading NE into Omar Ibn el-Khattab Square. Level floor, no steps.
  (H: OSM footway w472110707, P:052, P:053, R:g34, R:g35, R:g36)
- **Wall face NW of vertex A** (faces SW, outside) seen from the plaza, NW to SE:
  `long curtain (~11–11.5 m) | TALL SECTION ~9 m wide (~13–13.5 m) | lower curtain ~5–6 m wide with the BLIND ARCH (~10.8 m) | re-entrant corner A | gate tower`.
  Angular widths in R:g10 fit all three lying on the OSM wall line: blind-arch curtain s = 0–6 m
  and tall section s = 6–15 m from A (predicted 6.3 deg and 11.7 deg, measured 5.4 and 12.7). So the
  tall section is a raised stretch of the wall that projects at most ~1.5 m, not a big flanking
  tower. Schick's 1898 plan (R:g00) also shows a straight wall here. (M)
- **1898 breach**: runs past the tower's S side (corner C, edge 2) to the Citadel's NW tower at
  ~(16,-18)–(19,-13). No wall survives in the gap; it is a ~12–14 m wide paved road/plaza
  opening. (H: R:g00, R:g14, R:g15, R:g29, P:072)

## 1. Gate tower: exterior

### 1.1 Mass and height
- Plan: square ~10 x 10 m per OSM ring [(3.4,3.2), (-3.8,-3.7), (2.9,-11.1), (9.5,-4.7)]. (H)
- **Height to merlon tops ~13 m above the outer threshold (measured 11.8–13.4).** R:g33: merlon
  top 13.4, crenel sill 12.3. R:g10: ~12.2. R:g14: ~12.0. The machicolation cap is the highest
  point (~13.9). The current spec's 15.0 m is ~2 m too tall: use **13.0** (sill ~11.9). (M)
- Relative heights in the frontal views (R:g10, R:g14, P:062): the tall wall section NW is equal
  or slightly taller (x1.05–1.1). The blind-arch curtain is ~0.82 x, the long curtain ~0.87 x.
  The Citadel NW tower across the breach is clearly taller than the gate tower. (M)
- No batter at the foot: all four faces go straight into the paving. (H: R:g33, P:064, R:g22, P:063)
  The bottom 1–2 courses are darker (damp, grime). (M)
- The roof is a walkable terrace (start of the Ramparts Walk). A grey steel **railing** ~1.1 m
  runs along the inner side of the parapet. It shows above the SE/NE parapet from the square and
  through the crenels from outside. (H: R:g01, R:g02, P:063, P:064)

### 1.2 Masonry
- Coursed, smooth-dressed limestone ashlar. Courses ~0.45–0.65 m high, blocks 0.6–1.4 m long
  with irregular lengths. Thin lime joints. Some blocks have drafted margins; faces are pitted and
  honeycombed by weathering. (H: P:054, P:055, P:057, R:g18, R:g33)
- The gate tower is visibly smoother and paler than the Citadel tower across the breach, which has
  big rough **bossed (rusticated)** stones. Keep two materials. (H: R:g10, R:g15, R:g29, P:072)
- Colour (daylight): pale cream to warm honey, with greyish and pinkish blocks mixed in. Some
  stones are near-white where cleaned. Grey-black streaks run down below slits and merlon gaps.
  The inner NE face is darker and dirtier than the outer faces. (H)

### 1.3 Crenellation
- Shape: **plain rectangular merlons with flat tops** (no pointed caps), broad, with narrow
  crenels. A narrow vertical slit ~0.1 x 0.6 m is cut in most merlons, ending just below the top.
  (H: P:062, R:g14, R:g33, R:g10, P:060, R:g28)
- NW face (edge 0, entrance): three broad merlons ~2.8–3.0 m wide, crenels ~0.5–0.7 m. The
  middle one is the top of the box machicolation. (M: R:g33)
- SW face (edge 1): four merlons ~2.0–2.6 m wide, crenels 0.4–0.7 m, crenel depth ~1.05–1.15 m.
  (M: R:g14 and P:062, both near frontal)
- Inner NE face (edge 3): four merlons of uneven width ~1.5–2.2 m, crenels ~0.8–1.0 m.
  (M: P:060, R:g40, P:093 for the matching curtain)
- Corner merlons are wider and slightly taller and read as little corner turrets. Tops are uneven
  and worn, some broken; tufts of grass and caper bushes grow on them. (H)
- The current model (cw 2.6, mw 2.6, cr 0.95, sill 1.25) is close. Use crenels ~0.6 on the
  outer faces and sill depth ~1.1.

### 1.4 Outer entrance portal (NW face, edge 0), scaled from R:g33 at 54.6 px/m
Three nested layers, from the face inwards:
1. **Moulded pointed arch frame**: a single roll (torus) moulding standing proud of the face,
   two-centred pointed arch. Outer extent ~6.7 m wide, inner edge ~5.2 m. Springing at ~4.9 m,
   apex ~8.4 m (outer) / ~7.7 m (inner). At each springing the moulding turns outward into a
   **small spiral volute**. Just beyond each volute, at the same height, is a **carved rosette
   roundel** ~0.5–0.6 m across (an 8–12-petal geometric flower in a ring).
   (H: R:g33, P:067, P:068, R:g42; the inner twin is in R:g43, P:090, P:092)
2. **Recessed tympanum** inside the moulding, recessed ~0.4–0.6 m and filled with ashlar. It holds:
   the **inscription panel** (1.6); two plain roundels ~0.4 m flanking it and a third above it near
   the apex; below it a **curved moulded band** (convex cornice) following the doorway arch; a small
   projecting keystone block at the apex. (H: P:061, P:069, P:104, R:g33, R:g42)
3. **Doorway**: ~3.2–3.5 m wide x ~4.5–5.2 m to the crown. Jambs of large ashlar. The top is a very
   flat segmental arch of ~7–9 big voussoirs with rounded upper corners, directly under the curved
   band. The door frame steps back ~0.5 m behind the tympanum, and the passage behind it is taller
   and pointed. (M: R:g33, R:g10, P:094, R:g22)
- Inside the doorway, at the springing of the taller passage arch beside the door leaf, there is a
  small **muqarnas capital** (a band of little pointed niches, ~0.6 x 0.5 m). One is photographed;
  assume a matching pair. (H that it exists: R:g38; L for the pair)
- The model's `GATE_OUTER` (recess 5.0 m wide, springing 5.0, rise 3.45, so apex 8.45) fits these
  numbers. Door width 3.6 in the spec vs ~3.3 measured: acceptable.

### 1.5 Box machicolation over the outer doorway
- Centred over the doorway (within ~0.3 m). The box is ~1.5 m wide, projects ~0.6–0.8 m and spans
  ~9.9 m to ~12.8 m. It sits on **three stepped corbels with two dark drop-openings** between them.
  It has one narrow vertical slit in front, a thin cornice/dentil line under the top, and a small
  carved roundel just below the corbels. Its top rises as the middle merlon and ends in a **small
  pyramidal stone cap with a knob** (~13.9 m). (H: R:g33, R:g10, P:068, R:g42, R:g11)
- One slit with a round foot on each side of it, ~1 m lower (~8.5–10 m), ~1.2 m out from the box
  edges. (H: R:g42, P:068)

### 1.6 Inscription panels
- **Outer tympanum panel**: rectangular, ~2.0 x 0.75 m (aspect ~2.7:1). Centre ~6.8 m above the
  threshold, above the curved band, with a thin raised border. **Three lines of Ottoman Arabic
  thuluth in low relief**, in the same grey-cream stone as the wall, slightly darker; not legible at
  Commons resolution. The Ministry of Tourism plaque in the gate (P:089) paraphrases the dedication:
  "In the name of God, the compassionate... our lord the great sultan... Suleiman son of Selim
  Khan... ordered that this blessed wall be constructed. In the year 945 (1538)".
  (H for form; M for the dimensions)
- **Panel inside the passage** (on the chamber's back wall facing you as you enter): ~1.5 x 0.75 m
  with a raised outer frame of leafy arabesque scrolls. Inside is a cartouche with **one line** of
  thuluth, read in P:078 as "la ilaha illa Allah, Ibrahim khalil Allah" ("There is no god but God;
  Abraham is the Friend of God", the origin of the name Bab al-Khalil). (H for form: P:078, R:g34;
  M that this panel is the one in the chamber)
- Inner tympanum (NE face) also has a rectangular Arabic panel similar to the outer one.
  (H: P:060, R:g40, P:092)
- Texture all of these as **low-relief calligraphy in stone**, not bright plaques. (H)

### 1.7 Slits, roundels and other features on the faces
- **Arrow slits (gun loops)**: narrow vertical slits ~0.10–0.15 m wide x ~1.5–2.0 m tall, ending at
  the bottom in a **round or oval oillet ~0.2–0.3 m**. Often a small carved block or roundel sits
  above the slit, with two plain roundels at mid-height either side. Some go right through (daylight
  visible). From inside they open at the back of deep splayed embrasures. (H: P:054, P:055, P:057,
  P:068, P:147)
- NW face: the two slits by the machicolation, plus the merlon slits. (H)
- SW face (edge 1): plain. One slit high on the left, one carved roundel, and a **lamp bracket with
  two cables forming a wide V** at about 2/3 height near the middle (an old floodlight arm). A long
  repaired crack runs down from the parapet. (H: P:062, R:g10, R:g14, R:g29)
- SE face (edge 2, towards the breach road): plain. Patchy repairs near the D end, where the
  demolished 1898 wall joined: a vertical strip ~1.2 m wide of small, irregular, partly pinkish
  rebuilt stones set in the large ashlar. (M: R:g21, P:064, P:063)
- No windows on the gate-tower faces, only slits. (H)
- Roundels (flat discs 0.35–0.6 m, standing ~5 cm proud) are scattered: two at each arch springing,
  ~3 in each tympanum, single ones by slits, one on the SW face. (H)

### 1.8 Inner face (edge 3, facing NE onto the square)
- Same three-layer portal as outside, slightly smaller: moulded pointed arch ending in volutes with
  big carved rosettes (~0.6 m) at the springing, a recessed tympanum with an Arabic panel, and a flat
  doorway with rounded corners. (H: P:060, R:g40, R:g43, P:092)
- Over the apex at ~9–10 m is a **small corbelled machicolation / lantern** ~1.2 m wide, with a
  pendant bottom and a little carved crown-like crenellated top. Two small corbels sit either side
  of the arch at ~8 m. (H: P:060, R:g40, P:092)
- One slit on each side at ~8–9 m. (M)
- Plants grow in the joints, and there is more black staining than outside. (H: P:033, R:g40)
- **Signs on the SE part of the inner face (left of the arch as seen from the square, towards D)**, top to bottom (H: P:090,
  P:091, P:092, P:060, R:g43):
  - ~3.3 m: ceramic tile sign "JAFFA GATE / باب الخليل / שער יפו", white with black lettering and a
    green interlace border, ~0.45 x 0.40 m (Armenian ceramic style; the same design, damaged, in
    P:105).
  - ~2.4 m: ceramic street sign "ככר עמר אבן כטאב / ميدان عمر بن الخطاب / OMAR IBN EL-KHATTAB SQ.",
    two rows of tiles, white with a patterned green-yellow border, ~0.8 x 0.45 m.
  - ~1.4 m: black municipal heritage plaque "שער יפו / باب الخليل / Jaffa Gate", ~0.6 x 0.45 m,
    with teal bands at top and bottom.
  - Also: a CCTV camera and a small spotlight on the arch jambs, and a string of festoon bulbs
    looping across the upper face (2015).
- Right (N) of the inner doorway, within a few metres, is the 2-storey **Ramparts Walk** building
  (w1393747403). It has blue vertical banner signs "כניסה / Entrance" with a down arrow, a purple
  hanging blade sign "טיילת החומות / The Ramparts Walk / متنزه الأسوار", a red awning sign, and a
  roller shutter. (H: P:060, P:063, R:g39, R:g40; details in `square_north.md`)

## 2. The passage (interior)
- One square chamber, ~5–6 m inside (tower 10 m minus walls 2–2.5 m), under a **pointed groin
  (cross) vault with a round boss** at the crown. The groins are sharp and the vault surface is
  smooth, lime-washed or plastered, paler than the walls. Pointed transverse arches on all four
  sides frame the outer doorway, the inner doorway and two blind walls.
  (H: P:052, P:058, R:g34, R:g36)
- Heights (M, from the woman at the niche in P:052): blind-wall arch apex ~5.5 m, vault crown
  ~6.5–7 m. The model's vault should not go above ~7.5 m.
- **Back (SE) wall**, facing you as you enter: under its pointed arch, plain ashlar with a roundel
  at ~4.5 m and the framed Arabic panel (1.6) at ~3.5 m. (H: R:g34, P:052)
- **Side (SW) wall**: a big **pointed-arch niche** ~1.6 m wide x ~2.5 m high x ~0.8 m deep, sill
  ~1.2 m above the floor, with an arrow slit through its back (a streak of daylight) and a roundel
  above. Buskers sit in it, e.g. a harpist in R:g37. P:147 shows a terracotta pot of red geraniums
  on a slit sill. (H: R:g36, R:g37, P:052, P:147)
- **Door leaves fixed open**: two per doorway, each ~1.9 m wide x ~4.5 m, sheathed in grey-green
  painted iron plates (grid of ~0.45 x 0.9 m plates with rivet seams). One leaf has a wicket door
  ~0.8 x 1.8 m. Since 2023–25 the lower 2–3 m of the inner leaves are **covered in hundreds of
  stickers** (hostage/soldier memorial and political stickers), a strong current detail. Older
  photos show only scattered stickers and graffiti. They stand open against the jambs just inside
  both doorways. (H: R:g34, R:g36, P:094, R:g28, P:044, P:045, P:046)
- **Floor**: large worn limestone slabs 0.4–0.9 m in irregular courses, polished shiny by feet,
  cream/grey/pinkish, with a small square drain grate. The same slabs run a few metres out of both
  doorways. (H: R:g35, R:g36, R:g34, P:053)
- Under the inner arch is a pointed barrel vault of big voussoirs with the **old door pivot
  sockets** (round stone blocks with holes) at both upper corners. (H: P:059)
- Lighting: warm uplights or wall boxes at the vault impost, so at night the vault glows yellow.
  Black box lights sit on the doorway jambs. (H: R:g28, R:g30, R:g39, R:g48, R:g34)
- A free-standing info board in a black frame and A-frame signs stand just inside the inner
  doorway. A ka'ak (sesame bread) cart, a wooden barrow on two bicycle wheels piled with bread
  rings, and a vendor on a plastic chair are a fixture at the inner doorway. (H: P:060, P:047)

## 3. City wall NW of the gate

### 3.1 The blind arch next to the gate (curtain s = 0–6 m from A)
- A blind pointed arch on the SW-facing wall face just NW of vertex A, at the back of the
  re-entrant angle. It reaches the ground as a niche ~0.5–1 m deep with a low plinth/bench at its
  foot. ~4.5–5.5 m wide, springing ~4.5 m (its SE capital is level with the gate portal's NE
  rosette, ~1 m from the corner A on the other face: P:067 shows both planes meeting in the
  concave corner), apex ~6.5–7 m. The arch is plain voussoirs (no roll
  moulding). **Carved acanthus capitals** (Crusader-era spolia) sit at both springings. ~6–7
  roundels are scattered around it, and a rough carved projecting block sits above the apex.
  (H for features: P:070, P:093, R:g20, R:g19, P:067; M for size: P:062, R:g10, R:g14)
- Tympanum: a **stepped two-tier Arabic inscription**, an upper panel ~0.9 x 0.45 m centred over a
  wider lower panel ~1.8 x 0.6 m. Below it is a **white marble plaque** ~1.0 x 0.85 m with a
  bilingual Hebrew–Arabic text, and a roundel above. (H: P:066, P:070, P:093, R:g20)
- Position: arch centred ~3 m NW of A along the wall, at about (1.3, 5.3), facing ~225 deg. (M)
  The current model already places a 4.4 m blind arch 4.6 m from the gate end. Move it to ~3 m,
  raise the apex to ~6.5–7 m and add the capitals, the stepped inscription and the plaque.
- Curtain above it: top ~10.8 m. Merlons ~1.1–1.3 m wide (some up to ~2 m in P:093), gaps ~0.6 m,
  ~0.7 m tall, each with a slit. A grey railing of the wall walk shows behind the merlons. (M:
  R:g14, P:062, P:093)

### 3.2 Tall section (s ≈ 6–15 m from A)
- Face ~9 m wide, crenellated with three merlons ~2.0 m wide (gaps ~0.4–0.6 m, slit in each).
  Merlon tops ~13–13.5 m, so it stands out above both neighbours. It has arrow slits with round
  oillets at mid-height and a few roundels, and is otherwise plain. (M: R:g14, R:g10, P:062, P:065)
- Projects 0–1.5 m from the curtain line. Model it as a raised wall stretch with a slight forward
  step. (M/L)

### 3.3 Long curtain further NW (s > 15 m)
- Merlon tops ~11–11.5 m. Rectangular flat-topped merlons ~1.5–1.7 m wide, gaps ~0.4–0.5 m,
  ~0.75 m tall, many with slits. Square towers project from the curtain at intervals of ~40–60 m
  further NW (beyond the PoC edge). (M: R:g14, P:064 left, R:g49)
- Thickness: not directly visible. Suleiman's walls are ~2.5–3 m thick with a wall walk ~1.5–2 m
  behind a ~0.7–0.8 m parapet. The model's 3.2 m is fine. (L, general knowledge)
- Batter: none where the wall meets the outer plaza near the gate (H: R:g14, P:062). Further NW
  along Jaffa Road the wall stands on a high battered rubble revetment above the road cutting
  (P:085, P:086), outside the PoC area.
- Stone: like the gate but rougher and more weathered: honey-grey, many pitted and darker blocks,
  courses ~0.4–0.6 m. Vegetation (caper bushes, grass, wall pellitory) grows from joints in the
  upper half, typically every 10–20 m. (H: R:g49, P:064, P:087)
- Fixtures on/near the wall: a CCTV pole with 4 cameras on the plaza (P:064); flags (a yellow-white
  Vatican flag above the wall NW in P:064, Israeli flags on the Citadel side); large festival
  projections on the outer face (Hanukkah, P:085/P:086; the projectors are not on the wall). No
  wall-mounted floodlight rows visible by day near the gate. (M)

## 4. The 1898 breach (between the gate tower and the Citadel)
- A ~12–14 m wide opening between the gate tower's S corner C / SE face and the Citadel NW
  tower. It carries the paved road into the square (cars, taxis, the tourist "train"), with
  footways on either side. (H: R:g14, R:g15, R:g29, P:072, P:032, R:g07)
- Bounded on the NW by the plain SE face of the gate tower (repaired scar, railing on top) and on
  the SE by the Citadel NW tower: big **bossed rusticated** blocks, three **box machicolations** on
  each upper face, a barred rectangular window and a round oculus, taller than the gate tower.
  The Citadel side has the museum entrance dressing: **red vertical banners** in steel frames
  ("Tower of David / Jerusalem Museum", He/Ar/En), teal/red sign panels, a row of **Israeli flags on
  tall poles**, steel tube handrails on a short ramp/steps, and a railing along the moat edge.
  (H: P:062, R:g15, R:g29, R:g02, P:072)
- Paving in the breach: large rectangular light stone slabs; from the square side the car lane is
  grey setts (R:g07). From the gate roof (R:g02) the road continues SW downhill to the asphalt of
  Hativat Yerushalayim / Jaffa Road. (M)
- Nothing marks the line of the demolished wall on the ground. (M)

## 5. Outer plaza (west of the gate): only what is not already modelled
- Paving: honey-beige rectangular pavers ~0.2 x 0.4 m in running bond, divided into a large grid
  by **bands of pale cream stone ~0.5–0.6 m wide** (cells ~6–8 m). Square tree pits sit in the
  band grid. The pavers are noticeably warmer and smaller than the big worn slabs inside the gate.
  (H: P:062, P:096, R:g14, R:g32)
- Around the foot of the gate tower and the blind arch: grey steel crowd-barrier panels on wheels,
  often parked against the SW face; low black railings. A temporary steel cage (security kiosk
  enclosure) has stood on the NW-face side. (M: P:062, P:063, R:g33, R:g10)
- Signage near the gate outside: a pole-mounted white directional sign (He/Ar/En, ~0.6 x 0.3 m at
  ~2.5 m) by the railing E of the entrance; a large blue-white municipal banner on the plaza railing
  (2023); the red museum banners belong to the Citadel side of the breach (section 4). (M: R:g11, R:g10)
- A carved reused stone (ornamental band / worn inscription, ~0.6 x 0.9 m) is set in the lowest
  courses just left of the outer doorway. (M: P:044)
- Small white marble plaque "שער יפו / JAFFA GATE" plus a donor line, ~0.5 x 0.35 m at ~1.8 m, in
  a shaded re-entrant corner with ivy and capers hanging above. Exact spot uncertain: probably the
  angle at A. (L: R:g51)
- Seasonal: a giant lit Hanukkah menorah on the plaza (R:g53, P:037); light projections on the
  wall (P:085, P:086). (H; optional)

## 6. Just inside the gate (between the gate and the first buildings)
- Ground: big worn limestone slabs (0.5–0.9 m) in rough courses, grey-beige, shiny, with
  manhole/drain covers. The car lane along the Citadel's north wall is darker grey setts.
  (H: P:032, P:033, R:g07)
- Ramparts Walk building (w1393747403) is immediately N/NE of the inner doorway (1.8 and
  `square_north.md`). The Tourist Information office (w1393420835) is further NE beyond it, with
  a glazed arched shopfront and the blue Ministry of Tourism "i" sign on a bracket (P:099; details in
  `square_north.md`).
- The **Architects' Tombs**: two Ottoman stone cenotaphs (~1.8 x 0.7 x 0.8 m), one with a
  turban-shaped stone finial on a short post at its head. They stand on a small cobbled patch behind
  a railing against a rubble-faced wall with drainpipes and cables, just inside the gate on the N
  side, against the inner face of the wall. Exact spot not established. (H for appearance:
  R:g44; L for position)
- A black wayfinding totem (~2.2 x 0.6 m, teal top band, He/Ar/En arrows, light-blue map panel,
  stickers) on the square near the gate. (H: P:098)
- Fixed kiosk canopy (dark steel on tall square posts) and ice-cream freezer by the Citadel wall;
  the green-yellow **tourist "Old City train"** parks on the square inside the breach.
  (H: P:033; optional props)

## 7. Recurring authenticity details (gate area)
- Stone tone: pale cream / honey limestone, cooler grey in shade, warm gold at low sun. Individual
  blocks vary from near-white to pinkish-orange and grey. Avoid a uniform beige. (H)
- Weathering: black-grey vertical streaks below slits, merlon gaps and drip points; pitted,
  honeycombed faces; darker damp band at the foot; lighter patches where stones were replaced. (H)
- Vegetation from joints: caper bushes and grass on merlon tops and in upper courses; ivy and
  pellitory in shaded corners. (H)
- Cables: thin black cables run along the wall faces to CCTV cameras and spotlights. The V-shaped
  lamp bracket is on the gate's SW face. Drainpipes and conduits are on inner walls. (H)
- Flags: Israeli flags on tall poles along the Citadel side of the breach, banners in steel frames.
  (H)
- Stickers on the gate leaves (recent, dense), on lamp poles and on the wayfinding totem. (H)
- Signage style: ceramic tile street signs (white, black lettering, coloured interlace border) set
  into the stone; black municipal heritage plaques with teal bands; purple Ramparts Walk blade sign.
  (H)

## 8. Night appearance (optional but very recognisable)
- The outer faces are floodlit warm white from ground level; the passage vault glows yellow; the
  box machicolation and the arch frame catch the light. **Small lights in the crenels** make the
  merlon tops glow. The Citadel is floodlit warm white with its red banners lit. Tall poles
  carry cool-white LED heads. (H: R:g28, R:g29, R:g30, R:g39)

## 9. Numbers at a glance (heights above the outer threshold, z = 0)

| item | value | conf | source |
|---|---|---|---|
| gate tower merlon top | **13.0 m** (spec 15.0 is too tall) | M | R:g33, R:g10, R:g14 |
| gate tower crenel sill | 11.9 m (merlons ~1.1 m tall) | M | R:g33, R:g14 |
| machicolation box (outer) | w 1.5, projection 0.7, z 9.9–12.8, cap to 13.9 | M | R:g33 |
| outer moulded arch | outer w 6.7 / inner w 5.2; springing 4.9; apex 8.4 / 7.7 | M | R:g33 |
| outer doorway | w 3.2–3.5, crown 4.5–5.2, rounded upper corners | M | R:g33, R:g10 |
| outer inscription | 2.0 x 0.75, centre z 6.8, 3 lines | M | R:g33, P:069 |
| rosettes at springing | dia 0.5–0.6, z ~4.9, just outside the volutes | M | R:g33, P:067 |
| merlons, NW face | 3 x 2.8–3.0 m, crenels 0.5–0.7 | M | R:g33 |
| merlons, SW face | 4 x 2.0–2.6 m, crenels 0.4–0.7 | M | R:g14, P:062 |
| merlons, NE face | 4 x 1.5–2.2 m, crenels 0.8–1.0 | M | P:060, R:g40 |
| arrow slit | 0.10–0.15 x 1.5–2.0, round oillet 0.2–0.3 | H | P:054, P:055, P:057 |
| chamber vault crown | 6.5–7 m (keep below 7.5) | M | P:052 |
| chamber blind-wall arch apex | ~5.5 m | M | P:052 |
| chamber side niche | 1.6 w x 2.5 h x 0.8 d, sill 1.2 | M | R:g37 |
| door leaf | ~1.9 x 4.5, wicket 0.8 x 1.8 | M | R:g34, P:046 |
| blind arch (wall, ~3 m NW of A) | w 4.5–5.5, springing ~4.5, apex 6.5–7, depth 0.5–1 | M | P:062, R:g14, P:067 |
| blind-arch inscriptions | upper 0.9 x 0.45 over lower 1.8 x 0.6; marble plaque 1.0 x 0.85 below | M | P:066, R:g20 |
| curtain with blind arch, top | ~10.8 m, merlons 1.1–1.3 w, gaps 0.6, 0.7 tall | M | R:g14, P:062 |
| tall wall section (s 6–15 m) | top ~13–13.5 m, 3 merlons x 2.0 m | M | R:g14, R:g10 |
| long curtain further NW | top ~11–11.5 m, merlons 1.5–1.7 w, gaps 0.4–0.5, 0.75 tall | M | R:g14 |
| breach width | ~12–14 m | M | OSM + R:g14, R:g29 |
| ashlar courses | 0.45–0.65 m (gate), 0.4–0.6 m (wall) | H | close-ups |

## Model checklist (priority order: what makes the place read as Jaffa Gate)

1. **Correct massing and silhouette**: the ~10 x 10 m tower projecting 10 m out from the wall with
   the entrance in its NW flank (L-shaped route). Lower the merlon top to ~13 m. Raise the tall wall
   section NW (~13.5 m), keep the lower blind-arch curtain (~10.8 m) between them, and keep the
   long curtain at ~11–11.5 m. That stepped skyline is the signature view from the plaza.
2. **The outer portal**: moulded pointed arch with volutes and rosettes, recessed tympanum, flat
   rounded-corner doorway, curved band. Proportions as in section 9.
3. **The box machicolation over the outer arch**: three corbels, two drop-holes, slit, pyramid cap
   rising above the merlons. It is the one projecting element seen from every side, including in
   profile from the SW.
4. **Broad flat-topped rectangular merlons with narrow crenels and slits in the merlons** on the
   tower, and the smaller rhythm on the curtains.
5. **The outer inscription panel** (3-line thuluth, low relief) in the tympanum with its three
   roundels.
6. **The blind arch beside the gate** with acanthus capitals, the stepped two-tier inscription and
   the white plaque, about 3 m NW of the corner, plus the concave corner it makes with the portal.
7. **Two stone materials**: smooth pale ashlar for the gate and walls, big bossed rubble for the
   Citadel tower across the breach. Add colour variation, black streaks under slits and gaps, and
   plants on the tops and in the joints.
8. **The 1898 breach as an open road gap**, bounded by the plain SE face of the gate (repair scar)
   and the Citadel NW tower with its box machicolations, red museum banners and row of flags.
9. **The passage interior**: one square chamber, pointed groin vault with round boss (crown
   ~6.5–7 m), 90-deg left turn, big polished floor slabs, the side niche with a slit.
10. **The open iron-plated door leaves** (grey-green plate grid, wicket door) inside both
    doorways, with the dense sticker layer on the lower part for the current period.
11. **Arrow slits with round oillets** and the scattered **stone roundels** on all faces.
12. **The inner face**: portal twin with big rosettes and volutes, the small crowned lantern-
    machicolation over the apex, and the ceramic tile signs ("JAFFA GATE / باب الخليل / שער יפו",
    the Omar Ibn el-Khattab Sq. street sign) plus the black heritage plaque.
13. **The Ramparts Walk building and its signage** right beside the inner doorway (blue entrance
    banners, purple blade sign, red awning), and the roof railing of the tower.
14. **Ground contrast**: small warm pavers with pale grid bands outside vs big worn grey-beige slabs
    in the passage and on the square.
15. **Small identity props**: the V-shaped cable lamp bracket on the SW face, CCTV and spotlights on
    the arch jambs, the ka'ak cart at the inner doorway, and the Architects' Tombs (turban finial)
    just inside. For night: crenel lights, the glowing yellow vault and the floodlit Citadel.
