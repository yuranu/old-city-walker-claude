# North side of Omar Ibn el-Khattab Square — facade & street reference

Scope: facades facing the square from Jaffa Gate east to the head of David Street, plus paving and
street furniture. Local frame as in `hero_edges.md` (x east, y north, metres from the Jaffa Gate node).

**Edge numbers below are from the CURRENT `data/scene_spec.json` `buildings[].ring` (regenerated
2026-10-19 after the OSM footprint cleanup), not the older numbering in `hero_edges.md`.** Each facade
is given as `id / edge N (start->end, length, compass direction it faces)` so it can be re-matched if
rings change again.

Photo keys: `P:NNN` = `data/photos/NNN_*.jpg`; `R:NNN` = `data/photos_ref/square_north/NNN_*.jpg`
(index.json in that folder has title, page URL, author, licence, date). Dates matter: the square
changes (signs, shop fronts, the Tourist Info rebuild), so prefer the 2019+ evidence where they differ.
Confidence: **H** = seen clearly in 2+ photos / measured; **M** = one good photo or estimated from
scale; **L** = inferred / partly hidden.

Measuring: heights scaled from people (1.7 m), doors (2.2 m), traffic-sign discs (0.6 m) and OSM edge
lengths (Petra edge 0 = 24.4 m was the best ruler, R:012 is almost orthographic).

## West-to-east sequence along the north side (what a walker sees)

| x (m) | building / gap | facade(s) on the square |
|---|---|---|
| 4–16 | w1393747403 "Ramparts Walk" building (OSM calls it a kiosk) | edge 2 (SSE), edge 3 (ENE) |
| 0–20 | w290812408 (behind, NW of the Ramparts bldg; hotel) | edge 3 (SW) mostly hidden behind cypresses |
| 18–33 | w1393420835 Ministry of Tourism information office ("TOURIST INFO") | edge 2 (SSE, main), edge 1 (WSW), edge 3 (NE) |
| 29–37 | mouth of Latin Patriarchate Rd (runs NW) | w1393420836 edges 3–6 line its east side |
| 37–61 | w290812336 **New Imperial Hotel** | edge 3 (W), **edge 4 (S, main, 21.4 m)**, edge 5 (SE corner), edge 0 (E) |
| 61–68 | mouth of Greek Catholic Patriarchate Rd (runs N) | w1393420837 edge 8 behind on the W side |
| 68–80 | w1392903902 "two-arch building" (Franciscan bookshop / Karkash) | **edge 2 (S, 11.5 m)**, edge 1 (W), edge 3 (E) |
| 80–85 | alley / Tannour café recess (waste-disposal node at (81,22)) | — |
| 84–109 | w1393928801 **Petra Hotel** | **edge 0 (S, 24.4 m)**, edge 6 (W, above Tannour); hostel door at the SE corner (head of David St) |
| 106–111 | head of David Street (stairs down east) | — |
| — | w1393928800 | behind the Petra, not visible from the square |

## Which building is the Petra Hotel? — w1393928801 (H)

- OSM: w1393928801 has `addr:street=David Road`; the node "New Petra Hostel" (99.8, 18.1) and the
  viewpoint node "View of Hezekiah's Pool from Petra Hotel" (104.5, 23.6) both lie inside it.
- Photos in Commons "Category:Petra Hotel (Jerusalem)" (R:011, R:012, R:013, R:021, R:027–R:030, R:043)
  all show this 24.4 m south facade, the corner of David Street, and the hostel door
  "New PETRA Guest House" with house-number plate **1** at the head of David St (R:013).
- It is the 3-storey building with arched windows, small iron balconies, urns on piers and the
  "WELCOME TO THE OLD CITY" balcony fascia — not the two-arch building w1392903902 next to it.
- Heritage-listed (Commons descriptions). Its real height is ~12 m + parapet (urns ~14 m), **not
  18 m** — the current spec value is too high (see below).

---

## w1393928801 Petra Hotel — edge 0: (84.6,13.0)->(109.0,13.8), 24.4 m, faces 178° (main facade)

Best photos: R:012 (2021, frontal, used for all measurements), R:029 (2016 frontal telephoto),
R:011 (2021 from SW), R:043, R:041 (2015/18 from S), R:027/R:028 (from above), R:030 (welcome
balcony), R:010 (roof, aerial 2021), P:140, P:141, P:142 (2019), R:053/R:054 (2014 dawn, shops shut).

Overall
- 3 storeys (GF + 2) + open parapet. Ground 0 → GF top 3.85 m; 1F 3.85–8.0 m; 2F 8.0–11.8 m;
  cornice/coping top ~12.1 m; parapet piers to ~13.1 m; urn tops ~14.0–14.2 m. (M, R:012 scaled
  43 px/m from the 24.4 m width; cross-checked R:029)
- Rooftop room: white-rendered/stone room with **red clay-tile gable roof** (ridge parallel to the
  facade), set back ~4 m from the front, over the west ~45 % of the roof (x≈86–97); 3–4 small square
  windows on its south wall; eaves ~3.3 m, ridge ~4 m above the roof (ridge ≈ 16 m). (H, R:027,
  R:029, R:043, R:041, R:028, R:010)
- East half of the roof: rusty red steel lattice frame/pergola posts (~3 m), satellite dish (~1 m,
  at the E end), white solar water-heater tanks, potted plants, TV aerials. (H, R:029, R:010, R:028)
- Stone: cream-to-buff limestone ashlar, coursed (~0.35–0.45 m courses), strongly weathered: grey and
  brown vertical streaks below the cornice and every sill, caper/weed bushes growing out of the
  parapet and joints, darker grey patches. (H, R:012, R:028)
- End bays (W ~5.5 m and E ~6 m) are very shallow projecting pavilions (straight joints, slightly
  forward plane) — the twin windows sit in them. (M, R:012)

Bay layout (x measured from the W corner along edge 0; R:029/R:012)

