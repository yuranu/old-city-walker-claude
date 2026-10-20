# s05_souks: lower David St, the souq crossroads, Chain St (west), St Mark St: visual reference

Local frame: x east, y north, metres from the Jaffa Gate OSM node (lat 31.7766282, lon 35.2275435).
Sector box (data/sectors.json): x 152..420, y -42..48 (24,120 m²). It is the band between the s00 hero area
(Jaffa Gate, upper David St, x < 152) and the Haram side. North of y 48 is s04 (Christian Quarter, Muristan, the
three covered souqs north of y 48); south of y -42 are s01 (Armenian) and s06 (Jewish Quarter); east of x 420 is s09.
Spec: `data/spec/s05_souks.json`, 118 buildings (29 of them infill pieces `f*`), no landmark ids in the sector.
Photos: `data/photos_ref/s05_souks/KNN_<pageid>.jpg`, cited below as **A01**, **E04** and so on. Titles, authors,
licences, dates and GPS are in `index.json` there. Camera positions come from EXIF/Commons GPS where the file has it
("cam (x,y)"); several tags are place geocodes or a few metres off, see Provenance. Directions were fitted to OSM
(street axes, the sun slot along a street, ceramic street signs, the Redeemer tower and the Dome of the Rock).
Scale comes from people (1.7 m), doors (2.2-2.8 m shop leaves) and OSM edge lengths.
Confidence: **H** = seen clearly in 2+ photos, or OSM geometry plus one photo; **M** = one clear photo or a
consistent estimate; **L** = inferred, or seen only at an angle or far away.
Baseline renders of the current build: `renders/sectors/s05_souks/r0_baseline/` (see section 0 and 6).

> Status: research pass, 2026-10-20. 80 photos in `index.json` (121 downloaded and looked at; the rest were shop
> interiors, wrong places or duplicates). Coverage: David St x 152-342 (both the open and the covered parts), the
> crossroads and the south ends of Suq al-Lahhamin / al-Attarin / al-Khawajat, Chain St x 342-420, Khan al-Sultan,
> the market-roof promenade (Gagot Galizia), St Mark St, Habad St (north end), the Church of St John the Baptist
> and the Muristan gate passage are photo-backed. Maronite Convent St, Biqqur Holim and Ararat are OSM + survey
> only (one or two photos of details).

---------------------------------------------------------------------------------------------------------------

## 0. Key facts and likely model errors (summary)

1. **David St is blocked in the current model.** `pipeline/infill.py` skips every highway with layer < 0, and David
   St (way 279685572) is tagged layer -1 (it is the covered souq) without being in `COVERED_SOUQS`, so it gets no
   street corridor. Infill pieces then stand on its centreline: **f181** at x 165-187 (also across the mouth of
   Christian Quarter St, x 175-176, y 11-20), **f180** at x 196-279 in pieces, including a **2.5 m thick wall right
   across the street at x 214-217** (its east face (215.3,8.5)->(216.8,14.9)), **f190** at x 304-322 and **f158** at
   x 333-342. The same happens on the Jewish Quarter Rd north end (way 4710079, layer -1: f158 at y -2..19, f150 at
   y 37-46) and on the Cardo/Suq al-Attarin line (way 123231486, tunnel, layer -1: f158 at y -30..7; f144 at
   y 26-57 in s04). The baseline render `david_vault_w` (camera on the centreline at (222,13.2) looking W) ends at a
   blank stone wall with a wooden door 6 m ahead. Every David St photo (A01-A13, B01-B10, C01-C05) shows a
   continuous walkable market street. **H** (spec rings, render, photos). Needs code: section 6 / requests R1.
2. **The south side of David St x 215-310 is open garden at street level in the model; in reality it is a
   continuous row of shops.** OSM maps no building there; garden 1393351630 (x 212-253, y -9..11) and
   forest 290693096 (x 257-315, y -9..14) are kept free of infill. B04 (cam (237,16), looking W), B06 (from the
   Muristan corner (≈268,16), looking W: tall round-headed teal shop doors on the left/south side), B07 (cam
   (261,20)) and C01 (x ≈ 297, looking E: tall pointed openings with dark green lattice gates on the right/south
   side) all show shops on the south side. The gardens are the **Lutheran guesthouse terraces** at the St Mark St
   level, ~5.5-6 m above David St, i.e. on top of / behind a one-storey vaulted shop row (G07, G08). **H** for the
   shops, **M** for the terrace level.
3. **David St alternates open and covered stretches** (west to east): open with shed canopies x 152-177; a
   **groin-vaulted (cross-vaulted) section x ≈ 177-192** (A01 cam (180,9), A04 cam (183,11), A03); open with canopies
   x 192-268, with **flights of shallow steps at x ≈ 200-237** (A02, A13, B03, B05); then covered x ≈ 270-325 by
   **masonry transverse arches with a light barrel roof of painted corrugated sheet on wrought-iron scroll arches**
   between them (C01, C02, C03-C05); then the **vaulted crossroads** x 322-345. The model has no vaults on David St
   and no steps east of x 175. **H** for the sequence, **M** for the exact x limits.
4. **The souq crossroads (x 322-345, y 6-37) is covered, with the "Galicia roofs" promenade on top.** OSM area
   655718796 "Gagot Galizia" is `highway=pedestrian, area=yes, location=roof, tourism=viewpoint`; the spec treats it
   as open ground, so the crossroads is a 20 x 30 m open plaza at street level in the model. In reality the six
   souq streets meet under vaults (D03, D04, D05, E01) and the roof above is a paved terrace with black railings,
   globe lamps and a plastered skylight dome (F04, F05; the souq roofs around it are barrel humps with lunettes,
   F07, F08), reached by a **black steel stair** from the St
   Mark/Habad junction at (318,-6) (OSM steps 1104187000, D08) and by stone stairs elsewhere (F20). **H**
5. **Chain St (Silsileh, way 277508275) is vaulted from the crossroads to the Plugat HaKotel corner (x 345-≈378)**:
   plastered groin vaults, spring ~3 m, crown ~5 m, flexible silver air ducts and cables slung under them (E01, E02,
   E04, E03). **East of x ≈ 385 it is open to the sky under a steel frame with wire mesh** (anti-missile grille) at
   ~5-6 m, with green shed canopies below (E07 cam (416,16), E08 cam (401,14) looking up). **H** for both, **M** for
   the change point.
6. **Muristan St leaves David St at x ≈ 268-270 through a groin-vaulted passage** (~5 m wall to wall, plastered
   pointed groin vaults between transverse arches, stone benches along both walls, B13) and ends at the **Muristan gate**: a tall pointed arch in clean pale ashlar with the
   **Prussian eagle relief** in a shield above and a railing on the roof terrace (B14, B15), on the s04/s05
   boundary at y ≈ 41-48. The model has an open 2.5-3 m lane there. **H** for the form, **M** for the extent.
7. **Church of St John the Baptist (w166965387, in this sector, not a registered landmark)**: west facade e1
   (x ≈ 193, faces W) on a paved forecourt off Christian Quarter St, round-arched recessed portal, two-stage
   **bell gable** with two bells, and a **gold diamond-scale clad dome** with a gilt cross (2019-2021: H02, H03, H06;
   it was silver-grey ribbed in 2008-2013: H01). A semicircular **apse** with a copper eave faces E onto the Aftimos
   lane at (208,43) (H04). The generic builder gives it three random shallow domes at 11.7 m. **H**
8. Terrain: David St falls **~11.3 m** from x 155 (street_z -4.8) to the crossroads (-16.1), most of it before
   x 233 (-13.0); Chain St falls another 6.6 m to x 425 (-22.7). The OS 1865 spot heights inside the sector agree
   with `terrain_street` within 0.4 m. St Mark St runs 5-6 m above David St (garden terraces between). **H**
   (survey), see section 5.

---------------------------------------------------------------------------------------------------------------

## G. OSM geometry of the core (from data/osm_local.json and data/spec/s05_souks.json)

Streets (OSM centrelines, local m; z = `street_z` relative to the Jaffa Gate street):

