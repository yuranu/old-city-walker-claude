"""Geometry helpers for the city build (run inside Blender).

MeshBuilder accumulates flat-shaded polygons with a material per face, UVs and a per-face
vertex colour (exported as glTF COLOR_0 and multiplied onto the material colour in three.js).
UVs default to world-space box projection (metres / material tile size) so stone courses line
up across walls; pass uv=[...] for atlas-mapped faces (signs, doors, decals, foliage cards).

API contract (used by build_city.py, props.py, fortifications.py):
  mb = MeshBuilder(tiles)                       tiles: material name -> metres per texture repeat
  mb.poly(pts3d, mat, normal_hint=None, uv=None, col=None)
  mb.tris(pts3d, tris, mat, normal_hint, col=None, uvfn=None)
  mb.quad_strip(lo, hi, mat, normal_fn, col=None)
  box(mb, c, t, s, lt, ls, z0, z1, mat, top=True, bottom=False, col=None)
  cylinder(mb, cx, cy, z0, z1, r, mat, seg=16, cap=True, col=None, r1=None)
  dome(mb, cx, cy, z, r, mat, drum=0.5, seg=16, rings=6, col=None)
  prism(mb, ring, z0, z1, mat, top_mat=None, bottom=False, col=None)
  card(mb, centre, right, up, w, h, mat, uv_rect, col=None, double=False)   foliage / sign quads
  tube(mb, points, r, mat, sides=4, col=None)                              cables, pipes, rails
  atlas_rect(grid, cell, inset_px=3, size_px=2048) -> (u0, v0, u1, v1)       UV rect of an atlas cell
  mb.to_object(name, materials, collection, merge=True) / mb.to_mesh(name, materials)
"""
import math

import bmesh
import bpy
from mathutils import Vector, geometry

UP = Vector((0, 0, 1))
WHITE = (1.0, 1.0, 1.0)


class MeshBuilder:
    def __init__(self, tile_sizes):
        self.verts, self.faces, self.uvs, self.mats, self.cols = [], [], [], [], []
        self.mat_names = []
        self.tile = tile_sizes

    def _mat(self, name):
        if name not in self.mat_names:
            self.mat_names.append(name)
        return self.mat_names.index(name)

    def poly(self, pts, mat, normal_hint=None, uv=None, col=None):
        """Add one planar polygon (3D points). Flips it to agree with normal_hint."""
        pts = [Vector(p) for p in pts]
        if len(pts) < 3:
            return
        n = geometry.normal(pts)
        if n.length < 1e-9:
            return
        if normal_hint is not None and n.dot(Vector(normal_hint)) < 0:
            pts.reverse()
            n = -n
            if uv is not None:
                uv = list(uv)[::-1]
        if uv is None:
            t = self.tile.get(mat, 2.0)
            if abs(n.z) > 0.7:
                uv = [(p.x / t, p.y / t) for p in pts]
            else:
                h = Vector((-n.y, n.x, 0))
                h = h.normalized() if h.length > 1e-6 else Vector((1, 0, 0))
                uv = [(p.dot(h) / t, p.z / t) for p in pts]
        base = len(self.verts)
        self.verts.extend(pts)
        self.faces.append(list(range(base, base + len(pts))))
        self.uvs.append(list(uv))
        self.mats.append(self._mat(mat))
        self.cols.append(tuple(col) if col is not None else WHITE)

    def tris(self, pts, tris, mat, normal_hint, col=None, uvfn=None):
        for a, b, c in tris:
            tri = [pts[a], pts[b], pts[c]]
            self.poly(tri, mat, normal_hint, uv=[uvfn(p) for p in tri] if uvfn else None, col=col)

    def quad_strip(self, lo, hi, mat, normal_fn, col=None):
        for i in range(len(lo) - 1):
            q = [lo[i], lo[i + 1], hi[i + 1], hi[i]]
            self.poly(q, mat, normal_fn(q), col=col)

    def empty(self):
        return not self.faces

    def to_mesh(self, name, materials, merge=True):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in self.verts], [], self.faces)
        uvl = me.uv_layers.new(name="UVMap")
        ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
        uvd, cd = uvl.data, ca.data
        for f, uv, col in zip(me.polygons, self.uvs, self.cols):
            c4 = (col[0], col[1], col[2], 1.0)
            for k in range(f.loop_total):
                uvd[f.loop_start + k].uv = uv[k]
                cd[f.loop_start + k].color = c4
        me.color_attributes.active_color = ca
        me.color_attributes.render_color_index = 0
        for name_ in self.mat_names:
            me.materials.append(materials[name_])
        me.polygons.foreach_set("material_index", self.mats)
        if merge:                                   # weld coincident verts, keep hard edges
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
            bm.to_mesh(me)
            bm.free()
        me.validate()
        me.update()
        return me

    def to_object(self, name, materials, collection, merge=True):
        ob = bpy.data.objects.new(name, self.to_mesh(name, materials, merge))
        collection.objects.link(ob)
        return ob