| bay | x centre | 2F (8.0–11.8 m) | 1F (3.85–8.0 m) |
|---|---|---|---|
| W pavilion | 2.8 m | **twin** round-arched windows, shared balcony ~2.7 m | **twin** round-arched windows, own balcony ~3 m |
| 2 | 7.9 m | single round-arched French window, small balcony ~1.6 m | single round-arched window, **dentilled archivolt** |
| 3 | 11.4 m | single, small balcony | single, dentilled archivolt |
| 4 | 15.5 m | single, small balcony | single, dentilled archivolt |
| E pavilion | 21.0 m | **twin**, shared balcony ~3.3 m | **twin**, long balcony with "WELCOME TO THE OLD CITY" fascia |

- 1F: bays 2–4 share ONE long balcony (x≈6.7–18 m) carrying black perforated-mesh AC cages; the E
  pavilion balcony (x≈18–24 m) is a second long balcony at the same level. (H, R:012, R:029, R:011)
- Window details (H, R:012 crops):
  - singles ~1.1 m wide × 2.3 m (2F) / 2.1 m (1F) to the crown, semicircular heads, dark-brown/black
    steel glazing bars (4–6 panes + fanlight), set in a plain reveal;
  - 2F singles and all twins have a raised **drip-mould hood** following the arch, with short
    horizontal returns at springing level; twins have a double hood joined at the mullion and a small
    round oculus/rosette in the spandrel above the mullion;
  - 1F singles: archivolt decorated with **dentils / bead moulding** and projecting impost blocks;
  - **pairs of small white projecting stone tabs** (~0.15 × 0.45 m, vertical, like little corbels)
    flank each single window at springing height, plus odd ones between bays — very distinctive. (H)
- Balconies (H, R:012, R:011): slab = thin dark steel plate/channel ~0.12 m on curved wrought-iron
  S-brackets; depth ~0.6–0.7 m; railings black wrought iron ~1.0 m with scrollwork (2F singles have
  splayed/raked side panels so the balcony looks trapezoidal in plan); 1F long balconies have plain
  vertical-bar railings with a scroll frieze. White plastic chairs on several.
- "WELCOME TO THE OLD CITY": white capitals ~0.25 m on a dark grey steel fascia band ~0.35 m along the
  front of the E 1F balcony (x≈18–24 m, at the 1F floor ~4 m above ground), paint peeling. (H, R:030, R:012, P:142)
- E end, 2F level: projecting enclosed box of grey-green diamond-lattice metal screen
  (~1.4 w × 2.8 h × 0.8 d m, small sloping lid) on the SE corner. (H, R:012, R:029, R:011)
- Horizontal elements: thin projecting string course at 1F floor (~3.9 m) and 2F floor (~8.0 m)
  carrying the balcony brackets; simple projecting cornice/coping at ~11.8–12.1 m. (H)
- Parapet (H, R:012, R:028 close-up): **no solid parapet** — 6 square stone piers (~0.5 m square,
  ~1.0 m high, moulded caps) along the south front (two at the corners, others roughly over the bay
  divisions) each carrying a **white stone urn/finial** (~0.6–0.8 m, vase with knob; the SE pier had
  lost its urn by 2021); between piers a **black iron railing ~0.7–0.8 m** (plain vertical bars, top
  rail) plus thin taller steel posts (~1.5 m) for an awning/pergola.
- Services: black cables looping under every balcony and along string courses, black LED floodlights
  on short arms at 1F/2F, white PVC downpipe at the E end, AC units on balconies. (H)

Ground floor, W → E (R:012, R:011, P:141, P:140; 2019–2021 state)
- Continuous **flat galvanised steel canopy** along the whole facade at ~2.9–3.2 m, ~0.8–1.0 m deep,
  with a top rail, merchandise hooks and fluorescent tubes; scarves, keffiyehs, tallitot and rugs hang
  from it. (H)
- SW corner pier ~1 m with house-number plate **23** (white enamel, ~3 m up). (H, R:011)
- Shop 1 (x≈1–4.6 m): rectangular opening ~3.6 w × 3.0 h m under a segmental relieving arch;
  closed by **medium-grey painted steel folding doors** (8 tall leaves + small top panels, bolts),
  yellow hand-painted lettering (illegible) on the two centre leaves. (H, R:011)
- Pier ~0.8 m, then the money changer (x≈5.5–8.5 m): glazed door + boards: navy fascia
  "GMT | BEST MONEY CHANGER" (white/yellow), black board "money changer" (yellow), "MoneyGram"
  white sign, black vertical board **"authorized / best / money / changer / ATM"** (white + yellow
  letters, ~0.9 × 2.0 m, standing on the pavement), "ATM available" boards. (H, R:011, P:141, P:140)
- x≈9–17 m: open souvenir shops (textiles, ceramics, postcards); **beige/khaki retractable fabric
  awning with scalloped white-edged valance** ~5 m wide, ~1.2 m projection, at ~3 m (2016–2021);
  red and blue market umbrellas; blue ice-cream freezer, drinks fridge. (H, R:012, R:029, P:141)
- x≈18–23 m: big shop opening ~5.5 m wide closed by **light-grey multi-leaf steel doors** ~2.6 m.
  (H, R:012). 2014 dawn photos show all Petra shops shut with dark grey / grey-blue steel panel doors
  and a "BEST CHANGE" fascia (R:053, R:054).
- E of the big grey doors (x≈23–24.4 m and beyond): the hostel entrance and a lower neighbour with
  red-tile eaves and a barred window, under an old corrugated canopy (see the hostel door below).
  (M, R:012 right edge)

## w1393928801 Petra — edge 6: (83.3,23.2)->(84.6,13.0), 10.3 m, faces 263° (west, above Tannour)

- Greyer, rock-faced coursed masonry (rougher than the south front). (M, R:042, P:141)
- 2F: twin round-arched windows with a balcony; 1F: twin round-arched windows; small square window.
  Satellite dish and AC unit; dark sloping metal canopy over the Tannour recess at ~4.5 m. (M, R:042)
- SW corner: parapet pier with urn, toothed quoins on the corner, black railing continues;
  tall black steel rectangular frame on the roof behind. (M, R:042)
- Edge 5 (2.5 m, faces 352°) is a re-entrant jog behind the Tannour canopy. (L)

