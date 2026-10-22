"""What the model has in a REAL | MODEL pair's view: buildings (OSM id, infill, landmark, height) and OSM
walls inside its view cone, nearest first, to trace a critic finding ("invented building on the left",
"wall too low") to the spec entry that makes it.

    cd pipeline/qa && ../../.venv/bin/python sv_whatsthere.py <place> <pair> [--side left|right|centre] [--max 40]
"""
import json
import math
import sys

from shapely.geometry import LineString, Point, Polygon

from common import ROOT, load_spec


def main():
    place, pair = sys.argv[1], sys.argv[2]
    a = sys.argv
    side = a[a.index("--side") + 1] if "--side" in a else None
    rmax = float(a[a.index("--max") + 1]) if "--max" in a else 40.0
    v = next(v for v in json.loads((ROOT / "build/qa/svcmp" / place / "views.json").read_text()) if v["id"] == pair)
    x, y, h = v["x"], v["y"], v["heading"]
    half = 45.0                                       # the stills span 90 degrees
    lo, hi = {"left": (-45, -10), "right": (10, 45), "centre": (-15, 15)}.get(side, (-half, half))
    base, secs, blds = load_spec()
    cam = Point(x, y)

    def in_cone(g):
        best = None
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            p = g.exterior.interpolate(t, normalized=True) if hasattr(g, "exterior") else g.interpolate(t, normalized=True)
            ang = (math.degrees(math.atan2(p.x - x, p.y - y)) - h + 180) % 360 - 180
            if lo <= ang <= hi:
                d = cam.distance(g)
                best = d if best is None else min(best, d)
        return best
    rows = []
    for b in blds:
        g = Polygon(b["ring"])
        if g.distance(cam) > rmax:
            continue
        d = in_cone(g)
        if d is not None:
            src = "infill" if str(b["id"]).startswith("f") or b["tags"].get("note") == "infill" else ("landmark" if b.get("tier") == "hero" else "osm")
            rows.append((d, "building", b["id"], src, "h=%.1f" % (b.get("top", 0) - b.get("base", 0)),
                         b["tags"].get("name:en") or b["tags"].get("name") or "", b.get("sector", "base")))
    for w in base.get("osm_walls", []):
        g = LineString([w["a"], w["b"]])
        if g.distance(cam) > rmax:
            continue
        d = in_cone(g)
        if d is not None:
            rows.append((d, w["kind"], "w%s" % w["osm"], "osm_walls",
                         "top %.1f / foot %.1f" % (max(w["z1"]), min(w["z0"])), "", "base"))
    seen = set()
    print("%s %s at (%.1f, %.1f) heading %d, cone %s..%s deg" % (place, pair, x, y, h, lo, hi))
    for r in sorted(rows):
        if (r[1], r[2]) in seen:
            continue
        seen.add((r[1], r[2]))
        print("  %5.1f m  %-14s %-12s %-9s %-16s %s [%s]" % r)


if __name__ == "__main__":
    main()
