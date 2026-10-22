"""Skyline landmarks of the walled Old City outside the Temple Mount: churches, synagogues,
mosques and towers (registry: blender/landmarks.py).

Every builder is fn(mbs, bd, gen, place, lod=False). Footprints come from the spec record
(bd["ring"], CCW, local metres; x east, y north from the Jaffa Gate node); heights are measured
from bd["ground"] (or the ground of the facade edge) and never absolute. Hand-placed parts
(domes, towers, minarets) use OSM building:part geometry or OSM nodes in the same local frame.
Dimensions, sources and confidence: data/reference/landmarks_city.md; photographs:
data/photos_ref/landmarks_city/index.json.

Conventions shared by the helpers here:
* Edge(a, b): face frame of a footprint edge; u along a->b, z up, `off` along the outward
  normal (right of a->b for CCW rings).  Openings are CCW outlines in (u, z).
* Walls are single faces with holes; each hole gets a reveal (tunnel) and a dark backing or an
  atlas cell (doors are closed), so the shells stay closed and single-sided.
* lod=True: silhouette only (prisms, domes, towers, minarets), a few hundred triangles each.
"""
import math

from mathutils import Vector, geometry

import meshkit as mk

UP = Vector((0, 0, 1))
DRESSED = (1.0, 0.98, 0.94)          # frames, columns, cornices: pale dressed limestone
VOID = "void"


def gold(mb):
    """Gilded crosses and finials: the shared "gold" material once materials.py has it."""
    return "gold" if "gold" in mb.tile else "glass_lamp"


GOLD_COL = (1.0, 0.82, 0.38)          # vertex tint when falling back to glass_lamp


def gold_col(mb):
    return None if "gold" in mb.tile else GOLD_COL


# ================================================================== 2D helpers
def v2(p):
    return Vector((p[0], p[1]))


def area2(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def centroid(r):
    a = area2(r)
    if abs(a) < 1e-9:
        return Vector((sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)))
    cx = cy = 0.0
    for i in range(len(r)):
        (x0, y0), (x1, y1) = r[i], r[(i + 1) % len(r)]
        k = x0 * y1 - x1 * y0
        cx += (x0 + x1) * k
        cy += (y0 + y1) * k
    return Vector((cx / (6 * a), cy / (6 * a)))


def rect_ring(c, t, w, d):
    """CCW rectangle: centre c, unit axis t (length w), depth d along the left normal of t."""
    c, t = v2(c), v2(t).normalized()
    s = Vector((-t.y, t.x))
    return [tuple(c + t * a * w / 2 + s * b * d / 2) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def obb(ring):
    """Minimum-area oriented box of a ring: (centre, long axis t, length, width)."""
    best = None
    for i in range(len(ring)):
        a, b = v2(ring[i]), v2(ring[(i + 1) % len(ring)])
        t = b - a
        if t.length < 0.3:
            continue
        t.normalize()
        s = Vector((-t.y, t.x))
        us = [v2(p).dot(t) for p in ring]
        vs = [v2(p).dot(s) for p in ring]
        A = (max(us) - min(us)) * (max(vs) - min(vs))
        if best is None or A < best[0]:
            c = t * (max(us) + min(us)) / 2 + s * (max(vs) + min(vs)) / 2
            lu, lv = max(us) - min(us), max(vs) - min(vs)
            best = (A, c, t, lu, lv) if lu >= lv else (A, c, s, lv, lu)
    return best[1:]


def clip_convex(subject, clip):
    """Sutherland-Hodgman: subject ring clipped by a convex CCW ring (may carry zero-width
    bridges when the true result is in several pieces; walls() cancels those)."""
    out = [tuple(p) for p in subject]
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        if not inp:
            break

        def side(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            sp, sq = side(p), side(q)
            if sq >= 0:
                if sp < 0:
                    k = sp / (sp - sq)
                    out.append((p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k))
                out.append(q)
            elif sp >= 0:
                k = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k))
    res = []
    for p in out:                                   # drop duplicates and collinear points
        if res and abs(p[0] - res[-1][0]) < 1e-4 and abs(p[1] - res[-1][1]) < 1e-4:
            continue
        res.append(p)
    if len(res) > 1 and abs(res[0][0] - res[-1][0]) < 1e-4 and abs(res[0][1] - res[-1][1]) < 1e-4:
        res.pop()
    changed = True
    while changed and len(res) >= 3:
        changed = False
        for i in range(len(res)):
            a, b, c = v2(res[i - 1]), v2(res[i]), v2(res[(i + 1) % len(res)])
            if abs((b - a).cross(c - b)) < 1e-6 * max(1.0, (c - a).length):
                del res[i]
                changed = True
                break
    return res if len(res) >= 3 and abs(area2(res)) > 0.05 else []


def poly_box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def find_edge(ring, mid, direction, tol=2.5, ang=25):
    """Index of the ring edge whose midpoint is nearest `mid` with a direction within `ang` degrees."""
    d = v2(direction).normalized()
    best, bi = None, None
    for i in range(len(ring)):
        a, b = v2(ring[i]), v2(ring[(i + 1) % len(ring)])
        t = b - a
        if t.length < 0.5:
            continue
        if t.normalized().dot(d) < math.cos(math.radians(ang)):
            continue
        dist = ((a + b) / 2 - v2(mid)).length
        if dist < tol and (best is None or dist < best):
            best, bi = dist, i
    return bi


# ================================================================== face frames
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


def edge_at(c, t, u0):
    """Edge frame whose u axis is t, starting u0 before the point c (outward normal = right of t)."""
    c, t = v2(c), v2(t).normalized()
    a = c - t * u0
    return Edge(tuple(a), tuple(a + t))


def cell_uv(gen, atlas, name, size=2048):
    try:
        a = gen[atlas]
        return mk.atlas_rect(a["grid"], a["cells"][name], size_px=size)
    except (KeyError, TypeError):
        return None


def face(mb, e, outline, mat, off=0.0, holes=(), col=None, inward=False, uvrect=None):
    """Planar face in the plane of e at offset `off`: outline minus holes, both in (u, z).
    uvrect maps the outline's bounding box onto an atlas cell."""
    nrm = -e.n if inward else e.n
    verts, faces = [], []
    for r in [outline] + list(holes):
        r = [Vector((p[0], p[1])) for p in r]
        if sum(r[i].x * r[i - 1].y - r[i - 1].x * r[i].y for i in range(len(r))) > 0:
            r.reverse()
        faces.append(list(range(len(verts), len(verts) + len(r))))
        verts += r
    uvf = None
    if uvrect:
        us = [p[0] for p in outline]
        zs = [p[1] for p in outline]
        u0, u1, z0, z1 = min(us), max(us), min(zs), max(zs)
        r0, s0, r1, s1 = uvrect

        def uvf(p):
            return (r0 + (p.x - u0) / max(u1 - u0, 1e-6) * (r1 - r0), s0 + (p.y - z0) / max(z1 - z0, 1e-6) * (s1 - s0))
    try:
        ov, _e, of, _ov, _oe, origf = geometry.delaunay_2d_cdt(verts, [], faces, 1, 1e-5)
    except Exception:                                   # noqa: BLE001
        flat, tris = mk.tess2d([list(outline)] + [list(h) for h in holes])
        for a, b, c in tris:
            pts = [flat[a], flat[b], flat[c]]
            mb.poly([e.P(p[0], p[1], off) for p in pts], mat, nrm, col=col,
                    uv=[uvf(Vector(p)) for p in pts] if uvf else None)
        return
    for f, o in zip(of, origf):
        if len(o) % 2 == 1 and len(f) >= 3:
            mb.poly([e.P(ov[i].x, ov[i].y, off) for i in f], mat, nrm, col=col,
                    uv=[uvf(ov[i]) for i in f] if uvf else None)


def tunnel(mb, e, ol, off0, off1, mat, floor=False, col=None):
    """Reveal joining outline ol at off0 and off1; faces look at the axis. floor skips the bottom."""
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


def strip(mb, e, pts, off0, off1, mat, ref, col=None, toward=False):
    """Quads extruded between two offsets from an open (u, z) polyline, facing away from (or
    toward) the reference point ref = (u, z)."""
    c = e.P(ref[0], ref[1], (off0 + off1) / 2)
    for p, q in zip(pts, pts[1:]):
        if abs(p[0] - q[0]) < 1e-7 and abs(p[1] - q[1]) < 1e-7:
            continue
        quad = [e.P(p[0], p[1], off0), e.P(q[0], q[1], off0), e.P(q[0], q[1], off1), e.P(p[0], p[1], off1)]
        h = (quad[0] + quad[2]) / 2 - c
        h -= e.n * h.dot(e.n)
        mb.poly(quad, mat, -h if toward else h, col=col)


def section_prism(mb, e, u0, u1, prof, mat, skip=(), col=None, ends=True):
    """Prism along u of a closed side profile [(off, z), ...] (cornices, string courses)."""
    c = (sum(p[0] for p in prof) / len(prof), sum(p[1] for p in prof) / len(prof))
    for i in range(len(prof)):
        if i in skip:
            continue
        (o0, z0), (o1, z1) = prof[i], prof[(i + 1) % len(prof)]
        quad = [e.P(u0, z0, o0), e.P(u0, z1, o1), e.P(u1, z1, o1), e.P(u1, z0, o0)]
        mb.poly(quad, mat, (quad[0] + quad[2]) / 2 - e.P((u0 + u1) / 2, c[1], c[0]), col=col)
    if ends:
        for u, s in ((u0, -1), (u1, 1)):
            mb.poly([e.P(u, z, o) for o, z in prof], mat, e.t * s, col=col)


def cornice(mb, e, u0, u1, z, h, proj, mat="dressed", col=DRESSED, ends=True):
    """Moulded cornice / string course: a cyma-like stepped profile standing proud of the wall."""
    prof = [(0.0, z), (proj * 0.35, z), (proj, z + h * 0.55), (proj, z + h), (0.0, z + h)]
    section_prism(mb, e, u0, u1, prof, mat, skip=(4,), col=col, ends=ends)


def obox(mb, c, t, s, lt, ls, z0, z1, mat, col=None, top=True, bottom=False, skip=()):
    """Oriented box; skip sides: 0 = -s, 1 = +t, 2 = +s, 3 = -t."""
    c, t, s = Vector((c[0], c[1], 0)), Vector((t[0], t[1], 0)).normalized(), Vector((s[0], s[1], 0)).normalized()
    pts = [c - t * lt / 2 - s * ls / 2, c + t * lt / 2 - s * ls / 2, c + t * lt / 2 + s * ls / 2, c - t * lt / 2 + s * ls / 2]
    lo = [p + UP * z0 for p in pts]
    hi = [p + UP * z1 for p in pts]
    cz = c + UP * ((z0 + z1) / 2)
    for k in range(4):
        if k in skip:
            continue
        q = [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]]
        mb.poly(q, mat, (q[0] + q[2]) / 2 - cz, col=col)
    if top:
        mb.poly(hi, mat, UP, col=col)
    if bottom:
        mb.poly(lo, mat, -UP, col=col)


def column(mb, p, z0, z1, r, mat="dressed", col=DRESSED, seg=8, capital=True):
    """Colonnette with a square capital and base block."""
    mk.cylinder(mb, p[0], p[1], z0 + 0.18, z1 - 0.3, r, mat, seg=seg, cap=False, col=col)
    t = Vector((1, 0, 0))
    obox(mb, p, t, Vector((0, 1, 0)), r * 2.6, r * 2.6, z0, z0 + 0.18, mat, col=col)
    if capital:
        obox(mb, p, t, Vector((0, 1, 0)), r * 3.2, r * 3.2, z1 - 0.3, z1, mat, col=col, bottom=True)


