"""Stepped streets from the terrain.

The street surface (terrain_street.py) is a smooth field; Old City lanes are not ramps: anything
steeper than ~7 % is a run of long, low steps (David Street: 2.2 m treads, 13 cm risers; the
86 OSM steps ways average 12 % grade). For each centreline interval to be stepped:

* number of steps n = |dz| / riser (riser 0.13-0.16 m), tread = length / n;
* tread k is the slice of the street corridor between perpendicular cuts at s_k and s_k+1, at
  the level z_a + dz (k + 0.5) / n, clipped to the open street and to treads already placed;
* every tread is a flat polygon with risers down to below the lowest neighbour.

Steps ways are stepped over their whole length; other lanes only where the 6 m-smoothed grade
exceeds GRADE.
"""
import math

import numpy as np
from shapely import STRtree, clip_by_rect
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

GRADE = 0.07
PED = {"footway", "pedestrian", "steps", "path", "living_street"}


def steep_intervals(ln, zfun, always=False, sample=2.0, min_len=4.0):
    L = ln.length
    if always:
        return [(0.0, L)]
    ss = np.arange(0.0, L + 1e-6, sample)
    if len(ss) < 4:
        return []
    zs = np.array([zfun(*ln.interpolate(s).coords[0]) for s in ss])
    k = 3
    zsm = np.convolve(np.pad(zs, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    g = np.abs(np.gradient(zsm, ss))
    out, start = [], None
    for s, steep in zip(ss, g > GRADE):
        if steep and start is None:
            start = s
        if not steep and start is not None:
            if s - start >= min_len:
                out.append((start, s))
            start = None
    if start is not None and L - start >= min_len:
        out.append((start, L))
    return out


def _cut(ln, s, hw):
    """Perpendicular cut line across the corridor at station s."""
    a = ln.interpolate(max(0.0, s - 0.3)).coords[0]
    b = ln.interpolate(min(ln.length, s + 0.3)).coords[0]
    d = math.dist(a, b) or 1.0
    tx, ty = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    p = ln.interpolate(s).coords[0]
    return p, (tx, ty), ((p[0] - ty * hw, p[1] + tx * hw), (p[0] + ty * hw, p[1] - tx * hw))


def treads(ln, s0, s1, hw, zfun, region, riser=0.14):
    """Step polygons for ln between stations s0 and s1. -> [(polygon, top, (tx, ty))]"""
    za = zfun(*ln.interpolate(s0).coords[0])
    zb = zfun(*ln.interpolate(s1).coords[0])
    n = max(1, int(round(abs(zb - za) / riser)))
    if abs(zb - za) < 0.25:
        return []
    out = []
    for k in range(n):
        sa, sb = s0 + (s1 - s0) * k / n, s0 + (s1 - s0) * (k + 1) / n
        _, t, (l0, r0) = _cut(ln, sa, hw)
        _, _, (l1, r1) = _cut(ln, sb, hw)
        quad = Polygon([l0, r0, r1, l1])
        if not quad.is_valid:
            quad = quad.buffer(0)
        if quad.is_empty:
            continue
        _, t1, _ = _cut(ln, sb, hw)
        if t[0] * t1[0] + t[1] * t1[1] < 0.985:              # the corridor bends between the cuts:
            seg = LineString([ln.interpolate(s).coords[0] for s in np.linspace(sa, sb, 4)]).buffer(hw, cap_style="flat")
            quad = quad.intersection(seg)                    # keep what lies near the centreline
        piece = quad.intersection(region)
        if piece.is_empty:
            continue
        top = za + (zb - za) * (k + 0.5) / n
        out.append((piece, top, t if zb < za else (-t[0], -t[1])))
    return out


def build(ways, zfun, open_street, halfwidth, skip=None, extra=()):
    """ways: OSM ways (dicts with tags, pts); halfwidth(way, line) -> m; extra: [(line, hw, s0, s1)]
    always stepped (hand-specified runs, e.g. David Street). -> spec step records."""
    runs = list(extra)
    for w in ways:
        t = w["tags"]
        pts = w.get("pts") or []
        if t.get("highway") not in PED or len(pts) < 2 or t.get("area") == "yes":
            continue
        if int(t.get("layer", "0") or 0) != 0 or t.get("tunnel") == "yes" and t.get("layer", "0") != "0":
            continue
        ln = LineString(pts)
        if skip is not None and skip.intersects(ln):
            continue
        if not open_street.intersects(ln):
            continue
        for s0, s1 in steep_intervals(ln, zfun, always=t["highway"] == "steps"):
            runs.append((ln, halfwidth(w, ln), s0, s1))
    placed, polys = [], []
    tree = None
    for ln, hw, s0, s1 in runs:
        x0, y0, x1, y1 = ln.bounds
        bb = (x0 - hw - 2, y0 - hw - 2, x1 + hw + 2, y1 + hw + 2)
        try:
            region = clip_by_rect(open_street, *bb)                      # local copy
        except Exception:  # noqa: BLE001  (GEOS ring errors on the city-wide polygon)
            region = open_street.intersection(box(*bb))
        if region.is_empty:
            continue
        if polys:
            tree = STRtree(polys)
            near = [polys[i] for i in tree.query(ln.buffer(hw + 1.0))]
            if near:
                region = region.difference(unary_union(near).buffer(0.002))
        for piece, top, t in treads(ln, s0, s1, hw, zfun, region):
            for q in getattr(piece, "geoms", [piece]):
                if q.geom_type != "Polygon" or q.area < 0.05:
                    continue
                polys.append(q)
                placed.append((q, top, t))
    out = []
    for q, top, t in placed:
        zmin = min(zfun(*c) for c in q.exterior.coords)
        out.append({"poly": q, "top": round(top, 3), "bottom": round(min(zmin, top) - 0.45, 3),
                    "dir": [round(t[0], 4), round(t[1], 4)]})
    return out
