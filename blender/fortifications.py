"""City wall, Jaffa Gate tower and the Citadel (Tower of David).

    build(mbs, spec, gen, place)
        mbs    {"jaffa_gate", "city_wall", "citadel"}: MeshBuilders filled in place
        spec   scene spec: "gatehouse", "city_walls" (centre lines, outside on the right, joined end to
               end), "citadel" (outer / mass / inner rings, moat edges, towers: Phasael box + minaret)
        gen    generated-atlas manifest (doors atlas for the gate leaves, cut-outs for railings/grilles)
        place  place(type, Vector pos, yaw_radians, nocol) instances library props (only a few dry
               tufts on merlon tops: wall vegetation comes from pipeline/dressing.py)

Reference: data/reference/gate.md, citadel_east.md; what was taken from them and the remaining
deviations: data/reference/fort_notes.md.

Every wall face is ONE planar polygon per edge whose top outline already carries the crenellation
(merlons are not boxes stacked on the wall), triangulated with holes by a constrained Delaunay
triangulation: no coplanar overlaps, no slivers, and arrow slits, windows and arches are real
holes with reveals and dark backs.  Corner merlons are single L-shaped tops shared by both edges,
so merlon rows never overlap at corners.

Frames: an Edge(a, b) of a CCW ring has u along a->b, z up and `off` along the outward normal
(right of a->b). Inner faces (parapet backs, the gate chamber, the courtyard) use negative offsets.
"""
import math
import random

from mathutils import Vector, geometry

import meshkit as mk

UP = Vector((0, 0, 1))
DRESSED = (1.0, 0.98, 0.94)        # mouldings, roundels, inscription (lighter dressed stone)
WEATHER = (0.93, 0.9, 0.85)        # rubble glacis
LEAF_COL = (0.86, 0.9, 0.84)       # weathered grey-green iron plating of the gate leaves (door_wood2 cell)
OAK_COL = (0.8, 0.78, 0.62)        # olive-brown studded wooden doors of the Citadel (door_wood cell)
RUSTIC = (0.9, 0.88, 0.84)         # rough bossed masonry of the Citadel NW tower ("rubble")
HONEY = (0.93, 0.8, 0.63)          # Herodian blocks of Phasael

# ------------------------------------------------------------------ dimensions (fort_notes.md)
GATE_PARAPET = 0.8                 # parapet thickness on the gate tower
GATE_SILL = 1.1                    # merlon height above the crenel sill (gate.md s9: 13.0 / 11.9)
GATE_WALK = 2.2                    # wall walk below the merlon top
CIT_SILL = 1.6                     # citadel merlons ~1.6 m tall (citadel_east.md A4)
CIT_WALK = 2.7
PARAPET_H = 1.1                    # parapet height above the wall walk under a crenel
BATTER_H, BATTER_D = 1.5, 0.3      # battered plinth (only where a wall entry asks for "batter")
FORT_COL = {"jaffa_gate": (0.97, 0.97, 0.98),      # vertex colour on plain "fort" faces: the gate is
            "city_wall": (0.95, 0.95, 0.97),       # pale cream limestone, the Citadel greyer and more
            "citadel": (0.9, 0.9, 0.91)}           # weathered (photos); +-3 % per wall plane
FORT_TILE = 2.7                    # metres per repeat of the "fort" texture (5 courses -> ~0.54 m, as at the gate)


# ================================================================== geometry helpers
class Edge:
    """Face frame of the edge a->b: u along it, z up, off along the outward (right) normal."""

    def __init__(self, a, b):
        self.A = Vector((a[0], a[1], 0.0))
        d = Vector((b[0], b[1], 0.0)) - self.A
        self.L = d.length
        self.t = d / self.L if self.L > 1e-9 else Vector((1, 0, 0))
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, u, z, off=0.0):
        return self.A + self.t * u + self.n * off + Vector((0, 0, z))

    def u_of(self, p):
        return (Vector((p[0], p[1], 0.0)) - self.A).dot(self.t)

    def off_of(self, p):
        return (Vector((p[0], p[1], 0.0)) - self.A).dot(self.n)


def line_x(p, r, q, s):
    """Intersection of the 2D lines p + a r and q + b s (Vectors), or None if parallel."""
    den = r.x * s.y - r.y * s.x
    if abs(den) < 1e-6:
        return None
    a = ((q.x - p.x) * s.y - (q.y - p.y) * s.x) / den
    return p + r * a


def offset_ring(ring, d):
    """Exact inward offset of a CCW ring by d (d < 0: outward)."""
    n = len(ring)
    out = []
    for i in range(n):
        e0, e1 = Edge(ring[i - 1], ring[i]), Edge(ring[i], ring[(i + 1) % n])
        p0, p1 = e0.A - e0.n * d, e1.A - e1.n * d
        x = line_x(p0, e0.t, p1, e1.t)
        out.append((x.x, x.y) if x is not None else (p1.x, p1.y))
    return out


def face(mb, e, outline, mat, off=0.0, holes=(), col=None, inward=False):
    """Planar face in the plane of edge e at offset `off`: outline + holes given in (u, z).
    Constrained Delaunay triangulation (well-shaped triangles, no slivers between slits);
    a triangle is kept when it lies inside an odd number of rings (outline minus holes)."""
    nrm = -e.n if inward else e.n
    verts, faces = [], []
    for r in [outline] + list(holes):
        r = [Vector((p[0], p[1])) for p in r]
        if sum(r[i].x * r[i - 1].y - r[i - 1].x * r[i].y for i in range(len(r))) > 0:
            r.reverse()                                 # (the sum above is -2 * signed area)
        faces.append(list(range(len(verts), len(verts) + len(r))))
        verts += r
    try:
        ov, _e, of, _ov, _oe, origf = geometry.delaunay_2d_cdt(verts, [], faces, 1, 1e-5)
    except Exception:                                   # noqa: BLE001
        flat, tris = mk.tess2d([list(outline)] + [list(h) for h in holes])
        mb.tris([e.P(u, z, off) for u, z in flat], tris, mat, nrm, col=col)
        return
    for f, o in zip(of, origf):
        if len(o) % 2 == 1 and len(f) >= 3:
            mb.poly([e.P(ov[i].x, ov[i].y, off) for i in f], mat, nrm, col=col)


def tunnel(mb, e, ol, off0, off1, mat, floor=True, col=None):
    """Reveal joining the closed (u, z) outline ol at off0 and off1; faces look at the axis.
    floor=True skips the bottom segment (a passage floor is the ground)."""
    cu = sum(p[0] for p in ol) / len(ol)
    cz = sum(p[1] for p in ol) / len(ol)
    zmin = min(p[1] for p in ol)
    axis = e.P(cu, cz, (off0 + off1) / 2)
    for i in range(len(ol)):
        p, q = ol[i], ol[(i + 1) % len(ol)]
        if floor and abs(p[1] - zmin) < 1e-6 and abs(q[1] - zmin) < 1e-6:
            continue
        quad = [e.P(p[0], p[1], off0), e.P(q[0], q[1], off0), e.P(q[0], q[1], off1), e.P(p[0], p[1], off1)]
        h = axis - (quad[0] + quad[2]) / 2
        h -= e.n * h.dot(e.n)
        mb.poly(quad, mat, h, col=col)


def strip(mb, e, pts, off0, off1, mat, hint, col=None):
    """Quads extruded from an open (u, z) polyline between two offsets."""
    for p, q in zip(pts, pts[1:]):
        if abs(p[0] - q[0]) < 1e-7 and abs(p[1] - q[1]) < 1e-7:
            continue
        quad = [e.P(p[0], p[1], off0), e.P(q[0], q[1], off0), e.P(q[0], q[1], off1), e.P(p[0], p[1], off1)]
        mb.poly(quad, mat, hint(p, q) if callable(hint) else hint, col=col)


def u_shape(outer, inner):
    """Band between two outlines that share the ground line: outer is (u0,v0),(u1,v0),top...;
    returns outer from bottom-right over the top to bottom-left, then inner back."""
    return outer[1:] + [outer[0]] + [inner[0]] + inner[:0:-1]


