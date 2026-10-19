"""City gates of the Old City walls (all but Jaffa Gate) and a crenellated wall-circuit builder.

Landmark registry entries (blender/landmarks.py):  LANDMARKS = {osm_id: fn(mbs, bd, gen, place, lod=False)}

    w616186088     Damascus Gate (Bab al-Amud)        s08_damascus
    w288395731     Lions' Gate (Bab al-Asbat)         s10_herod_lions
    w290671706     Zion Gate (Bab an-Nabi Daud)       s02_zion
    w1545285986    Dung Gate (Bab al-Maghariba)       s07_kotel
    w1393450805    New Gate (Bab al-Jadid)            spec: must be tier "mid" in s03_christian_w
    m_herods_gate  Herod's Gate (Bab az-Zahra)        spec: manual record HEROD_RECORD (no OSM building)

    build_walls(mb, walls_generic, gen)    drop-in replacement for build_city.build_walls_generic: the
                                           OSM circuit cut around the gates (GATE_CUTS) and built with
                                           the crenellated profile of the gate sections.
    clip_walls(walls_generic)              only the cutting (segments outside the gates).

Reference, dimensions and confidence: data/reference/gates.md (photos data/photos_ref/gates/).

Conventions
* Each gate is built in a local frame whose z = 0 is the street level at its OUTER threshold
  (bd["edge_ground"] of the outer face) and merged into the sector builders shifted to that level,
  so nothing here depends on absolute heights.  The inner threshold follows edge_ground of the
  inner face; the passage floor is a plane through both thresholds.
* The footprint (bd["ring"]) is the truth for the massing; doors and passages are anchored on OSM
  points (passage ways, gate nodes) and found on whatever ring edge lies under them, so small
  changes of the cleaned footprints do not break the builders.
* (a, b) gate frame: origin at the outer door, a = inward across the wall, b = a rotated +90 deg.
* Passages: outer portal tunnel -> groin-vaulted hall(s) -> inner portal.  Floors "paving"/"setts",
  walls "fort", vaults "ashlar" (whitewashed).  Every passage clears the player capsule (r 0.35, h 1.75).
"""
import math
import random

from mathutils import Vector

import fortifications as F
import meshkit as mk

UP = Vector((0, 0, 1))
DRESSED = F.DRESSED
PLASTER = (1.0, 0.97, 0.88)                 # whitewashed vaults inside the passages (photos GD:26, s10 R:05, GH:04)
CARVED = (0.92, 0.89, 0.83)                 # carved stone (lions, shells, corbels)
GATE_COL = (0.97, 0.96, 0.95)               # vertex tint of plain "fort" faces (cf. FORT_COL in fortifications)
LOD_COL = (0.95, 0.94, 0.92)


# ====================================================================== small helpers
def v2(p):
    return Vector((p[0], p[1], 0.0))


def compass(deg):
    r = math.radians(deg)
    return Vector((math.sin(r), math.cos(r), 0.0))


def find_edge(ring, p, facing=None, tol=55.0, maxd=4.0):
    """(index, Edge, u) of the ring edge nearest to point p whose outward normal is within tol degrees
    of the compass bearing `facing`; None when nothing lies within maxd metres."""
    P = v2(p)
    best = None
    n = len(ring)
    for i in range(n):
        e = F.Edge(ring[i], ring[(i + 1) % n])
        if e.L < 0.5:
            continue
        if facing is not None and e.n.dot(compass(facing)) < math.cos(math.radians(tol)):
            continue
        u = min(max(e.u_of(P), 0.0), e.L)
        d = (e.P(u, 0) - P).length
        if best is None or d < best[0]:
            best = (d, i, e, e.u_of(P))
    if best is None or best[0] > maxd:
        return None
    return best[1], best[2], best[3]


class Frame:
    """2D frame: origin O, axis a, axis b = a rotated +90 deg (CCW in (a, b) is CCW in the plan)."""

    def __init__(self, origin, a_dir):
        self.O = v2(origin)
        self.a = Vector((a_dir[0], a_dir[1], 0.0)).normalized()
        self.b = Vector((-self.a.y, self.a.x, 0.0))

    def P(self, a, b, z=0.0):
        return self.O + self.a * a + self.b * b + UP * z

    def xy(self, a, b):
        p = self.P(a, b)
        return (p.x, p.y)

    def ab(self, p):
        d = v2(p) - self.O
        return d.dot(self.a), d.dot(self.b)

    def rect(self, a0, a1, b0, b1):
        return [self.xy(a0, b0), self.xy(a1, b0), self.xy(a1, b1), self.xy(a0, b1)]

    def edge(self, a0, b0, a1, b1):
        return F.Edge(self.xy(a0, b0), self.xy(a1, b1))


def merge(dst, src, dz=0.0):
    """Append the faces of MeshBuilder src to dst, raised by dz."""
    off = Vector((0.0, 0.0, dz))
    base = len(dst.verts)
    dst.verts.extend(v + off for v in src.verts)
    for f, uv, m, c in zip(src.faces, src.uvs, src.mats, src.cols):
        dst.faces.append([i + base for i in f])
        dst.uvs.append(uv)
        dst.mats.append(dst._mat(src.mat_names[m]))
        dst.cols.append(c)


def shifted(mb, dz, fn):
    """Run fn(tmp) on a temporary builder and merge it into mb raised by dz (helpers that assume z = 0)."""
    if abs(dz) < 1e-6:
        return fn(mb)
    tmp = mk.MeshBuilder(mb.tile)
    r = fn(tmp)
    merge(mb, tmp, dz)
    return r


def zshift(ol, dz):
    return [(u, z + dz) for u, z in ol]


def ushift(ol, du):
    return [(u + du, z) for u, z in ol]


class Local:
    """Local builders (z = 0 at the outer threshold) merged into the sector builders on flush()."""

    def __init__(self, mbs, z_ref):
        self.mbs, self.z = mbs, z_ref
        tiles = dict(mbs["solid"].tile, fort=F.FORT_TILE)
        self.solid = mk.MeshBuilder(tiles)
        self.deco = mk.MeshBuilder(tiles)

    def flush(self, col=GATE_COL):
        for mb in (self.solid, self.deco):
            F.tint_planes(mb, "fort", col)
        merge(self.mbs["solid"], self.solid, self.z)
        merge(self.mbs["deco"], self.deco, self.z)


def ramp(p0, z0, p1, z1):
    """Planar floor through (p0, z0) and (p1, z1), level across the p0->p1 direction."""
    A = v2(p0)
    d = v2(p1) - A
    L2 = max(d.length_squared, 1e-6)
    return lambda x, y: z0 + (z1 - z0) * (Vector((x, y, 0.0)) - A).dot(d) / L2


def floor(mb, quad, zf, mat="paving"):
    q = list(quad)
    if mk.ring_area(q) < 0:
        q = q[::-1]
    mb.poly([Vector((x, y, zf(x, y))) for x, y in q], mat, UP)


def segment(u0, u1, v0, vs, rise, seg=6):
    """Opening with a segmental arch: (u0,v0),(u1,v0),(u1,vs), arc, (u0,vs)."""
    w = u1 - u0
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = vs + rise - R
    a0 = math.asin(min(1.0, (w / 2) / R))
    pts = [(u0, v0), (u1, v0), (u1, vs)]
    for k in range(1, seg):
        a = a0 - 2 * a0 * k / seg
        pts.append(((u0 + u1) / 2 + math.sin(a) * R, cz + math.cos(a) * R))
    pts.append((u0, vs))
    return pts


def tudor(u0, u1, v0, vs, r, peak, seg=4):
    """Broad four-centred arch (New Gate): arcs of radius r at the springers, straight rises to a low
    point `peak` above them at the centre."""
    uc = (u0 + u1) / 2
    k70 = math.radians(70)
    pts = [(u0, v0), (u1, v0), (u1, vs)]
    for k in range(1, seg + 1):
        a = k70 * k / seg
        pts.append((u1 - r + r * math.cos(a), vs + r * math.sin(a)))
    pts.append((uc, vs + r * math.sin(k70) + peak))
    for k in range(seg, 0, -1):
        a = k70 * k / seg
        pts.append((u0 + r - r * math.cos(a), vs + r * math.sin(a)))
    pts.append((u0, vs))
    return pts


def rect_ring(pts):
    pts = [tuple(p) for p in pts]
    return pts if mk.ring_area(pts) > 0 else pts[::-1]


# ====================================================================== building blocks
def hall(mb, C, zf, vs, vr, z_bot, dome=0.5, holes=None, N=10):
    """Groin-vaulted chamber on the CCW plan quad C: inward walls whose tops follow the wall arches of the
    vault, openings per side {side: [(u, z) outline]} (side i = C[i] -> C[i+1], u from C[i]), the vault
    (whitewashed ashlar with dressed ribs and boss) and the floor zf(x, y)."""
    g = F.groin_vault(mb, C, vs, vr, N, "ashlar", col=PLASTER, dome=dome)
    for i in range(4):
        e = F.Edge(C[i], C[(i + 1) % 4])
        top = [(e.L * k / N, vs + vr * g(k / N)) for k in range(N + 1)]
        F.face(mb, e, [(0.0, z_bot), (e.L, z_bot)] + top[::-1], "fort", 0.0, holes=(holes or {}).get(i, []),
               inward=True)
    floor(mb, C, zf)
    return g


