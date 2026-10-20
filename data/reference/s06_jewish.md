# s06_jewish: Jewish Quarter (Hurva Square, Cardo, Batei Mahase): visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (lat 31.7766282, lon 35.2275435).
Sector polygon (data/sectors.json): x 250..600, y -330..-42, cut on the south-east by the city wall. You enter from
David St / Chain St (s05/s09) down Habad St, the Cardo or HaYehudim, from the Armenian Quarter (s01) down the stepped
lanes Or HaHayim / HaShofar / HaMalakh, from Zion Gate (s02) along the Batei Mahase road and the parking, or up the
escarpment stairs from the Western Wall plaza (s07).
Photos: `data/photos_ref/s06_jewish/KNN_<pageid>.jpg`, cited below as **A01**, **D07** and so on. Titles, authors,
licences, dates and GPS are in `index.json` there. Groups: A = HaYehudim north and the covered Cardo, B = HaYehudim
south, C = Cardo arcade / roofed excavation, D = Open Cardo, E = Habad St, F = Or HaHayim / HaMalakh (west lanes),
G = Hurva Plaza, H = Tiferet Israel St / housing, I = Misgav Ladach, J = HaTamid and the escarpment, K = Batei Mahase
Square, L = Beit El / Gal'ed / HaChatzotzrot lanes, M = Plugat HaKotel / HaOmer / HaSho'arim / Broad Wall, N = Gan
HaTkuma, O = St Mark's, P = aerial. Photos already downloaded by the landmark pass are cited by their path
(`data/photos_ref/landmarks_city/hurva_02_8333697.jpg` etc.).
Camera positions come from EXIF GPS where the file has it ("cam (x,y)"). The 2025-12-21 walk by מקף־עברי (A01-A05,
B01, B02, D01-D04, G01-G03; Fujifilm, EXIF GPS) and Bahnfrend 2019 (D05-D07, I01, I02) are the reliable positions;
several other geotags are place geocodes shared by many files (428.8,-243.7 = Batei Mahase Square; 364.3,-155.0 =
Hurva; 389.0,-239.3 = Four Sephardic Synagogues) and are not used as camera positions.
Scale comes from people (1.7 m), doors (2.2 m) and OSM edge lengths.
Confidence: **H** = seen clearly in 2+ photos, or OSM geometry plus one photo; **M** = one clear photo or a
consistent estimate; **L** = inferred or seen only at an angle.

> Status: complete (research pass, 2026-10-20). 77 photos in `data/photos_ref/s06_jewish/` (64 with GPS). Commons
> was rate-limiting thumbnails heavily (HTTP 429 with Retry-After 600 s, honoured), so 11 lower-priority selections
> were skipped; 13 downloaded files were discarded at review. No renders were made in this research pass.
> Coverage: HaYehudim, the three Cardo sections, Habad St, Hurva Plaza, Tiferet Israel St, Misgav Ladach, HaTamid,
> Batei Mahase Square, the west lanes and the Beit El / Gal'ed / HaChatzotzrot lanes are photo-backed. The
> south-east (Batei Mahase road, Nahamu, HaGitit, Cardo Minimus, the parking) and Yeshivat HaKotel / Porat Yosef
> street fronts are described from OSM and long views only.

---------------------------------------------------------------------------------------------------------------

## 0. Key facts and likely model errors (summary)

1. **The Jewish Quarter is a rebuilt, clean ashlar quarter, not a rubble one.** After 1967 almost every street
   wall was rebuilt or refaced in dressed limestone: either smooth-sawn ashlar (B02, D03, G02, I01, I07, M05) or
   pitched "rock-faced" ashlar with drafted margins (A03, E08, M01, M04), cream to pinkish, in regular courses
   ~0.25-0.35 m high, very clean, with crisp mortar joints. Only a minority of surviving older fabric is rough,
   weathered honey-grey rubble or old ashlar (Habad St north E01-E03, Or HaHayim F01-F02, HaChatzotzrot L01, the
   Batei Mahase / Rothschild buildings K01-K05, St Mark's O01). **The spec has `wall: rubble` on all 296
   buildings.** H (20+ photos)
2. **HaYehudim (Jewish Quarter Rd), the main street, is tagged `layer=-1` in OSM** (way 4710079, and its tunnel
   290722441). infill.py skips layer<0 streets, so **infill pieces sit across the street at six places**: f157
   (339,-80..-88), f154 (336,-98..-104), **f151 (336,-118 → 333,-137, 19 m, the approach to the Hurva)**, f155
   (330,-159..-163, the Open Cardo square), **f329 (326,-193 → 325,-209, the café widening, A12, B01)** and f331
   (326,-235..-240, the tunnel). The souq profile and steps.py also ignore it. Photos show an open street or square
   at every one of these points (A10, B06, B07, D06, D07, A12, B01, B03). H. This needs a code/spec change (requests).
3. **The Cardo is three different sunken / covered places along HaKardo 123231486 (also `layer=-1`, so not vaulted
   by covered_ways):** (a) y ≈ -48..-95, a **vaulted market arcade** with pointed transverse arches, cross vaults,
   shops in arched side bays and black iron gates (C03, C05, A05); (b) y ≈ -95..-150, the **excavated Byzantine
   Cardo under a modern dark roof on black square piers**, ~3 m below HaYehudim, with one colonnade, an ancient wall
   and a timber-beam reconstruction (A01, A02, A04, C01, C02); (c) y -170..-196, the **Open Cardo: an open trench
   ~4-5 m deep** with 6-8 standing columns, railed parapets, stairs and a bridge stair from Habad St (D01-D08).
   None of this exists in the spec (the trench even holds infill f328). H for (a) and (c), M for the extent of (b).
4. **Heights: a continuous 3-4 storey street wall, 10-14 m, flat roofs with railings.** Median spec height is
   9.7 m and the 83 infill pieces are 6-9 m. Photos show 3-4 storeys almost everywhere (B07, E04, G02, G03, F03,
   I01, I07), 4-5 storeys above the Cardo trench (D03, D05). Roofs are flat terraces with black or white steel
   railings, timber/steel pergolas, solar heaters and a field of small white domes
   (`landmarks_city/hurva_02_8333697.jpg`, P01). H
5. **Hurva Plaza** (way 290730185, 2170 m²) is the quarter's living room: large pale slabs, trees (pine/cypress,
   olive, ficus, OSM tree nodes), stone benches, café umbrellas and 3-4 storey ashlar fronts with **brown louvred
   shutters** (G02), the Hurva on its podium, the **golden Menorah in a glass cylinder** (since 2018) and a red
   Mandate-era pillar box (G08). H
6. **Batei Mahase Square** (way 44376187): on its west side **Rothschild House** (w290722438, e2 (436.3,-248.5)
   faces E) is a two-storey **double arcade** (round/segmental arches on square piers below, an open round-arched
   loggia above, 3 broad steps), with a re-erected Roman column, tall cypresses and olives in front (K01-K05). H