## Petra hostel entrance (SE corner, head of David St) and edge 1: (109.0,13.8)->(108.6,32.0), 18.3 m, faces 089°

- The hostel door ("1 David St") is at the SE corner where the square drops into David Street —
  most likely the east end of edge 0 (x≈105–108); edge 1 itself faces a ~1 m slot against
  w1393938083 and is not a street facade. (position L; door details H)
- Door details (H, R:013, 2021): plain rectangular opening ~1.5 w × 2.4 h m under a deep moulded stone
  lintel frame, reached by **3 limestone steps** (~0.17 m risers, full opening width); white sign
  board above the door, black frame: small red "NICE VIEW" (left) and "OLD CITY" (right) with a
  photo of the Petra treasury each side, centre "New" (black italic) over "Guest **PETRA** House"
  ("PETRA" big red sans, "Guest"/"House" black italic); white house-number plate **1** on the right
  jamb; inside a wooden reception counter, yellow Western Union "SEND & RECEIVE MONEY HERE"
  stickers; big white board leaning on the right jamb "A.T.M / MACHINE" with vertical black panels
  "ATM MACHINE" either side of red vertical "MONEY CHANGER" and a red arrow pointing left; green
  steel door further right; rusty corrugated canopy with S-hooks and a fluorescent tube above; a
  tangle of black/orange/green cables and a white downpipe on the stone; a faded white "DO NOT THROW
  … HERE" notice on the left.
- Neighbour to the east (w1393938083) is a white two-storey building with a dark grey **gabled
  metal roof**, round-arched windows and an oculus, seen at the end of the vista down David St.
  (H, P:142)

---

## w290812336 New Imperial Hotel — edge 4: (38.9,15.0)->(60.1,17.2), 21.4 m, faces 174° (main facade)

Best photos: R:005 (2021-07, frontal, measured), R:033 (2017 frontal), R:035 (2016 close),
R:025 (2016 from the Citadel, looking down on the centre bay), R:044 (2015 SE corner),
P:087 (2022, SW corner), R:008 (2021 W facade), R:036/R:037, R:053/R:054 (2014 dawn, shops shut).

Overall (OSM `building:levels=3`)
- GF + 2 upper storeys + balustraded roof terrace. GF 0–5.4 m (to top of the GF entablature);
  1F 5.4–10.3 m; 2F 10.3–14.5 m (top cornice); parapet piers to ~15.5–15.8 m; urn finials to
  ~16.5 m. (M, R:005 scaled ~50 px/m; crown/entablature ratio checked on R:033)
- Composition: **5 bays + a rounded (quarter-cylinder) corner bay at each end**; the centre bay is
  framed on every storey by **paired engaged round columns** (Tuscan-like, stacked storey by storey
  with an entablature between). (H, R:005, R:033, R:035)
- Stone: cream/beige limestone, heavily pitted ("honeycomb" erosion), grey patched repairs, dark
  streaks; looks the most worn facade on the square. (H)

Bay layout L→R (W → E), all floors (R:033, R:005, R:035)

| bay | GF | 1F | 2F |
|---|---|---|---|
| SW rounded corner | round-arched opening, green vertical "ATM" signs | round-arched window, small curved iron balcony | round-arched window, small curved iron balcony |
| 1 | segmental shop arch + canopy | rect French window, balcony | rect window, balcony |
| 2 | segmental shop arch + canopy | rect French window, balcony | rect window, balcony |
| centre | VERSAVEE passage between paired columns | **triple-arched-head window**, balcony; "IMPERIAL HOTEL" above | rect window, balcony (Greek flag) |
| 4 | segmental shop arch + canopy (St Michel grocery) | rect French window, balcony | rect window, balcony |
| 5 | segmental shop arch + canopy (Samara) | rect French window, balcony | rect window, balcony |
| SE rounded corner | round-arched window (shuttered) | round-arched window, curved balcony + AC | round-arched window with louvred shutters, curved balcony |

- **Every upper window on the south front has its own iron balcony** (5 per floor + the two curved
  corner balconies) — 14 balconies on this facade. (H)
- Upper windows: rectangular, ~1.4–1.6 m wide × 2.4–2.7 m, moulded eared architraves; above each a
  projecting **cornice hood** topped by a carved relief (C-scrolls/acanthus cartouche, ~1.3–1.5 m
  wide). 2F windows have louvred transoms and dark grey/brown roll-down shutters; 1F bays 4–5 have
  grey aluminium roll shutters. (H, R:035, R:033)
- Balconies: stone slab ~2.3 × 0.6 m, ~0.15 m thick, on 2 carved consoles; **black cast-iron
  railings ~1.0 m with lyre/vase-shaped baluster panels**; terracotta flower boxes on several; white
  split ACs on some 2F balconies. (H, R:025, R:035)
- Centre bay: 1F window has a head of **three small semicircular arches** inside a rectangular frame;
  above it **"IMPERIAL HOTEL"** in dark raised serif capitals (~0.3 m) on the frieze (below the 2F
  balcony); 2F centre door has a semicircular sunburst fanlight. (H, R:025, R:033, R:035)
- Horizontal: GF entablature + projecting cornice at ~5.0–5.4 m (balcony consoles sit on it);
  cornice under 2F balconies ~10 m; top frieze + strongly projecting moulded cornice ~14.5 m. (H)
- Roof: **parapet of square stone piers** (~0.5 m, ~0.9–1.0 m high) at the corners, flanking the
  centre bay and between bays, **stone urn finials** (~0.7 m) on the corner and centre piers;
  **black iron railing of plain vertical bars** between piers, an ornate scroll railing over the
  centre bay; plants and umbrellas of the roof terrace behind; swan-neck wall lanterns at the top
  corners. (H, R:005, R:044, R:033)
- Rooftop structures: none of note on the NIH itself (terrace furniture, a few TV aerials, thin
  posts); behind it the plain taller blocks w1393420836 / w1393420837 (4–5 storeys, flat windows,
  white louvred shutters, flat roofs with railings and a red-tile roof room further N) rise above its
  skyline on the north-east. (M, R:044, R:045, R:041)
