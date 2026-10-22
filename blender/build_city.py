"""Build the Jaffa Gate scene from data/scene_spec.json and export it for the game.

    blender -b --factory-startup -P blender/build_city.py -- \
        [--out game/public/city.glb] [--blend build/city.blend] [--preview renders] [--no-export]

Local frame: +X east, +Y north, Z up, metres; origin = Jaffa Gate (OSM node 561157424).
Objects carry a custom property nocol=1 when the game must not collide with them (exported as
glTF node extras). Props are linked duplicates of library meshes (blender/props.py).
"""
import argparse
import json
import math
import os
import sys
import zlib
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facade_build as fb  # noqa: E402
import fortifications  # noqa: E402
import landmarks  # noqa: E402
import materials  # noqa: E402
import meshkit as mk  # noqa: E402

try:
    import props as proplib  # noqa: E402
except Exception as e:  # noqa: BLE001
    print("props library unavailable:", e)
    proplib = None

ROOT = HERE.parent
UP = Vector((0, 0, 1))


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--spec", default=str(ROOT / "data/scene_spec.json"))
    p.add_argument("--out", default=str(ROOT / "game/public/city.glb"))
    p.add_argument("--blend", default=str(ROOT / "build/city.blend"))
    p.add_argument("--preview", default=str(ROOT / "renders"))
    p.add_argument("--no-export", action="store_true")
    p.add_argument("--part", default=None, help="base | <sector id>; default: legacy single scene (base + s00)")
    return p.parse_args(argv)


# ---------------------------------------------------------------- buildings
def obb(ring):
    best = None
    for i in range(len(ring)):
        a, b = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        t = b - a
        if t.length < 0.5:
            continue
        t.normalize()
        s = Vector((-t.y, t.x))
        us = [Vector(p).dot(t) for p in ring]
        vs = [Vector(p).dot(s) for p in ring]
        A = (max(us) - min(us)) * (max(vs) - min(vs))
        if best is None or A < best[0]:
            c = t * (max(us) + min(us)) / 2 + s * (max(vs) + min(vs)) / 2
            lu, lv = max(us) - min(us), max(vs) - min(vs)
            best = (A, c, t, s, lu, lv) if lu >= lv else (A, c, s, t, lv, lu)
    return best[1:]


def roof_tone(bd):
    """Weathered roof deck: grey lime/concrete, darker and more varied than the walls; the domes
    (vernacular_domes) stay whiter, which is what makes them read from above."""
    h = (zlib.crc32(("roof" + bd["id"]).encode()) % 1000) / 1000.0
    g = 0.66 + 0.24 * h
    warm = 0.03 * ((h * 7) % 1.0 - 0.5)
    return (g * (1 + warm), g, g * (1 - warm))


def roof_flat(mb, bd, wall_mat, col, gen=None):
    ring = [tuple(p) for p in bd["ring"]]
    top = bd["top"]
    rz = top - 0.9
    if bd["style"].get("parapet") == "balustrade" and bd["tier"] == "hero" and gen:
        return roof_balustrade(mb, bd, wall_mat, col, gen)
    roofs = bd.get("roof") or []
    if not roofs:
        fl, ft = mk.tess2d([ring])
        mb.tris([(p[0], p[1], top) for p in fl], ft, "lime", UP, col=roof_tone(bd))
        return []
    holes = [r["ext"] for r in roofs]
    try:
        fl, ft = mk.tess2d([ring] + holes)
        mb.tris([(p[0], p[1], top) for p in fl], ft, wall_mat, UP, col=col)
    except Exception:  # noqa: BLE001
        pass
    for r in roofs:
        ext = r["ext"]
        for i in range(len(ext)):
            a, b = ext[i], ext[(i + 1) % len(ext)]
            mb.poly([(a[0], a[1], rz), (b[0], b[1], rz), (b[0], b[1], top), (a[0], a[1], top)], wall_mat,
                    Vector((-(b[1] - a[1]), b[0] - a[0], 0)), col=col)
        fl, ft = mk.tess2d([ext] + r["holes"])
        mb.tris([(p[0], p[1], rz) for p in fl], ft, "lime", UP, col=roof_tone(bd))
    return roofs


def roof_balustrade(mb, bd, wall_mat, col, gen):
    """Stone balustrade parapet (hotels on the square): plinth, balusters (cut-out card), coping."""
    ring = [tuple(p) for p in bd["ring"]]
    top = bd["top"]
    rz = top - 0.9
    plinth = rz + 0.18
    roofs = bd.get("roof") or []
    holes = [r["ext"] for r in roofs]
    try:
        fl, ft = mk.tess2d([ring] + holes)
        mb.tris([(p[0], p[1], plinth) for p in fl], ft, wall_mat, UP, col=col)
    except Exception:  # noqa: BLE001
        pass
    rect = mk.atlas_rect(gen["cutout"]["grid"], gen["cutout"]["cells"]["balustrade"])
    kept = [i for i in range(len(ring)) if math.dist(ring[i], ring[(i + 1) % len(ring)]) >= 0.3]
    for ki, i in enumerate(kept):
        a, b = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        t = b - a
        L = t.length
        t.normalize()
        nin = Vector((-t.y, t.x))
        c = (a + b) / 2 + nin * 0.16
        k = max(1, round(L / 1.2))
        for j in range(k):
            p0, p1 = a + t * (L * j / k), a + t * (L * (j + 1) / k)
            mk.card(mb, ((p0 + p1) / 2 + nin * 0.16).to_3d() + UP * plinth, t.to_3d(), UP, (p1 - p0).length,
                    top - 0.14 - plinth, "cut", rect, col=STONE, double=True)
        # copings overlap at the corners: neighbours never share a height (> audit tolerance, 4 mm),
        # the last and the first edge of an odd ring included
        dz = 0.006 * (2 if (len(kept) % 2 and ki == len(kept) - 1) else ki % 2)
        mk.box(mb, c, t, nin, L, 0.34, top - 0.14 + dz, top + dz, "dressed", bottom=True, col=STONE)
        n_posts = max(1, round(L / 3.0))
        for j in range(n_posts + 1):
            p = a + t * (L * j / n_posts) + nin * 0.16
            mk.box(mb, p, t, nin, 0.3, 0.3, plinth, top - 0.14, "dressed", col=STONE)
    for r in roofs:
        ext = r["ext"]
        for i in range(len(ext)):
            a, b = ext[i], ext[(i + 1) % len(ext)]
            mb.poly([(a[0], a[1], rz), (b[0], b[1], rz), (b[0], b[1], plinth), (a[0], a[1], plinth)], wall_mat,
                    Vector((-(b[1] - a[1]), b[0] - a[0], 0)), col=col)
        fl, ft = mk.tess2d([ext] + r["holes"])
        mb.tris([(p[0], p[1], rz) for p in fl], ft, "lime", UP, col=roof_tone(bd))
    return roofs


