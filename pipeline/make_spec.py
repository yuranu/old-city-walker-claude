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
import ast
import functools
import os
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
from shapely.ops import substring

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
WILSON_HALL = Polygon([(621.91, 30.53), (646.06, 35.24), (640.68, 62.55), (639.28, 62.27), (626.48, 59.77),
                       (629.03, 46.85), (619.07, 44.91)])
# the Dome of the Rock's upper platform (landmarks_haram.PLATFORM, built PLAT_H = 5.1 m above the esplanade
# with retaining walls down below it): no esplanade ground inside, 0.5 m in from its walls. That ground was
# a sealed void under the platform top, and a teleport (lowest floor with headroom) stood players in it
DOME_PLATFORM = Polygon([
    (695.31, 87.30), (695.56, 86.02), (712.71, 89.35), (713.69, 84.34), (724.48, 86.29), (723.96, 89.05),
    (726.64, 89.56), (727.16, 86.80), (741.11, 89.48), (747.93, 90.70), (791.29, 97.93), (797.50, 99.05),
    (797.68, 87.31), (817.91, 91.95), (816.67, 164.42), (815.22, 174.28), (814.49, 210.13), (813.17, 210.16),
    (813.41, 240.38), (813.50, 265.07), (772.30, 259.75), (772.04, 261.88), (762.12, 260.64), (762.71, 255.95),
    (755.36, 255.03), (755.03, 257.60), (730.80, 254.58), (730.53, 256.69), (718.00, 255.13), (718.72, 249.45),
    (713.28, 248.78), (712.84, 252.34), (673.47, 247.42), (675.55, 230.87), (662.27, 229.22), (662.51, 227.33),
    (660.20, 227.04), (670.43, 181.88), (672.90, 182.35), (673.68, 178.19), (671.25, 177.73), (677.71, 144.88),
    (696.09, 148.79), (699.21, 134.32), (680.61, 131.10), (683.20, 116.88), (689.24, 86.12)])
GROUND_HOLES = []        # (DOME_PLATFORM.buffer(-0.5) once: the platform has no retaining wall beside the qanatir
                         #  stairs, and with no ground under it sky showed through; Player.teleport skips the void)
                         # (Wilson's Arch hall: paved at Chain Street level instead, see LOCAL_FLATS; a hole
                         #  left gaps between the hall's roof and the walls around it)
# sunken courts: paving at street level + dz (the Golden Gate's court, 4.5 m below the esplanade;
# retaining walls, railing and stairs by landmarks_haram)
SUNKEN = [{"poly": box(884.0, 249.0, 892.0, 266.0), "dz": -4.5, "name": "golden_gate_court"}]


# footprints that OSM draws across a street: clip them back to the street wall (way id, half-width)
CLIP_STREETS = {"w1022672085": [(26492706, 2.2)]}     # Holy Sepulchre over Christian Quarter St
# level areas the terrain field does not know about: (OSM way, point whose street level they take)
LOCAL_FLATS = [(612045223, (208.2, 183.4)),           # Holy Sepulchre parvis, at the main door
               # the Western Wall prayer-area level carried north to the front of Wilson's Arch hall
               (Polygon([(621.91, 30.53), (646.06, 35.24), (647.21, 29.35), (623.06, 24.64)]), -43.58),
               # paving over Wilson's Arch hall at Chain Street level (the hall's roof sits 3 cm below)
               (WILSON_HALL, (633.0, 61.0)),
               # the Austrian Hospice compound (retaining wall w375040920): a garden terrace ~5 m over the Via
               # Dolorosa at its gatehouse (Street View: the terrace and its planters level with the gate's roof)
               (375040920, (424.0, 374.0, 5.0)),
               # Dung Gate: the road runs level through the gate and its forecourt (Street View); the terrain
               # fell 20% straight through the passage
               (Polygon([(611.0, -189.0), (640.0, -187.0), (646.0, -211.0), (617.0, -214.0)]), (627.9, -199.3, 0.0))]


# covered streets: passages under buildings (OSM tunnel=yes|building_passage, covered=yes) are carved
# out of the footprints and vaulted; the covered souqs are vaulted between their facades
COVERED_SOUQS = {"Suq Al La'h'hamin", "Suq Al Attarin", "Suq Al-Khawajat", "Suq El-Quatta"}


def souq_key(w):
    """SOUQ_STREETS key of a way (its OSM id as a string, or its name:en), or None."""
    if str(w["id"]) in SOUQ_STREETS:
        return str(w["id"])
    n = w["tags"].get("name:en")
    return n if n in SOUQ_STREETS else None


LANE_SKIP = {None, "corridor", "elevator", "proposed", "construction"}     # highway values that are no lane


def layer_of(t):
    try:
        return int(t.get("layer", "0") or 0)
    except ValueError:
        return 0


def lines_of(g):
    """The LineStrings of a (multi)line or collection result, contiguous parts merged."""
    from shapely.ops import linemerge
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "MultiLineString":
        g = linemerge(g)
        return [g] if g.geom_type == "LineString" else list(g.geoms)
    return [s for h in getattr(g, "geoms", []) for s in lines_of(h)]


def stretches(ln, area, gap=1.0):
    """The stretches of line ln inside area, joined across gaps shorter than gap (the slits between
    neighbouring footprints)."""
    iv = sorted(sorted((ln.project(Point(s.coords[0])), ln.project(Point(s.coords[-1]))))
                for s in lines_of(ln.intersection(area)))
    out = []
    for a, b in iv:
        if out and a - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [substring(ln, a, b) for a, b in out if b - a > 0.01]


def widen(ln, part, d):
    """The stretch of ln covering part (a piece of it), d metres longer at both ends: a corridor
    carved along it also clears where the footprint edge crosses the lane at a slant."""
    a, b = sorted((ln.project(Point(part.coords[0])), ln.project(Point(part.coords[-1]))))
    return substring(ln, max(0.0, a - d), min(ln.length, b + d))