- Black cables run along the cornices; festoon string lights (bulbs on a catenary) strung across the
  GF at ~3.5–4.5 m in 2016, blue garlands in 2017. (H, R:025, R:033)

Ground floor detail (H unless noted; R:005, R:025, R:035, R:033)
- Rhythm along edge 4 (W→E, approx. centres from the W end, M): SW curved corner 0–2.2 m · bay 1
  arch 3.6 m · bay 2 arch 7.0 m · centre passage 10.7 m (between the paired columns, ~4.2 m incl.
  columns) · bay 4 arch 14.4 m · bay 5 arch 17.8 m · SE curved corner 19.2–21.4 m. So the "five shop
  bays" are 4 arched shops + the flat-lintelled VERSAVEE passage in the middle; the curved corners
  carry a narrow arched opening each. Piers between arches ~0.8 m.
- Shop bays 1, 2, 4, 5: **segmental/elliptical arches ~2.7 m wide, crown ~4.1–4.2 m**, moulded
  archivolt, keystone carved with the **ΤΦ monogram** (Holy Sepulchre; the building belongs to the
  Greek Orthodox Patriarchate), plain ashlar piers with impost mouldings, 1 stone step.
- Arch head (tympanum above ~3.2 m) filled with a **dark iron grille** (vertical bars + small
  arches) over glazing.
- At the springing (~3.0–3.2 m): projecting **galvanised flat steel canopy** ~0.8–1.0 m deep,
  tubular frame with hooks, tie rods to the wall.
- Closure: **grey galvanised roll-down shutter** (horizontal slats, box under the canopy); open:
  brown varnished wooden glazed shopfronts. 2014 dawn: all shut with grey shutters (R:053/R:054).
- Bay 4: "St MICHEL GROCERY & CAFETERIA" small navy bracket sign (white letters), Coca-Cola fridge,
  red snack rack, blue Nestlé freezer, red Coca-Cola / white Evian umbrellas.
- Bay 5: "SAMARA RESTAURANT & COFFEE SHOP" navy bracket sign + white standing menu board.
- Centre: **VERSAVEE passage** (to the courtyard and the Tenth Legion column) — rectangular opening
  ~2.7 w × 3.5–4.0 h m, dark interior, 3 thin steel bollards inside, two small round in-ground
  uplights in front; flanked by paired engaged columns on tall square pedestals (~0.9 m);
  above: **white marble plaque** with Greek text "1884 · ΠΑΤΡΙΑΡΧΕΥΟΝΤΟΣ ΝΙΚΟΔΗΜΟΥ ΤΟΥ Α' ·
  ΔΑΠΑΝΗΣ ΑΡΧΙΜΑΝΔΡΙΤΟΥ ΕΥΘΥΜΙΟΥ …" with a roundel at each end, and below it **"VERSAVEE"** in
  dark capitals on the stone; hanging inside: orange-red sign "VERSAVEE BISTRO BAR & CAFE" (white
  letters); short flag poles from the plaque with Greek flag and red-cross-on-white flags; white
  café umbrellas in front. (H, R:025, R:035, R:033)
- SW corner GF: round-arched opening with green/white vertical "ATM" signs. (H, P:087)

## w290812336 NIH — edge 3: (36.8,22.3)->(38.9,15.0), 7.6 m, faces 254° (west, toward the gate)

- 2 bays: flat-headed windows in moulded frames; 2F windows with small iron balconies (AC units),
  1F windows with balconies/AC; **"IMPERIAL HOTEL"** dark raised capitals on the frieze between 1F
  and 2F across both bays (often hidden by flags). (H, R:008, P:087)
- GF: wide segmental arch with a dark iron grille head and a dark grey/black closure. (M, R:008)
- Two Israeli flags and a white "ISRAEL MINISTRY OF TOURISM" banner on poles projecting from the
  wall at 1F (belong to the Tourist Info). (H, R:008, P:087)
- SW rounded corner between edge 3 and edge 4: radius ~1.5–2 m, toothed (long/short) quoins on both
  sides, one round-arched window per floor with a small curved iron balcony at 1F and 2F. (H, P:087)

## w290812336 NIH — edge 5 (60.1,17.2)->(60.7,18.3), 1.2 m, faces 119° + edge 0 (60.7,18.3)->(59.9,24.6), 6.4 m, faces 083°

- Edge 5 is the SE rounded corner bay (same treatment as SW: arched windows, curved balconies, AC
  unit, louvred shutters on the 2F arched window). (H, R:044)
- Edge 0 (east, on Greek Catholic Patriarchate Rd): 1 window per floor (louvred dark shutters at 2F),
  roof railing continues. GF: **tall round-arched window with a radiating fan grille + vertical bars**
  on a ~0.9 m stone sill, flanked by **pale blue-grey panelled shutters**; terracotta planter;
  "SAMARA restaurant & coffee shop" sign at the corner; marble plaque; further N an arched door with
  blue-grey leaves. No-entry sign + yellow time plate on a pole at the corner. (H, R:040, R:044)

---

## w1392903902 two-arch building — edge 2: (68.8,14.2)->(80.2,15.0), 11.5 m, faces 176° (main facade)

Best photos: R:042 (2016, oblique from W, sharp), R:038 (2015, looking up), R:039 (2015 signs),
P:141, P:143 (2019), P:077 (2024), R:053/R:054 (2014 dawn, shut), R:044, R:046.

Massing (M — three independent estimates agree within ±1 m)
- **Front block**: one tall storey of two big arches; arch springing ~4.4 m, crown ~6.4 m, top of
  the front wall / parapet band ~8.3 m.
- **Set-back upper block**: 2 storeys set back ~1.5–2 m behind the front wall, plain ashlar, 4 windows
  per row with **white louvred shutters**, white AC unit; roof ~14 m; **white tubular railing**
  (V / diagonal infill) ~1 m on top; thin white flagpole ~4 m and a satellite dish. (H, R:038, P:141,
  R:043)
- A row of thin **white steel rods at 45°** (~1.2 m, ~1 m spacing) lean from the front parapet back to
  the set-back wall (old awning/pergola supports). (H, R:038, R:042)