STONE = (1.0, 1.0, 1.0)


def roof_hipped(mb, ring, top):
    c, t, s, ll, ls = obb(ring)
    ov = 0.35
    ll, ls = ll + 2 * ov, ls + 2 * ov
    hr = ls / 2 * 0.5
    c3 = Vector((c.x, c.y, top))
    t3, s3 = Vector((t.x, t.y, 0)), Vector((s.x, s.y, 0))
    cs = [c3 - t3 * ll / 2 - s3 * ls / 2, c3 + t3 * ll / 2 - s3 * ls / 2,
          c3 + t3 * ll / 2 + s3 * ls / 2, c3 - t3 * ll / 2 + s3 * ls / 2]
    r0 = c3 - t3 * (ll / 2 - ls / 2) + UP * hr
    r1 = c3 + t3 * (ll / 2 - ls / 2) + UP * hr
    mb.poly([cs[0], cs[1], r1, r0], "roof_tiles", -s3 + UP)
    mb.poly([cs[2], cs[3], r0, r1], "roof_tiles", s3 + UP)
    mb.poly([cs[1], cs[2], r1], "roof_tiles", t3 + UP)
    mb.poly([cs[3], cs[0], r0], "roof_tiles", -t3 + UP)
    for k in range(4):                                     # eaves underside
        mb.poly([cs[k], cs[(k + 1) % 4], cs[(k + 1) % 4] - UP * 0.05, cs[k] - UP * 0.05], "roof_tiles",
                (cs[k] + cs[(k + 1) % 4]) / 2 - c3)
    fl, ft = mk.tess2d([ring])
    mb.tris([(p[0], p[1], top) for p in fl], ft, "lime", -UP)


def add_domes(mb, roofs, rz, count):
    for r in roofs[:1]:
        ext = r["ext"]
        c, t, s, ll, ls = obb(ext)
        rad = min(2.6, 0.24 * ls)
        if rad < 0.9:
            return
        spots = [c] if count == 1 else [c - t * ll / 4, c + t * ll / 4]
        for p in spots:
            if all(mk.point_in((p.x + math.cos(a) * rad * 1.1, p.y + math.sin(a) * rad * 1.1), ext)
                   for a in [k * math.pi / 4 for k in range(8)]):
                mk.dome(mb, p.x, p.y, rz, rad, "lime", drum=0.6)


def vernacular_domes(mb, bd, z, seg=12, rings=4, limit=None):
    """Field of shallow lime domes from the spec (pipeline/roofscape.py)."""
    for i, d in enumerate(bd.get("dome_list", [])[:limit]):
        g = 0.9 + 0.1 * ((i * 37 + len(bd["id"])) % 7) / 6
        mk.dome(mb, d["c"][0], d["c"][1], z - 0.05, d["r"], "lime", drum=d["drum"], seg=seg, rings=rings,
                rise=d["rise"], col=(g, g, g * 0.98))


def context_windows(mb, bd, gen):
    """Flat window cards on context buildings (positions from the spec): windows at distance for 2 tris."""
    ring = [tuple(p) for p in bd["ring"]]
    for wdw in bd.get("cwin", []):
        i = wdw["edge"]
        a, b = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        t = (b - a).normalized()
        n = Vector((t.y, -t.x))
        rect = mk.atlas_rect(gen["doors"]["grid"], gen["doors"]["cells"][wdw["cell"]])
        c = (a + t * wdw["u"] + n * 0.05).to_3d() + UP * wdw["z"]     # 5 cm: safe for depth precision far away
        mk.card(mb, c, t.to_3d(), UP, 1.0, 1.5, "doors", rect)


