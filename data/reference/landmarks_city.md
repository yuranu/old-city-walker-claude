# Skyline landmarks inside the walls (outside the Temple Mount): modelling reference

Builder: `blender/landmarks_city.py` (registry `LANDMARKS`, plugged in by `blender/landmarks.py`).
Photos: `data/photos_ref/landmarks_city/` (index.json: Commons title, page, author, licence, date,
camera/object coordinates when tagged; restore with `pipeline/fetch_ref_photos.py`). File prefixes:
`hs_` Holy Sepulchre, `red_` Redeemer, `hurva_`, `sav_` St Saviour, `omar_`, `khanqah_`, `sidna_`,
`minaret_`, `tif_`, `james_`, `anne_`, `ecce_`, `flag_`, `christ_`, `cocat_`, `nevsky_`, `seph_`.

Local frame: x east, y north, metres from the Jaffa Gate node. **Heights are relative**: every
builder measures from the spec record (`bd["ground"]`, or the edge ground of the facade edge for
the Holy Sepulchre parvis) and walls start at `bd["base"]`; no absolute z is hard-coded. Plan
positions of hand-placed parts (domes, towers, minarets) come from OSM building:part ways or nodes.

Confidence: **H** = OSM geometry or 2+ clear photos; **M** = one clear photo / consistent estimate
(people 1.7 m, doors 2.2 m); **L** = inferred.

## 1. Church of the Holy Sepulchre — w1022672085 (s04_sepulchre)

Massing is a set of height zones over the spec ring (convex boxes clipped from the ring; every
zone a closed prism from the base), heights above the parvis (facade edge ground):

| zone | box (x, y) | height | source / conf. |
|---|---|---|---|
| west strip along Christian Quarter Rd | x < 170 | 15 | Greek Patriarchate blocks, L |
| SW block, south part (St Helena Rd) | 170-204, y < 162 | 9 | photo omar_06 (low SW corner of the parvis), M |
| SW block (Patriarchate), behind the tower | 170-204, 162-183 | 13 | OSM part 1022663516, L |
| rotunda wrap | 170-204, y > 183 | 19 | OSM 1022663520 height 20, M |
| west parvis chapels, St James | 204-215, y < 162 | 8 | omar_06, hs_12, M |
| west parvis chapels, St John (big niche, dark block) | 204-215, 162-174 | 12 | hs_05..07, hs_12, M |
| Forty Martyrs | 204-215, 174-facade line | 8.8 | hs_10 (rounded top ~8.5 m), M |
| south transept facade block | 204-224.2, facade line-191 | 20.3 | hs_10 (top cornice 19.4-20.3, railing), M |
| Chapel of the Franks | 215-224.2, south of the facade line | 11.6 | hs_10 (cornice 11.0-11.6), M |
| east of the parvis (Greek/Coptic chapels) | 224.2-241, y < 191 | 12 | hs_12, L |
| katholikon | 204-228, 191-222.5 | 24 | OSM 1022663526 height 24, H |
| ambulatory | 228-241, 191-222.5 | 15 | L |
| north range (Franciscans) | 204-241, y > 222.5 | 16 | L |
| Coptic patriarchate | 241-270, y < 188.6 | 11 | L |
| Deir es-Sultan roof court | 241-270, y > 188.6 | 7.5 (paved) | hs_05/06 Deir photos, L |

Parts (positions OSM, dimensions):
* **Anastasis rotunda dome**: OSM 1022663528 (centre 187.5, 203.4; extent 23 m; min_height 20,
  height 34, dome 10 m). Built: 32-sided drum 18.7-25 m with 16 small arched windows, dressed
  cornice, ribbed lead dome r 11.7 rise 0.84 (36 ribs) to the oculus ring r 2.1 at ~34.6 m, lead
  collar + low cone (lantern), gilt cross to ~38.8 m. Rotunda top above the katholikon top
  (hs_08: it shows higher although farther). H/M.
* **Katholikon dome**: OSM 1022663527 (centre 210.8, 208.3; ~13 m; min 24, height 34). Built: 24-sided
  drum r 6.0, 24-28.3 m, 12 arched windows, two bands; ribbed lead dome r 6.2 rise 0.8 to ~33.3 m,
  knob and cross 2.8 m. H/M.