# ------------------------------------------------------------------ arch outlines (u, z)
def arch_top(u0, u1, zs, kind="round", rise=None, seg=8):
    """Arch from the right springer (u1, zs) over the crown to (u0, zs)."""
    w = u1 - u0
    if kind == "flat" or w <= 0:
        return [(u1, zs), (u0, zs)]
    if kind == "round":
        r, c = w / 2, (u0 + u1) / 2
        return [(c + r * math.cos(math.pi * k / seg), zs + r * math.sin(math.pi * k / seg)) for k in range(seg + 1)]
    if kind == "segment":
        rise = rise or 0.2 * w
        R = (w * w / 4 + rise * rise) / (2 * rise)
        a0 = math.asin(min(1.0, (w / 2) / R))
        c = (u0 + u1) / 2
        return [(c + R * math.sin(a0 - 2 * a0 * k / seg), zs + R * math.cos(a0 - 2 * a0 * k / seg) - (R - rise))
                for k in range(seg + 1)]
    rise = max(rise or 0.8 * w, w / 2 + 1e-3)                   # two-centred pointed arch
    R = (w * w / 4 + rise * rise) / w
    a_top = math.atan2(rise, R - w / 2)
    half = max(2, seg // 2)
    pts = [(u1 - R + R * math.cos(a_top * k / half), zs + R * math.sin(a_top * k / half)) for k in range(half + 1)]
    pts += [(u0 + R - R * math.cos(a_top * k / half), zs + R * math.sin(a_top * k / half)) for k in range(half - 1, -1, -1)]
    return pts


def arch_ol(u0, u1, z0, zs, kind="round", rise=None, seg=8):
    """CCW outline: bottom edge, jambs up to the springing zs, arch head."""
    if kind == "flat":
        return rect(u0, u1, z0, zs)
    top = arch_top(u0, u1, zs, kind, rise, seg)
    if zs - z0 < 1e-4:
        return top
    return [(u0, z0), (u1, z0)] + top


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


def circle(uc, zc, r, seg=10):
    return [(uc + r * math.cos(2 * math.pi * k / seg), zc + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]


# ------------------------------------------------------------------ openings
def hole(ol, depth=0.4, back=VOID, floor=False, grille=False, frame=0.0, fd=0.08, back_col=None):
    """Opening spec. back: 'void' (dark), 'wall' (blocked: stone set back), or a doors-atlas cell."""
    return {"ol": ol, "d": depth, "back": back, "floor": floor, "grille": grille, "frame": frame, "fd": fd,
            "back_col": back_col}


def build_hole(mb, e, h, mat, col, gen, off=0.0):
    ol, d = h["ol"], h["d"]
    tunnel(mb, e, ol, off, off - d, mat, floor=h["floor"], col=col)
    back = h["back"]
    if back is None:                                    # the caller builds the back face itself
        pass
    elif back == VOID:
        face(mb, e, ol, VOID, off - d)
    elif back == "wall":
        bc = h.get("back_col") or (tuple(c * 0.92 for c in col) if col else (0.92, 0.92, 0.92))
        face(mb, e, ol, mat, off - d, col=bc)
    else:
        r = cell_uv(gen, "doors", back) or cell_uv(gen, "doors", "glass")
        face(mb, e, ol, "doors" if r else VOID, off - d, uvrect=r)
    if h["grille"]:
        r = cell_uv(gen, "cutout", "grille")
        if r:
            us = [p[0] for p in ol]
            zs = [p[1] for p in ol]
            face(mb, e, rect(min(us), max(us), min(zs), max(zs)), "cut", off - min(0.12, d * 0.4), uvrect=r)
    fw = h["frame"]
    if fw > 0.02:
        frame(mb, e, ol, fw, off, h["fd"])


def frame(mb, e, ol, fw, off=0.0, fd=0.08, mat="dressed", col=DRESSED):
    """Dressed surround (sides and head) of an opening outline, standing fd proud of the wall."""
    us = [p[0] for p in ol]
    zs = [p[1] for p in ol]
    ref = ((min(us) + max(us)) / 2, min(zs) + 0.01)
    outer = _grow_open(ol, fw)
    inner = ol[1:] + [ol[0]]
    face(mb, e, outer + inner[::-1], mat, off + fd, col=col)
    strip(mb, e, outer, off, off + fd, mat, ref, col)
    strip(mb, e, inner, off, off + fd, mat, ref, col, toward=True)


def _grow_open(ol, fw):
    """Outline ol grown by fw on the sides and top, as an open polyline from bottom-right to bottom-left."""
    us = [p[0] for p in ol]
    zs = [p[1] for p in ol]
    u0, u1, z0 = min(us), max(us), min(zs)
    cu = (u0 + u1) / 2
    out = []
    for p in ol[1:]:                                    # skip the first bottom-left point
        du = p[0] - cu
        sx = 1 if du > 1e-6 else (-1 if du < -1e-6 else 0)
        dz = fw if p[1] > z0 + 1e-6 else 0.0
        scale = (abs(du) + fw) / max(abs(du), 1e-6) if abs(du) > 1e-6 else 1.0
        out.append((cu + du * scale if sx else p[0], p[1] + dz))
    out.append((u0 - fw, z0))
    return out


def wall(mb, e, u0, u1, z0, z1, mat, col=None, holes=(), gen=None, off=0.0):
    face(mb, e, rect(u0, u1, z0, z1), mat, off, [h["ol"] for h in holes], col)
    for h in holes:
        build_hole(mb, e, h, mat, col, gen, off)


# ------------------------------------------------------------------ volumes
def prism(mb, ring, z0, z1, mat, col=None, roof="lime", roof_col=None, hook=None, walls=True):
    """Closed prism (no bottom): walls on every edge unless hook(i, a, b, z0, z1) builds it."""
    n = len(ring)
    if walls:
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            if math.dist(a, b) < 0.02:
                continue
            if hook and hook(i, a, b, z0, z1):
                continue
            q = [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]
            mb.poly(q, mat, Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=col)
    if roof:
        cap(mb, ring, z1, roof, roof_col if roof_col is not None else (col if roof == mat else None))


def cap(mb, ring, z, mat, col=None, down=False):
    verts = [Vector((p[0], p[1])) for p in ring]
    try:
        ov, _e, of, _ov, _oe, origf = geometry.delaunay_2d_cdt(verts, [], [list(range(len(verts)))], 1, 1e-5)
        for f, o in zip(of, origf):
            if len(o) % 2 == 1 and len(f) >= 3:
                mb.poly([(ov[i].x, ov[i].y, z) for i in f], mat, -UP if down else UP, col=col)
    except Exception:                                   # noqa: BLE001
        fl, ft = mk.tess2d([ring])
        mb.tris([(p[0], p[1], z) for p in fl], ft, mat, -UP if down else UP, col=col)


def parapet(mb, ring, z, h, th, mat, col=None, coping="dressed"):
    """Solid parapet standing on the outer edge of a flat roof (outer face flush with the wall)."""
    inner = mk.inset_ring(ring, th)
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        a2, b2 = inner[i], inner[(i + 1) % n]
        q = [(a[0], a[1], z), (b[0], b[1], z), (b[0], b[1], z + h), (a[0], a[1], z + h)]
        mb.poly(q, mat, Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=col)
        q = [(b2[0], b2[1], z), (a2[0], a2[1], z), (a2[0], a2[1], z + h), (b2[0], b2[1], z + h)]
        mb.poly(q, mat, Vector((-(b2[1] - a2[1]), b2[0] - a2[0], 0)), col=col)
        q = [(a[0], a[1], z + h), (b[0], b[1], z + h), (b2[0], b2[1], z + h), (a2[0], a2[1], z + h)]
        mb.poly(q, coping, UP, col=DRESSED if coping == "dressed" else col)


def dome(mb, cx, cy, z, r, mat, rise=1.0, seg=24, rings=6, col=None, top=0.0, ribs=0, rib_col=None,
         rib_w=0.12, profile=None):
    """Dome on the circle (cx, cy, r) at z. top > 0 leaves an oculus of that radius (for a lantern).
    ribs > 0: that many narrow rib strips in a different vertex tint (lead sheeting with seams).
    profile(phi) -> (radius factor, height factor) for onion / pointed domes."""
    angs = []
    if ribs:
        for k in range(ribs):
            a = 2 * math.pi * k / ribs
            angs += [(a, False), (a + 2 * math.pi / ribs * (1 - rib_w), True)]
    else:
        angs = [(2 * math.pi * k / seg, False) for k in range(seg)]
    angs.append((2 * math.pi, False))
    cols = [rib_col if is_rib else col for _, is_rib in angs]
    phi_max = math.pi / 2 if top <= 0 else math.acos(min(0.999, top / r))

    def ringpts(phi):
        if profile:
            fr, fz = profile(phi)
        else:
            fr, fz = math.cos(phi), math.sin(phi)
        return [Vector((cx + math.cos(a) * r * fr, cy + math.sin(a) * r * fr, z + r * rise * fz)) for a, _ in angs]
    centre = Vector((cx, cy, z))
    prev = ringpts(0.0)
    for j in range(1, rings + 1):
        phi = phi_max * j / rings
        last = j == rings
        if last and top <= 0:
            apex = Vector((cx, cy, z + r * rise * (profile(math.pi / 2)[1] if profile else 1.0)))
            for k in range(len(prev) - 1):
                mb.poly([prev[k], prev[k + 1], apex], mat, (prev[k] + prev[k + 1]) / 2 - centre, col=cols[k])
            return apex.z
        cur = ringpts(phi)
        for k in range(len(prev) - 1):
            q = [prev[k], prev[k + 1], cur[k + 1], cur[k]]
            mb.poly(q, mat, (q[0] + q[2]) / 2 - centre, col=cols[k])
        prev = cur
    return prev[0].z


def drum(mb, cx, cy, r, z0, z1, n, mat, col=None, win=None, gen=None, rot=0.0, every=1, roof=None):
    """Polygonal drum; win=(w, zb, zs, kind, depth, back) puts an arched window in every `every`-th side."""
    pts = [(cx + r * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        e = Edge(a, b)
        hs = []
        if win and k % every == 0:
            w, zb, zs, kind, depth, back = win
            uc = e.L / 2
            hs = [hole(arch_ol(uc - w / 2, uc + w / 2, zb, zs, kind, seg=6), depth, back,
                       grille=back not in (VOID, "wall"))]
        wall(mb, e, 0, e.L, z0, z1, mat, col, hs, gen)
    if roof:
        cap(mb, pts, z1, roof, col)
    return pts


def ring_band(mb, cx, cy, r, z0, z1, n, mat, col=None, rot=0.0):
    """Projecting cylindrical band (drum cornice): outer wall, top and underside."""
    pts = [Vector((cx + r * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n), 0))
           for k in range(n + 1)]
    c = Vector((cx, cy, 0))
    for k in range(n):
        a, b = pts[k], pts[k + 1]
        mb.poly([a + UP * z0, b + UP * z0, b + UP * z1, a + UP * z1], mat, (a + b) / 2 - c, col=col)
    mb.poly([p + UP * z1 for p in pts[:-1]], mat, UP, col=col)
    mb.poly([p + UP * z0 for p in pts[:-1]], mat, -UP, col=col)


def pyramid_roof(mb, ring4, z, h, mat="roof_tiles", over=0.5, col=None, soffit=0.12):
    """Hipped / pyramidal roof over a 4-point ring with eaves overhang."""
    c = centroid(ring4)
    out = mk.inset_ring(ring4, -over)
    lo = [Vector((p[0], p[1], z)) for p in out]
    apex = Vector((c.x, c.y, z + h))
    for k in range(4):
        a, b = lo[k], lo[(k + 1) % 4]
        mb.poly([a, b, apex], mat, ((a + b) / 2 - Vector((c.x, c.y, z))) + UP, col=col)
        mb.poly([a, b, b - UP * soffit, a - UP * soffit], mat, (a + b) / 2 - Vector((c.x, c.y, z)), col=col)
    mb.poly([p - UP * soffit for p in lo], mat, -UP, col=col)


def pyramid(mb, ring, z, h, mat, col=None):
    c = centroid(ring)
    apex = Vector((c.x, c.y, z + h))
    n = len(ring)
    for k in range(n):
        a, b = Vector((*ring[k], z)), Vector((*ring[(k + 1) % n], z))
        mb.poly([a, b, apex], mat, (a + b) / 2 - Vector((c.x, c.y, z)) + UP * 0.3, col=col)


def cross(mb, p, z, h, mat, col=None, w=None, t=0.09):
    """Latin cross standing on z (two crossed bars on a ball)."""
    w = w or h * 0.55
    mk.cylinder(mb, p[0], p[1], z, z + 0.12, 0.09, mat, seg=6, col=col)
    for ax in ((1, 0), (0, 1)):
        obox(mb, p, ax, (-ax[1], ax[0]), t, t, z + 0.12, z + h, mat, col=col)
        ca = Vector((p[0], p[1]))
        obox(mb, ca, ax, (-ax[1], ax[0]), w, t, z + h * 0.62, z + h * 0.62 + t * 1.1, mat, col=col, bottom=True)


def crescent_finial(mb, p, z, h, mat, col=None):
    """Minaret finial: stacked balls on a rod and a flat crescent (two thin boxes in a V)."""
    mk.cylinder(mb, p[0], p[1], z, z + h, 0.05, mat, seg=6, col=col)
    for zz, r in ((z + 0.25 * h, 0.16), (z + 0.5 * h, 0.12)):
        mk.dome(mb, p[0], p[1], zz - r, r, mat, drum=0.0, seg=8, rings=2, col=col)
        mk.dome(mb, p[0], p[1], zz - r, r, mat, drum=0.0, seg=8, rings=2, col=col, rise=-1.0)
    zc = z + 0.85 * h
    for s in (-1, 1):
        a = math.radians(35 * s)
        d = Vector((math.sin(a), 0, math.cos(a)))
        c = Vector((p[0], p[1], zc)) + Vector((0.12 * s, 0, 0.1))
        q = [c - d * 0.18 - Vector((0, 0.02, 0)), c + d * 0.18 - Vector((0, 0.02, 0)),
             c + d * 0.18 + Vector((0, 0.02, 0)), c - d * 0.18 + Vector((0, 0.02, 0))]
        mb.poly(q, mat, Vector((s, 0, 0)), col=col)
        mb.poly(q[::-1], mat, Vector((-s, 0, 0)), col=col)


def rail(mb, ring_pts, z, h=1.0, closed=True, post=1.8, mat="iron"):
    """Thin iron railing (top and mid rails, posts) along a polyline."""
    pts = [Vector((p[0], p[1], z)) for p in ring_pts]
    if closed:
        pts.append(pts[0])
    for hh in (h, h * 0.5):
        mk.tube(mb, [p + UP * hh for p in pts], 0.02, mat)
    for a, b in zip(pts, pts[1:]):
        L = (b - a).length
        k = max(1, int(L / post))
        for j in range(k):
            p = a + (b - a) * (j / k)
            mk.tube(mb, [p, p + UP * h], 0.018, mat)


# ================================================================== zones
class Zones:
    """Height zones over one footprint: the spec ring clipped by convex zone polygons, each extruded
    from the base to its own height (hidden walls where a zone meets a taller one are back-to-back,
    never coplanar with a same-facing face).  Special edges (facades) are built by hooks matched on
    the zone edge's line; other exposed street walls get a plain grid of small windows."""

    def __init__(self, bd, gen=None):
        self.ring = [tuple(p) for p in bd["ring"]]
        self.base = bd["base"]
        self.exposed = bd.get("exposed") or [True] * len(self.ring)
        self.eground = bd.get("edge_ground") or [bd["ground"]] * len(self.ring)
        self.gen = gen
        self.parts = []                                 # (name, poly, z_top, mat, col, roof, windows)
        self.specials = []                              # (a, b, fn)

    def add(self, name, clip, z_top, mat, col, roof="lime", windows=True):
        poly = clip_convex(self.ring, clip)
        if poly:
            if area2(poly) < 0:
                poly.reverse()
            self.parts.append((name, poly, z_top, mat, col, roof, windows))
        return poly

    def special(self, a, b, fn):
        self.specials.append((v2(a), v2(b), fn))

    def _match(self, a, b):
        pa, pb = v2(a), v2(b)
        for sa, sb, fn in self.specials:
            t = sb - sa
            L = t.length
            t = t / L
            nrm = Vector((-t.y, t.x))
            if abs((pa - sa).dot(nrm)) > 0.08 or abs((pb - sa).dot(nrm)) > 0.08:
                continue
            ua, ub = (pa - sa).dot(t), (pb - sa).dot(t)
            if ub <= ua or ua < -0.1 or ub > L + 0.1:
                continue
            return fn, ua, ub, Edge(tuple(sa), tuple(sb))
        return None

    def ring_edge(self, a, b):
        """Index of the ring edge carrying the segment a-b (None for internal zone boundaries)."""
        pa, pb = v2(a), v2(b)
        n = len(self.ring)
        for i in range(n):
            sa, sb = v2(self.ring[i]), v2(self.ring[(i + 1) % n])
            t = sb - sa
            L = t.length
            if L < 1e-6:
                continue
            t /= L
            nrm = Vector((-t.y, t.x))
            if abs((pa - sa).dot(nrm)) < 0.03 and abs((pb - sa).dot(nrm)) < 0.03 and (pb - pa).dot(t) > 0:
                ua, ub = (pa - sa).dot(t), (pb - sa).dot(t)
                if ua > -0.05 and ub < L + 0.05:
                    return i
        return None

    def build(self, mb, lod=False):
        for name, poly, z_top, mat, col, roof, windows in self.parts:
            for a, b in _cancel_bridges(poly):
                m = None if lod else self._match(a, b)
                if m:
                    fn, ua, ub, e = m
                    if fn(mb, e, ua, ub, self.base, z_top, mat, col):
                        continue
                ri = self.ring_edge(a, b) if (windows and not lod) else None
                e = Edge(a, b)
                if ri is not None and self.exposed[ri] and e.L > 3.0:
                    zg = self.eground[ri]
                    hs = window_grid(e.L, zg, z_top, seed=int(a[0] * 7 + a[1] * 13))
                    wall(mb, e, 0, e.L, self.base, z_top, mat, col, hs, self.gen)
                    continue
                q = [(a[0], a[1], self.base), (b[0], b[1], self.base), (b[0], b[1], z_top), (a[0], a[1], z_top)]
                mb.poly(q, mat, Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=col)
            if roof:
                cap(mb, poly, z_top, roof, ROOF_COL.get(roof, col))

    def top_at(self, p):
        for name, poly, z_top, *_ in self.parts:
            if mk.point_in(p, poly):
                return z_top
        return None


ROOF_COL = {"lime": None, "paving": (0.93, 0.88, 0.8)}


def window_grid(L, zg, z_top, seed=0, sp=3.8, storey=3.6, w=0.8, h=1.25):
    """Small recessed windows on a plain street wall: rows from 4 m above the street, a column every
    ~3.8 m; barred dark openings low down, shuttered / glazed cells higher up."""
    out = []
    n = int((L - 1.6) / sp)
    if n < 1:
        return out
    u0 = (L - (n - 1) * sp) / 2 if n > 1 else L / 2
    cells = ["glass", "shutter_green", "glass_curtain", "shutter_brown", "glass"]
    row = 0
    z = zg + 4.2
    while z + h < z_top - 1.0:
        for k in range(n):
            u = u0 + k * sp
            hsh = (seed * 31 + k * 17 + row * 7) % 11
            if hsh == 0:
                continue
            back = VOID if row == 0 else cells[hsh % len(cells)]
            out.append(win(u, w, z, z + h, "flat", back, 0.25, grille=(row == 0)))
        z += storey
        row += 1
    return out


def _cancel_bridges(poly):
    """Edges of a clipped ring with the overlapping parts of opposite collinear edges removed."""
    n = len(poly)
    edges = [(v2(poly[i]), v2(poly[(i + 1) % n])) for i in range(n)]
    out = []
    for i, (a, b) in enumerate(edges):
        t = b - a
        L = t.length
        if L < 1e-4:
            continue
        t /= L
        nrm = Vector((-t.y, t.x))
        cuts = []
        for j, (c, d) in enumerate(edges):
            if j == i:
                continue
            if abs((c - a).dot(nrm)) > 1e-3 or abs((d - a).dot(nrm)) > 1e-3:
                continue
            if (d - c).dot(t) >= 0:
                continue                                # same direction: not a bridge
            u0, u1 = sorted(((c - a).dot(t), (d - a).dot(t)))
            u0, u1 = max(0.0, u0), min(L, u1)
            if u1 - u0 > 1e-4:
                cuts.append((u0, u1))
        if not cuts:
            out.append((tuple(a), tuple(b)))
            continue
        cuts.sort()
        u = 0.0
        for c0, c1 in cuts:
            if c0 > u + 1e-4:
                out.append((tuple(a + t * u), tuple(a + t * c0)))
            u = max(u, c1)
        if u < L - 1e-4:
            out.append((tuple(a + t * u), tuple(b)))
    return out


# ================================================================== shared edge decoration
def holes_in(specs, ua, ub, margin=0.15):
    """Hole specs whose u-extent lies inside [ua, ub] (zone clipping may split an edge)."""
    out = []
    for h in specs:
        us = [p[0] for p in h["ol"]]
        if min(us) >= ua + margin and max(us) <= ub - margin:
            out.append(h)
    return out


def edge_hook(specs_fn, extras_fn=None, gen=None):
    """Zone hook: wall over [ua, ub] with the holes from specs_fn(z0, z1) that fit, then extras."""
    def fn(mb, e, ua, ub, z0, z1, mat, col):
        hs = holes_in(specs_fn(z0, z1), ua, ub)
        wall(mb, e, ua, ub, z0, z1, mat, col, hs, gen)
        if extras_fn:
            extras_fn(mb, e, ua, ub, z0, z1, mat, col)
        return True
    return fn


def win(u, w, zb, zt, kind="round", back=VOID, depth=0.35, grille=False, frame=0.0, floor=False, rise=None):
    """Window/door hole centred at u from zb to the crown zt."""
    if kind == "round":
        zs = zt - w / 2
    elif kind == "pointed":
        zs = zt - (rise or 0.8 * w)
    elif kind == "segment":
        zs = zt - (rise or 0.2 * w)
    else:
        zs = zt
    return hole(arch_ol(u - w / 2, u + w / 2, zb, max(zb + 0.05, zs), kind, rise, seg=8), depth, back, floor,
                grille, frame)


def ladder(mb, p0, p1, w=0.45, step=0.3, mat="wood"):
    """Wooden ladder from foot centre p0 to top centre p1 (two rails and rungs)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    side = d.cross(UP)
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    for s in (-1, 1):
        mk.tube(mb, [p0 + side * s * w / 2, p1 + side * s * w / 2], 0.035, mat, sides=4)
    k = int(d.length / step)
    for j in range(1, k + 1):
        c = p0 + d * (j / (k + 0.5))
        mk.tube(mb, [c - side * w / 2, c + side * w / 2], 0.022, mat, sides=4)


def steps_run(mb, e, u0, u1, off0, off1, z0, z1, n, base, mat="dressed", col=(0.9, 0.88, 0.84)):
    """Straight flight along +u in the frame of e, rising from z0 to z1 in n steps (solid blocks)."""
    du = (u1 - u0) / n
    dz = (z1 - z0) / n
    for k in range(n):
        ua, ub = u0 + du * k, u0 + du * (k + 1)
        c = e.P((ua + ub) / 2, 0, (off0 + off1) / 2)
        obox(mb, c, e.t, e.n, ub - ua, off1 - off0, base, z0 + dz * (k + 1), mat, col=col, skip=(0,) if off0 <= 0.001 else ())


# ================================================================== Church of the Holy Sepulchre
HS_ROT = (187.5, 203.4, 11.6)          # Anastasis rotunda: OSM building:part 1022663528 (min_height 20, height 34)
HS_KAT = (210.8, 208.3, 6.2)           # katholikon dome: OSM 1022663527 (min_height 24, height 34)
HS_APSE = (227.5, 210.5, 7.4)          # katholikon apse: OSM 1022663525 (height 23)
HS_HELENA = (253.9, 207.9, 3.35)       # St Helena's chapel dome in Deir es-Sultan: OSM 1022663497
HS_TOWER_NE = (204.3, 183.75)          # bell tower NE corner (OSM 1022663529, height 30, pyramidal roof)
HS_TOWER = 10.5                         # shaft width: OSM part 11 x 10.5 m (massive in photo hs_08)
HS_SMALLDOME = (177.2, 182.4, 1.5)     # small dome, OSM 1022663502 (height 22, dome 2 m)
HS_STONE = (1.0, 0.8, 0.58)           # honey Crusader masonry of the facade (photos hs_07, hs_10)
HS_PALE = (1.0, 0.96, 0.88)            # bell tower and the Greek chapels: paler, whiter stone
HS_LIME = (0.97, 0.95, 0.9)


def holy_sepulchre(mbs, bd, gen, place, lod=False):
    sol, deco = mbs["solid"], mbs["deco"]
    ring = [tuple(p) for p in bd["ring"]]
    base = bd["base"]
    i_fac = find_edge(ring, (211.27, 184.01), (1.0, 0.078))
    eg = bd.get("edge_ground") or []
    g = eg[i_fac] if i_fac is not None and i_fac < len(eg) else bd["ground"]
    # facade line (zone boundary 0.25 m outside it)
    if i_fac is not None:
        fa, fb_ = v2(ring[i_fac]), v2(ring[(i_fac + 1) % len(ring)])
    else:
        fa, fb_ = Vector((203.793, 183.428)), Vector((218.739, 184.599))
    tf = (fb_ - fa).normalized()
    nf = Vector((tf.y, -tf.x))                                     # outward (south)

    def yl(x):
        p = fa + nf * 0.25
        return p.y + (x - p.x) * tf.y / tf.x

    Z = Zones(bd, gen)
    stone, pale = HS_STONE, HS_PALE
    # (x0, x1, y0, y1) boxes (or explicit polygons) -> height above the parvis; see landmarks_city.md
    Z.add("west", poly_box(150, 140, 170, 240), g + 15.0, "ashlar", pale, roof="paving")
    Z.add("sw_s", poly_box(170, 140, 204, 162), g + 9.0, "ashlar", pale, roof="paving")
    Z.add("sw", poly_box(170, 162, 204, 183.05), g + 13.0, "ashlar", pale, roof="paving")
    Z.add("rotunda", poly_box(170, 183.05, 204, 240), g + 19.0, "ashlar", stone, roof="paving")
    Z.add("chapels_ss", poly_box(204, 140, 215, 162), g + 8.0, "ashlar", pale, roof="paving")
    Z.add("chapels_s", poly_box(204, 162, 215, 174), g + 12.0, "ashlar", pale, roof="paving")
    Z.add("chapels_n", [(204, 174), (215, 174), (215, yl(215)), (204, yl(204))], g + 8.8, "ashlar", pale, roof="paving")
    Z.add("facade", [(204, yl(204)), (224.2, yl(224.2)), (224.2, 191), (204, 191)], g + 20.3, "ashlar", stone, roof="paving")
    Z.add("franks", [(215, 140), (224.2, 140), (224.2, yl(224.2)), (215, yl(215))], g + 11.6, "ashlar", stone, roof="paving")
    Z.add("east", poly_box(224.2, 140, 241, 191), g + 12.0, "ashlar", pale, roof="paving")
    Z.add("katholikon", poly_box(204, 191, 228, 222.5), g + 24.0, "ashlar", stone, roof="paving")
    Z.add("ambulatory", poly_box(228, 191, 241, 222.5), g + 15.0, "ashlar", stone, roof="paving")
    Z.add("north", poly_box(204, 222.5, 241, 240), g + 16.0, "ashlar", pale, roof="paving")
    Z.add("coptic", poly_box(241, 140, 270, 188.6), g + 11.0, "ashlar", pale, roof="paving")
    Z.add("deir_es_sultan", poly_box(241, 188.6, 270, 240), g + 7.5, "rubble", (0.98, 0.93, 0.85), roof="paving")

    if not lod:
        _hs_specials(Z, mbs, ring, g, base, gen, tf, nf)
    Z.build(sol, lod=lod)

    seg = 12 if lod else 32
    # ---- Anastasis rotunda: drum, ribbed lead dome, oculus lantern, cross
    rx, ry, rr = HS_ROT
    zd0, zd1 = g + 19.0, g + 25.0
    if lod:
        mk.cylinder(sol, rx, ry, zd0 - 0.3, zd1, rr, "ashlar", seg=seg, cap=False, col=stone)
        dome(sol, rx, ry, zd1, rr, "lead", rise=0.84, seg=seg, rings=4)
    else:
        drum(sol, rx, ry, rr, zd0 - 0.3, zd1, 32, "ashlar", stone, win=(0.8, zd0 + 1.4, zd0 + 2.9, "round", 0.4, VOID),
             gen=gen, every=2)
        ring_band(sol, rx, ry, rr + 0.25, zd1 - 0.35, zd1 + 0.05, 32, "dressed", DRESSED)
        ztop = dome(sol, rx, ry, zd1 + 0.05, rr + 0.1, "lead", rise=0.84, rings=9, top=2.1, ribs=36,
                    col=(0.8, 0.85, 0.95), rib_col=(1.15, 1.15, 1.2))
        mk.cylinder(sol, rx, ry, ztop - 0.25, ztop + 0.9, 2.1, "lead", seg=20, cap=False, col=(1.1, 1.1, 1.1))
        mk.cylinder(sol, rx, ry, ztop + 0.9, ztop + 1.5, 2.1, "lead", seg=20, cap=True, r1=0.5, col=(1.1, 1.1, 1.1))
        cross(deco, (rx, ry), ztop + 1.5, 2.6, gold(deco), gold_col(deco))
    # ---- katholikon: drum with arched windows, ribbed dome, knob and cross
    kx, ky, kr = HS_KAT
    zk0, zk1 = g + 24.0, g + 28.3
    if lod:
        mk.cylinder(sol, kx, ky, zk0 - 0.3, zk1, kr - 0.2, "ashlar", seg=12, cap=False, col=stone)
        dome(sol, kx, ky, zk1, kr, "lead", rise=0.8, seg=12, rings=3)
    else:
        drum(sol, kx, ky, kr - 0.2, zk0 - 0.3, zk1, 24, "ashlar", stone,
             win=(0.75, zk0 + 1.0, zk0 + 3.2, "round", 0.45, VOID), gen=gen, every=2)
        ring_band(sol, kx, ky, kr + 0.1, zk1 - 0.3, zk1 + 0.05, 24, "dressed", DRESSED)
        ring_band(sol, kx, ky, kr + 0.05, zk0 + 0.6, zk0 + 0.85, 24, "dressed", DRESSED)
        ztop = dome(sol, kx, ky, zk1 + 0.05, kr, "lead", rise=0.8, rings=8, ribs=28,
                    col=(0.8, 0.85, 0.95), rib_col=(1.15, 1.15, 1.2))
        mk.cylinder(sol, kx, ky, ztop - 0.2, ztop + 0.2, 0.55, "lead", seg=10, cap=False)
        mk.dome(sol, kx, ky, ztop + 0.2, 0.55, "lead", drum=0.0, seg=10, rings=3)
        cross(deco, (kx, ky), ztop + 0.7, 2.8, gold(deco), gold_col(deco))
    # ---- katholikon apse (half drum towards the east)
    ax_, ay_, ar_ = HS_APSE
    n_ap = 5 if lod else 9
    pts = [(ax_ + ar_ * math.cos(-math.pi / 2 + math.pi * k / n_ap), ay_ + ar_ * math.sin(-math.pi / 2 + math.pi * k / n_ap))
           for k in range(n_ap + 1)]
    za0, za1 = g + 14.7, g + 22.0
    for k in range(n_ap):
        e = Edge(pts[k], pts[k + 1])
        hs = [] if lod else [win(e.L / 2, 0.9, za0 + 2.2, za0 + 4.6, "round", VOID, 0.4),
                            hole(circle(e.L / 2, za0 + 6.0, 0.35, 8), 0.3, VOID)]
        wall(sol, e, 0, e.L, za0, za1, "ashlar", stone, hs, gen)
        if not lod:
            cornice(sol, e, 0.0, e.L, za1 - 0.45, 0.45, 0.35, ends=False)
    cap(sol, pts, za1, "lime")
    # ---- bell tower
    _hs_tower(mbs, g, tf, gen, lod)
    # ---- small domes on the roofs
    sx, sy, sr = HS_SMALLDOME
    zs0 = g + 19.0
    if not lod:
        drum(sol, sx, sy, sr, zs0 - 0.2, zs0 + 0.9, 12, "ashlar", pale)
        dome(sol, sx, sy, zs0 + 0.9, sr + 0.05, "lead", rise=0.9, seg=12, rings=4)
        cross(deco, (sx, sy), zs0 + 0.9 + sr * 0.9, 1.2, gold(deco), gold_col(deco))
    # ---- Deir es-Sultan: St Helena's dome in the roof court, Ethiopian cells
    hx, hy, hr = HS_HELENA
    zh = g + 7.5
    if lod:
        mk.cylinder(sol, hx, hy, zh - 0.1, zh + 2.4, hr, "rubble", seg=8, cap=False)
        dome(sol, hx, hy, zh + 2.4, hr + 0.1, "rubble", rise=0.75, seg=8, rings=2, col=(0.8, 0.7, 0.58))
    else:
        drum(sol, hx, hy, hr, zh - 0.05, zh + 2.4, 12, "rubble", (0.9, 0.84, 0.74),
             win=(1.0, zh + 0.55, zh + 1.75, "round", 0.5, VOID), gen=gen, every=2)
        ring_band(sol, hx, hy, hr + 0.15, zh + 2.2, zh + 2.45, 12, "rubble", (0.85, 0.78, 0.68))
        dome(sol, hx, hy, zh + 2.45, hr + 0.12, "rubble", rise=0.72, seg=16, rings=5, col=(0.78, 0.68, 0.56))
        _hs_cells(mbs, ring, zh, gen)
    # ---- white canvas roofs over the courts east of the parvis (aerials hs_06/07/08)
    if not lod:
        tent(deco, (233.0, 177.0), (0.06, 1.0), 13.0, 10.0, g + 12.0, 1.8, 4.2)
        tent(deco, (249.5, 178.0), (1.0, 0.07), 15.0, 11.0, g + 11.0, 1.8, 4.4)
    # ---- Chapel of the Franks: small dome on its roof
    i_fs = find_edge(ring, (221.75, 179.62), (1.0, 0.077))
    if i_fs is not None:
        e = Edge(ring[i_fs], ring[(i_fs + 1) % len(ring)])
        c = e.P(e.L / 2, 0, -2.5)
        zf = g + 11.6
        if lod:
            dome(sol, c.x, c.y, zf, 2.0, "lead", rise=0.95, seg=8, rings=2)
        else:
            drum(sol, c.x, c.y, 1.85, zf - 0.05, zf + 1.1, 16, "ashlar", stone)
            ring_band(sol, c.x, c.y, 2.0, zf + 0.95, zf + 1.15, 16, "dressed", DRESSED)
            dome(sol, c.x, c.y, zf + 1.15, 1.95, "lead", rise=0.95, rings=5, ribs=16, col=(0.95, 0.97, 1.0),
                 rib_col=(1.25, 1.25, 1.25))
            cross(deco, (c.x, c.y), zf + 1.15 + 1.95 * 0.95, 1.0, gold(deco), gold_col(deco))


def _hs_tower(mbs, g, tf, gen, lod):
    """Romanesque bell tower at the NW corner of the parvis (OSM 1022663529; photos hs_04..08,
    hs_12): pale shaft, cornices at ~15.6 and ~20.5 m, one arched window per face on the middle
    storey, paired arched openings with a colonnette on the top storey, low tiled pyramid with
    deep eaves (walls to 26 m, roof to ~29 m)."""
    sol, deco = mbs["solid"], mbs["deco"]
    W = HS_TOWER
    tn = Vector((-tf.y, tf.x))                                      # north-ish
    ne = v2(HS_TOWER_NE)
    c = ne - tf * (W / 2) - tn * (W / 2)
    rg = rect_ring(c, tf, W, W)                                     # CCW: SW, SE, NE, NW
    z0, z1 = g + 8.6, g + 26.0
    if lod:
        for k in range(4):
            a, b = rg[k], rg[(k + 1) % 4]
            sol.poly([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], "ashlar",
                     Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=HS_PALE)
        pyramid_roof(sol, rg, z1, 2.2, over=0.8)
        return
    zc1, zc2 = g + 15.6, g + 20.5
    for k in range(4):
        e = Edge(rg[k], rg[(k + 1) % 4])
        uc = e.L / 2
        hs = [win(uc, 1.5, zc1 + 1.0, zc1 + 4.2, "round", VOID, 0.55, frame=0.2)]
        for s in (-1, 1):
            hs.append(win(uc + s * 1.65, 1.7, zc2 + 0.8, zc2 + 4.6, "round", VOID, 0.6))
        if k == 1:                                                  # east face: small window above the chapel
            hs.append(win(uc, 0.7, g + 10.6, g + 12.4, "round", VOID, 0.4))
        wall(sol, e, 0, e.L, z0, z1, "ashlar", HS_PALE, hs, gen)
        for zc in (zc1, zc2):
            cornice(sol, e, 0.0, e.L + 0.25, zc - 0.35, 0.4, 0.25, ends=True)
        for s in (-1, 1):                                           # hood mouldings over the pair
            u0, u1 = uc + s * 1.65 - 0.85, uc + s * 1.65 + 0.85
            frame(sol, e, arch_ol(u0, u1, zc2 + 3.74, zc2 + 3.75, "round", seg=8), 0.16, 0.0, 0.08)
            obox(sol, e.P(uc + s * 1.65, 0, 0.15), e.t, e.n, 2.0, 0.3, zc2 + 0.6, zc2 + 0.8, "dressed",
                 col=DRESSED, bottom=True, skip=(0,))                # little balcony sills
        cornice(sol, e, 0.0, e.L + 0.32, z1 - 0.45, 0.45, 0.32, ends=True)
    pyramid_roof(sol, rg, z1, 2.2, over=0.9)
    mk.tube(deco, [Vector((c.x, c.y, z1 + 2.1)), Vector((c.x, c.y, z1 + 5.0))], 0.04, "iron", sides=6)


def tent(mb, c, t, length, width, z, h_eave, h_ridge, mat="lime", col=(1.0, 0.99, 0.96)):
    """White canvas roof on poles over a roof court (ridge along t)."""
    c, t = v2(c), v2(t).normalized()
    s = Vector((-t.y, t.x))
    P = lambda a, b, zz: Vector((*(c + t * a + s * b), zz))         # noqa: E731
    L2, W2 = length / 2, width / 2
    ze, zr = z + h_eave, z + h_ridge
    for side in (-1, 1):
        q = [P(-L2, side * W2, ze), P(L2, side * W2, ze), P(L2, 0, zr), P(-L2, 0, zr)]
        nrm = Vector((*(s * side), 0)) + UP
        mb.poly(q, mat, nrm, col=col)
        mb.poly(q[::-1], mat, -nrm, col=tuple(x * 0.8 for x in col))
    for a in (-L2, L2):                                             # gable valances
        tri = [P(a, -W2, ze), P(a, W2, ze), P(a, 0, zr)]
        nrm = Vector((*(t * (1 if a > 0 else -1)), 0))
        mb.poly(tri, mat, nrm, col=col)
        mb.poly(tri[::-1], mat, -nrm, col=col)
    for a in (-L2, 0, L2):
        for b in (-W2, W2):
            mk.tube(mb, [P(a, b, z), P(a, b, ze)], 0.05, "metal_grey", sides=4)


def _hs_cells(mbs, ring, zh, gen):
    """Ethiopian monks' cells round the roof court of Deir es-Sultan (photos hs_06/07, hs_02):
    small whitewashed rooms with green doors and low domes."""
    sol = mbs["solid"]
    cells = [((247.5, 217.0), (1, 0.08), 3.4, 2.6), ((251.5, 217.35), (1, 0.08), 3.0, 2.6),
             ((259.5, 218.0), (1, 0.08), 3.6, 2.6), ((243.3, 197.5), (0.05, -1), 3.2, 2.4),
             ((243.6, 203.0), (0.05, -1), 3.4, 2.4), ((262.0, 205.5), (-0.7, -0.72), 3.0, 2.4)]
    for (cx, cy), t, w, d in cells:
        if not mk.point_in((cx, cy), ring):
            continue
        rg = rect_ring((cx, cy), t, w, d)
        h = 2.7
        for k in range(4):
            e = Edge(rg[k], rg[(k + 1) % 4])
            hs = [win(e.L / 2, 0.8, zh, zh + 1.9, "flat", "door_green", 0.12, floor=True)] if k == 0 else \
                ([win(e.L / 2, 0.45, zh + 1.2, zh + 1.8, "flat", VOID, 0.15)] if k == 2 else [])
            wall(sol, e, 0, e.L, zh - 0.02, zh + h, "lime", HS_LIME, hs, gen)
        cap(sol, rg, zh + h, "lime", HS_LIME)
        dome(sol, cx, cy, zh + h, min(w, d) * 0.36, "lime", rise=0.7, seg=10, rings=3, col=HS_LIME)


def _hs_specials(Z, mbs, ring, g, base, gen, tf, nf):
    """Detailed walls round the parvis (special edges matched on the zone polygons)."""
    sol, deco = mbs["solid"], mbs["deco"]

    def edge_of(mid, d):
        i = find_edge(ring, mid, d)
        return (ring[i], ring[(i + 1) % len(ring)]) if i is not None else None

    fac = edge_of((211.27, 184.01), (1.0, 0.078))
    if fac:
        Z.special(fac[0], fac[1], _hs_facade(mbs, g, base, gen))
    fw = edge_of((218.88, 182.0), (0.05, -1.0))
    if fw:
        Z.special(fw[0], fw[1], _hs_franks_west(mbs, g, base, gen))
        # the door at the stair head, as a card on the face: the zone edge there does not always match the
        # special (it built a blank wall)  (_hs_specials runs for the full model only)
        ef_ = Edge(fw[0], fw[1])
        mk.card(deco, ef_.P(1.05, g + 2.2, 0.03), ef_.t, UP, 1.2, 2.6, "doors", cell_uv(gen, "doors", "door_wood"))
        frame(sol, ef_, rect(0.45, 1.65, g + 2.2, g + 4.8), 0.15, 0.0, 0.1)
    fs = edge_of((221.75, 179.62), (1.0, 0.077))
    if fs:
        Z.special(fs[0], fs[1], _hs_franks_south(mbs, g, base, gen))
    ea = edge_of((225.17, 172.1), (0.089, -1.0))
    if ea:
        def east_holes(z0, z1, L=math.dist(*ea)):
            return [win(3.3, 1.6, g, g + 3.7, "pointed", "door_green", 0.45, frame=0.2, floor=True),
                    win(6.5, 0.8, g + 6.0, g + 7.3, "flat", VOID, 0.3, grille=True, frame=0.12),
                    win(10.0, 0.8, g + 6.0, g + 7.3, "flat", VOID, 0.3, grille=True, frame=0.12),
                    win(12.6, 1.0, g + 2.4, g + 4.6, "pointed", VOID, 0.35, grille=True, frame=0.15)]
        Z.special(ea[0], ea[1], edge_hook(east_holes, gen=gen))
    jn = edge_of((207.88, 165.76), (-0.084, 1.0))                  # St John / St James chapels (west side)
    if jn:
        def john_holes(z0, z1):
            return [hole(arch_ol(5.0, 10.4, g + 4.2, g + 6.6, "round", seg=12), 1.3, "wall"),
                    win(3.1, 1.0, g, g + 2.3, "flat", "door_wood", 0.2, floor=True, frame=0.15),
                    win(3.1, 0.6, g + 8.4, g + 9.7, "round", VOID, 0.35, grille=True)]

        def john_extras(mb, e, ua, ub, z0, z1, mat, col):
            if ua < 2.0 and ub > 10.6:
                frame(sol, e, arch_ol(5.0, 10.4, g + 6.59, g + 6.6, "round", seg=12), 0.3, 0.0, 0.1)
                # dark masonry block below the niche (photos hs_05..07, hs_12)
                obox(sol, e.P(7.8, 0, 0.45), e.t, e.n, 5.0, 0.9, base, g + 3.9, "rubble", col=(0.6, 0.58, 0.55),
                     skip=(0,))
        Z.special(jn[0], jn[1], edge_hook(john_holes, john_extras, gen))
    fm = edge_of((206.39, 179.32), (-0.083, 1.0))                  # Forty Martyrs: small arched window
    if fm:
        Z.special(fm[0], fm[1], edge_hook(lambda z0, z1: [win(1.38, 0.7, g + 3.2, g + 4.9, "round", VOID, 0.35,
                                                              grille=True, frame=0.12)], gen=gen))
    sj = edge_of((207.14, 159.46), (0.811, 0.585))                 # St James: door
    if sj:
        Z.special(sj[0], sj[1], edge_hook(lambda z0, z1: [win(1.5, 1.0, g, g + 2.3, "round", "door_wood", 0.2,
                                                              floor=True, frame=0.12)], gen=gen))
    st = edge_of((193.5, 156.2), (1.0, 0.087))                     # St Helena Rd frontage
    if st:
        def sth(z0, z1):
            return [win(u, 0.8, g + 7.0, g + 8.4, "flat", VOID, 0.3, grille=True, frame=0.12) for u in (3, 7, 11, 15, 19, 23)]
        Z.special(st[0], st[1], edge_hook(sth, gen=gen))
    # facade storey behind the Franks chapel (zone boundary 0.25 m south of the facade line):
    # third arched window and the top cornice (photo hs_10)
    if fac:
        A, B = v2(fac[0]), v2(fac[1])
        t = (B - A).normalized()
        n = Vector((t.y, -t.x))
        a = A + n * 0.25 + t * ((218.75 - A.x) / t.x)
        b = A + n * 0.25 + t * ((224.2 - A.x) / t.x)
        Lb = (b - a).length

        def third(z0, z1):
            return [win(Lb * 0.42, 1.3, g + 13.2, g + 16.6, "round", "glass", 0.4, grille=True)]

        def third_x(mb, e, ua, ub, z0, z1, mat, col):
            if ub - ua > 4:
                uc = Lb * 0.42
                frame(sol, e, arch_ol(uc - 0.65, uc + 0.65, g + 15.94, g + 15.95, "round"), 0.3, 0, 0.1)
                cornice(sol, e, ua, ub, g + 19.4, 0.9, 0.5, ends=True)
        Z.special(tuple(a), tuple(b), edge_hook(third, third_x, gen))


def u_band(outer, inner):
    """Band between two outlines sharing their bottom line: outer bottom-right -> over the head ->
    bottom-left, then the inner outline back the other way."""
    return outer[1:] + [outer[0]] + [inner[0]] + inner[:0:-1]


def _hs_facade(mbs, g, base, gen):
    """South transept facade on the parvis (photos hs_07, hs_10, hs_12; landmarks_city.md S1):
    double Crusader portal with three stepped pointed orders, colonnettes and hood mouldings (left
    doorway open and dark, right one walled up), cornice at ~10 m, two round-arched windows in
    arched recesses above, cornice and railing at ~20 m, the immovable ladder, and the stair up
    to the Chapel of the Franks."""
    sol, deco = mbs["solid"], mbs["deco"]

    def fn(mb, e, ua, ub, z0, z1, mat, col):
        L = e.L
        if ua > 0.2 or ub < L - 0.2 or L < 13.0:
            return False
        zs, rise0 = g + 4.5, 3.8
        st, sd = 0.38, 0.33
        portals = [(1.65, 6.95, True), (7.55, 12.85, False)]
        bays = [((a + b) / 2) for a, b, _ in portals]
        holes_ = []
        for u0, u1, _ in portals:
            holes_.append(arch_ol(u0, u1, base, zs, "pointed", rise0, seg=10))
        ups = []
        for uc in bays:
            ups.append(arch_ol(uc - 2.45, uc + 2.45, g + 10.85, g + 15.5, "round", seg=12))
        face(mb, e, rect(0, L, z0, z1), mat, 0.0, holes_ + ups, col)
        dkcol = tuple(c * 0.93 for c in col)
        for (u0, u1, open_), O0 in zip(portals, holes_):
            uc = (u0 + u1) / 2
            orders = [arch_ol(u0 + st * k, u1 - st * k, base, zs, "pointed", rise0 - st * k, seg=10) for k in range(4)]
            for k in range(3):
                tunnel(mb, e, orders[k], -sd * k, -sd * (k + 1), mat, floor=True, col=col)
                face(mb, e, u_band(orders[k], orders[k + 1]), mat, -sd * (k + 1), col=col)
            offt = -sd * 3
            door = rect(uc - 1.4, uc + 1.4, base, g + 4.4)
            if open_:
                face(mb, e, u_band(orders[3], door), mat, offt, col=dkcol)
                # a dim stone interior 5 m deep (1.6 m to a black panel read as a flat navy void)
                tunnel(mb, e, door, offt, offt - 5.0, mat, floor=True, col=(0.42, 0.39, 0.35))
                face(mb, e, door, mat, offt - 5.0, col=(0.16, 0.14, 0.12))
                r = cell_uv(gen, "doors", "door_wood")
                if r:                                           # leaves folded back against the reveals
                    for s, uu in ((-1, uc - 1.35), (1, uc + 1.35)):
                        half = (r[0], r[1], (r[0] + r[2]) / 2, r[3]) if s < 0 else ((r[0] + r[2]) / 2, r[1], r[2], r[3])
                        q = [e.P(uu, g, offt - 0.1), e.P(uu, g, offt - 1.5), e.P(uu, g + 4.3, offt - 1.5),
                             e.P(uu, g + 4.3, offt - 0.1)]
                        mb.poly(q, "doors", e.t * (-s), uv=[(half[0], half[1]), (half[2], half[1]), (half[2], half[3]),
                                                             (half[0], half[3])])
                # floor of the recess and the doorway (the parvis ground stops at the wall line)
                fl = [e.P(u0, g + 0.005, 0), e.P(u1, g + 0.005, 0), e.P(u1 - st * 3, g + 0.005, offt),
                      e.P(uc + 1.4, g + 0.005, offt), e.P(uc + 1.4, g + 0.005, offt - 1.6),
                      e.P(uc - 1.4, g + 0.005, offt - 1.6), e.P(uc - 1.4, g + 0.005, offt), e.P(u0 + st * 3, g + 0.005, offt)]
                cap(mb, [(p.x, p.y) for p in fl], g + 0.005, "paving")
            else:
                face(mb, e, orders[3], mat, offt, col=dkcol)      # walled-up doorway
                fl = [e.P(u0, 0, 0), e.P(u1, 0, 0), e.P(u1 - st * 3, 0, offt), e.P(u0 + st * 3, 0, offt)]
                cap(mb, [(p.x, p.y) for p in fl], g + 0.005, "paving")
            # lintel band over the doorway
            obox(mb, e.P(uc, 0, offt + 0.05), e.t, e.n, 3.3, 0.1, g + 4.4, g + 4.75, "dressed", col=DRESSED,
                 bottom=True, skip=(0,))
            for k in range(3):                                  # colonnettes in the re-entrant corners
                for uu in (u0 + st * k + 0.17, u1 - st * k - 0.17):
                    column(mb, e.P(uu, 0, -sd * (k + 1) + 0.17), g, zs, 0.14)
            frame(mb, e, arch_ol(u0, u1, zs - 0.01, zs, "pointed", rise0, seg=10), 0.29, 0.0, 0.16)
        # upper storey: arched recesses, windows, colonnettes
        for uc, U0 in zip(bays, ups):
            U1 = arch_ol(uc - 2.1, uc + 2.1, g + 10.85, g + 15.5, "round", seg=12)
            tunnel(mb, e, U0, 0.0, -0.25, mat, col=col)
            face(mb, e, u_band(U0, U1), mat, -0.25, col=col)
            tunnel(mb, e, U1, -0.25, -0.5, mat, col=col)
            W = arch_ol(uc - 0.65, uc + 0.65, g + 12.4, g + 14.9, "round", seg=8)
            face(mb, e, U1, mat, -0.5, [W], col=dkcol)
            build_hole(mb, e, hole(W, 0.4, "glass", grille=True), mat, col, gen, -0.5)
            frame(mb, e, arch_ol(uc - 2.45, uc + 2.45, g + 15.49, g + 15.5, "round", seg=12), 0.32, 0.0, 0.12)
            frame(mb, e, arch_ol(uc - 0.65, uc + 0.65, g + 14.89, g + 14.9, "round", seg=8), 0.18, -0.5, 0.06)
            for s in (-1, 1):
                column(mb, e.P(uc + s * 1.05, 0, -0.5 + 0.16), g + 12.3, g + 14.95, 0.12)
        for uu in (1.55, 7.25, 12.95):
            column(mb, e.P(uu, 0, 0.21), g + 10.85, g + 15.5, 0.19)
        cornice(mb, e, 0.3, L, g + 9.95, 0.9, 0.45, ends=True)
        cornice(mb, e, 0.0, L, g + 19.4, 0.9, 0.55, ends=True)
        rail(deco, [e.P(0.4, 0, -0.35), e.P(L - 0.1, 0, -0.35)], z1, h=1.1, closed=False)
        # the immovable ladder: on the cornice ledge, leaning into the right window's recess
        ladder(deco, e.P(10.55, g + 10.86, 0.3), e.P(10.55, g + 12.95, -0.42))
        # stair up to the Chapel of the Franks along the facade (OSM way 1547245013, photo hs_04)
        steps_run(sol, e, 12.95, 14.98, 0.0, 1.9, g, g + 2.2, 9, base)
        return True
    return fn


def _hs_franks_west(mbs, g, base, gen):
    """West face of the Chapel of the Franks: glazed iron-grid door at the stair head (photo hs_04)."""
    def fn(mb, e, ua, ub, z0, z1, mat, col):
        # (any part of the edge the zones hand over: it is split, and requiring the whole edge left the
        #  stair from the parvis running into a blank wall)
        hs = [win(1.05, 1.3, g + 2.2, g + 5.0, "round", "glass", 0.35, grille=True, frame=0.15),
              win(3.6, 0.6, g + 6.8, g + 8.2, "round", VOID, 0.3, grille=True)]
        wall(mb, e, ua, ub, z0, z1, mat, col, holes_in(hs, ua, ub), gen)
        if z1 > g + 11.6:
            cornice(mb, e, max(-0.2, ua), min(e.L + 0.35, ub + (0.35 if ub > e.L - 0.2 else 0.0)), g + 11.0, 0.6, 0.35, ends=True)
        if ub > 1.95:
            cornice(mb, e, max(1.95, ua), ub, g + 5.0, 0.3, 0.2, ends=True)
        return True
    return fn


def _hs_franks_south(mbs, g, base, gen):
    """South face of the Chapel of the Franks (photos hs_10, hs_01_10053108): door and small window
    below, string course at 5 m, the large round-arched glazed window between marble colonnettes."""
    def fn(mb, e, ua, ub, z0, z1, mat, col):
        L = e.L
        uc = min(2.75, L / 2)
        hs = [win(L - 1.0, 0.9, g, g + 2.05, "flat", "door_wood", 0.2, floor=True, frame=0.12),
              win(L - 1.0, 0.45, g + 2.6, g + 3.1, "flat", VOID, 0.2, grille=True),
              win(uc, 3.2, g + 5.4, g + 9.9, "round", "glass", 0.45, grille=True)]
        wall(mb, e, ua, ub, z0, z1, mat, col, holes_in(hs, ua, ub), gen)
        if ua <= uc - 2.2 and ub >= uc + 2.2:                  # the window's frame and colonnettes, once
            frame(mb, e, arch_ol(uc - 1.6, uc + 1.6, g + 8.29, g + 8.3, "round", seg=10), 0.3, 0.0, 0.1)
            for uu in (uc - 2.0, uc + 2.0):
                column(mb, e.P(uu, 0, 0.2), g + 5.3, g + 8.3, 0.17, col=(1.08, 1.08, 1.08))
        cornice(mb, e, ua, ub, g + 5.0, 0.3, 0.2, ends=True)
        if z1 > g + 11.6:
            cornice(mb, e, ua, ub + 0.2, g + 11.0, 0.6, 0.35, ends=True)
        return True
    return fn


# ================================================================== generic parts
def solid_of(mbs):
    return mbs["solid"], mbs["deco"]


def big_box(ring, pad=20.0):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return poly_box(min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def massing(mbs, bd, gen, lod, mat="ashlar", col=None, top=None, roof="lime", parapet_h=0.8):
    """Plain block on the whole footprint (windows on exposed edges, parapet) for host buildings."""
    sol = mbs["solid"]
    col = col or tuple(min(1.0, c / 1.06) for c in bd.get("tint", (1, 1, 1)))
    z1 = bd["top"] if top is None else top
    Z = Zones(bd, gen)
    Z.add("all", big_box(bd["ring"]), z1, mat, col, roof=roof)
    Z.build(sol, lod)
    if parapet_h and not lod:
        parapet(sol, [tuple(p) for p in bd["ring"]], z1, parapet_h, 0.3, mat, col)
    return Z


def gable_roof(mb, c, t, L, W, z, rise, mat="roof_tiles", end_mat="ashlar", end_col=None, over=0.35, hip=False,
               z_eps=0.0):
    """Pitched roof over the oriented rectangle (c, t, L x W) with eaves at z; gable ends in end_mat
    (flush with the end walls) or hipped ends."""
    c, t = v2(c), v2(t).normalized()
    s = Vector((-t.y, t.x))
    P = lambda a, b, zz: Vector((*(c + t * a + s * b), zz))         # noqa: E731
    L2, W2 = L / 2 + over, W / 2 + over
    dz = rise * over / (W / 2)
    ze = z - dz
    r0 = -L2 + (W2 if hip else 0)
    r1 = L2 - (W2 if hip else 0)
    for side in (-1, 1):
        q = [P(-L2, side * W2, ze), P(L2, side * W2, ze), P(r1, 0, z + rise), P(r0, 0, z + rise)]
        mb.poly(q, mat, Vector((*(s * side), 0)) + UP)
        mb.poly([P(-L2, side * W2, ze), P(L2, side * W2, ze), P(L2, side * W2, ze - 0.12), P(-L2, side * W2, ze - 0.12)],
                mat, Vector((*(s * side), 0)))
    for a, sg in ((-L2, -1), (L2, 1)):
        n = Vector((*(t * sg), 0))
        if hip:
            mb.poly([P(a, -W2, ze), P(a, W2, ze), P(r1 if sg > 0 else r0, 0, z + rise)], mat, n + UP)
        else:
            mb.poly([P(a, -W2, ze), P(a, W2, ze), P(a, W2, ze - 0.12), P(a, -W2, ze - 0.12)], mat, n)
            aa = a - sg * over
            tri = [P(aa, -W / 2, z), P(aa, W / 2, z), P(aa, 0, z + rise)]
            mb.poly(tri, end_mat, n, col=end_col)
    zs = ze - 0.12 - z_eps                              # eave soffits only (crossing roofs never share a plane)
    for side in (-1, 1):
        mb.poly([P(-L2, side * W2, zs), P(L2, side * W2, zs), P(L2, side * W / 2, zs), P(-L2, side * W / 2, zs)], mat, -UP)
    if over > 0:
        for a_, sg in ((-1, -1), (1, 1)):
            mb.poly([P(sg * L2, -W / 2, zs), P(sg * L / 2, -W / 2, zs), P(sg * L / 2, W / 2, zs), P(sg * L2, W / 2, zs)],
                    mat, -UP)


def square_shaft(mb, c, t, w, z0, z1, mat, col, gen, holes_fn=None, d=None):
    """Square (w x d) shaft; holes_fn(k, e, L) gives the holes of face k (0 = the face along t)."""
    rg = rect_ring(c, t, w, d or w)
    for k in range(4):
        e = Edge(rg[k], rg[(k + 1) % 4])
        hs = holes_fn(k, e, e.L) if holes_fn else []
        wall(mb, e, 0, e.L, z0, z1, mat, col, hs, gen)
    return rg


def ring_cornice(mb, rg, z, h, proj, mat="dressed", col=DRESSED):
    """Cornice round a closed CCW ring (each side a moulded band, mitred by overlap at the corners)."""
    for k in range(len(rg)):
        e = Edge(rg[k], rg[(k + 1) % len(rg)])
        cornice(mb, e, 0.0, e.L + proj, z, h, proj, mat, col, ends=True)   # each corner covered once


def minaret(mbs, c, t, w, z0, z_bal, gen, lod=False, col=(1.0, 0.95, 0.86), upper="oct", h_up=3.4,
            cap="dome", cap_mat="lead", mat="ashlar", stages=3):
    """Mamluk / Ottoman minaret: square shaft with string courses and small arched windows, corbelled
    balcony with a parapet, an octagonal (or round) upper stage with arched openings, a small dome or
    cone and a crescent finial."""
    sol, deco = solid_of(mbs)
    c, t = v2(c), v2(t).normalized()
    ru = w * 0.36
    if lod:
        rg = rect_ring(c, t, w, w)
        prism(sol, rg, z0, z_bal + 0.6, mat, col, roof=mat)
        mk.cylinder(sol, c.x, c.y, z_bal + 0.6, z_bal + h_up, ru, mat, seg=6, cap=False, col=col)
        mk.cylinder(sol, c.x, c.y, z_bal + h_up, z_bal + h_up + ru * 1.6, ru * 1.05, cap_mat, seg=6, cap=False, r1=0.05)
        return
    hz = (z_bal - z0)

    def holes(k, e, L):
        out = []
        for j in range(stages):
            zb = z0 + hz * (0.25 + 0.75 * (j + 0.4) / stages)
            if zb + 1.3 < z_bal - 0.6:
                out.append(win(L / 2, 0.42, zb, zb + 1.3, "round", VOID, 0.3))
        return out
    rg = square_shaft(sol, c, t, w, z0, z_bal, mat, col, gen, holes)
    for j in range(1, stages):
        zc = z0 + hz * (0.25 + 0.75 * j / stages)
        ring_cornice(sol, rg, zc - 0.12, 0.24, 0.1, "dressed", DRESSED)
    # balcony: corbels + slab + parapet
    ring_cornice(sol, rg, z_bal - 0.55, 0.55, 0.45, "dressed", DRESSED)
    out = mk.inset_ring(rg, -0.5)
    prism(sol, out, z_bal, z_bal + 0.2, "dressed", DRESSED, roof="dressed")
    parapet(sol, out, z_bal + 0.2, 0.85, 0.15, "ashlar", col)
    # upper stage
    zu0, zu1 = z_bal + 0.2, z_bal + h_up
    if upper == "oct":
        drum(sol, c.x, c.y, ru / math.cos(math.pi / 8), zu0, zu1, 8, mat, col,
             win=(ru * 0.55, zu0 + 0.9, zu0 + 2.2, "round", 0.25, VOID), gen=gen, every=2, rot=math.pi / 8)
    else:
        drum(sol, c.x, c.y, ru, zu0, zu1, 12, mat, col, win=(ru * 0.4, zu0 + 0.9, zu0 + 2.2, "round", 0.2, VOID),
             gen=gen, every=3)
    ring_band(sol, c.x, c.y, ru * 1.15, zu1 - 0.25, zu1 + 0.05, 12, "dressed", DRESSED)
    if cap == "dome":
        ztop = dome(sol, c.x, c.y, zu1 + 0.05, ru * 1.02, cap_mat, rise=1.1, seg=12, rings=4,
                    col=(0.9, 0.9, 0.9) if cap_mat == "lead" else col)
    else:
        mk.cylinder(sol, c.x, c.y, zu1 + 0.05, zu1 + ru * 2.2, ru * 1.1, cap_mat, seg=12, cap=False, r1=0.04)
        ztop = zu1 + ru * 2.2
    crescent_finial(deco, (c.x, c.y), ztop - 0.05, 1.6, gold(deco), gold_col(deco))


def square_tower(mbs, c, t, w, z0, stages, gen, lod, mat="ashlar", col=(1.0, 0.97, 0.9)):
    """Square tower; stages = [(z_top, holes_fn(k, e, L) or None, cornice_proj)]. Returns the top ring."""
    sol = mbs["solid"]
    zb = z0
    rg = rect_ring(c, t, w, w)
    for z_top, holes_fn, proj in stages:
        square_shaft(sol, c, t, w, zb, z_top, mat, col, gen, None if lod else holes_fn)
        if proj and not lod:
            ring_cornice(sol, rg, z_top - 0.4, 0.4, proj)
        zb = z_top
    return rg, zb


def spire(mb, c, t, w, z, h, mat, col=None, n=4):
    """Square (n=4) or octagonal (n=8) spire."""
    c, t = v2(c), v2(t).normalized()
    if n == 4:
        rg = rect_ring(c, t, w, w)
    else:
        a0 = math.atan2(t.y, t.x) + math.pi / 8
        R = w / 2 / math.cos(math.pi / 8)
        rg = [(c.x + R * math.cos(a0 + 2 * math.pi * k / 8), c.y + R * math.sin(a0 + 2 * math.pi * k / 8)) for k in range(8)]
    pyramid(mb, rg, z, h, mat, col)
    cap(mb, rg, z, mat, col, down=True)
    return rg


def win_row(L, zb, zt, sp=4.0, w=1.0, kind="round", back="glass", grille=True, margin=1.5, depth=0.35, frame=0.0):
    n = int((L - 2 * margin) / sp) + 1
    if L < 2 * margin + w:
        return []
    if n <= 1:
        us = [L / 2]
    else:
        step = (L - 2 * margin) / (n - 1)
        us = [margin + step * k for k in range(n)]
    return [win(u, w, zb, zt, kind, back, depth, grille=grille, frame=frame) for u in us]


class StyledZones(Zones):
    """Zones whose exposed street walls get a style of openings instead of the plain window grid."""

    def __init__(self, bd, gen, style):
        super().__init__(bd, gen)
        self.style = style                              # style(L, zg, z_top) -> holes

    def build(self, mb, lod=False):
        for name, poly, z_top, mat, col, roof, windows in self.parts:
            for a, b in _cancel_bridges(poly):
                m = None if lod else self._match(a, b)
                if m:
                    fn, ua, ub, e = m
                    if fn(mb, e, ua, ub, self.base, z_top, mat, col):
                        continue
                ri = self.ring_edge(a, b) if (windows and not lod) else None
                e = Edge(a, b)
                if ri is not None and e.L > 2.5 and (self.exposed[ri] or z_top - self.eground[ri] > 10.0):
                    hs = self.style(e.L, self.eground[ri], z_top) if windows is True else windows(e.L, self.eground[ri], z_top)
                    if not self.exposed[ri]:          # a lower house stands against it: windows above its roof only
                        hs = [h for h in hs if min(p[1] for p in h["ol"]) >= self.eground[ri] + 7.5]   # (a blank face
                    wall(mb, e, 0, e.L, self.base, z_top, mat, col, hs, self.gen)                    # showed above the roofs)
                    continue
                q = [(a[0], a[1], self.base), (b[0], b[1], self.base), (b[0], b[1], z_top), (a[0], a[1], z_top)]
                mb.poly(q, mat, Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=col)
            if roof:
                cap(mb, poly, z_top, roof, ROOF_COL.get(roof, col))


def local_box(c, t, u0, u1, s0, s1):
    """Convex clip polygon given in the frame (c, t): u along t, s to its left."""
    c, t = v2(c), v2(t).normalized()
    s = Vector((-t.y, t.x))
    return [tuple(c + t * u + s * v) for u, v in ((u0, s0), (u1, s0), (u1, s1), (u0, s1))]


# ================================================================== Lutheran Church of the Redeemer
RED_COL = (1.0, 0.96, 0.88)


def redeemer(mbs, bd, gen, place, lod=False):
    """Church of the Redeemer (1898, w29268902): cross plan, 50 m west tower (OSM w375040918 at the
    SW corner; photos red_*), crossing dome on an octagonal drum, tiled pitched roofs."""
    sol, deco = solid_of(mbs)
    ring = [tuple(p) for p in bd["ring"]]
    g = bd["ground"]
    col = RED_COL
    # tower square at the SW corner, its outer faces 0.2 m proud of the church walls
    sw = min(ring, key=lambda p: math.dist(p, (265.1, 133.5)))
    i_s = find_edge(ring, (268.8, 133.7), (1.0, 0.05), tol=4)
    tx = (v2(ring[(i_s + 1) % len(ring)]) - v2(ring[i_s])).normalized() if i_s is not None else Vector((1, 0))
    ty = Vector((-tx.y, tx.x))
    W = 7.4
    tc = v2(sw) - tx * 0.2 - ty * 0.2 + tx * (W / 2) + ty * (W / 2)

    def style(L, zg, z_top):
        return win_row(L, zg + 5.0, zg + 9.5, sp=4.2, w=1.2, kind="round", back="glass", margin=1.8, frame=0.15)
    Z = StyledZones(bd, gen, style)
    ze, za = g + 13.5, g + 11.5
    tin = tc + tx * (W / 2 - 0.8) + ty * (W / 2 - 0.8)                # zone cuts inside the tower
    Z.add("nave_e", [(tin.x, 120), (290.8, 120), (290.8, tin.y), (tin.x, tin.y)], ze, "ashlar", col, roof=None)
    Z.add("nave_n", [(250, tin.y), (290.8, tin.y), (290.8, 165), (250, 165)], ze, "ashlar", col, roof=None)
    Z.add("cross", poly_box(290.8, 110, 299.4, 170), ze, "ashlar", col, roof=None)
    Z.add("apse", poly_box(299.4, 110, 320, 170), za, "ashlar", col, roof="lead")
    i_n = find_edge(ring, (294.8, 152.15), (-1.0, 0.01), tol=4)
    if i_n is not None and not lod:
        a, b = ring[i_n], ring[(i_n + 1) % len(ring)]

        def north(z0, z1, L=math.dist(a, b)):
            return [hole(circle(L / 2, g + 9.6, 1.5, 16), 0.4, "glass"),
                    win(L / 2, 2.4, g, g + 5.2, "round", "door_wood", 0.6, floor=True, frame=0.35)]
        Z.special(a, b, edge_hook(north, gen=gen))
    Z.build(sol, lod)
    # pitched roofs: nave (E-W) to the crossing centre, transepts (N-S), apse
    cx = 295.1
    gable_roof(sol, ((265.0 + cx) / 2, 140.2), (1, 0), cx - 265.0, 13.4, ze, 3.6, end_col=col, over=0.3 if not lod else 0.0)
    gable_roof(sol, (295.1, 140.15), (0, 1), 24.2, 8.6, ze, 3.6, end_col=col, over=0.3 if not lod else 0.0,
               z_eps=0.015)
    # crossing: octagonal drum with round windows, ribbed lead dome, cross
    dz0, dz1 = ze + 3.0, ze + 6.6
    if lod:
        mk.cylinder(sol, cx, 140.15, dz0 - 1, dz1, 4.0, "ashlar", seg=8, cap=False, col=col)
        dome(sol, cx, 140.15, dz1, 4.2, "lead", rise=0.95, seg=8, rings=2)
    else:
        drum(sol, cx, 140.15, 4.0, dz0 - 1.0, dz1, 8, "ashlar", col, rot=math.pi / 8,
             win=(0.9, dz0 + 0.3, dz0 + 2.3, "round", 0.35, "glass"), gen=gen, every=2)
        ring_band(sol, cx, 140.15, 4.45, dz1 - 0.35, dz1 + 0.05, 8, "dressed", DRESSED, rot=math.pi / 8)
        ztop = dome(sol, cx, 140.15, dz1 + 0.05, 4.2, "lead", rise=0.95, rings=6, ribs=16,
                    col=(0.75, 0.82, 0.9), rib_col=(1.1, 1.1, 1.15))
        cross(deco, (cx, 140.15), ztop - 0.05, 1.8, gold(deco), gold_col(deco))
    _redeemer_tower(mbs, tc, tx, W, g, bd["base"], gen, lod)


def _redeemer_tower(mbs, c, t, W, g, base, gen, lod):
    """West tower: string courses at 11 / 22 / 30 m, paired belfry openings, corbel table, stone
    spire with corner pinnacles (photos red_04, red_06, red_08); top of the cross ~50 m."""
    sol, deco = solid_of(mbs)
    col = (1.02, 1.0, 0.93)

    def low(k, e, L):
        return [win(L / 2, 0.7, g + 6.0, g + 8.4, "round", VOID, 0.4)] if k in (0, 3) else []

    def mid(k, e, L):
        return [win(L / 2, 0.8, g + 14.0, g + 18.0, "round", VOID, 0.45)]

    def up(k, e, L):
        return [win(L / 2 - 0.85, 0.75, g + 23.5, g + 27.5, "round", VOID, 0.45),
                win(L / 2 + 0.85, 0.75, g + 23.5, g + 27.5, "round", VOID, 0.45)]

    def bel(k, e, L):
        return [win(L / 2 - 1.15, 1.25, g + 30.9, g + 35.6, "round", VOID, 0.6, frame=0.18),
                win(L / 2 + 1.15, 1.25, g + 30.9, g + 35.6, "round", VOID, 0.6, frame=0.18)]
    stages = [(g + 11.0, low, 0.18), (g + 22.0, mid, 0.2), (g + 30.0, up, 0.22), (g + 37.0, bel, 0.0)]
    rg, ztop = square_tower(mbs, c, t, W, base, stages, gen, lod, col=col)
    if lod:
        spire(sol, c, t, W - 0.4, ztop, 10.5, "dressed", col)
        return
    ring_cornice(sol, rg, ztop - 0.7, 0.7, 0.45)
    spire(sol, c, t, W - 0.6, ztop, 10.5, "dressed", (0.97, 0.95, 0.9))
    for p in rg:                                                    # corner pinnacles
        q = v2(c) + (v2(p) - v2(c)) * 0.88
        rr = rect_ring(q, t, 0.9, 0.9)
        prism(sol, rr, ztop, ztop + 1.0, "dressed", DRESSED, roof=None)
        pyramid(sol, rr, ztop + 1.0, 1.6, "dressed", DRESSED)
    mk.dome(sol, c.x, c.y, ztop + 10.3, 0.3, "dressed", drum=0.0, seg=8, rings=3, col=DRESSED)
    cross(deco, (c.x, c.y), ztop + 10.55, 1.6, gold(deco), gold_col(deco))


# ================================================================== Mosque of Omar and minarets
OMAR_MIN = (206.891, 145.833)          # OSM node 12893656140 (man_made=tower, tower:type=minaret)
KHANQAH_MIN = "w620113736"             # 24 m2 OSM building on the Omar - Edicule axis, NW of the rotunda


def mosque_omar(mbs, bd, gen, place, lod=False):
    """Mosque of Omar opposite the Holy Sepulchre (w290821793): plain block and its 15th-century
    square minaret on the NE corner (node 12893656140; photos omar_*): square shaft with string
    courses, corbelled balcony, octagonal lantern stage and small lead dome."""
    g = bd["ground"]
    massing(mbs, bd, gen, lod, col=(1.0, 0.93, 0.83), top=g + 9.0)     # two storeys on the parvis side (omar_06)
    ring = [tuple(p) for p in bd["ring"]]
    i = find_edge(ring, (209.7, 147.4), (-1.0, -0.06), tol=4)
    t = (v2(ring[i]) - v2(ring[(i + 1) % len(ring)])).normalized() if i is not None else Vector((1, 0))
    minaret(mbs, OMAR_MIN, t, 3.6, bd["base"], g + 22.5, gen, lod, h_up=3.6)


def khanqah_minaret(mbs, bd, gen, place, lod=False):
    """Minaret of the Khanqah al-Salahiyya (1417): OSM w620113736, the 24 m2 square base on the line
    from the Omar minaret through the Edicule (both tops at about the same level; photo khanqah_08)."""
    ring = [tuple(p) for p in bd["ring"]]
    c, t, L, W = obb(ring)
    w = max(3.2, min(L, W) - 0.2)
    minaret(mbs, c, t, w, bd["base"], bd["ground"] + 19.0, gen, lod, h_up=3.6)


def host_minaret(node, w=3.0, h=17.0, upper="round"):
    """Builder for a building that hosts a minaret given as an OSM node: plain block + minaret."""
    def fn(mbs, bd, gen, place, lod=False):
        massing(mbs, bd, gen, lod)
        ring = [tuple(p) for p in bd["ring"]]
        c, t, L, W = obb(ring)
        minaret(mbs, node, t, w, bd["base"], bd["ground"] + h, gen, lod, upper=upper, h_up=3.2)
    return fn


# ================================================================== Hurva Synagogue
HURVA_C = (363.0, -145.0)              # body: OSM building:part 546355656 (h 16); dome part 372306586
SIDNA_OMAR = (354.6, -157.3)           # Sidna Omar minaret: NW corner of w1394070804 (the mosque, beside the Ramban)


def hurva(mbs, bd, gen, place, lod=False):
    """Hurva Synagogue (rebuilt 2010, w45081545): white cube on a rusticated podium, a great blind
    arch on each face with two rows of arched windows and a trefoil of oculi, square corner turrets,
    tall drum with arched windows and an iron-railed balcony, white dome (photos hurva_*)."""
    sol, deco = solid_of(mbs)
    ring = [tuple(p) for p in bd["ring"]]
    g = bd["ground"]
    white = (1.08, 1.06, 1.0)
    i = find_edge(ring, (359.3, -154.7), (1.0, -0.05), tol=5)
    t = (v2(ring[(i + 1) % len(ring)]) - v2(ring[i])).normalized() if i is not None else Vector((1, 0))
    # a low podium just round the cube (2.5 m wide; it stood 3 m high over the whole OSM footprint, which
    # takes in a stretch of Hurva Square, and walled the synagogue off from the square)
    c = v2(HURVA_C)
    Wb = 19.0
    Z = Zones(bd, gen)
    Z.add("podium", rect_ring(c, t, Wb + 5.0, Wb + 5.0), g + 1.2, "rubble", (1.02, 0.98, 0.9), roof="paving",
          windows=False)
    Z.build(sol, lod)
    zb0, zb1 = g + 1.2, g + 13.2
    rg = rect_ring(c, t, Wb, Wb)
    for k in range(4):
        e = Edge(rg[k], rg[(k + 1) % 4])
        L = e.L
        hs = []
        if not lod:
            hs.append(hole(arch_ol(3.4, L - 3.4, zb0 + 0.5, zb0 + 4.4, "round", seg=14), 0.45, None))
        wall(sol, e, 0, L, zb0 - 0.01, zb1, "ashlar", white, hs, gen)
        if lod:
            continue
        # inside the blind arch: two rows of three arched windows and a trefoil of oculi
        inner = []
        for r_, (z0_, z1_) in enumerate(((zb0 + 1.0, zb0 + 3.2), (zb0 + 4.0, zb0 + 6.4))):
            for du in (-2.6, 0.0, 2.6):
                inner.append(win(L / 2 + du, 1.1, z0_, z1_, "round", "glass", 0.3, grille=False))
        for du, dz in ((-0.9, 0.0), (0.9, 0.0), (0.0, 1.1)):
            inner.append(hole(circle(L / 2 + du, zb0 + 8.0 + dz, 0.5, 10), 0.3, "glass"))
        A = arch_ol(3.4, L - 3.4, zb0 + 0.5, zb0 + 4.4, "round", seg=14)
        face(sol, e, A, "ashlar", -0.45, [h["ol"] for h in inner], white)
        for h in inner:
            build_hole(sol, e, h, "ashlar", white, gen, -0.45)
        frame(sol, e, arch_ol(3.4, L - 3.4, zb0 + 4.39, zb0 + 4.4, "round", seg=14), 0.45, 0.0, 0.12)
        cornice(sol, e, 0.0, L + 0.35, zb1 - 0.5, 0.5, 0.35)
    cap(sol, rg, zb1, "lime")
    # corner turrets
    for p in rg:
        q = v2(p) + (c - v2(p)).normalized() * 1.2
        tr = rect_ring(q, t, 2.8, 2.8)
        prism(sol, tr, zb1 - 0.5, zb1 + 2.2, "ashlar", white, roof="lime")
        if not lod:
            ring_cornice(sol, tr, zb1 + 1.8, 0.4, 0.15)
            mk.cylinder(sol, q.x, q.y, zb1 + 2.2, zb1 + 3.3, 0.35, "dressed", seg=8, col=DRESSED)
            mk.dome(sol, q.x, q.y, zb1 + 3.3, 0.35, "dressed", drum=0.0, seg=8, rings=2, col=DRESSED)
    # drum, balcony, dome
    zd0, zd1 = zb1, zb1 + 4.6
    if lod:
        mk.cylinder(sol, c.x, c.y, zd0, zd1, 6.4, "ashlar", seg=12, cap=False, col=white)
        dome(sol, c.x, c.y, zd1, 6.9, "lime", rise=0.95, seg=12, rings=3, col=white)
    else:
        drum(sol, c.x, c.y, 6.4, zd0 - 0.02, zd1, 24, "ashlar", white,
             win=(0.85, zd0 + 1.2, zd0 + 3.5, "round", 0.35, "glass"), gen=gen, every=2)
        ring_band(sol, c.x, c.y, 7.6, zd0 + 0.6, zd0 + 0.85, 24, "dressed", DRESSED)
        rail(deco, [(c.x + 7.5 * math.cos(2 * math.pi * k / 24), c.y + 7.5 * math.sin(2 * math.pi * k / 24))
                    for k in range(24)], zd0 + 0.85, h=1.1, post=1.6)
        ring_band(sol, c.x, c.y, 6.75, zd1 - 0.3, zd1 + 0.05, 24, "dressed", DRESSED)
        ztop = dome(sol, c.x, c.y, zd1 + 0.05, 6.9, "lime", rise=0.95, seg=32, rings=8, col=white)
        mk.cylinder(sol, c.x, c.y, ztop - 0.1, ztop + 0.3, 0.4, "dressed", seg=8, col=DRESSED)
    # Sidna Omar minaret beside the Ramban synagogue
    minaret(mbs, SIDNA_OMAR, t, 3.4, bd["base"], g + 16.5, gen, lod, upper="round", h_up=3.8)


# ================================================================== St Saviour
SAV_TOWER = (-3.6, 250.4)              # Commons object location of the tower (sav_10..12)


def st_saviour_church(mbs, bd, gen, place, lod=False):
    """St Saviour's church (1885, w106249447): long nave, hipped tiled roof (OSM roof:shape)."""
    sol = mbs["solid"]
    g = bd["ground"]
    col = (1.04, 1.0, 0.92)

    def style(L, zg, z_top):
        return win_row(L, zg + 4.5, zg + 9.5, sp=4.0, w=1.3, kind="round", back="glass", margin=2.0, frame=0.15)
    Z = StyledZones(bd, gen, style)
    ze = g + 14.0
    Z.add("nave", big_box(bd["ring"]), ze, "ashlar", col, roof="lime")
    Z.build(sol, lod)
    ring = [tuple(p) for p in bd["ring"]]
    cc, tt, L, W = obb([p for p in ring if p[1] < 273.5] or ring)
    gable_roof(sol, cc, tt, L, W, ze, 3.2, hip=True, over=0.3 if not lod else 0.0)


def st_saviour_monastery(mbs, bd, gen, place, lod=False):
    """Monastery of St Saviour (r1515591): plain blocks and the tall bell tower, the NW skyline marker:
    cream shaft, clock stage with corner pilasters and balustrade, dark octagonal tiled spire with a
    ball and cross (photos sav_02, sav_07, sav_08)."""
    sol, deco = solid_of(mbs)
    massing(mbs, bd, gen, lod, col=(1.04, 1.0, 0.92))
    g = bd["ground"]
    c = v2(SAV_TOWER)
    t = Vector((0.98, 0.19))
    W = 5.6
    col = (1.06, 1.03, 0.95)

    def bel(k, e, L):
        return [win(L / 2, 1.3, g + 23.6, g + 27.4, "round", VOID, 0.5, frame=0.15)]

    def clock(k, e, L):
        return [win(L / 2 - 1.15, 0.55, g + 28.6, g + 30.4, "round", VOID, 0.3),
                win(L / 2 + 1.15, 0.55, g + 28.6, g + 30.4, "round", VOID, 0.3)]
    stages = [(g + 22.5, None, 0.2), (g + 28.2, bel, 0.25), (g + 32.0, clock, 0.0)]
    rg, ztop = square_tower(mbs, c, t, W, bd["base"], stages, gen, lod, col=col)
    if lod:
        spire(sol, c, t, W - 0.8, ztop, 8.0, "lead", (0.62, 0.78, 0.7), n=8)
        return
    ring_cornice(sol, rg, ztop - 0.5, 0.5, 0.35)
    for k in range(4):                                              # clock faces
        e = Edge(rg[k], rg[(k + 1) % 4])
        cc = e.P(e.L / 2, g + 30.4, 0.03)
        ring_c = [e.P(e.L / 2 + 0.75 * math.cos(2 * math.pi * j / 16), g + 30.4 + 0.75 * math.sin(2 * math.pi * j / 16), 0.04)
                  for j in range(16)]
        sol.poly(ring_c, "lime", e.n, col=(1.1, 1.1, 1.1))
        mk.tube(deco, [cc + e.n * 0.03, cc + e.n * 0.03 + UP * 0.55], 0.03, "iron")
        mk.tube(deco, [cc + e.n * 0.03, cc + e.n * 0.03 + e.t * 0.4], 0.03, "iron")
        for s in (-1, 1):                                           # corner pilasters
            obox(sol, e.P(e.L / 2 + s * (e.L / 2 - 0.25), 0, 0.08), e.t, e.n, 0.5, 0.16, g + 28.2, ztop - 0.5,
                 "dressed", col=DRESSED, skip=(0,))
    out = mk.inset_ring(rg, -0.3)
    rect_r = [tuple(p) for p in out]
    r = cell_uv(gen, "cutout", "balustrade")
    for k in range(4):                                              # balustrade (cut-out card, both sides)
        if r:
            e = Edge(rect_r[k], rect_r[(k + 1) % 4])
            face(deco, e, rect(0, e.L, ztop, ztop + 0.9), "cut", -0.15, uvrect=r)
            face(deco, Edge(rect_r[(k + 1) % 4], rect_r[k]), rect(0, e.L, ztop, ztop + 0.9), "cut", 0.15, uvrect=r)
    zs = ztop + 0.2
    drum(sol, c.x, c.y, (W - 1.6) / 2 / math.cos(math.pi / 8), zs - 0.2, zs + 1.4, 8, "ashlar", col, rot=math.pi / 8)
    spire(sol, c, t, W - 1.4, zs + 1.4, 7.5, "lead", (0.62, 0.78, 0.7), n=8)
    mk.dome(sol, c.x, c.y, zs + 8.7, 0.32, gold(deco), drum=0.0, seg=8, rings=3, col=gold_col(deco))
    cross(deco, (c.x, c.y), zs + 9.3, 1.5, gold(deco), gold_col(deco))


# ================================================================== Tiferet Yisrael
def tiferet(mbs, bd, gen, place, lod=False):
    """Tiferet Yisrael (1872, rebuilt with its dome): square two-storey block with arched windows,
    octagonal drum and a large grey dome."""
    sol, deco = solid_of(mbs)
    g = bd["ground"]
    col = (1.05, 1.02, 0.95)

    def style(L, zg, z_top):
        return (win_row(L, zg + 2.5, zg + 6.2, sp=3.3, w=1.3, kind="round", back="glass", margin=1.6) +
                win_row(L, zg + 8.0, zg + 11.8, sp=3.3, w=1.3, kind="round", back="glass", margin=1.6))
    Z = StyledZones(bd, gen, style)
    z1 = g + 14.0
    Z.add("body", big_box(bd["ring"]), z1, "ashlar", col, roof="lime")
    Z.build(sol, lod)
    ring = [tuple(p) for p in bd["ring"]]
    if not lod:
        ring_cornice(sol, ring, z1 - 0.6, 0.6, 0.4)
        parapet(sol, ring, z1, 0.7, 0.3, "ashlar", col)
    c = centroid(ring)
    if lod:
        mk.cylinder(sol, c.x, c.y, z1, z1 + 3.2, 5.0, "ashlar", seg=8, cap=False, col=col)
        dome(sol, c.x, c.y, z1 + 3.2, 5.3, "lead", rise=0.95, seg=8, rings=3)
        return
    drum(sol, c.x, c.y, 5.0, z1 - 0.02, z1 + 3.4, 8, "ashlar", col, win=(1.0, z1 + 0.7, z1 + 2.7, "round", 0.35, "glass"),
         gen=gen, rot=math.pi / 8)
    ring_band(sol, c.x, c.y, 5.35, z1 + 3.1, z1 + 3.45, 8, "dressed", DRESSED, rot=math.pi / 8)
    ztop = dome(sol, c.x, c.y, z1 + 3.45, 5.3, "lead", rise=0.95, rings=7, ribs=16, col=(0.8, 0.85, 0.9),
                rib_col=(1.1, 1.1, 1.12))
    mk.cylinder(sol, c.x, c.y, ztop - 0.1, ztop + 0.6, 0.45, "lead", seg=8)


# ================================================================== St James Cathedral
JAMES_DOME = (150.5, -233.0)


def st_james(mbs, bd, gen, place, lod=False):
    """Armenian Cathedral of St James (w265410575): massive block, porch of three pointed arches on the
    courtyard (photos james_01..03), central drum and ribbed lead dome."""
    sol, deco = solid_of(mbs)
    g = bd["ground"]
    col = (1.0, 0.96, 0.88)
    ring = [tuple(p) for p in bd["ring"]]

    def style(L, zg, z_top):
        return win_row(L, zg + 7.0, zg + 9.6, sp=5.0, w=0.8, kind="round", back=VOID, margin=2.5, grille=True)
    Z = StyledZones(bd, gen, style)
    z1 = g + 13.0
    Z.add("body", big_box(ring), z1, "ashlar", col, roof="paving")
    i = find_edge(ring, (133.9, -219.35), (-1.0, 0.04), tol=4)
    if i is not None and not lod:
        a, b = ring[i], ring[(i + 1) % len(ring)]

        zp = (bd.get("edge_ground") or [g] * len(ring))[i]

        def porch(z0, z1_, L=math.dist(a, b)):
            sp = L / 3
            return [win(sp * (k + 0.5), sp - 0.9, z0, zp + 6.8, "pointed", "wall", 2.4, floor=True, rise=2.2)
                    for k in range(3)]

        def porch_floor(mb, e, ua, ub, z0, z1_, mat, col):           # the street ground stops at the wall line
            sp = e.L / 3
            for k in range(3):
                u0, u1 = sp * k + 0.45, sp * (k + 1) - 0.45
                cap(mb, [tuple(e.P(u0, 0, 0).xy), tuple(e.P(u1, 0, 0).xy), tuple(e.P(u1, 0, -2.4).xy),
                         tuple(e.P(u0, 0, -2.4).xy)], zp + 0.01, "paving")
                r = cell_uv(gen, "cutout", "rail_moat")
                if r:                                              # wrought-iron screens (photo james_01)
                    face(deco, e, rect(u0, u1, zp, zp + 1.6), "cut", -0.25, uvrect=r)
                    face(deco, Edge(tuple(e.P(e.L, 0, 0).xy), tuple(e.A.xy)), rect(e.L - u1, e.L - u0, zp, zp + 1.6),
                         "cut", 0.25, uvrect=r)
        Z.special(a, b, edge_hook(porch, porch_floor, gen=gen))
    Z.build(sol, lod)
    if not lod:
        parapet(sol, ring, z1, 0.8, 0.3, "ashlar", col)
    c = v2(JAMES_DOME)
    if lod:
        mk.cylinder(sol, c.x, c.y, z1, z1 + 3.0, 3.6, "ashlar", seg=8, cap=False, col=col)
        dome(sol, c.x, c.y, z1 + 3.0, 3.8, "lead", rise=0.9, seg=8, rings=2)
        return
    drum(sol, c.x, c.y, 3.6, z1 - 0.02, z1 + 3.2, 12, "ashlar", col, win=(0.6, z1 + 0.8, z1 + 2.5, "round", 0.35, VOID),
         gen=gen, every=1)
    ring_band(sol, c.x, c.y, 3.9, z1 + 2.9, z1 + 3.25, 12, "dressed", DRESSED)
    ztop = dome(sol, c.x, c.y, z1 + 3.25, 3.85, "lead", rise=0.9, rings=6, ribs=12, col=(0.8, 0.84, 0.9),
                rib_col=(1.1, 1.1, 1.12))
    cross(deco, (c.x, c.y), ztop - 0.05, 1.5, gold(deco), gold_col(deco))


# ================================================================== St Anne
def st_anne(mbs, bd, gen, place, lod=False):
    """Crusader basilica of St Anne (w126864879): austere Romanesque block, higher nave with a low
    stone gable, pointed portal and windows on the west front, stone dome over the crossing on a
    square drum (photos anne_04..07)."""
    sol, deco = solid_of(mbs)
    ring = [tuple(p) for p in bd["ring"]]
    g = bd["ground"]
    col = (1.0, 0.95, 0.86)
    i_w = find_edge(ring, (825.15, 519.45), (0.396, -0.918), tol=5)
    if i_w is not None:
        a, b = v2(ring[i_w]), v2(ring[(i_w + 1) % len(ring)])
    else:
        a, b = Vector((822.5, 525.6)), Vector((827.8, 513.3))
    d = (b - a).normalized()
    t = Vector((-d.y, d.x))                                          # inward: west front -> apse
    c0 = (a + b) / 2

    def style(L, zg, z_top):
        return win_row(L, zg + 5.5, zg + 8.6, sp=5.0, w=0.9, kind="pointed", back="glass", margin=2.0)
    Z = StyledZones(bd, gen, style)
    zn, za = g + 15.0, g + 11.0
    Z.add("nave", local_box(c0, t, -5, 50, -3.8, 3.8), zn, "rubble", col, roof="paving")
    Z.add("aisle_s", local_box(c0, t, -5, 50, -30, -3.8), za, "rubble", col, roof="paving")
    Z.add("aisle_n", local_box(c0, t, -5, 50, 3.8, 30), za, "rubble", col, roof="paving")
    if i_w is not None and not lod:
        def front(z0, z1, L=(b - a).length):
            m = L / 2
            return [win(m, 2.4, g, g + 5.2, "pointed", "door_wood", 0.7, floor=True, frame=0.3, rise=1.6),
                    win(m, 1.4, g + 7.8, g + 11.5, "pointed", "glass", 0.5, grille=True, frame=0.18, rise=1.0),
                    win(m - 4.8, 0.8, g + 5.5, g + 7.8, "pointed", "glass", 0.4, rise=0.6),
                    win(m + 4.8, 0.8, g + 5.5, g + 7.8, "pointed", "glass", 0.4, rise=0.6)]
        Z.special(tuple(a), tuple(b), edge_hook(front, gen=gen))
    Z.build(sol, lod)
    # low stone gable over the nave
    L_n = 33.0
    gable_roof(sol, c0 + t * (L_n / 2 - 0.2), t, L_n, 7.6, zn, 1.4, mat="dressed", end_mat="rubble", end_col=col,
               over=0.0 if lod else 0.15)
    # crossing dome on a square drum
    cd = c0 + t * 24.5
    sq = rect_ring(cd, t, 7.0, 7.0)
    prism(sol, sq, zn, zn + 2.6, "rubble", col, roof="paving")
    if not lod:
        ring_cornice(sol, sq, zn + 2.2, 0.4, 0.2)
    dome(sol, cd.x, cd.y, zn + 2.6, 3.3, "dressed", rise=0.8, seg=12 if lod else 20, rings=3 if lod else 6,
         col=(0.86, 0.86, 0.84))


# ================================================================== Ecce Homo arch
ECCE_ARCH = (549.62, 402.22)           # OSM node 2710817408 (historic=city_gate, "Ecce Homo Arch")


def ecce_homo(mbs, bd, gen, place, lod=False):
    """Ecce Homo basilica (w744676490) and the Roman arch spanning the Via Dolorosa beside it
    (photos ecce_01/02/07/08): round arch springing at ~3.8 m, crown ~6 m, a block with a window
    above; the street stays open underneath.  Basilica: plain block, oculus on the street front,
    small dome."""
    sol, deco = solid_of(mbs)
    ring = [tuple(p) for p in bd["ring"]]
    col = (1.0, 0.95, 0.86)
    i = find_edge(ring, (539.0, 401.4), (0.97, 0.25), tol=5)
    zg = (bd.get("edge_ground") or [bd["ground"]] * len(ring))[i] if i is not None else bd["ground"]
    Z = Zones(bd, gen)
    Z.add("all", big_box(ring), bd["top"], "ashlar", col, roof="lime")
    if i is not None and not lod:
        a, b = ring[i], ring[(i + 1) % len(ring)]
        L = math.dist(a, b)
        Z.special(a, b, edge_hook(lambda z0, z1: [hole(circle(L - 6.4, zg + 6.6, 1.1, 14), 0.4, "glass"),
                                                  win(L - 10.5, 1.2, zg, zg + 2.6, "round", "door_wood", 0.3,
                                                      floor=True, frame=0.15)], gen=gen))
    Z.build(sol, lod)
    if not lod:
        parapet(sol, ring, bd["top"], 0.7, 0.3, "ashlar", col)
    cdm = centroid(ring)
    if lod:
        dome(sol, cdm.x, cdm.y, bd["top"], 2.6, "lead", rise=0.9, seg=8, rings=2)
    else:
        drum(sol, cdm.x, cdm.y, 2.4, bd["top"] - 0.02, bd["top"] + 1.4, 8, "ashlar", col, rot=math.pi / 8)
        ztop = dome(sol, cdm.x, cdm.y, bd["top"] + 1.4, 2.6, "lead", rise=0.95, rings=5, ribs=12, col=(0.85, 0.88, 0.92),
                    rib_col=(1.1, 1.1, 1.1))
        cross(deco, (cdm.x, cdm.y), ztop - 0.05, 1.2, gold(deco), gold_col(deco))
    # --- the arch across the street.  Frames: ef = east face (u from the south pier to the
    # basilica wall, outward normal = street direction), ew = west face (u from the north).
    if i is not None:
        a, b = v2(ring[i]), v2(ring[(i + 1) % len(ring)])
        ts = (b - a).normalized()                                    # street direction (east)
        n_ = Vector((-ts.y, ts.x))                                   # towards the basilica (north)
        node = v2(ECCE_ARCH)
        north = node + n_ * ((a - node).dot(n_) - 0.15)               # pier face 15 cm proud of the basilica wall
        span, T = 4.2, 2.6
        south = north - n_ * span
        ef = Edge(tuple(south + ts * T / 2), tuple(south + ts * T / 2 + n_))
        ew = Edge(tuple(north - ts * T / 2), tuple(north - ts * T / 2 - n_))
        zb, zs, zt = zg - 0.5, zg + 3.8, zg + 9.6
        acol = (0.98, 0.93, 0.84)
        A = arch_ol(0.0, span, zb, zs, "round", seg=12)
        for E, (u0, u1) in ((ef, (-1.2, span + 1.0)), (ew, (-1.0, span + 1.2))):
            W_ = hole(rect(span / 2 - 0.45, span / 2 + 0.45, zg + 7.0, zg + 8.4), 0.3, VOID, grille=True)
            face(sol, E, u_band(rect(u0, u1, zb, zt), A), "ashlar", 0.0, [] if lod else [W_["ol"]], acol)
            if not lod:
                build_hole(sol, E, W_, "ashlar", acol, gen)
                cornice(sol, E, u0, u1, zt - 0.35, 0.35, 0.18)
                frame(sol, E, arch_ol(0.0, span, zs - 0.01, zs, "round", seg=12), 0.35, 0.0, 0.1)
        tunnel(sol, ef, A, 0.0, -T, "ashlar", floor=True, col=acol)
        P = ef.P
        sol.poly([P(-1.2, zt, 0), P(span + 1.0, zt, 0), P(span + 1.0, zt, -T), P(-1.2, zt, -T)], "ashlar", UP, col=acol)
        for u, sg in ((-1.2, -1), (span + 1.0, 1)):                   # block ends (inside the neighbours)
            sol.poly([P(u, zb, 0), P(u, zb, -T), P(u, zt, -T), P(u, zt, 0)], "ashlar", Vector((*(n_ * sg), 0)), col=acol)


# ================================================================== smaller churches and synagogues
def simple_church(h, rise=0.0, kind="pointed", hip=False, domes=(), dome_mat="lead", col=(1.02, 0.98, 0.9),
                  win_w=1.0, win_h=3.0, sp=3.6, roof_mat="roof_tiles", parapet_h=0.0, cross_=True, obb_ring=None):
    """Builder for a modest church / synagogue: walls with a row of arched windows, a pitched roof
    over the footprint's oriented box (rise > 0) or a flat roof with a parapet, optional domes
    [(x, y, r, drum_h)] standing on the roof."""
    def fn(mbs, bd, gen, place, lod=False):
        sol, deco = solid_of(mbs)
        g = bd["ground"]
        ze = g + h

        def style(L, zg, z_top):
            zb = max(zg + 2.2, ze - win_h - 2.2)
            return win_row(L, zb, zb + win_h, sp=sp, w=win_w, kind=kind, back="glass", margin=1.4, frame=0.12)
        Z = StyledZones(bd, gen, style)
        ring = [tuple(p) for p in bd["ring"]]
        Z.add("all", big_box(ring), ze, "ashlar", col, roof=None if rise > 0 else "lime")
        Z.build(sol, lod)
        if rise > 0:
            c, t, L, W = obb(obb_ring or ring)
            gable_roof(sol, c, t, L, W, ze, rise, mat=roof_mat, end_col=col, hip=hip, over=0.0 if lod else 0.3)
            cap(sol, ring, ze - 0.02, "lime")                          # ceiling under eaves where the box is short
        elif parapet_h and not lod:
            parapet(sol, ring, ze, parapet_h, 0.3, "ashlar", col)
        for x, y, r, dh in domes:
            zd = ze + (rise if rise > 0 else 0.0)
            if lod:
                mk.cylinder(sol, x, y, zd - 0.2, zd + dh, r, "ashlar", seg=8, cap=False, col=col)
                dome(sol, x, y, zd + dh, r * 1.05, dome_mat, rise=0.9, seg=8, rings=2)
                continue
            drum(sol, x, y, r, zd - 0.2, zd + dh, 12 if r > 1.5 else 8, "ashlar", col,
                 win=(min(0.7, r * 0.4), zd + 0.25, zd + dh - 0.25, "round", 0.25, "glass") if dh > 1.0 else None,
                 gen=gen, every=2)
            zt = dome(sol, x, y, zd + dh, r * 1.05, dome_mat, rise=0.92, seg=16, rings=5,
                      col=(1.08, 1.06, 1.0) if dome_mat == "lime" else (0.85, 0.88, 0.92))
            if cross_:
                cross(deco, (x, y), zt - 0.05, 1.0 + r * 0.3, gold(deco), gold_col(deco))
    return fn


def austrian_hospice(mbs, bd, gen, place, lod=False):
    """Austrian Hospice of the Holy Family (w52890125, 1856-63, third storey 1931, roof terrace 1932-33):
    a palace in the manner of Vienna's Ringstrasse set back behind its compound wall and garden. Pale
    dressed ashlar, three storeys on a regular grid: round-arched windows on the ground floor, framed
    tall windows above, a string course over the ground floor and a main cornice under the roof
    terrace's parapet, where the Austrian and Vatican flags fly (the generic house builder gave it
    random doors on the upper floors, AC boxes and lime domes)."""
    sol, deco = solid_of(mbs)
    # floors from the garden terrace (the lowest ground round it; the record's ground is the median and on
    # the uphill north side, which put the string course storeys up)
    g = min(bd.get("edge_ground") or [bd["ground"]])
    col = (1.06, 1.01, 0.91)
    z1, z2, ze = g + 4.6, g + 8.9, g + 13.4               # floor levels and the eaves

    def style(L, zg, z_top):
        zg = g
        hs = win_row(L, zg + 1.3, zg + 3.8, sp=3.1, w=1.15, kind="round", back="glass", margin=1.7, frame=0.14)
        hs += win_row(L, z1 + 1.0, z1 + 3.3, sp=3.1, w=1.05, kind="round", back="glass", grille=False, margin=1.7,
                      frame=0.16)
        # the top storey (1931): an arcade of paired round arches, open, as it shows over the compound wall
        n = int((L - 3.4) / 3.6)
        for k in range(n):
            uc = 1.7 + 3.6 * (k + 0.5) + (L - 3.4 - 3.6 * n) / 2
            for du in (-0.62, 0.62):
                hs.append(win(uc + du, 1.0, z2 + 0.9, z2 + 3.4, "round", VOID, 0.6, frame=0.1))
        return hs
    Z = StyledZones(bd, gen, style)
    exposed = list(Z.exposed)
    Z.exposed = [True] * len(Z.ring)            # it stands storeys above the houses against it: windows all round
    ring = [tuple(p) for p in bd["ring"]]
    if area2(ring) < 0:
        ring.reverse()
        exposed = exposed[::-1][1:] + exposed[::-1][:1]
    Z.add("all", big_box(ring), ze, "ashlar", col, roof="lime")
    Z.build(sol, lod)
    if lod:
        return
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        if math.dist(a, b) < 1.0:
            continue
        e = Edge(a, b)
        if i < len(exposed) and exposed[i]:
            cornice(sol, e, 0.0, e.L, z1 - 0.3, 0.3, 0.16, ends=False)        # string course (free walls)
        cornice(sol, e, 0.0, e.L, ze - 0.55, 0.55, 0.42, ends=False)          # main cornice, all round
    parapet(sol, ring, ze, 1.05, 0.3, "ashlar", col)                       # the roof terrace's parapet
    c = centroid(ring)
    for k, (dx, cols) in enumerate(((-2.0, ((0.75, 0.06, 0.08), (1.0, 1.0, 1.0), (0.75, 0.06, 0.08))),
                                    (2.0, ((1.0, 0.82, 0.1), (1.0, 1.0, 1.0))))):
        x, y = c[0] + dx, c[1]
        mk.tube(deco, [(x, y, ze), (x, y, ze + 6.5)], 0.04, "metal_grey", sides=6)
        fw, fh = 1.8, 1.2
        nb = len(cols)
        for j, cl in enumerate(cols):                                     # stripes (horizontal / vertical)
            if k == 0:
                q = [(x, y, ze + 6.4 - fh * (j + 1) / nb), (x + fw, y, ze + 6.4 - fh * (j + 1) / nb),
                     (x + fw, y, ze + 6.4 - fh * j / nb), (x, y, ze + 6.4 - fh * j / nb)]
            else:
                q = [(x + fw * j / nb, y, ze + 6.4 - fh), (x + fw * (j + 1) / nb, y, ze + 6.4 - fh),
                     (x + fw * (j + 1) / nb, y, ze + 6.4), (x + fw * j / nb, y, ze + 6.4)]
            deco.poly(q, "plastic", Vector((0, -1, 0)), col=cl)
            deco.poly(q[::-1], "plastic", Vector((0, 1, 0)), col=cl)


def hospice_gate(mbs, bd, gen, place, lod=False):
    """Gatehouse of the Austrian Hospice (w375040921, corner of the Via Dolorosa and Al-Wad; Street View):
    one storey of weathered ashlar, its top level with the compound's garden terrace. On the Via Dolorosa a
    round-arched double wooden door up four steps between two round-arched barred windows, a string course
    and a cornice; a low parapet with an iron railing round the roof terrace."""
    sol, deco = solid_of(mbs)
    ring = [tuple(p) for p in bd["ring"]]
    eg = bd.get("edge_ground") or [bd["ground"]] * len(ring)
    i = find_edge(ring, (425.9, 380.45), (-0.97, 0.24), tol=3)
    g = eg[i] if i is not None else min(eg)
    col = (0.95, 0.93, 0.89)
    zt = g + 5.0
    Z = Zones(bd, gen)
    Z.add("all", big_box(ring), zt, "ashlar", col, roof="paving", windows=False)
    if i is not None and not lod:
        a, b = ring[i], ring[(i + 1) % len(ring)]
        L = math.dist(a, b)
        uc = L / 2

        def holes(z0, z1):
            return [win(uc, 1.5, g + 0.75, g + 3.75, "round", "door_wood", 0.35, floor=True, frame=0.18),
                    win(uc - 2.9, 0.95, g + 1.6, g + 3.4, "round", VOID, 0.3, grille=True, frame=0.15),
                    win(uc + 2.9, 0.95, g + 1.6, g + 3.4, "round", VOID, 0.3, grille=True, frame=0.15)]
        Z.special(a, b, edge_hook(holes, gen=gen))
    Z.build(sol, lod)
    if lod:
        return
    if i is not None:
        e = Edge(ring[i], ring[(i + 1) % len(ring)])
        steps_run(sol, Edge(tuple(e.P(e.L / 2 - 1.3, 0, 1.4)[:2]), tuple(e.P(e.L / 2 - 1.3, 0, 0.0)[:2])),
                  0.0, 1.4, -1.3, 1.3, g, g + 0.75, 4, g - 0.4)            # four steps up to the door
        cornice(sol, e, 0.0, e.L, g + 4.1, 0.25, 0.14, ends=False)
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        if math.dist(a, b) > 1.0:
            cornice(sol, Edge(a, b), 0.0, math.dist(a, b), zt - 0.35, 0.35, 0.2, ends=False)
    parapet(sol, ring, zt, 0.45, 0.25, "ashlar", col)
    rail(deco, mk.inset_ring(ring, 0.12), zt + 0.45, h=0.9, post=1.6)


def sephardic(mbs, bd, gen, place, lod=False):
    """Four Sephardic Synagogues (w29265134): sunk below the street, so only low walls show; small
    white domes over the four halls (OSM nodes 4905159136-39)."""
    sol = mbs["solid"]
    g = bd["ground"]
    col = (1.04, 1.0, 0.92)
    Z = StyledZones(bd, gen, lambda L, zg, z_top: win_row(L, zg + 2.4, zg + 4.0, sp=3.2, w=0.9, kind="round",
                                                           back="glass", margin=1.2))
    ring = [tuple(p) for p in bd["ring"]]
    z1 = g + 6.0
    Z.add("all", big_box(ring), z1, "ashlar", col, roof="lime")
    Z.build(sol, lod)
    if not lod:
        parapet(sol, ring, z1, 0.6, 0.3, "ashlar", col)
    for (x, y), r in (((387.35, -209.08), 2.6), ((369.5, -216.12), 3.2), ((374.17, -225.26), 3.4), ((384.46, -219.45), 2.4)):
        if mk.point_in((x, y), ring):
            dome(sol, x, y, z1 - 0.05, r, "lime", rise=0.55, seg=8 if lod else 16, rings=2 if lod else 4,
                 col=(1.08, 1.06, 1.0))


def co_cathedral(mbs, bd, gen, place, lod=False):
    """Co-Cathedral of the Most Holy Name of Jesus (Latin Patriarchate, w1392261827): Gothic Latin
    cross set at 45 degrees; pointed windows, two crossing gable roofs (arms from the OSM ring)."""
    sol = mbs["solid"]
    g = bd["ground"]
    col = (1.04, 1.0, 0.92)
    ze = g + 11.5
    Z = StyledZones(bd, gen, lambda L, zg, z_top: win_row(L, ze - 6.4, ze - 2.2, sp=3.4, w=1.2, kind="pointed",
                                                           back="glass", margin=1.4, frame=0.12))
    ring = [tuple(p) for p in bd["ring"]]
    Z.add("all", big_box(ring), ze, "ashlar", col, roof="lime")
    Z.build(sol, lod)
    ov = 0.0 if lod else 0.25
    gable_roof(sol, (-50.78, 118.08), (0.695, 0.719), 29.1, 11.6, ze, 4.4, end_col=col, over=ov)
    gable_roof(sol, (-50.08, 118.73), (-0.754, 0.656), 21.4, 10.6, ze, 4.0, end_col=col, over=ov, z_eps=0.015)


CONDEMNATION_DOMES = [(586.0, 416.6, 2.3, 1.6), (581.5, 413.4, 1.1, 0.8), (590.5, 414.3, 1.1, 0.8),
                      (580.6, 419.5, 1.1, 0.8), (589.6, 420.5, 1.1, 0.8)]


# ================================================================== registry
LANDMARKS = {
    "w1022672085": holy_sepulchre,
    "w29268902": redeemer,
    "w290821793": mosque_omar,
    KHANQAH_MIN: khanqah_minaret,
    "w45081545": hurva,
    "w106249447": st_saviour_church,
    "r1515591": st_saviour_monastery,
    "w195100862": tiferet,
    "w265410575": st_james,
    "w126864879": st_anne,
    "w744676490": ecce_homo,
    "w52890125": austrian_hospice,
    "w375040921": hospice_gate,
    "w1394857844": host_minaret((412.91, 379.34)),              # Via Dolorosa minaret, OSM node 5921367466
    "w126755060": simple_church(8.5, rise=3.4, kind="pointed", win_w=1.1, win_h=3.2,           # Christ Church (1849)
                                obb_ring=[(153.4, -72.5), (167.4, -72.0), (168.5, -62.4), (153.6, -61.7)]),
    "w1392261827": co_cathedral,
    "w612045244": simple_church(12.5, kind="flat", win_w=1.2, win_h=2.6, parapet_h=0.9, sp=3.0,
                                col=(1.05, 1.0, 0.9)),                                          # Alexander Nevsky
    "w29265134": sephardic,
    "w744674450": simple_church(7.5, rise=2.6, kind="pointed", win_w=1.0, win_h=2.4),           # Flagellation
    "w744674226": simple_church(8.0, kind="round", win_w=1.0, win_h=2.4, parapet_h=0.6,
                                domes=CONDEMNATION_DOMES, dome_mat="lime"),                     # Condemnation
}
