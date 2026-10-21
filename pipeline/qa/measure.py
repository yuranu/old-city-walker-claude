"""Geometry checks on the spec for a region (exhaustive, no rendering). Each finding names the
generator it most likely comes from, so fixes go to the rule, not the place.

    .venv/bin/python pipeline/qa/measure.py <region> <out findings.json>
"""
import json
import math
import sys
from pathlib import Path

from shapely import STRtree, make_valid, prepare
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, finding, load_spec, region_geom  # noqa: E402

WALL_PROPS = {"caper"}                         # grow out of walls, high above the ground


def main():
    reg = region_geom(sys.argv[1])
    out_path = Path(sys.argv[2])
    base, secs, blds = load_spec()
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    lids = set()
    lf = ROOT / "data/landmark_ids.json"
    if lf.exists():
        for v in json.loads(lf.read_text()).get("modules", {}).values():
            lids |= set(v or [])
    F = []
    rb = reg.buffer(5)
    blist = [(b, make_valid(Polygon(b["ring"]))) for b in blds]
    blist = [(b, p) for b, p in blist if p.intersects(rb)]
    bpolys = [p for _, p in blist]
    btree = STRtree(bpolys) if bpolys else None
    steps = [s for s in base.get("steps", []) if Polygon(s["poly"]["ext"]).intersects(rb)]
    spolys = [make_valid(Polygon(s["poly"]["ext"], s["poly"]["holes"])) for s in steps]
    tris = []
    for g in base["ground"]:
        for t in g["tris"]:
            P = Polygon([(p[0], p[1]) for p in t])
            if P.area > 1e-6 and P.intersects(rb):
                tris.append((P, t, g["mat"]))
    ttree = STRtree([P for P, _, _ in tris]) if tris else None

    def ground_z(x, y):
        pt = Point(x, y)
        for k in (ttree.query(pt) if ttree else []):
            P, t, _ = tris[k]
            if P.buffer(1e-6).contains(pt):
                (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
                den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
                if abs(den) < 1e-12:
                    return z1
                a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / den
                b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / den
                return a * z1 + b * z2 + (1 - a - b) * z3
        for k, sp in enumerate(spolys):
            if sp.contains(pt):
                return steps[k]["top"]
        return None

    # 1 ground gaps: open area covered by nothing walkable
    cit = base.get("citadel") or {}
    cit_mass = [make_valid(Polygon(cit["mass"]))] if cit.get("mass") else []     # built solid by landmarks_gates
    holes = [make_valid(Polygon(h_)) for h_ in base.get("ground_holes", [])]     # closed in by landmark walls
    cover = unary_union([P for P, _, _ in tris] + spolys + bpolys + cit_mass + holes)
    gaps = reg.difference(cover)
    for p in getattr(gaps, "geoms", [gaps]):
        if p.geom_type == "Polygon" and p.area > 1.5 and not p.buffer(-0.3).is_empty:
            c = p.representative_point()
            F.append(finding("ground_gap", 0, "high", c.x, c.y, what="%.1f m2 with no ground, step or building" % p.area,
                             source="make_spec ground regions / steps_union / buildings", evidence={"area": round(p.area, 1)}))
    # 2 spikes: ground no street could have
    lm_polys = [p for b, p in blist if b["osm"] in lids]
    lm_u = unary_union(lm_polys) if lm_polys else None
    for P, t, mat in tris:
        if not reg.intersects(P):
            continue
        if lm_u is not None and lm_u.contains(P.centroid):
            continue                                   # ground under a landmark: hidden by its floors
        zs = [q[2] for q in t]
        dz = max(zs) - min(zs)
        L = max(math.dist(t[i][:2], t[(i + 1) % 3][:2]) for i in range(3))
        if dz > 0.8 and dz / max(L, 0.1) > 0.6:
            c = P.centroid
            if dz <= 4.0 and dz / max(L, 0.1) <= 1.2:     # a steep but smooth slope (the terrain itself):
                F.append(finding("steep_ground", 1, "medium", c.x, c.y, sum(zs) / 3,    # wants terraces or steps
                                 what="paved slope of %.0f%% (%.1f m over %.1f m, %s)" % (100 * dz / max(L, 0.1), dz, L, mat),
                                 source="terrain: no steps or retaining walls on a steep open slope"))
                continue
            F.append(finding("spike", 0, "high" if dz > 2 else "medium", c.x, c.y, sum(zs) / 3,
                             what="ground triangle rises %.1f m over %.1f m (%s)" % (dz, L, mat),
                             source="terrain / flats edges in tess_regions"))
    # 3 retaining walls across walkways
    streets = []
    for w in osm["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if t.get("highway") and len(pts) > 1 and t.get("area") != "yes" and int(t.get("layer", "0") or 0) >= -1 \
                and t.get("bridge") != "yes":         # (a wall under a bridge blocks nothing)
            ln = LineString(pts)
            if ln.intersects(rb):
                streets.append((w, ln))
    stree = STRtree([ln for _, ln in streets]) if streets else None
    for r in base.get("retaining", []):
        ln = LineString([r["a"], r["b"]])
        if not ln.intersects(reg):
            continue
        if lm_u is not None and lm_u.buffer(0.1).contains(ln):
            continue                                   # the edge of a landmark: its own walls stand there
        h = max(r["hi"][0] - r["lo"][0], r["hi"][1] - r["lo"][1]) - 0.3
        for k in (stree.query(ln) if stree else []):
            if streets[k][0]["tags"].get("tunnel") == "yes":
                continue                               # (a tunnel ends at a door or a wall: the Haram gates)
            if streets[k][1].intersects(ln) and h > 0.4:
                c = ln.interpolate(0.5, normalized=True)
                F.append(finding("wall_across_street", 0, "high", c.x, c.y, what="retaining wall %.1f m high across %s"
                                 % (h, streets[k][0]["tags"].get("name:en") or streets[k][0]["id"]),
                                 source="make_spec retaining walls (flat edges)"))
                break
    # 4 blocked centrelines
    for w, ln in streets:
        for k in (btree.query(ln) if btree else []):
            b, p = blist[k]
            if b["osm"] in lids:
                continue
            L = ln.intersection(p).length
            if L > 1.0 and reg.intersects(ln.intersection(p)):
                c = ln.intersection(p).centroid
                F.append(finding("blocked_street", 0, "high", c.x, c.y, what="%s runs %.1f m inside %s" %
                                 (w["tags"].get("name:en") or w["id"], L, b["id"]), source="footprints / infill / passages"))
    # 5 treads overlapping each other or buildings; treads off the street
    stt = STRtree(spolys) if spolys else None
    for i, sp in enumerate(spolys):
        if not reg.intersects(sp):
            continue
        for j in stt.query(sp):
            if j > i and sp.intersection(spolys[j]).area > 0.05:
                c = sp.intersection(spolys[j]).representative_point()
                F.append(finding("steps_overlap", 0, "high", c.x, c.y, what="treads overlap (%.2f m2)" % sp.intersection(spolys[j]).area,
                                 source="stairs.build clipping"))
        for k in (btree.query(sp) if btree else []):
            if sp.intersection(bpolys[k]).area > 0.1:
                c = sp.intersection(bpolys[k]).representative_point()
                F.append(finding("steps_in_building", 0, "high", c.x, c.y, what="tread inside %s" % blist[k][0]["id"],
                                 source="stairs.build / footprints"))
    # 6 floating / buried props on the ground
    for sid, d in secs.items():
        for pr in d.get("props", []):
            x, y, z = pr["p"]
            if pr["type"] in WALL_PROPS or not reg.contains(Point(x, y)):
                continue
            if btree is not None and any(bpolys[k].contains(Point(x, y)) for k in btree.query(Point(x, y))):
                continue                              # rooftop clutter
            gz = ground_z(x, y)
            if gz is not None and abs(gz - z) > 0.3:
                F.append(finding("prop_float" if z > gz else "prop_buried", 0, "medium", x, y, z,
                                 what="%s %.2f m %s the ground" % (pr["type"], abs(gz - z), "above" if z > gz else "below"),
                                 source="dressing zat / profile props"))
    # 7 overlapping buildings
    for i, p in enumerate(bpolys):
        if not reg.intersects(p):
            continue
        for j in btree.query(p):
            if j > i:
                a = p.intersection(bpolys[j]).area
                if a > 0.5:
                    c = p.intersection(bpolys[j]).representative_point()
                    F.append(finding("buildings_overlap", 0, "high", c.x, c.y, what="%s and %s overlap %.1f m2" %
                                     (blist[i][0]["id"], blist[j][0]["id"], a), source="footprint priority pass / landmarks"))
    out_path.write_text(json.dumps(F, indent=1))
    kinds = {}
    for f in F:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    print("measure %s: %s" % (sys.argv[1], kinds))


if __name__ == "__main__":
    main()