- A white/cream board or screen stands on the front roof at the E end. (M, R:042, P:141)

Front block, L→R (W → E): W corner pier ~1.2 m · W arch ~4.0 m · centre pier ~1.3 m · E arch ~4.0 m ·
E pier ~1.0 m (sums to 11.5 m). (M)
- Stone: lighter, smoother cream ashlar than its neighbours; **rusticated, drafted-margin toothed
  quoins** at the W corner and as a vertical strip on the centre pier. (H, R:038, R:042)
- Arches: **semicircular**, moulded roll archivolt, carved foliate keystone, plain impost blocks. (H)
- Arch heads: **dark fan/sunburst iron grilles** — radial bars from a small semicircular hub with
  scroll ornament — over dark glazing; the fan fills the whole semicircle above the springing. (H)
- Under each fan, at springing level (~4.2 m): a **dark grey serpentine (wavy) sheet-metal canopy**
  ~4 m wide, ~1 m deep, over a dark grey fascia box; this wavy canopy is the building's signature.
  (H, R:042, R:038, P:141, P:143)
- Closures: E arch — **grey galvanised roll-down shutter** (shut in 2014 and 2024); W arch — honey
  wooden glazed shopfront with central round-windowed door (2016), dark-framed glazing (2024); both
  shut with grey roll-down shutters at dawn 2014. (H, R:042, P:077, R:054)
- Parapet band (~6.5–8.3 m): plain ashlar with a **carved coat-of-arms panel** centred over the centre
  pier (shield under an ecclesiastical hat with tassels — Franciscan/Custody arms), simple coping. (H,
  R:038, R:042)
- Signs (2015–2016): W pier — white square sign with a "C|C" logo (Christian Information Centre) on a
  black bracket at ~3 m; on the W corner pole cluster: "FRANCISCAN BOOKSHOP" (cream board, black serif),
  "KARKASH Jewlery & Souvenirs" (cream board, purple serif), "coffee / COFFEE SHOP" with a cup icon
  (red). Small hanging "KARKASH" sign on the centre pier. Postcard spinners, planters, textile racks in
  front. (H, R:039, R:042, P:141)

## w1392903902 — edge 1: (62.7,42.1)->(68.8,14.2), 28.5 m, faces 258° (west, Greek Catholic Patriarchate Rd)

Only the south ~6 m is seen from the square.
- Darker rock-faced masonry; narrow **round-arched doorway with a blue-grey iron bar gate**
  (~1.0 × 2.6 m, scroll head). (H, R:039, R:040)
- **Ceramic tile street sign** (white tiles, brown border, ~0.6 × 0.7 m, at ~2.5 m) left of a downpipe:
  "רח' הפטריארכיה היוונית הקתולית / طريق دير الروم الكاثوليك / GREEK CATHOLIC PATRIARCHATE St." (H, R:039)
- Grey pole at the corner: no-motorcycles + no-tractors discs and a yellow plate
  "מ- 10:00 / עד 17:00" (H, R:042); white horizontal pipe bracket at ~4.5 m. (M)
- Grey steel door with a "Soldiers" poster further up the street. (M, R:040)

## w1392903902 — edge 3: (80.2,15.0)->(76.6,30.3), 15.8 m, faces 077° (east, Tannour alley)

- Mostly hidden; AC units and a red pipe on the E return of the front block. (L, R:042)
- The 4.4 m gap between this building and the Petra's W face is the **Tannour** café: set back, dark
  metal canopy at ~4.5 m with a white lace-like fretwork valance (star cut-outs), "TANNOUR" sign and
  food-photo panels, wicker bistro chairs, blue extractor fan, water tank above. (H, P:077, P:141,
  R:011)

---

## w1393420835 Ministry of Tourism information office — edge 2: (21.8,8.0)->(33.0,13.2), 12.3 m, faces 155° (main)

Best photos: P:099 (2022), P:087 (2022), R:008 (2021), R:016 (2021 from E, above), R:056 (2017
from above), R:058 (2015 snow), P:053 (2024 through the gate).

**The facade was rebuilt/re-faced between 2017 and 2022**: the 2015 and 2017 photos (R:058, R:056)
show two tall narrow round-arched windows over a round-arched door, an "INFORMATION CENTER" bracket
sign and a stepped landing on this face; the 2022 photos show the layout below in new, clean
stone. Model the 2021+ state. (M)

