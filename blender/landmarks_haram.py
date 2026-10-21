"""Temple Mount / Haram al-Sharif landmarks and the Western Wall (registry: landmarks.py).

    LANDMARKS = {osm_id: fn}      fn(mbs, bd, gen, place, lod=False)

Reference, dimensions with sources and confidence, and the checklist: data/reference/landmarks_haram.md.
Photos: data/photos_ref/landmarks_haram/ (keys H:NN in the notes and comments below).

Levels: everything is keyed to bd["ground"] (the esplanade is one flat in data/terrain_street.json)
and bd["edge_ground"] (the Western Wall plaza); no absolute z anywhere.  The upper platform of the
Dome of the Rock is built here as a walkable solid, PLAT_H above the esplanade (terrain agent:
742.2 m asl vs 737.07 m, docs/TERRAIN.md); the buildings standing on it are lifted onto it.

Plan positions that are not in any building record come from OSM and are module constants:
the platform outline (retaining wall w137725307 united with the eight qanatir strips), Dome of the
Prophet w291836680, Wilson's Arch hall w499210296, the dome parts w291844838 / w291836700 /
w291836701, the minaret nodes n13791836098 / n13792233802 and the Wikidata positions of the
Ghawanima (Q25450229) and Bab al-Asbat (Q6863203) minarets.  Those pieces hang off a registered
landmark's builder so they get an LOD too.

Collision: "solid" collides, "deco" does not.  Arcades (qanatir, Dome of the Chain) collide on
their piers and columns only.
"""
import json
import math
import random
from pathlib import Path

from mathutils import Vector, geometry

import meshkit as mk

ROOT = Path(__file__).resolve().parent.parent
UP = Vector((0, 0, 1))
PLAT_H = 5.1                 # upper platform above the esplanade (terrain: 742.2 vs 737.07 m asl)
STONE = (1.0, 0.98, 0.94)
PALE = (1.0, 1.0, 1.0)
WARM = (1.0, 0.95, 0.86)
GREYSTONE = (0.92, 0.91, 0.88)

# ---------------------------------------------------------------- OSM-derived plan constants
# upper platform: OSM retaining wall w137725307 united with the eight qanatir strips (shapely, 5 cm simplify)
PLATFORM = [(695.31, 87.30), (695.56, 86.02), (712.71, 89.35), (713.69, 84.34), (724.48, 86.29), (723.96, 89.05),
            (726.64, 89.56), (727.16, 86.80), (741.11, 89.48), (747.93, 90.70), (791.29, 97.93), (797.50, 99.05),
            (797.68, 87.31), (817.91, 91.95), (816.67, 164.42), (815.22, 174.28), (814.49, 210.13), (813.17, 210.16),
            (813.41, 240.38), (813.50, 265.07), (772.30, 259.75), (772.04, 261.88), (762.12, 260.64), (762.71, 255.95),
            (755.36, 255.03), (755.03, 257.60), (730.80, 254.58), (730.53, 256.69), (718.00, 255.13), (718.72, 249.45),
            (713.28, 248.78), (712.84, 252.34), (673.47, 247.42), (675.55, 230.87), (662.27, 229.22), (662.51, 227.33),
            (660.20, 227.04), (670.43, 181.88), (672.90, 182.35), (673.68, 178.19), (671.25, 177.73), (677.71, 144.88),
            (696.09, 148.79), (699.21, 134.32), (680.61, 131.10), (683.20, 116.88), (689.24, 86.12)]
PLAT_C = (746.26, 175.36)
QANATIR = ("w748953239", "w748953246", "w748953248", "w748953252", "w291841778", "w748953265", "w748953254",
           "w748953257")
DOME_PROPHET = (709.55, 174.84)          # w291836680, octagon r ~1.4 m
WILSON_HALL = [(621.91, 30.53), (646.06, 35.24), (640.68, 62.55), (639.28, 62.27), (626.48, 59.77), (629.03, 46.85),
               (619.07, 44.91)]          # w499210296 (layer -1), south front (621.9,30.5)-(646.1,35.2)
AQSA_DOME = (770.17, -76.97)             # w291844838 building:part, r_eq 7.2 m
GG_DOMES = [((908.00, 261.63), 2.98), ((908.55, 255.53), 2.61)]   # w291836700 / w291836701
# minarets: (name, centre, kind); orientation follows the nearest Haram wall
MINARETS = [
    ("Bab al-Silsila", (640.0, 84.0), "silsila"),        # OSM node 13791836098 (Wikidata Q53535830 is 15 m N)
    ("al-Fakhriyya", (687.0, -82.0), "fakhriyya"),       # OSM node 13792233802 (SW corner)
    ("al-Ghawanima", (587.23, 370.77), "ghawanima"),     # Wikidata Q25450229 (NW corner)
    ("Bab al-Asbat", (840.23, 398.60), "asbat"),         # Wikidata Q6863203 (north wall)
]
WEST_WALL_BEARING = math.atan2(-0.983, 0.183)            # Haram west wall direction (heading NNW), plan
NORTH_WALL_DIR = (0.993, 0.12)                           # north wall heading E


# ================================================================== small geometry kit
def V(x, y, z=0.0):
    return Vector((x, y, z))


class Edge:
    """Frame of a->b: u along, z up, off along the outward (right-hand) normal of a CCW ring."""

    def __init__(self, a, b):
        self.A = Vector((a[0], a[1], 0.0))
        d = Vector((b[0], b[1], 0.0)) - self.A
        self.L = d.length
        self.t = d / self.L if self.L > 1e-9 else Vector((1, 0, 0))
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, u, z, off=0.0):
        return self.A + self.t * u + self.n * off + Vector((0, 0, z))


def area2(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def ccw(r):
    r = [tuple(p) for p in r]
    return r if area2(r) > 0 else r[::-1]


def centroid(r):
    a = area2(r)
    if abs(a) < 1e-9:
        return (sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r))
    cx = cy = 0.0
    for i in range(len(r)):
        x0, y0 = r[i]
        x1, y1 = r[(i + 1) % len(r)]
        f = x0 * y1 - x1 * y0
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    return (cx / (6 * a), cy / (6 * a))


def face(mb, e, outline, mat, off=0.0, holes=(), col=None, inward=False, uvf=None):
    """Planar polygon in the plane of edge e (outline/holes in (u, z)); constrained Delaunay."""
    nrm = -e.n if inward else e.n
    verts, faces = [], []
    for r in [outline] + list(holes):
        r = [Vector((p[0], p[1])) for p in r]
        faces.append(list(range(len(verts), len(verts) + len(r))))
        verts += r
    try:
        ov, _e, of, _ov, _oe, origf = geometry.delaunay_2d_cdt(verts, [], faces, 1, 1e-5)
    except Exception:                                   # noqa: BLE001
        flat, tris = mk.tess2d([list(outline)] + [list(h) for h in holes])
        for a, b, c in tris:
            pts = [flat[a], flat[b], flat[c]]
            mb.poly([e.P(u, z, off) for u, z in pts], mat, nrm, col=col,
                    uv=[uvf(u, z) for u, z in pts] if uvf else None)
        return
    for f, o in zip(of, origf):
        if len(o) % 2 == 1 and len(f) >= 3:
            mb.poly([e.P(ov[i].x, ov[i].y, off) for i in f], mat, nrm, col=col,
                    uv=[uvf(ov[i].x, ov[i].y) for i in f] if uvf else None)


def cell_uv(gen, name):
    return tuple(gen["landmarks"]["faience"]["cells"][name])


def rect_map(rect, ua, ub, za, zb, fu=(0.0, 1.0), fz=(0.0, 1.0)):
    """(u, z) in [ua, ub] x [za, zb] -> UV inside rect (optionally a sub-range fu/fz of the cell)."""
    U0, V0, U1, V1 = rect
    du, dv = U1 - U0, V1 - V0

    def f(u, z):
        s = fu[0] + (u - ua) / max(ub - ua, 1e-9) * (fu[1] - fu[0])
        t = fz[0] + (z - za) / max(zb - za, 1e-9) * (fz[1] - fz[0])
        return (U0 + s * du, V0 + t * dv)
    return f


def quad_uv(mb, pts, mat, hint, rect, col=None):
    U0, V0, U1, V1 = rect
    mb.poly(pts, mat, hint, uv=[(U0, V0), (U1, V0), (U1, V1), (U0, V1)], col=col)


