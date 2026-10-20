# s09_wad: Al-Wad south, Via Dolorosa (Stations I-V), Chain Street east, Cotton Market: visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (lat 31.7766282, lon 35.2275435).
Sector polygon (data/sectors.json): x 400..~660, y -42..430. Its east edge is the Haram's west wall (x ≈ 587-660), the
north edge is y = 430 (s10/s08 beyond), the west edge is x = 400 for y > 48 and x = 420 for y < 48 (s04 / s05 beyond).
The south part (y -40..32) holds ~80 % of the Western Wall Plaza (see s07_kotel.md "Sector polygon warning"; that note
documents the plaza and is not repeated here).
Photos: `data/photos_ref/s09_wad/KNN_<pageid>.jpg`, cited below as **A02**, **C14** and so on. Titles, authors,
licences, dates and GPS are in `index.json` there. Groups: A = Al-Wad, B = Via Dolorosa east of Al-Wad, C = Via Dolorosa
Stations III-VI, D = Chain Street, E = Cotton Market, Bab al-Hadid, Little Western Wall, F = Aladdin St / At-Takiyya /
Barquq / Al-Khalidiyya, G = Western Wall Plaza, H = roofscape and views from roofs. "cam (x,y)" is the Commons camera
position where the file has one. The 21 Dec 2025 walk by מקף־עברי (A01, A07, A11, A12, A16-A19, C02-C06, C12, C13,
E08, E10) has GPS positions that are 10-30 m off in places (see Provenance).
Scale from people (1.7 m), doors (2.2 m) and OSM edge lengths. Confidence: **H** = seen clearly in 2+ photos, or OSM
geometry plus one photo; **M** = one clear photo or a consistent estimate; **L** = inferred or seen at an angle.

> Status: complete (research pass, 2026-10-20). 80 Commons photos in data/photos_ref/s09_wad/ (index.json).
> Coverage: Al-Wad from the Via Dolorosa junction to the Chain Street steps, Via Dolorosa from the Bab al-Ghawanima
> corner to Station VI, Chain Street x 420-640, the Cotton Market, Bab al-Hadid, Aladdin St, At-Takiyya and the
> Haram gate lanes are photo-backed. The residential interior east of Al-Wad (x 540-590, y 220-380), Barquq and
> Al-Khalidiyya are thin (1-2 photos each). The Western Wall Plaza: see s07_kotel.md.
> Model state checked on data/spec/s09_wad.json (2026-10-20 01:15) and one render (renders/sectors/s09_wad/current/).

---------------------------------------------------------------------------------------------------------------

## 0. Key facts and likely model errors (summary)

Spec checks in this section are measured on data/spec/s09_wad.json with shapely (scripts in build/spec_s09_wad/).

1. **The Via Dolorosa east of Al-Wad is blocked by infill.** OSM draws it as one way **w44830379** with `layer=-1`
   (living street, sett, lit; (679,429) → (495,391)). `infill.py` skips ways with layer < 0, so no street corridor
   is reserved and the infill pieces **f122, f123, f126, f130, f133, f255, f256** sit on the centreline for **87 m of
   188 m** (x 495-632). Photos show an open 5-6 m sett street with parked cars, golf carts and shop canopies (B03-B09,
   B12, C04). The N-side street facades are hidden too: Praitorion w744679915 e3 and Pilgrim House w744676491 e0/e13
   are `exposed: false` because the infill touches them. **H** (spec geometry + 8 photos).
   Fix (profile, next pass): an `open_areas` strip along w44830379, e.g. the 2.6 m half-width ring in 1.3.
   Request (code): infill should keep corridors for street-level ways tagged layer=-1 without tunnel=yes.
2. **The Cotton Market (Souq al-Qattanin) is filled with infill, and the wrong lane is built as the souq.**
   - The real market is **w291837739** "Al-Qattaneen Market" (layer -1, wikidata Q12217373, (534,141) → (627,150)),
     ending at the Cotton Merchants' Gate w291836677. Infill **f236, f226, f237** cover 39 m of it, and it gets no
     shops, vault or souq profile (its `name:en` is missing, so `SOUQ_STREETS` and `COVERED_SOUQS` miss it).
   - **w291836769** "Suq El-Quatta" (tunnel, `name:ar` = Aqabat as-Saraya) is in `COVERED_SOUQS` and gets 13 facades
     of full shop rows under a souq vault. It is the vaulted lane to the **Ablution Gate (Bab al-Mathara,
     w291836686 at (630-638,131-136))**, ~20 m south of the market, with few shops.
   - Photos: the market is a 95 m vaulted hall with skylights (E01-E07, A16), its portal faces Al-Wad (A17, E02, E03).
     **H** for the market (OSM + 9 photos). **M** for the Ablution lane's character (OSM only; no photo).
   Fix (profile): `covered_streets: ["291837739"]`, `souq_streets: {"291837739": [1.0, 0.0], "291836769": [0.15, 0.0]}`.
3. **Al-Wad's south end is blocked, and its level is wrong there.**
   - The last 94 m of Al-Wad (w508241135 tunnel layer -1, (536,123) → (551,65), and w277508274 building passage,
     (551,65) → (555,34)) are covered by infill **f232, f230, f234** (25 m of w508241135 and 24 m of w277508274).
     In the model Al-Wad dead-ends at y ≈ 123 and nobody can walk from Al-Wad to the Western Wall.
   - `street_z` rises from 731 m (y 110) to **738-739 m at y 45-55** because it is single-valued and Chain Street
     passes overhead on a causeway. data/terrain_street.json already records the **underpass** (731.0 → 729.8 m asl,
     (536,110) → (562,18)) but nothing uses it. **H** (OSM, survey).
   - Photos: A18 and A20 (y ≈ 110) show the street open to the sky between arches. A21 shows the flight of ~10 steps
     that climbs from Al-Wad up to Chain Street (OSM steps w508241131 / w508241129).
   Fix: `open_areas` strip along w508241135 (ring in 1.2.4) plus `covered_streets: ["277508274"]` (the passage under
   the causeway). Request (terrain/code): pin Al-Wad to the underpass profile from y 123 to the plaza.
4. **At-Takiyya / Aladdin St is one 181 m OSM steps way (w291836767) laid across the Al-Wad valley.** `stairs.py`
   interpolates its treads linearly from 737.8 m at Bab an-Nazir to 746.2 m at Khan ez-Zeit. At the Al-Wad crossing
   (511,268) the treads stand **up to 8.5 m above the street**: a stepped wall across Al-Wad, 55 treads more than 1 m
   off the ground. **H** (spec). In reality:
   - the east half (Aladdin St / Tariq Bab an-Nazir, (512,268) → (604,277)) rises only 4 m in 92 m (4.5 %). A car is
     parked in it (F06), so it has no steps, or only a few;
   - the west half (Aqabat at-Takiyya) climbs 12.5 m in 90 m with steps (F02, F08).
   Request (code): split steps ways at junctions and at street_z extrema, or at least at node (512,268).
5. **Arches over streets are built as solid blocks.** OSM `building=roof` + `layer=1` objects (sabats, arched passages)
   are kept as ordinary buildings from the ground up and close the street they span:
   - **w1393388437**: Chain St at (568-576, 42-49), 6.1 m of centreline;
   - **w1393388444**: the vaulted porch of Bab al-Silsila, (631-639, 66-84), 10.6 m tall. D15 and D13 show it as an
     open pointed-arched porch;
   - **w1392511599**: Aladdin St at (492-498, 262-268);
   - **w1393158496**: the slot of the Ecce Homo arch on the Via Dolorosa, (552-555, 401-405). The arch itself is built
     by landmarks_city;
   - **w1393163032**: Aqabat ar-Rahbat at (564-569, 408-412);
   - **w1394857839**: the footway at Station III/IV, (438-442, 361-367);
   - **w1393380722** (Al-Hakkari), **w1393391237** (lane w1177205457), **w1393375646** (Misgav Ladach at
     (485-490, 17-24)) and **w1393375644** (Shonei Halachot at (457-463, -22..-17)).
   **H** (spec). Fix: `remove_buildings` for these ids (evidence above). Request (code): build `building=roof`
   `layer>=1` as a sabat (mass from ~3.5-4 m up) instead.
6. **Chain Street's covered stretch is blocked.** w26492743 (tunnel, layer -1, (566,45) → (601,55)) is covered by infill
   **f241, f234** and by w1393388437. D03 and D10 show the street entering a pointed-arched vaulted passage at its east
   end, with police barriers. **H**. Fix: `covered_streets: ["26492743"]` plus the removal in item 5.
7. **Al-Wad is modelled too narrow.** OSM maps almost no buildings along Al-Wad, so its frontage is infill. The
   infill corridor takes the minimum half-width (1.4 m), giving **2.7-2.9 m wall to wall** for y 125-325. The photos
   show:
   - 3.2-3.5 m inside the vaulted stretch (A05);
   - 3.5-4 m in the narrow middle (A08);
   - 4.5-5.5 m at Stations IV-V (A02, A25);
   - ~6 m at the Via Dolorosa junction (C03, C05, A23).
   **H**. Fix: `open_areas` strips with a 2.0 m half-width along w362057745 and 2.4 m along w362057747 (rings in
   1.2.4).