| street | OSM way | points in the sector | tags | z |
|---|---|---|---|---|
| David St (Tariq Suwayqat Allun / Suq el-Bazaar) | 279685572 | (159,8.2) (175.6,9.4) (177.9,12.0) (192.9,13.0) (205.8,12.7) (211.8,13.1) (235,13.3) (243.7,13.8) (268.5,16.0) (299,17.2) (315.6,18.4) (326.8,18.2) (332.4,18.2) (342.4,17.4) | pedestrian, **layer -1**, sett | -4.8 (x 155) → -9.7 (183) → -12.0 (213) → -13.0 (233-253) → -14.1 (273) → -15.3 (303) → -16.1 (333) |
| Chain St (Silsileh, Hashalshelet) | 277508275 | (345,9.1) (357.9,10.3) (365.4,10.0) (378.1,9.9) (393.1,12.1) (417.5,16.6) (454,22) | pedestrian, sett, layer 0 | -16.1 (346) → -16.0 (362) → -16.9 (378) → -18.9 (393) → -22.2 (417) |
| Suq al-Lahhamin (Butchers') | 26506018 | (326.8,18.2) (326.5,23.0) → north to (323,96.5) (s04) | pedestrian, layer -1, in `COVERED_SOUQS` (vaulted, s04 vault) | -16.0 |
| Cardo / Suq al-Attarin line | 123231486 "HaKardo" | (332.4,18.2) north to (327,137); south (332.5,9.7) (333.4,1.0) (332.7,-2.8) (328.6,-48.7) | pedestrian, **tunnel, layer -1** | -16.1 (y 18) → -15.0 (y -12) → -9.6 (y -44) |
| Jewish Quarter Rd / Suq al-Khawajat line | 4710079 "Jewish Quarter" | (344.5,39.2) (342.2,36.0) (342.4,17.4) (345.0,9.1) (344.6,0.9) (344.9,-3.7) (342.4,-45.9) | pedestrian, **layer -1** (whole way, y -219..116) | -16.7 (y 44) → -16.2 (y 13) → -13.9 (y -19) → -10.5 (y -43) |
| tunnel link Cardo-JQ Rd | 123245531 | (333.4,1.0)->(344.6,0.9) | pedestrian, tunnel, layer -1 | -16 |
| Gagot Galizia (market roofs) | 655718796 | area x 321.6-357.6, y 6.3-36.8 | pedestrian **area, location=roof**, viewpoint | (roof) |
| roof stair | 1104187000 | (318.3,-5.7)->(321.8,6.3) | steps, incline up (to the roof) | |
| St Mark St (west part) | 26492723 + 616359698 | (176,9)->(177,8)->(177,-1) -> (206,-1) -> (214.1,-3.3) | pedestrian; 26492723 incline up | -8.5 → -6.1 → -7.3 |
| St Mark St (east part) | 616359697 | (214.1,-3.3) (231.1,-10.1) (238.1,-12.1) (259.3,-17.2) (269.1,-17.2) (277.8,-16.3) (287.1,-12.6) (301.7,-11.0) (308.0,-9.5) | pedestrian, sett | -7.3 (214) -7.2 (238) -8.7 (269) -11.0 (284) -13.6 (308) |
| St Mark tunnel to Habad | 290731782 | (308,-9.5)->(313,-8)->(318.3,-5.7) | pedestrian, tunnel, layer -1 | -14 |
| Habad St (north part) | 26506011 | (315.6,18.4) (316.9,0) (318.3,-5.7) (320.7,-12.9) (318.1,-32.8) (316.2,-44.0) | footway | -15.6 (y 18) → -14.9 (y -5) → -11.6 (y -28) → -9.1 (y -44) |
| Maronite Convent St (steps) | 616359696 | (214.1,-3.3) (204,-17) (202,-29) (201.4,-31.7) | steps, step_count 32, ramp, handrail, incline up (to the SW) | -7.3 → +5.1 |
| Maronite Convent (steps) | 1005635992 | (201.4,-31.7) (192,-36) (179,-40) (169,-42) (156,-42) | steps 11, ramp, handrail | +5.3 → +6.1 |
| Biqqur Holim | 26492725 / 616359701 / 616359702 / 616359703 | (269,-17)->(269,-26) **covered** steps 5 → (266,-30) → (250,-39) (244,-49) (225,-56) | steps, ramp | -8.7 → -5 |
| Ararat Hamal'ach | 616359700 | (266,-30)->(278,-60) | pedestrian | |
| Muristan St (south end) | 26492713 | (268.5,16.0)->(267.9,38.3)->(267.2,58.1) | pedestrian, cobblestone (no tunnel tag) | -13.9 (y 17) → -14.9 (y 41) |
| Suq Aftimos (west branch) | 26492716 | (205.8,12.7)->(211,39)->(213,45)->(211,47)->(208,57) | pedestrian, sett | -12.3 (y 19) → -13.3 (y 43) |
| Khan al-Sultan passage | 1020791459 | (393.1,12.1)->(390.3,32.0) | footway, **layer 1** (no tunnel tag) | |
| Plugat HaKotel | 123246252 | (378,10) (378,1) (377,-17) (377,-36) | footway, sett (steps up to the S, E05) | -16.9 → -11 |

OSM wall-to-wall widths (perpendicular rays from the centreline to OSM footprints, every 5-6 m; script
`build/spec_s05_souks/widths.py`):
- **David St**: 5.2 m at x 155 (s00 edge); **1.4-1.6 m at x 183-190** (w1392856694 and w290692952 are drawn 0.5-0.9 m
  from the centreline: footprints of the rooms over the vaulted section; the real clear width is ~3.5-4 m, A01);
  3.7 m at x 201.5; 9.6-17 m at x 207-213 (the Aftimos junction); from x 214 to 323 the **north wall is 1.7-2.9 m
  from the centreline** (w1393364219, w1393364229, w1393364228) and the **south side is unmapped** (gardens behind).
  Photos give 3.5-4.5 m wall to wall and 2.5-3.5 m clear between goods and thresholds (A01, A02, B04, B06, C01).
- **Chain St**: north wall 1.5-2.3 m (w1393310559, x 360-371) and 2.8-3.4 m (w1393310560, x 346-354); south wall
  4.9-5.3 m (w1393371463, x 375-384) and 4.0-6.9 m (r3865736, x 395-409); gaps elsewhere. Photos: 4-5 m (E04, E07).
  The spec builds it 4.4 m (infill half-width 2.2).
- **St Mark St**: 2.4-4.5 m (x 214-300), with pockets of 7-11 m at x 231 (the alley to w290692949), x 249 and x 279.
- **Maronite Convent St steps**: 7.4-7.7 m at the bottom (x 208-211), 5.8 m, then 3.8 → 2.3 m at the top (x 201-203).
- **Habad St**: 5.0 m at y -10..-15 (w1393297099 / w1393297085-86), 7.2 m at y -40; no mapped buildings at all on
  either side for y -2..18 (x 300-322).

Key buildings (spec ids; height = top - ground in the spec):

| feature | OSM / spec id | position (local m) | spec now | notes |
|---|---|---|---|---|
| Church of St John the Baptist (Greek Orthodox) | w166965387 | x 192.5-210, y 31.9-54.0, 295 m²; c (200.1,42.5) | 11.7 m, 3 generic domes, rubble | west facade e1 (192.5,48.9)->(193.2,31.9) faces 268° onto the forecourt; apse at e6-e8 (208.6,40.3)-(209.2,44.9) faces E onto the Aftimos lane; OSM entrance node n7095366411 (175.8,37.4) on Christian Quarter St |
| St John forecourt | (no OSM area; free of buildings) | x 184-192.5, y 25-46; OSM tree n14052513175 (185.5,36.1) | open | paved pale slabs, potted geraniums, globe-lantern lamp post (H02) |
| CQR frontage block south of the church | w290821775 | x 174.6-190.4, y 23.9-53.2 | 11.2 m, flat | OSM roof:shape hipped, roof_tiles (ignored by the spec); the St John gate with Greek plaque, house no. "237/242", is in its west face on CQR (H07; see 2.1) |
| Maronite convent and church (Mar Maroun) | w290692945 | c (187.7,-22.8), 453 m², building:levels 5 | 19.2 m, 5 domes, 1 roof room | Maronite Church node n4057349707 (176.9,-22.5), door n14099701720 (200.7,-24.3) on Maronite Convent St; square campanile (G11, G12) |
| Lutheran guesthouse (Gästehaus des Propstes) | w290693095 (OSM name: yeshiva "Lenetivot Israel") | c (255.3,-5.8), 427 m² | 12.6 m, flat, 2 domes | OSM node "Lutheran Hospice" n4443280390 (273.1,-14.2) inside it; OSM roof:shape hipped, roof_tiles; 3 storeys, four small gabled dormers (dark timber eaves) with arched French windows and curved black balconies on the garden (north) face, roof terrace railing on a stair tower (G08) |
| Lutheran garden terraces | garden 1393351630; forest 290693096 | x 212-253, y -9..11; x 257-315, y -9..14; trees n14057570876-81 at y 4-9 | kept open (at street level) | raised planted terraces with palms and pepper trees, St Mark level (G07, G08) |
| Porat Yosef (kiosk/stair) | w1394034711 | (253.4-256.9, 5.5-9.0), 11 m² | 6.3 m | Café Luther node n6832647387 (255.9,7.7) inside it: probably a stair/door from David St up to the terrace (unverified) |
| Citadel Hostel | w290692949 (node n701248333 (235.9,-18.3)) | c (240.7,-29.4), 474 m² | 11.9 m | St Mark St 20; passages 722675055/58 run through it (G05) |
| New Swedish Hostel | in f180 (node n5472975322 (265.1,14.6), "29 (67) David") | north side x ≈ 249-265 | infill | plain door under a segmental arch, blue "SWEDISH HOSTEL" sign (B08, B10) |
| North row of David St | w1392856694, w1393364222, w1393364219, w1393364221, w1393364232, w1393364231, w1393364224, w1393364225, w1393364229, w1393364228, w1393371451 | street faces e0 at y 14.4-25.6, x 177-324 | 5.9-13.4 m | see the frontage list in 1.2 |
| South row of David St (west) | w1394458564, w290692952, w290692957 | x 152-158, 176-191, 196-215 | 5.5-10.6 m | e9 of w290692952 (191.5,12.1)->(178.2,11.8) and e8 of w290692957 (214.7,10.9)->(196.5,10.5) face N onto David St but are flagged unexposed because infill sits in the street |
| Rooftop viewpoint | node n12899629001 (308.2,33.8) in w1393364228 | | 11.3 m | roof terraces over the north row with tall steel fences, Redeemer tower beyond (F12, cam (316.3,28.3)) |
| Sultan Khan (Khan al-Sultan, al-Wakala) | node n6514903110 (394.2,34.6); passage way 1020791459 | courtyard ≈ x 388-401, y 33-46 (no OSM polygon) | covered by infill f149 | 2-storey courtyard khan (E12, E13) |
| "Crusader arched markets underground" | node n9358800051 (332.5,9.7) | on the Cardo line | in f158 | the vaulted market at the Cardo's north end (D03) |
| "Crusader shop fronts underground" | node n9358719799 (333.6,-11.0) | in w1393297098 | | |
| building=roof, layer 1 | w1393297096 (342.2,-39.6), w1392856695 (205.1,19.4), w1393297055 (292.7,-38.8) | | built as 5-6 m solid buildings | w1393297096 stands on the Jewish Quarter Rd centreline (y -42..-37): a sabat/roof over the street, not a building on the ground |

---------------------------------------------------------------------------------------------------------------

## 1. Sector character and STREET PROFILES

### 1.0 Character
The commercial spine of the Old City between the Jaffa Gate and the Haram. **David St** drops eastwards as a
narrow market street (3.5-4.5 m) lined on both sides by one-room shops (dukkans) closed by **teal and pale-green
panelled steel doors** and roofed in turn by **shed canopies on steel brackets**, by **stone groin vaults**, and,
in its lower part, by a **light barrel of painted corrugated sheet on wrought-iron scroll arches**. It ends at the
**crossroads** with the three parallel covered souqs (Lahhamin, Attarin, Khawajat) running north and the Cardo,
Habad St and Jewish Quarter Rd running south, all vaulted at the junction, with the **Galicia roofs promenade**
over them, and continues east as **Chain St**, vaulted, then open under a wire-mesh grille. South of David St, 5-6 m
higher, lies a quiet residential and hostel quarter (St Mark St, Maronite Convent St, Biqqur Holim) of pale
ashlar lanes, stairs and arched passages, with the Lutheran guesthouse gardens and the Maronite convent belfry.
North of David St the Church of St John the Baptist (gold dome) and the Muristan gate passage lead into s04.
From the roofs and the Tower of David the sector reads as a **dense pale roofscape of flat roofs, long barrel-vault
humps with rows of skylight boxes, low white domes, satellite dishes, black water tanks and a few red-tile pyramid
roof rooms**, with the Redeemer tower to the north (bearing ~328° from the roof plaza) and the gold Dome of the
Rock to the east (~70°).
Stone: cream to honey limestone, rough and darkened at shop level, plastered/whitewashed inside the vaults; clean
pale ashlar on St Mark St (Lutheran buildings) and on the Muristan gate.

### 1.1 Profile table (which OSM street gets which profile)

| profile | OSM streets | key look |
|---|---|---|
| P1 open market street | David St x 152-177 and x 192-268 | 3.5-4.5 m, shops both sides, teal/pale-green steel doors, shed canopies on triangular steel brackets with ring scrolls, sky slot ~1 m, hanging cream boards in ogee frames, flights of low steps |
| P1v vaulted market street | David St x 177-192; crossroads x 322-345; Chain St x 345-378; Cardo y -12..18; JQ Rd y -3..18; Lahhamin (all); Attarin/Khawajat south ends | plastered groin or pointed barrel vaults, spring ~2.8-3 m, crown ~4.5-5.5 m, same shops; no canopies; cables, ducts, bulbs |
| P1s sheet-roofed market street | David St x 270-325 | masonry transverse arches; between them a barrel of white/pale blue painted corrugated sheet on wrought-iron scroll arches at ~5-6 m; tall pointed or round shop openings, dark green lattice gates |
| P1g grille-roofed market street | Chain St x 385-420 | open, green shed canopies, a steel frame with wire mesh at ~5-6 m over the whole street |
| P2 residential lane | St Mark St (616359697, 616359698), Habad St north, Maronite Convent St, Biqqur Holim, Ararat | 2.4-4.5 m, pale ashlar, few shops, hostel/convent doors, arched passages and stairs, lamps on brackets, bougainvillea |
| P3 vaulted passage | Muristan gate passage (26492713, y 17-41); Khan al-Sultan entrance (1020791459); Biqqur Holim covered steps (26492725); passages 722675055/58 | stone groin or barrel vaults, 1-5 m wide, benches in the Muristan passage |
| P4 roof promenade | Gagot Galizia (655718796) and the roof walks over the souqs | paved roof plaza, black railings, globe lamps, skylight domes, barrel-vault humps |
| P5 courtyard | Khan al-Sultan courtyard; St John forecourt | open paved yards inside blocks |

### 1.2 P1: David St, open stretches (x 152-177 and x 192-268)
Photos: A02 (2009, 7:30 a.m., all closed, cam (202.7,11.7), looking E along the sun slot), A11 (2017, (200,14)),
A12/A13 (2011, the Aftimos corner (207,13)), B01 (2011, closed), B03 (2014 early morning, closed, (224,17)),
B04 (2011, cam (237,16), looking W), B06 (2014, closed, from the Muristan corner (≈268,16), looking W; the
"MURISTAN RD." ceramic sign is on the right pier), B07 (2012, closed, cam (261,20)), B09, B10.
- **Width**: 3.5-4.5 m wall to wall, 2.5-3.5 m clear between the raised thresholds and goods. North wall 1.7-2.9 m
  from the OSM centreline (OSM); put the south wall ~1.5-2 m south of the centreline. **H**
- **Shop openings (closed)**: one dukkan per 2.5-3.5 m of frontage, openings 2.0-2.8 m wide, 2.8-3.2 m to a flat
  steel lintel under the canopy (A02, B01, B07). Two other forms recur: **tall round-headed openings ~4 m to the
  crown with teal panelled doors and a teal arched fanlight grille** (A02 north side at x ≈ 205; B06 south side at
  x ≈ 245-265, a row of 3-4) and **plain segmental arches** (A01). **H**
- **Doors**: mostly **teal / pale verdigris panelled steel doors**, 2-4 leaves, each leaf in 3-4 tall panels, two
  hasp bars with padlocks at ~1.0 and ~1.9 m (A01, A02, B01, B03, B06). Also **pale teal leaves with diagonal X /
  Z flat-bar bracing** (A02 north side), **cream/pale-yellow panelled doors** (A02 south side), **dark blue
  panelled steel doors** (B09 "ALABAMA THE HEART OF DIXIE" board above; B10 left side by the Swedish Hostel),
  **grey corrugated roll-down shutters** (B07 left, the bigger shops) and the odd **black bar grille gate** (A02).
  Green paint daubs over graffiti on the doors (B01). **H**
- **Thresholds**: stone platforms 0.15-0.35 m high, 0.4-0.7 m deep along both sides; higher (~0.3 m, two steps) in
  front of the round-arched south-side shops (B06). **H**
- **Canopies**: continuous on both sides: steel frames with triangular brackets carrying **ring/C-scroll
  infill**, painted dark green or black, corrugated sheet roofing (some translucent), front edge ~3.0 m,
  ~3.6-3.8 m at the wall, projecting 1.2-1.5 m; they leave a **0.8-1.2 m slot of sky** (A01 view beyond the vault,
  A02, B03, B06, B07). Horizontal steel tie-bars cross between the two canopy rows (B06). Cream/white scalloped
  fabric awnings here and there (B04 right side). **H**
- **Signs**: hanging **cream boards in teal or black ogee-cornered frames** perpendicular to the street at
  ~2.8-3.2 m, many blank (A01, A02, B06); light boxes; the blue **"SWEDISH HOSTEL"** sign over a plain door on the
  north side at x ≈ 249-265 (B08, B10; OSM node n5472975322 (265.1,14.6), "29 (67) David St"); the white
  **"ALABAMA / THE HEART OF DIXIE"** board over blue doors at x ≈ 265 (B09); the ceramic street sign
  **"רחוב דוד / طريق الباذار / SUQ EL-BAZAAR RD."** (white tiles, green border, B12; position unknown, lower David St);
  "CHRISTIAN QUARTER ST." sign at the CQR corner with a CCTV camera (A09). **H**
- **Steps**: the street is stepped from the CQR junction down to x ≈ 237 (A02 foreground step down eastward at
  x ≈ 203; A13 people on a flight at x ≈ 207; B03 and B06 show flights 40-60 m west of the camera, i.e. at
  x ≈ 215-230; B05 not kept). Risers 0.12-0.16 m, treads 1.0-3.0 m, edges are plain slab edges. Between x 237 and
  268 the floor is a gentle slope (B06 foreground). **H** for steps existing, **M** for their x positions.
- **Paving**: large pitted (rough-picked) limestone slabs in courses across the street in the upper part (A01, A02),
  smaller dark grey setts ~0.2 x 0.4 m in courses from x ≈ 230 east (B04, C01); round cast-iron manholes on the
  centreline every ~8-10 m (A01, A02, B06); long steel trench grates across the street (A06, B04). **H**
- **Above the canopies**: rough honey ashlar, 1-2 upper storeys with small grilled windows, AC units, conduits,
  cables, a balcony on a building beyond (A02); flexible air ducts. The north row reaches ~8-11 m above the street;
  rooftop rooms set back higher. **M**
- North frontage, spec edges (all face S, ~173-179°): w1392856694 e0 (177.6,12.9)->(203.1,14.5) 25.6 m (vaulted
  part, then open); w1393364222 e0 (207.4,14.4)->(213.1,14.6); w1393364219 e0 (214.4,14.8)->(232.9,16.1) 18.5 m;
  w1393364221 e0 (236.0,18.0)->(242.6,18.5); w1393364232 e0 (244.3,18.3)->(248.9,18.9); w1393364231 e0
  (249.7,21.7)->(255.2,22.4) (set back 3 m: a recess or OSM error); w1393364224 e0 (256.8,18.3)->(262.2,18.7);
  w1393364225 e0 (263.3,18.5)->(267.9,18.6). Gaps at x 233-236, 243, 249 are probably lanes or doors to courtyards
  (OSM has no ways there).
- South frontage: only x 152-158 (w1394458564), 176-191 (w290692952 e9) and 196-215 (w290692957 e8) are mapped.
  x 215-310 needs a new street wall (see 0.2 and requests).

### 1.3 P1v: the vaulted section x ≈ 177-192 and the CQR / St Mark junction (x 172-180)
Photos: A01 (2009, cam (180.3,9.4), under the first bay, looking E into the open part), A04 (2011, cam (183,11),
under the vault looking E toward the light), A03 (2012, cam (187,12), closed, a stone arch in front, open street
beyond), A06 (2014, (169,13): a pointed arch over the street), A05 (2011, (181,10): St Mark St steps), A09, A14.
- **Vault**: plastered/whitewashed **groin (cross) vaults** in bays ~4 m long, springing at ~2.8-3.0 m from the
  shop piers, crown ~4.5-5 m; a round light fitting at the crown (A01). The vault ends at a pointed arch at
  x ≈ 190-192 (A01, A03). Under it: teal and grey-green panelled doors both sides, projecting steel hanging rails
  (A01). Length ~12-15 m. **H** for the form (A01, A04), **M** for the extent.
- At the CQR junction (x ≈ 172-178): a pointed stone arch spans the street (A06), CQR opens to the north
  (ceramic sign and CCTV, A09), and **St Mark St climbs south as a steep stair under an arch** (A05: ~15 steps of
  ~0.15 m between rough ashlar walls, shops either side at the bottom; OSM way 26492723 incline up). **H**

### 1.4 P1s: the covered lower stretch x ≈ 270-325
Photos: C02 (2011, x ≈ 279, direction not established: a massive transverse stone arch, then light, then more
arches; tall pointed-arch openings with black lattice and green doors on the left), C01 (2014, closed, x ≈ 295-300, looking
E: the "...Othman Ibn Affan Mosque" black sign on the left/north side), C03, C04, C05 (2013, looking down from the
roof promenade).
- **Roof**: masonry transverse arches (pointed, ~4 m span) every ~10-15 m; between them a **light barrel vault of
  painted corrugated sheet** (white, peeling, with pale blue ribs) carried on **wrought-iron arched trusses with
  scroll infill**, crown ~5.5-6 m, leaving slots of daylight at the ends (C01, C05). **H**
- **Shops**: tall **pointed-arch openings ~2.5 m wide, ~4.5 m high**, filled with **dark green steel lattice
  (diagonal grid) gates** over green doors on the south side at x ≈ 300 (C01 right); green panelled doors and black
  shed canopies with brackets on the north side (C01 left); translucent corrugated canopies at ~3 m (C05). **H**
- **Floor**: dark grey small setts in courses, raised slab kerbs 0.15-0.2 m along both sides (thresholds), round
  manhole on the centreline (C01). No steps. **H**
- **Othman ibn Affan Mosque**: its entrance is on the north side at x ≈ 295-300 (C01 sign; Commons file of the
  entrance geotagged (297.4,43.1)). **M**
- Spec north frontage: w1393364229 e0 (270.8,17.7)->(288.8,19.5) 18.1 m and w1393364228 e0 (291.1,19.8)->(310.6,20.8)
  19.5 m (both get 15 openings now), w1393371451 e0 (313.0,24.2)->(324.2,25.6) set back 6-7 m (the Lahhamin mouth).

### 1.5 The crossroads (x 322-345, y 6-37) and the south ends of the three covered souqs
Photos: D01 (2012, closed, cam (321,17), Lahhamin), D02 (2016, night, closed, Lahhamin), D03 (2016, cam (330,15):
"on the Cardo, just south of the Perfume Market"), D04 and D05 (cam (342,3): "north end of Jewish Quarter road",
2017 at night), D06 (2010, (328,34), Attarin corner), E01 (2012, (343,5), Chain St start).
- **Suq al-Lahhamin** (x ≈ 324-327): a long, straight **whitewashed pointed barrel vault** with a line of lamps
  and skylight openings at the crown, closed **grey steel doors and green roll-down shutters**, large pale slabs
  with a **darker central channel strip** (D01, D02). Already vaulted in s04 (vault id 26506018 from y 18). **H**
- **Cardo line** (x ≈ 331-333, y -12..18): whitewashed **pointed cross vaults** in bays, a hanging iron lantern,
  closed white, grey and green doors, raised slab thresholds ~0.2 m (D03). In the model it is under infill f158.
  **H** for the vaulted market, **M** for its southern end (the street rises 1 m by y -12 and the Cardo continues
  as an underground passage under w1393297098).
- **Jewish Quarter Rd north end** (x ≈ 344, y -3..17): a **rough stone pointed barrel vault**, shops, strings of
  bulbs (D04, D05). In the model under f158. **H**
- **Suq al-Attarin / al-Khawajat south ends** (x ≈ 332 and ≈ 342, y 18-48): covered (D06 shows the roofed souq
  at the Attarin corner; F01/F08 show the souq roofs as barrel humps). OSM: "Suq Al Attarin" is only the short E-W
  footway 26611965 at y 116-122 (s04), and the Khawajat line is way 4710079 named "Jewish Quarter", so
  `COVERED_SOUQS` misses both. **M**
- At the junction itself the vaults meet; the Galicia roof is above (1.7). **M**

### 1.6 Chain St x 342-420 (Silsileh / Hashalshelet / Tariq Bab al-Silsila)
Photos: E01 (2012, (343,5)), E02 (2013, (352,6)), E04 (2011, (363,9), "at the corner with Plugat HaKotel"),
E03 (2013, (376,10)), E05/E06 (2024, (367-375,12): stair up to Plugat HaKotel and inscription), E07 (2011,
(416,16)), E08 (2011, (401,14), looking up), E09 not kept, E10-E13 (Khan al-Sultan).
- **x 345-≈378: vaulted.** A row of **plastered groin vaults**, greyish, spring ~3 m, crown ~5 m, width ~4-4.5 m;
  shops in pointed bays both sides; **flexible silver air-duct pipes** and bundles of cables hang under the vaults;
  strings of bulbs (E01, E02, E04, E03). **H**
- **x ≈ 385-420: open, under a wire-mesh grille**: a light steel frame of crossbars at ~5-6 m carrying square
  wire mesh over the whole street (E08 looking up), green shed canopies on both sides below, shops with goods hung
  high, a blue plastic crate; a dark vaulted bay continues beyond x 420 (E07, the s09 part). **H**
- **Plugat HaKotel corner** (x ≈ 377-378): a stone stair rises south through a doorway with an open **pale green
  steel gate** and a grey crowd barrier (E05); a carved **Mamluk Arabic inscription** slab under the ceramic sign
  **"PLUGAT HAKOTEL"** (E06); the ceramic "CHAIN GATE ST." sign (E05). **H**
- **Khan al-Sultan** (entrance on the north side at x ≈ 393, OSM footway 1020791459): a **tall pointed barrel-vaulted
  entrance hall ~20 m long** with transverse ribs on corbels and upper windows (E10, E11, a green bin and a lantern),
  leading to a **paved open courtyard ringed by a two-storey arcade with an upper gallery (turquoise railings)**,
  blue doors, satellite dishes, and low white domes on the roofs (E12, E13). Courtyard ≈ x 388-401, y 33-46 (OSM
  node n6514903110 (394.2,34.6) and the end of the passage at (390.3,32.0); no OSM polygon). In the model it is
  infill f149. **H** for the form, **M** for the ring.
- Floor: worn grey setts; the street falls ~3 m from x 362 to 393 (survey); steps not clearly seen. **L**
- Shops: souvenirs, ceramics, spices, plastics; when closed, grey/green steel doors as on David St (E-series are
  all open-shop photos). **M**

### 1.7 P4: the market roofs promenade (Gagot Galizia) and the souq roofs
Photos: F01, F02 (vent boxes), F03 (looking down into a souq through a grille), F04 (2014), F05 (2017), F07 (2016),
F08 (2013), F10 (2009), F11 (2009, cam (370,8)), F12 (2016, cam (316,28)), F20 (stair up), D08 (black stair).
- **Roof plaza** (OSM area 655718796, x 322-357, y 6-37): large pale paving slabs, **black steel railings ~1.0 m
  with vertical bars**, **white globe lamps on grey poles**, timber/steel benches, low stone benches and steps
  between levels; a **plastered shallow cloister dome on a square ashlar base with two small arched openings** (a
  skylight over the souq below) and a sunken stairwell beside it (F05; a similar white dome in F04); a plastered dome
  with a tall chimney (Commons "Views in October of 2019 ... 30", not kept). **H**
- **Tall steel security fences** (2-3 m, vertical bars/mesh) along parts of the roofs, separating the Jewish Quarter
  roofs from the Muslim Quarter roofs (F10, F12). **H**
- **Souq roofs**: the covered souqs show on the roofs as **long barrel humps** with **small arched lunette
  openings** and rows of **skylight/vent boxes: low stone boxes with pitched corrugated sheet caps on rusty steel
  frames** along the crowns; low parapets; weeds in the joints (F01, F02, F07, F08). **H**
- Around: flat roofs, white plastered domes, satellite dishes, black water tanks, solar heaters, red-tile
  pyramid roofs on rooftop rooms (F05, F11), 2-4 storey houses rising above the souq roof (F05). The Redeemer tower
  is the landmark to the NNW, the Dome of the Rock and the Mount of Olives to the E (F04, F05, F10, F11). **H**
- **Level**: ~6-7 m above the crossroads street (one high vaulted storey plus parapet; F05 foreground shows the
  corrugated canopy of a street ~5-6 m below the promenade edge). **M**
- **Access**: the **black steel open-tread stair** (chequer-plate treads, ~1 m wide, ~14+ risers, railing) at the
  St Mark St / Habad St junction (D08, cam (315.8,-3.8); OSM steps 1104187000 (318.3,-5.7)->(321.8,6.3), incline up)
  and a steel stair with railings up a stone wall (F20, position unknown). **H**

### 1.8 P3: the Muristan gate passage (Muristan St, y ≈ 17-41)
Photos: B13 (2011, "Muristan gate and Muristan street", looking N from the David St end), B14 (2009), B15 (2006)
(the gate from the Muristan side).
- A straight passage ~5 m wall to wall under **plastered pointed groin vaults separated by transverse arches** (3-5
  bays, crown ~5 m), ashlar walls, **stone benches ~0.45 m high and ~0.5 m deep** along both sides, open **blue
  wrought-iron scroll gates** at the David St end, pale slab paving with a round manhole; it opens at the far end to the trees of
  the Muristan (B13). **H**
- The **Muristan gate** at the north end: a tall pointed arch (~4 m wide, ~6 m high) in clean pale rusticated ashlar,
  a **black Prussian-eagle relief in a shield-shaped cartouche** above the arch, a cornice and a **steel railing**
  round the roof terrace above, caper bushes on the wall (B14, B15). Hospitallers memorial node n9351323162
  (268.9,49.7) just north. **H** for the form, **M** for the position (y ≈ 41-48, s04/s05 boundary).
- Model: way 26492713 has no tunnel/covered tag, so the lane is open between w1393364225 (e1 (267.9,18.6)->
  (267.2,33.9), faces E) and w1393364229 (e5 (270.2,26.4)->(270.8,17.7), faces W), only 2.5-3 m apart.

### 1.9 P2: St Mark St, Habad St (north), Maronite Convent St, Biqqur Holim
Photos: A05 (St Mark stair from David St), G01 (2014, (222,-6): Maltese-cross keystone on the Lutheran wall), G02
(2014, (290,-5): St Mark St 32 / Biqqur Holim corner), G03 (2013, (310,-11): steep stair), G05 (alley of stairs,
(231,-13)), D08 (St Mark / Habad junction), G09 (2012, (316,-13): Habad St arched passage), G11, G12 (Maronite belfry).
- **St Mark St**: 2.4-4.5 m (OSM), pale to honey ashlar, mostly residential/hostel doors (Citadel Hostel at no. 20,
  the Lutheran guesthouse), few shops except near the two ends (green corrugated canopy on curved brackets and
  green round-arched doors at the Habad end, D08). Round-arched doorways, a **stone arch with a Maltese cross
  roundel in the keystone** on the Lutheran guesthouse wall at (222,-6) (G01). Wall lamps on brackets, AC units,
  steel grille doors (G02). The lane is level west of x 260 and **stepped down eastwards x 269-308** (~4 m;
  G03: risers ~0.15 m, treads ~0.6-0.8 m, iron canopy bracket with a ring scroll). **H**
- **Ceramic sign "רחוב סנט מרקוס / طريق مار مرقس / ST MARK ST."** at the Habad junction (D08). **H**
- **Narrow stair alleys** off St Mark St: G05 (~1 m wide, steep, under an arch, cam (231,-13), i.e. footway 722675050
  and the building passages 722675055/58 through w290692949). **H**
- **Habad St** north part: arched passages and a pointed arch over the lane with a door (G09 at night; RalfR
  2016 not kept); the north end (y -2..18) has no mapped buildings either side (OSM). **M** / **L** for y > -2.
- **Maronite Convent St**: climbs from St Mark St (214,-3) to the convent (201,-32) and on west; the convent's
  **square campanile** has two stages of round-arched openings and a stone pyramidal cap with a cross, rising above
  the lane (G11, G12; position on w290692945 unknown). Carved wooden doors, grey louvred shutters (20 Maronite
  Convent St, not kept). **M**
- **Biqqur Holim** (26492725 covered steps at x 269, y -17..-26; 616359702 steps south-west) and Ararat: OSM only. **L**

---------------------------------------------------------------------------------------------------------------

## 2. LANDMARKS

No id from the landmark registry has its centroid in s05. Seen from the sector (positions from OSM):
- **Lutheran Church of the Redeemer tower** (s04, (268.5,136.3), ~47 m): the landmark above every northward view and
  from all roofs (F04, F10, F12; bearing ~328° and ~135 m from the roof plaza (340,22)).
- **Dome of the Rock** (s11, (734,154)): gold dome over the roofs to the east from the promenade (bearing ~71°,
  ~415 m; F05, F10, F11).
- **Holy Sepulchre domes** (s04, w1022672085): grey domes to the NNW (bearing ~323° from the roof plaza).
- **Hurva synagogue** (s06, w45081545, (360,-144)): white dome to the south (bearing ~173°, 167 m from the plaza).
- **Tower of David / Phasael** (s00, r136164): to the WSW at the head of David St (bearing ~255°).
- Two notable buildings **in this sector that are not in the registry** (described here so the next pass can decide
  between overrides and a landmark request):

### 2.1 Church of St John the Baptist (w166965387), Greek Orthodox monastery
Photos: H01 (≈2008, cam (187.5,39.0) in the forecourt), H02, H03, H04 (2019), H05 (2016), H06 (2021, from the
Redeemer tower), H07 (2010, the gate on CQR), and s04 photos D01/D02/D05/D06 (the dome closing the SW vista of the Muristan).
- **Forecourt** x ≈ 184-192.5, y 25-46 (between w290821775 and the church; OSM tree (185.5,36.1)): pale slabs with
  pinkish ones, potted geraniums, a cast-iron lamp post with three globe lanterns, a wooden balcony on brackets of
  the monastery cells on the north side (H02). Entered from Christian Quarter St through a dark wooden door in a
  stone frame with a **marble plaque in Greek "ΕΛΛΗΝΟΡΘΟΔΟΞΟΝ ΠΑΤΡΙΑΡΧΕΙΟΝ ΙΕΡΟΣΟΛΥΜΩΝ / ΙΕΡΑ ΜΟΝΗ ΙΩΑΝΝΟΥ ΤΟΥ
  ΠΡΟΔΡΟΜΟΥ ΚΑΙ ΒΑΠΤΙΣΤΟΥ"**, house number "237 / 242" painted on the jamb, a narrow arched inner passage behind
  (H07, 2010; OSM entrance n7095366411 (175.8,37.4)). The forecourt lies ~2 m below CQR (spec ground
  -10.7 vs CQR -8.5). **H** for the court, **M** for the level.
- **West facade (e1, x ≈ 193, faces W, 17 m)**: clean pale ashlar, ~7 m to the parapet; a **large round-arched
  recess (~3.5 m wide, ~5.5 m high)** holding a glazed double door (~1.4 x 2.8 m) with black frames, an arched
  window with an iron grille above it and a small icon niche; a reused carved Byzantine capital set in the wall
  above the arch; a round-arched grilled window and a small round-arched door to the left. **H** (H02, H05)
- **Bell gable**: a two-stage open campanile rising ~5 m above the parapet over the portal (left of centre in H02,
  i.e. the north half of e1): each stage one round-arched opening with a bell, cornices, urn finials and a stone
  cross on top. A Greek Orthodox flag on a pole. **H**
- **Dome**: ~6-7 m across on a low drum behind the facade, top ~14-15 m above the forecourt (scaled from the
  2.8 m door in H02, **M**). **Gold diamond-scale cladding with a gilt Orthodox cross on a ball, re-clad between 2013 and 2019** (H02,
  H03, H06; the s04 D-photos 2019-2026); **silver-grey with ribs in 2008 and 2013** (H01; Commons "Suq Aftimos
  ... view to the Church of John the Baptist", 2013). Model the gold state. **H**
- **East end**: a **semicircular apse (~5 m across) with a copper-sheet eave and downpipe** next to a square tower
  block under the dome, behind a **gilded railing**, facing the Aftimos lane at (208,43) (H04, e6-e8). **H**
- Neighbours from the Redeemer tower (H06): red-tile hipped roofs, a rooftop restaurant with a glazed pavilion,
  flat roofs. **M**

### 2.2 Maronite convent (w290692945, 5 levels)
- The tallest building of the south part (spec 19.2 m from OSM levels). A **square stone campanile**: plain shaft,
  two belfry stages each with paired/single round-arched openings, a cornice and a low stone pyramid with a cross;
  next to it terraces with railings, black water tanks and dishes (G11 from a nearby roof, G12 from the lane).
  Position on the footprint not established (the church node is at (176.9,-22.5), the street door at
  (200.7,-24.3)). **M** for the form, **L** for the position.

---------------------------------------------------------------------------------------------------------------

## 3. GATES

The sector has no city gate. Gate-like structures:
1. **Muristan gate** (north end of the Muristan passage, y ≈ 41-48): pointed arch, Prussian eagle, roof railing
   (1.8). **H** for the form.
2. **Khan al-Sultan entrance** on Chain St at x ≈ 393 (north side): the vaulted entrance hall (1.6). **M** for the
   exact facade position.
3. **Arches across David St**: the pointed arch at the CQR junction (A06) and the pointed arches at both ends of the
   vaulted bays x 177-192 (A01, A03); the masonry transverse arches of the lower stretch (C02).
4. **The St Mark St stair arch** at the David St junction (A05) and the **Plugat HaKotel doorway** with its green
   steel gate (E05).

---------------------------------------------------------------------------------------------------------------

## 4. Street furniture, signage and vegetation

Signs and plaques
- **Ceramic street signs** (white glazed tiles, coloured border, Hebrew/Arabic/English): "SUQ EL-BAZAAR RD." (B12),
  "CHRISTIAN QUARTER ST." (A09, with a CCTV camera on a bracket beside it), "MURISTAN RD." (B06, on the right pier
  of the Muristan corner), "ST MARK ST." (D08), "CHAIN GATE ST." and "PLUGAT HAKOTEL" (E05, E06). ~0.6 x 0.4 m at
  ~2.5-3 m. **H**
- **Hanging shop boards** in ogee-cornered frames (teal or black), many blank (A01, A02, B06); the blue "SWEDISH
  HOSTEL" sign (B08, B10); "ALABAMA THE HEART OF DIXIE" (B09); black "Othman Ibn Affan Mosque" sign (C01); arrow
  boards "Mint Tea" (B02); the Arab Orthodox Society Cultural Centre door sign (looked at, not kept). **H**
- Mamluk inscription slab at the Chain St / Plugat HaKotel corner (E06). **H**

Overhead
- Shed canopies on scroll brackets (P1), steel tie-bars across, hanging rails above the doors (A01). **H**
- Cables in bundles along the walls and across the street at 4-6 m; **flexible silver air ducts** in the vaults
  (E01, C05); strings of bare bulbs (D05, E02). **H**
- Wire-mesh grille on a steel frame over Chain St east of x ≈ 385 (E08). **H**

Ground and walls
- Round cast-iron manholes on the centreline, steel trench grates across the street (A06), raised stone thresholds
  (P1). **H**
- **Green municipal wheelie bins** (A06 at the CQR corner, E11 in the khan passage). **H**
- AC units and conduits on the upper walls (A01, A02, C05). **H**
- **Black steel stairs to the roofs** (D08, F20). **H**
- Roof promenade: black railings, globe lamps, benches, tall security fences (1.7). **H**

Vehicles and props (closed state)
- Blue hand cart on car wheels (A11), a red mini tractor and a steel skip container by the St John apse (H04),
  white plastic chairs and stools, crates. **M**

Vegetation
- **Lutheran guesthouse gardens**: raised planted beds with stone kerbs, a date palm, pepper trees, a jacaranda,
  pomegranates and roses on terraces behind a ~1.5 m stone retaining wall (G07, G08); OSM trees at
  (221.6,4.1), (234.3,6.0), (268.2,4.2), (278.0,6.6), (285.3,5.6), (299.1,9.1). Seen from the Redeemer tower as a
  patch of trees beyond David St (F15). **H** for the gardens, **M** for the level.
- Bougainvillea over St Mark St walls (Commons "Holy Land Pilgrimage 2017 P041/P042", not kept). **M**
- Weeds and capers in roof joints and on the Muristan gate (F08, B14). **H**
- Trees in the St John forecourt (OSM (185.5,36.1)) and in Maronite Convent St (OSM (160.2,-35.6), (160.3,-40.4)). **M**

---------------------------------------------------------------------------------------------------------------

## 5. TERRAIN

`street_z` (relative to the street at the Jaffa Gate node, datum 770.58 m asl) against the OS 1865 spot heights in
the sector (all within 0.6 m):

| place | OS 1865 | street_z | note |
|---|---|---|---|
| (174.7,3.8) BM, St Mark St foot | 763.1 m → -7.51 | -7.40 | |
| (192.2,-7.8) St Mark St | -3.09 | -3.19 | |
| (221.5,-14.4) below the Maronite stair | -4.31 | -4.17 | |
| (209.9,-32.8) Maronite convent level | +4.83 | +4.28 | |
| (222.2,7.4) David St south edge | -11.93 | -11.68 | |
| (254.2,-20.9) BM, St Mark St | -6.35 | -6.57 | |
| (282.4,11.6) David St | -14.37 | -14.28 | |
| (300.7,-13.1) St Mark St east | -12.54 | -12.52 | |
| (315.6,21.4) BM "David-st" | -15.29 | -15.64 | |
| (332.4,-11.9) Cardo/Habad | -15.29 | -15.09 | |
| (371.0,30.6) north of Chain St | -16.50 | -16.72 | |
| (388.7,7.2) BM Chain St | -17.63 | -17.75 | |
| (418.7,12.8) Chain St | -21.99 | -21.66 | |

Profiles along the streets (sampled from `street_z`):
- **David St**: -4.8 (x 155), -6.9 (165), -8.6 (175), -9.7 (183), -10.2 (193), -10.9 (203), -12.0 (213), -12.9 (223),
  -13.0 (233), -12.95 (243), -13.1 (253), -13.5 (263), -14.1 (273), -14.7 (283), -15.0 (293), -15.3 (303), -15.5
  (313), -15.9 (323), -16.1 (333). Steep (~17 %) from the s00 edge to x 175, 7-11 % from 175 to 233, flat 233-253,
  ~3 % from 253 to the crossroads. Photos agree: steps to x ≈ 237 (A02, A13, B03, B06), a ramp below (C01). The spec
  has step runs only for x 153-175 (the `DAVID` table) and none further down. **H**
- **Chain St**: -16.1 (346) to -16.0 (362) level under the vaults, then -16.9 (378), -18.9 (393), -21.1 (409),
  -22.2 (417): ~10 % east of x 378. The spec has 48 steps at x 370-418 (stairs.py). Not checked in photos. **L**
- **St Mark St**: -6.1 (x 177-193), -7.2 (209-238 level), -8.7 (269), -11.0 (284), -12.7 (300), -13.6 (308): the
  stepped part is x 269-308 (G03). The spec has 48 steps on 616359697 at x 230-304. St Mark St is **5.5-6 m above
  David St** between x 215 and 260 (the Lutheran terraces sit at this level). **H**
- **Maronite Convent St** (616359696): -7.3 at St Mark St (214,-3), -3.8 (209,-10), -0.3 (204,-16), +2.9 (202,-24),
  +5.1 (201,-31): **12.4 m in 33 m**. OSM says 32 steps (they would be 0.39 m risers); the spec (stairs.py) already
  builds ~90 treads there, which fits the survey. The survey spots at (221.5,-14.4) and (209.9,-32.8) confirm ~9 m
  between them, so the OSM step count is probably per flight or wrong. **M** (survey) / unverified (no stair photo).
- **Habad St** (north part): -15.6 (y 18), -14.9 (y -5), -13.1 (y -20), -11.6 (y -28), -9.1 (y -44); the spec builds 39
  steps at y -42..-9.
- **The crossroads** sits at -16.0..-16.2; the roof promenade above it at ≈ -9.5..-10 (6-7 m higher, **M**).
- **Raised levels**: shop thresholds 0.15-0.35 m (P1); the Lutheran garden terraces ~5.5-6 m above David St (at the
  St Mark level, G07, G08); the St John forecourt ~2 m below CQR (spec grounds); the Khan al-Sultan courtyard
  roughly at Chain St level (E10: the hall floor slopes gently up from the street, **L**).

---------------------------------------------------------------------------------------------------------------

## 6. Model checklist (prioritised: the 15 things that make the sector read as itself)

1. **Open David St again**: no infill on the centreline (f181, f180 incl. the cross wall at x 214-217, f190, f158);
   3.5-4.5 m wall to wall, north wall at the OSM faces, south wall ~1.5-2 m south of the centreline. (0.1, R1)
2. **South shop row x 215-310** as a one-storey vaulted row (~5.5-6 m above David St) with the Lutheran gardens on
   top at the St Mark level. (0.2, 1.2, R4)
3. **The closed-shop profile**: teal/pale-green panelled steel doors with hasps, plus round-headed teal arched
   doors with fanlights (south side x 245-265), dark green lattice gates in tall pointed arches (x 280-320), grey
   roll-downs and a few dark blue doors; raised thresholds 0.15-0.35 m. (1.2, 1.4)
4. **Shed canopies on scroll brackets** with a ~1 m sky slot on the open stretches x 152-177 and 192-268, tie-bars
   across, hanging ogee-framed boards. (1.2)
5. **Groin vault x ≈ 177-192** and the pointed arch at the CQR junction; St Mark St stair rising south under an
   arch. (1.3, R2)
6. **Covered lower stretch x ≈ 270-325**: masonry transverse arches with a painted corrugated barrel on scroll
   arches between them; ramped floor of dark setts. (1.4, R2)
7. **Steps on David St x ≈ 195-237** (risers 0.12-0.16, treads 1-3 m), a ramp below. (5, R5)
8. **The vaulted crossroads** with Lahhamin (whitewashed pointed barrel), the Cardo (cross vaults, lantern) and the JQ
   Rd north end (rough pointed barrel) opening off it; no open plaza. (1.5, R3, R9)
9. **The Galicia roof promenade** on top: paved deck, black railings, globe lamps, the plastered skylight dome,
   security fences, and the black steel stair up from the St Mark/Habad corner. (1.7, R3)
10. **Chain St**: groin-vaulted x 345-378 with air ducts and cables; open under a wire-mesh grille with green
    canopies x 385-420; the Plugat HaKotel stair and green gate. (1.6, R7)
11. **Church of St John the Baptist**: gold scale dome with gilt cross, bell gable over the round-arched portal,
    apse on the Aftimos lane, forecourt with lamp post. (2.1, R10)
12. **Souq roofscape**: barrel humps with skylight boxes (pitched corrugated caps), low white domes, dishes, water
    tanks, red-tile pyramid roof rooms; north row of David St 8-11 m. (1.7)
13. **Muristan gate passage**: groin vaults with benches, the eagle gate at the north end. (1.8, R6)
14. **Khan al-Sultan**: vaulted entrance hall from Chain St and the open two-storey courtyard (keep it free of
    infill). (1.6)
15. **St Mark St** quiet lane: pale ashlar, Maltese-cross keystone, round-arched doors, wall lamps, steps down east of
    x 269, the stair alleys; the Maronite belfry above Maronite Convent St. (1.9, 2.2)

Baseline renders of the current build (`renders/sectors/s05_souks/r0_baseline/`, photo left / render right in the
`cmp_*.jpg` sheets; cameras on the OSM centrelines, z above the local ground):
- `cmp_david_w.jpg`: B04 (237,16 → W) against the render from (222,13.2) → W. The model shows a plain slab plaza
  ending in a stone wall with a round-arched wooden door (infill f180 across the street at x 214-217); no shops,
  canopies, thresholds, signs or steps.
- `cmp_david_e.jpg`: A02 (202.7,11.7 → E, 2009, closed) against the render from (240,13.5) → E. The south side is an
  open slab area with an olive tree (the Lutheran garden at street level); the street is blocked again at x ≈ 261
  (f180); north walls carry a few residential doors and windows only.
- `cmp_david_e_w.jpg`: B06 (Muristan corner → W) against the render from (285,16.7) → W: a free-standing block on
  the centreline (f180, x 261-279), the open garden with trees to its left, wooden arched doors instead of the teal
  round-headed shop doors.
- `cmp_crossroads.jpg`: E01 (343,5, the vaulted Chain St start) against the render from (327.3,18.2) → E: an open
  court between tall plain walls with arched windows (the "Gagot Galizia" area kept open at street level); no
  vaults, shops or souq character. (The camera tilt is exaggerated because the look point falls on a roof.)
- `cmp_chain.jpg`: E07 (416,16, Chain St under the grille) against the render from (377.5,9.9) → E. The camera
  ended up ~8-10 m up (the ground lookup at that point hit a roof), so it is a roofscape view along Chain St: a
  narrow slot between flat pale roofs with many solar water heaters, black tanks, low white domes and one red-tile
  pyramid roof. Compared with F05/F11 the domes and tanks are right; missing are the barrel humps with skylight
  boxes over the covered streets, the satellite-dish clutter and the tall security fences; Chain St shows no vaults
  or grille.
- `aerial_ne.png` (from (200,-40), 35 m up, towards (290,15)): pale flat roof decks with parapets, low white domes,
  solar heaters, black tanks and a red-tile pyramid roof room read well. The main difference from the roof photos
  (F05, F07, F08, F11, F15) is fragmentation: the model shows many deep light wells and gaps between blocks, while the
  souq quarter is an almost continuous roof surface (vault humps, skylight boxes, walkways) broken only by the street
  slots and a few courtyards (khan, St John forecourt, Lutheran gardens).
- `aerial_e.png` (from (300,-30), 35 m up, towards (380,15)): the same roof vocabulary; in addition, **curved
  building walls** where infill pieces follow the round end of a street buffer (f149 around the end of the khan
  passage at ≈ (380-401, 22-43), f150 at (343-364, 36-50)); the old city has no curved street walls here. Keeping
  the khan courtyard open (`open_areas`) and opening the souq corridors (R1) removes most of them.
- `stmark_e.png` (from (261,-17.2) → E): a narrow canyon of plain ashlar walls with one green louvred window;
  plausible for St Mark St, but without the round-arched doors, wall lamps, steps (x 269-308, G03) and canopy
  brackets of the photos (G02, G03, D08).

Requests that need code or the spec owner (values and evidence; repeated in the structured result):
- **R1** infill / street corridors: `infill.py` skips layer < 0 highways. Treat pedestrian ways with layer -1 and
  no `tunnel=yes` as street corridors (David St 279685572; Jewish Quarter Rd 4710079), or force layer 0 for them as
  for `COVERED_SOUQS`; and give the at-grade parts of the tunnel-tagged Cardo (123231486, y -12..57) and link
  123245531 a corridor. Pieces on David St now: f181 (x 165-187, also over CQR 26492706 at y 11-20), f180 (x 196-279,
  wall across at x 214-217), f190 (x 304-322), f158 (x 333-342; also the JQ Rd y -2..19 and the Cardo y -30..7),
  f150 (JQ Rd y 37-46), f144 (Cardo y 26-57, s04). Evidence: render r0_baseline/david_vault_w; A02, B01-B07, C01,
  D03, D04. **Workaround without code** (profile `open_areas`, which `infill` keeps free): a 3.2 m corridor along the
  David St centreline x 160-342, ring [[174.8,11.0],[177.1,13.6],[193.0,14.6],[197.0,13.9],[211.7,14.7],
  [234.9,14.9],[268.4,17.6],[298.9,18.8],[315.5,20.0],[332.4,19.8],[342.5,19.0],[342.3,15.8],[332.3,16.6],
  [315.6,16.8],[299.1,15.6],[268.6,14.4],[235.0,11.7],[211.8,11.5],[196.8,10.7],[192.9,11.4],[178.6,10.5],
  [176.4,7.9],[160.1,6.6],[159.9,9.8]] (buffer 1.6 m; stays clear of the OSM north walls), plus similar strips on the
  JQ Rd north end (x ≈ 344, y -3..19) and the Cardo line (x ≈ 332, y -12..18). It reopens the street but does not
  vault it (R2) and does not build the south wall (R4). Note: the s04 profile's Christian Quarter St open area stops
  at y ≈ 12 and does not touch David St.
- **R2** covered segments: a way-id + x-range (or polygon) form of `covered_streets`, because covering whole ways
  would vault the Jaffa Gate stretch of David St. David St x 177-192: groin vaults, spring 2.8-3.0 m, crown 4.5-5 m
  (A01, A04). David St x 270-325: masonry transverse arches every 10-15 m plus a new roof type, a painted
  corrugated-sheet barrel on wrought-iron scroll arches, crown 5.5-6 m (C01, C02, C05).
- **R3** Gagot Galizia (655718796, `location=roof`): do not treat it as open ground; build the souq vaults at
  street level beneath it and a walkable roof deck at ≈ +6-7 m over x 322-357, y 6-37 with railings, globe lamps
  and the skylight dome; steps 1104187000 are a steel stair UP from (318.3,-5.7) to the deck at (321.8,6.3), not a
  downhill run (D08, F04, F05, F07).
- **R4** south street wall of David St x 215-310 (manual building, lowest priority; can go in the profile, but
  the terrace level needs terrain support): ring ≈ (215.5,11.2) (255,13.0) (268,14.0) (310,15.8) (310,9.8) (268,8.0)
  (255,7.0) (215.5,5.2), height ~5.5-6 m above David St, shops on the north face; the gardens 1393351630/290693096 as
  a level terrace at the St Mark St level (≈ -7.5 at x 215-260, falling to ≈ -11 at x 300) instead of the
  interpolated slope. Evidence B04, B06, B07, C01, G07, G08.
- **R5** steps on David St x ≈ 195-237 (A02, A13, B03, B06): extend the David St step runs (riser 0.12-0.16, treads
  1-3 m) beyond the `DAVID` table's x 175 end; a ramp (no steps) from x 237 to the crossroads (C01).
- **R6** Muristan gate passage: vault Muristan St 26492713 between y ≈ 17 and 41 (pointed groin vaults, ~5 m wide,
  crown ~5 m, benches; B13) and build the gate arch with the eagle relief at y ≈ 41-48 (B14, B15) (gate/landmark module).
- **R7** Chain St: vault x 345-378 (groin vaults, spring ~3 m, crown ~5 m; E01-E04); a new overhead feature, a steel
  frame with wire mesh at 5-6 m over x 385-420 (E07, E08).
- **R8** layer-1 `building=roof` features built as ground buildings: w1393297096 stands on the Jewish Quarter Rd
  centreline at y -42..-37 (blocks the street); also w1392856695 (Aftimos corner) and w1393297055. Build them as
  sabats/roofs over the street.
- **R9** the south ends of Suq al-Attarin (Cardo line x ≈ 332, y 18-48) and Suq al-Khawajat (way 4710079, y 17-48)
  and the at-grade Cardo market (y -12..18) and JQ Rd north end (y -3..17) are vaulted (D03, D04, D05, D06); the names
  in `COVERED_SOUQS` do not match these OSM ways, and covering the whole ways would vault s06 too (segment form, R2).
- **R10** Church of St John the Baptist (w166965387): gold scale dome (~6.5 m, top ~14-15 m above the forecourt) with
  gilt cross centred ≈ (200,43), bell gable on the west facade e1, apse at (208,43); needs a landmark builder
  (landmarks_city) or new facade/roof features (H02-H06).
- **R11** Maronite campanile on w290692945 (G11, G12): a square two-stage belfry with a pyramid cap; position on the
  footprint unknown (needs one more photo or the landmark owner's judgement).
- **R12** (low) the Maronite Convent St stair (616359696): OSM step_count 32 against 12.4 m of survey rise; the spec
  builds ~90 treads, consistent with the survey; keep, but check with a photo when one is found (section 5).
- **R13** w1550439740 (173.6,-38.9) overlaps the Maronite Convent steps 1005635992 and pedestrian area 1550439741
  (OSM overlap; probably a room over the passage) - low priority, no photo.

Suggested inputs for the profile / override pass (no code needed; for the next worker to check and write):
- `souq_streets`: "David Street" stays (1.0, 0.6) but canopies only on the open stretches; "Silsileh" (0.95, 0.15)
  (all shops; canopies only east of x 385, E07); "Saint Mark Street" (0.2, 0.1) (residential and hostels, shops only
  at the two ends, D08, A05); 26506011 Habad north (0.5, 0.2) (D08).
- `covered_streets`: "1020791459" (the Khan al-Sultan entrance hall, E10, E11; layer 1 without a tunnel tag, so it is
  not carved now).
- `open_areas`: Khan al-Sultan courtyard ≈ [[388,33],[401,33],[401,46],[389,46]] (E12, E13; now infill f149).
- `remove_buildings`: w1393297096 (building=roof, layer 1, standing on the Jewish Quarter Rd centreline at
  y -42..-37) and w1392856695 (building=roof, layer 1, half across the mouth of the Aftimos lane at (205,19)), if the
  spec owner cannot build them as sabats (R8).
- `manual_buildings`: the south shop row of David St (ring in R4).
- Overrides: w166965387 settings wall ashlar, tint ≈ [1.04,1.0,0.94] (clean pale stone, H02), domes 1; west facade
  e1 (at [192.85,40.4], faces W) photo-matched with the round-arched portal and windows (H02, H05). w290693095
  (Lutheran guesthouse): 3 storeys + gabled dormers, pale ashlar, arched top-floor windows with curved black
  balconies on the north (garden) face (G08). North row of David St x 270-311 (w1393364229 e0 at [279.8,18.6],
  w1393364228 e0 at [300.85,20.3]): pointed tall openings with lattice gates and no canopies (C01, C02). South side of
  the Muristan corner: round-headed teal doors (B06).

---------------------------------------------------------------------------------------------------------------

## Provenance

80 Commons photos in `data/photos_ref/s05_souks/` (1280 px thumbnails; `index.json` has title, page, author,
licence, date, lat/lon and local x/y where geotagged). Groups: A = David St x 152-215 (CQR junction, vaulted bays,
Aftimos corner, St Mark stair), B = David St x 215-270 and the Muristan passage/gate, C = the covered lower David St x 270-325,
D = the crossroads, the three souqs' south ends, the Cardo and JQ Rd north end, E = Chain St and Khan al-Sultan,
F = market roofs, the promenade and skyline views, G = St Mark St, Habad St, Maronite convent, Lutheran gardens,
H = Church of St John the Baptist. Keys have gaps where a candidate was dropped after review.
Most useful: A01/A02 and B14 (Deror avi 2009, CC BY-SA 3.0; A01/A02 taken at 7:30 a.m. with every shop closed);
A04/A05/A12/A13/B04/C02/E04/E07 (Ariel Palmon 2011 GPS walk, CC BY-SA 3.0); A06/B06/C01 (Zairon 2014, closed shops,
CC BY-SA 4.0); A03/B07/D01/E01 (Jorge Láscar 2012, closed, CC BY 2.0); D02/D03/D08 (eugene_o 2016, CC BY 2.0);
E05/E06/E11-E13/H06/F19 (Bukvoed 2021-24, CC BY 4.0); H02-H04 (Chris06 2019, CC BY-SA 4.0); F05/G01/G02/G08/G11/A11
(Djampa 2014-17, CC BY-SA 4.0).
Caveats on the `index.json` coordinates:
- B06 is tagged (275.9,24.0) but was taken at the David St / Muristan corner (≈268,16) looking W (the "MURISTAN RD."
  sign is on the right pier). C01 is tagged (296.6,27.9), 10 m north of David St; it was taken on David St at
  x ≈ 295-300 looking E (Othman ibn Affan Mosque sign on the left). C02 (278.9,24.8) is inside w1393364229; it is on
  David St at x ≈ 279.
- All five ProtoplasmaKid photos (B01, B02, B13 and two not kept) share one place geocode (223.0,13.4); B13 is the
  Muristan passage at x ≈ 269.
- A12/A13 share (207.1,12.7); D04/D05 share (341.6,3.2) (two photographers, same spot, consistent).
- F15 is tagged (301.5,139.2) near the Redeemer tower top it was taken from; F12 (316.3,28.3) is a roof position.
- E10 is tagged (391.9,24.6), consistent with the khan passage (way 1020791459). D06 (328.4,33.7) is plausible
  (Attarin corner).
- Files without GPS (A14, B10, B12, C03-C05, E11-E13, F-series, G07, G08, G11, G12, H02-H05) were placed by
  content (signs, landmarks, OSM).
Not kept but used for a fact (looked at): "Suq Aftimos
Jerusalem - view to the Church of John the Baptist" (grey dome 2013), "Holy Land Pilgrimage 2017 P041/P042" (St
Mark St bougainvillea, unplaced), "Views in October of 2019 ... 30" (plastered roof dome).
Renders: `renders/sectors/s05_souks/r0_baseline/` (current build, before any change by this pass); scratch scripts
in `build/spec_s05_souks/` (plan.py, widths.py, edges.py, frontage.py, commons.py, sheet.py).
No code was edited and git was not run.
