"""Turn OSM footprints + hand-curated knowledge into a scene spec for Blender.

Reads data/osm_local.json, writes data/scene_spec.json. All 2D decisions happen here (shapely),
Blender only builds what the spec lists:
  * footprints cleaned, overlaps resolved by priority (no coplanar walls/roofs anywhere)
  * detail tiers: hero (gate + square: full facade dressing), mid (rest of the PoC), context
  * ground as region polygons clipped exactly to buildings/steps: street, road (-15 cm, kerbs),
    moat (-5 m), citadel courtyard (+1 m)
  * facades (facades.py + hero.py overrides), street dressing and clutter (dressing.py)

    .venv/bin/python pipeline/make_spec.py
"""
import functools
import os
import re
import json
import math
import random
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

import dressing
import facades
import hero
import infill
import roofscape
import stairs
from geo import LineString, Point, Polygon, ccw, clean, edge_frame, poly_json, polys_of, unary_union
import shapely
from shapely import STRtree, clip_by_rect, constrained_delaunay_triangles, prepare
from shapely.geometry import box

try:                                       # city-wide street-level terrain (pipeline/terrain_street.py)
    import terrain_street as _terrain
    if not (ROOT / "data/terrain_street.json").exists():
        _terrain = None
except Exception:                          # noqa: BLE001
    _terrain = None

POC = (-30, -75, 160, 60)
CONTEXT = (-350, -520, 1010, 860)   # whole walled city + a ring of context (west part from osm_west.osm)
_OC = json.loads((ROOT / "data/oldcity_polygon.json").read_text()) if (ROOT / "data/oldcity_polygon.json").exists() else None
CITY = Polygon(_OC["ring"]) if _OC else box(*POC)          # inside the walls -> mid tier (rule-based facades)
HARAM = Polygon(_OC["haram"]) if _OC and "haram" in _OC else Polygon()
HERO_ZONE = Polygon([(-45, -32), (100, -32), (100, -42), (152, -42), (152, 32), (102, 32), (102, 48), (-45, 48)])

# Heights in metres above local ground, from Commons photos (022, 010, 019/020, 024, 027 ...)
# and OSM building:levels where present. Storey ~4.2 m in these 19th c. stone buildings.
HEIGHTS = {
    "w290812336": 17.5,   # New Imperial Hotel: ground + 3 floors + balustrade (photo 022, 019)
    "w290812408": 16.0,   # west wing of the Imperial block, facing the gate
    "w1393420836": 16.5,  # Imperial block, rear
    "w1393420837": 14.0,
    "w1392903902": 15.0,
    "w1393928801": 18.0,  # corner of David St: tallest on the square
    "w1393928800": 13.0,
    "w1392903903": 12.0,
    "w290812333": 12.0,
    "w1553088734": 9.0,
    "w290812409": 10.0,
    "w1393420835": 5.5,   # Ministry of Tourism information office, 1 level (OSM)
    "w1393747403": 4.5,   # kiosk just inside the gate
    "w126781854": 11.0,   # Swedish Christian Study Centre: arcade + 1 floor (OSM levels=2, photo 022)
    "w1549766140": 8.0,
    "w126782745": 11.5,   # Christian Information Centre (photo 022, right)
    "w290692953": 11.0,
    "w1393938082": 10.0,
    "w1393938083": 10.5,
    "w1393938081": 9.0,
    "w126783156": 10.0,   # Christ Church Guest House, hipped tile roof (OSM roof:shape)
    "w290690288": 8.0,
    "w1394456869": 8.0,
    "w1392276721": 5.0,   # structure in the citadel courtyard
    "r3864551": 12.0,
}
SKIP = {"w1393445770"}    # 15 m2 sliver tagged layer=1 (a bridge room)
# Buildings missing from OSM but present in photographs. They take whatever space is left after the
# OSM footprints (lowest priority), so they only fill gaps.
MANUAL_BUILDINGS = [
    {"id": "m_david_s1", "ring": [(124.3, 8.75), (124.5, -3.2), (131.1, -2.2), (130.9, 8.4)], "height": 9.0,
     "why": "continuous shopfronts on the south side of David St at x 124-131 (citadel_east.md C1; photos C01, C04, C05)"},
]
# Herod's Gate is not a building in OSM: the tower of wall way 137726904 (vertices 50-53), extended to
# the curtain's inner face (gates.md); modelled by blender/landmarks_gates.py
MANUAL_BUILDINGS.append({"id": "m_herods_gate", "ring": [(577.0, 697.3), (587.7, 700.8), (585.5, 709.0), (574.7, 706.1)],
                         "height": 15.2, "shops": False, "name": "Herod's Gate",
                         "why": "gate tower on the north wall (landmarks_gates.HEROD_RECORD)"})
# buildings whose centroid lies on the wall line, outside every sector: force their sector (tier mid)
FORCE_SECTOR = {"w1393450805": "s03_christian_w"}           # New Gate (landmarks_gates)
# gate passages: OSM door points (outer, inner); the passage floor runs between the street levels
# sampled 1 m outside each door, so the paving meets it without a step
GATE_DOORS = {"w616186088": [(265.8, 558.2), (275.4, 551.8)], "w288395731": [(893.6, 468.0), (882.4, 466.3)],
              "m_herods_gate": [(580.1, 707.6), (582.3, 699.0)], "w290671706": [(198.4, -418.2), (210.7, -415.7)]}


# ground the landmark builders replace: no ground mesh here (Wilson's Arch hall under Chain Street,
# whose roof is the walking surface; landmarks_haram.WILSON_HALL)
GROUND_HOLES = [Polygon([(621.91, 30.53), (646.06, 35.24), (640.68, 62.55), (639.28, 62.27), (626.48, 59.77),
                         (629.03, 46.85), (619.07, 44.91)])]
# sunken courts: paving at street level + dz (the Golden Gate's court, 4.5 m below the esplanade;
# retaining walls, railing and stairs by landmarks_haram)
SUNKEN = [{"poly": box(884.0, 249.0, 892.0, 266.0), "dz": -4.5, "name": "golden_gate_court"}]


# footprints that OSM draws across a street: clip them back to the street wall (way id, half-width)
CLIP_STREETS = {"w1022672085": [(26492706, 2.2)]}     # Holy Sepulchre over Christian Quarter St
# level areas the terrain field does not know about: (OSM way, point whose street level they take)
LOCAL_FLATS = [(612045223, (208.2, 183.4)),           # Holy Sepulchre parvis, at the main door
               # the Western Wall prayer-area level carried north to the front of Wilson's Arch hall
               (Polygon([(621.91, 30.53), (646.06, 35.24), (647.21, 29.35), (623.06, 24.64)]), -43.58)]


# covered streets: passages under buildings (OSM tunnel=yes|building_passage, covered=yes) are carved
# out of the footprints and vaulted; the covered souqs are vaulted between their facades
COVERED_SOUQS = {"Suq Al La'h'hamin", "Suq Al Attarin", "Suq Al-Khawajat", "Suq El-Quatta"}


def souq_key(w):
    """SOUQ_STREETS key of a way (its OSM id as a string, or its name:en), or None."""
    if str(w["id"]) in SOUQ_STREETS:
        return str(w["id"])
    n = w["tags"].get("name:en")
    return n if n in SOUQ_STREETS else None