8. **Heights.** Buildings along Al-Wad are 3-4 storeys, ~11-14 m to the parapet, with fenced roof terraces on top
   (A02, A07, A08, A25, C05). The spec median along Al-Wad is **8.4 m** (p75 9.1 m). 16 of the 38 frontage buildings
   are infill at 6-9 m. **M-H**. Request: raise infill fronting Al-Wad, the Via Dolorosa and Chain Street to 10-12 m.
   Infill ids (fNNN) are renumbered on every spec run, so per-building overrides on them are fragile; this needs a
   rule.
9. **The Ghawanima minaret is duplicated.** landmarks_haram builds the Ghawanima minaret (square base 6.2 m) at
   (587.23,370.77). The s09 spec keeps OSM **w291836716** "Gate of Bani Ghanem" (historic=city_gate, layer 1,
   (583-590, 368-378)) as a generic 15 m block in the same place. That gives coplanar faces. **H** (code + spec).
   Fix: `remove_buildings: {"w291836716": ...}`. F10 shows the minaret rising behind a wall, with no block in front of
   it.
10. **The Mughrabi bridge** (OSM steps w277508271, bridge=yes; it runs from (613,-42) to (657,-27) inside the s09
    polygon) is built by `stairs.py` as a solid stepped mass **up to 7.8 m above the plaza**. It should be a timber
    bridge on stilts (s07_kotel.md). Request to the spec owner / the s07 and haram owners.
11. **Vaulted and arched stretches of Al-Wad** (not in OSM):
    - a pointed cross-vaulted stretch of ≥ 20 m at **(468-488, 302-318)**, south of Station V (A05 looking NW from its
      north part, A07 under its south arch, A08 looking at it from (488,300));
    - vaults at the **Aladdin St junction (505-515, 262-272)** over the Sabil al-Wad (A10, A14, F01);
    - single arches at y ≈ 109 (A18) and y ≈ 228 (A12).
    **M-H**. Request (code or manual): a `vaults` entry on part of a way, or split w362057745.
12. **Via Dolorosa east of Al-Wad must not be stepped.** OS 1865 grades are 5-7.5 % ((421.5,372.1) 737.0 →
    (461,383.3) 740.05 → (506.9,393.7) 742.8 → (574,408.2) 746.15). The smoothed field crosses the 7 % threshold, and
    `stairs.py` lays 34 treads on w582488415 (x 433-472) and 3 on w44830379 (x ≈ 523). Photos show a smooth sloping sett roadway used by cars and carts
    (B03, B04, C04, A23). **H**. Request: no steps on w582488415 / w44830379 (living streets).
13. **Closed-shop look (target state).**
    - Doors: steel plank or panel doors in **teal / blue-green** (A02, A05), **pale lime-olive green** (A08),
      **dark bottle green** (C14, B12), **olive grey** (A13) and **cream** (E05, F05). Each has two hasp bars with
      padlocks.
    - Canopies: shed canopies of **dark grey sheet steel on black perforated quarter-circle or scroll brackets**
      (C14, B03, B06), green fabric awnings (A07, A08) and green-white striped awnings (C03, C05).
    - Overhead: **wire-mesh / steel-grille nets** spanning Al-Wad and Chain Street at upper-floor level, which catch
      thrown objects (D14; the Commons captions of Chris Yunker 2007 and Joe Goldberg 2009 say so).
    - Israeli flags, roof fences, CCTV and rooftop guard posts mark the Jewish-owned houses (A07, A22, A25, H04).
    **H**.

**Render check** (renders/sectors/s09_wad/current/wad_n.png and sbs_wad_n_A02.jpg; cam (449.8,339.7) at Station IV
looking NW, matching A02). The E side has a teal-door shop row with green steel canopy frames. The **W side is a
blank wall with one grilled window, where A02 shows a continuous shop row** under sheet canopies. The walls are
clean, even, large-block ashlar, where the photo has rough, darker stone with cables, signs and goods hung out.
Width ~5 m, which is right here. The other three views (vault, Ecce Homo, Cotton Market) were cut off by a 20 min
timeout on a loaded machine; the spec geometry above already shows those streets blocked or too narrow.

Requests also go to the profile's "requests" (sections 0 and 5 give the values).

---------------------------------------------------------------------------------------------------------------

## G. OSM geometry of the core (data/osm_local.json, data/spec/s09_wad.json)

### G.1 Landmarks and notable buildings

| feature | OSM | position (local m) | notes |
|---|---|---|---|
| Ecce Homo arch | node n2710817408 (historic=city_gate) | (549.6,402.2) on the Via Dolorosa centreline | **landmark** (landmarks_city.ecce_homo, hangs off w744676490) |
| Ecce Homo Basilica (Sisters of Zion) | w744676490 | x 524-555, y 398-417 | **landmark**; N side of the Via Dolorosa |
| Ecce Homo Pilgrim House | w744676491 (hostel) | x 527-565, y 405-433 | ordinary building (overridable), N side; e1 faces 77° onto Aqabat ar-Rahbat |
| Praitorion (Prison of Christ, Greek Orthodox) | w744679915 | x 499-527, y 394-408 | ordinary; N side; street face e3 (501.3,393.9)->(526.6,398.3), faces 170° (not flagged exposed in the spec) |
| Church of the Condemnation | w744674226 | x 578-594, y 410-423 | **landmark**; Station II n2619678592 (589.3,419.5) |
| Church of the Flagellation | w744674450 | x 619-642, y 419-433 | **landmark** |
| Umariya school block (Station I) | w290986913 (1146 m², spec h 14.5) | x 612-675, y 378-426 | ordinary; S side of the Via Dolorosa (e22/e24 face 343-349°); Station I node (605.0,409.5) |
| Lithostrotos | n9351338558 | (575.4,422.5) | under the Sisters of Zion; r3867440 is its layer -1 hall |
| Via Dolorosa minaret | node n5921367466 in w1394857844 | (412.9,379.3); host x 397-418, y 368-393 | **landmark** (host_minaret); SW corner of the Al-Wad / Via Dolorosa junction |
| Austrian Hospice of the Holy Family | w52890125 (1088 m², spec h 12.2) | x 409-461, y 392-428 | ordinary (**not** a landmark); entrance n929266040 (430.5,397.4) up steps w617363479 (5) + w160699290 (tunnel, 5) + w744679916; café n3784277379 (414.0,406.1) |
| Church of Our Lady of the Spasm (Station IV) | w277705915 (219 m², spec h 8.6) | x 451-479, y 360-374 | ordinary; stands back behind a courtyard off Al-Wad (C10); Stations III+IV n2619678596 (437.6,364.3), IV n4191110381 (439.1,361.8) |
| Armenian Catholic Patriarchal Exarchate | n11473028461 | (440.4,371.8) | facade on Al-Wad, E side, just S of the junction (C06) |
| Station V (Franciscan) | n2619678604 | (462.7,320.2) | corner of Al-Wad and the Via Dolorosa steps (C12) |
| Ateret Cohanim yeshiva | w337612156 | x 450-472, y 329-355 | ordinary; corner of Al-Wad and Barquq; Al-Wad face e11 (449.6,342)->(461.1,329.1), faces 228° |
| Hazon Yekhezkel | w1071118807 | x 458-472, y 303-316 | ordinary; S of Station V |
| Kollel / library (Jewish) | w499223568, w499223567 | (463-470,141-147), (453-465,145-153) | small |
| Ohel Yitzchak synagogue | w499223566 (spec h 13.1) | x 540-559, y 79-101 | ordinary; Al-Wad face e0 (539.6,97.9)->(543,80.7), faces 259° |
| Shuvu Banim yeshiva | w499210295 | x 498-514, y 86-104 | ordinary |
| church (unnamed) | w508184693 | x 527-544, y 198-211 | at the Al-Wad / Bab al-Hadid corner |
| mosque (unnamed) | w1393158506 | x 529-540, y 342-356 | off Barquq |
| Gate of Bani Ghanem | w291836716 (layer 1, height 15) | x 583-590, y 368-378 | **duplicate of the Ghawanima minaret** (item 0.9) |
| Ghawanima minaret | (Wikidata, landmarks_haram) | (587.23,370.77) | **landmark** (haram module) |
| Haram gates (landmarks_haram.haram_gate) | Gate of the Chain w291836687 (638-649, 66-82); Cotton Merchants' w291836677 (626-636, 143-160); Ablution w291836686 (630-638, 131-136); Iron w291836690 (618-626, 194-200); Watchman / Bab an-Nazir (Bab al-Majlis) w291836689 (603-612, 274-281); "Council Gate" w620130982 (589-598, 346-352) | | **landmarks** |
| Bab al-Silsila minaret | node n13791836098 | (639.7,84.1) | **landmark** (hangs off the Western Wall) |
| Wilson's Arch prayer hall | w499210296 (layer -1) | x 619-646, y 31-63 | **landmark** (Western Wall builder); `GROUND_HOLES` in make_spec |
| Western Wall | w817206833 | x 641-665, y -23..67 | **landmark** |
| Tomb of Turkan Khatun | node n9362732611 | (616.5,60.8) | N side of Chain St (w291836757); carved window panels (D04) |
| Gate of the Chain hostel | n3749005285 | (610.6,84.5) | |
| Little Western Wall (HaKotel HaKatan) | n2954804553 | (618.0,217.0) | reached by the passage w609259748 from (616,199), just S of the Iron Gate |
| Entrance to the Western Wall plaza (checkpoint) | n290358852 | (550.6,64.5) | foot of Al-Wad; Western Wall tunnel entry n4975809347 (554.9,33.9) |
| North end block of the plaza | w394161633 (building:levels 5 → spec 19.2 m, the tallest in s09) | x 561-599, y 13-34 | see s07_kotel.md |
| big block W of the plaza | w1528632636 (1346 m², spec h 11.7) | x 535-572, y -49..3 | Western Wall police station n14073079423, Colel Chabad kitchen n14073003968 |

