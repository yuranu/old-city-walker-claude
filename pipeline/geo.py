"""Shared 2D helpers (shapely) for the spec pipeline. Local frame: x east, y north, metres."""
import math

from shapely import make_valid
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon
from shapely.ops import unary_union

__all__ = ["Polygon", "MultiPolygon", "LineString", "Point", "unary_union", "polys_of", "clean", "ccw",
           "poly_json", "ring_area", "edge_frame", "rand_point_in", "seg_dist"]


def polys_of(g, min_area=0.0):
    """Flatten any geometry to a list of Polygons."""
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g] if g.area > min_area else []
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        out = []
        for h in g.geoms:
            out += polys_of(h, min_area)
        return out
    return []


def clean(coords, simplify=0.15):
    """Valid, simplified polygon from a coordinate ring (may return None)."""
    if len(coords) < 3:
        return None
    p = make_valid(Polygon(coords))
    ps = polys_of(p, 1.0)
    if not ps:
        return None
    p = max(ps, key=lambda q: q.area).simplify(simplify, preserve_topology=True)
    return p if p.is_valid and p.area > 1.0 else None


def ring_area(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def ccw(coords):
    r = [(round(x, 3), round(y, 3)) for x, y in coords]
    if r and r[0] == r[-1]:
        r = r[:-1]
    # drop consecutive duplicates
    out = [p for i, p in enumerate(r) if p != r[i - 1]]
    return out if ring_area(out) > 0 else out[::-1]


def poly_json(p):
    return {"ext": ccw(p.exterior.coords), "holes": [ccw(h.coords)[::-1] for h in p.interiors]}


def edge_frame(a, b):
    """Unit tangent, outward normal (right of a->b for CCW rings) and length."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return (dx / L, dy / L), (dy / L, -dx / L), L


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay or 1)))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def rand_point_in(poly, rng, tries=60):
    x0, y0, x1, y1 = poly.bounds
    for _ in range(tries):
        q = Point(rng.uniform(x0, x1), rng.uniform(y0, y1))
        if poly.contains(q):
            return q
    return None