def disc(mb, e, uc, zc, r, depth, mat, off=0.0, seg=10, col=None):
    """Roundel / boss: a short prism standing out of the face."""
    ring = [(uc + r * math.cos(2 * math.pi * k / seg), zc + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    mb.poly([e.P(u, z, off + depth) for u, z in ring], mat, e.n if depth >= 0 else -e.n, col=col)
    for k in range(seg):
        p, q = ring[k], ring[(k + 1) % seg]
        quad = [e.P(p[0], p[1], off), e.P(q[0], q[1], off), e.P(q[0], q[1], off + depth), e.P(p[0], p[1], off + depth)]
        mb.poly(quad, mat, e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) - e.P(uc, zc), col=col)


def section_prism(mb, e, u0, u1, prof, mat, skip=(), col=None, ends=True):
    """Prism along u (u0..u1) of a closed side profile [(off, z), ...] (consoles, corbels, cornices).
    skip: indices of profile segments not to emit (those lying against the wall)."""
    c = (sum(p[0] for p in prof) / len(prof), sum(p[1] for p in prof) / len(prof))
    for i in range(len(prof)):
        if i in skip:
            continue
        (o0, z0), (o1, z1) = prof[i], prof[(i + 1) % len(prof)]
        quad = [e.P(u0, z0, o0), e.P(u0, z1, o1), e.P(u1, z1, o1), e.P(u1, z0, o0)]
        mid = (quad[0] + quad[2]) / 2
        mb.poly(quad, mat, mid - e.P((u0 + u1) / 2, c[1], c[0]), col=col)
    if ends:
        for u, s in ((u0, -1), (u1, 1)):
            mb.poly([e.P(u, z, o) for o, z in prof], mat, e.t * s, col=col)


def pyramid(mb, c, t, s, w, z, h, mat, col=None):
    """Small square pyramid (merlon knob / cap) standing on z, base w x w, axes t and s."""
    c = Vector((c[0], c[1], 0))
    pts = [c + (t * a + s * b) * (w / 2) + UP * z for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    ap = c + UP * (z + h)
    for k in range(4):
        tri = [pts[k], pts[(k + 1) % 4], ap]
        mb.poly(tri, mat, (tri[0] + tri[1]) / 2 - (c + UP * z), col=col)


def obox(mb, c, t, s, lt, ls, z0, z1, mat, col=None, top=True, bottom=False, skip_sides=()):
    """Oriented box (like meshkit.box) that can leave out sides: 0 = -s, 1 = +t, 2 = +s, 3 = -t."""
    c, t, s = Vector((c[0], c[1], 0)), Vector((t[0], t[1], 0)), Vector((s[0], s[1], 0))
    pts = [c - t * lt / 2 - s * ls / 2, c + t * lt / 2 - s * ls / 2, c + t * lt / 2 + s * ls / 2, c - t * lt / 2 + s * ls / 2]
    lo = [p + UP * z0 for p in pts]
    hi = [p + UP * z1 for p in pts]
    cz = c + UP * ((z0 + z1) / 2)
    for k in range(4):
        if k in skip_sides:
            continue
        q = [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]]
        mb.poly(q, mat, (q[0] + q[2]) / 2 - cz, col=col)
    if top:
        mb.poly(hi, mat, UP, col=col)
    if bottom:
        mb.poly(lo, mat, -UP, col=col)


# ------------------------------------------------------------------ arch outlines (u, z)
def pointed_top(u0, u1, vs, rise, seg=6):
    """Two-centred pointed arch from the right springer (u1, vs) over the apex to (u0, vs)."""
    w = u1 - u0
    rise = max(rise, w / 2 + 1e-3)
    R = (w * w / 4 + rise * rise) / w
    a_top = math.atan2(rise, R - w / 2)
    pts = [(u1 - R + R * math.cos(a_top * k / seg), vs + R * math.sin(a_top * k / seg)) for k in range(seg + 1)]
    pts += [(u0 + R - R * math.cos(a_top * k / seg), vs + R * math.sin(a_top * k / seg)) for k in range(seg - 1, -1, -1)]
    return pts


def pointed(u0, u1, v0, vs, rise, seg=6):
    return [(u0, v0), (u1, v0)] + pointed_top(u0, u1, vs, rise, seg)


def pointed_halfwidth(w, vs, rise, z):
    """Half width of a pointed opening at height z."""
    if z <= vs:
        return w / 2
    R = (w * w / 4 + rise * rise) / w
    dz = z - vs
    return max(0.0, math.sqrt(max(0.0, R * R - dz * dz)) - (R - w / 2))


def shouldered(u0, u1, v0, v1, r, seg=3):
    """Flat-topped opening with rounded upper corners (the Jaffa Gate doorways)."""
    pts = [(u0, v0), (u1, v0), (u1, v1 - r)]
    pts += [(u1 - r + r * math.cos(math.pi / 2 * k / seg), v1 - r + r * math.sin(math.pi / 2 * k / seg))
            for k in range(1, seg + 1)]
    pts += [(u0 + r - r * math.cos(math.pi / 2 * k / seg), v1 - r + r * math.sin(math.pi / 2 * k / seg))
            for k in range(seg, -1, -1)]
    return pts


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


# ================================================================== crenellation
def merlon_layout(L, c0, c1, mw, cr):
    """Merlon intervals [(a, b)] along an edge of length L: end merlons c0 / c1 wide (shared with
    the neighbouring edge at a corner), then evenly spaced merlons ~mw wide with crenels ~cr."""
    avail = L - c0 - c1
    if avail < 0.8 * cr:
        return [(0.0, L)]
    n = max(0, int(round((avail - cr) / (mw + cr))))
    if n == 0:
        if avail <= 2.2 * cr:
            return [(0.0, c0), (L - c1, L)]
        n = 1
    c = (avail - n * mw) / (n + 1)
    m = mw
    if c < 0.6 * cr or c > 1.5 * cr:
        c = cr
        m = (avail - (n + 1) * c) / n
    out = [(0.0, c0)]
    u = c0 + c
    for _ in range(n):
        out.append((u, u + m))
        u += m + c
    out.append((L - c1, L))
    return out


def merlon_cap(a, b, z_top, style):
    """Top outline of one merlon from u=a to u=b."""
    w = b - a
    if style == "round" and w < 2.5:
        r = min(0.32, w * 0.3)
        R = (w * w / 4 + r * r) / (2 * r)
        zc = z_top - R
        return [(a + w * k / 6, zc + math.sqrt(max(0.0, R * R - (w * k / 6 - w / 2) ** 2))) for k in range(7)]
    if style == "pointed" and w < 2.5:
        return [(a, z_top - 0.42), ((a + b) / 2, z_top), (b, z_top - 0.42)]
    return [(a, z_top), (b, z_top)]


def top_profile(merlons, z_sill, z_top, styles):
    """Ascending (u, z) top outline of a crenellated face (vertical jumps at merlon sides)."""
    prof = []
    for j, (a, b) in enumerate(merlons):
        if j > 0:
            prof.append((a, z_sill))
        prof += merlon_cap(a, b, z_top, styles[j])
        if j < len(merlons) - 1:
            prof.append((b, z_sill))
    return prof


def z_at(prof, u):
    if u <= prof[0][0]:
        return prof[0][1]
    if u >= prof[-1][0]:
        return prof[-1][1]
    for (u0, z0), (u1, z1) in zip(prof, prof[1:]):
        if u0 <= u <= u1:
            if u1 - u0 < 1e-9:
                return max(z0, z1)
            return z0 + (z1 - z0) * (u - u0) / (u1 - u0)
    return prof[-1][1]


def clip_profile(prof, ua, ub):
    return [(ua, z_at(prof, ua))] + [p for p in prof if ua + 1e-6 < p[0] < ub - 1e-6] + [(ub, z_at(prof, ub))]


class Battlement:
    """Crenellated parapet along one straight face: builds the parapet back, crenel sills and
    cheeks, merlon tops and slits.  The outer face (which also carries openings) is built by the
    caller from `outline(z_base)` + `slit_holes`."""

    def __init__(self, e, ua, ub, uia, uib, z_walk, z_sill, z_top, d, cw0, cw1, mw, cr, style="flat",
                 slits=True, slit_every=1, end_corner=(True, True)):
        self.e, self.ua, self.ub, self.uia, self.uib = e, ua, ub, uia, uib
        self.zw, self.zs, self.zt, self.d = z_walk, z_sill, z_top, d
        L = ub - ua
        m = merlon_layout(L, cw0, cw1, mw, cr)
        self.merlons = [(ua + a, ua + b) for a, b in m]
        k = len(self.merlons)
        self.styles = [("flat" if (j == 0 and end_corner[0]) or (j == k - 1 and end_corner[1]) else style)
                       for j in range(k)]
        self.prof = top_profile(self.merlons, z_sill, z_top, self.styles)
        self.slits = []
        if slits:
            for j, (a, b) in enumerate(self.merlons):
                lo, hi = max(a, uia + 0.25), min(b, uib - 0.25)
                if hi - lo < 0.9 or (j % slit_every):
                    continue
                c = (lo + hi) / 2
                ztop = min(self.cap_spring(j), z_top) - 0.3
                if ztop - (z_sill + 0.12) > 0.4:
                    self.slits.append(rect(c - 0.07, c + 0.07, z_sill + 0.12, ztop))

    def cap_spring(self, j):
        cap = merlon_cap(*self.merlons[j], self.zt, self.styles[j])
        return min(cap[0][1], cap[-1][1])

    def outline(self, z_base):
        return [(self.ua, z_base), (self.ub, z_base)] + self.prof[::-1]

    def build(self, mb, mat, col=None, tops=True, inner_face=True):
        e, d, zs = self.e, self.d, self.zs
        if inner_face:
            ip = clip_profile(self.prof, self.uia, self.uib)
            face(mb, e, [(self.uia, self.zw), (self.uib, self.zw)] + ip[::-1], mat, -d,
                 holes=self.slits, col=col, inward=True)
        for s in self.slits:
            tunnel(mb, e, s, 0.0, -d, mat, floor=False, col=col)
        m = self.merlons
        for j in range(1, len(m)):
            a, b = m[j - 1][1], m[j][0]
            mb.poly([e.P(a, zs, 0), e.P(b, zs, 0), e.P(b, zs, -d), e.P(a, zs, -d)], mat, UP, col=col)
            za, zb = z_at(self.prof, a - 1e-4), z_at(self.prof, b + 1e-4)
            mb.poly([e.P(a, zs, 0), e.P(a, zs, -d), e.P(a, za, -d), e.P(a, za, 0)], mat, e.t, col=col)
            mb.poly([e.P(b, zs, 0), e.P(b, zs, -d), e.P(b, zb, -d), e.P(b, zb, 0)], mat, -e.t, col=col)
        if tops:
            for j in range(1, len(m) - 1):
                self.merlon_top(mb, j, mat, col)

    def merlon_top(self, mb, j, mat, col=None, ua=None, ub=None):
        a, b = self.merlons[j]
        cap = merlon_cap(a, b, self.zt, self.styles[j])
        e, d = self.e, self.d
        strip(mb, e, cap, 0.0, -d, mat, UP, col=col)
        if self.styles[j] == "pointed" and b - a < 2.5:
            obox(mb, e.P((a + b) / 2, 0, -d / 2), e.t, e.n, 0.16, 0.16, self.zt - 0.06, self.zt + 0.22, mat, col=col)
            pyramid(mb, e.P((a + b) / 2, 0, -d / 2), e.t, e.n, 0.24, self.zt + 0.22, 0.2, mat, col)


def battlemented_ring(mb, ring, base, z_walk, z_sill, z_top, d, mat, col=None, style="flat", cw=1.6, mw=1.7,
                      cr=0.8, holes=None, roof=True, roof_holes=(), slits=True, slit_every=1, layout=None):
    """A closed crenellated tower / enceinte on a CCW ring.
    base, style: scalar or per-edge lists.  holes(i, e) -> [{"ol": outline, "build": fn(mb, e)}].
    Returns (edges, inner_ring) for further dressing."""
    n = len(ring)
    E = [Edge(ring[i], ring[(i + 1) % n]) for i in range(n)]
    inner = offset_ring(ring, d)
    uin = [(E[i].u_of(inner[i]), E[i].u_of(inner[(i + 1) % n])) for i in range(n)]
    bats = []
    for i, e in enumerate(E):
        st = style[i] if isinstance(style, (list, tuple)) else style
        cw_, mw_, cr_ = (layout(i) if layout else None) or (cw, mw, cr)
        c0 = max(cw_, uin[i][0] + 0.45)
        c1 = max(cw_, e.L - uin[i][1] + 0.45)
        bats.append(Battlement(e, 0.0, e.L, uin[i][0], uin[i][1], z_walk, z_sill, z_top, d, c0, c1, mw_, cr_, st,
                               slits=slits, slit_every=slit_every))
    for i, e in enumerate(E):
        bz = base[i] if isinstance(base, (list, tuple)) else base
        hl = holes(i, e) if holes else []
        face(mb, e, bats[i].outline(bz), mat, 0.0, [h["ol"] for h in hl if h.get("ol")] + bats[i].slits, col)
        for h in hl:
            if h.get("build"):
                h["build"](mb, e)
        bats[i].build(mb, mat, col)
    for i in range(n):                                  # L-shaped corner merlon tops
        bp, bc = bats[i - 1], bats[i]
        ep, ec = E[i - 1], E[i]
        a_prev = bp.merlons[-1][0] if len(bp.merlons) > 1 else ep.L / 2
        b_cur = bc.merlons[0][1] if len(bc.merlons) > 1 else ec.L / 2
        pts = [ep.P(a_prev, 0, 0), Vector((*ring[i], 0)), ec.P(b_cur, 0, 0), ec.P(b_cur, 0, -d),
               Vector((*inner[i], 0)), ep.P(a_prev, 0, -d)]
        fl, ft = mk.tess2d([[(p.x, p.y) for p in pts]])
        mb.tris([(p[0], p[1], z_top) for p in fl], ft, mat, UP, col=col)
        if bp.styles[-1] == "flat" and bc.styles[0] == "flat" and "pointed" in (bp.styles[1:-1] + bc.styles[1:-1]):
            cm = (Vector((*ring[i], 0)) + Vector((*inner[i], 0))) / 2      # knob on a pointed-style corner
            pyramid(mb, cm, ec.t, ec.n, 0.5, z_top, 0.4, mat, col)
    if roof:
        fl, ft = mk.tess2d([inner] + [list(h) for h in roof_holes])
        mb.tris([(p[0], p[1], z_walk) for p in fl], ft, mat, UP, col=col)
    return E, inner, bats


LEAF_CELLS = ("door_olive", "door_wood2", "door_grey", "door_teal")    # grey-green plate grid
OAK_CELLS = ("door_wood", "door_wood2")                                 # studded planks


def atlas_cell(gen, atlas, names):
    """UV rect of the first existing cell of `names` in a generated atlas (cell names change)."""
    if not gen or atlas not in gen:
        return None
    cells = gen[atlas]["cells"]
    name = next((nm for nm in names if nm in cells), None)
    return mk.atlas_rect(gen[atlas]["grid"], cells[name]) if name else None


def keyhole(u, z0, z1, w=0.14, r=0.13, seg=8):
    """Arrow slit ending at the bottom in a round oillet (gate.md 1.7): CCW (u, z) outline."""
    a = math.asin(min(0.99, (w / 2) / r))
    t0, t1 = math.pi / 2 + a, 2.5 * math.pi - a
    pts = [(u + r * math.cos(t0 + (t1 - t0) * k / seg), z0 + r + r * math.sin(t0 + (t1 - t0) * k / seg))
           for k in range(seg + 1)]
    return pts + [(u + w / 2, z1), (u - w / 2, z1)]


def circle(uc, zc, r, seg=10):
    return [(uc + r * math.cos(2 * math.pi * k / seg), zc + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]


def slit_hole(u, z0, z1, w=0.14, depth=0.6, mat="fort", col=None, oillet=True):
    ol = keyhole(u, z0, z1, w) if oillet else rect(u - w / 2, u + w / 2, z0, z1)

    def build(mb, e, ol=ol):
        tunnel(mb, e, ol, 0.0, -depth, mat, floor=False, col=col)
        face(mb, e, ol, "void", -depth)
    return {"ol": ol, "build": build}


def dark_hole(ol, depth=0.5, mat="fort", col=None, grille_w=None, gen=None):
    """Window / oculus: reveal + dark back, optionally an iron grille card just inside."""
    def build(mb, e, ol=ol):
        tunnel(mb, e, ol, 0.0, -depth, mat, floor=False, col=col)
        face(mb, e, ol, "void", -depth)
        if grille_w and gen:
            us = [p[0] for p in ol]
            zs = [p[1] for p in ol]
            grille(mb, e, (min(us) + max(us)) / 2, min(zs), max(zs), max(us) - min(us), gen, off=-0.1)
    return {"ol": ol, "build": build}


def roundel(u, z, r=0.25, depth=0.06):
    """Carved stone roundel in the wall's own stone (a boss with a sunk centre), not a pale disc."""
    def build(mb, e):
        disc(mb, e, u, z, r, depth, "fort", seg=10, col=(0.86, 0.84, 0.8))
        disc(mb, e, u, z, r * 0.55, depth + 0.03, "fort", seg=8, col=(0.8, 0.78, 0.74))
    return {"build": build}


def panel(mb, e, uc, zc, w, h, off, lines=3, sgn=1, col=(0.88, 0.85, 0.78), text=(0.7, 0.66, 0.58)):
    """Inscription panel with a raised border and `lines` bands of low-relief lettering."""
    side = 0 if sgn > 0 else 2                                   # the side against the wall
    obox(mb, e.P(uc, 0, off + sgn * 0.03), e.t, e.n, w, 0.06, zc - h / 2, zc + h / 2, "ashlar", col=col,
         bottom=True, skip_sides=(side,))
    lh = (h - 0.16) / max(1, lines)
    for k in range(lines):
        z0 = zc - h / 2 + 0.08 + k * lh + lh * 0.15
        obox(mb, e.P(uc, 0, off + sgn * 0.065), e.t, e.n, w - 0.22, 0.012, z0, z0 + lh * 0.7, "ashlar", col=text,
             bottom=True, skip_sides=(side,))


def blind_arch(u0, u1, z0, vs, rise, depth, mat="fort", col=None, bench=None, dress=True):
    """Blind pointed arch beside the gate (gate.md 3.1): niche with a bench, carved capitals at the
    springing, roundels, a carved block over the apex, a stepped two-tier inscription and a white
    marble plaque in the tympanum."""
    ol = pointed(u0, u1, z0, vs, rise, 6)
    uc = (u0 + u1) / 2
    apex = vs + max(rise, (u1 - u0) / 2)

    def build(mb, e, ol=ol):
        tunnel(mb, e, ol, 0.0, -depth, mat, floor=z0 <= 0.0, col=col)
        face(mb, e, ol, mat, -depth, col=col)
        if bench:
            bh, bd = bench
            section_prism(mb, e, u0, u1, [(-depth, z0), (-depth + bd, z0), (-depth + bd, z0 + bh), (-depth, z0 + bh)],
                          "ashlar", skip=(3,), col=DRESSED, ends=False)
        if not dress:
            return
        for uu in (u0, u1):                                           # acanthus capitals (spolia)
            obox(mb, e.P(uu, 0, 0.06), e.t, e.n, 0.5, 0.12, vs - 0.42, vs + 0.06, "ashlar", col=DRESSED,
                 bottom=True, skip_sides=(0,))
            obox(mb, e.P(uu, 0, 0.1), e.t, e.n, 0.36, 0.08, vs - 0.3, vs - 0.06, "ashlar", col=(0.9, 0.87, 0.8),
                 bottom=True, skip_sides=(0,))
        obox(mb, e.P(uc, 0, 0.08), e.t, e.n, 0.42, 0.16, apex + 0.12, apex + 0.5, "ashlar", col=(0.86, 0.83, 0.76),
             bottom=True, skip_sides=(0,))
        off = -depth
        panel(mb, e, uc, vs + 1.3, 0.9, 0.45, off, lines=2)            # stepped two-tier inscription
        panel(mb, e, uc, vs + 0.68, 1.8, 0.6, off, lines=3)
        obox(mb, e.P(uc, 0, off + 0.025), e.t, e.n, 1.0, 0.05, vs - 0.75, vs + 0.1, "lime",   # marble plaque
             col=(1.0, 1.0, 1.0), bottom=True, skip_sides=(0,))
        for k in range(4):
            zl = vs - 0.6 + k * 0.17
            obox(mb, e.P(uc, 0, off + 0.055), e.t, e.n, 0.78, 0.01, zl, zl + 0.08, "lime", col=(0.6, 0.6, 0.6),
                 bottom=True, skip_sides=(0,))
    return {"ol": ol, "build": build}


# ================================================================== Jaffa Gate tower
def portal(mb, e, uc, P, depth_total, mat, outer=True, blocked=(), gen=None):
    """The recessed pointed-arch portal of the Jaffa Gate (gate.md 1.4 / 1.8; both faces share it):
    moulded pointed frame (flat band + roll) ending in volutes with rosettes beyond them, a keystone,
    the recessed tympanum with a cornice and the inscription panel between roundels, the flat doorway
    with rounded corners, the door frame, the step out to the taller passage arch behind it and the
    open iron-plated door leaves standing against the passage walls."""
    rw, rs, rr, rd = P["recess_w"], P["recess_spring"], P["recess_rise"], P["recess_d"]
    dw, dh, dr = P["door_w"], P["door_h"], P["door_r"]
    pw, ps, pr = P["pass_w"], P["pass_spring"], P["pass_rise"]
    frame_d = P["frame_d"]
    free = lambda u: not any(a - 0.3 < u < b + 0.3 for a, b in blocked)   # noqa: E731
    r0, r1 = uc - rw / 2, uc + rw / 2
    recess = pointed(r0, r1, 0.0, rs, rr, 7)
    if P.get("door_shape") == "pointed":                      # inner doorway: a tall pointed arch
        door = pointed(uc - dw / 2, uc + dw / 2, 0.0, P["door_spring"], P["door_rise"], 6)
        dh = P["door_spring"] + max(P["door_rise"], dw / 2)
    else:                                                       # outer: flat with rounded corners
        door = shouldered(uc - dw / 2, uc + dw / 2, 0.0, dh, dr)
    pas = pointed(uc - pw / 2, uc + pw / 2, 0.0, ps, pr, 6)
    tunnel(mb, e, recess, 0.0, -rd, mat)                                       # recess reveal
    face(mb, e, u_shape(recess, door), mat, -rd)                               # tympanum + jambs
    tunnel(mb, e, door, -rd, -rd - frame_d, mat)                               # door frame
    face(mb, e, u_shape(pas, door), mat, -rd - frame_d, inward=True)           # rebate step
    tunnel(mb, e, pas, -rd - frame_d, -depth_total, mat)                       # passage to the chamber
    # moulded frame: a broad flat band with a roll moulding on its inner edge, around the arch only
    c = e.P(uc, rs)
    for bw, rise_k, bp0, bp1 in ((P["band"], P["band_rise"], 0.0, 0.08), (0.3, 0.3 * P["band_rise"] / P["band"],
                                                                          0.08, 0.2)):
        outer_top = pointed_top(r0 - bw, r1 + bw, rs, rr + rise_k, 7)
        inner_top = pointed_top(r0, r1, rs, rr, 7)
        face(mb, e, outer_top + inner_top[::-1], "ashlar", bp1, col=DRESSED)
        strip(mb, e, outer_top, bp0, bp1, "ashlar", lambda p, q: e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) - c,
              DRESSED)
        if bp0 == 0.0:
            strip(mb, e, inner_top, 0.0, bp1, "ashlar", lambda p, q: c - e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2),
                  DRESSED)
        for u_a, u_b in ((r1, r1 + bw), (r0 - bw, r0)):
            mb.poly([e.P(u_a, rs, bp0), e.P(u_b, rs, bp0), e.P(u_b, rs, bp1), e.P(u_a, rs, bp1)], "ashlar", -UP,
                    col=DRESSED)
    bw = P["band"]
    for u_v in (r0 - bw * 0.5, r1 + bw * 0.5):                                 # spiral volutes at the springing
        disc(mb, e, u_v, rs - 0.17, 0.2, 0.14, "ashlar", seg=8, col=DRESSED)
    for u_v in (r0 - bw - 0.42, r1 + bw + 0.42):                               # carved rosettes beyond them
        if free(u_v):
            disc(mb, e, u_v, rs, 0.28, 0.05, "ashlar", seg=10, col=DRESSED)
            disc(mb, e, u_v, rs, 0.16, 0.1, "ashlar", seg=8, col=DRESSED)
    apex = rs + rr + P["band_rise"]
    obox(mb, e.P(uc, 0, 0.12), e.t, e.n, 0.42, 0.24, apex - 0.45, apex + 0.12, "ashlar", col=DRESSED, bottom=True,
         skip_sides=(0,))                                                      # keystone block
    # tympanum: cornice over the doorway and the inscription panel between two roundels
    zc = dh + 0.75
    if P.get("door_shape") != "pointed":
        hw = pointed_halfwidth(rw, rs, rr, zc + 0.22) - 0.02
        section_prism(mb, e, uc - hw, uc + hw, [(-rd, zc), (-rd + 0.1, zc), (-rd + 0.17, zc + 0.12),
                                                (-rd + 0.17, zc + 0.22), (-rd, zc + 0.22)],
                      "ashlar", skip=(4,), col=DRESSED)
    pw_, ph_, pz_ = P["panel"]
    pz_ = max(pz_, dh + ph_ / 2 + 0.35)
    pw_ = min(pw_, 2 * pointed_halfwidth(rw, rs, rr, pz_ + ph_ / 2 + 0.05) - 0.9) if pz_ + ph_ / 2 < rs + rr else 0.0
    if pw_ > 0.5:                              # (a tall pointed doorway leaves no room for the panel)
        panel(mb, e, uc, pz_, pw_, ph_, -rd, lines=3)
        for s in (-1, 1):
            u_r = uc + s * (pw_ / 2 + 0.3)
            if pointed_halfwidth(rw, rs, rr, pz_ + 0.22) > abs(u_r - uc) + 0.22:
                disc(mb, e, u_r, pz_, 0.18, 0.05, "ashlar", off=-rd, seg=8, col=DRESSED)
    # the two leaves stand open against the passage walls just behind the door frame
    for s in (-1, 1):
        hinge = e.P(uc + s * (pw / 2 - 0.1 - 0.06), 0, -rd - frame_d - 0.06)
        ang = math.radians(4)                                  # nearly flat against the passage wall
        dirv = -e.n * math.cos(ang) - e.t * s * math.sin(ang)
        gate_leaf(mb, hinge, dirv, -e.t * s, dw / 2, min(4.6, dh - 0.3), gen, wicket=(s == 1))


