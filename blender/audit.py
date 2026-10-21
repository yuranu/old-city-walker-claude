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
import shapely  # noqa: E402
from shapely import STRtree  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--json", default="")
    p.add_argument("--min-area", type=float, default=0.02)
    p.add_argument("--bbox", default="", help="x0,y0,x1,y1: only triangles whose centre lies inside")
    return p.parse_args(argv)


def plane_basis(n):
    a = Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))
    u = n.cross(a).normalized()
    return u, n.cross(u)


def main():
    import numpy as np
    a = args()
    bb = [float(v) for v in a.bbox.split(",")] if a.bbox else None
    boundary = []
    degenerate = []
    names, matnames = [], []                  # object names; material names (global ids)
    Ps, Os, Qs, Ms = [], [], [], []            # per object: triangles (n,3,3), object id, polygon index, material id
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.visible_get():
            continue
        me = ob.data
        me.calc_loop_triangles()
        nv, nt = len(me.vertices), len(me.loop_triangles)
        if not nt:
            continue
        co = np.empty(nv * 3, np.float32)
        me.vertices.foreach_get("co", co)
        M = np.array(ob.matrix_world, np.float64)
        co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
        tv = np.empty(nt * 3, np.int32)
        me.loop_triangles.foreach_get("vertices", tv)
        tp = np.empty(nt, np.int32)
        me.loop_triangles.foreach_get("polygon_index", tp)
        tm = np.empty(nt, np.int32)
        me.loop_triangles.foreach_get("material_index", tm)
        P = co[tv.reshape(-1, 3)]
        if bb:                                                # only triangles whose centre lies in the box
            c = P.mean(axis=1)
            keep = (c[:, 0] >= bb[0]) & (c[:, 0] <= bb[2]) & (c[:, 1] >= bb[1]) & (c[:, 1] <= bb[3])
            P, tp, tm = P[keep], tp[keep], tm[keep]
        mats = [m.name if m else "" for m in me.materials] or [""]
        mid = []
        for m_ in mats:
            if m_ not in matnames:
                matnames.append(m_)
            mid.append(matnames.index(m_))
        cr = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        area = np.linalg.norm(cr, axis=1) / 2
        longest = np.max(np.stack([np.linalg.norm(P[:, 1] - P[:, 0], axis=1), np.linalg.norm(P[:, 2] - P[:, 1], axis=1),
                                   np.linalg.norm(P[:, 0] - P[:, 2], axis=1)]), axis=0)
        bad = (area < 1e-6) | ((longest > 0.5) & (area / np.maximum(longest * longest, 1e-12) < 1e-4))
        for k in np.nonzero(bad)[0][:200]:
            degenerate.append({"obj": ob.name, "at": [round(float(v), 2) for v in P[k].mean(axis=0)], "area": float(area[k])})
        ok = ~bad
        names.append(ob.name)
        if nt > 200000:
            print("AUDIT %s: %d triangles, %d in the box" % (ob.name, nt, int(ok.sum())), flush=True)
        Ps.append(P[ok])
        Os.append(np.full(int(ok.sum()), len(names) - 1, np.int32))
        Qs.append(tp[ok])
        Ms.append(np.asarray(mid, np.int32)[np.clip(tm[ok], 0, len(mid) - 1)])
        if not bb:                                            # (open edges: whole-scene audits only)
            bm = bmesh.new()
            bm.from_mesh(me)
            mw = ob.matrix_world
            for e in bm.edges:
                if e.is_boundary:
                    c = mw @ ((e.verts[0].co + e.verts[1].co) / 2)
                    if c.z > 0.3 and (e.verts[0].co - e.verts[1].co).length > 0.05:
                        boundary.append((ob.name, [round(c.x, 1), round(c.y, 1), round(c.z, 1)]))
            bm.free()
    P = np.concatenate(Ps) if Ps else np.zeros((0, 3, 3))
    O = np.concatenate(Os) if Os else np.zeros(0, np.int32)
    Q = np.concatenate(Qs) if Qs else np.zeros(0, np.int32)
    MT = np.concatenate(Ms) if Ms else np.zeros(0, np.int32)
    del Ps, Os, Qs, Ms
    ntri = len(P)
    seal_obj = np.array([n_.endswith("retaining_walls") for n_ in names] or [False])
    N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    D = (N * P[:, 0]).sum(1)
    C = P.mean(axis=1)
    # bucket by plane (coarse prefilter); each triangle also goes into the bucket one offset below, so a
    # near-coplanar pair straddling two offset buckets still meets in one
    kn = np.round(N * 50).astype(np.int64)
    kd = np.round(D / 0.02).astype(np.int64)
    idx = np.concatenate([np.arange(ntri), np.arange(ntri)])
    keys = np.stack([np.concatenate([kn[:, 0]] * 2), np.concatenate([kn[:, 1]] * 2), np.concatenate([kn[:, 2]] * 2),
                     np.concatenate([kd, kd - 1])], 1)
    order = np.lexsort(keys.T[::-1])
    keys, idx = keys[order], idx[order]
    brk = np.nonzero(np.any(keys[1:] != keys[:-1], axis=1))[0] + 1
    starts = np.concatenate([[0], brk])
    ends = np.concatenate([brk, [len(idx)]])
    issues = []
    seen = set()
    sizes = ends - starts
    print("AUDIT %d triangles, %d buckets, largest %s" % (ntri, len(sizes), sorted(sizes.tolist())[-5:]), flush=True)
    for s0, s1 in zip(starts, ends):
        if s1 - s0 < 2:
            continue
        g = idx[s0:s1]
        src = O[g].astype(np.int64) * 10_000_000 + Q[g]
        if np.all(src == src[0]):
            continue                                      # one source polygon only
        n = Vector(N[g[0]])
        u, v = plane_basis(n)
        uv = np.stack([P[g] @ np.array(u), P[g] @ np.array(v)], -1)          # (k, 3, 2)
        polys = shapely.make_valid(shapely.polygons(uv))
        I, J = STRtree(polys).query(polys, predicate="intersects")
        if len(I) > 200000:
            from collections import Counter
            print("AUDIT big bucket: %d tris, %d pairs, n=%s d=%.2f, objects %s" % (
                len(g), len(I), np.round(N[g[0]], 2).tolist(), float(D[g[0]]),
                Counter(names[o] for o in O[g]).most_common(4)), flush=True)
        m = I < J
        I, J = I[m], J[m]
        ti, tj = g[I], g[J]
        m = ~((O[ti] == O[tj]) & (Q[ti] == Q[tj]))                           # not the same source polygon
        m &= np.abs(((C[tj] - C[ti]) * N[ti]).sum(1)) <= 0.004                # within 4 mm of one plane
        m &= (N[ti] * N[tj]).sum(1) >= 0.999
        # one object, one material, horizontal (world-xy UVs): identical pixels, no visible flicker. This is
        # every pair of a flat plaza's ground triangles, so it goes before any geometry work
        m &= ~((O[ti] == O[tj]) & (MT[ti] == MT[tj]) & ((np.abs(N[ti, 2]) > 0.99) | seal_obj[O[ti]]))
        I, J, ti, tj = I[m], J[m], ti[m], tj[m]
        if not len(I):
            continue
        ov = np.concatenate([shapely.area(shapely.intersection(polys[I[k:k + 20000]], polys[J[k:k + 20000]]))
                             for k in range(0, len(I), 20000)])
        for k in np.nonzero(ov >= a.min_area)[0]:
            ma, mb_ = matnames[MT[ti[k]]], matnames[MT[tj[k]]]
            if "decal" in (ma, mb_):
                continue                                  # blended, no depth write + polygon offset in the game
            c = (C[ti[k]] + C[tj[k]]) / 2
            k_ = (names[O[ti[k]]], names[O[tj[k]]], round(c[0]), round(c[1]), round(c[2]))
            if k_ in seen:
                continue
            seen.add(k_)
            issues.append({"a": names[O[ti[k]]], "b": names[O[tj[k]]], "mat_a": ma, "mat_b": mb_, "area": round(float(ov[k]), 3),
                           "at": [round(float(c[0]), 1), round(float(c[1]), 1), round(float(c[2]), 1)],
                           "normal": [round(float(x), 2) for x in N[ti[k]]]})

    issues.sort(key=lambda r: -r["area"])
    by_pair = defaultdict(lambda: [0, 0.0])
    for r in issues:
        kk = (r["a"], r["b"], r["mat_a"], r["mat_b"])
        by_pair[kk][0] += 1
        by_pair[kk][1] += r["area"]
    print("AUDIT triangles %d  coplanar-overlaps %d (%.1f m2)  degenerate %d  open-edges(above 0.3 m) %d" %
          (ntri, len(issues), sum(r["area"] for r in issues), len(degenerate), len(boundary)))
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