### G.2 Streets (OSM centrelines)

- **Al-Wad** (Al Wadi / HaGai):
  - w362057747: (425,374) → (445,347) → (463,324). The Via Dolorosa junction to Station V; 63 m.
  - w362057745: (463,324) → (488,304) → (512,268) → (516,246) → (523,217) → (525,195) → (527,175) → (534,141) →
    (536,123). 222 m; sett.
  - w508241135: (536,123) → (539,107) → (540,82) → (551,65). Tunnel, layer -1.
  - w277508274: (551,65) → (555,34). Building passage, layer -1; under the Chain St causeway to the plaza.
- **Via Dolorosa**:
  - w44830379: (679,429) → (640,421) → (606,414) → (588,410) → (570,406) → (550,402) → (523,396) → (495,391). Living
    street, layer -1, sett, lit.
  - w582488415: (495,391) → (472,387) → (445,382) → (425,374). Living street, sett.
  - steps w26506003: (463,324) → (405,310). Station V → VI, incline up westwards, sett; it continues as w616344390
    (27 steps) into s04.
- **Chain St** (Silsileh / Tariq Bab al-Silsila):
  - w277508275: (345,9) → (393,12) → (418,17) → (454,22) → (486,27) → (519,32) → (535,35) → (566,45). The part
    x < 420 is in s05.
  - w26492743: (566,45) → (601,55). Tunnel, layer -1.
  - w291836757: (601,55) → (630,64) → (640,71). To the Chain Gate.
- **Al-Qattanin market** w291837739: (534,141) → (550,144) → (581,149) → (600,151) → (627,150), layer -1, then
  w723954927 (tunnel) to (634,152).
- **Lane to the Ablution Gate** ("Suq El-Quatta") w291836769: (556,125) → (574,128) → (584,121) → (599,124) →
  (614,131) → (630,132), tunnel; then w291836753.
- **Bab al-Hadid** w26611968: (525,195) → (553,194) → (577,185) → (595,191) → (619,196). Paving stones.
- **At-Takiyya** steps w291836767: (604,277) → (597,276) → (512,268) → (425,250). East of (512,268) it is Aladdin St /
  Tariq Bab an-Nazir; west of it Aqabat at-Takiyya. Then w44376193 into s04.
- **Aqabat as-Saraya** w26492741: (321,171) → (426,174) → (482,180) → (496,120) → (536,128).
- **Aqabat al-Khalidiyya** w26611966: (390,103) → (409,105) → (496,120).
- **Barquq** steps w26506004 (layer -1, lit): (445,347) → (478,357) → (502,343) → (526,338) → (563,348) → w603861900 →
  (578,351).
- **Bab al-Ghawanima St** w291836768: (570,406) → (576,363). Then steps w26492737 (12 steps, ramp, building passage,
  layer -1) down to (578,351), then the tunnel w291836764 to the gate at (597,349).
- Others: Al-Hakkari w290821800 (x 409-418); Aqabat Etkia w277275138; Al-Bairek w257617678 / w603861910 (x 400-408);
  Qukater Khoeir w26611969; Aqabat ar-Rahbat w26496671 (569,406) → (560,435); Al-Hilal w582488417; the Western Wall
  approach footways w288016683, w394161635/6; JQ steps HaKotel HaMaaravi w26493217 etc.; At Takiyyeh Road w44376193
  (tunnel); Western Wall tunnel w291970362 / w508242248 (layer -2, ignore).

### G.3 Widths (wall to wall, perpendicular rays to spec footprints every 5 m; build/spec_s09_wad/widths.py)

| street | model (spec) | photos | note |
|---|---|---|---|
| Al-Wad, junction → Station V (w362057747) | 4.6-4.8 m (16.6 m at the junction mouth, 10.6 m at y 356) | ~6 m at the junction (C03, C05, A23); 4.5-5.5 m at Station IV (A02, A25) | **M** |
| Al-Wad, Station V → Qattanin (w362057745) | **2.5-3.0 m** (infill on both sides) | 3.2-3.5 m in the vault (A05); 3.5-4 m at y 300 (A08); ~4.5 m at the Aladdin junction (A10); ~4 m at Bab al-Hadid (A22) | **H** that the model is too narrow |
| Via Dolorosa w582488415 | 2.4-3.1 m (infill f140 / f118) | **5-6 m** (C04, B05, B09) | **H** |
| Via Dolorosa w44830379 | 0 m on 87 m (infill on the street); 4.3-6.7 m elsewhere | 5-6 m (B03, B04, B06, B08) | **H** |
| Chain St w277508275 (x 420-566) | 3.7-4.8 m | 4-5 m (D02, D05, D11) | OK |
| Chain St w291836757 | 4.7-4.8 m | ~4 m (D13) | OK |
| Bab al-Hadid | 2.5-3.6 m, 4.7 m at the E end | 3-4 m (E08, E12, A22) | slightly narrow |
| Qattanin hall | none (filled) | clear 4.5-5 m between shop fronts, vault crown ~7-8 m (E01, E04, E07) | **M** |

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and STREET PROFILES

### 1.0 Character
The sector is the floor of the Tyropoeon valley: **Al-Wad**, a long, slightly winding market street that falls gently
south from the Via Dolorosa junction (737 m) to the Western Wall (730 m), with the Haram's west wall 50-90 m to the
east. Every few dozen metres a lane branches east up to a Haram gate:
- Barquq and Bab al-Ghawanima to the Ghawanima Gate;
- Aladdin St to Bab an-Nazir;
- Bab al-Hadid to the Iron Gate and the Little Western Wall;
- the Cotton Market hall to Bab al-Qattanin;
- the Ablution lane to Bab al-Mathara;
- Chain Street to Bab al-Silsila.
Stepped lanes climb west to Khan ez-Zeit: the Via Dolorosa steps, At-Takiyya, Al-Khalidiyya and As-Saraya.

The look:
- Mamluk monumental fabric (ablaq portals, sabils, madrasas) on Chain St, Bab al-Hadid, Aladdin St and At-Takiyya;
- shop rows with steel doors along Al-Wad, Chain St west and the Cotton Market;
- 19th-century Christian institutions with clean pale ashlar on the Via Dolorosa (Austrian Hospice, Ecce Homo,
  Armenian Catholic);
- Jewish-owned houses scattered along Al-Wad, with Israeli flags, fenced roofs and CCTV.
The skyline: dense flat roofs with shallow white domes, rooftop rooms, water tanks and dishes. It is pierced by the
Via Dolorosa and Ghawanima minarets and the Ecce Homo dome, and has the Dome of the Rock behind (H01-H03).

### 1.1 Profile table

| profile | OSM streets | key look |
|---|---|---|
| P1 main market street | Al-Wad w362057747, w362057745, w508241135 | 3.5-6 m; steel shop doors (teal, lime-olive, dark green); dark sheet canopies on black brackets and green fabric awnings; wire-mesh nets overhead; vaulted stretches; 3-4 storeys |
| P2 sloping institutional street with shops | Via Dolorosa w44830379, w582488415 | 5-6 m; grey sett ramp with a slab gutter; clean pale ashlar institutions on the N side, shops with canopies on the S side; cars, golf carts; the Ecce Homo arch |
| P3 stepped market lane | Via Dolorosa steps w26506003; Aqabat al-Khalidiyya w26611966; At-Takiyya W half; As-Saraya E part | 2.8-4 m; broad low steps (0.10-0.15 m risers, 1.2-2 m treads), central ramp strips; flying arches; dark canopies; closed doors dark green / olive / cream |
| P4 Mamluk approach street | Chain St w277508275 (x 420-566), w26492743 (vaulted), w291836757 | 4-5 m; souq in the W part, then Mamluk facades with grilled windows, carved panels and lanterns on curved brackets; a vaulted passage and the gate porch at the E end |
| P5 vaulted market hall | Al-Qattanin w291837739 | 95 m pointed cross-vaulted hall, skylights, shop recesses with tall wooden or steel doors |
| P6 Haram gate lane | Bab al-Hadid w26611968; Aladdin St (E half of w291836767); Bab al-Ghawanima St w291836768 + w26492737; Barquq w26506004; Ablution lane w291836769 | 3-5 m; mostly residential and institutional (few shops); ablaq Mamluk facades; flying arches; police barriers; a vaulted gate passage at the end |
| P7 residential interior | unnamed footways E of Al-Wad (w257617675, w257617680, w257612451, w257612452 …) | narrow, plain rubble and ashlar walls, doors with grilles, courtyards (OSM only, L) |

