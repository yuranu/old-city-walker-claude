"""City wall, Jaffa Gate tower and the Citadel (Tower of David).

    build(mbs, spec, gen, place)
        mbs    {"jaffa_gate", "city_wall", "citadel"}: MeshBuilders filled in place
        spec   scene spec ("gatehouse", "city_walls", "citadel")
        gen    generated-atlas manifest (cut-out railing cells)
        place  place(type, Vector pos, yaw_radians, nocol) instances library props (capers, weeds)

Reference photos and the measurements taken from them: data/reference/fort_notes.md.

Every wall face is ONE polygon per edge whose top outline already carries the crenellation
(merlons are not boxes stacked on the wall): no coplanar overlaps, no T-junctions, and arrow
slits / gate arches are real holes in that polygon (meshkit.tess2d) with reveals behind them.
Corner merlons are single L-shaped tops shared by both edges, so rows never overlap at corners.

Frames: an Edge(a, b) of a CCW ring has u along a->b, z up and `off` along the outward normal
(right of a->b). Inner faces (parapet backs, the gate chamber, the courtyard) use negative offsets.
"""
import math
import random

from mathutils import Vector

import meshkit as mk

UP = Vector((0, 0, 1))
DRESSED = (1.0, 0.98, 0.94)        # mouldings, roundels, inscription (lighter dressed stone)
WEATHER = (0.93, 0.9, 0.85)        # rubble glacis
IRON_DOOR = (0.55, 0.6, 0.6)       # grey-green iron-plated gate leaves (metal_grey * tint)

# ------------------------------------------------------------------ dimensions (fort_notes.md)
GATE_PARAPET = 0.8                 # parapet thickness on the gate tower
GATE_WALK = 2.4                    # wall walk below the merlon top
GATE_SILL = 1.25                   # crenel sill below the merlon top
WALL_WALK = 2.3
WALL_SILL = 1.2
CIT_WALK = 2.4
CIT_SILL = 1.25
BATTER_H, BATTER_D = 1.5, 0.3      # battered plinth of the city wall


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
    """Planar face in the plane of edge e at offset `off`: outline + holes given in (u, z)."""
    try:
        flat, tris = mk.tess2d([list(outline)] + [list(h) for h in holes])
    except Exception:                                   # noqa: BLE001
        return
    mb.tris([e.P(u, z, off) for u, z in flat], tris, mat, -e.n if inward else e.n, col=col)


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
    mb.poly([e.P(u, z, off + depth) for u, z in ring], mat, e.n, col=col)
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
            obox(mb, e.P((a + b) / 2, 0, -d / 2), e.t, e.n, 0.16, 0.16, self.zt - 0.06, self.zt + 0.28, mat, col=col)