def covered_ways(d):
    out = []
    for w in d["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if not t.get("highway") or len(pts) < 2 or t.get("area") == "yes":
            continue
        named = t.get("name:en") in COVERED_SOUQS or w["id"] in COVERED_IDS
        lay = int(t.get("layer", "0") or 0)
        under = t.get("tunnel") in ("yes", "building_passage") or t.get("covered") == "yes" or lay == -1
        if named or (under and infill.street_level(t)):       # layer -1 streets pass under rooms: passages
            out.append((w, LineString(pts), "souq" if named else "passage"))
    return out


def registered_ids(src):
    """OSM ids a landmark module registers, read from its source (it only imports inside Blender):
    the LANDMARKS dict literal (keys may be module-level string names), LANDMARKS["w…"] = …, and
    `for _q in <tuple literal or module-level tuple>: LANDMARKS[_q] = …`."""
    body, consts, ids = ast.parse(src).body, {}, set()

    def strs(node):
        if isinstance(node, ast.Name):
            return consts.get(node.id, [])
        try:
            v = ast.literal_eval(node)
        except (ValueError, TypeError, SyntaxError):
            return []
        return [s for s in (v if isinstance(v, (tuple, list, set)) else [v]) if isinstance(s, str)]

    def lm_key(tg):                          # the key node of a LANDMARKS[...] target, or None
        return tg.slice if isinstance(tg, ast.Subscript) and getattr(tg.value, "id", None) == "LANDMARKS" else None
    for st in body:
        if isinstance(st, ast.Assign):
            for tg in st.targets:
                if getattr(tg, "id", None) == "LANDMARKS" and isinstance(st.value, ast.Dict):
                    ids |= {s for k in st.value.keys if k is not None for s in strs(k)}
                elif isinstance(tg, ast.Name) and isinstance(st.value, (ast.Tuple, ast.List, ast.Constant)):
                    consts[tg.id] = strs(st.value)
                elif lm_key(tg) is not None:
                    ids |= set(strs(lm_key(tg)))
        elif isinstance(st, ast.For) and isinstance(st.target, ast.Name):
            if any(isinstance(s, ast.Assign) and any(getattr(lm_key(t), "id", None) == st.target.id for t in s.targets)
                   for s in st.body):
                ids |= set(strs(st.iter))
    return ids


def landmark_ids(modules=None):
    """OSM ids registered by the landmark builders (blender/landmarks_*.py LANDMARKS). The registry
    as Blender imports it comes from data/landmark_ids.json (blender/dump_landmarks.py, run by
    build.sh); each module's source is parsed as well, so a missing, stale or partial dump (a module
    that failed to import there) still yields every id the source lists."""
    fns = [ROOT / "blender" / (m + ".py") for m in modules] if modules else sorted((ROOT / "blender").glob("landmarks_*.py"))
    dump = {}
    try:
        dump = json.loads((ROOT / "data/landmark_ids.json").read_text()).get("modules", {})
    except (OSError, ValueError):
        pass
    ids = set()
    for fn in fns:
        ids |= set(dump.get(fn.stem) or [])
        if fn.exists():
            try:
                ids |= registered_ids(fn.read_text())
            except SyntaxError as e:                 # a module mid-edit by another worker
                print("landmark ids: %s not parsed (%s)" % (fn.name, e))
    return ids


def gate_ids():
    """OSM ids of the gates (blender/landmarks_gates.py LANDMARKS)."""
    return landmark_ids(["landmarks_gates"])


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
COVERED_IDS, PROFILE_OPEN, PROFILE_PROPS, PROFILE_REMOVED = set(), [], [], set()
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
    PROFILE_REMOVED.update(_pr.get("remove_buildings", {}).keys())
    PROFILE_PROPS += _pr.get("props", [])
SKIP |= PROFILE_REMOVED                  # (and infill keeps their ground open: they are not buildings)



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
    # steps live in the base with the ground they are cut into, so the two always load together
    for key in ("cables", "beams"):
        for it in spec[key]:
            m = ((it["a"][0] + it["b"][0]) / 2, (it["a"][1] + it["b"][1]) / 2)
            per[sector_or_nearest(*m)][key].append(it)
    for v in spec.get("vaults", []):
        m = v["pts"][len(v["pts"]) // 2]
        per[sector_or_nearest(m[0], m[1])]["vaults"].append(v)
    base = {k: spec[k] for k in ("poc_box", "context_box", "ground", "kerbs", "gatehouse", "city_walls", "citadel",
                                  "walls_generic", "retaining", "spawn", "sources", "ground_holes", "osm_walls", "bridges")}
    base.update({"buildings": base_b, "props": base_props, "ground_decals": base_dec, "steps": spec["steps"], "cables": [],
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
        legacy[k] = base[k] + per["s00_jaffa"][k] if k in ("props", "ground_decals", "steps") else per["s00_jaffa"][k]
    write_json(LEGACY_SPEC, legacy)
    print("sectors:", ", ".join("%s %d" % (i["id"], i["buildings"]) for i in index), "| base context", len(base_b))


# OSM ways tagged city_wall that are not a crenellated wall: the Haram enclosure boundary on the west
# and north sides (lined with porticoes and madrasas) and the Little Western Wall (landmarks_haram)
WALL_LANDMARKS = {"w817206833"}      # the Western Wall (landmarks_haram builds its face)
NOT_WALLS = {26554724, 291970363}
HARAM_WALL_H = 7.0     # the Haram's east and south walls: merlons ~7 m above the esplanade (Golden Gate photos)


def generic_walls(d, cit_outer, gate_poly, seg_len=15.0, height=11.5, thick=3.0):
    """City-wall segments from OSM outside the hand-modelled Jaffa Gate stretch: terrain-following,
    outside (beyond the walls) on the right-hand side of each segment."""
    from shapely.ops import linemerge
    lines = unary_union([LineString(w["pts"]) for w in d["ways"]
                         if "multipolygon" not in w and w["tags"].get("barrier") == "city_wall"
                         and w["id"] not in NOT_WALLS])
    # wall faces built by landmark modules (the Western Wall): the generic circuit along them would sit
    # on the same plane and flicker
    own = [Polygon(b["outer"][0]).buffer(2.0) for b in d["buildings"] if b["id"] in WALL_LANDMARKS and b.get("outer")]
    custom = unary_union(own + [LineString(w["pts"]).buffer(w["thick"] / 2 + 2.0) for w in CITY_WALLS]
                         + [gate_poly.buffer(3.0), cit_outer.buffer(3.0)])
    rest = lines.difference(custom)
    rest = linemerge(rest) if rest.geom_type == "MultiLineString" else rest
    inside = CITY.union(HARAM).buffer(-0.5)
    out = []
    taken = []                     # OSM draws some stretches twice (city wall + Haram enclosure, faces)
    for li, ln in enumerate(sorted(getattr(rest, "geoms", [rest]), key=lambda g: -g.length)):
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
            # the segment it joins on the same line does not count: after a sharp turn (a tower
            # corner) this one runs along that one's flat end cap
            if any(seg.intersection(t_).length > 0.4 * L for li_, end_, t_ in taken
                   if (li_, end_) != (li, a) and t_.intersects(seg)):
                continue
            taken.append((li, b, seg.buffer(thick + 0.5, cap_style="flat")))
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if inside.contains(Point(m[0] + nx * 5, m[1] + ny * 5)):     # right side must be outside
                a, b = b, a
                nx, ny = -nx, -ny
            z_in = street_z0(m[0] - nx * 5, m[1] - ny * 5)             # (not the sunken court level)
            z_out = street_z0(m[0] + nx * 5, m[1] + ny * 5)
            h = HARAM_WALL_H if HARAM.buffer(-2.0).contains(Point(m[0] - nx * 5, m[1] - ny * 5)) else height
            # foot below the lowest ground near the whole segment (the midpoint 5 m out missed the slope
            # falling away at the ends below a bastion: sky showed under the wall)
            z_low = min([z_in, z_out] + [street_z0(p_[0] + nx * d_, p_[1] + ny * d_)
                                         for p_ in (a, b, m) for d_ in (-10.0, -3.0, 0.0, 3.0, 10.0)])
            out.append({"a": [round(a[0], 2), round(a[1], 2)], "b": [round(b[0], 2), round(b[1], 2)],
                        "z0": round(z_low - 2.5, 2), "z1": round(z_in + h, 2), "thick": thick})
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


_FLATS = []                                    # [(polygon, z)] local flats, filled by setup_flats()
ALL_FLATS = []                                 # terrain flats + local flats: the level areas
OPEN_EDGES = {}                                # id(level area) -> the part of its outline it eases across, or None
SHRUNK = {}                                    # id(level area) -> the area 2 cm in from its outline
PAIR_EDGES = []                                # [(edge geometry, z of the higher-priority flat, smaller flat, its z)]
BLEND_SLOPE = 0.3                              # around a level area the ground eases into the terrain
                                               # over |dz| / BLEND_SLOPE metres (3-25 m)


def setup_flats(d):
    for wid, at in LOCAL_FLATS:                # (OSM way, point it takes its level from) or (polygon, z)
        if isinstance(wid, Polygon):
            if isinstance(at, tuple) and len(at) == 3:            # (x, y, dz): dz above the street at (x, y)
                _FLATS.append((wid, (float(_terrain.street_z(at[0], at[1])) if _terrain else 0.0) + at[2]))
            else:
                _FLATS.append((wid, float(at) if not isinstance(at, tuple) else float(_terrain.street_z(*at)) if _terrain else 0.0))
            continue
        w = next((w_ for w_ in d["ways"] if w_["id"] == wid), None)
        if w and _terrain is not None:
            z_ = float(_terrain.street_z(at[0], at[1])) + (at[2] if len(at) == 3 else 0.0)
            _FLATS.append((Polygon(w["pts"]).buffer(0), z_))
    _osm_fp = [Polygon(b["outer"][0]).buffer(0) for b in d["buildings"] if b.get("outer") and len(b["outer"][0]) > 2]
    _fp_tree = STRtree(_osm_fp)

    def grown(poly):
        """A plaza is level right up to the buildings around it: grow a (non-Haram) level area into the
        open ground within 12 m, stopping at building faces, so the easing starts beyond them."""
        if poly.area > 20000 or poly.equals(WILSON_HALL):
            return poly
        ring = poly.buffer(12.0)
        near = [_osm_fp[k] for k in _fp_tree.query(ring)]
        g = ring.difference(unary_union(near)) if near else ring
        parts = [q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon" and q.intersects(poly)]
        return unary_union(parts + [poly]).buffer(0) if parts else poly
    ALL_FLATS[:] = sorted([(grown(fp_), float(fz_)) for fp_, fz_ in (_terrain._runtime()[2] if _terrain else [])] + list(_FLATS),
                          key=lambda f_: f_[0].area)      # the most specific (smallest) level area wins where they overlap
    for poly, _ in ALL_FLATS:
        prepare(poly)
    # a level area eases into the terrain only across its open edges: not where buildings or walls line
    # it (the lanes outside the Haram's walls keep their own level instead of climbing to the esplanade)
    closers = [Polygon(b["outer"][0]).buffer(0) for b in d["buildings"] if b.get("outer") and len(b["outer"][0]) > 2]
    closers += [LineString(w["pts"]).buffer(1.0) for w in d["ways"] if len(w.get("pts") or []) > 1 and
                (w["tags"].get("barrier") in ("city_wall", "wall", "retaining_wall") or w["tags"].get("historic") == "citywalls")]
    closed = unary_union(closers).buffer(0.3)       # (1 m closed the narrow lanes that enter a plaza between buildings)
    OPEN_EDGES.clear()
    SHRUNK.clear()
    for poly, _ in ALL_FLATS:
        oe = poly.boundary.difference(closed)
        OPEN_EDGES[id(poly)] = oe if not oe.is_empty and oe.length > 0.5 else None
        SHRUNK[id(poly)] = poly.buffer(-0.02)
        prepare(SHRUNK[id(poly)])
    street_z0.cache_clear()
    street_z.cache_clear()


STAIR_FIELD = None                             # set by set_stair_field() once the flights are final
STAIR_REACH = 10.0                             # the ground follows a flight this far out at most
STAIR_SLOPE = 0.35                             # ... blending back to the terrain no steeper than this


def set_stair_field(recs):
    """The ground beside and past each flight follows the flight: a plane through each tread's centre
    falling along the flight at the flight's own grade, clamped to its top and bottom treads (a level
    landing at each end, where the cross street meets it), blended back into the surface over
    |dz| / STAIR_SLOPE metres (1.5-10 m). Tread sides then stand at most half a riser proud of the
    ground beside them, and a flight meeting a sloping street meets it at its own level."""
    global STAIR_FIELD
    if not recs:
        STAIR_FIELD = None
        return
    runs = {}
    for r_ in recs:
        runs.setdefault(r_["run"], []).append(r_)
    polys, top, cx, cy, dx, dy, slope, zlo, zhi = [], [], [], [], [], [], [], [], []
    for rr in runs.values():
        d_ = np.array(rr[0]["dir"], float)
        us = [np.dot(np.array(r_["poly"].centroid.coords[0]), d_) for r_ in rr]
        tops = [r_["top"] for r_ in rr]
        k0, k1 = int(np.argmin(us)), int(np.argmax(us))
        g = (tops[k0] - tops[k1]) / (us[k1] - us[k0]) if us[k1] - us[k0] > 0.3 else 0.0
        for r_ in rr:
            c = r_["poly"].centroid
            polys.append(r_["poly"])
            top.append(r_["top"]), cx.append(c.x), cy.append(c.y)
            dx.append(r_["dir"][0]), dy.append(r_["dir"][1]), slope.append(max(0.0, g))
            zlo.append(min(tops)), zhi.append(max(tops))
    STAIR_FIELD = {"tree": STRtree(polys), "polys": np.array(polys, dtype=object), "top": np.array(top), "cx": np.array(cx), "cy": np.array(cy),
                   "dx": np.array(dx), "dy": np.array(dy), "slope": np.array(slope),
                   "zlo": np.array(zlo), "zhi": np.array(zhi)}
    street_z0.cache_clear()
    street_z.cache_clear()


def _stair_conform(xs, ys, out):
    """Every tread within reach votes (weight 1 / (d + 0.3)^2) for its plane's height at the point: between
    two flights at different levels the ground ramps from one to the other (the nearest tread alone
    switched there and built cliffs). Conforming evens out what a flight's cheeks and landings show (under a
    metre): where the flights' level is more than 0.5 m off the surface it fades out, gone by 1.5 m (a flight
    in a cutting or on a bank keeps its ground; pulling steep terrain to the flight built spikes)."""
    F = STAIR_FIELD
    pts = shapely.points(xs, ys)
    ip, it = F["tree"].query(pts, predicate="dwithin", distance=STAIR_REACH)
    if len(ip) == 0:
        return out
    d = shapely.distance(F["polys"][it], pts[ip])
    x, y = xs[ip], ys[ip]
    zs = F["top"][it] - ((x - F["cx"][it]) * F["dx"][it] + (y - F["cy"][it]) * F["dy"][it]) * F["slope"][it]
    zs = np.clip(zs, F["zlo"][it], F["zhi"][it])
    wt = 1.0 / (d + 0.3) ** 2
    n = len(xs)
    sw = np.bincount(ip, wt, n)
    has = sw > 0
    zmix = np.bincount(ip, wt * zs, n)[has] / sw[has]
    dmin = np.full(n, np.inf)
    np.minimum.at(dmin, ip, d)
    dmin = dmin[has]
    zo = out[has]
    dz = np.abs(zmix - zo)
    D = np.clip(dz / STAIR_SLOPE, 1.5, STAIR_REACH)
    w = np.clip(dmin / D, 0.0, 1.0)
    w = w * w * (3.0 - 2.0 * w)
    w = np.maximum(w, np.clip((dz - 0.5) / 1.0, 0.0, 1.0))      # banks and cuttings keep their ground
    near = d < 2.0                                               # flights within 2 m a metre apart in level:
    zhi_ = np.full(n, -np.inf)                                   # a wall stands between them, not a ramp
    zlo_ = np.full(n, np.inf)
    np.maximum.at(zhi_, ip[near], zs[near])
    np.minimum.at(zlo_, ip[near], zs[near])
    split = (zhi_ - zlo_)[has] > 1.0
    w = np.where(split, 1.0, w)
    res = out.copy()
    res[has] = zmix + (zo - zmix) * w
    return res


def surface_z_v(xs, ys, prefer=None, ease_from=None):
    """THE walkable surface, one continuous function used by ground, steps, buildings and props:
    level areas exactly level, the terrain elsewhere, and around each level area a smooth easing
    from its level into the terrain over |dz| / BLEND_SLOPE metres. No discontinuity anywhere, so
    the ground mesh cannot open holes or build cliffs/pyramids at the edges of level areas."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    zt = terrain_z_v(xs, ys)
    if not ALL_FLATS:
        return zt
    pts = shapely.points(xs, ys)
    inside_any = np.zeros(xs.shape, bool)
    out = zt.copy()
    best = np.full(xs.shape, np.inf)
    order = ALL_FLATS
    if prefer is not None:              # a piece of this flat: its own outline counts as inside it
        order = [f_ for f_ in ALL_FLATS if f_[0] is prefer] + [f_ for f_ in ALL_FLATS if f_[0] is not prefer]
    owner = np.full(xs.shape, -1)
    for poly, fz in order:
        if poly is prefer:              # a piece of this level area: its outline counts as inside it
            inside = shapely.contains_xy(poly, xs, ys) | (shapely.distance(poly, pts) < 0.02)
        else:                           # anyone else: the outline belongs to the ground outside (where the
            inside = shapely.contains_xy(SHRUNK[id(poly)], xs, ys)    # area does not ease, a step is there)
        out = np.where(inside & ~inside_any, fz, out)
        owner = np.where(inside & ~inside_any, id(poly), owner)
        inside_any |= inside
    for edge, zbig, small, zsmall in PAIR_EDGES:     # two level areas meeting in open ground: the smaller
        ins = owner == id(small)                    # one ramps up/down to the other along that edge
        d = shapely.distance(edge, pts)
        D = max(3.0, min(40.0, abs(zbig - zsmall) / BLEND_SLOPE))
        m = ins & (d < D)
        out = np.where(m, zbig + (zsmall - zbig) * (d / D), out)
    for poly, fz in ALL_FLATS:                 # outside every flat: ease from the nearest one
        if poly is WILSON_HALL or OPEN_EDGES.get(id(poly)) is None:   # a raised deck, a walled area: no easing
            continue
        d = shapely.distance(OPEN_EDGES[id(poly)], pts)
        D = np.clip(np.abs(fz - zt) / BLEND_SLOPE, 3.0, 40.0)
        w = np.clip(d / D, 0.0, 1.0)                 # linear: the slope never exceeds |dz| / D
        near = (~inside_any) & (d < D) & (d / D < best)
        out = np.where(near, fz + (zt - fz) * w, out)
        best = np.where(near, d / D, best)
    if ease_from is not None:                  # a piece of an easing zone: eased from its own level area only
        fz = next(z_ for p_, z_ in ALL_FLATS if p_ is ease_from)
        d = shapely.distance(OPEN_EDGES[id(ease_from)], pts)
        D = np.clip(np.abs(fz - zt) / BLEND_SLOPE, 3.0, 40.0)
        m = (~inside_any) & (d < D)
        out = np.where(m, fz + (zt - fz) * np.clip(d / D, 0.0, 1.0), out)
    if STAIR_FIELD is not None:            # fading out over the first 3 m inside a level area (applied in it,
        conf = _stair_conform(xs, ys, out)   # it folded the Western Wall plaza into creases round the flights;
        k = np.ones(xs.shape)                # cut at its edge, the jump built spikes on the JQ escarpment)
        for poly, _ in ALL_FLATS:
            m = owner == id(poly)
            if m.any():
                k[m] = np.clip(1.0 - shapely.distance(poly.boundary, pts[m]) / 3.0, 0.0, 1.0)
        out = out + (conf - out) * k
    return out


EASE_ZONES = []                                # [(polygon, level area)]: where easing bands meet


def setup_ease_zones(cell=0.5):
    """Where the easing bands of two level areas meet, the surface switches from easing out of one to
    easing out of the other: a jump (the Mughrabi ramp beside the prayer area, 5-9 m). The ground is
    split along that switch line, each side eased from its own level area, so the jump is a clean
    vertical edge (closed by seal_cracks) instead of triangles spanning it."""
    EASE_ZONES.clear()
    fl = [(p_, z_) for p_, z_ in ALL_FLATS if p_ is not WILSON_HALL and OPEN_EDGES.get(id(p_)) is not None]
    bands = [OPEN_EDGES[id(p_)].buffer(40.0) for p_, _ in fl]
    allf = unary_union([p_ for p_, _ in fl])
    zones = []
    for i in range(len(fl)):
        for j in range(i + 1, len(fl)):
            if bands[i].intersects(bands[j]):
                ov = bands[i].intersection(bands[j]).difference(allf)
                if not ov.is_empty:
                    zones.append(ov)
    if not zones:
        return
    zone = unary_union(zones)
    x0, y0, x1, y1 = zone.bounds
    gx, gy = np.meshgrid(np.arange(x0, x1, cell) + cell / 2, np.arange(y0, y1, cell) + cell / 2)
    gx, gy = gx.ravel(), gy.ravel()
    k = shapely.contains_xy(zone, gx, gy)
    gx, gy = gx[k], gy[k]
    pts = shapely.points(gx, gy)
    zt = terrain_z_v(gx, gy)
    best = np.full(gx.shape, np.inf)
    own = np.full(gx.shape, -1)
    for i, (p_, fz) in enumerate(fl):
        r = shapely.distance(OPEN_EDGES[id(p_)], pts) / np.clip(np.abs(fz - zt) / BLEND_SLOPE, 3.0, 40.0)
        m = (r < 1.0) & (r < best)
        own[m], best[m] = i, r[m]
    for i, (p_, fz) in enumerate(fl):
        m = own == i
        if not m.any() or m.all():
            continue
        cells = shapely.box(gx[m] - cell / 2, gy[m] - cell / 2, gx[m] + cell / 2, gy[m] + cell / 2)
        poly = shapely.coverage_union_all(cells).buffer(0.01).buffer(-0.01).simplify(cell * 0.7) \
            .buffer(cell, join_style="mitre")       # overlapping (the first zone takes the overlap): no slivers between
        pieces = [q for q in getattr(poly, "geoms", [poly]) if q.geom_type == "Polygon" and q.area > 4.0]
        if pieces:
            EASE_ZONES.append((unary_union(pieces).segmentize(1.0), p_))
    for ez_, _ in EASE_ZONES:
        prepare(ez_)
    street_z0.cache_clear()
    street_z.cache_clear()
    print("ease zones: %d (%s m2)" % (len(EASE_ZONES), round(sum(z_.area for z_, _ in EASE_ZONES))))



def osm_walls(d, buildings, skip_ids=()):
    """OSM barrier=wall / retaining_wall lines (compound walls, garden and terrace walls: 5 km of them
    were not built at all, and every walled compound stood open to the street): segments of 2 m along
    each line outside the building footprints, a 2.6 m gap where a mapped path crosses. A wall stands
    3 m (or its OSM height) above the higher ground beside it; a retaining wall from the low side up to
    a 1.1 m parapet over the high side, and at least 4.5 m over the low side when it closes a ring (a compound). Lines inside the Haram are its builders' own."""
    # (clear of the footprints by 8 cm, the ends cut there run 25 cm on into the building: a wall line drawn
    #  along a building's face, the Austrian Hospice's on its gatehouse front, stood in front of the facade)
    fp = unary_union([bd["poly"] for bd in buildings]).buffer(0.08)
    paths = [LineString(w_["pts"]) for w_ in d["ways"] if w_["tags"].get("highway") and len(w_.get("pts") or []) > 1]
    ptree = STRtree(paths) if paths else None
    ctx = box(*CONTEXT)
    # walls standing inside a mapped square or pedestrian area are partitions and low walls (the Western Wall
    # prayer-area partition stood 3.4 m and hid the Wall; Street View: waist-high)
    plazas = unary_union([Polygon(w_["pts"]).buffer(0) for w_ in d["ways"] if w_.get("closed") and len(w_.get("pts") or []) > 3
                          and (w_["tags"].get("place") in ("square", "plaza")
                               or (w_["tags"].get("highway") == "pedestrian" and w_["tags"].get("area") == "yes"))]
                         or [Polygon()])
    out = []
    for w_ in d["ways"]:
        t_ = w_["tags"]
        kind = t_.get("barrier")
        pts_ = w_.get("pts") or []
        if kind not in ("wall", "retaining_wall") or len(pts_) < 2 or w_["id"] in skip_ids:
            continue
        ln = LineString(pts_)
        if not ctx.contains(ln.centroid) or HARAM.buffer(2.0).contains(ln.centroid):
            continue
        cuts = [fp]
        if ptree is not None:
            for k in ptree.query(ln):
                x_ = paths[k].intersection(ln)
                for g_ in getattr(x_, "geoms", [x_]):
                    if g_.geom_type == "Point":
                        cuts.append(g_.buffer(1.3))
        # a closed retaining-wall ring is a compound's enclosure: at least 4.5 m over its low side even where
        # the levels differ little (the Austrian Hospice wall on El-Wad hides the garden, only palms show over
        # it), a parapet over a terrace higher than that; an open retaining wall ends in a parapet
        ring_ = bool(w_.get("closed")) and len(pts_) > 3
        try:
            h_tag = float(str(t_.get("height", "")).replace("m", "").strip())
        except ValueError:
            h_tag = None
        if h_tag is None and kind == "wall" and plazas.contains(ln.interpolate(0.5, normalized=True)):
            h_tag = 1.2
        for seg in lines_of(ln.difference(unary_union(cuts))):
            if seg.length < 0.8:
                continue
            seg = seg.segmentize(2.0)
            cs = list(seg.coords)
            for i_, j_ in ((0, 1), (-1, -2)):          # an end stopped by a building runs on into it
                if fp.distance(Point(cs[i_])) < 0.02:
                    dx_, dy_ = cs[i_][0] - cs[j_][0], cs[i_][1] - cs[j_][1]
                    l_ = math.hypot(dx_, dy_) or 1.0
                    cs[i_] = (cs[i_][0] + dx_ / l_ * 0.25, cs[i_][1] + dy_ / l_ * 0.25)
            for a_, b_ in zip(cs, cs[1:]):
                (_, _), (nx_, ny_), L_ = edge_frame(a_, b_)
                if L_ < 0.05:
                    continue
                z0, z1 = [], []
                for p_ in (a_, b_):
                    zl = street_z(p_[0] - nx_ * 0.9, p_[1] - ny_ * 0.9)
                    zr = street_z(p_[0] + nx_ * 0.9, p_[1] + ny_ * 0.9)
                    z0.append(round(min(zl, zr) - 0.4, 2))
                    if kind != "retaining_wall":
                        top = max(zl, zr) + (h_tag or 3.0)
                    elif ring_:
                        top = max(max(zl, zr) + 1.1, min(zl, zr) + 4.5)
                    else:
                        top = max(zl, zr) + 1.1
                    z1.append(round(top, 2))
                out.append({"a": [round(a_[0], 3), round(a_[1], 3)], "b": [round(b_[0], 3), round(b_[1], 3)],
                            "z0": z0, "z1": z1, "thick": 0.6 if kind == "retaining_wall" else 0.45, "kind": kind,
                            "osm": w_["id"]})
    return out


def seal_cracks(ground, tol=0.003, skip=None, back_near=None):   # (2 cm left hairlines of sky at grazing angles)
    """Faces closing every vertical step between neighbouring ground triangles (a level area against
    the slope, the deck over Wilson's Arch, the ground lowered under landmarks): wherever the piece
    across an edge lies lower, one face from its surface up to this edge, looking at the low side.
    Seen from anywhere the ground is then closed: no sky through a seam."""
    T = np.array([t for g in ground for t in g["tris"]], float)
    mats = [g["mat"] for g in ground for _ in g["tris"]]
    if not len(T):
        return []
    polys = shapely.polygons(T[:, :, :2])
    tree = shapely.STRtree(polys)
    A = T[:, [0, 1, 2]]
    B = T[:, [1, 2, 0]]
    cen = T[:, :, :2].mean(axis=1)
    a, b = A.reshape(-1, 3), B.reshape(-1, 3)
    owner = np.repeat(np.arange(len(T)), 3)
    d = b[:, :2] - a[:, :2]
    L = np.hypot(d[:, 0], d[:, 1])
    ok = L > 0.02
    nrm = np.stack([d[:, 1], -d[:, 0]], 1) / np.maximum(L, 1e-9)[:, None]
    mid = (a[:, :2] + b[:, :2]) / 2
    flip = ((mid - cen[owner]) * nrm).sum(1) < 0
    nrm[flip] *= -1
    probe = mid + nrm * 0.01
    pi, ti = tree.query(shapely.points(probe), predicate="intersects")
    keep = (ti != owner[pi]) & ok[pi]
    pi, ti = pi[keep], ti[keep]
    _, first = np.unique(pi, return_index=True)          # one neighbour per edge
    pi, ti = pi[first], ti[first]

    def plane_z(k, xy):
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = T[k]
        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(den) < 1e-12:
            return z1
        u = ((y2 - y3) * (xy[0] - x3) + (x3 - x2) * (xy[1] - y3)) / den
        v = ((y3 - y1) * (xy[0] - x3) + (x1 - x3) * (xy[1] - y3)) / den
        return u * z1 + v * z2 + (1 - u - v) * z3
    if skip is not None and not skip.is_empty:
        m_ = ~shapely.contains_xy(skip, mid[pi, 0], mid[pi, 1])
        pi, ti = pi[m_], ti[m_]
    sel = []
    for e, k in zip(pi, ti):
        la = plane_z(k, a[e, :2] + nrm[e] * 0.01)
        lb = plane_z(k, b[e, :2] + nrm[e] * 0.01)
        if a[e, 2] - la > tol or b[e, 2] - lb > tol:
            sel.append((e, la, lb, k))
    ends = {}                                    # end point -> directions of the seals ending there
    for e, _, _, _ in sel:
        t_ = (b[e, :2] - a[e, :2]) / L[e]
        for p_ in (a[e], b[e]):
            ends.setdefault((round(p_[0], 2), round(p_[1], 2)), []).append(t_)

    def ext(p_, t_):                             # 6 cm longer where the seal turns a corner (no slit there);
        ds = ends.get((round(p_[0], 2), round(p_[1], 2)), [])      # not where a collinear one continues it
        return 0.0 if sum(1 for d_ in ds if abs(d_ @ t_) > 0.99) > 1 else 0.06
    out = []
    for e, la, lb, k in sel:
        za, zb = a[e, 2], b[e, 2]
        # 4 cm back under the high side: where a landmark builds its own face on the edge, the seal
        # stays behind it instead of z-fighting with it
        t_ = (b[e, :2] - a[e, :2]) / L[e]
        # 5 mm back, 4 cm only beside a landmark (4 cm everywhere left a floorless slot under the high
        # edge, and at grazing angles sky showed through it along every kerb)
        bk = 0.04 if (back_near is not None and shapely.contains_xy(back_near, mid[e, 0], mid[e, 1])) else 0.005
        pa = a[e, :2] - nrm[e] * bk - t_ * ext(a[e], t_)
        pb = b[e, :2] - nrm[e] * bk + t_ * ext(b[e], t_)
        out.append({"a": [round(pa[0], 3), round(pa[1], 3)], "b": [round(pb[0], 3), round(pb[1], 3)],
                    # well below the low side: it stands 4 cm back, and a grazing ray over the low edge
                    # would pass under a shallow foot
                    "lo": [round(min(la, za) - 0.3, 3), round(min(lb, zb) - 0.3, 3)],
                    "hi": [round(za, 3), round(zb, 3)], "cap": 0,
                    "n": [round(nrm[e, 0], 3), round(nrm[e, 1], 3)],
                    **({"mat": "dressed"} if mats[k] == "setts" else {})})      # the kerb along a road
    return out

def eased_at(x, y):
    """Inside a level area (it is level there: stair treads would stick out of it). In the easing
    bands the treads stay: they are built from the eased surface itself."""
    pt = Point(x, y)
    return any(poly.distance(pt) < 0.5 for poly, _ in ALL_FLATS if poly is not WILSON_HALL)
    zt = float(terrain_z_v([x], [y])[0])
    pt = Point(x, y)
    for poly, fz in ALL_FLATS:
        if poly.contains(pt):
            return True
        if poly is WILSON_HALL or OPEN_EDGES.get(id(poly)) is None:
            continue
        D = max(3.0, min(40.0, abs(fz - zt) / BLEND_SLOPE))
        if OPEN_EDGES[id(poly)].distance(pt) < D and abs(fz - zt) > 0.3:
            return True
    return False


@functools.lru_cache(maxsize=1 << 21)          # ground vertices are shared by ~6 triangles
def street_z0(x, y):
    """Street level: the walkable surface (not lowered in the SUNKEN courts)."""
    if _terrain is not None:
        for ez_, ef_ in EASE_ZONES:          # the same easing as the ground piece there
            if shapely.contains_xy(ez_, x, y):
                return float(surface_z_v([x], [y], ease_from=ef_)[0])
        return float(surface_z_v([x], [y])[0])
    if x > 100 and y > 3.5:
        return -david_drop(polyline_s(DAVID["pts"], (x, y))[0])
    return 0.0


@functools.lru_cache(maxsize=1 << 21)
def street_z(x, y):
    """Ground level: street_z0, and in a SUNKEN court its paving level, so buildings, props and
    steps standing in the court sit on its floor."""
    z = street_z0(x, y)
    for sk in SUNKEN:
        x0, y0, x1, y1 = sk["poly"].bounds
        if x0 <= x <= x1 and y0 <= y <= y1 and shapely.contains_xy(sk["poly"], x, y):
            return z + sk["dz"]
    return z


def street_z_v(xs, ys, prefer=None, ease_from=None):
    """street_z0 over arrays (one vectorised terrain lookup for a whole ground tile set; the SUNKEN
    court regions add their dz themselves)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    if _terrain is not None:
        return surface_z_v(xs, ys, prefer, ease_from)
    return np.array([street_z0(x, y) for x, y in zip(xs, ys)])


def terrain_z_v(xs, ys):
    """The continuous terrain without any flat (for ground outside the level areas: a vertex on a
    flat's edge must not snap up to the flat)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    if _terrain is None:
        return street_z_v(xs, ys)
    d_, zg_, _, _ = _terrain._runtime()
    return np.asarray(_terrain.bilinear(zg_, (xs - d_["x0"]) / d_["step"], (ys - d_["y0"]) / d_["step"]), float)


def cell_size(x, y):
    """Ground mesh density: fine in the hero area, medium inside the walls, coarse outside."""
    if box(*POC).contains(Point(x, y)):
        return 2.0
    return 4.0 if CITY.contains(Point(x, y)) else 8.0


def raise_ez_to_ground(steps, ground, reach=0.15):
    """Per tread corner: ez = max(ez, the ground mesh's height at the nearest point of each triangle
    within reach of the corner)."""
    tris = [t for g in ground if g["mat"] != "grass" for t in g["tris"]]
    if not tris or not steps:
        return
    polys = [Polygon([(q[0], q[1]) for q in t]) for t in tris]
    tree = STRtree(polys)

    def z_at(t, x, y):
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(den) < 1e-12:
            return max(z1, z2, z3)
        l1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / den
        l2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / den
        return l1 * z1 + l2 * z2 + (1 - l1 - l2) * z3

    for st in steps:
        ext, ez = st["poly"]["ext"], st.get("ez")
        if not ez:
            continue
        for i, c in enumerate(ext):
            pt = Point(c)
            best = ez[i]
            for k in tree.query(pt.buffer(reach)):
                if polys[k].distance(pt) > reach:
                    continue
                q = shapely.ops.nearest_points(polys[k], pt)[0]
                best = max(best, z_at(tris[k], q.x, q.y))
            ez[i] = round(best, 3)


def tess_regions(region, zfun, cell=None, tile=32.0):
    """Clip region to 32 m tiles (fast rectangle clipping), then to cells, and triangulate each
    piece; returns a flat triangle list with z. cell=None picks the size per tile (cell_size); a
    coarse tile's edges on a tile line it shares with a finer one then get the finer cell corners
    as vertices, so the two meshes meet without T-junctions (z is not linear: they would crack)."""
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
            finer = {}                             # tile side -> (axis, line, the neighbour's finer cell)
            if cell is None:
                for side, ax, line, (cx, cy) in (("w", 0, tx0, (tx0 - tile / 2, ty0 + tile / 2)),
                                                 ("e", 0, tx0 + tile, (tx0 + tile * 1.5, ty0 + tile / 2)),
                                                 ("s", 1, ty0, (tx0 + tile / 2, ty0 - tile / 2)),
                                                 ("n", 1, ty0 + tile, (tx0 + tile / 2, ty0 + tile * 1.5))):
                    cn = cell_size(cx, cy)
                    if cn < c:
                        finer[side] = (ax, line, cn)
            for i in range(n):
                for j in range(n):
                    try:
                        piece = clip_by_rect(sub, tx0 + i * c, ty0 + j * c, tx0 + (i + 1) * c, ty0 + (j + 1) * c)
                    except Exception:                      # noqa: BLE001
                        piece = sub.intersection(box(tx0 + i * c, ty0 + j * c, tx0 + (i + 1) * c, ty0 + (j + 1) * c))
                    if piece.is_empty:
                        continue
                    lines = [finer[s_] for s_, at in (("w", i == 0), ("e", i == n - 1), ("s", j == 0), ("n", j == n - 1))
                             if at and s_ in finer]
                    _tri_piece(piece, tris, lines)
    if tris:                                               # z for every vertex in one vectorised call
        xy = np.array(tris, float).reshape(-1, 2)
        z = np.round(zfun(xy[:, 0], xy[:, 1]), 3)
        tris = [[[round(xy[3 * k + m, 0], 3), round(xy[3 * k + m, 1], 3), float(z[3 * k + m])] for m in range(3)]
                for k in range(len(tris))]
    return tris


def _densify(p, lines):
    """p with extra vertices on its edges that lie on the given tile lines [(axis, coord, spacing)],
    at every multiple of spacing (the finer neighbour tile's cell corners)."""
    def ring(cs):
        out = []
        for a, b in zip(cs, cs[1:]):
            out.append(a)
            for ax, c0, sp in lines:
                if abs(a[ax] - c0) < 1e-6 and abs(b[ax] - c0) < 1e-6:
                    o = 1 - ax
                    lo, hi = sorted((a[o], b[o]))
                    vs = [k * sp for k in range(math.floor(lo / sp), math.ceil(hi / sp) + 1) if lo + 1e-6 < k * sp < hi - 1e-6]
                    vs = vs if a[o] < b[o] else vs[::-1]
                    out += [(c0, v) if ax == 0 else (v, c0) for v in vs]
        return out + [cs[-1]]
    return Polygon(ring(list(p.exterior.coords)), [ring(list(h.coords)) for h in p.interiors])


def _tri_piece(piece, tris, lines=()):
    if True:
        if True:
            for p in polys_of(piece, 1e-4):
                if lines:
                    p = _densify(p, lines)
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
    setup_ease_zones()
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
    # lowest street level just outside each mass edge: the walls stand on it (south of the citadel the ground
    # falls ~9 m below the Jaffa Gate level the builder used, and sky showed under them)
    cit_edge_ground = []
    _cm = Polygon(cit_mass_r)
    for i_ in range(len(cit_mass_r)):
        a_, b_ = cit_mass_r[i_], cit_mass_r[(i_ + 1) % len(cit_mass_r)]
        (_, _), (nx_, ny_), _ = edge_frame(a_, b_)
        mx_, my_ = (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2
        if _cm.contains(Point(mx_ + nx_ * 1.0, my_ + ny_ * 1.0)):
            nx_, ny_ = -nx_, -ny_
        zs_ = [street_z0(a_[0] + (b_[0] - a_[0]) * f_ + nx_ * d_, a_[1] + (b_[1] - a_[1]) * f_ + ny_ * d_)
               for f_ in (0.0, 0.25, 0.5, 0.75, 1.0) for d_ in (0.5, 3.0)]
        cit_edge_ground.append(round(min(zs_), 2))
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
    # covered ways: none inside the Haram (its tunnels are underground) or through a landmark (the
    # gates build their own passages); a passage is carved out of the footprints only along its
    # stretches under one, and vaulted only where walls flank it (see the vaults below)
    no_vault = HARAM.union(unary_union([p_ for b_, p_, _ in cands if b_["id"] in LANDMARK_IDS] or [Polygon()]).buffer(0.3))
    roofs = [p_ for b_, p_, t_ in cands if b_["id"] not in LANDMARK_IDS and t_ != "context"]
    roof_tree = STRtree(roofs)
    cov = []
    for w_, ln_, k_ in covered_ways(d):
        if not CITY.intersects(ln_) or HERO_ZONE.intersects(ln_):
            continue
        cov += [(w_, s_, k_) for s_ in lines_of(ln_.difference(no_vault)) if s_.length >= 1.0]
    cov_hw = {}
    for w_, ln_, k_ in cov:                       # passages ~3 m wide, souqs measured later from the facades
        try:
            cov_hw[w_["id"]] = float(w_["tags"]["width"]) / 2
        except (KeyError, ValueError):
            cov_hw[w_["id"]] = 1.6 if k_ == "passage" else 2.2
    carved = [widen(ln_, s_, cov_hw[w_["id"]]).buffer(cov_hw[w_["id"]], cap_style="flat") for w_, ln_, k_ in cov
              for s_ in (stretches(ln_, unary_union([roofs[k] for k in roof_tree.query(ln_)] or [Polygon()]))
                         if k_ == "passage" else [ln_])]
    # rooms and roofs over the lanes (OSM building=roof or layer >= 1): the lane under them stays
    # walkable. Its corridor is carved out of the footprint like a passage and vaulted up to the
    # building's top where walls flank it, so the room above stays; a roof standing on an open
    # square goes altogether
    def raised(b_):
        return b_["tags"].get("building") == "roof" or layer_of(b_["tags"]) >= 1
    cov_ids = {w_["id"] for w_, _, _ in cov}
    lanes = [(w_, LineString(w_["pts"])) for w_ in d["ways"] if w_["tags"].get("highway") not in LANE_SKIP
             and len(w_.get("pts") or []) > 1 and w_["tags"].get("area") != "yes" and w_["id"] not in cov_ids
             and not (w_["tags"].get("tunnel") and layer_of(w_["tags"]) <= -2)]   # (deep tunnels: underground)
    lane_tree = STRtree([ln_ for _, ln_ in lanes])
    street_walls = [p_ for b_, p_, _ in cands if not raised(b_)]
    street_walls_tree = STRtree(street_walls)
    squares = unary_union([Polygon(w_["pts"]).buffer(0) for w_ in d["ways"] if w_.get("closed") and len(w_.get("pts") or []) > 3
                           and "building" not in w_["tags"] and infill.is_open_area(w_["tags"])] or [Polygon()])
    over, over_fp, vaulted, drop = [], {}, [], set()     # over: (way, stretch under the footprint, hw, building id)
    sunk_lanes = []          # lanes OSM puts below layer 0 that run under one: street level there, kept free of infill
    for b_, p_, t_ in cands:
        if t_ != "mid" or b_["id"] in LANDMARK_IDS or HARAM.contains(p_.representative_point()):
            continue
        for k in lane_tree.query(p_):
            w_, ln_ = lanes[k]                   # (the lane runs under it, not along its edge)
            parts = [s_ for s_ in lines_of(ln_.intersection(p_)) if s_.length >= 1.0
                     and p_.exterior.distance(s_.interpolate(0.5, normalized=True)) >= 0.5]
            if not raised(b_):                   # an ordinary footprint a mapped lane runs right through
                parts = [s_ for s_ in parts if s_.length >= 3.0]    # (rooms over the lane, as so often here)
            if parts and b_["tags"].get("building") == "roof" and squares.contains(p_.representative_point()):
                drop.add(b_["id"])
                break
            if vaulted:                          # OSM may draw the same bridge room twice
                parts = [s_ for g_ in parts for s_ in lines_of(g_.difference(unary_union(vaulted))) if s_.length >= 1.0]
            if not parts:
                continue
            hw = min(3.2, infill.street_halfwidth(w_["tags"], ln_, street_walls_tree, street_walls))
            if layer_of(w_["tags"]) < 0:         # (only by the footprint: elsewhere it may well be a tunnel)
                sunk_lanes += [widen(ln_, s_, 6.0).buffer(hw) for s_ in parts]
            over += [(w_, s_, hw, b_["id"]) for s_ in parts]
            over_fp[b_["id"]] = (b_, p_)
            vaulted += [s_.buffer(hw, cap_style="flat") for s_ in parts]
            carved += [widen(ln_, s_, hw).buffer(hw, cap_style="flat").intersection(p_.buffer(0.5))
                       for s_ in parts]                        # (not into the neighbours)
    cands = [c_ for c_ in cands if c_[0]["id"] not in drop]
    passages = unary_union(carved or [Polygon()])
    prepare(passages)
    print("lanes under raised footprints: %d stretches, %.0f m (%d footprints; %d roofs on squares dropped; "
          "%d stretches of lanes below layer 0 kept free of infill)" % (len(over), sum(s_.length for _, s_, _, _ in over),
                                                                       len(over_fp), len(drop), len(sunk_lanes)))
    gids = gate_ids()
    # Dung and New Gate are sections of crenellated curtain (landmarks_gates builds them): still wall
    cuts = [p_.convex_hull.buffer(1.0) for b_, p_, _ in cands
            if b_["id"] in gids and b_["id"] not in ("w1545285986", "w1393450805")]
    if cuts:
        wall_slabs = wall_slabs.difference(unary_union(cuts).buffer(0.5))   # no wall inside a gate
    prepare(wall_slabs)
    # buildings OSM does not map along the streets (pipeline/infill.py), lowest priority of all; the
    # footprints a sector profile removes (yards, squares, ruins drawn as buildings) and the sunk
    # lanes stay open too
    removed = [p_ for p_ in (clean(b_["outer"][0]) for b_ in d["buildings"] if b_["id"] in PROFILE_REMOVED and b_["outer"]
                             and len(b_["outer"][0]) >= 3) if p_ is not None]
    fill = infill.infill(d, [p for _, p, t in cands if t != "context"], CITY.buffer(-16.5),
                         unary_union([HARAM.buffer(2.0), HERO_ZONE.buffer(3.0), blocked.buffer(2.0), wall_slabs.buffer(0.5),
                                      unary_union(GROUND_HOLES + [WILSON_HALL]).buffer(0.5), unary_union(PROFILE_OPEN or [Polygon()]),
                                      LineString(ROAD).buffer(ROAD_HALF + 1.0)] + removed + sunk_lanes
                                     # (and nothing under the Mughrabi bridge: the excavation it spans)
                                     + [LineString(w_["pts"]).buffer(6.0) for w_ in d["ways"] if w_["id"] == 277508271]))
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
        if tier in ("mid", "context") and b["id"] not in LANDMARK_IDS:
            # 8 cm larger: OSM neighbours that should touch often leave a few cm between them, a slit of sky
            # down the whole wall; grown, the priority pass below closes every gap under 16 cm
            p = p.buffer(0.08, join_style="mitre")
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
        # no simplify after the difference: it would re-open overlaps. Rings have no holes, and every
        # hole here was cut out (a building placed before, a passage, a wall): filling it would cover
        # that again, so the piece is cut through each hole instead. Pieces are snapped to the mm grid
        # the rings are written on (rounding a sliver spike left by a cut makes a ring self-intersect)
        pieces = [g for q in polys_of(shapely.set_precision(rest, 0.001), 6.0) for s in infill.split_holes(q)
                  for g in polys_of(shapely.set_precision(s, 0.001), 6.0) if g.is_valid]
        for k, q in enumerate(sorted(pieces, key=lambda q: -q.area)):
            if len(pieces) > 1 and q.area < 15:
                continue
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
    PAIR_EDGES.clear()
    for i_, (fa, za) in enumerate(ALL_FLATS):
        for fb_, zb in ALL_FLATS[i_ + 1:]:
            if abs(za - zb) < 0.1 or not fa.intersects(fb_.buffer(0.5)):
                continue
            if any(f_.equals(WILSON_HALL) for f_ in (fa, fb_)):
                continue                       # a real cliff: the hall's front wall (landmarks_haram builds it)
            big, zbig, small, zsmall = (fa, za, fb_, zb) if fa.area >= fb_.area else (fb_, zb, fa, za)
            # where the bigger area really is the ground next door: not where a smaller level area
            # (lying inside it) owns that ground, e.g. the prayer area around the strip in front of the hall
            owned = big.difference(unary_union([f_ for f_, _ in ALL_FLATS if f_.area < big.area and f_ is not small]
                                               or [Polygon()]))
            edge = small.exterior.intersection(owned.buffer(0.5)).difference(bld_union.buffer(0.5))
            if edge.length > 0.5:
                PAIR_EDGES.append((edge, zbig, small, zsmall))
    street_z0.cache_clear()
    street_z.cache_clear()
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
    st_recs = [r_ for r_ in st_recs if not eased_at(r_["poly"].centroid.x, r_["poly"].centroid.y)]
    # a flight laid across the slope (or over an eased ramp) has treads buried on one side and floating on
    # the other: where the treads sit (median) more than 0.6 m off the ground at their corners, the whole
    # flight goes and the ground stays a ramp
    dev = {}
    st_recs_all = list(st_recs)
    for r_ in st_recs:
        zs_ = [street_z(*c) for c in r_["poly"].exterior.coords]
        dev.setdefault(r_["run"], []).append(max(abs(z_ - r_["top"]) for z_ in zs_))
    bad_runs = {k for k, v in dev.items() if float(np.median(v)) > 0.6}
    st_recs = [r_ for r_ in st_recs if r_["run"] not in bad_runs]
    print("stairs: %d flights, %d dropped (laid across the slope)" % (len(dev), len(bad_runs)))
    if os.environ.get("STAIRS_DEBUG"):
        cen = {}
        for r_ in st_recs_all:
            cen.setdefault(r_["run"], []).append(r_["poly"].centroid.coords[0])
        for k in sorted(dev):
            c_ = np.mean(cen[k], axis=0)
            print("  run %3d at (%5.0f,%5.0f) treads %3d median %.2f %s" % (k, c_[0], c_[1], len(dev[k]), float(np.median(dev[k])), "DROP" if k in bad_runs else ""))
    if not os.environ.get("STAIRS_NO_FIELD"):
        set_stair_field(st_recs)             # from here on the street follows the flights
    steps = [{"poly": poly_json(r_["poly"]), "top": r_["top"], "bottom": r_["bottom"], "dir": r_["dir"],
              "ez": [round(street_z(*c), 3) for c in poly_json(r_["poly"])["ext"]]}     # street at each corner
             for r_ in st_recs]
    steps_union = unary_union([r_["poly"].buffer(0) for r_ in st_recs] or [Polygon()]).buffer(0.001)
    # a tread side rises to the street only where it borders ground; against another tread (the next
    # step, a crossing run) it stays at the tread's own level, or its wall would cut through that stair
    prepare(steps_union)
    for st in steps:
        ext = st["poly"]["ext"]
        eo = []
        for i in range(len(ext)):
            a_, b_ = ext[i], ext[(i + 1) % len(ext)]
            L_ = math.dist(a_, b_) or 1.0
            nx_, ny_ = (b_[1] - a_[1]) / L_, -(b_[0] - a_[0]) / L_          # outward for a CCW ring
            m_ = ((a_[0] + b_[0]) / 2 + nx_ * 0.12, (a_[1] + b_[1]) / 2 + ny_ * 0.12)
            m2 = ((a_[0] + b_[0]) / 2 - nx_ * 0.12, (a_[1] + b_[1]) / 2 - ny_ * 0.12)
            eo.append(0 if (steps_union.contains(Point(m_)) and steps_union.contains(Point(m2))) else 1)
        st["eo"] = eo

    sunken = unary_union([sk["poly"] for sk in SUNKEN])
    # the ground continues under landmark footprints: their builders inset walls inside the OSM ring and
    # build raised floors, so cutting the ground at the ring left gaps at the foot of their walls
    def spans_drop(q):
        zs = street_z_v([c[0] for c in q.exterior.coords], [c[1] for c in q.exterior.coords])
        return float(np.max(zs) - np.min(zs)) > 1.5
    ground_cut = unary_union([bd["poly"] for bd in buildings if bd["osm"] not in LANDMARK_IDS])
    # (the ground runs 2 mm under the treads: cut at steps_union, 1 mm wider than them, it left a hairline
    #  of sky around every tread)
    street = ctx.difference(ground_cut).difference(cit_outer).difference(steps_union.buffer(-0.003)) \
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
    # Level areas are tessellated on their own at their exact level and the rest on the eased surface,
    # which equals the level at the edge: no triangle straddles an edge, and there is no seam. Where two
    # level areas meet in open ground (the Western Wall plaza and the lower prayer area) one vertical
    # face closes the step between them.
    split_regions = []
    seg_flats = [(fp_.segmentize(1.0), fz_, fp_) for fp_, fz_ in ALL_FLATS]   # both sides of an edge get the same
    for mat, reg, zf in regions[:3]:                                     # vertices: no T-junction cracks
        for fp_, fz_, orig_ in seg_flats:
            inside = reg.intersection(fp_)
            if not inside.is_empty:
                k_ = KERB if mat == "setts" else 0.0
                split_regions.append((mat, inside, lambda x, y, k_=k_, o_=orig_: street_z_v(x, y, o_) - k_))
                reg = reg.difference(fp_)
        for ez_, ef_ in EASE_ZONES:
            inside = reg.intersection(ez_)
            if not inside.is_empty:
                k_ = KERB if mat == "setts" else 0.0
                split_regions.append((mat, inside, lambda x, y, k_=k_, e_=ef_: street_z_v(x, y, ease_from=e_) - k_))
                reg = reg.difference(ez_)
        split_regions.append((mat, reg, zf))
    regions = split_regions + regions[3:]
    # under landmark footprints the ground runs 4 cm lower: their floors sit on it without z-fighting
    # (the whole footprint: keeping a rim at full level put it in the same plane as the portico floors)
    lm_polys = unary_union([bd["poly"] for bd in buildings if bd["osm"] in LANDMARK_IDS
                            and not (bd["osm"] in WALL_LANDMARKS and spans_drop(bd["poly"]))]
                           or [Polygon()]).segmentize(1.0)
    # landmarks spanning a level change (the Western Wall: prayer area on one side, the Haram on the other):
    # flat ground under them at their lowest point, so it meets the low side and never pokes through a face
    drops = []
    for bd in buildings:
        if bd["osm"] in WALL_LANDMARKS and spans_drop(bd["poly"]):
            q = bd["poly"].segmentize(1.0)
            zmin = float(np.min(street_z_v([c[0] for c in q.exterior.coords], [c[1] for c in q.exterior.coords])))
            drops.append((q, zmin - 0.05))
    lowered = []
    for mat, reg, zf in regions:
        for q, zq in drops:
            under = reg.intersection(q)
            if not under.is_empty:
                lowered.append((mat, under, lambda x, y, zq=zq: np.full(len(x), zq)))
                reg = reg.difference(q)
        under = reg.intersection(lm_polys)
        if not under.is_empty:
            lowered.append((mat, under, lambda x, y, zf=zf: zf(x, y) - 0.04))
            reg = reg.difference(lm_polys)
        lowered.append((mat, reg, zf))
    regions = lowered
    ground = []
    for mat, reg, zf in regions:
        tri = tess_regions(reg, zf)
        ground.append({"mat": mat, "tris": tri})
    # far terrain: a coarse ring 1.2 km out around the context box, so that from the walls or the air the
    # world does not end in sky a few dozen metres past the walls (the Hinnom and Kidron valleys)
    far = box(*CONTEXT).buffer(1200.0, join_style="mitre").difference(box(*CONTEXT))
    ground.append({"mat": "grass", "tris": tess_regions(far, street_z_v, cell=40.0, tile=160.0)})
    # a tread side bordering ground rises to the street (ez); the ground mesh there can sit a few cm above
    # street_z (eased levels, linear triangles), and a slit of sky opened under its edge: take the mesh
    raise_ez_to_ground(steps, ground)
    # (the sunken courts and Wilson's Arch hall have their own walls on their outlines, landmarks_haram; a
    #  seal on the hall front would close its arches. The Citadel moat is sealed like any other step: its
    #  foot showed sky)
    # (any wall, not only landmarks: 5 mm from a house wall or the citadel the seal z-fought with it)
    lm_near = unary_union([bd["poly"] for bd in buildings] + [cit_outer, Polygon(cit_mass_r)]
                          + [LineString([w_["a"], w_["b"]]).buffer(w_["thick"] / 2) for w_ in walls_generic]).buffer(0.5)
    prepare(lm_near)
    retaining = seal_cracks(ground, skip=unary_union([sunken.boundary, WILSON_HALL.boundary]).buffer(0.1),
                            back_near=lm_near)
    kerbs = []               # (the kerb faces are the crack seals along the roads: seal_cracks)
    owalls = osm_walls(d, buildings, skip_ids={137725307})     # (the Dome platform's wall: landmarks_haram)
    # the Mughrabi bridge (OSM steps w277508271, bridge=yes): the covered timber ramp on steel scaffolding from
    # the prayer plaza up to the Mughrabi Gate, over the excavation (Street View: never built before, an
    # infill block stood under it); its top end at the esplanade level 5 m inside the gate
    bridges = []
    for w_ in d["ways"]:
        if w_["id"] == 277508271:
            a_, b_ = w_["pts"][0], w_["pts"][-1]
            ux, uy = (b_[0] - a_[0]), (b_[1] - a_[1])
            L_ = math.hypot(ux, uy)
            top = street_z(b_[0] + ux / L_ * 5.0, b_[1] + uy / L_ * 5.0)
            gnd = [round(street_z(a_[0] + ux * k / 12, a_[1] + uy * k / 12), 2) for k in range(13)]
            bridges.append({"a": [round(v, 3) for v in a_], "b": [round(v, 3) for v in b_],
                            "z0": round(street_z(*a_), 2), "z1": round(top, 2), "w": 4.2, "ground": gnd})
    print("osm walls: %d segments, %.0f m" % (len(owalls), sum(math.dist(w_["a"], w_["b"]) for w_ in owalls)))

    # ---------------------------------------------------------------- buildings
    def height_of(osm, tags, q, tier):
        """Height above its ground (m) of footprint q, and its sector (mid tier only)."""
        h = hero.BUILDING.get(osm, {}).get("height", HEIGHTS.get(osm))
        sid = sector_at(q.representative_point().x, q.representative_point().y) if tier == "mid" else None
        if h is None and sid:
            h = roofscape.height_for(osm, tags, q.area, sid)
        if h is None:
            h = roofscape.osm_height(tags) or (7.0 if q.area < 60 else 9.0 + (zlib.crc32(osm.encode()) % 5))
        return h, sid

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
        h, sid = height_of(osm, bd["tags"], q, bd["tier"])
        # a footprint narrower than 1.5 m is a wall OSM maps as a building (garden walls, the partitions at
        # the Kotel entrance): a 2.6 m wall without openings, not a blank block a storey or two high
        thin = bd["tier"] == "mid" and osm not in LANDMARK_IDS and osm not in hero.BUILDING and q.buffer(-0.75).is_empty
        if thin:
            h = min(h, 2.6)
        # a footprint under 16 m2 OSM gives no height or levels is a booth, kiosk or shrine (two of them by the
        # Golden Gate stood 6-11 m as stone towers; Street View: none there taller than a door)
        elif (bd["tier"] == "mid" and osm not in LANDMARK_IDS and osm not in hero.BUILDING and q.area < 16.0
              and not roofscape.osm_height(bd["tags"])):
            h = min(h, 3.0)
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
                if not exposed[i] or thin:
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
                a_, b_ = r[i], r[(i + 1) % len(r)]
                (tx_, ty_), (nx_, ny_), _ = edge_frame(a_, b_)
                fac = facades.layout(rec, i, eground[i], brng, ov,
                                     ground_at=lambda u, a_=a_, tx_=tx_, ty_=ty_, nx_=nx_, ny_=ny_:
                                     street_z(a_[0] + tx_ * u + nx_ * 0.6, a_[1] + ty_ * u + ny_ * 0.6))
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
                # a wall another building stands against (or a few cm in front of) keeps no openings or
                # fixtures there: the hole was hidden and its sill and threshold poked through the neighbour
                def covered(u0_, u1_):
                    return any(inside_other(Point(a[0] + tx * u_ + nx * 0.35, a[1] + ty * u_ + ny * 0.35), bidx)
                               for u_ in (u0_, (u0_ + u1_) / 2, u1_))
                fac["openings"] = [o for o in fac["openings"] if not covered(o["u0"], o["u1"])]
                for o in fac["openings"]:            # a door opening onto a stair flight: the treads are its step
                    if o.get("threshold"):
                        uc_ = (o["u0"] + o["u1"]) / 2
                        if steps_union.contains(Point(a[0] + tx * uc_ + nx * 0.4, a[1] + ty * uc_ + ny * 0.4)):
                            o["threshold"] = False
                # fixtures stand out from the wall (pipes 6-15 cm, boards over a metre): probed deeper, a
                # neighbour 36 cm in front left a corner pipe standing free in the street before its wall
                def blocked(u_):
                    return any(inside_other(Point(a[0] + tx * u_ + nx * d_, a[1] + ty * u_ + ny * d_), bidx)
                               for d_ in (0.15, 0.35, 0.6, 0.9))
                fac["fixtures"] = [fx for fx in fac["fixtures"] if "u" not in fx or not blocked(fx["u"])]
                # canopies stop short of the building across the lane (at the Muristan a shop canopy ran
                # into the Church of the Redeemer's wall a metre away)
                keep_cp = []
                for cp in fac.get("canopies", []):
                    dp = cp["depth"]
                    for u_ in (cp["u0"] + 0.3, (cp["u0"] + cp["u1"]) / 2, cp["u1"] - 0.3):
                        d_ = 0.3
                        while d_ <= dp + 0.25:
                            if inside_other(Point(a[0] + tx * u_ + nx * d_, a[1] + ty * u_ + ny * d_), bidx):
                                dp = min(dp, d_ - 0.25)
                                break
                            d_ += 0.25
                    if dp >= 0.6:
                        keep_cp.append(dict(cp, depth=round(dp, 2)))
                fac["canopies"] = keep_cp
                for key in ("signs", "decals", "awnings"):
                    fac[key] = [x for x in fac.get(key, []) if "u0" not in x or not covered(x["u0"], x["u1"])]
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
            if not style["domes"] and "domes" not in hb and rec["tier"] == "context" and 40 < q.area < 400 and brng.random() < 0.3:
                style["domes"] = 1
            # vernacular field of shallow domes, unless an override sets the dome count (0: none)
            if sid and "domes" not in hb and not style["domes"] and osm not in HEIGHTS:
                rec["dome_list"] = roofscape.domes_for(osm, roofpoly, rec["roof_rooms"], sid, brng,
                                                       roofscape.main_axis(q))
        out_b.append(rec)

    # ---------------------------------------------------------------- vaults over the covered streets
    def flanked(ln_, hw, gap=2.5, min_len=1.5):
        """The runs of ln_ with walls on both sides at about hw (a passage vault stands on them, it
        has no walls of its own below the springing), joined across gaps under gap metres; tested
        every metre, a run reaches half a step past its last stations."""
        n = max(1, int(math.ceil(ln_.length)))
        h = ln_.length / n / 2
        ok = []
        for k in range(n + 1):
            s = ln_.length * k / n
            (tx, ty), _, _ = edge_frame(ln_.interpolate(max(0.0, s - 0.5)).coords[0],
                                        ln_.interpolate(min(ln_.length, s + 0.5)).coords[0])
            x, y = ln_.interpolate(s).coords[0]
            if all(obstacles.intersects(LineString([(x + sg * ty * (hw - 0.2), y - sg * tx * (hw - 0.2)),
                                                    (x + sg * ty * (hw + 1.5), y - sg * tx * (hw + 1.5))])) for sg in (1, -1)):
                ok.append(s)
        runs = []
        for s in ok:
            if runs and s - runs[-1][1] < gap:
                runs[-1][1] = s
            else:
                runs.append([s, s])
        runs = [(max(0.0, a - h), min(ln_.length, b + h)) for a, b in runs]
        return [substring(ln_, a, b) for a, b in runs if b - a >= min_len]

    vaults, unbridged = [], 0.0
    rec_tree = STRtree([Polygon(r_["ring"]) for r_ in out_b])
    top_of = {}
    for r_ in out_b:
        top_of[r_["osm"]] = max(top_of.get(r_["osm"], r_["top"]), r_["top"])
    for b_, p_ in over_fp.values():          # carved away whole: the top it would have had
        if b_["id"] not in top_of:
            top_of[b_["id"]] = max(street_z(*c_) for c_ in p_.exterior.coords) + height_of(b_["id"], b_["tags"], p_, "mid")[0]
    runs = []                                # (way, line, kind, hw, raised footprint id or None)
    for w_, ln_, kind, hw, bid_ in [(w_, ln_, k_, cov_hw[w_["id"]], None) for w_, ln_, k_ in cov] + \
            [(w_, s_, "passage", hw_, bid_) for w_, s_, hw_, bid_ in over]:
        if kind == "souq" and "width" not in w_["tags"]:
            hw = min(3.2, infill.street_halfwidth(w_["tags"], ln_, fp_tree, fp_list) + 0.1)
        parts = [ln_] if kind == "souq" else flanked(ln_, hw)      # (a bare roof over open ground: none)
        unbridged += ln_.length - sum(s_.length for s_ in parts)
        runs += [(w_, s_, kind, hw, bid_) for s_ in parts]
    def side_dist(x, y, nx_, ny_, maxd=6.0):
        """Distance from (x, y) along (nx_, ny_) to the nearest wall, or None within maxd."""
        hit = LineString([(x, y), (x + nx_ * maxd, y + ny_ * maxd)]).intersection(obstacles)
        if hit.is_empty:
            return None
        return Point(x, y).distance(hit)

    for w_, ln_, kind, hw, under in runs:
        n = max(1, int(math.ceil(ln_.length / 3.0)))
        pts = [ln_.interpolate(ln_.length * k / n).coords[0] for k in range(n + 1)]
        if kind == "souq":
            # a souq is rarely centred on its OSM line: the vault goes midway between the walls at each
            # point, as wide as the wider spans (one half-width about the line left sky along one wall)
            cen, hws = [], []
            for k, (x, y) in enumerate(pts):
                a_, b_ = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
                (tx_, ty_), _, _ = edge_frame(a_, b_)
                dl, dr = side_dist(x, y, -ty_, tx_), side_dist(x, y, ty_, -tx_)
                if dl is not None and dr is not None and dl + dr < 9.0:
                    off = (dl - dr) / 2
                    cen.append((x - ty_ * off, y + tx_ * off))
                    hws.append((dl + dr) / 2)
                else:
                    cen.append((x, y))
            pts = cen
            if hws:                          # the widest span: at the 90th percentile the wider stretches
                hw = min(4.0, max(hws) + 0.1)    # showed a strip of sky between the vault and one wall
        pts = [(x, y, round(street_z(x, y), 3)) for x, y in pts]
        near = [out_b[k] for k in rec_tree.query(ln_.buffer(hw + 1.0))]
        spring = 3.0 if kind == "passage" else 4.4
        crown = max(p[2] for p in pts) + spring + 1.25 * hw
        tops = sorted(r_["top"] for r_ in near)
        top = max(tops[len(tops) // 2] if (tops and kind == "passage") else crown + 0.6, crown + 0.5)
        if under is not None:                # under a room or roof over the lane: up to its top
            top = max(top_of[under], crown + 0.5)
        vaults.append({"kind": kind, "name": w_["tags"].get("name:en", ""), "osm": w_["id"], "hw": round(hw, 2),
                       "spring": spring, "top": round(top, 2), "pts": [[round(x, 3), round(y, 3), z] for x, y, z in pts]})
    print("vaults:", len(vaults), "covered stretches, %.0f m (%.0f m of passage with no walls either side left open)"
          % (sum(ln_.length for _, ln_, _, _, _ in runs), unbridged))

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
    lm_cut = unary_union([bd["poly"] for bd in buildings if bd["osm"] in LANDMARK_IDS] or [Polygon()])
    ctxinfo = {"buildings": out_b, "road": road, "road_line": ROAD, "paving": paving_all.difference(lm_cut),
               "street": street.difference(lm_cut),       # no dressing inside landmarks (ground runs under them)
               "road_area": road_area, "obstacles": obstacles, "moat": moat, "cit_outer": cit_outer,
               "cit_outer_r": cit_outer_r, "moat_edges": moat_edges, "hero": HERO_ZONE, "david": DAVID,
               "street_z": street_z, "kerb": KERB, "gate": GATEHOUSE, "walls": CITY_WALLS, "steps": steps,
               "courtyard": courtyard, "haram": HARAM, "landmark_ids": LANDMARK_IDS,
               # (clipped to off the platform: woods that only touch it are still planted)
               "woods": [g for g in (Polygon(w["pts"]).buffer(0).difference(PLATFORM) for w in d["ways"]
                                     if w.get("closed") and len(w.get("pts") or []) > 3
                                     and (w["tags"].get("landuse") in ("forest", "orchard") or w["tags"].get("natural") in ("wood", "scrub")
                                          or w["tags"].get("leisure") in ("park", "garden")))
                         if g.area > 1.0]}
    props, cables, ground_decals, beams = dressing.dress(ctxinfo, rng)
    step_tree = STRtree([r_["poly"] for r_ in st_recs]) if st_recs else None

    def surface_z(x, y):
        """The visible ground at (x, y), as dressing.dress places props: tread top, citadel courtyard,
        moat floor, road (kerb down), else street_z (with the sunken courts)."""
        q = Point(x, y)
        if courtyard.contains(q):
            return 1.0
        if moat.contains(q):
            return -MOAT_DEPTH
        for k in (step_tree.query(q) if step_tree is not None else []):
            if st_recs[k]["poly"].contains(q):
                return steps[k]["top"]
        return street_z(x, y) - (KERB if road_area.contains(q) else 0.0)
    for pp in PROFILE_PROPS:                                   # notable furniture from the sector profiles
        x, y = pp["p"][:2]
        props.append({"type": pp["type"], "p": [round(x, 3), round(y, 3), round(surface_z(x, y), 3)],
                      "rot": pp.get("rot", 0.0), "s": pp.get("s", 1.0), "col": pp.get("col", True), "r": pp.get("r", 0.5)})

    # ---------------------------------------------------------------- the rest of the wall circuit (OSM)

    spec = {
        "poc_box": POC, "context_box": CONTEXT,
        "walls_generic": walls_generic,
        "retaining": retaining,
        "osm_walls": owalls,
        "bridges": bridges,
        # ground left out on purpose (closed in by landmark walls): QA counts these as covered
        "ground_holes": [[[round(x, 3), round(y, 3)] for x, y in h_.exterior.coords[:-1]] for h_ in GROUND_HOLES],
        "vaults": vaults,
        "buildings": out_b,
        "gatehouse": GATEHOUSE, "city_walls": CITY_WALLS,
        "citadel": {"outer": cit_outer_r, "mass": [list(p) for p in cit_mass_r], "inner": cit_inner_r,
                    "moat_edges": moat_edges, "wall_h": CITADEL_WALL_H, "moat_depth": MOAT_DEPTH, "towers": TOWERS,
                    "edge_ground": cit_edge_ground},
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