### 1.2 P1: Al-Wad (main market street)

Souq rule: `SOUQ_STREETS["Al Wadi"] = (0.7, 0.35)` is keyed by name and shared with s08. The photos show shop rows
almost continuously on both sides from the junction to the Cotton Market (A02, A25, A08, A05, A22), except at the
institutions (Armenian Catholic, Station V, sabils). Render wad_n (section 0, render check) shows a blank W wall
where A02 has shops. Suggested per-way keys in the s09 profile: `"362057747": [0.9, 0.4]`,
`"362057745": [0.85, 0.35]`, `"508241135": [0.6, 0.2]`. Then switch off the institutions with overrides.

#### 1.2.1 North: Via Dolorosa junction to Station V (w362057747, y 374 → 324)
Photos: C03, C05, C08, A23 (junction, looking N and NW); A02, A03, A25 (from Station IV looking N); C06, C10, C12,
A01.
- **Junction (425,374)**: a small widened space, ~6 m.
  - NE corner: the Austrian Hospice's terrace wall, with cypresses and palms above (C02, C05) and the hospice flags
    (Austria, Vatican, C11; an EU flag in a dropped photo, L).
  - SW corner: the Via Dolorosa minaret host (w1394857844). A white cylindrical minaret with a gallery and a
    green-copper dome rises from a 3-storey block with arcaded balconies and a "جمعية زهرة المدائن" sign (C09, A23).
  - The minaret closes the view N along Al-Wad from Station V (C08, A03). **H**
  - At the junction: a red cast-iron pillar post box, a stone bench, no-entry signs, CCTV clusters, a police cart and
    parked utility vehicles (C03, C05, A23).
  - The large menorah on the roof of the Jewish-owned building N of the junction (Beit Wittenberg, Al-Wad W side
    x ≈ 395-405; s04/s09 boundary) closes the view N (C03, C05, C08). **M**
- **Width** 4.5-5.5 m wall to wall (A02: three people abreast plus ~0.8 m of display on each side), 6 m at the
  junction. **M**
- **Shops**: continuous on both sides (A02, A25).
  - Openings 2-3 m wide with steel doors: teal panelled 2-leaf doors on the E side (A02 right).
  - Sheet-steel shed canopies at ~3 m with fluorescent tubes (A02 left), fabric canopies, goods hung on rails.
  - A modern glazed pharmacy front ("PHARMACY", green neon) on the E side near Station IV (A25, A03). **H**
- **Upper floors**: 3-4 storeys of rough ashlar with small grilled windows and fenced roof terraces. Israeli flags on
  the building closing the view at the junction (A25, A02). **M**
- **E side, y 360-372**: the Armenian Catholic Patriarchate.
  - A clean smooth-ashlar facade with a round-arched moulded portal on colonnettes, dark timber doors and a long
    red-blue-orange banner "ARMENIAN CATHOLIC PATRIARCHATE" (C06).
  - The arched gateway to the Our Lady of the Spasm courtyard: the station disc and the "ARMENIAN CATH…" lettering on
    the arch (A23).
  - The church stands back in a slab-paved courtyard. Its front is a gabled neo-Byzantine facade with a triple
    round-arched window and a portal with red-and-white banded voussoirs up steps (C10); a grey ribbed dome on a
    windowed drum shows from the hospice roof (H02).
  **H**
- **Station V corner (462.7,320.2)**: a bronze disc "V", a relief of Simon of Cyrene, the Franciscan arms, a ceramic
  VIA DOLOROSA sign and CCTV (C12). **H**
- **Paving**: rectangular limestone slabs 0.3-0.5 × 0.6-0.9 m in courses, rough-picked, with round cast-iron manholes
  on the centreline (A02, A25). A short stretch of Roman (Eastern Cardo) pavement is exposed at Station III/IV
  (OSM n9351440271 (445.4,381.7) "Roman pavement"). **H**

#### 1.2.2 Middle: Station V to the Aladdin St junction (w362057745, y 324 → 268)
Photos: A05, A07, A08, A10, A14, F01, A11 (y 240).
- **Vaulted stretch** at ~(468-488, 302-318):
  - a pointed barrel vault on transverse arches (cross-vaulted bays), clear width 3.2-3.5 m, springing ~3.0-3.3 m,
    crown ~5.2-5.5 m; plastered and stained, with cables and lamps (A05);
  - its S mouth is a pointed arch at ~(487,304) (A07: camera under it, looking SE; the same red-green Hebrew sign
    shows in both A05 and A07);
  - from (488,300) the street runs ~15 m to that arch (A08). **M-H**
- **S of the vault (A08, cam (487.9,300))**:
  - width ~3.8 m;
  - W wall of big rough blocks below (battered foot) with smaller ashlar above; 3-4 storeys (~13 m) with a fence and
    barbed wire on top, an LED floodlight at ~4 m and window grilles;
  - E side: **pale lime-olive plank steel doors** with hasps, a raised 0.15 m stone kerb in front of the shop row, a
    doorway up 4 steps with a teal handrail, a green fabric canopy;
  - water heaters on the roofs. **H**
- A07: Israeli flag on an upper floor, CCTV, cables bundled across the street; green shed canopies; black steel doors
  on the W side. **M**
- **Aladdin St junction (512,268)**:
  - the street runs under pointed vaults with Ramadan light strings (A10, F01);
  - the **Sabil al-Wad** stands at the corner (A14, cam (508.3,268.5)): a pointed niche ~2.5 m wide and ~4 m tall
    with a band of carved rosettes round the arch, twisted colonnettes, an inscription panel and a spout over a basin,
    next to the ceramic sign "ALAA AD-DIN ST.";
  - a police checkpoint (OSM n6923981786 (512.4,268.7)); food shops (OSM falafel n5972491687 (508.9,283.7),
    supermarket n5702896235 (503.3,273.3)); a bakery on the At-Takiyya corner (Commons captions, L). **H**
- **Hajj murals**: painted boards with the Kaaba and the Dome of the Rock next to doors (A11). **M**

#### 1.2.3 South: Aladdin St to the Cotton Market (w362057745, y 268 → 141)
Photos: A12, A13, A22, A16, A17, E02, E03.
- Width ~4 m (A22 at the Bab al-Hadid corner). **M**
- **Flying arch** across the street with a parapet walkway on top, CCTV, at (519,228) (A12). **M**
- No. 103 (A13, cam (519.3,212.8)): a closed bakery.
  - Olive-grey steel 2-leaf panel door ~1.3 × 2.2 m under a flat stone lintel, with a relieving course and a raised
    stone threshold.
  - A black steel post with painted house numbers; a white house-number plate "103"; steel canopy brackets above.
  **H** for the type.
- **Bab al-Hadid corner (525,195)** (A22, cam (544.7,201)):
  - dark-green 2-leaf steel gate;
  - a round-headed doorway with "בית אלחנן";
  - the ceramic sign "BAB EL-HADID RD." with a "المسجد الأقصى" arrow sign;
  - Israeli flags on the upper floors, a sabat arch over Bab al-Hadid, police barriers. **H**
- **Cotton Market portal** on the E side at (534-536, ~141) (A17, E02, E03; OSM w291837739 W end):
  - a tall pointed arch (~5 m span, apex ~7-8 m) in rough ashlar over a ~3.5 × 3.5 m flat-topped entrance;
  - the tympanum is laid in a radiating pattern with white joints and has a round oculus;
  - a black inscription plaque, a modern heritage plaque, a ceramic sign "שוק מוכרי הכותנה / سوق القطانين /
    AL-QATTANIN ST.", a box wall lamp;
  - a green-white striped awning on the left.
  The 2025-26 geotags (A16, A17, E06) sit 10-25 m S of the OSM entrance; that is probably GPS error in a deep street.
  Use OSM. **H** for the object, **M** for the position.

#### 1.2.4 Southern end: Cotton Market to the plaza (w508241135, w277508274, y 141 → 34)
Photos: A18, A19, A20, A21, D09.
- Arched / open alternation:
  - A18 (cam (540.2,109.3)): camera under a broad pointed arch; beyond it the street (~5 m) is open, with a white
    fabric canopy, shops and a green door;
  - A20 (cam (534.9,109.8)): an Ottoman sabil, with a pointed arch on clustered colonnettes, a cusped hood, an
    inscription panel and a basin, under string lights against the sky;
  - A19: a sabil trough made from a marble sarcophagus with ribbed jambs (cam (538.8,114)). **M-H**