7. **Streets are pale slab lanes with globe lamps and flying arches.** Narrow lanes (2-4 m) paved with pale
   rectangular slabs in courses and a slab gutter on the centre line, round manholes, **white globe lamps on black
   curved wall brackets** (the quarter's signature) or black lanterns, steel handrails on the slopes, and frequent
   flying arches and vaulted passages (Habad north, HaYehudim, Beit El, HaChatzotzrot, HaMalakh). H
8. **Doors and shutters**: dark brown panelled timber doors, dark green or grey steel doors, white steel doors with
   arched fanlights; shutters white louvred timber (Habad south, E04), brown louvred (Hurva Plaza, G02), rust-brown
   steel (M01), amber timber (F05). Shops have glazed arched fronts with dark frames, hanging signs and, closed,
   **cream/white panelled doors** in the Cardo arcade (C05). Teal souq doors are wrong here. H
9. **St Mary of the Germans** (w290733222, OSM ruins=yes) is a **roofless Crusader ruin** in a sunken garden; the
   spec builds a 19.2 m solid block. H (OSM tags + Commons category). Two `building=roof` canopies are also built
   as solid blocks, one of them across HaYehudim (w1393297095, (339.6,-70.3), 11.6 m). M
10. Terrain: a plateau at street_z -13..-7 (52 OS 1865 spots, fit within 0.13 m median) that drops 26 m to the
    Western Wall plaza in ~70 m on the east and climbs 6-12 m into the Armenian Quarter on the west (Or HaHayim,
    HaShofar, HaMalakh are stepped). street_z has a suspicious 2.8 m dip on HaYehudim at y ≈ -84 (one 1865 spot;
    section 5). H for the frame, L for the dip.

---------------------------------------------------------------------------------------------------------------

## G. OSM geometry of the core (from data/osm_local.json and data/spec/s06_jewish.json)

Sector polygon (data/sectors.json): x 250..600, y -330..-42, cut on the south-east by the city wall (Dung Gate
stretch, (584,-207) → (535,-262) → (473,-290) → (460,-330)). 296 spec buildings: 202 OSM ways, 11 relations,
83 infill pieces (`f…`, pipeline/infill.py). All 296 are currently `wall: rubble`, `shops: false`,
`roof: flat`; median height 9.7 m (min 3.0 = the Hurva podium, max 19.2 = St Mary of the Germans).
62 buildings carry vernacular domes, 34 a rooftop room.

| feature | OSM | position (local m) | notes |
|---|---|---|---|
| Hurva Synagogue (landmark) | w45081545 (podium, h 3) + parts 546355656 (h 16), 372306586 (dome, h 24) | x 342-378, y -156..-133 | built by landmarks_city.py; podium edge e1 (377.3,-144.5) faces the plaza (92°) |
| Hurva Plaza | way 290730185 (pedestrian area, sett) | x 352.7-417.0, y -185.1..-117.9, 2170 m² | L-shaped: the wide part is east of the Hurva (x 379-417); a tongue runs south-west to (353,-185) |
| Sidna Omar mosque (minaret host) | w1394070804 | edges e0 (357.8,-161.4) faces 185°, e1 (363.2,-158.8) faces 97° | minaret built by the Hurva builder at (354.6,-157.3) (landmarks_city.md §3) |
| Ramban Synagogue | w290730186 (synagogue) | x 338-352, y -174..-156 | e0 (343.6,-159.8) faces 277° onto HaYehudim; partly sunken (photos) |
| Chabad Welcome Center / Tzemach Tzedek area | w290723473 (synagogue) | x 310-326, y -164..-153 | e4 (317.3,-163.4) 15 m faces 187° onto the Open Cardo square |
| Open Cardo square | way 1545911834 (pedestrian area) | x 312-338, y -192..-163, 638 m² | HaYehudim crosses it at x 326-328 |
| Open Cardo trench | way 1545911833 (archaeological site) | x 314.1-319.7, y -185.8..-170.3, 66 m² | the sunken excavated Cardo with columns; HaKardo 290723470 runs in it |
| Steps over the trench | way 120425139 (steps, layer 1, incline down) | (308.6,-168.3) → (328.1,-169.6) | Habad St down to the Open Cardo square, bridging the trench |
| South steps out of the trench | way 508238575 (steps, paving stones) | (319.2,-196.1) → (326.0,-197.3) | |
| Four Sephardic Synagogues (landmark) | w29265134 | x 357-402, y -245..-199, 1153 m² | sunken courtyard type (seph_01) |
| Tiferet Yisrael Synagogue (landmark) | w195100862 (historic=ruins) | x 444-461, y -149..-127 | north face e2 (451.5,-128.2) on Tiferet Israel St, faces 354° |
| Batei Mahase Square | way 44376187 (pedestrian area) | x 428.0-484.3, y -286.8..-227.9, 1680 m² | Rothschild House w290722438 on the west (e2 (436.3,-248.5) 28.4 m faces 90°) |
| Batei Mahase south range | w290725362 + infill f363 | e3 (478.5,-253.6) 45.8 m faces 339°; f363 e9/e11 (471.7,-255.0)/(444.9,-278.2) | the long almshouse range (no clear photo in this set) is partly infill in the spec |
| Aish HaTorah yeshiva (Batei Mahase) | w290725352 (college) | x 446-474, y -230..-215 | south faces e16/e18/e20 (y ≈ -228..-230) face 179° onto the square |
| Yeshivat HaKotel | r3863218 (school) | x 411-499, y -188..-139, 2231 m² | Wohl Archaeological Museum (Herodian Quarter, n7613330285 (435.6,-158.2)) is in its basement |
| Porat Yosef yeshiva | w290726629 (school; OSM name:en wrongly "Yeshivat HaKotel"), amenity area 1545234304 | x 516-577, y -191..-139, 2208 m² | the big domed block on the escarpment above the Western Wall plaza; e15 (549.5,-141.4) 40.8 m faces 353° |
| Church of St Mary of the Germans | w290733222 (church, ruins=yes, levels 5) | x 499-525, y -125..-109 | a roofless Crusader ruin in a sunken garden; the spec builds a 19.2 m solid block |
| Burnt House museum | node n561134517 | (488.3,-114.8) | basement museum, no street feature |
| Broad Wall | node n4542880989 + park 1545547646 | (388.9,-76.5); park x 372-389, y -91..-75 | sunken excavation behind railings |
| Zion Gate parking | way 290701320 (parking) | x 306-385, y -317..-262, 3353 m² | asphalt, service ways 290701296/300/305/314 |
| Garden of the Redemption (Gan HaTkuma) | way 290701310 (archaeological site) + parks 290701309/299, playground 290701298 | x 300-462, y -404..-304 | mostly in s02; the north edge (y -304..-330) is in s06 |
| Retail landuse along HaYehudim / Cardo | way 1544671583 (landuse retail) | x 299-355, y -269..3 | the shopping spine of the quarter |
| St Mark's (Syriac) monastery | node n2710911176 (305.8,-61.8), church n563992070 (288.8,-69.4) | w1393297058 (christian, 115 m²) | west edge of the sector, Ararat St |

Streets (OSM centrelines, in-sector part):
- **Jewish Quarter Rd (HaYehudim)** way 4710079 (`name:en` "Jewish Quarter", **layer -1**, sett): (342.4,-45.9) →
  (340.1,-62.8) → (339.8,-77.6) → (335.9,-93.3) → (335.8,-103.2) → (337.0,-108.3) → (335.9,-127.1) → (333.8,-132.1) →
  (328.1,-169.6) → (328.0,-175.3) → (326.3,-190.9) → (326.0,-197.3) → (325.1,-204.4) → (324.5,-218.7) →
  (328.5,-219.0);
  then way 290722441 (**tunnel**, layer -1) (328.5,-219.0) → (328.2,-230.4) → (326.3,-234.4) → (326.8,-243.6); then
  way
  290722436 (open) (326.8,-243.6) → (327.0,-247.8) → (329.6,-267.6), and footway 496313367 on to the parking.
- **HaKardo** way 123231486 (layer -1, tunnel): (328.6,-48.7) → (328.2,-59.5) → (325.9,-82.3) → (326.2,-93.6) →
  (324.3,-106.1) → (323.9,-115.6) → (320.9,-172.7) (the covered Cardo arcade and the roofed excavation); then way
  290723470 (open, paving stones) (320.9,-172.7) → (319.6,-190.8) → (319.2,-196.1) in the Open Cardo trench.
- **Habad St** way 44376195 (pedestrian, sett; `SOUQ_STREETS` "Habad Street" (0.6, 0.2)): (312.8,-100.8) →
  (310.1,-131.0) →
  (309.9,-153.7) → (308.6,-168.3) → (306.8,-180.5) → (306.1,-195.3) → (305.0,-203.7) → (304.4,-233.7) →
  (305.7,-270.6) →
  (303.3,-302.0) → (298.9,-323.7) …; north of y -100 it is way 44376194 "Habad" (tunnel) (316.2,-44.0) →
  (312.8,-100.8).
- **Tiferet Israel St** ways 26612859 + 254576587 (sett): (390.4,-117.9) → (400.0,-122.3) → (413.5,-124.5) →
  (441.1,-126.9) →
  (460.7,-124.9) → (467.1,-128.6) → (478.6,-138.7) → (496.7,-137.4) → (503.5,-134.6).
- **Misgav Ladach** way 290730038: (497.6,-36.7) → (498.5,-47.1) → (497.7,-62.4) → (498.0,-85.4) → (496.9,-89.3) →
  (498.9,-120.6) → (503.5,-134.6) → (504.6,-140.0) → (500.9,-149.0); tunnel 290730039 (500.9,-149) → (500.9,-167.7);
  footway 368473452 on south to (491.8,-238.3) → (501.0,-243.5); steps 26492742 (tunnel, down) (501.0,-243.5) →
  (505.0,-255.3).
- **HaTamid** way 26493218 (498.0,-85.4) → (535.2,-85.6) → (536.6,-86.5), then steps 29388395 (down) to
  (557.0,-106.4).
- **Stepped descent to the Western Wall plaza** steps 29388393 (cobblestone, 94 m): (504.1,-135.6) → (514.2,-135.0) →
  (515.2,-142.0) → (538.2,-140.3) → (560.1,-137.7) → (557.0,-106.4), plus 29388399 / 368474893 / 288016710 to the
  checkpoint (563.5,-86.6) and the bus loop. Footway 722734611 "HaKotel HaMaaravi" (527.3,-21.9) → (536.6,-86.5).
- **Lohamei HaRova BeTashah** 44376196 (389.9,-131.6) → (335.9,-127.1): the north edge of the Hurva block.
- **Mishmerot HaKehuna** 254576583 (357.2,-177.9) → (410.9,-168.4) (south edge of the plaza), 254576585, then 26493225
  (353.6,-190.0) → (355.2,-224.8) → (366.1,-234.5) → (374.3,-270.6) along the Four Sephardic Synagogues.
- **HaMekubalim** 254576588 (409.9,-176.4) → (413.5,-124.5): the east edge of the plaza.
- **Beit El** 290722435 (354.6,-208.1) → (372.6,-199.5) → (401.5,-199.8) → (408.5,-190.2); steps 254576586
  (353.6,-190.0) → (362.7,-189.2) and 254576584 (362.7,-189.2) → (362.8,-176.8).
- **Or HaHayim** 290691380 (246.4,-151.3) → (268.2,-153.2) → (284.0,-158.6) → (290.1,-166.1) → (308.6,-168.3);
  **HaShofar** 123255617 (306.8,-180.5) → (251.5,-176.9) → (218.7,-188.6); **HaMalakh** 26506016 (306.1,-195.3) →
  (246.8,-203.9). All three climb west into the Armenian Quarter (see 5).
- **Plugat HaKotel / "Off the Wall"** 26496073 (339.8,-77.6) → (371.3,-78.3) → (375.5,-82.8) → (374.0,-94.0) →
  (390.4,-117.9), and 290731784 (363.4,-78.2) → (365.7,-35.9); **Bonei HaHoma** 123250581, 290731907; **HaOmer**
  290732619
  (442.1,-24.1) → (446.4,-90.3); **HaSho'arim** (unnamed in osm_local) footways 123245527 / 123250579.
- **Hayei Olam** 29264777 (408.5,-190.2) → (500.9,-167.7) along the south face of Yeshivat HaKotel; **HaKaraim**
  123250578; **Gilad** 26613951 (417.9,-232.2) → (425.2,-293.3); **HaChatzotzrot** 26613952 (418.0,-271.9) →
  (376.3,-277.9); **Beit HaSho'eva** 26613401, **Nahamu** 724596294, **Mamadot Israel** 290725363, **HaGitit**
  26493223 /
  724596293 (tunnels) / 368474204 (steps).
- **Batei Mahase road** 496167693 (residential, asphalt): (355.7,-318.4) → (387.9,-317.3) → (412.6,-315.1) →
  (437.6,-305.7) → (469.9,-288.1) → (518.2,-265.3) → (547.1,-239.9) → (575.6,-190.7) → (582.5,-164.7) → (588.0,-141.7)
  (the bus loop at the Western Wall); a parallel concrete footway 1545238187 runs inside the wall.

Widths. OSM footprints cover the quarter unevenly (many courtyards and small houses are unmapped), so the
perpendicular-ray widths are noisy: medians 3.4-5.7 m on HaYehudim south of y -219, 3.5 m Hayei Olam, 4.0 m Beit El,
4.8 m Nahamu, 5.4 m HaKaraim, 2.3 m HaChatzotzrot (min 1.8), 7-11 m elsewhere where one side is unmapped. The spec
(after infill) gives a uniform 2.6-3.3 m on most footways (Habad 3.2, Or HaHayim 2.7-2.8, Misgav Ladach 3.0,
Tiferet Israel 4.6). Photo estimates (people, doors):
- Habad St south of y -195: 2.5-3 m (E04, E05, E06, E08). Habad north (vaulted): ~3.5-4 m under a 5 m vault (E02).
- HaYehudim at the Hurva (y -140): ~3 m between rock-faced walls (A10); at the Ramban (y -170): ~4 m (B07); the
  Open Cardo square and the café widening at y -195..-215 are 10-20 m open (B06, A12).
- Cardo arcade: ~5.5 m between piers, plus 2-3 m deep shop bays (C03).
- Or HaHayim: 2.5-4 m (F01-F03); HaMalakh ~2.5 m (F05); HaChatzotzrot ~1.8-2 m (L01); Gal'ed vault ~2 m (L02).
- Tiferet Israel St at Hurva Plaza: 4-5 m (G03); near Tiferet Yisrael ~3.5 m (H02).
- Misgav Ladach south (by Yeshivat HaKotel): 2.5-3 m between 12-15 m high walls (I01, I07).

Spec state (data/spec/s06_jewish.json, as built before this pass): 296 buildings, all `wall: rubble`,
`shops: false`, `roof: flat`, tint ≈ [1.0, 0.97, 0.9]; median height 9.7 m; 1229 facades, 122 shop openings (the
Habad St souq profile); door/shutter cells mostly `glass`, `door_wood`, `shutter_green`, `door_green`,
`shutter_brown`, `shutter_blue`. Vaulted passages: Habad 44376194, Misgav Ladach steps 26492742, HaGitit
26493223/724596293, and three short unnamed tunnels; **not** the layer -1 tunnels HaYehudim 290722441, Misgav Ladach
290730039 (infill f71 sits on it) and HaKardo 123231486. Landmarks in the sector: w45081545 Hurva, w29265134 Four
Sephardic Synagogues, w195100862 Tiferet Yisrael.

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and STREET PROFILES

### 1.0 Character
A tidy, bright, residential-and-tourist quarter rebuilt after 1967 on the old street plan. It reads very
differently from the souqs:
(a) **narrow pale lanes** between continuous 3-4 storey walls of clean dressed limestone, with globe lamps on curved
brackets, steel handrails, potted plants and bougainvillea, flying arches and short vaulted passages, and many
stone stairs (the quarter sits on a slope that falls east);
(b) **a shopping spine** north-south: the vaulted Cardo arcade and HaYehudim, with glazed arched shopfronts, hanging
signs, cafés and Judaica shops, plus Tiferet Israel St east of the Hurva;
(c) **excavations and ruins set into the street level**: the roofed Byzantine Cardo, the Open Cardo trench with its
columns, the Broad Wall pit, the Hurva podium, the sunken Four Sephardic Synagogues court, the St Mary of the Germans
ruin and the Burnt House;
(d) **three squares**: Hurva Plaza (trees, cafés, the white Hurva dome and the Sidna Omar minaret), the Open Cardo
square (palms, tiered seating, parked cars) and Batei Mahase Square (Rothschild House arcade, cypresses, a Roman
column);
(e) **the eastern edge**: big modern yeshiva blocks (Yeshivat HaKotel, Porat Yosef) on the scarp above the Western
Wall plaza, with stairs and lookouts over the Temple Mount.
Skyline: flat roof terraces with railings, pergolas, water heaters, small white domes; the Hurva dome (~26 m) and
the minaret dominate; few red-tile roofs. Vehicles do enter (cars at the Open Cardo square, the Hurva tongue, the
south end of HaYehudim: B06, A12, G06, `landmarks_city/hurva_01_163083960.jpg`).

### 1.1 Profile table (which OSM street gets which profile)

| profile | OSM streets (name:en / way) | key look |
|---|---|---|
| J1 vaulted Cardo arcade | HaKardo 123231486, y ≈ -48..-95 (layer -1 tunnel) | pointed transverse arches, cross vaults, arched shop bays on raised sills, cream panelled shop doors, lanterns, iron gates at the ends |
| J2 roofed excavation | HaKardo 123231486, y ≈ -95..-150 | sunken ~3 m, Byzantine colonnade, ancient wall, modern dark roof on black piers, railed walkway at street level |
| J3 open excavation trench + square | HaKardo 290723470, archaeological site 1545911833, square 1545911834, steps 120425139 / 508238575 | trench ~4-5 m deep with columns, parapets with black railings; square above with palms, tiered seating, cars |
| J4 shopping street | Jewish Quarter Rd 4710079 (y -42..-219), 290722436; Tiferet Israel St 26612859 + 254576587 (x 390-470); Habad St 44376195 at y -160..-185 | 3-6 m, glazed arched shopfronts with dark green/black frames, hanging signs on wrought brackets, a few striped awnings, globe lamps, flying arches |
| J5 vaulted passage | Habad 44376194 (y -44..-100), HaYehudim tunnel 290722441, Misgav Ladach tunnel steps 26492742, Gal'ed vault, HaGitit 26493223 / 724596293 | pointed barrel or cross vaults ~4-5 m high, plastered or rubble, iron-grille doors, central gutter |
| J6 residential lane | Habad St south of y -190; Beit El 290722435; Gal'ed 26613951; HaChatzotzrot 26613952; Mishmerot HaKehuna 26493225; Misgav Ladach 290730038 / 368473452; Plugat HaKotel 26496073 / 290731784; HaOmer 290732619; HaSho'arim; Hayei Olam 29264777; HaKaraim 123250578; Nahamu 724596294; Beit HaSho'eva 26613401 | 2-4 m, residential doors, shutters, globe lamps, handrails, plants, sabats |
| J7 stepped lane | Or HaHayim 290691380, HaShofar 123255617, HaMalakh 26506016 (west, up into the Armenian Quarter); HaTamid 26493218 + steps 29388395; the descent 29388393; HaKotel HaMaaravi 722734611 | flights of broad stone steps with central or wall handrails, landings, flying arches |
| J8 plaza | Hurva Plaza 290730185; Batei Mahase Square 44376187 | large pale slabs, trees, benches, cafés |
| J9 service road | Batei Mahase road 496167693, parking 290701320 and its service ways | asphalt, kerbs, parking, the city wall on the south |

### 1.2 J1: the vaulted Cardo arcade (HaKardo, y ≈ -48..-95)
Photos: C03 (2011), C05 (closed, night), A05 (cam (335.7,-97.3), 2025, looking N into the arcade).
- **Section**: a long hall ~5.5 m wide between square piers, roofed by **cross vaults between pointed transverse
  arches** springing at ~3.5 m, crown ~6 m. Pale limestone, smoothed and somewhat weathered; plastered vault cells.
  H (C03, A05, C05)
- **Shops**: in the side bays between the piers, under round-arched heads, set on **raised stone sills / platforms
  0.2-0.35 m** with 1-2 steps; open shops are glazed with dark frames and goods outside; **closed shops have
  cream/white-painted panelled two-leaf doors** (vertical boards) and a few dark green ones (C05). H (C03, C05)
- **Ends**: pointed stone portals with **pairs of black iron grille gates** whose leaves have arched tops (A05 at
  y ≈ -97 facing S). H
- **Lighting**: brass/black hanging lanterns on chains down the axis, floodlights on the piers (C03, C05, A05). H
- **Floor**: pale rectangular slabs, glossy, with an **octagonal stone well-head** with an iron frame in the
  middle (C03) and round manholes. M
- Cables in bundles along the walls under the vaults (C05). M
- OSM: the way is `layer=-1, tunnel=yes`, so make_spec does not vault it; the spec has OSM buildings w1393297094,
  w1393310567, w1393351628, w1393310566 and infill f141 over this stretch, which is consistent with "a passage under
  buildings" if it is vaulted.

### 1.3 J2: the roofed Byzantine Cardo (HaKardo, y ≈ -95..-150)
Photos: A01 (cam (329.4,-129.0)), A02 (cam (333.3,-116.7), the mural), A04 (cam (333.8,-94.6), looking S), C01 (cam
(338.2,-106.0)), C02 (cam (325.3,-103.6)).
- An excavated stretch of the Byzantine Cardo **~3 m below HaYehudim**: a single **row of 5-6 limestone columns
  (~5 m, Corinthian capitals)** with a reconstructed **timber beam pergola** on top, a massive ancient ashlar wall
  on one side, a pale slab floor with patches of the original worn paving, column stumps and a stone basin. H
- Roof: a **modern dark grey roof slab with a curved soffit on black square steel piers** (~0.4 m) at 6-7 m,
  spanning the excavation; along the east side a **street-level walkway with black railings** about 2.5-3 m above
  the floor, with bicycles and a mosaic-faced wall below it (A04, C01). H (A01, A04, C01, C02)
- At one end a large **painted mural of the Cardo** in a stone frame (A02). M
- Extent and exact plan are not measured: GPS positions lie at x 325-338, y -94..-129; the OSM `building=roof`
  w1393351627 (321,-139, 31 m²) and the Chabad / Tzemach Tzedek block (w290723473, w1393297090) sit at its south end.
  M for position, L for width (~10-12 m).
- Between the hall and the Open Cardo the Cardo continues as a **round-vaulted plastered tunnel** with a stone
  wainscot, lit by tube lights (D02, cam (320.6,-174.0), looking N). H

### 1.4 J3: the Open Cardo trench and square (x 311-338, y -163..-197)
Photos: D01 (cam (317.6,-179.2), N), D02, D03 (cam (322.6,-168.6), W), D04 (cam (322.2,-170.4), S), D05 (cam
(324.8,-186.7)), D06 (cam (306.4,-171.3), E), D07 (cam (306.4,-183.6), NE), D08, B02 (cam (326.1,-186.7)), B06 (cam
(324.8,-185.8)), G07, `landmarks_city/hurva_06_85613817.jpg`.
- **Trench**: open to the sky, floor **~4-5 m below the square** (the east wall is ~3.5-4 m with a person at the
  railing, D04; the north wall rises ~4.5 m to a viewing landing, D01). Floor of large pale slabs, bedrock
  outcrops, **6-8 standing columns ~5-6 m tall with Corinthian capitals** along the west side and stumps. H
- **Width ~8-10 m**: from the backs of the Habad St houses (x ≈ 311-312, which rise 4-5 storeys straight out of the
  trench, D03, D05) to the east retaining wall (x ≈ 320-322). OSM's archaeological-site polygon 1545911833 (x
  314-320) is narrower than the photos. M
