# Haram al-Sharif / Temple Mount landmarks: reference notes

Builder: `blender/landmarks_haram.py` (registry `blender/landmarks.py`). Textures:
`pipeline/gen_landmark_textures.py` writes to `data/textures/gen/landmarks/`. Materials are in the
append-only block at the end of `blender/materials.py`.
Photos are in `data/photos_ref/landmarks_haram/` (keys **H:NN**; title, page, author, licence and date
for each are in `index.json` there).

Local frame: x east, y north, metres from the Jaffa Gate node. Levels come from the spec only
(`bd["ground"]`, `bd["edge_ground"]`), plus `data/terrain_street.json` for the street above Wilson's
Arch. The Haram is one flat at 737.07 m asl (local −33.51). The upper platform is built as a
solid, `PLAT_H = 5.1` m above it (terrain agent: 742.2 m asl, OS 1865 spots 2434–2439 ft, Warren
742.0).

Confidence: **H** means fixed by OSM geometry or by 2+ photos and a published figure; **M** means one
clear photo or a consistent estimate; **L** means inferred.

---------------------------------------------------------------------------------------------------

## 1. Dome of the Rock (w4709536)

| item | value | source | conf |
|---|---|---|---|
| plan | regular octagon fitted to the OSM ring: centre (734.42,154.05), circumradius 26.6 m, side 20.3 m (Creswell gives 20.59 m) | OSM w4709536 | H |
| orientation | one face normal at bearing ~352°. Portals on the four faces nearest the cardinal points: N 352°, E 82°, S 172°, W 262° | OSM; H:05/H:06 (S porch on the face with the long colonnade) | H |
| outer wall | 12.1 m to the parapet top: marble dado 0–4.9 m, tiled window zone 4.9–9.3 m, frieze zone 9.3–12.1 m (band of white cartouches + Ya-Sin inscription) | photo-matched view of H:05 (face 700 px = 20.3 m → 34.5 px/m at the face: dado 4.6, tiles 4.6, parapet 2.9 m); Creswell 9.5 m + 2.6 m parapet | H |
| bays | 7 arched bays per face: the 2 end bays blind, the 5 middle ones windows. That gives 36 windows in all, because the bay above each of the 4 doors is blind | H:04–H:06; Wikipedia "pierced by 36 windows" | H |
| drum | r 12.0 m (OSM part w291836699 r_eq 12.06 m), from the roof (12.6 m) to 21.8 m; 16 window bays (32 facets); a 2 m inscription band at the top; lead rim r 12.4 | OSM part; H:05 matched view (drum top ~1.2 m higher than the first estimate) | M |
| dome | gilded, base r 11.7 m on the rim at 22.15 m, slightly pointed (k = 1.02), apex 34.1 m above the platform; finial 3.6 m (pole, three balls, crescent) | H:05 matched view (dome/face width ratio 0.48; top at the same image height); OSM part height 34; Creswell dome 20.2 m inner diameter | M |
| porches | S and N: 8 marble columns (4 + 4) and 2 piers framing the central arch, 3.0 m deep, flat roof at 4.85–5.2 m with a dark timber fascia and a tiled soffit. E and W: 2 + 2 columns, 2.6 m deep. Tiled hood over each door, frame 3.8 m wide, apex 7.9 m | H:03, H:05, H:06, H:07 | M |
| doors | 2.6 × 4.3 m recessed 0.9 m, brass-plated leaves (faience `door_bronze`) | H:05 | M |
| roof | lead ambulatory roof from inside the 0.75 m parapet (11.3 m) up to the drum (13.3 m); not visible from the ground | Creswell section | M |

**Upper platform** (built by the DoR builder). The outline is OSM retaining wall w137725307 united
with the eight qanatir strips (23,086 m²). The top is paved, at esplanade + 5.1. The retaining
walls are ashlar and run down to 1 m below the esplanade, with a 0.32 m dressed coping. There
are no trees on the platform.

**Dome of the Prophet** (w291836680, 6 m², dropped from the spec by the area filter). Built by
the DoR builder at (709.55,174.84): 8 columns on r 1.75 m, pointed arches, drum, lead dome.

## 2. Qanatir / al-Mawazin (8 arcades: w748953239/246/248/252/257/254/265, w291841778)

* The footprints are the OSM strips (2.1–2.5 m deep, 10–18 m long) at the platform edge. The arcade stands on the strip centre line.
* End piers are 0.95 m wide; the marble columns between them have r 0.27 m. There are `round((L−2)/3.4)` pointed arches, 2–5 of them (SE: 3, matching H:14; W: 4, matching H:15). The arches spring at 3.8 m above the platform. The band runs to 6.8 m with a 0.28 m cornice. H:15 gives spring 3.8, apex 5.4 and top 7.0 m from a 1.7 m person (**M**).
* Only the piers and columns collide (`solid`). The arch band is `deco`, so the arcade is walk-through.
* The stairs run outward from the strip's outer long edge, as wide as the strip, with ~0.16 m risers and 0.34 m treads, 32 steps down 5.1 m (≈ 10.9 m run). OSM steps ways are 9.8–18.9 m long for S/SE/SW/E/W/NW, which matches. The N and NE ways are 3.7–4.0 m, because the real esplanade is higher in the north and the terrain flat ignores that, so those stairs come out longer than reality (**M**).