def battlemented_ring(mb, ring, base, z_walk, z_sill, z_top, d, mat, col=None, style="flat", cw=1.6, mw=1.7,
                      cr=0.8, holes=None, roof=True, roof_holes=(), slits=True, slit_every=1, extras=None):
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
        c0 = max(cw, uin[i][0] + 0.45)
        c1 = max(cw, e.L - uin[i][1] + 0.45)
        bats.append(Battlement(e, 0.0, e.L, uin[i][0], uin[i][1], z_walk, z_sill, z_top, d, c0, c1, mw, cr, st,
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
    if roof:
        fl, ft = mk.tess2d([inner] + [list(h) for h in roof_holes])
        mb.tris([(p[0], p[1], z_walk) for p in fl], ft, mat, UP, col=col)
    return E, inner, bats


def batter_ring(mb, ring, z0, z1, proj, mat, col=None):
    """Sloping plinth around a closed ring: from `proj` outside the face at z0 up to the face at z1."""
    out = offset_ring(ring, -proj)
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        q = [(*out[i], z0), (*out[j], z0), (*ring[j], z1), (*ring[i], z1)]
        e = Edge(ring[i], ring[j])
        mb.poly(q, mat, e.n * (z1 - z0) + UP * proj, col=col)


def slit_hole(u, z0, z1, w=0.2, depth=0.6, mat="fort", col=None):
    ol = rect(u - w / 2, u + w / 2, z0, z1)

    def build(mb, e, ol=ol):
        tunnel(mb, e, ol, 0.0, -depth, mat, floor=False, col=col)
        face(mb, e, ol, "void", -depth)
    return {"ol": ol, "build": build}


def blind_arch(u0, u1, z0, vs, rise, depth, mat="fort", col=None, bench=None):
    ol = pointed(u0, u1, z0, vs, rise, 6)

    def build(mb, e, ol=ol):
        tunnel(mb, e, ol, 0.0, -depth, mat, floor=z0 <= 0.0, col=col)
        face(mb, e, ol, mat, -depth, col=col)
        if bench:
            bh, bd = bench
            section_prism(mb, e, u0, u1, [(-depth, z0), (-depth + bd, z0), (-depth + bd, z0 + bh), (-depth, z0 + bh)],
                          "ashlar", skip=(3,), col=DRESSED, ends=False)
    return {"ol": ol, "build": build}


# ================================================================== Jaffa Gate tower
def portal(mb, e, uc, P, depth_total, mat, outer=True):
    """The recessed pointed-arch portal of the Jaffa Gate (both faces share the composition):
    moulded arch frame ending in volutes, roundels, a recessed tympanum with a cornice (and the
    inscription panel on the outer face), the flat doorway with rounded corners, the door frame,
    a step out to the taller pointed passage arch and the open iron-plated door leaves."""
    rw, rs, rr, rd = P["recess_w"], P["recess_spring"], P["recess_rise"], P["recess_d"]
    dw, dh, dr = P["door_w"], P["door_h"], P["door_r"]
    pw, ps, pr = P["pass_w"], P["pass_spring"], P["pass_rise"]
    frame_d = P["frame_d"]
    r0, r1 = uc - rw / 2, uc + rw / 2
    recess = pointed(r0, r1, 0.0, rs, rr, 7)
    door = shouldered(uc - dw / 2, uc + dw / 2, 0.0, dh, dr)
    pas = pointed(uc - pw / 2, uc + pw / 2, 0.0, ps, pr, 6)
    tunnel(mb, e, recess, 0.0, -rd, mat)                                       # recess reveal
    face(mb, e, u_shape(recess, door), mat, -rd)                               # tympanum + jambs
    tunnel(mb, e, door, -rd, -rd - frame_d, mat)                               # door frame
    face(mb, e, u_shape(pas, door), mat, -rd - frame_d, inward=True)           # rebate step
    tunnel(mb, e, pas, -rd - frame_d, -depth_total, mat)                       # passage to the chamber
    # moulded frame: a band around the arch only, ending in small volutes at the springing
    bw, bp = 0.42, 0.11
    outer_top = pointed_top(r0 - bw, r1 + bw, rs, rr + bw * 1.12, 7)
    inner_top = pointed_top(r0, r1, rs, rr, 7)
    band = outer_top + inner_top[::-1]
    face(mb, e, band, "ashlar", bp, col=DRESSED)
    c = e.P(uc, rs)
    strip(mb, e, outer_top, 0.0, bp, "ashlar", lambda p, q: e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) - c, DRESSED)
    strip(mb, e, inner_top, 0.0, bp, "ashlar", lambda p, q: c - e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), DRESSED)
    for u_a, u_b in ((r1, r1 + bw), (r0 - bw, r0)):
        mb.poly([e.P(u_a, rs, 0), e.P(u_b, rs, 0), e.P(u_b, rs, bp), e.P(u_a, rs, bp)], "ashlar", -UP, col=DRESSED)
    for u_v in (r0 - bw * 0.55, r1 + bw * 0.55):
        disc(mb, e, u_v, rs - 0.1, 0.15, bp + 0.04, "ashlar", seg=8, col=DRESSED)
    for u_v in (r0 - bw - 0.75, r1 + bw + 0.75):                                # rosettes at the springing
        disc(mb, e, u_v, rs + 0.05, 0.36, 0.05, "ashlar", seg=10, col=DRESSED)
        disc(mb, e, u_v, rs + 0.05, 0.2, 0.09, "ashlar", seg=8, col=DRESSED)
    apex = rs + rr + bw * 1.12
    disc(mb, e, uc, apex + 0.36, 0.2, 0.06, "ashlar", seg=8, col=DRESSED)
    # tympanum: cornice above the doorway lintel (and the inscription on the outer face)
    zc = dh + 0.75
    hw = pointed_halfwidth(rw, rs, rr, zc + 0.22) - 0.02
    section_prism(mb, e, uc - hw, uc + hw, [(-rd, zc), (-rd + 0.1, zc), (-rd + 0.17, zc + 0.12),
                                            (-rd + 0.17, zc + 0.22), (-rd, zc + 0.22)],
                  "ashlar", skip=(4,), col=DRESSED)
    if outer:
        z0, z1, iw = zc + 0.55, zc + 1.4, min(2.3, 2 * pointed_halfwidth(rw, rs, rr, zc + 1.45) - 0.5)
        o = -rd
        obox(mb, e.P(uc, 0, o + 0.03), e.t, e.n, iw, 0.06, z0, z1, "ashlar", col=(0.9, 0.87, 0.8), bottom=True,
             skip_sides=(0,))
        for k in range(3):                                                     # three lines of thuluth
            zl = z0 + 0.12 + k * 0.26
            obox(mb, e.P(uc, 0, o + 0.065), e.t, e.n, iw - 0.24, 0.012, zl, zl + 0.15, "ashlar",
                 col=(0.72, 0.68, 0.6), bottom=True, skip_sides=(0,))
        for s in (-1, 1):                                                      # flanking roundels
            disc(mb, e, uc + s * (iw / 2 + 0.3), (z0 + z1) / 2, 0.2, 0.05, "ashlar", off=o, seg=8, col=DRESSED)
    # door leaves standing open in the passage (hinged behind the door frame, ~75 deg open)
    hinge_off = -rd - frame_d - 0.05
    lw, lh, lt = dw / 2, min(dh - dr, ps + 0.4), 0.1
    for s in (-1, 1):
        hu = uc + s * (pw / 2 - 0.12)
        ang = math.radians(15)
        dirv = -e.n * math.cos(ang) - e.t * s * math.sin(ang)
        side = Vector((-dirv.y, dirv.x, 0))
        c0 = e.P(hu, 0, hinge_off) + dirv * (lw / 2)
        mk.box(mb, c0, dirv, side, lw, lt, 0.02, lh, "metal_grey", col=IRON_DOOR)
        for k in range(5):                                                     # riveted straps
            zb = 0.35 + k * (lh - 0.7) / 4
            for sg in (-1, 1):
                obox(mb, c0 + side * sg * (lt / 2 + 0.008), dirv, side, lw - 0.06, 0.016, zb, zb + 0.09, "iron")
        if s == 1:                                                             # wicket door in one leaf
            obox(mb, c0 + side * (lt / 2 + 0.02) - dirv * 0.1, dirv, side, 0.75, 0.04, 0.15, 1.95, "metal_grey",
                 col=(0.45, 0.5, 0.5), skip_sides=(0,))


def machicolation(mb, e, uc, zb, zt, w=1.5, pj=0.75, mat="fort", col=None, cap=True):
    """Box machicolation on three corbels, slit in front, dentil band and pyramid cap."""
    zband = zt - 0.18
    # box body (sides + front with a slit); open bottom between the corbels
    slit = rect(uc - 0.06, uc + 0.06, zband - 1.0, zband - 0.35)
    face(mb, e, rect(uc - w / 2, uc + w / 2, zb, zband), mat, pj, holes=[slit], col=col)
    tunnel(mb, e, slit, pj, pj - 0.12, mat, floor=False, col=col)
    face(mb, e, slit, "void", pj - 0.12)
    for s in (-1, 1):
        u = uc + s * w / 2
        mb.poly([e.P(u, zb, 0), e.P(u, zb, pj), e.P(u, zband, pj), e.P(u, zband, 0)], mat, e.t * s, col=col)
    mb.poly([e.P(uc - w / 2, zb, 0), e.P(uc + w / 2, zb, 0), e.P(uc + w / 2, zb, pj), e.P(uc - w / 2, zb, pj)],
            "void", -UP)
    # dentil band and pyramid cap
    bw, bpj = w / 2 + 0.07, pj + 0.07
    section_prism(mb, e, uc - bw, uc + bw, [(0, zband), (bpj, zband), (bpj, zt), (0, zt)], "ashlar",
                  skip=(2, 3), col=DRESSED)
    if cap:
        ap = e.P(uc, zt + 0.55, bpj * 0.5)
        corners = [e.P(uc - bw, zt, 0), e.P(uc + bw, zt, 0), e.P(uc + bw, zt, bpj), e.P(uc - bw, zt, bpj)]
        for k in (1, 2, 3):
            tri = [corners[k], corners[(k + 1) % 4], ap]
            mb.poly(tri, "ashlar", (tri[0] + tri[1]) / 2 - e.P(uc, zt, bpj * 0.5), col=DRESSED)
    # three corbels, stepped
    for k in (-1, 0, 1):
        u = uc + k * (w / 2 - 0.14)
        section_prism(mb, e, u - 0.13, u + 0.13,
                      [(0, zb - 0.95), (pj * 0.45, zb - 0.95), (pj * 0.45, zb - 0.5), (pj, zb - 0.5), (pj, zb), (0, zb)],
                      mat, skip=(4, 5), col=col)