- The Hammam al-Ayn entrance on Al-Wad just S of the Cotton Market (Commons "Chamam El En", (531.5,127.3)). **L**
- **Steps up to Chain St** (A21, cam (541.6,73.4)): a broad flight of ~10 steps (risers ~0.16 m, treads ~0.4 m),
  ~4 m wide, seen through a segmental arch, with a black handrail on the upper landing, orange pay phones, a convex
  mirror and trench grates at the foot. OSM steps w508241131 (553,79) → (564,74) and w508241129 (559,66) → (558,73).
  **H**
- The plaza checkpoint (n290358852 (550.6,64.5)) and the passage under the Chain St causeway (w277508274) lead to the
  plaza at (555,34). No photo in this set; s07_kotel.md K:008 covers the lane near (538,41).
- **Suggested `open_areas` strips** (computed from the centrelines; they keep infill out without touching OSM
  buildings):
  - Al-Wad S, w508241135, half-width 2.0 m: [[537.5,123.7],[533.6,122.9],[536.7,107.8],[534.5,104.3],[538.3,80.8],
    [548.9,63.5],[552.3,65.6],[542.2,82.2],[538.7,103.4],[540.9,107.1]]
  - Al-Wad middle, w362057745, half-width 2.0 m (22 points): [[474.9,316.3],[464.7,325.8],[462.0,322.9],[472.4,313.2],[487.0,302.8],[498.0,283.9],
    [509.8,267.1],[513.9,245.5],[521.0,216.6],[523.2,201.4],[524.7,175.1],[534.2,127.9],[533.6,124.0],[537.6,123.4],
    [538.2,128.0],[528.7,175.7],[527.2,201.8],[524.9,217.3],[517.8,246.3],[513.5,268.7],[501.4,286.0],[490.0,305.5]]
  - Al-Wad N, w362057747, half-width 2.4 m: [[427.2,375.2],[423.3,372.5],[455.9,327.4],[461.8,322.5],[464.9,326.2],
    [459.5,330.7]]
  (Rings are as shapely wrote them; re-orient CCW if the checker asks.)

### 1.3 P2: Via Dolorosa east of Al-Wad (w582488415, w44830379)
Photos: C04 (from the junction looking E), B05, B09 (looking W towards the junction), B04 (cam (484.7,388.1)
looking E), B08 (cam (524,389.9) looking E at the arch), B03, B06 (from the Bab al-Ghawanima corner looking W),
B02, B12, B07, B01.
- **Width** 5-6 m. **Surface**: a smooth sloping ramp of small grey setts or cobbles (~0.12-0.2 m) laid in arcs,
  with a central gutter or band of rectangular slabs (B01, B03, B04, B08). A dropped 2010 photo showed larger
  rectangular slabs on the lower part near Al-Wad (L). **No steps** in any photo: cars park at the Ghawanima corner
  (B03, B06), a golf cart at the junction (C04), a 4x4 at Station III (A23). **H**
- **x 420-490, N side**: the **Austrian Hospice garden's retaining wall**, ~4-5 m of rough, slightly battered ashlar
  with projecting piers and black wall lamps. On top: a green steel mesh fence (~1.5 m; razor wire in C09), date
  palms and cypresses (B05, B09, C04, C09). OSM tree nodes at (421-477, 387-401) match.
  **H**
- **x 420-490, S side**: smooth 3-storey ashlar buildings with tall round-arched windows (the Armenian Catholic
  complex), a black shed canopy, shops and hostels (Armenian Hospice n685536761 (468.6,381)). Yellow awnings and
  Israeli flags on a fenced roof (C07, deleted from the set: L). Small grey pyramid-capped bollards along the S edge
  (B05). **M**
- **x 499-527, N side**: the Praitorion (Greek Orthodox), 4 storeys of smooth pale ashlar with **green louvred
  shutters** (B04 left). **M**
- **x 524-565, N side**: Ecce Homo basilica and Pilgrim House.
  - Romanesque facade with a rose window and a round lattice window behind the arch (B07).
  - Tall barred windows and round-arched doorways (B03, B06, B08). **H**
  - Clean, very pale ashlar (19th c.).
- **S side x 500-570**: older 2-3 storey houses with shops under **dark sheet canopies on black scroll brackets**,
  textiles hung on the walls, green doors, a no-parking sign, ceramic street signs (B03, B06, B08). **H**
- **Ecce Homo arch** (landmark) spans the street at x 549.6. A round arch springing at ~4 m, with a 2-window room on
  top (top ~10 m) and the "VIA DOLOROSA" inscription on its soffit block (B03, B06, B07, B08). See 2.1.
- **Bab al-Ghawanima corner (570,406)**: ceramic signs "VIA DOLOROSA" and "BAB AL-GHAWANIMA ST.", house no. 235,
  cables, a light box (B02). **H**
- **East of x 575** (Stations I-II): the Condemnation and Flagellation compound (N, landmarks) and the Umariya school
  wall (S). B01 (2006, cam (609.2,415.8)) shows the sett ramp and shops with canopies. **L-M**
- **Slope**: falls 10.8 m from the arch (747.8 m) to Al-Wad (737.0 m) in ~125 m (5-7.5 %; section 5).

Suggested `open_areas` strip for the blocked part of w44830379 (x 494-632, half-width 2.6 m):
[[632.4,416.6],[631.3,421.7],[587.5,412.1],[568.3,408.8],[522.0,398.9],[494.0,393.8],[495.0,388.7],[523.0,393.8],
[569.3,403.7],[588.5,407.0]].

### 1.4 P3: Via Dolorosa steps (Station V → VI, w26506003) and other stepped lanes
Photos: C13 (cam (437.1,325.3)), C14 (2014, near Station VI looking E, all shops closed), F05 (Al-Khalidiyya,
closed), F02, F08 (At-Takiyya).
- **Via Dolorosa steps**: **2.8-3.2 m** wide.
  - Paving: slabs with **broad low steps** (single risers ~0.12-0.15 m in long kerb-stone rows, treads ~1.5-2 m) and
    round manholes on the centre line.
  - **Three flying arches** spanning at ~4-7 m: a broad segmental arch with masonry above, then two lighter arches.
  - A **salmon-pink timber oriel** (enclosed balcony on a cove bracket) at ~4-7 m on the N side near Station VI.
  - Dark grey sheet canopies on **black perforated quarter-circle brackets** at ~3 m on both sides.
  - Closed shops with **dark green steel plank doors** (2 leaves, ~2.2 m) with padlock bars; grey and blue utility
    cabinets; orange plastic drainpipes. **H** (C13, C14)
- **Al-Khalidiyya** (F05, closed): ~3.5 m.
  - Long low steps with a **central ramp strip** for carts.
  - Cream and pale green steel doors, green corrugated and fabric canopies.
  - Steel trench grates across the lane at the foot. **M**
- **At-Takiyya W half** (F02, F08, cam (427.4,251.2)): ~4 m, rising W in low steps and ramps.
  - Monumental **Mamluk ablaq portals**: tall recessed pointed arches with black-red-cream striped voussoirs and
    muqarnas hoods; the Dar al-Sitt Tunshuq facades, 10-12 m high, smooth ashlar with joggled lintels.
  - Graffiti. **H**

### 1.5 P4: Chain Street (x 420-640)
Photos: D05, D06, D08, D11 (souq part), D02, D03, D04, D09, D10, D12, D13, D14, D15.
- **x 420-520 (souq)**: 4-5 m.
  - Shops on both sides with hanging goods (D08, D11); closed green doors at night (D05).
  - Sheet canopies on scroll brackets; parts roofed by a **steel lattice of beams over the canopies** (D06).
  - Whitewashed vaults over short stretches (D11); low steps rising W in the distance (D11).
  - Mosque signs (Masjid ash-Shura, D06). **M-H**
- **x 520-640 (Mamluk approach)**: fewer shops.
  - Long plain 2-3 storey ashlar facades with rectangular grilled windows, AC units, electric cabinets.
  - **Wall lanterns on curved iron brackets**; ceramic signs "CHAIN GATE ST." and "BAB EL-SILSILA RD."; stone
    benches (D02, D03).
  - Carved window panels of the Turkan Khatun tomb (geometric and arabesque relief over iron window grilles, D04).
  - Mamluk inscription stones and the ceramic "EL-WAD RD." sign at the Al-Wad corner (D09). **H**
- **Vaulted passage** (w26492743, (566,45) → (601,55)): a pointed arch opening into a vaulted tunnel, with police
  barriers ("POLICE משטרה") and the sign "לכותל המערבי / THE WESTERN WALL ←" pointing to a side passage (D10, D03).
  D10 shows a Mamluk portal with a scalloped (interlaced) hood beside it. **H**
- **Bab al-Silsila porch** (w1393388444, then the gate building w291836687, landmark): a tall pointed arch with a
  moulded hood and colonnettes leading into a vaulted porch. Inside: the green double doors of the gate, a small
  green-domed kiosk, railings around a sunken area, a yellow fire hydrant (D15). Friday crowds and festoon lights
  under a transverse arch (D13). **H**