def gate_leaf(mb, hinge, dirv, face_n, w, h, gen, t=0.12, wicket=False):
    """One heavy door leaf (gate.md 2): timber clad in grey-green riveted iron plates.  hinge = foot of
    the hinge edge on the leaf's mid-plane, dirv = along the leaf, face_n ~ normal of the visible face
    (towards the passage axis).  Both faces carry the plate-grid texture; edges are iron; the visible
    face gets iron straps with rows of rivet heads and, on one leaf, the wicket door."""
    dirv = Vector((dirv.x, dirv.y, 0)).normalized()
    nrm = Vector((-dirv.y, dirv.x, 0))
    if nrm.dot(face_n) < 0:
        nrm = -nrm
    hinge = Vector((hinge.x, hinge.y, 0))
    rect_uv = atlas_cell(gen, "doors", LEAF_CELLS)
    z0, z1 = 0.02, 0.02 + h
    for sg in (1, -1):                                              # the two plated faces, 2 plate tiers each
        o = nrm * (sg * t / 2)
        for k in range(2):
            za, zb = z0 + h * k / 2, z0 + h * (k + 1) / 2
            q = [hinge + o + UP * za, hinge + o + dirv * w + UP * za, hinge + o + dirv * w + UP * zb, hinge + o + UP * zb]
            if rect_uv:
                u0, v0, u1, v1 = rect_uv
                uv = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
                if sg < 0:
                    uv = [(u1, v0), (u0, v0), (u0, v1), (u1, v1)]
                mb.poly(q, "doors", nrm * sg, uv=uv, col=LEAF_COL)
            else:
                mb.poly(q, "metal_dark", nrm * sg)
    c = hinge + dirv * (w / 2)
    obox(mb, c, dirv, nrm, w, t, z0, z1, "iron", skip_sides=(0, 2), top=True)    # edges: ends + top
    # straps with rivet heads on the visible face
    for k in range(4):
        zs = z0 + 0.3 + k * (h - 0.6) / 3
        obox(mb, c + nrm * (t / 2 + 0.006), dirv, nrm, w - 0.04, 0.012, zs - 0.05, zs + 0.05, "iron", bottom=True,
             skip_sides=(0,))
        for j in range(7):
            p = hinge + dirv * (0.12 + j * (w - 0.24) / 6) + nrm * (t / 2 + 0.018)
            obox(mb, p, dirv, nrm, 0.045, 0.018, zs - 0.022, zs + 0.022, "iron", skip_sides=(0,))
    if wicket:                                                      # small door in the leaf: iron frame strips
        a, b, zt = 0.3, 1.1, z0 + 1.85
        for (p0, p1, za, zb) in ((a, a + 0.05, z0 + 0.12, zt), (b - 0.05, b, z0 + 0.12, zt), (a, b, zt - 0.05, zt),
                                 (a, b, z0 + 0.12, z0 + 0.17)):
            obox(mb, hinge + dirv * ((p0 + p1) / 2) + nrm * (t / 2 + 0.01), dirv, nrm, p1 - p0, 0.02, za, zb, "iron",
                 bottom=True, skip_sides=(0,))
        obox(mb, hinge + dirv * (b - 0.15) + nrm * (t / 2 + 0.04), dirv, nrm, 0.04, 0.06, z0 + 0.95, z0 + 1.1, "iron",
             bottom=True)


def machicolation(mb, e, uc, zb, zt, w=1.5, pj=0.75, mat="fort", col=None, cap="pyramid"):
    """Box machicolation on three stepped corbels (two dark drop-holes between them), a slit in
    front, a dentil band and either a pyramid cap with a knob or a small crown of merlons."""
    zband = zt - 0.18
    slit = rect(uc - 0.06, uc + 0.06, max(zb + 0.25, zband - 1.0), zband - 0.35)
    face(mb, e, rect(uc - w / 2, uc + w / 2, zb, zband), mat, pj, holes=[slit], col=col)
    tunnel(mb, e, slit, pj, pj - 0.12, mat, floor=False, col=col)
    face(mb, e, slit, "void", pj - 0.12)
    for s in (-1, 1):
        u = uc + s * w / 2
        mb.poly([e.P(u, zb, 0), e.P(u, zb, pj), e.P(u, zband, pj), e.P(u, zband, 0)], mat, e.t * s, col=col)
    mb.poly([e.P(uc - w / 2, zb, 0), e.P(uc + w / 2, zb, 0), e.P(uc + w / 2, zb, pj), e.P(uc - w / 2, zb, pj)],
            "void", -UP)
    bw, bpj = w / 2 + 0.07, pj + 0.07
    section_prism(mb, e, uc - bw, uc + bw, [(0, zband), (bpj, zband), (bpj, zt), (0, zt)], "ashlar",
                  skip=(2, 3), col=DRESSED)
    if cap == "pyramid":
        ap = e.P(uc, zt + 0.75, bpj * 0.5)
        corners = [e.P(uc - bw, zt, 0), e.P(uc + bw, zt, 0), e.P(uc + bw, zt, bpj), e.P(uc - bw, zt, bpj)]
        for k in (1, 2, 3):
            tri = [corners[k], corners[(k + 1) % 4], ap]
            mb.poly(tri, "ashlar", (tri[0] + tri[1]) / 2 - e.P(uc, zt, bpj * 0.5), col=DRESSED)
        obox(mb, ap, e.t, e.n, 0.14, 0.14, zt + 0.7, zt + 0.95, "ashlar", col=DRESSED)          # knob
    elif cap in ("crown", "flat"):
        mb.poly([e.P(uc - bw, zt, 0), e.P(uc + bw, zt, 0), e.P(uc + bw, zt, bpj), e.P(uc - bw, zt, bpj)], "ashlar", UP,
                col=DRESSED)
        for k in ((-1, 0, 1) if cap == "crown" else ()):
            obox(mb, e.P(uc + k * (bw - 0.13), 0, bpj - 0.13), e.t, e.n, 0.22, 0.22, zt, zt + 0.32, "ashlar",
                 col=DRESSED)
    for k in (-1, 0, 1):
        u = uc + k * (w / 2 - 0.14)
        section_prism(mb, e, u - 0.13, u + 0.13,
                      [(0, zb - 0.95), (pj * 0.45, zb - 0.95), (pj * 0.45, zb - 0.5), (pj, zb - 0.5), (pj, zb), (0, zb)],
                      mat, skip=(4, 5), col=col)


def groin_vault(mb, C, z_spring, rise, N=12, mat="ashlar", col=None, dome=0.0):
    """Pointed groin vault over the quad C[0..3]: z = spring + rise*max(g(u), g(v)) + dome*sin(pi u)sin(pi v)
    (the wall arches stay at spring + rise, the crown rises by `dome`); returns g so the wall arches
    can follow it exactly."""
    r = 0.62                                           # rise / span of the normalised pointed arch
    R = 0.25 + r * r

    def g(s):
        s = min(s, 1 - s)
        return math.sqrt(max(0.0, R * R - (R - s) ** 2)) / r

    C = [Vector((c[0], c[1], 0)) for c in C]

    def P(u, v):
        p = C[0] * (1 - u) * (1 - v) + C[1] * u * (1 - v) + C[2] * u * v + C[3] * (1 - u) * v
        return Vector((p.x, p.y, z_spring + rise * max(g(u), g(v)) + dome * math.sin(math.pi * u) * math.sin(math.pi * v)))
    grid = [[P(i / N, j / N) for j in range(N + 1)] for i in range(N + 1)]
    h = N // 2
    for i in range(N):
        for j in range(N):
            a, b, c, d = grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]
            if (i < h) == (j < h):
                tris = ((a, b, c), (a, c, d))
            else:
                tris = ((a, b, d), (b, c, d))
            for t in tris:
                mb.poly(list(t), mat, -UP, col=col)
    for diag in (lambda k: (k / N, k / N), lambda k: (k / N, 1 - k / N)):     # diagonal ribs under the groins
        pts = [P(*diag(k)) for k in range(N + 1)]
        for k in range(N):
            a, b = pts[k], pts[k + 1]
            d = Vector((b.x - a.x, b.y - a.y, 0))
            if d.length < 1e-6:
                continue
            w = Vector((-d.y, d.x, 0)).normalized() * 0.15
            lo_a, lo_b = a - UP * 0.16, b - UP * 0.16
            mb.poly([lo_a - w, lo_b - w, lo_b + w, lo_a + w], "ashlar", -UP, col=DRESSED)
            for sgn in (-1, 1):
                q = [lo_a + w * sgn, lo_b + w * sgn, b + w * sgn + UP * 0.25, a + w * sgn + UP * 0.25]
                mb.poly(q, "ashlar", w * sgn, col=DRESSED)
    top = P(0.5, 0.5)                                  # round boss at the crown
    ring = [top + Vector((math.cos(2 * math.pi * k / 8) * 0.38, math.sin(2 * math.pi * k / 8) * 0.38, 0)) for k in range(8)]
    lo = [p - UP * 0.3 for p in ring]
    for k in range(8):
        q = [lo[k], lo[(k + 1) % 8], ring[(k + 1) % 8], ring[k]]
        mb.poly(q, "ashlar", (q[0] + q[1]) / 2 - (top - UP * 0.15), col=DRESSED)
    mb.poly(lo, "ashlar", -UP, col=DRESSED)
    return g