- **North end**: a plain retaining wall with an **arched doorway with black iron gates** at trench level (into the
  tunnel, D02), a balcony landing with a black railing above it, and a **stair climbing along the west wall** to
  street level; the 3-storey Tzemach Tzedek building (w290723473, south face e4 (317.3,-163.4)) stands above it
  with "TZEMACH-TZEDEK / CHABAD LUBAVITCH SYNAGOGUE" lettering and a roof railing (D01, hurva_06). H
- **Parapets**: the trench is ringed by a stone parapet ~1 m with a **black steel railing**; stairs come down at the
  south end (OSM steps 508238575, D04) and a **bridge stair** crosses from Habad St (OSM steps 120425139, layer 1,
  incline down eastwards; D06, D07 foreground). H
- **Square** (OSM area 1545911834): pale slab paving; **tiered stone seating steps (~4 rows)** on its north edge by
  the Tzemach Tzedek building (D06, D07, hurva_06); **palms** (two tall Washingtonia, several date palms, a fan palm),
  a **jacaranda** (purple in May, G07) and bare deciduous trees; a green parasol café; **cars parked** (B06, D06,
  D07, G07). OSM trees (333.5,-159.5), (333.0,-164.6), (332.6,-173.3), (333.4,-189.0), (311.7,-181.2),
  (312.0,-175.6). H
