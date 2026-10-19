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
import json
import math
import random
import zlib
from pathlib import Path

import dressing
import facades
import hero
from geo import LineString, Point, Polygon, ccw, clean, edge_frame, poly_json, polys_of, unary_union
from shapely import constrained_delaunay_triangles
from shapely.geometry import box

ROOT = Path(__file__).resolve().parent.parent

POC = (-30, -75, 160, 60)
CONTEXT = (-190, -200, 260, 170)    # as far west as the pinned OSM extract reaches
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
    {"name": "wall_nw", "pts": [(-52.0, 57.5), (-11.8, 18.0), (-6.99, 13.32)], "height": 11.25, "thick": 3.2},
    {"name": "tall_stretch", "pts": [(-6.99, 13.32), (-0.54, 7.04)], "height": 13.3, "thick": 3.8},
    {"name": "blind_arch_stretch", "pts": [(-0.54, 7.04), (3.4, 3.2)], "height": 10.8, "thick": 3.2},
]   # points run NW -> SE so the outside (south-west) is on the right of each segment
MOAT_DEPTH = 5.0
CITADEL_WALL_H = 13.0
MOAT_W = 6.0
TOWERS = [
    {"kind": "box", "name": "phasael", "c": (63.0, -17.0), "size": (20.0, 17.0), "rot": 24.0, "h": 21.0,
     "top": {"size": (14.0, 12.0), "h": 3.0}},       # NE corner, ~24 m above the street (citadel_east.md A5)
    {"kind": "minaret", "c": (24.0, -79.0), "r": 2.6, "h": 30.0},
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


def souq_profile(L, eg, rng):
    """Default override for a facade fronting David Street: closed dukkan shops (notes C3), raised
    thresholds (C2), shed canopies (C4), blade boards (C6). Hero overrides take precedence."""
    n = max(1, int((L - 0.8) // 3.0))
    sp = (L - 0.8) / n
    ground = []
    for k in range(n):
        w = min(sp - 0.55, rng.uniform(2.0, 2.9))
        ground.append({"kind": "shop" if w >= 1.4 else "blind", "w": round(w, 2), "h": round(rng.uniform(2.8, 3.15), 2),
                       "arch": rng.choice(["segment", "segment", None]),
                       "door": rng.choice(["door_teal", "door_teal", "door_teal", "door_olive", "rolldown_green",
                                           "rolldown_grey", "door_green2"])})
    return {"souq": True, "shops": True, "centres": [round(0.4 + sp * (k + 0.5), 2) for k in range(n)], "ground": ground,
            "ground_storey": 4.4, "awning": False, "thr": round(rng.uniform(0.16, 0.28), 2), "thr_out": round(rng.uniform(0.4, 0.65), 2),
            "canopy": {"depth": round(rng.uniform(1.2, 1.6), 2), "z_front": 3.15, "z_wall": 3.95}}


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


def street_z(x, y):
    if x > 100 and y > 3.5:
        return -david_drop(polyline_s(DAVID["pts"], (x, y))[0])
    return 0.0


def tess_regions(region, zfun, cell=2.0):
    """Clip region to a grid and triangulate each piece; returns flat triangle list with z."""
    tris = []
    x0, y0, x1, y1 = region.bounds
    i0, j0 = math.floor(x0 / cell), math.floor(y0 / cell)
    i1, j1 = math.ceil(x1 / cell), math.ceil(y1 / cell)
    for i in range(i0, i1):
        for j in range(j0, j1):
            c = box(i * cell, j * cell, (i + 1) * cell, (j + 1) * cell)
            if not region.intersects(c):
                continue
            piece = region.intersection(c)
            for p in polys_of(piece, 1e-4):
                for t in polys_of(constrained_delaunay_triangles(p), 1e-5):
                    pts = list(t.exterior.coords)[:3]
                    if (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[1][1] - pts[0][1]) * (pts[2][0] - pts[0][0]) < 0:
                        pts = [pts[0], pts[2], pts[1]]
                    tris.append([[round(x, 3), round(y, 3), round(zfun(x, y), 3)] for x, y in pts])
    return tris


def main():
    d = json.loads((ROOT / "data/osm_local.json").read_text())
    rng = random.Random(1898)

    # ---------------------------------------------------------------- citadel
    citadel = next(b for b in d["buildings"] if b["id"] == "r136164")
    cit_outer_r = ccw(douglas_peucker(list(map(tuple, citadel["outer"][0])), 2.5))
    cit_inner_r = ccw(clean(citadel["inner"][0]).exterior.coords)
    moat_edges = []
    for i in range(len(cit_outer_r)):
        a, b = cit_outer_r[i], cit_outer_r[(i + 1) % len(cit_outer_r)]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        moat_edges.append(MOAT_W if (m[1] > -62 and m[0] > 22 and not (m[0] < 30 and m[1] < -30)) else 0.0)
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
        tier = "hero" if HERO_ZONE.contains(c) else ("mid" if box(*POC).contains(c) else "context")
        cands.append((b, p, tier))
    prio = {"hero": 0, "mid": 1, "context": 2}
    cands.sort(key=lambda t: (prio[t[2]], -t[1].area))
    for m in MANUAL_BUILDINGS:                                  # gap fillers go last
        mp = Polygon(m["ring"])
        cands.append(({"id": m["id"], "tags": {"name": "", "building": "yes", "note": m["why"]}, "outer": [m["ring"]]},
                      mp, "hero" if HERO_ZONE.contains(mp.centroid) else "mid"))
        HEIGHTS[m["id"]] = m["height"]
        SHOPS.add(m["id"])
    blocked = unary_union([citadel_body, moat, gate_poly] + wall_polys)
    taken = []
    buildings = []
    for b, p, tier in cands:
        rest = p.difference(blocked)
        if taken:
            rest = rest.difference(unary_union(taken))
        pieces = polys_of(rest, 6.0)            # no simplify after the difference: it would re-open overlaps
        pieces = [q for q in pieces if q.is_valid and q.area > 6.0]
        for k, q in enumerate(sorted(pieces, key=lambda q: -q.area)):
            if len(pieces) > 1 and q.area < 15:
                continue
            q = Polygon(q.exterior)                              # drop courtyard holes
            taken.append(q)
            bid = b["id"] if k == 0 else "%s_%d" % (b["id"], k)
            buildings.append({"id": bid, "osm": b["id"], "poly": q, "tags": b["tags"], "tier": tier})

    obstacles = unary_union([bd["poly"] for bd in buildings] + [cit_mass, gate_poly] + wall_polys)

    # ---------------------------------------------------------------- ground regions
    ctx = box(*CONTEXT)
    road = LineString(ROAD).buffer(ROAD_HALF, cap_style="flat", join_style="round")
    bld_union = unary_union([bd["poly"] for bd in buildings])
    # David Street steps (footprints clipped to the open street)
    steps = []
    pts = DAVID["pts"]
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    s, k = DAVID["start_s"], 0
    open_street = ctx.difference(bld_union).difference(cit_outer)
    while s + DAVID["tread"] < total:
        acc = 0.0
        for a, b in zip(pts, pts[1:]):
            L = math.dist(a, b)
            if acc + L >= s:
                t = (s - acc) / L
                p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                dirn = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
                break
            acc += L
        k += 1
        side = (-dirn[1], dirn[0])
        hw, ln = DAVID["width"] / 2, DAVID["tread"] + 0.01
        quad = Polygon([(p[0] + side[0] * hw, p[1] + side[1] * hw), (p[0] - side[0] * hw, p[1] - side[1] * hw),
                        (p[0] - side[0] * hw + dirn[0] * ln, p[1] - side[1] * hw + dirn[1] * ln),
                        (p[0] + side[0] * hw + dirn[0] * ln, p[1] + side[1] * hw + dirn[1] * ln)])
        top = round(-(k - 1) * DAVID["riser"], 3)
        for q in polys_of(quad.intersection(open_street), 0.05):
            steps.append({"poly": poly_json(q), "top": top, "bottom": round(-david_drop(s + DAVID["tread"]) - 0.4, 3),
                          "dir": [round(dirn[0], 4), round(dirn[1], 4)]})
        s += DAVID["tread"]
    steps_union = unary_union([Polygon(st["poly"]["ext"]) for st in steps]).buffer(0.001)

    street = ctx.difference(bld_union).difference(cit_outer).difference(steps_union)
    road_area = street.intersection(road)
    paving_all = street.difference(road)
    kerb_band = paving_all.intersection(road.buffer(KERB_BAND))
    paving = paving_all.difference(kerb_band)
    courtyard = cit_inner.difference(bld_union)
    regions = [
        ("paving", paving, street_z),
        ("kerb_band", kerb_band, street_z),
        ("setts", road_area, lambda x, y: street_z(x, y) - KERB),
        ("grass", moat.buffer(-0.01), lambda x, y: -MOAT_DEPTH),
        ("paving", courtyard, lambda x, y: 1.0),
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
    for bd in buildings:
        bid, osm = bd["id"], bd["osm"]
        q = bd["poly"]
        r = ccw(q.exterior.coords)
        brng = random.Random(zlib.crc32(bid.encode()))
        others = obstacles.difference(q.buffer(0.05))
        exposed, eground = [], []
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            _, (nx, ny), L = edge_frame(a, b)
            hits = sum(1 for t in (0.25, 0.5, 0.75)
                       if others.contains(Point(a[0] + (b[0] - a[0]) * t + nx * 1.2, a[1] + (b[1] - a[1]) * t + ny * 1.2)))
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
        zs = [street_z(*p) for p in r]
        g_hi = max(zs) if not cit_inner.contains(q.centroid) else 1.0
        g_lo = min(min(zs), min(eground))
        hb = hero.BUILDING.get(osm, {})
        h = hb.get("height", HEIGHTS.get(osm))
        if h is None:
            h = 7.0 if q.area < 60 else 9.0 + (zlib.crc32(osm.encode()) % 5)
        ashlar = osm in ASHLAR
        style = {"wall": hb.get("wall", "ashlar" if ashlar else "rubble"), "shops": osm in SHOPS,
                 "domes": DOMES.get(osm, 0), "roof": "hipped" if osm in HIPPED else "flat",
                 "storey": hb.get("storey", 4.2 if ashlar or osm in SHOPS else 3.6),
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
            for i in range(len(r)):
                if not exposed[i]:
                    continue
                ov = hero.FACADES.get((osm, i))
                a_, b_ = r[i], r[(i + 1) % len(r)]
                m_ = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
                (tx_, ty_), (nx_, ny_), L_ = edge_frame(a_, b_)
                sd_, dd_ = polyline_s(DAVID["pts"], m_)
                if 104 < m_[0] < 175 and dd_ < 8.0 and L_ > 2.2:
                    cx_, cy_ = LineString(DAVID["pts"]).interpolate(sd_).coords[0]
                    if (cx_ - m_[0]) * nx_ + (cy_ - m_[1]) * ny_ > 0.3 * max(dd_, 0.1):
                        base_ov = souq_profile(L_, eground[i], brng)
                        ov = {**base_ov, **(ov or {})}
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
        if rec["tier"] == "context":
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
                    if others.contains(probe):
                        continue
                    z = eground[i] + 1.4
                    while z + 1.6 < g_hi + h - 1.2:
                        if brng.random() > 0.25:
                            rec["cwin"].append({"edge": i, "u": round(u, 2), "z": round(z, 2), "cell": brng.choice(cells)})
                        z += 3.6
        # skyline: rooftop rooms (some with red-tile roofs) and lime-washed domes
        rec["roof_rooms"] = []
        if style["roof"] == "flat" and rec["roof"]:
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
        out_b.append(rec)

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
               "courtyard": courtyard}
    props, cables, ground_decals, beams = dressing.dress(ctxinfo, rng)

    spec = {
        "poc_box": POC, "context_box": CONTEXT,
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
    (ROOT / "data/scene_spec.json").write_text(json.dumps(spec))
    nt = {t: sum(1 for b in out_b if b["tier"] == t) for t in ("hero", "mid", "context")}
    nf = sum(len(b.get("facades", [])) for b in out_b)
    no = sum(len(f["openings"]) for b in out_b for f in b.get("facades", []))
    print("buildings %s  facades %d  openings %d  steps %d  ground tris %d  kerbs %d  props %d  cables %d" %
          (nt, nf, no, len(steps), sum(len(g["tris"]) for g in ground), len(kerbs), len(props), len(cables)))


if __name__ == "__main__":
    main()
