"""Heights and roofscape of the rule-based (mid tier) buildings, by quarter.

OSM has heights for under 2 % of the Old City buildings, and the skyline is what reads first from
the walls, the Mount of Olives and every rooftop. Rules, from aerial and rooftop photographs:

* Heights: 2-3 storeys in the Muslim and Christian quarters, small 1-2 storey infill, 3-4 storeys
  in the rebuilt Jewish Quarter and the monasteries/patriarchates; OSM height/building:levels win.
* Domes: the vernacular roof is a field of shallow lime-washed domes, one over each cross-vaulted
  room (radius 1.8-2.8 m, rise well under a hemisphere), on a flat roof with a low parapet. Many
  were built over with rooftop rooms; still the most characteristic element of the skyline.
"""
import math
import zlib

from shapely.geometry import Point, Polygon
from shapely.affinity import rotate

# sector -> (height offset m, dome probability, domes density per 100 m2 of roof)
QUARTER = {
    "s00_jaffa": (0.0, 0.0, 0.0),        # hero area: hand tables
    "s01_armenian": (0.5, 0.40, 1.6),
    "s02_zion": (0.0, 0.30, 1.4),
    "s03_christian_w": (1.0, 0.40, 1.6),
    "s04_sepulchre": (0.5, 0.50, 1.8),
    "s05_souks": (0.0, 0.55, 2.0),       # the covered souqs' roofs are domes and vaults
    "s06_jewish": (1.5, 0.50, 1.6),      # rebuilt after 1967 in a neo-vernacular style, domes kept
    "s07_kotel": (0.5, 0.30, 1.2),
    "s08_damascus": (0.0, 0.60, 2.0),
    "s09_wad": (0.0, 0.60, 2.0),
    "s10_herod_lions": (0.0, 0.60, 1.8),
    "s11_haram": (-1.0, 0.35, 1.4),
}


def osm_height(tags):
    """Height from OSM tags, or None."""
    for k in ("height", "building:height"):
        v = tags.get(k)
        if v:
            try:
                return float(str(v).replace("m", "").strip())
            except ValueError:
                pass
    lv = tags.get("building:levels")
    if lv:
        try:
            return 1.2 + 3.6 * float(lv)
        except ValueError:
            pass
    return None


def height_for(osm, tags, area, sid):
    h = osm_height(tags)
    if h is not None:
        return h
    r = (zlib.crc32(("h" + osm).encode()) % 1000) / 1000.0
    if osm.startswith("f"):                  # infill (pipeline/infill.py): unmapped, mostly low buildings
        return 6.0 + 3.0 * r + QUARTER.get(sid, (0, 0, 0))[0] / 2
    if area < 40:
        h = 5.0 + 2.5 * r
    elif area < 120:
        h = 7.0 + 4.0 * r
    elif area < 400:
        h = 8.5 + 5.0 * r
    else:
        h = 10.0 + 5.0 * r
    return h + QUARTER.get(sid, (0, 0, 0))[0]