- Surrounding fronts: 2-3 storey smooth ashlar, flat roofs with black railings, small round-arched windows, shops
  at street level on the Habad side (OSM Cofix (305.5,-173.9), Hummus Haviv (303.9,-172.3)). H

### 1.5 J4: HaYehudim (Jewish Quarter Rd) and the shopping streets
Photos: A03 (cam (347.0,-98.2)), A10 (cam (330.2,-141.7), 2013), B07 (cam (331.3,-171.9), 2010), B01, A12 (2018),
B03 (cam (326.2,-249.7)), B05, A06/A07 (north end, probably s05), G03 (Tiferet Israel, cam (416.3,-122.2)), H02.
- **Width** 3-4 m in the built stretches (A10 ~3 m at the Hurva, B07 ~4 m at the Ramban), opening into the Open
  Cardo square and a 10-15 m café widening at y ≈ -195..-215 (A12: café tables, a millstone, cars, palms; OSM
  "Cardo pizza" (328.8,-210.4)). H
- **Walls**: 3-4 storeys; at the Hurva **old rock-faced ashlar** in big courses (A10); at the Ramban tall smooth
  walls with **tall narrow round-arched windows with dark grey louvred shutters** and a stone flying arch across the
  street (B07). H
- **Shopfronts**: tall **round-arched openings with deep reveals**, glazed in **dark green / black steel frames**
  (A10), hanging boards on wrought-iron brackets ("HADAYA JEWELRY SHOW ROOM", A10), white **globe lamps on black
  curved brackets** (A10, B05), Israeli flags, **bougainvillea** (B07), a column drum used as a bench (B07). H
- **Arches**: a segmental arch spans HaYehudim north of the Hurva (A10) and a flying arch at the Ramban (B07). H
- **Tunnel portal** at the HaTuppim / Barkai junction (326.8,-243.6): a **pointed arch ~3 m wide, ~4 m high** in
  rough ashlar under a 3-storey building, faces S, shops inside (postcard racks, a white awning); ceramic signs
  "HA-TUPPIM RD." and "BARKAI RD", a blue pedestrian sign (B03). H
- **Tiferet Israel St at Hurva Plaza** (G03): ~4-5 m, 3-4 storeys of smooth ashlar with **box oriels on corbel
  courses**, black wall lanterns with white globes, green-and-white striped awnings over food shops ("Off the
  Wall" juice bar, "MONEY CHANGE"), a stone stair climbing on the south side. Further east (H02, cam
  (450.2,-122.8), night) one side is a **rough rubble / bedrock face** with arched shopfronts and blade signs. H/M
- Closed state: shops are glass behind dark frames; at night or on Shabbat the Cardo arcade has cream panel
  doors (C05); HaYehudim near the Hurva shows **dark green steel doors** (A10). M
- North end of HaYehudim (A06, A07, Fallaner 2022, no GPS, house number 33): a green-plastered pointed vault with
  a mosaic panel and the ceramic sign "רחוב היהודים / حارة اليهود / JEWISH QUARTER ST.", opening onto a market lane
  with Arab clothes stalls under steel canopies. This is probably at the s05 junction (y > -42). L

### 1.6 J5: vaulted passages
- **Habad north** (tunnel 44376194, (316.2,-44) → (312.8,-100.8)): a sequence of **pointed barrel vaults and
  cross-vaulted bays ~4-5 m high**, plastered, between old ashlar walls, with stone benches (mastabas) at the foot
  of the walls, arched iron-grille doors and a "WALKING TOURS" sign; paving of slabs with a slab gutter on the
  centre line; through the arches a crenellated parapet (E01, E02, E03; cams (315,-53.2), (314.7,-61.7)). H
- **HaYehudim tunnel** 290722441 (y -219..-243): see 1.5 (B03). H for the south portal, L for the inside.
- **Misgav Ladach**: a **barrel-vaulted stepped passage** (~15 steps, wall handrails, a globe lamp, a pointed arch
  beyond) (I02, cam (497.7,-19.2), just north of the sector at the Misgav Ladach north end); the OSM tunnel 290730039
  (y -149..-168) looks open to the sky in I01 / I07 (narrow lane between 12-15 m walls), so its `tunnel=yes` is
  doubtful. M
- **Gal'ed**: a whitewashed pointed vault ~2 m wide over a rubble-walled lane (L02). M
- **Building passages** with round arches through houses, e.g. by Lohamei HaRova BeTashah (G09, cam (380,-128.9)). M

### 1.7 J6: residential lanes
Photos: E04 (cam (309.9,-264.9)), E05 (cam (303.9,-200.2)), E06 (cam (303.8,-237.6)), E08 (Habad/Or HaHayim corner),
L01 (cam (418.1,-273.2)), L03 (cam (398.5,-192.1)), L04 (cam (373.6,-187.1)), K07, I01, I03, I07, J02, M01, M02,
M04, M05, `landmarks_city/hurva_06`.
- **Habad St south** (y -195..-320): 2.5-3 m wide, 3-4 storeys of rock-faced or smooth ashlar, tall rectangular
  windows with **white louvred timber shutters** (E04) or plain grilles, **dark brown panelled timber doors** and
  **grey/blue-grey steel doors** on raised stone thresholds, ornate black iron door grilles (E06), cables slung
  across,
  a pointed sabat across the street with a room above (E04 at Tiferet Yerushalayim), globe lamps on brackets, a slab
  gutter on the centre line. Ceramic signs "HABAD ST." and "TIF'ERET YERUSHALAYIM ST." H
- **HaChatzotzrot / Gal'ed / Beit El** (south-centre): the narrowest lanes (1.8-2.5 m), rough rock-faced old
  ashlar, **a series of flying arches** (L01), vaults (L02), small courtyards with an **orange tree** (L03), a
  **round oculus window with a wrought-iron rosette grille** and twin arched windows with amber glazing bars over a
  segmental flying arch on Beit El (L04), dark brown timber doors, **green-painted steel window frames and doors**
  (L03). H