* **Apse** of the katholikon (OSM 1022663525, height 23): half 9-gon r 7.4 at (227.5, 210.5),
  14.7-22 m, arched windows + oculi, cornice (hs_03_90785852). M.
* **Bell tower**: OSM 1022663529 (x 193-205, y 172.6-184, height 30, pyramidal roof 4 m). Built as a
  10.5 m square shaft with its NE corner at (204.3, 183.75) aligned with the facade, walls from the
  parvis chapels' roof (8.6 m) to 26 m; cornices at 15.6 and 20.5; one arched window per face on the
  middle storey, a pair of large arched openings with sills on the top storey, low tiled pyramid
  (2.2 m, eaves 0.9 m), flag pole. Position/orientation checked against hs_08 (from the Redeemer
  tower: rotunda 8 deg right of the tower, katholikon 19 deg right — matches) and hs_12. H/M.
* **South facade** (ring edge (204.1,183.1)-(218.4,184.3), 15 m, faces 176 deg; photos hs_07, hs_10):
  portals 1.65-6.95 and 7.55-12.85 m along the edge, three stepped pointed orders (0.38 in, 0.33 deep),
  springing 4.5 m, apex 8.3 m, colonnettes in the re-entrant corners, hood mouldings, lintel at
  4.4 m; left doorway 2.8 x 4.4 m open and dark with the two wooden leaves folded back, right
  doorway walled up; recess floors paved. Cornice 9.95-10.85 m. Upper storey: round-arched recesses
  r 2.45 (spring 15.5) with two orders, windows 1.3 x 3.15 m (sill 12.4) glazed with grilles, inner
  colonnettes, four columns on the cornice. Top cornice 19.4-20.3 m + iron railing. **Immovable
  ladder** on the ledge under the right window (wood). **Stair** to the Chapel of the Franks: 9 steps
  along the facade (u 12.95-14.98, 1.9 m out, rise to 2.2 m; OSM way 1547245013, photo hs_04). M.
* **Chapel of the Franks** (ring edges (218.4,184.3)-(218.7,179.1) and -(224.2,179.5)): west face with
  the glazed iron-grid door at the stair head; south face with door and small window, string course
  at 5 m, large round-arched glazed window 3.2 x 4.5 m between marble colonnettes, cornice at 11 m;
  small ribbed lead dome on a drum (top ~14.7 m). Wall above with the third arched window. M.
* Parvis walls: St John chapel wall with the elevated deep round niche (spring 6.6 m) and the dark
  masonry block below it, St James door, Forty Martyrs window, east side with the pointed green door
  (Ethiopian/Coptic chapels), small barred windows on St Helena Rd. M/L.
* **Deir es-Sultan**: St Helena's chapel dome (OSM 1022663497, (253.9, 207.9), r 3.35): 12-sided drum
  2.4 m with 6 arched windows, rough brown stone dome rise 0.72 (photos hs_01/02_Helena); six
  whitewashed monks' cells with green doors and low domes. M.
* Small dome OSM 1022663502 (177.2, 182.4, height 22, dome 2 m). White canvas roofs over the courts
  east of the parvis (aerials hs_06/07/08). M/L.

## 2. Lutheran Church of the Redeemer — w29268902 (s04)
* Tower: OSM w375040918 (building:part, man_made=tower) at the SW corner (x 265.1-272.5, y 133.7-139.4);
  viewpoint node 9840842282. Built as a 7.4 m square, outer faces 0.2 m proud of the church walls;
  string courses 11 / 22 / 30 m, belfry 30-37 m with paired arched openings, corbel cornice, stone
  spire 10.5 m with four corner pinnacles, ball and cross: ~50 m. Photos red_04_*, red_06/08, hs_03
  (skyline from the Citadel matches: tower right of the domes, spire). M.