- **Wire-mesh nets** over the street, littered with objects thrown down (D14, from above). **M**
- The souq-street rule (`SOUQ_STREETS` "Silsileh" (0.8, 0.3)) suits x 420-520. East of x ≈ 520 the share should fall
  to ~0.3 with few canopies: this needs the Chain St ways split, or a per-way key for w277508275 E of x 520 (request).

### 1.6 P5: Souq al-Qattanin (Cotton Market, w291837739)
Photos: E01 (2021), E02, E03 (W portal), E04 (2024, all doors closed), E05 (2009, closed), E06 (2026, cam
(526.8,126.2)), E07 (2008, from the E end looking W), A16.
- A **straight vaulted hall ~95 m long** from the Al-Wad portal (534,141) to Bab al-Qattanin (627,150).
  - Clear width ~4.5-5 m between shop fronts.
  - **Pointed cross vaults in bays of ~4-4.5 m** on transverse pointed arches; crown ~7-8 m.
  - Each bay has a **square skylight opening** in the crown (light shafts, E01, E04, E06, E07). **H**
- **Shops**: one per bay on each side, in pointed-arched recesses ~2.5-3 m wide.
  - Closed: **tall dark brown or olive timber or steel 2-leaf doors** (E04) or cream / pale olive steel panel doors
    (E05), with padlock hasps.
  - Steel frames for hanging goods along the cornice; lanterns on scroll brackets at ~4 m (E04); string lights
    (E01). **H**
- **Floor**: worn slabs in courses, **rising E** towards the gate (E07 looks W down the slope). Survey: +5.8 m in 94 m
  (6 %). **H**
- Mid-hall the Khan Tankiz and Hammam al-Shifa open off the S side (Commons captions; not photographed here). **L**

### 1.7 P6: Haram gate lanes
- **Bab al-Hadid** (w26611968). Photos: E08 (cam (540.8,192.7), looking E), E12, E13, A22.
  - 3-4 m, residential and institutional.
  - **Ablaq** (red mizzi-ahmar and cream) Mamluk facades of the madrasas al-Arghuniyya, al-Muzhiriyya and
    al-Khatuniyya: pointed recessed doorways with green lattice gates, rectangular grilled windows (E12, E13).
  - A **flying arch** with a lamp box across the street (E12); a vaulted passage at the E end towards the Iron Gate
    (E08, E12).
  - Wall-top vegetation on a ruinous wall (E08); lantern brackets, Israeli flags on one house. **H**
  - The Little Western Wall court lies S of the gate (E10: huge drafted blocks of the Haram wall, a fence and shrubs
    on top). **M**
- **Aladdin St / Tariq Bab an-Nazir** (E half of w291836767). Photos: F06 (2022), F07, A10, F01.
  - 4-5 m with cars (F06).
  - The **Ribat al-Mansuri** portal: a tall pointed arch with red-white ablaq voussoirs (F06).
  - Shop tarps; vaulted at the Al-Wad end (F01).
  - The **Bab an-Nazir passage**: a dark vault with a green iron gate leaf opening on to the Haram trees (F07). **H**
  - The African community's ribats line it (Commons captions). **L**
- **Bab al-Ghawanima St** (w291836768 + steps w26492737). Photo: B12 (cam (568.3,402.8)).
  - A ~3 m lane with plain ashlar walls 3-4 storeys high, **mint-green steel doors**, a police barrier.
  - A dark arched passage at its S end (the building-passage steps). **M**
- **Barquq** (w26506004). Photo: F10.
  - A ~3 m lane at grade with a white globe lamp post and green shutters.
  - The **Ghawanima minaret** rises over a wall with a fence at its E end. OSM tags the whole lane as steps, layer -1.
    **M**
- **Ablution lane** (w291836769): no photo. Vaulted per OSM. **L**

### 1.8 P7: residential interior and open ground
- E of Al-Wad between Bab al-Hadid and Barquq (x 540-590, y 200-345), OSM maps detached blocks with gaps (see
  plan_north.png). Infill covers only a 9 m band along the streets, so the interior stays open. H01 (aerial) shows
  the block **densely built**, with small courtyards, not open ground (seen obliquely, **M-L**). OSM trees there:
  n14052609809-11 (516-569, 293-309), n14052609803 (592.5,355.4). Request: either manual buildings (if more photos
  are found) or leave as courtyards. This is not a street view; low priority.
- **Courtyards with trees**: Our Lady of the Spasm (C10), the hospice garden, the Umariya terrace. **H**

### 1.9 Western Wall Plaza (north part, in s09)
Described in **s07_kotel.md** (P1, the JQ steps, the north end block w394161633, the Mughrabi bridge). G01 (cam
(585.3,-11.1)) shows the plaza's W end: hoardings round the Beit Haliba excavation, a black steel fence, tall
ashlar Jewish Quarter buildings on the escarpment. **M**

---------------------------------------------------------------------------------------------------------------

## 2. LANDMARKS (described only; modelled by landmarks_city / landmarks_haram)

### 2.1 Ecce Homo arch and basilica (w744676490, arch node (549.6,402.2))
- A Roman round arch across the Via Dolorosa, springing at ~3.8-4 m (crown ~6 m), carrying a small room with **two
  rectangular grilled windows** on each face; total height ~10 m (B03, B06, B08). The soffit block under the arch is
  engraved "VIA DOLOROSA" (B07). Smooth pale stone. **H**
- Behind it to the N, the basilica's facade has a **rose window** and round lattice windows (B07). **M**
- landmarks_city.md item: arch 4.2 m wide; that note owns the dimensions.

### 2.2 Via Dolorosa minaret (w1394857844, n5921367466 (412.9,379.3))
- A white cylindrical shaft with a corbelled gallery and a short upper drum with a **green-copper dome and crescent**.
  It rises from a 3-storey building with arcaded balconies at the junction's SW corner (A03, A23, B05, B09, C08, C09).
  Top ~17-20 m above Al-Wad (C08 scaled from the 3-storey host). **H** form, **M** height.

### 2.3 Ghawanima minaret (landmarks_haram, (587.23,370.77))
- A square stone shaft with a corbelled balcony, an octagonal upper stage and a small dome, seen over a fenced wall
  from Barquq (F10). Owned by landmarks_haram (38.5 m). The generic block w291836716 must go (0.9).

### 2.4 Condemnation and Flagellation (w744674226, w744674450)
No new photo in this set (Commons has 36 + 88 files; categories listed in Provenance). OSM station node II
(589.3,419.5).

### 2.5 Bab al-Silsila (gate w291836687, minaret n13791836098 (639.7,84.1))
- Porch: see 1.5 (D15, D13). The twin-gate building and the minaret are in landmarks_haram.md.

### 2.6 Western Wall, Wilson's Arch hall
s07_kotel.md and landmarks_haram.md.

### 2.7 Notable ordinary buildings (override candidates, not landmarks)

| building | OSM | evidence | what to model |
|---|---|---|---|
| Austrian Hospice | w52890125 | C11 (garden front), H02, H03 (from its roof), A24 | 3 storeys + roof terrace. Ground-floor **round-arched arcade (loggia)**, 1st floor segmental-arched windows with keystones, 2nd floor paired round-arched windows. Warm cream ashlar with pinkish band courses; a parapet with flags (Austria, Vatican). ~15 m above its garden, which is ~4-5 m above the Via Dolorosa. Red-tile roofs on neighbouring pavilions show from its roof (A24, H03); which building they belong to is unclear (L). `wall: ashlar`, tint ~[1.03, 0.97, 0.88]. **H** |
| Our Lady of the Spasm | w277705915 | C10, H02, A23 | Gabled neo-Byzantine front in a courtyard; triple round-arched window; red-white banded portal arch up 5-6 steps; grey ribbed dome on a windowed drum. Gable apex ~12 m, dome top ~15 m. **M-H** |
| Armenian Catholic Patriarchate front | building at (433-440, 360-372) (infill f139 / f136 today) | C06 | Smooth ashlar, a round-arched portal on colonnettes with a relief in the tympanum, dark timber doors, a long banner at ~4.5 m. Needs a manual building or an OSM footprint (request). **M** |
| Praitorion | w744679915 | B04 | 4 storeys of smooth ashlar with green louvred shutters. **M** |
| Cotton Market portal block | E side of Al-Wad at (534-537, 136-146) (spec infill) | A17, E02, E03 | The portal described in 1.2.3; 2 storeys above it with grilled windows. **H** |
| Sabil al-Wad | at (508-511, 266-270), on the corner | A14 | The niche described in 1.2.2. Needs a facade feature (request). **H** |
| Turkan Khatun tomb | N side of Chain St at ~(616,61) | D04 | Two windows with carved geometric and arabesque panels above iron grilles. **M** |
| Ablaq madrasas of Bab al-Hadid | buildings S and N of w26611968 at x 590-618 | E12, E13 | Red / cream banded masonry, pointed doorways, a flying arch. Needs an `ablaq` wall type or tint bands (request). **H** |
| Ribat al-Mansuri | Aladdin St, N or S side x ~560-590 (unconfirmed) | F06 | Pointed ablaq portal. **M** |
| Dar al-Sitt Tunshuq | At-Takiyya, x ~418-440 (s04 / s09 boundary) | F02, F08 | Ablaq portals with muqarnas hoods. **M** |

