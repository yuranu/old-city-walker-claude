"""Stepped streets from the terrain.

The street surface (terrain_street.py) is a smooth field; Old City lanes are not ramps: anything
steeper than ~7 % is a run of long, low steps (David Street: 2.2 m treads, 13 cm risers; the
86 OSM steps ways average 12 % grade). For each centreline interval to be stepped:

* the interval is split into monotonic stretches at the turning points of its level profile (a lane
  that dips and climbs again is two flights, not one straight line between its ends);
* per stretch: number of steps n = |dz| / riser (riser 0.13-0.16 m), tread = length / n where the
  profile is close to straight (within CHORD_TOL); elsewhere tread k runs between the stations
  where the profile crosses the levels z_a + dz k / n and z_a + dz (k + 1) / n, so every tread
  stays within half a riser of the street;
* tread k is the slice of the street corridor between perpendicular cuts at s_k and s_k+1, at
  the level z_a + dz (k + 0.5) / n, clipped to the open street and to treads already placed;
* every tread is a flat polygon with risers down to below the lowest neighbour.

Steps ways are stepped over their whole length; other lanes only where the 6 m-smoothed grade
exceeds GRADE.
"""
import math
import os

import numpy as np
from shapely import STRtree, clip_by_rect
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

GRADE = 0.07
GRADE_RULE = False         # step every lane steeper than GRADE (off: only OSM steps ways and given runs)
STEEP = float(os.environ.get("STAIRS_STEEP", "99"))    # step lanes steeper than this too (off: at 0.2 the JQ
                           # escarpment footways got 48 flights and the steep ground only moved beside them)
REACH = 8.0                # a flight in a lane runs wall to wall when both walls stand within this
PED = {"footway", "pedestrian", "steps", "path", "living_street"}
TURN = 0.3          # a reversal of the level profile by more than this (m) ends a flight
CHORD_TOL = 0.25    # equal treads when the profile stays this close (m) to the straight line
WIDEN = 1.2         # treads reach this much past the measured half-width, clipped to the open street: a stepped
                    # lane runs wall to wall (a strip of ramp beside the steps, with cheeks, read as broken)


def wall_reach(ln, s0, s1, region, hw, step=2.0):
    """Half-width that takes the flight to the walls: where walls stand on both sides within REACH at most
    stations, the 90th percentile of the wider side's distance (+0.3, the treads are clipped to the open
    street anyway); else hw. (A flight narrower than its lane left a sloping strip of ramp beside it.)"""
    n = max(2, int((s1 - s0) / step) + 1)
    wide, walled = [], 0
    for k in range(n):
        s = s0 + (s1 - s0) * k / (n - 1)
        a = ln.interpolate(max(0.0, s - 0.5)).coords[0]
        b = ln.interpolate(min(ln.length, s + 0.5)).coords[0]
        L = math.dist(a, b) or 1.0
        nx, ny = (b[1] - a[1]) / L, -(b[0] - a[0]) / L
        x, y = ln.interpolate(s).coords[0]
        ds = []
        for sg in (1, -1):
            ray = LineString([(x, y), (x + sg * nx * REACH, y + sg * ny * REACH)])
            inside = ray.intersection(region)
            d = None
            for g in getattr(inside, "geoms", [inside]):
                if g.geom_type == "LineString" and g.distance(Point(x, y)) < 0.05 and g.length < REACH - 0.05:
                    d = g.length
            ds.append(d)
        if ds[0] is not None and ds[1] is not None:
            walled += 1
            wide.append(max(ds))
    if walled < 0.5 * n or not wide:
        return hw
    return max(hw, min(REACH, float(np.percentile(wide, 90))) + 0.3)


def steep_intervals(ln, zfun, always=False, sample=2.0, min_len=4.0, grade=GRADE):
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
    for s, steep in zip(ss, g > grade):
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


def flights(ss, zs):
    """Monotonic stretches of a sampled level profile, split at its turning points (reversals of
    more than TURN). -> [(stations, levels)], levels made monotonic (mean of the running and the
    remaining extreme, so small wiggles are flattened without biasing the level up or down)."""
    turns, ext, d = [0], 0, 0
    for i in range(1, len(zs)):
        if d == 0:
            if abs(zs[i] - zs[0]) > TURN:
                d, ext = (1 if zs[i] > zs[0] else -1), i
        elif d * (zs[i] - zs[ext]) >= 0:
            ext = i
        elif d * (zs[ext] - zs[i]) > TURN:
            turns.append(ext)
            d, ext = -d, i
    turns.append(len(zs) - 1)
    out = []
    for i0, i1 in zip(turns, turns[1:]):
        if i1 <= i0:
            continue
        z = zs[i0:i1 + 1]
        if z[-1] >= z[0]:
            zm = (np.maximum.accumulate(z) + np.minimum.accumulate(z[::-1])[::-1]) / 2
        else:
            zm = (np.minimum.accumulate(z) + np.maximum.accumulate(z[::-1])[::-1]) / 2
        out.append((ss[i0:i1 + 1], zm))
    return out