def domes_for(osm, roofpoly, rooms, sid, rng, axis_deg=0.0):
    """Shallow domes on a flat roof: a grid along the building's main axis, clear of the parapet
    and rooftop rooms. -> [{"c": [x, y], "r", "rise", "drum"}]"""
    _, prob, dens = QUARTER.get(sid, (0, 0.4, 1.6))
    if roofpoly.is_empty or roofpoly.area < 22 or rng.random() > prob:
        return []
    cs = list(roofpoly.minimum_rotated_rectangle.exterior.coords)
    width = min(math.dist(cs[0], cs[1]), math.dist(cs[1], cs[2]))
    r = min(rng.uniform(1.8, 2.8), width / 2 - 0.45)          # narrow houses get smaller domes
    if r < 1.4:
        return []
    step = 2 * r + rng.uniform(0.6, 1.6)
    budget = max(1, min(8, int(round(roofpoly.area * dens / 100.0))))
    keep = roofpoly.buffer(-(r + 0.35))
    for rm in rooms:
        keep = keep.difference(Polygon(rm["ring"]).buffer(r + 0.2))
    if keep.is_empty:
        return []
    c = roofpoly.centroid
    local = rotate(keep, -axis_deg, origin=c)
    x0, y0, x1, y1 = local.bounds
    pts = []
    nx, ny = max(1, int((x1 - x0) // step) + 1), max(1, int((y1 - y0) // step) + 1)
    ox, oy = (x0 + x1) / 2 - (nx - 1) * step / 2, (y0 + y1) / 2 - (ny - 1) * step / 2
    for i in range(nx):
        for j in range(ny):
            p = Point(ox + i * step, oy + j * step)
            if local.contains(p):
                pts.append(p)
    rng.shuffle(pts)
    out = []
    a = math.radians(axis_deg)
    for p in pts[:budget]:
        dx, dy = p.x - c.x, p.y - c.y
        x, y = c.x + dx * math.cos(a) - dy * math.sin(a), c.y + dx * math.sin(a) + dy * math.cos(a)
        out.append({"c": [round(x, 2), round(y, 2)], "r": round(r * rng.uniform(0.92, 1.0), 2),
                    "rise": round(rng.uniform(0.45, 0.7), 2), "drum": round(rng.uniform(0.25, 0.55), 2)})
    return out


def dome_circles(bd):
    """[(x, y, r)] of every dome Blender builds on a building's flat roof: the vernacular field
    (bd["dome_list"]) and the style domes (style["domes"] = 1 or 2), which blender/build_city.py
    add_domes() puts on the oriented box of the first roof piece. Rooftop clutter keeps clear."""
    out = [(d["c"][0], d["c"][1], d["r"]) for d in bd.get("dome_list", [])]
    count = bd["style"].get("domes")
    if not count or not bd.get("roof"):
        return out
    ext = bd["roof"][0]["ext"]
    best = None                                     # build_city.obb: smallest box along a ring edge
    for i in range(len(ext)):
        a, b = ext[i], ext[(i + 1) % len(ext)]
        ln = math.dist(a, b)
        if ln < 0.5:
            continue
        t = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        s = (-t[1], t[0])
        us = [p[0] * t[0] + p[1] * t[1] for p in ext]
        vs = [p[0] * s[0] + p[1] * s[1] for p in ext]
        area = (max(us) - min(us)) * (max(vs) - min(vs))
        if best is None or area < best[0]:
            cu, cv = (max(us) + min(us)) / 2, (max(vs) + min(vs)) / 2
            c = (t[0] * cu + s[0] * cv, t[1] * cu + s[1] * cv)
            lu, lv = max(us) - min(us), max(vs) - min(vs)
            best = (area, c, t, lu, lv) if lu >= lv else (area, c, s, lv, lu)
    if best is None:
        return out
    _, c, t, ll, ls = best
    rad = min(2.6, 0.24 * ls)
    if rad < 0.9:
        return out
    spots = [c] if count == 1 else [(c[0] - t[0] * ll / 4, c[1] - t[1] * ll / 4), (c[0] + t[0] * ll / 4, c[1] + t[1] * ll / 4)]
    roof = Polygon(ext)
    for x, y in spots:
        if all(roof.contains(Point(x + math.cos(k * math.pi / 4) * rad * 1.1, y + math.sin(k * math.pi / 4) * rad * 1.1))
               for k in range(8)):
            out.append((x, y, rad))
    return out


def main_axis(poly):
    """Bearing (degrees) of the longest edge of the minimum rotated rectangle."""
    mrr = poly.minimum_rotated_rectangle
    cs = list(mrr.exterior.coords)
    best = max(zip(cs, cs[1:]), key=lambda e: math.dist(*e))
    return math.degrees(math.atan2(best[1][1] - best[0][1], best[1][0] - best[0][0]))


def sector_lookup(secs):
    """secs = sectors.load() -> fn(x, y) -> sector id or None."""
    def f(x, y):
        pt = Point(x, y)
        for sid, geom, _ in secs:
            if geom.contains(pt):
                return sid
        return None
    return f