---------------------------------------------------------------------------------------------------------------

## 3. GATES of the sector

The sector has no city gate. Its "gates" are the **Haram gates** on its E edge, all built by landmarks_haram:
1. **Bab al-Silsila** (Chain Gate) at the end of Chain St, behind its porch (D15). **H**
2. **Bab al-Mathara** (Ablution Gate, w291836686) at the end of the vaulted lane w291836769. **L** (no photo)
3. **Bab al-Qattanin** at the E end of the Cotton Market (E07 looks back W from inside it). **M**
4. **Bab al-Hadid** (Iron Gate, w291836690) at the end of Bab al-Hadid St (E08, E12). **M**
5. **Bab an-Nazir / al-Majlis** (w291836689) at the end of Aladdin St: a vaulted passage with a green iron leaf (F07).
   **H**
6. **Bab al-Ghawanima** at the end of Bab al-Ghawanima St, through a building passage and a tunnel. **M**
   OSM w620130982 "Council Gate" at (589-598, 346-352) sits at the tunnel w291836764.
Police barriers (grey or blue steel crowd fences marked "POLICE משטרה") stand at the head of every gate lane (D10, B12,
A22). **H**

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Lighting
- Wall **lanterns on curved iron brackets** (Chain St, Bab al-Hadid; D02, D03, E08, E04). **H**
- LED floodlight boxes on the walls of Jewish-owned houses (A08). **H**
- Fluorescent tubes under shop canopies (A02, C14). **H**
- White globe lamps on steel posts (Barquq, F10). **M**
- Ramadan light strings across Al-Wad, Aladdin St and Chain St (A10, F01, D05, D13). Seasonal; leave out or keep
  sparse. **H**

Signs and plaques
- **Ceramic street signs**: white glazed tiles with a coloured border, three lines Hebrew / Arabic / English, ~0.5 ×
  0.4 m at ~2.5-3 m: "VIA DOLOROSA", "BAB AL-GHAWANIMA ST." (B02), "ALAA AD-DIN ST." (A14, F01), "AL-QATTANIN ST."
  (A17), "BAB EL-HADID RD." (A22), "CHAIN GATE ST." / "BAB EL-SILSILA RD." (D02, D03), "EL-WAD RD." (D09),
  "AL-HAKKARI ST." (D12). **H**
- **Via Dolorosa station markers**: round dark bronze discs (~0.6 m) with Roman numerals, with reliefs (C12, A23).
  **H**
- Black heritage plaques; Western Wall direction signs (brown or white with an arrow, "THE WESTERN WALL", D10);
  municipal "Welcome to the Old City" boards hung on frames over Al-Wad (A02). **H**
- Shop signs: "PHARMACY" (green neon, A25, A03), "HAMEDIAN GALLERY" (C02), "ALADDIN Boutique Hotel" (C03, C05),
  the Armenian Catholic banner (C06). **H**
- House numbers: small white plates with black numerals ("103", A13); numbers painted on stone ("235", B02). **H**
- Tile plaque "ساحة المهندس الأردني 2017" on As-Saraya (blue Ottoman-style border; photo dropped from the set). **L**

Barriers, security
- Grey and blue steel crowd barriers ("POLICE משטרה") at the Haram gate lanes and the Chain St tunnel (D10, B12,
  A22). **H**
- CCTV camera clusters on brackets at every junction (C03, C05, C12, A07, A12). **H**
- Jewish-owned houses: Israeli flags, steel mesh fences or barbed wire on roof edges, rooftop guard posts (H04: a
  boxy guard cabin with a mesh fence). **H**
- **Wire-mesh nets** over Al-Wad and Chain St (D14). **M**

Street objects
- Grey electric cabinets and utility boxes (A05, A08, C14, D02); red pillar post box at the junction (C03). **H**
- Gas cylinders by the doors (A05); hand trucks (A05); ka'ak bread carts (E02); golf carts and police carts (C04,
  C05). **H**
- Small grey pyramid-capped bollards (Via Dolorosa S edge, B05). **M**
- Stone benches (C03, D02). **M**

Vegetation
- Hospice garden: **date palms, cypresses**, oleander (OSM trees (402-477, 387-424)); red geraniums in boxes on the
  terrace parapet (C02, C05, B05, B09). **H**
- Our Lady of the Spasm courtyard: a tree and potted plants (C10). **H**
- Capers and weeds in wall joints and on wall tops (A08, E08, E10). **H**
- Planted window cages with flower boxes on As-Saraya (photo dropped). **L**

Roofscape (H01 aerial 2013, H02, H03 from the hospice roof, H04, A24)
- Dense **flat roofs with low parapets**, many **shallow whitewashed domes** (often several in a row over the vaults
  of a shop range, A24), rooftop rooms, **black plastic water tanks**, solar water heaters, many satellite dishes and
  TV masts. A few red-tile roofs (hospice pavilions, Armenian Catholic buildings). **H**
- The roofscape rule (`roofscape.QUARTER["s09_wad"] = (0.0, 0.60, 2.0)`) fits; the heights do not (0.8).

---------------------------------------------------------------------------------------------------------------

## 5. TERRAIN

Levels (m asl; street datum 770.58 m = street_z 0) from `pipeline/terrain_street.street_z` against the OS 1865 spot
heights in data/terrain_street.json and the photos:

| place | street_z → asl | survey / photo | verdict |
|---|---|---|---|
| Al-Wad at the Via Dolorosa junction (425,374) | -33.5 → 737.1 | OS (421.5,372.1) 737.0; B (410.3,380.9) 737.8 | OK |
| Al-Wad at Station V (463,324) | -35.8 → 734.8 | OS (469.5,329.7) 735.2 | OK |
| Al-Wad at Aladdin St (512,268) | -36.8 → 733.7 | OS (517.7,268.0) 733.65 | OK |
| Al-Wad at Bab al-Hadid (525,195) | -38.5 → 732.1 | OS (524.7,193.2) 732.46, (513.6,198.5) 732.13 | OK |
| Al-Wad at the Cotton Market (534,141) | -39.2 → 731.4 | OS (537.8,156.6) 731.5, (540.6,130.0) 731.2 | OK |
| Al-Wad y 110-120 | -39.7 → 730.9 | underpass 731.0 at (536,110) | OK |
| **Al-Wad at (546,71)** | **-35.1 → 735.5** | underpass 730.6-730.8 at (541-551, 65-81); OS (532.2,76.4) 732.4 W of the street | **wrong by ~5 m** (the field follows the Chain St causeway); A21 shows the steps up to Chain St |
| Al-Wad passage under Chain St (555,34) | → ~738-739 | underpass 730.2 | **wrong by ~8 m** |
| Chain St at Bab al-Silsila (640,71) | -33.2 → 737.4 | Warren 737.3; pinned profile | OK |
| Chain St at x 554 | -32.1 → 738.5 | OS (554.7,43.2) 738.5 | OK |
| Chain St at x 496 / 433 | 743.7 / 748.0 | OS (496.3,23.7) 743.1; (418.7,12.8) 748.6 | OK; ~8 % between x 433 and 496: low steps (D11) |
| Via Dolorosa at the Ecce Homo arch (547,402) | -22.7 → 747.8 | OS (574.0,408.2) 746.15 | OK |
| Via Dolorosa at (507,394) / (461,383) | 742.8 / 740.2 | OS 742.8 / 740.05 | OK; grade 5-7.5 %, a **ramp** (B04, C04) |
| Via Dolorosa at the Flagellation (630,415) | -24.7 → 745.9 | OS (630.3,415.5) 745.24 | OK (+0.6) |
| Via Dolorosa at (679,429) | -27.7 → 742.9 | OS B (696.8,427.1) 740.7 | falls E to Lions' Gate |
| Via Dolorosa steps V → VI | 734.8 → 742.1 in 60 m (12 %) | no OS spot on the run; C13, C14 | steps OK (broad, low) |
| At-Takiyya W (425,250) → Al-Wad | 746.2 → 733.7 in 90 m (14 %) | OS (414.8,246.5) 748.6, (470.2,256.3) 738.2 | steps OK (F02, F08) |
| Aladdin St, Al-Wad → Bab an-Nazir | 733.7 → 737.8 in 92 m (4.5 %) | OS (593.7,274.0) 737.0 | **ramp, no steps** (F06 car) |
| Cotton Market, W → E | 731.3 → 737.1 in 94 m (6 %) | OS (579.1,144.1) 733.35, (610.8,149.7) 734.57 | rising ramp (E07) |
| Bab al-Hadid, W → E | 732.1 → 737.9 in 97 m (6 %) | OS (586.6,185.9) 736.7 | ramp or low steps (E08, E12) |
| Al-Khalidiyya, W → E | 746.7 → 734.2 in 108 m (11.6 %) | OS (419.4,101.5) 745.2, (487.4,125.4) 735.2 | steps with central ramps (F05) |
| Barquq, W → E | 735.9 → 743.6 in 140 m (5.5 %) | OS (536.0,335.5) 743.1, (472.4,354.7) 740.4 | probably a ramp with a few steps; OSM says steps (L) |
| Bab al-Ghawanima St, N → S | 746.3 → 743.7 | OS court (567.4,364.8) 747.1 | 12 steps down through the passage (OSM) |
| Western Wall plaza | flats -41.58 / -43.58 (729 / 727) | s07_kotel.md | |

