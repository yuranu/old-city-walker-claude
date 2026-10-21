"""Plan QA viewpoints for a region: walkable coverage (street centrelines every 15 m, both ways, plus
a look at the ground ahead), squares, stair ends, an aerial grid, and the regression views in
data/qa/regression.json. Points inside buildings are skipped (a camera there stands on a roof).

    .venv/bin/python pipeline/qa/plan_views.py <region> <out views.json> [--level 0]
"""
import json
import math
import sys

from shapely import STRtree
from shapely.geometry import LineString, Point, Polygon

from common import ROOT, building_index, load_spec, region_geom


# footprints that are not spec buildings but have walls a camera must not stand in: Wilson's Arch hall
# (landmarks_haram.WILSON_HALL; game.setCam puts a camera there on the hall floor, under Chain Street,
# and its front wall seen edge-on read as a slit of sky in the paving)
NO_CAMERA = [Polygon([(621.91, 30.53), (646.06, 35.24), (640.68, 62.55), (639.28, 62.27), (626.48, 59.77),
                      (629.03, 46.85), (619.07, 44.91)])]


def main():
    region_name, out = sys.argv[1], sys.argv[2]
    reg = region_geom(region_name)
    base, secs, blds = load_spec()
    polys, tree = building_index(blds)
    # tree trunks too: a camera inside one sees the bark from within, which flickers
    trunks = [Point(p_["p"][:2]).buffer(1.0 * p_.get("s", 1.0)) for d_ in [base] + list(secs.values())
              for p_ in d_.get("props", []) if p_["type"].startswith("tree")]
    polys = polys + trunks
    tree = STRtree(polys)
    osm = json.loads((ROOT / "data/osm_local.json").read_text())

    def free(x, y, r=0.8):
        p = Point(x, y).buffer(r)
        return not any(polys[k].intersects(p) for k in tree.query(p)) and not any(q.intersects(p) for q in NO_CAMERA)
    views = []

    def add(vid, x, y, h, pitch=-6.0, z=1.7, fov=75):
        if reg.contains(Point(x, y)) and free(x, y):
            views.append({"id": vid, "x": round(x, 2), "y": round(y, 2), "z_eye": z, "heading": round(h % 360, 1),
                          "pitch": pitch, "fov": fov})
    n = 0
    for w in osm["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if not t.get("highway") or len(pts) < 2 or int(t.get("layer", "0") or 0) < -1:
            continue
        ln = LineString(pts)
        if not reg.intersects(ln):
            continue
        if w.get("closed") and t.get("area") == "yes":
            c = Polygon(pts).representative_point()
            for h in (0, 90, 180, 270):
                add("sq%d_%d" % (w["id"], h), c.x, c.y, h)
            continue
        steps = t["highway"] == "steps"
        sstep = 15.0
        k = 0
        s = 2.0
        while s < ln.length - 1.0:
            p, q = ln.interpolate(s), ln.interpolate(min(ln.length, s + 1.0))
            h = math.degrees(math.atan2(q.x - p.x, q.y - p.y))
            add("w%d_%d_f" % (w["id"], k), p.x, p.y, h, -20 if steps else -6)
            add("w%d_%d_b" % (w["id"], k), p.x, p.y, h + 180, -20 if steps else -6)
            if k % 2 == 0:
                add("w%d_%d_d" % (w["id"], k), p.x, p.y, h + 90 * ((k // 2) % 2 * 2 - 1), -38)
            k += 1
            s += sstep
            n += 1
    x0, y0, x1, y1 = reg.bounds
    gx = x0 + 20
    i = 0
    while gx < x1:
        gy = y0 + 20
        while gy < y1:
            if reg.contains(Point(gx, gy)):
                views.append({"id": "air_%d_%d" % (gx, gy), "x": round(gx, 1), "y": round(gy, 1), "z_eye": 28,
                              "heading": (i * 90 + 45) % 360, "pitch": -40, "fov": 70})
                i += 1
            gy += 45
        gx += 45
    rf = ROOT / "data/qa/regression.json"
    if rf.exists():
        for v in json.loads(rf.read_text()):
            if reg.contains(Point(v["x"], v["y"])):
                views.append(dict(v, id="reg_" + v["id"]))
    json.dump(views, open(out, "w"), indent=0)
    print("%d views (%d street samples) for %s" % (len(views), n, region_name))


if __name__ == "__main__":
    main()