def treads(ln, s0, s1, hw, zfun, region, riser=0.14, sample=1.0):
    """Step polygons for ln between stations s0 and s1. -> [(polygon, top, (tx, ty))]"""
    ss = np.linspace(s0, s1, max(2, int(math.ceil((s1 - s0) / sample)) + 1))
    zs = np.array([zfun(*ln.interpolate(s).coords[0]) for s in ss])
    out = []
    for fs, fz in flights(ss, zs):
        out += _flight(ln, fs, fz, hw, region, riser)
    return out


def _flight(ln, ss, zm, hw, region, riser):
    """Treads of one monotonic flight (stations ss, levels zm)."""
    s0, s1, za, zb = ss[0], ss[-1], zm[0], zm[-1]
    n = max(1, int(round(abs(zb - za) / riser)))
    if abs(zb - za) < 0.25 or (s1 - s0) / n > 2.6:
        return []                            # (treads over 2.6 m deep: a ramp, not a stair; they read as slabs)
    h = (zb - za) / n
    if np.abs(za + (zb - za) * (ss - s0) / (s1 - s0) - zm).max() < CHORD_TOL:
        cuts = [s0 + (s1 - s0) * k / n for k in range(n + 1)]                  # equal treads
    else:                                    # cut where the profile crosses each riser level
        lv = za + h * np.arange(n + 1)
        cuts = list(np.interp(lv, zm, ss) if h > 0 else np.interp(lv[::-1], zm[::-1], ss[::-1])[::-1])
        cuts[0], cuts[-1] = s0, s1
    out = []
    for k in range(n):
        sa, sb = cuts[k], cuts[k + 1]
        if sb - sa < 0.05:                   # the profile jumps: two risers in one
            continue
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
        top = za + h * (k + 0.5)
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
        # (lanes stay ramps up to STEEP: stepping every lane over 7 % put stairs where there are none)
        for s0, s1 in steep_intervals(ln, zfun, always=t["highway"] == "steps", grade=GRADE if GRADE_RULE else STEEP):
            runs.append((ln, halfwidth(w, ln) + WIDEN, s0, s1))
    placed, polys = [], []
    tree = None
    for run_id, (ln, hw, s0, s1) in enumerate(runs):
        x0, y0, x1, y1 = ln.bounds
        r_ = max(hw, REACH) + 2
        bb = (x0 - r_, y0 - r_, x1 + r_, y1 + r_)
        try:
            region = clip_by_rect(open_street, *bb)                      # local copy
        except Exception:  # noqa: BLE001  (GEOS ring errors on the city-wide polygon)
            region = open_street.intersection(box(*bb))
        if region.is_empty:
            continue
        if not os.environ.get("STAIRS_NO_REACH"):
            hw = wall_reach(ln, s0, s1, region, hw)
        if polys:
            tree = STRtree(polys)
            near = [polys[i] for i in tree.query(ln.buffer(hw + 1.0))]
            if near:
                region = region.difference(unary_union(near))
        own = []                             # treads of this flight so far: at a bend consecutive
        for piece, top, t in treads(ln, s0, s1, hw, zfun, region):   # quads overlap on the inner side
            if own:                          # (exactly: a 2 mm clearance left a slit of sky between treads)
                piece = piece.difference(unary_union(own))
            for q in getattr(piece, "geoms", [piece]):
                if q.geom_type != "Polygon" or q.area < 0.05:
                    continue
                polys.append(q)
                own.append(q)
                placed.append((q, top, t, run_id))
    # an OSM flight the terrain only gives a few deep treads (a gentle lane mapped as steps) reads as loose
    # slabs or strips across the paving: fewer than 3 treads, or treads deeper than 1.2 m on average, and
    # it stays a ramp (the given runs, David Street with its 2.2 m treads, are kept)
    count = {}
    for _, _, _, run_id in placed:
        count[run_id] = count.get(run_id, 0) + 1
    keep_run = {k for k, c in count.items()
                if k < len(extra) or (c >= 3 and (runs[k][3] - runs[k][2]) / c <= 1.2)}
    placed = [p_ for p_ in placed if p_[3] in keep_run]
    out = []
    for q, top, t, run_id in placed:
        zmin = min(zfun(*c) for c in q.exterior.coords)
        out.append({"poly": q, "top": round(top, 3), "bottom": round(min(zmin, top) - 0.45, 3),
                    "dir": [round(t[0], 4), round(t[1], 4)], "run": run_id})
    return out