Notes
- **Al-Wad is the valley bottom.** It falls ~6 m from the Via Dolorosa junction (737) to the Cotton Market (731) and
  stays at 730-731 to the plaza. Chain St crosses over its S end on a causeway at 737-738.5. The survey-based field
  is right everywhere except the last ~50 m of Al-Wad (see item 0.3). Request: implement terrain_street.json
  "underpasses" ("Al-Wad under Chain Street", pts and z_asl given there) as a local ramp in the ground mesh, with
  Chain St bridging it (the causeway already exists as the street above).
- **Spec step problems** (build/spec_s09_wad/steps_check.py; treads more than 1 m off `street_z`):
  - w291836767 At-Takiyya: 55 treads, up to **+8.5 m** at (511,268);
  - w277508271 Mughrabi bridge: 47 treads, up to +7.8 m;
  - w26506003 Via Dolorosa steps: 33 treads, up to +1.8 m (linear interpolation over a convex profile);
  - w26492734 plaza edge: 15 treads up to +7.1 m at (653,-23) (the plaza flats against the Mughrabi ramp);
  - small ones on Al-Khalidiyya (-1.1), Qukater Khoeir (+1.3), At Takiyyeh Road (-2.0).
- **Raised elements**: shop kerbs and platforms 0.15-0.2 m along Al-Wad (A02, A08). The hospice garden terrace is
  ~4-5 m above the Via Dolorosa (B05, C04). The Our Lady of the Spasm courtyard is a few steps above Al-Wad (C10). The
  Little Western Wall court is at the foot of the Haram wall (E10).

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **Al-Wad walkable end to end**, from the Via Dolorosa junction to the Western Wall plaza. Unblock the S end
   (w508241135 open strip, w277508274 covered) and keep its level at 730-731 m under the Chain St causeway (0.3, 5).
2. **Via Dolorosa open** from Al-Wad to Lions' Gate: open-area strip over w44830379, no steps, a 5-6 m sett ramp with
   a central slab gutter (0.1, 0.12, 1.3).
3. **Cotton Market** on w291837739 as a vaulted hall: covered street, shop rows on both sides, skylights,
   tall closed doors, floor rising E. Demote w291836769 to a vaulted lane with few shops (0.2, 1.6).
4. **Al-Wad width and heights**: 3.5-4 m in the middle, 4.5-6 m at the N end; 3-4 storeys (11-14 m) with fenced
   roof terraces (0.7, 0.8, 1.2).
5. **At-Takiyya / Aladdin St steps split at Al-Wad**: Aladdin St a ramp, At-Takiyya W a stair (0.4).
6. **Street arches**: remove the solid `building=roof` blocks (w1393388437, w1393388444, w1392511599, w1393158496,
   w1393163032, w1394857839, w1393380722, w1393391237, w1393375646, w1393375644) and, where the code allows, put sabats or flying arches back:
   Al-Wad (519,228), the Via Dolorosa steps ×3, Bab al-Hadid (0.5).
7. **Vaulted stretches of Al-Wad**: (468-488, 302-318) and the Aladdin junction (505-515, 262-272) (0.11).
8. **Closed-shop palette**: teal, pale lime-olive, dark green, olive-grey and cream steel doors with hasps; dark sheet
   canopies on black perforated or scroll brackets; green fabric awnings (0.13, 1.2, 1.4).
9. **Austrian Hospice** front and its **garden wall** along the Via Dolorosa: arcaded 3-storey front, flags, the
   4-5 m battered retaining wall with a green fence, palms and cypresses (2.7, 1.3).
10. **Chain Street E part**: Mamluk facades with lanterns on curved brackets, the vaulted tunnel w26492743 (covered
    street), the Bab al-Silsila porch (0.6, 1.5).
11. **Haram gate lanes**: ablaq facades and a flying arch on Bab al-Hadid; the Ribat al-Mansuri portal and cars on
    Aladdin St; police barriers at every gate lane (1.7, 3).
12. **Junction set piece at Al-Wad / Via Dolorosa**: the Via Dolorosa minaret closing the N view, the hospice terrace
    with flags, the menorah on the building to the N, the red post box, the Armenian Catholic banner, station discs
    (1.2.1).
13. **Stepped lanes W of Al-Wad** (Via Dolorosa V→VI, Al-Khalidiyya, At-Takiyya): broad low steps with central
    ramps, flying arches, the pink oriel at Station VI (1.4).
14. **Wire-mesh nets, flags and CCTV** on Al-Wad and Chain St: the signs of the Jewish-owned houses (0.13, 4).
15. **Roofscape and the Ghawanima duplicate**: shallow domes in rows, tanks, dishes, guard posts. Remove w291836716
    so the Ghawanima minaret stands clear (0.9, 4).

---------------------------------------------------------------------------------------------------------------

## Provenance

80 Commons photos in `data/photos_ref/s09_wad/` (1280 px standard thumbnails; `index.json` has key, title, page,
author, licence, date, lat/lon and local x/y where geotagged, description and size). Fetched with build/spec_s09_wad/
commons.py (1.6 s between requests, Retry-After honoured; Commons answered with frequent 429s / Retry-After ~50 s
because other workers shared the IP).

Sources used:
- Geosearch of the whole sector polygon: 1105 geotagged files, listed in build/spec_s09_wad/geo_found.json.
- Commons categories: Al-Wad Street; Via Dolorosa (35 subcategories, including Third, Fourth, Fifth Station, Arch of
  Ecce Homo); "Bab el-Silsileh Rd. / Chain Gate St."; Cotton Merchants' Market; Bab el-Hadid Road;
  "Aladdin Street, Jerusalem"; At-Takiyyah Ascent; Barquq Street; Ghawanima Gate Street.
- Category lists of the streets of the Muslim Quarter for names: Al-Khalidiyya Ascent, As-Saraya Ascent, "Lower north
  entrance to the Western Wall Plaza", Sabil al-Wad, Khan al-Sultan (41), Tankiziyya (39), Tashtamuriyya (30),
  Khalidi Library (43), Hammam al-Ayn (20), Khan Tankiz (25), Church of the Flagellation (88), Church of the
  Condemnation (36), Western Wall Plaza (250). These were not downloaded, and are the obvious next sources.

The most useful photos:
- **The 21 Dec 2025 walk by מקף־עברי** (CC BY-SA 4.0): A01, A07, A11, A12, A16-A19, C02-C06, C12,
  C13, E08, E10.
  - Its positions are **10-30 m off in places**: A16 and A17 are tagged at (531,122) and (535,112), 20-30 m S of the
    Cotton Market portal they show (OSM (534,141)). It is the same series as s04_sepulchre A01-A03.
  - Use those positions ±20 m.
- **Bahnfrend 2019** (CC BY-SA 4.0; A02, A05, A08, C10, C11, G01).
- **Ludvig14 2015** (B03-B05, F02).
- **Djampa 2010-17** (A13, A21, B07, C09, C14, D14).
- **Bukvoed 2017-24** (CC BY 4.0; D02-D04, D12, E01-E03, E12, E13, F06).
- **Deror Avi 2010** (A10, B12, F01, F07, F10).
- **Berthold Werner 2008** (public domain; B08, B09, E07).
- **Rahaf Tami 2024** (E04, all Cotton Market doors closed).

Groups: A Al-Wad (21 photos), B Via Dolorosa east (10), C Via Dolorosa III-VI (12), D Chain Street (13), E Cotton
Market / Bab al-Hadid / Little Western Wall (11), F Aladdin / At-Takiyya / Barquq / Al-Khalidiyya (8), G plaza (1),
H roofscape (4).

Position caveats:
- B06 / B07 (Oleg Moro, Djampa) carry place geocodes near the arch, not exact camera positions.
- H01 (aerial) is tagged at (402.4,308.0), which is a place geocode.
- H02 / H03 are tagged at the hospice roof, which is correct within ~10 m.
- The A23-A25, D12-D15, E01-E05, E12, E13 and F06-F10 photos have no geotag. Their positions come from what they show:
  street signs, landmarks and the OSM plan.

Dropped after review (deleted from the folder and the index): 15 photos with close-ups, people or off-sector content
(keys A04, A06, A09, A15, B10, B11, C01, C07, D01, D07, E09, E11, F03, F04, G02). Facts quoted from them are marked
**L** above.

Scratch files: build/spec_s09_wad/ (geo scan, metadata, contact sheets, the width / steps / profile scripts and plan
images plan_north.png, plan_mid.png, plan_south.png). Render of the current model at one photo viewpoint (wad_n,
with the side-by-side against A02): renders/sectors/s09_wad/current/ (see 0).

No code, profile or override was written in this pass.