- Two parts (H, P:099, P:087, R:008):
  - **W part (~6.5 m)**: two storeys high, **~8–9 m** (taller than the spec's 5.5 m). Smooth bright
    cream new ashlar with drafted edges. Upper: one **big round-arched window** ~1.8 × 3.8 m, dark grey
    steel grid (2 × 5 panes), deep reveal. GF: wide **segmental-arched glazed shopfront** ~3.4 m wide,
    ~2.8 m high, aluminium frames, thin stone voussoir arch; string course/ledge at ~3.1 m; row of
    small projecting corbel blocks under the coping. Blue sign "i / מידע לתייר / TOURIST INFO /
    معلومات سياحية" (~0.6 × 0.9 m) on a black bracket at ~3 m, plus a small blue square "i" plate at
    ~2 m. (H, P:099, P:087)
  - **E part (~6 m, wrapping onto edge 3)**: ~5.5 m in all (matches the OSM 1 level / 5.5 m) — a
    plain smooth-stone lower wall ~2.8 m with a dark map board "Jerusalem: The Old City"
    (~1.2 × 1.6 m, at ~1–2.6 m; OSM board node (31.6,12.5) facing 150°) and a small street-name
    plaque, and above it a **white-framed glazed upper level** (grid of ~0.8–1 m panes, ~2.5 m tall)
    topped by a row of **flower boxes** (red/yellow flowers) at ~5.5 m; two Israeli flags and a white
    "ISRAEL MINISTRY OF TOURISM" banner on poles at its NE corner, in front of the NIH west facade.
    (M — glazed level clear in P:087 and R:008, its height relative to the stone base L)
- Stone pier with a **pyramidal cap** and a black iron fence at the W end (between this building and
  the Ramparts building), 3 stone steps / landing in front; a very tall thin **cypress** (~15–18 m)
  behind the fence is a landmark seen from the whole square. (H, P:099, R:056, R:058, R:054)

## w1393420835 — edge 1: (18.5,13.6)->(21.8,8.0), 6.5 m, faces 240° (toward the gate)

- Upper: tall round-arched window; GF: round-arched door with dark leaves; 2017 sign "INFORMATION
  CENTER / i / מרכז מידע לתייר" (white with blue i) on a black bracket; stone stair/landing with the
  pyramid-capped pier and handrails in front. (M, R:056, R:058)

## w1393420835 — edge 3: (33.0,13.2)->(28.7,19.0), 7.3 m, faces 054° (Latin Patriarchate Rd mouth)

- Low ~5.5 m block: stone base, white-framed glazed upper level, flower boxes, flags (see E part above). (M, R:016, P:087)

---

## w1393747403 "Ramparts Walk" building — edges 2: (10.9,4.2)->(15.6,6.0), 5.0 m, 159° and 3: (15.6,6.0)->(13.1,11.0), 5.6 m, 063°

Best photos: P:063 (2024), P:099 (2022), P:053 (2024 through the gate), R:056 (2017), R:058 (2015).

- **Not a kiosk**: a 2-storey stone block, **~9.5 m** to the roof (GF ~4.5 m, upper ~4.5 m, parapet),
  with a galvanised tube railing ~1 m on the roof. Spec 4.5 m is far too low. (M, P:063 scaled from
  the 2.5 m counter opening; P:099)
- In the photos its south face starts right at the gate tower's north corner (OSM footprint sits
  ~4–5 m NE of the tower); the narrow arched doorway between is the way to the rampart stairs
  (OSM steps way 45081547). (M)
- Stone: rough-dressed yellowish ashlar (older-looking than the Tourist Info). (H)
- Upper floor: **tall narrow windows** ~1.0 × 2.8 m with deep reveals — 2 on edge 2, 3 on edge 3;
  since ~2022 each holds a vertical **blue banner** ("כניסה / Entrance" with a big white down-arrow;
  "THE RAMPARTS WALK" with costumed figures). (H, P:063, P:099, P:053)
- GF edge 2: ticket counter (rectangular opening, wooden counter) under a **red curved fabric
  awning** printed "טיילת החומות / ممشى الأسوار / THE RAMPARTS WALK" with figure silhouettes; narrow
  round-arched dark doorway to its left; free-standing blue sign "Entrance 9:00–17:00". (H, P:063)
- GF edge 3 / gate side: hanging bracket signs "טיילת החומות / The Ramparts Walk / ممشى الأسوار"
  (purple in 2017–2022, navy in 2024), "TICKET OFFICE" (navy, white), "INFORMATION / DAILY TOURS",
  "CHANGE" (blue); souvenir racks, hats; a "Kiosk" coffee A-board at the gate exit; CCTV cameras.
  (H, R:056, P:053, P:089)

## w290812408 (hotel) — edge 3: (10.0,26.3)->(19.5,14.0), 15.6 m, faces 232°; edges 1–2 behind

- Faces the stair/wall area NW of the gate; from the square it is hidden behind the Ramparts
  building, the Tourist Info and the cypresses. Visible bits: 3-storey plain ashlar with flat-headed
  windows, an iron balcony with laundry, AC units, flat roof with railing. (L, P:099, R:056, P:053)
- Edge 4 (151°) is a party wall against the Tourist Info; edge 5 (051°) lines Latin Patriarchate Rd
  (tall plain ashlar, flat windows, "Rossini's" red hanging sign further up). (L, P:056)

## w1393420836 — edges 3–4: (22.0,35.9)->(32.0,23.0), 16.3 m, faces 229–233°; edges 5–6 south returns

- Lines the east side of Latin Patriarchate Rd behind the NIH; tall (4–5 storeys) plain ashlar with
  flat rectangular windows and small iron balconies; only its south end (x≈32–37, edges 5–6) shows from
  the square, next to the NIH west facade. Edge 6 (164°) is otherwise a party wall behind the NIH.
  (L, R:008, P:056)

## w1393420837 — edges 2–7 (short faces at y≈26.5–29.5) and edge 8: (60.2,29.5)->(57.5,47.6), 18.3 m, 082°

- Entirely behind the NIH; its edge 8 lines the west side of Greek Catholic Patriarchate Rd north of
  the NIH (arched doors with blue-grey leaves, upper windows with balconies). Not seen from the
  square except looking up that street. (L, R:040)

## w1393928800 — behind the Petra (edges 2–4 face a courtyard south of it)

- Not visible from the square; only its roof shows from the Citadel / rooftops. Model as plain
  massing below the Petra's skyline. (M, R:010, P:022)

---

## Heights: corrections to the current spec (`pipeline/make_spec.py` HEIGHTS)

| building | spec top | observed | note |
|---|---|---|---|
| w1393928801 Petra | 18.0 | wall/coping **12.1**, piers 13.1, urns ~14.2, tiled rooftop room ridge ~16 (W half only) | M–H, R:012 measured |
| w290812336 NIH | 17.5 | top cornice **14.5**, parapet piers ~15.6, urns ~16.5 | M, R:005 |
| w1392903902 | 15.0 | front block (along edge 2, ~2 m deep) **8.3**; set-back block **~14** + 1 m white railing | M, 3 estimates |
| w1393420835 Tourist Info | 5.5 | W part (~6.5 m of edge 2 + edge 1) **~8.5**; E part (rest of edge 2 + edge 3) ~5.5 incl. glazed upper level | M |
| w1393747403 Ramparts bldg | 4.5 | **~9.5** (2 storeys) + 1 m tube railing | M |

Storey heights for facade generation: NIH GF 5.4 / 1F 4.9 / 2F 4.2 m; Petra GF 3.85 / 1F 4.15 /
2F 3.8 m; two-arch front block one 8.3 m storey (arch springing 4.4, crown 6.4).

---

## Square paving, road and street furniture