* Church: cross plan from the ring (nave x 265-290.8, crossing/transepts 290.8-299.4, apse > 299.4);
  walls 13.5 m with round-arched windows; north transept front on Suq ed-Dabbagha with a rose window
  and round portal (red_03); tiled gable roofs (rise 3.6) over nave and transepts; octagonal drum
  with arched windows and ribbed lead dome r 4.2 over the crossing (295.1, 140.15), cross ~27 m;
  apse flat-roofed at 11.5 m (L: the real apse has a half-cone roof). M.

## 3. Hurva Synagogue — w45081545 (s06_jewish)
* OSM ring 36 x 22 m with height 3 = podium (rubble face, paved top at 3 m). Body: OSM part
  546355656 (20 x 18, h 16) and dome part 372306586 (16 m, h 24, roof 9). Built: 19 m cube centred
  (363, -145), 3-15 m, on each face a great round blind arch (spring 7.4, crown ~13.5 m) with two
  rows of three arched windows and a trefoil of oculi, dressed hood, cornice; four 2.8 m corner
  turrets rising 2.7 m above the cornice with small finials; 24-sided drum r 6.4 (15-19.6 m) with 12
  arched windows, balcony band with iron railing (r 7.5), white dome r 6.9 rise 0.95 (~26 m above
  the plaza). Photos hurva_03_10591123, hurva_08, hurva_02_8333697. M.
* **Sidna Omar minaret** (no OSM node): placed at (354.6, -157.3), NW corner of w1394070804 (the small
  mosque beside the Ramban synagogue, just S of the Hurva). Square shaft 3.4 m to 16.5 m, corbelled
  balcony with parapet, round upper stage 3.8 m, small lead dome, crescent (sidna_02, hurva_03_36769466,
  hurva_05). Built by the Hurva builder. L for the exact position (photos show it SW of the Hurva).

## 4. St Saviour — church w106249447, monastery r1515591 (s03_christian_w)
* Tower at (-3.6, 250.4) = the Commons object location of the tower photos (sav_10..12), on the
  monastery roof E of the church's south end; 5.6 m square shaft to 22.5 m, belfry to 28.2 (arched
  opening per face), clock stage to 32 m (white clock face with hands, two small arched openings,
  corner pilasters), balustrade, octagonal base, dark green-grey octagonal tiled spire 7.5 m, gilt
  ball and cross (~43 m). Photos sav_02 (spire), sav_07 (clock stage), sav_08 (from the ramparts). M.
* Church: nave walls 14 m, hipped tiled roof (OSM roof:shape=hipped, roof:material=roof_tiles). M.
* Monastery: plain massing with window grid and parapet at the spec top.

## 5. Minarets
| minaret | where | built | conf. |
|---|---|---|---|
| Mosque of Omar (w290821793) | node 12893656140 (206.9, 145.8) | 3.6 m square shaft to 22.5 m, balcony, octagonal stage, lead dome, crescent (~28.5 m); mosque massing two storeys (9 m, omar_06) | H position / M size |
| Khanqah al-Salahiyya | w620113736, 24 m2 square building at (175, 247.3) on the line Omar minaret - Edicule (tops at the same level by tradition) | shaft to 19 m above its ground (~ same top as Omar with the current terrain) | M |
| Via Dolorosa (Muslim Quarter) | node 5921367466 (412.9, 379.3) in w1394857844 | host massing + 3 m shaft to 17 m, round stage (photo minaret_01_15622349) | M |
| Sidna Omar | see Hurva | | L |

## 6. Others
* **Tiferet Yisrael** w195100862: 14 m block with two rows of arched windows, cornice and parapet,
  octagonal drum r 5 with arched windows, ribbed lead dome r 5.3 (~22.6 m). L (rebuilt; few photos).
* **St James Cathedral** w265410575: 13 m block, porch of three pointed arches on the north
  courtyard edge (stone back, paved floor, iron screens; photos james_01..03), 12-sided drum with
  windows at (150.5, -233), ribbed lead dome, cross. M/L.
* **St Anne** w126864879: axis from the west front (edge (822.5,525.6)-(827.8,513.3)) to the apse;
  nave strip +-3.8 m at 15 m with a low stone gable, aisles 11 m (rubble), west front with the pointed
  portal, pointed window and aisle windows, square drum and grey stone dome over the crossing 24.5 m
  from the front (photos anne_04..07). M.
