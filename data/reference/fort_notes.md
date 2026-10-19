# Fortifications: modelling notes (blender/fortifications.py)

What the fortification builder takes from the reference notes (`gate.md`, `citadel_east.md`) and the
photos (`data/photos_ref/gate`, `data/photos_ref/citadel_east`, eval photos in `data/photos`), where
it deviates, and why. Local frame as everywhere: x east, y north, metres from the Jaffa Gate node,
z above the street (the outer plaza and the square are z = 0, the moat floor −5, the courtyard +1).

Comparison renders: `renders/fort/<view>_cmp.jpg` (photo left, model right, EEVEE, SW afternoon sun),
made with `blender/render_eval.py` on a scratch build and a fortification camera list (the eval poses
from `eval_cams.json` for passage, back_to_gate, inside_square, outside_gate, gate_outer, citadel_moat,
north_side; `passage_fix` is the passage pose moved back to (2.2, −5.4), see below).

## Construction rules (all objects)

- One planar polygon per wall face. Its top outline already carries the crenellation, and slits,
  windows and arches are holes in it (constrained Delaunay triangulation, no slivers). Every hole
  has reveals and a dark `void` back set at least 0.3 m behind the face.
- Corner merlons are single L-shaped tops shared by both edges, so merlon rows never overlap at
  corners. The audit shows 0 coplanar overlaps and 0 degenerate triangles for `jaffa_gate`,
  `city_wall` and `citadel`.
- Arrow slits are 0.14 m wide and end in a round oillet (keyhole), as in gate.md 1.7 and
  citadel_east.md A4. Each merlon carries a narrow slit.
- Materials: smooth `fort` ashlar on the gate and the walls (texture tile 2.7 m, so courses are
  ~0.55 m; vertex tint less orange than the raw texture, varied ±3 % per wall plane). The gate is
  paler and the Citadel greyer. Mouldings and panels use `ashlar`. The Citadel NW tower uses
  `rubble` (rough bossed blocks), the glacis slopes use `rubble`, and the counterscarp uses pale `ashlar`.
- Vegetation: only a few dry tufts on merlon tops. The wall capers and the wall-foot weeds come from
  `pipeline/dressing.py`. Nothing grows in the gate passage or on the vault.

## Jaffa Gate tower

- Height from the spec (13.0 m to the merlon tops). The merlons are 1.1 m tall, and the walk is 2.2 m
  below the merlon top. Merlons are plain and flat-topped, per face: NW 3 × 2.9 m with 0.6 m crenels,
  SW/SE 4 × ~2.2 m with ~0.5 m crenels, NE 4 × ~1.8 m with ~0.9 m crenels (gate.md 1.3).
- Outer portal (NW face, edge 0), gate.md 1.4 / s9:
  - moulded pointed frame 6.7 m wide outside and 5.2 m inside, springing at 4.9 m, apex 8.4 m
    outside and 7.7 m inside; it is a flat band with a roll moulding
  - volutes at the springing with rosettes (Ø 0.56 m) beyond them, and a keystone block
  - recessed tympanum with a cornice, and a 2.0 × 0.75 m three-line inscription panel centred at
    6.8 m between two roundels
  - flat doorway with rounded corners (3.6 × 4.9 m), a door frame, then a taller round/pointed
    passage arch.
  The inner portal (NE face) is a smaller twin: a moulded frame 5.0 m wide inside, a 0.6 m deep
  recess, a lower flat doorway (3.6 × 4.5 m, rounded corners), an inscription panel 1.6 × 0.6 m, and
  a small crowned lantern machicolation at 9.2–10.6 m.
- Behind both doorways the passage is a pointed barrel vault 4.4 m wide (spring 4.0, apex 6.5), so
  from inside the chamber you see, as in photo 053: a transverse pointed arch on pilasters on the
  chamber side, the pointed passage vault, then the lower flat doorway.
- The box machicolation over the outer arch is 1.5 m wide, projects 0.7 m and spans 9.9–12.8 m. It
  has three stepped corbels with dark drop-holes, a front slit, a dentil band, and a pyramid cap
  with a knob reaching ~13.75 m. There is one keyhole slit on each side of it, just below the merlons.
- SW face: two high slits, one roundel, and the old V-shaped floodlight bracket. SE face: one high
  slit and one roundel. Roundels are carved stone bosses in the wall's own stone, not pale discs.