# outer (NW) portal: gate.md s9 (moulded arch outer 6.7 / inner 5.2 m, springing 4.9, apex 8.4 / 7.7;
# doorway crown <= 4.9; inscription 2.0 x 0.75 centred at 6.8); the inner (NE) portal is a smaller twin
GATE_OUTER = dict(recess_w=5.2, recess_spring=4.9, recess_rise=2.8, recess_d=0.5, band=0.75, band_rise=0.7,
                  door_r=0.65, frame_d=0.5, pass_spring=4.0, pass_rise=2.5, door_hmax=4.9, panel=(2.0, 0.75, 6.8))
GATE_INNER = dict(recess_w=5.0, recess_spring=4.7, recess_rise=2.7, recess_d=0.6, band=0.6, band_rise=0.55,
                  door_r=0.7, frame_d=0.45, pass_spring=4.0, pass_rise=2.5, door_hmax=4.5, panel=(1.6, 0.6, 6.45),
                  # (Street View from Omar ibn al-Khattab Square: the inner doorway is an open pointed arch rising
                  #  well into the recess, not a flat 4.5 m door with a tympanum over it)
                  door_shape="pointed", door_spring=4.1, door_rise=2.3)
GATE_MERLONS = {"out": (2.9, 2.9, 0.6), "in": (2.0, 1.8, 0.9), "side": (2.3, 2.2, 0.5)}   # (corner, merlon, crenel)


def gate_params(p, k):
    P = dict(GATE_OUTER if k == 0 else GATE_INNER)
    P.update(door_w=p["w"], door_h=min(p["h"] - 1.4, P["door_hmax"]), pass_w=p["w"] + 0.8)
    P["pass_spring"] = min(P["pass_spring"], p["h"] - P["pass_rise"])
    P["recess_w"] = max(P["recess_w"], p["w"] + 1.3)
    return P


def build_gatehouse(mb, g, place, rng, gen=None, blocked=None):
    """blocked: {edge: [(u0, u1)]} stretches of the faces covered by abutting city walls."""
    ring = [tuple(p) for p in g["ring"]]
    H = g["height"]                                    # top of the merlons
    th = g.get("wall", 2.0)
    zw, zs, d = H - GATE_WALK, H - GATE_SILL, GATE_PARAPET
    passages = list(g["passages"])
    pas = {p["edge"]: (k, p) for k, p in enumerate(passages)}
    blocked = blocked or {}
    free = lambda i, u: not any(a - 0.3 < u < b + 0.3 for a, b in blocked.get(i, []))   # noqa: E731

    def holes(i, e):
        hs = []
        if i in pas:
            k, p = pas[i]
            uc = p["u"] * e.L
            P = gate_params(p, k)
            hs.append({"ol": pointed(uc - P["recess_w"] / 2, uc + P["recess_w"] / 2, 0.0, P["recess_spring"],
                                     P["recess_rise"], 7),
                       "build": lambda mb_, e_, uc=uc, P=P, k=k: portal(mb_, e_, uc, P, th, "fort", outer=(k == 0),
                                                                       blocked=blocked.get(i, []), gen=gen)})
            if k == 0:     # box machicolation over the outer arch, a slit each side of it, just under the merlons
                hs.append({"build": lambda mb_, e_, uc=uc: machicolation(mb_, e_, uc, H - 3.1, H - 0.2, 1.5, 0.7)})
                for s in (-1, 1):
                    if free(i, uc + s * 1.6):
                        hs.append(slit_hole(uc + s * 1.6, zw - 1.9, zw - 0.2))
            else:          # small crowned machicolation (lantern) over the inner arch, slits at ~8-9 m
                hs.append({"build": lambda mb_, e_, uc=uc: machicolation(mb_, e_, uc, H - 3.8, H - 2.4, 1.2, 0.55,
                                                                          cap="crown")})
                for s in (-1, 1):
                    if free(i, uc + s * 1.5):
                        hs.append(slit_hole(uc + s * 1.5, 7.9, 9.3))
        elif (i - 1) % 4 in pas and pas[(i - 1) % 4][0] == 0:       # SW face: plain, slits high up
            for f in (0.35, 0.65):
                hs.append(slit_hole(e.L * f, zw - 1.8, zw - 0.3))
            hs.append(roundel(e.L * 0.5, 6.0, 0.28))
            hs.append({"build": lambda mb_, e_: lamp_bracket(mb_, e_, e_.L * 0.5, 8.4)})
        else:                                                        # SE face (towards the breach road)
            hs.append(slit_hole(e.L * 0.5, zw - 1.7, zw - 0.3))
            hs.append(roundel(e.L * 0.3, 5.0, 0.25))
        return hs

    def layout(i):
        if i in pas:
            return GATE_MERLONS["out" if pas[i][0] == 0 else "in"]
        return GATE_MERLONS["side"]

    E, inner_par, bats = battlemented_ring(mb, ring, -0.6, zw, zs, H, d, "fort", holes=holes, roof=True,
                                           layout=layout)
    # ---- chamber: four walls under a pointed groin vault (crown <= 7.5 m, gate.md 2)
    C = offset_ring(ring, th)
    vs, vr, dome, N = 4.4, 2.4, 0.7, 12                    # wall arches 6.8 m (clear the passages), crown 7.5
    gfn = groin_vault(mb, C, vs, vr, N, "ashlar", col=(1.0, 0.99, 0.96), dome=dome)
    out_edge = passages[0]["edge"]
    back = (out_edge + 2) % 4
    for i, e in enumerate(E):
        ua, ub = e.u_of(C[i]), e.u_of(C[(i + 1) % 4])
        top = [(ua + (ub - ua) * k / N, vs + vr * gfn(k / N)) for k in range(N + 1)]
        hl = []
        uc = (ua + ub) / 2
        if i in pas:
            k, p = pas[i]
            P = gate_params(p, k)
            uc = p["u"] * e.L
            pas_ol = pointed(uc - P["pass_w"] / 2, uc + P["pass_w"] / 2, 0.0, P["pass_spring"], P["pass_rise"], 6)
            hl.append(pas_ol)
            # transverse arch on pilasters framing the passage on the chamber side (photo 053)
            bw = min(0.25, uc - P["pass_w"] / 2 - ua - 0.05, ub - uc - P["pass_w"] / 2 - 0.05)
            if bw > 0.08:
                outer = pointed(uc - P["pass_w"] / 2 - bw, uc + P["pass_w"] / 2 + bw, 0.0, P["pass_spring"],
                                P["pass_rise"] + bw * 0.9, 6)
                face(mb, e, u_shape(outer, pas_ol), "ashlar", -th - 0.12, col=DRESSED, inward=True)
                cc = e.P(uc, P["pass_spring"], -th)
                strip(mb, e, outer[1:] + [outer[0]], -th, -th - 0.12, "ashlar",
                      lambda p_, q_: e.P((p_[0] + q_[0]) / 2, (p_[1] + q_[1]) / 2, -th) - cc, DRESSED)
                strip(mb, e, pas_ol[1:] + [pas_ol[0]], -th, -th - 0.12, "ashlar",
                      lambda p_, q_: cc - e.P((p_[0] + q_[0]) / 2, (p_[1] + q_[1]) / 2, -th), DRESSED)
        elif i == back:                                             # roundel over an inscription panel
            disc(mb, e, uc, 4.5, 0.3, -0.06, "ashlar", off=-th, seg=10, col=DRESSED)
            panel(mb, e, uc, 3.5, 1.5, 0.5, -th, lines=2, sgn=-1)
        else:                                                       # pointed niche with an arrow slit
            niche = pointed(uc - 0.8, uc + 0.8, 1.2, 2.9, 0.85, 5)
            hl.append(niche)
            tunnel(mb, e, niche, -th, -th + 0.8, "fort", floor=False)
            sl = rect(uc - 0.06, uc + 0.06, 1.7, 3.1)
            face(mb, e, niche, "fort", -th + 0.8, holes=[sl], inward=True)
            tunnel(mb, e, sl, -th + 0.8, -th + 1.0, "fort", floor=False)
            face(mb, e, sl, "void", -th + 1.0, inward=True)
            disc(mb, e, uc, 4.35, 0.22, -0.05, "ashlar", off=-th, seg=8, col=DRESSED)
        face(mb, e, [(ua, -0.05), (ub, -0.05)] + top[::-1], "fort", -th, holes=hl, inward=True)
    # ---- a couple of dry tufts on merlon tops (no vegetation in the passage or on the faces)
    for bat in bats[1:3]:
        if len(bat.merlons) > 2:
            a, b = bat.merlons[1 + int(rng.random() * (len(bat.merlons) - 2))]
            place("weeds", bat.e.P((a + b) / 2, H, -d / 2), rng.uniform(0, 6.28), True)


def lamp_bracket(mb, e, uc, z):
    """The old V-shaped floodlight arm on the gate's SW face (gate.md 1.7): two iron rods and a lamp box."""
    tip = e.P(uc, z - 0.5, 0.9)
    for s in (-1, 1):
        mk.tube(mb, [e.P(uc + s * 0.7, z + 0.4, 0.02), tip], 0.025, "iron")
    obox(mb, tip - e.n * 0.0, e.t, e.n, 0.35, 0.25, z - 0.8, z - 0.5, "metal_dark", bottom=True)


# ================================================================== city wall
def wall_run(mb, e, ua, ub, ka, kb, H, T, mat, col=None, holes=(), cap_a=None, cap_b=None, batter=False,
             end_corner=(True, True), cw=1.3, mw=1.8, cr=0.8, mh=1.1, slit_every=1):
    """Straight run of the crenellated city wall along edge e from u=ua to u=ub (at the centre line).
    ka, kb: mitre slopes (the run ends at u = ua + ka*off); cap_*: None, "full" or "inner" end face.
    mh = merlon height above the crenel sill; the walk is PARAPET_H below the sill."""
    zs = H - mh
    zw = zs - PARAPET_H
    d = GATE_PARAPET
    o_out, o_par, o_in = T / 2, T / 2 - d, -T / 2
    ip_t, ip_h = 0.5, 1.0
    o_q = o_in + ip_t
    ua_o, ub_o = ua + ka * o_out, ub + kb * o_out
    ua_p, ub_p = ua + ka * o_par, ub + kb * o_par
    bat = Battlement(e, ua_o, ub_o, ua_p, ub_p, zw, zs, H, d, cw, cw, mw, cr, slits=True, slit_every=slit_every,
                     end_corner=end_corner)
    z_face = BATTER_H if batter else -0.6
    face(mb, e, bat.outline(z_face), mat, o_out, holes=[h["ol"] for h in holes if h.get("ol")] +
         [[(u, z) for u, z in s] for s in bat.slits], col=col)
    se = ShiftedEdge(e, o_out)                         # openings were given in u at the outer face
    for h in holes:
        if h.get("build"):
            h["build"](mb, se)
    bat.e = se
    bat.build(mb, mat, col, tops=False)
    for j in range(len(bat.merlons)):                              # all merlon tops (mitred at the ends)
        a, b = bat.merlons[j]
        if j == 0 or j == len(bat.merlons) - 1:
            if len(bat.merlons) == 1:
                q = [e.P(ua_o, H, o_out), e.P(ub_o, H, o_out), e.P(ub_p, H, o_par), e.P(ua_p, H, o_par)]
            elif j == 0:
                q = [e.P(ua_o, H, o_out), e.P(b, H, o_out), e.P(b, H, o_par), e.P(ua_p, H, o_par)]
            else:
                q = [e.P(a, H, o_out), e.P(ub_o, H, o_out), e.P(ub_p, H, o_par), e.P(a, H, o_par)]
            mb.poly(q, mat, UP, col=col)
        else:
            bat.merlon_top(mb, j, mat, col)
    ua_q, ub_q = ua + ka * o_q, ub + kb * o_q                      # walk, inner parapet, inner face
    ua_i, ub_i = ua + ka * o_in, ub + kb * o_in
    mb.poly([e.P(ua_p, zw, o_par), e.P(ub_p, zw, o_par), e.P(ub_q, zw, o_q), e.P(ua_q, zw, o_q)], mat, UP, col=col)
    mb.poly([e.P(ua_q, zw, o_q), e.P(ub_q, zw, o_q), e.P(ub_q, zw + ip_h, o_q), e.P(ua_q, zw + ip_h, o_q)], mat, e.n,
            col=col)
    mb.poly([e.P(ua_q, zw + ip_h, o_q), e.P(ub_q, zw + ip_h, o_q), e.P(ub_i, zw + ip_h, o_in),
             e.P(ua_i, zw + ip_h, o_in)], mat, UP, col=col)
    mb.poly([e.P(ua_i, -0.6, o_in), e.P(ub_i, -0.6, o_in), e.P(ub_i, zw + ip_h, o_in), e.P(ua_i, zw + ip_h, o_in)],
            mat, -e.n, col=col)
    if batter:
        o_b = o_out + BATTER_D
        q = [e.P(ua + ka * o_b, -0.6, o_b), e.P(ub + kb * o_b, -0.6, o_b), e.P(ub_o, BATTER_H, o_out),
             e.P(ua_o, BATTER_H, o_out)]
        mb.poly(q, mat, e.n * BATTER_H + UP * BATTER_D, col=col)
    for cap, u0, k, sgn in ((cap_a, ua, ka, -1), (cap_b, ub, kb, 1)):
        if not cap:
            continue
        if cap == "full":
            sec = [(o_in, -0.6), (o_out + (BATTER_D if batter else 0), -0.6)]
            if batter:
                sec.append((o_out, BATTER_H))
            sec += [(o_out, H), (o_par, H), (o_par, zw), (o_q, zw), (o_q, zw + ip_h), (o_in, zw + ip_h)]
        else:
            sec = [(o_in, -0.6), (0.0, -0.6), (0.0, zw), (o_q, zw), (o_q, zw + ip_h), (o_in, zw + ip_h)]
        mb.poly([e.P(u0 + k * o, z, o) for o, z in sec], mat, e.t * sgn, col=col)
    return bat