def build_building(mbs, bd, gen, signs, place):
    ring = [tuple(p) for p in bd["ring"]]
    st = bd["style"]
    wall = st["wall"]
    col = tuple(min(1.0, c / 1.06) for c in bd["tint"])
    mb = mbs["solid"]
    fac = {f["edge"]: f for f in bd.get("facades", [])}
    key = bd["id"]
    if bd["tier"] == "context":
        context_windows(mbs["deco"], bd, gen)
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        f = fac.get(i)
        z_top = bd["top"] - 0.72 if st.get("parapet") == "balustrade" and bd["tier"] == "hero" else bd["top"]
        fb.wall_panel(mb, a, b, bd["base"], z_top, f["openings"] if f else [], wall, col, gen, key + str(i))
        if f:
            fb.facade_extras(mbs, a, b, f, gen, signs, place, col)
    if st["roof"] == "hipped" and bd["tier"] != "context":
        roof_hipped(mb, ring, bd["top"])
        return
    roofs = roof_flat(mb, bd, wall, col, gen)
    rz = bd["top"] - 0.9
    for rm in bd.get("roof_rooms", []):
        rr = [tuple(p) for p in rm["ring"]]
        lens = [math.dist(rr[i], rr[(i + 1) % len(rr)]) for i in range(len(rr))]
        door_edge = lens.index(max(lens))
        for i in range(len(rr)):
            if i == door_edge:
                continue
            a, b = rr[i], rr[(i + 1) % len(rr)]
            fb.wall_panel(mb, a, b, rz, rz + rm["h"], [], "rubble" if wall == "rubble" else "ashlar", col, gen)
        if rm["roof"] == "tiles":
            roof_hipped(mb, rr, rz + rm["h"])
        else:
            fl, ft = mk.tess2d([rr])
            mb.tris([(p[0], p[1], rz + rm["h"]) for p in fl], ft, "lime", UP)
        i = door_edge                                       # a door on the longest side
        L = lens[i]
        fb.wall_panel(mb, rr[i], rr[(i + 1) % len(rr)], rz, rz + rm["h"],
                      [{"kind": "door", "u0": L / 2 - 0.45, "u1": L / 2 + 0.45, "v0": rz + 0.05, "v1": rz + 2.1,
                        "arch": None, "depth": 0.15, "lo": "door_green"}],
                      "rubble" if wall == "rubble" else "ashlar", col, gen)
    if st["domes"] and roofs:
        add_domes(mb, roofs, rz, st["domes"])
    vernacular_domes(mb, bd, rz)


# ---------------------------------------------------------------- ground
def build_ground(mbs, spec):
    mat_of = {"paving": "paving", "setts": "setts", "moat": "rubble", "grass": "grass", "kerb_band": "dressed"}
    for g in spec["ground"]:
        mb = mbs["ground"]
        mat = mat_of.get(g["mat"], "paving")
        col = (0.9, 0.88, 0.84) if g["mat"] == "kerb_band" else None
        for t in g["tris"]:
            mb.poly(t, mat, UP, col=col)
    for k in spec["kerbs"]:
        a, b = k["a"], k["b"]
        q = [(a[0], a[1], k["z0"] - 0.02), (b[0], b[1], k["z0"] - 0.02), (b[0], b[1], k["z1"]), (a[0], a[1], k["z1"])]
        n = Vector((b[1] - a[1], -(b[0] - a[0]), 0))
        mbs["ground"].poly(q, "dressed", n, col=(0.85, 0.83, 0.8))
    for s in spec["steps"]:
        ext = s["poly"]["ext"]
        try:
            fl, ft = mk.tess2d([ext] + s["poly"]["holes"])
        except Exception:  # noqa: BLE001
            continue
        tile = 4.0                                          # world-aligned like the ground around: one paving
        mbs["ground"].tris([(p[0], p[1], s["top"]) for p in fl], ft, "paving", UP,      # pattern, the risers read
                           uvfn=lambda p: (p[0] / tile, p[1] / tile))                   # as the steps
        ez = s.get("ez") or [s["top"]] * len(ext)
        for i in range(len(ext)):                 # sides: from below up to the tread or the street, whichever
            a, b = ext[i], ext[(i + 1) % len(ext)]                  # is higher, so no gap opens either way
            eo = s.get("eo") or [1] * len(ext)
            # (+2 cm where the street is higher: the ground's triangles sit up to a few cm above the street
            #  level sampled at the corners, and a slit of sky opened under their edge)
            up = lambda z_: z_ + 0.02 if z_ > s["top"] else s["top"]          # noqa: E731
            za, zb = (up(ez[i]), up(ez[(i + 1) % len(ext)])) if eo[i] else (s["top"], s["top"])
            q = [(a[0], a[1], s["bottom"]), (b[0], b[1], s["bottom"]), (b[0], b[1], zb), (a[0], a[1], za)]
            mbs["ground"].poly(q, "ashlar", Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=(0.82, 0.8, 0.76))


# ---------------------------------------------------------------- props
# extras.draw_dist (m) per prop type: the game hides a prop beyond it and keeps it out of the far
# copies and shadow casters (trees read from far, litter does not)
DRAW_DIST = {"tree_olive": 160, "tree_ficus": 160, "tree_young": 140, "palm": 150,
             "lamp_post": 110, "lamp_modern": 110, "lamp_modern_double": 110, "flagpole": 120, "banner_pole": 110,
             "cart": 90, "dumpster": 90, "bench": 80, "bench_stone": 80, "info_board": 80, "bin_slatted": 70,
             "bin_post": 70, "bollard": 60, "barrier_post": 60, "lamp_disc": 90,
             "water_heater": 90, "water_tank": 90, "sat_dish": 70, "antenna": 70,
             "wall_lantern": 60, "ac_unit": 55, "spout": 45, "caper": 50, "weeds": 40, "plant_pot": 50,
             "crate_stack": 50, "crate_single": 45, "box_stack": 50, "stool_stack": 45}
SMALL_DIST = 40                            # litter and anything else small


class Placer:
    def __init__(self, lib, col):
        self.lib, self.col = lib or {}, col
        self.count, self.missing = {}, {}

    def __call__(self, ty, pos, yaw, nocol=True, scale=1.0):
        me = self.lib.get(ty)
        if me is None:
            self.missing[ty] = self.missing.get(ty, 0) + 1
            return
        ob = bpy.data.objects.new("%s.%d" % (ty, self.count.get(ty, 0)), me)
        ob.location = pos
        ob.rotation_euler = (0, 0, yaw)
        ob.scale = (scale, scale, scale)
        if nocol:
            ob["nocol"] = 1
        ob["draw_dist"] = DRAW_DIST.get(ty, SMALL_DIST)
        self.col.objects.link(ob)
        self.count[ty] = self.count.get(ty, 0) + 1