def band_arch(mb, e, ol, v_spring, bw, rise_k, off=0.0, depth=0.12, col=DRESSED):
    """Moulded flat band around the arched head of an opening outline (from its springing up),
    standing `depth` proud of the face plane at `off`."""
    top = [p for p in ol if p[1] >= v_spring - 1e-6]
    us = [p[0] for p in ol]
    uc = (min(us) + max(us)) / 2
    w = max(us) - min(us)
    sc = (w + 2 * bw) / w
    zmax = max(p[1] for p in top)
    k = (zmax - v_spring + rise_k) / max(zmax - v_spring, 1e-3)
    outer = [(uc + (u - uc) * sc, v_spring + (z - v_spring) * k) for u, z in top]
    c = e.P(uc, v_spring, off)
    F.face(mb, e, outer + top[::-1], "ashlar", off + depth, col=col)
    F.strip(mb, e, outer, off, off + depth, "ashlar",
            lambda p, q: e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, off) - c, col)
    F.strip(mb, e, top, off, off + depth, "ashlar",
            lambda p, q: c - e.P((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, off), col)
    for (ua, za), (ub, zb) in ((outer[0], top[0]), (top[-1], outer[-1])):
        mb.poly([e.P(ua, za, off), e.P(ub, zb, off), e.P(ub, zb, off + depth), e.P(ua, za, off + depth)], "ashlar",
                -UP, col=col)
    return outer


def jamb_band(mb, e, u, z0, z1, w, off=0.0, depth=0.1, col=DRESSED):
    """Dressed pilaster strip (door frame) from z0 to z1 centred on u, proud of the face at off."""
    F.obox(mb, e.P(u, 0, off + depth / 2), e.t, e.n, w, depth, z0, z1, "ashlar", col=col, skip_sides=(0,))


def recess_outline(P, uc, v0=0.0):
    return F.pointed(uc - P["recess_w"] / 2, uc + P["recess_w"] / 2, v0, P["recess_spring"], P["recess_rise"], 7)


def pass_outline(P, uc, v0=0.0, dz=0.0):
    """Passage arch of portal P centred on uc, bottom v0, springing raised by dz (inner portals built dz up)."""
    return F.pointed(uc - P["pass_w"] / 2, uc + P["pass_w"] / 2, v0, P["pass_spring"] + dz, P["pass_rise"], 6)


def portal(mb, e, uc, P, depth, gen=None, leaves=True, v0=0.0):
    """Recessed portal (generalised from fortifications.portal): pointed recess with a moulded band and a
    keystone, tympanum (inscription panel), doorway ("flat" lintel with rounded corners, "segment" or
    "pointed"), door frame, rebate to the taller passage arch and the passage tunnel to `depth`;
    optional open iron-plated leaves against the passage walls.  v0: bottom of the outlines (below the
    floor where the passage ramps)."""
    rw, rs, rr, rd = P["recess_w"], P["recess_spring"], P["recess_rise"], P["recess_d"]
    dw, shape = P["door_w"], P.get("door", "flat")
    fd = P.get("frame_d", 0.45)
    recess = recess_outline(P, uc, v0)
    if shape == "pointed":
        door = F.pointed(uc - dw / 2, uc + dw / 2, v0, P["door_spring"], P["door_rise"], 6)
        dh = P["door_spring"] + max(P["door_rise"], dw / 2)
    elif shape == "segment":
        door = segment(uc - dw / 2, uc + dw / 2, v0, P["door_spring"], P["door_rise"], 6)
        dh = P["door_spring"] + P["door_rise"]
    else:
        dh = P["door_h"]
        door = F.shouldered(uc - dw / 2, uc + dw / 2, v0, dh, P.get("door_r", 0.15))
    pas = pass_outline(P, uc, v0)
    F.tunnel(mb, e, recess, 0.0, -rd, "fort")
    F.face(mb, e, F.u_shape(recess, door), "fort", -rd)
    F.tunnel(mb, e, door, -rd, -rd - fd, "fort")
    F.face(mb, e, F.u_shape(pas, door), "fort", -rd - fd, inward=True)
    F.tunnel(mb, e, pas, -rd - fd, -depth, "fort")
    band_arch(mb, e, recess, rs, P.get("band", 0.45), P.get("band_rise", 0.5), 0.0, 0.1)
    apex = rs + max(rr, rw / 2) + P.get("band_rise", 0.5)
    F.obox(mb, e.P(uc, 0, 0.11), e.t, e.n, 0.42, 0.22, apex - 0.5, apex + 0.08, "ashlar", col=DRESSED, bottom=True,
           skip_sides=(0,))                                                         # keystone
    if P.get("panel"):                                                              # inscription in the tympanum
        pw_, ph_ = P["panel"]
        pz = dh + 0.3 + ph_ / 2
        hw = F.pointed_halfwidth(rw, rs, rr, pz + ph_ / 2 + 0.1)
        pw_ = min(pw_, 2 * hw - 0.4)
        if pw_ > 0.6 and pz + ph_ / 2 < rs + max(rr, rw / 2) - 0.3:
            F.panel(mb, e, uc, pz, pw_, ph_, -rd, lines=2 if ph_ < 0.6 else 3)
    if P.get("lintel"):                                                             # dressed lintel + corbels
        F.obox(mb, e.P(uc, 0, -rd + 0.04), e.t, e.n, dw + 0.5, 0.08, dh, dh + 0.42, "ashlar", col=DRESSED,
               bottom=True, skip_sides=(0,))
        for s in (-1, 1):                                                           # stepped (muqarnas) corbels
            for k in range(3):
                F.obox(mb, e.P(uc + s * (dw / 2 - 0.12 - 0.07 * k), 0, -rd + 0.1 + 0.08 * k), e.t, e.n,
                       0.42 - 0.1 * k, 0.12, dh - 0.25 * (k + 1), dh - 0.25 * k, "ashlar", col=CARVED, bottom=True)
    if leaves:
        pw = P["pass_w"]
        for s in (-1, 1):
            hinge = e.P(uc + s * (pw / 2 - 0.16), 0, -rd - fd - 0.06)
            dirv = -e.n * math.cos(math.radians(4)) - e.t * s * math.sin(math.radians(4))
            F.gate_leaf(mb, hinge, dirv, -e.t * s, min(dw / 2, depth - rd - fd + 0.4), min(dh - 0.3, 5.6), gen,
                        wicket=(s == 1))
    return pas


def arch_open(mb, e, uc, w, spring, rise, depth, band=0.4, band_rise=0.45, v0=0.0):
    """Open pointed archway (no door) through the face: moulded band + tunnel to depth."""
    ol = F.pointed(uc - w / 2, uc + w / 2, v0, spring, rise, 7)
    F.tunnel(mb, e, ol, 0.0, -depth, "fort")
    band_arch(mb, e, ol, spring, band, band_rise, 0.0, 0.1)
    return ol


def niche(u, z0, w, spring, rise, depth=0.3, slit=False, shell=True, boss=False):
    """Blind pointed niche (Zion, Lions, Herod): reveal, stone back, optional slit in the back, a fluted
    shell hood (radial ribs) and a carved boss."""
    ol = F.pointed(u - w / 2, u + w / 2, z0, spring, rise, 6)

    def build(mb, e, ol=ol):
        F.tunnel(mb, e, ol, 0.0, -depth, "fort", floor=False)
        holes = []
        if slit:
            sl = F.rect(u - 0.06, u + 0.06, z0 + 0.3, spring - 0.15)
            holes.append(sl)
            F.tunnel(mb, e, sl, -depth, -depth - 0.4, "fort", floor=False)
            F.face(mb, e, sl, "void", -depth - 0.4)
        F.face(mb, e, ol, "fort", -depth, holes=holes)
        if shell:
            apex = spring + max(rise, w / 2)
            for k in range(7):
                a = math.pi * (k + 0.5) / 7
                tip = (u + math.cos(a) * (w / 2 - 0.1), spring + math.sin(a) * (apex - spring - 0.12))
                mk.tube(mb, [e.P(u, spring + 0.05, -depth + 0.035), e.P(tip[0], tip[1], -depth + 0.035)], 0.03,
                        "ashlar", sides=3, col=CARVED)
            F.obox(mb, e.P(u, 0, -depth + 0.05), e.t, e.n, w - 0.1, 0.1, spring - 0.08, spring, "ashlar",
                   col=CARVED, bottom=True, skip_sides=(0,))
        if boss:
            F.disc(mb, e, u, (z0 + spring) / 2 + 0.1, 0.17, 0.08, "ashlar", off=-depth, seg=8, col=CARVED)
    return {"ol": ol, "build": build}


def lion(mb, e, u, z, facing, size=1.0, off=0.0, col=CARVED):
    """Low-relief striding lion (Baybars' panther), ~1.3 m long: body, head, legs, curled tail."""
    s = size
    d = 0.07 * s

    def bx(du0, du1, z0, z1, dd):
        a, b = u + facing * du0 * s, u + facing * du1 * s
        F.obox(mb, e.P((a + b) / 2, 0, off + dd / 2), e.t, e.n, abs(b - a), dd, z + z0 * s, z + z1 * s, "ashlar",
               col=col, bottom=True, skip_sides=(0,))
    bx(-0.45, 0.35, 0.22, 0.5, d)               # body
    bx(0.32, 0.6, 0.4, 0.66, d * 1.15)          # head
    bx(0.55, 0.66, 0.46, 0.58, d * 0.9)         # muzzle
    bx(0.42, 0.5, 0.64, 0.74, d * 0.8)          # ear
    for du in (-0.42, -0.25, 0.14, 0.3):        # legs
        bx(du, du + 0.09, 0.0, 0.24, d * 0.85)
    bx(-0.62, -0.45, 0.42, 0.48, d * 0.6)       # tail, curled up
    bx(-0.66, -0.58, 0.48, 0.72, d * 0.6)


def pits(mb, e, rng, u0, u1, z0, z1, n, off=0.0, avoid=()):
    """Bullet scars (Zion Gate, 1948): small dark irregular chips just proud of the face."""
    for _ in range(n):
        u, z = rng.uniform(u0, u1), rng.uniform(z0, z1)
        if any(a0 < u < a1 and b0 < z < b1 for a0, a1, b0, b1 in avoid):
            continue
        r = rng.uniform(0.035, 0.09)
        ring = [(u + r * (0.7 + 0.3 * rng.random()) * math.cos(2 * math.pi * j / 5),
                 z + r * (0.7 + 0.3 * rng.random()) * math.sin(2 * math.pi * j / 5)) for j in range(5)]
        g = rng.uniform(0.45, 0.62)
        mb.poly([e.P(a, b, off + 0.012) for a, b in ring], "fort", e.n, col=(g, g * 0.97, g * 0.93))


def rosette(u, z, r=0.3):
    def build(mb, e):
        F.disc(mb, e, u, z, r, 0.05, "ashlar", seg=10, col=CARVED)
        F.disc(mb, e, u, z, r * 0.6, 0.09, "ashlar", seg=8, col=DRESSED)
        F.disc(mb, e, u, z, r * 0.25, 0.12, "ashlar", seg=6, col=CARVED)
    return {"build": build}


def crown(mb, e, uc, z0, z1, w=1.4, d=0.8, proud=0.12):
    """Raised central merlon block with a finial (Damascus, Lions'), enclosing the parapet behind it."""
    oc = (proud - d - 0.05) / 2
    F.obox(mb, e.P(uc, 0, oc), e.t, e.n, w, d + 0.05 + proud, z0, z1, "fort")
    F.obox(mb, e.P(uc, 0, oc), e.t, e.n, w * 0.45, (d + proud) * 0.5, z1, z1 + 0.4, "ashlar", col=DRESSED)
    F.pyramid(mb, e.P(uc, 0, oc), e.t, e.n, w * 0.5, z1 + 0.4, 0.6, "ashlar", col=DRESSED)


def window_panel(mb, e, uc, win, w=2.6):
    """Raised panel around the Damascus Gate window (s08_damascus.md 3.4): frame strips, engaged colonnettes
    with capitals, a lintel, a frieze of small cusped arches on consoles and a palmette band."""
    z0, z1, hw = win
    zt = z1 + 1.3
    for a, b, za, zb in ((uc - w / 2, uc - w / 2 + 0.25, z0 - 0.3, zt), (uc + w / 2 - 0.25, uc + w / 2, z0 - 0.3, zt),
                         (uc - w / 2, uc + w / 2, z0 - 0.3, z0 - 0.05)):
        F.obox(mb, e.P((a + b) / 2, 0, 0.05), e.t, e.n, b - a, 0.1, za, zb, "ashlar", col=DRESSED, bottom=True,
               skip_sides=(0,))
    for s in (-1, 1):                                                  # colonnettes beside the opening
        u = uc + s * (hw + 0.17)
        c = e.P(u, 0, 0.13)
        mk.cylinder(mb, c.x, c.y, z0, z1, 0.09, "ashlar", seg=6, col=CARVED)
        F.obox(mb, e.P(u, 0, 0.13), e.t, e.n, 0.3, 0.26, z1, z1 + 0.22, "ashlar", col=CARVED, bottom=True)
    F.obox(mb, e.P(uc, 0, 0.08), e.t, e.n, 2 * hw + 0.6, 0.16, z1 + 0.22, z1 + 0.55, "ashlar", col=DRESSED,
           bottom=True, skip_sides=(0,))                                # joggled lintel
    n = 6
    for k in range(n):                                                 # cusped arcade on small consoles
        u = uc - w / 2 + 0.3 + (w - 0.6) * (k + 0.5) / n
        F.disc(mb, e, u, z1 + 0.85, 0.15, 0.08, "ashlar", seg=6, col=CARVED)
        F.obox(mb, e.P(u, 0, 0.06), e.t, e.n, 0.1, 0.12, z1 + 0.58, z1 + 0.7, "ashlar", col=CARVED, bottom=True,
               skip_sides=(0,))
    F.obox(mb, e.P(uc, 0, 0.06), e.t, e.n, w, 0.12, zt - 0.3, zt, "ashlar", col=CARVED, bottom=True,
           skip_sides=(0,))                                             # palmette band


def lod_mass(mb, ring, zb, zs, zt, period=2.0, mw=1.0, d=0.8, doors=(), pointed=False):
    """Distant massing: walls to the crenel sill, roof, merlon boxes on the outer edges (pyramid tips when
    pointed), dark doorways."""
    mk.prism(mb, ring, zb, zs, "fort", col=LOD_COL)
    n = len(ring)
    for i in range(n):
        e = F.Edge(ring[i], ring[(i + 1) % n])
        k = max(1, int(e.L / period))
        for j in range(k):
            u = (j + 0.5) * e.L / k
            w = min(mw, e.L / k * 0.8)
            mk.box(mb, e.P(u, 0, -d / 2), e.t, e.n, w, d, zs, zt, "fort", top=not pointed, col=LOD_COL)
            if pointed:
                F.pyramid(mb, e.P(u, 0, -d / 2), e.t, e.n, w, zt, 0.8, "fort", col=LOD_COL)
    for e, uc, w, h in doors:
        ol = F.pointed(uc - w / 2, uc + w / 2, 0.0, h - w * 0.6, w * 0.6, 4)
        mb.poly([e.P(u, z, 0.05) for u, z in ol], "void", e.n)


def gate_base(ring, eg, z_ref, zl):
    """Foot of each face: below its own street level and below every passage opening."""
    return [min(eg[i] - z_ref - 0.8, zl - 0.4) for i in range(len(ring))]



# Clean OSM footprints of the gates (spec rings as of 2026-10-19).  When the spec ring drifts from them by more
# than a few per cent (a clipping pass cut into it), the builders fall back to these, so a gate never comes out
# broken; edge levels are then taken from the nearest spec edge.
REF_RINGS = {
    "damascus": [(285.443, 560.679), (277.629, 569.417), (283.18, 574.329), (279.694, 578.232), (269.729, 569.406),
                 (273.613, 565.07), (258.798, 551.942), (254.725, 556.499), (245.338, 548.183), (251.221, 541.607),
                 (260.977, 550.267), (263.667, 547.262), (266.31, 549.602), (269.237, 546.32)],
    "lions": [(892.476, 474.446), (882.369, 472.35), (884.586, 460.596), (894.636, 462.038)],
    "zion": [(198.461, -405.155), (194.028, -416.498), (208.198, -421.987), (212.631, -410.633)],
    "herod": [(577.0, 697.3), (587.7, 700.8), (585.5, 709.0), (574.7, 706.1)],
    "dung": [(626.015, -200.787), (630.192, -199.977), (629.756, -197.749), (625.579, -198.558)],
    "new": [(-131.54, 293.662), (-124.417, 298.086), (-126.207, 301.28), (-133.434, 297.077)],
}


def footprint(bd, ref, tol=0.06):
    """(ring, edge levels) for a gate record: the spec ring when it is intact, else the reference ring with
    levels from the nearest spec edges.  None for secondary pieces (id "<osm>_k") of a footprint the spec
    split: the main piece builds the whole gate."""
    if bd.get("id", bd.get("osm")) != bd.get("osm"):
        return None
    ring = despike([tuple(p) for p in bd["ring"]])
    eg = bd.get("edge_ground") or [bd["ground"]] * len(bd["ring"])
    if len(ring) == len(bd["ring"]) and abs(abs(mk.ring_area(ring)) - abs(mk.ring_area(ref))) <= tol * abs(mk.ring_area(ref)):
        return ring, list(eg)
    src = [tuple(p) for p in bd["ring"]]
    n = len(src)
    out = []
    for i in range(len(ref)):
        e = F.Edge(ref[i], ref[(i + 1) % len(ref)])
        m = e.P(e.L / 2, 0)
        best = None
        for j in range(n):
            f = F.Edge(src[j], src[(j + 1) % n])
            if f.L < 0.3 or f.n.dot(e.n) < 0.7:
                continue
            u = min(max(f.u_of(m), 0.0), f.L)
            d = (f.P(u, 0) - m).length
            if best is None or d < best[0]:
                best = (d, eg[j] if j < len(eg) else bd["ground"])
        out.append(best[1] if best and best[0] < 3.0 else bd["ground"])
    return [tuple(p) for p in ref], out

# ====================================================================== Damascus Gate
# OSM: building w616186088; passage w616186087 (covered) outer door (265.8,558.2) -> (268.0,555.6) ->
# (270.1,557.6) -> inner door (275.4,551.8); side passage w616338411 to (262.4,548.7); bridge w616383626.
DAM = {"door_out": (265.8, 558.2), "door_in": (275.4, 551.8), "side_out": (262.4, 548.7), "facing": 317.0,
       "e_tower_back": (280.4, 571.9), "screen_back": (261.0, 550.3),
       "z_sill": 14.0, "z_top": 15.2, "walk": 12.9,            # outer screen: merlon base ~14 m, finials ~16 m
       "tower_dz": 0.5,                                         # towers ~0.5 m higher
       "back_sill": 9.4, "back_walk": 8.4}                      # inner block behind the screen: parapet ~10 m
DAM_OUT = dict(recess_w=5.0, recess_spring=6.5, recess_rise=2.7, recess_d=0.9, band=0.5, band_rise=0.55,
               door="flat", door_w=4.0, door_h=5.2, door_r=0.1, frame_d=0.45, pass_w=4.6, pass_spring=5.0,
               pass_rise=2.3, panel=(2.2, 0.6))
DAM_IN = dict(recess_w=6.4, recess_spring=5.6, recess_rise=3.3, recess_d=0.5, band=0.5, band_rise=0.55,
              door="pointed", door_w=4.6, door_spring=4.6, door_rise=2.5, frame_d=0.4, pass_w=5.0,
              pass_spring=4.8, pass_rise=2.7)
SIDE_W = 2.0


def clip_half(poly, P, nrm):
    """Part of a (possibly concave) polygon on the side of the line through P where (p - P).nrm <= 0."""
    out = []
    n = len(poly)
    for k in range(n):
        a, b = Vector((*poly[k], 0)), Vector((*poly[(k + 1) % n], 0))
        da, db = (a - P).dot(nrm), (b - P).dot(nrm)
        if da <= 1e-9:
            out.append((a.x, a.y))
        if (da < -1e-9 < 1e-9 < db) or (db < -1e-9 < 1e-9 < da):
            x = a + (b - a) * (da / (da - db))
            out.append((x.x, x.y))
    clean = despike(out)
    return clean if len(clean) >= 3 and abs(mk.ring_area(clean)) > 1.0 else []


def despike(poly, eps=0.05):
    """Drop duplicate points, straight-through vertices and zero-width spikes (collinear back-tracks)."""
    pts = [tuple(p) for p in poly]
    changed = True
    while changed and len(pts) >= 3:
        changed = False
        n = len(pts)
        for i in range(n):
            a, b, c = Vector((*pts[i - 1], 0)), Vector((*pts[i], 0)), Vector((*pts[(i + 1) % n], 0))
            u, v = b - a, c - b
            if u.length < eps or v.length < eps or abs(u.normalized().cross(v.normalized()).z) < 1e-3:
                pts.pop(i)
                changed = True
                break
    return pts


def snap_ring(ring, fr, a_lines=(), b_lines=(), tol=0.2):
    """Move ring vertices lying within tol of the frame lines a = const / b = const onto them."""
    out = []
    for p in ring:
        a, b = fr.ab(p)
        for al in a_lines:
            if abs(a - al) < tol:
                a = al
        for bl in b_lines:
            if abs(b - bl) < tol:
                b = bl
        out.append(fr.xy(a, b))
    return out


def damascus(mbs, bd, gen, place, lod=False):
    got = footprint(bd, REF_RINGS["damascus"])
    if got is None:
        return
    ring, eg = got
    fo = find_edge(ring, DAM["door_out"], DAM["facing"])
    if fo is None:
        return generic_gate(mbs, bd, gen, place, lod)
    io, eo, uo = fo
    z_ref = eg[io]
    L = Local(mbs, z_ref)
    fr = Frame(eo.P(uo, 0), -eo.n)
    fi = find_edge(ring, DAM["door_in"], DAM["facing"] - 180)
    zs, zt, zw = DAM["z_sill"], DAM["z_top"], DAM["walk"]
    tdz = DAM["tower_dz"]
    dz_in = (eg[fi[0]] - z_ref) if fi else 0.0
    zl = min(0.0, dz_in) - 0.7
    zb = min(min(eg) - z_ref - 0.8, zl - 0.4)
    if lod:
        doors = [(eo, uo, 4.1, 6.0)] + ([(fi[1], fi[2], 4.6, 7.0)] if fi else [])
        lod_mass(L.solid, ring, zb, zs + 0.3, zt - 0.2, 1.9, 1.0, doors=doors, pointed=True)
        L.flush()
        return
    ui = fi[2] if fi else 8.3
    a_in, b_in = fr.ab(fi[1].P(ui, 0)) if fi else fr.ab(DAM["door_in"])
    zf = ramp(fr.xy(0, 0), 0.0, fr.xy(a_in, b_in), dz_in)
    T_out, T_in = 3.0, 3.0
    a0, a1 = T_out, a_in - T_in
    b0, b1 = -2.6, max(5.5, b_in + DAM_IN["pass_w"] / 2 + 0.5)
    rng = random.Random(616186088)
    bear_b = math.degrees(math.atan2(fr.b.x, fr.b.y))
    # ------------------------------------------------ four masses (s08_damascus.md 3.2, 3.7, 3.8): two towers,
    # the outer screen (merlons at 14 m, the window open to the sky) and the lower inner block behind it
    # (parapet ~10 m above the inner street, roof terrace with a railing); split lines in the gate frame
    bW = min(fr.ab(eo.P(0, 0))[1], fr.ab(eo.P(eo.L, 0))[1])          # facade ends = tower inner sides
    bE = max(fr.ab(eo.P(0, 0))[1], fr.ab(eo.P(eo.L, 0))[1])
    eb = find_edge(ring, DAM["e_tower_back"], bear_b + 90, tol=40, maxd=2.0)
    a_scr = min(fr.ab(DAM["screen_back"])[0], a0 - 0.2)              # back of the screen (in front of the hall)
    parts = []
    if eb:
        aE = fr.ab(eb[1].P(eb[1].L / 2, 0))[0]
        sr = snap_ring(ring, fr, (aE, a_scr), (bW, bE))
        W = clip_half(sr, fr.P(0, bW), fr.b)
        E = clip_half(clip_half(sr, fr.P(0, bE), -fr.b), fr.P(aE, 0), fr.a)
        C = clip_half(clip_half(sr, fr.P(0, bW), -fr.b), fr.P(aE, 0), -fr.a)
        Cf = clip_half(C, fr.P(a_scr, 0), fr.a) if C else []
        Cb = clip_half(C, fr.P(a_scr, 0), -fr.a) if C else []
        if W and E and Cf and Cb:
            parts = [("tower", rect_ring(W)), ("screen", rect_ring(Cf)), ("back", rect_ring(Cb)), ("tower", rect_ring(E))]
    if not parts:
        parts = [("screen", ring)]
    side = find_edge(ring, DAM["side_out"], bear_b + 180, tol=40, maxd=2.0)
    a_s = min(max(fr.ab(DAM["side_out"])[0], a0 + 1.4), a1 - 1.4)
    if side:
        b_face = fr.ab(side[1].P(side[1].u_of(fr.P(a_s, 0)), 0))[1]
        if b0 - b_face < 1.0:
            side = None
    if side:
        zl = min(zl, eg[side[0]] - z_ref - 0.6)
        zb = min(zb, zl - 0.4)
    side_ol = F.pointed(-SIDE_W / 2, SIDE_W / 2, zl, 2.6, 1.2, 5)
    anchors = [("out", DAM["door_out"], DAM["facing"]), ("in", DAM["door_in"], DAM["facing"] - 180),
               ("e_tower_front", fr.xy(-5.9, 17.0), DAM["facing"]), ("w_tower_front", fr.xy(-6.1, -15.7), DAM["facing"]),
               ("w_tower_side", fr.xy(-3.0, bW), bear_b), ("e_tower_side", fr.xy(-2.9, bE), bear_b + 180)]
    if side:
        anchors.append(("side", DAM["side_out"], bear_b + 180))
    if len(parts) > 1:
        anchors += [("scr_back", fr.xy(a_scr, 0.0), DAM["facing"] - 180), ("back_front", fr.xy(a_scr, 0.0), DAM["facing"])]
    win = (11.0, 13.0, 0.55)                                          # window 1.1 x 2.0 m, sill ~11 m (3.4)

    def which(e):
        for key, p, facing in anchors:
            if e.n.dot(compass(facing)) < math.cos(math.radians(40)):
                continue
            u = e.u_of(p)
            if -0.3 < u < e.L + 0.3 and abs(e.off_of(p)) < 1.0:
                return key, u
        return None, None

    def holes(i, e):
        hs = []
        item, u = which(e)
        if item == "out":                                              # central front (NW)
            hs.append({"ol": recess_outline(DAM_OUT, u, zl),
                       "build": lambda mb_, e_, u=u: portal(mb_, e_, u, DAM_OUT, T_out, gen, v0=zl)})
            wol = F.rect(u - win[2], u + win[2], win[0], win[1])        # the window: through the screen
            through = len(parts) > 1
            hs.append({"ol": wol, "build": lambda mb_, e_, wol=wol: (
                F.tunnel(mb_, e_, wol, 0.0, -a_scr, "fort", floor=False) if through else
                (F.tunnel(mb_, e_, wol, 0.0, -0.9, "fort", floor=False), F.face(mb_, e_, wol, "void", -0.9)),
                window_panel(L.deco, e_, u, win))})
            for s in (-1, 1):
                if 0.8 < u + s * 4.6 < e.L - 0.8:
                    hs.append(F.slit_hole(u + s * 4.6, 6.6, 8.2))
                    hs.append(F.slit_hole(u + s * 4.6, 10.2, 11.7))
                    hs.append({"build": lambda mb_, e_, uu=u + s * 4.6: F.machicolation(
                        L.deco, e_, uu, zs - 1.4, zs + 0.8, 1.1, 0.55, cap="pyramid")})     # parapet bartizans
                hs.append(rosette(u + s * 4.0, 7.9, 0.4))                # carved rosettes at the arch haunches
                hs.append(F.roundel(u + s * 2.4, 12.5, 0.35))            # plain discs beside the window panel
                if 0.6 < u + s * 7.4 < e.L - 0.6:
                    hs.append(F.roundel(u + s * 7.4, 9.6, 0.25))
            hs.append({"build": lambda mb_, e_, u=u: crown(L.deco, e_, u, win[1] + 1.3, zt + 0.3, 1.9, proud=0.15)})
        elif item == "in":                                             # inner face (SE)
            hs.append({"ol": zshift(recess_outline(DAM_IN, u, zl - dz_in), dz_in),
                       "build": lambda mb_, e_, u=u: shifted(mb_, dz_in, lambda m: portal(
                           m, e_, u, DAM_IN, T_in, gen, leaves=True, v0=zl - dz_in))})
            for s in (-1, 1):
                if 1.0 < u + s * 4.7 < e.L - 1.0:
                    hs.append(F.roundel(u + s * 4.7, 6.2 + dz_in, 0.35))
            for k in range(3):                                         # three small rosettes over the apex (3.7)
                hs.append(rosette(u + (k - 1) * 0.75, DAM_IN["recess_spring"] + DAM_IN["recess_rise"] + dz_in + 0.95,
                                  0.2))
            for k in range(1, 3):
                uu = u + 6.2 + k * 3.4
                if uu < e.L - 1.2:
                    hs.append(F.slit_hole(uu, 4.0, 5.5))
        elif item == "scr_back":                                       # passage + window through the screen back
            hs.append({"ol": pass_outline(DAM_OUT, u, zl)})
            hs.append({"ol": F.rect(u - win[2], u + win[2], win[0], win[1])})
        elif item == "back_front":                                     # inner block front (hidden) with the passage
            hs.append({"ol": pass_outline(DAM_OUT, u, zl)})
        elif item == "side":                                           # covered side passage (w616338411)
            us = e.u_of(fr.P(a_s, 0))
            ol = ushift(side_ol, us)
            hs.append({"ol": ol, "build": lambda mb_, e_, ol=ol: F.tunnel(mb_, e_, ol, 0.0, -(b0 - b_face), "fort")})
        elif item == "w_tower_side":
            hs.append(F.slit_hole(e.L * 0.5, 6.4, 7.9))
            hs.append(F.slit_hole(e.L * 0.5, 10.4, 11.9))
        elif item == "e_tower_front":                                  # bartizans at the towers' inner corners (3.5)
            um = max(2.0, e.L - 1.8)
            hs.append({"build": lambda mb_, e_, um=um: F.machicolation(L.deco, e_, um, zs + tdz - 2.3, zs + tdz - 0.15,
                                                                        2.0, 0.75, cap="flat")})
            for f, z in ((0.25, 6.2), (0.25, 10.2), (0.45, 8.0)):
                hs.append(F.slit_hole(e.L * f, z, z + 1.5))
            for f, z in ((0.12, 9.3), (0.4, 12.4), (0.62, 5.0), (0.82, 10.0)):
                hs.append(F.roundel(e.L * f, z, 0.22))
        elif item == "w_tower_front":
            um = min(1.8, e.L - 2.0)
            hs.append({"build": lambda mb_, e_, um=um: F.machicolation(L.deco, e_, um, zs + tdz - 2.3, zs + tdz - 0.15,
                                                                        2.0, 0.75, cap="flat")})
            for f, z in ((0.55, 6.2), (0.55, 10.2), (0.78, 8.0), (0.78, 12.2)):
                hs.append(F.slit_hole(e.L * f, z, z + 1.5))
            for f, z in ((0.12, 6.5), (0.4, 12.6), (0.4, 4.8), (0.9, 10.6)):
                hs.append(F.roundel(e.L * f, z, 0.22))
        elif item == "e_tower_side":
            hs.append(F.slit_hole(e.L * 0.5, 7.0, 8.5))
        elif e.L > 6.0 and abs(e.n.dot(fr.a)) < 0.9:                   # plain side faces: a couple of slits
            for f in (0.33, 0.67):
                z = 7.0 + rng.uniform(-1, 1)
                hs.append(F.slit_hole(e.L * f, z, z + 1.6))
        return hs

    for kind, pr in parts:
        if kind == "back":                                             # solid parapet + railing on the terrace
            F.battlemented_ring(L.solid, pr, zb, DAM["back_walk"], DAM["back_sill"], DAM["back_sill"] + 0.25, 0.6,
                                "fort", style="flat", holes=holes, layout=lambda i: (999.0, 999.0, 0.5), slits=False)
            F.ring_rail(L.deco, pr, DAM["back_sill"] + 0.25, h=0.9, inset=0.3, post=2.0)
            continue
        dz = tdz if kind == "tower" else 0.0
        lay = (1.5, 1.45, 0.95) if kind == "tower" else (1.1, 1.05, 0.85)
        _E, _inner, bats = F.battlemented_ring(L.solid, pr, zb, zw + dz, zs + dz, zt + dz, 0.8, "fort", style="pointed",
                                               holes=holes, layout=lambda i, lay=lay: lay, slit_every=2)
        for bat in bats:                                               # tall spade finials (photos GD:06, GD:20)
            if bat.e.n.dot(fr.a) > 0.9:                                # not on the screen's back
                continue
            for j in range(1, len(bat.merlons) - 1):
                if bat.styles[j] == "pointed":
                    a, b = bat.merlons[j]
                    c = bat.e.P((a + b) / 2, 0, -0.4)
                    F.obox(L.deco, c, bat.e.t, bat.e.n, 0.28, 0.28, zt + dz - 0.15, zt + dz + 0.4, "fort")
                    F.pyramid(L.deco, c, bat.e.t, bat.e.n, 0.36, zt + dz + 0.4, 0.55, "fort")
    # ------------------------------------------------ the bent passage: one hall between the two portals
    C = fr.rect(a0, a1, b0, b1)
    hl = {3: [pass_outline(DAM_OUT, b1, zl)],                     # side 3 runs b1 -> b0 at a = a0 (u = b1 - b)
          1: [pass_outline(DAM_IN, b_in - b0, zl, dz_in)]}        # side 1 runs b0 -> b1 at a = a1 (u = b - b0)
    if side:
        hl[0] = [ushift(side_ol, a_s - a0)]                       # side 0 runs a0 -> a1 at b = b0
    hall(L.solid, C, zf, 5.6, 2.0, zl - 0.3, dome=0.3, holes=hl, N=12)          # crown ~8 m (s08 3.6: 7-8 m)
    floor(L.solid, fr.rect(0.0, a0, -DAM_OUT["recess_w"] / 2, DAM_OUT["recess_w"] / 2), zf)
    floor(L.solid, fr.rect(a1, a_in, b_in - DAM_IN["recess_w"] / 2, b_in + DAM_IN["recess_w"] / 2), zf)
    if side:                                                          # ramps from the hall to the street outside
        p_in = fr.xy(a_s, b0)
        floor(L.solid, fr.rect(a_s - SIDE_W / 2, a_s + SIDE_W / 2, b_face, b0),
              ramp(p_in, zf(*p_in), fr.xy(a_s, b_face), eg[side[0]] - z_ref))
    L.flush()


# ====================================================================== Lions' Gate
# OSM: building w288395731; passage w288395746 (building_passage, sett) outer (893.6,468.0) -> inner
# (882.4,466.3); side passage w291836745 from the south face (889.5,461.2) to (888.4,467.2).
LIO = {"door_out": (893.6, 468.0), "door_in": (882.4, 466.3), "side_out": (889.5, 461.2), "facing": 80.0,
       "z_sill": 12.9, "z_top": 13.9, "walk": 11.8}
LIO_OUT = dict(recess_w=4.6, recess_spring=5.2, recess_rise=2.45, recess_d=0.6, band=0.42, band_rise=0.45,
               door="segment", door_w=3.3, door_spring=4.1, door_rise=0.55, frame_d=0.45, pass_w=4.0, pass_spring=4.2,
               pass_rise=2.1, panel=(1.6, 0.5))
LIO_IN = (5.0, 4.7, 2.9)                      # big open inner arch: width, springing, rise (photo s10 R:06)


def lions(mbs, bd, gen, place, lod=False):
    got = footprint(bd, REF_RINGS["lions"])
    if got is None:
        return
    ring, eg = got
    fo = find_edge(ring, LIO["door_out"], LIO["facing"])
    if fo is None:
        return generic_gate(mbs, bd, gen, place, lod)
    io, eo, uo = fo
    z_ref = eg[io]
    L = Local(mbs, z_ref)
    fr = Frame(eo.P(uo, 0), -eo.n)
    fi = find_edge(ring, LIO["door_in"], LIO["facing"] + 180)
    zs, zt, zw = LIO["z_sill"], LIO["z_top"], LIO["walk"]
    dz_in = (eg[fi[0]] - z_ref) if fi else 0.0
    zl = min(0.0, dz_in) - 0.7
    base = gate_base(ring, eg, z_ref, zl)
    W_IN, S_IN, R_IN = LIO_IN
    if lod:
        doors = [(eo, uo, 3.3, 4.6)] + ([(fi[1], fi[2], W_IN, S_IN + R_IN)] if fi else [])
        lod_mass(L.solid, ring, min(base), zs, zt, 2.4, 1.9, doors=doors)
        L.flush()
        return
    ui = fi[2] if fi else 6.0
    a_in, b_in = fr.ab(fi[1].P(ui, 0)) if fi else (10.0, 0.0)
    zf = ramp(fr.xy(0, 0), 0.0, fr.xy(a_in, b_in), dz_in)
    T_out, T_in = 2.6, 2.6
    a0, a1 = T_out, a_in - T_in
    bh = 3.2
    side = find_edge(ring, LIO["side_out"], None, maxd=2.0)
    if side and side[0] in (io, fi[0] if fi else -1):
        side = None
    a_s = min(max(fr.ab(LIO["side_out"])[0], a0 + 1.2), a1 - 1.2)
    sgn = 1 if fr.ab(LIO["side_out"])[1] > 0 else -1
    if side:
        zl = min(zl, eg[side[0]] - z_ref - 0.6)
        base = [min(b_, zl - 0.4) for b_ in base]
    side_ol = F.pointed(-0.9, 0.9, zl, 2.5, 1.0, 5)
    b_face = fr.ab(side[1].P(side[1].u_of(fr.P(a_s, 0)), 0))[1] if side else 0.0

    def holes(i, e):
        hs = []
        if i == io:                                                   # east front: lions, machicolation
            u = uo
            hs.append({"ol": recess_outline(LIO_OUT, u, zl),
                       "build": lambda mb_, e_, u=u: portal(mb_, e_, u, LIO_OUT, T_out, gen, v0=zl)})
            for s in (-1, 1):                                         # two confronted pairs of Baybars' panthers
                for k, f in ((0, 1), (1, -1)):
                    uu = u + s * (3.65 + (0.68 if k else -0.68))
                    if 0.7 < uu < e.L - 0.7:
                        hs.append({"build": lambda mb_, e_, uu=uu, f=f * s: lion(L.deco, e_, uu, 6.5, f, 1.0)})
                if 1.0 < u + s * 3.6 < e.L - 1.0:
                    hs.append(niche(u + s * 3.6, 10.7, 0.95, 11.6, 0.6, depth=0.25, boss=True))
                    hs.append(F.roundel(u + s * 3.6, 10.1, 0.22))
            hs.append({"build": lambda mb_, e_, u=u: F.machicolation(L.deco, e_, u, 10.1, 12.2, 2.2, 0.7, cap="flat")})
            hs.append(rosette(u, 8.55, 0.34))
            hs.append({"build": lambda mb_, e_, u=u: crown(L.deco, e_, u, zt, zt + 0.5, 1.3)})
        elif fi and i == fi[0]:                                        # inner face: the big open arch
            u = ui
            hs.append({"ol": zshift(F.pointed(u - W_IN / 2, u + W_IN / 2, zl - dz_in, S_IN, R_IN, 7), dz_in),
                       "build": lambda mb_, e_, u=u: shifted(mb_, dz_in, lambda m: arch_open(
                           m, e_, u, W_IN, S_IN, R_IN, T_in, 0.45, 0.5, v0=zl - dz_in))})
            for s in (-1, 1):
                if 0.8 < u + s * 4.2 < e.L - 0.8:
                    hs.append(F.slit_hole(u + s * 4.2, 8.6, 10.2))
        elif side and i == side[0]:                                    # side door to El-Ghazali square
            us = side[1].u_of(fr.P(a_s, 0))
            ol = ushift(side_ol, us)
            hs.append({"ol": ol, "build": lambda mb_, e_, ol=ol: F.tunnel(mb_, e_, ol, 0.0, -abs(b_face - sgn * bh),
                                                                          "fort")})
            if us + 3.0 < e.L - 0.8:
                hs.append(F.slit_hole(us + 3.0, 8.0, 9.6))
        elif e.L > 6:
            hs.append(F.slit_hole(e.L * 0.5, 8.0, 9.6))
        return hs
    F.battlemented_ring(L.solid, ring, base, zw, zs, zt, 0.8, "fort", style="flat", holes=holes,
                        layout=lambda i: (2.0, 1.9, 0.5), slit_every=1)
    # ------------------------------------------------ straight passage: portal -> vaulted hall -> big arch
    C = fr.rect(a0, a1, -bh, bh)
    hl = {3: [pass_outline(LIO_OUT, bh, zl)],
          1: [F.pointed(b_in + bh - W_IN / 2, b_in + bh + W_IN / 2, zl, S_IN + dz_in, R_IN, 7)]}
    if side:
        if sgn > 0:                                                   # side 2 runs a1 -> a0 at b = +bh
            hl[2] = [ushift(side_ol, a1 - a_s)]
        else:                                                         # side 0 runs a0 -> a1 at b = -bh
            hl[0] = [ushift(side_ol, a_s - a0)]
    hall(L.solid, C, zf, 5.7, 2.6, zl - 0.3, dome=0.5, holes=hl, N=10)
    floor(L.solid, fr.rect(0.0, a0, -LIO_OUT["recess_w"] / 2, LIO_OUT["recess_w"] / 2), zf, "setts")
    floor(L.solid, fr.rect(a1, a_in, b_in - W_IN / 2 - 0.3, b_in + W_IN / 2 + 0.3), zf, "setts")
    if side:                                                          # ramps from the hall to the square outside
        q = fr.rect(a_s - 0.9, a_s + 0.9, bh, b_face) if sgn > 0 else fr.rect(a_s - 0.9, a_s + 0.9, b_face, -bh)
        p_in = fr.xy(a_s, sgn * bh)
        floor(L.solid, q, ramp(p_in, zf(*p_in), fr.xy(a_s, b_face), eg[side[0]] - z_ref))
    L.flush()


# ====================================================================== Zion Gate
# OSM: building w290671706; passage w722675054 (building_passage): outer door (198.4,-418.2) in the south
# face -> turn (200.5,-411.6) -> inner door (210.7,-415.7) in the east face (L-shaped bent entrance).
ZIO = {"door_out": (198.4, -418.2), "door_in": (210.7, -415.7), "turn": (200.5, -411.6), "facing": 201.0,
       "z_sill": 13.0, "z_top": 14.0, "walk": 11.9}
ZIO_OUT = dict(recess_w=4.2, recess_spring=4.5, recess_rise=2.3, recess_d=0.5, band=0.38, band_rise=0.4,
               door="flat", door_w=2.9, door_h=4.0, door_r=0.08, frame_d=0.4, pass_w=3.5, pass_spring=4.1,
               pass_rise=1.9, lintel=True)
ZIO_IN = dict(recess_w=3.8, recess_spring=4.0, recess_rise=2.0, recess_d=0.25, band=0.3, band_rise=0.3,
              door="flat", door_w=3.0, door_h=3.9, door_r=0.08, frame_d=0.35, pass_w=3.5, pass_spring=4.0,
              pass_rise=1.9, lintel=True)


def zion(mbs, bd, gen, place, lod=False):
    got = footprint(bd, REF_RINGS["zion"])
    if got is None:
        return
    ring, eg = got
    fo = find_edge(ring, ZIO["door_out"], ZIO["facing"])
    if fo is None:
        return generic_gate(mbs, bd, gen, place, lod)
    io, eo, uo = fo
    uo = min(max(uo, 2.6), eo.L - 2.6)
    z_ref = eg[io]
    L = Local(mbs, z_ref)
    fr = Frame(eo.P(uo, 0), -eo.n)
    fi = find_edge(ring, ZIO["door_in"], ZIO["facing"] - 90)
    zs, zt, zw = ZIO["z_sill"], ZIO["z_top"], ZIO["walk"]
    dz_in = (eg[fi[0]] - z_ref) if fi else 0.0
    zl = min(0.0, dz_in) - 0.7
    base = gate_base(ring, eg, z_ref, zl)
    if lod:
        doors = [(eo, uo, 2.9, 4.2)] + ([(fi[1], fi[2], 3.0, 4.0)] if fi else [])
        lod_mass(L.solid, ring, min(base), zs, zt, 2.2, 1.5, doors=doors)
        L.flush()
        return
    if fi is None:
        return generic_gate(mbs, bd, gen, place, lod)
    ui = fi[2]
    a_in, b_in = fr.ab(fi[1].P(ui, 0))
    zf = ramp(fr.xy(0, 0), 0.0, fr.xy(a_in, b_in), dz_in)
    sgn = 1 if b_in > 0 else -1                                       # the inner door lies towards +-b
    T_out, T_in = 2.6, 2.6
    ac = max(a_in, 5.0)                                               # axis of the second leg
    aA0, aA1, bA0, bA1 = T_out, ac + 2.3, -2.3, 2.3                   # hall A over the corner
    bB0, bB1 = sgn * 2.9, b_in - sgn * T_in                           # cell B along the second leg
    arch = F.pointed(-1.75, 1.75, zl, 3.7, 1.9, 6)                    # transverse arch A|B (0.6 m)
    rng = random.Random(290671706)

    def holes(i, e):
        hs = []
        if i == io:                                                   # south front: bullet scars, niches
            u = uo
            hs.append({"ol": recess_outline(ZIO_OUT, u, zl),
                       "build": lambda mb_, e_, u=u: portal(mb_, e_, u, ZIO_OUT, T_out, gen, leaves=False, v0=zl)})
            for s, du in ((1, 3.7), (-1, 3.2)):
                if 1.0 < u + s * du < e.L - 1.0:
                    hs.append(niche(u + s * du, 1.7, 1.25, 3.4, 0.75, depth=0.32, slit=True))
            hs.append({"build": lambda mb_, e_, u=u: F.machicolation(L.deco, e_, u, 8.5, 10.7, 1.8, 0.75, cap="flat")})
            for s in (-1, 1):
                if 1.0 < u + s * 2.6 < e.L - 1.0:
                    hs.append(F.slit_hole(u + s * 2.6, 7.4, 8.9))
            for k in range(2):
                uu = u + 6.5 + k * 3.5
                if uu < e.L - 1.0:
                    hs.append(F.slit_hole(uu, 6.0 + k, 7.5 + k))
            hs.append({"build": lambda mb_, e_, u=u: pits(L.deco, e_, rng, 0.3, e_.L - 0.3, 0.6, 10.5, 190,
                                                         avoid=((u - 2.6, u + 2.6, -1, 7.4),))})
        elif i == fi[0]:                                               # east face (inside the city)
            u = ui
            hs.append({"ol": zshift(recess_outline(ZIO_IN, u, zl - dz_in), dz_in),
                       "build": lambda mb_, e_, u=u: shifted(mb_, dz_in, lambda m: portal(
                           m, e_, u, ZIO_IN, T_in, gen, leaves=False, v0=zl - dz_in))})
            for s_ in (-1, 1):                                          # two small windows high up (GZ:16)
                uu = u + s_ * 2.7
                if 3.4 < uu < e.L - 1.0:
                    hs.append(F.dark_hole(F.rect(uu - 0.3, uu + 0.3, 10.5, 11.2), depth=0.5))
        elif e.L > 6:
            for f in (0.35, 0.7):
                z = 6.5 + rng.uniform(-1, 1)
                hs.append(F.slit_hole(e.L * f, z, z + 1.5))
        return hs
    F.battlemented_ring(L.solid, ring, base, zw, zs, zt, 0.8, "fort", style="flat", holes=holes,
                        layout=lambda i: (1.6, 1.5, 0.55), slit_every=1)
    # ------------------------------------------------ L-shaped passage
    CA = fr.rect(aA0, aA1, bA0, bA1)
    CB = fr.rect(ac - 2.0, ac + 2.0, min(bB0, bB1), max(bB0, bB1))
    hlA = {3: [pass_outline(ZIO_OUT, bA1, zl)]}
    hlB = {}
    if sgn < 0:     # leg B towards -b: hall A side 0 (b = bA0, runs +a); cell B side 2 (b = bB0, runs -a)
        hlA[0] = [ushift(arch, ac - aA0)]
        hlB[2] = [ushift(arch, 2.0)]
        hlB[0] = [pass_outline(ZIO_IN, 2.0, zl, dz_in)]
        tun_e = fr.edge(ac - 5, bA0, ac + 5, bA0)                     # n = -b
        gap = (fr.rect(ac - 1.75, ac + 1.75, bB0, bA0), bA0 - bB0)
        inner_floor = fr.rect(ac - ZIO_IN["recess_w"] / 2, ac + ZIO_IN["recess_w"] / 2, b_in, bB1)
    else:
        hlA[2] = [ushift(arch, aA1 - ac)]
        hlB[0] = [ushift(arch, 2.0)]
        hlB[2] = [pass_outline(ZIO_IN, 2.0, zl, dz_in)]
        tun_e = fr.edge(ac + 5, bA1, ac - 5, bA1)                     # n = +b
        gap = (fr.rect(ac - 1.75, ac + 1.75, bA1, bB0), bB0 - bA1)
        inner_floor = fr.rect(ac - ZIO_IN["recess_w"] / 2, ac + ZIO_IN["recess_w"] / 2, bB1, b_in)
    hall(L.solid, CA, zf, 4.8, 2.3, zl - 0.3, dome=0.4, holes=hlA, N=10)
    hall(L.solid, CB, zf, 4.6, 2.0, zl - 0.3, dome=0.3, holes=hlB, N=10)
    F.tunnel(L.solid, tun_e, ushift(arch, 5.0), 0.0, gap[1], "fort")
    floor(L.solid, fr.rect(0.0, aA0, -ZIO_OUT["recess_w"] / 2, ZIO_OUT["recess_w"] / 2), zf)
    floor(L.solid, gap[0], zf)
    floor(L.solid, inner_floor, zf)
    L.flush()


# ====================================================================== Herod's Gate
# Not a building in OSM: the gate is the projecting tower of wall way 137726904 (vertices 50-53:
# (586.8,704.2) (585.5,709.0) (574.7,706.1) (576.1,700.7)); HEROD_RECORD extends it 3.5 m back to the inner
# face of the curtain.  Entrance in the north face (opened 1875), groin-vaulted hall with a boss (GH:04),
# straight vaulted passage south into the city (GH:16); the old entrance in the east side is blocked (GH:18).
HEROD_RING = [(577.0, 697.3), (587.7, 700.8), (585.5, 709.0), (574.7, 706.1)]
HEROD_RECORD = {"id": "m_herods_gate", "osm": "m_herods_gate", "tier": "mid", "ring": HEROD_RING,
                "tags": {"name": "باب الساهرة", "name:en": "Herod's Gate", "building": "yes"},
                "why": "Herod's Gate tower: OSM wall way 137726904 vertices 50-53 extended 3.5 m back to the "
                       "inner face of the curtain (data/reference/gates.md)"}
HER = {"door": (580.1, 707.55), "facing": 345.0, "z_sill": 14.1, "z_top": 15.2, "walk": 13.0}
HER_OUT = dict(recess_w=3.7, recess_spring=3.3, recess_rise=2.0, recess_d=0.4, band=0.3, band_rise=0.3,
               door="pointed", door_w=3.0, door_spring=3.0, door_rise=1.6, frame_d=0.4, pass_w=3.5, pass_spring=3.3,
               pass_rise=1.8)
HER_IN = (3.4, 3.4, 1.9)


def herod(mbs, bd, gen, place, lod=False):
    got = footprint(bd, REF_RINGS["herod"])
    if got is None:
        return
    ring, eg = got
    fo = find_edge(ring, HER["door"], HER["facing"], maxd=3.0)
    if fo is None:
        return generic_gate(mbs, bd, gen, place, lod)
    io, eo, uo = fo
    uo = min(max(uo, 2.5), eo.L - 2.5)
    z_ref = eg[io]
    L = Local(mbs, z_ref)
    fr = Frame(eo.P(uo, 0), -eo.n)
    fi = find_edge(ring, fr.xy(8.5, 0), HER["facing"] - 180, maxd=3.0)
    zs, zt, zw = HER["z_sill"], HER["z_top"], HER["walk"]
    dz_in = (eg[fi[0]] - z_ref) if fi else 0.0
    zl = min(0.0, dz_in) - 0.7
    base = gate_base(ring, eg, z_ref, zl)
    W_IN, S_IN, R_IN = HER_IN
    if lod:
        lod_mass(L.solid, ring, min(base), zs, zt, 2.0, 1.5, doors=[(eo, uo, 3.0, 4.6)])
        L.flush()
        return
    if fi is None:
        return generic_gate(mbs, bd, gen, place, lod)
    ui = fi[1].u_of(fr.P(8.0, 0))
    a_in = fr.ab(fi[1].P(ui, 0))[0]
    zf = ramp(fr.xy(0, 0), 0.0, fr.xy(a_in, 0), dz_in)
    T_out, T_in = 2.0, 2.1
    a0, a1 = T_out, a_in - T_in
    bh = 2.3
    bear_b = math.degrees(math.atan2(fr.b.x, fr.b.y))
    east = find_edge(ring, fr.xy(2.5, 5.6), bear_b, tol=40, maxd=3.0)

    def holes(i, e):
        hs = []
        if i == io:
            u = uo
            hs.append({"ol": recess_outline(HER_OUT, u, zl),
                       "build": lambda mb_, e_, u=u: portal(mb_, e_, u, HER_OUT, T_out, gen, v0=zl)})
            hs.append(F.dark_hole(F.rect(u - 0.4, u + 0.4, 7.6, 8.8), depth=0.9, grille_w=0.8, gen=gen))  # GH:09
            for s in (-1, 1):
                if 1.0 < u + s * 3.4 < e.L - 1.0:
                    hs.append(F.slit_hole(u + s * 3.4, 9.0, 10.5))
            hs.append(rosette(u, 10.9, 0.3))                           # roundel above the window (GH:09)
        elif i == fi[0]:
            u = ui
            hs.append({"ol": zshift(F.pointed(u - W_IN / 2, u + W_IN / 2, zl - dz_in, S_IN, R_IN, 7), dz_in),
                       "build": lambda mb_, e_, u=u: shifted(mb_, dz_in, lambda m: arch_open(
                           m, e_, u, W_IN, S_IN, R_IN, T_in, 0.32, 0.35, v0=zl - dz_in))})
        elif east and i == east[0]:                                    # the blocked original entrance
            u = e.L * 0.45
            hs.append(niche(u, zl + 0.2, 2.6, 2.7, 1.5, depth=0.35, shell=False))
            hs.append(rosette(u - 1.1, 5.0, 0.3))
            hs.append(rosette(u + 1.1, 5.0, 0.3))
            hs.append(F.slit_hole(u, 7.6, 9.1))
        elif e.L > 6:
            hs.append(F.slit_hole(e.L * 0.5, 7.5, 9.0))
        return hs
    F.battlemented_ring(L.solid, ring, base, zw, zs, zt, 0.8, "fort", style="flat", holes=holes,
                        layout=lambda i: (1.5, 1.6, 0.55), slit_every=1)
    C = fr.rect(a0, a1, -bh, bh)
    hall(L.solid, C, zf, 4.2, 2.2, zl - 0.3, dome=0.5, N=10,
         holes={3: [pass_outline(HER_OUT, bh, zl)], 1: [F.pointed(bh - W_IN / 2, bh + W_IN / 2, zl, S_IN + dz_in, R_IN, 7)]})
    floor(L.solid, fr.rect(0.0, a0, -HER_OUT["recess_w"] / 2, HER_OUT["recess_w"] / 2), zf)
    floor(L.solid, fr.rect(a1, a_in, -W_IN / 2 - 0.3, W_IN / 2 + 0.3), zf)
    L.flush()


# ====================================================================== wall sections (Dung, New Gate)
# How the OSM city-wall line relates to the masonry.  At Lions', Zion, Damascus and Herod's Gates the OSM
# line runs exactly along the gates' outer faces, so it is taken as the OUTER face of the curtain: the wall
# (and the Dung / New Gate sections) lie T/2 inside it.  "centre" reproduces make_spec's centred slabs.
WALL_LINE = "outer"
def wall_run(mb, e, ua, ub, ka, kb, H, T, z_bot, holes_out=(), holes_in=(), cap_a=None, cap_b=None,
             cw=1.6, mw=1.6, cr=0.45, mh=0.85, slit_every=1, col=None):
    """Crenellated curtain along edge e (centre line, outside on the right) from u=ua to ub with mitre
    slopes ka / kb: fortifications.wall_run's profile (outer face with parapet, merlons and slits, walk,
    low inner parapet, inner face) with absolute heights (H = merlon tops, z_bot = foot) and openings in
    BOTH faces (holes_out in u at the outer face, holes_in in u at the inner face; their "build"
    callbacks get the shifted frames).  Inner-face holes need square ends (ka = kb = 0)."""
    zs = H - mh
    zw = zs - F.PARAPET_H
    d = F.GATE_PARAPET
    o_out, o_par, o_in = T / 2, T / 2 - d, -T / 2
    ip_t, ip_h = 0.5, 1.0
    o_q = o_in + ip_t
    ua_o, ub_o = ua + ka * o_out, ub + kb * o_out
    ua_p, ub_p = ua + ka * o_par, ub + kb * o_par
    bat = F.Battlement(e, ua_o, ub_o, ua_p, ub_p, zw, zs, H, d, cw, cw, mw, cr, slits=slit_every > 0,
                       slit_every=max(1, slit_every))
    F.face(mb, e, bat.outline(z_bot), "fort", o_out, holes=[h["ol"] for h in holes_out if h.get("ol")] +
           [[(u, z) for u, z in s] for s in bat.slits], col=col)
    so = F.ShiftedEdge(e, o_out)
    for h in holes_out:
        if h.get("build"):
            h["build"](mb, so)
    bat.e = so
    bat.build(mb, "fort", col, tops=False)
    for j in range(len(bat.merlons)):
        a, b = bat.merlons[j]
        if j == 0 or j == len(bat.merlons) - 1:
            if len(bat.merlons) == 1:
                q = [e.P(ua_o, H, o_out), e.P(ub_o, H, o_out), e.P(ub_p, H, o_par), e.P(ua_p, H, o_par)]
            elif j == 0:
                q = [e.P(ua_o, H, o_out), e.P(b, H, o_out), e.P(b, H, o_par), e.P(ua_p, H, o_par)]
            else:
                q = [e.P(a, H, o_out), e.P(ub_o, H, o_out), e.P(ub_p, H, o_par), e.P(a, H, o_par)]
            mb.poly(q, "fort", UP, col=col)
        else:
            bat.merlon_top(mb, j, "fort", col)
    ua_q, ub_q = ua + ka * o_q, ub + kb * o_q
    ua_i, ub_i = ua + ka * o_in, ub + kb * o_in
    mb.poly([e.P(ua_p, zw, o_par), e.P(ub_p, zw, o_par), e.P(ub_q, zw, o_q), e.P(ua_q, zw, o_q)], "fort", UP, col=col)
    mb.poly([e.P(ua_q, zw, o_q), e.P(ub_q, zw, o_q), e.P(ub_q, zw + ip_h, o_q), e.P(ua_q, zw + ip_h, o_q)], "fort",
            e.n, col=col)
    mb.poly([e.P(ua_q, zw + ip_h, o_q), e.P(ub_q, zw + ip_h, o_q), e.P(ub_i, zw + ip_h, o_in),
             e.P(ua_i, zw + ip_h, o_in)], "fort", UP, col=col)
    zti = zw + ip_h
    si = F.ShiftedEdge(e, o_in)
    hin = [h["ol"] for h in holes_in if h.get("ol")]
    if hin:
        F.face(mb, si, [(ua, z_bot), (ub, z_bot), (ub, zti), (ua, zti)], "fort", 0.0, holes=hin, col=col, inward=True)
    else:
        mb.poly([e.P(ua_i, z_bot, o_in), e.P(ub_i, z_bot, o_in), e.P(ub_i, zti, o_in), e.P(ua_i, zti, o_in)],
                "fort", -e.n, col=col)
    for h in holes_in:
        if h.get("build"):
            h["build"](mb, si)
    for cap, u0, k, sgn in ((cap_a, ua, ka, -1), (cap_b, ub, kb, 1)):
        if not cap:
            continue
        sec = [(o_in, z_bot), (o_out, z_bot), (o_out, H), (o_par, H), (o_par, zw), (o_q, zw), (o_q, zti), (o_in, zti)]
        mb.poly([e.P(u0 + k * o, z, o) for o, z in sec], "fort", e.t * sgn, col=col)
    return bat


def voussoirs(mb, e, ol, v_spring, rng, depth=0.16, n=11, col=(0.9, 0.87, 0.82)):
    """Rusticated voussoirs and alternating jamb quoins around an arched opening (New Gate): rough
    bossed blocks standing proud of the face (frame e, face at off 0, n pointing away from the wall)."""
    top = [p for p in ol if p[1] >= v_spring - 1e-6]
    us = [p[0] for p in ol]
    u0, u1 = min(us), max(us)
    uc = (u0 + u1) / 2
    pts = [Vector((u, z, 0)) for u, z in top]
    acc = [0.0]
    for p, q in zip(pts, pts[1:]):
        acc.append(acc[-1] + (q - p).length)
    total = acc[-1]
    c = Vector((uc, v_spring - 0.8, 0))

    def at(s):
        for j in range(len(acc) - 1):
            if acc[j] <= s <= acc[j + 1]:
                return pts[j].lerp(pts[j + 1], (s - acc[j]) / max(acc[j + 1] - acc[j], 1e-9))
        return pts[-1]

    def block(quad, dd, cc):
        mb.poly([e.P(p.x, p.y, dd) for p in quad], "fort", e.n, col=cc)
        m = sum(quad, Vector((0, 0, 0))) / 4
        for p, q in zip(quad, quad[1:] + quad[:1]):
            mb.poly([e.P(p.x, p.y, 0), e.P(q.x, q.y, 0), e.P(q.x, q.y, dd), e.P(p.x, p.y, dd)], "fort",
                    e.P((p.x + q.x) / 2, (p.y + q.y) / 2, 0) - e.P(m.x, m.y, 0), col=cc)
    for k in range(n):
        pa, pb = at(total * (k + 0.05) / n), at(total * (k + 0.95) / n)
        Lr = 0.78 if k % 2 == 0 else 0.56
        ra, rb = (pa - c).normalized(), (pb - c).normalized()
        g = rng.uniform(0.92, 1.03)
        block([pa, pb, pb + rb * Lr, pa + ra * Lr], depth * rng.uniform(0.8, 1.2), tuple(x * g for x in col))
    z, k = 0.05, 0
    while z < v_spring - 0.2:
        h = min(0.55, v_spring - z)
        for uu, sg in ((u0, -1), (u1, 1)):
            w = 0.75 if k % 2 == 0 else 0.45
            a, b = sorted((uu, uu + sg * w))
            g = rng.uniform(0.92, 1.03)
            block([Vector((a, z + 0.03, 0)), Vector((b, z + 0.03, 0)), Vector((b, z + h - 0.03, 0)),
                   Vector((a, z + h - 0.03, 0))], depth * rng.uniform(0.7, 1.1), tuple(x * g for x in col))
        z += h
        k += 1


def section_edge(S):
    """Centre line of the section: along the OSM wall line through the gate node, S["half"] metres either
    side, outside on the right, moved T/2 inwards when the OSM line is the outer face (WALL_LINE)."""
    a, b = v2(S["line"][0]), v2(S["line"][1])
    t = (b - a).normalized()
    nrm = Vector((t.y, -t.x, 0.0))
    g = a + t * (v2(S["gate"]) - a).dot(t)
    if WALL_LINE == "outer":
        g = g - nrm * (S["thick"] / 2)
    return F.Edge(tuple((g - t * S["half"]).xy), tuple((g + t * S["half"]).xy))


def section_ring(S):
    e = section_edge(S)
    T = S["thick"]
    return rect_ring([e.P(0, 0, T / 2).xy, e.P(e.L, 0, T / 2).xy, e.P(e.L, 0, -T / 2).xy, e.P(0, 0, -T / 2).xy])


def gate_section(mbs, bd, gen, lod, S):
    """A gate that is an opening through the curtain (Dung Gate, New Gate): a crenellated section of the wall
    (same profile as build_walls) along the OSM wall line, the opening through it, its dressing on both
    faces and the passage floor.  Heights: the merlon tops follow make_spec.generic_walls (inner street
    + S["height"] + the merlon height) so the section meets the circuit."""
    got = footprint(bd, S["ref_ring"])
    if got is None:
        return
    ring, eg = got
    e = section_edge(S)
    T = S["thick"]
    n = len(ring)
    zo = [eg[i] for i in range(n) if F.Edge(ring[i], ring[(i + 1) % n]).n.dot(e.n) > 0.7]
    zi = [eg[i] for i in range(n) if F.Edge(ring[i], ring[(i + 1) % n]).n.dot(e.n) < -0.7]
    z_out = min(zo) if zo else bd["ground"]
    z_in = max(zi) if zi else bd["ground"]
    dz = z_in - z_out
    L = Local(mbs, z_out)
    H = dz + S["height"] + S["mh"]
    zb = min(0.0, dz) - 2.5
    uc = e.L / 2
    so = F.ShiftedEdge(e, T / 2)
    if lod:
        lod_mass(L.solid, section_ring(S), zb, H - S["mh"], H, 2.1, 1.5, doors=[(so, uc, S["w"], S["h"])])
        L.flush()
        return
    rng = random.Random(len(bd["id"]) * 7919)
    zl = min(0.0, dz) - 0.6
    ol = S["outline"](uc, zl)
    er = F.Edge(e.P(e.L, 0, -T / 2).xy, e.P(0, 0, -T / 2).xy)             # inner face seen from the city
    hout = [{"ol": ol, "build": lambda mb_, e_: (F.tunnel(mb_, e_, ol, 0.0, -T, "fort"), S["dress_out"](L, e_, uc, rng))}]
    hin = [{"ol": ol, "build": lambda mb_, e_: S["dress_in"](L, er, er.L - uc, rng, dz)}]
    for du, z0, z1 in S.get("slits", ()):
        for s in (-1, 1):
            hout.append(F.slit_hole(uc + s * du, z0, z1))
    wall_run(L.solid, e, 0.0, e.L, 0.0, 0.0, H, T, zb, holes_out=hout, holes_in=hin, cap_a="full", cap_b="full",
             cw=S["cw"], mw=S["mw"], cr=S["cr"], mh=S["mh"], slit_every=1)
    # floor: the footprint (the street mesh has a hole exactly there), a plane through both thresholds
    floor(L.solid, ring, ramp(e.P(uc, 0, T / 2).xy, 0.0, e.P(uc, 0, -T / 2).xy, dz), S.get("floor", "setts"))
    L.flush()


# Dung Gate: OSM wall way 391433911 (vertices 21-24), gate node 29944308, footprint w1545285986 (4.2 x 2.3 m:
# the passage roof).  Opening ~4.2 m wide, ~4.4 m high (GU:08, GU:09, GU:13); the 1952 widening kept the small
# Ottoman gate's carved pointed arch above the new opening (GU:09).
def _dung_out(L, e, uc, rng):
    ol = DUNG["outline"](uc, 0.0)
    band_arch(L.deco, e, ol, 3.7, 0.38, 0.0, 0.0, 0.08)
    for s in (-1, 1):
        jamb_band(L.deco, e, uc + s * (2.1 + 0.19), -0.6, 3.7, 0.38, 0.0, 0.08)
    F.section_prism(L.deco, e, uc - 2.4, uc + 2.4, [(0, 5.0), (0.18, 5.0), (0.18, 5.22), (0, 5.3)], "ashlar",
                    skip=(3,), col=DRESSED)                                        # moulding under the old arch
    arch = F.pointed(uc - 1.35, uc + 1.35, 5.3, 5.7, 1.55, 7)
    band_arch(L.deco, e, arch, 5.7, 0.32, 0.3, 0.0, 0.1, col=CARVED)
    F.face(L.deco, e, arch, "ashlar", 0.03, col=(0.88, 0.85, 0.8))
    for k in range(5):                                                              # cusps in the tympanum
        a = math.pi * (k + 0.5) / 5
        F.disc(L.deco, e, uc + math.cos(a) * 0.9, 5.75 + math.sin(a) * 0.85, 0.2, 0.06, "ashlar", off=0.03, seg=8,
               col=CARVED)
    F.disc(L.deco, e, uc, 7.6, 0.24, 0.08, "ashlar", seg=8, col=CARVED)
    F.panel(L.deco, e, uc + 3.3, 2.6, 0.75, 0.35, 0.0, lines=2, col=(0.9, 0.9, 0.88), text=(0.25, 0.35, 0.3))


def _dung_in(L, e, uc, rng, dz):
    ol = DUNG["outline"](uc, 0.0)
    band_arch(L.deco, e, ol, 3.7, 0.42, 0.05, 0.0, 0.08)
    for s in (-1, 1):
        jamb_band(L.deco, e, uc + s * (2.1 + 0.21), -0.6, 3.7, 0.42, 0.0, 0.08)


DUNG = {"line": ((622.4, -200.7), (759.6, -178.7)), "gate": (628.0, -199.8), "half": 8.0, "thick": 3.0,
        "ref_ring": REF_RINGS["dung"],
        "height": 11.5, "w": 4.2, "h": 4.4, "cw": 1.6, "mw": 1.6, "cr": 0.45, "mh": 0.85, "floor": "setts",
        "outline": lambda uc, v0: segment(uc - 2.1, uc + 2.1, v0, 3.7, 0.7, 6),
        "dress_out": _dung_out, "dress_in": _dung_in, "slits": [(5.6, 7.4, 8.9)]}


# New Gate (1889): OSM wall way 391433919 (vertices 28-30, reversed so the outside is on the right), gate node
# 561085431, footprint w1393450805 (8.4 x 3.7 m).  Broad four-centred arch ~4.2 m wide, ~5.3 m high, framed
# by rough bossed voussoirs and alternating jamb quoins on both faces (GN:02, GN:04, GN:05, GN:12).
def _new_out(L, e, uc, rng):
    voussoirs(L.deco, e, NEWG["outline"](uc, 0.0), 3.7, rng, 0.17, 11)
    F.panel(L.deco, e, uc - 3.3, 3.0, 0.7, 0.32, 0.0, lines=2, col=(0.92, 0.92, 0.9), text=(0.3, 0.32, 0.35))


def _new_in(L, e, uc, rng, dz):
    voussoirs(L.deco, e, NEWG["outline"](uc, 0.0), 3.7, rng, 0.14, 11)


NEWG = {"line": ((-124.5, 298.9), (-136.3, 291.3)), "gate": (-128.3, 296.8), "half": 8.5, "thick": 3.0,
        "ref_ring": REF_RINGS["new"],
        "height": 10.0, "w": 4.2, "h": 5.3, "cw": 1.4, "mw": 1.4, "cr": 0.7, "mh": 1.1, "floor": "setts",
        "outline": lambda uc, v0: tudor(uc - 2.1, uc + 2.1, v0, 3.7, 1.15, 0.45, 4),
        "dress_out": _new_out, "dress_in": _new_in}


def dung_gate(mbs, bd, gen, place, lod=False):
    gate_section(mbs, bd, gen, lod, DUNG)


def new_gate(mbs, bd, gen, place, lod=False):
    gate_section(mbs, bd, gen, lod, NEWG)


# ====================================================================== fallback
def generic_gate(mbs, bd, gen, place, lod=False):
    """Fallback when the OSM anchors no longer match the footprint: crenellated block, no passage."""
    ring = [tuple(p) for p in bd["ring"]]
    L = Local(mbs, bd["ground"])
    h = bd["top"] - bd["ground"]
    zb = bd["base"] - bd["ground"]
    if lod:
        lod_mass(L.solid, ring, zb, h - 1.0, h)
    else:
        F.battlemented_ring(L.solid, ring, zb, h - 2.1, h - 1.0, h, 0.8, "fort")
    L.flush()


LANDMARKS = {
    "w616186088": damascus,
    "w288395731": lions,
    "w290671706": zion,
    "w1545285986": dung_gate,
    "w1393450805": new_gate,
    "m_herods_gate": herod,
}


# ====================================================================== the wall circuit
# Where the generic OSM wall must not go: the convex hulls of the gate footprints (so nothing stands in the
# recess between the Damascus towers) and of the sections built here.  Spec rings as of 2026-10-19.  A wall
# slab running along a hull side (nearly parallel, closer than half its thickness) is dropped as well, so
# it cannot stand in front of a facade.
GATE_CUTS = {
    "damascus": REF_RINGS["damascus"],
    "lions": REF_RINGS["lions"],
    "zion": REF_RINGS["zion"],
    "herod": HEROD_RING,
    "dung": section_ring(DUNG),
    "new": section_ring(NEWG),
}


def convex_hull(pts):
    """CCW convex hull (monotone chain) of 2D points."""
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _blocked(p, d, T, cuts):
    """Is point p of a wall centre line running along d inside a gate, or alongside one of its faces?"""
    for ring in cuts:
        if mk.point_in(p, ring):
            return True
        n = len(ring)
        for i in range(n):
            e = F.Edge(ring[i], ring[(i + 1) % n])
            if e.L < 0.5 or abs(e.t.dot(d)) < 0.85:
                continue
            if -0.2 < e.u_of(p) < e.L + 0.2 and abs(e.off_of(p)) < T / 2 + 0.15:
                return True
    return False


def _face_dir(p, hulls):
    """Direction of the hull side nearest to point p (the gate face a cut wall stops against)."""
    best = None
    for ring in hulls:
        n = len(ring)
        for i in range(n):
            e = F.Edge(ring[i], ring[(i + 1) % n])
            if e.L < 0.3:
                continue
            u = min(max(e.u_of(p), 0.0), e.L)
            d = (e.P(u, 0) - Vector((p[0], p[1], 0))).length
            if best is None or d < best[0]:
                best = (d, (e.t.x, e.t.y))
    return best[1] if best else None


def clip_walls(walls, cuts=None, step=0.1):
    """walls_generic segments outside the gates (same dicts with new a / b).  Ends stopped by a gate carry
    "cut_a" / "cut_b" and "face_a" / "face_b" (direction of the gate face they meet, for a flush mitre)."""
    hulls = [convex_hull(r) for r in (cuts or GATE_CUTS).values()]     # the recess between towers too
    boxes = [(min(p[0] for p in r) - 4, min(p[1] for p in r) - 4, max(p[0] for p in r) + 4, max(p[1] for p in r) + 4)
             for r in hulls]
    out = []
    for w in walls:
        a, b = Vector((w["a"][0], w["a"][1], 0)), Vector((w["b"][0], w["b"][1], 0))
        near = [r for r, (x0, y0, x1, y1) in zip(hulls, boxes)
                if not (max(a.x, b.x) < x0 or min(a.x, b.x) > x1 or max(a.y, b.y) < y0 or min(a.y, b.y) > y1)]
        if not near:
            out.append(dict(w))
            continue
        Lw = (b - a).length
        d = (b - a) / max(Lw, 1e-9)
        n = max(2, int(Lw / step))
        T = w["thick"]
        blocked = lambda t: _blocked((a + d * t).xy, d, T, near)        # noqa: E731
        free = [not blocked(Lw * k / n) for k in range(n + 1)]

        def edge_t(t_free, t_blk):
            for _ in range(14):                                          # bisection to < 1 cm
                m = (t_free + t_blk) / 2
                if blocked(m):
                    t_blk = m
                else:
                    t_free = m
            return t_free
        k = 0
        while k <= n:
            if not free[k]:
                k += 1
                continue
            j = k
            while j + 1 <= n and free[j + 1]:
                j += 1
            ta = edge_t(Lw * k / n, Lw * (k - 1) / n) if k > 0 else 0.0
            tb = edge_t(Lw * j / n, Lw * (j + 1) / n) if j < n else Lw
            if tb - ta > 0.5:
                pa, pb = a + d * ta, a + d * tb
                seg = dict(w, a=[round(pa.x, 3), round(pa.y, 3)], b=[round(pb.x, 3), round(pb.y, 3)])
                seg["cut_a"], seg["cut_b"] = k > 0, j < n
                if k > 0:
                    seg["face_a"] = _face_dir(pa.xy, near)
                if j < n:
                    seg["face_b"] = _face_dir(pb.xy, near)
                out.append(seg)
            k = j + 1
    return out


def runs_of(walls, flag=None):
    """Group consecutive segments (b of one == a of the next) into runs."""
    runs = []
    for w in walls:
        if runs and math.dist(runs[-1][-1]["b"], w["a"]) < 0.02 and not (flag and w.get(flag)):
            runs[-1].append(w)
        else:
            runs.append([w])
    return runs


def _junctions(runs, tol=0.3):
    """Run ends meeting another run's end: {(run, 0 = start / 1 = end): (other run, its end)}."""
    ends = [(ri, 0, run[0]["a"]) for ri, run in enumerate(runs)] + [(ri, 1, run[-1]["b"]) for ri, run in enumerate(runs)]
    out = {}
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            (ri, ei, pi), (rj, ej, pj) = ends[i], ends[j]
            if ri != rj and math.dist(pi, pj) < tol and (ri, ei) not in out and (rj, ej) not in out:
                out[(ri, ei)] = (rj, ej)
                out[(rj, ej)] = (ri, ei)
    return out


def offset_walls(walls, inward=True):
    """Move every run of walls_generic by thick/2 to its inner side (left of a->b).  Joints, including
    those where two runs meet, sit on the intersections of the moved lines: the OSM line becomes the
    outer face of the curtain."""
    runs = runs_of(walls)
    junc = _junctions(runs)
    sgn = -1 if inward else 1

    def moved(w):
        e = F.Edge(tuple(w["a"]), tuple(w["b"]))
        return e, sgn * w["thick"] / 2

    def meet(e0, d0, e1, d1):
        x = F.line_x(e0.A + e0.n * d0, e0.t, e1.A + e1.n * d1, e1.t)
        if x is None or (x - (e1.A + e1.n * d1)).length > 3 * abs(d1) + e1.L:
            return None
        return x
    out = []
    for ri, run in enumerate(runs):
        E = [moved(w) for w in run]
        pts = []
        for k in range(len(run) + 1):
            if k == 0 or k == len(run):
                e, d = E[0] if k == 0 else E[-1]
                p = e.P(0, 0, d) if k == 0 else e.P(e.L, 0, d)
                o = junc.get((ri, 0 if k == 0 else 1))
                if o:
                    ow = runs[o[0]][0 if o[1] == 0 else -1]
                    oe, od = moved(ow)
                    x = meet(e, d, oe, od)
                    if x is not None and (x - p).length < 3 * abs(d):
                        p = x
                pts.append(p)
            else:
                (a, da), (b, db) = E[k - 1], E[k]
                x = meet(a, da, b, db)
                pts.append(x if x is not None and (x - (b.A + b.n * db)).length < 3 * abs(db) else b.A + b.n * db)
        for i, w in enumerate(run):
            out.append(dict(w, a=[round(pts[i].x, 3), round(pts[i].y, 3)], b=[round(pts[i + 1].x, 3), round(pts[i + 1].y, 3)]))
    return out


def bridge_gaps(walls, max_gap=6.0):
    """Re-insert short pieces missing between consecutive segments (make_spec's de-duplication drops the
    4-5 m flanks of towers because they lie within thick + 0.5 m of their neighbours)."""
    out = []
    for i, w in enumerate(walls):
        out.append(w)
        if i + 1 < len(walls):
            n = walls[i + 1]
            gap = math.dist(w["b"], n["a"])
            if 0.02 < gap < max_gap:
                out.append(dict(w, a=list(w["b"]), b=list(n["a"]), z0=min(w["z0"], n["z0"]), z1=max(w["z1"], n["z1"])))
    return out


def build_walls(mb, walls, gen=None, cuts=None, slit_every=3, mh=0.85, line=None):
    """The OSM wall circuit (spec walls_generic: {a, b, z0, z1, thick}, outside on the right; z1 = top of
    the wall, merlons above it) cut around the gates and built with the gate sections' profile: outer face
    with the crenellated parapet (merlons 1.6 m, crenels 0.45 m, an arrow slit in every third merlon),
    walk, low inner parapet, inner face.  line = "outer" (default WALL_LINE): the OSM line is the outer
    face, so the slabs are moved thick/2 inwards first.  Consecutive segments are mitred; where the
    terrain-following top steps, the taller segment closes the joint with a full end face, and so does a
    gate cut."""
    mb.tile = dict(mb.tile, fort=F.FORT_TILE)
    walls = bridge_gaps(walls)
    if (line or WALL_LINE) == "outer":
        walls = offset_walls(walls)
    runs = runs_of(clip_walls(walls, cuts), "cut_a")
    junc = _junctions(runs, 0.05)
    for ri, run in enumerate(runs):
        E = [F.Edge(tuple(w["a"]), tuple(w["b"])) for w in run]
        ks, ke = [0.0] * len(run), [0.0] * len(run)
        caps = {0: "full", 1: "full"}
        for end in (0, 1):                                             # another run meets this end: mitre it
            o = junc.get((ri, end))
            if not o:
                continue
            ow = runs[o[0]][0 if o[1] == 0 else -1]
            me, mw = (E[0], run[0]) if end == 0 else (E[-1], run[-1])
            oe = F.Edge(tuple(ow["a"]), tuple(ow["b"]))
            jd = me.n + oe.n
            if jd.length < 1e-6 or abs(jd.normalized().dot(me.n)) < 0.3:
                continue
            jd.normalize()
            k = jd.dot(me.t) / jd.dot(me.n)
            if end == 0:
                ks[0] = k
            else:
                ke[-1] = k
            caps[end] = "full" if mw["z1"] > ow["z1"] + 0.01 else None
        for i in range(len(run) - 1):
            ea, eb = E[i], E[i + 1]
            jd = ea.n + eb.n
            if jd.length < 1e-6:
                continue
            jd.normalize()
            ke[i] = jd.dot(ea.t) / jd.dot(ea.n) if abs(jd.dot(ea.n)) > 0.3 else 0.0
            ks[i + 1] = jd.dot(eb.t) / jd.dot(eb.n) if abs(jd.dot(eb.n)) > 0.3 else 0.0
        for end, i in (("face_a", 0), ("face_b", len(run) - 1)):        # flush against the gate face
            fdir = run[i].get(end)
            if fdir:
                g = Vector((fdir[0], fdir[1], 0))
                if abs(g.dot(E[i].n)) > 0.25:
                    k = g.dot(E[i].t) / g.dot(E[i].n)
                    if end == "face_a":
                        ks[0] = k
                    else:
                        ke[-1] = k
        for i, w in enumerate(run):
            e = E[i]
            if e.L < 0.5:
                continue
            ca = caps[0] if i == 0 else ("full" if w["z1"] > run[i - 1]["z1"] + 0.01 else None)
            cb = caps[1] if i == len(run) - 1 else ("full" if w["z1"] > run[i + 1]["z1"] + 0.01 else None)
            wall_run(mb, e, 0.0, e.L, ks[i], ke[i], w["z1"] + mh, w["thick"], w["z0"], cap_a=ca, cap_b=cb, mh=mh,
                     slit_every=slit_every)
    F.tint_planes(mb, "fort", (0.95, 0.95, 0.97))
