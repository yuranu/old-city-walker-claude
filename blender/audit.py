"""Geometry audit for the built scene: finds z-fighting and broken geometry.

    blender -b build/city.blend --python-exit-code 1 -P blender/audit.py -- [--top 40] [--json out.json]

Reports
* coplanar overlaps: triangles from different source polygons lying in the same plane
  (within 4 mm), facing the same way and overlapping in area -> flicker in the engine
* degenerate triangles (sliver area / extreme aspect)
* open boundary edges above ground level (holes, unclosed walls)
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(next((ROOT / ".venv/lib").glob("python3*/site-packages"))))
from shapely import STRtree  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--json", default="")
    p.add_argument("--min-area", type=float, default=0.02)
    return p.parse_args(argv)


def plane_basis(n):
    a = Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))
    u = n.cross(a).normalized()
    return u, n.cross(u)


def main():
    a = args()
    tris = []           # (obj, poly_index, material, [v0,v1,v2] world)
    boundary = []
    degenerate = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.visible_get():
            continue
        me = ob.data
        me.calc_loop_triangles()
        mw = ob.matrix_world
        verts = [mw @ v.co for v in me.vertices]
        mats = [m.name if m else "" for m in me.materials]
        for lt in me.loop_triangles:
            p = [verts[i] for i in lt.vertices]
            area = (p[1] - p[0]).cross(p[2] - p[0]).length / 2
            longest = max((p[1] - p[0]).length, (p[2] - p[1]).length, (p[0] - p[2]).length)
            if area < 1e-6 or (longest > 0.5 and area / (longest * longest) < 1e-4):
                degenerate.append({"obj": ob.name, "at": [round(c, 2) for c in (sum(p, Vector()) / 3)],
                                   "area": area})
                continue
            tris.append((ob.name, lt.polygon_index, mats[lt.material_index] if mats else "", p))
        bm = bmesh.new()
        bm.from_mesh(me)
        for e in bm.edges:
            if e.is_boundary:
                c = mw @ ((e.verts[0].co + e.verts[1].co) / 2)
                if c.z > 0.3 and (e.verts[0].co - e.verts[1].co).length > 0.05:
                    boundary.append((ob.name, [round(c.x, 1), round(c.y, 1), round(c.z, 1)]))
        bm.free()

    # bucket by plane
    buckets = defaultdict(list)
    for t in tris:
        p = t[3]
        n = (p[1] - p[0]).cross(p[2] - p[0]).normalized()
        d = n.dot(p[0])
        key = (round(n.x * 50), round(n.y * 50), round(n.z * 50), round(d / 0.02))   # coarse prefilter
        buckets[key].append((t, n))

    issues = []
    seen = set()
    for key, items in buckets.items():
        # merge with the neighbouring offset bucket so near-coplanar pairs are caught too
        cand = items + buckets.get((key[0], key[1], key[2], key[3] + 1), [])
        if len(cand) < 2:
            continue
        n = cand[0][1]
        u, v = plane_basis(n)
        polys = []
        for (t, _) in cand:
            q = Polygon([(pt.dot(u), pt.dot(v)) for pt in t[3]])
            polys.append(q if q.is_valid else q.buffer(0))
        tree = STRtree(polys)
        for i, j in zip(*tree.query(polys, predicate="intersects")):
            if i >= j:
                continue
            ti, tj = cand[i][0], cand[j][0]
            if ti[0] == tj[0] and ti[1] == tj[1]:
                continue                                  # same source polygon
            ci, cj = sum(ti[3], Vector()) / 3, sum(tj[3], Vector()) / 3
            if abs(cand[i][1].dot(cj - ci)) > 0.004 or cand[i][1].dot(cand[j][1]) < 0.999:
                continue                                  # precise local test: not within 4 mm of one plane
            if "decal" in (ti[2], tj[2]):
                continue                                  # blended, no depth write + polygon offset in the game
            ov = polys[i].intersection(polys[j]).area
            if ov < a.min_area:
                continue
            c = (sum(ti[3], Vector()) + sum(tj[3], Vector())) / 6
            k = (ti[0], tj[0], round(c.x), round(c.y), round(c.z))
            if k in seen:
                continue
            seen.add(k)
            issues.append({"a": ti[0], "b": tj[0], "mat_a": ti[2], "mat_b": tj[2], "area": round(ov, 3),
                           "at": [round(c.x, 1), round(c.y, 1), round(c.z, 1)], "normal": [round(x, 2) for x in n]})

    issues.sort(key=lambda r: -r["area"])
    by_pair = defaultdict(lambda: [0, 0.0])
    for r in issues:
        kk = (r["a"], r["b"], r["mat_a"], r["mat_b"])
        by_pair[kk][0] += 1
        by_pair[kk][1] += r["area"]
    print("AUDIT triangles %d  coplanar-overlaps %d (%.1f m2)  degenerate %d  open-edges(above 0.3 m) %d" %
          (len(tris), len(issues), sum(r["area"] for r in issues), len(degenerate), len(boundary)))
    print("AUDIT worst object pairs:")
    for kk, (cnt, ar) in sorted(by_pair.items(), key=lambda x: -x[1][1])[:a.top]:
        print("   %4d  %7.2f m2  %s [%s] x %s [%s]" % (cnt, ar, kk[0], kk[2], kk[1], kk[3]))
    print("AUDIT largest overlaps:")
    for r in issues[:a.top]:
        print("   %6.2f m2 at %s n=%s  %s/%s x %s/%s" % (r["area"], r["at"], r["normal"], r["a"], r["mat_a"], r["b"], r["mat_b"]))
    ob_b = defaultdict(int)
    for o, _ in boundary:
        ob_b[o] += 1
    print("AUDIT open edges by object:", sorted(ob_b.items(), key=lambda x: -x[1])[:15])
    if a.json:
        Path(a.json).write_text(json.dumps({"overlaps": issues, "degenerate": degenerate[:500],
                                            "boundary": boundary[:2000]}))


if __name__ == "__main__":
    main()
