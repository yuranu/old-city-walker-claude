# City gates (all but Jaffa Gate): reference and model notes

Model: `blender/landmarks_gates.py` (registry entries + `build_walls` for the wall circuit).
Local frame as in `hero_edges.md` (x east, y north, metres from the Jaffa Gate OSM node).

**Photos.** `data/photos_ref/gates/` (95 Commons photos, 1280 px; title, page, author, licence, date, lat/lon
and local x/y in `index.json`). Keys: GD = Damascus, GH = Herod's, GZ = Zion, GU = Dung, GN = New Gate.
Other sets: `s08_damascus` D:nn (see `s08_damascus.md` §3, measured there on D:12), and `s10_herod_lions` R:nn
(Lions' Gate R:01–R:10).

**Confidence.** **H** = seen clearly in 2+ photos or fixed by OSM geometry. **M** = one clear photo or a
consistent estimate (people 1.7 m, doors). **L** = inferred.

**Heights.** All heights are above the gate's OUTER threshold, which is local z = 0 in the builders and equals
`edge_ground` of the outer face. make_spec's `GATE_DOORS` samples that 1 m outside the OSM door point.

---------------------------------------------------------------------------------------------------------------

## Conventions shared by all gates (implementation)

- **Anchors.** Doors and passages are anchored on OSM points: passage ways, gate nodes, door nodes. The builder
  finds the footprint edge under each point (`find_edge`), so small changes to cleaned rings do not break it.
  The **(a, b) frame** has its origin at the outer door, a pointing inward across the wall and b = a rotated +90°.
- **Passage.** Outer portal → groin-vaulted hall(s) → inner portal. The floor is a plane through the two
  thresholds; side passages ramp to the street level of their own face. Opening outlines reach 0.6–0.7 m below
  the lowest threshold, so ramps never open a slit under the walls.
- **Portal kit.** Generalised from `fortifications.portal`. Pointed recess with a moulded band and keystone,
  tympanum panel, doorway (flat lintel / segmental / pointed), door frame, rebate, passage tunnel. Open
  iron-plated leaves use `fortifications.gate_leaf` with the doors-atlas plate cell.
- **Massing.** `fortifications.battlemented_ring`: one planar face per edge with all openings as real holes,
  parapet, merlons with slits, walk-level roof. Stone is "fort" with plane tints (`tint_planes`), carved parts are
  "ashlar". Small ornaments go to the nocol "deco" builder.
- **Walkability** was tested with ray casts (capsule r 0.35, h 1.75; floor under every 0.25 m step, head room
  ≥ 1.9 m, ≥ 0.4 m side clearance). Every main and side passage passes. The narrowest clearance is the side
  passages, 0.7 m either side of the path. The lowest head room is Dung, 3.4 m.

---------------------------------------------------------------------------------------------------------------

## 1. Damascus Gate (Bab al-Amud), w616186088, sector s08 (`damascus`)

**OSM plan (H).** Taken from `s08_damascus.md` §0/§3.1 and the footprint.
- In the gate frame the ring is rectilinear:
  - west tower a −6.1…2.7, b −21.9…−9.4, front 12.5 m;
  - central screen front at a = 0, from b −9.4 to 10.4 (19.8 m);
  - east tower a −5.8…−0.5, b 10.4…23.7, front 13.3 m;
  - inner face at a = 11.15.
- The towers project ~6 m. The gate faces NW (317°).
- The OSM passage is a shallow zig-zag: from the outer door (265.8,558.2) the inner door (275.4,551.8) lies
  11.15 m deeper and 2.9 m to the NE.
- The side passage w616338411 leaves west to the SW notch at (262.4,548.7).

**Heights and openings.** M, from s08 §3.2 (measured on D:12) unless noted.

| item | model | source |
|---|---|---|
| screen merlon base / gable apex / finial tips | 14.0 / 15.2 / ~16.2 m | s08 §3.2 (M) |
| towers | +0.5 m (14.5 / 15.7 / ~16.7) | s08 §3.2 (M), GD:10/15/16 |
| outer doorway | flat lintel 4.0 × 5.2 m | s08 §3.3 (M) |
| outer pointed recess | 5.0 m inner + 0.5 m moulded band, springing 6.5, apex 9.2, 0.9 m deep | s08 §3.3 (M) |
| window | 1.1 × 2.0 m, sill 11 m, open to the sky through the screen | s08 §3.4, GD:06, GD:20 (H) |
| inner block behind the screen | solid parapet at 9.65 m (≈ 11.4 m above the inner street) with a railing; roof terrace at 8.4 m | s08 §3.7–3.8 (M) |
| inner portal | pointed recess 6.4 m, springing 5.6, pointed door 4.6 m, all relative to the inner threshold (1.8 m lower) | s08 §3.7, GD:21 (M) |
| hall | 7.1 × 8.7 m groin vault, springing 5.6, crown ~7.9 m, whitewashed | s08 §3.6 (L/M), GD:26 |

**Modelled.**
- **Four masses.** Two towers, the outer screen and the lower inner block (`clip_half` in the gate frame).
- **Screen front.**
  - Recessed portal with the tympanum inscription panel and keystone.
  - Window panel with colonnettes, capitals, joggled lintel, cusped frieze and palmette band.
  - Raised central crown with finial.
  - Two corbelled bartizans on the parapet.
  - Carved rosettes at the arch haunches, plain discs, slits at two levels.
- **Towers.** Box bartizans on corbels at the inner corners of both tower fronts (s08 §3.5; GD:10, GD:15, GD:16);
  slits, discs.
- **Merlons.** Pointed merlons with tall spade finials everywhere except the screen's back face.
- **Inner face.** Big moulded pointed arch, three small rosettes over the apex (s08 §3.7) and a railing on the
  terrace.
- **Passage.** Outer portal with iron-plated leaves → one hall that takes the 2.9 m jog → inner portal with
  leaves. The covered side passage runs west to the inner court as a 2 m vaulted corridor ramping to its street.
- **Budget.** 7.6k tris (budget 35k), LOD 0.85k.

**Remaining differences.**
- The bridge w616383626 and the excavated Roman-gate trench under it are not built. The spec ground currently
  has a hole in front of the door.
- Not modelled: ivy (2023+), Ramadan lights, the shops and canopies in the hall, the police kiosk, the
  pitted/honeycomb weathering, the double archivolt of the inner arch.
- The hall's octagonal oculus (GD:26) is a boss.
- The merlons' stepped tops are simplified to gable + finial.

## 2. Lions' Gate (Bab al-Asbat), w288395731, sector s10 (`lions`)

**OSM (H).**
- Footprint ~12.6 × 10.2 m. The east face is the outer face; the OSM wall line runs exactly along it.
- Passage w288395746 (sett) runs straight E–W from (893.6,468.0) to (882.4,466.3); the inner door point lies
  1.1 m outside the west face.
- Side passage w291836745 runs from the south face (889.5,461.2) to El-Ghazali square.

**Heights** (M, measured on the frontal photo R:07 at ~56 px/m, face width 12 m):

| item | model | photo |
|---|---|---|
| merlon base / top | 12.9 / 13.9 m, flat merlons ~1.9 m with 0.5 m crenels (5 across the face) | R:07, R:04 (H for the count) |
| central crown | ogee-like finial rising to ~15 m | R:07 |
| outer recess | pointed, 4.6 m wide, springing 5.2, apex ~7.7, moulded band | R:07 |
| doorway | 3.3 m wide, segmental head at 4.1 + 0.55 m | R:07 |
| lion reliefs | two confronted pairs at z 6.5–7.2, centred 3.65 m either side of the door, each lion ~1.3 m long | R:07, R:02 (H) |
| machicolation | 2.2 m wide box, 10.1–12.2 m, three corbels | R:07 (H) |
| shell niches with lion-mask bosses | u ± 3.6 m, 10.7–12.2 m, roundels below | R:07 (M) |
| inner arch | open pointed arch 5.0 m wide, springing 4.7, rise 2.9, moulded band | R:06 (M) |

**Modelled.**
- Straight passage: portal with open studded leaves (R:01, R:05) → groin-vaulted hall (R:05/R:06 show the
  yellow-washed vault) → big open inner arch.
- Side door to El-Ghazali square with a ramp.
- Rosette under the machicolation, central crown, slits.
- **Budget.** 3.2k tris, LOD 0.2k.

**Remaining differences.**
- The lions are box-relief silhouettes, not carved.
- No signage, CCTV, the green sun-shade canvas (R:04) or crowd barriers.

## 3. Zion Gate (Bab an-Nabi Daud), w290671706, sector s02 (`zion`)

**OSM (H).**
- Footprint 15.2 × 12.2 m, inside the wall line. The south face is the outer face and lies on the OSM wall line.
- Passage w722675054 is L-shaped: outer door (198.4,−418.2) in the south face, 4.7 m from its west corner →
  north to the turn (200.5,−411.6) → east to the inner door (210.7,−415.7) in the east face.

**Heights and openings** (M, from GZ:09, GZ:11, GZ:15, GZ:16, GZ:05, GZ:06, GZ:10):

| item | model | photo |
|---|---|---|
| tower merlon base / top | 13.0 / 14.0 m (the block stands ~2 m above the curtain) | GZ:15, GZ:16 (M) |
| outer recess | pointed, 4.2 m wide, springing 4.5, moulded band | GZ:05, GZ:11 |
| outer doorway | flat lintel 2.9 × 4.0 m on stepped (muqarnas) corbels | GZ:10 (H) |
| decorative niches | shell-hooded pointed niches 1.25 m wide, 1.7–4.2 m, a slit in the back; right of the door at +3.7 m and left at −3.2 m | GZ:09, GZ:11 (H right, M left) |
| machicolation | 1.8 m box over the door at 8.5–10.7 m on carved corbels | GZ:05, GZ:06 (H) |
| bullet scars | ~190 small dark chips over the outer face | GZ:09, GZ:11 (H) |
| inner door | flat lintel 3.0 × 3.9 m in a shallow recess, two small windows high up | GZ:16 (M) |

**Modelled.**
- L-shaped passage: outer portal → groin-vaulted corner hall → transverse arch → groin-vaulted second cell →
  inner portal. Stone vaults as in GZ:13; no leaves.
- **Budget.** 3.4k tris, LOD 0.25k.

**Remaining differences.**
- Not modelled: the stair to the ramparts inside (GZ:19), the plaque and mezuzah, and the Harel memorial
  outside.
- The niches' carved hoods are simplified ribs.

## 4. Herod's Gate (Bab az-Zahra), manual record m_herods_gate, sector s10 (`herod`)

**Plan (H).**
- Not a building in OSM. The gate is the projecting tower of wall way 137726904, vertices 50–53:
  (586.8,704.2) (585.5,709.0) (574.7,706.1) (576.1,700.7).
- The record extends it 3.5 m back to the curtain's inner face (`HEROD_RECORD`, added to MANUAL_BUILDINGS).
- The tower front is 11.2 m and projects ~5 m.
- **Entrance.** Today it is in the north face of the tower; the Ottomans opened it in 1875. The passage runs
  straight south into the city: GH:16 shows a long straight vaulted passage looking out. The camera geometry of
  GH:08 (567,725) and GH:14 (563,714) puts the door on the lit north face.
- The original entrance in the east flank is blocked (GH:18 left face, GH:15/GH:17).
- So the brief's "side-facing entrance, bent passage" describes the pre-1875 gate; the model follows the
  photos.

**Heights and openings** (M, GH:01, GH:09, GH:14):
- **Tower.** Merlon base 14.1, top 15.2 m, standing 1.5–2 m above the adjacent curtain.
- **Outer door.** Pointed, 3.0 m wide, springing 3.0 (apex 4.6), in a 3.7 m pointed recess with a moulded hood.
- **Above the door.** A small barred window at 7.6–8.8 m, a roundel above it at 10.9 m (GH:09), slits at 9–10.5 m.
- **Blocked east entrance.** Pointed niche 2.6 m wide, two carved rosettes above it (GH:15, GH:17).
- **Inside.** A groin-vaulted hall with a boss; GH:04 shows an octagonal oculus. Open pointed arch to the city.
- **Budget.** 2.5k tris, LOD 0.2k.

**Remaining differences.**
- The steel stair up the east flank (GH:12, GH:18) and the shops in the passage are not modelled.
- The oculus is a boss.

## 5. Dung Gate (Bab al-Maghariba), w1545285986, sector s07 (`dung`)

**OSM (H).**
- Footprint 4.2 × 2.3 m, which is the roof of the opening, on wall way 391433911 at gate node 29944308.
  The road runs N–S through it.
- The builder makes a 16 m crenellated section of the curtain along the OSM line, with the same profile as
  `build_walls`, the opening and both faces dressed.

**Openings** (M, GU:08, GU:09, GU:13, GU:14):
- **Opening.** Widened in 1952: 4.2 m wide, jambs 3.7 m, segmental head to 4.4 m. Dressed frame band and jamb
  strips on both faces.
- **Above it** (outer face, GU:09 H): the small Ottoman gate's carved pointed arch, reset over a moulding at
  5.0 m. Arch 2.7 m wide, apex ~7.3 m, cusped tympanum, rosette at ~7.6 m.
- **Height.** The section's top follows the circuit rule: inner street + 11.5 m wall + 0.85 m merlons.
- **Budget.** 0.8k tris, LOD 0.18k.

**Remaining differences.**
- Not modelled: the guard booth (GU:08/09), barriers and signs.
- The spec ground has holes on both sides of the opening.

## 6. New Gate (Bab al-Jadid), w1393450805, sector s03 (FORCE_SECTOR) (`new`)

**OSM (H).**
- Footprint 8.4 × 3.7 m on wall way 391433919 at gate node 561085431, built 1889.
- The builder makes a 17 m section along the OSM line (direction reversed so the outside, NNW, is on the right).

**Openings** (M, GN:02, GN:04, GN:05, GN:07, GN:12):
- **Opening.** Broad four-centred arch 4.2 m wide, springing 3.7, crown ~5.3 m.
- **Frame.** On both faces, rough bossed rusticated voussoirs (11, alternating long and short) and alternating
  jamb quoins (H).
- **Merlons.** Flat, 1.4 m with 0.7 m crenels (GN:07, H).
- **Budget.** 0.9k tris, LOD 0.2k.

**Remaining differences.**
- Not modelled: the plaque, the street signs, and the caper plants on the voussoirs (GN:12).

## 7. Golden Gate

Skipped; the Temple Mount agent owns it.

---------------------------------------------------------------------------------------------------------------

## Wall circuit (`build_walls`, wired by build_city --part base through landmarks.walls_builder)

**OSM line = outer face (`WALL_LINE = "outer"`).** At Lions', Zion, Damascus (the tower fronts) and Herod's
Gates the OSM city_wall line runs exactly along the gates' outer faces. Each run of `walls_generic` is moved
thick/2 inwards, with joints on the intersections of the moved lines, including where two runs meet. With
centred slabs the curtain stood 1.5 m proud of the Lions' and Zion facades.

**Gate cuts (`GATE_CUTS`).**
- The cut areas are the convex hulls of the gate footprints, so nothing stands in the recess between the
  Damascus towers, plus the Dung and New Gate sections.
- A slab running along a hull side, nearly parallel and closer than half its thickness, is dropped.
- A cut end is bisected to < 1 cm and mitred flush with the gate face it meets.

**Profile.** As at the gates (`fortifications.wall_run` profile):
- outer face with the parapet;
- merlons 1.6 m, crenels 0.45 m, merlon height 0.85 m;
- an arrow slit in every third merlon;
- walk 1.1 m under the crenel sill and a low inner parapet.

Steps in the terrain-following top get full end faces on the taller side.

**Gaps.** Short gaps (< 6 m) between consecutive segments are bridged. make_spec's de-duplication drops the
4–5 m tower flanks.

**Budget.** ~50.6k tris for 442 segments (the old box walls were ~36k).

**Audit.** 7 coplanar overlaps totalling 0.8 m², at three very sharp corners: the Haram SE corner, where a 2 m
segment has z1 19 m below its neighbours, and the tiny 2.3–2.5 m tower flanks at (901,385).

**Remaining.**
- Generic towers are hollow U-shapes. The OSM traces their outline and nothing fills them.
- Buildings drawn against the wall overlap the inward slab. make_spec should clip footprints against the slabs.

## Model checklist (next passes)

1. The Damascus bridge, Roman trench and kiosk, once the terrain carves the trench.
2. Fill generic wall towers: detect U-shaped OSM projections and build them as battlemented boxes.
3. Shops, canopies and lights in the Damascus hall; the steel stair at Herod's Gate; Ramadan lights.
4. Carved detail by texture rather than geometry: lions, shell niches, pitted stone at Damascus and Zion.