def groin_vault(mb, C, z_spring, rise, N=12, mat="fort", col=None):
    """Pointed groin vault over the quad C[0..3] (bilinear patch, z = spring + rise*max(g(u), g(v)));
    returns g so the wall arches can follow it exactly."""
    r = 0.62                                           # rise / span of the normalised pointed arch
    R = 0.25 + r * r

    def g(s):
        s = min(s, 1 - s)
        return math.sqrt(max(0.0, R * R - (R - s) ** 2)) / r

    C = [Vector((c[0], c[1], 0)) for c in C]

    def P(u, v):
        p = C[0] * (1 - u) * (1 - v) + C[1] * u * (1 - v) + C[2] * u * v + C[3] * (1 - u) * v
        return Vector((p.x, p.y, z_spring + rise * max(g(u), g(v))))
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
    # central boss
    top = P(0.5, 0.5)
    ring = [top + Vector((math.cos(2 * math.pi * k / 8) * 0.38, math.sin(2 * math.pi * k / 8) * 0.38, 0)) for k in range(8)]
    lo = [p - UP * 0.3 for p in ring]
    for k in range(8):
        q = [lo[k], lo[(k + 1) % 8], ring[(k + 1) % 8], ring[k]]
        mb.poly(q, "ashlar", (q[0] + q[1]) / 2 - (top - UP * 0.15), col=DRESSED)
    mb.poly(lo, "ashlar", -UP, col=DRESSED)
    return g


GATE_OUTER = dict(recess_w=5.0, recess_spring=5.0, recess_rise=3.45, recess_d=0.45, door_r=0.65,
                  frame_d=0.5, pass_spring=4.0, pass_rise=2.5)
GATE_INNER = dict(recess_w=5.2, recess_spring=4.7, recess_rise=3.6, recess_d=0.4, door_r=0.7,
                  frame_d=0.45, pass_spring=4.0, pass_rise=2.5)


def build_gatehouse(mb, g, place, rng):
    ring = [tuple(p) for p in g["ring"]]
    H = g["height"]                                    # top of the merlons
    th = g.get("wall", 2.0)
    zw, zs, d = H - GATE_WALK, H - GATE_SILL, GATE_PARAPET
    passages = list(g["passages"])
    pas = {p["edge"]: (k, p) for k, p in enumerate(passages)}
    plants = []

    def holes(i, e):
        hs = []
        if i in pas:
            k, p = pas[i]
            uc = p["u"] * e.L
            P = dict(GATE_OUTER if k == 0 else GATE_INNER)
            P.update(door_w=p["w"], door_h=min(p["h"] - 1.4, 1.42 * p["w"]), pass_w=p["w"] + 0.4)
            P["pass_spring"] = min(P["pass_spring"], p["h"] - P["pass_rise"])
            P["recess_w"] = max(P["recess_w"], p["w"] + 1.3)
            hs.append({"ol": pointed(uc - P["recess_w"] / 2, uc + P["recess_w"] / 2, 0.0, P["recess_spring"],
                                     P["recess_rise"], 7),
                       "build": lambda mb_, e_, uc=uc, P=P, k=k: portal(mb_, e_, uc, P, th, "fort", outer=(k == 0))})
            top_arch = P["recess_spring"] + P["recess_rise"]
            for s in (-1, 1):                                       # gun slits flanking the portal
                hs.append(slit_hole(uc + s * (P["recess_w"] / 2 + 0.55), top_arch - 0.9, top_arch + 0.9, 0.2, 0.6))
            # box machicolation over the arch (both faces): corbels clear the moulding and its roundel
            zt_m = H - 0.25
            zb_m = max(top_arch + 0.47 + 0.75 + 0.95, zt_m - (2.6 if k == 0 else 2.2))
            hs.append({"build": lambda mb_, e_, uc=uc, zt_m=zt_m, zb_m=zb_m, k=k:
                       machicolation(mb_, e_, uc, zb_m, zt_m, w=1.5 if k == 0 else 1.25, pj=0.75 if k == 0 else 0.6)})
        else:
            for u in (e.L * 0.33, e.L * 0.67):
                hs.append(slit_hole(u, 6.0 + rng.uniform(-0.4, 0.6), 7.6 + rng.uniform(-0.3, 0.6), 0.2, 0.6))
            hs.append({"build": lambda mb_, e_: disc(mb_, e_, e_.L * 0.5, 4.2, 0.34, 0.05, "ashlar", seg=10,
                                                     col=DRESSED)})
        plants.append((e, [h["ol"] for h in hs if h.get("ol")]))
        return hs

    E, inner_par, bats = battlemented_ring(mb, ring, -0.6, zw, zs, H, d, "fort", cw=2.0, mw=2.3, cr=0.85,
                                           holes=holes, roof=True)
    # ---- chamber: four walls under a pointed groin vault
    C = offset_ring(ring, th)
    vs, vr, N = 4.3, 3.9, 12
    gfn = groin_vault(mb, C, vs, vr, N, "fort")
    for i, e in enumerate(E):
        ua, ub = e.u_of(C[i]), e.u_of(C[(i + 1) % 4])
        top = [(ua + (ub - ua) * k / N, vs + vr * gfn(k / N)) for k in range(N + 1)]
        hl = []
        if i in pas:
            k, p = pas[i]
            uc = p["u"] * e.L
            pw = p["w"] + 0.4
            ps = min(4.0, p["h"] - 2.5)
            hl.append(pointed(uc - pw / 2, uc + pw / 2, 0.0, ps, 2.5, 6))
        else:                                                       # arched niche with a slit
            uc = (ua + ub) / 2
            niche = pointed(uc - 0.9, uc + 0.9, 0.9, 2.9, 1.0, 5)
            hl.append(niche)
            tunnel(mb, e, niche, -th, -th + 0.55, "fort", floor=False)
            sl = rect(uc - 0.06, uc + 0.06, 1.6, 2.9)
            face(mb, e, niche, "fort", -th + 0.55, holes=[sl], inward=True)
            tunnel(mb, e, sl, -th + 0.55, -th + 0.75, "fort", floor=False)
            face(mb, e, sl, "void", -th + 0.75, inward=True)
        face(mb, e, [(ua, -0.05), (ub, -0.05)] + top[::-1], "fort", -th, holes=hl, inward=True)
    # ---- plants in the joints
    for e, ols in plants:
        for _ in range(2):
            u, z = rng.uniform(1.0, e.L - 1.0), rng.uniform(2.5, zw - 0.5)
            if any(min(p[0] for p in ol) - 0.6 < u < max(p[0] for p in ol) + 0.6 for ol in ols):
                continue
            place("caper", e.P(u, z, 0.02), math.atan2(-e.n.x, e.n.y), True)
    for e in E[1:3]:
        for _ in range(2):
            place("caper", e.P(rng.uniform(1.5, e.L - 1.5), zs + 0.1, 0.02), math.atan2(-e.n.x, e.n.y), True)