- Chamber: a pointed groin vault (lighter `ashlar`) with diagonal ribs and a round boss. The wall
  arches are 6.8 m high and the crown is 7.5 m.
  - Back (SE) wall: a roundel at 4.5 m over a 1.5 × 0.5 m inscription panel.
  - Side (SW) wall: a pointed niche 1.6 × 2.5 m (sill 1.2 m, 0.8 m deep) with an arrow slit and a
    roundel above.
  - gate.md puts the blind-wall arches at ~5.5 m. They are 6.8 m here so that the passage vault
    (apex 6.5) fits under them and the door leaves clear it.
- Door leaves: two per doorway, 1.8 m wide, 4.6 m (outer) / 4.2 m (inner) high, 0.12 m thick,
  standing open ~86° against the passage walls. The passage is only ~1 m deep, so they reach into
  the chamber, as in photo g34.
  - Both faces use the grey-green plate-grid cell of the doors atlas (`door_olive`, falling back to
    `door_wood2`/`door_grey`), with iron edges.
  - The visible face has four iron straps with rows of rivet heads.
  - One leaf per doorway has the wicket door frame.
- Faces hidden by an abutting city wall (computed from the spec) get no rosettes or slits.

## City wall NW of the gate (spec entries `blind_arch_stretch`, `tall_stretch`, `wall_nw`)

- Each entry is a centre line (outside on the right) with its own height and thickness. At a joint,
  the taller or thicker entry closes the joint with a full end face and the other stops against it.
  At the gate corner, the wall stops flush with the gate face. There is no batter (gate.md 3.3: none
  where the wall meets the outer plaza). A spec key `"batter": true` enables a 0.3 m plinth.
- Crenellation by entry name (gate.md s9):
  - blind-arch curtain: merlons 1.2 m wide, 0.6 m gaps, 0.7 m tall
  - tall stretch: 3 merlons ~2.6 m wide, 0.55 m gaps, 1.1 m tall
  - long curtain: 1.6 m merlons, 0.45 m gaps, 0.75 m tall
  The walk is 1.1 m below the crenel sill, with an inner parapet. Optional `"merlons": {"w", "gap", "h"}`
  in an entry overrides this.
- Blind arch on the low curtain (gate.md 3.1):
  - 4.8 m wide, springing 4.4 m, apex ~6.8 m, 0.7 m deep, with a bench at its foot
  - carved capitals at both springings and a carved block above the apex
  - the stepped two-tier inscription (0.9 × 0.45 m over 1.8 × 0.6 m) and the white marble plaque
    (1.0 × 0.85 m) in the tympanum
  It is centred in the 5.5 m stretch, i.e. ~2.7 m from the gate end instead of ~3 m.
- Tall stretch: two keyhole slits at mid-height. Long curtain: keyhole slits every 5.5–7.5 m at ~5 m.

## Citadel

- Enceinte on the `mass` ring, wall_h 13 m (absolute z). Merlons are 1.7 m wide and 1.6 m tall with
  0.7 m embrasures, each with a slit. There are two staggered rows of keyhole slits, at ~7.4–8.9 m
  and ~3.7–5.2 m. The roof runs between the parapet and the courtyard, and the courtyard faces carry
  a blind pointed arcade.
- Moat (citadel_east.md A1–A3):
  - a 65° rough-stone glacis from z 1.5 at the wall face down to the moat floor, 3.0 m out
  - a pale ashlar counterscarp with a flat 0.4 m coping raised 0.15 m above the pavement
  - a black steel railing 1.1 m high: 60 mm posts at ~2.2 m, top rail, second rail 0.15 m lower,
    foot rail and round-bar baluster card
  The moat floor (lawn) is built by the ground builder.
- Entrance: the barbican's north face. It is detected as the furthest-east short moat edge facing
  north; `citadel.entrance_edge` overrides this. Following citadel_east.md A6:
  - a tall pointed recess (4.5 m wide, apex 6.5 m above the podium) with a moulded hood
  - a pointed doorway 2.4 × 3.5 m with studded olive-brown wooden doors (`door_wood` cell)
  - a smaller blind niche to its left and a black notice plaque
  - a corbel frieze under the merlons, and merlons with pointed caps and knob finials on the three
    barbican faces
  - a 1.7 m stone podium bridging the moat, with an arch over the moat floor, parapets and railings
  - a 9-step stair along the street edge with a handrail