def cable_curve(a, b, sag, n=12):
    A, B = Vector(a), Vector(b)
    return [A.lerp(B, i / n) - UP * (sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


# ---------------------------------------------------------------- scene, export, preview
def setup_preview(outdir: Path):
    scn = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
        try:
            scn.render.engine = eng
            break
        except TypeError:
            continue
    world = bpy.data.worlds.new("sky")
    scn.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.55, 0.68, 0.9, 1)
    bg.inputs["Strength"].default_value = 0.8
    sun_d = bpy.data.lights.new("sun", "SUN")
    sun_d.energy = 4.5
    sun_d.color = (1.0, 0.93, 0.82)
    sun_d.angle = math.radians(1.0)
    sun = bpy.data.objects.new("sun", sun_d)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-130))
    scn.collection.objects.link(sun)
    scn.render.resolution_x, scn.render.resolution_y = 1280, 720
    try:
        scn.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    cams = {
        "outside_gate": ((-24, 4, 1.7), (3, -4, 5)),
        "square_west": ((22, -2, 1.7), (80, 14, 7)),
        "square_east": ((92, 2, 1.7), (20, -2, 6)),
        "david_street": ((104, 8.5, 1.7), (150, 8.5, -2)),
        "aerial": ((-40, -70, 70), (55, 5, 0)),
    }
    for name, (eye, look) in cams.items():
        cd = bpy.data.cameras.new(name)
        cd.lens = 18 if name != "aerial" else 28
        cam = bpy.data.objects.new("cam_" + name, cd)
        cam.location = eye
        cam.rotation_euler = (Vector(look) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
        scn.collection.objects.link(cam)
        scn.camera = cam
        scn.render.filepath = str(outdir / ("%s.png" % name))
        try:
            bpy.ops.render.render(write_still=True)
            print("rendered", scn.render.filepath)
        except Exception as e:  # noqa: BLE001
            print("render failed", name, e)
    bpy.data.objects.remove(sun)


def build_steps(mb, steps):
    for s in steps:
        ext = s["poly"]["ext"]
        try:
            fl, ft = mk.tess2d([ext] + s["poly"]["holes"])
        except Exception:  # noqa: BLE001
            continue
        # paving laid per tread: the slab rows start at the nosing and run along the step (world-aligned,
        # the street's joints ran across the treads and the steps read as stripes or staggered slabs;
        # the smooth lime read as an untextured lane on David Street's 2.2 m treads)
        tile = 4.0
        dx, dy = s["dir"]
        d0 = min(p[0] * dx + p[1] * dy for p in ext)
        mb.tris([(p[0], p[1], s["top"]) for p in fl], ft, "paving", UP,
                uvfn=lambda p, dx=dx, dy=dy, d0=d0: ((p[0] * dy - p[1] * dx) / tile, (p[0] * dx + p[1] * dy - d0) / tile))
        ez = s.get("ez") or [s["top"]] * len(ext)
        for i in range(len(ext)):                 # sides: from below up to the tread or the street, whichever
            a, b = ext[i], ext[(i + 1) % len(ext)]                  # is higher, so no gap opens either way
            eo = s.get("eo") or [1] * len(ext)
            # (+2 cm where the street is higher: the ground's triangles sit up to a few cm above the street
            #  level sampled at the corners, and a slit of sky opened under their edge)
            up = lambda z_: z_ + 0.02 if z_ > s["top"] else s["top"]          # noqa: E731
            za, zb = (up(ez[i]), up(ez[(i + 1) % len(ext)])) if eo[i] else (s["top"], s["top"])
            q = [(a[0], a[1], s["bottom"]), (b[0], b[1], s["bottom"]), (b[0], b[1], zb), (a[0], a[1], za)]
            mb.poly(q, "dressed", Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=(0.9, 0.88, 0.84))   # (ashlar: only
                                                                     # a dark mortar band shows at riser height)


def build_retaining(mb, walls, t=0.3):
    """Retaining walls along the edges of level areas (spec "retaining"): a 0.3 m stone slab from
    below the lower side up to the higher one, with a coping face on top."""
    for w in walls:
        a, b = Vector((*w["a"], 0)), Vector((*w["b"], 0))
        d = b - a
        if d.length < 1e-3:
            continue
        n = Vector((d.y, -d.x, 0)).normalized() * (t / 2)
        lo, hi = w["lo"], w["hi"]
        if not w.get("cap", 1):                       # a single face looking at the low side, nothing on top
            q = [a + UP * lo[0], b + UP * lo[1], b + UP * hi[1], a + UP * hi[0]]
            mb.poly(q, w.get("mat", "dressed"), Vector((*w["n"], 0)), col=(0.9, 0.88, 0.84))   # (pale stone, like a kerb)
            continue
        for sgn in (1, -1):
            o = n * sgn
            q = [a + o + UP * lo[0], b + o + UP * lo[1], b + o + UP * hi[1], a + o + UP * hi[0]]
            mb.poly(q, "ashlar", o, col=(0.86, 0.83, 0.77))
        if w.get("cap", 1):
            mb.poly([a + n + UP * hi[0], b + n + UP * hi[1], b - n + UP * hi[1], a - n + UP * hi[0]], "dressed", UP,
                    col=(0.9, 0.88, 0.83))


def wall_runs(walls, tol=0.15):
    """Chain walls_generic segments into runs through their end points, whatever their order in the
    list (base.json starts mid-circuit and lists some stretches backwards): a segment continues the
    one whose b lies within tol of its a (closest pair first, the next one in the list on a tie);
    such short gaps close on the shared point. Returns [(run, closed)]."""
    nw = len(walls)
    cand = sorted((math.dist(w["b"], v["a"]), 0 if j == i + 1 else 1, i, j)
                  for i, w in enumerate(walls) for j, v in enumerate(walls)
                  if i != j and abs(w["b"][0] - v["a"][0]) < tol and math.dist(w["b"], v["a"]) < tol)
    nxt, prv = [None] * nw, [None] * nw
    for _, _, i, j in cand:
        if nxt[i] is None and prv[j] is None:
            nxt[i], prv[j] = j, i
    runs, seen = [], [False] * nw
    for s0 in [i for i in range(nw) if prv[i] is None] + list(range(nw)):    # open chains, then loops
        if seen[s0]:
            continue
        run, i = [], s0
        while i is not None and not seen[i]:
            seen[i] = True
            run.append(walls[i])
            i = nxt[i]
        runs.append((run, i == s0 and len(run) > 2))
    return runs


def build_walls_generic(mb, walls, merlons=(0.9, 0.75, 1.4, 0.6)):
    """OSM wall circuit outside the hand-modelled Jaffa Gate stretch. Chained segments (wall_runs)
    form runs built as one mitred slab: faces meet on the mitre line (no overlapping boxes), a step
    in the terrain-following top gets a riser, merlons on the outer (right-hand) edge keep clear of
    the joints."""
    Z = lambda z: Vector((0, 0, z))  # noqa: E731
    mw, gap, mh, md = merlons
    for ri, (run, closed) in enumerate(wall_runs(walls)):
        n = len(run)
        lift = 0.015 * (ri % 3)                 # runs meeting at T-junctions: tops never coplanar
        run = [dict(w, z1=w["z1"] + lift) for w in run]
        pts = [Vector((*run[0]["a"], 0))] + [Vector((*w["b"], 0)) for w in run]
        if closed:
            pts[-1] = pts[0].copy()
        tan = [(pts[i + 1] - pts[i]).normalized() for i in range(n)]
        nrm = [Vector((t.y, -t.x, 0)) for t in tan]               # right = outside
        R, L = [], []
        for k in range(n + 1):
            i0, i1 = k - 1, k
            if closed:
                i0, i1 = (k - 1) % n, k % n
            if i0 < 0 or i1 >= n:
                m, f = nrm[max(0, min(i1, n - 1))], 1.0
            else:
                m = nrm[i0] + nrm[i1]
                m = m.normalized() if m.length > 1e-6 else nrm[i0]
                f = 1.0 / max(0.5, m.dot(nrm[i0]))
            h = run[k % n if closed else min(k, n - 1)]["thick"] / 2
            R.append(pts[k] + m * h * f)
            L.append(pts[k] - m * h * f)
        for i, w in enumerate(run):
            z0, z1 = w["z0"], w["z1"]
            ar, br, al, bl = R[i], R[i + 1], L[i], L[i + 1]
            mb.poly([ar + Z(z0), br + Z(z0), br + Z(z1), ar + Z(z1)], "fort", nrm[i])
            mb.poly([bl + Z(z0), al + Z(z0), al + Z(z1), bl + Z(z1)], "fort", -nrm[i])
            mb.poly([ar + Z(z1), br + Z(z1), bl + Z(z1), al + Z(z1)], "fort", UP)
            nxt = run[(i + 1) % n] if (i + 1 < n or closed) else None
            if nxt is not None and abs(nxt["z1"] - z1) > 0.01:
                lo, hi = min(z1, nxt["z1"]), max(z1, nxt["z1"])
                mb.poly([br + Z(lo), bl + Z(lo), bl + Z(hi), br + Z(hi)], "fort", tan[i] if nxt["z1"] < z1 else -tan[i])
            if not closed and i == 0:
                mb.poly([al + Z(z0), ar + Z(z0), ar + Z(z1), al + Z(z1)], "fort", -tan[i])
            if not closed and i == n - 1:
                mb.poly([br + Z(z0), bl + Z(z0), bl + Z(z1), br + Z(z1)], "fort", tan[i])
            # merlons along the outer edge, clear of the mitred corners
            a, b = pts[i], pts[i + 1]
            seg = (b - a).length
            h = w["thick"] / 2
            m0 = 0.4 + max(0.0, (ar - a).dot(tan[i])) + 0.0
            m1 = 0.4 + max(0.0, (b - br).dot(tan[i]))
            m0 = max(m0, 0.4 + max(0.0, (al - a).dot(tan[i])))
            m1 = max(m1, 0.4 + max(0.0, (b - bl).dot(tan[i])))
            avail = seg - m0 - m1
            if avail < mw:
                continue
            k = int((avail + gap) // (mw + gap))
            u = m0 + (avail - (k * mw + (k - 1) * gap)) / 2
            for _ in range(k):
                c = a + tan[i] * (u + mw / 2) + nrm[i] * (h - md / 2)
                mk.box(mb, c, tan[i], nrm[i], mw, md, z1, z1 + mh, "fort")
                u += mw + gap


VAULT_WALL = 0.4        # outer side walls this far beyond the springing: inside the flanking buildings
VAULT_DECK = 0.05       # deck this far below the spec top: under a flanking roof of the same height
VAULT_SEGS = 7          # arch profile, segments per side (a coarser LOD profile must divide it)


def _vault_prof(hw, segs):
    """Vault cross-section: right springing -> crown -> left springing, pointed (two arcs meeting at
    the crown, ~1.25 hw above the springing)."""
    rise, prof = 1.25 * hw, []
    for j in range(2 * segs + 1):
        u = j / segs - 1.0                     # -1 (right) .. 0 (crown) .. 1 (left)
        prof.append((-u * hw, rise * math.sin(math.acos(min(1.0, abs(u)))) ** 0.75))
    return prof


def build_vaults(mb, vaults, segs=VAULT_SEGS):
    """Covered streets: a pointed barrel vault along the way (springing `spring` above the street,
    crown ~1.25 hw higher), the mass above it up to `top` (flat roof deck, spandrels at the ends)
    and outer side walls, which show only from the rooftops: they stand VAULT_WALL beyond the
    springing, inside the flanking buildings (whose facades are at about hw), and a soffit at the
    springing closes the vault mass below them. The deck sits VAULT_DECK under `top` (the median
    height of the flanking roofs for passages), so a flanking roof of the same height covers the
    strip of it that reaches over. The sector LOD passes segs=1 (a gable for the arch) on the same
    axis (3 m steps): all that shows from outside (deck, side walls, soffits, end strips, and the
    spandrels, which always take the full profile) is the hi geometry triangle for triangle, so the
    game's per-cell swap (by triangle centroid) puts hi and lo of it in the same render cell and the
    two never overlap or leave a gap."""
    assert VAULT_SEGS % segs == 0
    Z = lambda z: Vector((0, 0, z))  # noqa: E731
    # vaults that meet (junctions, crossings, split ways): decks at least 6 mm apart (> audit
    # tolerance), and springings too where their soffits can touch (axis points within ow + ow)
    decks, drops = [], []
    for i, v in enumerate(vaults):
        reach, pairs = [], []                       # decks of the vaults met; springing heights (v, w)
        for j, w in enumerate(vaults[:i]):
            r = v["hw"] + w["hw"] + 2 * VAULT_WALL
            near = [(math.dist(p[:2], q[:2]), p, q) for p in v["pts"] for q in w["pts"]]
            if any(d < r + 3.0 for d, _, _ in near):
                reach.append(decks[j])
            pairs += [(p[2] + v["spring"], q[2] + w["spring"] + drops[j]) for d, p, q in near if d < r]
        z = v["top"] - VAULT_DECK
        while any(abs(z - q) < 0.006 for q in reach):
            z -= 0.006
        dz = 0.0
        while any(abs(a + dz - b) < 0.006 for a, b in pairs):
            dz -= 0.006
        decks.append(z)
        drops.append(dz)
    for v, top, drop in zip(vaults, decks, drops):
        pts = [Vector((p[0], p[1], 0)) for p in v["pts"]]
        zs = [p[2] for p in v["pts"]]
        spring = v["spring"] + drop
        n = len(pts) - 1
        if n < 1:
            continue
        hw = v["hw"]
        ow = hw + VAULT_WALL
        tan = [(pts[i + 1] - pts[i]).normalized() for i in range(n)]
        side = []
        for k in range(n + 1):
            if k == 0 or k == n:
                t = tan[min(k, n - 1)]
                m, f = Vector((t.y, -t.x, 0)), 1.0
            else:
                n1, n2 = Vector((tan[k - 1].y, -tan[k - 1].x, 0)), Vector((tan[k].y, -tan[k].x, 0))
                m = (n1 + n2).normalized() if (n1 + n2).length > 1e-6 else n1
                f = 1.0 / max(0.5, m.dot(n1))
            side.append(m * f)
        prof, full = _vault_prof(hw, segs), _vault_prof(hw, VAULT_SEGS)
        rings = []
        for k in range(n + 1):
            base = zs[k] + spring
            rings.append([pts[k] + side[k] * x + Z(base + z) for x, z in prof])
        for k in range(n):
            mid_axis = (pts[k] + pts[k + 1]) / 2 + Z((zs[k] + zs[k + 1]) / 2 + spring)
            for j in range(len(prof) - 1):
                q = [rings[k][j], rings[k + 1][j], rings[k + 1][j + 1], rings[k][j + 1]]
                c = (q[0] + q[2]) / 2
                mb.poly(q, "rubble", mid_axis - c)                  # inner surface faces the axis
            # roof deck and outer side walls (beyond the springing), visible from above only
            r0, r1 = pts[k] + side[k] * ow, pts[k + 1] + side[k + 1] * ow
            l0, l1 = pts[k] - side[k] * ow, pts[k + 1] - side[k + 1] * ow
            mb.poly([r0 + Z(top), r1 + Z(top), l1 + Z(top), l0 + Z(top)], "lime", UP, col=(0.78, 0.77, 0.75))
            sp0, sp1 = zs[k] + spring, zs[k + 1] + spring
            nr = Vector((tan[k].y, -tan[k].x, 0))
            mb.poly([r0 + Z(sp0), r1 + Z(sp1), r1 + Z(top), r0 + Z(top)], "rubble", nr)
            mb.poly([l1 + Z(sp1), l0 + Z(sp0), l0 + Z(top), l1 + Z(top)], "rubble", -nr)
            for sg, w0, w1 in ((1, r0, r1), (-1, l0, l1)):           # soffits: springing -> side wall
                s0, s1 = pts[k] + side[k] * (sg * hw), pts[k + 1] + side[k + 1] * (sg * hw)
                mb.poly([s0 + Z(sp0), s1 + Z(sp1), w1 + Z(sp1), w0 + Z(sp0)], "rubble", -UP)
        # ends: spandrels from the full profile up to the deck (fillers in the end plane close the
        # LOD's coarse arch up to it), and the mass out to the side walls (5 cm back: most passages
        # end on the facade line of the building they pass through)
        step = VAULT_SEGS // segs
        for k, sgn in ((0, -1), (n, 1)):
            t = tan[min(k, n - 1)] * sgn
            sp = zs[k] + spring
            ring = [pts[k] + side[k] * x + Z(sp + z) for x, z in full]
            for j in range(len(full) - 1):
                a, b = ring[j], ring[j + 1]
                q = [a, b, Vector((b.x, b.y, top)), Vector((a.x, a.y, top))]
                if (q[3].z - q[0].z) > 0.01 or (q[2].z - q[1].z) > 0.01:
                    mb.poly(q, "rubble", t)
            if step > 1:
                for c in range(2 * segs):
                    mb.poly(ring[c * step:(c + 1) * step + 1], "rubble", t)
            for sg in (1, -1):
                a, b = pts[k] + side[k] * (sg * hw) - t * 0.05, pts[k] + side[k] * (sg * ow) - t * 0.05
                mb.poly([a + Z(sp), b + Z(sp), b + Z(top), a + Z(top)], "rubble", t)


def build_lod(mb, bd, gen):
    """Cheap massing for distant sectors: plain walls, flat or hipped roof, window cards, domes."""
    ring = [tuple(p) for p in bd["ring"]]
    col = tuple(min(1.0, c / 1.06) for c in bd["tint"])
    wall = bd["style"]["wall"]
    for i in range(len(ring)):
        fb.wall_panel(mb, ring[i], ring[(i + 1) % len(ring)], bd["base"], bd["top"], [], wall, col, gen)
    if bd["style"]["roof"] == "hipped":
        roof_hipped(mb, ring, bd["top"])
    else:
        fl, ft = mk.tess2d([ring])
        mb.tris([(p[0], p[1], bd["top"]) for p in fl], ft, "lime", UP, col=roof_tone(bd))
    context_windows(mb, bd, gen)
    vernacular_domes(mb, bd, bd["top"], seg=8, rings=2, limit=4)
    if bd["style"]["domes"]:
        c, t, s, ll, ls = obb(ring)
        r = min(2.6, 0.24 * ls)
        if r > 0.9:
            mk.dome(mb, c.x, c.y, bd["top"], r, "lime", drum=0.4, seg=8, rings=3)


def material_library(mats, tiles, collection):
    """One small quad per material: the textured materials every sector GLB refers to by name."""
    mb = mk.MeshBuilder(tiles)
    for i, name in enumerate(sorted(mats)):
        x = (i % 8) * 2.0
        y = -2000.0 - (i // 8) * 2.0
        mb.poly([Vector((x, y, -50)), Vector((x + 1, y, -50)), Vector((x + 1, y + 1, -50)), Vector((x, y + 1, -50))],
                name, UP, uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
    ob = mb.to_object("material_library", mats, collection)
    ob["nocol"] = 1
    return ob


def export_glb(path, collections, images=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for o in bpy.context.scene.objects:
        o.select_set(False)
    n = 0
    for c in collections:
        for o in c.all_objects:
            o.select_set(True)
            n += 1
    if not n:
        print("nothing to export for", path)
        return
    kw = dict(filepath=str(path), export_format="GLB", export_extras=True, export_yup=True, use_selection=True,
              export_apply=True, export_image_format="WEBP" if images else "NONE", export_texcoords=True,
              export_image_quality=85)
    try:
        bpy.ops.export_scene.gltf(**kw, export_vertex_color="ACTIVE")
    except TypeError:
        bpy.ops.export_scene.gltf(**kw)
    print("exported", path, n, "objects")


SPEC_DIR = Path(os.environ["SPEC_DIR"]).resolve() if os.environ.get("SPEC_DIR") else ROOT / "data/spec"   # see make_spec


def main():
    args = parse_args()
    part = args.part
    if part == "base":
        spec = json.loads((SPEC_DIR / "base.json").read_text())
    elif part:
        spec = json.loads((SPEC_DIR / ("%s.json" % part)).read_text())
    else:
        spec = json.loads(Path(args.spec).read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats, tiles, gen = materials.build(ROOT)
    sj = ROOT / "data/textures/gen/signs.json"
    signs = json.loads(sj.read_text()) if sj.exists() and "signs" in mats else None
    cols = {}

    def col(name):
        if name not in cols:
            cols[name] = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(cols[name])
        return cols[name]
    lib = proplib.build_library(mats, tiles, gen) if proplib else {}
    place = Placer(lib, col("props"))

    def mbset():
        return {"solid": mk.MeshBuilder(tiles), "deco": mk.MeshBuilder(tiles), "signs": mk.MeshBuilder(tiles),
                "cables": mk.MeshBuilder(tiles)}

    def flush(mbs, name, collection, label=None):
        for p_, mb in mbs.items():
            if mb.empty():
                continue
            ob = mb.to_object(name if p_ == "solid" else "%s_%s" % (name, p_), mats, collection)
            if p_ != "solid":
                ob["nocol"] = 1
            if label:
                ob["label"] = label

    detailed = [b for b in spec["buildings"] if b["tier"] in ("hero", "mid")]
    context = [b for b in spec["buildings"] if b["tier"] == "context"]
    hi = col("city")
    for bd in detailed:                                     # sector detail (or legacy scene)
        mbs = mbset()
        if not landmarks.build(mbs, bd, gen, place):
            build_building(mbs, bd, gen, signs, place)
        flush(mbs, "bld_%s" % bd["id"], hi, bd["tags"].get("name:en") or bd["tags"].get("name") or bd["id"])
    if context:
        mbs = mbset()
        for bd in context:
            build_building(mbs, bd, gen, signs, place)
        flush(mbs, "context_massing", col("context"))
    if part in (None, "base"):
        fmbs = {k: mk.MeshBuilder(tiles) for k in ("jaffa_gate", "city_wall", "citadel")}
        fortifications.build(fmbs, spec, gen, place)
        for k, mb in fmbs.items():
            mb.to_object(k, mats, col("walls"))
        wg = mk.MeshBuilder(tiles)
        wb = landmarks.walls_builder()
        try:
            if wb:
                wb(wg, spec.get("walls_generic", []), gen)
            else:
                build_walls_generic(wg, spec.get("walls_generic", []))
        except Exception:  # noqa: BLE001
            if landmarks.STRICT:                            # LANDMARKS_STRICT=1: the wall circuit too
                raise
            import traceback
            print("WALLS WARNING: landmarks_gates.build_walls failed, generic walls instead")
            traceback.print_exc()
            wg = mk.MeshBuilder(tiles)
            build_walls_generic(wg, spec.get("walls_generic", []))
        if not wg.empty():
            wg.to_object("city_walls_osm", mats, col("walls"))
        gmbs = {"ground": mk.MeshBuilder(tiles)}
        build_ground(gmbs, dict(spec, steps=[]))
        gmbs["ground"].to_object("ground", mats, col("ground"))["ground"] = 1
        rw = mk.MeshBuilder(tiles)
        build_retaining(rw, spec.get("retaining", []))
        if not rw.empty():
            rw.to_object("retaining_walls", mats, col("ground"))
    st = mk.MeshBuilder(tiles)
    build_steps(st, spec.get("steps", []))
    if not st.empty():
        st.to_object("steps", mats, col("ground") if part == "base" else hi)
    gd = mk.MeshBuilder(tiles)
    for dcl in spec.get("ground_decals", []):
        cell = gen["decal"]["cells"].get(dcl["type"])
        if not cell:
            continue
        rect = mk.atlas_rect(gen["decal"]["grid"], cell, size_px=1024)
        a = math.radians(dcl["rot"])
        right = Vector((math.cos(a), -math.sin(a), 0))
        fwd = Vector((math.sin(a), math.cos(a), 0))
        c = Vector(dcl["p"]) - fwd * dcl["h"] / 2 + UP * 0.03      # (lifted: a sloping ground swallowed half a cover)
        q = [c - right * dcl["w"] / 2, c + right * dcl["w"] / 2, c + right * dcl["w"] / 2 + fwd * dcl["h"],
             c - right * dcl["w"] / 2 + fwd * dcl["h"]]
        u0, v0, u1, v1 = rect
        gd.poly(q, "decal", UP, uv=[(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    if not gd.empty():
        gd.to_object("ground_decals", mats, col("ground") if part == "base" else hi)["nocol"] = 1
    vb = mk.MeshBuilder(tiles)
    build_vaults(vb, spec.get("vaults", []))
    if not vb.empty():
        vb.to_object("vaults", mats, hi)
    bm_ = mk.MeshBuilder(tiles)
    for bmz in spec.get("beams", []):
        mk.tube(bm_, [bmz["a"], bmz["b"]], 0.05, "metal_green", sides=6, col=fb.GREEN)
    if not bm_.empty():
        bm_.to_object("street_beams", mats, hi)["nocol"] = 1
    cab = mk.MeshBuilder(tiles)
    for c in spec.get("cables", []):
        mk.tube(cab, cable_curve(c["a"], c["b"], c["sag"]), c.get("r", 0.012), "iron")
    if not cab.empty():
        cab.to_object("street_cables", mats, hi)["nocol"] = 1
    for p in spec.get("props", []):
        place(p["type"], Vector(p["p"]), -math.radians(p["rot"]), not p.get("col", False), p.get("s", 1.0))
    if part not in (None, "base") and detailed:             # massing LOD for this sector
        lo = mk.MeshBuilder(tiles)
        lo4 = {"solid": lo, "deco": lo, "signs": lo, "cables": lo}
        for bd in detailed:
            if not landmarks.build(lo4, bd, gen, place, lod=True):
                build_lod(lo, bd, gen)
        build_vaults(lo, spec.get("vaults", []), segs=1)    # covered streets keep their roofs
        lo.to_object("lod_%s" % part, mats, col("lod"))

    for name, c in cols.items():
        print("collection %-8s objects %5d faces %8d" % (name, len(c.all_objects),
                                                          sum(len(o.data.polygons) for o in c.all_objects if o.type == "MESH")))
    print("missing prop types %s" % place.missing)
    pub = ROOT / "game/public"
    if not args.no_export:
        if part == "base":
            # textures live once in materials.glb; every other GLB refers to materials by name
            material_library(mats, tiles, col("materials"))
            export_glb(pub / "base/materials.glb", [col("materials")])
            export_glb(pub / "base/ground.glb", [col("ground")], images=False)
            export_glb(pub / "base/walls.glb", [col("walls")], images=False)
            export_glb(pub / "base/context.glb", [col("context"), col("props")], images=False)
        elif part:
            export_glb(pub / ("sectors/%s.glb" % part), [hi, col("props")], images=False)
            export_glb(pub / ("sectors/%s_lo.glb" % part), [col("lod")], images=False)
        else:
            export_glb(args.out, [c for n, c in cols.items() if n != "lod"])
    if args.preview and not part:
        out = Path(args.preview)
        out.mkdir(parents=True, exist_ok=True)
        setup_preview(out)
    blend = args.blend if not part else str(ROOT / ("build/%s.blend" % part))
    Path(blend).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("saved", blend)


if __name__ == "__main__":
    main()