# ================================================================== city wall
def wall_run(mb, e, ua, ub, ka, kb, H, T, mat, col=None, holes=(), cap_a=None, cap_b=None, batter=True,
             end_corner=(True, True), cw=1.3, mw=1.8, cr=0.8):
    """Straight run of the crenellated city wall along edge e from u=ua to u=ub (at the centre line).
    ka, kb: mitre slopes (the run ends at u = ua + ka*off); cap_*: None, "full" or "inner" end face."""
    zw, zs, d = H - WALL_WALK, H - WALL_SILL, GATE_PARAPET
    o_out, o_par, o_in = T / 2, T / 2 - d, -T / 2
    ip_t, ip_h = 0.5, 1.0
    o_q = o_in + ip_t
    ua_o, ub_o = ua + ka * o_out, ub + kb * o_out
    ua_p, ub_p = ua + ka * o_par, ub + kb * o_par
    bat = Battlement(e, ua_o, ub_o, ua_p, ub_p, zw, zs, H, d, cw, cw, mw, cr, slits=True, slit_every=2,
                     end_corner=end_corner)
    z_face = BATTER_H if batter else -0.6
    face(mb, e, bat.outline(z_face), mat, o_out, holes=[h["ol"] for h in holes if h.get("ol")] +
         [[(u, z) for u, z in s] for s in bat.slits], col=col)
    # slits / openings were given in u at the outer face; build their reveals in place
    for h in holes:
        if h.get("build"):
            h["build"](mb, ShiftedEdge(e, o_out))
    # the battlement's own faces are expressed at off 0 = outer face: shift the frame
    se = ShiftedEdge(e, o_out)
    bat.e = se
    bat.build(mb, mat, col, tops=False)
    for j in range(len(bat.merlons)):                              # all merlon tops (mitred at the ends)
        a, b = bat.merlons[j]
        if j == 0 or j == len(bat.merlons) - 1:
            if j == 0:
                q = [e.P(ua_o, H, o_out), e.P(b, H, o_out), e.P(b, H, o_par), e.P(ua_p, H, o_par)]
            else:
                q = [e.P(a, H, o_out), e.P(ub_o, H, o_out), e.P(ub_p, H, o_par), e.P(a, H, o_par)]
            if len(bat.merlons) == 1:
                q = [e.P(ua_o, H, o_out), e.P(ub_o, H, o_out), e.P(ub_p, H, o_par), e.P(ua_p, H, o_par)]
            mb.poly(q, mat, UP, col=col)
        else:
            bat.merlon_top(mb, j, mat, col)
    # walk, inner parapet, inner face
    ua_q, ub_q = ua + ka * o_q, ub + kb * o_q
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
        zt_end = H
        if cap == "full":
            sec = [(o_in, -0.6), (o_out + (BATTER_D if batter else 0), -0.6)]
            if batter:
                sec.append((o_out, BATTER_H))
            sec += [(o_out, zt_end), (o_par, zt_end), (o_par, zw), (o_q, zw), (o_q, zw + ip_h), (o_in, zw + ip_h)]
        else:
            sec = [(o_in, -0.6), (0.0, -0.6), (0.0, zw), (o_q, zw), (o_q, zw + ip_h), (o_in, zw + ip_h)]
        mb.poly([e.P(u0 + k * o, z, o) for o, z in sec], mat, e.t * sgn, col=col)
    return bat


class ShiftedEdge(Edge):
    """The same edge frame with off measured from a parallel line (the outer face)."""

    def __init__(self, e, off0):
        self.A = e.A + e.n * off0
        self.L, self.t, self.n = e.L, e.t, e.n


def wall_tower(mb, e, uc, w, out, T, H, mat, col=None, rng=None, place=None):
    """Rectangular tower projecting from the outer face of the wall at u=uc."""
    o0, o1 = -T / 2, T / 2 + out
    ring = [(e.P(uc - w / 2, 0, o0)), (e.P(uc - w / 2, 0, o1)), (e.P(uc + w / 2, 0, o1)), (e.P(uc + w / 2, 0, o0))]
    ring = [(p.x, p.y) for p in ring]
    if mk.ring_area(ring) < 0:
        ring = ring[::-1]

    def holes(i, ee):
        if ee.n.dot(e.n) > 0.7:                                    # front face
            return [slit_hole(ee.L * 0.5, 5.5, 7.4, 0.2, 0.6),
                    {"build": lambda mb_, e_: machicolation(mb_, e_, e_.L * 0.5, H - 3.2, H - 0.25, 1.4, 0.7)}]
        if abs(ee.n.dot(e.t)) > 0.7:
            return [slit_hole(ee.L * 0.62, 6.0, 7.6, 0.2, 0.6)]
        return []
    batter_ring(mb, ring, -0.6, BATTER_H, BATTER_D, mat, col)
    battlemented_ring(mb, ring, -0.6, H - WALL_WALK, H - WALL_SILL, H, GATE_PARAPET, mat, col, cw=1.5, mw=1.8,
                      cr=0.8, holes=holes)