- Phasael: the spec `towers` box named "phasael" (citadel_east.md A5).
  - The rectangle is clipped by every wall face that its centre lies behind and that it crosses: at
    most 0.4 m proud of the wall faces. With the current spec (centre (66, −23), 20 × 17, rot 24)
    the result is 14.0 × 17.0 m, its east face on the east moat and its north face ~3 m behind the
    north curtain. Total height is h + top.h = 24 m.
  - A ~70° stone skirt rises from the moat floor to 2.5 m.
  - Above it, a band of smaller ashlar with three small grilled windows.
  - Then Herodian drafted blocks from 6.0 to 15.5 m (≈ 9 courses of ~1.05 m, 1.5–3 m long, honey
    tint, projecting bosses).
  - Smaller masonry above, with two grilled windows ~8 m below the top, a slit, and two oculi near
    the top of the north face.
  - A low notched parapet with a steel railing.
  - The spec's set-back top storey, with its own railing and two Israeli flags at its SE part.
- NW corner tower across the 1898 breach (gate.md 4; spec `towers` "nw_tower", h 18, machicolations 3).
  A spec box tower whose centre lies in a corner lobe of the mass ring (4 consecutive vertices) is
  built on that lobe instead of its rough rectangle: currently ~13–20 m faces, 18 m to the merlons,
  0.36 m proud of the curtain faces. Without a spec tower, the lobe at the corner nearest the gate is
  raised 2 m as a fallback.
  - Rough bossed masonry (`rubble`).
  - Box machicolations with flat tops: 3 per face of 12 m or more, 2 per face of 7 m or more.
  - Keyhole slits.
  - A barred window and an oculus on the face towards the gate.
  Disable it with `citadel.corner_tower = false`. It is skipped automatically if a spec box tower
  stands in that lobe.
- Minaret (spec): a square base hidden inside the walls, a banded cylindrical shaft, a corbelled
  balcony with an iron railing, a lantern, and a pointed lead cap with a finial.

## Wall heights NW of the gate, measured on photo 062 with the eval pose

The eval pose of `outside_gate` (−27.25, −34.25, heading 50, pitch 13, vfov 44.4) puts the gate's SW
face corners B and C at x 422 / 683 px against 430 / 695 in the photo, and gives 12.9 m for the
gate's merlon tops (gate.md: 13.0). Measured the same way, i.e. foot and top rows with the wall's
distance, which the naive row ratios in gate.md leave out:

- tall stretch: merlon tops ≈ 16–16.5 m (spec 13.3), face ≈ 9 m wide, ~9.4–18 m NW of the corner
- low curtain with the blind arch: merlon tops ≈ 12.5–13 m (spec 10.8)
- blind arch: ≈ 5.3–5.8 m wide, apex ≈ 7.5 m, centred ≈ 5 m NW of the corner (spec stretch: 0–5.5 m)

The ~4 m north-west offset of the stretches may be partly a pose heading error. The heights hold
for any heading, because the camera looks at these faces almost head-on.

## Known deviations (data, not code)

- Eval pose `passage` (4, −4) stands ~1.9 m from the chamber wall. The photo's near-arch apex near
  the top of the frame and the doorway crown at 37 % from the top fit a camera ~4.3 m from the
  inner wall, ≈ (2.2, −5.4) (render `passage_fix`).

- Moat geometry. citadel_east.md puts Phasael's east face at x ≈ 72 and the glacis toe at x ≈ 76–78,
  so the moat lies outside the OSM outline. `make_spec.py` carves the 6 m moat inside it
  (mass = outline − 6 m). That is why every Phasael rectangle tried so far runs several metres over
  the moat and gets clipped. It is also why the moat reads narrower than in photo A19.
- City-wall centre lines end at the gate corner A, so half the wall thickness (1.6 m) covers the gate's
  NW face next to A. The photos show the whole 10 m NW face, with the wall's outer face meeting the
  tower at A (gate.md 3.1: the blind arch centre (1.3, 5.3) lies on the outer face). Shifting all
  CITY_WALLS points by (+1.12, +1.15), i.e. T/2 into the city, fixes this. It was tested: the code
  handles it unchanged, and the audit stays clean.
- The barbican is built at the enceinte height (13 m). The photos show it lower (~9–10 m to the
  merlon tops). The stair descends to the east because, in the spec rings, the moat corner west of
  the barbican's north face is where the photos put the bottom of the stair.
- The minaret is spec h 30 m. citadel_east.md A8 has it rising only ~8–10 m above the walls, which
  means h ≈ 22.
- The glacis capers (citadel_east.md A2: one per 2–4 m², the most recognisable texture from the
  square) are not placed by anyone now. That would be a dressing rule on the glacis band in front of
  the moat edges.