- **Misgav Ladach / HaTamid** (east): smooth sawn ashlar, tall dark doors, louvred vent grilles, slit windows on
  the yeshiva walls (I01, I07); an old building with a deep **pointed-arched portico** over 5 broad steps with black
  handrails (I03, cam (500.5,-118.6)); shoring beams in an alley, a white spiral stair on a roof, timber pergolas
  (J02). H
- **Plugat HaKotel / HaOmer / HaSho'arim** (north-east): **pitched rock-faced ashlar with drafted margins** (M01,
  M04), **rust-brown steel louvred shutters** (M01), **white steel doors with louvres and an arched fanlight** (M04),
  **dark green steel doors** (M05), white ceramic house-number plates with black numerals, a small blue round plate,
  courtyards paved in **diagonal / herringbone slabs** (M04, M05), terraces with bougainvillea, pergolas with flags
  and **white tube railings** on the roofs (M02). H
- Common: steel handrails fixed to the walls on slopes (E08, F01, F02, I02, J01), plant pots, AC units low on the
  walls, electrical boxes. H

### 1.8 J7: stepped lanes
- **Or HaHayim** (west; F01 cam (250.6,-164.2), F02 cam (250.3,-144.8), F03 cam (267.9,-154.7)): 2.5-4 m, steps at
  intervals and a long slope down eastwards (street_z +2.9 → -8.9 over 67 m), old rubble and big ashlar walls with
  a stone plinth, **black classic lanterns** and globe lamps, wall handrails, bougainvillea, banners of the **Old
  Yishuv Court Museum** (OSM museum (268.6,-156.9), house no. 6). H
- **HaMalakh**: a round flying arch over a lane that turns into a **steep flight of ~12-15 steps** going up west,
  **amber/orange louvred timber shutters** (F05). M
- **HaTamid** (J01, cam (513.2,-84.4)): broad stone steps (risers ~0.15 m, treads ~0.4 m) with a **galvanised
  central handrail**, smooth pale ashlar, an **orange-brown timber door**, green steel window grilles and railings,
  a raised terrace with a black railing. H
- **The escarpment stairs** (29388393, 29388395, HaKotel HaMaaravi 722734611): wide stone stairs with landings and
  steel railings down to the Western Wall plaza, lookouts over the Temple Mount (J03, J05, J06; s07 notes P2). M

### 1.9 J8: plazas
**Hurva Plaza** (way 290730185; G01 cam (393.7,-141.3), G02 cam (396.1,-146.3), G03, G06 cam (381.6,-175.9), G08 cam
(393.0,-131.2), G09; `landmarks_city/hurva_03_10591123.jpg`, `hurva_08_75802671.jpg`, `hurva_01_163083960.jpg`):
- Paving: **large pale limestone slabs**; low stone benches; tall black lamp/camera poles. H
- West side: the **Hurva podium** (~3 m ashlar wall with white tube railings and a stair/ramp, G06, hurva_03) and
  the old 2-storey **"MORIAH" building** (rough ashlar, arched windows, lettering, G01, hurva_01). H
- East side: **3-4 storey ashlar houses** (w290730728, e7/e9 (415,-139..-148) face 275°) with **brown louvred
  timber shutters**, round-arched and rectangular windows, a round corner block, flat roofs with railings and
  timber pergolas; ground-floor cafés and food shops with **red umbrellas**, "BBQ" sign, a green wheelie bin (G02). H
- Trees: a big dark conifer by the Hurva's north-east corner (G01), a broad **ficus / chinaberry** on the east side
  (G02), an **old olive** south of the Hurva and cypresses (G06). OSM: trees (413.5,-164.2), (413.4,-157.8),
  (413.3,-161.0), (407.8,-153.3), (405.5,-134.3), (371.2,-161.8), (357.5,-168.2), (375.6,-173.7); benches
  (412.8,-162.7), (411.1,-160.1); waste basket (410.6,-163.9); bicycle parking (415.9,-164.3); drinking water
  (360.1,-156.9). H
- Objects: the **golden Menorah replica in a glass cylinder** with a low railing, on the plaza east of the Hurva
  (hurva_08, 2018); a **red cylindrical Mandate-era pillar box** at a café (G08, (393.0,-131.2)); a giant metal
  Hanukkah menorah on a lamp post in December (G01, seasonal); crowd barriers (G01). H
- North edge: Lohamei HaRova BeTashah (44376196); NE corner opens into Tiferet Israel St (G03). South tongue: cars
  parked by the Hurva's south face (G06, hurva_01). H

**Batei Mahase Square** (way 44376187; K01-K05, K07; geotags are the square's geocode except K02 cam
(459.3,-254.3) and K03 cam (453.4,-251.3)):
- **Rothschild House** (w290722438, e2 (436.3,-248.5), 28.4 m, faces E): two storeys, ~10-11 m; ground floor an
  **arcade of 7 round/segmental arches on square piers** in front of a recessed wall with pointed-arched grilled
  windows, round oculi and doors; upper floor an **open round-arched loggia** of the same rhythm; flat roof with a
  parapet; **3 broad steps** along the whole base; weathered grey-honey ashlar (K01, K02, K05). The Commons file of
  K05 carries the category "Wilhelm Carl von Rothschild". H for form, M for the edge.
- Its south side (e1 (430.1,-262.8), faces S): two storeys with segmental-arched windows with amber glazing, a
  basement stair, a cypress (K04). M
- Square: large pale slabs sloping gently east, **tall cypresses** and **olives**, stone blocks as benches and a
  stone table, tall lamp poles with lantern heads, a black railing along the raised south-east edge (K03), a
  **re-erected Roman column on a plinth with a railing** near the arcade (K02, K05). OSM trees (463.0,-236.1),
  (443.2,-237.7), (473.0,-232.2), (475.6,-236.0), (469.7,-246.2), (462.0,-250.3), (442.1,-261.9), (431.3,-266.6);
  monument n7605347985 (427.0,-229.5) (the War Memorial); school n563992104 (437.7,-244.9). H
- North side: Aish HaTorah yeshiva (w290725352, 12 m, modern ashlar). The long two-storey almshouse range of Batei
  Mahase on the south side (w290725362 e3 and infill f363) has no clear photo in this set. L
- At the corner of Ma'amadot Israel and Gal'ed: a ~2.5 m stone garden wall with trees spilling over and a short
  stair (K07). M

### 1.10 J9: the southern service road
- Batei Mahase road (496167693) and the Zion Gate parking (290701320) are asphalt with kerbs and parked cars along
  the inside of the south wall; Gan HaTkuma (north edge of 290701310) is a fenced ruin garden of low rubble walls in
  grass (N01, cam (378.2,-332.6)). OSM: a row of broadleaf trees along footway 1544667236 (x 385-388, y -283..-303)
  and in the parking (x 302-340, y -278..-299). M (OSM + N01)

---------------------------------------------------------------------------------------------------------------

## 2. LANDMARKS (described only; built by blender/landmarks_city.py and the spec rules)

### 2.1 Hurva Synagogue (w45081545, landmark) and the Sidna Omar minaret
- Rebuilt 2010: a pale, almost white smooth-ashlar cube on a **3 m rubble-faced podium** (OSM ring height 3) with
  a railed terrace, a great round blind arch on each face (two rows of round-arched windows, trefoil of oculi), four
  corner turrets, a drum with a **black wrought-iron balcony** and a **white dome** (~26 m above the plaza). The
  dome is the quarter's beacon: it shows over the rooflines in D07, G06, G07, hurva_02, sidna_03. Already modelled
  (landmarks_city.md §3). H
- **Sidna Omar minaret** (built by the Hurva builder at (354.6,-157.3)): square lower shaft of darker, rougher
  stone, then a round upper stage with a corbelled balcony (arcaded parapet), a small lead dome and a crescent.
  It is seen from the Open Cardo square and HaYehudim directly above the trees (B01 from (326.9,-204.9), D06, D07,
  hurva_01). H for the look; position: B01's bearing (~30° from (326.9,-204.9)) and D06/D07 agree with the
  landmark position within the photo accuracy. M
- Plaza side: the podium wall carries a long black steel railing, a broad stair rises to the terrace; the **golden
  Menorah replica in a glass cylinder** stands on the plaza east of the synagogue since 2018 (hurva_08; Commons
  category "Golden Menorah on Kikkar haHurvah"). OSM still has the menorah at its old place on the Western Wall steps
  (n9351190456 (550.6,-127.9)): a prop request, not a landmark change. M

### 2.2 Ramban Synagogue (w290730186) and the Sidna Omar mosque body (w1394070804)
- A low, partly sunken medieval hall entered down steps from HaYehudim, with the mosque and minaret on its
  north side. In the spec it is an ordinary 13.7 m block, which is too tall: from the street the Ramban reads as a
  1-2 storey rubble wall with a few small windows (hurva_01: the low rubble-walled block at the foot of the minaret,
  probably the Ramban). L (no direct photo of e0 in this set)

### 2.3 Four Sephardic Synagogues (w29265134, landmark)
- Four connected synagogues sunk ~3-4 m below the street round a **sunken courtyard** with arched windows, seen
  over a parapet and railing from Mishmerot HaKehuna / the HaTuppim corner; plain rubble-ashlar walls with a
  stepped parapet, a round stair turret, a lattice (mashrabiya-like) window, black floodlights and the metal letters
  "ארבעת בתי הכנסת הספרדיים / Four Sephardi Synagogues" (seph_01). Interiors whitewashed with low domes (seph_02-04).
  Built by the landmark module; note for it: the street level is the **roof/terrace level**, not the floor. H

