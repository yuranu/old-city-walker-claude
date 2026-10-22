"""QA views of one iconic place (data/qa/iconic.json): street views from the open ground around it, each
aimed at the place's centre (eye height, a little upward so the facade fills the frame), plus two
aerial obliques.

    .venv/bin/python pipeline/qa/plan_iconic.py <place id> <out views.json>
"""
import json
import math
import sys

from shapely.geometry import Point, Polygon

from common import ROOT, building_index, load_spec


def main():
    pid, out = sys.argv[1], sys.argv[2]
    places = {p["id"]: p for p in json.loads((ROOT / "data/qa/iconic.json").read_text())["places"]}
    pl = places[pid]
    base, secs, blds = load_spec()
    polys, tree = building_index(blds)
    if "osm" in pl:
        osm = json.loads((ROOT / "data/osm_local.json").read_text())
        b = next(b for b in osm["buildings"] if b["id"] == pl["osm"])
        c = Polygon(b["outer"][0]).buffer(0).centroid
        cx, cy = c.x, c.y
    else:
        cx, cy = pl["at"]
    r = pl.get("r", 25)

    def free(x, y, rad=0.9):
        p = Point(x, y).buffer(rad)
        return not any(polys[k].intersects(p) for k in tree.query(p))
    views = []
    for ring_r in (r * 0.5, r * 0.8, r * 1.1):
        n = max(8, int(2 * math.pi * ring_r / 6))
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = cx + ring_r * math.sin(a), cy + ring_r * math.cos(a)
            if not free(x, y):
                continue
            h = math.degrees(math.atan2(cx - x, cy - y))
            views.append({"id": "%s_%d_%d" % (pid, int(ring_r), k), "x": round(x, 2), "y": round(y, 2),
                          "z_eye": 1.7, "heading": round(h % 360, 1), "pitch": 6, "fov": 75})
    # keep at most 16 street views, spread round the place
    if len(views) > 16:
        views.sort(key=lambda v: math.atan2(v["x"] - cx, v["y"] - cy))
        step = len(views) / 16
        views = [views[int(i * step)] for i in range(16)]
    for k, a in enumerate((35, 215)):
        d = r + 45
        x, y = cx + d * math.sin(math.radians(a)), cy + d * math.cos(math.radians(a))
        views.append({"id": "%s_air%d" % (pid, k), "x": round(x, 2), "y": round(y, 2), "z_eye": 40,
                      "heading": round((a + 180) % 360, 1), "pitch": -28, "fov": 60})
    json.dump(views, open(out, "w"), indent=1)
    json.dump({"place": pl, "centre": [cx, cy]}, open(out.replace("views.json", "place.json"), "w"), indent=1)
    print("%d views for %s" % (len(views), pl["name"]))


if __name__ == "__main__":
    main()