Paving (H unless noted)
- **Plaza and pavements**: large rectangular limestone slabs, cream/buff to warm grey, lightly
  bush-hammered, ~0.4–0.6 m wide × 0.6–1.2 m long, laid in irregular running-bond rows (no regular
  grid); scattered **paler, almost white replacement slabs** give a patchwork look, especially on the
  north pavement in front of the NIH and Petra; joints dark, worn smooth and darker in the main
  walking lines. (P:032, P:099, R:028, R:025, P:142)
- No decorative patterned bands; the only "pattern" is lines of **long kerb/gutter slabs** and the
  frequent **square recessed access covers** (steel tray infilled with the same stone, ~0.6–0.8 m) and
  small cast-iron manhole lids; linear slot drains across the road at the gate. (P:032, R:016, R:028)
- **Road** (Armenian Patriarchate Rd / Omar Ibn el-Khattab Sq., OSM way 265414845: enters from the
  gate area at ~(21,-10), runs east along the SOUTH side of the square at y≈0–8 to (82,8), then turns
  SE down past the Citadel at (96,3)): small grey-brown stone **setts ~0.10 × 0.20 m**, rough split
  faces, laid in rows across the carriageway (fanning on the curves), with a slightly dished centre
  line; ~6–7 m wide. (R:045, P:140, R:028, R:016)
- **Kerbs**: on the north (shop) side the kerb is almost flush — a 3–5 cm drop at a line of long
  smooth limestone kerb slabs (~0.3 m wide) — so the north plaza (y≈8–18) reads as one paved surface
  with the road; on the south (Citadel) side a raised pavement with a ~0.12–0.15 m rounded limestone
  kerb that curves round the moat corner. (R:045, P:140, R:028)

Furniture
- **Lamp posts**: dark anthracite **square-section steel poles** with a flat rectangular LED head
  (~0.8 × 0.25 m) on a short horizontal arm — an inverted "L"; tall ones ~9–10 m (some with a second,
  lower head at ~6 m), short ones ~5–6 m; usually **grouped in twos or threes of different heights**.
  Seen: cluster at the gate exit (~(8–12, 0–4)), along the north edge of the road in front of the
  Tourist Info and NIH (~x 40, 47, 55), in front of the two-arch building (~x 70) and the Petra
  (~x 90–95). Pole number stencils "181 101 1", "181 201 2". (H, P:063, P:099, R:016, R:033, R:054,
  P:033)
- **Benches**: backless; a limestone slab ~1.6–2.0 × 0.45 × 0.15 m on two black steel rectangular
  frame legs, seat ~0.45 m; set in loose groups of 2–4 (some at right angles) in the plaza between the
  Tourist Info / NIH and the road, and a row along the road edge south of the Tourist Info.
  OSM bench node (22.2, 2.1): white stone, 4 seats. (H, P:099, R:025, R:058, R:056)
- **Litter bins**: dark grey/black steel cylinders ~0.5 m Ø × 0.9–1.0 m with slotted sides and a
  lid, next to benches and poles (~4–5 on this side). (H, R:025, P:032, R:016, R:022)
- **Wayfinding totems**: slim black/dark-grey monoliths ~0.5 × 0.2 × 2.2 m with map panels — one at
  the gate exit, one or two in the plaza in front of the NIH. (H, R:056, R:016, R:022, P:032)
- **Bollards**: square limestone bollards ~0.35 m × 0.65 m with chamfered tops around the gate plaza
  (P:064, P:099); black steel cylindrical bollards ~0.9 m at ~1.5–2 m spacing along the Citadel-side
  road edge (P:064, R:028, R:031); 3 thin steel bollards inside the Versavee passage (R:025).
- **Railings**: black steel railing along the Citadel moat (south); galvanised handrails on the
  Tourist Info steps; galvanised crowd barriers on castors stacked against the gate tower's NE face.
  (H, P:063, P:064, R:056)
- **Trees**: none on the square itself; one very tall thin **cypress** (~15–18 m) rises behind the
  Tourist Info / Ramparts building and is visible from everywhere; potted shrubs at shop doors. (H)
- Traffic signs on grey poles at the street corners (no entry, no motorcycles/tractors, yellow time
  plates "10:00–17:00"); blue taxi/parking signs along the Citadel wall. (H, R:042, R:044, R:022)
- Festoon string lights across the north plaza in front of the NIH (2016), blue garlands (2017). (M)

Typical clutter (for a "shops closed" scene)
- Shut shops: grey galvanised roll-down shutters (NIH, two-arch bldg) or grey painted multi-leaf steel
  doors with bolts and hand-painted yellow numbers/letters (Petra). (H, R:053, R:054, R:011)
- Left outside: stacked cardboard boxes, plastic crates, folded postcard spinners and racks chained
  to the canopy posts, white plastic chairs, drinks fridges / ice-cream freezers under covers,
  closed market umbrellas, A-boards. (M, R:054, R:025, R:012)
- Vehicles/props: municipal **mini tractor (green) with a yellow tipping trailer** (R:031, R:054),
  green wooden **hand cart** with blue and red panels on two bicycle wheels (R:032), ka'ak bread cart
  (P:063), white taxis (Mercedes Vito vans, Skoda Octavia) parked along the Citadel wall, the yellow
  and green **tourist road train** (R:028, P:033, R:049).

---

## Sign texts on the north side (position · text · colours)