### 2.4 Tiferet Yisrael Synagogue (w195100862, landmark, historic=ruins)
- On Tiferet Israel St (north face e2 (451.5,-128.2)). Ruined in 1948; a reconstruction with a dome has been under way
  since the 2010s (general knowledge, not from this photo set; the one 2011 night photo of the ruin was discarded).
  The street in front: H02 (2012, night). L

### 2.5 Yeshivat HaKotel (r3863218) and Porat Yosef (w290726629)
- The two biggest buildings of the sector, both modern (1970s-80s) neo-vernacular ashlar blocks on the eastern
  scarp: Yeshivat HaKotel stretches 88 m along Hayei Olam; Porat Yosef (Moshe Safdie, 1970s) steps down the scarp
  above
  the Western Wall plaza with **rows of large round-arched openings and a field of white domes** on its roofs
  (Western Wall photos from the plaza; s07 notes L7). Not landmarks; they need overrides (heights 15-20 m, arched
  bays). M

### 2.6 Church of St Mary of the Germans (w290733222, ruins=yes)
- A **roofless Crusader church ruin** in a sunken garden on Misgav Ladach: three apses, rubble walls 2-6 m high,
  arches standing free; lawn and trees around. The spec builds it as a 19.2 m solid block (OSM building:levels=5),
  which is wrong. H (category "Saint Mary of the Germans church"; OSM ruins=yes). Request: treat as ruin / open
  area.

### 2.7 Batei Mahase (almshouses, 1860s) and Rothschild House
- See 1.9: Rothschild House on the west side of Batei Mahase Square (w290722438 e2) is a two-storey double arcade
  (K01, K02, K05; H for the form). The long two-storey almshouse range on the south side (w290725362 e3, infill f363)
  has no clear photo in this set. L

### 2.8 How landmark positions were checked

| landmark | position | evidence |
|---|---|---|
| Hurva dome over the Open Cardo | (360,-144) | D07 (GPS (306.4,-183.6)) shows the minaret just right of the dome, as the positions predict (bearings 61° and 54°); in D06 (GPS (306.4,-171.3), looking E) the minaret (74°) is at the left edge and the dome (63°) is out of frame, as predicted |
| Sidna Omar minaret | (354.6,-157.3) | B01 (GPS (326.9,-204.9), the minaret NNE over the trees), D06, D07, hurva_01 |
| Four Sephardic Synagogues sunken court | w29265134 | seph_01 (2024, geotag (364.3,-237.5), looking E into the court) |
| Golden Menorah | Hurva Plaza (since 2018), not OSM n9351190456 | hurva_08 (2018) |

---------------------------------------------------------------------------------------------------------------

## 3. GATES of the sector

The sector has **no city gate of its own**. It is entered:
1. from **Zion Gate** (s02) along the Batei Mahase road / the parking (Habad St south end, HaYehudim south end);
2. from **Jaffa Gate** through the Armenian Quarter lanes (St James St → Or HaHayim, HaShofar, HaMalakh: all
   stepped down eastwards) or from David St into Habad St (tunnel 44376194), the Cardo arcade (HaKardo) and
   HaYehudim;
3. from the **Western Wall plaza** up the escarpment stairs (29388393, HaTamid, HaKotel HaMaaravi) and from the
   **Dung Gate** along the Batei Mahase road;
4. the **Tanners' Gate** (n5003920349 at (597,-205), a modern opening in the south wall beside the Dung Gate) lies
   on the s06/s07 boundary; the Cardo Minimus excavation (way 288016648, (596.6,-200.7) → (590.5,-156.3)) runs
   north from it inside s06 (see s07 notes K:039). M

Gate-like features inside the quarter:
- **Iron grille gates** of the Cardo arcade: pairs of black iron leaves with arched tops in pointed stone arches at
  both ends of the vaulted market (A05). H
- **Arched tunnel portal** of HaYehudim at (326.8,-243.6), facing south onto the HaTuppim / Barkai junction:
  a pointed arch ~3 m wide in rough ashlar under a 3-storey building (B03). H
- **Batei Mahase gate**: an arched gateway into the Batei Mahase compound from Gal'ed St (Commons file "BATEI MAHSE
  GATE JERUSALEM.JPG", category Gal'ed Street; not downloaded). L

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Lighting
- **White opal globe lamps (~0.35 m) on black curved wall brackets** at ~3-3.5 m: the standard street light of the
  quarter's lanes (A10, B05, E04, E05, E08, I01, I02, M05). H
- **Black classic lanterns** (square, tapering, on scroll brackets) on Or HaHayim, Tiferet Israel and HaYehudim (F01,
  F02, F03, G03). H
- Plazas: tall black poles with lantern heads (K03, K05) and modern lamp/camera masts (Hurva Plaza, hurva_08). H
- Cardo arcade: hanging lanterns down the axis, floodlights on the piers (C03, C05, A05). H
Signs and plaques
- **Ceramic street signs**: white glazed tiles with a thin olive-green patterned border, three lines (Hebrew, Arabic,
  English, black letters), ~0.5 x 0.35 m at ~2.5-3 m: "JEWISH QUARTER ST." (A07), "HA-TUPPIM RD.", "BARKAI RD" (B03),
  "HABAD ST." (E08), "TIF'ERET YERUSHALAYIM ST." (E04), HaChatzotzrot (L01). H
- House numbers: **white ceramic squares with black numerals** ("33" A07, "3" M04, "12" M05, "6" F03) or numbers
  painted on the stone ("62", E08). H
- **Blue municipal map boards** "Jewish Quarter Map / מפת הרובע היהודי" in a blue steel frame with an arched top,
  on a tube railing (J04); brown/white museum and synagogue signs (F01, I03); a black-on-white "WALKING TOURS" sign
  (E02). H
