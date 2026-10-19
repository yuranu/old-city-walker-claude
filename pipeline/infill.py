"""Infill: buildings OSM does not map, along the streets of the walled city.

Inside the walls nearly every square metre is built up; what is open is a street, a mapped
square/area, or a courtyard. OSM coverage is patchy in places (lower David Street, parts of
the Muslim Quarter), which leaves the streets as wide open gaps in a row of footprints. The rule:

* street corridors: every OSM highway centreline, with a half-width measured from the existing
  street walls (25th percentile of the distance to the nearest mapped building), at least 1.4 m
  and at most 3-3.5 m for lanes, souqs and steps (5.5 m for the few roads), or the OSM width;
* open areas: every mapped non-building area (pedestrian areas, squares, parks, parking,
  archaeological sites, …), the Haram, a band along the walls;
* infill = a 9 m deep frontage band along the corridors minus corridors, open areas and mapped
  buildings, in pieces of at least 20 m2 and 2.4 m width. Interior courtyards stay open.

The pieces join the spec as lowest-priority buildings (like MANUAL_BUILDINGS), so they only take
space the OSM footprints leave free.
"""
import numpy as np
from shapely import STRtree
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

# mapped areas that are open ground (kept free of infill). Built-up landuse (retail, residential,
# religious: e.g. the souq block between the three parallel market streets) is NOT open.
OPEN_TAGS = {"landuse": {"grass", "forest", "meadow", "recreation_ground", "cemetery", "orchard", "village_green",
                         "greenfield", "construction", "brownfield"},
             "leisure": {"park", "garden", "playground", "pitch", "common", "nature_reserve"},
             "amenity": {"parking", "grave_yard"}, "place": {"square", "plaza"},
             "historic": {"archaeological_site"}}


def is_open_area(t):
    if t.get("natural") or (t.get("highway") and t.get("area") == "yes"):
        return True
    return any(t.get(k) in v for k, v in OPEN_TAGS.items())
# the largest half-width a street is given where one side is unmapped: lanes and souqs are 3-7 m wide
HW_MAX = {"footway": 3.5, "pedestrian": 3.5, "steps": 3.0, "path": 3.0, "living_street": 3.5, "corridor": 2.5}
DEPTH = 9.0


def _polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def street_halfwidth(t, ln, tree, footprints):
    """Half-width of a street: OSM width, else measured from the mapped street walls."""
    try:
        return float(np.clip(float(t["width"]) / 2, 1.2, 8.0))
    except (KeyError, ValueError):
        pass
    ds = []
    for s in np.arange(0, ln.length + 0.01, 3.0):
        p = ln.interpolate(s)
        k = tree.nearest(p)
        ds.append(footprints[k].distance(p))
    return float(np.clip(np.percentile(ds, 25), 1.4, HW_MAX.get(t.get("highway"), 5.5))) if ds else 2.5


def infill(d, footprints, domain, keep_open):
    """d: osm_local.json; footprints: shapely polygons of the mapped buildings;
    domain: where infill may go (inside the walls, clear of them); keep_open: extra open areas.
    -> [(polygon, half-width of the street it fronts)]"""
    tree = STRtree(footprints)
    corridors, fronts = [], []
    for w in d["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if not t.get("highway") or len(pts) < 2:
            continue
        if int(t.get("layer", "0") or 0) < 0 or t.get("tunnel") == "yes" and t.get("layer", "0") != "0":
            continue
        ln = LineString(pts)
        if not domain.intersects(ln):
            continue
        if w.get("closed") and t.get("area") == "yes":          # pedestrian area / square
            corridors.append(Polygon(pts).buffer(0))
            continue
        hw = street_halfwidth(t, ln, tree, footprints)
        corridors.append(ln.buffer(hw))
        fronts.append(ln.buffer(hw + DEPTH))
    areas = []
    for w in d["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if not w.get("closed") or len(pts) < 4 or "building" in t:
            continue
        if is_open_area(t):
            p = Polygon(pts).buffer(0)
            if p.area > 15 and domain.intersects(p):
                areas.append(p)
    open_ = unary_union(corridors + areas + [keep_open])
    band = unary_union(fronts).intersection(domain)
    built = unary_union(footprints).buffer(0.05)
    rest = band.difference(open_).difference(built)
    out = []
    for p in _polys(rest):
        if p.area < 20 or p.buffer(-1.2).is_empty:
            continue
        p = p.buffer(-0.02).simplify(0.25)                       # tidy; the priority pass resolves overlaps
        for q in _polys(p):
            if q.area >= 20:
                out.append(Polygon(q.exterior))
    return out


def stats(pieces):
    a = sum(p.area for p in pieces)
    return "%d infill pieces, %.0f m2" % (len(pieces), a)