* **Ecce Homo arch** (node 2710817408 on the Via Dolorosa centreline (549.6, 402.2)): round arch 4.2 m
  span between a south pier and a pier 15 cm proud of the basilica wall, springing 3.8 m, crown 5.9 m,
  2.6 m thick block to 9.6 m with a barred window and cornice on both faces; street open below
  (photos ecce_01/02/07/08). Built by the Ecce Homo basilica builder (w744676490) with the basilica
  massing, an oculus on its street front and a small dome. M.
* Smaller churches (simple style: arched windows, pitched or flat roof): Christ Church w126755060
  (gable over the nave box), Co-Cathedral w1392261827 (Latin cross: two crossing gables from the ring
  arms), Alexander Nevsky w612045244 (flat, parapet), Flagellation w744674450 (gable), Condemnation
  w744674226 (five white domes), Four Sephardic Synagogues w29265134 (sunken: 6 m walls, four low
  white domes at the synagogue nodes). L.

## Budgets (triangles, hi incl. deco / LOD)
Holy Sepulchre 12 967 / 567; Redeemer 3 378 / 172; Mosque of Omar 1 313 / 71; Khanqah minaret
1 146 / 34; Hurva + Sidna Omar minaret 5 636 / 178; St Saviour monastery + tower 5 426 / 120, church
355 / 29; Tiferet 2 716 / 66; St James 1 998 / 62; St Anne 1 130 / 150; Ecce Homo 981 / 111; Via
Dolorosa minaret host 1 564 / 44; Christ Church 1 449 / 63; Co-Cathedral 1 032 / 62; Nevsky 430 / 10;
Four Sephardic 2 932 / 202; Flagellation 1 628 / 30; Condemnation 2 430 / 210.

## Checklist
- [x] Sepulchre: two domes with lantern/cross, bell tower, facade (portals, windows, cornices,
      ladder, stair), Chapel of the Franks, parvis walls, Deir es-Sultan dome and cells, tents.
- [x] Redeemer tower and church; Hurva with corner turrets and railed drum; St Saviour tower.
- [x] Minarets: Omar, Khanqah, Sidna Omar, Via Dolorosa.
- [x] Tiferet, St James, St Anne, Ecce Homo arch; simple versions of five more.
- [x] Audit: no coplanar overlaps in any landmark object (s01, s03, s04, s06, s09, s10).
- [ ] Sepulchre facade: carved voussoir pattern of the hood mouldings, frieze ornament (texture work).
- [ ] Redeemer apse half-cone roof; north portal zodiac arch detail.
- [ ] Khanqah minaret and Sidna Omar minaret: exact positions to confirm on site photos with known
      camera positions.
- [ ] Red Minaret (al-Zawiya al-Hamra, Muslim Quarter) and Al-Qaymariyya: no OSM node found; photos
      in minaret_01_41893380 / minaret_02_36690863 / minaret_03_48400067.
- [ ] Church of the Condemnation domes and the Flagellation gable portal from photos (flag_*).

## Spec issues found (for the main session)
1. The Sepulchre ring overlaps Christian Quarter St (x 160-170, y 150-205; s04 notes): the "west"
   zone walls stand on the street centreline. Clipping the ring along the street fixes it (the
   zones follow the ring automatically).
2. Fill block f300 (x 174-225, y 119-154, ~15 m above its ground) between the parvis and the Mosque
   of Omar hides the minaret from the parvis; photos (omar_06, hs_01_60046068) show two-storey
   buildings (~8 m) there.
3. Parvis ground: edge grounds round the parvis range -9.5 to -12.1 (a 2.5 m slope); the parvis is
   one level, and St Helena Rd is ~1 m *above* it (4 steps down into the parvis, OSM 616344391),
   while the Mosque of Omar's north edge ground is -14.5.
4. Minaret nodes without building records: Via Dolorosa minaret (node 5921367466) is built through
   its host w1394857844 (the whole host is replaced by plain massing); Sidna Omar has no node at all.
   Building records for the minarets would let them stand alone.