- Shop signs: hanging boards on wrought brackets ("HADAYA JEWELRY", A10), fascia letters ("Off the Wall", G03),
  "MONEY CHANGE" blades (G03, H02), "BBQ" (G02). Metal letters on the synagogues ("TZEMACH-TZEDEK", D01; "Four
  Sephardi Synagogues", seph_01). H
Railings, handrails, barriers
- **Black steel railings** on every excavation parapet (Open Cardo, D04-D07; Broad Wall, M03; Hurva terrace, G06),
  white tube railings on the Hurva podium (G06) and on roof terraces (M02). H
- **Galvanised or grey steel handrails** fixed to the walls on every sloping lane and stair (E08, F01, F02, I02,
  J01). H
- Galvanised crowd barriers (G01, seasonal), security booths and railings at the bottom of the escarpment (J05). M
Benches, bins, other
- Stone benches and stone blocks (Hurva Plaza, Batei Mahase K03), tiered stone seating at the Open Cardo (D06, D07),
  column drums used as seats (B07, A04). H
- Green municipal wheelie bins (G02). The **red Mandate pillar box** on Hurva Plaza (G08). The **golden Menorah**
  (hurva_08). Two yellow painted **fibreglass lions** at the Misgav Ladach / Tiferet Israel lookout in 2014 (I04, an
  art installation, probably gone). Utility golf carts and scooters (I01, A06). Parked cars (B06, A12, G06). H/M
Flags
- Israeli flags on poles and balconies everywhere (A10, D04, G02, M02); flags at the Hurva (hurva_03). H
Vegetation
- **Palms**: Washingtonia and date palms at the Open Cardo square (B06, D06, D07, G07; OSM trees there), date palms
  by HaYehudim (A10, A12, B01). H
- **Jacaranda** (purple, May) at the Open Cardo square (G07). M
- **Cypresses** (Batei Mahase Square K02-K05, south of the Hurva G06), **olives** (Hurva G06, Batei Mahase K03),
  **ficus / chinaberry** (Hurva Plaza G02, K07), a big conifer at the Hurva (G01), an **orange tree** in a Beit El
  courtyard (L03). H
- **Bougainvillea** (magenta) on walls and pergolas (B07, F03, M02), climbing jasmine/ivy, geraniums and potted
  plants at doors and on terraces (J01, F01). H
- Weeds and capers only on the old rubble and excavation walls (D01 bedrock, H02, N01). M

---------------------------------------------------------------------------------------------------------------

## 5. TERRAIN

The quarter is a plateau at ~757-763 m asl (street_z -13 .. -7) that falls away on three sides: west up into the
Armenian Quarter (+3 at Or HaHayim's west end), and east and south-east steeply down to the Western Wall plaza
(-41.6) and the Dung Gate road. 52 OS 1865 spot heights fall inside the sector, so the street field is well
anchored in the core: `street_z` reproduces them with a median residual of 0.13 m. The only misfits are under the
Western Wall plaza flat ((590.6,-58.7), 3.1 m) and in the Mughrabi garden ((595.9,-112.4), 1.3 m). Absolute levels
below are street_z (m relative to the
Jaffa Gate street, datum 770.58 m asl).

| place | street_z (m) | basis | confidence |
|---|---|---|---|
| Hurva Plaza, north / centre / south (390,-125) / (395,-150) / (385,-172) | -7.6 / -8.1 / -9.5 | OS 1865 2503 ft (389.9,-119.5) = -7.67, 2502 ft (406.1,-151.3) = -7.97 | H |
| HaYehudim beside the Hurva (333,-136) | -9.0 | interpolated; OS 2508 ft (313.3,-130.7) = -6.14 on Habad | M |
| Open Cardo square (325,-178) | -10.1 | OS 2492 ft (338.1,-168.7) = -11.02 | H |
| Habad St at Or HaHayim (309,-166) | -9.0 | OS bench mark 2504 ft (301.5,-159.4) = -7.36 is 8 m west | M |
| Habad St, y -120 / -200 / -260 | -6.2 / -6.2 / -8.9 | OS 2508 ft (313.3,-130.7), 2505 ft (311.4,-192.8), 2504 ft (292.9,-249.2) | M (wavy, ±1.5 m) |
| Or HaHayim west end (250,-151) → Habad (309,-168) | +2.9 → -8.9 | OS 2531 ft (280.8,-151.1) = +0.87, 2527 ft (277.9,-174.5) = -0.35; 11.8 m in 67 m, max 31 % | H for the drop |
| HaShofar (219,-189) → Habad (307,-181) | +2.6 → -7.8 | same anchors, 10.4 m in 99 m, max 27 % | H |
| HaMalakh (247,-204) → Habad (306,-195) | -0.1 → -6.5 | 6.4 m in 61 m | M |
| Four Sephardic Synagogues entrance (370,-243) | -8.9 | OS 2501 ft (375.4,-258.4) = -8.28 | H |
| Batei Mahase Square centre / south (455,-245) / (460,-260) | -11.5 / -12.3 | OS 2496 ft (429.2,-246.3) = -9.80 | M (1-3 m slope down to the east) |
| Tiferet Israel St, Hurva end (414,-125) → Misgav Ladach (503,-135) | -7.5 → -15.3 | OS 2501.6 ft BM (442.3,-124.5) = -8.09, 2476 ft (506.4,-132.1) = -15.90; 7.8 m in 96 m, max 14 % | H |
| Misgav Ladach N (498,-60) / at HaTamid (498,-85) / at Tiferet Israel (503,-135) | -12.4 / -16.7 / -15.2 | OS 2489 ft (481.4,-74.2), 2474.4 ft BM (483.1,-85.4) = -16.38, 2476 ft (506.4,-132.1) | H |
| HaTamid bottom (537,-87) | -25.1 | OS 2462 ft (518.0,-91.9) = -20.16, 2459 ft (533.6,-62.2) = -21.08 | M |
| Porat Yosef top of the escarpment (540,-140) | -21.9 | OS 2447 ft (534.2,-119.8) = -24.73 | M |
| Bottom of the SW descent (557,-106) | -31.6 | steps 29388393 | M |
| Western Wall plaza (flat) | -41.58 | terrain_street flat `western_wall_plaza` | H |
| Zion Gate parking (345,-290) | -11.0 | OS 2491 ft (347.1,-284.5) = -11.32 | H |
| Batei Mahase road at the Dung Gate bend (575,-191) | ~-31 | street_z along 496167693 (-9.3 at x 356 → -34.3 at the bus loop) | M |

Notes
- **HaYehudim profile** (way 4710079, street_z every ~20 m from y -44): -10.4, -10.9, **-13.2** (y -84), -11.3, -9.3,
  -9.3, -10.7, -9.9, -8.4, -8.8 (y -219). The 2.8 m dip at y ≈ -75..-90 rests on a single 1865 spot (331.8,-78.9)
  2484 ft = -13.46, 17 m from another of 2499 ft (325.9,-62.3) = -8.88. Today the street is continuous here and the
  sunken Cardo lies beside it; the dip is probably the 1865 level of a courtyard or lane, not of the modern street
  (**unverified**: no photo of y -60..-90 in this set). Check before building steps there.
- **The Cardo is sunken** below HaYehudim: ~3 m at the roofed excavation (A04, C01: the street-level walkway with
  railings stands ~2.5-3 m above the Cardo floor) and ~4-5 m at the Open Cardo trench (D01, D04, D06, D07: the trench
  floor with the column bases lies more than a storey below the railed parapet). street_z knows nothing of this; it
  needs a
  sunken court / ground hole (see requests).
- **The quarter edge is a scarp**: from Misgav Ladach (-15) to the plaza (-41.6) the ground falls 26 m in ~70 m
  (Misgav Ladach / Tiferet Israel junction (503,-135) to the plaza edge at x ≈ 570).
  OSM carries it on HaTamid (+steps 29388395), the long stepped descent 29388393 (16.4 m in 94 m, median 17 %, max
  34 %) and HaKotel HaMaaravi 722734611 (escarpment steps 722871632: 6 m in 10.7 m).
- **Steps directions** (OSM incline vs street_z): all consistent except **26492742 Misgav Ladach** (tunnel steps,
  incline=down drawn (505,-255) → (501,-243), i.e. down northwards, while street_z rises +1.9 m northwards). One of
  them is wrong; the road to the south-east is lower (-20 at (518,-265)), so the OSM tag is the likely error. L
- **Flat-ish plazas**: Hurva Plaza falls ~2 m from NE to SW over 60 m (3 %); Batei Mahase Square ~2.5 m W → E over
  50 m. Neither needs a flat, but both read level in photos (G02, K03): a local flat or soft grading would help.
- **Raised and sunken features** (photos): the Hurva podium (OSM height 3 m; terrace with railings, stair on the
  plaza side, hurva_03), the Four Sephardic Synagogues' sunken court (~3-4 m below the street, seph_01), the Broad
  Wall
  excavation (~4 m below Plugat HaKotel, M03), St Mary of the Germans in a sunken garden below Misgav Ladach
  (the spec puts its ground at -16.6 against -15 on the street), the Burnt House basement.

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **Clean dressed ashlar, not rubble**: smooth-sawn or pitched (rock-faced, drafted-margin) cream-to-pinkish
   limestone in regular courses on the rebuilt fabric (most buildings); rubble / old weathered ashlar only for the
   old pieces (Habad north, Or HaHayim, HaChatzotzrot, Rothschild House, St Mark's, excavations). (0.1, 1.7)
2. **HaYehudim open as a street** from y -42 to -270, with its café widening at y -195..-215 and the pointed tunnel
   portal at (326.8,-243.6); the infill on it removed (f157, f154, f151, f155, f329, f331). (0.2, 1.5)
3. **The Open Cardo**: a trench ~4-5 m deep and ~8-10 m wide at x 311-322, y -170..-196, with 6-8 columns,
   parapets with black railings, the bridge stair from Habad St, the north wall with gate and landing under the
   Tzemach Tzedek building, and the square above with palms, a jacaranda, tiered seating and cars. (1.4)
4. **The vaulted Cardo arcade** (y -48..-95): pointed transverse arches and cross vaults, arched shop bays on raised
   sills with cream panelled doors, lanterns, iron gates at both ends. (1.2)
5. **The roofed Byzantine Cardo** (y -95..-150): sunken ~3 m, one colonnade with a timber-beam top, the ancient
   wall, a dark roof slab on black square piers, a railed walkway at street level. (1.3)
6. **Heights and roofscape**: continuous 3-4 storey street walls (10-14 m), 4-5 storeys above the Cardo trench;
   flat roof terraces with black/white railings, pergolas, water heaters and small white domes; the Hurva dome and
   the Sidna Omar minaret above everything. (0.4, 2.1)
7. **Hurva Plaza**: pale slabs, trees (OSM nodes), benches, cafés with red umbrellas, east fronts with brown louvred
   shutters, the Hurva podium with railings, the golden Menorah in its glass cylinder, the red pillar box. (1.9)
8. **Globe lamps on curved black brackets** in every lane, black lanterns on the shopping streets, steel handrails
   on every slope. (4)
9. **Flying arches and vaulted passages**: Habad north (pointed vaults), the HaYehudim tunnel, sabats on Habad south,
   Beit El, HaChatzotzrot, HaMalakh, the Gal'ed vault. (1.6, 1.7)
10. **Stepped lanes** climbing west into the Armenian Quarter (Or HaHayim, HaShofar, HaMalakh: 6-12 m) and the stairs
    down the eastern scarp (HaTamid, 29388393, HaKotel HaMaaravi). (1.8, 5)
11. **Batei Mahase Square**: Rothschild House's two-storey arcade with 3 steps, cypresses, olives, the re-erected
    Roman column, stone benches. (1.9)
12. **Doors, shutters and signs**: dark brown timber doors, dark green / grey / white steel doors with fanlights;
    white, brown, rust or amber louvred shutters; glazed arched shopfronts with dark frames and hanging boards;
    ceramic three-script street signs and white number plates. No teal souq doors. (0.8, 4)
13. **Lane paving**: pale rectangular slabs in courses with a slab gutter on the centre line and round manholes;
    herringbone / diagonal slabs in courtyards; large slabs on the plazas. (1.7)
14. **The eastern edge**: the long Yeshivat HaKotel and Porat Yosef blocks (15-20 m, rows of arched openings, domes),
    the lookout at the Misgav Ladach / Tiferet Israel junction over the Temple Mount. (2.5, 1.8)
15. **Ruins and pits set into the street level**: St Mary of the Germans as a roofless ruin, the Broad Wall pit, the
    Four Sephardic Synagogues' sunken court (landmark), Gan HaTkuma's ruin garden and the parking on the south.
    (2.3, 2.6, 1.10)

---------------------------------------------------------------------------------------------------------------

## 7. Hand-off: suggested profile entries and requests (not written in this pass)

Profile (data/reference/profiles/s06_jewish.json) candidates for the next worker:
- `souq_streets`: `"44376195"` (Habad St) **[0.25, 0.05]**, overriding the global "Habad Street" (0.6, 0.2): only the
  stretch at the Open Cardo (y -160..-185) has shops; the south half is residential (E04, E05, E06, E08).
  `"44376194"` (Habad tunnel) [0.4, 0.0] (E01-E03: arched iron-grille shop doors and house doors under the vaults).
  `"26612859"` + `"254576587"` (Tiferet Israel St) [0.5, 0.25] (G03, H02; OSM fast food / café / gift nodes at
  (422.8,-134.7), (431.8,-122.2), (435.4,-122.6), (459.9,-118.2), (465.2,-136.6), (470.5,-136.7), (471.2,-122.9)).
  HaYehudim `"4710079"` [0.6, 0.1] only works after request R1.
- `covered_streets`: `"290722441"` (HaYehudim tunnel, B03): it becomes street level and vaulted.
- `open_areas` (to keep infill off until R1 lands; polygons from OSM, ±1 m):
  - HaYehudim corridor: the centreline 4710079 from (342.4,-45.9) to (328.5,-219.0) buffered by 1.6 m (3.2 m lane,
    A10, B07), and the café widening ≈ [(320,-192),(334,-192),(333,-216),(321,-216)] (A12, B01).
  - Open Cardo trench ≈ [(311.5,-170.0),(321.5,-170.5),(320.5,-196.0),(311.5,-195.5)] (D01-D08), which also removes
    infill f328.
  - St Mary of the Germans garden ≈ [(499,-125),(525,-125),(525,-109),(499,-109)] (with remove_buildings w290733222
    only once a ruin builder exists; otherwise leave the block and file R4).
  - Misgav Ladach south lane: 290730039 buffered by 1.4 m (I01, I07), which removes infill f71's hold on it.
- `props`: `bench_stone` at the OSM bench nodes are already real furniture; add `palm` at the OSM tree nodes of the
  Open Cardo square if the dressing does not already use them, a `bench_stone` row for the tiered seating, and the
  menorah / pillar box / column below (R7).

Requests (code, spec owner, landmark modules), with evidence:
- **R1 HaYehudim is `layer=-1` in OSM** (4710079; also 290722441 tunnel). infill.py, stairs.py and the souq lines skip
  it, so infill f157, f154, f151, f155, f329, f331 stand on the street. Treat 4710079 south of y -42 and 290722436 as
  layer 0 (a per-way layer override). Evidence: A10, B07, B06, D06, D07, A12, B01, B03; OSM retail landuse 1544671583.
- **R2 Cardo arcade vault**: HaKardo 123231486 is `layer=-1, tunnel=yes` for 345 m, from s04 (y 171) to y -172.
  covered_streets would vault the whole line, including the part under the triple souq in s05/s04. Needed: a vaulted
  souq only for y ≈ -48..-95 (pointed transverse arches, crown ~6 m, ~5.5 m wide, arched shop bays; C03, C05, A05),
  and the round-vaulted tunnel y ≈ -150..-172 (D02).
- **R3 Sunken courts** (`SUNKEN`, paving at street level + dz):
  - Open Cardo trench, ring as in open_areas, floor ≈ street_z **-14.5** (4.5 m below the square at -10.1; street_z
    at the trench centre (317,-178) is -9.4, so **dz ≈ -5** there), with
    retaining walls, a ~1 m parapet with a black railing, the stair 508238575 at the south end, the bridge stair
    120425139 (layer 1) and 6-8 columns ~5.5 m with capitals (D01, D04, D05, D06, D07, D08). H for the form, M for dz.
  - Roofed Cardo hall: along HaKardo x ≈ 318-332, y ≈ -95..-150, **dz ≈ -3**, a colonnade, a roof slab at ~+6.5 m on
    black square piers, a railed walkway on the east (A01, A02, A04, C01, C02). L for the extents.
  - Broad Wall pit: park 1545547646 (x 372-389, y -91..-75), **dz ≈ -4**, railings (M03; OSM n4542880989). M
- **R4 St Mary of the Germans** w290733222: build as a roofless ruin (rubble walls 2-6 m, three apses, free-standing
  arches) in a garden ~1-2 m below Misgav Ladach, not a 19.2 m solid (OSM ruins=yes; Commons category "Saint Mary of
  the Germans church"). H for the type, no close photo in this set.
- **R5 `building=roof`** parts are built as solid blocks: w1393297095 (339.6,-70.3, 53 m², 11.6 m) lies across
  HaYehudim; w1393351627 (321.2,-139.1, 31 m²) is part of the Cardo hall roof. Build them as roofs over a passage. M
- **R6 Door/shutter atlas**: missing cells for cream/white panelled shop doors (C05), white louvred timber shutters
  (E04), white steel door with an arched fanlight (M04), grey steel door (E05) and amber timber shutters (F05).
  Existing cells that fit: `door_wood` (dark brown), `door_green` (dark green), `shutter_brown` (G02, M01),
  `rolldown_grey`, `glass` (shopfronts).
- **R7 Props** (positions ±5 m unless stated): the **golden Menorah** in a glass cylinder (~2 m diameter, ~2.5 m
  high with base, low railing) on Hurva Plaza in front of the Hurva's east face, ≈ (385,-146) (hurva_08; OSM still
  has it at n9351190456 (550.6,-127.9)). L for the position. The **red pillar box** at (393.0,-131.2) (G08 geotag,
  M). The **Roman column on a plinth with a railing** at the north end of Rothschild House's arcade, ≈ (441,-236)
  (K02, K05, L). Globe wall lamps (`wall_lantern`) on narrow lanes.
- **R8 Heights**: in s06 the infill pieces are 6-9 m (`roofscape.height_for` gives infill only half the quarter
  offset) and many OSM blocks are 7-10 m; photos show 10-14 m nearly everywhere (B07, E04, G02, G03, F03, I01, I07)
  and 4-5 storeys above the Cardo trench (D03, D05). Suggest infill 9.5-12 m in s06 and a 10 m floor for OSM blocks
  in the core (x 300-500, y -60..-280), storey ~3.3 m.
- **R9 Terrain checks**: the 2.8 m dip in street_z on HaYehudim at y ≈ -75..-90 rests on one 1865 spot (331.8,-78.9)
  2484 ft; no photo shows a descent there. Misgav Ladach steps 26492742 are tagged incline=down northwards while
  street_z rises northwards. L
- **R10 Landmark notes** (for landmarks_city.py): the Four Sephardic Synagogues are entered from a **sunken court
  ~3-4 m below the street** (seph_01); the Ramban synagogue (w290730186, not a landmark) is a low, partly sunken hall
  and its 13.7 m spec height looks too tall (hurva_01; L).
- Info: OSM `name:en` of w290726629 is "Yeshivat HaKotel", but its Hebrew name and the amenity area 1545234304 say
  **Porat Yosef**; r3863218 is the real Yeshivat HaKotel.

---------------------------------------------------------------------------------------------------------------

## Provenance

77 Commons photos in `data/photos_ref/s06_jewish/` (1280 px thumbnails; `index.json` has key, title, page, author,
licence, date, lat/lon and local x/y where geotagged). Licences: CC BY-SA 4.0 (53), CC BY-SA 3.0 (10), CC BY-SA 2.0
(3), CC BY 2.5 (3), CC BY 2.0 (3), CC BY 3.0 pl (2), CC0 (1), public domain (1), CC BY 4.0 (1).
- Found by a Commons geosearch over the sector (959 geotagged files) and the street / square categories ("Jewish
  Quarter Road", "Ha-Kardo Street", "Open Cardo, Jerusalem", "Cardo west of Lohame ha-Rova be-Tashah Street",
  "Habad Street", "Hurva Square", "Batei Mahase Square", "Tiferet Israel Street", "Misgav Ladakh Street",
  "Beit-El Road", "Or ha-Hayim Street", "Ha-Tamid Street", "Gal'ed Street", "Ha-Hatsotsrot Street", "Plugat ha-Kotel
  Street", "Ha-Omer Street", "Ha-Malakh Street", "Ha-Tkuma Garden" and others). Interiors (Hurva, Old Yishuv Court
  Museum, Herodian Quarter, Karaite synagogue, the Four Sephardic Synagogues), night festival shots and portraits
  were excluded.
- Most useful: the GPS walk by מקף־עברי, 21 Dec 2025 (A01-A05, B01, B02, D01-D04, G01-G03; CC BY-SA 4.0); Bahnfrend
  2019 (D05-D07, I01, I02; GPS); Djampa 2010-2017 (E01, E06, G08, G09, I03, I04, J01, J02, K02, K04, K07, L01-L04,
  M01, M02, M04; street-named, many GPS); Paul Arps 2013 (E04, E05); Berthold Werner 2010 (B07, G06); Juandev 2011
  (B03, B06); Morany84 / Moranaviv (F01-F03, I07); richlv 2018 (A12, M05); Fallaner 2022 (A06, A07, J04).
- D06 and D07 are the same files as `data/photos_ref/landmarks_city/sidna_05_85913034.jpg` and `sidna_06_85913035.jpg`
  (copied, not re-downloaded). The landmark pass's Hurva / Sidna / Four Sephardic photos in `landmarks_city/` are
  cited by path (hurva_01, hurva_02, hurva_03, hurva_06, hurva_08, sidna_03, seph_01-04).
- Coordinate caveats: K01, K05 carry the Batei Mahase Square geocode (428.8,-243.7); I02 (497.7,-19.2) and M02
  (372.9,-31.1) lie just north of the sector (s09 / s05); A06, A07, A12, C03, C05, E08, F05, G07, H04, J02, J04, K04,
  L02 have no GPS. H04 is a reproduction of an older photograph of the 1970s-80s housing (style reference only).
- Commons throttled thumbnails (429, Retry-After 600 s, honoured): 11 lower-priority selections and the Tanners'
  Gate / Cardo Minimus views (Djampa 2009) were skipped; 13 downloaded files were discarded at review (duplicates,
  night shots, portraits, a sign close-up). No renders were made in this research pass.
- OSM: data/osm_local.json (ways, nodes, buildings); spec: data/spec/s06_jewish.json; terrain:
  pipeline/terrain_street.py
  `street_z` and the OS 1865 spot heights (data/raw/terrain/os1865_spot_heights.csv).