class ShiftedEdge(Edge):
    """The same edge frame with off measured from a parallel line (the outer face)."""

    def __init__(self, e, off0):
        self.A = e.A + e.n * off0
        self.L, self.t, self.n = e.L, e.t, e.n


def wall_tower(mb, e, uc, w, out, T, H, mat, col=None):
    """Rectangular tower projecting from the outer face of the wall at u=uc (spec "towers" only)."""
    o0, o1 = -T / 2, T / 2 + out
    ring = [(e.P(uc - w / 2, 0, o0)), (e.P(uc - w / 2, 0, o1)), (e.P(uc + w / 2, 0, o1)), (e.P(uc + w / 2, 0, o0))]
    ring = [(p.x, p.y) for p in ring]
    if mk.ring_area(ring) < 0:
        ring = ring[::-1]

    def holes(i, ee):
        if ee.n.dot(e.n) > 0.7:                                    # front face
            return [slit_hole(ee.L * 0.5, 5.5, 7.4),
                    {"build": lambda mb_, e_: machicolation(mb_, e_, e_.L * 0.5, H - 3.2, H - 0.25, 1.4, 0.7)}]
        if abs(ee.n.dot(e.t)) > 0.7:
            return [slit_hole(ee.L * 0.62, 6.0, 7.6)]
        return []
    battlemented_ring(mb, ring, -0.6, H - 1.1 - PARAPET_H, H - 1.1, H, GATE_PARAPET, mat, col, cw=1.5, mw=1.8,
                      cr=0.6, holes=holes)


# crenellation of the three stretches NW of the gate (gate.md 3 / s9): corner merlon, merlon, gap, height
WALL_STYLES = {
    "blind": dict(cw=1.2, mw=1.2, cr=0.6, mh=0.7),        # low curtain with the blind arch, top ~10.8
    "tall": dict(cw=2.6, mw=2.6, cr=0.55, mh=1.1),        # tall stretch: three ~2-2.6 m merlons, top ~13.3
    "long": dict(cw=1.6, mw=1.6, cr=0.45, mh=0.75),       # long curtain further NW, top ~11.25
}


def wall_style(w, touches_gate, tallest):
    name = w.get("name", "")
    if "blind" in name:
        key = "blind"
    elif "tall" in name:
        key = "tall"
    elif touches_gate and len(w["pts"]) == 2:
        key = "blind"
    elif tallest and len(w["pts"]) == 2:
        key = "tall"
    else:
        key = "long"
    st = dict(WALL_STYLES[key], kind=key)
    m = w.get("merlons")
    if m:
        st.update(mw=m.get("w", st["mw"]), cw=m.get("w", st["cw"]), cr=m.get("gap", st["cr"]), mh=m.get("h", st["mh"]))
    return st