def build_city_walls(mb, walls, gate, place, rng):
    gring = [tuple(p) for p in gate["ring"]] if gate else []
    for w in walls:
        pts = [tuple(p) for p in w["pts"]]
        H, T = w["height"], w["thick"]
        segs = [Edge(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        # mitre slopes at interior joints and at an end that abuts the gate tower
        kstart, kend = [0.0] * len(segs), [0.0] * len(segs)
        for i in range(len(segs) - 1):
            a, b = segs[i], segs[i + 1]
            jd = (a.n + b.n).normalized()                      # the joint line runs along the mean normal
            # u offset per unit off along each segment: point = joint + jd*s has off = s*(jd.n), u = s*(jd.t)
            kend[i] = jd.dot(a.t) / jd.dot(a.n) if abs(jd.dot(a.n)) > 1e-6 else 0.0
            kstart[i + 1] = jd.dot(b.t) / jd.dot(b.n) if abs(jd.dot(b.n)) > 1e-6 else 0.0
        gate_end = None
        if gring:
            for k, end in ((0, pts[0]), (1, pts[-1])):
                for gi in range(len(gring)):
                    if math.dist(gring[gi], end) < 0.5:
                        gate_end = (k, gi)
        cap_s, cap_e = "full", "full"
        if gate_end:
            k, gi = gate_end
            # the wall ends flush with the gate face that starts at that corner (outer side)
            ge = Edge(gring[gi], gring[(gi + 1) % len(gring)])
            if k == 1:
                sg = segs[-1]
                if abs(ge.t.dot(sg.n)) > 1e-6:
                    kend[-1] = ge.t.dot(sg.t) / ge.t.dot(sg.n)
                cap_e = "inner"
            else:
                sg = segs[0]
                if abs(ge.t.dot(sg.n)) > 1e-6:
                    kstart[0] = ge.t.dot(sg.t) / ge.t.dot(sg.n)
                cap_s = "inner"
        # wall towers (spec "towers": [{"s": metres from the gate end, "w", "out", "h"}])
        towers = w.get("towers")
        if towers is None:
            towers = [{"s": 17.0, "w": 7.0, "out": 3.0, "h": H + 2.5}] if gate_end else []
        total = sum(s.L for s in segs)
        tw_on = []
        for tw in towers:
            s_abs = (total - tw["s"]) if (gate_end and gate_end[0] == 1) else tw["s"]
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
                runs.append((u, c0, "tower_b"))
                u = c1
            runs.append((u, sg.L, None))
            for ri, (u0, u1, _) in enumerate(runs):
                first, last = ri == 0, ri == len(runs) - 1
                if u1 - u0 < 0.3:
                    continue
                ka = kstart[si] if first else 0.0
                kb = kend[si] if last else 0.0
                ca = (cap_s if (si == 0 and first) else None)
                cb = (cap_e if (si == len(segs) - 1 and last) else None)
                near_gate = gate_end and ((gate_end[0] == 1 and si == len(segs) - 1 and last) or
                                          (gate_end[0] == 0 and si == 0 and first))
                hl = []
                if near_gate:                                     # blind pointed arch beside the gate
                    uo = (u1 + kb * T / 2) if gate_end[0] == 1 else (u0 + ka * T / 2)
                    c = uo - 4.6 if gate_end[0] == 1 else uo + 4.6
                    if u0 + 2.6 < c < u1 - 2.6:
                            hl.append(blind_arch(c - 2.2, c + 2.2, 0.0, 4.4, 2.6, 0.6, bench=(0.45, 0.45)))
                else:
                    u = u0 + 3.5
                    while u < u1 - 3.0:                           # arrow slits along the face
                        if rng.random() < 0.7:
                            hl.append(slit_hole(u, 5.0 + rng.uniform(-0.3, 0.3), 6.6 + rng.uniform(-0.3, 0.3)))
                        u += rng.uniform(5.5, 7.5)
                wall_run(mb, sg, u0, u1, ka, kb, H, T, "fort", holes=hl, cap_a=ca, cap_b=cb,
                         batter=not near_gate)
                if not near_gate:                                 # weeds along the batter toe
                    u = u0 + rng.uniform(0.5, 2.0)
                    while u < u1 - 0.5:
                        place("weeds", sg.P(u, 0.0, T / 2 + BATTER_D + 0.12), rng.uniform(0, 6.28), True)
                        u += rng.uniform(2.0, 5.0)
            for s_i, u, tw in tw_on:
                if s_i == si:
                    wall_tower(mb, sg, u, tw["w"], tw["out"], T, tw["h"], "fort", rng=rng, place=place)


# ================================================================== Citadel
def railing(mb, a, b, z, gen, h=1.1, post_every=2.2):
    """Black steel fence of the moat and bridge: cut-out bar card, square posts, flat top and foot rails."""
    A, B = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
    t = B - A
    L = t.length
    if L < 0.2:
        return
    t.normalize()
    s = Vector((-t.y, t.x, 0))
    rect_uv = mk.atlas_rect(gen["cutout"]["grid"], gen["cutout"]["cells"]["rail_moat"])
    k = max(1, round(L / 1.6))
    for i in range(k):
        p0, p1 = A + t * (L * i / k), A + t * (L * (i + 1) / k)
        mk.card(mb, (p0 + p1) / 2 + UP * 0.06, t, UP, (p1 - p0).length, h - 0.06, "cut", rect_uv, double=True)
    n = max(1, round(L / post_every))
    for i in range(n + 1):
        p = A + t * (L * i / n)
        obox(mb, p, t, s, 0.06, 0.06, z, z + h + 0.05, "iron")
    obox(mb, (A + B) / 2, t, s, L, 0.05, z + h - 0.02, z + h + 0.02, "iron", bottom=True)
    obox(mb, (A + B) / 2, t, s, L, 0.03, z + 0.08, z + 0.12, "iron", bottom=True)


def moat_wall(mb, eo, ring, i, z_floor, first, last, th=0.5, z_cop=0.55):
    """Street-side retaining wall of the moat along ring edge i (the moat on its left/inner side):
    ashlar face down to the moat floor, a coping slab overhanging both faces, street face."""
    col = (0.95, 0.93, 0.88)
    n = len(ring)
    L = eo.L
    # mitre slopes of the street-side face and coping (offset lines) at the run's inner joints
    def k_at(v, start):
        if (start and first) or ((not start) and last):
            return 0.0
        if start:
            ep = Edge(ring[(i - 1) % n], ring[i])
        else:
            ep = Edge(ring[(i + 1) % n], ring[(i + 2) % n])
        bis = (eo.n + ep.n)
        if bis.length < 1e-6:
            return 0.0
        jd = bis.normalized()                                       # joint line along the mean normal
        return jd.dot(eo.t) / jd.dot(eo.n) if abs(jd.dot(eo.n)) > 1e-6 else 0.0
    ka, kb = k_at(i, True), k_at(i + 1, False)
    U = lambda u0, k, o: u0 + k * o                                 # noqa: E731
    z_cb = z_cop - 0.1
    for o, z0, z1, sgn in ((0.0, z_floor - 0.1, z_cb, -1), (th, -0.25, z_cb, 1)):
        mb.poly([eo.P(U(0, ka, o), z0, o), eo.P(U(L, kb, o), z0, o), eo.P(U(L, kb, o), z1, o),
                 eo.P(U(0, ka, o), z1, o)], "ashlar", eo.n * sgn, col=col)
    oa, ob = -0.06, th + 0.06                                       # coping slab
    q = [(oa, z_cb), (ob, z_cb), (ob, z_cop), (oa, z_cop)]
    for (o0, z0), (o1, z1), nrm in ((q[0], q[1], -UP), (q[1], q[2], eo.n), (q[2], q[3], UP), (q[3], q[0], -eo.n)):
        mb.poly([eo.P(U(0, ka, o0), z0, o0), eo.P(U(L, kb, o0), z0, o0), eo.P(U(L, kb, o1), z1, o1),
                 eo.P(U(0, ka, o1), z1, o1)], "ashlar", nrm, col=DRESSED)
    for u0, k, s, flag in ((0.0, ka, -1, first), (L, kb, 1, last)):  # open ends of a run
        if flag:
            mb.poly([eo.P(U(u0, k, o), z, o) for o, z in
                     ((0.0, z_floor - 0.1), (th, -0.25), (th, z_cb), (ob, z_cb), (ob, z_cop), (oa, z_cop), (oa, z_cb),
                      (0.0, z_cb))], "ashlar", eo.t * s, col=col)


def glacis(mb, ring, idx, z_top, z_toe, run, cut_a, cut_b, mat="rubble", col=WEATHER):
    """Sloping revetment in front of consecutive ring edges idx (vertex idx[0] .. idx[-1]+1).
    cut_a / cut_b: (point, direction) lines that trim the toe at both ends (the moat end walls)."""
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
    for k, i in enumerate(idx):
        a, b = Vector((*ring[verts[k]], z_top)), Vector((*ring[verts[k + 1]], z_top))
        ta, tb = toe[k].to_2d().to_3d() + UP * z_toe, toe[k + 1].to_2d().to_3d() + UP * z_toe
        mb.poly([ta, tb, b, a], mat, E[i].n * (z_top - z_toe) + UP * run, col=col)
    # end faces above the street where the glacis is trimmed by the moat ends
    for k, cut in ((0, cut_a), (len(verts) - 1, cut_b)):
        v = Vector((*ring[verts[k]], 0))
        t = toe[k].to_2d().to_3d()
        frac = (z_top - 0.0) / (z_top - z_toe)
        p0 = v.lerp(t, frac)
        tri = [v + UP * z_top, v + UP * -0.2, p0 + UP * -0.2]
        nrm = (t - v).cross(UP)
        e = E[idx[0]] if k == 0 else E[idx[-1]]
        if nrm.dot(e.t * (-1 if k == 0 else 1)) < 0:
            nrm = -nrm
        mb.poly(tri, mat, nrm, col=col)
    return toe


def herodian_band(mb, e, u0, u1, z0, z1, off, mat="ashlar", rng=None, col=(0.95, 0.9, 0.82)):
    """Huge drafted-margin blocks: courses of raised bosses with sunken margins."""
    rng = rng or random.Random(3)
    z = z0
    course = 0
    while z + 0.9 < z1:
        h = min(1.25 + rng.uniform(-0.1, 0.15), z1 - z)
        u = u0 + (0.0 if course % 2 == 0 else -1.3)
        while u < u1 - 0.3:
            L = 2.4 + rng.uniform(-0.5, 0.9)
            a, b = max(u, u0) + 0.09, min(u + L, u1) - 0.09
            if b - a > 0.5:
                bp = 0.07 + rng.uniform(0.0, 0.05)
                section_prism(mb, e, a, b, [(off, z + 0.09), (off + bp, z + 0.13), (off + bp, z + h - 0.13),
                                            (off, z + h - 0.09)], mat, skip=(3,), col=col)
            u += L
        z += h
        course += 1


def tower_box(mb, c, size, rot, z0, H, mat="fort", col=None, top=None, herodian=None, rng=None, place=None,
              gen=None, glacis_h=None, windows=True, machis=True):
    """Square citadel tower: battered foot, crenellations, slits, box machicolations, optional
    superstructure and a band of Herodian drafted blocks."""
    rng = rng or random.Random(5)
    t = Vector((math.cos(math.radians(rot)), math.sin(math.radians(rot)), 0))
    s = Vector((-t.y, t.x, 0))
    cc = Vector((c[0], c[1], 0))
    hl, hw = size[0] / 2, size[1] / 2
    ring = [cc - t * hl - s * hw, cc + t * hl - s * hw, cc + t * hl + s * hw, cc - t * hl + s * hw]
    ring = [(p.x, p.y) for p in ring]
    zw, zs = H - CIT_WALK, H - CIT_SILL

    def holes(i, e):
        hs = []
        if windows:
            for f in (0.3, 0.7):
                hs.append(slit_hole(e.L * f, zw - 6.0 + rng.uniform(-0.5, 0.5), zw - 4.4, 0.22, 0.7))
            hs.append({"ol": rect(e.L * 0.5 - 0.4, e.L * 0.5 + 0.4, zw - 3.0, zw - 1.8),
                       "build": lambda mb_, e_: (tunnel(mb_, e_, rect(e_.L * 0.5 - 0.4, e_.L * 0.5 + 0.4, zw - 3.0,
                                                                     zw - 1.8), 0, -0.5, mat, floor=False),
                                                 face(mb_, e_, rect(e_.L * 0.5 - 0.4, e_.L * 0.5 + 0.4, zw - 3.0,
                                                                    zw - 1.8), "void", -0.5),
                                                 grille(mb_, e_, e_.L * 0.5, zw - 3.0, zw - 1.8, 0.8, gen))})
        if machis:
            for f in ((0.5,) if e.L < 12 else (0.3, 0.7)):
                hs.append({"build": lambda mb_, e_, f=f: machicolation(mb_, e_, e_.L * f, H - 3.4, H - 0.3, 1.5, 0.75)})
        if herodian:
            hz0, hz1 = herodian
            hs.append({"build": lambda mb_, e_: herodian_band(mb_, e_, 0.15, e_.L - 0.15, hz0, hz1, 0.0, rng=rng)})
        return hs
    battlemented_ring(mb, ring, z0, zw, zs, H, 0.9, mat, col, cw=1.6, mw=1.8, cr=0.8, holes=holes)
    if top:
        tr = top["size"]
        H2 = H + top["h"]
        cc2 = cc + s * 0.0
        r2 = [cc2 - t * tr[0] / 2 - s * tr[1] / 2, cc2 + t * tr[0] / 2 - s * tr[1] / 2,
              cc2 + t * tr[0] / 2 + s * tr[1] / 2, cc2 - t * tr[0] / 2 + s * tr[1] / 2]
        r2 = [(p.x, p.y) for p in r2]
        battlemented_ring(mb, r2, zw - 0.3, H2 - CIT_WALK + 0.6, H2 - CIT_SILL + 0.2, H2, 0.6, mat, col, cw=1.2,
                          mw=1.4, cr=0.7,
                          holes=lambda i, e: [slit_hole(e.L * 0.5, zw + 1.2, zw + 2.6, 0.2, 0.5)])
    return ring


def grille(mb, e, uc, z0, z1, w, gen, off=-0.12):
    if not gen:
        return
    gr = mk.atlas_rect(gen["cutout"]["grid"], gen["cutout"]["cells"]["grille"])
    mk.card(mb, e.P(uc, z0, off), e.t, UP, w, z1 - z0, "cut", gr, double=True)


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


def east_entrance(mb, e, D, gen, H):
    """Citadel entrance on the east face: pointed recess with a wooden door, and a stone bridge
    over the moat with parapet walls, railings and steps down to the street."""
    uc = e.L / 2
    zt = 1.0                                               # threshold = courtyard level
    bw = 4.2                                               # bridge width
    span = 6.0                                             # moat width
    # bridge deck + parapets (local frame of e: off >0 = out over the moat)
    o0, o1 = 0.0, span + 0.4
    u0, u1 = uc - bw / 2, uc + bw / 2
    mb.poly([e.P(u0 + 0.35, zt, o0), e.P(u1 - 0.35, zt, o0), e.P(u1 - 0.35, zt, o1), e.P(u0 + 0.35, zt, o1)],
            "paving", UP)
    for s, ua, ub in ((-1, u0, u0 + 0.35), (1, u1 - 0.35, u1)):
        # side (spandrel) wall down into the moat with an arch over the moat floor
        uo = ua if s < 0 else ub
        arch = [(3.0, -D), (span - 0.1, -D)] + [(p[0], p[1]) for p in
                                                 _seg_arch(3.0, span - 0.1, -D + 1.6, 0.9)]
        outline = [(0.0, -D - 0.1), (o1, -D - 0.1), (o1, zt + 0.55), (0.0, zt + 0.55)]
        ef = BridgeFrame(e, uo, s)
        face(mb, ef, outline, "fort", 0.0, holes=[arch])
        if s < 0:
            tunnel(mb, ef, arch, 0.0, -bw, "fort")
        # parapet top and inner face
        ui = ub if s < 0 else ua
        mb.poly([e.P(ua, zt + 0.55, o0), e.P(ub, zt + 0.55, o0), e.P(ub, zt + 0.55, o1), e.P(ua, zt + 0.55, o1)],
                "ashlar", UP, col=DRESSED)
        mb.poly([e.P(ui, zt, o0), e.P(ui, zt, o1), e.P(ui, zt + 0.55, o1), e.P(ui, zt + 0.55, o0)], "fort",
                e.t * (-s))
        mb.poly([e.P(ua, zt, o1), e.P(ub, zt, o1), e.P(ub, zt + 0.55, o1), e.P(ua, zt + 0.55, o1)], "fort", e.n)
        railing(mb, e.P((ua + ub) / 2, 0, o0 + 0.1).to_2d(), e.P((ua + ub) / 2, 0, o1 - 0.1).to_2d(), zt + 0.55, gen,
                h=1.0)
    # steps down to the street beyond the outer moat edge (6 x 0.167 m)
    nst = 6
    for k in range(nst):
        z1 = zt - k * zt / nst
        oa, ob = o1 + k * 0.32, o1 + (k + 1) * 0.32
        ua, ub = u0 + 0.1, u1 - 0.1
        mb.poly([e.P(ua, z1, oa), e.P(ub, z1, oa), e.P(ub, z1, ob), e.P(ua, z1, ob)], "paving", UP)
        mb.poly([e.P(ua, z1 - zt / nst - 0.15, ob), e.P(ub, z1 - zt / nst - 0.15, ob), e.P(ub, z1, ob),
                 e.P(ua, z1, ob)], "ashlar", e.n, col=DRESSED)
        for uu, sgn in ((ua, -1), (ub, 1)):
            mb.poly([e.P(uu, -0.2, oa), e.P(uu, -0.2, ob), e.P(uu, z1, ob), e.P(uu, z1, oa)], "ashlar", e.t * sgn,
                    col=DRESSED)
    # the street-side face under the deck between the parapet walls
    mb.poly([e.P(u0 + 0.35, -0.2, o1), e.P(u1 - 0.35, -0.2, o1), e.P(u1 - 0.35, zt, o1), e.P(u0 + 0.35, zt, o1)],
            "fort", e.n)


def _seg_arch(a, b, vs, rise, seg=6):
    w = b - a
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = vs + rise - R
    a0 = math.asin((w / 2) / R)
    return [((a + b) / 2 + math.sin(-a0 + 2 * a0 * k / seg) * R * -1, cz + math.cos(-a0 + 2 * a0 * k / seg) * R)
            for k in range(seg + 1)]


class BridgeFrame(Edge):
    """Frame for a bridge side wall: u = offset from the face, off along +-t of the citadel face."""

    def __init__(self, e, u_at, s):
        self.A = e.P(u_at, 0.0, 0.0)
        self.t = e.n
        self.n = e.t * s
        self.L = 0.0


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
    # the entrance: the short moat-side edge facing east (barbican), else none
    ent = None
    cands = [i for i in range(n) if moat[i] and 4.0 < E[i].L < 12.0 and E[i].n.x > 0.8]
    if cands:
        ent = max(cands, key=lambda i: E[i].A.x)
    barb = set()
    if ent is not None:
        barb = {(ent - 1) % n, ent, (ent + 1) % n}
    styles = ["pointed" if i in barb else "flat" for i in range(n)]
    base = [(-D - 0.5) if moat[i] else -0.6 for i in range(n)]
    plants = []

    def holes(i, e):
        hs = []
        if i == ent:
            uc = e.L / 2
            rec = pointed(uc - 2.0, uc + 2.0, 1.0, 5.2, 2.9, 7)
            door = pointed(uc - 1.25, uc + 1.25, 1.0, 3.3, 1.5, 6)

            def build(mb_, e_, uc=uc, rec=rec, door=door):
                tunnel(mb_, e_, rec, 0.0, -0.6, "fort", floor=False)
                face(mb_, e_, rec, "fort", -0.6, holes=[door])
                tunnel(mb_, e_, door, -0.6, -0.9, "fort", floor=False)
                rect_uv = mk.atlas_rect(gen["doors"]["grid"], gen["doors"]["cells"]["door_wood"])
                fl, ft = mk.tess2d([door])
                pts = [e_.P(u, z, -0.9) for u, z in fl]
                for a_, b_, c_ in ft:
                    uvs = [((fl[k][0] - (uc - 1.25)) / 2.5 * (rect_uv[2] - rect_uv[0]) + rect_uv[0],
                            (fl[k][1] - 1.0) / 3.8 * (rect_uv[3] - rect_uv[1]) + rect_uv[1]) for k in (a_, b_, c_)]
                    mb_.poly([pts[a_], pts[b_], pts[c_]], "doors", e_.n, uv=uvs)
                # moulded hood over the recess
                ot = pointed_top(uc - 2.35, uc + 2.35, 5.2, 3.3, 7)
                it = pointed_top(uc - 2.0, uc + 2.0, 5.2, 2.9, 7)
                face(mb_, e_, ot + it[::-1], "ashlar", 0.1, col=DRESSED)
                cc = e_.P(uc, 5.2)
                strip(mb_, e_, ot, 0.0, 0.1, "ashlar", lambda p, q: e_.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) - cc,
                      DRESSED)
                strip(mb_, e_, it, 0.0, 0.1, "ashlar", lambda p, q: cc - e_.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2),
                      DRESSED)
                for ua_, ub_ in ((uc + 2.0, uc + 2.35), (uc - 2.35, uc - 2.0)):
                    mb_.poly([e_.P(ua_, 5.2, 0), e_.P(ub_, 5.2, 0), e_.P(ub_, 5.2, 0.1), e_.P(ua_, 5.2, 0.1)], "ashlar",
                             -UP, col=DRESSED)
                east_entrance(mb_, e_, D, gen, H)
            hs.append({"ol": rec, "build": build})
        elif e.L > 6.0:
            u = 3.0
            while u < e.L - 3.0:
                if rng.random() < 0.55:
                    hs.append(slit_hole(u, 6.6 + rng.uniform(-0.3, 0.3), 8.1 + rng.uniform(-0.3, 0.3), 0.2, 0.6))
                u += rng.uniform(5.0, 7.5)
        if i in barb:                                              # dentil band under the merlons
            hs.append({"build": lambda mb_, e_: section_prism(
                mb_, e_, 0.05, e_.L - 0.05, [(0, zw - 0.75), (0.1, zw - 0.65), (0.1, zw - 0.35), (0, zw - 0.3)],
                "ashlar", skip=(3,), col=DRESSED, ends=False)})
        plants.append((e, [h["ol"] for h in hs if h.get("ol")], moat[i]))
        return hs

    E, inner_par, bats = battlemented_ring(mb, mass, base, zw, zs, H, 0.8, "fort", style=styles, cw=1.4, mw=1.6,
                                           cr=0.75, holes=holes, roof=False, slit_every=2)
    # roof of the enceinte between the parapet and the courtyard; courtyard faces with an arcade
    try:
        fl, ft = mk.tess2d([inner_par, court])
        mb.tris([(p[0], p[1], zw) for p in fl], ft, "fort", UP)
    except Exception:                                              # noqa: BLE001
        pass
    nc = len(court)
    for i in range(nc):
        a, b = court[(i + 1) % nc], court[i]                       # reversed: normal into the courtyard
        e = Edge(a, b)
        L = e.L
        hl = []
        u = 2.2
        while u + 3.0 < L:
            ol = pointed(u, u + 2.6, 1.0, 3.6, 1.6, 5)
            hl.append(ol)
            u += 4.4
        face(mb, e, [(0, 0.9), (L, 0.9), (L, zw), (0, zw)], "fort", 0.0, holes=hl)
        for ol in hl:
            tunnel(mb, e, ol, 0.0, -0.9, "fort", floor=False)
            face(mb, e, ol, "void", -0.9)
    # ---- moat: glacis, street-side retaining wall with coping and railing, end walls
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
        glacis(mb, mass, run, 2.2, -D - 0.05, 3.1, cut_a, cut_b)
        # retaining wall on the street side (outer ring edges with the same indices)
        # street-side retaining wall: one mitred chain from the mass corner round the moat and back
        chain = [mass[ia]] + [outer[i] for i in run] + [outer[(ib + 1) % no], mass[(ib + 1) % n]]
        chain = [p for k, p in enumerate(chain) if k == 0 or math.dist(p, chain[k - 1]) > 0.2]
        bridge = None
        if ent is not None and ent in run:
            e_m = E[ent]
            bridge = e_m.P(e_m.L / 2, 0)
        for k in range(len(chain) - 1):
            eo = Edge(chain[k], chain[k + 1])
            first, last = k == 0, k == len(chain) - 2
            moat_wall(mb, eo, chain, k, -D, first, last)
            p0, p1 = 0.1 if first else 0.0, eo.L - (0.1 if last else 0.0)
            spans = [(p0, p1)]
            if bridge is not None and abs(eo.off_of(bridge) + 6.0) < 1.0 and 0 < eo.u_of(bridge) < eo.L:
                ub = eo.u_of(bridge)
                spans = [(p0, ub - 2.15), (ub + 2.15, p1)]
            for a_, b_ in spans:
                if b_ - a_ > 0.3:
                    railing(mb, eo.P(a_, 0, 0.25).xy, eo.P(b_, 0, 0.25).xy, 0.55, gen)
    # ---- towers
    for tw in c.get("towers", []):
        cx, cy = tw["c"]
        if tw["kind"] in ("box", "phasael"):
            z0 = -D - 0.5
            her = (2.5, 10.5) if tw["kind"] == "phasael" else None
            ring = tower_box(mb, tw["c"], tw["size"], tw.get("rot", 0.0), z0, tw["h"], top=tw.get("top"), herodian=her,
                             rng=rng, place=place, gen=gen, machis=tw["kind"] != "phasael")
            batter_ring(mb, ring, -D - 0.3, 3.0, 1.6, "rubble", WEATHER)
        elif tw["kind"] == "minaret":
            minaret(mb, cx, cy, 1.0, tw["h"], tw["r"])
    # ---- plants: capers in the joints of the walls and on the glacis
    for e, ols, is_moat in plants:
        k = int(e.L / 9) + (2 if is_moat else 0)
        for _ in range(k):
            u, z = rng.uniform(1.0, e.L - 1.0), rng.uniform(3.0 if is_moat else 1.5, zw - 0.8)
            if any(min(p[0] for p in ol) - 0.6 < u < max(p[0] for p in ol) + 0.6 for ol in ols):
                continue
            place("caper", e.P(u, z, 0.02), math.atan2(-e.n.x, e.n.y), True)
        if is_moat:
            for _ in range(int(e.L / 3)):
                u, f = rng.uniform(0.5, e.L - 0.5), rng.uniform(0.1, 0.9)
                p = e.P(u, 2.2 + (-D - 0.05 - 2.2) * f, 3.1 * f + 0.05)
                place("caper", p, math.atan2(-e.n.x, e.n.y), True)


# ================================================================== entry point
def build(mbs, spec, gen, place):
    """mbs: dict of MeshBuilders by object name -> filled in place."""
    rng = random.Random(1538)
    build_gatehouse(mbs["jaffa_gate"], spec["gatehouse"], place, rng)
    build_city_walls(mbs["city_wall"], spec["city_walls"], spec.get("gatehouse"), place, rng)
    build_citadel(mbs["citadel"], spec["citadel"], gen, place, rng)