## 3. Dome of the Chain (w45099263)

* 11-sided outer arcade on the OSM ring (r 7.3 m → columns on r 6.85 m), 6 inner columns on r 3.0 m. The qibla side is centred south, with a mihrab panel between the two southern columns (H:13).
* Columns are 2.75 m; arches are pointed (k = 0.62), with tiled spandrels and a tile band (`chain_drum` / `tile_green`). The sloping lead roof runs up to a tiled hexagonal drum (r 3.45 m). The lead dome is r 3.15 m, k 1.15, with a gilded finial. The top is ~11.6 m above the platform. OSM gives height 9 / min_height 5 (**M**).

## 4. Al-Aqsa / al-Qibli (w280309331)

* Footprint from OSM (~80 × 55 m, with the women's mosque to the W and the east annex at the S end). The facade frame is the north edge, 55.5 m long, bearing 80°.
* North porch is 6 m deep, with 7 pointed arches between 1.6 m piers. The central bay is 7.3 m wide, springs at 5.0 m and has a raised parapet bay to 12.2 m. Side bays are 5.9 m and spring at 4.6 m. The porch is walk-in, with 7 wooden doors on the back wall. Crenellated parapet (H:10, H:11) (**M**).
* The hall walls rise to 10.6 m with a lead-covered roof (the aerial H:23 shows grey roofs). The long walls have a tall blind pointed arcade between pilasters, each bay holding a square lower window and a pointed upper window (H:10) (**M**).
* The central nave is 11.6 m wide, with a clerestory to 13.0 m and a lead gable roof (ridge 15.2 m). The north gable has two arched windows (H:10) (**M**).
* The transept block under the dome is 15.2 m square and 15.4 m high. The drum is r 7.0 m, 15.2–19.0 m, with 24 arched window bays. The lead dome is r 6.8 m, pointed k 1.25, apex ~27.6 m, with a gilded finial. Dome position from OSM part w291844838 (r_eq 7.2 m) (**H** position, **M** heights). OSM height 35 is probably to the finial from the lower ground at the south.

## 5. Western Wall (w817206833), Wilson's Arch hall (w499210296)

* The plaza faces are the edges whose edge_ground is more than 2 m below the record ground: the two west-facing segments (646,35)→(652,−2)→(656,−23).
* Height is 19.0 m above the prayer area (Wikipedia: ~19 m / 28 visible courses). The terrain has the prayer area at 727.0 asl, so the top is at 746 asl, ~9 m above the esplanade, which matches the west portico's roof behind it (**H**).
* Courses: 7 Herodian courses of ~1.14 m with drafted margins (`herodian`, 8 m texture tile aligned to the plaza level) up to 8.0 m. Above them, set back 0.12 m: Umayyad/early courses to 12.2 m, then Mamluk/Ottoman small courses (`fort`, two tints) (H:27–H:31) (**M**).
* Capers on the joints, ~1 per 4.5 m (H:31). The parapet is on the top.
* The Haram side (east face) is the back of the west portico: a blind pointed arcade with dark 1.6 m recesses.
* Wilson's Arch hall: footprint from OSM, floor at the prayer-area level. The south front has the end of Wilson's Arch (span 12.8 m, semicircular, springing at +1.6, apex +8.0 m; Wikipedia gives 12.8 m span) next to the Wall, plus two smaller arches. A barrel vault runs 15 m north. The flat roof sits at the Chain Street level sampled from terrain_street (≈ −33.9). The main session has cut a ground hole over the footprint (GROUND_HOLES).

## 6. Golden Gate (w291836693)

* Footprint from OSM, 27 × 17 m. It is clipped at the inner face of the circuit wall (nearest walls_generic segment; `landmarks_gates.WALL_LINE` = "outer", so the OSM line is the wall's outer face).
* Roof at esplanade + 7.0 with a low parapet. Two low stone domes on drums at the OSM parts w291836700/701 (r 3.0 / 2.6) (H:24, H:26) (**M**).
* West front: two broad round arches with double archivolts springing ~1 m above the esplanade. Inside them are tympana with walled-up doorways (green grilles) at the court floor (H:24, H:26).
* Sunken court: the main session's SUNKEN box (884,249)–(892,266) at esplanade − 4.5. I built the retaining walls, coping, iron railing and a central stair flight down from the west (H:24, H:25).
* East front (outside, H:22, H:08): a relief block 1 m proud of the wall's outer face up to the wall top. It has two blocked arches springing 6.2 m above the outside ground, walled-up pointed doorways at the foot, three bosses and a round boss (the oculus) up top.

## 7. Minarets (hung off nearby landmarks so they get an LOD)

| minaret | position | height | form | host | conf |
|---|---|---|---|---|---|
| Bab al-Silsila | OSM node 13791836098 (640,84). Wikidata Q53535830 puts it 15 m further N; OSM was kept, ~10 m N of the Chain Gate | 35 m (Wikipedia) | square, string courses, gallery on muqarnas corbels, broad timber canopy, cylindrical drum, lead dome (H:19) | Western Wall | M |
| al-Fakhriyya | OSM node 13792233802 (687,−82), SW corner | ~23.5 m (unpublished; from H:17 proportions) | square shaft, mouldings, muqarnas balcony, square chamber with lattice, canopy, small lead dome (H:17) | Al-Aqsa | M/L |
| al-Ghawanima | Wikidata Q25450229 (587.23,370.77), NW corner | 38.5 m (Wikipedia) | wide square base storeys, square shaft with string courses, gallery + timber canopy, octagonal turret, bulbous dome (H:20) | Dome of the Rock | H position, M form |
| Bab al-Asbat | Wikidata Q6863203 (840.23,398.60), north wall | 28.5 m Ottoman + raised in 1927 → 30.5 m | rectangular base, cylindrical shaft, balcony, narrower upper shaft, pointed lead cap (H:18) | Dome of the Rock | M |

The base runs 6 m below the esplanade, hidden where the ground is higher. Silsila stands partly
inside the generic Madrasa al-Ashrafiyya block, and Fakhriyya inside the Islamic Museum block.

## 8. Other Haram buildings (item 7)

* **Riwaq** builder (porticoes / madrasa ranges along the N and W sides: w291836727, 706, 724, 735, 712, 721, 708, w508175933, w620130981, w291836726, w291836720). The pointed arcade faces the esplanade: 4.2 m bays, springing 3.6 m, 3 m deep recesses with paved floors. The upper storey has small arched windows. Flat roof at 9.5 m, replacing the generic 15 m shop-house facades (H:18).
* **Haram gates** (Chain, Cotton Merchants', Iron, Council, Watchman, Darkness, Remission, Tribes, Ablution, East, Mughrabi): 9.5 m blocks with a tall pointed portal recess and closed wooden leaves on the two faces most aligned with the Haram centre.
* **Wall strips** (OSM building=wall along the E and S walls: w1080613977, w620099942, w508175930/931/932, w291836729, w620099941): plain mass, 0.3 m below the circuit wall's top.
* **Islamic Museum** (w291836691): two-storey Mamluk range, 9 m, two rows of arched windows. The Fakhriyya minaret rises above it.
* **Small domes**: Dome of the Ascension, Dome of the Tablets (open kiosks on the platform), Dome of al-Khalili (closed, on the platform), Dome of Suleiman Pasha, Dome of Solomon, Dome of Musa and three unnamed octagonal qubbas (closed, lead domes), Dome of Yusuf (open), **Sabil of Qaytbay** (square base with grilled windows, drum, carved stone dome, 13 m).

---------------------------------------------------------------------------------------------------

## Model checklist

- [x] DoR octagon, bays, frieze, porches, drum, gilded dome, finial; photo-matched to H:05
- [x] Upper platform, retaining walls, coping, 8 stairways, 8 qanatir (walk-through)
- [x] Dome of the Chain (11 + 6 columns, mihrab, drum, dome)
- [x] Al-Aqsa porch (walk-in), blind-arcade walls, nave gable, transept, drum, lead dome
- [x] Western Wall plaza face (Herodian + later courses, capers), portico back, parapet
- [x] Wilson's Arch hall front, vault, roof at street level
- [x] Golden Gate: west front, roof domes, sunken court, east relief
- [x] Four minarets
- [x] Riwaqs, gates, wall strips, museum, small domes, Sabil of Qaytbay
- [ ] Summer pulpit (minbar of Burhan al-Din) by the south qanatir; Dome of the Spirits / al-Khidr (not in OSM)
- [ ] Al-Kas fountain (OSM w291836683 is not a building; it would need a prop or a ground feature)
- [ ] The N/NE stairs are too long because the terrain flat ignores the higher northern esplanade

---------------------------------------------------------------------------------------------------

## Build status (2026-10-20)

Triangle budgets (hi / LOD), measured by calling each builder on its spec record:

| landmark | hi | LOD | budget hi / LOD |
|---|---|---|---|
| Dome of the Rock, with platform, Dome of the Prophet, Ghawanima + Asbat minarets | 7,531 | 721 | 45k / 1.5k |
| Al-Aqsa, with the Fakhriyya minaret | 13,152 | 210 | 25k / 1.5k |
| Dome of the Chain | 2,433 | 171 | 25k / 1.5k |
| Western Wall, with Wilson's hall and the Silsila minaret | 1,944 | 146 | 25k / 1.5k |
| Golden Gate | 1,522 | 90 | 25k / 1.5k |
| each qanatir arcade with its stairs | 404–680 | 82–138 | |
| all 54 Haram builders | 59,655 | 3,593 | |

Geometry audit (`blender/audit.py` on build/s11_haram.blend with the LOD and props removed): 13
coplanar overlaps, 1.1 m² in all. 0.26 m² of that is mine (Dome of Yusuf, tiny column caps); the
rest is generic buildings (w291836734, w291836694). The worst single overlap of mine is 0.04 m².

Photo comparisons: `renders/landmarks/haram/compare/*.jpg` (render left, photo right), with the
single renders in `renders/landmarks/haram/`.
