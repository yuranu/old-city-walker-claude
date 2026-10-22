"""Candidate Street View lookup points for the iconic places (data/qa/iconic.json), as lat/lon, for
resolving to panoramas in a browser (Google Maps snaps a pano link to the nearest panorama).

Street View is shot from where people walk: the candidates are points every 8 m along the street-level
OSM ways (no rampart walks, roofs or tunnels) within 1.6 r of the place, clear of the buildings, nearest
first and spread round the place (up to 24 a place).

    .venv/bin/python pipeline/qa/sv_points.py [place ...] > build/sv/points.json
    .venv/bin/python pipeline/qa/sv_points.py --region <sector|x0,y0,x1,y1> [--step 35] > build/sv/points_<r>.json

--region: for the improvement cycle, points every ~35 m along the region's street-level ways (at least
25 m apart), each with the street's two directions as headings to aim at; "place" is "reg_<region>".
"""
import json
import math
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon

from common import ROOT, building_index, load_spec, region_geom

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from infill import street_level                      # noqa: E402

ORIGIN = json.loads((ROOT / "data/osm_local.json").read_text())["origin"]


def to_latlon(x, y):
    return (ORIGIN["lat"] + y / 111320.0,
            ORIGIN["lon"] + x / (111320.0 * math.cos(math.radians(ORIGIN["lat"]))))


def centre_of(pl, osm):
    if "osm" in pl:
        b = next(b for b in osm["buildings"] if b["id"] == pl["osm"])
        c = Polygon(b["outer"][0]).buffer(0).centroid
        return c.x, c.y
    return tuple(pl["at"])


def walkable(t):
    """a way a Street View camera could stand on: street level, not along the top of a wall"""
    if not t.get("highway") or not street_level(t):
        return False
    if int(t.get("layer", "0") or 0) >= 1 or t.get("wall") or t.get("bridge") or t.get("indoor"):
        return False
    name = (t.get("name:en") or t.get("name") or "").lower()
    return "rampart" not in name


def region_points(name, step=35.0):
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    _, _, blds = load_spec()
    polys, tree = building_index(blds)
    geom = region_geom(name)
    pts = []
    for w in osm["ways"]:
        if not walkable(w["tags"]) or len(w.get("pts") or []) < 2:
            continue
        ln = LineString(w["pts"]).intersection(geom)
        for part in getattr(ln, "geoms", [ln]):
            if part.is_empty or part.geom_type != "LineString" or part.length < 6:
                continue
            for k in range(max(1, int(part.length // step))):
                d = min(part.length, (k + 0.5) * part.length / max(1, int(part.length // step)))
                q = part.interpolate(d)
                a, b = part.interpolate(max(0, d - 2)), part.interpolate(min(part.length, d + 2))
                h = math.degrees(math.atan2(b.x - a.x, b.y - a.y)) % 360
                pb = Point(q.x, q.y).buffer(1.0)
                if any(polys[j].intersects(pb) for j in tree.query(pb)):
                    continue
                if any(math.hypot(q.x - x, q.y - y) < 25 for x, y, _ in pts):
                    continue
                pts.append((q.x, q.y, h))
    out = []
    for x, y, h in pts:
        lat, lon = to_latlon(x, y)
        out.append({"place": "reg_" + name.replace(",", "_"), "x": round(x, 1), "y": round(y, 1), "lat": round(lat, 7),
                    "lon": round(lon, 7), "centre": [round(x, 1), round(y, 1)],
                    "headings": [round(h), round((h + 180) % 360)]})
    return out


def main():
    if "--region" in sys.argv:
        a = sys.argv
        step = float(a[a.index("--step") + 1]) if "--step" in a else 35.0
        print(json.dumps(region_points(a[a.index("--region") + 1], step), indent=0))
        return
    want = sys.argv[1:]
    places = json.loads((ROOT / "data/qa/iconic.json").read_text())["places"]
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    _, _, blds = load_spec()
    polys, tree = building_index(blds)
    ways = [LineString(w["pts"]) for w in osm["ways"] if walkable(w["tags"]) and len(w.get("pts") or []) > 1]

    def free(x, y):
        p = Point(x, y).buffer(1.0)
        return not any(polys[k].intersects(p) for k in tree.query(p))
    out = []
    for pl in places:
        if want and pl["id"] not in want:
            continue
        cx, cy = centre_of(pl, osm)
        r = pl.get("r", 25) * 1.6
        disc = Point(cx, cy).buffer(r)
        cand = []
        for ln in ways:
            if not ln.intersects(disc):
                continue
            seg = ln.intersection(disc)
            for part in getattr(seg, "geoms", [seg]):
                if part.length < 1:
                    continue
                for k in range(int(part.length // 8) + 1):
                    q = part.interpolate(min(k * 8.0, part.length))
                    if free(q.x, q.y):
                        cand.append((q.x, q.y))
        # nearest first, but no two within 6 m, and every 45-degree sector round the place gets its turn
        cand.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
        picked = []
        for _round in range(4):
            seen = set()
            for x, y in cand:
                sec = int((math.degrees(math.atan2(x - cx, y - cy)) % 360) // 45)
                if sec in seen or any(math.hypot(x - a, y - b) < 6 for a, b in picked):
                    continue
                seen.add(sec)
                picked.append((x, y))
        for x, y in picked[:24]:
            lat, lon = to_latlon(x, y)
            out.append({"place": pl["id"], "x": round(x, 1), "y": round(y, 1), "lat": round(lat, 7),
                        "lon": round(lon, 7), "centre": [round(cx, 1), round(cy, 1)]})
    print(json.dumps(out, indent=0))


if __name__ == "__main__":
    main()