def build_city_walls(mb, walls, gate, place, rng):
    """Each spec entry is a centre line (outside of the city on its right) with its own height and
    thickness.  Entries meet end to end: the taller / thicker one closes the joint with a full end
    face, the other stops against it.  An end at a gate-tower corner stops flush with that face."""
    gring = [tuple(p) for p in gate["ring"]] if gate else []
    ents = []
    for w in walls:
        pts = [tuple(p) for p in w["pts"]]
        if w.get("outside") == "left":
            pts = pts[::-1]
        ents.append((w, pts))
    tallest = max(range(len(ents)), key=lambda j: ents[j][0]["height"]) if ents else -1

    def dominant(j, k):
        a, b = ents[j][0], ents[k][0]
        return (a["height"], a["thick"], -j) > (b["height"], b["thick"], -k)

    for j, (w, pts) in enumerate(ents):
        H, T = w["height"], w["thick"]
        segs = [Edge(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        if not segs:
            continue
        kstart, kend = [0.0] * len(segs), [0.0] * len(segs)
        for i in range(len(segs) - 1):                     # interior joints: mitre along the mean normal
            a, b = segs[i], segs[i + 1]
            jd = (a.n + b.n).normalized()
            kend[i] = jd.dot(a.t) / jd.dot(a.n) if abs(jd.dot(a.n)) > 1e-6 else 0.0
            kstart[i + 1] = jd.dot(b.t) / jd.dot(b.n) if abs(jd.dot(b.n)) > 1e-6 else 0.0
        caps = ["full", "full"]
        gate_end = None
        for end, p in ((0, pts[0]), (1, pts[-1])):
            sg = segs[0] if end == 0 else segs[-1]
            gi = next((g for g in range(len(gring)) if math.dist(gring[g], p) < 0.5), None)
            if gi is not None:                             # flush with the gate face starting at that corner
                ge = Edge(gring[gi], gring[(gi + 1) % len(gring)])
                k = ge.t.dot(sg.t) / ge.t.dot(sg.n) if abs(ge.t.dot(sg.n)) > 1e-6 else 0.0
                if end == 0:
                    kstart[0] = k
                else:
                    kend[-1] = k
                caps[end] = "inner"
                gate_end = end
                continue
            for k2, (w2, pts2) in enumerate(ents):         # joint with another entry
                if k2 == j:
                    continue
                for end2, p2 in ((0, pts2[0]), (1, pts2[-1])):
                    if math.dist(p, p2) < 0.3:
                        s2 = Edge(pts2[0], pts2[1]) if end2 == 0 else Edge(pts2[-2], pts2[-1])
                        jd = (sg.n + s2.n).normalized()
                        kk = jd.dot(sg.t) / jd.dot(sg.n) if abs(jd.dot(sg.n)) > 1e-6 else 0.0
                        if end == 0:
                            kstart[0] = kk
                        else:
                            kend[-1] = kk
                        caps[end] = "full" if dominant(j, k2) else None
        st = wall_style(w, gate_end is not None, j == tallest)
        towers = w.get("towers") or []
        total = sum(s.L for s in segs)
        tw_on = []
        for tw in towers:
            s_abs = (total - tw["s"]) if gate_end == 1 else tw["s"]
            acc = 0.0
            for si, sg in enumerate(segs):
                if acc <= s_abs <= acc + sg.L:
                    tw_on.append((si, s_abs - acc, tw))
                    break
                acc += sg.L
        for si, sg in enumerate(segs):
            cuts = sorted((u - tw["w"] / 2, u + tw["w"] / 2, tw) for s_i, u, tw in tw_on if s_i == si)
            runs, u = [], 0.0
            for c0, c1, tw in cuts:
                runs.append((u, c0))
                u = c1
            runs.append((u, sg.L))
            for ri, (u0, u1) in enumerate(runs):
                first, last = ri == 0, ri == len(runs) - 1
                if u1 - u0 < 0.3:
                    continue
                ka = kstart[si] if first else 0.0
                kb = kend[si] if last else 0.0
                ca = caps[0] if (si == 0 and first) else None
                cb = caps[1] if (si == len(segs) - 1 and last) else None
                ua_o, ub_o = u0 + ka * T / 2, u1 + kb * T / 2
                hl = []
                if st["kind"] == "blind":                  # blind pointed arch, ~3 m from the gate corner
                    Lf = ub_o - ua_o
                    if Lf < 6.6:
                        c = (ua_o + ub_o) / 2
                    else:
                        c = ub_o - 3.0 if gate_end == 1 else ua_o + 3.0
                    wd = min(5.0, 2 * min(c - ua_o, ub_o - c) - 0.6)
                    if wd > 2.5:
                        hl.append(blind_arch(c - wd / 2, c + wd / 2, 0.0, 4.4, 2.3, 0.7, bench=(0.45, 0.45)))
                elif st["kind"] == "tall":                 # slits with oillets at mid-height, a few roundels
                    for f in (0.3, 0.7):
                        hl.append(slit_hole(ua_o + (ub_o - ua_o) * f, 0.45 * H, 0.45 * H + 1.7))
                else:
                    u = u0 + 3.5
                    while u < u1 - 3.0:                    # arrow slits along the face
                        if rng.random() < 0.7:
                            z0 = 4.8 + rng.uniform(-0.3, 0.3)
                            hl.append(slit_hole(u, z0, z0 + 1.6))
                        u += rng.uniform(5.5, 7.5)
                bat = wall_run(mb, sg, u0, u1, ka, kb, H, T, "fort", holes=hl, cap_a=ca, cap_b=cb,
                               batter=bool(w.get("batter")), cw=st["cw"], mw=st["mw"], cr=st["cr"], mh=st["mh"])
                if len(bat.merlons) > 2 and rng.random() < (u1 - u0) / 25.0:     # sparse dry tufts on top
                    a, b = bat.merlons[1 + int(rng.random() * (len(bat.merlons) - 2))]
                    place("weeds", bat.e.P((a + b) / 2, H, -GATE_PARAPET / 2), rng.uniform(0, 6.28), True)
            for s_i, u, tw in tw_on:
                if s_i == si:
                    wall_tower(mb, sg, u, tw["w"], tw["out"], T, tw.get("h", H + 2.0), "fort")


def gate_blocked(walls, gate):
    """Stretches of the gate faces covered by abutting wall ends: {edge: [(u0, u1)]}."""
    ring = [tuple(p) for p in gate["ring"]]
    out = {}
    for w in walls:
        pts = [tuple(p) for p in w["pts"]]
        for p, q in ((pts[0], pts[1]), (pts[-1], pts[-2])):
            gi = next((g for g in range(len(ring)) if math.dist(ring[g], p) < 0.5), None)
            if gi is None:
                continue
            for ei, at_start in ((gi, True), ((gi - 1) % len(ring), False)):
                ge = Edge(ring[ei], ring[(ei + 1) % len(ring)])
                d = Vector((q[0] - p[0], q[1] - p[1], 0)).normalized()
                if d.dot(ge.n) > 0.3:                      # the wall runs out in front of this face
                    half = w["thick"] / 2
                    out.setdefault(ei, []).append((0.0, half) if at_start else (ge.L - half, ge.L))
    return out


# ================================================================== Citadel
def railing(mb, a, b, z, gen, h=1.1, post_every=2.2):
    """Black steel fence of the moat (citadel_east.md A3): ~60 mm square posts every ~2.2 m, top rail,
    a second rail 0.15 m below it, a foot rail, round balusters (cut-out bar card) between them."""
    A, B = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
    t = B - A
    L = t.length
    if L < 0.2:
        return
    t.normalize()
    s = Vector((-t.y, t.x, 0))
    rect_uv = atlas_cell(gen, "cutout", ("rail_moat", "rail_balcony"))
    k = max(1, round(L / 1.6)) if rect_uv else 0
    for i in range(k):
        p0, p1 = A + t * (L * i / k), A + t * (L * (i + 1) / k)
        mk.card(mb, (p0 + p1) / 2 + UP * 0.08, t, UP, (p1 - p0).length, h - 0.1, "cut", rect_uv)   # "cut" is 2-sided
    n = max(1, round(L / post_every))
    for i in range(n + 1):
        p = A + t * (L * i / n)
        obox(mb, p, t, s, 0.06, 0.06, z, z + h + 0.03, "iron")
    for z0, z1, w in ((h - 0.02, h + 0.02, 0.05), (h - 0.18, h - 0.15, 0.03), (0.08, 0.11, 0.03)):
        obox(mb, (A + B) / 2, t, s, L, w, z + z0, z + z1, "iron", bottom=True)


def moat_wall(mb, eo, ring, i, z_floor, first, last, th=0.3, z_cop=0.15):
    """Street-side counterscarp along chain edge i (moat on its left): pale tooled ashlar down to
    the moat floor, a flat coping ~0.4 m wide raised ~0.15 m above the pavement (citadel_east.md A1)."""
    col = (1.0, 0.98, 0.93)
    n = len(ring)
    L = eo.L

    def k_at(start):
        if (start and first) or ((not start) and last):
            return 0.0
        ep = Edge(ring[(i - 1) % n], ring[i]) if start else Edge(ring[(i + 1) % n], ring[(i + 2) % n])
        bis = eo.n + ep.n
        if bis.length < 1e-6:
            return 0.0
        jd = bis.normalized()
        return jd.dot(eo.t) / jd.dot(eo.n) if abs(jd.dot(eo.n)) > 1e-6 else 0.0
    ka, kb = k_at(True), k_at(False)
    U = lambda u0, k, o: u0 + k * o                                 # noqa: E731
    z_cb = z_cop - 0.1
    for o, z0, z1, sgn in ((0.0, z_floor - 0.1, z_cb, -1), (th, -0.25, z_cb, 1)):
        mb.poly([eo.P(U(0, ka, o), z0, o), eo.P(U(L, kb, o), z0, o), eo.P(U(L, kb, o), z1, o),
                 eo.P(U(0, ka, o), z1, o)], "ashlar", eo.n * sgn, col=col)
    oa, ob = -0.05, th + 0.05                                       # coping slab
    q = [(oa, z_cb), (ob, z_cb), (ob, z_cop), (oa, z_cop)]
    for (o0, z0), (o1, z1), nrm in ((q[0], q[1], -UP), (q[1], q[2], eo.n), (q[2], q[3], UP), (q[3], q[0], -eo.n)):
        mb.poly([eo.P(U(0, ka, o0), z0, o0), eo.P(U(L, kb, o0), z0, o0), eo.P(U(L, kb, o1), z1, o1),
                 eo.P(U(0, ka, o1), z1, o1)], "ashlar", nrm, col=DRESSED)
    for u0, k, s, flag in ((0.0, ka, -1, first), (L, kb, 1, last)):  # open ends of a chain
        if flag:
            mb.poly([eo.P(U(u0, k, o), z, o) for o, z in
                     ((0.0, z_floor - 0.1), (th, -0.25), (th, z_cb), (ob, z_cb), (ob, z_cop), (oa, z_cop), (oa, z_cb),
                      (0.0, z_cb))], "ashlar", eo.t * s, col=col)


def toe_line(ring, idx, run, cut_a, cut_b):
    """Toe points of a slope of horizontal width `run` in front of ring edges idx (mitred joints,
    ends trimmed by the (point, direction) lines cut_a / cut_b, or square)."""
    n = len(ring)
    verts = [idx[0]] + [(i + 1) % n for i in idx]
    E = {i: Edge(ring[i], ring[(i + 1) % n]) for i in idx}
    toe = []
    for k, v in enumerate(verts):
        e_in = E.get((v - 1) % n) if k > 0 else None
        e_out = E.get(v) if k < len(verts) - 1 else None
        if e_in and e_out:
            p = line_x(e_in.A + e_in.n * run, e_in.t, e_out.A + e_out.n * run, e_out.t)
            toe.append(p if p is not None else e_out.A + e_out.n * run)
        else:
            e = e_out or e_in
            cut = cut_a if e_out else cut_b
            base = e.A + e.n * run
            p = line_x(base, e.t, Vector((*cut[0], 0)), Vector((*cut[1], 0))) if cut else None
            toe.append(p if p is not None else Vector((*ring[v], 0)) + e.n * run)
    return verts, E, toe


def glacis(mb, ring, idx, z_top, z_toe, run, cut_a, cut_b, mat="rubble", col=WEATHER, full_ends=False):
    """Steep rough-stone slope (60-70 deg) in front of consecutive ring edges idx, from the wall face
    at z_top down to the moat floor `run` metres out.  The ends are closed by vertical triangles
    (down to just below the street, or to the floor with full_ends)."""
    verts, E, toe = toe_line(ring, idx, run, cut_a, cut_b)
    for k, i in enumerate(idx):
        a, b = Vector((*ring[verts[k]], z_top)), Vector((*ring[verts[k + 1]], z_top))
        ta, tb = toe[k].to_2d().to_3d() + UP * z_toe, toe[k + 1].to_2d().to_3d() + UP * z_toe
        mb.poly([ta, tb, b, a], mat, E[i].n * (z_top - z_toe) + UP * run, col=col)
    for k in (0, len(verts) - 1):
        v = Vector((*ring[verts[k]], 0))
        t = toe[k].to_2d().to_3d()
        if full_ends:
            tri = [v + UP * z_top, v + UP * z_toe, t + UP * z_toe]
        else:
            frac = (z_top + 0.2) / (z_top - z_toe)
            tri = [v + UP * z_top, v + UP * -0.2, v.lerp(t, frac) + UP * -0.2]
        nrm = (t - v).cross(UP)
        e = E[idx[0]] if k == 0 else E[idx[-1]]
        if nrm.dot(e.t * (-1 if k == 0 else 1)) < 0:
            nrm = -nrm
        mb.poly(tri, mat, nrm, col=col)
    return toe


def herodian_band(mb, e, u0, u1, z0, z1, off, mat="ashlar", rng=None, col=HONEY, holes=()):
    """Huge Herodian blocks (citadel_east.md A5): courses ~1.0-1.1 m high, blocks 1.5-3 m long, rough
    projecting bosses inside sunken drafted margins.  holes: (u0, u1, z0, z1) boxes left free."""
    rng = rng or random.Random(3)
    z = z0
    course = 0
    while z + 0.6 < z1:
        h = min(1.05 + rng.uniform(-0.08, 0.08), z1 - z)
        u = u0 - (0.0 if course % 2 == 0 else rng.uniform(0.6, 1.4))
        while u < u1 - 0.3:
            L = 2.2 + rng.uniform(-0.7, 0.8)
            a, b = max(u, u0) + 0.08, min(u + L, u1) - 0.08
            if b - a > 0.5 and not any(a < hu1 and b > hu0 and z < hz1 and z + h > hz0 for hu0, hu1, hz0, hz1 in holes):
                bp = 0.08 + rng.uniform(0.0, 0.06)
                section_prism(mb, e, a, b, [(off, z + 0.08), (off + bp, z + 0.15), (off + bp, z + h - 0.15),
                                            (off, z + h - 0.08)], mat, skip=(3,),
                              col=tuple(c * rng.uniform(0.93, 1.04) for c in col))
            u += L
        z += h
        course += 1


def clip_convex(poly, lines):
    """Sutherland-Hodgman: keep the part of the convex CCW polygon on the inner side of each
    (point, outward normal) line."""
    pts = [Vector((p[0], p[1])) for p in poly]
    for P, nrm in lines:
        P, nrm = Vector((P[0], P[1])), Vector((nrm[0], nrm[1]))
        out = []
        for k in range(len(pts)):
            a, b = pts[k], pts[(k + 1) % len(pts)]
            da, db = (a - P).dot(nrm), (b - P).dot(nrm)
            if da <= 0:
                out.append(a)
            if (da < 0 < db) or (db < 0 < da):
                out.append(a + (b - a) * (da / (da - db)))
        pts = out
        if len(pts) < 3:
            return []
    return [(p.x, p.y) for p in pts]


def rect_ring(c, size, rot):
    t = Vector((math.cos(math.radians(rot)), math.sin(math.radians(rot)), 0))
    s = Vector((-t.y, t.x, 0))
    cc = Vector((c[0], c[1], 0))
    hl, hw = size[0] / 2, size[1] / 2
    return [tuple((cc + a * t * hl + b * s * hw).xy) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def fit_to_mass(rect, mass, proud=0.4):
    """Clip a tower rectangle where it runs out over the moat or the street: every mass-ring edge that
    the rectangle's centre lies behind (inside, projecting within the edge) and that the rectangle
    crosses limits it to `proud` m beyond that wall face."""
    lines = []
    cx = sum(p[0] for p in rect) / len(rect)
    cy = sum(p[1] for p in rect) / len(rect)
    for i in range(len(mass)):
        e = Edge(mass[i], mass[(i + 1) % len(mass)])
        if e.L < 2.0:
            continue
        uc, oc = e.u_of((cx, cy)), e.off_of((cx, cy))
        if not (0.0 < uc < e.L) or oc > 0.0:
            continue
        if max(e.off_of(p) for p in rect) <= proud:
            continue
        lines.append((tuple((e.A + e.n * proud).xy), tuple(e.n.xy)))
    return clip_convex(rect, lines) if lines else list(rect)


def corner_lobe(p, mass):
    """Smallest 4-vertex stretch of the mass ring (a corner lobe) whose quad contains point p."""
    n = len(mass)
    best = None
    for k in range(n):
        lobe = [mass[(k + d) % n] for d in (-1, 0, 1, 2)]
        a = mk.ring_area(lobe)
        if 40.0 < a < 900.0 and mk.point_in(p, lobe) and (best is None or a < best[0]):
            best = (a, lobe)
    return best[1] if best else None


def flag(mb, base, h, along, w=1.4, fh=0.95):
    """Flagpole with an Israeli flag (white field, two blue stripes) hanging out along `along`."""
    mk.cylinder(mb, base.x, base.y, base.z, base.z + h, 0.04, "metal_grey", seg=6)
    a = Vector((along.x, along.y, 0)).normalized()
    nrm = Vector((-a.y, a.x, 0))
    top = base + UP * (h - 0.1)
    for f0, f1, col in ((0.0, 0.12, (1.0, 1.0, 1.0)), (0.12, 0.27, (0.08, 0.2, 0.75)), (0.27, 0.73, (1.0, 1.0, 1.0)),
                        (0.73, 0.88, (0.08, 0.2, 0.75)), (0.88, 1.0, (1.0, 1.0, 1.0))):
        za, zb = top.z - fh * f1, top.z - fh * f0
        q = [Vector((top.x, top.y, za)) + a * 0.05, Vector((top.x, top.y, za)) + a * (w + 0.05),
             Vector((top.x, top.y, zb)) + a * (w + 0.05), Vector((top.x, top.y, zb)) + a * 0.05]
        mb.poly(q, "plastic", nrm, col=col)
        mb.poly(q[::-1], "plastic", -nrm, col=col)


def ring_rail(mb, ring, z, h=1.0, inset=0.25, post=2.0):
    """Modern black steel railing along a closed ring (tower roofs)."""
    inner = offset_ring(ring, inset)
    pts = [Vector((p[0], p[1], z + h)) for p in inner] + [Vector((inner[0][0], inner[0][1], z + h))]
    mk.tube(mb, pts, 0.025, "iron")
    mk.tube(mb, [p - UP * 0.5 for p in pts], 0.018, "iron")
    for k in range(len(inner)):
        a, b = Vector(inner[k]), Vector(inner[(k + 1) % len(inner)])
        m = max(1, round((b - a).length / post))
        for j in range(m):
            p = a.lerp(b, j / m)
            obox(mb, p, (b - a).normalized(), Vector((-(b - a).y, (b - a).x)).normalized(), 0.05, 0.05, z, z + h, "iron")


def phasael(mb, tw, mass, D, gen, rng):
    """Phasael ("David's Tower", NE corner): the spec rectangle fitted to the wall line, a steep
    stone skirt rising out of the moat, a band of smaller ashlar with small grilled windows, ~9
    courses of Herodian drafted blocks, ~18 courses of smaller later masonry with grilled windows,
    a slit and two oculi, a low notched parapet with a steel railing, and flags (citadel_east.md A5)."""
    ring = fit_to_mass(rect_ring(tw["c"], tw["size"], tw.get("rot", 0.0)), mass, 0.4)
    if len(ring) < 3:
        return None
    if mk.ring_area(ring) < 0:
        ring = ring[::-1]
    top = tw.get("top")
    Hm = tw["h"]
    Ht = Hm + (top["h"] if top else 0.0)
    n = len(ring)
    E = [Edge(ring[i], ring[(i + 1) % n]) for i in range(n)]
    exposed = [E[i].L > 1.5 and not mk.point_in(tuple(E[i].P(E[i].L / 2, 0, 0.8).xy), mass) for i in range(n)]
    north = max(range(n), key=lambda i: E[i].n.y)
    z_skirt, z_her0, z_her1 = 2.5, 6.0, 15.5
    zw, zs = Hm - 1.0, Hm - 0.3

    def holes(i, e):
        if e.L < 4.0:
            return []
        hs, keep = [], []
        if exposed[i]:
            for f in (0.3, 0.55, 0.8):                              # small grilled windows in the lower band
                u = e.L * f
                hs.append(dark_hole(rect(u - 0.3, u + 0.3, 4.0, 4.8), 0.3, grille_w=0.6, gen=gen))
        zg = Ht - 8.0
        for f in (0.3, 0.7):                                        # grilled windows in the upper zone
            u = e.L * f
            hs.append(dark_hole(rect(u - 0.4, u + 0.4, zg, zg + 1.0), 0.3, grille_w=0.8, gen=gen))
            keep.append((u - 0.5, u + 0.5, zg - 0.1, zg + 1.1))
        hs.append(slit_hole(e.L * 0.5, zg + 1.6, zg + 3.0, depth=0.3))
        if i == north:
            for f in (0.38, 0.62):
                hs.append(dark_hole(circle(e.L * f, Hm - 1.9, 0.25), 0.3))
        if exposed[i]:
            hs.append({"build": lambda mb_, e_: herodian_band(mb_, e_, 0.12, e_.L - 0.12, z_her0, z_her1, 0.0,
                                                               rng=rng)})
        return hs
    base = [(-D - 0.5) if exposed[i] else -0.6 for i in range(n)]
    battlemented_ring(mb, ring, base, zw, zs, Hm, 0.6, "fort", col=(0.92, 0.91, 0.9), holes=holes, cw=0.9, mw=1.3,
                      cr=0.35, slits=False)
    ring_rail(mb, ring, Hm)
    # steep stone skirt out of the moat in front of the exposed faces
    runs, cur = [], []
    i0 = next((i for i in range(n) if exposed[i] and not exposed[i - 1]), 0 if all(exposed) else None)
    if i0 is not None:
        for k in range(n):
            i = (i0 + k) % n
            if exposed[i]:
                cur.append(i)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
    for run in runs:
        ia, ib = run[0], run[-1]
        cut_a = (ring[ia], tuple(E[ia].n.xy))
        cut_b = (ring[(ib + 1) % n], tuple(E[ib].n.xy))
        glacis(mb, ring, run, z_skirt, -D - 0.05, 2.8, cut_a, cut_b, full_ends=True)     # ~70 deg, lawn stays
    if top:                                                         # set-back top storey with railing
        lines = [(tuple((e.A - e.n * 1.5).xy), tuple(e.n.xy)) for e in E]
        r2 = clip_convex(rect_ring(tw["c"], top["size"], tw.get("rot", 0.0)), lines)
        if len(r2) >= 3:
            if mk.ring_area(r2) < 0:
                r2 = r2[::-1]
            battlemented_ring(mb, r2, zw - 0.2, Ht - 1.0, Ht - 0.3, Ht, 0.5, "fort", col=(0.92, 0.91, 0.9),
                              cw=0.9, mw=1.3, cr=0.35, slits=False,
                              holes=lambda i, e: [dark_hole(pointed(e.L / 2 - 0.4, e.L / 2 + 0.4, zw + 0.4, zw + 1.6,
                                                                    0.5, 4), 0.4)] if e.L > 4 else [])
            ring_rail(mb, r2, Ht)
            se = max(r2, key=lambda p: p[0] - p[1])                  # flags at the SE part of the roof
            cse = Vector((sum(p[0] for p in r2) / len(r2), sum(p[1] for p in r2) / len(r2), 0))
            d = (Vector((se[0], se[1], 0)) - cse)
            for k, f in enumerate((0.75, 0.6)):
                flag(mb, cse + d * f + UP * (Ht - 1.0), 6.5 - k * 0.6, Vector((d.y, -d.x, 0)) if k else -d)
    return ring


def corner_tower(mb, lobe, mass, moat_of, H, D, gen, rng, H2=None, n_machi=3):
    """Citadel NW tower across the 1898 breach (gate.md 4): the corner lobe of the enceinte raised
    above the curtain in rough bossed masonry, three box machicolations on each outer face, a barred
    window and an oculus on the face towards the gate, slits with oillets."""
    ring = offset_ring(lobe, -0.36)
    n = len(ring)
    E = [Edge(ring[i], ring[(i + 1) % n]) for i in range(n)]
    exposed = [not mk.point_in(tuple(E[i].P(E[i].L / 2, 0, 0.8).xy), mass) for i in range(n)]
    H2 = H2 or H + 2.0
    zw, zs = H2 - 1.9, H2 - 1.25

    def holes(i, e):
        if not exposed[i]:
            return []
        nm = max(1, min(n_machi, 3 if e.L >= 12 else 2 if e.L >= 7 else 1))
        hs = [{"build": lambda mb_, e_, f=(k + 1) / (nm + 1): machicolation(mb_, e_, e_.L * f, H2 - 3.4, H2 - 0.3, 1.5,
                                                                              0.75, mat="rubble", col=RUSTIC,
                                                                              cap="flat")}
              for k in range(nm)]
        for k in range(nm + 1):
            u = e.L * (k + 0.5) / (nm + 1)
            hs.append(slit_hole(u, 6.0, 7.6, mat="rubble", col=RUSTIC))
        if i == towards_gate:
            hs.append(dark_hole(rect(e.L * 0.5 - 0.45, e.L * 0.5 + 0.45, 9.0, 10.2), 0.5, mat="rubble", col=RUSTIC,
                                grille_w=0.9, gen=gen))
            hs.append(dark_hole(circle(e.L * 0.5, 4.2, 0.35), 0.5, mat="rubble", col=RUSTIC))
        return hs
    gate_dir = Vector((-1.0, 1.0, 0)).normalized()
    towards_gate = max((i for i in range(n) if exposed[i]), key=lambda i: E[i].n.dot(gate_dir))
    base = [(-D - 0.5) if (exposed[i] and moat_of(E[i])) else (-0.6 if exposed[i] else H - CIT_WALK - 0.3)
            for i in range(n)]
    battlemented_ring(mb, ring, base, zw, zs, H2, 0.9, "rubble", col=RUSTIC, holes=holes, cw=1.7, mw=1.7, cr=0.7)
    return ring


def grille(mb, e, uc, z0, z1, w, gen, off=-0.12):
    if not gen:
        return
    gr = atlas_cell(gen, "cutout", ("grille",))
    if not gr:
        return
    mk.card(mb, e.P(uc, z0, off), e.t, UP, w, z1 - z0, "cut", gr)


def minaret(mb, cx, cy, z0, h, r, mat="fort"):
    """Ottoman minaret (1655): square base, banded cylindrical shaft, corbelled balcony with a
    railing, lantern and lead cap with a finial."""
    seg = 16
    zb = z0 + h * 0.36                                     # top of the square base (rises above the walls)
    obox(mb, (cx, cy), (1, 0, 0), (0, 1, 0), 2 * r + 0.7, 2 * r + 0.7, z0, zb, mat)
    cyl_top = z0 + h * 0.82
    nb = 6
    for k in range(nb):                                    # shaft registers divided by string courses
        a0 = zb + (cyl_top - zb) * k / nb
        a1 = zb + (cyl_top - zb) * (k + 1) / nb
        rr0 = r * (1 - 0.04 * k / nb)
        rr1 = r * (1 - 0.04 * (k + 1) / nb)
        mk.cylinder(mb, cx, cy, a0, a1 - 0.12, rr0, mat, seg=seg, cap=False, r1=rr1)
        mk.cylinder(mb, cx, cy, a1 - 0.12, a1, rr1 + 0.07, "ashlar", seg=seg, cap=False, col=DRESSED)
        ring_poly(mb, cx, cy, a1 - 0.12, rr1, rr1 + 0.07, seg, "ashlar", -UP, DRESSED)
        if k < nb - 1:
            ring_poly(mb, cx, cy, a1, rr1, rr1 + 0.07, seg, "ashlar", UP, DRESSED)
    rt = r * 0.96
    # muqarnas-like corbel ring and balcony slab
    mk.cylinder(mb, cx, cy, cyl_top, cyl_top + 0.5, rt + 0.07, "ashlar", seg=seg, cap=False, r1=rt + 0.65, col=DRESSED)
    mk.cylinder(mb, cx, cy, cyl_top + 0.5, cyl_top + 0.68, rt + 0.75, "ashlar", seg=seg, cap=False, col=DRESSED)
    ring_poly(mb, cx, cy, cyl_top + 0.5, rt + 0.65, rt + 0.75, seg, "ashlar", -UP, DRESSED)
    rl = rt * 0.68                                         # lantern
    ring_poly(mb, cx, cy, cyl_top + 0.68, rl, rt + 0.75, seg, "ashlar", UP, DRESSED)
    zl = cyl_top + 0.68
    for k in range(seg):                                   # balcony railing: posts + rail
        a = 2 * math.pi * (k + 0.5) / seg
        obox(mb, (cx + math.cos(a) * (rt + 0.62), cy + math.sin(a) * (rt + 0.62)), (math.cos(a + 1.57), math.sin(a + 1.57)),
             (math.cos(a), math.sin(a)), 0.05, 0.05, zl, zl + 0.95, "iron")
    pts = [Vector((cx + math.cos(2 * math.pi * k / seg) * (rt + 0.62), cy + math.sin(2 * math.pi * k / seg) * (rt + 0.62),
                   zl + 0.95)) for k in range(seg + 1)]
    mk.tube(mb, pts, 0.03, "iron", sides=4)
    mk.cylinder(mb, cx, cy, zl, zl + 2.3, rl, mat, seg=seg, cap=False)
    for k in range(4):                                     # lantern openings (dark)
        a = 2 * math.pi * k / 4 + math.pi / 4
        p = Vector((cx + math.cos(a) * (rl + 0.01), cy + math.sin(a) * (rl + 0.01), 0))
        tt = Vector((-math.sin(a), math.cos(a), 0))
        mb.poly([p - tt * 0.25 + UP * (zl + 0.5), p + tt * 0.25 + UP * (zl + 0.5), p + tt * 0.25 + UP * (zl + 1.8),
                 p - tt * 0.25 + UP * (zl + 1.8)], "void", Vector((math.cos(a), math.sin(a), 0)))
    zc = zl + 2.3
    mk.cylinder(mb, cx, cy, zc, zc + 0.2, rl + 0.25, "ashlar", seg=seg, cap=False, col=DRESSED)
    ring_poly(mb, cx, cy, zc, rl, rl + 0.25, seg, "ashlar", -UP, DRESSED)
    # lead cap: a pointed (ogee-ish) cone + finial
    prof = [(rl + 0.25, 0.2), (rl + 0.1, 0.55), (rl * 0.75, 1.1), (rl * 0.35, 1.7), (0.12, 2.1)]
    prev = None
    for rr, dz in prof:
        cur = [Vector((cx + math.cos(2 * math.pi * k / seg) * rr, cy + math.sin(2 * math.pi * k / seg) * rr, zc + dz))
               for k in range(seg + 1)]
        if prev:
            mb.quad_strip(prev, cur, "lead", lambda q: Vector((((q[0] + q[2]) / 2 - Vector((cx, cy, 0))).xy[:]) + (0.4,)))
        prev = cur
    mb.poly(prev[:-1], "lead", UP)
    mk.cylinder(mb, cx, cy, zc + 2.1, zc + 2.9, 0.05, "metal_grey", seg=6)
    for zz, rr in ((zc + 2.35, 0.13), (zc + 2.6, 0.1)):
        mk.cylinder(mb, cx, cy, zz - 0.07, zz + 0.07, rr, "metal_grey", seg=6)


def ring_poly(mb, cx, cy, z, r0, r1, seg, mat, nrm, col=None):
    for k in range(seg):
        a0, a1 = 2 * math.pi * k / seg, 2 * math.pi * (k + 1) / seg
        q = [(cx + math.cos(a0) * r0, cy + math.sin(a0) * r0, z), (cx + math.cos(a1) * r0, cy + math.sin(a1) * r0, z),
             (cx + math.cos(a1) * r1, cy + math.sin(a1) * r1, z), (cx + math.cos(a0) * r1, cy + math.sin(a0) * r1, z)]
        mb.poly(q, mat, nrm, col=col)


ENT_Z = 1.7                        # barbican podium / threshold above the square (citadel_east.md A6: 1.6-1.8 m)


def entrance_podium(mb, e, D, gen, span, sd, z0=ENT_Z):
    """Stone podium bridging the moat in front of the barbican door (citadel_east.md A6, photo A07):
    paved deck at z0 between parapets with black railings, an arch over the moat floor through it,
    and a broad stair of 9 steps running along the street edge of the moat, descending towards
    sd * e.t.  Returns the u-range along e that the deck covers (the moat railing stops there)."""
    uc = e.L / 2
    zt, pt, ph = z0, 0.4, 0.6
    ua, ub = uc - 2.6, uc + 2.6                            # deck between the parapets
    os_, oe = span + 0.56, span + 2.6                      # the stair lies between the coping and oe
    zp = zt + ph
    col = DRESSED
    u_full = ua - pt if sd > 0 else ub + pt                # outer face of the full-length side parapet
    u_stair = ub + pt if sd > 0 else ua - pt               # outer face of the stair-side parapet
    mb.poly([e.P(ua, zt, 0), e.P(ub, zt, 0), e.P(ub, zt, oe), e.P(ua, zt, oe)], "paving", UP)
    # and 1 cm lower 0.6 m on into the doorway (sky showed in the joint at the threshold; lower, it never
    # z-fights with a recess floor at the deck's level)
    mb.poly([e.P(ua, zt - 0.01, -0.6), e.P(ub, zt - 0.01, -0.6), e.P(ub, zt - 0.01, 0.0), e.P(ua, zt - 0.01, 0.0)],
            "paving", UP)
    arch = [(3.0, -D), (span - 0.1, -D)] + _seg_arch(3.0, span - 0.1, -D + 1.7, 0.9)
    full = [(0.0, -D - 0.1), (span, -D - 0.1), (span, -0.2), (oe + pt, -0.2), (oe + pt, zp), (0.0, zp)]
    short = [(0.0, -D - 0.1), (span, -D - 0.1), (span, -0.2), (os_, -0.2), (os_, zp), (0.0, zp)]
    face(mb, BridgeFrame(e, u_full, -sd), full, "fort", 0.0, holes=[arch])
    face(mb, BridgeFrame(e, u_stair, sd), short, "fort", 0.0, holes=[arch])
    tunnel(mb, BridgeFrame(e, ua - pt, -1), arch, 0.0, -(ub - ua + 2 * pt), "fort")
    fa, fb = (ua - pt, ua) if sd > 0 else (ub, ub + pt)     # parapet tops: full side, street end, stair side
    sa, sb = (ub, ub + pt) if sd > 0 else (ua - pt, ua)
    for (u0, u1, o0, o1) in ((fa, fb, 0.0, oe + pt), (ua, ub, oe, oe + pt), (sa, sb, 0.0, os_)):
        mb.poly([e.P(u0, zp, o0), e.P(u1, zp, o0), e.P(u1, zp, o1), e.P(u0, zp, o1)], "ashlar", UP, col=col)
    u_fi = ua if sd > 0 else ub                            # inner faces of the parapets
    u_si = ub if sd > 0 else ua
    mb.poly([e.P(u_fi, zt, 0), e.P(u_fi, zt, oe), e.P(u_fi, zp, oe), e.P(u_fi, zp, 0)], "fort", e.t * sd)
    mb.poly([e.P(ua, zt, oe), e.P(ub, zt, oe), e.P(ub, zp, oe), e.P(ua, zp, oe)], "fort", -e.n)
    mb.poly([e.P(u_si, zt, 0), e.P(u_si, zt, os_), e.P(u_si, zp, os_), e.P(u_si, zp, 0)], "fort", -e.t * sd)
    mb.poly([e.P(sa, zt, os_), e.P(sb, zt, os_), e.P(sb, zp, os_), e.P(sa, zp, os_)], "fort", e.n)
    mb.poly([e.P(u_si, -0.2, oe), e.P(u_si, -0.2, oe + pt), e.P(u_si, zp, oe + pt), e.P(u_si, zp, oe)], "fort",
            e.t * sd)
    mb.poly([e.P(u_full, -0.2, oe + pt), e.P(u_si, -0.2, oe + pt), e.P(u_si, zp, oe + pt), e.P(u_full, zp, oe + pt)],
            "fort", e.n)
    for (uu, o0, o1) in (((fa + fb) / 2, 0.15, oe + pt - 0.15), ((sa + sb) / 2, 0.15, os_ - 0.1)):
        railing(mb, e.P(uu, 0, o0).xy, e.P(uu, 0, o1).xy, zp, gen, h=1.0)
    railing(mb, e.P(ua + 0.1, 0, oe + pt / 2).xy, e.P(ub - 0.1, 0, oe + pt / 2).xy, zp, gen, h=1.0)
    nst, tr = 9, 0.32
    r = zt / nst
    for k in range(nst):                                   # the stair, beside the deck on the street
        zk_top = zt - k * r
        zk = zt - (k + 1) * r if k < nst - 1 else -0.2
        u = u_si + sd * k * tr
        mb.poly([e.P(u, zk, os_), e.P(u, zk, oe), e.P(u, zk_top, oe), e.P(u, zk_top, os_)], "ashlar", e.t * sd,
                col=col)
        if k < nst - 1:
            u2 = u + sd * tr
            mb.poly([e.P(u, zk, os_), e.P(u2, zk, os_), e.P(u2, zk, oe), e.P(u, zk, oe)], "ashlar", UP, col=col)
            for o, sg in ((os_, -1), (oe, 1)):
                mb.poly([e.P(u, -0.2, o), e.P(u2, -0.2, o), e.P(u2, zk, o), e.P(u, zk, o)], "ashlar", e.n * sg,
                        col=col)
    top = e.P(u_stair + sd * 0.05, zt + 0.95, os_ + 0.12)  # black handrail on the moat side of the stair
    bot = e.P(u_si + sd * (nst - 1) * tr, r + 0.95, os_ + 0.12)
    mk.tube(mb, [top, bot, bot + e.t * (0.3 * sd)], 0.025, "iron")
    for f in (0.0, 0.5, 1.0):
        p = top.lerp(bot, f)
        obox(mb, p, e.t, e.n, 0.05, 0.05, p.z - 0.95, p.z, "iron")
    return min(ua - pt, ub + pt) - 0.05, max(ua - pt, ub + pt) + 0.05


def stair_clear(e, span, sd, outer):
    """True when the podium stair (descending towards sd * e.t) stays off the moat (outside `outer`)."""
    uc = e.L / 2
    u_si = uc + 2.6 if sd > 0 else uc - 2.6
    for k in range(10):
        for o in (span + 0.56, span + 2.6):
            if mk.point_in(tuple(e.P(u_si + sd * k * 0.32, 0, o).xy), outer):
                return False
    return True


def _seg_arch(a, b, vs, rise, seg=6):
    w = b - a
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = vs + rise - R
    a0 = math.asin((w / 2) / R)
    return [((a + b) / 2 + math.sin(-a0 + 2 * a0 * k / seg) * R * -1, cz + math.cos(-a0 + 2 * a0 * k / seg) * R)
            for k in range(seg + 1)]


class BridgeFrame(Edge):
    """Frame for a podium side wall: u = offset from the citadel face, off along s * e.t."""

    def __init__(self, e, u_at, s):
        self.A = e.P(u_at, 0.0, 0.0)
        self.t = e.n
        self.n = e.t * s
        self.L = 0.0


def barbican_door(mb, e, uc, z0, gen):
    """North face of the barbican (citadel_east.md A6): tall pointed recess (~4.5 m wide, apex ~6.5 m
    above the podium) with a moulded hood, a pointed doorway ~2.4 x 3.5 m with studded olive-brown
    wooden doors, and a smaller blind pointed niche to its left (east)."""
    rec = pointed(uc - 2.25, uc + 2.25, z0, z0 + 3.6, 2.9, 7)
    door = pointed(uc - 1.2, uc + 1.2, z0, z0 + 2.3, 1.2, 6)
    tunnel(mb, e, rec, 0.0, -0.6, "fort")
    face(mb, e, rec, "fort", -0.6, holes=[door])
    tunnel(mb, e, door, -0.6, -0.9, "fort")
    rect_uv = atlas_cell(gen, "doors", OAK_CELLS)
    for lo, hi in ((uc - 1.2, uc), (uc, uc + 1.2)) if rect_uv else ():   # two leaves, one half of the cell each
        half = [p for p in door if lo - 1e-6 <= p[0] <= hi + 1e-6] + [(uc, z0)]
        poly = sorted(half, key=lambda p: math.atan2(p[1] - (z0 + 1.5), p[0] - (lo + hi) / 2))
        try:
            fl, ft = mk.tess2d([poly])
        except Exception:                                  # noqa: BLE001
            continue
        pts = [e.P(u, z, -0.9) for u, z in fl]
        u0r, u1r = (rect_uv[0], (rect_uv[0] + rect_uv[2]) / 2) if lo < uc else ((rect_uv[0] + rect_uv[2]) / 2, rect_uv[2])
        for a_, b_, c_ in ft:
            uvs = [(u0r + (fl[k][0] - lo) / 1.2 * (u1r - u0r), rect_uv[1] + (fl[k][1] - z0) / 3.5 * (rect_uv[3] - rect_uv[1]))
                   for k in (a_, b_, c_)]
            mb.poly([pts[a_], pts[b_], pts[c_]], "doors", e.n, uv=uvs, col=OAK_COL)
    ot = pointed_top(uc - 2.6, uc + 2.6, z0 + 3.6, 3.25, 7)
    it = pointed_top(uc - 2.25, uc + 2.25, z0 + 3.6, 2.9, 7)
    face(mb, e, ot + it[::-1], "ashlar", 0.1, col=DRESSED)
    cc = e.P(uc, z0 + 3.6)
    strip(mb, e, ot, 0.0, 0.1, "ashlar", lambda p, q: e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) - cc, DRESSED)
    strip(mb, e, it, 0.0, 0.1, "ashlar", lambda p, q: cc - e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), DRESSED)
    for ua_, ub_ in ((uc + 2.25, uc + 2.6), (uc - 2.6, uc - 2.25)):
        mb.poly([e.P(ua_, z0 + 3.6, 0), e.P(ub_, z0 + 3.6, 0), e.P(ub_, z0 + 3.6, 0.1), e.P(ua_, z0 + 3.6, 0.1)],
                "ashlar", -UP, col=DRESSED)
    obox(mb, e.P(uc - 1.9, 0, 0.02), e.t, e.n, 0.7, 0.04, z0 + 1.2, z0 + 2.1, "metal_dark", bottom=True,
         skip_sides=(0,))                                  # black framed notice plaque beside the door


def build_citadel(mb, c, gen, place, rng):
    mass = [tuple(p) for p in c["mass"]]
    court = [tuple(p) for p in c["inner"]]
    outer = [tuple(p) for p in c["outer"]]
    H, D = c["wall_h"], c["moat_depth"]
    me = c["moat_edges"]
    n = len(mass)
    zw, zs = H - CIT_WALK, H - CIT_SILL
    moat = [me[i] > 0 for i in range(n)]
    E = [Edge(mass[i], mass[(i + 1) % n]) for i in range(n)]
    mid = lambda i: E[i].P(E[i].L / 2, 0)                          # noqa: E731
    # the entrance: the barbican's north face (short moat edge facing the square, furthest east)
    ent = c.get("entrance_edge")
    if ent is None:
        cands = [i for i in range(n) if moat[i] and 6.0 < E[i].L < 18.0 and E[i].n.y > 0.7]
        ent = max(cands, key=lambda i: mid(i).x) if cands else None
    barb = set()
    if ent is not None:
        barb = {ent} | {(ent + d) % n for d in (-2, -1, 1, 2)
                        if moat[(ent + d) % n] and E[(ent + d) % n].L < 14.0 and (mid((ent + d) % n) - mid(ent)).length < 15}
    styles = ["pointed" if i in barb else "flat" for i in range(n)]
    eg = c.get("edge_ground") or [0.0] * n                        # the ground just outside each edge
    base = [(-D - 0.5) if moat[i] else min(-0.6, eg[i] - 0.6) for i in range(n)]
    state = {}

    def holes(i, e):
        hs = []
        if i == ent:
            uc = e.L / 2
            rec = pointed(uc - 2.25, uc + 2.25, ENT_Z, ENT_Z + 3.6, 2.9, 7)

            def build(mb_, e_, uc=uc):
                barbican_door(mb_, e_, uc, ENT_Z, gen)
                sd = 1 if stair_clear(e_, me[ent], 1, outer) else -1
                state["gap"] = (e_, entrance_podium(mb_, e_, D, gen, me[ent], sd))
            hs.append({"ol": rec, "build": build})
            if uc - 4.2 > 0.5:                                     # smaller blind niche left of the door
                hs.append(blind_arch(uc - 4.2, uc - 3.35, ENT_Z, ENT_Z + 1.8, 0.5, 0.35, dress=False))
        elif e.L > 6.0:                                            # two rows of keyhole slits, staggered
            for row, (z0, z1, ph) in enumerate(((zw - 2.9, zw - 1.4, 0.0), (zw - 6.6, zw - 5.1, 3.0))):
                if row == 1 and moat[i] and zw - 6.6 < 2.5:
                    continue
                u = 2.5 + ph
                while u < e.L - 2.5:
                    if rng.random() < 0.75:
                        hs.append(slit_hole(u, z0, z1))
                    u += rng.uniform(5.5, 7.0)
        if i in barb:                                              # corbel frieze under the merlons
            hs.append({"build": lambda mb_, e_: section_prism(
                mb_, e_, 0.05, e_.L - 0.05, [(0, zw - 0.75), (0.1, zw - 0.65), (0.1, zw - 0.35), (0, zw - 0.3)],
                "ashlar", skip=(3,), col=DRESSED, ends=False)})
        return hs

    E, inner_par, bats = battlemented_ring(mb, mass, base, zw, zs, H, 0.8, "fort", style=styles, cw=1.7, mw=1.7,
                                           cr=0.7, holes=holes, roof=False, slit_every=1,
                                           layout=lambda i: (1.2, 1.1, 0.8) if i in barb else None)
    try:                                                           # enceinte roof between parapet and courtyard
        fl, ft = mk.tess2d([inner_par, court])
        mb.tris([(p[0], p[1], zw) for p in fl], ft, "fort", UP)
    except Exception:                                              # noqa: BLE001
        pass
    nc = len(court)
    for i in range(nc):                                            # courtyard faces with a blind arcade
        a, b = court[(i + 1) % nc], court[i]
        e = Edge(a, b)
        L = e.L
        hl = []
        u = 2.2
        while u + 3.0 < L:
            hl.append(pointed(u, u + 2.6, 1.0, 3.6, 1.6, 5))
            u += 4.4
        face(mb, e, [(0, 0.9), (L, 0.9), (L, zw), (0, zw)], "fort", 0.0, holes=hl)
        for ol in hl:
            tunnel(mb, e, ol, 0.0, -0.9, "fort", floor=False)
            face(mb, e, ol, "void", -0.9)
    # ---- moat: glacis, street-side counterscarp with coping and railing
    runs = []
    i0 = next((i for i in range(n) if moat[i] and not moat[i - 1]), None)
    if i0 is not None:
        cur = []
        for k in range(n):
            i = (i0 + k) % n
            if moat[i]:
                cur.append(i)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
    no = len(outer)
    for run in runs:
        ia, ib = run[0], run[-1]
        cut_a = (mass[ia], tuple(Edge(outer[(ia - 1) % no], outer[ia]).t.xy))
        cut_b = (mass[(ib + 1) % n], tuple(Edge(outer[(ib + 1) % no], outer[(ib + 2) % no]).t.xy))
        # (topping out below the street: at 1.5 m it stood over the moat railing as a pale 2 m plinth in front
        #  of the wall, where Street View shows the wall rising straight from behind the railing)
        glacis(mb, mass, run, -0.5, -D - 0.05, 2.4, cut_a, cut_b)
        chain = [mass[ia]] + [outer[i] for i in run] + [outer[(ib + 1) % no], mass[(ib + 1) % n]]
        chain = [p for k, p in enumerate(chain) if k == 0 or math.dist(p, chain[k - 1]) > 0.2]
        for k in range(len(chain) - 1):
            eo = Edge(chain[k], chain[k + 1])
            first, last = k == 0, k == len(chain) - 2
            moat_wall(mb, eo, chain, k, -D, first, last)
            p0, p1 = 0.1 if first else 0.0, eo.L - (0.1 if last else 0.0)
            spans = [(p0, p1)]
            if "gap" in state:
                e_m, (g0, g1) = state["gap"]
                if abs(eo.t.cross(e_m.t).z) < 0.2 and abs(eo.off_of(e_m.P(g0, 0)) + me[ent]) < 1.5:
                    ga, gb = sorted((eo.u_of(e_m.P(g0, 0)), eo.u_of(e_m.P(g1, 0))))
                    if ga < p1 and gb > p0:
                        spans = [(p0, min(p1, ga)), (max(p0, gb), p1)]
            for a_, b_ in spans:
                if b_ - a_ > 0.3:
                    railing(mb, eo.P(a_, 0, 0.15).xy, eo.P(b_, 0, 0.15).xy, 0.15, gen)
    # ---- towers: Phasael, box towers and the minaret from the spec (fallback NW tower from the outline)
    def moat_of(ee):
        return any(moat[j] and abs(E[j].t.cross(ee.t).z) < 0.2 and abs(E[j].off_of(ee.P(ee.L / 2, 0))) < 1.0
                   for j in range(n))
    spec_boxes = []
    for tw in c.get("towers", []):
        cx, cy = tw["c"]
        if tw["kind"] in ("box", "phasael"):
            if tw["kind"] == "phasael" or tw.get("herodian") or "phasael" in tw.get("name", ""):
                ring = phasael(mb, tw, mass, D, gen, rng)
            else:
                lobe = corner_lobe((cx, cy), mass)
                if lobe:                       # a corner tower (e.g. the NW tower): raise that corner lobe
                    corner_tower(mb, lobe, mass, moat_of, H, D, gen, rng, H2=tw["h"],
                                 n_machi=tw.get("machicolations", 3))
                else:                          # free-standing box, fitted to the wall faces
                    ring = fit_to_mass(rect_ring(tw["c"], tw["size"], tw.get("rot", 0.0)), mass, 0.36)
                    if len(ring) >= 3:
                        if mk.ring_area(ring) < 0:
                            ring = ring[::-1]
                        nmach = tw.get("machicolations", 1)
                        battlemented_ring(mb, ring, -D - 0.5, tw["h"] - CIT_WALK, tw["h"] - CIT_SILL, tw["h"], 0.9,
                                          "rubble", col=RUSTIC, holes=lambda i, e: [
                                              {"build": lambda mb_, e_, f=(k + 1) / (nmach + 1): machicolation(
                                                  mb_, e_, e_.L * f, tw["h"] - 3.4, tw["h"] - 0.3, mat="rubble",
                                                  col=RUSTIC, cap="flat")} for k in range(nmach)] if e.L > 6 else [])
            spec_boxes.append((cx, cy))
        elif tw["kind"] == "minaret":
            minaret(mb, cx, cy, 1.0, tw["h"], tw["r"])
    if c.get("corner_tower", True):          # fallback when the spec has no tower at the gate-side corner
        gate_c = Vector(c.get("gate_xy", (2.9, -4.0)))
        k = min(range(n), key=lambda i: (Vector(mass[i]) - gate_c).length)
        lobe = [mass[(k + d) % n] for d in (-1, 0, 1, 2)]
        if mk.ring_area(lobe) > 0 and not any(mk.point_in(p, lobe) for p in spec_boxes):
            corner_tower(mb, lobe, mass, moat_of, H, D, gen, rng)
    # ---- a few dry tufts on merlon tops
    for i in range(n):
        bat = bats[i]
        if i not in barb and len(bat.merlons) > 2 and rng.random() < E[i].L / 40.0:
            a, b = bat.merlons[1 + int(rng.random() * (len(bat.merlons) - 2))]
            place("weeds", bat.e.P((a + b) / 2, H, -0.4), rng.uniform(0, 6.28), True)


# ================================================================== entry point
def build(mbs, spec, gen, place):
    """mbs: dict of MeshBuilders by object name -> filled in place."""
    rng = random.Random(1538)
    for mb in mbs.values():
        mb.tile = dict(mb.tile, fort=FORT_TILE)
    build_gatehouse(mbs["jaffa_gate"], spec["gatehouse"], place, rng, gen,
                    blocked=gate_blocked(spec["city_walls"], spec["gatehouse"]))
    build_city_walls(mbs["city_wall"], spec["city_walls"], spec.get("gatehouse"), place, rng)
    build_citadel(mbs["citadel"], spec["citadel"], gen, place, rng)
    for name, mb in mbs.items():
        tint_planes(mb, "fort", FORT_COL.get(name, (0.95, 0.95, 0.97)))


def tint_planes(mb, mat, base, var=0.03):
    """Vertex colour for untinted faces of `mat`: a base tint (less orange than the raw texture)
    varied per plane, so every triangle of one wall face gets the same colour."""
    if mat not in mb.mat_names:
        return
    k = mb.mat_names.index(mat)
    for i, (m, c, f) in enumerate(zip(mb.mats, mb.cols, mb.faces)):
        if m != k or c != mk.WHITE:
            continue
        a, b, cc = (mb.verts[j] for j in f[:3])
        n = (b - a).cross(cc - a)
        if n.length < 1e-12:
            continue
        n.normalize()
        key = (round(n.x * 20), round(n.y * 20), round(n.z * 20), round(n.dot(a) / 1.5))
        h = (hash(key) & 0xFFFF) / 0xFFFF - 0.5
        g = 1.0 + 2 * var * h
        mb.cols[i] = (base[0] * g, base[1] * g, base[2] * (g * 0.7 + 0.3))