def arch_curve(u0, u1, zs, kind="pointed", seg=8, k=0.85):
    """Intrados points from the left springer (u0, zs) to the right one (u1, zs), inclusive."""
    w = u1 - u0
    if kind == "round":
        return [((u0 + u1) / 2 - math.cos(math.pi * i / seg) * w / 2, zs + math.sin(math.pi * i / seg) * w / 2)
                for i in range(seg + 1)]
    if kind == "flat":
        return [(u0, zs), (u1, zs)]
    R = k * w
    amax = math.acos(max(-1.0, min(1.0, (w / 2 - R) / R)))
    half = max(2, seg // 2)
    left = [(u0 + R + R * math.cos(math.pi - (math.pi - amax) * i / half), zs + R * math.sin(math.pi - (math.pi - amax) * i / half))
            for i in range(half + 1)]
    right = [(u1 - R + R * math.cos(amax - amax * i / half), zs + R * math.sin(amax - amax * i / half))
             for i in range(1, half + 1)]
    return left + right


def arch_rise(w, kind="pointed", k=0.85):
    if kind == "round":
        return w / 2
    if kind == "flat":
        return 0.0
    R = k * w
    return math.sqrt(max(0.0, R * R - (R - w / 2) ** 2))


def opening(u0, u1, z0, zs, kind="pointed", seg=8, k=0.85):
    """Closed CCW outline of an arched opening: jambs from z0 to the springing zs, then the arch."""
    c = arch_curve(u0, u1, zs, kind, seg, k)
    return [(u0, z0), (u1, z0)] + c[::-1]


def reveal(mb, e, ol, off0, off1, mat, col=None, skip_bottom=True, uvf=None):
    """Tube joining the closed (u, z) outline ol at off0 and off1, faces looking at the axis."""
    cu = sum(p[0] for p in ol) / len(ol)
    cz = sum(p[1] for p in ol) / len(ol)
    n = len(ol)
    for i in range(n):
        a, b = ol[i], ol[(i + 1) % n]
        if skip_bottom and abs(a[1] - b[1]) < 1e-6 and a[1] <= min(p[1] for p in ol) + 1e-6:
            continue
        q = [e.P(a[0], a[1], off0), e.P(b[0], b[1], off0), e.P(b[0], b[1], off1), e.P(a[0], a[1], off1)]
        mid = (q[0] + q[2]) / 2
        hint = e.P(cu, cz, (off0 + off1) / 2) - mid
        mb.poly(q, mat, hint, col=col, uv=uvf(a, b) if uvf else None)


def arch_band(mb, e, cv_i, cv_o, off, mat, col=None):
    """Flat arch band (archivolt / frame) between the inner and outer curves, as two planar halves
    split at the apex: no overlapping quads near the crown."""
    h = len(cv_i) // 2
    for a, b in ((0, h + 1), (h, len(cv_i))):
        face(mb, e, list(cv_o[a:b]) + list(cv_i[a:b])[::-1], mat, off=off, col=col)


def corner_undersides(mb, Po, Pi, z, w, mat="dressed", col=PALE):
    """Soffits over the columns of an arcade ring (outer ring Po, inner Pi, same vertex angles):
    two quads per corner, from w before to w after the vertex along each side."""
    n = len(Po)
    for k in range(n):
        ep, en = Edge(Po[k - 1], Po[k]), Edge(Po[k], Po[(k + 1) % n])
        eip, ein = Edge(Pi[k - 1], Pi[k]), Edge(Pi[k], Pi[(k + 1) % n])
        shp, shn = (ep.L - eip.L) / 2, (en.L - ein.L) / 2
        mb.poly([ep.P(ep.L - w, z), ep.P(ep.L, z), eip.P(eip.L, z), eip.P(ep.L - w - shp, z)], mat, -UP, col=col)
        mb.poly([en.P(0, z), en.P(w, z), ein.P(w - shn, z), ein.P(0, z)], mat, -UP, col=col)


def obox(mb, c, t, lt, ls, z0, z1, mat, col=None, top=True, bottom=False):
    t = Vector((t[0], t[1], 0)).normalized()
    s = Vector((-t.y, t.x, 0))
    mk.box(mb, c, t, s, lt, ls, z0, z1, mat, top=top, bottom=bottom, col=col)


def wbox(mb, e, u, off_c, lt, ls, z0, z1, mat, col=None, top=True, bottom=False):
    """Box mounted on the wall of edge e (centre at u, off_c > 0 outside): no face against the wall."""
    c = e.P(u, 0, off_c)
    mk.box(mb, c, e.t, e.n, lt, ls, z0, z1, mat, top=top, bottom=bottom, col=col, back=False)


def prism_walls(mb, ring, z0, z1, mat, col=None, skip=()):
    for i in range(len(ring)):
        if i in skip:
            continue
        a, b = ring[i], ring[(i + 1) % len(ring)]
        mb.poly([V(a[0], a[1], z0), V(b[0], b[1], z0), V(b[0], b[1], z1), V(a[0], a[1], z1)], mat,
                V(b[1] - a[1], -(b[0] - a[0])), col=col)


def cap(mb, ring, z, mat, col=None, down=False, holes=()):
    fl, ft = mk.tess2d([list(ring)] + [list(h) for h in holes])
    mb.tris([V(p[0], p[1], z) for p in fl], ft, mat, -UP if down else UP, col=col)


def reg_poly(c, R, n, a0):
    return [(c[0] + R * math.cos(a0 + 2 * math.pi * k / n), c[1] + R * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def offset_reg(R, n, d):
    """Vertex radius of a regular n-gon whose sides are moved out by d."""
    return R + d / math.cos(math.pi / n)


def band(mb, outer, z0, z1, mat, inner=None, col=None, top=True, bottom=False):
    """Ring-shaped moulding: vertical outer faces, top / bottom annulus to the inner ring."""
    prism_walls(mb, outer, z0, z1, mat, col)
    if inner is not None:
        n = len(outer)
        for i in range(n):
            a, b = outer[i], outer[(i + 1) % n]
            c, d = inner[(i + 1) % n], inner[i]
            if top:
                mb.poly([V(*a, z1), V(*b, z1), V(*c, z1), V(*d, z1)], mat, UP, col=col)
            if bottom:
                mb.poly([V(*a, z0), V(*b, z0), V(*c, z0), V(*d, z0)], mat, -UP, col=col)
    elif top:
        cap(mb, outer, z1, mat, col)


def cylinder_uv(mb, cx, cy, z0, z1, r, mat, rect=None, seg=12, col=None, r1=None, tile=None):
    """Vertical cylinder side; UVs wrap once around rect (an atlas cell) or tile in metres."""
    r1 = r if r1 is None else r1
    for k in range(seg):
        a0, a1 = 2 * math.pi * k / seg, 2 * math.pi * (k + 1) / seg
        p = [V(cx + r * math.cos(a0), cy + r * math.sin(a0), z0), V(cx + r * math.cos(a1), cy + r * math.sin(a1), z0),
             V(cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z1), V(cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z1)]
        if rect:
            U0, V0, U1, V1 = rect
            uv = [(U0 + (U1 - U0) * k / seg, V0), (U0 + (U1 - U0) * (k + 1) / seg, V0),
                  (U0 + (U1 - U0) * (k + 1) / seg, V1), (U0 + (U1 - U0) * k / seg, V1)]
        else:
            t = tile or 2.0
            c = 2 * math.pi * r / t
            uv = [(c * k / seg, z0 / t), (c * (k + 1) / seg, z0 / t), (c * (k + 1) / seg, z1 / t), (c * k / seg, z1 / t)]
        mb.poly(p, mat, V(math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2)), uv=uv, col=col)


def dome_uv(mb, cx, cy, z, r, mat, k=1.0, seg=24, rings=8, tile=2.0, col=None, n_u=None):
    """Pointed (k > 1) or hemispherical (k = 1) dome; u along the parallels (n_u repeats around),
    v along the meridians in metres / tile.  Returns the apex z."""
    R = k * r
    amax = math.acos(max(-1.0, min(1.0, (R - r) / R)))
    prof = []
    for j in range(rings + 1):
        a = amax * j / rings
        prof.append(((r - R) + R * math.cos(a), R * math.sin(a), R * a))   # radial, height, arc length
    prof[-1] = (0.0, prof[-1][1], prof[-1][2])
    nu = n_u if n_u is not None else max(1, round(2 * math.pi * r / tile))
    for j in range(rings):
        (r0, h0, s0), (r1, h1, s1) = prof[j], prof[j + 1]
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            u0, u1 = nu * i / seg, nu * (i + 1) / seg
            p00 = V(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0), z + h0)
            p01 = V(cx + r0 * math.cos(a1), cy + r0 * math.sin(a1), z + h0)
            p11 = V(cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z + h1)
            p10 = V(cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z + h1)
            hint = (p00 + p11) / 2 - V(cx, cy, z)
            if j == rings - 1:
                mb.poly([p00, p01, p11], mat, hint, uv=[(u0, s0 / tile), (u1, s0 / tile), ((u0 + u1) / 2, s1 / tile)], col=col)
            else:
                mb.poly([p00, p01, p11, p10], mat, hint,
                        uv=[(u0, s0 / tile), (u1, s0 / tile), (u1, s1 / tile), (u0, s1 / tile)], col=col)
    return z + prof[-1][1]


def ball(mb, c, r, mat, seg=8, rings=4, col=None):
    for j in range(rings):
        p0, p1 = -math.pi / 2 + math.pi * j / rings, -math.pi / 2 + math.pi * (j + 1) / rings
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            q = [V(c[0] + r * math.cos(p0) * math.cos(a0), c[1] + r * math.cos(p0) * math.sin(a0), c[2] + r * math.sin(p0)),
                 V(c[0] + r * math.cos(p0) * math.cos(a1), c[1] + r * math.cos(p0) * math.sin(a1), c[2] + r * math.sin(p0)),
                 V(c[0] + r * math.cos(p1) * math.cos(a1), c[1] + r * math.cos(p1) * math.sin(a1), c[2] + r * math.sin(p1)),
                 V(c[0] + r * math.cos(p1) * math.cos(a0), c[1] + r * math.cos(p1) * math.sin(a0), c[2] + r * math.sin(p1))]
            if j == 0:
                q = [q[0], q[2], q[3]]
            elif j == rings - 1:
                q = q[:3]
            mb.poly(q, mat, (q[0] + q[-1]) / 2 - V(*c), col=col)


def finial(mb, cx, cy, z, h, mat="gold", crescent=True, face_dir=(0.0, 1.0), lod=False):
    """Pole with balls and a crescent (horns up) on top of a dome; h = total height."""
    if lod:
        mk.cylinder(mb, cx, cy, z - 0.2, z + h, 0.12 * h / 3, mat, seg=4)
        return
    mk.cylinder(mb, cx, cy, z - 0.3, z + 0.62 * h, 0.035 * h + 0.03, mat, seg=6)
    for f, rr in ((0.18, 0.11), (0.36, 0.14), (0.52, 0.09)):
        ball(mb, (cx, cy, z + f * h), rr * h / 2.2, mat, seg=8, rings=4)
    if crescent:
        R = 0.2 * h
        zc = z + 0.62 * h + R * 0.55
        fx, fy = face_dir
        side = Vector((-fy, fx, 0)).normalized()
        pts = []
        for i in range(9):
            a = math.radians(200 + 140 * i / 8)
            pts.append(V(cx, cy, zc) + side * (R * math.cos(a)) + UP * (R * math.sin(a)))
        mk.tube(mb, pts, 0.075 * h / 2, mat, sides=6)


# ================================================================== shared level helpers
_SPEC_CACHE = {}


def _sector_spec(part="s11_haram"):
    if part not in _SPEC_CACHE:
        try:
            _SPEC_CACHE[part] = json.loads((ROOT / ("data/spec/%s.json" % part)).read_text())
        except Exception:                               # noqa: BLE001
            _SPEC_CACHE[part] = {"buildings": []}
    return _SPEC_CACHE[part]


def esplanade(bd):
    """Esplanade level: the Dome of the Rock record's ground (the Haram is one flat), else bd's own."""
    for b in _sector_spec()["buildings"]:
        if b["id"] == "w4709536":
            return b["ground"]
    return bd["ground"]


def terrain_z(x, y, key="z_ground"):
    """Street-level terrain (data/terrain_street.json, bilinear), None when unavailable."""
    if "terrain" not in _SPEC_CACHE:
        try:
            _SPEC_CACHE["terrain"] = json.loads((ROOT / "data/terrain_street.json").read_text())
        except Exception:                               # noqa: BLE001
            _SPEC_CACHE["terrain"] = None
    d = _SPEC_CACHE["terrain"]
    if not d:
        return None
    gi, gj = (x - d["x0"]) / d["step"], (y - d["y0"]) / d["step"]
    i0, j0 = int(math.floor(gi)), int(math.floor(gj))
    if not (0 <= i0 < d["nx"] - 1 and 0 <= j0 < d["ny"] - 1):
        return None
    fi, fj = gi - i0, gj - j0
    z = d[key]
    return (z[j0][i0] * (1 - fi) * (1 - fj) + z[j0][i0 + 1] * fi * (1 - fj) + z[j0 + 1][i0] * (1 - fi) * fj
            + z[j0 + 1][i0 + 1] * fi * fj)


def platform_top(bd):
    return esplanade(bd) + PLAT_H


def column(mb, gen, x, y, z0, h, r=0.26, seg=10, base=True, capital=True, col=None, lod=False):
    """Marble column (faience 'column' cell) with a stone base and a flared capital."""
    if lod:
        mk.cylinder(mb, x, y, z0, z0 + h, r, "dressed", seg=4, cap=False)
        return
    zb = z0 + (0.22 if base else 0.0)
    zc = z0 + h - (0.38 if capital else 0.0)
    if base:
        obox(mb, (x, y), (1, 0), 2.4 * r, 2.4 * r, z0 - 0.05, zb, "dressed", col=PALE)
    cylinder_uv(mb, x, y, zb, zc, r, "faience", rect=cell_uv(gen, "column"), seg=seg, col=col)
    if capital:
        cylinder_uv(mb, x, y, zc, zc + 0.24, r, "dressed", seg=seg, r1=r * 1.5, col=PALE)
        obox(mb, (x, y), (1, 0), 3.0 * r, 3.0 * r, zc + 0.24, z0 + h, "dressed", col=PALE, bottom=True)


# ================================================================== arcade (qanatir, porticoes)
def arcade(mbs, gen, e, u0, u1, off0, off1, z0, zs, z_top, n, kind="pointed", pier=1.0, col_r=0.27,
           mat="ashlar", col=STONE, cornice=True, lod=False, solid_piers=True):
    """Free-standing arcade along edge frame e between u0..u1, depth off0..off1 (off0 < off1):
    end piers, n arches on columns, an arch band from the springing zs to z_top.
    Piers and columns collide; the arch band is decoration."""
    sol, dec = mbs["solid"], mbs["deco"]
    d = off1 - off0
    om = (off0 + off1) / 2
    L = u1 - u0
    span = (L - 2 * pier) / n
    tvec = e.t
    # end piers
    for ua in (u0, u1 - pier):
        c = e.P(ua + pier / 2, 0, om)
        obox(sol, c, tvec, pier, d, z0 - 0.3, zs, mat, col=col, top=False)
    cols = [u0 + pier + span * i for i in range(1, n)]
    cw = 3.0 * col_r
    supports = [(u0, u0 + pier)] + [(c_ - cw / 2, c_ + cw / 2) for c_ in cols] + [(u1 - pier, u1)]
    for uc in cols:
        c = e.P(uc, 0, om)
        if lod:
            obox(sol, c, tvec, 0.5, 0.5, z0, zs, "dressed", col=PALE, top=False)
        else:
            column(sol, gen, c.x, c.y, z0, zs - z0, r=col_r, col=PALE)
    # arch band: front/back faces with arch notches, intrados, top, ends
    outline = [(u0, z_top), (u0, zs)]
    curves = []
    for i in range(n):
        a, b = supports[i][1], supports[i + 1][0]
        cv = arch_curve(a, b, zs, kind, 4 if lod else 10)
        curves.append(cv)
        outline += cv
    outline += [(u1, zs), (u1, z_top)]
    clean = [outline[0]]
    for p in outline[1:]:
        if (p[0] - clean[-1][0]) ** 2 + (p[1] - clean[-1][1]) ** 2 > 1e-8:
            clean.append(p)
    face(dec, e, clean, mat, off=off1, col=col)                           # outer face
    face(dec, e, clean, mat, off=off0, col=col, inward=True)              # inner face
    for cv in curves:                                                     # intrados
        for i in range(len(cv) - 1):
            a, b = cv[i], cv[i + 1]
            q = [e.P(a[0], a[1], off0), e.P(b[0], b[1], off0), e.P(b[0], b[1], off1), e.P(a[0], a[1], off1)]
            mid = (cv[0][0] + cv[-1][0]) / 2
            dec.poly(q, mat, e.P(mid, zs, om) - (q[0] + q[2]) / 2, col=col)
    for a, b in supports:                                                # undersides over piers/columns
        if b - a > 0.01:
            dec.poly([e.P(a, zs, off0), e.P(b, zs, off0), e.P(b, zs, off1), e.P(a, zs, off1)], mat, -UP, col=col)
    for ua, sgn in ((u0, -1), (u1, 1)):                                  # end faces of the band
        q = [e.P(ua, zs, off0), e.P(ua, zs, off1), e.P(ua, z_top, off1), e.P(ua, z_top, off0)]
        dec.poly(q, mat, tvec * sgn, col=col)
    zc = z_top
    if cornice and not lod:
        ov = 0.12
        dec.poly([e.P(u0 - ov, z_top, off0 - ov), e.P(u1 + ov, z_top, off0 - ov), e.P(u1 + ov, z_top, off1 + ov),
                  e.P(u0 - ov, z_top, off1 + ov)], "dressed", -UP, col=PALE)
        obox(dec, e.P((u0 + u1) / 2, 0, om), tvec, L + 2 * ov, d + 2 * ov, z_top, z_top + 0.28, "dressed", col=PALE)
        zc = z_top + 0.28
    else:
        dec.poly([e.P(u0, z_top, off0), e.P(u1, z_top, off0), e.P(u1, z_top, off1), e.P(u0, z_top, off1)], mat, UP, col=col)
    return zc


# ================================================================== Dome of the Rock (+ platform, kiosks, minarets)
def octagon_fit(ring):
    c = centroid(ring)
    R = sum(math.dist(c, p) for p in ring) / len(ring)
    n = len(ring)
    ang = [math.atan2(p[1] - c[1], p[0] - c[0]) for p in ring]
    # mean of (angle - k * 2pi/n) on the circle of period 2pi/n
    per = 2 * math.pi / n
    sx = sum(math.cos((a - per * k) * n) for k, a in enumerate(ang))
    sy = sum(math.sin((a - per * k) * n) for k, a in enumerate(ang))
    a0 = math.atan2(sy, sx) / n
    return c, R, a0


def dome_of_the_rock(mbs, bd, gen, place, lod=False):
    """Octagon 20.3 m sides (OSM; Creswell 20.59), walls 12.1 m (marble dado 4.9, tiled zone with
    7 bays per side, Ya-Sin frieze parapet), drum r 11.8 with 16 windows, gilded dome r 11.4 rising
    to ~33 m above the platform + 3.6 m finial, four porches (S/N with 4+4 columns, E/W smaller).
    H:03-H:07, H:16 and the Mount of Olives views H:01/H:02/H:08."""
    sol, dec = mbs["solid"], mbs["deco"]
    zp = platform_top(bd)
    ring = ccw(bd["ring"])
    C, R, a0 = octagon_fit(ring)
    O = reg_poly(C, R, 8, a0)
    side = math.dist(O[0], O[1])
    H_MAR, H_TILE, H_WALL = 4.9, 9.3, 12.1
    Z_ROOF_O, Z_ROOF_I = 11.3, 13.3
    R_DRUM, Z_DRUM0, Z_DRUM1, Z_BAND = 12.0, 12.6, 21.8, 19.8
    R_DOME, K_DOME = 11.7, 1.02
    if lod:
        b = sol
        for k in range(8):
            e = Edge(O[k], O[(k + 1) % 8])
            for j in range(7):
                ua, ub = side * j / 7, side * (j + 1) / 7
                cname = "bay_blind" if j in (0, 6) else "bay_window"
                quad_uv(b, [e.P(ua, zp + H_MAR), e.P(ub, zp + H_MAR), e.P(ub, zp + H_TILE), e.P(ua, zp + H_TILE)],
                        "faience", e.n, cell_uv(gen, cname))
            quad_uv(b, [e.P(0, zp - 0.3), e.P(side, zp - 0.3), e.P(side, zp + H_MAR), e.P(0, zp + H_MAR)], "faience", e.n,
                    cell_uv(gen, "marble_bay"))
            quad_uv(b, [e.P(0, zp + H_TILE), e.P(side, zp + H_TILE), e.P(side, zp + H_WALL), e.P(0, zp + H_WALL)],
                    "faience", e.n, cell_uv(gen, "parapet"))
        cap(b, O, zp + H_WALL, "leaddome")
        D = reg_poly(C, R_DRUM, 16, a0)
        for k in range(16):
            e = Edge(D[k], D[(k + 1) % 16])
            quad_uv(b, [e.P(0, zp + H_WALL), e.P(e.L, zp + H_WALL), e.P(e.L, zp + Z_DRUM1), e.P(0, zp + Z_DRUM1)],
                    "faience", e.n, cell_uv(gen, "drum_window"))
        top = dome_uv(b, C[0], C[1], zp + Z_DRUM1, R_DOME + 0.2, "gold", k=K_DOME, seg=16, rings=5, tile=4.4)
        finial(b, C[0], C[1], top, 3.6, lod=True)
        _platform(mbs, bd, gen, place, lod=True)
        _platform_kiosks(mbs, bd, gen, lod=True)
        _minarets(mbs, bd, gen, place, lod=True)
        return

    # ---------------- octagon walls
    portal_faces = {}
    for k in range(8):
        e = Edge(O[k], O[(k + 1) % 8])
        bearing = math.degrees(math.atan2(e.n.x, e.n.y)) % 360
        card = min(range(4), key=lambda q: min(abs(bearing - 90 * q), 360 - abs(bearing - 90 * q)))
        dev = min(abs(bearing - 90 * card), 360 - abs(bearing - 90 * card))
        if dev < 22.5:
            portal_faces[k] = "NESW"[card]
    door_w, door_h = 2.6, 4.3
    for k in range(8):
        e = Edge(O[k], O[(k + 1) % 8])
        L = e.L
        bw = L / 7
        portal = k in portal_faces
        for j in range(7):
            ua, ub = bw * j, bw * (j + 1)
            # marble dado
            rect = cell_uv(gen, "marble_bay")
            uvf = rect_map(rect, ua, ub, zp, zp + H_MAR)
            if portal and j == 3:
                uc = L / 2
                hole = [(uc - door_w / 2, zp), (uc + door_w / 2, zp), (uc + door_w / 2, zp + door_h), (uc - door_w / 2, zp + door_h)]
                outline = [(ua, zp - 0.3), (uc - door_w / 2, zp - 0.3), (uc - door_w / 2, zp), (uc - door_w / 2, zp + door_h),
                           (uc + door_w / 2, zp + door_h), (uc + door_w / 2, zp), (uc + door_w / 2, zp - 0.3),
                           (ub, zp - 0.3), (ub, zp + H_MAR - 0.12), (ua, zp + H_MAR - 0.12)]
                face(sol, e, outline, "faience", uvf=uvf)
                reveal(sol, e, hole, 0.0, -0.9, "dressed", col=PALE)
                d_rect = cell_uv(gen, "door_bronze")
                quad_uv(sol, [e.P(uc - door_w / 2, zp, -0.9), e.P(uc + door_w / 2, zp, -0.9),
                              e.P(uc + door_w / 2, zp + door_h, -0.9), e.P(uc - door_w / 2, zp + door_h, -0.9)],
                        "faience", e.n, d_rect)
            else:
                face(sol, e, [(ua, zp - 0.3), (ub, zp - 0.3), (ub, zp + H_MAR - 0.12), (ua, zp + H_MAR - 0.12)], "faience",
                     uvf=uvf)
            # tiled zone
            cname = "bay_blind" if (j in (0, 6) or (portal and j == 3)) else "bay_window"
            face(sol, e, [(ua, zp + H_MAR + 0.12), (ub, zp + H_MAR + 0.12), (ub, zp + H_TILE), (ua, zp + H_TILE)], "faience",
                 uvf=rect_map(cell_uv(gen, cname), ua, ub, zp + H_MAR, zp + H_TILE))
        # parapet zone (frieze) up to the cornice
        face(sol, e, [(0, zp + H_TILE), (L, zp + H_TILE), (L, zp + H_WALL - 0.3), (0, zp + H_WALL - 0.3)], "faience",
             uvf=rect_map(cell_uv(gen, "parapet"), 0, L, zp + H_TILE, zp + H_WALL, fz=(0.0, 1.0)))
    # moulding between dado and tiles, cornice + parapet top, parapet inner face
    O_led = reg_poly(C, offset_reg(R, 8, 0.1), 8, a0)
    band(sol, O_led, zp + H_MAR - 0.12, zp + H_MAR + 0.12, "dressed", inner=O, col=PALE, bottom=True)
    O_cor = reg_poly(C, offset_reg(R, 8, 0.28), 8, a0)
    O_in = reg_poly(C, offset_reg(R, 8, -0.75), 8, a0)
    band(sol, O_cor, zp + H_WALL - 0.3, zp + H_WALL, "dressed", inner=O_in, col=PALE, bottom=False)
    for k in range(8):                                                   # cornice underside
        a, b = O_cor[k], O_cor[(k + 1) % 8]
        c, d = O[(k + 1) % 8], O[k]
        sol.poly([V(*a, zp + H_WALL - 0.3), V(*b, zp + H_WALL - 0.3), V(*c, zp + H_WALL - 0.3), V(*d, zp + H_WALL - 0.3)],
                 "dressed", -UP, col=PALE)
    for k in range(8):                                                   # parapet inner face
        a, b = O_in[k], O_in[(k + 1) % 8]
        sol.poly([V(*a, zp + Z_ROOF_O), V(*b, zp + Z_ROOF_O), V(*b, zp + H_WALL), V(*a, zp + H_WALL)], "dressed",
                 -V(b[1] - a[1], -(b[0] - a[0])), col=GREYSTONE)
    # ambulatory roof: lead, from inside the parapet up to the drum
    N = 32
    D = reg_poly(C, R_DRUM, N, a0)
    inner_pts = []
    for j in range(N):
        ang = a0 + 2 * math.pi * j / N
        dirv = Vector((math.cos(ang), math.sin(ang)))
        # intersect the ray with the inner octagon
        best = None
        for k in range(8):
            p, q = Vector(O_in[k]), Vector(O_in[(k + 1) % 8])
            den = dirv.x * (q.y - p.y) - dirv.y * (q.x - p.x)
            if abs(den) < 1e-9:
                continue
            tt = ((p.x - C[0]) * (q.y - p.y) - (p.y - C[1]) * (q.x - p.x)) / den
            ss = ((p.x - C[0]) * dirv.y - (p.y - C[1]) * dirv.x) / den
            if tt > 0 and -1e-6 <= ss <= 1 + 1e-6 and (best is None or tt < best):
                best = tt
        inner_pts.append((C[0] + dirv.x * best, C[1] + dirv.y * best))
    for j in range(N):
        a, b = inner_pts[j], inner_pts[(j + 1) % N]
        c, d = D[(j + 1) % N], D[j]
        p = [V(*a, zp + Z_ROOF_O), V(*b, zp + Z_ROOF_O), V(*c, zp + Z_ROOF_I), V(*d, zp + Z_ROOF_I)]
        sol.poly([p[0], p[1], p[2]], "leaddome", UP)
        sol.poly([p[0], p[2], p[3]], "leaddome", UP)
    # ---------------- drum (32 facets = 16 window bays) and band
    rw, rb = cell_uv(gen, "drum_window"), cell_uv(gen, "drum_band")
    for j in range(N):
        e = Edge(D[j], D[(j + 1) % N])
        half = j % 2
        uvf = rect_map(rw, 0, e.L, zp + Z_DRUM0, zp + Z_BAND, fu=(0.5 * half, 0.5 * half + 0.5))
        face(sol, e, [(0, zp + Z_DRUM0), (e.L, zp + Z_DRUM0), (e.L, zp + Z_BAND), (0, zp + Z_BAND)], "faience", uvf=uvf)
        m = j % 8
        uvf = rect_map(rb, 0, e.L, zp + Z_BAND, zp + Z_DRUM1, fu=(m / 8, (m + 1) / 8))
        face(sol, e, [(0, zp + Z_BAND), (e.L, zp + Z_BAND), (e.L, zp + Z_DRUM1), (0, zp + Z_DRUM1)], "faience", uvf=uvf)
    D_rim = reg_poly(C, R_DRUM + 0.4, N, a0)
    band(sol, D_rim, zp + Z_DRUM1, zp + Z_DRUM1 + 0.35, "leaddome", inner=reg_poly(C, R_DOME, N, a0), bottom=False)
    for j in range(N):                                                   # rim underside
        a, b, c, d = D_rim[j], D_rim[(j + 1) % N], D[(j + 1) % N], D[j]
        sol.poly([V(*a, zp + Z_DRUM1), V(*b, zp + Z_DRUM1), V(*c, zp + Z_DRUM1), V(*d, zp + Z_DRUM1)], "leaddome", -UP)
    # ---------------- gilded dome + finial (dome rises from the rim top; slightly pointed)
    zd = zp + Z_DRUM1 + 0.35
    top = dome_uv(sol, C[0], C[1], zd, R_DOME, "gold", k=K_DOME, seg=48, rings=12, tile=4.4, n_u=16)
    finial(dec, C[0], C[1], top - 0.05, 3.6, "gold", face_dir=(math.cos(a0 + math.pi / 8), math.sin(a0 + math.pi / 8)))
    # ---------------- porches
    for k, cardinal in portal_faces.items():
        e = Edge(O[k], O[(k + 1) % 8])
        _dor_porch(mbs, gen, e, zp, cardinal, door_w)
    _platform(mbs, bd, gen, place)
    _platform_kiosks(mbs, bd, gen)
    _minarets(mbs, bd, gen, place)


def _dor_porch(mbs, gen, e, zp, cardinal, door_w):
    """Porch on a cardinal face: columns carrying a flat roof at the top of the marble dado, the
    tiled arched hood over the door rising into the tiled zone (H:03, H:05, H:06, H:07)."""
    sol, dec = mbs["solid"], mbs["deco"]
    L = e.L
    uc = L / 2
    depth = 3.0 if cardinal in "SN" else 2.6
    per_side = 4 if cardinal in "SN" else 2
    z_lint, z_roof = 4.85, 5.2
    xs = [uc - 1.95 - 1.75 * i for i in range(per_side)] + [uc + 1.95 + 1.75 * i for i in range(per_side)]
    for x in xs:
        p = e.P(x, 0, depth - 0.35)
        column(sol, gen, p.x, p.y, zp, z_lint - 0.25, r=0.24)
    for x in (uc - 1.95 + 0.3, uc + 1.95 - 0.3):                       # piers framing the central arch
        obox(sol, e.P(x, 0, depth - 0.35), e.t, 0.6, 0.6, zp - 0.2, zp + z_lint, "dressed", col=PALE, top=False)
    u0, u1 = min(xs) - 0.5, max(xs) + 0.5
    # flat roof slab with a lintel band; underside in tile
    zr0, zr1 = zp + z_lint, zp + z_roof
    q_top = [e.P(u0, zr1, 0), e.P(u1, zr1, 0), e.P(u1, zr1, depth), e.P(u0, zr1, depth)]
    sol.poly(q_top, "leaddome", UP)
    quad_uv(sol, [e.P(u0, zr0 - 0.25, depth), e.P(u0, zr0 - 0.25, 0.01), e.P(u1, zr0 - 0.25, 0.01), e.P(u1, zr0 - 0.25, depth)],
            "faience", -UP, cell_uv(gen, "tile_field"))
    face(sol, e, [(u0, zr0 - 0.25), (u1, zr0 - 0.25), (u1, zr1), (u0, zr1)], "wood", off=depth, col=(0.45, 0.38, 0.33))
    for ua, sgn in ((u0, -1), (u1, 1)):
        q = [e.P(ua, zr0 - 0.25, 0.01), e.P(ua, zr0 - 0.25, depth), e.P(ua, zr1, depth), e.P(ua, zr1, 0.01)]
        sol.poly(q, "wood", e.t * sgn, col=(0.7, 0.62, 0.55))
    # hood: tiled arched frame over the door, projecting from the wall, rising to ~8.7 m
    hw = 1.9
    zs = zp + 6.0
    rect = cell_uv(gen, "hood")
    outline = [(uc - hw, zr1), (uc + hw, zr1)] + arch_curve(uc - hw, uc + hw, zs, "round", 12)[::-1]
    # front face of the hood with a recessed inner arch
    inner = [(uc - hw + 0.45, zr1 + 0.25), (uc + hw - 0.45, zr1 + 0.25)] + \
        arch_curve(uc - hw + 0.45, uc + hw - 0.45, zs, "round", 12)[::-1]
    hd = depth - 0.2
    face(dec, e, outline, "faience", off=hd, holes=[inner], uvf=rect_map(cell_uv(gen, "bay_blind"), uc - hw, uc + hw, zr1, zs + hw))
    face(dec, e, inner, "faience", off=hd - 0.45, uvf=rect_map(rect, uc - hw, uc + hw, zr1, zs + hw))
    reveal(dec, e, inner, hd, hd - 0.45, "faience", skip_bottom=False)
    # hood top: half-cylinder vault from the front back to the wall
    cv = arch_curve(uc - hw, uc + hw, zs, "round", 12)
    for i in range(len(cv) - 1):
        a, b = cv[i], cv[i + 1]
        q = [e.P(a[0], a[1], hd), e.P(b[0], b[1], hd), e.P(b[0], b[1], 0.02), e.P(a[0], a[1], 0.02)]
        dec.poly(q, "leaddome", e.P(uc, zs, hd / 2) * -1 + (q[0] + q[2]) / 2)
    for ua, sgn in ((uc - hw, -1), (uc + hw, 1)):
        q = [e.P(ua, zr1, 0.02), e.P(ua, zr1, hd), e.P(ua, zs, hd), e.P(ua, zs, 0.02)]
        dec.poly(q, "dressed", e.t * sgn, col=PALE)


# ---------------------------------------------------------------- the upper platform
def _platform(mbs, bd, gen, place, lod=False):
    """Walkable upper platform (PLATFORM outline), retaining walls of ashlar down below the esplanade,
    a dressed coping.  Stairs are built by the qanatir (top riser = this wall)."""
    sol = mbs["solid"]
    E = esplanade(bd)
    zt = E + PLAT_H
    ring = ccw(PLATFORM)
    cap(sol, ring, zt, "paving")
    prism_walls(sol, ring, E - 1.0, zt - (0.0 if lod else 0.32), "ashlar", col=WARM)
    if lod:
        return
    # coping: 0.32 m dressed band projecting 6 cm
    n = len(ring)
    out = []
    for i in range(n):
        a, b, c = Vector(ring[i - 1]), Vector(ring[i]), Vector(ring[(i + 1) % n])
        e1, e2 = (b - a).normalized(), (c - b).normalized()
        n1, n2 = Vector((e1.y, -e1.x)), Vector((e2.y, -e2.x))
        bis = (n1 + n2)
        bis = bis.normalized() if bis.length > 1e-6 else n1
        cosh = max(0.3, bis.dot(n1))
        out.append(tuple(b + bis * (0.06 / cosh)))
    band(sol, out, zt - 0.32, zt, "dressed", inner=ring, col=PALE, bottom=True)


def _platform_kiosks(mbs, bd, gen, lod=False):
    """Dome of the Prophet (w291836680): octagonal kiosk of 8 marble columns with pointed arches and a
    lead dome on a drum (r ~1.4 m footprint)."""
    zt = platform_top(bd)
    _open_qubba(mbs, gen, DOME_PROPHET, 1.75, 8, zt, h_col=2.3, dome_r=1.35, drum=0.6, lod=lod, a0=math.pi / 8)


def _open_qubba(mbs, gen, c, R, n, z0, h_col=2.4, dome_r=None, drum=0.7, lod=False, a0=0.0, dome_mat="leaddome",
                mihrab=None):
    """Small open domed kiosk: n columns on a circle R, arches, an n-sided drum and a dome."""
    sol, dec = mbs["solid"], mbs["deco"]
    P = reg_poly(c, R, n, a0)
    zs = z0 + h_col
    side = math.dist(P[0], P[1])
    rise = arch_rise(side - 0.4, "pointed")
    z_top = zs + rise + 0.45
    if lod:
        for p in P:
            mk.cylinder(sol, p[0], p[1], z0, zs, 0.2, "dressed", seg=4, cap=False)
        prism_walls(sol, P, zs, z_top, "dressed", col=PALE)
        cap(sol, P, z_top, "dressed", col=PALE)
        dome_uv(sol, c[0], c[1], z_top, dome_r or R * 0.8, dome_mat, k=1.1, seg=8, rings=3)
        return z_top
    for p in P:
        column(sol, gen, p[0], p[1], z0, h_col, r=0.17, col=PALE)
    Rin = offset_reg(R, n, -0.25)
    Rout = offset_reg(R, n, 0.25)
    Pi, Po = reg_poly(c, Rin, n, a0), reg_poly(c, Rout, n, a0)
    for k in range(n):
        e = Edge(Po[k], Po[(k + 1) % n])
        ei = Edge(Pi[k], Pi[(k + 1) % n])
        L = e.L
        Li = ei.L
        w = 0.32
        cv = arch_curve(w, L - w, zs, "pointed", 8)
        face(dec, e, [(0, z_top), (0, zs)] + cv + [(L, zs), (L, z_top)], "dressed", col=PALE)
        sh = (L - Li) / 2
        # inner face: same curve, projected on the inner edge (shifted by sh)
        face(dec, ei, [(0, z_top), (0, zs)] + [(u - sh, z) for u, z in cv] + [(Li, zs), (Li, z_top)], "dressed",
             col=PALE, inward=True)
        for i in range(len(cv) - 1):
            a, b = cv[i], cv[i + 1]
            q = [e.P(a[0], a[1]), e.P(b[0], b[1]), ei.P(b[0] - sh, b[1]), ei.P(a[0] - sh, a[1])]
            dec.poly(q, "dressed", V(c[0], c[1], zs) - (q[0] + q[2]) / 2, col=PALE)
    corner_undersides(dec, Po, Pi, zs, 0.32)
    cap(dec, Pi, zs + rise + 0.1, "dressed", col=GREYSTONE, down=True)    # ceiling
    cap(dec, Po, z_top, "dressed", col=PALE)
    dr = dome_r or R * 0.8
    D = reg_poly(c, dr + 0.15, max(n, 8), a0)
    prism_walls(dec, D, z_top, z_top + drum, "dressed", col=PALE)
    topz = dome_uv(dec, c[0], c[1], z_top + drum, dr, dome_mat, k=1.12, seg=16, rings=6, tile=2.0)
    cap(dec, D, z_top + drum, "dressed", col=PALE)
    finial(dec, c[0], c[1], topz, 0.9, "gold")
    return z_top


# ---------------------------------------------------------------- minarets
def _minarets(mbs, bd, gen, place, lod=False):
    """Ghawanima and Bab al-Asbat (no nearer host); Silsila hangs off the Western Wall, Fakhriyya off Al-Aqsa."""
    E = esplanade(bd)
    for name, c, kind in MINARETS:
        if kind not in ("ghawanima", "asbat"):
            continue
        if kind in ("silsila", "fakhriyya", "ghawanima"):
            t = (math.cos(WEST_WALL_BEARING), math.sin(WEST_WALL_BEARING))
        else:
            t = NORTH_WALL_DIR
        minaret(mbs, gen, c, t, E, kind, lod)


MINARET_SPECS = {
    # Ghawanima: 38.5 m (Wikipedia, Minarets of Al-Aqsa), square base two wider storeys, square shaft,
    # balcony with timber canopy, octagonal turret, bulbous dome (H:20)
    "ghawanima": dict(base=6.2, base_h=10.0, shaft=4.7, gallery=27.0, canopy=29.6, upper="oct", up_r=1.75,
                      up_h=33.6, dome_r=1.7, dome_k=1.35, top=38.5, courses=(14.5, 19.0, 23.5)),
    # Bab al-Silsila: 35 m, square Syrian type, closed balcony on stone columns, broad canopy,
    # cylindrical drum, lead dome (H:19)
    "silsila": dict(base=5.6, base_h=3.0, shaft=5.0, gallery=24.5, canopy=27.4, upper="cyl", up_r=1.85,
                    up_h=31.0, dome_r=2.0, dome_k=1.1, top=35.0, courses=(9.0, 14.5, 19.5)),
    # al-Fakhriyya: square, three floors divided by mouldings, muqarnas balcony, square chamber,
    # lead dome (H:17); height not published -> ~23.5 m from H:17 proportions (M/L)
    "fakhriyya": dict(base=4.6, base_h=2.0, shaft=4.3, gallery=17.0, canopy=19.8, upper="sq", up_r=1.5,
                      up_h=20.6, dome_r=1.5, dome_k=1.15, top=23.5, courses=(6.5, 12.0)),
    # Bab al-Asbat: rectangular Mamluk base, triangular transition, Ottoman cylindrical shaft 28.5 m
    # (rebuilt taller 1927), balcony, narrower upper shaft, pointed lead cap (H:18)
    "asbat": dict(base=5.0, base_h=8.0, shaft=3.4, gallery=21.5, canopy=None, upper="cyl", up_r=1.2,
                  up_h=27.0, dome_r=1.25, dome_k=1.7, top=30.5, courses=(), cyl=True),
}


def minaret(mbs, gen, c, t, E, kind, lod=False):
    sp = MINARET_SPECS[kind]
    sol, dec = mbs["solid"], mbs["deco"]
    t = Vector((t[0], t[1])).normalized()
    s = Vector((-t.y, t.x))
    z_b = E - 6.0                                        # foot well below: hidden where the ground is higher

    def sq(half):
        cc = Vector(c)
        return [tuple(cc + (t * sx + s * sy) * half) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    zg = E + sp["gallery"]
    if lod:
        prism_walls(sol, sq(sp["base"] / 2), z_b, E + sp["base_h"], "ashlar", col=WARM)
        if sp.get("cyl"):
            mk.cylinder(sol, c[0], c[1], E + sp["base_h"], zg, sp["shaft"] / 2, "ashlar", seg=8, cap=False)
        else:
            prism_walls(sol, sq(sp["shaft"] / 2), E + sp["base_h"], zg, "ashlar", col=WARM)
        prism_walls(sol, sq(sp["shaft"] / 2 + 0.6), zg, zg + 1.2, "ashlar", col=WARM)
        cap(sol, sq(sp["shaft"] / 2 + 0.6), zg + 1.2, "ashlar", col=WARM)
        mk.cylinder(sol, c[0], c[1], zg + 1.2, E + sp["up_h"], sp["up_r"], "ashlar", seg=6, cap=False)
        dome_uv(sol, c[0], c[1], E + sp["up_h"], sp["dome_r"], "leaddome", k=sp["dome_k"], seg=6, rings=2)
        return
    # base block
    prism_walls(sol, sq(sp["base"] / 2), z_b, E + sp["base_h"], "ashlar", col=WARM)
    cap(sol, sq(sp["base"] / 2), E + sp["base_h"], "ashlar", col=WARM)
    zs0 = E + sp["base_h"]
    if sp.get("cyl"):
        r = sp["shaft"] / 2
        cylinder_uv(sol, c[0], c[1], zs0, zg, r, "ashlar", seg=16, col=PALE, tile=3.0)
    else:
        sh = sq(sp["shaft"] / 2)
        prism_walls(sol, sh, zs0, zg, "ashlar", col=WARM)
        for zc in sp["courses"]:                                          # string courses
            band(dec, sq(sp["shaft"] / 2 + 0.12), E + zc, E + zc + 0.3, "dressed", inner=sh, col=PALE, bottom=True)
        # slit windows / blind niches on the faces
        for k in range(4):
            e = Edge(sh[k], sh[(k + 1) % 4])
            for zc in sp["courses"]:
                z0w = E + zc + 1.0
                quad_uv(dec, [e.P(e.L / 2 - 0.35, z0w, 0.08), e.P(e.L / 2 + 0.35, z0w, 0.08),
                              e.P(e.L / 2 + 0.35, z0w + 1.6, 0.08), e.P(e.L / 2 - 0.35, z0w + 1.6, 0.08)],
                        "faience", e.n, cell_uv(gen, "window_grille"))
    # muqarnas gallery: corbel steps + balcony floor + parapet
    r_sh = sp["shaft"] / 2
    pr = 0.75
    for i, (dz, dd) in enumerate(((-1.0, 0.25), (-0.65, 0.5), (-0.3, pr))):
        ring_ = sq(r_sh + dd) if not sp.get("cyl") else reg_poly(c, r_sh + dd, 16, math.atan2(t.y, t.x))
        inner_ = sq(r_sh) if not sp.get("cyl") else reg_poly(c, r_sh, 16, math.atan2(t.y, t.x))
        band(dec, ring_, zg + dz, zg + dz + 0.3, "dressed", inner=inner_, col=PALE, bottom=True, top=(i < 2))
    zf = zg + 0.25
    if sp.get("cyl"):
        outer = reg_poly(c, r_sh + pr + 0.05, 16, math.atan2(t.y, t.x))
        inner = reg_poly(c, sp["up_r"], 16, math.atan2(t.y, t.x))
    else:
        outer = sq(r_sh + pr + 0.05)
        inner = sq(sp["up_r"]) if sp["upper"] == "sq" else reg_poly(c, sp["up_r"], 8, math.atan2(t.y, t.x) + math.pi / 8)
    prism_walls(sol, outer, zg, zf, "dressed", col=PALE)
    cap(sol, outer, zf, "dressed", col=PALE)
    # parapet: stone balustrade card ring
    par_out = outer
    for k in range(len(par_out)):
        a, b = Vector(par_out[k]), Vector(par_out[(k + 1) % len(par_out)])
        q = [V(a.x, a.y, zf), V(b.x, b.y, zf), V(b.x, b.y, zf + 1.05), V(a.x, a.y, zf + 1.05)]
        n_ = V(b.y - a.y, -(b.x - a.x))
        dec.poly(q, "ashlar", n_, col=PALE)
        dec.poly(q[::-1], "ashlar", -n_, col=GREYSTONE)
    # upper storey: octagonal / cylindrical / square turret
    zu0, zu1 = zf, E + sp["up_h"]
    if sp["upper"] == "oct":
        U = reg_poly(c, sp["up_r"], 8, math.atan2(t.y, t.x) + math.pi / 8)
        prism_walls(sol, U, zu0, zu1, "ashlar", col=WARM)
        for k in range(8):
            e = Edge(U[k], U[(k + 1) % 8])
            quad_uv(dec, [e.P(e.L / 2 - 0.3, zu0 + 1.0, 0.08), e.P(e.L / 2 + 0.3, zu0 + 1.0, 0.08),
                          e.P(e.L / 2 + 0.3, zu0 + 2.4, 0.08), e.P(e.L / 2 - 0.3, zu0 + 2.4, 0.08)], "faience", e.n,
                    cell_uv(gen, "window_grille"))
        Dr = reg_poly(c, sp["dome_r"] * 0.9, 12, 0)
        prism_walls(sol, Dr, zu1, zu1 + 0.9, "ashlar", col=WARM)
        cap(sol, U, zu1, "dressed", col=PALE)
        zd = zu1 + 0.9
        r_d = sp["dome_r"] * 0.9
    elif sp["upper"] == "sq":
        U = sq(sp["up_r"])
        prism_walls(sol, U, zu0, zu1, "ashlar", col=WARM)
        for k in range(4):
            e = Edge(U[k], U[(k + 1) % 4])
            quad_uv(dec, [e.P(e.L / 2 - 0.45, zu0 + 0.6, 0.08), e.P(e.L / 2 + 0.45, zu0 + 0.6, 0.08),
                          e.P(e.L / 2 + 0.45, zu0 + 2.3, 0.08), e.P(e.L / 2 - 0.45, zu0 + 2.3, 0.08)], "faience", e.n,
                    cell_uv(gen, "lattice"))
        cap(sol, U, zu1, "dressed", col=PALE)
        zd = zu1
        r_d = sp["dome_r"]
    else:
        cylinder_uv(sol, c[0], c[1], zu0, zu1, sp["up_r"], "ashlar", seg=16, col=PALE, tile=3.0)
        cap(sol, reg_poly(c, sp["up_r"], 16, 0), zu1, "dressed", col=PALE)
        zd = zu1
        r_d = sp["dome_r"]
    # canopy (timber, flat hipped) on posts over the gallery
    if sp["canopy"]:
        zc = E + sp["canopy"]
        ext = r_sh + pr + 0.55
        cq = sq(ext)
        for corner in sq(r_sh + pr - 0.12):
            mk.cylinder(dec, corner[0], corner[1], zf, zc, 0.07, "wood", seg=4, cap=False)
        apex = sq(max(0.3, sp["up_r"] - 0.1))
        for k in range(4):
            a, b = cq[k], cq[(k + 1) % 4]
            a2, b2 = apex[k], apex[(k + 1) % 4]
            q = [V(*a, zc), V(*b, zc), V(*b2, zc + 0.7), V(*a2, zc + 0.7)]
            dec.poly(q, "wood", V((a[0] + b[0]) / 2 - c[0], (a[1] + b[1]) / 2 - c[1], 2.0), col=(0.8, 0.75, 0.7))
            dec.poly(q[::-1], "wood", -V((a[0] + b[0]) / 2 - c[0], (a[1] + b[1]) / 2 - c[1], 2.0), col=(0.6, 0.55, 0.5))
    topz = dome_uv(dec, c[0], c[1], zd, r_d, "leaddome", k=sp["dome_k"], seg=16, rings=6, tile=1.0)
    finial(dec, c[0], c[1], topz, max(1.0, E + sp["top"] - topz + 0.6), "gold")


# ================================================================== qanatir and stairs
def qanatir(mbs, bd, gen, place, lod=False):
    """Free-standing arcade at a stair head (al-Mawazin, H:07, H:14-H:16): end piers, marble columns,
    3-4 pointed arches springing at 3.8 m, band to 6.8 m, cornice; stairs down to the esplanade
    (risers ~16 cm, treads 34 cm) along the OSM steps direction.  Collision on piers/columns only."""
    zt = platform_top(bd)
    E = esplanade(bd)
    ring = ccw(bd["ring"])
    n = len(ring)
    pts = []                                             # drop collinear OSM vertices
    for i in range(n):
        a, b, c = Vector(ring[i - 1]), Vector(ring[i]), Vector(ring[(i + 1) % n])
        d1, d2 = b - a, c - b
        if abs(d1.x * d2.y - d1.y * d2.x) / max(d1.length * d2.length, 1e-9) > 0.05:
            pts.append(tuple(b))
    if len(pts) < 4:
        pts = ring
    m = len(pts)
    lens = [math.dist(pts[i], pts[(i + 1) % m]) for i in range(m)]
    i_long = max(range(m), key=lambda i: lens[i])
    e0 = Edge(pts[i_long], pts[(i_long + 1) % m])
    depth = max(abs((Vector((p[0], p[1], 0)) - e0.A).dot(e0.n)) for p in pts)
    mid0 = e0.P(e0.L / 2, 0)
    away = Vector((mid0.x - PLAT_C[0], mid0.y - PLAT_C[1], 0))
    if e0.n.dot(away) > 0:
        e_out = e0                                       # the long edge is the outer side
    else:                                                # outer side = the opposite long edge, reversed
        e_out = Edge(tuple(e0.P(e0.L, 0, -depth)[:2]), tuple(e0.P(0, 0, -depth)[:2]))
    o_lo = -depth
    L = e_out.L
    narch = max(2, min(5, round((L - 2.0) / 3.4)))
    zs, z_top = zt + 3.8, zt + 6.8
    om0, om1 = o_lo + (depth - 1.0) / 2, o_lo + (depth - 1.0) / 2 + 1.0
    arcade(mbs, gen, e_out, 0.0, L, om0, om1, zt, zs, z_top, narch, lod=lod, pier=0.95, col_r=0.22)
    _stairs(mbs, e_out, 0.0, L, zt, E, lod=lod)


def _stairs(mbs, e, u0, u1, z_top, z_foot, riser=0.16, tread=0.34, lod=False):
    """Flight going down from the edge e (outward normal) to z_foot.  The top riser is the platform's
    retaining wall; the bottom step top would sit on the ground and is left out."""
    sol = mbs["solid"]
    drop = z_top - z_foot
    nst = max(1, round(drop / riser))
    r = drop / nst
    zb = z_foot - 0.3
    if lod:
        run = nst * tread
        q = [e.P(u0, z_top, 0), e.P(u1, z_top, 0), e.P(u1, z_foot, run), e.P(u0, z_foot, run)]
        sol.poly(q, "paving", e.n + UP)
        for ua, sgn in ((u0, -1), (u1, 1)):
            sol.poly([e.P(ua, z_top, 0), e.P(ua, z_foot, run), e.P(ua, zb, run), e.P(ua, zb, 0)], "ashlar", e.t * sgn,
                     col=WARM)
        return
    tile = 4.0
    for k in range(1, nst + 1):
        zk = z_top - k * r                       # top of step k
        a, b = (k - 1) * tread, k * tread
        if k < nst:
            q = [e.P(u0, zk, a), e.P(u1, zk, a), e.P(u1, zk, b), e.P(u0, zk, b)]
            sol.poly(q, "paving", UP, uv=[((p.dot(e.t)) / tile, (p.dot(e.n)) / tile) for p in q])
        if k >= 2:                               # riser at the front of step k-1 -> top of step k
            zr0 = zk if k < nst else zb
            q = [e.P(u0, zr0, a), e.P(u1, zr0, a), e.P(u1, zk + r, a), e.P(u0, zk + r, a)]
            sol.poly(q, "dressed", e.n, col=(0.9, 0.88, 0.84))
        # cheeks: from below ground up to this step's top
        if k < nst:
            for ua, sgn in ((u0, -1), (u1, 1)):
                sol.poly([e.P(ua, zb, a), e.P(ua, zb, b), e.P(ua, zk, b), e.P(ua, zk, a)], "ashlar", e.t * sgn, col=WARM)


# ================================================================== Dome of the Chain
def dome_of_the_chain(mbs, bd, gen, place, lod=False):
    """Open 11-sided arcade (11 outer + 6 inner columns), sloping lead roof, tiled hexagonal drum,
    lead dome (H:13, H:14); OSM ring r ~7.3 m, height 9 m (OSM) -> dome top ~11 m with the finial.
    Mihrab panel on the qibla (south) side."""
    sol, dec = mbs["solid"], mbs["deco"]
    zt = platform_top(bd)
    ring = ccw(bd["ring"])
    C = centroid(ring)
    Rr = sum(math.dist(C, p) for p in ring) / len(ring)
    n = 11
    # orient so that the southern side is centred on the qibla (side normal pointing south)
    a0 = -math.pi / 2 - math.pi / n
    Rc = Rr - 0.45
    P = reg_poly(C, Rc, n, a0)
    h_col = 2.75
    zs = zt + h_col
    KCH = 0.62
    side_o = 2 * offset_reg(Rr - 0.45, n, 0.3) * math.sin(math.pi / n)
    z_band = zs + arch_rise(side_o - 0.68, "pointed", KCH) + 0.3
    z_top = z_band + 0.6
    if lod:
        for p in P:
            mk.cylinder(sol, p[0], p[1], zt, zs, 0.2, "dressed", seg=4, cap=False)
        prism_walls(sol, P, zs, z_top, "dressed", col=PALE)
        cap(sol, P, z_top, "leaddome")
        H6 = reg_poly(C, 3.4, 6, 0)
        prism_walls(sol, H6, z_top, z_top + 2.6, "faience", col=PALE)
        dome_uv(sol, C[0], C[1], z_top + 2.6, 3.0, "leaddome", k=1.15, seg=8, rings=3)
        return
    for p in P:
        column(sol, gen, p[0], p[1], zt, h_col, r=0.2, col=PALE)
    Pi = reg_poly(C, offset_reg(Rc, n, -0.3), n, a0)
    Po = reg_poly(C, offset_reg(Rc, n, 0.3), n, a0)
    for k in range(n):
        e, ei = Edge(Po[k], Po[(k + 1) % n]), Edge(Pi[k], Pi[(k + 1) % n])
        L, Li = e.L, ei.L
        sh = (L - Li) / 2
        w = 0.34
        cv = arch_curve(w, L - w, zs, "pointed", 8, KCH)
        face(dec, e, [(0, z_band), (0, zs)] + cv + [(L, zs), (L, z_band)], "faience", col=PALE,
             uvf=rect_map(cell_uv(gen, "chain_drum"), -0.2, L + 0.2, zs - 0.4, z_band + 0.15))
        face(dec, ei, [(0, z_band), (0, zs)] + [(u - sh, z) for u, z in cv] + [(Li, zs), (Li, z_band)], "dressed",
             col=PALE, inward=True)
        face(dec, e, [(0, z_band), (L, z_band), (L, z_top), (0, z_top)], "faience",
             uvf=rect_map(cell_uv(gen, "tile_green"), 0, L, z_band, z_band + L / 4))
        for i in range(len(cv) - 1):
            a, b = cv[i], cv[i + 1]
            q = [e.P(a[0], a[1]), e.P(b[0], b[1]), ei.P(b[0] - sh, b[1]), ei.P(a[0] - sh, a[1])]
            dec.poly(q, "dressed", V(C[0], C[1], zs) - (q[0] + q[2]) / 2, col=PALE)
    corner_undersides(dec, Po, Pi, zs, 0.34)
    # mihrab: a wall between the two southern columns (side 0 is centred south), niche face in tile
    e = Edge(P[0], P[1])
    obox(sol, e.P(e.L / 2, 0, 0.0), e.t, e.L - 0.9, 0.45, zt - 0.1, zs - 0.02, "dressed", col=PALE)
    quad_uv(sol, [e.P(e.L / 2 + 0.7, zt + 0.2, -0.23), e.P(e.L / 2 - 0.7, zt + 0.2, -0.23),
                  e.P(e.L / 2 - 0.7, zs - 0.2, -0.23), e.P(e.L / 2 + 0.7, zs - 0.2, -0.23)], "faience", -e.n,
            cell_uv(gen, "chain_drum"))
    # inner hexagon of columns carrying the drum
    a6 = -math.pi / 2
    H6c = reg_poly(C, 3.0, 6, a6)
    for p in H6c:
        column(sol, gen, p[0], p[1], zt, h_col + 0.6, r=0.2, col=PALE)
    zd0 = zs + 0.6
    H6 = reg_poly(C, 3.45, 6, a6)
    cap(dec, H6, zd0, "dressed", col=GREYSTONE, down=True)
    # ambulatory ceiling + sloping lead roof from the arcade top to the drum
    Rtop_o = offset_reg(Rc, n, 0.42)
    Po2 = reg_poly(C, Rtop_o, n, a0)
    band(dec, Po2, z_top - 0.2, z_top, "dressed", inner=Po, col=PALE, bottom=True)
    z_roof_i = z_top + 1.0
    RN = 22
    inner = reg_poly(C, 3.45, 6, a6)
    # roof: fan from the 11-gon to the hexagon, via a 66-point sampling (lcm-ish) -> triangles
    outer_s = _sample_poly(Po2, RN * 3, a6)
    inner_s = _sample_poly(inner, RN * 3, a6)
    for j in range(len(outer_s)):
        a, b = outer_s[j], outer_s[(j + 1) % len(outer_s)]
        cc, d = inner_s[(j + 1) % len(inner_s)], inner_s[j]
        p = [V(*a, z_top), V(*b, z_top), V(*cc, z_roof_i), V(*d, z_roof_i)]
        dec.poly([p[0], p[1], p[2]], "leaddome", UP)
        dec.poly([p[0], p[2], p[3]], "leaddome", UP)
    cap(dec, Pi, z_top - 0.2, "dressed", col=GREYSTONE, down=True, holes=[reg_poly(C, 3.45, 6, a6)[::-1]])
    # drum (hexagonal, tiled), cornice, dome
    zdr1 = z_roof_i + 1.9
    for k in range(6):
        e = Edge(H6[k], H6[(k + 1) % 6])
        face(dec, e, [(0, zd0), (e.L, zd0), (e.L, zdr1), (0, zdr1)], "faience",
             uvf=rect_map(cell_uv(gen, "chain_drum"), 0, e.L, zd0, zdr1))
    H6r = reg_poly(C, 3.7, 6, a6)
    band(dec, H6r, zdr1, zdr1 + 0.3, "dressed", inner=reg_poly(C, 3.15, 6, a6), col=PALE, bottom=True)
    topz = dome_uv(dec, C[0], C[1], zdr1 + 0.3, 3.15, "leaddome", k=1.15, seg=24, rings=8, tile=2.0)
    finial(dec, C[0], C[1], topz, 1.6, "gold")


def _sample_poly(P, m, a0=0.0):
    """m points evenly spaced by angle (from a0) around a convex polygon (rays from its centre)."""
    c = (sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P))
    out = []
    for j in range(m):
        ang = a0 + 2 * math.pi * j / m
        d = Vector((math.cos(ang), math.sin(ang)))
        best = None
        for k in range(len(P)):
            p, q = Vector(P[k]), Vector(P[(k + 1) % len(P)])
            den = d.x * (q.y - p.y) - d.y * (q.x - p.x)
            if abs(den) < 1e-9:
                continue
            tt = ((p.x - c[0]) * (q.y - p.y) - (p.y - c[1]) * (q.x - p.x)) / den
            ss = ((p.x - c[0]) * d.y - (p.y - c[1]) * d.x) / den
            if tt > 0 and -1e-6 <= ss <= 1 + 1e-6 and (best is None or tt < best):
                best = tt
        out.append((c[0] + d.x * best, c[1] + d.y * best))
    return out


# ================================================================== small domed buildings on the platform
def _lifted_qubba(open_):
    def fn(mbs, bd, gen, place, lod=False):
        zt = platform_top(bd)
        ring = ccw(bd["ring"])
        C = centroid(ring)
        R = sum(math.dist(C, p) for p in ring) / len(ring)
        n = 8
        if open_:
            _open_qubba(mbs, gen, C, R, n, zt, h_col=2.4 if R > 2 else 1.9, dome_r=R * 0.78, lod=lod, a0=math.pi / 8)
        else:
            _closed_qubba(mbs, gen, ring, zt, lod=lod)
    return fn


def _closed_qubba(mbs, gen, ring, z0, h=5.2, lod=False, dome_mat="leaddome", z_base=None):
    """Closed domed cube: walls with an arched door and windows, flat roof, drum and dome."""
    sol, dec = mbs["solid"], mbs["deco"]
    zb = z0 - 0.4 if z_base is None else z_base
    C = centroid(ring)
    for i in range(len(ring)):
        e = Edge(ring[i], ring[(i + 1) % len(ring)])
        if lod or e.L < 2.2:
            face(sol, e, [(0, zb), (e.L, zb), (e.L, z0 + h), (0, z0 + h)], "ashlar", col=WARM)
            continue
        holes = []
        nb = max(1, int(e.L // 3.2))
        for j in range(nb):
            uc = e.L * (j + 0.5) / nb
            holes.append(opening(uc - 0.45, uc + 0.45, z0 + 1.4, z0 + 2.8, "pointed"))
        face(sol, e, [(0, zb), (e.L, zb), (e.L, z0 + h), (0, z0 + h)], "ashlar", holes=holes, col=WARM)
        for ol in holes:
            reveal(sol, e, ol, 0.0, -0.35, "ashlar", col=GREYSTONE, skip_bottom=False)
            u_a, u_b = ol[0][0], ol[1][0]
            face(sol, e, ol, "faience", off=-0.35,
                 uvf=rect_map(cell_uv(gen, "window_grille"), u_a - 0.08, u_b + 0.08, z0 + 1.4 - 0.2, max(p[1] for p in ol) + 0.1))
    cap(sol, ring, z0 + h, "lime")
    R = min(math.dist(C, ring[i]) * math.cos(math.pi / len(ring)) for i in range(len(ring))) * 0.82
    if R < 0.8:
        return
    if lod:
        dome_uv(sol, C[0], C[1], z0 + h, R, dome_mat, k=1.05, seg=8, rings=3)
        return
    D = reg_poly(C, R + 0.15, 16, 0)
    prism_walls(dec, D, z0 + h - 0.05, z0 + h + 0.7, "ashlar", col=WARM)
    cap(dec, D, z0 + h + 0.7, "dressed", col=PALE)
    topz = dome_uv(dec, C[0], C[1], z0 + h + 0.7, R, dome_mat, k=1.05, seg=16, rings=6, tile=2.0)
    finial(dec, C[0], C[1], topz, 1.0, "gold")


def dome_of_al_khalili(mbs, bd, gen, place, lod=False):
    """Ottoman domed cube (18th c.) on the NW corner of the platform; lead dome."""
    _closed_qubba(mbs, gen, ccw(bd["ring"]), platform_top(bd), h=5.6, lod=lod)


# ================================================================== Al-Aqsa
def al_aqsa(mbs, bd, gen, place, lod=False):
    """Al-Qibli mosque (H:09-H:12): footprint ~80 x 55 m (OSM), north porch of 7 pointed arches (the
    central one wider and taller under a raised bay) 6 m deep, side walls with rows of arched windows
    to 10.6 m, central nave clerestory to 15 m with a lead gable roof (ridge 17.3 m) from the porch to
    the dome, transept block under the dome; drum r 7.0 with 24 window bays, grey lead dome
    (r 6.8, pointed) to ~26 m + finial.  The Fakhriyya minaret hangs off this builder."""
    sol, dec = mbs["solid"], mbs["deco"]
    E = bd["ground"]
    ring = ccw(bd["ring"])
    n = len(ring)
    # north facade: the longest edge whose outward normal points north
    best = None
    for i in range(n):
        e = Edge(ring[i], ring[(i + 1) % n])
        if e.n.y > 0.8 and e.L > 30 and (best is None or e.L > best[1].L):
            best = (i, e)
    i_n, en = best
    W = en.L
    # frame: a along the facade from its west end (= en.A since CCW + outward north -> heading west? check)
    if en.t.x < 0:                                       # CCW ring with outward north: a->b runs west
        o = en.P(W, 0)
        ux = -en.t
    else:
        o = en.A
        ux = en.t
    sx = Vector((ux.y, -ux.x, 0))                        # points south, into the building

    def P(a, b, z):
        return o + ux * a + sx * b + Vector((0, 0, z))
    H = 10.6
    if lod:
        prism_walls(sol, ring, E - 0.5, E + H, "ashlar", col=WARM)
        cap(sol, ring, E + H, "lime")
        _aqsa_nave(mbs, P, E, W, gen, lod=True)
        _minaret_fakh(mbs, bd, gen, lod=True)
        return
    # ---- outer walls except the north facade, with arched windows
    for i in range(n):
        if i == i_n:
            continue
        e = Edge(ring[i], ring[(i + 1) % n])
        if e.L >= 12:
            _blind_arcade_wall(sol, dec, gen, e, E - 0.5, E + H, E)
        else:
            _wall_windows(sol, gen, e, E - 0.5, E + H, E, "ashlar", WARM, rows=((E + 5.2, E + 8.4, 0.95),), bay=4.3)
    # ---- porch: front face with 7 arches, interior, back wall with doors
    D = 6.0
    piers = 1.6
    widths = [5.9, 5.9, 5.9, 7.3, 5.9, 5.9, 5.9]
    scale = (W - 8 * piers) / sum(widths)
    widths = [w * scale for w in widths]
    spans = []
    a = piers
    for w in widths:
        spans.append((a, a + w))
        a += w + piers
    ef = Edge(tuple(P(0, 0, 0)[:2]), tuple(P(W, 0, 0)[:2]))   # outward normal = -sx (north)
    if ef.n.dot(sx) > 0:
        ef = Edge(tuple(P(W, 0, 0)[:2]), tuple(P(0, 0, 0)[:2]))
        flip = True
    else:
        flip = False

    def U(a_):
        return W - a_ if flip else a_
    z_c = E + 9.8                                       # porch ceiling
    holes = []
    for i, (a0_, a1_) in enumerate(spans):
        mid = i == 3
        zs = E + (5.0 if mid else 4.6)
        ua, ub = sorted((U(a0_), U(a1_)))
        holes.append(opening(ua, ub, E, zs, "pointed", 10, k=0.58 if mid else 0.6))
    # front face outline: rectangle with the arch openings as notches (holes touching the bottom are
    # made into notches by starting the outline below the ground)
    raise_w = widths[3] / 2 + piers + 1.2
    uc = U((spans[3][0] + spans[3][1]) / 2)
    outline = [(0, E - 0.5), (W, E - 0.5), (W, E + H), (uc + raise_w, E + H), (uc + raise_w, E + H + 1.6),
               (uc - raise_w, E + H + 1.6), (uc - raise_w, E + H), (0, E + H)]
    hol = []
    for ol in holes:
        hol.append([(u, max(z, E - 0.0)) for u, z in ol])
    face(sol, ef, outline, "ashlar", holes=[[(u, z if z > E + 1e-6 else E - 0.25) for u, z in ol] for ol in hol], col=WARM)
    for ol in hol:
        olb = [(u, z if z > E + 1e-6 else E - 0.25) for u, z in ol]
        reveal(sol, ef, olb, 0.0, -piers, "ashlar", col=GREYSTONE, skip_bottom=True)
    # porch interior box (inward faces): back wall with doors, ceiling, end walls
    eb = Edge(tuple(ef.P(0, 0, -D)[:2]), tuple(ef.P(ef.L, 0, -D)[:2]))   # back wall facing north (into the porch)
    doors = []
    for i, (a0_, a1_) in enumerate(spans):
        ucen = (a0_ + a1_) / 2
        dw = 2.2 if i != 3 else 2.8
        doors.append(ucen)
    for i, ucen in enumerate(doors):
        uu = U(ucen)
        dw = 2.8 if i == 3 else 2.2
        quad_uv(sol, [eb.P(uu - dw / 2, E, 0.02), eb.P(uu + dw / 2, E, 0.02), eb.P(uu + dw / 2, E + 3.4, 0.02),
                      eb.P(uu - dw / 2, E + 3.4, 0.02)], "doors", eb.n, mk.atlas_rect(gen["doors"]["grid"],
                                                                                         gen["doors"]["cells"]["door_wood"]))
    face(sol, eb, [(piers, E - 0.1), (eb.L - piers, E - 0.1), (eb.L - piers, z_c), (piers, z_c)], "ashlar", col=GREYSTONE)
    q = [ef.P(piers, z_c, -piers), ef.P(ef.L - piers, z_c, -piers), ef.P(ef.L - piers, z_c, -D), ef.P(piers, z_c, -D)]
    sol.poly(q, "dressed", -UP, col=GREYSTONE)
    q = [ef.P(0.3, E, -0.02), ef.P(ef.L - 0.3, E, -0.02), ef.P(ef.L - 0.3, E, -D), ef.P(0.3, E, -D)]
    sol.poly(q, "paving", UP)                            # porch floor (no spec ground under buildings)
    for ua, sgn in ((piers, 1), (ef.L - piers, -1)):
        q = [ef.P(ua, E - 0.1, -piers), ef.P(ua, E - 0.1, -D), ef.P(ua, z_c, -D), ef.P(ua, z_c, -piers)]
        sol.poly(q, "ashlar", ef.t * sgn, col=GREYSTONE)
    # front face soffit between piers above the arch tops is the ceiling; arch reveal tops close the wall
    # ---- roof over the hall and porch, crenellated parapet along the facade
    cap(sol, ring, E + H, "leaddome")
    u = 0.4
    while u < W - 0.6:
        c = ef.P(u + 0.3, 0, -0.35)
        if not (uc - raise_w < u + 0.3 < uc + raise_w):
            obox(dec, c, ef.t, 0.6, 0.55, E + H, E + H + 0.75, "ashlar", col=WARM)
        u += 1.15
    # raised central bay: a block behind the front face
    for (a_, b_, nn) in (((uc - raise_w, 0), (uc - raise_w, -3.0), -ef.t), ((uc + raise_w, -3.0), (uc + raise_w, 0), ef.t)):
        sol.poly([ef.P(a_[0], E + H, a_[1]), ef.P(b_[0], E + H, b_[1]), ef.P(b_[0], E + H + 1.6, b_[1]),
                  ef.P(a_[0], E + H + 1.6, a_[1])], "ashlar", nn, col=WARM)
    sol.poly([ef.P(uc + raise_w, E + H, -3.0), ef.P(uc - raise_w, E + H, -3.0), ef.P(uc - raise_w, E + H + 1.6, -3.0),
              ef.P(uc + raise_w, E + H + 1.6, -3.0)], "ashlar", -ef.n, col=WARM)
    sol.poly([ef.P(uc - raise_w, E + H + 1.6, 0), ef.P(uc + raise_w, E + H + 1.6, 0), ef.P(uc + raise_w, E + H + 1.6, -3.0),
              ef.P(uc - raise_w, E + H + 1.6, -3.0)], "lime", UP)
    _aqsa_nave(mbs, P, E, W, gen)
    _minaret_fakh(mbs, bd, gen)


def _blind_arcade_wall(mb, dec, gen, e, z0, z1, E, bay=4.3, margin=0.6):
    """Long wall of Al-Aqsa (H:10): tall pointed blind arches between pilasters, each holding a lower
    square window and an upper pointed window; a moulded band under the roof line."""
    nb = max(1, int((e.L - 2 * margin) // bay))
    bw = (e.L - 2 * margin) / nb
    holes, inner = [], []
    for j in range(nb):
        ua, ub = margin + bw * j + 0.45, margin + bw * (j + 1) - 0.45
        uc = (ua + ub) / 2
        ol = opening(ua, ub, E + 0.9, E + 6.4, "pointed", 10, 0.7)
        w1 = opening(uc - 0.5, uc + 0.5, E + 2.0, E + 3.5, "flat")
        w2 = opening(uc - 0.45, uc + 0.45, E + 5.0, E + 7.6 - arch_rise(0.9), "pointed", 6)
        holes.append(ol)
        inner.append((ol, [w1, w2]))
    face(mb, e, [(0, z0), (e.L, z0), (e.L, z1), (0, z1)], "ashlar", holes=holes, col=WARM)
    rect = cell_uv(gen, "window_grille")
    for ol, ws in inner:
        reveal(mb, e, ol, 0.0, -0.25, "ashlar", col=GREYSTONE, skip_bottom=False)
        face(mb, e, ol, "ashlar", off=-0.25, holes=ws, col=(0.95, 0.92, 0.86))
        for w in ws:
            reveal(mb, e, w, -0.25, -0.6, "ashlar", col=GREYSTONE, skip_bottom=False)
            za, zb = w[0][1], max(p[1] for p in w)
            face(mb, e, w, "faience", off=-0.6, uvf=rect_map(rect, w[0][0] - 0.12, w[1][0] + 0.12, za - 0.1, zb + 0.05))
    for j in range(nb + 1):                                 # pilasters at the bay boundaries
        uu = margin + bw * j
        wbox(mb, e, min(max(uu, 0.35), e.L - 0.35), 0.2, 0.7, 0.4, z0, z1 - 0.6, "ashlar", col=WARM)
    wbox(dec, e, e.L / 2, 0.12, e.L - 0.3, 0.24, z1 - 0.6, z1 - 0.25, "dressed", col=PALE, bottom=True)


def _wall_windows(mb, gen, e, z0, z1, zg, mat, col, rows=(), bay=4.3, margin=1.5):
    """Wall face with rows of recessed pointed windows (faience 'window_grille' cell at the back)."""
    holes = []
    if e.L > 2 * margin + 1.2:
        nb = max(1, int((e.L - 2 * margin) // bay))
        for (wa, wb, ww) in rows:
            for j in range(nb):
                ucn = margin + (e.L - 2 * margin) * (j + 0.5) / nb
                holes.append((opening(ucn - ww / 2, ucn + ww / 2, wa, wb - arch_rise(ww, "pointed"), "pointed", 8), ww))
    face(mb, e, [(0, z0), (e.L, z0), (e.L, z1), (0, z1)], mat, holes=[h for h, _ in holes], col=col)
    rect = cell_uv(gen, "window_grille")
    for ol, ww in holes:
        reveal(mb, e, ol, 0.0, -0.4, mat, col=GREYSTONE, skip_bottom=False)
        ua, ub = ol[0][0], ol[1][0]
        za, zb = ol[0][1], max(p[1] for p in ol)
        face(mb, e, ol, "faience", off=-0.4, uvf=rect_map(rect, ua - 0.12 * ww, ub + 0.12 * ww, za - 0.05 * (zb - za), zb + 0.02))


def _aqsa_nave(mbs, P, E, W, gen, lod=False):
    sol, dec = mbs["solid"], mbs["deco"]
    H, HN, RIDGE = 10.6, 13.0, 15.2
    ac = W / 2
    hw = 5.8
    # dome centre in the facade frame
    o = P(0, 0, 0)
    ux = (P(1, 0, 0) - o)
    sx = (P(0, 1, 0) - o)
    d = Vector((AQSA_DOME[0], AQSA_DOME[1], 0)) - Vector((o.x, o.y, 0))
    ad, bd_ = d.dot(ux), d.dot(sx)
    b0, b1 = 6.0, bd_ - 7.6                             # nave from behind the porch to the transept
    T = 7.6                                             # transept half size
    if lod:
        prism_walls(sol, [tuple(P(ac - hw, b1, 0)[:2]), tuple(P(ac + hw, b1, 0)[:2]), tuple(P(ac + hw, b0, 0)[:2]),
                          tuple(P(ac - hw, b0, 0)[:2])], E + H, E + HN, "ashlar", col=WARM)
        for s in (-1, 1):
            sol.poly([P(ac + s * hw, b0, E + HN), P(ac + s * hw, b1, E + HN), P(ac, b1, E + RIDGE), P(ac, b0, E + RIDGE)],
                     "leaddome", UP + (P(s, 0, 0) - o))
        sq_ = [tuple(P(ad - T, bd_ - T, 0)[:2]), tuple(P(ad + T, bd_ - T, 0)[:2]), tuple(P(ad + T, bd_ + T, 0)[:2]),
               tuple(P(ad - T, bd_ + T, 0)[:2])]
        sq_ = ccw(sq_)
        prism_walls(sol, sq_, E + H, E + 15.4, "ashlar", col=WARM)
        cap(sol, sq_, E + 15.4, "lime")
        mk.cylinder(sol, AQSA_DOME[0], AQSA_DOME[1], E + 15.2, E + 19.3, 7.0, "ashlar", seg=8, cap=False)
        dome_uv(sol, AQSA_DOME[0], AQSA_DOME[1], E + 19.3, 6.8, "leaddome", k=1.25, seg=10, rings=4)
        return
    # nave clerestory walls (with windows) and the north gable
    corners = [P(ac - hw, b0, 0), P(ac + hw, b0, 0), P(ac + hw, b1, 0), P(ac - hw, b1, 0)]
    cr = ccw([tuple(c[:2]) for c in corners])
    for i in range(4):
        e = Edge(cr[i], cr[(i + 1) % 4])
        if e.L > 20:
            _wall_windows(sol, gen, e, E + H - 0.3, E + HN, E, "ashlar", WARM, rows=((E + 11.1, E + 12.7, 0.8),), bay=4.6,
                          margin=1.0)
        else:
            prism = [(0, E + H - 0.3), (e.L, E + H - 0.3), (e.L, E + HN), (0, E + HN)]
            north = e.n.dot(Vector((0, 1, 0))) > 0
            if north:
                # gable end with two arched windows
                gab = prism[:3] + [(e.L / 2, E + RIDGE), (0, E + HN)]
                hs = [opening(e.L / 2 - 2.2, e.L / 2 - 0.8, E + 11.1, E + 12.4, "pointed", 8),
                      opening(e.L / 2 + 0.8, e.L / 2 + 2.2, E + 11.1, E + 12.4, "pointed", 8)]
                face(sol, e, gab, "ashlar", holes=hs, col=WARM)
                for ol in hs:
                    reveal(sol, e, ol, 0.0, -0.4, "ashlar", col=GREYSTONE, skip_bottom=False)
                    face(sol, e, ol, "faience", off=-0.4, uvf=rect_map(cell_uv(gen, "window_grille"), ol[0][0] - 0.15,
                                                                         ol[1][0] + 0.15, E + 11.0, E + 13.7))
    # gable roof (lead), slightly overhanging
    ov = 0.35
    for s in (-1, 1):
        q = [P(ac + s * (hw + ov), b0 - ov, E + HN - 0.2), P(ac + s * (hw + ov), b1, E + HN - 0.2), P(ac, b1, E + RIDGE),
             P(ac, b0 - ov, E + RIDGE)]
        hint = UP + (P(s, 0, 0) - o)
        dec.poly(q, "leaddome", hint, uv=[((p - o).dot(sx) / 2.0, (p - o).dot(ux) * s / 2.0) for p in q])
    # transept block under the dome
    sq_ = ccw([tuple(P(ad - T, bd_ - T, 0)[:2]), tuple(P(ad + T, bd_ - T, 0)[:2]), tuple(P(ad + T, bd_ + T, 0)[:2]),
               tuple(P(ad - T, bd_ + T, 0)[:2])])
    for i in range(4):
        e = Edge(sq_[i], sq_[(i + 1) % 4])
        _wall_windows(sol, gen, e, E + H - 0.3, E + 15.4, E, "ashlar", WARM, rows=((E + 12.2, E + 14.6, 0.9),), bay=3.6,
                      margin=1.2)
    cap(sol, sq_, E + 15.4, "lime")
    # drum: 24 facets, every facet with a window recess
    cx, cy = AQSA_DOME
    N = 24
    Rd = 7.0
    Dg = reg_poly((cx, cy), Rd, N, 0)
    z0, z1 = E + 15.2, E + 19.0
    for j in range(N):
        e = Edge(Dg[j], Dg[(j + 1) % N])
        ol = opening(e.L / 2 - 0.42, e.L / 2 + 0.42, z0 + 1.2, z1 - 1.1, "round", 6)
        face(sol, e, [(0, z0), (e.L, z0), (e.L, z1), (0, z1)], "ashlar", holes=[ol], col=WARM)
        reveal(sol, e, ol, 0.0, -0.35, "ashlar", col=GREYSTONE, skip_bottom=False)
        face(sol, e, ol, "faience", off=-0.35, uvf=rect_map(cell_uv(gen, "window_grille"), e.L / 2 - 0.55, e.L / 2 + 0.55,
                                                             z0 + 0.6, z1 - 0.5))
    Dr = reg_poly((cx, cy), Rd + 0.3, N, 0)
    band(sol, Dr, z1, z1 + 0.3, "dressed", inner=reg_poly((cx, cy), 6.8, N, 0), col=PALE, bottom=True)
    topz = dome_uv(sol, cx, cy, z1 + 0.3, 6.8, "leaddome", k=1.25, seg=40, rings=10, tile=2.0, n_u=24)
    finial(dec, cx, cy, topz, 2.6, "gold")


def _minaret_fakh(mbs, bd, gen, lod=False):
    name, c, kind = MINARETS[1]
    minaret(mbs, gen, c, (math.cos(WEST_WALL_BEARING), math.sin(WEST_WALL_BEARING)), esplanade(bd), kind, lod)


# ================================================================== Western Wall (+ Wilson's Arch hall)
def western_wall(mbs, bd, gen, place, lod=False):
    """Haram west wall at the prayer plaza (w817206833): plaza face 19 m high (Wikipedia/Western Wall:
    28 courses visible above the plaza) with 7 Herodian courses (~1.14 m, drafted margins, 'herodian')
    then smaller Umayyad/Mamluk/Ottoman courses ('fort'), each zone set back slightly; capers in the
    joints; the Haram-side face as the back of the west portico (blind arcade).  Wilson's Arch hall
    (w499210296) at the north end hangs off this builder.  H:27-H:31."""
    sol, dec = mbs["solid"], mbs["deco"]
    ring = ccw(bd["ring"])
    n = len(ring)
    eg = bd.get("edge_ground") or [bd["ground"]] * n
    G = bd["ground"]
    plaza = [i for i in range(n) if eg[i] < G - 2.0]
    zpl = min(eg[i] for i in plaza) if plaza else G
    z_top = max(zpl + 19.0, G + 2.0)
    z_her = zpl + 8.0
    rng = random.Random(817206833)
    for i in range(n):
        e = Edge(ring[i], ring[(i + 1) % n])
        if e.L < 0.05:
            continue
        if i in plaza:
            z0 = eg[i] - 0.6
            if lod:
                face(sol, e, [(0, z0), (e.L, z0), (e.L, z_her), (0, z_her)], "herodian")
                face(sol, e, [(0, z_her), (e.L, z_her), (e.L, z_top), (0, z_top)], "fort", col=(0.97, 0.95, 0.9))
                continue
            uvh = lambda u, z, e=e: ((e.A.dot(e.t) + u) / 8.0, (z - zpl) / 8.0)
            face(sol, e, [(0, z0), (e.L, z0), (e.L, z_her), (0, z_her)], "herodian", uvf=uvh, col=(1.0, 0.98, 0.95))
            # upper zones set back 0.12 m: ledge, Umayyad band (4 courses), Mamluk/Ottoman courses
            sb = -0.12
            sol.poly([e.P(0, z_her, 0), e.P(e.L, z_her, 0), e.P(e.L, z_her, sb), e.P(0, z_her, sb)], "herodian", UP)
            face(sol, e, [(0, z_her), (e.L, z_her), (e.L, zpl + 12.2), (0, zpl + 12.2)], "herodian", off=sb,
                 col=(0.93, 0.9, 0.84), uvf=lambda u, z, e=e: ((e.A.dot(e.t) + u) / 8.0 + 0.37, (z - zpl) / 8.0))
            face(sol, e, [(0, zpl + 12.2), (e.L, zpl + 12.2), (e.L, z_top), (0, z_top)], "fort", off=sb,
                 col=(0.93, 0.92, 0.9))
            # capers hanging from the joints, high up (H:31)
            for _ in range(int(e.L / 4.5)):
                u = rng.uniform(1.0, e.L - 1.0)
                z = zpl + rng.choice([2.4, 3.5, 4.6, 5.8, 6.9, 9.5, 11.0, 13.5, 15.0])
                p = e.P(u, z, 0.03 if z < z_her else sb + 0.03)
                place("caper", p, -math.atan2(e.n.x, e.n.y), True, rng.uniform(0.7, 1.15))
        else:
            z0 = G - 0.6
            if lod or e.L < 12:
                face(sol, e, [(0, z0), (e.L, z0), (e.L, z_top), (0, z_top)], "ashlar", col=WARM)
                continue
            # back of the west portico facing the esplanade: blind pointed arcade, dark recesses
            nb = max(1, int(e.L // 4.4))
            holes = []
            for j in range(nb):
                ucn = e.L * (j + 0.5) / nb
                holes.append(opening(ucn - 1.5, ucn + 1.5, G, G + 4.6, "pointed", 8))
            hb = [[(u, z if z > G + 1e-6 else G - 0.25) for u, z in ol] for ol in holes]
            face(sol, e, [(0, z0), (e.L, z0), (e.L, z_top), (0, z_top)], "ashlar", holes=hb, col=WARM)
            for ol in hb:
                reveal(sol, e, ol, 0.0, -1.6, "ashlar", col=(0.7, 0.68, 0.64), skip_bottom=True)
                face(sol, e, ol, "ashlar", off=-1.6, col=(0.45, 0.43, 0.4))
    cap(sol, ring, z_top, "lime")
    # parapet along the plaza face
    if not lod:
        for i in plaza:
            e = Edge(ring[i], ring[(i + 1) % n])
            obox(dec, e.P(e.L / 2, 0, -0.35), e.t, e.L, 0.5, z_top, z_top + 0.9, "fort", col=(0.93, 0.92, 0.9))
    _wilson_hall(mbs, gen, zpl, lod=lod)
    _minaret_silsila(mbs, bd, gen, lod=lod)


def _minaret_silsila(mbs, bd, gen, lod=False):
    name, c, kind = MINARETS[0]
    minaret(mbs, gen, c, (math.cos(WEST_WALL_BEARING), math.sin(WEST_WALL_BEARING)), esplanade(bd), kind, lod)


def _wilson_hall(mbs, gen, zf, lod=False):
    """Wilson's Arch hall (w499210296): south front on the prayer plaza with the end of Wilson's Arch
    (span 12.8 m E-W next to the Wall, semicircular, apex ~8 m above today's floor; Wikipedia) and
    two smaller arches to the west; barrel vault running north 15 m inside; flat roof below the
    Chain Street level.  Footprint and front from OSM; heights M (H:27, H:30, H:31)."""
    sol, dec = mbs["solid"], mbs["deco"]
    ring = ccw(WILSON_HALL)
    a, b = Vector((621.91, 30.53, 0)), Vector((646.06, 35.24, 0))
    ef = Edge(tuple(a[:2]), tuple(b[:2]))
    if ef.n.y > 0:
        ef = Edge(tuple(b[:2]), tuple(a[:2]))
    zs_street = terrain_z(633.0, 61.0)                  # Chain Street over the hall (north edge)
    z_top = (zs_street - 0.03) if zs_street is not None and zs_street > zf + 9.0 else zf + 9.6
    if lod:
        prism_walls(sol, ring, zf - 0.5, z_top, "ashlar", col=WARM)
        cap(sol, ring, z_top, "lime")
        return
    L = ef.L
    # which end of the front touches the Wall (east end, larger x)
    east_u = L if ef.P(L, 0).x > ef.P(0, 0).x else 0.0
    span = 12.8
    ua, ub = (L - span - 0.3, L - 0.3) if east_u == L else (0.3, span + 0.3)
    zs = zf + 1.6
    big = opening(ua, ub, zf, zs, "round", 16)
    small = []
    rest = (0.8, ua - 0.8) if east_u == L else (ub + 0.8, L - 0.8)
    for j in range(2):
        uc = rest[0] + (rest[1] - rest[0]) * (j + 0.5) / 2
        small.append(opening(uc - 1.6, uc + 1.6, zf, zf + 3.4, "round", 10))
    holes = [[(u, z if z > zf + 1e-6 else zf - 0.25) for u, z in ol] for ol in [big] + small]
    for i in range(len(ring)):
        e = Edge(ring[i], ring[(i + 1) % len(ring)])
        if abs(e.t.dot(ef.t)) > 0.99 and abs((e.A - ef.A).dot(ef.n)) < 0.5:
            continue                                     # front handled below
        if e.L < 0.3:
            continue
        face(sol, e, [(0, zf - 0.5), (e.L, zf - 0.5), (e.L, z_top), (0, z_top)], "ashlar", col=WARM)
    # the end at the Wall runs 1 m on into it: the Wall's face is inset from its OSM ring, which left a
    # slit of sky in the corner
    u0_, u1_ = (0.0, L + 1.0) if east_u == L else (-1.0, L)
    face(sol, ef, [(u0_, zf - 0.5), (u1_, zf - 0.5), (u1_, z_top), (u0_, z_top)], "ashlar", holes=holes, col=WARM)
    for ol in holes:
        reveal(sol, ef, ol, 0.0, -1.2, "ashlar", col=GREYSTONE, skip_bottom=True)
    cap(sol, ring, z_top, "lime")
    # barrel vault (Wilson's Arch) running north, inward faces; dark end wall
    vault_len = 15.0
    cv = arch_curve(ua, ub, zs, "round", 16)
    for i in range(len(cv) - 1):
        p0, p1 = cv[i], cv[i + 1]
        q = [ef.P(p0[0], p0[1], -1.2), ef.P(p1[0], p1[1], -1.2), ef.P(p1[0], p1[1], -vault_len), ef.P(p0[0], p0[1], -vault_len)]
        sol.poly(q, "rubble", ef.P((ua + ub) / 2, zs, -5) - (q[0] + q[2]) / 2, col=(0.72, 0.69, 0.64))
    for uu, sgn in ((ua, 1), (ub, -1)):
        q = [ef.P(uu, zf - 0.1, -1.2), ef.P(uu, zf - 0.1, -vault_len), ef.P(uu, zs, -vault_len), ef.P(uu, zs, -1.2)]
        sol.poly(q, "herodian" if (uu == ub) == (east_u == L) else "ashlar", ef.t * sgn, col=(0.85, 0.82, 0.78))
    end = opening(ua, ub, zf - 0.1, zs, "round", 16)
    face(sol, ef, end, "rubble", off=-vault_len, col=(0.5, 0.47, 0.43))
    sol.poly([ef.P(ua, zf, -0.02), ef.P(ub, zf, -0.02), ef.P(ub, zf, -vault_len), ef.P(ua, zf, -vault_len)], "paving", UP)
    for ol in holes[1:]:
        u0_, u1_ = ol[0][0], ol[1][0]
        sol.poly([ef.P(u0_, zf, -0.02), ef.P(u1_, zf, -0.02), ef.P(u1_, zf, -1.2), ef.P(u0_, zf, -1.2)], "paving", UP)
    for ol in holes[1:]:
        face(sol, ef, ol, "rubble", off=-1.2, col=(0.4, 0.38, 0.35))


# ================================================================== Golden Gate
def _base_wall_near(p, max_d=12.0):
    """Generic city-wall segment of data/spec/base.json nearest to p: (a, b, z1, thick) or None."""
    key = "base_walls"
    if key not in _SPEC_CACHE:
        try:
            _SPEC_CACHE[key] = json.loads((ROOT / "data/spec/base.json").read_text()).get("walls_generic", [])
        except Exception:                               # noqa: BLE001
            _SPEC_CACHE[key] = []
    best = None
    P_ = Vector((p[0], p[1]))
    for w in _SPEC_CACHE[key]:
        a, b = Vector(w["a"]), Vector(w["b"])
        ab = b - a
        t = max(0.0, min(1.0, (P_ - a).dot(ab) / max(ab.length_squared, 1e-9)))
        d = (a + ab * t - P_).length
        if d < max_d and (best is None or d < best[0]):
            best = (d, w)
    return best[1] if best else None


def golden_gate(mbs, bd, gen, place, lod=False):
    """Golden Gate (w291836693): double gate, 27 x 17 m (OSM), roof ~6 m above the esplanade with two
    low domes (OSM parts w291836700/701, r 3.0 / 2.6), west front with two broad arches under
    decorated archivolts (H:21, H:24-H:26); east front on the city wall: two blocked arches with
    archivolts (H:22, H:08).  The building is clipped at the inner face of the generic city wall
    from base.json; the east relief is a slab on the wall's outer face.  The sunken court in front of
    the west front needs a ground hole (spec request)."""
    sol, dec = mbs["solid"], mbs["deco"]
    E = bd["ground"]
    ring = ccw(bd["ring"])
    n = len(ring)
    eg = bd.get("edge_ground") or [E] * n
    # west and east fronts
    i_w = min(range(n), key=lambda i: Edge(ring[i], ring[(i + 1) % n]).n.x)
    i_e = max(range(n), key=lambda i: Edge(ring[i], ring[(i + 1) % n]).n.x)
    ew, ee = Edge(ring[i_w], ring[(i_w + 1) % n]), Edge(ring[i_e], ring[(i_e + 1) % n])
    wall = _base_wall_near(ee.P(ee.L / 2, 0))
    if wall:
        a, b = Vector(wall["a"]), Vector(wall["b"])
        t = (b - a).normalized()
        nr = Vector((t.y, -t.x))                         # right of a->b: outside the city
        mid = Vector(tuple(ee.P(ee.L / 2, 0)[:2]))
        if (mid - Vector(centroid(ring))).dot(nr) < 0:   # outward = from the gate body towards the wall
            nr = -nr
        try:                                             # the circuit builder's convention for the OSM line
            import landmarks_gates
            line = getattr(landmarks_gates, "WALL_LINE", "centre")
        except Exception:                                # noqa: BLE001
            line = "centre"
        if line == "outer":                              # OSM line = outer face, the wall lies inside it
            inner_off, outer_off = -wall["thick"] + 0.4, 0.0
        else:
            inner_off, outer_off = -wall["thick"] / 2 + 0.4, wall["thick"] / 2
        z_wall = wall["z1"]
    else:
        a = Vector(tuple(ee.A[:2]))
        t = Vector(tuple(ee.t[:2]))
        nr = Vector(tuple(ee.n[:2]))
        inner_off, outer_off, z_wall = -3.0, 0.0, E + 11.0
    # clip the footprint: keep the part on the inner side of the line a + nr*inner_off
    p0 = a + nr * inner_off
    clipped = []
    for i in range(n):
        P1, P2 = Vector(ring[i]), Vector(ring[(i + 1) % n])
        d1, d2 = (P1 - p0).dot(nr), (P2 - p0).dot(nr)
        if d1 <= 0:
            clipped.append(tuple(P1))
        if (d1 < 0) != (d2 < 0):
            f = d1 / (d1 - d2)
            clipped.append(tuple(P1 + (P2 - P1) * f))
    body = ccw(clipped)
    z_roof = E + 7.0
    m = len(body)
    for i in range(m):
        e = Edge(body[i], body[(i + 1) % m])
        if e.L < 0.05:
            continue
        if abs((Vector(tuple(e.A[:2])) - p0).dot(nr)) < 0.05 and abs(e.t.dot(Vector((t.x, t.y, 0)))) > 0.95:
            continue                                     # the clipped end inside the wall
        if e.n.x < -0.9 and not lod:
            _gg_front(sol, dec, e, E - 4.8, z_roof, E - 4.5, gen)
        else:
            face(sol, e, [(0, E - 0.8), (e.L, E - 0.8), (e.L, z_roof), (0, z_roof)], "ashlar", col=WARM)
    cap(sol, body, z_roof, "lime")
    if not lod:
        # parapet (low wall) along the roof edge except the wall side
        for i in range(m):
            e = Edge(body[i], body[(i + 1) % m])
            if e.L < 0.5 or (abs((Vector(tuple(e.A[:2])) - p0).dot(nr)) < 0.05 and abs(e.t.dot(Vector((t.x, t.y, 0)))) > 0.95):
                continue
            obox(dec, e.P(e.L / 2, 0, -0.2), e.t, e.L, 0.4, z_roof, z_roof + 0.8 + 0.03 * (i % 2), "ashlar", col=WARM)
    for (c, r) in GG_DOMES:
        D = reg_poly(c, r + 0.1, 16, 0)
        if lod:
            dome_uv(sol, c[0], c[1], z_roof, r, "lime", k=1.0, seg=8, rings=3)
            continue
        prism_walls(dec, D, z_roof - 0.05, z_roof + 0.7, "ashlar", col=WARM)
        cap(dec, D, z_roof + 0.7, "dressed", col=PALE)
        dome_uv(dec, c[0], c[1], z_roof + 0.7, r * 0.97, "ashlar", k=1.0, seg=20, rings=6, tile=3.0, col=(0.98, 0.92, 0.82))
    if not lod:
        _gg_court(mbs, body, E, gen)
    # east relief on the outer face of the city wall
    if wall:
        z_out = eg[i_e] if eg[i_e] < E else E - 7.0
        ue0 = (Vector(tuple(ee.P(0, 0)[:2])) - a).dot(t)
        ue1 = (Vector(tuple(ee.P(ee.L, 0)[:2])) - a).dot(t)
        ua, ub = sorted((ue0, ue1))
        PR = 1.0                                         # the gate block projects ~1 m from the wall
        er = Edge(tuple(a + t * ua + nr * (outer_off + PR)), tuple(a + t * ub + nr * (outer_off + PR)))
        if er.n.dot(Vector((nr.x, nr.y, 0))) < 0:
            er = Edge(tuple(a + t * ub + nr * (outer_off + PR)), tuple(a + t * ua + nr * (outer_off + PR)))
        L = er.L
        zt = z_wall + 1.6                                # the gate block rises above the curtain (H:22)
        if lod:
            face(sol, er, [(0, z_out - 0.5), (L, z_out - 0.5), (L, zt), (0, zt)], "ashlar", col=WARM)
        else:
            # two blocked arches (filled with smaller stones) under archivolts, a cornice band
            zs = z_out + 6.2
            arches = [(L * 0.1, L * 0.47), (L * 0.53, L * 0.9)]
            holes = [opening(u0, u1, z_out + 3.0, zs, "round", 14) for u0, u1 in arches]
            face(sol, er, [(0, z_out - 0.5), (L, z_out - 0.5), (L, zt), (0, zt)], "ashlar", holes=holes, col=WARM)
            for ol in holes:
                reveal(sol, er, ol, 0.0, -0.3, "ashlar", col=GREYSTONE, skip_bottom=False)
                face(sol, er, ol, "fort", off=-0.3, col=(0.95, 0.9, 0.82))
                # archivolt ring
                u0, u1 = ol[0][0], ol[1][0]
                cv_o = arch_curve(u0 - 0.55, u1 + 0.55, zs, "round", 14)
                cv_i = arch_curve(u0 - 0.05, u1 + 0.05, zs, "round", 14)
                arch_band(dec, er, cv_i, cv_o, 0.18, "dressed", col=(0.98, 0.9, 0.75))
                for k in range(len(cv_o) - 1):
                    q2 = [er.P(*cv_o[k], 0.0), er.P(*cv_o[k + 1], 0.0), er.P(*cv_o[k + 1], 0.18), er.P(*cv_o[k], 0.18)]
                    dec.poly(q2, "dressed", (q2[0] + q2[2]) / 2 - er.P((u0 + u1) / 2, zs, 0.09), col=(0.95, 0.88, 0.74))
            # sides and top of the relief slab
            for uu, sgn in ((0, -1), (L, 1)):
                q = [er.P(uu, z_out - 0.5, -PR - 0.05), er.P(uu, z_out - 0.5, 0), er.P(uu, zt, 0), er.P(uu, zt, -PR - 0.05)]
                sol.poly(q, "ashlar", er.t * sgn, col=WARM)
            sol.poly([er.P(0, zt, -PR - 0.05), er.P(L, zt, -PR - 0.05), er.P(L, zt, 0), er.P(0, zt, 0)], "ashlar", UP, col=WARM)
            sol.poly([er.P(L, z_wall - 0.1, -PR - 0.05), er.P(0, z_wall - 0.1, -PR - 0.05), er.P(0, zt, -PR - 0.05),
                      er.P(L, zt, -PR - 0.05)], "ashlar", -er.n, col=WARM)   # back of the part above the curtain
            nm = max(3, int(L // 2.1))
            for j in range(nm):                          # merlons along the outer edge
                uu = L * (j + 0.5) / nm
                wbox(dec, er, uu, -0.3, 1.2, 0.6, zt, zt + 1.0 + 0.02 * (j % 2), "ashlar", col=WARM)
            # blocked doorways at the foot, rosettes and the round window above (H:22)
            for u0, u1 in arches:
                um = (u0 + u1) / 2
                ol = opening(um - 0.8, um + 0.8, z_out + 0.2, z_out + 2.0, "pointed", 8)
                face(dec, er, ol, "fort", off=0.06, col=(0.9, 0.84, 0.74))
            for uu in (L * 0.1, L * 0.5, L * 0.9):
                pr_ = er.P(uu, zs + 1.0, 0.0)
                ball(dec, (pr_.x, pr_.y, pr_.z), 0.35, "dressed", seg=8, rings=4, col=(0.95, 0.9, 0.8))
            ring_c = er.P(L / 2, 0, 0.12)
            ball(dec, (ring_c.x, ring_c.y, zt - 3.2), 0.9, "dressed", seg=10, rings=4, col=(0.95, 0.9, 0.8))


GG_COURT = (884.0, 249.0, 892.0, 266.0)      # main session's SUNKEN box (make_spec): street - 4.5


def _gg_court(mbs, body, E, gen):
    """Sunken court before the west front (H:24, H:25): ashlar retaining walls from the court floor
    (E - 4.5) to the esplanade, iron railing on the coping, a stair flight down from the west."""
    sol, dec = mbs["solid"], mbs["deco"]
    x0, y0, x1, y1 = GG_COURT
    zc = E - 4.5
    # clip the box's east side at the gate's west face: use the body vertex x range on that side
    xe = max(x0 + 1.0, min(p[0] for p in body) + 0.02) if body else x1
    rail = mk.atlas_rect(gen["cutout"]["grid"], gen["cutout"]["cells"]["rail_moat"])
    # walls facing into the court: south (y0, faces north), west (x0, faces east), north (y1, faces south)
    sides = [((xe, y0), (x0, y0)), ((x0, y0), (x0, y1)), ((x0, y1), (xe, y1))]
    for i, (a, b) in enumerate(sides):
        e = Edge(a, b)                                   # outward normal = right of a->b = into the court
        face(sol, e, [(0, zc - 0.3), (e.L, zc - 0.3), (e.L, E - 0.25), (0, E - 0.25)], "ashlar", col=WARM)
        obox(sol, e.P(e.L / 2, 0, -0.25), e.t, e.L + 0.5, 0.5, E - 0.25, E + 0.16 + 0.02 * (i % 2), "dressed", col=PALE)
        mk.card(dec, e.P(e.L / 2, E + 0.16, -0.25), e.t, UP, e.L, 1.0, "cut", rail, double=True)
    # stair flight from the west edge down eastwards, 2.4 m wide, centred on the court
    yc = (y0 + y1) / 2
    ea = Edge((x0, yc + 1.2), (x0, yc - 1.2))            # outward normal = +x (east, into the court)
    nst = round(4.5 / 0.2)
    r = 4.5 / nst
    tread = min(0.28, (xe - x0 - 0.8) / nst)
    for k in range(1, nst + 1):
        zk = E - k * r
        a_, b_ = (k - 1) * tread, k * tread
        if k < nst:
            sol.poly([ea.P(0, zk, a_), ea.P(ea.L, zk, a_), ea.P(ea.L, zk, b_), ea.P(0, zk, b_)], "paving", UP)
        if k >= 2:
            z0_ = zk if k < nst else zc - 0.3
            sol.poly([ea.P(0, z0_, a_), ea.P(ea.L, z0_, a_), ea.P(ea.L, zk + r, a_), ea.P(0, zk + r, a_)], "dressed", ea.n,
                     col=(0.9, 0.88, 0.84))
        if k < nst:
            for ua, sgn in ((0, -1), (ea.L, 1)):
                sol.poly([ea.P(ua, zc - 0.3, a_), ea.P(ua, zc - 0.3, b_), ea.P(ua, zk, b_), ea.P(ua, zk, a_)], "ashlar",
                         ea.t * sgn, col=WARM)


def _gg_front(sol, dec, e, z0, z1, zb, gen):
    """West front: two broad arches with double archivolts and a moulded impost band (H:26)."""
    L = e.L
    zs = zb + 5.4                                      # court floor + 5.4: springing ~1 m above the esplanade
    arches = [(0.9, L / 2 - 0.45), (L / 2 + 0.45, L - 0.9)]
    holes = [opening(u0, u1, zb - 0.1, zs, "round", 14) for u0, u1 in arches]
    face(sol, e, [(0, z0), (L, z0), (L, z1), (0, z1)], "ashlar", holes=holes, col=WARM)
    door = mk.atlas_rect(gen["doors"]["grid"], gen["doors"]["cells"]["door_green2"])
    for ol in holes:
        reveal(sol, e, ol, 0.0, -0.45, "ashlar", col=GREYSTONE, skip_bottom=True)
        face(sol, e, ol, "ashlar", off=-0.45, col=(0.92, 0.86, 0.76))
        u0, u1 = ol[0][0], ol[1][0]
        um = (u0 + u1) / 2                               # the walled-up doorway with a green grille (H:24)
        quad_uv(sol, [e.P(um - 1.0, zb, -0.43), e.P(um + 1.0, zb, -0.43), e.P(um + 1.0, zb + 2.9, -0.43),
                      e.P(um - 1.0, zb + 2.9, -0.43)], "doors", e.n, door)
        for (w0, w1, off) in ((0.05, 0.4, 0.15), (0.45, 0.8, 0.08)):
            cv_o = arch_curve(u0 - w1, u1 + w1, zs, "round", 14)
            cv_i = arch_curve(u0 - w0, u1 + w0, zs, "round", 14)
            arch_band(dec, e, cv_i, cv_o, off, "dressed", col=(1.0, 0.92, 0.78))
            for k in range(len(cv_o) - 1):
                q2 = [e.P(*cv_o[k], 0.0), e.P(*cv_o[k + 1], 0.0), e.P(*cv_o[k + 1], off), e.P(*cv_o[k], off)]
                dec.poly(q2, "dressed", (q2[0] + q2[2]) / 2 - e.P((u0 + u1) / 2, zs, off / 2), col=(0.95, 0.88, 0.74))
    # impost / cornice band across the front
    wbox(dec, e, L / 2, 0.1, L + 0.2, 0.2, z1 - 0.6, z1 - 0.35, "dressed", col=PALE, bottom=True)


# ================================================================== porticoes, gates, wall strips, small buildings
HARAM_C = (760.0, 170.0)


def _toward_inside(e):
    m = e.P(e.L / 2, 0)
    v = Vector((HARAM_C[0] - m.x, HARAM_C[1] - m.y, 0)).normalized()
    return e.n.dot(v)


def _facade(mb, gen, e, z0, z1, arches=(), windows=(), col=WARM, depth=3.0, zf=None, mat="ashlar", doors=()):
    """Wall face with deep arched recesses (arches: (u0, u1, zs, k), floor zf, dark back) and small
    recessed windows (windows: (uc, w, z0, z1))."""
    holes, arch_ols, win_ols = [], [], []
    for (u0, u1, zs, k) in arches:
        ol = opening(u0, u1, zf - 0.25, zs, "pointed", 10, k)
        holes.append(ol)
        arch_ols.append((ol, u0, u1))
    for (uc, w, wa, wb) in windows:
        ol = opening(uc - w / 2, uc + w / 2, wa, wb - arch_rise(w, "pointed"), "pointed", 6)
        holes.append(ol)
        win_ols.append(ol)
    face(mb, e, [(0, z0), (e.L, z0), (e.L, z1), (0, z1)], mat, holes=holes, col=col)
    for ol, u0, u1 in arch_ols:
        reveal(mb, e, ol, 0.0, -depth, mat, col=(0.82, 0.79, 0.74), skip_bottom=True)
        face(mb, e, ol, mat, off=-depth, col=(0.5, 0.48, 0.45))
        mb.poly([e.P(u0, zf, 0), e.P(u1, zf, 0), e.P(u1, zf, -depth), e.P(u0, zf, -depth)], "paving", UP)
    for ol in win_ols:
        reveal(mb, e, ol, 0.0, -0.35, mat, col=GREYSTONE, skip_bottom=False)
        face(mb, e, ol, "faience", off=-0.35,
             uvf=rect_map(cell_uv(gen, "window_grille"), ol[0][0] - 0.1, ol[1][0] + 0.1, ol[0][1] - 0.15, max(q[1] for q in ol) + 0.05))
    for (uc, w, h) in doors:
        quad_uv(mb, [e.P(uc - w / 2, zf, -depth + 0.02), e.P(uc + w / 2, zf, -depth + 0.02), e.P(uc + w / 2, zf + h, -depth + 0.02),
                     e.P(uc - w / 2, zf + h, -depth + 0.02)], "doors", e.n,
                mk.atlas_rect(gen["doors"]["grid"], gen["doors"]["cells"]["door_wood"]))


def riwaq(mbs, bd, gen, place, lod=False):
    """Portico (riwaq) / madrasa range along the N and W sides (H:18, H:15 background): pointed arcade
    towards the esplanade (bays 4.2 m, arches springing 3.6 m, vaulted recesses 3 m deep), an upper
    storey with small arched windows, flat roof 9.5 m above the ground (the generic 15 m with shop
    facades was too tall).  Other sides plain with windows."""
    sol, dec = mbs["solid"], mbs["deco"]
    E = bd["ground"]
    H = 9.5
    ring = ccw(bd["ring"])
    n = len(ring)
    for i in range(n):
        e = Edge(ring[i], ring[(i + 1) % n])
        if e.L < 0.3:
            continue
        if lod:
            face(sol, e, [(0, E - 0.6), (e.L, E - 0.6), (e.L, E + H), (0, E + H)], "ashlar", col=WARM)
            continue
        nb = int((e.L - 1.0) // 4.2)
        if _toward_inside(e) > 0.6 and int((e.L - 6.4) // 4.2) >= 1:
            nb = int((e.L - 6.4) // 4.2)
            m = (e.L - nb * 4.2) / 2
            arches = [(m + 4.2 * j + 0.6, m + 4.2 * (j + 1) - 0.6, E + 3.6, 0.72) for j in range(nb)]
            wins = [(m + 4.2 * (j + 0.5), 0.8, E + 6.0, E + 7.9) for j in range(nb)]
            _facade(sol, gen, e, E - 0.6, E + H, arches, wins, zf=E, depth=3.0)
            wbox(dec, e, e.L / 2, 0.1, e.L, 0.2, E + 5.0, E + 5.25, "dressed", col=PALE, bottom=True)
        elif nb >= 1:
            m = (e.L - nb * 4.2) / 2
            wins = [(m + 4.2 * (j + 0.5), 0.8, E + 6.0, E + 7.9) for j in range(nb)]
            _facade(sol, gen, e, E - 0.6, E + H, (), wins, zf=E)
        else:
            face(sol, e, [(0, E - 0.6), (e.L, E - 0.6), (e.L, E + H), (0, E + H)], "ashlar", col=WARM)
    cap(sol, ring, E + H, "lime")


def haram_gate(mbs, bd, gen, place, lod=False):
    """Gate building of the Haram (Bab al-Silsila, al-Qattanin, al-Hadid ...): a block with a tall pointed
    portal on the esplanade side and on the street side (recess 1.8 m, closed wooden leaves),
    9.5 m high."""
    sol, dec = mbs["solid"], mbs["deco"]
    E = bd["ground"]
    H = 9.5
    ring = ccw(bd["ring"])
    n = len(ring)
    ranks = sorted(range(n), key=lambda i: -abs(_toward_inside(Edge(ring[i], ring[(i + 1) % n]))))
    portals = set(ranks[:2])
    for i in range(n):
        e = Edge(ring[i], ring[(i + 1) % n])
        if e.L < 0.3:
            continue
        zf = (bd.get("edge_ground") or [E] * n)[i]
        if not lod and i in portals and e.L > 3.6:
            w = min(3.4, e.L - 1.6)
            uc = e.L / 2
            _facade(sol, gen, e, min(zf, E) - 0.6, E + H, [(uc - w / 2, uc + w / 2, zf + 3.4, 0.8)], (), zf=zf, depth=1.8,
                    doors=[(uc, w, 3.6)])
            # frame: a dressed arch band around the portal
            cv_o = arch_curve(uc - w / 2 - 0.35, uc + w / 2 + 0.35, zf + 3.4, "pointed", 10, 0.8)
            cv_i = arch_curve(uc - w / 2, uc + w / 2, zf + 3.4, "pointed", 10, 0.8)
            arch_band(dec, e, cv_i, cv_o, 0.06, "dressed", col=PALE)
        else:
            face(sol, e, [(0, min(zf, E) - 0.6), (e.L, min(zf, E) - 0.6), (e.L, E + H), (0, E + H)], "ashlar", col=WARM)
    cap(sol, ring, E + H, "lime")


def wall_strip(mbs, bd, gen, place, lod=False):
    """OSM building=wall strips along the E and S Haram walls: the inner part of the wall, a plain
    ashlar mass up to 0.3 m below the generic city wall's top (base.json), so the wall's merlons read
    above it.  No windows (they were shop-house facades)."""
    sol = mbs["solid"]
    E = bd["ground"]
    ring = ccw(bd["ring"])
    w = _base_wall_near(centroid(ring), max_d=25.0)
    zt = (w["z1"] - 0.3) if w else E + 6.0
    zt = max(zt, E + 2.5)
    eg = bd.get("edge_ground") or [E] * len(ring)
    for i in range(len(ring)):
        e = Edge(ring[i], ring[(i + 1) % len(ring)])
        if e.L < 0.05:
            continue
        z0 = min(eg[i], E) - 0.6
        mid = ((ring[i][0] + ring[(i + 1) % len(ring)][0]) / 2, (ring[i][1] + ring[(i + 1) % len(ring)][1]) / 2)
        if eg[i] < E - 1 and _base_wall_near(mid, max_d=0.6):
            continue                                     # the city wall's own face stands there (it z-fought)
        face(sol, e, [(0, z0), (e.L, z0), (e.L, zt), (0, zt)], "fort" if eg[i] < E - 1 else "ashlar", col=WARM)
    cap(sol, ring, zt, "ashlar", col=WARM)


def madrasa_block(H):
    def fn(mbs, bd, gen, place, lod=False):
        """Two-storey Mamluk range (Islamic Museum / al-Fakhriyya): arched windows in two rows, flat roof."""
        sol = mbs["solid"]
        E = bd["ground"]
        ring = ccw(bd["ring"])
        eg = bd.get("edge_ground") or [E] * len(ring)
        for i in range(len(ring)):
            e = Edge(ring[i], ring[(i + 1) % len(ring)])
            if e.L < 0.05:
                continue
            z0 = min(eg[i], E) - 0.6
            if lod or e.L < 3.0:
                face(sol, e, [(0, z0), (e.L, z0), (e.L, E + H), (0, E + H)], "ashlar", col=WARM)
                continue
            nb = max(1, int((e.L - 1.0) // 3.6))
            m = (e.L - nb * 3.6) / 2
            wins = []
            for j in range(nb):
                uc = m + 3.6 * (j + 0.5)
                wins.append((uc, 0.9, E + 1.4, E + 3.4))
                if H > 7:
                    wins.append((uc, 0.8, E + 5.2, E + 7.0))
            _facade(sol, gen, e, z0, E + H, (), wins, zf=E)
        cap(sol, ring, E + H, "lime")
        if bd["id"] == "w291836691":
            pass
    return fn


def closed_qubba(h):
    def fn(mbs, bd, gen, place, lod=False):
        _closed_qubba(mbs, gen, ccw(bd["ring"]), bd["ground"], h=h, lod=lod)
    return fn


def open_qubba_ground(mbs, bd, gen, place, lod=False):
    ring = ccw(bd["ring"])
    C = centroid(ring)
    R = sum(math.dist(C, p) for p in ring) / len(ring)
    _open_qubba(mbs, gen, C, R * 0.9, 4, bd["ground"], h_col=2.6, dome_r=R * 0.75, lod=lod, a0=math.pi / 4)


def sabil_qaytbay(mbs, bd, gen, place, lod=False):
    """Sabil of Qaytbay (1482): square base ~3.7 m with grilled windows, a tall drum and a carved stone
    dome, 13 m (H:15 background; Archnet / Burgoyne).  Footprint from OSM (octagon of the base)."""
    sol, dec = mbs["solid"], mbs["deco"]
    E = bd["ground"]
    ring = ccw(bd["ring"])
    C = centroid(ring)
    R = sum(math.dist(C, p) for p in ring) / len(ring)
    hs = R * 0.72
    t = Vector(ring[1]) - Vector(ring[0])
    a0 = math.atan2(t.y, t.x)
    sq = [(C[0] + hs * math.cos(a0 + math.pi / 4 + k * math.pi / 2) * math.sqrt(2),
           C[1] + hs * math.sin(a0 + math.pi / 4 + k * math.pi / 2) * math.sqrt(2)) for k in range(4)]
    sq = ccw(sq)
    if lod:
        prism_walls(sol, sq, E - 0.4, E + 5.5, "dressed", col=PALE)
        cap(sol, sq, E + 5.5, "dressed", col=PALE)
        dome_uv(sol, C[0], C[1], E + 7.0, hs * 0.85, "dressed", k=1.35, seg=8, rings=3)
        mk.cylinder(sol, C[0], C[1], E + 5.5, E + 7.0, hs * 0.85, "dressed", seg=8, cap=False)
        return
    for i in range(4):
        e = Edge(sq[i], sq[(i + 1) % 4])
        ol = opening(e.L / 2 - 0.7, e.L / 2 + 0.7, E + 0.8, E + 2.6, "pointed", 8)
        face(sol, e, [(0, E - 0.4), (e.L, E - 0.4), (e.L, E + 5.5), (0, E + 5.5)], "dressed", holes=[ol], col=(1.0, 0.94, 0.86))
        reveal(sol, e, ol, 0.0, -0.4, "dressed", col=PALE, skip_bottom=False)
        face(sol, e, ol, "faience", off=-0.4, uvf=rect_map(cell_uv(gen, "window_grille"), ol[0][0] - 0.2, ol[1][0] + 0.2, E + 0.6, E + 3.5))
    band(dec, ccw([(C[0] + (p[0] - C[0]) * 1.08, C[1] + (p[1] - C[1]) * 1.08) for p in sq]), E + 5.2, E + 5.6, "dressed",
         inner=sq, col=PALE, bottom=True)
    cap(sol, sq, E + 5.5, "dressed", col=PALE)
    D = reg_poly(C, hs * 0.92, 16, a0)
    prism_walls(sol, D, E + 5.5, E + 7.4, "dressed", col=(1.0, 0.94, 0.86))
    cap(sol, D, E + 7.4, "dressed", col=PALE)
    topz = dome_uv(sol, C[0], C[1], E + 7.4, hs * 0.86, "dressed", k=1.4, seg=20, rings=8, tile=1.2, col=(1.0, 0.95, 0.88))
    finial(dec, C[0], C[1], topz, 1.3, "gold")


# ================================================================== registry
LANDMARKS = {
    "w4709536": dome_of_the_rock,
    "w45099263": dome_of_the_chain,
    "w280309331": al_aqsa,
    "w817206833": western_wall,
    "w291836693": golden_gate,
    "w137729566": _lifted_qubba(True),     # Dome of the Ascension: open octagon, columns, dome
    "w291836681": _lifted_qubba(True),     # Dome of the Tablets: tiny open kiosk
    "w291836713": dome_of_al_khalili,
}
for _q in QANATIR:
    LANDMARKS[_q] = qanatir
for _q in ("w291836727", "w291836706", "w291836724", "w291836735", "w291836712", "w291836721", "w291836708",
           "w508175933", "w620130981", "w291836726", "w291836720"):
    LANDMARKS[_q] = riwaq                    # porticoes / madrasa ranges, N and W sides
for _q in ("w1080613977", "w620099942", "w508175930", "w508175931", "w508175932", "w291836729", "w620099941"):
    LANDMARKS[_q] = wall_strip               # inner part of the E and S walls
for _q in ("w291836687", "w291836677", "w291836690", "w620130982", "w291836689", "w291836695", "w291836685",
           "w291836688", "w291836686", "w508175929", "w291836692"):
    LANDMARKS[_q] = haram_gate               # Chain, Cotton Merchants', Iron, Council, Watchman, Darkness,
                                             # Remission, Tribes, Ablution, East, Mughrabi
LANDMARKS["w291836691"] = madrasa_block(9.0)        # Islamic Museum (al-Fakhriyya buildings)
LANDMARKS["w291836679"] = closed_qubba(4.6)         # Dome of Suleiman Pasha
LANDMARKS["w291836678"] = closed_qubba(3.4)         # Dome of Solomon (octagon)
LANDMARKS["w291836718"] = closed_qubba(4.4)         # Dome of Musa
LANDMARKS["w291836730"] = closed_qubba(3.2)         # small octagonal qubbas (unnamed in OSM)
LANDMARKS["w291836731"] = closed_qubba(3.6)
LANDMARKS["w291836697"] = closed_qubba(3.6)
LANDMARKS["w291836719"] = open_qubba_ground         # Dome of Yusuf
LANDMARKS["w291836733"] = sabil_qaytbay             # Sabil of Qaytbay