def covered_ways(d):
    out = []
    for w in d["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if not t.get("highway") or len(pts) < 2 or t.get("area") == "yes":
            continue
        named = t.get("name:en") in COVERED_SOUQS or w["id"] in COVERED_IDS
        lay = int(t.get("layer", "0") or 0)
        if named or (lay >= 0 and (t.get("tunnel") in ("yes", "building_passage") or t.get("covered") == "yes")):
            out.append((w, LineString(pts), "souq" if named else "passage"))
    return out


def landmark_ids():
    """OSM ids registered by the landmark builders (blender/landmarks_*.py LANDMARKS dicts)."""
    ids = set()
    for fn in (ROOT / "blender").glob("landmarks_*.py"):
        m = re.search(r"^LANDMARKS = \{(.*?)^\}", fn.read_text(), re.M | re.S)   # the module-level dict
        if m:
            ids |= set(re.findall(r'"([wrnm][\w]+)"\s*:', m.group(1)))
    return ids


def gate_ids():
    """OSM ids of the gates (blender/landmarks_gates.py LANDMARKS)."""
    fn = ROOT / "blender/landmarks_gates.py"
    m = re.search(r"^LANDMARKS = \{(.*?)^\}", fn.read_text(), re.M | re.S) if fn.exists() else None
    return set(re.findall(r'"([wrnm][\w]+)"\s*:', m.group(1))) if m else set()


SHOPS = {"w290812336", "w290812408", "w1392903902", "w1393928801", "w126781854",
         "w1549766140", "w126782745", "w290692953", "w1393938082", "w1393938083", "w1393938081"}
ASHLAR = {"w290812336", "w290812408", "w1393420836", "w1393928801", "w126781854", "w126782745",
          "w126783156", "w1393420835"}
DOMES = {"w1393938082": 1, "w1393938083": 1, "w290692953": 2, "w1393938081": 1, "r3864551": 2,
         "w1392903903": 1}
HIPPED = {"w126783156", "w290690288"}
# Jerusalem limestone varies from cream to pinkish to grey; multiplied onto the texture
TINTS = [(1.0, 0.97, 0.9), (1.03, 0.95, 0.87), (0.94, 0.93, 0.9), (1.05, 0.99, 0.86), (1.06, 1.04, 0.98),
         (0.98, 0.92, 0.86)]

GATEHOUSE = {"ring": [(3.4, 3.2), (-3.8, -3.7), (2.9, -11.1), (9.5, -4.7)], "height": 13.0,    # gate.md s9
             "wall": 2.0,
             "passages": [{"edge": 0, "u": 0.5, "w": 3.6, "h": 6.5},      # outer arch (A-B)
                          {"edge": 3, "u": 0.45, "w": 3.6, "h": 6.5}]}    # inner arch (D-A)
# The wall NW of the gate steps: low stretch with the blind arch, a taller stretch, then the long wall
# (gate.md section 2 / 9; photos from the plaza and Schick's 1898 plan)
CITY_WALLS = [
    {"name": "wall_nw", "pts": [(-50.88, 58.65), (-10.68, 19.15), (-5.87, 14.47)], "height": 11.25, "thick": 3.2},
    {"name": "tall_stretch", "pts": [(-5.87, 14.47), (0.58, 8.19)], "height": 16.0, "thick": 3.8},
    {"name": "blind_arch_stretch", "pts": [(0.58, 8.19), (4.52, 4.35)], "height": 12.8, "thick": 3.2},
]   # points run NW -> SE so the outside (south-west) is on the right of each segment. Heights measured
#     on photo 062 with its calibrated eval pose (fort_notes.md); the line is shifted 1.6 m inwards so
#     the outer face passes through gate corner A (3.4, 3.2) and the gate's whole NW face shows.
MOAT_DEPTH = 5.0
CITADEL_WALL_H = 13.0
MOAT_W = 6.0
TOWERS = [
    {"kind": "box", "name": "phasael", "c": (66.0, -23.0), "size": (20.0, 17.0), "rot": 24.0, "h": 18.0,
     "top": {"size": (14.0, 12.0), "h": 3.0}},       # 21 m in all with the set-back top storey       # east side by the east ditch (citadel_east.md A5, eval north_side)
    {"kind": "box", "name": "nw_tower", "c": (27.0, -27.0), "size": (17.0, 15.0), "rot": 35.0, "h": 18.0,
     "machicolations": 3},                           # by the 1898 breach (eval back_to_gate / outside_gate)
    {"kind": "minaret", "c": (24.0, -79.0), "r": 2.6, "h": 22.0},   # 8-10 m above the walls (fort_notes.md)
]
DAVID = {"pts": [(96.7, 2.8), (106.4, 9.1), (115.4, 9.3), (135.9, 8.7), (159.0, 8.2), (175.6, 9.4)],
         "start_s": 16.0, "riser": 0.13, "tread": 2.2, "width": 7.0}
# road through the breach and along the square (OSM ways 26492720 + 265414845)
ROAD = [(-10.9, -79.3), (-1.8, -38.3), (0.2, -31.8), (3.4, -24.2), (8.0, -16.7), (13.4, -11.6), (21.0, -9.7),
        (25.4, -7.5), (47.8, -0.2), (58.4, 3.7), (65.3, 5.7), (69.5, 7.2), (75.5, 8.6), (82.0, 8.4), (88.5, 6.7),
        (94.5, 4.2), (100.2, -1.2), (104.0, -6.0), (108.6, -14.0), (111.2, -21.2), (112.8, -31.6), (113.0, -41.2),
        (110.6, -57.0), (108.1, -78.4)]
ROAD_HALF = 3.1
KERB = 0.05
KERB_BAND = 0.4
SPAWN = {"p": (-22.0, 2.0), "heading": 104.0}


# Market streets (OSM name:en) -> (share of facades that are shop rows, canopy probability).
# Every facade fronting one gets the souq profile, as David Street does; covered souqs get no
# canopies. From the sector notes and the OSM shop/amenity nodes per street.
SOUQ_STREETS = {
    "David Street": (1.0, 0.6), "Suq Khan al-Zeit": (0.95, 0.5), "Al Wadi": (0.7, 0.35),
    "Christian Quarter Street": (0.9, 0.35), "Suq Aftimos": (0.9, 0.5), "Muristan Street": (0.7, 0.3),
    "Suq Al La'h'hamin": (1.0, 0.0), "Suq Al Attarin": (1.0, 0.0), "Suq Al-Khawajat": (1.0, 0.0),
    "Suq El-Quatta": (1.0, 0.0), "Suq Ed-Dabbagha": (0.9, 0.4), "Suq Al-Aqbat": (0.8, 0.3),
    "Silsileh": (0.8, 0.3), "Damascus Gate": (0.9, 0.5), "Aqabat El-Khanqa": (0.6, 0.2),
    "Saint Mark Street": (0.5, 0.2), "Habad Street": (0.6, 0.2), "Habad": (0.7, 0.1),
    "Via Dolorosa": (0.35, 0.2), "Lions' Gate Street": (0.3, 0.2), "Bab Hutta Street": (0.25, 0.1),
    "Latin Patriarchate Road": (0.25, 0.2), "Greek Orthodox Patriarchate Street": (0.3, 0.2),
}


# ---------------------------------------------------------------- sector profiles
# data/reference/profiles/<sector>.json, written by the per-sector passes (format and checks:
# pipeline/check_profiles.py): market and covered streets, open areas, missing / non-existent
# buildings, notable props. Building settings (height, wall, tint, shops, domes, roof, parapet,
# storey) and facades go in data/reference/overrides/<osm>.json ("settings" / "facades").
PROFILES = {}
_PDIR = ROOT / "data/reference/profiles"
for _fn in sorted(_PDIR.glob("*.json")) if _PDIR.exists() else []:
    try:
        PROFILES[_fn.stem] = json.loads(_fn.read_text())
    except (ValueError, OSError) as _e:
        print("profile %s skipped: %s" % (_fn.name, _e))
COVERED_IDS, PROFILE_OPEN, PROFILE_PROPS = set(), [], []
for _sid, _pr in PROFILES.items():
    for _k, _v in _pr.get("souq_streets", {}).items():
        SOUQ_STREETS[str(_k)] = tuple(_v)
    for _k in _pr.get("covered_streets", []):
        if str(_k).isdigit():
            COVERED_IDS.add(int(_k))
        else:
            COVERED_SOUQS.add(_k)
    PROFILE_OPEN += [Polygon(_o["ring"]).buffer(0) for _o in _pr.get("open_areas", [])]
    MANUAL_BUILDINGS.extend({**_m, "ring": [tuple(_q) for _q in _m["ring"]]} for _m in _pr.get("manual_buildings", []))
    SKIP.update(_pr.get("remove_buildings", {}).keys())
    PROFILE_PROPS += _pr.get("props", [])



def souq_profile(L, eg, rng, canopy=True, width=7.0):
    """Default override for a facade fronting a market street: closed dukkan shops (notes C3), raised
    thresholds (C2), shed canopies (C4) where the street is wide enough, blade boards (C6). Hero
    overrides take precedence."""
    n = max(1, int((L - 0.8) // 3.0))
    sp = (L - 0.8) / n
    ground = []
    for k in range(n):
        w = min(sp - 0.55, rng.uniform(2.0, 2.9))
        ground.append({"kind": "shop" if w >= 1.4 else "blind", "w": round(w, 2), "h": round(rng.uniform(2.8, 3.15), 2),
                       "arch": rng.choice(["segment", "segment", None]),
                       "door": rng.choice(["door_teal", "door_teal", "door_teal", "door_olive", "rolldown_green",
                                           "rolldown_grey", "door_green2"])})
    ov = {"souq": True, "shops": True, "centres": [round(0.4 + sp * (k + 0.5), 2) for k in range(n)], "ground": ground,
          "ground_storey": 4.4, "awning": False, "thr": round(rng.uniform(0.16, 0.28), 2),
          "thr_out": round(min(rng.uniform(0.4, 0.65), 0.12 * width), 2)}
    depth = min(rng.uniform(1.2, 1.6), 0.3 * width)
    if canopy and depth >= 0.8:
        ov["canopy"] = {"depth": round(depth, 2), "z_front": 2.9, "z_wall": 3.6}   # eval david_street
    return ov


# SPEC_DIR=<dir> writes the spec there instead of data/spec (parallel workers each use their own;
# build_city.py --part reads the same variable). Files are written atomically.
SPEC_DIR = Path(os.environ["SPEC_DIR"]).resolve() if os.environ.get("SPEC_DIR") else ROOT / "data/spec"
LEGACY_SPEC = SPEC_DIR / "scene_spec.json" if os.environ.get("SPEC_DIR") else ROOT / "data/scene_spec.json"


def write_json(path, obj, indent=None):
    tmp = path.with_name(path.name + ".tmp%d" % os.getpid())
    tmp.write_text(json.dumps(obj, indent=indent))
    os.replace(tmp, path)


def write_sectors(spec):
    """Split the spec: data/spec/base.json (ground, kerbs, walls, citadel, gate, context) and one file
    per sector (its buildings, props, steps, cables, beams, ground decals). data/scene_spec.json stays
    a legacy single-scene spec (base + s00) for the evaluation loop and tools."""
    import sectors as S
    secs = S.load()
    out_dir = SPEC_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    def sector_of(x, y, osm=None):
        if osm in FORCE_SECTOR:
            return FORCE_SECTOR[osm]
        pt = Point(x, y)
        if HERO_ZONE.contains(pt):
            return "s00_jaffa"
        for sid, geom, _ in secs:
            if geom.contains(pt):
                return sid
        return None

    per = {sid: {"buildings": [], "props": [], "steps": [], "cables": [], "beams": [], "ground_decals": [], "vaults": []}
           for sid, _, _ in secs}
    base_b, base_props, base_dec = [], [], []
    for b in spec["buildings"]:
        sid = sector_of(*b["c"], osm=b["osm"]) if b["tier"] != "context" else None
        if sid is None and b["tier"] != "context":            # centroid on the wall line: nearest sector
            pt = Point(b["c"])
            sid = min(secs, key=lambda s_: s_[1].distance(pt))[0]
        b["sector"] = sid
        (per[sid]["buildings"] if sid else base_b).append(b)
    for key, arr in (("props", spec["props"]), ("ground_decals", spec["ground_decals"])):
        for it in arr:
            sid = sector_of(it["p"][0], it["p"][1])
            if sid:
                per[sid][key].append(it)
            else:
                (base_props if key == "props" else base_dec).append(it)
    def sector_or_nearest(x, y):
        return sector_of(x, y) or min(secs, key=lambda s_: s_[1].distance(Point(x, y)))[0]
    for st in spec["steps"]:
        e = st["poly"]["ext"][0]
        per[sector_or_nearest(*e)]["steps"].append(st)
    for key in ("cables", "beams"):
        for it in spec[key]:
            m = ((it["a"][0] + it["b"][0]) / 2, (it["a"][1] + it["b"][1]) / 2)
            per[sector_or_nearest(*m)][key].append(it)
    for v in spec.get("vaults", []):
        m = v["pts"][len(v["pts"]) // 2]
        per[sector_or_nearest(m[0], m[1])]["vaults"].append(v)
    base = {k: spec[k] for k in ("poc_box", "context_box", "ground", "kerbs", "gatehouse", "city_walls", "citadel",
                                  "walls_generic", "spawn", "sources")}
    base.update({"buildings": base_b, "props": base_props, "ground_decals": base_dec, "steps": [], "cables": [],
                 "beams": []})
    write_json(out_dir / "base.json", base)
    index = []
    for sid, geom, rec in secs:
        bx = list(geom.bounds)                              # sector area plus what its buildings overhang
        for bd in per[sid]["buildings"]:
            xs = [p[0] for p in bd["ring"]]
            ys = [p[1] for p in bd["ring"]]
            bx = [min(bx[0], min(xs)), min(bx[1], min(ys)), max(bx[2], max(xs)), max(bx[3], max(ys))]
        part = dict(per[sid], id=sid, bounds=[round(v, 1) for v in bx], name=rec["name"])
        write_json(out_dir / ("%s.json" % sid), part)
        index.append({"id": sid, "bounds": part["bounds"], "buildings": len(part["buildings"]),
                      "props": len(part["props"]), "name": rec["name"]})
    write_json(out_dir / "index.json", {"sectors": index}, indent=1)
    legacy = dict(base)
    legacy["buildings"] = base_b + per["s00_jaffa"]["buildings"]
    for k in ("props", "steps", "cables", "beams", "ground_decals"):
        legacy[k] = base[k] + per["s00_jaffa"][k] if k in ("props", "ground_decals") else per["s00_jaffa"][k]
    write_json(LEGACY_SPEC, legacy)
    print("sectors:", ", ".join("%s %d" % (i["id"], i["buildings"]) for i in index), "| base context", len(base_b))


# OSM ways tagged city_wall that are not a crenellated wall: the Haram enclosure boundary on the west
# and north sides (lined with porticoes and madrasas) and the Little Western Wall (landmarks_haram)
NOT_WALLS = {26554724, 291970363}
HARAM_WALL_H = 7.0     # the Haram's east and south walls: merlons ~7 m above the esplanade (Golden Gate photos)


def generic_walls(d, cit_outer, gate_poly, seg_len=15.0, height=11.5, thick=3.0):
    """City-wall segments from OSM outside the hand-modelled Jaffa Gate stretch: terrain-following,
    outside (beyond the walls) on the right-hand side of each segment."""
    from shapely.ops import linemerge
    lines = unary_union([LineString(w["pts"]) for w in d["ways"]
                         if "multipolygon" not in w and w["tags"].get("barrier") == "city_wall"
                         and w["id"] not in NOT_WALLS])
    custom = unary_union([LineString(w["pts"]).buffer(w["thick"] / 2 + 2.0) for w in CITY_WALLS]
                         + [gate_poly.buffer(3.0), cit_outer.buffer(3.0)])
    rest = lines.difference(custom)
    rest = linemerge(rest) if rest.geom_type == "MultiLineString" else rest
    inside = CITY.union(HARAM).buffer(-0.5)
    out = []
    taken = []                     # OSM draws some stretches twice (city wall + Haram enclosure, faces)
    for ln in sorted(getattr(rest, "geoms", [rest]), key=lambda g: -g.length):
        if ln.geom_type != "LineString" or ln.length < 2.0:
            continue
        cs = list(ln.coords)                    # keep OSM vertices (towers project from the curtain)
        pts = [cs[0]]
        for a_, b_ in zip(cs, cs[1:]):
            n = max(1, int(math.ceil(math.dist(a_, b_) / seg_len)))
            pts += [(a_[0] + (b_[0] - a_[0]) * k / n, a_[1] + (b_[1] - a_[1]) * k / n) for k in range(1, n + 1)]
        for a, b in zip(pts, pts[1:]):
            (tx, ty), (nx, ny), L = edge_frame(a, b)
            if L < 0.5:
                continue
            seg = LineString([a, b])
            if any(seg.intersection(t_).length > 0.4 * L for t_ in taken if t_.intersects(seg)):
                continue
            taken.append(seg.buffer(thick + 0.5, cap_style="flat"))
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if inside.contains(Point(m[0] + nx * 5, m[1] + ny * 5)):     # right side must be outside
                a, b = b, a
                nx, ny = -nx, -ny
            z_in = street_z(m[0] - nx * 5, m[1] - ny * 5)
            z_out = street_z(m[0] + nx * 5, m[1] + ny * 5)
            h = HARAM_WALL_H if HARAM.buffer(-2.0).contains(Point(m[0] - nx * 5, m[1] - ny * 5)) else height
            out.append({"a": [round(a[0], 2), round(a[1], 2)], "b": [round(b[0], 2), round(b[1], 2)],
                        "z0": round(min(z_in, z_out) - 2.5, 2), "z1": round(z_in + h, 2), "thick": thick})
    return out


def douglas_peucker(r, tol):
    i1 = max(range(len(r)), key=lambda i: math.dist(r[0], r[i]))

    def dp(pts):
        if len(pts) < 3:
            return pts
        from geo import seg_dist
        dmax, k = max((seg_dist(pts[i], pts[0], pts[-1]), i) for i in range(1, len(pts) - 1))
        if dmax < tol:
            return [pts[0], pts[-1]]
        return dp(pts[:k + 1])[:-1] + dp(pts[k:])
    return dp(r[0:i1 + 1])[:-1] + dp(r[i1:] + [r[0]])[:-1]


def offset_ring(r, dists):
    """Offset each edge i of a CCW ring inward by dists[i]."""
    n = len(r)
    lines = []
    for i in range(n):
        (tx, ty), _, _ = edge_frame(r[i], r[(i + 1) % n])
        d = dists[i]
        lines.append(((r[i][0] - ty * d, r[i][1] + tx * d), (tx, ty)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 0.15:
            out.append(p2)
            continue
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
    return out


def polyline_s(pts, p):
    best, s0 = (1e9, 0.0), 0.0
    for a, b in zip(pts, pts[1:]):
        ax, ay = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ax, ay)
        t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (L * L)))
        d = math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)
        if d < best[0]:
            best = (d, s0 + t * L)
        s0 += L
    return best[1], best[0]


def david_drop(s):
    return max(0.0, s - DAVID["start_s"]) * DAVID["riser"] / DAVID["tread"]


_FLATS = []                                    # [(polygon, z)] filled by setup_flats()


def setup_flats(d):
    for wid, at in LOCAL_FLATS:                # (OSM way, point it takes its level from) or (polygon, z)
        if isinstance(wid, Polygon):
            _FLATS.append((wid, float(at)))
            continue
        w = next((w_ for w_ in d["ways"] if w_["id"] == wid), None)
        if w and _terrain is not None:
            _FLATS.append((Polygon(w["pts"]).buffer(0), float(_terrain.street_z(*at))))
    street_z.cache_clear()


@functools.lru_cache(maxsize=1 << 21)          # ground vertices are shared by ~6 triangles
def street_z(x, y):
    for poly, z in _FLATS:
        if poly.contains(Point(x, y)):
            return z
    if _terrain is not None:
        return float(_terrain.street_z(x, y))
    if x > 100 and y > 3.5:
        return -david_drop(polyline_s(DAVID["pts"], (x, y))[0])
    return 0.0


def street_z_v(xs, ys):
    """street_z over arrays (one vectorised terrain lookup for a whole ground tile set)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    if _terrain is not None:
        z = np.asarray(_terrain.street_z(xs, ys), float)
        for poly, zf in _FLATS:
            z = np.where(shapely.contains_xy(poly, xs, ys), zf, z)
        return z
    return np.array([street_z(x, y) for x, y in zip(xs, ys)])


def cell_size(x, y):
    """Ground mesh density: fine in the hero area, medium inside the walls, coarse outside."""
    if box(*POC).contains(Point(x, y)):
        return 2.0
    return 4.0 if CITY.contains(Point(x, y)) else 8.0


def tess_regions(region, zfun, cell=None, tile=32.0):
    """Clip region to 32 m tiles (fast rectangle clipping), then to cells, and triangulate each
    piece; returns a flat triangle list with z. cell=None picks the size per tile (cell_size)."""
    tris = []
    if region.is_empty:
        return tris
    from shapely import make_valid as _mv
    region = _mv(region)
    region = unary_union(polys_of(region, 1e-3))           # polygons only, no stray lines or points
    if region.is_empty:
        return tris
    x0, y0, x1, y1 = region.bounds
    for ti in range(math.floor(x0 / tile), math.ceil(x1 / tile)):
        for tj in range(math.floor(y0 / tile), math.ceil(y1 / tile)):
            tx0, ty0 = ti * tile, tj * tile
            try:
                sub = clip_by_rect(region, tx0, ty0, tx0 + tile, ty0 + tile)
            except Exception:                              # noqa: BLE001
                sub = region.intersection(box(tx0, ty0, tx0 + tile, ty0 + tile))
            if sub.is_empty:
                continue
            c = cell or cell_size(tx0 + tile / 2, ty0 + tile / 2)
            n = int(round(tile / c))
            for i in range(n):
                for j in range(n):
                    try:
                        piece = clip_by_rect(sub, tx0 + i * c, ty0 + j * c, tx0 + (i + 1) * c, ty0 + (j + 1) * c)
                    except Exception:                      # noqa: BLE001
                        piece = sub.intersection(box(tx0 + i * c, ty0 + j * c, tx0 + (i + 1) * c, ty0 + (j + 1) * c))
                    if piece.is_empty:
                        continue
                    _tri_piece(piece, tris)
    if tris:                                               # z for every vertex in one vectorised call
        xy = np.array(tris, float).reshape(-1, 2)
        z = np.round(zfun(xy[:, 0], xy[:, 1]), 3)
        tris = [[[round(xy[3 * k + m, 0], 3), round(xy[3 * k + m, 1], 3), float(z[3 * k + m])] for m in range(3)]
                for k in range(len(tris))]
    return tris


def _tri_piece(piece, tris):
    if True:
        if True:
            for p in polys_of(piece, 1e-4):
                try:
                    tri_set = polys_of(constrained_delaunay_triangles(p), 1e-5)
                except Exception:                          # noqa: BLE001  (rare degenerate pieces)
                    from shapely.ops import triangulate as _tri
                    pv = p.buffer(0)
                    tri_set = [t for t in _tri(pv) if pv.contains(t.representative_point())]
                for t in tri_set:
                    pts = list(t.exterior.coords)[:3]
                    if (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[1][1] - pts[0][1]) * (pts[2][0] - pts[0][0]) < 0:
                        pts = [pts[0], pts[2], pts[1]]
                    tris.append([(x, y) for x, y in pts])


LANDMARK_IDS = landmark_ids()


def main():
    d = json.loads((ROOT / "data/osm_local.json").read_text())
    rng = random.Random(1898)
    for w in d["ways"]:            # the covered souqs are mapped as layer -1 (under the buildings above):
        if w["tags"].get("name:en") in COVERED_SOUQS or w["id"] in COVERED_IDS:   # they are the street level
            w["tags"] = dict(w["tags"], layer="0")
    setup_flats(d)
    # the Dome of the Rock's upper platform (OSM retaining wall w137725307): no trees on it
    PLATFORM = next((Polygon(w["pts"]).buffer(0) for w in d["ways"] if w["id"] == 137725307), Polygon())
    souq_lines = [(LineString(w["pts"]), SOUQ_STREETS[souq_key(w)]) for w in d["ways"]
                  if w["tags"].get("highway") and souq_key(w)
                  and len(w.get("pts") or []) > 1 and int(w["tags"].get("layer", "0") or 0) >= 0]
    souq_tree = STRtree([ln for ln, _ in souq_lines])
    if (ROOT / "data/sectors.json").exists():
        import sectors
        sector_at = roofscape.sector_lookup(sectors.load())
    else:
        sector_at = lambda x, y: None  # noqa: E731

    # ---------------------------------------------------------------- citadel
    citadel = next(b for b in d["buildings"] if b["id"] == "r136164")
    cit_outer_r = ccw(douglas_peucker(list(map(tuple, citadel["outer"][0])), 2.5))
    # split the long north edge at x = 42 so the moat can start there
    for i in range(len(cit_outer_r)):
        a, b = cit_outer_r[i], cit_outer_r[(i + 1) % len(cit_outer_r)]
        if (a[0] - 42) * (b[0] - 42) < 0 and min(a[1], b[1]) > -30:
            t = (42 - a[0]) / (b[0] - a[0])
            cit_outer_r.insert(i + 1, (42.0, round(a[1] + (b[1] - a[1]) * t, 3)))
            break
    cit_inner_r = ccw(clean(citadel["inner"][0]).exterior.coords)
    moat_edges = []
    for i in range(len(cit_outer_r)):
        a, b = cit_outer_r[i], cit_outer_r[(i + 1) % len(cit_outer_r)]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        moat_edges.append(MOAT_W if (m[1] > -62 and m[0] > 42 and not (m[0] < 30 and m[1] < -30)) else 0.0)
    cit_mass_r = offset_ring(cit_outer_r, moat_edges)
    cit_outer, cit_mass, cit_inner = Polygon(cit_outer_r), Polygon(cit_mass_r), Polygon(cit_inner_r)
    assert cit_mass.is_valid and cit_outer.is_valid, "citadel rings invalid"
    citadel_body = cit_mass.difference(cit_inner)
    moat = cit_outer.difference(cit_mass)

    gate_poly = Polygon(GATEHOUSE["ring"])
    wall_polys = [LineString(w["pts"]).buffer(w["thick"] / 2, cap_style="flat") for w in CITY_WALLS]

    # ---------------------------------------------------------------- footprints
    cands = []
    for b in d["buildings"]:
        if b["id"] in SKIP or b["id"] == "r136164" or not b["outer"] or len(b["outer"][0]) < 3:
            continue
        if b["tags"].get("layer", "0").startswith("-"):
            continue
        p = clean(b["outer"][0])
        if p is None or p.area < 6:
            continue
        c = p.centroid
        if not box(*CONTEXT).contains(c):
            continue
        tier = "hero" if HERO_ZONE.contains(c) else ("mid" if (box(*POC).contains(c) or CITY.contains(c)) else "context")
        if b["id"] in FORCE_SECTOR:
            tier = "mid"
        cands.append((b, p, tier))
    prio = {"hero": 0, "mid": 1, "context": 2}
    cands.sort(key=lambda t: (prio[t[2]], -t[1].area))
    for m in MANUAL_BUILDINGS:                                  # gap fillers go last
        mp = Polygon(m["ring"])
        tags = {"name": m.get("name", ""), "building": "yes", "note": m["why"]}
        if m.get("name"):
            tags["name:en"] = m["name"]
        cands.append(({"id": m["id"], "tags": tags, "outer": [m["ring"]]},
                      mp, "hero" if HERO_ZONE.contains(mp.centroid) else "mid"))
        HEIGHTS[m["id"]] = m["height"]
        if m.get("shops", True):
            SHOPS.add(m["id"])
    blocked = unary_union([citadel_body, moat, gate_poly] + wall_polys)
    # the OSM wall circuit: its line is the walls' OUTER face (landmarks_gates.WALL_LINE), so the slab
    # occupies the 3 m inside it; ordinary footprints drawn up against the wall are clipped to it
    walls_generic = generic_walls(d, cit_outer, gate_poly)
    wall_slabs = unary_union([LineString([w_["a"], w_["b"]]).buffer(w_["thick"] + 0.05, single_sided=True,
                                                                     cap_style="flat") for w_ in walls_generic])
    cov = [(w_, ln_, k_) for w_, ln_, k_ in covered_ways(d) if CITY.intersects(ln_)
           and not HERO_ZONE.intersects(ln_) and not any(g_ in str(w_["id"]) for g_ in ())]
    cov_hw = {}
    for w_, ln_, k_ in cov:                       # passages ~3 m wide, souqs measured later from the facades
        try:
            cov_hw[w_["id"]] = float(w_["tags"]["width"]) / 2
        except (KeyError, ValueError):
            cov_hw[w_["id"]] = 1.6 if k_ == "passage" else 2.2
    passages = unary_union([ln_.buffer(cov_hw[w_["id"]], cap_style="flat") for w_, ln_, k_ in cov] or [Polygon()])
    prepare(passages)
    gids = gate_ids()
    # Dung and New Gate are sections of crenellated curtain (landmarks_gates builds them): still wall
    cuts = [p_.convex_hull.buffer(1.0) for b_, p_, _ in cands
            if b_["id"] in gids and b_["id"] not in ("w1545285986", "w1393450805")]
    if cuts:
        wall_slabs = wall_slabs.difference(unary_union(cuts).buffer(0.5))   # no wall inside a gate
    prepare(wall_slabs)
    # buildings OSM does not map along the streets (pipeline/infill.py), lowest priority of all
    fill = infill.infill(d, [p for _, p, t in cands if t != "context"], CITY.buffer(-16.5),
                         unary_union([HARAM.buffer(2.0), HERO_ZONE.buffer(3.0), blocked.buffer(2.0), wall_slabs.buffer(0.5),
                                      unary_union(GROUND_HOLES).buffer(0.5), unary_union(PROFILE_OPEN or [Polygon()]),
                                      LineString(ROAD).buffer(ROAD_HALF + 1.0)]))
    for k, fp in enumerate(fill):
        cands.append(({"id": "f%d" % k, "tags": {"building": "yes", "note": "infill"}, "outer": [list(fp.exterior.coords)[:-1]]},
                      fp, "mid"))
    print("infill:", infill.stats(fill))
    prepare(blocked)
    taken = []
    grid = {}                                  # 20 m cells -> indices into taken
    G = 20.0

    def cells_of(g):
        bx0, by0, bx1, by1 = g.bounds
        return [(i, j) for i in range(math.floor(bx0 / G), math.floor(bx1 / G) + 1)
                for j in range(math.floor(by0 / G), math.floor(by1 / G) + 1)]
    buildings = []
    for b, p, tier in cands:
        rest = p.difference(blocked) if blocked.intersects(p) else p
        for wid, hw_ in CLIP_STREETS.get(b["id"], []):
            wpts = next((w_["pts"] for w_ in d["ways"] if w_["id"] == wid), None)
            if wpts:
                rest = rest.difference(LineString(wpts).buffer(hw_))
        if b["id"] not in LANDMARK_IDS and wall_slabs.intersects(rest):
            rest = rest.difference(wall_slabs)
        if b["id"] not in LANDMARK_IDS and passages.intersects(rest):      # covered passages stay walkable
            rest = rest.difference(passages)
        near = {k for c_ in cells_of(p) for k in grid.get(c_, ())}
        near = [taken[k] for k in near if taken[k].intersects(rest)]
        if near:
            rest = rest.difference(unary_union(near))
        pieces = polys_of(rest, 6.0)            # no simplify after the difference: it would re-open overlaps
        pieces = [q for q in pieces if q.is_valid and q.area > 6.0]
        for k, q in enumerate(sorted(pieces, key=lambda q: -q.area)):
            if len(pieces) > 1 and q.area < 15:
                continue
            q = Polygon(q.exterior)                              # drop courtyard holes
            taken.append(q)
            for c_ in cells_of(q):
                grid.setdefault(c_, []).append(len(taken) - 1)
            bid = b["id"] if k == 0 else "%s_%d" % (b["id"], k)
            buildings.append({"id": bid, "osm": b["id"], "poly": q, "tags": b["tags"], "tier": tier})

    obs_list = [bd["poly"] for bd in buildings] + [cit_mass, gate_poly] + wall_polys
    obstacles = unary_union(obs_list)
    prepare(obstacles)
    obs_tree = STRtree(obs_list)

    def inside_other(pt, self_idx):
        """Is the point inside any obstacle other than building self_idx?"""
        for k in obs_tree.query(pt):
            if k != self_idx and obs_list[k].contains(pt):
                return True
        return False

    # ---------------------------------------------------------------- ground regions
    ctx = box(*CONTEXT)
    road = LineString(ROAD).buffer(ROAD_HALF, cap_style="flat", join_style="round")
    bld_union = unary_union([bd["poly"] for bd in buildings])
    # stepped streets (pipeline/stairs.py): David Street from its first step, every OSM steps way,
    # and any lane steeper than 7 %, all from the terrain
    open_street = ctx.difference(bld_union).difference(cit_outer).difference(unary_union(GROUND_HOLES))
    fp_list = [bd["poly"] for bd in buildings]
    fp_tree = STRtree(fp_list)
    david = LineString(DAVID["pts"])
    st_recs = stairs.build(d["ways"], street_z, open_street,
                           lambda w, ln: infill.street_halfwidth(w["tags"], ln, fp_tree, fp_list),
                           skip=david.buffer(DAVID["width"] / 2 + 1.0).union(box(*CONTEXT).difference(CITY.buffer(80.0))),
                           extra=[(david, DAVID["width"] / 2, DAVID["start_s"], david.length)])
    steps = [{"poly": poly_json(r_["poly"]), "top": r_["top"], "bottom": r_["bottom"], "dir": r_["dir"]}
             for r_ in st_recs]
    steps_union = unary_union([r_["poly"].buffer(0) for r_ in st_recs] or [Polygon()]).buffer(0.001)

    sunken = unary_union([sk["poly"] for sk in SUNKEN])
    street = ctx.difference(bld_union).difference(cit_outer).difference(steps_union) \
        .difference(unary_union(GROUND_HOLES)).difference(sunken)
    road_area = street.intersection(road)
    paving_all = street.difference(road)
    kerb_band = paving_all.intersection(road.buffer(KERB_BAND))
    paving = paving_all.difference(kerb_band)
    courtyard = cit_inner.difference(bld_union)
    regions = [
        ("paving", paving, street_z_v),                    # z functions take arrays
        ("kerb_band", kerb_band, street_z_v),
        ("setts", road_area, lambda x, y: street_z_v(x, y) - KERB),
        ("grass", moat.buffer(-0.01), lambda x, y: np.full(len(x), -MOAT_DEPTH)),
        ("paving", courtyard, lambda x, y: np.full(len(x), 1.0)),
    ] + [
        ("paving", sk["poly"].difference(bld_union), lambda x, y, dz=sk["dz"]: street_z_v(x, y) + dz) for sk in SUNKEN
    ]
    ground = []
    for mat, reg, zf in regions:
        tri = tess_regions(reg, zf)
        ground.append({"mat": mat, "tris": tri})
    # kerbs: where road meets paving (not where it meets buildings or the moat)
    kerbs = []
    edge = road_area.boundary.intersection(paving_all.buffer(0.02))
    for ls in getattr(edge, "geoms", [edge]):
        if ls.geom_type != "LineString" or ls.length < 0.1:
            continue
        c = list(ls.coords)
        for a, b in zip(c, c[1:]):
            if math.dist(a, b) < 0.02:
                continue
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            # orient so the face looks into the road (right-hand normal points into the road)
            (tx, ty), (nx, ny), _ = edge_frame(a, b)
            if not road_area.buffer(0.01).contains(Point(m[0] + nx * 0.05, m[1] + ny * 0.05)):
                a, b = b, a
            z = street_z(*m)
            kerbs.append({"a": [round(a[0], 3), round(a[1], 3)], "b": [round(b[0], 3), round(b[1], 3)],
                          "z0": round(z - KERB, 3), "z1": round(z, 3)})

    # ---------------------------------------------------------------- buildings
    out_b = []
    for bidx, bd in enumerate(buildings):
        bid, osm = bd["id"], bd["osm"]
        q = bd["poly"]
        r = ccw(q.exterior.coords)
        brng = random.Random(zlib.crc32(bid.encode()))
        exposed, eground = [], []
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            _, (nx, ny), L = edge_frame(a, b)
            hits = sum(1 for t in (0.25, 0.5, 0.75)
                       if inside_other(Point(a[0] + (b[0] - a[0]) * t + nx * 1.2, a[1] + (b[1] - a[1]) * t + ny * 1.2), bidx))
            exposed.append(hits <= 1 and L > 0.3)
            m = ((a[0] + b[0]) / 2 + nx * 1.0, (a[1] + b[1]) / 2 + ny * 1.0)
            z = street_z(*m)
            if road.contains(Point(m)) and not courtyard.contains(Point(m)):
                z -= KERB
            if moat.contains(Point(m)):
                z = -MOAT_DEPTH
            if cit_inner.contains(Point(m)):
                z = 1.0
            eground.append(round(z, 3))
        for door in GATE_DOORS.get(osm, []):              # gate passages: level at the doors
            i_ = min(range(len(r)), key=lambda k_: LineString([r[k_], r[(k_ + 1) % len(r)]]).distance(Point(door)))
            _, (nx_, ny_), _ = edge_frame(r[i_], r[(i_ + 1) % len(r)])
            eground[i_] = round(street_z(door[0] + nx_, door[1] + ny_), 3)
        zs = [street_z(*p) for p in r]
        g_hi = max(zs) if not cit_inner.contains(q.centroid) else 1.0
        g_lo = min(min(zs), min(eground))
        hb = hero.BUILDING.get(osm, {})
        h = hb.get("height", HEIGHTS.get(osm))
        sid = sector_at(q.representative_point().x, q.representative_point().y) if bd["tier"] == "mid" else None
        if h is None and sid:
            h = roofscape.height_for(osm, bd["tags"], q.area, sid)
        if h is None:
            h = roofscape.osm_height(bd["tags"]) or (7.0 if q.area < 60 else 9.0 + (zlib.crc32(osm.encode()) % 5))
        ashlar = hb["wall"] == "ashlar" if "wall" in hb else osm in ASHLAR
        shops = hb.get("shops", osm in SHOPS)
        style = {"wall": hb.get("wall", "ashlar" if ashlar else "rubble"), "shops": shops,
                 "domes": hb.get("domes", DOMES.get(osm, 0)), "roof": hb.get("roof", "hipped" if osm in HIPPED else "flat"),
                 "storey": hb.get("storey", 4.2 if ashlar or shops else 3.6),
                 "parapet": hb.get("parapet", "solid")}
        rec = {"id": bid, "osm": osm, "tier": bd["tier"], "ring": r, "c": [round(q.centroid.x, 2), round(q.centroid.y, 2)],
               "tags": {k_: v for k_, v in bd["tags"].items() if k_ in ("name", "name:en", "building")},
               "base": round(g_lo - 0.6, 3), "ground": round(g_hi, 3), "top": round(g_hi + h, 3),
               "exposed": exposed, "edge_ground": eground, "style": style,
               "tint": list(hb.get("tint", TINTS[zlib.crc32(osm.encode()) % len(TINTS)])),
               "arch_pref": brng.choice(["round", "round", None]) if ashlar else brng.choice(["pointed", "pointed", "round", None])}
        inner = q.buffer(-0.32, join_style="mitre", mitre_limit=2.0)
        rec["roof"] = [poly_json(p) for p in polys_of(inner, 1.5)]
        if rec["tier"] in ("hero", "mid"):
            rec["facades"] = []
            fov = hero.facades_for(osm, r)
            for i in range(len(r)):
                if not exposed[i]:
                    continue
                ov = fov.get(i)
                a_, b_ = r[i], r[(i + 1) % len(r)]
                m_ = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
                (tx_, ty_), (nx_, ny_), L_ = edge_frame(a_, b_)
                sd_, dd_ = polyline_s(DAVID["pts"], m_)
                if 104 < m_[0] < 175 and dd_ < 8.0 and L_ > 2.2:
                    cx_, cy_ = LineString(DAVID["pts"]).interpolate(sd_).coords[0]
                    if (cx_ - m_[0]) * nx_ + (cy_ - m_[1]) * ny_ > 0.3 * max(dd_, 0.1):
                        base_ov = souq_profile(L_, eground[i], brng)
                        ov = {**base_ov, **(ov or {})}
                elif rec["tier"] == "mid" and L_ > 2.2 and souq_lines:      # other market streets
                    pm = Point(m_)
                    for j in souq_tree.query(pm.buffer(6.0)):
                        ln, (p_shop, p_can) = souq_lines[j]
                        dist = ln.distance(pm)
                        if dist > 6.0:
                            continue
                        cp = ln.interpolate(ln.project(pm))
                        if (cp.x - m_[0]) * nx_ + (cp.y - m_[1]) * ny_ <= 0.5 * max(dist, 0.1):
                            continue                                 # facade does not face this street
                        if brng.random() < p_shop:
                            base_ov = souq_profile(L_, eground[i], brng, canopy=brng.random() < p_can,
                                                   width=2 * dist)
                            ov = {**base_ov, **(ov or {})}
                        break
                fac = facades.layout(rec, i, eground[i], brng, ov)
                # balconies must not touch any wall (stepped facades, narrow alleys)
                a, b = r[i], r[(i + 1) % len(r)]
                (tx, ty), (nx, ny), _ = edge_frame(a, b)
                keep = []
                for bl in fac["balconies"]:
                    p0 = (a[0] + tx * bl["u0"] + nx * 0.05, a[1] + ty * bl["u0"] + ny * 0.05)
                    p1 = (a[0] + tx * bl["u1"] + nx * 0.05, a[1] + ty * bl["u1"] + ny * 0.05)
                    d_ = bl["depth"] + 0.3
                    quad = Polygon([p0, p1, (p1[0] + nx * d_, p1[1] + ny * d_), (p0[0] + nx * d_, p0[1] + ny * d_)])
                    if not obstacles.intersects(quad):
                        keep.append(bl)
                    else:                                   # turn the balcony door back into a window
                        for o in fac["openings"]:
                            if o["kind"] == "balcony_door" and bl["u0"] < o["u0"] < bl["u1"] and abs(o["v0"] - bl["z"] - 0.08) < 0.01:
                                o["kind"], o["v0"], o["sill"] = "window", bl["z"] + 0.9, True
                fac["balconies"] = keep
                if fac["openings"] or fac["fixtures"] or fac["decals"]:
                    rec["facades"].append(fac)
        # context buildings: flat window cards, each checked against neighbouring walls
        if True:                                   # context tier draws these; hero/mid use them in their LOD
            cells = ["glass", "glass", "glass_curtain", "shutter_green", "shutter_blue", "shutter_brown"]
            rec["cwin"] = []
            for i in range(len(r)):
                if not exposed[i]:
                    continue
                a, b = r[i], r[(i + 1) % len(r)]
                (tx, ty), (nx, ny), L = edge_frame(a, b)
                if L < 3.5:
                    continue
                nb = max(1, int((L - 1.2) // 3.2))
                for k in range(nb):
                    u = 0.6 + (L - 1.2) * (k + 0.5) / nb
                    probe = Point(a[0] + tx * u + nx * 0.3, a[1] + ty * u + ny * 0.3)
                    if inside_other(probe, bidx):
                        continue
                    z = eground[i] + 1.4
                    while z + 1.6 < g_hi + h - 1.2:
                        if brng.random() > 0.25:
                            rec["cwin"].append({"edge": i, "u": round(u, 2), "z": round(z, 2), "cell": brng.choice(cells)})
                        z += 3.6
        # skyline: rooftop rooms (some with red-tile roofs) and lime-washed domes
        rec["roof_rooms"] = []
        if style["roof"] == "flat" and rec["roof"] and osm not in LANDMARK_IDS and not HARAM.contains(q.centroid):
            rp = max(rec["roof"], key=lambda p_: Polygon(p_["ext"]).area)
            roofpoly = Polygon(rp["ext"], rp["holes"]).buffer(-0.6)
            if roofpoly.area > 90 and brng.random() < (0.45 if rec["tier"] != "context" else 0.3):
                for _ in range(15):
                    c_ = roofpoly.representative_point() if _ == 0 else Point(
                        brng.uniform(roofpoly.bounds[0], roofpoly.bounds[2]), brng.uniform(roofpoly.bounds[1], roofpoly.bounds[3]))
                    w_, d2 = brng.uniform(2.8, 4.5), brng.uniform(2.5, 3.8)
                    room = box(c_.x - w_ / 2, c_.y - d2 / 2, c_.x + w_ / 2, c_.y + d2 / 2)
                    if roofpoly.contains(room):
                        rec["roof_rooms"].append({"ring": ccw(room.exterior.coords), "h": round(brng.uniform(2.5, 3.0), 2),
                                                  "roof": "tiles" if brng.random() < 0.45 else "flat"})
                        break
            if not style["domes"] and rec["tier"] == "context" and 40 < q.area < 400 and brng.random() < 0.3:
                style["domes"] = 1
            if sid and not style["domes"] and osm not in HEIGHTS:     # vernacular field of shallow domes
                rec["dome_list"] = roofscape.domes_for(osm, roofpoly, rec["roof_rooms"], sid, brng,
                                                       roofscape.main_axis(q))
        out_b.append(rec)

    # ---------------------------------------------------------------- vaults over the covered streets
    vaults = []
    rec_tree = STRtree([Polygon(r_["ring"]) for r_ in out_b])
    for w_, ln_, kind in cov:
        hw = cov_hw[w_["id"]]
        if kind == "souq" and "width" not in w_["tags"]:
            hw = min(3.2, infill.street_halfwidth(w_["tags"], ln_, fp_tree, fp_list) + 0.1)
        n = max(1, int(math.ceil(ln_.length / 3.0)))
        pts = [ln_.interpolate(ln_.length * k / n).coords[0] for k in range(n + 1)]
        pts = [(x, y, round(street_z(x, y), 3)) for x, y in pts]
        near = [out_b[k] for k in rec_tree.query(ln_.buffer(hw + 1.0))]
        spring = 3.0 if kind == "passage" else 4.4
        crown = max(p[2] for p in pts) + spring + 1.25 * hw
        tops = sorted(r_["top"] for r_ in near)
        top = max(tops[len(tops) // 2] if (tops and kind == "passage") else crown + 0.6, crown + 0.5)
        vaults.append({"kind": kind, "name": w_["tags"].get("name:en", ""), "osm": w_["id"], "hw": round(hw, 2),
                       "spring": spring, "top": round(top, 2), "pts": [[round(x, 3), round(y, 3), z] for x, y, z in pts]})
    print("vaults:", len(vaults), "covered ways, %.0f m" % sum(ln_.length for _, ln_, _ in cov))

    # ---------------------------------------------------------------- street-name plaques from OSM names
    signs_meta = {}
    sj = ROOT / "data/textures/gen/signs.json"
    if sj.exists():
        signs_meta = json.loads(sj.read_text())["signs"]
    plaque_of = {"David Street": "plaque_david", "Latin Patriarchate Road": "plaque_latin",
                 "Greek Catholic Patriarchate Street": "plaque_greek", "The Armenian Patriarchate Street": "plaque_armenian",
                 "Omar Ibn El-Khattab Square": "plaque_omar", "Christian Quarter Street": "plaque_christian"}
    anchors = []
    for w in d["ways"]:
        if "multipolygon" in w:
            continue
        cell = plaque_of.get(w["tags"].get("name:en"))
        if not cell or cell not in signs_meta:
            continue
        pts_in = [p for p in w["pts"] if box(*POC).contains(Point(p))]
        if not pts_in:
            continue
        for p in {tuple(pts_in[0]), tuple(pts_in[-1])}:
            anchors.append((cell, p))
    placed_cells = []
    for cell, p in anchors:
        best = None
        for rec in out_b:
            if rec["tier"] == "context":
                continue
            r = rec["ring"]
            for fac in rec.get("facades", []):
                i = fac["edge"]
                a, b = r[i], r[(i + 1) % len(r)]
                (tx, ty), (nx, ny), L = edge_frame(a, b)
                if L < 2.5:
                    continue
                u = max(0.7, min(L - 0.7, (p[0] - a[0]) * tx + (p[1] - a[1]) * ty))
                q = (a[0] + tx * u, a[1] + ty * u)
                dist_ = math.dist(q, p)
                facing = ((p[0] - q[0]) * nx + (p[1] - q[1]) * ny) / (dist_ or 1)
                if dist_ < 9 and facing > 0.2 and (best is None or dist_ < best[0]):
                    best = (dist_, fac, u, L)
        if best is None or (cell, round(best[2])) in placed_cells:
            continue
        _, fac, u, L = best
        meta = signs_meta[cell]
        z = fac["ground"] + 2.75
        for _ in range(12):                                   # slide clear of openings
            if not any(o["u0"] - 0.5 < u < o["u1"] + 0.5 and o["v0"] < z + meta["h_m"] and o["v1"] > z for o in fac["openings"]):
                break
            u = min(L - 0.7, u + 0.6) if u < L / 2 else max(0.7, u - 0.6)
        fac["fixtures"].append({"type": "sign", "cell": cell, "u": round(u, 2), "z": round(z, 2),
                                "w": meta["w_m"], "h": meta["h_m"]})
        placed_cells.append((cell, round(u)))
    print("street plaques:", sorted(c for c, _ in placed_cells))

    # ---------------------------------------------------------------- dressing
    ctxinfo = {"buildings": out_b, "road": road, "road_line": ROAD, "paving": paving_all, "street": street,
               "road_area": road_area, "obstacles": obstacles, "moat": moat, "cit_outer": cit_outer,
               "cit_outer_r": cit_outer_r, "moat_edges": moat_edges, "hero": HERO_ZONE, "david": DAVID,
               "street_z": street_z, "kerb": KERB, "gate": GATEHOUSE, "walls": CITY_WALLS, "steps": steps,
               "courtyard": courtyard, "haram": HARAM, "landmark_ids": LANDMARK_IDS,
               "woods": [Polygon(w["pts"]).buffer(0) for w in d["ways"] if w.get("closed") and len(w.get("pts") or []) > 3
                         and (w["tags"].get("landuse") in ("forest", "orchard") or w["tags"].get("natural") in ("wood", "scrub")
                              or w["tags"].get("leisure") in ("park", "garden"))
                         and not Polygon(w["pts"]).buffer(0).intersects(PLATFORM)]}
    props, cables, ground_decals, beams = dressing.dress(ctxinfo, rng)
    for pp in PROFILE_PROPS:                                   # notable furniture from the sector profiles
        x, y = pp["p"][:2]
        props.append({"type": pp["type"], "p": [round(x, 3), round(y, 3), round(street_z(x, y), 3)],
                      "rot": pp.get("rot", 0.0), "s": pp.get("s", 1.0), "col": pp.get("col", True), "r": pp.get("r", 0.5)})

    # ---------------------------------------------------------------- the rest of the wall circuit (OSM)

    spec = {
        "poc_box": POC, "context_box": CONTEXT,
        "walls_generic": walls_generic,
        "vaults": vaults,
        "buildings": out_b,
        "gatehouse": GATEHOUSE, "city_walls": CITY_WALLS,
        "citadel": {"outer": cit_outer_r, "mass": [list(p) for p in cit_mass_r], "inner": cit_inner_r,
                    "moat_edges": moat_edges, "wall_h": CITADEL_WALL_H, "moat_depth": MOAT_DEPTH, "towers": TOWERS},
        "ground": ground, "kerbs": kerbs, "steps": steps,
        "props": props, "cables": cables, "ground_decals": ground_decals, "beams": beams,
        "spawn": SPAWN,
        "sources": {
            "footprints": "OpenStreetMap contributors (ODbL), API 0.6 map call",
            "heights": "estimated from Wikimedia Commons geotagged photos + OSM building:levels",
            "terrain": "AWS Terrain Tiles (SRTM) checked; too coarse, ground hand-modelled",
        },
    }
    write_sectors(spec)
    nt = {t: sum(1 for b in out_b if b["tier"] == t) for t in ("hero", "mid", "context")}
    nf = sum(len(b.get("facades", [])) for b in out_b)
    no = sum(len(f["openings"]) for b in out_b for f in b.get("facades", []))
    print("buildings %s  facades %d  openings %d  steps %d  ground tris %d  kerbs %d  props %d  cables %d" %
          (nt, nf, no, len(steps), sum(len(g["tris"]) for g in ground), len(kerbs), len(props), len(cables)))


if __name__ == "__main__":
    main()