| where | text | style | photos |
|---|---|---|---|
| Ramparts bldg awning, edge 2 GF | "טיילת החומות / ممشى الأسوار / THE RAMPARTS WALK" + silhouettes | red curved fabric awning, white text | P:063 |
| Ramparts bldg upper windows | "כניסה / Entrance" + big ↓ ; "טיילת החומות / THE RAMPARTS WALK" + costumed figures | tall blue banners | P:063, P:099 |
| Ramparts bldg, gate side | "TICKET OFFICE"; "טיילת החומות / The Ramparts Walk / ممشى الأسوار"; "CHANGE" | navy / purple bracket boards, white text | R:056, P:053 |
| Tourist Info edge 2, W part | "i · מידע לתייר · TOURIST INFO · معلومات سياحية" (Israel Ministry of Tourism logo) | blue panel on black bracket, ~3 m up | P:099, P:087 |
| Tourist Info roof flags | "ISRAEL / MINISTRY OF TOURISM" (+ Hebrew) | white banner, 2 Israeli flags | R:008, P:087 |
| NIH W frieze & S centre frieze | "IMPERIAL HOTEL" | dark raised serif caps ~0.3 m | R:025, R:033, P:087 |
| NIH centre GF | marble plaque "1884 ΠΑΤΡΙΑΡΧΕΥΟΝΤΟΣ ΝΙΚΟΔΗΜΟΥ ΤΟΥ Α' … ΕΥΘΥΜΙΟΥ …" ; "VERSAVEE" ; "VERSAVEE BISTRO BAR & CAFE" | white marble, black Greek; dark caps on stone; orange-red hanging board | R:025, R:035 |
| NIH bay 4 / bay 5 | "St MICHEL GROCERY & CAFETERIA" ; "SAMARA RESTAURANT & COFFEE SHOP" | small navy bracket signs, white text | R:005, R:044, R:040 |
| NIH SW corner | "ATM" (vertical) | green/white | P:087 |
| Greek Catholic Patriarchate Rd corner | "רח' הפטריארכיה היוונית הקתולית / طريق دير الروم الكاثوليك / GREEK CATHOLIC PATRIARCHATE St." | ceramic tile plaque, brown border | R:039 |
| two-arch bldg | "FRANCISCAN BOOKSHOP"; "KARKASH Jewlery & Souvenirs"; "COFFEE SHOP"; C\|C logo sign | cream boards (black / purple serif), red; white square on black bracket | R:039, R:042 |
| Tannour recess | "TANNOUR" + food photos | dark canopy, white fretwork valance | P:077 |
| Petra SW pier | house no. "23" | white enamel plate | R:011 |
| Petra GF | "GMT · BEST MONEY CHANGER"; "money changer"; "MoneyGram"; "authorized / best / money / changer / ATM" | navy fascia; black boards with yellow/white text | R:011, P:140 |
| Petra E 1F balcony | "WELCOME TO THE OLD CITY" | white caps on dark grey steel fascia | R:030, R:012 |
| Petra hostel door (edge 1) | "NICE VIEW · New · OLD CITY · Guest PETRA House"; "A.T.M MACHINE / MONEY CHANGER"; house no. "1" | white light box, black + red; white board red/black | R:013, R:057 |

---

## Model checklist (prioritised: the 15 details that make this side recognisable)

1. **NIH south front (w290812336 edge 4)**: 5 bays + quarter-round corner bays, paired engaged
   columns framing the centre bay on all floors, ~14.5 m cornice. (H)
2. **NIH iron balconies on every upper window** (10 on the five bays + 4 curved corner balconies = 14 on the south front), stone slabs on
   consoles, black cast-iron lyre-pattern railings, with carved scroll reliefs over the windows. (H)
3. **NIH roofline**: stone piers with urn finials and black iron railing between (ornate over the
   centre). Same pier-urn-railing motif on the Petra: it ties the square together. (H)
4. **NIH GF arcade**: four segmental shop arches with dark grilles in the heads, flat galvanised
   canopies at ~3.1 m and grey roll-down shutters; central VERSAVEE passage with marble plaque. (H)
5. **"IMPERIAL HOTEL"** letters on the centre frieze (S) and on the W facade; triple-arched centre
   window. (H)
6. **Petra (w1393928801 edge 0)**: 3 storeys of round-arched windows — twin windows in the end
   pavilions, singles between — each with small black iron balconies on S-brackets, and the
   dentilled 1F archivolts with little white stone tabs. ~12 m, not 18 m. (H)
7. **Petra red-tile gable rooftop room** over the west half + steel frames/dish on the east half:
   the skyline marker at the head of David St. (H)
8. **Petra GF**: one continuous galvanised canopy with hanging textiles; grey steel folding doors;
   money-changer boards; "WELCOME TO THE OLD CITY" balcony fascia. (H)
9. **Two-arch building (w1392903902 edge 2)**: two big semicircular arches with **sunburst iron
   fan grilles** and **dark wavy canopies**, rusticated quoins, coat of arms in the parapet, set-back
   upper block with white shutters and a white tube railing. (H)
10. **Mixed heights**: two-arch front block (~8 m) low between the NIH (~15.5 m) and the Petra
    (~12 m + rooftop room); Tourist Info ~8.5/5.5 m; Ramparts building ~9.5 m. (M)
11. **Tourist Info (w1393420835 edge 2)**: new smooth stone, big round-arched window over a
    segmental glazed shopfront, blue "TOURIST INFO" bracket sign, the low glazed E part with flowers
    and Israeli flags. (H)
12. **Ramparts Walk building (w1393747403 edges 2–3)** by the gate: red awning and tall blue banners. (H)
13. **Paving**: big irregular cream limestone slabs with white patches on the plaza; small grey
    setts on the road along the south side; almost no kerb on the north side. (H)
14. **Street furniture**: clusters of tall anthracite inverted-L LED poles, backless stone benches on
    black legs, dark slotted bins, black wayfinding totems; the tall cypress behind the Tourist
    Info. (H)
15. **Weathering & clutter**: pitted/streaked stone (NIH worst), black cables along cornices and
    balconies, ACs and dishes, plants growing out of parapets; for closed shops grey shutters/doors
    with crates, covered fridges, a hand cart and the green municipal tractor. (H/M)

---

Provenance: 58 Commons photos downloaded for this note to `data/photos_ref/square_north/`
(1280 px thumbnails; `index.json` has title, page URL, author, licence, date, lat/lon where
geotagged). Most useful: R:005 (NIH frontal, Bukvoed 2021, CC BY 4.0), R:012/R:011/R:013 (Petra,
2021, CC BY 4.0), R:025/R:027–R:029 (2015–16 from the Citadel, CC BY-SA 4.0), R:033/R:035 (NIH,
2016–17), R:042 (two-arch building 2016, GFDL), R:053/R:054 (2014 dawn, shops shut).