# ---------------------------------------------------------------- 2D helpers
def ring_area(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def point_in(p, r):
    x, y = p
    c = False
    for i in range(len(r)):
        (x1, y1), (x2, y2) = r[i], r[(i + 1) % len(r)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def inset_ring(r, d):
    """Constant inward offset of a CCW ring with clamped mitres."""
    n = len(r)
    out = []
    for i in range(n):
        a, b, c = Vector(r[i - 1]), Vector(r[i]), Vector(r[(i + 1) % n])
        e1 = (b - a).normalized()
        e2 = (c - b).normalized()
        n1 = Vector((-e1.y, e1.x))
        n2 = Vector((-e2.y, e2.x))
        bis = n1 + n2
        if bis.length < 1e-6:
            out.append(tuple(b + n1 * d))
            continue
        bis.normalize()
        cosh = max(0.35, bis.dot(n1))
        out.append(tuple(b + bis * (d / cosh)))
    return out


def tess2d(rings):
    """Triangulate 2D rings (first outer, rest holes); returns (flat point list, tris)."""
    polys = [[(p[0], p[1], 0.0) for p in r] for r in rings]
    tris = geometry.tessellate_polygon(polys)
    flat = [p for r in rings for p in r]
    return flat, tris


def atlas_rect(grid, cell, inset_px=3, size_px=2048):
    """UV rectangle (u0, v0, u1, v1) of cell (col, row-from-top) in a grid x grid atlas."""
    g = grid[0] if isinstance(grid, (list, tuple)) else grid
    c, r = cell
    e = inset_px / size_px
    return (c / g + e, 1 - (r + 1) / g + e, (c + 1) / g - e, 1 - r / g - e)


# ---------------------------------------------------------------- openings
def opening_outline(u0, u1, v0, v1, arch, seg=8):
    """Outline (counter-clockwise in u,v) of a rectangular / round / pointed / segmental opening."""
    w = u1 - u0
    if arch == "round" and v1 - v0 > w / 2:
        vs = v1 - w / 2
        pts = [(u0, v0), (u1, v0), (u1, vs)]
        for k in range(1, seg):
            a = math.pi * k / seg
            pts.append(((u0 + u1) / 2 + math.cos(a) * w / 2, vs + math.sin(a) * w / 2))
        pts.append((u0, vs))
        return pts
    if arch == "pointed" and v1 - v0 > 0.78 * w:
        R = 0.85 * w
        ha = w * math.sqrt(0.85 ** 2 - 0.35 ** 2)
        vs = v1 - ha
        amax = math.acos((0.5 * w - R) / R)
        pts = [(u0, v0), (u1, v0), (u1, vs)]
        half = seg // 2
        for k in range(1, half + 1):
            a = (math.pi - amax) * k / half
            pts.append((u1 - R + math.cos(a) * R, vs + math.sin(a) * R))
        for k in range(1, half):
            a = amax + (math.pi - amax) * k / half
            pts.append((u0 + R + math.cos(a) * R, vs + math.sin(a) * R))
        pts.append((u0, vs))
        return pts
    if arch == "segment" and v1 - v0 > 0.2 * w:
        rise = 0.18 * w
        vs = v1 - rise
        R = (w * w / 4 + rise * rise) / (2 * rise)
        cy = v1 - R
        a0 = math.asin((w / 2) / R)
        pts = [(u0, v0), (u1, v0), (u1, vs)]
        for k in range(seg - 1, 0, -1):            # arc from the right springer to the left one
            a = -a0 + 2 * a0 * k / seg
            pts.append(((u0 + u1) / 2 + math.sin(a) * R, cy + math.cos(a) * R))
        pts.append((u0, vs))
        return pts
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def thick_wall(mb, pts, z0, z1, thick, mat, merlons=None, outside="right", col=None):
    """Wall slab along a 2D polyline (centred), with optional merlons on the outer edge."""
    for i in range(len(pts) - 1):
        a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0))
        t = (b - a).normalized()
        nr = Vector((t.y, -t.x, 0))
        h = thick / 2
        corners = [a + nr * h, b + nr * h, b - nr * h, a - nr * h]
        lo = [c + Vector((0, 0, z0)) for c in corners]
        hi = [c + Vector((0, 0, z1)) for c in corners]
        for k in range(4):
            q = [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]]
            mid = (q[0] + q[2]) / 2
            ctr = (a + b) / 2 + Vector((0, 0, mid.z))
            mb.poly(q, mat, mid - ctr, col=col)
        mb.poly(hi, mat, UP, col=col)
        if merlons:
            side = nr if outside == "right" else -nr
            mw, gap, mh, md = merlons
            L = (b - a).length
            u = gap / 2
            while u + mw <= L - gap / 2:
                p0 = a + t * u + side * (h - md / 2)
                box(mb, p0 + t * (mw / 2), t, side, mw, md, z1, z1 + mh, mat, col=col)
                u += mw + gap


