"""Procedural street-prop library for the Jaffa Gate build (run inside Blender).

build_library(mats, tiles, gen) -> {prop type: bpy.types.Mesh}. Each mesh is built once with
MeshBuilder(...).to_mesh("prop_<type>", mats); the main build places it many times as linked duplicates.

Conventions (metres, Z up, the prop's front faces +Y at yaw 0):
  ground props  origin at the centre of the footprint on the ground (z = 0)
  wall props    origin on the wall surface; the wall is the XZ plane at y = 0 and the prop sticks out
                towards +Y.  z = 0 is the mounting point:
                  wall_lantern  the bracket arm (lantern hangs below it, plate spans z -0.22..0.12)
                  ac_unit       underside of the unit (brackets reach down to z = -0.33)
                  spout         the pipe axis at the wall
                  caper         the root in the wall joint (cards spread from z ~ -0.45 to +0.4)
  roof props    water_heater, water_tank, sat_dish, antenna: origin on the roof surface
Colour: flat materials tinted by per-face vertex colour (COLOR_0, multiplied in the game); foliage cards
use the "cut" atlas; nothing invents a material name.
"""
import math
import random

from mathutils import Vector, geometry

from meshkit import MeshBuilder, atlas_rect, card, tess2d

UP = Vector((0, 0, 1))
TAU = 2 * math.pi

GROUND = ["lamp_post", "bollard", "bin_post", "dumpster", "bench", "info_board", "tree_olive", "tree_ficus",
          "cart", "box_stack", "crate_stack", "crate_single", "stool_stack", "plant_pot", "weeds"]
LITTER = ["bottle", "can", "cup", "paper", "bag", "pack", "flat_box", "butt_cluster"]
MODERN = ["lamp_modern", "lamp_modern_double", "lamp_disc", "bin_slatted", "bench_stone", "barrier_post",
          "banner_pole", "flagpole", "palm", "tree_young"]     # present-day plaza / square furniture (photo-matched)
WALL = ["wall_lantern", "ac_unit", "spout", "caper"]
ROOF = ["water_heater", "water_tank", "sat_dish", "antenna"]
KIND = {**{k: "ground" for k in GROUND + LITTER + MODERN}, **{k: "wall" for k in WALL},
        **{k: "roof" for k in ROOF}}


# ------------------------------------------------------------------ geometry helpers
def _frame(axis):
    w = Vector(axis).normalized()
    a = Vector((1, 0, 0)) if abs(w.x) < 0.9 else Vector((0, 1, 0))
    u = w.cross(a).normalized()
    return w, u, w.cross(u).normalized()


def obox(mb, c, size, mat, col=None, ax=(1, 0, 0), ay=(0, 1, 0), az=(0, 0, 1), skip=(), over=None, inward=False):
    """Oriented box centred at c with axes ax/ay/az and edge lengths size.
    skip: faces to leave out ('+x', '-z', ...); over: {face: (mat, col)} per-face overrides."""
    c = Vector(c)
    A = [Vector(ax).normalized() * size[0] / 2, Vector(ay).normalized() * size[1] / 2,
         Vector(az).normalized() * size[2] / 2]
    for key in ("+x", "-x", "+y", "-y", "+z", "-z"):
        if key in skip:
            continue
        i = "xyz".index(key[1])
        s = 1 if key[0] == "+" else -1
        j, k = [m for m in range(3) if m != i]
        fc = c + A[i] * s
        q = [fc - A[j] - A[k], fc + A[j] - A[k], fc + A[j] + A[k], fc - A[j] + A[k]]
        m, cl = (over or {}).get(key, (mat, col))
        mb.poly(q, m, A[i] * (-s if inward else s), col=cl)


def beam(mb, p0, p1, w, h, mat, col=None, up=(0, 0, 1), caps=True, cap0=None, cap1=None):
    """Rectangular bar from p0 to p1 (w across, h along `up`)."""
    p0, p1 = Vector(p0), Vector(p1)
    t = p1 - p0
    L = t.length
    t /= L
    u = Vector(up).normalized()
    if abs(t.dot(u)) > 0.98:
        u = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
    s = t.cross(u).normalized()
    u = s.cross(t).normalized()
    c0 = caps if cap0 is None else cap0
    c1 = caps if cap1 is None else cap1
    skip = tuple(k for k, on in (("-x", c0), ("+x", c1)) if not on)
    obox(mb, (p0 + p1) / 2, (L, w, h), mat, col, ax=t, ay=s, az=u, skip=skip)


def lathe(mb, prof, mat, col=None, seg=8, o=(0, 0, 0), axis=(0, 0, 1), cap0=None, cap1=None, bands=None,
          phase=0.0, ell=(1.0, 1.0)):
    """Surface of revolution of profile [(r, h), ...] about `axis` through o.
    The profile is walked with the solid on its inner side (bottom -> up on the outside, then inwards
    over a rim and down an inner wall), which fixes the facing. r = 0 makes an apex.
    cap0 / cap1: (mat, col) to close the first / last ring. bands: [(mat, col)] per profile segment."""
    o = Vector(o)
    w, u, v = _frame(axis)
    u, v = u * ell[0], v * ell[1]
    angs = [phase + TAU * k / seg for k in range(seg)]
    rings = [[o + w * h + (u * math.cos(a) + v * math.sin(a)) * r for a in angs] for r, h in prof]
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        if r0 < 1e-7 and r1 < 1e-7:
            continue
        m, cl = bands[i] if bands else (mat, col)
        dr, dh = r1 - r0, h1 - h0
        for k in range(seg):
            k2 = (k + 1) % seg
            am = phase + TAU * (k + 0.5) / seg
            hint = (u * math.cos(am) + v * math.sin(am)) * dh - w * dr
            if r0 < 1e-7:
                q = [rings[i][k], rings[i + 1][k], rings[i + 1][k2]]
            elif r1 < 1e-7:
                q = [rings[i][k], rings[i][k2], rings[i + 1][k]]
            else:
                q = [rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]]
            mb.poly(q, m, hint, col=cl)
    if cap0 and prof[0][0] > 1e-7:
        sgn = 1 if prof[1][1] >= prof[0][1] else -1
        mb.poly(rings[0], cap0[0], -w * sgn, col=cap0[1])
    if cap1 and prof[-1][0] > 1e-7:
        sgn = 1 if prof[-1][1] >= prof[-2][1] else -1
        mb.poly(rings[-1], cap1[0], w * sgn, col=cap1[1])
    return rings


