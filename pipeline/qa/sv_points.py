"""Candidate Street View lookup points for the iconic places (data/qa/iconic.json): the place centre and
points round it on the open ground, as lat/lon, for resolving to panoramas in a browser
(Google Maps snaps a pano link to the nearest panorama).

    .venv/bin/python pipeline/qa/sv_points.py [place ...] > build/sv/points.json
"""
import json
import math
import sys

from shapely.geometry import Point, Polygon

from common import ROOT, building_index, load_spec

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


def main():
    want = sys.argv[1:]
    places = json.loads((ROOT / "data/qa/iconic.json").read_text())["places"]
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    _, _, blds = load_spec()
    polys, tree = building_index(blds)

    def free(x, y):
        p = Point(x, y).buffer(1.0)
        return not any(polys[k].intersects(p) for k in tree.query(p))
    out = []
    for pl in places:
        if want and pl["id"] not in want:
            continue
        cx, cy = centre_of(pl, osm)
        r = pl.get("r", 25)
        pts = []
        for rr in (r * 0.9, r * 1.4):
            for k in range(8):
                a = 2 * math.pi * k / 8
                x, y = cx + rr * math.sin(a), cy + rr * math.cos(a)
                if free(x, y):
                    pts.append((x, y))
        for x, y in pts[:10]:
            lat, lon = to_latlon(x, y)
            out.append({"place": pl["id"], "x": round(x, 1), "y": round(y, 1), "lat": round(lat, 6),
                        "lon": round(lon, 6), "centre": [round(cx, 1), round(cy, 1)]})
    print(json.dumps(out, indent=0))


if __name__ == "__main__":
    main()