def box(mb, c, t, s, lt, ls, z0, z1, mat, top=True, bottom=False, col=None, back=True):
    """Oriented box: centre c (z ignored), unit axes t (length lt) and s (length ls).
    back=False drops the face on the -s side (boxes mounted on a wall whose normal is s)."""
    c = Vector((c[0], c[1], 0))
    t = Vector((t[0], t[1], 0))
    s = Vector((s[0], s[1], 0))
    pts = [c - t * lt / 2 - s * ls / 2, c + t * lt / 2 - s * ls / 2,
           c + t * lt / 2 + s * ls / 2, c - t * lt / 2 + s * ls / 2]
    lo = [p + Vector((0, 0, z0)) for p in pts]
    hi = [p + Vector((0, 0, z1)) for p in pts]
    cz = c + Vector((0, 0, (z0 + z1) / 2))
    for k in range(4):
        if k == 0 and not back:
            continue
        q = [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]]
        mb.poly(q, mat, (q[0] + q[2]) / 2 - cz, col=col)
    if top:
        mb.poly(hi, mat, UP, col=col)
    if bottom:
        mb.poly(lo, mat, -UP, col=col)


def prism(mb, ring, z0, z1, mat, top_mat=None, bottom=False, col=None):
    """Vertical extrusion of a CCW ring (outer walls + cap)."""
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        q = [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]
        mb.poly(q, mat, Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=col)
    fl, ft = tess2d([ring])
    mb.tris([(p[0], p[1], z1) for p in fl], ft, top_mat or mat, UP, col=col)
    if bottom:
        mb.tris([(p[0], p[1], z0) for p in fl], ft, top_mat or mat, -UP, col=col)


def dome(mb, cx, cy, z, r, mat, drum=0.5, seg=16, rings=6, col=None):
    """Drum + hemisphere."""
    pts_lo = [Vector((cx + math.cos(2 * math.pi * k / seg) * r, cy + math.sin(2 * math.pi * k / seg) * r, z))
              for k in range(seg + 1)]
    pts_hi = [p + Vector((0, 0, drum)) for p in pts_lo]
    centre = Vector((cx, cy, z))
    mb.quad_strip(pts_lo, pts_hi, mat, lambda q: (q[0] + q[2]) / 2 - centre, col=col)
    prev = pts_hi
    zc = z + drum
    for j in range(1, rings + 1):
        phi = (math.pi / 2) * j / rings
        rr, hz = r * math.cos(phi), r * math.sin(phi)
        if j == rings:
            apex = Vector((cx, cy, zc + r))
            for k in range(seg):
                mb.poly([prev[k], prev[k + 1], apex], mat, (prev[k] + apex) / 2 - Vector((cx, cy, zc)), col=col)
            break
        cur = [Vector((cx + math.cos(2 * math.pi * k / seg) * rr, cy + math.sin(2 * math.pi * k / seg) * rr, zc + hz))
               for k in range(seg + 1)]
        mb.quad_strip(prev, cur, mat, lambda q: (q[0] + q[2]) / 2 - Vector((cx, cy, zc)), col=col)
        prev = cur


def cylinder(mb, cx, cy, z0, z1, r, mat, seg=16, cap=True, col=None, r1=None):
    """Vertical (optionally tapered: r at z0, r1 at z1) cylinder."""
    r1 = r if r1 is None else r1
    lo = [Vector((cx + math.cos(2 * math.pi * k / seg) * r, cy + math.sin(2 * math.pi * k / seg) * r, z0))
          for k in range(seg + 1)]
    hi = [Vector((cx + math.cos(2 * math.pi * k / seg) * r1, cy + math.sin(2 * math.pi * k / seg) * r1, z1))
          for k in range(seg + 1)]
    centre = Vector((cx, cy, z0))
    mb.quad_strip(lo, hi, mat, lambda q: Vector(((q[0] + q[2]) / 2 - centre).xy[:] + (0,)), col=col)
    if cap:
        mb.poly(hi[:-1], mat, UP, col=col)


def card(mb, centre, right, up, w, h, mat, uv_rect, col=None, double=False):
    """Textured quad (foliage cards, signs, decals): centre-bottom at `centre`."""
    c, r, u = Vector(centre), Vector(right).normalized(), Vector(up).normalized()
    q = [c - r * w / 2, c + r * w / 2, c + r * w / 2 + u * h, c - r * w / 2 + u * h]
    u0, v0, u1, v1 = uv_rect
    uv = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    n = r.cross(u)
    mb.poly(q, mat, n, uv=uv, col=col)
    if double:
        mb.poly(q[::-1], mat, -n, uv=uv[::-1], col=col)


def tube(mb, points, r, mat, sides=4, col=None):
    """Thin tube along a 3D polyline (cables, pipes, railings)."""
    pts = [Vector(p) for p in points]
    if len(pts) < 2:
        return
    rings = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        x = d.cross(a).normalized()
        y = d.cross(x).normalized()
        rings.append([p + (x * math.cos(2 * math.pi * k / sides) + y * math.sin(2 * math.pi * k / sides)) * r
                      for k in range(sides + 1)])
    for i in range(len(rings) - 1):
        ci = (pts[i] + pts[i + 1]) / 2
        for k in range(sides):
            q = [rings[i][k], rings[i][k + 1], rings[i + 1][k + 1], rings[i + 1][k]]
            mb.poly(q, mat, (q[0] + q[2]) / 2 - ci, uv=[(0, 0), (1, 0), (1, 1), (0, 1)], col=col)