def ttube(mb, pts, radii, mat, col=None, sides=5, cap=False, rng=None, jit=0.0, phase=0.0):
    """Tapered tube along a 3D polyline (parallel-transport frame); optional radial jitter (gnarl)."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    d = (pts[1] - pts[0]).normalized()
    a = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    x = d.cross(a).normalized()
    rings = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        x = (x - d * x.dot(d)).normalized()
        y = d.cross(x)
        ring = []
        for k in range(sides):
            ang = phase + TAU * k / sides
            rr = radii[i] * (1 + (rng.uniform(-jit, jit) if rng else 0.0))
            ring.append(p + (x * math.cos(ang) + y * math.sin(ang)) * rr)
        rings.append(ring)
    for i in range(n - 1):
        ci = (pts[i] + pts[i + 1]) / 2
        for k in range(sides):
            k2 = (k + 1) % sides
            q = [rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]]
            mb.poly(q, mat, (q[0] + q[1] + q[2] + q[3]) / 4 - ci, col=col)
    if cap:
        mb.poly(rings[-1], cap[0] if isinstance(cap, tuple) else mat, pts[-1] - pts[-2],
                col=cap[1] if isinstance(cap, tuple) else col)
    return rings


def disc(mb, c, n, r, seg, mat, col=None, phase=0.0):
    c = Vector(c)
    w, u, v = _frame(n)
    mb.poly([c + (u * math.cos(phase + TAU * k / seg) + v * math.sin(phase + TAU * k / seg)) * r
             for k in range(seg)], mat, w, col=col)


def rect(mb, c, right, up, w, h, mat, col=None):
    """Flat quad centred at c, facing right x up."""
    c, r, u = Vector(c), Vector(right).normalized() * w / 2, Vector(up).normalized() * h / 2
    mb.poly([c - r - u, c + r - u, c + r + u, c - r + u], mat, r.cross(u), col=col)


def R(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def C(cx, cy, r, seg, phase=0.0):
    return [(cx + r * math.cos(phase + TAU * k / seg), cy + r * math.sin(phase + TAU * k / seg)) for k in range(seg)]


def mosaic(mb, o, right, up, node):
    """Flat panel in the plane o + right*x + up*y built from nested 2D rings that never overlap (no
    coplanar z-fighting): node = (ring, mat, col, [child nodes]); every child is cut out of its parent
    as a hole and filled by its own face (mat None: hole left open). Faces point along right x up."""
    o, r, u = Vector(o), Vector(right).normalized(), Vector(up).normalized()
    n = r.cross(u)

    def emit(nd):
        ring, mat, col = nd[0], nd[1], nd[2]
        if mat is None:                             # pure hole: cut out, left open
            return
        kids = nd[3] if len(nd) > 3 else []
        if kids:
            flat, tris = tess2d([ring] + [k[0] for k in kids])
            mb.tris([o + r * p[0] + u * p[1] for p in flat], tris, mat, n, col=col)
        else:
            mb.poly([o + r * p[0] + u * p[1] for p in ring], mat, n, col=col)
        for k in kids:
            emit(k)
    emit(node)


def frustum(mb, c, z0, z1, h0, h1, mat, col=None, top=True, bottom=False):
    """Axis-aligned rectangular frustum: half sizes h0=(hx, hy) at z0, h1 at z1."""
    cx, cy = c
    lo = [Vector((cx + sx * h0[0], cy + sy * h0[1], z0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    hi = [Vector((cx + sx * h1[0], cy + sy * h1[1], z1)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    mid = Vector((cx, cy, (z0 + z1) / 2))
    for k in range(4):
        q = [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]]
        n = (q[0] + q[1]) / 2 - Vector((cx, cy, q[0].z))
        mb.poly(q, mat, n if n.length > 1e-6 else (q[0] + q[2]) / 2 - mid, col=col)
    if top:
        mb.poly(hi, mat, UP, col=col)
    if bottom:
        mb.poly(lo, mat, -UP, col=col)


def torus(mb, c, axis, R, r, seg, sides, mat, col=None):
    c = Vector(c)
    w, u, v = _frame(axis)
    rings = []
    for i in range(seg):
        a = TAU * i / seg
        rad = u * math.cos(a) + v * math.sin(a)
        rings.append([c + rad * (R + r * math.cos(TAU * k / sides)) + w * (r * math.sin(TAU * k / sides))
                      for k in range(sides)])
    for i in range(seg):
        i2 = (i + 1) % seg
        am = TAU * (i + 0.5) / seg
        core = c + (u * math.cos(am) + v * math.sin(am)) * R
        for k in range(sides):
            k2 = (k + 1) % sides
            q = [rings[i][k], rings[i2][k], rings[i2][k2], rings[i][k2]]
            mb.poly(q, mat, (q[0] + q[1] + q[2] + q[3]) / 4 - core, col=col)


_ICO_V = None
_ICO_F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2),
          (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11),
          (6, 2, 10), (8, 6, 7), (9, 8, 1)]


def blob(mb, c, size, mat, col, rng, jit=0.25, sink=0.0):
    """Lumpy icosahedron (20 tris) of the given extents, resting on z = c.z (crumpled paper, bags)."""
    t = (1 + 5 ** 0.5) / 2
    base = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
            (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    pts = []
    for p in base:
        p = Vector(p).normalized() * (1 + rng.uniform(-jit, jit))
        pts.append(Vector((p.x * size[0] / 2, p.y * size[1] / 2, p.z * size[2] / 2)))
    zmin = min(p.z for p in pts)
    c = Vector(c)
    pts = [c + p - Vector((0, 0, zmin + sink)) for p in pts]
    ctr = sum(pts, Vector()) / len(pts)
    for f in _ICO_F:
        tri = [pts[i] for i in f]
        mb.poly(tri, mat, (tri[0] + tri[1] + tri[2]) / 3 - ctr, col=col)


def clump(mb, c, d, uv, col=None, n=3, rot=0.0, horiz=True, rng=None, tilt=0.25, hs=1.0):
    """Foliage clump: n crossed vertical cards (+ one horizontal) of size d centred at c."""
    c = Vector(c)
    for i in range(n):
        a = rot + math.pi * i / n
        r = Vector((math.cos(a), math.sin(a), 0))
        tau = rng.uniform(-tilt, tilt) if rng else 0.0
        up = Vector((-math.sin(a) * math.sin(tau), math.cos(a) * math.sin(tau), math.cos(tau)))
        card(mb, c - up * (d * hs / 2), r, up, d, d * hs, "cut", uv, col=col)
    if horiz:                                       # a tilted cross card fills the clump seen from above/below
        a = rot + 0.4
        r = Vector((math.cos(a), math.sin(a), 0))
        tau = 0.45 + (rng.uniform(-0.15, 0.15) if rng else 0.0)
        fwd = Vector((-math.sin(a) * math.cos(tau), math.cos(a) * math.cos(tau), math.sin(tau)))
        card(mb, c - fwd * d * 0.45, r, fwd, d * 0.9, d * 0.9, "cut", uv, col=col)


def _recentre(mb):
    """Move the footprint centre to the origin (xy), keep z."""
    xs = [v.x for v in mb.verts]
    ys = [v.y for v in mb.verts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for v in mb.verts:
        v.x -= cx
        v.y -= cy


def tri_count(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


# ------------------------------------------------------------------ street furniture
def lamp_head(mb, c, z0, s=1.0, drop=False):
    """Classic four-sided Jerusalem lantern standing on z0: plate, flared glass, cornice, hipped roof, finial."""
    I = "iron"
    cx, cy = c
    obox(mb, (cx, cy, z0 + 0.02 * s), (0.26 * s, 0.26 * s, 0.04 * s), I)
    zb, zt = z0 + 0.04 * s, z0 + 0.46 * s
    rb, rt = 0.105 * s * 2 ** 0.5, 0.155 * s * 2 ** 0.5
    lathe(mb, [(rb, zb), (rt, zt)], "glass_lamp", seg=4, o=(cx, cy, 0), phase=math.pi / 4)
    for k in range(4):
        a = math.pi / 4 + math.pi / 2 * k
        ttube(mb, [(cx + math.cos(a) * rb, cy + math.sin(a) * rb, zb), (cx + math.cos(a) * rt, cy + math.sin(a) * rt, zt)],
              [0.014 * s] * 2, I, sides=4, phase=math.pi / 4)
    obox(mb, (cx, cy, zt + 0.025 * s), (0.37 * s, 0.37 * s, 0.05 * s), I)
    r2 = 2 ** 0.5
    lathe(mb, [(0.175 * s * r2, zt + 0.05 * s), (0.09 * s * r2, zt + 0.16 * s), (0.0, zt + 0.25 * s)], I, seg=4,
          o=(cx, cy, 0), phase=math.pi / 4)
    lathe(mb, [(0.022 * s, zt + 0.22 * s), (0.03 * s, zt + 0.28 * s), (0.0, zt + 0.36 * s)], I, seg=6, o=(cx, cy, 0))
    if drop:                                        # pendant finial under a hanging lantern
        lathe(mb, [(0.0, z0 - 0.09 * s), (0.04 * s, z0)], I, seg=6, o=(cx, cy, 0))
    return zt + 0.36 * s


def lamp_post(mb, ctx):
    I = "iron"
    obox(mb, (0, 0, 0.06), (0.36, 0.36, 0.12), I, skip=("-z",))          # square cast-iron plinth
    prof = [(0.15, 0.12), (0.15, 0.24), (0.105, 0.32), (0.095, 0.62), (0.065, 0.74), (0.078, 0.80),
            (0.055, 0.86), (0.045, 3.20), (0.07, 3.27), (0.07, 3.33), (0.12, 3.42)]
    lathe(mb, prof, I, seg=8, phase=math.pi / 8)
    beam(mb, (-0.3, 0, 3.08), (0.3, 0, 3.08), 0.03, 0.03, I)               # ladder rest bar
    lamp_head(mb, (0, 0), 3.42)


def wall_lantern(mb, ctx):
    I = "iron"
    obox(mb, (0, 0.015, -0.05), (0.12, 0.03, 0.34), I, skip=("-y",))        # wall plate
    ttube(mb, [(0, 0.02, 0.06), (0, 0.66, 0.06)], [0.017, 0.015], I, sides=4, cap=True, phase=math.pi / 4)
    ttube(mb, [(0, 0.02, -0.19), (0, 0.2, -0.07), (0, 0.44, 0.05)], [0.013] * 3, I, sides=4)   # brace
    sc = Vector((0, 0.15, -0.015))                                            # scroll between arm and brace
    ttube(mb, [sc + Vector((0, 0.06 * math.cos(a), 0.06 * math.sin(a))) * (1 - 0.15 * i)
               for i, a in enumerate([1.6, 3.0, 4.4, 5.8, 7.0])], [0.01] * 5, I, sides=3)
    ttube(mb, [(0, 0.62, 0.06), (0, 0.62, -0.03)], [0.01] * 2, I, sides=4)    # hanger
    s = 0.72
    lamp_head(mb, (0, 0.62), -0.03 - 0.36 * s - 0.46 * s, s=s, drop=True)


def bollard(mb, ctx):
    lathe(mb, [(0.10, 0.0), (0.085, 0.06), (0.085, 0.76), (0.074, 0.86), (0.0, 0.90)], "iron", seg=8,
          phase=math.pi / 8)


def bin_post(mb, ctx):
    G, D = "metal_green", "metal_dark"
    obox(mb, (0, -0.235, 0.53), (0.05, 0.05, 1.06), D, skip=("-z",))         # post behind the bin
    for z in (0.58, 0.86):                                                    # mounting straps
        beam(mb, (0, -0.25, z), (0, -0.16, z), 0.07, 0.03, D, cap0=False)
    lathe(mb, [(0.17, 0.45), (0.2, 0.95), (0.18, 0.95), (0.18, 0.82), (0.0, 0.82)], G, seg=10,
          bands=[(G, None), (G, None), (G, (0.55, 0.55, 0.55)), ("void", None)], cap0=(G, None))


def dumpster(mb, ctx):
    P = "plastic"
    g = (0.045, 0.15, 0.06)
    g2 = (0.04, 0.13, 0.055)
    frustum(mb, (0, 0), 0.24, 1.17, (0.6, 0.45), (0.67, 0.52), P, g, top=False, bottom=True)
    obox(mb, (0, 0, 1.18), (1.42, 1.12, 0.06), P, g)                          # top lip
    obox(mb, (0, 0.53, 1.02), (1.1, 0.06, 0.07), P, g2)                       # front comb bar
    arc = [(-0.57, 1.21), (-0.32, 1.29), (0.0, 1.32), (0.32, 1.29), (0.57, 1.21)]
    for i in range(4):
        (y0, z0), (y1, z1) = arc[i], arc[i + 1]
        q = [(-0.72, y0, z0), (0.72, y0, z0), (0.72, y1, z1), (-0.72, y1, z1)]
        mb.poly(q, P, (0, (y0 + y1) / 2, (z0 + z1) / 2 - 0.9), col=g2)
    for sx in (-1, 1):
        mb.poly([(sx * 0.72, y, z) for y, z in arc], P, (sx, 0, 0), col=g2)
    beam(mb, (-0.5, 0.6, 1.235), (0.5, 0.6, 1.235), 0.05, 0.035, P, g2)        # lid handle
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.5, sy * 0.36
            beam(mb, (x, y, 0.25), (x, y, 0.1), 0.085, 0.05, "metal_grey", caps=False)
            lathe(mb, [(0.1, -0.03), (0.1, 0.03)], P, (0.05, 0.05, 0.05), seg=6, o=(x, y, 0.1), axis=(1, 0, 0),
                  cap0=(P, (0.25, 0.25, 0.25)), cap1=(P, (0.25, 0.25, 0.25)), phase=math.pi / 6)


def bench(mb, ctx):
    I, W = "iron", "wood"
    wc = (0.95, 0.88, 0.82)
    for x in (-0.78, 0.78):
        beam(mb, (x, 0.22, 0.0), (x, 0.22, 0.637), 0.05, 0.05, I, caps=False)          # front leg
        ttube(mb, [(x, -0.2, 0.0), (x, -0.16, 0.44), (x, -0.27, 0.88)], [0.035] * 3, I, sides=4,
              cap=True, phase=math.pi / 4)                                              # rear leg + back
        beam(mb, (x, 0.195, 0.40), (x, -0.14, 0.40), 0.03, 0.05, I, caps=False)        # seat rail
        beam(mb, (x, 0.28, 0.655), (x, -0.2, 0.675), 0.07, 0.035, I)                   # armrest
    for i, y in enumerate((0.19, 0.085, -0.02, -0.125)):
        obox(mb, (0, y, 0.45), (1.8, 0.09, 0.03), W, tuple(c * (0.92 + 0.05 * (i % 2)) for c in wc))
    dv = Vector((0, -0.11, 0.44)).normalized()
    nv = Vector((0, dv.z, -dv.y))                   # backrest normal, facing front-up
    for t in (0.3, 0.58, 0.86):
        p = Vector((0, -0.16, 0.44)) + dv * (0.45 * t) + nv * 0.04
        obox(mb, p, (1.8, 0.03, 0.1), W, wc, ax=(1, 0, 0), ay=nv, az=dv)


def info_board(mb, ctx):
    D, P = "metal_dark", "plastic"
    for sx in (-1, 1):
        obox(mb, (sx * 0.69, 0, 1.08), (0.07, 0.07, 2.16), D, skip=("-z",))
    obox(mb, (0, 0, 1.45), (1.30, 0.06, 1.02), D, skip=("+y",))
    obox(mb, (0, 0, 2.18), (1.48, 0.16, 0.04), D)
    # front: frame / 1.2 x 0.9 face / header + title / map with blocks / legend lines, all one plane
    legend = [(R(0.27, 1.60 - 0.12 * k, 0.54 - 0.06 * (k % 2), 1.63 - 0.12 * k), P, (0.75, 0.75, 0.72))
              for k in range(4)]
    face = (R(-0.6, 1.0, 0.6, 1.9), P, (0.035, 0.035, 0.04), [
        (R(-0.56, 1.73, 0.56, 1.86), P, (0.30, 0.07, 0.10), [(R(-0.5, 1.775, 0.05, 1.815), P, (0.9, 0.88, 0.8))]),
        (R(-0.56, 1.05, 0.22, 1.69), P, (0.80, 0.75, 0.60), [
            (R(-0.40, 1.25, 0.02, 1.56), P, (0.66, 0.58, 0.44)),                 # Old City block
            (R(-0.10, 1.10, 0.18, 1.22), P, (0.30, 0.50, 0.25)),                 # park
            (R(-0.52, 1.40, -0.44, 1.44), P, (0.75, 0.10, 0.08))]),              # you-are-here
        *legend])
    mosaic(mb, (0, 0.03, 0), (-1, 0, 0), (0, 0, 1), (R(-0.65, 0.94, 0.65, 1.96), D, None, [face]))


# ------------------------------------------------------------------ trees and plants
def tree_olive(mb, ctx):
    rng = random.Random(41)
    uv = ctx["olive"]
    bc = (0.85, 0.85, 0.85)
    ttube(mb, [(0, 0, -0.05), (0.1, 0.02, 0.45), (-0.04, 0.12, 0.95), (0.06, 0.04, 1.35)],
          [0.33, 0.26, 0.25, 0.21], "bark", bc, sides=6, rng=rng, jit=0.22)
    limbs = [[(0.06, 0.04, 1.2), (0.6, 0.3, 1.9), (1.3, 0.55, 2.65)],
             [(0.0, 0.08, 1.2), (-0.65, 0.4, 2.0), (-1.25, 0.8, 2.7)],
             [(0.06, -0.02, 1.2), (0.2, -0.7, 2.05), (0.0, -1.3, 2.8)]]
    for L in limbs:
        ttube(mb, L, [0.16, 0.11, 0.06], "bark", bc, sides=5, rng=rng, jit=0.15)
    col = (0.97, 1.0, 1.0)
    for c, d in [((1.35, 0.55, 3.25), 2.2), ((-1.35, 0.85, 3.35), 2.3), ((0.05, -1.35, 3.45), 2.2),
                 ((0.2, 0.3, 4.0), 2.6), ((0.95, -0.65, 3.85), 1.9), ((-0.85, -0.55, 3.75), 2.0),
                 ((-0.2, 1.35, 3.65), 1.8)]:
        clump(mb, c, d, uv, col, rot=rng.uniform(0, math.pi), rng=rng)


def tree_ficus(mb, ctx):
    rng = random.Random(23)
    uv = ctx["ficus"]
    bc = (0.8, 0.9, 1.0)
    ttube(mb, [(0, 0, -0.05), (0, 0, 0.3), (0.04, 0, 1.2), (0.0, 0.04, 2.1)], [0.3, 0.22, 0.2, 0.18], "bark", bc,
          sides=6, rng=rng, jit=0.07)
    for k in range(3):
        a = TAU * k / 3 + 0.4
        ttube(mb, [(0, 0, 1.95), (math.cos(a) * 0.55, math.sin(a) * 0.55, 2.75), (math.cos(a) * 1.1, math.sin(a) * 1.1, 3.5)],
              [0.14, 0.1, 0.06], "bark", bc, sides=5, rng=rng, jit=0.06)
    col = (0.72, 0.8, 0.72)
    C = Vector((0, 0, 4.25))
    n = 12
    for i in range(n):                               # dense clipped dome: clumps on an ellipsoid shell
        zz = 0.92 - 1.55 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        a = i * 2.39996
        p = C + Vector((math.cos(a) * rr * 1.75, math.sin(a) * rr * 1.75, zz * 1.4))
        clump(mb, p, rng.uniform(2.3, 2.8), uv, col, rot=rng.uniform(0, math.pi), rng=rng)
    clump(mb, C + Vector((0.1, -0.1, 1.25)), 2.4, uv, col, rot=0.9, rng=rng)       # crown top


def weeds(mb, ctx):
    uv = ctx["weeds"]
    for i, (w, h) in enumerate([(0.46, 0.42), (0.40, 0.36), (0.36, 0.40)]):
        a = math.pi * i / 3 + 0.3
        card(mb, (0, 0, -0.02), (math.cos(a), math.sin(a), 0), UP, w, h, "cut", uv)


def caper(mb, ctx):
    uv = ctx["caper"]
    card(mb, (0, 0.05, -0.42), (-1, 0, 0), UP, 0.82, 0.68, "cut", uv)                   # flat against the wall
    for sx in (-1, 1):
        a = math.radians(38)
        r = Vector((-math.cos(a), sx * math.sin(a), 0))
        card(mb, (sx * 0.16, 0.2, -0.38), r if r.cross(UP).y > 0 else -r, UP, 0.6, 0.58, "cut", uv)
    out = Vector((0, 0.78, -0.62)).normalized()                                        # drooping skirt
    card(mb, (0, 0.03, -0.08), (1, 0, 0), out, 0.78, 0.5, "cut", uv)
    rise = Vector((0, 0.55, 0.83)).normalized()                                        # upward sprig
    card(mb, (0.05, 0.03, 0.0), (1, 0, 0), rise, 0.6, 0.42, "cut", uv)


def plant_pot(mb, ctx):
    T = "roof_tiles"
    lathe(mb, [(0.12, 0.0), (0.17, 0.28), (0.195, 0.29), (0.195, 0.34), (0.17, 0.34), (0.0, 0.32)], T, seg=8,
          bands=[(T, (1.0, 0.85, 0.75)), (T, (1.0, 0.9, 0.8)), (T, (1.0, 0.9, 0.8)), (T, (1.0, 0.9, 0.8)),
                 ("bark", (0.55, 0.45, 0.4))])
    uv = ctx["caper"]
    for i in range(3):
        a = math.pi * i / 3 + 0.2
        card(mb, (0, 0, 0.27), (math.cos(a), math.sin(a), 0), UP, 0.55, 0.5, "cut", uv)
    card(mb, (0, -0.25, 0.42), (1, 0, 0), (0, 1, 0), 0.5, 0.5, "cut", uv)


# ------------------------------------------------------------------ shop clutter
def cart(mb, ctx):
    W, M, P = "wood", "metal_dark", "plastic"
    for i, x in enumerate((-0.265, 0.0, 0.265)):
        obox(mb, (x, 0, 0.52), (0.26, 1.6, 0.04), W, ((0.95, 0.9, 0.85), (0.82, 0.76, 0.7), (1.0, 0.95, 0.88))[i])
    for sx in (-1, 1):
        obox(mb, (sx * 0.385, 0, 0.6), (0.03, 1.6, 0.12), W, (0.75, 0.7, 0.65), skip=("-z",))
    for sx in (-1, 1):
        x = sx * 0.3
        ttube(mb, [(x, 0.78, 0.475), (x, -0.8, 0.475), (x, -1.15, 0.8)], [0.03] * 3, M, sides=4, cap=True,
              phase=math.pi / 4)                                                        # frame rail + handle
        beam(mb, (x, 0.7, 0.0), (x, 0.7, 0.453), 0.04, 0.04, M, caps=False)             # front stand
        beam(mb, (x, 0.0, 0.24), (x, 0.0, 0.453), 0.05, 0.06, M, caps=False)            # axle hanger
    beam(mb, (-0.47, 0, 0.24), (0.47, 0, 0.24), 0.04, 0.04, M, caps=False)              # axle
    for sx in (-1, 1):
        x = sx * 0.43
        tyre, hub = (0.035, 0.035, 0.035), (0.45, 0.45, 0.45)
        lathe(mb, [(0.24, -0.055), (0.24, 0.055)], P, tyre, seg=8, o=(x, 0, 0.24), axis=(1, 0, 0),
              cap0=(P, tyre), cap1=(P, tyre), phase=math.pi / 8)
        lathe(mb, [(0.12, 0.0), (0.0, 0.035)], "metal_grey", hub, seg=6, o=(x + sx * 0.055, 0, 0.24),
              axis=(sx, 0, 0))                                                      # hub cone
    ax = Vector((0, 1, 0.35)).normalized()                                              # brake tyre at the back
    torus(mb, (0, -0.9, 0.27), ax, 0.2, 0.07, 8, 3, P, (0.035, 0.035, 0.035))
    _recentre(mb)


def _carton(mb, c, size, yaw, col, top=True):
    ax = Vector((math.cos(yaw), math.sin(yaw), 0))
    ay = Vector((-math.sin(yaw), math.cos(yaw), 0))
    c = Vector(c)
    hx, hy, h = size[0] / 2, size[1] / 2, size[2]
    obox(mb, (c.x, c.y, c.z + h / 2), size, "cardboard", col, ax, ay, skip=("-z", "+z", "+x", "-x"))
    edges = [-hy, -0.0275, 0.0275, hy]               # top split into flap / packing tape / flap
    for sx in (-1, 1):                               # end faces include the split points of the top edge
        pts = [c + ax * sx * hx + ay * e + UP * (h if k else 0.0) for k, e in
               [(0, -hy), (0, hy)] + [(1, e) for e in edges[::-1]]]
        mb.poly(pts, "cardboard", ax * sx, col=col)
    tape = tuple(min(1.0, k * 1.18) for k in col)
    for i in range(3):
        mb.poly([c + ax * (sx * hx) + ay * edges[i + j] + UP * h for sx, j in ((-1, 0), (1, 0), (1, 1), (-1, 1))],
                "cardboard", UP, col=tape if i == 1 and top else col)


def box_stack(mb, ctx):
    _carton(mb, (0, 0, 0), (0.56, 0.40, 0.38), 0.0, (0.85, 0.82, 0.78))
    _carton(mb, (0.02, -0.01, 0.38), (0.50, 0.38, 0.33), 0.1, (0.78, 0.72, 0.62))
    _carton(mb, (-0.03, 0.01, 0.71), (0.40, 0.32, 0.27), -0.14, (0.84, 0.8, 0.74))
    _carton(mb, (0.5, 0.06, 0), (0.36, 0.30, 0.30), 0.3, (0.72, 0.66, 0.56))
    _recentre(mb)


def _crate(mb, c, yaw, col, top=True, size=(0.6, 0.4, 0.27)):
    P = "plastic"
    sx, sy, sz = size
    t = 0.022
    ax = Vector((math.cos(yaw), math.sin(yaw), 0))
    ay = Vector((-math.sin(yaw), math.cos(yaw), 0))
    c = Vector(c)
    dark = tuple(k * 0.3 for k in col)
    for n, half, w, hole in ((ay, sy / 2, sx, R(-0.18, sz * 0.5 - 0.035, 0.18, sz * 0.5 + 0.035)),      # vent slot
                             (ax, sx / 2, sy, R(-0.065, sz - 0.085, 0.065, sz - 0.045))):              # hand hole
        for s_ in (1, -1):
            nn = n * s_
            mosaic(mb, c + nn * half, UP.cross(nn), UP, (R(-w / 2, 0, w / 2, sz), P, col, [(hole, P, dark)]))
    if top:
        obox(mb, c + UP * (sz / 2 + 0.015), (sx - 2 * t, sy - 2 * t, sz - 0.03), P, tuple(k * 0.8 for k in col),
             ax, ay, skip=("-z", "+z"), inward=True)
        rect(mb, c + UP * 0.03, ax, ay, sx - 2 * t, sy - 2 * t, P, tuple(k * 0.6 for k in col))
        o = [c + ax * (i * sx / 2) + ay * (j * sy / 2) + UP * sz for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        n = [c + ax * (i * (sx / 2 - t)) + ay * (j * (sy / 2 - t)) + UP * sz for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for k in range(4):
            mb.poly([o[k], o[(k + 1) % 4], n[(k + 1) % 4], n[k]], P, UP, col=col)


CRATE_COLS = {"red": (0.55, 0.04, 0.03), "blue": (0.04, 0.13, 0.45), "green": (0.06, 0.32, 0.08),
              "yellow": (0.85, 0.55, 0.03), "black": (0.05, 0.05, 0.05)}


def crate_stack(mb, ctx):
    C = CRATE_COLS
    _crate(mb, (0, 0, 0), 0.0, C["blue"], top=False)
    _crate(mb, (0.01, 0.005, 0.27), 0.03, C["red"], top=False)
    _crate(mb, (-0.01, 0.0, 0.54), -0.04, C["green"], top=True)
    _crate(mb, (0.58, 0.12, 0), 0.25, C["yellow"], top=True)
    _recentre(mb)


def crate_single(mb, ctx):
    _crate(mb, (0, 0, 0), 0.0, CRATE_COLS["blue"], top=True)


def stool_stack(mb, ctx):
    P = "plastic"
    col = (0.6, 0.04, 0.03)
    n, z0, dz = 5, 0.40, 0.05
    ztop = z0 + (n - 1) * dz
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam(mb, (sx * 0.19, sy * 0.19, 0), (sx * 0.135, sy * 0.135, ztop), 0.04, 0.04, P,
                 tuple(k * 0.9 for k in col), caps=False)
    for i in range(n):
        z = z0 + i * dz
        frustum(mb, (0, 0), z, z + 0.03, (0.155, 0.155), (0.165, 0.165), P, col, top=True, bottom=(i == 0))


# ------------------------------------------------------------------ litter
def bottle(mb, ctx):
    r = 0.034
    body = (0.72, 0.84, 0.95)
    lathe(mb, [(r, 0.0), (r, 0.16), (0.013, 0.215)], "plastic", body, seg=5, o=(-0.11, 0, r * math.cos(math.pi / 5)),
          axis=(1, 0, 0), cap0=("plastic", body), cap1=("plastic", (0.05, 0.2, 0.75)), phase=math.pi + math.pi / 5)


def can(mb, ctx):
    r = 0.033
    lathe(mb, [(r, 0.0), (r, 0.115)], "plastic", (0.62, 0.03, 0.03), seg=8,
          o=(-0.058, 0, r * math.cos(math.pi / 8) * 0.88), axis=(1, 0, 0),
          cap0=("metal_grey", None), cap1=("metal_grey", None),
          phase=math.pi + math.pi / 8, ell=(0.88, 1.0))


def cup(mb, ctx):
    r0, r1, L = 0.027, 0.04, 0.095
    al = math.atan2(r1 - r0, L)
    ax = Vector((math.cos(al), 0, math.sin(al)))
    o = Vector((-0.045, 0, r0 * math.cos(math.pi / 6)))
    lathe(mb, [(r0, 0.0), (r1, L)], "plastic", (0.95, 0.94, 0.9), seg=6, o=o, axis=ax,
          cap0=("plastic", (0.95, 0.94, 0.9)), phase=math.pi + math.pi / 6)
    disc(mb, o + ax * (L - 0.006), ax, r1 * 0.93, 6, "plastic", (0.42, 0.34, 0.27), phase=math.pi + math.pi / 6)


def paper(mb, ctx):
    blob(mb, (0, 0, 0), (0.09, 0.08, 0.065), "plastic", (0.92, 0.91, 0.86), random.Random(5), jit=0.32, sink=0.002)


def bag(mb, ctx):
    rng = random.Random(9)
    col = (0.9, 0.92, 0.95)
    blob(mb, (0, 0, 0), (0.32, 0.24, 0.09), "plastic", col, rng, jit=0.35, sink=0.006)
    for sx in (-1, 1):                              # handle loops
        mb.poly([(sx * 0.14, -0.05, 0.03), (sx * 0.14, 0.05, 0.03), (sx * 0.24, 0.0, 0.012)], "plastic", UP, col=col)
        mb.poly([(sx * 0.14, -0.05, 0.026), (sx * 0.24, 0.0, 0.008), (sx * 0.14, 0.05, 0.026)], "plastic", -UP, col=col)


def pack(mb, ctx):
    yaw = 0.3
    ax, ay = Vector((math.cos(yaw), math.sin(yaw), 0)), Vector((-math.sin(yaw), math.cos(yaw), 0))
    obox(mb, (0, 0, 0.011), (0.088, 0.055, 0.022), "plastic", (0.1, 0.075, 0.035), ax, ay, skip=("-z", "+z"))
    mosaic(mb, (0, 0, 0.022), ax, ay, (R(-0.044, -0.0275, 0.044, 0.0275), "plastic", (0.1, 0.075, 0.035),
                                       [(R(-0.013, -0.024, 0.037, 0.024), "plastic", (0.85, 0.85, 0.8))]))


def flat_box(mb, ctx):
    """Flattened carton lying slightly warped (tilted ~2.5 deg, 7-25 mm off the ground: never coplanar with it)."""
    Cb = "cardboard"
    col = (0.92, 0.86, 0.76)
    up = Vector((0, 0.42, 0.018)).normalized()
    o = Vector((-0.135, 0, 0.016))

    def za(y):
        return o.z + y * 0.018 / 0.42
    mosaic(mb, o, (1, 0, 0), up, (R(-0.175, -0.21, 0.175, 0.21), Cb, col, [
        (R(-0.165, -0.025, 0.165, 0.025), Cb, (1.0, 0.95, 0.85)),                  # packing tape
        (R(-0.115, 0.09, -0.015, 0.15), Cb, (0.25, 0.2, 0.15))]))                  # printed mark
    b = [(0.04, -0.21, za(-0.21)), (0.31, -0.2, 0.045), (0.31, 0.22, 0.05), (0.04, 0.21, za(0.21))]
    mb.poly(b, Cb, UP, col=tuple(k * 0.92 for k in col))                           # second panel, curling up
    mb.poly(b, Cb, -UP, col=tuple(k * 0.5 for k in col))
    for p0, p1, n in (((-0.31, -0.21), (-0.31, 0.21), (-1, 0, 0)), ((-0.31, 0.21), (0.04, 0.21), (0, 1, 0)),
                      ((-0.31, -0.21), (0.04, -0.21), (0, -1, 0))):              # edge skirts down to the ground
        mb.poly([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], za(p1[1])), (p0[0], p0[1], za(p0[1]))],
                Cb, n, col=tuple(k * 0.8 for k in col))


def butt_cluster(mb, ctx):
    rng = random.Random(3)
    r = 0.0045
    for i in range(4):
        a = rng.uniform(0, TAU)
        p = Vector((math.cos(i * 1.7) * 0.05, math.sin(i * 1.7) * 0.05, r / 2))
        d = Vector((math.cos(a), math.sin(a), 0)) * 0.03
        col = (1.0, 0.62, 0.3) if i % 2 == 0 else (0.95, 0.94, 0.9)
        ttube(mb, [p - d / 2, p + d / 2], [r, r], "plastic", col, sides=3, cap=("plastic", (0.18, 0.17, 0.16)),
              phase=math.pi / 6)


# ------------------------------------------------------------------ roof props
def water_heater(mb, ctx):
    G, P = "metal_grey", "plastic"
    white = (1.0, 1.0, 0.98)
    t = math.radians(40)
    ay = Vector((0, -math.cos(t), math.sin(t)))
    az = Vector((0, math.sin(t), math.cos(t)))
    lo = Vector((0, 0.75, 0.06))                                    # bottom edge of the collector
    obox(mb, lo + ay * 1.0 + az * 0.04, (1.1, 2.0, 0.07), G, ax=(1, 0, 0), ay=ay, az=az,
         over={"+z": ("solar", None)})
    for sx in (-1, 1):
        x = sx * 0.5
        beam(mb, (x, 0.85, 0.02), (x, -1.15, 0.02), 0.04, 0.04, G, caps=False)                 # floor runner
        beam(mb, lo + Vector((sx * 0.47, 0, -0.04)), lo + ay * 2.26 + Vector((sx * 0.47, 0, -0.03)), 0.04, 0.04, G,
             caps=False)
        beam(mb, (sx * 0.56, -0.98, 0.0), (sx * 0.56, -0.98, 1.5), 0.045, 0.045, G, caps=False)  # rear leg
        beam(mb, (sx * 0.56, -0.72, 1.5), (sx * 0.56, -1.22, 1.5), 0.065, 0.04, G, caps=False)   # tank saddle
    lathe(mb, [(0.27, -0.72), (0.27, 0.72)], P, white, seg=7, o=(0, -0.98, 1.79), axis=(1, 0, 0),
          cap0=(P, (0.9, 0.9, 0.88)), cap1=(P, (0.9, 0.9, 0.88)))
    _recentre(mb)


def water_tank(mb, ctx):
    P = "plastic"
    blk = (0.07, 0.07, 0.07)
    lathe(mb, [(0.55, 0.0), (0.55, 1.0), (0.2, 1.15), (0.2, 1.21)], P, blk, seg=7, cap1=(P, (0.05, 0.05, 0.05)),
          bands=[(P, blk), (P, (0.08, 0.08, 0.08)), (P, (0.05, 0.05, 0.05))])


def sat_dish(mb, ctx):
    G, P = "metal_grey", "plastic"
    wc = (0.92, 0.92, 0.9)
    obox(mb, (0, 0, 0.02), (0.45, 0.45, 0.04), G, skip=("-z",))
    ttube(mb, [(0, -0.03, 0.04), (0, -0.03, 1.03)], [0.025] * 2, G, sides=4, cap=True, phase=math.pi / 4)
    t = math.radians(25)
    a = Vector((0, math.cos(t), math.sin(t)))
    dn = Vector((0, math.sin(t), -math.cos(t)))
    c = Vector((0, 0.04, 1.06))
    lathe(mb, [(0.4, 0.075), (0.22, 0.022), (0.0, 0.0)], P, wc, seg=7, o=c, axis=a)
    lathe(mb, [(0.0, -0.05), (0.4, 0.075)], P, (0.8, 0.8, 0.78), seg=7, o=c, axis=a)
    f = c + a * 0.46 + dn * 0.1
    ttube(mb, [c + a * 0.07 + dn * 0.38, f], [0.012] * 2, G, sides=3)
    obox(mb, f + a * 0.03, (0.05, 0.12, 0.05), P, (0.3, 0.3, 0.3), ax=(1, 0, 0), ay=a, az=a.cross(Vector((1, 0, 0))))


def antenna(mb, ctx):
    G = "metal_grey"
    for k in range(3):
        a = TAU * k / 3
        ttube(mb, [(0, 0, 0.5), (math.cos(a) * 0.42, math.sin(a) * 0.42, 0.0)], [0.012] * 2, G, sides=3)
    ttube(mb, [(0, 0, 0.0), (0, 0, 3.0)], [0.024, 0.02], G, sides=4)
    zb = 2.88
    ttube(mb, [(0, -0.5, zb), (0, 0.72, zb)], [0.012] * 2, G, sides=3)
    for y, hl in [(-0.46, 0.34), (-0.2, 0.29), (0.06, 0.24), (0.3, 0.21), (0.5, 0.19), (0.68, 0.17)]:
        ttube(mb, [(-hl, y, zb), (hl, y, zb)], [0.0065] * 2, G, sides=3)


# ------------------------------------------------------------------ wall props
def ac_unit(mb, ctx):
    P, G = "plastic", "metal_grey"
    body = (0.93, 0.91, 0.84)
    obox(mb, (0, 0.2, 0.275), (0.8, 0.3, 0.55), P, body, skip=("-y", "+y"))
    # front casing with the fan opening cut out (no overlay faces), protruding fan hub
    mosaic(mb, (0, 0.35, 0), (-1, 0, 0), (0, 0, 1),
           (R(-0.4, 0.0, 0.4, 0.55), P, body, [(C(-0.1, 0.28, 0.215, 10), "metal_dark", None)]))
    lathe(mb, [(0.05, 0.0), (0.0, 0.03)], P, (0.55, 0.55, 0.53), seg=5, o=(0.1, 0.35, 0.28), axis=(0, 1, 0))
    for sx in (-0.28, 0.28):                        # L brackets
        ttube(mb, [(sx, 0.0, -0.02), (sx, 0.37, -0.02)], [0.018] * 2, G, sides=3)
        ttube(mb, [(sx, 0.0, -0.33), (sx, 0.3, -0.035)], [0.015] * 2, G, sides=3, phase=math.pi / 2)


def spout(mb, ctx):
    rust = (0.62, 0.34, 0.2)
    pts = [Vector((0, -0.02, 0)), Vector((0, 0.16, -0.006)), Vector((0, 0.30, -0.045))]
    ttube(mb, pts, [0.036, 0.035, 0.034], "metal_grey", rust, sides=4, cap=("void", None))   # ~18 tris: thousands
    #                                                                                      of these per sector


# ------------------------------------------------------------------ present-day plaza furniture (photo-matched)
def backface(mb, start, gap=0.004):
    """Back copies (reversed winding, `gap` behind) of the faces added since index `start`: two-sided flags.
    The gap keeps them from being welded / validated away as duplicate faces."""
    for i in range(start, len(mb.faces)):
        pts = [mb.verts[j].copy() for j in mb.faces[i]]
        n = geometry.normal(pts)
        mb.poly([p - n * gap for p in pts][::-1], mb.mat_names[mb.mats[i]], None, uv=mb.uvs[i][::-1],
                col=mb.cols[i])


def _square_pole(mb, h, arms):
    """Dark-grey 0.16 m square pole on a base collar; arms = [(z, +1/-1 along Y)], each a short square arm
    ending in a flat LED head (glass underside). Matches the poles on Omar Ibn el-Khattab Square and at the gate."""
    D = "metal_dark"
    obox(mb, (0, 0, 0.15), (0.26, 0.26, 0.3), D, skip=("-z",))
    obox(mb, (0, 0, (0.3 + h) / 2), (0.16, 0.16, h - 0.3), D, skip=("-z",))
    for z, s_ in arms:
        L = 0.85
        beam(mb, (0, 0, z), (0, s_ * L, z), 0.1, 0.1, D, caps=False)
        obox(mb, (0, s_ * (L + 0.25), z), (0.28, 0.66, 0.14), D, over={"-z": ("glass_lamp", None)})


def lamp_modern(mb, ctx):
    _square_pole(mb, 8.0, [(7.91, 1)])


def lamp_modern_double(mb, ctx):
    _square_pole(mb, 9.0, [(8.91, 1), (6.4, -1)])


def lamp_disc(mb, ctx):
    """Plaza lamp outside the gate: slim round grey pole with a flat disc ("mushroom") luminaire, ~4.5 m."""
    G = "metal_grey"
    gc = (0.75, 0.75, 0.78)
    lathe(mb, [(0.11, 0.0), (0.11, 0.35), (0.065, 0.42), (0.055, 4.3)], G, gc, seg=8)
    lathe(mb, [(0.0, 4.22), (0.27, 4.30), (0.3, 4.34), (0.26, 4.40), (0.08, 4.46), (0.0, 4.47)], G, gc, seg=12,
          bands=[("glass_lamp", None), (G, gc), (G, gc), (G, gc), (G, gc)])


def bin_slatted(mb, ctx):
    """Municipal litter bin: dark-grey vertical slats round a dark liner, top rim and base ring, ~0.95 m."""
    G, D = "metal_grey", "metal_dark"
    gc = (0.62, 0.62, 0.64)
    lathe(mb, [(0.235, 0.05), (0.235, 0.86)], D, seg=12)                                   # liner
    n = 12
    for k in range(n):
        a = TAU * (k + 0.5) / n
        d = Vector((math.cos(a), math.sin(a), 0))
        t = Vector((-math.sin(a), math.cos(a), 0))
        obox(mb, d * 0.248 + UP * 0.46, (0.075, 0.03, 0.8), G, gc, ax=t, ay=d, skip=("-y", "-z", "+z"))
    lathe(mb, [(0.285, 0.86), (0.285, 0.92), (0.225, 0.92), (0.225, 0.75), (0.0, 0.75)], G, gc, seg=12,
          bands=[(G, gc), (G, gc), (D, None), ("void", None)])                              # rim, bag
    lathe(mb, [(0.285, 0.0), (0.285, 0.06), (0.235, 0.06)], G, gc, seg=12)                  # base ring


def bench_stone(mb, ctx):
    """Plaza bench: thick pale stone slab on two dark steel legs."""
    obox(mb, (0, 0, 0.4), (1.7, 0.45, 0.12), "lime", (1.0, 0.98, 0.93))
    for sx in (-1, 1):
        obox(mb, (sx * 0.55, 0, 0.17), (0.07, 0.36, 0.34), "metal_dark", skip=("-z", "+z"))


def barrier_post(mb, ctx):
    """Pale stone bollard block with a chamfered top, as set along the road edge at the gate."""
    col = (1.0, 0.98, 0.93)
    frustum(mb, (0, 0), 0.0, 0.48, (0.18, 0.18), (0.18, 0.18), "lime", col, top=False)
    frustum(mb, (0, 0), 0.48, 0.55, (0.18, 0.18), (0.13, 0.13), "lime", col, top=True)


def banner_pole(mb, ctx):
    """Grey square post (4.8 m) carrying a red vertical Tower of David museum banner on two arms (+X side)."""
    G, P = "metal_grey", "plastic"
    gc = (0.6, 0.6, 0.62)
    red = (0.55, 0.05, 0.04)
    obox(mb, (0, 0, 2.4), (0.12, 0.12, 4.8), G, gc, skip=("-z",))
    for z in (1.75, 4.25):
        beam(mb, (0, 0, z), (0.76, 0, z), 0.03, 0.03, G, gc, cap0=False)
    # banner x 0.1..0.7, z 1.8..4.2; front (+Y) with a pale text column and logo, plain back
    mosaic(mb, (0, 0, 0), (-1, 0, 0), (0, 0, 1), (R(-0.7, 1.8, -0.1, 4.2), P, red, [
        (R(-0.47, 2.45, -0.33, 3.95), P, (0.9, 0.85, 0.8)),
        (C(-0.4, 2.12, 0.1, 8), P, (0.95, 0.95, 0.95))]))
    mb.poly([(0.1, -0.004, 1.8), (0.7, -0.004, 1.8), (0.7, -0.004, 4.2), (0.1, -0.004, 4.2)], P, (0, -1, 0), col=red)


def flagpole(mb, ctx):
    """White flagpole (8 m) with an Israeli flag (white, two blue stripes, blue star outline), two-sided."""
    P = "plastic"
    wc, bl = (0.95, 0.95, 0.95), (0.03, 0.12, 0.5)
    lathe(mb, [(0.05, 0.0), (0.035, 8.0)], P, (0.9, 0.9, 0.9), seg=6, cap1=(P, (0.9, 0.9, 0.9)))
    lathe(mb, [(0.0, 7.98), (0.05, 8.04), (0.0, 8.1)], "metal_grey", (1.0, 0.85, 0.5), seg=6)   # finial
    start = len(mb.faces)
    z0, H = 6.85, 1.0
    bands = [(0.0, 0.1, wc), (0.1, 0.25, bl), (0.25, 0.75, wc), (0.75, 0.9, bl), (0.9, 1.0, wc)]
    x0, xf, x1 = 0.04, 1.06, 1.44                      # panel 1 flat, panel 2 kinked (the flag waves)
    yk = 0.2
    for v0, v1, col in bands:
        za, zb = z0 + v0 * H, z0 + v1 * H
        mb.poly([(xf, 0, za), (x1, yk, za - 0.03), (x1, yk, zb - 0.03), (xf, 0, zb)], P, (-0.2, 1, 0), col=col)
        if v0 != 0.25:                                 # panel 1 middle band: mosaic with the star below
            mb.poly([(x0, 0, za), (xf, 0, za), (xf, 0, zb), (x0, 0, zb)], P, (0, 1, 0), col=col)
    cx, cz = 0.55, z0 + 0.5 * H                        # middle band of panel 1 carries the star
    mosaic(mb, (0, 0, 0), (-1, 0, 0), (0, 0, 1), (R(-xf, z0 + 0.25 * H, -x0, z0 + 0.75 * H), P, wc, [
        (C(-cx, cz, 0.17, 6, math.pi / 2), P, bl, [(C(-cx, cz, 0.12, 6, math.pi / 2), P, wc)])]))
    backface(mb, start)


def palm(mb, ctx):
    """Small fan palm as in the Citadel moat: slender trunk, crown of fan leaves (weeds cut-out cards)."""
    rng = random.Random(17)
    uv = ctx["weeds"]
    bc = (0.72, 0.66, 0.6)
    top = Vector((0.1, 0.03, 2.75))
    ttube(mb, [(0, 0, -0.05), (0.03, 0, 0.9), (0.07, 0.02, 1.9), (0.1, 0.03, 2.55), top + Vector((0, 0, 0.12))],
          [0.17, 0.145, 0.135, 0.17, 0.11], "bark", bc, sides=6, rng=rng, jit=0.06)
    n = 17
    for i in range(n):
        az = i * 2.39996 + rng.uniform(-0.2, 0.2)
        el = math.radians(78 - 98 * i / (n - 1))       # young leaves upright, old ones drooping
        d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        p0 = top + Vector((0, 0, 0.05))
        p1 = p0 + d * 0.6
        ttube(mb, [p0, p1], [0.025, 0.015], "bark", (0.55, 0.65, 0.4), sides=3)
        up = (d + Vector((0, 0, -0.3 * (1 - math.sin(el))))).normalized()
        r = Vector((-math.sin(az), math.cos(az), 0))
        card(mb, p1 - up * 0.06, r, up, 1.25, 1.0, "cut", uv, col=(0.42, 0.56, 0.38))


def tree_young(mb, ctx):
    """Young plaza tree in a square stone-edged tree pit (the rows outside the gate)."""
    rng = random.Random(29)
    uv = ctx["olive"]
    bc = (0.8, 0.8, 0.82)
    ttube(mb, [(0, 0, 0.0), (0.03, 0, 1.4), (0.0, 0.03, 2.3)], [0.07, 0.06, 0.05], "bark", bc, sides=5)
    for k in range(3):
        a = TAU * k / 3 + 0.5
        ttube(mb, [(0.0, 0.03, 2.1), (math.cos(a) * 0.45, math.sin(a) * 0.45, 2.9)], [0.035, 0.02], "bark", bc, sides=4)
    col = (0.78, 1.0, 0.62)
    for c, d in [((0.35, 0.2, 3.1), 1.4), ((-0.35, 0.25, 3.25), 1.3), ((0.0, -0.4, 3.2), 1.35), ((0.05, 0.05, 3.7), 1.5)]:
        clump(mb, c, d, uv, col, rot=rng.uniform(0, math.pi), rng=rng)
    # tree pit: stone kerb frame proud of the paving, dark soil inside (never coplanar with the ground)
    K, ko, ki, zt, zs = "lime", 0.6, 0.48, 0.035, 0.015
    mosaic(mb, (0, 0, zt), (1, 0, 0), (0, 1, 0), (R(-ko, -ko, ko, ko), K, None, [(R(-ki, -ki, ki, ki), None, None)]))
    mb.poly([(-ki, -ki, zs), (ki, -ki, zs), (ki, ki, zs), (-ki, ki, zs)], "bark", UP, col=(0.45, 0.38, 0.32))
    frustum(mb, (0, 0), 0.0, zt, (ko, ko), (ko, ko), K, top=False)
    for sx, sy, n in ((1, 0, (-1, 0, 0)), (-1, 0, (1, 0, 0)), (0, 1, (0, -1, 0)), (0, -1, (0, 1, 0))):
        if sx:
            q = [(sx * ki, -ki, zs), (sx * ki, ki, zs), (sx * ki, ki, zt), (sx * ki, -ki, zt)]
        else:
            q = [(-ki, sy * ki, zs), (ki, sy * ki, zs), (ki, sy * ki, zt), (-ki, sy * ki, zt)]
        mb.poly(q, K, n)


BUILDERS = {
    "lamp_post": lamp_post, "wall_lantern": wall_lantern, "bollard": bollard, "bin_post": bin_post,
    "dumpster": dumpster, "bench": bench, "info_board": info_board, "tree_olive": tree_olive,
    "tree_ficus": tree_ficus, "cart": cart, "box_stack": box_stack, "crate_stack": crate_stack,
    "crate_single": crate_single, "stool_stack": stool_stack, "plant_pot": plant_pot,
    "bottle": bottle, "can": can, "cup": cup, "paper": paper, "bag": bag, "pack": pack, "flat_box": flat_box,
    "butt_cluster": butt_cluster, "weeds": weeds, "caper": caper, "water_heater": water_heater,
    "water_tank": water_tank, "sat_dish": sat_dish, "antenna": antenna, "ac_unit": ac_unit, "spout": spout,
    "lamp_modern": lamp_modern, "lamp_modern_double": lamp_modern_double, "lamp_disc": lamp_disc,
    "bin_slatted": bin_slatted, "bench_stone": bench_stone, "barrier_post": barrier_post, "banner_pole": banner_pole,
    "flagpole": flagpole, "palm": palm, "tree_young": tree_young,
}


def build_library(mats, tiles, gen):
    """Build every prop mesh once; returns {type: bpy.types.Mesh} (mesh names 'prop_<type>')."""
    cut = gen["cutout"]
    ctx = {k: atlas_rect(cut["grid"], tuple(v)) for k, v in cut["cells"].items()}
    lib = {}
    for name, fn in BUILDERS.items():
        mb = MeshBuilder(tiles)
        fn(mb, ctx)
        lib[name] = mb.to_mesh("prop_" + name, mats)
    return lib
